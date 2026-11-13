#!/usr/bin/env python3
"""A2, frame by frame: around +zoom and -zoom, the aim yaw step of each frame divided by 0.11 deg (one count at x1).
  py -3 -I analyze_a2q.py <frames.csv> <marks.tsv> <out_dir> [base_fov=89]
At x1 every step is a whole number of counts (3 or 4 at 400 counts/s, ~140 fps); at a scaled sensitivity the step is counts x scale.
scale_est = step / counts_sent_in_the_interval (blank when 0 counts were sent; the send and the frame can be one frame apart).
pred_tan_prev = tan(fov_prev/2)/tan(base/2) with the previous frame's FOV. Writes A2-QUANTA.tsv."""
import csv, math, os, sys
from collections import defaultdict


def main():
    frames, marks, out = sys.argv[1:4]
    base = float(sys.argv[4]) if len(sys.argv) > 4 else 89.0
    mk = defaultdict(list)
    for l in open(marks, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("a2_"):
            mk[p[0]].append((float(p[1]) * 1000, p[2], p[3] if len(p) > 3 else ""))
    fr = [r for r in csv.DictReader(open(frames)) if r["w"]]
    tan = lambda f: math.tan(math.radians(f / 2)) / math.tan(math.radians(base / 2))
    o = open(os.path.join(out, "A2-QUANTA.tsv"), "w", encoding="utf-8")
    o.write("run\tedge\tms_from_key\tzf\tfov\tstep_deg\tstep_in_counts_x1\tcounts_sent\tscale_est\tpred_tan_prev\n")
    for tag, m in mk.items():
        mv = [(x[0], int(x[2].split(",")[0])) for x in m if x[1] == "m"]
        for key in ("+zoom", "-zoom"):
            tz = next((x[0] for x in m if x[1] == key), None)
            if tz is None: continue
            rows = [r for r in fr if tz - 60 <= float(r["w"]) <= tz + 250]
            for a, b in zip(rows, rows[1:]):
                d = float(a["bY"]) - float(b["bY"]); w0, w1 = float(a["w"]), float(b["w"])
                c = sum(n for t, n in mv if w0 < t <= w1)
                o.write(f"{tag}\t{key}\t{w1 - tz:.1f}\t{float(b['zf']):.3f}\t{float(b['fov']):.2f}\t{d:.4f}\t{d / 0.11:.3f}\t{c}\t{(d / 0.11 / c) if c else '':{'.3f' if c else ''}}\t{tan(float(a['fov'])):.3f}\n")
    o.close()


if __name__ == "__main__":
    main()
