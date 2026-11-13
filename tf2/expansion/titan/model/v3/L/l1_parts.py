"""L-1 Beichen (北辰): light chassis, long-range, hover. Parts, extra joints and sockets. No bpy.
SPEC v1.2 + user spec 4.3. World rest coordinates, analysis axes (x forward, y left, z up)."""
import math

import numpy as np

import geo
import light_common as C
import light_rig as R

CODE = "L1"
LEAN = 8.0       # torso shell leans forward 8 deg about the waist; the bullet nose itself points forward
COLORS = dict(pri="#22344F", sec="#E4E0D6", frame="#2A2D31", emit="#2FE6FF")

WR = np.array((0.0, -R.SH_Y, R.WR_Z))   # right wrist, rest
RIFLE_DU = 0.0   # whole gun moved away from (+) / toward (-) the forearm axis
RIFLE_DV = 0.0   # whole gun shifted toward the body (+) / outward (-)


def rifle_pt(s, u, v):
    """Rifle frame at the right wrist (rest: arm hanging). s along the barrel (rest -z), u below the forearm in the aim pose
    (rest -x), v toward the body (rest +y)."""
    return (float(-(u + RIFLE_DU)), float(WR[1] + v + RIFLE_DV), float(WR[2] - s))


def rifle_box(s0, s1, u0, u1, v0, v1, ch=0.04):
    """Box in rifle coordinates, chamfered along the barrel edges."""
    secs = []
    for s in (s0, s1):
        pts = [(u0 + ch, v0), (u1 - ch, v0), (u1, v0 + ch), (u1, v1 - ch), (u1 - ch, v1), (u0 + ch, v1), (u0, v1 - ch), (u0, v0 + ch)]
        secs.append([rifle_pt(s, u, v) for u, v in pts])
    return geo.loft3(secs)


def rifle_tube(s0, s1, u, v, r, seg=14, r2=None):
    return geo.tube(rifle_pt(s0, u, v), rifle_pt(s1, u, v), r, seg, r2)


def hand_grip(P, prefix, root, s_front, u_top):
    """R5 round: what the right fist holds, made readable (lead 11-12 #2). Stirrup grip.
    The claw is two fingers (far side) and a thumb (gun side) curling toward each other; they close on a SIDEWAYS bar. So the
    gun carries a closed light-coloured frame on its top: two cheeks (v +-0.19..0.23, outside the fingers), the crossbar the
    claw holds (s 0.40, u 0, r 0.055; fingers curl 25 deg and touch it from both sides) and a front bar in front of the finger
    tips that closes the frame (hand guard). First try (kept in README, not used): a pistol grip block + an open D-bow on the
    outer side; in the close-up the bow stood 0.3 m clear of the hand and read as a carry handle, the claw looked like it rested
    on the block. All on the weapon root (one bone). s_front: front bar position."""
    def cheek(v0, v1):
        """Tapered bracket: wide foot on the gun top (s 0.28-0.58), narrow at the crossbar (s 0.33-0.47), so the claw
        shows from the side (a full-height plate hid it; close-up r5_i1/r5 first build)."""
        secs = []
        for (sa, sb), u in (((0.33, 0.47), -0.09), ((0.28, 0.58), u_top + 0.03)):
            secs.append([rifle_pt(ss, u, vv) for ss, vv in ((sa, v0), (sb, v0), (sb, v1), (sa, v1))])
        return geo.loft3(secs)
    front_post = lambda v0, v1: rifle_box(s_front - 0.035, s_front + 0.035, -0.06, u_top + 0.02, v0, v1, 0.01)
    cross = geo.tube(rifle_pt(0.40, 0.0, -0.21), rifle_pt(0.40, 0.0, 0.21), 0.055, 12)
    front = geo.tube(rifle_pt(s_front, -0.06, -0.21), rifle_pt(s_front, -0.06, 0.21), 0.04, 10)
    P.add(prefix + "_Grip", root, "sec", geo.merge(cheek(-0.23, -0.19), cheek(0.19, 0.23), cross, front,
                                                    front_post(-0.23, -0.19), front_post(0.19, 0.23)), 1, hub=True)


