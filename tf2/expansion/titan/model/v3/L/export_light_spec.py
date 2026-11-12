"""Writes the light rig (nodes, parents, rest positions, limits, poses) per titan as JSON for the Unity side, like v2/export_unity_spec.py.
Analysis axes (x forward, y left, z up, metres). No bpy.   py -3 export_light_spec.py"""
import hashlib
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import light_rig as R

for code, mod in (("L1", "l1_parts"), ("L2", "l2_parts")):
    M = importlib.import_module(mod)
    parts, xj, socks, weapon = M.build()
    root = "Titan_" + code
    nodes = R.core_joints(root)
    nodes.update(xj)
    nodes.update(socks)
    fbx = os.path.join(HERE, "Titan_%s.fbx" % code)
    out = dict(source="v3/L/light_rig.py + %s.py" % mod, root=root, fbx_sha256=hashlib.sha256(open(fbx, "rb").read()).hexdigest() if os.path.exists(fbx) else None,
               lean_deg=M.LEAN, lean_pivot=[float(x) for x in R.LEAN_PIVOT], weapon=weapon,
               nodes=[dict(name=n, parent=p, pos=[round(float(c), 5) for c in pos]) for n, (p, pos) in nodes.items()],
               limits=[dict(label=a, key=b, lo=c, hi=d) for a, b, c, d in R.LIMITS + R.LIMITS_SIDED],
               wing_axis_L=[round(float(c), 6) for c in R.wing_axis("L")], wing_axis_R=[round(float(c), 6) for c in R.wing_axis("R")],
               poses={k: {kk: float(vv) for kk, vv in v.items()} for k, v in R.poses().items()},
               parts=[dict(object="%s_%s" % (code, p["name"]), joint=p["joint"], slot=p["slot"]) for p in parts])
    json.dump(out, open(os.path.join(HERE, code, "rig_%s.json" % code), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(code, len(out["nodes"]), "nodes", len(out["parts"]), "parts")
