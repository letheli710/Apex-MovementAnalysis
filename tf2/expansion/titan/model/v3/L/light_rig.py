"""Light chassis skeleton (shared by L-1 and L-2). No bpy.

Coordinates: ANALYSIS axes, world REST position (x forward, y left, z up, metres), like v2-design/out/spec.json.
Rest = legs straight, feet flat (as v2). The standing pose bends hip 23 / knee 46 so the hip sits at the measured 3.05.

Sources: SPEC.md 3.2 [meas] light column (TF2 skeleton, ../../v2-design/out/tf2_geometry.txt); joint tree, limit names,
pose parameter names and the 19 pose names from v2 (../../v2/titan_v2_data.py, ../../v2-design/out/spec.json).
"""
import json
import math
import os

import numpy as np

import geo

HERE = os.path.dirname(os.path.abspath(__file__))
V2_SPEC = json.load(open(os.path.join(HERE, "..", "..", "v2-design", "out", "spec.json"), encoding="utf-8"))

# ------------------------------------------------------------------ measured targets (SPEC 3.2, light column, standing)
MEAS = dict(stand_top=5.73, hip_z=3.05, leg_ratio=0.53, pelvis_z=3.45, thigh=1.69, shin=1.21, ankle_z=0.38, ankle_ball=0.34,
            hip_spacing=1.57, shoulder_spacing=2.10, upper_arm=1.08, forearm=1.08)
DESIGN = dict(shoulder_w=3.3, hip_w=1.9, torso_h=1.9, torso_d=1.5, foot_l=1.35, foot_w=0.7)

STAND_HIP, STAND_KNEE = 23.0, 46.0      # thigh + shin at 23 deg: 2.90 * cos23 + 0.38 = 3.05
REST_LIFT = MEAS["thigh"] + MEAS["shin"] + MEAS["ankle_z"] - MEAS["hip_z"]   # 0.23: rest stands this much taller than the standing pose

HIP_Y, HIP_Z = MEAS["hip_spacing"] / 2, MEAS["thigh"] + MEAS["shin"] + MEAS["ankle_z"]     # 0.785, 3.28
KNEE_Z, ANKLE_Z = MEAS["shin"] + MEAS["ankle_z"], MEAS["ankle_z"]                          # 1.59, 0.38
PELVIS_Z = MEAS["pelvis_z"] + REST_LIFT                                                    # 3.68
WAIST_Z = PELVIS_Z + 0.30                                                                  # 3.98
# shoulder joints: 2.40 apart, not the measured 2.10 (SPEC marks it reference-only, the clavicle moves). At 2.10 the hanging
# forearm (half width 0.17) overlaps the thigh (outer edge 0.99) at rest. 2.40 is the TF2 medium value.
SH_Y, SH_Z = 1.20, 4.62
ELB_Z, WR_Z = SH_Z - MEAS["upper_arm"], SH_Z - MEAS["upper_arm"] - MEAS["forearm"]         # 3.54, 2.46
WAIST = np.array((0.0, 0.0, WAIST_Z))

# wing hinge: folded = back-up 45 deg with a slight outward splay (SPEC v1 4.3), deployed = straight out, span 5.5
WING_ROOT = (-0.80, 0.95, 4.58)
WING_SPAN = 1.80
# The wing is modelled DEPLOYED in its own frame (span +y, chord +x = leading edge, normal +z = top) and folded for the rest
# pose by WING_FOLD_L. Folded: span back-up 45 deg with a slight outward splay, chord (leading edge) forward-up, so the folded
# wings stand like two fins beside each other (top faces inward). One hinge axis does the whole sweep.
_df = np.array((-0.686, 0.245, 0.686)); _df /= np.linalg.norm(_df)
_cf = np.array((0.707, 0.0, 0.707)); _cf -= _df * np.dot(_cf, _df); _cf /= np.linalg.norm(_cf)
WING_FOLD_L = np.column_stack([_cf, _df, np.cross(_cf, _df)])
WING_ANGLE = math.degrees(math.acos((np.trace(WING_FOLD_L) - 1) / 2))                       # 86.4: deploy sweep
WING_AXIS_L = np.array([WING_FOLD_L[2, 1] - WING_FOLD_L[1, 2], WING_FOLD_L[0, 2] - WING_FOLD_L[2, 0], WING_FOLD_L[1, 0] - WING_FOLD_L[0, 1]])
WING_AXIS_L /= np.linalg.norm(WING_AXIS_L)


