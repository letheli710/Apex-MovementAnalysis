"""Terrain route numbers per feature (C1, 2026-11-13), from a TitanWalkFilm -route terrain folder (body/joints/boxes/terrain.tsv) and, when
given, the Blender replay's replay.tsv (walk_replay_blend.py with HSD_REPLAY_TERRAIN).

  py -3 terrain_stats.py <film style dir> [replay dir] [--json]

Per feature (drop, ramp 5..30, each stair set; split into the walk out and the sprint back by the titan's facing):
  box  (part boxes over the ground, any chassis):  planted foot lowest / highest, swinging foot lowest, shin lowest
  mesh (the replay, every 5th frame):              the same from the real mesh, plus contact frames
  slide: metres a planted foot's bearing point moved, per 100 m walked on that feature (body.tsv slideL/R, rootX/Y)."""
import csv
import json
import math
import os
import sys

d = sys.argv[1]
rp = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
U = 0.0254


def tsv(p):
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


marks = {}
for line in open(os.path.join(d, "terrain.tsv"), encoding="utf-8"):
    f = line.split()
    if f and f[0] == "mark":
        marks[f[1]] = float(f[2])
edges = sorted((v, k) for k, v in marks.items() if not k.endswith("_mid"))
first = edges[0][0]


def feature(x):
    if x < first:
        return "drop"
    name = "flat"
    for v, k in edges:
        if x >= v:
            name = k
    return name


body, joints, boxes = tsv(os.path.join(d, "body.tsv")), tsv(os.path.join(d, "joints.tsv")), tsv(os.path.join(d, "boxes.tsv"))
rows = {}


def cell(feat, pas):
    return rows.setdefault((feat, pas), dict(frames=0, planted_low=9.0, planted_high=-9.0, swing_low=9.0, shin_low=9.0, slide=0.0, dist=0.0,
                                              m_frames=0, m_planted_low=9.0, m_planted_high=-9.0, m_swing_low=9.0, m_shin_low=9.0, m_contacts=0))


prev = None
for b, j, x in zip(body, joints, boxes):
    rx, ry = float(j["rootX"]), float(j["rootY"])
    yaw = float(j["rootYaw"])
    pas = "back" if abs(((yaw + 180) % 360) - 180) > 90 else "out"
    c = cell(feature(rx), pas)
    c["frames"] += 1
    for s in "LR":
        m = x["mode" + s]
        fz, sh = float(x["foot" + s]), float(x["shin" + s])
        if m == "Planted":
            c["planted_low"] = min(c["planted_low"], fz)
            c["planted_high"] = max(c["planted_high"], fz)
        elif m == "Swing":
            c["swing_low"] = min(c["swing_low"], fz)
        c["shin_low"] = min(c["shin_low"], sh)
    c["slide"] += float(b["slideL"]) + float(b["slideR"])
    if prev:
        c["dist"] += math.hypot(rx - prev[0], ry - prev[1])
    prev = (rx, ry)

if rp:
    jt = {r["t"]: r for r in joints}
    for r in tsv(os.path.join(rp, "replay.tsv")):
        j = jt.get(r["t"])
        if not j:
            continue
        yaw = float(j["rootYaw"])
        c = cell(feature(float(j["rootX"])), "back" if abs(((yaw + 180) % 360) - 180) > 90 else "out")
        c["m_frames"] += 1
        for s in "LR":
            m, lo, sh = r["mode" + s], float(r["low" + s]), float(r["shin" + s])
            if m == "Planted":
                c["m_planted_low"] = min(c["m_planted_low"], lo)
                c["m_planted_high"] = max(c["m_planted_high"], lo)
            elif m == "Swing":
                c["m_swing_low"] = min(c["m_swing_low"], lo)
            c["m_shin_low"] = min(c["m_shin_low"], sh)
        c["m_contacts"] += bool(r["collisions"])

order = ["drop"] + [k for _, k in edges] + ["flat"]
out = []
for pas in ("out", "back"):
    for f in order:
        c = rows.get((f, pas))
        if not c or c["frames"] == 0:
            continue
        c["slide_per_100m"] = c["slide"] / c["dist"] * 100 if c["dist"] > 1 else 0.0
        out.append(dict(feature=f, part="walk" if pas == "out" else "sprint", **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()}))

if "--json" in sys.argv:
    print(json.dumps(out))
else:
    hdr = "part\tfeature\tframes\tslide/100m\tbox:planted lo\thi\tswing lo\tshin lo" + ("\tmesh:planted lo\thi\tswing lo\tshin lo\tcontacts" if rp else "")
    print(hdr)
    for r in out:
        line = "%s\t%s\t%d\t%.2f\t%.3f\t%.3f\t%.3f\t%.3f" % (r["part"], r["feature"], r["frames"], r["slide_per_100m"], r["planted_low"], r["planted_high"], r["swing_low"], r["shin_low"])
        if rp:
            line += "\t%.3f\t%.3f\t%.3f\t%.3f\t%d" % (r["m_planted_low"], r["m_planted_high"], r["m_swing_low"], r["m_shin_low"], r["m_contacts"])
        print(line)
