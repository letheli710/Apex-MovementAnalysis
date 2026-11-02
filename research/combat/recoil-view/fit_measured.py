#!/usr/bin/env python3
"""Fit delay D + time constant T of a first-order return to the measured pitch punch after the last kick, per weapon/mode; yaw too.
  py -3 -I fit_measured.py <dir>"""
import math, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A


def fit(pts):
    best = None
    for Di in range(0, 61):
        D = Di * 0.01
        for Ti in range(2, 121):
            T = Ti * 0.01
            e = sum((y - (1.0 if t < D else math.exp(-(t - D) / T))) ** 2 for t, y in pts)
            if best is None or e < best[0]: best = (e, D, T)
    return best[1], best[2], math.sqrt(best[0] / len(pts))


def main():
    F, S, M = A.load(sys.argv[1])
    print("group\tcases\tD\tT\trms\tt50_from_peak\tt10_from_peak\tkick_to_peak\tyaw_T50")
    for w in ("r301", "spit", "wing", "p20"):
        for mode in ("hip", "ads"):
            pts, t50, t10, tp, y50 = [], [], [], [], []
            n = 0
            for tag in M:
                if not re.match(rf"{w}_{mode}_(b08|b15|tri)_\d", tag): continue
                fr, sh = A.case(F, S, M, tag)
                if not sh: continue
                tl = sh[-1]["t"]; aft = [r for r in fr if r["t"] >= tl]
                pk = max(aft, key=lambda r: abs(r["s2P"])); p = abs(pk["s2P"])
                if p < 0.3: continue
                rest = [r for r in aft if r["t"] >= pk["t"]]
                pts += [(r["t"] - pk["t"], abs(r["s2P"]) / p * (1 if r["s2P"] * pk["s2P"] >= 0 else -1)) for r in rest[::4] if r["t"] - pk["t"] < 3]
                t50.append(next(r["t"] - pk["t"] for r in rest if abs(r["s2P"]) <= p / 2)); t10.append(next(r["t"] - pk["t"] for r in rest if abs(r["s2P"]) <= p / 10))
                tp.append(pk["t"] - tl); n += 1
                ypk = max(aft, key=lambda r: abs(r["s2Y"])); py = abs(ypk["s2Y"])
                if py > 0.2: y50.append(next((r["t"] - ypk["t"] for r in aft if r["t"] >= ypk["t"] and abs(r["s2Y"]) <= py / 2), float("nan")))
            if not pts: print(w, mode, "none"); continue
            D, T, r = fit(pts)
            print(f"{w}_{mode}", n, f"{D:.2f}", f"{T:.2f}", f"{r:.3f}", f"{st.mean(t50):.3f}", f"{st.mean(t10):.3f}", f"{st.mean(tp):.3f}", f"{st.mean(y50) if y50 else float('nan'):.3f}", sep="\t")


if __name__ == "__main__":
    main()
