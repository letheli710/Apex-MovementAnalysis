"""L-2 Ronin (浪人): light chassis, melee + dash. Same skeleton as L-1 (wing joints kept, no wing meshes); armour and weapons differ.
SPEC v1.2 + user spec 4.4. World rest coordinates, analysis axes (x forward, y left, z up). No bpy."""
import math

import numpy as np

import geo
import light_common as C
import light_rig as R
from l1_parts import rifle_box, rifle_pt, rifle_tube, WR

CODE = "L2"
LEAN = 18.0      # L-1 + 10 deg (user spec 4.4)
COLORS = dict(pri="#1B1C20", sec="#B3261E", frame="#34373C", emit="#9A5CFF")
HAS_WINGS = False

# sword, upright torso coordinates (leaned with the shell): hilt end behind the right shoulder, 45 deg down to the left hip
SW_HILT = np.array((-1.02, -0.95, 5.58))
SW_DIR = np.array((0.0, 0.7071, -0.7071))     # along the blade, hilt -> tip
SW_W = np.array((0.0, 0.7071, 0.7071))        # across the blade: back edge (+) to cutting edge (-)
SW_T = np.array((1.0, 0.0, 0.0))              # thickness (toward the body = +)
SW_LEN, SW_GRIP = 3.60, 0.35                  # total length, grip point (origin of the sword) from the hilt end


def sw(s, w=0.0, t=0.0):
    return SW_HILT + SW_DIR * s + SW_W * w + SW_T * t


def sw_box(s0, s1, w0, w1, t0, t1):
    secs = []
    for s in (s0, s1):
        secs.append([sw(s, w, t) for w, t in ((w0, t0), (w1, t0), (w1, t1), (w0, t1))])
    return geo.loft3(secs)


def sword(P):
    L = lambda m: C.leaned(m, LEAN)
    pommel = geo.lathe(sw(0.0), sw(0.10), [(0, 0.05), (0.4, 0.09), (1, 0.06)], 12)
    grip = geo.merge(geo.tube(sw(0.10), sw(0.62), 0.055, 12), *[geo.tube(sw(0.14 + 0.08 * i), sw(0.17 + 0.08 * i), 0.065, 12) for i in range(6)])
    guard = sw_box(0.62, 0.72, -0.30, 0.26, -0.08, 0.08)
    # single-edged straight blade: back edge straight (+w), cutting edge (-w) with a bevel, angled tip
    secs = []
    for s, wb, we, th in ((0.72, 0.17, -0.18, 0.07), (2.80, 0.17, -0.18, 0.06), (3.30, 0.17, -0.10, 0.05), (3.60, 0.17, 0.12, 0.03)):
        secs.append([sw(s, wb, th / 2), sw(s, we + 0.04, th / 2), sw(s, we, 0.0), sw(s, we + 0.04, -th / 2), sw(s, wb, -th / 2)])
    blade = geo.loft3(secs)
    edge = geo.loft3([[sw(s, -0.165, 0.012), sw(s, -0.150, 0.012), sw(s, -0.150, -0.012), sw(s, -0.165, -0.012)] for s in (0.80, 3.20)])
    fuller = sw_box(0.85, 2.70, 0.06, 0.12, -0.034, 0.034)
    P.add("Sword_Hilt", "S_Sword_Back", "frame", L(geo.merge(pommel, grip, guard)), 1, hub=True)
    P.add("Sword_Blade", "S_Sword_Back", "frame", L(blade), 1)
    P.add("Sword_Fuller", "S_Sword_Back", "frame", L(fuller), 3)
    P.add("Sword_Edge", "S_Sword_Back", "emit", L(edge), 2)
    # rack (鞘架): rail behind the back edge, three clamps round the blade, two brackets into the back
    rail = geo.sweep_rect([sw(0.80, 0.24, 0.10), sw(3.40, 0.24, 0.10)], 0.10, 0.08, up=SW_T)
    clamps = []
    for s in (1.10, 2.10, 3.10):
        clamps.append(sw_box(s, s + 0.14, -0.22, 0.30, 0.06, 0.12))
        clamps.append(sw_box(s, s + 0.14, -0.22, -0.18, -0.08, 0.12))
        clamps.append(sw_box(s, s + 0.14, -0.22, 0.30, -0.08, -0.05))
    brackets = [geo.tube(sw(s, 0.24, 0.12), sw(s, 0.24, 0.12) + np.array((0.36, 0.0, 0.0)), 0.07, 10) for s in (1.0, 2.4)]
    P.add("Rack", "J_Torso", "pri", L(geo.merge(rail, *brackets)), 1, hub=True)
    P.add("Rack_Clamps", "J_Torso", "sec", L(geo.merge(*clamps)), 2)
    grip_pt = R.lean(sw(SW_GRIP), LEAN)
    return grip_pt


