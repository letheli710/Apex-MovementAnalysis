"""km_monarch: salvo rocket paths in the view frame (client per frame), multi-target lock fractions, damage.
Usage: py -3 -I an_km_monarch.py <run dir>"""
import math
import os
sys_path_fix = None
import sys

import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, basis, dot, sub, norm

r = Run(sys.argv[1])


def paths(tag, show=True, step=0.025):
    a, b = r.tag(tag)
    hs = r.client_proj_in(a, b)
    print("\n== %s: %d projectiles (client)" % (tag, len(hs)))
    t_first = r.pj_new[hs[0]][0] if hs else a
    pc = r.pc_at(t_first)
    eye = tuple(pc[10:13])
    f, rt, up = basis(pc[8], pc[9])
    out = []
    for k, h in enumerate(hs):
        pts = r.pj[h]
        t0 = pts[0][0]
        rows = []
        prev = None
        for t, x, y, z in pts:
            d = sub((x, y, z), eye)
            fw, rr, uu = dot(d, f), dot(d, rt), dot(d, up)
            ang = math.degrees(math.atan2(math.hypot(rr, uu), fw))      # angle off the aim line seen from the eye
            az = math.degrees(math.atan2(uu, rr))
            vdeg = spd = float("nan")
            if prev and t > prev[0]:
                v = sub((x, y, z), prev[1:])
                dt = t - prev[0]
                spd = norm(v) / dt
                vdeg = math.degrees(math.acos(max(-1, min(1, dot(v, f) / max(norm(v), 1e-9)))))
            rows.append((t - t0, fw, rr, uu, ang, az, vdeg, spd))
            prev = (t, x, y, z)
        end = r.pj_end.get(h, pts[-1][0])
        out.append((h, t0 - t_first, rows, end - t0))
        if show:
            print("-- missile %d h=%d weapon=%s  launch +%.3f s  life %.2f s  first pos fwd %.0f right %.0f up %.0f" % (
                k, h, r.pj_new[h][2], t0 - t_first, end - t0, rows[0][1], rows[0][2], rows[0][3]))
            print("   t     fwd     right    up    offAxis  azim   velAngle  speed")
            nxt = 0.0
            for row in rows:
                if row[0] + 1e-6 >= nxt:
                    print("  %.3f %7.1f %7.1f %7.1f %6.2f %7.1f %7.2f %7.0f" % row)
                    nxt += step
                if row[0] > 1.0:
                    break
    return out


def sa(tag):
    a, b = r.tag(tag)
    rows = [x for x in r.SA if a <= x[0] < b]
    print("\n== %s smart ammo: %d frames" % (tag, len(rows)))
    if not rows:
        return
    t0 = rows[0][0]
    last = None
    for t, slot, w, ts in rows:
        key = tuple((h, round(fr, 2)) for h, fr, ac in ts)
        if key != last:
            print("  +%.3f slot %d %s %s" % (t - t0, slot, w, " ".join("%s:%.3f%s" % (h, fr, "*" if ac else "") for h, fr, ac in ts)))
            last = key


def dmg(tag):
    a, b = r.tag(tag)
    a += r.offset
    b += r.offset
    for d in r.TD:
        if a <= d[0] < b:
            print("  TD +%.3f %s %.1f src %d inf %s h %d type %d" % (d[0] - a, d[1], d[2], d[3], d[4], d[5], d[6]))


for name in ("sv_0", "sv_1", "sv_2", "sv_3"):
    if r.tag(name):
        paths(name, show=(name in ("sv_0", "sv_3")))
if r.tag("sv_dmg"):
    paths("sv_dmg", show=False)
    dmg("sv_dmg")
for pre in ("mt", "mr"):
    for suf in ("none", "one0.8", "one3", "two"):
        tg = "%s_%s" % (pre, suf)
        if r.tag(tg):
            sa(tg)
            paths(tg, show=(suf == "none"), step=0.05)
            dmg(tg)
print("\nKMERR:", [o for o in r.other if o[0] == "KMERR"][:5])
