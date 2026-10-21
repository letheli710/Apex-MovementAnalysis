#!/usr/bin/env python3
"""M3 E3 lurch (tap-strafe) analysis.

    python lurch_analysis.py <session folder> [<session folder> ...] [--json results.json]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). Only trials with ok=true,
warmup=false and a schedule starting with "e3_" are used.

Physics truth: client first-time MOVE-TRACE commands (side cl, rp=0). dt and yaw per command come from the
client HSD frame that shows the command's post-state (the M2 join, ../../m2/air_jump/aj_load.py, validated per
command). Dedi MOVE-TRACE rows of the same usercmd and client replay rows (rp=1) are used for parity.

Per trial:
  j  = jump command (pre-state on ground, post vz > 50); it is also the take-off command.
  p  = first command after j with a press edge on IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT (0x618).
  v' = v0 + AirAccelerate(v0)  (M2 model: accel 500*dt, wish cap 60*movescale, current yaw)
  D  = v1 - v'                 (the lurch term on the press command)
Everything printed is computed here; nothing is tuned to pass. stdlib only, no local paths.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m2", "air_jump")))
import aj_load as L  # noqa: E402  (also puts hsdtel on sys.path)
from hsdtel import derive, parse  # noqa: E402

LURCH_MASK = 0x618
A_AIR, AIR_SPEED = 500.0, 60.0
K6 = ("ox", "oy", "oz", "vx", "vy", "vz")
P6 = ("pox", "poy", "poz", "pvx", "pvy", "pvz")
TOL = 0.002  # print precision (%.3f) incl. rounding of both values


# ----------------------------------------------------------------------------- loading
def load_session(folder):
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    plat = L._plat_index(files)
    for r in rows:
        r["plat"] = plat.get((r.get("session"), r.get("file"), r.get("line_no")))
    cl_mt, cl_rp, cl_fr, sv_mt = {}, {}, {}, {}
    for r in rows:
        run = r.get("drv_run")
        if r["source"] == "MT":
            if r.get("side") == "cl":
                (cl_rp if r.get("replay") else cl_mt).setdefault(run, []).append(r)
            elif not r.get("replay"):
                sv_mt.setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "cl" and r.get("kind") == "frame":
            cl_fr.setdefault(run, []).append(r)
    trials = []
    for t in runner["trials"]:
        if t.get("warmup") or not t.get("ok") or not str(t.get("schedule", "")).startswith("e3_"):
            continue
        lab = f"r{t['run']}"
        cmds = sorted(cl_mt.get(lab, []), key=lambda r: r["cmd"])
        frames = sorted([f for f in cl_fr.get(lab, []) if f.get("plat") is not None], key=lambda r: r["plat"])
        st = L.join(cmds, frames)
        trials.append({"session": os.path.basename(os.path.normpath(folder)), "run": t["run"], "label": lab,
                       "schedule": t["schedule"], "fps_set": runner.get("client_fps"), "fps": t.get("measured_fps"),
                       "sched_lines": t.get("sched_lines", []), "cmds": cmds, "join": st,
                       "sv": {r["cmd"]: r for r in sv_mt.get(lab, [])},
                       "rp": cl_rp.get(lab, [])})
    return {"folder": os.path.basename(os.path.normpath(folder)), "client_fps": runner.get("client_fps"),
            "trials": trials, "parse_errors": sum(1 for i in issues if i.severity == "error")}


# ----------------------------------------------------------------------------- vector helpers
def norm(v):
    return math.hypot(v[0], v[1])


def unit(v):
    n = norm(v)
    return (v[0] / n, v[1] / n) if n > 1e-9 else None


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def wish(c):
    r = math.radians(c["yaw"] or 0.0)
    f, rt = (math.cos(r), math.sin(r)), (math.sin(r), -math.cos(r))
    wx = c["fwd"] * f[0] + c["sidemove"] * rt[0]
    wy = c["fwd"] * f[1] + c["sidemove"] * rt[1]
    n = math.hypot(wx, wy)
    if n < 1e-9:
        return None, 0.0
    return (wx / n, wy / n), min(n, 1.0) * c["maxspeed"]


def air_accel(c, v):
    """M2 AirAccelerate (no free parameters)."""
    w, ws = wish(c)
    if w is None:
        return v
    add = min(ws, AIR_SPEED * c["movescale"]) - dot(v, w)
    if add <= 0:
        return v
    a = min(A_AIR * c["dt"], add)
    return (v[0] + a * w[0], v[1] + a * w[1])


# ----------------------------------------------------------------------------- lurch models
def lurch_lerp(v, w, lam, Lmax):
    """Chosen model: target = |v| * normalize((1-lam)*vhat + lam*w); D = clampLen(target - v, Lmax)."""
    s = norm(v)
    u = unit(v)
    if u is None or lam <= 0:
        return v
    d = unit(((1 - lam) * u[0] + lam * w[0], (1 - lam) * u[1] + lam * w[1]))
    if d is None:
        return v
    D = (s * d[0] - v[0], s * d[1] - v[1])
    n = norm(D)
    if n > Lmax:
        D = (D[0] * Lmax / n, D[1] * Lmax / n)
    return (v[0] + D[0], v[1] + D[1])


def lurch_slerp(v, w, f, Lmax):
    """Alternative: rotate v toward w by f * angle(v, w) (speed kept), then the same clamp."""
    s = norm(v)
    u = unit(v)
    th = math.atan2(cross(u, w), dot(u, w))
    if abs(abs(th) - math.pi) < 1e-9:
        th = math.pi  # direction ambiguous at 180 deg: take one side (heading change is then the test)
    a = f * th
    d = (u[0] * math.cos(a) - u[1] * math.sin(a), u[0] * math.sin(a) + u[1] * math.cos(a))
    D = (s * d[0] - v[0], s * d[1] - v[1])
    n = norm(D)
    if n > Lmax:
        D = (D[0] * Lmax / n, D[1] * Lmax / n)
    return (v[0] + D[0], v[1] + D[1])


def lurch_ab(v0, w, a, b):
    """User hypothesis: v1 = a*v0 + b*|v0|*wishdir (applied to v')."""
    s = norm(v0)
    return (a * v0[0] + b * s * w[0], a * v0[1] + b * s * w[1])


def lam_of(u, w, d):
    """lam such that (1-lam)*u + lam*w is parallel to d; None when undefined (w = -u)."""
    c1, c2 = cross(u, d), cross(w, d)
    if abs(c1 - c2) < 1e-9:
        return None
    return c1 / (c1 - c2)


# ----------------------------------------------------------------------------- per-trial events
def event(t):
    cs = t["cmds"]
    J = [i for i in range(1, len(cs)) if cs[i]["ground"] == 1 and cs[i]["pvz"] > 50]
    if not J:
        return None
    j = J[0]
    P = [i for i in range(j + 1, len(cs)) if (cs[i]["buttons"] & LURCH_MASK) & ~(cs[i - 1]["buttons"] & LURCH_MASK)]
    if not P:
        return None
    p = P[0]
    c = cs[p]
    if any(cs[i]["dt"] is None for i in range(j, p + 1)) or c["yaw"] is None:
        return {"run": t["run"], "bad": "missing dt in jump..press"}
    land = next((i for i in range(j + 1, len(cs)) if cs[i]["ground"] == 1), len(cs))
    w, _ = wish(c)
    v0 = (c["vx"], c["vy"])
    vp = air_accel(c, v0)
    v1 = (c["pvx"], c["pvy"])
    u = unit(vp)
    nrm = (-u[1], u[0])
    if dot(nrm, w) < 0:
        nrm = (-nrm[0], -nrm[1])
    D = (v1[0] - vp[0], v1[1] - vp[1])
    s0, s1 = norm(vp), norm(v1)
    clamped = (s0 - s1) > 0.01
    if norm(D) < 0.01:
        T = vp
    elif clamped:  # target lies on the |v'| circle along D: reflect v' about the normal of D
        Dh = unit(D)
        k = dot(vp, Dh)
        T = (vp[0] - 2 * k * Dh[0], vp[1] - 2 * k * Dh[1])
    else:
        T = v1
    lam = lam_of(u, w, unit(T)) if norm(D) >= 0.01 else 0.0
    theta = math.degrees(math.acos(max(-1.0, min(1.0, dot(u, w)))))
    dts = [cs[i]["dt"] for i in range(j, p + 1)]
    tA = sum(dts[:-1])  # start of jump command .. start of press command
    # spread check: AirAccelerate residual on the other airborne commands of this jump
    other = []
    for i in range(j + 1, land):
        if i == p or cs[i]["dt"] is None or cs[i]["yaw"] is None:
            continue
        q = cs[i]
        pv = air_accel(q, (q["vx"], q["vy"]))
        other.append(math.hypot(q["pvx"] - pv[0], q["pvy"] - pv[1]))
    sv = t["sv"].get(c["cmd"])
    sv_d = max(abs(sv[k] - c[k]) for k in K6 + P6) if sv else None
    rp = [r for r in t["rp"] if r["cmd"] == c["cmd"]]
    rp_d = [max(abs(r[k] - c[k]) for k in K6 + P6) for r in rp]
    corr = [i - j for i in range(max(1, j - 2), min(len(cs), land + 2))
            if max(abs(cs[i][k] - cs[i - 1]["p" + k]) for k in ("ox", "oy", "vx", "vy", "vz")) > TOL]
    return {"session": t["session"], "run": t["run"], "schedule": t["schedule"], "fps_set": t["fps_set"],
            "fps": t["fps"], "n_cmds": p - j, "dt_press": c["dt"], "dt_mean": sum(dts) / len(dts), "tA": tA,
            "t_frame": (c.get("t") or 0) - (cs[j].get("t") or 0), "theta_deg": theta, "fwd": c["fwd"],
            "side": c["sidemove"], "s0_pre_aa": norm(v0), "s0": s0, "s1": s1, "ratio": s1 / s0,
            "D_par": dot(D, u), "D_perp": dot(D, nrm), "D_len": norm(D), "clamped": clamped,
            "heading_change_deg": math.degrees(math.atan2(cross(u, v1), dot(u, v1))), "lam": lam,
            "a_user": dot(v1, u) / s0 if theta < 179 else None,
            "b_user": dot(v1, nrm) / s0 if theta < 179 else None,
            "_v0": v0, "_vp": vp, "_v1": v1, "_w": w, "_aa": (vp[0] - v0[0], vp[1] - v0[1]), "_c": c,
            "jump_s_pre": math.hypot(cs[j]["vx"], cs[j]["vy"]), "jump_s_post": math.hypot(cs[j]["pvx"], cs[j]["pvy"]),
            "s_max_before_jump": max(math.hypot(q["vx"], q["vy"]) for q in cs[:j + 1]),
            "other_resid_max": max(other) if other else None, "other_n": len(other),
            "sv_diff": sv_d, "sv_D_len": (math.hypot(sv["pvx"] - air_accel(c, (sv["vx"], sv["vy"]))[0],
                                                     sv["pvy"] - air_accel(c, (sv["vx"], sv["vy"]))[1])
                                          if sv else None),
            "rp_n": len(rp), "rp_diff": rp_d, "corrections_rel_j": corr,
            "dvz_resid": c["vz"] - c["pvz"] - 750.0 * c["dt"]}


# ----------------------------------------------------------------------------- stats helpers
def lin_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    b = my - m * mx
    res = [y - (m * x + b) for x, y in zip(xs, ys)]
    dof = max(n - 2, 1)
    s2 = sum(r * r for r in res) / dof
    se_m = math.sqrt(s2 / sxx)
    se_b = math.sqrt(s2 * (1 / n + mx * mx / sxx))
    cov_mb = -mx * s2 / sxx
    return {"m": m, "b": b, "se_m": se_m, "se_b": se_b, "cov_mb": cov_mb, "rms": math.sqrt(sum(r * r for r in res) / n),
            "max_abs": max(abs(r) for r in res), "n": n, "res": res}


def x_at(fit, y):
    """x where the line reaches y, with a 1-sigma error from the fit covariance."""
    x = (y - fit["b"]) / fit["m"]
    dxdb, dxdm = -1 / fit["m"], -(y - fit["b"]) / fit["m"] ** 2
    var = dxdb ** 2 * fit["se_b"] ** 2 + dxdm ** 2 * fit["se_m"] ** 2 + 2 * dxdb * dxdm * fit["cov_mb"]
    return x, math.sqrt(max(var, 0.0))


def rms(v):
    v = list(v)
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


def group(evs, key):
    out = {}
    for e in evs:
        out.setdefault(key(e), []).append(e)
    return out


def cond(e):
    s = e["schedule"]
    if s.startswith("e3_right_k"):
        return "sprint right %d fps" % e["fps_set"]
    return {"e3_right_walk_k5": "walk right", "e3_right_slide350_k5": "slide right"}.get(
        s, "back" if s.startswith("e3_back") else "W re-tap" if s.startswith("e3_wtap") else s)


# ----------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    sessions = [load_session(f) for f in a.sessions]
    out = {"sessions": [], "events": []}
    evs = []
    print("=" * 100)
    print("1. DATA")
    for S in sessions:
        js = [t["join"] for t in S["trials"]]
        print("  %-34s fps %5s  trials %3d  parse errors %d  cmds %6d  joined %6d  state mismatches %d"
              % (S["folder"], S["client_fps"], len(S["trials"]), S["parse_errors"], sum(x["cmds"] for x in js),
                 sum(x["cmds_with_dt"] for x in js), sum(x["state_bad"] for x in js)))
        out["sessions"].append({"folder": S["folder"], "client_fps": S["client_fps"], "trials": len(S["trials"])})
        for t in S["trials"]:
            e = event(t)
            if e is None or e.get("bad"):
                print("    SKIP", t["label"], t["schedule"], e and e.get("bad"))
                continue
            evs.append(e)
    print("  press events: %d" % len(evs))

    # --- one command or spread
    print("=" * 100)
    print("2. IS THE LURCH ONE COMMAND?  max |v1 - AirAccelerate| on the other airborne commands of each jump")
    om = [e["other_resid_max"] for e in evs if e["other_resid_max"] is not None]
    print("  over %d jumps (%d commands): max %.4f u/s ; press command |D| range %.3f .. %.3f"
          % (len(om), sum(e["other_n"] for e in evs), max(om), min(e["D_len"] for e in evs), max(e["D_len"] for e in evs)))
    out["other_cmd_resid_max"] = max(om)
    dz = [e["dvz_resid"] for e in evs]
    print("  vertical: (vz - pvz) - 750*dt on the press command: %.4f .. %.4f u/s (dt printed to 1e-5 s)" % (min(dz), max(dz)))
    out["press_dvz_resid_range"] = [min(dz), max(dz)]

    # --- plateau table
    print("=" * 100)
    print("3. PRESS COMMAND, EARLY PRESSES (t < 0.20 s): D = v1 - (v0 + AirAccelerate), frame (vhat', n toward wish)")
    early = [e for e in evs if e["tA"] < 0.20]
    hdr = "  %-22s %3s %7s %7s %8s %8s %8s %8s %8s %8s %7s %7s"
    print(hdr % ("condition", "n", "theta", "s0", "s1", "D_par", "D_perp", "|D|", "lam", "a_user", "b_user", "head"))
    plateau = {}
    for k, g in sorted(group(early, cond).items()):
        f = lambda key: [e[key] for e in g if e[key] is not None]
        st = {key: L.stats(f(key)) for key in ("theta_deg", "s0", "s1", "D_par", "D_perp", "D_len", "lam", "a_user",
                                                "b_user", "heading_change_deg")}
        plateau[k] = st
        m = lambda key, nd=3: ("%.*f" % (nd, st[key]["mean"])) if st[key]["n"] else "-"
        print(hdr % (k, len(g), m("theta_deg", 2), m("s0", 2), m("s1", 2), m("D_par"), m("D_perp"), m("D_len"),
                     m("lam", 4), m("a_user", 4), m("b_user", 4), m("heading_change_deg", 2)))
    out["plateau"] = plateau
    lam_pl = [e["lam"] for e in early if e["lam"] is not None and e["theta_deg"] < 179 and e["theta_deg"] > 1]
    L_pl = [e["D_len"] for e in evs if e["clamped"]]
    LAM, LMAX = sum(lam_pl) / len(lam_pl), sum(L_pl) / len(L_pl)
    print("  lam (early, sideways presses)     = %s" % L.fmt(L.stats(lam_pl), 5))
    print("  |D| on every clamped press (any t) = %s" % L.fmt(L.stats(L_pl), 4))
    out["lam_plateau"], out["L_clamp"] = L.stats(lam_pl), L.stats(L_pl)

    # --- model comparison on early presses
    print("=" * 100)
    print("4. MODEL COMPARISON ON EARLY PRESSES: |v1_pred - v1_obs| (u/s); parameters fitted on 'sprint right 144 fps'")
    ref = [e for e in early if cond(e) == "sprint right 144 fps"]
    a_ref = sum(e["a_user"] for e in ref) / len(ref)
    b_ref = sum(e["b_user"] for e in ref) / len(ref)
    # slerp fraction from the reference set (target angle / theta)
    f_ref = []
    for e in ref:
        u = unit(e["_vp"])
        Dh = unit((e["_v1"][0] - e["_vp"][0], e["_v1"][1] - e["_vp"][1]))
        k = dot(e["_vp"], Dh)
        T = (e["_vp"][0] - 2 * k * Dh[0], e["_vp"][1] - 2 * k * Dh[1])
        f_ref.append(math.degrees(math.atan2(abs(cross(u, T)), dot(u, T))) / e["theta_deg"])
    f_ref = sum(f_ref) / len(f_ref)
    lam_ref = sum(e["lam"] for e in ref) / len(ref)
    L_ref = sum(e["D_len"] for e in ref) / len(ref)
    models = {
        "M0 AirAccelerate only (M2)": lambda e: e["_vp"],
        "M1 v1 = a*v' + b*|v'|*w  (a=%.4f b=%.4f)" % (a_ref, b_ref): lambda e: lurch_ab(e["_vp"], e["_w"], a_ref, b_ref),
        "M2 lerp(lam=%.4f) + clamp |D|<=%.3f" % (lam_ref, L_ref): lambda e: lurch_lerp(e["_vp"], e["_w"], lam_ref, L_ref),
        "M3 slerp(f=%.4f) + clamp |D|<=%.3f" % (f_ref, L_ref): lambda e: lurch_slerp(e["_vp"], e["_w"], f_ref, L_ref),
        "M2b as M2 but lurch BEFORE AirAccelerate": lambda e: air_accel(e["_c"], lurch_lerp(e["_v0"], e["_w"], lam_ref, L_ref)),
    }
    conds = sorted(group(early, cond))
    print("  %-46s" % "model" + "".join("%15s" % c[:15] for c in conds))
    mc = {}
    for name, fn in models.items():
        row = {}
        for c in conds:
            g = [e for e in early if cond(e) == c]
            r = [norm((fn(e)[0] - e["_v1"][0], fn(e)[1] - e["_v1"][1])) for e in g]
            row[c] = {"rms": rms(r), "max": max(r)}
        mc[name] = row
        print("  %-46s" % name[:46] + "".join("%15.3f" % row[c]["max"] for c in conds))
    print("  (max error per condition; rms in results.json)")
    out["model_comparison_early"] = mc
    out["ref_params"] = {"a": a_ref, "b": b_ref, "slerp_f": f_ref, "lam": lam_ref, "L": L_ref}

    # --- window
    print("=" * 100)
    print("5. WINDOW: lam vs time since the jump command (sideways presses, sprint)")
    side = [e for e in evs if e["schedule"].startswith("e3_right_k")]
    for e in sorted(side, key=lambda e: (e["fps_set"], e["tA"])):
        print("  %3d fps  run %4d  k-cmds %3d  tA %.4f s  dt %.5f  |D| %7.3f  clamp %d  s1/s0 %.4f  head %6.2f  lam %.4f"
              % (e["fps_set"], e["run"], e["n_cmds"], e["tA"], e["dt_press"], e["D_len"], e["clamped"], e["ratio"],
                 e["heading_change_deg"], e["lam"]))
    # fade points: strictly between the plateau and zero
    lam_sd = L.stats(lam_pl)["sd"]
    fade = [e for e in side if 0.001 < e["lam"] < LAM - 5 * max(lam_sd, 1e-4)]
    print("  fade points: 0.001 < lam < lam_plateau - 5 sd  ->  n = %d" % len(fade))
    win = {}
    for conv, off in (("tA (start jump cmd -> start press cmd)", 0), ("tA + dt (-> end of press cmd)", 1),
                      ("tA - dt (end of jump cmd -> start press cmd)", -1)):
        win[conv] = {}
        print("  convention: %s" % conv)
        for key, g in sorted(group(fade, lambda e: e["fps_set"]).items()) + [("all", fade)]:
            xs = [e["tA"] + off * e["dt_mean"] for e in g]
            ys = [e["lam"] for e in g]
            f = lin_fit(xs, ys)
            t0, t0e = x_at(f, LAM)
            t1, t1e = x_at(f, 0.0)
            win[conv][str(key)] = {"slope": f["m"], "se_slope": f["se_m"], "t_plateau_end": t0, "se_t_plateau_end": t0e,
                                   "t_zero": t1, "se_t_zero": t1e, "rms": f["rms"], "max_abs": f["max_abs"], "n": f["n"]}
            print("    %-4s n=%2d  slope %8.4f /s (se %.4f)  plateau end %.4f s (se %.4f)  zero %.4f s (se %.4f)  rms %.4f max %.4f"
                  % (key, f["n"], f["m"], f["se_m"], t0, t0e, t1, t1e, f["rms"], f["max_abs"]))
    out["window_fits"] = win
    # brackets from the sampled points themselves (no fit)
    print("  brackets from samples (tA):")
    br = {}
    for key, g in sorted(group(side, lambda e: e["fps_set"]).items()):
        full = [e["tA"] for e in g if e["lam"] >= LAM - 5 * max(lam_sd, 1e-4)]
        part = [e["tA"] for e in g if 0.001 < e["lam"] < LAM - 5 * max(lam_sd, 1e-4)]
        zero = [e["tA"] for e in g if e["lam"] <= 0.001]
        br[str(key)] = {"last_full": max(full) if full else None, "first_partial": min(part) if part else None,
                        "last_partial": max(part) if part else None, "first_zero": min(zero) if zero else None}
        print("    %3d fps: last full %.4f | first partial %s | last partial %s | first zero %s"
              % (key, max(full), "%.4f" % min(part) if part else "-", "%.4f" % max(part) if part else "-",
                 "%.4f" % min(zero) if zero else "-"))
    out["window_brackets"] = br
    # frames vs seconds: zero crossing in commands per fps
    print("  same zero crossing expressed in commands (fit 'tA' per fps / mean dt):")
    for key, g in sorted(group(fade, lambda e: e["fps_set"]).items()):
        dtm = sum(e["dt_mean"] for e in g) / len(g)
        w = win["tA (start jump cmd -> start press cmd)"][str(key)]
        print("    %3d fps: dt %.5f s  plateau end %.1f cmds  zero %.1f cmds" % (key, dtm, w["t_plateau_end"] / dtm,
                                                                               w["t_zero"] / dtm))
    # --- full model over all presses with the fitted window
    wa = win["tA (start jump cmd -> start press cmd)"]["all"]
    t_pl, t_z = wa["t_plateau_end"], wa["t_zero"]

    def lam_t(t):
        if t <= t_pl:
            return LAM
        if t >= t_z:
            return 0.0
        return LAM * (t_z - t) / (t_z - t_pl)

    full = {}
    for label, P in (("fitted", (LAM, t_pl, t_z, LMAX)), ("rounded", (0.7, 0.2, 0.5, 209.3))):
        lam0, ta, tb, Lm = P

        def lam_r(t, lam0=lam0, ta=ta, tb=tb):
            return lam0 if t <= ta else 0.0 if t >= tb else lam0 * (tb - t) / (tb - ta)

        print("=" * 100)
        print("6%s. FULL MODEL ON EVERY PRESS, %s parameters: lam=%.4f until %.4f s, linear to 0 at %.4f s, clamp %.3f"
              % ("a" if label == "fitted" else "b", label, lam0, ta, tb, Lm))
        full[label] = {"params": P}
        for c, g in sorted(group(evs, cond).items()):
            r = []
            for e in g:
                pr = lurch_lerp(e["_vp"], e["_w"], lam_r(e["tA"]), Lm)
                r.append(norm((pr[0] - e["_v1"][0], pr[1] - e["_v1"][1])))
            r0 = [norm((e["_vp"][0] - e["_v1"][0], e["_vp"][1] - e["_v1"][1])) for e in g]
            full[label][c] = {"n": len(g), "rms": rms(r), "max": max(r), "rms_M0": rms(r0)}
            print("  %-22s n=%2d  rms %.3f  max %.3f u/s   (AirAccelerate only: rms %.3f)" % (c, len(g), rms(r), max(r), rms(r0)))
    out["full_model"] = full
    print("  time offset implied by each fade sample under the rounded window, (0.5 - lam/(0.7/0.3)) - tA, in ms:")
    offs = {}
    for key, g in sorted(group(fade, lambda e: e["fps_set"]).items()):
        o = [((0.5 - e["lam"] / (0.7 / 0.3)) - e["tA"]) * 1000 for e in g]
        offs[str(key)] = L.stats(o)
        print("    %3d fps: %s" % (key, L.fmt(L.stats(o), 3)))
    out["fade_time_offset_ms"] = offs
    print("  slide trials: speed before the jump (max), jump pre/post speed, press s0:")
    for e in [e for e in evs if cond(e) == "slide right"]:
        print("    run %d: max %.2f  jump cmd %.2f -> %.2f  press %.2f" % (e["run"], e["s_max_before_jump"], e["jump_s_pre"],
                                                                         e["jump_s_post"], e["s0"]))

    # --- back / W re-tap
    print("=" * 100)
    print("7. BACK AND W RE-TAP")
    for c in ("back", "W re-tap"):
        for e in [e for e in evs if cond(e) == c]:
            pr = lurch_lerp(e["_vp"], e["_w"], lam_t(e["tA"]), LMAX)
            print("  %-8s run %4d tA %.4f theta %6.2f  s0 %.2f -> s1 %.2f (pred %.2f)  heading %.3f  |D| %.3f"
                  % (c, e["run"], e["tA"], e["theta_deg"], e["s0"], e["s1"], norm(pr), e["heading_change_deg"], e["D_len"]))

    # --- parity
    print("=" * 100)
    print("8. CLIENT / DEDI PARITY ON THE PRESS COMMAND")
    sd = [e for e in evs if e["sv_diff"] is not None]
    bad = [e for e in sd if e["sv_diff"] > TOL]
    print("  dedi MT present %d/%d; identical within %.3f: %d; different: %d" % (len(sd), len(evs), TOL, len(sd) - len(bad), len(bad)))
    for e in bad:
        print("    run %d %s tA %.4f: max diff %.3f  client |D| %.3f  dedi |D| %.3f" % (e["run"], e["schedule"], e["tA"],
                                                                                    e["sv_diff"], e["D_len"], e["sv_D_len"]))
    rpn = [e for e in evs if e["rp_n"]]
    print("  client replays (rp=1) of the press command: %d events; max diff to first-time %s"
          % (len(rpn), "%.3f" % max(max(e["rp_diff"]) for e in rpn) if rpn else "-"))
    cr = [(e["run"], e["corrections_rel_j"]) for e in evs if e["corrections_rel_j"]]
    print("  client state discontinuities between jump-2 and landing+1 (cmd index rel. jump): %s" % (cr or "none"))
    out["parity"] = {"n": len(sd), "different": [{"run": e["run"], "tA": e["tA"], "diff": e["sv_diff"], "cl_D": e["D_len"],
                                                  "sv_D": e["sv_D_len"]} for e in bad],
                     "replays_of_press": len(rpn), "discontinuities": cr}
    rep = {}
    for k, g in sorted(group(evs, lambda e: (e["schedule"], e["fps_set"])).items()):
        if len(g) > 1:
            rep["%s@%d" % k] = {"n": len(g), "D_len": L.stats([e["D_len"] for e in g]), "lam": L.stats([e["lam"] for e in g]),
                                "tA": L.stats([e["tA"] for e in g])}
    out["repeatability"] = rep
    print("=" * 100)
    print("9. REPEATABILITY (same schedule and fps): spread of |D|, lam and tA")
    for k, v in rep.items():
        print("  %-26s n=%d  |D| %s  lam sd %s  tA range %.4f s" % (k, v["n"], L.fmt(v["D_len"], 3),
                                                                     "%.5f" % v["lam"]["sd"] if v["lam"]["n"] else "- (undefined, w = -v)",
                                                                     v["tA"]["max"] - v["tA"]["min"]))
    out["events"] = [{k: v for k, v in e.items() if not k.startswith("_")} for e in evs]
    out["chosen"] = {"lam_plateau": LAM, "L": LMAX, "t_plateau_end": t_pl, "t_zero": t_z}
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
