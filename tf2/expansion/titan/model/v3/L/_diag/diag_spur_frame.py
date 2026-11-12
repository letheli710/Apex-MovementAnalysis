"""Diagnostic: one terrain frame, left heel spur vertices against the ground under them (new spur geometry)."""
import os, sys, csv, math
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import build_light as B
A = sys.argv[sys.argv.index("--") + 1:]
tsv, tq = A[2], A[3]
TX = TZ = None
def load_terrain(path):
    pts = []
    for line in open(path):
        f = line.split()
        if not f or f[0].startswith("#") or f[0] in ("lane", "mark"): continue
        pts.append((float(f[0]), float(f[1])))
    xs, zs = [], []
    for i, (x, z) in enumerate(pts):
        if i + 1 < len(pts) and pts[i + 1][0] == x and pts[i + 1][1] > z: x -= 1e-4
        elif i > 0 and pts[i - 1][0] == x and pts[i - 1][1] > z: x += 1e-4
        xs.append(x); zs.append(z)
    return np.array(xs), np.array(zs)
TX, TZ = load_terrain(os.path.join(os.path.dirname(tsv), "terrain.tsv"))
r = [x for x in csv.DictReader(open(tsv), delimiter="\t") if x["t"] == tq][0]
objs, meshes, mats = B.build()
root = objs[B.ROOT]; root.rotation_mode = "XYZ"
f = lambda k: float(r[k])
root.location = (f("rootY") + f("offY"), -(f("rootX") + f("offX")), f("rootZ") + f("offZ"))
root.rotation_euler = (math.radians(f("rootPitch")), 0.0, math.radians(f("rootYaw")))
p = dict(pel_yaw=f("pelYaw"), pel_pitch=f("pelPitch"), pel_roll=f("pelRoll"), w_yaw=f("waistYaw"), w_bend=f("waistBend"), w_side=f("waistSide"),
         h_flex_L=f("lFlex"), h_out_L=f("lOut"), h_twist_L=f("lTwist"), k_L=f("lKnee"), a_L=f("lAnkle"), a_roll_L=f("lAnkleRoll"),
         h_flex_R=f("rFlex"), h_out_R=f("rOut"), h_twist_R=-f("rTwist"), k_R=f("rKnee"), a_R=f("rAnkle"), a_roll_R=f("rAnkleRoll"))
B.set_pose(objs, p, (f("pelX"), f("pelY"), f("pelZ")))
for n in ("Heel_Spur_L", "Foot_L", "Toe_L"):
    v = B.wverts(meshes[n]); x = -v[:, 1]; g = np.interp(x, TX, TZ, left=0.0, right=0.0)
    i = int(np.argmin(v[:, 2] - g))
    print(n, "x %.3f..%.3f z %.3f..%.3f  worst vertex x %.3f z %.3f ground %.3f" % (x.min(), x.max(), v[:, 2].min(), v[:, 2].max(), x[i], v[i, 2], g[i]))
near = [(a, b) for a, b in zip(TX, TZ) if abs(a - x.mean()) < 2.0]
print("terrain near", [(round(a, 3), round(b, 3)) for a, b in near])
