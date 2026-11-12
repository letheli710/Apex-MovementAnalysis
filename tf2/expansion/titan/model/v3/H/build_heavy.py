"""Heavy titans H-1 Forge / H-2 Legion: build in Blender, run the SPEC.md section 5 checks, render, export.

  blender.exe -b -P build_heavy.py -- H1 r1      round 1 silhouette: base blocks, black silhouettes + grey block renders -> H1/r1_silhouette/
  blender.exe -b -P build_heavy.py -- H1 r2      round 2 mid-poly: + plates, 3 cm bevels                                -> H1/r2_midpoly/
  blender.exe -b -P build_heavy.py -- H1 r3      round 3 detail: + bolts, grilles, hydraulics, hoses                     -> H1/r3_detail/
  blender.exe -b -P build_heavy.py -- H1 r5c export   final stage (round 5+): checks, colour renders, poses -> H1/r5c_final/; 'export'
                                                   also writes Titan_H1.blend / .fbx. ('final' = archived round 4, refused; see _r4_source/)
  blender.exe -b -P build_heavy.py -- H1 contacts | kneelfit <pose> | dbg <pose|json> <A> <B>   diagnostics
  (same with H2)
  py -3 build_heavy.py compose [r5c_final]       (no Blender) lineup / pose / before-after sheets from that round's renders

Geometry: heavy_parts.py (part table), heavy_rig.py (skeleton + sockets), heavy_geom.py (primitives). Analysis axes in those files
(x forward, y left, z up); Blender X = y, Y = -x, Z up, titan faces -Y (SPEC 5). Poses: v2 spec.json hand_poses (same parameter
meaning as v2/build_titan.py) + two walk keys designed here.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
SPEC_JSON = os.path.normpath(os.path.join(HERE, "..", "..", "v2-design", "out", "spec.json"))
ROUND_DIR = {"r1": "r1_silhouette", "r2": "r2_midpoly", "r3": "r3_detail", "final": "r4_final"}
KINDS = {"r1": {"base"}, "r2": {"base", "plate"}, "r3": {"base", "plate", "detail"}, "final": {"base", "plate", "detail"}}
POSE_EXTRA = {
    # walk keys for the heavy (no B-heavy retarget yet): contact and passing, short stride for the 40 % legs
    "walk_contact": {"pel_pitch": 6, "h_flex_L": 30, "k_L": 12, "h_flex_R": -14, "k_R": 22, "s_flex_R": 60.0, "e_R": 30.0, "s_in_R": 8, "s_out_R": 6,
                     "s_flex_L": 5, "e_L": 60, "s_out_L": 12, "w_yaw": -6},
    "walk_passing": {"pel_pitch": 6, "h_flex_L": 4, "k_L": 8, "h_flex_R": 38, "k_R": 62, "s_flex_R": 60.0, "e_R": 30.0, "s_in_R": 8, "s_out_R": 6,
                     "s_flex_L": 15, "e_L": 70, "s_out_L": 12, "w_yaw": 4},
}
# R5 (H-P1 closed, H-P3): the heavy's own defaults for the two one-knee poses replace v2's under the same names, so the 19 v2 poses are the
# heavy set. Two differences from v2, both from the heavy's short shin (shin + ankle 0.98 vs thigh 1.52; v2 1.45 vs 1.40):
#  - right ankle 30 instead of 55: v2's 55 folds the right foot sole into the thigh back (r1d sweep -20 / 0 / 15 / 30 all clean,
#    30 closest to v2);
#  - front (left) leg: v2's thigh-level knee (hip 90-100, knee 105-110) leaves the front foot ~1.1 m in the air on the heavy
#    (v2 itself ~0.5 / 1.0 m by a sagittal model); the heavy default plants it: hip 40 / knee 55 and hip 52 / knee 64, found by
#    the 'kneelfit' search (left foot and right knee both within 4 cm of the ground, no collisions, H1 and H2).
# v2's originals stay as compare poses (<name>_v2orig), tested and reported but not counted.
HEAVY_POSE_OVERRIDE = {"kneel_hatch": {"a_R": 30.0, "h_flex_L": 40.0, "k_L": 55.0},
                       "landing_one_knee": {"a_R": 30.0, "h_flex_L": 52.0, "k_L": 64.0}}
SHEET_POSES = ["stand_aim", "walk_contact", "walk_passing", "kneel_hatch", "yaw_85_level", "yaw_-85_level", "aim_up_45", "aim_down_45"]
COLORS = {
    "H1": {"pri": "#8A3B24", "sec": "#1E1E1E", "frame": "#2A2D31", "emit": "#FFA41C"},
    "H2": {"pri": "#4E5A3A", "sec": "#C9A227", "frame": "#2A2D31", "emit": "#4DFF6A"},
}
GREY = {"pri": 0.78, "sec": 0.42, "frame": 0.22, "emit": 0.97}
MATNAME = {"pri": "MAT_Primary", "sec": "MAT_Secondary", "frame": "MAT_Frame", "emit": "MAT_Emissive"}


# ------------------------------------------------------------------ compose (plain Python + PIL)
def compose(fin="r4_final"):
    """Sheets from the final-round folder 'fin'. r4 sheets keep their old names; later rounds write compare/<fin>/ and
    <code>/<fin>/, so nothing earlier is overwritten. From r5 on also a before/after sheet against r4."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 54)
        small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 34)
    except OSError:
        font = small = ImageFont.load_default()
    M1 = os.path.join(HERE, "..", "M1", "silhouette")
    out = os.path.join(HERE, "compare") if fin == "r4_final" else os.path.join(HERE, "compare", fin)
    os.makedirs(out, exist_ok=True)

    def crop_all(paths):
        ims = [Image.open(p).convert("RGB") for p in paths]
        box = None
        for im in ims:
            bb = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()
            if bb:
                box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
        box = (box[0] - 15, box[1] - 15, box[2] + 15, box[3] + 10)
        return [im.crop(box) for im in ims]

    def sheet(cells, name, cols):
        ims = crop_all([p for _, p in cells])
        w, h = ims[0].size
        pad, top = 24, 80
        rows = (len(ims) + cols - 1) // cols
        S = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * (h + top) + pad), "white")
        d = ImageDraw.Draw(S)
        for i, ((label, _), im) in enumerate(zip(cells, ims)):
            x, y = pad + (i % cols) * (w + pad), (i // cols) * (h + top)
            S.paste(im, (x, y + top))
            d.text((x + 10, y + 12), label, fill=(40, 40, 40), font=font)
        S.save(os.path.join(out, name + ".png"))
        S.resize((S.width // 4, S.height // 4), Image.LANCZOS).save(os.path.join(out, name + "_quarter.png"))
        return S.size

    # lineup: every titan that exists, black silhouettes, same camera. M-1 renders use another camera scale -> own sheet only for H.
    cells = []
    for view in ("front", "side", "back", "3q"):
        for code in ("H1", "H2"):
            p = os.path.join(HERE, code, fin, "sil_%s.png" % view)
            if os.path.exists(p):
                cells.append(("%s %s" % ({"H1": "H-1", "H2": "H-2"}[code], {"front": "正", "side": "侧", "back": "背", "3q": "前3/4"}[view]), p))
    if cells:
        print("lineup_H", sheet(cells, "lineup_H1_H2", 4))
    # same-scale lineup with M-1 (M-1 silhouette was rendered with ortho 9.6, ours with LINEUP renders at 9.6 too)
    cells = []
    for view in ("front", "side"):
        if os.path.exists(os.path.join(M1, "sil_%s.png" % view)):
            cells.append(("M-1 " + view, os.path.join(M1, "sil_%s.png" % view)))
        for code in ("H1", "H2"):
            p = os.path.join(HERE, code, fin, "lineup_%s.png" % view)
            if os.path.exists(p):
                cells.append(("%s %s" % ({"H1": "H-1", "H2": "H-2"}[code], view), p))
    L = os.path.normpath(os.path.join(HERE, "..", "L"))
    if os.path.isdir(L):
        for root, _, files in os.walk(L):
            for f in files:
                if f in ("sil_front.png",) and "final" in root:
                    cells.append(("L " + os.path.basename(os.path.dirname(root)), os.path.join(root, f)))
    if cells:
        print("lineup_M", sheet(cells, "lineup_with_M1", 3))
    # pose sheets
    for code in ("H1", "H2"):
        d = os.path.join(HERE, code, fin, "poses")
        if os.path.isdir(d):
            cells = [(p, os.path.join(d, p + ".png")) for p in SHEET_POSES if os.path.exists(os.path.join(d, p + ".png"))]
            if cells:
                ims = crop_all([c[1] for c in cells])
                w, h = ims[0].size
                cols, pad, top = 4, 16, 60
                rows = (len(ims) + cols - 1) // cols
                S = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * (h + top) + pad), "white")
                dd = ImageDraw.Draw(S)
                for i, ((label, _), im) in enumerate(zip(cells, ims)):
                    x, y = pad + (i % cols) * (w + pad), (i // cols) * (h + top)
                    S.paste(im, (x, y + top))
                    dd.text((x + 8, y + 10), label, fill=(40, 40, 40), font=small)
                S.save(os.path.join(HERE, code, fin, "poses_sheet.png"))
                print("poses", code, S.size)
    # round progression per titan (3/4 view)
    for code in ("H1", "H2"):
        cells = []
        rounds = [("r1_silhouette", "grey_3q.png"), ("r2_midpoly", "grey_3q.png"), ("r3_detail", "grey_3q.png"), ("r4_final", "color_3q.png")]
        if fin != "r4_final":
            rounds.append((fin, "color_3q.png"))
        for r, f in rounds:
            p = os.path.join(HERE, code, r, f)
            if os.path.exists(p):
                cells.append((r, p))
        if cells:
            ims = [Image.open(p).convert("RGB") for _, p in cells]
            w, h = ims[0].size
            S = Image.new("RGB", (len(ims) * w, h + 70), "white")
            dd = ImageDraw.Draw(S)
            for i, ((label, _), im) in enumerate(zip(cells, ims)):
                S.paste(im, (i * w, 70))
                dd.text((i * w + 12, 8), label, fill=(40, 40, 40), font=font)
            S.save(os.path.join(HERE, code, "rounds_3q.png" if fin == "r4_final" else "rounds_3q_%s.png" % fin))
    if fin != "r4_final":
        for code in ("H1", "H2"):
            cells = [("%s %s" % (r[:2], v), os.path.join(HERE, code, r, f)) for v, f in (("front", "color_front.png"), ("side", "color_side.png"),
                                                                                        ("kneel", "color_kneel_hatch.png"))
                     for r in ("r4_final", fin)]
            cells = [c for c in cells if os.path.exists(c[1])]
            if cells:
                print("before_after", code, sheet(cells, "before_after_%s" % code, 2))


if args and args[0] == "compose":
    compose(args[1] if len(args) > 1 else "r4_final")
    sys.exit(0)

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import heavy_geom as G  # noqa: E402
import heavy_parts as HP  # noqa: E402
import heavy_rig as RIG  # noqa: E402

WHICH = args[0] if args else "H1"
ROUND = args[1] if len(args) > 1 else "r1"
STAGE = "final" if (ROUND.startswith("final") or ROUND[:2] in ("r5", "r6", "r7", "r8", "r9")) else ROUND[:2]   # r1a / r1b ... retries, own folders
if ROUND[:2] in ("r5", "r6", "r7", "r8", "r9"):
    OUT = os.path.join(HERE, WHICH, ROUND + "_final")
else:
    OUT = os.path.join(HERE, WHICH, (ROUND + ROUND_DIR[STAGE][2:]) if STAGE in ("r1", "r2", "r3") else (ROUND_DIR["final"] + ROUND[5:]))
DO_EXPORT = ROUND == "final" or "export" in args[2:]
if ROUND.startswith("final") and not args[:1] == ["compose"]:
    # r4_final is the archived round 4 (A rig, v2 kneels); its exact sources are in _r4_source/. Do not overwrite it from here.
    sys.exit("round 'final' = archived r4; use r5x [export] (or run _r4_source/build_heavy.py to rebuild r4)")
CODE = WHICH
ROOT = "Titan_" + WHICH
SPEC = json.load(open(SPEC_JSON, encoding="utf-8"))
V2_POSES = dict(SPEC["hand_poses"])                     # the 19 v2 poses
POSES = {}
for _k, _v in V2_POSES.items():
    POSES[_k] = dict(_v, **HEAVY_POSE_OVERRIDE.get(_k, {}))
POSE_SET19 = list(V2_POSES)
for _k, _v in POSE_EXTRA.items():
    POSES[_k] = _v
COMPARE_POSES = {}
for _k in HEAVY_POSE_OVERRIDE:
    POSES[_k + "_v2orig"] = dict(V2_POSES[_k])
    COMPARE_POSES[_k + "_v2orig"] = _k
C = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)
NODES = RIG.nodes(WHICH)


def to_b(v):
    return (float(v[1]), float(-v[0]), float(v[2]))


def hex_lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ------------------------------------------------------------------ build
def make_materials(final):
    mats = {}
    for k, name in MATNAME.items():
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if final:
            col = hex_lin(COLORS[WHICH][k])
            m.diffuse_color = col
            if bsdf:
                bsdf.inputs["Base Color"].default_value = col
                bsdf.inputs["Roughness"].default_value = 0.55 if k != "frame" else 0.45
                bsdf.inputs["Metallic"].default_value = 0.25 if k in ("pri", "sec") else 0.6
                if k == "emit":
                    bsdf.inputs["Emission Color"].default_value = col
                    bsdf.inputs["Emission Strength"].default_value = 6.0
        else:
            g = GREY[k]
            m.diffuse_color = (g, g, g, 1)
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (g, g, g, 1)
        m["slot"] = k
        mats[k] = m
    return mats


def add_shell(bm, mesh, off, mi):
    vs = [bm.verts.new(to_b(np.array(v) - off)) for v in mesh[0]]
    new_faces = []
    for f in mesh[1]:
        try:
            face = bm.faces.new([vs[i] for i in f])
            face.material_index = mi
            new_faces.append(face)
        except ValueError:
            pass
    return vs, new_faces


def build(stage):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.context.scene.collection
    final = stage == "final"
    mats = make_materials(final)
    objs = {ROOT: bpy.data.objects.new(ROOT, None)}
    objs[ROOT].empty_display_size = 0.3
    col.objects.link(objs[ROOT])
    rest = {}
    for name, (parent, pos, d) in NODES.items():
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = "ARROWS" if name[0] in "JW" else "SPHERE"
        e.empty_display_size = 0.18 if name[0] in "JW" else 0.08
        e.rotation_mode = "QUATERNION"
        col.objects.link(e)
        objs[name] = e
        rest[name] = np.array(pos, float)
    for name, (parent, pos, d) in NODES.items():
        e = objs[name]
        e.parent = objs[ROOT] if parent == "ROOT" else objs[parent]
        ppos = np.zeros(3) if parent == "ROOT" else rest[parent]
        e.location = to_b(rest[name] - ppos)
        if d is not None and name.startswith("S_"):
            # socket direction: local +x (analysis) along d, i.e. Blender local -Y along d
            R = G.align_x(d)
            if parent != "ROOT":
                pass  # joints are identity at rest, so local == world
            e.rotation_quaternion = Matrix((C @ R @ C.T).tolist()).to_quaternion()
            e["direction_analysis"] = [round(float(x), 4) for x in d]
    P = HP.build(WHICH)
    kinds = KINDS[stage]
    meshes = {}
    for pname, p in P.parts.items():
        joint = p["joint"]
        off = rest[joint]
        shells = [s for s in p["shells"] if s[0] in kinds]
        if not shells:
            continue
        used = []
        for _, m, _ in shells:
            if m not in used:
                used.append(m)
        bm = bmesh.new()
        bevel_faces = []
        for kind, m, mesh in shells:
            if kind in ("base", "plate"):
                _, fs = add_shell(bm, mesh, off, used.index(m))
                bevel_faces += fs
        if stage != "r1" and bevel_faces:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.edges.ensure_lookup_table()
            edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(30)]
            if edges:
                bmesh.ops.bevel(bm, geom=edges, offset=0.03, offset_type="OFFSET", segments=2, profile=0.5, affect="EDGES", clamp_overlap=True)
        for kind, m, mesh in shells:
            if kind == "detail":
                add_shell(bm, mesh, off, used.index(m))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        md = bpy.data.meshes.new("%s_%s" % (CODE, pname))
        bm.to_mesh(md)
        bm.free()
        for m in used:
            md.materials.append(mats[m])
        md.update()
        ob = bpy.data.objects.new("%s_%s" % (CODE, pname), md)
        col.objects.link(ob)
        ob.parent = objs[joint]
        ob["owner_joint"] = joint
        meshes[pname] = ob
    bpy.context.view_layer.update()
    return objs, meshes, rest, P


