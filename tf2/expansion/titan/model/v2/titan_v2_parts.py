"""Part table of the v2 graybox. Every part is written in its joint's local frame at rest, ANALYSIS axes (x forward, y left, z up),
and stays inside the matching box of spec.parts unless a comment says otherwise. Shape rules: DESIGN.md section 2.

The wedge profiles on the thigh, shin, upper arm and forearm are what lets the knee reach 140 and the elbows 140 / 120: at flex f the
two segments meet where half-thickness = d * tan((180 - f) / 2), d = distance from the joint."""
from prims import box, cyl, ext_poly
from prims_v2 import loft, ball, merge, rect16, circle16
from titan_v2_data import ROCKET_TUBES, FINGER_ROOTS

PARTS = []


def add(joint, m):
    m.joint = joint
    PARTS.append(m)


def R(z, x0, x1, y0, y1, c=0.08):
    return (z, rect16(x0, x1, y0, y1, c))


def C(z, cx, cy, r):
    return (z, circle16(cx, cy, r))


def yaxis(name, x, z, y0, y1, r, mat, seg=12):
    return cyl(name, (x, y0, z), (x, y1, z), r, mat=mat, seg=seg)


def zaxis(name, x, y, z0, z1, r0, r1=None, mat="dark", seg=12):
    return cyl(name, (x, y, z0), (x, y, z1), r0, r1, mat=mat, seg=seg)


def xaxis(name, y, z, x0, x1, r, mat, seg=10):
    return cyl(name, (x0, y, z), (x1, y, z), r, mat=mat, seg=seg)


def fork(name, z_center, gap, width, half_x, half_z, mat="hub"):
    """Two side plates around a joint hub. Nothing between them, so the hub never touches the fork."""
    a = box(name + "a", (0, gap + width / 2, z_center), (2 * half_x, width, 2 * half_z), mat)
    b = box(name + "b", (0, -gap - width / 2, z_center), (2 * half_x, width, 2 * half_z), mat)
    return merge(name, [a, b])


def stencil(name, origin, u, v, h=0.26, mat="white"):
    """The number 713 as thin boxes. origin = centre, u = reading direction, v = up, both unit vectors along axes."""
    w, t = h * 0.5, h * 0.2
    SEG = {"T": (0.5, 1.0, 1, 0), "M": (0.5, 0.5, 1, 0), "B": (0.5, 0.0, 1, 0), "UR": (1.0, 0.75, 0, 1), "LR": (1.0, 0.25, 0, 1)}
    GLYPH = [("T", "UR", "LR"), ("UR", "LR"), ("T", "M", "B", "UR", "LR")]
    out = []
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    for g, segs in enumerate(GLYPH):
        ox = (g - 1) * (w + 0.5 * t + 0.05) - w / 2
        for s in segs:
            cu, cv, horiz, vert = SEG[s]
            lu = w if horiz else t
            lv = h / 2 if vert else t
            c = [origin[i] + u[i] * (ox + cu * w) + v[i] * ((cv - 0.5) * h) for i in range(3)]
            size = [abs(u[i]) * lu + abs(v[i]) * lv + abs(n[i]) * 0.01 for i in range(3)]
            out.append(box(name + s, c, size, mat))
    return merge(name, out)


# ------------------------------------------------------------------ pelvis and waist
add("J_Pelvis", loft("Pelvis_Core", [R(-0.43, -0.36, 0.26, -0.26, 0.26, 0.08), R(-0.27, -0.51, 0.41, -0.46, 0.46, 0.14),
                                     R(0.08, -0.51, 0.41, -0.46, 0.46, 0.14), R(0.23, -0.42, 0.32, -0.38, 0.38, 0.10)], "olive"))
add("J_Pelvis", ext_poly("Pelvis_Plate", [(-0.20, -0.36), (0.20, -0.36), (0.26, -0.18), (0.26, 0.04), (-0.26, 0.04), (-0.26, -0.18)], "yz", 0.36, 0.42, "sand"))
add("J_Pelvis", ext_poly("Pelvis_Plate_Back", [(-0.20, -0.30), (0.20, -0.30), (0.26, -0.15), (-0.26, -0.15)], "yz", -0.54, -0.50, "sand"))
add("J_Waist", zaxis("Waist_Column", 0, 0, -0.32, 0.28, 0.32, mat="hub", seg=16))

# ------------------------------------------------------------------ torso. z = height above the waist axis (3.45 world).
add("J_Torso", loft("Torso_Shell", [
    C(0.20, 0.02, 0, 0.48), C(0.62, 0.02, 0, 0.50), C(0.70, 0.02, 0, 0.50),   # lower section: nearly round, stays within +-0.50
    R(0.92, -0.77, 0.87, -0.76, 0.76, 0.26),                                   # transition, width 1.52
    R(1.14, -0.88, 0.93, -0.90, 0.90, 0.28),
    R(1.25, -0.92, 0.93, -0.92, 0.92, 0.28),                                   # upper section, width 1.84
    R(2.13, -0.92, 0.93, -0.92, 0.92, 0.28)], "olive"))
