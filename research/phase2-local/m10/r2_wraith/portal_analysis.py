#!/usr/bin/env python3
"""M10 track R2: Wraith Dimensional Rift follow-up (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 portal_analysis.py <session> [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader ../r2_common/r2_load.py; dedi logger [M10R2-WR] (one row per dedi script frame = 0.1 s:
speed_boost and placing severities, phase flag, isInPhaseTunnel, clips, origin, velocity, eye yaw, portal blockers and their
origins when the count changes; pre-portal blocker origins from sub-run M10R2_wraith2 on), [M10R2-TP] (teleport helper).
Script reference (local mp_weapon_phase_tunnel.nut, Flowstate copy): nodes recorded per dedi frame while placing; travel moves a
script mover through the nodes at FRAME_TIME 0.1 with pathTime = clamp(L / 1024, 0.3, 2.0) (2.0 -> 3.5 s for L 3000..6000),
SetVelocity(node velocity) per step, then ClearParent + SetAbsOrigin; speed steps +0.1 severity per 20 % of 6000 u of the
straight (3D) distance from the start node; min portal gap 128 u; lifetime 45 s; debounce 0.5 s; use cooldown 0.25 s.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "r2_common")))
import r2_load as R  # noqa: E402

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=2):
    return None if x is None else round(x, n)


def stats(v):
    v = [x for x in v if x is not None]
    if not v:
        return {"n": 0}
    m = sum(v) / len(v)
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else 0.0
    return {"n": len(v), "mean": m, "sd": sd, "min": min(v), "max": max(v)}


def fmt(s, nd=2):
    if not s or not s.get("n"):
        return "n=0"
    if s["n"] == 1:
        return "%.*f (n=1)" % (nd, s["mean"])
    return "%.*f (sd %.*f, %.*f..%.*f, n=%d)" % (nd, s["mean"], nd, s["sd"], nd, s["min"], nd, s["max"], s["n"])


def rows(W, run):
    out = []
    for w in W.get(run, []):
        d = {"t": w["t"], "boost": float(w["boost"]), "placing": float(w["placing"]), "ph": int(w["ph"]), "tun": int(w.get("tun", 0)),
             "uclip": int(w.get("uclip", -1)), "o": R.f3(w["o"]), "v": R.f3(w["v"]), "yaw": float(w.get("yaw", 0)),
             "blockers": int(w["blockers"]), "pre": int(w.get("pre", 0))}
        for k in ("bls", "pbls"):
            if k in w:
                d[k] = [R.f3(x) for x in w[k].split(";") if x]
        out.append(d)
    return out


def episodes(ws):
    """travel episodes: consecutive rows with isInPhaseTunnel = 1 (the phase flag alone is also set by Into the Void)"""
    eps, cur = [], []
    for w in ws:
        if w["tun"]:
            cur.append(w)
        elif cur:
            eps.append(cur)
            cur = []
    if cur:
        eps.append(cur)
    return eps


def pair_info(ws, origin):
    """portal pair from the first row after the placement start whose blockers list has 2 entries (earlier rows can still
    list the previous trial's pair); start = the one nearest the reset origin (tower: the high one)"""
    t_pl = next((w["t"] for w in ws if w["placing"] > 0), None)
    if t_pl is None:
        return None
    for w in ws:
        if w["t"] < t_pl:
            continue
        b = w.get("bls")
        if b and len(b) == 2:
            b = sorted(b, key=lambda p: math.hypot(p[0] - origin[0], p[1] - origin[1]))
            if abs(origin[2] - 5532.8) < 1 and abs(b[0][2] - b[1][2]) > 1000:   # tower: start = the high one
                b = sorted(b, key=lambda p: -p[2])
            return {"t": w["t"], "start": b[0], "end": b[1]}
    return None


def portal_trial(T, ws, origin):
    E = {"run": T["run"], "schedule": T["schedule"][6:]}
    pl = [w for w in ws if w["placing"] > 0]
    E["placed"] = bool(pl)
    tap = R.sched_t(T, "key=offhand4", 0)
    if pl:
        E["place_start_delay_s"] = r(pl[0]["t"] - tap, 2) if tap else None
        E["place_s"] = r(pl[-1]["t"] - pl[0]["t"] + 0.1, 2)
        E["place_len"] = r(sum(math.dist(pl[i]["o"], pl[i + 1]["o"]) for i in range(len(pl) - 1)), 1)
        E["sev_levels"] = sorted(set(round(w["boost"], 3) for w in pl))
        E["place_vh_first"] = r(math.hypot(*pl[0]["v"][:2]), 1)
        E["place_vh_last"] = r(math.hypot(*pl[-1]["v"][:2]), 1)
    P = pair_info(ws, origin)
    E["pair"] = P is not None
    if P:
        E["gap"] = r(math.dist(P["start"], P["end"]), 1)
        st, en = P["start"], P["end"]
        E["start_portal"] = [r(x, 1) for x in st]
        E["end_portal"] = [r(x, 1) for x in en]
        gone = next((w["t"] for w in ws if w["t"] > P["t"] and w["blockers"] == 0), None)
        E["pair_life_s"] = r(gone - P["t"], 2) if gone else None
    pb = next((w["pbls"] for w in ws if w.get("pbls") and (not pl or w["t"] >= pl[0]["t"] - 0.15)), None)
    if pb:
        E["pre_portal"] = [r(x, 1) for x in pb[0]]
        if pl:
            s0 = (pb[0][0], pb[0][1], pb[0][2] - 45.0)
            E["end_dist"] = r(math.dist(s0, pl[-1]["o"]), 1)
    uc = [w["uclip"] for w in ws]
    E["ult_spent"] = any(u == 0 for u in uc)
    eps = episodes(ws)
    E["travels"] = len(eps)
    E["travel"] = []
    for ep in eps:
        nxt = next((w for w in ws if w["t"] > ep[-1]["t"] and not w["tun"]), None)
        D = {"t0": r(ep[0]["t"], 2), "rows": len(ep), "dur_s": r(ep[-1]["t"] - ep[0]["t"] + 0.1, 2)}
        D["from"] = [r(x, 1) for x in ep[0]["o"]]
        D["to"] = [r(x, 1) for x in ep[-1]["o"]]
        D["disp"] = r(math.dist(ep[0]["o"], ep[-1]["o"]), 1)
        D["path_len"] = r(sum(math.dist(ep[i]["o"], ep[i + 1]["o"]) for i in range(len(ep) - 1)), 1)
        D["vfield_h"] = [r(math.hypot(*w["v"][:2]), 1) for w in ep]
        D["vfield_z"] = [r(w["v"][2], 1) for w in ep]
        if P:
            D["dir"] = "end->start" if math.hypot(ep[-1]["o"][0] - P["start"][0], ep[-1]["o"][1] - P["start"][1]) < math.hypot(ep[-1]["o"][0] - P["end"][0], ep[-1]["o"][1] - P["end"][1]) else "start->end"
        if nxt:
            D["exit_v"] = [r(x, 1) for x in nxt["v"]]
            D["exit_yaw"] = r(nxt["yaw"], 1)
            D["yaw_series"] = [r(w["yaw"], 1) for w in ep]
        # entry speed (client frames 0.3 s before the client phase flag) and client exit
        D["rate"] = r(D["path_len"] / max(D["dur_s"] - 0.2, 0.1), 1)
        E["travel"].append(D)
    st = [s for s in T["states"] if s.get("ph")]
    if st:
        # client phase episodes
        cl, cur = [], [st[0]]
        for a, b in zip(st, st[1:]):
            if b["fc"] - a["fc"] > 2:
                cl.append(cur)
                cur = [b]
            else:
                cur.append(b)
        cl.append(cur)
        E["client_phase_s"] = [r(c[-1]["t"] - c[0]["t"], 3) for c in cl]
        ex = []
        for c in cl:
            t1 = c[-1]["t"]
            fr = [f for f in T["frames"] if f["t"] > t1 + 1e-6]
            pre = [f for f in T["frames"] if c[0]["t"] - 0.3 <= f["t"] < c[0]["t"]]
            ex.append({"entry_vh": r(max((math.hypot(f["vx"], f["vy"]) for f in pre), default=None), 1),
                       "exit_v": [r(fr[0]["vx"], 1), r(fr[0]["vy"], 1), r(fr[0]["vz"], 1)] if fr else None,
                       "exit_v_0p2s": [r(f["vx"], 1) for f in fr[:1]] and [r(max(math.hypot(f["vx"], f["vy"]) for f in fr[:24]), 1)]})
        E["client_exit"] = ex
    return E


def drop_steps(T, ws, origin):
    """severity steps vs straight distance from the start portal node (start blocker - 45 z) during the placement"""
    P = pair_info(ws, origin)
    if not P:
        return None
    s0 = (P["start"][0], P["start"][1], P["start"][2] - 45.0)
    pl = [w for w in ws if w["placing"] > 0]
    steps, last = [], None
    for i, w in enumerate(pl):
        b = round(w["boost"], 3)
        if last is not None and b != last:
            prev = pl[i - 1]
            steps.append({"sev": b, "t": r(w["t"] - pl[0]["t"], 2), "dist_prev": r(math.dist(prev["o"], s0), 1),
                          "dist_at": r(math.dist(w["o"], s0), 1),
                          "pct_prev": r(100 * math.dist(prev["o"], s0) / 6000.0, 1), "pct_at": r(100 * math.dist(w["o"], s0) / 6000.0, 1)})
        last = b
    land = next((w for w in pl if w["o"][2] < 300 and w["v"][2] == 0), None)
    spr = [math.hypot(*w["v"][:2]) for w in pl if w["o"][2] < 300]
    return {"run": T["run"], "steps": steps, "max_dist": r(max(math.dist(w["o"], s0) for w in pl), 1),
            "place_s": r(pl[-1]["t"] - pl[0]["t"] + 0.1, 2), "floor_vh_max": r(max(spr), 1) if spr else None,
            "landed_at_s": r(land["t"] - pl[0]["t"], 2) if land else None}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    keep = lambda t: t["schedule"].startswith("m10r2_w_") and not t.get("explore")
    S = R.load_many(a.sessions, keep)
    W = R.tagged_many(a.sessions, "[M10R2-WR]")
    say("# M10 R2 Wraith portal")
    say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(S["excluded"]),
                                                    ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in S["excluded"]]))
    origins = {t["run"]: t["origin"] for t in S["runner"]["trials"]}
    res = {"trials": [], "drop": []}
    for T in S["trials"]:
        ws = rows(W, T["run"])
        o = origins[T["run"]]
        E = portal_trial(T, ws, o)
        res["trials"].append(E)
        if T["schedule"] == "m10r2_w_drop":
            d = drop_steps(T, ws, o)
            if d:
                res["drop"].append(d)
    groups = {}
    for E in res["trials"]:
        groups.setdefault(E["schedule"], []).append(E)
    say("\n## 1. Exit velocity / travel (dedi rows; travel = rows with the phase flag; exit = first free row)")
    for g in ("w_runin_end", "w_runin_start", "w_stand_start", "w_stay", "w_repeat", "w_drop"):
        for E in groups.get(g, []):
            say("  r%d %-14s place start %s s after the tap, %s s, len %s, sev %s, v first/last %s/%s | pair %s gap %s | travels %d" % (
                E["run"], g, E.get("place_start_delay_s"), E.get("place_s"), E.get("place_len"), E.get("sev_levels"), E.get("place_vh_first"),
                E.get("place_vh_last"), E["pair"], E.get("gap"), E["travels"]))
            for D in E["travel"]:
                say("      %s dur %s s (%d rows) disp %s path %s rate %s u/s | v-field h %s | exit v %s yaw %s (series %s)" % (
                    D.get("dir"), D["dur_s"], D["rows"], D["disp"], D["path_len"], D["rate"], D["vfield_h"], D.get("exit_v"), D.get("exit_yaw"), D.get("yaw_series")))
            if E.get("client_exit"):
                say("      client phase %s s; client exits %s" % (E.get("client_phase_s"), E["client_exit"]))
    say("\n## 2. Long portal (tower drop, 5238 u): severity steps vs straight distance from the start node")
    for d in res["drop"]:
        say("  r%d place %s s landed at %s s, max dist %s, floor v_h max %s" % (d["run"], d["place_s"], d["landed_at_s"], d["max_dist"], d["floor_vh_max"]))
        for s in d["steps"]:
            say("      -> sev %s at %s s: dist %s..%s (%s..%s %% of 6000)" % (s["sev"], s["t"], s["dist_prev"], s["dist_at"], s["pct_prev"], s["pct_at"]))
    say("\n## 3. Minimum portal gap (walk W for X s after the placement start, end tap)")
    for g in sorted(k for k in groups if k.startswith("w_gap")):
        for E in groups[g]:
            st = E.get("start_portal") or E.get("pre_portal")
            say("  r%d %-10s pre-portal %s | straight start->end-tap %s | pair %s gap %s | ult spent %s | place len %s" % (
                E["run"], g, E.get("pre_portal"), E.get("end_dist"), E["pair"], E.get("gap"), E["ult_spent"], E.get("place_len")))
    say("\n## 4. Lifetime (pair -> blockers gone)")
    for E in groups.get("w_life", []):
        say("  r%d pair life %s s (pair %s)" % (E["run"], E.get("pair_life_s"), E["pair"]))
    say("\n## 5. Into the Void + portal")
    for g in ("w_void_in", "w_void_place", "w_vctrl", "w_vin2"):
        for E in groups.get(g, []):
            ws = rows(W, E["run"])
            P = pair_info(ws, origins[E["run"]])
            mind = None
            if P:
                phd = [w for w in ws if w["ph"] or True]
                mind = r(min(math.hypot(w["o"][0] - P["end"][0], w["o"][1] - P["end"][1]) for w in ws if w["t"] > P["t"]), 1)
            phs = [w["t"] for w in ws if w["ph"]]
            say("  r%d %-12s placed %s pair %s portal travels %d ult spent %s | phase (Void) %s..%s | min 2D distance to the end portal after pairing %s" % (
                E["run"], g, E["placed"], E["pair"], E["travels"], E["ult_spent"], r(min(phs), 2) if phs else None, r(max(phs), 2) if phs else None, mind))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Wraith portal, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; portal_analysis.py"}
        ex = [D["exit_v"] for E in res["trials"] for D in E["travel"] if D.get("exit_v")]
        P["portal.exit_speed_dedi"] = {"value": r(max(math.hypot(*v[:2]) for v in ex), 2) if ex else None, "evidence": "meas (max over exits)", "n": len(ex)}
        dl = [E.get("place_start_delay_s") for E in res["trials"] if E.get("place_start_delay_s") is not None]
        P["portal.place_start_delay_s"] = {"value": r(stats(dl)["mean"], 2), "spread": {"sd": r(stats(dl)["sd"], 3)}, "evidence": "meas", "n": len(dl)}
        lf = [E.get("pair_life_s") for E in groups.get("w_life", []) if E.get("pair_life_s")]
        P["portal.lifetime_s"] = {"value": r(stats(lf)["mean"], 2) if lf else None, "evidence": "meas (10 Hz)", "n": len(lf)}
        tr = [(D["path_len"], D["dur_s"]) for E in res["trials"] for D in E["travel"] if D.get("dur_s")]
        P["portal.travel_len_dur"] = {"value": sorted(tr), "evidence": "meas (dedi rows)", "n": len(tr)}
        gaps = sorted((E.get("gap") or 0.0, E["pair"]) for g, es in groups.items() if g.startswith("w_gap") for E in es)
        P["portal.gap_trials"] = {"value": gaps, "evidence": "meas"}
        st = [s for d in res["drop"] for s in d["steps"]]
        P["portal.drop_steps"] = {"value": [(s["sev"], s["pct_prev"], s["pct_at"]) for s in st], "evidence": "meas", "n": len(res["drop"])}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
