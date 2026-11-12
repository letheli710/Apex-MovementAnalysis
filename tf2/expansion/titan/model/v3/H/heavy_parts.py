"""Part tables for H-1 Forge and H-2 Legion (no bpy). World rest coordinates, analysis axes (x forward, y left, z up).

Each part = one object = one owner joint; a part is a list of shells (kind, material, mesh):
  kind 'base'   silhouette volume (round 1)
       'plate'  armor plates / seams / large secondary volumes added at the mid-poly round (round 2)
       'detail' bolts, grilles, hydraulics, hoses, belt links (round 3)
  material 'pri' | 'sec' | 'frame' | 'emit'  ->  MAT_Primary / MAT_Secondary / MAT_Frame / MAT_Emissive
Base and plate shells get a 3 cm bevel in Blender from round 2 on; details are not bevelled.
"""
import math
import os

import numpy as np

import heavy_geom as G
import heavy_rig as RIG
from heavy_geom import box, cyl, cyl_ab, loft, merge, mirror, rect, se_front_x, se_sect, tube, xform

# geometry below is authored on the A rig (rounds 1-4); build() maps it to the active rig with RIG.map_pt (R5, H-SK8)
SY, ZS, ZE, ZW = RIG.SH_Y, RIG.Z_SH, RIG.A["elbow"], RIG.A["wrist"]
HY, ZH, ZK, ZA = RIG.HIP_Y, RIG.A["hip"], RIG.A["knee"], RIG.A["ankle"]
FINGERS_A = {"J_Finger_L_1": (0.17, SY + 0.15, ZW - 0.30), "J_Finger_L_2": (0.17, SY - 0.15, ZW - 0.30), "J_Finger_L_3": (-0.17, SY, ZW - 0.30)}


class Parts:
    def __init__(self, code):
        self.code = code
        self.parts = {}   # name -> dict(joint, shells)

    def add(self, name, joint, kind, mat, mesh):
        p = self.parts.setdefault(name, dict(joint=joint, shells=[]))
        assert p["joint"] == joint, (name, joint)
        p["shells"].append((kind, mat, mesh))

    def mirrored(self, name_l, name_r, joint_r, shells):
        for kind, mat, mesh in shells:
            self.add(name_r, joint_r, kind, mat, mirror(mesh))


def side_shells(P, name):
    return list(P.parts[name]["shells"])


# ------------------------------------------------------------------ shared: pelvis, waist, legs, left arm hand
def pelvis_waist(P, style):
    c = 0.16 if style == "round" else 0.08
    P.add("Pelvis", "J_Pelvis", "base", "frame", loft([
        (2.05, rect(-0.50, 0.40, -0.52, 0.52, c)), (2.40, rect(-0.60, 0.50, -0.56, 0.56, c + 0.02)),
        (2.80, rect(-0.64, 0.46, -0.56, 0.56, c + 0.02)), (3.05, rect(-0.60, 0.30, -0.48, 0.48, c)),
        (3.25, rect(-0.52, 0.02, -0.36, 0.36, c - 0.04))]))
    # back skirt + short rear corner skirts (behind the thigh swing, x <= -0.52). Tops <= 3.15: a 45 deg bend in any direction
    # (twist 90 + bend 45) brings the torso cone down to z 3.22.
    back = loft([(2.40, rect(-0.86, -0.62, -0.96, 0.96, c * 0.6)), (3.15, rect(-0.80, -0.58, -0.90, 0.90, c * 0.6))])
    # R5: the corner tops stay at absolute z 3.10 when the pelvis rides up with the longer B legs (the twist 90 + bend 45 sweep of
    # the torso front edge comes down to 3.18 over them)
    corner = loft([(2.45, rect(-0.86, -0.52, 0.92, 1.30, c * 0.5)), (3.10 - RIG.D_HIP, rect(-0.80, -0.56, 0.90, 1.24, c * 0.5))])
    cod = loft([(2.02, rect(0.44, 0.64, -0.36, 0.36, c * 0.5)), (2.62, rect(0.46, 0.70, -0.42, 0.42, c * 0.5)),
                (2.96, rect(0.40, 0.56, -0.36, 0.36, c * 0.5))])
    if style == "round":
        girdle = G.revolve([(2.78, 0.66), (3.02, 0.96), (3.10, 0.94), (3.15, 0.86)], "z", (-0.04, 0.0), 48)
    else:
        girdle = loft([(2.78, rect(-0.70, 0.40, -0.62, 0.62, 0.10)), (3.02, rect(-0.96, 0.58, -0.94, 0.94, 0.20)),
                       (3.10, rect(-0.95, 0.57, -0.93, 0.93, 0.20)), (3.15, rect(-0.88, 0.52, -0.86, 0.86, 0.18))])
    P.add("Pelvis", "J_Pelvis", "base", "pri", merge(back, corner, mirror(corner), cod, girdle))
    # round 2: seam strip over the back skirt, lip on the codpiece
    P.add("Pelvis", "J_Pelvis", "plate", "frame", merge(
        box((-0.865, 0, 2.80), (0.02, 0.90, 0.03)),
        box((0.66, 0, 2.30), (0.04, 0.30, 0.025))))
    # round 3: rivets on skirts, hip axle caps
    pts = [(-0.87, y, z) for y in (-0.80, -0.40, 0.40, 0.80) for z in (2.52, 3.00)]
    det = [G.bolts(pts, (-1, 0, 0))]
    for s in (1, -1):
        det.append(G.bolts([(-0.70, s * 1.31, z) for z in (2.60, 2.95 - RIG.D_HIP)], (0, s, 0)))
    det.append(G.bolts([(0.71, y, 2.62) for y in (-0.28, 0.0, 0.28)], (1, 0, 0)))
    P.add("Pelvis", "J_Pelvis", "detail", "frame", merge(*det))
    # waist drum: rides J_Waist, the torso turns over it
    P.add("Waist", "J_Waist", "base", "sec", G.revolve([(3.05, 0.62), (3.42, 0.62), (3.52, 0.54)], "z", (0.0, 0.0), 40))
    P.add("Waist", "J_Waist", "detail", "frame", merge(*[box((0.63 * math.cos(a), 0.63 * math.sin(a), 3.28), (0.03, 0.03, 0.14))
                                                       for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]))