def rifle(P):
    """R5: barrel line 0.32 below the forearm axis (r4: 0.44) and stock 0.14 shorter, so the gun sits on the fist and clears the
    knees in crouch / crouch_yaw_85 (diag: du -0.14 cleared crouch). Total length 4.20 m (r4 4.34)."""
    U, UT = 0.32, 0.20   # barrel axis, receiver top
    P.add("Rifle_Receiver", "W_Rifle", "pri", geo.merge(rifle_box(-0.80, 0.98, UT, 0.46, -0.15, 0.15, 0.06),
                                                         rifle_box(-0.55, 0.80, 0.46, 0.53, -0.11, 0.11, 0.03)), 1, panel=True)
    # r5b: stock top lowered to u 0.24 (clears the bigger elbow hub). Stock underside kept at u <= 0.40: the butt corner at u 0.46-0.54 went 0.08 into the left thigh plate in crouch_yaw_85 (diag)
    P.add("Rifle_Stock", "W_Rifle", "sec", geo.merge(rifle_box(-1.18, -0.78, 0.24, 0.38, -0.10, 0.10, 0.05),
                                                       rifle_box(-1.20, -1.08, 0.24, 0.40, -0.12, 0.12, 0.04)), 1)
    hand_grip(P, "Rifle", "W_Rifle", 0.66, UT)
    P.add("Rifle_Shroud", "W_Rifle", "pri", geo.merge(rifle_tube(0.98, 2.24, U, 0.0, 0.14, 16, 0.12),
                                                      rifle_box(0.98, 1.80, U - 0.05, U + 0.05, -0.17, 0.17, 0.02)), 1, panel=True)
    P.add("Rifle_Barrel", "W_Rifle", "frame", geo.merge(rifle_tube(2.24, 2.86, U, 0.0, 0.075, 14), rifle_tube(2.86, 2.98, U, 0.0, 0.12, 14),
                                                        rifle_tube(2.98, 3.00, U, 0.0, 0.09, 14)), 1)
    # scope on the outer side, behind the guard (the top of the gun is the fist)
    P.add("Rifle_Scope", "W_Rifle", "frame", geo.merge(rifle_tube(-0.55, 0.30, 0.30, -0.31, 0.085, 12), rifle_box(-0.35, 0.10, 0.26, 0.34, -0.25, -0.14, 0.01)), 2)
    P.add("Rifle_Vents", "W_Rifle", "frame", geo.merge(*[rifle_box(1.04 + 0.12 * i, 1.10 + 0.12 * i, U - 0.10, U + 0.10, 0.168, 0.185, 0.0) for i in range(6)]), 3)
    # charge ticks (emissive): 8 short bars on the inner side of the receiver
    P.add("Rifle_Charge", "W_Rifle", "emit", geo.merge(*[rifle_box(0.10 + 0.11 * i, 0.16 + 0.11 * i, 0.27, 0.41, 0.150, 0.162, 0.0) for i in range(8)]), 2)
    P.add("Rifle_Bolts", "W_Rifle", "frame", geo.merge(*[geo.tube(rifle_pt(s, 0.28, -0.15), rifle_pt(s, 0.28, -0.175), 0.018, 6) for s in (-0.7, -0.3, 0.1, 0.5)],
                                                       *[geo.tube(rifle_pt(s, 0.40, -0.15), rifle_pt(s, 0.40, -0.175), 0.018, 6) for s in (-0.7, -0.3, 0.1, 0.5, 0.9)]), 3)
    return rifle_pt(3.00, U, 0.0)


