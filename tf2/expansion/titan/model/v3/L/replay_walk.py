"""Replay a Unity walk film on the real light mesh (walk plan §4): read TitanWalkFilm's joints.tsv, pose the light titan frame by frame,
check what the box model in Unity cannot: mesh clipping (build_light.collide), joints touching (build_light.joint_gaps), feet against the ground.

  blender.exe -b -P replay_walk.py -- L1 4 <film_dir>/<style>/joints.tsv [every=2] [out=<dir>]      (4 = build stage, the finished model)

Mapping (HSD-Unity TitanSkeleton.Solve vs light_rig.local_rotations, both the v2 meanings): pelvis yaw/pitch/roll, waist yaw/bend/side and the arms map 1:1;
the hip twist is signed per side in Unity (Rz(sg*twist)) and not in light_rig (Rz(h_twist)), so h_twist_R = -twist; left wrist yaw = wr_side_L. Unity does not
drive the right wrist, the fingers of the right hand or the wings: they stay as the prefab holds them (wrist 0, fingers 25 = light_rig grip, wings folded).
The left claw's grip (0 open … 1 closed) is -18 + 55 * grip deg on the three left fingers, as TitanBodyAnimator writes it.
Ground: the film's floor is flat; a point's height over it = its height in the titan's frame + the rig's offset z (offZ). The root's yaw and place do not matter here.

Writes <out>/replay.tsv (per checked frame) and <out>/replay.json (summary, the plan's §4 lines)."""
import csv
import json
import os
import sys

os.environ["LIGHT_NO_MAIN"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import build_light as B  # noqa: E402

A = sys.argv[sys.argv.index("--") + 1:]
TSV = A[2]
OPTS = dict(x.split("=", 1) for x in A[3:] if "=" in x)
EVERY = int(OPTS.get("every", 2))
OUT = OPTS.get("out", os.path.join(os.path.dirname(TSV), "replay_" + B.CODE))
os.makedirs(OUT, exist_ok=True)
FOOT = ("Foot", "Toe", "Heel_Spur", "Ankle")


def params(r):
    f = lambda k: float(r[k])
    p = dict(pel_yaw=f("pelYaw"), pel_pitch=f("pelPitch"), pel_roll=f("pelRoll"), w_yaw=f("waistYaw"), w_bend=f("waistBend"), w_side=f("waistSide"),
             h_flex_L=f("lFlex"), h_out_L=f("lOut"), h_twist_L=f("lTwist"), k_L=f("lKnee"), a_L=f("lAnkle"), a_roll_L=f("lAnkleRoll"),
             h_flex_R=f("rFlex"), h_out_R=f("rOut"), h_twist_R=-f("rTwist"), k_R=f("rKnee"), a_R=f("rAnkle"), a_roll_R=f("rAnkleRoll"),
             s_flex_L=f("aLFlex"), s_out_L=f("aLOut"), s_in_L=f("aLIn"), e_L=f("aLElbow"), wr_pitch_L=f("aLWristPitch"), wr_side_L=f("aLWristYaw"),
             s_flex_R=f("aRFlex"), s_out_R=f("aROut"), s_in_R=f("aRIn"), e_R=f("aRElbow"), hatch=f("hatch"), op_yaw=f("opticYaw"), op_pitch=f("opticPitch"),
             f1_R=25.0, f2_R=25.0, f3_R=25.0)
    g = -18.0 + 55.0 * f("aLGrip")      # TitanBodyAnimator: front fingers Ry(grip), back Ry(-grip)
    p.update(f1_L=g, f2_L=g, f3_L=g)
    off = (f("pelX"), f("pelY"), f("pelZ") + f("offZ"))
    return p, off


def main():
    objs, meshes, mats = B.build()
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    feet = {s: [n for n in meshes if any(n == k + "_" + s for k in FOOT)] for s in "LR"}
    out = ["t\tmodeL\tmodeR\tlowL\tlowR\tcontactL\tcontactR\thits\tgaps"]
    worst = dict(below=0.0, below_t=None, hits=0, gap_frames=0, planted_lift=0.0, planted_lift_t=None, swing_min=9.0, swing_min_t=None)
    hit_names = {}
    for i, r in enumerate(rows):
        if i % EVERY:
            continue
        p, off = params(r)
        B.set_pose(objs, p, off)
        low = {s: float(min(B.wverts(meshes[n])[:, 2].min() for n in feet[s])) for s in "LR"}
        hits = B.collide(meshes)
        gaps = {k: v for k, v in B.joint_gaps(meshes).items() if v > 0}
        modes = (r["modeL"], r["modeR"])
        for s, m in zip("LR", modes):
            if low[s] < worst["below"]:
                worst["below"], worst["below_t"] = low[s], r["t"]
            if m == "Planted" and low[s] > worst["planted_lift"]:
                worst["planted_lift"], worst["planted_lift_t"] = low[s], r["t"]
            if m == "Swing" and low[s] < worst["swing_min"]:
                worst["swing_min"], worst["swing_min_t"] = low[s], r["t"]
        if hits:
            worst["hits"] += 1
            for h in hits:
                hit_names[h] = hit_names.get(h, 0) + 1
        if gaps:
            worst["gap_frames"] += 1
        out.append("%s\t%s\t%s\t%.4f\t%.4f\t\t\t%s\t%s" % (r["t"], modes[0], modes[1], low["L"], low["R"], ";".join(hits), json.dumps(gaps)))
    open(os.path.join(OUT, "replay.tsv"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    summary = dict(code=B.CODE, tsv=TSV, frames=len(rows), checked=len(out) - 1, every=EVERY,
                   lowest_foot_m=round(worst["below"], 4), lowest_foot_t=worst["below_t"],
                   planted_lowest_point_highest_m=round(worst["planted_lift"], 4), planted_t=worst["planted_lift_t"],
                   swing_lowest_m=round(worst["swing_min"], 4), swing_t=worst["swing_min_t"],
                   clip_frames=worst["hits"], clip_pairs=hit_names, joint_gap_frames=worst["gap_frames"],
                   lines=dict(no_sink="lowest foot >= -0.01", planted_on_ground="planted foot's lowest point <= 0.01",
                              swing_clear="swing foot >= 0.05 mid-swing (min over all swing frames includes lift-off and touch-down)",
                              no_clip="0 frames", joints="0 frames with a gap"))
    json.dump(summary, open(os.path.join(OUT, "replay.json"), "w", encoding="utf-8"), indent=1)
    print("=== replay", json.dumps(summary)[:900])


main()
