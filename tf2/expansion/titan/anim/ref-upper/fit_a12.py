"""A12: which full-body clip plays after a stagger hit. The client logs the main-sequence cycle every frame
(RC field 7) and CHESTFOCUS / HAND_L relative to the origin; for every candidate clip, take its own attachment
heights at the logged cycle (clip_attach.py) and compare (height only: model and log share the up axis).
Usage: py -3 -I fit_a12.py <run dir>"""
import csv
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_ref import parse, fl, a12, cycle_events  # noqa: E402
from clip_attach import clip_path  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "seqgraph_medium.csv")


def candidates():
    rows = []
    for r in csv.DictReader(open(OUT, encoding="utf-8")):
        if "STAGGER" in r["activity"] or "stagger" in r["modifiers"].split("+"):
            rows.append((r["seq"], r["activity"], r["modifiers"], float(r["dur"])))
    return rows


def run(rundir):
    d, tags, ev = parse(rundir)
    cands = candidates()
    paths = {}
    for seq, act, mods, dur in cands:
        try:
            paths[seq] = (clip_path(seq, "CHESTFOCUS"), clip_path(seq, "HAND_L"))
        except Exception as e:  # noqa: BLE001
            print("skip", seq, e)
    res = []
    for r in a12(d, tags, ev):
        th = [t for t, e in r["hits"]]
        if not th:
            continue
        run_ = next(((ta, tb) for ta, tb, rate, c0, c1 in cycle_events(r["rc"]) if ta >= th[0] - 0.08 and tb - ta > 0.5), None)
        if not run_:
            continue
        ta, tb = run_
        seg = [(fl(f[7]), fl(f[18]), fl(f[12])) for t, f in r["rc"] if ta + 0.25 <= t <= tb - 0.05]  # skip the 0.2 s fade-in
        scores = []
        for seq, act, mods, dur in cands:
            if seq not in paths:
                continue
            cp, hp = paths[seq]
            n = len(cp) - 1
            errs = []
            for c, chest_u, hand_u in seg:
                i = min(n, max(0, int(round(c * n))))
                errs.append((cp[i][3] - chest_u, hp[i][3] - hand_u))
            # allow a constant height offset (model origin vs entity origin)
            mc = sum(e[0] for e in errs) / len(errs)
            mh = sum(e[1] for e in errs) / len(errs)
            rms = math.sqrt(sum((e[0] - mc) ** 2 + (e[1] - mh) ** 2 for e in errs) / len(errs))
            scores.append((rms, seq, act, mods, dur, round(mc, 1)))
        scores.sort()
        res.append((r["name"], round(tb - ta, 3), scores[:4]))
    return res


if __name__ == "__main__":
    for name, L, sc in run(sys.argv[1]):
        print(name, "seq run %.3f s" % L)
        for s in sc:
            print("   rms %.2f  %s  %s  %s  %.3f s  offset %.1f" % s)
