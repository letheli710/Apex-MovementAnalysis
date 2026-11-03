"""Titan structure derived from the TF2 measurements, checked before any modelling.

Parts are oriented boxes on a joint tree. Axes: x forward, y left, z up (metres), same as the TF2 analysis;
the Blender build uses front = -Y, left = +X (see DESIGN.md).
Test set: real TF2 medium + heavy animation frames from pose/out/joint_frames_*.csv (retargeted by joint angle),
plus aim combinations and the hand-set entrance / kneel poses HSD needs.
Run: py -3 design.py   -> out/report.json. `draw.py` makes the drawings from the same data.
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
POSE_OUT = os.path.join(HERE, "..", "..", "pose", "out")


def Rx(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


# ---------------------------------------------------------------- structure
V2 = dict(
    name="v2",
    hip_z=2.85, hip_x=0.86, pelvis_z=3.00, waist_z=3.45, knee_z=1.45, ankle_z=0.70,
    eye=(0.72, 0, 4.70), top=5.88,
    shoulder=(0.0, 1.30, 4.55), upper_arm=0.90, forearm=0.85, cannon_len=2.00, cannon_mount=-0.15,
    # name: (joint, centre xyz in the joint's local frame at rest, half size xyz). Rest pose = legs down, arms down.
    parts={
        "pelvis": ("pelvis", (-0.05, 0, -0.10), (0.46, 0.46, 0.33)),
        "waist": ("waist", (0, 0, -0.02), (0.32, 0.32, 0.30)),
        "torso_low": ("torso", (0.02, 0, 0.45), (0.50, 0.50, 0.25)),
        "torso_mid": ("torso", (0.05, 0, 0.92), (0.82, 0.76, 0.22)),
        "torso_up": ("torso", (0.05, 0, 1.67), (1.02, 0.92, 0.76)),
        "hip_L": ("hip_L", (0, 0.02, 0), (0.33, 0.24, 0.33)),
        "hip_R": ("hip_R", (0, -0.02, 0), (0.33, 0.24, 0.33)),
        "thigh_L": ("hip_L", (0, 0, -0.75), (0.30, 0.25, 0.55)),
        "thigh_R": ("hip_R", (0, 0, -0.75), (0.30, 0.25, 0.55)),
        "shin_L": ("knee_L", (-0.04, 0, -0.42), (0.27, 0.22, 0.38)),
        "shin_R": ("knee_R", (-0.04, 0, -0.42), (0.27, 0.22, 0.38)),
        "foot_L": ("ankle_L", (0.28, 0, -0.50), (0.85, 0.46, 0.20)),
        "foot_R": ("ankle_R", (0.28, 0, -0.50), (0.85, 0.46, 0.20)),
        "anklelink_L": ("ankle_L", (0, 0, -0.17), (0.25, 0.20, 0.20)),
        "anklelink_R": ("ankle_R", (0, 0, -0.17), (0.25, 0.20, 0.20)),
        "pauldron_L": ("sh_L", (0, 0.08, 0.05), (0.46, 0.34, 0.44)),
        "pauldron_R": ("sh_R", (0, -0.08, 0.05), (0.46, 0.34, 0.44)),
        "uparm_L": ("sh_L", (0, 0, -0.55), (0.22, 0.20, 0.30)),
        "uparm_R": ("sh_R", (0, 0, -0.55), (0.26, 0.24, 0.30)),
        "forearm_L": ("el_L", (0, 0, -0.42), (0.22, 0.20, 0.42)),
        "claw_L": ("el_L", (0, 0, -1.12), (0.28, 0.24, 0.30)),
        "cannon_R": ("el_R", (0, 0, -0.90), (0.26, 0.24, 1.10)),
        "launcher_L": ("torso", (-0.30, 0.62, 2.28), (0.42, 0.26, 0.15)),
    },
)
# Old structure for the dimension table only. The boxes are too rough to judge collisions: use pose-test/ for those.
OLD = dict(
    name="old",
    hip_z=3.60, hip_x=0.90, pelvis_z=3.60, waist_z=3.95, knee_z=2.10, ankle_z=0.70,
    eye=(0.8, 0, 4.70), top=6.25,
    shoulder=(0.0, 1.30, 5.30), upper_arm=1.11, forearm=0.96, cannon_len=2.30, cannon_mount=0.0,
    parts={
        "pelvis": ("pelvis", (0, 0, -0.05), (0.50, 0.62, 0.30)),
        "waist": ("waist", (0, 0, -0.12), (0.30, 0.30, 0.28)),
        "torso_up": ("torso", (0, 0, 1.15), (1.10, 1.05, 1.15)),
        "hip_L": ("hip_L", (0, 0.05, 0), (0.36, 0.28, 0.36)),
        "hip_R": ("hip_R", (0, -0.05, 0), (0.36, 0.28, 0.36)),
        "thigh_L": ("hip_L", (0, 0, -0.78), (0.30, 0.25, 0.55)),
        "thigh_R": ("hip_R", (0, 0, -0.78), (0.30, 0.25, 0.55)),
        "shin_L": ("knee_L", (0, 0, -0.70), (0.27, 0.22, 0.62)),
        "shin_R": ("knee_R", (0, 0, -0.70), (0.27, 0.22, 0.62)),
        "foot_L": ("ankle_L", (0.28, 0, -0.50), (0.95, 0.52, 0.20)),
        "foot_R": ("ankle_R", (0.28, 0, -0.50), (0.95, 0.52, 0.20)),
        "pauldron_L": ("sh_L", (0, 0.08, 0.05), (0.46, 0.34, 0.44)),
        "pauldron_R": ("sh_R", (0, -0.08, 0.05), (0.46, 0.34, 0.44)),
        "uparm_L": ("sh_L", (0, 0, -0.55), (0.22, 0.20, 0.30)),
        "uparm_R": ("sh_R", (0, 0, -0.55), (0.26, 0.24, 0.30)),
        "forearm_L": ("el_L", (0, 0, -0.45), (0.22, 0.20, 0.45)),
        "claw_L": ("el_L", (0, 0, -1.20), (0.28, 0.24, 0.30)),
        "cannon_R": ("el_R", (0, 0, -1.15), (0.26, 0.24, 1.15)),
    },
)
# Measured limits the structure must allow (deg). Source column in DESIGN.md.
LIMITS = {
    "pelvis": dict(yaw=(-30, 30), pitch=(-25, 35), roll=(-35, 35)),
    "waist": dict(yaw=(-90, 90), bend=(-25, 45), side=(-30, 30)),
    "hip": dict(flex=(-65, 110), out=(-20, 60), twist=(-35, 60)),
    "knee": dict(flex=(0, 140)),
    "ankle": dict(pitch=(-35, 60), roll=(-20, 20)),
}
IGNORE = {  # designed contact at a joint
    ("pelvis", "waist"), ("waist", "torso_low"), ("hip_L", "thigh_L"), ("hip_R", "thigh_R"), ("thigh_L", "shin_L"), ("thigh_R", "shin_R"),
    ("shin_L", "foot_L"), ("shin_R", "foot_R"), ("shin_L", "anklelink_L"), ("shin_R", "anklelink_R"), ("anklelink_L", "foot_L"), ("anklelink_R", "foot_R"), ("pelvis", "hip_L"), ("pelvis", "hip_R"), ("torso_low", "torso_mid"), ("torso_mid", "torso_up"),
    ("torso_low", "torso_up"), ("pauldron_L", "uparm_L"), ("pauldron_R", "uparm_R"), ("uparm_L", "forearm_L"), ("uparm_R", "cannon_R"),
    ("forearm_L", "claw_L"), ("pauldron_L", "torso_up"), ("pauldron_R", "torso_up"), ("launcher_L", "torso_up"), ("waist", "torso_mid"),
}
IGNORE |= {(b, a) for a, b in IGNORE}


def obb_hit(A, B, margin=0.0):
    """Separating axis test. A, B: (centre, R, half)."""
    ca, Ra, ha = A
    cb, Rb, hb = B
    t = Ra.T @ (cb - ca)
    R = Ra.T @ Rb
    AR = np.abs(R) + 1e-9
    ha = ha - margin
    hb = hb - margin
    for i in range(3):
        if abs(t[i]) > ha[i] + AR[i] @ hb:
            return False
        if abs(t @ R[:, i]) > AR[:, i] @ ha + hb[i]:
            return False
    for i in range(3):
        for j in range(3):
            ra = ha[(i + 1) % 3] * AR[(i + 2) % 3, j] + ha[(i + 2) % 3] * AR[(i + 1) % 3, j]
            rb = hb[(j + 1) % 3] * AR[i, (j + 2) % 3] + hb[(j + 2) % 3] * AR[i, (j + 1) % 3]
            if abs(t[(i + 2) % 3] * R[(i + 1) % 3, j] - t[(i + 1) % 3] * R[(i + 2) % 3, j]) > ra + rb:
                return False
    return True


def fk(S, p):
    """p: dict of joint angles. Returns {joint: (origin, R)} with feet not yet on the ground."""
    J = {}
    Rp = Rz(p.get("pel_yaw", 0)) @ Ry(p.get("pel_pitch", 0)) @ Rx(p.get("pel_roll", 0))
    op = np.array([0, 0, S["pelvis_z"]]) + np.array(p.get("pel_off", (0, 0, 0)), float)
    J["pelvis"] = (op, Rp)
    ow = op + Rp @ np.array([0, 0, S["waist_z"] - S["pelvis_z"]])
    J["waist"] = (ow, Rp)
    Rt = Rp @ Rz(p.get("w_yaw", 0)) @ Ry(p.get("w_bend", 0)) @ Rx(p.get("w_side", 0))
    J["torso"] = (ow, Rt)
    for side, sg in (("L", 1), ("R", -1)):
        oh = op + Rp @ np.array([0, sg * S["hip_x"], S["hip_z"] - S["pelvis_z"]])
        Rh = Rp @ Rz(p.get("h_twist_" + side, 0)) @ Ry(-p.get("h_flex_" + side, 0)) @ Rx(sg * p.get("h_out_" + side, 0))
        J["hip_" + side] = (oh, Rh)
        ok = oh + Rh @ np.array([0, 0, S["knee_z"] - S["hip_z"]])
        Rk = Rh @ Ry(p.get("k_" + side, 0))
        J["knee_" + side] = (ok, Rk)
        oa = ok + Rk @ np.array([0, 0, S["ankle_z"] - S["knee_z"]])
        Ra = Rk @ Ry(p.get("a_" + side, 0))
        J["ankle_" + side] = (oa, Ra)
        sh0 = np.array([S["shoulder"][0], sg * S["shoulder"][1], S["shoulder"][2] - S["waist_z"]])
        osh = ow + Rt @ sh0
        Rs = Rt @ Rz(p.get("s_in_" + side, 0) * -sg) @ Ry(-p.get("s_flex_" + side, 0)) @ Rx(sg * p.get("s_out_" + side, 0))
        J["sh_" + side] = (osh, Rs)
        oe = osh + Rs @ np.array([0, 0, -S["upper_arm"]])
        Re = Rs @ Ry(-p.get("e_" + side, 0))
        J["el_" + side] = (oe, Re)
    return J


def boxes(S, J):
    out = {}
    for name, (j, c, h) in S["parts"].items():
        o, R = J[j]
        if j == "torso":
            base = np.array(c, float)
        else:
            base = np.array(c, float)
        out[name] = (o + R @ base, R, np.array(h, float))
    return out


def corners(b):
    c, R, h = b
    pts = []
    for a in (-1, 1):
        for d in (-1, 1):
            for e in (-1, 1):
                pts.append(c + R @ (h * np.array([a, d, e])))
    return np.array(pts)


def solve(S, p, level_feet=True):
    """FK, flatten stance feet within ankle limits, put the lowest point on the ground."""
    p = dict(p)
    if level_feet:
        for side in "LR":
            if "a_" + side in p:
                continue
            J = fk(S, p)
            R = J["ankle_" + side][1]
            f = R @ np.array([1, 0, 0])
            pitch = math.degrees(math.atan2(-f[2], math.hypot(f[0], f[1])))  # + = toe down
            p["a_" + side] = float(np.clip(-pitch, *LIMITS["ankle"]["pitch"]))
    J = fk(S, p)
    B = boxes(S, J)
    low = min(corners(B[k])[:, 2].min() for k in ("foot_L", "foot_R", "shin_L", "shin_R"))
    p["pel_off"] = (0, 0, -low)
    J = fk(S, p)
    return p, J, boxes(S, J)


def collisions(S, B, margin=0.02):
    names = list(B)
    hits = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if (a, b) in IGNORE:
                continue
            if obb_hit(B[a], B[b], margin):
                hits.append(a + " x " + b)
    return hits


# ---------------------------------------------------------------- arms
def aim_arm(p, pitch=0.0):
    """right forearm is the cannon: flex + elbow - 90 = elevation relative to the chest"""
    p = dict(p)
    e = 30.0
    p["s_flex_R"] = 90 - e + pitch
    p["e_R"] = e
    p["s_in_R"] = 8
    p["s_out_R"] = 6
    p.setdefault("s_flex_L", 15)
    p.setdefault("e_L", 80)
    p.setdefault("s_out_L", 12)
    return p


# ---------------------------------------------------------------- test set
LOCO = re.compile(r"^(a_(WalkForward|combat_WalkBackward|RunForward|combat_runBackward|combat_sprint|Crouch_WalkForward|Crouch_WalkBackward|MP_CQB_idle|MP_crouch_IDLE|MP_crouch_ADS_IDLE)|at_Dodge)")


def frames():
    out = []
    for ch in ("medium", "heavy"):
        with open(os.path.join(POSE_OUT, "joint_frames_%s.csv" % ch)) as f:
            for r in csv.DictReader(f):
                if r["part"] != "mp_core" or not LOCO.match(r["anim"]) or "_rocket" in r["anim"]:
                    continue
                if int(r["frame"]) % 3:
                    continue
                g = lambda k: float(r[k])
                p = dict(pel_yaw=g("pelvis_yaw"), pel_pitch=g("pelvis_pitch"), pel_roll=g("pelvis_roll"),
                         w_yaw=g("waist_twist"), w_bend=g("waist_bend"), w_side=g("waist_side"))
                for s, k in (("L", "l"), ("R", "r")):
                    p["h_flex_" + s] = g(k + "_hip_fwd")
                    p["h_out_" + s] = g(k + "_hip_out")
                    p["h_twist_" + s] = g(k + "_hip_twist") * 0.0  # thigh twist is hidden by the box shape
                    p["k_" + s] = g(k + "_knee")
                # legs come out in pelvis frame, the body yaw of the TF2 root is folded into pelvis_yaw
                p = aim_arm(p, 0)
                out.append(("%s/%s/%s" % (ch, r["anim"], r["frame"]), p))
    return out


STAND = dict(h_flex_L=14, k_L=28, h_flex_R=14, k_R=28)
HAND = {
    "stand_aim": aim_arm(dict(STAND), 0),
    "aim_up_45": aim_arm(dict(STAND, w_bend=-20), 25),
    "aim_down_45": aim_arm(dict(STAND, w_bend=30), -15),
    "yaw_85_level": aim_arm(dict(STAND, w_yaw=85), 0),
    "yaw_-85_level": aim_arm(dict(STAND, w_yaw=-85), 0),
    "yaw_85_up": aim_arm(dict(STAND, w_yaw=85, w_bend=-20), 25),
    "yaw_85_down": aim_arm(dict(STAND, w_yaw=85, w_bend=30), -15),
    "yaw_-85_down": aim_arm(dict(STAND, w_yaw=-85, w_bend=30), -15),
    "crouch": aim_arm(dict(pel_pitch=14, w_bend=4, h_flex_L=92, k_L=115, h_flex_R=92, k_R=115), 0),
    "crouch_yaw_85": aim_arm(dict(pel_pitch=14, w_bend=4, w_yaw=85, h_flex_L=92, k_L=115, h_flex_R=92, k_R=115), 0),
    "sprint_stride": aim_arm(dict(pel_pitch=33, w_bend=8, h_flex_L=65, k_L=52, h_flex_R=-24, k_R=30), -20),
    "sprint_lean_L": aim_arm(dict(pel_pitch=28, pel_roll=-34, w_bend=8, w_side=10, h_flex_L=65, k_L=52, h_flex_R=-24, k_R=30), -20),
    "dash_float_L": aim_arm(dict(pel_pitch=10, pel_roll=-10, w_bend=4, w_side=-26, h_flex_L=31, h_out_L=8, k_L=26, h_flex_R=20, h_out_R=45, k_R=10), 0),
    "dash_land": aim_arm(dict(pel_pitch=-16, w_bend=40, h_flex_L=37, k_L=77, h_flex_R=-8, k_R=30), 0),
    "landing_one_knee": dict(pel_pitch=12, w_bend=25, h_flex_L=100, k_L=110, h_flex_R=-25, k_R=85, a_R=55, s_flex_L=35, e_L=15, s_out_L=25, s_flex_R=25, e_R=30, s_out_R=25),
    "landing_rise": dict(pel_pitch=20, w_bend=15, h_flex_L=80, k_L=100, h_flex_R=25, k_R=70, s_flex_L=20, e_L=50, s_out_L=30, s_flex_R=25, e_R=40, s_out_R=20),
    "kneel_hatch": dict(pel_pitch=5, w_bend=-5, h_flex_L=90, k_L=105, h_flex_R=-25, k_R=85, a_R=55, s_flex_L=15, e_L=30, s_out_L=12, s_flex_R=12, e_R=25, s_out_R=12),
    "melee_L": dict(STAND, w_yaw=-45, w_bend=12, s_flex_L=85, e_L=25, s_flex_R=-5, s_out_R=12, e_R=35),
    "doomed": dict(pel_roll=-6, w_bend=25, w_side=-14, w_yaw=15, h_flex_L=25, k_L=40, h_flex_R=-5, k_R=15, s_flex_R=25, e_R=15, s_out_R=18, s_flex_L=-5, e_L=20, s_out_L=20),
}


def hull_report(S, J, B):
    pts = np.vstack([corners(b) for b in B.values()])
    return dict(top=round(float(pts[:, 2].max()), 2), width=round(float(np.ptp(pts[:, 1])), 2), depth=round(float(np.ptp(pts[:, 0])), 2))


def fp_view(S, pitch=0):
    """Where the cannon sits in the first-person view at level aim (16:9, about 91 deg horizontal)."""
    p, J, B = solve(S, aim_arm(dict(STAND), pitch))
    oe, Re = J["el_R"]
    muzzle = oe + Re @ np.array([0, 0, -S["cannon_len"]])
    # eye is fixed on the player capsule, not on the body
    eye = np.array(S["eye"], float)
    # body offset removed: compare in the unlifted stand pose height of the eye plane
    out = {}
    for name, pt in (("muzzle", muzzle), ("elbow", oe)):
        d = pt - eye
        out[name] = dict(pos=[round(float(x), 2) for x in pt], yaw_right=round(math.degrees(math.atan2(-d[1], d[0])), 1), pitch=round(math.degrees(math.atan2(d[2], d[0])), 1))
    out["cannon_axis_elev"] = round(float(math.degrees(math.asin((muzzle - oe)[2] / np.linalg.norm(muzzle - oe)))), 1)
    return out


HATCH = dict(hinge=(0.95, 0, 4.15), width=1.10, length=1.35, thick=0.10, open_deg=120)


def hatch_box(S, J, deg):
    """door hangs on the torso front; deg 0 = closed (pointing up), + swings forward and down"""
    o, R = J["torso"]
    h = HATCH
    hinge = o + R @ (np.array(h["hinge"], float) - np.array([0, 0, S["waist_z"]]))
    Rd = R @ Ry(deg)
    c = hinge + Rd @ np.array([h["thick"] / 2, 0, h["length"] / 2])
    return (c, Rd, np.array([h["thick"] / 2, h["width"] / 2, h["length"] / 2]))


def hatch_check(S):
    out = {}
    for name in ("stand_aim", "kneel_hatch"):
        _, J, B = solve(S, HAND[name])
        for deg in (30, 60, 90, 120):
            hb = hatch_box(S, J, deg)
            hit = [k for k, b in B.items() if not k.startswith("torso") and obb_hit(hb, b, 0.02)]
            low = float(corners(hb)[:, 2].min())
            out["%s_%d" % (name, deg)] = dict(hits=hit, door_low=round(low, 2))
    return out


def run(S):
    tally = {}
    fails = {}
    F = frames()
    tops = []
    for name, p in F:
        _, J, B = solve(S, p)
        hits = collisions(S, B)
        tops.append(hull_report(S, J, B)["top"])
        for h in hits:
            tally[h] = tally.get(h, 0) + 1
        if hits:
            fails[name] = hits
    hand = {}
    for name, p in HAND.items():
        q, J, B = solve(S, p)
        hand[name] = dict(hits=collisions(S, B), **hull_report(S, J, B), pelvis_z=round(float(J["pelvis"][0][2]), 2))
    return dict(name=S["name"], frames=len(F), frames_fail=len(fails), fail_pct=round(100 * len(fails) / max(1, len(F)), 1), fail_sample=dict(list(fails.items())[:40]), top_p99=sorted(tops)[int(.99*len(tops))],
                pairs=dict(sorted(tally.items(), key=lambda kv: -kv[1])[:14]), top_max=max(tops), hand=hand, fp=fp_view(S), hatch=hatch_check(S))


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    rep = {}
    for S in (V2,):
        r = run(S)
        rep[S["name"]] = r
        print("==", r["name"], "frames", r["frames"], "fail", r["frames_fail"], r["fail_pct"], "%", "top_max", r["top_max"])
        print(" pairs", r["pairs"])
        for k, v in r["hand"].items():
            print("  ", k, "pel", v["pelvis_z"], "top", v["top"], "w", v["width"], "d", v["depth"], v["hits"])
        print(" fp", r["fp"])
        print(" hatch", r["hatch"])
    json.dump(rep, open(os.path.join(HERE, "out", "report.json"), "w"), indent=1)
