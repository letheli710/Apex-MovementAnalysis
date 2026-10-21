#!/usr/bin/env python3
"""M6-A2 climb / ledge / mantle / superglide analysis (R5Flowstate S21, Gibraltar, empty-handed, 120 fps).

    py -3 a2_climb_analysis.py <session folder> [<session folder> ...] [--json results.json] [--params params.json]

Session kinds are recognised from the runner label:
  *_M6_A2b_h<H> / *_M6_A2_h<H>   ledge-height sessions (a2_climb, a2_walk, a2_hang, a2_cancel, a2_hop, a2_hop_back)
  *_M6_A2_sg_off / *_sg_on       superglide sessions (e7_<variant>_f<N>)

Only runner trials with ok=true and warmup=false are scored. Physics truth = client first-time MOVE-TRACE usercmds
(raw logs, joined to the client HSD frames for dt and game time, see a2_load.py). Client [HSD-STATE] lines give the
per-frame state flags (wr = climbing, trav/mant = mantle traversal). Dedi MOVE-TRACE rows of the same usercmd give
client/dedi parity; dedi HSD events give JUMP / MANTLE / wallrun edges; [MB-*] lines give the SDK mantle-boost FSM.

stdlib only; no local paths (session folders come from the command line). Nothing is tuned to pass: every scored
trial is classified and every failure or odd case is printed.
"""
import argparse
import bisect
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2_load as L  # noqa: E402

G = 750.0
FLOOR = 294.92
IN_JUMP, IN_DUCK, IN_FWD, IN_BACK, IN_RIGHT = 0x2, 0x4, 0x8, 0x10, 0x400
T_TRAV_NORMAL = 0.59           # M3 measured plain traversal duration (WALL-MANTLE-MODEL.md section 2.3)
LEDGE_SG = 532.84              # mantle exit z on the superglide rock (H 232 geometry, measured in the A2b h232 session)
M3 = {"plain_exit_h": 299.0, "plain_exit_vz": 0.0, "fail3_exit_vz": 289.82, "boost_exit_h": 388.708, "boost_exit_vz": 367.42,
      "climb_end_z": 441.93, "climb_Z0": 475.33, "climb_k": 1.735, "final_dvz_dt0": 208.0}
st, fmt = L.stats, L.fmt


def r(x, n=3):
    return None if x is None else round(x, n)


def hs(c, post=True):
    return L.hs(c, post)


def lin_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    b = my - m * mx
    return m, b, math.sqrt(sum((y - m * x - b) ** 2 for x, y in zip(xs, ys)) / n)


def edges(cmds, bit, start=0):
    return [i for i in range(max(start, 1), len(cmds)) if cmds[i]["buttons"] & bit and not cmds[i - 1]["buttons"] & bit]


def dt_of(c, fps):
    return c["dt"] if c.get("dt") else 1.0 / fps


# ----------------------------------------------------------------------------- state segments
def segments(states, flag):
    """Contiguous runs of states[flag] == True -> list of (t_start, t_end, n_frames); t_end = t of the first false."""
    out, s, n = [], None, 0
    for x in states:
        if x.get(flag):
            if s is None:
                s, n = x["t"], 0
            n += 1
        elif s is not None:
            out.append((s, x["t"], n))
            s = None
    if s is not None:
        out.append((s, states[-1]["t"], n))
    return out


def state_at(states, t):
    ts = [x["t"] for x in states]
    k = bisect.bisect_left(ts, t - 0.0005)
    return states[k] if k < len(states) else None


# ----------------------------------------------------------------------------- per-trial phases
def contact_idx(cmds, start):
    return next((i for i in range(start, len(cmds)) if hs(cmds[i], False) > 150 and hs(cmds[i]) < 50), None)


def gaps(cmds, start=1):
    return [i for i in range(max(start, 1), len(cmds)) if cmds[i]["cmd"] - cmds[i - 1]["cmd"] != 1]


def climb_phase(cmds, k, fps):
    """From the contact usercmd k: follow the climb until final jump-up (dvz > 100), traversal (MOVE-TRACE gap),
    detach (post vx < -50, outward) or leaving the wall without either."""
    c0 = cmds[k]
    out = {"contact_i": k, "contact_t": c0["t"], "contact_pre_z": c0["oz"], "contact_post_z": c0["poz"],
           "contact_pre_vz": c0["vz"], "contact_post_vz": c0["pvz"], "contact_pre_h": hs(c0, False),
           "contact_dvz": c0["pvz"] - c0["vz"], "contact_x": c0["ox"]}
    e, kind = None, None
    for i in range(k + 1, len(cmds)):
        c = cmds[i]
        if c["cmd"] - cmds[i - 1]["cmd"] != 1:
            e, kind = i, "traversal"
            break
        if c["pvz"] - c["vz"] > 100:
            e, kind = i, "final_jump"
            break
        if c["pvx"] < -50:
            e, kind = i, "detach"
            break
        if c["ground"] == 1 and c["poz"] < FLOOR + 0.5 and c["vz"] < 0:
            e, kind = i, "floor"
            break
    out["end_i"], out["end_kind"] = e, kind
    if e is None:
        return out
    cl = cmds[k + 1:e]
    out["climb_cmds"] = len(cl) + 1
    out["duration"] = sum(dt_of(c, fps) for c in cmds[k:e])           # contact cmd start .. end cmd start
    out["end_pre_z"] = cmds[e]["oz"] if kind != "traversal" else cmds[e - 1]["poz"]
    out["end_vz_pre"] = cmds[e]["vz"] if kind != "traversal" else cmds[e - 1]["pvz"]
    out["gain_from_contact"] = out["end_pre_z"] - c0["poz"]
    out["end_above_floor"] = out["end_pre_z"] - FLOOR
    if kind == "final_jump":
        f = cmds[e]
        out.update(final_dvz=f["pvz"] - f["vz"], final_post_vx=f["pvx"], final_post_vz=f["pvz"], final_dt=dt_of(f, fps),
                   final_V_dt0=f["pvz"] - f["vz"] + 0.5 * G * dt_of(f, fps) + 375.0 * dt_of(f, fps) * 0,
                   prev_pre_z=cmds[e - 1]["oz"])
    held = [c for c in cl if c["fwd"] > 0]
    if len(held) >= 3:
        ipk = max(range(len(cl)), key=lambda i: cl[i]["pvz"])
        out["peak_vz"] = cl[ipk]["pvz"]
        out["peak_z"] = cl[ipk]["poz"]
        out["peak_t"] = sum(dt_of(c, fps) for c in cmds[k:k + 2 + ipk])
        acc = [(c["pvz"] - c["vz"]) / dt_of(c, fps) for c in cl[:max(ipk - 1, 1)]]
        out["accel"] = st(acc)
        out["accel_mean"] = out["accel"].get("mean")
        dec = [c for c in cl[ipk + 1:] if c["fwd"] > 0]
        out["decay_rate_step"] = st([-(c["pvz"] - c["vz"]) / dt_of(c, fps) / c["vz"] for c in dec if c["vz"] > 1]).get("mean")
        if len(dec) >= 6:
            m, b, rms = lin_fit([c["poz"] for c in dec], [c["pvz"] for c in dec])
            out["line_k"] = -m
            out["line_Z0"] = -b / m
            out["line_rms"] = rms
            out["line_n"] = len(dec)
    return out


def traversal_phase(T, cmds, g, fps):
    last, first = cmds[g - 1], cmds[g]
    fr = [f for f in T["frames"] if last["t"] is not None and first["t"] is not None and last["t"] < f["t"] < first["t"]]
    peak = max(fr, key=lambda f: f["oz"]) if fr else None
    out = {"gap_i": g, "t_last": last["t"], "t_first": first["t"],
           "duration": (first["t"] - last["t"]) if (first["t"] and last["t"]) else None,
           "start_z": last["poz"], "start_x": last["pox"], "start_vz": last["pvz"], "start_vx": last["pvx"],
           "exit_x": first["ox"], "exit_z": first["oz"], "exit_ground": first["ground"], "exit_duck": first["duck"],
           "exit_pre": (first["vx"], first["vy"], first["vz"]), "exit_post": (first["pvx"], first["pvy"], first["pvz"]),
           "exit_pre_h": hs(first, False), "exit_post_h": hs(first), "exit_dt": dt_of(first, fps),
           "exit_buttons": first["buttons"], "frames": len(fr),
           "peak_z": peak["oz"] if peak else None, "peak_x": peak["ox"] if peak else None}
    out["rise"] = first["oz"] - last["poz"]
    out["completed"] = first["oz"] > last["poz"] + 5 and first["ox"] > -13712
    # reversal inside the traversal (mantle cancel): x moves back by > 3 u after its maximum
    if fr:
        xmax = max(f["ox"] for f in fr)
        out["x_back_after_max"] = xmax - fr[-1]["ox"]
        imax = max(range(len(fr)), key=lambda i: fr[i]["ox"])
        out["t_xmax_rel_start"] = fr[imax]["t"] - last["t"]
        fwd_drop = next((f for f in fr if f["in_fwd"] == 0), None)
        out["t_w_release_rel_start"] = (fwd_drop["t"] - last["t"]) if fwd_drop else None
    sv = T["sv"].get(first["cmd"])
    if sv:
        out["sv_exit_pre"] = (sv["vx"], sv["vy"], sv["vz"])
        out["sv_exit_post"] = (sv["pvx"], sv["pvy"], sv["pvz"])
        out["sv_exit_pos"] = (sv["ox"], sv["oz"])
    return out


def parity(T, i0, n=6):
    """max |client - dedi| over position and velocity of cmds i0 .. i0+n-1."""
    worst = 0.0
    cnt = 0
    for c in T["cmds"][i0:i0 + n]:
        s = T["sv"].get(c["cmd"])
        if not s:
            continue
        cnt += 1
        worst = max(worst, max(abs(c[k] - s[k]) for k in ("pox", "poy", "poz", "pvx", "pvy", "pvz")))
    return {"cmds": cnt, "max_diff": worst}


