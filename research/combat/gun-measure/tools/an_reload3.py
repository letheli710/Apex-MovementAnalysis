#!/usr/bin/env python3
"""C summary. Reload length from the weapon state (11), first ammo rise, the moment the script flag ends, against the fields. Fire points inside the reload. ADS pressed in the reload.
  py -3 -I an_reload3.py <session dir> <runs dir> <out prefix>"""
import csv, os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut
from an_motion import G


def main():
    d, runs, pre = sys.argv[1:4]
    F, S, M = load(d)
    V = {r["gun"]: r for r in csv.DictReader(open(os.path.join(os.path.dirname(pre), "GUN-VARS.tsv")), delimiter="\t")}
    rows = defaultdict(list)
    for t in M:
        g = re.match(r"rt_([\w+]+?)_(tac|emp)_(\d)$", t)
        if not g: continue
        fr = cut(F, M[t][0][0], M[t][-1][0] + 0.2)
        rel = [r for r in fr if int(r["ws"]) == 11]
        if not rel: rows[g[1], g[2]].append(None); continue
        t0, t1 = rel[0]["ct"], rel[-1]["ct"]
        # state 11 may be broken by nothing here; rises are on the clip, only those from t0 on
        ri = [(y["ct"] - t0, y["clip"] - x["clip"]) for x, y in zip(fr, fr[1:]) if y["clip"] > x["clip"] and y["ct"] >= t0]
        # a client correction can repeat the same rise: drop one within 0.15 s
        rr = []
        for a, b in ri:
            if rr and a - rr[-1][0] < 0.15: continue
            rr.append((a, b))
        cl = G(runs, t)
        on = next((x["t"] for x in cl if x["rel"]), None)
        off = next((x["t"] for i, x in enumerate(cl) if i and cl[i - 1]["rel"] and not x["rel"]), None)
        # D-118: off is on the script log's clock, t0 on the Frida log's, so the flag column reads up to 0.13 s early. Kept to reproduce the table; use reload-motion/RM-SUMMARY.tsv's unlock.
        cyc = [r for r in rel]
        rows[g[1], g[2]].append(dict(state=t1 - t0, rise=rr[0][0] if rr else float("nan"), n=len(rr), amount=sum(b for _, b in rr), flag=(off - t0) if off else float("nan"), low=min(r["clip"] for r in fr), end=fr[-1]["clip"], seqs=len({r["seq"] for r in rel})))
    out = []
    for (g, k), v in rows.items():
        base = g.split("+")[0]; fv = V.get(base, {})
        ok = [x for x in v if x]
        r = dict(gun=g, kind=k, runs=len(v), ok=len(ok), field=fv.get("reload_time" if k == "tac" else "reloadempty_time", ""))
        if ok:
            for key in ("state", "rise", "flag"):
                w = [x[key] for x in ok if x[key] == x[key]]
                r[key] = round(st.mean(w), 3) if w else ""
            r["shells"] = ok[0]["n"]; r["amount"] = int(ok[0]["amount"]); r["seqs"] = ok[0]["seqs"]; r["clip_low"] = int(ok[0]["low"]); r["clip_end"] = int(ok[0]["end"])
            if r["state"] and r["rise"]: r["rise_frac"] = round(r["rise"] / r["state"], 3)
        out.append(r)
    keys = ["gun", "kind", "runs", "ok", "field", "state", "rise", "rise_frac", "flag", "shells", "amount", "seqs", "clip_low", "clip_end"]
    with open(pre + "-RELOAD-SUMMARY.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in out: f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    print("## fire inside the reload")
    for t in M:
        g = re.match(r"rf_(\w+?)_([\d.]+)$", t)
        if not g: continue
        at = next((x for x, m in M[t] if m == "+attack"), None); rk = next((x for x, m in M[t] if m == "+reload"), None)
        sh = cut(S, at - 0.02, M[t][-1][0] + 0.2)
        print(t, f"key_at={at - rk:.2f}", f"first_kick_at={sh[0]['t'] - rk:.2f}" if sh else "no kick", "kicks", len(sh), "ws at key", int(cut(F, at - 0.02, at + 0.02)[0]["ws"]) if cut(F, at - 0.02, at + 0.02) else "")
    print("## ADS pressed in the reload")
    for t in M:
        if not t.startswith("ra2_"): continue
        fr = cut(F, M[t][0][0], M[t][-1][0] + 0.2)
        rel = [r for r in fr if int(r["ws"]) == 11]
        z = next((r for r in fr if r["zf"] > 0.01), None)
        print(t, "reload", f"{rel[0]['t']:.2f}-{rel[-1]['t']:.2f}", "first zoom", f"{z['t']:.2f}" if z else "none", "max zf during", max((r["zf"] for r in rel), default=0))


if __name__ == "__main__":
    main()
