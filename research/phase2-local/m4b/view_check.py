#!/usr/bin/env python3
"""M4b view-control acceptance: constant-rate turns (+right/+left at cl_yawspeed, +lookup/+lookdown at cl_pitchspeed).

MOVE-TRACE carries no view angles, so the per-usercmd view is read from the client [HSD-MD] frame rows (one row per
usercmd at 120 fps: the post-state of the latest command, ft = that command's dt). For every turning command the rate
dangle/ft is compared with the set rate; the net angle of each trial with the schedule's expected net angle. For
m4b_view_run the dedi's MOVE-TRACE velocity heading is compared with the client yaw, which shows that the server
received the turned view in the usercmds (the trajectory turns, not just the camera).

  py -3 view_check.py <session folder> [--json out.json]
"""
import csv
import json
import math
import os
import sys

RATES = {"m4b_view_yaw": ("yaw", 90.0), "m4b_view_run": ("yaw", 90.0), "m4b_view_pitch": ("pitch", 45.0)}
# net angle from the schedule: yaw right 1.0 s then left 0.5 s; pitch up 0.5 s then down 1.0 s (Source: up = -pitch)
EXPECTED_NET = {"m4b_view_yaw": -90.0 + 45.0, "m4b_view_run": -90.0, "m4b_view_pitch": -22.5 + 45.0}


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def main():
    sdir = sys.argv[1]
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    runner = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
    sched = {t["run"]: t["schedule"] for t in runner["trials"] if t["ok"] and not t["warmup"]}
    frames, sv = {}, {}
    with open(os.path.join(sdir, "report", "rows.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["source"] == "HSD" and r["side"] == "cl" and r["kind"] == "frame" and r["run"]:
                run = int(r["run"])
                if sched.get(run, "").startswith("m4b_view"):
                    frames.setdefault(run, []).append((float(r["ft"]), float(r["pitch"]), float(r["yaw"])))
            elif r["source"] == "MT" and r["side"] == "sv" and r["drv_run"].startswith("r"):
                run = int(r["drv_run"][1:])
                if sched.get(run) == "m4b_view_run":
                    sv.setdefault(run, []).append((int(r["cmd"]), float(r["pvx"]), float(r["pvy"])))
    res = []
    for run in sorted(frames):
        name = sched[run]
        axis, rate = RATES[name]
        k = 1 if axis == "pitch" else 2
        fr = frames[run]
        devs, n = [], 0
        for a, b in zip(fr, fr[1:]):
            d = wrap(b[k] - a[k])
            if abs(d) < 1e-4 or b[0] <= 0:
                continue
            n += 1
            devs.append(abs(d) / b[0] - rate)
        net = wrap(fr[-1][k] - fr[0][k])
        devs = devs or [float("nan")]
        row = {"run": run, "schedule": name, "axis": axis, "set_rate": rate, "turn_cmds": n,
               "rate_mean": round(rate + sum(devs) / len(devs), 4), "rate_max_dev": round(max(abs(x) for x in devs), 4),
               "within_1pct": sum(abs(x) <= 0.01 * rate for x in devs),
               "rate_median": round(rate + sorted(devs)[len(devs) // 2], 4),
               "net_deg": round(net, 3), "net_expected": EXPECTED_NET[name], "net_err": round(net - EXPECTED_NET[name], 3)}
        if name == "m4b_view_run" and run in sv:
            vx, vy = sv[run][-1][1], sv[run][-1][2]
            # heading of the dedi velocity at the last moving command vs the client's final yaw
            moving = [s for s in sv[run] if math.hypot(s[1], s[2]) > 50]
            hx, hy = moving[-1][1], moving[-1][2]
            row["sv_heading_end"] = round(math.degrees(math.atan2(hy, hx)), 3)
            row["cl_yaw_end"] = round(fr[-1][2], 3)
            row["heading_minus_yaw"] = round(wrap(row["sv_heading_end"] - fr[-1][2]), 3)
        res.append(row)
        print(" ".join(f"{k}={v}" for k, v in row.items()))
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
