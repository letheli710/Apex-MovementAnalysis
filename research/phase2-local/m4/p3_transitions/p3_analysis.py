#!/usr/bin/env python3
"""M4 P3 (transitions only): Wraith Into the Void and Loba translocation, from the dedi MOVE-TRACE.

Wraith: the movescale (msc) timeline after the tactical press (deploy slow, boost plateau, fade) and the sprint speed it gives.
Loba: the teleport command (origin jump > 200 u in one command), velocity just before and after it, and how long until the
held forward input accelerates the player again (control lock).

  py -3 p3_analysis.py --wraith <session> [<session> ...] --loba <session> [<session> ...] [--json results.json]
"""
import csv
import json
import math
import os
import statistics as st
import sys

TAC = 1 << 21


def load(sdir):
    runner = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
    sched = {"r%d" % t["run"]: t["schedule"] for t in runner["trials"] if t["ok"] and not t["warmup"]}
    rows = {}
    with open(os.path.join(sdir, "report", "rows.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["source"] == "MT" and r["side"] == "sv" and r["drv_run"] in sched:
                rows.setdefault(r["drv_run"], []).append(r)
    for v in rows.values():
        v.sort(key=lambda r: int(r["cmd"]))
    return sched, rows


def f(r, k):
    return float(r[k])


def wraith(sdirs):
    sched, rows = {}, {}
    for sdir in sdirs:
        a, b = load(sdir)
        sched.update(a)
        rows.update(b)
    out = []
    for run in sorted(rows):
        rs = rows[run]
        name = sched[run]
        press = next((i for i, r in enumerate(rs) if int(r["buttons"]) & TAC), None)
        msc = [f(r, "movescale") for r in rs]
        spd = [math.hypot(f(r, "pvx"), f(r, "pvy")) for r in rs]
        row = {"run": run, "schedule": name, "sprint_cap": round(max(spd), 2)}
        if press is not None:
            post = msc[press:]
            lo = min(post[:200])
            hi = max(post)
            i_hi = next(i for i, m in enumerate(post) if abs(m - hi) < 1e-4)
            i_hi_end = max(i for i, m in enumerate(post) if abs(m - hi) < 1e-4)
            i_back = next((i for i in range(i_hi_end, len(post)) if post[i] <= 1.15 + 1e-3), None)
            row.update({"press_cmd": int(rs[press]["cmd"]), "deploy_msc_min": lo,
                        "deploy_slow_cmds": i_hi, "boost_msc": hi, "boost_ratio": round(hi / 1.15, 4),
                        "plateau_cmds": i_hi_end - i_hi + 1, "fade_cmds": (i_back - i_hi_end) if i_back else None,
                        "boost_speed": round(max(spd[press:]), 2),
                        "speed_over_msc": round(max(spd[press:]) / hi, 2)})
        out.append(row)
        print("wraith", " ".join(f"{k}={v}" for k, v in row.items()))
    return out


def loba(sdirs):
    sched, rows = {}, {}
    for sdir in sdirs:
        a, b = load(sdir)
        sched.update(a)
        rows.update(b)
    out = []
    for run in sorted(rows):
        rs = rows[run]
        name = sched[run]
        tele = None
        for i in range(1, len(rs)):
            d = math.dist([f(rs[i - 1], k) for k in ("pox", "poy", "poz")], [f(rs[i], k) for k in ("pox", "poy", "poz")])
            if d > 200:
                tele = i
                break
        row = {"run": run, "schedule": name, "teleported": tele is not None}
        if tele is not None:
            b, a = rs[tele - 1], rs[tele]
            row.update({"tele_cmd": int(a["cmd"]), "jump_u": round(math.dist([f(b, k) for k in ("pox", "poy", "poz")],
                                                                                [f(a, k) for k in ("pox", "poy", "poz")]), 1),
                        "v_before": round(math.hypot(f(b, "pvx"), f(b, "pvy"), f(b, "pvz")), 2),
                        "v_after": round(math.hypot(f(a, "pvx"), f(a, "pvy"), f(a, "pvz")), 2)})
            # first command after the teleport at which speed rises again (forward held in m4_loba_tele)
            sp = [math.hypot(f(r, "pvx"), f(r, "pvy")) for r in rs[tele:]]
            row["cmds_until_accel"] = next((i for i in range(1, len(sp)) if sp[i] > sp[i - 1] + 0.5), None)
            row["fwd_after"] = a["fwd"]
        out.append(row)
        print("loba", " ".join(f"{k}={v}" for k, v in row.items()))
    return out


def main():
    args = sys.argv[1:]
    if "--json" in args:
        i = args.index("--json")
        args = args[:i] + args[i + 2:]
    w = wraith(args[args.index("--wraith") + 1:args.index("--loba")])
    l = loba(args[args.index("--loba") + 1:])
    void = [r for r in w if r["schedule"] == "m4_wraith_void"]
    if void:
        for k in ("deploy_msc_min", "deploy_slow_cmds", "boost_msc", "plateau_cmds", "fade_cmds", "boost_speed"):
            vals = [r[k] for r in void if r.get(k) is not None]
            print(f"wraith_void {k}: mean {st.mean(vals):.4f} min {min(vals)} max {max(vals)} n {len(vals)}")
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"wraith": w, "loba": l}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
