"""Raw-log loader for the M6-A2 climb / ledge / mantle / superglide analysis.

load(folder) reads <folder>/runner.json and the raw client / dedi logs under <folder>/platform/logs and returns
per scored trial (ok=true, warmup=false):

- cmds    client first-time MOVE-TRACE usercmds (the first print of each cmd number), joined to the client
          HSD frame that shows each command's post-state (dt = that frame's ft, t = its game time);
- sv      dedi MOVE-TRACE rows of the same cmd numbers (cmd -> row);
- frames  client [HSD-MD] kind=frame lines of the run (one per client frame);
- states  client [HSD-STATE] lines of the run (trav / mant / hang / wr / zip / gr / ph / glide per frame);
- sv_evt  dedi [HSD-MD] kind=evt lines of the run (JUMP, MANTLE, BEGIN/END_WALLRUN, ...);
- mb      [MB-TRIG] / [MB-APPLY] / [MB-CLIMB] / [MB-AUTH] lines of both sides inside the trial's game-time range.

The raw logs are parsed (not report/rows.csv) because rows.csv keeps only 6 significant digits, which loses
position and time precision at |x| > 10000 and t > 100 s. The join follows m2/air_jump/aj_load.py: lines are
ordered by the per-line Plat_FloatTime() stamp of the same process; an HSD frame shows the post-state of the
latest first-time command printed before it; a join is accepted only if exactly one new command lies between
consecutive frames and the frame state equals the command post-state to print precision.

stdlib only; no local paths (the session folder comes from the caller).
"""
import bisect
import glob
import json
import math
import os
import re

PLAT_RE = re.compile(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]\s*\[\s*(-?\d+\.\d+)\]")
MT_RE = re.compile(r"\[MOVE-TRACE\] cmd=(\d+) ent=(\d+) ms=(\S+) spr=(\d) duck=(\d) slide=(\d) ge=(\d) fwd=(\S+) sd=(\S+) "
                   r"b=([0-9A-Fa-f]+) msc=(\S+) o=(\S+) (\S+) (\S+) v=(\S+) (\S+) (\S+) po=(\S+) (\S+) (\S+) "
                   r"pv=(\S+) (\S+) (\S+)")
KV_RE = re.compile(r"(\w+)=(\S+)")
MB_RE = re.compile(r"\[(MB-TRIG|MB-APPLY|MB-CLIMB|MB-AUTH)\]\s*(.*)$")
STATE_RE = re.compile(r"\[HSD-STATE\] run=(\d+) fc=(\d+) t=([\d.]+) (.*)$")
TOL = 0.0016

IN_JUMP, IN_DUCK = 0x2, 0x4
IN_FORWARD, IN_BACK, IN_MOVELEFT, IN_MOVERIGHT = 0x8, 0x10, 0x200, 0x400
IN_SPEED = 1 << 15


def _files(folder, side, stem):
    fs = glob.glob(os.path.join(folder, "platform", "logs", side, "*", stem + "*.log"))
    return [f for f in fs if re.fullmatch(stem + r"(\.\d+)?\.log", os.path.basename(f))]


def _f3(s):
    return [float(x) for x in s.split(",")]


