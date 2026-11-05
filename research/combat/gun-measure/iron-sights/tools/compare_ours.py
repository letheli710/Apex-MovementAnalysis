#!/usr/bin/env python3
"""R5's sights against our pilot model, same cameras (capture.py, render_ours.py): R5, overlay, ours.
  py -3 compare_ours.py <run dir> <renders dir> <out dir> r301 wingman peacekeeper"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
F = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
run, rd, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
UNITY = r"C:\Workspace\Playground\ReApex-DataAnalysis\HSD-Unity-GUNMODEL\Docs\gun-models\pilot"
PARTS = {"r301": [0, 2], "wingman": [0, 1], "peacekeeper": [0, 1]}   # the front and rear close-ups of capture.py
NAMES = {"r301": "R-301", "wingman": "Wingman", "peacekeeper": "Peacekeeper"}


def lab(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, d.textlength(t, font=F) + 10, 34), fill=(12, 12, 16))
    d.text((5, 2), t, fill=(240, 240, 240), font=F)
    return im


def over(r5, ours):
    """R5 under a see-through copy of ours with its outline in red."""
    o = Image.open(ours).convert("RGBA")
    s = r5.convert("RGBA")
    a = np.asarray(o.split()[3]) > 40
    edge = a ^ ndi.binary_erosion(a, iterations=2)
    o2 = o.copy()
    o2.putalpha(o.split()[3].point(lambda v: int(v * 0.35)))
    s.alpha_composite(o2)
    arr = np.asarray(s.convert("RGB")).copy()
    arr[edge] = (255, 40, 40)
    return Image.fromarray(arr)


def plain(ours, bg=(150, 155, 165)):
    o = Image.open(ours).convert("RGBA")
    s = Image.new("RGBA", o.size, bg + (255,))
    s.alpha_composite(o)
    return s.convert("RGB")


def row(r5, ours, box, title, W=1400):
    w, h = box[2] - box[0], box[3] - box[1]
    cw = W // 3
    ch = int(h * cw / w)
    im = Image.new("RGB", (W, ch), (12, 12, 16))
    for i, (x, t) in enumerate(((r5.convert("RGB"), "R5"), (over(r5, ours), "叠图（红框 = 我们）"), (plain(ours), "我们"))):
        c = x.crop(box).resize((cw, ch), Image.LANCZOS)
        im.paste(lab(c, f"{title} · {t}" if i == 0 else t), (i * cw, 0))
    return im


for g in sys.argv[4:]:
    d = os.path.join(run, g)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    rows = []
    def r5(n):
        return Image.open(os.path.join(d, n + ".png"))
    idx = PARTS[g]
    rows.append(row(r5("side_full_base"), os.path.join(rd, f"{g}_side_full.png"), (0, 200, 1600, 750), "左侧全貌"))
    # aimed: R5, our model at R5's aimed pose and view model FOV, Unity as it is now (pilot sheet)
    box = (400, 225, 1200, 675)
    a = r5("vm_ads_wall").convert("RGB").crop(box)
    ey = Image.open(os.path.join(rd, f"{g}_eye_r5.png")).convert("RGBA")
    bg = r5("vm_ads_wall").convert("RGBA")
    # the same wall behind ours: R5's gun cannot be removed from this picture, so a plain panel
    plain_bg = Image.new("RGBA", ey.size, (190, 195, 200, 255))
    plain_bg.alpha_composite(ey)
    b = plain_bg.convert("RGB").crop(box)
    pil = sys.argv[-1]
    aimed = Image.new("RGB", (1400, 262), (12, 12, 16))
    aimed.paste(lab(a.resize((466, 262), Image.LANCZOS), "开镜 · R5"), (0, 0))
    aimed.paste(lab(b.resize((466, 262), Image.LANCZOS), "我们的模型放到 R5 开镜位置"), (467, 0))
    gp = os.path.join(UNITY, f"game-{g}.png")
    if os.path.exists(gp):
        gg = Image.open(gp).convert("RGB").crop((640, 360, 1280, 720)).crop((160, 90, 480, 270))
        aimed.paste(lab(gg.resize((466, 262), Image.LANCZOS), "Unity 现状（枪在准星下方）"), (934, 0))
    rows.append(aimed)
    for k in idx:
        tag = "前瞄" if k == idx[0] else "后瞄"
        foc = meta["shots"][f"side_{k}_base"]["focus"][0]
        rows.append(row(r5(f"side_{k}_base"), os.path.join(rd, f"{g}_side_{k}.png"), (480, 250, 1120, 650), f"{tag} 侧视 F≈{foc:.1f}"))
        rows.append(row(r5(f"back_{k}_base"), os.path.join(rd, f"{g}_back_{k}.png"), (560, 230, 1040, 670), f"{tag} 从后往前"))
        rows.append(row(r5(f"top_{k}_base"), os.path.join(rd, f"{g}_top_{k}.png"), (480, 250, 1120, 650), f"{tag} 俯视"))
    H = sum(r.height for r in rows) + 56
    s = Image.new("RGB", (1400, H), (12, 12, 16))
    ImageDraw.Draw(s).text((10, 8), f"{NAMES.get(g, g)}：R5 基瞄 vs 我们的模型（相机相同）", fill=(255, 255, 255), font=F)
    y = 56
    for r in rows:
        s.paste(r, (0, y))
        y += r.height
    s.save(os.path.join(out, f"compare-{g}.png"), optimize=True)
    print(g, s.size)
