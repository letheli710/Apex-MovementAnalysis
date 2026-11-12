"""Shared light-chassis parts (L-1 and L-2 differ in armour, weapons and the torso lean). No bpy.

A part = dict(name, joint, slot, mesh, stage, hub). World rest coordinates, analysis axes.
stage: 1 = silhouette volume, 2 = secondary armour plate (mid model), 3 = detail (bolts, pistons, grilles, pipes).
slot: pri / sec / frame / emit  ->  MAT_Primary / MAT_Secondary / MAT_Frame / MAT_Emissive.
hub: a joint hub that sits inside its parent part on purpose; pairs with a hub on adjacent joints are not collision-tested.
"""
import math

import numpy as np

import geo
import light_rig as R

SH_Y, SH_Z, ELB_Z, WR_Z = R.SH_Y, R.SH_Z, R.ELB_Z, R.WR_Z
HIP_Y, HIP_Z, KNEE_Z, ANKLE_Z = R.HIP_Y, R.HIP_Z, R.KNEE_Z, R.ANKLE_Z


class Parts(list):
    def add(self, name, joint, slot, mesh, stage=1, hub=False, panel=False):
        self.append(dict(name=name, joint=joint, slot=slot, mesh=mesh, stage=stage, hub=hub, panel=panel))

    def pair(self, name, joint_L, slot, mesh_L, stage=1, hub=False, panel=False):
        """Left part given; right part mirrored."""
        self.add(name + "_L", joint_L, slot, mesh_L, stage, hub, panel)
        self.add(name + "_R", joint_L[:-1] + "R" if joint_L.endswith("_L") else joint_L, slot, geo.mirror(mesh_L), stage, hub, panel)


def leaned(mesh, deg):
    return geo.xform(mesh, geo.Ry(deg), about=R.LEAN_PIVOT)


# ------------------------------------------------------------------ torso shell (bullet)
# upright sections (z, nose x, back x, half width, cut x). Hatch = the nose in front of the cut, between HATCH_Z0 and HATCH_Z1.
TORSO_SECTIONS = [
    (3.98, 0.34, -0.36, 0.38, 0.33),
    (4.12, 0.62, -0.50, 0.52, 0.61),
    (4.40, 1.05, -0.70, 0.66, 0.66),
    (4.80, 1.28, -0.80, 0.74, 0.55),
    (5.10, 1.10, -0.82, 0.74, 0.42),
    (5.40, 0.74, -0.80, 0.68, 0.30),
    (5.62, 0.30, -0.76, 0.62, 0.29),
    (5.74, 0.00, -0.64, 0.52, -0.01),
]
HATCH_IDX = (2, 5)             # sections that carry the nose (hatch, the sloped canopy) part
SEAT_UP = (0.10, 0.0, 4.55)    # upright torso coordinates; leaned with the shell
HINGE_UP = (1.05, 0.0, 4.40)   # hatch hinge: lower front edge of the nose
PILOT_UP = [((0.10, 0.0, 4.55), (-0.25, 0.0, 4.97), 0.13, 0.20),   # trunk, 40 deg back
            ((-0.39, 0.0, 5.13), (-0.39, 0.0, 5.13), 0.12, 0.0),   # head
            ((0.10, 0.0, 4.55), (0.50, 0.0, 4.77), 0.09, 0.15),    # thighs
            ((0.50, 0.0, 4.77), (0.77, 0.0, 4.57), 0.07, 0.15)]    # shins


