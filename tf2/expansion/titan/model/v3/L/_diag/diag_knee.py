"""Diagnostic: per pose and side, smallest distance from the thigh parts to the knee parts (0 = touching/overlapping).
blender -b -P _diag/diag_knee.py -- L1 4"""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
from mathutils import Vector
objs, meshes, mats = B.build()
TH = ("Thigh", "Thigh_Plate", "Thigh_Side", "Thigh_Clevis")
KN = ("Knee_Hub", "Shin", "Shin_Plate", "Knee_Guard")
poses = dict(B.R.poses(code=B.CODE)); poses["BIND"] = B.R.BIND
worst = 0
for name, h in poses.items():
    if name == "BIND":
        B.set_pose(objs, h)
    else:
        B.solve_pose(objs, meshes, h)
    out = []
    for s in "LR":
        th = [meshes[n + "_" + s] for n in TH if n + "_" + s in meshes]
        kn = [meshes[n + "_" + s] for n in KN if n + "_" + s in meshes]
        trees = [B.tree_of(o) for o in kn]
        d = min(min((t.find_nearest(Vector(p))[0] - Vector(p)).length for t in trees) for o in th for p in B.wverts(o)
                if any(True for _ in [0]))
        # touching if any thigh vertex is inside a knee part
        inside = any(B._inside(t, p) for o in th for p in B.wverts(o)[::3] for t in trees)
        out.append("%s %.3f%s" % (s, 0.0 if inside else d, "" if inside else " GAP" if d > 0.005 else ""))
        worst = max(worst, 0.0 if inside else d)
    print("%-20s %s" % (name, "  ".join(out)))
print("WORST", round(worst, 3))
