"""R6 lineup helpers (run inside Blender): pose an imported Titan_<code>.fbx with its own line's rotation rules, and
compare titans as black masks.

Posing: every line uses the v2 convention - joints rest at identity, a pose gives each joint a local rotation R in analysis
axes and the Blender quaternion is C R C^T (build_m1_silhouette.set_pose, build_heavy.set_pose, build_light.set_pose).
  M-1, H-1, H-2: v2 spec hand_poses (H-1/H-2 stand_aim is the v2 one, H/README section 1), v2 local_rotations.
  L-1, L-2: rig_L<n>.json "poses" (light stand: hip 23 / knee 46, right fingers 25), light_rig.local_rotations.
Then the v2 rule of every line's solve_pose: free feet levelled with the ankle (clip -35..60), lowest foot / toe / shin
vertex put on the ground.
"""
import json
import math
import os
import re
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
C = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)
FWD_B = Vector((0.0, -1.0, 0.0))     # analysis +x (titan forward) in Blender axes


def base(name):
    return re.sub(r"\.\d{3}$", "", name)


def by_name(objs):
    return {base(o.name): o for o in objs}


def rotations(code, pose):
    if code.startswith("L"):
        sys.path.insert(0, os.path.join(V3, "L"))
        import light_rig
        rig = json.load(open(os.path.join(V3, "L", code[:2], "rig_%s.json" % code[:2]), encoding="utf-8"))
        p = dict(rig["poses"][pose])
        return p, light_rig.local_rotations
    sys.path.insert(0, os.path.join(V3, "M1"))
    import build_m1_silhouette as S
    p = {k: v for k, v in S.D.SPEC["hand_poses"][pose].items() if not k.startswith("_")}
    if code.startswith("H"):
        p.update(HEAVY_POSE_OVERRIDE.get(pose, {}))
    return p, S.local_rotations


# the heavy line's own kneels (H/build_heavy.py HEAVY_POSE_OVERRIDE, H-P3); copied because build_heavy runs on import
HEAVY_POSE_OVERRIDE = {"kneel_hatch": {"a_R": 30.0, "h_flex_L": 40.0, "k_L": 55.0},
                       "landing_one_knee": {"a_R": 30.0, "h_flex_L": 52.0, "k_L": 64.0}}


def pose_names(code):
    """The 19 v2 pose names (every line keeps them; L and H use their own values for some)."""
    sys.path.insert(0, os.path.join(V3, "M1"))
    import build_m1_silhouette as S
    return list(S.D.SPEC["hand_poses"])


def rest_offsets(objs):
    """Largest joint rotation (deg) as imported: 0 for a file saved in rest, the bind pose for L."""
    out = {}
    for n, o in by_name(objs).items():
        if o.type == "EMPTY" and n.startswith("J_"):
            q = o.rotation_quaternion if o.rotation_mode == "QUATERNION" else o.rotation_euler.to_quaternion()
            out[n] = round(math.degrees(q.angle), 2)
    return out


def apply(objs, code, pose):
    """Pose one imported titan in place; returns the parameters used (with the solved ankles) and the ground offset."""
    p, local = rotations(code, pose)
    J = {n: o for n, o in by_name(objs).items() if o.type == "EMPTY" and (n.startswith("J_") or n == "W_Cannon")}
    root = [o for o in objs if o.parent is None][0]

    def setp(p):
        for n, R in local(p).items():
            if n in J:
                J[n].rotation_mode = "QUATERNION"
                J[n].rotation_quaternion = Matrix((C @ R @ C.T).tolist()).to_quaternion()
        bpy.context.view_layer.update()

    setp(p)
    for side in "LR":
        if "a_" + side in p or "J_Ankle_" + side not in J:
            continue
        f = J["J_Ankle_" + side].matrix_world.to_3x3() @ FWD_B
        pitch = math.degrees(math.atan2(-f.z, math.hypot(f.x, f.y)))
        p["a_" + side] = float(np.clip(-pitch, -35, 60))
    setp(p)
    feet = [o for n, o in by_name(objs).items() if o.type == "MESH" and re.search(r"_(Foot|Toe|Shin|Heel|Calf)", n)]
    low = min((o.matrix_world @ v.co).z for o in (feet or [o for o in objs if o.type == "MESH"]) for v in o.data.vertices)
    root.location.z -= low
    bpy.context.view_layer.update()
    return {k: round(v, 2) for k, v in p.items()}, round(-low, 3)


# ------------------------------------------------------------------ masks
def mask(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.array(img.pixels[:]).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px[:, :, :3].mean(axis=2) < 0.5          # black titan on white


def quarter(m):
    h, w = m.shape
    return m[: h // 4 * 4, : w // 4 * 4].reshape(h // 4, 4, w // 4, 4).mean(axis=(1, 3)) >= 0.5


def compare(a, b):
    """Share of the black pixels that the two titans do NOT have in common."""
    u, x = np.logical_or(a, b).sum(), np.logical_xor(a, b).sum()
    return dict(not_shared_pct=round(100.0 * x / u, 1), only_first_pct=round(100.0 * (a & ~b).sum() / a.sum(), 1),
                only_second_pct=round(100.0 * (b & ~a).sum() / b.sum(), 1), first_px=int(a.sum()), second_px=int(b.sum()))


def titan_masks(titans, xs, outdir, tag, camera, render, scale=9.0, res=480):
    """Each titan alone (others and helpers hidden), centred, same ortho scale; front and 3/4. Returns {view: {code: mask}}."""
    os.makedirs(outdir, exist_ok=True)
    allm = [o for o in bpy.data.objects if o.type in ("MESH", "FONT")]
    out = {"front": {}, "3q": {}}
    for code, objs in titans.items():
        mine = {o for o in objs if o.type == "MESH"}
        for o in allm:
            o.hide_render = o not in mine
        x = xs[code]
        for view, (loc, tgt) in (("front", ((x, -60, 2.55), (x, 0, 2.55))), ("3q", ((x + 40, -40, 2.55), (x, 0, 2.55)))):
            camera(loc, tgt, scale)
            p = os.path.join(outdir, "mask_%s_%s_%s.png" % (tag, view, code))
            render(p, (res, res))
            out[view][code] = mask(p)
    for o in allm:
        o.hide_render = False
    return out


def pair_table(M):
    codes = list(M["front"])
    T = {}
    for view in ("front", "3q"):
        for i, a in enumerate(codes):
            for b in codes[i + 1:]:
                T["%s/%s %s" % (a, b, view)] = dict(full=compare(M[view][a], M[view][b]),
                                                    quarter=compare(quarter(M[view][a]), quarter(M[view][b])))
    return T
