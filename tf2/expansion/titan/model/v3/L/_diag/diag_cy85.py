"""Diagnostic: crouch_yaw_85 at wrist 0, which rifle parts hit and by how much (vertex depth below the thigh surface)."""
import os, sys
os.environ["LIGHT_NO_MAIN"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_light as B
import numpy as np
from mathutils import Vector
objs, meshes, mats = B.build()
for nm in ("crouch_yaw_85", "crouch", "sprint_stride", "melee_L"):
    h = dict(B.R.poses(code="L1")[nm], wr_pitch_R=0.0)
    B.solve_pose(objs, meshes, h)
    hits = B.collide(meshes, only=set(B.weapon_names(meshes)))
    print(nm, hits)
    for pair in hits:
        a, b = pair.split(" x ")
        w = a if a.startswith("Rifle") else b
        o = b if w == a else a
        t = B.tree_of(meshes[o])
        W = B.wverts(meshes[w])
        ins = [p for p in W if B._inside(t, p)]
        if ins:
            ins = np.array(ins)
            # rifle coords: s along forearm from wrist
            M = np.array(objs["W_Rifle"].matrix_world)
            loc = (ins - M[:3, 3]) @ M[:3, :3]
            print("   ", pair, len(ins), "verts inside; local Blender min/max", loc.min(0).round(2), loc.max(0).round(2))