def mantle(P):
    """Torso-fixed shoulder block (M-1 decision 4 scheme A). Front-view profile: underside 4.97 over the arm hub (0.49 thick there),
    outer wedge down to 4.50 sloping away from the hub, top rising inward to 5.58 so it runs into the torso top in one line."""
    # inner part (over the torso, kept behind the canopy door) and outer part (over the arm hub, full depth)
    inner = geo.extrude([(0.50, 4.97), (0.84, 4.97), (0.84, 5.62), (0.50, 5.68)], "yz", -0.58, 0.16)
    prof = [(0.80, 4.97), (1.47, 4.97), (1.58, 4.50), (1.74, 4.56), (1.78, 5.00), (1.66, 5.42), (0.95, 5.60), (0.80, 5.62)]
    slab = geo.extrude(prof, "yz", -0.58, 0.48)
    nose = geo.extrude([(0.84, 5.00), (1.44, 5.00), (1.70, 5.04), (1.62, 5.38), (0.95, 5.52), (0.84, 5.54)], "yz", 0.47, 0.60)
    P.pair("Mantle", "J_Torso", "pri", geo.merge(inner, slab, nose), 1, panel=True)
    lip = geo.extrude([(0.70, 5.02), (1.60, 5.06), (1.56, 5.16), (0.70, 5.12)], "yz", 0.59, 0.63)
    P.pair("Mantle_Lip", "J_Torso", "sec", lip, 2)
    ridge = geo.loft([(5.46, geo.rect(-0.40, 0.24, 1.18, 1.36, 0.04)), (5.60, geo.rect(-0.34, 0.18, 1.20, 1.34, 0.03))])
    P.pair("Mantle_Ridge", "J_Torso", "frame", ridge, 2)
    P.pair("Mantle_Bolts", "J_Torso", "frame", geo.merge(geo.bolts_line((-0.30, 1.75, 5.20), (0.30, 1.75, 5.20), (0, 1, 0), 0.022, 5),
                                                         geo.bolts_line((-0.30, 1.75, 4.80), (0.20, 1.75, 4.80), (0, 1, 0), 0.022, 4)), 3)


def optic(P):
    """Three small lenses stacked vertically at the front-left of the torso, on J_Optic."""
    c_up = np.array((0.18, C.torso_y(5.02, 0.18) + 0.02, 5.02))
    face = np.array((0.45, 0.89, 0.0)); face /= np.linalg.norm(face)
    up = np.array((0.0, 0.0, 1.0))
    side = np.cross(up, face)
    def at(a, b, c):  # along face, side, up
        return c_up + a * face + b * side + c * up
    secs = []
    for c in (-0.32, 0.32):
        secs.append([at(a, b, c) for a, b in ((0.06, -0.11), (0.06, 0.11), (-0.14, 0.11), (-0.14, -0.11))])
    housing = geo.loft3(secs)
    P.add("Optic_Housing", "J_Optic", "frame", C.leaned(housing, LEAN), 1, hub=True)
    lenses = geo.merge(*[geo.tube(at(0.05, 0.0, z), at(0.10, 0.0, z), 0.068, 16) for z in (-0.19, 0.0, 0.19)])
    rims = geo.merge(*[geo.tube(at(0.04, 0.0, z), at(0.075, 0.0, z), 0.09, 16) for z in (-0.19, 0.0, 0.19)])
    P.add("Optic_Rims", "J_Optic", "frame", C.leaned(rims, LEAN), 2, hub=True)
    P.add("Optic_Lenses", "J_Optic", "emit", C.leaned(lenses, LEAN), 1, hub=True)
    return R.lean(c_up, LEAN), R.lean(at(0.10, 0.0, 0.0), LEAN)


