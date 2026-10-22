#!/usr/bin/env python3
"""M8 track R2: Vantage jet drive (Echo relocation) feasibility probe (R5Flowstate S21, local offline).

  py -3 vantage_analysis.py <session> [--json results.json] [--params params.json] > analysis_output.txt

Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py). stdlib only, no local paths. Schedules m8r2_jd_* and
m8r2_echo_* on lane C (tools/hsd_trial.py):
- m8r2_jd_d<D>[...]: the reset spawns a script mover D u ahead, 120 u above the floor; a server thread calls
  BeginJetDrive(787, 1575, mover, mover, <0,0,-69>, round(2*dist/787, 1)) and EnableJetDriveDoubleJump(<512,0,394>, 0.5)
  1.5 s after the reset and prints "[R2-JD] begin t=<server time> o=<player> tgt=<mover> timeout=<s>". The drive target
  is mover + (0, 0, -69). _mvy / _mvx: the mover moves +300 u in y over 1.0 s / +600 u in x over 1.5 s from the begin.
- m8r2_echo_send_launch: the real tactical (tap = send Echo, hold = launch); a server thread logs the Echo origin
  ("[R2-ECHO] t=... o=<echo> p=<player> jd=<drive active>") at the server frame rate for 9 s.

Per trial (client first-time usercmds; the dedi rows of the same usercmds are compared):
- launch    = first usercmd with post |v| > 500; launch speed, elevation, heading;
- path      = |v| every 0.1 s, apex height, closest approach to the target point (time, distance), crossing of the target
              plane (first usercmd whose position along the start->target direction passes the target);
- landing   = first grounded usercmd after the launch; overshoot = landing position past the target along the travel;
- double jump = the usercmd with a new jump press: pre / post velocity; applied if post vz rises by > 200;
- duck      = the usercmd with a new crouch press: pre / post velocity (duck-cancel scale);
- server/client: largest position difference between the client and dedi rows of the same usercmds.
Server and client clocks differ, so server lines are matched to trials by order (jd begin lines) or by the player
leaving the start (Echo lines), and server time is aligned through the dedi LEAVE_GROUND event of the trial.
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
IN_JUMP, IN_DUCK = 0x2, 0x4
VEC = r"<\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*>"
JD_RE = re.compile(r"\[R2-JD\] begin t=([\d.]+) o=" + VEC + r" tgt=" + VEC + r" timeout=([\d.]+)")
ECHO_RE = re.compile(r"\[R2-ECHO\] t=([\d.]+) valid=(\w+) o=" + VEC + r" p=" + VEC + r" jd=(\w+)")
MOVES = {"m8r2_jd_d800_mvy": ((0.0, 300.0, 0.0), 1.0), "m8r2_jd_d800_mvx": ((600.0, 0.0, 0.0), 1.5)}


def r(x, n=3):
    return None if x is None else round(x, n)


def vlen(v):
    return math.sqrt(sum(a * a for a in v))


def server_lines(folder):
    jd, echo = [], []
    for f in L._files(folder, "server", "script"):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
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
    jd.sort(key=lambda d: d["t"])
    echo.sort(key=lambda d: d["t"])
    return jd, echo


def echo_groups(echo):
    out, cur = [], []
    for e in echo:
        if cur and e["t"] - cur[-1]["t"] > 1.0:
            out.append(cur)
            cur = []
        cur.append(e)
    if cur:
        out.append(cur)
    return out


def trial_row(T, target_fn, extra):
    cmds = [c for c in T["cmds"] if c.get("t") is not None]
    row = {"run": T["run"], "schedule": T["schedule"], "fps": T["fps"], "join": T["join"]}
    row.update(extra)
    i0 = next((i for i, c in enumerate(cmds) if vlen((c["pvx"], c["pvy"], c["pvz"])) > 500.0), None)
    if i0 is None:
        row["launched"] = False
        return row
    row["launched"] = True
    c0 = cmds[i0]
    tL = c0["t"]
    start = (cmds[i0 - 1]["pox"], cmds[i0 - 1]["poy"], cmds[i0 - 1]["poz"]) if i0 else (c0["ox"], c0["oy"], c0["oz"])
    v0 = (c0["pvx"], c0["pvy"], c0["pvz"])
    row["launch_v"] = [r(x, 2) for x in v0]
    row["launch_speed"] = r(vlen(v0), 2)
    row["launch_elev_deg"] = r(math.degrees(math.atan2(v0[2], math.hypot(v0[0], v0[1]))), 2)
    row["start"] = [r(x, 2) for x in start]
    # speeds every 0.1 s, apex, landing
    prof = {}
    for k in range(0, 31):
        tt = tL + 0.1 * k
        c = min(cmds[i0:], key=lambda c: abs(c["t"] - tt))
        if abs(c["t"] - tt) < 0.02:
            prof["%.1f" % (0.1 * k)] = [r(vlen((c["pvx"], c["pvy"], c["pvz"])), 1), r(math.hypot(c["pvx"], c["pvy"]), 1), r(c["pvz"], 1)]
    row["profile"] = prof
    air = []
    for c in cmds[i0:]:
        if c["ground"] and c["t"] > tL + 0.05:
            break
        air.append(c)
    land = cmds[i0 + len(air)] if i0 + len(air) < len(cmds) else None
    row["apex_z"] = r(max(c["poz"] for c in air) - FLOOR, 2)
    row["air_time"] = r((land["t"] if land else air[-1]["t"]) - tL, 4)
    # target geometry
    if target_fn is not None:
        best, cross = None, None
        for c in air:
            tg = target_fn(c["t"] - tL)
            d = vlen((c["pox"] - tg[0], c["poy"] - tg[1], c["poz"] - tg[2]))
            if best is None or d < best[0]:
                best = (d, c["t"] - tL, c)
            u = (tg[0] - start[0], tg[1] - start[1])
            un = math.hypot(*u) or 1.0
            along = ((c["pox"] - start[0]) * u[0] + (c["poy"] - start[1]) * u[1]) / un
            if cross is None and along >= un:
                cross = (c["t"] - tL, c, tg)
        tg0 = target_fn(0.0)
        row["target_dist0"] = r(vlen((tg0[0] - start[0], tg0[1] - start[1], tg0[2] - start[2])), 1)
        row["closest_dist"] = r(best[0], 2)
        row["closest_t"] = r(best[1], 4)
        row["closest_speed"] = r(vlen((best[2]["pvx"], best[2]["pvy"], best[2]["pvz"])), 1)
        if cross:
            t_c, c, tg = cross
            row["cross_t"] = r(t_c, 4)
            row["cross_offset"] = [r(c["pox"] - tg[0], 1), r(c["poy"] - tg[1], 1), r(c["poz"] - tg[2], 1)]
            row["cross_mean_speed"] = r(row["target_dist0"] / t_c, 1) if t_c > 0 else None
        if land:
            tgL = target_fn(land["t"] - tL)
            u = (tgL[0] - start[0], tgL[1] - start[1])
            un = math.hypot(*u) or 1.0
            along = ((land["pox"] - start[0]) * u[0] + (land["poy"] - start[1]) * u[1]) / un
            row["land_past_target"] = r(along - un, 1)
            row["land_lateral"] = r(((land["pox"] - start[0]) * -u[1] + (land["poy"] - start[1]) * u[0]) / un, 1)
            row["land_pos"] = [r(land["pox"], 1), r(land["poy"], 1), r(land["poz"] - FLOOR, 2)]
            row["land_hspeed"] = r(math.hypot(land["vx"], land["vy"]), 1)
    # presses during the flight
    prev_b = cmds[i0 - 1]["buttons"] if i0 else 0
    for c in cmds[i0:]:
        new = c["buttons"] & ~prev_b
        prev_b = c["buttons"]
        if c["t"] > tL + (row["air_time"] or 0) + 0.2:
            break
        for bit, name in ((IN_JUMP, "dj"), (IN_DUCK, "duck")):
            if new & bit and name not in row:
                pre = (c["vx"], c["vy"], c["vz"])
                post = (c["pvx"], c["pvy"], c["pvz"])
                d = {"t_after_launch": r(c["t"] - tL, 4), "pre": [r(x, 2) for x in pre], "post": [r(x, 2) for x in post],
                     "pre_h": r(math.hypot(pre[0], pre[1]), 2), "post_h": r(math.hypot(post[0], post[1]), 2),
                     "z": r(c["poz"] - FLOOR, 2), "grounded": bool(c["ground"])}
                if target_fn is not None:
                    tg = target_fn(c["t"] - tL)
                    d["dist_to_target"] = r(vlen((c["ox"] - tg[0], c["oy"] - tg[1], c["oz"] - tg[2])), 1)
                if name == "dj":
                    d["applied"] = post[2] - pre[2] > 200.0
                    d["post_vz_plus_half_g_dt"] = r(post[2] + 0.5 * 750.0 * (c["dt"] or 1 / 120.0), 2)
                else:
                    d["scale_h"] = r(math.hypot(*post[:2]) / math.hypot(*pre[:2]), 4) if math.hypot(*pre[:2]) > 1 else None
                row[name] = d
    # dedi vs client
    diffs = [vlen((c["pox"] - T["sv"][c["cmd"]]["pox"], c["poy"] - T["sv"][c["cmd"]]["poy"], c["poz"] - T["sv"][c["cmd"]]["poz"]))
             for c in air if c["cmd"] in T["sv"]]
    row["sv_cl_max_pos_diff"] = r(max(diffs), 3) if diffs else None
    row["sv_rows"] = len(diffs)
    return row


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    rows, metas = [], []
    for folder in a.sessions:
        D = L.load(folder)
        jd, echo = server_lines(folder)
        runner_trials = D["runner"]["trials"]
        jd_trials = [t for t in runner_trials if t["schedule"].startswith("m8r2_jd_")]
        jd_by_run = {t["run"]: jd[i] for i, t in enumerate(jd_trials) if i < len(jd)}
        groups = echo_groups(echo)
        echo_trials = [t for t in runner_trials if t["schedule"].startswith("m8r2_echo")]
        echo_by_run = {t["run"]: groups[i] for i, t in enumerate(echo_trials) if i < len(groups)}
        excl = [(t["run"], t["schedule"], t["why"]) for t in runner_trials if not t["ok"] and not t.get("warmup")]
        metas.append({"session": D["folder"], "legend": D["runner"].get("legend"), "scored": len(D["trials"]),
                      "excluded": excl, "jd_begin_lines": len(jd), "jd_trials_incl_warmup": len(jd_trials),
                      "echo_groups": len(groups), "echo_trials": len(echo_trials),
                      "fps": [r(min(t["fps"] for t in D["trials"]), 2), r(max(t["fps"] for t in D["trials"]), 2)]})
        for T in D["trials"]:
            sch = T["schedule"]
            extra, tfn = {}, None
            if T["run"] in jd_by_run:
                b = jd_by_run[T["run"]]
                tgt0 = (b["tgt"][0], b["tgt"][1], b["tgt"][2] - 69.0)
                lg = next((e for e in T["sv_evt"] if e["evt"] == "LEAVE_GROUND"), None)
                delay = (lg["t"] - b["t"]) if lg else None
                extra.update(timeout=b["timeout"], begin_to_leave_ground_sv=r(delay, 4), target0=[r(x, 2) for x in tgt0])
                mv = MOVES.get(sch)
                if mv:
                    (dx, dy, dz), T_mv = mv

                    def tfn(t, tgt0=tgt0, dx=dx, dy=dy, dz=dz, T_mv=T_mv, delay=delay or 0.0):
                        f = min(max((t + delay) / T_mv, 0.0), 1.0)
                        return (tgt0[0] + dx * f, tgt0[1] + dy * f, tgt0[2] + dz * f)
                    extra["target_move"] = {"delta": [dx, dy, dz], "over_s": T_mv}
                else:
                    def tfn(t, tgt0=tgt0):
                        return tgt0
            elif T["run"] in echo_by_run:
                g = echo_by_run[T["run"]]
                e_on = next((e for e in g if e["jd"]), None)
                if e_on:
                    eo = e_on["echo"]
                    extra["echo_at_launch"] = [r(x, 1) for x in eo]
                    extra["echo_height_above_floor"] = r(eo[2] - FLOOR, 1)
                    tgt0 = (eo[0], eo[1], eo[2] - 69.0)

                    def tfn(t, tgt0=tgt0):
                        return tgt0
                    extra["echo_moves_during_drive"] = r(max(vlen([x - y for x, y in zip(e["echo"], eo)]) for e in g if e["jd"]), 2)
                    sent = [e for e in g if not e["jd"] and e["t"] < e_on["t"]]
                    if sent:
                        extra["echo_send_settle"] = [r(x, 1) for x in sent[-1]["echo"]]
                    extra["echo_jd_server_span"] = r(max(e["t"] for e in g if e["jd"]) - e_on["t"], 2)
            rows.append(trial_row(T, tfn, extra))

    print("M8 R2 Vantage jet drive probe")
    print("=" * 72)
    print("\n1. Sessions")
    for m in metas:
        print("  %s legend=%s scored=%d fps %s..%s excluded=%s  jd begin lines %d / jd trials incl. warm-up %d; echo groups %d / "
              "echo trials %d" % (m["session"], m["legend"], m["scored"], m["fps"][0], m["fps"][1], m["excluded"] or "none",
                                  m["jd_begin_lines"], m["jd_trials_incl_warmup"], m["echo_groups"], m["echo_trials"]))
    print("\n2. Per trial")
    hdr = "  %-6s %-22s %7s %7s %6s %7s %7s %7s %7s %7s %8s %7s %7s %6s"
    print(hdr % ("run", "schedule", "dist0", "v0", "elev", "apex", "cl_d", "cl_t", "x_t", "x_v", "land+", "lat", "air", "sv-cl"))
    for w in rows:
        print(hdr % (w["run"], w["schedule"], w.get("target_dist0"), w.get("launch_speed"), w.get("launch_elev_deg"), w.get("apex_z"),
                     w.get("closest_dist"), w.get("closest_t"), w.get("cross_t"), w.get("cross_mean_speed"),
                     w.get("land_past_target"), w.get("land_lateral"), w.get("air_time"), w.get("sv_cl_max_pos_diff")))
        for k in ("dj", "duck"):
            if k in w:
                d = w[k]
                print("        %s: t+%s dist %s pre %s -> post %s (h %s -> %s)%s" % (
                    k, d["t_after_launch"], d.get("dist_to_target"), d["pre"], d["post"], d["pre_h"], d["post_h"],
                    (" applied=%s" % d["applied"]) if k == "dj" else (" scale_h=%s" % d.get("scale_h"))))
        if "echo_at_launch" in w:
            print("        echo at launch %s (h %s above floor), moved %s during the drive, server jd span %s s" % (
                w["echo_at_launch"], w["echo_height_above_floor"], w["echo_moves_during_drive"], w["echo_jd_server_span"]))
        if "begin_to_leave_ground_sv" in w:
            print("        server BeginJetDrive -> LEAVE_GROUND %s s; timeout %s; cross offset %s" % (
                w["begin_to_leave_ground_sv"], w["timeout"], w.get("cross_offset")))

    groups = {}
    for w in rows:
        groups.setdefault(w["schedule"], []).append(w)
    summary = {}
    print("\n3. Groups")
    for sch, ws in groups.items():
        g = {"n": len(ws)}
        for f in ("launch_speed", "launch_elev_deg", "apex_z", "closest_dist", "closest_t", "cross_t", "cross_mean_speed",
                  "land_past_target", "land_lateral", "air_time", "sv_cl_max_pos_diff", "begin_to_leave_ground_sv", "target_dist0",
                  "echo_height_above_floor"):
            s = L.stats([w.get(f) for w in ws])
            if s["n"]:
                g[f] = s
        dj = [w["dj"] for w in ws if "dj" in w]
        if dj:
            g["dj_applied"] = sum(1 for d in dj if d["applied"])
            g["dj_post_h"] = L.stats([d["post_h"] for d in dj if d["applied"]])
            g["dj_post_vz_plus_half_g_dt"] = L.stats([d["post_vz_plus_half_g_dt"] for d in dj if d["applied"]])
            g["dj_t"] = L.stats([d["t_after_launch"] for d in dj])
            g["dj_dist"] = L.stats([d.get("dist_to_target") for d in dj])
        du = [w["duck"] for w in ws if "duck" in w]
        if du:
            g["duck_scale_h"] = L.stats([d.get("scale_h") for d in du])
            g["duck_t"] = L.stats([d["t_after_launch"] for d in du])
        prof = {}
        for k in ("0.0", "0.2", "0.4", "0.6", "0.8", "1.0", "1.2", "1.4", "1.6", "1.8", "2.0", "2.2"):
            s = L.stats([w.get("profile", {}).get(k, [None])[0] for w in ws])
            if s["n"]:
                prof[k] = r(s["mean"], 1)
        g["speed_profile"] = prof
        summary[sch] = g
        print("  %s n=%d" % (sch, len(ws)))
        for k, v in g.items():
            if isinstance(v, dict) and "n" in v:
                print("      %-28s %s" % (k, L.fmt(v, 3)))
        if "dj_applied" in g:
            print("      dj applied %d / %d" % (g["dj_applied"], len(dj)))
        print("      |v| every 0.2 s: %s" % prof)

    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sessions": metas, "trials": rows, "groups": summary}, fh, indent=1)
    if a.params:
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(build_params(summary, rows), fh, indent=1)
    return 0


def _p(name, s, unit, cls, note=""):
    if not s or not s.get("n"):
        return None
    return {"name": name, "value": r(s["mean"], 4), "sd": r(s["sd"], 4), "n": s["n"], "unit": unit, "class": cls, "note": note}


def build_params(summary, rows):
    P = []
    allj = [w for w in rows if w["schedule"].startswith("m8r2_jd_") and w.get("launched")]
    P.append(_p("jd_launch_speed", L.stats([w["launch_speed"] for w in allj]), "u/s", "meas",
                "first drive usercmd; source speed 787 x jetdrive_initial_speed_mult 1.2 (SDK cvar)"))
    for sch in ("m8r2_jd_d400", "m8r2_jd_d800", "m8r2_jd_d1200", "m8r2_echo_send_launch"):
        g = summary.get(sch)
        if not g:
            continue
        tag = sch.replace("m8r2_", "")
        P.append(_p(tag + "_launch_elev", g.get("launch_elev_deg"), "deg", "meas"))
        P.append(_p(tag + "_apex", g.get("apex_z"), "u above floor", "meas"))
        P.append(_p(tag + "_target_cross_t", g.get("cross_t"), "s", "meas", "launch -> passing the target along the start-target line"))
        P.append(_p(tag + "_mean_speed_to_target", g.get("cross_mean_speed"), "u/s", "meas", "3D start-target distance / cross_t"))
        P.append(_p(tag + "_closest_dist", g.get("closest_dist"), "u", "meas", "closest approach to the drive target point"))
        P.append(_p(tag + "_land_past_target", g.get("land_past_target"), "u", "meas", "first grounded usercmd, along the travel"))
        if g.get("speed_profile"):
            P.append({"name": tag + "_speed_profile", "value": g["speed_profile"], "n": g["n"], "unit": "|v| u/s at t s after launch",
                      "class": "meas", "note": ""})
    dj = [w["dj"] for w in rows if "dj" in w]
    if dj:
        P.append({"name": "jd_double_jump", "value": [{"t": d["t_after_launch"], "dist": d.get("dist_to_target"), "applied": d["applied"],
                                                       "post_h": d["post_h"], "post_vz": d["post"][2]} for d in dj],
                  "n": len(dj), "unit": "s / u / bool / u/s", "class": "meas", "note": "source EnableJetDriveDoubleJump(<512,0,394>, 0.5)"})
    du = [w["duck"] for w in rows if "duck" in w]
    if du:
        P.append(_p("jd_duck_scale_h", L.stats([d.get("scale_h") for d in du]), "ratio", "meas",
                    "post / pre horizontal speed on the crouch usercmd; SDK cvar jetdrive_duck_cancel_vel_frac 0.8"))
    for sch in ("m8r2_jd_d800_mvy", "m8r2_jd_d800_mvx"):
        g = summary.get(sch)
        if g:
            P.append(_p(sch.replace("m8r2_", "") + "_land_lateral", g.get("land_lateral"), "u", "meas",
                        "landing offset from the start->target(t_land) line; target moved during the drive"))
            P.append(_p(sch.replace("m8r2_", "") + "_closest_dist", g.get("closest_dist"), "u", "meas", "to the moving target point"))
    P.append(_p("jd_sv_cl_max_pos_diff", L.stats([w.get("sv_cl_max_pos_diff") for w in rows if w.get("launched")]), "u", "meas",
                "client vs dedi rows of the same usercmds during the flight"))
    return [p for p in P if p]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
