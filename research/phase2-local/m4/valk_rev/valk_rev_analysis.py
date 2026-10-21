#!/usr/bin/env python3
"""M4 Valkyrie jets (sustained thrust) and Revenant shadow pounce (charged impulse).

    python valk_rev_analysis.py <session folder> [<session folder> ...] [--json results.json] [--params params.json]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). Only trials with ok=true and
warmup=false are used; the schedule decides the role (m4_valk_ctrl / m4_valk_jets / m4_valk_jets_fwd,
m4_pounce_c0 / _c06 / _c13). Census sessions (runner census=true) also get a class-var diff against the
T0 smoke census when --census-ref <census.csv> is given.

Physics truth: client first-time MOVE-TRACE commands (M2 loader ../../m2/air_jump/aj_load.py, unchanged).
The jetpack runs AFTER the MOVE-TRACE post print, so for the jets the state a command hands on is the next
command's pre-state (equal to the client HSD frame of that command, checked below). dt per command is the
frametime of the HSD frame printed after the command (exactly one command between frames, SAMPLING-PHASE
rule); the M2 state check is relaxed to "frame == post OR frame == next pre". Dedi MOVE-TRACE rows of the
same usercmd are used for parity and as the authoritative state where client and dedi disagree.
Nothing is tuned to pass: the jet model is the SDK twin's math (game/server/jetpack.cpp Jetpack_Apply /
Jetpack_Stop) with its setfile constants left free and fitted. stdlib only, no local paths.
"""
import argparse
import bisect
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m2", "air_jump")))
import aj_load as L  # noqa: E402

IN_JUMP, IN_DUCK, IN_FWD = 0x2, 0x4, 0x8
IN_DODGE = 0x10000000      # bit 28: the airborne jump-hold abilities read it
IN_OFFHAND1 = 0x200000     # bit 21: tactical
G = 750.0                  # sv_gravity (gravityScale 1, census)
LN2 = math.log(2.0)
TIGHT_ABOVE_LIMIT = 0.4    # SDK JP_TIGHTNESS_ABOVE_LIMIT (fixed constant in jetpack.cpp, not a setfile field)
FLOOR = 294.274            # lane C floor (reset origin z)
POUNCE_PULLOUT, POUNCE_MAXCHARGE = 0.9, 1.3   # toss_pullout_time (weapon .txt), SHADOW_POUNCE_MAX_HOLD_TIME
POUNCE_VMIN, POUNCE_VMAX, POUNCE_PITCH_UP = 700.0, 1150.0, 35.0


# ----------------------------------------------------------------------------- helpers
def st(vals):
    return L.stats(list(vals))


def f(s, nd=4):
    return L.fmt(s, nd)


