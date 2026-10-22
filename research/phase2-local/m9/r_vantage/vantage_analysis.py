#!/usr/bin/env python3
"""M9 track R ④ Vantage: Echo placement / launch conditions with the real tactical, and jet-drive end-jump window, lurch and
wall collision with the M8 shortcut (R5Flowstate S21 client + S3 dedi + SDK, local offline).

  py -3 vantage_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader: ../../m6/a2_climb/a2_load.py. Schedules m9v_* (tools/hsd_trial.py).
- Server lines: [HSD-RESET] (run, server time t=), [R2-ECHO] (10 Hz Echo / player origin, jet drive flag; logger started by the
  m9v_ reset after a recall), [R2-JD] (shortcut drive begin: player, target mover, timeout). Server lines are assigned to the
  run whose reset precedes them (server clock).
- Real tactical trials: press / release of offhand1 (client schedule edges); launched = a client usercmd with post |v| > 500
  after the hold press; t_launch_after_hold / _after_release; Echo position before the hold (last log line before the
  first jet-drive flag or the end): distance from the player, height above the floor, horizontal angle between the view yaw at
  the hold press and the player -> Echo direction.
- Shortcut trials: jump press after the lift-off: applied if post vz - pre vz > 200; distance to the target point (mover - 69 u,
  M8) at the press; time after the lift-off; lurch |dv_h| on a later moveright press; wall: the lowest |v| after the launch and
  where it happened.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

FLOOR = 294.92
IN_JUMP, IN_MOVERIGHT = 0x2, 0x400
VEC = r"<\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*>"
JD_RE = re.compile(r"\[R2-JD\] begin t=([\d.]+) o=" + VEC + r" tgt=" + VEC + r" timeout=([\d.]+)")
ECHO_RE = re.compile(r"\[R2-ECHO\] t=([\d.]+) valid=(\w+) o=" + VEC + r" p=" + VEC + r" jd=(\w+)")
RESET_RE = re.compile(r"\[HSD-RESET\] ver=1 batch=(\d+) run=(\d+) .* t=([\d.]+)")


def r(x, n=3):
    return None if x is None else round(x, n)


def vlen(v):
    return math.sqrt(sum(a * a for a in v))


def server_lines(folder):
    jd, echo, resets = [], [], []
    for f in L._files(folder, "server", "script"):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                m = RESET_RE.search(raw)
                if m:
                    resets.append((float(m.group(3)), int(m.group(2))))
                    continue
                m = JD_RE.search(raw)
                if m:
                    g = [float(x) for x in m.groups()]
                    jd.append({"t": g[0], "o": g[1:4], "tgt": g[4:7], "timeout": g[7]})
                    continue
                m = ECHO_RE.search(raw)
                if m:
                    g = m.groups()
                    echo.append({"t": float(g[0]), "valid": g[1] == "true", "echo": [float(x) for x in g[2:5]],
                                 "p": [float(x) for x in g[5:8]], "jd": g[8] == "true"})
    resets = sorted(set(resets))
    return jd, echo, resets


def assign(lines, resets):
    out = {}
    ts = [t for t, _ in resets]
    for d in lines:
        i = max((k for k, t in enumerate(ts) if t <= d["t"]), default=None)
        if i is not None:
            out.setdefault(resets[i][1], []).append(d)
    return out


def edges(T, key, edge):
    return [float(next(tok[2:] for tok in l.split() if tok.startswith("t="))) for l in T["sched_lines"]
            if ("edge=%s" % edge) in l and ("key=%s " % key) in l]


def real_row(T, echo):
    cmds = [c for c in T["cmds"] if c.get("t") is not None]
    row = {"run": T["run"], "schedule": T["schedule"]}
    dn, up = edges(T, "offhand1", "down"), edges(T, "offhand1", "up")
    row["n_presses"] = len(dn)
    hold = None
    for a, b in zip(dn, up):
        if b - a > 0.05:
            hold = (a, b)
    if hold is None and dn:
        hold = (dn[-1], up[-1] if up else None)
    if hold:
        row["hold_s"] = r(hold[1] - hold[0], 3) if hold[1] else None
    la = next((c for c in cmds if hold and c["t"] > hold[0] and vlen((c["pvx"], c["pvy"], c["pvz"])) > 500.0), None)
    row["launched"] = la is not None
    if la:
        row["t_launch_after_hold"] = r(la["t"] - hold[0], 4)
        row["t_launch_after_release"] = r(la["t"] - hold[1], 4) if hold[1] else None
        row["launch_speed"] = r(vlen((la["pvx"], la["pvy"], la["pvz"])), 2)
    jd_lines = [e for e in echo if e["jd"]]
    row["echo_log_lines"] = len(echo)
    row["jd_flag_lines"] = len(jd_lines)
    pre = [e for e in echo if e["valid"] and not e["jd"]]
    if jd_lines:
        pre = [e for e in pre if e["t"] < jd_lines[0]["t"]]
    if pre:
        e = pre[-1]
        d = [e["echo"][i] - e["p"][i] for i in range(3)]
        row["echo_rel"] = [r(x, 1) for x in d]
        row["echo_dist"] = r(vlen(d), 1)
        row["echo_dist_h"] = r(math.hypot(d[0], d[1]), 1)
        row["echo_z_above_floor"] = r(e["echo"][2] - FLOOR, 1)
        # settle: the first log line after which the Echo moves < 5 u per line for the rest of the pre-launch log
        ms = [vlen([pre[k + 1]["echo"][i] - pre[k]["echo"][i] for i in range(3)]) for k in range(len(pre) - 1)]
        k_set = next((k for k in range(len(ms)) if all(m < 5.0 for m in ms[k:])), None)
        row["echo_settle_t"] = r(pre[k_set]["t"] - pre[0]["t"], 2) if k_set is not None else None
        if hold:
            f = min(T["frames"], key=lambda f: abs(f["t"] - hold[0])) if T["frames"] else None
            if f and f.get("yaw") is not None:
                ang = math.degrees(math.atan2(d[1], d[0]))
                row["view_to_echo_deg"] = r(((ang - f["yaw"] + 180) % 360) - 180, 1)
                el = math.degrees(math.atan2(d[2] - 60.0, math.hypot(d[0], d[1])))
                row["view_to_echo_3d_deg"] = r(math.degrees(math.acos(max(-1.0, min(1.0,
                    math.cos(math.radians(el)) * math.cos(math.radians(-f["pitch"])) * math.cos(math.radians(ang - f["yaw"])) +
                    math.sin(math.radians(el)) * math.sin(math.radians(-f["pitch"])))))), 1)
    return row


def jd_row(T, jdl):
    cmds = [c for c in T["cmds"] if c.get("t") is not None]
    row = {"run": T["run"], "schedule": T["schedule"]}
    i0 = next((i for i, c in enumerate(cmds) if vlen((c["pvx"], c["pvy"], c["pvz"])) > 500.0), None)
    row["launched"] = i0 is not None
    if i0 is None:
        return row
    tL = cmds[i0]["t"]
    start = (cmds[i0 - 1]["pox"], cmds[i0 - 1]["poy"], cmds[i0 - 1]["poz"]) if i0 else (cmds[0]["ox"], cmds[0]["oy"], cmds[0]["oz"])
    tgt = None
    if jdl:
        g = jdl[0]["tgt"]
        tgt = (g[0], g[1], g[2] - 69.0)
        row["target_dist0"] = r(vlen([tgt[k] - start[k] for k in range(3)]), 1)
    jp = [t for t in edges(T, "jump", "down") if t > tL]
    if jp:
        c = next((c for c in cmds if c["t"] >= jp[0] - 1e-6), None)
        if c:
            row["jump"] = {"t_after_liftoff": r(c["t"] - tL, 4), "applied": c["pvz"] - c["vz"] > 200,
                           "pre_v": [r(c["vx"], 1), r(c["vy"], 1), r(c["vz"], 1)], "post_v": [r(c["pvx"], 1), r(c["pvy"], 1), r(c["pvz"], 1)],
                           "dist_to_target": r(vlen([c["ox"] - tgt[k] if k == 0 else (c["oy"] - tgt[1] if k == 1 else c["oz"] - tgt[2])
                                                     for k in range(3)]), 1) if tgt else None,
                           "along_past_target": None}
            if tgt:
                u = (tgt[0] - start[0], tgt[1] - start[1])
                un = math.hypot(*u) or 1.0
                row["jump"]["along_past_target"] = r(((c["ox"] - start[0]) * u[0] + (c["oy"] - start[1]) * u[1]) / un - un, 1)
            k = cmds.index(c)
            md = [t for t in edges(T, "moveright", "down") if t > c["t"]]
            if md:
                c2 = next((q for q in cmds[k + 1:] if q["t"] >= md[0] - 1e-6), None)
                if c2:
                    row["lurch"] = {"t_after_jump": r(c2["t"] - c["t"], 4), "dv_abs": r(math.hypot(c2["pvx"] - c2["vx"], c2["pvy"] - c2["vy"]), 3)}
            elif len(cmds) > k + 3:
                c2 = cmds[k + 3]
                row["lurch_ctrl"] = {"dv_abs": r(math.hypot(c2["pvx"] - c2["vx"], c2["pvy"] - c2["vy"]), 3)}
    # lowest speed in the first 1.5 s after the lift-off (wall collision)
    win = [c for c in cmds[i0:] if c["t"] <= tL + 1.5 and not c["ground"]]
    if win:
        lo = min(win, key=lambda c: vlen((c["pvx"], c["pvy"], c["pvz"])))
        row["min_speed"] = r(vlen((lo["pvx"], lo["pvy"], lo["pvz"])), 1)
        row["min_speed_t"] = r(lo["t"] - tL, 4)
        row["min_speed_pos"] = [r(lo["pox"], 1), r(lo["poy"], 1), r(lo["poz"] - FLOOR, 1)]
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
    metas, rows = [], []
    for folder in a.sessions:
        D = L.load(folder)
        jd, echo, resets = server_lines(folder)
        jd_by, echo_by = assign(jd, resets), assign(echo, resets)
        excl = [(t["run"], t["schedule"], t["why"]) for t in D["runner"]["trials"] if not t["ok"] and not t.get("warmup")]
        metas.append({"session": D["folder"], "legend": D["runner"].get("legend"), "scored": len(D["trials"]), "excluded": excl,
                      "fps": [r(min(t["fps"] for t in D["trials"]), 2), r(max(t["fps"] for t in D["trials"]), 2)] if D["trials"] else None,
                      "server_lines": {"jd": len(jd), "echo": len(echo), "resets": len(resets)}})
        for T in D["trials"]:
            if T["schedule"].startswith("m9v_jd_"):
                rows.append(jd_row(T, jd_by.get(T["run"], [])))
            elif T["schedule"].startswith("m9v_"):
                rows.append(real_row(T, echo_by.get(T["run"], [])))
    print("M9 R Vantage (R5Flowstate S21 client + S3 dedi + SDK, local offline)")
    print("=" * 100)
    print("\n1. Sessions")
    for m in metas:
        print("  %s legend=%s scored=%d fps=%s excluded=%s server lines=%s" % (m["session"], m["legend"], m["scored"], m["fps"],
              m["excluded"] or "none", m["server_lines"]))
    G = {}
    for w in rows:
        G.setdefault(w["schedule"], []).append(w)
    S = {}
    print("\n2. Per schedule")
    for k in sorted(G):
        ws = G[k]
        g = {"n": len(ws), "launched": sum(1 for w in ws if w.get("launched"))}
        for f in ("hold_s", "t_launch_after_hold", "t_launch_after_release", "launch_speed", "echo_dist", "echo_dist_h", "echo_z_above_floor",
                  "echo_settle_t", "view_to_echo_deg", "view_to_echo_3d_deg", "target_dist0", "min_speed", "min_speed_t"):
            s = stats([w.get(f) for w in ws])
            if s["n"]:
                g[f] = s
        js = [w["jump"] for w in ws if w.get("jump")]
        if js:
            g["jump"] = js
        lu = [w["lurch"]["dv_abs"] for w in ws if w.get("lurch")]
        lc = [w["lurch_ctrl"]["dv_abs"] for w in ws if w.get("lurch_ctrl")]
        if lu:
            g["lurch_dv"] = stats(lu)
        if lc:
            g["lurch_ctrl_dv"] = stats(lc)
        g["min_speed_pos"] = [w.get("min_speed_pos") for w in ws if w.get("min_speed_pos")]
        S[k] = g
        print("\n  %s  n=%d launched=%d" % (k, g["n"], g["launched"]))
        for f in ("hold_s", "t_launch_after_hold", "t_launch_after_release", "launch_speed", "echo_dist", "echo_dist_h", "echo_z_above_floor",
                  "echo_settle_t", "view_to_echo_deg", "view_to_echo_3d_deg", "target_dist0", "min_speed", "min_speed_t"):
            if f in g:
                print("    %-24s %s" % (f, fmt(g[f], 2)))
        for j in js:
            print("    jump %s" % json.dumps(j))
        if lu:
            print("    lurch |dv_h| %s" % fmt(g["lurch_dv"]))
        if lc:
            print("    control |dv_h| 3 cmds after the jump %s" % fmt(g["lurch_ctrl_dv"]))
        if k == "m9v_jd_wall":
            print("    min speed positions %s" % g["min_speed_pos"])
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sessions": metas, "groups": S, "trials": rows}, fh, indent=1)
    if a.params:
        P = []
        for k, g in sorted(S.items()):
            ent = {"name": k, "n": g["n"], "launched": g["launched"], "class": "meas"}
            for f in ("t_launch_after_hold", "t_launch_after_release", "echo_dist", "echo_z_above_floor", "echo_settle_t", "view_to_echo_deg"):
                if f in g:
                    ent[f] = r(g[f]["mean"], 3)
            if "jump" in g:
                ent["jump_applied"] = sum(1 for j in g["jump"] if j["applied"])
                ent["jump_dist_to_target"] = r(stats([j["dist_to_target"] for j in g["jump"]]).get("mean"), 1)
                ent["jump_t_after_liftoff"] = r(stats([j["t_after_liftoff"] for j in g["jump"]]).get("mean"), 3)
            if "lurch_dv" in g:
                ent["lurch_dv"] = r(g["lurch_dv"]["mean"], 3)
            P.append(ent)
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"build": "R5Flowstate S21 client + S3 dedicated server + SDK, local offline, 120 fps, Vantage (kit)", "params": P}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
