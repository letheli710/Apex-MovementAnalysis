"""HSD movement trial contract "hsdmove-trial/2" (UNITY-DATA-CONTRACT.md).

A trial is a folder with
  trial.json   manifest: identity, source, units/axes, timing, initial state,
               terrain, parameters (with the side and reader that produced
               each), per-column provenance
  samples.csv  one row per simulation step: the usercmd(s) and inputs applied
               during the step and the state after it

Canonical space is the recording space: Source axes (+X forward at yaw 0,
+Y left, +Z up, right-handed), lengths in Source units (1 u = 0.0254 m),
angles in degrees. Unity adapters convert with to_unity_*().

Version 1 trials (no usercmd / edge / initial-state fields) still load and
check against the v1 column set.
"""
import csv
import json
import math
import os
from collections import OrderedDict

from .derive import streams
from .schema import BUTTON_BITS, IN_SPEED
from . import analysis

CONTRACT_ID = "hsdmove-trial/2"
CONTRACT_V1 = "hsdmove-trial/1"
CONTRACT_IDS = (CONTRACT_V1, CONTRACT_ID)
METERS_PER_UNIT = 0.0254

# column -> (unit, meaning)
SAMPLE_COLUMNS = OrderedDict([
    ("step", ("", "0-based step index within the trial")),
    ("t", ("s", "time at the end of the step (trial-relative, starts near 0)")),
    ("dt", ("s", "duration of the step")),
    ("cmd", ("", "usercmd command_number of the last command simulated in the step")),
    ("n_cmds", ("", "number of usercmds logged in the step; cmd - previous cmd must equal it")),
    ("in_fwd", ("", "forward input -1..1 applied during the step")),
    ("in_right", ("", "right input -1..1 applied during the step")),
    ("in_yaw", ("deg", "view yaw during the step (Source convention: + = turn left)")),
    ("in_pitch", ("deg", "view pitch during the step")),
    ("in_jump", ("", "jump held 0/1")),
    ("in_duck", ("", "duck held 0/1")),
    ("in_sprint", ("", "sprint (IN_SPEED) held 0/1 in the usercmd")),
    ("buttons", ("", "usercmd m_nButtons held mask (in_buttons.h bits) of the step's last command")),
    ("cmd_fwd", ("", "usercmd forwardmove -1..1 of the step's last command")),
    ("cmd_side", ("", "usercmd sidemove -1..1 (+ = right) of the step's last command")),
    ("pressed", ("", "'|'-joined inputs that went down during the step: button names, AX_FWD/AX_BACK/AX_RIGHT/AX_LEFT")),
    ("released", ("", "'|'-joined inputs that went up during the step (same names)")),
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
STATE = REQUIRED[3:]
# Inputs a replay needs, per contract version. Every sample must carry a value
# (edge columns may be empty = no edge, but must be present and consistent).
INPUTS = {
    1: ["in_fwd", "in_right", "in_yaw", "in_pitch", "in_jump", "in_duck"],
    2: ["cmd", "n_cmds", "in_fwd", "in_right", "in_yaw", "in_pitch", "in_jump", "in_duck", "in_sprint",
        "buttons", "cmd_fwd", "cmd_side"],
}
EDGE_COLUMNS = ["pressed", "released"]
V1_COLUMNS = [c for c in SAMPLE_COLUMNS if c not in ("cmd", "n_cmds", "in_sprint", "buttons", "cmd_fwd",
                                                    "cmd_side", "pressed", "released")]
AXIS_KEYS = ("AX_FWD", "AX_BACK", "AX_RIGHT", "AX_LEFT")

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


# ---------------------------------------------------------------- input edges
_BIT_NAMES = {b: n for n, b in BUTTON_BITS.items()}


def held_inputs(buttons, fwd=0.0, side=0.0):
    """Names of the inputs held in one usercmd: every set bit of m_nButtons
    (in_buttons.h names, else BIT<n>) plus the sign of forwardmove/sidemove."""
    out = []
    for bit in range(32):
        if int(buttons) & (1 << bit):
            out.append(_BIT_NAMES.get(1 << bit, f"BIT{bit}"))
    fwd, side = fwd or 0.0, side or 0.0
    out += [n for n, on in zip(AXIS_KEYS, (fwd > 0, fwd < 0, side > 0, side < 0)) if on]
    return out


def _join(names):
    return "|".join(names)


def _split(text):
    return [x for x in (text or "").split("|") if x]


# ---------------------------------------------------------------- export
def _frames_and_cmds(rows, run, side, session):
    """Frame stream of the run plus, per frame, the usercmds logged at or before
    its wall time (MOVE-TRACE is printed during prediction, before the script
    samples the frame). Returns (frames, cmds_by_frame, prev_cmd, session, n_all)."""
    found = []
    for key, srows in streams(rows).items():
        if key[0] == "HSD" and key[1] == side and key[2] == "frame" and (session is None or key[4] == session):
            sel = [r for r in srows if r.get("drv_run") == run]
            if sel:
                found.append((key, srows, sel))
    if len(found) > 1:
        raise ValueError(f"run {run!r} occurs in {len(found)} {side} frame streams "
                         f"(sessions {', '.join(str(k[4]) for k, _s, _r in found)}); pick one with session=/--session")
    if not found:
        raise ValueError(f"run {run!r} has 0 HSD frame rows on side {side!r}; "
                         "was hsd_md_cl_trace 1 set during the trial?")
    key, stream, frames = found[0]
    ses = key[4]
    if len(frames) < 2:
        raise ValueError(f"run {run!r} has {len(frames)} HSD frame rows on side {side!r}; "
                         "was hsd_md_cl_trace 1 set during the trial?")
    ent = key[3] if side == "sv" else None
    mts = [r for key, srows in streams(rows).items()
           if key[0] == "MT" and key[1] == side and key[4] == ses and (ent is None or key[3] == ent)
           for r in srows if not r.get("replay") and r.get("wall") is not None]
    mts.sort(key=lambda r: (r["wall"], r.get("_rank", 0), r.get("line_no", 0)))
    cmds = {}
    j = 0
    prev_cmd = None
    for f in stream:
        if f is frames[0] and j:
            prev_cmd = mts[j - 1]   # the last usercmd before the trial
        got = []
        if f.get("wall") is not None:
            while j < len(mts) and mts[j]["wall"] <= f["wall"]:
                got.append(mts[j])
                j += 1
        cmds[id(f)] = got
    return frames, cmds, prev_cmd, ses, len(mts)


def _stance(duck):
    return {0: "standing", 2: "crouched"}.get(duck, f"duck_state_{duck}" if duck is not None else "unknown")


def _initial_state(frames, cmds, prev_cmd, stream_prev):
    """State before step 0: the pre-move MT state of the first usercmd when
    available, else the HSD frame before the trial, else step 0 minus vel*dt."""
    f0 = frames[0]
    c0 = (cmds.get(id(f0)) or [None])[0]
    angle_row = stream_prev or f0
    st = OrderedDict()
    if c0 is not None:
        st["source"] = "MT pre-move state of the first usercmd of step 0 (o= v= ge= slide= spr= duck=)"
        st["cmd"] = c0["cmd"]
        st["pos"] = [_f(c0.get(k)) for k in ("ox", "oy", "oz")]
        st["vel"] = [_f(c0.get(k)) for k in ("vx", "vy", "vz")]
        st["grounded"], st["sliding"], st["sprinting"] = _b(c0.get("ground")), _b(c0.get("slide")), _b(c0.get("sprint"))
        st["duck_state"] = c0.get("duck")
        st["stance"] = _stance(c0.get("duck"))
    elif stream_prev is not None:
        st["source"] = "HSD frame before step 0"
        st["cmd"] = None
        st["pos"] = [_f(stream_prev.get(k)) for k in ("ox", "oy", "oz")]
        st["vel"] = [_f(stream_prev.get(k)) for k in ("vx", "vy", "vz")]
        st["grounded"], st["sliding"], st["sprinting"] = (_b(stream_prev.get("ground")), _b(stream_prev.get("slide")),
                                                          _b(stream_prev.get("sprint")))
        st["duck_state"] = None
        st["stance"] = "crouched" if stream_prev.get("crouch") == 1 else ("standing" if stream_prev.get("crouch") == 0 else "unknown")
    else:
        dt = f0.get("ft") or 0.0
        st["source"] = "estimated: step 0 position minus velocity * dt (no earlier sample)"
        st["cmd"] = None
        st["pos"] = [_f(f0[p] - f0[v] * dt) if f0.get(p) is not None and f0.get(v) is not None else ""
                     for p, v in (("ox", "vx"), ("oy", "vy"), ("oz", "vz"))]
        st["vel"] = [_f(f0.get(k)) for k in ("vx", "vy", "vz")]
        st["grounded"], st["sliding"], st["sprinting"] = _b(f0.get("ground")), _b(f0.get("slide")), _b(f0.get("sprint"))
        st["duck_state"] = None
        st["stance"] = "unknown"
    st["crouched"] = _b(angle_row.get("crouch"))
    st["angles"] = OrderedDict([("pitch", _f(angle_row.get("pitch"))), ("yaw", _f(angle_row.get("yaw")))])
    st["angles_source"] = "HSD frame before step 0" if stream_prev is not None else "HSD frame of step 0"
    if prev_cmd is not None:
        st["buttons_held"] = int(prev_cmd["buttons"])
        st["inputs_held"] = _join(held_inputs(prev_cmd["buttons"], prev_cmd.get("fwd"), prev_cmd.get("sidemove")))
        st["inputs_source"] = f"MT usercmd {prev_cmd['cmd']} (the command before step 0)"
    else:
        st["buttons_held"] = 0
        st["inputs_held"] = ""
        st["inputs_source"] = "no usercmd before the trial was logged: nothing held is assumed"
    return st


def _map_name(rows, side, session, wall):
    """Last level load of this side and session at or before wall, else any."""
    maps = [r for r in rows if r["source"] == "LOG" and r.get("kind") == "map" and r.get("side") == side
            and r.get("session") == session]
    before = [r for r in maps if r.get("wall") is not None and wall is not None and r["wall"] <= wall]
    pick = (before or maps)
    return pick[-1]["value"] if pick else ""


def export_trial(rows, run, out_dir, side="cl", trial_id=None, source="r5flowstate", experiment="",
                 parameters=None, notes="", parameter_issues=None, parameters_side=None, session=None,
                 course_note="", map_name=None):
    """Build a trial from the HSD frame stream of one run (inputs + time + state),
    with the usercmd number, held buttons and input edges of each step from the
    MOVE-TRACE lines of the same side and session.

    parameters: {key: {"value", "side", "reader", ...}} as from
    parameters_from_census(). They must come from the trajectory's side unless
    parameters_side names another side on purpose."""
    params_side = parameters_side or side
    for k, p in (parameters or {}).items():
        if not isinstance(p, dict) or p.get("side") not in ("cl", "sv") or not p.get("reader"):
            raise ValueError(f"parameter {k!r} does not say which side/reader produced it")
        if p["side"] != params_side:
            raise ValueError(f"parameter {k!r} was read on side {p['side']!r} but the trajectory is {side!r}; "
                             "use parameters of the same side or pass parameters_side explicitly")
    frames, cmds, prev_cmd, ses, n_mt = _frames_and_cmds(rows, run, side, session)
    stream = [r for key, srows in streams(rows).items()
              if key[0] == "HSD" and key[1] == side and key[2] == "frame" and key[4] == ses for r in srows]
    i0 = next(i for i, r in enumerate(stream) if r is frames[0])
    stream_prev = stream[i0 - 1] if i0 else None
    ev_by_line = {}
    for e in analysis.events(rows):
        if e["source"] == "HSD" and e["side"] == side and e["drv_run"] == run:
            ev_by_line.setdefault((e["file"], e["line_no"]), []).append(e["event"])
    use_cmds = n_mt > 0
    init = _initial_state(frames, cmds, prev_cmd, stream_prev)
    t0 = frames[0]["t"] - (frames[0].get("ft") or 0.0)
    held = _split(init["inputs_held"])
    samples, pending = [], []
    prev_t = t0
    no_cmd = multi = origin_ok = 0
    for i, r in enumerate(frames):
        pending += ev_by_line.get((r["file"], r["line_no"]), [])
        got = cmds.get(id(r), [])
        if use_cmds and not got:
            no_cmd += 1     # no usercmd ran this frame: not a simulation step, its time joins the next one
            continue
        multi += len(got) > 1
        pressed, released = [], []
        for c in got:
            now = held_inputs(c["buttons"], c.get("fwd"), c.get("sidemove"))
            pressed += [n for n in now if n not in held and n not in pressed]
            released += [n for n in held if n not in now and n not in released]
            held = now
        last = got[-1] if got else None
        if last is not None and all(abs(last.get(a, 0) - r.get(b, 1e9)) <= 0.002
                                    for a, b in (("pox", "ox"), ("poy", "oy"), ("poz", "oz"))):
            origin_ok += 1
        dt = r["t"] - prev_t if samples else (r["t"] - t0)
        prev_t = r["t"]
        samples.append(OrderedDict([
            ("step", len(samples)), ("t", _f(r["t"] - t0)), ("dt", _f(dt)),
            ("cmd", last["cmd"] if last else ""), ("n_cmds", len(got) if last else ""),
            ("in_fwd", _f(_axis(r.get("ax_fwd")))),
            ("in_right", _f(_axis(r.get("ax_right")))),
            ("in_yaw", _f(r.get("yaw"))), ("in_pitch", _f(r.get("pitch"))),
            ("in_jump", _b(r.get("in_jump"))), ("in_duck", _b(r.get("in_duck"))),
            ("in_sprint", int(bool(last["buttons"] & IN_SPEED)) if last else ""),
            ("buttons", int(last["buttons"]) if last else ""),
            ("cmd_fwd", _f(last.get("fwd")) if last else ""), ("cmd_side", _f(last.get("sidemove")) if last else ""),
            ("pressed", _join(pressed)), ("released", _join(released)),
            ("pos_x", _f(r.get("ox"))), ("pos_y", _f(r.get("oy"))), ("pos_z", _f(r.get("oz"))),
            ("vel_x", _f(r.get("vx"))), ("vel_y", _f(r.get("vy"))), ("vel_z", _f(r.get("vz"))),
            ("grounded", _b(r.get("ground"))), ("sliding", _b(r.get("slide"))),
            ("crouched", _b(r.get("crouch"))), ("sprinting", _b(r.get("sprint"))),
            ("events", "|".join(pending)),
        ]))
        pending = []
    if len(samples) < 2:
        raise ValueError(f"run {run!r} has {len(samples)} frames with a usercmd on side {side!r}")
    provenance = {c: "obs" for c in SAMPLE_COLUMNS}
    provenance.update({
        "step": "meta", "t": "obs (Time() minus trial start)",
        "dt": "drv (difference of observed Time(); frames without a usercmd are merged into the next step)",
        "events": "drv (hsdtel edge detection)",
        "cmd": "obs MOVE-TRACE cmd= of the last usercmd logged at or before the frame (wall clock)",
        "n_cmds": "drv (count of MOVE-TRACE lines assigned to the frame)",
        "in_fwd": "obs GetInputAxisForward", "in_right": "obs GetInputAxisRight",
        "in_jump": "obs IsInputCommandHeld(IN_JUMP)", "in_duck": "obs IsInputCommandHeld(IN_DUCK)",
        "in_sprint": "obs MOVE-TRACE b= IN_SPEED bit (1<<17) of the step's last usercmd",
        "buttons": "obs MOVE-TRACE b=", "cmd_fwd": "obs MOVE-TRACE fwd=", "cmd_side": "obs MOVE-TRACE sd=",
        "pressed": "drv (MOVE-TRACE b= bits and fwd=/sd= signs, per usercmd, against the previous usercmd)",
        "released": "drv (as pressed)",
    })
    start = init["pos"]
    terrain = OrderedDict([
        ("map", map_name if map_name is not None else _map_name(rows, side, ses, frames[0].get("wall"))),
        ("map_source", "argument" if map_name is not None else "level-load log line of the session (LOG map)"),
        ("start_origin", start),
        ("standable", True if init.get("grounded") == 1 else None),
        ("standable_source", "ground flag at trial start (ge= / IsOnGround); null = not on ground or unknown"),
        ("ground_normal", None),
        ("ground_normal_source", "not recorded: neither MOVE-TRACE nor HSD.MoveDiag prints a surface normal"),
        ("course_note", course_note or ""),
    ])
    manifest = OrderedDict([
        ("contract", CONTRACT_ID),
        ("trial_id", trial_id or f"{source}_{run}"),
        ("source", source),
        ("experiment", experiment),
        ("recorded_side", side),
        ("session", ses),
        ("producer", "hsdtel.contract.export_trial from HSD.MoveDiag v0.2 frames + MOVE-TRACE usercmds"),
        ("space", {"axes": "source_zup_righthanded", "x": "forward at yaw 0", "y": "left", "z": "up",
                   "length_unit": "u", "meters_per_unit": METERS_PER_UNIT, "angle_unit": "deg"}),
        ("timing", OrderedDict([
            ("variable_dt", True), ("steps", len(samples)), ("duration_s", samples[-1]["t"]),
            ("sampling", "one row per client script frame (WaitFrame) that simulated at least one usercmd"),
            ("cmd_first", samples[0]["cmd"]), ("cmd_last", samples[-1]["cmd"]),
            ("frames_without_cmd", no_cmd), ("steps_with_several_cmds", multi),
            ("cmd_association", "usercmds whose MOVE-TRACE wall time is at or before the frame's; "
                                f"post-move origin equals the frame origin in {origin_ok}/{len(samples)} steps"
                                if use_cmds else "none: no MOVE-TRACE rows with a wall clock in this session"),
        ])),
        ("step_semantics", "inputs held during the step; state sampled after the step"),
        ("initial_state", init),
        ("terrain", terrain),
        ("parameters_side", params_side if parameters else None),
        ("parameters", parameters or {}),
        ("parameter_issues", list(parameter_issues or [])),
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


# ---------------------------------------------------------------- load / check
def contract_version(manifest):
    return {CONTRACT_V1: 1, CONTRACT_ID: 2}.get(manifest.get("contract"))


def load_trial(path):
    """(manifest, samples). Samples stay strings as written. A v1 manifest gets
    the v2 keys with None/empty defaults so callers can read them uniformly."""
    with open(os.path.join(path, "trial.json")) as fh:
        manifest = json.load(fh)
    with open(os.path.join(path, "samples.csv"), newline="") as fh:
        samples = list(csv.DictReader(fh))
    if contract_version(manifest) == 1:
        for k, v in (("initial_state", None), ("terrain", None), ("parameters_side", None),
                     ("parameter_issues", []), ("session", None)):
            manifest.setdefault(k, v)
    return manifest, samples


class _Problems:
    """Collects row problems by kind and prints each kind once with examples."""

    def __init__(self):
        self.kinds = OrderedDict()

    def add(self, kind, row):
        self.kinds.setdefault(kind, []).append(row)

    def lines(self):
        out = []
        for kind, rows in self.kinds.items():
            ex = ", ".join(str(r) for r in rows[:5])
            out.append(f"{kind}: {len(rows)} row(s) (first: {ex})")
        return out


def _num(text):
    try:
        v = float(text)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _check_manifest(manifest, version):
    problems = []
    if manifest.get("contract") not in CONTRACT_IDS:
        problems.append(f"contract is {manifest.get('contract')!r}, expected one of {CONTRACT_IDS}")
    space = manifest.get("space", {})
    if space.get("axes") != "source_zup_righthanded" or not space.get("meters_per_unit"):
        problems.append("space.axes/meters_per_unit missing or not the canonical source space")
    if version == 2:
        init = manifest.get("initial_state") or {}
        for k in ("pos", "vel", "angles", "grounded", "stance", "buttons_held", "inputs_held"):
            if k not in init:
                problems.append(f"initial_state.{k} missing")
        for k in ("pos", "vel"):
            v = init.get(k)
            if k in init and (not isinstance(v, list) or len(v) != 3 or any(_num(x) is None for x in v)):
                problems.append(f"initial_state.{k} is not three finite numbers")
        terrain = manifest.get("terrain") or {}
        for k in ("map", "start_origin", "standable", "ground_normal", "course_note"):
            if k not in terrain:
                problems.append(f"terrain.{k} missing")
        pside = manifest.get("parameters_side")
        for k, p in (manifest.get("parameters") or {}).items():
            if not isinstance(p, dict) or p.get("side") not in ("cl", "sv") or not p.get("reader"):
                problems.append(f"parameter {k} has no side/reader")
            elif p["side"] != pside:
                problems.append(f"parameter {k} is from side {p['side']} but parameters_side is {pside}")
    return problems


def check_trial(path):
    """Contract conformance, strict. Returns a list of problem strings (empty = OK).

    Rows: steps consecutive; t strictly increasing (duplicates and backwards
    steps reported); dt > 0 after step 0 and equal to the t difference; state
    columns finite; every sample carries every input column of its version.
    v2 also: usercmd numbers strictly increasing with no gaps (cmd - previous
    cmd == n_cmds), and pressed/released contain every edge implied by the held
    buttons/axes (no missing edges)."""
    try:
        manifest, samples = load_trial(path)
    except (OSError, ValueError) as e:
        return [f"unreadable trial: {e}"]
    version = contract_version(manifest) or 2
    problems = _check_manifest(manifest, version)
    if not samples:
        return problems + ["no samples"]
    cols = list(samples[0].keys())
    need = REQUIRED + INPUTS[version] + (EDGE_COLUMNS if version == 2 else [])
    for c in need:
        if c not in cols:
            problems.append(f"missing {'required' if c in REQUIRED else 'input'} column {c}")
    for c in cols:
        if c not in manifest.get("provenance", {}):
            problems.append(f"column {c} has no provenance entry")
    if problems:
        return problems
    pr = _Problems()
    prev_t = prev_cmd = None
    held = _split((manifest.get("initial_state") or {}).get("inputs_held", ""))
    init_cmd = (manifest.get("initial_state") or {}).get("cmd")
    for i, s in enumerate(samples):
        if _num(s["step"]) != i:
            pr.add("step not consecutive", i)
        t, dt = _num(s["t"]), _num(s["dt"])
        if t is None or dt is None:
            pr.add("t/dt not numeric", i)
        else:
            if prev_t is not None:
                if t == prev_t:
                    pr.add("duplicate t", i)
                elif t < prev_t:
                    pr.add("t goes backwards", i)
                if dt <= 0:
                    pr.add("dt <= 0", i)
                elif abs(dt - (t - prev_t)) > 2e-6 + 1e-6 * abs(t):
                    pr.add("dt differs from the t difference", i)
            elif dt < 0:
                pr.add("dt < 0", i)
            prev_t = t
        if any(_num(s[c]) is None for c in STATE):
            pr.add("non-numeric/non-finite state value", i)
        missing = [c for c in INPUTS[version] if s.get(c) in (None, "")]
        if missing:
            pr.add(f"input missing ({','.join(missing[:4])})", i)
        if version == 2:
            cmd, n = _num(s["cmd"]), _num(s["n_cmds"])
            if cmd is not None:
                if prev_cmd is not None:
                    if cmd == prev_cmd:
                        pr.add("duplicate cmd", i)
                    elif cmd < prev_cmd:
                        pr.add("cmd goes backwards", i)
                    elif cmd - prev_cmd != (n if n is not None else 1):
                        pr.add("cmd gap (usercmds missing between steps)", i)
                elif init_cmd is not None and n is not None and cmd - init_cmd + 1 != n:
                    pr.add("cmd gap (usercmds missing between steps)", i)
                prev_cmd = cmd
            b, f, sd = _num(s["buttons"]), _num(s["cmd_fwd"]), _num(s["cmd_side"])
            if b is not None and f is not None and sd is not None:
                now = held_inputs(int(b), f, sd)
                n_cmds = n if n is not None else 1
                pressed, released = _split(s["pressed"]), _split(s["released"])
                # with one usercmd per step the edges are exact; with several only the net change is implied
                want_p = [x for x in now if x not in held]
                want_r = [x for x in held if x not in now]
                if any(x not in pressed for x in want_p) or any(x not in released for x in want_r):
                    pr.add("missing input edge", i)
                elif n_cmds == 1 and (sorted(pressed) != sorted(want_p) or sorted(released) != sorted(want_r)):
                    pr.add("spurious input edge", i)
                held = now
    return problems + pr.lines()


# ---------------------------------------------------------------- compare
def _vec(s, p):
    return float(s[p + "_x"]), float(s[p + "_y"]), float(s[p + "_z"])


def _has_cmds(samples):
    return bool(samples) and "cmd" in samples[0] and all(s.get("cmd") not in (None, "") for s in samples)


def align(ref, test):
    """Pairs of (ref sample, test sample). By usercmd number when both trials
    carry cmd on every row, else by step index. Any difference in length or in
    the usercmd sequence is a failure: nothing is truncated or skipped.
    Returns (pairs or None, {"by", "ok", "message"})."""
    if _has_cmds(ref) and _has_cmds(test):
        rc, tc = [s["cmd"] for s in ref], [s["cmd"] for s in test]
        info = OrderedDict([("by", "cmd")])
        if rc == tc:
            info.update(ok=True, message=f"{len(rc)} steps, usercmd {rc[0]}..{rc[-1]} in both")
            return list(zip(ref, test)), info
        rs, ts = set(rc), set(tc)
        only_r = [c for c in rc if c not in ts]
        only_t = [c for c in tc if c not in rs]
        msg = (f"usercmd sequences differ: ref {len(rc)} steps (cmd {rc[0]}..{rc[-1]}), "
               f"test {len(tc)} steps (cmd {tc[0]}..{tc[-1]}); only in ref: {len(only_r)} {only_r[:5]}, "
               f"only in test: {len(only_t)} {only_t[:5]}")
        if not only_r and not only_t:
            msg += "; same commands in a different order or repeated"
        info.update(ok=False, message=msg)
        return None, info
    info = OrderedDict([("by", "step")])
    if len(ref) != len(test):
        info.update(ok=False, message=f"length mismatch: ref {len(ref)} steps vs test {len(test)} steps "
                                      "(no usercmd numbers on both sides to align by; nothing is truncated)")
        return None, info
    if not ref:
        info.update(ok=False, message="no samples")
        return None, info
    info.update(ok=True, message=f"{len(ref)} steps aligned by step index (no usercmd numbers on both sides)")
    return list(zip(ref, test)), info


def compare_trials(ref_path, test_path, tolerances=None):
    """Aligned comparison of a test trial (e.g. a Unity replay) against a
    reference trial (e.g. an R5 recording). Alignment is by usercmd number (or
    step index without cmd), and a length/sequence mismatch fails the comparison."""
    tol = dict(DEFAULT_TOLERANCES, **(tolerances or {}))
    _, ref = load_trial(ref_path)
    _, test = load_trial(test_path)
    out = OrderedDict([("steps_ref", len(ref)), ("steps_test", len(test))])
    out["conformance"] = OrderedDict([("ref", check_trial(ref_path)), ("test", check_trial(test_path))])
    pairs, info = align(ref, test)
    out["alignment"] = info
    if pairs is None:
        out["checks"] = OrderedDict([("alignment", False),
                                     ("conformance", not out["conformance"]["ref"] and not out["conformance"]["test"])])
        out["tolerances"] = tol
        out["pass"] = False
        return out
    n = len(pairs)
    pe = ve = 0.0
    spd_max = 0.0
    gmis = gcount = 0
    for a, b in pairs:
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

    def ev_steps(side, name):
        return [i for i, p in enumerate(pairs) if name in (p[side].get("events") or "").split("|")]

    worst = 0
    ev_ok = True
    for name in ("TAKEOFF", "LAND", "SLIDE_START", "SLIDE_END"):
        ra, tb = ev_steps(0, name), ev_steps(1, name)
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
        ("alignment", True),
        ("conformance", not out["conformance"]["ref"] and not out["conformance"]["test"]),
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


# ---------------------------------------------------------------- parameters
def parameters_from_census_rows(census_rows, side="cl", experiment="E0"):
    """census rows -> (parameters, issues) for one side.

    Each parameter carries the side and the reader that produced it
    (analysis.CENSUS_READERS: cl_classvar, cl_setting, sv_setting). Within the
    client, the class var (the live block the movement code reads) wins over the
    script settings getter. A key with no reading on the requested side is left
    out and reported; a reading that differs from the other side is kept for this
    side, flagged side_mismatch and reported. Nothing is filled in across sides."""
    readers = [r for r, (s, _d) in analysis.CENSUS_READERS.items() if s == side]
    others = [r for r, (s, _d) in analysis.CENSUS_READERS.items() if s != side]
    params, issues = OrderedDict(), []
    for row in census_rows:
        key = row.get("key")
        have = OrderedDict((r, row.get(r)) for r in analysis.CENSUS_READERS if row.get(r) not in (None, "", "-"))
        if not key or not have:
            continue
        other = OrderedDict((r, v) for r, v in have.items() if r in others)
        pick = next((r for r in readers if r in have), None)
        if pick is None:
            issues.append(f"{key}: no {side} reading (other side: "
                          + ", ".join(f"{r}={v}" for r, v in other.items()) + "); left out")
            continue
        mine = analysis.census_number(have[pick])
        mismatch = [r for r, v in other.items() if analysis.values_differ([mine, analysis.census_number(v)])]
        same_side = [r for r in readers if r in have and r != pick]
        params[key] = OrderedDict([
            ("value", have[pick]), ("side", side), ("reader", pick),
            ("reader_desc", analysis.CENSUS_READERS[pick][1]), ("type", row.get(pick + "_type")),
            ("differs_between_readers", str(row.get("differs")) == "1"),
            ("same_side_readings", OrderedDict((r, have[r]) for r in same_side)),
            ("other_side_readings", other),
            ("side_mismatch", bool(mismatch)),
            ("experiment", experiment),
        ])
        if mismatch:
            issues.append(f"{key}: {side} {pick}={have[pick]} differs from "
                          + ", ".join(f"{r}={other[r]}" for r in mismatch) + f" (kept the {side} value)")
    return params, issues


def parameters_from_census(path, experiment="E0", side="cl"):
    """census.csv (from 'census'/'report') -> (parameters, issues); see
    parameters_from_census_rows()."""
    with open(path, newline="") as fh:
        return parameters_from_census_rows(list(csv.DictReader(fh)), side, experiment)
