#!/usr/bin/env python3
"""ADS curves. Cuts view.csv / vm.csv by marks.tsv; fits FOV and the view model offset to the formulas; prints the attachment path from the client log, normalised per frame.
  py -3 -I analyze_ads.py <dir with view.csv vm.csv marks.tsv wall.txt> <runs dir>"""
import csv, math, os, re, statistics as st, sys
from collections import defaultdict

CFG = {"r301": dict(z=55, hip=(0, 1.1, 0.4), ads=(0, 0.38, 0), ti=0.27, to=0.23), "wing": dict(z=60, hip=None, ads=(0, 1.0, 0), ti=0.18, to=0.16), "spit": dict(z=55, hip=(0, 1.4, 0.4), ads=(0, 1.3, 0), ti=0.34, to=0.30)}
SCALE = 1.27217  # cl_fovScale here: 69.97 / 55, 76.33 / 60
sst = lambda t: t * t * (3 - 2 * t)
cosc = lambda t: (1 - math.cos(math.pi * t)) / 2
cl = lambda x: max(0.0, min(1.0, x))

def rows(p):
    out = []
    for r in csv.DictReader(open(p)):
        try: out.append({k: float(v) for k, v in r.items() if k})
        except (TypeError, ValueError): pass
    return out

def main():
    d, runs = sys.argv[1], sys.argv[2]
    wall = int(open(os.path.join(d, "wall.txt")).read()) / 1000
    V, Mf = rows(os.path.join(d, "view.csv")), rows(os.path.join(d, "vm.csv"))
    marks = defaultdict(list)
    for l in open(os.path.join(d, "marks.tsv"), encoding="utf-8"):
        t, ts, m = l.rstrip("\n").split("\t"); marks[t].append((float(ts) - wall, m))
    agg = defaultdict(list)
    print("## FOV: 3t^2-2t^3 of zf (window 0..1) from base to zoom_fov * cl_fovScale; residual degrees. zf slope against 1/time")
    for tag, m in marks.items():
        w = tag.split("_")[0]; c = CFG[w]
        t0, t1 = m[0][0], m[-1][0] + 0.2
        fr = [r for r in V if t0 <= r["t"] <= t1]; vm = [r for r in Mf if t0 <= r["t"] <= t1]
        if not fr: continue
        base = fr[0]["fov"]; zo = c["z"] * SCALE
        res = [r["fov"] - (base + (zo - base) * sst(cl(r["zf"]))) for r in fr]
        tin = [(a, b) for a, b in zip(fr, fr[1:]) if 0.02 < b["zf"] < 0.98 and b["zf"] > a["zf"]]
        tout = [(a, b) for a, b in zip(fr, fr[1:]) if 0.02 < b["zf"] < 0.98 and b["zf"] < a["zf"]]
        sl = lambda p: (sum(abs(b["zf"] - a["zf"]) for a, b in p) / sum(b["ct"] - a["ct"] for a, b in p)) if p and sum(b["ct"] - a["ct"] for a, b in p) > 0 else float("nan")
        print(f"{tag}\tbase={base:.1f} min={min(r['fov'] for r in fr):.2f} expect={zo:.2f} maxres={max(abs(x) for x in res):.3f} meanres={st.mean(res):+.3f} in_t={1 / sl(tin) if tin else 0:.3f}({c['ti']}) out_t={1 / sl(tout) if tout else 0:.3f}({c['to']})")
        for r in vm:
            agg[w].append(r)
    print("## vm offset: dF dU against the cosine of zf over the window; window from the data. Per weapon")
    for w, r in agg.items():
        z = sorted({round(x["zf"], 3) for x in r})
        hipF = st.median(x["dF"] for x in r if x["zf"] == 0); hipU = st.median(x["dU"] for x in r if x["zf"] == 0)
        adsF = st.median(x["dF"] for x in r if x["zf"] == 1); adsU = st.median(x["dU"] for x in r if x["zf"] == 1)
        print(w, f"hip F,U = {hipF:.3f},{hipU:.3f}  ads F,U = {adsF:.3f},{adsU:.3f}")
        best = None
        for a in [i * 0.05 for i in range(0, 8)]:
            for b in [i * 0.05 for i in range(8, 21)]:
                e = [(x["dU"] - (hipU + (adsU - hipU) * cosc(cl((x["zf"] - a) / (b - a))))) for x in r if 0 < x["zf"] < 1] + [(x["dF"] - (hipF + (adsF - hipF) * cosc(cl((x["zf"] - a) / (b - a))))) for x in r if 0 < x["zf"] < 1]
                s = math.sqrt(sum(q * q for q in e) / len(e))
                if best is None or s < best[0]: best = (s, a, b)
        print("   best window", f"{best[1]:.2f}..{best[2]:.2f} rms={best[0]:.4f}")
    print("## attachments (client log) in camera axes: forward = +x, right = -y, up = +z; normalised path per zf")
    bins = [i / 10 for i in range(11)]
    for w, att in (("r301", "sight"), ("wing", "sight"), ("spit", "sight")):
        P = {"in": defaultdict(list), "out": defaultdict(list)}
        ends = []
        for tag in marks:
            if not tag.startswith(w + "_full"): continue
            rowsl = []
            for l in open(os.path.join(runs, tag + ".txt"), encoding="utf-8"):
                g = re.search(r"ad t=([\d.]+) zf=([\d.]+) fov=([\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+) a=\S+ id=(\d+) o=([-\d.]+),([-\d.]+),([-\d.]+) mz=([-\d.]+),([-\d.]+),([-\d.]+)", l)
                if g:
                    v = list(map(float, g.groups()))
                    rowsl.append(dict(t=v[0], zf=v[1], fov=v[2], s=(v[7] - v[3], -(v[8] - v[4]), v[9] - v[5]), m=(v[10] - v[3], -(v[11] - v[4]), v[12] - v[5])))
            first = next(i for i, x in enumerate(rowsl) if x["zf"] > 0)
            h = rowsl[max(0, first - 25):first]; a = [x for x in rowsl if x["zf"] == 1]
            if not h or not a: continue
            mean = lambda L, key: tuple(st.mean(x[key][i] for x in L) for i in range(3))
            hs, as_ = mean(h, "s"), mean(a, "s"); hm, am = mean(h, "m"), mean(a, "m"); ends.append((hs, as_, hm, am))
            up = True
            for i, x in enumerate(rowsl):
                if i and x["zf"] != rowsl[i - 1]["zf"]: up = x["zf"] > rowsl[i - 1]["zf"]
                if 0 < x["zf"] < 1:
                    b = round(x["zf"] * 20) / 20
                    P["in" if up else "out"][b].append(tuple((x["s"][k] - hs[k]) / (as_[k] - hs[k]) if abs(as_[k] - hs[k]) > 0.05 else float("nan") for k in range(3)) + tuple((x["m"][k] - hm[k]) / (am[k] - hm[k]) if abs(am[k] - hm[k]) > 0.05 else float("nan") for k in range(3)) + (x["s"][1], x["s"][2],))
        mp = lambda k: [round(st.mean(e[k][i] for e in ends), 2) for i in range(3)]
        print(w, "sight hip", mp(0), "ads", mp(1), "| muzzle hip", mp(2), "ads", mp(3))
        for ph in ("in", "out"):
            print(" ", ph, "zf: sight(F,R,U) muzzle(F,R,U)  [smoothstep cosine(0..0.5 window)]")
            for b in sorted(P[ph]):
                r = P[ph][b]
                av = [st.mean(y[k] for y in r if y[k] == y[k]) if any(y[k] == y[k] for y in r) else float("nan") for k in range(6)]
                print(f"   {b:.2f} n={len(r):2d} " + " ".join(f"{a:+.2f}" for a in av) + f"   [{sst(b):.2f} {cosc(cl(b / 0.5)):.2f}]")


if __name__ == "__main__":
    main()
