"""Turn joint_frames_*.csv into per-state and per-joint tables (Markdown fragments and CSV)."""
import csv
import math
import os
import re
from collections import defaultdict

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
CH = ["light", "medium", "heavy"]

# state name -> regex on anim name, core parts only
STATES = [
    ("站立待机", r"^a_MP_CQB_idle$"),
    ("站立瞄准待机", r"^a_MP_CQB_ADS_idle$"),
    ("蹲待机", r"^a_MP_crouch_IDLE$"),
    ("走·前", r"^a_WalkForward$"),
    ("走·前偏右", r"^a_WalkForward_R$"),
    ("走·前偏左", r"^a_WalkForward_L$"),
    ("走·后", r"^a_combat_WalkBackward$"),
    ("跑·前", r"^a_RunForward$"),
    ("跑·后", r"^a_combat_runBackward$"),
    ("冲刺跑", r"^a_combat_sprint$"),
    ("冲刺跑·左倾", r"^a_combat_sprint_Lean_L$"),
    ("冲刺跑·右倾", r"^a_combat_sprint_Lean_R$"),
    ("蹲走·前", r"^a_Crouch_WalkForward$"),
    ("蹲走·后", r"^a_Crouch_WalkBackward$"),
    ("dash 起·前", r"^at_Dodge_Start$"),
    ("dash 飘·前", r"^at_Dodge_Float$"),
    ("dash 落·前", r"^at_Dodge_Land$"),
    ("dash 起·左", r"^at_Dodge_Start_L$"),
    ("dash 飘·左", r"^at_Dodge_Float_L$"),
    ("dash 落·左", r"^at_Dodge_Land_L$"),
    ("dash 起·右", r"^at_Dodge_Start_R$"),
    ("dash 飘·右", r"^at_Dodge_Float_R$"),
    ("dash 落·右", r"^at_Dodge_Land_R$"),
    ("dash 起·后", r"^at_DodgeBackward_Start$"),
    ("dash 飘·后", r"^at_DodgeBackward_Float$"),
    ("dash 落·后", r"^at_DodgeBackward_Land$"),
    ("跳跃落地", r"^a_MP_Jump_end$"),
    ("濒死待机", r"^.*doomed_idle.*$"),
    ("濒死蹲", r"^.*doomed_crouch_idle.*$"),
    ("濒死走·前", r"^.*doomed_walk_F.*$"),
    ("濒死走·后", r"^.*doomed_walk_B.*$"),
    ("濒死·横移", r"^.*doomed_strafe_R.*$"),
    ("被骑待机", r"^a_MP_CQB_idle_Rodeo$"),
    ("近战拳", r"^.*player_melee_punch_01.*$"),
    ("冲刺近战", r"^.*player_dash_melee_punch_01.*$"),
]


def load(ch):
    with open(os.path.join(OUT, "joint_frames_%s.csv" % ch), newline="") as f:
        r = csv.reader(f)
        head = next(r)
        rows = []
        for row in r:
            d = dict(zip(head, row))
            for k in head[2:]:
                d[k] = float(d[k])
            rows.append(d)
    return head, rows


def rng(rows, k):
    v = [r[k] for r in rows]
    return min(v), max(v), sum(v) / len(v)


JOINTS = [
    ("腰·前弯(+)/后仰", "waist_bend"),
    ("腰·扭转", "waist_twist"),
    ("腰·侧弯", "waist_side"),
    ("脖子·左右", "neck_yaw"),
    ("脖子·俯仰", "neck_pitch"),
    ("脖子·滚转", "neck_roll"),
    ("肩·前摆(+)/后摆(左)", "l_sh_fwd"),
    ("肩·外展(左)", "l_sh_out"),
    ("肩·抬起角(左,0垂下)", "l_sh_elev"),
    ("肩·前摆(+)/后摆(右)", "r_sh_fwd"),
    ("肩·外展(右)", "r_sh_out"),
    ("肩·抬起角(右,0垂下)", "r_sh_elev"),
    ("肘·弯曲(左,0伸直)", "l_elbow"),
    ("肘·弯曲(右,0伸直)", "r_elbow"),
    ("腕·合转角(左)", "l_wrist_total"),
    ("腕·合转角(右)", "r_wrist_total"),
    ("髋·前摆(+)/后摆(左)", "l_hip_fwd"),
    ("髋·外展(左)", "l_hip_out"),
    ("髋·扭转(左)", "l_hip_twist"),
    ("膝·弯曲(左,0伸直)", "l_knee"),
    ("膝·弯曲(右,0伸直)", "r_knee"),
    ("踝·小腿与脚夹角(左)", "l_ankle"),
    ("脚·前掌下压(+)(左)", "l_foot_pitch"),
]


def pct(sorted_v, q):
    return sorted_v[min(len(sorted_v) - 1, int(q * len(sorted_v)))]


def joint_table(ch, rows):
    groups = {
        "core": [r for r in rows if r["part"] == "mp_core"],
        "all": rows,
    }
    out = []
    for label, k in JOINTS:
        row = [ch, label, k]
        for g in ("core", "all"):
            vs = sorted(r[k] for r in groups[g])
            mn = min(groups[g], key=lambda r: r[k])
            mx = max(groups[g], key=lambda r: r[k])
            row += [round(vs[0], 1), round(pct(vs, 0.01), 1), round(pct(vs, 0.99), 1), round(vs[-1], 1), mn["anim"], mx["anim"]]
        out.append(row)
    return out


