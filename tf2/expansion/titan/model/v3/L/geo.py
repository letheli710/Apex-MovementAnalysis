"""Mesh primitives for the light titans. Pure Python + numpy, no bpy.
Coordinates: ANALYSIS axes, world rest position (x forward, y left, z up, metres). A mesh is (verts, faces)."""
import math

import numpy as np


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
    a = np.array(v, float) - np.array(about, float)
    if R is not None:
        a = a @ np.array(R, float).T
    a = a + np.array(about, float) + np.array(t, float)
    return [tuple(p) for p in a], f


def Rx(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def Raxis(axis, d):
    a = np.array(axis, float); a /= np.linalg.norm(a)
    t = math.radians(d); c, s = math.cos(t), math.sin(t)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


def frame_from(axis):
    """Orthonormal (u, v, w) with w along axis."""
    w = np.array(axis, float); w /= np.linalg.norm(w)
    h = np.array((0, 0, 1.0)) if abs(w[2]) < 0.9 else np.array((1.0, 0, 0))
    u = np.cross(h, w); u /= np.linalg.norm(u)
    return u, np.cross(w, u), w


# ------------------------------------------------------------------ outlines (2D, CCW seen from +z)
def rect(x0, x1, y0, y1, c=0.06):
    c = min(c, (x1 - x0) / 2.01, (y1 - y0) / 2.01)
    return [(x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c), (x0 + c, y0), (x1 - c, y0)]


def ellipse(cx, cy, rx, ry, n=16, a0=0.0):
    return [(cx + rx * math.cos(a0 + 2 * math.pi * i / n), cy + ry * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def teardrop_dense(xf, xb, w, sharp=0.42, n=240):
    """Top-view bullet: rounded back at xb, pointed front at xf, half-width w. Dense CCW polyline starting at the nose."""
    xm, ax = (xf + xb) / 2, (xf - xb) / 2
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        f = 1 - sharp * ((1 + c) / 2) ** 2
        pts.append((xm + ax * c, w * s * f))
    return pts


def _resample(poly, m, closed=False):
    p = np.array(poly, float)
    if closed:
        p = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    tt = np.linspace(0, d[-1], m + (1 if closed else 0))[: m]
    return [(float(np.interp(t, d, p[:, 0])), float(np.interp(t, d, p[:, 1]))) for t in tt]


def split_teardrop(xf, xb, w, xcut, m_body, m_nose, sharp=0.42):
    """Cut the bullet at x = xcut. Returns (body outline, nose outline); each closes with a straight edge along the cut.
    Point counts are fixed so sections loft."""
    d = teardrop_dense(xf, xb, w, sharp)
    n = len(d)
    # rotate so the list starts at the back (index n/2) and goes CCW: back -> right side -> nose -> left side -> back
    d = d[n // 2:] + d[: n // 2]
    xcut = min(xcut, xf - 1e-3)
    body, nose = [], []
    for i in range(n):
        a, b = d[i], d[(i + 1) % n]
        if a[0] <= xcut:
            body.append(a)
        else:
            nose.append(a)
        if (a[0] - xcut) * (b[0] - xcut) < 0:
            t = (xcut - a[0]) / (b[0] - a[0])
            q = (xcut, a[1] + t * (b[1] - a[1]))
            body.append(q)
            nose.append(q)
    # body: CCW from back through right side to cut (right), then (cut left) ... back. Nose list starts at right cut point.
    # make the body polyline open at the cut: rotate so it starts at the left cut point
    k = [i for i, p in enumerate(body) if abs(p[0] - xcut) < 1e-9]
    if len(k) == 2:
        i0 = k[1]
        body = body[i0:] + body[:i0]
    nk = [i for i, p in enumerate(nose) if abs(p[0] - xcut) < 1e-9]
    if len(nk) == 2:
        nose = nose[nk[0]:nk[1] + 1]
    return _resample(body, m_body), _resample(nose, m_nose)


# ------------------------------------------------------------------ solids
def loft(sections, cap=True):
    """Closed solid through horizontal sections [(z, [(x, y) ...]), ...], every section the same point count (CCW)."""
    vs, faces = [], []
    n = len(sections[0][1])
    for z, pts in sections:
        vs += [(x, y, z) for x, y in pts]
    if cap:
        faces.append(tuple(reversed(range(n))))
        faces.append(tuple(range(n * (len(sections) - 1), n * len(sections))))
    for s in range(len(sections) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((s * n + i, s * n + j, (s + 1) * n + j, (s + 1) * n + i))
    return vs, faces


def loft3(sections):
    """Like loft but every section is a list of 3D points (any orientation), same count, consistently ordered."""
    vs, faces = [], []
    n = len(sections[0])
    for pts in sections:
        vs += [tuple(map(float, p)) for p in pts]
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple(range(n * (len(sections) - 1), n * len(sections))))
    for s in range(len(sections) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((s * n + i, s * n + j, (s + 1) * n + j, (s + 1) * n + i))
    return vs, faces


def box(c, h, ch=0.04):
    """Axis box centre c, half sizes h, vertical edges chamfered."""
    x, y, z = c
    return loft([(z - h[2], rect(x - h[0], x + h[0], y - h[1], y + h[1], ch)), (z + h[2], rect(x - h[0], x + h[0], y - h[1], y + h[1], ch))])


def extrude(profile, plane, a0, a1):
    """Extrude a 2D CCW profile. plane 'xz': profile (x, z), extruded along y from a0 to a1. 'yz': (y, z) along x. 'xy': (x, y) along z."""
    def p3(u, v, a):
        return {"xz": (u, a, v), "yz": (a, u, v), "xy": (u, v, a)}[plane]
    n = len(profile)
    vs = [p3(u, v, a0) for u, v in profile] + [p3(u, v, a1) for u, v in profile]
    f0, f1 = tuple(reversed(range(n))), tuple(range(n, 2 * n))
    side = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    if plane == "xz":  # (x, z) CCW looking from +y means outward normals need the reversed order
        f0, f1 = tuple(range(n)), tuple(reversed(range(n, 2 * n)))
        side = [tuple(reversed(s)) for s in side]
    return vs, [f0, f1] + side


def tube(a, b, r, seg=12, r2=None):
    """Cylinder / cone between points a and b."""
    a, b = np.array(a, float), np.array(b, float)
    u, v, w = frame_from(b - a)
    r2 = r if r2 is None else r2
    secs = []
    for c, rr in ((a, r), (b, r2)):
        secs.append([c + rr * (math.cos(2 * math.pi * i / seg) * u + math.sin(2 * math.pi * i / seg) * v) for i in range(seg)])
    return loft3(secs)


def lathe(a, b, prof, seg=16):
    """Solid of revolution along a->b; prof = [(t along 0..1, radius), ...]."""
    a, b = np.array(a, float), np.array(b, float)
    u, v, w = frame_from(b - a)
    secs = []
    for t, r in prof:
        c = a + (b - a) * t
        secs.append([c + r * (math.cos(2 * math.pi * i / seg) * u + math.sin(2 * math.pi * i / seg) * v) for i in range(seg)])
    return loft3(secs)


def sweep_rect(path, w, h, up=(0, 0, 1)):
    """Rectangular bar (w across, h along 'up') along a polyline."""
    path = [np.array(p, float) for p in path]
    secs = []
    for i, p in enumerate(path):
        d = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)])
        d /= np.linalg.norm(d)
        s = np.cross(d, up); s /= np.linalg.norm(s)
        uu = np.cross(s, d)
        secs.append([p + s * w / 2 + uu * h / 2, p - s * w / 2 + uu * h / 2, p - s * w / 2 - uu * h / 2, p + s * w / 2 - uu * h / 2])
    return loft3(secs)


def bolt_ring(c, axis, R, r, n, length=0.03, seg=6):
    """n bolt heads on a circle of radius R around c, facing along axis."""
    u, v, w = frame_from(axis)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        p = np.array(c, float) + R * (math.cos(t) * u + math.sin(t) * v)
        out.append(tube(p, p + w * length, r, seg))
    return merge(*out)


def bolts_line(a, b, axis, r, n, length=0.03, seg=6):
    a, b = np.array(a, float), np.array(b, float)
    w = np.array(axis, float); w /= np.linalg.norm(w)
    return merge(*[tube(a + (b - a) * (i / max(n - 1, 1)), a + (b - a) * (i / max(n - 1, 1)) + w * length, r, seg) for i in range(n)])


def piston(a, b, r_body, r_rod, split=0.55, seg=10):
    """Hydraulic: body cylinder from a, rod to b, end eyes."""
    a, b = np.array(a, float), np.array(b, float)
    m = a + (b - a) * split
    return merge(tube(a, m, r_body, seg), tube(m - (b - a) * 0.02, b, r_rod, seg), tube(a - (b - a) * 0.03, a + (b - a) * 0.03, r_body * 1.35, seg),
                 tube(b - (b - a) * 0.04, b, r_rod * 1.6, seg))


def grille(c, axis_n, axis_u, w, h, n, bar=0.025, depth=0.04):
    """n slats across a w x h opening centred at c; slats run along axis_u, normal axis_n."""
    nrm = np.array(axis_n, float); nrm /= np.linalg.norm(nrm)
    u = np.array(axis_u, float); u /= np.linalg.norm(u)
    v = np.cross(nrm, u)
    out = []
    for i in range(n):
        off = (i - (n - 1) / 2) * (h / n)
        p = np.array(c, float) + v * off
        out.append(sweep_rect([p - u * w / 2, p + u * w / 2], bar * 1.6, depth, up=nrm) if abs(np.dot(nrm, (0, 0, 1))) < 0.9 else
                   sweep_rect([p - u * w / 2, p + u * w / 2], bar * 1.6, depth, up=v))
    return merge(*out)
