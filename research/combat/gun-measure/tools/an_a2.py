#!/usr/bin/env python3
"""A2 details from one session dir and the runs: pellet radius, barrel kick ratio, optics FOV windows and zoom times, stock timing, laser spread.
  py -3 -I an_a2.py <session dir> <runs dir>"""
import math, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut

sst = lambda t: t * t * (3 - 2 * t)
cl = lambda x: max(0.0, min(1.0, x))


def hits(runs, tag):
    return [(float(a), int(h), float(y), float(z)) for a, h, y, z in re.findall(r"\[RT\] dmg t=\S+ amt=([\d.]+) hg=(\d+) .*?pos=\S+?,([-\d.]+),([-\d.]+)", open(os.path.join(runs, tag + ".txt"), encoding="utf-8").read())]


def main():
    d, runs = sys.argv[1], sys.argv[2]
    F, S, M = load(d)
    print("## pellet spread at 150 u: radius in degrees about the mean per shot, all pellets")
    for t in M:
        if not re.match(r"(ck_|c2_|dt_eva|st_r3030_shatter|hp_moz)", t): continue
        H = hits(runs, t)
        if len(H) < 4: continue
        my, mz = st.mean(x[2] for x in H), st.mean(x[3] for x in H)
        r = [math.degrees(math.atan2(math.hypot(x[2] - my, x[3] - mz), 150)) for x in H]
        print(f"{t}\tn={len(H)}\tmean_r={st.mean(r):.2f}\tmax_r={max(r):.2f}\tspread_y={st.pstdev(x[2] for x in H):.2f}u\tspread_z={st.pstdev(x[3] for x in H):.2f}u")
    print("## barrel: kick per row against the table, mean of dpitch / (hard * row) over ADS bursts; peak s2 at the end")
    G = {}
    for t in M:
        g = re.match(r"bs_r301_(.+)_\d$", t)
        if not g: continue
        a, b = M[t][0][0], M[t][-1][0] + 0.2
        sh = cut(S, a, b)
        rr = [((x["s2P1"] - x["s2P0"]) / x["hard"]) for x in sh if x["hard"]]
        cc = [x["c1"] for x in sh]
        ry = [((x["s2Y1"] - x["s2Y0"]) / x["hard"]) for x in sh if x["hard"]]
        cy = [x["c0"] for x in sh]
        fr = cut(F, a, b)
        G.setdefault(g[1], []).append((sum(rr) / sum(cc) if sum(cc) else 0, max(abs(x["s2P"]) for x in fr), max(abs(x["s2Y"]) for x in fr), st.pstdev(a2 - c2 for a2, c2 in zip(rr, cc))))
    for k, v in G.items():
        print(f"{k}\tpitch_ratio={st.mean(x[0] for x in v):.3f}\tpeakP={st.mean(x[1] for x in v):.2f}\tpeakY={st.mean(x[2] for x in v):.2f}\trow_sd={st.mean(x[3] for x in v):.3f}")
    print("## optics: base, end FOV, fitted smoothstep window of zf, zoom in/out time")
    for t in M:
        if not t.startswith(("op_", "tk_", "sn_", "o2_")): continue
        a, b = M[t][0][0], M[t][-1][0] + 0.2
        fr = cut(F, a, b)
        if not fr or max(x["zf"] for x in fr) <= 0: print(t, "no zoom"); continue
        base, end = fr[0]["fov"], min(x["fov"] for x in fr)
        pts = [(x["zf"], (x["fov"] - base) / (end - base)) for x in fr if 0 < x["zf"] < 1 and end != base]
        best = None
        for i in range(0, 60, 2):
            for j in range(i + 10, 101, 2):
                A, B = i / 100, j / 100
                e = sum((y - sst(cl((z - A) / (B - A)))) ** 2 for z, y in pts)
                if best is None or e < best[0]: best = (e, A, B)
        up = [(x, y) for x, y in zip(fr, fr[1:]) if 0.02 < y["zf"] < 0.98 and y["zf"] > x["zf"]]
        dn = [(x, y) for x, y in zip(fr, fr[1:]) if 0.02 < y["zf"] < 0.98 and y["zf"] < x["zf"]]
        rate = lambda L: sum(y["ct"] - x["ct"] for x, y in L) / sum(abs(y["zf"] - x["zf"]) for x, y in L) if L else float("nan")
        rms = math.sqrt(best[0] / len(pts)) if pts else 0
        print(f"{t}\tbase={base:.1f}\tend={end:.2f}\twindow={best[1]:.2f}..{best[2]:.2f}\trms={rms:.3f}\tt_in={rate(up):.3f}\tt_out={rate(dn):.3f}")
    print("## laser: hip spread min..max from the client")
    for t in M:
        if not t.startswith("ls_"): continue
        v = [float(x) for x in re.findall(r"\] g t=\S+ zf=\S+ fov=\S+ sp=(\S+)", open(os.path.join(runs, t + ".txt"), encoding="utf-8").read())]
        print(t, f"min={min(v):.3f} max={max(v):.3f}")


if __name__ == "__main__":
    main()