def gait(rows, frames_fps):
    """natural speed from stance foot: median of strongest backward foot speed while foot is low."""
    fr = sorted(rows, key=lambda r: r["frame"])
    fps = fr[0]["fps"]
    n = len(fr)
    speeds = []
    for side in "lr":
        for a, b in zip(fr, fr[1:]):
            if a[side + "_ball_z"] < 18 and b[side + "_ball_z"] < 18:
                dx = b[side + "_ball_x"] - a[side + "_ball_x"]
                dy = b[side + "_ball_y"] - a[side + "_ball_y"]
                speeds.append(math.hypot(dx, dy) * fps)
    speeds.sort()
    nat = speeds[len(speeds) // 2] if speeds else 0
    return nat, n / fps


def state_table(ch, rows):
    by = defaultdict(list)
    for r in rows:
        if r["part"] != "sp_core":
            by[r["anim"]].append(r)
    out = []
    for name, rx in STATES:
        hits = [a for a in by if re.match(rx, a) and "_rocket" not in a]
        if not hits:
            out.append([ch, name, "-"] + [""] * 20)
            continue
        # prefer shortest name
        a = sorted(hits, key=len)[0]
        R = by[a]
        z = rng(R, "hip_z")
        cp = rng(R, "chest_pitch")
        cr = rng(R, "chest_roll")
        cy = rng(R, "chest_yaw")
        pp = rng(R, "pelvis_pitch")
        pr = rng(R, "pelvis_roll")
        py = rng(R, "pelvis_yaw")
        hp = rng(R, "head_pitch")
        hipy = rng(R, "hip_y")
        hipx = rng(R, "hip_x")
        kn = rng(R, "l_knee")
        hf = rng(R, "l_hip_fwd")
        sf = rng(R, "l_sh_fwd")
        st = rng(R, "stride_x")
        sw = rng(R, "stance_w")
        nat, dur = gait(R, None)
        out.append(
            [ch, name, a, len(R), round(dur, 2), round(z[2], 1), round(z[1] - z[0], 1), round(hipx[2], 1), round(hipy[1] - hipy[0], 1),
             round(pp[2], 1), round(pr[2], 1), round(pr[1] - pr[0], 1), round(py[1] - py[0], 1),
             round(cp[2], 1), round(cp[1] - cp[0], 1), round(cr[2], 1), round(cr[1] - cr[0], 1), round(cy[2], 1), round(cy[1] - cy[0], 1),
             round(hp[2], 1), round(kn[0], 1), round(kn[1], 1), round(hf[0], 1), round(hf[1], 1), round(sf[0], 1), round(sf[1], 1), round(st[1], 1), round(sw[2], 1), round(nat, 0),
             round(rng(R, "cam_z")[2], 1), round(rng(R, "cam_z")[1] - rng(R, "cam_z")[0], 2)]
        )
    return out


def main():
    jt, st = [], []
    for ch in CH:
        head, rows = load(ch)
        jt += joint_table(ch, rows)
        st += state_table(ch, rows)
        # bones that move the camera: which anims move jx_c_camera / pov
        by = defaultdict(list)
        for r in rows:
            by[(r["part"], r["anim"])].append(r)
        cam = []
        for (p, a), R in by.items():
            c = [max(r[x] for r in R) - min(r[x] for r in R) for x in ("pov_x", "pov_y", "pov_z", "cam_x", "cam_y", "cam_z")]
            mv = max(c)
            if mv > 0.5:
                cam.append((ch, p, a, R[0]["frames"], R[0]["fps"], round(mv, 1), [round(x, 1) for x in c]))
        with open(os.path.join(OUT, "camera_bone_motion_%s.csv" % ch), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ch", "part", "anim", "frames", "fps", "max_travel", "travel_pov_cam_xyz"])
            w.writerows(sorted(cam, key=lambda x: -x[5]))
        print(ch, "anims with camera bone motion:", len(cam), "of", len(by))
    with open(os.path.join(OUT, "joint_ranges.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["chassis", "joint", "key", "core_min", "core_p1", "core_p99", "core_max", "core_min_anim", "core_max_anim", "all_min", "all_p1", "all_p99", "all_max", "all_min_anim", "all_max_anim"])
        w.writerows(jt)
    with open(os.path.join(OUT, "state_poses.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["chassis", "state", "anim", "frames", "dur_s", "hip_z", "hip_bob", "hip_x_mean", "hip_sway_y", "pelvis_pitch", "pelvis_roll", "pelvis_roll_amp", "pelvis_yaw_amp", "chest_pitch", "chest_pitch_amp", "chest_roll", "chest_roll_amp", "chest_yaw", "chest_yaw_amp", "head_pitch", "knee_min", "knee_max", "hip_fwd_min", "hip_fwd_max", "sh_fwd_min", "sh_fwd_max", "stride_max", "stance_w", "foot_speed", "cam_z", "cam_z_amp"])
        w.writerows(st)
    for row in jt:
        if row[0] == "medium":
            print(row[1], "core", row[3:7], row[7], row[8], "all", row[9:13], row[13], row[14])
    print()
    for row in st:
        if row[0] == "medium":
            print(row[1:])


if __name__ == "__main__":
    main()
