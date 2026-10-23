"""M10 track R2 loader: the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py, imported unchanged) restricted to the trials a
caller keeps, plus the R2 dedi logger lines.

load(folder, keep) -> like a2_load.load(folder) but only for the scored trials with keep(trial) true (the R2 session folder holds
all R2 sub-runs; each analysis keeps its own schedules). Per kept trial also:
  log    dedi logger rows of the run for the tag given by the caller's `tags` (dict tag -> list of rows), deduplicated by t
  pitch  per usercmd (from the joined client HSD frame)
Session-wide:
  tagged(folder, tag)   all rows of one dedi logger tag, {run: [row, ...]} (key=value parse, t as float, deduplicated by t)
  al_phase(folder)      the SDK [AL-PHASE] lines (Newcastle leap phases) of the dedi message log: (t, kind, a, b, type, end)
stdlib only; no local paths (the folder comes from the caller).
"""
import bisect
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

KV_RE = re.compile(r"(\w+)=(\S+)")
AL_RE = re.compile(r"\[AL-PHASE\] player=\S+ (?:start type=(\d+) end=\(([-\d. ]+)\) timeout=([\d.]+)|type=(\d+) (\d+) -> (\d+) t=([\d.]+))")


def f3(s):
    return tuple(float(x) for x in s.split(","))


def tagged(folder, tag):
    out, seen = {}, set()
    for f in sorted(L._files(folder, "server", "script")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if tag not in raw:
                    continue
                body = raw.split(tag, 1)[1]
                if body.startswith(" error"):
                    continue
                kv = dict(KV_RE.findall(body))
                if "run" not in kv or "t" not in kv:
                    continue
                key = (kv["run"], kv["t"])
                if key in seen:
                    continue
                seen.add(key)
                kv["t"] = float(kv["t"])
                out.setdefault(int(kv["run"]), []).append(kv)
    for k in out:
        out[k].sort(key=lambda r: r["t"])
    return out


def al_phase(folder):
    """[AL-PHASE] lines: start rows (type, end point, timeout, plat) and phase changes (type, from, to, game time t)."""
    rows = []
    for f in sorted(L._files(folder, "server", "message")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[AL-PHASE]" not in raw:
                    continue
                m = AL_RE.search(raw)
                pm = L.PLAT_RE.match(raw)
                if not m:
                    continue
                plat = float(pm.group(1)) if pm else None
                if m.group(1):
                    rows.append({"kind": "start", "type": int(m.group(1)), "end": tuple(float(x) for x in m.group(2).split()),
                                 "timeout": float(m.group(3)), "plat": plat})
                else:
                    rows.append({"kind": "phase", "type": int(m.group(4)), "a": int(m.group(5)), "b": int(m.group(6)),
                                 "t": float(m.group(7)), "plat": plat})
    return rows


def load(folder, keep):
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    frames, _, states = L._parse_hsd(folder, "client")
    _, sv_evts, _ = L._parse_hsd(folder, "server")
    allsc = [t for t in runner["trials"] if not t.get("warmup") and keep(t)]
    scored = [t for t in allsc if t.get("ok")]
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

    cl_all = L._parse_mt(folder, "client", lambda p, c: run_of(p) is not None)
    cl, seen = {}, set()
    for r in cl_all:
        if r["cmd"] in seen:
            continue
        seen.add(r["cmd"])
        cl.setdefault(run_of(r["plat"]), []).append(r)
    allc = set(c["cmd"] for cs in cl.values() for c in cs)
    sv_all = L._parse_mt(folder, "server", lambda p, c: c in allc)
    sv = {}
    for r in sv_all:
        sv.setdefault(r["cmd"], r)
    trials = []
    for t in scored:
        run = t["run"]
        cmds = sorted(cl.get(run, []), key=lambda r: r["cmd"])
        fr = frames.get(run, [])
        js = L.join(cmds, fr)
        by_t = {round(f["t"], 5): f for f in fr}
        for c in cmds:
            f = by_t.get(round(c["t"], 5)) if c.get("t") is not None else None
            c["pitch"] = f.get("pitch") if f else None
        trials.append({"run": run, "schedule": t.get("schedule"), "sub": t.get("sub_label"), "explore": bool(t.get("explore")),
                       "fps": t.get("measured_fps"), "sched_lines": t.get("sched_lines", []), "reset": t.get("reset", ""),
                       "cmds": cmds, "frames": fr, "join": js, "states": states.get(run, []), "sv_evt": sv_evts.get(run, []),
                       "sv": {c["cmd"]: sv[c["cmd"]] for c in cmds if c["cmd"] in sv}})
    excluded = [t for t in allsc if not t.get("ok")]
    return {"folder": os.path.basename(os.path.normpath(folder)), "runner": runner, "trials": trials, "excluded": excluded}


def sched_frame(T, key, nth=0):
    """client frame index (from the schedule start) of the nth edge line containing `key` (e.g. 'key=jump', 'edge=waitph')"""
    hits = [l for l in T["sched_lines"] if key in l and "edge=down" in l or (key.startswith("edge=") and key in l)]
    if len(hits) <= nth:
        return None
    m = re.search(r"frame=(\d+)", hits[nth])
    return int(m.group(1)) if m else None


def sched_t(T, key, nth=0):
    """game time t of the nth schedule edge line containing `key` (down edges for keys)"""
    hits = [l for l in T["sched_lines"] if key in l and ("edge=down" in l or key.startswith("edge="))]
    if len(hits) <= nth:
        return None
    m = re.search(r" t=([\d.]+)", hits[nth])
    return float(m.group(1)) if m else None


def load_many(folders, keep):
    """load() over several session folders (run labels are unique across the R2 sessions); trials concatenated"""
    out = {"folder": " + ".join(os.path.basename(os.path.normpath(f)) for f in folders), "runner": {"trials": []}, "trials": [], "excluded": []}
    for f in folders:
        S = load(f, keep)
        out["runner"]["trials"] += S["runner"]["trials"]
        out["trials"] += S["trials"]
        out["excluded"] += S["excluded"]
    return out


def tagged_many(folders, tag):
    out = {}
    for f in folders:
        for k, v in tagged(f, tag).items():
            out.setdefault(k, []).extend(v)
    return out
