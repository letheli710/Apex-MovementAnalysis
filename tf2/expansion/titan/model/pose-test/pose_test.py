"""Try the poses the game needs on the mid model, without saving the .blend.
blender -b base-medium/titan_m_mid.blend -P pose-test/pose_test.py
Renders pose-test/<name>.png and writes pose-test/result.json. Signs: + X on pelvis/waist = lean forward,
hip/knee/shoulder + = back, elbow - = forward. The model is lifted so its lowest vertex is on the ground."""
import json
import math
import os

import bpy
from mathutils import Euler, Vector
from mathutils.bvhtree import BVHTree

OUT = os.path.dirname(os.path.abspath(__file__))
S = bpy.context.scene
AIM = {"J_Shoulder_R": {"X": -35}, "J_Elbow_R": {"X": -55}}
LEGS = {"J_Hip_L": {"X": -14}, "J_Knee_L": {"X": 28}, "J_Ankle_L": {"X": -14}, "J_Hip_R": {"X": -14}, "J_Knee_R": {"X": 28}, "J_Ankle_R": {"X": -14}}
ARM_L = {"J_Shoulder_L": {"X": -20}, "J_Elbow_L": {"X": -35}}


def P(*parts):
    out = {}
    for p in parts:
        for j, a in p.items():
            out.setdefault(j, {}).update(a)
    return out


POSES = {
    "01_stand_aim": P(LEGS, AIM, ARM_L),
    "02_waist35": P(LEGS, AIM, ARM_L, {"J_Waist": {"Z": 35}}),
    "03_waist55": P(LEGS, AIM, ARM_L, {"J_Waist": {"Z": 55}}),
    "04_waist85": P(LEGS, AIM, ARM_L, {"J_Waist": {"Z": 85}}),
    "05_waist-85": P(LEGS, AIM, ARM_L, {"J_Waist": {"Z": -85}}),
    "06_pelvis30_waist55": P(LEGS, AIM, ARM_L, {"J_Pelvis": {"Z": 30}, "J_Waist": {"Z": 55}, "J_Hip_L": {"Z": -30}, "J_Hip_R": {"Z": -30}}),
    "07_aim_up45": P(LEGS, ARM_L, {"J_Shoulder_R": {"X": -70}, "J_Elbow_R": {"X": -65}}),
    "08_aim_down30": P(LEGS, ARM_L, {"J_Shoulder_R": {"X": -20}, "J_Elbow_R": {"X": -40}}),
    "09_walk": P(AIM, ARM_L, {"J_Hip_L": {"X": -35}, "J_Knee_L": {"X": 15}, "J_Ankle_L": {"X": 10}, "J_Hip_R": {"X": 22}, "J_Knee_R": {"X": 25}, "J_Ankle_R": {"X": -25}, "J_Waist": {"Z": 8}}),
    "10_sprint": P(AIM, {"J_Pelvis": {"X": 15}, "J_Waist": {"X": 22}, "J_Hip_L": {"X": -60}, "J_Knee_L": {"X": 50}, "J_Ankle_L": {"X": 0}, "J_Hip_R": {"X": 20}, "J_Knee_R": {"X": 60}, "J_Ankle_R": {"X": -30}, "J_Shoulder_L": {"X": 30}, "J_Elbow_L": {"X": -60}}),
    "11_dash_left": P(AIM, ARM_L, {"J_Pelvis": {"Y": 10}, "J_Waist": {"Y": 25, "X": 12}, "J_Hip_L": {"X": -35, "Y": -25}, "J_Knee_L": {"X": 55}, "J_Ankle_L": {"X": -20}, "J_Hip_R": {"X": -10, "Y": -25}, "J_Knee_R": {"X": 25}, "J_Ankle_R": {"X": -15}}),
    "12_crouch": P(AIM, ARM_L, {"J_Pelvis": {"X": 12}, "J_Waist": {"X": 6}, "J_Hip_L": {"X": -75}, "J_Knee_L": {"X": 95}, "J_Ankle_L": {"X": -20}, "J_Hip_R": {"X": -75}, "J_Knee_R": {"X": 95}, "J_Ankle_R": {"X": -20}}),
    "13_landing": P({"J_Pelvis": {"X": 15}, "J_Waist": {"X": 25}, "J_Hip_L": {"X": -90}, "J_Knee_L": {"X": 125}, "J_Ankle_L": {"X": -25}, "J_Hip_R": {"X": -30}, "J_Knee_R": {"X": 125}, "J_Ankle_R": {"X": -30}, "J_Shoulder_L": {"X": -45}, "J_Elbow_L": {"X": -20}, "J_Shoulder_R": {"X": 15}, "J_Elbow_R": {"X": -25}}),
    "14_kneel_hatch": P({"J_Hatch": {"X": 120}, "J_Pelvis": {"X": 8}, "J_Hip_L": {"X": -85}, "J_Knee_L": {"X": 110}, "J_Ankle_L": {"X": -25}, "J_Hip_R": {"X": -40}, "J_Knee_R": {"X": 125}, "J_Ankle_R": {"X": -30}, "J_Shoulder_L": {"X": -15}, "J_Elbow_L": {"X": -30}, "J_Shoulder_R": {"X": -10}, "J_Elbow_R": {"X": -20}}),
    "15_melee": P(LEGS, {"J_Waist": {"Z": -45, "X": 12}, "J_Shoulder_L": {"X": -85}, "J_Elbow_L": {"X": -25}, "J_Shoulder_R": {"X": 20}, "J_Elbow_R": {"X": -40}}),
    "16_doomed": P({"J_Pelvis": {"Y": -6}, "J_Waist": {"X": 25, "Y": -14, "Z": 15}, "J_Hip_L": {"X": -25}, "J_Knee_L": {"X": 40}, "J_Ankle_L": {"X": -15}, "J_Hip_R": {"X": 5}, "J_Knee_R": {"X": 15}, "J_Ankle_R": {"X": -15}, "J_Shoulder_R": {"X": -5}, "J_Elbow_R": {"X": -8}, "J_Shoulder_L": {"X": 5}, "J_Elbow_L": {"X": -12}}),
}