def leg_left(P, style):
    """Left leg; the right one is the mirror image. Thigh hub is a y drum (flex-invariant), body chamfered at the top so the
    hip flex sweep stays under the side skirt (z 2.86)."""
    c = 0.14 if style == "round" else 0.07
    th = []
    th.append(("base", "frame", cyl("y", (0, ZH), 0.32, HY - 0.335, HY + 0.345, 28)))
    th.append(("base", "pri", loft([(2.33, rect(-0.28, 0.28, HY - 0.32, HY + 0.32, c)), (2.15, rect(-0.40, 0.40, HY - 0.38, HY + 0.38, c)),
                                    (1.85, rect(-0.40, 0.42, HY - 0.39, HY + 0.39, c)), (1.55, rect(-0.18, 0.40, HY - 0.36, HY + 0.36, c * 0.8)),
                                    (1.22, rect(0.02, 0.34, HY - 0.30, HY + 0.30, c * 0.6))])))
    # outer thigh skirt: flares out at the top like a hip skirt, rides the thigh so the hip swing never hits it
    if style == "round":
        guard = loft([(2.66, rect(-0.30, 0.30, HY + 0.34, HY + 0.47, 0.06)), (2.40, rect(-0.42, 0.42, HY + 0.37, HY + 0.51, 0.07)),
                      (1.55, rect(-0.34, 0.38, HY + 0.36, HY + 0.49, 0.06))])
    else:
        guard = loft([(2.66, rect(-0.34, 0.34, HY + 0.34, HY + 0.47, 0.03)), (2.40, rect(-0.44, 0.44, HY + 0.37, HY + 0.51, 0.03)),
                      (1.60, rect(-0.40, 0.40, HY + 0.36, HY + 0.49, 0.03))])
    th.append(("base", "pri", guard))
    # front thigh plate (starts 0.55 below the hip so the flex sweep stays under the hip girdle)
    th.append(("plate", "pri", loft([(1.83, rect(0.38, 0.47, HY - 0.30, HY + 0.30, 0.04)), (1.40, rect(0.34, 0.45, HY - 0.28, HY + 0.28, 0.04))])))
    th.append(("plate", "frame", box((0.46, HY, 1.62), (0.02, 0.24, 0.02))))
    # hydraulic on the thigh back (both ends on the thigh)
    th.append(("detail", "frame", merge(cyl_ab((-0.43, HY - 0.18, 2.12), (-0.43, HY - 0.18, 1.90), 0.075, 12),
                                        cyl_ab((-0.43, HY + 0.18, 2.12), (-0.43, HY + 0.18, 1.90), 0.075, 12),
                                        cyl_ab((-0.43, HY, 1.95), (-0.21, HY, 1.50), 0.05, 10))))
    th.append(("detail", "frame", G.bolts([(0.0, HY + 0.50, z) for z in (1.80, 2.05, 2.30)] + [(0.28, HY + 0.50, z) for z in (1.9, 2.25)], (0, 1, 0))))
    th.append(("detail", "frame", G.bolts([(x, HY + 0.345, ZH) for x in (0.0,)], (0, 1, 0), r=0.12, h=0.04, seg=16)))
    for k, m, mesh in th:
        P.add("Thigh_L", "J_Hip_L", k, m, mesh)
    sh = []
    sh.append(("base", "pri", loft([(1.30, rect(-0.40, 0.46, HY - 0.43, HY + 0.44, c)), (1.02, rect(-0.50, 0.56, HY - 0.47, HY + 0.48, c + 0.02)),
                                    (0.62, rect(-0.46, 0.52, HY - 0.45, HY + 0.46, c + 0.02)), (0.42, rect(-0.38, 0.44, HY - 0.39, HY + 0.40, c))])))
    # thick knee guard
    if style == "round":
        kg = loft([(1.56, rect(0.40, 0.62, HY - 0.30, HY + 0.30, 0.10)), (1.22, rect(0.52, 0.80, HY - 0.36, HY + 0.36, 0.12)),
                   (0.80, rect(0.50, 0.70, HY - 0.32, HY + 0.32, 0.10))])
    else:
        kg = loft([(1.56, rect(0.40, 0.64, HY - 0.36, HY + 0.36, 0.05)), (1.25, rect(0.52, 0.82, HY - 0.40, HY + 0.40, 0.05)),
                   (0.80, rect(0.50, 0.72, HY - 0.36, HY + 0.36, 0.05))])
    sh.append(("base", "pri", kg))
    sh.append(("plate", "frame", merge(box((0.0, HY + 0.485, 0.82), (0.36, 0.02, 0.025)), box((0.0, HY - 0.475, 0.82), (0.36, 0.02, 0.025)))))
    sh.append(("plate", "frame", box((-0.51, HY, 0.80), (0.03, 0.30, 0.22))))     # calf vent plate
    sh.append(("detail", "frame", merge(G.slats(-0.545, HY - 0.26, HY + 0.26, 0.62, 0.98, 6, depth=0.04, axis="x"),
                                        cyl_ab((-0.47, HY - 0.30, 1.20), (-0.43, HY - 0.30, 0.50), 0.07, 12),
                                        cyl_ab((-0.47, HY + 0.30, 1.20), (-0.43, HY + 0.30, 0.50), 0.07, 12))))
    sh.append(("detail", "frame", G.bolts([(0.75, HY + y, z) for y in (-0.25, 0.25) for z in (1.0, 1.3)], (1, 0, 0.2))))
    for k, m, mesh in sh:
        P.add("Shin_L", "J_Knee_L", k, m, mesh)
    ft = []
    fc = 0.12 if style == "round" else 0.06
    ft.append(("base", "pri", loft([(0.00, rect(-0.66, 0.84, HY - 0.60, HY + 0.60, fc)), (0.22, rect(-0.62, 0.82, HY - 0.59, HY + 0.59, fc)),
                                      (0.38, rect(-0.44, 0.58, HY - 0.46, HY + 0.46, fc)), (0.48, rect(-0.28, 0.38, HY - 0.36, HY + 0.36, fc * 0.8))])))
    ft.append(("base", "frame", loft([(0.00, rect(-0.78, -0.58, HY - 0.30, HY + 0.30, 0.05)), (0.20, rect(-0.70, -0.58, HY - 0.26, HY + 0.26, 0.05))])))
    ft.append(("plate", "frame", loft([(0.23, rect(-0.40, 0.70, HY - 0.52, HY + 0.52, 0.06)), (0.36, rect(-0.30, 0.56, HY - 0.44, HY + 0.44, 0.06))])))
    ft.append(("plate", "frame", loft([(-0.005, rect(-0.67, 0.85, HY - 0.61, HY + 0.61, fc)), (0.07, rect(-0.67, 0.85, HY - 0.61, HY + 0.61, fc))])))
    ft.append(("detail", "frame", merge(*[box((x, HY, 0.025), (0.035, 0.58, 0.03)) for x in np.linspace(-0.55, 0.75, 9)])))   # tread
    ft.append(("detail", "frame", G.bolts([(x, HY + s * 0.53, 0.30) for x in (-0.2, 0.2, 0.5) for s in (-1, 1)], lambda p: (0, 1 if p[1] > HY else -1, 0))))
    for k, m, mesh in ft:
        P.add("Foot_L", "J_Ankle_L", k, m, mesh)
    # toes: two pieces on J_Ankle (no toe bone, SPEC 0 #7)
    toes = []
    for y0, y1 in ((HY - 0.58, HY - 0.03), (HY + 0.03, HY + 0.58)):
        toes.append(loft([(0.00, rect(0.80, 1.08, y0, y1, 0.06)), (0.18, rect(0.80, 1.04, y0 + 0.02, y1 - 0.02, 0.06)),
                          (0.30, rect(0.80, 0.92, y0 + 0.04, y1 - 0.04, 0.04))]))
    P.add("Toe_L", "J_Ankle_L", "base", "pri", merge(*toes))
    P.add("Toe_L", "J_Ankle_L", "detail", "frame", merge(*[box((1.09, (a + b) / 2, 0.06), (0.03, (b - a) / 2 - 0.04, 0.05))
                                                         for a, b in ((HY - 0.58, HY - 0.03), (HY + 0.03, HY + 0.58))]))
    for src, dst, j in (("Thigh_L", "Thigh_R", "J_Hip_R"), ("Shin_L", "Shin_R", "J_Knee_R"), ("Foot_L", "Foot_R", "J_Ankle_R"), ("Toe_L", "Toe_R", "J_Ankle_R")):
        P.mirrored(src, dst, j, side_shells(P, src))


