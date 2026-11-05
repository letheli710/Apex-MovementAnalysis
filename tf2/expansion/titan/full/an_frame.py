"""Cockpit frame position on screen, from g_frame bursts: template match of cockpit-only patches against the idle frame.
Usage: an_frame.py <run dir> <frame dir> [regex]
Prints, per frame: time, camera pitch/yaw rate from the log, and the patch shift in pixels (dx right+, dy down+), with match score."""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from g_tools import load
import numpy as np
from PIL import Image

run, fd = sys.argv[1], sys.argv[2]
rx = re.compile(sys.argv[3] if len(sys.argv) > 3 else '.')
d, c = load(run)
CAM = np.array([x[:8] for x in d['CAM']])
T = {}
for t, cmd in c:
    if cmd.startswith('jpeg t1_'):
        T[cmd.split()[1][3:]] = t
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


ref = gray(os.path.join(fd, 't1_idle_00.jpg'))
print("frame t dpitch dyaw/s | " + " ".join(BOX))
for f in sorted(glob.glob(os.path.join(fd, 't1_*.jpg'))):
    n = os.path.basename(f)[3:-4]
    if not rx.search(n):
        continue
    img = gray(f)
    t = T.get(n, 0)
    i = np.searchsorted(CAM[:, 0], t)
    i = min(i, len(CAM) - 2)
    yr = ((CAM[i + 1, 3] - CAM[max(i - 5, 0), 3] + 180) % 360 - 180) / max(CAM[i + 1, 0] - CAM[max(i - 5, 0), 0], 1e-3)
    s = f"{n:14s} {t:7.2f} p={CAM[i, 2]:+6.2f} r={CAM[i, 4]:+5.2f} yr={yr:+6.0f} |"
    for k, b in BOX.items():
        m = match(ref, img, b)
        s += f" {k}:{m[1]:+d},{m[2]:+d}({m[0]:.2f})"
    print(s)
