"""D-74 B: per-traversal summary of the Frida probe (frida_d72_trav.js) — states, rates, the duck-complete frame.

One row per traversal (a run of TraversalMove calls; a new one starts when +0x2b34 enters as 0, i.e. after Traversal_PickAnim):
  start / end game time, duration (frames x frametime), the state sequence with frames per state ("4x12 8x31"), the fraction rate per state
  (d fraction / d t, median), the duck state on entry, the game time of the duck press (duck 0 -> non-0) and of the duck completing
  (-> 2) taken from the PlayerMove rows, both relative to the traversal start, the origin z at the start, the fraction when the state switched.
Trials come from the session's runner.json: a traversal belongs to the last trial whose jump (HSD-SCHED edge=down key=jump, game time t =
the probe's curtime) is before its start; jump_t / duck_cmd_t = the jump and the duck command relative to the traversal start.

Usage: frida_d72_summary.py <trav.csv> <runner.json> <height> <out.csv>
"""
import csv
import json
import re
import statistics as st
import sys


def trials(runner):
    out = []
    for t in json.load(open(runner, encoding="utf-8"))["trials"]:
        ev = {}
        for ln in t["sched_lines"]:
            m = re.search(r"edge=down key=(\w+) .* t=([\d.]+)", ln)
            if m and m.group(1) not in ev:
                ev[m.group(1)] = float(m.group(2))
        out.append(dict(run=t["run"], schedule=t["schedule"], warmup=t.get("warmup", False), ok=t["ok"], jump=ev.get("jump"), duck=ev.get("duck")))
    return [t for t in out if t["jump"] is not None]


def main():
    path, runner, height, out = sys.argv[1:5]
    tl = trials(runner)
    T, P = [], []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r.get("z") is None or r["ev"] not in ("T", "P"):
            continue                               # a line cut by the flush, or a start row (ev S)
        (T if r["ev"] == "T" else P).append(r)
    # client prediction re-runs replay a command (same curtime) after a server correction: keep the last run of every command
    T = list({round(float(r["cur"]), 4): r for r in T}.values())
    P = list({round(float(r["cur"]), 4): r for r in P}.values())
    T.sort(key=lambda r: float(r["cur"]))
    P.sort(key=lambda r: float(r["cur"]))
    # duck transitions from the PlayerMove rows (one per command)
    duck_ev = []                                   # (cur, from, to)
    prev = None
    for r in P:
        d = int(r["duck"])
        if prev is not None and d != prev:
            duck_ev.append((float(r["cur"]), prev, d))
        prev = d
    travs, cur = [], None
    for r in T:
        if r["arg2"] == "1" or int(r["s0"]) == 0 and (cur is None or float(r["fr0"]) < cur[-1]["fr1f"] - 0.2):
            cur = []
            travs.append(cur)
        if cur is None:
            continue
        r["fr0f"], r["fr1f"] = float(r["fr0"]), float(r["fr1"])
        cur.append(r)
    rows = []
    for i, tr in enumerate(travs):
        t0, t1 = float(tr[0]["cur"]), float(tr[-1]["cur"])
        ft = float(tr[0]["ft"])
        seq, rates = [], {}
        for r in tr:
            s = int(r["s1"])
            if seq and seq[-1][0] == s:
                seq[-1][1] += 1
            else:
                seq.append([s, 1])
            dfr = r["fr1f"] - r["fr0f"]
            if r["arg2"] != "1" and int(r["s0"]) == s and 0 < r["fr1f"] < 1:
                rates.setdefault(s, []).append(dfr / float(r["ft"]))
        sw = next((r for r in tr if int(r["s1"]) >= 7 and int(r["s1"]) <= 10), None)
        before = [e for e in duck_ev if e[0] <= t1 + 1e-6 and e[0] >= t0 - 1.5]
        press = [e[0] - t0 for e in before if e[1] == 0]
        full = [e[0] - t0 for e in before if e[2] == 2]
        tr_ = [t for t in tl if t["jump"] <= t0]
        tri = tr_[-1] if tr_ else {}
        eyes = [float(r["eye"]) for r in tr if r.get("eye") not in (None, "")]
        rows.append(dict(
            idx=i, run=tri.get("run", ""), trial=tri.get("schedule", ""), warmup=int(tri.get("warmup", False)), height=height,
            jump_t=round(tri["jump"] - t0, 4) if tri else "", duck_cmd_t=round(tri["duck"] - t0, 4) if tri.get("duck") else "",
            eye0=eyes[0] if eyes else "", eye_end=eyes[-1] if eyes else "", start=round(t0, 4), frames=len(tr), dur=round(len(tr) * ft, 4),
            seq=" ".join("%dx%d" % (s, n) for s, n in seq),
            rates=" ".join("%d:%.3f" % (s, st.median(v)) for s, v in sorted(rates.items())),
            duck_in=tr[0]["duck"], duck_press=round(press[-1], 4) if press else "", duck_full=round(full[-1], 4) if full else "",
            switch_t=round(float(sw["cur"]) - t0, 4) if sw else "", switch_fr=round(sw["fr0f"], 4) if sw else "",
            f_start=tr[0]["fr0"], z0=tr[0]["z"], p2b60=tr[0]["p2b60"], p2bb4=tr[0]["p2bb4"], type=tr[0]["type"]))
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(travs), "traversals,", len(tl), "trials ->", out)


if __name__ == "__main__":
    main()
