#!/usr/bin/env python3
"""M2 E2 (air control) + E4 (gravity / jump / landing / hops) analysis.

    python air_jump_analysis.py <session folder> [<session folder> ...] [--json results.json]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). Only trials with
ok=true and warmup=false and a schedule in SCHEDULES are used. Physics truth = client first-time
MOVE-TRACE commands (side cl, rp=0); dt and yaw per command come from the client HSD frame that shows
the command's post-state (aj_load.join, validated per command). Dedi MOVE-TRACE rows of the same
usercmd are used for parity, dedi HSD events (JUMP / TOUCH_GROUND) and the [HSD-RESET] server time
for the server-only jump penalty check.

Everything printed is computed here; nothing is tuned to pass. stdlib only, no local paths.
"""
import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aj_load as L  # noqa: E402

SCHEDULES = {"e2_strafe", "e2_noinput", "e2_keepfwd", "e4_stand", "e4_hop0", "e4_hop3", "e4_hop43"}
CENSUS = {"sv_gravity": 750.0, "gravityScale": 1.0, "jumpHeight": 56.0, "airSpeed": 60.0,
          "airAcceleration": 500.0, "airFriction": 0.0, "airDrag": 0.0, "antiMultiJumpHeightFrac": 0.3,
          "landSlowdownDuration": 1.0, "stepHeight": 22.0}
G = CENSUS["sv_gravity"] * CENSUS["gravityScale"]
H = CENSUS["jumpHeight"]
V0 = math.sqrt(2 * G * H)
FLOOR_Z = None  # taken per trial from the first command's origin (flat test platform)
K6 = ("ox", "oy", "oz", "vx", "vy", "vz")
P6 = ("pox", "poy", "poz", "pvx", "pvy", "pvz")


