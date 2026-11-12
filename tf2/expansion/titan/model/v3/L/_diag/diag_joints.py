"""Diagnostic: contact between the parts on either side of every limb joint, all poses. 0 = touching."""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
from mathutils import Vector
objs, meshes, mats = B.build()
by_joint = {}
for n, o in meshes.items():
    by_joint.setdefault(o["owner_joint"], []).append(n)
pairs = []
for s in "LR":
    for a, b in (("J_Pelvis", "J_Hip_"), ("J_Hip_", "J_Knee_"), ("J_Knee_", "J_Ankle_"), ("J_Torso", "J_Shoulder_"), ("J_Shoulder_", "J_Elbow_"), ("J_Elbow_", "J_Wrist_")):
        pairs.append((a if a == "J_Pelvis" or a == "J_Torso" else a + s, b + s))
pairs.append(("J_Pelvis", "J_Waist")); pairs.append(("J_Waist", "J_Torso"))
def gap(a, b):
    A = [meshes[n] for n in by_joint.get(a, [])]; Bm = [meshes[n] for n in by_joint.get(b, [])]
    if not A or not Bm: return None
    trees = [B.tree_of(o) for o in Bm]
    pts = [p for o in A for p in B.wverts(o)]
    if any(B._inside(t, p) for p in pts[::2] for t in trees): return 0.0
    tA = [B.tree_of(o) for o in A]; ptsB = [p for o in Bm for p in B.wverts(o)]
    if any(B._inside(t, p) for p in ptsB[::2] for t in tA): return 0.0
    return min((t.find_nearest(Vector(p))[0] - Vector(p)).length for t in trees for p in pts)
poses = dict(B.R.poses(code=B.CODE))
worst = {}
for name, h in list(poses.items()) + [("BIND", None)]:
    if h is None: B.set_pose(objs, B.R.BIND)
    else: B.solve_pose(objs, meshes, h)
    for a, b in pairs:
        g = gap(a, b)
        if g is None: continue
        k = a + "-" + b
        if g > worst.get(k, (-1, ""))[0]: worst[k] = (g, name)
for k, (g, n) in worst.items():
    print("%-28s worst %.3f (%s)%s" % (k, g, n, "  GAP" if g > 0.005 else ""))
