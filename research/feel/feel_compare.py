"""F1 feel comparison: lay the Unity game body (and the replay motor) over R5 for every trial, metric by metric.

Usage: feel_compare.py <feel_out_dir>[,<feel_out_dir>...] <trials_dir> [<trials_dir> ...] [--json out.json] [--series out_series.json] [--export dir]
  <feel_out_dir>  FeelBatch output: <trial_id>/{replay,reference,fun}.csv
  <trials_dir>    folders of R5 trials (<name>/trial.json + samples.csv), e.g. research/phase2-local/m2/trials
Prints the per-metric verdict table; --json writes the full per-trial result, --series a downsampled time series per trial for the plots.
stdlib only.
"""
import json
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feel_metrics import (ABILITY_METRICS, ABILITY_ONLY, CLIMB_METRICS, TOL, event_offsets, hspeed, load_inputs, load_trace, metrics, path_error, verdict)  # noqa: E402

BODIES = ("replay", "reference", "fun")
ABILITY_ONLY_SET = set(ABILITY_ONLY)


def family(trial_id):
    """Group name of a trial id, e.g. M2_e1_sprint_r301 -> e1_sprint, M3_e3_right_k35_144fps_r410 -> e3_right_k35."""
    if trial_id.startswith("M1_"):
        return "m1_basic"
    s = trial_id.split("_", 1)[1] if "_" in trial_id else trial_id
    s = s.rsplit("_r", 1)[0] if "_r" in s else s
    for fps in ("_144fps", "_120fps", "_60fps"):
        s = s.replace(fps, "")
    return s


def ability_view(traces, inp):
    """F3: the M4 trials ran on a flat field in R5, with two things the game bodies' flat floor does not have. (1) The field ends: a lift
    eject with strafe carried R5 off the edge (z -133), so every trace is cut where R5 first drops 5 u below its start height. (2) R5 sets
    its ground flag while the body slides down the M3 test wall after a grapple, so a row counts as grounded only within 2 u of the
    start height (the field floor) on every trace."""
    r5 = traces["r5"]
    z0 = r5["z"][0]
    cut = next((i for i, z in enumerate(r5["z"]) if z < z0 - 5), len(r5["z"]))
    out = {}
    for k, tr in traces.items():
        c = {f: v[:cut] for f, v in tr.items()}
        c["grounded"] = [int(g and z <= z0 + 2) for g, z in zip(c["grounded"], c["z"])]
        out[k] = c
    return out, {f: v[:cut] for f, v in inp.items()}


def series(tr, step=6):
    idx = list(range(0, len(tr["t"]), step))
    if idx[-1] != len(tr["t"]) - 1:
        idx.append(len(tr["t"]) - 1)
    r = lambda v, d=2: round(v, d)
    return {"t": [r(tr["t"][i], 4) for i in idx], "hs": [r(hspeed(tr, i)) for i in idx], "z": [r(tr["z"][i]) for i in idx],
            "x": [r(tr["x"][i]) for i in idx], "y": [r(tr["y"][i]) for i in idx]}


def main():
    args = sys.argv[1:]
    out_json = out_series = None
    if "--json" in args:
        i = args.index("--json"); out_json = args[i + 1]; del args[i:i + 2]
    if "--series" in args:
        i = args.index("--series"); out_series = args[i + 1]; del args[i:i + 2]
    out_export = None
    if "--export" in args:
        i = args.index("--export"); out_export = args[i + 1]; del args[i:i + 2]
    feel_dirs, trial_dirs = args[0].split(","), args[1:]
    results, ser = [], {}
    for td in trial_dirs:
        for name in sorted(os.listdir(td)):
            d = os.path.join(td, name)
            if not os.path.isfile(os.path.join(d, "trial.json")) or name.endswith("_REJECTED"):
                continue
            man = json.load(open(os.path.join(d, "trial.json"), encoding="utf-8"))
            tid = man["trial_id"]
            ud = next((os.path.join(f, tid) for f in feel_dirs if os.path.isdir(os.path.join(f, tid))), None)
            if ud is None:
                continue
            inp = load_inputs(os.path.join(d, "samples.csv"))
            r5 = load_trace(os.path.join(d, "samples.csv"))
            traces = {"r5": r5}
            traces.update({b: load_trace(os.path.join(ud, b + ".csv")) for b in BODIES if os.path.isfile(os.path.join(ud, b + ".csv"))})
            climb = bool((man.get("world") or {}).get("wall"))
            ability = not climb and str(man.get("experiment", "")).startswith("M4_")   # F3: the M4 ability trials (scenarios.json)
            if ability:
                traces, inp = ability_view(traces, inp)
            ms = {k: metrics(v, inp) for k, v in traces.items()}
            fam = family(tid)
            if man.get("schedule") and man.get("session"):            # F2 climb trials: schedule @ wall height
                h = man["session"].rsplit("_h", 1)[-1]
                fam = f"{man['schedule']}@h{h}"
            res = {"trial": tid, "family": fam, "climb": climb, "kind": "climb" if climb else "ability" if ability else "flat",
                   "duration": r5["t"][-1], "metrics": ms, "verdict": {}, "path": {}, "events": {}}
            for b in BODIES:
                if b not in traces:
                    continue
                res["path"][b] = path_error(r5, traces[b])
                res["verdict"][b] = {}
                for k in scored(res):
                    v, w = verdict(k, ms["r5"][k], ms[b][k])
                    if v:
                        res["verdict"][b][k] = [v, w]
                res["events"][b] = {e: event_offsets(r5, traces[b], e) for e in ("TAKEOFF", "LAND", "SLIDE_START", "SLIDE_END")}
            results.append(res)
            # climb trials: every 14th command and no Fun line, so the climb series stays under the page's 8 MB file limit
            ser[tid] = {k: series(v, 14 if res["climb"] else 6) for k, v in traces.items() if not (res["climb"] and k == "fun")}
    # summary: per metric, how many trials agree / close / differ / count, per body
    print(f"{len(results)} trials")
    for b in ("replay", "reference"):
        print(f"\n== {b} vs R5")
        agg = defaultdict(lambda: defaultdict(int))
        for res in results:
            for k, (v, _) in res["verdict"].get(b, {}).items():
                agg[k][v] += 1
        for k in TOL:
            a = agg[k]
            if a:
                print(f"  {k:16s} agree {a['agree']:3d}  close {a['close']:3d}  differ {a['differ']:3d}  count {a['count']:3d}")
        pr = sorted(r["path"][b]["path_rms"] for r in results if b in r["path"])
        if pr:
            print(f"  path_rms median {pr[len(pr) // 2]:.2f} u, max {pr[-1]:.2f} u")
    if out_json:
        json.dump(results, open(out_json, "w", encoding="utf-8"), indent=1)
    if out_series:
        json.dump(ser, open(out_series, "w", encoding="utf-8"), separators=(",", ":"))
    if out_export:
        export(results, ser, out_export)


