#!/usr/bin/env python3
"""M5.5 grapple range check: does the grapple attach at 800 / 840 / 860 / 900 u (pitch 0, straight at the test wall face)?

Attach = the grapple hop: the first dedi command after the tactical press whose pre-command vz is 200 u/s (M4: the hop
sets vz to 200; the post value already carries a gravity step). The hook flight time (press -> hop) is compared with the M4 hook model t = 0.004 + L / 2035 u/s.

  py -3 grapple_range_check.py <M55_grapple_range session> [--json out.json]
"""
import csv
import json
import os
import sys

TAC = 1 << 21
DT = 1.0 / 120.0


def main():
    sdir = sys.argv[1]
    runner = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
    trials = {"r%d" % t["run"]: t for t in runner["trials"] if t["ok"] and not t["warmup"]}
    rows = {}
    with open(os.path.join(sdir, "report", "rows.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["source"] == "MT" and r["side"] == "sv" and r["drv_run"] in trials:
                rows.setdefault(r["drv_run"], []).append(r)
    out = []
    for run in sorted(rows):
        if "_d" not in trials[run]["schedule"]:
            continue
        rs = sorted(rows[run], key=lambda r: int(r["cmd"]))
        d = int(trials[run]["schedule"].rsplit("_d", 1)[1])
        press = next((i for i, r in enumerate(rs) if int(r["buttons"]) & TAC), None)
        hop = None
        if press is not None:
            hop = next((i for i in range(press, len(rs)) if abs(float(rs[i]["vz"]) - 200.0) < 0.5), None)
        moved = max(float(r["pox"]) for r in rs) - float(rs[0]["pox"])
        row = {"run": run, "distance_u": d, "attached": hop is not None, "max_dx_u": round(moved, 1)}
        if hop is not None:
            t = (hop - press) * DT
            row["flight_s"] = round(t, 4)
            row["model_flight_s"] = round(0.004 + d / 2035.0, 4)
        out.append(row)
        print(" ".join(f"{k}={v}" for k, v in row.items()))
    for d in sorted({r["distance_u"] for r in out}):
        g = [r for r in out if r["distance_u"] == d]
        print(f"d={d}: attached {sum(r['attached'] for r in g)}/{len(g)}")
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