def pauldron(P):
    """Left: layered pauldron, torso-fixed (M-1 decision 4 scheme A). Cap 0.55+ thick over the arm hub, three lames stepping out and down."""
    inner = geo.extrude([(0.50, 4.97), (0.84, 4.97), (0.84, 5.64), (0.50, 5.68)], "yz", -0.58, 0.12)
    cap = geo.extrude([(0.80, 4.97), (1.47, 4.97), (1.62, 4.86), (1.88, 4.92), (1.94, 5.20), (1.74, 5.56), (1.00, 5.66), (0.80, 5.66)], "yz", -0.66, 0.50)
    capnose = geo.extrude([(0.86, 5.00), (1.50, 5.00), (1.84, 5.02), (1.70, 5.46), (1.00, 5.56), (0.86, 5.56)], "yz", 0.49, 0.64)
    P.add("Pauldron_L", "J_Torso", "sec", geo.merge(inner, cap, capnose), 1, panel=True)
    lames = []
    for k in range(3):
        y0, z0 = 1.60 + 0.06 * k, 4.94 - 0.18 * k     # each lame tucks under the one above
        lames.append(geo.extrude([(y0, z0), (y0 + 0.34, z0 + 0.02), (y0 + 0.40, z0 - 0.24), (y0 + 0.06, z0 - 0.28)], "yz", -0.58 + 0.03 * k, 0.46 - 0.04 * k))
    P.add("Pauldron_Lames_L", "J_Torso", "sec", geo.merge(*lames), 1)
    trim = geo.extrude([(1.00, 5.66), (1.74, 5.56), (1.76, 5.60), (1.00, 5.71)], "yz", -0.60, 0.52)
    P.add("Pauldron_Trim_L", "J_Torso", "frame", trim, 2)
    P.add("Pauldron_Bolts_L", "J_Torso", "frame", geo.merge(geo.bolts_line((-0.40, 1.93, 5.10), (0.30, 1.93, 5.10), (0, 1, 0), 0.024, 6),
                                                            geo.bolts_line((-0.50, 1.20, 5.66), (0.30, 1.20, 5.66), (0, 0, 1), 0.024, 5)), 3)
    # right: near bare. A short cap (frame) bridges the torso top to the hub; the arm hub itself carries the width.
    rcap = geo.extrude([(-0.50, 4.97), (-1.30, 4.97), (-1.40, 5.10), (-1.30, 5.30), (-0.95, 5.48), (-0.50, 5.66)], "yz", -0.50, 0.12)
    P.add("Shoulder_Cap_R", "J_Torso", "frame", rcap, 1, panel=True)


