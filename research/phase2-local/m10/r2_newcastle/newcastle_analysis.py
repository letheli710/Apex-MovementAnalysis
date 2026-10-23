#!/usr/bin/env python3
"""M10 track R2: Newcastle Castle Wall leap (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 newcastle_analysis.py <session> [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader ../r2_common/r2_load.py; dedi logger [M10R2-NC] (per dedi frame: origin, velocity, ground,
ult clip, wall entity count), [M10R2-NI] (interruption helper), and the SDK leap trace [AL-PHASE] (dedi message log, cvar
bridge_armored_leap_trace 2): start type (1 = ground dash, 2 = jump), end point, timeout; phase changes with game time
(1 prep, 2 air travel, 3 air hover, 4 ground travel / slam, 5 arrival, 6 interrupted, 0 none).
On this build the dedi leap is the SDK twin (s21-r5sdk armored_leap.cpp, "follows the client body line for line"); the S21 client
predicts its native leap. Speeds are given per side: client = first-time MOVE-TRACE usercmd post-velocity, dedi = MOVE-TRACE row
of the same usercmd.
Schedules: tap offhand4 (raise 1.5 s), 1.6 s later attack; view pitch aims the floor at e<D> = D u for a 69 u eye (d<D>: probes
with a 60 u eye); int = a rock spawned 206 u ahead once v_x > 1500 (wall); ceil = the rock spawned above the path (ceiling).
"""
import argparse
import bisect
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "r2_common")))
import r2_load as R  # noqa: E402

OUT = []
PH = {0: "none", 1: "prep", 2: "air", 3: "hover", 4: "ground/slam", 5: "arrival", 6: "interrupted"}


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=1):
    return None if x is None else round(x, n)


def stats(v):
    v = [x for x in v if x is not None]
    if not v:
        return {"n": 0}
    m = sum(v) / len(v)
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else 0.0
    return {"n": len(v), "mean": m, "sd": sd, "min": min(v), "max": max(v)}


def fmt(s, nd=1):
    if not s or not s.get("n"):
        return "n=0"
    if s["n"] == 1:
        return "%.*f (n=1)" % (nd, s["mean"])
    return "%.*f (sd %.*f, %.*f..%.*f, n=%d)" % (nd, s["mean"], nd, s["sd"], nd, s["min"], nd, s["max"], s["n"])


def speed(c, side):
    if side == "cl":
        return math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2), (c["pvx"], c["pvy"], c["pvz"])
    return math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2), (c["pvx"], c["pvy"], c["pvz"])


