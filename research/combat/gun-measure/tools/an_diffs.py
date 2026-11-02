#!/usr/bin/env python3
"""Every var a mod changed on the client, per gun. py -3 -I an_diffs.py <out.tsv> <session dir> ..."""
import json, os, sys
SKIP = ("fx_", "sound", "effect", "_1p", "_3p", "ui", "hud", "menu", "mesh", "icon", "model", "anim", "rui", "printname", "description", "skin", "tracer")
def session(d):
    wall = int(open(os.path.join(d, "wall.txt")).read()) / 1000
    dumps = []
    for l in open(os.path.join(d, "vars.jsonl"), encoding="utf-8"):
        try: j = json.loads(l); dumps.append((j["t"] + wall, j["v"]))
        except ValueError: pass
    rows = [l.split("\t") for l in open(os.path.join(d, "sweep.tsv"), encoding="utf-8")]
    out, base = [], {}
    for i, r in enumerate(rows):
        t, g, m = float(r[0]), r[1], r[2]
        tn = float(rows[i + 1][0]) if i + 1 < len(rows) else t + 1
        ds = [v for tt, v in dumps if t < tt <= tn + 0.05]
        if not ds: continue
        if m == "none": base[g] = ds[-1]; continue
        if g in base:
            b = base[g]; v = ds[-1]
            ch = {k: (b.get(k), v[k]) for k in v if v[k] != b.get(k)}
            out.append((g, m, ch))
    return out
def main():
    res = []
    for d in sys.argv[2:]: res += session(d)
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        f.write("gun\tmod\tn_changed\tchanges (visuals and sounds left out)\n")
        for g, m, ch in res:
            keep = {k: x for k, x in ch.items() if not any(s in k for s in SKIP)}
            f.write(f"{g}\t{m}\t{len(ch)}\t" + "; ".join(f"{k}:{x[0]}->{x[1]}" for k, x in sorted(keep.items())) + "\n")
main()
