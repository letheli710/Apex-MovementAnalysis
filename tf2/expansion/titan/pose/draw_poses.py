"""Stick figures of titan states from decoded animation data (bones only, no game art)."""
import os

from PIL import Image, ImageDraw, ImageFont

from anim53 import Anim, Mdl, world
from joints import CHASSIS, ROOT

FONT = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
CHAINS = [
    (["def_c_hip", "def_c_spineA", "def_c_spineB", "def_c_spineC", "def_c_neckA", "def_c_head"], (40, 40, 40), 4),
    (["def_c_spineC", "def_l_clav", "def_l_shoulder", "def_l_elbow", "def_l_wrist"], (30, 110, 200), 3),
    (["def_c_spineC", "def_r_clav", "def_r_shoulder", "def_r_elbow", "def_r_wrist"], (210, 70, 50), 3),
    (["def_c_hip", "def_l_hip", "def_l_thigh", "def_l_knee", "def_l_ankle", "def_l_ball"], (30, 110, 200), 3),
    (["def_c_hip", "def_r_hip", "def_r_thigh", "def_r_knee", "def_r_ankle", "def_r_ball"], (210, 70, 50), 3),
]
ROWS = [
    ("站立待机", "mp_core", "a_MP_CQB_idle", 0), ("蹲", "mp_core", "a_MP_crouch_IDLE", 0),
    ("走·蹬地", "mp_core", "a_WalkForward", .05), ("走·腾步", "mp_core", "a_WalkForward", .26),
    ("走·右前", "mp_core", "a_WalkForward_R", .05), ("走·后", "mp_core", "a_combat_WalkBackward", .05),
    ("跑", "mp_core", "a_RunForward", .05), ("跑·腾步", "mp_core", "a_RunForward", .3),
    ("冲刺跑", "mp_core", "a_combat_sprint", .05), ("冲刺跑·腾", "mp_core", "a_combat_sprint", .3),
    ("冲刺跑左倾", "mp_core", "a_combat_sprint_Lean_L", .05), ("冲刺跑右倾", "mp_core", "a_combat_sprint_Lean_R", .05),
    ("dash 起·前", "mp_core", "at_Dodge_Start", .5), ("dash 飘·前", "mp_core", "at_Dodge_Float", .5),
    ("dash 落·前", "mp_core", "at_Dodge_Land", .4), ("dash 飘·右", "mp_core", "at_Dodge_Float_R", .5),
    ("dash 飘·左", "mp_core", "at_Dodge_Float_L", .5), ("dash 飘·后", "mp_core", "at_DodgeBackward_Float", .5),
    ("蹲走", "mp_core", "a_Crouch_WalkForward", .05), ("落地", "mp_core", "a_MP_Jump_end", .15),
    ("濒死待机", "mp_reactions", "@at_doomed_idle", .2), ("濒死走", "mp_reactions", "@at_doomed_walk_F", .3),
    ("近战拳·挥", "mp_synced", "@at_player_melee_punch_01", .35), ("跪下上机", "mp_embark", "@at_mount_kneel_front", .45),
]
CACHE = {}


def get(ch, part):
    k = (ch, part)
    if k not in CACHE:
        m = Mdl(os.path.join(ROOT, CHASSIS[ch] + "_" + part + ".mdl"))
        CACHE[k] = (m, {Anim(m, i).name: Anim(m, i) for i in range(m.numlocalanim)}, {b["name"]: b["idx"] for b in m.bones})
    return CACHE[k]


def draw(d, W, idx, ox, oy, s, axis):
    d.line((ox - 60, oy, ox + 60, oy), fill=(190, 190, 190))
    for ch, col, w in CHAINS:
        pts = []
        for n in ch:
            if n in idx:
                p = W[idx[n]][0]
                h = p[0] if axis == "x" else -p[1]
                pts.append((ox + h * s, oy - p[2] * s))
        d.line(pts, fill=col, width=w)


def sheet(ch, cols=6, W_=210, H_=250):
    n = len(ROWS)
    S = Image.new("RGB", (cols * W_, ((n + cols - 1) // cols) * H_ + 30), "white")
    d = ImageDraw.Draw(S)
    d.text((6, 6), ch + "：每格左=侧视（右为前），右=正视。蓝=左肢 红=右肢。由动画数据解算，不含游戏美术", fill=(0, 0, 0), font=FONT)
    for i, (lab, part, anim, f) in enumerate(ROWS):
        x, y = (i % cols) * W_, 30 + (i // cols) * H_
        d.rectangle((x, y, x + W_ - 1, y + H_ - 1), outline=(225, 225, 225))
        d.text((x + 4, y + 2), lab, fill=(0, 0, 0), font=FONT)
        m, A, idx = get(ch, part)
        a = A.get(anim)
        if a is None:
            d.text((x + 4, y + 40), "（无此动画）", fill=(160, 0, 0), font=FONT)
            continue
        W = world(m, a.local(min(a.frames - 1, int(f * a.frames))))
        draw(d, W, idx, x + W_ * 0.28, y + H_ - 14, 0.72, "x")
        draw(d, W, idx, x + W_ * 0.74, y + H_ - 14, 0.72, "y")
    S.save("out/poses_%s.png" % ch)


for c in CHASSIS:
    sheet(c)