def _parse_hsd(folder, side):
    """[HSD-MD] frame / evt lines and [HSD-STATE] lines of one side, with plat stamps."""
    frames, evts, states = {}, {}, {}
    for f in _files(folder, side, "script"):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[HSD-MD]" in raw:
                    if "kind=frame" not in raw and "kind=evt" not in raw:
                        continue
                    pm = PLAT_RE.match(raw)
                    kv = dict(KV_RE.findall(raw.split("[HSD-MD]", 1)[1]))
                    run = int(kv["run"])
                    o, v = _f3(kv["o"]), _f3(kv["vel"])
                    r = {"plat": float(pm.group(1)) if pm else None, "t": float(kv["t"]), "ox": o[0], "oy": o[1], "oz": o[2],
                         "vx": v[0], "vy": v[1], "vz": v[2], "ground": int(kv.get("ground", 0)),
                         "slide": int(kv.get("slide", 0)), "crouch": int(kv.get("crouch", 0)), "seq": int(kv.get("seq", 0))}
                    if kv["kind"] == "frame":
                        r.update(ft=float(kv["ft"]), in_jump=int(kv["in_jump"]), in_duck=int(kv["in_duck"]),
                                 in_fwd=int(kv["in_fwd"]), ax_fwd=float(kv["ax_fwd"]), ax_right=float(kv["ax_right"]))
                        ang = kv.get("ang")
                        if ang:
                            r["pitch"], r["yaw"] = _f3(ang)
                        frames.setdefault(run, []).append(r)
                    else:
                        r["evt"] = kv["evt"]
                        evts.setdefault(run, []).append(r)
                elif "[HSD-STATE]" in raw:
                    m = STATE_RE.search(raw)
                    if not m:
                        continue
                    kv = dict(KV_RE.findall(m.group(4)))
                    st = {k: (v == "true") for k, v in kv.items() if v in ("true", "false")}
                    st["glide"] = float(kv.get("glide", 0))
                    st.update(fc=int(m.group(2)), t=float(m.group(3)))
                    states.setdefault(int(m.group(1)), []).append(st)
    for d in (frames, evts):
        for k in d:
            d[k].sort(key=lambda r: (r["plat"] if r["plat"] is not None else 0.0, r["seq"]))
    for k in states:
        states[k].sort(key=lambda r: r["fc"])
    return frames, evts, states


def _parse_mt(folder, side, keep):
    """MOVE-TRACE lines of one side. keep(plat, cmd) -> bool decides which lines are stored."""
    out = []
    for f in _files(folder, side, "message"):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[MOVE-TRACE]" not in raw:
                    continue
                m = MT_RE.search(raw)
                if not m:
                    continue
                pm = PLAT_RE.match(raw)
                plat = float(pm.group(1)) if pm else None
                cmd = int(m.group(1))
                if not keep(plat, cmd):
                    continue
                g = m.groups()
                out.append({"plat": plat, "cmd": cmd, "maxspeed": float(g[2]), "sprint": int(g[3]), "duck": int(g[4]),
                            "slide": int(g[5]), "ground": int(g[6]), "fwd": float(g[7]), "sidemove": float(g[8]),
                            "buttons": int(g[9], 16), "msc": float(g[10]),
                            "ox": float(g[11]), "oy": float(g[12]), "oz": float(g[13]),
                            "vx": float(g[14]), "vy": float(g[15]), "vz": float(g[16]),
                            "pox": float(g[17]), "poy": float(g[18]), "poz": float(g[19]),
                            "pvx": float(g[20]), "pvy": float(g[21]), "pvz": float(g[22])})
    out.sort(key=lambda r: (r["plat"] if r["plat"] is not None else 0.0))
    return out


def parse_mb(folder):
    out = []
    for side in ("client", "server"):
        for f in _files(folder, side, "message"):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    if "[MB-" not in raw:
                        continue
                    m = MB_RE.search(raw)
                    if not m:
                        continue
                    body = m.group(2)
                    kv = dict(re.findall(r"(\w+)=(\([^)]*\)|\S+)", body))
                    d = {"tag": m.group(1)[3:], "side": "cl" if side == "client" else "sv", "raw": body.strip()}
                    if "t" in kv:
                        d["t"] = float(kv["t"])
                    if d["tag"] == "TRIG":
                        res = re.search(r"-> (\d)", body)
                        d.update(anim=float(kv["anim"]), delta=float(kv["delta"]), prev=float(kv["prev"]), gate=kv["gate"],
                                 travState=int(kv["travState"]), result=int(res.group(1)) if res else None)
                    elif d["tag"] == "APPLY":
                        d.update(state=int(kv["state"]), speed=float(kv["speed"]), pose=float(kv["pose"]),
                                 vel=[float(x) for x in kv["vel"].strip("()").split()])
                    out.append(d)
    return out


def _close(f, c):
    def tol(a):
        return max(TOL, abs(a) * 2e-6)
    for a, b in (("ox", "pox"), ("oy", "poy"), ("oz", "poz"), ("vx", "pvx"), ("vy", "pvy"), ("vz", "pvz")):
        if abs(f[a] - c[b]) > tol(c[b]) + TOL:
            return False
    return True


