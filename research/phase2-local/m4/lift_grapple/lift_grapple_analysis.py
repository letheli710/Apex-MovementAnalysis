"""M4: Horizon gravity lift, Pathfinder grapple and Horizon passive -> movement primitives.

usage:
  python lift_grapple_analysis.py --horizon <M4_horizon session> --pathfinder <M4_pathfinder session>
                                  [--ref <session with report/census.csv, e.g. T0_smoke>]
                                  [--json results.json] [--params params.json]

Every number printed here is computed from the session logs (client first-time MOVE-TRACE = physics
truth, dedi MOVE-TRACE for parity, dedi HSD events). Trials: runner.json ok=true and warmup=false.
stdlib only; no local paths (folders come from the command line).
"""
import argparse
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lg_load  # noqa: E402
from lg_load import IN_JUMP, IN_OFFHAND1, G, stats, fmt  # noqa: E402

MSC = 1.15
FLOOR_LIFT = 294.92        # lift deploy z (reset origin z; SpaceElevator_PropDeploy(o + <120,0,0>))
WALL_X = -13706.0          # rock face (normal -X) on lane A
PULL_TOL = 0.05            # u/s per cmd: deviation from ballistic that marks an externally driven cmd
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def post(c):
    return (c["pvx"], c["pvy"], c["pvz"])


def pre(c):
    return (c["vx"], c["vy"], c["vz"])


def norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return ([x / n for x in v] if n > 0 else [0.0] * len(v)), n


