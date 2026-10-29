#!/usr/bin/env python3
"""G-6: the recorded client (cl) and dedi (sv) paths around the grapple detach of each trial of a G6 session.

The detach = the first client frame of the [M10-GRC] logger with pull=false after pull=true. Prints, per run, the vz / ground of
the client and dedi movement rows (report/rows.csv, kind move) from 4 frames before to 16 after, and the peak height gained after
the detach (client).

  py -3 wall_detach.py <session dir> [run ...]
"""
import csv
import glob
import os
import re
import sys

GRS = re.compile(r"\[M10-GRS\] run=(\d+) t=([\d.]+) .*? o=([-\d.,]+) v=([-\d.,]+) .*gnd=(\w+)")
GRC = re.compile(r"\[M10-GRC\] run=(\d+) fc=(\d+) t=([\d.]+) act=(\w+) att=(\w+) pull=(\w+)")


def detaches(sess):
    out = {}
    for f in glob.glob(os.path.join(sess, "platform", "logs", "client", "*", "*")):
        try:
            lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        except (IsADirectoryError, PermissionError):
            continue
        prev = {}
        for ln in lines:
            m = GRC.search(ln)
            if not m:
                continue
            run, t, pull = int(m.group(1)), float(m.group(3)), m.group(6) == "true"
            if prev.get(run) and not pull and run not in out:
                out[run] = t
            prev[run] = pull
    return out


def main(sess, runs):
    det = detaches(sess)
    rows = {}
    with open(os.path.join(sess, "report", "rows.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["source"] != "HSD" or r["kind"] != "frame" or not r["run"] or not r["vz"]:
                continue
            rows.setdefault((int(float(r["run"])), r["side"]), []).append(r)
    # the dedi: the [M10-GRS] logger (per server frame: origin, velocity, ground)
    for f in glob.glob(os.path.join(sess, "platform", "logs", "server", "*", "*")):
        try:
            lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        except (IsADirectoryError, PermissionError):
            continue
        for ln in lines:
            m = GRS.search(ln)
            if m:
                o = [float(v) for v in m.group(3).split(",")]
                v = [float(x) for x in m.group(4).split(",")]
                rows.setdefault((int(m.group(1)), "sv"), []).append({"t": m.group(2), "ox": o[0], "oz": o[2], "vz": v[2], "vx": v[0],
                                                                    "ground": m.group(5)})
    for run in sorted(det):
        if runs and run not in runs:
            continue
        td = det[run]
        print("run %d: client pull ends t=%.4f" % (run, td))
        for side in ("cl", "sv"):
            rs = sorted(rows.get((run, side), []), key=lambda r: float(r["t"]))
            if not rs:
                print("  %s: no rows" % side)
                continue
            k = min(range(len(rs)), key=lambda i: abs(float(rs[i]["t"]) - td))
            z0 = float(rs[k]["oz"])
            peak = max(float(r["oz"]) for r in rs[k:k + 120]) - z0
            seg = rs[max(0, k - 4):k + 16]
            print("  %s (peak +%.1f u in 1 s): " % (side, peak) + " ".join(
                "%s%.0f%s" % ("[" if r is rs[k] else "", float(r["vz"]), "g" if str(r["ground"]) in ("1", "True", "true") else "")
                + ("]" if r is rs[k] else "") for r in seg))
            print("      x: " + " ".join("%.0f" % float(r["ox"]) for r in seg[::2]))


if __name__ == "__main__":
    main(sys.argv[1], [int(a) for a in sys.argv[2:]])
