#!/usr/bin/env python3
"""M2 / E5: slide and slide-jump momentum from hsd_session.py folders.

  py -3 slide_analysis.py <session folder> [<session folder> ...] [--json out.json] [--verbose]

Physics truth = client MOVE-TRACE first-time rows (side cl, not replay) of each scored trial
(runner.json: ok=true, warmup=false). Per-usercmd dt comes from the HSD client frame whose state equals
the command's post-state (SAMPLING-PHASE.md: frame = post of the latest usercmd, ft = its frametime).
The dedi MT rows (joined by hsdtel) and the dedi HSD events are used for parity only.

Trials used: schedules e5_slide, e5_slidejump02, e5_slidejump06 (and e1_sprint as a sprint baseline when
present). Nothing is fitted on dedi data. Stdlib only; no local paths.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-prep", "tools"))
from hsdtel import derive, parse  # noqa: E402

IN_JUMP, IN_DUCK, IN_SPEED = 0x2, 0x4, 1 << 15  # sprint is bit 15 in this build (see hsdtel schema.BUTTON_BITS)
SCHEDS = ("e5_slide", "e5_slidejump02", "e5_slidejump06", "e1_sprint")
XCHECK = ("e4_stand",)
CENSUS = {  # E0 census (T0 smoke report/census.csv), cl classvar == cl setting == sv setting
    "slideAccel": 50, "slideDecel": 100, "slideVelocityDecay": 0.7, "slideRequiredStartSpeed": 200,
    "slideSpeedBoost": 150, "slideSpeedBoostCap": 400, "slideJumpHeight": 50, "slideMaxJumpSpeed": 350,
    "slideStopSpeed": 125, "slideMaxStopSpeed": 350, "slideWantToStopDecel": 400, "jumpHeight": 56,
    "deceleration": 1250, "landSlowdownDuration": 1, "gravityScale": 1,
}
G_SV = 750.0  # sv_gravity default (Movement-Analysis.md 4.1); checked against the data below


def spd(vx, vy):
    return math.hypot(vx, vy)


def pre(r):
    return spd(r["vx"], r["vy"])


def post(r):
    return spd(r["pvx"], r["pvy"])


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    m = st.fmean(xs)
    sd = st.pstdev(xs) if len(xs) > 1 else 0.0
    return {"n": len(xs), "mean": m, "sd": sd, "min": min(xs), "max": max(xs),
            "spread_pct": (100.0 * (max(xs) - min(xs)) / abs(m)) if m else None}


def linfit(xs, ys):
    """least squares y = a + b x -> (a, b, rmse)."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    rmse = math.sqrt(sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / n)
    return a, b, rmse


# ------------------------------------------------------------------ loading and the dt join
def load(folder):
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    mt, fr, ev = {}, {}, {}
    for r in rows:
        run = r.get("drv_run")
        if r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay"):
            mt.setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "cl" and r.get("kind") == "frame":
            fr.setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "sv" and r.get("kind") == "evt":
            ev.setdefault(run, []).append(r)
    for d in (mt, fr, ev):
        for v in d.values():
            v.sort(key=lambda r: (r.get("cmd") if r["source"] == "MT" else r.get("seq")) or 0)
    return runner, mt, fr, ev, len(issues)


def key_post(r):
    return tuple(round(r[k], 3) for k in ("pox", "poy", "poz", "pvx", "pvy", "pvz"))


def key_frame(f):
    return tuple(round(f[k], 3) for k in ("ox", "oy", "oz", "vx", "vy", "vz"))


