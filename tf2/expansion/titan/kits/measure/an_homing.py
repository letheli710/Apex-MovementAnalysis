"""Homing per client frame. For each missile (stitched): speed, turn rate omega (deg/s) of the velocity,
angle alpha between velocity and the line to the target, distance, and the homing strength implied by the
native rule (REF-NATIVE §10: every 1/60 s  dir = normalize(v + H * u)):  tan(theta) = H sin(a) / (|v| + H cos(a)),
theta = omega / 60  ->  H = |v| tan(theta) / (sin(a) - tan(theta) cos(a)).
Target: the foe's position (server TF, interpolated) + 0..235 centre height, or a fixed point (--point x y z).
Usage: py -3 -I an_homing.py <run dir> <tag> [step] [--point x y z]"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, sub, norm, dot  # noqa: E402
from an_expand import stitch  # noqa: E402

args = sys.argv[1:]
point = None
if "--point" in args:
    i = args.index("--point")
    point = tuple(float(x) for x in args[i + 1:i + 4])
    args = args[:i] + args[i + 4:]
run, tag = args[0], args[1]
step = float(args[2]) if len(args) > 2 else 0.05
r = Run(run)
a, b = r.tag(tag)
tracks = sorted(stitch(r, r.client_proj_in(a, b)), key=lambda t: t[0][0])
tf = [x for x in r.TF if x[1] == 0]


def foe_at(tc):
    ts = tc + r.offset
    best = min(tf, key=lambda x: abs(x[0] - ts)) if tf else None
    if best is None:
        return None
    # linear interpolation between the two nearest samples
    after = [x for x in tf if x[0] >= ts]
    before = [x for x in tf if x[0] < ts]
    if after and before:
        p, q = before[-1], after[0]
        w = (ts - p[0]) / (q[0] - p[0]) if q[0] > p[0] else 0
        return tuple(p[2 + k] + w * (q[2 + k] - p[2 + k]) for k in range(3))
    return tuple(best[2:5])


print("== %s: %d missiles" % (tag, len(tracks)))
for k, tr in enumerate(tracks):
    t0 = tr[0][0]
    print("-- missile %d launch +%.3f s, flight %.2f s" % (k, t0 - tracks[0][0][0], tr[-1][0] - t0))
    print("   t      dist   speed  alpha  omega(deg/s)  H_est")
    nxt = 0.0
    for i in range(3, len(tr) - 3):
        tm = tr[i][0] - t0
        if tm + 1e-6 < nxt:
            continue
        p0, p1, p2 = tr[i - 3], tr[i], tr[i + 3]
        v1 = sub(p1[1:], p0[1:])
        v2 = sub(p2[1:], p1[1:])
        dt1, dt2 = p1[0] - p0[0], p2[0] - p1[0]
        if dt1 <= 0 or dt2 <= 0 or norm(v1) < 1 or norm(v2) < 1:
            continue
        sp = norm(v2) / dt2
        if sp < 300:
            break
        ang = math.acos(max(-1.0, min(1.0, dot(v1, v2) / (norm(v1) * norm(v2)))))
        omega = ang / ((dt1 + dt2) / 2)
        tgt = point if point else foe_at(p1[0])
        if tgt is None:
            continue
        if not point:
            tgt = (tgt[0], tgt[1], tgt[2] + 120.0)
        u = sub(tgt, p1[1:])
        dist = norm(u)
        alpha = math.acos(max(-1.0, min(1.0, dot(v2, u) / (norm(v2) * dist)))) if dist > 1 else 0
        th = math.tan(omega / 60.0)
        den = math.sin(alpha) - th * math.cos(alpha)
        h = sp * th / den if den > 1e-3 else float("nan")
        print("  %5.3f  %6.0f  %5.0f  %5.1f  %7.1f  %7.0f" % (tm, dist, sp, math.degrees(alpha), math.degrees(omega), h))
        nxt += step
