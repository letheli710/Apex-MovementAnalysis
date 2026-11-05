#!/usr/bin/env python3
"""Gun path during ADS from the client log (attachment origins, camera fixed): per weapon and phase, delta from hip in game units per zf bin, gun pitch/yaw from sight->muzzle, the sight's progress towards its ADS spot. Writes ADS-CURVES.tsv; prints smoothstep-window fits.
  py -3 -I ads_curves.py <runs dir> <out.tsv>"""
import math, os, re, statistics as st, sys
from collections import defaultdict
sst = lambda t: t * t * (3 - 2 * t)
cl = lambda x: max(0.0, min(1.0, x))
RX = re.compile(r"ad t=([\d.]+) zf=([\d.]+) fov=([\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+) a=\S+ id=(\d+) o=([-\d.]+),([-\d.]+),([-\d.]+) mz=([-\d.]+),([-\d.]+),([-\d.]+)")
BIN = 0.05

def load(p):
    R = []
    for l in open(p, encoding="utf-8"):
        g = RX.search(l)
        if g:
            v = list(map(float, g.groups()))
            s = (v[7] - v[3], -(v[8] - v[4]), v[9] - v[5]); m = (v[10] - v[3], -(v[11] - v[4]), v[12] - v[5])
            ax = (m[0] - s[0], m[1] - s[1], m[2] - s[2])
            R.append(dict(t=v[0], zf=v[1], s=s, pit=math.degrees(math.atan2(ax[2], ax[0])), yaw=math.degrees(math.atan2(ax[1], ax[0]))))
    return R

def main():
    runs, out = sys.argv[1], sys.argv[2]
    tags = sorted(f[:-4] for f in os.listdir(runs) if re.match(r"(r301|wing|spit)_full_\d\.txt", f))
    P = defaultdict(lambda: defaultdict(list)); END = {}
    for tag in tags:
        w = tag.split("_")[0]; R = load(os.path.join(runs, tag + ".txt"))
        first = next(i for i, x in enumerate(R) if x["zf"] > 0)
        h = R[max(0, first - 25):first]; a = [x for x in R if x["zf"] == 1]
        m = lambda L, f: st.mean(f(x) for x in L)
        hs = tuple(m(h, lambda x: x["s"][k]) for k in range(3)); az = tuple(m(a, lambda x: x["s"][k]) for k in range(3))
        hp, hy = m(h, lambda x: x["pit"]), m(h, lambda x: x["yaw"]); ap, ay = m(a, lambda x: x["pit"]), m(a, lambda x: x["yaw"])
        END.setdefault(w, []).append((hs, az, hp, hy, ap, ay))
        up = True
        for i, x in enumerate(R):
            if i and x["zf"] != R[i - 1]["zf"]: up = x["zf"] > R[i - 1]["zf"]
            if i and 0 < x["zf"] < 1:
                d0 = math.dist(hs, az); pr = 1 - math.dist(x["s"], az) / d0
                P[(w, "in" if up else "out")][round(x["zf"] / BIN) * BIN].append((x["s"][0] - hs[0], x["s"][1] - hs[1], x["s"][2] - hs[2], x["pit"] - hp, x["yaw"] - hy, pr, (x["s"][1] - hs[1]) / (az[1] - hs[1])))
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("# R5 local hybrid, measured. Deltas from the hip pose: dF forward, dR right, dU up in game units (camera fixed), dPitch dYaw degrees of the sight->muzzle line, progress = 1 - dist(sight, ADS spot) / dist(hip, ADS spot) (negative = further than at hip), normR = dR / total dR. n = frames over 4 runs. +-1 frame of lag against zf.\n")
        f.write("weapon\tphase\tzf\tn\tdF\tdR\tdU\tdPitch\tdYaw\tprogress\tnormR\n")
        for (w, ph), bins in sorted(P.items()):
            for b in sorted(bins):
                r = bins[b]; av = [st.mean(y[k] for y in r) for k in range(7)]
                f.write(f"{w}\t{ph}\t{b:.2f}\t{len(r)}\t" + "\t".join(f"{a:.3f}" for a in av) + "\n")
    for w, e in END.items():
        mm = lambda i, k: st.mean(x[i][k] for x in e)
        print(w, "hip sight", [round(mm(0, k), 2) for k in range(3)], "ads sight", [round(mm(1, k), 2) for k in range(3)], "gun pitch/yaw change", round(st.mean(x[4] - x[2] for x in e), 2), round(st.mean(x[5] - x[3] for x in e), 2))
    print("fit normR by smoothstep over a window (zf):")
    for (w, ph), bins in sorted(P.items()):
        best = None
        for a in [i * 0.01 for i in range(0, 60)]:
            for b in [i * 0.01 for i in range(int(a * 100) + 5, 101)]:
                e = [st.mean(y[6] for y in bins[z]) - sst(cl((z - a) / (b - a))) for z in bins]
                s = math.sqrt(sum(q * q for q in e) / len(e))
                if best is None or s < best[0]: best = (s, a, b)
        over = max(st.mean(y[6] for y in bins[z]) for z in bins)
        dip = min(st.mean(y[2] for y in bins[z]) for z in bins); top = max(st.mean(y[2] for y in bins[z]) for z in bins)
        pm = max(bins, key=lambda z: abs(st.mean(y[3] for y in bins[z])))
        print(f"  {w} {ph}: window {best[1]:.2f}..{best[2]:.2f} rms {best[0]:.3f}; normR max {over:.2f}; dU min {dip:.2f} max {top:.2f}; largest dPitch {st.mean(y[3] for y in bins[pm]):.2f} deg at zf {pm:.2f}")

if __name__ == "__main__":
    main()