def scored(res):
    return CLIMB_METRICS if res["kind"] == "climb" else ABILITY_METRICS if res["kind"] == "ability" else tuple(k for k in TOL if k not in ABILITY_ONLY_SET)


RANK = {"agree": 0, "close": 1, "differ": 2, "count": 3}
VZH = {"agree": "一致", "close": "接近", "differ": "不一致", "count": "次数不同", None: None}


def export(results, ser, out_dir):
    """Row tables for the overlay page: scorecard.json (one row per metric occurrence), trials.json (one row per trial),
    series.json / series_climb.json (one row per plotted point; flat and climb trials)."""
    from feel_metrics import NAME_ZH, UNIT
    os.makedirs(out_dir, exist_ok=True)
    score, trials, points = [], [], []
    for res in results:
        ms = res["metrics"]
        for k in scored(res):
            n = max(len(ms[b][k]) for b in ms)
            for i in range(n):
                g = lambda b: round(ms[b][k][i], 4) if b in ms and i < len(ms[b][k]) else None
                row = {"id": f"{res['trial']}/{k}/{i + 1}", "trial": res["trial"], "family": res["family"], "climb": res["climb"], "kind": res["kind"], "metric": k, "metric_zh": NAME_ZH[k], "unit": UNIT[k], "k": i + 1,
                       "r5": g("r5"), "replay": g("replay"), "reference": g("reference"), "fun": g("fun")}
                for b in ("replay", "reference"):
                    row["verdict_" + b] = res["verdict"].get(b, {}).get(k, [None])[0]
                    row["verdict_" + b + "_zh"] = VZH[row["verdict_" + b]]
                    row["delta_" + b] = None if row[b] is None or row["r5"] is None else round(row[b] - row["r5"], 4)
                score.append(row)
        worst = {b: max((v for v, _ in res["verdict"][b].values()), key=RANK.get, default="agree") if b in res["verdict"] else None for b in BODIES}
        trials.append({"trial": res["trial"], "family": res["family"], "climb": res["climb"], "kind": res["kind"], "duration": round(res["duration"], 3),
                       "verdict_reference": worst["reference"], "verdict_replay": worst["replay"], "verdict_fun": worst["fun"],
                       "verdict_reference_zh": VZH[worst["reference"]], "verdict_replay_zh": VZH[worst["replay"]],
                       "path_rms_reference": round(res["path"]["reference"]["path_rms"], 2),
                       "path_rms_replay": round(res["path"]["replay"]["path_rms"], 2) if "replay" in res["path"] else None,
                       "path_rms_fun": round(res["path"]["fun"]["path_rms"], 2),
                       "jumps_r5": len(ms["r5"]["takeoff_speed"]), "jumps_reference": len(ms["reference"]["takeoff_speed"])})
        for body, s in ser[res["trial"]].items():
            for j in range(len(s["t"])):
                points.append({"trial": res["trial"], "body": body, "t": s["t"][j], "hs": s["hs"][j], "z": s["z"][j], "x": s["x"][j], "y": s["y"][j]})
    climb = {r["trial"] for r in results if r["climb"]}
    flat_pts = [p for p in points if p["trial"] not in climb]
    climb_pts = [p for p in points if p["trial"] in climb]
    for name, rows in (("scorecard", score), ("trials", trials), ("series", flat_pts), ("series_climb", climb_pts)):
        json.dump(rows, open(os.path.join(out_dir, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"{name}.json: {len(rows)} rows")


if __name__ == "__main__":
    main()
