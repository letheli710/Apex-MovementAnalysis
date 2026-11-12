"""Light terrain replay (terrain tuning, 2026-11-13): replay_walk.py's light posing, placed on the C1 course the way Unity places the rig, every vertex measured
against the course's ground under it. Output columns match model/v3/H/walk_replay_blend.py, so model/v3/H/terrain_stats.py and score scripts read it.

  blender.exe -b -P replay_terrain.py -- L1 4 <film>/<style>/joints.tsv [every=5] [out=<dir>]        (terrain.tsv next to joints.tsv)

- Root: (rootX + offX, rootY + offY, rootZ + offZ), yaw then pitch about the titan's side axis (TitanBodyAnimator; walk_replay_blend.py does the same).
- Ground: terrain.tsv's profile z(x), the higher side at a vertical step (walk_replay_blend.ground_under), 0 off the course.
- lowL / lowR: lowest point of that foot's sole parts (Foot, Toe, Heel_Spur, Ankle) over the ground; shinL / shinR: the shin parts (Shin, Shin_Plate,
  Calf_Blade, Knee_Guard, Calf_Mount, Ankle_Piston) over the ground; collisions: build_light.collide (the light's own touching rules).
- Light posing: replay_walk.params (h_twist_R = -twist, right wrist 0, right fingers 25, left claw -18 + 55 * grip).
- The joints.tsv chassis column must be 'light' on every row (a fallback to the medium sizes would make the numbers void); the script stops otherwise."""
import csv
import json
import math
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
EVERY = int(OPTS.get("every", 5))
OUT = OPTS.get("out", os.path.join(os.path.dirname(TSV), "replay_terrain_" + B.CODE))
os.makedirs(OUT, exist_ok=True)
FOOT = ("Foot", "Toe", "Heel_Spur", "Ankle")
SHIN = ("Shin", "Shin_Plate", "Calf_Blade", "Knee_Guard", "Calf_Mount", "Ankle_Piston")


def load_terrain(path):
    pts = []
    for line in open(path, encoding="utf-8"):
        f = line.split()
        if not f or f[0].startswith("#") or f[0] in ("lane", "mark"):
            continue
        pts.append((float(f[0]), float(f[1])))
    xs, zs = [], []
    for i, (x, z) in enumerate(pts):
        if i + 1 < len(pts) and pts[i + 1][0] == x and pts[i + 1][1] > z:
            x -= 1e-4
        elif i > 0 and pts[i - 1][0] == x and pts[i - 1][1] > z:
            x += 1e-4
        xs.append(x); zs.append(z)
    return np.array(xs), np.array(zs)


def params(r):
    f = lambda k: float(r[k])
    p = dict(pel_yaw=f("pelYaw"), pel_pitch=f("pelPitch"), pel_roll=f("pelRoll"), w_yaw=f("waistYaw"), w_bend=f("waistBend"), w_side=f("waistSide"),
             h_flex_L=f("lFlex"), h_out_L=f("lOut"), h_twist_L=f("lTwist"), k_L=f("lKnee"), a_L=f("lAnkle"), a_roll_L=f("lAnkleRoll"),
             h_flex_R=f("rFlex"), h_out_R=f("rOut"), h_twist_R=-f("rTwist"), k_R=f("rKnee"), a_R=f("rAnkle"), a_roll_R=f("rAnkleRoll"),
             s_flex_L=f("aLFlex"), s_out_L=f("aLOut"), s_in_L=f("aLIn"), e_L=f("aLElbow"), wr_pitch_L=f("aLWristPitch"), wr_side_L=f("aLWristYaw"),
             s_flex_R=f("aRFlex"), s_out_R=f("aROut"), s_in_R=f("aRIn"), e_R=f("aRElbow"), hatch=f("hatch"), op_yaw=f("opticYaw"), op_pitch=f("opticPitch"),
             f1_R=25.0, f2_R=25.0, f3_R=25.0)
    g = -18.0 + 55.0 * f("aLGrip")
    p.update(f1_L=g, f2_L=g, f3_L=g)
    return p


