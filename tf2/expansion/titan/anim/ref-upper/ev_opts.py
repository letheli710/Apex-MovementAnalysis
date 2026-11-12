"""F21: every titan sequence event with its option string; finds screen shake / rumble on footsteps.
Reads local unpacked models only (never copies animation data). Output: out/ev_opts_<chassis>.csv
Usage: py -3 -I ev_opts.py"""
import csv, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pose"))
sys.path.insert(0, os.path.join(HERE, ".."))
from anim53 import Mdl, Seq, cstr  # noqa: E402
from seqgraph import CHASSIS, PARTS, ROOT  # noqa: E402

def events(m, s):
    b, i = m.b, m.i
    if not s.numevents:
        return []
    for st in (0x50, 0x54, 0x58, 0x110, 0x114, 0x118):
        tmp = []
        for k in range(s.numevents):
            o = s.off + s.eventindex + k * st
            c = struct.unpack_from("<f", b, o)[0]
            if not (-0.01 <= c <= 1.01):
                tmp = None
                break
            nameoff = i(o + st - 4)
            name = cstr(b, o + nameoff)[:48] if 0 < o + nameoff < len(b) else ""
            tmp.append((round(c, 3), name, cstr(b, o + 12)[:120]))
        if tmp is not None:
            return tmp
    return []

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
for ch, base in CHASSIS.items():
    rows = []
    for part in PARTS:
        p = os.path.join(ROOT, base + "_" + part + ".mdl")
        if not os.path.exists(p):
            continue
        m = Mdl(p)
        for k in range(m.numlocalseq):
            s = Seq(m, k)
            for c, n, o in events(m, s):
                rows.append([ch, part, s.label, s.activity, c, n, o])
    with open(os.path.join(HERE, "out", "ev_opts_%s.csv" % ch), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["ch", "part", "seq", "activity", "cycle", "event", "options"]] + rows)
    print(ch, len(rows))
