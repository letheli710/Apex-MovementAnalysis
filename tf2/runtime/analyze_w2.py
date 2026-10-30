"""W2 analysis helpers: per-frame client rows in a time window (expansion/w2/W2-REPORT.md)."""
import math
import sys


def load(path):
    C, other = [], []
    for l in open(path, encoding="utf-8", errors="replace"):
        r = l.split()
        if l.startswith("HSDDIAG C ") and len(r) >= 18:
            C.append((float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[6]), float(r[7]), float(r[8]),
                      int(r[11]), int(r[17])))
        else:
            other.append(r)
    return C, other


def show(C, t0, t1, step=0.25):
    nxt = t0
    for i, r in enumerate(C):
        if r[0] < t0:
            continue
        if r[0] > t1:
            break
        if r[0] >= nxt:
            j = i
            while j < len(C) - 1 and C[j][0] - r[0] < 0.1:
                j += 1
            dt = C[j][0] - r[0]
            az = (C[j][6] - r[6]) / dt if dt > 0 else 0
            ah = (math.hypot(C[j][4], C[j][5]) - math.hypot(r[4], r[5])) / dt if dt > 0 else 0
            print("%.2f x=%.1f y=%.1f z=%.1f vz=%.1f az=%.0f h=%.1f ah=%.0f vx=%.1f vy=%.1f g=%d b=%d" % (
                r[0], r[1], r[2], r[3], r[6], az, math.hypot(r[4], r[5]), ah, r[4], r[5], r[7], r[8]))
            nxt += step


if __name__ == "__main__":
    C, _ = load(sys.argv[1])
    show(C, float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]) if len(sys.argv) > 4 else 0.25)


def phases(C, t0, t1, g=600.0, tol=60.0):
    """segments of airborne frames by vertical accel class: 'g' (free fall), 'h' (|az| < g-tol)."""
    out, cur, start = [], None, None
    for a, b in zip(C, C[1:]):
        if a[0] < t0 or b[0] > t1:
            continue
        dt = b[0] - a[0]
        if dt <= 0:
            continue
        az = (b[6] - a[6]) / dt
        k = "ground" if b[7] else ("g" if abs(az + g) < tol else ("h" if abs(az) < g - tol else "x"))
        if k != cur:
            if cur is not None:
                out.append((cur, start, a[0]))
            cur, start = k, a[0]
    out.append((cur, start, t1))
    return out
