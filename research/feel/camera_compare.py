"""F4 camera feel comparison: lay the Unity native camera (CameraFeelBatch) over R5's camera (camera_to_trial.py camera.csv), metric by metric.

Usage: camera_compare.py <camera_out_dir> <trials_dir> [--json out.json] [--export dir]
  <camera_out_dir>  CameraFeelBatch output: <trial_id>/reference.csv
  <trials_dir>      camera_to_trial.py output: <trial_id>/{trial.json, samples.csv, camera.csv}
Both sides are what the camera ADDS to the aim (Source degrees: pitch + = down, roll + = bank right), the eye height above the origin and
the FOV scale. Drops are aligned on the landing (trial.json camera_align); the other trials share the trial's row time.
--export adds kind "camera" rows to an existing feel_compare.py export (scorecard.json, trials.json) and writes series_camera.json.
stdlib only.
"""
import csv
import json
import math
import os
import sys

FRAME = 1 / 120
ANG = (0.3, 0.10)            # degrees: within max(0.3, 10 %) agrees (the punch has a random part per landing, C3 §2)
TOL = {"kick_peak": ANG, "kick_t_peak": (FRAME * 2, 0.10), "kick_t_zero": (FRAME * 3, 0.10), "kick_roll": ANG,
       "slide_eye_min": (1.0, 0.0), "slide_t_eye": (FRAME * 3, 0.10), "slide_roll": ANG, "slide_fov": (0.005, 0.0),
       "turn_roll_peak": ANG, "turn_roll_end": ANG, "bob_pitch_p2p": (0.05, 0.10), "bob_yaw_p2p": (0.05, 0.10), "bob_period": (FRAME * 3, 0.05)}
NAME_ZH = {"kick_peak": "落地 kick 俯仰峰值", "kick_t_peak": "kick 到峰值用时", "kick_t_zero": "kick 回到零的时刻", "kick_roll": "落地后横滚峰值",
           "slide_eye_min": "滑铲眼高最低", "slide_t_eye": "滑铲眼高下沉用时", "slide_roll": "滑铲横滚峰值", "slide_fov": "滑铲 FOV 倍数",
           "turn_roll_peak": "转向横滚峰值", "turn_roll_end": "转向结束时横滚", "bob_pitch_p2p": "跑步晃动俯仰幅度（峰峰）",
           "bob_yaw_p2p": "跑步晃动偏航幅度（峰峰）", "bob_period": "跑步晃动周期"}
UNIT = {k: ("s" if k.endswith(("t_peak", "t_zero", "t_eye", "period")) else "u" if k == "slide_eye_min" else "×" if k == "slide_fov" else "deg")
        for k in TOL}
COLS = ("pitch", "yaw", "roll", "eye", "fov")


def load(path):
    out = {k: [] for k in ("t",) + COLS + ("ground", "slide")}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            for k in out:
                out[k].append(float(r[k]))
    return out


def landing(tr):
    return next((i for i in range(1, len(tr["t"])) if not tr["ground"][i - 1] and tr["ground"][i]), None)


def at(tr, t):
    return min(range(len(tr["t"])), key=lambda i: abs(tr["t"][i] - t))


def kick(tr, li):
    """Landing kick: pitch relative to the frame before the landing, its peak, the time of the peak and of the first zero crossing after it,
    and the largest roll within 0.6 s."""
    t0, p0 = tr["t"][li - 1], tr["pitch"][li - 1]
    idx = [i for i in range(li - 1, len(tr["t"])) if tr["t"][i] - t0 <= 1.0]
    pk = max(idx, key=lambda i: abs(tr["pitch"][i] - p0))
    zero = next((tr["t"][i] - t0 for i in idx if i > pk and (tr["pitch"][i] - p0) * (tr["pitch"][pk] - p0) < 0), None)
    roll = max(abs(tr["roll"][i]) for i in idx if tr["t"][i] - t0 <= 0.6)
    return {"kick_peak": [tr["pitch"][pk] - p0], "kick_t_peak": [tr["t"][pk] - t0], "kick_t_zero": [zero] if zero is not None else [],
            "kick_roll": [roll]}