def trial(T, AL, NC, NI):
    E = {"run": T["run"], "schedule": T["schedule"][6:]}
    cs = [c for c in T["cmds"] if c.get("t") is not None]
    if not cs:
        return E
    t_lo, t_hi = cs[0]["t"], cs[-1]["t"]
    att = R.sched_t(T, "key=attack", 0)
    ph = sorted((a for a in AL if a["kind"] == "phase" and t_lo - 0.05 <= a["t"] <= t_hi + 0.05), key=lambda a: a["t"])
    if not ph:
        E["leap"] = False
        nc = NC.get(T["run"], [])
        E["ult_spent"] = any(int(w.get("uclip", 1)) == 0 for w in nc)
        return E
    E["leap"] = True
    E["type"] = ph[0]["type"]
    # the start row = the last start row printed before the first phase row (same dedi process clock)
    st = [a for a in AL if a["kind"] == "start" and a["plat"] is not None and ph[0]["plat"] is not None and a["plat"] <= ph[0]["plat"]]
    if st:
        s0 = max(st, key=lambda a: a["plat"])
        E["end_point"] = [r(x) for x in s0["end"]]
        E["timeout"] = s0["timeout"]
        o0 = (cs[0]["pox"], cs[0]["poy"], cs[0]["poz"])
        E["target_dist_2d"] = r(math.hypot(s0["end"][0] - o0[0], s0["end"][1] - o0[1]))
    E["phases"] = [(PH[a["a"]] + "->" + PH[a["b"]], r(a["t"] - (att or a["t"]), 3)) for a in ph]
    tch = [(a["b"], a["t"]) for a in ph]
    E["prep_s"] = r(ph[0]["t"] - att, 3) if att else None
    seg = {}
    for i, (b, t0) in enumerate(tch):
        t1 = tch[i + 1][1] if i + 1 < len(tch) else t0 + 1.0
        seg.setdefault(b, []).append((t0, t1))
    E["dur"] = {PH[b]: r(sum(t1 - t0 for t0, t1 in v), 3) for b, v in seg.items() if b != 0}
    for side in ("cl", "sv"):
        S = {}
        for b, v in seg.items():
            if b == 0:
                continue
            rows = []
            for t0, t1 in v:
                for c in cs:
                    if t0 <= c["t"] < t1:
                        rr = c if side == "cl" else T["sv"].get(c["cmd"])
                        if rr:
                            rows.append(rr)
            if rows:
                sp = [speed(x, side)[0] for x in rows]
                hz = [math.hypot(x["pvx"], x["pvy"]) for x in rows]
                vz = [x["pvz"] for x in rows]
                S[PH[b]] = {"n": len(rows), "max": r(max(sp)), "min": r(min(sp)), "vh_max": r(max(hz)), "vz_max": r(max(vz)), "vz_min": r(min(vz))}
        E["speeds_" + side] = S
    # landing / end
    land = next((c for c in cs if att and c["t"] > att + 0.3 and c["ground"] and math.hypot(c["pvx"], c["pvy"]) < 1.0), None)
    if land:
        E["land_xy"] = [r(land["pox"]), r(land["poy"])]
        E["land_s"] = r(land["t"] - att, 3)
    # post-interruption (and post-arrival) velocity: first client cmd and dedi row after the 6 / 5 phase start
    for code, key in ((6, "after_interrupt"), (5, "at_arrival")):
        t6 = next((t for b, t in tch if b == code), None)
        if t6 is not None:
            aft = [c for c in cs if c["t"] >= t6][:3]
            if aft:
                E[key + "_cl"] = [[r(c["pvx"]), r(c["pvy"]), r(c["pvz"])] for c in aft]
                E[key + "_sv"] = [[r(T["sv"][c["cmd"]]["pvx"]), r(T["sv"][c["cmd"]]["pvy"]), r(T["sv"][c["cmd"]]["pvz"])] for c in aft if c["cmd"] in T["sv"]]
            pre = [c for c in cs if c["t"] < t6][-2:]
            if pre:
                E[key + "_pre_cl"] = [[r(c["pvx"]), r(c["pvy"]), r(c["pvz"])] for c in pre]
                E[key + "_pre_sv"] = [[r(T["sv"][c["cmd"]]["pvx"]), r(T["sv"][c["cmd"]]["pvy"]), r(T["sv"][c["cmd"]]["pvz"])] for c in pre if c["cmd"] in T["sv"]]
    ni = NI.get(T["run"])
    if ni:
        E["obstacle_spawned_at_vx"] = float(ni[0]["vx"])
    nc = NC.get(T["run"], [])
    E["walls_max"] = max((int(w.get("walls", 0)) for w in nc), default=0)
    # client vs dedi max difference in |v| over the leap
    dif = [abs(speed(c, "cl")[0] - speed(T["sv"][c["cmd"]], "sv")[0]) for c in cs if c["cmd"] in T["sv"] and att and c["t"] >= att]
    E["max_cl_sv_speed_diff"] = r(max(dif), 2) if dif else None
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    keep = lambda t: t["schedule"].startswith("m10r2_n_") and not t.get("explore")
    S = R.load(a.session, keep)
    AL = R.al_phase(a.session)
    NC = R.tagged(a.session, "[M10R2-NC]")
    NI = R.tagged(a.session, "[M10R2-NI]")
    say("# M10 R2 Newcastle Castle Wall leap")
    say("session %s: scored %d, excluded %d %s; [AL-PHASE] lines %d" % (S["folder"], len(S["trials"]), len(S["excluded"]),
                                                                       ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in S["excluded"]], len(AL)))
    res = [trial(T, AL, NC, NI) for T in S["trials"]]
    order = ["n_e300", "n_d500", "n_e600", "n_e700", "n_d900", "n_e1200", "n_d1400", "n_e1800", "n_d2000", "n_int", "n_ceil", "n_fly1300"]
    for g in order:
        for E in [x for x in res if x["schedule"] == g]:
            if not E.get("leap"):
                say("\n  r%d %-9s no leap (ult spent %s)" % (E["run"], g, E.get("ult_spent")))
                continue
            say("\n  r%d %-9s type %s target %s (2D %s, timeout %s) prep %s s | phases %s" % (E["run"], g, E.get("type"), E.get("end_point"),
                                                                                         E.get("target_dist_2d"), E.get("timeout"), E.get("prep_s"), E.get("phases")))
            say("      durations %s | landed %s s at %s | walls %s | max |v| client-dedi diff %s" % (E.get("dur"), E.get("land_s"), E.get("land_xy"),
                                                                                                E.get("walls_max"), E.get("max_cl_sv_speed_diff")))
            say("      client %s" % E.get("speeds_cl"))
            say("      dedi   %s" % E.get("speeds_sv"))
            for key in ("after_interrupt", "at_arrival"):
                if E.get(key + "_cl"):
                    say("      %s: pre cl %s sv %s -> post cl %s sv %s" % (key, E.get(key + "_pre_cl"), E.get(key + "_pre_sv"), E.get(key + "_cl"), E.get(key + "_sv")))
    say("\n## Summary (jump leaps, type 2; dedi rows)")
    jl = [E for E in res if E.get("type") == 2 and E["schedule"] not in ("n_int", "n_ceil")]
    for ph_ in ("air", "hover", "ground/slam"):
        say("  %-12s dur %s | max |v| dedi %s client %s | min |v| dedi %s" % (
            ph_, fmt(stats([E["dur"].get(ph_) for E in jl]), 3), fmt(stats([E["speeds_sv"].get(ph_, {}).get("max") for E in jl])),
            fmt(stats([E["speeds_cl"].get(ph_, {}).get("max") for E in jl])), fmt(stats([E["speeds_sv"].get(ph_, {}).get("min") for E in jl]))))
    say("  prep (attack -> first phase change) %s s; arrival -> none %s s" % (fmt(stats([E.get("prep_s") for E in jl]), 3), fmt(stats([E["dur"].get("arrival") for E in jl]), 3)))
    dl = [E for E in res if E.get("type") == 1]
    say("  dash (type 1): ground dur %s max |v| dedi %s client %s" % (fmt(stats([E["dur"].get("ground/slam") for E in dl]), 3),
                                                                   fmt(stats([E["speeds_sv"].get("ground/slam", {}).get("max") for E in dl])),
                                                                   fmt(stats([E["speeds_cl"].get("ground/slam", {}).get("max") for E in dl]))))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Newcastle leap, R5Flowstate local hybrid (S21 client prediction + SDK-twin dedi), offline, 120 fps; newcastle_analysis.py"}
        for ph_ in ("air", "hover", "ground/slam", "arrival"):
            st = stats([E["dur"].get(ph_) for E in jl])
            if st["n"]:
                P["leap.dur." + ph_] = {"value": r(st["mean"], 3), "spread": {"sd": r(st["sd"], 3)}, "evidence": "meas (SDK trace)", "n": st["n"]}
            for side in ("sv", "cl"):
                st = stats([E["speeds_" + side].get(ph_, {}).get("max") for E in jl])
                if st["n"]:
                    P["leap.vmax.%s.%s" % (ph_, side)] = {"value": r(st["mean"], 1), "spread": {"min": r(st["min"]), "max": r(st["max"])}, "evidence": "meas", "n": st["n"]}
        P["leap.targets"] = {"value": sorted((E["schedule"], E.get("type"), E.get("target_dist_2d")) for E in res if E.get("leap")), "evidence": "meas (SDK trace)"}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