def join_dt(cmds, frames):
    """Attach r['dt'] = ft of the HSD frame that shows this command's post-state.

    A frame is joined to a command when its 6 state values equal the command's post values (print
    precision 0.001) and the command is the latest such one at or before the frame's wall time
    (+20 ms slack for the ms log stamp). Only *moving* frames (|v| > 1) are joined; static frames match
    many commands and are not needed here (all fitted commands move). Returns join statistics."""
    by_key = {}
    for i, r in enumerate(cmds):
        by_key.setdefault(key_post(r), []).append(i)
    moving = [f for f in frames if abs(f["vx"]) > 1 or abs(f["vy"]) > 1 or abs(f["vz"]) > 1]
    joined, multi, none, ft_vs_est = 0, 0, 0, []
    last_i = -1
    steps = []
    for f in moving:
        cand = [i for i in by_key.get(key_frame(f), []) if cmds[i].get("wall", 0) <= f.get("wall", 0) + 0.02]
        if not cand:
            none += 1
            continue
        if len(cand) > 1:
            multi += 1
        i = max(cand)
        r = cmds[i]
        r["dt"] = f["ft"]
        joined += 1
        if last_i >= 0:
            steps.append(i - last_i)
        last_i = i
        if r.get("drv_dt_est") and post(r) > 150:
            ft_vs_est.append(abs(f["ft"] - r["drv_dt_est"]))
    return {"moving_frames": len(moving), "joined": joined, "unjoined": none, "multi_candidate": multi,
            "step1_frac": (sum(1 for s in steps if s == 1) / len(steps)) if steps else None,
            "ft_minus_dtest_abs_median_us": (st.median(ft_vs_est) * 1e6) if ft_vs_est else None,
            "ft_minus_dtest_abs_p95_us": (sorted(ft_vs_est)[int(0.95 * (len(ft_vs_est) - 1))] * 1e6) if ft_vs_est else None}


# ------------------------------------------------------------------ per-trial analysis
def slide_segments(cmds):
    """contiguous runs of the pre-move slide flag -> list of (first index, last index)."""
    segs, s = [], None
    for i, r in enumerate(cmds):
        if r["slide"] == 1 and s is None:
            s = i
        elif r["slide"] != 1 and s is not None:
            segs.append((s, i - 1))
            s = None
    if s is not None:
        segs.append((s, len(cmds) - 1))
    return segs


def decay_points(cmds, a, b):
    """grounded slide commands without a jump press and with a joined dt: (v_pre, v_post, dt, duck)."""
    pts = []
    for r in cmds[a:b + 1]:
        if r["ground"] != 1 or r["buttons"] & IN_JUMP or r.get("dt") is None:
            continue
        if r["pvz"] != 0 or abs(r["poz"] - r["oz"]) > 0.5:
            continue
        pts.append((pre(r), post(r), r["dt"], r["duck"]))
    return pts


def fit_decay(pts):
    """Compare three decel laws on a = (v_pre - v_post)/dt:
       M1 constant a = D;  M2 a = D + k v (= v*decay^dt - D dt, decay = e^-k);  M3 a = k v."""
    vs = [p[0] for p in pts]
    acc = [(p[0] - p[1]) / p[2] for p in pts]
    d1 = st.fmean(acc)
    r1 = math.sqrt(st.fmean([(x - d1) ** 2 for x in acc]))
    D2, k2, r2 = linfit(vs, acc)
    k3 = sum(v * x for v, x in zip(vs, acc)) / sum(v * v for v in vs)
    r3 = math.sqrt(st.fmean([(x - k3 * v) ** 2 for v, x in zip(vs, acc)]))
    # residual in speed units (u/s) per command for M2, closed-form step v' = v*exp(-k dt) - D dt
    res = [p[1] - (p[0] * math.exp(-k2 * p[2]) - D2 * p[2]) for p in pts]
    # the census law with no free parameter: decay 0.7 per second, decel 100 u/s^2
    out = {"n": len(pts), "v_range": [min(vs), max(vs)],
            "M1_const_D": d1, "M1_rmse_acc": r1,
            "M2_D": D2, "M2_k": k2, "M2_decay": math.exp(-k2), "M2_rmse_acc": r2,
            "M2_res_speed_rms": math.sqrt(st.fmean([x * x for x in res])), "M2_res_speed_maxabs": max(abs(x) for x in res),
            "M3_k": k3, "M3_rmse_acc": r3}
    # the census law with no free parameter (decay 0.7 per second, decel 100 u/s^2) in three step orderings
    for name, step in STEPS.items():
        resc = [p[1] - step(p[0], p[2]) for p in pts]
        out[f"census_{name}_res_mean"] = st.fmean(resc)
        out[f"census_{name}_res_rms"] = math.sqrt(st.fmean([x * x for x in resc]))
        out[f"census_{name}_res_maxabs"] = max(abs(x) for x in resc)
    return out


