#!/usr/bin/env python3
"""A2: mouse sensitivity while zooming in and at zoom-out.
  py -3 -I analyze_a2.py <frames.csv> <marks.tsv> <out_dir> [deg_per_count=0.11] [base_fov=89]
The mouse turns right at a constant 400 counts/s (44 deg/s at hip). Per frame: yaw rate of the aim over a centred ~60 ms window,
ratio = rate / 44, and two predictions from the frame's FOV: tan(fov/2)/tan(base/2) (decompile 0x1408372b0) and fov/base.
Writes A2-FRAMES.tsv and A2-RUNS.tsv (per run: ratio at full zoom, and how the ratio moves in the frames right after -zoom)."""
import csv, math, os, sys
from collections import defaultdict


def main():
    frames, marks, out = sys.argv[1:4]
    k = float(sys.argv[4]) if len(sys.argv) > 4 else 0.11
    base = float(sys.argv[5]) if len(sys.argv) > 5 else 89.0
    mk = defaultdict(list)
    for l in open(marks, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("a2_"):
            mk[p[0]].append((float(p[1]) * 1000, p[2], p[3] if len(p) > 3 else ""))
    fr = [r for r in csv.DictReader(open(frames)) if r["w"]]
    fo = open(os.path.join(out, "A2-FRAMES.tsv"), "w", encoding="utf-8")
    fo.write("run\tt\tzoom_key\tzf\tfov\taimY\tyaw_rate\tratio\tpred_tan\tpred_lin\n")
    ro = open(os.path.join(out, "A2-RUNS.tsv"), "w", encoding="utf-8")
    ro.write("run\tratio_hip\tratio_full_zoom\tpred_tan_full\tfov_full\tzf_at_release\tratio_at_release\tframes_to_ratio_0.95\ts_to_ratio_0.95\tzf_when_0.95\tpred_tan_when_0.95\n")
    rate = 400 * k
    for tag, m in mk.items():
        ms = next(x[0] for x in m if x[1] == "mstart"); me = next(x[0] for x in m if x[1] == "mend")
        zin = next((x[0] for x in m if x[1] == "+zoom"), None); zout = next((x[0] for x in m if x[1] == "-zoom"), None)
        rows = [r for r in fr if ms + 150 <= float(r["w"]) <= me - 80]
        W = [float(r["w"]) for r in rows]; Y = [float(r["bY"]) for r in rows]
        res = []
        for i, r in enumerate(rows):
            a = i; b = i
            while a > 0 and W[i] - W[a - 1] <= 30: a -= 1
            while b < len(rows) - 1 and W[b + 1] - W[i] <= 30: b += 1
            if b == a: continue
            dy = Y[a] - Y[b]
            if dy < -180: dy += 360
            if dy > 180: dy -= 360
            yr = dy / ((W[b] - W[a]) / 1000)
            fov = float(r["fov"]); zf = float(r["zf"] or 0)
            pt = math.tan(math.radians(fov / 2)) / math.tan(math.radians(base / 2))
            ky = "in" if zin and (zout is None or W[i] < zout) and W[i] >= zin else ("out" if zout and W[i] >= zout else "")
            res.append((W[i], ky, zf, fov, Y[i], yr, yr / rate, pt, fov / base))
            fo.write(f"{tag}\t{(W[i] - ms) / 1000:.4f}\t{ky}\t{zf:.4f}\t{fov:.3f}\t{Y[i]:.4f}\t{yr:.3f}\t{yr / rate:.4f}\t{pt:.4f}\t{fov / base:.4f}\n")
        hip = [x[6] for x in res if (zin is None or x[0] < zin - 50)]
        full = [x for x in res if x[2] >= 0.999]
        rh = sum(hip) / len(hip) if hip else float("nan")
        rf = sum(x[6] for x in full) / len(full) if full else float("nan")
        pf = sum(x[7] for x in full) / len(full) if full else float("nan")
        ff = sum(x[3] for x in full) / len(full) if full else float("nan")
        line = [tag, f"{rh:.4f}", f"{rf:.4f}", f"{pf:.4f}", f"{ff:.2f}"]
        if zout:
            after = [x for x in res if x[0] >= zout]
            z0 = after[0][2] if after else float("nan"); r0 = after[0][6] if after else float("nan")
            j = next((n for n, x in enumerate(after) if x[6] >= 0.95), None)
            line += [f"{z0:.3f}", f"{r0:.4f}"]
            line += [str(j), f"{(after[j][0] - zout) / 1000:.3f}", f"{after[j][2]:.3f}", f"{after[j][7]:.4f}"] if j is not None else ["", "", "", ""]
        ro.write("\t".join(line) + "\n")
    fo.close(); ro.close()
    print(open(os.path.join(out, "A2-RUNS.tsv")).read())


if __name__ == "__main__":
    main()
