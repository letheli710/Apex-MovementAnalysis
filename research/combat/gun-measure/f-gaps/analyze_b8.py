#!/usr/bin/env python3
"""B8: long-range drop. For each server hit ([RT] dmg) the shot is the last server [RT] atk before it; the launch line is
attack origin + attackDir (this already holds punch and drift), so drop = height of that line at the hit's distance - hit height.
Formula drop = 0.5 * 750 * gravity_scale * (d / v)^2 (no drag). Zeroing would put the hit ABOVE the formula.
  py -3 -I analyze_b8.py <runs dir> <out dir>  ->  B8-DROP.tsv"""
import math, os, re, sys

G = {"rspn101": (29000, 1.3, 0.0025, 1968.5), "r97": (19000, 1.2, 0.0025, 1378), "wingman": (18000, 1.2, 0.0025, 1378), "dmr": (31000, 1.3, 0.0, 1968.5), "sniper": (29500, 1.4, 0.0033, 1968.5)}
ATK = re.compile(r"atk t=([\d.]+) w=\S+ n=\d+ o=(-?[\d.]+),(-?[\d.]+),(-?[\d.]+) dP=(-?[\d.]+) dY=(-?[\d.]+)")
DMG = re.compile(r"\] dmg t=([\d.]+) amt=([\d.]+) hg=(\d+) src=\d+ dist=([\d.]+) type=\d+ pos=(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)")


def main():
    rd, out = sys.argv[1:3]
    rows = []
    for fn in sorted(os.listdir(rd)):
        if not fn.startswith("b8_"): continue
        w = fn.split("_")[1]
        txt = open(os.path.join(rd, fn), encoding="utf-8").read()
        srv = txt.split("## client")[0]
        atks = [m for m in ATK.finditer(srv)]
        for d in DMG.finditer(srv):
            t = float(d.group(1))
            prev = [a for a in atks if float(a.group(1)) <= t]
            if not prev: continue
            a = prev[-1]
            ox, oy, oz = (float(a.group(i)) for i in (2, 3, 4))
            pitch = (float(a.group(5)) + 180) % 360 - 180; yaw = (float(a.group(6)) + 180) % 360 - 180
            hx, hy, hz = (float(d.group(i)) for i in (5, 6, 7))
            dist = math.hypot(hx - ox, hy - oy)
            line_z = oz - math.tan(math.radians(pitch)) * dist
            drop = line_z - hz
            v, gs, drag, zero = G[w]
            f = 0.5 * 750 * gs * (dist / v) ** 2
            rows.append([fn[:-4], f"{dist:.0f}", f"{dist / 39.37:.0f}", f"{pitch:.4f}", f"{drop:.2f}", f"{f:.2f}", f"{drop / f if f else float('nan'):.3f}", f"{t - float(a.group(1)):.3f}", f"{dist / v:.3f}", d.group(3), zero])
    with open(os.path.join(out, "B8-DROP.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tdist_u\tdist_m\tlaunch_pitch\tdrop_meas_u\tdrop_formula_u\tratio\tshot_to_damage_s\tflight_formula_s\thitgroup\tbolt_zero_distance\n")
        for r in rows: f.write("\t".join(map(str, r)) + "\n")
    print(len(rows))


if __name__ == "__main__":
    main()