KC = -math.log(CENSUS["slideVelocityDecay"])
DC = CENSUS["slideDecel"]
STEPS = {  # one usercmd of slide friction, census values, three orderings
    "decelThenDecay": lambda v, dt: (v - DC * dt) * math.exp(-KC * dt),
    "decayThenDecel": lambda v, dt: v * math.exp(-KC * dt) - DC * dt,
    "odeExact": lambda v, dt: (v + DC / KC) * math.exp(-KC * dt) - DC / KC,
}


def crouch_decel(cmds, a):
    """after slide end: deceleration while above the crouch max speed, then the steady speed."""
    acc, steady = [], []
    for r in cmds[a:]:
        if r["slide"] == 1 or r["ground"] != 1 or not r["buttons"] & IN_DUCK:
            break
        if r.get("dt") is None:
            continue
        if post(r) > r["maxspeed"] + 0.01:
            acc.append((pre(r) - post(r)) / r["dt"])
        elif pre(r) > r["maxspeed"] + 0.01:
            pass  # clamped step (lands exactly on maxspeed)
        else:
            steady.append(post(r))
    return acc, steady


def trial(sched, cmds, evts):
    out = {"schedule": sched, "cmds": len(cmds)}
    g_air = [(r["vz"] - r["pvz"]) / r["dt"] for r in cmds if r["ground"] == 0 and r.get("dt") and r["pvz"] != 0
             and r["vz"] != 0 and abs(r["poz"] - r["oz"]) > 0.01]
    out["gravity"] = st.median(g_air) if g_air else None
    if sched == "e4_stand":  # --jump-xcheck only: calibrates the jump-command vz offset on a plain jump
        j = next(i for i, r in enumerate(cmds) if r["ground"] == 1 and r["vz"] == 0 and r["pvz"] > 100)
        rj = cmds[j]
        out["plain_pvz"] = rj["pvz"]
        out["plain_dt"] = rj["dt"]
        out["plain_H_est_1p5"] = (rj["pvz"] + 1.5 * G_SV * rj["dt"]) ** 2 / (2 * G_SV)
        out["plain_H_est_1p0"] = (rj["pvz"] + 1.0 * G_SV * rj["dt"]) ** 2 / (2 * G_SV)
        out["plain_H_census"] = CENSUS["jumpHeight"]
        return out
    if sched == "e1_sprint":
        sp = [post(r) for r in cmds if r["sprint"] == 1 and r["ground"] == 1]
        out["sprint_cruise"] = st.median(sp) if sp else None
        out["sprint_maxspeed"] = sorted({r["maxspeed"] for r in cmds if r["sprint"] == 1})
        out["movescale"] = sorted({r["movescale"] for r in cmds})
        stop = [(pre(r) - post(r)) / r["dt"] for r in cmds if r.get("dt") and r["ground"] == 1 and r["fwd"] == 0
                and r["duck"] == 0 and post(r) > 1 and pre(r) - post(r) > 0.01]
        out["stand_stop_decel"] = st.fmean(stop) if stop else None
        out["stand_stop_decel_n"] = len(stop)
        return out
    segs = slide_segments(cmds)
    out["segments"] = len(segs)
    a, b = segs[0]
    s0 = cmds[a]
    duck_i = next(i for i, r in enumerate(cmds) if r["buttons"] & IN_DUCK)
    before = cmds[a - 1]
    out["movescale"] = sorted({r["movescale"] for r in cmds})
    out["duck_press_index_minus_slide_start"] = duck_i - a
    out["entry_speed"] = post(before)
    out["entry_sprint"] = before["sprint"]
    out["entry_maxspeed"] = before["maxspeed"]
    out["peak_speed"] = pre(s0)  # pre-state of the first slide command already carries the boost
    out["peak_is_max"] = max(post(r) for r in cmds[a:b + 1]) <= pre(s0) + 1e-6
    out["boost"] = pre(s0) - post(before)
    out["slide_maxspeed"] = s0["maxspeed"]
    out["sv_peak_parity"] = (abs(pre(s0) - pre(s0["_join"])) if s0.get("_join") else None)
    pts = decay_points(cmds, a, b)
    out["decay_seg1"] = fit_decay(pts)
    allpts = [q for (c, d) in segs for q in decay_points(cmds, c, d)]
    out["decay_all_segments"] = fit_decay(allpts)
    out["decay_seg1_duck1"] = fit_decay([p for p in pts if p[3] == 1]) if sum(1 for p in pts if p[3] == 1) > 5 else None
    out["decay_seg1_duck2"] = fit_decay([p for p in pts if p[3] == 2]) if sum(1 for p in pts if p[3] == 2) > 5 else None
    # dedi parity over the whole trial: |client post speed - dedi post speed|
    par = [abs(post(r) - post(r["_join"])) for r in cmds if r.get("_join")]
    out["sv_parity_postspeed_maxabs"] = max(par) if par else None
    out["sv_join_frac"] = len(par) / len(cmds)
    out["sv_slide_flag_mismatch"] = sum(1 for r in cmds if r.get("_join") and r["_join"]["slide"] != r["slide"])
    out["sv_events"] = sorted({e.get("evt") for e in evts})
    if sched == "e5_slide":
        t_slide = sum(r["dt"] for r in cmds[a:b + 1] if r.get("dt"))
        out["slide_duration_s"] = t_slide
        out["slide_cmds"] = b - a + 1
        out["end_last_slide_post"] = post(cmds[b])
        out["end_last_slide_pre"] = pre(cmds[b])
        out["end_first_noslide_duck"] = cmds[b + 1]["duck"]
        out["end_duck_held"] = bool(cmds[b + 1]["buttons"] & IN_DUCK)
        acc, steady = crouch_decel(cmds, b + 1)
        out["crouch_decel"] = st.fmean(acc) if acc else None
        out["crouch_decel_n"] = len(acc)
        out["crouch_steady"] = st.median(steady) if steady else None
        out["crouch_maxspeed"] = cmds[b + 1]["maxspeed"]
        out["sim_census_end"] = simulate_slide(pre(s0), [r["dt"] for r in cmds[a:] if r.get("dt")])
        out["obs_end_cmds"] = b - a + 1
        return out
    # slide jumps
    j = next(i for i in range(a, len(cmds)) if cmds[i]["buttons"] & IN_JUMP and not cmds[i - 1]["buttons"] & IN_JUMP)
    rj = cmds[j]
    out["jump_cmds_after_slide_start"] = j - a
    out["jump_time_after_boost_s"] = sum(r["dt"] for r in cmds[a:j] if r.get("dt"))  # boost applied at start of cmd a
    out["jump_time_incl_jump_cmd_s"] = out["jump_time_after_boost_s"] + (rj.get("dt") or 0)
    out["jump_in_slide"] = rj["slide"] == 1 and rj["ground"] == 1
    out["jump_duck"] = rj["duck"]
    out["takeoff_pre_speed"] = pre(rj)
    out["takeoff_post_speed"] = post(rj)
    out["takeoff_delta"] = post(rj) - pre(rj)
    out["takeoff_pvz"] = rj["pvz"]
    out["jump_dt"] = rj.get("dt")
    g = out["gravity"] or G_SV
    out["takeoff_v0_est"] = rj["pvz"] + g * rj["dt"] if rj.get("dt") else None
    # jump command post vz = sqrt(2 g H) - 1.5 g dt (calibrated on plain standing jumps, see --jump-xcheck)
    out["takeoff_H_est"] = ((rj["pvz"] + 1.5 * G_SV * rj["dt"]) ** 2 / (2 * G_SV)) if rj.get("dt") else None
    out["takeoff_pvz_pred_H50"] = (math.sqrt(2 * G_SV * CENSUS["slideJumpHeight"]) - 1.5 * G_SV * rj["dt"]) if rj.get("dt") else None
    out["takeoff_pvz_res_H50"] = rj["pvz"] - out["takeoff_pvz_pred_H50"] if rj.get("dt") else None
    out["takeoff_refund_expected"] = out["takeoff_pre_speed"] - out["boost"]
    out["takeoff_dz"] = rj["poz"] - rj["oz"]
    z0 = rj["oz"]
    land = next(i for i in range(j + 1, len(cmds)) if cmds[i]["ground"] == 1)
    air = cmds[j + 1:land]
    out["apex_height"] = max(r["poz"] for r in [rj] + air) - z0
    out["airtime_s"] = sum(r["dt"] for r in [rj] + air if r.get("dt"))
    out["air_speed_gain"] = post(cmds[land - 1]) - post(rj)
    out["land_speed"] = pre(cmds[land])
    out["land_slide_flag"] = cmds[land]["slide"]
    out["land_duck"] = cmds[land]["duck"]
    rl = cmds[land]
    out["land_first_cmd_decel"] = (pre(rl) - post(rl)) / rl["dt"] if rl.get("dt") else None
    out["land_first_cmd_decel_census"] = CENSUS["slideDecel"] - math.log(CENSUS["slideVelocityDecay"]) * pre(rl)
    segs2 = [s for s in segs if s[0] >= land]
    if segs2:
        c, d = segs2[0]
        out["post_land_slide"] = fit_decay(decay_points(cmds, c, d))
        out["post_land_slide_end_post"] = post(cmds[d])
        out["post_land_slide_cmds"] = d - c + 1
        out["post_land_slide_boost"] = pre(cmds[c]) - post(cmds[c - 1])
    ej = [e for e in evts if e.get("evt") == "JUMP"]
    if ej:
        out["sv_jump_evt_speed"] = spd(ej[0]["vx"], ej[0]["vy"])
    if rj.get("_join"):
        out["sv_takeoff_post_speed"] = post(rj["_join"])
        out["sv_takeoff_pvz"] = rj["_join"]["pvz"]
    return out


