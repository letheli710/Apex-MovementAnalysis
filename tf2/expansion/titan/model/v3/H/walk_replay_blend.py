"""Walk retarget H3 check on a saved heavy model (WALK-RETARGET-PLAN.md section 5), independent of the build scripts:
opens a .blend made by build_heavy.py (e.g. H1/r5c_final/Titan_H1_r5c.blend = the model Unity's titan_h1_v3.fbx came from), re-poses its
joint empties from Unity's TitanWalkFilm joints.tsv every N frames, and checks the feet against the floor and the parts against each other.

  blender.exe -b <model.blend> -P walk_replay_blend.py -- <joints.tsv> <out dir> [every=5] [code=H1]

Pose rules = build_heavy.local_rotations / set_pose (v2 hand-pose meaning; Unity's TitanSkeleton follows design.py the same way); the only
mapping is the hip twist: Unity's is + outward on both legs, here h_twist_R = -twist. Analysis axes x forward, y left, z up; Blender X = y, Y = -x.
Checks: lowest point of each foot (+ toes) and shin over the ground (Unity's root z): planted -0.02 .. +0.01, swinging >= 0.05; BVH overlap
of every part pair except same-joint pairs and the r5c touching list.

Terrain (C1, 2026-11-13): HSD_REPLAY_TERRAIN=<terrain.tsv> (TitanWalkFilm -route terrain writes it next to joints.tsv) measures every
vertex against the course's ground under it (the profile z(x), the higher side at a vertical step) instead of Unity's root height, so
"under the floor" also means into a ramp, a tread or through a riser; planted_high then says how far a planted foot floats."""
import csv
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index("--") + 1:]
TSV, OUT = args[0], args[1]
EVERY = int(args[2]) if len(args) > 2 else 5
CODE = args[3] if len(args) > 3 else "H1"
C = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)

TERRAIN = os.environ.get("HSD_REPLAY_TERRAIN")
TX = TZ = None
if TERRAIN:
    pts = []
    for line in open(TERRAIN, encoding="utf-8"):
        f = line.split()
        if not f or f[0].startswith("#") or f[0] in ("lane", "mark"):
            continue
        pts.append((float(f[0]), float(f[1])))
    # a vertical step: its lower point moves 0.1 mm off to the low side, so np.interp gives the higher side at the step
    xs, zs = [], []
    for i, (x, z) in enumerate(pts):
        if i + 1 < len(pts) and pts[i + 1][0] == x and pts[i + 1][1] > z:
            x -= 1e-4
        elif i > 0 and pts[i - 1][0] == x and pts[i - 1][1] > z:
            x += 1e-4
        xs.append(x); zs.append(z)
    TX, TZ = np.array(xs), np.array(zs)


def ground_under(v):
    """Ground height under each world vertex (analysis x = -Blender Y); 0 off the course."""
    return np.interp(-v[:, 1], TX, TZ, left=0.0, right=0.0)

# heavy_parts.py r5c EXCLUDED_COMMON (+ H2's), touching on purpose
EXCL = {frozenset(p) for p in [
    ("Pelvis", "Waist"), ("Waist", "Torso_Lower"), ("Waist", "Torso_Upper"), ("Hatch", "Torso_Upper"), ("Hatch", "Torso_Lower"), ("Optic", "Torso_Upper"),
    ("UpperArm_L", "Forearm_L"), ("Forearm_L", "Hand_L"), ("UpperArm_R", "Cannon"),
    ("Hand_L", "Finger_L_1"), ("Hand_L", "Finger_L_2"), ("Hand_L", "Finger_L_3"),
    ("Thigh_L", "Shin_L"), ("Thigh_R", "Shin_R"), ("Shin_L", "Foot_L"), ("Shin_R", "Foot_R"), ("Shin_L", "Toe_L"), ("Shin_R", "Toe_R"),
    ("Cannon", "Barrels"), ("Drum", "Torso_Upper"), ("Belt_Torso", "Belt_Arm"), ("Belt_Arm", "Belt_Cannon"), ("Belt_Arm", "Cannon"),
    ("Belt_Cannon", "UpperArm_R"), ("Drum", "Belt_Torso"),
    # r6 joint pieces (heavy_parts.EXCLUDED_JOINT): each only against the part it sits in
    ("Hip_Axle_L", "Thigh_L"), ("Hip_Axle_R", "Thigh_R"), ("Shoulder_Socket_L", "UpperArm_L"), ("Shoulder_Socket_R", "UpperArm_R"),
    ("Wrist_Drum_L", "Hand_L"), ("Wrist_Drum_L", "Finger_L_1"), ("Wrist_Drum_L", "Finger_L_2"), ("Wrist_Drum_L", "Finger_L_3")]}


def Rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def to_b(v):
    return (float(v[1]), float(-v[0]), float(v[2]))


def local_rotations(p):
    g = lambda k: p.get(k, 0.0)
    out = {
        "J_Pelvis": Rz(g("pel_yaw")) @ Ry(g("pel_pitch")) @ Rx(g("pel_roll")),
        "J_Torso": Rz(g("w_yaw")) @ Ry(g("w_bend")) @ Rx(g("w_side")),
        "J_Hatch": Ry(g("hatch")),
        "J_Optic": Rz(g("op_yaw")) @ Ry(-g("op_pitch")),
        "J_Elbow_L": Ry(-g("e_L")),
        "J_Elbow_R": Ry(-g("e_R")),
        "J_Wrist_L": Ry(g("wr_pitch")) @ Rx(g("wr_side")),
    }
    for side, sg in (("L", 1), ("R", -1)):
        out["J_Hip_" + side] = Rz(g("h_twist_" + side)) @ Ry(-g("h_flex_" + side)) @ Rx(sg * g("h_out_" + side))
        out["J_Knee_" + side] = Ry(g("k_" + side))
        out["J_Ankle_" + side] = Ry(g("a_" + side)) @ Rx(g("a_roll_" + side))
        out["J_Shoulder_" + side] = Rz(g("s_in_" + side) * -sg) @ Ry(-g("s_flex_" + side)) @ Rx(sg * g("s_out_" + side))
    return out


root = bpy.data.objects["Titan_" + CODE]
joints = {o.name: o for o in bpy.data.objects if o.type == "EMPTY" and (o.name.startswith("J_") or o.name == "W_Cannon")}
meshes = {o.name[len(CODE) + 1:]: o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(CODE + "_")}
for o in joints.values():
    o.rotation_mode = "QUATERNION"
bpy.context.view_layer.update()
pelvis_rest = joints["J_Pelvis"].location.copy()


def world_verts(ob):
    m = np.array(ob.matrix_world)
    v = np.array([x.co[:] for x in ob.data.vertices])
    return v @ m[:3, :3].T + m[:3, 3]


def set_pose(p, pel_off):
    rots = local_rotations(p)
    for name, o in joints.items():
        R = rots.get(name)
        M = C @ R @ C.T if R is not None else np.eye(3)
        o.rotation_quaternion = Matrix(M.tolist()).to_quaternion()
    joints["J_Pelvis"].location = pelvis_rest + Vector(to_b(pel_off))


DBG = os.environ.get("HSD_REPLAY_DBG")      # "Foot_R,Thigh_R": print where that pair overlaps, in each part's own (joint) frame, analysis axes
dbg_pts = {}


def collide():
    T = {n: BVHTree.FromPolygons([Vector(x) for x in world_verts(o)], [list(q.vertices) for q in o.data.polygons]) for n, o in meshes.items()}
    names, hits = list(meshes), []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if meshes[a].parent == meshes[b].parent or frozenset((a, b)) in EXCL:
                continue
            pairs = T[a].overlap(T[b])
            if pairs:
                hits.append(a + " x " + b)
                if DBG and {a, b} == set(DBG.split(",")):
                    for name, idx in ((a, 0), (b, 1)):
                        ob = meshes[name]
                        for pr in pairs:
                            c = ob.data.polygons[pr[idx]].center
                            dbg_pts.setdefault(name, []).append((-c.y, c.x, c.z))
    return hits


os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
out = ["t\tmodeL\tmodeR\tlowL\tlowR\tshinL\tshinR\tcollisions"]
worst = dict(model=bpy.data.filepath, planted_low=0.0, planted_high=0.0, swing_min=9.0, frames=0, frames_with_collision=0, pairs={},
             planted_frames_under_2cm=0, swing_frames_under_5cm=0)