# ------------------------------------------------------------------ posing (same parameter meaning as v2/build_titan.py)
def local_rotations(p):
    g = lambda k: p.get(k, 0.0)
    R = G
    out = {
        "J_Pelvis": R.Rz(g("pel_yaw")) @ R.Ry(g("pel_pitch")) @ R.Rx(g("pel_roll")),
        "J_Torso": R.Rz(g("w_yaw")) @ R.Ry(g("w_bend")) @ R.Rx(g("w_side")),
        "J_Hatch": R.Ry(g("hatch")),
        "J_Optic": R.Rz(g("op_yaw")) @ R.Ry(-g("op_pitch")),
        "J_Elbow_L": R.Ry(-g("e_L")),
        "J_Elbow_R": R.Ry(-g("e_R")),
        "J_Wrist_L": R.Ry(g("wr_pitch")) @ R.Rx(g("wr_side")),
        "J_Finger_L_1": R.Ry(g("f1")), "J_Finger_L_2": R.Ry(g("f2")), "J_Finger_L_3": R.Ry(-g("f3")),
    }
    for side, sg in (("L", 1), ("R", -1)):
        out["J_Hip_" + side] = R.Rz(g("h_twist_" + side)) @ R.Ry(-g("h_flex_" + side)) @ R.Rx(sg * g("h_out_" + side))
        out["J_Knee_" + side] = R.Ry(g("k_" + side))
        out["J_Ankle_" + side] = R.Ry(g("a_" + side)) @ R.Rx(g("a_roll_" + side))
        out["J_Shoulder_" + side] = R.Rz(g("s_in_" + side) * -sg) @ R.Ry(-g("s_flex_" + side)) @ R.Rx(sg * g("s_out_" + side))
    return out


