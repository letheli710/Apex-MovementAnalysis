#!/usr/bin/env python3
"""M4 Octane: stim (speed multiplier), jump pad (instant impulse + slow-mo flight), landing slowdown.

    python octane_analysis.py <session folder> [<session folder> ...] [--json results.json] [--params params.json]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). Only trials with ok=true and
warmup=false are used; the schedule decides the role (m4_stim_*, m4_ctrl_*, m4_pad_*).

Physics truth: client first-time MOVE-TRACE commands. dt and yaw per command come from the client HSD frame
that shows the command's post-state (M2 join, ../../m2/air_jump/aj_load.py, validated per command). Dedi
MOVE-TRACE rows of the same usercmd are used for parity and for the authoritative stim fade timing.
The M2/M3 models are reused unchanged (AirAccelerate, lurch). Nothing is tuned to pass.
stdlib only, no local paths.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m2", "air_jump")))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m3", "lurch")))
import aj_load as L  # noqa: E402
import lurch_analysis as LU  # noqa: E402  (M3 helpers: air_accel, lurch_lerp, wish)

TAC = 0x200000          # +offhand1 (tactical)
IN_JUMP, IN_DUCK, IN_FWD, IN_SPEED = 0x2, 0x4, 0x8, 0x8000
STRAFE_MASK = 0x618
# census (M2 PARAMETER-TABLE and this session's census): base values the factors multiply
SPEED, SPRINTSPEED, LOWSPEED = 173.5, 260.0, 120.0
ACC, LOWACC, SPRINTACC, DECEL = 450.0, 2500.0, 100.0, 1250.0
G = 750.0
MSC0 = 1.15            # empty-handed weapon factor seen in every M2/M3 trial
PAD_PUSH, PAD_VERT, PAD_DUCK = 1150.0, 2.0, 0.5   # sh_jump_pads.gnut constants, SDK ducked scalar
POS = ("ox", "oy", "oz", "vx", "vy", "vz", "pox", "poy", "poz", "pvx", "pvy", "pvz")


# ----------------------------------------------------------------------------- small helpers
def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def st(vals):
    return L.stats(list(vals))


def f(s, nd=4):
    return L.fmt(s, nd)


def lin_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    rms = math.sqrt(sum(r * r for r in res) / n)
    se_b = math.sqrt(sum(r * r for r in res) / max(n - 2, 1) / sxx) if n > 2 else 0.0
    return a, b, rms, se_b, max(abs(r) for r in res)


def rising(cs, i, bit):
    return bool(cs[i]["buttons"] & bit) and (i == 0 or not cs[i - 1]["buttons"] & bit)


def tsum(cs, a, b):
    return sum(cs[k]["dt"] for k in range(a, b))


def load(folders):
    trials = []
    meta = []
    for fo in folders:
        S = L.load_session(fo)
        meta.append({"session": S["folder"], "trials": len(S["trials"]), "parse_errors": S["parse_errors"],
                     "census": bool(S.get("census"))})
        for t in S["trials"]:
            t["session"] = S["folder"]
            t.pop("frames", None)
            t["sv"] = {r["cmd"]: r for r in t["sv_mt"]}
            trials.append(t)
    return trials, meta


def parity(t):
    """max |cl - dedi| over all commands of the trial for position/velocity and movescale."""
    dp, dm, n = 0.0, 0.0, 0
    for c in t["cmds"]:
        s = t["sv"].get(c["cmd"])
        if not s:
            continue
        n += 1
        dp = max(dp, max(abs(s[k] - c[k]) for k in POS))
        dm = max(dm, abs(s["movescale"] - c["movescale"]))
    return n, dp, dm


# ----------------------------------------------------------------------------- 1. stim
def stim_events(t):
    cs = t["cmds"]
    taps = [i for i in range(len(cs)) if rising(cs, i, TAC)]
    ev = {"run": t["run"], "schedule": t["schedule"], "session": t["session"], "msc_first": cs[0]["movescale"],
          "taps": taps}
    if cs[0]["movescale"] > MSC0 + 1e-4:
        ev["carry_over"] = True   # a stim from the previous trial was still active at the start
    on = next((i for i in range(1, len(cs)) if cs[i]["movescale"] > MSC0 + 5e-4 and cs[i - 1]["movescale"] <= MSC0 + 5e-4), None)
    ev["onset"] = on
    if taps and on is not None and on > taps[0]:
        ev["tap_to_onset_cmds"] = on - taps[0]
        ev["tap_to_onset_s"] = tsum(cs, taps[0], on)
        ev["onset_step"] = (cs[on - 1]["movescale"], cs[on]["movescale"])
    elif taps:
        ev["tap_without_onset"] = True
    if on is None:
        return ev
    plateau = cs[on]["movescale"]
    ev["plateau_msc"] = plateau
    ev["plateau_walkcap"] = [c["maxspeed"] for c in cs[on:on + 400] if not c["sprint"] and c["ground"]][:1]
    rs = next((i for i in range(on, len(cs)) if cs[i]["movescale"] < plateau - 5e-5), None)
    en = next((i for i in range(rs, len(cs)) if cs[i]["movescale"] <= MSC0 + 5e-5), None) if rs else None
    ev["ramp_start_cl"], ev["ramp_end_cl"] = rs, en
    if rs:
        ev["full_s_cl"] = tsum(cs, on, rs)
    if rs and en:
        ev["ramp_s_cl"] = tsum(cs, rs, en)
        ev["onset_to_end_s_cl"] = tsum(cs, on, en)
        ev["nonmono_cl"] = [i - rs for i in range(rs + 1, en) if cs[i]["movescale"] > cs[i - 1]["movescale"] + 5e-5]
    # dedi (authoritative status effect): onset and fade of the same usercmds
    sv = [t["sv"].get(c["cmd"]) for c in cs]
    if all(s is not None for s in sv[max(on - 2, 0):]):
        son = next((i for i in range(1, len(cs)) if sv[i]["movescale"] > MSC0 + 5e-4
                    and sv[i - 1]["movescale"] <= MSC0 + 5e-4), None)
        ev["onset_sv"] = son
        ev["onset_cl_minus_sv_cmds"] = on - son if son is not None else None
        srs = next((i for i in range(son, len(cs)) if sv[i]["movescale"] < plateau - 5e-5), None) if son else None
        sen = next((i for i in range(srs, len(cs)) if sv[i]["movescale"] <= MSC0 + 5e-5), None) if srs else None
        ev["ramp_start_sv"], ev["ramp_end_sv"] = srs, sen
        if srs:
            ev["full_s_sv"] = tsum(cs, son, srs)
            if rs:
                ev["rampshift_cmds_cl_minus_sv"] = rs - srs
        if srs and sen:
            ev["onset_to_end_s_sv"] = tsum(cs, son, sen)
            ev["ramp_s_sv"] = tsum(cs, srs, sen)
            # fade samples (dedi msc vs time since the start of the last full-strength command)
            ev["_fade"] = [(tsum(cs, srs - 1, i), sv[i]["movescale"]) for i in range(srs - 1, min(sen + 2, len(cs)))]
            eq = [i for i in range(srs, sen) if abs(cs[i]["movescale"] - sv[i]["movescale"]) >= 5e-5]
            ev["cl_differs_in_fade_cmds"] = (eq[0] - srs, eq[-1] - srs) if eq else None
    return ev


def fade_models(samples, T=0.5):
    """samples: (t since last plateau cmd, msc). shape g(x) of the boost fraction, x = t/T."""
    out = {}
    if not samples:
        return out
    m0 = samples[0][1]
    shapes = {"linear": lambda x: 1 - x,
              "smoothstep": lambda x: 1 - (3 * x * x - 2 * x ** 3),
              "cosine": lambda x: 0.5 + 0.5 * math.cos(math.pi * x),
              "quadratic_out": lambda x: 1 - x * x}
    best = {}
    for name, g in shapes.items():
        bestv = None
        for Tm in range(440, 561, 4):          # fade duration 0.44..0.56 s
            TT = Tm / 1000.0
            for k in range(-20, 21):           # time shift of the fade start, 0.5 ms steps
                sh = k * 0.0005
                res = []
                for (t, m) in samples:
                    x = min(max((t - sh) / TT, 0.0), 1.0)
                    res.append(m - (MSC0 + (m0 - MSC0) * g(x)))
                rms = math.sqrt(sum(r * r for r in res) / len(res))
                if bestv is None or rms < bestv[0]:
                    bestv = (rms, sh, max(abs(r) for r in res), TT)
        best[name] = {"rms": bestv[0], "shift_s": bestv[1], "max": bestv[2], "T": bestv[3]}
    out["shapes"] = best
    return out


def accel_bands(t, msc_tol=5e-5):
    """Per-command accelerations on the ground with W, grouped by band. Returns list of (band, msc, a/msc, a)."""
    cs = t["cmds"]
    out = []
    for i in range(1, len(cs)):
        c = cs[i]
        if not c["join_ok"] or not c["ground"] or c["pvz"] != 0 or c["fwd"] < 0.99 or c["duck"]:
            continue
        if abs(cs[i - 1]["movescale"] - c["movescale"]) > msc_tol:
            continue
        s0, s1, m = hs(c, False), hs(c), c["movescale"]
        if s1 <= s0 + 1e-6 or s0 < 1:
            continue
        a = (s1 - s0) / c["dt"]
        walkcap, lowcap = SPEED * m, LOWSPEED * m
        if s1 < lowcap - 0.01:
            band = "low"
        elif s0 >= lowcap and s1 < walkcap - 0.01:
            band = "walk"
        elif c["sprint"] and s0 >= walkcap and s1 < c["maxspeed"] - 0.01:
            band = "sprint"
        else:
            continue
        out.append((band, m, a / m, a))
    return out


def decel_samples(t):
    cs = t["cmds"]
    out = []
    for i in range(1, len(cs)):
        c = cs[i]
        if c["join_ok"] and c["ground"] and c["fwd"] == 0 and c["sidemove"] == 0 and not c["duck"]:
            s0, s1 = hs(c, False), hs(c)
            if s0 > 20 and s1 > 1 and s1 < s0:
                out.append(((s0 - s1) / c["dt"], c["movescale"]))
    return out


def air_trial(t):
    """Jump + first strafe press (M3 lurch) for m4_stim_air / m4_ctrl_air."""
    cs = t["cmds"]
    J = [i for i in range(1, len(cs)) if cs[i]["ground"] == 1 and cs[i]["pvz"] > 50 and cs[i]["pvz"] < 400]
    if not J:
        return None
    j = J[0]
    P = [i for i in range(j + 1, len(cs)) if (cs[i]["buttons"] & STRAFE_MASK) & ~(cs[i - 1]["buttons"] & STRAFE_MASK)]
    if not P:
        return None
    p = P[0]
    c = cs[p]
    land = next((i for i in range(j + 1, len(cs)) if cs[i]["ground"] == 1), len(cs))
    tA = tsum(cs, j, p)
    lam = 0.7 * min(max((0.5 - tA) / 0.3, 0.0), 1.0)
    w, _ = LU.wish(c)
    v0 = (c["vx"], c["vy"])
    vp = LU.air_accel(c, v0)
    obs = (c["pvx"], c["pvy"])
    m = c["movescale"]
    preds = {}
    for name, Lmax in (("L=209.3 const", 209.3), ("L=182*msc", 182.0 * m), ("L=0.7*sprintcap", 0.7 * cs[j]["maxspeed"])):
        v1 = LU.lurch_lerp(vp, w, lam, Lmax)
        preds[name] = {"Lmax": Lmax, "err": math.hypot(v1[0] - obs[0], v1[1] - obs[1]), "s1_pred": math.hypot(*v1)}
    D = (obs[0] - vp[0], obs[1] - vp[1])
    # other airborne commands: M2 AirAccelerate residual
    other, adds = [], []
    for i in range(j + 1, land):
        if i == p or not cs[i]["join_ok"]:
            continue
        q = cs[i]
        pv = LU.air_accel(q, (q["vx"], q["vy"]))
        other.append(math.hypot(q["pvx"] - pv[0], q["pvy"] - pv[1]))
        ww, ws = LU.wish(q)
        if ww is not None:
            adds.append(min(ws, 60.0 * q["movescale"]) - (q["vx"] * ww[0] + q["vy"] * ww[1]))
    return {"run": t["run"], "schedule": t["schedule"], "session": t["session"], "msc_jump": cs[j]["movescale"],
            "s_pre_jump": hs(cs[j], False), "s_post_jump": hs(cs[j]), "vz_jump": cs[j]["pvz"],
            "maxspeed_jump": cs[j]["maxspeed"], "press_k": p - j, "tA": tA, "lam": lam, "s_before": math.hypot(*vp),
            "s_after": math.hypot(*obs), "D_len": math.hypot(*D), "preds": preds,
            "air_resid_max": max(other) if other else None, "air_n": len(other),
            "air_add_max": max(adds) if adds else None, "land_s": hs(cs[land - 1]) if land < len(cs) else None}


# ----------------------------------------------------------------------------- 2. jump pad
def pad_launch(t):
    cs = t["cmds"]
    Ls = [i for i in range(1, len(cs)) if cs[i]["pvz"] - cs[i]["vz"] > 500]
    if not Ls:
        return None
    i = Ls[0]
    c = cs[i]
    land = next((k for k in range(i + 1, len(cs)) if cs[k]["ground"] == 1), None)
    ducked = c["duck"] > 0
    V = PAD_VERT * (PAD_DUCK if ducked else 1.0)
    n = math.sqrt(1 + V * V)
    pred_h, pred_v = PAD_PUSH / n, PAD_PUSH * V / n
    return {"run": t["run"], "schedule": t["schedule"], "session": t["session"], "i": i, "land": land,
            "dt": c["dt"], "duck": c["duck"], "ground_pre": c["ground"], "buttons": c["buttons"],
            "s_in": hs(c, False), "vz_in": c["vz"], "h_out": hs(c), "vz_out": c["pvz"],
            "dir_out_deg": math.degrees(math.atan2(c["pvy"], c["pvx"])),
            "dir_in_deg": math.degrees(math.atan2(c["vy"], c["vx"])) if hs(c, False) > 1 else None,
            "yaw": c["yaw"], "x_in": c["ox"], "x0": cs[0]["ox"], "pred_h": pred_h, "pred_v": pred_v,
            "sv_same": (lambda s: s is not None and max(abs(s[k] - c[k]) for k in POS) < 0.002)(t["sv"].get(c["cmd"]))}


def flight_samples(t, lp):
    """Per airborne command after the launch: position scale k (dx = k*v*dt), gravity, horizontal drift."""
    cs = t["cmds"]
    i, land = lp["i"], lp["land"]
    lc = land - 1                       # the landing command (airborne pre-state, post vz = 0)
    drift_w, drift_now = [], []
    sx = sv = sz = svz = sg = sdt = 0.0
    for k in range(i + 1, lc):          # pure flight commands
        c = cs[k]
        if not c["join_ok"]:
            continue
        sx += c["pox"] - c["ox"]
        sv += c["pvx"] * c["dt"]
        sz += c["poz"] - c["oz"]
        svz += 0.5 * (c["vz"] + c["pvz"]) * c["dt"]
        sg += c["vz"] - c["pvz"]
        sdt += c["dt"]
        d = (hs(c) - hs(c, False)) / c["dt"]
        (drift_w if c["fwd"] > 0 else drift_now).append((d, c["vz"]))
    apex = max(cs[k]["poz"] for k in range(i, land))
    return {"k_xy": sx / sv, "g_eff": sg / sdt, "drift_W": st(d for d, _ in drift_w),
            "drift_noW": st(d for d, _ in drift_now), "_drift_W": drift_w,
            "air_time": tsum(cs, i, land), "apex_rise": apex - cs[i]["oz"], "apex_z": apex,
            "h_at_land": hs(cs[lc], False), "h_gain": hs(cs[lc], False) - hs(cs[i])}


def jumpin_miss(t, pad_x, reach=48.0):
    cs = t["cmds"]
    floor = cs[0]["oz"]
    inside = [c for c in cs if abs(c["pox"] - pad_x) <= reach and abs(c["poy"] - cs[0]["oy"]) < 5]
    if not inside:
        return None
    return {"run": t["run"], "n_inside": len(inside), "min_feet_above_floor": min(c["poz"] - floor for c in inside),
            "airborne_all": all(c["ground"] == 0 for c in inside), "launch": False}


# ----------------------------------------------------------------------------- 3. landing slowdown
def landings(t):
    cs = t["cmds"]
    out = []
    for i in range(1, len(cs) - 2):
        c = cs[i]
        if not (c["ground"] == 0 and c["vz"] < -100 and c["pvz"] == 0):
            continue
        base = c["movescale"]
        h0, h1 = hs(c, False), hs(c)
        rec = None
        series = []
        tt = 0.0
        for k in range(i + 1, min(i + 200, len(cs))):
            tt += cs[k - 1]["dt"]       # time from the start of the landing command to the start of command k
            series.append((tt, cs[k]["movescale"] / base, cs[k]))
            if cs[k]["movescale"] >= base - 5e-5 and rec is None and k > i + 1:
                rec = tt
                break
        k0 = i
        while k0 > 0 and cs[k0 - 1]["ground"] == 0:
            k0 -= 1
        apex = max(cs[k]["poz"] for k in range(max(k0 - 1, 0), i + 1))
        dm = [abs(t["sv"][q["cmd"]]["movescale"] - q["movescale"]) for (_, _, q) in series if q["cmd"] in t["sv"]]
        # dedi series with the same clock (for the authoritative recovery shape)
        sser = [(tt, t["sv"][q["cmd"]]["movescale"] / base) for (tt, _, q) in series if q["cmd"] in t["sv"]]
        out.append({"run": t["run"], "schedule": t["schedule"], "session": t["session"], "i": i,
                    "vz_pre": c["vz"], "h_pre": h0, "h_post": h1, "ratio": h1 / h0 if h0 > 1 else None,
                    "fall_h": apex - c["poz"], "f_next": cs[i + 1]["movescale"] / base, "recover_s": rec, "base": base,
                    "buttons_land": c["buttons"], "duck": c["duck"], "_series": series, "_sv_series": sser,
                    "cl_sv_msc_maxdiff": max(dm) if dm else None})
    return out


def rec_fit(hard, key, p=2.0, eps=0.0):
    best = None
    for Tm in range(950, 1051):
        T = Tm / 1000.0
        res = []
        for l in hard:
            f0 = l["ratio"]
            for row in l[key]:
                tt, fr = row[0] + eps, row[1]
                pred = 1.0 if tt >= T else f0 + (1 - f0) * (tt / T) ** p
                res.append(fr - pred)
        rms = math.sqrt(sum(r * r for r in res) / len(res))
        if best is None or rms < best[0]:
            best = (rms, T, max(abs(r) for r in res), len(res))
    return {"rms": best[0], "T": best[1], "max": best[2], "n": best[3], "p": p, "eps": eps}


def landing_fits(lands):
    hard = [l for l in lands if l["ratio"] is not None and l["ratio"] < 0.999]
    soft = [l for l in lands if l["ratio"] is not None and l["ratio"] >= 0.999]
    res = {"n_hard": len(hard), "n_soft": len(soft),
           "soft_max_impact": max((-l["vz_pre"] for l in soft), default=None),
           "hard_min_impact": min((-l["vz_pre"] for l in hard), default=None)}
    xs1 = [-l["vz_pre"] for l in hard]
    xs2 = [l["vz_pre"] ** 2 for l in hard]
    ys = [l["ratio"] for l in hard]
    if len(hard) >= 3:
        a1, b1, r1, se1, m1 = lin_fit(xs1, ys)
        a2, b2, r2, se2, m2 = lin_fit(xs2, ys)
        res["linear_vz"] = {"a": a1, "b": b1, "rms": r1, "max": m1, "v_f1": (1 - a1) / b1, "v_f0": -a1 / b1}
        res["linear_vz2"] = {"a": a2, "b": b2, "rms": r2, "max": m2, "v_f1": math.sqrt((1 - a2) / b2),
                             "v_f0": math.sqrt(-a2 / b2)}
        # within-cluster slopes (separates the two forms independent of the intercept)
        cl = {}
        for l in hard:
            cl.setdefault(round(-l["vz_pre"] / 100), []).append(l)
        res["cluster_slopes"] = []
        for key, g in sorted(cl.items()):
            if len(g) >= 3:
                aa, bb, rr, se, mm = lin_fit([-l["vz_pre"] for l in g], [l["ratio"] for l in g])
                vm = sum(-l["vz_pre"] for l in g) / len(g)
                res["cluster_slopes"].append({"vz_mean": vm, "n": len(g), "dratio_dvz": bb, "se": se,
                                              "pred_linear": b1, "pred_vz2": 2 * b2 * vm})
    # fall height as the regressor (apex z - landing z), same linear form
    if len(hard) >= 3:
        a3, b3, r3, se3, m3 = lin_fit([l["fall_h"] for l in hard], ys)
        res["linear_fallh"] = {"a": a3, "b": b3, "rms": r3, "max": m3, "h_f1": (1 - a3) / b3, "h_f0": -a3 / b3}
    # recovery: f(t) = f0 + (1-f0)*(t/T)^p, t from the start of the landing command
    # landings whose recovery clock was moved by a dedi correction: residual vs the T=1, p=2 curve > 0.01
    def _r(l):
        return max(abs(fr - (1.0 if tt >= 1.0 else l["ratio"] + (1 - l["ratio"]) * tt * tt)) for (tt, fr, _) in l["_series"])
    corrected = [l for l in hard if _r(l) > 0.01]
    clean = [l for l in hard if l not in corrected]
    res["recovery_corrected_runs"] = [l["run"] for l in corrected]
    rec = {}
    for p in (1.0, 2.0, 3.0):
        rec[f"client_all_p{p:g}"] = rec_fit(hard, "_series", p)
    rec["client_clean_p2"] = rec_fit(clean, "_series", 2.0)
    rec["dedi_all_p2"] = rec_fit(hard, "_sv_series", 2.0)
    best_eps = min((rec_fit(clean, "_series", 2.0, e / 1000.0) for e in range(0, 9)), key=lambda r: r["rms"])
    rec["client_clean_p2_free_eps"] = best_eps
    bestp = None
    for pk in range(150, 251):
        r = rec_fit(clean, "_series", pk / 100.0)
        if bestp is None or r["rms"] < bestp["rms"]:
            bestp = r
    rec["client_clean_free_p"] = bestp
    res["recovery"] = rec
    return res


# ----------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    trials, meta = load(a.sessions)
    R = {"sessions": meta}
    P = {}
    out = print

    out("# M4 Octane analysis\n")
    for m in meta:
        out(f"session {m['session']}: scored trials {m['trials']}, parse errors {m['parse_errors']}, census {m['census']}")
    by = {}
    for t in trials:
        by.setdefault(t["schedule"], []).append(t)
    out("\n## 0. Trials, join and client/dedi parity")
    for sch in sorted(by):
        ts = by[sch]
        js = [t["join"] for t in ts]
        par = [parity(t) for t in ts]
        out(f"{sch:16s} n={len(ts)} runs={[t['run'] for t in ts]} cmds={sum(j['cmds'] for j in js)} "
            f"joined={sum(j['cmds_with_dt'] for j in js)} state_bad={sum(j['state_bad'] for j in js)} "
            f"max|cl-sv| pos/vel={max(p[1] for p in par):.3f} msc={max(p[2] for p in par):.4f}")
    R["trials"] = {sch: [t["run"] for t in ts] for sch, ts in by.items()}

    # ---------------------------------------------------------------- stim
    out("\n## 1. Stim (m4_stim_*, controls m4_ctrl_*)")
    sev = [stim_events(t) for t in trials if t["schedule"].startswith("m4_stim")]
    for e in sev:
        e2 = {k: (round(v, 5) if isinstance(v, float) else v) for k, v in e.items() if not k.startswith("_")}
        out("  " + json.dumps(e2))
    clean = [e for e in sev if not e.get("carry_over") and e.get("onset") is not None]
    carry = [e for e in sev if e.get("carry_over")]
    plateaus = st(e["plateau_msc"] for e in clean)
    walkcaps = [w for e in clean for w in e["plateau_walkcap"]]
    msc_from_cap = st(w / SPEED for w in walkcaps)
    out(f"plateau msc (printed 4 dp): {f(plateaus)}; walk cap during stim {f(st(walkcaps), 3)} -> msc = cap/173.5 = {f(msc_from_cap, 6)}")
    m_st = msc_from_cap["mean"]
    boost = m_st / MSC0
    sev_eff = (boost - 1) / 2
    out(f"boost factor msc/1.15 = {boost:.6f}; severity (extraScale 2) = {sev_eff:.6f}; 0.15 -> 38/255 = {38/255:.6f} "
        f"-> factor {1 + 2 * 38 / 255:.6f}; unquantised 0.15 -> 1.300000")
    ton = st(e["tap_to_onset_s"] for e in clean if "tap_to_onset_s" in e)
    tonc = st(e["tap_to_onset_cmds"] for e in clean if "tap_to_onset_cmds" in e)
    out(f"tap -> onset: {f(ton)} s, {f(tonc, 1)} cmds; onset is a single-command step: "
        f"{sorted(set((round(e['onset_step'][0], 4), round(e['onset_step'][1], 4)) for e in clean if 'onset_step' in e))}")
    full_sv = st(e["full_s_sv"] for e in clean if "full_s_sv" in e)
    full_cl = st(e["full_s_cl"] for e in clean if "full_s_cl" in e)
    tot_sv = st(e["onset_to_end_s_sv"] for e in clean if "onset_to_end_s_sv" in e)
    ramp_sv = st(e["ramp_s_sv"] for e in clean if "ramp_s_sv" in e)
    shift = st(e["rampshift_cmds_cl_minus_sv"] for e in clean if "rampshift_cmds_cl_minus_sv" in e)
    out(f"full strength (onset -> first faded cmd): dedi {f(full_sv)} s, client {f(full_cl)} s")
    out(f"fade (first faded -> back to 1.15): dedi {f(ramp_sv)} s; onset -> end dedi {f(tot_sv)} s")
    out(f"client fade starts {f(shift, 2)} cmds before the dedi; client msc differs from the dedi on fade cmds (first,last rel. to dedi fade start): "
        f"{[e.get('cl_differs_in_fade_cmds') for e in clean if 'ramp_s_sv' in e]}")
    oc = [e.get("onset_cl_minus_sv_cmds") for e in clean if e.get("onset_cl_minus_sv_cmds") is not None]
    out(f"client onset minus dedi onset (cmds): {oc}")
    fade = [s for e in clean for s in e.get("_fade", []) if e.get("ramp_end_sv")]
    fm = fade_models(fade)
    for name, v in fm.get("shapes", {}).items():
        out(f"  fade shape {name:14s}: rms {v['rms']:.5f} max {v['max']:.5f} (fade T {v['T']:.3f} s, time shift {v['shift_s']*1000:+.1f} ms), n={len(fade)}")
    R["stim_events"] = [{k: v for k, v in e.items() if not k.startswith("_")} for e in sev]
    R["stim_fade"] = fm
    out(f"carry-over trials (stim of the previous trial still active at start): {[e['run'] for e in carry]}; "
        f"their tap produced a new stim: {[not e.get('tap_without_onset') for e in carry]}")

    # caps and accelerations
    out("\n### 1b. Caps, accelerations, decel")
    caps = {}
    for t in trials:
        for c in t["cmds"]:
            if c["ground"] and c["join_ok"] and abs(hs(c) - c["maxspeed"]) < 0.002 and abs(hs(c, False) - hs(c)) < 0.002 and c["fwd"] > 0.99:
                key = ("stim" if c["movescale"] > 1.4 else "ctrl" if abs(c["movescale"] - MSC0) < 1e-4 else None,
                       "sprint" if c["sprint"] else "walk")
                if key[0]:
                    caps.setdefault(key, []).append(hs(c))
    for k in sorted(caps):
        s = st(caps[k])
        base = s["mean"] / (m_st if k[0] == "stim" else MSC0)
        out(f"  terminal {k[0]:4s} {k[1]:6s}: {f(s, 3)} -> /msc = {base:.3f}")
        P[f"cap_{k[0]}_{k[1]}"] = s
    bands = {}
    for t in trials:
        for (band, m, an, a_) in accel_bands(t):
            kind = "stim" if m > 1.4 else "ctrl" if abs(m - MSC0) < 1e-4 else "other"
            bands.setdefault((kind, band), []).append(an)
    for k in sorted(bands):
        s = st(bands[k])
        out(f"  accel {k[0]:5s} {k[1]:6s}: a/msc = {f(s, 2)}")
    ss = bands.get(("stim", "sprint"), [])
    near120 = [x for x in ss if abs(x - 120) < 2]
    near100 = [x for x in ss if abs(x - 100) < 2]
    other = [round(x, 2) for x in ss if abs(x - 120) >= 2 and abs(x - 100) >= 2]
    out(f"  stim sprint band split: ~120 {f(st(near120), 3)}; ~100 (stim_sprint mod absent) n={len(near100)}; other {other}")
    mod_off = []
    for t in trials:
        cs = t["cmds"]
        for i in range(1, len(cs)):
            c = cs[i]
            if c["movescale"] > 1.4 and c["sprint"] and c["ground"] and c["fwd"] > 0.99 and c["join_ok"]:
                s0, s1 = hs(c, False), hs(c)
                if s0 >= SPEED * c["movescale"] and s1 > s0 and s1 < c["maxspeed"] - 0.01 and abs((s1 - s0) / c["dt"] / c["movescale"] - 100) < 2:
                    mod_off.append((t["run"], i, round(c["movescale"], 4), round(c["maxspeed"] / c["movescale"], 2)))
    out(f"  commands with boost but sprintAcceleration 100 (run, cmd, msc, maxspeed/msc): {mod_off}")
    R["stim_sprint_mod_absent_cmds"] = mod_off
    bands[("stim", "sprint")] = near120
    R["accel_bands"] = {f"{k[0]}_{k[1]}": st(v) for k, v in bands.items()}
    dec = {}
    for t in trials:
        if t["schedule"].startswith("m4_pad"):
            continue
        for (d, m) in decel_samples(t):
            dec.setdefault("stim" if m > 1.4 else "ctrl" if abs(m - MSC0) < 1e-4 else "other", []).append(d)
    for k, v in sorted(dec.items()):
        out(f"  no-input decel {k}: {f(st(v), 1)} u/s^2")
    R["decel"] = {k: st(v) for k, v in dec.items()}

    # air
    out("\n### 1c. Jump and air strafe with stim (m4_stim_air) vs control (m4_ctrl_air)")
    airs = [air_trial(t) for t in trials if t["schedule"] in ("m4_stim_air", "m4_ctrl_air")]
    airs = [x for x in airs if x]
    for x in airs:
        pr = "; ".join(f"{k}: L={v['Lmax']:.1f} err={v['err']:.3f}" for k, v in x["preds"].items())
        out(f"  r{x['run']} {x['schedule']:12s} msc@jump {x['msc_jump']:.4f} cap {x['maxspeed_jump']:.2f} "
            f"s jump {x['s_pre_jump']:.3f}->{x['s_post_jump']:.3f} vz {x['vz_jump']:.3f} press k={x['press_k']} t={x['tA']:.4f} "
            f"lam={x['lam']:.3f} s {x['s_before']:.3f}->{x['s_after']:.3f} |D|={x['D_len']:.3f} | {pr} | "
            f"other air cmds n={x['air_n']} max resid {x['air_resid_max']:.4f}, max(add) {x['air_add_max']:.1f}")
    R["air"] = airs

    # ---------------------------------------------------------------- pad
    out("\n## 2. Jump pad")
    pads = []
    for t in trials:
        if not t["schedule"].startswith("m4_pad"):
            continue
        lp = pad_launch(t)
        if lp is None:
            continue
        fl = flight_samples(t, lp)
        lp["flight"] = {k: v for k, v in fl.items() if not k.startswith("_")}
        lp["_drift"] = fl["_drift_W"]
        pads.append(lp)
        out(f"  r{lp['run']} {lp['schedule']:13s} dt {lp['dt']:.5f} duck {lp['duck']} in |h| {lp['s_in']:.3f} -> out |h| {lp['h_out']:.3f} "
            f"vz {lp['vz_out']:.3f} dir {lp['dir_out_deg']:+.3f} (in {lp['dir_in_deg']}, yaw {lp['yaw']}) | pred h {lp['pred_h']:.3f} v {lp['pred_v']:.3f} "
            f"| dedi same {lp['sv_same']} | k_xy {fl['k_xy']:.5f} g {fl['g_eff']:.2f} "
            f"air {fl['air_time']:.4f}s rise {fl['apex_rise']:.2f} |h| gain launch->landing {fl['h_gain']:+.3f} "
            f"driftW {fl['drift_W'].get('mean', float('nan')):.3f} n{fl['drift_W']['n']} drift0 {fl['drift_noW'].get('mean', float('nan')):.4f} n{fl['drift_noW']['n']}")
    ks = st(p["flight"]["k_xy"] for p in pads)
    ge = st(p["flight"]["g_eff"] for p in pads)
    out(f"  slow-mo factor k from position (sum dx / sum v*dt): {f(ks, 5)}; "
        f"gravity in velocity units {f(ge, 3)} = 750*{ge['mean']/G:.5f}")
    # launch vz: post-launch vz = Vz - 0.5*g_eff*dt (half-step gravity of the launch command, in slow-mo)
    for duck in (0, 2):
        g = [p for p in pads if (p["duck"] > 0) == (duck > 0)]
        if len(g) >= 3:
            vz0 = st(p["vz_out"] + 0.5 * ge["mean"] * p["dt"] for p in g)
            hx = st(p["h_out"] for p in g)
            out(f"  stance {'ducked' if duck else 'standing'} (n={len(g)}, approach speeds {sorted(set(round(p['s_in'], 2) for p in g))}): "
                f"launch vz = vz_out + 0.5*g*dt = {f(vz0, 4)} vs formula {g[0]['pred_v']:.4f}; "
                f"|h| out {f(hx, 4)} vs formula {g[0]['pred_h']:.4f} (+ one command of W drift)")
            R[f"pad_launch_{'ducked' if duck else 'standing'}"] = {"vz0": vz0, "h_out": hx, "pred_v": g[0]["pred_v"],
                                                                   "pred_h": g[0]["pred_h"]}
    # drift vs vz (W held)
    dW = [d for p in pads for d in p["_drift"]]
    if len(dW) > 10:
        a_, b_, rms, se, mx = lin_fit([v for _, v in dW], [d for d, _ in dW])
        out(f"  W-held horizontal drift in flight: d|h|/dt = {a_:.3f} + {b_:.5f}*vz (rms {rms:.3f}, n={len(dW)}); "
            f"|h| gain launch->landing {f(st(p['flight']['h_gain'] for p in pads), 3)} u/s")
        R["pad_drift"] = {"a": a_, "b": b_, "rms": rms, "n": len(dW)}
    R["pads"] = [{k: v for k, v in p.items() if not k.startswith("_")} for p in pads]
    # jump-in misses
    miss = [jumpin_miss(t, t["cmds"][0]["ox"] + 300.0) for t in trials if t["schedule"] == "m4_pad_jumpin"]
    miss = [m for m in miss if m]
    if miss:
        out(f"  m4_pad_jumpin: no launch in {len(miss)} trials; while within 48 u (radius 32 + hull 16) of the pad axis the feet were "
            f"{f(st(m['min_feet_above_floor'] for m in miss), 2)} u above the floor (trigger above-height 32), airborne={all(m['airborne_all'] for m in miss)}")
    R["pad_jumpin"] = miss
    sx = st(p["x_in"] - p["x0"] - 300.0 for p in pads)
    out(f"  launch command start x relative to the pad centre (reset x + 300): {f(sx, 2)} u")

    # ---------------------------------------------------------------- landing
    out("\n## 3. Landing slowdown")
    lands = [l for t in trials for l in landings(t)]
    for l in lands:
        out(f"  r{l['run']} {l['schedule']:13s} vz_pre {l['vz_pre']:9.3f} |h| {l['h_pre']:8.3f}->{l['h_post']:8.3f} ratio {l['ratio']:.5f} "
            f"msc_next/base {l['f_next']:.5f} recover {l['recover_s'] if l['recover_s'] is None else round(l['recover_s'], 4)} s "
            f"fall {l['fall_h']:.2f} u buttons {l['buttons_land']:08x} max|cl-sv| msc {l['cl_sv_msc_maxdiff']:.4f}")
    lf = landing_fits(lands)
    out(f"  soft landings: n={lf['n_soft']}, max impact {lf['soft_max_impact']:.1f}; hard: n={lf['n_hard']}, min impact {lf['hard_min_impact']:.1f}")
    for k in ("linear_vz", "linear_vz2"):
        v = lf.get(k)
        if v:
            out(f"  f0 model {k:10s}: f0 = {v['a']:.6f} + {v['b']:.4e}*x  rms {v['rms']:.5f} max {v['max']:.5f}; f0=1 at |vz|={v['v_f1']:.1f}, f0=0 at |vz|={v['v_f0']:.1f}")
    for c in lf.get("cluster_slopes", []):
        out(f"  cluster |vz|~{c['vz_mean']:.1f} n={c['n']}: d f0/d|vz| = {c['dratio_dvz']:.6f} (se {c['se']:.6f}); "
            f"linear-|vz| predicts {c['pred_linear']:.6f}, vz^2 predicts {c['pred_vz2']:.6f}")
    v = lf.get("linear_fallh")
    if v:
        out(f"  f0 model fall height: f0 = {v['a']:.6f} + {v['b']:.4e}*H  rms {v['rms']:.5f} max {v['max']:.5f}; f0=1 at H={v['h_f1']:.1f}, f0=0 at H={v['h_f0']:.1f}")
    out(f"  landings whose recovery the dedi delayed (client corrected; residual vs T=1 curve > 0.01): {lf['recovery_corrected_runs']}")
    for k, v in lf["recovery"].items():
        out(f"  recovery {k:26s}: f = f0 + (1-f0)*((t+{v['eps']*1000:.0f}ms)/T)^{v['p']:.2f}: best T {v['T']:.3f} s, rms {v['rms']:.5f}, max {v['max']:.5f}, n={v['n']}")
    R["landings"] = [{k: v for k, v in l.items() if not k.startswith("_")} for l in lands]
    R["landing_fits"] = lf

    # ---------------------------------------------------------------- params
    hard = [l for l in lands if l["ratio"] is not None and l["ratio"] < 0.999]
    stand = [p for p in pads if p["duck"] == 0]
    duckp = [p for p in pads if p["duck"] > 0]
    v2 = lf.get("linear_vz2", {})

    def prm(value, unit, source, n=None, spread=None, note=None):
        d = {"value": value, "unit": unit, "source": source}
        if n is not None:
            d["n"] = n
        if spread is not None:
            d["spread"] = spread
        if note:
            d["note"] = note
        return d

    sprint_st = bands.get(("stim", "sprint"), [])
    P2 = {
        "_scope": "Octane (character_octane), R5Flowstate S21 client / S3 dedi, 120 fps, lane C flat floor; sessions M4_octane + M4_octane_rerun",
        "stim.boost_factor": prm(round(boost, 6), "x movescale", "fitted (walk cap / 173.5 / 1.15)", msc_from_cap["n"],
                                 f"sd {msc_from_cap['sd']:.2e}", "= 1 + 2*severity; severity 0.15 stored as 38/255 = 0.14902"),
        "stim.severity_effective": prm(round(sev_eff, 6), "-", "fitted; script 0.15 (sh_stim.gnut:12)", msc_from_cap["n"]),
        "stim.tap_to_onset": prm(round(ton["mean"], 4), "s", "observed", ton["n"], f"{ton['min']:.4f}..{ton['max']:.4f}",
                                 "19-20 cmds at 120 fps; weapon deploy 0.15 s [inf]"),
        "stim.full_duration": prm(round(full_sv["mean"], 4), "s", "observed (dedi)", full_sv["n"], f"sd {full_sv['sd']:.4f}",
                                  "script duration 6.0 s; first faded command at 6.0 s after onset"),
        "stim.fade_duration": prm(round(ramp_sv["mean"], 4), "s", "observed (dedi)", ramp_sv["n"], f"sd {ramp_sv['sd']:.4f}",
                                  "script fade 0.5 s; shape: see fade_shape"),
        "stim.fade_shape": prm(min(fm["shapes"], key=lambda k: fm["shapes"][k]["rms"]) if fm.get("shapes") else None, "-", "fitted",
                               len(fade), None, json.dumps({k: round(v["rms"], 5) for k, v in fm.get("shapes", {}).items()})),
        "stim.sprintspeed_mod": prm(round(st(caps.get(("stim", "sprint"), [0]))["mean"] / m_st, 3), "u/s", "fitted (sprint cap / msc)",
                                    len(caps.get(("stim", "sprint"), [])), None, "stim_sprint mod: base 260 -> 282"),
        "stim.sprintAcceleration_mod": prm(round(st(sprint_st)["mean"], 2) if sprint_st else None, "u/s^2 (x msc)", "fitted",
                                           len(sprint_st), f"sd {st(sprint_st)['sd']:.3f}" if sprint_st else None, "base 100 -> 120"),
        "stim.walk_speed": prm(SPEED, "u/s (x msc)", "fitted: unchanged", len(caps.get(("stim", "walk"), []))),
        "stim.acceleration": prm(round(st(bands.get(("stim", "walk"), [0]))["mean"], 2), "u/s^2 (x msc)", "fitted: unchanged",
                                 len(bands.get(("stim", "walk"), []))),
        "stim.lowAcceleration": prm(round(st(bands.get(("stim", "low"), [0]))["mean"], 1), "u/s^2 (x msc)", "fitted: unchanged",
                                    len(bands.get(("stim", "low"), []))),
        "stim.deceleration": prm(round(st(dec.get("stim", [0]))["mean"], 1), "u/s^2 (not x msc)", "fitted: unchanged",
                                 len(dec.get("stim", []))),
        "pad.push_speed": prm(PAD_PUSH, "u/s", "script JUMP_PAD_PUSH_VELOCITY; confirmed", len(pads),
                              f"h_out {st(p['h_out'] for p in stand)['mean']:.3f} vs pred {stand[0]['pred_h']:.3f}" if stand else None),
        "pad.vert_override": prm(PAD_VERT, "-", "script JUMP_PAD_VERT_OVERRIDE; confirmed", len(stand)),
        "pad.ducked_vert_scalar": prm(PAD_DUCK, "-", "SDK cvar; confirmed", len(duckp)),
        "pad.launch_h_standing": prm(round(PAD_PUSH / math.sqrt(5), 3), "u/s", "formula, observed +1 tick drift", len(stand),
                                     f"{f(st(p['h_out'] for p in stand), 3)}" if stand else None),
        "pad.launch_vz_standing": prm(round(2 * PAD_PUSH / math.sqrt(5), 3), "u/s", "formula; intercept fit",
                                      len(stand), f"launch vz {f(R['pad_launch_standing']['vz0'], 4)}"),
        "pad.launch_h_ducked": prm(round(PAD_PUSH / math.sqrt(2), 3), "u/s", "formula", len(duckp),
                                   f"{f(st(p['h_out'] for p in duckp), 3)}" if duckp else None),
        "pad.launch_vz_ducked": prm(round(PAD_PUSH / math.sqrt(2), 3), "u/s", "formula; intercept fit", len(duckp),
                                    f"launch vz {f(R['pad_launch_ducked']['vz0'], 4)}"),
        "pad.slowmo_timescale": prm(round(ks["mean"], 4), "-", "fitted (position step / (v*dt)); m_slowMoEnabled [src]", ks["n"],
                                    f"sd {ks['sd']:.5f}", f"gravity in velocity units {ge['mean']:.2f} = 750*{ge['mean']/G:.4f}"),
        "pad.debounce": prm(1.0, "s", "SDK constant; not exercised"),
        "pad.double_jump_delay": prm(0.1, "s", "SDK cvar; not exercised"),
        "land.f0_model": prm("f0 = clamp(a + b*vz^2, 0, 1)", "-", "fitted (two impact clusters)", len(hard), None,
                             json.dumps({k: (round(v, 9) if isinstance(v, float) else v) for k, v in v2.items()})),
        "land.f0_onset_impact": prm(round(v2.get("v_f1", float("nan")), 1), "u/s", "fitted (extrapolated)", len(hard)),
        "land.f0_zero_impact": prm(round(v2.get("v_f0", float("nan")), 1), "u/s", "fitted (extrapolated)", len(hard)),
        "land.recovery_T": prm(lf["recovery"]["client_clean_p2"]["T"], "s", "fitted (client, uncorrected landings); census landSlowdownDuration 1",
                               lf["recovery"]["client_clean_p2"]["n"], f"rms {lf['recovery']['client_clean_p2']['rms']:.5f} (in f)"),
        "land.recovery_exponent": prm(2, "-", "fitted", None, f"free p: {lf['recovery']['client_clean_free_p']['p']:.2f}"),
        "lurch.clamp": prm("0.7 * sprint cap (sprintspeed * msc)", "u/s", "fitted: M3 lurch clamp under stim", len(airs),
                           f"stim 294.667 = 0.7*420.954; ctrl 209.3 = 0.7*299",
                           "resolves M3 open question 2; 209.3 const and 182*msc rejected (errors 85 / 23 u/s)"),
        "land.no_slowdown_max_observed_impact": prm(round(lf["soft_max_impact"], 1), "u/s", "observed"),
    }
    R["params"] = P2
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(P2, fh, indent=1)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(R, fh, indent=1, default=lambda o: None)


if __name__ == "__main__":
    main(sys.argv[1:])