def upper_arm(P, side, style):
    s = 1 if side == "L" else -1
    j = "J_Shoulder_" + side
    yc = s * SY
    c = 0.10 if style == "round" else 0.05
    # shoulder drum on the flex axis (y): turning the arm forward/back never changes its outline; ends chamfered for the abduction
    P.add("UpperArm_" + side, j, "base", "frame", G.revolve([(yc - 0.40, 0.26), (yc - 0.30, 0.40), (yc + 0.30, 0.40), (yc + 0.40, 0.26)], "y", (0.0, ZS), 40))
    P.add("UpperArm_" + side, j, "base", "pri", loft([(4.62, rect(-0.27, 0.27, yc - 0.26, yc + 0.26, c)), (4.45, rect(-0.32, 0.32, yc - 0.31, yc + 0.31, c)),
                                                       (3.92, rect(-0.29, 0.29, yc - 0.29, yc + 0.29, c))]))
    plate = loft([(4.40, rect(-0.24, 0.24, -0.04, 0.03, 0.02)), (3.98, rect(-0.22, 0.22, -0.04, 0.03, 0.02))])
    P.add("UpperArm_" + side, j, "plate", "pri", xform(plate, t=(0, yc + s * 0.33, 0)))
    P.add("UpperArm_" + side, j, "detail", "frame", merge(
        cyl_ab((0.33, yc - 0.12, 4.38), (0.33, yc - 0.12, 3.98), 0.05, 10), cyl_ab((0.33, yc + 0.12, 4.38), (0.33, yc + 0.12, 3.98), 0.05, 10),
        G.bolts([(0.0, yc + s * 0.365, z) for z in (4.05, 4.33)], (0, s, 0))))


def hand_left(P, style):
    yc = SY
    P.add("Hand_L", "J_Wrist_L", "base", "frame", loft([(2.70, rect(-0.24, 0.26, yc - 0.26, yc + 0.26, 0.08)), (2.42, rect(-0.22, 0.25, yc - 0.25, yc + 0.25, 0.08)),
                                                        (2.30, rect(-0.15, 0.19, yc - 0.20, yc + 0.20, 0.06))]))
    P.add("Hand_L", "J_Wrist_L", "plate", "pri", loft([(2.68, rect(0.24, 0.30, yc - 0.22, yc + 0.22, 0.02)), (2.40, rect(0.23, 0.29, yc - 0.20, yc + 0.20, 0.02))]))
    for i, (jn, (fx, fy, fz)) in enumerate([(n, FINGERS_A[n]) for n in ("J_Finger_L_1", "J_Finger_L_2", "J_Finger_L_3")]):
        inward = -1 if fx > 0 else 1    # curl toward the palm centre
        seg1 = loft([(fz + 0.02, rect(fx - 0.09, fx + 0.09, fy - 0.08, fy + 0.08, 0.03)), (fz - 0.24, rect(fx - 0.08, fx + 0.08, fy - 0.07, fy + 0.07, 0.03))])
        tipx = fx + inward * 0.07
        seg2 = loft([(fz - 0.22, rect(tipx - 0.075, tipx + 0.075, fy - 0.065, fy + 0.065, 0.03)),
                     (fz - 0.44, rect(tipx + inward * 0.04 - 0.03, tipx + inward * 0.04 + 0.03, fy - 0.04, fy + 0.04, 0.012))])
        name = "Finger_L_%d" % (i + 1)
        P.add(name, jn, "base", "frame", merge(seg1, seg2))
        P.add(name, jn, "detail", "frame", cyl("y", (fx, fz), 0.07, fy - 0.10, fy + 0.10, 12))


# ------------------------------------------------------------------ shoulder domes (bell shells, fixed to J_Torso)
def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def rim_fn(s_sign, yc, lo=0.46, hi=0.54):
    """Rim height of the dome at azimuth phi; eq = the surface point at the equator, used for its sideways distance dy from the pivot.
    dy < lo is the arm's swing slot: the rim stays high there (ZS + 0.42, above the arm's top face when it is level). Past hi the wall
    comes down: to ZS - 0.06 on the outer side (covers the arm top, clear of a 30 deg abduction), ZS + 0.05 on the torso side.
    lo/hi are measured at the equator; the rim sits lower where the dome is ~13 % narrower, so the slot there is ~0.40 wide each side."""
    def rim(phi, eq):
        dy = (eq[1] - yc) * s_sign
        low = ZS - 0.06 if dy > 0 else ZS + 0.05
        return low + (ZS + 0.42 - low) * (1 - smooth((abs(dy) - lo) / (hi - lo)))
    return rim


def dome_left(p_out=2.0, rad=(0.72, 0.72, 0.72), c=(0.0, SY + 0.04, ZS + 0.34), r_in=(0.48, 0.60, 0.56), seg=48, rings=14):
    """Torso-fixed dome. The cavity is a rounded box (p 4) centred 0.02 above the shoulder pivot, long in y, so the arm's
    shoulder drum (r 0.42 on the flex axis, +-0.40 in y) turns inside it. The front and back walls stop at ZS + 0.42 over the
    drum (the drum fills that slot, so the dome reads solid from the front); outside the slot they come down."""
    return G.bell(c, rad, (0.0, SY, ZS + 0.02), r_in, (rim_fn(1, SY), rim_fn(1, SY, 0.44, 0.52)), p_out=p_out, seg=seg, rings=rings, p_in=4.0)


# ------------------------------------------------------------------ H-1 Forge
H1_BARREL = [(4.00, 0.86, 0.86, 0.86), (4.08, 1.25, 1.05, 1.08), (4.35, 1.35, 1.15, 1.15), (5.25, 1.35, 1.15, 1.15),
             (5.52, 1.22, 1.05, 1.04), (5.66, 1.02, 0.88, 0.86), (5.70, 0.85, 0.72, 0.70)]
