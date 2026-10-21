"""M4b: Pathfinder grapple swing / steering / detach / release, tested against the M4 RopePull primitive.

usage:
  py -3 swing_analysis.py --swing <M4b_swing> [<M4b_swing2> ...] --m4 <M4_pathfinder> [<M4_pathfinder2> ...]
                          [--json results.json] [--params params.json]

--swing: M4b swing sessions; the first one must hold report/census.csv (the second ran with --no-census).
--m4:    M4 grapple sessions; used for the detach-rule test over all grapple trials and for the envelopes.
Trials: runner.json ok=true and warmup=false. Physics: client first-time MOVE-TRACE commands joined to the client HSD
frames (M2 loader via the M4 lg_load wrapper, both imported unchanged); the view yaw/pitch come from the joined HSD frame.
The dedi (sv) MOVE-TRACE rows of the same usercmd are compared per command (section 6).
Event detection (fire, hop/attach, pull start, pull end, impact) is the unchanged M4 grapple_events().

Geometry: wall face x = -13706 (normal -X, M4 convention). Anchor = hit of the aim ray from the eye at fire time
(origin + EYE up, yaw/pitch of the fire command) on the plane x = -13706. EYE is not measured; 60 is assumed and it
is varied in the detach-rule search.
stdlib only; no local paths (folders come from the command line).
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m4", "lift_grapple")))
import lg_load  # noqa: E402
import lift_grapple_analysis as LG  # noqa: E402  (functions only; its main() is not run)
from lg_load import IN_JUMP, IN_OFFHAND1, G, stats, fmt  # noqa: E402

WALL_X = LG.WALL_X          # -13706
EYE = 60.0                  # assumed eye height above the origin (not measured)
HOOK_T0, HOOK_SPEED = 0.0043, 2034.9   # M4 update 2 hook-flight fit
MSC = 1.15
OUT = []
NOINPUT_M4B = ("m4b_swing_side", "m4b_swing_turn", "m4b_swing_jump", "m4b_swing_turn_jump")


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def dtc(c):
    return LG.dtc(c)


def v3(c, post=False):
    return (c["pvx"], c["pvy"], c["pvz"]) if post else (c["vx"], c["vy"], c["vz"])


def o3(c, post=False):
    return (c["pox"], c["poy"], c["poz"]) if post else (c["ox"], c["oy"], c["oz"])


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def acc(c):
    dt = dtc(c)
    return [(c["pvx"] - c["vx"]) / dt, (c["pvy"] - c["vy"]) / dt, (c["pvz"] - c["vz"]) / dt]


def tspan(cm, a, b):
    return sum(dtc(cm[i]) for i in range(a, b))


def anchor(T, eye=EYE):
    x0, y0, z0 = T["o0"]
    yw, pu = T["yaw0"], T["pitch_up"]
    d = (math.cos(pu) * math.cos(yw), math.cos(pu) * math.sin(yw), math.sin(pu))
    k = (WALL_X - x0) / d[0]
    return (WALL_X, y0 + k * d[1], z0 + eye + k * d[2])


# ------------------------------------------------------------------------------------------------- loading
def load_trials(folders, tag):
    out = []
    for f in folders:
        S = lg_load.load(f)
        say(f"session {S['folder']} ({tag}): {len(S['trials'])} scored trials, parse errors {S['parse_errors']}")
        for t in S["trials"]:
            j = t["join"]
            cm = t["cmds"]
            ev = LG.grapple_events(cm, t)
            say(f"  r{t['run']} {t['schedule']:20s} cmds {j['cmds']} joined {j['cmds_with_dt']} state_bad {j['state_bad']} "
                f"cmd_gaps {j['cmd_gaps']} fps {t['fps']}" + ("" if ev else "  -> no grapple events, not used"))
            if not ev:
                continue
            c0 = cm[ev["fire"]]
            T = {"run": t["run"], "sched": t["schedule"], "session": S["folder"], "tag": tag, "cm": cm,
                 "sv": {r["cmd"]: r for r in t["sv_mt"]}, "fps": t["fps"],
                 "f": ev["fire"], "h": ev["hop"], "p": ev["pull"], "e": ev["pull_end"], "imp": ev["impact"],
                 "yaw0": math.radians(c0["yaw"]), "pitch_up": math.radians(-(c0.get("pitch") or 0.0)),
                 "o0": (c0["ox"], c0["oy"], c0["oz"])}
            T["contact_end"] = T["imp"] is not None and T["imp"] <= T["e"]
            T["jump"] = next((i for i in range(ev["fire"], len(cm)) if lg_load.aj_load.pressed(cm, i, IN_JUMP)), None)
            T["w_held"] = any(cm[i]["fwd"] for i in range(T["p"], T["e"]))
            out.append(T)
    return out


def census(folder):
    p = os.path.join(folder, "report", "census.csv")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return {r["key"]: r["cl_classvar"] for r in csv.DictReader(fh)}


# ------------------------------------------------------------------------------------------------- section 1
def section_timeline(TR, res):
    say("\n=== 1. Timeline per condition (client cmds; times from the +offhand1 press) ===")
    say("hook-flight prediction (M4): t_attach = 0.0043 + hook_len / 2034.9, hook_len = face distance / cos(yaw) / cos(pitch)")
    rows = []
    for T in TR:
        cm, f, h, p, e = T["cm"], T["f"], T["h"], T["p"], T["e"]
        dface = WALL_X - T["o0"][0]
        hook = dface / math.cos(T["yaw0"]) / math.cos(T["pitch_up"])
        ce = cm[e]
        r = {"run": T["run"], "sched": T["sched"], "tag": T["tag"], "t_attach": tspan(cm, f, h), "t_pull": tspan(cm, f, p),
             "windup": tspan(cm, h, p), "pull_dur": tspan(cm, p, e), "hook_len": hook,
             "t_attach_pred": HOOK_T0 + hook / HOOK_SPEED, "v_end": norm(v3(ce)), "gap_end": WALL_X - ce["ox"],
             "end": "contact" if T["contact_end"] else "detach",
             "t_jump": tspan(cm, f, T["jump"]) if T["jump"] is not None else None,
             "heading_end": math.degrees(math.atan2(ce["vy"], ce["vx"])), "z_end": ce["oz"], "vz_end": ce["vz"]}
        rows.append(r)
    conds = []
    for r in rows:
        if r["sched"] not in conds:
            conds.append(r["sched"])
    say(f"{'condition':20s} {'n':>2s} {'hook':>6s} {'t_att':>6s} {'pred':>6s} {'windup':>6s} {'pull_dur':>8s} {'end':>8s} "
        f"{'v_end':>6s} {'gap':>5s} {'head':>6s} {'jump@':>6s}")
    by = {}
    for cnd in conds:
        rr = [r for r in rows if r["sched"] == cnd]
        S = {k: stats([r[k] for r in rr]) for k in ("hook_len", "t_attach", "t_attach_pred", "windup", "pull_dur", "v_end",
                                                      "gap_end", "heading_end", "z_end", "vz_end", "t_jump")}
        S["end"] = sorted({r["end"] for r in rr})
        by[cnd] = S
        say(f"{cnd:20s} {len(rr):2d} {S['hook_len']['mean']:6.1f} {S['t_attach']['mean']:6.3f} {S['t_attach_pred']['mean']:6.3f} "
            f"{S['windup']['mean']:6.3f} {S['pull_dur']['mean']:8.3f} {'/'.join(S['end']):>8s} {S['v_end']['mean']:6.1f} "
            f"{S['gap_end']['mean']:5.1f} {S['heading_end']['mean']:6.2f} "
            f"{(S['t_jump']['mean'] if S['t_jump'].get('n') else float('nan')):6.3f}")
    m4b = [r for r in rows if r["tag"] == "m4b"]
    say("M4b attach time vs hook model:", fmt(stats([r["t_attach"] - r["t_attach_pred"] for r in m4b]), 4), "s;  wind-up",
        fmt(stats([r["windup"] for r in m4b]), 4), "s")
    res["timeline"] = {"trials": rows, "by_condition": by}


# ------------------------------------------------------------------------------------------------- section 2
def pull_kinematics(T, eye=EYE):
    """Per pull command: distance to the anchor, radial/tangential speed, horizontal accel vs rope azimuth."""
    cm, p, e = T["cm"], T["p"], T["e"]
    A = anchor(T, eye)
    out = []
    for i in range(p, e):
        c = cm[i]
        o, v, a = o3(c), v3(c), acc(c)
        r = sub(A, o)
        d = norm(r)
        u = [x / d for x in r]
        vr = dot(v, u)
        vt = norm([v[k] - vr * u[k] for k in range(3)])
        dh = math.hypot(r[0], r[1])
        rx, ry = r[0] / dh, r[1] / dh
        a_lon = a[0] * rx + a[1] * ry
        a_lat = -a[0] * ry + a[1] * rx          # + = left of the rope (horizontal)
        v_lat = -v[0] * ry + v[1] * rx
        yw = math.radians(c["yaw"]) if c.get("yaw") is not None else T["yaw0"]
        w = (math.cos(yw), math.sin(yw))
        out.append({"i": i, "t": tspan(cm, p, i), "d": d, "dh": dh, "v": norm(v), "vr": vr, "vt": vt, "a_lon": a_lon,
                    "a_lat": a_lat, "a_z": a[2], "v_lat": v_lat, "a_w": a[0] * w[0] + a[1] * w[1],
                    "v_w": v[0] * w[0] + v[1] * w[1], "vh": math.hypot(v[0], v[1]), "yaw": c.get("yaw"),
                    "az_rope": math.degrees(math.atan2(ry, rx)), "az_acc": math.degrees(math.atan2(a[1], a[0])),
                    "head": math.degrees(math.atan2(v[1], v[0])), "elev_v": math.degrees(math.atan2(v[2], math.hypot(v[0], v[1]))),
                    "elev_rope": math.degrees(math.atan2(r[2], dh)), "y_int": c["oy"] + (WALL_X - c["ox"]) * a[1] / a[0]
                    if abs(a[0]) > 1e-6 else None, "fwd": c["fwd"]})
    return out


def section_rope(TR, res):
    say("\n=== 2. Q1: rope constraint or pure acceleration; tangential motion; effective pull direction ===")
    say("anchor = aim-ray hit on x = -13706 from origin + 60 u (eye assumed); 'after burst' = from 10 cmds after the pull start")
    R = {"trials": []}
    say(f"{'run':>5s} {'condition':20s} {'d_up_max':>8s} {'vt0':>6s} {'n<10':>5s} {'vt_max':>6s} {'vr/v_min':>8s} "
        f"{'lat_max':>7s} {'az_err':>13s} {'y_int':>15s} {'y_aim':>7s} {'ramp':>6s} {'elev_v-rope_end':>15s}")
    for T in TR:
        K = pull_kinematics(T)
        T["K"] = K
        cm, p = T["cm"], T["p"]
        dup = max(K[k + 1]["d"] - K[k]["d"] for k in range(len(K) - 1))
        vt0 = K[0]["vt"]
        n10 = next((k for k in range(len(K)) if K[k]["vt"] < 10), None)
        after = K[10:]
        vtmax = max(k["vt"] for k in after)
        vrmin = min(k["vr"] / k["v"] for k in after)
        A = anchor(T)
        x0, y0 = cm[p]["ox"], cm[p]["oy"]
        ux, uy = A[0] - x0, A[1] - y0
        n = math.hypot(ux, uy)
        lat = max(abs(-(cm[i]["ox"] - x0) * uy / n + (cm[i]["oy"] - y0) * ux / n) for i in range(p, T["e"]))
        far = [k for k in after if k["dh"] > 150]
        az = stats([k["az_acc"] - k["az_rope"] for k in far]) if not T["w_held"] else {"n": 0}
        yi = stats([k["y_int"] for k in far if k["y_int"] is not None]) if not T["w_held"] else {"n": 0}
        tv = [k["t"] for k in far]
        vv = [norm(v3(cm[k["i"]], True)) for k in far]
        ramp = LG.linfit(tv, vv)[1] if len(tv) > 5 else None
        el_end = K[-1]["elev_v"] - K[-1]["elev_rope"]
        row = {"run": T["run"], "sched": T["sched"], "tag": T["tag"], "d_increase_max": dup, "vt_start": vt0,
               "cmds_to_vt_below_10": n10, "vt_max_after_burst": vtmax, "vr_over_v_min": vrmin, "lateral_max": lat,
               "az_err": az, "y_int": yi, "y_aim": A[1], "speed_ramp": ramp, "elev_v_minus_rope_end": el_end,
               "elev_v_minus_rope_mid": K[len(K) // 2]["elev_v"] - K[len(K) // 2]["elev_rope"], "w": T["w_held"]}
        R["trials"].append(row)
        say(f"{T['run']:5d} {T['sched']:20s} {dup:8.3f} {vt0:6.1f} {str(n10):>5s} {vtmax:6.1f} {vrmin:8.4f} {lat:7.2f} "
            + (f"{az['mean']:6.2f}+-{az['sd']:5.2f}" if az.get("n") else f"{'(W)':>13s}") + " "
            + (f"{yi['mean']:7.1f}+-{yi['sd']:5.1f}" if yi.get("n") else f"{'':15s}")
            + f" {A[1]:7.1f} {(ramp or float('nan')):6.1f} {el_end:15.2f}")
    # group summaries
    R["groups"] = {}
    for name, sel in (("m4b_noinput_noturn", lambda r: r["sched"] in ("m4b_swing_side", "m4b_swing_jump")),
                      ("m4b_noinput_turn", lambda r: r["sched"] in ("m4b_swing_turn", "m4b_swing_turn_jump")),
                      ("m4b_turn_w", lambda r: r["sched"] == "m4b_swing_turn_w"),
                      ("m4_noinput", lambda r: r["tag"] == "m4" and not r["w"]),
                      ("m4_fwd", lambda r: r["tag"] == "m4" and r["w"]),
                      ("cross_noinput (r2)", lambda r: r["sched"] in ("m4b_swing_cross", "m4b_swing_cross_walk")),
                      ("cross_w (r2)", lambda r: r["sched"] == "m4b_swing_cross_w")):
        rr = [r for r in R["trials"] if sel(r)]
        if not rr:
            continue
        g = {k: stats([r[k] for r in rr]) for k in ("d_increase_max", "vt_start", "cmds_to_vt_below_10", "vt_max_after_burst",
                                                     "vr_over_v_min", "lateral_max", "speed_ramp", "elev_v_minus_rope_end",
                                                     "elev_v_minus_rope_mid")}
        g["az_err_mean"] = stats([r["az_err"]["mean"] for r in rr if r["az_err"].get("n")])
        g["az_err_sd_within"] = stats([r["az_err"]["sd"] for r in rr if r["az_err"].get("n")])
        g["y_int_minus_aim"] = stats([r["y_int"]["mean"] - r["y_aim"] for r in rr if r["y_int"].get("n")])
        R["groups"][name] = g
        say(f"\n[{name}] n={len(rr)}")
        say("  max increase of the 3D anchor distance between cmds (u):", fmt(g["d_increase_max"], 3))
        say("  tangential speed at pull start (u/s):", fmt(g["vt_start"], 1), "; cmds until < 10 u/s:", fmt(g["cmds_to_vt_below_10"], 1))
        say("  after the burst: max tangential speed (u/s):", fmt(g["vt_max_after_burst"], 1), "; min v_r/|v|:", fmt(g["vr_over_v_min"], 4))
        say("  max lateral deviation of the path from the start->anchor line (u):", fmt(g["lateral_max"], 2))
        if g["az_err_mean"].get("n"):
            say("  horizontal accel azimuth - rope azimuth (deg, > 150 u from the anchor): mean", fmt(g["az_err_mean"], 3),
                "; within-trial sd", fmt(g["az_err_sd_within"], 3))
            say("  horizontal accel lines cross the face at y - aim-ray hit y (u):", fmt(g["y_int_minus_aim"], 2))
        say("  speed ramp d|v|/dt (> 150 u from the anchor, u/s^2):", fmt(g["speed_ramp"], 1))
        say("  elevation of v minus elevation of the rope (deg): mid-pull", fmt(g["elev_v_minus_rope_mid"], 2), "; last pulled cmd",
            fmt(g["elev_v_minus_rope_end"], 2))
    res["rope"] = R


# ------------------------------------------------------------------------------------------------- section 3
def mean_series(trials, key, tgrid):
    out = []
    for tg in tgrid:
        vals = []
        for T in trials:
            K = T["K"]
            k = min(K, key=lambda x: abs(x["t"] - tg))
            if abs(k["t"] - tg) < 0.006:
                vals.append(k[key])
        out.append(sum(vals) / len(vals) if vals else None)
    return out


def section_steer(TR, res):
    say("\n=== 3. Q2: steering - view turn without and with W ===")
    R = {}
    side = [T for T in TR if T["sched"] in ("m4b_swing_side", "m4b_swing_jump")]
    turn = [T for T in TR if T["sched"] in ("m4b_swing_turn", "m4b_swing_turn_jump")]
    tw = [T for T in TR if T["sched"] == "m4b_swing_turn_w"]
    fwd = [T for T in TR if T["sched"] == "m4_grapple_fwd"]
    if not (side and turn):
        return
    # end-state differences turn - side
    def end(T, k):
        c = T["cm"][T["e"]]
        return {"head": math.degrees(math.atan2(c["vy"], c["vx"])), "vz": c["vz"], "z": c["oz"], "y": c["oy"],
                "v": norm(v3(c)), "vy": c["vy"], "yaw": c["yaw"], "dur": tspan(T["cm"], T["p"], T["e"])}[k]
    R["end"] = {}
    say(f"{'quantity at the first released cmd':36s} {'no turn (side+jump)':>28s} {'turn (turn+turn_jump)':>28s} {'turn_w':>28s}")
    for k in ("yaw", "head", "v", "vy", "vz", "z", "dur"):
        a, b, c = stats([end(T, k) for T in side]), stats([end(T, k) for T in turn]), stats([end(T, k) for T in tw])
        R["end"][k] = {"side": a, "turn": b, "turn_w": c}
        say(f"{k:36s} {fmt(a, 2):>28s} {fmt(b, 2):>28s} {fmt(c, 2):>28s}")
    # lateral accel during and after the turn (no W)
    lat_turn, lat_after, latd_after = [], [], []
    for T in turn:
        K = T["K"]
        for k in K:
            if k["t"] < 0.12:
                continue
            ys = [x["yaw"] for x in K]
            j = K.index(k)
            turning = j > 0 and abs(K[j]["yaw"] - K[j - 1]["yaw"]) > 0.5
            if turning:
                lat_turn.append(k["a_lat"])
            elif k["yaw"] < 0 and 50 < k["dh"] < 250:
                lat_after.append(k["a_lat"])
                latd_after.append(k["a_lat"] * k["dh"])
    side_lat = [k["a_lat"] for T in side for k in T["K"] if k["t"] > 0.12 and k["dh"] > 50]
    R["a_lat_side"] = stats(side_lat)
    R["a_lat_turning"] = stats(lat_turn)
    R["a_lat_after_turn"] = stats(lat_after)
    R["a_lat_times_d_after_turn"] = stats(latd_after)
    say("\nno W, horizontal accel perpendicular to the rope (+ = left of the rope, u/s^2):")
    say("  no turn                           ", fmt(R["a_lat_side"], 2))
    say("  while the view turns right (~90 deg/s)", fmt(R["a_lat_turning"], 2))
    say("  after the turn (view 54 deg right of the rope), 50 < d_h < 250:", fmt(R["a_lat_after_turn"], 2))
    say("  same, a_lat * d_h (u^2/s^2):        ", fmt(R["a_lat_times_d_after_turn"], 0),
        " (constant => a lateral offset of the rope's player end of a_lat*d/|a_lon| ~ "
        f"{R['a_lat_times_d_after_turn']['mean'] / 470.0:.1f} u at |a_lon| ~ 470) [inf]")
    tg = [0.1 * k for k in range(1, 12)]
    hs, ht, hw = mean_series(side, "head", tg), mean_series(turn, "head", tg), mean_series(tw, "head", tg)
    vs, vt, vw = mean_series(side, "v", tg), mean_series(turn, "v", tg), mean_series(tw, "v", tg)
    yw = mean_series(tw, "yaw", tg)
    aws, awt, aww = mean_series(side, "a_w", tg), mean_series(turn, "a_w", tg), mean_series(tw, "a_w", tg)
    say("\ntime series (mean over trials; t from pull start): velocity heading (deg), |v| (u/s), accel along the flat view forward a.w")
    say(f"{'t':>5s} {'yaw_w':>7s} | {'head_side':>9s} {'head_turn':>9s} {'head_W':>7s} | {'v_side':>7s} {'v_turn':>7s} {'v_W':>7s} | "
        f"{'aw_side':>7s} {'aw_turn':>7s} {'aw_W':>7s}")
    f_ = lambda x, n=2: (f"{x:.{n}f}" if x is not None else "-")  # noqa: E731
    R["series"] = []
    for k, t in enumerate(tg):
        R["series"].append({"t": t, "yaw_w": yw[k], "head_side": hs[k], "head_turn": ht[k], "head_w": hw[k], "v_side": vs[k],
                            "v_turn": vt[k], "v_w": vw[k], "aw_side": aws[k], "aw_turn": awt[k], "aw_w": aww[k]})
        say(f"{t:5.2f} {f_(yw[k]):>7s} | {f_(hs[k]):>9s} {f_(ht[k]):>9s} {f_(hw[k]):>7s} | {f_(vs[k], 1):>7s} {f_(vt[k], 1):>7s} "
            f"{f_(vw[k], 1):>7s} | {f_(aws[k], 0):>7s} {f_(awt[k], 0):>7s} {f_(aww[k], 0):>7s}")
    # W: accel along the view forward, speed ramp, horizontal speed vs the 483 cap
    if tw:
        aw = [k["a_w"] for T in tw for k in T["K"] if k["t"] > 0.25 and k["dh"] > 100]
        azw = [k["a_z"] for T in tw for k in T["K"] if k["t"] > 0.25 and k["dh"] > 100]
        vhmax = [max(k["vh"] for k in T["K"]) for T in tw]
        vwmax = [max(k["v_w"] for k in T["K"]) for T in tw]
        ramp = []
        for T in tw:
            far = [k for k in T["K"] if k["t"] > 0.12 and k["dh"] > 150]
            ramp.append(LG.linfit([k["t"] for k in far], [norm(v3(T["cm"][k["i"]], True)) for k in far])[1])
        latmax = [max(abs(k["a_lat"]) for k in T["K"] if k["t"] > 0.12) for T in tw]
        R["turn_w"] = {"a_w": stats(aw), "a_z": stats(azw), "vh_max": stats(vhmax), "v_w_max": stats(vwmax),
                       "speed_ramp": stats(ramp), "a_lat_abs_max": stats(latmax)}
        say("\nW held + view turn (turn_w):")
        say("  accel along the flat view forward a.w (t > 0.25 s, d_h > 100, u/s^2):", fmt(R["turn_w"]["a_w"], 1))
        say("  vertical accel a_z (same cmds, u/s^2):", fmt(R["turn_w"]["a_z"], 1))
        say("  speed ramp d|v|/dt (u/s^2):", fmt(R["turn_w"]["speed_ramp"], 1))
        say("  max horizontal speed (u/s):", fmt(R["turn_w"]["vh_max"], 1), "-> M4 'W clamps v_h to 483' does NOT hold here")
        say("  max v.w (velocity along the view forward, u/s):", fmt(R["turn_w"]["v_w_max"], 1),
            "-> a clamp of v.w at 483 = 420*msc is not contradicted (never reached)")
        say("  max |horizontal accel perpendicular to the rope| (u/s^2):", fmt(R["turn_w"]["a_lat_abs_max"], 1))
    if fwd:
        pre = [k for T in fwd for k in T["K"] if k["t"] > 0.25
               and math.hypot(T["cm"][k["i"]]["pvx"], T["cm"][k["i"]]["pvy"]) < 482.9]
        cap = [k for T in fwd for k in T["K"] if k["vh"] >= 482.99]
        ax = stats([k["a_w"] for k in pre])
        az = stats([k["a_z"] for k in pre])
        azc = stats([k["a_z"] for k in cap])
        vhc = stats([k["vh"] for k in cap])
        R["m4_fwd"] = {"a_w_precap": ax, "a_z_precap": az, "a_z_capped": azc, "vh_capped": vhc}
        say("\nM4 m4_grapple_fwd (W toward the anchor, view = rope azimuth) for comparison:")
        say("  before the cap (t > 0.25 s): a.w", fmt(ax, 1), "; a_z", fmt(az, 1))
        say("  capped: v_h", fmt(vhc, 3), "; a_z", fmt(azc, 1))
    res["steer"] = R


# ------------------------------------------------------------------------------------------------- section 4
def features(T, i, eye=EYE, hgt=0.0):
    cm = T["cm"]
    c = cm[i]
    A = anchor(T, eye)
    o, v = o3(c), v3(c)
    r = [A[0] - o[0], A[1] - o[1], A[2] - o[2] - hgt]
    d = norm(r)
    dh = math.hypot(r[0], r[1])
    sp = norm(v)
    vr = dot(v, r) / d
    p = T["p"]
    d0 = norm([A[0] - cm[p]["ox"], A[1] - cm[p]["oy"], A[2] - cm[p]["oz"] - hgt])
    gap = WALL_X - c["ox"]
    return {"gap": gap, "gap_post": WALL_X - c["pox"], "d3": d, "dh": dh, "dz": r[2], "tt_face": (gap - 16.0) / c["vx"] if c["vx"] > 1 else 99,
            "tt_anchor": d / sp if sp > 1 else 99, "tt_radial": d / vr if vr > 1 else 99, "frac_d0": d / d0,
            "t_pull": tspan(cm, p, i), "t_fire": tspan(cm, T["f"], i), "speed": sp,
            "ang_v_rope": math.degrees(math.acos(max(-1.0, min(1.0, vr / sp)))) if sp > 1 else 0.0,
            "rope_elev_abs": abs(math.degrees(math.atan2(r[2], dh)))}


RULES = (("gap", "<"), ("gap_post", "<"), ("d3", "<"), ("dh", "<"), ("tt_face", "<"), ("tt_anchor", "<"), ("tt_radial", "<"),
         ("frac_d0", "<"), ("t_pull", ">"), ("t_fire", ">"), ("speed", ">"), ("ang_v_rope", ">"), ("rope_elev_abs", ">"))


def rule_test(TR, key, sense, eye=EYE, hgt=0.0):
    """Each trial contributes its pulled cmds (pre-state, from 10 cmds after the pull start) and, if it detached
    before contact, its first released cmd. Rule: release at the first cmd where key < T (or > T)."""
    det, pul = [], []
    for T in TR:
        last = T["e"] + 1 if T["contact_end"] else T["e"]
        pv = [features(T, i, eye, hgt)[key] for i in range(T["p"] + 10, last)]
        dv = None if T["contact_end"] else features(T, T["e"], eye, hgt)[key]
        if sense == ">":
            pv = [-x for x in pv]
            dv = None if dv is None else -dv
        pul.append(min(pv))
        det.append(dv)
    # best threshold: minimise the number of trials whose release is mispredicted
    cands = sorted({x for x in pul} | {x for x in det if x is not None})
    best = None
    for k in range(len(cands)):
        thr = cands[k] + 1e-9
        bad = sum(1 for a, b in zip(pul, det) if a < thr or (b is not None and b >= thr))
        if best is None or bad < best[1]:
            best = (thr, bad)
    dmax = max(x for x in det if x is not None)
    pmin = min(pul)
    sg = -1 if sense == ">" else 1
    return {"released_max": sg * dmax, "pulled_min": sg * pmin, "consistent": dmax < pmin, "best_T": sg * best[0],
            "mispredicted": best[1], "n": len(TR), "n_detached": sum(1 for x in det if x is not None)}


def section_detach(TR, res):
    say("\n=== 4. Q3: detach rule over all M4 + M4b grapple trials ===")
    R = {"rules": {}}
    rows = []
    for T in TR:
        F = features(T, T["e"])
        Fl = features(T, T["e"] - 1)
        rows.append({"run": T["run"], "sched": T["sched"], "end": "contact" if T["contact_end"] else "detach", "w": T["w_held"],
                     "at_release": F, "last_pulled": Fl, "imp_minus_end": (T["imp"] - T["e"]) if T["imp"] is not None else None})
    R["trials"] = rows
    say(f"{'condition':20s} {'n':>2s} {'end':>14s} {'gap':>13s} {'d3(60,0)':>13s} {'t_pull':>7s} {'speed':>6s} {'ang_v_rope':>10s} "
        f"{'cmds to impact':>14s}")
    conds = []
    for r in rows:
        if r["sched"] not in conds:
            conds.append(r["sched"])
    for cnd in conds:
        rr = [r for r in rows if r["sched"] == cnd]
        ends = sorted({r["end"] for r in rr})
        g = stats([r["at_release"]["gap"] for r in rr])
        d = stats([r["at_release"]["d3"] for r in rr])
        imp = [r["imp_minus_end"] for r in rr if r["imp_minus_end"] is not None]
        say(f"{cnd:20s} {len(rr):2d} {'/'.join(ends):>14s} {g['min']:5.1f}..{g['max']:5.1f} {d['min']:5.1f}..{d['max']:5.1f} "
            f"{stats([r['at_release']['t_pull'] for r in rr])['mean']:7.3f} {stats([r['at_release']['speed'] for r in rr])['mean']:6.1f} "
            f"{stats([r['at_release']['ang_v_rope'] for r in rr])['mean']:10.2f} "
            f"{(str(min(imp)) + '..' + str(max(imp))) if imp else 'none':>14s}")
    say("('contact' = still pulled on the wall-impact cmd; quantities are taken on the pre-state of the first released / impact cmd)")
    say("\nsingle-feature threshold rules (release at the first cmd with feature < T or > T; pulled cmds from pull start + 10):")
    say(f"{'feature':14s} {'sense':>5s} {'released max':>12s} {'pulled min':>11s} {'consistent':>10s} {'best T':>9s} {'mispredicted trials':>20s}")
    for key, sense in RULES:
        rt = rule_test(TR, key, sense)
        R["rules"][key] = rt
        say(f"{key:14s} {sense:>5s} {rt['released_max']:12.3f} {rt['pulled_min']:11.3f} {str(rt['consistent']):>10s} "
            f"{rt['best_T']:9.3f} {rt['mispredicted']:>8d} / {rt['n']}")
    # 3D distance from a body point (origin + hgt) to the anchor (eye assumed) over a grid
    grid = []
    for eye in range(36, 76, 4):
        for hgt in range(0, 78, 6):
            rt = rule_test(TR, "d3", "<", eye, hgt)
            grid.append((rt["mispredicted"], eye, hgt, rt))
    grid.sort(key=lambda x: x[0])
    R["d3_grid_best"] = [{"eye": g[1], "body_h": g[2], **g[3]} for g in grid[:5]]
    say("\n3D distance rule, grid over eye height (anchor) and body-point height: best 5")
    for g in grid[:5]:
        say(f"  eye {g[1]:3d} body {g[2]:3d}: released max {g[3]['released_max']:.2f}, pulled min {g[3]['pulled_min']:.2f}, "
            f"mispredicted {g[0]} / {g[3]['n']}")
    # same tests restricted to no-input trials (W trials have their own release behaviour)
    noW = [T for T in TR if not T["w_held"]]
    R["rules_noW"] = {k: rule_test(noW, k, s) for k, s in RULES}
    say(f"\nno-input trials only (n={len(noW)}):")
    for key, sense in RULES:
        rt = R["rules_noW"][key]
        say(f"  {key:14s} {sense}: released max {rt['released_max']:9.3f}  pulled min {rt['pulled_min']:9.3f}  "
            f"consistent {rt['consistent']}  best T {rt['best_T']:.3f}  mispredicted {rt['mispredicted']}/{rt['n']}")
    gaps = [r["at_release"]["gap"] for r in rows if r["end"] == "detach" and not r["w"]]
    R["gap_envelope_noW"] = stats(gaps)
    R["gap_envelope_W_detach"] = stats([r["at_release"]["gap"] for r in rows if r["end"] == "detach" and r["w"]])
    R["gap_at_contact_W"] = stats([r["at_release"]["gap"] for r in rows if r["end"] == "contact"])
    say("\nrelease envelope (origin gap to the face on the first released cmd): no input", fmt(R["gap_envelope_noW"], 2),
        "; W, released", fmt(R["gap_envelope_W_detach"], 2), "; W, still pulled at contact", fmt(R["gap_at_contact_W"], 2))
    res["detach"] = R


# ------------------------------------------------------------------------------------------------- section 5
def section_release(TR, res):
    say("\n=== 5. Q4: momentum at and after release; jump release ===")
    R = {"trials": []}
    for T in TR:
        if T["contact_end"]:
            continue
        cm, e = T["cm"], T["e"]
        cont = norm(sub(v3(cm[e]), v3(cm[e - 1], True)))       # pre(e) vs post(e-1): set outside the move?
        bal = LG.ballistic_dev(cm[e])
        n_bal = (T["imp"] - e) if T["imp"] is not None else None
        gs = [-(cm[i]["pvz"] - cm[i]["vz"]) / dtc(cm[i]) for i in range(e, (T["imp"] if T["imp"] else min(len(cm), e + 30)))
              if cm[i]["ground"] == 0]
        dh = [math.hypot(cm[i]["pvx"], cm[i]["pvy"]) - math.hypot(cm[i]["vx"], cm[i]["vy"])
              for i in range(e, (T["imp"] if T["imp"] else min(len(cm), e + 30)))]
        post = None
        if T["imp"] is not None:
            ci = cm[T["imp"]]
            post = {"vx": ci["pvx"], "vy": ci["pvy"], "vz": ci["pvz"], "vy_pre": ci["vy"]}
        R["trials"].append({"run": T["run"], "sched": T["sched"], "v_release": norm(v3(cm[e])),
                            "vh_release": math.hypot(cm[e]["vx"], cm[e]["vy"]), "vz_release": cm[e]["vz"],
                            "continuity": cont, "ballistic_dev_first": bal, "ballistic_cmds_before_impact": n_bal,
                            "g_after": stats(gs), "dh_after_max": max(abs(x) for x in dh) if dh else None, "impact_post": post})
    rr = R["trials"]
    say("velocity continuity at release |v_pre(first released) - v_post(last pulled)| (u/s):", fmt(stats([r["continuity"] for r in rr]), 4))
    say("first released cmd deviation from ballistic (u/s):", fmt(stats([r["ballistic_dev_first"] for r in rr]), 4))
    say("gravity after release (u/s^2):", fmt(stats([r["g_after"]["mean"] for r in rr if r["g_after"].get("n")]), 2),
        "; max |d v_h| per cmd after release:", fmt(stats([r["dh_after_max"] for r in rr if r["dh_after_max"] is not None]), 4))
    say("ballistic cmds between release and wall impact:", fmt(stats([r["ballistic_cmds_before_impact"] for r in rr
                                                                        if r["ballistic_cmds_before_impact"] is not None]), 1))
    by = {}
    for r in rr:
        by.setdefault(r["sched"], []).append(r)
    say(f"\n{'condition':20s} {'n':>2s} {'|v| release':>24s} {'v_h':>8s} {'vz':>8s}")
    R["by_condition"] = {}
    for k, v in by.items():
        s = {x: stats([r[x] for r in v]) for x in ("v_release", "vh_release", "vz_release")}
        R["by_condition"][k] = s
        say(f"{k:20s} {len(v):2d} {fmt(s['v_release'], 1):>24s} {s['vh_release']['mean']:8.1f} {s['vz_release']['mean']:8.1f}")
    # wall impact: what is kept
    imp = [r["impact_post"] for r in rr if r["impact_post"]]
    R["impact"] = {"vx_after": stats([x["vx"] for x in imp]), "vy_kept": stats([x["vy"] - x["vy_pre"] for x in imp]),
                   "vz_after": stats([x["vz"] for x in imp])}
    say("\nwall impact after a release: vx after", fmt(R["impact"]["vx_after"], 2), "; vy change (wall-parallel kept)",
        fmt(R["impact"]["vy_kept"], 3), "; vz after", fmt(R["impact"]["vz_after"], 1))
    # jump release test: jump trial vs the mean of the matching no-jump group, aligned on the pull start
    say("\njump press during the pull (0.81 s after fire = 0.39 s into the pull):")
    R["jump"] = {}
    for jg, rg in (("m4b_swing_jump", "m4b_swing_side"), ("m4b_swing_turn_jump", "m4b_swing_turn"), ("m4_grapple_jump", "m4_grapple_hold")):
        J = [T for T in TR if T["sched"] == jg]
        Rf = [T for T in TR if T["sched"] == rg]
        if not J or len(Rf) < 2:
            continue
        def dev(T, refs):
            mx = 0.0
            k0 = (T["jump"] - T["p"]) if T["jump"] is not None else 10
            n = min(T["e"] - T["p"], min(Ri["e"] - Ri["p"] for Ri in refs))
            for k in range(max(0, k0), n - 1):
                vm = [sum(v3(Ri["cm"][Ri["p"] + k], True)[j] for Ri in refs) / len(refs) for j in range(3)]
                mx = max(mx, norm(sub(v3(T["cm"][T["p"] + k], True), vm)))
            return mx
        dj = [dev(T, Rf) for T in J]
        T0 = J[0]
        base = []
        for k, T in enumerate(Rf):
            others = [x for x in Rf if x is not T]
            Tc = dict(T)
            Tc["jump"] = T["p"] + (T0["jump"] - T0["p"])
            base.append(dev(Tc, others))
        dur_j = stats([tspan(T["cm"], T["p"], T["e"]) for T in J])
        dur_r = stats([tspan(T["cm"], T["p"], T["e"]) for T in Rf])
        R["jump"][jg] = {"max_dv_vs_ref": stats(dj), "ref_baseline": stats(base), "pull_dur_jump": dur_j, "pull_dur_ref": dur_r,
                         "jump_into_pull": stats([tspan(T["cm"], T["p"], T["jump"]) for T in J])}
        say(f"  {jg} vs {rg}: max |dv| after the press {fmt(stats(dj), 2)}; same metric within {rg} {fmt(stats(base), 2)}; "
            f"pull duration {dur_j['mean']:.3f} vs {dur_r['mean']:.3f} s; press at {R['jump'][jg]['jump_into_pull']['mean']:.3f} s into the pull")
    res["release"] = R


# ------------------------------------------------------------------------------------------------- section 6
def section_dedi(TR, res):
    say("\n=== 6. Client vs dedi during the pull (M4b trials) ===")
    R = []
    for T in TR:
        if T["tag"] != "m4b":
            continue
        cm, sv = T["cm"], T["sv"]
        dv, dp, miss, corr = 0.0, 0.0, 0, 0
        for i in range(T["p"], T["e"] + 1):
            s = sv.get(cm[i]["cmd"])
            if i > T["p"] and norm(sub(v3(cm[i]), v3(cm[i - 1], True))) > 0.01:
                corr += 1
            if not s:
                miss += 1
                continue
            dv = max(dv, norm(sub(v3(cm[i], True), v3(s, True))))
            dp = max(dp, norm(sub(o3(cm[i], True), o3(s, True))))
        # dedi release cmd: same ballistic test on the dedi rows with the client's dt
        e_sv = None
        for i in range(T["p"] + 10, min(len(cm), T["e"] + 10)):
            s = sv.get(cm[i]["cmd"])
            if not s:
                continue
            ss = dict(s)
            ss["dt"] = cm[i]["dt"]
            dev = abs(ss["pvz"] - (ss["vz"] - G * dtc(ss))) if T["w_held"] else LG.ballistic_dev(ss)
            if dev <= LG.PULL_TOL or ss["pvx"] - ss["vx"] < -50:
                e_sv = i
                break
        R.append({"run": T["run"], "sched": T["sched"], "max_dv": dv, "max_dpos": dp, "sv_missing": miss,
                  "client_corrections": corr, "release_cmd_sv_minus_cl": (e_sv - T["e"]) if e_sv is not None else None})
    say("max |post v client - dedi| during the pull (u/s):", fmt(stats([r["max_dv"] for r in R]), 3))
    say("max |post origin client - dedi| (u):", fmt(stats([r["max_dpos"] for r in R]), 3))
    say("client prediction corrections per pull (pre v != previous post v):", fmt(stats([r["client_corrections"] for r in R]), 1))
    say("dedi rows missing in the pull window:", fmt(stats([r["sv_missing"] for r in R]), 1))
    say("release/contact cmd, dedi minus client (cmds):", sorted({r["release_cmd_sv_minus_cl"] for r in R}, key=lambda x: (x is None, x)))
    res["dedi"] = R


# ------------------------------------------------------------------------------------------------- section 7
def section_envelopes(TR, res):
    say("\n=== 7. Observed envelopes for a Unity swing/pull (all grapple trials) ===")
    tg = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]
    conds = []
    for T in TR:
        if T["sched"] not in conds:
            conds.append(T["sched"])
    R = {"speed_vs_t": {}, "elev_vs_t": {}}
    say("mean |v| (u/s) vs time since pull start (blank = released)")
    say(f"{'condition':20s} " + " ".join(f"{t:6.1f}" for t in tg) + "   release")
    for cnd in conds:
        tr = [T for T in TR if T["sched"] == cnd]
        row = []
        for t in tg:
            vals = []
            for T in tr:
                k = min(T["K"], key=lambda x: abs(x["t"] - t))
                if abs(k["t"] - t) < 0.006:
                    vals.append(k["v"])
            row.append(sum(vals) / len(vals) if len(vals) == len(tr) else None)
        rel = stats([norm(v3(T["cm"][T["e"]])) for T in tr])
        R["speed_vs_t"][cnd] = {"t": tg, "v": row, "release": rel}
        say(f"{cnd:20s} " + " ".join(f"{x:6.1f}" if x is not None else "      " for x in row) + f"   {rel['mean']:6.1f}")
    say("\nvelocity elevation (deg) vs time since pull start")
    for cnd in conds:
        tr = [T for T in TR if T["sched"] == cnd]
        row = []
        for t in tg:
            vals = []
            for T in tr:
                k = min(T["K"], key=lambda x: abs(x["t"] - t))
                if abs(k["t"] - t) < 0.006:
                    vals.append(k["elev_v"])
            row.append(sum(vals) / len(vals) if len(vals) == len(tr) else None)
        R["elev_vs_t"][cnd] = row
        say(f"{cnd:20s} " + " ".join(f"{x:6.1f}" if x is not None else "      " for x in row))
    # speed law |v| = v0 + A t (t since pull start), fitted per condition over the pulled cmds after the burst
    say("\nspeed law |v| = v0 + A * t_pull, fitted over pulled cmds with t >= 0.1 s (all of them, also near the face)")
    say(f"{'condition':20s} {'v0':>7s} {'A':>7s} {'rms':>6s} {'max|res|':>8s} {'n':>5s}")
    R["speed_law"] = {}
    pooled = []
    for cnd in conds:
        tr = [T for T in TR if T["sched"] == cnd]
        xs, ys = [], []
        for T in tr:
            for k in T["K"]:
                if k["t"] >= 0.1:
                    xs.append(k["t"])
                    ys.append(norm(v3(T["cm"][k["i"]], True)))
        a, b, rms = LG.linfit(xs, ys)
        mres = max(abs(y - (a + b * x)) for x, y in zip(xs, ys))
        R["speed_law"][cnd] = {"v0": a, "A": b, "rms": rms, "max_abs_res": mres, "n": len(xs)}
        if not tr[0]["w_held"]:
            pooled += list(zip(xs, ys))
        say(f"{cnd:20s} {a:7.1f} {b:7.1f} {rms:6.2f} {mres:8.2f} {len(xs):5d}")
    a, b, rms = LG.linfit([x for x, _ in pooled], [y for _, y in pooled])
    R["speed_law_pooled_noW"] = {"v0": a, "A": b, "rms": rms, "n": len(pooled)}
    say(f"pooled, all no-input conditions: |v| = {a:.1f} + {b:.1f} t (rms {rms:.2f} u/s, n {len(pooled)}); "
        "release speed = this law at the release time (no terminal speed seen up to 804 u/s)")
    res["envelopes"] = R


# ------------------------------------------------------------------------------------------------- params
def build_params(res):
    out = _build_params_r1(res)
    if "cross" in res:
        out.update(cross_params(res))
    return out


def _build_params_r1(res):
    def P(value, unit, source, s=None, note=""):
        d = {"value": value, "unit": unit, "source": source}
        if s and s.get("n"):
            d["n"] = s["n"]
            d["spread"] = {"sd": round(s["sd"], 5), "min": round(s["min"], 5), "max": round(s["max"], 5)}
        if note:
            d["note"] = note
        return d
    rp = res["rope"]["groups"]
    st = res["steer"]
    de = res["detach"]
    rl = res["release"]
    tl = res["timeline"]["by_condition"]
    out = {"_scope": "Pathfinder grapple, R5Flowstate S21 client / S3 dedi, 120 fps; M4b swing sessions + M4 pathfinder "
                     "sessions; values computed by swing_analysis.py. Anchor = aim-ray hit from origin + 60 (eye assumed)."}
    g = rp.get("m4b_noinput_noturn", {})
    out["pull.horizontal_direction"] = P("toward the aim-ray hit point (world-fixed anchor)", "-",
                                         "horizontal accel azimuth - rope azimuth, M4b side+jump (deg)", g.get("az_err_mean"))
    out["pull.anchor_y_from_accel_lines_minus_aim"] = P(round(g["y_int_minus_aim"]["mean"], 3), "u",
                                                        "intersection of horizontal accel lines with the face",
                                                        g.get("y_int_minus_aim"))
    out["pull.path_lateral_max"] = P(round(g["lateral_max"]["mean"], 3), "u", "max deviation from the start->anchor line",
                                     g.get("lateral_max"))
    out["pull.tangential_speed_after_burst_max"] = P(round(g["vt_max_after_burst"]["mean"], 2), "u/s",
                                                     "relative to the aim-ray anchor (eye 60 assumed)", g.get("vt_max_after_burst"))
    out["pull.anchor_distance_max_increase"] = P(round(g["d_increase_max"]["mean"], 4), "u per cmd",
                                                 "negative = distance strictly decreasing", g.get("d_increase_max"))
    out["pull.speed_ramp"] = P(round(g["speed_ramp"]["mean"], 2), "u/s^2", "d|v|/dt > 150 u from the anchor, M4b side+jump",
                               g.get("speed_ramp"))
    out["steer.view_turn_no_W.heading_change_at_release"] = P(
        round(st["end"]["head"]["turn"]["mean"] - st["end"]["head"]["side"]["mean"], 3), "deg",
        "turn(+turn_jump) minus side(+jump); view turned ~54 deg right", st["end"]["head"]["turn"])
    out["steer.view_turn_no_W.a_lat_turning"] = P(round(st["a_lat_turning"]["mean"], 2), "u/s^2",
                                                  "horizontal accel perpendicular to the rope while turning", st["a_lat_turning"])
    out["steer.view_turn_no_W.a_lat_after"] = P(round(st["a_lat_after_turn"]["mean"], 2), "u/s^2",
                                                "after the turn, 50 < d_h < 250", st["a_lat_after_turn"])
    if "turn_w" in st:
        out["steer.W.a_along_view"] = P(round(st["turn_w"]["a_w"]["mean"], 1), "u/s^2", "turn_w, accel along the flat view forward",
                                        st["turn_w"]["a_w"])
        out["steer.W.speed_ramp"] = P(round(st["turn_w"]["speed_ramp"]["mean"], 1), "u/s^2", "turn_w d|v|/dt",
                                      st["turn_w"]["speed_ramp"])
        out["steer.W.vh_max"] = P(round(st["turn_w"]["vh_max"]["mean"], 1), "u/s", "turn_w: v_h exceeds 483 (M4 cap not general)",
                                  st["turn_w"]["vh_max"])
        out["steer.W.heading_at_contact"] = P(round(st["end"]["head"]["turn_w"]["mean"], 2), "deg",
                                              "turn_w; no W: " + f"{st['end']['head']['turn']['mean']:.2f}", st["end"]["head"]["turn_w"])
    if "m4_fwd" in st:
        out["steer.W.m4_fwd_a_along_view_precap"] = P(round(st["m4_fwd"]["a_w_precap"]["mean"], 1), "u/s^2", "M4 fwd",
                                                      st["m4_fwd"]["a_w_precap"])
        out["steer.W.m4_fwd_vh_cap"] = P(round(st["m4_fwd"]["vh_capped"]["mean"], 3), "u/s", "M4 fwd (= 420*msc)",
                                         st["m4_fwd"]["vh_capped"])
    best = min(de["rules"].items(), key=lambda kv: kv[1]["mispredicted"])
    out["detach.rule"] = P("unidentified", "-", "no single-feature threshold (gap, 3D/2D anchor distance, time-to-face/anchor, "
                           "fraction of rope length, pull time, speed, angle) separates released and pulled cmds over all trials",
                           note=f"best: {best[0]} (T {best[1]['best_T']:.3f}) mispredicts {best[1]['mispredicted']}/{best[1]['n']} trials")
    out["detach.gap_envelope_noW"] = P(round(de["gap_envelope_noW"]["mean"], 2), "u", "origin gap to the face, first released cmd",
                                       de["gap_envelope_noW"])
    out["detach.gap_at_contact_W_turn"] = P(round(de["gap_at_contact_W"]["mean"], 2), "u",
                                            "turn_w: never released, still pulled on the impact cmd", de["gap_at_contact_W"])
    out["release.boost"] = P(0.0, "u/s", "first released cmd is ballistic; velocity continuous",
                             stats([r["ballistic_dev_first"] for r in rl["trials"]]))
    ej = rl["jump"].get("m4b_swing_jump", {})
    if ej:
        out["release.jump_effect"] = P(round(ej["max_dv_vs_ref"]["mean"], 3), "u/s", "max |dv| jump vs side after the press "
                                       f"(baseline side vs side {ej['ref_baseline']['mean']:.3f})", ej["max_dv_vs_ref"],
                                       "jump does not release the grapple during the pull")
    ev = res["envelopes"]["speed_law_pooled_noW"]
    out["envelope.speed_law_noinput"] = P({"v0": round(ev["v0"], 1), "A": round(ev["A"], 1)}, "u/s, u/s^2",
                                          f"|v| = v0 + A t since pull start, pooled no-input pulled cmds (t >= 0.1 s), "
                                          f"rms {ev['rms']:.2f} u/s, n {ev['n']}")
    for k, v in res["envelopes"]["speed_law"].items():
        out[f"envelope.speed_law.{k}"] = P({"v0": round(v["v0"], 1), "A": round(v["A"], 1)}, "u/s, u/s^2",
                                          f"rms {v['rms']:.2f}, max |res| {v['max_abs_res']:.1f} u/s, n {v['n']}")
    out["timeline.m4b_pull_duration_noinput"] = P(round(tl["m4b_swing_side"]["pull_dur"]["mean"], 4), "s", "m4b_swing_side",
                                                  tl["m4b_swing_side"]["pull_dur"])
    return out


# ------------------------------------------------------------------------------------------------- section 8 (round 2)
CROSS_NOINPUT = ("m4b_swing_cross", "m4b_swing_cross_walk")
MODELS = {
    # name: (parameter keys, start values, steps, description)
    "F1": (["A", "s", "H"], {"A": 550.0, "s": 0.1, "H": 50.0}, {"A": 40.0, "s": 0.1, "H": 20.0},
           "pure acceleration toward the anchor: v += dt (A r_hat - s g z)"),
    "RC": (["A", "s", "H"], {"A": 500.0, "s": 0.5, "H": 50.0}, {"A": 40.0, "s": 0.2, "H": 20.0},
           "rope / pendulum: along-rope speed += A dt, perpendicular velocity kept (rotates with the rope), + s g perp"),
    "R1": (["A", "s", "H", "D"], {"A": 500.0, "s": 0.5, "H": 50.0, "D": 2.0}, {"A": 40.0, "s": 0.2, "H": 20.0, "D": 1.0},
           "as RC, perpendicular velocity damped exponentially: v_perp *= (1 - D dt)  (M4 R1)"),
    "RF": (["A", "s", "H", "C"], {"A": 500.0, "s": 0.5, "H": 50.0, "C": 350.0}, {"A": 40.0, "s": 0.2, "H": 20.0, "C": 50.0},
           "as RC, perpendicular speed reduced by a constant C dt (constant tangential deceleration)"),
}


def c_anchor(T, P):
    A = anchor(T)
    return (A[0], A[1] + P.get("dY", 0.0), A[2] + P["H"])


def c_step(model, P, A, pos, v, dt):
    r = [A[k] - pos[k] for k in range(3)]
    L = norm(r)
    u = [x / L for x in r]
    if model == "F1":
        return [v[0] + dt * P["A"] * u[0], v[1] + dt * P["A"] * u[1], v[2] + dt * (P["A"] * u[2] - P["s"] * G)]
    vr = dot(v, u)
    vp = [v[k] - vr * u[k] for k in range(3)]
    g = [0.0, 0.0, -P["s"] * G * dt]
    gr = dot(g, u)
    vp = [vp[k] + g[k] - gr * u[k] for k in range(3)]
    if model == "R1":
        f = max(0.0, 1.0 - P["D"] * dt)
        vp = [x * f for x in vp]
    elif model == "RF":
        m = norm(vp)
        f = max(0.0, m - P["C"] * dt) / m if m > 1e-9 else 0.0
        vp = [x * f for x in vp]
    vr += P["A"] * dt
    return [vr * u[k] + vp[k] for k in range(3)]


def c_segment(T):
    return T["p"] + 2, T["e"]          # pulled cmds; for contact ends the impact cmd itself is excluded


def c_run(model, P, T):
    """Open-loop from the recorded state at the segment start. Returns (rms3d, max3d, rms_h, max_h, min|v| simulated,
    one-step squared-error sum, n)."""
    cm = T["cm"]
    a, b = c_segment(T)
    A = c_anchor(T, P)
    c = cm[a]
    pos = [c["ox"], c["oy"], c["oz"]]
    v = [c["vx"], c["vy"], c["vz"]]
    e2 = eh2 = mx = mh = os2 = 0.0
    vmin = 1e9
    n = 0
    for i in range(a, b):
        c = cm[i]
        dt = dtc(c)
        ov = c_step(model, P, A, [c["ox"], c["oy"], c["oz"]], [c["vx"], c["vy"], c["vz"]], dt)
        pv = v3(c, True)
        os2 += sum((ov[k] - pv[k]) ** 2 for k in range(3))
        nv = c_step(model, P, A, pos, v, dt)
        pos = [pos[k] + 0.5 * (v[k] + nv[k]) * dt for k in range(3)]
        v = nv
        vmin = min(vmin, norm(v))
        po = o3(c, True)
        dd = [pos[k] - po[k] for k in range(3)]
        d3 = norm(dd)
        dh = math.hypot(dd[0], dd[1])
        e2 += d3 * d3
        eh2 += dh * dh
        mx, mh = max(mx, d3), max(mh, dh)
        n += 1
    return (math.sqrt(e2 / n), mx, math.sqrt(eh2 / n), mh, vmin, os2, n)


def c_cost(model, P, trials):
    return math.sqrt(sum(c_run(model, P, T)[0] ** 2 for T in trials) / len(trials))


def c_fit(model, keys, P0, st, trials, iters=200):
    P, st = dict(P0), dict(st)
    best = c_cost(model, P, trials)
    for _ in range(iters):
        imp = False
        for k in keys:
            for sg in (1, -1):
                Q = dict(P)
                Q[k] += sg * st[k]
                if k in ("D", "C", "s") and Q[k] < 0:
                    continue
                cq = c_cost(model, Q, trials)
                if cq < best:
                    best, P, imp = cq, Q, True
        if not imp:
            for k in keys:
                st[k] /= 2
            if max(st[k] / max(1.0, abs(P[k])) for k in keys) < 2e-4:
                break
    return P, best


def c_report(model, P, trials, label):
    per = {}
    tot_os, tot_n = 0.0, 0
    for T in trials:
        r = c_run(model, P, T)
        per.setdefault(T["sched"], []).append(r)
        tot_os += r[5]
        tot_n += r[6]
    out = {"params": P, "one_step_rms": math.sqrt(tot_os / tot_n), "per_condition": {}}
    for k, rr in per.items():
        out["per_condition"][k] = {"ol_rms": math.sqrt(sum(x[0] ** 2 for x in rr) / len(rr)), "ol_max": max(x[1] for x in rr),
                                   "ol_rms_h": math.sqrt(sum(x[2] ** 2 for x in rr) / len(rr)), "ol_max_h": max(x[3] for x in rr),
                                   "vmin_sim": stats([x[4] for x in rr])}
    allr = [x for rr in per.values() for x in rr]
    out["ol_rms"] = math.sqrt(sum(x[0] ** 2 for x in allr) / len(allr))
    out["ol_rms_h"] = math.sqrt(sum(x[2] ** 2 for x in allr) / len(allr))
    say(f"  {label}: " + ", ".join(f"{k}={v:.3f}" for k, v in P.items()) + f"; one-step rms {out['one_step_rms']:.2f} u/s per cmd; "
        f"open-loop rms {out['ol_rms']:.1f} u (horizontal {out['ol_rms_h']:.1f} u)")
    for k, v in out["per_condition"].items():
        say(f"      {k:22s} open-loop 3D rms {v['ol_rms']:6.1f} max {v['ol_max']:6.1f} | horizontal rms {v['ol_rms_h']:6.1f} "
            f"max {v['ol_max_h']:6.1f} | simulated min|v| {v['vmin_sim']['mean']:6.1f}")
    return out


def c_series(T):
    """Per pull cmd: |v|, radial speed, signed horizontal speed across the rope, distance, |r x v|."""
    cm = T["cm"]
    A = anchor(T)
    out = []
    for i in range(T["p"], T["e"]):
        c = cm[i]
        r = [A[0] - c["ox"], A[1] - c["oy"], A[2] - c["oz"]]
        d = norm(r)
        u = [x / d for x in r]
        v = v3(c)
        dh = math.hypot(r[0], r[1])
        out.append({"i": i, "t": tspan(cm, T["p"], i), "v": norm(v), "vr": dot(v, u), "vth": -v[0] * r[1] / dh + v[1] * r[0] / dh,
                    "d": d, "dh": dh,
                    "L": norm([r[1] * v[2] - r[2] * v[1], r[2] * v[0] - r[0] * v[2], r[0] * v[1] - r[1] * v[0]])})
    return out


def section_cross(TR, CR, res):
    say("\n=== 8. Round 2: cross swing (tangential speed at attach) ===")
    say("start (-14100, 6050, 294.92), sprint (cross, cross_w) or walk (cross_walk) along +Y for 1.0 s, jump, release the keys,")
    say("turn the view to ~23 deg (no move keys), tap the grapple; cross_w holds W from the tap. Anchor = aim-ray hit at fire (eye 60).")
    R = {"timeline": {}, "series": {}, "models": {}, "anchor": {}, "transfer": {}, "w": {}}
    conds = []
    for T in CR:
        if T["sched"] not in conds:
            conds.append(T["sched"])
    say("\n8.1 state at fire and attach; end of the pull")
    say(f"{'condition':22s} {'n':>2s} {'|v_h| fire':>10s} {'head fire':>9s} {'yaw':>6s} {'hop vz':>7s} {'d|v_h| hop':>10s} "
        f"{'attach-pred':>11s} {'pull':>6s} {'end':>14s} {'gap':>11s} {'cmds to imp':>11s}")
    for cnd in conds:
        tr = [T for T in CR if T["sched"] == cnd]
        rows = []
        for T in tr:
            cm, f, h, p, e = T["cm"], T["f"], T["h"], T["p"], T["e"]
            hook = (WALL_X - T["o0"][0]) / math.cos(T["yaw0"]) / math.cos(T["pitch_up"])
            rows.append({"vh_fire": math.hypot(cm[f]["vx"], cm[f]["vy"]),
                         "head_fire": math.degrees(math.atan2(cm[f]["vy"], cm[f]["vx"])),
                         "yaw": math.degrees(T["yaw0"]), "hop_vz": cm[h]["vz"],
                         "hop_dvh": math.hypot(cm[h]["vx"], cm[h]["vy"]) - math.hypot(cm[h - 1]["pvx"], cm[h - 1]["pvy"]),
                         "attach_err": tspan(cm, f, h) - (HOOK_T0 + hook / HOOK_SPEED), "pull_dur": tspan(cm, p, e),
                         "end": "contact" if T["contact_end"] else "release", "gap": WALL_X - cm[e]["ox"],
                         "to_imp": (T["imp"] - e) if T["imp"] is not None else None})
        S = {k: stats([r[k] for r in rows]) for k in ("vh_fire", "head_fire", "yaw", "hop_vz", "hop_dvh", "attach_err", "pull_dur",
                                                      "gap", "to_imp")}
        S["end"] = sorted({r["end"] for r in rows})
        R["timeline"][cnd] = S
        ti = S["to_imp"]
        say(f"{cnd:22s} {len(tr):2d} {S['vh_fire']['mean']:10.1f} {S['head_fire']['mean']:9.2f} {S['yaw']['mean']:6.2f} "
            f"{S['hop_vz']['mean']:7.2f} {S['hop_dvh']['mean']:10.3f} {S['attach_err']['mean']:11.4f} {S['pull_dur']['mean']:6.3f} "
            f"{'/'.join(S['end']):>14s} {S['gap']['min']:5.1f}..{S['gap']['max']:4.1f} "
            f"{(str(int(ti['min'])) + '..' + str(int(ti['max']))) if ti.get('n') else 'none':>11s}")
    say("(hop vz = pre-vz of the attach cmd; d|v_h| hop = horizontal speed change at the hop; yaw spread: see results.json)")
    say("\n8.2 radial and tangential speed (mean over trials, t from pull start; v_th = horizontal speed across the rope, "
        "+ = left of the rope)")
    tg = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for cnd in conds:
        tr = [T for T in CR if T["sched"] == cnd]
        for T in tr:
            T["CS"] = c_series(T)
        rows = []
        for t in tg:
            pts = []
            for T in tr:
                k = min(T["CS"], key=lambda x: abs(x["t"] - t))
                if abs(k["t"] - t) < 0.006:
                    pts.append(k)
            if len(pts) == len(tr):
                rows.append({"t": t, **{q: sum(x[q] for x in pts) / len(pts) for q in ("v", "vr", "vth", "d", "L")}})
        R["series"][cnd] = rows
        say(f"[{cnd}]  t: " + " ".join(f"{r['t']:6.1f}" for r in rows))
        for q, lab in (("v", "|v|"), ("vr", "v_r"), ("vth", "v_th"), ("d", "d"), ("L", "|r x v|/100")):
            say(f"   {lab:12s} " + " ".join(f"{(r[q] / 100 if q == 'L' else r[q]):6.1f}" for r in rows))
        vr_s, vt_s, dip = [], [], []
        for T in tr:
            pts = [k for k in T["CS"] if 0.1 <= k["t"] <= 0.6]
            vr_s.append(LG.linfit([k["t"] for k in pts], [k["vr"] for k in pts])[1])
            p2 = [k for k in T["CS"] if 0.05 <= k["t"] <= 0.30]
            vt_s.append(LG.linfit([k["t"] for k in p2], [abs(k["vth"]) for k in p2])[1])
            km = min(T["CS"], key=lambda x: x["v"])
            dip.append((T["CS"][0]["v"], km["v"], km["t"]))
        F = {"vr_ramp": stats(vr_s), "vth_decel_0.05_0.30": stats(vt_s), "v_start": stats([x[0] for x in dip]),
             "v_min": stats([x[1] for x in dip]), "t_v_min": stats([x[2] for x in dip])}
        R["series"][cnd + ".fits"] = F
        say(f"   d v_r/dt (0.1-0.6 s) {fmt(F['vr_ramp'], 1)}; d|v_th|/dt (0.05-0.30 s) {fmt(F['vth_decel_0.05_0.30'], 1)}")
        say(f"   |v| at pull start {F['v_start']['mean']:.1f} -> minimum {F['v_min']['mean']:.1f} at t {F['t_v_min']['mean']:.3f} s")
    fit_tr = [T for T in CR if T["sched"] in CROSS_NOINPUT]
    say(f"\n8.3 model comparison, fitted (open-loop 3D position) on the {len(fit_tr)} no-input cross trials "
        "(cross + cross_walk), pulled cmds from pull start + 2; anchor = aim-ray hit + H up")
    for name, (keys, P0, st, desc) in MODELS.items():
        say(f"  {name}: {desc}")
    obs_vmin = stats([min(k["v"] for k in T["CS"][2:]) for T in fit_tr])
    R["observed_vmin"] = obs_vmin
    say(f"  observed min|v| after pull start + 2: {fmt(obs_vmin, 1)}")
    for name, (keys, P0, st, desc) in MODELS.items():
        P, _ = c_fit(name, keys, P0, st, fit_tr)
        R["models"][name] = c_report(name, P, fit_tr, name)
    best_name = min(R["models"], key=lambda k: R["models"][k]["ol_rms"])
    R["best_model"] = best_name
    say(f"  best open-loop: {best_name}")
    keys, P0, st, _ = MODELS[best_name]
    Pb = dict(R["models"][best_name]["params"])
    Pb["dY"] = 0.0
    stb = {k: st[k] / 4 for k in keys}
    stb["dY"] = 10.0
    Pd, _ = c_fit(best_name, keys + ["dY"], Pb, stb, fit_tr)
    disp = stats([T["cm"][T["h"]]["oy"] - T["cm"][T["f"]]["oy"] for T in fit_tr])
    say("\n8.4 anchor rule with lateral motion: best model with a free lateral anchor shift dY")
    R["anchor"] = {"fit": c_report(best_name, Pd, fit_tr, best_name + " + free dY"), "player_dy_fire_to_attach": disp}
    say(f"  fitted dY = {Pd['dY']:.1f} u; the player moved {disp['mean']:.1f} u along +Y between fire and attach "
        "(an aim ray cast from the attach position would need dY ~ that)")
    r1 = [T for T in TR if not T["w_held"] and T["sched"] not in CROSS_NOINPUT]
    say(f"\n8.5 transfer: cross-fitted parameters on the {len(r1)} round-1 / M4 no-input trials")
    for name in sorted({best_name, "F1"}):
        R["transfer"][name] = c_report(name, R["models"][name]["params"], r1, name + " (cross params)")
    allno = [T for T in TR if not T["w_held"]]
    say(f"\n8.7 one parameter set for all {len(allno)} no-input trials (round 1 + M4 + cross), started from the cross fits")
    R["joint"] = {}
    for name in ("F1", "RF"):
        keys, _, st, _ = MODELS[name]
        P, _ = c_fit(name, keys, R["models"][name]["params"], {k: st[k] / 2 for k in keys}, allno, iters=120)
        R["joint"][name] = c_report(name, P, allno, name + " (joint)")
    wt = [T for T in CR if T["w_held"]]
    if wt:
        aw, asd, az, vwc, vh, late = [], [], [], [], [], []
        for T in wt:
            cm = T["cm"]
            for i in range(T["p"] + 2, T["e"]):
                c = cm[i]
                yw = math.radians(c["yaw"])
                w = (math.cos(yw), math.sin(yw))
                a = acc(c)
                vw_post = c["pvx"] * w[0] + c["pvy"] * w[1]
                vw_pre = c["vx"] * w[0] + c["vy"] * w[1]
                vh.append(math.hypot(c["pvx"], c["pvy"]))
                if WALL_X - c["ox"] < 120:
                    late.append(a[2])
                    continue
                if vw_post < 482.9:
                    aw.append(a[0] * w[0] + a[1] * w[1])
                    asd.append(-a[0] * w[1] + a[1] * w[0])
                    az.append(a[2])
                elif vw_pre >= 482.9:
                    vwc.append(vw_post)
        R["w"] = {"a_w_before_clamp": stats(aw), "a_side_before_clamp": stats(asd), "a_z_before_clamp": stats(az),
                  "v_w_clamped": stats(vwc), "vh_max": max(vh), "a_z_last_120u": stats(late)}
        say("\n8.6 W held from the tap (cross_w), view-frame accelerations (side + = left of the view), > 120 u from the face:")
        say("  before v.w reaches the clamp: a.w", fmt(R["w"]["a_w_before_clamp"], 1), "; a_side",
            fmt(R["w"]["a_side_before_clamp"], 1), "; a_z", fmt(R["w"]["a_z_before_clamp"], 1))
        say("  clamped: v.w", fmt(R["w"]["v_w_clamped"], 3), f"; max v_h {R['w']['vh_max']:.1f}")
        say("  last 120 u before the face: a_z", fmt(R["w"]["a_z_last_120u"], 1))
    res["cross"] = R


def cross_params(res):
    def P(value, unit, source, s=None, note=""):
        d = {"value": value, "unit": unit, "source": source}
        if s and s.get("n"):
            d["n"] = s["n"]
            d["spread"] = {"sd": round(s["sd"], 5), "min": round(s["min"], 5), "max": round(s["max"], 5)}
        if note:
            d["note"] = note
        return d
    R = res["cross"]
    out = {}
    for name, m in R["models"].items():
        out[f"r2.model.{name}"] = P({k: round(v, 4) for k, v in m["params"].items()}, "-",
                                    f"fit on cross+cross_walk; open-loop rms {m['ol_rms']:.2f} u (horizontal {m['ol_rms_h']:.2f}), "
                                    f"one-step {m['one_step_rms']:.2f} u/s",
                                    note="; ".join(f"{k}: {v['ol_rms']:.1f}/{v['ol_max']:.1f} u (h {v['ol_rms_h']:.1f}/{v['ol_max_h']:.1f})"
                                                   for k, v in m["per_condition"].items()))
    out["r2.best_model"] = P(R["best_model"], "-", "lowest open-loop rms on the cross trials")
    out["r2.anchor_dY"] = P(round(R["anchor"]["fit"]["params"]["dY"], 2), "u", "best model with a free lateral anchor shift",
                            note=f"player moved {R['anchor']['player_dy_fire_to_attach']['mean']:.1f} u between fire and attach")
    for name, m in R["transfer"].items():
        out[f"r2.transfer.{name}"] = P(round(m["ol_rms"], 2), "u", "cross-fitted params on round-1/M4 no-input trials, open-loop rms",
                                       note="; ".join(f"{k}: {v['ol_rms']:.1f}" for k, v in m["per_condition"].items()))
    for name, m in R.get("joint", {}).items():
        out[f"r2.joint.{name}"] = P({k: round(v, 4) for k, v in m["params"].items()}, "-",
                                    f"one parameter set, all no-input trials; open-loop rms {m['ol_rms']:.2f} u "
                                    f"(horizontal {m['ol_rms_h']:.2f}), one-step {m['one_step_rms']:.2f} u/s",
                                    note="; ".join(f"{k}: {v['ol_rms']:.1f}/{v['ol_max']:.1f} u (h {v['ol_rms_h']:.1f})"
                                                   for k, v in m["per_condition"].items()))
    for cnd in ("m4b_swing_cross", "m4b_swing_cross_walk", "m4b_swing_cross_w"):
        F = R["series"].get(cnd + ".fits")
        if F:
            out[f"r2.{cnd}.vr_ramp"] = P(round(F["vr_ramp"]["mean"], 1), "u/s^2", "d v_r/dt, 0.1-0.6 s", F["vr_ramp"])
            out[f"r2.{cnd}.speed_dip"] = P({"start": round(F["v_start"]["mean"], 1), "min": round(F["v_min"]["mean"], 1),
                                           "t_min": round(F["t_v_min"]["mean"], 3)}, "u/s, s", "observed |v| dip")
    if R.get("w"):
        out["r2.W.a_along_view"] = P(round(R["w"]["a_w_before_clamp"]["mean"], 1), "u/s^2", "cross_w before the clamp",
                                     R["w"]["a_w_before_clamp"])
        out["r2.W.a_side_view"] = P(round(R["w"]["a_side_before_clamp"]["mean"], 1), "u/s^2", "cross_w before the clamp",
                                    R["w"]["a_side_before_clamp"])
        out["r2.W.v_w_clamp"] = P(round(R["w"]["v_w_clamped"]["mean"], 3), "u/s", "cross_w: v.w held at 420*msc",
                                  R["w"]["v_w_clamped"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--swing", required=True, nargs="+", help="M4b swing session folder(s); the first holds report/census.csv")
    ap.add_argument("--m4", default=[], nargs="*", help="M4 pathfinder session folder(s) for the detach test and envelopes")
    ap.add_argument("--cross", default=[], nargs="*",
                    help="round 2: M4b cross-swing session folder(s) (m4b_swing_cross*); adds section 8 and joins sections 1-7")
    ap.add_argument("--json", default=None)
    ap.add_argument("--params", default=None)
    a = ap.parse_args()
    res = {}
    say("=== M4b grapple swing analysis ===")
    cz = census(a.swing[0])
    if cz:
        say("census (" + os.path.basename(os.path.normpath(a.swing[0])) + "): " + ", ".join(
            f"{k} {cz.get(k)}" for k in ("airSpeed", "airAcceleration", "gravityScale", "jumpHeight", "climbEnabled", "wallrun")))
        res["census"] = cz
    SW = load_trials(a.swing, "m4b")
    M4 = load_trials(a.m4, "m4") if a.m4 else []
    CR = load_trials(a.cross, "m4b") if a.cross else []
    TR = SW + M4 + CR
    section_timeline(TR, res)
    section_rope(TR, res)
    section_steer(TR, res)
    section_detach(TR, res)
    section_release(TR, res)
    section_dedi(TR, res)
    section_envelopes(TR, res)
    if CR:
        section_cross(TR, CR, res)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(build_params(res), fh, indent=1)


if __name__ == "__main__":
    main()
