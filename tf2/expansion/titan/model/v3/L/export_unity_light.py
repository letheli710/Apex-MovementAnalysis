"""Unity copy of a light titan (walk plan step 2a): the FBX in the ZERO pose + the spec JSON the Unity import tests read.

  blender.exe -b -P export_unity_light.py -- L1        (then L2)

Why a separate FBX: HSD-Unity's TitanModelImport bakes every node's rotation into the vertices and rests each joint at identity, so the pose a
file is in becomes Unity's rest pose. The product file opens in the R5 bind pose (right arm carrying the rifle, L-D16); imported as it is,
the arm would be bent twice once the animator adds its angles. The geometry is the same build (build_light.py, current code = r5b).

Writes unity/titan_<code>_v3.fbx and unity/titan_<code>_v3_spec.json (analysis axes x forward, y left, z up; Unity converts with
TitanPose.ToUnity). Spec: fbx sha256, root, nodes (name, parent, zero-pose position), part meshes (object, joint, slot, triangles),
a few posed checks (joint world position + world rotation, pelvis grounded like build_light.solve_pose), foot and body numbers."""
import hashlib
import json
import os
import sys

os.environ["LIGHT_NO_MAIN"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import numpy as np  # noqa: E402

import build_light as B  # noqa: E402

CODE = B.CODE
OUTD = os.path.join(HERE, "unity")
os.makedirs(OUTD, exist_ok=True)
POSES = ["stand_aim", "yaw_85_level", "crouch", "kneel_hatch", "walk_A", "aim_down_45"]


def joint_frame(objs, n):
    m = objs[n].matrix_world
    p = B.C.T @ np.array(m.translation)            # Blender -> analysis
    return [round(float(x), 5) for x in p], [round(float(x), 6) for x in B.world_R(objs[n]).ravel()]


def degenerate(ob):
    """Triangles with no area or with two corners within 0.1 mm (0.01 mm was not enough: L-2 Torso_Upper lost 8, counted 4): Unity's importer welds and drops some of these (L-1 Blender 51 780,
    Unity 51 100). The import test allows a part to lose at most this many."""
    me = ob.data
    me.calc_loop_triangles()
    V = np.array([v.co[:] for v in me.vertices])
    n = 0
    for t in me.loop_triangles:
        a, b, c = (V[i] for i in t.vertices)
        if t.area < 1e-9 or min(np.linalg.norm(a - b), np.linalg.norm(b - c), np.linalg.norm(a - c)) < 1e-4:
            n += 1
    return n


def main():
    objs, meshes, mats = B.build()
    B.set_materials("color", mats)
    # posed checks first (same solve as the build's checks, incl. the right-wrist table)
    poses = []
    for name in POSES:
        p, off = B.solve_pose(objs, meshes, B.R.poses(code=CODE)[name], name)
        joints = []
        for n in B.node_order():
            if n.startswith(("J_", "W_")):
                pos, rot = joint_frame(objs, n)
                joints.append(dict(joint=n, pos=pos, R=rot))
        poses.append(dict(name=name, params={k: float(v) for k, v in p.items()}, joints=joints))
    # zero pose: every joint at identity (arms straight), pelvis at rest
    B.set_pose(objs, {})
    nodes = [dict(name=n, parent=B.PARENT[n], pos=[round(float(x), 5) for x in B.POS[n]]) for n in B.node_order()]
    allv = np.vstack([B.wverts(o) for o in meshes.values()])
    footb = {}
    for k in ("Foot", "Toe"):
        W = B.wverts(meshes[k + "_L"])
        footb[k] = dict(min=[round(float(x), 4) for x in (B.C.T @ W.T).T.min(0)], max=[round(float(x), 4) for x in (B.C.T @ W.T).T.max(0)])
    for ob in [o for o in bpy.data.objects if o.type not in ("EMPTY", "MESH")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    # Unity copy only: triangulate here (Blender's own split, the one the renders show). Left as n-gons, Unity split some of them its own way
    # and lost surface (L-2 Torso_Upper 0.6 %, Rack_Clamps 15 % before that part was rebuilt). The product FBX keeps its quads and n-gons.
    import bmesh
    for ob in meshes.values():
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="EAR_CLIP")
        bm.to_mesh(ob.data)
        bm.free()
        ob.data.update()
    parts = [dict(object=ob.name, joint=ob["owner_joint"], slot=ob["slot"], tris=B.tri_count(ob), degenerate=degenerate(ob), area=round(float(sum(t.area for t in ob.data.loop_triangles)), 5)) for ob in meshes.values()]   # triangle area: polygon area is approximate for non-flat quads   # after the split, so tris and area are what Unity gets
    fbx = os.path.join(OUTD, "titan_%s_v3.fbx" % CODE.lower())
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                             apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                             add_leaf_bones=False, mesh_smooth_type="FACE")
    spec = dict(code=CODE, source="v3/L/export_unity_light.py (build_light.py r5b geometry), zero pose", root=B.ROOT,
                fbx=os.path.basename(fbx), fbx_sha256=hashlib.sha256(open(fbx, "rb").read()).hexdigest(),
                nodes=nodes, parts=parts, triangles=int(sum(p["tris"] for p in parts)),
                weapon_root=B.WEAPON["root"], has_wings=bool(B.MOD.HAS_WINGS),
                body_top_zero_pose=round(float(allv[:, 2].max()), 4),
                foot_L=footb, poses=poses, bind_pose=B.R.BIND,
                note="body top and foot bounds in the zero pose (arms straight, legs straight), analysis axes")
    json.dump(spec, open(os.path.join(OUTD, "titan_%s_v3_spec.json" % CODE.lower()), "w", encoding="utf-8"), indent=1)
    print("=== unity export", CODE, spec["fbx_sha256"][:12], len(nodes), "nodes", len(parts), "parts", spec["triangles"], "tris", "top", spec["body_top_zero_pose"])


main()
