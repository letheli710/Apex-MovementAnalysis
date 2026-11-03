"""Primitives added for v2 on top of prims.py (copied unchanged from the old model)."""
import math

from prims import Mesh


def rect16(x0, x1, y0, y1, c):
    """Chamfered rectangle as 16 points, starting at the middle of the +x edge, counter-clockwise."""
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    return [(x1, ym), (x1, y1 - c), (x1 - c / 2, y1 - c / 2), (x1 - c, y1),
            (xm, y1), (x0 + c, y1), (x0 + c / 2, y1 - c / 2), (x0, y1 - c),
            (x0, ym), (x0, y0 + c), (x0 + c / 2, y0 + c / 2), (x0 + c, y0),
            (xm, y0), (x1 - c, y0), (x1 - c / 2, y0 + c / 2), (x1, y0 + c)]


def circle16(cx, cy, r):
    return [(cx + r * math.cos(i * math.pi / 8), cy + r * math.sin(i * math.pi / 8)) for i in range(16)]


def loft(name, sections, mat="dark", joint=None):
    """Closed solid through horizontal sections [(z, [16 (x, y) points]), ...]."""
    vs, faces = [], []
    for z, pts in sections:
        vs += [(x, y, z) for x, y in pts]
    n = 16
    faces.append(tuple(range(n)))
    faces.append(tuple(range(n * (len(sections) - 1), n * len(sections))))
    for s in range(len(sections) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((s * n + i, s * n + j, (s + 1) * n + j, (s + 1) * n + i))
    return Mesh(name, vs, faces, mat, joint)


def ball(name, center, rx, ry=None, rz=None, mat="dark", seg=10, rings=6, joint=None):
    """Low-poly ellipsoid."""
    ry = rx if ry is None else ry
    rz = rx if rz is None else rz
    cx, cy, cz = center
    vs = [(cx, cy, cz + rz)]
    for k in range(1, rings):
        t = math.pi * k / rings
        for i in range(seg):
            a = 2 * math.pi * i / seg
            vs.append((cx + rx * math.sin(t) * math.cos(a), cy + ry * math.sin(t) * math.sin(a), cz + rz * math.cos(t)))
    vs.append((cx, cy, cz - rz))
    faces = []
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((0, 1 + i, 1 + j))
        faces.append((len(vs) - 1, 1 + (rings - 2) * seg + j, 1 + (rings - 2) * seg + i))
    for k in range(rings - 2):
        for i in range(seg):
            j = (i + 1) % seg
            faces.append((1 + k * seg + i, 1 + k * seg + j, 1 + (k + 1) * seg + j, 1 + (k + 1) * seg + i))
    return Mesh(name, vs, faces, mat, joint)


def merge(name, meshes, mat=None, joint=None):
    """One mesh object from several closed shells."""
    vs, faces = [], []
    for m in meshes:
        o = len(vs)
        vs += m.verts
        faces += [tuple(i + o for i in f) for f in m.faces]
    out = Mesh.__new__(Mesh)
    out.name, out.mat, out.joint = name, mat or meshes[0].mat, joint or meshes[0].joint
    out.verts, out.faces = vs, faces
    return out