def simulate_slide(v0, dts, stop=None):
    """census law with no free parameter, using the observed per-command dt; returns commands until
    the post speed drops below slideStopSpeed (the observed end rule)."""
    stop = CENSUS["slideStopSpeed"] if stop is None else stop
    v = v0
    for n, dt in enumerate(dts, 1):
        v = STEPS["decelThenDecay"](v, dt)
        if v < stop:
            return {"cmds": n, "end_post": v}
    return None


# ------------------------------------------------------------------ aggregation
def agg(trials, path):
    vals = []
    for t in trials:
        v = t
        for p in path:
            v = v.get(p) if isinstance(v, dict) else None
        vals.append(v)
    return stats([v for v in vals if isinstance(v, (int, float))])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params", help="write params.json here")
    ap.add_argument("--jump-xcheck", action="store_true",
                    help="also read ok e4_stand trials (plain standing jump) to calibrate the jump-command vz offset")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)
    use = SCHEDS + (XCHECK if a.jump_xcheck else ())
    per = {s: [] for s in use}
    joins = []
    for folder in a.sessions:
        runner, mt, fr, ev, nissues = load(folder)
        sess = os.path.basename(os.path.normpath(folder))
        for t in runner["trials"]:
            if t.get("warmup") or not t.get("ok") or t["schedule"] not in use:
                continue
            run = f"r{t['run']}"
            cmds = mt.get(run, [])
            frames = fr.get(run, [])
            if not cmds:
                continue
            js = join_dt(cmds, frames)
            js.update({"session": sess, "run": run, "cmds": len(cmds), "frames": len(frames)})
            joins.append(js)
            res = trial(t["schedule"], cmds, ev.get(run, []))
            res.update({"session": sess, "run": run, "measured_fps": t.get("measured_fps"), "yaw": t.get("yaw")})
            per[t["schedule"]].append(res)
    summary = {"join": joins, "trials": per, "agg": {}}
    A = summary["agg"]
    for s, ts in per.items():
        if not ts:
            continue
        keys = {}
        for t in ts:
            for k, v in t.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    keys.setdefault(k, None)
                elif isinstance(v, dict):
                    for k2, v2 in v.items():
                        if isinstance(v2, (int, float)):
                            keys.setdefault(k + "." + k2, None)
        A[s] = {k: agg(ts, k.split(".")) for k in keys}
    pooled = [t for s in ("e5_slide", "e5_slidejump02", "e5_slidejump06") for t in per.get(s, [])]
    A["pooled_slide_trials"] = {k: agg(pooled, ["decay_all_segments", k]) for k in
                                ("n", "M2_D", "M2_decay", "M2_k", "M2_res_speed_rms", "M1_const_D", "M1_rmse_acc", "M3_rmse_acc",
                                 "M2_rmse_acc", "census_decelThenDecay_res_mean", "census_decelThenDecay_res_rms",
                                 "census_decayThenDecel_res_mean", "census_decayThenDecel_res_rms",
                                 "census_odeExact_res_mean", "census_odeExact_res_rms",
                                 "census_decelThenDecay_res_maxabs")}
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(build_params(A), fh, indent=1)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=1, default=str)
    report(summary, a.verbose)
    return 0


