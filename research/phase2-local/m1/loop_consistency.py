#!/usr/bin/env python3
"""M1 acceptance: are the automated "reset -> forward -> stop -> jump -> land" trials consistent?

For every run label of every given session folder (made by hsd_session.py), the script
reads the client MOVE-TRACE usercmds (first-time predictions only) and finds:

  fwd_down   first usercmd with fwd > 0          (and its fwd value: kbutton half-press 0.5)
  fwd_up     first usercmd with fwd == 0 after fwd_down
  stop       first usercmd after fwd_up whose post-move 2D speed < 1 u/s
  jump       first usercmd after fwd_up with IN_JUMP (0x2) in the buttons
  takeoff    first usercmd after jump that ends airborne (ge=0)
  land       first usercmd after takeoff that is grounded again

and the integrity numbers the plan asks for: usercmd numbers without gaps, the share of
client usercmds that have a dedi twin (session/ent/batch/cmd join), HSD frames per usercmd,
the runner's measured frame rate and its edge frames. A trial is consistent with the others
when its event *sequence* is the same and its event spacings (in usercmds) agree within
--tol-cmds. Nothing is truncated or filled: a missing event is reported as missing.

  py -3 loop_consistency.py <session>... [-o out_dir]
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-prep", "tools"))
from hsdtel import derive, parse  # noqa: E402

IN_JUMP = 0x2
EVENTS = ["fwd_down", "fwd_up", "stop", "jump", "takeoff", "land"]


def spd2d_post(r):
    return math.hypot(r["pvx"], r["pvy"])


def first(rows, start, pred):
    for i in range(start, len(rows)):
        if pred(rows[i]):
            return i
    return None


def trial_events(rows):
    ev = {}
    i = first(rows, 0, lambda r: r["fwd"] > 0)
    ev["fwd_down"] = i
    if i is None:
        return ev
    j = first(rows, i, lambda r: r["fwd"] == 0)
    ev["fwd_up"] = j
    if j is None:
        return ev
    ev["stop"] = first(rows, j, lambda r: spd2d_post(r) < 1.0)
    k = first(rows, j, lambda r: int(r["buttons"]) & IN_JUMP)
    ev["jump"] = k
    if k is None:
        return ev
    t = first(rows, k, lambda r: r["ground"] == 0)
    ev["takeoff"] = t
    if t is not None:
        ev["land"] = first(rows, t, lambda r: r["ground"] == 1)
    return ev


def analyse_session(folder):
    logs = os.path.join(folder, "platform", "logs")
    files, rows, issues = parse.parse_inputs([logs])
    derive.derive(rows)
    runner = {}
    rpath = os.path.join(folder, "runner.json")
    if os.path.exists(rpath):
        with open(rpath, encoding="utf-8") as fh:
            for t in json.load(fh)["trials"]:
                runner[f"r{t['run']}"] = t
    by_run = {}
    for r in rows:
        # trial labels only: "r0" is between trials, "b<N>" marks unlabelled rows of a reset batch
        if (r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay")
                and str(r.get("drv_run", "")).startswith("r") and r["drv_run"] != "r0"):
            by_run.setdefault(r["drv_run"], []).append(r)
    hsd = {}
    for r in rows:
        if r["source"] == "HSD" and r.get("kind") == "frame" and r.get("side") == "cl":
            hsd[r.get("drv_run")] = hsd.get(r.get("drv_run"), 0) + 1
    out = []
    for run, rs in sorted(by_run.items(), key=lambda kv: int(kv[0][1:])):
        if runner.get(run, {}).get("warmup"):
            continue  # unscored warm-up trial (hsd_trial.py --warmup)
        rs.sort(key=lambda r: r["cmd"])
        cmds = [r["cmd"] for r in rs]
        gaps = sum(1 for a, b in zip(cmds, cmds[1:]) if b - a != 1)
        joined = sum(1 for r in rs if r.get("drv_join") == "ok")
        ev = trial_events(rs)
        rec = {"session": os.path.basename(folder), "run": run, "cmds": len(rs), "cmd_first": cmds[0],
               "cmd_gaps": gaps, "batches": len({r.get("drv_batch") for r in rs}),
               "join_ok": round(joined / len(rs), 4), "hsd_frames": hsd.get(run, 0),
               "msc": sorted({r["movescale"] for r in rs}), "maxspeed": sorted({r["maxspeed"] for r in rs})}
        for e in EVENTS:
            rec[e] = rs[ev[e]]["cmd"] if ev.get(e) is not None else None
        if ev.get("fwd_down") is not None:
            rec["fwd_first_value"] = rs[ev["fwd_down"]]["fwd"]
        seg = rs[ev["fwd_down"]:ev["fwd_up"]] if ev.get("fwd_up") is not None else []
        rec["peak_spd2d"] = round(max((spd2d_post(r) for r in seg), default=float("nan")), 3)
        # the label is set before the reset teleport, so measure from the first forward command
        if ev.get("fwd_down") is not None and ev.get("land") is not None:
            rec["dist_x"] = round(rs[ev["land"]]["pox"] - rs[ev["fwd_down"]]["ox"], 2)
        if ev.get("takeoff") is not None and ev.get("land") is not None:
            air = rs[ev["takeoff"]:ev["land"]]
            rec["apex_dz"] = round(max(r["poz"] for r in air) - rs[ev["jump"]]["oz"], 2)
            rec["takeoff_vz"] = round(rs[ev["takeoff"]]["pvz"], 3)
        t = runner.get(run)
        if t:
            rec["runner_fps"] = t.get("measured_fps")
            rec["runner_ok"] = t.get("ok")
        out.append(rec)
    return out


def spans(rec):
    keys = [e for e in EVENTS if rec.get(e) is not None]
    return {f"{a}->{b}": rec[b] - rec[a] for a, b in zip(keys, keys[1:])}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--tol-cmds", type=int, default=2, help="allowed spread of an event spacing, in usercmds")
    a = ap.parse_args(argv)
    recs = []
    for s in a.sessions:
        recs += analyse_session(s)
    if not recs:
        print("no labelled runs found"); return 2

    seqs = {r["run"]: tuple(e for e in EVENTS if r.get(e) is not None) for r in recs}
    all_spans = {r["run"]: spans(r) for r in recs}
    verdict = {"trials": len(recs), "full_sequence": all(s == tuple(EVENTS) for s in seqs.values()),
               "no_cmd_gaps": all(r["cmd_gaps"] == 0 for r in recs),
               "min_join": min(r["join_ok"] for r in recs),
               "runner_ok": all(r.get("runner_ok", False) for r in recs), "spans": {}}
    for k in sorted({k for s in all_spans.values() for k in s}):
        vals = [s[k] for s in all_spans.values() if k in s]
        verdict["spans"][k] = {"min": min(vals), "max": max(vals), "spread": max(vals) - min(vals),
                               "ok": max(vals) - min(vals) <= a.tol_cmds}
    for key in ("peak_spd2d", "dist_x", "apex_dz", "takeoff_vz"):
        vals = [r[key] for r in recs if isinstance(r.get(key), float) and not math.isnan(r[key])]
        if vals:
            verdict[key] = {"min": min(vals), "max": max(vals), "mean": round(statistics.fmean(vals), 3),
                            "rel_spread": round((max(vals) - min(vals)) / abs(statistics.fmean(vals)), 5) if statistics.fmean(vals) else None}
    verdict["consistent"] = (verdict["full_sequence"] and verdict["no_cmd_gaps"] and verdict["runner_ok"]
                             and verdict["min_join"] >= 0.9 and all(v["ok"] for v in verdict["spans"].values()))

    cols = ["session", "run", "cmds", "cmd_first", "cmd_gaps", "batches", "join_ok", "hsd_frames", "runner_fps", "runner_ok",
            "fwd_first_value"] + EVENTS + ["peak_spd2d", "dist_x", "apex_dz", "takeoff_vz", "msc", "maxspeed"]
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(cols)
    for r in recs:
        w.writerow([r.get(c, "") for c in cols])
    print(json.dumps(verdict, indent=1))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "trials.csv"), "w", newline="", encoding="utf-8") as fh:
            cw = csv.writer(fh, lineterminator="\n")
            cw.writerow(cols)
            for r in recs:
                cw.writerow([r.get(c, "") for c in cols])
        with open(os.path.join(a.out, "verdict.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(verdict, fh, indent=1)
    return 0 if verdict["consistent"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