def parity_all(T):
    n, wp, wv, worst, nbad = 0, 0.0, 0.0, None, 0
    t_first = next((c["t"] for c in T["cmds"] if c.get("t")), 0.0)
    for c in T["cmds"]:
        s = T["sv"].get(c["cmd"])
        if not s:
            continue
        n += 1
        wp = max(wp, max(abs(c[k] - s[k]) for k in ("pox", "poy", "poz")))
        dv = max(abs(c[k] - s[k]) for k in ("pvx", "pvy", "pvz"))
        nbad += dv > 1.0
        if dv > wv:
            wv = dv
            worst = {"cmd": c["cmd"], "t_in_trial": r((c["t"] or 0) - t_first), "cl_pre": (c["vx"], c["vy"], c["vz"]),
                     "cl_post": (c["pvx"], c["pvy"], c["pvz"]), "sv_pre": (s["vx"], s["vy"], s["vz"]),
                     "sv_post": (s["pvx"], s["pvy"], s["pvz"]), "z": c["oz"], "x": c["ox"], "ground": (c["ground"], s["ground"])}
    return {"cmds": n, "max_pos": wp, "max_vel": wv, "cmds_dv_gt1": nbad, "worst": worst}


# ----------------------------------------------------------------------------- height sessions
def release_phase(cmds, i_rel, fps, sv=None):
    """W released while climbing: what happens on the wall (vz series, detach, landing)."""
    out = {"rel_i": i_rel, "rel_z": cmds[i_rel]["oz"], "rel_vz": cmds[i_rel]["vz"]}
    c = cmds[i_rel]
    out["first_dvz_dt"] = (c["pvz"] - c["vz"]) / dt_of(c, fps)
    out["first_dvx"] = c["pvx"] - c["vx"]
    out["first_dvy"] = c["pvy"] - c["vy"]
    i, t = i_rel, 0.0
    series = []
    det = None
    while i < len(cmds):
        c = cmds[i]
        if c["cmd"] - cmds[i - 1]["cmd"] != 1:
            break
        if c["pvx"] < -50:
            det = i
            break
        series.append((round(t, 4), round(c["poz"], 2), round(c["pvz"], 2), round((c["pvz"] - c["vz"]) / dt_of(c, fps), 1)))
        t += dt_of(c, fps)
        i += 1
    out["series"] = series[:80]
    zero = next((s for s in series if s[2] <= 0), None)
    out["t_to_vz0"] = zero[0] if zero else None
    out["z_top"] = max(s[1] for s in series) if series else None
    neg = [s[3] for s in series if s[2] < -20]
    out["accel_falling"] = st(neg)
    if sv is not None:
        svn = []
        for c in cmds[i_rel:i]:
            s = sv.get(c["cmd"])
            if s and s["pvz"] < -20 and s["pvx"] > -50:
                svn.append((s["pvz"] - s["vz"]) / dt_of(c, fps))
        out["sv_accel_falling"] = st(svn)
    if series:
        pos = [s[3] for s in series[1:] if s[2] > 5]
        out["decel_rising"] = st(pos)
    if det is not None:
        d = cmds[det]
        out.update(detach_i=det, detach_t_after_rel=t, detach_z=d["oz"], detach_pre=(d["vx"], d["vy"], d["vz"]),
                   detach_post=(d["pvx"], d["pvy"], d["pvz"]), detach_dvx=d["pvx"] - d["vx"],
                   detach_dvz=d["pvz"] - d["vz"])
    return out


def press_phase(T, cmds, i, fps, kind):
    c = cmds[i]
    s = state_at(T["states"], c["t"]) if c.get("t") and T["states"] else None
    out = {"kind": kind, "press_i": i, "ground": c["ground"], "z": c["oz"], "x": c["ox"],
           "state": {k: s.get(k) for k in ("trav", "mant", "hang", "wr")} if s else None,
           "pre": (c["vx"], c["vy"], c["vz"]), "post": (c["pvx"], c["pvy"], c["pvz"]),
           "dvz": c["pvz"] - c["vz"], "V": c["pvz"] - c["vz"] + 0.5 * G * dt_of(c, fps) if c["pvz"] - c["vz"] > 100 else None,
           "on": "ledge_top" if c["ground"] and c["oz"] > FLOOR + 30 else "floor" if c["ground"] else "air"}
    nx = cmds[min(i + 12, len(cmds) - 1)]
    out["post_0p1s"] = (nx["pvx"], nx["pvy"], nx["pvz"])
    return out


def height_trial(T, H, fps):
    cmds = T["cmds"]
    sch = T["schedule"]
    R = {"run": T["run"], "schedule": sch, "H": H, "fps": T["fps"], "join": T["join"], "parity": parity_all(T),
         "sv_evt": [e["evt"] for e in T["sv_evt"]], "notes": []}
    js = edges(cmds, IN_JUMP)
    j = js[0] if js else None
    t0 = cmds[j]["t"] if j is not None else None
    if j is not None:
        R["jump_x"] = cmds[j]["ox"]
        R["jump_speed"] = hs(cmds[j], False)
    if sch == "a2_walk":
        t0 = next((c["t"] for c in cmds if c["fwd"] > 0), cmds[0]["t"])
    R["t0"] = t0
    # state segments relative to t0
    stt = T["states"]
    R["has_states"] = bool(stt)
    for flag in ("wr", "trav", "hang"):
        R["seg_" + flag] = [(r(a - t0), r(b - t0), n) for a, b, n in segments(stt, flag)] if stt and t0 else []
    # W release (fwd 1 -> 0)
    rel = next((i for i in range((j or 0) + 1, len(cmds)) if cmds[i]["fwd"] == 0 and cmds[i - 1]["fwd"] > 0), None)
    R["rel_t"] = r(cmds[rel]["t"] - t0) if rel is not None and cmds[rel]["t"] else None
    start = j if j is not None else 0
    k = contact_idx(cmds, start)
    R["contact"] = k is not None
    gs = gaps(cmds, start + 1)
    g = gs[0] if gs else None
    if k is not None:
        R["contact_t"] = r(cmds[k]["t"] - t0) if cmds[k]["t"] else None
        R["contact_x"] = cmds[k]["ox"]
        R["contact_pre_z"] = cmds[k]["oz"]
        in_wr = state_at(stt, cmds[k]["t"]) if stt and cmds[k]["t"] else None
        R["contact_state_wr"] = in_wr.get("wr") if in_wr else None
        if g is not None and g == k + 1 and not (R["seg_wr"] and R["seg_wr"][0][0] < (cmds[g]["t"] - t0) - 0.02):
            R["climb"] = None
        else:
            R["climb"] = climb_phase(cmds, k, fps)
    if g is not None:
        R["trav"] = traversal_phase(T, cmds, g, fps)
        R["trav"]["start_t"] = r(cmds[g - 1]["t"] - t0) if cmds[g - 1]["t"] else None
        R["_prev_poz"] = cmds[g - 2]["poz"] if g >= 2 else None     # usercmd before the one that triggered the mantle
        if rel is not None and cmds[rel]["t"] and R["trav"]["t_last"] and cmds[rel]["t"] < R["trav"]["t_first"]:
            R["trav"]["rel_rel_start"] = R["trav"].get("t_w_release_rel_start")
    # landing on top without traversal (low ledge)
    if j is not None:
        land = next((i for i in range(j + 1, len(cmds)) if cmds[i - 1]["ground"] == 0 and cmds[i]["ground"] == 1
                     and cmds[i]["cmd"] - cmds[i - 1]["cmd"] == 1), None)
        if land is not None:
            R["first_land_z"] = cmds[land]["oz"]
            R["first_land_t"] = r(cmds[land]["t"] - t0) if cmds[land]["t"] else None
    # outcome
    cl = R.get("climb")
    tv = R.get("trav")
    wr_n = len(R["seg_wr"])
    if sch == "a2_walk":
        rise = max(c["poz"] for c in cmds) - FLOOR
        R["walk_max_rise"] = rise
        R["walk_wr_segments"] = wr_n
        R["walk_wr_frames"] = sum(s[2] for s in R["seg_wr"])
        if tv:
            R["outcome"] = "mantle"
        elif wr_n:
            R["outcome"] = "blocked_ground_microclimbs"
        elif k is not None:
            R["outcome"] = "blocked"
        else:
            R["outcome"] = "no_contact"
        if k is not None:
            R["walk_stop_x"] = cmds[k]["pox"]
    else:
        if tv and (not cl or cl.get("end_kind") == "traversal" and cl.get("climb_cmds", 0) <= 3):
            # traversal starts on the contact usercmd or within 2 usercmds of it (wr flag set for <= 2 frames)
            R["outcome"] = "instant_mantle"
        elif tv and cl and cl.get("end_kind") == "traversal":
            R["outcome"] = "climb_mantle"
        elif tv and cl and cl.get("end_kind") == "final_jump":
            R["outcome"] = "climb_jumpup_mantle"
        elif cl and cl.get("end_kind") == "final_jump":
            R["outcome"] = "climb_jumpup_fall"
        elif cl and cl.get("end_kind") in ("detach", "floor"):
            R["outcome"] = "climb_slide_fall"
        elif k is None and R.get("first_land_z", 0) > FLOOR + 20:
            R["outcome"] = "land_on_top"
        else:
            R["outcome"] = "other"
        if tv and not tv["completed"]:
            R["outcome"] += "+mantle_aborted"
    if tv:
        R["ledge_z"] = tv["exit_z"] if tv["completed"] else None
    # W released on the wall
    if rel is not None and cl and cl.get("end_i") and rel < cl["end_i"] and rel > cl["contact_i"]:
        R["release_on_wall"] = release_phase(cmds, rel, fps, T["sv"])
        R["release_on_wall"]["t_rel_after_contact"] = sum(dt_of(c, fps) for c in cmds[cl["contact_i"]:rel])
        R["release_on_wall"]["detach_t_after_contact"] = (R["release_on_wall"]["t_rel_after_contact"] +
                                                          R["release_on_wall"].get("detach_t_after_rel", float("nan")))
    # later climbs (re-contact after the final jump-up / re-climb from the floor)
    R["wr_segments_after_first"] = R["seg_wr"][1:]
    # presses after the release: back / jump
    if sch in ("a2_cancel", "a2_hop", "a2_hop_back") and rel is not None:
        b = [i for i in edges(cmds, IN_BACK, rel + 1)]
        jj = [i for i in edges(cmds, IN_JUMP, rel + 1)]
        if sch == "a2_cancel" and b:
            R["press"] = press_phase(T, cmds, b[0], fps, "back")
        elif jj:
            R["press"] = press_phase(T, cmds, jj[0], fps, "jump" if sch == "a2_hop" else "back+jump")
        if R.get("press") is not None:
            R["press"]["t"] = r(cmds[R["press"]["press_i"]]["t"] - t0) if cmds[R["press"]["press_i"]]["t"] else None
    R["mb"] = [m["raw"][:200] for m in T["mb"]]
    return R