def dtc(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def sv_diff(c, s):
    keys = ("pox", "poy", "poz", "pvx", "pvy", "pvz")
    return max(abs(c[k] - s[k]) for k in keys)


def ballistic_dev(c):
    """|post v - ballistic(pre v)| for an airborne cmd with no input-driven accel expected."""
    dt = dtc(c)
    return max(abs(c["pvx"] - c["vx"]), abs(c["pvy"] - c["vy"]), abs(c["pvz"] - (c["vz"] - G * dt)))


# ----------------------------------------------------------------------------------------- census
CV_RE = re.compile(r"\[CLASSVAR\] ([A-Za-z_]+) = (\S+)")


def census_from_logs(folder):
    out = {}
    for f in glob.glob(os.path.join(folder, "platform", "logs", "client", "*", "message*.log")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = CV_RE.search(line)
                if m:
                    out[m.group(1)] = m.group(2)
    return out


def census_from_csv(folder):
    p = os.path.join(folder, "report", "census.csv")
    out = {}
    if not os.path.exists(p):
        return out
    with open(p, encoding="utf-8") as fh:
        hdr = fh.readline().strip().split(",")
        for line in fh:
            f = line.strip().split(",")
            if len(f) >= 2:
                out[f[0]] = f[1]
    return out


def section_census(hz, pf, ref_folder, res):
    say("\n=== 1. Class-var census (client [CLASSVAR]) ===")
    ch = census_from_logs(hz)
    cp = census_from_logs(pf)
    cr = census_from_csv(ref_folder) if ref_folder else {}
    say(f"Horizon keys {len(ch)}, Pathfinder keys {len(cp)}, reference census keys {len(cr)}")
    diffs = {}
    for k in sorted(set(ch) | set(cp) | set(cr)):
        a, b, r = ch.get(k), cp.get(k), cr.get(k)
        if a != b or (cr and a != r):
            diffs[k] = {"horizon": a, "pathfinder": b, "reference": r}
            say(f"  {k:24s} horizon={a}  pathfinder={b}  reference={r}")
    res["census"] = {"n_horizon": len(ch), "n_pathfinder": len(cp), "n_reference": len(cr), "diff": diffs}
    return ch, cp


# ------------------------------------------------------------------------------------ horizon ctl
def section_horizon_controls(H, ch, res):
    say("\n=== 2. Horizon passive: controls (e4_stand, e2_noinput) ===")
    out = {}
    jumpV, gfit, air_dh, land_dv, land_rate = {"e4_stand": [], "e2_noinput": []}, [], [], [], []
    for t in H["trials"]:
        cm = t["cmds"]
        if t["schedule"] not in ("e4_stand", "e2_noinput"):
            continue
        for i0, i1 in lg_load.aj_load.airborne_segments(cm):
            c = cm[i0 - 1]          # the jump command: grounded pre-state (MT ground is the pre-move flag)
            if c["pvz"] < 100:
                continue
            jumpV[t["schedule"]].append(c["pvz"] + 1.5 * G * dtc(c))   # M2: jump command already removes 1.5 g dt
            for j in range(i0 + 1, (i1 or len(cm)) - 1):
                cj = cm[j]
                if cj["buttons"] & 0x618 or cj["fwd"] or cj["sidemove"]:
                    continue
                gfit.append(-(cj["pvz"] - cj["vz"]) / dtc(cj))
                air_dh.append(lg_load.vh(cj) - lg_load.vh(cj, post=False))
            if t["schedule"] == "e2_noinput" and i1:
                v_before = lg_load.vh(cm[i1 - 1])
                v_land = lg_load.vh(cm[i1])
                land_dv.append(v_land - v_before)
                # ground decel after landing (no input), u/s^2, first 5 grounded cmds
                rates = [(lg_load.vh(cm[k], post=False) - lg_load.vh(cm[k])) / dtc(cm[k])
                         for k in range(i1 + 1, min(i1 + 6, len(cm))) if lg_load.vh(cm[k]) > 5]
                land_rate += rates
    out["jump_V"] = stats(jumpV["e2_noinput"])
    out["jump_V_e4_stand"] = stats(jumpV["e4_stand"])
    out["gravity"] = stats(gfit)
    out["air_dvh_per_cmd_noinput"] = stats(air_dh)
    out["landing_cmd_dvh"] = stats(land_dv)
    out["post_landing_decel"] = stats(land_rate)
    say("jump V (pvz + 1.5 g dt), e2_noinput (2 s on the ground first):", fmt(out["jump_V"]), " M2 reference 289.823 (jumpHeight 56)")
    say("jump V, e4_stand (standing jump):", fmt(out["jump_V_e4_stand"]), " M2 reference 289.823")
    say("gravity (no-input air cmds):", fmt(out["gravity"]), " M2 reference 750")
    say("air horizontal change per cmd, no input:", fmt(out["air_dvh_per_cmd_noinput"], 4), " (airFriction/airDrag 0)")
    say("e2_noinput landing cmd horizontal change:", fmt(out["landing_cmd_dvh"]), " (one ground-decel step = -1250*dt = -10.4)")
    say("post-landing decel (no input):", fmt(out["post_landing_decel"], 1), " M2 deceleration 1250")
    res["horizon_controls"] = out


# ------------------------------------------------------------------------------------------- lift
def lift_center(cm):
    """Centre of the bang-bang centring oscillation: no input, |v_h| = 25 and the velocity reverses on
    every command. The centre is the mean of the pre/post origins of those commands -> (xc, yc)."""
    xs, ys = [], []
    for i in range(1, len(cm)):
        c, b = cm[i], cm[i - 1]
        if c["ground"] or c["fwd"] or c["sidemove"] or abs(lg_load.vh(c) - 25.0) > 0.01:
            continue
        if c["pvx"] * c["vx"] + c["pvy"] * c["vy"] < 0:      # reversal
            xs += [c["ox"], c["pox"]]
            ys += [c["oy"], c["poy"]]
    if not xs:
        # the centring step can land exactly on the centre: then v_h = 0 (dist 0 -> no direction) and the
        # body stays there; use those in-lift, no-input commands instead
        for c in cm:
            if c["ground"] == 0 and not c["fwd"] and not c["sidemove"] and lg_load.vh(c) < 1e-3 \
                    and lg_load.vh(c, post=False) < 1e-3 and abs(c["pvz"] - 300) < 0.01:
                xs.append(c["pox"])
                ys.append(c["poy"])
    if not xs:
        return None
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def runner_resets(folder):
    """run -> (server reset time, schedule) in runner order (for the previous-lift age)."""
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        rn = json.load(fh)
    out = []
    for t in rn["trials"]:
        m = re.search(r" t=([\d.]+)", t.get("reset", ""))
        st = re.search(r" t=([\d.]+)", t["sched_lines"][0]) if t.get("sched_lines") else None
        out.append((t["run"], float(m.group(1)) if m else None, float(st.group(1)) if st else None, t["schedule"]))
    return out


def lift_events(cm):
    """entry: first cmd with post vz >= 299 from a grounded pre-state; eject: first cmd after entry whose
    post v_h jumps to >= 350 (eject 400) ; hover start: first in-lift cmd with post vz < 5."""
    ent = next((i for i, c in enumerate(cm) if c["ground"] == 1 and c["pvz"] > 299), None)
    if ent is None:
        return None
    hov = next((i for i in range(ent, len(cm)) if cm[i]["pvz"] < 5), None)
    ej = next((i for i in range(ent, len(cm)) if lg_load.vh(cm[i]) > 350), None)
    if hov is not None and ej is not None and hov > ej:
        hov = None
    land = next((i for i in range(ej or ent, len(cm)) if cm[i]["ground"] == 1), None) if ej else None
    return {"entry": ent, "hover": hov, "eject": ej, "land": land}


def air_accel(v, wish, wishspeed, accel, dt):
    """M2 AirAccelerate: accelspeed = accel*dt, capped by wishspeed - v.wishdir."""
    cur = v[0] * wish[0] + v[1] * wish[1]
    add = wishspeed - cur
    if add <= 0:
        return v
    a = min(accel * dt, add)
    return (v[0] + a * wish[0], v[1] + a * wish[1])


def lift_h_model(vpre, wish, entry, A, hspeed=170.0, air_speed=80.0, air_acc=800.0, dt=1 / 120.0):
    """Horizontal lift steering with input (dedi twin trigger_gravity.cpp:804-872) then engine AirAccelerate."""
    base = (0.0, 0.0) if entry else vpre
    sp = max(math.hypot(*vpre), hspeed)
    cap2 = max(vpre[0] ** 2 + vpre[1] ** 2, sp * sp)
    v = (base[0] + wish[0] * A * dt, base[1] + wish[1] * A * dt)
    n2 = v[0] ** 2 + v[1] ** 2
    if n2 > cap2:
        k = math.sqrt(cap2 / n2)
        v = (v[0] * k, v[1] * k)
    return air_accel(v, wish, air_speed * MSC, air_acc, dt)


def wishdir(c):
    # yaw 0 in every lift trial: forward = +X, moveright = -Y (Source: right = -Y at yaw 0)
    yaw = math.radians(c.get("yaw") or 0.0)
    f, s = c["fwd"], c["sidemove"]
    fx, fy = math.cos(yaw), math.sin(yaw)
    rx, ry = math.sin(yaw), -math.cos(yaw)
    w = (f * fx + s * rx, f * fy + s * ry)
    n = math.hypot(*w)
    return ((w[0] / n, w[1] / n), n) if n > 0 else ((0.0, 0.0), 0.0)


LIFT_KEYS = ("entry_dpre", "entry_dpre_prev", "sv_entry_lag", "vz_rise_noinput", "vz_rise_input",
             "hover_frac", "hover_vz_err", "hover_time", "eject_h", "eject_up", "eject_dir_err",
             "eject_sv_lag", "center_speed_err", "center_x", "center_y", "tocenter_inner_fit",
             "jump_effect", "ramp_resid_2000", "ramp_resid_4000", "strafe_resid_2000",
             "strafe_resid_4000", "post_eject_g", "post_eject_dh", "land_decel", "exit_dpre",
             "exit_dpre_prev", "sv_exit_dpre", "rise_creep", "parity_bad_inlift", "entry_step",
             "prev_lift_age_at_entry")


def section_lift(sessions, res):
    say("\n=== 3. Gravity lift (Horizon tactical, SpaceElevator_PropDeploy 120 u ahead) ===")
    R = {"trials": []}
    groups = {"single": {k: [] for k in LIFT_KEYS}, "overlap": {k: [] for k in LIFT_KEYS}}
    brackets = {}
    ride_ref = None
    hover_by_session = {}
    items = []
    for H, folder in sessions:
        rs = runner_resets(folder)
        items += [(t, rs, H["folder"]) for t in H["trials"]]
    for t, resets, sname in items:
        order = [r[0] for r in resets]
        if not t["schedule"].startswith("m4_lift"):
            continue
        cm = t["cmds"]
        sv = lg_load.sv_by_cmd(t)
        ev = lift_events(cm)
        cen = lift_center(cm)
        if not ev or not cen:
            say(f"r{t['run']}: no lift events found")
            continue
        xc, yc = cen
        # classify: first lifted cmds gain 2000*dt + 800*dt = 23.3 u/s with one lift trigger, 2x2000*dt (+air)
        # with two overlapping lift triggers (the previous reset's lift still alive)
        e0 = ev["entry"]
        steps = [abs(lg_load.vh(cm[i]) - lg_load.vh(cm[i], post=False)) for i in range(e0 + 1, e0 + 3)]
        step = sorted(steps)[len(steps) // 2]
        grp = "single" if step < 28 else "overlap"
        agg = groups[grp]
        agg["entry_step"].append(step)
        k = order.index(t["run"])
        prev = resets[k - 1] if k > 0 else None
        if prev and prev[1] is not None and resets[k][2] is not None:
            t_entry = resets[k][2] + sum(dtc(c) for c in cm[:e0])
            agg["prev_lift_age_at_entry"].append(t_entry - prev[1])
        agg["center_x"].append(xc)
        agg["center_y"].append(yc)
        e = ev["entry"]
        d = lambda c: math.hypot(c["ox"] - xc, c["oy"] - yc)  # noqa: E731
        agg["entry_dpre"].append(d(cm[e]))
        agg["entry_dpre_prev"].append(d(cm[e - 1]))
        # dedi entry
        svl = [sv.get(c["cmd"]) for c in cm]
        se = next((i for i, s in enumerate(svl) if s and s["ground"] == 1 and s["pvz"] > 299), None)
        if se is not None:
            agg["sv_entry_lag"].append(se - e)
        # rise: vz post inside the lift below the hover band
        top = ev["hover"] if ev["hover"] is not None else ev["eject"]
        for i in range(e, top):
            c = cm[i]
            (agg["vz_rise_input"] if (c["fwd"] or c["sidemove"]) else agg["vz_rise_noinput"]).append(c["pvz"])
        # creep above 170 with forward held after the ramp
        fw = [i for i in range(e + 10, top) if cm[i]["fwd"] and lg_load.vh(cm[i]) > 169.9]
        if len(fw) > 2:
            agg["rise_creep"].append((lg_load.vh(cm[fw[-1]]) - lg_load.vh(cm[fw[0]])) / (len(fw) - 1))
        # entry ramp residuals (forward held): A = 2000 vs 4000
        for i in range(e, min(e + 12, top)):
            c = cm[i]
            w, wn = wishdir(c)
            if wn == 0:
                continue
            for A, key in ((2000.0, "ramp_resid_2000"), (4000.0, "ramp_resid_4000")):
                p = lift_h_model((c["vx"], c["vy"]), w, i == e, A, dt=dtc(c))
                agg[key].append(math.hypot(p[0] - c["pvx"], p[1] - c["pvy"]))
        # strafe residuals
        if t["schedule"] == "m4_lift_strafe":
            st = [i for i in range(e + 1, ev["eject"] or len(cm)) if cm[i]["sidemove"]]
            for i in st:
                c = cm[i]
                w, wn = wishdir(c)
                for A, key in ((2000.0, "strafe_resid_2000"), (4000.0, "strafe_resid_4000")):
                    p = lift_h_model((c["vx"], c["vy"]), w, False, A, dt=dtc(c))
                    agg[key].append(math.hypot(p[0] - c["pvx"], p[1] - c["pvy"]))
        # no-input centring speed: graph(dist, 20..70 -> 25..50); evaluate on pre-origin distance
        for i in range(e + 1, top):
            c = cm[i]
            if c["fwd"] or c["sidemove"] or cm[i - 1]["fwd"] or cm[i - 1]["sidemove"]:
                continue
            dist = d(c)
            if dist < 0.5:
                continue
            f = min(max((dist - 20.0) / (70.0 - 20.0), 0.0), 1.0)
            pred = 25.0 + 25.0 * f
            agg["center_speed_err"].append(lg_load.vh(c) - pred)
            if 20.5 < dist < 69 and lg_load.vh(c) > 25.01:
                # implied inner radius r0 from speed = 25 + 25 (d - r0)/(70 - r0)
                q = (lg_load.vh(c) - 25.0) / 25.0
                if q < 0.999:
                    agg["tocenter_inner_fit"].append((dist - 70.0 * q) / (1.0 - q))
        # hover band
        if ev["hover"] is not None:
            h = ev["hover"]
            for i in range(h, ev["eject"] or len(cm)):
                c = cm[i]
                frac = (c["oz"] - FLOOR_LIFT) / 1200.0
                if frac >= 0.9:
                    pred = 0.5 + (-1.0) * min(max((frac - 0.9) / 0.1, 0), 1)
                    agg["hover_vz_err"].append(c["pvz"] - pred)
            agg["hover_frac"].append((cm[h]["oz"] - FLOOR_LIFT) / 1200.0)
            # hover time: sum dt of cmds whose pre vz < 5, up to and including the eject cmd
            ht = sum(dtc(cm[i]) for i in range(h + 1, (ev["eject"] or h) + 1) if cm[i]["vz"] < 5.0)
            agg["hover_time"].append(ht)
            hover_by_session.setdefault(f"{sname} [{grp}]", []).append(ht)
        # eject
        if ev["eject"] is not None:
            j = ev["eject"]
            c = cm[j]
            up = c["pvz"] + 0.5 * G * dtc(c)   # remove the half-step of gravity applied after the eject
            agg["eject_up"].append(up)
            agg["eject_h"].append(lg_load.vh(c))
            # direction: hover/top eject -> flat view (yaw); exit through side -> travel from centre (> 40 u)
            rx, ry = c["ox"] - xc, c["oy"] - yc
            if math.hypot(rx, ry) > 40:
                pd = math.degrees(math.atan2(ry, rx))
            else:
                pd = c.get("yaw") or 0.0
            od = math.degrees(math.atan2(c["pvy"], c["pvx"]))
            agg["eject_dir_err"].append((od - pd + 180) % 360 - 180)
            if math.hypot(rx, ry) > 40:
                agg["exit_dpre"].append(d(c))
                agg["exit_dpre_prev"].append(d(cm[j - 1]))
            sj = next((i for i in range((se or 0) + 1, len(svl)) if svl[i] and math.hypot(svl[i]["pvx"], svl[i]["pvy"]) > 350), None)
            if sj is not None:
                agg["eject_sv_lag"].append(sj - j)
                if math.hypot(rx, ry) > 40:
                    agg["sv_exit_dpre"].append(math.hypot(svl[sj]["ox"] - xc, svl[sj]["oy"] - yc))
            # after the eject: ballistic until landing
            for i in range(j + 1, (ev["land"] or len(cm)) - 1):
                ci = cm[i]
                if ci["ground"] == 1 or cm[i + 1]["ground"] == 1:   # stop before the landing cmd
                    break
                agg["post_eject_g"].append(-(ci["pvz"] - ci["vz"]) / dtc(ci))
                if not (ci["fwd"] or ci["sidemove"]):
                    agg["post_eject_dh"].append(lg_load.vh(ci) - lg_load.vh(ci, post=False))
            if ev["land"]:
                L = ev["land"]
                rates = [(lg_load.vh(cm[k], post=False) - lg_load.vh(cm[k])) / dtc(cm[k])
                         for k in range(L + 1, min(L + 20, len(cm))) if lg_load.vh(cm[k]) > 5 and not cm[k]["fwd"]]
                agg["land_decel"] += rates
        # parity: in-lift cmds with dedi diff > 0.002
        bad = sum(1 for i in range(e, ev["eject"] or len(cm)) if svl[i] and sv_diff(cm[i], svl[i]) > 0.002)
        agg["parity_bad_inlift"].append(bad)
        # jump inside the lift: compare with the ride trial at the same offset from entry
        if t["schedule"] == "m4_lift_ride" and ride_ref is None:
            ride_ref = (cm, e)
        if t["schedule"] == "m4_lift_jumpout" and ride_ref:
            jp = next((i for i in range(e, len(cm)) if lg_load.aj_load.pressed(cm, i, IN_JUMP)), None)
            if jp is not None:
                rc, re_ = ride_ref
                mx = 0.0
                for k in range(jp - e, min(jp - e + 120, len(cm) - e, len(rc) - re_)):
                    a, b = cm[e + k], rc[re_ + k]
                    mx = max(mx, abs(a["pvz"] - b["pvz"]), abs(lg_load.vh(a) - lg_load.vh(b)))
                agg["jump_effect"].append(mx)
        tr = {"session": sname, "run": t["run"], "schedule": t["schedule"], "group": grp, "entry_step": step, "center": [xc, yc], "events": ev,
              "sv_entry": se, "eject_v": list(post(cm[ev["eject"]])) if ev["eject"] is not None else None,
              "eject_cmd_sv_minus_cl": (agg["eject_sv_lag"][-1] if ev["eject"] is not None and agg["eject_sv_lag"] else None),
              "inlift_cmds_dedi_differs": bad}
        R["trials"].append(tr)
        say(f"r{t['run']} {t['schedule']:16s} [{grp:7s} step {step:.2f}] entry cmd {e} (dedi {se}), hover {ev['hover']}, eject {ev['eject']}, "
            f"land {ev['land']}, eject v=({cm[ev['eject']]['pvx']:.2f},{cm[ev['eject']]['pvy']:.2f},{cm[ev['eject']]['pvz']:.2f}) "
            f"centre=({xc:.2f},{yc:.2f}) in-lift cmds dedi!=client: {bad}" if ev["eject"] is not None else f"r{t['run']} no eject")
        for side, lst in (("client", cm), ("dedi", svl)):
            brackets.setdefault(side, []).append(touch_samples(lst, xc, yc, side == "client" and e or se, ev, svl, side))
    R["stats"] = {}
    for gname, agg in groups.items():
        S = {k: stats(v) for k, v in agg.items()}
        R["stats"][gname] = S
        label = "one lift trigger" if gname == "single" else "previous reset's lift still alive -> two triggers"
        say(f"\n-- lift summary: {gname} ({label}) --")
        for k in agg:
            say(f"{k:22s}", fmt(S[k], 4))
    say("\n-- hover-to-eject time per session and group --")
    R["hover_by_session"] = {}
    for k_, v_ in hover_by_session.items():
        R["hover_by_session"][k_] = stats(v_)
        say(f"  {k_:48s}", fmt(stats(v_), 4))
    # touch-radius bracket: lifted iff dist(origin at the start of cmd i - lag) < r
    say("\n-- touch radius bracket (horizontal origin distance, all lift trials; lag = cmds between the "
        "sampled origin and the lifted cmd) --")
    R["touch_bracket"] = {}
    for side in ("client", "dedi"):
        for lag in range(0, 7):
            lo, hi = 0.0, 1e9
            for samp in brackets[side]:
                for (i, d_by_lag, lifted) in samp:
                    if lag not in d_by_lag:
                        continue
                    if lifted:
                        lo = max(lo, d_by_lag[lag])
                    else:
                        hi = min(hi, d_by_lag[lag])
            ok = lo < hi
            R["touch_bracket"][f"{side}_lag{lag}"] = [lo, hi, ok]
            say(f"  {side:6s} lag {lag}: lifted max {lo:.3f}  not-lifted min {hi:.3f}  -> "
                f"{'consistent, r in (%.2f, %.2f]' % (lo, hi) if ok else 'inconsistent'}")
    res["lift"] = R


def touch_samples(lst, xc, yc, e, ev, svl, side):
    """(i, {lag: distance of the pre-origin of cmd i-lag}, lifted) for cmds near entry and exit.
    lifted = the lift force acted on cmd i (vz post >= 299 or hover band), judged on the same stream."""
    out = []
    if e is None:
        return out
    n = len(lst)

    def lifted(i):
        c = lst[i]
        if c is None:
            return None
        if c["ground"] == 1 and c["pvz"] < 299:
            return False
        return c["pvz"] > 299 or (abs(math.hypot(c["pvx"], c["pvy"]) - 25) < 0.02 and c["pvz"] > 0)

    def dist(i):
        c = lst[i] if 0 <= i < n else None
        return math.hypot(c["ox"] - xc, c["oy"] - yc) if c else None
    # exit: first cmd after entry whose post horizontal speed is an eject (> 350) on this stream
    j = next((i for i in range(e + 1, n) if lst[i] and math.hypot(lst[i]["pvx"], lst[i]["pvy"]) > 350), None)
    idx = list(range(max(e - 6, 1), e + 3))
    side_exit = j is not None and dist(j) is not None and dist(j) > 40
    if side_exit:
        idx += list(range(j - 3, j + 1))
    for i in idx:
        if lst[i] is None:
            continue
        if side_exit and i == j:
            lf = False
        elif side_exit and j - 3 <= i < j:
            lf = True
        else:
            lf = lifted(i)
            if lf is None:
                continue
        d = {lag: dist(i - lag) for lag in range(0, 7) if dist(i - lag) is not None}
        out.append((i, d, lf))
    return out


# ---------------------------------------------------------------------------------------- grapple
def grapple_events(cm, t):
    fire = next((i for i in range(len(cm)) if lg_load.aj_load.pressed(cm, i, IN_OFFHAND1)), None)
    if fire is None:
        return None
    # hop: first cmd after fire whose pre-velocity differs from the previous post-velocity (set outside the move)
    hop = next((i for i in range(fire + 1, len(cm))
                if max(abs(cm[i]["vz"] - cm[i - 1]["pvz"]), abs(cm[i]["vx"] - cm[i - 1]["pvx"])) > 20), None)
    if hop is None:
        return None
    # pull: first airborne cmd after the hop that deviates from ballistic (+ air accel when W held)
    def driven(i):
        c = cm[i]
        if c["fwd"] or c["sidemove"]:
            # W held: air accel cannot add speed above 69 u/s (airSpeed 60 * 1.15) along +X
            return abs(c["pvz"] - (c["vz"] - G * dtc(c))) > PULL_TOL
        return ballistic_dev(c) > PULL_TOL
    pull = next((i for i in range(hop + 1, len(cm)) if cm[i]["ground"] == 0 and driven(i)), None)
    if pull is None:
        return None
    # end of pull: first cmd after pull that is ballistic again (pull cmds are contiguous)
    end = next((i for i in range(pull + 1, len(cm)) if not driven(i) or cm[i]["ground"] == 1
                or cm[i]["pvx"] - cm[i]["vx"] < -50), len(cm))
    impact = next((i for i in range(pull, len(cm)) if cm[i]["pvx"] - cm[i]["vx"] < -100), None)
    return {"fire": fire, "hop": hop, "pull": pull, "pull_end": end, "impact": impact}


def m1_pred(c, p):
    """speed ramp + direction steering toward the anchor: v' = (|v|+A dt) * norm(v_hat + k dt r_hat)"""
    dt = dtc(c)
    v = pre(c)
    pos = (c["ox"], c["oy"], c["oz"])
    r, _ = norm((p["xA"] - pos[0], p["yA"] - pos[1], p["zA"] - pos[2]))
    d, sp = norm(v)
    d2, _ = norm([d[k] + p["k"] * dt * r[k] for k in range(3)])
    return [(sp + p["A"] * dt) * d2[k] for k in range(3)]


def m2_pred(c, p):
    """central pull toward the anchor with scaled gravity: v' = v + dt (A r_hat - k g z)"""
    dt = dtc(c)
    v = pre(c)
    pos = (c["ox"], c["oy"], c["oz"])
    r, _ = norm((p["xA"] - pos[0], p["yA"] - pos[1], p["zA"] - pos[2]))
    return [v[k] + dt * p["A"] * r[k] - (dt * G * p["k"] if k == 2 else 0.0) for k in range(3)]


def fit(model, data, p0, keys, steps):
    def cost(p):
        e = 0.0
        for c in data:
            q = model(c, p)
            e += sum((q[k] - post(c)[k]) ** 2 for k in range(3))
        return math.sqrt(e / len(data))
    p = dict(p0)
    st = dict(steps)
    best = cost(p)
    for _ in range(2000):
        imp = False
        for kk in keys:
            for sg in (1, -1):
                q = dict(p)
                q[kk] += sg * st[kk]
                cq = cost(q)
                if cq < best:
                    best, p, imp = cq, q, True
        if not imp:
            for kk in keys:
                st[kk] /= 2
            if max(st[kk] for kk in keys) < 1e-4:
                break
    return p, best


def openloop(model, prm, cm, a, b):
    """Simulate from the observed state at cmd a with recorded dt; return (max position error, end |dv|)."""
    st = dict(cm[a])
    pos = [st["ox"], st["oy"], st["oz"]]
    vel = [st["vx"], st["vy"], st["vz"]]
    mx = 0.0
    for i in range(a, b):
        c = dict(cm[i])
        c["ox"], c["oy"], c["oz"] = pos
        c["vx"], c["vy"], c["vz"] = vel
        nv = model(c, prm)
        dt = dtc(cm[i])
        pos = [pos[k] + 0.5 * (vel[k] + nv[k]) * dt for k in range(3)]
        vel = nv
        mx = max(mx, math.sqrt(sum((pos[k] - (cm[i]["pox"], cm[i]["poy"], cm[i]["poz"])[k]) ** 2 for k in range(3))))
    endv = math.sqrt(sum((vel[k] - post(cm[b - 1])[k]) ** 2 for k in range(3)))
    return mx, endv


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    return a, b, math.sqrt(sum(r * r for r in res) / n)


def section_grapple(P, res):
    say("\n=== 4. Grapple (Pathfinder tactical, aim yaw 0 pitch -10 at the lane-A wall, face x = -13706) ===")
    R = {"trials": []}
    agg = {k: [] for k in ("t_fire_hop", "t_fire_pull", "t_hop_pull", "hop_vz", "init_accel", "init_accel_cmds",
                           "ramp_A", "ramp_rms", "v_end", "t_pull", "detach_gap", "detach_speed",
                           "impact_vx_after", "impact_vz_after", "cap_W_vh", "ramp_A_W",
                           "m1_A", "m1_k", "m1_zA", "m1_rms", "m2_A", "m2_k", "m2_zA", "m2_rms",
                           "jump_effect", "hold_vs_hold", "sv_max_dv_pull", "sv_rms_dv_pull", "client_corrections_pull",
                           "elev_v_start", "elev_v_end", "pitch", "detach_gap_W", "detach_speed_W",
                           "detach_time_to_face", "detach_time_to_face_W", "apex_z_after_impact", "t_pull_W",
                           "ramp_A_W_precap", "m1_openloop_maxpos", "m2_openloop_maxpos", "m1_openloop_endv",
                           "m2_openloop_endv")}
    hold_ref = None
    for t in P["trials"]:
        cm = t["cmds"]
        sv = lg_load.sv_by_cmd(t)
        ev = grapple_events(cm, t)
        if not ev:
            say(f"r{t['run']}: no grapple events")
            continue
        f, h, p, e = ev["fire"], ev["hop"], ev["pull"], ev["pull_end"]
        agg["pitch"].append(cm[f].get("pitch"))
        tsum = lambda a, b: sum(dtc(cm[i]) for i in range(a, b))  # noqa: E731
        agg["t_fire_hop"].append(tsum(f, h))
        agg["t_fire_pull"].append(tsum(f, p))
        agg["t_hop_pull"].append(tsum(h, p))
        agg["hop_vz"].append(cm[h]["vz"])
        # initial accel burst: cmds from p while |dv/dt| (gravity removed) > 1200
        k = p
        burst = []
        while k < e:
            c = cm[k]
            dt = dtc(c)
            a = math.sqrt(((c["pvx"] - c["vx"]) / dt) ** 2 + ((c["pvy"] - c["vy"]) / dt) ** 2
                          + ((c["pvz"] - c["vz"]) / dt + G) ** 2)
            if a < 1200:
                break
            burst.append(a)
            k += 1
        held = any(cm[i]["fwd"] for i in range(p, e))
        if not held:
            agg["init_accel"] += burst
            agg["init_accel_cmds"].append(len(burst))
        # speed ramp |v| vs time over the steady pull (skip 12 cmds, stop 2 before the end)
        ts, vs = [], []
        tacc = 0.0
        for i in range(p + 12, e - 2):
            tacc += dtc(cm[i])
            ts.append(tacc)
            vs.append(math.sqrt(sum(x * x for x in post(cm[i]))))
        if len(ts) > 5:
            a, b, rms = linfit(ts, vs)
            agg["ramp_A_W" if held else "ramp_A"].append(b)
            if not held:
                agg["ramp_rms"].append(rms)
        agg["v_end"].append(math.sqrt(sum(x * x for x in post(cm[e - 1]))))
        agg["t_pull_W" if held else "t_pull"].append(tsum(p, e))
        agg["elev_v_start"].append(math.degrees(math.atan2(cm[p + 12]["pvz"], lg_load.vh(cm[p + 12]))))
        agg["elev_v_end"].append(math.degrees(math.atan2(cm[e - 1]["pvz"], lg_load.vh(cm[e - 1]))))
        if held:
            vh = [lg_load.vh(cm[i]) for i in range(p, e)]
            agg["cap_W_vh"].append(max(vh))
            capi = next(i for i in range(p, e) if lg_load.vh(cm[i]) > 482.9)
            ts2, vs2, tacc = [], [], 0.0
            for i in range(p + 3, capi):
                tacc += dtc(cm[i])
                ts2.append(tacc)
                vs2.append(math.sqrt(sum(x * x for x in post(cm[i]))))
            if len(ts2) > 5:
                agg["ramp_A_W_precap"].append(linfit(ts2, vs2)[1])
        gap = WALL_X - cm[e]["ox"]
        dsp = math.sqrt(sum(x * x for x in pre(cm[e])))
        agg["detach_gap_W" if held else "detach_gap"].append(gap)
        agg["detach_speed_W" if held else "detach_speed"].append(dsp)
        # time for the hull face (origin + 16) to reach the wall at the detach velocity
        if cm[e]["vx"] > 1:
            agg["detach_time_to_face_W" if held else "detach_time_to_face"].append((gap - 16.0) / cm[e]["vx"])
        if ev["impact"] is not None:
            agg["impact_vx_after"].append(cm[ev["impact"]]["pvx"])
            agg["impact_vz_after"].append(cm[ev["impact"]]["pvz"])
            if not held:
                agg["apex_z_after_impact"].append(max(cm[i]["poz"] for i in range(ev["impact"], min(ev["impact"] + 120, len(cm)))))
        # models on the steady pull of hold/jump trials (no input)
        if not held:
            data = [cm[i] for i in range(p + 14, e - 4)]
            p1, r1 = fit(m1_pred, data, {"A": 500, "k": 1.0, "zA": 450, "xA": WALL_X, "yA": 6500},
                         ["A", "k", "zA"], {"A": 50, "k": 0.5, "zA": 40})
            p2, r2 = fit(m2_pred, data, {"A": 1000, "k": 1.0, "zA": 600, "xA": WALL_X, "yA": 6500},
                         ["A", "k", "zA"], {"A": 50, "k": 0.5, "zA": 40})
            for name, model, pp in (("m1", m1_pred, p1), ("m2", m2_pred, p2)):
                mp, mv = openloop(model, pp, cm, p + 14, e - 4)
                agg[name + "_openloop_maxpos"].append(mp)
                agg[name + "_openloop_endv"].append(mv)
            for kk, v in (("m1_A", p1["A"]), ("m1_k", p1["k"]), ("m1_zA", p1["zA"]), ("m1_rms", r1),
                          ("m2_A", p2["A"]), ("m2_k", p2["k"]), ("m2_zA", p2["zA"]), ("m2_rms", r2)):
                agg[kk].append(v)
        # parity during the pull (no SDK bridge for the grapple)
        dvs = []
        corr = 0
        for i in range(p, e):
            s = sv.get(cm[i]["cmd"])
            if s:
                dvs.append(max(abs(cm[i][kk] - s[kk]) for kk in ("pvx", "pvy", "pvz")))
            if i > p and max(abs(cm[i][kk] - cm[i - 1]["p" + kk]) for kk in ("vx", "vy", "vz")) > 0.002:
                corr += 1
        if dvs:
            agg["sv_max_dv_pull"].append(max(dvs))
            agg["sv_rms_dv_pull"].append(math.sqrt(sum(x * x for x in dvs) / len(dvs)))
        agg["client_corrections_pull"].append(corr)
        # jump during the pull vs the first hold trial, aligned at the pull start
        if t["schedule"] == "m4_grapple_hold" and hold_ref is None:
            hold_ref = (cm, p)
        elif t["schedule"] == "m4_grapple_hold" and hold_ref:
            # trial-to-trial baseline over the same window the jump comparison uses (from pull + 25 cmds)
            rc, rp = hold_ref
            mx = 0.0
            for kk in range(25, min(e - p, len(rc) - rp)):
                a, b = cm[p + kk], rc[rp + kk]
                mx = max(mx, max(abs(post(a)[q] - post(b)[q]) for q in range(3)))
            agg["hold_vs_hold"].append(mx)
        if t["schedule"] == "m4_grapple_jump" and hold_ref:
            jp = next((i for i in range(f + 1, len(cm)) if lg_load.aj_load.pressed(cm, i, IN_JUMP)), None)
            if jp is not None:
                rc, rp = hold_ref
                mx = 0.0
                for kk in range(jp - p, min(e - p, len(rc) - rp)):
                    a, b = cm[p + kk], rc[rp + kk]
                    mx = max(mx, max(abs(post(a)[q] - post(b)[q]) for q in range(3)))
                agg["jump_effect"].append(mx)
                ev["jump"] = jp
        R["trials"].append({"run": t["run"], "schedule": t["schedule"], "events": ev, "W_held": held})
        say(f"r{t['run']} {t['schedule']:15s} fire {f} hop {h} (vz {cm[h]['vz']:.1f}) pull {p}..{e} "
            f"impact {ev['impact']} v_end {agg['v_end'][-1]:.1f} burst {len(burst)} cmds "
            f"dedi max|dv| in pull {max(dvs) if dvs else float('nan'):.3f} corrections {corr}")
    S = {k: stats(v) for k, v in agg.items()}
    R["stats"] = S
    say("\n-- grapple summary --")
    for k in agg:
        say(f"{k:24s}", fmt(S[k], 4))
    res["grapple"] = R


# ------------------------------------------------------------------ grapple: distance / pitch series
SERIES = ("m4_grapple_hold", "m4_grapple_near", "m4_grapple_far", "m4_grapple_p0", "m4_grapple_p20")
HOOK_EYE = None   # the hook path length is taken horizontally from the player x at fire / cos(pitch)


def g_anchor(tr, H):
    return (WALL_X, tr["y"], tr["z0"] + H + tr["rise"])


def g_step(model, P, tr, pos, v, dt):
    """F1: constant pull A toward the target (view-ray hit on the face + H above the origin height at fire)
    plus gravity scaled by s.  R1: the velocity component along the rope gains A*dt, the perpendicular
    component takes s*g and is damped at rate D."""
    an = g_anchor(tr, P["H"])
    r = [an[k] - pos[k] for k in range(3)]
    L = math.sqrt(sum(x * x for x in r))
    u = [x / L for x in r]
    if model == "F1":
        a = [P["A"] * u[k] for k in range(3)]
        a[2] -= P["s"] * G
        return [v[k] + a[k] * dt for k in range(3)]
    vr = sum(v[k] * u[k] for k in range(3))
    vp = [v[k] - vr * u[k] for k in range(3)]
    g = [0.0, 0.0, -P["s"] * G * dt]
    gr = sum(g[k] * u[k] for k in range(3))
    gp = [g[k] - gr * u[k] for k in range(3)]
    damp = max(0.0, 1 - P["D"] * dt)
    return [(vr + P["A"] * dt) * u[k] + (vp[k] + gp[k]) * damp for k in range(3)]


def g_cost(model, P, trials, mode="ol", per=False):
    out = {}
    tot = 0.0
    for tr in trials:
        cm = tr["cm"]
        c = cm[tr["a"]]
        pos = [c["ox"], c["oy"], c["oz"]]
        v = [c["vx"], c["vy"], c["vz"]]
        e2, n, mx = 0.0, 0, 0.0
        for i in range(tr["a"], tr["b"]):
            c = cm[i]
            dt = dtc(c)
            if mode == "1s":
                nv = g_step(model, P, tr, [c["ox"], c["oy"], c["oz"]], [c["vx"], c["vy"], c["vz"]], dt)
                e2 += sum((nv[k] - post(c)[k]) ** 2 for k in range(3))
            else:
                nv = g_step(model, P, tr, pos, v, dt)
                pos = [pos[k] + 0.5 * (v[k] + nv[k]) * dt for k in range(3)]
                v = nv
                dd = math.sqrt(sum((pos[k] - (c["pox"], c["poy"], c["poz"])[k]) ** 2 for k in range(3)))
                e2 += dd * dd
                mx = max(mx, dd)
            n += 1
        out.setdefault(tr["sched"], []).append((math.sqrt(e2 / n), mx))
        tot += e2 / n
    return out if per else math.sqrt(tot / len(trials))


def g_fit(model, P, keys, st, trials):
    best = g_cost(model, P, trials)
    st = dict(st)
    for _ in range(300):
        imp = False
        for k in keys:
            for sg in (1, -1):
                Q = dict(P)
                Q[k] += sg * st[k]
                c = g_cost(model, Q, trials)
                if c < best:
                    best, P, imp = c, Q, True
        if not imp:
            for k in keys:
                st[k] /= 2
            if max(st[k] for k in keys) < 1e-3:
                break
    return P, best


def section_grapple_series(PS, res):
    say("\n=== 5. Grapple distance / pitch series (no input; face x = -13706) ===")
    R = {"trials": [], "by_condition": {}}
    rows = []
    mtrials = []
    for Pf in PS:
        for t in Pf["trials"]:
            if t["schedule"] not in SERIES:
                continue
            cm = t["cmds"]
            ev = grapple_events(cm, t)
            if not ev:
                continue
            f, h, p, e = ev["fire"], ev["hop"], ev["pull"], ev["pull_end"]
            c0 = cm[f]
            pitch_up = -(c0.get("pitch") or 0.0)
            dface = WALL_X - c0["ox"]
            Lh = dface / math.cos(math.radians(pitch_up))
            rise = dface * math.tan(math.radians(pitch_up))
            ts = lambda a_, b_: sum(dtc(cm[i]) for i in range(a_, b_))  # noqa: E731
            tv, vv, tacc = [], [], 0.0
            for i in range(p + 12, e - 2):
                tacc += dtc(cm[i])
                # only cmds farther than 150 u from the face (the end phase is not a constant ramp)
                if WALL_X - cm[i]["ox"] > 150:
                    tv.append(tacc)
                    vv.append(math.sqrt(sum(x * x for x in post(cm[i]))))
            ramp = linfit(tv, vv)[1] if len(tv) > 5 else None
            # tangential accel along the velocity, gravity part split by direction of motion
            at_up, at_dn = [], []
            for i in range(p + 12, e - 1):
                c = cm[i]
                if WALL_X - c["ox"] < 150:
                    continue
                dt = dtc(c)
                v = pre(c)
                sp = math.sqrt(sum(x * x for x in v))
                vh_ = [x / sp for x in v]
                at = sum(((post(c)[k] - v[k]) / dt) * vh_[k] for k in range(3))
                gt = -G * vh_[2]
                (at_up if gt <= 0 else at_dn).append(at if gt <= 0 else at - gt)
            row = {"run": t["run"], "sched": t["schedule"], "dface": dface, "pitch_up": pitch_up, "hook_len": Lh,
                   "t_hop": ts(f, h), "t_pull": ts(f, p), "t_pull_dur": ts(p, e), "v_end": math.sqrt(sum(x * x for x in pre(cm[e]))),
                   "gap": WALL_X - cm[e]["ox"], "gap_prev": WALL_X - cm[e - 1]["ox"], "v_prev": math.sqrt(sum(x * x for x in pre(cm[e - 1]))),
                   "vx_e": cm[e]["vx"], "vx_prev": cm[e - 1]["vx"], "z_end": cm[e]["oz"], "ramp": ramp,
                   "at_up": stats(at_up), "at_dn": stats(at_dn), "rise": rise}
            # per-trial free target (F1 = earlier M2) for the target-vs-view-hit test
            data = [cm[i] for i in range(p + 14, e - 4)]
            p2, r2 = fit(m2_pred, data, {"A": 1000, "k": 1.0, "zA": 450, "xA": WALL_X, "yA": c0["oy"]},
                         ["A", "k", "zA"], {"A": 50, "k": 0.5, "zA": 40})
            row.update({"f1_A": p2["A"], "f1_s": p2["k"], "f1_zA": p2["zA"], "f1_rms": r2,
                        "f1_H_implied": p2["zA"] - c0["oz"] - rise})
            rows.append(row)
            mtrials.append({"sched": t["schedule"], "cm": cm, "a": p + 12, "b": e - 1, "z0": c0["oz"], "rise": rise, "y": c0["oy"]})
    R["trials"] = rows
    # per condition table
    conds = [c for c in SERIES if any(r["sched"] == c for r in rows)]
    say(f"{'condition':16s} {'d_face':>6s} {'pitch':>5s} {'hook':>6s} {'t_hop':>7s} {'t_pull':>7s} {'pull_dur':>8s} "
        f"{'v_end':>6s} {'gap':>5s} {'ramp':>6s} {'F1 A':>6s} {'F1 s':>6s} {'F1 H':>6s} {'F1 rms':>6s}")
    for cnd in conds:
        rr = [r for r in rows if r["sched"] == cnd]
        S = {k: stats([r[k] for r in rr]) for k in ("dface", "pitch_up", "hook_len", "t_hop", "t_pull", "t_pull_dur", "v_end",
                                                      "gap", "ramp", "f1_A", "f1_s", "f1_H_implied", "f1_rms", "z_end")}
        S["at_up"] = stats([x for r in rr for x in ([r["at_up"]["mean"]] if r["at_up"].get("n") else [])])
        S["at_dn"] = stats([x for r in rr for x in ([r["at_dn"]["mean"]] if r["at_dn"].get("n") else [])])
        R["by_condition"][cnd] = S
        say(f"{cnd:16s} {S['dface']['mean']:6.0f} {S['pitch_up']['mean']:5.1f} {S['hook_len']['mean']:6.1f} "
            f"{S['t_hop']['mean']:7.4f} {S['t_pull']['mean']:7.4f} {S['t_pull_dur']['mean']:8.4f} {S['v_end']['mean']:6.1f} "
            f"{S['gap']['mean']:5.1f} {S['ramp']['mean']:6.1f} {S['f1_A']['mean']:6.1f} {S['f1_s']['mean']:6.3f} "
            f"{S['f1_H_implied']['mean']:6.1f} {S['f1_rms']['mean']:6.3f}   (n={S['dface']['n']})")
    # hook flight: t_hop = t0 + hook_len / speed
    if len({round(r["hook_len"]) for r in rows}) > 1:
        a0, b0, rms0 = linfit([r["hook_len"] for r in rows], [r["t_hop"] for r in rows])
        R["hook"] = {"t0": a0, "s_per_u": b0, "speed": 1.0 / b0 if b0 else None, "rms": rms0, "n": len(rows)}
        say(f"\nhook flight: t_hop = {a0:.4f} + hook_len / {1.0 / b0:.1f} u/s (rms {rms0:.4f} s, n={len(rows)}); "
            f"hook_len = horizontal distance to the face / cos(pitch)")
    else:
        R["hook"] = None
        say("\nhook flight: one hook length only -> flight time and wind-up cannot be separated")
    wind = stats([r["t_pull"] - r["t_hop"] for r in rows])
    R["windup"] = wind
    say("attach (hop) -> pull start:", fmt(wind, 4), "s")
    # terminal speed: v_end vs pull duration
    a1, b1, rms1 = linfit([r["t_pull_dur"] for r in rows], [r["v_end"] for r in rows])
    R["v_end_vs_duration"] = {"v0": a1, "slope": b1, "rms": rms1}
    say(f"speed at detach vs pull duration: v_end = {a1:.1f} + {b1:.1f} * t_pull (rms {rms1:.1f} u/s); max v_end "
        f"{max(r['v_end'] for r in rows):.1f} (no plateau)")
    say("tangential accel (> 150 u from the face), moving up:", fmt(stats([r["at_up"]["mean"] for r in rows if r["at_up"].get("n")]), 2),
        "; moving down, minus the gravity component:", fmt(stats([r["at_dn"]["mean"] for r in rows if r["at_dn"].get("n")]), 2))
    # detach rule: static gap threshold T on the pre-origin, or a time-to-contact tau
    lo = max(r["gap"] for r in rows)
    hi = min(r["gap_prev"] for r in rows)
    say(f"detach, static threshold on the gap to the face: detached max {lo:.2f}, still pulling min {hi:.2f} -> "
        f"{'consistent' if lo < hi else 'inconsistent'}")
    best_tau = None
    for k_ in range(0, 101):
        tau = k_ * 0.001
        lo_t = max(r["gap"] - 16 - r["vx_e"] * tau for r in rows)
        hi_t = min(r["gap_prev"] - 16 - r["vx_prev"] * tau for r in rows)
        if lo_t < hi_t and (best_tau is None or hi_t - lo_t > best_tau[2] - best_tau[1]):
            best_tau = (tau, lo_t, hi_t)
    R["detach_static"] = [lo, hi, lo < hi]
    R["detach_tau"] = best_tau
    if best_tau:
        say(f"detach with look-ahead: gap - 16 - vx*tau < T, widest consistent tau = {best_tau[0]:.3f} s, "
            f"T in ({best_tau[1]:.2f}, {best_tau[2]:.2f}]")
    else:
        say("detach with look-ahead gap - 16 - vx*tau: no tau in 0..0.1 s is consistent")
    R["gap_all"] = stats([r["gap"] for r in rows])
    say("detach gap to the face, all no-input trials:", fmt(R["gap_all"], 2))
    # global models (round 3: all distances and pitches with one parameter set)
    say("\nglobal pull models (one parameter set for all conditions; target = view-ray hit on the face + H):")
    R["global_models"] = {}
    for model, P0, keys, st in (("F1", {"A": 550, "s": 0.15, "H": 50}, ["A", "s", "H"], {"A": 40, "s": 0.05, "H": 30}),
                                ("R1", {"A": 500, "s": 0.4, "H": 60, "D": 10.0}, ["A", "s", "H", "D"],
                                 {"A": 40, "s": 0.2, "H": 20, "D": 2.0})):
        Pm, best = g_fit(model, P0, keys, st, mtrials)
        per = g_cost(model, Pm, mtrials, "ol", True)
        one = g_cost(model, Pm, mtrials, "1s")
        perc = {k: {"ol_rms": sum(x[0] for x in v) / len(v), "ol_max": max(x[1] for x in v)} for k, v in per.items()}
        R["global_models"][model] = {"params": Pm, "ol_rms": best, "one_step_rms": one, "per_condition": perc}
        say(f"  {model} {', '.join(f'{k}={v:.3f}' for k, v in Pm.items())}: open-loop rms {best:.2f} u, one-step {one:.3f} u/s per cmd")
        for k, v in perc.items():
            say(f"      {k:16s} open-loop rms {v['ol_rms']:5.1f} u, max {v['ol_max']:5.1f} u")
    res["grapple_series"] = R


def series_params(res, P, m, sp):
    S = res.get("grapple_series")
    if not S:
        return {}
    out = {}
    hk = S["hook"]
    if hk:
        out["hook_speed"] = P(round(hk["speed"], 1), "u/s", "fit t_hop = t0 + hook_len/speed over all distance/pitch trials; hook_len = horizontal face distance / cos(pitch)", None, f"n = {hk['n']}, t0 = {hk['t0']:.4f} s, rms {hk['rms']:.4f} s")
    out["attach_to_pull_windup"] = P(m(S["windup"]), "s", "data: hop (attach) -> pull start, all conditions", S["windup"])
    for cnd, C in S["by_condition"].items():
        key = cnd.replace("m4_grapple_", "")
        out[f"{key}_t_hop"] = P(m(C["t_hop"]), "s", f"data, face {C['dface']['mean']:.0f} u, pitch up {C['pitch_up']['mean']:.0f} deg", C["t_hop"])
        out[f"{key}_pull_duration"] = P(m(C["t_pull_dur"]), "s", "data", C["t_pull_dur"])
        out[f"{key}_speed_at_detach"] = P(m(C["v_end"]), "u/s", "data", C["v_end"])
        out[f"{key}_detach_gap"] = P(m(C["gap"]), "u", "data: face x - origin x at the first ballistic cmd", C["gap"])
        out[f"{key}_speed_ramp"] = P(m(C["ramp"]), "u/s^2", "data: d|v|/dt, > 150 u from the face", C["ramp"])
        out[f"{key}_free_target_H"] = P(m(C["f1_H_implied"]), "u", "per-trial F1 fit: target z - origin z at fire - view-ray rise", C["f1_H_implied"])
    rows = S["trials"]
    out["tangential_accel_up"] = P(round(sum(r["at_up"]["mean"] for r in rows if r["at_up"].get("n")) / max(1, sum(1 for r in rows if r["at_up"].get("n"))), 2), "u/s^2", "data: accel along the velocity while moving up (> 150 u from the face), all conditions")
    out["detach_gap_all"] = P(m(S["gap_all"]), "u", "data, all no-input trials; no single static / look-ahead / 3D-distance threshold fits all", S["gap_all"])
    for name, G_ in S["global_models"].items():
        out[f"global_{name}"] = P({k: round(v, 3) for k, v in G_["params"].items()}, "-", f"one parameter set for all conditions; open-loop rms {G_['ol_rms']:.2f} u, one-step {G_['one_step_rms']:.3f} u/s",
                                  None, "; ".join(f"{k}: {v['ol_rms']:.1f}/{v['ol_max']:.1f} u" for k, v in G_["per_condition"].items()))
    return out


def build_params(res):
    L = res["lift"]["stats"]["single"]
    Lo = res["lift"]["stats"]["overlap"]
    Gs = res["grapple"]["stats"]
    Hc = res["horizon_controls"]
    m = lambda s, k="mean": (round(s[k], 4) if s.get("n") else None)  # noqa: E731
    sp = lambda s: ({"sd": round(s["sd"], 4), "min": round(s["min"], 4), "max": round(s["max"], 4)} if s.get("n") else None)  # noqa: E731

    def P(value, unit, source, s=None, note=""):
        d = {"value": value, "unit": unit, "source": source}
        if s is not None:
            d["n"] = s.get("n", 0)
            d["spread"] = sp(s)
        if note:
            d["note"] = note
        return d
    cen = res["census"]["diff"]
    out = {
        "scope": "R5Flowstate S21 client / S3 dedi, 120 fps, sessions M4_horizon and M4_pathfinder; values computed by lift_grapple_analysis.py",
        "gravity_lift": {
            "radius": P(70, "u", "script SPACEELEVATOR_TUNING_RADIUS (sh_space_elevator.gnut:51); touch radius incl. hull ~86 bracketed by data", None),
            "entry_dist_bracket_client": P([m(L["entry_dpre"]), m(L["entry_dpre_prev"])], "u", "data: pre-origin distance of the first lifted cmd and of the cmd before", L["entry_dpre"]),
            "exit_dist_bracket_client": P([m(L["exit_dpre_prev"]), m(L["exit_dpre"])], "u", "data: last lifted cmd and the eject cmd (strafe trials)", L["exit_dpre"]),
            "exit_dist_dedi": P(m(L["sv_exit_dpre"]), "u", "data: dedi eject cmd pre-origin distance", L["sv_exit_dpre"]),
            "lift_center_offset_x": P(m(L["center_x"]), "u", "data: oscillation centre x (deploy point -14680)", L["center_x"]),
            "height": P(1200, "u", "script SPACEELEVATOR_TUNING_HEIGHT; hover band starts at frac 0.9 (data)", L["hover_frac"]),
            "rise_speed": P(m(L["vz_rise_noinput"]), "u/s", "data (post vz in lift, no input); script up_speed 300", L["vz_rise_noinput"]),
            "rise_speed_with_input": P(m(L["vz_rise_input"]), "u/s", "data", L["vz_rise_input"]),
            "up_accel": P(100000, "u/s^2", "script up_accel; vz reaches 300 on the first lifted cmd (data)"),
            "gravity_in_lift": P(0, "u/s^2", "data: post vz = target exactly (gravity replaced, not added)"),
            "steer_speed": P(170, "u/s", "script horizontal_speed; data plateau 170.01"),
            "steer_accel_entry": P(2000, "u/s^2", "data entry ramp (residual below) = script horizontal_accel", L["ramp_resid_2000"], "residual u/s per cmd"),
            "steer_accel_strafe": P(2000, "u/s^2", "data: strafe at the centre, single-lift trials (residual below)", L["strafe_resid_2000"], "residual u/s per cmd"),
            "overlap_entry_step": P(m(Lo["entry_step"]), "u/s per cmd", "data: two live lift triggers (previous reset's lift) -> steering and hover timer applied twice", Lo["entry_step"]),
            "overlap_hover_time": P(m(Lo["hover_time"]), "s", "data: hover-eject time with two triggers", Lo["hover_time"]),
            "single_entry_step": P(m(L["entry_step"]), "u/s per cmd", "data: one trigger = (2000+800)*dt", L["entry_step"]),
            "air_accel_after_lift": P(800, "u/s^2", "Horizon airAcceleration (census); engine AirAccelerate runs after the lift force, cap airSpeed*msc = 92"),
            "tocenter_speed_outer": P(50, "u/s", "script tocenter_speed at radius 70"),
            "tocenter_speed_inner": P(25, "u/s", "0.5*tocenter_speed inside 20 u (dedi twin TG_TOCENTER_INNER); data", L["center_speed_err"], "error vs graph model, u/s"),
            "tocenter_inner_radius_fit": P(m(L["tocenter_inner_fit"]), "u", "data (implied from speed vs distance)", L["tocenter_inner_fit"]),
            "tocenter_accel": P(0, "u/s^2", "script tocenter_accel 0 -> horizontal velocity SET (no smoothing), data shows the step"),
            "hover_frac": P(m(L["hover_frac"]), "-", "data", L["hover_frac"]),
            "hover_vz_graph": P("0.5 -> -0.5 over frac 0.9..1.0", "u/s", "dedi twin; data error below", L["hover_vz_err"]),
            "max_hover_time": P(m(L["hover_time"]), "s", "data (script 0.5)", L["hover_time"]),
            "eject_up": P(m(L["eject_up"]), "u/s", "data (script 450), dwell >= 0.5 s", L["eject_up"]),
            "eject_horizontal": P(m(L["eject_h"]), "u/s", "data (script 400)", L["eject_h"]),
            "eject_dir_error": P(m(L["eject_dir_err"]), "deg", "data: flat view at the top; radial travel dir (>40 u) when leaving the side", L["eject_dir_err"]),
            "max_eject_time": P(0.5, "s", "script; eject scales with min(dwell/0.5,1) (not exercised: all dwells > 0.5 s)"),
            "reentry_block": P(2.0, "s", "dedi twin TG_EJECT_DEBOUNCE (not exercised)"),
            "jump_in_lift_effect": P(m(L["jump_effect"], "max"), "u/s", "data: max |dv| vs ride trial after the jump press", L["jump_effect"]),
            "dedi_entry_lag": P(m(L["sv_entry_lag"]), "cmds", "data: dedi enters later than the client", L["sv_entry_lag"]),
            "dedi_eject_lag": P(m(L["eject_sv_lag"]), "cmds", "data", L["eject_sv_lag"]),
        },
        "grapple": {
            "range": P(850, "u", "PW:mp_ability_grapple.txt:47-50 (not exercised)"),
            "fire_to_hop": P(m(Gs["t_fire_hop"]), "s", "data", Gs["t_fire_hop"]),
            "hop_vz": P(m(Gs["hop_vz"]), "u/s", "data: vz set to this on the hop cmd (pre-velocity of the hop cmd)", Gs["hop_vz"]),
            "fire_to_pull": P(m(Gs["t_fire_pull"]), "s", "data", Gs["t_fire_pull"]),
            "initial_accel": P(m(Gs["init_accel"]), "u/s^2", "data, gravity removed", Gs["init_accel"]),
            "initial_accel_cmds": P(m(Gs["init_accel_cmds"]), "cmds", "data", Gs["init_accel_cmds"]),
            "pull_speed_ramp": P(m(Gs["ramp_A"]), "u/s^2", "data: d|v|/dt, linear fit, no input", Gs["ramp_A"]),
            "pull_speed_ramp_W": P(m(Gs["ramp_A_W"]), "u/s^2", "data: W held", Gs["ramp_A_W"]),
            "pull_speed_ramp_W_precap": P(m(Gs["ramp_A_W_precap"]), "u/s^2", "data: W held, before the horizontal cap", Gs["ramp_A_W_precap"]),
            "m1_openloop_max_pos_err": P(m(Gs["m1_openloop_maxpos"]), "u", "M1 simulated over the steady pull (~0.95 s)", Gs["m1_openloop_maxpos"]),
            "m2_openloop_max_pos_err": P(m(Gs["m2_openloop_maxpos"]), "u", "M2 simulated over the steady pull", Gs["m2_openloop_maxpos"]),
            "W_horizontal_cap": P(m(Gs["cap_W_vh"]), "u/s", "data: = 420*msc", Gs["cap_W_vh"]),
            "pull_accel_M2": P(m(Gs["m2_A"]), "u/s^2", "fit M2 (chosen): v' = v + dt (A r_hat - s g z), steady pull, no input", Gs["m2_A"]),
            "pull_gravity_scale_M2": P(m(Gs["m2_k"]), "-", "fit M2", Gs["m2_k"]),
            "pull_target_z_M2": P(m(Gs["m2_zA"]), "u (abs, floor 294.92)", "fit M2, target x fixed at the wall face", Gs["m2_zA"]),
            "m2_rms": P(m(Gs["m2_rms"]), "u/s per cmd", "fit residual", Gs["m2_rms"]),
            "m1_turn_rate": P(m(Gs["m1_k"]), "1/s", "fit M1 (no input trials)", Gs["m1_k"]),
            "m1_anchor_z": P(m(Gs["m1_zA"]), "u", "fit M1 (anchor x fixed at the wall face)", Gs["m1_zA"]),
            "m1_rms": P(m(Gs["m1_rms"]), "u/s per cmd", "fit residual", Gs["m1_rms"]),
            "pull_time_to_wall": P(m(Gs["t_pull"]), "s", "data (394 u start distance)", Gs["t_pull"]),
            "speed_at_end": P(m(Gs["v_end"]), "u/s", "data", Gs["v_end"]),
            "detach_gap": P(m(Gs["detach_gap"]), "u", "data: wall face x - player origin x at the first ballistic cmd", Gs["detach_gap"]),
            "jump_effect": P(m(Gs["jump_effect"], "max"), "u/s", "data: max |dv| vs hold trial after the jump press", Gs["jump_effect"]),
            "hold_vs_hold_baseline": P(m(Gs["hold_vs_hold"], "max"), "u/s", "data: same metric between hold trials", Gs["hold_vs_hold"]),
            "detach_gap_W": P(m(Gs["detach_gap_W"]), "u", "data, W held", Gs["detach_gap_W"]),
            "detach_time_to_face": P(m(Gs["detach_time_to_face"]), "s", "data: (gap - 16) / vx at detach, no input", Gs["detach_time_to_face"]),
            "detach_time_to_face_W": P(m(Gs["detach_time_to_face_W"]), "s", "data, W held", Gs["detach_time_to_face_W"]),
            "impact_vz_after": P(m(Gs["impact_vz_after"]), "u/s", "data: vz on the wall-impact cmd (horizontal ~6 u/s)", Gs["impact_vz_after"]),
            "dedi_max_dv": P(m(Gs["sv_max_dv_pull"], "max"), "u/s", "data: client vs dedi post velocity during the pull", Gs["sv_max_dv_pull"]),
            "apex_z_after_impact": P(m(Gs["apex_z_after_impact"]), "u", "data, absolute z (floor 294.92)", Gs["apex_z_after_impact"]),
        },
        "grapple_series": series_params(res, P, m, sp),
        "horizon_passive": {
            "airSpeed": P(cen.get("airSpeed", {}).get("horizon"), "u/s", "census (others 60)"),
            "airAcceleration": P(cen.get("airAcceleration", {}).get("horizon"), "u/s^2", "census (others 500); data: lift entry ramp +800*dt up to 92"),
            "landSlowdownDuration": P(cen.get("landSlowdownDuration", {}).get("horizon"), "s", "census (others 1)"),
            "jump_V": P(m(Hc["jump_V"]), "u/s", "data e2_noinput (M2 289.823)", Hc["jump_V"]),
            "jump_V_e4_stand": P(m(Hc["jump_V_e4_stand"]), "u/s", "data e4_stand (M2 289.823)", Hc["jump_V_e4_stand"]),
            "gravity": P(m(Hc["gravity"]), "u/s^2", "data (M2 750)", Hc["gravity"]),
            "post_landing_decel": P(m(Hc["post_landing_decel"]), "u/s^2", "data (M2 1250)", Hc["post_landing_decel"]),
            "hard_landing_decel": P(m(L["land_decel"]), "u/s^2", "data: after the lift eject, impact ~ -1300 u/s", L["land_decel"]),
        },
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", required=True, nargs="+",
                    help="Horizon session folder(s); the first one must hold the [CLASSVAR] census and the e2/e4 controls")
    ap.add_argument("--pathfinder", required=True, nargs="+",
                    help="Pathfinder session folder(s); the first one holds hold/jump/fwd (section 4)")
    ap.add_argument("--ref", default=None, help="session folder with report/census.csv (reference legend)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--params", default=None)
    a = ap.parse_args()
    res = {}
    HS = [lg_load.load(f) for f in a.horizon]
    PS = [lg_load.load(f) for f in a.pathfinder]
    H, Pf = HS[0], PS[0]
    say("sessions: " + ", ".join(f"{S['folder']} ({len(S['trials'])} scored trials, parse errors {S['parse_errors']})"
                                 for S in HS + PS))
    for S in HS + PS:
        for t in S["trials"]:
            j = t["join"]
            say(f"  r{t['run']} {t['schedule']:16s} cmds {j['cmds']} joined {j['cmds_with_dt']} state_bad {j['state_bad']} "
                f"cmd_gaps {j['cmd_gaps']} fps {t['fps']}")
    section_census(a.horizon[0], a.pathfinder[0], a.ref, res)
    section_horizon_controls(H, None, res)
    section_lift(list(zip(HS, a.horizon)), res)
    section_grapple(Pf, res)
    section_grapple_series(PS, res)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(build_params(res), fh, indent=1)


if __name__ == "__main__":
    main()
