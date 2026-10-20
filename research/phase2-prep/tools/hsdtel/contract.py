"""HSD movement trial contract "hsdmove-trial/1" (UNITY-DATA-CONTRACT.md).

A trial is a folder with
  trial.json   manifest: identity, source, units/axes, timing, parameters, per-column provenance
  samples.csv  one row per simulation step, inputs applied during the step and
               the state after it

Canonical space is the recording space: Source axes (+X forward at yaw 0,
+Y left, +Z up, right-handed), lengths in Source units (1 u = 0.0254 m),
angles in degrees. Unity adapters convert with to_unity_*().
"""
import csv
import json
import math
import os
from collections import OrderedDict

from .derive import streams
from . import analysis

CONTRACT_ID = "hsdmove-trial/1"
METERS_PER_UNIT = 0.0254

# column -> (unit, meaning)
SAMPLE_COLUMNS = OrderedDict([
    ("step", ("", "0-based step index within the trial")),
    ("t", ("s", "time at the end of the step (trial-relative, starts near 0)")),
    ("dt", ("s", "duration of the step")),
    ("in_fwd", ("", "forward input -1..1 applied during the step")),
    ("in_right", ("", "right input -1..1 applied during the step")),
    ("in_yaw", ("deg", "view yaw during the step (Source convention: + = turn left)")),
    ("in_pitch", ("deg", "view pitch during the step")),
    ("in_jump", ("", "jump held 0/1")),
    ("in_duck", ("", "duck held 0/1")),
    ("pos_x", ("u", "position after the step")),
    ("pos_y", ("u", "")),
    ("pos_z", ("u", "")),
    ("vel_x", ("u/s", "velocity after the step")),
    ("vel_y", ("u/s", "")),
    ("vel_z", ("u/s", "")),
    ("grounded", ("", "1/0 after the step; empty = unknown")),
    ("sliding", ("", "1/0 after the step; empty = unknown")),
    ("crouched", ("", "1/0 after the step; empty = unknown")),
    ("sprinting", ("", "1/0 after the step; empty = unknown")),
    ("events", ("", "'|'-joined events detected at this step: TAKEOFF, LAND, SLIDE_START, SLIDE_END")),
])
REQUIRED = ["step", "t", "dt", "pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z"]

DEFAULT_TOLERANCES = {
    "pos_rms_u": 4.0,          # RMS 3D position error over the trial
    "vel_rms_ups": 10.0,       # RMS 3D velocity error
    "spd2d_max_abs_ups": 25.0,  # worst horizontal speed difference at any step
    "grounded_mismatch_frac": 0.02,
    "event_step_tolerance": 2,  # LAND/TAKEOFF may differ by this many steps
}


def to_unity_position(x, y, z):
    """Source (x fwd, y left, z up; inches) -> Unity (x right, y up, z fwd; meters)."""
    return (-y * METERS_PER_UNIT, z * METERS_PER_UNIT, x * METERS_PER_UNIT)


def to_unity_velocity(vx, vy, vz):
    return to_unity_position(vx, vy, vz)


def to_unity_yaw(source_yaw_deg):
    """Source yaw (CCW from +X seen from above) -> Unity yaw about +Y (CW from +Z)."""
    return -source_yaw_deg


def _b(v):
    return "" if v is None or (isinstance(v, float) and v < 0) else int(v)


def _axis(v):
    """Input axes use -9 for 'method unavailable' in the mod."""
    return None if v is None or (isinstance(v, float) and v < -2) else v


def _f(v):
    return "" if v is None or (isinstance(v, float) and not math.isfinite(v)) else round(float(v), 6)


