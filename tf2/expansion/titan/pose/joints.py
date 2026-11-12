"""Joint angles and body metrics from decoded titan animation frames.

Model axes after the root rotation: +X forward, +Y left, +Z up (units: inches = TF2 u).
Output: pose/out/joint_frames_<chassis>.csv, one row per anim per frame, plus summaries via summarize.py.
"""
import csv
import math
import os
import sys

from anim53 import Anim, Mdl, Seq, qconj, qmul, qrot, world

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "local", "titan-models", "models")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
CHASSIS = {"light": "titans/light/titan_light", "medium": "titans/medium/titan_medium", "heavy": "titans/heavy/titan_heavy"}
PARTS = ["mp_core", "mp_reactions", "mp_scripted", "mp_synced", "mp_embark", "mp_melee", "sp_core"]


def v(a, b):
    return (b[0] - a[0], b[1] - a[1], b[2] - a[2])


def norm(a):
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def angle(a, b):
    na, nb = norm(a), norm(b)
    if na < 1e-6 or nb < 1e-6:
        return 0.0
    return math.degrees(math.acos(max(-1, min(1, dot(a, b) / na / nb))))


def euler(q):
    """Rotation in model axes -> yaw (about Z), pitch (about Y, + nose down), roll (about X), degrees."""
    x, y, z, w = q
    if w < 0:
        x, y, z, w = -x, -y, -z, -w
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    s = max(-1, min(1, 2 * (w * y - z * x)))
    pitch = math.asin(s)
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    return math.degrees(yaw), math.degrees(pitch), math.degrees(roll)


def swing_twist(q):
    """Split about model Z: returns twist (about Z), then swing about Y and X, in degrees; no wrap at 90."""
    x, y, z, w = q
    if w < 0:
        x, y, z, w = -x, -y, -z, -w
    twist = 2 * math.atan2(z, w)
    # swing = q * conj(twist)
    n = math.hypot(z, w) or 1
    tw = (0.0, 0.0, z / n, w / n)
    sx, sy, sz, sw = qmul((x, y, z, w), qconj(tw))
    return (
        math.degrees((twist + math.pi) % (2 * math.pi) - math.pi),
        math.degrees(2 * math.atan2(sy, sw)),
        math.degrees(2 * math.atan2(sx, sw)),
    )


def qangle(q):
    return 2 * math.degrees(math.acos(min(1.0, abs(q[3]))))


class Rig:
    def __init__(self, m):
        self.m = m
        self.idx = {b["name"]: b["idx"] for b in m.bones}
        # Rest orientation in the model frame comes from the anim root rotation applied to the rest pose.
        a0 = Anim(m, 0)
        self.rest = world(m, [a0.local(0)[0]] + [None] * (m.numbones - 1))

    def has(self, *names):
        return all(n in self.idx for n in names)

    def rel(self, W, child, parent):
        """Rotation of child relative to parent, measured from rest and written in model axes."""
        c, p = self.idx[child], self.idx[parent]
        dc = qmul(W[c][1], qconj(self.rest[c][1]))
        dp = qmul(W[p][1], qconj(self.rest[p][1]))
        return qmul(qconj(dp), dc)

    def to_frame(self, W, bone, vec):
        """World vector -> frame of a bone's rest-aligned axes (X fwd, Y left, Z up when bone is at rest)."""
        i = self.idx[bone]
        d = qmul(W[i][1], qconj(self.rest[i][1]))
        return qrot(qconj(d), vec)