# ----------------------------------------------------------------------------- superglide sessions
def lurch_pred(v, w, t, lmax=209.3):
    lam = 0.7 * max(0.0, min(1.0, (0.5 - t) / 0.3))
    sp = math.hypot(*v)
    if lam <= 0 or sp == 0:
        return v
    u = (v[0] / sp, v[1] / sp)
    d = ((1 - lam) * u[0] + lam * w[0], (1 - lam) * u[1] + lam * w[1])
    dn = math.hypot(*d)
    if dn == 0:
        return v
    d = (d[0] / dn, d[1] / dn)
    D = (sp * d[0] - v[0], sp * d[1] - v[1])
    Dn = math.hypot(*D)
    if Dn > lmax:
        D = (D[0] * lmax / Dn, D[1] * lmax / Dn)
    return (v[0] + D[0], v[1] + D[1])


def sg_trial(T, fps, fsm_on):
    cmds = T["cmds"]
    sch = T["schedule"]
    m = re.fullmatch(r"e7_(\w+?)_f(\d+)", sch)
    var, N = m.group(1), int(m.group(2))
    R = {"run": T["run"], "schedule": sch, "variant": var, "N": N, "fsm_on": fsm_on, "fps": T["fps"], "join": T["join"],
         "sv_evt": [e["evt"] for e in T["sv_evt"]], "notes": []}
    js = edges(cmds, IN_JUMP)
    fr = T["frames"]
    fj = [i for i in range(1, len(fr)) if fr[i]["in_jump"] and not fr[i - 1]["in_jump"]]
    fd = [i for i in range(1, len(fr)) if fr[i]["in_duck"] and not fr[i - 1]["in_duck"]]
    R["press_frame_offsets"] = [x - fj[0] for x in fj] if fj else []
    R["duck_frame_offsets"] = [x - fj[0] for x in fd] if fj else []
    R["duck_minus_jump_frames"] = (fd[0] - fj[1]) if len(fj) > 1 and fd else None
    j = js[0]
    k = contact_idx(cmds, j)
    cl = climb_phase(cmds, k, fps) if k is not None else None
    R["climb_end_kind"] = cl.get("end_kind") if cl else None
    gs = gaps(cmds, j + 1)
    if not gs:
        R["class"] = "no_traversal"
        return R
    g = gs[0]
    tv = traversal_phase(T, cmds, g, fps)
    R["trav"] = tv
    pt = fr[fj[1]]["t"] if len(fj) > 1 else None
    if pt is not None:
        pf, pp = fr[fj[1]], fr[fj[1] - 1]
        # position on the frame before the press (the press frame itself already shows the cut / snap)
        R["press_z"], R["press_x"] = pp["oz"], pp["ox"]
        R["press_rise_frac"] = (pp["oz"] - tv["start_z"]) / (LEDGE_SG - tv["start_z"])
        R["press_frame_pos"] = (pf["ox"], pf["oz"])
        R["press_frame_snap"] = (pf["ox"] - pp["ox"], pf["oz"] - pp["oz"])
        R["press_rel_trav_start"] = pt - tv["t_last"]
        R["press_rel_trav_end"] = pt - tv["t_first"]
        R["press_frames_before_end"] = (tv["t_first"] - pt) * fps
        R["press_frac_of_normal"] = (pt - tv["t_last"]) / T_TRAV_NORMAL
    first = cmds[g]
    R["exit_pre_h"], R["exit_pre_vz"] = hs(first, False), first["vz"]
    R["exit_post_h"], R["exit_post_vz"] = hs(first), first["pvz"]
    # vertical launch: native jump law post = V - 1.5*g*dt (M2), FSM forced jump post = V - g*dt (M3)
    R["exit_V"] = (first["pvz"] + (1.0 if fsm_on else 1.5) * G * dt_of(first, fps)) if first["pvz"] > 100 else None
    R["exit_buttons"] = first["buttons"]
    R["exit_ground"], R["exit_duck"] = first["ground"], first["duck"]
    R["trav_duration"] = tv["duration"]
    R["exit_x"], R["exit_z"] = first["ox"], first["oz"]
    R["parity_exit"] = parity(T, g, 6)
    R["parity_all"] = parity_all(T)
    sv = T["sv"].get(first["cmd"])
    R["sv_exit_pre"] = (sv["vx"], sv["vy"], sv["vz"]) if sv else None
    # jump on top: a ground jump after the exit
    jt = [i for i in edges(cmds, IN_JUMP, g) if cmds[i]["ground"] == 1]
    R["jump_on_top"] = None
    if jt and cmds[jt[0]]["oz"] > FLOOR + 30:
        c = cmds[jt[0]]
        R["jump_on_top"] = {"cmds_after_exit": jt[0] - g, "post_h": hs(c), "post_vz": c["pvz"], "pre_h": hs(c, False),
                            "duck_next": [cmds[q]["duck"] for q in range(jt[0], min(jt[0] + 4, len(cmds)))]}
    # class
    trig = [x for x in T["mb"] if x["tag"] == "TRIG"]
    app = [x for x in T["mb"] if x["tag"] == "APPLY"]
    svr = [x["result"] for x in trig if x["side"] == "sv"]
    clr = [x["result"] for x in trig if x["side"] == "cl"]
    R["mb_trig"] = [{"side": x["side"], "anim": x["anim"], "delta": x["delta"], "gate": x["gate"], "result": x["result"]}
                    for x in trig]
    R["mb_apply"] = [{"side": x["side"], "state": x["state"], "speed": x["speed"], "vel": x["vel"]} for x in app]
    R["mb_cl_sv_mismatch"] = bool(svr and clr and svr[0] != clr[0])
    eh, ev = R["exit_pre_h"], R["exit_pre_vz"]
    if fsm_on and 4 in svr:
        cls = "boost_state4"
    elif fsm_on and 3 in svr:
        cls = "failed_state3"
    elif eh > 320 and ev > 200:
        cls = "superglide_native"
    elif ev > 200:
        cls = "mantle_jump_native"
    elif R["jump_on_top"]:
        cls = "jump_on_top"
    elif not tv["completed"] or first["ground"] == 0:
        cls = "cut_to_top_no_jump"
    else:
        cls = "mantle_only"
    R["class"] = cls
    R["trav_early_by"] = T_TRAV_NORMAL - tv["duration"] if tv["duration"] else None
    # lurch after the exit (mbl): first moveright edge after the exit
    rr = edges(cmds, IN_RIGHT, g)
    if rr:
        i = rr[0]
        c = cmds[i]
        t_exit = cmds[g]["t"]
        tj = (c["t"] - t_exit) + dt_of(cmds[g], fps) if c["t"] and t_exit else None   # time since the exit-jump cmd start
        yaw = math.radians(c.get("yaw") or 0.0)
        fwd = (math.cos(yaw), math.sin(yaw))
        right = (math.sin(yaw), -math.cos(yaw))
        wv = (fwd[0] * (1 if c["fwd"] > 0 else 0) + right[0] * (1 if c["sidemove"] > 0 else 0),
              fwd[1] * (1 if c["fwd"] > 0 else 0) + right[1] * (1 if c["sidemove"] > 0 else 0))
        wn = math.hypot(*wv)
        w = (wv[0] / wn, wv[1] / wn) if wn else (0.0, 0.0)
        pred = lurch_pred((c["vx"], c["vy"]), w, tj) if tj is not None else None
        prev = cmds[i - 1]
        R["lurch"] = {"press_cmds_after_exit": i - g, "t_since_exit_jump": tj, "fwd": c["fwd"], "side": c["sidemove"],
                      "pre": (c["vx"], c["vy"]), "post": (c["pvx"], c["pvy"]), "dv": (c["pvx"] - c["vx"], c["pvy"] - c["vy"]),
                      "prev_dv": (prev["pvx"] - prev["vx"], prev["pvy"] - prev["vy"]),
                      "pred_lurch_post": pred, "pred_dv": (pred[0] - c["vx"], pred[1] - c["vy"]) if pred else None,
                      "sv_post": (T["sv"][c["cmd"]]["pvx"], T["sv"][c["cmd"]]["pvy"]) if c["cmd"] in T["sv"] else None,
                      "next_dv": [(round(cmds[q]["pvx"] - cmds[q]["vx"], 3), round(cmds[q]["pvy"] - cmds[q]["vy"], 3))
                                  for q in range(i + 1, min(i + 6, len(cmds)))]}
    return R


# ----------------------------------------------------------------------------- printing / summary
def P(*a):
    print(*a)


def climb_residuals(T, R, fps, k, Z0, Zend, acc=490.0):
    """Re-simulate a W-held climb from the contact usercmd's post state with
    vz = min(vz + acc*dt, k*(Z0 - z)); z += vz*dt; end on the first usercmd whose pre z >= Zend."""
    cl = R.get("climb")
    if not cl or cl.get("end_i") is None:
        return None
    cmds = T["cmds"]
    i0, e = cl["contact_i"], cl["end_i"]
    z, vz = cmds[i0]["poz"], cmds[i0]["pvz"]
    errs, pred_end = [], None
    for i in range(i0 + 1, len(cmds)):
        c = cmds[i]
        if z >= Zend:
            pred_end = i
            break
        if i >= e:
            if cl["end_kind"] != "final_jump":
                break
        dt = dt_of(c, fps)
        vz = min(vz + acc * dt, k * (Z0 - z))
        z += vz * dt
        if i < e:
            errs.append(vz - c["pvz"])
    return {"n": len(errs), "max_abs_vz_err": max(abs(x) for x in errs) if errs else None,
            "rms_vz_err": math.sqrt(sum(x * x for x in errs) / len(errs)) if errs else None,
            "end_cmd_offset": (pred_end - e) if (pred_end is not None and cl["end_kind"] == "final_jump") else None,
            "z_err_at_end": (z - cmds[e - 1]["poz"]) if errs else None}


