#!/usr/bin/env python3
"""M10 track R (4) D1 slide re-check (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 slide_analysis.py <session> [<session> ...] [--json results.json] > analysis_output.txt

stdlib only, no local paths. Loader: ../r_grapple/m10_load.py (M6-A2 raw-log loader). Client first-time MOVE-TRACE usercmds:
- slide start = the first usercmd with the post slide flag set; age of a usercmd = game time since that usercmd
- crouch release = the duck-button up edge; slide end = the first usercmd at or after the release without the slide flag
- slide jump = the jump press edge; exit = its post v_h and vz; heading change = post v_h heading - pre v_h heading
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "r_grapple")))
import m10_load  # noqa: E402

IN_JUMP, IN_DUCK = 0x2, 0x4
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=2):
    return None if x is None else round(x, n)


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


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


def tt(c):
    return c.get("t")


def row(T):
    cs = T["cmds"]
    E = {"run": T["run"], "schedule": T["schedule"]}
    starts = [i for i in range(1, len(cs)) if cs[i]["slide"] and not cs[i - 1]["slide"]]
    E["n_slides"] = len(starts)
    # the slide of interest: the last slide start before the jump / release (sj2 has two slides)
    jumps = [i for i in range(1, len(cs)) if cs[i]["buttons"] & IN_JUMP and not cs[i - 1]["buttons"] & IN_JUMP]
    rel = [i for i in range(1, len(cs)) if cs[i - 1]["buttons"] & IN_DUCK and not cs[i]["buttons"] & IN_DUCK]
    key = jumps[0] if jumps else (rel[0] if rel else None)
    s0 = max([i for i in starts if key is None or i <= key], default=None)
    if s0 is None:
        return E
    E["slide_start_pre_vh"] = r(hs(cs[s0], False))
    E["slide_start_post_vh"] = r(hs(cs[s0]))
    E["slide_boost"] = r(hs(cs[s0]) - hs(cs[s0], False))
    if starts and len(starts) > 1:
        E["first_slide_boost"] = r(hs(cs[starts[0]]) - hs(cs[starts[0]], False))
    if rel and (not jumps or rel[0] < jumps[0]) and T["schedule"].startswith("m10_s_rel"):
        i = rel[0]
        E["release_age"] = r(tt(cs[i]) - tt(cs[s0]), 3) if tt(cs[i]) and tt(cs[s0]) else None
        e = next((k for k in range(i, len(cs)) if not cs[k]["slide"]), None)
        E["slide_end_after_release_cmds"] = (e - i) if e is not None else None
        E["vh_at_release"] = r(hs(cs[i], False))
        if e is not None:
            E["vh_at_end"] = r(hs(cs[e]))
            E["duck_flag_at_end"] = cs[e]["duck"]
            later = next((c for c in cs[e:] if tt(c) and tt(cs[e]) and tt(c) - tt(cs[e]) >= 0.5), None)
            E["vh_05s_after_end"] = r(hs(later)) if later else None
    if T["schedule"] == "m10_s_hold":
        e = next((k for k in range(s0, len(cs)) if not cs[k]["slide"]), None)
        E["slide_len_s"] = r(tt(cs[e]) - tt(cs[s0]), 3) if e is not None and tt(cs[e]) and tt(cs[s0]) else None
        E["vh_at_slide_end"] = r(hs(cs[e])) if e is not None else None
    if jumps:
        j = jumps[0]
        c = cs[j]
        E["jump_age"] = r(tt(c) - tt(cs[s0]), 3) if tt(c) and tt(cs[s0]) else None
        E["jump_sliding"] = cs[j - 1]["slide"]
        E["pre_vh"] = r(hs(c, False))
        E["exit_vh"] = r(hs(c))
        E["exit_vz"] = r(c["pvz"])
        h0 = math.degrees(math.atan2(c["vy"], c["vx"]))
        h1 = math.degrees(math.atan2(c["pvy"], c["pvx"]))
        E["heading_change"] = r((h1 - h0 + 180) % 360 - 180, 3)
        air = [q for q in cs[j:] if not q["ground"]]
        E["max_vh_air"] = r(max(hs(q) for q in air)) if air else None
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    say("# M10 R4 D1 slide re-check")
    by = {}
    for f in a.sessions:
        S = m10_load.load(f)
        sc = [t for t in S["runner"]["trials"] if not t.get("warmup")]
        bad = [t for t in sc if not t.get("ok")]
        say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(bad),
                                                        ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in bad]))
        for T in S["trials"]:
            if T["schedule"].startswith("m10_s"):
                by.setdefault(T["schedule"], []).append(row(T))
    res = {"trials": [], "groups": {}}
    keys = ("slide_start_post_vh", "slide_boost", "release_age", "slide_end_after_release_cmds", "vh_at_release", "vh_at_end",
            "vh_05s_after_end", "slide_len_s", "vh_at_slide_end", "jump_age", "pre_vh", "exit_vh", "exit_vz", "heading_change", "max_vh_air")
    for n in sorted(by):
        rows = by[n]
        res["trials"].extend(rows)
        g = {k: stats([E.get(k) for E in rows]) for k in keys}
        res["groups"][n] = {k: {q: r(w, 3) for q, w in s.items()} for k, s in g.items() if s["n"]}
        say("\n%s" % n)
        for k in keys:
            if g[k]["n"]:
                say("  %-30s %s" % (k, fmt(g[k])))
        say("  jump while sliding: %s; slides per trial: %s" % (sorted(set(E.get("jump_sliding") for E in rows)), sorted(set(E.get("n_slides") for E in rows))))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "D1 slide re-check, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; slide_analysis.py"}
        for n, field in (("m10_s_hold", "slide_start_post_vh"), ("m10_s_hold", "slide_len_s"), ("m10_s_hold", "vh_at_slide_end"),
                         ("m10_s_rel_t010", "slide_end_after_release_cmds"), ("m10_s_rel_t010", "vh_at_end"),
                         ("m10_s_rel_t025", "slide_end_after_release_cmds"), ("m10_s_rel_t025", "vh_at_end"),
                         ("m10_s_rel_t050", "slide_end_after_release_cmds"), ("m10_s_rel_t100", "slide_end_after_release_cmds"),
                         ("m10_s_sj_a010", "exit_vh"), ("m10_s_sj_a025", "exit_vh"), ("m10_s_sj_a040", "exit_vh"), ("m10_s_sj_a060", "exit_vh"),
                         ("m10_s_sj_a100", "exit_vh"), ("m10_s_sj2_a025", "exit_vh"), ("m10_s_sj2_a060", "exit_vh"), ("m10_s_sj2_a025", "slide_start_post_vh")):
            g = res["groups"].get(n, {}).get(field)
            if g:
                P[n[6:] + "." + field] = {"value": g.get("mean"), "spread": {k: g.get(k) for k in ("sd", "min", "max")}, "evidence": "meas", "n": g.get("n")}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
