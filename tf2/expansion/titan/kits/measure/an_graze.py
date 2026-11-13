"""Graze test: missiles aimed past a static foe. For each tag: the missile's closest horizontal approach to the foe
axis (foe origin, bounding box +-60 u, 0..235 u high) from the client per-frame track, the height there, and whether
a direct hit (inflictor rpg_missile) landed within 0.6 s. Usage: py -3 -I an_graze.py <run dir> <tag prefix>"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run  # noqa: E402
from an_expand import stitch  # noqa: E402

r = Run(sys.argv[1])
pre = sys.argv[2]
for a, b, tag in r.tags:
    if not tag.startswith(pre):
        continue
    tf = [x for x in r.TF if x[1] == 0 and a + r.offset <= x[0] < b + r.offset]
    if not tf:
        continue
    fx, fy, fz = tf[0][2], tf[0][3], tf[0][4]
    trs = stitch(r, r.client_proj_in(a, b))
    hit = [d for d in r.TD if a + r.offset <= d[0] < a + r.offset + 0.8 and d[4] == "rpg_missile"]
    for t in trs:
        best = min(t, key=lambda p: math.hypot(p[1] - fx, p[2] - fy))
        dmin = math.hypot(best[1] - fx, best[2] - fy)
        # signed lateral offset (lane faces +x: +y = left)
        print("%-6s pass %5.1f u from the foe axis (y offset %+6.1f) at height %5.1f above its feet; direct hit: %s" % (
            tag, dmin, best[2] - fy, best[3] - fz, ", ".join("%.0f" % d[2] for d in hit) or "no"))