def summarise_heights(rows):
    out = {}
    Hs = sorted({x["H"] for x in rows})
    for H in Hs:
        hr = [x for x in rows if x["H"] == H]
        D = {}
        for sch in ("a2_climb", "a2_walk", "a2_hang", "a2_cancel", "a2_hop", "a2_hop_back"):
            xs = [x for x in hr if x["schedule"] == sch]
            if not xs:
                continue
            oc = {}
            for x in xs:
                oc[x["outcome"]] = oc.get(x["outcome"], 0) + 1
            d = {"n": len(xs), "outcomes": oc}
            cls = [x["climb"] for x in xs if x.get("climb")]
            if cls:
                for key in ("duration", "gain_from_contact", "end_pre_z", "end_above_floor", "end_vz_pre", "peak_vz",
                            "line_k", "line_Z0", "final_dvz", "final_post_vx", "contact_post_z", "contact_dvz",
                            "decay_rate_step", "accel_mean"):
                    d["climb_" + key] = st([c.get(key) for c in cls])
                d["climb_end_kinds"] = sorted({c.get("end_kind") for c in cls if c.get("end_kind")})
            tvs = [x["trav"] for x in xs if x.get("trav")]
            if tvs:
                for key in ("duration", "start_z", "exit_z", "rise", "exit_pre_h", "exit_post_h", "peak_z"):
                    d["trav_" + key] = st([t.get(key) for t in tvs])
                d["trav_start_below_ledge"] = st([t["exit_z"] - t["start_z"] for t in tvs if t["completed"]])
                d["trav_completed"] = sum(1 for t in tvs if t["completed"])
                d["trav_exit_pre"] = [tuple(r(v, 2) for v in t["exit_pre"]) for t in tvs]
            rw = [x["release_on_wall"] for x in xs if x.get("release_on_wall")]
            if rw:
                for key in ("t_rel_after_contact", "rel_vz", "first_dvz_dt", "t_to_vz0", "z_top", "detach_t_after_rel",
                            "detach_t_after_contact", "detach_z", "detach_dvx", "detach_dvz"):
                    d["rel_" + key] = st([w.get(key) for w in rw])
                d["rel_accel_falling"] = st([w["accel_falling"].get("mean") for w in rw if w["accel_falling"].get("n")])
                d["rel_sv_accel_falling"] = st([w["sv_accel_falling"].get("mean") for w in rw if w.get("sv_accel_falling", {}).get("n")])
                d["rel_decel_rising"] = st([w["decel_rising"].get("mean") for w in rw if w.get("decel_rising", {}).get("n")])
            pr = [x["press"] for x in xs if x.get("press")]
            if pr:
                d["press_on"] = sorted({p["on"] for p in pr})
                d["press_t"] = st([p.get("t") for p in pr])
                d["press_post"] = [tuple(r(v, 2) for v in p["post"]) for p in pr]
                d["press_V"] = st([p.get("V") for p in pr])
            if sch == "a2_walk":
                d["walk_wr_segments"] = [x.get("walk_wr_segments") for x in xs]
                d["walk_max_rise"] = st([x.get("walk_max_rise") for x in xs])
                d["walk_stop_x"] = st([x.get("walk_stop_x") for x in xs])
            d["ledge_z"] = st([x.get("ledge_z") for x in xs])
            D[sch] = d
        out[str(H)] = D
    return out


def build_params(rows, HS, anchor, fit_rt, SG, SGsum):
    out = []

    def add(name, value, unit, label, n=None, spread=None, note=""):
        out.append({"name": name, "value": value, "unit": unit, "label": label, "n": n,
                    "spread": spread if spread is None or isinstance(spread, str) else round(spread, 4), "note": note})

    def S(vals):
        return st([v for v in vals if v is not None])

    full = [x["climb"] for x in rows if x["schedule"] == "a2_climb" and x.get("climb") and x["climb"].get("end_kind") == "final_jump"]
    held = [x["climb"] for x in rows if x.get("climb") and x["climb"].get("line_k") and
            x["climb"].get("end_kind") in ("final_jump", "traversal")]
    s = S([c.get("accel_mean") for c in held])
    add("climb_accel_phase", s.get("mean"), "u/s^2", "fit", s["n"], s.get("sd"), "vz += a*dt until the speed line is reached")
    s = S([c.get("line_k") for c in held])
    add("climb_speed_line_k", s.get("mean"), "1/s", "fit", s["n"], s.get("sd"),
        "vz = k*(Z0 - z) after the peak (least-squares on post vz vs post z); per-step -dvz/dt/vz is listed separately")
    s = S([c.get("decay_rate_step") for c in held])
    add("climb_decay_rate_per_step", s.get("mean"), "1/s", "fit", s["n"], s.get("sd"), "M3 value 1.735 used the same per-step definition")
    s = S([c.get("line_Z0") for c in held])
    add("climb_speed_line_Z0_above_floor", s.get("mean") - FLOOR if s.get("n") else None, "u", "fit", s["n"], s.get("sd"),
        "identical at H 180..400 -> floor/takeoff-anchored, not ledge-anchored")
    lo, hi = anchor.get("bracket", (None, None))
    add("climb_end_height_above_floor", ((lo + hi) / 2 - FLOOR) if lo else None, "u", "meas", len(full),
        f"bracket ({lo - FLOOR:.3f}, {hi - FLOOR:.3f}]" if lo else None,
        "climb ends (final jump-up) on the first usercmd whose pre z reaches it; same at H 232/300/400")
    s = S([c["duration"] for c in full])
    add("climb_duration_full", s.get("mean"), "s", "meas", s["n"], s.get("sd"), "contact -> final jump-up (W held)")
    s = S([c["gain_from_contact"] for c in full])
    add("climb_height_gained_full", s.get("mean"), "u", "meas", s["n"], s.get("sd"), "from contact; climbHeight census 100")
    s = S([c["final_dvz"] for c in full])
    add("climb_final_jumpup_dvz_120fps", s.get("mean"), "u/s", "meas", s["n"], s.get("sd"), "M3 dt->0 value 208")
    s = S([c["final_post_vx"] for c in full])
    add("climb_final_jumpup_out_vx_120fps", s.get("mean"), "u/s", "meas", s["n"], s.get("sd"), "outward (-n); M3 68.1 - 500*dt")
    rb = anchor.get("reach_bracket")
    add("mantle_reach_on_wall", 80.0, "u", "fit", None,
        f"max observed at trigger {rb[0]:.2f}" if rb else None,
        "mantle starts once ledge_top - origin_z is within ~75-80 u; not a sharp height threshold: triggers seen at gaps "
        "up to 79.9 u, but other climbs passed gaps down to 76.0 u without triggering (lag of up to ~3 usercmds)")
    s = anchor.get("reach_air", {})
    add("mantle_reach_after_jumpup", s.get("mean"), "u", "meas", s.get("n"), s.get("sd"), "ledge - origin z at the traversal start in the air")
    if fit_rt:
        add("traversal_duration_intercept", fit_rt["intercept_s"], "s", "fit", fit_rt["n"], f"rms {fit_rt['rms']:.4f}", "T = a + b*rise")
        add("traversal_duration_per_u", fit_rt["slope_s_per_u"], "s/u", "fit", fit_rt["n"], f"rms {fit_rt['rms']:.4f}", "rise 43..80 u")
    ex = [x["trav"] for x in rows if x.get("trav") and x["trav"]["completed"]]
    add("mantle_exit_speed_W_held", 299.0, "u/s", "meas", sum(1 for t in ex if t["exit_pre_h"] > 250), "0",
        "pre-velocity of the first post-traversal usercmd = sprint pose speed along the move dir, vz 0. In 24/65 exits "
        "(H90/H120 only) that usercmd then loses 9.46 u/s (both sides in 20, client only in 4) and is back at 299 within "
        "a few usercmds; cause [unknown]")
    add("mantle_exit_speed_W_released", 0.0, "u/s", "meas", sum(1 for t in ex if t["exit_pre_h"] < 1), "0",
        "W released during the traversal (after the cancel window) -> exit at rest")
    add("mantle_exit_offset_past_face", -13698.1 - (-13704.5), "u", "meas", len(ex), "0",
        "exit origin x is fixed (-13698.1) at every height; face line at climb height ~ -13704.5 (contact origin + 16)")
    cb = anchor.get("cancel_bracket_frac")
    add("mantle_cancel_window_frac", cb, "frac of T", "meas", None, None,
        "W released at frac <= lo -> traversal reverses and drops; >= hi -> completes at rest. Threshold inside "
        "the bracket is [unknown]; Unity default 0.5 is [design-needed]")
    ab = [q for q in anchor.get("release_in_traversal", []) if not q["completed"]]
    s = S([q["reverse_s"] for q in ab])
    add("mantle_cancel_reverse_time", s.get("mean"), "s", "meas", s.get("n"), s.get("sd"),
        "after the release the path runs back out ~18 u, then the origin snaps to the traversal start z and falls with v = 0")
    rw = [x["release_on_wall"] for x in rows if x.get("release_on_wall") and x["H"] >= 232]
    s = S([w["first_dvz_dt"] for w in rw])
    add("climb_release_first_cmd_dvz_dt", s.get("mean"), "u/s^2", "fit", s.get("n"), s.get("sd"), "first usercmd after W release")
    s = S([w["decel_rising"].get("mean") for w in rw if w.get("decel_rising", {}).get("n")])
    add("climb_release_rising_decel", s.get("mean"), "u/s^2", "fit", s.get("n"), s.get("sd"), "while vz > 5 after release")
    s = S([w["accel_falling"].get("mean") for w in rw if w["accel_falling"].get("n")])
    add("climb_release_slide_down_accel", s.get("mean"), "u/s^2", "fit", s.get("n"), s.get("sd"),
        "while vz < -20, still on the wall (wr=true); dedi value differs by a few u/s^2, see section 2")
    s = S([w.get("detach_t_after_contact") for w in rw if w.get("detach_t_after_contact") == w.get("detach_t_after_contact")])
    add("climb_release_detach_time_after_contact", s.get("mean"), "s", "meas", s.get("n"), s.get("sd"),
        "W was always released 0.63-0.65 s after contact, so 'after contact' and 'after release (0.36 s)' cannot be told apart")
    s = S([w.get("detach_dvx") for w in rw])
    add("climb_detach_pushoff_dv_out", -s.get("mean") if s.get("n") else None, "u/s", "meas", s.get("n"), s.get("sd"),
        "outward velocity added on the detach usercmd (no input held)")
    add("hang_state", "never observed", "", "meas", sum(len(x["seg_hang"]) == 0 for x in rows), None,
        "hang=false on every client frame of every A2b trial; releasing W never stops the player on the wall")
    add("climb_once_per_airborne", True, "", "meas", None, None,
        "after the final jump-up at H 300/400 the player re-touches the face and slides without climbing; a new climb "
        "starts only after landing at the wall with W held")
    # superglide
    off = [x for x in SG if not x["fsm_on"]]
    sgn = [x for x in off if x["class"] == "superglide_native"]
    mj = [x for x in off if x["class"] == "mantle_jump_native"]
    s = S([x["exit_pre_h"] for x in sgn])
    add("native_superglide_exit_h", s.get("mean"), "u/s", "meas", s.get("n"), s.get("sd"),
        "FSM off, jump in the traversal then crouch on the exit usercmd; = slide-start boost cap 460 (M3 slide model "
        "min(v + 150*msc, 460)); client = dedi")
    s = S([x["exit_V"] for x in sgn + mj])
    add("native_mantle_jump_V", s.get("mean"), "u/s", "meas", s.get("n"), s.get("sd"),
        "vertical launch, native jump law post vz = V - 1.5*g*dt (same as a ground jump, 289.8 = sqrt(2*750*56))")
    s = S([x["exit_pre_h"] for x in mj])
    add("native_mantle_jump_exit_h", s.get("mean"), "u/s", "meas", s.get("n"), s.get("sd"), "FSM off, no crouch")
    cut = [x for x in off if x["class"] == "cut_to_top_no_jump"]
    s = S([x["press_rel_trav_start"] for x in cut])
    add("native_early_press_cut", s.get("max"), "s after traversal start", "meas", s.get("n"), None,
        "presses up to this time (f196 all, f200 4/10) end the traversal at ledge height with v = (299,0,0) and no jump")
    s = S([x["press_rel_trav_start"] for x in sgn + mj])
    add("native_jump_press_window_start", s.get("min"), "s after traversal start", "meas", s.get("n"), None,
        "earliest press that produced the jump; f200 is a mixed band, the hidden variable is [unknown]")
    on = [x for x in SG if x["fsm_on"] and x["class"] == "boost_state4"]
    s = S([x["exit_pre_h"] for x in on])
    add("fsm_boost_exit_h", s.get("mean"), "u/s", "meas", s.get("n"), s.get("sd"), "= 1.3*299 (src); crouch same frame / one frame early: no change")
    s = S([x["exit_V"] for x in on])
    add("fsm_boost_exit_V", s.get("mean"), "u/s", "meas", s.get("n"), s.get("sd"), "= sqrt(2*750*90) (src)")
    lu = [x["lurch"] for x in SG if x.get("lurch") and x["class"] == "boost_state4"]
    s = S([math.hypot(*l["dv"]) for l in lu])
    add("fsm_post_boost_lurch_dv", s.get("mean"), "u/s", "meas", s.get("n"), s.get("max"),
        f"moveright press 0.19-0.22 s after the boost exit; the M3 lurch law predicts |dv| "
        f"{S([math.hypot(*l['pred_dv']) for l in lu]).get('mean', 0):.1f} -> suppressed (src: state 4 masks tap strafe)")
    add("superglide_choice_for_unity", "design-needed", "", "design-needed", None, None,
        "native (460 + V 289.8, frame-order exploit) vs SDK FSM (388.7 / 367.4, 133 ms window) vs none")
    return out


