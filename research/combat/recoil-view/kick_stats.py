#!/usr/bin/env python3
"""Aggregates over the batch: per-row pitch offset of the punch before each kick against the cumulative pattern table, return metrics per weapon/mode, rounds against the punch (runs/*_bul_*).
  py -3 -I kick_stats.py <dir> <runs dir>"""
import os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A


def main():
    d, runs = sys.argv[1], sys.argv[2]
    F, S, M = A.load(d)
    groups = {}
    for tag in M:
        g = re.match(r"(\w+?)_(hip|ads)_(\w+?)_\d+$", tag)
        if g: groups.setdefault((g[1], g[2], g[3]), []).append(tag)
    print("## return (s from last kick; mean of reps)\ngroup\tshots\tpeak\ttpk\tt50\tt10\tt01\tover\tzero\tview/s2\treplayRMS")
    for key, tags in sorted(groups.items()):
        ms = []
        for t in tags:
            fr, sh = A.case(F, S, M, t); m = A.return_metrics(fr, sh)
            if m: m["rms"] = A.replay(fr, sh, None)[0]; ms.append(m)
        if ms:
            av = lambda k: st.mean(m[k] for m in ms if m[k] == m[k]) if any(m[k] == m[k] for m in ms) else float("nan")
            print("_".join(key), *[f"{av(k):.3f}" for k in ("shots", "peak", "tpk", "t50", "t10", "t01", "over", "zero", "fracview", "rms")], sep="\t")
    print("## rows: mean s2P at each kick (before it) over longest bursts, against the cumulative table")
    for w, mode in (("r301", "hip"), ("r301", "ads"), ("spit", "hip"), ("spit", "ads")):
        rows = {}
        for t in groups.get((w, mode, "b15"), []):
            _, sh = A.case(F, S, M, t)
            for i, s in enumerate(sh):
                rows.setdefault(i, []).append((s["s2P0"], s["s2Y0"], s["c1"], s["c0"], s["val"], s["row"]))
        cum = cumy = 0
        print(w, mode, "i row table_cum s2P_mean s2P_sd s2Y_mean tableY_cum")
        for i in sorted(rows):
            r = rows[i]
            print(i, int(r[0][5]), f"{cum:.2f}", f"{st.mean(x[0] for x in r):.2f}", f"{st.pstdev(x[0] for x in r):.2f}", f"{st.mean(x[1] for x in r):.2f}", f"{cumy:.2f}", sep="\t")
            cum += r[0][2]; cumy += r[0][3]
    print("## gap tests: value and row of the shot after a gap")
    for tag in M:
        if "_gap" not in tag: continue
        _, sh = A.case(F, S, M, tag)
        if len(sh) < 2: print(tag, "shots", len(sh)); continue
        a, b = sh[-2], sh[-1]
        print(tag, f"prevval={a['val']:.2f} gap={b['ct'] - a['ct']:.3f} val={b['val']:.2f} row={int(b['row'])} shots={len(sh)}")
    print("## rounds: dummie at 150 u, height of each hit against the first, degrees; punch before that kick")
    for tag in M:
        if "_bul_" not in tag: continue
        p = os.path.join(runs, tag + ".txt")
        zs = []
        for l in open(p, encoding="utf-8"):
            g = re.search(r"\[RT\] dmg t=([\d.]+) amt=([\d.]+) hg=(\d+).*pos=([-\d.]+),([-\d.]+),([-\d.]+)", l)
            if g: zs.append((float(g[1]), float(g[5]), float(g[6]), int(g[3])))
        _, sh = A.case(F, S, M, tag)
        print(tag, "hits", len(zs), "kicks", len(sh))
        n = min(len(zs), len(sh))
        for i in range(n):
            dist = 150.0
            import math
            z = math.degrees(math.atan2(zs[i][2] - zs[0][2], dist)); y = math.degrees(math.atan2(zs[i][1] - zs[0][1], dist))
            s = sh[i]
            print(f"  {i} hitP={-z:+.2f} hitY={y:+.2f} s2P={s['s2P0']:+.2f} s2Y={s['s2Y0']:+.2f} hg={zs[i][3]}")


if __name__ == "__main__":
    main()
