"""Rig data for the v2 medium base titan: read from ../v2-design/out/spec.json, plus the names DESIGN.md section 3 asks for
that the spec has no coordinates for (fingers and most sockets). Coordinates here are ANALYSIS axes: x forward, y left, z up."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(HERE, "..", "v2-design", "out", "spec.json"), encoding="utf-8"))
JA = SPEC["joints_analysis"]
JB = SPEC["joints_blender"]

# name: (parent, rest position). Tree = DESIGN.md section 3.
JOINTS = {
    "J_Pelvis": ("Titan_M_Base", JA["J_Pelvis"]),
    "J_Waist": ("J_Pelvis", JA["J_Waist"]),
    "J_Torso": ("J_Waist", JA["J_Waist"]),
    "J_Hatch": ("J_Torso", JA["J_Hatch"]),
    "J_Optic": ("J_Torso", JA["J_Optic"]),
    "J_Launcher_L": ("J_Torso", JA["J_Launcher_L"]),
    "J_Shoulder_L": ("J_Torso", JA["J_Shoulder_L"]),
    "J_Elbow_L": ("J_Shoulder_L", JA["J_Elbow_L"]),
    "J_Wrist_L": ("J_Elbow_L", JA["J_Wrist_L"]),
    "J_Shoulder_R": ("J_Torso", JA["J_Shoulder_R"]),
    "J_Elbow_R": ("J_Shoulder_R", JA["J_Elbow_R"]),
    "W_Cannon": ("J_Elbow_R", JA["W_Cannon"]),
    "J_Hip_L": ("J_Pelvis", JA["J_Hip_L"]),
    "J_Knee_L": ("J_Hip_L", JA["J_Knee_L"]),
    "J_Ankle_L": ("J_Knee_L", JA["J_Ankle_L"]),
    "J_Hip_R": ("J_Pelvis", JA["J_Hip_R"]),
    "J_Knee_R": ("J_Hip_R", JA["J_Knee_R"]),
    "J_Ankle_R": ("J_Knee_R", JA["J_Ankle_R"]),
}
_w = JA["J_Wrist_L"]
# not in the spec: finger roots on the palm (part box claw_L ends 0.57 below the wrist)
FINGER_ROOTS = {"J_Finger_L_1": (0.14, 0.12, -0.22), "J_Finger_L_2": (0.14, -0.12, -0.22), "J_Finger_L_3": (-0.14, 0.0, -0.22)}
for _n, _o in FINGER_ROOTS.items():
    JOINTS[_n] = ("J_Wrist_L", [_w[0] + _o[0], _w[1] + _o[1], _w[2] + _o[2]])

# launcher tube mouths, in launcher-local coordinates (used for S_Rocket_n and the tube meshes)
ROCKET_TUBES = [(0.44, y, z) for z in (0.22, 0.09) for y in (-0.16, 0.0, 0.16)]
_la = JA["J_Launcher_L"]

# name: (parent, rest position). S_Eye / S_Seat / S_Muzzle are from the spec, the others are placed on the surface they name.
SOCKETS = {
    "S_Eye": ("J_Torso", JA["S_Eye"]),
    "S_Seat": ("J_Torso", JA["S_Seat"]),
    "S_Muzzle": ("W_Cannon", JA["S_Muzzle"]),
    "S_Hand_L": ("J_Wrist_L", [_w[0], _w[1], _w[2] - 0.30]),
    "S_Chest": ("J_Torso", [1.05, 0.0, 4.75]),
    "S_Thrust": ("J_Torso", [-0.97, 0.0, 4.95]),
    "S_Vent_L": ("J_Torso", [-0.97, 0.42, 5.32]),
    "S_Vent_R": ("J_Torso", [-0.97, -0.42, 5.32]),
    "S_Dmg_Torso_F": ("J_Torso", [1.07, 0.70, 5.00]),
    "S_Dmg_Torso_B": ("J_Torso", [-0.97, 0.0, 4.60]),
    "S_Dmg_Shoulder_L": ("J_Shoulder_L", [0.0, 1.72, 4.60]),
    "S_Dmg_Shoulder_R": ("J_Shoulder_R", [0.0, -1.72, 4.60]),
    "S_Dmg_Elbow_L": ("J_Elbow_L", JA["J_Elbow_L"]),
    "S_Dmg_Elbow_R": ("J_Elbow_R", JA["J_Elbow_R"]),
    "S_Dmg_Thigh_L": ("J_Hip_L", [0.30, 0.86, 2.10]),
    "S_Dmg_Thigh_R": ("J_Hip_R", [0.30, -0.86, 2.10]),
    "S_Dmg_Knee_L": ("J_Knee_L", [0.20, 0.86, 1.45]),
    "S_Dmg_Knee_R": ("J_Knee_R", [0.20, -0.86, 1.45]),
    "S_Foot_L": ("J_Ankle_L", [0.28, 0.86, 0.0]),
    "S_Foot_R": ("J_Ankle_R", [0.28, -0.86, 0.0]),
}
for _i, _t in enumerate(ROCKET_TUBES):
    SOCKETS["S_Rocket_%d" % (_i + 1)] = ("J_Launcher_L", [_la[0] + _t[0], _la[1] + _t[1], _la[2] + _t[2]])

ALL = dict(JOINTS)
ALL.update(SOCKETS)

# spec.expected_poses key -> object name
POSE_KEYS = {"pelvis": "J_Pelvis", "waist": "J_Waist", "torso": "J_Torso", "hip_L": "J_Hip_L", "knee_L": "J_Knee_L", "ankle_L": "J_Ankle_L",
             "sh_L": "J_Shoulder_L", "el_L": "J_Elbow_L", "hip_R": "J_Hip_R", "knee_R": "J_Knee_R", "ankle_R": "J_Ankle_R", "sh_R": "J_Shoulder_R", "el_R": "J_Elbow_R"}

# Limit sweeps: (label, param, low, high). Sides are expanded by the build. DESIGN.md section 3 table.
# wrist "±45 / ±60" is read as pitch ±45, side ±60. Finger range is not in DESIGN: chosen here, see manifest notes.
LIMITS = [
    ("pelvis.yaw", "pel_yaw", -30, 30), ("pelvis.pitch", "pel_pitch", -25, 35), ("pelvis.roll", "pel_roll", -35, 35),
    ("waist.yaw", "w_yaw", -90, 90), ("waist.bend", "w_bend", -25, 45), ("waist.side", "w_side", -30, 30),
    ("hatch", "hatch", 0, 120), ("optic.yaw", "op_yaw", -40, 40), ("optic.pitch", "op_pitch", -25, 25),
]
LIMITS_SIDED = [
    ("hip.flex", "h_flex", -65, 110), ("hip.out", "h_out", -20, 60), ("hip.twist", "h_twist", -35, 60),
    ("knee", "k", 0, 140), ("ankle.pitch", "a", -35, 60), ("ankle.roll", "a_roll", -20, 20),
    ("shoulder.flex", "s_flex", -60, 120), ("shoulder.out", "s_out", -30, 90), ("shoulder.twist", "s_in", -45, 45),
]
LIMITS_LEFT = [("elbow_L", "e_L", 0, 140), ("wrist.pitch", "wr_pitch", -45, 45), ("wrist.side", "wr_side", -60, 60),
               ("finger_1", "f1", -25, 50), ("finger_2", "f2", -25, 50), ("finger_3", "f3", -25, 50)]
LIMITS_RIGHT = [("elbow_R", "e_R", 0, 120)]

MATERIALS = {
    "sand": ("M_Sand", (0.56, 0.48, 0.32, 1)),
    "olive": ("M_Olive", (0.21, 0.26, 0.13, 1)),
    "dark": ("M_Dark", (0.075, 0.08, 0.085, 1)),
    "hub": ("M_Hub", (0.17, 0.17, 0.18, 1)),
    "yellow": ("M_Yellow", (0.80, 0.50, 0.07, 1)),
    "optic": ("M_Optic", (1.0, 0.42, 0.06, 1)),
    "white": ("M_Stencil", (0.85, 0.85, 0.80, 1)),
    "black": ("M_Cockpit", (0.012, 0.012, 0.014, 1)),
}
