#!/usr/bin/env python3
"""Second pass: the turn lag per gun, checks on the runs, and whether guns group: distance between guns' sprint and other poses, and a simple clustering.
  py -3 -I an_hp2.py <runs dir> <out dir>"""
import csv, glob, math, os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_hp import load, key, window, _write


def main():
    runs, out = sys.argv[1:3]
    T = []
    for p in sorted(glob.glob(os.path.join(runs, "hp_*_turn_*.txt"))):
        gun = re.match(r"hp_(\w+?)_turn_", os.path.basename(p))[1]
        F, K = load(p)
        base = [r for r in F if r["t"] < (key(K, "+left") or 0)]
        if not base: continue
        b = {a: st.mean(r[a] for r in base) for a in ("mR", "mU", "gY", "gP")}
        row = dict(gun=gun)
        for name, down, up in (("left", "+left", "-left"), ("right", "+right", "-right")):
            d, u = key(K, down), key(K, up)
            if d is None or u is None: continue
            hold = [r for r in F if d + 0.4 <= r["t"] <= u]
            rate = abs((hold[-1]["t"] - hold[0]["t"]) and 0)
            row[name + "_dR"] = st.mean(r["mR"] for r in hold) - b["mR"]
            row[name + "_dY"] = st.mean(r["gY"] for r in hold) - b["gY"]
            pk = max(F, key=lambda r: abs(r["mR"] - b["mR"]) if d <= r["t"] <= u + 0.5 else 0)
            row[name + "_peak"] = pk["mR"] - b["mR"]; row[name + "_tpeak"] = pk["t"] - d
            aft = [r for r in F if r["t"] >= u]
            tot = st.mean(r["mR"] for r in hold) - b["mR"]
            row[name + "_back90"] = next((r["t"] - u for r in aft if abs(r["mR"] - b["mR"]) < 0.1 * abs(tot)), float("nan"))
        T.append(row)
    G = defaultdict(list)
    for r in T: G[r["gun"]].append(r)
    keys = [k for k in T[0] if k != "gun"]
    rows = [dict(gun=g, runs=len(v), **{k: st.mean(x[k] for x in v if k in x and x[k] == x[k]) for k in keys if any(k in x and x[k] == x[k] for x in v)}) for g, v in G.items()]
    _write(os.path.join(out, "HP-TURN.tsv"), rows, ["gun", "runs"] + keys)
    P = list(csv.DictReader(open(os.path.join(out, "HP-POSE.tsv")), delimiter="\t"))
    V = defaultdict(dict)
    for r in P:
        if r.get("dmF"): V[r["gun"]][r["state"]] = r
    FE = ("dmF", "dmR", "dmU", "dgP", "dgY", "dgR")
    print("guns", len(V), "states bad:", [(r["gun"], r["state"], r["good"]) for r in P if r["good"] != r["runs"]][:40])
    print("worst repeat:", sorted([(float(r["repeat"]), r["gun"], r["state"]) for r in P if r.get("repeat")], reverse=True)[:8])
    for state in ("sprint", "crouch", "slide", "walk"):
        vec = {g: [float(v[state][k]) for k in FE] for g, v in V.items() if state in v and all(v[state].get(k) for k in FE)}
        names = sorted(vec)
        # greedy: single-link clusters on the sprint vector with distance threshold in u + deg
        print("==", state)
        for g in sorted(vec, key=lambda g: vec[g][2]):
            print(f"  {g:12s}", " ".join(f"{x:7.2f}" for x in vec[g]))


if __name__ == "__main__":
    main()
