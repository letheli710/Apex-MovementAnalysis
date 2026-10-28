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
       "turn_roll_peak": ANG, "turn_roll_end": ANG, "bob_pitch_p2p": (0.05, 0.10), "bob_yaw_p2p": (0.05, 0.10), "bob_period": (FRAME * 3, 0.05),
       "jump_kick_peak": ANG, "jump_kick_t_peak": (FRAME * 2, 0.10), "jump_kick_roll": ANG, "mantle_pitch_peak": ANG,
       "mantle_t_peak": (FRAME * 3, 0.10), "eye_stand": (1.0, 0.0), "eye_sprint": (1.0, 0.0), "zip_roll_peak": ANG, "zip_roll_end": ANG,
       "grapple_roll_peak": ANG, "grapple_roll_t_peak": (FRAME * 3, 0.10), "grapple_roll_rms": (0.5, 0.0)}
NAME_ZH = {"kick_peak": "落地 kick 俯仰峰值", "kick_t_peak": "kick 到峰值用时", "kick_t_zero": "kick 回到零的时刻", "kick_roll": "落地后横滚峰值",
           "slide_eye_min": "滑铲眼高最低", "slide_t_eye": "滑铲眼高下沉用时", "slide_roll": "滑铲横滚峰值", "slide_fov": "滑铲 FOV 倍数",
           "turn_roll_peak": "转向横滚峰值", "turn_roll_end": "转向结束时横滚", "bob_pitch_p2p": "跑步晃动俯仰幅度（峰峰）",
           "bob_yaw_p2p": "跑步晃动偏航幅度（峰峰）", "bob_period": "跑步晃动周期", "jump_kick_peak": "起跳 kick 俯仰峰值",
           "jump_kick_t_peak": "起跳 kick 到峰值用时", "jump_kick_roll": "起跳 kick 横滚峰值", "mantle_pitch_peak": "翻越时镜头俯仰峰值",
           "mantle_t_peak": "翻越俯仰峰值时刻（起跳后）", "eye_stand": "站立眼高", "eye_sprint": "冲刺眼高", "zip_roll_peak": "滑索横滚峰值",
           "zip_roll_end": "滑索转向结束时横滚", "grapple_roll_peak": "钩爪横滚峰值", "grapple_roll_t_peak": "钩爪横滚到峰值用时（按 Q 后）",
           "grapple_roll_rms": "钩爪横滚和 R5 的逐帧差（rms）"}
