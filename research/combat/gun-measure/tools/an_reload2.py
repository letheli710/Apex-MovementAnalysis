#!/usr/bin/env python3
"""Reload against the field: per run the weapon states with their lengths, the animation sequences with cycle start and end and the rate they imply, ammo rise and when the gun is ready, all from the reload key or the auto reload.
  py -3 -I an_reload2.py <session dir> <prefix filter> ..."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut


def main():
    d = sys.argv[1]; pre = tuple(sys.argv[2:])
    F, S, M = load(d)
    for t in M:
        if not t.startswith(pre): continue
        fr = cut(F, M[t][0][0], M[t][-1][0] + 0.2)
        sh = cut(S, M[t][0][0], M[t][-1][0] + 0.2)
        key = next((x for x, m in M[t] if m == "+reload"), None)
        t0 = key if key else (sh[-1]["t"] if sh else fr[0]["t"])
        fr = [r for r in fr if r["t"] >= t0 - 0.02]
        st, sq = [], []
        for r in fr:
            if not st or st[-1][0] != r["ws"]: st.append([r["ws"], r["t"], r["t"]])
            st[-1][2] = r["t"]
            if not sq or sq[-1][0] != r["seq"]: sq.append([r["seq"], r["t"], r["t"], r["cyc"], r["cyc"]])
            sq[-1][2] = r["t"]; sq[-1][4] = r["cyc"]
        rises = [(y["t"] - t0, y["clip"] - x["clip"]) for x, y in zip(fr, fr[1:]) if y["clip"] > x["clip"]]
        nx = [(r["next"] - r["ct"]) for r in fr[:3]]
        print(t, "states", " ".join(f"{int(a)}:{c - b:.2f}" for a, b, c in st[:6]), "| rises", " ".join(f"{a:.2f}+{int(b)}" for a, b in rises[:7]), "| seq", " ".join(f"{int(a)}:{c - b:.2f}[{e:.2f}-{f:.2f}]" + (f"={(c - b) / (f - e):.2f}s" if f > e else "") for a, b, c, e, f in sq[:5]), "| next", f"{nx[0]:.2f}" if nx else "")


if __name__ == "__main__":
    main()
