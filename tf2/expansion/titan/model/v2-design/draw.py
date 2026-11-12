"""Drawings and spec.json from design.py. No game art: boxes on our own structure, skeleton numbers from the TF2 survey."""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import design as D

HERE = D.HERE
OUT = os.path.join(HERE, "out")
F = lambda s: ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", s)
S = D.V2
COL = {"torso": (120, 134, 92), "pelvis": (90, 92, 84), "waist": (60, 62, 66), "hip": (70, 72, 74), "thigh": (178, 164, 124), "shin": (150, 140, 108),
       "foot": (66, 68, 72), "anklelink": (70, 72, 74), "pauldron": (178, 164, 124), "uparm": (150, 140, 108), "forearm": (170, 156, 118), "claw": (66, 68, 72), "cannon": (48, 50, 54), "launcher": (120, 134, 92)}


def col(n):
    for k, v in COL.items():
        if n.startswith(k):
            return v
    return (150, 150, 150)


FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
NORM = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]


def render(d, B, proj, view_dir, extra=None):
    polys = []
    light = np.array([0.4, 0.5, 0.75])
    for n, b in B.items():
        c, R, h = b
        pts = D.corners(b)
        for f, nn in zip(FACES, NORM):
            N = R @ np.array(nn, float)
            if N @ view_dir >= 0:
                continue
            P = pts[list(f)]
            depth = (P @ view_dir).mean()
            sh = 0.55 + 0.45 * max(0, float(N @ light))
            polys.append((depth, [proj(p) for p in P], tuple(int(v * sh) for v in col(n))))
    for dep, pp, c in sorted(polys, key=lambda t: -t[0]):
        d.polygon(pp, fill=c, outline=(30, 30, 30))


def ortho(d, B, ox, oy, s, hor, sign, view):
    proj = lambda p: (ox + sign * p[hor] * s, oy - p[2] * s)
    render(d, B, proj, np.array(view, float))
    return proj


def blueprint():
    W, H = 1760, 860
    I = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(I)
    s = 118
    gy = 790
    d.text((20, 10), "HSD 基础泰坦 v2 结构图（方块只表示占位和转轴，不是外形）。单位 m。虚线 = 碰撞体 3.05 × 5.97", fill=(0, 0, 0), font=F(22))
    p = dict(D.STAND, s_flex_R=60, e_R=30, s_in_R=8, s_out_R=6, s_flex_L=15, e_L=80, s_out_L=12)
    pose = dict(p)
    pose, J, B = D.solve(S, pose)
    lift = float(J["pelvis"][0][2])
    centers = [(330, 1, "正视", 1, (1, 0, 0)), (930, 0, "侧视（前在左）", -1, (0, 1, 0))]
    # front view looks along -x: titan's left on the viewer's right
    for ox, hor, title, sign, _ in centers:
        view = np.array((-1, 0, 0), float) if hor == 1 else np.array((0, -1, 0), float)
        if hor == 0:
            proj = lambda q, ox=ox: (ox - q[0] * s, gy - q[2] * s)
        else:
            proj = lambda q, ox=ox: (ox + q[1] * s, gy - q[2] * s)
        d.text((ox - 60, 44), title, fill=(0, 0, 0), font=F(20))
        d.line((ox - 260, gy, ox + 300, gy), fill=(120, 120, 120), width=2)
        hw = 1.525 * s
        for seg in ((ox - hw, gy, ox - hw, gy - 5.97 * s), (ox + hw, gy, ox + hw, gy - 5.97 * s), (ox - hw, gy - 5.97 * s, ox + hw, gy - 5.97 * s)):
            d.line(seg, fill=(210, 40, 40), width=1)
        render(d, B, proj, view)
        for n in ("pelvis", "waist", "hip_L", "hip_R", "knee_L", "knee_R", "ankle_L", "ankle_R", "sh_L", "sh_R", "el_L", "el_R"):
            q = proj(J[n][0])
            d.ellipse((q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6), fill=(255, 210, 40), outline=(0, 0, 0))
        e = np.array(S["eye"])
        q = proj(e)
        d.ellipse((q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7), fill=(240, 60, 60), outline=(0, 0, 0))
    # height scale
    x0 = 30
    for z, lab in ((0.7, "踝 0.70"), (1.45, "膝 1.45"), (2.85, "髋轴 2.85"), (3.0, ""), (3.45, "腰 3.45"), (4.55, "肩 4.55"), (4.70, "眼 4.70 [实测]"), (5.88, "顶 5.88"), (5.97, "")):
        yy = gy - z * s
        d.line((x0 + 70, yy, 1240, yy), fill=(225, 225, 225))
        if lab:
            d.text((x0, yy - 10), lab, fill=(70, 70, 70), font=F(14))
    # legend and thigh sweep
    ox = 1420
    d.text((ox - 150, 44), "大腿前摆 110° 和躯干的关系", fill=(0, 0, 0), font=F(20))
    pose2 = dict(pose)
    for k in ("h_flex_L", "k_L", "a_L"):
        pose2.pop(k, None)
    pose2.update(h_flex_L=105, k_L=110, w_bend=25, pel_pitch=12, s_flex_L=35, e_L=15, s_out_L=25, s_flex_R=25, e_R=30, s_out_R=25, h_flex_R=-25, k_R=85, a_R=55)
    pose2.pop("a_R", None)
    q2, J2, B2 = D.solve(S, pose2)
    proj = lambda q: (ox - q[0] * 95 + 40, gy - q[2] * 95)
    render(d, B2, proj, np.array((0, -1, 0), float))
    d.line((ox - 220, gy, ox + 230, gy), fill=(120, 120, 120), width=2)
    txt = ["窄腰下段：大腿从两侧扫过", "躯干下段半宽 0.50 < 大腿内缘 0.61", "舱门宽 1.10 也从两腿之间开", "红点 = 第一人称眼 / 黄点 = 关节"]
    for i, t in enumerate(txt):
        d.text((ox - 200, 90 + i * 24), t, fill=(60, 60, 60), font=F(16))
    I.save(os.path.join(OUT, "blueprint.png"))


