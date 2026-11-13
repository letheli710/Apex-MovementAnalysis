"""Diagnostic: triangles Unity's FBX import drops (zero area), per titan."""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
objs, meshes, mats = B.build()
import numpy as np
tot = 0
cnt = {e: 0 for e in (1e-7, 1e-6, 1e-5, 1e-4)}
for n, o in meshes.items():
    me = o.data; me.calc_loop_triangles()
    V = np.array([v.co[:] for v in me.vertices])
    for t in me.loop_triangles:
        tot += 1
        a, b, c = (V[i] for i in t.vertices)
        d = min(np.linalg.norm(a - b), np.linalg.norm(b - c), np.linalg.norm(a - c))
        for e in cnt:
            if d < e: cnt[e] += 1
print("TRIS", tot, {e: (k, tot - k) for e, k in cnt.items()})
