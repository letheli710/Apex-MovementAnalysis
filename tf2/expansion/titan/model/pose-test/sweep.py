"""How far the thigh can swing before it hits the torso, per body lean; where the level cannon sits in the first-person view.
blender -b base-medium/titan_m_mid.blend -P pose-test/sweep.py   (does not save the .blend)"""
import json
import math
import os

import bpy
from mathutils import Euler, Vector
from mathutils.bvhtree import BVHTree

OUT = os.path.dirname(os.path.abspath(__file__))
joints = [o for o in bpy.data.objects if o.type == "EMPTY" and (o.name.startswith("J_") or o.name.startswith("W_"))]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]


def owner(o):
    while o and not (o.type == "EMPTY" and (o.name.startswith("J_") or o.name.startswith("W_"))):
        o = o.parent
    return o.name if o else ""


OWN = {m.name: owner(m) for m in meshes}
REST = {j.name: j.rotation_euler.copy() for j in joints}


def pose(p):
    for j in joints:
        j.rotation_mode = "XYZ"
        j.rotation_euler = REST[j.name]
    for n, a in p.items():
        bpy.data.objects[n].rotation_euler = Euler([math.radians(a.get(k, 0)) for k in "XYZ"], "XYZ")
    bpy.context.view_layer.update()


def tree(names):
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for m in meshes:
        if OWN[m.name] in names:
            ob = m.evaluated_get(dg)
            me = ob.to_mesh()
            out.append((m.name, BVHTree.FromPolygons([ob.matrix_world @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])))
            ob.to_mesh_clear()
    return out


def hit():
    a = tree({"J_Hip_L", "J_Knee_L"})
    b = tree({"J_Torso", "J_Hatch"})
    for na, ta in a:
        for nb, tb in b:
            if ta.overlap(tb):
                return na + " x " + nb
    return None


res = {"first_hit_hip_forward": {}}
for lean in (0, 10, 20, 30, 40):
    first = None
    for h in range(10, 121, 5):
        pose({"J_Waist": {"X": lean}, "J_Hip_L": {"X": -h}, "J_Knee_L": {"X": min(130, h)}})
        w = hit()
        if w:
            first = (h, w)
            break
    res["first_hit_hip_forward"]["lean_%d" % lean] = first

eye0 = bpy.data.objects["S_Eye"].matrix_world.translation.copy()
pose({"J_Shoulder_R": {"X": -30}, "J_Elbow_R": {"X": -31}})
m = bpy.data.objects["S_Muzzle"].matrix_world.translation.copy()
e = bpy.data.objects["J_Elbow_R"].matrix_world.translation.copy()
ax = (m - e).normalized()
res["level_aim"] = {"cannon_elev": round(math.degrees(math.asin(ax.z)), 1), "muzzle": [round(v, 2) for v in m], "elbow": [round(v, 2) for v in e], "eye": [round(v, 2) for v in eye0]}
for n, p in (("muzzle", m), ("elbow", e)):
    d = p - eye0
    res["level_aim"][n + "_yaw_pitch_deg_from_eye"] = (round(math.degrees(math.atan2(-d.x, -d.y)), 1), round(math.degrees(math.atan2(d.z, -d.y)), 1))
# parallax: where the muzzle line crosses the view line
res["level_aim"]["muzzle_side_offset_m"] = round(abs(m.x - eye0.x), 2)
json.dump(res, open(os.path.join(OUT, "sweep.json"), "w"), indent=1)
print(json.dumps(res))
print("SWEEP_DONE")
