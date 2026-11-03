"""Prints the failures in manifest.json. py -3 show_checks.py"""
import json
import os
from collections import Counter

m = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json"), encoding="utf-8"))
c = m["checks"]
for k in ("tris", "hierarchy", "rest_joints", "heights", "shape_rules", "first_person", "fbx_roundtrip"):
    if k in c:
        print(k, c[k])
print({k: v for k, v in c["pose_joints"].items() if k != "per_pose"})
print("POSES failed:")
for k, v in c["collision_poses"]["failed"].items():
    print("  ", k, [(r["pair"], r["depth"]) for r in v])
print("HATCH required failed:", [(r["pose"], r["door_deg"], r["pair"], r["depth"]) for r in c["collision_hatch"]["failed"]])
print("hatch other:", Counter((r["pose"], r["pair"]) for r in c["collision_hatch"]["other_poses_info"]).most_common(30))
for b in ("failed_rest", "failed_stand_aim", "failed_arms_clear"):
    print(b, len(c["collision_limits"][b]), "limits:", sorted({r["limit"] for r in c["collision_limits"][b]}))
for b, rows in c["collision_limits"]["reachable_without_collision"].items():
    print("reach from", b)
    for k, v in rows.items():
        print("  ", k, v)
if c["collision_limits"]["failed_arms_clear"]:
    for r in c["collision_limits"]["failed_arms_clear"]:
        print("  clear:", r["limit"], r["value"], r["pair"], r["depth"])
print("lowest", min(m["pose_lowest_mesh_z"].values()), "seconds", m.get("check_seconds"))
