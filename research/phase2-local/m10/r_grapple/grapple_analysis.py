#!/usr/bin/env python3
"""M10 track R (1) Pathfinder grapple (R5Flowstate local hybrid: S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 grapple_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader: m10_load.py (M6-A2 raw-log loader + the M10 grapple loggers + the class-var census).
Per trial (every scored m10_g_* trial):
  fire     first tactical (offhand1, bit 21) press edge of the client usercmds
  attach   first client [M10-GRC] frame with att=true; pull = first frame with pull=true; anchor = the dedi [M10-GRS] hook
           origin while attached (median), else the client hook at the pull start
  end      first frame after the pull start where the client pull flag is false and stays false for >= 4 frames (the client
           flag flickers for 1-3 frames on some rope geometries while the dedi stays attached); the end usercmd = the first
           usercmd at or after that frame time. Class: 'key' (tactical / crouch edge within the 3 usercmds before), 'contact'
           (|v_h| falls by > 100 u/s on the end usercmd or the next one), else 'auto'
  rope     |anchor - (post-origin + h)| on the last pulled usercmd for h = 0 / 36 / 70 (origin, chest, eye)
Numbers are client first-time MOVE-TRACE usercmds (the dedi is authoritative; M4b showed per-usercmd parity <= 0.24 u/s).
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m10_load  # noqa: E402

IN_JUMP, IN_DUCK, IN_FWD, IN_BACK, IN_LEFT, IN_RIGHT, IN_OFF1 = 0x2, 0x4, 0x8, 0x10, 0x200, 0x400, 0x200000
FLOOR = 294.92
WALL_X = -13706.0
G = 750.0
OUT = []
CV_KEYS = ("grapple_swing", "grapple_swingType", "grapple_accel", "grapple_decel", "grapple_airAccel", "grapple_airSpeedMax",
           "grapple_speedRampMin", "grapple_speedRampMax", "grapple_speedRampTime", "grapple_attachVerticalBoost",
           "grapple_gravityFracMin", "grapple_gravityFracMax", "grapple_detachLengthMin", "grapple_detachLengthMax",
           "grapple_detachAwaySpeed", "grapple_detachSpeedLoss", "grapple_detachSpeedLossMin", "grapple_detachVerticalBoost",
           "grapple_detachVerticalMaxSpeed", "grapple_detachHorizontalMaxSpeed", "grapple_detachLowSpeedThreshold",
           "grapple_detachLowSpeedTime", "grapple_detachLowSpeedWallTime", "grapple_detachLowSpeedGroundTime",
           "grapple_detachOnGrapple", "grapple_detachOnGrappleDebounceTime", "grapple_impactVerticalBoost",
           "grapple_impactVerticalMaxSpeed", "grapple_swingAccel", "grapple_swingMaxSpeed", "grapple_swingMinLength",
           "grapple_swingSticky", "grapple_swingHoldTime", "grapple_lastZiplineCooldown")


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=2):
    return None if x is None else round(x, n)


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def sp(c, post=True):
    return math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2) if post else math.sqrt(c["vx"] ** 2 + c["vy"] ** 2 + c["vz"] ** 2)


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


def press(cs, i, bit):
    return bool(cs[i]["buttons"] & bit) and (i == 0 or not cs[i - 1]["buttons"] & bit)


def first_cmd_at(cs, t):
    for i, c in enumerate(cs):
        if c.get("t") is not None and c["t"] >= t - 1e-6:
            return i
    return None


def median(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def angd(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def seg_dist(anc, o, h=72.0):
    z = min(max(anc[2], o[2]), o[2] + h)
    return math.dist(anc, (o[0], o[1], z))


def view_angle(c, anc, eye=70.0):
    yaw, pitch = c.get("yaw"), c.get("pitch")
    if yaw is None or pitch is None:
        return None
    cp = math.cos(math.radians(pitch))
    f = (cp * math.cos(math.radians(yaw)), cp * math.sin(math.radians(yaw)), -math.sin(math.radians(pitch)))
    d = (anc[0] - c["pox"], anc[1] - c["poy"], anc[2] - c["poz"] - eye)
    n = math.sqrt(sum(x * x for x in d))
    if n < 1e-6:
        return None
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(f[k] * d[k] for k in range(3)) / n))))


def events(T):
    cs, gr = T["cmds"], T["grc"]
    E = {"run": T["run"], "schedule": T["schedule"]}
    i_fire = next((i for i in range(len(cs)) if press(cs, i, IN_OFF1)), None)
    E["i_fire"] = i_fire
    if i_fire is None:
        return E
    t_fire = cs[i_fire]["t"]
    ta = next((g["t"] for g in gr if g["att"] and g["t"] >= t_fire - 1e-6), None)
    tp = next((g["t"] for g in gr if g["pull"] and g["t"] >= t_fire - 1e-6), None)
    E["t_fire"] = t_fire
    E["attach_s"] = r(ta - t_fire, 4) if ta is not None else None
    E["pull_s"] = r(tp - t_fire, 4) if tp is not None else None
    if tp is None:
        E["end"] = "no_pull"
        return E
    # anchor: dedi hook while attached (median per axis), else the client hook at the pull start
    hk = [g["hook"] for g in T["grs"] if g["att"]]
    if hk:
        anc = tuple(median([h[k] for h in hk]) for k in range(3))
        E["anchor_src"] = "dedi"
    else:
        anc = next(g["hook"] for g in gr if g["pull"])
        E["anchor_src"] = "client"
    E["anchor"] = [r(x, 2) for x in anc]
    # end of the pull
    idx = [k for k, g in enumerate(gr) if g["t"] >= tp - 1e-6]
    t_end = None
    for j, k in enumerate(idx):
        if not gr[k]["pull"]:
            run = idx[j:j + 4]
            if len(run) == 4 and all(not gr[q]["pull"] for q in run):
                t_end = gr[k]["t"]
                break
    i_pull = first_cmd_at(cs, tp)
    i_end = first_cmd_at(cs, t_end) if t_end is not None else None
    E["i_pull"], E["i_end"] = i_pull, i_end
    flick = 0
    for j in range(1, len(idx)):
        a, b = gr[idx[j - 1]], gr[idx[j]]
        if t_end is not None and b["t"] >= t_end:
            break
        if a["pull"] and not b["pull"]:
            flick += 1
    E["client_flag_flickers"] = flick
    if i_end is None or i_pull is None:
        E["end"] = "none_in_trial"
        return E
    c_end, c_last = cs[i_end], cs[i_end - 1]
    # dedi end (10 Hz flags: first row with pull false after a pulled row) minus the client end; the client pull flag coming
    # back after the end marks a client-only (predicted) detach that the dedi did not make
    seen, tde = False, None
    for g in T["grs"]:
        if g["pull"]:
            seen = True
        elif seen:
            tde = g["t"]
            break
    E["dedi_end_minus_client_s"] = r(tde - c_end["t"], 2) if tde is not None and c_end.get("t") is not None else None
    E["client_relapse"] = any(g["pull"] for g in gr if g["t"] > t_end + 0.05)
    key = any(press(cs, q, IN_OFF1) or press(cs, q, IN_DUCK) for q in range(max(i_pull, i_end - 3), i_end + 1))
    dvh = max(hs(cs[q], False) - hs(cs[q]) for q in (i_end, min(i_end + 1, len(cs) - 1)))
    E["end"] = "key" if key else ("contact" if dvh > 100 else "auto")
    E["pull_dur_s"] = r(t_end - tp, 4)
    po = (c_last["pox"], c_last["poy"], c_last["poz"])
    for h in (0, 36, 70):
        E["rope_h%d" % h] = r(math.dist(anc, (po[0], po[1], po[2] + h)), 2)
    E["rope0"] = r(math.dist(anc, (cs[i_pull]["ox"], cs[i_pull]["oy"], cs[i_pull]["oz"] + 36)), 1)
    v = (c_last["pvx"], c_last["pvy"], c_last["pvz"])
    rv = [anc[k] - po[k] - (36 if k == 2 else 0) for k in range(3)]
    rn = math.sqrt(sum(x * x for x in rv))
    E["v_end"] = [r(x, 2) for x in v]
    E["speed_end"] = r(sp(c_last), 2)
    E["vh_end"] = r(hs(c_last), 2)
    E["radial_end"] = r(sum(v[k] * rv[k] for k in range(3)) / rn, 2) if rn > 0 else None   # + = toward the anchor (chest)
    E["anchor_dx_end"] = r(anc[0] - po[0], 2)
    yaw = c_last.get("yaw")
    E["view_rope_deg_end"] = r(abs(angd(yaw, math.degrees(math.atan2(rv[1], rv[0])))), 1) if yaw is not None else None
    # distance from the anchor to the player's vertical segment [origin, origin + 72] (pre / post of the last pulled usercmd)
    pre = (c_last["ox"], c_last["oy"], c_last["oz"])
    E["seg_pre_last"] = r(seg_dist(anc, pre), 2)
    E["seg_post_last"] = r(seg_dist(anc, po), 2)
    E["seg_post_end"] = r(seg_dist(anc, (c_end["pox"], c_end["poy"], c_end["poz"])), 2)
    # 3D angle between the view forward (pitch, yaw) and the eye -> anchor direction, on the last pulled and the end usercmd
    for lab, c in (("last", c_last), ("end", c_end)):
        E["view3d_" + lab] = r(view_angle(c, anc), 1)
    E["gap_wall_end"] = r(WALL_X - po[0], 2)
    # first free usercmd after the end: ballistic?
    if i_end + 1 < len(cs):
        c = cs[i_end + 1]
        E["free_dvh"] = r(hs(c) - hs(c, False), 3)
        E["free_dvz_plus_g"] = r(c["pvz"] - c["vz"] + G * dt_of(c), 3)
    E["dv_at_end"] = [r(c_end["pvx"] - c_last["pvx"], 2), r(c_end["pvy"] - c_last["pvy"], 2), r(c_end["pvz"] - c_last["pvz"], 2)]
    seg = cs[i_pull:i_end]
    E["max_speed"] = r(max(sp(c) for c in seg), 1) if seg else None
    E["max_vh"] = r(max(hs(c) for c in seg), 1) if seg else None
    E["v_fire"] = [r(cs[i_fire]["vx"], 1), r(cs[i_fire]["vy"], 1), r(cs[i_fire]["vz"], 1)]
    ia = first_cmd_at(cs, ta) if ta is not None else None
    if ia is not None:
        E["vh_attach_pre"] = r(hs(cs[ia], False), 1)
        E["vz_attach_post"] = r(cs[ia]["pvz"], 1)
    return E


def after_end(T, E, secs=1.5):
    """max v_h, v_h at +0.3 s, ground contact after the end."""
    cs = T["cmds"]
    i = E.get("i_end")
    if i is None:
        return {}
    t0, out = cs[i]["t"], {}
    q = [c for c in cs[i:] if c.get("t") is not None and c["t"] - t0 <= secs]
    out["max_vh_after"] = r(max(hs(c) for c in q), 1) if q else None
    land = next((c for c in q if c["ground"]), None)
    out["land_s"] = r(land["t"] - t0, 3) if land else None
    out["max_z_after"] = r(max(c["poz"] for c in q) - FLOOR, 1) if q else None
    return out


def accel_frame(c):
    dt = dt_of(c)
    return [(c["pvx"] - c["vx"]) / dt, (c["pvy"] - c["vy"]) / dt, (c["pvz"] - c["vz"]) / dt]


def rf_parts(T, E, anc, i0, i1):
    """per usercmd: along-rope speed v_r, horizontal across-rope speed, view-frame accelerations (ŵ = flat view)."""
    cs = T["cmds"]
    rows = []
    for i in range(i0, i1):
        c = cs[i]
        p = (c["ox"], c["oy"], c["oz"] + 36)
        rv = [anc[k] - p[k] for k in range(3)]
        rn = math.sqrt(sum(x * x for x in rv))
        if rn < 60:
            continue
        u = [x / rn for x in rv]
        v = (c["pvx"], c["pvy"], c["pvz"])
        vr = sum(v[k] * u[k] for k in range(3))
        hn = math.hypot(u[0], u[1])
        th = (-u[1] / hn, u[0] / hn) if hn > 1e-6 else (0.0, 0.0)
        vt = v[0] * th[0] + v[1] * th[1]
        a = accel_frame(c)
        yaw = c.get("yaw")
        if yaw is None:
            continue
        w = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
        rt = (w[1], -w[0])                                     # view right
        rows.append({"t": c["t"], "vr": vr, "vt": vt, "a_w": a[0] * w[0] + a[1] * w[1], "a_r": a[0] * rt[0] + a[1] * rt[1],
                     "v_w": v[0] * w[0] + v[1] * w[1], "v_r": v[0] * rt[0] + v[1] * rt[1], "az": a[2], "dist": rn})
    return rows


def slope(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    sessions = [m10_load.load(f) for f in a.sessions]
    say("# M10 R1 grapple analysis")
    rows, byname = [], {}
    for S in sessions:
        sc = [t for t in S["runner"]["trials"] if not t.get("warmup")]
        bad = [t for t in sc if not t.get("ok")]
        say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(bad),
                                                        ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in bad]))
        for T in S["trials"]:
            if not T["schedule"].startswith("m10_g"):
                continue
            E = events(T)
            E.update(after_end(T, E))
            E["session"] = S["folder"]
            T["E"] = E
            rows.append(E)
            byname.setdefault(T["schedule"], []).append(T)
    cv = {}
    for S in sessions:
        cv.update({k: v for k, v in S["classvars"].items() if v is not None or k not in cv})
    say("\n## 0. Class-var census (client bridge_classvar_get, Pathfinder setfile pilot_survival_grapple)")
    for k in CV_KEYS:
        say("  %-40s %s" % (k, cv.get(k, "(not read)")))

    say("\n## 1. Per-trial table")
    say("run    schedule              att_s  pull_s end      dur_s  rope0  rope_h0 rope_h36 rope_h70 seg_pre seg_post speed_end vh_end radial_end view_rope view3d_end max_speed max_vh_after")
    for E in sorted(rows, key=lambda e: e["run"]):
        say("%-6d %-21s %-6s %-6s %-8s %-6s %-6s %-7s %-8s %-8s %-7s %-8s %-9s %-6s %-10s %-9s %-10s %-9s %s" % (
            E["run"], E["schedule"][6:], E.get("attach_s"), E.get("pull_s"), E.get("end"), E.get("pull_dur_s"), E.get("rope0"),
            E.get("rope_h0"), E.get("rope_h36"), E.get("rope_h70"), E.get("seg_pre_last"), E.get("seg_post_last"), E.get("speed_end"),
            E.get("vh_end"), E.get("radial_end"), E.get("view_rope_deg_end"), E.get("view3d_end"), E.get("max_speed"), E.get("max_vh_after")))

    def grp(names, key):
        return stats([T["E"].get(key) for n in names for T in byname.get(n, [])])

    res = {"trials": rows, "groups": {}}
    say("\n## 2. Group summaries (mean (sd, min..max, n))")
    for n in sorted(byname):
        g = {k: grp([n], k) for k in ("attach_s", "pull_dur_s", "speed_end", "vh_end", "max_speed", "max_vh_after", "rope_h36",
                                       "radial_end", "view_rope_deg_end", "max_z_after")}
        ends = sorted(set(T["E"].get("end") for T in byname[n]))
        res["groups"][n] = {k: {kk: r(vv, 3) for kk, vv in s.items()} for k, s in g.items()}
        res["groups"][n]["ends"] = ends
        say("%-22s end=%s speed_end %s | vh_end %s | max_speed %s | max_vh_after %s | rope36 %s | radial %s | view_rope %s" % (
            n[6:], "/".join(str(e) for e in ends), fmt(g["speed_end"]), fmt(g["vh_end"]), fmt(g["max_speed"]),
            fmt(g["max_vh_after"]), fmt(g["rope_h36"]), fmt(g["radial_end"]), fmt(g["view_rope_deg_end"])))

    # ---- 3. Detach rule
    say("\n## 3. Detach rule. Classes of auto ends: 'near' = moving toward the anchor (radial > 0) and within 60 u of it (segment")
    say("   distance, anchor to [origin, origin + 72]); 'view' = moving toward it but far, with the anchor > 90 deg off the view;")
    say("   'passed' = moving away from the anchor (radial <= 0). Key ends: tactical / crouch press on the end usercmd.")
    auto = [E for E in rows if E.get("end") == "auto"]
    say("auto %d; contact %d; key %d; no_pull %d" % (len(auto), sum(1 for E in rows if E.get("end") == "contact"),
                                                    sum(1 for E in rows if E.get("end") == "key"), sum(1 for E in rows if E.get("end") == "no_pull")))
    cls = {"near": [], "view": [], "passed": [], "other": []}
    for E in auto:
        if E.get("radial_end") is not None and E["radial_end"] <= 0:
            cls["passed"].append(E)
        elif E.get("seg_post_last") is not None and E["seg_post_last"] < 60:
            cls["near"].append(E)
        elif E.get("view3d_end") is not None and E["view3d_end"] > 90:
            cls["view"].append(E)
        else:
            cls["other"].append(E)
    res["detach_classes"] = {}
    for k in ("near", "view", "passed", "other"):
        sel = cls[k]
        g = {q: stats([E.get(q) for E in sel]) for q in ("seg_pre_last", "seg_post_last", "seg_post_end", "speed_end", "radial_end",
                                                          "view3d_last", "view3d_end", "view_rope_deg_end")}
        res["detach_classes"][k] = {"n": len(sel), "schedules": sorted(set(E["schedule"][6:] for E in sel)),
                                    **{q: {kk: r(vv, 3) for kk, vv in s2.items()} for q, s2 in g.items()}}
        say("  %-6s n=%d schedules %s" % (k, len(sel), sorted(set(E["schedule"][6:] for E in sel))))
        for q in g:
            if g[q]["n"]:
                say("         %-18s %s" % (q, fmt(g[q], 2)))
    say("  dedi end - client end (s), per class: " + "; ".join("%s %s" % (k, fmt(stats([E.get("dedi_end_minus_client_s") for E in cls[k]]), 2)) for k in cls))
    rel = sorted(set(E["schedule"][6:] for E in rows if E.get("client_relapse")))
    say("  client-only detaches (the client pull flag returns after the end; the dedi kept pulling): %s" % rel)
    res["client_only_detach_schedules"] = rel
    nr = cls["near"]
    if nr:
        say("  near: largest post-distance still pulled %.2f u; smallest pre-distance of the last pulled usercmd %.2f u -> no single"
            % (max(E["seg_post_last"] for E in nr), min(E["seg_pre_last"] for E in nr)))
        say("        threshold separates them when the two overlap (class vars: grapple_detachLengthMin 33 / Max 50)")
        for n in sorted(set(E["schedule"] for E in nr)):
            sel = [E for E in nr if E["schedule"] == n]
            say("        %-14s seg_post_last %s | radial %s | view3d_last %s" % (n[6:], fmt(stats([E["seg_post_last"] for E in sel])),
                                                                         fmt(stats([E["radial_end"] for E in sel])), fmt(stats([E["view3d_last"] for E in sel]))))
    say("  momentum on the first free usercmd (all auto/key ends): d|v_h| %s, dvz + g dt %s" % (
        fmt(stats([E.get("free_dvh") for E in rows if E.get("end") in ("auto", "key")]), 3),
        fmt(stats([E.get("free_dvz_plus_g") for E in rows if E.get("end") in ("auto", "key")]), 3)))

    # ---- 4. RF pull law on the no-input lane-A trials
    say("\n## 4. RF pull law (no-input trials d250/d400/d700/p0/p20, sl_hold, sl8_hold): along-rope ramp and speed law")
    law = {}
    for n in ("m10_g_d250", "m10_g_d400", "m10_g_d700", "m10_g_p0", "m10_g_p20", "m10_g_sl_hold", "m10_g_sl8_hold"):
        ramps, sps = [], []
        for T in byname.get(n, []):
            E = T["E"]
            if E.get("i_pull") is None or E.get("i_end") is None:
                continue
            anc = E["anchor"]
            pr = rf_parts(T, E, anc, E["i_pull"] + 12, E["i_end"] - 2)
            if len(pr) > 5:
                t0 = pr[0]["t"]
                ramps.append(slope([q["t"] - t0 for q in pr], [q["vr"] for q in pr]))
            cs = T["cmds"]
            seg = cs[E["i_pull"] + 12:E["i_end"] - 2]
            if len(seg) > 5:
                sps.append(slope([c["t"] for c in seg], [sp(c) for c in seg]))
        law[n] = {"dvr_dt": stats(ramps), "dspeed_dt": stats(sps)}
        say("  %-16s d v_r/dt %s | d|v|/dt %s" % (n[6:], fmt(law[n]["dvr_dt"]), fmt(law[n]["dspeed_dt"])))
    res["rf_law"] = {k: {kk: {q: r(w, 3) for q, w in vv.items()} for kk, vv in v.items()} for k, v in law.items()}

    # ---- 5. Keys during the pull (A / D / S / W / W+D): view-frame accelerations
    say("\n## 5. Keys held during the pull: mean accel along the flat view (a_w) and view-right (a_r), max v along view / right")
    keyres = {}
    for n in ("m10_g_d400", "m10_g_hold_w", "m10_g_hold_s", "m10_g_hold_d", "m10_g_hold_wd", "m10_g_sl_hold", "m10_g_sl_a",
              "m10_g_sl_d", "m10_g_sl_s", "m10_g_sl8_hold", "m10_g_sl8_w"):
        aw, ar, vw, vrt, vt = [], [], [], [], []
        for T in byname.get(n, []):
            E = T["E"]
            if E.get("i_pull") is None or E.get("i_end") is None:
                continue
            pr = rf_parts(T, E, E["anchor"], E["i_pull"] + 12, E["i_end"] - 2)
            if not pr:
                continue
            aw.append(sum(q["a_w"] for q in pr) / len(pr))
            ar.append(sum(q["a_r"] for q in pr) / len(pr))
            vw.append(max(q["v_w"] for q in pr))
            vrt.append(max(abs(q["v_r"]) for q in pr))
            vt.append(max(abs(q["vt"]) for q in pr))
        keyres[n] = {"a_w": stats(aw), "a_r": stats(ar), "max_v_w": stats(vw), "max_abs_v_right": stats(vrt), "max_abs_vt": stats(vt)}
        say("  %-14s a_w %s | a_r %s | max v_w %s | max |v_right| %s | max |v_t across rope| %s" % (
            n[6:], fmt(keyres[n]["a_w"]), fmt(keyres[n]["a_r"]), fmt(keyres[n]["max_v_w"]), fmt(keyres[n]["max_abs_v_right"]),
            fmt(keyres[n]["max_abs_vt"])))
    res["keys"] = {k: {kk: {q: r(w, 3) for q, w in vv.items()} for kk, vv in v.items()} for k, v in keyres.items()}

    # ---- 6. Entry speed / ground slow
    say("\n## 6. Entry state: v_h at the fire, v_h just before the attach, vz after the attach hop")
    for n in ("m10_g_d400", "m10_g_sprint", "m10_g_slide", "m10_g_air", "m10_g_g400_spr", "m10_g_g400_sl", "m10_g_sl_spr"):
        say("  %-14s vh_fire %s | vh_attach_pre %s | vz_attach_post %s | speed_end %s" % (
            n[6:], fmt(stats([math.hypot(T["E"]["v_fire"][0], T["E"]["v_fire"][1]) for T in byname.get(n, []) if T["E"].get("v_fire")])),
            fmt(grp([n], "vh_attach_pre")), fmt(grp([n], "vz_attach_post")), fmt(grp([n], "speed_end"))))

    # ---- 7. Jump grapple / hop: jump applied? exit speed
    say("\n## 7. Jump grapple (ground hook) and grapple hop: the jump usercmd's vz step, exit and max speeds")
    jres = {}
    for n in sorted(k for k in byname if k.startswith(("m10_g_g", "m10_g_hop", "m10_g_jump_ctrl", "m10_g_ctrl"))):
        steps, apex = [], []
        for T in byname[n]:
            cs = T["cmds"]
            ij = [i for i in range(len(cs)) if press(cs, i, IN_JUMP)]
            if ij:
                c = cs[ij[0]]
                steps.append(c["pvz"] - c["vz"])
            apex.append(max(c["poz"] for c in cs) - FLOOR)
        jres[n] = {"jump_dvz": stats(steps), "apex": stats(apex), "max_vh_after": grp([n], "max_vh_after"),
                   "vh_end": grp([n], "vh_end"), "max_vh": grp([n], "max_vh")}
        say("  %-16s jump dvz %s | apex %s | vh_end %s | max_vh(pull) %s | max_vh_after %s | ends %s" % (
            n[6:], fmt(jres[n]["jump_dvz"]), fmt(jres[n]["apex"]), fmt(jres[n]["vh_end"]), fmt(jres[n]["max_vh"]),
            fmt(jres[n]["max_vh_after"]), "/".join(sorted(set(str(T["E"].get("end")) for T in byname[n])))))
    res["jump"] = {k: {kk: {q: r(w, 3) for q, w in vv.items()} for kk, vv in v.items()} for k, v in jres.items()}

    # ---- 8. Release press (detachSpeedLoss test): speed on the end usercmd vs the usercmd before
    say("\n## 8. Release by a second tactical press: speed before / after the end usercmd")
    for n in ("m10_g_rel_t06", "m10_g_rel_t09", "m10_g_rel_t12", "m10_g_rel_t16", "m10_g_rel_t18", "m10_g_sl_rel", "m10_g_sl_turn_rel", "m10_g_crouch", "m10_g_look180"):
        pre, post, dvv = [], [], []
        for T in byname.get(n, []):
            E = T["E"]
            if E.get("i_end") is None:
                continue
            cs = T["cmds"]
            pre.append(sp(cs[E["i_end"] - 1]))
            post.append(sp(cs[E["i_end"]]))
            dvv.append(E["dv_at_end"][2])
        say("  %-15s end %s | speed before %s | after %s | dvz on the end usercmd %s | view_rope %s" % (
            n[6:], "/".join(sorted(set(str(T["E"].get("end")) for T in byname.get(n, [])))), fmt(stats(pre)), fmt(stats(post)),
            fmt(stats(dvv)), fmt(grp([n], "view_rope_deg_end"))))

    # ---- 9. Overhead anchor (pendulum test), slingshot inputs, rodeo
    say("\n## 9. Overhead anchor / slingshot / rodeo")
    for n in sorted(k for k in byname if k.startswith(("m10_g_over", "m10_g_sl", "m10_g_rodeo", "m10_g_tether"))):
        ov, hd = [], []
        for T in byname[n]:
            E = T["E"]
            if E.get("i_pull") is None or E.get("i_end") is None:
                continue
            cs = T["cmds"]
            seg = cs[E["i_pull"]:E["i_end"]]
            ax = E["anchor"][0]
            ov.append(max(c["pox"] for c in seg) - ax)
            hds = [math.degrees(math.atan2(c["pvy"], c["pvx"])) for c in seg if hs(c) > 30]
            tot = sum(angd(b2, a2) for a2, b2 in zip(hds, hds[1:]))
            hd.append(abs(tot))
        say("  %-16s max x past the anchor %s | |heading change| in the pull %s | max_speed %s | max_vh %s | ends %s" % (
            n[6:], fmt(stats(ov)), fmt(stats(hd)), fmt(grp([n], "max_speed")), fmt(grp([n], "max_vh")),
            "/".join(sorted(set(str(T["E"].get("end")) for T in byname[n])))))
    say("\n## 10. Other probes (super grapple, double bounce, flag flicker)")
    for n in ("m10_g_super_none", "m10_g_super_jump", "m10_g_dbounce"):
        for T in byname.get(n, []):
            E = T["E"]
            say("  r%d %-12s attach_s %s pull_s %s end %s anchor %s speed_end %s" % (E["run"], n[6:], E.get("attach_s"), E.get("pull_s"),
                                                                              E.get("end"), E.get("anchor"), E.get("speed_end")))
    say("  client pull-flag flickers before the end (dedi stays attached): %s" % sorted(
        set((E["schedule"][6:], E.get("client_flag_flickers")) for E in rows if E.get("client_flag_flickers"))))
    res["classvars"] = {k: cv.get(k) for k in CV_KEYS}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Pathfinder grapple, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; grapple_analysis.py"}
        for k in CV_KEYS:
            P["classvar." + k] = {"value": cv.get(k), "evidence": "src (client class-var census)", "n": 1}
        for k, v in res.get("detach_classes", {}).items():
            P["detach." + k] = {"value": {q: v[q] for q in ("seg_post_last", "view3d_end", "radial_end") if q in v}, "evidence": "meas",
                                "n": v["n"], "schedules": v["schedules"]}
        for key, n, field, ev in (("rf.speed_ramp_d700", "m10_g_d700", "max_speed", "meas"), ("slingshot.hold_600", "m10_g_sl_hold", "max_speed", "meas"),
                                  ("slingshot.track_d_g1_600", "m10_g_sl_g1", "max_speed", "meas"), ("slingshot.track_d_g1_800", "m10_g_sl8_g1", "max_speed", "meas"),
                                  ("slingshot.side_key_a", "m10_g_sl_a", "max_speed", "meas"), ("slingshot.side_key_d", "m10_g_sl_d", "max_speed", "meas"),
                                  ("jump_grapple.g700_no_jump", "m10_g_g700", "vh_end", "meas"), ("jump_grapple.g700_j6", "m10_g_g700_j6", "vh_end", "meas"),
                                  ("jump_grapple.g700_j24_no_effect", "m10_g_g700_j24", "vh_end", "meas"), ("release.press_t18_speed_before", "m10_g_rel_t18", "speed_end", "meas"),
                                  ("w_clamp.v_along_view", "m10_g_hold_w", "vh_end", "meas"), ("tether.max_speed", "m10_g_tether", "max_speed", "meas")):
            g = res["groups"].get(n, {}).get(field)
            if g:
                P[key] = {"value": g.get("mean"), "spread": {"sd": g.get("sd"), "min": g.get("min"), "max": g.get("max")}, "unit": "u/s",
                          "evidence": ev, "n": g.get("n"), "schedule": n, "field": field}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
