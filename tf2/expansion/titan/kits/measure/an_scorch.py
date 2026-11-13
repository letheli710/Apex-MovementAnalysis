"""km_scorch: thermite fire spots (owned prop_physics, server 10 Hz) per tag: count, life, how far each rolled,
bounces (vz turning from - to +), final spread around the impact; damage ticks per target (same fire twice).
Usage: py -3 -I an_scorch.py <run dir>"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, norm  # noqa: E402

r = Run(sys.argv[1])
for a, b, tag in r.tags:
    if not tag.startswith("th_"):
        continue
    sa, sb = a + r.offset, b + r.offset
    props = {h: pts for h, pts in r.pf.items() if sa <= pts[0][0] < sb}
    print("\n== %s: %d fire spots" % (tag, len(props)))
    if not props:
        pass
    else:
        t_imp = min(p[0][0] for p in props.values())
        xs = [p[0][1] for p in props.values()]
        ys = [p[0][2] for p in props.values()]
        c = (sum(xs) / len(xs), sum(ys) / len(ys))
        ends = []
        for h, pts in sorted(props.items(), key=lambda kv: kv[1][0][0]):
            path = sum(norm((q[1] - p[1], q[2] - p[2], q[3] - p[3])) for p, q in zip(pts, pts[1:]))
            bounces = sum(1 for p, q in zip(pts, pts[1:]) if p[6] < -20 and q[6] > 20)
            settle = next((q[0] for q in pts if norm(q[4:7]) < 5), None)
            v0 = norm(pts[0][4:7])
            end = pts[-1]
            ends.append(end)
            print("  h=%s first +%.2f s, life %.2f s, v0 %.0f (vz %.0f), path %.0f u, moved %.0f u, bounces %d, still at +%s s, end %.0f %.0f %.0f" % (
                h, pts[0][0] - t_imp, end[0] - pts[0][0], v0, pts[0][6], path,
                norm((end[1] - pts[0][1], end[2] - pts[0][2], end[3] - pts[0][3])), bounces,
                "%.2f" % (settle - t_imp) if settle else "-", end[1], end[2], end[3]))
        d = [math.hypot(e[1] - c[0], e[2] - c[1]) for e in ends]
        print("  final distance from the impact centre: %s" % " ".join("%.0f" % x for x in sorted(d)))
    ticks = {}
    for t in r.TD:
        if sa <= t[0] < sb:
            ticks.setdefault(t[1], []).append(t)
    for v, ts in ticks.items():
        times = [round(t[0] - sa, 2) for t in ts]
        print("  TD %s: %d events, total %.0f, values %s" % (v, len(ts), sum(t[2] for t in ts), sorted(set(t[2] for t in ts))))
        print("     times %s" % " ".join("%.2f" % x for x in times[:40]))
