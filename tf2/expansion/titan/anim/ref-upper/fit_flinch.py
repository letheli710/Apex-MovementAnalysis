"""A12 small tier: additive flinch on top of the idle. Per trial: peak deviation of CHESTFOCUS / HAND_L / HAND_R
from their pre-hit mean, direction of the chest push (f, r), and how long the chest stays > 1 u away.
Usage: py -3 -I fit_flinch.py <run dir>"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_ref import parse, fl, a12  # noqa: E402

def run(rundir):
    d, tags, ev = parse(rundir)
    for r in a12(d, tags, ev):
        if not r["hits"] or "stand" not in r["name"]:
            continue
        th = r["hits"][0][0]
        pre = [f for t, f in d["RC"] if f[0] == "1" and len(f) >= 19 and th - 0.5 <= t < th]
        post = [(t - th, f) for t, f in r["rc"] if t >= th]
        out = [r["name"]]
        for name, i in (("CHEST", 16), ("HAND_L", 10), ("HAND_R", 13)):
            ref = [sum(fl(f[i + k]) for f in pre) / len(pre) for k in range(3)]
            dev = [(t, [fl(f[i + k]) - ref[k] for k in range(3)]) for t, f in post]
            pk = max(dev, key=lambda x: math.hypot(*x[1]))
            away = [t for t, v in dev if math.hypot(*v) > 1.0]
            out.append("%s peak %.1f u at %.2f s (f %.1f r %.1f u %.1f) >1u until %.2f s" % (
                name, math.hypot(*pk[1]), pk[0], pk[1][0], pk[1][1], pk[1][2], away[-1] if away else 0))
        print(" | ".join(out))

if __name__ == "__main__":
    run(sys.argv[1])
