#!/usr/bin/env python3
"""M10 track R (5) Wraith feasibility: Into the Void regression, Dimensional Rift (portal) placement / travel / exit
(R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 wraith_analysis.py <session> [<session> ...] [--json results.json] > analysis_output.txt

stdlib only, no local paths. Loader: ../r_grapple/m10_load.py + the dedi [M10-WR] lines (10 Hz: speed_boost severity,
placing_phase_tunnel severity, phase flag, ult clip, origin / velocity, portal trace blockers).
- tactical: client usercmd msc series (MOVE-TRACE msc) after the tactical press, as M4 P3; sprint v_h plateau
- portal: placement window = dedi rows with placing > 0; boost steps; end portal placed = blockers 2; travel = dedi rows with
  the phase flag; exit = the first dedi row after the travel (velocity), and the client frames around it
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

IN_OFF1 = 0x200000
OUT = []


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


def fmt(s, nd=2):
    if not s or s.get("n", 0) == 0:
        return "n=0"
    if s["n"] == 1:
        return "%.*f (n=1)" % (nd, s["mean"])
    return "%.*f (sd %.*f, %.*f..%.*f, n=%d)" % (nd, s["mean"], nd, s["sd"], nd, s["min"], nd, s["max"], s["n"])


def wr_lines(folder):
    out = {}
    for f in sorted(m10_load.L._files(folder, "server", "script")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[M10-WR]" not in raw or " error " in raw:
                    continue
                kv = dict(re.findall(r"(\w+)=(\S+)", raw.split("[M10-WR]", 1)[1]))
                out.setdefault(int(kv["run"]), []).append({
                    "t": float(kv["t"]), "boost": float(kv["boost"]), "placing": float(kv["placing"]), "ph": int(kv["ph"]),
                    "clip": int(kv["clip"]), "o": tuple(float(x) for x in kv["o"].split(",")),
                    "v": tuple(float(x) for x in kv["v"].split(",")), "blockers": int(kv["blockers"]), "pre": int(kv["pre"])})
    return out


def void_row(T):
    cs = T["cmds"]
    E = {"run": T["run"], "schedule": T["schedule"]}
    tp = next((i for i in range(1, len(cs)) if cs[i]["buttons"] & IN_OFF1 and not cs[i - 1]["buttons"] & IN_OFF1), None)
    seq = [(c["t"], c["msc"], math.hypot(c["pvx"], c["pvy"])) for c in cs if c.get("t") is not None]
    if tp is None or not seq:
        E["sprint_vh_max"] = r(max(v for _, _, v in seq), 2) if seq else None
        return E
    t0 = cs[tp]["t"]
    after = [(t - t0, m, v) for t, m, v in seq if t >= t0]
    lvl = sorted(set(round(m, 4) for _, m, _ in after))
    E["msc_levels"] = lvl[:8]
    hi = max(m for _, m, _ in after)
    on = next((t for t, m, _ in after if abs(m - hi) < 1e-4), None)
    off = max((t for t, m, _ in after if abs(m - hi) < 1e-4), default=None)
    E["msc_peak"] = r(hi, 4)
    E["peak_from_s"] = r(on, 3)
    E["peak_len_s"] = r(off - on, 3) if on is not None and off is not None else None
    lo = min(m for t, m, _ in after if t < (on or 0) + 1e-6) if on else None
    E["msc_deploy"] = r(lo, 4)
    E["vh_max"] = r(max(v for _, _, v in after), 2)
    return E


def portal_row(T, W):
    E = {"run": T["run"], "schedule": T["schedule"]}
    ws = W.get(T["run"], [])
    if not ws:
        return E
    pl = [q for q in ws if q["placing"] > 0]
    E["placed_start"] = bool(pl)
    if pl:
        E["placing_s"] = r(pl[-1]["t"] - pl[0]["t"] + 0.1, 2)
        E["boost_levels"] = sorted(set(round(q["boost"], 3) for q in pl))
        E["place_vh_max"] = r(max(math.hypot(q["v"][0], q["v"][1]) for q in pl), 1)
        E["place_dist"] = r(math.dist(pl[0]["o"], pl[-1]["o"]), 1)
    E["portal_pair"] = any(q["blockers"] >= 2 for q in ws)
    ph = [q for q in ws if q["ph"]]
    E["travel_rows"] = len(ph)
    if ph:
        E["travel_s"] = r(ph[-1]["t"] - ph[0]["t"] + 0.1, 2)
        E["travel_vh"] = [r(math.hypot(q["v"][0], q["v"][1]), 1) for q in ph]
        nxt = next((q for q in ws if q["t"] > ph[-1]["t"] and not q["ph"]), None)
        if nxt:
            E["exit_v"] = [r(x, 1) for x in nxt["v"]]
            E["exit_vh"] = r(math.hypot(nxt["v"][0], nxt["v"][1]), 1)
            E["exit_o"] = [r(x, 1) for x in nxt["o"]]
    # client side: phase flag frames and velocity at the first frame after the phase
    st = [s for s in T["states"] if s.get("ph")]
    if st:
        t1 = st[-1]["t"]
        fr = [f for f in T["frames"] if f["t"] > t1 + 1e-6]
        if fr:
            f = fr[0]
            E["client_exit_vh"] = r(math.hypot(f["vx"], f["vy"]), 1)
            E["client_exit_vz"] = r(f["vz"], 1)
        E["client_phase_s"] = r(st[-1]["t"] - st[0]["t"], 3)
    # entry speed: client frames 0.3 s before the first phase frame
    if st:
        t0 = st[0]["t"]
        pre = [f for f in T["frames"] if t0 - 0.3 <= f["t"] < t0]
        if pre:
            E["entry_vh"] = r(max(math.hypot(f["vx"], f["vy"]) for f in pre), 1)
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    say("# M10 R5 Wraith feasibility")
    res = {"void": [], "portal": []}
    for f in a.sessions:
        S = m10_load.load(f)
        W = wr_lines(f)
        sc = [t for t in S["runner"]["trials"] if not t.get("warmup")]
        bad = [t for t in sc if not t.get("ok")]
        say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(bad),
                                                        ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in bad]))
        for T in S["trials"]:
            if T["schedule"] in ("m10_w_void", "m10_w_ctrl"):
                res["void"].append(void_row(T))
            elif T["schedule"].startswith("m10_w_portal"):
                res["portal"].append(portal_row(T, W))
    say("\n## 1. Into the Void (tactical) vs control")
    for E in res["void"]:
        say("  r%d %-10s msc deploy %s peak %s from %s s for %s s | v_h max %s | levels %s" % (
            E["run"], E["schedule"][6:], E.get("msc_deploy"), E.get("msc_peak"), E.get("peak_from_s"), E.get("peak_len_s"),
            E.get("vh_max", E.get("sprint_vh_max")), E.get("msc_levels")))
    say("\n## 2. Portal")
    for E in res["portal"]:
        say("  r%d %-18s start placed %s placing %s s dist %s boost %s place v_h max %s | pair %s | travel %s s (client %s s) v_h %s | exit v %s (vh %s; client vh %s vz %s) entry vh %s" % (
            E["run"], E["schedule"][6:], E.get("placed_start"), E.get("placing_s"), E.get("place_dist"), E.get("boost_levels"),
            E.get("place_vh_max"), E.get("portal_pair"), E.get("travel_s"), E.get("client_phase_s"), E.get("travel_vh"), E.get("exit_v"),
            E.get("exit_vh"), E.get("client_exit_vh"), E.get("client_exit_vz"), E.get("entry_vh")))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Wraith, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; wraith_analysis.py"}
        vd = [E for E in res["void"] if E["schedule"] == "m10_w_void"]
        for key, field in (("void.msc_deploy", "msc_deploy"), ("void.msc_peak", "msc_peak"), ("void.peak_from_s", "peak_from_s"),
                           ("void.peak_len_s", "peak_len_s"), ("void.vh_max", "vh_max")):
            st = stats([E.get(field) for E in vd])
            if st["n"]:
                P[key] = {"value": r(st["mean"], 4), "spread": {"sd": r(st["sd"], 4)}, "evidence": "meas", "n": st["n"]}
        pt = [E for E in res["portal"] if E["schedule"] != "m10_w_portal_hold"]
        for key, field in (("portal.place_vh_max", "place_vh_max"), ("portal.exit_vh_dedi", "exit_vh"), ("portal.client_exit_vh", "client_exit_vh"),
                           ("portal.entry_vh", "entry_vh")):
            st = stats([E.get(field) for E in pt])
            if st["n"]:
                P[key] = {"value": r(st["mean"], 3), "spread": {"sd": r(st["sd"], 3), "min": r(st["min"], 3), "max": r(st["max"], 3)}, "evidence": "meas", "n": st["n"]}
        P["portal.placing_boost_severity"] = {"value": sorted(set(b for E in pt for b in E.get("boost_levels", []))), "evidence": "meas (dedi)", "n": len(pt)}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
