"""The Unity copy of M-1: zero pose, triangulated in Blender, + per-part areas for the import test.

  blender.exe -b -P export_unity_m1.py

Degenerate edges / faces under 0.1 mm are dissolved first (slivers). Writes Titan_M1_unity.fbx next to Titan_M1.fbx (same export settings as build_m1_final.export) and unity_parts.json
(object, owner joint, triangles, Blender's zero-area triangles, area m^2). export_unity_spec_m1.py puts both into titan_m1_spec.json.
Why (light line, HSD-Unity #74): TitanModelImport bakes every node's rotation into the vertices, so the file must be in its zero
pose (M-1's is: checked here); and Unity's own n-gon split can drop faces (L-2 lost 15 % of one part), Blender's does not.
The finished Titan_M1.fbx / .blend stay as they are (quads and n-gons).
"""
import json
import math
import os

import bpy
import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "Titan_M1.blend"))
bad = [o.name for o in bpy.data.objects if o.type == "EMPTY" and o.rotation_mode == "QUATERNION" and o.rotation_quaternion.angle > 1e-6]
bad += [o.name for o in bpy.data.objects if o.type == "EMPTY" and o.rotation_mode != "QUATERNION" and o.rotation_euler.to_quaternion().angle > 1e-6]
assert not bad, "not in the zero pose: %s" % bad[:5]
parts = []
FLAT = {}
for ob in sorted((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: o.name):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    # first Unity run: two sliver triangles (bevel clamp overlaps) had a face normal ~90 deg from their vertex normal (TitanImportTests
    # MeshFacesPointOutward, M1_Backpack / M1_Forearm_L); dissolving edges and faces under 0.1 mm removes them before the split
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    # triangles whose corner normal (smooth shading over < 35 deg edges, after the bevel) points away from the triangle itself: Unity's
    # MeshFacesPointOutward caught one on M1_Forearm_L (dot -0.006). Mark that triangle's edges sharp, so it is shaded flat.
    me = ob.data
    cn = me.corner_normals
    flip = [p for p in me.polygons if any(cn[li].vector.dot(p.normal) < 0.05 for li in p.loop_indices)]
    if flip:
        sharp = me.attributes.get("sharp_edge") or me.attributes.new("sharp_edge", "BOOLEAN", "EDGE")
        ekmap = {e.key: e.index for e in me.edges}
        for p in flip:
            for ek in p.edge_keys:
                sharp.data[ekmap[ek]].value = True
        me.update()
        bad = [p.index for p in me.polygons if any(me.corner_normals[li].vector.dot(p.normal) < 0.05 for li in p.loop_indices)]
        FLAT[ob.name] = (len(flip), len(bad))
    M = ob.matrix_world
    area, degen = 0.0, 0
    for p in ob.data.polygons:
        a, b, c = (M @ ob.data.vertices[i].co for i in p.vertices)
        t = 0.5 * (b - a).cross(c - a).length
        area += t
        degen += t < 1e-9
    parts.append({"object": ob.name, "joint": ob.parent.name, "tris": len(ob.data.polygons), "degenerate": degen, "area": round(area, 5)})
fbx = os.path.join(HERE, "Titan_M1_unity.fbx")
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                         apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                         add_leaf_bones=False, mesh_smooth_type="FACE")
json.dump({"fbx": "Titan_M1_unity.fbx", "triangles": sum(p["tris"] for p in parts), "parts": parts},
          open(os.path.join(HERE, "unity_parts.json"), "w", encoding="utf-8"), indent=1)
print("=== FLAT (triangles made flat, still bad after)", FLAT)
print("=== UNITY COPY parts", len(parts), "tris", sum(p["tris"] for p in parts), "degenerate", sum(p["degenerate"] for p in parts))
