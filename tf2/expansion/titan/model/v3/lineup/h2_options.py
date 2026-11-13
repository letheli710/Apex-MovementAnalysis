"""R6: mock-ups of H-2 upper-body changes to tell it from H-1 at 1/4. Only edits the imported copy in memory; H/ files untouched.

  blender.exe -b -P h2_options.py -- [out_dir]      (default lineup/r6/h2_options)

Options (all keep the static top <= 5.97):
  A  cannon x1.45 thicker (barrels, body, belt end) and x1.25 longer, measured from W_Cannon (rest: muzzle ~0.4 m into the floor)
  A2 cannon x1.45 thicker only, same length
  B  left shield pushed 0.45 m outward and widened: a vertical plate 0.18 thick, 1.6 deep, from z 4.30 to 5.95 outside the left shoulder
  C  A + B
  D  A2 + B (thicker cannon, same length, shield out): nothing goes into the floor
Each: H-1 and the H-2 variant side by side, black, rest pose (lineup default) front + 3/4 and stand_aim 3/4, full + 1/4,
and the share of black pixels the two do not have in common (lineup_pose.compare), against H-1.
"""
import json
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lineup_pose as LP  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = args[0] if args else os.path.join(HERE, "r6", "h2_options")
DX = 3.6


def camera(loc, target, ortho):
    cam = bpy.data.objects.get("Cam") or bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    if cam.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam)
    cam.data.type, cam.data.ortho_scale, cam.data.clip_end = "ORTHO", ortho, 300
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


def render(path, res):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def imp(code, x):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(V3, "H", "Titan_%s.fbx" % code), axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.parent is None:
            o.location.x += x
    bpy.context.view_layer.update()
    return new


def thicker_cannon(objs, radial=1.45, length=1.25):
    N = LP.by_name(objs)
    for n in ("H2_Cannon", "H2_Barrels", "H2_Belt_Cannon"):
        o = N.get(n)
        if o is None:
            continue
        # vertices in the owning joint's frame; barrel runs along local -Z (Blender) at rest. Scale about the cannon's own centre line.
        jw = N["W_Cannon"].matrix_world
        M = jw.inverted() @ o.matrix_world
        vs = [M @ v.co for v in o.data.vertices]
        cx = float(np.mean([v.x for v in vs])); cy = float(np.mean([v.y for v in vs]))
        for v, p in zip(o.data.vertices, vs):
            q = Vector((cx + (p.x - cx) * radial, cy + (p.y - cy) * radial, p.z * length))
            v.co = M.inverted() @ q
        o.data.update()


def shield_plate(objs):
    """A vertical plate outside the left shoulder, parented to J_Torso so it follows the waist like the shoulder block."""
    N = LP.by_name(objs)
    sh = N["H2_Shoulder_L"]
    w = [sh.matrix_world @ v.co for v in sh.data.vertices]
    out_x = max(p.x for p in w)          # Blender +X = titan left
    yc = float(np.mean([p.y for p in w]))
    x0, x1 = out_x + 0.45 - 0.18, out_x + 0.45
    y0, y1 = yc - 0.8, yc + 0.8
    z0, z1 = 4.30, 5.95
    md = bpy.data.meshes.new("H2_ShieldMock")
    vv = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    md.from_pydata(vv, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ob = bpy.data.objects.new("H2_ShieldMock", md)
    md.materials.append(sh.data.materials[0])
    bpy.context.scene.collection.objects.link(ob)
    # bridge from the shoulder to the plate (otherwise it floats)
    md2 = bpy.data.meshes.new("H2_ShieldArm")
    bx0, bx1 = out_x - 0.05, x0 + 0.01
    vv = [(x, y, z) for z in (5.20, 5.55) for y in (yc - 0.25, yc + 0.25) for x in (bx0, bx1)]
    md2.from_pydata(vv, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ob2 = bpy.data.objects.new("H2_ShieldArm", md2)
    md2.materials.append(sh.data.materials[0])
    bpy.context.scene.collection.objects.link(ob2)
    for o in (ob, ob2):
        mw = o.matrix_world.copy()
        o.parent = N["J_Torso"]
        o.matrix_world = mw
    objs += [ob, ob2]
    return objs


def setup():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.color = (1, 1, 1)
    sc.view_settings.view_transform = "Standard"
    sh = sc.display.shading
    sh.light, sh.color_type = "FLAT", "SINGLE"
    sh.single_color = (0, 0, 0)
    sh.show_object_outline = sh.show_cavity = sh.show_shadows = False


VIEWS = {"front": ((0, -60, 2.55), (0, 0, 2.55)), "3q": ((40, -40, 2.55), (0, 0, 2.55))}


def run(opt):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup()
    h1, h2 = imp("H1", -DX), imp("H2", DX)
    if opt in ("A", "C"):
        thicker_cannon(h2)
    if opt in ("A2", "D"):
        thicker_cannon(h2, length=1.0)
    if opt in ("B", "C", "D"):
        h2 = shield_plate(h2)
    low = min((o.matrix_world @ v.co).z for o in h2 if o.type == "MESH" for v in o.data.vertices)
    top = max((o.matrix_world @ v.co).z for o in h2 if o.type == "MESH" for v in o.data.vertices)
    res = {"top_rest_m": round(top, 3), "lowest_rest_m": round(low, 3)}
    for pose in ("rest", "stand_aim"):
        if pose == "stand_aim":
            LP.apply(h1, "H1", pose)
            LP.apply(h2, "H2", pose)
        M = LP.titan_masks({"H1": h1, "H2": h2}, {"H1": -DX, "H2": DX}, os.path.join(OUT, "masks"), "%s_%s" % (opt, pose), camera, render)
        for view in ("front", "3q"):
            a, b = M[view]["H1"], M[view]["H2"]
            res["%s %s" % (pose, view)] = dict(full=LP.compare(a, b), quarter=LP.compare(LP.quarter(a), LP.quarter(b)))
            if pose == "rest" or view == "3q":
                loc, tgt = VIEWS[view]
                camera(loc, tgt, 15.5)
                p = os.path.join(OUT, "pair_%s_%s_%s.png" % (opt, pose, view))
                render(p, (800, 400))
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    R = {opt: run(opt) for opt in ("now", "A", "A2", "B", "C", "D")}
    json.dump(R, open(os.path.join(OUT, "h2_options.json"), "w", encoding="utf-8"), indent=1)
    print("=== H2OPT", json.dumps({o: {k: (v["quarter"]["not_shared_pct"] if isinstance(v, dict) else v) for k, v in r.items()} for o, r in R.items()}))


main()
