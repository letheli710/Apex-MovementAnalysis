#!/usr/bin/env python3
"""Sprint and slide to fire: was the player sprinting when the key went down, and how long to the first kick. Also holster and deploy lengths from the weapon state.
  py -3 -I an_raise.py <session dir> <out prefix>"""
import math, os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut


def main():
    d, pre = sys.argv[1:3]
    F, S, M = load(d)
    with open(pre + "-RAISE2.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("tag\tspeed_at_key\tspeed_first_kick\tlatency\tws_at_key\tvmU_at_key\tvmaP_at_key\n")
        for t in M:
            g = re.match(r"ra_(\w+?)_(sprint|slide|stand)_(\d)$", t)
            if not g: continue
            at = next((x for x, m in M[t] if m == "+attack"), None)
            sh = cut(S, M[t][0][0], M[t][-1][0] + 0.2)
            fr = cut(F, at - 0.03, at + 0.03) if at else []
            if not fr or not sh: continue
            r = fr[0]
            f.write(f"{t}\t{math.hypot(r['vx'], r['vy']):.0f}\t{math.hypot(sh[0]['vx'], sh[0]['vy']):.0f}\t{sh[0]['t'] - at:.3f}\t{int(r['ws'])}\t{r['vmU']:.2f}\t{r['vmaP']:.2f}\n")
    D = defaultdict(lambda: defaultdict(list))
    for t in M:
        if not re.match(r"ws_\w+_(swap|cycle)$", t): continue
        fr = cut(F, M[t][0][0], M[t][-1][0] + 0.2)
        run = []
        for r in fr:
            if not run or run[-1][0] != r["ws"] or run[-1][3] != r["w"]: run.append([r["ws"], r["ct"], r["ct"], r["w"]])
            run[-1][2] = r["ct"]
        for s, a, b, w in run[1:-1]:
            if s in (1, 2): D[t][int(s)].append(round(b - a, 3))
    with open(pre + "-SWITCH-STATES.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("tag\tstate2_lengths\tstate1_lengths\n")
        for t, v in D.items():
            f.write(f"{t}\t{','.join(map(str, v[2]))}\t{','.join(map(str, v[1]))}\n")


if __name__ == "__main__":
    main()
