"""M-1 round 6 (R6): joint contact test (the L line's r5b test, L-D20) on top of R5, and the fixes it needs.

  blender.exe -b -P build_m1_r6.py -- r6 diag     only the test on the R5 geometry (no files written except r6_diag/)
  blender.exe -b -P build_m1_r6.py -- r6          build R6: test, checks, renders to r6_final/, Titan_M1.blend / .fbx

Test: for every joint, 0 when a part owned by the joint on one side touches or enters a part owned by the joint on the other
side, else the smallest distance (m). Rest + the 19 v2 poses. Same rule as v3/L/build_light.joint_gaps.
build_m1_r5.py is not changed; this file imports it and only adds R6_FIXES to its model.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_m1_r5 as F  # noqa: E402  (its main only runs with "r5" in argv)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

S = F.S
OUT = os.path.join(HERE, "r6_final")
DIAG = "diag" in sys.argv

# right arm: the cannon (W_Cannon) is the forearm, no mesh on J_Elbow_R
JOINT_PAIRS = [("J_Pelvis", "J_Waist"), ("J_Waist", "J_Torso"), ("J_Torso", "J_Hatch"), ("J_Torso", "J_Optic"), ("J_Torso", "J_Launcher_L"),
               ("J_Shoulder_L", "J_Elbow_L"), ("J_Elbow_L", "J_Wrist_L"), ("J_Shoulder_R", "W_Cannon"),
               ("J_Torso", "J_Shoulder_L"), ("J_Torso", "J_Shoulder_R")] + \
              [("J_Wrist_L", "J_Finger_L_%d" % i) for i in (1, 2, 3)] + \
              [(a + s if a != "J_Pelvis" else a, b + s) for s in "LR" for a, b in (("J_Pelvis", "J_Hip_"), ("J_Hip_", "J_Knee_"), ("J_Knee_", "J_Ankle_"))]


def tree(o):
    return BVHTree.FromPolygons([Vector(v) for v in S.world_verts(o)], [list(p.vertices) for p in o.data.polygons])


def joint_gaps(meshes, touch=0.005):
    """0 when a part on one side of the joint touches a part on the other side (surfaces intersect, or closer than 5 mm),
    else the smallest surface-to-surface distance (m). No inside-by-ray-parity test: the merged parts hold overlapping shells,
    where counting crossings gives wrong answers (the first R6 diag said the knee touched; it has a 3 cm gap)."""
    by = {}
    for n, o in meshes.items():
        by.setdefault(o["owner_joint"], []).append(o)
    out = {}
    for a, b in JOINT_PAIRS:
        A, B = by.get(a, []), by.get(b, [])
        if not A or not B:
            out[a + "-" + b] = "no part"
            continue
        tA, tB = [tree(o) for o in A], [tree(o) for o in B]
        if any(x.overlap(y) for x in tA for y in tB):
            out[a + "-" + b] = 0.0
            continue
        pA = [Vector(p) for o in A for p in S.world_verts(o)]
        pB = [Vector(p) for o in B for p in S.world_verts(o)]
        d = min(min((t.find_nearest(p)[0] - p).length for t in tB for p in pA), min((t.find_nearest(p)[0] - p).length for t in tA for p in pB))
        out[a + "-" + b] = 0.0 if d <= touch else round(d, 3)
    return out


def all_gaps(objs, meshes, solved):
    S.set_pose(objs, {})
    G = {"rest": joint_gaps(meshes)}
    for name, (p, off) in solved.items():
        S.set_pose(objs, p, off)
        G[name] = joint_gaps(meshes)
    S.set_pose(objs, {})
    worst = {}
    for pose, g in G.items():
        for k, v in g.items():
            if isinstance(v, float) and v > worst.get(k, (0, ""))[0]:
                worst[k] = (v, pose)
    return dict(ok=not worst, worst_gap_m={k: v for k, v in sorted(worst.items(), key=lambda kv: -kv[1][0])}, poses=len(G),
                joints=[a + "-" + b for a, b in JOINT_PAIRS], per_pose=G)


# ------------------------------------------------------------------ R6 fixes (from the diag run on R5, r6_diag/joint_gaps_r5_geometry.json)
# Same idea as the L line (L-D20): pieces centred on the joint axis, so they touch at any angle. Each new piece is its own part,
# excluded from the clash test only against the part it sits in on the other side of the joint; everything else is still checked.
def _part(P, name, joint, mesh, slot="frame"):
    P[name] = {"joint": joint, "pieces": [(mesh, slot, False, "detail")]}


def fix_shoulder_socket(P):
    """R5: torso-shoulder gap up to 0.097 (dash_float_L). Drum on J_Torso along the arm swing axis, y 0.88 (inside the torso
    cheek) to 1.12 (inside the arm hub, whose inner end is at 1.04, r 0.24)."""
    s = F.ring_y([(0.88, 0.20), (1.12, 0.20)], 0.0, 4.55, 24)
    _part(P, "Shoulder_Socket_L", "J_Torso", s)
    _part(P, "Shoulder_Socket_R", "J_Torso", F.mirror(s))


def fix_hip_axle(P):
    """R5: pelvis-hip gap 0.03 at rest (axle end y 0.58, thigh inner face 0.61). Axle extension y 0.55-0.68, r 0.15, on the hip axis."""
    a = F.ring_y([(0.55, 0.15), (0.68, 0.15)], 0.0, 2.85, 24)
    _part(P, "Hip_Axle_L", "J_Pelvis", a)
    _part(P, "Hip_Axle_R", "J_Pelvis", F.mirror(a))


def fix_ankle_fork(P):
    """R5: knee-ankle gap up to 0.054 (dash_float_L): the foot's ankle drum (r 0.16, y 0.58-1.14) only touches the shin
    bottom (z 0.86) when the ankle is level. Fork on the shin: two discs on the ankle axis inside the drum's length, straps up
    into the shin."""
    disc = lambda y0, y1: F.ring_y([(y0, 0.20), (y1, 0.20)], 0.0, 0.70, 24)
    fork = F.merge(disc(0.60, 0.645), disc(1.075, 1.12), F.box(-0.10, 0.10, 0.60, 0.645, 0.70, 0.95, 0.01), F.box(-0.10, 0.10, 1.075, 1.12, 0.70, 0.95, 0.01))
    _part(P, "Ankle_Fork_L", "J_Knee_L", fork)
    _part(P, "Ankle_Fork_R", "J_Knee_R", F.mirror(fork))


def fix_wrist_drum(P):
    """R5: elbow-wrist gap 0.02 at rest (forearm ends at z 2.92, palm starts at 2.90). Drum on the forearm along the wrist pitch
    axis (z 2.80), r 0.13: reaches into the palm at any wrist angle."""
    _part(P, "Wrist_Drum_L", "J_Elbow_L", F.ring_y([(1.13, 0.13), (1.47, 0.13)], 0.0, 2.80, 24))


def fix_knee_drum(P):
    """Found on the first R6 build (the diag sampled every 3rd vertex and missed it): hip-knee gap 0.03 at rest, the thigh ends
    at z 1.75 and the shin starts at 1.72, M-1 has no knee drum. Drum on the thigh along the knee axis (z 1.45), r 0.31 so it
    reaches into the thigh's bottom; inside the shin's width (y 0.66-1.06), hidden by the shin and the kneecap."""
    d = F.ring_y([(0.66, 0.31), (1.06, 0.31)], 0.0, 1.45, 28)
    _part(P, "Knee_Drum_L", "J_Hip_L", d)
    _part(P, "Knee_Drum_R", "J_Hip_R", F.mirror(d))


R6_FIXES = [fix_shoulder_socket, fix_hip_axle, fix_ankle_fork, fix_wrist_drum, fix_knee_drum]
for s_ in "LR":
    F.EXCLUDED.update({frozenset(("Shoulder_Socket_" + s_, "UpperArm_" + s_)), frozenset(("Hip_Axle_" + s_, "Thigh_" + s_)),
                       frozenset(("Ankle_Fork_" + s_, "Foot_" + s_)), frozenset(("Ankle_Fork_" + s_, "Toe_" + s_)),
                       frozenset(("Knee_Drum_" + s_, "Shin_" + s_))})
F.EXCLUDED.update({frozenset(("Wrist_Drum_L", "Hand_L"))} | {frozenset(("Wrist_Drum_L", "Finger_L_%d" % i)) for i in (1, 2, 3)})


def model_r6():
    P = F._model_r5()
    for fix in ([] if DIAG else R6_FIXES):      # diag = the R5 geometry as it was
        fix(P)
    return P


F._model_r5 = F.model
F.model = model_r6


def main():
    if DIAG:
        d = os.path.join(HERE, "r6_diag")
        os.makedirs(d, exist_ok=True)
        F.BOLT_LOG.clear()
        objs, meshes = F.build("final")
        feet = {"M1_Foot_L", "M1_Foot_R", "M1_Toe_L", "M1_Toe_R", "M1_Shin_L", "M1_Shin_R"}
        solved = {n: S.solve_pose(objs, h, feet) for n, h in S.D.SPEC["hand_poses"].items()}
        G = all_gaps(objs, meshes, solved)
        json.dump(G, open(os.path.join(d, "joint_gaps_r5_geometry.json"), "w", encoding="utf-8"), indent=1)
        print("=== R6 DIAG", json.dumps(G["worst_gap_m"]))
        return
    for ext in ("blend", "fbx"):          # keep R5 before Titan_M1.* is rewritten
        dst = os.path.join(HERE, "r5_final", "Titan_M1_r5." + ext)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(HERE, "Titan_M1." + ext), dst)
    F.FINAL = OUT
    F.BOLT_LOG.clear()
    objs, meshes = F.build("final")
    R, solved = F.run_checks(objs, meshes)
    R["joints_connected"] = all_gaps(objs, meshes, solved)
    os.makedirs(OUT, exist_ok=True)
    R["visible_colour_pct"] = F.visible_colour_share(objs, solved)
    F.render_grey(objs, solved, OUT, "")
    F.render_colour(objs, solved, OUT)
    R["fbx_roundtrip"] = F.export(objs)
    json.dump(R, open(os.path.join(OUT, "m1_r6_checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("=== R6 tris", R["tris_total"], "max", R["tris_max_part"], "poses", R["poses_clean"], "joints", R["joints_connected"]["ok"],
          json.dumps(R["joints_connected"]["worst_gap_m"]), "bolts off", R["bolts"]["off_surface"], "arm", R["arm_raise"]["clean_up_to_deg"],
          "vis", R["visible_colour_pct"], "hatch", R["kneel_hatch"]["ok"], "pilot", R["pilot_fit"]["ok"])


if "r6" in sys.argv:
    main()