def join(cmds, frames):
    cp = [c["plat"] for c in cmds]
    st = {"frames": len(frames), "cmds": len(cmds), "joined": 0, "bad_state": 0, "multi": 0}
    for c in cmds:
        c["dt"], c["t"], c["join_ok"] = None, None, False
    prev_j = None
    for f in frames:
        if f["plat"] is None:
            continue
        j = bisect.bisect_right(cp, f["plat"]) - 1
        if j < 0:
            continue
        nb = j - prev_j if prev_j is not None else 1
        prev_j = j
        c = cmds[j]
        if nb != 1:
            st["multi"] += nb > 1
            continue
        if not _close(f, c):
            st["bad_state"] += 1
            continue
        if c["dt"] is None:
            c["dt"], c["t"], c["join_ok"] = f["ft"], f["t"], True
            c["yaw"] = f.get("yaw")
            st["joined"] += 1
    return st


# Callers that replay the recorded usercmds (feel/camera_to_trial.py) may also take the trials that failed the runner fps check: the
# commands are logged one by one, so the replay does not depend on the frame rate.
INCLUDE_UNSCORED = False


def load(folder):
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    frames, _, states = _parse_hsd(folder, "client")
    _, sv_evts, _ = _parse_hsd(folder, "server")
    scored = [t for t in runner["trials"] if (t.get("ok") or INCLUDE_UNSCORED) and not t.get("warmup")]
    win = []
    for t in scored:
        fr = frames.get(t["run"], [])
        ps = [f["plat"] for f in fr if f["plat"] is not None]
        if ps:
            win.append((min(ps) - 0.05, max(ps) + 0.001, t["run"]))
    win.sort()
    starts = [w[0] for w in win]

    def run_of(plat):
        if plat is None:
            return None
        i = bisect.bisect_right(starts, plat) - 1
        if i >= 0 and plat <= win[i][1]:
            return win[i][2]
        return None

    cl_all = _parse_mt(folder, "client", lambda p, c: run_of(p) is not None)
    cl = {}
    seen = set()
    for r in cl_all:                      # first-time prints only (later prints of the same cmd are replays)
        if r["cmd"] in seen:
            continue
        seen.add(r["cmd"])
        cl.setdefault(run_of(r["plat"]), []).append(r)
    rng = {run: (cs[0]["cmd"], cs[-1]["cmd"]) for run, cs in cl.items() if cs}
    allc = set(c["cmd"] for cs in cl.values() for c in cs)
    sv_all = _parse_mt(folder, "server", lambda p, c: c in allc)
    sv = {}
    for r in sv_all:
        sv.setdefault(r["cmd"], r)
    mb = parse_mb(folder)
    trials = []
    for t in scored:
        run = t["run"]
        cmds = sorted(cl.get(run, []), key=lambda r: r["cmd"])
        fr = frames.get(run, [])
        js = join(cmds, fr)
        ts = [f["t"] for f in fr]
        lo, hi = (min(ts), max(ts)) if ts else (0, 0)
        trials.append({"run": run, "schedule": t.get("schedule"), "fps": t.get("measured_fps"),
                       "sched_lines": t.get("sched_lines", []), "cmds": cmds, "frames": fr, "join": js,
                       "states": states.get(run, []), "sv_evt": sv_evts.get(run, []),
                       "sv": {c["cmd"]: sv[c["cmd"]] for c in cmds if c["cmd"] in sv},
                       "mb": [m for m in mb if "t" in m and lo - 0.01 <= m["t"] <= hi + 0.01]})
    return {"folder": os.path.basename(os.path.normpath(folder)), "runner": runner, "trials": trials,
            "mb_lines_total": len(mb),
            "mb_tags": {f"{s}:{g}": sum(1 for m in mb if m["side"] == s and m["tag"] == g)
                        for s in ("cl", "sv") for g in ("TRIG", "APPLY", "CLIMB", "AUTH")}}


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


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
    if s["n"] == 1:
        return f"{s['mean']:.{nd}f} (n=1)"
    return f"{s['mean']:.{nd}f} (sd {s['sd']:.{nd}f}, {s['min']:.{nd}f}..{s['max']:.{nd}f}, n={s['n']})"