def metrics(rig, W):
    i = rig.idx
    p = lambda n: W[i[n]][0]
    r = {}
    root_z = 0
    r["hip_z"] = p("def_c_hip")[2]
    r["hip_x"] = p("def_c_hip")[0]
    r["hip_y"] = p("def_c_hip")[1]
    r["head_z"] = p("def_c_head")[2]
    r["chest_z"] = p("def_c_spineC")[2]
    r["pov_x"], r["pov_y"], r["pov_z"] = p("jx_c_pov")
    r["cam_x"], r["cam_y"], r["cam_z"] = p("jx_c_camera")
    # world attitude of pelvis and chest (from rest)
    for name, bone in (("pelvis", "def_c_hip"), ("chest", "def_c_spineC"), ("head", "def_c_head")):
        d = qmul(W[i[bone]][1], qconj(rig.rest[i[bone]][1]))
        y, pi, ro = euler(d)
        r[name + "_yaw"], r[name + "_pitch"], r[name + "_roll"] = y, pi, ro
    # spine: chest relative to pelvis
    y, pi, ro = swing_twist(rig.rel(W, "def_c_spineC", "def_c_hip"))
    r["waist_twist"], r["waist_bend"], r["waist_side"] = y, pi, ro
    y, pi, ro = swing_twist(rig.rel(W, "def_c_head", "def_c_spineC"))
    r["neck_yaw"], r["neck_pitch"], r["neck_roll"] = y, pi, ro
    for side in "lr":
        s = "def_%s_" % side
        sgn = 1 if side == "l" else -1
        # arm in chest frame
        sh, el, wr = p(s + "shoulder"), p(s + "elbow"), p(s + "wrist")
        ua = rig.to_frame(W, "def_c_spineC", v(sh, el))
        n = norm(ua) or 1
        r[side + "_sh_fwd"] = math.degrees(math.asin(max(-1, min(1, ua[0] / n))))  # + = forward component, -90..90
        r[side + "_sh_out"] = math.degrees(math.asin(max(-1, min(1, sgn * ua[1] / n))))  # + = outward component
        r[side + "_sh_elev"] = math.degrees(math.acos(max(-1, min(1, -ua[2] / n))))  # 0 hanging, 90 horizontal, 180 up
        r[side + "_elbow"] = 180 - angle(v(sh, el), v(el, wr)) if False else angle(v(sh, el), v(el, wr))  # 0 straight
        y, pi, ro = euler(rig.rel(W, s + "wrist", s + "elbow"))
        r[side + "_wrist_total"] = qangle(rig.rel(W, s + "wrist", s + "elbow"))
        y, pi, ro = euler(rig.rel(W, s + "clav", "def_c_spineC"))
        r[side + "_clav_total"] = qangle(rig.rel(W, s + "clav", "def_c_spineC"))
        # leg in pelvis frame
        th, kn, an, ba = p(s + "thigh"), p(s + "knee"), p(s + "ankle"), p(s + "ball")
        ul = rig.to_frame(W, "def_c_hip", v(th, kn))
        n = norm(ul) or 1
        r[side + "_hip_fwd"] = math.degrees(math.atan2(ul[0], -ul[2]))  # + = thigh forward
        r[side + "_hip_out"] = math.degrees(math.asin(max(-1, min(1, sgn * ul[1] / n))))  # + = outward
        r[side + "_hip_total"] = math.degrees(math.acos(max(-1, min(1, -ul[2] / n))))
        y, pi, ro = swing_twist(rig.rel(W, s + "thigh", "def_c_hip"))
        r[side + "_hip_twist"] = y
        r[side + "_knee"] = angle(v(th, kn), v(kn, an))  # 0 straight, grows with flexion
        # ankle: foot vector vs shin, 90 = foot square to shin
        r[side + "_ankle"] = angle(v(kn, an), v(an, ba))
        ba_frame = v(an, ba)
        r[side + "_foot_pitch"] = math.degrees(math.atan2(-ba_frame[2], math.hypot(ba_frame[0], ba_frame[1])))  # + = toe down
        r[side + "_ball_x"], r[side + "_ball_y"], r[side + "_ball_z"] = ba
        r[side + "_ankle_z"] = an[2]
        r[side + "_hand_x"], r[side + "_hand_y"], r[side + "_hand_z"] = wr
    r["stance_w"] = abs(r["l_ball_y"] - r["r_ball_y"])
    r["stride_x"] = abs(r["l_ball_x"] - r["r_ball_x"])
    return r


def analyze(chassis):
    os.makedirs(OUT, exist_ok=True)
    rows = []
    fields = None
    for part in PARTS:
        path = os.path.join(ROOT, CHASSIS[chassis] + "_" + part + ".mdl")
        if not os.path.exists(path):
            continue
        m = Mdl(path)
        rig = Rig(m)
        need = ["def_c_hip", "def_c_spineC", "def_c_head", "jx_c_pov", "jx_c_camera", "def_l_shoulder", "def_l_elbow", "def_l_wrist", "def_l_thigh", "def_l_knee", "def_l_ankle", "def_l_ball", "def_l_clav"]
        if not rig.has(*need):
            print(part, "missing bones", [n for n in need if n not in rig.idx])
            continue
        for k in range(m.numlocalanim):
            a = Anim(m, k)
            if a.delta or a.data == 0:
                continue
            step = 1 if a.frames <= 240 else a.frames // 240
            for fr in range(0, a.frames, step):
                W = world(m, a.local(fr))
                r = metrics(rig, W)
                if fields is None:
                    fields = list(r.keys())
                rows.append([part, a.name, fr, a.frames, round(a.fps, 2), int(a.looping)] + [round(r[f], 2) for f in fields])
        print(chassis, part, "anims", m.numlocalanim, "rows", len(rows), flush=True)
    with open(os.path.join(OUT, "joint_frames_%s.csv" % chassis), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["part", "anim", "frame", "frames", "fps", "loop"] + fields)
        w.writerows(rows)


if __name__ == "__main__":
    for c in sys.argv[1:] or list(CHASSIS):
        analyze(c)
