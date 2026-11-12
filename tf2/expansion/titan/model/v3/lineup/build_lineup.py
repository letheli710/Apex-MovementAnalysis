"""Five-titan lineup: imports every Titan_*.fbx under v3/ (M1, H, L), stands them side by side in their rest pose, renders
black silhouettes (full size + 1/4) and colour images.

  blender.exe -b -P build_lineup.py -- [out_dir]

Order left to right: L-1, L-2, M-1, H-1, H-2 (whatever exists). Names come from the file name (Titan_<code>.fbx).
"""
import glob
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
# R5: each round goes to its own folder (the first lineup stays in lineup/ itself). Default: lineup/r5/.
OUT = os.path.join(HERE, args[0]) if args else os.path.join(HERE, "r5")
# Optional explicit files, code=path (e.g. L1=../L/L1/r5_final/Titan_L1.fbx), relative to v3/
PICK = dict(a.split("=", 1) for a in args[1:] if "=" in a)
ORDER = ["L1", "L-1", "L2", "L-2", "M1", "M-1", "H1", "H-1", "H2", "H-2"]
SPACING = 7.6
EXT = {}
HUMAN_DX = 3.0      # human block this far to the right of each titan's centre


def find():
    # R5: only the current finished file of each line (v3/<line>/Titan_<code>.fbx). Round folders also hold copies
    # (H/H1/r4_final/Titan_H1.fbx, M1/final/Titan_M1_r4.fbx ...), which must not be picked up.
    files = sorted(f for f in glob.glob(os.path.join(V3, "*", "Titan_*.fbx"))
                   if os.path.basename(f)[6:-4].replace("-", "").upper() in ("L1", "L2", "M1", "H1", "H2"))
    for code, rel in PICK.items():
        files = [f for f in files if os.path.basename(f)[6:-4].upper() != code.upper()] + [os.path.normpath(os.path.join(V3, rel))]
    def key(f):
        code = os.path.basename(f)[6:-4].upper().replace("_", "-")
        return next((i for i, o in enumerate(ORDER) if code.replace("-", "") == o.replace("-", "")), 99)
    return sorted(files, key=key)


def flat_mat(name, rgba):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = rgba
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m


def collider(x):
    """3.05 x 5.97 m collider frame (TITAN-DESIGN A: 120 x 235 u), wireframe."""
    v = [(x + a * 1.525, b * 1.525, c * 5.97) for c in (0, 1) for b in (-1, 1) for a in (-1, 1)]
    md = bpy.data.meshes.new("H_collider")
    md.from_pydata(v, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ob = bpy.data.objects.new("H_collider", md)
    md.materials.append(flat_mat("H_collider", (0.10, 0.40, 0.95, 1)))
    ob.modifiers.new("wire", "WIREFRAME").thickness = 0.04
    bpy.context.scene.collection.objects.link(ob)


def label(x, text):
    cu = bpy.data.curves.new("H_label", "FONT")
    cu.body, cu.size, cu.align_x = text, 0.9, "CENTER"
    ob = bpy.data.objects.new("H_label", cu)
    ob.location = (x, -1.6, -1.25)
    ob.rotation_euler = (math.radians(90), 0, 0)
    cu.materials.append(flat_mat("H_label", (0.05, 0.05, 0.05, 1)))
    bpy.context.scene.collection.objects.link(ob)


def human(x):
    md = bpy.data.meshes.new("H_human")
    v = [(x + a * 0.25, b * 0.15, c * 1.8) for c in (0, 1) for b in (-1, 1) for a in (-1, 1)]
    md.from_pydata(v, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ob = bpy.data.objects.new("H_human", md)
    m = bpy.data.materials.new("H_human"); m.diffuse_color = (0.92, 0.38, 0.08, 1)
    m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.35, 0.08, 1)
    md.materials.append(m)
    bpy.context.scene.collection.objects.link(ob)


def camera(loc, target, ortho):
    cam = bpy.data.objects.get("Cam") or bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    if cam.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam)
    if ortho:
        cam.data.type, cam.data.ortho_scale = "ORTHO", ortho
    else:
        cam.data.type, cam.data.lens = "PERSP", 50
    cam.data.clip_end = 300
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


