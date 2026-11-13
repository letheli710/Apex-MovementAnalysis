"""Expand / contract missile paths (salvo rockets, multi-target missiles with no lock) from the client per-frame
projectile log. The local player's predicted missile lives ~0.1 s and is then replaced by the server's entity:
both are stitched by position. For each missile: signed radial angle of the velocity (+ = away from the aim line,
along the missile's own azimuth), lateral offset, speed, per 0.01 s bins averaged over missiles.
Usage: py -3 -I an_expand.py <run dir> <tag> [<tag> ...]"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, basis, dot, sub, norm  # noqa: E402


def stitch(r, hs):
    tracks = []
    for h in hs:
        pts = r.pj[h]
        if not pts:
            continue
        joined = False
        for tr in tracks:
            t, x, y, z = tr[-1]
            t2, x2, y2, z2 = pts[0]
            if 0 <= t2 - t < 0.05 and norm((x2 - x, y2 - y, z2 - z)) < 2200 * (t2 - t) + 40 and len(tr) < 40:
                tr.extend(p for p in pts if p[0] > t)
                joined = True
                break
            # server copy can start before the predicted one ended: match by position at the same time
            for p in tr:
                if abs(p[0] - t2) < 0.004 and norm((p[1] - x2, p[2] - y2, p[3] - z2)) < 25:
                    tr[:] = [q for q in tr if q[0] < t2] + list(pts)
                    joined = True
                    break
            if joined:
                break
        if not joined:
            tracks.append(list(pts))
    return [tr for tr in tracks if len(tr) > 5]


def analyse(r, tag, show_each=False):
    a, b = r.tag(tag)
    hs = r.client_proj_in(a, b)
    tracks = stitch(r, hs)
    tracks.sort(key=lambda tr: tr[0][0])
    t_first = tracks[0][0][0]
    pc = r.pc_at(t_first)
    eye = tuple(pc[10:13])
    f, rt, up = basis(pc[8], pc[9])
    print("\n== %s: %d client entities -> %d missiles; eye pitch %.1f yaw %.1f" % (tag, len(hs), len(tracks), pc[8], pc[9]))
    bins = {}
    summary = []
    for k, tr in enumerate(tracks):
        t0 = tr[0][0]
        # azimuth from the first 0.08 s of flight (the outward leg)
        early = [p for p in tr if p[0] - t0 <= 0.08]
        d = sub(early[-1][1:], tr[0][1:])
        az = math.atan2(dot(d, up), dot(d, rt))
        radial = tuple(math.cos(az) * rt[i] + math.sin(az) * up[i] for i in range(3))
        rows = []
        for i in range(2, len(tr)):
            p0, p1 = tr[i - 2], tr[i]
            dt = p1[0] - p0[0]
            if dt <= 0:
                continue
            v = sub(p1[1:], p0[1:])
            sp = norm(v) / dt
            if sp < 500:
                break  # hit something
            ang = math.degrees(math.atan2(dot(v, radial), dot(v, f)))
            side = math.degrees(math.atan2(dot(v, (radial[1] * f[2] - radial[2] * f[1], radial[2] * f[0] - radial[0] * f[2], radial[0] * f[1] - radial[1] * f[0])), dot(v, f)))
            tm = (p1[0] + p0[0]) / 2 - t0
            off = dot(sub(p1[1:], eye), radial)
            rows.append((tm, ang, side, off, sp, dot(sub(p1[1:], eye), f)))
            bins.setdefault(round(tm, 2), []).append((ang, side, off, sp))
        peak = max(rows, key=lambda x: x[3]) if rows else None
        summary.append((k, t0 - t_first, math.degrees(az), rows[-1][0] if rows else 0, peak))
        if show_each:
            for row in rows[::4]:
                print("   m%d %.3f rad %+6.2f side %+5.2f off %+6.1f v %5.0f fwd %6.0f" % ((k,) + row))
    print("  missile  launch  azimuth  flight(s)  peak outward offset (t, fwd)")
    for k, tl, az, fl, pk in summary:
        print("  %d  +%.3f  %6.1f  %.2f  %s" % (k, tl, az, fl, "%.1f u at %.3f s, fwd %.0f" % (pk[3], pk[0], pk[5]) if pk else "-"))
    print("  t(s)  radial angle mean (min..max)  side angle  outward offset  speed   n")
    for tm in sorted(bins):
        if tm > 1.2:
            break
        xs = bins[tm]
        ra = [x[0] for x in xs]
        print("  %.2f  %+6.2f (%+6.2f..%+6.2f)  %+5.2f  %+6.1f  %5.0f  %d" % (tm, sum(ra) / len(ra), min(ra), max(ra),
              sum(x[1] for x in xs) / len(xs), sum(x[2] for x in xs) / len(xs), sum(x[3] for x in xs) / len(xs), len(xs)))
    return tracks


if __name__ == "__main__":
    r = Run(sys.argv[1])
    for tag in sys.argv[2:]:
        if r.tag(tag):
            analyse(r, tag)
