#!/usr/bin/env python3
"""M9 track R ② Revenant: shadow pounce grid, pull-out / cancel / air press, landing, lurch after a pounce, wall contact,
climb (R5Flowstate S21 client + S3 dedi + SDK, local offline).

  py -3 rev_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py): client first-time MOVE-TRACE usercmds
joined to client HSD frames (post-state per usercmd), client [HSD-STATE] flags.

Per trial:
- press / release   = schedule offhand1 down / up edges (client game time);
- launch            = the first usercmd after the press whose post |v| exceeds its pre |v| by > 300 u/s (the pounce replaces the
                      velocity); launch vector = (post vx, post vy, post vz + g dt / 2) (removes the half gravity step, M4);
- model (script mp_ability_revenant_shadow_pounce_free.nut, M4): c = clamp((t_release - t_press - 0.9) / 1.3, 0, 1) (release after
  the 0.9 s pull-out, else 0); pitch p (+ = down); if p >= 20 and the ground is within 200 u along the view: p = 15;
  -15 <= p <= 75: p' = p - 35, div 1; p < -15: p' = p - 35 * (1 - f), div = 1 + 0.5 f, f = clamp((p + 15) / -65, 0, 1);
  v = (700 + 450 c) / div along (p', yaw). The ground check is evaluated as 'flat floor' (eye 60 u above it) or 'ledge' runs;
- landing           = the first grounded usercmd after the launch: |v_h| before and 0.1 / 0.25 / 0.5 s after;
- lurch             = |dv_h| on the usercmd of a moveright press after the launch (control: the same usercmd index, no press);
- wall              = first usercmd after the launch whose post |v_h| < 100 from pre > 300; climb start = first wr=true state.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

G = 750.0
FLOOR = 294.92
IN_FORWARD = 0x8
IN_JUMP = 0x2
EYE = 60.0


def r(x, n=3):
    return None if x is None else round(x, n)


def edges(T, key, edge):
    out = []
    for l in T["sched_lines"]:
        if ("edge=%s" % edge) in l and ("key=%s " % key) in l:
            out.append(float(next(tok[2:] for tok in l.split() if tok.startswith("t="))))
    return out


def vmag(c, post=True):
    if post:
        return math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2)
    return math.sqrt(c["vx"] ** 2 + c["vy"] ** 2 + c["vz"] ** 2)


def model(pitch, yaw, hold, ground_hit):
    c = max(0.0, min(1.0, (hold - 0.9) / 1.3)) if hold is not None and hold > 0.9 else 0.0
    p = pitch
    if p >= 20 and ground_hit:
        p = 15.0
    if -15 <= p <= 75:
        pp, div = p - 35, 1.0
    elif p < -15:
        f = max(0.0, min(1.0, (p + 15) / -65.0))
        pp, div = p - 35 * (1 - f), 1 + 0.5 * f
    else:
        pp, div = p, 1.0
    v = (700 + 450 * c) / div
    pr, yr = math.radians(pp), math.radians(yaw)
    return {"c": r(c, 4), "pitch_used": r(p, 2), "pitch_launch": r(pp, 3), "speed": r(v, 3),
            "vec": [r(v * math.cos(pr) * math.cos(yr), 3), r(v * math.cos(pr) * math.sin(yr), 3), r(-v * math.sin(pr), 3)]}


def ground_hit_flat(pitch):
    """Flat floor, eye 60 u above it: the view ray meets the floor within 200 u when pitch > asin(60 / 200)."""
    return pitch > 0 and EYE / math.sin(math.radians(pitch)) <= 200.0


def trial_row(T, session):
    cmds = [c for c in T["cmds"] if c.get("t") is not None]
    sch = T["schedule"]
    row = {"session": session, "run": T["run"], "schedule": sch, "fps": T["fps"]}
    dn, up = edges(T, "offhand1", "down"), edges(T, "offhand1", "up")
    if not dn:
        return row
    tp = dn[0]
    tr = up[0] if up else None
    hold = (tr - tp) if tr is not None else None
    row["hold"] = r(hold, 3)
    launch = None
    for c in cmds:
        if c["t"] > tp + 1e-6 and vmag(c) - vmag(c, post=False) > 300:
            launch = c
            break
    pre = cmds[cmds.index(launch) - 1] if launch and cmds.index(launch) > 0 else None
    f0 = next((f for f in T["frames"] if f.get("pitch") is not None and f["t"] <= tp), None)
    fr = [f for f in T["frames"] if f.get("pitch") is not None and f["t"] <= (launch["t"] if launch else tp) + 1e-6]
    fv = fr[-1] if fr else f0
    row["press_ground"] = None
    if not launch:
        row["launched"] = False
        return row
    # heading / speed after a tap strafe (m9r_ts_*) or turn-only control (m9r_turn_*): v_h 0.1 / 0.25 / 0.4 s after the launch
    if sch.startswith(("m9r_ts_", "m9r_turn_")):
        h0 = math.degrees(math.atan2(launch["pvy"], launch["pvx"]))
        s0 = math.hypot(launch["pvx"], launch["pvy"])
        hd = {}
        for tt in (0.1, 0.25, 0.4):
            c2 = next((c for c in cmds if c["t"] >= launch["t"] + tt - 1e-6), None)
            if c2:
                hd["%.2f" % tt] = [r((math.degrees(math.atan2(c2["pvy"], c2["pvx"])) - h0 + 180) % 360 - 180, 2),
                                   r(math.hypot(c2["pvx"], c2["pvy"]) / s0, 4), r(c2.get("yaw"), 1)]
        row["ts_heading"] = hd
        fw = [c for c in cmds if c["t"] > launch["t"] and c["buttons"] & IN_FORWARD and
              not cmds[cmds.index(c) - 1]["buttons"] & IN_FORWARD and not c["ground"]]
        row["ts_w_edges"] = len(fw)
        row["ts_max_dv_on_w_edge"] = r(max((math.hypot(c["pvx"] - c["vx"], c["pvy"] - c["vy"]) for c in fw), default=0.0), 3)
    row["launched"] = True
    dt = launch["dt"] or 1 / 120.0
    vec = [launch["pvx"], launch["pvy"], launch["pvz"] + 0.5 * G * dt]
    sp = math.sqrt(sum(x * x for x in vec))
    vh = math.hypot(vec[0], vec[1])
    row.update(t_launch_after_press=r(launch["t"] - tp, 4), t_launch_after_release=r(launch["t"] - tr, 4) if tr is not None else None,
               launch_vec=[r(x, 3) for x in vec], launch_speed=r(sp, 3), launch_elev=r(math.degrees(math.atan2(vec[2], vh)), 3),
               launch_heading=r(math.degrees(math.atan2(vec[1], vec[0])), 3), pre_ground=launch["ground"],
               pre_v=[r(pre["pvx"], 2), r(pre["pvy"], 2), r(pre["pvz"], 2)] if pre else None,
               pre_speed_h=r(math.hypot(pre["pvx"], pre["pvy"]), 2) if pre else None,
               view=[r(fv["pitch"], 3), r(fv["yaw"], 3)] if fv else None)
    if fv:
        hit = "ledge" not in sch and ground_hit_flat(fv["pitch"])
        m = model(fv["pitch"], fv["yaw"], hold, hit)
        row["model"] = m
        row["model_err_speed"] = r(sp - m["speed"], 3)
        row["model_err_vec"] = r(math.sqrt(sum((a - b) ** 2 for a, b in zip(vec, m["vec"]))), 3)
    # landing
    k = cmds.index(launch)
    land = next((c for c in cmds[k + 2:] if c["ground"]), None)
    if land:
        j = cmds.index(land)
        b = cmds[j - 1]
        row["air_time"] = r(land["t"] - launch["t"], 4)
        row["land_vh_before"] = r(math.hypot(b["pvx"], b["pvy"]), 2)
        row["land_vz_before"] = r(b["pvz"], 2)
        for tt in (0.1, 0.25, 0.5):
            c2 = next((c for c in cmds[j:] if c["t"] >= land["t"] + tt - 1e-6), None)
            if c2:
                row["land_vh_%.2fs" % tt] = r(math.hypot(c2["pvx"], c2["pvy"]), 2)
        row["land_vh_first"] = r(math.hypot(land["pvx"], land["pvy"]), 2)
    # lurch press after the launch
    md = [t for t in edges(T, "moveright", "down") if t > launch["t"]]
    after = cmds[k + 1:]
    if md:
        c = next((c for c in after if c["t"] >= md[0] - 1e-6), None)
    elif "lurch_ctrl" in sch and len(after) > 3:
        c = after[3]
    else:
        c = None
    if c:
        row["lurch"] = {"t_after_launch": r(c["t"] - launch["t"], 4),
                        "dv": [r(c["pvx"] - c["vx"], 3), r(c["pvy"] - c["vy"], 3)],
                        "dv_abs": r(math.hypot(c["pvx"] - c["vx"], c["pvy"] - c["vy"]), 3),
                        "v_h": r(math.hypot(c["vx"], c["vy"]), 2)}
    # wall contact / climb
    con = next((c for c in after if L.hs(c, post=False) > 300 and L.hs(c) < 100), None)
    wr = next((s["t"] for s in T["states"] if s.get("wr") and s["t"] > launch["t"]), None)
    if con:
        row["contact_after_launch"] = r(con["t"] - launch["t"], 4)
        row["contact_z"] = r(con["poz"] - FLOOR, 2)
        row["contact_v"] = [r(con["vx"], 2), r(con["vy"], 2), r(con["vz"], 2)]
        row["post_contact_v"] = [r(con["pvx"], 2), r(con["pvy"], 2), r(con["pvz"], 2)]
    if wr is not None:
        row["climb_after_launch"] = r(wr - launch["t"], 4)
    # jump press after the launch (wall bounce inside the climb lock)
    jd = [t for t in edges(T, "jump", "down") if t > launch["t"]]
    if jd:
        c = next((c for c in after if c["t"] >= jd[0] - 1e-6), None)
        if c:
            row["jump_press"] = {"t_after_launch": r(c["t"] - launch["t"], 4), "pre_v": [r(c["vx"], 2), r(c["vy"], 2), r(c["vz"], 2)],
                                 "post_v": [r(c["pvx"], 2), r(c["pvy"], 2), r(c["pvz"], 2)], "ground": c["ground"],
                                 "wr_at_press": any(s.get("wr") and abs(s["t"] - c["t"]) < 0.02 for s in T["states"])}
    return row


def climb_row(T, session):
    """Trials without a pounce (m9r_climb_*, m9r_wall_bounce_ctrl): climb segments (client wr flag), lateral speed while a side key
    is held, and the velocity change on jump / back presses."""
    cmds = [c for c in T["cmds"] if c.get("t") is not None]
    row = {"session": session, "run": T["run"], "schedule": T["schedule"], "fps": T["fps"], "launched": False}
    segs, cur = [], None
    for st in T["states"]:
        if st.get("wr"):
            cur = [st["t"], st["t"]] if cur is None else [cur[0], st["t"]]
        elif cur is not None:
            segs.append(cur)
            cur = None
    if cur is not None:
        segs.append(cur)
    row["wr_segments"] = [[r(a, 4), r(b, 4)] for a, b in segs]
    if segs:
        t0, t1 = segs[0]
        ins = [c for c in cmds if t0 <= c["t"] <= t1]
        if ins:
            row["climb"] = {"dur": r(t1 - t0, 4), "z0": r(ins[0]["poz"] - FLOOR, 2), "z1": r(max(c["poz"] for c in ins) - FLOOR, 2)}
    trav = [st["t"] for st in T["states"] if st.get("trav")]
    row["traversal_t"] = [r(min(trav), 4), r(max(trav), 4)] if trav else None
    md = edges(T, "moveright", "down")
    mu = edges(T, "moveright", "up")
    if md:
        ins = [c for c in cmds if md[0] + 0.1 <= c["t"] <= (mu[0] if mu else md[0] + 1.0)]
        row["side_hold"] = {"vy_mean": r(sum(c["pvy"] for c in ins) / len(ins), 2) if ins else None,
                            "dy": r(ins[-1]["poy"] - ins[0]["oy"], 2) if ins else None,
                            "wr_during": sum(1 for st in T["states"] if st.get("wr") and md[0] <= st["t"] <= (mu[0] if mu else md[0] + 1.0)),
                            "vz_mean": r(sum(c["pvz"] for c in ins) / len(ins), 2) if ins else None}
    out = []
    for key in ("jump", "backward"):
        for te in edges(T, key, "down"):
            c = next((c for c in cmds if c["t"] >= te - 1e-6), None)
            if not c:
                continue
            k = cmds.index(c)
            c2 = next((q for q in cmds[k:] if q["t"] >= c["t"] + 0.1 - 1e-6), None)
            out.append({"key": key, "t": r(te, 4), "wr_at": any(st.get("wr") and abs(st["t"] - c["t"]) < 0.02 for st in T["states"]),
                        "ground": c["ground"], "z": r(c["oz"] - FLOOR, 2), "pre_v": [r(c["vx"], 2), r(c["vy"], 2), r(c["vz"], 2)],
                        "post_v": [r(c["pvx"], 2), r(c["pvy"], 2), r(c["pvz"], 2)],
                        "v_0.1s": [r(c2["pvx"], 2), r(c2["pvy"], 2), r(c2["pvz"], 2)] if c2 else None})
    row["presses"] = out
    return row


def stats(v):
    return L.stats(v)


def fmt(s, nd=3):
    return L.fmt(s, nd)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    rows, metas = [], []
    for folder in a.sessions:
        D = L.load(folder)
        excl = [(t["run"], t["schedule"], t["why"]) for t in D["runner"]["trials"] if not t["ok"] and not t.get("warmup")]
        metas.append({"session": D["folder"], "legend": D["runner"].get("legend"), "scored": len(D["trials"]), "excluded": excl,
                      "fps": [r(min(t["fps"] for t in D["trials"]), 2), r(max(t["fps"] for t in D["trials"]), 2)] if D["trials"] else None})
        for T in D["trials"]:
            if T["schedule"].startswith(("m9r_climb", "m9r_wall_bounce_ctrl")):
                rows.append(climb_row(T, D["folder"]))
            elif T["schedule"].startswith("m9r_"):
                rows.append(trial_row(T, D["folder"]))
    print("M9 R Revenant (R5Flowstate S21 client + S3 dedi + SDK, local offline)")
    print("=" * 100)
    print("\n1. Sessions")
    for m in metas:
        print("  %s legend=%s scored=%d fps=%s excluded=%s" % (m["session"], m["legend"], m["scored"], m["fps"], m["excluded"] or "none"))
    groups = {}
    for w in rows:
        groups.setdefault(w["schedule"], []).append(w)
    S = {}
    print("\n2. Per schedule (launch vector = post v + g dt/2 on the launch usercmd; model = script formula)")
    keys = ("hold", "t_launch_after_press", "t_launch_after_release", "pre_speed_h", "launch_speed", "launch_elev", "model_err_speed",
            "model_err_vec", "air_time", "land_vh_before", "land_vh_first", "land_vh_0.10s", "land_vh_0.25s", "land_vh_0.50s",
            "contact_after_launch", "contact_z", "climb_after_launch")
    for sch in sorted(groups):
        ws = groups[sch]
        g = {"n": len(ws), "launched": sum(1 for w in ws if w.get("launched"))}
        for k in keys:
            s = stats([w.get(k) for w in ws])
            if s["n"]:
                g[k] = s
        m = next((w["model"] for w in ws if w.get("model")), None)
        g["model"] = m
        g["view"] = next((w["view"] for w in ws if w.get("view")), None)
        lu = [w["lurch"]["dv_abs"] for w in ws if w.get("lurch")]
        if lu:
            g["lurch_dv_abs"] = stats(lu)
        jp = [w["jump_press"] for w in ws if w.get("jump_press")]
        if jp:
            g["jump_press"] = jp
        g["launch_vec"] = [w.get("launch_vec") for w in ws]
        S[sch] = g
        print("\n  %s  n=%d launched=%d view=%s" % (sch, g["n"], g["launched"], g["view"]))
        if m:
            print("    model: c %s pitch used %s -> launch pitch %s speed %s vec %s" % (m["c"], m["pitch_used"], m["pitch_launch"], m["speed"],
                  m["vec"]))
        for k in keys:
            if k in g:
                print("    %-24s %s" % (k, fmt(g[k], 3)))
        if lu:
            print("    %-24s %s" % ("lurch |dv_h|", fmt(g["lurch_dv_abs"], 3)))
        for j in jp:
            print("    jump press %s" % json.dumps(j))
        th = [w["ts_heading"] for w in ws if w.get("ts_heading")]
        if th:
            g["ts_heading"] = th
            g["ts_max_dv_on_w_edge"] = stats([w.get("ts_max_dv_on_w_edge") for w in ws])
            print("    heading/speed ratio/yaw after the launch: %s" % json.dumps(th))
            print("    max |dv_h| on a W edge: %s (W edges in the air %s)" % (fmt(g["ts_max_dv_on_w_edge"], 3), [w.get("ts_w_edges") for w in ws]))
        cl = [w for w in ws if "wr_segments" in w]
        if cl:
            g["climb_rows"] = cl
            for w in cl:
                print("    r%s wr %s climb %s trav %s side %s presses %s" % (w["run"], w["wr_segments"], w.get("climb"), w.get("traversal_t"),
                      w.get("side_hold"), json.dumps(w["presses"])))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sessions": metas, "groups": S, "trials": rows}, fh, indent=1)
    if a.params:
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"build": "R5Flowstate S21 client + S3 dedicated server + SDK, local offline, 120 fps, Revenant (kit)",
                       "params": build_params(S)}, fh, indent=1)
    return 0


def build_params(S):
    P = []
    grid = [g for k, g in S.items() if k.startswith("m9r_p") and "model_err_speed" in g]
    if grid:
        errs = [abs(x) for g in grid for x in (g["model_err_speed"]["min"], g["model_err_speed"]["max"])]
        verr = [g["model_err_vec"]["max"] for g in grid]
        P.append({"name": "pounce_formula_grid", "value": "v = (700 + 450 c)/div along (p', yaw), M4 + script rules",
                  "n": sum(g["n"] for g in grid), "class": "fit",
                  "note": "max |speed error| %.2f u/s, max vector error %.2f u/s over the pitch x charge x start grid" % (max(errs), max(verr))})
    for k, g in sorted(S.items()):
        ent = {"name": k, "n": g["n"], "class": "meas", "launched": g["launched"]}
        for f in ("t_launch_after_press", "launch_speed", "launch_elev", "pre_speed_h", "land_vh_first", "land_vh_0.25s", "lurch_dv_abs",
                  "contact_after_launch", "climb_after_launch", "air_time"):
            if f in g:
                ent[f] = r(g[f]["mean"], 3)
        if g.get("model"):
            ent["model_speed"] = g["model"]["speed"]
            ent["model_pitch_launch"] = g["model"]["pitch_launch"]
        P.append(ent)
    return P


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