H1_P = 2.4
H1_DOOR = (4.12, 5.22, 0.49, 1.16)       # z0, z1, half-width, recess x


def h1_barrel_at(z):
    T = H1_BARREL
    for (z0, *a), (z1, *b) in zip(T, T[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return [u + (v - u) * t for u, v in zip(a, b)]
    return list(T[-1][1:]) if z > T[-1][0] else list(T[0][1:])


def h1_barrel():
    z0, z1, hw, rx = H1_DOOR
    zs = sorted(set([r[0] for r in H1_BARREL] + [z0 - 0.01, z0 + 0.02, z1 - 0.02, z1 + 0.01]))
    secs = []
    for z in zs:
        af, ab, b = h1_barrel_at(z)
        clip = (lambda x, y: min(x, rx) if abs(y) < hw + 0.02 else x) if z0 + 0.01 < z < z1 - 0.01 else None
        secs.append((z, se_sect(af, ab, b, H1_P, 64, clip=clip)))
    return loft(secs)


def h1_parts():
    P = Parts("H1")
    pelvis_waist(P, "round")
    # torso lower: coned bottom for the 45 deg bend, r <= 0.58 so it clears the lifted thighs in the yaw 85 crouch
    # torso lower: 45 deg cone (boiler bottom). A 45 deg cone bent 45 deg in any direction lies flat at z 3.22, above the pelvis.
    P.add("Torso_Lower", "J_Torso", "base", "pri", G.revolve([(3.55, 0.30), (3.56, 0.40), (4.02, 0.86), (4.06, 0.86)], "z", (0.0, 0.0), 48))
    P.add("Torso_Lower", "J_Torso", "plate", "frame", G.revolve([(3.78, 0.645), (3.82, 0.70), (3.88, 0.70), (3.90, 0.70)], "z", (0.0, 0.0), 48))
    P.add("Torso_Lower", "J_Torso", "detail", "frame", merge(*[cyl_ab((0.5 * math.cos(a), 0.5 * math.sin(a), 3.67), (0.83 * math.cos(a), 0.83 * math.sin(a), 4.00), 0.035, 8)
                                                              for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]))
    # barrel torso, hatch recess cut into the front
    P.add("Torso_Upper", "J_Torso", "base", "pri", h1_barrel())
    # round 2: seam bands (frame) around the barrel, a top cap, chest brow over the hatch
    bands = []
    for z in (4.36, 5.24):
        af, ab, b = h1_barrel_at(z)
        clip = lambda x, y: min(x, 1.17) if abs(y) < 0.53 else x
        bands.append(loft([(z - 0.035, se_sect(af + 0.02, ab + 0.02, b + 0.02, H1_P, 64, clip=clip)), (z + 0.035, se_sect(af + 0.02, ab + 0.02, b + 0.02, H1_P, 64, clip=clip))]))
    P.add("Torso_Upper", "J_Torso", "plate", "frame", merge(*bands))
    P.add("Torso_Upper", "J_Torso", "plate", "frame", loft([(5.66, se_sect(0.80, 0.70, 0.68, H1_P, 48)), (5.73, se_sect(0.62, 0.55, 0.52, H1_P, 48))]))
    brow = loft([(5.24, rect(1.14, 1.40, -0.62, 0.62, 0.06)), (5.36, rect(1.12, 1.34, -0.56, 0.56, 0.06))])
    P.add("Torso_Upper", "J_Torso", "plate", "pri", brow)
    # recess back wall (dark): shows when the hatch opens
    P.add("Torso_Upper", "J_Torso", "plate", "frame", box((1.155, 0, 4.67), (0.012, 0.47, 0.52)))
    # vents low on the barrel sides (S_Vent_L/R), amber inner wall
    for s in (1, -1):
        yv = s * 1.10
        vn = "Vent_" + ("L" if s > 0 else "R")
        P.add(vn, "J_Torso", "plate", "frame", box((-0.10, yv, 4.10), (0.30, 0.10, 0.20)))
        P.add(vn, "J_Torso", "plate", "emit", box((-0.10, s * 1.195, 4.10), (0.25, 0.006, 0.15)))
        P.add(vn, "J_Torso", "detail", "frame", G.slats(s * 1.215, -0.34, 0.14, 3.95, 4.25, 6, depth=0.04, axis="y"))
    # back: horizontal exhaust slot offset to the left (S_Thrust), not a round "mouth"
    P.add("Torso_Upper", "J_Torso", "plate", "frame", box((-1.04, 0.32, 4.10), (0.10, 0.32, 0.13)))
    P.add("Torso_Upper", "J_Torso", "detail", "frame", G.slats(-1.15, 0.04, 0.60, 3.99, 4.21, 4, depth=0.03, axis="x"))
    # fuel tanks (secondary), amber level windows, clamps, valves; S_Tank_L/R at the tops
    for s in (1, -1):
        cx, cy = -1.30, s * 0.55
        tn = "Tank_" + ("L" if s > 0 else "R")
        tank = G.revolve([(4.40, 0.24), (4.44, 0.30), (5.84, 0.30), (5.88, 0.24), (5.90, 0.18)], "z", (cx, cy), 32)
        P.add(tn, "J_Torso", "base", "sec", tank)
        a = math.radians(180 + s * 40)        # window faces back and outward
        n = (math.cos(a), math.sin(a))
        win = xform(box((0, 0, 0), (0.02, 0.055, 0.55)), G.Rz(math.degrees(a)), (cx + 0.30 * n[0], cy + 0.30 * n[1], 5.10))
        P.add(tn, "J_Torso", "plate", "emit", win)
        P.add(tn, "J_Torso", "plate", "frame", merge(*[cyl("z", (cx, cy), 0.315, z, z + 0.06, 32) for z in (4.62, 5.55)]))
        P.add(tn, "J_Torso", "detail", "frame", merge(cyl("z", (cx, cy), 0.08, 5.88, 5.94, 12),
                                                                cyl_ab((cx + 0.22, cy, 4.65), (-1.02, cy, 4.65), 0.05, 8),
                                                                cyl_ab((cx + 0.22, cy, 5.58), (-1.02, cy, 5.58), 0.05, 8),
                                                                G.bolts([(cx + 0.315 * math.cos(t), cy + 0.315 * math.sin(t), z + 0.03) for t in np.linspace(0, 2 * math.pi, 10, endpoint=False) for z in (4.62, 5.55)],
                                                                        lambda p, cx=cx, cy=cy: (p[0] - cx, p[1] - cy, 0), r=0.022, h=0.02, seg=6)))
    # asymmetric fuel plumbing: cross-feed low between the tanks, a hose from the left tank to the left dome
    P.add("Plumbing", "J_Torso", "detail", "frame", merge(
        tube([(-1.32, 0.30, 4.50), (-1.42, 0.10, 4.48), (-1.42, -0.20, 4.52), (-1.32, -0.30, 4.55)], 0.07, 10),
        tube([(-1.20, 0.82, 5.30), (-1.00, 1.05, 5.30), (-0.70, 1.15, 5.12), (-0.55, 1.20, 5.00)], 0.08, 10),
        tube([(-1.15, -0.80, 4.95), (-0.98, -1.00, 4.70), (-0.70, -1.10, 4.55)], 0.06, 10)))
    # shoulder domes (secondary), fixed to the torso; rim band in primary (round 2), bolts (round 3)
    dl = dome_left()
    P.add("Shoulder_L", "J_Torso", "base", "sec", dl)
    P.add("Shoulder_R", "J_Torso", "base", "sec", mirror(dl))
    for side, s in (("L", 1), ("R", -1)):
        cy = s * (SY + 0.04)
        ring = G.revolve([(ZS + 0.50, 0.725), (ZS + 0.58, 0.70)], "z", (0.0, cy), 48)    # band round the dome's widest line
        rib = loft([(ZS + 0.34, rect(-0.06, 0.06, min(cy + s * 0.70, cy + s * 0.745), max(cy + s * 0.70, cy + s * 0.745), 0.01)),
                    (ZS + 0.74, rect(-0.06, 0.06, min(cy + s * 0.40, cy + s * 0.53), max(cy + s * 0.40, cy + s * 0.53), 0.01))])
        P.add("Shoulder_" + side, "J_Torso", "plate", "pri", merge(ring, rib))
        bpts = [(0.715 * math.cos(t), cy + 0.715 * math.sin(t), ZS + 0.54) for t in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
        P.add("Shoulder_" + side, "J_Torso", "detail", "frame", G.bolts(bpts, lambda p, cy=cy: (p[0], p[1] - cy, 0), r=0.03, h=0.025, seg=8))
    # trap launcher on the right dome, 30 deg up from forward (S_Trap at the mouth)
    d = np.array([math.cos(math.radians(30)), 0, math.sin(math.radians(30))])
    base = np.array([0.10, -1.55, 5.58])
    P.add("Shoulder_R", "J_Torso", "plate", "frame", merge(cyl_ab(base, base + d * 0.50, 0.12, 20), box((0.05, -1.55, 5.62), (0.18, 0.16, 0.08))))
    P.add("Shoulder_R", "J_Torso", "detail", "frame", merge(cyl_ab(base + d * 0.44, base + d * 0.51, 0.14, 20), cyl_ab(base + d * 0.1, base + d * 0.16, 0.135, 20)))
    # hatch: door block filling the recess, proud of the barrel; hinge at its lower edge (J_Hatch)
    z0, z1, hw, rx = H1_DOOR
    def door_sect(z, inset=0.0):
        af, ab, b = h1_barrel_at(z)
        ys = np.linspace(-hw + inset, hw - inset, 11)
        front = [(se_front_x(af, b, y, H1_P) + 0.04, y) for y in ys]     # y from right to left
        return front + [(rx - 0.02, hw - inset), (rx - 0.02, -hw + inset)]
    secs = [(z0 + 0.005, door_sect(z0, 0.03)), (z0 + 0.06, door_sect(z0 + 0.06)), (z1 - 0.06, door_sect(z1 - 0.06)), (z1 - 0.005, door_sect(z1, 0.03))]
    P.add("Hatch", "J_Hatch", "base", "pri", loft(secs))
    # furnace door: three horizontal ribs, two hinge knuckles on the lower edge, a latch bar on the left edge
    ribs = []
    for z in (4.40, 4.67, 4.94):
        af, ab, b = h1_barrel_at(z)
        ribs.append(loft([(z - 0.035, [(se_front_x(af, b, y, H1_P) + 0.075, y) for y in np.linspace(-0.40, 0.40, 9)] + [(1.30, 0.40), (1.30, -0.40)]),
                          (z + 0.035, [(se_front_x(af, b, y, H1_P) + 0.075, y) for y in np.linspace(-0.40, 0.40, 9)] + [(1.30, 0.40), (1.30, -0.40)])]))
    P.add("Hatch", "J_Hatch", "plate", "frame", merge(*ribs))
    P.add("Hatch", "J_Hatch", "detail", "frame", merge(cyl("y", (1.33, 4.15), 0.07, -0.42, -0.22, 16), cyl("y", (1.33, 4.15), 0.07, 0.22, 0.42, 16),
                                                      box((1.43, 0.43, 4.67), (0.035, 0.035, 0.30)), box((1.45, 0.43, 4.67), (0.05, 0.05, 0.05)),
                                                      G.bolts([(1.425, y, z) for y in (-0.44, 0.44) for z in (4.27, 5.07)], (1, 0, 0))))
    # optic: single round lens offset to the right, in a grille shroud (J_Optic)
    ox, oy, oz = RIG.H1["optic"]
    P.add("Optic", "J_Optic", "base", "frame", cyl("x", (oy, oz), 0.24, ox - 0.10, ox + 0.16, 28))
    P.add("Optic", "J_Optic", "plate", "emit", cyl("x", (oy, oz), 0.15, ox + 0.16, ox + 0.195, 28))
    bars = [cyl_ab((ox + 0.15, oy + 0.21 * math.cos(t), oz + 0.21 * math.sin(t)), (ox + 0.29, oy + 0.21 * math.cos(t), oz + 0.21 * math.sin(t)), 0.022, 6)
            for t in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
    ringp = [(ox + 0.29, oy + 0.215 * math.cos(t), oz + 0.215 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 25)]
    P.add("Optic", "J_Optic", "plate", "frame", merge(tube(ringp, 0.03, 8), box((ox + 0.27, oy, oz), (0.015, 0.21, 0.018)), box((ox + 0.27, oy, oz), (0.015, 0.018, 0.21))))
    P.add("Optic", "J_Optic", "detail", "frame", merge(*bars))
    # arms
    for side in "LR":
        upper_arm(P, side, "round")
    # left forearm: thick, with the flame nozzle on the outer side (S_Flame_L)
    yc = SY
    P.add("Forearm_L", "J_Elbow_L", "base", "frame", cyl("y", (0, ZE), 0.28, yc - 0.32, yc + 0.32, 28))
    P.add("Forearm_L", "J_Elbow_L", "base", "pri", loft([(3.62, rect(-0.32, 0.34, yc - 0.34, yc + 0.34, 0.12)), (3.30, rect(-0.38, 0.40, yc - 0.40, yc + 0.40, 0.14)),
                                                         (2.86, rect(-0.36, 0.38, yc - 0.38, yc + 0.38, 0.14)), (2.74, rect(-0.30, 0.32, yc - 0.32, yc + 0.32, 0.10))]))
    P.add("Forearm_L", "J_Elbow_L", "plate", "frame", merge(G.revolve([(3.22, 0.13), (2.80, 0.13), (2.70, 0.16), (2.64, 0.15)], "z", (0.0, yc + 0.46), 20),
                                                           box((0.0, yc + 0.42, 3.00), (0.14, 0.05, 0.22))))
    P.add("Forearm_L", "J_Elbow_L", "plate", "pri", loft([(3.50, rect(0.38, 0.44, yc - 0.30, yc + 0.30, 0.02)), (2.95, rect(0.36, 0.42, yc - 0.28, yc + 0.28, 0.02))]))
    P.add("Forearm_L", "J_Elbow_L", "detail", "frame", merge(
        tube([(-0.30, yc + 0.36, 3.55), (-0.22, yc + 0.46, 3.30), (-0.10, yc + 0.50, 3.10), (0.0, yc + 0.50, 3.00)], 0.05, 10),
        G.bolts([(0.43, yc + y, z) for y in (-0.22, 0.22) for z in (3.05, 3.40)], (1, 0, 0)),
        G.slats(-0.39, yc - 0.28, yc + 0.28, 2.95, 3.45, 5, depth=0.03, axis="x")))
    hand_left(P, "round")
    # right forearm = thermite launcher (W_Cannon, S_Muzzle), thinner than the left
    yr = -SY
    P.add("Cannon", "W_Cannon", "base", "frame", cyl("y", (0, ZE), 0.27, yr - 0.30, yr + 0.30, 28))
    P.add("Cannon", "W_Cannon", "base", "pri", loft([(3.62, rect(-0.25, 0.27, yr - 0.27, yr + 0.27, 0.10)), (3.20, rect(-0.27, 0.29, yr - 0.28, yr + 0.28, 0.10)),
                                                     (2.82, rect(-0.24, 0.26, yr - 0.25, yr + 0.25, 0.08))]))
    P.add("Cannon", "W_Cannon", "plate", "frame", merge(G.revolve([(2.95, 0.17), (2.42, 0.17), (2.40, 0.21), (2.30, 0.21)], "z", (0.0, yr), 24),
                                                       cyl("y", (-0.04, 3.22), 0.22, yr - 0.40, yr - 0.27, 24)))
    P.add("Cannon", "W_Cannon", "detail", "frame", merge(G.bolts([(0.27, yr + y, z) for y in (-0.15, 0.15) for z in (3.0, 3.4)], (1, 0, 0)),
                                                        cyl_ab((0.10, yr - 0.28, 3.55), (0.10, yr - 0.28, 2.95), 0.04, 8),
                                                        cyl("y", (-0.04, 3.22), 0.10, yr - 0.43, yr - 0.40, 16)))
    leg_left(P, "round")
    return P


# ------------------------------------------------------------------ H-2 Legion
H2_DOOR = (4.15, 5.10, 0.49, 1.10)


def h2_box_sections(clip=None):
    T = [(4.00, -0.82, 0.86, 0.82, 0.12), (4.15, -1.10, 1.28, 1.15, 0.14), (5.05, -1.15, 1.32, 1.20, 0.14), (5.65, -1.05, 0.75, 1.05, 0.12)]
    return T


def h2_at(z):
    T = h2_box_sections()
    for (z0, *a), (z1, *b) in zip(T, T[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return [u + (v - u) * t for u, v in zip(a, b)]
    return list(T[-1][1:])


def rect_clip(x0, x1, hy, c, n_front=9, clip=None):
    """Rectangle with chamfered corners, the front edge sampled with n points (so a recess can be cut into it). CCW."""
    pts = []
    for y in np.linspace(-hy + c, hy - c, n_front):
        pts.append((clip(x1, y) if clip else x1, y))
    pts += [(x1 - c, hy), (x0 + c, hy), (x0, hy - c), (x0, -hy + c), (x0 + c, -hy), (x1 - c, -hy)]
    return pts


def h2_box():
    z0, z1, hw, rx = H2_DOOR
    zs = sorted(set([t[0] for t in h2_box_sections()] + [z0 - 0.01, z0 + 0.02, z1 - 0.02, z1 + 0.01]))
    secs = []
    for z in zs:
        xb, xf, hy, c = h2_at(z)
        clip = (lambda x, y: min(x, rx) if abs(y) < hw + 0.03 else x) if z0 + 0.01 < z < z1 - 0.01 else None
        secs.append((z, rect_clip(xb, xf, hy, c, 15, clip)))
    return loft(secs)


def h2_parts():
    P = Parts("H2")
    pelvis_waist(P, "box")
    P.add("Torso_Lower", "J_Torso", "base", "pri", loft([(3.55, rect(-0.30, 0.30, -0.30, 0.30, 0.06)), (3.56, rect(-0.40, 0.40, -0.40, 0.40, 0.08)),
                                                          (4.02, rect(-0.80, 0.80, -0.80, 0.80, 0.16)), (4.06, rect(-0.80, 0.80, -0.80, 0.80, 0.16))]))
    P.add("Torso_Lower", "J_Torso", "detail", "frame", merge(*[box((x, y, 3.82), (0.03, 0.03, 0.12)) for x in (-0.59, 0.59) for y in np.linspace(-0.45, 0.45, 5)]))
    P.add("Torso_Upper", "J_Torso", "base", "pri", h2_box())
    # round 2: horizontal seam, side armour slabs, glacis plate, recess wall
    xb, xf, hy, c = h2_at(4.50)
    P.add("Torso_Upper", "J_Torso", "plate", "frame", merge(
        loft([(4.47, rect_clip(xb - 0.02, xf + 0.02, hy + 0.02, c, 9, lambda x, y: min(x, 1.11) if abs(y) < 0.53 else x)),
              (4.53, rect_clip(xb - 0.02, xf + 0.02, hy + 0.02, c, 9, lambda x, y: min(x, 1.11) if abs(y) < 0.53 else x))]),
        box((1.105, 0, 4.62), (0.012, 0.47, 0.46))))
    for s in (1, -1):
        P.add("Torso_Upper", "J_Torso", "plate", "pri", loft([(4.18, rect(-0.95, 0.95, s * 1.20 - 0.04, s * 1.20 + 0.04, 0.02)), (4.95, rect(-0.95, 0.95, s * 1.20 - 0.04, s * 1.20 + 0.04, 0.02))]))
    # glacis plate along the sloped top front
    gl = loft_slope = G.loft([(5.10, rect(1.22, 1.30, -0.90, 0.90, 0.02)), (5.60, rect(0.78, 0.86, -0.80, 0.80, 0.02))])
    P.add("Torso_Upper", "J_Torso", "plate", "pri", gl)
    # back: exhaust grille on the left (S_Thrust / vents), drum bracket on the right
    P.add("Torso_Upper", "J_Torso", "plate", "frame", merge(box((-1.17, 0.55, 4.85), (0.04, 0.38, 0.48)), box((-1.20, -0.62, 4.80), (0.08, 0.40, 0.42))))
    P.add("Torso_Upper", "J_Torso", "detail", "frame", merge(G.slats(-1.22, 0.22, 0.88, 4.42, 5.28, 9, depth=0.04, axis="x"),
                                                            G.bolts([(-1.29, -0.62 + y, z) for y in (-0.30, 0.30) for z in (4.45, 5.15)], (-1, 0, 0)),
                                                            G.bolts([(x, s * 1.245, z) for x in (-0.8, -0.3, 0.3, 0.8) for z in (4.25, 4.88) for s in (1, -1)],
                                                                    lambda p: (0, 1 if p[1] > 0 else -1, 0)),
                                                            G.bolts([(1.21 - 0.88 * t, y, 5.13 + 0.45 * t + 0.02) for t in (0.15, 0.85) for y in (-0.7, -0.35, 0.35, 0.7)], (0.69, 0, 0.72))))
    # sensor: two square lenses side by side on the glacis (J_Optic)
    ox, oy, oz = RIG.H2["optic"]
    tilt = math.degrees(math.atan2(0.57, 0.60))     # glacis leans back 43.5 deg from vertical
    Rt = G.Ry(-tilt)    # turns +x (forward) up toward +z by 'tilt'
    vis = xform(box((0.05, 0, 0), (0.08, 0.44, 0.15)), Rt, (ox, oy, oz))
    P.add("Optic", "J_Optic", "base", "frame", vis)
    lens = merge(*[xform(box((0.135, y, 0), (0.012, 0.12, 0.085)), Rt, (ox, oy, oz)) for y in (-0.21, 0.21)])
    P.add("Optic", "J_Optic", "plate", "emit", lens)
    P.add("Optic", "J_Optic", "detail", "frame", merge(*[xform(box((0.14, y, 0), (0.02, 0.012, 0.10)), Rt, (ox, oy, oz)) for y in (-0.36, 0.0, 0.36)]))
    # hatch door (boxy)
    z0, z1, hw, rx = H2_DOOR
    def door_sect(z, inset=0.0):
        xb, xf, hy, c = h2_at(z)
        return [(rx - 0.02, hw - inset), (rx - 0.02, -hw + inset), (xf + 0.04, -hw + inset), (xf + 0.04, hw - inset)][::-1]
    P.add("Hatch", "J_Hatch", "base", "pri", loft([(z0 + 0.005, door_sect(z0, 0.03)), (z0 + 0.05, door_sect(z0 + 0.05)), (z1 - 0.05, door_sect(z1 - 0.05)), (z1 - 0.005, door_sect(z1, 0.03))]))
    P.add("Hatch", "J_Hatch", "plate", "frame", merge(box((1.37, 0.0, 4.62), (0.02, 0.40, 0.025)), box((1.37, -0.25, 4.62), (0.02, 0.025, 0.40)), box((1.37, 0.25, 4.62), (0.02, 0.025, 0.40))))
    P.add("Hatch", "J_Hatch", "detail", "frame", G.bolts([(1.375, y, z) for y in (-0.42, 0.42) for z in (4.25, 4.62, 5.00)], (1, 0, 0)))
    # shoulders: boxy domes (p 5); left carries the vertical shield slab (secondary), top 5.95 = torso top + 0.30
    dl = dome_left(p_out=5.0, rad=(0.68, 0.64, 0.64), c=(0.0, SY + 0.02, ZS + 0.40), r_in=(0.48, 0.58, 0.56), seg=48, rings=14)
    P.add("Shoulder_L", "J_Torso", "base", "pri" if os.environ.get("HSD_H2_LDOME") == "pri" else "sec", dl)   # R5 H-C3
    P.add("Shoulder_R", "J_Torso", "base", "pri", mirror(dl))
    shield = loft([(4.72, rect(-0.70, 0.70, SY + 0.66, SY + 0.98, 0.05)), (4.90, rect(-0.80, 0.80, SY + 0.54, SY + 1.00, 0.06)),
                   (5.80, rect(-0.80, 0.80, SY + 0.54, SY + 1.00, 0.06)), (5.95, rect(-0.66, 0.72, SY + 0.58, SY + 0.96, 0.05))])
    P.add("Shoulder_L", "J_Torso", "base", "sec", shield)
    P.add("Shoulder_L", "J_Torso", "plate", "frame", merge(box((0.0, SY + 1.005, 5.25), (0.70, 0.012, 0.04)), box((-0.81, SY + 0.77, 5.25), (0.012, 0.18, 0.60))))
    P.add("Shoulder_L", "J_Torso", "detail", "frame", G.bolts([(x, SY + 1.01, z) for x in (-0.6, -0.2, 0.2, 0.6) for z in (5.00, 5.70)], (0, 1, 0), r=0.04, h=0.03))
    for side, s in (("L", 1), ("R", -1)):
        cy = s * (SY + 0.02)
        P.add("Shoulder_" + side, "J_Torso", "plate", "frame", box((0.0, cy, ZS + 1.00), (0.50, 0.46, 0.04)))
        P.add("Shoulder_" + side, "J_Torso", "detail", "frame", G.bolts([(x, cy + y, ZS + 1.04) for x in (-0.4, 0.4) for y in (-0.36, 0.36)], (0, 0, 1)))
    P.add("Shoulder_R", "J_Torso", "plate", "sec", box((0.0, -(SY + 0.66), ZS + 0.35), (0.42, 0.015, 0.12)))   # yellow stripe, right side
    # ammo drum (J_Drum, spins about x): yellow cover, green status light; bracket on the torso
    dx, dy, dz = RIG.H2_EXTRA["J_Drum"][1]
    P.add("Drum", "J_Drum", "base", "frame", cyl("x", (dy, dz), 0.65, -1.74, -1.22, 48))
    P.add("Drum", "J_Drum", "plate", "sec", G.revolve([(-1.74, 0.60), (-1.78, 0.58), (-1.80, 0.20)], "x", (dy, dz), 48))
    P.add("Drum", "J_Drum", "plate", "emit", cyl("x", (dy, dz), 0.10, -1.83, -1.79, 20))
    P.add("Drum", "J_Drum", "detail", "frame", merge(*[xform(box((-1.48, 0, 0.62), (0.24, 0.03, 0.05)), G.Rx(math.degrees(t)), (0, dy, dz)) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)],
                                                    *[xform(box((-1.79, 0, 0.40), (0.015, 0.025, 0.17)), G.Rx(math.degrees(t)), (0, dy, dz)) for t in np.linspace(0, 2 * math.pi, 6, endpoint=False)]))
    # feed belt in three pieces, one per bone it rides on (torso -> under the right shoulder -> along the upper arm -> breech)
    belt_t = [(-1.42, -1.20, 5.02), (-1.20, -1.33, 4.80), (-0.90, -1.40, 4.55), (-0.60, -1.46, 4.40), (-0.42, -1.55, 4.36)]
    belt_a = [(-0.40, -1.60, 4.34), (-0.38, -1.66, 4.05), (-0.36, -1.70, 3.80)]
    belt_c = [(-0.36, -1.70, 3.76), (-0.48, -1.72, 3.50), (-0.46, -1.74, 3.25)]
    for name, joint, path in (("Belt_Torso", "J_Torso", belt_t), ("Belt_Arm", "J_Shoulder_R", belt_a), ("Belt_Cannon", "W_Cannon", belt_c)):
        P.add(name, joint, "plate", "frame", tube(path, 0.035, 8))
        P.add(name, joint, "detail", "sec", G.chain_links(path, 0.22, 0.07, 0.10, 0.07))
    # arms
    for side in "LR":
        upper_arm(P, side, "box")
    yc = SY
    P.add("Forearm_L", "J_Elbow_L", "base", "frame", cyl("y", (0, ZE), 0.27, yc - 0.30, yc + 0.30, 28))
    P.add("Forearm_L", "J_Elbow_L", "base", "pri", loft([(3.62, rect(-0.28, 0.30, yc - 0.29, yc + 0.29, 0.06)), (3.25, rect(-0.33, 0.35, yc - 0.33, yc + 0.33, 0.07)),
                                                         (2.76, rect(-0.29, 0.31, yc - 0.29, yc + 0.29, 0.06))]))
    P.add("Forearm_L", "J_Elbow_L", "plate", "pri", loft([(3.45, rect(0.34, 0.40, yc - 0.26, yc + 0.26, 0.02)), (2.90, rect(0.30, 0.36, yc - 0.24, yc + 0.24, 0.02))]))
    P.add("Forearm_L", "J_Elbow_L", "detail", "frame", merge(G.bolts([(0.39, yc + y, z) for y in (-0.2, 0.2) for z in (3.0, 3.35)], (1, 0, 0)),
                                                            cyl_ab((-0.34, yc - 0.15, 3.50), (-0.30, yc - 0.15, 2.85), 0.05, 10)))
    hand_left(P, "box")
    # cannon: breech = forearm (W_Cannon), six-barrel bundle on J_Barrel, 3.40 m elbow -> muzzle
    yr = -SY
    P.add("Cannon", "W_Cannon", "base", "frame", cyl("y", (0, ZE), 0.30, yr - 0.32, yr + 0.32, 28))
    P.add("Cannon", "W_Cannon", "base", "pri", loft([(3.60, rect(-0.40, 0.40, yr - 0.40, yr + 0.40, 0.07)), (3.30, rect(-0.44, 0.44, yr - 0.44, yr + 0.44, 0.08)),
                                                     (2.66, rect(-0.42, 0.42, yr - 0.42, yr + 0.42, 0.08)), (2.56, rect(-0.36, 0.36, yr - 0.36, yr + 0.36, 0.06))]))
    P.add("Cannon", "W_Cannon", "plate", "frame", merge(cyl("z", (0, yr), 0.40, 2.40, 2.58, 40), box((0, yr - 0.45, 3.05), (0.12, 0.03, 0.14))))
    P.add("Cannon", "W_Cannon", "plate", "emit", box((0.0, yr - 0.448, 3.38), (0.20, 0.008, 0.028)))
    P.add("Cannon", "W_Cannon", "plate", "emit", box((0.0, yr - 0.448, 3.30), (0.13, 0.008, 0.028)))
    P.add("Cannon", "W_Cannon", "detail", "frame", merge(G.bolts([(0.445, yr + y, z) for y in (-0.3, 0.0, 0.3) for z in (2.80, 3.40)], (1, 0, 0)),
                                                        G.slats(-0.445, yr - 0.30, yr + 0.30, 2.75, 3.45, 6, depth=0.03, axis="x")))
    bundle = [cyl("z", (0.0, yr), 0.09, 0.50, 2.45, 16)]
    for t in np.linspace(0, 2 * math.pi, 6, endpoint=False):
        bx, by = 0.27 * math.cos(t), yr + 0.27 * math.sin(t)
        bundle.append(G.revolve([(2.45, 0.10), (0.34, 0.10), (0.30, 0.115)], "z", (bx, by), 16))
    P.add("Barrels", "J_Barrel", "base", "frame", merge(*bundle))
    P.add("Barrels", "J_Barrel", "plate", "frame", merge(cyl("z", (0, yr), 0.40, 1.48, 1.62, 40), cyl("z", (0, yr), 0.40, 0.55, 0.68, 40)))
    P.add("Barrels", "J_Barrel", "detail", "frame", merge(*[cyl("z", (0.27 * math.cos(t), yr + 0.27 * math.sin(t)), 0.125, z, z + 0.05, 12)
                                                           for t in np.linspace(0, 2 * math.pi, 6, endpoint=False) for z in (1.1, 2.0)]))
    leg_left(P, "box")
    return P


# pairs that touch on purpose (joint hubs, plates sitting on a surface, the belt joints). Everything else is collision tested.
EXCLUDED_COMMON = [
    ("Pelvis", "Waist"), ("Waist", "Torso_Lower"), ("Waist", "Torso_Upper"), ("Hatch", "Torso_Upper"), ("Hatch", "Torso_Lower"), ("Optic", "Torso_Upper"),
    ("UpperArm_L", "Forearm_L"), ("Forearm_L", "Hand_L"), ("UpperArm_R", "Cannon"),
    ("Hand_L", "Finger_L_1"), ("Hand_L", "Finger_L_2"), ("Hand_L", "Finger_L_3"),
    ("Thigh_L", "Shin_L"), ("Thigh_R", "Shin_R"), ("Shin_L", "Foot_L"), ("Shin_R", "Foot_R"), ("Shin_L", "Toe_L"), ("Shin_R", "Toe_R"),
]
EXCLUDED_H2 = [("Cannon", "Barrels"), ("Drum", "Torso_Upper"), ("Belt_Torso", "Belt_Arm"), ("Belt_Arm", "Belt_Cannon"), ("Belt_Arm", "Cannon"),
               ("Belt_Cannon", "UpperArm_R"), ("Drum", "Belt_Torso")]


def remap(P):
    """Move authored (A rig) geometry to the active rig: each vertex z through the owner joint's map (identity for variant A)."""
    for name, p in P.parts.items():
        j = p["joint"]
        if RIG.group_of(j, name) == "fixed":
            continue
        p["shells"] = [(k, m, ([RIG.map_pt(j, v, name) for v in vs], fs)) for k, m, (vs, fs) in p["shells"]]
    return P


def build(which):
    return remap(h1_parts() if which == "H1" else h2_parts())
