"""Server-side (10 Hz) projectile tracks per tag: class / weapon, launch speed, speed change, vertical
acceleration fit (gravity), life, path bend; client-stitched missiles where present.
Usage: py -3 -I an_proj.py <run dir> <tag> ..."""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, norm  # noqa: E402


def fit_az(pts):
    """least squares vz = a + g t over the samples -> g (u/s^2)"""
    ts = [p[0] for p in pts]
    vz = [p[6] for p in pts]
    n = len(ts)
    if n < 3:
        return float("nan")
    mt, mv = sum(ts) / n, sum(vz) / n
    den = sum((t - mt) ** 2 for t in ts)
    return sum((t - mt) * (v - mv) for t, v in zip(ts, vz)) / den if den else float("nan")


r = Run(sys.argv[1])
for tag in sys.argv[2:]:
    if not r.tag(tag):
        continue
    a, b = r.tag(tag)
    hs = r.server_proj_in(a, b)
    print("\n== %s: %d server projectiles" % (tag, len(hs)))
    for h in hs:
        nw = r.ps_new[h]
        pts = r.ps[h]
        t0 = pts[0][0]
        sp = [norm(p[4:7]) for p in pts]
        moving = [p for p, s in zip(pts, sp) if s > 50]
        g = fit_az(moving) if len(moving) >= 3 else float("nan")
        v0 = pts[0][4:7]
        ang0 = math.degrees(math.atan2(v0[2], math.hypot(v0[0], v0[1])))
        # heading change over the flight
        hd = [math.degrees(math.atan2(p[5], p[4])) for p in moving]
        dist = norm((pts[-1][1] - pts[0][1], pts[-1][2] - pts[0][2], pts[-1][3] - pts[0][3]))
        print("  h=%d %s %s owner %s: n=%d first +%.2f s, life>=%.2f s, speed %0.f -> %0.f, launch pitch %+.2f deg, vz' %.1f u/s2, heading %s, travelled %.0f u" % (
            h, nw[1], nw[2], nw[3], len(pts), t0 - r.offset - a, pts[-1][0] - t0, sp[0], sp[-1], ang0, g,
            "%.1f->%.1f" % (hd[0], hd[-1]) if hd else "-", dist))
