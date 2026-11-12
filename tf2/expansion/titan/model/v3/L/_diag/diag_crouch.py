"""Diagnostic: crouch at wrist 0, weapon hits and lowest point."""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
objs, meshes, mats = B.build()
w = B.weapon_names(meshes)
for nm in ("crouch", "crouch_yaw_85"):
    B.solve_pose(objs, meshes, dict(B.R.poses(code=B.CODE)[nm], wr_pitch_R=0.0))
    print(nm, "low %.3f" % min(B.wverts(meshes[n])[:, 2].min() for n in w), B.collide(meshes, only=set(w)))