UNIT = {k: ("s" if k.endswith(("t_peak", "t_zero", "t_eye", "period")) else "u" if k.startswith(("slide_eye", "eye_")) else "×" if k == "slide_fov" else "deg")
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
    # F4 K-3: peak to peak per step (0.28 s) and per stride (0.56 s, the yaw cycle), median over the windows. The whole-window peak to peak
    # mixed slow drift into the bob and made the R5 sessions look different (0.53 / 0.60 / 0.73; per step they all give about 0.50).
    def per(col, w):
        vals, t = [], tr["t"][idx[0]]
        while t + w <= tr["t"][idx[-1]] + 1e-9:
            seg = [tr[col][i] for i in idx if t <= tr["t"][i] < t + w]
            if len(seg) > 5:
                vals.append(p2p(seg))
            t += w
        vals.sort()
        return [vals[len(vals) // 2]] if vals else []
    out = {"bob_pitch_p2p": per("pitch", 0.28), "bob_yaw_p2p": per("yaw", 0.56)}
    if len(ups) >= 3:
        out["bob_period"] = [(ups[-1] - ups[0]) / (len(ups) - 1)]
    return out


OFFHAND1 = 1 << 21


def grapple_press(trial_dir):
    """F7: the time of the first tactical (Q) press of a grapple trial."""
    rows = list(csv.DictReader(open(os.path.join(trial_dir, "samples.csv"), encoding="utf-8")))
    return next((float(r["t"]) for r in rows if int(r["buttons"]) & OFFHAND1), None)


def grapple_roll(tr, press, other=None):
    """F7 C-12: the roll from the Q press to 1.6 s after it (N12 §3's window): its signed peak, the time of the peak after the press and,
    with <other> (R5's trace), the rms of the difference on this trace's rows (the other trace sampled at the nearest row)."""
    idx = [i for i in range(len(tr["t"])) if press <= tr["t"][i] <= press + 1.6]
    if not idx:
        return {}
    pk = max(idx, key=lambda i: abs(tr["roll"][i]))
    out = {"grapple_roll_peak": [tr["roll"][pk]], "grapple_roll_t_peak": [tr["t"][pk] - press]}
    if other is not None:
        d = [tr["roll"][i] - other["roll"][at(other, tr["t"][i])] for i in idx]
        out["grapple_roll_rms"] = [math.sqrt(sum(x * x for x in d) / len(d))]
    return out


def inputs(trial_dir):
    rows = list(csv.DictReader(open(os.path.join(trial_dir, "samples.csv"), encoding="utf-8")))
    return [(float(r["t"]), float(r["cmd_fwd"]), float(r["in_yaw"]), int(r["in_duck"]), int(r["in_sprint"])) for r in rows]


def flags(trial_dir):
    """Per command: t, events, sprinting, crouched, jump key (R5's own flags: both bodies are scored on R5's timeline)."""
    rows = list(csv.DictReader(open(os.path.join(trial_dir, "samples.csv"), encoding="utf-8")))
    return [(float(r["t"]), r.get("events") or "", r.get("sprinting") == "1", (r.get("crouched") or "0") != "0", int(r["in_jump"]))
            for r in rows]


def first_takeoff(fl):
    t0 = next((t for t, ev, _, _, j in fl if "TAKEOFF" in ev and j), None)
    return t0 if t0 is not None else next((t for t, ev, *_ in fl if "TAKEOFF" in ev), None)


def takeoff_kick(tr, fl):
    """F4 K-5: the camera kick at the jump takeoff: pitch and roll change from the frame before, within 0.25 s."""
    t0 = first_takeoff(fl)
    if t0 is None:
        return {}
    i0 = max(0, at(tr, t0) - 1)
    p0, r0 = tr["pitch"][i0], tr["roll"][i0]
    idx = [i for i in range(i0, len(tr["t"])) if tr["t"][i] - t0 <= 0.25]
    pk = max(idx, key=lambda i: tr["pitch"][i] - p0)
    return {"jump_kick_peak": [tr["pitch"][pk] - p0], "jump_kick_t_peak": [tr["t"][pk] - t0],
            "jump_kick_roll": [max((tr["roll"][i] - r0 for i in idx), key=abs)]}


def mantle_hump(tr, fl):
    """F4 K-6: the pitch hump of the mantle after the jump, 0.25-1.2 s after the takeoff."""
    t0 = first_takeoff(fl)
    if t0 is None:
        return {}
    i0 = max(0, at(tr, t0) - 1)
    idx = [i for i in range(i0, len(tr["t"])) if 0.25 <= tr["t"][i] - t0 <= 1.2]
    if not idx:
        return {}
    pk = max(idx, key=lambda i: tr["pitch"][i])
    return {"mantle_pitch_peak": [tr["pitch"][pk] - tr["pitch"][i0]], "mantle_t_peak": [tr["t"][pk] - t0]}


def eyes(tr, fl):
    """F4 K-4: the median eye on the ground standing / walking (not sprinting, not crouched, for 0.5 s) and after 1.2 s of sprint."""
    out, stand, sprint = {}, [], []
    since_stand = since_sprint = 0.0
    last = None
    for t, ev, spr, cr, _ in fl:
        dt = t - last if last is not None else 0.0
        last = t
        since_sprint = since_sprint + dt if spr else 0.0
        since_stand = since_stand + dt if not spr and not cr else 0.0
        i = at(tr, t)
        if not tr["ground"][i]:
            continue
        if since_stand >= 0.5:
            stand.append(tr["eye"][i])
        if since_sprint >= 1.2:
            sprint.append(tr["eye"][i])
    for k, v in (("eye_stand", stand), ("eye_sprint", sprint)):
        if len(v) >= 5:
            v.sort()
            out[k] = [v[len(v) // 2]]
    return out


def metrics(tr, inp, sched, fl=None):
    m = {}
    if fl:
        m.update(eyes(tr, fl))
        if sched.startswith(("c3_jumpland", "b1_")):
            m.update(takeoff_kick(tr, fl))
        if sched.startswith("b1_") and "_none_" in sched:
            m.update(mantle_hump(tr, fl))
        if sched.startswith("m9zd"):
            ys = [y for _, _, y, _, _ in inp]
            moving = [i for i in range(1, len(ys)) if abs(ys[i] - ys[i - 1]) > 1e-6]
            if moving:
                a, b = inp[moving[0]][0], inp[moving[-1]][0]
                idx = [i for i in range(len(tr["t"])) if a <= tr["t"][i] <= b + 0.3]
                if idx:
                    m["zip_roll_peak"] = [max((tr["roll"][i] for i in idx), key=abs)]
                    m["zip_roll_end"] = [tr["roll"][at(tr, b)]]
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
        if sched.startswith("b1_") and "_none_" not in sched:           # B1 boost / superglide presses: R5 ran the S27 mantle-boost mod
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
        hooks = man.get("world", {}).get("hooks")
        if hooks is not None and not hooks:                             # F7: a grapple trial where R5's hook never attached (N12 y90)
            continue
        inp, fl = inputs(d), flags(d)
        ms = {"r5": metrics(r5, inp, sched, fl), "reference": metrics(ref, inp, sched, fl)}
        press = grapple_press(d) if hooks else None
        r5_roll = None
        if press is not None:
            # GN F-1: the measured roll of the look-away / rodeo clips is the hybrid (S21 client + local S3 dedi re-attaching); when
            # rea-native/n13/look_split.py --write left the client-only model (cut at the native view rule) in the trial folder, it is R5's roll
            cc = os.path.join(d, "camera_client.csv")
            if os.path.exists(cc):
                rows = list(csv.DictReader(open(cc, encoding="utf-8")))
                r5_roll = {"t": [press + float(r["t_press"]) for r in rows], "roll": [float(r["roll"]) for r in rows]}
            src = r5_roll or r5
            ms["r5"].update(grapple_roll(src, press, src))
            ms["reference"].update(grapple_roll(ref, press, src))
        keys = [k for k in TOL if k in ms["r5"] or k in ms["reference"]]
        for b in ms:
            for k in keys:
                ms[b].setdefault(k, [])
        res = {"trial": man["trial_id"], "family": family(man), "metrics": ms, "verdict": {"reference": {}}}
        if r5_roll is not None:
            res["r5_roll_ref"] = "client-only model (N13 F-1, look_split.py)"
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


# Metrics R5 shows and Unity does not model yet (the user decides, DECISIONS.md): their rows carry "pending" and stay out of the headline
PENDING = {"jump_kick_peak": "K-5", "jump_kick_t_peak": "K-5", "jump_kick_roll": "K-5", "mantle_pitch_peak": "K-6", "mantle_t_peak": "K-6"}
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
                if k in PENDING:
                    row["pending"] = PENDING[k]
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