# ------------------------------------------------------------------ params.json
def build_params(A):
    """Every parameter: value, unit, source (census key and/or fitted), n, spread, formula, evidence."""
    def g(sched, key):
        return A.get(sched, {}).get(key, {"n": 0})

    def sp(x):
        return ({"sd": x.get("sd"), "min": x.get("min"), "max": x.get("max"), "spread_pct": x.get("spread_pct")}
                if x.get("n") else None)

    S, J2, J6, PO = "e5_slide", "e5_slidejump02", "e5_slidejump06", "pooled_slide_trials"
    pk, bo = g(S, "peak_speed"), g(S, "boost")
    D, dec = A[PO]["M2_D"], A[PO]["M2_decay"]
    grav = [A[s]["gravity"] for s in (J2, J6) if s in A]
    out = {
        "_meta": {
            "experiment": "M2 E5 slide and slide-jump momentum",
            "truth": "client MOVE-TRACE first-time usercmds; dt per usercmd = FrameTime() of the joined HSD client frame",
            "trials": {k: g(k, "cmds").get("n", 0) for k in (S, J2, J6, "e1_sprint")},
            "movescale": 1.15, "units": "Source units (u), seconds",
            "evidence_levels": "A = observed exactly (spread ~0) in every trial; B = fitted, spread <= 5 %; "
                               "C = consistent but only one operating point or bracketed; D = census value, not exercised",
        },
        "slideRequiredStartSpeed": {
            "value": CENSUS["slideRequiredStartSpeed"], "unit": "u/s", "source": "census slideRequiredStartSpeed",
            "n": 0, "spread": None, "evidence": "D",
            "formula": "slide starts on the duck-press usercmd when grounded and |v_xy| >= value "
                       "(threshold not exercised: slide entries were at 299, 248 and 350 u/s)"},
        "slideSpeedBoost": {
            "value": CENSUS["slideSpeedBoost"], "unit": "u/s (times movescale)",
            "source": "census slideSpeedBoost; data only bound it: slideSpeedBoost*msc >= 161 (unscaled 150 rejected)",
            "n": bo.get("n"), "observed_gain": bo.get("mean"), "spread": sp(bo), "evidence": "C",
            "formula": "v_peak = min(v_entry + slideSpeedBoost*msc, slideSpeedBoostCap*msc); lastSlideBoost = v_peak - v_entry"},
        "slideSpeedBoostCap": {
            "value": CENSUS["slideSpeedBoostCap"], "unit": "u/s (times movescale)",
            "source": "census slideSpeedBoostCap; observed peak = 400 * 1.15",
            "n": pk.get("n"), "observed_peak": pk.get("mean"), "spread": sp(pk),
            "evidence": "A for 460 at msc 1.15 from 299; C for the scaling (one movescale)",
            "formula": "cap = slideSpeedBoostCap * movescale = 460 u/s"},
        "slideDecel": {
            "value": CENSUS["slideDecel"], "fitted": D.get("mean"), "unit": "u/s^2",
            "source": "census slideDecel (unscaled), confirmed: free fit a = D + k*v per trial over all slide usercmds",
            "census_law_residual_u_per_s_per_cmd": {k: A[PO][k].get("mean") for k in (
                "census_decelThenDecay_res_mean", "census_decelThenDecay_res_rms", "census_decelThenDecay_res_maxabs")},
            "n": D.get("n"), "spread": sp(D), "evidence": "B",
            "formula": "per usercmd: v' = (v - slideDecel*dt) * slideVelocityDecay^dt"},
        "slideVelocityDecay": {
            "value": CENSUS["slideVelocityDecay"], "fitted": dec.get("mean"), "unit": "fraction of speed kept per second",
            "source": "census slideVelocityDecay, confirmed: free fit exp(-k) per trial", "n": dec.get("n"), "spread": sp(dec),
            "evidence": "B", "formula": "k = -ln(0.7) = 0.3567 1/s"},
        "slideStopSpeed": {
            "value": CENSUS["slideStopSpeed"], "unit": "u/s",
            "source": "census slideStopSpeed; last slide usercmd has pre >= 125 and post < 125",
            "n": g(S, "end_last_slide_post").get("n"), "observed_last_post": g(S, "end_last_slide_post").get("mean"),
            "observed_last_pre": g(S, "end_last_slide_pre").get("mean"), "spread": sp(g(S, "end_last_slide_post")),
            "evidence": "A", "formula": "slide ends after the first usercmd whose post speed < slideStopSpeed (unscaled)"},
        "slideDuration_from460": {
            "value": g(S, "slide_duration_s").get("mean"), "unit": "s", "source": "observed (a consequence, not an input)",
            "n": g(S, "slide_duration_s").get("n"), "spread": sp(g(S, "slide_duration_s")), "evidence": "A",
            "formula": "continuous: t = ln((v0 + D/k) / (125 + D/k)) / k = 1.689 s for v0 = 460; "
                       "the census law stepped on the observed dt ends on the same usercmd (244) in 5/5 trials"},
        "crouchOverspeedDecel": {
            "value": 1500.0, "fitted": g(S, "crouch_decel").get("mean"), "unit": "u/s^2",
            "source": "fitted, rounded; no census key identified (standing decel = deceleration 1250; ratio 1.2)",
            "n": g(S, "crouch_decel").get("n"), "spread": sp(g(S, "crouch_decel")),
            "evidence": "B (3 usercmds per trial)", "formula": "ducked, after the slide: v' = max(v - 1500*dt, 92)"},
        "crouchMaxSpeed": {
            "value": g(S, "crouch_steady").get("mean"), "unit": "u/s", "source": "observed MT maxspeed (ms=92) and steady speed",
            "n": g(S, "crouch_steady").get("n"), "spread": sp(g(S, "crouch_steady")), "evidence": "A",
            "formula": "crouch-walk speed at movescale 1.15"},
        "standStopDecel": {
            "value": 1250.0, "fitted": g("e1_sprint", "stand_stop_decel").get("mean"), "unit": "u/s^2",
            "source": "fitted on e1_sprint release (baseline) == census deceleration",
            "n": g("e1_sprint", "stand_stop_decel").get("n"), "spread": sp(g("e1_sprint", "stand_stop_decel")),
            "evidence": "B (baseline only)", "formula": "standing, no input: v' = v - 1250*dt"},
        "slideBoostRefundWindow": {
            "value": 0.4, "unit": "s", "source": "Phase 1 source note (player.h m_lastSlideBoost); data bracket 0.201 < w <= 0.597",
            "n": g(J2, "jump_time_after_boost_s").get("n", 0) + g(J6, "jump_time_after_boost_s").get("n", 0),
            "jump_time_early": g(J2, "jump_time_after_boost_s").get("mean"),
            "jump_time_late": g(J6, "jump_time_after_boost_s").get("mean"),
            "evidence": "C (bracketed, edge not measured)",
            "formula": "slide jump with t_since_boost < window: v_h' = v_h - lastSlideBoost"},
        "slideBoostRefundAmount": {
            "value": -g(J2, "takeoff_delta").get("mean", 0), "unit": "u/s",
            "source": "observed take-off speed change of the early jump (contains about +0.008 u/s air accel)",
            "n": g(J2, "takeoff_delta").get("n"), "spread": sp(g(J2, "takeoff_delta")), "expected": bo.get("mean"),
            "evidence": "A", "formula": "refund = lastSlideBoost (161 here: the actual gain, not slideSpeedBoost)"},
        "slideMaxJumpSpeed": {
            "value": CENSUS["slideMaxJumpSpeed"], "unit": "u/s", "source": "census slideMaxJumpSpeed; observed late take-off speed (unscaled)",
            "n": g(J6, "takeoff_post_speed").get("n"), "observed_takeoff": g(J6, "takeoff_post_speed").get("mean"),
            "observed_pre": g(J6, "takeoff_pre_speed").get("mean"), "spread": sp(g(J6, "takeoff_post_speed")),
            "evidence": "C (one operating point: 318 -> 350)",
            "formula": "chosen: outside the refund window v_h' = max(v_h, 350); "
                       "alternative max(v_h, min(v_h + J, 350)) with J >= 31.85 u/s cannot be separated by these data"},
        "slideJumpHeight": {
            "value": CENSUS["slideJumpHeight"], "unit": "u", "source": "census slideJumpHeight; H estimated from the jump usercmd's post vz",
            "H_est_early": g(J2, "takeoff_H_est").get("mean"), "H_est_late": g(J6, "takeoff_H_est").get("mean"),
            "n": g(J2, "takeoff_H_est").get("n", 0) + g(J6, "takeoff_H_est").get("n", 0),
            "spread_early": sp(g(J2, "takeoff_H_est")), "spread_late": sp(g(J6, "takeoff_H_est")), "evidence": "B",
            "formula": "v_up = sqrt(2*750*slideJumpHeight) = 273.86 u/s; the logged post vz of the jump usercmd = v_up - 1.5*g*dt"},
        "gravity": {
            "value": 750.0, "fitted": st.fmean([x["mean"] for x in grav]) if grav else None,
            "census": "sv_gravity 750 x gravityScale 1",
            "unit": "u/s^2", "source": "fitted (median of -dvz/dt per airborne usercmd, per trial)",
            "n": sum(x["n"] for x in grav), "spread": [sp(x) for x in grav], "evidence": "B", "formula": "vz' = vz - 750*dt"},
        "landingWhileDucked": {
            "value": None, "unit": "-", "source": "observed",
            "land_speed_early": g(J2, "land_speed").get("mean"), "land_speed_late": g(J6, "land_speed").get("mean"),
            "first_cmd_decel_obs_early": g(J2, "land_first_cmd_decel").get("mean"),
            "first_cmd_decel_census_early": g(J2, "land_first_cmd_decel_census").get("mean"),
            "first_cmd_decel_obs_late": g(J6, "land_first_cmd_decel").get("mean"),
            "first_cmd_decel_census_late": g(J6, "land_first_cmd_decel_census").get("mean"),
            "post_land_boost": g(J2, "post_land_slide_boost").get("mean"), "evidence": "A",
            "formula": "landing with duck held and v >= 200: slide resumes on the landing usercmd, no speed loss, no new boost"},
    }
    return out


