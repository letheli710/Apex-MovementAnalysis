"""Shared loader for the M4 gravity-lift / grapple / Horizon-passive analysis.

Reuses the verified M2 loader (m2/air_jump/aj_load.py: hsdtel parse + derive, runner.json filter
ok=true and warmup=false, client first-time MOVE-TRACE joined to the client HSD frame that shows each
command's post-state, SAMPLING-PHASE.md join rule) and adds the view pitch of the joined frame.

stdlib only. No local paths: session folders come from the command line.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m2", "air_jump")))
import aj_load  # noqa: E402
from aj_load import IN_JUMP, IN_DUCK, IN_SPEED, stats, fmt, spd  # noqa: E402,F401

IN_OFFHAND1 = 0x200000  # tactical (bit 21)
G = 750.0               # sv_gravity x gravityScale (M2 PARAMETER-TABLE)


def load(folder):
    s = aj_load.load_session(folder)
    for t in s["trials"]:
        cmds, frames = t["cmds"], t["frames"]
        # pitch of the joined frame: same join, frames are matched by time stamp t
        by_t = {f.get("t"): f for f in frames}
        for c in cmds:
            f = by_t.get(c.get("t")) if c.get("join_ok") else None
            c["pitch"] = f.get("pitch") if f else None
        for c in cmds:
            c["t_cmd"] = None
        # time axis: cumulative dt of the client commands (dt from the joined frame; gaps use 1/120)
        tacc = 0.0
        for c in cmds:
            c["t_cmd"] = tacc
            tacc += c["dt"] if c.get("dt") else 1.0 / 120.0
    return s


def first_press(cmds, bit):
    for i in range(len(cmds)):
        if aj_load.pressed(cmds, i, bit):
            return i
    return None


def vh(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def sv_by_cmd(trial):
    return {r["cmd"]: r for r in trial["sv_mt"]}
