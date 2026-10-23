#!/usr/bin/env python3
"""M10 track R2: Zipline Gun from a wall climb, grapple onto the own gun rope, tap strafe off an Octane pad (O-5)
(R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps; legend pathfinder with kit).

  py -3 pathfinder_analysis.py <session> [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader ../r2_common/r2_load.py; dedi logger [M10R2-ZP] (per dedi frame: zipline / wall-run /
wall-hang / grapple flags, origin, velocity, ult clip, gun ropes), [M10R2-GR] (rope-grapple aim helper: teleport + eye snap).
- z_ground_m90: the gun fired on the floor of lane A toward -Y (control that a valid target exists along the wall).
- z_climb_*: raise the gun, sprint, jump into the stacked s950 wall, then (t90 / t135: turn 90 / 135 deg in 0.1 / 0.15 s;
  side / back: 90 / 180 deg in 4 frames; t0: no turn, view 30 deg up) attack; z_climb_ctrl: the same climb without the gun.
- z_grope / z_gup / z_gdn: rope fired flat along +X from lane C (far terrain); the helper puts the player 250 u right of the rope,
  400 u from its start, eye snapped to the rope point (+0 / -1.5 / +1.5 deg pitch); then the grapple.
- o5b_* (session 2; the session-1 o5_* runs are excluded: leftover Newcastle walls on lane C): Octane pad (JumpPad_CreateAtLocation) on lane C; j<D>: pad D u ahead, sprint 1 s, jump, then 30 W press edges every
  2 frames with D held and the view turning right at 720 deg/s (tap strafe input) starting 1 frame after the jump;
  ctrl: the same TS input from the launch (no pre-pad jump); jnots: the pre-pad jump without TS input.
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
IN_FORWARD = 0x8


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


def zrows(Z, run):
    out = []
    for w in Z.get(run, []):
        d = {"t": w["t"], "zip": int(w["zip"]), "wr": int(w["wr"]), "hang": int(w.get("hang", 0)), "gract": int(w["gract"]),
             "gratt": int(w["gratt"]), "o": R.f3(w["o"]), "v": R.f3(w["v"]), "uclip": int(w["uclip"]), "gnd": int(w["gnd"]),
             "nrope": int(w["nrope"])}
        if "rope" in w:
            a, b = w["rope"].split(">")
            d["rope"] = (R.f3(a), R.f3(b))
        out.append(d)
    return out


def climb(T, Z):
    E = {"run": T["run"], "schedule": T["schedule"][6:]}
    zs = zrows(Z, T["run"])
    E["fired"] = any(w["uclip"] == 0 for w in zs)
    rope = next((w["rope"] for w in zs if w.get("rope")), None)
    E["rope"] = bool(rope)
    if rope:
        E["rope_len"] = r(math.dist(rope[0], rope[1]))
    tj = R.sched_t(T, "key=jump", 0)
    ta = R.sched_t(T, "key=attack", 0)
    wr = [s for s in T["states"] if s.get("wr")]
    if wr and tj:
        E["wr_client_s"] = (r(wr[0]["t"] - tj, 3), r(wr[-1]["t"] - tj, 3))
    swr = [w for w in zs if w["wr"]]
    if swr and tj:
        E["wr_dedi_s"] = (r(swr[0]["t"] - tj, 2), r(swr[-1]["t"] - tj, 2))
        E["wr_dedi_max_z"] = r(max(w["o"][2] for w in zs) - 294.92)
    if ta and tj:
        E["attack_s"] = r(ta - tj, 3)
        if wr:
            E["attack_in_client_wr"] = wr[0]["t"] <= ta <= wr[-1]["t"]
    return E


def grope(T, Z, G):
    E = {"run": T["run"], "schedule": T["schedule"][6:]}
    zs = zrows(Z, T["run"])
    g = G.get(T["run"])
    if g:
        E["aim_pitch"] = float(g[0]["pitch"])
    tg = R.sched_t(T, "key=offhand1", 0)
    att = next((w for w in zs if w["gratt"]), None)
    zp = next((w for w in zs if w["zip"]), None)
    E["hooked"] = att is not None
    E["zipline"] = zp is not None
    if zp and tg:
        E["press_to_zip_s"] = r(zp["t"] - tg, 2)
        pre = [w for w in zs if w["t"] < zp["t"]][-1:]
        E["speed_before_zip"] = r(math.sqrt(sum(x * x for x in pre[0]["v"])) if pre else None)
        # ride speed from the client frames (the ride is a MOVE-TRACE gap) at 0.3 / 0.6 / 1.0 / 1.5 / 2.0 s after the zip flag
        zst = [s for s in T["states"] if s.get("zip")]
        if zst:
            t0 = zst[0]["t"]
            ser = []
            for k in (0.0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 2.5):
                f = min(T["frames"], key=lambda f: abs(f["t"] - (t0 + k)))
                if abs(f["t"] - (t0 + k)) < 0.02:
                    ser.append((k, r(math.sqrt(f["vx"] ** 2 + f["vy"] ** 2 + f["vz"] ** 2))))
            E["ride_series"] = ser
            fz = [f for f in T["frames"] if f["t"] < t0][-3:]
            E["client_speed_before_zip"] = [r(math.sqrt(f["vx"] ** 2 + f["vy"] ** 2 + f["vz"] ** 2)) for f in fz]
        E["ride_vmax_dedi"] = r(max(math.hypot(w["v"][0], w["v"][1]) for w in zs if w["zip"]))
    return E


def heading(vx, vy):
    return math.degrees(math.atan2(vy, vx))


def pad_ts(T):
    E = {"run": T["run"], "schedule": T["schedule"][6:]}
    cs = [c for c in T["cmds"] if c.get("t") is not None]
    # launch = first cmd whose post vz jumps above 800 from below 400
    li = next((i for i in range(1, len(cs)) if cs[i]["pvz"] > 800 and cs[i - 1]["pvz"] < 400), None)
    if li is None:
        E["launch"] = None
        return E
    L = cs[li]
    E["launch_v"] = [r(L["pvx"]), r(L["pvy"]), r(L["pvz"])]
    E["launch_heading"] = r(heading(L["pvx"], L["pvy"]), 2)
    tj = R.sched_t(T, "key=jump", 0)
    E["jump_to_launch_cmds"] = sum(1 for c in cs if tj is not None and tj <= c["t"] < L["t"]) if tj else None
    pre = cs[li - 1]
    E["pre_heading"] = r(heading(pre["pvx"], pre["pvy"]), 2)
    E["pre_vh"] = r(math.hypot(pre["pvx"], pre["pvy"]))
    for dt in (0.1, 0.2, 0.3, 0.5):
        c = min(cs, key=lambda c: abs(c["t"] - (L["t"] + dt)))
        E["heading_+%.1f" % dt] = r(heading(c["pvx"], c["pvy"]) - E["launch_heading"], 2)
        E["vh_+%.1f" % dt] = r(math.hypot(c["pvx"], c["pvy"]))
    # forward press edges after the launch and the largest one-cmd |dv_h| (lurch) after the launch within 0.5 s
    edges = [c for i, c in enumerate(cs[1:], 1) if c["buttons"] & IN_FORWARD and not cs[i - 1]["buttons"] & IN_FORWARD]
    E["w_edges_after_launch"] = sum(1 for c in edges if L["t"] < c["t"] <= L["t"] + 0.5)
    E["w_edges_before_launch"] = sum(1 for c in edges if tj is not None and tj <= c["t"] <= L["t"])
    dv = []
    for i in range(li + 1, len(cs)):
        if cs[i]["t"] > L["t"] + 0.5:
            break
        a, b = cs[i - 1], cs[i]
        dv.append(math.hypot(b["pvx"] - a["pvx"], b["pvy"] - a["pvy"]))
    E["max_dvh_cmd_after"] = r(max(dv), 2) if dv else None
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    keep = lambda t: (t["schedule"].startswith("m10r2_z_") or t["schedule"].startswith("m10r2_o5b_")) and not t.get("explore")
    S = R.load_many(a.sessions, keep)
    Z = R.tagged_many(a.sessions, "[M10R2-ZP]")
    G = R.tagged_many(a.sessions, "[M10R2-GR]")
    say("# M10 R2 Pathfinder: Zipline Gun from a climb, grapple onto the own rope, pad tap strafe (O-5)")
    say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(S["excluded"]),
                                                    ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in S["excluded"]]))
    res = {"climb": [], "grope": [], "pad": []}
    for T in S["trials"]:
        sch = T["schedule"]
        if sch.startswith("m10r2_z_climb") or sch == "m10r2_z_ground_m90":
            res["climb"].append(climb(T, Z))
        elif sch in ("m10r2_z_grope", "m10r2_z_gup", "m10r2_z_gdn"):
            E = grope(T, Z, G)
            if G.get(T["run"]):
                res["grope"].append(E)
        elif sch.startswith("m10r2_o5"):
            res["pad"].append(pad_ts(T))
    say("\n## 1. Zipline Gun: ground control and climb fire (times from the jump press)")
    for E in res["climb"]:
        say("  r%d %-14s fired %s rope %s len %s | climb (client wr) %s dedi wr %s max z %s | attack at %s in climb %s" % (
            E["run"], E["schedule"], E["fired"], E["rope"], E.get("rope_len"), E.get("wr_client_s"), E.get("wr_dedi_s"), E.get("wr_dedi_max_z"),
            E.get("attack_s"), E.get("attack_in_client_wr")))
    say("\n## 2. Grapple onto the own gun rope (aim helper)")
    for E in res["grope"]:
        say("  r%d %-6s pitch %s | hooked %s zipline %s (%s s after the press) | speed before zip dedi %s client %s | ride (s, |v|) %s, dedi ride max %s" % (
            E["run"], E["schedule"], E.get("aim_pitch"), E["hooked"], E["zipline"], E.get("press_to_zip_s"), E.get("speed_before_zip"),
            E.get("client_speed_before_zip"), E.get("ride_series"), E.get("ride_vmax_dedi")))
    say("  hooked %d/%d, handed to the zipline %d/%d" % (sum(E["hooked"] for E in res["grope"]), len(res["grope"]),
                                                        sum(E["zipline"] for E in res["grope"]), len(res["grope"])))
    say("\n## 3. O-5 tap strafe off a pad (headings relative to the launch heading, deg)")
    for E in res["pad"]:
        say("  r%d %-9s launch %s (heading %s, pre %s at %s) jump->launch %s cmds | W edges before/after %s/%s | dHeading +0.1/0.2/0.3/0.5 s %s/%s/%s/%s | v_h %s/%s/%s/%s | max one-cmd dv_h after %s" % (
            E["run"], E["schedule"], E.get("launch_v"), E.get("launch_heading"), E.get("pre_heading"), E.get("pre_vh"), E.get("jump_to_launch_cmds"),
            E.get("w_edges_before_launch"), E.get("w_edges_after_launch"), E.get("heading_+0.1"), E.get("heading_+0.2"), E.get("heading_+0.3"),
            E.get("heading_+0.5"), E.get("vh_+0.1"), E.get("vh_+0.2"), E.get("vh_+0.3"), E.get("vh_+0.5"), E.get("max_dvh_cmd_after")))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Pathfinder R2, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; pathfinder_analysis.py"}
        gr = res["grope"]
        P["zipgun.grapple_own_rope.hooked"] = {"value": "%d/%d" % (sum(E["hooked"] for E in gr), len(gr)), "evidence": "meas", "n": len(gr)}
        P["zipgun.grapple_own_rope.zipline"] = {"value": "%d/%d" % (sum(E["zipline"] for E in gr), len(gr)), "evidence": "meas", "n": len(gr)}
        st = stats([E.get("ride_vmax_dedi") for E in gr])
        if st["n"]:
            P["zipgun.grapple_own_rope.ride_vmax"] = {"value": r(st["mean"], 2), "evidence": "meas (dedi)", "n": st["n"]}
        cl = [E for E in res["climb"] if E["schedule"].startswith("z_climb_") and E["schedule"] != "z_climb_ctrl"]
        P["zipgun.climb_fire"] = {"value": "fired %d/%d" % (sum(E["fired"] for E in cl), len(cl)), "evidence": "meas", "n": len(cl)}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
