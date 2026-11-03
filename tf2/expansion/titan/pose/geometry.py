"""TF2 titan proportions: bone lengths and heights in a standing frame, per-sequence bounding boxes,
and bone-derived tops per state. Writes out/geometry.txt. Numbers only."""
import math
import os
import struct

from anim53 import Anim, Mdl, Seq, world
from joints import CHASSIS, ROOT

M = 0.0254
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def d(a, b):
    return math.dist(a, b)


SEQS = ["CQB_Idle_MP", "CQB_ADS_Idle_MP", "CQB_CrouchIdle_MP", "Walk_forward_MP", "Run_forward_MP", "Sprint_mp_forward", "Walk_Crouch_forward_MP", "at_MP_dodge_float", "at_MP_dodge_land", "Jump_end_MP"]
for ch, base in CHASSIS.items():
    m = Mdl(os.path.join(ROOT, base + "_mp_core.mdl"))
    idx = {b["name"]: b["idx"] for b in m.bones}
    A = {Anim(m, i).name: Anim(m, i) for i in range(m.numlocalanim)}
    W = world(m, A["a_MP_CQB_idle"].local(0))
    p = lambda n: W[idx[n]][0]
    P("==", ch, "standing idle, heights in m (x fwd, y left, z up)")
    for n in ["def_c_hip", "def_c_spineA", "def_c_spineC", "def_c_neckA", "def_c_head", "def_l_clav", "def_l_shoulder", "def_l_elbow", "def_l_wrist", "def_r_shoulder", "def_r_elbow", "def_r_wrist", "ja_c_propGun", "def_l_thigh", "def_l_knee", "def_l_ankle", "def_l_ball", "def_r_thigh", "def_r_knee", "def_r_ankle", "def_r_ball"]:
        if n in idx:
            print_p = [round(v * M, 2) for v in p(n)]
            P(" ", n, print_p)
    seg = [("hip->chest", "def_c_hip", "def_c_spineC"), ("chest->head", "def_c_spineC", "def_c_head"), ("clav->shoulder", "def_l_clav", "def_l_shoulder"),
           ("shoulder->elbow", "def_l_shoulder", "def_l_elbow"), ("elbow->wrist", "def_l_elbow", "def_l_wrist"),
           ("thigh->knee", "def_l_thigh", "def_l_knee"), ("knee->ankle", "def_l_knee", "def_l_ankle"), ("ankle->ball", "def_l_ankle", "def_l_ball")]
    P(" lengths m:", {k: round(d(p(a), p(b)) * M, 2) for k, a, b in seg})
    P(" model hull u", [round(v, 1) for v in m.hull], "eye", m.eye)
    P(" sequence bbox from file, m: (xmin xmax ymin ymax zmin zmax)")
    for k in range(m.numlocalseq):
        s = Seq(m, k)
        if s.label in SEQS:
            bb = struct.unpack_from("<6f", m.b, s.off + 0x20)
            P("  ", s.label, [round(bb[i] * M, 2) for i in (0, 3, 1, 4, 2, 5)])
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "geometry.txt"), "w", encoding="utf-8").write("\n".join(lines))
