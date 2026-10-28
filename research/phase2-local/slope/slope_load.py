"""R6 slope slide: load raw sessions (a2_load) and attach the lane surface to every usercmd.

Per scored trial: lane name (from the schedule), and per client first-time usercmd a row with the pre / post origin and
velocity, flags, buttons, dt, and the designed surface under the pre and post origin (height, rise angle along +X, normal).
stdlib only; no local paths.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "m6", "a2_climb")))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "tools")))
import a2_load as L  # noqa: E402
import slope_geo as G  # noqa: E402

G_SV = 750.0                      # sv_gravity (census); Gibraltar gravityScale 1
IN_JUMP, IN_DUCK, IN_FORWARD, IN_SPEED = 0x2, 0x4, 0x8, 1 << 15


def lane_of(schedule):
    s = schedule[3:]                                   # r6_<lane>_<kind>
    for name in sorted(G.LANES, key=len, reverse=True):
        if s.startswith(name + "_"):
            return name
    if s.startswith("diag20"):
        return "lat20"
    raise ValueError(schedule)


def surface(lane, x, y):
    """(z, rise_deg, normal) of the lane at (x, y); None outside the lane footprint."""
    _, yc, _, w, _ = G.LANES[lane]
    if abs(y - yc) > w / 2 + 1e-6:
        return None
    z, rise = G.surface_z(lane, x)
    if z is None:
        return None
    t = math.radians(rise)
    return z, rise, (-math.sin(t), 0.0, math.cos(t))


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def load(folder):
    d = L.load(folder)
    out = []
    for T in d["trials"]:
        sched = T["schedule"] or ""
        if not sched.startswith("r6_"):
            continue
        lane = lane_of(sched)
        rows, t = [], 0.0
        for c in T["cmds"]:
            dt = dt_of(c)
            s0 = surface(lane, c["ox"], c["oy"])
            s1 = surface(lane, c["pox"], c["poy"])
            rows.append({"cmd": c["cmd"], "t": t, "dt": dt, "x": c["ox"], "y": c["oy"], "z": c["oz"],
                         "px": c["pox"], "py": c["poy"], "pz": c["poz"],
                         "vx": c["vx"], "vy": c["vy"], "vz": c["vz"], "pvx": c["pvx"], "pvy": c["pvy"], "pvz": c["pvz"],
                         "ground": c["ground"], "slide": c["slide"], "duck": c["duck"], "sprint": c["sprint"],
                         "buttons": c["buttons"], "fwd": c["fwd"], "msc": c["msc"],
                         "surf0": s0, "surf1": s1,
                         "h0": math.hypot(c["vx"], c["vy"]), "h1": math.hypot(c["pvx"], c["pvy"])})
            t += dt
        out.append({"session": d["folder"], "run": T["run"], "schedule": sched, "lane": lane, "fps": T["fps"],
                    "join": T["join"], "rows": rows})
    return out
