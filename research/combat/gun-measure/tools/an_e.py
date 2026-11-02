#!/usr/bin/env python3
"""Follow-ups: flinch with damage confirmed; P2020 ADS slope after taking off the no-shot drift by time since +zoom; table end past the clip.
  py -3 -I an_e.py <session dir> <out prefix>"""
import os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut


def main():
    d, pre = sys.argv[1:3]
    F, S, M = load(d)
    print("## flinch: peak change in 1.2 s after the damage, against the 0.2 s before; drift shows as the same value in every ADS run")
    G = defaultdict(list)
    for t in M:
        g = re.match(r"fl2_(none|self)_(hip|ads)_\d$", t)
        if not g: continue
        c = next(x for x, m in M[t] if m == "sv td")
        fr = cut(F, c - 0.2, c + 1.2)
        b = [r for r in fr if r["t"] < c]; a = [r for r in fr if r["t"] >= c]
        pk = lambda k: max((abs(r[k] - st.mean(x[k] for x in b)) for r in a), default=0)
        G[g[1], g[2]].append({k: pk(k) for k in ("fP", "fY", "fR", "puP", "puY", "s2P", "s2Y", "vmF", "vmU", "fov")})
    for k, v in sorted(G.items()):
        print(k, {x: round(st.mean(r[x] for r in v), 3) for x in v[0]})

    print("## P2020 ADS: puP from the no-shot runs by time since +zoom, taken off the shot runs")
    def series(t):
        z = next(x for x, m in M[t] if m == "+zoom")
        return z, cut(F, z, M[t][-1][0])
    base = defaultdict(list)
    for t in M:
        if t.startswith("fxn_"):
            z, fr = series(t)
            for r in fr: base[round((r["t"] - z) / 0.01)].append(r["puP"])
    base = {k: st.mean(v) for k, v in base.items()}
    if base:
        print("no-shot drift over the ADS hold: min", round(min(base.values()), 3), "max", round(max(base.values()), 3))
    res = []
    for t in M:
        if not t.startswith("fx_"): continue
        z, fr = series(t)
        sh = cut(S, z, M[t][-1][0])
        if not sh: continue
        w = [r for r in fr if sh[0]["t"] <= r["t"] <= sh[0]["t"] + 0.6 and r["zf"] >= 0.999]
        Y = [r["puP"] - base.get(round((r["t"] - z) / 0.01), 0) for r in w]; X = [r["s2P"] for r in w]
        if len(X) < 10: continue
        mx, my = st.mean(X), st.mean(Y)
        res.append(sum((x - mx) * (y - my) for x, y in zip(X, Y)) / sum((x - mx) ** 2 for x in X))
    print("slope after drift removed:", [round(x, 3) for x in res], "mean", round(st.mean(res), 3) if res else "")

    print("## table end past the clip")
    with open(pre + "-TABLE-END2.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("tag\tn\tidx\trow\tval\tc0\tc1\n")
        for t in M:
            if not t.startswith("lp2_"): continue
            sh = cut(S, M[t][0][0], M[t][-1][0] + 0.2)
            for i, s in enumerate(sh):
                f.write(f"{t}\t{i + 1}\t{int(s['idx'])}\t{int(s['row'])}\t{s['val']:.0f}\t{s['c0']}\t{s['c1']}\n")
            print(t, "shots", len(sh), "max idx", max(int(s["idx"]) for s in sh), "max row", max(int(s["row"]) for s in sh), "last rows", [int(s["row"]) for s in sh[-5:]], "last val", [round(s["val"]) for s in sh[-5:]], "last c1", sh[-1]["c1"])


if __name__ == "__main__":
    main()
