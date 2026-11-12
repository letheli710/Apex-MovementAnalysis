"""1/4-size copies of the lineup silhouettes (Blender's Python has no PIL).  py -3 build_lineup_quarter.py [dir]"""
import os
import sys

from PIL import Image

d = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
for n in ("lineup_sil_front", "lineup_sil_3q", "lineup_colour_front"):
    p = os.path.join(d, n + ".png")
    if os.path.exists(p):
        im = Image.open(p)
        im.resize((im.width // 4, im.height // 4), Image.LANCZOS).save(os.path.join(d, n + "_quarter.png"))
        print(n, im.size, "->", (im.width // 4, im.height // 4))