def wing_axis(side):
    """Mirror of a rotation about a by t is a rotation about -(mirrored a) by t."""
    return WING_AXIS_L if side == "L" else -np.array((WING_AXIS_L[0], -WING_AXIS_L[1], WING_AXIS_L[2]))


def wing_fold(side):
    M = np.diag((1.0, -1.0, 1.0))
    return WING_FOLD_L if side == "L" else M @ WING_FOLD_L @ M


LEAN_PIVOT = WAIST.copy()   # set by each titan's build(): L-1 leans about the waist point, L-2 about a point 0.37 higher


def lean(p, deg):
    """Torso shell lean: rotate a rest point about LEAN_PIVOT so the top goes forward."""
    return tuple(LEAN_PIVOT + geo.Ry(deg) @ (np.array(p, float) - LEAN_PIVOT))


# ------------------------------------------------------------------ joints shared by the light chassis
def core_joints(root):
    J = {
        "J_Pelvis": (root, (0.0, 0.0, PELVIS_Z)),
        "J_Waist": ("J_Pelvis", (0.0, 0.0, WAIST_Z)),
        "J_Torso": ("J_Waist", (0.0, 0.0, WAIST_Z)),
    }
    for s, sg in (("L", 1), ("R", -1)):
        J["J_Shoulder_" + s] = ("J_Torso", (0.0, sg * SH_Y, SH_Z))
        J["J_Elbow_" + s] = ("J_Shoulder_" + s, (0.0, sg * SH_Y, ELB_Z))
        J["J_Wrist_" + s] = ("J_Elbow_" + s, (0.0, sg * SH_Y, WR_Z))
        # finger roots on the palm, v2 offsets (titan_v2_data.FINGER_ROOTS), mirrored for the right hand
        for i, (dx, dy, dz) in enumerate(((0.14, 0.12, -0.22), (0.14, -0.12, -0.22), (-0.14, 0.0, -0.22)), 1):
            J["J_Finger_%s_%d" % (s, i)] = ("J_Wrist_" + s, (dx, sg * SH_Y + sg * dy, WR_Z + dz))
        J["J_Hip_" + s] = ("J_Pelvis", (0.0, sg * HIP_Y, HIP_Z))
        J["J_Knee_" + s] = ("J_Hip_" + s, (0.0, sg * HIP_Y, KNEE_Z))
        J["J_Ankle_" + s] = ("J_Knee_" + s, (0.0, sg * HIP_Y, ANKLE_Z))
        J["J_Wing_" + s] = ("J_Torso", (WING_ROOT[0], sg * WING_ROOT[1], WING_ROOT[2]))
    return J


# ------------------------------------------------------------------ limits (v2 table + the new joints)
LIMITS = [("pelvis.yaw", "pel_yaw", -30, 30), ("pelvis.pitch", "pel_pitch", -25, 35), ("pelvis.roll", "pel_roll", -35, 35),
          ("waist.yaw", "w_yaw", -90, 90), ("waist.bend", "w_bend", -25, 45), ("waist.side", "w_side", -30, 30),
          ("hatch", "hatch", 0, 120), ("optic.yaw", "op_yaw", -40, 40), ("optic.pitch", "op_pitch", -25, 25)]
LIMITS_SIDED = [("hip.flex", "h_flex", -65, 110), ("hip.out", "h_out", -20, 60), ("hip.twist", "h_twist", -35, 60),
                ("knee", "k", 0, 140), ("ankle.pitch", "a", -35, 60), ("ankle.roll", "a_roll", -20, 20),
                ("shoulder.flex", "s_flex", -60, 120), ("shoulder.out", "s_out", -30, 90), ("shoulder.twist", "s_in", -45, 45),
                ("elbow", "e", 0, 140), ("wrist.pitch", "wr_pitch", -45, 45), ("wrist.side", "wr_side", -60, 60),
                ("finger_1", "f1", -25, 50), ("finger_2", "f2", -25, 50), ("finger_3", "f3", -25, 50),
                ("wing", "wing", 0, round(WING_ANGLE, 1))]


