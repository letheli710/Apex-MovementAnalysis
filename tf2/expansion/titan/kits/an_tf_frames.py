"""T-f (kit_e): cockpit frame shift on screen for dash, hit and pitch-while-moving, light / medium / heavy.
Each burst frame is matched against the same titan's idle frame on cockpit-only patches (boxes of ../full/an_frame.py).
Camera pitch / yaw / roll and pitch rate at the shot time come from the CAM log.
Usage: an_tf_frames.py <run dir> <frame dir>"""
import glob
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "full"))
from g_tools import load  # noqa: E402

run, fd = sys.argv[1], sys.argv[2]
d, c = load(run)
CAM = np.array([x[:8] for x in d['CAM']])
T = {}
for t, cmd in c:
    if cmd.startswith('jpeg t1_'):
        T[cmd.split()[1][3:]] = t
BOX = {'top': (430, 590, 0, 50), 'topL': (260, 430, 20, 70), 'botL': (170, 310, 665, 715)}


def gray(f):
    return np.asarray(Image.open(f).convert('L'), float)


def match(ref, img, box, mx=90, my=70):
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


for cls in ("ronin", "ion", "legion"):
    ref = gray(os.path.join(fd, "t1_tf_%s_idle_00.jpg" % cls))
    for kind in ("dashf", "dashr", "hit", "pu", "pd"):
        files = sorted(glob.glob(os.path.join(fd, "t1_tf_%s_%s_*.jpg" % (cls, kind))))
        if not files:
            continue
        t0 = T.get(os.path.basename(files[0])[3:-4], 0)
        print("\n%s %s" % (cls, kind))
        for f in files:
            n = os.path.basename(f)[3:-4]
            t = T.get(n, 0)
            i = min(np.searchsorted(CAM[:, 0], t), len(CAM) - 2)
            j = max(i - 7, 0)
            pr = (CAM[i + 1, 2] - CAM[j, 2]) / max(CAM[i + 1, 0] - CAM[j, 0], 1e-3)
            img = gray(f)
            s = "  +%.2f p=%+6.2f r=%+5.2f prate=%+6.0f |" % (t - t0, CAM[i, 2], CAM[i, 4], pr)
            for k, b in BOX.items():
                m = match(ref, img, b)
                s += " %s:%+d,%+d(%.2f)" % (k, m[1], m[2], m[0])
            print(s)