POSED = [n for n in NODES if n.startswith("J_") or n == "W_Cannon"]


def set_pose(objs, rest, p, pel_off=(0, 0, 0)):
    rots = local_rotations(p)
    for name in POSED:
        if name in ("J_Barrel", "J_Drum"):
            continue
        Rm = rots.get(name)
        M = C @ Rm @ C.T if Rm is not None else np.eye(3)
        objs[name].rotation_quaternion = Matrix(M.tolist()).to_quaternion()
    objs["J_Pelvis"].location = to_b(rest["J_Pelvis"] + np.array(pel_off, float))
    bpy.context.view_layer.update()


def world_R_analysis(ob):
    return C.T @ np.array(ob.matrix_world.to_3x3()) @ C


def world_verts(ob):
    m = np.array(ob.matrix_world)
    v = np.array([x.co[:] for x in ob.data.vertices])
    return v @ m[:3, :3].T + m[:3, 3]


FEET = ("Foot_L", "Foot_R", "Toe_L", "Toe_R", "Shin_L", "Shin_R")


def solve_pose(objs, meshes, rest, hand):
    """v2 rule: level free feet within the ankle limits, then put the lowest foot/toe/shin vertex on the ground."""
    p = {k: v for k, v in hand.items() if not k.startswith("_")}
    set_pose(objs, rest, p)
    for side in "LR":
        if "a_" + side in p:
            continue
        f = world_R_analysis(objs["J_Ankle_" + side]) @ np.array([1.0, 0, 0])
        pitch = math.degrees(math.atan2(-f[2], math.hypot(f[0], f[1])))
        p["a_" + side] = float(np.clip(-pitch, -35, 60))
    set_pose(objs, rest, p)
    low = min(float(world_verts(meshes[n])[:, 2].min()) for n in FEET if n in meshes)
    off = (0.0, 0.0, -low)
    set_pose(objs, rest, p, off)
    return p, off


