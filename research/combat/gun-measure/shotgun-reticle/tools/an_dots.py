#!/usr/bin/env python3
"""Measure synthetic projectile_hit_dot frames against a blank frame of the same view.
  py -3 -I an_dots.py <blank_full.png> <held_full.png> <ages comma list> [dist=300] [step=30]
Dots sit at world points (column i: right (i - (n-1)/2) * step, row up +step = normal, -step = crit) at dist ahead; the camera is 89 (4:3) on 1600x900.
Prints per dot: age, row, centre colour, peak difference, pixels over the threshold, the box they fill."""
import math, sys
from PIL import Image

blank = Image.open(sys.argv[1]).convert("RGB")
held = Image.open(sys.argv[2]).convert("RGB")
ages = [float(a) for a in sys.argv[3].split(",")]
dist = float(sys.argv[4]) if len(sys.argv) > 4 else 300.0
step = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
W, H = held.size
k = (H / 2) / (math.tan(math.radians(89 / 2)) * 0.75)       # pixels per unit tangent
n = len(ages)
print(f"k={k:.2f} px/tan")
print("age\trow\tx\ty\tpeak_rgb\tpeak_diff\tpix>40\tbox_w\tbox_h")
for i, age in enumerate(ages):
    for row, up in (("normal", step), ("crit", -step)):
        x = W / 2 + k * ((i - (n - 1) / 2) * step) / dist
        y = H / 2 - k * up / dist
        best, bp, cnt, xs, ys = 0, (0, 0, 0), 0, [], []
        for yy in range(int(y) - 9, int(y) + 10):
            for xx in range(int(x) - 9, int(x) + 10):
                a, b = held.getpixel((xx, yy)), blank.getpixel((xx, yy))
                d = max(abs(a[c] - b[c]) for c in range(3))
                if d > best:
                    best, bp = d, a
                if d > 40:
                    cnt += 1; xs.append(xx); ys.append(yy)
        bw = (max(xs) - min(xs) + 1) if xs else 0
        bh = (max(ys) - min(ys) + 1) if ys else 0
        print(f"{age}\t{row}\t{x:.1f}\t{y:.1f}\t{bp}\t{best}\t{cnt}\t{bw}\t{bh}")
