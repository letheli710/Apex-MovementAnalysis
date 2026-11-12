"""Joint ranges without reference poses; prints joint and state tables for the report."""
import csv
import re

K = ["waist_bend", "waist_twist", "waist_side", "neck_yaw", "neck_pitch", "l_sh_fwd", "l_sh_out", "l_sh_elev", "r_sh_elev",
     "l_elbow", "r_elbow", "l_wrist_total", "r_wrist_total", "l_hip_fwd", "l_hip_out", "l_hip_twist", "l_knee", "r_knee", "l_ankle"]
LOCO = re.compile(r"(a_(Walk|combat_Walk|Run|combat_run|combat_sprint|Crouch_Walk|MP_CQB|MP_crouch_I|MP_crouch_A)|at_Dodge)")
out = []


def q(x, p):
    return x[int(p * (len(x) - 1))]


for ch in ("light", "medium", "heavy"):
    R = list(csv.DictReader(open("out/joint_frames_%s.csv" % ch)))
    R = [r for r in R if not r["anim"].lower().endswith(("ref", "ref_core", "ref_reactions", "ref_mp_scripted")) and float(r["frames"]) > 1]
    G = [r for r in R if r["part"] == "mp_core" and "rodeo" not in r["anim"].lower()]
    L = [r for r in G if LOCO.match(r["anim"]) and "_rocket" not in r["anim"]]
    for k in K:
        w = sorted(float(r[k]) for r in L)
        v = sorted(float(r[k]) for r in G)
        a = sorted(float(r[k]) for r in R)
        row = [ch, k, round(q(w, .005)), round(q(w, .995)), round(q(v, .005)), round(q(v, .995)), round(q(a, .005)), round(q(a, .995)), round(a[0]), round(a[-1])]
        out.append(row)
        print(*row)
with open("out/joint_ranges_clean.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["chassis", "key", "loco_p0.5", "loco_p99.5", "core_p0.5", "core_p99.5", "all_p0.5", "all_p99.5", "all_min", "all_max"])
    w.writerows(out)
print()
for r in csv.DictReader(open("out/state_poses.csv", encoding="utf-8-sig")):
    if r["anim"] == "-":
        print(r["chassis"][0], r["state"], "-")
        continue
    print(r["chassis"][0], r["state"], r["dur_s"], "hipZ", r["hip_z"], "bob", r["hip_bob"], "hipX", r["hip_x_mean"], "sway", r["hip_sway_y"],
          "pelP", r["pelvis_pitch"], "pelR", r["pelvis_roll"], "pelYawA", r["pelvis_yaw_amp"], "chP", r["chest_pitch"], "chPA", r["chest_pitch_amp"],
          "chR", r["chest_roll"], "chRA", r["chest_roll_amp"], "chYA", r["chest_yaw_amp"], "kn", r["knee_min"], r["knee_max"],
          "hipF", r["hip_fwd_min"], r["hip_fwd_max"], "strd", r["stride_max"], "stW", r["stance_w"], "v", r["foot_speed"])
print()
want = ("Walk_forward_MP", "Run_forward_MP", "Sprint_mp_forward", "at_MP_dodge_Start", "at_MP_dodge_float", "at_MP_dodge_land",
        "at_mount_kneel_front", "at_MP_stand2knee_straight", "at_dismount_stand", "at_MP_eject_stand_start", "at_hotdrop_01")
for r in csv.DictReader(open("out/sequences.csv", encoding="utf-8")):
    if r["seq"] in want:
        print(r["ch"], r["seq"], r["frames"], r["fps"], r["dur"], r["fadein"], r["fadeout"], r["n_events"])
