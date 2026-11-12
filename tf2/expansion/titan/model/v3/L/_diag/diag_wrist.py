"""Diagnostic: sweep right wrist pitch per pose; lowest weapon point and collisions. blender -b -P _diag/diag_wrist.py -- L1 1"""
import os, sys, json
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
objs, meshes, mats = B.build()
wpn = [n for n in meshes if n.startswith(("Rifle", "Shotgun"))]
poses = B.R.poses()
names = sys.argv[sys.argv.index("--") + 3].split(",")
for name in names:
    print("==", name)
    for w in range(-90, 91, 15):
        p, off = B.solve_pose(objs, meshes, dict(poses[name], wr_pitch_R=w))
        low = min(B.wverts(meshes[n])[:, 2].min() for n in wpn)
        hits = B.collide(meshes)
        print("  w %4d low %6.2f %s" % (w, low, "; ".join(hits) if hits else "clean"))
