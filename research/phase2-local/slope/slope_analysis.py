#!/usr/bin/env python3
"""R6 slope slide: metrics of R5 trials and of the Unity Reference game body on the same inputs and the same lanes.

  py -3 slope_analysis.py <trials_dir> [--unity <unity_dir>] [--json results.json] > analysis_output.txt

<trials_dir>: slope_to_trial.py output (samples.csv = R5, one row per client usercmd, post-state). <unity_dir>: the slope harness
output (<trial_id>/reference.csv, the Reference body stepped with the same per-command inputs in a MovementWorld with the same lane).
Both are read as the same row stream (pre-state of a row = the previous row's post-state), so every metric is computed the same way
for R5 and for Unity. stdlib only; no local paths.

Native law [native S-09, N4D §3] checked per command (grounded sliding commands on one planar segment, >= 24 u from a joint):
  v_h += 0.5*g*dt*n_z*n_h (before the move);  s = |v_h|;  s = max(0, s - D*dt) * 0.7^dt (D = slideDecel 100, slideWantToStopDecel 400
  with duck released);  v_h += 0.5*g*dt*n_z*n_h (after the move, normal under the post origin);  g = 750.
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "tools")))
import slope_geo as G  # noqa: E402

GRAV = 750.0
DECAY = 0.7
JOINT_MARGIN = 24.0
M8_FIT = (147.3, 342.1)          # M8 r_slope: extra = 147 + 342*sin(slope), 29-41 deg downhill, duck held


def r(x, n=2):
    return None if x is None else round(x, n)


def lane_of(schedule):
    s = schedule[3:]
    for name in sorted(G.LANES, key=len, reverse=True):
        if s.startswith(name + "_"):
            return name
    if s.startswith("diag20"):
        return "lat20"
    raise ValueError(schedule)


def read(path, kind):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for d in csv.DictReader(fh):
            row = {"t": float(d["t"]), "dt": float(d["dt"]) if "dt" in d and d["dt"] else None,
                   "x": float(d["pos_x"]), "y": float(d["pos_y"]), "z": float(d["pos_z"]),
                   "vx": float(d["vel_x"]), "vy": float(d["vel_y"]), "vz": float(d["vel_z"]),
                   "g": int(float(d["grounded"])), "s": int(float(d["sliding"]))}
            rows.append(row)
    return rows


def inputs(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for d in csv.DictReader(fh):
            out.append({"duck": int(d["in_duck"]), "jump": int(d["in_jump"]), "fwd": float(d["in_fwd"]), "dt": float(d["dt"]),
                        "yaw": float(d["in_yaw"])})
    return out


def seg_at(lane, x, y):
    _, yc, _, w, _ = G.LANES[lane]
    if abs(y - yc) > w / 2:
        return None
    for i, s in enumerate(G.segments(lane)):
        if s["xa"] <= x <= s["xb"]:
            return i, s
    return None


def joints(lane):
    segs = G.segments(lane)
    return [s["xb"] for s in segs[:-1]]


def near_joint(lane, x):
    return any(abs(x - j) < JOINT_MARGIN for j in joints(lane))


def normal(rise):
    t = math.radians(rise)
    return -math.sin(t), math.cos(t)          # (n_x, n_z); n_y = 0 on every lane


def flat_law(s, dt, D):
    return max(0.0, s - D * dt) * DECAY ** dt


def native_post(vx, vy, dt, rise0, rise1, D):
    nx0, nz0 = normal(rise0)
    nx1, nz1 = normal(rise1)
    vx += 0.5 * GRAV * dt * nz0 * nx0
    s = math.hypot(vx, vy)
    s1 = flat_law(s, dt, D)
    if s > 1e-9:
        vx, vy = vx / s * s1, vy / s * s1
    vx += 0.5 * GRAV * dt * nz1 * nx1
    return vx, vy


def h(row):
    return math.hypot(row["vx"], row["vy"])


def stats(v):
    if not v:
        return None
    return {"n": len(v), "mean": r(statistics.fmean(v), 3), "sd": r(statistics.pstdev(v), 3) if len(v) > 1 else 0.0,
            "rms": r(math.sqrt(sum(x * x for x in v) / len(v)), 3), "min": r(min(v), 3), "max": r(max(v), 3)}


def law_rows(rows, ins, lane):
    """Per grounded sliding command on one planar segment: residual of the native law, extra accel along travel."""
    out = []
    for i in range(1, len(rows)):
        a, b, u = rows[i - 1], rows[i], ins[i]
        if not (a["g"] and b["g"] and a["s"] and b["s"]) or u["jump"]:
            continue
        sa, sb = seg_at(lane, a["x"], a["y"]), seg_at(lane, b["x"], b["y"])
        if sa is None or sb is None or sa[0] != sb[0] or near_joint(lane, a["x"]) or near_joint(lane, b["x"]):
            continue
        dt = u["dt"]
        rise = sa[1]["rise_deg"]
        D = 100.0 if u["duck"] else 400.0
        h0, h1 = h(a), h(b)
        if h0 < 1:
            continue
        if h1 - h0 > 20:                      # a re-boost (ground entity change), reported separately
            continue
        px, py = native_post(a["vx"], a["vy"], dt, rise, rise, D)
        ux = a["vx"] / h0
        nx, nz = normal(rise)
        out.append({"rise": rise, "duck": u["duck"], "h0": h0, "dt": dt,
                    "res": math.hypot(px, py) - h1,                          # predicted - measured |v_h|
                    "extra": (h1 - flat_law(h0, dt, D)) / dt,                 # beyond the flat slide law
                    "pred_extra": GRAV * nz * nx * ux,                        # g n_z (n_h . v_hat)
                    "lat": abs(a["vy"]) > 0.2 * h0})
    return out


def move_rows(rows, ins, lane):
    """Per grounded command on one sloped segment (>= 24 u from a joint, |v_h| >= 50): horizontal displacement / (|v_h| dt), the climb
    angle of the motion (+ = uphill), and the origin height above the designed surface."""
    out = []
    for i in range(1, len(rows)):
        a, b = rows[i - 1], rows[i]
        sa, sb = seg_at(lane, a["x"], a["y"]), seg_at(lane, b["x"], b["y"])
        if not (a["g"] and b["g"]) or sa is None or sb is None or sa[0] != sb[0] or near_joint(lane, a["x"]) or near_joint(lane, b["x"]):
            continue
        rise = sa[1]["rise_deg"]
        hb = h(b)
        if hb < 50:
            continue
        ux, uy = b["vx"] / hb, b["vy"] / hb
        climb = math.degrees(math.atan(math.tan(math.radians(rise)) * ux))      # slope of the motion direction
        d = math.hypot(b["x"] - a["x"], b["y"] - a["y"])
        out.append({"rise": rise, "climb": round(climb, 1), "ratio": d / (hb * ins[i]["dt"]),
                    "dz": b["z"] - G.surface_z(lane, b["x"])[0]})
    return out


def move_summary(trials, side):
    by = {}
    for t in trials:
        for q in t.get(side + "_move", []):
            if q["rise"] == 0:
                continue
            key = (abs(q["rise"]), "up" if q["climb"] > 1 else "down" if q["climb"] < -1 else "across")
            by.setdefault(key, []).append(q)
    out = []
    for (th, kind), qs in sorted(by.items()):
        cl = statistics.median([abs(q["climb"]) for q in qs])
        out.append({"slope_deg": th, "kind": kind, "n": len(qs), "climb_deg": r(cl, 1),
                    "ratio": r(statistics.median([q["ratio"] for q in qs]), 4), "cos_climb": r(math.cos(math.radians(cl)), 4),
                    "cos2_climb": r(math.cos(math.radians(cl)) ** 2, 4), "dz_on_slope": r(statistics.median([q["dz"] for q in qs]), 2)})
    return out


def first_idx(rows, cond, start=0):
    return next((i for i in range(start, len(rows)) if cond(rows[i])), None)


def uphill(rows, ins, lane):
    """Up lanes: ramp entry, slide end, distance up, back-slide."""
    foot = joints(lane)[0]
    rise = G.segments(lane)[1]["rise_deg"]
    ie = first_idx(rows, lambda q: q["x"] > foot and q["g"])
    if ie is None:
        return None
    i_end = first_idx(rows, lambda q: not q["s"], ie)
    entry = rows[ie]
    land = None
    il = next((i for i in range(1, len(rows)) if rows[i]["g"] and not rows[i - 1]["g"]), None)
    if il is not None:
        land = {"x_from_foot": r(rows[il]["x"] - foot, 1), "h": r(h(rows[il]), 1), "slide": rows[il]["s"], "t": r(rows[il]["t"], 3)}
    after = rows[i_end:] if i_end is not None else []
    back = min((q["vx"] for q in after), default=None)            # most negative x velocity (downhill) after the slide end
    x_rest = rows[-1]["x"]
    out = {"rise": rise, "entry_h": r(h(entry), 1), "entry_t": r(entry["t"], 3), "entry_sliding": entry["s"], "landing": land}
    if i_end is not None:
        e = rows[i_end]
        out.update({"end_t_after_entry": r(e["t"] - entry["t"], 3), "end_h_pre": r(h(rows[i_end - 1]), 1), "end_h": r(h(e), 1),
                    "end_up_slope": r((e["x"] - foot) / math.cos(math.radians(rise)), 1),
                    "min_vx_after_end": r(back, 2), "rest_x_minus_end_x": r(x_rest - e["x"], 1),
                    "crouch_walk_h": r(statistics.median([h(q) for q in after[10:60]]), 1) if len(after) > 60 else None})
    max_back_slide = min((q["vx"] for q in rows[ie:] if q["s"]), default=None)
    out["min_vx_while_sliding"] = r(max_back_slide, 2)
    return out


def transitions(rows, lane):
    """Each joint crossing: speed just before / after, grounded state within +-0.3 s, max |vz| while grounded nearby."""
    out = []
    for j, xj in enumerate(joints(lane)):
        i = first_idx(rows, lambda q: q["x"] >= xj)
        if i is None or i == 0:
            continue
        t0 = rows[i]["t"]
        win = [q for q in rows if abs(q["t"] - t0) <= 0.3]
        segs = G.segments(lane)
        out.append({"joint": j, "from_deg": segs[j]["rise_deg"], "to_deg": segs[j + 1]["rise_deg"], "t": r(t0, 3),
                    "h_before": r(h(rows[i - 1]), 2), "h_after": r(h(rows[i]), 2), "dh": r(h(rows[i]) - h(rows[i - 1]), 2),
                    "dh_m01_p01": r(h(next((q for q in rows[i:] if q["t"] >= t0 + 0.1), rows[-1])) - h(next((q for q in reversed(rows[:i]) if q["t"] <= t0 - 0.1), rows[0])), 2),
                    "sliding": rows[i]["s"], "airborne_cmds_pm03": sum(1 for q in win if not q["g"]),
                    "max_abs_vz_grounded_pm03": r(max((abs(q["vz"]) for q in win if q["g"]), default=0.0), 2),
                    "max_rise_above_surface_pm03": r(max((q["z"] - (G.surface_z(lane, q["x"])[0] or q["z"]) for q in win), default=0.0), 2)})
    return out


def reboosts(rows, ins):
    """Grounded sliding commands whose |v_h| jumps up by > 20 (not a jump, not the slide start)."""
    out = []
    t_start = None
    for i in range(1, len(rows)):
        a, b = rows[i - 1], rows[i]
        if b["s"] and not a["s"]:
            t_start = b["t"]
        if a["g"] and b["g"] and a["s"] and b["s"] and not ins[i]["jump"] and h(b) - h(a) > 20:
            out.append({"t": r(b["t"], 3), "x": r(b["x"], 1), "y": r(b["y"], 1), "h0": r(h(a), 2), "h1": r(h(b), 2),
                        "since_slide_start": r(b["t"] - t_start, 3) if t_start is not None else None})
    return out


def lateral(rows, ins, lane):
    """Slides on lat20: heading change and downhill drift over the slide."""
    i0 = first_idx(rows, lambda q: q["s"])
    if i0 is None:
        return None
    i1 = first_idx(rows, lambda q: not q["s"], i0) or len(rows) - 1
    a, b = rows[i0], rows[i1 - 1]
    head = lambda q: math.degrees(math.atan2(q["vy"], q["vx"]))  # noqa: E731
    pts = []
    for k in range(0, 40):
        q = next((rows[j] for j in range(i0, i1) if rows[j]["t"] >= a["t"] + 0.25 * k), None)
        if q is None:
            break
        pts.append([r(q["t"] - a["t"], 2), r(q["x"] - a["x"], 1), r(q["y"] - a["y"], 1), r(h(q), 1), r(head(q), 1)])
    return {"slide_t": r(b["t"] - a["t"], 3), "start_h": r(h(a), 1), "end_h": r(h(b), 1), "start_heading": r(head(a), 1),
            "end_heading": r(head(b), 1), "dx_downhill": r(b["x"] - a["x"], 1), "dy": r(b["y"] - a["y"], 1),
            "min_h": r(min(h(rows[j]) for j in range(i0, i1)), 1), "series": pts}


def trial_metrics(rows, ins, sched):
    lane = lane_of(sched)
    m = {"lane": lane}
    if lane.startswith("up"):
        m["uphill"] = uphill(rows, ins, lane)
    if lane != "lat20":
        m["transitions"] = transitions(rows, lane)
    else:
        m["lateral"] = lateral(rows, ins, lane)
    m["reboosts"] = reboosts(rows, ins)
    i0 = first_idx(rows, lambda q: q["s"])
    m["slide_start"] = {"t": r(rows[i0]["t"], 3), "x": r(rows[i0]["x"], 1), "h": r(h(rows[i0]), 1)} if i0 is not None else None
    m["max_h"] = r(max(h(q) for q in rows), 2)
    m["airborne_cmds"] = sum(1 for q in rows if not q["g"])
    m["slide_cmds"] = sum(1 for q in rows if q["s"])
    return m


def group(trials):
    by = {}
    for t in trials:
        by.setdefault(t["schedule"], []).append(t)
    return by


def summarize(name, by, side):
    """Condition summaries: means over the trials of one schedule."""
    out = {}
    for sched, ts in sorted(by.items()):
        ms = [t[side] for t in ts if t.get(side)]
        if not ms:
            continue
        s = {"n": len(ms)}
        ups = [m["uphill"] for m in ms if m.get("uphill")]
        if ups:
            for k in ("entry_h", "end_t_after_entry", "end_up_slope", "end_h_pre", "min_vx_after_end", "rest_x_minus_end_x", "crouch_walk_h",
                      "min_vx_while_sliding"):
                v = [u[k] for u in ups if u.get(k) is not None]
                s[k] = stats(v)
            s["landing_x_from_foot"] = stats([u["landing"]["x_from_foot"] for u in ups if u.get("landing")])
            s["landing_sliding"] = [u["landing"]["slide"] for u in ups if u.get("landing")]
        trs = [m["transitions"] for m in ms if m.get("transitions")]
        if trs:
            s["transitions"] = []
            for j in range(max(len(x) for x in trs)):
                rows = [x[j] for x in trs if len(x) > j]
                s["transitions"].append({"from_deg": rows[0]["from_deg"], "to_deg": rows[0]["to_deg"], "n": len(rows),
                                         "h_before": stats([q["h_before"] for q in rows]), "dh": stats([q["dh"] for q in rows]), "dh_m01_p01": stats([q["dh_m01_p01"] for q in rows]),
                                         "sliding": sum(q["sliding"] for q in rows),
                                         "airborne_cmds_pm03": [q["airborne_cmds_pm03"] for q in rows],
                                         "max_abs_vz_grounded_pm03": max(q["max_abs_vz_grounded_pm03"] for q in rows),
                                         "max_rise_above_surface_pm03": max(q["max_rise_above_surface_pm03"] for q in rows)})
        lats = [m["lateral"] for m in ms if m.get("lateral")]
        if lats:
            for k in ("slide_t", "start_h", "end_h", "min_h", "end_heading", "dx_downhill", "dy"):
                s[k] = stats([q[k] for q in lats if q.get(k) is not None])
            s["series_first"] = lats[0]["series"]
        s["reboosts"] = [b for m in ms for b in m["reboosts"]]
        s["max_h"] = stats([m["max_h"] for m in ms])
        s["airborne_cmds"] = [m["airborne_cmds"] for m in ms]
        out[sched] = s
    return out


def law_summary(trials, side):
    rows = [q for t in trials for q in t.get(side + "_law", [])]
    by = {}
    for q in rows:
        if q["lat"]:
            key = ("lat", q["rise"], q["duck"])
        else:
            key = ("up" if q["pred_extra"] < -1 else "down" if q["pred_extra"] > 1 else "flat", q["rise"], q["duck"])
        by.setdefault(key, []).append(q)
    out = []
    for (kind, rise, duck), qs in sorted(by.items(), key=lambda kv: (kv[0][0], abs(kv[0][1]), kv[0][2])):
        th = abs(rise)
        out.append({"kind": kind, "slope_deg": th, "duck": duck, "n": len(qs),
                    "res_rms": stats([q["res"] for q in qs])["rms"], "res_mean": stats([q["res"] for q in qs])["mean"],
                    "extra": stats([q["extra"] for q in qs]), "native_extra": r(statistics.fmean([q["pred_extra"] for q in qs]), 1),
                    "m8_fit_extra": r((M8_FIT[0] + M8_FIT[1] * math.sin(math.radians(th))) * (1 if kind == "down" else -1 if kind == "up" else 0), 1)
                    if kind in ("down", "up") else None})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trials")
    ap.add_argument("--unity")
    ap.add_argument("--json")
    a = ap.parse_args()
    trials = []
    for tid in sorted(os.listdir(a.trials)):
        p = os.path.join(a.trials, tid)
        if not os.path.isfile(os.path.join(p, "samples.csv")):
            continue
        man = json.load(open(os.path.join(p, "trial.json"), encoding="utf-8"))
        sched = man["schedule"]
        ins = inputs(os.path.join(p, "samples.csv"))
        R = read(os.path.join(p, "samples.csv"), "r5")
        t = {"id": tid, "schedule": sched, "r5": trial_metrics(R, ins, sched), "r5_law": law_rows(R, ins, lane_of(sched)),
             "r5_move": move_rows(R, ins, lane_of(sched))}
        up =os.path.join(a.unity, tid, "reference.csv") if a.unity else None
        if up and os.path.isfile(up):
            U = read(up, "unity")
            t["unity"] = trial_metrics(U, ins, sched)
            t["unity_law"] = law_rows(U, ins, lane_of(sched))
            t["unity_move"] = move_rows(U, ins, lane_of(sched))
            # trajectory agreement while both are in the first slide: |v_h| and position gaps
            n = min(len(R), len(U))
            dv = [abs(h(R[i]) - h(U[i])) for i in range(n)]
            dp = [math.dist((R[i]["x"], R[i]["y"], R[i]["z"]), (U[i]["x"], U[i]["y"], U[i]["z"])) for i in range(n)]
            # the same up to R5's first re-boost (a ground-entity change the Unity world does not have)
            rb = [b["t"] for b in t["r5"]["reboosts"] if b["since_slide_start"] and b["since_slide_start"] > 0.05]
            k = next((i for i in range(n) if rb and R[i]["t"] >= rb[0] - 1e-6), n)
            t["gap"] = {"max_dh": r(max(dv), 1), "max_dpos": r(max(dp), 1), "end_dpos": r(dp[n - 1], 1),
                        "pre_reboost_p50_dh": r(sorted(dv[:k])[k // 2], 1), "pre_reboost_p95_dh": r(sorted(dv[:k])[int(k * 0.95)], 1), "pre_reboost_max_dxy": r(max(math.dist((R[i]["x"], R[i]["y"]), (U[i]["x"], U[i]["y"])) for i in range(k)), 1),
                        "reboost_t": rb[0] if rb else None}
        trials.append(t)
    by = group(trials)
    res = {"n_trials": len(trials), "law_r5": law_summary(trials, "r5"), "cond_r5": summarize("r5", by, "r5"),
           "move_r5": move_summary(trials, "r5")}
    if a.unity:
        res["law_unity"] = law_summary(trials, "unity")
        res["move_unity"] = move_summary(trials, "unity")
        res["cond_unity"] = summarize("unity", by, "unity")
        res["gaps"] = {s: [t["gap"] for t in ts if t.get("gap")] for s, ts in by.items()}
    res["trials"] = [{k: t[k] for k in ("id", "schedule", "r5") if k in t} | ({"unity": t["unity"]} if "unity" in t else {}) for t in trials]
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1)
    print("trials:", len(trials))
    for side in ("r5", "unity") if a.unity else ("r5",):
        print("\n## per-command native law,", side)
        print("kind  slope duck    n  res_rms res_mean | extra mean (sd)   native   M8fit")
        for q in res["law_" + side]:
            print("%-5s %5.1f %4d %5d  %7.3f %8.3f | %8.1f (%5.1f) %8.1f %7s" % (q["kind"], q["slope_deg"], q["duck"], q["n"], q["res_rms"], q["res_mean"],
                  q["extra"]["mean"], q["extra"]["sd"], q["native_extra"], q["m8_fit_extra"]))
    for side in ("r5", "unity") if a.unity else ("r5",):
        print("\n## move along the slope,", side, "(horizontal step / (|v_h| dt); origin height above the surface)")
        for q in res["move_" + side]:
            print("  %4.0f deg %-6s n %5d climb %5.1f ratio %.4f  cos %.4f  cos^2 %.4f  dz %.2f" % (
                q["slope_deg"], q["kind"], q["n"], q["climb_deg"], q["ratio"], q["cos_climb"], q["cos2_climb"], q["dz_on_slope"]))
    print("\n## conditions (R5" +(" | Unity" if a.unity else "") + ")")
    for sched in sorted(by):
        cr = res["cond_r5"].get(sched)
        cu = res.get("cond_unity", {}).get(sched)
        print("\n#", sched, "n", cr["n"] if cr else 0)
        for k in sorted(cr or {}):
            if k in ("n",):
                continue
            vu = cu.get(k) if cu else None
            print("  %-26s R5 %s" % (k, json.dumps(cr[k])[:300]))
            if cu is not None:
                print("  %-26s U  %s" % ("", json.dumps(vu)[:300]))
        if a.unity:
            print("  gaps", json.dumps(res["gaps"][sched])[:300])


if __name__ == "__main__":
    main()