def main():
    TX, TZ = load_terrain(os.path.join(os.path.dirname(TSV), "terrain.tsv"))
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    bad = sorted({r["chassis"] for r in rows} - {"light"})
    if bad:
        raise SystemExit("joints.tsv chassis column is %s, not light: the film fell back to other sizes" % bad)
    objs, meshes, mats = B.build()
    root = objs[B.ROOT]
    root.rotation_mode = "XYZ"
    feet = {s: [n for n in meshes if any(n == k + "_" + s for k in FOOT)] for s in "LR"}
    shins = {s: [n for n in meshes if any(n == k + "_" + s for k in SHIN)] for s in "LR"}

    def rel(ob):
        v = B.wverts(ob)
        return float((v[:, 2] - np.interp(-v[:, 1], TX, TZ, left=0.0, right=0.0)).min())

    out = ["t\tmodeL\tmodeR\tlowL\tlowR\tshinL\tshinR\tcollisions\tbodyLow\tbodyPart\tpartL\tpartR"]
    worst = dict(model=B.CODE, planted_low=0.0, planted_high=0.0, swing_min=9.0, frames=0, frames_with_collision=0, pairs={},
                 planted_frames_under_2cm=0, planted_frames_over_3cm=0, swing_frames_under_5cm=0, body_low=9.0)
    for i, r in enumerate(rows):
        if i % EVERY:
            continue
        f = lambda k: float(r[k])
        root.location = (f("rootY") + f("offY"), -(f("rootX") + f("offX")), f("rootZ") + f("offZ"))
        root.rotation_euler = (math.radians(f("rootPitch")), 0.0, math.radians(f("rootYaw")))
        B.set_pose(objs, params(r), (f("pelX"), f("pelY"), f("pelZ")))
        fl = {s: {n: rel(meshes[n]) for n in feet[s]} for s in "LR"}
        low = {s: min(fl[s].values()) for s in "LR"}
        lowpart = {s: min(fl[s], key=fl[s].get) for s in "LR"}
        sh = {s: min(rel(meshes[n]) for n in shins[s]) for s in "LR"}
        hits = B.collide(meshes)
        bl = {n: rel(o) for n, o in meshes.items()}
        bpart = min(bl, key=bl.get)
        if bl[bpart] < worst["body_low"]:
            worst["body_low"], worst["body_low_part"], worst["body_low_t"] = bl[bpart], bpart, r["t"]
        for s in "LR":
            m, lo = r["mode" + s], low[s]
            if m == "Planted":
                worst["planted_low"] = min(worst["planted_low"], lo)
                worst["planted_high"] = max(worst["planted_high"], lo)
                worst["planted_frames_under_2cm"] += lo < -0.02
                worst["planted_frames_over_3cm"] += lo > 0.03
            elif m == "Swing":
                worst["swing_min"] = min(worst["swing_min"], lo)
                worst["swing_frames_under_5cm"] += lo < 0.05
        worst["frames"] += 1
        if hits:
            worst["frames_with_collision"] += 1
            for h in hits:
                worst["pairs"][h] = worst["pairs"].get(h, 0) + 1
        out.append("\t".join([r["t"], r["modeL"], r["modeR"], "%.4f" % low["L"], "%.4f" % low["R"], "%.4f" % sh["L"], "%.4f" % sh["R"],
                              ";".join(hits), "%.4f" % bl[bpart], bpart, lowpart["L"], lowpart["R"]]))
    open(os.path.join(OUT, "replay.tsv"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    json.dump(worst, open(os.path.join(OUT, "replay_summary.json"), "w", encoding="utf-8"), indent=1, default=float)
    print("=== REPLAY", json.dumps(worst, default=float)[:900])


main()
