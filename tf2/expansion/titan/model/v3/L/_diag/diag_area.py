"""Diagnostic: polygon area vs triangle area, non-planar / concave / duplicate faces of given parts."""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
import numpy as np
objs, meshes, mats = B.build()
for n in sys.argv[sys.argv.index("--") + 3].split(","):
    me = meshes[n].data; me.calc_loop_triangles()
    pa = sum(p.area for p in me.polygons); ta = sum(t.area for t in me.loop_triangles)
    keys = {}
    dup = 0
    for p in me.polygons:
        k = tuple(sorted(round(c, 5) for v in p.vertices for c in me.vertices[v].co))
        if k in keys: dup += 1
        keys[k] = 1
    ngon = sum(1 for p in me.polygons if len(p.vertices) > 4)
    print("AREA", n, "poly %.4f tri %.4f" % (pa, ta), "polys", len(me.polygons), "ngons", ngon, "dup", dup)
