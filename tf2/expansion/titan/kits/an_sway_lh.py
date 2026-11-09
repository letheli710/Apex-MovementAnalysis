"""T-f: cockpit frame shift on screen for the light (Ronin), medium (Ion) and heavy (Legion) cockpits,
from the 11-03 g_sway screenshots (run 20261103_201719_g_sway, frames in local/titan-gaps/g_sway).
Each frame is template-matched against the same titan's idle frame on cockpit-only patches
(the patch boxes of ../full/an_frame.py). Prints shift (dx right+, dy down+) and the match score.
Usage: an_sway_lh.py <frame dir>"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "full"))
fd = sys.argv[1]
BOX = {'top': (430, 590, 0, 50), 'topR': (1180, 1275, 10, 150), 'left': (0, 50, 180, 320), 'botL': (170, 310, 665, 715), 'topL': (260, 430, 20, 70)}


def gray(f):
    return np.asarray(Image.open(f).convert('L'), float)


def match(ref, img, box, mx=90, my=60):
    x0, x1, y0, y1 = box
    tpl = ref[y0:y1, x0:x1]
    tpl = tpl - tpl.mean()
    nt = np.sqrt((tpl ** 2).sum()) + 1e-6
    best = (-2, 0, 0)
    H, W = img.shape
    for step, rx_, ry_, cx, cy in ((3, mx, my, 0, 0), (1, 4, 4, None, None)):
        if cx is None:
            cx, cy = best[1], best[2]
        for dy in range(cy - ry_, cy + ry_ + 1, step):
            for dx in range(cx - rx_, cx + rx_ + 1, step):
                a, b, e, f = y0 + dy, y1 + dy, x0 + dx, x1 + dx
                if a < 0 or e < 0 or b > H or f > W:
                    continue
                w = img[a:b, e:f]
                w = w - w.mean()
                s = (tpl * w).sum() / (nt * (np.sqrt((w ** 2).sum()) + 1e-6))
                if s > best[0]:
                    best = (s, dx, dy)
    return best


for cls in ("ion", "ronin", "legion"):
    ref = gray(os.path.join(fd, "t1_sw_%s_idle.jpg" % cls))
    for shot in ("turn30", "turn90", "turn210", "turn400", "landref", "land1", "land2", "hit"):
        f = os.path.join(fd, "t1_sw_%s_%s.jpg" % (cls, shot))
        if not os.path.exists(f):
            continue
        img = gray(f)
        s = "%-7s %-8s |" % (cls, shot)
        for k, b in BOX.items():
            m = match(ref, img, b)
            s += " %s:%+d,%+d(%.2f)" % (k, m[1], m[2], m[0])
        print(s)