def skirt(P):
    """Waist skirt (裙甲): back and side plates on the pelvis, front tassets on the thighs (they move with the leg)."""
    # three plates with gaps, the side ones hang lower and splay out (not one flat board)
    back = geo.merge(geo.loft([(3.06, geo.rect(-0.69, -0.60, -0.24, 0.24, 0.03)), (3.72, geo.rect(-0.62, -0.53, -0.26, 0.26, 0.03))]),
                     geo.loft([(2.96, geo.rect(-0.72, -0.62, 0.30, 0.90, 0.03)), (3.40, geo.rect(-0.69, -0.59, 0.30, 0.92, 0.03)),
                               (3.70, geo.rect(-0.62, -0.53, 0.30, 0.78, 0.03))]),
                     geo.loft([(2.96, geo.rect(-0.72, -0.62, -0.90, -0.30, 0.03)), (3.40, geo.rect(-0.69, -0.59, -0.92, -0.30, 0.03)),
                               (3.70, geo.rect(-0.62, -0.53, -0.78, -0.30, 0.03))]))
    # side plates ride the thighs (J_Hip): hip abduction 45 would drive a pelvis-mounted side plate into the thigh
    side = geo.extrude([(-0.42, 3.62), (0.04, 3.58), (0.02, 3.02), (-0.38, 2.94)], "xz", 0.955, 1.02)
    hang = geo.merge(geo.box((-0.60, 0.70, 3.68), (0.06, 0.16, 0.05), 0.02), geo.box((-0.60, -0.70, 3.68), (0.06, 0.16, 0.05), 0.02),
                     )
    P.add("Skirt_Back", "J_Pelvis", "pri", back, 1, panel=True)
    P.pair("Skirt_Side", "J_Hip_L", "pri", side, 1, panel=True)
    P.add("Skirt_Hangers", "J_Pelvis", "frame", hang, 2)
    edge_b = geo.merge(geo.loft([(2.92, geo.rect(-0.73, -0.62, 0.30, 0.90, 0.02)), (3.00, geo.rect(-0.73, -0.62, 0.30, 0.90, 0.02))]),
                       geo.loft([(2.92, geo.rect(-0.73, -0.62, -0.90, -0.30, 0.02)), (3.00, geo.rect(-0.73, -0.62, -0.90, -0.30, 0.02))]),
                       geo.loft([(3.02, geo.rect(-0.70, -0.60, -0.24, 0.24, 0.02)), (3.10, geo.rect(-0.70, -0.60, -0.24, 0.24, 0.02))]))
    edge_s = geo.extrude([(-0.40, 3.00), (0.03, 3.08), (0.03, 3.01), (-0.40, 2.92)], "xz", 0.95, 1.025)
    P.add("Skirt_Edge", "J_Pelvis", "sec", edge_b, 2)
    P.pair("Skirt_Side_Edge", "J_Hip_L", "sec", edge_s, 2)
    tasset = geo.extrude([(0.34, 3.40), (0.42, 3.40), (0.46, 2.82), (0.38, 2.82)], "xz", 0.60, 1.02)
    P.pair("Tasset", "J_Hip_L", "pri", tasset, 1, panel=True)
    P.pair("Tasset_Edge", "J_Hip_L", "sec", geo.extrude([(0.37, 2.86), (0.47, 2.86), (0.47, 2.80), (0.37, 2.80)], "xz", 0.60, 1.02), 2)


def optic(P):
    """Vertical slit sensor at the torso centre line, above the canopy door."""
    housing = geo.loft([(5.45, geo.rect(0.18, 0.34, -0.09, 0.09, 0.04)), (5.74, geo.rect(0.14, 0.30, -0.08, 0.08, 0.04))])
    slit = geo.loft([(5.48, geo.rect(0.30, 0.355, -0.028, 0.028, 0.01)), (5.70, geo.rect(0.26, 0.315, -0.028, 0.028, 0.01))])
    P.add("Optic_Housing", "J_Optic", "frame", C.leaned(housing, LEAN), 1, hub=True)
    P.add("Optic_Slit", "J_Optic", "emit", C.leaned(slit, LEAN), 1, hub=True)
    return R.lean((0.26, 0.0, 5.59), LEAN), R.lean((0.34, 0.0, 5.59), LEAN)