# ------------------------------------------------------------------ checks
def trees(meshes):
    return {n: BVHTree.FromPolygons([Vector(x) for x in world_verts(o)], [list(p.vertices) for p in o.data.polygons]) for n, o in meshes.items()}


EXCL = {frozenset(p) for p in HP.EXCLUDED_COMMON + (HP.EXCLUDED_H2 if WHICH == "H2" else [])}


def collide(meshes):
    T = trees(meshes)
    names = list(meshes)
    hits = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if meshes[a]["owner_joint"] == meshes[b]["owner_joint"] or frozenset((a, b)) in EXCL:
                continue
            if T[a].overlap(T[b]):
                hits.append(a + " x " + b)
    return hits


def pair_overlap(meshes, a, b):
    T = trees({a: meshes[a], b: meshes[b]})
    return bool(T[a].overlap(T[b]))


def _inside(tree, pt):
    o = Vector(pt); d = Vector((0.0123, 0.0071, 1.0)).normalized(); n = 0
    for _ in range(64):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        n += 1
        o = h[0] + d * 1e-5
    return n % 2 == 1


# reclined 1.8 m pilot (same as M-1: hip at S_Seat (0.55, 0, 4.28), trunk 40 deg back), capsules (a, b, radius, half-width y)
PILOT = [((0.55, 0.0, 4.28), (0.20, 0.0, 4.70), 0.13, 0.20), ((0.06, 0.0, 4.86), (0.06, 0.0, 4.86), 0.12, 0.0),
         ((0.55, 0.0, 4.28), (0.95, 0.0, 4.50), 0.09, 0.15), ((0.95, 0.0, 4.50), (1.24, 0.0, 4.25), 0.07, 0.15)]


def pilot_points(objs, rest):
    M = objs["J_Torso"].matrix_world
    w = rest["J_Torso"]
    pts = []
    for a, b, r, hw in PILOT:
        a, b = np.array(a), np.array(b)
        for t in np.linspace(0, 1, 7):
            c = a + (b - a) * t
            for yy in ([0.0] if hw == 0 else [-hw, 0.0, hw]):
                for dx, dz in ((r, 0), (-r, 0), (0, r), (0, -r)):
                    pts.append(np.array(M @ Vector(to_b(c + np.array((dx, yy, dz)) - w))))
    return pts


def area_by_material(meshes):
    A = {}
    for ob in meshes.values():
        sc = np.array(ob.matrix_world.to_3x3())
        for poly in ob.data.polygons:
            k = ob.data.materials[poly.material_index]["slot"]
            A[k] = A.get(k, 0.0) + poly.area * abs(np.linalg.det(sc)) ** (2 / 3)
    tot = sum(A.values())
    return {k: round(100 * v / tot, 1) for k, v in A.items()}, tot


def extents(meshes, skip=()):
    v = np.vstack([world_verts(o) for n, o in meshes.items() if n not in skip])
    return v.min(0), v.max(0)