def rms(xs):
    xs = list(xs)
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def nelder_mead(fun, x0, step, iters=1500, tol=1e-12):
    n = len(x0)
    pts = [list(x0)]
    for i in range(n):
        p = list(x0)
        p[i] += step[i]
        pts.append(p)
    vals = [fun(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda i: vals[i])
        pts = [pts[i] for i in order]
        vals = [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < tol:
            break
        c = [sum(p[j] for p in pts[:-1]) / n for j in range(n)]
        r = [c[j] + (c[j] - pts[-1][j]) for j in range(n)]
        fr = fun(r)
        if fr < vals[0]:
            e = [c[j] + 2 * (c[j] - pts[-1][j]) for j in range(n)]
            fe = fun(e)
            pts[-1], vals[-1] = (e, fe) if fe < fr else (r, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = r, fr
        else:
            k = [c[j] + 0.5 * (pts[-1][j] - c[j]) for j in range(n)]
            fk = fun(k)
            if fk < vals[-1]:
                pts[-1], vals[-1] = k, fk
            else:
                for i in range(1, n + 1):
                    pts[i] = [pts[0][j] + 0.5 * (pts[i][j] - pts[0][j]) for j in range(n)]
                    vals[i] = fun(pts[i])
    i = min(range(n + 1), key=lambda i: vals[i])
    return pts[i], vals[i]


def frame_dt(t):
    """dt per command = ft of the client HSD frame printed after it (exactly one command between frames).
    Also counts whether that frame equals the command's post-state or the next command's pre-state."""
    cs = t["cmds"]
    cp = [c["plat"] for c in cs]
    out = [None] * len(cs)
    pitch = [None] * len(cs)
    n_post = n_next = n_none = 0
    prev = None
    for fr in t["frames"]:
        if fr.get("plat") is None:
            continue
        j = bisect.bisect_right(cp, fr["plat"]) - 1
        if j < 0:
            continue
        one = prev is None or j - prev == 1
        prev = j
        if not one:
            continue
        c = cs[j]
        dpost = max(abs(fr[k] - c["p" + k]) for k in ("ox", "oy", "oz", "vx", "vy", "vz"))
        dnext = None
        if j + 1 < len(cs):
            nx = cs[j + 1]
            dnext = max(abs(fr[k] - nx[k]) for k in ("ox", "oy", "oz", "vx", "vy", "vz"))
        if dpost < L.TOL:
            n_post += 1
        elif dnext is not None and dnext < L.TOL:
            n_next += 1
        else:
            n_none += 1
        out[j] = fr["ft"]
        pitch[j] = fr.get("pitch")
    for j, c in enumerate(cs):
        c["pitch"] = pitch[j]
    return out, {"frame_eq_post": n_post, "frame_eq_next_pre_only": n_next, "frame_eq_neither": n_none}


def load(folders):
    trials, meta = [], []
    for fo in folders:
        S = L.load_session(fo)
        meta.append({"session": S["folder"], "trials": len(S["trials"]), "parse_errors": S["parse_errors"],
                     "census": bool(S.get("census"))})
        for t in S["trials"]:
            t["session"] = S["folder"]
            t["dt"], t["frame_join"] = frame_dt(t)
            t["sv_by_cmd"] = {r["cmd"]: r for r in t["sv_mt"]}
            trials.append(t)
    return trials, meta


def dtv(t, i):
    return t["dt"][i] if t["dt"][i] else 1.0 / 120.0


def dt_of_cmd(t, cmd):
    """dt of a usercmd (the dedi runs the client's frametime for the same command)."""
    if "_cmd_index" not in t:
        t["_cmd_index"] = {c["cmd"]: i for i, c in enumerate(t["cmds"])}
    i = t["_cmd_index"].get(cmd)
    return dtv(t, i) if i is not None else 1.0 / 120.0


# ----------------------------------------------------------------------------- census
def census_diff(folders, ref_csv):
    out = {}
    ref = {}
    if ref_csv and os.path.exists(ref_csv):
        with open(ref_csv, encoding="utf-8") as fh:
            ref = {r["key"]: r["cl_classvar"] for r in csv.DictReader(fh)}
    rx = re.compile(r"\[CLASSVAR\] (\S+) = (\S+)")
    for fo in folders:
        got = {}
        for root, _, files in os.walk(os.path.join(fo, "platform", "logs", "client")):
            for fn in files:
                if fn != "message.log":
                    continue
                with open(os.path.join(root, fn), encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        m = rx.search(line)
                        if m:
                            got.setdefault(m.group(1), []).append(m.group(2))
        if not got:
            continue
        diffs = {k: {"ref": ref.get(k), "now": v} for k, v in got.items()
                 if (ref and ref.get(k) != v[0]) or len(set(v)) > 1}
        missing_in_now = [k for k in ref if k not in got]
        glide = None
        for root, _, files in os.walk(os.path.join(fo, "platform", "logs", "server")):
            for fn in files:
                with open(os.path.join(root, fn), encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        m = re.search(r"SetGlideMeter first call .*value=([0-9.]+)", line)
                        if m:
                            glide = float(m.group(1))
        jet_keys = [k for k in got if re.search(r"jet|glide|hover", k, re.I)]
        out[os.path.basename(os.path.normpath(fo))] = {"keys": len(got), "diffs_vs_ref": diffs,
                                                       "ref_keys_missing": missing_in_now,
                                                       "jetpack_or_glide_keys_in_census": jet_keys,
                                                       "SetGlideMeter_first_value": glide}
    return out


# ----------------------------------------------------------------------------- Valkyrie: jet model (SDK twin)
def terminal(acc, tight, dt):
    return acc * dt / (1.0 - math.exp(-LN2 / tight * dt))


def jet_apply(P, post, fwd, side, t, dt):
    """One Jetpack_Apply step (jetpack.cpp:403-602) for pitch 0, no afterburner, jump held, no alt hand.
    P = (T, H, tu, tfb, strafe, s0, R, ts, tf). Returns (next velocity, vertical branch, fwd over-limit)."""
    T, H, tu, tfb, strafe, s0, R, ts, tf = P
    vx, vy, vz = post
    wish = min(1.0, math.hypot(fwd, side))
    th = T
    if wish > 1e-4:
        th = (H - T) * wish + T
    stt = H
    if R > 0 and R >= t:
        sc = (t / R) * (1.0 - s0) + s0
        th *= sc
        stt = H * sc
    vin = vz
    vz += G * th * dt
    vz = math.exp(-LN2 / tu * dt) * vz          # d > 0 throughout these trials: tightness up
    branch = "A"
    if vin > 0 and vin - terminal((th - 1.0) * G, tu, dt) > 0.01:
        vz = vin * math.exp(-LN2 / TIGHT_ABOVE_LIMIT * dt) + G * dt
        branch = "B"
    moving = fwd != 0.0 or side != 0.0
    lim = terminal(stt * strafe, tfb, dt) if moving else 0.0
    over_side = abs(vy) > lim
    vy = math.exp(-LN2 / (TIGHT_ABOVE_LIMIT if over_side else tfb) * dt) * vy   # sideways tightness assumed = fwd
    over_fwd = abs(vx) > lim
    vx = math.exp(-LN2 / (TIGHT_ABOVE_LIMIT if over_fwd else tfb) * dt) * vx
    wx, wy = fwd, side
    w2 = wx * wx + wy * wy
    if w2 > 1e-6:
        if w2 > 1.0:
            n = math.sqrt(w2)
            wx, wy = wx / n, wy / n
        ax, ay = wx * strafe, wy * strafe
        if tf > ts:
            s = vx * wx + vy * wy
            tp = 1.0
            if ts < s < tf:
                tp = 1.0 - (s - ts) / (tf - ts)
            elif s >= tf:
                tp = 0.0
            ax, ay = ax * tp, ay * tp
        if over_fwd:
            ax = 0.0
        if over_side:
            ay = 0.0
        vx += ax * stt * dt
        vy += ay * stt * dt
    return (vx, vy, vz), branch, over_fwd


def jet_samples(trials):
    """(trial, k, t since activation, dt, post velocity, fwd, side, next pre velocity) for every command with
    the jets on, from the activating command (first airborne IN_DODGE command) to the last held command."""
    D, act = [], []
    for t in trials:
        if not t["schedule"].startswith("m4_valk_jets"):
            continue
        cs = t["cmds"]
        k0 = None
        for i in range(1, len(cs)):
            if cs[i]["buttons"] & IN_DODGE and cs[i]["ground"] == 0 and cs[i - 1]["ground"] == 0:
                k0 = i
                break
        if k0 is None:
            continue
        # leaving ground: first command whose post ground flag is 0
        i_air = next(i for i in range(len(cs)) if cs[i]["ground"] == 1 and cs[i + 1]["ground"] == 0)
        jets_on_first = abs(cs[k0 + 1]["vz"] - cs[k0]["pvz"]) > 0.01
        prev_off = abs(cs[k0]["vz"] - cs[k0 - 1]["pvz"]) < 0.002
        act.append({"trial": t["label"], "schedule": t["schedule"], "k_activate": k0,
                    "t_after_leave_ground": sum(dtv(t, k) for k in range(i_air, k0)),
                    "vz_pre_at_activation": cs[k0]["vz"], "jet_on_activation_cmd": jets_on_first,
                    "no_jet_before": prev_off,
                    "vz_scale_on_activation": cs[k0]["vz"] / cs[k0 - 1]["pvz"] if cs[k0 - 1]["pvz"] else None})
        tt = 0.0
        for i in range(k0, len(cs) - 1):
            c, n = cs[i], cs[i + 1]
            if not c["buttons"] & IN_DODGE:
                break
            dt = dtv(t, i)
            D.append((t["label"], i - k0, tt, dt, (c["pvx"], c["pvy"], c["pvz"]), c["fwd"], c["sidemove"],
                      (n["vx"], n["vy"], n["vz"]), t["schedule"]))
            tt += dt
    return D, act


def jet_cost(P, D, axes):
    s = 0.0
    for _, _, tt, dt, post, fwd, side, nxt, _ in D:
        p, _, _ = jet_apply(P, post, fwd, side, tt, dt)
        for j in axes:
            s += (p[j] - nxt[j]) ** 2
    return s


def jet_residuals(P, D):
    out = []
    for lab, k, tt, dt, post, fwd, side, nxt, sch in D:
        p, b, ov = jet_apply(P, post, fwd, side, tt, dt)
        out.append({"trial": lab, "k": k, "t": tt, "branch": b, "over_fwd": ov, "fwd": fwd,
                    "rx": p[0] - nxt[0], "rz": p[2] - nxt[2]})
    return out


def fit_jets(D):
    """Stage 1: vertical (T, H, tu, s0, R) on vz. Stage 2: horizontal (tfb, strafe, ts, tf) on vx of the W
    trials. Two starts each; the fit is not seeded from the result (see the doc for the round values)."""
    res = {}
    best1 = None
    for x0 in ([2.0, 1.5, 0.3, 1.5, 0.4], [1.5, 2.0, 0.5, 2.0, 0.7]):
        def f1(q):
            T, H, tu, s0, R = q
            if tu <= 0.01 or R <= 0.01:
                return 1e18
            return jet_cost([T, H, tu, 0.14, 1000.0, s0, R, 0.0, 0.0], D, (2,))
        p, v = nelder_mead(f1, x0, [0.1, 0.1, 0.05, 0.1, 0.05], 2500)
        for _ in range(3):  # restarts from the best point (Nelder-Mead stalls on this valley)
            p, v = nelder_mead(f1, p, [0.01, 0.01, 0.005, 0.01, 0.005], 1500)
        if best1 is None or v < best1[1]:
            best1 = (p, v)
    T, H, tu, s0, R = best1[0]
    W = [r for r in D if r[8] == "m4_valk_jets_fwd"]
    best2 = None
    for x0 in ([0.5, 1500.0, 200.0, 400.0], [0.2, 800.0, 350.0, 700.0]):
        def f2(q):
            tfb, strafe, ts, tf = q
            if tfb <= 0.005 or tf < ts:
                return 1e18
            return jet_cost([T, H, tu, tfb, strafe, s0, R, ts, tf], W, (0,))
        p, v = nelder_mead(f2, x0, [0.05, 100.0, 30.0, 30.0], 2500)
        for _ in range(3):
            p, v = nelder_mead(f2, p, [0.005, 10.0, 3.0, 3.0], 1500)
        if best2 is None or v < best2[1]:
            best2 = (p, v)
    tfb, strafe, ts, tf = best2[0]
    P = [T, H, tu, tfb, strafe, s0, R, ts, tf]
    res["fit"] = dict(zip(["T", "H", "tu", "tfb", "strafe", "s0", "R", "ts", "tf"], P))
    res["fit_rms_z"] = math.sqrt(best1[1] / len(D))
    res["fit_rms_x_W"] = math.sqrt(best2[1] / len(W))
    # no-taper alternative for the horizontal (round 2 of the model choice)
    def f3(q):
        a, b = q
        if a <= 0.005:
            return 1e18
        return jet_cost([T, H, tu, a, b, s0, R, 0.0, 0.0], W, (0,))
    p3, v3 = nelder_mead(f3, [0.0632, 2068.0], [0.01, 50.0], 2000)
    res["alt_no_taper"] = {"tfb": p3[0], "strafe": p3[1], "rms_x": math.sqrt(v3 / len(W))}
    return P, res


def summarize_res(R, sel=None):
    R = [r for r in R if sel is None or sel(r)]
    if not R:
        return {"n": 0}
    return {"n": len(R), "rms_z": rms(r["rz"] for r in R), "max_z": max(abs(r["rz"]) for r in R),
            "rms_x": rms(r["rx"] for r in R), "max_x": max(abs(r["rx"]) for r in R)}


def valk_release(trials, P):
    """Release: command of the stop on client and dedi, vertical scale, post-effect gravity and drag, end."""
    rows = []
    drag_pts = []
    for t in trials:
        if not t["schedule"].startswith("m4_valk_jets"):
            continue
        cs, sv = t["cmds"], t["sv_by_cmd"]
        rel = max(i for i in range(len(cs)) if cs[i]["buttons"] & IN_DODGE) + 1     # first command without +jump
        land = next(i for i in range(rel, len(cs)) if cs[i]["ground"] == 1)
        svl = t["sv_mt"]
        idx = {r["cmd"]: k for k, r in enumerate(svl)}

        def stop_cmd(get_post, get_next, a, b):
            for i in range(a, b):
                post, nxt = get_post(i), get_next(i)
                if post is None or nxt is None:
                    continue
                if abs(nxt - post) > 0.01 and abs(nxt / post - 0.4) < 0.002:
                    return i, nxt / post
            return None, None
        cl_i, cl_s = stop_cmd(lambda i: cs[i]["pvz"], lambda i: cs[i + 1]["vz"], rel - 1, rel + 6)
        k_rel = idx[cs[rel]["cmd"]]
        sv_k, sv_s = stop_cmd(lambda k: svl[k]["pvz"], lambda k: svl[k + 1]["vz"] if k + 1 < len(svl) else None,
                              k_rel - 1, k_rel + 6)
        # vertical acceleration per command (MT post - pre)/dt on both sides, after the stop
        def classify(rows_, a, b, dts):
            lo, hi = [], []
            for j in range(a, b):
                r = rows_[j]
                if r["ground"]:
                    break
                g = (r["pvz"] - r["vz"]) / dts(j)
                (lo if abs(g + 0.45 * G) < 4 else hi if abs(g + G) < 4 else []).append(j)
            return lo, hi
        sv_dt = lambda k: dt_of_cmd(t, svl[k]["cmd"])  # dedi runs the client's frametime
        lo_sv, hi_sv = classify(svl, sv_k + 1, len(svl), sv_dt)
        lo_cl, hi_cl = classify(cs, cl_i + 1, land, lambda i: dtv(t, i))
        g_lo_sv = [-(svl[k]["pvz"] - svl[k]["vz"]) / sv_dt(k) for k in lo_sv]
        # end of the post effect: first dedi command from which every airborne command has full gravity
        air_k = [k for k in range(sv_k + 1, len(svl)) if not svl[k]["ground"]]
        hs = set(hi_sv)
        end_k = None
        for k in reversed(air_k[:-1]):  # the last airborne command is the landing command
            if k in hs:
                end_k = k
            else:
                break
        last_lo = max([k for k in lo_sv if end_k is None or k < end_k], default=None)
        rec = {"trial": t["label"], "schedule": t["schedule"], "release_cmd": rel,
               "client_stop_cmd_minus_release": None if cl_i is None else cl_i - rel, "client_vz_scale": cl_s,
               "dedi_stop_cmd_minus_release": None if sv_k is None else sv_k - k_rel, "dedi_vz_scale": sv_s,
               "vz_post_at_stop_dedi": svl[sv_k]["pvz"] if sv_k is not None else None,
               "terminal_T_check": terminal((P[0] - 1) * G, P[2], 1 / 120.0),
               "dedi_lowg_cmds": len(lo_sv), "dedi_fullg_cmds_after": len(hi_sv),
               "dedi_lowg_mean": st(g_lo_sv)["mean"] if g_lo_sv else None,
               "client_lowg_cmds": len(lo_cl), "client_fullg_cmds": len(hi_cl),
               "postfx_end_after_stop_s": None if end_k is None else (end_k - sv_k) / 120.0,
               "postfx_end_height_first_fullg": None if end_k is None else svl[end_k]["oz"] - FLOOR,
               "postfx_end_height_last_lowg": None if last_lo is None else svl[last_lo]["oz"] - FLOOR,
               "land_cmd": land, "land_vz": cs[land - 1]["vz"] if land else None,
               "vh_before_land": math.hypot(cs[land - 1]["pvx"], cs[land - 1]["pvy"]),
               "vh_after_land_cmd": math.hypot(cs[land]["vx"], cs[land]["vy"])}
        # dedi drag samples (horizontal) on low-gravity commands
        for k in lo_sv:
            r = svl[k]
            v0, v1 = math.hypot(r["vx"], r["vy"]), math.hypot(r["pvx"], r["pvy"])
            if v0 > 1.0:
                drag_pts.append((v0, v1, sv_dt(k)))
        # client drag on its own commands after the stop (client full or low gravity)
        cl_drag = []
        for i in range(cl_i + 1 if cl_i is not None else rel, land - 1):
            c = cs[i]
            v0, v1 = math.hypot(c["vx"], c["vy"]), math.hypot(c["pvx"], c["pvy"])
            if v0 > 1.0:
                cl_drag.append((v0 - v1) / dtv(t, i) / (v0 * v0))
        rec["client_drag_coef_mean"] = st(cl_drag)["mean"] if cl_drag else None
        # dedi corrections seen by the client after release (next pre != post)
        rec["client_corrections"] = sum(1 for i in range(rel, land - 1)
                                        if max(abs(cs[i + 1]["vz"] - cs[i]["pvz"]), abs(cs[i + 1]["vx"] - cs[i]["pvx"])) > 0.01)
        # movescale timeline
        msc = [(i, cs[i]["movescale"]) for i in range(1, len(cs)) if cs[i]["movescale"] != cs[i - 1]["movescale"]]
        rec["movescale_changes"] = [(i - rel, m) for i, m in msc]
        rows.append(rec)
    drag = {}
    for name, fn in (("constant", lambda v: 1.0), ("linear", lambda v: v), ("quadratic", lambda v: v * v)):
        xs = [fn(v0) for v0, v1, _ in drag_pts]
        ys = [(v0 - v1) / d for v0, v1, d in drag_pts]
        if not xs:
            continue
        c = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
        dt = 1.0 / 120.0
        res = [(y - c * x) * d for (x, y), (_, _, d) in zip(zip(xs, ys), drag_pts)]
        hi = [r for (v0, _, _), r in zip(drag_pts, res) if v0 > 330]
        lo = [r for (v0, _, _), r in zip(drag_pts, res) if v0 < 318]
        n = len(xs)
        se = math.sqrt(sum((r / dt) ** 2 for r in res) / max(n - 1, 1) / sum(x * x for x in xs))
        drag[name] = {"c": c, "se": se, "rms_per_cmd": rms(res), "mean_res_fast": sum(hi) / len(hi) if hi else None,
                      "mean_res_slow": sum(lo) / len(lo) if lo else None, "n": n}
    return rows, drag


def valk_ctrl(trials):
    out = []
    for t in trials:
        if t["schedule"] != "m4_valk_ctrl":
            continue
        cs = t["cmds"]
        i0 = next(i for i in range(len(cs)) if cs[i]["ground"] == 1 and cs[i + 1]["ground"] == 0)
        land = next(i for i in range(i0 + 2, len(cs)) if cs[i]["ground"] == 1)
        apex = max(c["poz"] for c in cs[i0:land]) - FLOOR
        g = [-(cs[i]["pvz"] - cs[i]["vz"]) / dtv(t, i) for i in range(i0 + 2, land - 1)]
        out.append({"trial": t["label"], "jump_vz_post": cs[i0]["pvz"] if cs[i0]["pvz"] > 1 else cs[i0 + 1]["vz"],
                    "apex": apex, "air_s": sum(dtv(t, i) for i in range(i0, land)), "g": st(g)["mean"],
                    "any_dodge_in_air": any(cs[i]["buttons"] & IN_DODGE for i in range(i0 + 1, land))})
    return out


def parity_jets(trials):
    out = []
    for t in trials:
        if not t["schedule"].startswith("m4_valk_jets"):
            continue
        cs, sv = t["cmds"], t["sv_by_cmd"]
        rel = max(i for i in range(len(cs)) if cs[i]["buttons"] & IN_DODGE) + 1
        held = [i for i in range(len(cs)) if cs[i]["buttons"] & IN_DODGE and i > 10]
        dmax = 0.0
        for i in held:
            s = sv.get(cs[i]["cmd"])
            if s:
                dmax = max(dmax, max(abs(s[k] - cs[i][k]) for k in ("vx", "vy", "vz", "pvx", "pvz", "ox", "oz")))
        out.append({"trial": t["label"], "max_abs_client_minus_dedi_during_hold": dmax})
    return out


# ----------------------------------------------------------------------------- Revenant
def pounce(trials):
    out = []
    for t in trials:
        if not t["schedule"].startswith("m4_pounce"):
            continue
        cs, svl = t["cmds"], t["sv_mt"]
        p = next(i for i in range(len(cs)) if cs[i]["buttons"] & IN_OFFHAND1)
        r = next(i for i in range(p, len(cs)) if not cs[i]["buttons"] & IN_OFFHAND1)
        Lc = next(i for i in range(len(cs)) if abs(cs[i]["pvx"]) > 1 or abs(cs[i]["pvz"]) > 1)
        k = next(j for j, s in enumerate(svl) if abs(s["pvx"]) > 1 or abs(s["pvz"]) > 1)
        s = svl[k]
        Lsv = next(i for i in range(len(cs)) if cs[i]["cmd"] == s["cmd"])
        tim = lambda a, b: sum(dtv(t, i) for i in range(a, b))
        hold = tim(p, r)
        # launch vector on the dedi launch command: vz0 = post vz + g*dt/2 (FinishGravity half step)
        dtL = dtv(t, Lsv)
        vh = math.hypot(s["pvx"], s["pvy"])
        vz0 = s["pvz"] + 0.5 * G * dtL
        spd = math.hypot(vh, vz0)
        elev = math.degrees(math.atan2(vz0, vh))
        charge_obs = (spd - POUNCE_VMIN) / (POUNCE_VMAX - POUNCE_VMIN)
        # hypotheses for the charge clock: Time() at the release (OnWeaponToss) vs at the launch command
        t_rel = tim(p, r)
        t_launch = tim(p, Lsv)
        h_rel = min(max((t_rel - POUNCE_PULLOUT) / POUNCE_MAXCHARGE, 0.0), 1.0)
        h_launch = min(max((t_launch - POUNCE_PULLOUT) / POUNCE_MAXCHARGE, 0.0), 1.0)
        # flight: from launch+1 to landing (client), gravity, horizontal drift, client corrections
        land = next(i for i in range(Lc + 2, len(cs)) if cs[i]["ground"] == 1)
        g, dvh, corr = [], [], []
        for i in range(Lc + 1, land - 1):
            c, n = cs[i], cs[i + 1]
            jump = max(abs(n["vz"] - c["pvz"]), abs(n["vx"] - c["pvx"]))
            if jump > 0.003:
                corr.append((i - Lc, round(n["vx"] - c["pvx"], 3), round(n["vz"] - c["pvz"], 3)))
            if t["dt"][i]:
                g.append(-(c["pvz"] - c["vz"]) / t["dt"][i])
            dvh.append(math.hypot(c["pvx"], c["pvy"]) - math.hypot(c["vx"], c["vy"]))
        # dedi flight gravity too
        ks = next(j for j in range(k + 2, len(svl)) if svl[j]["ground"] == 1)
        gsv = [-(svl[j]["pvz"] - svl[j]["vz"]) / dt_of_cmd(t, svl[j]["cmd"]) for j in range(k + 1, ks - 1)]
        lc = cs[land]
        vh_in = math.hypot(lc["vx"], lc["vy"])
        vh_out = math.hypot(lc["pvx"], lc["pvy"])
        # charge-phase movement state
        msc_charge = sorted(set(cs[i]["movescale"] for i in range(p, Lc)))
        ms_charge = sorted(set(cs[i]["maxspeed"] for i in range(p, Lc)))
        msc_back = next((i - land for i in range(land, len(cs)) if cs[i]["movescale"] != cs[land]["movescale"]), None)
        out.append({"trial": t["label"], "schedule": t["schedule"], "hold_s": hold,
                    "press_to_launch_cmds": Lc - p, "press_to_launch_s": tim(p, Lc),
                    "release_to_launch_cmds": Lc - r, "client_launch_cmd_minus_dedi": Lc - Lsv,
                    "launch_client_post": (cs[Lc]["pvx"], cs[Lc]["pvz"]), "launch_dedi_post": (s["pvx"], s["pvz"]),
                    "launch_on_ground": cs[Lc]["ground"], "pitch": cs[Lc].get("pitch"), "yaw": cs[Lc].get("yaw"),
                    "speed": spd, "elev_deg": elev, "vh0": vh, "vz0": vz0, "charge_obs": charge_obs,
                    "charge_h_release": h_rel, "charge_h_launch": h_launch,
                    "speed_h_release": POUNCE_VMIN + (POUNCE_VMAX - POUNCE_VMIN) * h_rel,
                    "speed_h_launch": POUNCE_VMIN + (POUNCE_VMAX - POUNCE_VMIN) * h_launch,
                    "air_cmds": land - Lc, "g_client": st(g), "g_dedi": st(gsv),
                    "dvh_max_abs_per_cmd": max(abs(x) for x in dvh) if dvh else None,
                    "client_corrections": corr, "land_vz": cs[land - 1]["vz"], "vh_land_in": vh_in,
                    "vh_land_out": vh_out, "land_dv_over_dt": (vh_in - vh_out) / dtv(t, land),
                    "movescale_charge": msc_charge, "maxspeed_charge": ms_charge,
                    "movescale_restore_cmds_after_land": msc_back})
    return out


def landing_factor_octane(vz):
    return min(max(1.99647 - 1.6714e-6 * vz * vz, 0.0), 1.0)


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    ap.add_argument("--census-ref", help="T0 smoke census.csv to diff the [CLASSVAR] census against")
    a = ap.parse_args()
    trials, meta = load(a.sessions)
    R = {"sessions": meta}
    pr = print
    pr("== sessions")
    for m in meta:
        pr("  %(session)s: %(trials)d trials used, parse errors %(parse_errors)d, census %(census)s" % m)
    by = {}
    for t in trials:
        by.setdefault(t["schedule"], []).append(t["label"])
    for k, v in sorted(by.items()):
        pr("  %-18s n=%d %s" % (k, len(v), " ".join(v)))
    R["trials"] = by
    pr("\n== join (frame after each command; jets trials: frame shows the NEXT pre-state)")
    for t in trials:
        j = t["frame_join"]
        if t["schedule"].startswith("m4_valk_jets") or t is trials[0]:
            pr("  %s %-17s post=%d next-pre-only=%d neither=%d" % (t["label"], t["schedule"], j["frame_eq_post"],
                                                                    j["frame_eq_next_pre_only"], j["frame_eq_neither"]))
    R["join"] = {t["label"]: t["frame_join"] for t in trials}

    # census
    cen = census_diff(a.sessions, a.census_ref)
    R["census"] = cen
    pr("\n== census ([CLASSVAR] at session start vs T0 smoke)")
    for s, c in cen.items():
        pr("  %s: %d keys, diffs %s, jet/glide keys in census list: %s, SetGlideMeter first value: %s"
           % (s, c["keys"], c["diffs_vs_ref"], c["jetpack_or_glide_keys_in_census"], c["SetGlideMeter_first_value"]))

    valk = [t for t in trials if t["schedule"].startswith("m4_valk")]
    rev = [t for t in trials if t["schedule"].startswith("m4_pounce")]
    P = None
    if valk:
        pr("\n== Valkyrie control jumps")
        cj = valk_ctrl(valk)
        R["valk_ctrl"] = cj
        pr("  jump vz post %s | apex %s | air %s s | g %s | IN_DODGE in air: %s" % (
            f(st(c["jump_vz_post"] for c in cj)), f(st(c["apex"] for c in cj), 2), f(st(c["air_s"] for c in cj)),
            f(st(c["g"] for c in cj), 2), sorted(set(c["any_dodge_in_air"] for c in cj))))
        D, act = jet_samples(valk)
        R["valk_activation"] = act
        pr("\n== Valkyrie activation (first airborne +jump/IN_DODGE command)")
        for x in act:
            pr("  %(trial)s %(schedule)-17s k=%(k_activate)d  t after leave-ground %(t_after_leave_ground).4f s  vz %(vz_pre_at_activation).3f  jet on that cmd: %(jet_on_activation_cmd)s  no jet before: %(no_jet_before)s  vz scale on activation %(vz_scale_on_activation).5f" % x)
        pr("\n== Valkyrie jet flight model (SDK Jetpack_Apply math, constants fitted); %d jet commands" % len(D))
        P, fitres = fit_jets(D)
        R["valk_fit"] = fitres
        pr("  free fit: " + ", ".join("%s=%.5f" % (k, v) for k, v in fitres["fit"].items()))
        pr("  free fit rms: vz %.5f (all), vx %.5f (W trials)" % (fitres["fit_rms_z"], fitres["fit_rms_x_W"]))
        alt = fitres["alt_no_taper"]
        pr("  alternative without strafe taper: tfb=%.5f strafe=%.2f rms vx %.4f" % (alt["tfb"], alt["strafe"], alt["rms_x"]))
        # round values for everything but strafe; strafe refitted with the others held at their round values
        Wd = [r for r in D if r[8] == "m4_valk_jets_fwd"]
        ps, vs = nelder_mead(lambda q: jet_cost([1.9, 1.7, 0.27, 0.14, q[0], 1.8, 0.5, 300.0, 600.0], Wd, (0,)),
                             [fitres["fit"]["strafe"]], [5.0], 400)
        fitres["strafe_with_round_others"] = ps[0]
        pr("  strafe refitted with the other constants at round values: %.3f (rms vx %.5f)" % (ps[0], math.sqrt(vs / len(Wd))))
        Pr = [1.9, 1.7, 0.27, 0.14, round(ps[0]), 1.8, 0.5, 300.0, 600.0]
        for name, PP in (("free", P), ("rounded", Pr)):
            rr = jet_residuals(PP, D)
            s_all = summarize_res(rr)
            s0 = summarize_res(rr, lambda r: r["fwd"] == 0)
            sW = summarize_res(rr, lambda r: r["fwd"] != 0)
            nb = sum(1 for r in rr if r["branch"] == "B")
            novf = sum(1 for r in rr if r["over_fwd"] and r["fwd"] != 0)
            pr("  %-7s %s | all: rms z %.5f max %.5f, rms x %.5f max %.5f | no-W n=%d rms z %.5f | W n=%d rms z %.5f rms x %.5f | branch B cmds %d | W over-limit cmds %d"
               % (name, [round(x, 5) for x in PP], s_all["rms_z"], s_all["max_z"], s_all["rms_x"], s_all["max_x"],
                  s0["n"], s0["rms_z"], sW["n"], sW["rms_z"], sW["rms_x"], nb, novf))
            R["valk_resid_" + name] = {"P": PP, "all": s_all, "noW": s0, "W": sW, "branchB": nb, "W_over_limit": novf}
        # phase boundaries per trial (rounded model)
        rr = jet_residuals(Pr, D)
        phases = {}
        for r in rr:
            phases.setdefault(r["trial"], []).append(r["branch"])
        pb = {}
        for lab, br in phases.items():
            b0 = br.index("B") if "B" in br else None
            b1 = (len(br) - 1 - br[::-1].index("B")) if "B" in br else None
            pb[lab] = (b0, b1, len(br))
        R["valk_branchB_span"] = pb
        pr("  branch-B (decay at 0.4 s half-life above the thrust terminal) command span per trial (k from activation): " + str(pb))
        # terminals
        dt = 1 / 120.0
        eu = math.exp(-LN2 / Pr[2] * dt)
        vT = eu * (Pr[0] - 1) * G * dt / (1 - eu)  # fixed point of next = eu*(next - g dt + g T dt)
        vH = eu * (Pr[1] - 1) * G * dt / (1 - eu)
        pr("  vertical terminal (next pre-state, = speed on screen): no W %.3f, W %.3f u/s" % (vT, vH))
        e_fb = math.exp(-LN2 / Pr[3] * dt)
        A = Pr[4] * Pr[1] * dt
        vx_inf = A * Pr[8] / (Pr[8] - Pr[7]) / (1 - e_fb + A * e_fb / (Pr[8] - Pr[7]))  # taper reads the speed after the tightness step
        pr("  horizontal terminal with W (taper balance): %.3f u/s" % vx_inf)
        obs_T = [n[2] for lab, k, tt, dtt, post, fw, sd, n, sch in D if k > 230 and fw == 0]
        obs_H = [n[2] for lab, k, tt, dtt, post, fw, sd, n, sch in D if k > 230 and fw != 0]
        obs_X = [n[0] for lab, k, tt, dtt, post, fw, sd, n, sch in D if k > 230 and fw != 0]
        pr("  observed at k>230: vz no-W %s, vz W %s, vx W %s" % (f(st(obs_T), 3), f(st(obs_H), 3), f(st(obs_X), 3)))
        R["valk_terminals"] = {"vz_noW_model": vT, "vz_W_model": vH, "vx_W_model": vx_inf,
                               "vz_noW_obs": st(obs_T), "vz_W_obs": st(obs_H), "vx_W_obs": st(obs_X)}
        pr("\n== Valkyrie parity during the hold")
        par = parity_jets(valk)
        R["valk_parity_hold"] = par
        pr("  max |client - dedi| over held commands: %s" % f(st(p["max_abs_client_minus_dedi_during_hold"] for p in par), 4))
        pr("\n== Valkyrie release, post effect, landing")
        rel, drag = valk_release(valk, Pr)
        R["valk_release"] = rel
        R["valk_drag"] = drag
        for x in rel:
            pr("  %(trial)s %(schedule)-17s stop: client +%(client_stop_cmd_minus_release)s cmd (x%(client_vz_scale).5f), dedi +%(dedi_stop_cmd_minus_release)s cmd (x%(dedi_vz_scale).5f) vz_post %(vz_post_at_stop_dedi).2f | dedi low-g cmds %(dedi_lowg_cmds)d mean %(dedi_lowg_mean).3f | client low-g %(client_lowg_cmds)d full-g %(client_fullg_cmds)d corrections %(client_corrections)d" % x)
            pr("      post effect end (dedi): %.4f s after stop, height first full-g %.2f, last low-g %.2f | land vz %.2f vh %.3f -> %.3f | movescale changes (cmd-release, value) %s"
               % (x["postfx_end_after_stop_s"] or float("nan"), x["postfx_end_height_first_fullg"] or float("nan"),
                  x["postfx_end_height_last_lowg"] or float("nan"), x["land_vz"], x["vh_before_land"],
                  x["vh_after_land_cmd"], x["movescale_changes"]))
        pr("  vertical scale on stop (dedi): %s; terminal(T) at stop check %.2f" % (
            f(st(x["dedi_vz_scale"] for x in rel), 5), rel[0]["terminal_T_check"]))
        pr("  dedi post-effect gravity: %s u/s^2 (= %s x 750)" % (
            f(st(x["dedi_lowg_mean"] for x in rel), 3), f(st(x["dedi_lowg_mean"] / G for x in rel), 5)))
        for k, v in drag.items():
            pr("  drag %-9s c=%.6g (se %.2g) rms/cmd %.5f mean res fast %.5f slow %.5f n=%d" % (
                k, v["c"], v["se"], v["rms_per_cmd"], v["mean_res_fast"], v["mean_res_slow"], v["n"]))
        cl = [x["client_drag_coef_mean"] for x in rel if x["client_drag_coef_mean"]]
        pr("  client horizontal drag coefficient after release (all its airborne commands): %s" % f(st(cl), 7))
        pr("  Octane landing factor at the landing vz: %s" % sorted(set(round(landing_factor_octane(x["land_vz"]), 3) for x in rel)))

    if rev:
        pr("\n== Revenant shadow pounce")
        po = pounce(rev)
        R["pounce"] = po
        for x in po:
            pr("  %(trial)s %(schedule)-14s hold %(hold_s).4f s, press->launch %(press_to_launch_cmds)d cmds %(press_to_launch_s).4f s, release->launch %(release_to_launch_cmds)d, client-dedi launch cmd %(client_launch_cmd_minus_dedi)d, ground %(launch_on_ground)d, pitch %(pitch)s" % x)
            pr("      speed %(speed).3f elev %(elev_deg).4f deg vh0 %(vh0).3f vz0 %(vz0).3f | charge obs %(charge_obs).5f, H-release %(charge_h_release).5f (%(speed_h_release).2f), H-launch %(charge_h_launch).5f (%(speed_h_launch).2f)" % x)
            pr("      flight %d cmds g_client %s g_dedi %s max|dvh|/cmd %.4f corrections %s | land vz %.2f vh %.3f -> %.3f (%.1f u/s^2) | charge msc %s maxspeed %s, msc restored %s cmds after landing"
               % (x["air_cmds"], f(x["g_client"], 2), f(x["g_dedi"], 2), x["dvh_max_abs_per_cmd"], x["client_corrections"],
                  x["land_vz"], x["vh_land_in"], x["vh_land_out"], x["land_dv_over_dt"], x["movescale_charge"],
                  x["maxspeed_charge"], x["movescale_restore_cmds_after_land"]))
        for sch in sorted(set(x["schedule"] for x in po)):
            xs = [x for x in po if x["schedule"] == sch]
            pr("  %-14s n=%d speed %s elev %s charge_obs %s | err H-release %s | err H-launch %s" % (
                sch, len(xs), f(st(x["speed"] for x in xs), 3), f(st(x["elev_deg"] for x in xs), 4),
                f(st(x["charge_obs"] for x in xs), 5),
                f(st(x["speed"] - x["speed_h_release"] for x in xs), 3), f(st(x["speed"] - x["speed_h_launch"] for x in xs), 3)))
        pr("  Octane landing factor at the landing vz: %s" % sorted(set(round(landing_factor_octane(x["land_vz"]), 3) for x in po)))

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(R, fh, indent=1, default=str)
    if a.params:
        write_params(a.params, R)


def write_params(path, R):
    def prm(value, unit, source, n=None, spread=None, note=None):
        d = {"value": value, "unit": unit, "source": source}
        if n is not None:
            d["n"] = n
        if spread is not None:
            d["spread"] = spread
        if note:
            d["note"] = note
        return d
    P = {"_scope": "Valkyrie (character_valkyrie, PAS_VALK jets) and Revenant (S21 Reborn shadow pounce), R5Flowstate S21 client / S3 dedi, 120 fps, lane C flat floor; sessions M4_valkyrie(+rerun), M4_revenant(+rerun)"}
    if "valk_fit" in R:
        fit = R["valk_fit"]["fit"]
        rz = R["valk_resid_rounded"]
        nJ = rz["all"]["n"]
        nW = rz["W"]["n"]
        P.update({
            "valk.jets.activation_delay": prm(0, "commands", "observed: jet acceleration on the command of the airborne +jump press", len(R["valk_activation"])),
            "valk.jets.thrust": prm(1.9, "x gravity", "fitted (SDK Jetpack_Apply, free fit %.5f)" % fit["T"], nJ, "rms vz %.4f u/s/cmd" % rz["all"]["rms_z"], "jetpackThrust; vertical accel = g*thrust on top of normal gravity"),
            "valk.jets.horizontal_move_thrust": prm(1.7, "x gravity", "fitted (free %.5f)" % fit["H"], nW, None, "jetpackHorizontalMoveThrust: replaces thrust when move input is held (lerp by |wish|); also multiplies strafe"),
            "valk.jets.tightness_up": prm(0.27, "s (half-life)", "fitted (free %.5f)" % fit["tu"], nJ, None, "vel_up *= 2^(-dt/0.27) every jet command"),
            "valk.jets.tightness_above_limit": prm(TIGHT_ABOVE_LIMIT, "s (half-life)", "SDK constant JP_TIGHTNESS_ABOVE_LIMIT; data: branch B exact", rz["branchB"]),
            "valk.jets.thrust_scale_on_activation": prm(1.8, "x", "fitted (free %.5f)" % fit["s0"], nJ, None, "jetpackThrustScaleOnActivation, linear ramp to 1"),
            "valk.jets.thrust_scale_time": prm(0.5, "s", "fitted (free %.5f)" % fit["R"], nJ, None, "jetpackThrustScaleTimeOnActivation"),
            "valk.jets.tightness_forwardback": prm(0.14, "s (half-life)", "fitted (free %.5f)" % fit["tfb"], nW, "rms vx %.4f" % rz["W"]["rms_x"], "sideways assumed equal (untested)"),
            "valk.jets.strafe": prm(R["valk_resid_rounded"]["P"][4], "u/s^2 per unit thrust", "fitted (free %.3f; %.3f with the other constants rounded)" % (fit["strafe"], R["valk_fit"]["strafe_with_round_others"]), nW, None, "jetpackStrafe; horizontal accel = strafe*horizontalMoveThrust*taper"),
            "valk.jets.strafe_taper_start": prm(300.0, "u/s", "fitted (free %.3f)" % fit["ts"], nW),
            "valk.jets.strafe_taper_finish": prm(600.0, "u/s", "fitted (free %.3f)" % fit["tf"], nW),
            "valk.jets.vz_terminal_noW": prm(round(R["valk_terminals"]["vz_noW_model"], 3), "u/s", "model; observed %s" % f(R["valk_terminals"]["vz_noW_obs"], 3), R["valk_terminals"]["vz_noW_obs"]["n"]),
            "valk.jets.vz_terminal_W": prm(round(R["valk_terminals"]["vz_W_model"], 3), "u/s", "model; observed %s" % f(R["valk_terminals"]["vz_W_obs"], 3), R["valk_terminals"]["vz_W_obs"]["n"]),
            "valk.jets.vh_terminal_W": prm(round(R["valk_terminals"]["vx_W_model"], 3), "u/s", "model; observed %s" % f(R["valk_terminals"]["vx_W_obs"], 3), R["valk_terminals"]["vx_W_obs"]["n"]),
        })
        rel = R["valk_release"]
        sc = st(x["dedi_vz_scale"] for x in rel)
        lg = st(x["dedi_lowg_mean"] / G for x in rel)
        ends = [x for x in rel if x["postfx_end_after_stop_s"] is not None]
        dq = R["valk_drag"]["quadratic"]
        P.update({
            "valk.jets.vz_scale_on_deactivation": prm(0.4, "x", "observed dedi %s" % f(sc, 5), sc["n"], None, "applied when vz <= terminal(thrust); release stops the jets on the release command (dedi)"),
            "valk.jets.vz_scale_on_activation": prm(1.0, "x", "observed (vz unchanged on the activation command, vz > 0)", len(R["valk_activation"])),
            "valk.postfx.gravity_scale": prm(0.45, "x gravity", "observed dedi %s" % f(lg, 5), lg["n"]),
            "valk.postfx.drag_quadratic": prm(float("%.4g" % dq["c"]), "1/u (dv/dt = -c*vh^2)", "fitted dedi, se %.2g" % dq["se"], dq["n"], "rms %.5f u/s/cmd" % dq["rms_per_cmd"], "horizontal only; vertical unaffected"),
            "valk.postfx.end_probe": prm(50.0, "u below origin", "SDK JP_POSTEFFECT_PROBE; observed end heights %s" % f(st(x["postfx_end_height_first_fullg"] for x in ends), 2), len(ends)),
            "valk.postfx.min_duration": prm(round(max(x["postfx_end_after_stop_s"] for x in ends), 3), "s (lower bound of jetpackPostEffectTime)", "observed (never timed out)", len(ends)),
            "valk.fuel.initial_meter": prm((list(R["census"].values()) or [{}])[0].get("SetGlideMeter_first_value"), "meter units", "server log SetGlideMeter(glideDuration)", 1, None, "drain rate not observed"),
            "valk.fuel.min_hold_observed": prm(2.0, "s", "observed: no fuel cut in a 2.0 s hold", len(rel)),
        })
    if "pounce" in R:
        po = R["pounce"]
        c13 = [x for x in po if x["schedule"] == "m4_pounce_c13"]
        low = [x for x in po if x["schedule"] != "m4_pounce_c13"]
        P.update({
            "rev.pounce.pullout_time": prm(POUNCE_PULLOUT, "s", "weapon toss_pullout_time; observed press->launch %s" % f(st(x["press_to_launch_s"] for x in low), 4), len(low), None, "a release before 0.9 s still launches at 0.9 s with charge 0"),
            "rev.pounce.speed_min": prm(POUNCE_VMIN, "u/s", "script; observed %s (charge 0..1 cmd)" % f(st(x["speed"] for x in low), 3), len(low)),
            "rev.pounce.speed_max": prm(POUNCE_VMAX, "u/s", "script only (full charge needs a 2.2 s hold; not tested)"),
            "rev.pounce.charge_time": prm(POUNCE_MAXCHARGE, "s", "script; observed c13 err %s u/s (charge clock = release time)" % f(st(x["speed"] - x["speed_h_release"] for x in c13), 3), len(c13)),
            "rev.pounce.elevation": prm(POUNCE_PITCH_UP, "deg above view pitch (view pitch 0)", "observed %s" % f(st(x["elev_deg"] for x in po), 4), len(po)),
            "rev.pounce.flight_gravity": prm(G, "u/s^2", "observed dedi %s" % f(st(x["g_dedi"]["mean"] for x in po), 3), len(po), None, "no drag, no horizontal change without input"),
            "rev.pounce.landing_slowdown": prm(1.0, "x", "observed (vh after landing = ground friction only)", len(po)),
            "rev.charge.movescale": prm(1.0, "x", "observed (1.15 otherwise)", len(po), None, "the empty-hands toss weapon is active while charging"),
        })
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(P, fh, indent=1)


if __name__ == "__main__":
    main()
