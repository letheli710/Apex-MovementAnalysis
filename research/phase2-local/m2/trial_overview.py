#!/usr/bin/env python3
"""Per-trial overview of an hsd_session.py folder: what the movement did in each scored trial.

Columns (client MOVE-TRACE usercmds of the trial's run label, first-time predictions only):
schedule, usercmds, gaps, fps, peak 2D speed, end displacement (dx, dy, dz) from the first
usercmd, min z change (a fall off the platform shows as a large negative dz), the set of
move scales and max speeds seen, and counts of sprint / duck / slide / airborne usercmds and
take-offs. Meant for sanity checks before fitting; it decides nothing.

  py -3 trial_overview.py <session folder>
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-prep", "tools"))
from hsdtel import derive, parse  # noqa: E402


def load(folder):
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    by_run = {}
    for r in rows:
        if r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay"):
            by_run.setdefault(r.get("drv_run"), []).append(r)
    for rs in by_run.values():
        rs.sort(key=lambda r: r["cmd"])
    return runner, by_run, rows


def overview(t, rs):
    cmds = [r["cmd"] for r in rs]
    sp = [math.hypot(r["pvx"], r["pvy"]) for r in rs]
    takeoffs = sum(1 for a, b in zip(rs, rs[1:]) if a["ground"] == 1 and b["ground"] == 0)
    return {
        "run": f"r{t['run']}", "schedule": t.get("schedule"), "ok": t["ok"], "fps": t["measured_fps"],
        "cmds": len(rs), "gaps": sum(1 for a, b in zip(cmds, cmds[1:]) if b - a != 1),
        "peak": round(max(sp), 2), "end_dx": round(rs[-1]["pox"] - rs[0]["ox"], 1),
        "end_dy": round(rs[-1]["poy"] - rs[0]["oy"], 1), "end_dz": round(rs[-1]["poz"] - rs[0]["oz"], 1),
        "min_dz": round(min(r["poz"] for r in rs) - rs[0]["oz"], 1),
        "msc": sorted({r["movescale"] for r in rs}), "ms": sorted({r["maxspeed"] for r in rs}),
        "sprint": sum(1 for r in rs if r["sprint"]), "duck": sum(1 for r in rs if r["duck"]),
        "slide": sum(1 for r in rs if r["slide"]), "air": sum(1 for r in rs if r["ground"] == 0),
        "takeoffs": takeoffs,
    }


def main(argv):
    runner, by_run, rows = load(argv[0])
    print(f"{'run':6s} {'schedule':16s} ok   fps    cmds gaps  peak   end dx/dy/dz        min_dz sprint duck slide air takeoffs msc / ms")
    for t in runner["trials"]:
        if t.get("warmup"):
            continue
        rs = by_run.get(f"r{t['run']}")
        if not rs:
            print(f"r{t['run']}: no usercmds"); continue
        o = overview(t, rs)
        print(f"{o['run']:6s} {o['schedule']:16s} {'Y' if o['ok'] else 'N'} {o['fps']:7} {o['cmds']:5d} {o['gaps']:3d} {o['peak']:7.2f} "
              f"{o['end_dx']:7.1f}/{o['end_dy']:7.1f}/{o['end_dz']:6.1f} {o['min_dz']:7.1f} {o['sprint']:5d} {o['duck']:5d} {o['slide']:4d} "
              f"{o['air']:4d} {o['takeoffs']:3d}  {o['msc']} / {o['ms']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