FACE_X = -13704.5      # face line at climb height (round-1 contact origin x + 16 u hull half-width)
LANE_A_X = -14100.0    # round-1 a2_* start x (tools/hsd_trial.py LANE_A)


def round2_trial(T, fps):
    """Round-2 (a2r_*) validity and outcome: did the trial reach the face at all?"""
    cmds = T["cmds"]
    js = edges(cmds, IN_JUMP)
    j = js[0] if js else None
    rel = next((i for i in range((j or 0) + 1, len(cmds)) if cmds[i]["fwd"] == 0 and cmds[i - 1]["fwd"] > 0), None)
    k = contact_idx(cmds, j or 0)
    t0 = cmds[j]["t"] if j is not None else None
    land = None
    if j is not None:
        land = next((i for i in range(j + 1, len(cmds)) if cmds[i - 1]["ground"] == 0 and cmds[i]["ground"] == 1), None)
    xmax = max(c["pox"] for c in cmds)
    R = {"run": T["run"], "schedule": T["schedule"], "fps": T["fps"], "join": T["join"],
         "start_x": cmds[0]["ox"], "jump_x": cmds[j]["ox"] if j is not None else None,
         "jump_to_face": (FACE_X - cmds[j]["ox"]) if j is not None else None,
         "max_x": xmax, "closest_gap_to_face": FACE_X - (xmax + 16.0),
         "first_land_t": r(cmds[land]["t"] - t0) if land is not None and t0 else None,
         "rel_t": r(cmds[rel]["t"] - t0) if rel is not None and t0 else None,
         "contact": k is not None, "wr_frames": sum(1 for s in T["states"] if s.get("wr")),
         "trav_frames": sum(1 for s in T["states"] if s.get("trav")), "hang_frames": sum(1 for s in T["states"] if s.get("hang")),
         "state_lines": len(T["states"]), "sv_evt": sorted({e["evt"] for e in T["sv_evt"]})}
    R["valid"] = bool(R["contact"] or R["wr_frames"] or R["trav_frames"])
    return R


