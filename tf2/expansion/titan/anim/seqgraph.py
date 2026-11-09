"""Dump the titan animation graph from MDL v53: every sequence with its blend grid,
fades, layers, bone weights, IK rules, root motion and events.

Research tool only: reads numbers and names from the local game's models (never copies
animation data out). Output: anim/out/seqgraph_<chassis>.csv and seqgraph_pov.csv.

Layout added on top of ../pose/anim53.py (worked out 2026-11-09 from the files, see
ANIM-BLEND.md appendix A):
  seqdesc +0x64 paramparent, +0x68 fadein, +0x6C fadeout, +0x90 numikrules,
          +0x94 numautolayers, +0x98 autolayerindex, +0x9C weightlistindex,
          +0xA0 posekeyindex, +0xA4 numiklocks, +0xA8 iklockindex, +0xBC numactivitymodifiers
  autolayer 24 bytes: short seq, short pose, int flags, float start, peak, tail, end
  weightlist: float per bone
  ikrule (animdesc +0x24 count, +0x28 offset) 140 bytes: int index, type, chain, bone, slot,
          float height, radius, floor, pos[3], q[4], int compressedErr, int iStart, int ikErr,
          float start, peak, tail, end, contact
  activity modifier (+0xB8 offset, +0xBC count) 8 bytes: int name offset, int flags
  framemovement (animdesc +0x1C): float scale[4] (x, y, z, yaw), short offset[4] -> RLE tracks
"""
import csv
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pose"))
from anim53 import Anim, Mdl, Seq, cstr, poseparams, rle  # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "local", "titan-models", "models")
OUT = os.path.join(HERE, "out")
CHASSIS = {"light": "titans/light/titan_light", "medium": "titans/medium/titan_medium", "heavy": "titans/heavy/titan_heavy"}
PARTS = ["mp_core", "mp_embark", "mp_reactions", "mp_melee", "mp_scripted", "mp_synced", "sp_core"]
POV = ["weapons/arms/pov_titan_%s_cockpit" % c for c in ("light", "medium", "heavy")]

SEQ_FLAGS = {0x1: "loop", 0x2: "snap", 0x4: "delta", 0x8: "autoplay", 0x10: "post", 0x20: "allzeros",
             0x40: "frameanim", 0x80: "cyclepose", 0x100: "realtime", 0x200: "local", 0x400: "hidden",
             0x800: "override", 0x1000: "activity", 0x2000: "event", 0x4000: "world"}
IK_TYPE = {1: "self", 2: "world", 3: "ground", 4: "release", 5: "attachment", 6: "unlatch"}


def flags_str(f):
    return "|".join(n for b, n in SEQ_FLAGS.items() if f & b) or "-"


def seq_extra(m, s):
    b, i, o = m.b, m.i, s.off
    d = {}
    d["paramparent"] = i(o + 0x64)
    d["numikrules"] = i(o + 0x90)
    nal, ali = i(o + 0x94), i(o + 0x98)
    layers = []
    for k in range(nal):
        p = o + ali + 24 * k
        sq, pose = struct.unpack_from("<hh", b, p)
        fl = i(p + 4)
        st, pk, tl, en = struct.unpack_from("<4f", b, p + 8)
        layers.append((sq, pose, fl, round(st, 3), round(pk, 3), round(tl, 3), round(en, 3)))
    d["layers"] = layers
    wli = i(o + 0x9C)
    d["weights"] = struct.unpack_from("<%df" % m.numbones, b, o + wli) if wli else None
    d["numiklocks"] = i(o + 0xA4)
    mods = []
    for k in range(i(o + 0xBC)):  # activity modifiers: 8 bytes each, +0 name offset
        p = o + i(o + 0xB8) + 8 * k
        mods.append(cstr(b, p + i(p)))
    d["mods"] = mods
    return d


def ikrules(m, a):
    b = m.b
    out = []
    for k in range(a.numik):
        r = a.off + a.ikindex + 140 * k
        ints = struct.unpack_from("<35i", b, r)
        fl = struct.unpack_from("<35f", b, r)
        start = fl[18]
        out.append(dict(type=IK_TYPE.get(ints[1], ints[1]), chain=ints[2], height=fl[5], radius=fl[6],
                        start=round(start, 3), peak=round(fl[19], 3), tail=round(fl[20], 3), end=round(fl[21], 3),
                        contact=round(fl[22], 3)))
    return out


def root_motion(m, a):
    """(dx, dy, dz, dyaw) over the whole clip from the per-frame movement tracks, or None."""
    fm = m.i(a.off + 0x1C)
    if not fm:
        return None
    o = a.off + fm
    sc = struct.unpack_from("<4f", m.b, o)
    offs = struct.unpack_from("<4h", m.b, o + 16)
    last = a.frames - 1
    return tuple(rle(m.b, o + offs[c], last, sc[c]) if offs[c] else 0.0 for c in range(4))