def slide(tr, press_t):
    idx = [i for i in range(len(tr["t"])) if press_t <= tr["t"][i] <= press_t + 1.2]
    if not idx:
        return {}
    eye_min = min(tr["eye"][i] for i in idx)
    t_eye = next(tr["t"][i] - press_t for i in idx if tr["eye"][i] <= eye_min + 0.05)
    return {"slide_eye_min": [eye_min], "slide_t_eye": [t_eye], "slide_roll": [max(abs(tr["roll"][i]) for i in idx)],
            "slide_fov": [max(tr["fov"][i] for i in idx)]}


def p2p(xs):
    return max(xs) - min(xs) if xs else 0.0


def bob(tr, a, b):
    """Step bob while running straight between times a and b: peak-to-peak pitch and yaw, and the period of the pitch (mean spacing of
    its upward crossings of the window mean, times two: the pitch bobs once per step, the step period is the reported one)."""
    idx = [i for i in range(len(tr["t"])) if a <= tr["t"][i] <= b]
    if len(idx) < 10:
        return {}
    ps = [tr["pitch"][i] for i in idx]
    m = sum(ps) / len(ps)
    ups = [tr["t"][idx[j]] for j in range(1, len(idx)) if ps[j - 1] < m <= ps[j]]
    out = {"bob_pitch_p2p": [p2p(ps)], "bob_yaw_p2p": [p2p([tr["yaw"][i] for i in idx])]}
    if len(ups) >= 3:
        out["bob_period"] = [(ups[-1] - ups[0]) / (len(ups) - 1)]
    return out


def inputs(trial_dir):
    rows = list(csv.DictReader(open(os.path.join(trial_dir, "samples.csv"), encoding="utf-8")))
    return [(float(r["t"]), float(r["cmd_fwd"]), float(r["in_yaw"]), int(r["in_duck"]), int(r["in_sprint"])) for r in rows]


def metrics(tr, inp, sched):
    m = {}
    li = landing(tr)
    if li is not None and (sched.startswith("c3_drop") or sched.startswith("c3_jumpland")):
        m.update(kick(tr, li))
    if "slide" in sched:
        press = next((t for (t, _, _, d, _), (_, _, _, d0, _) in zip(inp[1:], inp) if d and not d0), None)
        if press is not None:
            m.update(slide(tr, press))
    if "turn" in sched or sched == "n6_strafe":
        ys = [y for _, _, y, _, _ in inp]
        moving = [i for i in range(1, len(ys)) if abs(ys[i] - ys[i - 1]) > 1e-6]
        if moving:
            a, b = inp[moving[0]][0], inp[moving[-1]][0]
            idx = [i for i in range(len(tr["t"])) if a <= tr["t"][i] <= b + 0.05]
            if idx:
                m["turn_roll_peak"] = [max((tr["roll"][i] for i in idx), key=abs)]
                m["turn_roll_end"] = [tr["roll"][at(tr, b)]]
            run0 = next((t for t, f, _, _, s in inp if f > 0 and s), None)
            if run0 is not None and a - run0 > 0.7:
                m.update(bob(tr, run0 + 0.4, a - 0.02))   # steady sprint (or walk) before the turn
    return m


def verdict(k, a, b):
    if len(a) != len(b):
        return "count", None
    if not a:
        return None, None
    ab, rel = TOL[k]
    w = max(abs(y - x) / max(ab, rel * abs(x)) for x, y in zip(a, b))
    return ("agree" if w <= 1 else "close" if w <= 3 else "differ"), w


def family(man):
    return man.get("schedule", "camera")


