#!/usr/bin/env python3
"""Cut frames.csv by run marks. py -3 -I slice.py <frames.csv> <marks.tsv> <tag> [every]
Prints per frame: t (s from start), marks in between, aim bP bY, view fP fY, punch s2P v2P, zf, fov."""
import csv, sys


def load(frames, marks, tag):
    mk = [l.rstrip("\n").split("\t") for l in open(marks, encoding="utf-8") if l.startswith(tag + "\t")]
    t0 = float(mk[0][1]) * 1000; t1 = float(mk[-1][1]) * 1000
    rows = [r for r in csv.DictReader(open(frames)) if r["w"] and t0 - 200 <= float(r["w"]) <= t1 + 200]
    return t0, rows, [(float(m[1]) * 1000, m[2], m[3] if len(m) > 3 else "") for m in mk]


if __name__ == "__main__":
    t0, rows, mk = load(*sys.argv[1:4])
    ev = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    mi = 0
    for i, r in enumerate(rows):
        w = float(r["w"])
        while mi < len(mk) and mk[mi][0] <= w:
            if mk[mi][1] != "m": print(f"   --- {(mk[mi][0]-t0)/1000:.3f} {mk[mi][1]} {mk[mi][2]}")
            mi += 1
        if i % ev == 0:
            print(f"{(w-t0)/1000:7.3f} b={r['bP']:>9},{r['bY']:>9} f={r['fP']:>9},{r['fY']:>9} s2={r['s2P']:>8} v2={r['v2P']:>8} zf={r['zf']} fov={r['fov']} idx={r['idx']}")
