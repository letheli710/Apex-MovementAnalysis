#!/usr/bin/env python3
"""One picture per gun from capture.py + measure.py, for a phone: the aimed picture, the hip picture, the side view with sights marked, close-ups.

  py -3 pages.py <run dir> <data dir> <out dir> [gun ...]
Colours: green = what the bodygroup switch removes (the raised sight parts), orange dashed = line of sight, red cross = ADS_CENTER attachment.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from measure import FPX, load, mask, clean, side_xy

FONT = "C:/Windows/Fonts/msyh.ttc"
F18 = ImageFont.truetype(FONT, 18)
F22 = ImageFont.truetype(FONT, 22)
F30 = ImageFont.truetype(FONT, 30)


def lab(im, t, font=F22):
    d = ImageDraw.Draw(im)
    w = d.textlength(t, font=font)
    d.rectangle((0, 0, w + 10, font.size + 12), fill=(12, 12, 16))
    d.text((5, 2), t, fill=(240, 240, 240), font=font)
    return im


def tint(rgb, m, col=(60, 255, 90), a=0.55):
    out = rgb.astype(np.float32).copy()
    out[m] = out[m] * (1 - a) + np.array(col, dtype=np.float32) * a
    return out.astype(np.uint8)


def keep_big(m):
    from scipy import ndimage as ndi
    l, n = ndi.label(m, structure=np.ones((3, 3)))
    if n == 0:
        return m
    s = ndi.sum(m, l, range(1, n + 1))
    k = np.zeros(n + 1, bool)
    k[1:] = s >= max(25, s.max() * 0.06)
    return k[l]


def overlay_side(d, name, sh, prof):
    b, o, n0 = load(d, name + "_base"), load(d, name + "_off"), load(d, name + "_none")
    if b is None:
        return None
    rgb = b.copy()
    if o is not None and n0 is not None:
        rgb = tint(b, keep_big(mask(b, n0) & ~mask(o, n0)))
    im = Image.fromarray(rgb.astype(np.uint8))
    dr = ImageDraw.Draw(im)
    L = prof.get("los")
    if L:
        import math
        th = math.radians(L["pitch"])
        def at(F):
            return (-L["mU"] + F * math.sin(th)) / math.cos(th)
        F0, F1 = -L["mF"], 0.0
        p0, p1 = side_xy(F0, at(F0), sh), side_xy(F1, at(F1), sh)
        n = 60
        for i in range(n):
            if i % 2 == 0:
                a = (p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n)
                b2 = (p0[0] + (p1[0] - p0[0]) * (i + 1) / n, p0[1] + (p1[1] - p0[1]) * (i + 1) / n)
                dr.line((a, b2), fill=(255, 150, 20), width=2)
    c = prof.get("ads_center")
    if c:
        x, y = side_xy(c[0], c[2], sh)
        dr.line((x - 9, y, x + 9, y), fill=(255, 30, 30), width=2)
        dr.line((x, y - 9, x, y + 9), fill=(255, 30, 30), width=2)
    x, y = side_xy(0, 0, sh)
    dr.ellipse((x - 4, y - 4, x + 4, y + 4), outline=(255, 255, 0), width=2)
    return im


def crop(im, cx, cy, w, h):
    x0 = int(max(min(cx - w / 2, 1600 - w), 0))
    y0 = int(max(min(cy - h / 2, 900 - h), 0))
    return im.crop((x0, y0, x0 + w, y0 + h))


def page(run, prof, g, out, names):
    d = os.path.join(run, g)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    p = prof.get(g, {})
    W = 1400
    rows = []
    # 1. aimed and hip
    ads, hip = os.path.join(d, "vm_ads_wall.png"), os.path.join(d, "vm_hip.png")
    if os.path.exists(ads):
        row = Image.new("RGB", (W, 394), (10, 10, 12))
        a = Image.open(ads).convert("RGB")
        a2 = a.crop((400, 225, 1200, 675)).resize((700, 394), Image.LANCZOS)
        dr = ImageDraw.Draw(a2)
        dr.line((342, 197, 358, 197), fill=(255, 0, 255), width=1)
        dr.line((350, 189, 350, 205), fill=(255, 0, 255), width=1)
        row.paste(lab(a2, "开镜（R5 实拍，亮度全开，紫十字 = 屏幕中心）"), (0, 0))
        row.paste(lab(Image.open(hip).convert("RGB").resize((700, 394), Image.LANCZOS), "腰射"), (700, 0))
        rows.append(row)
    # 2. full side
    sh = meta["shots"].get("side_full_base")
    if sh:
        im = overlay_side(d, "side_full", sh, p)
        x0, _ = side_xy(meta["F_extent"][1], 0, sh)
        x1, _ = side_xy(meta["F_extent"][0], 0, sh)
        arr = np.asarray(im)
        im2 = im.crop((max(int(x0) - 20, 0), 200, min(int(x1) + 20, 1600), 700))
        s = W / im2.width
        im2 = im2.resize((W, int(im2.height * s)), Image.LANCZOS)
        rows.append(lab(im2, "左侧全貌：绿 = 瞄具开关去掉的部分，橙虚线 = 视线，红十字 = 瞄准中心挂点，黄圈 = 枪口"))
    # 3. close-ups, front first
    idx = range(len(meta.get("foci", [])))
    for k in idx:
        sh = meta["shots"].get(f"side_{k}_base")
        if not sh:
            continue
        row = Image.new("RGB", (W, 350), (10, 10, 12))
        im = overlay_side(d, f"side_{k}", sh, p)
        f = sh["focus"]
        pp = p.get("parts", [{}] * 9)[k] if k < len(p.get("parts", [])) else {}
        cap = f"F≈{f[0]:.1f}"
        if "F" in pp and "U" in pp:
            cap = f"F {pp['F'][0]}..{pp['F'][1]} 顶 U {pp['U'][1]}"
            if "los_U" in pp:
                cap += f" 视线 {pp['los_U']:.2f}"
        row.paste(lab(crop(im, 800, 450, 560, 350), cap), (0, 0))
        b, o, n0 = load(d, f"back_{k}_base"), load(d, f"back_{k}_off"), load(d, f"back_{k}_none")
        rgb = b if o is None else tint(b, keep_big(mask(b, n0) & ~mask(o, n0)))
        row.paste(lab(crop(Image.fromarray(rgb.astype(np.uint8)), 800, 450, 420, 350), "从后往前"), (560, 0))
        q = Image.open(os.path.join(d, f"q34_{k}.png")).convert("RGB")
        row.paste(lab(crop(q, 800, 420, 420, 350), "左后上方"), (980, 0))
        rows.append(row)
    if not rows:
        return
    H = sum(r.height for r in rows) + 60
    s = Image.new("RGB", (W, H), (10, 10, 12))
    ImageDraw.Draw(s).text((12, 8), f"{names.get(g, g)}  ·  {meta['id']}  ·  {meta['vm'].split('/')[-1]}", fill=(255, 255, 255), font=F30)
    y = 60
    for r in rows:
        s.paste(r, (0, y))
        y += r.height
    s.save(os.path.join(out, g + ".png"), optimize=True)


def main():
    run, data, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    prof = json.load(open(os.path.join(data, "IS-PROFILES.json"), encoding="utf-8"))
    names = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "names.json"), encoding="utf-8"))
    guns = sys.argv[4:] or sorted(x for x in os.listdir(run) if os.path.exists(os.path.join(run, x, "meta.json")))
    for g in guns:
        page(run, prof, g, out, names)
        print(g, flush=True)


if __name__ == "__main__":
    main()
