"""Pure-Python geometry helpers for the heavy titans (no bpy). Analysis axes: x forward, y left, z up, metres.
A mesh is (verts, faces). Helpers copied from ../M1/build_m1_silhouette.py where they exist, plus a few new ones.
"""
import math

import numpy as np


# ------------------------------------------------------------------ sections
def rect(x0, x1, y0, y1, c=0.06):
    return [(x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c), (x0 + c, y0), (x1 - c, y0)]


def se_sect(af, ab, b, p=2.4, n=40, cx=0.0, cy=0.0, clip=None):
    """Superellipse top-view section: front half-depth af, back half-depth ab, half-width b. CCW from the front.
    clip(x, y) -> x lets a caller flatten part of the outline (hatch recess)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = (af if c >= 0 else ab) * math.copysign(abs(c) ** (2.0 / p), c)
        y = b * math.copysign(abs(s) ** (2.0 / p), s)
        if clip:
            x = clip(x, y)
        pts.append((cx + x, cy + y))
    return pts


def se_front_x(af, b, y, p=2.4):
    r = abs(y) / b
    return af * max(0.0, 1 - r ** p) ** (1.0 / p)


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


def loft_axis(sections, axis="z"):
    """Like loft, but the sections are stacked along 'x' or 'y' instead: [(a, [(u, v) ...])], u/v = the other two axes in x, y, z order."""
    v, f = loft(sections)
    if axis == "z":
        return v, f
    if axis == "x":
        return [(z, x, y) for x, y, z in v], f
    return [(x, z, y) for x, y, z in v], f


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


def revolve(prof, axis, c, seg=24):
    """Solid of revolution. prof = [(a, r), ...] along the axis; c = centre (other two coords in x, y, z order)."""
    vs, fs = [], []
    for a, r in prof:
        for i in range(seg):
            t = 2 * math.pi * i / seg
            u, v = r * math.cos(t), r * math.sin(t)
            vs.append({"x": (a, c[0] + u, c[1] + v), "y": (c[0] + v, a, c[1] + u), "z": (c[0] + u, c[1] + v, a)}[axis])
    fs.append(tuple(reversed(range(seg))))
    fs.append(tuple(range(seg * (len(prof) - 1), seg * len(prof))))
    for k in range(len(prof) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            fs.append((k * seg + i, k * seg + j, (k + 1) * seg + j, (k + 1) * seg + i))
    return vs, fs


def sphere(c, r, seg=20, rings=10, scale=(1, 1, 1)):
    vs = [(c[0], c[1], c[2] + r * scale[2])]
    for k in range(1, rings):
        th = math.pi * k / rings
        for i in range(seg):
            ph = 2 * math.pi * i / seg
            vs.append((c[0] + r * scale[0] * math.sin(th) * math.cos(ph), c[1] + r * scale[1] * math.sin(th) * math.sin(ph), c[2] + r * scale[2] * math.cos(th)))
    vs.append((c[0], c[1], c[2] - r * scale[2]))
    fs = []
    last = len(vs) - 1
    for i in range(seg):
        fs.append((0, 1 + i, 1 + (i + 1) % seg))
    for k in range(rings - 2):
        a, b = 1 + k * seg, 1 + (k + 1) * seg
        for i in range(seg):
            j = (i + 1) % seg
            fs.append((a + i, b + i, b + j, a + j))
    a = 1 + (rings - 2) * seg
    for i in range(seg):
        fs.append((a + (i + 1) % seg, a + i, last))
    return vs, fs


def box(c, h):
    x0, x1, y0, y1, z0, z1 = c[0] - h[0], c[0] + h[0], c[1] - h[1], c[1] + h[1], c[2] - h[2], c[2] + h[2]
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return v, f


def merge(*meshes):
    vs, fs = [], []
    for v, f in meshes:
        o = len(vs)
        vs += [tuple(map(float, p)) for p in v]
        fs += [tuple(i + o for i in x) for x in f]
    return vs, fs


def mirror(mesh):
    v, f = mesh
    return [(x, -y, z) for x, y, z in v], [tuple(reversed(x)) for x in f]


def xform(mesh, R=None, t=(0, 0, 0), about=(0, 0, 0)):
    v, f = mesh
    V = np.array(v, float) - np.array(about, float)
    if R is not None:
        V = V @ np.array(R, float).T
    V = V + np.array(about, float) + np.array(t, float)
    return [tuple(p) for p in V], f


def Rx(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def align_z(n):
    """Rotation taking +z to unit vector n."""
    n = np.array(n, float); n /= np.linalg.norm(n)
    z = np.array([0, 0, 1.0])
    v = np.cross(z, n); c = float(np.dot(z, n))
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * (1 / (1 + c))


def align_x(n):
    """Rotation taking +x to unit vector n (keeps 'up' as close to +z as possible)."""
    n = np.array(n, float); n /= np.linalg.norm(n)
    up = np.array([0, 0, 1.0]) if abs(n[2]) < 0.95 else np.array([0, 1.0, 0])
    y = np.cross(up, n); y /= np.linalg.norm(y)
    z = np.cross(n, y)
    return np.column_stack([n, y, z])


def cyl_ab(a, b, r, seg=12, r2=None):
    """Cylinder (or cone with r2) from point a to point b."""
    a, b = np.array(a, float), np.array(b, float)
    L = float(np.linalg.norm(b - a))
    r2 = r if r2 is None else r2
    v, f = revolve([(0, r), (L, r2)], "z", (0, 0), seg)
    return xform((v, f), align_z(b - a), a)


def tube(path, r, seg=10):
    """Swept circle along a polyline (closed ends)."""
    P = [np.array(p, float) for p in path]
    T = []
    for i in range(len(P)):
        d = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)])
        T.append(d / np.linalg.norm(d))
    ref = np.array([0, 0, 1.0]) if abs(T[0][2]) < 0.9 else np.array([1.0, 0, 0])
    N = np.cross(T[0], ref); N /= np.linalg.norm(N)
    vs, fs = [], []
    for i, p in enumerate(P):
        if i:
            N = N - T[i] * np.dot(N, T[i]); N /= np.linalg.norm(N)
        B = np.cross(T[i], N)
        for k in range(seg):
            t = 2 * math.pi * k / seg
            vs.append(tuple(p + r * (math.cos(t) * N + math.sin(t) * B)))
    fs.append(tuple(reversed(range(seg))))
    fs.append(tuple(range(seg * (len(P) - 1), seg * len(P))))
    for i in range(len(P) - 1):
        for k in range(seg):
            j = (k + 1) % seg
            fs.append((i * seg + k, i * seg + j, (i + 1) * seg + j, (i + 1) * seg + k))
    return vs, fs


def bolts(points, normal, r=0.035, h=0.03, seg=8):
    out = []
    for p in points:
        n = np.array(normal(p) if callable(normal) else normal, float)
        out.append(cyl_ab(np.array(p) - n * 0.01, np.array(p) + n * h, r, seg))
    return merge(*out)


def slats(x, y0, y1, z0, z1, n, depth=0.05, axis="x", t=0.035):
    """n horizontal slats on a plane x = const (axis 'x') or y = const (axis 'y'), spanning the other coordinate y0..y1, z0..z1."""
    out = []
    for k in range(n):
        z = z0 + (z1 - z0) * (k + 0.5) / n
        if axis == "x":
            out.append(box((x, (y0 + y1) / 2, z), (depth / 2, (y1 - y0) / 2, t / 2)))
        else:
            out.append(box(((y0 + y1) / 2, x, z), ((y1 - y0) / 2, depth / 2, t / 2)))
    return merge(*out)


def se_point(u, p):
    n = sum(abs(c) ** p for c in u) ** (1.0 / p)
    return [c / n for c in u]


def bell(c_out, r_out, c_in, r_in, rim, p_out=2.0, seg=40, rings=12, p_in=2.0):
    """Thick shell open at the bottom: outer (super)ellipsoid c_out/r_out (radii per axis), inner sphere c_in/r_in, cut at the
    azimuth-dependent rim height rim(phi) (phi 0 = +x, 90 = +y). Used for the shoulder domes: the arm hub sits in the cavity."""
    def surf(c, r, p, phi, th):
        u = (math.sin(th) * math.cos(phi), math.sin(th) * math.sin(phi), math.cos(th))
        q = se_point(u, p)
        return (c[0] + r[0] * q[0], c[1] + r[1] * q[1], c[2] + r[2] * q[2])

    def th_max(c, r, p, phi, zr):
        lo, hi = 0.0, math.pi
        for _ in range(40):
            mid = (lo + hi) / 2
            if surf(c, r, p, phi, mid)[2] > zr:
                lo = mid
            else:
                hi = mid
        return lo

    rin = r_in if isinstance(r_in, (tuple, list)) else (r_in, r_in, r_in)
    rims = rim if isinstance(rim, (tuple, list)) else (rim, rim)
    vs, fs = [], []
    rings_idx = {}
    for name, c, r, p, rim in (("o", c_out, r_out, p_out, rims[0]), ("i", c_in, rin, p_in, rims[1])):
        top = len(vs)
        vs.append((c[0], c[1], c[2] + r[2]))
        base = len(vs)
        for k in range(seg):
            phi = 2 * math.pi * k / seg
            tm = th_max(c, r, p, phi, rim(phi, surf(c, r, p, phi, math.pi / 2)))
            for i in range(1, rings + 1):
                vs.append(surf(c, r, p, phi, tm * i / rings))
        idx = lambda k, i, base=base: base + (k % seg) * rings + (i - 1)
        for k in range(seg):
            fs.append((top, idx(k, 1), idx(k + 1, 1)) if name == "o" else (top, idx(k + 1, 1), idx(k, 1)))
            for i in range(1, rings):
                q = (idx(k, i), idx(k, i + 1), idx(k + 1, i + 1), idx(k + 1, i))
                fs.append(q if name == "o" else tuple(reversed(q)))
        rings_idx[name] = idx
    io, ii = rings_idx["o"], rings_idx["i"]
    for k in range(seg):
        fs.append((io(k, rings), ii(k, rings), ii(k + 1, rings), io(k + 1, rings)))
    return vs, fs


def chain_links(path, w, t, pitch=0.12, depth=0.06):
    """Ammo belt: a box link every 'pitch' metres along a polyline, link width w (across), thickness t."""
    P = [np.array(p, float) for p in path]
    out = []
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        L = np.linalg.norm(b - a)
        d = (b - a) / L
        n = max(1, int(L / pitch))
        for k in range(n):
            c = a + d * (k + 0.5) * L / n
            R = align_z(d)
            out.append(xform(box((0, 0, 0), (w / 2, t / 2, pitch * 0.38)), R, c))
            out.append(xform(cyl("y", (0, 0), depth * 0.45, -w * 0.42, w * 0.42, 8), R, c))
    return merge(*out)