def local_rotations(p):
    """Same parameter meaning as v2/build_titan.py local_rotations, extended to both hands and the wings."""
    g = lambda k: p.get(k, 0.0)
    out = {
        "J_Pelvis": geo.Rz(g("pel_yaw")) @ geo.Ry(g("pel_pitch")) @ geo.Rx(g("pel_roll")),
        "J_Torso": geo.Rz(g("w_yaw")) @ geo.Ry(g("w_bend")) @ geo.Rx(g("w_side")),
        "J_Hatch": geo.Ry(g("hatch")),
        "J_Optic": geo.Rz(g("op_yaw")) @ geo.Ry(-g("op_pitch")),
    }
    for side, sg in (("L", 1), ("R", -1)):
        out["J_Hip_" + side] = geo.Rz(g("h_twist_" + side)) @ geo.Ry(-g("h_flex_" + side)) @ geo.Rx(sg * g("h_out_" + side))
        out["J_Knee_" + side] = geo.Ry(g("k_" + side))
        out["J_Ankle_" + side] = geo.Ry(g("a_" + side)) @ geo.Rx(g("a_roll_" + side))
        out["J_Shoulder_" + side] = geo.Rz(g("s_in_" + side) * -sg) @ geo.Ry(-g("s_flex_" + side)) @ geo.Rx(sg * g("s_out_" + side))
        out["J_Elbow_" + side] = geo.Ry(-g("e_" + side))
        out["J_Wrist_" + side] = geo.Ry(g("wr_pitch_" + side)) @ geo.Rx(sg * g("wr_side_" + side))
        out["J_Finger_%s_1" % side] = geo.Ry(g("f1_" + side))
        out["J_Finger_%s_2" % side] = geo.Ry(g("f2_" + side))
        out["J_Finger_%s_3" % side] = geo.Ry(-g("f3_" + side))
        out["J_Wing_" + side] = geo.Raxis(wing_axis(side), -g("wing_" + side))
    return out


# ------------------------------------------------------------------ poses
def _swap_stand(h):
    """v2 standing legs (hip 14 / knee 28) -> light standing legs (23 / 46)."""
    h = dict(h)
    for s in "LR":
        if h.get("h_flex_" + s) == 14 and h.get("k_" + s) == 28:
            h["h_flex_" + s], h["k_" + s] = STAND_HIP, STAND_KNEE
    return h


def _v2_to_light(h):
    """v2 pose -> light pose: v2 left elbow / wrist keys get the side suffix; right arm cannon keys mean the forearm."""
    h = _swap_stand(h)
    out = {}
    for k, v in h.items():
        if k in ("e_L", "e_R"):
            out[k] = v
        elif k == "wr_pitch":
            out["wr_pitch_L"] = v
        elif k == "wr_side":
            out["wr_side_L"] = v
        else:
            out[k] = v
    return out


def poses(grip_R=40.0):
    """The 19 v2 pose names (legs of the standing ones moved to the light stance) + walk A/B.
    grip_R: right fingers closed on the weapon grip in every pose."""
    P = {}
    for name, h in V2_SPEC["hand_poses"].items():
        P[name] = _v2_to_light(h)
    P["walk_A"] = dict(P["stand_aim"], h_flex_L=38, k_L=40, h_flex_R=4, k_R=30, pel_pitch=4)
    P["walk_B"] = dict(P["stand_aim"], h_flex_L=6, k_L=58, h_flex_R=34, k_R=36, pel_pitch=4)
    # light variants of v2 poses that fail on the narrower light chassis (the v2 originals stay in the set and are reported)
    for name, extra in LIGHT_VARIANTS.items():
        P[name + "~light"] = dict(P[name], **extra)
    for p in P.values():
        for i in (1, 2, 3):
            p.setdefault("f%d_R" % i, grip_R)
    return P


# reason: light shoulders are 1.20 out (v2 1.30) and the right hand holds a rifle 0.44 below the forearm
LIGHT_VARIANTS = {
    "crouch": dict(s_flex_R=78, s_out_R=14),          # rifle 18 deg up and out so it clears the right knee
    "crouch_yaw_85": dict(s_flex_R=78, s_out_R=14),
    "dash_float_L": dict(s_out_L=34, e_L=60),          # left arm out so the elbow clears the raised left thigh
}
STAND = "stand_aim"
REQUIRED = ["stand_aim", "walk_A", "walk_B", "sprint_stride", "kneel_hatch", "yaw_85_level", "yaw_-85_level", "aim_up_45", "aim_down_45"]
