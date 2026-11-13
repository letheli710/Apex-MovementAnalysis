#!/usr/bin/env python3
"""B4: real hits from a bot player. For each server damage event ([RT] pdmg, server Time = client game time), the client view
0.6 s after the hit against the frame before it.  py -3 -I analyze_b4.py <frida dir> <runs dir> <out dir> -> B4-HITS.tsv
Columns are max abs change: aim (eye angles), punch1, punch2, r_out (screen - aim - punch output), roll, eye position, FOV."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_b1 import load_frames


def main():
    fd, rd, out = sys.argv[1:4]
    fr = load_frames(fd)
    rows = []
    for fn in sorted(os.listdir(rd)):
        if not fn.startswith("b4_"): continue
        txt = open(os.path.join(rd, fn), encoding="utf-8").read()
        for m in re.finditer(r"pdmg t=([\d.]+) amt=([\d.]+) src=(\d+)", txt):
            t, amt = float(m.group(1)), float(m.group(2))
            B = [x for x in fr if t - 0.2 <= x["ct"] < t]
            A = [x for x in fr if t <= x["ct"] < t + 0.6]
            if not B or not A: continue
            b = B[-1]
            d = lambda k: max(abs(x[k] - b[k]) for x in A)
            r = lambda x: (x["fP"] - x["bP"] - x["puP"], x["fY"] - x["bY"] - x["puY"])
            rb = r(b)
            rout = max(max(abs(r(x)[0] - rb[0]), abs(r(x)[1] - rb[1])) for x in A)
            pos = max(((x["eX"] - b["eX"]) ** 2 + (x["eY"] - b["eY"]) ** 2 + (x["eZ"] - b["eZ"]) ** 2) ** 0.5 for x in A)
            rows.append([fn[:-4], f"{t:.3f}", f"{amt:.0f}", f"{max(d('bP'), d('bY')):.4f}", f"{max(d('p1P'), d('p1Y'), d('p1R')):.4f}", f"{max(d('s2P'), d('s2Y'), d('s2R')):.4f}",
                         f"{rout:.4f}", f"{d('fR'):.4f}", f"{max(d('fP'), d('fY')):.4f}", f"{pos:.3f}", f"{d('fov'):.3f}", f"{b['zf']:.2f}", len(A)])
    with open(os.path.join(out, "B4-HITS.tsv"), "w", encoding="utf-8") as f:
        f.write("run\thit_t\tdamage\taim\tpunch1\tpunch2\tr_out\tscreen_roll\tscreen_pitch_yaw\teye_pos_u\tfov\tzf\tframes\n")
        for x in rows: f.write("\t".join(map(str, x)) + "\n")
    print(len(rows), "hits")


if __name__ == "__main__":
    main()
