"""Unity test data for M-1 (titan_m1_spec.json), the M-1 version of v2/export_unity_spec.py. Runs inside Blender because the
socket table lives in the build script.

  blender.exe -b -P export_unity_spec_m1.py -- <output json>

Run export_unity_m1.py first (the Unity copy and its part table).
Same layout as titan_v2_spec.json (JsonUtility reads arrays only): fbx_sha256, root, nodes [{name, parent, pos (analysis axes,
metres), from_spec}], poses (v2 expected_poses, unchanged: M-1 keeps the v2 joints). Nodes: the v2 joints with J_Hatch moved
(SPEC 0.1 #21) + M-1's socket table (v2 sockets at their M-1 positions + S_Optic, S_Embark, S_Shield_L, S_Mine_L, S_Rodeo).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_m1_r7  # noqa: E402,F401  (R7: R6's joint pieces + the R7 hip axle; build_m1_r7 imports build_m1_r6 and patches build_m1_r5's model)
import build_m1_r5 as F  # noqa: E402

D = F.D
out_path = sys.argv[sys.argv.index("--") + 1]
fbx = os.path.join(HERE, "Titan_M1_unity.fbx")      # the Unity copy (export_unity_m1.py: zero pose, triangulated in Blender)
UP = json.load(open(os.path.join(HERE, "unity_parts.json"), encoding="utf-8"))
nodes = []
for n, (par, pos) in D.JOINTS.items():
    nodes.append({"name": n, "parent": par if par in D.JOINTS else F.ROOT, "pos": [float(c) for c in F.pos_of(n)], "from_spec": n in D.JA})
for n, (par, pos) in F.socket_table().items():
    nodes.append({"name": n, "parent": par, "pos": [float(c) for c in pos], "from_spec": n in D.JA})
out = {
    "source": "TF2-Research/expansion/titan/model/v3/M1 (build_m1_r6.py, socket table of build_m1_final.py), v2-design/out/spec.json for the poses",
    "fbx_sha256": hashlib.sha256(open(fbx, "rb").read()).hexdigest(),
    "root": F.ROOT,
    "nodes": nodes,
    "poses": [],
    "triangles": UP["triangles"],
    "parts": UP["parts"],      # per mesh: owner joint, Blender triangles (+ its zero-area ones), area m^2 (import test: Unity within 0.5 %)
}
for name, joints in D.SPEC["expected_poses"].items():
    out["poses"].append({"name": name,
                         "joints": [{"joint": obj, "pos": joints[key]["o"], "R": [c for row in joints[key]["R"] for c in row]} for key, obj in D.POSE_KEYS.items()]})
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("=== SPEC nodes", len(nodes), "from_spec", sum(1 for x in nodes if x["from_spec"]), "poses", len(out["poses"]), "sha", out["fbx_sha256"][:12])
