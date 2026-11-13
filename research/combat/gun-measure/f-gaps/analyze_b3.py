#!/usr/bin/env python3
"""B3: muzzle flash on screen from engine screenshots taken k frames after single shots (gen_b3.py), plus the particle lifetimes (fx_life.nut).
  py -3 -I analyze_b3.py <screenshot dir> <first index> <runs dir> <out dir>  ->  B3-FLASH.tsv, B3-FXLIFE.tsv
Screens are matched to the runs' [RT] shot lines in order (one baseline k=-1 per run). Region: the muzzle area of the hip view
(x 600..1000, y 150..480 of 1600x900). bright_px = pixels whose luminance rose by > 60 against that run's baseline; sum_excess = summed rise of those."""
import os, re, sys
from PIL import Image, ImageChops


def lum(im):
    return im.convert("L")


def main():
    sd, first, rd, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    files = sorted(f for f in os.listdir(sd) if f.endswith(".tga"))
    files = [f for f in files if int(re.search(r"(\d+)\.tga$", f).group(1)) >= first]
    runs = sorted(f for f in os.listdir(rd) if f.startswith("b3_"))
    order = []
    for fn in runs:
        for m in re.finditer(r"^\[RT\] shot k=(-?\d+)(?: dt=([\d.]+))?", open(os.path.join(rd, fn), encoding="utf-8").read(), re.M):
            order.append((fn[:-4], int(m.group(1)), float(m.group(2)) if m.group(2) else -1))
    box = (600, 150, 1000, 480)
    rows, base = [], None
    for (run, k, dt), f in zip(order, files):
        im = lum(Image.open(os.path.join(sd, f)).crop(box))
        if k == -1:
            base = im; rows.append([run, k, "", f, 0, 0]); continue
        d = ImageChops.subtract(im, base)
        px = [v for v in d.getdata() if v > 60]
        rows.append([run, k, f"{dt:.4f}", f, len(px), sum(px)])
    with open(os.path.join(out, "B3-FLASH.tsv"), "w", encoding="utf-8") as fo:
        fo.write("run\tk_frames\tt_after_shot_s\tscreenshot\tbright_px\tsum_excess\n")
        for r in rows: fo.write("\t".join(map(str, r)) + "\n")
    L = []
    for fn in os.listdir(rd):
        if fn.startswith("b3_fx_life"):
            for m in re.finditer(r"fx (\S+) life=([\d.]+) frames=(\d+)", open(os.path.join(rd, fn), encoding="utf-8").read()):
                L.append(m.groups())
    with open(os.path.join(out, "B3-FXLIFE.tsv"), "w", encoding="utf-8") as fo:
        fo.write("particle_system\tlife_s\tframes\n")
        for r in L: fo.write("\t".join(r) + "\n")
    print(len(rows), "screens", len(L), "fx rows")


if __name__ == "__main__":
    main()
