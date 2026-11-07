#!/usr/bin/env python3
"""Crosshair geometry from the hip screenshots (dark door behind the screen centre, 1600x900).
  py -3 -I an_reticle.py <dir with <gun>_<state>_full.png> [guns]
A pixel counts as crosshair when it is near white (min channel > 150) and much brighter than the same pixel of a frame with no weapon
(noweapon_full.png, same view), so the door lights and the blue centre ring drop out. Prints, per gun and state, the radius range of the
crosshair pixels from the centre, their bounding box, and the brightest colour. Also writes an ASCII map of the still frame."""
import math, os, sys
from PIL import Image

d = sys.argv[1]
guns = sys.argv[2:] or ["eva8", "mastiff", "peacekeeper", "mozambique"]
ref = Image.open(os.path.join(d, "..", "nw", "noweapon_full.png")).convert("RGB")
CX, CY, R = 800, 450, 75
print("gun\tstate\tn\tr_min\tr_med\tr_max\tx0\tx1\ty0\ty1\tpeak")
for g in guns:
    for st in ("still", "crouch", "walk", "air", "fired"):
        p = os.path.join(d, f"{g}_{st}_full.png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB")
        pts, peak = [], (0, 0, 0)
        for y in range(CY - R, CY + R):
            for x in range(CX - R, CX + R):
                a = im.getpixel((x, y))
                b = ref.getpixel((x, y))
                if min(a) > 150 and abs(a[0] - a[2]) < 40 and (st != "still" or min(b) < 110):
                    pts.append((x, y))
                    if sum(a) > sum(peak):
                        peak = a
        if not pts:
            print(f"{g}\t{st}\t0"); continue
        rs = sorted(math.hypot(x - CX + 0.5, y - CY + 0.5) for x, y in pts)
        xs = [x for x, _ in pts]; ys = [y for _, y in pts]
        print(f"{g}\t{st}\t{len(pts)}\t{rs[0]:.1f}\t{rs[len(rs)//2]:.1f}\t{rs[-1]:.1f}\t{min(xs)-CX}\t{max(xs)-CX}\t{min(ys)-CY}\t{max(ys)-CY}\t{peak}")
        if st == "still":
            s = set(pts)
            rows = []
            for y in range(CY - 45, CY + 46, 1):
                rows.append("".join("#" if (x, y) in s else "." for x in range(CX - 60, CX + 61)))
            open(os.path.join(d, f"{g}_still_ascii.txt"), "w").write("\n".join(rows) + "\n")