def main():
    args = sys.argv[1:]
    out_json = out_export = None
    if "--json" in args:
        i = args.index("--json"); out_json = args[i + 1]; del args[i:i + 2]
    if "--export" in args:
        i = args.index("--export"); out_export = args[i + 1]; del args[i:i + 2]
    cam_dir, trials_dir = args[0], args[1]
    results, series = [], {}
    for name in sorted(os.listdir(trials_dir)):
        d = os.path.join(trials_dir, name)
        if not os.path.isfile(os.path.join(d, "camera.csv")):
            continue
        man = json.load(open(os.path.join(d, "trial.json"), encoding="utf-8"))
        sched = man.get("schedule", "")
        if "roll" in sched and sched.startswith("m9zd"):                 # zipline rides: the flat-floor body has no rope (not compared)
            continue
        u_csv = os.path.join(cam_dir, man["trial_id"], "reference.csv")
        if not os.path.isfile(u_csv):
            continue
        r5, ref = load(os.path.join(d, "camera.csv")), load(u_csv)
        if man.get("camera_align") == "landing":                        # shift R5 so its landing is at the Unity landing
            lr, lu = landing(r5), landing(ref)
            if lr is not None and lu is not None:
                dt = ref["t"][lu] - r5["t"][lr]
                r5["t"] = [t + dt for t in r5["t"]]
        inp = inputs(d)
        ms = {"r5": metrics(r5, inp, sched), "reference": metrics(ref, inp, sched)}
        keys = [k for k in TOL if k in ms["r5"] or k in ms["reference"]]
        for b in ms:
            for k in keys:
                ms[b].setdefault(k, [])
        res = {"trial": man["trial_id"], "family": family(man), "metrics": ms, "verdict": {"reference": {}}}
        for k in keys:
            v, w = verdict(k, ms["r5"][k], ms["reference"][k])
            if v:
                res["verdict"]["reference"][k] = [v, w]
        results.append(res)
        series[man["trial_id"]] = {b: {c: [round(x, 3) for x in tr[c][::2]] for c in ("t",) + COLS} for b, tr in (("r5", r5), ("reference", ref))}
    print(f"{len(results)} camera trials")
    agg = {}
    for r in results:
        for k, (v, _) in r["verdict"]["reference"].items():
            agg.setdefault(k, {}).setdefault(v, 0)
            agg[k][v] += 1
    for k in TOL:
        if k in agg:
            a = agg[k]
            print(f"  {k:16s} agree {a.get('agree', 0):3d}  close {a.get('close', 0):3d}  differ {a.get('differ', 0):3d}  count {a.get('count', 0):3d}")
    if out_json:
        json.dump(results, open(out_json, "w", encoding="utf-8"), indent=1)
    if out_export:
        export(results, series, out_export)


VZH = {"agree": "一致", "close": "接近", "differ": "不一致", "count": "次数不同", None: None}
RANK = {"agree": 0, "close": 1, "differ": 2, "count": 3}


def export(results, series, out_dir):
    sc_path, tr_path = os.path.join(out_dir, "scorecard.json"), os.path.join(out_dir, "trials.json")
    score = [r for r in json.load(open(sc_path, encoding="utf-8")) if r.get("kind") != "camera"]
    trials = [r for r in json.load(open(tr_path, encoding="utf-8")) if r.get("kind") != "camera"]
    for res in results:
        ms = res["metrics"]
        for k, (v, _) in res["verdict"]["reference"].items():
            n = max(len(ms["r5"][k]), len(ms["reference"][k]))
            for i in range(n):
                g = lambda b: round(ms[b][k][i], 4) if i < len(ms[b][k]) else None
                row = {"id": f"{res['trial']}/{k}/{i + 1}", "trial": res["trial"], "family": res["family"], "climb": False, "kind": "camera",
                       "metric": k, "metric_zh": NAME_ZH[k], "unit": UNIT[k], "k": i + 1, "r5": g("r5"), "replay": None, "reference": g("reference"),
                       "fun": None, "verdict_reference": v, "verdict_reference_zh": VZH[v], "verdict_replay": None, "verdict_replay_zh": None,
                       "delta_reference": None if g("r5") is None or g("reference") is None else round(g("reference") - g("r5"), 4), "delta_replay": None}
                score.append(row)
        worst = max((v for v, _ in res["verdict"]["reference"].values()), key=RANK.get, default="agree")
        trials.append({"trial": res["trial"], "family": res["family"], "climb": False, "kind": "camera", "duration": None,
                       "verdict_reference": worst, "verdict_replay": None, "verdict_fun": None, "verdict_reference_zh": VZH[worst],
                       "verdict_replay_zh": None, "path_rms_reference": None, "path_rms_replay": None, "path_rms_fun": None,
                       "jumps_r5": None, "jumps_reference": None})
    points = [{"trial": tid, "body": b, "t": s["t"][j], **{c: s[c][j] for c in COLS}}
              for tid, bodies in series.items() for b, s in bodies.items() for j in range(len(s["t"]))]
    for name, rows in (("scorecard", score), ("trials", trials), ("series_camera", points)):
        json.dump(rows, open(os.path.join(out_dir, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"{name}.json: {len(rows)} rows")


if __name__ == "__main__":
    main()
