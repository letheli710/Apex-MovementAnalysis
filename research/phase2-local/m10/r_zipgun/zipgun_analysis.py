#!/usr/bin/env python3
"""M10 track R (2) Pathfinder Zipline Gun (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 zipgun_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader: ../r_grapple/m10_load.py (M6-A2 raw-log loader) + the dedi [M10-ZIP] lines (10 Hz: gun
ropes = script name zipline_start origin > linked zipline_end origin, the player's zipline flag / origin / velocity, ult clip)
and the reset line of runner.json (ropes in the world before the reset, ult mods, clip).
- fire: a rope is 'created' when a zipline_start appears after the reset (the m10_z_keep* trials keep the earlier ropes); the
  rope geometry is the last logged one (the end station animates for ~0.2 s); slope = atan(dz / dxy) of start -> end
- regen: ult clip after the fire, slope of clip vs dedi time
- ride (client per-frame HSD-MD + HSD-STATE zip flag; the ride is a gap in MOVE-TRACE, M6-A3): mount = first zip frame;
  speed series along the ride; exit = the client frame 0.1 s after the last zip frame (velocity; includes 0.1 s of gravity)
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "r_grapple")))
import m10_load  # noqa: E402

FLOOR = 294.92
OUT = []
ROPE_RE = re.compile(r"rope=(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)>(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)")


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=2):
    return None if x is None else round(x, n)


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": m, "sd": sd, "min": min(vals), "max": max(vals)}


def fmt(s, nd=1):
    if not s or s.get("n", 0) == 0:
        return "n=0"
    if s["n"] == 1:
        return "%.*f (n=1)" % (nd, s["mean"])
    return "%.*f (sd %.*f, %.*f..%.*f, n=%d)" % (nd, s["mean"], nd, s["sd"], nd, s["min"], nd, s["max"], s["n"])


def zip_lines(folder):
    out = {}
    for f in sorted(m10_load.L._files(folder, "server", "script")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[M10-ZIP]" not in raw or " error " in raw:
                    continue
                body = raw.split("[M10-ZIP]", 1)[1]
                kv = dict(re.findall(r"(\w+)=([^\s>]+)", ROPE_RE.sub("", body)))
                ropes = [tuple(float(x) for x in m) for m in ROPE_RE.findall(body)]
                out.setdefault(int(kv["run"]), []).append({"t": float(kv["t"]), "zip": int(kv["zip"]), "clip": int(kv["clip"]),
                                                           "o": tuple(float(x) for x in kv["o"].split(",")),
                                                           "v": tuple(float(x) for x in kv["v"].split(",")), "ropes": ropes})
    return out


def row(T, Z, trial_meta):
    E = {"run": T["run"], "schedule": T["schedule"]}
    reset = trial_meta.get("reset", "")
    m = re.search(r"ropes_before=(\d+)", reset)
    E["ropes_before_reset"] = int(m.group(1)) if m else None
    E["ult_mods"] = re.findall(r"mod:(\S+)", reset)
    m = re.search(r"clip=(\d+)/(\d+)", reset)
    E["clip_reset"] = "%s/%s" % (m.group(1), m.group(2)) if m else None
    zs = Z.get(T["run"], [])
    if not zs:
        return E
    keep = T["schedule"].startswith("m10_z_keep")
    n0 = len(zs[0]["ropes"])
    E["ropes_first_line"] = n0
    E["ropes_last_line"] = len(zs[-1]["ropes"])
    t_fire = next((q["t"] for q in zs if q["clip"] < zs[0]["clip"]), None)
    E["clip_dropped"] = t_fire is not None
    E["created"] = len(zs[-1]["ropes"]) > (n0 if keep else 0)
    if E["created"]:
        new = zs[-1]["ropes"][-1] if keep else zs[-1]["ropes"][0]
        a, b = new[:3], new[3:]
        dxy = math.hypot(b[0] - a[0], b[1] - a[1])
        E["rope_start"] = [r(x, 1) for x in a]
        E["rope_end"] = [r(x, 1) for x in b]
        E["rope_len"] = r(math.dist(a, b), 1)
        E["rope_slope_deg"] = r(math.degrees(math.atan2(b[2] - a[2], dxy)), 2)
        E["start_above_floor"] = r(a[2] - FLOOR, 1)
        E["start_offset_xy"] = r(math.hypot(a[0] - T["cmds"][0]["ox"], a[1] - T["cmds"][0]["oy"]), 1) if T["cmds"] else None
        t_rope = next((q["t"] for q in zs if len(q["ropes"]) > (n0 if keep else 0)), None)
        E["rope_seen_after_fire_s"] = r(t_rope - t_fire, 2) if t_rope is not None and t_fire is not None else None
    if t_fire is not None:
        cl = [(q["t"], q["clip"]) for q in zs if q["t"] > t_fire + 0.5]
        if len(cl) > 5:
            E["regen_per_s"] = r((cl[-1][1] - cl[0][1]) / (cl[-1][0] - cl[0][0]), 3)
    # ride from client frames and states
    st = T["states"]
    fr = T["frames"]
    zt = [s["t"] for s in st if s.get("zip")]
    if zt:
        t0, t1 = zt[0], zt[-1]
        E["mount_t"] = r(t0, 3)
        ride = [f for f in fr if t0 - 1e-6 <= f["t"] <= t1 + 1e-6]
        sp = [(f["t"] - t0, math.sqrt(f["vx"] ** 2 + f["vy"] ** 2 + f["vz"] ** 2)) for f in ride]
        E["ride_s"] = r(t1 - t0, 3)
        E["ride_max_speed"] = r(max(s for _, s in sp), 1) if sp else None
        for q in (0.25, 0.5, 1.0, 1.5, 2.0):
            x = next((s for tt, s in sp if tt >= q), None)
            E["speed_%.2fs" % q] = r(x, 1)
        # the zip flag drops a frame or two before the detach / jump-off velocity shows: take the frame 0.1 s after the ride
        after = [f for f in fr if f["t"] > t1 + 0.1 - 1e-6]
        if after:
            f = after[0]
            E["exit_v"] = [r(f["vx"], 1), r(f["vy"], 1), r(f["vz"], 1)]
            E["exit_vh"] = r(math.hypot(f["vx"], f["vy"]), 1)
            E["exit_speed"] = r(math.sqrt(f["vx"] ** 2 + f["vy"] ** 2 + f["vz"] ** 2), 1)
            E["exit_heading"] = r(math.degrees(math.atan2(f["vy"], f["vx"])), 1)
            if E.get("rope_end"):
                E["exit_dist_to_end"] = r(math.dist((f["ox"], f["oy"], f["oz"]), tuple(E["rope_end"])), 1)
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    say("# M10 R2 zipline gun analysis")
    rows = []
    for f in a.sessions:
        S = m10_load.load(f)
        Z = zip_lines(f)
        meta = {t["run"]: t for t in S["runner"]["trials"]}
        sc = [t for t in S["runner"]["trials"] if not t.get("warmup")]
        bad = [t for t in sc if not t.get("ok")]
        say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(bad),
                                                        ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in bad]))
        for T in S["trials"]:
            if T["schedule"].startswith("m10_z"):
                rows.append(row(T, Z, meta[T["run"]]))
    say("\n## 1. Per trial")
    for E in rows:
        say("r%d %-20s created %s clip_drop %s ropes(before reset/first/last) %s/%s/%s len %s slope %s start_h %s start_xy %s seen %s s regen %s | ride %s s max %s v@0.5 %s v@1 %s v@1.5 %s exit %s (%s) dist_end %s" % (
            E["run"], E["schedule"][6:], E.get("created"), E.get("clip_dropped"), E.get("ropes_before_reset"), E.get("ropes_first_line"),
            E.get("ropes_last_line"), E.get("rope_len"), E.get("rope_slope_deg"), E.get("start_above_floor"), E.get("start_offset_xy"),
            E.get("rope_seen_after_fire_s"), E.get("regen_per_s"), E.get("ride_s"), E.get("ride_max_speed"), E.get("speed_0.50s"),
            E.get("speed_1.00s"), E.get("speed_1.50s"), E.get("exit_v"), E.get("exit_speed"), E.get("exit_dist_to_end")))
    say("\n## 2. Groups")
    groups = {}
    for E in rows:
        groups.setdefault(E["schedule"], []).append(E)
    res = {"trials": rows, "groups": {}}
    for n in sorted(groups):
        g = groups[n]
        keys = ("rope_len", "rope_slope_deg", "start_above_floor", "ride_max_speed", "speed_0.50s", "speed_1.00s", "speed_1.50s",
                "exit_speed", "exit_vh", "exit_heading", "regen_per_s", "rope_seen_after_fire_s")
        s = {k: stats([E.get(k) for E in g]) for k in keys}
        res["groups"][n] = {"created": sum(1 for E in g if E.get("created")), "n": len(g),
                            **{k: {q: r(w, 3) for q, w in v.items()} for k, v in s.items() if v["n"]}}
        say("%-20s created %d/%d | len %s | slope %s | start_h %s | ride max %s | v@1s %s | exit %s | exit heading %s" % (
            n[6:], res["groups"][n]["created"], len(g), fmt(s["rope_len"]), fmt(s["rope_slope_deg"], 2), fmt(s["start_above_floor"]),
            fmt(s["ride_max_speed"]), fmt(s["speed_1.00s"]), fmt(s["exit_speed"]), fmt(s["exit_heading"])))
    say("\nult mods seen at the resets: %s" % sorted(set(m for E in rows for m in E.get("ult_mods", []))))
    say("regen (clip units per s after a fire): %s" % fmt(stats([E.get("regen_per_s") for E in rows]), 3))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Pathfinder Zipline Gun, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; zipgun_analysis.py"}
        for key, n, field, unit in (("rope.start_above_floor", "m10_z_fire_d1500", "start_above_floor", "u"),
                                    ("ride.speed_0.5s", "m10_z_ride_d1500", "speed_0.50s", "u/s"), ("ride.speed_1.0s", "m10_z_ride_d1500", "speed_1.00s", "u/s"),
                                    ("ride.speed_1.5s", "m10_z_ride_d1500", "speed_1.50s", "u/s"), ("ride.max_flat_1475", "m10_z_ride_d1500", "ride_max_speed", "u/s"),
                                    ("exit.flat", "m10_z_ride_d1500", "exit_speed", "u/s"), ("exit.steep52_vertical", "m10_z_ride_s50", "exit_speed", "u/s"),
                                    ("jumpoff.flat", "m10_z_ride_jump", "exit_vh", "u/s"), ("regen.clip_per_s", None, "regen_per_s", "1/s")):
            st = stats([E.get(field) for E in rows if (n is None or E["schedule"] == n)])
            if st["n"]:
                P[key] = {"value": r(st["mean"], 3), "unit": unit, "evidence": "meas", "n": st["n"],
                          "spread": {"sd": r(st["sd"], 3), "min": r(st["min"], 3), "max": r(st["max"], 3)}, "schedule": n}
        for n in ("m10_z_fire_d600", "m10_z_fire_d800", "m10_z_wall_d600", "m10_z_wall_d800", "m10_z_fire_air"):
            g = [E for E in rows if E["schedule"] == n]
            P["fire." + n[6:]] = {"value": "%d/%d ropes" % (sum(1 for E in g if E.get("created")), len(g)), "evidence": "meas", "n": len(g)}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
