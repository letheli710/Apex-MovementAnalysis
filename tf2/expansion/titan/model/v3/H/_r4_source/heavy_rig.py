"""Heavy chassis rig (shared by H-1 and H-2) + per-armor nodes. No bpy. Analysis axes (x forward, y left, z up), world rest positions.

Decisions (README.md section 2, shared log topic 泰坦模型):
  H-SK1  leg chain = TF2 heavy bone ratios (thigh : shin : ankle = 1.73 : 0.67 : 0.44 [meas]) scaled x0.838 so that
         hip height / rest top = 40 % (SPEC 3.2, user decision 2: "keep short legs 40 %, top <= 5.97").
  H-SK2  arms keep the [meas] lengths 1.08 / 1.08; shoulder joints at y +-1.76 (not the [meas] 2.13 spacing, which is a
         clavicle-in-idle reference only) so the 1.44 m domes sit outside the barrel and the arms hang clear of the hips.
  H-SK3  hip spacing 2.11 [meas].
  H-SK4  "shared skeleton" = every joint that animation drives (pelvis, waist, torso, arms, fingers, legs, W_Cannon).
         Hatch, optic, launcher and S_* sockets are the armor's own layer (J_Hatch / J_Optic positions differ per titan).
  H-SK5  same cockpit as M-1: S_Seat (0.55, 0, 4.28), reclined pilot, S_Eye (0.72, 0, 4.70) unchanged.
"""
import math

# leg: TF2 heavy 1.73 / 0.67 / 0.44, scaled
LEG_K = 0.838
THIGH, SHIN, ANKLE = round(1.73 * LEG_K, 3), round(0.67 * LEG_K, 3), round(0.44 * LEG_K, 3)  # 1.450 / 0.561 / 0.369
Z_ANKLE = 0.37
Z_KNEE = round(Z_ANKLE + SHIN, 2)       # 0.93
Z_HIP = round(Z_KNEE + THIGH, 2)        # 2.38
HIP_Y = 1.055                           # 2.11 / 2
Z_PELVIS = 2.95
Z_WAIST = 3.38
SH_Y = 1.76
Z_SH = 4.78
UPPER, FORE = 1.08, 1.08
Z_ELBOW = round(Z_SH - UPPER, 2)        # 3.70
Z_WRIST = round(Z_ELBOW - FORE, 2)      # 2.62

SKELETON = {
    "J_Pelvis": ("ROOT", (0.0, 0.0, Z_PELVIS)),
    "J_Waist": ("J_Pelvis", (0.0, 0.0, Z_WAIST)),
    "J_Torso": ("J_Waist", (0.0, 0.0, Z_WAIST)),
    "J_Shoulder_L": ("J_Torso", (0.0, SH_Y, Z_SH)),
    "J_Elbow_L": ("J_Shoulder_L", (0.0, SH_Y, Z_ELBOW)),
    "J_Wrist_L": ("J_Elbow_L", (0.0, SH_Y, Z_WRIST)),
    "J_Finger_L_1": ("J_Wrist_L", (0.17, SH_Y + 0.15, Z_WRIST - 0.30)),
    "J_Finger_L_2": ("J_Wrist_L", (0.17, SH_Y - 0.15, Z_WRIST - 0.30)),
    "J_Finger_L_3": ("J_Wrist_L", (-0.17, SH_Y, Z_WRIST - 0.30)),
    "J_Shoulder_R": ("J_Torso", (0.0, -SH_Y, Z_SH)),
    "J_Elbow_R": ("J_Shoulder_R", (0.0, -SH_Y, Z_ELBOW)),
    "W_Cannon": ("J_Elbow_R", (0.0, -SH_Y, Z_ELBOW)),
    "J_Hip_L": ("J_Pelvis", (0.0, HIP_Y, Z_HIP)),
    "J_Knee_L": ("J_Hip_L", (0.0, HIP_Y, Z_KNEE)),
    "J_Ankle_L": ("J_Knee_L", (0.0, HIP_Y, Z_ANKLE)),
    "J_Hip_R": ("J_Pelvis", (0.0, -HIP_Y, Z_HIP)),
    "J_Knee_R": ("J_Hip_R", (0.0, -HIP_Y, Z_KNEE)),
    "J_Ankle_R": ("J_Knee_R", (0.0, -HIP_Y, Z_ANKLE)),
}