def render(path, res):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    files = find()
    os.makedirs(OUT, exist_ok=True)
    import json, time, hashlib
    json.dump([dict(file=os.path.relpath(f, V3).replace("\\", "/"), bytes=os.path.getsize(f),
                    modified=time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(f))),
                    sha1=hashlib.sha1(open(f, "rb").read()).hexdigest()[:12]) for f in files],
              open(os.path.join(OUT, "lineup_files.json"), "w", encoding="utf-8"), indent=1)   # which file of each titan was used
    names = []
    for i, f in enumerate(files):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=f, axis_forward="-Z", axis_up="Y")
        new = [o for o in bpy.data.objects if o not in before]
        x = (i - (len(files) - 1) / 2) * SPACING
        for o in new:
            if o.parent is None:
                o.location.x += x
        names.append(os.path.basename(f)[6:-4])
        bpy.context.view_layer.update()
        vs = [o.matrix_world @ v.co for o in new if o.type == "MESH" for v in o.data.vertices]
        EXT[names[-1]] = dict(width_m=round(max(v.x for v in vs) - min(v.x for v in vs), 2), depth_m=round(max(v.y for v in vs) - min(v.y for v in vs), 2),
                              top_m=round(max(v.z for v in vs), 3), lowest_m=round(min(v.z for v in vs), 3),
                              meshes=sum(1 for o in new if o.type == "MESH"),
                              tris=sum(len(p.vertices) - 2 for o in new if o.type == "MESH" for p in o.data.polygons))
        collider(x)
        human(x + HUMAN_DX)
        code = os.path.basename(f)[6:-4]
        label(x, code[0] + "-" + code[1:] if "-" not in code else code)
    width = len(files) * SPACING + 1
    sc = bpy.context.scene
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    os.makedirs(OUT, exist_ok=True)
    # black silhouettes
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.world.color = (1, 1, 1)
    sc.view_settings.view_transform = "Standard"
    sh = sc.display.shading
    sh.light, sh.color_type = "FLAT", "MATERIAL"
    sh.show_object_outline = sh.show_cavity = False
    saved = {}
    for m in bpy.data.materials:
        if not m.name.startswith("H_"):
            saved[m.name] = tuple(m.diffuse_color)
            m.diffuse_color = (0, 0, 0, 1)
    camera((0, -60, 2.55), (0, 0, 2.55), width)
    res = (int(400 * len(files) + 100), int((400 * len(files) + 100) * 8.2 / width))   # 8.2 m tall window: ground line, label, 5.97 frame
    render(os.path.join(OUT, "lineup_sil_front.png"), res)
    camera((40, -40, 2.55), (0, 0, 2.55), width * 1.02)
    render(os.path.join(OUT, "lineup_sil_3q.png"), res)
    for n, c in saved.items():
        bpy.data.materials[n].diffuse_color = c
    # colour
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.64, 0.67, 1)
    for nm, rot, en in (("Sun", (math.radians(50), 0, math.radians(-35)), 3.5), ("Fill", (math.radians(70), 0, math.radians(150)), 1.2)):
        l = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN")); l.data.energy = en; l.rotation_euler = rot
        sc.collection.objects.link(l)
    camera((0, -60, 2.55), (0, 0, 2.55), width)
    render(os.path.join(OUT, "lineup_colour_front.png"), res)
    camera((40, -40, 2.55), (0, 0, 2.55), width * 1.02)
    render(os.path.join(OUT, "lineup_colour_3q.png"), res)
    try:
        from PIL import Image
        for n in ("lineup_sil_front", "lineup_sil_3q"):
            im = Image.open(os.path.join(OUT, n + ".png"))
            im.resize((im.width // 4, im.height // 4), Image.LANCZOS).save(os.path.join(OUT, n + "_quarter.png"))
    except ImportError:
        pass   # Blender's Python has no PIL; the quarter images are made by: py -3 build_lineup_quarter.py
    json.dump(EXT, open(os.path.join(OUT, "lineup_extents.json"), "w", encoding="utf-8"), indent=1)
    print("=== LINEUP", names, EXT)


main()