def export_trial(rows, run, out_dir, side="cl", trial_id=None, source="r5flowstate", experiment="",
                 parameters=None, notes=""):
    """Build a trial from the HSD frame stream of one run (inputs + time + state)."""
    frames = []
    for key, srows in streams(rows).items():
        if key[0] == "HSD" and key[1] == side and key[2] == "frame":
            frames += [r for r in srows if r.get("drv_run") == run]
    if len(frames) < 2:
        raise ValueError(f"run {run!r} has {len(frames)} HSD frame rows on side {side!r}; "
                         "was hsd_md_cl_trace 1 set during the trial?")
    ev_by_line = {}
    for e in analysis.events(rows):
        if e["source"] == "HSD" and e["side"] == side and e["drv_run"] == run:
            ev_by_line.setdefault((e["file"], e["line_no"]), []).append(e["event"])
    t0 = frames[0]["t"] - (frames[0].get("ft") or 0.0)
    samples = []
    prev_t = t0
    for i, r in enumerate(frames):
        dt = r["t"] - prev_t if i else (r.get("ft") or 0.0)
        prev_t = r["t"]
        samples.append(OrderedDict([
            ("step", i), ("t", _f(r["t"] - t0)), ("dt", _f(dt)),
            ("in_fwd", _f(_axis(r.get("ax_fwd")))),
            ("in_right", _f(_axis(r.get("ax_right")))),
            ("in_yaw", _f(r.get("yaw"))), ("in_pitch", _f(r.get("pitch"))),
            ("in_jump", _b(r.get("in_jump"))), ("in_duck", _b(r.get("in_duck"))),
            ("pos_x", _f(r.get("ox"))), ("pos_y", _f(r.get("oy"))), ("pos_z", _f(r.get("oz"))),
            ("vel_x", _f(r.get("vx"))), ("vel_y", _f(r.get("vy"))), ("vel_z", _f(r.get("vz"))),
            ("grounded", _b(r.get("ground"))), ("sliding", _b(r.get("slide"))),
            ("crouched", _b(r.get("crouch"))), ("sprinting", _b(r.get("sprint"))),
            ("events", "|".join(ev_by_line.get((r["file"], r["line_no"]), []))),
        ]))
    provenance = {c: "obs" for c in SAMPLE_COLUMNS}
    provenance.update({"step": "meta", "t": "obs (Time() minus trial start)",
                       "dt": "drv (difference of observed Time())", "events": "drv (hsdtel edge detection)",
                       "in_fwd": "obs GetInputAxisForward", "in_right": "obs GetInputAxisRight",
                       "in_jump": "obs IsInputCommandHeld(IN_JUMP)", "in_duck": "obs IsInputCommandHeld(IN_DUCK)"})
    manifest = OrderedDict([
        ("contract", CONTRACT_ID),
        ("trial_id", trial_id or f"{source}_{run}"),
        ("source", source),
        ("experiment", experiment),
        ("recorded_side", side),
        ("producer", "hsdtel.contract.export_trial from HSD.MoveDiag v0.2 client frames"),
        ("space", {"axes": "source_zup_righthanded", "x": "forward at yaw 0", "y": "left", "z": "up",
                   "length_unit": "u", "meters_per_unit": METERS_PER_UNIT, "angle_unit": "deg"}),
        ("timing", {"variable_dt": True, "steps": len(samples),
                    "duration_s": samples[-1]["t"], "sampling": "one row per client script frame (WaitFrame)"}),
        ("step_semantics", "inputs held during the step; state sampled after the step"),
        ("parameters", parameters or {}),
        ("provenance", provenance),
        ("columns", {c: {"unit": u, "meaning": m} for c, (u, m) in SAMPLE_COLUMNS.items()}),
        ("notes", notes),
    ])
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "trial.json"), "w", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
    with open(os.path.join(out_dir, "samples.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(SAMPLE_COLUMNS))
        w.writeheader()
        w.writerows(samples)
    return manifest, samples


def load_trial(path):
    with open(os.path.join(path, "trial.json")) as fh:
        manifest = json.load(fh)
    with open(os.path.join(path, "samples.csv"), newline="") as fh:
        samples = list(csv.DictReader(fh))
    return manifest, samples


def check_trial(path):
    """Contract conformance. Returns a list of problem strings (empty = OK)."""
    problems = []
    try:
        manifest, samples = load_trial(path)
    except (OSError, ValueError) as e:
        return [f"unreadable trial: {e}"]
    if manifest.get("contract") != CONTRACT_ID:
        problems.append(f"contract is {manifest.get('contract')!r}, expected {CONTRACT_ID!r}")
    space = manifest.get("space", {})
    if space.get("axes") != "source_zup_righthanded" or not space.get("meters_per_unit"):
        problems.append("space.axes/meters_per_unit missing or not the canonical source space")
    if not samples:
        return problems + ["no samples"]
    cols = list(samples[0].keys())
    for c in REQUIRED:
        if c not in cols:
            problems.append(f"missing required column {c}")
    for c in cols:
        if c not in manifest.get("provenance", {}):
            problems.append(f"column {c} has no provenance entry")
    if problems:
        return problems
    last_t, bad = -1e9, 0
    for i, s in enumerate(samples):
        if int(s["step"]) != i:
            problems.append(f"row {i}: step {s['step']} not consecutive")
            break
        try:
            t, dt = float(s["t"]), float(s["dt"])
        except ValueError:
            problems.append(f"row {i}: t/dt not numeric")
            break
        if t < last_t - 1e-9 or dt < 0:
            problems.append(f"row {i}: time not monotonic or negative dt")
            break
        last_t = t
        for c in REQUIRED[3:]:
            try:
                if not math.isfinite(float(s[c])):
                    bad += 1
            except ValueError:
                bad += 1
    if bad:
        problems.append(f"{bad} non-numeric/non-finite values in required state columns")
    return problems


def _vec(s, p):
    return float(s[p + "_x"]), float(s[p + "_y"]), float(s[p + "_z"])


def compare_trials(ref_path, test_path, tolerances=None):
    """Step-aligned comparison of a test trial (e.g. a Unity replay) against a
    reference trial (e.g. an R5 recording). Both must have the same step count."""
    tol = dict(DEFAULT_TOLERANCES, **(tolerances or {}))
    _, ref = load_trial(ref_path)
    _, test = load_trial(test_path)
    n = min(len(ref), len(test))
    out = OrderedDict([("steps_ref", len(ref)), ("steps_test", len(test))])
    if n == 0:
        out["pass"] = False
        return out
    pe = ve = 0.0
    spd_max = 0.0
    gmis = gcount = 0
    for a, b in zip(ref[:n], test[:n]):
        pa, pb = _vec(a, "pos"), _vec(b, "pos")
        va, vb = _vec(a, "vel"), _vec(b, "vel")
        pe += sum((x - y) ** 2 for x, y in zip(pa, pb))
        ve += sum((x - y) ** 2 for x, y in zip(va, vb))
        spd_max = max(spd_max, abs(math.hypot(va[0], va[1]) - math.hypot(vb[0], vb[1])))
        if a.get("grounded") not in ("", None) and b.get("grounded") not in ("", None):
            gcount += 1
            gmis += a["grounded"] != b["grounded"]
    out["pos_rms_u"] = math.sqrt(pe / n)
    out["vel_rms_ups"] = math.sqrt(ve / n)
    out["spd2d_max_abs_ups"] = spd_max
    out["grounded_mismatch_frac"] = gmis / gcount if gcount else None

    def ev_steps(samples, name):
        return [i for i, s in enumerate(samples) if name in (s.get("events") or "").split("|")]

    worst = 0
    ev_ok = True
    for name in ("TAKEOFF", "LAND", "SLIDE_START", "SLIDE_END"):
        ra, tb = ev_steps(ref, name), ev_steps(test, name)
        if len(ra) != len(tb):
            ev_ok = False
            out[f"events_{name}"] = f"count {len(ra)} vs {len(tb)}"
            continue
        if ra:
            d = max(abs(x - y) for x, y in zip(ra, tb))
            worst = max(worst, d)
            out[f"events_{name}"] = f"{len(ra)} matched, worst offset {d} step(s)"
    out["event_step_worst"] = worst
    checks = OrderedDict([
        ("step_count", len(ref) == len(test)),
        ("pos_rms_u", out["pos_rms_u"] <= tol["pos_rms_u"]),
        ("vel_rms_ups", out["vel_rms_ups"] <= tol["vel_rms_ups"]),
        ("spd2d_max_abs_ups", spd_max <= tol["spd2d_max_abs_ups"]),
        ("grounded", out["grounded_mismatch_frac"] is None or out["grounded_mismatch_frac"] <= tol["grounded_mismatch_frac"]),
        ("events", ev_ok and worst <= tol["event_step_tolerance"]),
    ])
    out["checks"] = checks
    out["tolerances"] = tol
    out["pass"] = all(checks.values())
    return out


def parameters_from_census(path, experiment="E0"):
    """census.csv -> manifest parameters. Reader preference: dedi setting
    (authoritative engine), then client class var, then client setting."""
    out = OrderedDict()
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            for reader in ("sv_setting", "cl_classvar", "cl_setting"):
                v = row.get(reader)
                if v not in (None, "", "-"):
                    out[row["key"]] = OrderedDict([("value", v), ("reader", reader),
                                                   ("type", row.get(reader + "_type")),
                                                   ("differs_between_readers", row.get("differs") == "1"),
                                                   ("experiment", experiment)])
                    break
    return out