def wing(P, side):
    """Modelled deployed in the wing frame (root at origin, span +y, leading edge +x, top +z), folded by light_rig.wing_fold."""
    sg = 1 if side == "L" else -1
    F = R.wing_fold("L")
    root = np.array(R.WING_ROOT)
    def W(mesh):   # wing frame -> world rest (folded), left side; right mirrored afterwards
        v, f = mesh
        a = np.array(v, float) @ F.T + root
        return [tuple(p) for p in a], f
    span = R.WING_SPAN
    def sec(y, xl, xt, t):
        return (y, [(xl, t * 0.3), (xl - 0.06, t), (xt + 0.05, t * 0.6), (xt, 0.0), (xt + 0.05, -t * 0.5), (xl - 0.06, -t * 0.7)])
    secs = [sec(0.10, 0.16, -0.62, 0.075), sec(0.9, 0.00, -0.60, 0.06), sec(span - 0.05, -0.16, -0.56, 0.045)]
    panel = geo.loft3([[(x, y, z) for x, z in pts] for y, pts in secs])
    top = geo.loft3([[(x, y, z) for x, z in [(xl - 0.10, t * 1.0 + 0.012), (xt + 0.10, t * 0.6 + 0.012), (xt + 0.10, t * 0.6 + 0.03), (xl - 0.10, t + 0.03)]]
                     for y, xl, xt, t in ((0.18, 0.10, -0.55, 0.075), (span - 0.25, -0.16, -0.50, 0.045))])
    hub = geo.lathe((-0.18, -0.06, 0.0), (-0.18, 0.30, 0.0), [(0, 0.12), (0.2, 0.16), (0.8, 0.16), (1, 0.11)], 16)
    root_thr = geo.lathe((-0.10, 0.18, -0.02), (-0.70, 0.18, -0.02), [(0, 0.10), (0.3, 0.13), (1, 0.15)], 14)
    vt_c = (-0.36, span - 0.06)
    nacelle = geo.lathe((vt_c[0], vt_c[1], 0.14), (vt_c[0], vt_c[1], -0.20), [(0, 0.10), (0.25, 0.15), (0.85, 0.15), (1, 0.13)], 18)
    vt_ring = geo.tube((vt_c[0], vt_c[1], -0.20), (vt_c[0], vt_c[1], -0.215), 0.11, 18, 0.08)
    pod_y = 0.95
    pod = geo.merge(geo.box((0.08, pod_y, 0.13), (0.24, 0.12, 0.07), 0.03),
                    *[geo.tube((0.30, pod_y + dy, 0.13), (0.34, pod_y + dy, 0.13), 0.045, 10) for dy in (-0.075, 0.0, 0.075)])
    parts = [("Wing_Hub", "frame", hub, 1, True), ("Wing", "pri", panel, 1, False), ("Wing_Top", "sec", top, 2, False),
             ("Wing_Thruster", "frame", root_thr, 2, False), ("Wing_Nacelle", "sec", nacelle, 1, False), ("Wing_VTOL", "emit", vt_ring, 2, False),
             ("Wing_Pod", "frame", pod, 2, False)]
    ribs = geo.merge(*[geo.loft3([[(x, y, z) for x, z in ((0.0 - 0.18 * y / span, 0.0), (-0.55, 0.0), (-0.55, 0.075 - 0.02 * y), (0.0 - 0.18 * y / span, 0.08 - 0.02 * y))]
                                 for y in (yy - 0.02, yy + 0.02)]) for yy in (0.45, 1.3)])
    parts.append(("Wing_Ribs", "frame", ribs, 3, False))
    for nm, slot, mesh, st, hb in parts:
        m = W(mesh)
        if side == "R":
            m = geo.mirror(m)
        P.add("%s_%s" % (nm, side), "J_Wing_" + side, slot, m, st, hub=hb)
    def wp(x, y, z):
        p = F @ np.array((x, y, z)) + root
        return (float(p[0]), float(sg * p[1]), float(p[2]))
    sockets = {"S_VTOL_" + side: wp(vt_c[0], vt_c[1], -0.22), "S_Pod_" + side: wp(0.34, pod_y, 0.13)}
    for k, dy in enumerate((-0.075, 0.0, 0.075)):
        sockets["S_Rocket_%d" % (k + 1 + (0 if side == "L" else 3))] = wp(0.34, pod_y + dy, 0.13)
    return sockets


