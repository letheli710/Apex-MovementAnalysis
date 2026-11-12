"""Light titans L-1 / L-2: build in Blender, run the SPEC.md section 5 checks, render, export.

  blender.exe -b -P build_light.py -- L1 <stage> [nocheck] [norender]
      stage 1 silhouette blocks, 2 mid model (plates, bevels, panel grooves), 3 detail, 4 materials + sockets + export
      images go to <code>/r<stage>_<name>/ (one folder per round, nothing overwritten), checks to the same folder.
      stage 4 also writes Titan_<code>.blend / .fbx next to this script's folder (L/).

Coordinates in the part tables are ANALYSIS axes, world rest (x forward, y left, z up). Blender: X = y, Y = -x, Z up (titan faces -Y),
exactly like v2/build_titan.py and M1/build_m1_silhouette.py.
"""
import importlib
import json
import math
import os
import sys
import time

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo  # noqa: E402
import light_common as LC  # noqa: E402
import light_rig as R  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
CODE = args[0] if args else "L1"
STAGE = int(args[1]) if len(args) > 1 else 4
FLAGS = set(args[2:])
MOD = importlib.import_module({"L1": "l1_parts", "L2": "l2_parts"}[CODE])
STAGE_NAME = {1: "silhouette", 2: "mid", 3: "detail", 4: "final"}[STAGE]
OUT = os.path.join(HERE, CODE, "r%d_%s" % (STAGE, STAGE_NAME))
os.makedirs(OUT, exist_ok=True)
ROOT = "Titan_" + CODE
C = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)
SLOT_NAME = {"pri": "MAT_Primary", "sec": "MAT_Secondary", "frame": "MAT_Frame", "emit": "MAT_Emissive"}
GREY = {"pri": 0.78, "sec": 0.45, "frame": 0.22, "emit": 0.97}
TRI_MIN, TRI_MAX, TRI_PART = 40000, 60000, 6000


def to_b(v):
    return (float(v[1]), float(-v[0]), float(v[2]))


def hexrgb(h):
    h = h.lstrip("#")
    s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)   # sRGB -> linear


# ------------------------------------------------------------------ rig + parts
PARTS, XJ, SOCKETS, WEAPON = MOD.build()
NODES = R.core_joints(ROOT)
NODES.update(XJ)
JOINT_NAMES = list(NODES)
NODES.update(SOCKETS)
POS = {n: np.array(p, float) for n, (par, p) in NODES.items()}
PARENT = {n: par for n, (par, p) in NODES.items()}


def node_order():
    done, order = {ROOT}, []
    while len(order) < len(NODES):
        for n, par in PARENT.items():
            if n not in done and par in done:
                order.append(n); done.add(n)
    return order


