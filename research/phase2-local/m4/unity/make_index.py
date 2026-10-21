"""Build m4/unity/index.md from the Unity batch-replay outputs of the M4 trials (stdlib only).

Inputs (relative to this folder):
  <trial_id>/steps.csv, summary.json                 after:  R5MotorV2 + the legend's ability kit (BatchReplay -scenarios scenarios.json)
  before_plain_v2/<trial_id>/steps.csv, summary.json before: plain R5MotorV2/m3 (HSD-Unity main), recorded movescale column
  ../trials/<dir>/samples.csv, trial.json             reference inputs (movescale, buttons) for the event extraction
  scenarios.json                                      grapple release steps

    python make_index.py

Event extraction is the same on both series where the quantity exists in both (step indices; Δ = sim − ref). Reference ability events
come from signatures in the recorded state (movescale onset, velocity steps); simulated ones from the ability events the replay logs in
steps.csv sim_events (STIM_ON, PAD_LAUNCH, LIFT_EJECT, GRAPPLE_PULL, JETS_ON, JETS_POSTFX_END, POUNCE_LAUNCH, ...).
"""
import csv
import json
import math
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS = os.path.join(HERE, "..", "trials")
BEFORE = os.path.join(HERE, "before_plain_v2")
IN_OFFHAND1, IN_JUMP = 0x200000, 0x2
G = 750.0

ORDER = ["m4_ctrl_sprint", "m4_stim_sprint", "m4_stim_walk", "m4_ctrl_air", "m4_stim_air", "m4_pad_walk", "m4_pad_sprint",
         "m4_pad_crouch", "e2_noinput", "e4_stand", "m4_lift_ride", "m4_lift_jumpout", "m4_lift_strafe", "m4_grapple_hold",
         "m4_grapple_near", "m4_valk_ctrl", "m4_valk_jets", "m4_pounce_c0", "m4_pounce_c13"]
ABILITY = {"m4_ctrl_sprint": "control (Octane)", "m4_stim_sprint": "stim", "m4_stim_walk": "stim", "m4_ctrl_air": "control (Octane)",
           "m4_stim_air": "stim", "m4_pad_walk": "jump pad", "m4_pad_sprint": "jump pad", "m4_pad_crouch": "jump pad",
           "e2_noinput": "control (Horizon)", "e4_stand": "control (Horizon)", "m4_lift_ride": "gravity lift",
           "m4_lift_jumpout": "gravity lift", "m4_lift_strafe": "gravity lift", "m4_grapple_hold": "grapple", "m4_grapple_near": "grapple",
           "m4_valk_ctrl": "control (Valkyrie)", "m4_valk_jets": "jets", "m4_pounce_c0": "pounce", "m4_pounce_c13": "pounce"}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def f(v, fmt="{:.3f}"):
    return "–" if v is None or (isinstance(v, float) and math.isnan(v)) else fmt.format(v)


def sd(v):
    return "–" if v is None else "{:+d}".format(v)