def back(P):
    """Two phase generators on a diagonal (upper left, lower right), not level: no face from behind. Spine plate."""
    spine = geo.loft([(4.30, geo.rect(-0.86, -0.62, -0.14, 0.14, 0.05)), (5.55, geo.rect(-0.82, -0.58, -0.12, 0.12, 0.05))])
    P.add("Spine", "J_Torso", "pri", C.leaned(spine, LEAN), 1)
    gens, glows = [], []
    for (y, z, r) in ((0.42, 5.18, 0.19), (-0.40, 4.48, 0.17)):
        x0 = -0.70
        gens.append(geo.lathe((x0, y, z), (x0 - 0.30, y, z), [(0, r), (0.5, r + 0.03), (1, r - 0.02)], 18))
        glows.append(geo.tube((x0 - 0.30, y, z), (x0 - 0.31, y, z), r * 0.62, 18))
    P.add("Phase_Gen", "J_Torso", "frame", C.leaned(geo.merge(*gens), LEAN), 1)
    P.add("Phase_Glow", "J_Torso", "emit", C.leaned(geo.merge(*glows), LEAN), 2)
    ribs = geo.merge(*[geo.tube((-0.84, 0.42, 5.18 + d), (-0.95, 0.42, 5.18 + d), 0.215, 18) for d in ()])
    louv = geo.grille((-0.62, -1.00, 5.22), (-1, 0, 0), (0, 1, 0), 0.40, 0.24, 3, 0.02, 0.05)
    P.add("Vent_R", "J_Torso", "frame", louv, 3)


def shotgun(P):
    U = 0.44
    P.add("Shotgun_Body", "W_Shotgun", "pri", geo.merge(rifle_box(-0.70, 0.62, 0.26, 0.68, -0.16, 0.16, 0.06), rifle_box(-0.78, -0.40, 0.34, 0.62, -0.12, 0.12, 0.05)), 1, panel=True)
    P.add("Shotgun_Grip", "W_Shotgun", "frame", rifle_box(0.20, 0.38, 0.02, 0.30, -0.07, 0.07, 0.03), 1, hub=True)
    P.add("Shotgun_Barrels", "W_Shotgun", "frame", geo.merge(rifle_tube(0.60, 1.55, 0.37, 0.0, 0.085, 14), rifle_tube(0.60, 1.55, 0.56, 0.0, 0.085, 14),
                                                             rifle_tube(1.40, 1.56, 0.37, 0.0, 0.10, 14), rifle_tube(1.40, 1.56, 0.56, 0.0, 0.10, 14)), 1)
    P.add("Shotgun_Drum", "W_Shotgun", "frame", geo.lathe(rifle_pt(0.05, 0.80, -0.14), rifle_pt(0.05, 0.80, 0.14), [(0, 0.16), (0.2, 0.19), (0.8, 0.19), (1, 0.16)], 18), 2)
    P.add("Shotgun_Shroud", "W_Shotgun", "frame", geo.merge(*[rifle_box(0.70 + 0.16 * i, 0.76 + 0.16 * i, 0.30, 0.64, -0.12, 0.12, 0.02) for i in range(5)]), 3)
    return rifle_pt(1.56, 0.465, 0.0)


def torso_details(P):
    hinge = geo.tube((1.02, -0.22, 4.45), (1.02, 0.22, 4.45), 0.05, 14)   # recessed into the nose bottom
    P.add("Hatch_Hinge", "J_Hatch", "frame", C.leaned(hinge, LEAN), 2, hub=True)
    stripe = geo.sweep_rect([(1.16, 0.0, 4.55), (1.29, 0.0, 4.80), (1.11, 0.0, 5.10), (0.71, 0.0, 5.38)], 0.10, 0.05, up=(1, 0, 0.3))
    P.add("Hatch_Stripe", "J_Hatch", "sec", C.leaned(stripe, LEAN), 2)
    yi = C.torso_y(4.62, 0.05) - 0.01
    g = geo.grille((0.05, yi, 4.62), (0, 1, 0), (1, 0, 0), 0.44, 0.26, 3, 0.02, 0.05)
    P.add("Side_Intakes", "J_Torso", "frame", C.leaned(geo.merge(g, geo.mirror(g)), LEAN), 3)
    bl = [geo.tube((x, C.torso_y(4.80, x) - 0.01, 4.80), (x, C.torso_y(4.80, x) + 0.02, 4.80), 0.022, 6) for x in np.linspace(0.30, -0.60, 7)]
    P.add("Torso_Bolts", "J_Torso", "frame", C.leaned(geo.merge(*bl, *[geo.mirror(b) for b in bl]), LEAN), 3)
    band = geo.loft([(4.02, geo.ellipse(0.0, 0, 0.37, 0.37, 20)), (4.07, geo.ellipse(0.0, 0, 0.37, 0.37, 20))])
    P.add("Torso_Band", "J_Torso", "frame", C.leaned(band, LEAN), 2)


