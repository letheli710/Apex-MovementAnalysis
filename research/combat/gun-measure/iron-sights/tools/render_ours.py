"""Renders our placeholder gun (HSD-Unity Docs/tools/gun-models) from the same cameras capture.py used on the R5 model, so the two can be laid over each other. Reads the kit, writes nothing there.

  blender --background --factory-startup --python render_ours.py -- <gun-models dir> <run dir> <out dir> r301 wingman peacekeeper

Views: every side_*/top_*/back_* base shot in meta.json, plus eye_r5 and eye_unity:
  eye_r5     the eye where R5's aimed muzzle puts it (meta.json), same pitch, R5's view model FOV (zoom_fov)
  eye_unity  the eye Unity's aimed pose gives (table below), 65.5 degree gun camera
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
a = sys.argv[sys.argv.index("--") + 1:]
KIT, RUN, OUT = a[0], a[1], a[2]
GUNS = a[3:]
sys.path.insert(0, KIT)
import bpy  # noqa: E402
import gunkit  # noqa: E402
import guns as G  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

K = gunkit.METRES
FPX = 611.0
F_R5_ADS = {"r301": 1153.0, "wingman": 1039.0, "peacekeeper": 1039.0}   # zoom_fov 55 / 60, see vmcal2.py
F_UNITY = 450.0 / math.tan(math.radians(65.5 / 2))
UNITY_AIM = {"r301": -3.9, "wingman": -3.5, "peacekeeper": -4.0}


def build(key):
    gunkit.clear()
    dims = json.load(open(os.path.join(KIT, "r5_dims.json"), encoding="utf-8"))["guns"]
    fn, name = G.GUNS[key]
    g = gunkit.Gun(key, dims[key], name)
    fn(g)
    root, obs = g.objects()
    return g, root, obs


def scene():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.9, 0.92, 0.95, 1)
    bg.inputs[1].default_value = 0.55
    for name, rot, e in (("sun", (math.radians(55), 0, math.radians(-30)), 2.6), ("fill", (math.radians(70), 0, math.radians(120)), 0.9)):
        l = bpy.data.lights.new(name, "SUN")
        l.energy = e
        ob = bpy.data.objects.new(name, l)
        sc.collection.objects.link(ob)
        ob.rotation_euler = rot
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.clip_start = 0.002
    cam.data.clip_end = 50
    cam.data.type = "PERSP"
    cam.data.sensor_fit = "HORIZONTAL"
    return sc, cam


def place(cam, loc, right, up, f):
    """Camera at loc (gun R, F, U in R5 units), screen right and up as gun-frame vectors, f in px per tangent."""
    r, u = Vector(right).normalized(), Vector(up).normalized()
    back = r.cross(u)
    m = Matrix((r, u, back)).transposed().to_4x4()
    m.translation = Vector(loc) * K
    cam.matrix_world = m
    cam.data.angle_x = 2 * math.atan(800.0 / f)


def main():
    os.makedirs(OUT, exist_ok=True)
    for gk in GUNS:
        meta = json.load(open(os.path.join(RUN, gk, "meta.json"), encoding="utf-8"))
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o)
        g, root, obs = build(gk)
        sc, cam = scene()
        for name, sh in meta["shots"].items():
            if not name.endswith("_base") or "focus" not in sh or name.startswith("side_wide"):
                continue
            F, R, U = sh["focus"]
            d = sh["d"]
            v = name.split("_")[0]
            if v == "side":   # camera on the gun's left, muzzle to screen left
                place(cam, (R - d, F, U), (0, -1, 0), (0, 0, 1), FPX)
            elif v == "top":  # camera above, muzzle to screen left, gun's right up the screen
                place(cam, (R, F, U + d), (0, -1, 0), (1, 0, 0), FPX)
            elif v == "back":  # camera behind, looking forward
                place(cam, (R, F - d, U), (1, 0, 0), (0, 0, 1), FPX)
            else:
                continue
            cam.data.clip_start = 7.0 * K   # the same near plane as the R5 pictures
            sc.render.filepath = os.path.join(OUT, f"{gk}_{name[:-5]}.png")
            bpy.ops.render.render(write_still=True)
        cam.data.clip_start = 0.002
        n = meta["attach_names"]["muzzle_flash"]
        am = meta["ads"][str(n)]
        th = math.radians(am["g"][0])
        mF, mU = am["p"][0], am["p"][2]
        # the eye in the gun frame when aimed in R5: the gun is pitched down by th against the view
        fwd, up = (0, math.cos(th), math.sin(th)), (0, -math.sin(th), math.cos(th))
        # gun axes as seen from the camera are (cos th, -sin th), (sin th, cos th): invert
        eyeF = -mF * math.cos(th) + mU * math.sin(th)
        eyeU = -mF * math.sin(th) - mU * math.cos(th)
        place(cam, (0, eyeF, eyeU), (1, 0, 0), (0, -math.sin(-th), math.cos(th)), F_R5_ADS[gk])
        sc.render.filepath = os.path.join(OUT, f"{gk}_eye_r5.png")
        bpy.ops.render.render(write_still=True)
        # Unity: the aimed muzzle's height is the one difference asked about, forward from R5's table
        place(cam, (0, -mF, -UNITY_AIM[gk]), (1, 0, 0), (0, 0, 1), F_UNITY)
        sc.render.filepath = os.path.join(OUT, f"{gk}_eye_unity.png")
        bpy.ops.render.render(write_still=True)


main()