def fmt(s, nd=3):
    if not s or not s.get("n"):
        return "-"
    sp = f"{s['spread_pct']:.2f}%" if s.get("spread_pct") is not None else "-"
    return f"{s['mean']:.{nd}f} (sd {s['sd']:.{nd}f}, {s['min']:.{nd}f}..{s['max']:.{nd}f}, spread {sp}, n={s['n']})"


def report(S, verbose):
    print("== dt join (HSD client frame -> MT post-state) ==")
    for j in S["join"]:
        print(f"  {j['run']:5s} cmds {j['cmds']:4d} frames {j['frames']:4d} moving {j['moving_frames']:4d} joined {j['joined']:4d} "
              f"unjoined {j['unjoined']} multi {j['multi_candidate']} step1 {j['step1_frac']} "
              f"|ft-dt_est| med {j['ft_minus_dtest_abs_median_us'] or float('nan'):.1f}us p95 {j['ft_minus_dtest_abs_p95_us'] or float('nan'):.1f}us")
    for s, A in S["agg"].items():
        print(f"== {s} ==")
        for k in sorted(A):
            if verbose or not k.startswith(("decay_seg1_duck", "post_land_slide.M1", "post_land_slide.M3")):
                print(f"  {k:42s} {fmt(A[k], 4)}")
        if verbose:
            for t in S["trials"][s]:
                print("   ", t["run"], {k: v for k, v in t.items() if not isinstance(v, dict)})


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
