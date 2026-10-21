#!/usr/bin/env python3
"""M2 / E1 ground model: start, cruise, stop, directions, stances and turning.

  python ground_analysis.py <session folder> [<session folder> ...] [--out DIR]

Reads each session's platform/logs (hsdtel parse + derive), runner.json (scored trials:
ok=true, warmup=false, E1 schedules only) and report/census.csv (client class vars).
Writes into --out (default: the folder of this script):

  results.json      every number quoted in GROUND-MODEL.md (join/dt validation, per-trial
                    terminal speeds and fitted parameters, model comparisons, turning)
  params.json       the chosen model's parameters (value, unit, source, n, spread, formula)
  curves_<cond>.csv speed vs time per trial (time from the first command with movement input)
  curves_<cond>.svg the same curves with the chosen model's closed-loop prediction overlaid

Physics truth = client first-time MOVE-TRACE rows (side cl, rp=0). The per-command dt comes
from the HSD client frame stream. Each HSD frame shows the post-state of exactly one command
(joined by exact post-state equality, validated per trial). The frame whose state is post(N+1)
carries FrameTime() and view angles equal to command N's frametime and yaw (validated against
the displacement-derived dt and the velocity heading; see results.json 'dt_validation').
No raw log lines and no absolute paths are written.  Stdlib only.
"""
import argparse
import csv
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-prep", "tools"))
from hsdtel import derive, parse  # noqa: E402
from hsdtel.schema import BUTTON_BITS  # noqa: E402

E1 = ("e1_walk", "e1_sprint", "e1_crouch", "e1_back", "e1_side", "e1_diag", "e1_turn")
MOVE_BITS = BUTTON_BITS["FORWARD"] | BUTTON_BITS["BACK"] | BUTTON_BITS["MOVELEFT"] | BUTTON_BITS["MOVERIGHT"]
IN_SPEED = BUTTON_BITS["SPEED"]
IN_DUCK = BUTTON_BITS["DUCK"]
EQ_TOL = 0.0015          # print precision of %.3f states
CLAMP_TOL = 0.002        # a post speed within this of the cap counts as clamped
CRUISE_S = 1.0           # terminal speed = mean post speed over the last CRUISE_S before release


# ------------------------------------------------------------------ loading and joining
def load_census(folder):
    path = os.path.join(folder, "report", "census.csv")
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    out[row["key"]] = float(row["cl_classvar"])
                except (TypeError, ValueError):
                    pass
    return out


def same(a, b):
    return abs(a - b) < EQ_TOL


def frame_matches_post(f, r):
    return (same(f["ox"], r["pox"]) and same(f["oy"], r["poy"]) and same(f["oz"], r["poz"])
            and same(f["vx"], r["pvx"]) and same(f["vy"], r["pvy"]) and same(f["vz"], r["pvz"]))


