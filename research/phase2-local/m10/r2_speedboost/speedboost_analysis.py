#!/usr/bin/env python3
"""M10 track R2: speed_boost severity -> move scale (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 speedboost_analysis.py <session> [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader ../r2_common/r2_load.py (a2_load + the dedi [M10R2-WR] / [M10R2-MG] logger rows).
- m10r2_sev_*: Wraith (kit) on lane C; StatusEffect_AddTimed( speed_boost, S, 5 s, fade 0 ) at the reset, sprint 2.5 s
  (1.6 s for S = 1.0); stack = 0.2 + 0.1; fade = 0.15 for 1.5 s with a 0.25 s fade; ctrl = no effect.
  Per trial: logged severity (dedi StatusEffect_GetSeverity), client usercmd msc / maxspeed while sprinting, sprint v_h plateau.
- cross-checks from the other R2 sub-runs: Wraith portal placement (m10r2_w_runin_*, m10r2_w_drop: msc levels while placing),
  Maggie pad (m10r2_m_pass: msc and v_h while the dedi severity is 0.149).
Model checked: msc = W * (1 + 2 * q(S)), q(S) = floor(255 * S) / 255 (byte severity), W = 1.15 with the default melee in hand,
1.0 while an ability holsters / locks the weapons; sprint max speed = 260 * msc, walk max speed = 173.5 * msc.
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
IN_SPEED = 1 << 15


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=4):
    return None if x is None else round(x, n)


def q(s):
    return math.floor(255.0 * s + 1e-9) / 255.0


SEV = {"ctrl": [], "s005": [0.05], "s010": [0.10], "s015": [0.15], "s020": [0.20], "s030": [0.30], "s040": [0.40], "s050": [0.50],
       "s100": [1.00], "stack": [0.20, 0.10], "fade": [0.15]}


def sev_row(T, W):
    k = T["schedule"][len("m10r2_sev_"):]
    E = {"run": T["run"], "case": k, "script_sev": SEV[k]}
    ws = W.get(T["run"], [])
    E["logged_sev"] = sorted(set(round(float(w["boost"]), 4) for w in ws))
    spr = [c for c in T["cmds"] if c["sprint"] and c["ground"]]
    if spr:
        E["msc_max"] = r(max(c["msc"] for c in spr))
        E["ms_max"] = r(max(c["maxspeed"] for c in spr), 3)
        E["vh_max"] = r(max(math.hypot(c["pvx"], c["pvy"]) for c in spr), 3)
        lv = {}
        for c in spr:
            lv.setdefault(round(c["msc"], 4), 0)
            lv[round(c["msc"], 4)] += 1
        E["msc_levels"] = sorted((m, n) for m, n in lv.items() if n >= 5)
    if SEV[k]:
        qq = max(q(s) for s in SEV[k])
        E["q_model"] = r(qq)
        E["msc_model"] = r(1.15 * (1 + 2 * qq))
        E["vh_model"] = r(260.0 * 1.15 * (1 + 2 * qq), 3)
    if k == "fade":
        seq = [(w["t"], float(w["boost"])) for w in ws]
        on = [t for t, b in seq if b > 0]
        if on:
            t0 = on[0]
            E["fade_series"] = [(r(t - t0, 2), r(b)) for t, b in seq if t0 - 0.1 <= t <= t0 + 2.2]
    return E


def placing_levels(T, W):
    """client msc levels while the dedi says the portal placement is on (placing > 0)"""
    ws = W.get(T["run"], [])
    pl = [(w["t"], float(w["boost"])) for w in ws if float(w.get("placing", 0)) > 0]
    if not pl:
        return None
    t0, t1 = pl[0][0], pl[-1][0]
    cs = [c for c in T["cmds"] if c.get("t") is not None and t0 <= c["t"] <= t1 + 0.1]
    lv = {}
    for c in cs:
        key = (round(c["msc"], 4), round(c["maxspeed"], 3), c["sprint"])
        lv[key] = lv.get(key, 0) + 1
    return {"run": T["run"], "schedule": T["schedule"], "sev_logged": sorted(set(round(b, 4) for _, b in pl)),
            "msc_ms_spr": sorted(k for k, n in lv.items() if n >= 3)}


def maggie_levels(T, M):
    ms = M.get(T["run"], [])
    on = [w["t"] for w in ms if abs(float(w["boost"]) - 0.149) < 1e-3]
    if not on:
        return None
    cs = [c for c in T["cmds"] if c.get("t") is not None and min(on) <= c["t"] <= max(on)]
    lv = {}
    for c in cs:
        key = (round(c["msc"], 4), round(c["maxspeed"], 3), c["sprint"])
        lv[key] = lv.get(key, 0) + 1
    vh = max((math.hypot(c["pvx"], c["pvy"]) for c in cs), default=None)
    return {"run": T["run"], "schedule": T["schedule"], "msc_ms_spr": sorted(k for k, n in lv.items() if n >= 3), "vh_max": r(vh, 3)}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    keep = lambda t: (t["schedule"].startswith("m10r2_sev_") or t["schedule"] in ("m10r2_w_runin_end", "m10r2_w_runin_start", "m10r2_w_drop", "m10r2_m_pass")) and not t.get("explore")
    S = R.load(a.session, keep)
    W = R.tagged(a.session, "[M10R2-WR]")
    M = R.tagged(a.session, "[M10R2-MG]")
    say("# M10 R2 speed_boost severity -> move scale")
    say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(S["excluded"]),
                                                    ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in S["excluded"]]))
    res = {"sev": [], "placing": [], "maggie": []}
    for T in S["trials"]:
        if T["schedule"].startswith("m10r2_sev_"):
            res["sev"].append(sev_row(T, W))
        elif T["schedule"] == "m10r2_m_pass":
            x = maggie_levels(T, M)
            if x:
                res["maggie"].append(x)
        else:
            x = placing_levels(T, W)
            if x:
                res["placing"].append(x)
    say("\n## 1. Script severity S -> logged severity, client msc / maxspeed, sprint v_h (model msc = 1.15 (1 + 2 q(S)))")
    for E in sorted(res["sev"], key=lambda e: (e["case"], e["run"])):
        say("  r%d %-6s S %-11s logged %-16s q %-7s | msc %s (model %s) ms %s v_h %s (model %s) | levels %s" % (
            E["run"], E["case"], E["script_sev"], E["logged_sev"], E.get("q_model"), E.get("msc_max"), E.get("msc_model"),
            E.get("ms_max"), E.get("vh_max"), E.get("vh_model"), E.get("msc_levels")))
        if "fade_series" in E:
            say("        fade series (s from the first non-zero row, severity): %s" % E["fade_series"])
    say("\n## 2. Cross-check: Wraith portal placement (weapons locked) -- (msc, maxspeed, sprint flag) levels while placing")
    for E in res["placing"]:
        say("  r%d %-20s sev %s levels %s" % (E["run"], E["schedule"][6:], E["sev_logged"], E["msc_ms_spr"]))
    say("\n## 3. Cross-check: Mad Maggie pad (dedi severity 0.149) -- levels while boosted")
    for E in res["maggie"]:
        say("  r%d %-12s levels %s v_h max %s" % (E["run"], E["schedule"][6:], E["msc_ms_spr"], E["vh_max"]))
    # summary per case
    say("\n## 4. Summary per case (mean over trials)")
    summ = {}
    for E in res["sev"]:
        summ.setdefault(E["case"], []).append(E)
    P = {"_scope": "speed_boost severity mapping, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; speedboost_analysis.py",
         "model": "msc = W * (1 + 2 * q), q = floor(255 * S) / 255, W = 1.15 (melee in hand) / 1.0 (ability holsters weapons); sprint max = 260 * msc; walk max = 173.5 * msc"}
    for k in ("ctrl", "s005", "s010", "s015", "s020", "s030", "s040", "s050", "s100", "stack", "fade"):
        es = summ.get(k, [])
        if not es:
            continue
        msc = [e.get("msc_max") for e in es if e.get("msc_max") is not None]
        vh = [e.get("vh_max") for e in es if e.get("vh_max") is not None]
        dev = [abs(e["msc_max"] - e["msc_model"]) for e in es if e.get("msc_model") and e.get("msc_max")]
        say("  %-6s n=%d msc %s v_h %s max |msc - model| %s" % (k, len(es), sorted(set(msc)), sorted(set(vh)), r(max(dev), 5) if dev else None))
        P["sev.%s" % k] = {"value": {"msc": sorted(set(msc)), "vh_sprint": sorted(set(vh)), "logged_sev": sorted(set(x for e in es for x in e["logged_sev"]))},
                           "evidence": "meas", "n": len(es)}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