for i, r in enumerate(rows):
    if i % EVERY:
        continue
    f = lambda k: float(r[k])
    p = {"pel_yaw": f("pelYaw"), "pel_pitch": f("pelPitch"), "pel_roll": f("pelRoll"), "w_yaw": f("waistYaw"), "w_bend": f("waistBend"), "w_side": f("waistSide"),
         "h_flex_L": f("lFlex"), "h_out_L": f("lOut"), "h_twist_L": f("lTwist"), "k_L": f("lKnee"), "a_L": f("lAnkle"), "a_roll_L": f("lAnkleRoll"),
         "h_flex_R": f("rFlex"), "h_out_R": f("rOut"), "h_twist_R": -f("rTwist"), "k_R": f("rKnee"), "a_R": f("rAnkle"), "a_roll_R": f("rAnkleRoll"),
         "s_flex_L": f("aLFlex"), "s_out_L": f("aLOut"), "s_in_L": f("aLIn"), "e_L": f("aLElbow"), "wr_pitch": f("aLWristPitch"), "wr_side": f("aLWristYaw"),
         "s_flex_R": f("aRFlex"), "s_out_R": f("aROut"), "s_in_R": f("aRIn"), "e_R": f("aRElbow"), "hatch": f("hatch"), "op_yaw": f("opticYaw"), "op_pitch": f("opticPitch")}
    set_pose(p, (f("pelX"), f("pelY"), f("pelZ")))
    gz = f("rootZ")
    root.location = to_b((f("rootX") + f("offX"), f("rootY") + f("offY"), gz + f("offZ")))
    root.rotation_euler = (math.radians(f("rootPitch")), 0, math.radians(f("rootYaw")))      # Unity: yaw, then pitch about the titan's side axis (Blender X)
    bpy.context.view_layer.update()
    if TERRAIN:
        def rel(o):
            v = world_verts(o)
            return float((v[:, 2] - ground_under(v)).min())
        low = lambda names: min(rel(meshes[n]) for n in names if n in meshes)
    else:
        low = lambda names: min(float(world_verts(meshes[n])[:, 2].min()) for n in names if n in meshes) - gz
    lowL, lowR = low(("Foot_L", "Toe_L")), low(("Foot_R", "Toe_R"))
    shL, shR = low(("Shin_L",)), low(("Shin_R",))
    hits = collide()
    body_low, body_part = min(((rel(o) if TERRAIN else float(world_verts(o)[:, 2].min()) - gz), n) for n, o in meshes.items())
    if body_low < worst.get("body_low", 9.0):
        worst["body_low"], worst["body_low_part"], worst["body_low_t"] = body_low, body_part, r["t"]
    mL, mR = r["modeL"], r["modeR"]
    for m, lo in ((mL, lowL), (mR, lowR)):
        if m == "Planted":
            worst["planted_low"] = min(worst["planted_low"], lo)
            worst["planted_high"] = max(worst["planted_high"], lo)
            worst["planted_frames_under_2cm"] += lo < -0.02
            worst["planted_frames_over_3cm"] = worst.get("planted_frames_over_3cm", 0) + (lo > 0.03)
        elif m == "Swing":
            worst["swing_min"] = min(worst["swing_min"], lo)
            worst["swing_frames_under_5cm"] += lo < 0.05
    worst["frames"] += 1
    if hits:
        worst["frames_with_collision"] += 1
        for h in hits:
            worst["pairs"][h] = worst["pairs"].get(h, 0) + 1
    out.append("%s\t%s\t%s\t%.4f\t%.4f\t%.4f\t%.4f\t%s" % (r["t"], mL, mR, lowL, lowR, shL, shR, ";".join(hits)))
open(os.path.join(OUT, "replay.tsv"), "w", encoding="utf-8").write("\n".join(out) + "\n")
json.dump(worst, open(os.path.join(OUT, "replay_summary.json"), "w", encoding="utf-8"), indent=1, default=float)
print("=== REPLAY", json.dumps(worst, default=float))
for name, pts in dbg_pts.items():
    p = np.array(pts)
    print("=== DBG", name, "local min", np.round(p.min(0), 3), "max", np.round(p.max(0), 3), "n", len(p))