def forearm_guard(P):
    y = R.SH_Y + 0.24
    guard = geo.lathe((0.02, y - 0.02, 3.10), (0.02, y + 0.06, 3.10), [(0, 0.22), (0.6, 0.24), (1, 0.18)], 18)
    P.add("Forearm_Guard_L", "J_Elbow_L", "sec", guard, 2)


LEAN_PIVOT_Z = 4.35   # higher than the waist (3.98): the extra lean tips the chest, not the torso bottom into the pelvis


def build():
    R.LEAN_PIVOT[:] = (0.0, 0.0, LEAN_PIVOT_Z)
    P = C.Parts()
    C.torso_shell(P, CODE, LEAN, body_slot="pri", hatch_slot="pri")
    C.pelvis(P, collar_slot="pri", waist_slot="pri")
    C.thigh(P, "L2")
    C.shin_foot(P, "L2")
    C.upper_arm(P, "L", plate=True)
    C.upper_arm(P, "R", plate=False)    # right shoulder near bare (swing room for the sword)
    for s in "LR":
        C.forearm(P, s)
        C.hand(P, s)
    pauldron(P)
    skirt(P)
    optic_c, optic_lens = optic(P)
    grip = sword(P)
    muzzle = shotgun(P)
    back(P)
    torso_details(P)
    forearm_guard(P)
    socks = C.base_sockets(LEAN)
    joints = {
        "J_Hatch": ("J_Torso", R.lean(C.HINGE_UP, LEAN)),
        "J_Optic": ("J_Torso", optic_c),
        "W_Shotgun": ("J_Wrist_R", tuple(WR)),
    }
    socks.update({
        "S_Sword_Back": ("J_Torso", grip),
        "S_Sword_R": ("J_Wrist_R", (0.0, -R.SH_Y, R.WR_Z - 0.30)),
        "S_Muzzle": ("W_Shotgun", muzzle),
        "S_Holster": ("J_Pelvis", (-0.62, -0.80, 3.30)),
        "S_Phase": ("J_Torso", R.lean((-0.10, 0.0, 4.90), LEAN)),
        "S_Optic": ("J_Optic", optic_lens),
        "S_Thrust": ("J_Torso", R.lean((-0.86, 0.0, 4.30), LEAN)),
        "S_Vent_L": ("J_Torso", (-0.68, 1.30, 5.30)),
        "S_Vent_R": ("J_Torso", (-0.64, -1.00, 5.22)),
    })
    weapon = dict(root="W_Shotgun", sword_root="S_Sword_Back", sword_len=SW_LEN)
    return P, joints, socks, weapon


EXCLUDED_NAMES = [("Torso_Upper", "Hatch"),
                  ("Sword_Blade", "Rack_Clamps"), ("Sword_Blade", "Rack"), ("Sword_Edge", "Rack_Clamps"), ("Sword_Fuller", "Rack_Clamps"),
                  ("Sword_Hilt", "Rack")]   # the blade sits in its rack on purpose
SHOULDER_PARTS = ("Pauldron_L", "Pauldron_Lames_L", "Shoulder_Cap_R", "UpperArm_Hub_R")