add("J_Torso", ext_poly("Torso_HingeBracket", [(0.46, 0.70), (0.93, 0.70), (0.93, 0.92), (0.50, 0.92)], "xz", -0.42, 0.42, "dark"))
add("J_Torso", yaxis("Torso_HatchHinge", 0.95, 0.70, -0.45, 0.45, 0.05, "hub", 8))
add("J_Torso", box("Torso_Cockpit", (0.935, 0, 1.52), (0.01, 1.08, 1.16), "black"))
for sg, n, mat in ((1, "L", "sand"), (-1, "R", "olive")):
    y0, y1 = sorted((sg * 0.57, sg * 0.86))
    add("J_Torso", ext_poly("Torso_Cheek_" + n, [(0.70, 0.98), (0.93, 0.98), (1.07, 1.16), (1.07, 2.00), (0.95, 2.13), (0.70, 2.13)], "xz", y0, y1, mat))
    add("J_Torso", cyl("Torso_ShoulderMount_" + n, (0, sg * 0.70, 1.10), (0, sg * 0.96, 1.10), 0.20, 0.10, mat="hub"))
    add("J_Torso", box("Torso_Vent_" + n, (-0.96, sg * 0.42, 1.87), (0.02, 0.32, 0.26), "dark"))
# depth stops at -0.97 (spec torso_up) with this pack; the shell itself is 5 cm less so the pack reads as a part
add("J_Torso", box("Torso_BackPack", (-0.925, 0, 1.55), (0.07, 1.20, 0.90), "sand"))
add("J_Torso", xaxis("Torso_ThrustNozzle", 0, 1.50, -0.97, -0.94, 0.20, "dark", 12))
# the top is split so the launcher has room on the left: crown to the right, brow over the optic
add("J_Torso", loft("Torso_Crown", [R(2.10, -0.90, 0.40, -0.85, 0.30, 0.12), R(2.30, -0.85, 0.40, -0.80, 0.30, 0.12), R(2.43, -0.70, 0.30, -0.55, 0.30, 0.10)], "olive"))
add("J_Torso", ext_poly("Torso_Brow", [(0.15, 2.10), (0.93, 2.10), (0.93, 2.17), (1.07, 2.20), (0.98, 2.40), (0.30, 2.43), (0.15, 2.43)], "xz", -0.62, 0.34, "sand"))
add("J_Torso", zaxis("Torso_Antenna", -0.55, -0.35, 2.40, 3.30, 0.03, 0.012, "dark", 6))

# ------------------------------------------------------------------ hatch: door from the hinge up, notched around the optic
add("J_Hatch", box("Hatch_Center", (0.05, 0, 0.475), (0.10, 0.56, 0.95), "sand"))
add("J_Hatch", ext_poly("Hatch_Wing_L", [(0.28, 0), (0.55, 0), (0.55, 1.20), (0.42, 1.35), (0.28, 1.35)], "yz", 0, 0.10, "olive"))
add("J_Hatch", ext_poly("Hatch_Wing_R", [(-0.55, 0), (-0.28, 0), (-0.28, 1.35), (-0.42, 1.35), (-0.55, 1.20)], "yz", 0, 0.10, "sand"))
add("J_Hatch", stencil("Hatch_713", (0.105, 0, 0.45), (0, 1, 0), (0, 0, 1), 0.26))

# ------------------------------------------------------------------ optic
add("J_Optic", ball("Optic_Ball", (0, 0, 0), 0.20, mat="dark", seg=12, rings=6))
add("J_Optic", xaxis("Optic_Lens", 0, 0, 0.14, 0.205, 0.125, "optic", 12))

# ------------------------------------------------------------------ launcher: spec box, sits on the torso top left
add("J_Launcher_L", loft("Launcher_Pod", [R(0.01, -0.42, 0.42, -0.26, 0.26, 0.05), R(0.30, -0.42, 0.42, -0.26, 0.26, 0.05)], "dark"))
add("J_Launcher_L", box("Launcher_Band", (0.10, 0, 0.155), (0.14, 0.53, 0.29), "yellow"))
add("J_Launcher_L", box("Launcher_Mount", (0, 0, 0), (0.40, 0.24, 0.05), "hub"))
add("J_Launcher_L", merge("Launcher_Tubes", [xaxis("t%d" % i, t[1], t[2], 0.40, 0.44, 0.058, "black", 8) for i, t in enumerate(ROCKET_TUBES)]))


