#!/usr/bin/env python3
"""B7: real fire intervals and charge curves.
  py -3 -I analyze_b7.py <frida dir> <marks.tsv> <runs dir> <out dir>  ->  B7-RATE.tsv, B7-CHARGE.tsv
Shots: server [RT] atk lines. Press times: marks (wall clock) turned into game time with the Frida frames (w, ct).
Charge: client [RT] ch lines (GetWeaponChargeFraction per frame) after the first press."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_b1 import load_frames, marks, run_lines, ATK


def main():
    fd, mk, rd, out = sys.argv[1:5]
    fr = load_frames(fd); M = marks(mk)
    rate, charge = [], []
    for tag in sorted(M):
        if not tag.startswith("b7_"): continue
        ev = M[tag]
        F = [x for x in fr if ev[0][0] * 1000 <= x["w"] <= ev[-1][0] * 1000]
        if not F: continue
        off = sum(x["w"] / 1000 - x["ct"] for x in F) / len(F)
        press = [t - off for t, m in ev if m == "+attack"]
        release = [t - off for t, m in ev if m == "-attack"]
        s, c = run_lines(os.path.join(rd, tag + ".txt"))
        at = sorted(set(round(float(m.group(1)), 4) for m in (ATK.search(l) for l in s) if m))
        iv = [at[i + 1] - at[i] for i in range(len(at) - 1)]
        first = (at[0] - press[0]) if at and press else float("nan")
        med = sorted(iv)[len(iv) // 2] if iv else float("nan")
        rate.append([tag, len(at), f"{first:.3f}", f"{med:.3f}", f"{min(iv) if iv else float('nan'):.3f}", f"{max(iv) if iv else float('nan'):.3f}",
                     f"{(1 / med) if iv else float('nan'):.2f}", " ".join(f"{x:.3f}" for x in iv[:16])])
        ch = [(float(m.group(1)), float(m.group(2))) for m in (re.search(r"\] ch t=([\d.]+) c=([\d.]+)", l) for l in c) if m]
        if press and ch:
            p0 = press[0]; rel = release[0] if release else p0 + 99
            C = [(t - p0, v) for t, v in ch if p0 - 0.05 <= t <= rel + 0.05]
            mx = max((v for _, v in C), default=0)
            tx = lambda q: next((t for t, v in C if v >= q), float("nan"))
            if mx > 0:
                charge.append([tag, f"{mx:.3f}", f"{tx(0.01):.3f}", f"{tx(0.25):.3f}", f"{tx(0.5):.3f}", f"{tx(0.75):.3f}", f"{tx(0.999):.3f}",
                               f"{(release[0] - p0) if release else float('nan'):.3f}"])
    with open(os.path.join(out, "B7-RATE.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tshots\tpress_to_first_shot_s\tmedian_interval_s\tmin_interval_s\tmax_interval_s\trate_per_s\tintervals\n")
        for r in rate: f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(out, "B7-CHARGE.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tmax_charge\tt_1pct\tt_25pct\tt_50pct\tt_75pct\tt_full\thold_s\n")
        for r in charge: f.write("\t".join(map(str, r)) + "\n")
    print(len(rate), len(charge))


if __name__ == "__main__":
    main()
