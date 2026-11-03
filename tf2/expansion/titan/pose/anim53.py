"""Decode MDL v53 sequences and animation tracks into local bone transforms.

Layout worked out from the files themselves (2026-11-02), checked by decoding @ref
against the bone rest pose (see check_ref):
  animdesc, 0x5c bytes: +0 base, +4 name, +8 fps, +0xC flags, +0x10 frames, +0x20 data, +0x24 ikrules
  bone record, 0x20 bytes + tracks: +0 posscale, +4 bone, +5 flags,
    +8 rot (quat64, or 3 shorts of track offsets from +8),
    +0x10 pos (vector48, or 3 shorts of track offsets from +0x10), +0x16 scale, +0x1C next
    flags: 0x02 raw pos, 0x04 raw rot, 0x08 raw scale, 0x01 delta-style record
  tracks are the usual Source RLE value streams, multiplied by bone rotscale / record posscale
"""
import math
import struct

from mdl53 import Mdl, cstr

ANIM_STRIDE = 0x5C
SEQ_STRIDE = 0xE8


def half(u):
    s = (u >> 15) & 1
    e = (u >> 10) & 0x1F
    f = u & 0x3FF
    if e == 0:
        v = f * 2.0 ** -24
    elif e == 31:
        v = float("inf")
    else:
        v = (1 + f / 1024.0) * 2.0 ** (e - 15)
    return -v if s else v


def quat64(b, o):
    v = struct.unpack_from("<Q", b, o)[0]
    x = (v & 0x1FFFFF) - 1048576
    y = ((v >> 21) & 0x1FFFFF) - 1048576
    z = ((v >> 42) & 0x1FFFFF) - 1048576
    k = 1 / 1048576.5
    x, y, z = x * k, y * k, z * k
    w = math.sqrt(max(0.0, 1 - x * x - y * y - z * z))
    if v >> 63:
        w = -w
    return (x, y, z, w)


def euler_quat(e):
    """RadianEuler -> quaternion, Source AngleQuaternion."""
    sr, cr = math.sin(e[0] / 2), math.cos(e[0] / 2)
    sp, cp = math.sin(e[1] / 2), math.cos(e[1] / 2)
    sy, cy = math.sin(e[2] / 2), math.cos(e[2] / 2)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def qconj(q):
    return (-q[0], -q[1], -q[2], q[3])


def qrot(q, v):
    x, y, z, w = q
    tx = 2 * (y * v[2] - z * v[1])
    ty = 2 * (z * v[0] - x * v[2])
    tz = 2 * (x * v[1] - y * v[0])
    return (
        v[0] + w * tx + y * tz - z * ty,
        v[1] + w * ty + z * tx - x * tz,
        v[2] + w * tz + x * ty - y * tx,
    )


def rle(b, o, frame, scale):
    """Source ExtractAnimValue on a byte offset."""
    k = frame
    while True:
        valid, total = b[o], b[o + 1]
        if total == 0:
            return 0.0
        if total <= k:
            k -= total
            o += (valid + 1) * 2
            continue
        idx = k + 1 if valid > k else valid
        return struct.unpack_from("<h", b, o + idx * 2)[0] * scale


class Anim:
    def __init__(self, model, index):
        self.m = model
        b = model.b
        i = model.i
        self.off = o = model.localanimindex + index * ANIM_STRIDE
        self.index = index
        self.name = cstr(b, o + i(o + 4))
        self.fps = struct.unpack_from("<f", b, o + 8)[0]
        self.flags = i(o + 0xC)
        self.frames = i(o + 0x10)
        self.nummovements = i(o + 0x14)
        self.movementindex = i(o + 0x18)
        self.framemovement = i(o + 0x1C)
        self.data = i(o + 0x20)
        self.numik = i(o + 0x24)
        self.ikindex = i(o + 0x28)
        self.sectionindex = i(o + 0x34)
        self.sectionframes = i(o + 0x38)
        self.delta = bool(self.flags & 0x4)
        self.looping = bool(self.flags & 0x1)
        self._records = {}

    def records(self, section=0):
        if section in self._records:
            return self._records[section]
        b, m = self.m.b, self.m
        out = {}
        data = self.data
        if self.sectionframes:
            data = m.i(self.off + self.sectionindex + 4 * section)
        p = self.off + data
        if data == 0:
            self._records[section] = out
            return out
        for _ in range(m.numbones + 2):
            bone, fl = b[p + 4], b[p + 5]
            ps = struct.unpack_from("<f", b, p)[0]
            nxt = struct.unpack_from("<i", b, p + 0x1C)[0]
            out[bone] = (p, fl, ps)
            if nxt == 0:
                break
            p += nxt
        self._records[section] = out
        return out

    def local(self, frame):
        """list of (pos, quat) for each bone; bones without a record stay None."""
        m = self.m
        b = m.b
        res = [None] * m.numbones
        section = 0
        if self.sectionframes:
            section = frame // self.sectionframes
            frame -= section * self.sectionframes
        for bone, (p, fl, ps) in self.records(section).items():
            if bone >= m.numbones:
                continue
            B = m.bones[bone]
            rotscale = struct.unpack_from("<3f", b, B["off"] + 0x60)
            if fl & 0x04:
                q = quat64(b, p + 8)
            else:
                e = []
                for a in range(3):
                    off = struct.unpack_from("<H", b, p + 8 + a * 2)[0]
                    e.append(rle(b, p + 8 + off, frame, rotscale[a]) if off else 0.0)
                if not self.delta:
                    e = [e[a] + B["rot"][a] for a in range(3)]
                q = euler_quat(e)
            if fl & 0x02:
                pos = [half(struct.unpack_from("<H", b, p + 0x10 + a * 2)[0]) for a in range(3)]
            else:
                pos = []
                for a in range(3):
                    off = struct.unpack_from("<H", b, p + 0x10 + a * 2)[0]
                    pos.append(rle(b, p + 0x10 + off, frame, ps) if off else 0.0)
                if not self.delta:
                    pos = [pos[a] + B["pos"][a] for a in range(3)]
            res[bone] = (tuple(pos), q)
        return res


