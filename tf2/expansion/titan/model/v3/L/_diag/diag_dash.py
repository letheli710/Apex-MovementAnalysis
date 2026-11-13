"""Diagnostic: dash_float_L left arm vs thigh for a few left-arm options. blender -b -P _diag/diag_dash.py -- L1 1"""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
objs, meshes, mats = B.build()
P = B.R.poses()["dash_float_L"]
print({k: v for k, v in P.items() if k.endswith("_L") or k.startswith(("w_", "pel"))})
for extra in ({"s_out_L": 22}, {"s_out_L": 24}, {"s_out_L": 26}, {"s_out_L": 28}):
    B.solve_pose(objs, meshes, dict(P, **extra))
    h = [x for x in B.collide(meshes)]
    print(extra, "clean" if not h else h)
