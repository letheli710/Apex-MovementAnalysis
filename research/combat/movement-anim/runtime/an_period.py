#!/usr/bin/env python3
"""Bob period by mean-crossings of the view-model yaw (vmaY) in the steady part of each walk / crouch-walk / sprint run (from 1.2 s after +forward to -forward).
  py -3 -I an_period.py <raw runtime dir>   -> prints tag, speed, period (s), distance per period (u), yaw / roll half-range"""
import gzip, csv, sys, os, math, bisect, collections

def opn(p):
    """plain file, or its .gz (the raw repo keeps the big CSVs gzipped)"""
    return open(p, encoding="utf-8") if os.path.exists(p) else gzip.open(p + ".gz", "rt", encoding="utf-8")
D = sys.argv[1]
MK = collections.defaultdict(list)
for l in open(os.path.join(D, "marks.tsv"), encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    MK[p[0]].append((float(p[1]) * 1000, p[2]))
F = []
with opn(os.path.join(D, "frida", "frames.csv")) as fh:
    rd = csv.DictReader(fh)
    for x in rd:
        try: F.append((float(x["w"]), float(x["ct10"]), float(x["vx"]), float(x["vy"]), float(x["vmaY"]), float(x["vmaR"])))
        except ValueError: pass
W = [f[0] for f in F]
print("tag\tspeed\tperiod_s\tunits_per_period\tyaw_half\troll_half")
for tag in sorted(MK):
    if not any(s in tag for s in ("walk", "_cw_", "sprint")) or tag.startswith("t_"): continue
    on = [t for t, m in MK[tag] if m == ("+speed" if "sprint" in tag else "+forward")]
    off = [t for t, m in MK[tag] if m == ("-speed" if "sprint" in tag else "-forward")]
    if not on or not off: continue
    a = on[0] + (1500 if "sprint" in tag else 1200); b = off[0]
    fr = F[bisect.bisect_left(W, a):bisect.bisect_right(W, b)]
    if len(fr) < 100: continue
    if "wall" in tag: fr = [f for f in fr if math.hypot(f[2], f[3]) < 50]
    if len(fr) < 100: continue
    y = [f[4] for f in fr]; m = sum(y) / len(y)
    cr = [fr[i][1] for i in range(1, len(fr)) if (y[i - 1] - m) < 0 <= (y[i] - m)]
    if len(cr) < 2: continue
    per = (cr[-1] - cr[0]) / (len(cr) - 1)
    v = sum(math.hypot(f[2], f[3]) for f in fr) / len(fr)
    ys = sorted(y); rs = sorted(f[5] for f in fr)
    h = lambda s: (s[int(.95 * len(s))] - s[int(.05 * len(s))]) / 2
    print(f"{tag}\t{v:.1f}\t{per:.3f}\t{v * per:.0f}\t{h(ys):.2f}\t{h(rs):.2f}")