def hspd(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def lin_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    m = sxy / sxx
    b = my - m * mx
    res = [y - (m * x + b) for x, y in zip(xs, ys)]
    rms = math.sqrt(sum(r * r for r in res) / n)
    return m, b, rms, res


def rms(v):
    v = list(v)
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


# ----------------------------------------------------------------------------- events per trial
def jump_cmds(cs):
    """Indices of jump commands: pre-state on ground (MT ge=1) and post vz > 50."""
    return [i for i in range(len(cs)) if cs[i]["ground"] == 1 and cs[i]["pvz"] > 50.0]


def land_cmds(cs):
    """Indices of landing commands: pre-state airborne, post vz zeroed, pre vz < 0."""
    return [i for i in range(len(cs)) if cs[i]["ground"] == 0 and cs[i]["pvz"] == 0.0 and cs[i]["vz"] < 0.0]


def discontinuities(cs):
    out = []
    for k in range(1, len(cs)):
        a, b = cs[k - 1], cs[k]
        d = max(abs(b[x] - a[y]) for x, y in zip(K6, P6))
        if d > 0.002:
            out.append({"i": k, "max_abs": round(d, 3), "dz": round(b["oz"] - a["poz"], 3),
                        "dvz": round(b["vz"] - a["pvz"], 3),
                        "dvxy": round(math.hypot(b["vx"] - a["pvx"], b["vy"] - a["pvy"]), 3)})
    return out


# ----------------------------------------------------------------------------- 1. gravity / integration
def gravity_section(trials):
    gs, rz_trap, rz_post, rz_pre, rxy_post, rxy_pre = [], [], [], [], [], []
    for t in trials:
        cs = t["cmds"]
        lands = set(land_cmds(cs))
        disc = {d["i"] for d in discontinuities(cs)}
        for i, c in enumerate(cs):
            if c["ground"] != 0 or i in lands or c["dt"] is None or i in disc:
                continue
            dt = c["dt"]
            gs.append((c["vz"] - c["pvz"]) / dt)
            dz = c["poz"] - c["oz"]
            rz_trap.append(dz - 0.5 * (c["vz"] + c["pvz"]) * dt)
            rz_post.append(dz - c["pvz"] * dt)
            rz_pre.append(dz - c["vz"] * dt)
            dx, dy = c["pox"] - c["ox"], c["poy"] - c["oy"]
            rxy_post.append(math.hypot(dx - c["pvx"] * dt, dy - c["pvy"] * dt))
            rxy_pre.append(math.hypot(dx - c["vx"] * dt, dy - c["vy"] * dt))
    return {"g_per_cmd": L.stats(gs),
            "dz_resid_rms": {"half_step(trapezoid)": rms(rz_trap), "semi_implicit(post v)": rms(rz_post),
                             "explicit(pre v)": rms(rz_pre)},
            "dz_resid_max_halfstep": max(abs(x) for x in rz_trap),
            "dxy_resid_rms": {"post v": rms(rxy_post), "pre v": rms(rxy_pre)},
            "n": len(gs)}


# ----------------------------------------------------------------------------- 2. jumps
def frac_model(t, t0, T, f0=CENSUS["antiMultiJumpHeightFrac"]):
    if t is None:
        return 1.0
    return min(1.0, max(f0, f0 + (1.0 - f0) * (t - t0) / T))


def jump_rows(trials):
    rows = []
    for t in trials:
        cs = t["cmds"]
        sv = {c["cmd"]: c for c in t["sv_mt"]}
        js, ls = jump_cmds(cs), land_cmds(cs)
        disc = discontinuities(cs)
        floor = cs[0]["oz"]
        evj = [e for e in t["sv_evt"] if e.get("evt") == "JUMP"]
        evl = [e for e in t["sv_evt"] if e.get("evt") == "TOUCH_GROUND"]
        reset_t = None
        m = re.search(r"\bt=([0-9.]+)", t.get("reset", "") or "")
        if m:
            reset_t = float(m.group(1))
        for k, j in enumerate(js):
            c = cs[j]
            dt = c["dt"]
            V = c["pvz"] + 1.5 * G * dt
            mid = (c["poz"] - c["oz"]) / dt
            land = next((l for l in ls if l > j), None)
            prev_land = max((l for l in ls if l < j), default=None)
            t_land = sum(cs[m_]["dt"] for m_ in range(prev_land, j)) if prev_land is not None else None
            seg_end = land if land is not None else len(cs) - 1
            apex = max(cs[m_]["poz"] for m_ in range(j, seg_end + 1)) - c["oz"]
            s = sv.get(c["cmd"])
            Vs = s["pvz"] + 1.5 * G * dt if s else None
            corr = [d for d in disc if j < d["i"] <= (land if land is not None else len(cs))]
            sv_jt = evj[k]["t"] if k < len(evj) else None
            sv_prev_land_t = None
            if sv_jt is not None:
                prior = [e["t"] for e in evl if e["t"] < sv_jt]
                sv_prev_land_t = prior[-1] if prior else None
            r = {"run": t["label"], "schedule": t["schedule"], "hop": k + 1, "i_jump": j, "i_land": land,
                 "dt": dt, "V_cl": V, "frac_cl": V * V / (2 * G * H), "mid_vz": mid, "mid_pred": V - G * dt,
                 "V_sv": Vs, "frac_sv": (Vs * Vs / (2 * G * H)) if Vs else None,
                 "t_since_land": t_land, "n_ground": (j - prev_land) if prev_land is not None else None,
                 "apex": apex, "air_cmds": (land - j) if land is not None else None,
                 "air_s": sum(cs[m_]["dt"] for m_ in range(j, land + 1)) if land is not None else None,
                 "land_height": (cs[land]["poz"] - floor) if land is not None else None,
                 "land_vz": cs[land]["vz"] if land is not None else None,
                 "spd_pre_jump": hspd(c, False), "spd_post_jump": hspd(c),
                 "spd_pre_land": hspd(cs[prev_land], False) if prev_land is not None else None,
                 "spd_post_land": hspd(cs[prev_land]) if prev_land is not None else None,
                 "corrections_in_air": corr,
                 "sv_jump_t": sv_jt, "sv_since_land": (sv_jt - sv_prev_land_t) if sv_prev_land_t else None,
                 "sv_since_reset": (sv_jt - reset_t) if (sv_jt is not None and reset_t is not None and k == 0) else None}
            rows.append(r)
    return rows


def simulate_jump(cs, j, V, floor, probe=2.0):
    """Half-step gravity integration of one jump over the recorded dts. Returns (apex, i_land)."""
    c = cs[j]
    dt = c["dt"]
    z = c["oz"] + (V - G * dt) * dt
    vz = V - 1.5 * G * dt
    apex = z - c["oz"]
    i = j + 1
    while i < len(cs) and cs[i]["dt"] is not None:
        dt = cs[i]["dt"]
        z += (vz - 0.5 * G * dt) * dt
        vz -= G * dt
        apex = max(apex, z - c["oz"])
        if vz < 0 and z - floor < probe:
            return apex, i
        i += 1
    return apex, None


# ----------------------------------------------------------------------------- 3. air control
def wish(c, yaw):
    r = math.radians(yaw)
    f = (math.cos(r), math.sin(r))
    rt = (math.sin(r), -math.cos(r))
    wx = c["fwd"] * f[0] + c["sidemove"] * rt[0]
    wy = c["fwd"] * f[1] + c["sidemove"] * rt[1]
    n = math.hypot(wx, wy)
    if n < 1e-9:
        return None, 0.0
    return (wx / n, wy / n), min(n, 1.0) * c["maxspeed"]


def air_accel_pred(c, yaw, cap, form):
    w, ws = wish(c, yaw)
    if w is None:
        return 0.0, 0.0
    wcap = min(ws, cap)
    vw = c["vx"] * w[0] + c["vy"] * w[1]
    add = wcap - vw
    if add <= 0:
        return 0.0, 0.0
    A = CENSUS["airAcceleration"]
    acc = {"A*dt": A * c["dt"], "A*wishcap*dt": A * wcap * c["dt"], "A*wishspeed*dt": A * ws * c["dt"]}[form]
    acc = min(acc, add)
    return acc * w[0], acc * w[1]


def air_section(trials):
    out = {}
    # (a) no input / keep forward: horizontal speed change per airborne command
    for sched in ("e2_noinput", "e2_keepfwd"):
        d_noin, d_fwd, gain = [], [], []
        for t in trials:
            if t["schedule"] != sched:
                continue
            cs = t["cmds"]
            lands = set(land_cmds(cs))
            j = jump_cmds(cs)[0]
            land = min(l for l in lands if l > j)
            gain.append(hspd(cs[land]) - hspd(cs[j]))
            for i in range(j + 1, land + 1):
                c = cs[i]
                d = hspd(c) - hspd(c, False)
                (d_fwd if (c["fwd"] or c["sidemove"]) else d_noin).append(d)
        out[sched] = {"dspd_per_cmd_noinput": L.stats(d_noin), "dspd_per_cmd_input": L.stats(d_fwd),
                      "total_gain_jump_to_land": L.stats(gain)}
        if sched == "e2_keepfwd":
            xs, ys = [], []
            for t in trials:
                if t["schedule"] != sched:
                    continue
                cs = t["cmds"]
                j = jump_cmds(cs)[0]
                land = min(l for l in land_cmds(cs) if l > j)
                for i in range(j + 1, land):
                    c = cs[i]
                    xs.append(c["vz"])
                    ys.append((hspd(c) - hspd(c, False)) / c["dt"])
            fits = {}
            for nm, f in (("const", lambda v: 1.0), ("|vz|", abs), ("vz^2", lambda v: v * v)):
                fx = [f(v) for v in xs]
                k = sum(a_ * b_ for a_, b_ in zip(fx, ys)) / sum(a_ * a_ for a_ in fx)
                fits[nm] = {"k": k, "rms": rms(y - k * x for x, y in zip(fx, ys))}
            out[sched]["residual_accel_fits(u/s^2)"] = fits
    # (b) strafe + turn: fit AirAccelerate forms
    forms = ["A*dt", "A*wishcap*dt", "A*wishspeed*dt"]
    caps = {"airSpeed": CENSUS["airSpeed"], "airSpeed*movescale": None}
    yaws = ("cur", "prev")
    res = {}
    samples = []
    lurch = []
    cap_lo, cap_hi = -1e9, 1e9
    afit = []
    for t in trials:
        if not t["schedule"].startswith("e2_"):
            continue
        cs = t["cmds"]
        lands = set(land_cmds(cs))
        j = jump_cmds(cs)[0]
        land = min(l for l in lands if l > j)
        for i in range(j + 1, land):  # airborne, landing command excluded (ground logic)
            c, p = cs[i], cs[i - 1]
            if c["dt"] is None or p["yaw"] is None:
                continue
            press = (c["buttons"] & 0x618) & ~(p["buttons"] & 0x618)
            if press:
                lurch.append((t, i))
                continue
            samples.append((t, c, p))
            if t["schedule"] == "e2_strafe" and c["sidemove"] == 1.0:
                w, _ = wish(c, c["yaw"])
                vw = c["vx"] * w[0] + c["vy"] * w[1]
                a = (c["pvx"] - c["vx"]) * w[0] + (c["pvy"] - c["vy"]) * w[1]
                full = CENSUS["airAcceleration"] * c["dt"]
                if vw < 60.0:  # far below either cap candidate minus one step: unclipped step
                    afit.append(a / c["dt"])
                if a < 0.05:         # inactive: cap <= vw (+ the small residual)
                    cap_hi = min(cap_hi, vw + a)
                elif a > full - 0.01:  # full step: cap >= vw + full step
                    cap_lo = max(cap_lo, vw + a)
                else:                  # add-speed limited: cap = vw + a exactly
                    cap_lo = max(cap_lo, vw + a)
                    cap_hi = min(cap_hi, vw + a)
    for form in forms:
        for capname in caps:
            for yw in yaws:
                rr, rr_active = [], []
                for t, c, p in samples:
                    cap = c["movescale"] * CENSUS["airSpeed"] if capname == "airSpeed*movescale" else caps[capname]
                    yaw = c["yaw"] if yw == "cur" else p["yaw"]
                    px, py = air_accel_pred(c, yaw, cap, form)
                    e = math.hypot(c["pvx"] - c["vx"] - px, c["pvy"] - c["vy"] - py)
                    rr.append(e)
                    if t["schedule"] == "e2_strafe" and (c["sidemove"] or c["fwd"]):
                        rr_active.append(e)
                res[f"{form} | cap={capname} | yaw={yw}"] = {"rms_all": rms(rr), "max_all": max(rr),
                                                             "rms_strafe": rms(rr_active),
                                                             "max_strafe": max(rr_active), "n": len(rr)}
    out["strafe_fit"] = res
    out["cap_bracket"] = [cap_lo, cap_hi]
    out["accel_per_s_unclipped"] = L.stats(afit)
    # (c) lurch (tap-strafe) events
    lu = []
    for t, i in lurch:
        c = cs_ = t["cmds"][i]
        w, ws = wish(c, c["yaw"])
        v0 = (c["vx"], c["vy"])
        v1 = (c["pvx"], c["pvy"])
        a0 = math.degrees(math.atan2(v0[1], v0[0]))
        a1 = math.degrees(math.atan2(v1[1], v1[0]))
        aw = math.degrees(math.atan2(w[1], w[0]))
        # decompose v1 = alpha*w + beta*v0hat
        s0 = math.hypot(*v0)
        u = (v0[0] / s0, v0[1] / s0)
        det = w[0] * u[1] - w[1] * u[0]
        alpha = (v1[0] * u[1] - v1[1] * u[0]) / det
        beta = (w[0] * v1[1] - w[1] * v1[0]) / det
        lu.append({"run": t["label"], "i": i, "t_after_jump_cmds": i - jump_cmds(t["cmds"])[0],
                   "sidemove": c["sidemove"], "fwd": c["fwd"], "spd0": s0, "spd1": math.hypot(*v1),
                   "ratio": math.hypot(*v1) / s0, "dir0": a0, "dir1": a1, "wishdir": aw,
                   "turn_deg": a1 - a0, "turn_frac_of_wish": (a1 - a0) / (aw - a0),
                   "alpha_w": alpha, "beta_v0hat": beta, "sv_same": _sv_same(t, c)})
    out["lurch"] = lu
    return out


def _sv_same(t, c):
    s = next((x for x in t["sv_mt"] if x["cmd"] == c["cmd"]), None)
    if s is None:
        return None
    return max(abs(s[k] - c[k]) for k in K6 + P6) < 0.002


# ----------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    trials, joins = [], []
    for folder in a.sessions:
        S = L.load_session(folder)
        runner = json.load(open(os.path.join(folder, "runner.json"), encoding="utf-8"))
        resets = {t["run"]: t.get("reset", "") for t in runner["trials"]}
        for t in S["trials"]:
            if t["schedule"] not in SCHEDULES:
                continue
            t["session"] = S["folder"]
            t["reset"] = resets.get(t["run"], "")
            trials.append(t)
            joins.append({"session": S["folder"], "run": t["label"], "schedule": t["schedule"], **t["join"]})
    print(f"# trials used: {len(trials)}")
    by = {}
    for t in trials:
        by.setdefault(t["schedule"], []).append(t["label"])
    for k in sorted(by):
        print(f"  {k}: {', '.join(by[k])}")
    nc = sum(j["cmds"] for j in joins)
    nd = sum(j["cmds_with_dt"] for j in joins)
    print(f"\n## join: {nd}/{nc} commands have a validated frame (state==post, 1 cmd per frame interval); "
          f"state mismatches {sum(j['state_bad'] for j in joins)}, intervals !=1 cmd {sum(j['multi_or_zero'] for j in joins)}, "
          f"cmd gaps {sum(j['cmd_gaps'] for j in joins)}")
    dts = [c["dt"] for t in trials for c in t["cmds"] if c["dt"] is not None]
    print(f"   dt per usercmd: {L.fmt(L.stats(dts), 5)}")

    # 1 gravity
    gsec = gravity_section(trials)
    print("\n## 1. gravity / integration (airborne commands, landing commands and corrected commands excluded)")
    print(f"   g = (vz - pvz)/dt: {L.fmt(gsec['g_per_cmd'], 3)}")
    for k, v in gsec["dz_resid_rms"].items():
        print(f"   dz residual rms, {k}: {v:.5f} u")
    print(f"   dz residual max (half-step): {gsec['dz_resid_max_halfstep']:.5f} u")
    for k, v in gsec["dxy_resid_rms"].items():
        print(f"   dxy residual rms, {k}: {v:.5f} u")

    # 2 jumps
    jr = jump_rows(trials)
    first = [r for r in jr if r["hop"] == 1]
    print("\n## 2. jump take-off (V = post vz of the jump command + 1.5 g dt)")
    print(f"   first jumps, client V: {L.fmt(L.stats([r['V_cl'] for r in first]), 3)}  (sqrt(2 g h) = {V0:.3f})")
    print(f"   first jumps, client post vz: {L.fmt(L.stats([r['V_cl'] - 1.5 * G * r['dt'] for r in first]), 3)}")
    print(f"   all jumps, mid vz (dz/dt) - (V - g dt): {L.fmt(L.stats([r['mid_vz'] - r['mid_pred'] for r in jr]), 3)}"
          f"  (dz printed to 0.001 u -> +-{0.0005 / 0.0069:.3f} u/s)")
    alt = L.stats([r["V_cl"] - 0.5 * G * r["dt"] for r in first])
    print(f"   alt. (post = V - g dt) would give V: {L.fmt(alt, 3)}")
    full = [r for r in jr if r["frac_cl"] > 0.999 and r["i_land"] is not None and not r["corrections_in_air"]]
    print(f"   full jumps (client=server): apex {L.fmt(L.stats([r['apex'] for r in full]), 3)} u, "
          f"air cmds {L.fmt(L.stats([r['air_cmds'] for r in full]), 2)}, air s {L.fmt(L.stats([r['air_s'] for r in full]), 4)}")
    cont = L.stats([r["V_cl"] ** 2 / (2 * G) - 0.5 * r["V_cl"] * r["dt"] + 0.125 * G * r["dt"] ** 2 for r in full])
    print(f"   closed-form apex of the half-step trajectory, V^2/2g - V dt/2 + g dt^2/8: {L.fmt(cont, 3)}")
    print(f"   landing command: post height above floor {L.fmt(L.stats([r['land_height'] for r in jr if r['land_height'] is not None]), 3)}")
    sim = []
    for t in trials:
        cs = t["cmds"]
        for r in [x for x in jr if x["run"] == t["label"] and x["i_land"] is not None and not x["corrections_in_air"]]:
            ap_, il = simulate_jump(cs, r["i_jump"], r["V_cl"], cs[0]["oz"])
            sim.append((ap_ - r["apex"], (il - r["i_land"]) if il is not None else None))
    print(f"   half-step sim with fitted V, 2 u ground probe: apex err {L.fmt(L.stats([s[0] for s in sim]), 4)}, "
          f"land-index err {L.fmt(L.stats([s[1] for s in sim]), 2)}")

    # parity / corrections
    print("\n## parity: client prediction vs dedi, corrections (pre-state != previous post-state)")
    for r in jr:
        if r["V_sv"] is not None and abs(r["V_sv"] - r["V_cl"]) > 0.01:
            print(f"   {r['run']} {r['schedule']} hop{r['hop']}: V_cl {r['V_cl']:.3f} V_sv {r['V_sv']:.3f} "
                  f"(frac_sv {r['frac_sv']:.4f}); server time since [HSD-RESET] {r['sv_since_reset']}; "
                  f"correction {r['corrections_in_air']}")
    nmis = sum(1 for r in jr if r["V_sv"] is not None and abs(r["V_sv"] - r["V_cl"]) > 0.01)
    print(f"   jumps with V mismatch: {nmis}/{len(jr)}")
    allc = [d for t in trials for d in discontinuities(t["cmds"])]
    print(f"   corrections in all used trials: {len(allc)}")

    # 3 hops
    print("\n## 3. hops: per-hop table (client)")
    print("   run   sched     hop nGnd t_land  V_cl    frac   apex   airc spd_preland spd_postland spd_prejump spd_postjump")
    for r in jr:
        if not r["schedule"].startswith("e4_hop"):
            continue
        tl = f"{r['t_since_land']:.4f}" if r["t_since_land"] is not None else "   -  "
        ng = r["n_ground"] if r["n_ground"] is not None else "-"
        def f(x, n=2):
            return f"{x:.{n}f}" if x is not None else "-"
        print(f"   {r['run']} {r['schedule']:9s} {r['hop']}  {str(ng):>4s} {tl} {r['V_cl']:7.2f} {r['frac_cl']:.4f} "
              f"{r['apex']:6.2f} {str(r['air_cmds']):>4s} {f(r['spd_pre_land']):>8s} {f(r['spd_post_land']):>8s} "
              f"{r['spd_pre_jump']:8.2f} {r['spd_post_jump']:8.2f}")
    # penalty fit
    pts = [(r["t_since_land"], r["frac_cl"]) for r in jr if r["t_since_land"] is not None]
    ramp = [(x, y) for x, y in pts if 0.31 < y < 0.995]
    m, b, rr, res = lin_fit([x for x, _ in ramp], [y for _, y in ramp])
    t0, T = (0.3 - b) / m, 0.7 / m
    print(f"\n   height-frac ramp fit on {len(ramp)} hops with 0.31<frac<0.995: slope {m:.4f}/s, "
          f"t0 {t0:.4f} s, T {T:.4f} s (full at {t0 + T:.4f} s), rms {rr:.4f}, max |res| {max(abs(x) for x in res):.4f}")
    mv, bv, rv, resv = lin_fit([x for x, _ in ramp], [math.sqrt(y) for _, y in ramp])
    print(f"   alternative: V/V0 linear in t: rms {rv:.4f} (in V/V0 units; x2 ~ frac units {2 * rv:.4f})")
    worst = sorted(zip(res, ramp), key=lambda z: -abs(z[0]))[:3]
    print(f"   worst residuals (res, t, frac): {[(round(a_, 4), round(x, 4), round(y, 4)) for a_, (x, y) in worst]}")
    plateau = [y for x, y in pts if x < 0.05]
    print(f"   plateau (t<0.05 s): frac {L.fmt(L.stats(plateau), 5)}")
    # same fit on the dedi event clock (JUMP.t - previous TOUCH_GROUND.t, both dedi script Time())
    svh = [(r["sv_since_land"], r["frac_sv"]) for r in jr if r["sv_since_land"] is not None and r["frac_sv"] is not None
           and r["schedule"].startswith("e4_hop")]
    svr = [(x, y) for x, y in svh if 0.31 < y < 0.995]
    ms, bs, rs_, ress = lin_fit([x for x, _ in svr], [y for _, y in svr])
    t0s, Ts = (0.3 - bs) / ms, 0.7 / ms
    print(f"   same fit on dedi event clock (JUMP.t - TOUCH_GROUND.t): slope {ms:.5f}/s, t0 {t0s:.5f} s, "
          f"T {Ts:.5f} s, rms {rs_:.5f}, max |res| {max(abs(x) for x in ress):.5f}, n {len(svr)}")
    _, _, rvs, _ = lin_fit([x for x, _ in svr], [math.sqrt(y) for _, y in svr])
    print(f"   alternative on dedi clock: V/V0 linear in t: rms {rvs:.5f} V/V0 units (height-frac linear: {rs_:.5f} frac units)")
    print(f"   dedi clock minus client dt-sum, per hop: "
          f"{L.fmt(L.stats([r['sv_since_land'] - r['t_since_land'] for r in jr if r['sv_since_land'] is not None and r['t_since_land'] is not None]), 4)}")
    t0r, Tr = round(t0s, 3), round(Ts, 3)
    for name, data in (("dedi clock", svh), ("client dt-sum", pts)):
        pred = [(x, y, frac_model(x, t0r, Tr)) for x, y in data]
        print(f"   model t0={t0r}, T={Tr} on {name}: residual rms {rms(y - p for _, y, p in pred):.5f}, "
              f"max {max(abs(y - p) for _, y, p in pred):.5f} over {len(pred)} hops")
    # server-side check (independent condition): first jump of stand trials, time since [HSD-RESET]
    chk = [(r["run"], r["sv_since_reset"], r["frac_sv"], frac_model(r["sv_since_reset"], t0r, Tr))
           for r in jr if r["schedule"] == "e4_stand" and r["sv_since_reset"] is not None]
    print("   server check, stand jumps: (run, dedi t since HSD-RESET, frac_sv, model) "
          + ", ".join(f"({a_}, {b_:.3f}, {c_:.4f}, {d_:.4f})" for a_, b_, c_, d_ in chk))
    # horizontal through hops
    hl = [r["spd_post_jump"] - r["spd_pre_jump"] for r in jr]
    ll = [r["spd_post_land"] - r["spd_pre_land"] for r in jr if r["spd_pre_land"] is not None]
    print(f"\n   horizontal speed change on the jump command: {L.fmt(L.stats(hl), 3)}")
    print(f"   horizontal speed change on the landing command: {L.fmt(L.stats(ll), 3)}")
    print(f"   speed at take-off, hops 2-5: {L.fmt(L.stats([r['spd_post_jump'] for r in jr if r['hop'] > 1]), 3)}")

    # 4 air control
    asec = air_section(trials)
    print("\n## 4. air control")
    for k in ("e2_noinput", "e2_keepfwd"):
        v = asec[k]
        print(f"   {k}: dspd/cmd no input {L.fmt(v['dspd_per_cmd_noinput'], 4)}; with input {L.fmt(v['dspd_per_cmd_input'], 4)}; "
              f"jump->land gain {L.fmt(v['total_gain_jump_to_land'], 3)}")
        if "residual_accel_fits(u/s^2)" in v:
            print("     keepfwd residual horizontal accel (u/s^2) = k*f(vz): "
                  + "; ".join(f"{n}: k={x['k']:.4g} rms={x['rms']:.4f}" for n, x in v["residual_accel_fits(u/s^2)"].items()))
    print("   AirAccelerate forms, residual |dv_obs - dv_pred| (u/s per command):")
    for k, v in sorted(asec["strafe_fit"].items(), key=lambda kv: kv[1]["rms_all"]):
        print(f"     {k:48s} rms_all {v['rms_all']:8.4f} max_all {v['max_all']:8.4f} | strafe rms {v['rms_strafe']:8.4f} max {v['max_strafe']:8.4f} (n {v['n']})")
    print(f"   air wish-speed cap bracket from strafe commands: [{asec['cap_bracket'][0]:.3f}, {asec['cap_bracket'][1]:.3f}]")
    print(f"   unclipped air accel along wishdir, a/dt (strafe, v.wishdir < 60): {L.fmt(asec['accel_per_s_unclipped'], 3)} u/s^2")
    print("   lurch (direction-key press edge in the air):")
    for x in asec["lurch"]:
        print(f"     {x['run']} cmd+{x['t_after_jump_cmds']} after jump, side {x['sidemove']}: speed {x['spd0']:.3f} -> {x['spd1']:.3f} "
              f"(x{x['ratio']:.4f}); dir {x['dir0']:.3f} -> {x['dir1']:.3f} deg (wish {x['wishdir']:.3f}, "
              f"{x['turn_frac_of_wish']:.4f} of the way); v1 = {x['beta_v0hat']:.2f}*v0hat + {x['alpha_w']:.2f}*wishdir; dedi same: {x['sv_same']}")

    out = {"trials": by, "join": joins, "gravity": gsec, "jumps": jr, "air": asec,
           "penalty_fit": {"client_dtsum": {"slope": m, "intercept": b, "t0": t0, "T": T, "rms": rr, "n": len(ramp)},
                           "dedi_clock": {"slope": ms, "intercept": bs, "t0": t0s, "T": Ts, "rms": rs_, "n": len(svr)},
                           "rounded": {"t0": t0r, "T": Tr}, "server_stand_check": chk}}
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, default=lambda o: None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