def shoulder_armour_check(span):
    L = C.shoulder_check(span, ["Pauldron_L"], R.SH_Y, 0.27, 1)
    Rr = C.shoulder_check(span, ["Shoulder_Cap_R"], R.SH_Y, 0.27, -1)
    Rr["note"] = "right shoulder near bare by design (user spec 4.4); the 0.45 rule is applied to the left pauldron only"
    return dict(ok=L["ok"], left=L, right_info=Rr, rule="SPEC 3.1 rule 7: >= 0.45 thick and over the arm top (left pauldron)")


def hatch_opening():
    return C.hatch_opening()


REQUIRED_NAMES = (["J_Pelvis", "J_Waist", "J_Torso", "J_Hatch", "J_Optic", "W_Shotgun", "S_Muzzle", "S_Eye", "S_Seat", "S_Chest", "S_Embark", "S_Rodeo",
                   "S_Thrust", "S_Vent_L", "S_Vent_R", "S_Optic", "S_Sword_Back", "S_Sword_R", "S_Holster", "S_Phase", "S_Dmg_Torso_F", "S_Dmg_Torso_B"]
                  + ["%s_%s" % (n, s) for s in "LR" for n in ("J_Shoulder", "J_Elbow", "J_Wrist", "J_Hip", "J_Knee", "J_Ankle", "J_Wing", "S_Hand", "S_Foot",
                                                             "S_Dmg_Shoulder", "S_Dmg_Elbow", "S_Dmg_Thigh", "S_Dmg_Knee")]
                  + ["J_Finger_%s_%d" % (s, i) for s in "LR" for i in (1, 2, 3)])


def extra_renders(objs, meshes, solved, h):
    """Sword drawn: the sword parts moved from the back rack to the right hand, for one picture (the file keeps it on the back)."""
    import bpy
    from mathutils import Matrix
    hold = solved["melee_L"] if "melee_L" in solved else solved["stand_aim"]
    p, off = solved["stand_aim"]
    pose = dict(p, s_flex_R=70, e_R=20, s_in_R=10, wr_pitch_R=-60)
    p2, off2 = h["solve"](pose)
    sw_obs = [o for n, o in meshes.items() if n.startswith("Sword_")]
    back = objs["S_Sword_Back"]
    hand = objs["S_Sword_R"]
    saved = [(o, o.parent, o.matrix_parent_inverse.copy()) for o in sw_obs]
    # sword frame on the back, in back-socket space -> place the grip in the hand, blade along the forearm (rest -z), edge forward
    import numpy as _np
    d = R.geo.Ry(LEAN) @ SW_DIR
    wv = R.geo.Ry(LEAN) @ SW_W
    Cm = _np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float)
    src = _np.column_stack([d, wv, _np.cross(d, wv)])
    dst_d, dst_w = _np.array((0.0, 0.0, -1.0)), _np.array((-1.0, 0.0, 0.0))
    dst = _np.column_stack([dst_d, dst_w, _np.cross(dst_d, dst_w)])
    Rm = Cm @ (dst @ src.T) @ Cm.T
    M = Matrix(Rm.tolist()).to_4x4()
    for o in sw_obs:
        o.parent = hand
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = M
    shot = [o for n, o in meshes.items() if n.startswith("Shotgun")]
    for o in shot:
        o.hide_render = True
    bpy.context.view_layer.update()
    h["setup"]((1000, 1000), h["mode"])
    h["helper"]("human", (3.6, 1.2))
    if h["mode"] == "color":
        h["helper"]("ground"); h["lights"]()
    h["camera"]((10.5, -14.0, 6.0), (0.0, -0.8, 3.0), lens=50)
    h["render"](__import__("os").path.join(h["out"], "%s_3q_sword_drawn.png" % h["mode"]))
    h["clear"]()
    for o, par, inv in saved:
        o.parent = par
        o.matrix_parent_inverse = inv
        o.matrix_basis = Matrix.Identity(4)
    for o in shot:
        o.hide_render = False
    bpy.context.view_layer.update()
