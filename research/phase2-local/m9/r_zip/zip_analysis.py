#!/usr/bin/env python3
"""M9 track R ① zipline A1: mid-rope / end mounts, ride direction, air mounts, re-mounts (R5Flowstate S21, local offline).

  py -3 zip_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Schedules m9z_* / m9zd_* / m9zv_* (tools/hsd_trial.py), geometry m9zip (flat ropes 100 / 130 /
170 / 80 u above the floor, a sloped rope 60 -> 260 u) or m3,m9zipv (vertical rope in front of the 232 u rock). The rope
geometry is read from runner.json (geometry_ropes) so the script needs no copy of it.

Per trial (client first-time MOVE-TRACE usercmds joined to client HSD frames; zipline state from the client [HSD-STATE] zip
flag; SDK diag lines [ZIPRAIL-USE] of both sides):
- use presses   = schedule 'use' down edges; the usercmd of a press is the first client usercmd at or after the edge time
                  whose buttons carry IN_USE (0x20), or (mount) the first usercmd missing from MOVE-TRACE after the edge;
- pre-state     = the last client usercmd before the press: origin, view (yaw / pitch from the joined frame), ground;
- Find rule     = M6-A3: P = origin + (0,0,72), e = eye direction; Q* = the rope point with the smallest angle(e, Q - P) among
                  points with |Q - P| <= 130; reported as the predicted angle (deg) and Q*;
- mount         = the zip flag turns true within 0.1 s of the press (client); dedi [ZIPRAIL-USE] result / use / rev;
- grip          = the dedi use position (or the client hang point + 80 u when no dedi line); along-rope fraction;
- ride dir      = sign of the client velocity along the rope (start -> end) averaged over zip frames 0.1..0.6 s after the
                  mount; 'fwd' = toward the rope end, 'rev' = toward the start (vertical: up / down);
- ride end      = zip flag off: by an auto-detach (no jump / duck press within 2 frames), jump-off or crouch-off.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zip_load as Z  # noqa: E402

L = Z.L
FLOOR = 294.92
IN_USE = 0x20
FIND_R = 130.0
EYE_RAISE = 72.0


def r(x, n=3):
    return None if x is None else round(x, n)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    return math.sqrt(dot(a, a))


def eye_dir(pitch, yaw):
    p, y = math.radians(pitch), math.radians(yaw)
    return (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), -math.sin(p))


def ropes_of(runner):
    """name -> (A, B) world end points (A = rope start)."""
    g = runner.get("geometry_ropes") or {}
    out = {}
    for name, v in g.items():
        if name == "vertical":
            x, y, h0, h1 = v
            out["v"] = ((x, y, FLOOR + h0), (x, y, FLOOR + h1))
        else:
            y, x0, h0, x1, h1 = v
            out[name] = ((x0, y, FLOOR + h0), (x1, y, FLOOR + h1))
    return out


def rope_param(A, B, Q):
    d = sub(B, A)
    Lr = norm(d)
    s = dot(sub(Q, A), d) / Lr
    return s, Lr


def find_rule(P, e, A, B, step=0.25):
    """Minimum-angle rope point within FIND_R of P. Returns (angle_deg, Q, s) or None."""
    d = sub(B, A)
    Lr = norm(d)
    u = (d[0] / Lr, d[1] / Lr, d[2] / Lr)
    best = None
    n = int(Lr / step)
    for i in range(n + 1):
        s = i * step
        Q = (A[0] + u[0] * s, A[1] + u[1] * s, A[2] + u[2] * s)
        v = sub(Q, P)
        dist = norm(v)
        if dist > FIND_R or dist == 0:
            continue
        c = max(-1.0, min(1.0, dot(v, e) / dist))
        ang = math.degrees(math.acos(c))
        if best is None or ang < best[0]:
            best = (ang, Q, s)
    return best


def nearest_rope(ropes, P):
    best = None
    for name, (A, B) in ropes.items():
        s, Lr = rope_param(A, B, P)
        sc = min(max(s, 0.0), Lr)
        d = sub(B, A)
        Q = (A[0] + d[0] * sc / Lr, A[1] + d[1] * sc / Lr, A[2] + d[2] * sc / Lr)
        dist = norm(sub(Q, P))
        if best is None or dist < best[0]:
            best = (dist, name)
    return best[1] if best else None


def sched_edges(T, key, edge="down"):
    out = []
    for l in T["sched_lines"]:
        if ("edge=%s" % edge) in l and ("key=%s " % key) in l:
            out.append(float(next(tok[2:] for tok in l.split() if tok.startswith("t="))))
    return out


def zip_segments(states):
    segs, cur = [], None
    for s in states:
        if s.get("zip"):
            if cur is None:
                cur = [s["t"], s["t"]]
            else:
                cur[1] = s["t"]
        elif cur is not None:
            segs.append(tuple(cur))
            cur = None
    if cur is not None:
        segs.append(tuple(cur))
    return segs


def frames_between(T, t0, t1):
    return [f for f in T["frames"] if t0 - 1e-6 <= f["t"] <= t1 + 1e-6]


def pre_cmd(T, t):
    """Last joined client usercmd strictly before game time t."""
    best = None
    for c in T["cmds"]:
        if c.get("t") is None:
            continue
        if c["t"] < t - 1e-6 and (best is None or c["t"] > best["t"]):
            best = c
    return best


def frame_at(T, t):
    best = None
    for f in T["frames"]:
        if best is None or abs(f["t"] - t) < abs(best["t"] - t):
            best = f
    return best


def analyse_press(T, ropes, t_press, segs):
    """One use press: pre-state, Find rule prediction, mount result, grip, ride direction."""
    c = pre_cmd(T, t_press)
    f = frame_at(T, c["t"]) if c else None
    out = {"t_press": r(t_press, 4)}
    if not c or not f or f.get("pitch") is None:
        out["error"] = "no pre-state"
        return out
    o = (c["pox"], c["poy"], c["poz"])
    P = (o[0], o[1], o[2] + EYE_RAISE)
    e = eye_dir(f["pitch"], f["yaw"])
    out.update(pre_o=[r(x, 2) for x in o], pre_v=[r(c["pvx"], 2), r(c["pvy"], 2), r(c["pvz"], 2)], pre_ground=c["ground"],
               pitch=r(f["pitch"], 3), yaw=r(f["yaw"], 3), z_above_floor=r(o[2] - FLOOR, 2))
    rn = nearest_rope(ropes, P)
    out["rope"] = rn
    if rn:
        A, B = ropes[rn]
        s0, Lr = rope_param(A, B, P)
        out["P_along"] = r(s0, 1)
        out["rope_len"] = r(Lr, 1)
        d = sub(B, A)
        sc = min(max(s0, 0.0), Lr)
        Qn = (A[0] + d[0] * sc / Lr, A[1] + d[1] * sc / Lr, A[2] + d[2] * sc / Lr)
        out["P_to_rope"] = r(norm(sub(Qn, P)), 2)
        out["rope_minus_P_z"] = r(Qn[2] - P[2], 2)
        fr = find_rule(P, e, A, B)
        if fr:
            out["rule_angle"] = r(fr[0], 3)
            out["rule_s"] = r(fr[2], 1)
            out["rule_Q"] = [r(x, 2) for x in fr[1]]
        else:
            out["rule_angle"] = None
    # mount: a zip segment starting within 0.1 s after the press
    seg = next((s for s in segs if -0.02 <= s[0] - t_press <= 0.1), None)
    out["mounted_cl"] = seg is not None
    # client / dedi Use lines near the press usercmd
    cmd_lo = c["cmd"]
    cl = [d for d in T["cl_zip"] if d["tag"] == "ZIPRAIL-USE" and cmd_lo < d["cmd"] <= cmd_lo + 12]
    sv = [d for d in T["sv_zip"] if d["tag"] == "ZIPRAIL-USE" and cmd_lo < d["cmd"] <= cmd_lo + 12]
    out["cl_use"] = [{"cmd": d["cmd"], "result": d.get("result"), "why": d.get("why"), "cd": d.get("cd")} for d in cl]
    out["sv_use"] = [{"cmd": d["cmd"], "result": d.get("result"), "rev": d.get("rev"), "use": [r(x, 2) for x in d.get("use", ())]}
                     for d in sv]
    finds = [fd for d in T["sv_zip"] if cmd_lo < d["cmd"] <= cmd_lo + 12 for fd in d.get("finds", [])]
    out["sv_find"] = [{"found": fd.get("found"), "rev": fd.get("rev"), "use": [r(x, 2) for x in fd.get("use", ())]} for fd in finds]
    disc = [d for d in T["cl_zip"] + T["sv_zip"] if d["tag"] == "ZIP-DISC" and cmd_lo < d["cmd"] <= cmd_lo + 12]
    out["disc"] = [d.get("what") + ":" + str(d.get("left")) for d in disc]
    sv_ok = any(d.get("result") == 1 for d in sv)
    out["mounted_sv"] = sv_ok
    if not seg:
        return out
    out["seg"] = [r(seg[0], 4), r(seg[1], 4)]
    out["ride_s"] = r(seg[1] - seg[0], 4)
    # grip: dedi use position, else the rule point
    grip = next((d["use"] for d in sv if d.get("result") == 1 and d.get("use")), None)
    if grip and rn:
        A, B = ropes[rn]
        s, Lr = rope_param(A, B, grip)
        out["grip"] = [r(x, 2) for x in grip]
        out["grip_s"] = r(s, 1)
        out["grip_frac"] = r(s / Lr, 4)
        if out.get("rule_s") is not None:
            out["grip_minus_rule_s"] = r(s - out["rule_s"], 2)
        out["grip_minus_P_s"] = r(s - out["P_along"], 1)
    # ride direction over 0.1..0.6 s of the ride
    fr_ = frames_between(T, seg[0] + 0.1, min(seg[1], seg[0] + 0.6))
    if rn and fr_:
        A, B = ropes[rn]
        d = sub(B, A)
        Lr = norm(d)
        u = (d[0] / Lr, d[1] / Lr, d[2] / Lr)
        va = [dot((g["vx"], g["vy"], g["vz"]), u) for g in fr_]
        m = sum(va) / len(va)
        out["v_along_mean"] = r(m, 2)
        out["ride_dir"] = "fwd" if m > 5 else "rev" if m < -5 else "none"
        if rn == "v":
            out["ride_dir"] = "up" if m > 5 else "down" if m < -5 else "none"
    # speed at the end of the ride and the exit kind
    last = frames_between(T, seg[1] - 0.02, seg[1] + 0.001)
    nxt = [g for g in T["frames"] if g["t"] > seg[1] + 1e-6][1:3]
    if last:
        out["v_end"] = r(math.sqrt(last[-1]["vx"] ** 2 + last[-1]["vy"] ** 2 + last[-1]["vz"] ** 2), 1)
    if nxt:
        g = nxt[0]
        out["v_exit"] = [r(g["vx"], 1), r(g["vy"], 1), r(g["vz"], 1)]
        out["o_exit"] = [r(g["ox"], 1), r(g["oy"], 1), r(g["oz"], 1)]
        jt = [t for t in sched_edges(T, "jump") if abs(t - seg[1]) < 0.03]
        dt_ = [t for t in sched_edges(T, "duck") if abs(t - seg[1]) < 0.03]
        out["exit"] = "jump" if jt else "duck" if dt_ else "auto/other"
        if rn:
            A, B = ropes[rn]
            s, Lr = rope_param(A, B, (g["ox"], g["oy"], g["oz"]))
            out["exit_s"] = r(s, 1)
    return out


def cmd_after(T, t):
    return next((c for c in T["cmds"] if c.get("t") is not None and c["t"] >= t - 1e-6), None)


def extras(T, row, ropes, segs):
    """Schedule-specific measurements."""
    sch = T["schedule"]
    ex = {}
    if segs:
        s0 = segs[0]
        f1 = frames_between(T, s0[0], s0[0] + 0.02)
        if f1:
            ex["v_first_ride_frame"] = r(math.sqrt(f1[0]["vx"] ** 2 + f1[0]["vy"] ** 2 + f1[0]["vz"] ** 2), 2)
        for tt in (0.25, 0.5, 1.0):
            g = frames_between(T, s0[0] + tt - 0.005, s0[0] + tt + 0.005)
            if g and s0[0] + tt <= s0[1]:
                ex["v_ride_%.2fs" % tt] = r(math.sqrt(g[0]["vx"] ** 2 + g[0]["vy"] ** 2 + g[0]["vz"] ** 2), 2)
    if sch == "m9zd_turn180" and segs:
        s0 = segs[0]
        rn = row["presses"][0].get("rope") if row["presses"] else None
        if rn:
            A, B = ropes[rn]
            d = sub(B, A)
            Lr = norm(d)
            u = (d[0] / Lr, d[1] / Lr, d[2] / Lr)
            pts = []
            for tt in (0.6, 0.9, 1.2, 1.5):
                g = frames_between(T, s0[0] + tt - 0.005, s0[0] + tt + 0.005)
                if g and s0[0] + tt <= s0[1]:
                    pts.append([tt, r(dot((g[0]["vx"], g[0]["vy"], g[0]["vz"]), u), 1), r(g[0].get("yaw"), 1)])
            ex["v_along_yaw"] = pts
    if sch in ("m9zd_jo_lurch", "m9zd_jo_ctrl") and segs:
        # D press 3 frames after the jump-off (lurch) or the same usercmd index without a press (control)
        tj = segs[0][1]
        cs = [c for c in T["cmds"] if c.get("t") is not None and c["t"] > tj + 1e-6]
        dk = sched_edges(T, "moveright")
        k = None
        if dk:
            c = cmd_after(T, dk[0])
            k = cs.index(c) if c in cs else None
        elif len(cs) > 3:
            k = 3
        if k is not None and k < len(cs):
            c = cs[k]
            ex["press_cmd_after_exit"] = k
            ex["dv_press"] = [r(c["pvx"] - c["vx"], 3), r(c["pvy"] - c["vy"], 3)]
            ex["dv_press_abs"] = r(math.hypot(c["pvx"] - c["vx"], c["pvy"] - c["vy"]), 3)
            ex["v_after"] = [r(c["pvx"], 2), r(c["pvy"], 2), r(c["pvz"], 2)]
            ex["t_since_jumpoff"] = r(c["t"] - tj, 4)
    if segs:
        # velocity 3 client frames after the first ride ends (jump-off / crouch-off / auto-detach result)
        aft = [f for f in T["frames"] if f["t"] > segs[0][1] + 1e-6]
        if len(aft) > 3:
            ex["v_after_exit3"] = [r(aft[3]["vx"], 2), r(aft[3]["vy"], 2), r(aft[3]["vz"], 2)]
    if (sch == "m9zd_superjump" or sch.startswith("m9zd_sj_")) and segs:
        tj = segs[0][1]
        # skip the jump-off command itself (its post-state carries the 289.8 jump-off impulse)
        fr = [f for f in T["frames"] if tj + 0.012 <= f["t"] <= tj + 0.35]
        best = None
        for a_, b_ in zip(fr, fr[1:]):
            if b_["vz"] - a_["vz"] > 100:
                best = (b_["t"] - tj, b_["vz"], a_["vz"])
                break
        ex["second_jump"] = [r(x, 3) for x in best] if best else None
        after = [f for f in T["frames"] if f["t"] >= tj]
        if after:
            ex["apex_above_exit"] = r(max(f["oz"] for f in after[:240]) - after[0]["oz"], 2)
    return ex


def trial_row(T, ropes, session):
    row = {"session": session, "run": T["run"], "schedule": T["schedule"], "fps": T["fps"], "join": T["join"]["joined"]}
    segs = zip_segments(T["states"])
    row["zip_segments"] = [[r(a, 4), r(b, 4)] for a, b in segs]
    row["presses"] = [analyse_press(T, ropes, t, segs) for t in sched_edges(T, "use")]
    # a mount without a press (none expected: no auto-attach)
    pts = [p["t_press"] for p in row["presses"]]
    row["mount_without_press"] = [[r(a, 4), r(b, 4)] for a, b in segs if not any(-0.02 <= a - t <= 0.1 for t in pts)]
    row["extras"] = extras(T, row, ropes, segs)
    return row


def cnt(vals):
    out = {}
    for v in vals:
        out[str(v)] = out.get(str(v), 0) + 1
    return out


def mean(vals):
    vals = [v for v in vals if v is not None]
    return r(sum(vals) / len(vals), 2) if vals else None


def span(vals):
    vals = [v for v in vals if v is not None]
    return [r(min(vals), 2), r(max(vals), 2)] if vals else None


def summarise(rows):
    groups = {}
    for w in rows:
        groups.setdefault(w["schedule"], []).append(w)
    S = {}
    for sch in sorted(groups):
        ws = groups[sch]
        npress = max(len(w["presses"]) for w in ws)
        G = {"n": len(ws), "presses": []}
        for k in range(npress):
            ps = [w["presses"][k] for w in ws if len(w["presses"]) > k]
            G["presses"].append({
                "n": len(ps),
                "mounted_cl": sum(1 for p in ps if p.get("mounted_cl")),
                "mounted_sv": sum(1 for p in ps if p.get("mounted_sv")),
                "cl_use_lines": cnt([",".join("%s/%s" % (u["result"], u["why"]) for u in p.get("cl_use", [])) or "-" for p in ps]),
                "disc": cnt([",".join(p.get("disc", [])) or "-" for p in ps]),
                "pre_ground": cnt([p.get("pre_ground") for p in ps]),
                "z_above_floor": mean([p.get("z_above_floor") for p in ps]),
                "rope_minus_P_z": span([p.get("rope_minus_P_z") for p in ps]),
                "P_to_rope": span([p.get("P_to_rope") for p in ps]),
                "P_along": span([p.get("P_along") for p in ps]),
                "yaw_pitch": [mean([p.get("yaw") for p in ps]), mean([p.get("pitch") for p in ps])],
                "rule_angle": span([p.get("rule_angle") for p in ps]),
                "grip_s": span([p.get("grip_s") for p in ps]),
                "grip_minus_rule_s": span([p.get("grip_minus_rule_s") for p in ps]),
                "grip_minus_P_s": span([p.get("grip_minus_P_s") for p in ps]),
                "ride_dir": cnt([p.get("ride_dir") for p in ps if p.get("mounted_cl")]),
                "sv_rev": cnt([u.get("rev") for p in ps for u in p.get("sv_use", []) if u.get("result") == 1]),
                "exit": cnt([p.get("exit") for p in ps if p.get("mounted_cl")]),
                "exit_s": span([p.get("exit_s") for p in ps]),
                "v_exit": [mean([p["v_exit"][i] for p in ps if p.get("v_exit")]) for i in range(3)],
                "ride_s": span([p.get("ride_s") for p in ps]),
            })
        ex = {}
        for key in ("v_first_ride_frame", "v_ride_0.25s", "v_ride_0.50s", "v_ride_1.00s", "dv_press_abs", "apex_above_exit",
                    "t_since_jumpoff"):
            vals = [w["extras"].get(key) for w in ws if w["extras"].get(key) is not None]
            if vals:
                ex[key] = {"mean": mean(vals), "span": span(vals), "n": len(vals)}
        for key in ("v_along_yaw", "second_jump", "dv_press", "v_after", "v_after_exit3"):
            vals = [w["extras"].get(key) for w in ws if key in w["extras"]]
            if vals:
                ex[key] = vals
        G["extras"] = ex
        G["mount_without_press"] = sum(len(w["mount_without_press"]) for w in ws)
        S[sch] = G
    return S


def standing_presses(rows):
    """First press of the m9z_ standing schedules (no crouch, no move), horizontal / sloped ropes."""
    for w in rows:
        if not w["schedule"].startswith("m9z_") or not w["presses"]:
            continue
        p = w["presses"][0]
        if p.get("pre_ground") == 1 and p.get("rope") not in (None, "v"):
            yield w, p


def find_bracket(rows):
    """Standing ground presses: dedi mount vs the Find-rule angle (cone) and vs the distance from origin+72 to the rope
    (candidate collector). r80 (hang point at floor level) is listed separately."""
    ok, bad = [], []
    for w, p in standing_presses(rows):
        if p["rope"] == "r80" or p.get("rule_angle") is None or p.get("P_to_rope", 999) > 120:
            continue
        (ok if p.get("mounted_sv") else bad).append((p["rule_angle"], w["schedule"], w["run"]))
    col_ok, col_bad = [], []
    for w, p in standing_presses(rows):
        if p["rope"] == "r80":
            continue
        if p.get("rule_angle") is not None and p["rule_angle"] > 33.2:
            continue
        (col_ok if p.get("mounted_sv") else col_bad).append((p.get("P_to_rope"), w["schedule"], w["run"]))
    r80 = [(w["schedule"], bool(p.get("mounted_sv"))) for w, p in standing_presses(rows) if p["rope"] == "r80"]
    none = sorted(set(w["schedule"] for w, p in standing_presses(rows) if p.get("rule_angle") is None))
    return {"max_success": max(ok) if ok else None, "min_failure": min(bad) if bad else None,
            "n_success": len(ok), "n_failure": len(bad), "failure_below_max_success": sum(1 for b in bad if ok and b[0] < max(ok)[0]),
            "collector_max_success": max(col_ok) if col_ok else None, "collector_min_failure": min(col_bad) if col_bad else None,
            "collector_failure_below_max_success": sum(1 for b in col_bad if col_ok and b[0] < max(col_ok)[0]),
            "r80": {"n": len(r80), "mounted": sum(1 for x in r80 if x[1])},
            "no_point_within_130": none}


def remount_table(rows):
    """Every later press of a trial: time since the previous ride ended, airborne, mounted, client cooldown before it."""
    out = []
    for w in rows:
        segs = w["zip_segments"]
        cds = []
        for k, p in enumerate(w["presses"]):
            prev = [s for s in segs if s[1] < p["t_press"] - 1e-6]
            cd_prev = next((u["cd"] for q in w["presses"][:k][::-1] for u in q.get("cl_use", []) if u.get("result") == 1), None)
            if k == 0 or not prev:
                continue
            out.append({"schedule": w["schedule"], "run": w["run"], "k": k, "dt_since_detach": r(p["t_press"] - prev[-1][1], 3),
                        "ground": p.get("pre_ground"), "mounted_cl": bool(p.get("mounted_cl")), "mounted_sv": bool(p.get("mounted_sv")),
                        "client_use_line": bool(p.get("cl_use")), "cd_after_prev_grant": cd_prev, "rule_angle": p.get("rule_angle"),
                        "rope_minus_P_z": p.get("rope_minus_P_z"), "disc": p.get("disc")})
    return out


def direction_table(rows, ropes_by_session):
    """Ride direction against the view: view_dot_rope = eye direction . rope direction (start -> end)."""
    out = []
    for w in rows:
        ropes = ropes_by_session[w["session"]]
        for p in w["presses"]:
            if not p.get("mounted_cl") or not p.get("rope") or p.get("yaw") is None:
                continue
            A, B = ropes[p["rope"]]
            d = sub(B, A)
            Lr = norm(d)
            e = eye_dir(p["pitch"], p["yaw"])
            rev = next((u.get("rev") for u in p.get("sv_use", []) if u.get("result") == 1), None)
            out.append({"schedule": w["schedule"], "run": w["run"], "press_ground": p.get("pre_ground"),
                        "view_dot_rope": r(dot(e, d) / Lr, 4), "grip_minus_P_s": p.get("grip_minus_P_s"),
                        "ride_dir": p.get("ride_dir"), "sv_rev": rev})
    return out


def _g(S, sch, k=0):
    G = S.get(sch)
    return G["presses"][k] if G and len(G["presses"]) > k else None


def _pp(name, value, unit, cls, n, note=""):
    return {"name": name, "value": value, "unit": unit, "class": cls, "n": n, "note": note}


def build_params(S, B, DT, RT):
    """Unity-facing parameters with evidence class (meas / fit / src / inf) and n. Build = local hybrid (S21 client + S3 dedi + SDK)."""
    P = []
    P.append(_pp("find_cone_half_angle_bracket_deg", [r(B["max_success"][0], 3) if B["max_success"] else None,
                                                       r(B["min_failure"][0], 3) if B["min_failure"] else None],
                 "deg (largest mounted, smallest refused rule angle)", "fit", B["n_success"] + B["n_failure"],
                 "standing ground presses; angle between the eye direction and the min-angle rope point within 130 u of origin+72 "
                 "(M6-A3 rule); failures below the largest success: %d; M6-A3 bracket was 27.0-40.7" % B["failure_below_max_success"]))
    P.append(_pp("find_collector_distance_bracket", [B["collector_max_success"][0] if B["collector_max_success"] else None,
                                                      B["collector_min_failure"][0] if B["collector_min_failure"] else None],
                 "u, origin+72 -> nearest rope point (largest mounted, smallest refused)", "fit",
                 B["n_success"] + B["n_failure"], "consistent with the 120 u candidate collector (SDK comment); the 130 u point "
                 "search radius of M6-A3 still fits every grip point"))
    res = [p for d in DT for p in [d]]
    P.append(_pp("grip_point", "= the M6-A3 min-angle rope point (within 130 u of origin+72) at any position along the rope, incl. "
                 "mid-rope and at the anchors", "-", "meas", len(res), "see analysis_output §3 grip - rule residual"))
    fwd = [d for d in DT if d["view_dot_rope"] > 0.001 and d["press_ground"] == 1]
    rev = [d for d in DT if d["view_dot_rope"] < -0.001 and d["press_ground"] == 1]
    zero = [d for d in DT if abs(d["view_dot_rope"]) <= 0.001]
    P.append(_pp("ride_direction_rule", "sign(eye . rope_dir): > 0 -> toward the rope end, <= 0 (incl. exactly 0) -> toward the start; "
                 "dedi reverse flag = 1 for the start direction", "-", "meas", len(DT),
                 "dot>0: %s; dot<0: %s; dot=0: %s (ends excepted, see end_zone)" % (cnt([d["ride_dir"] for d in fwd]),
                 cnt([d["ride_dir"] for d in rev]), cnt([d["ride_dir"] for d in zero]))))
    g1, g2, g3 = _g(S, "m9z_r130_s166_l0_bx"), _g(S, "m9z_r130_s186_l0_bx"), _g(S, "m9z_r130_s226_l0_bx")
    if g1 and g2 and g3:
        P.append(_pp("end_zone_reverse", {"grip_s_from_end": [g1["grip_s"][0], g2["grip_s"][0], g3["grip_s"][0]],
                                           "ride_dir": [g1["ride_dir"], g2["ride_dir"], g3["ride_dir"]],
                                           "ride_s": [g1["ride_s"], g2["ride_s"], g3["ride_s"]]},
                     "u / - / s", "meas", g1["n"] + g2["n"] + g3["n"],
                     "a grip within ~90 u (between 70 and 110) of the end the view points to rides away from it; just outside, the ride "
                     "reaches the 90 u stop-short at once and auto-detaches at 600 (no end refusal in R5)"))
    sp = _g(S, "m9zd_sprint_mount")
    sl = _g(S, "m9zd_slide_mount_up")
    exs, exl = S.get("m9zd_sprint_mount", {}).get("extras", {}), S.get("m9zd_slide_mount_up", {}).get("extras", {})
    if sp and sl:
        P.append(_pp("ground_entry_speed_along_rope", {"sprint_first_ride_v": exs.get("v_first_ride_frame"),
                                                        "slide_first_ride_v": exl.get("v_first_ride_frame"),
                                                        "slide_v_0.5s": exl.get("v_ride_0.50s")},
                     "u/s", "meas", sp["n"] + sl["n"], "running / sliding along the rope: the speed along the rope is kept as the mount-state "
                     "floor (the M6-G grapple rule); 0.5 s later the normal +400 u/s^2 to 600"))
    for sch, key in (("m9zd_crouch_mount", "crouch_view0"), ("m9zd_crouch_mount_up", "crouch_view_up45"),
                     ("m9zd_slide_mount", "slide_view0"), ("m9zd_slide_mount_up", "slide_view_up45")):
        g = _g(S, sch)
        if g:
            P.append(_pp("mount_" + key, "%d/%d" % (g["mounted_sv"], g["n"]), "mounted", "meas", g["n"],
                         "rule angle %s; crouched (and sliding) the reach with a level view is shorter [cause unknown]" % g["rule_angle"]))
    air = [g for sch, G in S.items() if sch.startswith("m9zd_air") for g in G["presses"][:1]]
    if air:
        P.append(_pp("air_mount", "%d/%d accepted on client and dedi" % (sum(g["mounted_sv"] for g in air), sum(g["n"] for g in air)),
                     "-", "meas", sum(g["n"] for g in air), "standing jump under / 20-80 u beside the rope, view 0-80 deg off, use at "
                     "the apex / rising / held; same Find rule; Mid Air Interact works in this build"))
    jair = [g for sch, G in S.items() if sch.startswith("m9zd_r100_jair") for g in G["presses"][:1]]
    if jair:
        P.append(_pp("air_mount_height_gate", "none: mounted with origin+72 from %s below to %s above the rope" % (
                     max(g["rope_minus_P_z"][1] for g in jair), -min(g["rope_minus_P_z"][0] for g in jair)), "u", "meas",
                     sum(g["n"] for g in jair), "M6-A3 'rope must be above P' hypothesis rejected"))
    lk = {d["schedule"]: d for d in RT}
    fail_jo = max((d["dt_since_detach"] for d in RT if d["schedule"] == "m9zd_jo_spam" and not d["mounted_sv"] and d["k"] <= 10), default=None)
    ok_jo = min((d["dt_since_detach"] for d in RT if d["schedule"] == "m9zd_jo_spam" and d["mounted_sv"]), default=None)
    fail_dr = max((d["dt_since_detach"] for d in RT if d["schedule"].startswith("m9zd_lock_t") and not d["mounted_sv"]), default=None)
    ok_dr = min((d["dt_since_detach"] for d in RT if d["schedule"].startswith("m9zd_lock_t") and d["mounted_sv"]), default=None)
    P.append(_pp("remount_lockout_after_detach_s", {"jump_off": [fail_jo, ok_jo], "crouch_off": [fail_dr, ok_dr]},
                 "s (longest refused, shortest accepted)", "meas", sum(1 for d in RT if d["schedule"] in ("m9zd_jo_spam",) or
                 d["schedule"].startswith("m9zd_lock_t")),
                 "refused before Zipline_Use on the client (no diag line on either side): a native S21-client gate, independent of "
                 "height; wiki useZiplineCooldown 0.4"))
    P.append(_pp("regrab_ladder", "ground mount, then 2 air re-grabs (client cd 0.1 -> 0.2 -> 1.0 s); the 3rd air re-grab 0.42 s after "
                 "detach is refused; landing resets (cd 0.1, SDK left=3)", "-", "meas",
                 sum(1 for d in RT if d["schedule"].startswith("m9zd_budget_jo")),
                 "the S21 client cooldown (1.0 s after the 3rd grant) and the SDK hop-regrab count (3, 'latest Apex') refuse together "
                 "here; the 3 s refill was not tested"))
    for k in (12, 18, 24, 30):
        G = S.get("m9zd_sj_k%d" % k)
        if G:
            sj = G["extras"].get("second_jump", [])
            P.append(_pp("super_jump_k%d" % k, "%d/%d applied" % (sum(1 for x in sj if x), len(sj)), "-", "meas", len(sj),
                         "jump-off on the command after the mount, second press K commands later"))
    jl, jc = S.get("m9zd_jo_lurch", {}).get("extras", {}), S.get("m9zd_jo_ctrl", {}).get("extras", {})
    if jl:
        P.append(_pp("lurch_after_jumpoff", jl.get("dv_press_abs"), "|dv| u/s on the D press 3 cmds after the jump-off", "meas",
                     jl.get("dv_press_abs", {}).get("n"), "AirAccelerate only (4.17 = 500 dt): a zipline jump-off does not open the lurch window"))
    for sch in ("m9zd_carry3_j1", "m9zd_carry3_j3"):
        G = S.get(sch)
        if G:
            P.append(_pp("carry_" + sch[-2:], G["extras"].get("v_after_exit3"), "u/s (3 frames after the exit)", "meas", G["n"],
                         "run across the rope (+Y, ~285 u/s), use, jump on the next command (j1) / 2 commands later (j3)"))
    v = S.get("m9zd_turn180", {}).get("extras", {}).get("v_along_yaw")
    if v:
        P.append(_pp("direction_locked_during_ride", v[0], "[t, v along rope, yaw]", "meas", len(v),
                     "a 180 deg view turn after the mount state does not reverse the ride"))
    for sch, key in (("m9zv_ledge_up", "vertical_mid_up"), ("m9zv_ledge_p0", "vertical_mid_level"), ("m9zv_ledge_dn", "vertical_mid_down"),
                     ("m9zv_floor_dn", "vertical_floor_down"), ("m9zv_ledge_turn", "vertical_turn_down_after_mount"),
                     ("m9zv_floor_air", "vertical_air"), ("m9zv_ledge_air", "vertical_ledge_air")):
        g = _g(S, sch)
        if g:
            P.append(_pp(key, {"client": g["mounted_cl"], "dedi": g["mounted_sv"], "dir": g["ride_dir"], "ride_s": g["ride_s"]},
                         "count / dir / s", "meas", g["n"], "vertical rope (CreateZipline, |dir.z|>0.7)"))
    for sch in ("m9z_r80_p50_l0_fx", "m9z_r200_p50_l0_up", "m9z_r240_p50_l0_up", "m9z_r170_p50_l0_up"):
        g = _g(S, sch)
        if g:
            P.append(_pp("height_" + sch.split("_")[1], "%d/%d" % (g["mounted_sv"], g["n"]), "mounted", "meas", g["n"],
                         "rope height above the floor = %s; origin+72 -> rope %s" % (sch.split("_")[1][1:], g["P_to_rope"])))
    return P


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    ap.add_argument("--trials", action="store_true", help="also print every press as JSON")
    a = ap.parse_args(argv)
    rows, metas, ropes_by_session = [], [], {}
    for folder in a.sessions:
        D = Z.load(folder)
        ropes = ropes_of(D["runner"])
        ropes_by_session[D["folder"]] = ropes
        excl = [(t["run"], t["schedule"], t["why"]) for t in D["runner"]["trials"] if not t["ok"] and not t.get("warmup")]
        metas.append({"session": D["folder"], "geometry": D["runner"].get("geometry_zip"), "scored": len(D["trials"]),
                      "excluded": excl, "zip_lines": D["zip_lines"],
                      "fps": [r(min(t["fps"] for t in D["trials"]), 2), r(max(t["fps"] for t in D["trials"]), 2)] if D["trials"] else None})
        for T in D["trials"]:
            rows.append(trial_row(T, ropes, D["folder"]))
    print("M9 R zipline A1 (R5Flowstate S21 client + S3 dedi + SDK, local offline)")
    print("=" * 100)
    print("\n1. Sessions")
    for m in metas:
        print("  %s  geometry=%s scored=%d fps=%s excluded=%s diag lines=%s" % (m["session"], m["geometry"], m["scored"], m["fps"],
              m["excluded"] or "none", m["zip_lines"]))
    S = summarise(rows)
    print("\n2. Per schedule and use press (k = press index; mounted cl/sv = client zip flag / dedi [ZIPRAIL-USE] result=1)")
    for sch, G in S.items():
        print("\n  %s  n=%d  mounts without a press=%d" % (sch, G["n"], G["mount_without_press"]))
        for k, g in enumerate(G["presses"]):
            print("    k%d n=%d mounted cl %d sv %d | ground %s z+%s | yaw/pitch %s | P->rope %s rope-Pz %s P_along %s | rule angle %s"
                  % (k, g["n"], g["mounted_cl"], g["mounted_sv"], g["pre_ground"], g["z_above_floor"], g["yaw_pitch"], g["P_to_rope"],
                     g["rope_minus_P_z"], g["P_along"], g["rule_angle"]))
            print("        grip_s %s grip-rule %s grip-P %s | dir %s sv rev %s | exit %s at s %s v_exit %s ride %s s"
                  % (g["grip_s"], g["grip_minus_rule_s"], g["grip_minus_P_s"], g["ride_dir"], g["sv_rev"], g["exit"], g["exit_s"],
                     g["v_exit"], g["ride_s"]))
            print("        client Use lines %s  disc %s" % (g["cl_use_lines"], g["disc"]))
        if G["extras"]:
            print("    extras: %s" % json.dumps(G["extras"]))
    B = find_bracket(rows)
    print("\n3. Find rule (M6-A3: min angle within 130 u of origin+72), standing ground presses (first press of m9z_ schedules)")
    print("  cone (rope within 120 u of origin+72, r80 excluded): success n=%d, largest rule angle %s" % (B["n_success"], B["max_success"]))
    print("  cone: failure n=%d, smallest rule angle %s; failures below the largest success: %d" % (B["n_failure"], B["min_failure"],
          B["failure_below_max_success"]))
    print("  collector (rule angle <= 33.2): largest origin+72 -> rope distance mounted %s; smallest refused %s; refused below: %d"
          % (B["collector_max_success"], B["collector_min_failure"], B["collector_failure_below_max_success"]))
    print("  r80 rope (hang point at floor level): mounted %d of %d" % (B["r80"]["mounted"], B["r80"]["n"]))
    print("  schedules with no rope point within 130 u: %s" % (B["no_point_within_130"] or "none"))
    res = [p["grip_minus_rule_s"] for w in rows for p in w["presses"] if p.get("grip_minus_rule_s") is not None and p.get("pre_ground") == 1]
    if res:
        print("  grip - rule point along the rope (ground mounts with a dedi use position): mean %s, |max| %s, n=%d"
              % (mean(res), r(max(abs(x) for x in res), 2), len(res)))
    DT = direction_table(rows, ropes_by_session)
    print("\n4. Ride direction vs the view (view . rope direction, start -> end)")
    agg = {}
    for d in DT:
        key = (d["schedule"], d["view_dot_rope"])
        agg.setdefault(key, []).append(d)
    for (sch, vd), ds in sorted(agg.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        print("  %-30s view.rope %+.4f  dir %s  sv rev %s  grip-P %s" % (sch, vd, cnt([d["ride_dir"] for d in ds]),
              cnt([d["sv_rev"] for d in ds]), span([d["grip_minus_P_s"] for d in ds])))
    RT = remount_table(rows)
    print("\n5. Later presses in a trial (re-mounts): time since the previous ride ended")
    agg = {}
    for d in RT:
        agg.setdefault((d["schedule"], d["k"]), []).append(d)
    for (sch, k), ds in sorted(agg.items()):
        print("  %-26s k%d dt %s ground %s mounted cl %d sv %d | client Use line %d | client cd after previous grant %s | rope-Pz %s | disc %s"
              % (sch, k, span([d["dt_since_detach"] for d in ds]), cnt([d["ground"] for d in ds]), sum(d["mounted_cl"] for d in ds),
                 sum(d["mounted_sv"] for d in ds), sum(d["client_use_line"] for d in ds), cnt([d["cd_after_prev_grant"] for d in ds]),
                 span([d["rope_minus_P_z"] for d in ds]), cnt([",".join(d["disc"] or []) or "-" for d in ds])))
    if a.trials:
        print("\n6. Every press")
        for w in rows:
            print("r%s %s segs=%s extras=%s" % (w["run"], w["schedule"], w["zip_segments"], json.dumps(w["extras"])))
            for p in w["presses"]:
                print("   ", json.dumps(p))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sessions": metas, "groups": S, "find_bracket": B, "direction": DT, "remounts": RT,
                       "trials": [dict(w, presses=[{k: v for k, v in p.items() if k != "sv_find"} for p in w["presses"]]) for w in rows]},
                      fh, indent=None, separators=(",", ":"))
    if a.params:
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"build": "R5Flowstate S21 client + S3 dedicated server + SDK, local offline, 120 fps, Gibraltar",
                       "params": build_params(S, B, DT, RT)}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