def run_checks(objs, meshes, rest, P, stage):
    R = {"titan": WHICH, "round": stage, "date": "2026-11-12"}
    set_pose(objs, rest, {})
    tris, per = 0, {}
    for n, ob in meshes.items():
        ob.data.calc_loop_triangles()
        per[n] = len(ob.data.loop_triangles)
        tris += per[n]
    R["tris"] = dict(total=tris, ok=(40000 <= tris <= 60000) if STAGE == "final" else None, budget="40000-60000",
                     max_part=max(per, key=per.get), max_part_tris=max(per.values()), part_ok=max(per.values()) <= 6000, per_part=per)
    lo, hi = extents(meshes)
    H = float(hi[2])
    R["rest_top_m"] = round(H, 3)
    R["rest_top_part"] = max(meshes, key=lambda n: world_verts(meshes[n])[:, 2].max())
    sh = np.vstack([world_verts(meshes[n]) for n in ("Shoulder_L", "Shoulder_R")])
    hipv = np.vstack([world_verts(meshes[n]) for n in ("Thigh_L", "Thigh_R", "Pelvis")])
    hipv = hipv[(hipv[:, 2] > RIG.Z_HIP - 0.25) & (hipv[:, 2] < RIG.Z_HIP + 0.25)]
    sw, hw = float(sh[:, 0].max() - sh[:, 0].min()), float(hipv[:, 0].max() - hipv[:, 0].min())
    R["shoulder_width_m"], R["hip_width_m"] = round(sw, 3), round(hw, 3)
    R["shoulder_ge_hip_x1.5"] = dict(ok=sw >= 1.5 * hw, ratio=round(sw / hw, 3), need=round(1.5 * hw, 3))
    # dome thickness above the arm hub (outer top minus cavity top) and the hub covered by the dome footprint
    hub_top = RIG.Z_SH + 0.34
    dome = world_verts(meshes["Shoulder_L"])
    near = dome[(np.abs(dome[:, 0] - RIG.SH_Y) < 0.08) & (np.abs(dome[:, 1]) < 0.08)]
    zz = np.sort(near[:, 2])
    inner_top = float(zz[zz < float(zz.max()) - 0.2].max()) if len(zz) > 1 else float("nan")
    R["shoulder_armor"] = dict(ok=float(zz.max()) - inner_top >= 0.45, thickness_over_hub_m=round(float(zz.max()) - inner_top, 3),
                               dome_top_m=round(float(zz.max()), 3), cavity_top_m=round(inner_top, 3), hub_top_m=round(hub_top, 3),
                               dome_outer_rim_m=round(RIG.Z_SH - 0.06, 3),
                               how="vertical line through the shoulder pivot: dome outer top minus cavity top; hub (ball r 0.34) sits in the cavity, "
                                   "outer rim 0.06 below the pivot")
    pel_top = float(world_verts(meshes["Pelvis"])[:, 2].max())
    tor_bot = float(world_verts(meshes["Torso_Lower"])[:, 2].min())
    wh = tor_bot - pel_top
    R["waist_le_height_x0.06"] = dict(ok=wh <= 0.06 * H, waist_visible_m=round(wh, 3), limit_m=round(0.06 * H, 3))
    f = np.vstack([world_verts(meshes["Foot_L"]), world_verts(meshes["Toe_L"])])
    fl = float(f[:, 1].max() - f[:, 1].min())
    R["foot_ge_height_x0.22"] = dict(ok=fl >= 0.22 * H, foot_len_m=round(fl, 3), need_m=round(0.22 * H, 3), foot_width_m=round(float(f[:, 0].max() - f[:, 0].min()), 3))

    def girth(n):
        v = world_verts(meshes[n]); return float((v[:, 0].max() - v[:, 0].min()) * (v[:, 1].max() - v[:, 1].min()))
    R["calf_ge_thigh"] = dict(ok=girth("Shin_L") >= girth("Thigh_L"), thigh_m2=round(girth("Thigh_L"), 3), shin_m2=round(girth("Shin_L"), 3))
    R["top_le_collider_5.97"] = dict(ok=H <= 5.97, rest_top_m=round(H, 3))
    R["leg_ratio"] = dict(hip_rest_m=RIG.Z_HIP, ratio=round(RIG.Z_HIP / H, 3), target="0.40 [meas] (TF2 idle: hip 2.61 / top 6.55, knees bent)")
    M = RIG.MEAS
    have = dict(thigh=RIG.THIGH, shin=RIG.SHIN, ankle=RIG.Z_ANKLE, upper=RIG.UPPER, fore=RIG.FORE)
    R["bones_vs_meas"] = dict(variant=RIG.RIG_VARIANT, k_basis=RIG.K_B,
                              rows={b: dict(meas=M[b], meas_x_k=round(M[b] * RIG.K_B, 3), have=round(v, 3),
                                            dev_raw_pct=round(100 * (v / M[b] - 1), 1), dev_basis_pct=round(100 * (v / (M[b] * RIG.K_B) - 1), 1))
                                    for b, v in have.items()},
                              basis="[meas] x 0.878: the uniform factor that brings the TF2 heavy's straight-leg top (6.55 idle + 0.23) to 5.95 "
                                    "(user decision 2). Widths (hip 2.11, shoulder spacing) not scaled.")
    R["bones_vs_meas"]["ok_5pct_basis"] = all(abs(r["dev_basis_pct"]) <= 5 for r in R["bones_vs_meas"]["rows"].values())
    tor = np.vstack([world_verts(meshes[n]) for n in ("Torso_Upper",)])
    R["torso_size"] = dict(width_m=round(float(tor[:, 0].max() - tor[:, 0].min()), 3), depth_m=round(float(tor[:, 1].max() - tor[:, 1].min()), 3),
                           height_m=round(float(tor[:, 2].max() - tor[:, 2].min()), 3))
    bend = {}
    for k, v in (("bend_45", {"w_bend": 45}), ("bend_-25", {"w_bend": -25}), ("side_30", {"w_side": 30}), ("side_-30", {"w_side": -30}),
                 ("yaw_90_bend_45", {"w_yaw": 90, "w_bend": 45})):
        set_pose(objs, rest, v)
        bend[k] = [n for n in ("Torso_Lower", "Torso_Upper") if pair_overlap(meshes, n, "Pelvis")]
    R["waist_bend_clear"] = dict(ok=not any(bend.values()), cases=bend)
    # poses
    set_pose(objs, rest, {})
    R["rest_collisions_info"] = collide(meshes)
    poses, tops, solved, cont = {}, {}, {}, {}
    for name, hand in POSES.items():
        p, off = solve_pose(objs, meshes, rest, hand)
        solved[name] = (p, off)
        cont[name] = contacts_of(meshes)
        poses[name] = collide(meshes)
        tops[name] = round(float(extents(meshes)[1][2]), 3)
    R["poses_tested"] = list(POSES)
    R["pose_collisions"] = {k: v for k, v in poses.items() if v and k not in COMPARE_POSES}
    R["pose_clean"] = "%d / %d" % (sum(1 for k in POSE_SET19 if not poses[k]), len(POSE_SET19))
    R["pose_set19"] = dict(ok=all(not poses[k] for k in POSE_SET19), clean=R["pose_clean"],
                           overrides={k: v for k, v in HEAVY_POSE_OVERRIDE.items()},
                           how="v2 spec.json hand_poses; kneel_hatch and landing_one_knee use the heavy default (right ankle 30 instead of 55)")
    R["pose_extra_walk"] = {k: (poses[k] or "clean") for k in POSE_EXTRA}
    R["pose_v2_original_compare"] = {k: dict(heavy_default=v, collisions=poses[k] or "clean", contacts_v2orig=cont[k], contacts_heavy=cont[v],
                                             diff={x: dict(v2=V2_POSES[v].get(x), heavy=POSES[v].get(x)) for x in HEAVY_POSE_OVERRIDE[v]})
                                     for k, v in COMPARE_POSES.items()}
    R["pose_ground_contact_m"] = dict(rows=cont, how="lowest point of each foot (foot + toes) and shin after solving; 0 = on the ground. "
                                      "One foot up is part of the pose in sprint / dash / landing_rise / walk_passing (also in v2)")
    R["pose_top_m"] = tops
    p_sa, off_sa = solved["stand_aim"]
    set_pose(objs, rest, p_sa, off_sa)
    hz = float(objs["J_Hip_L"].matrix_world.translation.z)
    pz = float(objs["J_Pelvis"].matrix_world.translation.z)
    top_sa = float(extents(meshes)[1][2])
    R["stand_aim_vs_idle_meas"] = dict(hip_m=round(hz, 3), pelvis_m=round(pz, 3), top_m=round(top_sa, 3), leg_ratio=round(hz / top_sa, 3),
                                       meas_idle=dict(hip=M["hip_idle"], pelvis=M["pelvis_idle"], top=M["top_idle"], ratio=round(M["hip_idle"] / M["top_idle"], 3)),
                                       meas_idle_x_k=dict(hip=round(M["hip_idle"] * RIG.K_B, 3), pelvis=round(M["pelvis_idle"] * RIG.K_B, 3)),
                                       dev_basis_pct=dict(hip=round(100 * (hz / (M["hip_idle"] * RIG.K_B) - 1), 1),
                                                          pelvis=round(100 * (pz / (M["pelvis_idle"] * RIG.K_B) - 1), 1),
                                                          ratio=round(100 * ((hz / top_sa) / (M["hip_idle"] / M["top_idle"]) - 1), 1)))
    # pilot
    set_pose(objs, rest, {})
    # inside test by ray-crossing parity: run it on each closed base shell separately (from round 2 on the part objects hold
    # overlapping shells - bands, ribs - which break the parity). Base shells are the un-bevelled volumes (bevel moves edges <= 3 cm).
    T = []
    for n in ("Torso_Upper", "Torso_Lower", "Hatch"):
        for kind, m, (vs, fs) in P.parts[n]["shells"]:
            if kind == "base":
                T.append(BVHTree.FromPolygons([Vector(to_b(v)) for v in vs], [list(f) for f in fs]))
    pts = pilot_points(objs, rest)
    outside = [p for p in pts if not any(_inside(t, p) for t in T)]
    R["pilot_fit"] = dict(ok=not outside, points=len(pts), outside=len(outside),
                          how="reclined 1.8 m pilot capsules (hip at S_Seat, trunk 40 deg back), hatch closed, rest pose; inside torso / cone / door base shells")
    # kneel + hatch 120
    p, off = solved["kneel_hatch"]
    set_pose(objs, rest, dict(p, hatch=120), off)
    hinge = objs["J_Hatch"].matrix_world.translation
    door = {"H1": HP.H1_DOOR, "H2": HP.H2_DOOR}[WHICH]
    ow, oh = 2 * door[2], door[1] - door[0]
    th = BVHTree.FromPolygons([Vector(x) for x in world_verts(meshes["Hatch"])], [list(q.vertices) for q in meshes["Hatch"].data.polygons])
    R["kneel_hatch"] = dict(ok=ow >= 0.60 and oh >= 0.94, opening_w_m=round(ow, 3), opening_h_m=round(oh, 3), hinge_height_m=round(float(hinge.z), 3),
                            seat_height_m=round(float((objs["J_Torso"].matrix_world @ Vector(to_b(np.array((0.55, 0, 4.28)) - rest["J_Torso"]))).z), 3),
                            pilot_points_in_open_hatch=sum(1 for q in pilot_points(objs, rest) if _inside(th, q)),
                            hatch_vs_other_parts=[h for h in collide(meshes) if "Hatch" in h])
    set_pose(objs, rest, {})
    # emissive and colour shares
    shares, area = area_by_material(meshes)
    R["material_area_pct"] = dict(shares=shares, emissive_ok=shares.get("emit", 0) <= 3.0, total_m2=round(area, 1),
                                  target="Primary ~60, Secondary ~15, Frame ~22, Emissive <= 3")
    R["materials"] = sorted({m.name for ob in meshes.values() for m in ob.data.materials})
    R["materials_ok"] = R["materials"] == sorted(MATNAME.values())
    # names and origins
    required = ["J_Pelvis", "J_Waist", "J_Torso", "J_Hatch", "J_Optic", "J_Launcher_L", "J_Shoulder_L", "J_Elbow_L", "J_Wrist_L", "J_Shoulder_R", "J_Elbow_R",
                "W_Cannon", "J_Hip_L", "J_Knee_L", "J_Ankle_L", "J_Hip_R", "J_Knee_R", "J_Ankle_R", "J_Finger_L_1", "J_Finger_L_2", "J_Finger_L_3",
                "S_Eye", "S_Seat", "S_Muzzle", "S_Hand_L", "S_Chest", "S_Thrust", "S_Vent_L", "S_Vent_R", "S_Dmg_Torso_F", "S_Dmg_Torso_B",
                "S_Dmg_Shoulder_L", "S_Dmg_Shoulder_R", "S_Dmg_Elbow_L", "S_Dmg_Elbow_R", "S_Dmg_Thigh_L", "S_Dmg_Thigh_R", "S_Dmg_Knee_L", "S_Dmg_Knee_R",
                "S_Foot_L", "S_Foot_R"] + ["S_Rocket_%d" % i for i in range(1, 7)] + ["S_Embark", "S_Rodeo", "S_Optic"]
    required += ["S_Flame_L", "S_Tank_L", "S_Tank_R", "S_Trap"] if WHICH == "H1" else ["J_Barrel", "J_Drum", "S_Drum", "S_GunShield", "S_Eject"]
    R["names"] = dict(ok=all(n in objs for n in required), missing=[n for n in required if n not in objs], count=len(required))
    worst = 0.0
    for n, ob in meshes.items():
        worst = max(worst, (ob.matrix_world.translation - objs[ob["owner_joint"]].matrix_world.translation).length)
    R["origins_on_joints"] = dict(ok=worst < 1e-5, worst_m=worst)
    R["parts"] = {n: dict(joint=ob["owner_joint"], tris=per[n]) for n, ob in meshes.items()}
    return R, solved