def torso_outline(z):
    """Interpolated upright section at height z: (xf, xb, w, xcut)."""
    S = TORSO_SECTIONS
    for a, b in zip(S, S[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + t * (b[i] - a[i]) for i in range(1, 5))
    return S[0][1:] if z < S[0][0] else S[-1][1:]


def torso_y(z, x, sharp=0.42):
    """Half width of the upright torso section at height z and depth x (0 outside)."""
    xf, xb, w, _ = torso_outline(z)
    xm, ax = (xf + xb) / 2, (xf - xb) / 2
    c = (x - xm) / ax
    if abs(c) > 1:
        return 0.0
    return w * math.sqrt(1 - c * c) * (1 - sharp * ((1 + c) / 2) ** 2)


def torso_shell(P, code, lean, body_slot="pri", hatch_slot="sec", scale_w=1.0):
    body, nose = [], []
    for i, (z, xf, xb, w, xc) in enumerate(TORSO_SECTIONS):
        has_nose = HATCH_IDX[0] <= i <= HATCH_IDX[1]
        b, n = geo.split_teardrop(xf, xb, w * scale_w, xc if has_nose else xf - 0.015, 30, 12)
        body.append((z, b))
        if has_nose:
            nose.append((z, n))   # shares the cut face with the body (seated door; the pair is excluded and the door swing is checked)
    P.add("Torso_Upper", "J_Torso", body_slot, leaned(geo.loft(body), lean), 1, panel=True)
    P.add("Hatch", "J_Hatch", hatch_slot, leaned(geo.loft(nose), lean), 1, panel=True)
    # lower torso: narrow (radius <= 0.46) so the thighs pass at waist yaw 85; coned at the bottom for the 45 deg bend
    low = geo.loft([(3.90, geo.ellipse(0.0, 0.0, 0.26, 0.26, 16)), (4.00, geo.ellipse(0.0, 0.0, 0.33, 0.33, 16)),
                    (4.10, geo.ellipse(0.0, 0.0, 0.34, 0.34, 16))])
    P.add("Torso_Lower", "J_Torso", "frame", leaned(low, lean), 1)


def pilot_capsules(lean):
    return [(R.lean(a, lean), R.lean(b, lean), r, hw) for a, b, r, hw in PILOT_UP]


# ------------------------------------------------------------------ pelvis + waist
def pelvis(P, collar_slot="pri", waist_slot="sec"):
    core = geo.loft([(3.18, geo.rect(-0.32, 0.26, -0.36, 0.36, 0.10)), (3.40, geo.rect(-0.40, 0.32, -0.46, 0.46, 0.12)),
                     (3.56, geo.rect(-0.38, 0.24, -0.40, 0.40, 0.12))])
    axle = geo.tube((0.0, 0.30, HIP_Z), (0.0, 0.66, HIP_Z), 0.15, 12)
    P.add("Pelvis", "J_Pelvis", "frame", geo.merge(core, axle, geo.mirror(axle)), 1, hub=True)
    # collar: back and sides up to 3.74, front open and low (forward bend 45, back bend 25, side bend 30 clear)
    side = geo.extrude([(-0.50, 3.38), (0.30, 3.38), (0.30, 3.46), (-0.16, 3.57), (-0.50, 3.64)], "xz", 0.41, 0.52)
    back = geo.loft([(3.38, geo.rect(-0.54, -0.40, -0.50, 0.50, 0.04)), (3.74, geo.rect(-0.54, -0.42, -0.48, 0.48, 0.04))])
    P.add("Collar", "J_Pelvis", collar_slot, geo.merge(side, geo.mirror(side), back), 1, panel=True)
    P.add("Waist", "J_Waist", waist_slot, geo.lathe((0, 0, 3.58), (0, 0, 4.02), [(0, 0.34), (0.2, 0.44), (0.8, 0.44), (1, 0.36)], 20), 1, hub=True)


# ------------------------------------------------------------------ legs
def thigh(P, style):
    hub = geo.lathe((0.0, 0.60, HIP_Z), (0.0, 1.00, HIP_Z), [(0, 0.18), (0.15, 0.25), (0.85, 0.25), (1, 0.18)], 16)
    P.pair("Thigh_Hub", "J_Hip_L", "frame", hub, 1, hub=True)
    core = geo.loft([(3.08, geo.rect(-0.20, 0.18, 0.62, 0.96, 0.08)), (2.40, geo.rect(-0.19, 0.17, 0.63, 0.95, 0.08)),
                     (1.95, geo.rect(-0.15, 0.13, 0.66, 0.92, 0.06))])
    P.pair("Thigh", "J_Hip_L", "pri", core, 1)
    if style == "L1":
        plate = geo.loft([(3.12, geo.rect(0.04, 0.28, 0.60, 1.00, 0.08)), (2.45, geo.rect(0.10, 0.34, 0.61, 1.01, 0.10)),
                          (1.88, geo.rect(0.02, 0.22, 0.66, 0.94, 0.06))])
        side = geo.loft([(3.00, geo.rect(-0.16, 0.20, 0.96, 1.03, 0.02)), (2.05, geo.rect(-0.10, 0.14, 0.95, 1.01, 0.02))])
    else:   # L2: sharper, faceted front guard and a taller side plate
        plate = geo.loft([(3.10, geo.rect(0.02, 0.30, 0.60, 1.00, 0.14)), (2.60, geo.rect(0.12, 0.38, 0.60, 1.02, 0.16)),
                          (1.90, geo.rect(0.00, 0.20, 0.68, 0.92, 0.08))])
        side = geo.loft([(3.05, geo.rect(-0.20, 0.22, 0.96, 1.04, 0.02)), (2.00, geo.rect(-0.12, 0.14, 0.95, 1.01, 0.02))])
    P.pair("Thigh_Plate", "J_Hip_L", "pri", plate, 1, panel=True)
    P.pair("Thigh_Side", "J_Hip_L", "pri", side, 2)
    # r5b (lead 11-12): the thigh ended at 1.95 and the knee hub at 1.79, so thigh and knee never touched (gap 0.08-0.11 in every
    # pose, _diag/diag_knee.py). Clevis: two round lobes centred on the knee axis (r 0.24) either side of the hub, with straps up
    # into the thigh. A disc on the axis looks the same at every knee angle, so the joint stays closed without sweeping the shin.
    lobe = lambda y0, y1: geo.tube((0.0, y0, KNEE_Z), (0.0, y1, KNEE_Z), 0.24, 20)
    strap = lambda y0, y1: geo.loft([(2.08, geo.rect(-0.15, 0.13, y0, y1, 0.03)), (KNEE_Z, geo.rect(-0.17, 0.15, y0, y1, 0.03))])
    # straps stay outside the shin width (y 0.64-0.94) below z 1.97 and bridge into the thigh core only above it (the shin core
    # reaches up there at knee 115+ when the straps were full width: crouch, kneel, landing hits in the first try)
    bridge = lambda y0, y1: geo.loft([(2.10, geo.rect(-0.15, 0.13, y0, y1, 0.03)), (1.97, geo.rect(-0.15, 0.13, y0, y1, 0.03))])
    # outer lobe only 3 cm thick (to y 1.005) and r 0.23: at 1.035 / 0.24 it touched the right-hand weapon in crouch (weapon inner
    # edge y 1.05)
    lobe_o = lambda y0, y1: geo.tube((0.0, y0, KNEE_Z), (0.0, y1, KNEE_Z), 0.23, 20)
    P.pair("Thigh_Clevis", "J_Hip_L", "pri", geo.merge(lobe(0.565, 0.625), strap(0.565, 0.625), bridge(0.565, 0.70),
                                                       lobe_o(0.975, 1.005), strap(0.975, 1.005), bridge(0.90, 1.005)), 1)
    # exposed hydraulic on the back of the thigh (joints exposed, armour on the front only)
    P.pair("Thigh_Piston", "J_Hip_L", "frame", geo.merge(geo.piston((-0.24, 0.70, 3.02), (-0.20, 0.70, 1.98), 0.055, 0.032),
                                                          geo.piston((-0.24, 0.84, 3.02), (-0.20, 0.84, 1.98), 0.055, 0.032)), 3)


def shin_foot(P, style):
    hub = geo.lathe((0.0, 0.62, KNEE_Z), (0.0, 0.98, KNEE_Z), [(0, 0.16), (0.15, 0.20), (0.85, 0.20), (1, 0.16)], 16)
    P.pair("Knee_Hub", "J_Knee_L", "frame", hub, 1, hub=True)
    core = geo.loft([(1.42, geo.rect(-0.20, 0.16, 0.64, 0.94, 0.08)), (0.62, geo.rect(-0.16, 0.14, 0.66, 0.92, 0.06)),
                     (0.56, geo.rect(-0.13, 0.11, 0.68, 0.90, 0.04))])   # r5b: down to 0.56, into the ankle drum
    P.pair("Shin", "J_Knee_L", "pri", core, 1)
    # r5b: top of the shin plate and the knee guard narrowed to y 0.64-0.96 so they turn between the thigh clevis lobes
    plate = geo.loft([(1.42, geo.rect(0.08, 0.30, 0.64, 0.96, 0.08)), (1.18, geo.rect(0.11, 0.34, 0.58, 1.00, 0.10)), (0.95, geo.rect(0.14, 0.38, 0.55, 1.03, 0.12)),
                      (0.60, geo.rect(0.04, 0.26, 0.62, 0.96, 0.08))])
    P.pair("Shin_Plate", "J_Knee_L", "pri", plate, 1, panel=True)
    guard = geo.loft([(1.86, geo.rect(0.10, 0.26, 0.66, 0.92, 0.06)), (1.62, geo.rect(0.16, 0.36, 0.645, 0.955, 0.08)),
                      (1.42, geo.rect(0.12, 0.32, 0.645, 0.955, 0.08))])
    P.pair("Knee_Guard", "J_Knee_L", "sec" if style == "L2" else "pri", guard, 2, panel=True)
    # long heel bone (calf blade): the reverse-joint read. Rides the shin, ends at 0.80 so the heel spur clears it at ankle 60 deg.
    # on the OUTER side of the leg (y 1.04-1.16, thigh ends at 1.03): at knee 115-140 it sweeps past the thigh instead of into it
    blade = geo.extrude([(-0.10, 1.50), (-0.40, 1.44), (-0.64, 0.98), (-0.68, 0.82), (-0.52, 0.80), (-0.12, 1.10)], "xz", 1.04, 1.15)
    P.pair("Calf_Blade", "J_Knee_L", "pri", blade, 1, panel=True)
    # mount from the shin core out to the blade, low enough (0.4+ below the knee) to pass behind the thigh at full knee flex
    mount = geo.merge(geo.box((-0.30, 1.00, 1.06), (0.14, 0.06, 0.10), 0.03), geo.box((-0.12, 0.98, 0.86), (0.07, 0.05, 0.14), 0.02))
    P.pair("Calf_Mount", "J_Knee_L", "frame", mount, 1)
    P.pair("Ankle_Piston", "J_Knee_L", "frame", geo.merge(geo.piston((-0.12, 0.64, 1.20), (-0.10, 0.64, 0.66), 0.05, 0.03),
                                                           geo.piston((-0.16, 0.99, 1.16), (-0.46, 0.99, 0.92), 0.045, 0.028)), 3)
    # foot: ankle drum, forefoot (front pad), two toes, heel spur. Sole at z 0, ankle 0.38 above it.
    # r5b: ankle drum radius 0.17 -> 0.23 (top 0.61) so it meets the shin bottom; gap was up to 0.056
    P.pair("Ankle", "J_Ankle_L", "frame", geo.lathe((0.0, 0.64, ANKLE_Z), (0.0, 0.94, ANKLE_Z), [(0, 0.18), (0.2, 0.23), (0.8, 0.23), (1, 0.18)], 16), 1, hub=True)
    foot = geo.loft([(0.00, geo.rect(-0.22, 0.62, 0.48, 1.10, 0.10)), (0.18, geo.rect(-0.20, 0.56, 0.50, 1.08, 0.10)),
                     (0.30, geo.rect(-0.12, 0.30, 0.60, 0.98, 0.08))])
    P.pair("Foot", "J_Ankle_L", "pri", foot, 1, panel=True)
    toe_a = geo.loft([(0.00, geo.rect(0.56, 0.96, 0.50, 0.77, 0.06)), (0.10, geo.rect(0.56, 0.94, 0.51, 0.76, 0.06)),
                      (0.20, geo.rect(0.56, 0.72, 0.53, 0.74, 0.04))])
    toe_b = geo.loft([(0.00, geo.rect(0.56, 0.92, 0.81, 1.08, 0.06)), (0.10, geo.rect(0.56, 0.90, 0.82, 1.07, 0.06)),
                      (0.20, geo.rect(0.56, 0.70, 0.84, 1.05, 0.04))])
    P.pair("Toe", "J_Ankle_L", "sec" if style == "L1" else "pri", geo.merge(toe_a, toe_b), 1)
    spur = geo.extrude([(-0.10, 0.02), (-0.48, 0.10), (-0.50, 0.18), (-0.12, 0.34)], "xz", 0.70, 0.88)
    P.pair("Heel_Spur", "J_Ankle_L", "pri", spur, 1)


# ------------------------------------------------------------------ arms
def upper_arm(P, side, plate=True, hub_r=0.27):
    sg = 1 if side == "L" else -1
    y0, y1 = sg * (SH_Y - 0.23), sg * (SH_Y + 0.23)
    hub = geo.lathe((0.0, y0, SH_Z), (0.0, y1, SH_Z), [(0, 0.20), (0.18, hub_r), (0.82, hub_r), (1, 0.20)], 18)
    P.add("UpperArm_Hub_" + side, "J_Shoulder_" + side, "frame", hub, 1, hub=True)
    # r5b: socket drum from inside the torso side out to the hub's inner end (y SH_Y - 0.23), on J_Torso. Front view showed a dark
    # hole between torso and arm hub under the mantle (gap 0.10-0.23).
    P.add("Shoulder_Socket_" + side, "J_Torso", "frame",
          geo.lathe((0.0, sg * 0.62, SH_Z), (0.0, sg * (SH_Y - 0.225), SH_Z), [(0, 0.22), (0.7, 0.21), (1, 0.18)], 18), 1)
    yc = sg * SH_Y
    strut = geo.loft([(4.40, geo.rect(-0.18, 0.18, yc - 0.16, yc + 0.16, 0.07)), (3.72, geo.rect(-0.15, 0.15, yc - 0.13, yc + 0.13, 0.06))])
    P.add("UpperArm_" + side, "J_Shoulder_" + side, "frame", strut, 1)
    if plate:
        pl = geo.loft([(4.30, geo.rect(0.06, 0.26, yc - 0.19, yc + 0.20, 0.07)), (3.80, geo.rect(0.05, 0.22, yc - 0.17, yc + 0.18, 0.06))])
        P.add("UpperArm_Plate_" + side, "J_Shoulder_" + side, "pri", pl, 2, panel=True)
        op = geo.loft([(4.28, geo.rect(-0.17, 0.21, yc + sg * 0.16 - 0.04, yc + sg * 0.16 + 0.04, 0.02)),
                       (3.82, geo.rect(-0.14, 0.18, yc + sg * 0.16 - 0.035, yc + sg * 0.16 + 0.035, 0.02))])
        P.add("UpperArm_Side_" + side, "J_Shoulder_" + side, "pri", op, 2)
    P.add("UpperArm_Piston_" + side, "J_Shoulder_" + side, "frame",
          geo.merge(geo.piston((-0.21, yc - sg * 0.07, 4.32), (-0.19, yc - sg * 0.07, 3.74), 0.045, 0.028),
                    geo.piston((-0.21, yc + sg * 0.07, 4.32), (-0.19, yc + sg * 0.07, 3.74), 0.045, 0.028)), 3)


def forearm(P, side, armour_slot="pri"):
    sg = 1 if side == "L" else -1
    yc = sg * SH_Y
    # r5b: hub radius 0.17 -> 0.195 so it reaches the upper-arm strut end (3.72); gap was up to 0.032 (_diag/diag_joints.py). 0.21 hit the rifle stock
    hub = geo.lathe((0.0, yc - 0.17, ELB_Z), (0.0, yc + 0.17, ELB_Z), [(0, 0.15), (0.2, 0.195), (0.8, 0.195), (1, 0.15)], 16)
    P.add("Elbow_Hub_" + side, "J_Elbow_" + side, "frame", hub, 1, hub=True)
    # r5b: core runs down to 2.54 (was 2.62) into the new wrist hub; the palm started 0.18 below the forearm before
    core = geo.loft([(3.42, geo.rect(-0.16, 0.16, yc - 0.15, yc + 0.15, 0.07)), (2.62, geo.rect(-0.14, 0.14, yc - 0.13, yc + 0.13, 0.06)),
                     (2.54, geo.rect(-0.11, 0.11, yc - 0.11, yc + 0.11, 0.04))])
    P.add("Forearm_" + side, "J_Elbow_" + side, "pri", core, 1)
    lo, hi = (yc - 0.10, yc + 0.22) if side == "L" else (yc - 0.22, yc + 0.10)
    arm = geo.loft([(3.40, geo.rect(-0.06, 0.22, lo, hi, 0.08)), (3.00, geo.rect(-0.04, 0.24, lo - 0.01 * sg, hi + 0.01 * sg, 0.09)),
                    (2.66, geo.rect(-0.04, 0.20, lo, hi, 0.07))])
    P.add("Forearm_Plate_" + side, "J_Elbow_" + side, armour_slot, arm, 1, panel=True)


def hand(P, side, finger_len=0.40):
    sg = 1 if side == "L" else -1
    yc = sg * SH_Y
    palm = geo.loft([(2.44, geo.rect(-0.16, 0.16, yc - 0.15, yc + 0.15, 0.06)), (2.30, geo.rect(-0.17, 0.17, yc - 0.16, yc + 0.16, 0.06)),
                     (2.12, geo.rect(-0.14, 0.15, yc - 0.14, yc + 0.14, 0.05))])
    P.add("Hand_" + side, "J_Wrist_" + side, "frame", palm, 1, hub=True)
    # r5b: wrist drum on the pitch axis (y), joins forearm end (2.54) and palm top (2.44) at every wrist angle
    P.add("Wrist_Hub_" + side, "J_Wrist_" + side, "frame",
          geo.lathe((0.0, yc - 0.13, WR_Z), (0.0, yc + 0.13, WR_Z), [(0, 0.11), (0.2, 0.14), (0.8, 0.14), (1, 0.11)], 16), 1, hub=True)
    for i, (dx, dy) in enumerate(((0.14, 0.12), (0.14, -0.12), (-0.14, 0.0)), 1):
        rx, ry, rz = dx, yc + sg * dy, WR_Z - 0.22
        seg1 = geo.loft([(rz + 0.02, geo.rect(rx - 0.055, rx + 0.055, ry - 0.055, ry + 0.055, 0.02)),
                         (rz - finger_len * 0.55, geo.rect(rx - 0.05, rx + 0.05, ry - 0.05, ry + 0.05, 0.02))])
        seg2 = geo.loft([(rz - finger_len * 0.55, geo.rect(rx - 0.048, rx + 0.048, ry - 0.048, ry + 0.048, 0.02)),
                         (rz - finger_len, geo.rect(rx - 0.035, rx + 0.035, ry - 0.04, ry + 0.04, 0.015))])
        knuckle = geo.tube((rx, ry - 0.06, rz), (rx, ry + 0.06, rz), 0.05, 10)
        P.add("Finger_%s_%d" % (side, i), "J_Finger_%s_%d" % (side, i), "frame", geo.merge(seg1, seg2, knuckle), 1, hub=True)


# ------------------------------------------------------------------ sockets shared by both
def base_sockets(lean, torso_back_x=-0.80):
    """name: (parent, rest position). Names per SPEC 3.3 table."""
    S = {}
    S["S_Eye"] = ("J_Torso", (0.62, 0.0, 4.70))
    S["S_Seat"] = ("J_Torso", R.lean(SEAT_UP, lean))
    S["S_Chest"] = ("J_Torso", R.lean((0.80, 0.0, 4.95), lean))
    S["S_Embark"] = ("J_Torso", (2.20, 0.0, 0.0))
    S["S_Rodeo"] = ("J_Torso", R.lean((-0.55, 0.0, 5.62), lean))
    S["S_Dmg_Torso_F"] = ("J_Torso", R.lean((0.86, 0.34, 4.95), lean))
    S["S_Dmg_Torso_B"] = ("J_Torso", R.lean((-0.82, 0.0, 4.95), lean))
    for s, sg in (("L", 1), ("R", -1)):
        S["S_Hand_" + s] = ("J_Wrist_" + s, (0.0, sg * SH_Y, WR_Z - 0.30))
        S["S_Dmg_Shoulder_" + s] = ("J_Shoulder_" + s, (0.0, sg * (SH_Y + 0.25), SH_Z))
        S["S_Dmg_Elbow_" + s] = ("J_Elbow_" + s, (0.0, sg * SH_Y, ELB_Z))
        S["S_Dmg_Thigh_" + s] = ("J_Hip_" + s, (0.30, sg * HIP_Y, 2.45))
        S["S_Dmg_Knee_" + s] = ("J_Knee_" + s, (0.30, sg * HIP_Y, KNEE_Z))
        S["S_Foot_" + s] = ("J_Ankle_" + s, (0.24, sg * HIP_Y, 0.0))
    return S


def hatch_opening(scale_w=1.0):
    """Cockpit opening = the cut face behind the nose. Width per nose section, height along the cut (upright, before lean)."""
    rows = []
    for i in range(HATCH_IDX[0], HATCH_IDX[1] + 1):
        z, xf, xb, w, xc = TORSO_SECTIONS[i]
        rows.append((z, xc, 2 * torso_y(z, xc) * scale_w))
    (z0, x0, _), (z1, x1, _) = rows[0], rows[-1]
    inner = [r[2] for r in rows[1:-1]]
    return dict(width_m=round(min(inner), 3), widths_m=[round(r[2], 3) for r in rows], height_m=round(math.hypot(z1 - z0, x1 - x0), 3),
                how="cut face behind the nose: width = min of the inner sections, height = length along the cut from bottom to top section")


def shoulder_check(span, plate_names, hub_y, hub_r, side_sign=1, hub_half=0.23):
    """Plate over the arm hub. span(names, X, Y) -> (top z, bottom z) of the plate column at Blender X (= analysis y), Y (= -analysis x),
    or None. Thickness straight above the hub axis; cover = every column over the hub footprint exists and starts above the hub top."""
    yc = side_sign * hub_y
    c = span(plate_names, yc, 0.0)
    hub_top = SH_Z + hub_r
    if c is None:
        return dict(ok=False, note="no plate over the hub axis")
    cols = [span(plate_names, yc + dy, dx) for dy in np.linspace(-hub_half, hub_half, 5) for dx in np.linspace(-hub_r, hub_r, 5)]
    covers = all(k is not None and k[1] >= hub_top - 1e-3 for k in cols)
    return dict(thickness_m=round(c[0] - c[1], 3), underside_m=round(c[1], 3), top_m=round(c[0], 3), hub_top_m=round(hub_top, 3),
                covers_hub=covers, ok=(c[0] - c[1]) >= 0.45 and covers)
