"""Black silhouettes side by side at one scale, full size and 1/4 (SPEC 5 check 1). No Blender.

  py -3 compose_lineup.py

Reads (does not change): L1/L2 r4_final (ortho 12 m / 1000 px), ../M1/silhouette_r2 and ../H/H1/r4_final (ortho 9.6 m / 1000 px).
The orange 1.8 m block is removed; every titan is bottom-aligned on one ground line. Output: lineup/ in this folder.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "lineup")
os.makedirs(OUT, exist_ok=True)
PX_PER_M = 1000 / 12.0
SRC = [("L-1 北辰", os.path.join(HERE, "L1", "r4_final"), 12.0), ("L-2 浪人", os.path.join(HERE, "L2", "r4_final"), 12.0),
       ("M-1 棱镜", os.path.join(HERE, "..", "M1", "silhouette_r2"), 9.6), ("H-1 熔炉", os.path.join(HERE, "..", "H", "H1", "r4_final"), 9.6)]


def black_only(im):
    """Keep near-black pixels (the titan), white elsewhere (drops the orange block)."""
    g = im.convert("RGB")
    px = g.load()
    for y in range(g.height):
        for x in range(g.width):
            r, gg, b = px[x, y]
            px[x, y] = (0, 0, 0) if max(r, gg, b) < 60 else (255, 255, 255)
    return g


def main():
    font = None
    for f in ("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"):
        if os.path.exists(f):
            font = ImageFont.truetype(f, 46)
            break
    for view in ("front", "side", "back", "3q"):
        cells = []
        for label, d, ortho in SRC:
            p = os.path.join(d, "sil_%s.png" % view)
            if not os.path.exists(p):
                continue
            im = black_only(Image.open(p))
            if view != "3q":
                s = (1000 / ortho) / PX_PER_M
                im = im.resize((round(im.width / s), round(im.height / s)), Image.LANCZOS) if abs(s - 1) > 1e-6 else im
            bb = Image.eval(im.convert("L"), lambda v: 255 if v < 128 else 0).getbbox()
            cells.append((label, im.crop((bb[0] - 20, bb[1] - 20, bb[2] + 20, bb[3]))))
        if not cells:
            continue
        H = max(c.height for _, c in cells) + 90
        W = sum(c.width for _, c in cells) + 40 * (len(cells) + 1)
        sheet = Image.new("RGB", (W, H + 30), "white")
        dr = ImageDraw.Draw(sheet)
        x = 40
        for label, c in cells:
            sheet.paste(c, (x, H - c.height + 10))
            dr.text((x, 10), label, fill=(200, 40, 20), font=font)
            x += c.width + 40
        sheet.save(os.path.join(OUT, "sil_lineup_%s.png" % view))
        sheet.resize((sheet.width // 4, sheet.height // 4), Image.LANCZOS).save(os.path.join(OUT, "sil_lineup_%s_quarter.png" % view))
        print(view, [l for l, _ in cells], sheet.size)


main()
