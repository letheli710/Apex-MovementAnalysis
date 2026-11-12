"""The Unity copy of a finished heavy (walk retarget H4): triangulated in Blender, so Unity's own polygon split cannot drop faces (found on the
light titan, HSD-Unity #74), exported with build_heavy.py's FBX settings, plus each part's area for the import check (Unity within 0.5 %).

  blender.exe -b <Titan_Hx.blend> -P unity_export.py -- <out.fbx> <out_areas.tsv>

The .blend must be at rest (build_heavy saves it that way: every joint at identity = the zero pose), so TitanModelImport's bake bends nothing twice."""
import os
import sys

import bmesh
import bpy

args = sys.argv[sys.argv.index("--") + 1:]
fbx, areas = args[0], args[1]
rows = ["part\ttris\tarea_m2"]
for ob in bpy.data.objects:
    ob.select_set(False)
for ob in sorted([o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("REF_")], key=lambda o: o.name):
    for e in [ob] + [p for p in [ob.parent] if p]:
        pass
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    area = sum(p.area for p in ob.data.polygons)
    rows.append("%s\t%d\t%.6f" % (ob.name, len(ob.data.polygons), area))
    ob.select_set(True)
for ob in bpy.data.objects:
    if ob.type == "EMPTY":
        ob.select_set(True)
# rest check: every joint empty at identity rotation
bad = [o.name for o in bpy.data.objects if o.type == "EMPTY" and o.name.startswith(("J_", "W_")) and o.rotation_quaternion.angle > 1e-6 and o.rotation_mode == "QUATERNION"]
print("=== REST", "ok" if not bad else "NOT AT REST: " + ",".join(bad))
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                         apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                         add_leaf_bones=False, mesh_smooth_type="FACE", use_mesh_modifiers=True)
open(areas, "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("=== EXPORT", fbx, len(rows) - 1, "meshes")
