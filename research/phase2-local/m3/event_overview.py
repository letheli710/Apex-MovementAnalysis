#!/usr/bin/env python3
"""Per-trial movement-event overview of an hsd_session.py folder (sanity check before fitting).

For each scored trial: schedule, dedi movement-event sequence (JUMP, LEAVE_GROUND, TOUCH_GROUND,
BEGIN/END_WALLRUN, MANTLE, BEGIN/END_SLIDE, ...; consecutive duplicates collapsed), client peak 2D
speed, the largest single-usercmd heading change while airborne (a lurch shows here), and the end
position relative to the start. It decides nothing.

  py -3 event_overview.py <session folder> [--filter e7_]
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-prep", "tools"))
from hsdtel import derive, parse  # noqa: E402

SHORT = {"JUMP": "J", "LEAVE_GROUND": "L", "TOUCH_GROUND": "T", "BEGIN_WALLRUN": "W+", "END_WALLRUN": "W-",
         "BEGIN_WALLHANG": "H+", "END_WALLHANG": "H-", "MANTLE": "M", "BEGIN_SLIDE": "S+", "END_SLIDE": "S-",
         "DOUBLE_JUMP": "DJ", "DODGE": "D", "RESPAWN": "R"}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--filter", default="")
    a = ap.parse_args(argv)
    files, rows, issues = parse.parse_inputs([os.path.join(a.session, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(a.session, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    mt, ev = {}, {}
    for r in rows:
        run = r.get("drv_run")
        if r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay"):
            mt.setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "sv" and r.get("kind") == "evt":
            ev.setdefault(f"r{int(float(r.get('run') or 0))}", []).append(r)
    for t in runner["trials"]:
        name = t.get("schedule", "")
        if t.get("warmup") or not name.startswith(a.filter):
            continue
        run = f"r{t['run']}"
        rs = sorted(mt.get(run, []), key=lambda r: r["cmd"])
        seq = []
        for e in sorted(ev.get(run, []), key=lambda e: e.get("seq", 0)):
            s = SHORT.get(e.get("evt"), e.get("evt"))
            if not seq or seq[-1] != s:
                seq.append(s)
        if not rs:
            print(f"{run:6s} {name:24s} no usercmds"); continue
        peak = max(math.hypot(r["pvx"], r["pvy"]) for r in rs)
        turn = 0.0
        for r in rs:
            if r["ground"] == 0 and math.hypot(r["vx"], r["vy"]) > 50 and math.hypot(r["pvx"], r["pvy"]) > 50:
                d = math.degrees(math.atan2(r["pvy"], r["pvx"]) - math.atan2(r["vy"], r["vx"]))
                d = (d + 180) % 360 - 180
                if abs(d) > abs(turn):
                    turn = d
        o0 = t.get("origin", [rs[0]["ox"], rs[0]["oy"], rs[0]["oz"]])
        end = (rs[-1]["pox"] - o0[0], rs[-1]["poy"] - o0[1], rs[-1]["poz"] - o0[2])
        print(f"{run:6s} {name:24s} {'Y' if t['ok'] else 'N'} peak {peak:6.1f} maxturn {turn:7.2f} "
              f"end {end[0]:7.1f} {end[1]:7.1f} {end[2]:7.1f}  " + " ".join(seq))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
