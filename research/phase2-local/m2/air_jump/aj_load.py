"""Shared loader for the M2 air/jump analysis (E2 air control, E4 jump/hop).

load_session(folder) parses <folder>/platform/logs with hsdtel (parse + derive), reads
<folder>/runner.json and returns, per scored trial (ok=true, warmup=false), the client
first-time MOVE-TRACE commands joined to the client HSD frame that shows each command's
post-state. The join gives every command its frametime (dt = HSD ft) and view yaw.

Join rule (research/phase2-local/m1/sampling/SAMPLING-PHASE.md): an HSD client frame shows the
post-state of the latest first-time command printed before it, and ft is that command's
frametime. Ordering uses the per-line Plat_FloatTime() stamp "[wall] [plat]" (1 ms) of
message.log / script.log of the same client process. Each join is validated: the frame's
origin and velocity must equal the command's post-state within the print precision, and
exactly one command must lie between consecutive frames. Commands that fail are kept but
flagged (join_ok=False) and are never given a dt.

stdlib only. No local paths: the session folder comes from the command line.
"""
import bisect
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "phase2-prep", "tools"))
sys.path.insert(0, TOOLS)
from hsdtel import derive, parse  # noqa: E402

IN_JUMP, IN_DUCK, IN_SPEED = 0x2, 0x4, 1 << 15  # sprint is bit 15 in this build (see hsdtel schema.BUTTON_BITS)
PLAT_RE = re.compile(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]\s*\[\s*(-?\d+\.\d+)\]")
TOL = 0.0016  # print precision %.3f (+ rounding of both prints)


def _plat_index(files):
    """(session, basename, line_no) -> plat for MT / HSD lines."""
    out = {}
    for f in files:
        b = os.path.basename(f)
        if not (b.startswith("message") or b.startswith("script")):
            continue
        ses = parse.session_of(f)
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for ln, raw in enumerate(fh, 1):
                if "[MOVE-TRACE]" not in raw and "[HSD-MD]" not in raw:
                    continue
                m = PLAT_RE.match(raw)
                if m:
                    out[(ses, b, ln)] = float(m.group(1))
    return out


def _close(f, c):
    d1 = max(abs(f["ox"] - c["pox"]), abs(f["oy"] - c["poy"]), abs(f["oz"] - c["poz"]))
    d2 = max(abs(f["vx"] - c["pvx"]), abs(f["vy"] - c["pvy"]), abs(f["vz"] - c["pvz"]))
    return max(d1, d2)


def load_session(folder):
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    plat = _plat_index(files)
    for r in rows:
        r["plat"] = plat.get((r.get("session"), r.get("file"), r.get("line_no")))
    errors = [i for i in issues if i.severity == "error"]
    trials = []
    cl_mt, cl_fr, sv_ev, sv_mt = {}, {}, {}, {}
    for r in rows:
        run = r.get("drv_run")
        if r["source"] == "MT" and not r.get("replay"):
            (cl_mt if r.get("side") == "cl" else sv_mt).setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "cl" and r.get("kind") == "frame":
            cl_fr.setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "sv" and r.get("kind") == "evt":
            sv_ev.setdefault(run, []).append(r)
    for t in runner["trials"]:
        if t.get("warmup") or not t.get("ok"):
            continue
        lab = f"r{t['run']}"
        cmds = sorted(cl_mt.get(lab, []), key=lambda r: r["cmd"])
        frames = sorted(cl_fr.get(lab, []), key=lambda r: r["plat"])
        stats = join(cmds, frames)
        trials.append({"run": t["run"], "label": lab, "schedule": t.get("schedule"), "yaw0": t.get("yaw"),
                       "fps": t.get("measured_fps"), "sched_lines": t.get("sched_lines", []),
                       "cmds": cmds, "frames": frames, "join": stats,
                       "sv_evt": sorted(sv_ev.get(lab, []), key=lambda r: r.get("seq", 0)),
                       "sv_mt": sorted(sv_mt.get(lab, []), key=lambda r: r["cmd"])})
    return {"folder": os.path.basename(os.path.normpath(folder)), "trials": trials,
            "parse_errors": len(errors), "census": runner.get("census")}


def join(cmds, frames):
    """Attach dt (ft) and yaw of the frame that shows each command's post-state."""
    cp = [c["plat"] for c in cmds]
    st = {"frames": len(frames), "cmds": len(cmds), "state_ok": 0, "state_bad": 0, "one_cmd": 0,
          "multi_or_zero": 0, "cmds_with_dt": 0}
    for c in cmds:
        c["dt"] = None
        c["yaw"] = None
        c["join_ok"] = False
    prev_j = None
    for f in frames:
        if f.get("plat") is None:
            continue
        j = bisect.bisect_right(cp, f["plat"]) - 1
        if j < 0:
            continue
        n_between = j - prev_j if prev_j is not None else 1
        prev_j = j
        c = cmds[j]
        ok_state = _close(f, c) < TOL
        st["state_ok" if ok_state else "state_bad"] += 1
        if n_between == 1:
            st["one_cmd"] += 1
        else:
            st["multi_or_zero"] += 1
        if ok_state and n_between == 1 and c["dt"] is None:
            c["dt"] = f["ft"]
            c["yaw"] = f.get("yaw")
            c["join_ok"] = True
            c["t"] = f.get("t")
    st["cmds_with_dt"] = sum(1 for c in cmds if c["join_ok"])
    gaps = sum(1 for a, b in zip(cmds, cmds[1:]) if b["cmd"] - a["cmd"] != 1)
    st["cmd_gaps"] = gaps
    return st


def spd(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def pressed(cmds, i, bit):
    return bool(cmds[i]["buttons"] & bit) and (i == 0 or not cmds[i - 1]["buttons"] & bit)


def airborne_segments(cmds):
    """List of (i_takeoff, i_land): i_takeoff = first command whose post ground=0 after a grounded
    pre-state (the jump command), i_land = first command whose post ground=1 again."""
    segs = []
    i = 1
    n = len(cmds)
    while i < n:
        if cmds[i - 1]["ground"] == 1 and cmds[i]["ground"] == 0:
            j = i + 1
            while j < n and cmds[j]["ground"] == 0:
                j += 1
            segs.append((i, j if j < n else None))
            i = j
        else:
            i += 1
    return segs


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": m, "sd": sd, "min": min(vals), "max": max(vals)}


def fmt(s, nd=3):
    if not s or s.get("n", 0) == 0:
        return "n=0"
    return (f"{s['mean']:.{nd}f} (sd {s['sd']:.{nd}f}, {s['min']:.{nd}f}..{s['max']:.{nd}f}, n={s['n']})")