def clean_mesh(bm):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def process(bm, part):
    """Stage >= 2: armour plates get panel grooves on their large faces, every part gets 2-4 cm bevels on hard edges."""
    if STAGE < 2:
        return
    size = max((max(v.co[i] for v in bm.verts) - min(v.co[i] for v in bm.verts)) for i in range(3))
    if part.get("panel") and size > 0.5:
        big = [f for f in bm.faces if f.calc_area() > 0.10 and len(f.verts) == 4]
        if big:
            bmesh.ops.inset_individual(bm, faces=big, thickness=0.028, depth=-0.012, use_even_offset=True)
    w = 0.03 if size > 0.6 else (0.02 if size > 0.25 else 0.008)
    edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(28)]
    if edges and size > 0.08 and (part["stage"] < 3 or size > 0.25):
        bmesh.ops.bevel(bm, geom=edges, offset=w, segments=2 if (size > 0.25 and part["stage"] < 3) else 1, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.context.scene.collection
    mats = {}
    for k, nm in SLOT_NAME.items():
        m = bpy.data.materials.new(nm)
        m["grey"] = GREY[k]
        m["slot"] = k
        mats[k] = m
    objs = {ROOT: bpy.data.objects.new(ROOT, None)}
    col.objects.link(objs[ROOT])
    for n in node_order():
        e = bpy.data.objects.new(n, None)
        e.empty_display_type = "ARROWS" if n[0] in "JW" else "SPHERE"
        e.empty_display_size = 0.15 if n[0] in "JW" else 0.07
        e.rotation_mode = "QUATERNION"
        col.objects.link(e)
        objs[n] = e
        e.parent = objs[PARENT[n]]
        pp = POS[PARENT[n]] if PARENT[n] != ROOT else np.zeros(3)
        e.location = to_b(POS[n] - pp)
    meshes = {}
    for part in PARTS:
        if part["stage"] > STAGE:
            continue
        jp = POS[part["joint"]]
        name = "%s_%s" % (CODE, part["name"])
        md = bpy.data.meshes.new(name)
        vs, fs = part["mesh"]
        md.from_pydata([to_b(np.array(v) - jp) for v in vs], [], [list(f) for f in fs])
        md.validate()
        bm = bmesh.new()
        bm.from_mesh(md)
        clean_mesh(bm)
        process(bm, part)
        bm.to_mesh(md)
        bm.free()
        md.update()
        if STAGE >= 2:
            md.shade_smooth()
            md.set_sharp_from_angle(angle=math.radians(32))
        md.materials.append(mats[part["slot"]])
        ob = bpy.data.objects.new(name, md)
        col.objects.link(ob)
        ob.parent = objs[part["joint"]]
        ob["owner_joint"] = part["joint"]
        ob["slot"] = part["slot"]
        ob["hub"] = bool(part["hub"])
        ob["stage"] = part["stage"]
        meshes[part["name"]] = ob
    bpy.context.view_layer.update()
    return objs, meshes, mats


# ------------------------------------------------------------------ posing
def set_pose(objs, p, off=(0, 0, 0)):
    rots = R.local_rotations(p)
    for n in JOINT_NAMES:
        Rm = rots.get(n)
        M = C @ Rm @ C.T if Rm is not None else np.eye(3)
        objs[n].rotation_quaternion = Matrix(M.tolist()).to_quaternion()
    objs["J_Pelvis"].location = to_b(POS["J_Pelvis"] + np.array(off, float))
    bpy.context.view_layer.update()


def world_R(ob):
    return C.T @ np.array(ob.matrix_world.to_3x3()) @ C


def wverts(ob):
    m = np.array(ob.matrix_world)
    v = np.array([x.co[:] for x in ob.data.vertices])
    return v @ m[:3, :3].T + m[:3, 3]


GROUND_PARTS = ("Foot", "Toe", "Heel_Spur", "Ankle", "Shin", "Shin_Plate", "Knee_Guard", "Calf_Blade", "Knee_Hub", "Calf_Mount")


def ground_names(meshes):
    return [n for n in meshes if any(n == g + s for g in GROUND_PARTS for s in ("_L", "_R"))]


def solve_pose(objs, meshes, hand):
    p = {k: v for k, v in hand.items() if not k.startswith("_")}
    set_pose(objs, p)
    for side in "LR":
        if "a_" + side in p:
            continue
        f = world_R(objs["J_Ankle_" + side]) @ np.array([1.0, 0, 0])
        pitch = math.degrees(math.atan2(-f[2], math.hypot(f[0], f[1])))
        p["a_" + side] = float(np.clip(-pitch, -35, 60))
    set_pose(objs, p)
    low = min(wverts(meshes[n])[:, 2].min() for n in ground_names(meshes))
    off = (0.0, 0.0, -float(low))
    set_pose(objs, p, off)
    return p, off


# ------------------------------------------------------------------ collision
def adjacent(a, b):
    return PARENT.get(a) == b or PARENT.get(b) == a


def owner_of(ob):
    """Weapons and the sword hang under sockets / W_ roots: their owner for adjacency is the node they are parented to."""
    return ob["owner_joint"]


def collide(meshes, skip_names=()):
    names = [n for n in meshes if n not in skip_names]
    W = {n: wverts(meshes[n]) for n in names}
    BB = {n: (W[n].min(0), W[n].max(0)) for n in names}
    T = {}

    def tree(n):
        if n not in T:
            T[n] = BVHTree.FromPolygons([Vector(x) for x in W[n]], [list(p.vertices) for p in meshes[n].data.polygons])
        return T[n]
    hits = []
    for i, a in enumerate(names):
        oa = owner_of(meshes[a])
        for b in names[i + 1:]:
            ob_ = owner_of(meshes[b])
            if oa == ob_:
                continue
            if (adjacent(oa, ob_) or PARENT.get(oa) == PARENT.get(ob_)) and (meshes[a]["hub"] or meshes[b]["hub"]):
                continue
            if frozenset((a, b)) in EXCL:
                continue
            if np.any(BB[a][1] < BB[b][0]) or np.any(BB[b][1] < BB[a][0]):
                continue
            if tree(a).overlap(tree(b)):
                hits.append(a + " x " + b)
    return hits


EXCL = {frozenset(p) for p in getattr(MOD, "EXCLUDED_NAMES", [])}


def _inside(tree, pt):
    o = Vector(pt); d = Vector((0.0123, 0.0071, 1.0)).normalized(); n = 0
    for _ in range(64):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        n += 1
        o = h[0] + d * 1e-5
    return n % 2 == 1


def tree_of(ob):
    return BVHTree.FromPolygons([Vector(x) for x in wverts(ob)], [list(p.vertices) for p in ob.data.polygons])


# ------------------------------------------------------------------ measurements
def slice_extent(obs, z):
    """Width (Blender x) and depth (Blender y) of the horizontal section at height z through the given meshes."""
    pts = []
    for ob in obs:
        W = wverts(ob)
        for p in ob.data.polygons:
            vs = list(p.vertices)
            for i in range(len(vs)):
                a, b = W[vs[i]], W[vs[(i + 1) % len(vs)]]
                if (a[2] - z) * (b[2] - z) < 0:
                    t = (z - a[2]) / (b[2] - a[2])
                    pts.append(a + t * (b - a))
    if not pts:
        return 0.0, 0.0
    P = np.array(pts)
    return float(np.ptp(P[:, 0])), float(np.ptp(P[:, 1]))


def max_girth(obs, z0, z1):
    best = (0.0, 0.0, 0.0, 0.0)
    for z in np.arange(z0, z1, 0.04):
        w, d = slice_extent(obs, z)
        if w * d > best[0]:
            best = (w * d, w, d, z)
    return dict(area_m2=round(best[0], 3), width_m=round(best[1], 3), depth_m=round(best[2], 3), at_z=round(best[3], 2))


def tri_count(ob):
    ob.data.calc_loop_triangles()
    return len(ob.data.loop_triangles)


def slot_areas(meshes):
    a = {k: 0.0 for k in SLOT_NAME}
    for ob in meshes.values():
        s = ob["slot"]
        a[s] += sum(p.area for p in ob.data.polygons)
    tot = sum(a.values())
    return {SLOT_NAME[k]: round(100 * v / tot, 1) for k, v in a.items()}


def by_prefix(meshes, *prefixes):
    return [ob for n, ob in meshes.items() if any(n.startswith(p) for p in prefixes)]


# ------------------------------------------------------------------ checks
def run_checks(objs, meshes):
    t0 = time.time()
    Rp = {"code": CODE, "stage": STAGE, "stage_name": STAGE_NAME}
    set_pose(objs, {})
    allv = np.vstack([wverts(o) for o in meshes.values()])
    H = float(allv[:, 2].max())
    Rp["rest_top_m"] = round(H, 3)
    Rp["rest_top_part"] = max(meshes, key=lambda n: wverts(meshes[n])[:, 2].max())
    Rp["parts"] = len(meshes)
    tris = {n: tri_count(o) for n, o in meshes.items()}
    T = sum(tris.values())
    big = max(tris, key=tris.get)
    Rp["tris"] = dict(ok=(TRI_MIN <= T <= TRI_MAX) and tris[big] <= TRI_PART, total=T, target=[TRI_MIN, TRI_MAX], largest_part=big,
                      largest_part_tris=tris[big], part_limit=TRI_PART, note="only judged at stage 4")
    # shoulder / hip width (front view outer edges)
    sh = np.vstack([wverts(o) for o in by_prefix(meshes, *MOD.SHOULDER_PARTS)])
    sw = float(sh[:, 0].max() - sh[:, 0].min())
    hip = np.vstack([wverts(o) for o in by_prefix(meshes, "Thigh", "Pelvis", "Collar", "Skirt")])
    hip = hip[(hip[:, 2] > R.HIP_Z - 0.30) & (hip[:, 2] < R.HIP_Z + 0.20)]
    hw = float(hip[:, 0].max() - hip[:, 0].min())
    Rp["shoulder_ge_hip_x1.5"] = dict(ok=sw >= 1.5 * hw, shoulder_w=round(sw, 3), hip_w=round(hw, 3), need=round(1.5 * hw, 3), ratio=round(sw / hw, 3),
                                      shoulder_parts=list(MOD.SHOULDER_PARTS), how="outer x extent of the shoulder parts; hip = thighs+pelvis+collar within -0.30/+0.20 of the hip joint")
    # shoulder armour thickness and cover over the arm top
    trees = {}

    def span(names, X, Y):
        zs = []
        for n in names:
            if n not in meshes:
                continue
            t = trees.setdefault(n, tree_of(meshes[n]))
            o = Vector((X, Y, 9.0))
            while True:
                h = t.ray_cast(o, Vector((0, 0, -1)))
                if h[0] is None:
                    break
                zs.append(h[0].z)
                o = h[0] + Vector((0, 0, -1e-4))
        return (max(zs), min(zs)) if zs else None
    Rp["shoulder_armour"] = MOD.shoulder_armour_check(span)
    # waist
    pel_top = max(wverts(o)[:, 2].max() for o in by_prefix(meshes, "Collar", "Pelvis"))
    tor_bot = min(wverts(o)[:, 2].min() for o in by_prefix(meshes, "Torso_Lower", "Torso_Upper"))
    wh = tor_bot - pel_top
    Rp["waist_le_height_x0.06"] = dict(ok=wh <= 0.06 * H, waist_visible_m=round(wh, 3), limit_m=round(0.06 * H, 3),
                                       how="gap between collar/pelvis top and torso bottom at rest")
    bend = {}
    tor = [n for n in meshes if n.startswith("Torso_Lower") or n.startswith("Torso_Upper")]
    pel = [n for n in meshes if n.startswith("Pelvis") or n.startswith("Collar") or n.startswith("Skirt")]
    for k, v in (("bend_45", {"w_bend": 45}), ("bend_-25", {"w_bend": -25}), ("side_30", {"w_side": 30}), ("side_-30", {"w_side": -30}),
                 ("yaw_90_bend_45", {"w_yaw": 90, "w_bend": 45}), ("yaw_-90_bend_45", {"w_yaw": -90, "w_bend": 45})):
        set_pose(objs, v)
        sub = {n: meshes[n] for n in tor + pel}
        bend[k] = [h for h in collide(sub)]
    Rp["waist_bend_clear"] = dict(ok=not any(bend.values()), cases={k: (not v) for k, v in bend.items()}, hits={k: v for k, v in bend.items() if v})
    set_pose(objs, {})
    # feet
    f = np.vstack([wverts(o) for o in by_prefix(meshes, "Foot_L", "Toe_L", "Heel_Spur_L")])
    fl = float(np.ptp(f[:, 1]))
    Rp["foot_ge_height_x0.22"] = dict(ok=fl >= 0.22 * H, foot_len_m=round(fl, 3), need_m=round(0.22 * H, 3), foot_w_m=round(float(np.ptp(f[:, 0])), 3))
    th = by_prefix(meshes, "Thigh_L", "Thigh_Plate_L", "Thigh_Side_L", "Thigh_Hub_L")
    sn = by_prefix(meshes, "Shin_L", "Shin_Plate_L", "Calf_Blade_L", "Knee_Guard_L", "Tasset")
    gt = max_girth(th, R.KNEE_Z + 0.25, R.HIP_Z - 0.10)
    gs = max_girth([o for o in sn if o.name.endswith("_L")], R.ANKLE_Z + 0.2, R.KNEE_Z + 0.2)
    Rp["calf_ge_thigh"] = dict(ok=gs["area_m2"] >= gt["area_m2"], thigh=gt, shin=gs, how="largest horizontal section (width x depth) of all parts on that bone, 4 cm steps")
    Rp["top_le_collider_5.97"] = dict(ok=H <= 5.97, rest_top_m=round(H, 3))
    # poses
    poses = R.poses()
    pose_hits, tops, solved = {}, {}, {}
    for name, hand in poses.items():
        p, off = solve_pose(objs, meshes, hand)
        solved[name] = (p, off)
        pose_hits[name] = collide(meshes)
        tops[name] = round(float(max(wverts(o)[:, 2].max() for o in meshes.values())), 3)
    if MOD.HAS_WINGS:
        for name in ("stand_aim", "aim_up_45", "aim_down_45", "yaw_85_level", "yaw_-85_level", "walk_A", "walk_B", "dash_float_L"):
            hand = dict(poses[name], wing_L=R.WING_ANGLE, wing_R=R.WING_ANGLE)
            p, off = solve_pose(objs, meshes, hand)
            solved[name + "+wings"] = (p, off)
            pose_hits[name + "+wings"] = collide(meshes)
            tops[name + "+wings"] = round(float(max(wverts(o)[:, 2].max() for o in meshes.values())), 3)
    set_pose(objs, {})
    rest_hits = collide(meshes)
    req = [n for n in pose_hits if n.split("+")[0] in R.REQUIRED]
    Rp["poses_required"] = dict(ok=not any(pose_hits[n] for n in req), names=req, failed={n: pose_hits[n] for n in req if pose_hits[n]})
    Rp["poses_all"] = dict(ok=not any(pose_hits.values()), poses=len(pose_hits), clean=sum(1 for v in pose_hits.values() if not v),
                           failed={k: v for k, v in pose_hits.items() if v}, rest_pose_hits=rest_hits)
    Rp["pose_top_m"] = tops
    # skeleton vs [meas]
    p, off = solved["stand_aim"]
    set_pose(objs, {k: v for k, v in p.items()}, off)
    hipz = float(objs["J_Hip_L"].matrix_world.translation.z)
    pelz = float(objs["J_Pelvis"].matrix_world.translation.z)
    stand_top = float(max(wverts(o)[:, 2].max() for n, o in meshes.items() if not n.startswith("Rifle") and not n.startswith("Shotgun")))
    rows = {
        "stand_top": (stand_top, R.MEAS["stand_top"]), "hip_z": (hipz, R.MEAS["hip_z"]), "leg_ratio": (hipz / stand_top, R.MEAS["leg_ratio"]),
        "pelvis_z": (pelz, R.MEAS["pelvis_z"]), "thigh": (R.HIP_Z - R.KNEE_Z, R.MEAS["thigh"]), "shin": (R.KNEE_Z - R.ANKLE_Z, R.MEAS["shin"]),
        "ankle_z": (R.ANKLE_Z, R.MEAS["ankle_z"]), "hip_spacing": (2 * R.HIP_Y, R.MEAS["hip_spacing"]),
        "shoulder_spacing (reference only)": (2 * R.SH_Y, R.MEAS["shoulder_spacing"]), "upper_arm": (R.SH_Z - R.ELB_Z, R.MEAS["upper_arm"]),
        "forearm": (R.ELB_Z - R.WR_Z, R.MEAS["forearm"]),
    }
    meas = {k: dict(ours=round(a, 3), meas=b, diff_pct=round(100 * (a - b) / b, 1)) for k, (a, b) in rows.items()}
    Rp["meas_within_5pct"] = dict(ok=all(abs(v["diff_pct"]) <= 5 for k, v in meas.items() if "reference" not in k), rows=meas,
                                  design_reference={"shoulder_w": (round(sw, 2), R.DESIGN["shoulder_w"]), "hip_w": (round(hw, 2), R.DESIGN["hip_w"]),
                                                    "foot_l": (round(fl, 2), R.DESIGN["foot_l"])},
                                  stand_pose="stand_aim with the light legs (hip %g, knee %g), feet levelled, lowest vertex on the ground" % (R.STAND_HIP, R.STAND_KNEE),
                                  note="stand_top without the weapon")
    set_pose(objs, {})
    # sockets / names / slots / origins
    want = MOD.REQUIRED_NAMES
    Rp["sockets"] = dict(ok=all(n in objs for n in want), missing=[n for n in want if n not in objs], count=len([n for n in NODES if n.startswith("S_")]),
                         joints=len([n for n in NODES if n.startswith("J_")]))
    used = sorted({ob.active_material.name for ob in meshes.values()})
    Rp["material_slots"] = dict(ok=used == sorted(SLOT_NAME.values()) and all(len(o.data.materials) == 1 for o in meshes.values()), used=used,
                                area_pct=slot_areas(meshes), target_pct={"MAT_Primary": 60, "MAT_Secondary": 15, "MAT_Frame": 22, "MAT_Emissive": "<=3"})
    off_origin = [n for n, o in meshes.items() if o.location.length > 1e-6 or o.parent.name != o["owner_joint"]]
    Rp["origins_on_joints"] = dict(ok=not off_origin, bad=off_origin, how="every part is parented to its joint with zero local offset, so its origin is the joint")
    # pilot fit (closed hatch, rest) and kneel + hatch open
    shell = [meshes[n] for n in ("Torso_Upper", "Hatch", "Torso_Lower") if n in meshes]
    trees = [tree_of(o) for o in shell]
    pts = pilot_points(objs)
    # a point counts as inside when it is inside the shell or the door, or within 3 cm of their surface (the panel grooves and
    # bevels cut up to 3 cm into the faces where the closed door meets the shell)
    out = [q for q in pts if not any(_inside(t, q) for t in trees) and min((t.find_nearest(Vector(q))[0] - Vector(q)).length for t in trees) > 0.03]
    Rp["pilot_fit"] = dict(ok=not out, points=len(pts), outside=len(out), outside_analysis=[[round(-float(q[1]), 2), round(float(q[0]), 2), round(float(q[2]), 2)] for q in out[:6]], note="reclined 1.8 m pilot capsules, hip at S_Seat, trunk 40 deg back; closed hatch, rest")
    p, off = solved["kneel_hatch"]
    set_pose(objs, dict(p, hatch=120), off)
    hinge = objs["J_Hatch"].matrix_world.translation
    hv = tree_of(meshes["Hatch"])
    pilot_vs_door = sum(1 for q in pilot_points(objs) if _inside(hv, q))
    kneel_hits = collide(meshes)
    op = MOD.hatch_opening()
    Rp["kneel_hatch"] = dict(ok=op["width_m"] >= 0.60 and op["height_m"] >= 0.94 and not kneel_hits and pilot_vs_door == 0,
                             hinge_height_m=round(float(hinge.z), 3), seat_height_m=round(float(objs["S_Seat"].matrix_world.translation.z), 3),
                             opening=op, need="width >= 0.60, height >= 0.94 (seated 1.8 m pilot)", collisions_with_door_open=kneel_hits,
                             pilot_points_inside_open_door=pilot_vs_door)
    set_pose(objs, {})
    Rp["check_seconds"] = round(time.time() - t0, 1)
    return Rp, solved


def pilot_points(objs):
    M = np.array(objs["J_Torso"].matrix_world)
    w = R.WAIST
    pts = []
    for a, b, r, hw in LC.pilot_capsules(MOD.LEAN):
        a, b = np.array(a), np.array(b)
        for t in np.linspace(0, 1, 7):
            c = a + (b - a) * t
            for yy in ([0.0] if hw == 0 else [-hw, 0.0, hw]):
                for dx, dz in ((r, 0), (-r, 0), (0, r), (0, -r)):
                    q = np.array(to_b(c + np.array((dx, yy, dz)) - w) + (1.0,))
                    pts.append((M @ q)[:3])
    return pts


# ------------------------------------------------------------------ rendering
def set_materials(mode, mats):
    for k, m in mats.items():
        g = m["grey"]
        if mode == "sil":
            m.diffuse_color = (0, 0, 0, 1)
        elif mode == "grey":
            m.diffuse_color = (g, g, g, 1)
        else:
            col = hexrgb(MOD.COLORS[k])
            m.diffuse_color = col + (1,)
            m.use_nodes = True
            nt = m.node_tree
            b = nt.nodes.get("Principled BSDF")
            b.inputs["Base Color"].default_value = col + (1,)
            b.inputs["Roughness"].default_value = {"pri": 0.48, "sec": 0.42, "frame": 0.55, "emit": 0.3}[k]
            b.inputs["Metallic"].default_value = {"pri": 0.25, "sec": 0.1, "frame": 0.6, "emit": 0.0}[k]
            if k == "emit":
                b.inputs["Emission Color"].default_value = col + (1,)
                b.inputs["Emission Strength"].default_value = 2.0


def setup(res, mode):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.view_settings.view_transform = "Standard"
    if mode == "color":
        sc.render.engine = "BLENDER_EEVEE"
        sc.world.use_nodes = True
        bg = sc.world.node_tree.nodes.get("Background")
        bg.inputs[0].default_value = (0.78, 0.80, 0.83, 1)
        bg.inputs[1].default_value = 0.55
        sc.view_settings.view_transform = "AgX"
        try:
            sc.eevee.taa_render_samples = 48
            sc.eevee.use_shadows = True
        except AttributeError:
            pass
        return
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.world.color = (1, 1, 1)
    sh = sc.display.shading
    sh.color_type = "MATERIAL"
    if mode == "sil":
        sh.light = "FLAT"
        sh.show_object_outline, sh.show_cavity, sh.show_shadows = False, False, False
    else:
        sh.light = "STUDIO"
        sh.show_object_outline, sh.show_cavity = True, True
        sh.object_outline_color = (0, 0, 0)
        sh.cavity_type = "BOTH"


_cam = None


def camera(loc, target, ortho=None, lens=55):
    global _cam
    if _cam is None:
        _cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
        bpy.context.scene.collection.objects.link(_cam)
    cd = _cam.data
    if ortho:
        cd.type, cd.ortho_scale = "ORTHO", ortho
    else:
        cd.type, cd.lens, cd.sensor_fit = "PERSP", lens, "AUTO"
    cd.clip_start, cd.clip_end = 0.05, 300
    _cam.location = Vector(loc)
    _cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = _cam
    bpy.context.view_layer.update()


def helper(kind, xy=(0, 0)):
    if kind == "human":
        v = [(x * 0.25, y * 0.15, z * 1.8) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.92, 0.38, 0.08, 1)
    elif kind == "ground":
        v = [(x * 14, y * 14, z * 0.02 - 0.02) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.42, 0.43, 0.45, 1)
    else:
        v = [(x * 1.525, y * 1.525, z * 5.97) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.15, 0.45, 0.95, 1)
    md = bpy.data.meshes.new("H_" + kind)
    md.from_pydata(v, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ob = bpy.data.objects.new("H_" + kind, md)
    ob.location = (xy[0], xy[1], 0)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new("H_" + kind)
    m.diffuse_color = rgba
    m.use_nodes = True
    m.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = rgba
    m.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.9
    md.materials.append(m)
    if kind == "collider":
        ob.modifiers.new("wire", "WIREFRAME").thickness = 0.025
    return ob


def clear_helpers():
    for ob in [o for o in bpy.data.objects if o.name.startswith("H_") or o.type == "LIGHT"]:
        bpy.data.objects.remove(ob, do_unlink=True)


def lights():
    for nm, rot, e, size in (("Key", (math.radians(50), 0, math.radians(-35)), 3.2, 0.05), ("Rim", (math.radians(60), 0, math.radians(150)), 2.0, 0.05)):
        ld = bpy.data.lights.new("H_" + nm, "SUN")
        ld.energy = e
        ld.angle = size
        ob = bpy.data.objects.new("H_" + nm, ld)
        ob.rotation_euler = rot
        bpy.context.scene.collection.objects.link(ob)


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


SCALE, ZC = 12.0, 3.1
# camera locations in Blender axes; side view centred a little forward so rifle and wings both fit
ORTHO = {"front": ((0.0, -40, ZC), (0.0, 0.0, ZC), (3.9, 0)), "side": ((40, -0.9, ZC), (0, -0.9, ZC), (0, 3.4)),
         "back": ((0.0, 40, ZC), (0.0, 0.0, ZC), (-3.9, 0))}
Q34 = ((10.5, -14.0, 6.0), (0.0, -0.8, 3.0), (3.6, 1.2))


def render_set(mode, tag, collider=False):
    setup((1000, 1000), mode)
    for name, (loc, tgt, hxy) in ORTHO.items():
        helper("human", hxy)
        if collider:
            helper("collider")
        if mode == "color":
            helper("ground"); lights()
        camera(loc, tgt, ortho=SCALE)
        render(os.path.join(OUT, "%s_%s.png" % (tag, name)))
        clear_helpers()
    helper("human", Q34[2])
    if mode == "color":
        helper("ground"); lights()
    camera(Q34[0], Q34[1], lens=55)
    render(os.path.join(OUT, "%s_3q.png" % tag))
    clear_helpers()


def render_all(objs, meshes, mats, solved):
    p, off = solved["stand_aim"]
    set_pose(objs, p, off)
    set_materials("sil", mats)
    render_set("sil", "sil")
    if STAGE < 4:
        set_materials("grey", mats)
        render_set("grey", "grey", collider=True)
        mode = "grey"
    else:
        set_materials("color", mats)
        render_set("color", "color")
        mode = "color"
    # kneel + hatch open
    p, off = solved["kneel_hatch"]
    set_pose(objs, dict(p, hatch=120), off)
    setup((1000, 1000), mode)
    helper("human", (2.4, -3.0))
    if mode == "color":
        helper("ground"); lights()
    camera((9.5, -12.0, 4.6), (0, -0.8, 2.6), lens=50)
    render(os.path.join(OUT, "%s_kneel_hatch.png" % mode))
    clear_helpers()
    if MOD.HAS_WINGS:
        p, off = solved["stand_aim+wings"]
        set_pose(objs, p, off)
        setup((1000, 1000), mode)
        helper("human", Q34[2])
        if mode == "color":
            helper("ground"); lights()
        camera(Q34[0], Q34[1], lens=55)
        render(os.path.join(OUT, "%s_3q_wings_open.png" % mode))
        camera((0, -40, ZC), (0, 0, ZC), ortho=SCALE)
        render(os.path.join(OUT, "%s_front_wings_open.png" % mode))
        camera((-9.0, 13.0, 7.5), (0, 0.6, 3.6), lens=55)
        render(os.path.join(OUT, "%s_back3q_wings_open.png" % mode))
        clear_helpers()
        p, off = solved["stand_aim"]
        set_pose(objs, p, off)
        setup((1000, 1000), mode)
        if mode == "color":
            helper("ground"); lights()
        camera((-9.0, 13.0, 7.5), (0, 0.6, 3.6), lens=55)
        render(os.path.join(OUT, "%s_back3q_wings_folded.png" % mode))
        clear_helpers()
    extra = getattr(MOD, "extra_renders", None)
    if extra:
        extra(objs, meshes, solved, dict(set_pose=set_pose, setup=setup, helper=helper, lights=lights, camera=camera, render=render,
                                         clear=clear_helpers, out=OUT, mode=mode, solve=lambda h: solve_pose(objs, meshes, h)))
    poses_sheet(objs, meshes, solved, mode)
    set_pose(objs, {})


def poses_sheet(objs, meshes, solved, mode):
    names = [n for n in solved]
    setup((420, 420), "grey" if mode != "color" else "color")
    tiles = []
    txt = bpy.data.curves.new("label", "FONT")
    label = bpy.data.objects.new("Label", txt)
    txt.size = 0.6
    lm = bpy.data.materials.new("H_label")
    lm.diffuse_color = (0, 0, 0, 1)
    lm.use_nodes = True
    lm.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0, 0, 0, 1)
    txt.materials.append(lm)
    bpy.context.scene.collection.objects.link(label)
    if mode == "color":
        helper("ground"); lights()
    for name in names:
        p, off = solved[name]
        set_pose(objs, p, off)
        camera((11.0, -14.5, 6.8), (0, -0.6, 2.9), lens=50)
        txt.body = name
        label.rotation_mode = "QUATERNION"
        label.rotation_quaternion = _cam.rotation_euler.to_quaternion()
        label.location = _cam.matrix_world @ Vector((-4.6, 4.0, -18.5))
        bpy.context.view_layer.update()
        fn = os.path.join(OUT, "_tile.png")
        render(fn)
        im = bpy.data.images.load(fn, check_existing=False)
        w, h = im.size
        tiles.append(np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4))
        bpy.data.images.remove(im)
    clear_helpers()
    bpy.data.objects.remove(label, do_unlink=True)
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    h, w = tiles[0].shape[:2]
    sheet = np.ones((rows * h, cols * w, 4), np.float32)
    for i, t in enumerate(tiles):
        r, c = i // cols, i % cols
        sheet[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = t
    im = bpy.data.images.new("sheet", cols * w, rows * h, alpha=True)
    im.pixels[:] = sheet.ravel().tolist()
    im.filepath_raw = os.path.join(OUT, "poses_sheet.png")
    im.file_format = "PNG"
    im.save()
    os.remove(os.path.join(OUT, "_tile.png"))


# ------------------------------------------------------------------ export
def export(objs):
    set_pose(objs, {})
    for ob in [o for o in bpy.data.objects if o.type not in ("EMPTY", "MESH") or o.name.startswith("H_")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    blend = os.path.join(HERE, "Titan_%s.blend" % CODE)
    fbx = os.path.join(HERE, "Titan_%s.fbx" % CODE)
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                             apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                             add_leaf_bones=False, mesh_smooth_type="FACE")
    want = {n: np.array(to_b(POS[n])) for n in NODES}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx, axis_forward="-Z", axis_up="Y")
    bpy.context.view_layer.update()
    worst, we, missing = None, 0.0, []
    for n, v in want.items():
        ob = bpy.data.objects.get(n)
        if ob is None:
            missing.append(n); continue
        e = float(np.linalg.norm(np.array(ob.matrix_world.translation) - v))
        if e > we:
            worst, we = n, e
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    zs = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
    mats = sorted({s.material.name for o in meshes for s in o.material_slots if s.material})
    return dict(ok=not missing and we <= 0.01, nodes=len(want), worst=worst, worst_m=round(we, 5), missing=missing, meshes=len(meshes),
                mesh_z=[round(min(zs), 3), round(max(zs), 3)], materials=mats, blend=os.path.basename(blend), fbx=os.path.basename(fbx),
                setting="v2 setting: bake_space_transform=False, axis_forward=-Z, axis_up=Y, FBX_SCALE_ALL; Blender re-import only, Unity not run")