def load_session(folder):
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    mt, frames_by_run, frames_by_seq = {}, {}, {}
    sv_by_key = {}
    for r in rows:
        if r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay"):
            mt.setdefault(r.get("drv_run"), []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "cl" and r.get("kind") == "frame":
            frames_by_run.setdefault(r.get("drv_run"), []).append(r)
            frames_by_seq[(r.get("session"), int(r["seq"]))] = r
    for v in mt.values():
        v.sort(key=lambda r: r["cmd"])
    for v in frames_by_run.values():
        v.sort(key=lambda r: r["seq"])
    return runner, mt, frames_by_run, frames_by_seq, len(issues)


def join_trial(cmds, frames, frames_by_seq):
    """Join HSD frames to commands: offset = seq - cmd from unique exact post-state matches of
    moving frames, then every frame/command pair under that offset is checked for equality."""
    offs = {}
    for f in frames:
        if math.hypot(f["vx"], f["vy"]) < 1.0 and abs(f["vz"]) < 1.0:
            continue
        cand = [r for r in cmds if frame_matches_post(f, r)]
        if len(cand) == 1:
            offs[int(f["seq"]) - cand[0]["cmd"]] = offs.get(int(f["seq"]) - cand[0]["cmd"], 0) + 1
    if not offs:
        return None, {"error": "no moving frame matched"}
    off = max(offs, key=offs.get)
    ses = frames[0].get("session")
    n_eq = n_moving_eq = n_moving = 0
    gaps = sum(1 for a, b in zip(cmds, cmds[1:]) if b["cmd"] - a["cmd"] != 1)
    for r in cmds:
        f = frames_by_seq.get((ses, r["cmd"] + off))
        if f is None:
            continue
        mv = math.hypot(r["pvx"], r["pvy"]) >= 1.0
        n_moving += mv
        if frame_matches_post(f, r):
            n_eq += 1
            n_moving_eq += mv
    stats = {"cmds": len(cmds), "frames": len(frames), "cmd_gaps": gaps, "offsets_seen": {str(k): v for k, v in offs.items()},
             "offset": off, "post_equal": n_eq, "moving": n_moving, "moving_post_equal": n_moving_eq}
    return off, stats


def build_trial(t, cmds, frames, frames_by_seq):
    off, jstats = join_trial(cmds, frames, frames_by_seq)
    if off is None:
        return None, jstats
    ses = frames[0].get("session")
    recs = []
    shift_err = {-1: [], 0: [], 1: []}
    yaw_err = {0: [], 1: []}
    for r in cmds:
        f_next = frames_by_seq.get((ses, r["cmd"] + off + 1))
        f_this = frames_by_seq.get((ses, r["cmd"] + off))
        s0, s1 = math.hypot(r["vx"], r["vy"]), math.hypot(r["pvx"], r["pvy"])
        disp = math.hypot(r["pox"] - r["ox"], r["poy"] - r["oy"])
        est = disp / s1 if s1 >= 150.0 else None
        if est is not None and r["ground"] == 1:
            for s in shift_err:
                f = frames_by_seq.get((ses, r["cmd"] + off + s))
                if f is not None:
                    shift_err[s].append(abs(f["ft"] - est))
        heading = math.degrees(math.atan2(r["pvy"], r["pvx"])) if s1 > 50 else None
        if heading is not None and r["buttons"] & MOVE_BITS:
            for s, f in ((0, f_this), (1, f_next)):
                if f is not None:
                    wish = wish_yaw(f["yaw"], r["fwd"], r["sidemove"])
                    if wish is not None:
                        yaw_err[s].append(abs(angdiff(heading, wish)))
        recs.append({
            "cmd": r["cmd"], "b": r["buttons"], "fwd": r["fwd"], "sd": r["sidemove"], "ms": r["maxspeed"],
            "msc": r["movescale"], "spr": r["sprint"], "duck": r["duck"], "slide": r["slide"], "ground": r["ground"],
            "s0": s0, "s1": s1, "vx1": r["pvx"], "vy1": r["pvy"], "heading": heading,
            "dt": f_this["ft"] if f_this is not None else None,
            "yaw": f_this["yaw"] if f_this is not None else None,
            "dt_est": est,
        })
    jstats["dt_missing"] = sum(1 for x in recs if x["dt"] is None)
    return recs, {"join": jstats, "shift_err": shift_err, "yaw_err": yaw_err}


def wish_yaw(yaw, fwd, sd):
    if abs(fwd) < 1e-6 and abs(sd) < 1e-6:
        return None
    # Source: forward = (cos y, sin y), right = (sin y, -cos y); wish = fwd*forward + sd*right
    y = math.radians(yaw)
    x = fwd * math.cos(y) + sd * math.sin(y)
    z = fwd * math.sin(y) - sd * math.cos(y)
    return math.degrees(math.atan2(z, x))


def angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


# ------------------------------------------------------------------ segmentation
def segment(recs):
    """press = first command with a movement button; release = first later command without one."""
    press = next((i for i, x in enumerate(recs) if x["b"] & MOVE_BITS), None)
    if press is None:
        return None, None
    release = next((i for i in range(press, len(recs)) if not recs[i]["b"] & MOVE_BITS), None)
    return press, release


def times(recs, i0):
    """t[i] = time at the END of command i, measured from the start of command i0."""
    t, acc = [], 0.0
    for i, x in enumerate(recs):
        if i >= i0:
            acc += x["dt"] or 0.0
            t.append(acc)
        else:
            t.append(None)
    return t


def spread(vals):
    m = st.mean(vals)
    return (max(vals) - min(vals)) / abs(m) * 100.0 if m else float("nan")


def summ(vals, nd=3):
    vals = [v for v in vals if v is not None and math.isfinite(v)]
    if not vals:
        return None
    out = {"n": len(vals), "mean": round(st.mean(vals), nd), "min": round(min(vals), nd), "max": round(max(vals), nd),
           "spread_pct": round(spread(vals), 3) if len(vals) > 1 else 0.0}
    if len(vals) > 1:
        out["sd"] = round(st.stdev(vals), nd + 1)
    return out


# ------------------------------------------------------------------ fits
def accel_commands(recs, press, release):
    """Commands with movement input on the ground whose post speed was not clamped at maxspeed."""
    out = []
    for x in recs[press:release]:
        if x["ground"] != 1 or x["dt"] is None or x["slide"]:
            continue
        if x["s1"] >= x["ms"] - CLAMP_TOL or x["s1"] <= x["s0"] + 1e-4:
            continue
        out.append(x)
    return out


def decel_commands(recs, release):
    out = []
    for x in recs[release:]:
        if x["ground"] != 1 or x["dt"] is None or x["b"] & MOVE_BITS:
            continue
        if x["s0"] <= 0.0 or x["s1"] <= 0.0:   # stopped, or the last step clamped at zero
            continue
        out.append(x)
    return out


def ratio_fit(cs):
    """a = sum(ds) / sum(dt): least-squares constant rate for steps ds = a*dt."""
    if not cs:
        return None
    return sum(x["s1"] - x["s0"] for x in cs) / sum(x["dt"] for x in cs)


def classify_bands(cs, a_low, a_mid, a_spr):
    """Assign each accel command to the band whose rate it matches best."""
    out = {"low": [], "mid": [], "sprint": []}
    for x in cs:
        a = (x["s1"] - x["s0"]) / x["dt"]
        cands = [("low", a_low), ("mid", a_mid)] + ([("sprint", a_spr)] if a_spr else [])
        band = min(cands, key=lambda kv: abs(a - kv[1]))[0]
        out[band].append(x)
    return out


def fit_source_friction(steps, grid_stop, grid_f):
    """Source Friction(): drop = max(speed, stopspeed) * f * dt.  Least squares over a grid."""
    best = None
    for sp in grid_stop:
        # for a fixed stopspeed the model is linear in f: ds = f * max(s0, sp) * dt
        num = sum((x["s0"] - x["s1"]) * max(x["s0"], sp) * x["dt"] for x in steps)
        den = sum((max(x["s0"], sp) * x["dt"]) ** 2 for x in steps)
        f = num / den if den else 0.0
        res = [(x["s0"] - x["s1"]) - f * max(x["s0"], sp) * x["dt"] for x in steps]
        rms = math.sqrt(sum(e * e for e in res) / len(res))
        if best is None or rms < best[2]:
            best = (sp, f, rms)
    return best


# ------------------------------------------------------------------ closed-loop models
def model_ground(params, msc, stance, sprinting):
    """Return (a(s0), cap) for the chosen piecewise-constant model."""
    m = msc
    if stance == "crouch":
        cap = params["crouch_speed"] * m
    elif sprinting:
        cap = params["sprintspeed"] * m
    else:
        cap = params["speed"] * m

    def accel(s0, dt):
        if s0 < params["lowSpeed"] * m:
            return params["lowAcceleration"] * m
        if not sprinting:
            return params["acceleration"] * m
        # sprint band: by default it starts one sprint step BELOW speed*msc (s0 + a_spr*dt >= speed*msc);
        # with sprint_lookahead=False it starts at s0 >= speed*msc (the plain pre-speed rule)
        a_spr = params["sprintAcceleration"] * m
        edge = params["speed"] * m - (a_spr * dt if params.get("sprint_lookahead", True) else 0.0)
        return params["acceleration"] * m if s0 < edge else a_spr
    return accel, cap


def step(x, params, stance):
    """One command of the chosen model from the observed pre-speed."""
    decel = params["crouch_deceleration"] if stance == "crouch" else params["deceleration"]
    s = x["s0"]
    if x["b"] & MOVE_BITS:
        accel, cap = model_ground(params, x["msc"], stance, bool(x["spr"]))
        if s < cap:
            return min(cap, s + accel(s, x["dt"]) * x["dt"])
        return max(cap, s - decel * x["dt"])
    return snap(s - decel * x["dt"], params)


def snap(s, params):
    """Post-decel speeds below stop_snap_speed become 0 (Source WalkMove's 1 u/s rule; bracketed by the data)."""
    return 0.0 if s < params.get("stop_snap_speed", 0.0) else s


def simulate(recs, press, params, stance):
    """Closed loop over the observed dt and input sequence from the press: speed only."""
    decel_key = "crouch_deceleration" if stance == "crouch" else "deceleration"
    s = recs[press]["s0"]
    pred = []
    for x in recs[press:]:
        if x["dt"] is None:      # only the last command of a trial (its frame N+1 is not logged)
            break
        held = bool(x["b"] & MOVE_BITS)
        sprinting = bool(x["spr"])
        if held:
            accel, cap = model_ground(params, x["msc"], stance, sprinting)
            if s < cap:
                s = min(cap, s + accel(s, x["dt"]) * x["dt"])
            elif s > cap:
                s = max(cap, s - params[decel_key] * x["dt"])
        else:
            s = snap(s - params[decel_key] * x["dt"], params)
        pred.append(s)
    return pred


def simulate_single(recs, press, a, d):
    s = recs[press]["s0"]
    pred = []
    for x in recs[press:]:
        if x["dt"] is None:
            break
        if x["b"] & MOVE_BITS:
            s = min(x["ms"], s + a * x["dt"])
        else:
            s = max(0.0, s - d * x["dt"])
        pred.append(s)
    return pred


def simulate_source_stop(recs, release, sp, f):
    s = recs[release]["s0"]
    pred = []
    for x in recs[release:]:
        drop = max(s, sp) * f * x["dt"]
        s = max(0.0, s - drop)
        pred.append(s)
    return pred


def rms(pred, obs):
    e = [p - o for p, o in zip(pred, obs)]
    return math.sqrt(sum(v * v for v in e) / len(e)) if e else float("nan"), max((abs(v) for v in e), default=0.0)


# ------------------------------------------------------------------ SVG
def svg_curves(path, title, series, model):
    W, H, L, B, T, R = 760, 380, 56, 40, 30, 14
    xs = [t for s in series for t, _ in s[1]] + [t for t, _ in model]
    ys = [v for s in series for _, v in s[1]] + [v for _, v in model]
    x0, x1 = min(xs), max(xs)
    y1 = max(ys) * 1.08 if ys else 1.0

    def X(t):
        return L + (t - x0) / (x1 - x0 or 1) * (W - L - R)

    def Y(v):
        return H - B - v / y1 * (H - B - T)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="11">',
           f'<rect width="{W}" height="{H}" fill="#fff"/>',
           f'<text x="{L}" y="18" font-size="13">{title}</text>']
    step = 50 if y1 < 400 else 100
    v = 0
    while v <= y1:
        out.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e4e4e4"/>'
                   f'<text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}</text>')
        v += step
    t = math.ceil(x0 * 2) / 2
    while t <= x1:
        out.append(f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H - B}" stroke="#eeeeee"/>'
                   f'<text x="{X(t):.1f}" y="{H - B + 14}" text-anchor="middle">{t:g}</text>')
        t += 0.5
    out.append(f'<text x="{(L + W) / 2}" y="{H - 6}" text-anchor="middle">time from first input command (s)</text>')
    out.append(f'<text x="14" y="{(T + H - B) / 2}" transform="rotate(-90 14 {(T + H - B) / 2})" text-anchor="middle">2D speed (u/s)</text>')
    cols = ["#1f77b4", "#2ca02c", "#9467bd", "#8c564b", "#17becf"]
    for k, (name, pts) in enumerate(series):
        d = " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in pts)
        out.append(f'<polyline points="{d}" fill="none" stroke="{cols[k % 5]}" stroke-width="1.2"/>')
        out.append(f'<text x="{W - R - 4}" y="{T + 14 * (k + 1)}" text-anchor="end" fill="{cols[k % 5]}">{name}</text>')
    if model:
        d = " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in model)
        out.append(f'<polyline points="{d}" fill="none" stroke="#d62728" stroke-width="1" stroke-dasharray="4 3"/>')
        out.append(f'<text x="{W - R - 4}" y="{T + 14 * (len(series) + 1)}" text-anchor="end" fill="#d62728">model (closed loop, first trial dt)</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))


# ------------------------------------------------------------------ main analysis
def analyse(folders, outdir):
    trials = []
    session_info = []
    census = {}
    for folder in folders:
        runner, mt, frames_by_run, frames_by_seq, n_issues = load_session(folder)
        c = load_census(folder)
        census = census or c
        session_info.append({"session": os.path.basename(os.path.normpath(folder)), "parse_issues": n_issues,
                             "census_keys": len(c)})
        for t in runner["trials"]:
            if t.get("warmup") or not t.get("ok") or t.get("schedule") not in E1:
                continue
            run = f"r{t['run']}"
            cmds, frames = mt.get(run, []), frames_by_run.get(run, [])
            if not cmds or not frames:
                trials.append({"run": run, "cond": t["schedule"], "error": "no commands or frames"})
                continue
            recs, val = build_trial(t, cmds, frames, frames_by_seq)
            trials.append({"run": run, "cond": t["schedule"], "yaw": t.get("yaw"), "fps": t.get("measured_fps"),
                           "recs": recs, "val": val, "census": c})

    res = {"sessions": session_info, "census_used": {k: census.get(k) for k in (
        "speed", "sprintspeed", "acceleration", "deceleration", "lowSpeed", "lowAcceleration", "sprintAcceleration",
        "sprintDeceleration", "speedScaleSide", "speedScaleBack", "sprintStartDelay", "sprintStartDuration",
        "sprintStartFastDuration", "sprintEndDuration")}}

    # ---- join and dt validation
    jv = []
    sh = {-1: [], 0: [], 1: []}
    ye = {0: [], 1: []}
    for tr in trials:
        if "val" not in tr:
            continue
        j = tr["val"]["join"]
        jv.append({"run": tr["run"], "cond": tr["cond"], **{k: j[k] for k in (
            "cmds", "frames", "cmd_gaps", "offset", "post_equal", "moving", "moving_post_equal", "dt_missing")},
            "offsets_seen": j["offsets_seen"]})
        for s in sh:
            sh[s] += tr["val"]["shift_err"][s]
        for s in ye:
            ye[s] += tr["val"]["yaw_err"][s]
    tot = {k: sum(x[k] for x in jv) for k in ("cmds", "frames", "cmd_gaps", "post_equal", "moving", "moving_post_equal", "dt_missing")}
    res["join"] = {"per_trial": jv, "total": tot,
                   "single_offset_trials": sum(1 for x in jv if len(x["offsets_seen"]) == 1), "trials": len(jv)}
    res["dt_validation"] = {
        "note": "|ft of frame showing post(N+s) - dt_est(N)| over grounded commands with post speed >= 150 u/s; "
                "dt_est = |po_xy - o_xy| / |pv_xy|",
        **{f"shift_{s:+d}": {"n": len(v), "mean_abs_us": round(1e6 * st.mean(v), 2),
                             "within_10us_pct": round(100 * sum(e < 1e-5 for e in v) / len(v), 2),
                             "within_20us_pct": round(100 * sum(e < 2e-5 for e in v) / len(v), 2)}
           for s, v in sh.items() if v},
        "yaw": {f"frame_N{'+1' if s else ''}": {"n": len(v), "mean_abs_deg": round(st.mean(v), 4),
                                               "max_abs_deg": round(max(v), 4)} for s, v in ye.items() if v},
    }

    # ---- per-trial analysis
    by_cond = {}
    for tr in trials:
        if "recs" not in tr:
            continue
        by_cond.setdefault(tr["cond"], []).append(tr)
    cond_out = {}
    all_low, all_mid, all_spr, all_dec, crouch_dec = [], [], [], [], []
    thresholds = {"low_max_s0": [], "mid_min_s0": [], "mid_max_s0": [], "spr_min_s0": []}
    for cond, trs in sorted(by_cond.items()):
        rows_c = []
        for tr in trs:
            recs = tr["recs"]
            press, release = segment(recs)
            tt = times(recs, press)
            tr["press"], tr["release"], tr["t"] = press, release, tt
            # terminal speed: last CRUISE_S of hold
            t_rel = tt[release - 1]
            cruise = [x["s1"] for i, x in enumerate(recs[press:release], press) if tt[i] > t_rel - CRUISE_S]
            ac = accel_commands(recs, press, release)
            # first-pass rates by speed band from the session census (only to seed the classifier)
            c = tr["census"]
            m = recs[press]["msc"]
            bands = classify_bands(ac, c.get("lowAcceleration", 2500) * m, c.get("acceleration", 450) * m,
                                   c.get("sprintAcceleration", 100) * m if cond in ("e1_sprint", "e1_turn") else None)
            a_low, a_mid, a_spr = ratio_fit(bands["low"]), ratio_fit(bands["mid"]), ratio_fit(bands["sprint"])
            all_low += bands["low"]
            all_mid += bands["mid"]
            all_spr += bands["sprint"]
            if bands["low"]:
                thresholds["low_max_s0"].append(max(x["s0"] for x in bands["low"]))
            if bands["mid"]:
                thresholds["mid_min_s0"].append(min(x["s0"] for x in bands["mid"]))
                thresholds["mid_max_s0"].append(max(x["s0"] for x in bands["mid"]))
            if bands["sprint"]:
                thresholds["spr_min_s0"].append(min(x["s0"] for x in bands["sprint"]))
            dc = decel_commands(recs, release)
            if cond == "e1_crouch":
                crouch_dec.extend(dc)
            else:
                all_dec.extend(dc)
            d_fit = -ratio_fit(dc) if dc else None
            # per-command residuals of the constant-rate fits
            res_a = [((x["s1"] - x["s0"]) / x["dt"]) for x in bands["mid"]]
            # stop: time and commands from release to zero
            stop_i = next((i for i in range(release, len(recs)) if recs[i]["s1"] == 0.0), None)
            hold_peak = max(x["s1"] for x in recs[press:release])
            t_cap = next((tt[i] for i in range(press, release) if recs[i]["s1"] >= recs[i]["ms"] - CLAMP_TOL), None)
            # direction of motion vs +X during cruise
            hd = [x["heading"] for x in recs[press:release] if x["heading"] is not None]
            row = {
                "run": tr["run"], "fps": tr["fps"], "press_cmd": recs[press]["cmd"], "release_cmd": recs[release]["cmd"],
                "hold_s": round(t_rel, 4), "first_cmd_fwd_sd": [recs[press]["fwd"], recs[press]["sd"]],
                "maxspeed": sorted({x["ms"] for x in recs[press:release]}), "movescale": sorted({x["msc"] for x in recs}),
                "terminal_speed": round(st.mean(cruise), 4), "terminal_sd": round(st.pstdev(cruise), 5), "n_cruise": len(cruise),
                "peak_speed": round(hold_peak, 4),
                "t_to_cap_s": round(t_cap, 4) if t_cap is not None else None,
                "accel_low": a_low and round(a_low, 3), "n_low": len(bands["low"]),
                "accel_mid": a_mid and round(a_mid, 3), "n_mid": len(bands["mid"]),
                "accel_sprint": a_spr and round(a_spr, 3), "n_sprint": len(bands["sprint"]),
                "accel_mid_per_cmd_sd": round(st.pstdev(res_a), 3) if len(res_a) > 1 else None,
                "decel": d_fit and round(d_fit, 3), "n_decel": len(dc),
                "speed_at_release": round(recs[release]["s0"], 4),
                "stop_cmds": (stop_i - release + 1) if stop_i is not None else None,
                "stop_s": round(tt[stop_i] - t_rel, 4) if stop_i is not None else None,
                "heading_deg_range": [round(min(hd), 4), round(max(hd), 4)] if hd and cond != "e1_turn" else None,
            }
            # sprint flag timing
            if cond in ("e1_sprint", "e1_turn"):
                spr_on = next((i for i in range(press, release) if recs[i]["spr"]), None)
                spd_in = next((i for i in range(press - 1, release) if recs[i]["b"] & IN_SPEED), None)
                row["sprint_flag_cmds_after_press"] = (spr_on - press) if spr_on is not None else None
                row["speed_button_cmd_offset"] = (spd_in - press) if spd_in is not None else None
                sb = bands["sprint"]
                if sb:
                    i0 = recs.index(sb[0])
                    row["sprint_band_start_s"] = round(tt[i0 - 1], 4)
                    early = [x for x in sb if tt[recs.index(x)] - tt[i0 - 1] <= 0.2]
                    late = [x for x in sb if tt[recs.index(x)] - tt[i0 - 1] > 0.2]
                    row["sprint_accel_first_0p2s"] = early and round(ratio_fit(early), 3)
                    row["sprint_accel_after_0p2s"] = late and round(ratio_fit(late), 3)
            if cond == "e1_crouch":
                duck_on = next((i for i, x in enumerate(recs) if x["b"] & IN_DUCK), None)
                row["duck_states_before_press"] = sorted({x["duck"] for x in recs[duck_on:press]}) if duck_on is not None else None
                d2 = next((i for i in range(duck_on, len(recs)) if recs[i]["duck"] == 2), None) if duck_on is not None else None
                row["duck_full_after_s"] = round(sum(recs[i]["dt"] for i in range(duck_on, d2)), 4) if d2 is not None else None
                row["maxspeed_before_duck"] = recs[0]["ms"]
            rows_c.append(row)
        agg = {}
        for k in ("terminal_speed", "accel_low", "accel_mid", "accel_sprint", "decel", "stop_s", "t_to_cap_s"):
            vals = [r[k] for r in rows_c if r.get(k) is not None]
            if vals:
                agg[k] = summ(vals, 4)
        cond_out[cond] = {"trials": rows_c, "agg": agg}
    res["conditions"] = cond_out
    res["band_thresholds_s0"] = {k: [round(min(v), 3), round(max(v), 3)] if v else None for k, v in thresholds.items()}
    res["pooled_rates"] = {"low": ratio_fit(all_low), "mid": ratio_fit(all_mid), "sprint": ratio_fit(all_spr),
                           "decel": -ratio_fit(all_dec), "crouch_decel": -ratio_fit(crouch_dec) if crouch_dec else None,
                           "n": [len(all_low), len(all_mid), len(all_spr), len(all_dec), len(crouch_dec)],
                           "note": "decel pools the standing conditions; crouch is separate"}

    # ---- decel model comparison (pooled, per command)
    const = res["pooled_rates"]["decel"]
    e_const = [(x["s0"] - x["s1"]) - const * x["dt"] for x in all_dec]
    sp, f, rms_src = fit_source_friction(all_dec, [10 * i for i in range(0, 41)], None)
    # Source with a typical stopspeed fixed at 100 u/s (friction fitted)
    sp100, f100, rms100 = fit_source_friction(all_dec, [100.0], None)
    # per-speed-band decel rate (does the drop rate depend on speed?)
    bands_dec = {}
    for lo in range(0, 300, 50):
        b = [x for x in all_dec if lo <= x["s0"] < lo + 50]
        if b:
            bands_dec[f"{lo}-{lo + 50}"] = {"n": len(b), "rate": round(-ratio_fit(b), 3)}
    res["decel_models"] = {
        "constant": {"D": round(const, 3), "rms_per_cmd_drop": round(math.sqrt(st.mean([e * e for e in e_const])), 5),
                     "max_abs": round(max(abs(e) for e in e_const), 5), "n": len(all_dec)},
        "source_friction_best": {"stopspeed": sp, "friction": round(f, 4), "rms_per_cmd_drop": round(rms_src, 5),
                                 "note": "grid stopspeed 0..400 step 10; at the top of the grid the model is constant decel"},
        "source_friction_stop100": {"stopspeed": 100, "friction": round(f100, 4), "rms_per_cmd_drop": round(rms100, 5)},
        "rate_by_speed_band": bands_dec,
    }

    # ---- stop snap: would-be post speeds of the zeroing command vs. the smallest kept post speed
    zeroed, kept = [], []
    for cond, trs in by_cond.items():
        D = res["pooled_rates"]["crouch_decel"] if cond == "e1_crouch" else res["pooled_rates"]["decel"]
        for tr in trs:
            for x in tr["recs"][tr["release"]:]:
                if x["dt"] is None or x["s0"] == 0.0 or x["b"] & MOVE_BITS:
                    continue
                (zeroed if x["s1"] == 0.0 else kept).append(x["s0"] - D * x["dt"] if x["s1"] == 0.0 else x["s1"])
    res["stop_snap"] = {"max_wouldbe_speed_zeroed": round(max(zeroed), 4), "min_kept_post_speed": round(min(kept), 4),
                        "n_zeroing_cmds": len(zeroed), "n_zeroed_with_wouldbe_positive": sum(z > 0 for z in zeroed)}

    # ---- accel model comparison: closed-loop simulation per trial
    c = census
    m = 1.15
    chosen = {"speed": c["speed"], "sprintspeed": c["sprintspeed"], "acceleration": c["acceleration"],
              "lowSpeed": c["lowSpeed"], "lowAcceleration": c["lowAcceleration"],
              "sprintAcceleration": c["sprintAcceleration"], "deceleration": c["deceleration"],
              "sprintDeceleration": c["sprintDeceleration"],
              "crouch_deceleration": res["pooled_rates"]["crouch_decel"], "stop_snap_speed": 1.0}
    crouch_caps = sorted({x["ms"] for tr in by_cond.get("e1_crouch", []) for x in tr["recs"][tr["press"]:tr["release"]]})
    msc_all = sorted({x["msc"] for tr in trials if "recs" in tr for x in tr["recs"]})
    chosen["crouch_speed"] = crouch_caps[0] / msc_all[0] if crouch_caps and len(msc_all) == 1 else float("nan")
    # single-rate alternative: one accel fitted over all non-clamped accel commands of walk-like conditions
    walk_like = [x for cond in ("e1_walk", "e1_back", "e1_side", "e1_diag") for tr in by_cond.get(cond, [])
                 for x in accel_commands(tr["recs"], tr["press"], tr["release"])]
    a_single = ratio_fit(walk_like)
    sim = {}
    for cond, trs in sorted(by_cond.items()):
        stance = "crouch" if cond == "e1_crouch" else "stand"
        per = []
        for tr in trs:
            recs, p = tr["recs"], tr["press"]
            obs = [x["s1"] for x in recs[p:]]
            pr = simulate(recs, p, chosen, stance)
            r_c = rms(pr, obs)
            prm = dict(chosen, lowAcceleration=chosen["acceleration"])  # no low-speed branch
            r_nolow = rms(simulate(recs, p, prm, stance), obs)
            pr1 = simulate_single(recs, p, a_single, const)
            r_1 = rms(pr1, obs)
            prs = dict(chosen, sprintAcceleration=100.0)  # the T0-smoke census value
            r_s100 = rms(simulate(recs, p, prs, stance), obs) if cond in ("e1_sprint", "e1_turn") else None
            pnl = dict(chosen, sprint_lookahead=False)
            r_nl = rms(simulate(recs, p, pnl, stance), obs) if cond in ("e1_sprint", "e1_turn") else None
            pdm = dict(chosen, deceleration=chosen["deceleration"] * m)  # decel also scaled by movescale
            r_decm = rms(simulate(recs, p, pdm, stance), obs)
            per.append({"run": tr["run"], "chosen_rms": round(r_c[0], 4), "chosen_max": round(r_c[1], 4),
                        "no_low_branch_rms": round(r_nolow[0], 3), "single_rate_rms": round(r_1[0], 3),
                        "sprintAccel100_rms": r_s100 and round(r_s100[0], 3),
                        "sprint_edge_at_speed_rms": r_nl and round(r_nl[0], 3), "sprint_edge_at_speed_max": r_nl and round(r_nl[1], 3),
                        "decel_times_msc_rms": round(r_decm[0], 3)})
            tr["pred"] = pr
        sim[cond] = per
    # open loop: one step from the OBSERVED pre-speed, for every command from the press on
    ol = {}
    edge_cases = []
    for cond, trs in sorted(by_cond.items()):
        stance = "crouch" if cond == "e1_crouch" else "stand"
        errs = []
        for tr in trs:
            for x in tr["recs"][tr["press"]:]:
                if x["dt"] is None or x["ground"] != 1:
                    continue
                pr1 = step(x, chosen, stance)
                errs.append(pr1 - x["s1"])
                if cond in ("e1_sprint", "e1_turn") and x["spr"] and x["b"] & MOVE_BITS and 185 <= x["s0"] < 201:
                    simple = step(x, dict(chosen, sprint_lookahead=False), stance)
                    edge_cases.append({"run": tr["run"], "s0": round(x["s0"], 3), "s1": round(x["s1"], 3), "dt": x["dt"],
                                       "err_lookahead": round(pr1 - x["s1"], 4), "err_edge_at_speed": round(simple - x["s1"], 4)})
        ol[cond] = {"n": len(errs), "rms": round(math.sqrt(st.mean([e * e for e in errs])), 5),
                    "max_abs": round(max(abs(e) for e in errs), 5), "n_over_0p05": sum(abs(e) > 0.05 for e in errs)}
    near = [e for e in edge_cases if 197.5 <= e["s0"] <= 199.6]
    res["open_loop"] = {"per_condition": ol, "sprint_edge_commands": near,
                        "sprint_edge_summary": {
                            "commands_s0_185_201": len(edge_cases),
                            "lookahead_misses_over_0p05": sum(abs(e["err_lookahead"]) > 0.05 for e in edge_cases),
                            "edge_at_speed_misses_over_0p05": sum(abs(e["err_edge_at_speed"]) > 0.05 for e in edge_cases)}}
    res["closed_loop"] = {"single_rate_accel": round(a_single, 3), "per_condition": sim,
                          "note": "speed RMS / max |error| (u/s) of a closed-loop speed simulation from the press "
                                  "using observed dt and input bits, against observed post speed, to the end of the trial"}

    # ---- diagonal / direction
    dirs = {}
    for cond in ("e1_walk", "e1_back", "e1_side", "e1_diag"):
        for tr in by_cond.get(cond, []):
            recs = tr["recs"]
            errs = []
            for x in recs[tr["press"]:tr["release"]]:
                if x["heading"] is None or x["yaw"] is None:
                    continue
                w = wish_yaw(x["yaw"], x["fwd"], x["sd"])
                if w is not None:
                    errs.append(abs(angdiff(x["heading"], w)))
            dirs.setdefault(cond, []).append(round(max(errs), 4) if errs else None)
    res["direction_heading_vs_wishdir_max_deg"] = dirs

    # ---- turning
    turn = []
    for tr in by_cond.get("e1_turn", []):
        recs = tr["recs"]
        TURN = 1 << 8   # bit seen while +right is held (IN_RIGHT in Source in_buttons.h)
        on = [i for i, x in enumerate(recs) if x["b"] & TURN]
        if not on:
            turn.append({"run": tr["run"], "error": "no turn bit"})
            continue
        i0, i1 = on[0], on[-1]
        rates, errs, spd = [], [], []
        for i in range(i0, i1 + 1):
            x, prev = recs[i], recs[i - 1]
            if x["yaw"] is not None and prev["yaw"] is not None:
                rates.append(angdiff(x["yaw"], prev["yaw"]) / x["dt"])
            if x["heading"] is not None:
                errs.append(abs(angdiff(x["heading"], x["yaw"])))
            spd.append(x["s1"])
        y_start = recs[i0 - 1]["yaw"]
        y_end = recs[i1]["yaw"]
        post = [abs(angdiff(x["heading"], x["yaw"])) for x in recs[i1 + 1:tr["release"]] if x["heading"] is not None]
        speeds_before = [x["s1"] for x in recs[i0 - 20:i0]]
        turn.append({
            "run": tr["run"], "turn_cmds": i1 - i0 + 1, "turn_s": round(sum(recs[i]["dt"] for i in range(i0, i1 + 1)), 4),
            "yaw_total_deg": round(sum(angdiff(recs[i]["yaw"], recs[i - 1]["yaw"]) for i in range(i0, i1 + 1)), 3),
            "yaw_start_end": [y_start, y_end],
            "yaw_rate_mean_dps": round(st.mean(rates), 3), "yaw_rate_sd": round(st.pstdev(rates), 3),
            "yaw_rate_median_dps": round(st.median(rates), 3),
            "yaw_rate_first_cmd_dps": round(rates[0], 3),
            "yaw_rate_after_first_sd": round(st.pstdev(rates[1:]), 3),
            "yaw_rate_min": round(min(rates), 3), "yaw_rate_max": round(max(rates), 3),
            "heading_minus_yaw_max_deg": round(max(errs), 4), "heading_minus_yaw_mean_deg": round(st.mean(errs), 5),
            "speed_before": round(st.mean(speeds_before), 4), "speed_min_in_turn": round(min(spd), 4),
            "speed_max_in_turn": round(max(spd), 4), "speed_loss_pct": round(100 * (1 - min(spd) / st.mean(speeds_before)), 4),
            "after_turn_heading_minus_yaw_max_deg": round(max(post), 4) if post else None,
        })
    res["turn"] = {"per_trial": turn,
                   "yaw_rate": summ([t["yaw_rate_median_dps"] for t in turn if "yaw_rate_median_dps" in t], 3),
                   "yaw_total": summ([abs(t["yaw_total_deg"]) for t in turn if "yaw_total_deg" in t], 3)}

    # ---- dedi agreement (same usercmds, post-state)
    # (cheap: compare joined dedi rows when derive joined them)
    res["dedi_check"] = DEDI_STATS

    # ---- acceptance
    acc = {}
    for cond, co in cond_out.items():
        a = co["agg"]
        acc[cond] = {"terminal_speed_spread_pct": a["terminal_speed"]["spread_pct"],
                     "terminal_pass_2pct": a["terminal_speed"]["spread_pct"] <= 2.0}
        for k in ("accel_low", "accel_mid", "accel_sprint", "decel"):
            if k in a and a[k]["n"] > 1:
                acc[cond][f"{k}_spread_pct"] = a[k]["spread_pct"]
                acc[cond][f"{k}_pass_5pct"] = a[k]["spread_pct"] <= 5.0
    res["acceptance"] = acc

    # ---- curves
    for cond, trs in sorted(by_cond.items()):
        series = []
        with open(os.path.join(outdir, f"curves_{cond}.csv"), "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh)
            w.writerow(["cond", "run", "k", "t_s", "speed", "model_speed", "held", "sprint", "duck", "yaw"])
            for tr in trs:
                recs, p = tr["recs"], tr["press"]
                pts = []
                for k, x in enumerate(recs[p - 10:], p - 10):
                    t = tr["t"][k] if k >= p else -sum(recs[j]["dt"] for j in range(k + 1, p))
                    mp = tr["pred"][k - p] if p <= k < p + len(tr["pred"]) else ""
                    w.writerow([cond, tr["run"], k - p, f"{t:.5f}", f"{x['s1']:.3f}",
                                f"{mp:.3f}" if mp != "" else "", int(bool(x["b"] & MOVE_BITS)), x["spr"], x["duck"],
                                "" if x["yaw"] is None else f"{x['yaw']:.3f}"])
                    pts.append((t, x["s1"]))
                series.append((tr["run"], pts))
        tr0 = trs[0]
        model = [(tr0["t"][k], v) for k, v in zip(range(tr0["press"], len(tr0["recs"])), tr0["pred"])]
        svg_curves(os.path.join(outdir, f"curves_{cond}.svg"), f"{cond}: observed (5 trials) vs model", series, model)

    return res, chosen, cond_out, by_cond


DEDI_STATS = {}


def dedi_check(folder):
    """Max |post-state difference| between client and joined dedi MT rows of the E1 runs."""
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    runs = {f"r{i}" for i in range(301, 336)}
    n = ok = 0
    mx = 0.0
    for r in rows:
        if r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay") and r.get("drv_run") in runs:
            n += 1
            p = r.get("_join")
            if p is None:
                continue
            ok += 1
            for k in ("pox", "poy", "poz", "pvx", "pvy", "pvz"):
                mx = max(mx, abs(p[k] - r[k]))
    return {"client_cmds": n, "joined": ok, "max_abs_post_diff": mx}


def build_params(res, chosen, census):
    pr = res["pooled_rates"]
    co = res["conditions"]

    def agg(cond, key):
        a = co.get(cond, {}).get("agg", {}).get(key)
        return a

    def p(value, unit, source, formula, n=None, spread=None, extra=None):
        d = {"value": value, "unit": unit, "source": source, "formula": formula}
        if n is not None:
            d["n_trials"] = n
        if spread is not None:
            d["spread_pct"] = spread
        if extra:
            d.update(extra)
        return d

    acc_ns = [agg(c, "accel_mid") for c in ("e1_walk", "e1_sprint", "e1_back", "e1_side", "e1_diag", "e1_turn")]
    low_ns = [agg(c, "accel_low") for c in ("e1_walk", "e1_sprint", "e1_crouch", "e1_back", "e1_side", "e1_diag", "e1_turn")]
    dec_ns = [agg(c, "decel") for c in ("e1_walk", "e1_sprint", "e1_back", "e1_side", "e1_diag", "e1_turn")]

    def pooled_spread(aggs):
        vals = [a["min"] for a in aggs if a] + [a["max"] for a in aggs if a]
        return round(spread(vals), 3) if vals else None

    ntr = sum(len(v["trials"]) for v in co.values())
    F_ACC = "if held and s < cap: s = min(cap, s + a*dt) with a chosen from the pre-move speed s: "             "lowAcceleration*msc if s < lowSpeed*msc; else acceleration*msc if not sprinting or "             "s + sprintAcceleration*msc*dt < speed*msc; else sprintAcceleration*msc"
    F_DEC = "if no move input: s = max(0, s - deceleration*dt)  (NOT scaled by movescale)"
    F_DIR = "v = s * wishdir; wishdir = normalize(fwd*forward(yaw) + side*right(yaw)) (horizontal; instant redirect)"
    out = {
        "_doc": "M2/E1 ground model parameters. 'source' says where the value comes from: census = the session's "
                "client class var (E0 dump), fitted = this analysis. spread_pct = (max-min)/mean over per-trial fits, "
                "pooled across the conditions where the parameter applies.",
        "movescale": p(1.15, "-", "observed MOVE-TRACE msc (constant in every E1 command)",
                       "multiplies speed, sprintspeed, crouch speed, lowSpeed, lowAcceleration, acceleration, sprintAcceleration"),
        "speed": p(chosen["speed"], "u/s", "census speed; fitted terminal walk speed / msc",
                   "cap = speed*msc (stand, not sprinting)", n=len(co["e1_walk"]["trials"]),
                   spread=agg("e1_walk", "terminal_speed")["spread_pct"],
                   extra={"fitted_terminal": agg("e1_walk", "terminal_speed")["mean"]}),
        "sprintspeed": p(chosen["sprintspeed"], "u/s", "census sprintspeed; fitted terminal sprint speed / msc",
                         "cap = sprintspeed*msc while the sprint flag is set", n=len(co["e1_sprint"]["trials"]),
                         spread=agg("e1_sprint", "terminal_speed")["spread_pct"],
                         extra={"fitted_terminal": agg("e1_sprint", "terminal_speed")["mean"]}),
        "crouch_speed": p(round(chosen["crouch_speed"], 4), "u/s", "fitted: observed crouch maxspeed / msc (no census key read)",
                          "cap = crouch_speed*msc while ducked", n=len(co["e1_crouch"]["trials"]),
                          spread=agg("e1_crouch", "terminal_speed")["spread_pct"],
                          extra={"fitted_terminal": agg("e1_crouch", "terminal_speed")["mean"]}),
        "lowSpeed": p(chosen["lowSpeed"], "u/s", "census lowSpeed; fitted band edge (bracketed)", F_ACC,
                      extra={"observed_edge_bracket_u_s": [res["band_thresholds_s0"]["low_max_s0"][1],
                                                           res["band_thresholds_s0"]["mid_min_s0"][0]],
                             "model_edge_u_s": chosen["lowSpeed"] * 1.15}),
        "lowAcceleration": p(chosen["lowAcceleration"], "u/s^2", "census lowAcceleration; fitted pooled rate / msc", F_ACC,
                             n=ntr, spread=pooled_spread(low_ns), extra={"fitted_pooled": round(pr["low"], 3)}),
        "acceleration": p(chosen["acceleration"], "u/s^2", "census acceleration; fitted pooled rate / msc", F_ACC,
                          n=sum(a["n"] for a in acc_ns if a), spread=pooled_spread(acc_ns),
                          extra={"fitted_pooled": round(pr["mid"], 3)}),
        "sprintAcceleration": p(chosen["sprintAcceleration"], "u/s^2",
                                "census sprintAcceleration of THIS session (102; the T0 smoke census had 100); fitted pooled rate / msc",
                                F_ACC, n=sum(a["n"] for a in (agg("e1_sprint", "accel_sprint"), agg("e1_turn", "accel_sprint")) if a),
                                spread=pooled_spread([agg("e1_sprint", "accel_sprint"), agg("e1_turn", "accel_sprint")]),
                                extra={"fitted_pooled": round(pr["sprint"], 3)}),
        "deceleration": p(chosen["deceleration"], "u/s^2", "census deceleration; fitted pooled constant rate", F_DEC,
                          n=sum(a["n"] for a in dec_ns if a), spread=pooled_spread(dec_ns),
                          extra={"fitted_pooled": round(pr["decel"], 3)}),
        "sprintDeceleration": p(chosen["sprintDeceleration"], "u/s^2",
                                "census only; indistinguishable from deceleration here (both 1250; sprint stop fitted with the same rate)",
                                F_DEC, n=len(co["e1_sprint"]["trials"]), spread=agg("e1_sprint", "decel")["spread_pct"],
                                extra={"fitted_sprint_stop": agg("e1_sprint", "decel")["mean"]}),
        "crouch_deceleration": p(round(pr["crouch_decel"], 3), "u/s^2",
                                 "fitted (crouch trials; no crouch census key was read)",
                                 "while ducked with no move input: s = max(0, s - crouch_deceleration*dt) (not scaled by movescale)",
                                 n=len(co["e1_crouch"]["trials"]), spread=agg("e1_crouch", "decel")["spread_pct"]),
        "stop_snap_speed": p(1.0, "u/s", "assumed Source WalkMove value (speed < 1 -> 0); data bracket it",
                             "after decel: if s < stop_snap_speed: s = 0",
                             n=sum(len(v["trials"]) for v in co.values()),
                             extra={"observed_bracket_u_s": [res["stop_snap"]["max_wouldbe_speed_zeroed"],
                                                             res["stop_snap"]["min_kept_post_speed"]]}),
        "speedScaleBack": p(census.get("speedScaleBack"), "-", "census; back terminal speed equals walk", "cap *= speedScaleBack when moving back (1 here)",
                            n=len(co["e1_back"]["trials"]), spread=agg("e1_back", "terminal_speed")["spread_pct"],
                            extra={"fitted_terminal": agg("e1_back", "terminal_speed")["mean"]}),
        "speedScaleSide": p(census.get("speedScaleSide"), "-", "census; side terminal speed equals walk", "cap *= speedScaleSide when strafing (1 here)",
                            n=len(co["e1_side"]["trials"]), spread=agg("e1_side", "terminal_speed")["spread_pct"],
                            extra={"fitted_terminal": agg("e1_side", "terminal_speed")["mean"]}),
        "direction": p("normalized wishdir, instant redirect", "-", "fitted (heading = wishdir; diagonal speed = walk speed; turn keeps speed)", F_DIR,
                       n=len(co["e1_diag"]["trials"]) + len(co["e1_turn"]["trials"])),
        "yaw_rate_turn_key": p(res["turn"]["yaw_rate"]["mean"], "deg/s", "fitted from HSD yaw (+right console turn); a cl_yawspeed-type client setting, not movement physics",
                               "yaw -= rate*dt while +right is held", n=res["turn"]["yaw_rate"]["n"],
                               spread=res["turn"]["yaw_rate"]["spread_pct"]),
        "sprintStartDelay": p(census.get("sprintStartDelay"), "s", "census only; no effect on the speed curve was found",
                              "not used by the speed model (sprint band starts when s >= speed*msc; see GROUND-MODEL.md)"),
        "sprintStartDuration": p(census.get("sprintStartDuration"), "s", "census only; no effect on the speed curve was found", "not used"),
        "sprintStartFastDuration": p(census.get("sprintStartFastDuration"), "s", "census only; no effect on the speed curve was found", "not used"),
        "sprintEndDuration": p(census.get("sprintEndDuration"), "s", "census only; not exercised (sprint and forward were released together)", "not used"),
    }
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    for f in a.sessions:
        DEDI_STATS[os.path.basename(os.path.normpath(f))] = dedi_check(f)
    res, chosen, cond_out, by_cond = analyse(a.sessions, a.out)
    census = load_census(a.sessions[0])
    params = build_params(res, chosen, census)
    with open(os.path.join(a.out, "results.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, default=lambda o: round(o, 6) if isinstance(o, float) else str(o))
    with open(os.path.join(a.out, "params.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(params, fh, indent=1)
    # console summary
    print("join:", res["join"]["total"], "single-offset trials", res["join"]["single_offset_trials"], "/", res["join"]["trials"])
    for k, v in res["dt_validation"].items():
        print("dt", k, v)
    for cond, co in sorted(cond_out.items()):
        print(cond, json.dumps(co["agg"]))
    print("pooled", res["pooled_rates"])
    print("decel models", json.dumps(res["decel_models"]))
    print("closed loop", json.dumps(res["closed_loop"]))
    print("turn", json.dumps(res["turn"]))
    print("dirs", res["direction_heading_vs_wishdir_max_deg"])
    print("dedi", res["dedi_check"])
    print("acceptance", json.dumps(res["acceptance"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