def report_round2(rows, metas):
    P("\n" + "=" * 100)
    P("4c. ROUND 2 (a2r_* sessions): validity check")
    P("=" * 100)
    for m in metas:
        P(f"  {m['session']}: label {m['label']} scored {m['scored']}/{m['trials_total']} trial start origins {m['trial_origins']}")
    out = {"per_schedule": {}}
    for sch in sorted({x["schedule"] for x in rows}):
        xs = [x for x in rows if x["schedule"] == sch]
        d = {"n": len(xs), "valid": sum(x["valid"] for x in xs), "start_x": st([x["start_x"] for x in xs]),
             "jump_x": st([x["jump_x"] for x in xs]), "jump_to_face": st([x["jump_to_face"] for x in xs]),
             "max_x": st([x["max_x"] for x in xs]), "closest_gap_to_face": st([x["closest_gap_to_face"] for x in xs]),
             "first_land_t": st([x["first_land_t"] for x in xs]), "rel_t": st([x["rel_t"] for x in xs]),
             "wr_frames": sum(x["wr_frames"] for x in xs), "trav_frames": sum(x["trav_frames"] for x in xs),
             "sv_evt": sorted({e for x in xs for e in x["sv_evt"]})}
        out["per_schedule"][sch] = d
        P(f"  H{xs[0]['H']} {sch:<17} n={d['n']} reached the face {d['valid']}/{d['n']}; start x {fmt(d['start_x'], 1)}; jump x "
          f"{fmt(d['jump_x'], 1)} ({fmt(d['jump_to_face'], 1)} u before the face; round 1: ~100); landed {fmt(d['first_land_t'])} s "
          f"after the jump; W released {fmt(d['rel_t'])} s; max x {fmt(d['max_x'], 1)} (closest gap {fmt(d['closest_gap_to_face'], 1)} u); "
          f"wr frames {d['wr_frames']} trav frames {d['trav_frames']}; dedi events {d['sv_evt']}")
    nv = sum(x["valid"] for x in rows)
    out["valid_trials"], out["n"] = nv, len(rows)
    out["verdict"] = ("no round-2 trial touched the face: the a2r_* trials started at the runner default origin instead of "
                      f"lane A (x {LANE_A_X}), so every release / press happened on the floor far from the rock" if nv == 0
                      else f"{nv}/{len(rows)} trials reached the face")
    P(f"  VERDICT: {out['verdict']}.")
    out["params"] = [{"name": "round2_a2r_validity", "value": f"{nv}/{len(rows)} trials reached the face", "unit": "",
                      "label": "meas", "n": len(rows), "spread": None,
                      "note": "a2r_* schedules have no SCHEDULE_ORIGIN_PREFIX entry (only 'a2_' maps to lane A); no round-2 "
                              "parameter could be measured; round-1 values stand"}]
    out["trials"] = rows
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json", default=None)
    ap.add_argument("--params", default=None)
    a = ap.parse_args(argv)
    H_rows, SG_rows, sess_meta, R2_rows = [], [], [], []
    for folder in a.sessions:
        S = L.load(folder)
        lab = S["runner"].get("label", S["folder"])
        fps = S["runner"].get("client_fps") or 120.0
        n_all = len(S["runner"]["trials"])
        rej = [(t["run"], t["schedule"], t.get("why")) for t in S["runner"]["trials"] if not t.get("ok") and not t.get("warmup")]
        meta = {"session": S["folder"], "label": lab, "client_fps": fps, "trials_total": n_all, "scored": len(S["trials"]),
                "rejected": rej, "warmup": [t["run"] for t in S["runner"]["trials"] if t.get("warmup")],
                "both_cvars": S["runner"].get("both_cvars"), "geometry_wall_z": S["runner"].get("geometry_wall_z"),
                "mb_lines": {k: v for k, v in S["mb_tags"].items() if v}, "state_lines": sum(len(t["states"]) for t in S["trials"])}
        mh = re.search(r"_h(\d+)$", lab)
        if "_A2r_" in lab:                       # round-2 sessions (optional arguments; absent -> round-1 output unchanged)
            meta["kind"], meta["H"] = "round2", int(mh.group(1)) if mh else None
            origins = {tuple(t["origin"]) for t in S["runner"]["trials"]}
            meta["trial_origins"] = sorted(origins)
            for T in S["trials"]:
                R = round2_trial(T, fps)
                R["session"], R["H"] = S["folder"], meta["H"]
                R2_rows.append(R)
        elif mh:
            meta["kind"], meta["H"] = "height", int(mh.group(1))
            for T in S["trials"]:
                if T["schedule"].startswith("a2_"):
                    R = height_trial(T, meta["H"], fps)
                    R["_T"] = {"cmds": T["cmds"]}          # kept for the climb re-simulation, dropped before JSON
                    R["session"] = S["folder"]
                    R["repeat_check"] = not lab.startswith("M6_A2b")
                    H_rows.append(R)
        elif "_sg_" in lab:
            meta["kind"] = "superglide"
            on = (S["runner"].get("both_cvars") or {}).get("mantle_boost_enabled", "1") != "0"
            meta["fsm_on"] = on
            for T in S["trials"]:
                if T["schedule"].startswith("e7_"):
                    R = sg_trial(T, fps, on)
                    R["session"] = S["folder"]
                    SG_rows.append(R)
        sess_meta.append(meta)
        del S

    # ------------------------------------------------------------------ print: sessions
    P("M6-A2 climb / ledge / mantle / superglide analysis")
    P("=" * 100)
    for m in sess_meta:
        P(f"{m['session']}: label {m['label']} kind {m.get('kind')} H {m.get('H')} fps {m['client_fps']} scored "
          f"{m['scored']}/{m['trials_total']} warmup {m['warmup']} rejected {m['rejected']} both_cvars {m['both_cvars']} "
          f"wall_z {m['geometry_wall_z']} MB lines {m['mb_lines']} state lines {m['state_lines']}")
    joinbad = [(x["session"][-12:], x["run"], x["join"]) for x in H_rows + SG_rows
               if x["join"]["cmds"] - x["join"]["joined"] > 8 or x["join"]["bad_state"] > 0]
    P(f"join: trials with > 8 unjoined cmds or bad-state joins: {joinbad if joinbad else 'none'}")

    main_rows = [x for x in H_rows if not x["repeat_check"]]
    # ------------------------------------------------------------------ print: per trial (heights)
    P("\n" + "=" * 100)
    P("1. LEDGE HEIGHTS: per trial (t relative to the climb-jump usercmd; walk: first W usercmd)")
    P("=" * 100)
    for x in H_rows:
        cl, tv = x.get("climb"), x.get("trav")
        s = (f"H{x['H']:>3} r{x['run']} {x['schedule']:<11} {'[repeat] ' if x['repeat_check'] else ''}{x['outcome']:<28}"
             f" wr {x['seg_wr']} trav {x['seg_trav']} hang {len(x['seg_hang'])}")
        P(s)
        if cl:
            P(f"     climb: contact t {x.get('contact_t')} z {r(cl['contact_post_z'], 2)} (pre vz {r(cl['contact_pre_vz'], 1)}) "
              f"end {cl.get('end_kind')} dur {r(cl.get('duration'))} s z_end {r(cl.get('end_pre_z'), 2)} gain {r(cl.get('gain_from_contact'), 2)} "
              f"vz_end {r(cl.get('end_vz_pre'), 2)} peak {r(cl.get('peak_vz'), 1)} k {r(cl.get('line_k'), 4)} Z0 {r(cl.get('line_Z0'), 2)}"
              + (f" final dvz {r(cl['final_dvz'], 2)} post vx {r(cl['final_post_vx'], 2)}" if cl.get("final_dvz") else ""))
        if tv:
            P(f"     trav: start t {tv.get('start_t')} z {r(tv['start_z'], 2)} vz {r(tv['start_vz'], 1)} -> exit x {r(tv['exit_x'], 1)} "
              f"z {r(tv['exit_z'], 2)} dur {r(tv['duration'])} rise {r(tv['rise'], 2)} exit pre {tuple(r(v, 2) for v in tv['exit_pre'])} "
              f"post h {r(tv['exit_post_h'], 2)} completed {tv['completed']} peak z {r(tv['peak_z'], 2)} "
              f"W release rel start {r(tv.get('t_w_release_rel_start'))} x back {r(tv.get('x_back_after_max'), 2)}")
        if x.get("release_on_wall"):
            w = x["release_on_wall"]
            P(f"     W released on the wall: t after contact {r(w['t_rel_after_contact'])} vz {r(w['rel_vz'], 2)} first dvz/dt "
              f"{r(w['first_dvz_dt'], 1)} t to vz<=0 {w['t_to_vz0']} z top {w['z_top']} rising decel {fmt(w.get('decel_rising'), 1)} "
              f"falling accel {fmt(w['accel_falling'], 1)} detach after rel {r(w.get('detach_t_after_rel'))} "
              f"(after contact {r(w.get('detach_t_after_contact'))}) z {r(w.get('detach_z'), 2)} dvx {r(w.get('detach_dvx'), 2)} "
              f"post {tuple(r(v, 2) for v in w.get('detach_post', ()))}")
        if x.get("press"):
            p = x["press"]
            P(f"     press {p['kind']} at t {p.get('t')} on {p['on']} z {r(p['z'], 2)} state {p['state']} pre "
              f"{tuple(r(v, 2) for v in p['pre'])} post {tuple(r(v, 2) for v in p['post'])} V {r(p.get('V'), 2)} "
              f"0.1 s later {tuple(r(v, 2) for v in p['post_0p1s'])}")
        if x["schedule"] == "a2_walk":
            P(f"     walk: stop x {r(x.get('walk_stop_x'), 2)} wr segments {x['walk_wr_segments']} ({x['walk_wr_frames']} frames) "
              f"max rise {r(x['walk_max_rise'], 2)}")
        if x.get("first_land_z") and x["outcome"].startswith("land_on_top"):
            P(f"     landed on top at z {r(x['first_land_z'], 2)} t {x.get('first_land_t')}")
        if x["wr_segments_after_first"]:
            P(f"     later climb segments: {x['wr_segments_after_first']}")
        if x["mb"]:
            P(f"     MB lines: {len(x['mb'])}: " + " | ".join(m[:90] for m in x["mb"][:4]))

    HS = summarise_heights(main_rows)
    REP = summarise_heights([x for x in H_rows if x["repeat_check"]])
    # ------------------------------------------------------------------ summary tables
    P("\n" + "=" * 100)
    P("2. LEDGE HEIGHTS: summary (A2b sessions only)")
    P("=" * 100)
    for H, D in HS.items():
        P(f"\n--- H = {H} (nominal; floor {FLOOR})")
        for sch, d in D.items():
            P(f"  {sch:<11} n={d['n']} outcomes {d['outcomes']} ledge z {fmt(d['ledge_z'], 2)}")
            if "climb_duration" in d:
                P(f"     climb dur {fmt(d['climb_duration'])}  gain {fmt(d['climb_gain_from_contact'], 2)}  z_end {fmt(d['climb_end_pre_z'], 2)}"
                  f"  end kinds {d['climb_end_kinds']}")
                P(f"     contact z {fmt(d['climb_contact_post_z'], 2)}  peak vz {fmt(d['climb_peak_vz'], 2)}  k {fmt(d['climb_line_k'], 4)}"
                  f"  Z0 {fmt(d['climb_line_Z0'], 2)}  final dvz {fmt(d['climb_final_dvz'], 2)}  final vx {fmt(d['climb_final_post_vx'], 2)}")
                P(f"     per-step decay rate -dvz/dt/vz {fmt(d['climb_decay_rate_step'], 4)}  accel phase {fmt(d['climb_accel_mean'], 1)}")
            if "trav_duration" in d:
                P(f"     trav dur {fmt(d['trav_duration'])}  start z {fmt(d['trav_start_z'], 2)}  exit z {fmt(d['trav_exit_z'], 2)}"
                  f"  rise {fmt(d['trav_rise'], 2)}  ledge-start {fmt(d['trav_start_below_ledge'], 2)}  completed {d['trav_completed']}/{len(d['trav_exit_pre'])}")
                P(f"     exit pre-vel {sorted(set(d['trav_exit_pre']))}  exit post h {fmt(d['trav_exit_post_h'], 2)}")
            if "rel_t_rel_after_contact" in d:
                P(f"     W release on wall: after contact {fmt(d['rel_t_rel_after_contact'])} vz {fmt(d['rel_rel_vz'], 2)} first dvz/dt "
                  f"{fmt(d['rel_first_dvz_dt'], 1)} rising decel {fmt(d['rel_decel_rising'], 1)} t->vz0 {fmt(d['rel_t_to_vz0'])} z top {fmt(d['rel_z_top'], 2)}")
                P(f"        falling accel {fmt(d['rel_accel_falling'], 1)} (dedi {fmt(d['rel_sv_accel_falling'], 1)}) detach after rel {fmt(d['rel_detach_t_after_rel'])} "
                  f"after contact {fmt(d['rel_detach_t_after_contact'])} z {fmt(d['rel_detach_z'], 2)} dvx {fmt(d['rel_detach_dvx'], 2)}")
            if "press_on" in d:
                P(f"     press on {d['press_on']} at t {fmt(d['press_t'])} post {sorted(set(d['press_post']))} V {fmt(d['press_V'], 2)}")
            if sch == "a2_walk":
                P(f"     walk wr segments {d['walk_wr_segments']} max rise {fmt(d['walk_max_rise'], 2)} stop x {fmt(d['walk_stop_x'], 2)}")
    if REP:
        P("\n--- repeatability (older session without state log)")
        for H, D in REP.items():
            for sch, d in D.items():
                if "climb_duration" in d:
                    P(f"  H{H} {sch} n={d['n']} outcomes {d['outcomes']} climb dur {fmt(d['climb_duration'])} z_end {fmt(d['climb_end_pre_z'], 2)}"
                      f" k {fmt(d['climb_line_k'], 4)} Z0 {fmt(d['climb_line_Z0'], 2)}"
                      + (f" trav dur {fmt(d['trav_duration'])} exit z {fmt(d['trav_exit_z'], 2)}" if "trav_duration" in d else ""))

    # ------------------------------------------------------------------ anchors: ledge vs floor
    P("\n" + "=" * 100)
    P("3. CLIMB ANCHOR TEST (M3 open question 3)")
    P("=" * 100)
    full = [x for x in main_rows if x["schedule"] == "a2_climb" and x.get("climb") and x["climb"].get("end_kind") == "final_jump"]
    anchor = {}
    for H in sorted({x["H"] for x in full}):
        xs = [x["climb"] for x in full if x["H"] == H]
        ledge = HS[str(H)]["a2_climb"]["ledge_z"].get("mean") if str(H) in HS else None
        zend = st([c["end_pre_z"] for c in xs])
        Z0 = st([c.get("line_Z0") for c in xs])
        anchor[str(H)] = {"n": len(xs), "z_end": zend, "Z0": Z0, "ledge_z": ledge,
                          "z_end_minus_floor": zend["mean"] - FLOOR,
                          "ledge_minus_z_end": (ledge - zend["mean"]) if ledge else None,
                          "duration": st([c["duration"] for c in xs])}
        P(f"  H{H}: full climbs (end = final jump-up) n={len(xs)} z_end {fmt(zend, 3)} Z0 {fmt(Z0, 2)} floor+{zend['mean'] - FLOOR:.2f} "
          f"ledge {r(ledge, 2)} ledge - z_end {r((ledge - zend['mean']) if ledge else None, 2)}")
    allz = [x["climb"]["end_pre_z"] for x in full]
    allZ0 = [x["climb"].get("line_Z0") for x in full]
    P(f"  pooled over heights: z_end {fmt(st(allz), 3)}  Z0 {fmt(st(allZ0), 2)}  (M3 H=232: z_end bracket (441.913, 441.934], Z0 475.33)")
    # bracket of the absolute end threshold: last climb cmd pre-z < Z_end <= end cmd pre-z
    lo = max(x["climb"]["prev_pre_z"] for x in full) if full else None
    hi = min(x["climb"]["end_pre_z"] for x in full) if full else None
    P(f"  absolute end-height bracket over all full climbs: ({r(lo, 3)}, {r(hi, 3)}] -> consistent {lo is not None and lo < hi}")
    anchor["bracket"] = (lo, hi)

    # mantle trigger reach
    P("\n  Mantle trigger: origin z at traversal start vs the ledge (completed traversals, a2_climb):")
    reach = []
    for H, D in HS.items():
        d = D.get("a2_climb", {})
        if "trav_start_below_ledge" in d and d["trav_start_below_ledge"].get("n"):
            P(f"    H{H}: ledge - start z {fmt(d['trav_start_below_ledge'], 2)}  trav dur {fmt(d['trav_duration'])}  outcomes {d['outcomes']}")
            reach.append((int(H), d["trav_start_below_ledge"]["mean"], d["trav_duration"]["mean"]))
    tr = [(x["trav"]["exit_z"] - x["trav"]["start_z"], x["trav"]["duration"]) for x in main_rows
          if x.get("trav") and x["trav"]["completed"] and x["trav"]["duration"] and x["schedule"] in ("a2_climb",)
          and not (x["trav"].get("t_w_release_rel_start") is not None)]
    fit_rt = None
    if len(tr) > 3:
        m_, b_, rms_ = lin_fit([a for a, _ in tr], [b for _, b in tr])
        fit_rt = {"slope_s_per_u": m_, "intercept_s": b_, "rms": rms_, "n": len(tr)}
        P(f"  traversal duration vs rise (a2_climb, W held): dur = {b_:.4f} + {m_:.5f}*rise  rms {rms_:.4f} n={len(tr)}")
        P("   (per point: " + ", ".join(f"{a:.1f}u/{b:.3f}s" for a, b in sorted(set((round(a, 1), round(b, 3)) for a, b in tr))) + ")")

    # on-wall mantle trigger bracket: start gap <= R < gap of the previous climb usercmd
    wall = []
    for x in main_rows:
        cl, tv = x.get("climb"), x.get("trav")
        if not (cl and tv and tv["completed"] and cl.get("end_kind") == "traversal" and cl.get("climb_cmds", 0) > 3):
            continue                      # only climbs that reached the trigger while on the wall (not at contact)
        wall.append((x["H"], tv["exit_z"] - tv["start_z"], tv["exit_z"] - x["_prev_poz"] if x.get("_prev_poz") else None))
    if wall:
        lo_r = max(w[1] for w in wall)
        hi_r = min(w[2] for w in wall if w[2] is not None)
        P(f"  on-wall mantle trigger reach bracket (ledge - origin z): ({lo_r:.2f} observed max at trigger, "
          f"{hi_r:.2f} min not triggered one usercmd earlier]; n={len(wall)} -> consistent {lo_r < hi_r}")
        anchor["reach_bracket"] = (lo_r, hi_r)
    air = [x["trav"]["exit_z"] - x["trav"]["start_z"] for x in main_rows
           if x.get("trav") and x["trav"]["completed"] and x.get("climb") and x["climb"].get("end_kind") == "final_jump"]
    if air:
        P(f"  after the final jump-up (in the air): ledge - start z {fmt(st(air), 2)}")
        anchor["reach_air"] = st(air)
    # first post-exit usercmd speed (W held, completed traversals)
    ex = [x["trav"]["exit_post_h"] for x in main_rows if x.get("trav") and x["trav"]["completed"] and x["trav"]["exit_pre_h"] > 250]
    n299 = sum(1 for v in ex if abs(v - 299.0) < 0.05)
    P(f"  first usercmd after a completed traversal (W held): post h = 299.00 in {n299}/{len(ex)}; others "
      f"{fmt(st([v for v in ex if abs(v - 299.0) >= 0.05]), 2)}")
    anchor["exit_post_h_299"] = (n299, len(ex))

    # W released inside the traversal
    P("\n  W released during the traversal (a2_hang / a2_cancel / a2_hop / a2_hop_back):")
    ledge_by_H = {int(H): D.get("a2_climb", {}).get("ledge_z", {}).get("mean") for H, D in HS.items()}
    relt = []
    for x in main_rows:
        tv = x.get("trav")
        if not tv or tv.get("t_w_release_rel_start") is None:
            continue
        ledge = ledge_by_H.get(x["H"])
        if not ledge:
            continue
        exp = fit_rt["intercept_s"] + fit_rt["slope_s_per_u"] * (ledge - tv["start_z"]) if fit_rt else T_TRAV_NORMAL
        q = {"H": x["H"], "run": x["run"], "rel": tv["t_w_release_rel_start"], "exp_dur": exp,
             "frac": tv["t_w_release_rel_start"] / exp, "completed": tv["completed"], "dur": tv["duration"],
             "reverse_s": (tv["duration"] - tv["t_w_release_rel_start"]) if not tv["completed"] else None,
             "peak_z": tv["peak_z"], "exit_z": tv["exit_z"], "start_z": tv["start_z"], "exit_x": tv["exit_x"],
             "x_back": tv.get("x_back_after_max"), "exit_pre": tv["exit_pre"]}
        relt.append(q)
        x["trav"]["release_frac"] = q["frac"]
    for H in sorted({q["H"] for q in relt}):
        qs = [q for q in relt if q["H"] == H]
        P(f"    H{H}: n={len(qs)} release {fmt(st([q['rel'] for q in qs]))} s after start, frac of expected duration "
          f"{fmt(st([q['frac'] for q in qs]))}; completed {sum(q['completed'] for q in qs)}/{len(qs)}; exit v "
          f"{sorted(set(tuple(r(v, 1) for v in q['exit_pre']) for q in qs))}")
        ab = [q for q in qs if not q["completed"]]
        if ab:
            P(f"       aborted: peak z {fmt(st([q['peak_z'] for q in ab]), 2)} (ledge {ledge_by_H.get(H)}), reverse phase "
              f"{fmt(st([q['reverse_s'] for q in ab]))} s, drop from x {fmt(st([q['exit_x'] for q in ab]), 2)} z "
              f"{fmt(st([q['exit_z'] for q in ab]), 2)} (start z {fmt(st([q['start_z'] for q in ab]), 2)}), x moved back "
              f"{fmt(st([q['x_back'] for q in ab]), 2)} u")
    comp = [q["frac"] for q in relt if q["completed"]]
    abo = [q["frac"] for q in relt if not q["completed"]]
    if comp and abo:
        P(f"    cancel threshold bracket (release frac): ({max(abo):.3f} aborted, {min(comp):.3f} completed]; in s after "
          f"start: ({max(q['rel'] for q in relt if not q['completed']):.3f}, {min(q['rel'] for q in relt if q['completed']):.3f}]")
        anchor["cancel_bracket_frac"] = (max(abo), min(comp))
        anchor["cancel_bracket_s"] = (max(q['rel'] for q in relt if not q['completed']), min(q['rel'] for q in relt if q['completed']))
    anchor["release_in_traversal"] = relt
    # parity outliers
    P(f"\n  client/dedi parity over whole trials (A2b): max |dv| {fmt(st([x['parity']['max_vel'] for x in main_rows]), 3)}; "
      f"max |dpos| {fmt(st([x['parity']['max_pos'] for x in main_rows]), 3)}")
    P("  trials with a usercmd |dv| > 1 (worst usercmd: t in trial, x, z, ground cl/sv, client post v vs dedi post v):")
    for x in main_rows:
        p = x["parity"]
        if p["max_vel"] <= 1.0 and p["max_pos"] <= 0.5:
            continue
        w = p["worst"]
        P(f"    H{x['H']} r{x['run']} {x['schedule']:<11} {x['outcome']:<24} max dv {p['max_vel']:.3f} dpos {p['max_pos']:.3f} "
          f"n(dv>1) {p['cmds_dv_gt1']}: t {w['t_in_trial']} x {w['x']:.1f} z {w['z']:.2f} g {w['ground']} cl "
          f"{tuple(r(v, 2) for v in w['cl_post'])} sv {tuple(r(v, 2) for v in w['sv_post'])}")

    # ------------------------------------------------------------------ superglide
    P("\n" + "=" * 100)
    P("4. SUPERGLIDE / MANTLE BOOST (press N frames after the climb jump; frames before end: 1 = last traversal frame)")
    P("=" * 100)
    for x in SG_rows:
        tv = x.get("trav") or {}
        P(f"{'ON ' if x['fsm_on'] else 'OFF'} r{x['run']} {x['schedule']:<12} class {x['class']:<20} presses {x['press_frame_offsets']} "
          f"ducks {x['duck_frame_offsets']} press-end frames {r(x.get('press_frames_before_end'), 1)} press rel start {r(x.get('press_rel_trav_start'))}"
          f" trav dur {r(x.get('trav_duration'))} exit x {r(x.get('exit_x'), 1)} z {r(x.get('exit_z'), 2)} g{x.get('exit_ground')} d{x.get('exit_duck')}")
        P(f"      exit pre h {r(x.get('exit_pre_h'), 3)} vz {r(x.get('exit_pre_vz'), 3)} post h {r(x.get('exit_post_h'), 3)} vz {r(x.get('exit_post_vz'), 3)}"
          f" V {r(x.get('exit_V'), 2)} sv pre {tuple(r(v, 3) for v in x['sv_exit_pre']) if x.get('sv_exit_pre') else None} parity exit "
          f"{r(x['parity_exit']['max_diff'], 3) if x.get('parity_exit') else None} all {x.get('parity_all')}")
        if x.get("mb_trig") or x.get("mb_apply"):
            P(f"      MB trig {[(t['side'], t['anim'], t['delta'], t['gate'], t['result']) for t in x['mb_trig']]} apply "
              f"{[(a_['side'], a_['state'], a_['speed'], a_['vel']) for a_ in x['mb_apply']]} mismatch {x['mb_cl_sv_mismatch']}")
        if x.get("jump_on_top"):
            P(f"      jump on top: {x['jump_on_top']}")
        if x.get("lurch"):
            lu = x["lurch"]
            P(f"      moveright press {lu['press_cmds_after_exit']} cmds after exit, t {r(lu['t_since_exit_jump'])} s since the exit jump; "
              f"pre {tuple(r(v, 3) for v in lu['pre'])} post {tuple(r(v, 3) for v in lu['post'])} dv {tuple(r(v, 3) for v in lu['dv'])} "
              f"pred lurch dv {tuple(r(v, 2) for v in lu['pred_dv']) if lu['pred_dv'] else None} sv post {lu['sv_post']}")
    # summary by group
    P("\n  Summary by (FSM, variant, N):")
    SGS = {}
    for x in SG_rows:
        key = f"{'on' if x['fsm_on'] else 'off'}|{x['variant']}|{x['N']}"
        SGS.setdefault(key, []).append(x)
    SGsum = {}
    for key, xs in sorted(SGS.items(), key=lambda kv: (kv[0].split('|')[0], kv[0].split('|')[1], int(kv[0].split('|')[2]))):
        cls = {}
        for x in xs:
            cls[x["class"]] = cls.get(x["class"], 0) + 1
        d = {"n": len(xs), "classes": cls, "exit_pre_h": st([x.get("exit_pre_h") for x in xs]),
             "exit_pre_vz": st([x.get("exit_pre_vz") for x in xs]), "exit_V": st([x.get("exit_V") for x in xs]),
             "press_frames_before_end": st([x.get("press_frames_before_end") for x in xs]),
             "press_rel_trav_start": st([x.get("press_rel_trav_start") for x in xs]),
             "trav_duration": st([x.get("trav_duration") for x in xs]),
             "exit_x": st([x.get("exit_x") for x in xs]), "exit_z": st([x.get("exit_z") for x in xs]),
             "parity_exit": st([x["parity_exit"]["max_diff"] for x in xs if x.get("parity_exit")]),
             "sv_exit_pre_h": st([math.hypot(x["sv_exit_pre"][0], x["sv_exit_pre"][1]) for x in xs if x.get("sv_exit_pre")]),
             "mb_mismatch": sum(1 for x in xs if x.get("mb_cl_sv_mismatch"))}
        SGsum[key] = d
        P(f"  {key:<14} n={d['n']} {d['classes']} exit h {fmt(d['exit_pre_h'], 3)} vz {fmt(d['exit_pre_vz'], 3)} sv h {fmt(d['sv_exit_pre_h'], 3)}")
        P(f"                 press-end frames {fmt(d['press_frames_before_end'], 1)} trav dur {fmt(d['trav_duration'])} exit x {fmt(d['exit_x'], 2)} "
          f"z {fmt(d['exit_z'], 2)} parity exit {fmt(d['parity_exit'], 3)} MB cl/sv mismatch {d['mb_mismatch']}")
    # class vs press timing (FSM off)
    off = [x for x in SG_rows if not x["fsm_on"] and x.get("press_frames_before_end") is not None]
    if off:
        P("\n  FSM off: class vs press timing (frames before the end of a normal traversal are not known per trial; "
          "press rel traversal start used):")
        for cname in sorted({x["class"] for x in off}):
            xs = [x for x in off if x["class"] == cname]
            P(f"    {cname:<22} n={len(xs)} press rel start {fmt(st([x['press_rel_trav_start'] for x in xs]))} press z "
              f"{fmt(st([x.get('press_z') for x in xs]), 2)} rise frac {fmt(st([x.get('press_rise_frac') for x in xs]))} press x "
              f"{fmt(st([x.get('press_x') for x in xs]), 2)} variants {sorted({x['variant'] for x in xs})} N {sorted({x['N'] for x in xs})}")
        P("    per trial (N, variant, press rel start, press z, rise frac, class):")
        for x in sorted(off, key=lambda x: (x["N"], x["variant"], x["run"])):
            P(f"      f{x['N']} {x['variant']} r{x['run']} {x['press_rel_trav_start']:.3f} s z {x['press_z']:.2f} frac "
              f"{x['press_rise_frac']:.3f} x {x['press_x']:.1f} snap {tuple(r(v, 1) for v in x['press_frame_snap'])} "
              f"-> {x['class']} (exit h {x['exit_pre_h']:.3f} vz {x['exit_pre_vz']:.3f}, "
              f"duck on exit cmd {x['exit_duck']}, buttons {x['exit_buttons']:x})")
        # what follows a native superglide: speed over the next 0.5 s
    sgx = [x for x in SG_rows if x["class"] == "superglide_native"]
    if sgx:
        P(f"  native superglide exit: h {fmt(st([x['exit_pre_h'] for x in sgx]), 3)} vz {fmt(st([x['exit_pre_vz'] for x in sgx]), 3)} "
          f"V(native: post vz + 1.5*g*dt) {fmt(st([x['exit_V'] for x in sgx]), 2)} dedi h {fmt(st([math.hypot(*x['sv_exit_pre'][:2]) for x in sgx]), 3)}")
    po = [(x["run"], x["schedule"], r(x["parity_exit"]["max_diff"], 3), x["parity_all"]) for x in SG_rows
          if x.get("parity_exit") and x["parity_exit"]["max_diff"] > 0.1]
    P(f"  superglide-session parity: exit-window max |cl - sv| {fmt(st([x['parity_exit']['max_diff'] for x in SG_rows if x.get('parity_exit')]), 3)}; "
      f"> 0.1: {po if po else 'none'}")
    P(f"  whole-trial parity max |dv| {fmt(st([x['parity_all']['max_vel'] for x in SG_rows if x.get('parity_all')]), 3)} max |dpos| "
      f"{fmt(st([x['parity_all']['max_pos'] for x in SG_rows if x.get('parity_all')]), 3)}")
    res = {"sessions": sess_meta, "height_trials": H_rows, "height_summary": HS, "repeat_summary": REP, "anchor": anchor,
           "trav_rise_fit": fit_rt, "superglide_trials": SG_rows, "superglide_summary": SGsum}
    # climb re-simulation residuals (W-held climbs: a2_climb all heights with a climb, and the pre-release part is skipped)
    P("\n" + "=" * 100)
    P("4b. CLIMB MODEL RESIDUALS (re-simulation from the contact usercmd, pooled constants of this data set)")
    P("=" * 100)
    held = [x["climb"] for x in main_rows if x.get("climb") and x["climb"].get("line_k") and
            x["climb"].get("end_kind") in ("final_jump", "traversal")]
    kk = st([c["line_k"] for c in held]).get("mean")
    Z0 = st([c["line_Z0"] for c in held]).get("mean")
    lo, hi = anchor.get("bracket", (None, None))
    Zend = (lo + hi) / 2 if lo else M3["climb_end_z"]
    resid = {}
    for label, kv, z0v in (("this data (line fit)", kk, Z0), ("M3 constants", M3["climb_k"], M3["climb_Z0"])):
        rs = []
        for x in H_rows:
            if x["schedule"] != "a2_climb" or not x.get("climb") or x["climb"].get("end_kind") not in ("final_jump", "traversal"):
                continue
            if x["climb"].get("climb_cmds", 0) <= 3:
                continue
            q = climb_residuals(x["_T"], x, 120.0, kv, z0v, Zend)
            if q:
                q.update(H=x["H"], run=x["run"], repeat=x["repeat_check"])
                rs.append(q)
        resid[label] = {"k": kv, "Z0": z0v, "Zend": Zend, "n": len(rs),
                        "max_abs_vz_err": st([q["max_abs_vz_err"] for q in rs]), "rms_vz_err": st([q["rms_vz_err"] for q in rs]),
                        "end_cmd_offsets": sorted({q["end_cmd_offset"] for q in rs if q["end_cmd_offset"] is not None}),
                        "per_H_max": {str(H): max(q["max_abs_vz_err"] for q in rs if q["H"] == H) for H in sorted({q["H"] for q in rs})}}
        P(f"  {label}: k {kv:.4f} Z0 {z0v:.2f} Z_end {Zend:.3f} accel 490; n={len(rs)} climbs; max |vz err| per climb "
          f"{fmt(resid[label]['max_abs_vz_err'], 2)}; rms {fmt(resid[label]['rms_vz_err'], 2)}; final jump-up usercmd offset "
          f"{resid[label]['end_cmd_offsets']}; worst per H {resid[label]['per_H_max']}")
    res["climb_resim"] = resid
    for x in H_rows:
        x.pop("_T", None)
    params = build_params(main_rows, HS, anchor, fit_rt, SG_rows, SGsum)
    if R2_rows:
        res["round2"] = report_round2(R2_rows, [m for m in sess_meta if m.get("kind") == "round2"])
        params.extend(res["round2"]["params"])
    P("\n" + "=" * 100)
    P("5. PARAMETERS (label: meas = read from usercmds, fit = formula fitted to usercmds, src = source/census, "
      "unknown, design-needed)")
    P("=" * 100)
    for p in params:
        v = p["value"]
        vs = f"{v:.4f}" if isinstance(v, float) else str(v)
        P(f"  [{p['label']}] {p['name']} = {vs} {p.get('unit', '')}  (n={p.get('n')}, spread {p.get('spread')})  {p.get('note', '')}")
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(params, fh, indent=1)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=lambda o: None)
    return res


if __name__ == "__main__":
    main(sys.argv[1:])
