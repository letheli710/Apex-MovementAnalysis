"""Pure-python graybox primitives (no bpy). All coordinates are WORLD metres in the
neutral pose, Blender axes: +Z up, front of the titan = -Y, the titan's LEFT side = +X.
Every primitive is a CONVEX closed solid with outward-wound faces."""
import math


class Mesh:
    def __init__(self, name, verts, faces, mat, joint=None):
        self.name, self.mat, self.joint = name, mat, joint
        self.verts = [tuple(float(c) for c in v) for v in verts]
        self.faces = [tuple(f) for f in faces]
        self._orient()

    def _orient(self):
        n = len(self.verts)
        c = [sum(v[i] for v in self.verts) / n for i in range(3)]
        out = []
        for f in self.faces:
            pts = [self.verts[i] for i in f]
            nx = ny = nz = 0.0
            for i in range(len(pts)):  # Newell normal
                a, b = pts[i], pts[(i + 1) % len(pts)]
                nx += (a[1] - b[1]) * (a[2] + b[2])
                ny += (a[2] - b[2]) * (a[0] + b[0])
                nz += (a[0] - b[0]) * (a[1] + b[1])
            fc = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
            d = nx * (fc[0] - c[0]) + ny * (fc[1] - c[1]) + nz * (fc[2] - c[2])
            out.append(tuple(reversed(f)) if d < 0 else f)
        self.faces = out

    def tris(self):
        return sum(len(f) - 2 for f in self.faces)

    def bounds(self):
        xs, ys, zs = zip(*self.verts)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def mirrored_x(self, joint=None):
        return Mesh(self.name, [(-x, y, z) for x, y, z in self.verts], self.faces, self.mat, joint or self.joint)


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    l = math.sqrt(_dot(a, a))
    return (a[0] / l, a[1] / l, a[2] / l)


def _frame(axis, side_hint):
    a = _norm(axis)
    u = _sub(side_hint, _mul(a, _dot(side_hint, a)))
    if _dot(u, u) < 1e-9:
        u = _sub((0, 1, 0), _mul(a, a[1]))
    u = _norm(u)
    return a, u, _cross(a, u)


def limb(name, p0, p1, size0, size1=None, mat="dark", side_hint=(1, 0, 0), joint=None):
    """Rectangular tapered bar from p0 to p1. size=(w,d): w along side_hint (default X), d perpendicular
    to both the bar axis and w. size0 != size1 tapers it."""
    size1 = size1 or size0
    a, u, v = _frame(_sub(p1, p0), side_hint)
    vs = []
    for p, (w, d) in ((p0, size0), (p1, size1)):
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(_add(p, _add(_mul(u, su * w / 2), _mul(v, sv * d / 2))))
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return Mesh(name, vs, faces, mat, joint)


def box(name, center, size, mat="dark", joint=None):
    """Axis-aligned box. size=(sx,sy,sz)."""
    cx, cy, cz = center
    sx, sy, sz = size
    vs = [(cx + i * sx / 2, cy + j * sy / 2, cz + k * sz / 2) for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)]
    return Mesh(name, vs, faces, mat, joint)


def cyl(name, p0, p1, r0, r1=None, mat="dark", seg=12, joint=None):
    """Cylinder / cone frustum from p0 (radius r0) to p1 (radius r1). Joint hubs: a cylinder along X."""
    r1 = r0 if r1 is None else r1
    ax = _norm(_sub(p1, p0))
    a, u, v = _frame(ax, (1, 0, 0) if abs(ax[0]) < .9 else (0, 1, 0))
    vs = []
    for p, r in ((p0, r0), (p1, r1)):
        for i in range(seg):
            t = 2 * math.pi * i / seg
            vs.append(_add(p, _add(_mul(u, r * math.cos(t)), _mul(v, r * math.sin(t)))))
    faces = [tuple(range(seg)), tuple(range(seg, 2 * seg))]
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((i, j, seg + j, seg + i))
    return Mesh(name, vs, faces, mat, joint)


def ext_poly(name, poly, plane, lo, hi, mat="dark", joint=None):
    """Extrude a CONVEX 2D polygon. plane 'xz' -> poly=(x,z), extruded along y from lo to hi;
    'yz' -> poly=(y,z), extruded along x; 'xy' -> poly=(x,y), extruded along z.
    Use for chamfered plates, wedges, side profiles."""
    n = len(poly)

    def pt(p, t):
        if plane == "xz": return (p[0], t, p[1])
        if plane == "yz": return (t, p[0], p[1])
        return (p[0], p[1], t)

    vs = [pt(p, lo) for p in poly] + [pt(p, hi) for p in poly]
    faces = [tuple(range(n)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return Mesh(name, vs, faces, mat, joint)


def chamfer_box(name, center, size, c, mat="dark", joint=None, plane="xz"):
    """Box with the 4 edges parallel to the thickness axis chamfered by c (octagonal section).
    plane 'xz': octagon in X/Z, thickness along Y (front plates); 'yz': thickness along X; 'xy': along Z."""
    cx, cy, cz = center
    sx, sy, sz = size
    if plane == "xz": w, h, lo, hi, o = sx, sz, cy - sy / 2, cy + sy / 2, (cx, cz)
    elif plane == "yz": w, h, lo, hi, o = sy, sz, cx - sx / 2, cx + sx / 2, (cy, cz)
    else: w, h, lo, hi, o = sx, sy, cz - sz / 2, cz + sz / 2, (cx, cy)
    a, b = w / 2, h / 2
    poly = [(o[0] - a + c, o[1] - b), (o[0] + a - c, o[1] - b), (o[0] + a, o[1] - b + c), (o[0] + a, o[1] + b - c),
            (o[0] + a - c, o[1] + b), (o[0] - a + c, o[1] + b), (o[0] - a, o[1] + b - c), (o[0] - a, o[1] - b + c)]
    return ext_poly(name, poly, plane, lo, hi, mat, joint)
