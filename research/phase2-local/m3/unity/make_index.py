"""Build m3/unity/index.md from the Unity batch-replay outputs (stdlib only).

Inputs (relative to this folder):
  <trial_id>/steps.csv, summary.json         M3 trials, R5MotorV2/m3 (after)
  before_m2model/<trial_id>/...              same trials, R5MotorV2/m2 (main branch, before)
  regression_m2_m1/<trial_id>/...            M2 + M1 trials, R5MotorV2/m3
  ../../m2/unity/<trial_id>/...              M2 + M1 trials, R5MotorV2/m2 (published M2 results)
  ../trials/<dir>/samples.csv, ../../m2/trials/<dir>/samples.csv   buttons (press edge)

    python make_index.py
"""
import csv, json, math, os, re, glob, filecmp
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
M3_TRIALS = os.path.join(HERE, "..", "trials")
M2_TRIALS = os.path.join(HERE, "..", "..", "m2", "trials")
M2_UNITY = os.path.join(HERE, "..", "..", "m2", "unity")
MOVE_KEYS = 0x618


def f(v, fmt="{:.3f}"):
    return "–" if v is None or (isinstance(v, float) and math.isnan(v)) else fmt.format(v)


def read_steps(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def press_steps(trial_dir):
    """Rows whose buttons gain a bit of 0x618 while the previous row was airborne (lurch candidates)."""
    tj = json.load(open(os.path.join(trial_dir, "trial.json")))
    prev = int(tj["initial_state"].get("buttons_held", 0) or 0)
    pg = int(tj["initial_state"].get("grounded", 1))
    out = []
    with open(os.path.join(trial_dir, "samples.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            b = int(r["buttons"] or 0)
            if (b & ~prev & MOVE_KEYS) and not pg:
                out.append((int(r["step"]), b & ~prev & MOVE_KEYS))
            prev = b
            pg = int(r["grounded"] or 1)
    return out


def jump_t(rows, press_idx):
    """Seconds from the start of the last takeoff step to the start of the press step (ref takeoff = jump command)."""
    j = None
    for i in range(press_idx, 0, -1):
        if rows[i]["ref_grounded"] == "0" and rows[i - 1]["ref_grounded"] == "1":
            j = i
            break
    if j is None:
        return None
    return sum(float(rows[k]["dt"]) for k in range(j, press_idx))


def hvec(r, who):
    return float(r[who + "_vel_x"]), float(r[who + "_vel_y"])


def ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def wrap(a):
    return (a + 180) % 360 - 180


def press_metrics(rows, p):
    """Heading error and velocity errors on the press step p."""
    r, q = rows[p], rows[p - 1]
    rv, sv = hvec(r, "ref"), hvec(r, "sim")
    rv0, sv0 = hvec(q, "ref"), hvec(q, "sim")
    head_err = wrap(ang(sv) - ang(rv))
    ref_turn = wrap(ang(rv) - ang(rv0))
    sim_turn = wrap(ang(sv) - ang(sv0))
    dref = (rv[0] - rv0[0], rv[1] - rv0[1])
    dsim = (sv[0] - sv0[0], sv[1] - sv0[1])
    dv_err = math.hypot(dsim[0] - dref[0], dsim[1] - dref[1])      # error of the command's Δv (removes upstream drift)
    v_err = math.hypot(sv[0] - rv[0], sv[1] - rv[1])
    return dict(head_err=head_err, ref_turn=ref_turn, sim_turn=sim_turn, ref_D=math.hypot(*dref), sim_D=math.hypot(*dsim),
                dv_err=dv_err, v_err=v_err, ref_s=math.hypot(*rv), sim_s=math.hypot(*sv))


def seg_stats(rows, a, b):
    """pos/vel RMS and max (3D) over rows a..b inclusive."""
    pe = [float(rows[i]["pos_err_3d"]) for i in range(a, b + 1)]
    ve = [float(rows[i]["vel_err_3d"]) for i in range(a, b + 1)]
    if not pe:
        return None
    rms = lambda l: math.sqrt(sum(x * x for x in l) / len(l))
    return dict(pos_rms=rms(pe), pos_max=max(pe), vel_rms=rms(ve), vel_max=max(ve))


def first_air(rows):
    t = next((i for i in range(1, len(rows)) if rows[i]["ref_grounded"] == "0" and rows[i - 1]["ref_grounded"] == "1"), None)
    if t is None:
        return None
    l = next((i for i in range(t, len(rows)) if rows[i]["ref_grounded"] == "1"), len(rows) - 1)
    return t, l


def event_cells(summary):
    ea = summary.get("events_all", {})
    out = {}
    for k in ("takeoff", "land", "slide_start", "slide_end"):
        e = ea.get(k)
        if not e or (e["count_ref"] == 0 and e["count_sim"] == 0):
            out[k] = "–"
            continue
        d = e["delta_steps_sim_minus_ref"]
        worst = max(d, key=abs) if d else None
        c = str(e["count_ref"]) if e["count_ref"] == e["count_sim"] else "%d/%d" % (e["count_ref"], e["count_sim"])
        out[k] = ("%+d" % worst if worst is not None else "n/a") + " (" + c + ")"
    return out


def condition(tid):
    m = re.match(r"^M[123]_(.+)_r\d+$", tid)
    return m.group(1) if m else tid


def trial_dir_for(tid):
    m = re.match(r"^M3_(.+)$", tid)
    if m:
        return os.path.join(M3_TRIALS, m.group(1))
    m = re.match(r"^M2_(.+)$", tid)
    if m:
        return os.path.join(M2_TRIALS, m.group(1))
    return None


def analyse(dir_after, dir_before, tid):
    rows = read_steps(os.path.join(dir_after, tid, "steps.csv"))
    summ = json.load(open(os.path.join(dir_after, tid, "summary.json")))
    rec = dict(tid=tid, cond=condition(tid), n=len(rows), overall=summ["overall"], events=event_cells(summ), summ=summ)
    td = trial_dir_for(tid)
    presses = press_steps(td) if td and os.path.isdir(td) else []
    rec["presses"] = []
    for step, bits in presses:
        idx = next(i for i, r in enumerate(rows) if int(r["step"]) == step)
        m = press_metrics(rows, idx)
        m["step"], m["bits"], m["t"] = step, bits, jump_t(rows, idx)
        if dir_before:
            brows = read_steps(os.path.join(dir_before, tid, "steps.csv"))
            m["before"] = press_metrics(brows, idx)
        rec["presses"].append(m)
    fa = first_air(rows)
    rec["air"] = seg_stats(rows, fa[0], fa[1]) if fa else None
    rec["air_span"] = fa
    if fa:   # from the landing to the end: the ground phase after the first air phase
        rec["after_land"] = seg_stats(rows, fa[1], len(rows) - 1)
    if dir_before:
        bs = json.load(open(os.path.join(dir_before, tid, "summary.json")))
        rec["before_overall"] = bs["overall"]
        brows = read_steps(os.path.join(dir_before, tid, "steps.csv"))
        rec["before_air"] = seg_stats(brows, fa[0], fa[1]) if fa else None
    return rec


def mean(l):
    l = [x for x in l if x is not None]
    return sum(l) / len(l) if l else None


def mx(l, key=lambda x: x):
    l = [x for x in l if x is not None]
    return max(l, key=key) if l else None


def main():
    m3 = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(HERE, "M3_*", "summary.json")))
    recs = [analyse(HERE, os.path.join(HERE, "before_m2model"), t) for t in m3]
    conds = list(OrderedDict.fromkeys(r["cond"] for r in recs))
    L = []
    A = L.append
    A("# R5 replay — M3 Unity motor (`R5MotorV2/m3`) vs R5 trials")
    A("")
    A("Generated by `make_index.py` from the Unity 6000.6.5f1 batch replay (`HSD.R5Replay.Editor.BatchReplay.Run -motor v2`) on branch "
      "`m3/advanced-tech` of HSD-Unity. Open-loop replay from initial_state with the recorded usercmd inputs, aligned by cmd; errors are "
      "sim − ref in Source units (u, u/s). Nothing is tuned per trial: lurch 0.7 / 0.2 s / 0.5 s / 209.3, ground-jump min(v, 299), resumed-slide "
      "jump keeps speed. **Before** = `R5MotorV2/m2` (HSD-Unity main) on the same trials (`before_m2model/`). Per-trial reports: `<trial_id>/report.md`; "
      "the generic batch index is `batch_index.md`; M2/M1 regression outputs are in `regression_m2_m1/`.")
    A("")
    A("Press = the airborne step whose buttons gain a bit of 0x618 (lurch trigger). t = seconds from the start of the jump step to the start of the press step. "
      "Heading err = heading(sim v_h) − heading(ref v_h) after the press step; Δv err = |Δv_sim − Δv_ref| of the press step (Δv = v_h after − v_h before; "
      "removes the drift that existed before the press); |D| = |Δv_h| of the press step (lurch + that command's air accel). Air = first takeoff step .. first landing step "
      "(ref). Event cells: worst step delta sim − ref (count ref, or ref/sim when the counts differ).")
    A("")

    # ---------------- per condition
    A("## 1. Per condition (after; RMS = mean over trials, max = worst trial)")
    A("")
    A("| condition | n | pos RMS 3D | pos max 3D | vel RMS 3D | vel max 3D | air pos RMS | air pos max | air vel max | press t (s) | max \\|heading err\\| at press (°) | max Δv err at press (u/s) | takeoff | land | slide start | slide end | before: pos RMS / air pos RMS / heading err |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in conds:
        l = [r for r in recs if r["cond"] == c]
        pr = [p for r in l for p in r["presses"]]
        ts = sorted(set(round(p["t"], 3) for p in pr if p["t"] is not None))
        he = mx([abs(p["head_err"]) for p in pr])
        dve = mx([p["dv_err"] for p in pr])
        bhe = mx([abs(p["before"]["head_err"]) for p in pr])
        ev = {k: " / ".join(sorted(set(r["events"][k] for r in l))) for k in ("takeoff", "land", "slide_start", "slide_end")}
        A("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s / %s |" % (
            c, len(l), f(mean([r["overall"]["pos_rms_3d_u"] for r in l])), f(mx([r["overall"]["pos_max_3d_u"] for r in l])),
            f(mean([r["overall"]["vel_rms_3d_ups"] for r in l])), f(mx([r["overall"]["vel_max_3d_ups"] for r in l])),
            f(mean([r["air"]["pos_rms"] for r in l if r["air"]])), f(mx([r["air"]["pos_max"] for r in l if r["air"]])),
            f(mx([r["air"]["vel_max"] for r in l if r["air"]])),
            ", ".join("%.3f" % t for t in ts) if ts else "–", f(he), f(dve),
            ev["takeoff"], ev["land"], ev["slide_start"], ev["slide_end"],
            f(mean([r["before_overall"]["pos_rms_3d_u"] for r in l])), f(mean([r["before_air"]["pos_rms"] for r in l if r.get("before_air")])), f(bhe, "{:.2f}")))
    A("")

    # ---------------- press commands
    A("## 2. Lurch press command, per trial")
    A("")
    A("| trial | press step | key | t (s) | lam (model) | ref \\|D\\| | sim \\|D\\| | ref turn (°) | sim turn (°) | heading err (°) | ref speed after | sim speed after | Δv err (u/s) | before: heading err (°) / Δv err |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    names = {0x8: "W", 0x10: "S", 0x200: "A", 0x400: "D"}
    for r in recs:
        for p in r["presses"]:
            lam = None if p["t"] is None else 0.7 * min(1, max(0, (0.5 - p["t"]) / 0.3))
            A("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
                r["tid"], p["step"], "+".join(v for k, v in names.items() if p["bits"] & k), f(p["t"], "{:.4f}"), f(lam, "{:.4f}"),
                f(p["ref_D"]), f(p["sim_D"]), f(p["ref_turn"], "{:.2f}"), f(p["sim_turn"], "{:.2f}"), f(p["head_err"], "{:+.3f}"),
                f(p["ref_s"]), f(p["sim_s"]), f(p["dv_err"]), f(p["before"]["head_err"], "{:+.2f}"), f(p["before"]["dv_err"])))
    A("")

    # ---------------- per trial
    A("## 3. Per trial (after vs before)")
    A("")
    A("| trial | steps | pos RMS 3D | pos max 3D | vel RMS 3D | vel max 3D | air pos RMS / max | after-landing pos RMS / vel max | takeoff | land | slide start | slide end | jump vz err max | before pos RMS / max | before vel RMS / max |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in recs:
        o, b = r["overall"], r["before_overall"]
        al = r.get("after_land")
        A("| [%s](%s/report.md) | %d | %s | %s | %s | %s | %s / %s | %s / %s | %s | %s | %s | %s | %s | %s / %s | %s / %s |" % (
            r["tid"], r["tid"], r["n"], f(o["pos_rms_3d_u"]), f(o["pos_max_3d_u"]), f(o["vel_rms_3d_ups"]), f(o["vel_max_3d_ups"]),
            f(r["air"]["pos_rms"] if r["air"] else None), f(r["air"]["pos_max"] if r["air"] else None),
            f(al["pos_rms"] if al else None), f(al["vel_max"] if al else None),
            r["events"]["takeoff"], r["events"]["land"], r["events"]["slide_start"], r["events"]["slide_end"],
            f(r["summ"].get("jump_max_abs_takeoff_vz_err_ups")),
            f(b["pos_rms_3d_u"]), f(b["pos_max_3d_u"]), f(b["vel_rms_3d_ups"]), f(b["vel_max_3d_ups"])))
    A("")

    # ---------------- regression
    reg = os.path.join(HERE, "regression_m2_m1")
    ids = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(reg, "*", "steps.csv")))
    same, diff = [], []
    for t in ids:
        old = os.path.join(M2_UNITY, t, "steps.csv")
        (same if os.path.exists(old) and filecmp.cmp(old, os.path.join(reg, t, "steps.csv"), shallow=False) else diff).append(t)
    A("## 4. M2 / M1 regression")
    A("")
    A("All %d M2 + M1 trials were replayed with `R5MotorV2/m3` (`regression_m2_m1/`) and their steps.csv compared byte-for-byte with the published "
      "M2 results in `../../m2/unity/` (the `R5MotorV2/m2` replay, also reproduced byte-for-byte from HSD-Unity main before the change)." % len(ids))
    A("")
    A("- **Identical (%d):** %s." % (len(same), ", ".join(same)))
    A("- **Changed (%d):** %s — these are the only M1/M2 trials with an airborne direction-key press edge (one MOVERIGHT press each); "
      "every other trial has none, so the lurch never fires there. The byte-identical outputs also show that the ground-jump cap and the resumed-slide rule did not change a single value in any M1/M2 trial." % (len(diff), ", ".join(diff) or "none"))
    A("")
    A("### 4.1 M2 e2_strafe before / after (one lurch each)")
    A("")
    A("| trial | pos RMS 3D before → after | pos max 3D | vel RMS 3D | vel max 3D | press t (s) | heading err at press (°) | Δv err at press (u/s) | ref \\|D\\| / sim \\|D\\| after | takeoff / land after |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for t in diff:
        a = analyse(reg, None, t)
        bs = json.load(open(os.path.join(M2_UNITY, t, "summary.json")))["overall"]
        brows = read_steps(os.path.join(M2_UNITY, t, "steps.csv"))
        o = a["overall"]
        for p in a["presses"]:
            idx = next(i for i, rr in enumerate(brows) if int(rr["step"]) == p["step"])
            bp = press_metrics(brows, idx)
            A("| %s | %s → %s | %s → %s | %s → %s | %s → %s | %s | %s → %s | %s → %s | %s / %s | %s / %s |" % (
                t, f(bs["pos_rms_3d_u"]), f(o["pos_rms_3d_u"]), f(bs["pos_max_3d_u"]), f(o["pos_max_3d_u"]),
                f(bs["vel_rms_3d_ups"]), f(o["vel_rms_3d_ups"]), f(bs["vel_max_3d_ups"]), f(o["vel_max_3d_ups"]),
                f(p["t"], "{:.4f}"), f(bp["head_err"], "{:+.2f}"), f(p["head_err"], "{:+.3f}"), f(bp["dv_err"]), f(p["dv_err"]),
                f(p["ref_D"]), f(p["sim_D"]), a["events"]["takeoff"], a["events"]["land"]))
    A("")
    notes = os.path.join(HERE, "index_notes.md")
    if os.path.exists(notes):   # hand-written findings, inserted after the intro
        L[6:6] = [open(notes, encoding="utf-8").read().rstrip("\n"), ""]
    with open(os.path.join(HERE, "index.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote index.md:", len(recs), "M3 trials,", len(same), "identical,", len(diff), "changed")


if __name__ == "__main__":
    main()
