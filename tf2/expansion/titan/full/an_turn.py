"""Foot steps during real-key turns. Usage: an_turn.py <run dir> <tag regex>
For each tagged window: when each foot starts to move (attachment speed relative to the titan origin),
the view yaw change at that moment, and how far the legs had fallen behind the view."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from g_tools import load, tags
import numpy as np


def wrap(a):
    return (a + 180) % 360 - 180


def steps(F, thresh=25.0, gap=0.08):
    """F: array t x y z (relative to origin). returns list of (t0, t1, dist, lift)"""
    t = F[:, 0]
    v = np.hypot(np.gradient(F[:, 1], t), np.gradient(F[:, 2], t))
    mov = v > thresh
    out = []
    i = 0
    while i < len(t):
        if mov[i]:
            j = i
            while j + 1 < len(t) and (mov[j + 1] or (j + 2 < len(t) and mov[j + 2])):
                j += 1
            if t[j] - t[i] > gap:
                d = np.hypot(F[j, 1] - F[i, 1], F[j, 2] - F[i, 2])
                out.append((t[i], t[j], d, F[i:j + 1, 3].max() - min(F[i, 3], F[j, 3])))
            i = j + 1
        else:
            i += 1
    return out


def main():
    d, c = load(sys.argv[1])
    rx = re.compile(sys.argv[2])
    CAM = np.array([x[:8] for x in d['CAM']])
    L = np.array([x[:7] for x in d['BD_foot_L_sole']])
    R = np.array([x[:7] for x in d['BD_foot_R_sole']])
    CH = np.array([x[:7] for x in d['BD_CHESTFOCUS']])
    print("tag | view_total | first-step view_yaw | legs lag at step | steps: foot t yaw dist dur")
    for a, b, n in tags(c):
        if not rx.search(n):
            continue
        K = CAM[(CAM[:, 0] >= a) & (CAM[:, 0] < b)]
        if len(K) < 10:
            continue
        y0 = K[0, 3]
        vy = wrap(K[:, 3] - y0)
        vy = np.unwrap(np.radians(vy))
        vy = np.degrees(vy)
        lf = L[(L[:, 0] >= a) & (L[:, 0] < b)]
        rf = R[(R[:, 0] >= a) & (R[:, 0] < b)]
        ch = CH[(CH[:, 0] >= a) & (CH[:, 0] < b)]
        if len(lf) < 5:
            continue
        # BD columns: t pitch yaw roll x y z
        lxy = lf[:, [0, 4, 5, 6]]
        rxy = rf[:, [0, 4, 5, 6]]
        ev = [("L", *s) for s in steps(lxy)] + [("R", *s) for s in steps(rxy)]
        ev.sort(key=lambda e: e[1])
        # legs yaw from the line between the feet
        fy = np.degrees(np.unwrap(np.arctan2(lxy[:, 2] - np.interp(lxy[:, 0], rxy[:, 0], rxy[:, 2]), lxy[:, 1] - np.interp(lxy[:, 0], rxy[:, 0], rxy[:, 1]))))
        fy = fy - fy[0]
        chy = np.degrees(np.unwrap(np.radians(wrap(ch[:, 2] - ch[0, 2]))))
        chest_lag = np.interp(ch[:, 0], K[:, 0], vy) - chy
        s = f"{n:18s} view {vy[np.argmax(np.abs(vy))]:+7.1f} chestlag max {chest_lag[np.argmax(np.abs(chest_lag))]:+5.1f} end {chest_lag[-1]:+5.1f} feetline end {fy[-1]:+6.1f} |"
        for e in ev:
            ti = e[1]
            s += f" {e[0]} t={ti - a:.2f} view={np.interp(ti, K[:, 0], vy):+.0f} feet={np.interp(ti, lxy[:, 0], fy):+.0f} d={e[3]:.0f} dur={e[2] - e[1]:.2f};"
        print(s)


main()
