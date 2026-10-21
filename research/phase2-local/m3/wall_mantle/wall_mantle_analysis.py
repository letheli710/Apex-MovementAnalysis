#!/usr/bin/env python3
"""M3 wall / mantle / landing-chain analysis (E6 climb + wall bounce, E7 mantle boost / superglide, E8 chains).

    python wall_mantle_analysis.py <session folder> [<session folder> ...] [--json results.json]
                                   [--rejected]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). Only trials with
ok=true and warmup=false are scored. With --rejected, E7 trials that the runner rejected (frame rate
outside +/-3 %) are listed separately as supplementary evidence; they never enter a fitted value.

Physics truth = client first-time MOVE-TRACE usercmds (aj_load.join gives dt per command). Dedi MOVE-TRACE
rows of the same usercmd give parity. Dedi HSD events give JUMP / MANTLE / wallrun edges. [MB-TRIG] /
[MB-APPLY] lines (SDK mantle_boost.cpp) are read from the raw client and server message logs and are
assigned to a trial by game time (client frame t range of the trial; client and dedi print the same
curTime for the same usercmd).

stdlib only; no local paths (session folders come from the command line). Nothing is tuned to pass.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m2", "air_jump")))
import aj_load as L  # noqa: E402

IN_JUMP, IN_DUCK = 0x2, 0x4
G = 750.0
WALL_N = (-1.0, 0.0)          # rock face normal (outward), from the spawn geometry: face at x ~ -13706, normal -X
AIR_ACCEL, AIR_WISH = 500.0, 60.0 * 1.15
CENSUS = {"wallrunJumpOutwardSpeed": 188.0, "wallrunJumpUpSpeed": 240.0, "wallrunJumpInputDirSpeed": 75.0,
          "climbHeight": 100.0, "climbSpeedStart": 200.0, "climbFinalJumpUpHeight": 28.0,
          "landSlowdownDuration": 1.0, "jumpHeight": 56.0, "sprint_cap": 299.0,
          "mantle_boost_mult": 1.3, "mantle_boost_jump_h": 90.0, "mantle_fail_jump_h": 56.0}
MB_RE = re.compile(r"\[(MB-TRIG|MB-APPLY)\]\s*(.*)$")


# ----------------------------------------------------------------------------- small helpers
def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def st(vals):
    return L.stats([v for v in vals if v is not None])


def r(x, n=3):
    return None if x is None else round(x, n)


def lin_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    b = my - m * mx
    rms = math.sqrt(sum((y - m * x - b) ** 2 for x, y in zip(xs, ys)) / n)
    return m, b, rms


def edges(seq, key, bit=None):
    out = []
    for i in range(1, len(seq)):
        a = seq[i][key] & bit if bit else seq[i][key]
        b = seq[i - 1][key] & bit if bit else seq[i - 1][key]
        if a and not b:
            out.append(i)
    return out


def parse_mb(folder):
    """[MB-TRIG]/[MB-APPLY] lines of client and server message logs -> list of dicts."""
    out = []
    for side in ("client", "server"):
        for f in sorted(glob.glob(os.path.join(folder, "platform", "logs", side, "*", "message*.log"))):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    m = MB_RE.search(ln)
                    if not m:
                        continue
                    kv = dict(re.findall(r"(\w+)=(\([^)]*\)|\S+)", m.group(2)))
                    res = re.search(r"-> (\d)", m.group(2))
                    d = {"tag": m.group(1)[3:], "side": "cl" if side == "client" else "sv", "t": float(kv["t"])}
                    if d["tag"] == "TRIG":
                        d.update(anim=float(kv["anim"]), raw=float(kv["raw"]), delta=float(kv["delta"]),
                                 prev=float(kv["prev"]), thr=float(kv["thr"]), gate=kv["gate"],
                                 travState=int(kv["travState"]), result=int(res.group(1)) if res else None)
                    else:
                        v = [float(x) for x in kv["vel"].strip("()").split()]
                        d.update(state=int(kv["state"]), speed=float(kv["speed"]), pose=float(kv["pose"]),
                                 scale=float(kv["scale"]), vel=v)
                    out.append(d)
    return out


# ----------------------------------------------------------------------------- climb / mantle phases
def phases(cmds):
    """Split a wall trial into approach / contact / climb / end / mantle using client usercmds."""
    js = edges(cmds, "buttons", IN_JUMP)
    if not js:
        return None
    j = js[0]
    k = next((i for i in range(j + 1, len(cmds)) if cmds[i]["vx"] > 250 and cmds[i]["pvx"] < 50), None)
    if k is None:
        return None
    P = {"j": j, "k": k, "presses": js}
    e, kind = None, None
    for i in range(k + 1, len(cmds)):
        c = cmds[i]
        if c["cmd"] - cmds[i - 1]["cmd"] != 1:
            e, kind = i, "gap"
            break
        if c["pvz"] - c["vz"] > 100:          # climb end: climbFinalJumpUp (big vz step, small outward kick)
            e, kind = i, "final_jump"
            break
        if c["pvx"] < -50:                     # jump out of the climb (wall bounce)
            e, kind = i, "bounce"
            break
        if c["ground"] == 0:
            e, kind = i, "left"
            break
    P["e"], P["end_kind"] = e, kind
    gaps = [i for i in range(k + 1, len(cmds)) if cmds[i]["cmd"] - cmds[i - 1]["cmd"] != 1]
    P["gap"] = gaps[0] if gaps else None
    return P


def climb_metrics(cmds, P):
    j, k, e = P["j"], P["k"], P["e"]
    c0 = cmds[k]
    out = {"jump_x": cmds[j]["ox"], "jump_speed": hs(cmds[j], False),
           "t_air_to_contact": sum(cmds[i]["dt"] or 0 for i in range(j, k)),
           "contact_pre": {"x": c0["ox"], "z": c0["oz"], "vx": c0["vx"], "vz": c0["vz"]},
           "contact_post": {"x": c0["pox"], "z": c0["poz"], "vx": c0["pvx"], "vy": c0["pvy"], "vz": c0["pvz"]},
           "contact_dvz": c0["pvz"] - c0["vz"], "contact_dt": c0["dt"]}
    z0 = c0["poz"]
    cl = [cmds[i] for i in range(k + 1, e)] if e else []
    if len(cl) < 3:
        out["climb_cmds"] = len(cl)
        return out
    a =[(c["pvz"] - c["vz"]) / c["dt"] for c in cl if c["dt"]]
    ipk = max(range(len(cl)), key=lambda i: cl[i]["pvz"])
    acc = a[:max(ipk - 1, 1)]
    dec = [(c["pvz"] - c["vz"]) / c["dt"] / c["vz"] for c in cl[ipk + 1:] if c["dt"]]
    out["accel_first8"] = st(acc[:8])
    out["accel_after8"] = st(acc[8:])
    out["peak_vz"] = cl[ipk]["pvz"]
    out["peak_h"] = cl[ipk]["poz"] - z0
    out["peak_t"] = sum(c["dt"] for c in cl[:ipk + 1])
    out["decay_rate"] = st([-x for x in dec])                      # 1/s  (dvz/dt = -k vz  <=>  dvz/dh = -k)
    if len(cl) - ipk > 5:
        m, b, rms_ = lin_fit([c["poz"] for c in cl[ipk + 1:]], [c["pvz"] for c in cl[ipk + 1:]])
        out["decay_line"] = {"dvz_dz": m, "vz_at_contact_z": m * z0 + b, "zero_vz_abs_z": -b / m, "rms": rms_}
    out["vx_over_vz"] = st([c["pvx"] / c["pvz"] for c in cl if c["pvz"] > 30])
    out["climb_cmds"] = len(cl) + 1
    out["climb_time"] = sum(c["dt"] for c in cl) + (c0["dt"] or 0)
    if P["end_kind"] == "final_jump":
        f = cmds[e]
        out["end_abs_z"] = f["oz"]
        out["end_h"] = f["oz"] - z0
        out["end_vz_pre"] = f["vz"]
        out["final_dvz"] = f["pvz"] - f["vz"]
        out["final_post_vx"] = f["pvx"]
        out["final_post_vz"] = f["pvz"]
        out["final_dt"] = f["dt"]
        # V such that post vz = vz_pre + V - k*g*dt  (k unknown: report V for k = 0.5 and 1.5)
        out["final_V_half"] = f["pvz"] - f["vz"] + 0.5 * G * f["dt"]
        pr = cmds[e - 1]
        out["end_t_start"] = sum(cmds[i]["dt"] for i in range(k, e))          # time from contact cmd start to final cmd start
        out["prev_t_start"] = out["end_t_start"] - pr["dt"]
        out["prev_abs_z"] = pr["oz"]
        out["prev_vz_pre"] = pr["vz"]
    return out


def mantle_metrics(cmds, frames, P):
    g = P.get("gap")
    if g is None:
        return None
    last, first = cmds[g - 1], cmds[g]
    tf = [f for f in frames if last["t"] < f["t"] < first["t"]]
    return {"air_cmds_before": (g - 1) - P["e"] if P["end_kind"] == "final_jump" else None,
            "t_last_cmd": last["t"], "t_first_cmd": first["t"],
            "duration": first["t"] - last["t"],                 # traversal: no MOVE-TRACE commands
            "start_z": last["poz"], "start_vz": last["pvz"], "start_vx": last["pvx"],
            "exit_z": first["oz"], "rise": first["oz"] - last["poz"],
            "exit_v": (first["vx"], first["vy"], first["vz"]), "exit_speed": hs(first, False),
            "exit_ground": first["ground"], "frames": len(tf),
            "path": [(round(f["t"] - last["t"], 4), round(f["ox"], 2), round(f["oz"], 2)) for f in tf]}


# ----------------------------------------------------------------------------- wall bounce
def bounce_metrics(cmds, P, sched):
    p = P["e"]
    c, n1 = cmds[p], cmds[p + 1]
    d = {"dt": c["dt"], "fwd": c["fwd"], "side": c["sidemove"], "t_since_contact": sum(cmds[i]["dt"] for i in range(P["k"], p)),
         "pre": (c["vx"], c["vy"], c["vz"]), "post": (c["pvx"], c["pvy"], c["pvz"]),
         "next_post": (n1["pvx"], n1["pvy"], n1["pvz"])}
    dx, dy, dz = c["pvx"] - c["vx"], c["pvy"] - c["vy"], c["pvz"] - c["vz"]
    # in-command air acceleration along the held wish direction (only forward held matters here:
    # back / side already exceed the 69 u/s wish cap along their direction after the jump)
    accel = 0.0
    if c["fwd"] > 0 and c["pvx"] < AIR_WISH:
        accel = AIR_ACCEL * c["dt"]
    # outward = along the wall normal (-X): d_out = -dx; tangential (moveright at yaw 0 = -Y): d_tan = dy
    d.update(d_out=-dx, d_tan=dy, dvz=dz, air_accel_x=accel,
             d_out_jump=-(dx - accel), dvz_plus_1p5g=dz + 1.5 * G * c["dt"], dvz_plus_halfg=dz + 0.5 * G * c["dt"],
             next_dvx=n1["pvx"] - c["pvx"])
    d["input"] = ("none" if "none" in sched else "back" if "back" in sched else "side" if "side" in sched
                  else "fwd_held")
    return d


# ----------------------------------------------------------------------------- E8 chains
def landing_chain(cmds):
    """Landings: MOVE-TRACE 'ground' is the pre-move flag, so the landing usercmd is the last one with
    ground=0; it ends with vz = 0. The next command is the first ground move (friction / slide)."""
    out = {"landings": [], "jumps": []}
    for i in range(1, len(cmds)):
        a, c = cmds[i - 1], cmds[i]
        if c["cmd"] - a["cmd"] != 1:
            continue
        if a["ground"] == 0 and c["ground"] == 1 and a["vz"] < -1:   # a real landing (not the wall contact)
            ser = []
            t = 0.0
            for q in range(i - 1, min(i + 160, len(cmds))):
                x = cmds[q]
                if q >= i and x["ground"] == 0:
                    break
                t += x["dt"] or 0
                ser.append((round(t, 4), round(hs(x), 3), x["maxspeed"], x["slide"], x["duck"]))
            land = {"i": i - 1, "air_speed": hs(a, False), "land_cmd_post_speed": hs(a), "vz_impact": a["vz"],
                    "pre_speed": hs(c, False), "post_speed": hs(c), "dt": c["dt"],
                    "decel": (hs(c) - hs(c, False)) / c["dt"] if c["dt"] else None,
                    "slide_before": a["slide"], "slide_after": c["slide"], "duck": c["duck"], "series": ser}
            q = i
            while q < len(cmds) and hs(cmds[q]) > CENSUS["sprint_cap"] + 0.01 and cmds[q]["ground"] == 1:
                q += 1
            land["cmds_to_cap"] = (q - i + 1) if hs(c, False) > CENSUS["sprint_cap"] + 0.01 else 0
            land["decel_series"] = [round((hs(cmds[x]) - hs(cmds[x], False)) / cmds[x]["dt"], 1)
                                    for x in range(i, min(q + 1, len(cmds))) if cmds[x]["dt"]]
            # speed while the same input is still held (forward for the drop / hops), first 1.0 s after landing
            held, tt = [], 0.0
            for x in range(i, min(i + 160, len(cmds))):
                if cmds[x]["fwd"] < 0.5 or cmds[x]["ground"] == 0 or tt > 1.0:
                    break
                tt += cmds[x]["dt"] or 0
                held.append(hs(cmds[x]))
            land["held_after"] = {"s": round(tt, 4), "cmds": len(held), "min": min(held), "max": max(held),
                                  "last": held[-1]} if held else None
            out["landings"].append(land)
    for i in edges(cmds, "buttons", IN_JUMP):
        c = cmds[i]
        if c["ground"] != 1 or c["pvz"] < 50:
            continue
        prev = [l["i"] for l in out["landings"] if l["i"] < i]
        last_land = max(prev) if prev else None
        out["jumps"].append({"i": i, "pre_speed": hs(c, False), "post_speed": hs(c), "post_vz": c["pvz"],
                             "slide": c["slide"], "duck": c["duck"], "dt": c["dt"],
                             "cmds_since_land": (i - last_land) if last_land is not None else None,
                             "V": c["pvz"] + 1.5 * G * c["dt"]})
    return out


# ----------------------------------------------------------------------------- parity
def parity(t, key_idx=()):
    """Client vs dedi MOVE-TRACE of the same usercmd: worst position / velocity difference overall and on
    the key commands (contact, climb end, bounce, first command after the mantle)."""
    sv = {c["cmd"]: c for c in t["sv_mt"]}
    n, wp, wv, nbad = 0, 0.0, 0.0, 0
    for c in t["cmds"]:
        s = sv.get(c["cmd"])
        if not s:
            continue
        n += 1
        dp = max(abs(c[k] - s[k]) for k in ("pox", "poy", "poz"))
        dv = max(abs(c[k] - s[k]) for k in ("pvx", "pvy", "pvz"))
        wp, wv = max(wp, dp), max(wv, dv)
        nbad += dv > 0.01
    key = {}
    for name, i in key_idx:
        if i is None or i >= len(t["cmds"]):
            continue
        c = t["cmds"][i]
        s = sv.get(c["cmd"])
        if s:
            key[name] = max(abs(c[k] - s[k]) for k in ("pox", "poy", "poz", "pvx", "pvy", "pvz"))
    return {"cmds_both": n, "cl_cmds": len(t["cmds"]), "max_pos_diff": wp, "max_vel_diff": wv,
            "cmds_vel_diff_gt_0p01": nbad, "key": key}


# ----------------------------------------------------------------------------- main
def analyse_session(folder, want_rejected):
    S = L.load_session(folder)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    fps = runner.get("client_fps")
    mb = parse_mb(folder)
    res = {"session": S["folder"], "client_fps": fps, "trials": [], "rejected_e7": []}
    for t in S["trials"]:
        sch = t["schedule"] or ""
        if not sch.startswith(("e6", "e7", "e8")):
            continue
        cmds, frames = t["cmds"], t["frames"]
        T = {"run": t["label"], "schedule": sch, "fps_measured": t["fps"], "parity": parity(t),
             "sv_events": [e["evt"] for e in t["sv_evt"]], "mb_logged": bool(mb)}
        ft = [f["t"] for f in frames]
        lo, hi = min(ft), max(ft)
        T["mb"] = [m for m in mb if lo <= m["t"] <= hi]
        if sch.startswith(("e6", "e7")) or sch == "e8_drop_land":
            P = phases(cmds)
            if P:
                T["end_kind"] = P["end_kind"]
                T["parity"] = parity(t, [("contact", P["k"]), ("climb_end_or_bounce", P["e"]), ("mantle_exit", P["gap"])])
                T["climb"] = climb_metrics(cmds, P)
                T["mantle"] = mantle_metrics(cmds, frames, P)
                if P["end_kind"] == "bounce":
                    T["bounce"] = bounce_metrics(cmds, P, sch)
                if sch.startswith("e7"):
                    fj = edges(frames, "in_jump")
                    fd = edges(frames, "in_duck")
                    e7 = {"press_frame_offsets": [x - fj[0] for x in fj], "duck_frame_offsets": [x - fj[0] for x in fd]}
                    if len(fj) > 1:
                        pf = frames[fj[1]]
                        e7["press_t_after_first"] = pf["t"] - frames[fj[0]]["t"]
                        e7["press_t"] = pf["t"]
                        M = T.get("mantle")
                        if M:
                            e7["press_rel_trav_start"] = pf["t"] - M["t_last_cmd"]
                            e7["press_rel_trav_end"] = pf["t"] - M["t_first_cmd"]
                            e7["trav_start_after_first"] = M["t_last_cmd"] - frames[fj[0]]["t"]
                            e7["trav_end_after_first"] = M["t_first_cmd"] - frames[fj[0]]["t"]
                    trig = [m for m in T["mb"] if m["tag"] == "TRIG"]
                    app = [m for m in T["mb"] if m["tag"] == "APPLY"]
                    sv_ev = T["sv_events"]
                    i_m = sv_ev.index("MANTLE") if "MANTLE" in sv_ev else None
                    jump_after_m = i_m is not None and "JUMP" in sv_ev[i_m:]
                    if P["end_kind"] == "bounce":
                        cls = "wall_bounce"
                    elif any(m["result"] == 4 for m in trig if m["side"] == "sv"):
                        cls = "boost_state4"
                    elif any(m["result"] == 3 for m in trig if m["side"] == "sv"):
                        cls = "failed_state3"
                    elif jump_after_m and cmds[P["gap"]]["pvz"] > 200 and not mb:
                        cls = "exit_jump_unlogged"     # jump applied on the first command after the traversal; MB log off
                    elif jump_after_m and cmds[P["gap"]]["pvz"] > 200:
                        cls = "exit_jump_no_trig"
                    elif jump_after_m:
                        cls = "jump_on_top"
                    elif i_m is not None:
                        cls = "mantle_only"
                    else:
                        cls = "other"
                    e7["class"] = cls
                    rc = {m["side"]: m["result"] for m in trig}
                    e7["cl_sv_state_mismatch"] = len(rc) == 2 and rc["cl"] != rc["sv"]
                    if T.get("mantle") and len(fj) > 1:
                        e7["press_frames_before_trav_end"] = (T["mantle"]["t_first_cmd"] - frames[fj[1]]["t"]) * fps
                    e7["trig"] = trig
                    e7["apply"] = app
                    # exit of the mantle when a jump was applied at the finish
                    if T.get("mantle"):
                        g = P["gap"]
                        first = cmds[g]
                        e7["exit_post"] = (first["pvx"], first["pvy"], first["pvz"])
                        e7["exit_pre"] = (first["vx"], first["vy"], first["vz"])
                        e7["exit_duck"] = [cmds[q]["duck"] for q in range(g, min(g + 5, len(cmds)))]
                    tc = [m for m in trig if m["side"] == "cl"]
                    ac = [m for m in app if m["side"] == "cl"]
                    if tc and T.get("mantle"):
                        e7["trig_t_rel_start"] = tc[0]["t"] - T["mantle"]["t_last_cmd"]
                    if tc and ac:
                        e7["apply_minus_trig"] = ac[0]["t"] - tc[0]["t"]
                    T["e7"] = e7
        if sch.startswith("e8"):
            T["chain"] = landing_chain(cmds)
        res["trials"].append(T)
    if want_rejected:
        for tr in runner["trials"]:
            if tr.get("ok") or tr.get("warmup") or not tr.get("schedule", "").startswith("e7"):
                continue
            ts = {}
            for l in tr.get("sched_lines", []):
                m = re.search(r"edge=(\w+)(?: key=(\w+))? frame=(\d+).* t=([\d.]+)", l)
                if m:
                    ts.setdefault((m.group(1), m.group(2)), []).append((int(m.group(3)), float(m.group(4))))
            if ("start", None) not in ts or ("end", None) not in ts:
                continue
            a, b = ts[("start", None)][0][1], ts[("end", None)][0][1]
            L2 = [m for m in mb if a <= m["t"] <= b and m["side"] == "sv"]
            res["rejected_e7"].append({"run": f"r{tr['run']}", "schedule": tr["schedule"], "why": tr.get("why"),
                                       "fps_measured": tr.get("measured_fps"), "mb": L2})
    return res


def summarise(sessions):
    """Pooled numbers used by the model write-up."""
    out = {}
    allT = [(s["client_fps"], s["session"], t) for s in sessions for t in s["trials"]]
    # --- climb (all trials that ended with the final jump-up)
    cl = [(f, t) for f, _, t in allT if t.get("end_kind") == "final_jump"]
    C = {}
    for fps in sorted({f for f, _ in cl}):
        xs = [t["climb"] for f, t in cl if f == fps]
        C[str(int(fps))] = {k: st([x.get(k) for x in xs]) for k in
                            ("t_air_to_contact", "contact_dvz", "peak_vz", "peak_h", "peak_t", "climb_time",
                             "climb_cmds", "end_abs_z", "end_h", "end_vz_pre", "final_dvz", "final_V_half",
                             "final_post_vx")}
        C[str(int(fps))]["accel_first8"] = st([x["accel_first8"].get("mean") for x in xs])
        C[str(int(fps))]["accel_after8"] = st([x["accel_after8"].get("mean") for x in xs])
        C[str(int(fps))]["decay_rate"] = st([x["decay_rate"].get("mean") for x in xs])
        C[str(int(fps))]["vx_over_vz"] = st([x["vx_over_vz"].get("mean") for x in xs])
        C[str(int(fps))]["contact_z"] = st([x["contact_post"]["z"] for x in xs])
        C[str(int(fps))]["contact_vz_pre"] = st([x["contact_pre"]["vz"] for x in xs])
        C[str(int(fps))]["decay_vz_at_contact"] = st([x["decay_line"]["vz_at_contact_z"] for x in xs if "decay_line" in x])
        C[str(int(fps))]["decay_zero_abs_z"] = st([x["decay_line"]["zero_vz_abs_z"] for x in xs if "decay_line" in x])
        # end height: absolute vs relative (which one is tighter)
        if len(xs) > 2:
            m, b, _ = lin_fit([x["contact_post"]["z"] for x in xs], [x["end_abs_z"] for x in xs])
            C[str(int(fps))]["end_abs_z_vs_contact_z_slope"] = m
    out["climb"] = C
    # --- mantle (no press during it: e6_climb, e8_drop_land, e7 'mantle_only')
    M = {}
    for fps in sorted({f for f, _, _ in allT}):
        xs = [t["mantle"] for f, _, t in allT if f == fps and t.get("mantle") and
              (t["schedule"] in ("e6_climb", "e8_drop_land") or t.get("e7", {}).get("class") == "mantle_only")]
        ys = [t["mantle"] for f, _, t in allT if f == fps and t.get("mantle") and t.get("e7", {}).get("class") in ("failed_state3",)]
        if xs:
            M[str(int(fps))] = {"no_press": {k: st([x[k] for x in xs]) for k in
                                             ("duration", "start_z", "exit_z", "rise", "exit_speed", "air_cmds_before")},
                                "failed_state3": {k: st([y[k] for y in ys]) for k in ("duration", "exit_speed")}}
    out["mantle"] = M
    # --- bounce
    B = {}
    bt = [(f, t) for f, _, t in allT if t.get("bounce")]
    for f, t in bt:
        b = t["bounce"]
        timing = "0.15" if t["schedule"].endswith("_15") else "0.40" if t["schedule"].endswith("_40") else "e7"
        key = f"{b['input']}|{timing}|{int(f)}"
        B.setdefault(key, []).append(b)
    BS = {}
    for key, xs in sorted(B.items()):
        BS[key] = {k: st([x[k] for x in xs]) for k in ("t_since_contact", "d_out", "d_out_jump", "d_tan", "dvz",
                                                         "dvz_plus_1p5g", "next_dvx", "fwd", "side")}
        BS[key]["pre_vz"] = st([x["pre"][2] for x in xs])
        BS[key]["post"] = [st([x["post"][q] for x in xs]) for q in range(3)]
    out["bounce"] = BS
    none = [x["d_out_jump"] for k, xs in B.items() if k.startswith("none|") for x in xs]
    back = [x["d_out_jump"] for k, xs in B.items() if k.startswith("back|") for x in xs]
    fwd = [x["d_out_jump"] for k, xs in B.items() if k.startswith("fwd_held|") for x in xs]
    side = [x for k, xs in B.items() if k.startswith("side|") for x in xs]
    if none and fwd:
        mn, mf = sum(none) / len(none), sum(fwd) / len(fwd)
        O, I = (mn + mf) / 2, (mn - mf) / 2
        out["bounce_fit"] = {"O_outward": O, "I_inputdir": I, "n_none": len(none), "n_fwd": len(fwd),
                             "none_sd": st(none)["sd"], "fwd_sd": st(fwd)["sd"],
                             "back_mean": sum(back) / len(back) if back else None,
                             "side_pred_out": O, "side_pred_tan": -I,
                             "side_obs_out": st([x["d_out"] for x in side]), "side_obs_tan": st([x["d_tan"] for x in side])}
    # dvz relation
    xs = [t["bounce"] for f, t in bt]
    if len(xs) > 3:
        m, b, rr = lin_fit([x["pre"][2] for x in xs], [x["dvz_plus_1p5g"] for x in xs])
        out["bounce_dvz_fit"] = {"slope_vs_pre_vz": m, "intercept": b, "rms": rr, "n": len(xs)}
    # --- E8 hop350_d<D>: re-jump D frames after the landing frame
    H = {}
    for f, _, t in allT:
        m_ = re.match(r"e8_hop350_d(\d+)$", t["schedule"])
        if not m_ or not t.get("chain"):
            continue
        for k_, j in enumerate(t["chain"]["jumps"][1:]):     # first re-jump lands from the 350 slide jump
            H.setdefault((int(m_.group(1)), "first" if k_ == 0 else "later"), []).append(j)
    out["hop350"] = {f"d{d}_{w}": {"n": len(js), "cmds_since_land": st([j["cmds_since_land"] for j in js]),
                              "pre_speed": st([j["pre_speed"] for j in js]), "post_speed": st([j["post_speed"] for j in js]),
                              "loss": st([j["pre_speed"] - j["post_speed"] for j in js]), "V": st([j["V"] for j in js])}
                     for (d, w), js in sorted(H.items())}
    # --- E7 classification table
    E = {}
    for f, sname, t in allT:
        e = t.get("e7")
        if not e:
            continue
        tsv = [m for m in e["trig"] if m["side"] == "sv"]
        tr = tsv[0] if tsv else (e["trig"][0] if e["trig"] else None)
        E.setdefault(str(int(f)), []).append({
            "run": t["run"], "session": sname, "schedule": t["schedule"], "class": e["class"],
            "N": e["press_frame_offsets"][1] if len(e["press_frame_offsets"]) > 1 else None,
            "crouch": bool(e["duck_frame_offsets"]),
            "press_after_first_s": r(e.get("press_t_after_first"), 4),
            "press_rel_trav_start_s": r(e.get("press_rel_trav_start"), 4),
            "press_rel_trav_end_s": r(e.get("press_rel_trav_end"), 4),
            "trav_start_after_first_s": r(e.get("trav_start_after_first"), 4),
            "trav_end_after_first_s": r(e.get("trav_end_after_first"), 4),
            "anim": tr["anim"] if tr else None, "delta": tr["delta"] if tr else None,
            "gate": tr["gate"] if tr else None, "state": tr["result"] if tr else None,
            "trig_sides": sorted({m["side"] for m in e["trig"]}),
            "apply": [(a["side"], a["state"], a["speed"], a["vel"]) for a in e["apply"]],
            "raw": tr["raw"] if tr else None, "cl_sv_mismatch": e.get("cl_sv_state_mismatch"),
            "press_frames_before_trav_end": r(e.get("press_frames_before_trav_end"), 2),
            "exit_post": [r(v) for v in e.get("exit_post", ())]})
    for k in E:
        E[k].sort(key=lambda x: (x["N"] or 0, x["crouch"]))
    out["e7"] = E
    # class boundaries per fps: N (frames after the climb jump press) and press time relative to the
    # last usercmd before the traversal (the traversal's first frame is +1 frame)
    W = {}
    for fps, rows in E.items():
        W[fps] = {}
        for cls in sorted({x["class"] for x in rows}):
            xs = [x for x in rows if x["class"] == cls]
            W[fps][cls] = {"n": len(xs), "N_min": min(x["N"] for x in xs), "N_max": max(x["N"] for x in xs),
                           "rel_trav_start_min": min((x["press_rel_trav_start_s"] for x in xs if x["press_rel_trav_start_s"] is not None), default=None),
                           "rel_trav_start_max": max((x["press_rel_trav_start_s"] for x in xs if x["press_rel_trav_start_s"] is not None), default=None),
                           "anim_max": max((x["anim"] for x in xs if x["anim"] is not None), default=None),
                           "crouch_n": sum(x["crouch"] for x in xs)}
    out["e7_windows"] = W
    # measured boost window (dedi decision): anim / raw edges and press position before the traversal end
    BW = {}
    for fps, rows in E.items():
        b = [x for x in rows if x["class"] == "boost_state4"]
        f3 = [x for x in rows if x["class"] == "failed_state3" and x["anim"] is not None]
        top = [x for x in rows if x["class"] == "jump_on_top"]
        if not b:
            continue
        fb = [x["press_frames_before_trav_end"] for x in b if x["press_frames_before_trav_end"] is not None]
        ff = [x["press_frames_before_trav_end"] for x in f3 if x["press_frames_before_trav_end"] is not None]
        BW[fps] = {"n_boost": len(b), "n_fail": len(f3), "n_jump_on_top": len(top),
                   "N_boost": [min(x["N"] for x in b), max(x["N"] for x in b)],
                   "N_fail_max": max((x["N"] for x in f3), default=None),
                   "N_top_min": min((x["N"] for x in top), default=None),
                   "anim_open": {"last_fail": max((x["anim"] for x in f3), default=None),
                                 "first_boost": min(x["anim"] for x in b)},
                   "raw_open": {"last_fail": max((x["raw"] for x in f3), default=None),
                                "first_boost": min(x["raw"] for x in b)},
                   "delta_open": {"last_fail": min((x["delta"] for x in f3 if x["anim"] > 0.5), default=None),
                                  "first_boost": max(x["delta"] for x in b)},
                   "anim_last_boost": max(x["anim"] for x in b),
                   "frames_before_end_boost": [min(fb), max(fb)] if fb else None,
                   "frames_before_end_fail_min": min((v for v in ff if v > 0), default=None),
                   "exit_post_boost": [st([x["exit_post"][0] for x in b]), st([x["exit_post"][2] for x in b])],
                   "cl_sv_mismatch": [x["run"] for x in rows if x.get("cl_sv_mismatch")]}
    out["boost_window"] = BW
    # traversal timing vs climb jump (jitter), per fps
    out["e7_traversal"] = {fps: {"start_after_first": st([x["trav_start_after_first_s"] for x in rows]),
                                 "end_after_first": st([x["trav_end_after_first_s"] for x in rows])} for fps, rows in E.items()}
    # anim fraction vs time since the last pre-traversal usercmd (scored trials, client MB-TRIG time)
    pts = [(t["e7"]["trig_t_rel_start"], t["e7"]["trig"][0]["anim"]) for f, _, t in allT
           if t.get("e7", {}).get("trig_t_rel_start") is not None]
    if len(pts) > 3:
        m, b, rr = lin_fit([p[0] for p in pts], [p[1] for p in pts])
        out["anim_vs_time"] = {"slope_per_s": m, "intercept": b, "rms": rr, "n": len(pts),
                               "implied_traversal_s": 1 / m, "anim0_time_s": -b / m}
    # traversal remaining time after the activation press vs anim fraction (APPLY t - TRIG t, client side)
    rem = [(t["e7"]["trig"][0]["anim"], t["e7"]["apply_minus_trig"]) for f, _, t in allT
           if t.get("e7", {}).get("apply_minus_trig") is not None]
    rej = []
    for s_ in sessions:
        for x in s_.get("rejected_e7", []):
            tr = [m for m in x["mb"] if m["tag"] == "TRIG"]
            apl = [m for m in x["mb"] if m["tag"] == "APPLY"]
            if tr and apl:
                rej.append((tr[0]["anim"], apl[0]["t"] - tr[0]["t"], tr[0]["delta"], tr[0]["gate"], tr[0]["result"], x["run"], x["fps_measured"]))
    if len(rem) > 3:
        m, b, rr = lin_fit([1 - p[0] for p in rem], [p[1] for p in rem])
        out["remaining_vs_anim_scored"] = {"T_s": m, "offset_s": b, "rms": rr, "n": len(rem),
                                           "anim_range": [min(p[0] for p in rem), max(p[0] for p in rem)]}
        allp = rem + [(p[0], p[1]) for p in rej]
        m2, b2, rr2 = lin_fit([1 - p[0] for p in allp], [p[1] for p in allp])
        out["remaining_vs_anim_with_rejected"] = {"T_s": m2, "offset_s": b2, "rms": rr2, "n": len(allp)}
    out["rejected_trig"] = rej
    # climb end: which variable gives a consistent threshold (bracket = (max prev, min end])
    ends = [t["climb"] for f, _, t in allT if t.get("end_kind") == "final_jump" and "prev_abs_z" in t["climb"]]
    if ends:
        out["climb_end_bracket"] = {
            "abs_z": {"lo": max(x["prev_abs_z"] for x in ends), "hi": min(x["end_abs_z"] for x in ends)},
            "h_above_contact": {"lo": max(x["prev_abs_z"] - x["contact_post"]["z"] for x in ends),
                                "hi": min(x["end_abs_z"] - x["contact_post"]["z"] for x in ends)},
            "time_since_contact": {"lo": max(x["prev_t_start"] for x in ends), "hi": min(x["end_t_start"] for x in ends)},
            "vz_pre": {"hi": min(x["prev_vz_pre"] for x in ends), "lo": max(x["end_vz_pre"] for x in ends)},
            "n": len(ends), "note": "a variable is a consistent end trigger only if lo < hi (for vz: end when vz <= thr, lo < thr < hi)"}
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json", default=None)
    ap.add_argument("--rejected", action="store_true")
    a = ap.parse_args(argv)
    sessions = [analyse_session(s, a.rejected) for s in a.sessions]
    summ = summarise(sessions)
    # ---------------------------------------------------------------- console report
    print("== climb (trials ending in the final jump-up), per client fps")
    for fps, C in summ["climb"].items():
        print(f"-- {fps} fps")
        for k, v in C.items():
            print(f"   {k:30s} {L.fmt(v, 4) if isinstance(v, dict) else round(v, 5)}")
    print("== mantle")
    for fps, M in summ["mantle"].items():
        for grp, D in M.items():
            for k, v in D.items():
                print(f"   {fps:>4s} {grp:14s} {k:16s} {L.fmt(v, 4)}")
    print("== bounce per input|timing|fps")
    for key, D in summ["bounce"].items():
        print(f"-- {key}")
        for k, v in D.items():
            print(f"   {k:16s} {L.fmt(v, 3) if isinstance(v, dict) else [L.fmt(x, 3) for x in v]}")
    print("   fit", json.dumps(summ.get("bounce_fit"), default=lambda o: o), json.dumps(summ.get("bounce_dvz_fit")))
    print("== E7 per fps")
    for fps, rows in summ["e7"].items():
        print(f"-- {fps} fps")
        for x in rows:
            print(f"   {x['run']:6s} N={x['N']:<4} {'sg' if x['crouch'] else 'mb'} {x['class']:14s} "
                  f"press-trav_start {x['press_rel_trav_start_s']} trav_start {x['trav_start_after_first_s']} "
                  f"end {x['trav_end_after_first_s']} anim {x['anim']} delta {x['delta']} gate {x['gate']} "
                  f"state {x['state']} sides {x['trig_sides']} exit {x['exit_post']}")
    print("== E7 class windows", json.dumps(summ["e7_windows"], indent=None))
    print("== measured boost window", json.dumps(summ.get("boost_window"), default=lambda o: o))
    print("== hop350 by D", json.dumps(summ.get("hop350"), default=lambda o: o))
    print("== E7 traversal timing", json.dumps(summ["e7_traversal"], default=lambda o: o))
    print("== anim vs time", json.dumps(summ.get("anim_vs_time")))
    print("== remaining traversal vs anim (scored)", json.dumps(summ.get("remaining_vs_anim_scored")))
    print("== remaining traversal vs anim (scored + rejected)", json.dumps(summ.get("remaining_vs_anim_with_rejected")))
    print("== rejected TRIG (anim, apply-trig s, delta, gate, state, run, fps)", json.dumps(summ.get("rejected_trig")))
    print("== climb end bracket", json.dumps(summ.get("climb_end_bracket")))
    print("== E8 chains")
    for s in sessions:
        for t in s["trials"]:
            ch = t.get("chain")
            if not ch:
                continue
            ls = "; ".join(f"land air {l['air_speed']:.2f}->{l['land_cmd_post_speed']:.2f} 1st-ground {l['pre_speed']:.2f}->{l['post_speed']:.2f} vz {l['vz_impact']:.1f} "
                           f"decel {l['decel']:.1f} sl {l['slide_before']}->{l['slide_after']} toCap {l['cmds_to_cap']} "
                           f"decels {l['decel_series'][:8]} held {l['held_after']}"
                           for l in ch["landings"])
            js = "; ".join(f"jump pre {j['pre_speed']:.2f} post {j['post_speed']:.3f} V {j['V']:.2f} sl {j['slide']} "
                           f"since_land {j['cmds_since_land']}" for j in ch["jumps"])
            print(f"   {s['client_fps']:.0f} {t['run']:6s} {t['schedule']:15s} {js} || {ls}")
    print("== parity (client vs dedi MOVE-TRACE, same usercmd)")
    tot = sum(t["parity"]["cmds_both"] for s in sessions for t in s["trials"])
    for sch in ("e6", "e7", "e8"):
        P_ = [t["parity"] for s in sessions for t in s["trials"] if t["schedule"].startswith(sch)]
        if not P_:
            continue
        print(f"   {sch}: trials {len(P_)} cmds {sum(p['cmds_both'] for p in P_)} worst pos {max(p['max_pos_diff'] for p in P_):.3f} "
              f"worst vel {max(p['max_vel_diff'] for p in P_):.3f}; trials with any vel diff > 0.01: "
              f"{sum(p['cmds_vel_diff_gt_0p01'] > 0 for p in P_)}")
        for kname in ("contact", "climb_end_or_bounce", "mantle_exit"):
            v = [p["key"][kname] for p in P_ if kname in p.get("key", {})]
            if v:
                print(f"      key cmd {kname:20s} n {len(v)} max|diff| {max(v):.3f}  >0.01: {sum(x > 0.01 for x in v)}")
    print(f"   compared cmds total {tot}")
    mbpar = []
    for s in sessions:
        for t in s["trials"]:
            tc = [m for m in t["mb"] if m["side"] == "cl"]
            tsv = [m for m in t["mb"] if m["side"] == "sv"]
            for x, y in zip(tc, tsv):
                if x["tag"] == y["tag"] == "TRIG":
                    mbpar.append((abs(x["anim"] - y["anim"]), abs(x["delta"] - y["delta"]), x["result"] == y["result"]))
    if mbpar:
        print(f"   MB-TRIG cl/sv pairs {len(mbpar)}: max |anim diff| {max(p[0] for p in mbpar):.3f}, "
              f"max |delta diff| {max(p[1] for p in mbpar):.2f}, same state {sum(p[2] for p in mbpar)}/{len(mbpar)}")
    if a.rejected:
        print("== rejected E7 trials (frame rate outside tolerance; supplementary only)")
        for s in sessions:
            for x in s["rejected_e7"]:
                tr = [m for m in x["mb"] if m["tag"] == "TRIG"]
                ap_ = [m for m in x["mb"] if m["tag"] == "APPLY"]
                print(f"   {s['client_fps']:.0f} {x['run']:6s} {x['schedule']:12s} fps {x['fps_measured']} | " +
                      "; ".join(f"anim {m['anim']} delta {m['delta']} prev {m['prev']} gate {m['gate']} -> {m['result']} t {m['t']}" for m in tr) +
                      " | " + "; ".join(f"state {m['state']} speed {m['speed']} vel {m['vel']} t {m['t']}" for m in ap_))
    if a.json:
        slim = {"sessions": [{"session": s["session"], "client_fps": s["client_fps"],
                              "trials": [{k: v for k, v in t.items() if k not in ("mb",)} for t in s["trials"]],
                              "rejected_e7": s["rejected_e7"]} for s in sessions], "summary": summ}
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(slim, fh, indent=1, default=lambda o: None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
