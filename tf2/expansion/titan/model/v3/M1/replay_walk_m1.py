"""M-1 walk replay on the real mesh: pose the finished model from Unity's TitanWalkFilm joints.tsv and check every part pair.

  blender.exe -b -P replay_walk_m1.py -- <joints.tsv> <out dir> [every=5]

Same mapping as the heavy line's build_heavy.replay (Unity's TitanBodyPose angles are the v2 hand-pose parameters, except the right
hip twist's sign). Collisions use M-1's 19-pose test (build_m1_r6: the R5 exclusions + the R6 joint pieces). Also the lowest point of
each foot (+ toe) against the ground under the root. Writes replay.tsv and replay_summary.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_m1_r7  # noqa: E402,F401  (R7: R6's joint pieces + the R7 hip axle; build_m1_r7 imports build_m1_r6 and patches build_m1_r5's model)
import build_m1_r5 as F  # noqa: E402

import bpy  # noqa: E402

S = F.S
args = sys.argv[sys.argv.index("--") + 1:]
tsv, out_dir = args[0], args[1]
every = int(args[2]) if len(args) > 2 else 5
os.makedirs(out_dir, exist_ok=True)
F.BOLT_LOG.clear()
objs, meshes = F.build("final")
rows = [l.rstrip("\n").split("\t") for l in open(tsv, encoding="utf-8")]
head, rows = rows[0], rows[1:]
col = {h: i for i, h in enumerate(head)}
f = lambda r, k: float(r[col[k]])
out = ["t\tmodeL\tmodeR\tlowL\tlowR\tcollisions"]
worst = dict(frames=0, frames_with_collision=0, pairs={})
DBG = [] if "dbg" in args else None
pel0 = S.J["J_Pelvis"]
for i, r in enumerate(rows):
    if i % every:
        continue
    p = {"pel_yaw": f(r, "pelYaw"), "pel_pitch": f(r, "pelPitch"), "pel_roll": f(r, "pelRoll"),
         "w_yaw": f(r, "waistYaw"), "w_bend": f(r, "waistBend"), "w_side": f(r, "waistSide"),
         "h_flex_L": f(r, "lFlex"), "h_out_L": f(r, "lOut"), "h_twist_L": f(r, "lTwist"), "k_L": f(r, "lKnee"), "a_L": f(r, "lAnkle"), "a_roll_L": f(r, "lAnkleRoll"),
         "h_flex_R": f(r, "rFlex"), "h_out_R": f(r, "rOut"), "h_twist_R": -f(r, "rTwist"), "k_R": f(r, "rKnee"), "a_R": f(r, "rAnkle"), "a_roll_R": f(r, "rAnkleRoll"),
         "s_flex_L": f(r, "aLFlex"), "s_out_L": f(r, "aLOut"), "s_in_L": f(r, "aLIn"), "e_L": f(r, "aLElbow"), "wr_pitch": f(r, "aLWristPitch"), "wr_side": f(r, "aLWristYaw"),
         "s_flex_R": f(r, "aRFlex"), "s_out_R": f(r, "aROut"), "s_in_R": f(r, "aRIn"), "e_R": f(r, "aRElbow"),
         "hatch": f(r, "hatch"), "op_yaw": f(r, "opticYaw"), "op_pitch": f(r, "opticPitch")}
    # joints.tsv pelX/Y/Z are the pelvis's offset from its rest place (TitanBodyPose.pelvis), as build_heavy.replay uses them
    S.set_pose(objs, p, (f(r, "pelX"), f(r, "pelY"), f(r, "pelZ")))
    bpy.context.view_layer.update()
    low = lambda names: min(float(S.world_verts(meshes[n])[:, 2].min()) for n in names)
    lowL, lowR = low(("Foot_L", "Toe_L")), low(("Foot_R", "Toe_R"))
    hits = S.collide(meshes)
    if hits and DBG is not None and len(DBG) < 6:
        from mathutils.bvhtree import BVHTree
        for h in hits[:1]:
            a, b = h.split(" x ")
            ta = BVHTree.FromPolygons([__import__("mathutils").Vector(v) for v in S.world_verts(meshes[a])], [list(q.vertices) for q in meshes[a].data.polygons])
            tb = BVHTree.FromPolygons([__import__("mathutils").Vector(v) for v in S.world_verts(meshes[b])], [list(q.vertices) for q in meshes[b].data.polygons])
            pr = ta.overlap(tb)
            inv = meshes[a].matrix_world.inverted()
            import numpy as np
            pts = np.array([list(inv @ meshes[a].matrix_world @ meshes[a].data.polygons[x[0]].center) for x in pr])
            jp = np.array(F.pos_of(meshes[a]["owner_joint"]))
            ana = np.array([[-q[1], q[0], q[2]] for q in pts]) + jp
            DBG.append((r[col["t"]], h, len(pr), ana.min(0).round(3).tolist(), ana.max(0).round(3).tolist(), {k: round(v, 1) for k, v in p.items() if k[0] in "hk" or k.startswith("pel")}))
    worst["frames"] += 1
    if hits:
        worst["frames_with_collision"] += 1
        for h in hits:
            worst["pairs"][h] = worst["pairs"].get(h, 0) + 1
    out.append("%s\t%s\t%s\t%.4f\t%.4f\t%s" % (r[col["t"]], r[col["modeL"]], r[col["modeR"]], lowL, lowR, ";".join(hits)))
open(os.path.join(out_dir, "replay.tsv"), "w", encoding="utf-8").write("\n".join(out) + "\n")
json.dump(worst, open(os.path.join(out_dir, "replay_summary.json"), "w", encoding="utf-8"), indent=1)
print("=== REPLAY", json.dumps(worst))
for d in DBG or []:
    print("=== DBG", d)