# ------------------------------------------------------------------ legs
def leg(sg, n):
    def s(z, x0, x1, y, c=0.08):
        return R(z, x0, x1, -y, y, c)
    hip, knee, ankle = "J_Hip_" + n, "J_Knee_" + n, "J_Ankle_" + n
    y0, y1 = sorted((sg * 0.40, sg * 0.67))
    add("J_Pelvis", cyl("Pelvis_HipAxle_" + n, (0, y0, -0.15), (0, y1, -0.15), 0.13, mat="hub"))
    add(hip, ball("Hip_Ball_" + n, (0, 0, 0), 0.33, 0.20, 0.33, "hub"))
    add(hip, loft("Thigh_" + n, [s(-0.26, -0.30, 0.27, 0.21, 0.10), s(-0.55, -0.30, 0.27, 0.21), s(-0.78, -0.24, 0.27, 0.21),
                                 s(-1.05, -0.11, 0.25, 0.21), s(-1.18, -0.06, 0.20, 0.21)], "sand"))
    add(hip, ext_poly("Thigh_Plate_" + n, [(-0.14, -0.95), (0.14, -0.95), (0.18, -0.70), (0.18, -0.32), (-0.18, -0.32), (-0.18, -0.70)], "yz", 0.25, 0.30, "olive"))
    add(hip, fork("Thigh_Fork_" + n, -1.36, 0.155, 0.055, 0.12, 0.17))
    add(knee, yaxis("Knee_Hub_" + n, 0, 0, -0.145, 0.145, 0.17, "hub"))
    add(knee, loft("Shin_" + n, [s(-0.15, -0.05, 0.13, 0.14, 0.04), s(-0.27, -0.08, 0.18, 0.14, 0.04), s(-0.30, -0.09, 0.20, 0.20), s(-0.45, -0.14, 0.23, 0.22), s(-0.56, -0.19, 0.21, 0.22)], "olive"))
    add(knee, ext_poly("Shin_Plate_" + n, [(0.20, -0.25), (0.23, -0.30), (0.23, -0.52), (0.20, -0.55), (0.0, -0.55), (0.0, -0.25)], "xz", -0.14, 0.14, "sand"))
    add(knee, fork("Shin_Fork_" + n, -0.68, 0.155, 0.06, 0.11, 0.17))
    add(ankle, ball("Ankle_Hub_" + n, (0, 0, 0), 0.13, mat="hub", seg=8, rings=4))
    add(ankle, box("Ankle_Pillar_" + n, (0, 0, -0.22), (0.26, 0.19, 0.20), "hub"))
    add(ankle, loft("Foot_" + n, [R(-0.70, -0.50, 1.13, -0.32, 0.32, 0.10), R(-0.60, -0.57, 1.13, -0.46, 0.46, 0.16), R(-0.50, -0.57, 0.80, -0.46, 0.46, 0.16), R(-0.32, -0.22, 0.42, -0.34, 0.34, 0.10)], "dark"))
    add(ankle, ext_poly("Foot_Top_" + n, [(-0.12, -0.31), (0.38, -0.31), (0.72, -0.47), (0.72, -0.52), (-0.12, -0.52)], "xz", -0.20, 0.20, "sand"))


# ------------------------------------------------------------------ arms: common shoulder and upper arm
def shoulder(sg, n, front, back, half_y):
    sh = "J_Shoulder_" + n

    def sy(a, b):
        return tuple(sorted((sg * a, sg * b)))
    add(sh, ball("Shoulder_Hub_" + n, (0, 0, 0), 0.345, mat="hub"))
    add(sh, loft("Pauldron_" + n, [R(-0.30, -0.28, 0.28, *sy(0.08, 0.38), 0.06), R(-0.12, -0.46, 0.46, *sy(-0.14, 0.42), 0.26),
                                   R(0.20, -0.46, 0.46, *sy(-0.14, 0.42), 0.26), R(0.36, -0.30, 0.30, *sy(0.22, 0.38), 0.05)], "sand" if n == "L" else "olive"))
    add(sh, loft("UpperArm_" + n, [R(-0.28, -back, front[0], -half_y, half_y, 0.05), R(-0.36, -back, front[0], -half_y, half_y, 0.05),
                                   R(-0.68, -back * 0.8, front[1], -half_y, half_y, 0.04)], "hub"))
    add(sh, fork("UpperArm_Fork_" + n, -0.86, 0.155, 0.06, 0.12, 0.18))


shoulder(1, "L", (0.20, 0.075), 0.22, 0.20)
shoulder(-1, "R", (0.20, 0.13), 0.26, 0.20)
leg(1, "L")
leg(-1, "R")
add("J_Shoulder_L", stencil("Pauldron_713", (0, 0.425, 0.05), (-1, 0, 0), (0, 0, 1), 0.20))
add("J_Shoulder_L", box("Pauldron_Band", (0.0, 0.40, -0.25), (0.60, 0.05, 0.10), "yellow"))

