"""km_life: (1) lf_* tags: every server projectile in the window: life (first to last sample), peak height, speed
at the end, last position (did it vanish in the air or hit something); (2) cb_* tags: cluster-missile bomblets
(ownerless moving prop_physics, PF lines): each bomblet's path, the points where its velocity jumps (= where it
exploded and was sent to the next point), distance of those points from the rocket's impact point, and timing.
Usage: py -3 -I an_life.py <run dir>"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, norm, sub  # noqa: E402

r = Run(sys.argv[1])
for a, b, tag in r.tags:
    sa, sb = a + r.offset, b + r.offset
    if tag.startswith("lf_"):
        hs = [h for h, v in r.ps_new.items() if sa <= v[0] < sb]
        print("\n== %s: %d projectiles" % (tag, len(hs)))
        for h in hs:
            pts = r.ps[h]
            moving = [p for p in pts if norm(p[4:7]) > 1]
            if not moving:
                continue
            life = moving[-1][0] - pts[0][0]
            top = max(p[3] for p in pts)
            last = moving[-1]
            stopped = len(pts) > len(moving)
            print("  %s %s: moving %.2f s (samples to %.2f s), z %.0f -> peak %.0f -> last %.0f, end speed %.0f, %s" % (
                h, r.ps_new[h][1], life, pts[-1][0] - pts[0][0], pts[0][3], top, last[3], norm(last[4:7]),
                "stopped (hit something)" if stopped else "vanished while flying"))
    if tag.startswith("cb_"):
        rockets = [h for h, v in r.ps_new.items() if sa <= v[0] < sb and v[1] == "rpg_missile"]
        imp = r.ps[rockets[0]][-1][1:4] if rockets else None
        t_imp = r.ps[rockets[0]][-1][0] if rockets else sa
        props = {h: p for h, p in r.pf.items() if sa <= p[0][0] < sb}
        print("\n== %s: impact %s, %d bomblets" % (tag, "%.0f %.0f %.0f" % imp if imp else "-", len(props)))
        pops = []
        for h, pts in sorted(props.items(), key=lambda kv: kv[1][0][0]):
            jumps = []
            # the script sets a new launch velocity for every hop (the logged velocity is that launch value), and the
            # hop starts from the point where the previous explosion went off: a changed velocity = a new hop
            for p, q in zip(pts, pts[1:]):
                if norm(sub(q[4:7], p[4:7])) > 1:
                    jumps.append(p)  # last sample of the old hop, within 0.1 s of the explosion
            jumps.append(pts[-1])
            print("  bomblet %s: %d samples %.2f..%.2f s after impact, %d velocity jumps" % (h, len(pts), pts[0][0] - t_imp, pts[-1][0] - t_imp, len(jumps)))
            for q in jumps:
                d = math.hypot(q[1] - imp[0], q[2] - imp[1]) if imp else -1
                pops.append((q[0] - t_imp, d, q[3] - imp[2] if imp else 0))
                print("     pop ~+%.2f s near %.0f u from impact (dz %+.0f)" % pops[-1])
        if pops:
            ds = sorted(p[1] for p in pops)
            print("  pops %d; distance from impact min %.0f median %.0f max %.0f; times %.2f .. %.2f s" % (
                len(pops), ds[0], ds[len(ds) // 2], ds[-1], min(p[0] for p in pops), max(p[0] for p in pops)))