root = bpy.data.objects["Titan_M_Base"]
joints = [o for o in bpy.data.objects if o.type == "EMPTY" and (o.name.startswith("J_") or o.name.startswith("W_"))]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]


def owner(o):
    while o and not (o.type == "EMPTY" and (o.name.startswith("J_") or o.name.startswith("W_"))):
        o = o.parent
    return o.name if o else ""


OWN = {m.name: owner(m) for m in meshes}
PARENT = {j.name: (j.parent.name if j.parent else "") for j in joints}
REST = {j.name: j.rotation_euler.copy() for j in joints}


def near(a, b):
    """same joint, or joints one or two links apart: they are meant to touch at the hub"""
    if a == b:
        return True
    pa, pb = PARENT.get(a, ""), PARENT.get(b, "")
    return a == pb or b == pa or pa == pb or PARENT.get(pa, "") == b or PARENT.get(pb, "") == a


def bvh(m):
    dg = bpy.context.evaluated_depsgraph_get()
    return BVHTree.FromObject(m, dg)


def overlaps():
    dg = bpy.context.evaluated_depsgraph_get()
    T = {}
    for m in meshes:
        ob = m.evaluated_get(dg)
        me = ob.to_mesh()
        T[m.name] = BVHTree.FromPolygons([ob.matrix_world @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
        ob.to_mesh_clear()
    hits = {}
    names = list(T)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if near(OWN[a], OWN[b]):
                continue
            if T[a].overlap(T[b]):
                k = " x ".join(sorted((OWN[a], OWN[b])))
                hits[k] = hits.get(k, 0) + 1
    return hits


def apply(pose):
    for j in joints:
        j.rotation_mode = "XYZ"
        j.rotation_euler = REST[j.name]
    for j, ax in pose.items():
        bpy.data.objects[j].rotation_euler = Euler((math.radians(ax.get("X", 0)), math.radians(ax.get("Y", 0)), math.radians(ax.get("Z", 0))), "XYZ")
    root.location.z = 0
    bpy.context.view_layer.update()
    low = min((m.matrix_world @ Vector(c)).z for m in meshes for c in m.bound_box)
    root.location.z = -low
    bpy.context.view_layer.update()
    return low


def wpos(n):
    return bpy.data.objects[n].matrix_world.translation.copy()


def setup_render():
    S.render.engine = "BLENDER_WORKBENCH"
    S.display.shading.light = "STUDIO"
    S.display.shading.color_type = "MATERIAL"
    S.display.shading.show_shadows = True
    S.render.resolution_x, S.render.resolution_y = 640, 640
    S.render.film_transparent = False
    S.world = S.world or bpy.data.worlds.new("w")
    S.world.color = (0.82, 0.82, 0.82)
    cam = bpy.data.objects.get("PoseCam")
    if cam is None:
        cam = bpy.data.objects.new("PoseCam", bpy.data.cameras.new("PoseCam"))
        S.collection.objects.link(cam)
    S.camera = cam
    return cam


def aim_cam(cam, pos, target, lens):
    cam.data.lens = lens
    cam.data.sensor_width = 36
    cam.location = pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y")
    bpy.context.view_layer.update()


cam = setup_render()
res = {}
for name, pose in POSES.items():
    low = apply(pose)
    musz = wpos("S_Muzzle")
    elb = wpos("J_Elbow_R")
    axis = (musz - elb).normalized()
    res[name] = {
        "pelvis_z": round(wpos("J_Pelvis").z, 2),
        "eye_z_body": round(wpos("S_Eye").z, 2),
        "cannon_elev_deg": round(math.degrees(math.asin(axis.z)), 1),
        "cannon_yaw_deg": round(math.degrees(math.atan2(axis.x, -axis.y)), 1),
        "muzzle": [round(v, 2) for v in musz],
        "overlaps": overlaps(),
    }
    aim_cam(cam, (6.5, -9.5, 4.0), (0, -0.2, 3.0), 55)
    S.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)

# first person: from S_Eye with the shell hidden, as a cockpit view would be
apply(POSES["01_stand_aim"])
hide = {"J_Torso", "J_Hatch", "J_Optic", "J_Waist", "J_Pelvis", "J_Launcher_L"}
for m in meshes:
    m.hide_render = OWN[m.name] in hide
eye = wpos("S_Eye")
S.render.resolution_x, S.render.resolution_y = 1280, 720
# 16:9 horizontal FOV for TF2's 75 (4:3 based) is about 91 degrees
aim_cam(cam, eye, eye + Vector((0, -10, 0)), 36 / (2 * math.tan(math.radians(91 / 2))))
S.render.filepath = os.path.join(OUT, "fp_aim.png")
bpy.ops.render.render(write_still=True)
vis = []
for n in ("J_Elbow_R", "S_Muzzle", "J_Wrist_L", "S_Hand_L"):
    p = wpos(n) - eye
    vis.append((n, round(math.degrees(math.atan2(p.x, -p.y)), 1), round(math.degrees(math.atan2(p.z, -p.y)), 1), round(p.length, 2)))
res["fp_screen_angles_yaw_pitch_dist"] = vis
for m in meshes:
    m.hide_render = False
json.dump(res, open(os.path.join(OUT, "result.json"), "w"), indent=1)
print("POSE_TEST_DONE")
