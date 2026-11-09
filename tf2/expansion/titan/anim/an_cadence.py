"""Measured step cadence of a driven TF2 titan vs the clip's own cycle and root-motion speed.

Reads an existing runtime run (diag.tsv: HSDDIAG C = time, pos, vel ...; HSDDIAG BD = body
attachments every 4th frame; HSDDIAG TAG = segment start) and prints, per segment:
horizontal speed, foot lift-off period (left and right sole height), and the cycle the clip
would have if playback rate = speed / clip ground speed.
Usage: py -3 an_cadence.py <run dir> [segment-substring ...]
"""
import os
import statistics
import sys

CLIP = {  # clip cycle (s) and root-motion ground speed (u/s) per chassis, from out/seqgraph_*.csv
    "medium": {"walk": (1.133, 246.1), "sprint": (0.833, 437.6), "back": (0.80, 281.7), "crouch": (1.133, 245.8), "strafe": (1.133, 246.1)},
    "light": {"walk": (1.0, 274.1), "sprint": (0.833, 465.6), "back": (1.0, 274.1), "crouch": (1.0, 274.1), "strafe": (1.0, 274.1)},
    "heavy": {"walk": (1.133, 246.1), "sprint": (0.833, 441.1), "back": (0.80, 281.7), "crouch": (1.133, 246.1), "strafe": (1.133, 246.1)},
}
CHASSIS_OF = {"ion": "medium", "ronin": "light", "legion": "heavy"}


def load(run):
    C, BD, TAG = [], [], []
    with open(os.path.join(run, "diag.tsv"), encoding="utf-8", errors="replace") as f:
        for line in f:
            p = line.split()
            if len(p) < 3 or p[0] != "HSDDIAG":
                continue
            if p[1] == "C":
                C.append((float(p[2]), float(p[3]), float(p[4])))
            elif p[1] == "BD" and p[3] in ("foot_L_sole", "foot_R_sole"):
                BD.append((float(p[2]), p[3], float(p[9])))
            elif p[1] == "TAG":
                TAG.append((float(p[3]), p[2]))
    return C, BD, TAG


def liftoffs(series, thr):
    out = []
    up = False
    for t, z in series:
        if not up and z > thr:
            out.append(t)
            up = True
        elif up and z < thr - 2:
            up = False
    return out


def main():
    run = sys.argv[1]
    want = sys.argv[2:]
    C, BD, TAG = load(run)
    TAG.sort()
    for k, (t0, name) in enumerate(TAG):
        if want and not any(w in name for w in want):
            continue
        t1 = TAG[k + 1][0] if k + 1 < len(TAG) else t0 + 4
        a, b = t0 + 1.2, t1 - 0.2  # skip the start-up
        seg = [c for c in C if a <= c[0] <= b]
        if len(seg) < 20:
            continue
        v = ((seg[-1][1] - seg[0][1]) ** 2 + (seg[-1][2] - seg[0][2]) ** 2) ** 0.5 / (seg[-1][0] - seg[0][0])
        res = []
        for foot in ("foot_L_sole", "foot_R_sole"):
            s = [(t, z) for t, n, z in BD if n == foot and a <= t <= b]
            if len(s) < 10:
                continue
            zmin = min(z for _, z in s)
            lo = liftoffs(s, zmin + 6)
            if len(lo) >= 3:
                res.append(statistics.median([lo[i + 1] - lo[i] for i in range(len(lo) - 1)]))
        ch = next((CHASSIS_OF[x] for x in CHASSIS_OF if x in name), "medium")
        kind = next((x for x in CLIP[ch] if x in name), None)
        pred = ""
        if kind and res and v > 1:
            cyc, gs = CLIP[ch][kind]
            rate = v / gs
            pred = "clip %.3f s; rate v/gs %.2f -> cycle %.3f s; measured/clip %.2f" % (cyc, rate, cyc / rate, statistics.mean(res) / cyc)
        print("%-18s %-6s v %6.1f u/s  cycle L/R %s  %s" % (name, ch, v, " / ".join("%.3f" % x for x in res) or "-", pred))


if __name__ == "__main__":
    main()
