"""Homing strength from each missile's own impact point (fixed-point homing, e.g. flight core rockets):
per 0.05 s bin over missiles: distance, speed, alpha (velocity vs line to the impact point), turn rate, H_est
(per 1/60 s tick: tan(theta) = H sin(a) / (|v| + H cos(a))). Usage: py -3 -I an_homing_end.py <run> <tag> [xmin]"""
import math
import os
import statistics
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, sub, norm, dot  # noqa: E402
from an_expand import stitch  # noqa: E402

r = Run(sys.argv[1])
a, b = r.tag(sys.argv[2])
xmin = float(sys.argv[3]) if len(sys.argv) > 3 else -1e9
trs = [t for t in stitch(r, r.client_proj_in(a, b)) if t[-1][1] > xmin]
print("== %s: %d missiles (end x > %g)" % (sys.argv[2], len(trs), xmin))
bins = {}
for t in trs:
    t0 = t[0][0]
    tgt = t[-1][1:]
    for i in range(3, len(t) - 3):
        p0, p1, p2 = t[i - 3], t[i], t[i + 3]
        v1, v2 = sub(p1[1:], p0[1:]), sub(p2[1:], p1[1:])
        d1, d2 = p1[0] - p0[0], p2[0] - p1[0]
        if d1 <= 0 or d2 <= 0 or norm(v1) < 1 or norm(v2) < 1:
            continue
        sp = norm(v2) / d2
        if sp < 500:
            break
        om = math.acos(max(-1, min(1, dot(v1, v2) / (norm(v1) * norm(v2))))) / ((d1 + d2) / 2)
        u = sub(tgt, p1[1:])
        dist = norm(u)
        if dist < 60:
            break
        al = math.acos(max(-1, min(1, dot(v2, u) / (norm(v2) * dist))))
        th = math.tan(om / 60)
        den = math.sin(al) - th * math.cos(al)
        h = sp * th / den if den > 1e-3 else float("nan")
        bins.setdefault(round(round((p1[0] - t0) / 0.05) * 0.05, 2), []).append((dist, sp, math.degrees(al), math.degrees(om), h))
print("  t     n   dist  speed  alpha  omega(deg/s)  H_est(median)")
for k in sorted(bins):
    xs = bins[k]
    hs = sorted(x[4] for x in xs if x[4] == x[4])
    print("  %.2f  %3d  %5.0f  %5.0f  %5.1f  %6.1f  %6.0f" % (k, len(xs), statistics.mean(x[0] for x in xs), statistics.mean(x[1] for x in xs),
          statistics.mean(x[2] for x in xs), statistics.mean(x[3] for x in xs), hs[len(hs) // 2] if hs else float("nan")))