def back(P):
    # spine ridge, wing booms from the spine to the wing roots, asymmetric thruster (right of centre, low), mantle louvres only on
    # the right (left carries radiator fins): nothing reads as two eyes and a mouth from behind.
    spine = geo.loft([(4.30, geo.rect(-0.84, -0.60, -0.12, 0.12, 0.05)), (5.60, geo.rect(-0.80, -0.56, -0.10, 0.10, 0.05))])
    P.add("Spine", "J_Torso", "pri", C.leaned(spine, LEAN), 1)
    boom = geo.merge(geo.tube((-0.66, 0.10, 4.48), (-0.80, 0.86, 4.48), 0.13, 14), geo.box((-0.70, 0.30, 4.48), (0.14, 0.20, 0.16), 0.05))
    P.pair("Wing_Boom", "J_Torso", "frame", boom, 1, hub=True)
    thr = geo.merge(geo.lathe((-0.70, -0.30, 5.02), (-1.02, -0.30, 5.02), [(0, 0.20), (0.4, 0.22), (1, 0.17)], 18))
    P.add("Thruster", "J_Torso", "frame", C.leaned(thr, LEAN), 2)
    P.add("Thruster_Glow", "J_Torso", "emit", C.leaned(geo.tube((-1.02, -0.30, 5.02), (-1.03, -0.30, 5.02), 0.13, 16), LEAN), 3)
    louv = geo.grille((-0.61, -1.10, 5.16), (-1, 0, 0), (0, 1, 0), 0.60, 0.30, 4, 0.025, 0.05)
    P.add("Vent_R", "J_Torso", "frame", louv, 3)
    fins = geo.merge(*[geo.box((-0.64, 0.86 + 0.13 * i, 5.18), (0.05, 0.025, 0.18), 0.01) for i in range(6)])
    P.add("Radiator_L", "J_Torso", "frame", fins, 3)
    pipes = geo.merge(geo.sweep_rect([(-0.62, 0.16, 5.30), (-0.86, 0.30, 5.05), (-0.86, 0.50, 4.62)], 0.06, 0.06),
                      geo.sweep_rect([(-0.62, -0.16, 5.30), (-0.86, -0.36, 5.05), (-0.86, -0.50, 4.62)], 0.06, 0.06))
    P.add("Back_Pipes", "J_Torso", "frame", C.leaned(pipes, LEAN), 3)


def torso_details(P):
    # hatch frame strip and hinge, chest panel bolts, side intakes
    hinge = geo.tube((1.02, -0.22, 4.45), (1.02, 0.22, 4.45), 0.05, 14)   # recessed into the nose bottom
    P.add("Hatch_Hinge", "J_Hatch", "frame", C.leaned(hinge, LEAN), 2, hub=True)
    stripe = geo.sweep_rect([(1.16, 0.0, 4.55), (1.29, 0.0, 4.80), (1.11, 0.0, 5.10), (0.71, 0.0, 5.38)], 0.08, 0.05, up=(1, 0, 0.3))
    P.add("Hatch_Stripe", "J_Hatch", "frame", C.leaned(stripe, LEAN), 3)
    yi = C.torso_y(4.62, 0.05) - 0.01
    intake = geo.merge(geo.grille((0.05, yi, 4.62), (0, 1, 0), (1, 0, 0), 0.50, 0.28, 4, 0.02, 0.05),
                       geo.mirror(geo.grille((0.05, yi, 4.62), (0, 1, 0), (1, 0, 0), 0.50, 0.28, 4, 0.02, 0.05)))
    P.add("Side_Intakes", "J_Torso", "frame", C.leaned(intake, LEAN), 3)
    bl = [geo.tube((x, C.torso_y(4.62, x) - 0.01, 4.62), (x, C.torso_y(4.62, x) + 0.02, 4.62), 0.022, 6) for x in np.linspace(0.25, -0.55, 6)]
    bolts = geo.merge(*bl, *[geo.mirror(b) for b in bl])
    P.add("Torso_Bolts", "J_Torso", "frame", C.leaned(bolts, LEAN), 3)
    collar_band = geo.loft([(4.02, geo.ellipse(0.0, 0, 0.37, 0.37, 20)), (4.07, geo.ellipse(0.0, 0, 0.37, 0.37, 20))])
    P.add("Torso_Band", "J_Torso", "frame", C.leaned(collar_band, LEAN), 2)


