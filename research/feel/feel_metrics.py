"""F1 feel metrics: the same functions run on an R5 trace (trial samples.csv) and on a Unity trace (FeelBatch replay / reference / fun .csv).

A trace is a dict of lists: t, x, y, z, vx, vy, vz, grounded, sliding, events (list of str per row). The inputs (fwd, side, yaw, jump, duck,
sprint) always come from the R5 trial, since Unity replays them.

stdlib only.
"""
import csv
import math

FRAME = 1 / 144


def load_trace(path):
    tr = {k: [] for k in ("t", "x", "y", "z", "vx", "vy", "vz", "grounded", "sliding", "events")}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            tr["t"].append(float(r["t"]))
            for a, b in (("x", "pos_x"), ("y", "pos_y"), ("z", "pos_z"), ("vx", "vel_x"), ("vy", "vel_y"), ("vz", "vel_z")):
                tr[a].append(float(r[b]))
            tr["grounded"].append(int(r["grounded"] or 0))
            tr["sliding"].append(int(r["sliding"] or 0))
            ev = r.get("events") or ""
            tr["events"].append([e for e in ev.replace(";", "|").split("|") if e])
    return tr


def load_inputs(samples_csv):
    inp = {k: [] for k in ("t", "fwd", "side", "yaw", "jump", "duck", "sprint")}
    with open(samples_csv, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            inp["t"].append(float(r["t"]))
            inp["fwd"].append(float(r["cmd_fwd"]))
            inp["side"].append(float(r["cmd_side"]))
            inp["yaw"].append(float(r["in_yaw"]))
            b = int(r["buttons"] or 0)
            inp["jump"].append(int(r["in_jump"] or 0) or int(bool(b & 0x2)))
            inp["duck"].append(int(r["in_duck"] or 0) or int(bool(b & 0x4)))
            inp["sprint"].append(int(r["in_sprint"] or 0) or int(bool(b & ((1 << 15) | (1 << 17)))))
    return inp


def hspeed(tr, i):
    return math.hypot(tr["vx"][i], tr["vy"][i])


def heading(tr, i):
    return math.degrees(math.atan2(tr["vy"][i], tr["vx"][i]))


def event_rows(tr, name):
    return [i for i, ev in enumerate(tr["events"]) if name in ev]


def segments(flags):
    """[start, end) row ranges where flags is truthy."""
    out, s = [], None
    for i, f in enumerate(flags):
        if f and s is None:
            s = i
        elif not f and s is not None:
            out.append((s, i)); s = None
    if s is not None:
        out.append((s, len(flags)))
    return out


def input_edges(inp):
    """Rows where the move input starts / stops / changes direction (the steady phases between them)."""
    edges, prev = [0], (inp["fwd"][0], inp["side"][0])
    for i in range(1, len(inp["t"])):
        cur = (inp["fwd"][i], inp["side"][i])
        if (cur[0] != 0) != (prev[0] != 0) or (cur[1] != 0) != (prev[1] != 0):
            edges.append(i)
        prev = cur
    edges.append(len(inp["t"]))
    return edges


def metrics(tr, inp):
    """Feel metrics of one trace. Lists are per occurrence (per jump, per slide, per steady phase)."""
    n = len(tr["t"])
    m = {}
    # jumps: takeoff speed, apex rise, air time, landing speed
    take, land = event_rows(tr, "TAKEOFF"), event_rows(tr, "LAND")
    m["takeoff_speed"], m["apex_rise"], m["air_time"], m["land_speed"] = [], [], [], []
    for a in take:
        b = next((j for j in land if j > a), None)
        m["takeoff_speed"].append(hspeed(tr, a))
        if b is None:
            continue
        m["apex_rise"].append(max(tr["z"][a:b + 1]) - tr["z"][a])
        m["air_time"].append(tr["t"][b] - tr["t"][a])
        m["land_speed"].append(hspeed(tr, b - 1) if b > 0 else hspeed(tr, b))
    # slides: peak speed, duration, speed at the end
    m["slide_peak"], m["slide_time"], m["slide_end_speed"] = [], [], []
    for a, b in segments(tr["sliding"]):
        if b - a < 3:
            continue
        m["slide_peak"].append(max(hspeed(tr, i) for i in range(a, b)))
        m["slide_time"].append(tr["t"][b - 1] - tr["t"][a])
        m["slide_end_speed"].append(hspeed(tr, b - 1))
    # steady ground phases between input changes (only phases >= 0.4 s fully on the ground and not sliding)
    m["ground_terminal"], m["accel_time90"], m["stop_time"], m["stop_dist"] = [], [], [], []
    ed = input_edges(inp)
    for a, b in zip(ed, ed[1:]):
        if tr["t"][b - 1] - tr["t"][a] < 0.4 or not all(tr["grounded"][a:b]) or any(tr["sliding"][a:b]):
            continue
        moving = inp["fwd"][a] != 0 or inp["side"][a] != 0
        if moving:
            tail = [hspeed(tr, i) for i in range(a, b) if tr["t"][i] >= tr["t"][b - 1] - 0.25]
            v_end = sum(tail) / len(tail)
            m["ground_terminal"].append(v_end)
            v0 = hspeed(tr, a)
            if abs(v_end - v0) > 20:
                target = v0 + 0.9 * (v_end - v0)
                k = next((i for i in range(a, b) if (hspeed(tr, i) - target) * (v_end - v0) >= 0), b - 1)
                m["accel_time90"].append(tr["t"][k] - tr["t"][a])
        elif hspeed(tr, a) > 20:
            k = next((i for i in range(a, b) if hspeed(tr, i) < 1), b - 1)
            m["stop_time"].append(tr["t"][k] - tr["t"][a])
            m["stop_dist"].append(math.hypot(tr["x"][k] - tr["x"][a], tr["y"][k] - tr["y"][a]))
    # air direction changes (lurch / strafe): heading and speed 0.15 s after each airborne input change
    m["air_turn"], m["air_turn_speed"] = [], []
    for e in ed[1:-1]:
        if tr["grounded"][e]:
            continue
        k = next((i for i in range(e, n) if tr["t"][i] >= tr["t"][e] + 0.15), None)
        if k is None or tr["grounded"][k] or e == 0:
            continue
        d = (heading(tr, k) - heading(tr, e - 1) + 540) % 360 - 180
        m["air_turn"].append(d)
        m["air_turn_speed"].append(hspeed(tr, k))
    m["end_speed"] = [hspeed(tr, n - 1)]
    return m


def event_offsets(ref, other, name):
    """Time offset (s) of each event of ref to the nearest same event of other, and the count difference."""
    ra, ob = event_rows(ref, name), event_rows(other, name)
    offs = []
    for a in ra:
        if ob:
            b = min(ob, key=lambda j: abs(other["t"][j] - ref["t"][a]))
            offs.append(other["t"][b] - ref["t"][a])
    return offs, len(ob) - len(ra)


def path_error(ref, other):
    """RMS / max horizontal distance between the two traces row by row, and the speed RMS error."""
    n = min(len(ref["t"]), len(other["t"]))
    d = [math.hypot(ref["x"][i] - other["x"][i], ref["y"][i] - other["y"][i]) for i in range(n)]
    dz = [abs(ref["z"][i] - other["z"][i]) for i in range(n)]
    dv = [hspeed(ref, i) - hspeed(other, i) for i in range(n)]
    rms = lambda xs: math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else 0.0
    return {"path_rms": rms(d), "path_max": max(d) if d else 0.0, "z_max": max(dz) if dz else 0.0, "speed_rms": rms(dv),
            "final_dist": d[-1] if d else 0.0}


# tolerance per metric: (absolute, relative); a difference within max(abs, rel*|R5|) agrees, within 3x is "close"
TOL = {
    "takeoff_speed": (2.0, 0.01), "apex_rise": (1.0, 0.02), "air_time": (FRAME * 1.5, 0.0), "land_speed": (2.0, 0.01),
    "slide_peak": (3.0, 0.01), "slide_time": (FRAME * 3, 0.03), "slide_end_speed": (5.0, 0.02),
    "ground_terminal": (2.0, 0.01), "accel_time90": (FRAME * 3, 0.05), "stop_time": (FRAME * 3, 0.05), "stop_dist": (2.0, 0.05),
    "air_turn": (2.0, 0.0), "air_turn_speed": (3.0, 0.01), "end_speed": (3.0, 0.02),
}
UNIT = {"takeoff_speed": "u/s", "apex_rise": "u", "air_time": "s", "land_speed": "u/s", "slide_peak": "u/s", "slide_time": "s",
        "slide_end_speed": "u/s", "ground_terminal": "u/s", "accel_time90": "s", "stop_time": "s", "stop_dist": "u", "air_turn": "deg",
        "air_turn_speed": "u/s", "end_speed": "u/s"}
NAME_ZH = {"takeoff_speed": "起跳水平速度", "apex_rise": "跳跃高度", "air_time": "滞空时间", "land_speed": "落地前速度",
           "slide_peak": "滑铲峰值速度", "slide_time": "滑铲时长", "slide_end_speed": "滑铲结束速度", "ground_terminal": "地面稳定速度",
           "accel_time90": "加速到 90 % 用时", "stop_time": "停下用时", "stop_dist": "停下距离", "air_turn": "空中转向角（0.15 s 后）",
           "air_turn_speed": "空中转向后速度", "end_speed": "结束时速度"}


def verdict(name, r5, other):
    """'agree' / 'close' / 'differ' / 'count' (different number of occurrences) for one metric list."""
    if len(r5) != len(other):
        return "count", None
    if not r5:
        return None, None
    a, rel = TOL[name]
    worst = 0.0
    for x, y in zip(r5, other):
        tol = max(a, rel * abs(x))
        worst = max(worst, abs(y - x) / tol)
    return ("agree" if worst <= 1 else "close" if worst <= 3 else "differ"), worst
