"""M-1 finished model: mid-poly (bevelled blocks, hatch panels) -> details -> 4 material slots -> sockets -> checks -> FBX + renders.

  blender.exe -b -P build_m1_final.py -- final

Shapes follow the round-2 silhouette (build_m1_silhouette.py, silhouette_r2/) with the changes listed in ../SPEC.md section 0.2.
Rig = v2 spec.json except the positions in MOVED. Coordinates here: ANALYSIS axes, world rest (x forward, y left, z up, m).
Outputs: Titan_M1.blend, Titan_M1.fbx, mid/ (grey, before details), final/ (colour), final/m1_final_checks.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_m1_silhouette as S  # helpers: loft, rect, poly8, cyl, ring_y, rot_y, merge, mirror, posing, collision, cameras

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

D, J, to_b = S.D, S.J, S.to_b
loft, rect, poly8, cyl, ring_y, rot_y, merge, mirror = S.loft, S.rect, S.poly8, S.cyl, S.ring_y, S.rot_y, S.merge, S.mirror
ROOT = "Titan_M1"
MID, FINAL = os.path.join(HERE, "mid"), os.path.join(HERE, "final")

SLOTS = ["MAT_Primary", "MAT_Secondary", "MAT_Frame", "MAT_Emissive"]
SLOT_IX = {"pri": 0, "sec": 1, "frame": 2, "emit": 3}
COLOR = {"pri": "#C9CDD2", "sec": "#3D4A5C", "frame": "#2A2D31", "emit": "#FF5A1F"}

# ------------------------------------------------------------------ rig changes from v2 (SPEC 0.1 #21, 0.2)
SLOPE = 0.70                        # chest front / hatch: leans back 0.70 m per metre of height (35 deg from vertical)
HINGE = (1.42, 0.0, 4.30)
EMIT_Z = 4.78
EMIT_X = HINGE[0] - (EMIT_Z - HINGE[2]) * SLOPE            # outer face of the hatch (the hinge line is on the outer face)
HT = 0.12                                                  # hatch panel thickness; the chest face sits HT behind the hatch
TILT = math.degrees(math.atan(SLOPE))
MOVED = {"J_Hatch": HINGE, "S_Seat": (0.55, 0.0, 4.28), "S_Chest": (round(EMIT_X, 3), 0.0, EMIT_Z)}
S.M1_MOVED.clear(); S.M1_MOVED.update(MOVED)   # the silhouette helpers read this
S.PILOT[:] = [((0.55, 0.0, 4.28), (0.20, 0.0, 4.70), 0.13, 0.20),   # trunk, 40 deg back
              ((0.06, 0.0, 4.86), (0.06, 0.0, 4.86), 0.12, 0.0),    # head
              ((0.55, 0.0, 4.28), (0.90, 0.0, 4.46), 0.09, 0.15),   # thighs
              ((0.90, 0.0, 4.46), (1.15, 0.0, 4.22), 0.07, 0.15)]   # shins


def pos_of(name):
    if name in MOVED:
        return MOVED[name]
    if name in J:
        return J[name]
    return D.ALL[name][1]


# ------------------------------------------------------------------ small parts for details
def box(x0, x1, y0, y1, z0, z1, c=0.02):
    return loft([(z0, rect(x0, x1, y0, y1, c)), (z1, rect(x0, x1, y0, y1, c))])


def bolts(points, axis, r=0.032, h=0.03, seg=12):
    """Short cylinders standing on a surface; axis 'x', 'y' or 'z' (+ or - prefix gives the outward direction)."""
    out = []
    sgn = -1 if axis.startswith("-") else 1
    ax = axis[-1]
    for p in points:
        for rr, a0, a1 in ((r * 1.35, 0.0, 0.3 * h), (r, 0.3 * h, h)):      # washer, head
            if ax == "x":
                out.append(cyl("x", (p[1], p[2]), rr, p[0] + sgn * a0, p[0] + sgn * a1, seg))
            elif ax == "y":
                out.append(cyl("y", (p[0], p[2]), rr, p[1] + sgn * a0, p[1] + sgn * a1, seg))
            else:
                out.append(cyl("z", (p[0], p[1]), rr, p[2] + sgn * a0, p[2] + sgn * a1, seg))
    return merge(*out)


def tube(a, b, r, seg=16):
    """Cylinder between two points (any direction)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    v, f = cyl("z", (0, 0), r, 0, L, seg)
    zax = d / L
    tmp = np.array([1.0, 0, 0]) if abs(zax[0]) < 0.9 else np.array([0, 1.0, 0])
    xax = np.cross(tmp, zax); xax /= np.linalg.norm(xax)
    yax = np.cross(zax, xax)
    M = np.stack([xax, yax, zax], 1)
    return [tuple(a + M @ np.array(p)) for p in v], f


def fins(x0, x1, y0, y1, z0, z1, n, along="y", t=0.025):
    """Grille: n thin plates spread along 'y' or 'z' inside the box."""
    out = []
    for i in range(n):
        u = (i + 0.5) / n
        if along == "y":
            yc = y0 + (y1 - y0) * u
            out.append(box(x0, x1, yc - t / 2, yc + t / 2, z0, z1, 0.004))
        else:
            zc = z0 + (z1 - z0) * u
            out.append(box(x0, x1, y0, y1, zc - t / 2, zc + t / 2, 0.004))
    return merge(*out)


