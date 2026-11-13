#!/usr/bin/env python3
"""B10 / B3 screenshots: match engine screenshots (r2/screenshots, numbered) to the [RT] ss lines in time order, save PNG crops
(center 800x450 at full resolution for the crosshair, full frame at half size for the HUD) into the raw-data folder.
  py -3 -I shots_b10.py <screenshot dir> <first> <last> <runs dir> <out dir>   -> B10-SCREENS.tsv here"""
import os, re, sys
from PIL import Image
d, a, b, rd, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
labels = []
for fn in sorted(os.listdir(rd)):
    if fn.startswith("b10_"):
        for m in re.finditer(r"^\[RT\] ss (\S+) (\S+) t=([\d.]+)", open(os.path.join(rd, fn), encoding="utf-8").read(), re.M):
            labels.append((float(m.group(3)), m.group(1), m.group(2)))
labels.sort()
files = [f for f in sorted(os.listdir(d)) if f.endswith(".tga") and a <= int(re.search(r"(\d+)\.tga$", f).group(1)) <= b]
print(len(labels), len(files))
os.makedirs(os.path.join(out, "b10"), exist_ok=True)
rows = []
for (t, g, v), f in zip(labels, files):
    im = Image.open(os.path.join(d, f)).convert("RGB")
    im.crop((400, 225, 1200, 675)).save(os.path.join(out, "b10", f"{g}_{v}_center.png"))
    im.resize((800, 450)).save(os.path.join(out, "b10", f"{g}_{v}_full.png"))
    rows.append(f"{g}\t{v}\t{t:.3f}\t{f}\tscreens/b10/{g}_{v}_center.png")
open("B10-SCREENS.tsv", "w", encoding="utf-8").write("gun\tview\tgame_t\tsource_tga\tcrop\n" + "\n".join(rows) + "\n")
