#!/usr/bin/env python3
"""M6-A1 lurch stacking / tap strafe analysis (Apex R5Flowstate S21, 120 fps, Gibraltar, movescale 1.15).

    py -3 a1_lurch_analysis.py <session folder> [<session folder> ...] [--json results.json] [--params params.json]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). Only trials with ok=true and
warmup=false are used; every a1_* schedule and the e6_bounce_none_15 control are analysed.

Physics truth: client first-time MOVE-TRACE commands (side cl, rp=0). dt and view yaw per command come from the client
HSD frame that shows the command's post-state (M2 join, ../../m2/air_jump/aj_load.py, validated per command). The dedi
MOVE-TRACE row of the same usercmd is used for parity. The M3 lurch model and the M2 AirAccelerate are imported from
../../m3/lurch/lurch_analysis.py unchanged.

Per airborne command (pre-state and post-state airborne, not a jump command) the model predicts the post horizontal
velocity from the observed pre-state, buttons, yaw and dt:
    v' = v + AirAccelerate(v)                                     (M2: 500*dt, wish cap 60*movescale)
    if new bits in buttons & 0x618:  v' = lurch(v', wishdir, lam(t), 209.3)       (M3 sec. 8)
    t = sum of dt from the start of the anchor jump command to the start of this command
The anchor is the latest jump command (IN_JUMP press with a grounded / wall-contact pre-state and an airborne
post-state): the ground jump, the slide jump or the wall-bounce jump. Alternatives are computed with the same code and
printed side by side. Everything printed is computed here; nothing is tuned to pass. stdlib only, no local paths.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m3", "lurch")))
import lurch_analysis as LA  # noqa: E402  (puts aj_load and hsdtel on sys.path)
L = LA.L
from hsdtel import derive, parse  # noqa: E402

MASK = 0x618
BITS = {"F": 0x8, "B": 0x10, "L": 0x200, "R": 0x400}
IN_JUMP = 0x2
LMAX = 209.3
LAM_MAX, T_FULL, T_ZERO = 0.7, 0.2, 0.5
TOL = 0.002
K6 = ("ox", "oy", "oz", "vx", "vy", "vz")
P6 = ("pox", "poy", "poz", "pvx", "pvy", "pvz")
norm, unit, dot, cross = LA.norm, LA.unit, LA.dot, LA.cross


# ----------------------------------------------------------------------------- loading
def load_session(folder):
    files, rows, issues = parse.parse_inputs([os.path.join(folder, "platform", "logs")])
    derive.derive(rows)
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    plat = L._plat_index(files)
    for r in rows:
        r["plat"] = plat.get((r.get("session"), r.get("file"), r.get("line_no")))
    cl, fr, sv = {}, {}, {}
    for r in rows:
        run = r.get("drv_run")
        if r["source"] == "MT" and not r.get("replay"):
            (cl if r.get("side") == "cl" else sv).setdefault(run, []).append(r)
        elif r["source"] == "HSD" and r.get("side") == "cl" and r.get("kind") == "frame":
            fr.setdefault(run, []).append(r)
    trials, skipped = [], []
    for t in runner["trials"]:
        if t.get("warmup") or not t.get("ok"):
            skipped.append((t["run"], t.get("schedule"), "warmup" if t.get("warmup") else "ok=false: %s" % t.get("why")))
            continue
        lab = "r%d" % t["run"]
        cmds = sorted(cl.get(lab, []), key=lambda r: r["cmd"])
        frames = sorted([f for f in fr.get(lab, []) if f.get("plat") is not None], key=lambda r: r["plat"])
        st = L.join(cmds, frames)
        trials.append({"session": os.path.basename(os.path.normpath(folder)), "run": t["run"], "schedule": t["schedule"],
                       "fps": t.get("measured_fps"), "cmds": cmds, "join": st,
                       "sv": {r["cmd"]: r for r in sv.get(lab, [])}})
    return {"folder": os.path.basename(os.path.normpath(folder)), "client_fps": runner.get("client_fps"),
            "census": runner.get("census"), "trials": trials, "skipped": skipped,
            "parse_errors": sum(1 for i in issues if i.severity == "error")}


# ----------------------------------------------------------------------------- model pieces
def lam_t(t):
    return LAM_MAX * min(1.0, max(0.0, (T_ZERO - t) / (T_ZERO - T_FULL)))


def wish_raw(c, yaw):
    """Unnormalized key vector (fwd/side are +-0.5 on the press command, +-1 when held)."""
    r = math.radians(yaw)
    f, rt = (math.cos(r), math.sin(r)), (math.sin(r), -math.cos(r))
    return (c["fwd"] * f[0] + c["sidemove"] * rt[0], c["fwd"] * f[1] + c["sidemove"] * rt[1])


def wish_unit(c, yaw):
    return unit(wish_raw(c, yaw))


def air_accel(c, v, yaw):
    cc = dict(c)
    cc["yaw"] = yaw
    return LA.air_accel(cc, v)


def lurch_vec(v, wvec, lam, lmax):
    """M3 lerp with a free (possibly non-unit) wish vector; with a unit wishdir this is LA.lurch_lerp."""
    s, u = norm(v), unit(v)
    if u is None or lam <= 0 or wvec is None:
        return v, 0.0
    d = unit(((1 - lam) * u[0] + lam * wvec[0], (1 - lam) * u[1] + lam * wvec[1]))
    if d is None:
        return v, 0.0
    D = (s * d[0] - v[0], s * d[1] - v[1])
    n = norm(D)
    if lmax is not None and n > lmax:
        D = (D[0] * lmax / n, D[1] * lmax / n)
    return (v[0] + D[0], v[1] + D[1]), norm(D)


def keys(bits):
    return "".join(k for k, b in BITS.items() if bits & b) or "-"


# ----------------------------------------------------------------------------- per-trial walk
def walk(t):
    """Classify commands, find jump anchors and presses, compute one-step predictions for every model variant."""
    cs = t["cmds"]
    n = len(cs)
    jumps = [i for i in range(1, n - 1) if cs[i]["ground"] == 1 and (cs[i]["buttons"] & IN_JUMP)
             and not (cs[i - 1]["buttons"] & IN_JUMP) and cs[i + 1]["ground"] == 0]
    out = {"jumps": jumps, "air": []}
    if not jumps:
        return out
    j0 = jumps[0]
    budget = {}   # per anchor: cumulative |D| used (for the cumulative-clamp alternative)
    seen = {}     # per anchor: presses seen (for the one-lurch-per-jump alternative)
    for i in range(j0 + 1, n - 1):
        c = cs[i]
        if c["ground"] != 0 or cs[i + 1]["ground"] != 0 or i in jumps:
            continue
        anc = max(a for a in jumps if a < i)
        if c["dt"] is None or c["yaw"] is None or any(cs[k]["dt"] is None for k in range(anc, i)):
            continue
        tA = sum(cs[k]["dt"] for k in range(anc, i))
        t0 = sum(cs[k]["dt"] for k in range(j0, i))
        tf = (cs[i - 1].get("t") - cs[anc - 1].get("t")) if (cs[i - 1].get("t") is not None and cs[anc - 1].get("t") is not None) else None
        new = (c["buttons"] & MASK) & ~(cs[i - 1]["buttons"] & MASK)
        yaw = c["yaw"]
        yaw_prev = cs[i - 1]["yaw"] if cs[i - 1]["yaw"] is not None else yaw
        v0 = (c["vx"], c["vy"])
        v1 = (c["pvx"], c["pvy"])
        w = wish_unit(c, yaw)
        vp = air_accel(c, v0, yaw)
        rec = {"i": i, "anchor": anc, "anchor_k": jumps.index(anc), "t": tA, "t_frame": tf, "t_first_jump": t0, "new": new,
               "held": c["buttons"] & MASK, "yaw": yaw, "fwd": c["fwd"], "side": c["sidemove"], "dt": c["dt"],
               "v0": v0, "v1": v1, "vp": vp, "s_pre": norm(v0), "s_aa": norm(vp), "s1": norm(v1),
               "head0": math.degrees(math.atan2(v0[1], v0[0])), "head1": math.degrees(math.atan2(v1[1], v1[0]))}
        pred = {}
        lam = lam_t(tA)
        if new and w is not None:
            pred["M3"], rec["D_model"] = lurch_vec(vp, w, lam, LMAX)
            pred["aa_only"] = vp
            pred["t_from_first_jump"] = lurch_vec(vp, w, lam_t(t0), LMAX)[0]
            k = seen.get(anc, 0)
            pred["once_per_jump"] = lurch_vec(vp, w, lam, LMAX)[0] if k == 0 else vp
            left = max(0.0, LMAX - budget.get(anc, 0.0))
            pc, used = lurch_vec(vp, w, lam, left)
            pred["cumulative_clamp"] = pc
            budget[anc] = budget.get(anc, 0.0) + used
            seen[anc] = k + 1
            wp = wish_unit(c, yaw_prev)
            pred["yaw_prev_frame"] = lurch_vec(air_accel(c, v0, yaw_prev), wp, lam, LMAX)[0]
            pred["wish_raw_keys"] = lurch_vec(vp, wish_raw(c, yaw), lam, LMAX)[0]
            sgn = (math.copysign(1, c["fwd"]) if c["fwd"] else 0.0, math.copysign(1, c["sidemove"]) if c["sidemove"] else 0.0)
            cc = dict(c, fwd=sgn[0], sidemove=sgn[1])
            pred["wish_sign_keys"] = lurch_vec(vp, wish_raw(cc, yaw), lam, LMAX)[0]
            pred["lurch_before_aa"] = air_accel(c, lurch_vec(v0, w, lam, LMAX)[0], yaw)
            pred["no_clamp"] = lurch_vec(vp, w, lam, None)[0]
            rec["press_k"] = k
            rec["lam_model"] = lam
            rec["keys"] = keys(new)
            # observed lurch term and recovered lambda (M3 sec. 3.2 method)
            D = (v1[0] - vp[0], v1[1] - vp[1])
            u = unit(vp)
            rec["D_obs"] = norm(D)
            rec["theta"] = math.degrees(math.acos(max(-1.0, min(1.0, dot(u, w))))) if u else None
            rec["clamped_obs"] = (norm(vp) - norm(v1)) > 0.01
            if norm(D) < 0.01:
                rec["lam_obs"] = 0.0
            else:
                if rec["clamped_obs"]:
                    Dh = unit(D)
                    kk = dot(vp, Dh)
                    T = (vp[0] - 2 * kk * Dh[0], vp[1] - 2 * kk * Dh[1])
                else:
                    T = v1
                rec["lam_obs"] = LA.lam_of(u, w, unit(T)) if rec["theta"] and rec["theta"] > 0.3 else None
            rec["gap_before"] = angdiff(yaw_of(w), rec["head0"]) if w else None
            rec["gap_after"] = angdiff(yaw_of(w), rec["head1"]) if w else None
        else:
            pred["M3"] = vp
        rec["res"] = {k: math.hypot(v1[0] - p[0], v1[1] - p[1]) for k, p in pred.items()}
        sv = t["sv"].get(c["cmd"])
        if sv:
            rec["sv_diff"] = max(abs(sv[q] - c[q]) for q in K6 + P6)
            rec["sv_dvh"] = max(abs(sv[q] - c[q]) for q in ("vx", "vy", "pvx", "pvy"))
            rec["sv_contact"] = abs(sv["pvz"] - c["pvz"]) > 1.0 or abs(sv["vz"] - c["vz"]) > 1.0
            svv0 = (sv["vx"], sv["vy"])
            svp = air_accel(c, svv0, yaw)
            if new and w is not None:
                svp = lurch_vec(svp, w, lam, LMAX)[0]
            rec["sv_res"] = math.hypot(sv["pvx"] - svp[0], sv["pvy"] - svp[1])
        out["air"].append(rec)
    return out


def yaw_of(u):
    return math.degrees(math.atan2(u[1], u[0]))


def angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def closed_loop(t, w):
    """Integrate the chosen model from the post-state of each anchor jump through the following airborne commands,
    using only the observed buttons / yaw / dt; stop at the first non-airborne command. Returns per anchor the
    final horizontal velocity error."""
    cs = t["cmds"]
    out = []
    byi = {r["i"]: r for r in w["air"]}
    for a in w["jumps"]:
        v = (cs[a]["pvx"], cs[a]["pvy"])
        i = a + 1
        last = None
        err_max = 0.0
        while i in byi:
            r = byi[i]
            c = cs[i]
            vp = air_accel(c, v, r["yaw"])
            if r["new"]:
                wu = wish_unit(c, r["yaw"])
                vp = lurch_vec(vp, wu, lam_t(r["t"]), LMAX)[0] if wu else vp
            v = vp
            e = math.hypot(v[0] - r["v1"][0], v[1] - r["v1"][1])
            err_max = max(err_max, e)
            last = (i, e)
            i += 1
        if last:
            out.append({"anchor": a, "n": last[0] - a, "err_end": last[1], "err_max": err_max})
    return out


def simulate_ts(s0, rate, dt=1.0 / 120, msc=1.15, maxspeed=199.525):
    """Chosen model, forward taps on every second command from command 4 (fwd 0.5), yaw turning at -rate deg/s."""
    v = (s0, 0.0)
    out = {"clamped": 0}
    yaw = 0.0
    head = 0.0  # unwrapped heading of v
    for k in range(4, 61):
        t = k * dt
        yaw = -rate * (t - 4 * dt + dt / 2)
        if k % 2 == 0:
            c = {"fwd": 0.5, "sidemove": 0.0, "maxspeed": maxspeed, "movescale": msc, "dt": dt}
            vp = air_accel(c, v, yaw)
            vn, dl = lurch_vec(vp, wish_unit(c, yaw), lam_t(t), LMAX)
            head += math.degrees(math.atan2(cross(v, vn), dot(v, vn)))
            v = vn
            out["clamped"] += dl > LMAX - 1e-6
        if k == 32:
            out["dh_267"], out["dyaw_267"], out["s_267"] = head, yaw, norm(v)
    out["dh_end"], out["dyaw_end"], out["s_end"] = head, yaw, norm(v)
    return out


# ----------------------------------------------------------------------------- report helpers
def st(vals):
    return L.stats([v for v in vals if v is not None])


def f3(s, nd=3):
    return L.fmt(s, nd)


def mx(vals):
    vals = [v for v in vals if v is not None]
    return max(vals) if vals else float("nan")


CONDS = ["a1_rr_n6", "a1_rr_n12", "a1_rr_n24", "a1_rrr_n6", "a1_lr_n12", "a1_shift", "a1_diag_fr", "a1_diag_br",
         "a1_ts_360", "a1_ts_180", "a1_ts_noturn", "a1_turn_only", "a1_turn_hold_w", "a1_sj_ts_360",
         "a1_wb_lurch3", "a1_wb_lurch30", "e6_bounce_none_15"]
VARIANTS = ["M3", "aa_only", "once_per_jump", "cumulative_clamp", "no_clamp", "t_from_first_jump", "yaw_prev_frame",
            "wish_raw_keys", "wish_sign_keys", "lurch_before_aa"]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    sessions = [load_session(f) for f in a.sessions]
    R = {"sessions": [], "conditions": {}, "presses": [], "tap_strafe": [], "closed_loop": [], "parity": {}}
    trials = []
    print("=" * 110)
    print("1. DATA")
    for S in sessions:
        js = [t["join"] for t in S["trials"]]
        print("  %-30s fps %5s  scored trials %3d  parse errors %d  cmds %6d  joined %6d  state mismatches %d  census %s"
              % (S["folder"], S["client_fps"], len(S["trials"]), S["parse_errors"], sum(x["cmds"] for x in js),
                 sum(x["cmds_with_dt"] for x in js), sum(x["state_bad"] for x in js), bool(S["census"])))
        for s in S["skipped"]:
            print("    not scored: r%d %s (%s)" % s)
        R["sessions"].append({"folder": S["folder"], "client_fps": S["client_fps"], "trials": len(S["trials"]),
                              "skipped": [list(s) for s in S["skipped"]]})
        trials += S["trials"]
    W = {}
    for t in trials:
        W[(t["session"], t["run"])] = walk(t)
    bycond = {}
    for t in trials:
        bycond.setdefault(t["schedule"], []).append(t)
    print("  trials per condition: " + ", ".join("%s %d" % (c, len(bycond.get(c, []))) for c in CONDS))
    other = sorted(set(bycond) - set(CONDS))
    if other:
        print("  other schedules (not analysed):", other)

    # ------------------------------------------------------------------ 2. one-step residuals
    print("=" * 110)
    print("2. ONE-STEP RESIDUALS |v1_obs - v1_pred| (u/s, horizontal) on airborne commands, per condition")
    print("   non-press = airborne commands without a new 0x618 bit (model = M2 AirAccelerate only)")
    hdr = "  %-18s %3s %6s %9s %7s | %7s" + " %9s" * len(VARIANTS)
    print(hdr % tuple(["condition", "n", "nonpr", "nonpr max", ">0.01", "press"] + VARIANTS))
    for cnd in CONDS:
        ts = bycond.get(cnd, [])
        recs = [r for t in ts for r in W[(t["session"], t["run"])]["air"]]
        npr = [r for r in recs if not r["new"]]
        pr = [r for r in recs if r["new"]]
        row = [cnd, len(ts), len(npr), mx(r["res"]["M3"] for r in npr), sum(1 for r in npr if r["res"]["M3"] > 0.01), len(pr)]
        row += [mx(r["res"].get(v) for r in pr) for v in VARIANTS]
        print(("  %-18s %3d %6d %9.4f %7d | %7d" + " %9.3f" * len(VARIANTS)) % tuple(row))
        R["conditions"][cnd] = {"trials": len(ts), "nonpress_n": len(npr), "nonpress_max": row[3],
                                "nonpress_over_0.01": row[4], "press_n": len(pr),
                                "press_max_by_variant": dict(zip(VARIANTS, row[6:]))}
    print("  Non-press commands with residual > 0.01 (contact with the wall etc.), first 3 per condition:")
    for cnd in CONDS:
        shown = 0
        for t in bycond.get(cnd, []):
            for r in W[(t["session"], t["run"])]["air"]:
                if not r["new"] and r["res"]["M3"] > 0.01 and shown < 3:
                    print("    %-18s r%d i-anchor %3d t %.3f  res %.3f  s %.2f -> %.2f  held %s" % (
                        cnd, t["run"], r["i"] - r["anchor"], r["t"], r["res"]["M3"], r["s_pre"], r["s1"], keys(r["held"])))
                    shown += 1

    # ------------------------------------------------------------------ 3. every press
    print("=" * 110)
    print("3. EVERY PRESS-EDGE COMMAND (grouped by condition and press index k within the jump; mean over trials)")
    print("   t = s since the anchor jump; theta = angle(v', wishdir); |D|obs = |v1 - v'|; lam_obs from M3 sec 3.2;")
    print("   res = |v1_obs - v1_M3|; spread = max-min of |D|obs over trials")
    h3 = "  %-16s %2s %-3s %2s %6s %7s %8s %8s %8s %8s %6s %7s %7s %8s %8s"
    print(h3 % ("condition", "k", "key", "n", "t", "theta", "s'", "s1", "|D|obs", "|D|mod", "clamp", "lam_ob", "lam_md",
                "res max", "spread"))
    for cnd in CONDS:
        g = {}
        for t in bycond.get(cnd, []):
            for r in W[(t["session"], t["run"])]["air"]:
                if r["new"]:
                    g.setdefault((r["anchor_k"], r["press_k"]), []).append((t, r))
                    R["presses"].append({"session": t["session"], "run": t["run"], "condition": cnd,
                                         "anchor_k": r["anchor_k"], "press_k": r["press_k"], "keys": r["keys"],
                                         "t": r["t"], "t_frame": r["t_frame"], "t_first_jump": r["t_first_jump"], "theta": r["theta"],
                                         "fwd": r["fwd"], "side": r["side"], "yaw": r["yaw"],
                                         "s_pre": r["s_pre"], "s_aa": r["s_aa"], "s1": r["s1"],
                                         "head0": r["head0"], "head1": r["head1"], "D_obs": r["D_obs"],
                                         "D_model": r["D_model"], "clamped_obs": r["clamped_obs"],
                                         "lam_obs": r["lam_obs"], "lam_model": r["lam_model"],
                                         "res": r["res"], "sv_diff": r.get("sv_diff"), "sv_res": r.get("sv_res")})
        for (ak, k), lst in sorted(g.items()):
            rs = [r for _, r in lst]
            m = lambda key: sum(r[key] for r in rs if r[key] is not None) / max(1, sum(1 for r in rs if r[key] is not None))
            lo = [r["lam_obs"] for r in rs if r["lam_obs"] is not None]
            print(h3 % (cnd if ak == 0 else cnd + "/b%d" % ak, k, rs[0]["keys"], len(rs), "%.3f" % m("t"),
                        "%.1f" % m("theta"), "%.2f" % m("s_aa"), "%.2f" % m("s1"), "%.3f" % m("D_obs"),
                        "%.3f" % m("D_model"), "%d/%d" % (sum(r["clamped_obs"] for r in rs), len(rs)),
                        ("%.4f" % (sum(lo) / len(lo))) if lo else "-", "%.4f" % m("lam_model"),
                        "%.3f" % max(r["res"]["M3"] for r in rs), "%.3f" % (max(r["D_obs"] for r in rs) - min(r["D_obs"] for r in rs))))
    pr_all = [p for p in R["presses"]]
    print("  all presses: n %d ; M3 residual %s" % (len(pr_all), f3(st(p["res"]["M3"] for p in pr_all), 4)))
    cl = [p["D_obs"] for p in pr_all if p["clamped_obs"]]
    print("  clamped presses |D|obs: %s" % f3(st(cl), 4))
    lamr = [p["lam_obs"] - p["lam_model"] for p in pr_all if p["lam_obs"] is not None and p["theta"] and p["theta"] > 2]
    print("  lam_obs - lam_model (theta > 2 deg): %s" % f3(st(lamr), 5))
    full = [p["lam_obs"] for p in pr_all if p["lam_obs"] is not None and p["t"] < 0.195 and p["theta"] and p["theta"] > 2]
    print("  lam_obs on presses with t < 0.195 s, theta > 2 deg: %s" % f3(st(full), 5))
    unc = [p for p in pr_all if not p["clamped_obs"] and p["D_obs"] > 0.01]
    print("  unclamped lurches: speed change s1 - s' = %s (model: 0)" % f3(st(p["s1"] - p["s_aa"] for p in unc), 4))
    fade = [p for p in pr_all if p["lam_obs"] is not None and 0.01 < p["lam_obs"] < 0.69 and p["theta"] and p["theta"] > 2]
    off = [T_ZERO - p["lam_obs"] * (T_ZERO - T_FULL) / LAM_MAX - p["t"] for p in fade]
    offf = [T_ZERO - p["lam_obs"] * (T_ZERO - T_FULL) / LAM_MAX - p["t_frame"] for p in fade if p["t_frame"] is not None]
    print("  FADE CLOCK (presses with 0.01 < lam_obs < 0.69): implied t from lam_obs minus measured t, in ms")
    print("    sum-of-dt clock: %s" % f3(st(o * 1000 for o in off), 3))
    print("    client frame-time clock (frame t before the press - frame t before the jump): %s" % f3(st(o * 1000 for o in offf), 3))
    by = {}
    for p, o in zip(fade, off):
        by.setdefault(p["condition"], []).append(o * 1000)
    print("    by condition (sum-of-dt): " + "; ".join("%s %.2f (n %d)" % (k, sum(v) / len(v), len(v)) for k, v in sorted(by.items())))
    sh = (sum(off) / len(off)) if off else 0.0
    rs_sh = [abs(lam_t(p["t"] + sh) - p["lam_obs"]) for p in fade]
    print("    |lam_obs - lam_model| on fade presses: as is %s ; with t shifted by the mean %.2f ms %s" % (
        f3(st(abs(p["lam_obs"] - p["lam_model"]) for p in fade), 5), sh * 1000, f3(st(rs_sh), 5)))
    R["fade_clock"] = {"n": len(fade), "offset_ms_sumdt": st(o * 1000 for o in off),
                       "offset_ms_frame_t": st(o * 1000 for o in offf), "by_condition_ms": {k: sum(v) / len(v) for k, v in by.items()}}
    R["press_summary"] = {"n": len(pr_all), "res_M3": st(p["res"]["M3"] for p in pr_all), "clamped_D": st(cl),
                          "lam_res": st(lamr), "lam_full": st(full),
                          "unclamped_speed_gain": st(p["s1"] - p["s_aa"] for p in unc)}

    # ------------------------------------------------------------------ 4. stacking
    print("=" * 110)
    print("4. STACKING: every press vs the M3 model applied independently per press (t from the jump)")
    print("   'once' = only the first press per jump lurches; 'cum' = one 209.3 budget per jump shared by its presses")
    for cnd in ["a1_rr_n6", "a1_rr_n12", "a1_rr_n24", "a1_rrr_n6", "a1_lr_n12", "a1_shift"]:
        rs = [p for p in R["presses"] if p["condition"] == cnd]
        later = [p for p in rs if p["press_k"] > 0]
        print("  %-10s presses %2d (later %2d): later |D|obs %s ; res max  M3 %.3f  once %.3f  cum %.3f  aa_only %.3f"
              % (cnd, len(rs), len(later), f3(st(p["D_obs"] for p in later), 2), mx(p["res"]["M3"] for p in rs),
                 mx(p["res"]["once_per_jump"] for p in rs), mx(p["res"]["cumulative_clamp"] for p in rs),
                 mx(p["res"]["aa_only"] for p in rs)))
        both = {}
        for p in rs:
            both.setdefault(p["run"], []).append(p)
        tot = [sum(q["D_obs"] for q in v) for v in both.values()]
        ncl = [sum(1 for q in v if q["clamped_obs"]) for v in both.values()]
        print("             per jump: sum |D| %s ; clamped presses per jump %s" % (f3(st(tot), 2), sorted(set(ncl))))

    # ------------------------------------------------------------------ 5. tap strafe
    print("=" * 110)
    print("5. TAP STRAFE / TURN CONTROLS: heading of v vs view yaw across the 30-command input window")
    print("   window = jump+4 .. jump+34 (the 15 W edges, 2 commands apart); dyaw = view turn; dhead = velocity turn;")
    print("   lag = yaw - heading at window end; s_end/s_start speed ratio; dhead@land = heading change jump->landing")
    h5 = "  %-15s %5s %7s %7s %7s %7s %8s %8s %9s %10s"
    print(h5 % ("condition", "run", "dyaw", "dhead", "lag", "s_start", "s_end", "ratio", "|D|max", "dhead@land"))
    tsum = {}
    for cnd in ["a1_ts_360", "a1_ts_180", "a1_ts_noturn", "a1_turn_only", "a1_turn_hold_w", "a1_sj_ts_360"]:
        for t in bycond.get(cnd, []):
            w = W[(t["session"], t["run"])]
            cs = t["cmds"]
            j = w["jumps"][0]
            byi = {r["i"]: r for r in w["air"]}
            i0, i1 = j + 4, j + 33
            if i0 not in byi or i1 not in byi:
                print("  %-15s r%d  window not fully airborne/joined" % (cnd, t["run"]))
                continue
            r0, r1 = byi[i0], byi[i1]
            dyaw = angdiff(r1["yaw"], cs[i0 - 1]["yaw"])
            dhead = angdiff(r1["head1"], r0["head0"])
            lag = angdiff(r1["yaw"], r1["head1"])
            last = max(byi)
            dland = angdiff(byi[last]["head1"], r0["head0"])
            dmax = mx(byi[i]["D_obs"] for i in range(i0, i1 + 1) if byi[i]["new"])
            row = {"condition": cnd, "run": t["run"], "dyaw": dyaw, "dhead": dhead, "lag": lag, "s_start": r0["s_pre"],
                   "s_end": r1["s1"], "ratio": r1["s1"] / r0["s_pre"], "D_max": dmax, "dhead_land": dland,
                   "track": [(byi[i]["t"], byi[i]["yaw"], byi[i]["head1"], byi[i]["s1"]) for i in range(i0, i1 + 1)]}
            R["tap_strafe"].append(row)
            tsum.setdefault(cnd, []).append(row)
            print(h5 % (cnd, "r%d" % t["run"], "%.2f" % dyaw, "%.2f" % dhead, "%.2f" % lag, "%.2f" % row["s_start"],
                        "%.2f" % row["s_end"], "%.5f" % row["ratio"], "%.3f" % dmax if dmax == dmax else "-",
                        "%.2f" % dland))
    print("  per condition (mean over trials):")
    R["tap_strafe_summary"] = {}
    for cnd, rows in tsum.items():
        s = {k: sum(r[k] for r in rows) / len(rows) for k in ("dyaw", "dhead", "lag", "ratio", "s_start", "s_end")}
        R["tap_strafe_summary"][cnd] = s
        print("    %-15s n %d  dyaw %.2f  dhead %.2f  lag %.2f  speed %.2f -> %.2f (x%.5f)" % (
            cnd, len(rows), s["dyaw"], s["dhead"], s["lag"], s["s_start"], s["s_end"], s["ratio"]))
    print("  Per W edge (a1_ts_360 / a1_ts_180 / a1_sj_ts_360, first trial): t, gap yaw-heading before -> after, lam_obs/lam_model")
    for cnd in ["a1_ts_360", "a1_ts_180", "a1_sj_ts_360"]:
        ps = [p for p in R["presses"] if p["condition"] == cnd]
        if not ps:
            continue
        run0 = ps[0]["run"]
        line = []
        for p in ps:
            if p["run"] != run0:
                continue
            g0 = angdiff(p["yaw"], p["head0"])
            g1 = angdiff(p["yaw"], p["head1"])
            line.append("%.3f:%.2f->%.2f(%s/%.3f)" % (p["t"], g0, g1, "%.3f" % p["lam_obs"] if p["lam_obs"] is not None else "-",
                                                      p["lam_model"]))
        print("    %s r%d: %s" % (cnd, run0, "  ".join(line)))
    print("  Clamp limit on one press: max turn at constant speed s is 2*asin(209.3/(2 s)) = %.1f deg at 297, %.1f at 350;"
          % (2 * math.degrees(math.asin(LMAX / (2 * 297))), 2 * math.degrees(math.asin(LMAX / (2 * 350)))))
    print("  a press with lam 0.7 closes 70% of the yaw-heading gap, so the clamp binds when 0.7*gap exceeds that.")

    # ------------------------------------------------------------------ 6. diagonals
    print("=" * 110)
    print("6. DIAGONALS (two keys on one press command): wish variants")
    for cnd in ["a1_diag_fr", "a1_diag_br"]:
        rs = [p for p in R["presses"] if p["condition"] == cnd]
        if not rs:
            continue
        print("  %-10s n %d  keys %s  fwd %.2f side %.2f  theta %s  s' %s -> s1 %s  |D|obs %s  head1 %s" % (
            cnd, len(rs), rs[0]["keys"], rs[0]["fwd"], rs[0]["side"], f3(st(p["theta"] for p in rs), 2),
            f3(st(p["s_aa"] for p in rs), 2), f3(st(p["s1"] for p in rs), 2), f3(st(p["D_obs"] for p in rs), 3),
            f3(st(p["head1"] for p in rs), 2)))
        for v in ("M3", "wish_raw_keys", "wish_sign_keys", "no_clamp", "aa_only"):
            print("      res %-16s max %.3f" % (v, mx(p["res"][v] for p in rs)))

    # ------------------------------------------------------------------ 7. wall bounce
    print("=" * 110)
    print("7. WALL BOUNCE: does the bounce jump restart the window?")
    for cnd in ["a1_wb_lurch3", "a1_wb_lurch30", "e6_bounce_none_15"]:
        for t in bycond.get(cnd, []):
            w = W[(t["session"], t["run"])]
            cs = t["cmds"]
            js = w["jumps"]
            txt = "  %-17s r%d jumps at cmd idx %s (t of bounce after first jump %s)" % (
                cnd, t["run"], [x - js[0] for x in js],
                ["%.3f" % sum(cs[k]["dt"] for k in range(js[0], x)) for x in js[1:]])
            ps = [r for r in w["air"] if r["new"]]
            for r in ps:
                txt += ("\n      press %s at %d cmds after anchor: t_bounce %.3f (lam %.3f)  t_jump %.3f (lam %.3f)  s %.2f -> %.2f"
                        "  |D|obs %.2f  res: t_bounce %.3f  t_jump %.3f  aa_only %.3f"
                        % (r["keys"], r["i"] - r["anchor"], r["t"], lam_t(r["t"]), r["t_first_jump"],
                           lam_t(r["t_first_jump"]), r["s_aa"], r["s1"], r["D_obs"], r["res"]["M3"],
                           r["res"]["t_from_first_jump"], r["res"]["aa_only"]))
            if not ps:
                txt += "  (no direction press edge in the air)"
            print(txt)

    # ------------------------------------------------------------------ 8. parity
    print("=" * 110)
    print("8. CLIENT (native S21) vs DEDI: max |sv - cl| over the 12 pre/post fields of the same usercmd (u, u/s)")
    print("  free air = airborne commands where client and dedi agree on contact (|dvz| < 1); 'contact' = commands where")
    print("  one side touched down / hit the wall on a different command (counted, not in the max). dvh = max over vx vy pvx pvy")
    print("  %-18s %6s %8s %10s %10s %10s %9s %12s" % ("condition", "air n", "contact", "air max", "air dvh", "press max",
                                                     "trials eq", "sv model res"))
    for cnd in CONDS:
        recs, eq, nt, ncont = [], 0, 0, 0
        for t in bycond.get(cnd, []):
            rr = [r for r in W[(t["session"], t["run"])]["air"] if r.get("sv_diff") is not None]
            ncont += sum(1 for r in rr if r["sv_contact"])
            rr = [r for r in rr if not r["sv_contact"]]
            recs += rr
            if rr:
                nt += 1
                eq += all(r["sv_diff"] <= TOL for r in rr)
        prs = [r for r in recs if r["new"]]
        row = {"air_n": len(recs), "contact_mismatch_n": ncont, "air_max": mx(r["sv_diff"] for r in recs),
               "air_dvh_max": mx(r["sv_dvh"] for r in recs), "press_max": mx(r["sv_diff"] for r in prs),
               "press_dvh_max": mx(r["sv_dvh"] for r in prs),
               "trials_identical": eq, "trials": nt, "sv_model_res_press_max": mx(r.get("sv_res") for r in prs)}
        R["parity"][cnd] = row
        print("  %-18s %6d %8d %10.4f %10.4f %10.4f %6d/%-3d %12.4f" % (cnd, row["air_n"], ncont, row["air_max"],
                                                                     row["air_dvh_max"], row["press_max"], eq, nt,
                                                                     row["sv_model_res_press_max"]))
    nomt = sum(1 for t in trials for r in W[(t["session"], t["run"])]["air"] if r.get("sv_diff") is None)
    print("  airborne commands without a dedi row: %d" % nomt)

    # ------------------------------------------------------------------ 9. closed loop
    print("=" * 110)
    print("9. CLOSED LOOP: chosen model integrated from each jump's post-state over the airborne commands (no resets)")
    print("  %-18s %5s %10s %10s" % ("condition", "jumps", "end err max", "err max"))
    for cnd in CONDS:
        rows = []
        for t in bycond.get(cnd, []):
            for c in closed_loop(t, W[(t["session"], t["run"])]):
                c.update({"run": t["run"], "condition": cnd})
                rows.append(c)
        R["closed_loop"] += rows
        print("  %-18s %5d %10.3f %10.3f   (cmds per segment %s)" % (
            cnd, len(rows), mx(r["err_end"] for r in rows), mx(r["err_max"] for r in rows),
            sorted(set(r["n"] for r in rows))[:6]))

    # ------------------------------------------------------------------ 10. prediction
    print("=" * 110)
    print("10. MODEL PREDICTION (not measured): tap strafe at 120 fps, W edge every 2 commands from t = 0.033 s, view turning")
    print("    right at a constant rate from t = 0.033 s; heading change of v at t = 0.267 s (end of the measured window)")
    print("    and at t = 0.5 s (end of the lurch window); AirAccelerate (fwd 0.5, wish cap 69) included")
    print("  %-8s %6s | %9s %9s %8s | %9s %9s %8s %7s" % ("rate", "speed", "dh@0.267", "dyaw", "s", "dh@0.5", "dyaw", "s", "clamped"))
    R["prediction"] = []
    for s0 in (297.0, 350.0):
        for rate in (90, 180, 360, 720, 1440, 2880):
            res = simulate_ts(s0, rate)
            R["prediction"].append(dict(res, speed0=s0, rate=rate))
            print("  %6d/s %6.0f | %9.2f %9.2f %8.2f | %9.2f %9.2f %8.2f %7d" % (
                rate, s0, res["dh_267"], res["dyaw_267"], res["s_267"], res["dh_end"], res["dyaw_end"], res["s_end"], res["clamped"]))

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(R, fh, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
        print("wrote", os.path.basename(a.json))
    if a.params:
        P = {
            "model": "per usercmd, after M2 AirAccelerate, on any command with a new bit in buttons & 0x618 (FORWARD|BACK|"
                     "MOVELEFT|MOVERIGHT): lam = 0.7*clamp01((0.5 - t)/0.3), t from the start of the latest jump command "
                     "(ground, slide or wall-bounce jump); d = normalize((1-lam)*vhat + lam*wishdir); D = |v| d - v; "
                     "|D| <= 209.3 per press; v += D",
            "lam_max": {"value": LAM_MAX, "source": "M3 fit; A1 re-check", "A1_lam_full": R["press_summary"]["lam_full"]},
            "t_full_s": {"value": T_FULL, "source": "M3 fit (+-1 ms)"},
            "t_zero_s": {"value": T_ZERO, "source": "M3 fit (+-1 ms)", "A1_fade_offset_ms": R["fade_clock"]["offset_ms_sumdt"], "note": "A1 fade presses imply the window edges are about 0.5 ms later than the start-to-start sum of dt; inside the M3 +-1 ms, model not changed"},
            "clamp_ups": {"value": LMAX, "source": "M3 fit; per press (A1 sec 4)", "A1_clamped": R["press_summary"]["clamped_D"],
                          "note": "0.7 x sprint cap 299 (movescale 1.15); M4 showed it scales with the sprint cap"},
            "press_gate": {"value": "0x618 new bits (buttons & ~prev_buttons)", "source": "A1 obs; SDK TS_LURCH_PRESS_MASK"},
            "wishdir": {"value": "normalize(fwd*forward + side*right) from the command's own view yaw",
                        "source": "A1 diagonals + tap strafe (sec 5, 6)"},
            "anchor": {"value": "latest jump command incl. wall bounce", "source": "A1 sec 7"},
            "order": {"value": "AirAccelerate then lurch", "source": "M3; A1 lurch_before_aa column"},
            "air_accel": {"value": "500*dt, wish cap 60*movescale", "source": "M2"},
            "budget_cooldown": {"value": "none observed (presses 2 commands apart all lurch fully)", "source": "A1 sec 4/5"},
            "unmodelled": {"unclamped_speed_gain_per_press": R["press_summary"]["unclamped_speed_gain"]},
            "data": [s["folder"] for s in R["sessions"]],
        }
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(P, fh, indent=1)
        print("wrote", os.path.basename(a.params))


if __name__ == "__main__":
    main(sys.argv[1:])
