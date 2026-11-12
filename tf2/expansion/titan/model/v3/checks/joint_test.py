"""Joint contact test on a finished FBX, any line (R6 version, SPEC 0.4 #40-#41).

  blender.exe -b -P joint_test.py -- <code> [out_dir]        code = L1 | L2 | M1 | H1 | H2; reads v3/<line>/Titan_<code>.fbx

Rule: for every joint, the parts on its two sides must touch - surfaces intersect (BVH overlap) or the closest surface
distance is <= 5 mm. Joint pairs come from the file itself: every node that owns meshes is paired with its nearest ancestor
that owns meshes (so J_Shoulder_R - W_Cannon on M-1, J_Torso - J_Wing_L on L-1, J_Torso - S_Sword_Back on L-2 ...).
Poses: the file as it opens (L: the bind pose, others: rest) + the 19 v2 pose names with each line's own values
(lineup/lineup_pose.py: L from rig_L*.json, H with its kneel overrides), feet levelled and put on the ground.
Same judgement as M1/build_m1_r6.joint_gaps; the L line's r5b test used ray-parity for 'inside', which is wrong on parts
made of several overlapping shells (M-1: a 3 cm knee gap read as touching).
"""
import json
import os
import re
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(V3, "lineup"))
import lineup_pose as LP  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
CODE = args[0] if args else "H2"
OUT = args[1] if len(args) > 1 else os.path.join(HERE, "r6_joints")
TOUCH = 0.005
LINE = {"L1": "L", "L2": "L", "M1": "M1", "H1": "H", "H2": "H"}[CODE]


def base(n):
    return re.sub(r"\.\d{3}$", "", n)


def world_tri(o):
    m = o.matrix_world
    vs = [m @ v.co for v in o.data.vertices]
    return vs, BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons])


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    f = os.path.join(V3, LINE, "Titan_%s.fbx" % CODE)
    bpy.ops.import_scene.fbx(filepath=f, axis_forward="-Z", axis_up="Y")
    objs = list(bpy.data.objects)
    meshes = [o for o in objs if o.type == "MESH"]
    owners = {}
    for o in meshes:
        owners.setdefault(base(o.parent.name), []).append(o)
    pairs = []
    for n in owners:
        node = bpy.data.objects[[o for o in owners[n]][0].parent.name]
        p = node.parent
        while p is not None and base(p.name) not in owners:
            p = p.parent
        if p is not None:
            pairs.append((base(p.name), n))

    def gaps():
        cache = {o.name: world_tri(o) for o in meshes}
        out = {}
        for a, b in pairs:
            A, B = [cache[o.name] for o in owners[a]], [cache[o.name] for o in owners[b]]
            if any(ta.overlap(tb) for _, ta in A for _, tb in B):
                out[a + "-" + b] = 0.0
                continue
            d = min(min((tb.find_nearest(v)[0] - v).length for _, tb in B for va, _ in A for v in va),
                    min((ta.find_nearest(v)[0] - v).length for _, ta in A for vb, _ in B for v in vb))
            out[a + "-" + b] = 0.0 if d <= TOUCH else round(d, 3)
        return out

    G = {"as_opened": gaps()}
    for name in LP.pose_names(CODE):
        LP.apply(objs, CODE, name)
        G[name] = gaps()
    worst = {}
    for pose, g in G.items():
        for k, v in g.items():
            if v > worst.get(k, (0, ""))[0]:
                worst[k] = (v, pose)
    R = dict(titan=CODE, file=os.path.relpath(f, V3).replace("\\", "/"), touch_m=TOUCH, pairs=[a + "-" + b for a, b in pairs], poses=len(G),
             ok=not worst, gaps_m={k: v for k, v in sorted(worst.items(), key=lambda kv: -kv[1][0])},
             poses_with_gap={k: [p for p, g in G.items() if g.get(k, 0) > 0] for k in worst}, per_pose=G)
    os.makedirs(OUT, exist_ok=True)
    json.dump(R, open(os.path.join(OUT, "joints_%s.json" % CODE), "w", encoding="utf-8"), indent=1)
    print("=== JOINTS", CODE, "pairs", len(pairs), "ok", R["ok"], json.dumps(R["gaps_m"]))


main()