class Seq:
    def __init__(self, model, index):
        self.m = model
        b = model.b
        i = model.i
        o = self.off = model.localseqindex + index * SEQ_STRIDE
        self.index = index
        self.label = cstr(b, o + i(o + 4))
        self.activity = cstr(b, o + i(o + 8)) if i(o + 8) else ""
        self.flags = i(o + 0xC)
        self.numevents = i(o + 0x18)
        self.eventindex = i(o + 0x1C)
        self.numblends = i(o + 0x38)
        self.animindexindex = i(o + 0x3C)
        self.groupsize = (i(o + 0x44), i(o + 0x48))
        self.paramindex = (i(o + 0x4C), i(o + 0x50))
        self.paramstart = struct.unpack_from("<2f", b, o + 0x54)
        self.paramend = struct.unpack_from("<2f", b, o + 0x5C)
        self.fadein, self.fadeout = struct.unpack_from("<2f", b, o + 0x68)
        self.numautolayers = i(o + 0x98) if False else 0

    def anims(self):
        b = self.m.b
        return [struct.unpack_from("<h", b, self.off + self.animindexindex + 2 * k)[0] for k in range(self.numblends)]


def poseparams(m):
    n, idx = m.i(0x130), m.i(0x134)
    out = []
    for k in range(n):
        o = idx + k * 20
        out.append((cstr(m.b, o + m.i(o)),) + struct.unpack_from("<3f", m.b, o + 8))
    return out


def attachments(m):
    n, idx = m.i(0xF4), m.i(0xF8)
    out = []
    for k in range(n):
        o = idx + k * 92
        mat = struct.unpack_from("<12f", m.b, o + 12)
        out.append(dict(name=cstr(m.b, o + m.i(o)), bone=m.i(o + 8), pos=(mat[3], mat[7], mat[11]), mat=mat))
    return out


def rest_local(m):
    return [(B["pos"], B["quat"]) for B in m.bones]


def world(m, local, base=None):
    """local list (None -> rest) to world pos/quat per bone."""
    rest = rest_local(m)
    w = [None] * m.numbones
    for n, B in enumerate(m.bones):
        lp, lq = local[n] if local[n] is not None else rest[n]
        if B["parent"] < 0:
            w[n] = (tuple(lp), lq)
        else:
            pp, pq = w[B["parent"]]
            r = qrot(pq, lp)
            w[n] = ((pp[0] + r[0], pp[1] + r[1], pp[2] + r[2]), qmul(pq, lq))
    return w


def check_ref(m):
    a = Anim(m, 0)
    L = a.local(0)
    worst = 0
    worstp = 0
    for n, B in enumerate(m.bones):
        if L[n] is None:
            continue
        q, q2 = L[n][1], B["quat"]
        d = abs(sum(x * y for x, y in zip(q, q2)))
        ang = 2 * math.degrees(math.acos(min(1, d)))
        worst = max(worst, ang)
        worstp = max(worstp, max(abs(L[n][0][k] - B["pos"][k]) for k in range(3)))
    return a.name, len(a.records()), worst, worstp


if __name__ == "__main__":
    import sys

    m = Mdl(sys.argv[1])
    print(check_ref(m))
    print(poseparams(m))
    for k in range(m.numlocalseq):
        s = Seq(m, k)
        names = [Anim(m, x).name for x in s.anims()][:3]
        print(k, s.label, "|", s.activity, "| blends", s.numblends, s.groupsize, s.paramindex, s.paramstart, s.paramend, "fade", round(s.fadein, 2), round(s.fadeout, 2), names)