def poses():
    names = list(D.HAND)
    cols = 5
    cw, ch = 340, 330
    I = Image.new("RGB", (cols * cw, ((len(names) + cols - 1) // cols) * ch + 40), "white")
    d = ImageDraw.Draw(I)
    d.text((10, 8), "v2 结构试摆：TF2 量到的角度套到新结构上。红字 = 这个姿势还有碰撞", fill=(0, 0, 0), font=F(20))
    yaw, el = math.radians(-35), math.radians(14)
    cam_f = np.array([math.cos(el) * math.cos(yaw), math.cos(el) * math.sin(yaw), math.sin(el)])  # toward camera
    right = np.array([-math.sin(yaw), math.cos(yaw), 0.0])
    up = np.cross(cam_f, right)
    up = up if up[2] > 0 else -up
    for i, n in enumerate(names):
        q, J, B = D.solve(S, D.HAND[n])
        hits = D.collisions(S, B)
        ox, oy = (i % cols) * cw, 40 + (i // cols) * ch
        s = 42
        proj = lambda p, ox=ox, oy=oy: (ox + cw / 2 + (p @ right) * s, oy + ch - 18 - (p @ up) * s)
        d.polygon([proj(np.array(v, float)) for v in ((-3, -3, 0), (3, -3, 0), (3, 3, 0), (-3, 3, 0))], fill=(236, 236, 232))
        render(d, B, proj, -cam_f)
        d.text((ox + 6, oy + 2), n, fill=(190, 20, 20) if hits else (0, 0, 0), font=F(16))
        if hits:
            d.text((ox + 6, oy + 22), "; ".join(hits)[:44], fill=(190, 20, 20), font=F(12))
    I.save(os.path.join(OUT, "poses.png"))


def fp():
    W, H = 1280, 720
    I = Image.new("RGB", (W, H), (205, 215, 225))
    d = ImageDraw.Draw(I)
    d.rectangle((0, H // 2, W, H), fill=(165, 160, 150))
    q, J, B = D.solve(S, D.aim_arm(dict(D.STAND), 0))
    B = {k: v for k, v in B.items() if k in ("cannon_R", "forearm_L", "claw_L", "uparm_R")}
    eye = np.array(S["eye"], float)
    fx = (W / 2) / math.tan(math.radians(91 / 2))

    def proj(p):
        v = p - eye
        x = max(v[0], 0.05)
        return (W / 2 - v[1] / x * fx, H / 2 - v[2] / x * fx)

    render(d, {k: v for k, v in B.items()}, proj, np.array((1, 0, 0), float))
    for m in (0, 1):
        d.line((W / 2 - 12, H / 2, W / 2 + 12, H / 2), fill=(255, 255, 255), width=2)
        d.line((W / 2, H / 2 - 12, W / 2, H / 2 + 12), fill=(255, 255, 255), width=2)
    d.text((16, 12), "第一人称（FOV 75，16:9，水平约 91°）。炮水平瞄准。只画手臂和炮，舱框另做", fill=(0, 0, 0), font=F(20))
    I.save(os.path.join(OUT, "fp_view.png"))


def spec():
    rest = {
        "J_Pelvis": (0, 0, S["pelvis_z"]), "J_Waist": (0, 0, S["waist_z"]),
        "J_Hip_L": (0, S["hip_x"], S["hip_z"]), "J_Knee_L": (0, S["hip_x"], S["knee_z"]), "J_Ankle_L": (0, S["hip_x"], S["ankle_z"]),
        "J_Shoulder_L": S["shoulder"], "J_Elbow_L": (0, S["shoulder"][1], S["shoulder"][2] - S["upper_arm"]), "J_Wrist_L": (0, S["shoulder"][1], S["shoulder"][2] - S["upper_arm"] - S["forearm"]),
        "J_Hatch": D.HATCH["hinge"], "J_Optic": (0.92, 0, 5.40), "J_Launcher_L": (-0.30, 0.62, 5.58),
        "S_Eye": S["eye"], "S_Seat": (0.25, 0, 3.92),
    }
    for k in ("Hip", "Knee", "Ankle", "Shoulder", "Elbow"):
        x, y, z = rest["J_%s_L" % k]
        rest["J_%s_R" % k] = (x, -y, z)
    x, y, z = rest["J_Elbow_R"]
    rest["W_Cannon"] = (x, y, z)
    rest["S_Muzzle"] = (x, y, z - S["cannon_len"])
    data = dict(axes_analysis="x forward, y left, z up", axes_blender="X = titan left (y), Y = -x (front is -Y), Z up", units="m",
                joints_analysis={k: [round(float(v), 3) for v in p] for k, p in rest.items()},
                joints_blender={k: [round(float(p[1]), 3), round(float(-p[0]), 3), round(float(p[2]), 3)] for k, p in rest.items()},
                expected_poses={n: {j: dict(o=[round(float(v), 4) for v in T[0]], R=[[round(float(x), 5) for x in row] for row in T[1]]) for j, T in D.solve(S, q)[1].items()} for n, q in D.HAND.items()},
                limits_deg=D.LIMITS, parts=S["parts"], hatch=D.HATCH, shape_targets=dict(top=S["top"]), hand_poses=D.HAND)
    json.dump(data, open(os.path.join(OUT, "spec.json"), "w"), indent=1, ensure_ascii=False)


blueprint()
poses()
fp()
spec()
print("done")