# left forearm and claw
add("J_Elbow_L", yaxis("Elbow_Hub_L", 0, 0, -0.145, 0.145, 0.17, "hub"))
add("J_Elbow_L", loft("Forearm_L", [R(-0.15, -0.08, 0.075, -0.14, 0.14, 0.03), R(-0.24, -0.15, 0.08, -0.14, 0.14, 0.03), R(-0.30, -0.22, 0.10, -0.20, 0.20, 0.05),
                                    R(-0.68, -0.22, 0.14, -0.20, 0.20, 0.06), R(-0.80, -0.10, 0.10, -0.10, 0.10, 0.03)], "sand"))
add("J_Wrist_L", ball("Wrist_Hub", (0, 0, 0), 0.09, mat="hub", seg=8, rings=4))
add("J_Wrist_L", loft("Palm", [R(-0.09, -0.10, 0.10, -0.10, 0.10, 0.03), R(-0.22, -0.22, 0.22, -0.20, 0.20, 0.05)], "dark"))
for name, (fx, fy, fz) in FINGER_ROOTS.items():
    add(name, ball(name.replace("J_", "") + "_Root", (0, 0, 0), 0.05, mat="hub", seg=6, rings=3))
    add(name, loft(name.replace("J_", ""), [R(-0.02, -0.06, 0.06, -0.06, 0.06, 0.02), R(-0.20, -0.07, 0.07, -0.06, 0.06, 0.02), R(-0.35, -0.025, 0.025, -0.03, 0.03, 0.01)], "hub"))

# right cannon: forearm. Local +x is the top side at level aim.
add("W_Cannon", yaxis("Cannon_Hub", 0, 0, -0.145, 0.145, 0.17, "hub"))
add("W_Cannon", loft("Cannon_Neck", [R(-0.15, -0.14, 0.09, -0.14, 0.14, 0.03), R(-0.30, -0.20, 0.10, -0.14, 0.14, 0.03)], "dark"))
add("W_Cannon", loft("Cannon_Body", [R(-0.30, -0.26, 0.12, -0.21, 0.21, 0.06), R(-0.70, -0.26, 0.20, -0.21, 0.21, 0.06), R(-1.55, -0.26, 0.26, -0.21, 0.21, 0.08),
                                     R(-1.68, -0.20, 0.20, -0.17, 0.17, 0.06)], "dark"))
add("W_Cannon", box("Cannon_Band", (0, 0, -1.30), (0.54, 0.44, 0.12), "yellow"))
add("W_Cannon", loft("Cannon_Barrel", [C(-1.60, 0, 0, 0.13), C(-2.00, 0, 0, 0.13)], "hub"))

# designed contact: the only mesh pairs the collision check leaves out. a, b (mesh names without G_), reason.
EXCLUDED = [
    ("Pelvis_Core", "Waist_Column", "腰柱底插进骨盆（固定连接，同转）"),
    ("Waist_Column", "Torso_Shell", "腰柱顶插进躯干下段，转轴就在腰柱上"),
    ("Pelvis_HipAxle_L", "Hip_Ball_L", "髋轴伸进髋球（关节支承）"),
    ("Pelvis_HipAxle_R", "Hip_Ball_R", "髋轴伸进髋球（关节支承）"),
    ("Torso_ShoulderMount_L", "Shoulder_Hub_L", "肩座伸进肩球（关节支承）"),
    ("Torso_ShoulderMount_R", "Shoulder_Hub_R", "肩座伸进肩球（关节支承）"),
    ("Torso_HatchHinge", "Hatch_Center", "铰链销穿过舱门下边"),
    ("Torso_HatchHinge", "Hatch_Wing_L", "铰链销穿过舱门下边"),
    ("Torso_HatchHinge", "Hatch_Wing_R", "铰链销穿过舱门下边"),
    ("Optic_Ball", "Torso_Shell", "单眼球嵌在躯干前面（球窝）"),
    ("Optic_Ball", "Torso_Brow", "单眼球上缘嵌进眉甲（球窝）"),
    ("Optic_Ball", "Torso_Cockpit", "单眼球穿过驾驶舱黑面板（球窝）"),
    ("Launcher_Mount", "Torso_Shell", "火箭巢底座固定在躯干顶"),
    ("Wrist_Hub", "Forearm_L", "腕球伸进前臂端（关节支承）"),
    ("Finger_L_1_Root", "Palm", "指根嵌在手掌（关节支承）"),
    ("Finger_L_2_Root", "Palm", "指根嵌在手掌（关节支承）"),
    ("Finger_L_3_Root", "Palm", "指根嵌在手掌（关节支承）"),
    ("Finger_L_1", "Palm", "手指根部贴手掌"),
    ("Finger_L_2", "Palm", "手指根部贴手掌"),
    ("Finger_L_3", "Palm", "手指根部贴手掌"),
]
