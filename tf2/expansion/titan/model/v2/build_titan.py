"""Builds the HSD v2 medium base titan graybox and runs its acceptance checks.

  blender.exe -b -P build_titan.py -- [checks] [render] [export]        no argument = all three

Inputs: ../v2-design/out/spec.json via titan_v2_data.py, part table titan_v2_parts.py.
Outputs: titan_m_base_v2.blend / .fbx, manifest.json, renders/.
Analysis axes (spec, parts): x forward, y left, z up. Blender: X = y, Y = -x, Z up. C below is that rotation.
"""
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
import titan_v2_data as D
import titan_v2_parts as P

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODES = set(args) or {"checks", "render", "export"}
RENDERS = os.path.join(HERE, "renders")
os.makedirs(RENDERS, exist_ok=True)
NAME = "titan_m_base_v2"
TRI_LIMIT = 5000
ROOT = "Titan_M_Base"
C = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)


def to_b(v):
    return (float(v[1]), float(-v[0]), float(v[2]))


def Rx(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


# ------------------------------------------------------------------ scene
def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.context.scene.collection
    mats = {}
    for key, (name, rgba) in D.MATERIALS.items():
        m = bpy.data.materials.new(name)
        m.diffuse_color = rgba
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = rgba
            bsdf.inputs["Roughness"].default_value = 0.8
        mats[key] = m
    objs = {}
    root = bpy.data.objects.new(ROOT, None)
    root.empty_display_size = 0.3
    col.objects.link(root)
    objs[ROOT] = root
    for name, (parent, pos) in D.ALL.items():
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "ARROWS" if name[0] in "JW" else "SPHERE"
        e.empty_display_size = 0.18 if name[0] in "JW" else 0.10
        e.rotation_mode = "QUATERNION"
        col.objects.link(e)
        objs[name] = e
    for name, (parent, pos) in D.ALL.items():
        objs[name].parent = objs[parent]
        ppos = D.ALL[parent][1] if parent != ROOT else (0, 0, 0)
        objs[name].location = to_b(np.array(pos, float) - np.array(ppos, float))
    meshes = {}
    for part in P.PARTS:
        jp = np.array(D.JOINTS[part.joint][1], float)
        md = bpy.data.meshes.new("G_" + part.name)
        # part vertices are joint-local in analysis axes: rotate to Blender axes, the object sits at the joint
        md.from_pydata([to_b(v) for v in part.verts], [], [list(f) for f in part.faces])
        bm = bmesh.new()
        bm.from_mesh(md)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(md)
        bm.free()
        md.update()
        md.materials.append(mats[part.mat])
        ob = bpy.data.objects.new("G_" + part.name, md)
        col.objects.link(ob)
        ob.parent = objs[part.joint]
        ob["owner_joint"] = part.joint
        meshes[part.name] = ob
    bpy.context.view_layer.update()
    return objs, meshes


# ------------------------------------------------------------------ posing. Parameter names are the ones in spec.hand_poses / design.fk.
def local_rotations(p):
    g = lambda k: p.get(k, 0.0)
    out = {
        "J_Pelvis": Rz(g("pel_yaw")) @ Ry(g("pel_pitch")) @ Rx(g("pel_roll")),
        "J_Torso": Rz(g("w_yaw")) @ Ry(g("w_bend")) @ Rx(g("w_side")),
        "J_Hatch": Ry(g("hatch")),
        "J_Optic": Rz(g("op_yaw")) @ Ry(-g("op_pitch")),
        "J_Elbow_L": Ry(-g("e_L")),
        "J_Elbow_R": Ry(-g("e_R")),
        "J_Wrist_L": Ry(g("wr_pitch")) @ Rx(g("wr_side")),
        "J_Finger_L_1": Ry(g("f1")),
        "J_Finger_L_2": Ry(g("f2")),
        "J_Finger_L_3": Ry(-g("f3")),
    }
    for side, sg in (("L", 1), ("R", -1)):
        out["J_Hip_" + side] = Rz(g("h_twist_" + side)) @ Ry(-g("h_flex_" + side)) @ Rx(sg * g("h_out_" + side))
        out["J_Knee_" + side] = Ry(g("k_" + side))
        out["J_Ankle_" + side] = Ry(g("a_" + side)) @ Rx(g("a_roll_" + side))
        out["J_Shoulder_" + side] = Rz(g("s_in_" + side) * -sg) @ Ry(-g("s_flex_" + side)) @ Rx(sg * g("s_out_" + side))
    return out


def set_pose(objs, p, pel_off=(0, 0, 0)):
    rots = local_rotations(p)
    for name in D.JOINTS:
        R = rots.get(name)
        M = C @ R @ C.T if R is not None else np.eye(3)
        objs[name].rotation_quaternion = Matrix(M.tolist()).to_quaternion()
    objs["J_Pelvis"].location = to_b(np.array(D.JA["J_Pelvis"], float) + np.array(pel_off, float))
    bpy.context.view_layer.update()


def world_R_analysis(ob):
    """World rotation of an object, in analysis axes."""
    M = np.array(ob.matrix_world.to_3x3())
    return C.T @ M @ C


def world_pos_analysis(ob):
    w = ob.matrix_world.translation
    return np.array((-w.y, w.x, w.z))


def solve_pose(objs, hand):
    """Same rule as design.solve: level free feet within the ankle limits, then lift so that the lowest spec box corner is on the ground.
    Done on the Blender rig with the spec boxes, so a hierarchy mistake shows up against spec.expected_poses."""
    p = dict(hand)
    set_pose(objs, p)
    for side in "LR":
        if "a_" + side in p:
            continue
        f = world_R_analysis(objs["J_Ankle_" + side]) @ np.array([1.0, 0, 0])
        pitch = math.degrees(math.atan2(-f[2], math.hypot(f[0], f[1])))
        p["a_" + side] = float(np.clip(-pitch, -35, 60))
    set_pose(objs, p)
    low = 1e9
    for part, joint in (("foot_L", "J_Ankle_L"), ("foot_R", "J_Ankle_R"), ("shin_L", "J_Knee_L"), ("shin_R", "J_Knee_R")):
        _, c, h = D.SPEC["parts"][part]
        o, R = world_pos_analysis(objs[joint]), world_R_analysis(objs[joint])
        for a in (-1, 1):
            for b in (-1, 1):
                for e in (-1, 1):
                    low = min(low, (o + R @ (np.array(c, float) + np.array(h, float) * (a, b, e)))[2])
    p["_off"] = (0.0, 0.0, -float(low))
    set_pose(objs, p, p["_off"])
    return p


# ------------------------------------------------------------------ collision, real meshes
class Collider:
    def __init__(self, meshes):
        self.meshes = meshes
        self.names = list(meshes)
        self.local_v = {n: np.array([v.co[:] for v in meshes[n].data.vertices]) for n in self.names}
        self.polys = {n: [list(pl.vertices) for pl in meshes[n].data.polygons] for n in self.names}
        self.owner = {n: meshes[n]["owner_joint"] for n in self.names}
        self.excl = {frozenset((a, b)) for a, b, _ in P.EXCLUDED}

    def check(self):
        """All mesh pairs on different joints, except EXCLUDED. A pair counts if triangles cross or one mesh sits inside the other."""
        W, BB, T = {}, {}, {}
        for n in self.names:
            m = np.array(self.meshes[n].matrix_world)
            v = self.local_v[n] @ m[:3, :3].T + m[:3, 3]
            W[n] = v
            BB[n] = (v.min(0), v.max(0))

        def tree(n):
            if n not in T:
                T[n] = BVHTree.FromPolygons([Vector(x) for x in W[n]], self.polys[n], all_triangles=False)
            return T[n]
        hits = []
        for i, a in enumerate(self.names):
            for b in self.names[i + 1:]:
                if self.owner[a] == self.owner[b] or frozenset((a, b)) in self.excl:
                    continue
                if np.any(BB[a][1] < BB[b][0]) or np.any(BB[b][1] < BB[a][0]):
                    continue
                if tree(a).overlap(tree(b)):
                    hits.append((a, b, self.depth(W, a, b, tree)))
                elif self.inside(tree(b), W[a][0]) or self.inside(tree(a), W[b][0]):
                    hits.append((a, b, self.depth(W, a, b, tree)))
        return hits

    @staticmethod
    def inside(t, pt):
        o = Vector(pt)
        d = Vector((0.0123, 0.0071, 1.0)).normalized()
        n = 0
        for _ in range(64):
            h = t.ray_cast(o, d)
            if h[0] is None:
                break
            n += 1
            o = h[0] + d * 1e-5
        return n % 2 == 1

    def depth(self, W, a, b, tree):
        """Deepest vertex of one mesh inside the other, as a size indication. 0 = only edges cross."""
        best = 0.0
        for x, y in ((a, b), (b, a)):
            t = tree(y)
            for v in W[x]:
                if self.inside(t, v):
                    best = max(best, (t.find_nearest(Vector(v))[0] - Vector(v)).length)
        return round(best, 3)


# ------------------------------------------------------------------ helpers for the checks
def tree_ok(objs):
    want = {n: v[0] for n, v in D.ALL.items()}
    bad = [n for n, par in want.items() if objs[n].parent is None or objs[n].parent.name != par]
    design_tree = {  # DESIGN.md section 3, written out again here so a data-table slip fails
        "J_Pelvis": ROOT, "J_Waist": "J_Pelvis", "J_Torso": "J_Waist", "J_Hatch": "J_Torso", "J_Optic": "J_Torso", "J_Launcher_L": "J_Torso",
        "J_Shoulder_L": "J_Torso", "J_Elbow_L": "J_Shoulder_L", "J_Wrist_L": "J_Elbow_L", "J_Finger_L_1": "J_Wrist_L", "J_Finger_L_2": "J_Wrist_L",
        "J_Finger_L_3": "J_Wrist_L", "S_Hand_L": "J_Wrist_L", "J_Shoulder_R": "J_Torso", "J_Elbow_R": "J_Shoulder_R", "W_Cannon": "J_Elbow_R", "S_Muzzle": "W_Cannon",
        "J_Hip_L": "J_Pelvis", "J_Knee_L": "J_Hip_L", "J_Ankle_L": "J_Knee_L", "J_Hip_R": "J_Pelvis", "J_Knee_R": "J_Hip_R", "J_Ankle_R": "J_Knee_R",
    }
    bad += [n for n, par in design_tree.items() if n not in objs or objs[n].parent is None or objs[n].parent.name != par]
    sockets = ["S_Eye", "S_Seat", "S_Muzzle", "S_Hand_L", "S_Chest", "S_Thrust", "S_Vent_L", "S_Vent_R"] + ["S_Rocket_%d" % i for i in range(1, 7)] + \
        ["S_Dmg_Torso_F", "S_Dmg_Torso_B", "S_Dmg_Shoulder_L", "S_Dmg_Shoulder_R", "S_Dmg_Elbow_L", "S_Dmg_Elbow_R", "S_Dmg_Thigh_L", "S_Dmg_Thigh_R",
         "S_Dmg_Knee_L", "S_Dmg_Knee_R", "S_Foot_L", "S_Foot_R"]
    missing = [s for s in sockets if s not in objs]
    extra = [n for n in D.ALL if n not in design_tree and n not in sockets]
    return dict(ok=not bad and not missing and not extra, wrong_parent=bad, missing_sockets=missing, extra_names=extra, joints=len(D.JOINTS), sockets=len(D.SOCKETS))


def mesh_z_range(ob):
    m = ob.matrix_world
    zs = [(m @ v.co).z for v in ob.data.vertices]
    return min(zs), max(zs)


def limit_cases():
    out = []
    for label, key, lo, hi in D.LIMITS:
        out.append((label, key, lo, hi))
    for label, key, lo, hi in D.LIMITS_SIDED:
        for side in "LR":
            l, h = (lo, hi)
            if key == "h_twist" and side == "R":  # design.fk uses the same axis sense on both sides; the outward limit is mirrored for R
                l, h = -hi, -lo
            out.append(("%s_%s" % (label, side), "%s_%s" % (key, side), l, h))
    out += D.LIMITS_LEFT + D.LIMITS_RIGHT
    return out


def sweep(col, objs, base, base_off, case):
    label, key, lo, hi = case
    res = []
    for frac, val in ((0.5, lo), (1.0, lo), (0.5, hi), (1.0, hi)):
        if val == 0:
            continue
        p = dict(base)
        p[key] = p.get(key, 0.0) * (1 - frac) + val * frac
        set_pose(objs, p, base_off)
        for a, b, d in col.check():
            res.append(dict(limit=label, value=round(p[key], 1), pair=a + " x " + b, depth=d))
    return res


def free_ranges(col, objs, base, off, cases, failed):
    """For each limit that collided: how far the joint really goes from this base pose, in 1 degree steps, and what stops it."""
    names = {h["limit"] for h in failed}
    out = {}
    for label, key, lo, hi in cases:
        if label not in names:
            continue
        start = base.get(key, 0.0)
        row = {}
        for end, tag in ((lo, "low"), (hi, "high")):
            n = int(abs(end - start))
            if n == 0:
                continue
            last, stop = start, None
            for i in range(1, n + 1):
                v = start + (end - start) * i / n
                set_pose(objs, dict(base, **{key: v}), off)
                hits = col.check()
                if hits:
                    stop = hits[0][0] + " x " + hits[0][1]
                    break
                last = v
            if stop:
                row[tag] = dict(limit=end, reaches=round(last, 1), stopped_by=stop)
        if row:
            out[label] = row
    return out


def group_hits(hits):
    """Collapse sweep rows: per limit and pair, keep the largest depth."""
    g = {}
    for h in hits:
        k = (h["limit"], h["pair"])
        if k not in g or h["depth"] > g[k]["depth"]:
            g[k] = h
    return list(g.values())


# ------------------------------------------------------------------ checks
def run_checks(objs, meshes):
    t0 = time.time()
    mf = dict(name=NAME, date="2026-11-02", checks={}, deviations=[], not_passed=[], notes=[])
    tris = 0
    for ob in meshes.values():
        ob.data.calc_loop_triangles()
        tris += len(ob.data.loop_triangles)
    mf["tris"] = tris
    mf["mesh_objects"] = len(meshes)
    mf["checks"]["tris"] = dict(ok=tris <= TRI_LIMIT, tris=tris, limit=TRI_LIMIT)

    # 1 names and tree
    mf["checks"]["hierarchy"] = tree_ok(objs)

    # 2 rest joints
    set_pose(objs, {})
    errs = {n: float(np.linalg.norm(np.array(objs[n].matrix_world.translation) - np.array(v))) for n, v in D.JB.items()}
    worst = max(errs, key=errs.get)
    mf["checks"]["rest_joints"] = dict(ok=errs[worst] <= 0.01, worst=worst, worst_m=round(errs[worst], 5), compared=len(errs))

    # 3 height rules, at rest
    eye = objs["S_Eye"].matrix_world.translation
    feet = min(mesh_z_range(meshes[n])[0] for n in ("Foot_L", "Foot_R"))
    top_name, top = None, -1.0
    for n, ob in meshes.items():
        if n == "Torso_Antenna":
            continue
        z = mesh_z_range(ob)[1]
        if z > top:
            top_name, top = n, z
    ant = mesh_z_range(meshes["Torso_Antenna"])[1]
    mf["checks"]["heights"] = dict(ok=abs(eye.z - 4.70) <= 0.02 and abs(feet) < 1e-4 and top <= 5.97, eye=round(eye.z, 4), feet=round(feet, 4),
                                   top=round(top, 3), top_part=top_name, antenna_top=round(ant, 3), target_top=D.SPEC["shape_targets"]["top"])

    # shape rules, DESIGN section 2, measured on the mesh
    w = meshes["Torso_Shell"]
    tv = [(w.matrix_world @ v.co) for v in w.data.vertices]
    low = [v for v in tv if 3.45 + 0.20 - 1e-4 <= v.z <= 3.45 + 0.70 + 1e-4]
    low_r = max(math.hypot(v.x, v.y + 0.02) for v in low)
    top_w = max(abs(v.x) for v in tv)
    all_torso = [ob.matrix_world @ v.co for n, ob in meshes.items() if ob["owner_joint"] == "J_Torso" and n != "Torso_Antenna" for v in ob.data.vertices]
    ys = [v.y for v in all_torso]
    upper_h = 5.88 - 4.36
    col_ob = meshes["Waist_Column"]
    cz = mesh_z_range(col_ob)
    mf["checks"]["shape_rules"] = dict(
        ok=low_r <= 0.5 + 1e-3 and abs(2 * top_w - 1.84) < 0.02 and abs(max(ys) - min(ys) - 2.04) < 0.06,
        lower_section_radius=round(low_r, 3), lower_section_limit=0.50, upper_width=round(2 * top_w, 3), upper_depth=round(max(ys) - min(ys), 3), upper_height=round(upper_h, 2),
        waist_column_radius=0.32, waist_column_height=round(cz[1] - cz[0], 2), waist_column_exposed=round(3.65 - 3.23, 2), hip_axis=0.86, pelvis_half_width=0.46, shoulder_axis=1.30, cannon_len=2.00)

    # poses: joints against the spec, collision on the real meshes
    col = Collider(meshes)
    pose_err, pose_hits, pose_low, pose_tops = {}, {}, {}, {}
    solved = {}
    for name, hand in D.SPEC["hand_poses"].items():
        p = solve_pose(objs, hand)
        solved[name] = p
        e, r = 0.0, 0.0
        for key, joint in D.POSE_KEYS.items():
            want = D.SPEC["expected_poses"][name][key]
            e = max(e, float(np.linalg.norm(world_pos_analysis(objs[joint]) - np.array(want["o"]))))
            r = max(r, float(np.abs(world_R_analysis(objs[joint]) - np.array(want["R"])).max()))
        pose_err[name] = dict(pos_m=round(e, 5), rot_abs=round(r, 5))
        pose_hits[name] = [dict(pair=a + " x " + b, depth=d) for a, b, d in col.check()]
        zs = [mesh_z_range(ob) for n, ob in meshes.items() if n != "Torso_Antenna"]
        pose_low[name] = round(min(z[0] for z in zs), 3)
        pose_tops[name] = round(max(z[1] for z in zs), 3)
    worst = max(pose_err, key=lambda k: pose_err[k]["pos_m"])
    mf["checks"]["pose_joints"] = dict(ok=pose_err[worst]["pos_m"] <= 0.01, poses=len(pose_err), worst=worst, worst_m=pose_err[worst]["pos_m"],
                                       worst_rot=max(v["rot_abs"] for v in pose_err.values()), per_pose=pose_err)
    bad = {k: v for k, v in pose_hits.items() if v}
    mf["checks"]["collision_poses"] = dict(ok=not bad, poses=len(pose_hits), failed=bad)
    mf["pose_lowest_mesh_z"] = pose_low
    mf["pose_top_z"] = pose_tops

    # joint limits: from the rest pose and from stand_aim
    # arms_clear: arms lifted out to the sides, so a leg, waist or pelvis limit is tested without a rigid arm in its way
    arms_clear = dict(s_out_L=40, s_flex_L=10, e_L=20, s_out_R=40, s_flex_R=10, e_R=20)
    bases = {"rest": ({}, (0, 0, 0)), "stand_aim": ({k: v for k, v in solved["stand_aim"].items() if k != "_off"}, solved["stand_aim"]["_off"]), "arms_clear": (arms_clear, (0, 0, 0))}
    cases = limit_cases()
    lim, reach = {}, {}
    for bname, (base, off) in bases.items():
        rows = []
        for case in cases:
            rows += sweep(col, objs, base, off, case)
        lim[bname] = group_hits(rows)
        reach[bname] = free_ranges(col, objs, base, off, cases, lim[bname])
    mf["checks"]["collision_limits"] = dict(ok=not any(lim.values()), cases=len(cases), bases=list(bases), samples="each limit at 50% and 100%, one joint at a time",
                                            base_arms_clear=arms_clear, failed_rest=lim["rest"], failed_stand_aim=lim["stand_aim"], failed_arms_clear=lim["arms_clear"],
                                            reachable_without_collision=reach)

    # hatch 0-120 every 15 degrees: rest, stand and kneel are required (the door only opens when standing still or kneeling); all 19 as information
    hatch_required, hatch_other = [], []
    for name in ["rest"] + list(solved):
        if name == "rest":
            base, off = {}, (0, 0, 0)
        else:
            base, off = {k: v for k, v in solved[name].items() if k != "_off"}, solved[name]["_off"]
        for deg in range(0, 121, 15):
            p = dict(base, hatch=deg)
            set_pose(objs, p, off)
            for a, b, d in col.check():
                row = dict(pose=name, door_deg=deg, pair=a + " x " + b, depth=d)
                (hatch_required if name in ("rest", "stand_aim", "kneel_hatch") else hatch_other).append(row)
    mf["checks"]["collision_hatch"] = dict(ok=not hatch_required, step_deg=15, required_poses=["rest", "stand_aim", "kneel_hatch"], failed=hatch_required, other_poses_info=hatch_other)
    mf["excluded_pairs"] = [dict(a=a, b=b, reason=r) for a, b, r in P.EXCLUDED]
    mf["collision_method"] = "BVHTree.overlap on world triangles plus inside-test by ray parity. All mesh pairs on different joints are tested (this includes torso x pelvis, thigh x pelvis, forearm x upper arm). No tolerance: touching counts."

    # first person
    mf["checks"]["first_person"] = first_person(objs, meshes, solved["stand_aim"])
    mf["check_seconds"] = round(time.time() - t0, 1)
    return mf, solved


def first_person(objs, meshes, p):
    sc = bpy.context.scene
    set_pose(objs, {k: v for k, v in p.items() if k != "_off"}, p["_off"])
    eye = objs["S_Eye"].matrix_world.translation.copy()
    cd = bpy.data.cameras.new("FP")
    cam = bpy.data.objects.new("FP", cd)
    sc.collection.objects.link(cam)
    cd.sensor_fit = "HORIZONTAL"
    cd.angle_x = math.radians(91)
    cd.clip_start = 0.05
    cam.location = eye
    cam.rotation_euler = Vector((0, -1, 0)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    from bpy_extras.object_utils import world_to_camera_view
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    muzzle = objs["S_Muzzle"].matrix_world.translation
    uvw = world_to_camera_view(sc, cam, muzzle)
    pts = []
    for n in ("Cannon_Body", "Cannon_Barrel"):
        ob = meshes[n]
        pts += [world_to_camera_view(sc, cam, ob.matrix_world @ v.co) for v in ob.data.vertices]
    vis = [q for q in pts if 0 <= q.x <= 1 and 0 <= q.y <= 1 and q.z > 0]
    d = muzzle - eye
    yaw = math.degrees(math.atan2(d.x * -1, -d.y))
    pitch = math.degrees(math.atan2(d.z, -d.y))
    capsule_eye = Vector(D.JB["S_Eye"])
    d2 = muzzle - capsule_eye
    bpy.data.objects.remove(cam, do_unlink=True)
    ok = 0.5 < uvw.x <= 1 and 0 <= uvw.y < 0.5 and uvw.z > 0 and len(vis) > 0
    return dict(ok=ok, muzzle_screen=[round(uvw.x, 3), round(uvw.y, 3)], screen_note="0,0 = lower left, 1,1 = upper right", cannon_verts_in_frame=len(vis), cannon_verts=len(pts),
                muzzle_right_deg=round(yaw, 1), muzzle_down_deg=round(-pitch, 1), design_right_deg=30.0, design_down_deg=17.7, eye_pose_z=round(eye.z, 3),
                from_fixed_capsule_eye=dict(right_deg=round(math.degrees(math.atan2(-d2.x, -d2.y)), 1), down_deg=round(-math.degrees(math.atan2(d2.z, -d2.y)), 1)))


# ------------------------------------------------------------------ renders
def setup_render(res):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.color = (1, 1, 1)
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_object_outline = True
    sh.object_outline_color = (0, 0, 0)
    sh.show_cavity = True
    sc.view_settings.view_transform = "Standard"
    return sc


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
    cd.clip_start, cd.clip_end = 0.05, 200
    _cam.location = Vector(loc)
    _cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = _cam
    bpy.context.view_layer.update()


def add_helper(kind, xy=(0, 0)):
    """1.8 m human block or the 3.05 x 5.97 collider wire."""
    if kind == "human":
        v = [(x * 0.25, y * 0.15, z * 1.8) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.9, 0.35, 0.1, 1)
    else:
        v = [(x * 1.525, y * 1.525, z * 5.97) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.1, 0.4, 0.9, 1)
    md = bpy.data.meshes.new("H_" + kind)
    md.from_pydata(v, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ob = bpy.data.objects.new("H_" + kind, md)
    ob.location = (xy[0], xy[1], 0)
    bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new("H_" + kind)
    m.diffuse_color = rgba
    md.materials.append(m)
    if kind != "human":
        mod = ob.modifiers.new("wire", "WIREFRAME")
        mod.thickness = 0.03
    return ob


def remove_helpers():
    for ob in [o for o in bpy.data.objects if o.name.startswith("H_")]:
        bpy.data.objects.remove(ob, do_unlink=True)


def render_to(name):
    bpy.context.scene.render.filepath = os.path.join(RENDERS, name)
    bpy.ops.render.render(write_still=True)


def silhouette(on):
    sh = bpy.context.scene.display.shading
    if on:
        sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (0, 0, 0)
        sh.show_object_outline, sh.show_cavity = False, False
    else:
        sh.light, sh.color_type = "STUDIO", "MATERIAL"
        sh.show_object_outline, sh.show_cavity = True, True


def render_all(objs, meshes, solved):
    set_pose(objs, {})
    setup_render((888, 900))
    scale, zc = 8.1, 3.5
    views = {"front": ((0, -30), (3.0, 0)), "side_left": ((30, 0), (0, 3.2)), "back": ((0, 30), (-3.0, 0))}
    for name, (off, hp) in views.items():
        add_helper("human", hp)
        add_helper("collider")
        camera((off[0], off[1], zc), (0, 0, zc), ortho=scale)
        render_to("ortho_%s.png" % name)
        remove_helpers()
    setup_render((1200, 1000))
    camera((9.0, -13.0, 5.4), (0, 0, 3.1), lens=60)
    render_to("view_3q.png")
    camera((-9.0, -13.0, 5.4), (0, 0, 3.1), lens=60)
    render_to("view_3q_right.png")
    camera((9.0, 13.0, 6.5), (0, 0, 3.1), lens=60)
    render_to("view_3q_back.png")
    silhouette(True)
    setup_render((888, 900))
    silhouette(True)
    camera((0, -30, zc), (0, 0, zc), ortho=scale)
    render_to("silhouette_front.png")
    camera((30, 0, zc), (0, 0, zc), ortho=scale)
    render_to("silhouette_side.png")
    setup_render((1200, 1000))
    silhouette(True)
    camera((9.0, -13.0, 5.4), (0, 0, 3.1), lens=60)
    render_to("silhouette_3q.png")
    silhouette(False)
    setup_render((1200, 1000))
    p = solved["kneel_hatch"]
    set_pose(objs, dict({k: v for k, v in p.items() if k != "_off"}, hatch=120), p["_off"])
    camera((9.0, -13.0, 4.6), (0, -0.5, 2.5), lens=60)
    render_to("view_kneel_hatch_open.png")

    # first person from S_Eye in stand_aim, torso hidden
    p = solved["stand_aim"]
    set_pose(objs, {k: v for k, v in p.items() if k != "_off"}, p["_off"])
    hidden = [ob for ob in meshes.values() if ob["owner_joint"] in ("J_Torso", "J_Hatch", "J_Optic", "J_Launcher_L")]
    for ob in hidden:
        ob.hide_render = True
    setup_render((1280, 720))
    bpy.context.scene.world.color = (0.62, 0.70, 0.78)
    eye = objs["S_Eye"].matrix_world.translation.copy()
    cd = bpy.data.cameras.new("FPView")
    cam = bpy.data.objects.new("FPView", cd)
    bpy.context.scene.collection.objects.link(cam)
    cd.sensor_fit = "HORIZONTAL"
    cd.angle_x = math.radians(91)
    cd.clip_start = 0.05
    cam.location = eye
    cam.rotation_euler = Vector((0, -1, 0)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    render_to("first_person_stand_aim.png")
    bpy.data.objects.remove(cam, do_unlink=True)
    for ob in hidden:
        ob.hide_render = False
    bpy.context.scene.world.color = (1, 1, 1)

    # 19 poses
    setup_render((440, 440))
    tiles = []
    txt = bpy.data.curves.new("label", "FONT")
    label = bpy.data.objects.new("label", txt)
    txt.size = 0.55
    lm = bpy.data.materials.new("label")
    lm.diffuse_color = (0, 0, 0, 1)
    txt.materials.append(lm)
    bpy.context.scene.collection.objects.link(label)
    target = Vector((0, -0.2, 2.9))
    loc = Vector((9.0, -13.0, 6.2)) * 1.05
    for name, p in solved.items():
        set_pose(objs, {k: v for k, v in p.items() if k != "_off"}, p["_off"])
        camera(loc, target, lens=62)
        txt.body = name
        label.rotation_mode = "QUATERNION"
        label.rotation_quaternion = _cam.rotation_euler.to_quaternion()
        label.location = _cam.matrix_world @ Vector((-3.9, 3.6, -16.5))
        bpy.context.view_layer.update()
        fn = os.path.join(RENDERS, "_tile.png")
        bpy.context.scene.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(fn, check_existing=False)
        w, h = im.size
        a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        tiles.append(a)
        bpy.data.images.remove(im)
    bpy.data.objects.remove(label, do_unlink=True)
    cols, rows = 5, 4
    h, w = tiles[0].shape[:2]
    sheet = np.ones((rows * h, cols * w, 4), np.float32)
    for i, t in enumerate(tiles):
        r, c = i // cols, i % cols
        sheet[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = t
    im = bpy.data.images.new("sheet", cols * w, rows * h, alpha=True)
    im.pixels[:] = sheet.ravel().tolist()
    im.filepath_raw = os.path.join(RENDERS, "poses_19.png")
    im.file_format = "PNG"
    im.save()
    os.remove(os.path.join(RENDERS, "_tile.png"))
    set_pose(objs, {})


# ------------------------------------------------------------------ export and round trip
def export_files(objs):
    set_pose(objs, {})
    for ob in [o for o in bpy.data.objects if o.type not in ("EMPTY", "MESH") or o.name.startswith("H_")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    blend = os.path.join(HERE, NAME + ".blend")
    fbx = os.path.join(HERE, NAME + ".fbx")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    # bake_space_transform=False: baking breaks the empties + parented meshes on re-import, see ../_old-713-base-medium/FBX-ROUNDTRIP.md
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                             apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                             add_leaf_bones=False, mesh_smooth_type="FACE")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx, axis_forward="-Z", axis_up="Y")
    bpy.context.view_layer.update()
    worst, worst_e, missing = None, 0.0, []
    for n, v in D.JB.items():
        ob = bpy.data.objects.get(n)
        if ob is None:
            missing.append(n)
            continue
        e = (ob.matrix_world.translation - Vector(v)).length
        if e > worst_e:
            worst, worst_e = n, e
    zs = [(o.matrix_world @ v.co).z for o in bpy.data.objects if o.type == "MESH" and o.name != "G_Torso_Antenna" for v in o.data.vertices]
    return dict(ok=not missing and worst_e <= 0.01, worst=worst, worst_m=round(worst_e, 5), missing=missing, mesh_z=[round(min(zs), 3), round(max(zs), 3)],
                setting="bake_space_transform=False, axis_forward=-Z, axis_up=Y", note="Blender re-import only. How Unity reads it is not checked.")


# ------------------------------------------------------------------ main
def main():
    objs, meshes = build_scene()
    path = os.path.join(HERE, "manifest.json")
    if "checks" in MODES:
        mf, solved = run_checks(objs, meshes)
    else:
        mf = json.load(open(path, encoding="utf-8"))
        solved = {n: solve_pose(objs, h) for n, h in D.SPEC["hand_poses"].items()}
    extra = os.path.join(HERE, "manifest_notes.json")
    if os.path.exists(extra):
        mf.update(json.load(open(extra, encoding="utf-8")))
    json.dump(mf, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if "render" in MODES:
        render_all(objs, meshes, solved)
    if "export" in MODES:
        mf["checks"]["fbx_roundtrip"] = export_files(objs)
    mf["not_passed"] = [k for k, v in mf["checks"].items() if not v.get("ok")]
    json.dump(mf, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("=== SUMMARY tris", mf["tris"], "failed:", mf["not_passed"])
    for k, v in mf["checks"].items():
        print("  ", k, "OK" if v.get("ok") else "FAIL")


main()