# ------------------------------------------------------------------ rendering
def setup(mode, res=(1000, 1000)):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    if mode in ("sil", "grey"):
        sc.render.engine = "BLENDER_WORKBENCH"
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
            sh.show_shadows = False
    else:
        sc.render.engine = "BLENDER_EEVEE"
        sc.view_settings.view_transform = "AgX"
        try:
            sc.view_settings.look = "AgX - Medium High Contrast"
        except TypeError:
            pass
        sc.world.use_nodes = True
        bg = sc.world.node_tree.nodes.get("Background")
        bg.inputs[0].default_value = (0.62, 0.66, 0.72, 1)
        bg.inputs[1].default_value = 0.55
        try:
            sc.eevee.taa_render_samples = 48
        except AttributeError:
            pass


def set_colors(mode, final):
    for m in bpy.data.materials:
        if m.name.startswith("H_"):
            continue
        k = m.get("slot")
        if mode == "sil":
            m.diffuse_color = (0, 0, 0, 1)
        elif final:
            m.diffuse_color = hex_lin(COLORS[WHICH][k])
        else:
            g = GREY[k]
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
        v = [(x * 14, y * 14, z * 0.02 - 0.02) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
        rgba = (0.30, 0.31, 0.32, 1)
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
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    md.materials.append(m)
    if kind == "collider":
        ob.modifiers.new("wire", "WIREFRAME").thickness = 0.025
    return ob


def clear_helpers():
    for ob in [o for o in bpy.data.objects if o.name.startswith("H_")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    for m in [m for m in bpy.data.materials if m.name.startswith("H_") and m.users == 0]:
        bpy.data.materials.remove(m)


def lights(on):
    for ob in [o for o in bpy.data.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(ob, do_unlink=True)
    if not on:
        return
    for name, typ, loc, rot, en in (("Key", "SUN", (0, 0, 10), (math.radians(50), 0, math.radians(-35)), 3.2),
                                     ("Rim", "SUN", (0, 0, 10), (math.radians(60), 0, math.radians(160)), 1.6)):
        ld = bpy.data.lights.new(name, typ)
        ld.energy = en
        ld.angle = math.radians(4)
        ob = bpy.data.objects.new(name, ld)
        ob.location, ob.rotation_euler = loc, rot
        bpy.context.scene.collection.objects.link(ob)


def render(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


SCALE, ZC = 9.6, 3.2
ORTHO = {"front": ((0, -40, ZC), (3.7, 0)), "side": ((40, 0, ZC), (0, 3.8)), "back": ((0, 40, ZC), (-3.7, 0))}
Q34 = ((10.0, -13.5, 5.6), (0.2, -0.3, 2.9), (3.6, 0.6))


def render_set(mode, final, prefix, collider=True):
    set_colors(mode, final)
    setup(mode)
    lights(mode == "color")
    for name, (loc, hxy) in ORTHO.items():
        helper("human", hxy)
        if mode == "color":
            helper("ground")
        if mode == "grey" and collider:
            helper("collider")
        camera(loc, (0, 0, ZC), ortho=SCALE)
        render(os.path.join(OUT, "%s_%s.png" % (prefix, name)))
        clear_helpers()
    helper("human", Q34[2])
    if mode == "color":
        helper("ground")
    camera(Q34[0], Q34[1], lens=62)
    render(os.path.join(OUT, "%s_3q.png" % prefix))
    clear_helpers()


ID_COL = {"pri": (1, 0, 0, 1), "sec": (0, 1, 0, 1), "frame": (0, 0, 1, 1), "emit": (1, 1, 0, 1)}


def visible_shares():
    """Share of each material in the pixels a viewer sees: flat ID colours, front/side/back/3q, stand_aim. Hidden faces do not count."""
    for m in bpy.data.materials:
        if m.get("slot"):
            m.diffuse_color = ID_COL[m["slot"]]
    setup("sil", (500, 500))
    counts = {k: 0 for k in ID_COL}
    path = os.path.join(OUT, "_id.png")
    views = [(ORTHO[n][0], (0, 0, ZC), SCALE) for n in ORTHO] + [(Q34[0], Q34[1], None)]
    for loc, tgt, orth in views:
        camera(loc, tgt, ortho=orth, lens=62)
        render(path)
        im = bpy.data.images.load(path)
        px = np.array(im.pixels[:]).reshape(-1, 4)[:, :3]
        bpy.data.images.remove(im)
        for k, c in ID_COL.items():
            counts[k] += int(np.sum(np.all(np.abs(px - np.array(c[:3])) < 0.25, axis=1)))
    os.remove(path)
    tot = sum(counts.values())
    return {k: round(100 * v / tot, 1) for k, v in counts.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    objs, meshes, rest, P = build(STAGE)
    R, solved = run_checks(objs, meshes, rest, P, ROUND)
    final = STAGE == "final"
    p, off = solved["stand_aim"]
    set_pose(objs, rest, p, off)
    R["pose_rendered"] = "stand_aim (v2 hand pose: hip 14, knee 28, cannon level), feet levelled, lowest foot vertex on the ground"
    render_set("sil", final, "sil")
    if final:
        R["material_visible_pct"] = dict(shares=visible_shares(), emissive_ok=None,
                                         how="pixels of each material in flat-colour renders, front + side + back + 3/4, stand_aim; target Primary ~60, Secondary ~15, Frame ~22, Emissive <= 3")
        R["material_visible_pct"]["emissive_ok"] = R["material_visible_pct"]["shares"]["emit"] <= 3.0
        render_set("color", True, "color")
        # same camera as the M-1 silhouettes (ortho 9.6, centre z 3.2) for the lineup sheet, no human block
        set_colors("sil", True); setup("sil")
        for name in ("front", "side"):
            camera(ORTHO[name][0], (0, 0, ZC), ortho=SCALE)
            render(os.path.join(OUT, "lineup_%s.png" % name))
        # kneel + hatch open, colour
        kp, koff = solved["kneel_hatch"]
        set_pose(objs, rest, dict(kp, hatch=120), koff)
        set_colors("color", True); setup("color"); lights(True)
        helper("human", (3.6, 1.2)); helper("ground")
        camera((9.5, -13.0, 4.2), (0.3, -0.6, 2.2), lens=48)
        render(os.path.join(OUT, "color_kneel_hatch.png"))
        clear_helpers()
        # pose set (grey, 3/4) for the pose sheet
        set_colors("grey", False); setup("grey", (700, 700)); lights(False)
        for name in SHEET_POSES:
            pp, po = solved[name]
            set_pose(objs, rest, pp, po)
            camera((10.0, -13.5, 5.6), (0.2, -0.3, 2.6), lens=55)
            render(os.path.join(OUT, "poses", name + ".png"))
        set_colors("color", True)
    else:
        render_set("grey", False, "grey")
        kp, koff = solved["kneel_hatch"]
        set_pose(objs, rest, dict(kp, hatch=120), koff)
        set_colors("grey", False); setup("grey")
        helper("human", (3.6, 1.2))
        camera((9.5, -13.0, 4.2), (0.3, -0.6, 2.2), lens=48)
        render(os.path.join(OUT, "grey_kneel_hatch.png"))
        clear_helpers()
    set_pose(objs, rest, {})
    if final and DO_EXPORT:
        R["fbx_roundtrip"] = export(objs, rest)
    json.dump(R, open(os.path.join(OUT, "checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    summ = {k: (v.get("ok") if isinstance(v, dict) and "ok" in v else None) for k, v in R.items()}
    print("=== %s %s tris %d top %.3f poses %s" % (WHICH, ROUND, R["tris"]["total"], R["rest_top_m"], R["pose_clean"]))
    print("=== CHECKS", json.dumps(summ))
    print("=== COLL", json.dumps(R["pose_collisions"]))
    print("=== REST", json.dumps(R["rest_collisions_info"]))


def export(objs, rest):
    for ob in [o for o in bpy.data.objects if o.type not in ("EMPTY", "MESH") or o.name.startswith("H_")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    clear_helpers()
    # 1.8 m reference block stays in the .blend (SPEC 5), not in the FBX
    v = [(x * 0.25, y * 0.15, z * 1.8) for z in (0, 1) for y in (-1, 1) for x in (-1, 1)]
    md = bpy.data.meshes.new("REF_Human_1.8m")
    md.from_pydata(v, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    ref = bpy.data.objects.new("REF_Human_1.8m", md)
    ref.location = (3.6, -1.0, 0)
    bpy.context.scene.collection.objects.link(ref)
    blend = os.path.join(HERE, "Titan_%s.blend" % WHICH)
    fbx = os.path.join(HERE, "Titan_%s.fbx" % WHICH)
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    for ob in bpy.data.objects:
        ob.select_set(ob.name != "REF_Human_1.8m")
    # Unity preset as v2 (bake_space_transform=False: baking breaks the empties + parented meshes on re-import, ../../_old-713-base-medium/FBX-ROUNDTRIP.md)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                             apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                             add_leaf_bones=False, mesh_smooth_type="FACE", use_mesh_modifiers=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx, axis_forward="-Z", axis_up="Y")
    bpy.context.view_layer.update()
    worst, worst_e, missing = None, 0.0, []
    for n in NODES:
        ob = bpy.data.objects.get(n)
        if ob is None:
            missing.append(n)
            continue
        e = (ob.matrix_world.translation - Vector(to_b(rest[n]))).length
        if e > worst_e:
            worst, worst_e = n, e
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    zs = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
    tri = 0
    for o in meshes:
        o.data.calc_loop_triangles()
        tri += len(o.data.loop_triangles)
    return dict(ok=not missing and worst_e <= 0.01, worst=worst, worst_m=round(worst_e, 5), missing=missing, mesh_objects=len(meshes), tris=tri,
                mesh_z=[round(min(zs), 3), round(max(zs), 3)], setting="Unity preset: axis_forward=-Z, axis_up=Y, FBX_SCALE_ALL, bake_space_transform=False",
                note="Blender re-import only. How Unity reads it is not checked (not imported into Unity by this task).")


def debug(pose, a, b):
    """Print where parts a and b overlap in a pose: polygon centres in each part's own rest coordinates (analysis axes)."""
    objs, meshes, rest, P = build(STAGE)
    if pose.startswith("{"):
        POSES[pose] = json.loads(pose)
    p, off = solve_pose(objs, meshes, rest, POSES[pose]) if pose != "rest" else ({}, (0, 0, 0))
    if pose == "rest":
        set_pose(objs, rest, {})
    lows = sorted((float(world_verts(o)[:, 2].min()), n) for n, o in meshes.items())[:4]
    print("=== DBG lowest parts", [(round(z, 3), n) for z, n in lows])
    T = trees({a: meshes[a], b: meshes[b]})
    pairs = T[a].overlap(T[b])
    print("=== DBG", pose, a, b, "pairs", len(pairs))
    for name, idx in ((a, 0), (b, 1)):
        ob = meshes[name]
        inv = ob.matrix_world.inverted()
        js = rest[ob["owner_joint"]]
        pts = []
        for pr in pairs[:4000]:
            poly = ob.data.polygons[pr[idx]]
            c = poly.center
            pts.append(np.array((-c.y, c.x, c.z)) + js)   # local Blender -> analysis, + joint rest position
        pts = np.array(pts)
        print("===  %s rest-coords min %s max %s" % (name, np.round(pts.min(0), 3), np.round(pts.max(0), 3)))


def contacts_of(meshes):
    g = lambda ns: round(min(float(world_verts(meshes[n])[:, 2].min()) for n in ns if n in meshes), 3)
    return dict(foot_L=g(("Foot_L", "Toe_L")), foot_R=g(("Foot_R", "Toe_R")), shin_L=g(("Shin_L",)), shin_R=g(("Shin_R",)))


def contacts():
    objs, meshes, rest, P = build("r3")
    for name, hand in POSES.items():
        solve_pose(objs, meshes, rest, hand)
        print("=== CONTACT", name, json.dumps(contacts_of(meshes)))


def kneelfit(name):
    """Heavy kneel: search the front (left) leg so its foot is planted while the right knee stays on the ground."""
    objs, meshes, rest, P = build("r3")
    base = dict(POSES[name])
    for hf in range(20, 92, 4):
        for dk in (-10, 0, 10, 20):
            p = dict(base, h_flex_L=float(hf), k_L=float(hf + base.get("pel_pitch", 0) + dk))
            p.pop("a_L", None)
            solve_pose(objs, meshes, rest, p)
            c = contacts_of(meshes)
            if c["foot_L"] < 0.06 and c["shin_R"] < 0.06:
                print("=== FIT", name, hf, dk, json.dumps(c), json.dumps(collide(meshes)))


if args and len(args) > 1 and args[1] == "contacts":
    STAGE = "r3"
    contacts()
elif args and len(args) > 2 and args[1] == "kneelfit":
    STAGE = "r3"
    kneelfit(args[2])
elif args and len(args) > 2 and args[1] == "dbg":
    STAGE = "r3"
    debug(args[2], args[3], args[4])
else:
    main()
