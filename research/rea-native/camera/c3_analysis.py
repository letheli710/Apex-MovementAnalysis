"""C3 camera capture analysis (rea-native camera feel).

  py -3 c3_analysis.py <session folder> [--json out.json]

Reads the client [HSD-MD] kind=frame lines with the HSD.MoveDiag camera tokens
(cpos, cang, epos, eang, vv, fov) straight from platform/logs, per trial run:

  c3_drop*        landing view kick: camera pitch relative to the last airborne frame,
                  peak, time of the peak, first zero crossing; the same for the eye
                  (aim) pitch and the aim vector, to see whether the punch moves the aim
  c3_jumpland*    the same for a standing-jump landing, with and without duck held
  c3_slide_*      roll (cang z) and eye height (epos z - origin z) from the duck press

Prediction (N2-C): kick angular velocity s*(2 + 0.75 r)*20 deg/s on a spring with
k 65, c 9 -> peak about 0.064 * v0 at about 0.146 s.
Standard library only.
"""
import argparse
import glob
import json
import math
import os
import re

LINE = re.compile(r"\[HSD-MD\] ver=2 side=cl kind=frame (.*)$")
KV = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S*)")


def vec(s):
    try:
        return tuple(float(x) for x in s.split(","))
    except (ValueError, AttributeError):
        return None


def load(session):
    runs = {}
    for f in glob.glob(os.path.join(session, "platform", "logs", "client", "*", "*.log")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = LINE.search(line)
                if not m:
                    continue
                kv = dict(KV.findall(m.group(1)))
                if "cang" not in kv:
                    continue
                run = kv.get("run")
                rec = {"t": float(kv["t"]), "ground": int(kv.get("ground", "-1")), "slide": int(kv.get("slide", "0")),
                       "vel_z": float(kv.get("vz", "0")), "run": run,
                       "o": vec(kv.get("o")), "cang": vec(kv["cang"]), "eang": vec(kv.get("eang")),
                       "epos": vec(kv.get("epos")), "cpos": vec(kv.get("cpos")), "vv": vec(kv.get("vv")),
                       "fov": float(kv.get("fov", "nan")), "in_duck": int(kv.get("in_duck", "0"))}
                runs.setdefault(run, []).append(rec)
    for v in runs.values():
        v.sort(key=lambda r: r["t"])
    return runs


def drop(recs):
    land = next((i for i in range(1, len(recs)) if recs[i - 1]["ground"] == 0 and recs[i]["ground"] == 1), None)
    if land is None:
        return None
    base_c, base_e = recs[land - 1]["cang"][0], recs[land - 1]["eang"][0]
    t0 = recs[land - 1]["t"]
    series = [(r["t"] - t0, r["cang"][0] - base_c, r["eang"][0] - base_e) for r in recs[land - 1:] if r["t"] - t0 <= 1.0]
    peak = max(series, key=lambda x: abs(x[1]))
    cross = next((x[0] for x in series if x[0] > peak[0] and x[1] * peak[1] < 0), None)
    return {"peak_cam_pitch": round(peak[1], 3), "t_peak": round(peak[0], 3), "t_zero_cross": cross,
            "max_aim_pitch_change": round(max(abs(x[2]) for x in series), 4),
            "max_cam_minus_aim": round(max(abs(x[1] - x[2]) for x in series), 3),
            "fov_range": [min(r["fov"] for r in recs), max(r["fov"] for r in recs)]}


def slide(recs):
    start = next((i for i in range(1, len(recs)) if recs[i]["in_duck"] and not recs[i - 1]["in_duck"]), None)
    if start is None:
        return None
    t0 = recs[start]["t"]
    rows = []
    for r in recs[start:]:
        if r["t"] - t0 > 1.2:
            break
        rows.append((round(r["t"] - t0, 3), round(r["cang"][2], 3), round(r["epos"][2] - r["o"][2], 3), r["slide"], r["fov"]))
    eye0 = recs[start - 1]["epos"][2] - recs[start - 1]["o"][2]
    eyes = [x[2] for x in rows]
    sink_end = min(eyes)
    t_sink = next((x[0] for x in rows if x[2] <= sink_end + 0.05), None)
    return {"eye_before": round(eye0, 3), "eye_min": round(sink_end, 3), "t_eye_min": t_sink,
            "roll_max": max(abs(x[1]) for x in rows), "fov_min": min(x[4] for x in rows), "fov_max": max(x[4] for x in rows),
            "samples": rows[::6]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--json")
    a = ap.parse_args()
    with open(os.path.join(a.session, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    runs = load(a.session)
    out = []
    # Drops of 96-400 u land before the client labels the trial (the label comes ~1.2 s
    # after the reset), so landings are found in time order over all frames and given to
    # the next drop trial whose label follows.
    names = {str(t["run"]): t["schedule"] for t in runner["trials"]}
    allrecs = sorted((r for v in runs.values() for r in v), key=lambda r: r["t"])
    labels = [(r["t"], r["run"]) for r in allrecs]
    for i in range(1, len(allrecs)):
        p, q = allrecs[i - 1], allrecs[i]
        if p["ground"] == 0 and q["ground"] == 1 and p["vel_z"] < -300:
            run = next((rn for tt, rn in labels[i:i + 400] if names.get(rn, "").startswith("c3_drop")), None)
            if run is None:
                continue
            res = drop(allrecs[i - 1:i + 130])
            out.append({"schedule": names.get(run), "run": run, "land_vz": p["vel_z"], "duck_held": p["in_duck"], "result": res})
            print(names.get(run), run, "land vz %.1f duck %d" % (p["vel_z"], p["in_duck"]),
                  {k: v for k, v in res.items() if k != "fov_range"})
    for t in runner["trials"]:
        name = t["schedule"]
        if t.get("warmup") or not name.startswith("c3_jumpland"):
            continue
        # Standing-jump landings (~280-320 u/s) happen after the label, inside the trial.
        recs = runs.get(str(t["run"]), [])
        land = next((i for i in range(1, len(recs)) if recs[i - 1]["ground"] == 0 and recs[i]["ground"] == 1), None)
        if land is None:
            print(name, t["run"], "no landing")
            continue
        p = recs[land - 1]
        res = drop(recs[land - 1:land + 130])
        out.append({"schedule": name, "run": t["run"], "land_vz": p["vel_z"], "duck_held": p["in_duck"], "result": res})
        print(name, t["run"], "land vz %.1f duck %d" % (p["vel_z"], p["in_duck"]),
              {k: v for k, v in res.items() if k != "fov_range"})
    for t in runner["trials"]:
        name = t["schedule"]
        if t.get("warmup") or not name.startswith("c3_slide"):
            continue
        recs = runs.get(str(t["run"]), [])
        if not recs:
            print(name, t["run"], "no camera frames")
            continue
        res = slide(recs)
        out.append({"schedule": name, "run": t["run"], "ok": t.get("ok"), "fps": t.get("measured_fps"), "result": res})
        brief = {k: v for k, v in (res or {}).items() if k != "samples"}
        print(name, t["run"], "fps", t.get("measured_fps"), "" if t.get("ok") else "(fps check failed)", brief)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
