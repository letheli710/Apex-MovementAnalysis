#!/usr/bin/env python3
"""R5 aimed pose against what the Unity code gives, per gun. Unity numbers are worked out from HeldModels.cs and HoldPose.cs (read-only), not run.

  py -3 an_unity.py <run dir> <D-VIEWMODEL.tsv> <HeldModels.cs> <IS-STATIC.tsv> <out.tsv>

Unity, aimed: anchor = (0, AimAnchor.y * thick, hip.z), muzzle = anchor + Scale(model.muzzle, size).
  so U = thick * (AimAnchor.y + 0.15 * height * ModelScale) / MetresPerUnit, F = the hip F, R = 0. One number per class, not per gun.
R5 view model picture: px per tangent = 800 / (tan(fov / 2) * 4 / 3), fov = 70 at the hip, zoom_fov aimed (vmcal2.py). Unity's gun camera: 65.5 degrees vertical, fixed, 700 px per tangent.
"""
import csv
import json
import math
import os
import re
import sys

run, dv, cs, st, out = sys.argv[1:6]
SHAPE = {"Smg": 0.04, "Shotgun": 0.05, "Sniper": 0.035, "Lmg": 0.06, "Pistol": 0.035, "Rifle": 0.042}
THICK = {"Pistol": 1.15, "Sniper": 1.7, "Lmg": 1.35, "Shotgun": 1.35, "Smg": 1.3, "Rifle": 1.3}
txt = open(cs, encoding="utf-8").read()
cls = dict(re.findall(r'\["(mp_[a-z0-9_]+)"\]\s*=\s*GunClass\.(\w+)', txt))
dvm = {}
for r in csv.DictReader(open(dv, encoding="utf-8"), delimiter="\t"):
    if r["mode"] == "ads":
        dvm[r["gun"]] = float(r["muzzleU"])
static = {r["gun"]: r for r in csv.DictReader(open(st, encoding="utf-8"), delimiter="\t")}


def fx(fov):
    return 800 / (math.tan(math.radians(fov) / 2) * 4 / 3)


rows = []
for g in sorted(os.listdir(run)):
    p = os.path.join(run, g, "meta.json")
    if not os.path.exists(p):
        continue
    m = json.load(open(p, encoding="utf-8"))
    n = m["attach_names"].get("muzzle_flash", -1)
    ads, hip = (m.get("ads") or {}).get(str(n)), (m.get("hip") or {}).get(str(n))
    if not ads:
        continue
    c = cls.get(m["id"], "Rifle")
    uU = THICK[c] * (-0.032 + 0.15 * SHAPE[c] * 0.55) / 0.0095
    zf = float(static[g]["zoom_fov"]) if static[g]["zoom_fov"] else 70.0
    fA = fx(zf)
    r = dict(gun=g, cls=c, r5_F=ads["p"][0], r5_R=ads["p"][1], r5_U=ads["p"][2], r5_pitch=ads["g"][0], dviewmodel_U=dvm.get(g, ""), unity_U=round(uU, 2), unity_F=hip["p"][0] if hip else "",
             dU=round(uU - ads["p"][2], 2), dF=round(hip["p"][0] - ads["p"][0], 2) if hip else "", zoom_fov=zf, r5_ads_fpx=round(fA), r5_ads_vfov=round(2 * math.degrees(math.atan(450 / fA)), 1),
             size_ratio_ads=round(fA / 700, 2))
    rows.append(r)
keys = list(rows[0])
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(keys) + "\n")
    for r in rows:
        f.write("\t".join(str(r[k]) for k in keys) + "\n")
print(len(rows))
