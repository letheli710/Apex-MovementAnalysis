#!/usr/bin/env python3
"""D-129 pictures from HSD.ShotgunScatterDump (PIL only): per shotgun, R5's fixed pattern against six random shots, on a wall 300 u ahead.
  py -3 -I plot_scatter.py <SCATTER-300U.tsv> <out dir>"""
import csv, os, sys
from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/msyh.ttc"
NAMES = {"mp_weapon_shotgun": "EVA-8", "mp_weapon_energy_shotgun": "和平捍卫者", "mp_weapon_mastiff": "獒犬", "mp_weapon_shotgun_pistol": "莫桑比克"}
CASES = {"hip": "腰射", "aimed": "开镜（图案收紧）", "choke4": "收束器 4 级"}
COLORS = [(214, 39, 40), (31, 119, 180), (44, 160, 44), (255, 127, 14), (148, 103, 189), (140, 86, 75)]
P = 360          # panel size, px


def main():
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    f18, f14, f12 = ImageFont.truetype(FONT, 20), ImageFont.truetype(FONT, 15), ImageFont.truetype(FONT, 12)
    for gun, name in NAMES.items():
        cases = [c for c in CASES if any(r["gun"] == gun and r["case"] == c for r in rows)]
        lim = max(max(abs(float(r["right"])), abs(float(r["up"]))) for r in rows if r["gun"] == gun) * 1.15
        W, H = 2 * P + 30, 50 + len(cases) * (P + 34)
        im = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(im)
        d.text((10, 10), f"{name}：300 u 墙上的落点（格子 5 u）", font=f18, fill="black")
        for i, c in enumerate(cases):
            sel = [r for r in rows if r["gun"] == gun and r["case"] == c]
            for j, kind in enumerate(("fixed", "random")):
                x0, y0 = 10 + j * (P + 10), 50 + i * (P + 34) + 24
                d.text((x0, y0 - 22), f"{CASES[c]}：" + ("R5 固定（6 枪完全重合）" if kind == "fixed" else "随机（6 枪，一枪一色）"), font=f14, fill="black")
                d.rectangle((x0, y0, x0 + P, y0 + P), outline=(160, 160, 160))
                sc = P / 2 / lim
                g = -int(lim // 5) * 5
                while g <= lim:
                    gx, gy = x0 + P / 2 + g * sc, y0 + P / 2 - g * sc
                    col = (200, 200, 200) if g == 0 else (238, 238, 238)
                    d.line((gx, y0, gx, y0 + P), fill=col); d.line((x0, gy, x0 + P, gy), fill=col)
                    g += 5
                for r in sel:
                    if r["kind"] != kind:
                        continue
                    px, py = x0 + P / 2 + float(r["right"]) * sc, y0 + P / 2 - float(r["up"]) * sc
                    rad = 6 if kind == "fixed" else 4
                    d.ellipse((px - rad, py - rad, px + rad, py + rad), fill=(0, 0, 0) if kind == "fixed" else COLORS[int(r["shot"]) % 6])
                d.text((x0 + 4, y0 + P - 16), f"±{lim:.0f} u", font=f12, fill=(120, 120, 120))
        im.save(os.path.join(out, f"scatter_{gun.replace('mp_weapon_', '')}.png"))
        print(gun)


if __name__ == "__main__":
    main()