# v2 for the comparison table (spec.json joints_analysis)
V2 = {"J_Pelvis": 3.00, "J_Waist": 3.45, "J_Hip": 2.85, "J_Knee": 1.45, "J_Ankle": 0.70, "J_Shoulder": 4.55, "J_Elbow": 3.65,
      "J_Wrist": 2.80, "hip_y": 0.86, "sh_y": 1.30}

# directional sockets: local +x (analysis) points along the effect direction; others keep identity (v2 convention)
def _d(*v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def common_sockets(ch):
    """Sockets every heavy has. ch = per-armor dict with the few positions that differ."""
    w = SKELETON["J_Wrist_L"][1]
    S = {
        "S_Eye": ("J_Torso", (0.72, 0.0, 4.70), None),
        "S_Seat": ("J_Torso", (0.55, 0.0, 4.28), None),
        "S_Hand_L": ("J_Wrist_L", (w[0], w[1], w[2] - 0.34), _d(0, 0, -1)),
        "S_Chest": ("J_Torso", ch["chest"], _d(1, 0, 0)),
        "S_Thrust": ("J_Torso", ch["thrust"], _d(-1, 0, 0)),
        "S_Vent_L": ("J_Torso", ch["vent_L"], ch["vent_dir_L"]),
        "S_Vent_R": ("J_Torso", ch["vent_R"], ch["vent_dir_R"]),
        "S_Embark": ("J_Torso", ch["embark"], _d(1, 0, 0)),
        "S_Rodeo": ("J_Torso", (-0.55, 0.0, 5.72), None),          # not used (no rodeo / batteries); empty kept by SPEC 3.3
        "S_Optic": ("J_Optic", ch["optic_face"], _d(1, 0, 0)),
        "S_Muzzle": ("W_Cannon", ch["muzzle"], _d(0, 0, -1)),
        "S_Dmg_Torso_F": ("J_Torso", ch["dmg_f"], None),
        "S_Dmg_Torso_B": ("J_Torso", ch["dmg_b"], None),
        "S_Dmg_Shoulder_L": ("J_Shoulder_L", (0.0, SH_Y + 0.30, Z_SH - 0.20), None),
        "S_Dmg_Shoulder_R": ("J_Shoulder_R", (0.0, -SH_Y - 0.30, Z_SH - 0.20), None),
        "S_Dmg_Elbow_L": ("J_Elbow_L", SKELETON["J_Elbow_L"][1], None),
        "S_Dmg_Elbow_R": ("J_Elbow_R", SKELETON["J_Elbow_R"][1], None),
        "S_Dmg_Thigh_L": ("J_Hip_L", (0.42, HIP_Y, 1.80), None),
        "S_Dmg_Thigh_R": ("J_Hip_R", (0.42, -HIP_Y, 1.80), None),
        "S_Dmg_Knee_L": ("J_Knee_L", (0.62, HIP_Y, 1.05), None),
        "S_Dmg_Knee_R": ("J_Knee_R", (0.62, -HIP_Y, 1.05), None),
        "S_Foot_L": ("J_Ankle_L", (0.20, HIP_Y, 0.0), None),
        "S_Foot_R": ("J_Ankle_R", (0.20, -HIP_Y, 0.0), None),
    }
    la = ch["launcher"]
    for i, (dy, dz) in enumerate([(y, z) for z in (0.10, -0.03) for y in (-0.12, 0.0, 0.12)]):
        S["S_Rocket_%d" % (i + 1)] = ("J_Launcher_L", (la[0] + 0.10, la[1] + dy, la[2] + dz), _d(1, 0, 0.2))
    return S


# H-1 Forge
H1 = dict(
    hatch=(1.30, 0.0, 4.12), optic=(1.06, -0.80, 5.30), launcher=(-0.45, 1.40, 5.42),
    chest=(1.20, 0.0, 4.68), thrust=(-1.14, 0.30, 4.10), embark=(1.75, 0.0, 4.10),
    vent_L=(-0.10, 1.17, 4.08), vent_R=(-0.10, -1.17, 4.08), vent_dir_L=_d(0, 1, -0.2), vent_dir_R=_d(0, -1, -0.2),
    optic_face=(1.27, -0.80, 5.30), muzzle=(0.0, -SH_Y, 2.30),
    dmg_f=(1.30, 0.55, 4.90), dmg_b=(-1.10, 0.0, 4.60),
)
H1_EXTRA = {
    "S_Flame_L": ("J_Elbow_L", (0.0, SH_Y + 0.46, 2.64), _d(0, 0, -1)),          # along the forearm: forward in the aim pose
    "S_Tank_L": ("J_Torso", (-1.30, 0.55, 5.90), _d(0, 0, 1)),
    "S_Tank_R": ("J_Torso", (-1.30, -0.55, 5.90), _d(0, 0, 1)),
    "S_Trap": ("J_Torso", (0.53, -1.55, 5.83), _d(math.cos(math.radians(30)), 0, math.sin(math.radians(30)))),
}

# H-2 Legion
H2 = dict(
    hatch=(1.33, 0.0, 4.15), optic=(1.00, 0.0, 5.38), launcher=(-0.40, 1.30, 5.40),
    chest=(1.15, 0.0, 4.62), thrust=(-1.18, 0.55, 4.45), embark=(1.75, 0.0, 4.10),
    vent_L=(-1.17, 0.55, 5.05), vent_R=(-1.17, 0.15, 5.05), vent_dir_L=_d(-1, 0, 0), vent_dir_R=_d(-1, 0, 0),
    optic_face=(1.10, 0.0, 5.38), muzzle=(0.0, -SH_Y, 0.30),
    dmg_f=(1.32, 0.55, 4.80), dmg_b=(-1.17, 0.40, 4.40),
)
H2_EXTRA = {
    "J_Barrel": ("W_Cannon", (0.0, -SH_Y, 2.55), None),          # spins about the cannon axis (SOCKET_Barrel)
    "J_Drum": ("J_Torso", (-1.48, -0.62, 4.80), None),            # spins about x (SOCKET_Drum)
    "S_Drum": ("J_Drum", (-1.48, -0.62, 4.80), _d(-1, 0, 0)),
    "S_GunShield": ("W_Cannon", (0.0, -SH_Y, 0.90), _d(0, 0, -1)),   # 0.6 m behind the muzzle, facing out of the barrels
    "S_Eject": ("W_Cannon", (0.0, -SH_Y - 0.46, 3.05), _d(0, -1, -1)),
}


def nodes(which):
    """All nodes (name -> (parent, pos, dir)) for 'H1' or 'H2', parents before children."""
    ch = H1 if which == "H1" else H2
    out = {n: (p, pos, None) for n, (p, pos) in SKELETON.items()}
    out["J_Hatch"] = ("J_Torso", ch["hatch"], None)
    out["J_Optic"] = ("J_Torso", ch["optic"], None)
    out["J_Launcher_L"] = ("J_Torso", ch["launcher"], None)
    extra = H1_EXTRA if which == "H1" else H2_EXTRA
    for n, v in extra.items():
        if n.startswith("J_"):
            out[n] = v
    for n, v in common_sockets(ch).items():
        out[n] = v
    for n, v in extra.items():
        if not n.startswith("J_"):
            out[n] = v
    return out
