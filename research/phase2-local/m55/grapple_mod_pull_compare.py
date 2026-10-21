#!/usr/bin/env python3
"""M5.5: does the range-doubling dev mod (infinite_abilities_grapple, added by DevAbilities_RefillWeapon) change the grapple
pull? Compares the dedi trajectory of m55_nomod_hold (mod removed) with the M4 m4_grapple_hold trials (mod present), aligned
on the tactical press: speed and position at fixed offsets, and the release command.

  py -3 grapple_mod_pull_compare.py <M4_pathfinder session> <M55_grapple_nomod session>
"""
import csv
import json
import math
import os
import sys

TAC = 1 << 21


def traces(sdir, schedule):
    runner = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
    runs = {"r%d" % t["run"] for t in runner["trials"] if t["ok"] and not t["warmup"] and t["schedule"] == schedule}
    rows = {}
    with open(os.path.join(sdir, "report", "rows.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["source"] == "MT" and r["side"] == "sv" and r["drv_run"] in runs:
                rows.setdefault(r["drv_run"], []).append(r)
    out = {}
    for run, rs in rows.items():
        rs.sort(key=lambda r: int(r["cmd"]))
        p = next(i for i, r in enumerate(rs) if int(r["buttons"]) & TAC)
        out[run] = [(float(r["pox"]), float(r["poz"]), math.hypot(float(r["pvx"]), float(r["pvy"]), float(r["pvz"]))) for r in rs[p:]]
    return out


def main():
    a = traces(sys.argv[1], "m4_grapple_hold")
    b = traces(sys.argv[2], "m55_nomod_hold")
    print("with mod (M4):", sorted(a), " without mod:", sorted(b))
    for k in (40, 60, 80, 100, 120, 140):
        sa = [t[k][2] for t in a.values() if len(t) > k]
        sb = [t[k][2] for t in b.values() if len(t) > k]
        xa = [t[k][0] for t in a.values() if len(t) > k]
        xb = [t[k][0] for t in b.values() if len(t) > k]
        print(f"cmd +{k:3d}: |v| mod {min(sa):7.2f}..{max(sa):7.2f}  nomod {min(sb):7.2f}..{max(sb):7.2f}   "
              f"x mod {min(xa):9.2f}..{max(xa):9.2f}  nomod {min(xb):9.2f}..{max(xb):9.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