def load_steps(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        d = {"step": int(r["step"]), "dt": num(r["dt"]), "ref_g": int(r["ref_grounded"] or 1), "sim_g": int(r["sim_grounded"]),
             "ref_ev": r["ref_events"].split("|") if r["ref_events"] else [], "sim_ev": r["sim_events"].split("|") if r["sim_events"] else [],
             "ref_ms": num(r["ref_maxspeed"]), "sim_ms": num(r["sim_maxspeed"]), "err": num(r["pos_err_3d"]), "verr": num(r["vel_err_3d"])}
        for s in ("ref", "sim"):
            d[s + "_p"] = (num(r[s + "_pos_x"]), num(r[s + "_pos_y"]), num(r[s + "_pos_z"]))
            d[s + "_v"] = (num(r[s + "_vel_x"]), num(r[s + "_vel_y"]), num(r[s + "_vel_z"]))
        out.append(d)
    return out


def load_samples(d):
    with open(os.path.join(TRIALS, d, "samples.csv"), newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [{"buttons": int(r["buttons"] or 0), "msc": num(r["movescale"]), "fwd": num(r["cmd_fwd"]), "side": num(r["cmd_side"])} for r in rows]


def summary(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def hlen(v):
    return math.hypot(v[0], v[1])


def vlen(v):
    return math.sqrt(sum(x * x for x in v))


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def first(rows, pred, start=0):
    for i in range(max(start, 0), len(rows)):
        if pred(i):
            return i
    return None


def sim_event(rows, name, start=0):
    return first(rows, lambda i: any(e.startswith(name) for e in rows[i]["sim_ev"]), start)


def ref_event(rows, name, start=0):
    return first(rows, lambda i: name in rows[i]["ref_ev"], start)


def delta(a, b):
    return None if a is None or b is None else b - a


def verr(rows, ir, isim, comp):
    """sim quantity at its own event step − ref quantity at its own event step."""
    if ir is None or isim is None:
        return float("nan")
    return comp(rows[isim]["sim_v"]) - comp(rows[ir]["ref_v"])


BROWS = []   # before-series rows of the trial being processed (set in main)


def window_rms(rows, a, b):
    xs = [rows[i]["err"] for i in range(a, b) if not math.isnan(rows[i]["err"])] if a is not None and b is not None else []
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def press_dv(rows, k, side):
    a, b = rows[k - 1][side + "_v"], rows[k][side + "_v"]
    return (b[0] - a[0], b[1] - a[1])


# ---------------------------------------------------------------------------------------------------- per-ability key events

def ev_stim(rows, smp, sched):
    out = OrderedDict()
    tap = first(smp, lambda i: smp[i]["buttons"] & IN_OFFHAND1 and not (smp[i - 1]["buttons"] & IN_OFFHAND1) if i > 0 else False)
    on_r = first(smp, lambda i: i > 0 and smp[i]["msc"] > 1.4 and smp[i - 1]["msc"] < 1.2) if tap is not None else None
    on_s = sim_event(rows, "STIM_ON")
    out["stim onset step ref/sim (Δ)"] = (on_r, on_s)
    # fade start: first step after the onset (or step 0) where the cap drops below the plateau, maxspeed series of both sides
    base = on_r if on_r is not None else 0
    if on_r is not None or smp[0]["msc"] > 1.4:
        def fade(side, start):
            # first drop of the cap with the inputs and ground state unchanged from the previous step (a move-scale drop)
            g = side + "_g"
            # (persisting on the next step: the client's one-command settings-mod drop, octane §2.1, is not a fade)
            return first(rows, lambda i: i + 1 < len(rows) and rows[i][side + "_ms"] < rows[i - 1][side + "_ms"] * (1 - 2e-5)
                         and rows[i + 1][side + "_ms"] < rows[i - 1][side + "_ms"] * (1 - 2e-5) and rows[i][g] == rows[i - 1][g]
                         and smp[i]["buttons"] == smp[i - 1]["buttons"] and smp[i]["fwd"] == smp[i - 1]["fwd"] and smp[i]["side"] == smp[i - 1]["side"],
                         start)
        out["stim fade start step ref/sim (Δ)"] = (fade("ref", base + 2), fade("sim", (on_s if on_s is not None else 0) + 2))
    ms = [abs(r["sim_ms"] - r["ref_ms"]) for r in rows if not math.isnan(r["sim_ms"]) and not math.isnan(r["ref_ms"])]
    out["max |Δ maxspeed| (u/s)"] = max(ms) if ms else float("nan")
    if sched in ("m4_stim_air", "m4_ctrl_air"):
        k = first(smp, lambda i: i > 0 and (smp[i]["buttons"] & 0x400) and not (smp[i - 1]["buttons"] & 0x400))
        if k is not None:
            dr, ds, db = press_dv(rows, k, "ref"), press_dv(rows, k, "sim"), press_dv(BROWS, k, "sim")
            out["strafe press |Δv| ref / Δv err after / before (u/s)"] = (math.hypot(*dr), math.hypot(ds[0] - dr[0], ds[1] - dr[1]),
                                                                          math.hypot(db[0] - dr[0], db[1] - dr[1]))
    return out


def ev_pad(rows, smp, sched):
    out = OrderedDict()
    lr, ls = ref_event(rows, "TAKEOFF"), sim_event(rows, "PAD_LAUNCH")
    out["launch step ref/sim (Δ)"] = (lr, ls)
    out["launch v_h err (u/s)"] = verr(rows, lr, ls, hlen)
    out["launch vz err (u/s)"] = verr(rows, lr, ls, lambda v: v[2])
    dr, ds = ref_event(rows, "LAND", (lr or 0) + 1), sim_event(rows, "LAND", (ls or 0) + 1)
    out["landing step ref/sim (Δ)"] = (dr, ds)
    if dr is not None and ds is not None:
        out["landing f0 ref / sim"] = (hlen(rows[dr]["ref_v"]) / hlen(rows[dr - 1]["ref_v"]), hlen(rows[ds]["sim_v"]) / hlen(rows[ds - 1]["sim_v"]))
        out["flight pos RMS after / before (u)"] = (window_rms(rows, lr, dr), window_rms(BROWS, lr, dr))
        out["landing point h err (u)"] = hlen(tuple(a - b for a, b in zip(rows[ds]["sim_p"], rows[dr]["ref_p"])))
    return out


def ev_lift(rows, smp, sched):
    out = OrderedDict()
    er, es = ref_event(rows, "TAKEOFF"), sim_event(rows, "LIFT_ENTER")
    out["entry step ref/sim (Δ)"] = (er, es)

    def hover(side, start):
        return first(rows, lambda i: abs(rows[i][side + "_v"][2]) < 5 and rows[i][side + "_p"][2] > 1300, start)

    hr, hs = hover("ref", er or 0), hover("sim", es or 0)
    out["hover start step ref/sim (Δ)"] = (hr, hs)
    jr = first(rows, lambda i: rows[i]["ref_v"][2] - rows[i - 1]["ref_v"][2] > 100 or hlen(rows[i]["ref_v"]) - hlen(rows[i - 1]["ref_v"]) > 150,
               (er or 0) + 1)
    js = sim_event(rows, "LIFT_EJECT")
    out["eject step ref/sim (Δ)"] = (jr, js)
    out["eject v_h err (u/s)"] = verr(rows, jr, js, hlen)
    out["eject vz err (u/s)"] = verr(rows, jr, js, lambda v: v[2])
    if jr is not None and js is not None:
        out["pos err at ref eject (u)"] = rows[jr]["err"]
    dr, ds = ref_event(rows, "LAND", (er or 0) + 1), sim_event(rows, "LAND", (es or 0) + 1)
    out["landing step ref/sim (Δ)"] = (dr, ds)
    out["lift phase pos RMS after / before (u)"] = (window_rms(rows, er, jr), window_rms(BROWS, er, jr))
    return out


def ev_grapple(rows, smp, sched, release):
    out = OrderedDict()
    ar, as_ = ref_event(rows, "TAKEOFF"), sim_event(rows, "GRAPPLE_ATTACH")
    out["attach (hop) step ref/sim (Δ)"] = (ar, as_)
    pr = first(rows, lambda i: abs(rows[i]["ref_v"][0] - rows[i - 1]["ref_v"][0]) > 0.5, (ar or 0) + 1)
    ps = sim_event(rows, "GRAPPLE_PULL")
    out["pull start step ref/sim (Δ)"] = (pr, ps)
    out["release step (scenario: recorded detach)"] = release
    if release is not None:
        r = rows[release - 1]
        out["pos err at release (u)"] = r["err"]
        out["speed err at release (u/s)"] = vlen(r["sim_v"]) - vlen(r["ref_v"])
        out["vel err at release (u/s)"] = r["verr"]
        out["pull window pos RMS after / before (u)"] = (window_rms(rows, pr, release), window_rms(BROWS, pr, release))
    return out


def ev_jets(rows, smp, sched):
    out = OrderedDict()
    k = first(smp, lambda i: i > 0 and (smp[i]["buttons"] & IN_JUMP) and not (smp[i - 1]["buttons"] & IN_JUMP) and not rows[i - 1]["ref_g"])
    js = sim_event(rows, "JETS_ON")
    out["activation step press/sim (Δ)"] = (k, js)
    rel = first(smp, lambda i: i > (k or 0) and not (smp[i]["buttons"] & IN_JUMP)) if k is not None else None
    if rel is not None:
        out["vz err, last held step (u/s)"] = rows[rel - 1]["sim_v"][2] - rows[rel - 1]["ref_v"][2]
        out["vz ref/sim on the release step (u/s)"] = (rows[rel]["ref_v"][2], rows[rel]["sim_v"][2])
        out["vz err, release + 1 (u/s)"] = rows[rel + 1]["sim_v"][2] - rows[rel + 1]["ref_v"][2]
        fr = first(rows, lambda i: abs((rows[i]["ref_v"][2] - rows[i - 1]["ref_v"][2]) / rows[i]["dt"] + G) < 30 and not rows[i]["ref_g"], rel + 3)
        fs = sim_event(rows, "JETS_POSTFX_END")
        out["post effect end step ref/sim (Δ)"] = (fr, fs)
        out["jet phase pos RMS after / before (u)"] = (window_rms(rows, k, rel), window_rms(BROWS, k, rel))
    dr, ds = ref_event(rows, "LAND", (k or 0) + 1), sim_event(rows, "LAND", (k or 0) + 1)
    out["landing step ref/sim (Δ)"] = (dr, ds)
    return out


def ev_pounce(rows, smp, sched):
    out = OrderedDict()
    lr, ls = ref_event(rows, "TAKEOFF"), sim_event(rows, "POUNCE_LAUNCH")
    out["launch step ref/sim (Δ)"] = (lr, ls)
    out["launch v_h err (u/s)"] = verr(rows, lr, ls, hlen)
    out["launch vz err (u/s)"] = verr(rows, lr, ls, lambda v: v[2])
    dr, ds = ref_event(rows, "LAND", (lr or 0) + 1), sim_event(rows, "LAND", (ls or 0) + 1)
    out["landing step ref/sim (Δ)"] = (dr, ds)
    if None not in (lr, ls, dr, ds):
        rng_r = hlen(tuple(a - b for a, b in zip(rows[dr]["ref_p"], rows[lr - 1]["ref_p"])))
        rng_s = hlen(tuple(a - b for a, b in zip(rows[ds]["sim_p"], rows[ls - 1]["sim_p"])))
        out["pounce range err (u)"] = rng_s - rng_r
        out["flight pos RMS after / before (u)"] = (window_rms(rows, lr, dr), window_rms(BROWS, lr, dr))
    return out


def ev_control(rows, smp, sched):
    out = OrderedDict()
    tr, ts = ref_event(rows, "TAKEOFF"), first(rows, lambda i: "TAKEOFF" in rows[i]["sim_ev"])
    if tr is not None:
        out["takeoff step ref/sim (Δ)"] = (tr, ts)
        dr, ds = ref_event(rows, "LAND", tr + 1), first(rows, lambda i: "LAND" in rows[i]["sim_ev"], (ts or 0) + 1)
        out["landing step ref/sim (Δ)"] = (dr, ds)
    if sched == "m4_ctrl_air":
        out.update((k, v) for k, v in ev_stim(rows, smp, sched).items() if k.startswith("strafe") or k.startswith("max"))
    return out


def cell(v):
    if isinstance(v, tuple) and len(v) == 2 and all(isinstance(x, int) or x is None for x in v):
        a, b = v
        return f"{'–' if a is None else a}/{'–' if b is None else b} ({sd(delta(a, b))})"
    if isinstance(v, tuple):
        return " / ".join(f(x) for x in v)
    if isinstance(v, int):
        return str(v)
    return f(v)


def main():
    scen = json.load(open(os.path.join(HERE, "scenarios.json"), encoding="utf-8"))
    recs = []
    for d in sorted(os.listdir(TRIALS)):
        if d.endswith("_REJECTED") or not os.path.isdir(os.path.join(TRIALS, d)):
            continue
        tid = "M4_" + d
        sched = d.rsplit("_", 1)[0]
        after = os.path.join(HERE, tid)
        before = os.path.join(BEFORE, tid)
        rows = load_steps(os.path.join(after, "steps.csv"))
        brows = load_steps(os.path.join(before, "steps.csv"))
        smp = load_samples(d)
        BROWS[:] = brows
        sa, sb = summary(os.path.join(after, "summary.json")), summary(os.path.join(before, "summary.json"))
        fam = ABILITY[sched]
        if fam == "stim" or sched in ("m4_ctrl_sprint",):
            ev = ev_stim(rows, smp, sched)
        elif fam == "jump pad":
            ev = ev_pad(rows, smp, sched)
        elif fam == "gravity lift":
            ev = ev_lift(rows, smp, sched)
        elif fam == "grapple":
            ev = ev_grapple(rows, smp, sched, scen["trials"].get(tid, {}).get("grapple_release_step"))
        elif fam == "jets":
            ev = ev_jets(rows, smp, sched)
        elif fam == "pounce":
            ev = ev_pounce(rows, smp, sched)
        else:
            ev = ev_control(rows, smp, sched)
        recs.append({"tid": tid, "sched": sched, "fam": fam, "a": sa["overall"], "b": sb["overall"], "ev": ev,
                     "model": sa["model"], "terminal_a": sa.get("terminal_speed_err_ups"), "terminal_b": sb.get("terminal_speed_err_ups"),
                     "carry": tid in scen["trials"] and "stim_initial_onset_s" in scen["trials"][tid]})

    L = []
    L.append("# R5 replay — M4 Unity ability primitives (`R5MotorV2/m4+<kit>`) vs R5 trials")
    L.append("")
    L.append("Generated by `make_index.py` from the Unity 6000.6.5f1 batch replay (`HSD.R5Replay.Editor.BatchReplay.Run -motor v2 -scenarios scenarios.json`) "
             "on branch `m4/ability-primitives` of HSD-Unity. Open-loop replay from initial_state with the recorded usercmd inputs, aligned by cmd; "
             "errors are sim − ref in Source units (u, u/s). **After** = R5MotorV2 with the legend's ability kit (`<trial_id>/`): abilities fire from the "
             "recorded buttons (IN_OFFHAND1 bit 21, jump/IN_DODGE), deployables/targets come from `scenarios.json`, the move scale is modelled "
             "(parameter moveScale 1.15 × ability factors; the recorded movescale column is not used), and the lurch clamp is 0.7 × the current sprint cap. "
             "**Before** = plain `R5MotorV2/m3` (HSD-Unity main) on the same trials (`before_plain_v2/`); it is fed the recorded movescale column, "
             "which already contains the measured stim / landing / weapon move scale, so the before numbers are optimistic for those. "
             "Nothing is tuned per trial. Generic batch index of the after run: `batch_index.md`. Findings (section 0) are hand-written in `index_notes.md`. Regression: `regression.md`.")
    L.append("")
    L.append("## 1. Per condition (RMS = mean over the trials, max = worst trial)")
    L.append("")
    L.append("| condition | ability | n | after pos RMS 3D | after pos max 3D | after vel RMS 3D | after vel max 3D | before pos RMS 3D | before vel RMS 3D |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for s in ORDER:
        l = [r for r in recs if r["sched"] == s]
        if not l:
            continue
        m = lambda k, key: sum(r[k][key] for r in l) / len(l)  # noqa: E731
        mx = lambda k, key: max(r[k][key] for r in l)  # noqa: E731
        L.append(f"| {s} | {l[0]['fam']} | {len(l)} | {f(m('a', 'pos_rms_3d_u'))} | {f(mx('a', 'pos_max_3d_u'))} | {f(m('a', 'vel_rms_3d_ups'))} | "
                 f"{f(mx('a', 'vel_max_3d_ups'))} | {f(m('b', 'pos_rms_3d_u'))} | {f(m('b', 'vel_rms_3d_ups'))} |")
    L.append("")
    L.append("## 2. Per trial")
    L.append("")
    L.append("| condition | trial | steps-model | pos RMS 3D after | before | pos max 3D after | before | vel RMS 3D after | before | terminal Δ after / before |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in ORDER:
        for r in [x for x in recs if x["sched"] == s]:
            L.append(f"| {s} | [{r['tid']}]({r['tid']}/report.md){' (stim carried over)' if r['carry'] else ''} | `{r['model'].replace('R5MotorV2/m4+', 'm4+')}` | "
                     f"{f(r['a']['pos_rms_3d_u'])} | {f(r['b']['pos_rms_3d_u'])} | {f(r['a']['pos_max_3d_u'])} | {f(r['b']['pos_max_3d_u'])} | "
                     f"{f(r['a']['vel_rms_3d_ups'])} | {f(r['b']['vel_rms_3d_ups'])} | {f(r['terminal_a'])} / {f(r['terminal_b'])} |")
    L.append("")
    L.append("## 3. Key ability events (after)")
    L.append("")
    L.append("Step cells: ref/sim (Δ = sim − ref). Velocity errors at an event compare each series at its own event step. "
             "Reference events: stim onset = first step with movescale > 1.4; fade start = first step whose maxspeed drops (and stays down on the next step) with unchanged inputs; "
             "pad/pounce launch = TAKEOFF; lift entry = TAKEOFF, hover = first |vz| < 5 above z 1300, eject = first vz step > 100 or v_h step > 150; "
             "grapple attach = TAKEOFF, pull = first |Δvx| > 0.5; jets activation = the airborne jump press, post-effect end = first full-g command "
             "after the release. The grapple release step is the recorded detach command (scenario), so it is not an error.")
    for s in ORDER:
        l = [r for r in recs if r["sched"] == s]
        if not l:
            continue
        keys = list(l[0]["ev"].keys())
        if not keys:
            continue
        L.append("")
        L.append(f"### {s} ({l[0]['fam']})")
        L.append("")
        L.append("| quantity | " + " | ".join(r["tid"] for r in l) + " |")
        L.append("|---|" + "---|" * len(l))
        for k in keys:
            L.append(f"| {k} | " + " | ".join(cell(r["ev"].get(k)) for r in l) + " |")
    L.append("")
    notes = os.path.join(HERE, "index_notes.md")
    if os.path.exists(notes):   # hand-written findings, inserted after the intro (as in M3)
        L[4:4] = [open(notes, encoding="utf-8").read().rstrip("\n"), ""]
    with open(os.path.join(HERE, "index.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))
    print("wrote index.md:", len(recs), "trials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
