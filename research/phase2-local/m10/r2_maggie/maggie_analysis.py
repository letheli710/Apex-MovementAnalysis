#!/usr/bin/env python3
"""M10 track R2: Mad Maggie Wrecking Ball speed pads (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 maggie_analysis.py <session> [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader ../r2_common/r2_load.py; dedi logger [M10R2-MG] (per dedi frame = 0.1 s: speed_boost
severity, ground friction scale, sliding, origin, velocity, speed-trigger count and origins when the count changes).
Real ultimate (legend madmaggie, kit): tap offhand4 throws the ball along the view (+X on lane C); pieces with an 88 u speed
trigger drop along its path. Schedules (lane C, 2.8 s after the throw): pass = sprint 2.6 s through the first piece; pass2 =
sprint 4.6 s through pieces 1 and 2; walk = W only 3.6 s; slide = sprint 1.4 s then slide 1.6 s into piece 1; stand = walk into
piece 1, stand 3 s, walk out; ctrl_slide = the slide without a ball.
Per usercmd the client MOVE-TRACE msc is the boost signal (1.15 base, 1.15 * (1 + 2 * 0.149) = 1.4927 boosted); trigger enter /
leave = 2D distance of the client origin to the piece centre.
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
BASE, BOOST = 1.15, round(1.15 * (1 + 2 * 38 / 255.0), 4)


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


def pieces(ms, t_after=None):
    """trigger origins from the last row (before t_after) that lists them"""
    last = None
    for w in ms:
        if "trs" in w and (t_after is None or w["t"] <= t_after):
            last = [R.f3(x) for x in w["trs"].split(";") if x]
    return last or []


def trial(T, M):
    E = {"run": T["run"], "schedule": T["schedule"][6:]}
    ms = M.get(T["run"], [])
    tap = R.sched_t(T, "key=offhand4", 0)
    first = next((w for w in ms if "trs" in w and w["trs"]), None)
    if first and tap:
        E["first_piece_s"] = r(first["t"] - tap, 2)
    cs = [c for c in T["cmds"] if c.get("t") is not None]
    if not cs:
        return E
    t_end = cs[-1]["t"]
    pcs = [p for p in pieces(ms, t_end) if abs(p[2] - 294.5) < 5]        # pieces resting on the field floor
    E["pieces_x"] = [r(p[0], 1) for p in sorted(pcs)]
    if len(pcs) >= 2:
        xs = sorted(p[0] for p in pcs)
        E["piece_spacing"] = [r(b - a, 1) for a, b in zip(xs, xs[1:])]
    # per cmd: boost on/off and the nearest-piece 2D distance
    def dmin(c):
        return min((math.hypot(c["pox"] - p[0], c["poy"] - p[1]) for p in pcs), default=None)
    on = [c for c in cs if abs(c["msc"] - BOOST) < 2e-4]
    mid = [c for c in cs if BASE + 2e-4 < c["msc"] < BOOST - 2e-4]
    E["msc_max"] = r(max(c["msc"] for c in cs), 4)
    E["boost_cmds"] = len(on)
    if on and pcs:
        c0 = on[0]
        i0 = cs.index(c0)
        E["enter_dist"] = r(dmin(cs[i0 - 1]), 1) if i0 > 0 else None
        E["enter_dist_on"] = r(dmin(c0), 1)
        # leave: first cmd after the boost start with dmin > the entry distance (the trigger edge seen at entry)
        edge = dmin(c0)
        inside = [c for c in cs[i0:] if dmin(c) is not None and dmin(c) <= edge + 1.0]
        # the last cmd inside the first contiguous inside stretch
        lv = None
        for c in cs[i0:]:
            if dmin(c) is not None and dmin(c) > edge + 1.0:
                lv = c
                break
        if lv:
            E["leave_t_rel"] = r(lv["t"] - c0["t"], 3)
            post = [c for c in cs if c["t"] >= lv["t"]]
            off = next((c for c in post if abs(c["msc"] - BOOST) >= 2e-4), None)
            zero = next((c for c in post if abs(c["msc"] - BASE) < 2e-4), None)
            # re-entry (pass2) keeps the boost: only report the trailing for trials that do not touch a second piece
            E["hold_after_leave_s"] = r(off["t"] - lv["t"], 3) if off else None
            E["fade_s"] = r(zero["t"] - off["t"], 3) if (off and zero) else None
            E["fade_msc"] = sorted(set(round(c["msc"], 4) for c in post if off and zero and off["t"] <= c["t"] < zero["t"]))[:12]
    spr = [c for c in on if c["sprint"] and c["ground"] and not c["slide"]]
    wk = [c for c in on if not c["sprint"] and c["ground"] and not c["slide"]]
    if spr:
        E["ms_sprint_boost"] = r(max(c["maxspeed"] for c in spr), 3)
        E["vh_sprint_boost"] = r(max(math.hypot(c["pvx"], c["pvy"]) for c in spr), 3)
    if wk:
        E["ms_walk_boost"] = r(max(c["maxspeed"] for c in wk), 3)
        E["vh_walk_boost"] = r(max(math.hypot(c["pvx"], c["pvy"]) for c in wk), 3)
    # dedi friction values while boosted / after
    E["fric_values"] = sorted(set(round(float(w["fric"]), 3) for w in ms))
    E["fric_seq"] = []
    last = None
    for w in ms:
        k = (round(float(w["fric"]), 3), int(w["slide"]), round(float(w["boost"]), 3) > 0)
        if k != last:
            E["fric_seq"].append((r(w["t"] - (tap or w["t"]), 2), k[0], k[1], round(float(w["boost"]), 4)))
            last = k
    # slide speed series (client, 0.1 s steps from the slide start)
    sl = [c for c in cs if c["slide"]]
    if sl:
        t0 = sl[0]["t"]
        ser = []
        for k in range(0, 17):
            c = min(sl, key=lambda c: abs(c["t"] - (t0 + 0.1 * k)))
            if abs(c["t"] - (t0 + 0.1 * k)) < 0.02:
                ser.append((r(0.1 * k, 1), r(math.hypot(c["pvx"], c["pvy"]), 1), int(abs(c["msc"] - BOOST) < 2e-4)))
        E["slide_series"] = ser
        E["slide_len_s"] = r(sl[-1]["t"] - t0, 3)
        # slide deceleration inside the pad (boosted, within 88 u of a piece) vs the same slide-age window without a ball
        ins = [c for c in sl if pcs and abs(c["msc"] - BOOST) < 2e-4 and dmin(c) is not None and dmin(c) <= 88.0]
        if len(ins) >= 6:
            sp = {"age0": r(ins[0]["t"] - t0, 3), "age1": r(ins[-1]["t"] - t0, 3),
                  "v0": r(math.hypot(ins[0]["pvx"], ins[0]["pvy"]), 1), "v1": r(math.hypot(ins[-1]["pvx"], ins[-1]["pvy"]), 1)}
            sp["decel"] = r((sp["v0"] - sp["v1"]) / max(ins[-1]["t"] - ins[0]["t"], 1e-3), 1)
            E["slide_in_pad"] = sp
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    keep = lambda t: t["schedule"].startswith("m10r2_m_") and not t.get("explore")
    S = R.load(a.session, keep)
    M = R.tagged(a.session, "[M10R2-MG]")
    say("# M10 R2 Mad Maggie Wrecking Ball speed pads")
    say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(S["excluded"]),
                                                    ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in S["excluded"]]))
    res = [trial(T, M) for T in S["trials"]]
    for E in res:
        say("\n  r%d %-10s first piece %s s after the throw; pieces x %s spacing %s" % (E["run"], E["schedule"], E.get("first_piece_s"),
                                                                                      E.get("pieces_x"), E.get("piece_spacing")))
        say("      msc max %s, boosted cmds %s | enter at 2D dist %s (first boosted cmd %s) | leave %s s after entry, hold %s s, fade %s s (fade msc %s)" % (
            E.get("msc_max"), E.get("boost_cmds"), E.get("enter_dist"), E.get("enter_dist_on"), E.get("leave_t_rel"),
            E.get("hold_after_leave_s"), E.get("fade_s"), E.get("fade_msc")))
        say("      boosted sprint ms %s v_h %s | walk ms %s v_h %s" % (E.get("ms_sprint_boost"), E.get("vh_sprint_boost"), E.get("ms_walk_boost"), E.get("vh_walk_boost")))
        say("      dedi (t from throw, friction, sliding, severity) %s" % E.get("fric_seq"))
        if E.get("slide_series"):
            say("      slide v_h series (s, v_h, boosted) %s; slide length %s s" % (E["slide_series"], E.get("slide_len_s")))
    ctrl = [E for E in res if E["schedule"] == "m_ctrl_slide" and E.get("slide_series")]
    for E in res:
        sp = E.get("slide_in_pad")
        if sp and ctrl:
            dec = []
            for C in ctrl:   # the control slide over the same slide-age window
                ser = dict((a_, v) for a_, v, _ in C["slide_series"])
                a0, a1 = round(sp["age0"], 1), round(sp["age1"], 1)
                if a0 in ser and a1 in ser and a1 > a0:
                    dec.append((ser[a0] - ser[a1]) / (a1 - a0))
            sp["ctrl_decel_same_age"] = r(sum(dec) / len(dec), 1) if dec else None
            say("  r%d slide inside the pad: v %s -> %s over slide age %s..%s s, decel %s u/s^2; control slide same ages %s u/s^2" % (
                E["run"], sp["v0"], sp["v1"], sp["age0"], sp["age1"], sp["decel"], sp["ctrl_decel_same_age"]))
    say("\n## Summary")
    for key, field in (("enter distance (last unboosted cmd)", "enter_dist"), ("hold after leaving (s)", "hold_after_leave_s"), ("fade (s)", "fade_s"),
                       ("first piece after the throw (s)", "first_piece_s")):
        vals = [E.get(field) for E in res if E["schedule"] in ("m_pass", "m_walk", "m_slide", "m_stand", "m_pass2") and E.get(field) is not None
                and not (field in ("hold_after_leave_s", "fade_s") and E["schedule"] == "m_pass2")]
        say("  %-36s %s" % (key, fmt(stats(vals), 3)))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Mad Maggie Wrecking Ball pads, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; maggie_analysis.py"}
        for key, field, scope in (("pad.hold_after_leave_s", "hold_after_leave_s", ("m_pass", "m_walk", "m_slide", "m_stand")),
                                  ("pad.fade_s", "fade_s", ("m_pass", "m_walk", "m_slide", "m_stand")),
                                  ("pad.enter_dist", "enter_dist", ("m_pass", "m_pass2", "m_walk", "m_slide", "m_stand")),
                                  ("pad.sprint_vh", "vh_sprint_boost", ("m_pass", "m_pass2")), ("pad.walk_ms", "ms_walk_boost", ("m_walk", "m_stand")),
                                  ("pad.first_piece_s", "first_piece_s", ("m_pass", "m_pass2", "m_walk", "m_slide", "m_stand"))):
            st = stats([E.get(field) for E in res if E["schedule"] in scope])
            if st["n"]:
                P[key] = {"value": r(st["mean"], 3), "spread": {"sd": r(st["sd"], 3), "min": r(st["min"], 3), "max": r(st["max"], 3)}, "evidence": "meas", "n": st["n"]}
        P["pad.msc_boost"] = {"value": BOOST, "evidence": "meas (client msc)", "n": sum(1 for E in res if E.get("msc_max") == BOOST)}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