def events(m, s):
    """Sequence events; stride found by trying (same method as ../pose/events.py)."""
    b, i = m.b, m.i
    if not s.numevents:
        return []
    for st in (0x50, 0x54, 0x58, 0x110, 0x114, 0x118):
        tmp = []
        ok = True
        for k in range(s.numevents):
            o = s.off + s.eventindex + k * st
            c = struct.unpack_from("<f", b, o)[0]
            if not (-0.01 <= c <= 1.01):
                ok = False
                break
            nameoff = i(o + st - 4)
            name = cstr(b, o + nameoff)[:40] if 0 < o + nameoff < len(b) else ""
            opts = cstr(b, o + 12)[:50]
            tmp.append((round(c, 3), name or opts))
        if ok:
            return tmp
    return [("?", "?")]


def bone_groups(m, w):
    """Mean weight on legs / pelvis / spine / arms for a weight list (None = all 1)."""
    if w is None:
        return "all1"
    groups = {"legs": ("thigh", "knee", "ankle", "ball"), "hip": ("def_c_hip",), "spine": ("spine",),
              "arms": ("shoulder", "elbow", "wrist", "clav"), "cam": ("camera", "jx_c_pov")}
    res = []
    for g, keys in groups.items():
        vals = [w[k] for k, B in enumerate(m.bones) if any(x in B["name"] for x in keys)]
        if vals:
            res.append("%s=%.2f" % (g, sum(vals) / len(vals)))
    return " ".join(res)


def dump(model_path, tag, rows):
    m = Mdl(model_path)
    pps = poseparams(m)
    for k in range(m.numlocalseq):
        s = Seq(m, k)
        ex = seq_extra(m, s)
        an = s.anims()
        mid = Anim(m, an[len(an) // 2]) if an else None
        dur = (mid.frames - 1) / mid.fps if mid and mid.fps else 0
        rm = root_motion(m, mid) if mid else None
        speed = ""
        if rm and dur > 0:
            speed = round((rm[0] ** 2 + rm[1] ** 2) ** 0.5 / dur, 1)
        params = []
        for a in range(2):
            pi = s.paramindex[a]
            if pi >= 0 and pi < len(pps):
                params.append("%s[%g..%g]x%d" % (pps[pi][0], s.paramstart[a], s.paramend[a], s.groupsize[a]))
        iks = ikrules(m, mid) if mid else []
        ikstr = " ; ".join("%s c%d %g/%g/%g/%g ct%g" % (r["type"], r["chain"], r["start"], r["peak"], r["tail"], r["end"], r["contact"]) for r in iks)
        layers = []
        for (sq, pose, fl, st, pk, tl, en) in ex["layers"]:
            nm = Seq(m, sq).label if 0 <= sq < m.numlocalseq else "#%d" % sq
            layers.append("%s pose%d fl%#x %g/%g/%g/%g" % (nm, pose, fl, st, pk, tl, en))
        ev = events(m, s)
        rows.append([tag, k, s.label, s.activity, "+".join(ex["mods"]), flags_str(s.flags), len(an), " ".join(params),
                     round(s.fadein, 3), round(s.fadeout, 3), mid.frames if mid else 0, round(mid.fps, 1) if mid else 0,
                     round(dur, 3), " | ".join(layers), bone_groups(m, ex["weights"]), ex["numiklocks"], ikstr,
                     "" if rm is None else "%.1f %.1f %.1f %.1f" % rm, speed,
                     " ; ".join("%s:%s" % e for e in ev)[:700],
                     " ".join(Anim(m, x).name for x in an)[:300]])


HEAD = ["part", "idx", "seq", "activity", "modifiers", "flags", "nblend", "params", "fadein", "fadeout", "frames", "fps", "dur",
        "autolayers", "weights", "iklocks", "ikrules(type chain start/peak/tail/end contact)", "rootmotion(dx dy dz dyaw)",
        "ground_speed", "events(cycle:name)", "anims"]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for ch, base in CHASSIS.items():
        rows = []
        for part in PARTS:
            p = os.path.join(ROOT, base + "_" + part + ".mdl")
            if os.path.exists(p):
                dump(p, part, rows)
        with open(os.path.join(OUT, "seqgraph_%s.csv" % ch), "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([HEAD] + rows)
        print(ch, len(rows))
    rows = []
    for p in POV:
        dump(os.path.join(ROOT, p + ".mdl"), os.path.basename(p), rows)
    with open(os.path.join(OUT, "seqgraph_pov.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([HEAD] + rows)
    print("pov", len(rows))