def _js(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def main():
    t0 = time.time()
    objs, meshes, mats = build()
    if "nocheck" in FLAGS:
        Rp = {}
        solved = {n: solve_pose(objs, meshes, h) for n, h in R.poses().items()}
        if MOD.HAS_WINGS:
            solved["stand_aim+wings"] = solve_pose(objs, meshes, dict(R.poses()["stand_aim"], wing_L=R.WING_ANGLE, wing_R=R.WING_ANGLE))
    else:
        Rp, solved = run_checks(objs, meshes)
    if STAGE >= 4:
        Rp["stage4_sockets_note"] = "sockets exist from stage 1 on; stage 4 adds colours and the export"
    p, off = solved["stand_aim"]
    set_pose(objs, p, off)
    lo = np.vstack([wverts(o) for o in meshes.values()])
    Rp["stand_aim_extent_blender"] = dict(min=[round(float(x), 3) for x in lo.min(0)], max=[round(float(x), 3) for x in lo.max(0)])
    json.dump(Rp, open(os.path.join(OUT, "checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=_js)
    if "norender" not in FLAGS:
        render_all(objs, meshes, mats, solved)
    set_pose(objs, {})
    if STAGE >= 4:
        set_materials("color", mats)
        Rp["fbx_roundtrip"] = export(objs)
        json.dump(Rp, open(os.path.join(OUT, "checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=_js)
    else:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Titan_%s_r%d.blend" % (CODE, STAGE)))
    print("=== %s stage %d (%.0fs)" % (CODE, STAGE, time.time() - t0))
    for k, v in Rp.items():
        if isinstance(v, dict) and "ok" in v:
            print("   %-26s %s" % (k, "OK" if v["ok"] else "FAIL"))


main()