def tether(P):
    """Tether launcher on the left forearm, outer side; muzzle points along the forearm (rest -z = forward in the aim pose)."""
    y = R.SH_Y + 0.29
    body = geo.loft([(3.26, geo.rect(-0.12, 0.20, y - 0.09, y + 0.09, 0.05)), (2.78, geo.rect(-0.10, 0.22, y - 0.09, y + 0.09, 0.05))])
    barrel = geo.tube((0.06, y, 2.78), (0.06, y, 2.62), 0.07, 14)
    P.add("Tether", "J_Elbow_L", "sec", geo.merge(body, barrel), 2, panel=True)
    P.add("Tether_Glow", "J_Elbow_L", "emit", geo.tube((0.06, y, 2.62), (0.06, y, 2.60), 0.045, 14), 3)
    return (0.06, y, 2.60)


def build():
    R.LEAN_PIVOT[:] = R.WAIST
    P = C.Parts()
    C.torso_shell(P, CODE, LEAN, body_slot="pri", hatch_slot="sec")
    C.pelvis(P)
    C.thigh(P, "L1")
    C.shin_foot(P, "L1")
    for s in "LR":
        C.upper_arm(P, s)
        C.forearm(P, s)
        C.hand(P, s)
    mantle(P)
    optic_c, optic_lens = optic(P)
    muzzle = rifle(P)
    tether_pt = tether(P)
    back(P)
    torso_details(P)
    socks = C.base_sockets(LEAN)
    for s in "LR":
        for k, v in wing(P, s).items():
            socks[k] = ("J_Wing_" + s, v)
    joints = {
        "J_Hatch": ("J_Torso", R.lean(C.HINGE_UP, LEAN)),
        "J_Optic": ("J_Torso", optic_c),
        "W_Rifle": ("J_Wrist_R", tuple(WR)),
    }
    socks.update({
        "S_Muzzle": ("W_Rifle", muzzle),
        "S_Optic": ("J_Optic", optic_lens),
        "S_Tether": ("J_Elbow_L", tether_pt),
        "S_Thrust": ("J_Torso", R.lean((-1.03, -0.30, 5.02), LEAN)),
        "S_Vent_L": ("J_Torso", (-0.66, 1.18, 5.18)),
        "S_Vent_R": ("J_Torso", (-0.66, -1.10, 5.16)),
    })
    weapon = dict(root="W_Rifle", length_m=4.20, note="right hand, barrel along the forearm, 0.32 below it in the aim pose; light grip + knuckle guard (R5)")
    return P, joints, socks, weapon


EXCLUDED_NAMES = [("Torso_Upper", "Hatch")]   # the closed door sits in the shell opening; its swing is checked against everything else

HAS_WINGS = True
SHOULDER_PARTS = ("Mantle_L", "Mantle_R")


def shoulder_armour_check(span):
    L = C.shoulder_check(span, ["Mantle_L"], R.SH_Y, 0.27, 1)
    Rr = C.shoulder_check(span, ["Mantle_R"], R.SH_Y, 0.27, -1)
    return dict(ok=L["ok"] and Rr["ok"], left=L, right=Rr, rule="SPEC 3.1 rule 7: >= 0.45 thick and over the arm top")


def hatch_opening():
    return C.hatch_opening()


REQUIRED_NAMES = (["J_Pelvis", "J_Waist", "J_Torso", "J_Hatch", "J_Optic", "W_Rifle", "S_Muzzle", "S_Eye", "S_Seat", "S_Chest", "S_Embark", "S_Rodeo",
                   "S_Thrust", "S_Vent_L", "S_Vent_R", "S_Optic", "S_Tether", "S_Dmg_Torso_F", "S_Dmg_Torso_B"]
                  + ["%s_%s" % (n, s) for s in "LR" for n in ("J_Shoulder", "J_Elbow", "J_Wrist", "J_Hip", "J_Knee", "J_Ankle", "J_Wing", "S_Hand", "S_Foot",
                                                             "S_Dmg_Shoulder", "S_Dmg_Elbow", "S_Dmg_Thigh", "S_Dmg_Knee", "S_VTOL", "S_Pod")]
                  + ["J_Finger_%s_%d" % (s, i) for s in "LR" for i in (1, 2, 3)] + ["S_Rocket_%d" % i for i in range(1, 7)])
