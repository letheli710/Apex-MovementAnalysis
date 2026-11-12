"""M-1 silhouette draft: basic blocks on the v2 skeleton (joints, hierarchy, poses unchanged), renders and the SPEC.md section 5 checks.

  blender.exe -b -P build_m1_silhouette.py -- m1     build M-1, run checks, render, write silhouette/m1_checks.json and Titan_M1_silhouette.blend
  blender.exe -b -P build_m1_silhouette.py -- v2     open ../../v2/titan_m_base_v2.blend, render the same views for the comparison
  py -3 build_m1_silhouette.py compose               (no Blender) comparison sheet from the two runs

Coordinates in this file are ANALYSIS axes, world rest position (x forward, y left, z up, metres), the same as v2-design/out/spec.json.
Blender axes: X = y, Y = -x, Z up (titan faces -Y), like v2/build_titan.py.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "silhouette")
V2 = os.path.normpath(os.path.join(HERE, "..", "..", "v2"))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
MODE = args[0] if args else "m1"


# ------------------------------------------------------------------ comparison sheet (plain Python + PIL)
def compose():
    from PIL import Image, ImageDraw, ImageFont
    cells = [("v2 正面", "v2_sil_front.png"), ("M-1 正面", "sil_front.png"), ("v2 侧面", "v2_sil_side.png"), ("M-1 侧面", "sil_side.png")]
    ims = [Image.open(os.path.join(OUT, f)).convert("RGB") for _, f in cells]
    box = None
    for im in ims:
        bb = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()
        box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
    box = (box[0] - 15, box[1] - 15, box[2] + 15, box[3] + 10)
    ims = [im.crop(box) for im in ims]  # same window for all four: same camera, same scale
    w, h = ims[0].size
    pad, top = 30, 110
    sheet = Image.new("RGB", (4 * w + 5 * pad, h + top + pad), "white")
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 78)
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(sheet)
    for i, ((label, _), im) in enumerate(zip(cells, ims)):
        x = pad + i * (w + pad)
        sheet.paste(im, (x, top))
        d.text((x + 20, 12), label, fill=(200, 40, 20) if "M-1" in label else (60, 60, 60), font=font)
    sheet.save(os.path.join(OUT, "compare_v2_m1.png"))
    q = sheet.resize((sheet.width // 4, sheet.height // 4), Image.LANCZOS)
    q.save(os.path.join(OUT, "compare_v2_m1_quarter.png"))
    print("sheet", sheet.size, "quarter", q.size)


if MODE == "compose":
    compose()
    sys.exit(0)

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

sys.path.insert(0, V2)
import titan_v2_data as D  # noqa: E402  (only reads v2-design/out/spec.json)

C = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)
J = D.JA  # joint rest positions, analysis axes
ROOT = "Titan_M1"


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


# ------------------------------------------------------------------ posing: copied from v2/build_titan.py (same parameter meaning)
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
        if name not in objs:
            continue
        R = rots.get(name)
        M = C @ R @ C.T if R is not None else np.eye(3)
        objs[name].rotation_quaternion = Matrix(M.tolist()).to_quaternion()
    objs["J_Pelvis"].location = to_b(np.array(J["J_Pelvis"], float) + np.array(pel_off, float))
    bpy.context.view_layer.update()


def world_R_analysis(ob):
    return C.T @ np.array(ob.matrix_world.to_3x3()) @ C


def mesh_objs():
    return [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("H_")]


def lowest_z(names=None):
    z = 1e9
    for o in mesh_objs():
        if names and o.name not in names:
            continue
        m = o.matrix_world
        z = min(z, min((m @ v.co).z for v in o.data.vertices))
    return z


def solve_pose(objs, hand, feet):
    """v2 rule: level free feet within the ankle limits, then put the lowest foot/shin vertex on the ground."""
    p = {k: v for k, v in hand.items() if not k.startswith("_")}
    set_pose(objs, p)
    for side in "LR":
        if "a_" + side in p:
            continue
        f = world_R_analysis(objs["J_Ankle_" + side]) @ np.array([1.0, 0, 0])
        pitch = math.degrees(math.atan2(-f[2], math.hypot(f[0], f[1])))
        p["a_" + side] = float(np.clip(-pitch, -35, 60))
    set_pose(objs, p)
    off = (0.0, 0.0, -lowest_z(feet))
    set_pose(objs, p, off)
    return p, off


# ------------------------------------------------------------------ primitives (world rest coords, analysis axes)
def poly8(xf, xb, wf, wb, c, yc=0.0):
    """Top-view outline: front edge at x=xf half-width wf, back edge at x=xb half-width wb, corners cut by c. CCW."""
    return [(xf, yc - wf + c), (xf, yc + wf - c), (xf - c, yc + wf), (xb + c, yc + wb),
            (xb, yc + wb - c), (xb, yc - wb + c), (xb + c, yc - wb), (xf - c, yc - wf)]


def rect(x0, x1, y0, y1, c=0.06):
    return [(x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c), (x0 + c, y0), (x1 - c, y0)]


def loft(sections):
    """Closed solid through horizontal sections [(z, [(x, y) ...]), ...], every section the same point count."""
    vs, faces = [], []
    n = len(sections[0][1])
    for z, pts in sections:
        vs += [(x, y, z) for x, y in pts]
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple(range(n * (len(sections) - 1), n * len(sections))))
    for s in range(len(sections) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((s * n + i, s * n + j, (s + 1) * n + j, (s + 1) * n + i))
    return vs, faces


def cyl(axis, c, r, a0, a1, seg=16):
    """Cylinder along 'x', 'y' or 'z' through centre c (the other two coords in x, y, z order), from a0 to a1 on the axis."""
    vs = []
    for a in (a0, a1):
        for i in range(seg):
            t = 2 * math.pi * i / seg
            u, v = r * math.cos(t), r * math.sin(t)
            vs.append({"x": (a, c[0] + u, c[1] + v), "y": (c[0] + v, a, c[1] + u), "z": (c[0] + u, c[1] + v, a)}[axis])
    faces = [tuple(reversed(range(seg))), tuple(range(seg, 2 * seg))]
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((i, j, seg + j, seg + i))
    return vs, faces


def merge(*meshes):
    vs, fs = [], []
    for v, f in meshes:
        o = len(vs)
        vs += v
        fs += [tuple(i + o for i in x) for x in f]
    return vs, fs


def mirror(mesh):
    v, f = mesh
    return [(x, -y, z) for x, y, z in v], [tuple(reversed(x)) for x in f]


# ------------------------------------------------------------------ M-1 blocks. (name, joint, material slot, mesh)
# Round 2 (user review 11-12): seat raised + pilot reclined, so the hatch hinge moves forward onto the chest prow.
# These are the only rig positions that differ from v2. Everything else is v2 spec.json.
M1_MOVED = {
    "J_Hatch": (1.42, 0.0, 4.30),   # v2 (0.95, 0, 4.15)
    "S_Seat": (0.55, 0.0, 4.28),    # v2 (0.25, 0, 3.92): raised 0.36, pilot reclined 40 deg
    "S_Chest": None,                # set below to the emitter centre (v2 (1.05, 0, 4.75))
}
HATCH_SLOPE = 0.49                  # hatch leans back 0.49 m per metre of height (26 deg from vertical)
EMIT_Z = 4.80
EMIT_X = 1.42 + 0.10 - (EMIT_Z - 4.30) * HATCH_SLOPE   # hatch outer face at EMIT_Z
M1_MOVED["S_Chest"] = (round(EMIT_X, 3), 0.0, EMIT_Z)
# reclined 1.8 m pilot as capsules (a, b, radius, half-width in y) in torso rest coordinates, hip at S_Seat
PILOT = [((0.55, 0.0, 4.28), (0.20, 0.0, 4.70), 0.13, 0.20),   # trunk, leaning back 40 deg
         ((0.06, 0.0, 4.86), (0.06, 0.0, 4.86), 0.12, 0.0),    # head
         ((0.55, 0.0, 4.28), (0.95, 0.0, 4.50), 0.09, 0.15),   # thighs
         ((0.95, 0.0, 4.50), (1.24, 0.0, 4.25), 0.07, 0.15)]   # shins


def ring_y(prof, cx, cz, seg=16):
    """Solid of revolution about a y axis through (cx, cz): prof = [(y, radius), ...]."""
    vs, fs = [], []
    for y, r in prof:
        vs += [(cx + r * math.cos(2 * math.pi * i / seg), y, cz + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    fs.append(tuple(range(seg)))
    fs.append(tuple(reversed(range(seg * (len(prof) - 1), seg * len(prof)))))
    for k in range(len(prof) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            fs.append((k * seg + j, k * seg + i, (k + 1) * seg + i, (k + 1) * seg + j))
    return vs, fs


def rot_y(mesh, deg, c):
    """Rotate about a y axis through c; positive turns +x toward +z."""
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    v, f = mesh
    return [(c[0] + (x - c[0]) * ca - (z - c[2]) * sa, y, c[2] + (x - c[0]) * sa + (z - c[2]) * ca) for x, y, z in v], f


def m1_parts():
    P = []
    add = lambda n, j, m, mesh: P.append((n, j, m, mesh))
    axle = loft([(2.72, rect(-0.15, 0.15, 0.40, 0.50, 0.05)), (2.98, rect(-0.15, 0.15, 0.40, 0.50, 0.05))])
    # pelvis with a collar (hip skirt) around the waist drum: high at the back and sides, sloped low at the front for the 45 deg bend
    add("Pelvis", "J_Pelvis", "frame", merge(
        loft([(2.70, rect(-0.36, 0.28, -0.40, 0.40, 0.10)), (2.95, rect(-0.44, 0.36, -0.46, 0.46, 0.12)),
              (3.12, rect(-0.50, 0.34, -0.46, 0.46, 0.14)), (3.27, rect(-0.50, 0.24, -0.34, 0.34, 0.12)),
              (3.35, rect(-0.48, -0.04, -0.26, 0.26, 0.10))]),
        axle, mirror(axle)))
    # waist drum: rides J_Waist (does not turn), torso turns over it
    add("Waist", "J_Waist", "sec", cyl("z", (0, 0), 0.40, 3.20, 3.66, 12))
    # torso lower: radius <= 0.50 between the thighs (v2 DESIGN shape rule 2), coned at the bottom for the 45 deg bend
    add("Torso_Lower", "J_Torso", "pri", loft([(3.61, rect(-0.36, 0.36, -0.36, 0.36, 0.12)), (3.76, rect(-0.48, 0.48, -0.48, 0.48, 0.16)),
                                                (4.12, rect(-0.50, 0.50, -0.50, 0.50, 0.16))]))
    # torso upper: wedge. Front view: widest at the shoulder line, narrowing down. Side view: chest prow forward at 4.1-4.4,
    # sloped front face (the hatch) back up to the top, top 5.70.
    add("Torso_Upper", "J_Torso", "pri", loft([(4.12, poly8(1.35, -0.55, 0.62, 0.55, 0.16)), (4.40, poly8(1.40, -0.95, 0.72, 0.98, 0.18)),
                                                (5.40, poly8(0.88, -0.98, 0.80, 1.00, 0.18)), (5.70, poly8(0.72, -0.92, 0.70, 0.82, 0.16))]))
    # hatch: one plate on the sloped face, hinge at its lower edge (J_Hatch), 1.10 wide, 1.00 high (1.11 along the slope)
    hx = lambda z: 1.42 - (z - 4.30) * HATCH_SLOPE
    add("Hatch", "J_Hatch", "pri", loft([(4.30, rect(hx(4.30), hx(4.30) + 0.10, -0.55, 0.55, 0.05)),
                                         (5.30, rect(hx(5.30), hx(5.30) + 0.10, -0.55, 0.55, 0.05))]))
    # emitter: smaller (core 0.44 inside a dark grille ring 0.72), faces along the hatch normal
    tilt = math.degrees(math.atan(HATCH_SLOPE))
    c = (EMIT_X, 0.0, EMIT_Z)
    ring = cyl("x", (0, EMIT_Z), 0.36, EMIT_X - 0.02, EMIT_X + 0.03, 24)
    core = cyl("x", (0, EMIT_Z), 0.22, EMIT_X - 0.02, EMIT_X + 0.035, 24)
    add("Emitter_Grille", "J_Hatch", "frame", rot_y(ring, tilt, c))
    add("Emitter_Core", "J_Hatch", "emit", rot_y(core, tilt, c))
    # sensor slit 0.60 x 0.12 on J_Optic (z 5.40), on the sloped face above the hatch
    add("Optic_Slit", "J_Optic", "emit", loft([(5.34, rect(0.84, 0.95, -0.30, 0.30, 0.02)), (5.46, rect(0.81, 0.92, -0.30, 0.30, 0.02))]))
    # shoulder blocks: solid, fixed to the torso. Top flat 5.44 continues the torso's top line; over the arm hub the underside
    # is 4.98 (0.46 thick) and the hub fills the space below it; outside the hub the block runs down as a solid wedge to 4.78
    # (0.66 thick), its underside sloping away from the hub so the arm can still go 30 deg out.
    blk = loft([(4.78, rect(-0.50, 0.48, 1.80, 1.92, 0.05)), (4.97, rect(-0.60, 0.56, 1.58, 1.95, 0.08)),
                (4.98, rect(-0.64, 0.60, 0.90, 1.95, 0.10)), (5.26, rect(-0.66, 0.62, 0.90, 1.95, 0.10)),
                (5.44, rect(-0.62, 0.56, 0.90, 1.72, 0.10))])
    # rear skirt: closes the gap over the arm hub in the front view; sits behind the hub (x <= -0.40), out of the arm's swing
    blk = merge(blk, loft([(4.66, rect(-0.64, -0.42, 0.96, 1.66, 0.04)), (4.99, rect(-0.64, -0.42, 0.96, 1.66, 0.04))]))
    add("Shoulder_L", "J_Torso", "sec", blk)
    add("Shoulder_R", "J_Torso", "sec", mirror(blk))
    # upper arm + shoulder hub: the hub is a drum on the arm's swing axis (y), so swinging the arm forward never lifts it.
    # Radius 0.34 in the middle, 0.24 at the ends so it still clears the block with the arm 30 deg out (landing poses).
    hub = ring_y([(1.04, 0.24), (1.16, 0.34), (1.44, 0.34), (1.56, 0.24)], 0.0, 4.55)
    uparm = merge(hub, loft([(4.45, rect(-0.26, 0.26, 1.06, 1.54, 0.08)), (3.86, rect(-0.22, 0.22, 1.09, 1.51, 0.07))]))
    add("UpperArm_L", "J_Shoulder_L", "frame", uparm)
    add("UpperArm_R", "J_Shoulder_R", "frame", mirror(uparm))
    add("Forearm_L", "J_Elbow_L", "pri", loft([(3.78, rect(-0.22, 0.22, 1.10, 1.50, 0.07)), (3.20, rect(-0.28, 0.28, 1.05, 1.55, 0.09)),
                                               (2.92, rect(-0.24, 0.24, 1.08, 1.52, 0.08))]))
    add("Hand_L", "J_Wrist_L", "frame", loft([(2.90, rect(-0.24, 0.24, 1.09, 1.51, 0.07)), (2.40, rect(-0.19, 0.19, 1.13, 1.47, 0.06))]))
    add("Cannon", "W_Cannon", "pri", loft([(3.80, rect(-0.26, 0.30, -1.57, -1.03, 0.08)), (2.62, rect(-0.30, 0.30, -1.60, -1.00, 0.09)),
                                           (2.46, rect(-0.17, 0.17, -1.47, -1.13, 0.06)), (1.65, rect(-0.15, 0.15, -1.45, -1.15, 0.05))]))
    add("Pod_L", "J_Launcher_L", "sec", loft([(5.52, rect(-0.86, 0.04, 0.24, 0.96, 0.06)), (5.92, rect(-0.80, 0.04, 0.28, 0.96, 0.06))]))
    thigh = loft([(3.10, rect(-0.24, 0.24, 0.72, 1.12, 0.08)), (2.95, rect(-0.31, 0.31, 0.61, 1.16, 0.10)), (2.70, rect(-0.32, 0.32, 0.61, 1.16, 0.10)),
                  (1.75, rect(-0.25, 0.25, 0.64, 1.09, 0.08))])  # inner edge 0.61 = v2 DESIGN rule (thighs sweep past the torso)
    add("Thigh_L", "J_Hip_L", "pri", thigh)
    add("Thigh_R", "J_Hip_R", "pri", mirror(thigh))
    shin = loft([(1.72, rect(-0.26, 0.36, 0.59, 1.13, 0.08)), (1.15, rect(-0.38, 0.42, 0.52, 1.20, 0.12)),
                 (0.86, rect(-0.30, 0.32, 0.58, 1.14, 0.10))])
    add("Shin_L", "J_Knee_L", "pri", shin)
    add("Shin_R", "J_Knee_R", "pri", mirror(shin))
    foot = loft([(0.00, rect(-0.57, 0.62, 0.40, 1.32, 0.08)), (0.38, rect(-0.50, 0.50, 0.44, 1.28, 0.08)),
                 (0.80, rect(-0.24, 0.26, 0.60, 1.12, 0.06))])
    add("Foot_L", "J_Ankle_L", "frame", foot)
    add("Foot_R", "J_Ankle_R", "frame", mirror(foot))
    toe = loft([(0.00, rect(0.55, 1.13, 0.42, 1.30, 0.06)), (0.30, rect(0.55, 0.95, 0.46, 1.26, 0.06))])
    add("Toe_L", "J_Ankle_L", "sec", toe)
    add("Toe_R", "J_Ankle_R", "sec", mirror(toe))
    return P


# pairs that touch on purpose (joint hubs, plates sitting on a surface). Everything else is tested.
EXCLUDED = {frozenset(p) for p in [
    ("Pelvis", "Waist"), ("Waist", "Torso_Lower"), ("Hatch", "Torso_Upper"), ("Hatch", "Torso_Lower"), ("Optic_Slit", "Torso_Upper"),
    ("Pod_L", "Torso_Upper"), ("Pod_L", "Shoulder_L"), ("UpperArm_L", "Forearm_L"), ("Forearm_L", "Hand_L"), ("UpperArm_R", "Cannon"),
    ("Thigh_L", "Shin_L"), ("Thigh_R", "Shin_R"), ("Shin_L", "Foot_L"), ("Shin_R", "Foot_R"),
    ("Emitter_Grille", "Torso_Upper"), ("Emitter_Core", "Torso_Upper"),
    ("Shoulder_L", "UpperArm_L"), ("Shoulder_R", "UpperArm_R"),  # reported separately (plate_arm)
]}


GREY = {"pri": 0.78, "sec": 0.42, "frame": 0.22, "emit": 0.97}


def build_m1():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.context.scene.collection
    mats = {}
    for k, g in GREY.items():
        m = bpy.data.materials.new("MAT_" + {"pri": "Primary", "sec": "Secondary", "frame": "Frame", "emit": "Emissive"}[k])
        m.diffuse_color = (g, g, g, 1)
        mats[k] = m
    objs = {ROOT: bpy.data.objects.new(ROOT, None)}
    col.objects.link(objs[ROOT])
    for name, (parent, pos) in D.JOINTS.items():
        if name.startswith("J_Finger"):
            continue
        e = bpy.data.objects.new(name, None)
        e.rotation_mode = "QUATERNION"
        e.empty_display_size = 0.15
        col.objects.link(e)
        objs[name] = e
    for name, e in objs.items():
        if name == ROOT:
            continue
        parent, pos = D.JOINTS[name]
        pos = M1_MOVED.get(name, pos)
        root = parent not in D.JOINTS
        e.parent = objs[ROOT] if root else objs[parent]
        ppos = (0, 0, 0) if root else M1_MOVED.get(parent, D.JOINTS[parent][1])
        e.location = to_b(np.array(pos, float) - np.array(ppos, float))
    meshes = {}
    for name, joint, mat, (vs, fs) in m1_parts():
        jp = np.array(M1_MOVED.get(joint, J[joint] if joint in J else D.JOINTS[joint][1]), float)
        md = bpy.data.meshes.new("M1_" + name)
        md.from_pydata([to_b(np.array(v) - jp) for v in vs], [], [list(f) for f in fs])
        md.validate()
        md.update()
        md.materials.append(mats[mat])
        ob = bpy.data.objects.new("M1_" + name, md)
        col.objects.link(ob)
        ob.parent = objs[joint]
        ob["owner_joint"] = joint
        ob["slot"] = mat
        meshes[name] = ob
    bpy.context.view_layer.update()
    return objs, meshes


# ------------------------------------------------------------------ checks
def world_verts(ob):
    m = np.array(ob.matrix_world)
    v = np.array([x.co[:] for x in ob.data.vertices])
    return v @ m[:3, :3].T + m[:3, 3]


def collide(meshes):
    W = {n: world_verts(o) for n, o in meshes.items()}
    T = {n: BVHTree.FromPolygons([Vector(x) for x in W[n]], [list(p.vertices) for p in o.data.polygons]) for n, o in meshes.items()}
    names = list(meshes)
    hits = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if meshes[a]["owner_joint"] == meshes[b]["owner_joint"] or frozenset((a, b)) in EXCLUDED:
                continue
            if T[a].overlap(T[b]):
                hits.append(a + " x " + b)
    return hits


def pair_overlap(meshes, a, b):
    ta = BVHTree.FromPolygons([Vector(x) for x in world_verts(meshes[a])], [list(p.vertices) for p in meshes[a].data.polygons])
    tb = BVHTree.FromPolygons([Vector(x) for x in world_verts(meshes[b])], [list(p.vertices) for p in meshes[b].data.polygons])
    return bool(ta.overlap(tb))


def _inside(tree, pt):
    o = Vector(pt); d = Vector((0.0123, 0.0071, 1.0)).normalized(); n = 0
    for _ in range(64):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        n += 1
        o = h[0] + d * 1e-5
    return n % 2 == 1


def pilot_points(objs):
    """Sample points on the reclined pilot capsules, posed with J_Torso (rest coords -> world)."""
    M = objs["J_Torso"].matrix_world
    w = np.array(J["J_Waist"], float)
    pts = []
    for a, b, r, hw in PILOT:
        a, b = np.array(a), np.array(b)
        for t in np.linspace(0, 1, 7):
            c = a + (b - a) * t
            for yy in ([0.0] if hw == 0 else [-hw, 0.0, hw]):
                for dx, dz in ((r, 0), (-r, 0), (0, r), (0, -r)):
                    q = c + np.array((dx, yy, dz))
                    pts.append(np.array(M @ Vector(to_b(q - w))))
    return pts


def pilot_fit(meshes):
    shell = [n for n in ("Torso_Upper", "Torso_Lower", "Hatch")]
    trees = [BVHTree.FromPolygons([Vector(x) for x in world_verts(meshes[n])], [list(p.vertices) for p in meshes[n].data.polygons]) for n in shell]
    pts = pilot_points({"J_Torso": meshes["Torso_Upper"].parent})
    out = [p for p in pts if not any(_inside(t, p) for t in trees)]
    worst = max(out, key=lambda p: p[1] * -1) if out else None
    return dict(ok=not out, points=len(pts), outside=len(out),
                note="reclined pilot capsules (hip at S_Seat, trunk 40 deg back) sampled at rest, closed hatch; points must be inside torso + hatch",
                example_outside_blender=[round(float(x), 3) for x in worst] if worst is not None else None)


def pilot_hits_part(meshes, objs, part):
    t = BVHTree.FromPolygons([Vector(x) for x in world_verts(meshes[part])], [list(p.vertices) for p in meshes[part].data.polygons])
    pts = pilot_points({"J_Torso": meshes["Torso_Upper"].parent})
    return sum(1 for p in pts if _inside(t, p))


def extents(meshes, skip=()):
    v = np.vstack([world_verts(o) for n, o in meshes.items() if n not in skip])
    return v.min(0), v.max(0)  # Blender axes


def run_checks(objs, meshes):
    R = {}
    set_pose(objs, {})
    lo, hi = extents(meshes)
    H = float(hi[2])
    R["rest_top_m"] = round(H, 3)
    R["rest_top_part"] = max(meshes, key=lambda n: world_verts(meshes[n])[:, 2].max())
    # shoulder width = outer x extent of the shoulder plates; hip width = outer x extent at hip-joint height (thighs) in the front view
    sh = np.vstack([world_verts(meshes[n]) for n in ("Shoulder_L", "Shoulder_R")])
    hip = np.vstack([world_verts(meshes[n]) for n in ("Thigh_L", "Thigh_R", "Pelvis")])
    hip = hip[(hip[:, 2] > 2.60) & (hip[:, 2] < 3.15)]
    sw, hw = float(sh[:, 0].max() - sh[:, 0].min()), float(hip[:, 0].max() - hip[:, 0].min())
    R["shoulder_width_m"], R["hip_width_m"] = round(sw, 3), round(hw, 3)
    R["shoulder_ge_hip_x1.5"] = dict(ok=sw >= 1.5 * hw, ratio=round(sw / hw, 3), need=round(1.5 * hw, 3))
    pel_top = float(world_verts(meshes["Pelvis"])[:, 2].max())
    tor_bot = float(world_verts(meshes["Torso_Lower"])[:, 2].min())
    wh = tor_bot - pel_top
    R["waist_le_height_x0.06"] = dict(ok=wh <= 0.06 * H, waist_visible_m=round(wh, 3), limit_m=round(0.06 * H, 3),
                                      how="gap between pelvis top and torso-lower bottom at rest (the drum shows there)")
    f = world_verts(meshes["Foot_L"]); t = world_verts(meshes["Toe_L"])
    fl = float(max(f[:, 1].max(), t[:, 1].max()) - min(f[:, 1].min(), t[:, 1].min()))
    R["foot_ge_height_x0.22"] = dict(ok=fl >= 0.22 * H, foot_len_m=round(fl, 3), need_m=round(0.22 * H, 3))
    # girth: thigh vs shin, largest section width x depth
    def girth(n):
        v = world_verts(meshes[n]); return float((v[:, 0].max() - v[:, 0].min()) * (v[:, 1].max() - v[:, 1].min()))
    R["calf_ge_thigh"] = dict(ok=girth("Shin_L") >= girth("Thigh_L"), thigh_area_m2=round(girth("Thigh_L"), 3), shin_area_m2=round(girth("Shin_L"), 3),
                              how="bounding section width x depth at rest")
    R["top_le_collider_5.97"] = dict(ok=H <= 5.97, rest_top_m=round(H, 3))
    # waist bend limits (DESIGN.md: bend -25..45, side +-30): torso-lower must clear the pelvis
    bend = {}
    for k, v in (("bend_45", {"w_bend": 45}), ("bend_-25", {"w_bend": -25}), ("side_30", {"w_side": 30}), ("side_-30", {"w_side": -30}),
                 ("yaw_90_bend_45", {"w_yaw": 90, "w_bend": 45})):
        set_pose(objs, v)
        bend[k] = not pair_overlap(meshes, "Torso_Lower", "Pelvis")
    R["waist_bend_clear"] = dict(ok=all(bend.values()), cases=bend)
    # the 19 v2 poses: block collisions (info only at silhouette stage)
    feet = {"M1_Foot_L", "M1_Foot_R", "M1_Toe_L", "M1_Toe_R", "M1_Shin_L", "M1_Shin_R"}
    poses, tops, plate_arm = {}, {}, {}
    solved = {}
    for name, hand in D.SPEC["hand_poses"].items():
        p, off = solve_pose(objs, hand, feet)
        solved[name] = (p, off)
        poses[name] = collide(meshes)
        tops[name] = round(float(extents(meshes)[1][2]), 3)
        plate_arm[name] = [s for s in "LR" if pair_overlap(meshes, "Shoulder_" + s, "UpperArm_" + s)]
    set_pose(objs, {})
    plate_arm["rest"] = [s for s in "LR" if pair_overlap(meshes, "Shoulder_" + s, "UpperArm_" + s)]
    R["pose_collisions_info"] = {k: v for k, v in poses.items() if v}
    R["pose_clean"] = sum(1 for v in poses.values() if not v)
    R["pose_top_m"] = tops
    R["plate_vs_upper_arm"] = {k: v for k, v in plate_arm.items() if v}
    R["pilot_fit"] = pilot_fit(meshes)
    # kneel + hatch 120: sill (hinge) height, opening size, seated pilot
    p, off = solved["kneel_hatch"]
    set_pose(objs, dict(p, hatch=120), off)
    hinge = objs["J_Hatch"].matrix_world.translation
    hv = world_verts(meshes["Hatch"])
    R["kneel_hatch"] = dict(
        hinge_height_m=round(float(hinge.z), 3),
        opening_w_m=1.10, opening_h_m=round(1.0 * math.hypot(1, HATCH_SLOPE), 3),
        seated_pilot_needs="1.8 m pilot: shoulders 0.50 wide, sitting height 0.94 m (0.52 x stature); standing block 0.5 x 0.3 x 1.8",
        opening_ok_for_seated=bool(1.10 >= 0.50 + 0.10 and 1.0 * math.hypot(1, HATCH_SLOPE) >= 0.94),
        standing_block_fits=False,
        hatch_lowest_m=round(float(hv[:, 2].min()), 3),
        torso_top_m=round(float(world_verts(meshes["Torso_Upper"])[:, 2].max()), 3),
        seat_height_m=round(float((objs["J_Torso"].matrix_world @ Vector(to_b(np.array(M1_MOVED["S_Seat"]) - np.array(J["J_Waist"])))).z), 3),
        pilot_vs_open_hatch=pilot_hits_part(meshes, objs, "Hatch"),
    )
    set_pose(objs, {})
    return R, solved


# ------------------------------------------------------------------ rendering
def setup_render(res, mode):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.color = (1, 1, 1)
    sc.view_settings.view_transform = "Standard"
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


def set_colors(mode):
    for m in bpy.data.materials:
        if m.name.startswith("H_"):
            continue
        if mode == "sil":
            m.diffuse_color = (0, 0, 0, 1)
        else:
            g = m.get("grey")
            if g is not None:
                m.diffuse_color = (g, g, g, 1)


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


def helper(kind, xy=(0, 0)):
    if kind == "human":
        v = [(x * 0.25, y * 0.15, z * 1.8) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.92, 0.38, 0.08, 1)
    elif kind == "ground":
        v = [(x * 6, y * 6, z * 0.02 - 0.02) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.55, 0.55, 0.55, 1)
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
    md.materials.append(m)
    if kind == "collider":
        ob.modifiers.new("wire", "WIREFRAME").thickness = 0.025
    return ob


def clear_helpers():
    for ob in [o for o in bpy.data.objects if o.name.startswith("H_")]:
        bpy.data.objects.remove(ob, do_unlink=True)


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


SCALE, ZC = 9.6, 3.2
# Blender axes. human block placed beside the titan, not in front of it
ORTHO = {"front": ((0, -40, ZC), (3.4, 0)), "side": ((40, 0, ZC), (0, 3.6)), "back": ((0, 40, ZC), (-3.4, 0))}
Q34 = ((9.0, -12.5, 5.2), (0.2, -0.3, 2.9), (3.3, 0.6))


def render_views(prefix, kinds, collider):
    for mode in kinds:
        set_colors(mode)
        setup_render((1000, 1000), mode)
        tag = "sil" if mode == "sil" else "grey"
        for name, (loc, hxy) in ORTHO.items():
            helper("human", hxy)
            if mode != "sil" and collider:
                helper("collider")
            camera(loc, (0, 0, ZC), ortho=SCALE)
            render(os.path.join(OUT, "%s%s_%s.png" % (prefix, tag, name)))
            clear_helpers()
        if prefix == "":
            helper("human", Q34[2])
            setup_render((1000, 1000), mode)
            camera(Q34[0], Q34[1], lens=62)
            render(os.path.join(OUT, "%s_3q.png" % tag))
            clear_helpers()


def main_m1():
    os.makedirs(OUT, exist_ok=True)
    objs, meshes = build_m1()
    for m in bpy.data.materials:
        for k, g in GREY.items():
            if m.name == "MAT_" + {"pri": "Primary", "sec": "Secondary", "frame": "Frame", "emit": "Emissive"}[k]:
                m["grey"] = g
    R, solved = run_checks(objs, meshes)
    R["blocks"] = len(meshes)
    R["block_kinds"] = len({n.replace("_L", "").replace("_R", "") for n in meshes})
    R["pose_rendered"] = "stand_aim (v2 hand pose, feet levelled, lowest foot vertex on the ground)"
    p, off = solved["stand_aim"]
    set_pose(objs, p, off)
    lo, hi = extents(meshes)
    R["stand_aim_extent_blender"] = dict(min=[round(float(x), 3) for x in lo], max=[round(float(x), 3) for x in hi])
    json.dump(R, open(os.path.join(OUT, "m1_checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    render_views("", ("sil", "grey"), True)
    set_pose(objs, dict(solved["kneel_hatch"][0], hatch=120), solved["kneel_hatch"][1])
    set_colors("grey")
    helper("human", (2.6, -2.6))
    setup_render((1000, 1000), "grey")
    camera((9.5, -12.0, 4.2), (0, -0.6, 2.4), lens=50)
    render(os.path.join(OUT, "grey_kneel_hatch.png"))
    clear_helpers()
    set_pose(objs, {})
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "Titan_M1_silhouette.blend"))
    print("=== M1 CHECKS", json.dumps({k: (v.get("ok") if isinstance(v, dict) and "ok" in v else None) for k, v in R.items()}))


def main_v2():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(V2, "titan_m_base_v2.blend"))
    for o in list(bpy.data.objects):
        if o.type in ("CAMERA", "LIGHT") or o.name.startswith("H_"):
            bpy.data.objects.remove(o, do_unlink=True)
    objs = {o.name: o for o in bpy.data.objects if o.type == "EMPTY"}
    feet = {o.name for o in mesh_objs() if any(k in o.name for k in ("Foot", "Shin", "Ankle"))}
    p, off = solve_pose(objs, D.SPEC["hand_poses"]["stand_aim"], feet)
    render_views("v2_", ("sil",), False)
    print("=== V2 rendered, ground offset", off)


if MODE == "m1":
    main_m1()
elif MODE == "v2":
    main_v2()