# ------------------------------------------------------------------ the model. part -> joint, list of (mesh, slot, bevel, stage)
def model():
    P = {}

    def add(part, joint, mesh, slot, bevel=True, stage="mid"):
        P.setdefault(part, {"joint": joint, "pieces": []})["pieces"].append((mesh, slot, bevel, stage))

    def det(part, mesh, slot, bevel=False):
        add(part, P[part]["joint"], mesh, slot, bevel, "detail")

    # --- pelvis: core + collar (round 2), hip axles, front plate
    axle = cyl("y", (0, 2.85), 0.17, 0.40, 0.58, 24)
    add("Pelvis", "J_Pelvis", loft([(2.70, rect(-0.36, 0.28, -0.40, 0.40, 0.10)), (2.95, rect(-0.44, 0.36, -0.46, 0.46, 0.12)),
                                     (3.12, rect(-0.50, 0.34, -0.46, 0.46, 0.14)), (3.27, rect(-0.50, 0.24, -0.34, 0.34, 0.12)),
                                     (3.35, rect(-0.48, -0.04, -0.26, 0.26, 0.10))]), "pri")
    add("Pelvis", "J_Pelvis", merge(axle, mirror(axle)), "frame", False)
    add("Pelvis", "J_Pelvis", loft([(2.72, rect(0.30, 0.40, -0.26, 0.26, 0.04)), (3.05, rect(0.30, 0.44, -0.30, 0.30, 0.05))]), "pri")
    det("Pelvis", bolts([(-0.50, y, z) for y in (-0.30, -0.10, 0.10, 0.30) for z in (3.00, 3.20)], "-x"), "frame")
    det("Pelvis", bolts([(0.44, y, 2.92) for y in (-0.20, 0.0, 0.20)], "x", r=0.028), "frame")

    # --- waist drum (J_Waist does not turn) with ribs
    add("Waist", "J_Waist", cyl("z", (0, 0), 0.40, 3.20, 3.66, 32), "frame", False)
    det("Waist", merge(*[cyl("z", (0, 0), 0.42, z, z + 0.035, 32) for z in (3.38, 3.47, 3.56)]), "frame")

    # --- torso lower (radius <= 0.50 between the thighs)
    add("Torso_Lower", "J_Torso", loft([(3.61, rect(-0.36, 0.36, -0.36, 0.36, 0.12)), (3.76, rect(-0.48, 0.48, -0.48, 0.48, 0.16)),
                                         (4.12, rect(-0.50, 0.50, -0.50, 0.50, 0.16))]), "pri")
    det("Torso_Lower", fins(-0.505, -0.47, -0.30, 0.30, 3.80, 4.05, 6), "frame")
    det("Torso_Lower", bolts([(0.50, y, 4.04) for y in (-0.36, 0.36)] + [(0.50, y, 3.82) for y in (-0.36, 0.36)], "x"), "frame")

    # --- torso upper: wedge, chest prow at z 4.30-4.42 (x 1.42), front leans back 35 deg up to the top (x 0.55)
    xf = lambda z: HINGE[0] - HT - (z - HINGE[2]) * SLOPE     # chest face behind the hatch
    add("Torso_Upper", "J_Torso", loft([(4.12, poly8(1.22, -0.55, 0.60, 0.55, 0.16)), (4.30, poly8(xf(4.30), -0.80, 0.70, 0.85, 0.18)),
                                         (4.42, poly8(xf(4.42), -0.92, 0.74, 0.98, 0.18)), (5.40, poly8(xf(5.40), -0.98, 0.80, 1.00, 0.18)),
                                         (5.70, poly8(0.40, -0.82, 0.70, 0.82, 0.16))]), "pri")
    # chin plate under the prow (secondary): makes the forward thrust read from the side
    add("Torso_Upper", "J_Torso", loft([(4.10, poly8(1.30, 0.55, 0.52, 0.50, 0.10)), (4.24, poly8(1.40, 0.50, 0.62, 0.55, 0.12))]), "frame")
    # side cheek plates (armour panels over the torso sides)
    # behind the arm hub only (x <= -0.32): the hub's inner end swings inward when the arm goes out
    cheek = loft([(4.45, rect(-0.80, -0.32, 0.985, 1.015, 0.01)), (5.30, rect(-0.82, -0.32, 0.99, 1.02, 0.01))])
    add("Torso_Upper", "J_Torso", merge(cheek, mirror(cheek)), "pri")
    # sensor brow: fixed housing on the slope, the lens (J_Optic) sits in it
    add("Torso_Upper", "J_Torso", loft([(5.27, rect(0.45, 0.99, -0.42, 0.42, 0.05)), (5.53, rect(0.36, 0.93, -0.40, 0.40, 0.05))]), "sec")
    det("Torso_Upper", bolts([(0.60, y, 5.70) for y in (-0.55, -0.20, 0.20, 0.55)] + [(-0.60, y, 5.70) for y in (-0.55, 0.55)], "z"), "frame")
    det("Torso_Upper", fins(1.33, 1.37, -0.45, 0.45, 4.13, 4.21, 3, along="z", t=0.02), "frame")   # grille on the chin lip

    # --- backpack: breaks the flat back; thruster slot at the bottom, two vents on top (asymmetric), fuel line on the left
    add("Backpack", "J_Torso", loft([(4.48, rect(-1.38, -0.86, -0.70, 0.66, 0.14)), (4.80, rect(-1.42, -0.90, -0.72, 0.68, 0.16)),
                                      (5.40, rect(-1.10, -0.92, -0.56, 0.50, 0.10)), (5.52, rect(-1.02, -0.90, -0.50, 0.44, 0.06))]), "pri")
    add("Backpack", "J_Torso", loft([(4.46, rect(-1.42, -1.36, -0.62, -0.30, 0.02)), (5.12, rect(-1.33, -1.27, -0.60, -0.30, 0.02))]), "frame")  # vertical louvre on the right, runs down into the thruster slot
    det("Backpack", fins(-1.45, -1.37, -0.60, -0.32, 4.52, 4.80, 5, along="y", t=0.025), "frame")
    add("Backpack", "J_Torso", box(-1.40, -1.06, -0.50, 0.50, 4.34, 4.50, 0.04), "frame")                    # thruster housing (slot)
    det("Backpack", fins(-1.41, -1.35, -0.46, 0.46, 4.37, 4.47, 2, along="z", t=0.02), "frame")
    det("Backpack", fins(-1.02, -0.93, -0.42, -0.20, 5.52, 5.57, 5), "frame")                                  # vent R
    det("Backpack", fins(-1.00, -0.93, 0.14, 0.32, 5.52, 5.57, 4), "frame")                                    # vent L
    det("Backpack", merge(tube((-1.08, 0.66, 5.10), (-1.16, 0.80, 4.75), 0.05), tube((-1.16, 0.80, 4.75), (-1.00, 0.90, 4.50), 0.05),
                          tube((-1.12, 0.66, 5.00), (-1.20, 0.76, 4.70), 0.035)), "frame")                     # fuel lines, left only
    det("Backpack", bolts([(-1.42, y, z) for y in (0.32, 0.58) for z in (4.70, 4.95)] + [(-1.42, -0.66, 4.90)], "-x"), "frame")
    det("Backpack", bolts([(x, y, 5.53) for x in (-0.98,) for y in (-0.05, 0.05)], "z", r=0.025), "frame")

    # --- hatch: three panels on one joint (centre + two wings), hinge at the lower edge
    hx = lambda z: HINGE[0] - (z - HINGE[2]) * SLOPE
    def panel(y0, y1, z0, z1, t):
        return loft([(z0, rect(hx(z0) - t, hx(z0), y0, y1, 0.04)), (z1, rect(hx(z1) - t, hx(z1), y0, y1, 0.04))])
    add("Hatch_Center", "J_Hatch", panel(-0.36, 0.36, 4.30, 5.26, 0.12), "pri")
    add("Hatch_Wing_L", "J_Hatch", panel(0.375, 0.56, 4.36, 5.16, 0.10), "pri")
    add("Hatch_Wing_R", "J_Hatch", panel(-0.56, -0.375, 4.36, 5.16, 0.10), "pri")
    c = (EMIT_X, 0.0, EMIT_Z)
    add("Hatch_Center", "J_Hatch", rot_y(cyl("x", (0, EMIT_Z), 0.32, EMIT_X - 0.02, EMIT_X + 0.03, 32), TILT, c), "frame", False)
    add("Hatch_Center", "J_Hatch", rot_y(cyl("x", (0, EMIT_Z), 0.20, EMIT_X - 0.02, EMIT_X + 0.035, 32), TILT, c), "emit", False)
    ring_bolts = [(EMIT_X + 0.03, 0.27 * math.cos(a), EMIT_Z + 0.27 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
    det("Hatch_Center", rot_y(bolts(ring_bolts, "x", r=0.022, h=0.02), TILT, c), "frame")
    det("Hatch_Center", rot_y(fins(EMIT_X + 0.0, EMIT_X + 0.04, -0.30, 0.30, EMIT_Z - 0.30, EMIT_Z - 0.28, 1, along="z"), TILT, c), "frame")
    for s, part in ((1, "Hatch_Wing_L"), (-1, "Hatch_Wing_R")):
        det(part, rot_y(bolts([(hx(z), s * 0.47, z) for z in (4.45, 5.05)], "x", r=0.025), 0, (0, 0, 0)), "frame")

    # --- sensor lens 0.60 x 0.12 on J_Optic
    add("Optic", "J_Optic", box(0.93, 1.00, -0.30, 0.30, 5.34, 5.46, 0.02), "emit", False)

    # --- shoulder blocks (round 2), fixed to the torso; top panel strip and bolts
    blk = loft([(4.78, rect(-0.50, 0.48, 1.80, 1.92, 0.05)), (4.97, rect(-0.60, 0.56, 1.58, 1.95, 0.08)),
                (4.98, rect(-0.64, 0.60, 0.90, 1.95, 0.10)), (5.26, rect(-0.66, 0.62, 0.90, 1.95, 0.10)),
                (5.44, rect(-0.62, 0.56, 0.90, 1.72, 0.10))])
    skirt = box(-0.64, -0.42, 0.96, 1.66, 4.66, 4.99, 0.04)
    strip = box(-0.50, 0.46, 1.20, 1.52, 5.44, 5.47, 0.02)
    for s, part in ((1, "Shoulder_L"), (-1, "Shoulder_R")):
        f = (lambda m: m) if s == 1 else mirror
        add(part, "J_Torso", f(blk), "sec")
        add(part, "J_Torso", f(skirt), "sec")
        add(part, "J_Torso", f(strip), "pri")
        det(part, f(bolts([(x, 1.80, 5.40) for x in (-0.45, -0.15, 0.15, 0.45)], "z", r=0.03)), "frame")
        det(part, f(bolts([(0.62, y, 5.12) for y in (1.05, 1.40, 1.75)], "x", r=0.03)), "frame")
        det(part, f(fins(-0.66, -0.63, 1.05, 1.60, 4.72, 4.95, 6)), "frame")

    # --- arms. Hub on the swing axis (round 2), arm body, plate, piston
    hub = ring_y([(1.04, 0.24), (1.16, 0.34), (1.44, 0.34), (1.56, 0.24)], 0.0, 4.55, 24)
    arm = loft([(4.45, rect(-0.26, 0.26, 1.06, 1.54, 0.08)), (3.86, rect(-0.22, 0.22, 1.09, 1.51, 0.07))])
    for s, part, jn in ((1, "UpperArm_L", "J_Shoulder_L"), (-1, "UpperArm_R", "J_Shoulder_R")):
        f = (lambda m: m) if s == 1 else mirror
        add(part, jn, f(hub), "frame", False)
        add(part, jn, f(arm), "pri")
        add(part, jn, f(box(0.22, 0.30, 1.12, 1.48, 3.95, 4.38, 0.03)), "pri")
        det(part, f(merge(tube((-0.25, 1.30, 4.30), (-0.25, 1.30, 3.92), 0.06, 12), tube((-0.25, 1.30, 4.36), (-0.25, 1.30, 4.25), 0.08, 12))), "frame")
        det(part, f(ring_y([(1.565, 0.20), (1.60, 0.20)], 0.0, 4.55, 24)), "sec")

    # --- left arm: elbow hub, forearm (shield emitter pad on the outside), palm, three fingers
    add("Forearm_L", "J_Elbow_L", ring_y([(1.08, 0.18), (1.12, 0.22), (1.48, 0.22), (1.52, 0.18)], 0.0, 3.65, 20), "frame", False)
    add("Forearm_L", "J_Elbow_L", loft([(3.62, rect(-0.22, 0.22, 1.10, 1.50, 0.07)), (3.20, rect(-0.28, 0.28, 1.05, 1.55, 0.09)),
                                         (2.92, rect(-0.24, 0.24, 1.08, 1.52, 0.08))]), "pri")
    add("Forearm_L", "J_Elbow_L", box(-0.18, 0.18, 1.55, 1.60, 3.05, 3.45, 0.03), "sec")
    det("Forearm_L", bolts([(x, 1.60, z) for x in (-0.12, 0.12) for z in (3.10, 3.40)], "y", r=0.025), "frame")
    det("Forearm_L", tube((-0.24, 1.30, 3.55), (-0.26, 1.30, 3.00), 0.05), "frame")
    add("Hand_L", "J_Wrist_L", loft([(2.90, rect(-0.24, 0.24, 1.09, 1.51, 0.07)), (2.60, rect(-0.21, 0.21, 1.12, 1.48, 0.06))]), "pri")
    w = np.array(J["J_Wrist_L"], float)
    for i, (dx, dy, dz) in enumerate(((0.14, 0.12, -0.22), (0.14, -0.12, -0.22), (-0.14, 0.0, -0.22)), 1):
        r0 = w + (dx, dy, dz)
        sx = 1 if dx > 0 else -1
        fing = loft([(r0[2] + 0.04, rect(r0[0] - 0.08, r0[0] + 0.08, r0[1] - 0.07, r0[1] + 0.07, 0.03)),
                     (r0[2] - 0.22, rect(r0[0] - 0.07 + sx * 0.03, r0[0] + 0.07 + sx * 0.03, r0[1] - 0.06, r0[1] + 0.06, 0.03)),
                     (r0[2] - 0.40, rect(r0[0] - 0.03 + sx * 0.08, r0[0] + 0.03 + sx * 0.08, r0[1] - 0.04, r0[1] + 0.04, 0.015))])
        add("Finger_L_%d" % i, "J_Finger_L_%d" % i, fing, "frame")

    # --- right forearm cannon: elbow hub, body, barrel, muzzle ring, three energy slots on the outer side
    add("Cannon", "W_Cannon", ring_y([(-1.52, 0.18), (-1.48, 0.22), (-1.12, 0.22), (-1.08, 0.18)], 0.0, 3.65, 20), "frame", False)
    add("Cannon", "W_Cannon", loft([(3.62, rect(-0.26, 0.30, -1.57, -1.03, 0.08)), (2.62, rect(-0.30, 0.30, -1.60, -1.00, 0.09)),
                                     (2.46, rect(-0.20, 0.20, -1.50, -1.10, 0.06))]), "pri")
    add("Cannon", "W_Cannon", cyl("z", (0, -1.30), 0.15, 1.75, 2.48, 32), "frame", False)
    add("Cannon", "W_Cannon", cyl("z", (0, -1.30), 0.19, 1.65, 1.80, 32), "sec", False)
    det("Cannon", merge(*[box(-0.20, 0.20, -1.615, -1.595, z - 0.025, z + 0.025, 0.005) for z in (3.30, 3.10, 2.90)]), "emit")
    det("Cannon", merge(*[cyl("z", (0, -1.30), 0.165, z, z + 0.03, 32) for z in (2.05, 2.20, 2.35)]), "sec")
    det("Cannon", bolts([(0.30, y, z) for y in (-1.45, -1.15) for z in (3.45, 2.75)], "x", r=0.028), "frame")
    det("Cannon", fins(-0.31, -0.28, -1.50, -1.10, 2.70, 3.40, 7, along="z", t=0.03), "frame")

    # --- left shoulder pod: six tube mouths on the front face
    add("Pod_L", "J_Launcher_L", loft([(5.52, rect(-0.86, 0.04, 0.24, 0.96, 0.06)), (5.92, rect(-0.80, 0.04, 0.28, 0.96, 0.06))]), "sec")
    tubes = [(0.04, y, z) for z in (5.81, 5.65) for y in (0.42, 0.60, 0.78)]
    add("Pod_L", "J_Launcher_L", merge(*[cyl("x", (t[1], t[2]), 0.065, 0.02, 0.07, 16) for t in tubes]), "frame", False)
    det("Pod_L", bolts([(x, 0.96, 5.72) for x in (-0.70, -0.40, -0.10)], "y", r=0.025), "frame")

    # --- legs
    thigh = loft([(3.10, rect(-0.24, 0.24, 0.72, 1.12, 0.08)), (2.95, rect(-0.31, 0.31, 0.61, 1.16, 0.10)),
                  (2.70, rect(-0.32, 0.32, 0.61, 1.16, 0.10)), (1.75, rect(-0.25, 0.25, 0.64, 1.09, 0.08))])
    tplate = loft([(2.85, rect(0.30, 0.36, 0.68, 1.04, 0.03)), (1.95, rect(0.24, 0.30, 0.70, 1.02, 0.03))])
    shin = loft([(1.72, rect(-0.26, 0.36, 0.59, 1.13, 0.08)), (1.15, rect(-0.38, 0.42, 0.52, 1.20, 0.12)),
                 (0.86, rect(-0.30, 0.32, 0.58, 1.14, 0.10))])
    kneecap = loft([(1.30, rect(0.36, 0.46, 0.66, 1.06, 0.04)), (1.62, rect(0.30, 0.40, 0.68, 1.04, 0.04))])
    foot = loft([(0.00, rect(-0.57, 0.62, 0.40, 1.32, 0.08)), (0.38, rect(-0.50, 0.50, 0.44, 1.28, 0.08)),
                 (0.80, rect(-0.24, 0.26, 0.60, 1.12, 0.06))])
    toe = loft([(0.00, rect(0.63, 1.13, 0.42, 1.30, 0.06)), (0.30, rect(0.63, 0.95, 0.46, 1.26, 0.06))])
    for s, side in ((1, "L"), (-1, "R")):
        f = (lambda m: m) if s == 1 else mirror
        add("Thigh_" + side, "J_Hip_" + side, f(thigh), "pri")
        add("Thigh_" + side, "J_Hip_" + side, f(tplate), "frame")
        add("Thigh_" + side, "J_Hip_" + side, f(ring_y([(1.12, 0.22), (1.17, 0.22)], 0.0, 2.85, 20)), "frame", False)
        det("Thigh_" + side, f(merge(tube((-0.30, 0.86, 2.60), (-0.27, 0.86, 1.95), 0.06), tube((-0.31, 0.86, 2.65), (-0.30, 0.86, 2.40), 0.085))), "frame")
        det("Thigh_" + side, f(bolts([(0.36, y, 2.70) for y in (0.75, 0.97)] + [(0.31, y, 2.05) for y in (0.76, 0.96)], "x", r=0.025)), "frame")
        add("Shin_" + side, "J_Knee_" + side, f(shin), "pri")
        add("Shin_" + side, "J_Knee_" + side, f(kneecap), "pri")
        det("Shin_" + side, f(merge(tube((-0.36, 0.86, 1.50), (-0.33, 0.86, 0.95), 0.07), tube((-0.38, 0.86, 1.55), (-0.37, 0.86, 1.25), 0.095))), "frame")
        det("Shin_" + side, f(fins(-0.06, 0.06, 1.195, 1.22, 0.95, 1.40, 4, along="z", t=0.03)), "frame")
        det("Shin_" + side, f(bolts([(0.42, y, 1.15) for y in (0.70, 1.02)], "x", r=0.03)), "frame")
        add("Foot_" + side, "J_Ankle_" + side, f(foot), "pri")
        add("Foot_" + side, "J_Ankle_" + side, f(ring_y([(0.58, 0.16), (1.14, 0.16)], 0.0, 0.70, 20)), "frame", False)
        add("Foot_" + side, "J_Ankle_" + side, f(box(-0.62, -0.45, 0.55, 1.17, 0.0, 0.22, 0.04)), "frame")   # heel spur
        det("Foot_" + side, f(bolts([(x, 1.30, 0.20) for x in (-0.30, 0.0, 0.30)], "y", r=0.028)), "frame")
        add("Toe_" + side, "J_Ankle_" + side, f(toe), "frame")
        det("Toe_" + side, f(merge(*[box(0.70, 1.00, y - 0.012, y + 0.012, 0.0, 0.31, 0.004) for y in (0.72, 1.00)])), "frame")
    # --- extra bolt rows and cables (detail stage: joints and back)
    for s_, sd in ((1, "L"), (-1, "R")):
        f = (lambda m: m) if s_ == 1 else mirror
        det("Shoulder_" + sd, f(bolts([(x, 1.95, 5.15) for x in (-0.50, -0.20, 0.10, 0.40)], "y", r=0.03)), "frame")
        det("Shoulder_" + sd, f(bolts([(-0.66, y, 5.12) for y in (1.05, 1.40, 1.75)], "-x", r=0.03)), "frame")
        det("Thigh_" + sd, f(bolts([(x, 1.16, z) for x in (-0.18, 0.18) for z in (2.55, 2.15)], "y", r=0.028)), "frame")
        det("Shin_" + sd, f(bolts([(x, 1.20, z) for x in (-0.30, 0.30) for z in (1.28, 1.00)], "y", r=0.028)), "frame")
        det("Foot_" + sd, f(bolts([(x, y, 0.38) for x in (-0.35, 0.35) for y in (0.55, 1.17)], "z", r=0.03)), "frame")
        det("Torso_Lower", f(merge(tube((0.20, 0.42, 3.70), (0.30, 0.44, 4.10), 0.035), tube((-0.25, 0.43, 3.70), (-0.15, 0.45, 4.10), 0.035))), "frame")
    det("Cannon", bolts([(x, y, 3.62) for x in (-0.15, 0.15) for y in (-1.45, -1.30, -1.15)], "z", r=0.025), "frame")
    det("Backpack", bolts([(-1.40, y, z) for y in (-0.15, 0.10, 0.35) for z in (4.62,)] + [(-1.33, -0.15, 5.05)], "-x", r=0.025), "frame")
    det("Torso_Lower", bolts([(-0.50, y, z) for y in (-0.30, 0.0, 0.30) for z in (3.80, 4.06)], "-x", r=0.025), "frame")
    det("Torso_Upper", bolts([(-0.98, y, z) for y in (-0.85, 0.85) for z in (4.55, 4.95, 5.30)], "-x", r=0.03), "frame")
    det("Forearm_L", bolts([(0.28, y, z) for y in (1.15, 1.45) for z in (3.15, 2.98)], "x", r=0.025), "frame")
    for sd, part in ((1, "Hatch_Wing_L"), (-1, "Hatch_Wing_R")):
        hxx = lambda z: HINGE[0] - (z - HINGE[2]) * SLOPE
        det(part, bolts([(hxx(z), sd * 0.47, z) for z in (4.65, 4.85)], "x", r=0.025), "frame")
    return P


# sockets: v2 names first (D.SOCKETS), M-1 positions where the shell moved them, then the M-1 additions (SPEC 3.3)
def socket_table():
    T = {n: (par, list(p)) for n, (par, p) in D.SOCKETS.items()}
    T["S_Seat"] = ("J_Torso", list(MOVED["S_Seat"]))
    T["S_Chest"] = ("J_Torso", list(MOVED["S_Chest"]))
    T["S_Thrust"] = ("J_Torso", [-1.41, 0.0, 4.42])
    T["S_Vent_L"] = ("J_Torso", [-0.965, 0.23, 5.57])
    T["S_Vent_R"] = ("J_Torso", [-0.975, -0.31, 5.57])
    T["S_Dmg_Torso_F"] = ("J_Torso", [1.20, 0.60, 4.80])
    T["S_Dmg_Torso_B"] = ("J_Torso", [-1.42, -0.20, 4.90])
    T["S_Dmg_Shoulder_L"] = ("J_Shoulder_L", [0.0, 1.60, 4.55])
    T["S_Dmg_Shoulder_R"] = ("J_Shoulder_R", [0.0, -1.60, 4.55])
    for i, t in enumerate([(0.07, y, z) for z in (5.81, 5.65) for y in (0.42, 0.60, 0.78)], 1):
        T["S_Rocket_%d" % i] = ("J_Launcher_L", list(t))
    T["S_Optic"] = ("J_Optic", [1.00, 0.0, 5.40])
    T["S_Embark"] = ("J_Torso", [1.85, 0.0, 4.00])
    T["S_Shield_L"] = ("J_Elbow_L", [0.0, 1.60, 3.25])
    T["S_Mine_L"] = ("J_Launcher_L", [-0.70, 0.60, 5.92])
    T["S_Rodeo"] = ("J_Torso", [-0.60, 0.0, 5.72])   # placeholder only: rodeo / battery are not done (SPEC 3.3)
    return T


EXCLUDED = {frozenset(p) for p in [
    ("Pelvis", "Waist"), ("Waist", "Torso_Lower"), ("Optic", "Torso_Upper"),
    ("Pod_L", "Torso_Upper"), ("Pod_L", "Shoulder_L"), ("UpperArm_L", "Forearm_L"), ("Forearm_L", "Hand_L"), ("UpperArm_R", "Cannon"),
    ("Thigh_L", "Shin_L"), ("Thigh_R", "Shin_R"), ("Shin_L", "Foot_L"), ("Shin_R", "Foot_R"), ("Shin_L", "Toe_L"), ("Shin_R", "Toe_R"),
    ("Hand_L", "Finger_L_1"), ("Hand_L", "Finger_L_2"), ("Hand_L", "Finger_L_3"),
    ("Shoulder_L", "UpperArm_L"), ("Shoulder_R", "UpperArm_R"),
] + [(h, t) for h in ("Hatch_Center", "Hatch_Wing_L", "Hatch_Wing_R") for t in ("Torso_Upper", "Torso_Lower")]}
S.EXCLUDED = EXCLUDED


# ------------------------------------------------------------------ build
def hex_rgba(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v]
    return (*lin, 1.0)


def make_materials():
    mats = []
    for name, key in zip(SLOTS, ("pri", "sec", "frame", "emit")):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        rgba = hex_rgba(COLOR[key])
        m.diffuse_color = rgba
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = rgba
        b.inputs["Roughness"].default_value = 0.55 if key != "frame" else 0.45
        b.inputs["Metallic"].default_value = 0.2 if key != "frame" else 0.6
        if key == "emit":
            b.inputs["Emission Color"].default_value = rgba
            b.inputs["Emission Strength"].default_value = 2.0   # idle state (SPEC 3.4); Unity drives 2 / 6 / red
        m["grey"] = {"pri": 0.78, "sec": 0.48, "frame": 0.22, "emit": 0.97}[key]
        mats.append(m)
    return mats


def piece_mesh(vs, fs, jp, bevel):
    """Temporary object -> bevel modifier (2-4 cm) -> evaluated mesh (joint-local, Blender axes)."""
    md = bpy.data.meshes.new("tmp")
    md.from_pydata([to_b(np.array(v) - jp) for v in vs], [], [list(f) for f in fs])
    md.validate(); md.update()
    bm = bmesh.new(); bm.from_mesh(md)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(md); bm.free()
    if not bevel:
        return md
    ob = bpy.data.objects.new("tmp", md)
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new("bev", "BEVEL")
    mod.width, mod.segments, mod.limit_method, mod.angle_limit = 0.03, 4, "ANGLE", math.radians(30)
    mod.use_clamp_overlap = True
    dg = bpy.context.evaluated_depsgraph_get()
    out = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(md)
    return out


def build(stage):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S._cam = None
    col = bpy.context.scene.collection
    mats = make_materials()
    objs = {ROOT: bpy.data.objects.new(ROOT, None)}
    col.objects.link(objs[ROOT])
    names = list(D.JOINTS) + list(socket_table())
    table = dict(D.JOINTS); table.update(socket_table())
    for n in names:
        e = bpy.data.objects.new(n, None)
        e.rotation_mode = "QUATERNION"
        e.empty_display_type = "ARROWS" if n[0] in "JW" else "SPHERE"
        e.empty_display_size = 0.15 if n[0] in "JW" else 0.08
        col.objects.link(e)
        objs[n] = e
    for n in names:
        par, _ = table[n]
        root = par not in D.JOINTS
        objs[n].parent = objs[ROOT] if root else objs[par]
        ppos = (0, 0, 0) if root else pos_of(par)
        objs[n].location = to_b(np.array(pos_of(n) if n not in socket_table() else table[n][1], float) - np.array(ppos, float))
    objs["S_Rodeo"]["not_used"] = "rodeo / battery not in scope (SPEC 3.3)"
    meshes = {}
    global MODEL
    MODEL = model()
    for part, spec in MODEL.items():
        jp = np.array(pos_of(spec["joint"]), float)
        bm = bmesh.new()
        for (vs, fs), slot, bev, st in spec["pieces"]:
            if stage == "mid" and st == "detail":
                continue
            md = piece_mesh(vs, fs, jp, bev)
            n0 = len(bm.faces)
            bm.from_mesh(md)
            bm.faces.ensure_lookup_table()
            for i in range(n0, len(bm.faces)):
                bm.faces[i].material_index = SLOT_IX[slot]
            bpy.data.meshes.remove(md)
        md = bpy.data.meshes.new("M1_" + part)
        bm.to_mesh(md); bm.free()
        for m in mats:
            md.materials.append(m)
        for p in md.polygons:
            p.use_smooth = True
        md.set_sharp_from_angle(angle=math.radians(35))
        ob = bpy.data.objects.new("M1_" + part, md)
        col.objects.link(ob)
        ob.parent = objs[spec["joint"]]
        ob["owner_joint"] = spec["joint"]
        meshes[part] = ob
    bpy.context.view_layer.update()
    return objs, meshes


# ------------------------------------------------------------------ checks
def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def slot_areas(meshes):
    a = [0.0] * 4
    for ob in meshes.values():
        for p in ob.data.polygons:
            a[p.material_index] += p.area
    t = sum(a)
    return {SLOTS[i]: round(100 * a[i] / t, 1) for i in range(4)}


def run_checks(objs, meshes):
    R = {}
    S.set_pose(objs, {})
    tris = {n: tri_count(o) for n, o in meshes.items()}
    R["tris_total"] = sum(tris.values())
    R["tris_ok_40k_60k"] = 40000 <= R["tris_total"] <= 60000
    R["tris_max_part"] = max(tris.items(), key=lambda kv: kv[1])
    R["tris_part_ok_6000"] = R["tris_max_part"][1] <= 6000
    R["tris_per_part"] = tris
    R["material_slots"] = sorted({m.name for o in meshes.values() for m in o.data.materials})
    R["material_slots_ok"] = R["material_slots"] == sorted(SLOTS)
    R["slot_area_pct"] = slot_areas(meshes)
    R["emissive_le_3pct"] = R["slot_area_pct"]["MAT_Emissive"] <= 3.0
    # origins on joints: each mesh object sits exactly on its parent joint (identity local transform)
    R["origins_on_joints"] = all((o.matrix_world.translation - o.parent.matrix_world.translation).length < 1e-6 for o in meshes.values())
    v = np.vstack([S.world_verts(o) for o in meshes.values()])
    H = float(v[:, 2].max())
    R["rest_top_m"] = round(H, 3)
    R["top_le_5.97"] = H <= 5.97
    R["torso_front_x_m"] = round(float(-np.vstack([S.world_verts(meshes[n]) for n in ("Torso_Upper", "Hatch_Center")])[:, 1].min()), 3)
    R["torso_back_x_m"] = round(float(-np.vstack([S.world_verts(meshes[n]) for n in ("Torso_Upper", "Backpack")])[:, 1].max()), 3)
    sh = np.vstack([S.world_verts(meshes[n]) for n in ("Shoulder_L", "Shoulder_R")])
    hip = np.vstack([S.world_verts(meshes[n]) for n in ("Thigh_L", "Thigh_R", "Pelvis")])
    hip = hip[(hip[:, 2] > 2.60) & (hip[:, 2] < 3.15)]
    sw, hw = float(np.ptp(sh[:, 0])), float(np.ptp(hip[:, 0]))
    R["shoulder_hip"] = dict(ok=sw >= 1.5 * hw, shoulder=round(sw, 3), hip=round(hw, 3), ratio=round(sw / hw, 3))
    pel_top = float(S.world_verts(meshes["Pelvis"])[:, 2].max())
    tor_bot = float(S.world_verts(meshes["Torso_Lower"])[:, 2].min())
    R["waist"] = dict(ok=(tor_bot - pel_top) <= 0.06 * H, visible=round(tor_bot - pel_top, 3), limit=round(0.06 * H, 3))
    f = np.vstack([S.world_verts(meshes[n]) for n in ("Foot_L", "Toe_L")])
    fl = float(np.ptp(f[:, 1]))
    R["foot"] = dict(ok=fl >= 0.22 * H, length=round(fl, 3), need=round(0.22 * H, 3))
    def girth(n):
        q = S.world_verts(meshes[n]); return float(np.ptp(q[:, 0]) * np.ptp(q[:, 1]))
    R["calf_thigh"] = dict(ok=girth("Shin_L") >= girth("Thigh_L"), shin=round(girth("Shin_L"), 3), thigh=round(girth("Thigh_L"), 3))
    bend = {}
    for k, p in (("bend_45", {"w_bend": 45}), ("bend_-25", {"w_bend": -25}), ("side_30", {"w_side": 30}), ("side_-30", {"w_side": -30}),
                 ("yaw_90_bend_45", {"w_yaw": 90, "w_bend": 45})):
        S.set_pose(objs, p)
        bend[k] = not S.pair_overlap(meshes, "Torso_Lower", "Pelvis")
    R["waist_bend"] = dict(ok=all(bend.values()), cases=bend)
    feet = {"M1_Foot_L", "M1_Foot_R", "M1_Toe_L", "M1_Toe_R", "M1_Shin_L", "M1_Shin_R"}
    poses, tops, solved, sh_arm = {}, {}, {}, {}
    for name, hand in D.SPEC["hand_poses"].items():
        p, off = S.solve_pose(objs, hand, feet)
        solved[name] = (p, off)
        poses[name] = S.collide(meshes)
        tops[name] = round(float(np.vstack([S.world_verts(o) for o in meshes.values()])[:, 2].max()), 3)
        sh_arm[name] = [s for s in "LR" if S.pair_overlap(meshes, "Shoulder_" + s, "UpperArm_" + s)]
    R["poses_clean"] = sum(1 for x in poses.values() if not x)
    R["pose_collisions"] = {k: x for k, x in poses.items() if x}
    R["shoulder_vs_arm"] = {k: x for k, x in sh_arm.items() if x}
    R["pose_top_m"] = tops
    S.set_pose(objs, {})
    R["pilot_fit"] = pilot_fit(objs, meshes)
    # kneel, hatch open 120: hinge height, opened panels must not hit the torso
    p, off = solved["kneel_hatch"]
    S.set_pose(objs, dict(p, hatch=120), off)
    open_hits = [h + " x " + t for h in ("Hatch_Center", "Hatch_Wing_L", "Hatch_Wing_R") for t in ("Torso_Upper", "Torso_Lower", "Shoulder_L", "Shoulder_R")
                 if S.pair_overlap(meshes, h, t)]
    R["kneel_hatch"] = dict(hinge_height=round(float(objs["J_Hatch"].matrix_world.translation.z), 3), opening_w=1.12,
                            opening_len=round((5.26 - 4.30) * math.hypot(1, SLOPE), 3), open_hatch_hits=open_hits,
                            ok=not open_hits and 1.12 >= 0.60 and (5.26 - 4.30) * math.hypot(1, SLOPE) >= 0.94)
    S.set_pose(objs, {})
    # sockets present
    want = set(D.SOCKETS) | {"S_Optic", "S_Embark", "S_Shield_L", "S_Mine_L", "S_Rodeo"}
    have = {o.name for o in bpy.data.objects if o.type == "EMPTY"}
    R["sockets_missing"] = sorted(want - have)
    R["joints_missing"] = sorted(set(D.JOINTS) - have)
    R["joint_positions_v2_unchanged"] = all((objs[n].matrix_world.translation - S.Vector(to_b(J[n]))).length < 1e-5
                                            for n in J if n in objs and n.startswith(("J_", "W_")) and n not in MOVED)
    return R, solved


def pilot_fit(objs, meshes):
    """At rest (world = rest), each shell piece of the torso and hatch tested on its own."""
    shell = ["Torso_Upper", "Torso_Lower", "Hatch_Center", "Hatch_Wing_L", "Hatch_Wing_R", "Backpack"]
    trees = []
    for n in shell:
        for (vs, fs), slot, bev, st in MODEL[n]["pieces"]:
            trees.append(BVHTree.FromPolygons([Vector(to_b(v)) for v in vs], [list(f) for f in fs]))
    pts = S.pilot_points({"J_Torso": objs["J_Torso"]})
    out = [q for q in pts if not any(S._inside(t, q) for t in trees)]
    return dict(ok=not out, points=len(pts), outside=len(out))


# ------------------------------------------------------------------ renders
def colour_setup(res=(1400, 1400)):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.62, 0.64, 0.67, 1)
    bg.inputs["Strength"].default_value = 0.9
    if "Sun" not in bpy.data.objects:
        for nm, rot, en in (("Sun", (math.radians(50), 0, math.radians(-35)), 3.5), ("Fill", (math.radians(70), 0, math.radians(150)), 1.2)):
            l = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN"))
            l.data.energy = en
            l.rotation_euler = rot
            sc.collection.objects.link(l)
    return sc


def ground():
    if "H_ground" in bpy.data.objects:
        return
    md = bpy.data.meshes.new("H_ground")
    md.from_pydata([(-12, -12, 0), (12, -12, 0), (12, 12, 0), (-12, 12, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("H_ground", md)
    m = bpy.data.materials.new("H_ground"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.36, 0.37, 1)
    m.diffuse_color = (0.35, 0.36, 0.37, 1)
    md.materials.append(m)
    bpy.context.scene.collection.objects.link(ob)


def human(xy):
    ob = S.helper("human", xy)
    m = ob.data.materials[0]
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.35, 0.08, 1)
    return ob


def render_colour(objs, solved, outdir):
    os.makedirs(outdir, exist_ok=True)
    p, off = solved["stand_aim"]
    S.set_pose(objs, p, off)
    colour_setup()
    ground()
    for name, (loc, hxy) in S.ORTHO.items():
        h = human(hxy)
        S.camera(loc, (0, 0, S.ZC), ortho=S.SCALE)
        S.render(os.path.join(outdir, "colour_%s.png" % name))
        bpy.data.objects.remove(h, do_unlink=True)
    h = human(S.Q34[2])
    S.camera(S.Q34[0], S.Q34[1], lens=62)
    S.render(os.path.join(outdir, "colour_3q.png"))
    S.camera((-9.0, 12.5, 5.6), (0.0, 0.2, 3.4), lens=62)
    S.render(os.path.join(outdir, "colour_3q_back.png"))
    bpy.data.objects.remove(h, do_unlink=True)
    p, off = solved["kneel_hatch"]
    S.set_pose(objs, dict(p, hatch=120), off)
    h = human((2.6, -2.6))
    S.camera((9.5, -12.0, 4.4), (0, -0.6, 2.4), lens=55)
    S.render(os.path.join(outdir, "colour_kneel_hatch.png"))
    bpy.data.objects.remove(h, do_unlink=True)
    S.set_pose(objs, {})


def render_grey(objs, solved, outdir, prefix):
    """Workbench grey (same look as the silhouette rounds) and black silhouettes, stand_aim."""
    os.makedirs(outdir, exist_ok=True)
    S.OUT = outdir
    p, off = solved["stand_aim"]
    S.set_pose(objs, p, off)
    S.render_views("", ("sil", "grey"), True)
    for m in bpy.data.materials:            # set_colors('sil') blackened them
        if m.name in SLOTS:
            m.diffuse_color = hex_rgba(COLOR[["pri", "sec", "frame", "emit"][SLOTS.index(m.name)]])
    S.set_pose(objs, {})


# ------------------------------------------------------------------ export
def export(objs):
    S.set_pose(objs, {})
    for ob in [o for o in bpy.data.objects if o.type not in ("EMPTY", "MESH") or o.name.startswith("H_") or o.name == "Cam"]:
        bpy.data.objects.remove(ob, do_unlink=True)
    blend = os.path.join(HERE, "Titan_M1.blend")
    fbx = os.path.join(HERE, "Titan_M1.fbx")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    # same settings as v2 (bake_space_transform=False keeps empties + parented meshes right on re-import)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, object_types={"EMPTY", "MESH"}, axis_forward="-Z", axis_up="Y",
                             apply_scale_options="FBX_SCALE_ALL", bake_space_transform=False, bake_anim=False, global_scale=1.0,
                             add_leaf_bones=False, mesh_smooth_type="FACE")
    want = {n: to_b(pos_of(n)) for n in list(D.JOINTS) if n.startswith(("J_", "W_"))}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S._cam = None
    bpy.ops.import_scene.fbx(filepath=fbx, axis_forward="-Z", axis_up="Y")
    bpy.context.view_layer.update()
    worst, missing = 0.0, []
    for n, v in want.items():
        ob = bpy.data.objects.get(n)
        if ob is None:
            missing.append(n); continue
        worst = max(worst, (ob.matrix_world.translation - Vector(v)).length)
    ms = [o for o in bpy.data.objects if o.type == "MESH"]
    zs = [(o.matrix_world @ v.co).z for o in ms for v in o.data.vertices]
    return dict(ok=not missing and worst <= 0.01, worst_joint_err_m=round(worst, 5), missing=missing, meshes=len(ms),
                mesh_z=[round(min(zs), 3), round(max(zs), 3)], note="Blender re-import only; Unity import not run")


def main():
    # mid-poly: bevelled blocks + hatch panels, grey renders
    objs, meshes = build("mid")
    Rm, solved = run_checks(objs, meshes)
    render_grey(objs, solved, MID, "")
    json.dump(Rm, open(os.path.join(MID, "m1_mid_checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    # final: + details, colour renders, export
    objs, meshes = build("final")
    R, solved = run_checks(objs, meshes)
    os.makedirs(FINAL, exist_ok=True)
    render_grey(objs, solved, FINAL, "")
    render_colour(objs, solved, FINAL)
    R["fbx_roundtrip"] = export(objs)
    json.dump(R, open(os.path.join(FINAL, "m1_final_checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("=== MID tris", Rm["tris_total"], "FINAL tris", R["tris_total"], "max part", R["tris_max_part"], "clean poses", R["poses_clean"])


if __name__ == "__main__" or True:
    if "final" in sys.argv:
        main()
