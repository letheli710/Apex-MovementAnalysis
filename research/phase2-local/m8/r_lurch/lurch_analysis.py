#!/usr/bin/env python3
"""M8 track R item 5: lurch follow-ups (reverse chains, held key + new press, tap strafe at 720 / 1440 deg/s, slide-jump
entry clamp). R5Flowstate S21, local offline.

  py -3 lurch_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

Reuses the M6-A1 loader and per-command walk unchanged (../../m6/a1_lurch/a1_lurch_analysis.py: client first-time
MOVE-TRACE joined to HSD frames; per airborne command v' = v + AirAccelerate(v), then on a new move-key edge
v' = lurch(v', wishdir, lam(t), 209.3) with lam = 0.7*clamp01((0.5 - t)/0.3), t from the latest jump command).
Only m8_lurch_* trials with ok=true, warmup=false are used. stdlib only, no local paths.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a1_lurch")))
import a1_lurch_analysis as A1  # noqa: E402


def r(x, n=3):
    return None if x is None else round(x, n)


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": m, "sd": sd, "min": min(vals), "max": max(vals)}


def fmt(s, nd=3):
    if not s.get("n"):
        return "n=0"
    return f"{s['mean']:.{nd}f} (sd {s['sd']:.{nd}f}, {s['min']:.{nd}f}..{s['max']:.{nd}f}, n={s['n']})"


def trial_row(t):
    w = A1.walk(t)
    cs = t["cmds"]
    R = {"run": t["run"], "schedule": t["schedule"], "fps": t["fps"], "jumps": len(w["jumps"])}
    if not w["jumps"]:
        R["presses"] = []
        R["ledge"] = ledge_row(cs)
        return R
    j0 = w["jumps"][0]
    R["jump_post_h"] = r(math.hypot(cs[j0]["pvx"], cs[j0]["pvy"]))
    pr = [a for a in w["air"] if a["new"]]
    R["presses"] = [{"t": r(a["t"], 4), "keys": a.get("keys"), "fwd": a["fwd"], "side": a["side"], "held": A1.keys(a["held"]),
                     "s_pre": r(a["s_pre"]), "s_post": r(a["s1"]), "head_pre": r(a["head0"], 2), "head_post": r(a["head1"], 2),
                     "lam_model": r(a.get("lam_model"), 4), "lam_obs": r(a.get("lam_obs"), 4), "D_obs": r(a.get("D_obs"), 3),
                     "D_model": r(a.get("D_model"), 3), "res_M3": r(a["res"].get("M3"), 4), "res_aa_only": r(a["res"].get("aa_only"), 3),
                     "res_sign_keys": r(a["res"].get("wish_sign_keys"), 4),
                     "sv_res": r(a.get("sv_res"), 4)} for a in pr]
    # heading / view 0.3 s after the jump command (turn-only controls have no press)
    tsum, k = 0.0, j0
    while k + 1 < len(cs) and tsum < 0.3 and cs[k + 1]["ground"] == 0:
        k += 1
        tsum += cs[k]["dt"] or 1 / 120
    R["jump_0p3"] = {"t": r(tsum, 3), "s": r(math.hypot(cs[k]["pvx"], cs[k]["pvy"])), "head": r(math.degrees(math.atan2(cs[k]["pvy"], cs[k]["pvx"])), 2),
                     "yaw": r(cs[k].get("yaw"), 2)}
    R["air_res_M3_max"] = r(max([a["res"]["M3"] for a in w["air"]] or [0]), 4)
    if pr:
        a0, a1 = pr[0], pr[-1]
        R["chain"] = {"s_before": r(a0["s_pre"]), "s_after": r(a1["s1"]), "head_before": r(a0["head0"], 2), "head_after": r(a1["head1"], 2),
                      "turn": r(A1.angdiff(a1["head1"], a0["head0"]), 2), "speed_ratio": r(a1["s1"] / a0["s_pre"], 4) if a0["s_pre"] else None}
    # heading and speed 0.3 s after the first press (tap strafe)
    if pr:
        i0 = pr[0]["i"]
        tsum, k = 0.0, i0
        while k + 1 < len(cs) and tsum < 0.3 and cs[k + 1]["ground"] == 0:
            k += 1
            tsum += cs[k]["dt"] or 1 / 120
        R["after_0p3"] = {"t": r(tsum, 3), "s": r(math.hypot(cs[k]["pvx"], cs[k]["pvy"])), "head": r(math.degrees(math.atan2(cs[k]["pvy"], cs[k]["pvx"])), 2),
                          "yaw": r(cs[k].get("yaw"), 2)}
    return R


def ledge_row(cs):
    """Walk-off without a jump (m8_lurch_ledge_*): the first airborne usercmd after a grounded one, then the first D press
    edge in the air; the press usercmd's horizontal change against the previous airborne usercmd's change."""
    io = next((i for i in range(1, len(cs)) if cs[i - 1]["ground"] == 1 and cs[i]["ground"] == 0), None)
    if io is None:
        return None
    out = {"walkoff_h": r(math.hypot(cs[io]["vx"], cs[io]["vy"])), "walkoff_z": r(cs[io]["oz"], 2)}
    ip = next((i for i in range(io + 1, len(cs)) if cs[i]["buttons"] & 0x400 and not cs[i - 1]["buttons"] & 0x400 and cs[i]["ground"] == 0), None)
    if ip is not None:
        c, p = cs[ip], cs[ip - 1]
        dv = (c["pvx"] - c["vx"], c["pvy"] - c["vy"])
        pdv = (p["pvx"] - p["vx"], p["pvy"] - p["vy"])
        out.update({"t_since_walkoff": r(sum((cs[k]["dt"] or 1 / 120) for k in range(io, ip)), 4), "side": c["sidemove"],
                    "pre": [r(c["vx"]), r(c["vy"])], "post": [r(c["pvx"]), r(c["pvy"])], "dv": [r(dv[0]), r(dv[1])],
                    "dv_mag": r(math.hypot(*dv)), "prev_dv": [r(pdv[0]), r(pdv[1])],
                    "next_dv_mag": [r(math.hypot(cs[q]["pvx"] - cs[q]["vx"], cs[q]["pvy"] - cs[q]["vy"])) for q in range(ip + 1, min(ip + 4, len(cs)))]})
    land = next((i for i in range(io + 1, len(cs)) if cs[i]["ground"] == 1), None)
    out["air_time"] = r(sum((cs[k]["dt"] or 1 / 120) for k in range(io, land)), 3) if land else None
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    rows, metas = [], []
    for f in a.sessions:
        s = A1.load_session(f)
        metas.append({"folder": s["folder"], "skipped": s["skipped"], "scored": len(s["trials"])})
        for t in s["trials"]:
            if t["schedule"].startswith("m8_lurch"):
                rows.append(trial_row(t))
    P = print
    P("M8 R item 5: lurch follow-ups")
    P("=" * 100)
    for m in metas:
        P(f"{m['folder']}: scored {m['scored']} skipped {m['skipped']}")
    P()
    P("1. PER TRIAL: every new move-key edge in the air (t from the jump command; M3 = one-step prediction residual)")
    P("-" * 100)
    for R in rows:
        P(f"r{R['run']} {R['schedule']:<22} jump |v_h| {R.get('jump_post_h')} air max res(M3) {R.get('air_res_M3_max')}"
          + (f" chain {R['chain']}" if R.get("chain") else ""))
        for p in R["presses"]:
            P(f"    t {p['t']} keys {p['keys']} held {p['held']} fwd {p['fwd']} side {p['side']} s {p['s_pre']}->{p['s_post']}"
              f" head {p['head_pre']}->{p['head_post']} D obs {p['D_obs']} model {p['D_model']} lam obs {p['lam_obs']} model {p['lam_model']}"
              f" res M3 {p['res_M3']} (aa-only {p['res_aa_only']}, sign-keys wish {p['res_sign_keys']}) sv {p['sv_res']}")
    P()
    P("1b. WALK-OFF WITHOUT A JUMP (ledge): D press after leaving the 232 u rock edge")
    P("-" * 100)
    for R in rows:
        if R.get("ledge"):
            P(f"r{R['run']} {R['schedule']:<22} {R['ledge']}")
    P()
    P("1c. HEADING 0.3 s AFTER THE JUMP (tap strafe and turn-only controls)")
    P("-" * 100)
    for R in rows:
        if R.get("jump_0p3") and ("_ts_" in R["schedule"] or "_turn_" in R["schedule"]):
            P(f"r{R['run']} {R['schedule']:<22} {R['jump_0p3']}")
    P()
    P("2. SUMMARY BY SCHEDULE")
    P("-" * 100)
    groups = {}
    for R in rows:
        groups.setdefault(R["schedule"], []).append(R)
    summ = {}
    for sch in sorted(groups):
        rs = groups[sch]
        ps = [p for R in rs for p in R["presses"]]
        d = {"n_trials": len(rs), "n_presses": len(ps), "res_M3": stats([p["res_M3"] for p in ps]),
             "res_sign_keys": stats([p["res_sign_keys"] for p in ps]), "res_aa_only": stats([p["res_aa_only"] for p in ps]),
             "D_obs": stats([p["D_obs"] for p in ps]),
             "turn": stats([R["chain"]["turn"] for R in rs if R.get("chain")]),
             "speed_ratio": stats([R["chain"]["speed_ratio"] for R in rs if R.get("chain")]),
             "s_after": stats([R["chain"]["s_after"] for R in rs if R.get("chain")]),
             "head_0p3": stats([R["after_0p3"]["head"] for R in rs if R.get("after_0p3")]),
             "yaw_0p3": stats([R["after_0p3"]["yaw"] for R in rs if R.get("after_0p3")]),
             "s_0p3": stats([R["after_0p3"]["s"] for R in rs if R.get("after_0p3")]),
             "air_res_max": stats([R.get("air_res_M3_max") for R in rs])}
        summ[sch] = d
        P(f"  {sch:<22} trials {len(rs)} presses {len(ps)}")
        for k in ("res_M3", "res_sign_keys", "res_aa_only", "air_res_max", "D_obs", "turn", "speed_ratio", "s_after", "head_0p3", "yaw_0p3", "s_0p3"):
            if d[k].get("n"):
                P(f"      {k:<12} {fmt(d[k], 4 if k in ('res_M3', 'res_sign_keys', 'res_aa_only', 'air_res_max', 'speed_ratio') else 2)}")
        # per press index (chains)
        k_max = max((len(R["presses"]) for R in rs), default=0)
        if k_max > 1:
            for k in range(k_max):
                pk = [R["presses"][k] for R in rs if len(R["presses"]) > k]
                P(f"      press {k}: keys {sorted(set(p['keys'] for p in pk))} t {fmt(stats([p['t'] for p in pk]), 3)}"
                  f" D obs {fmt(stats([p['D_obs'] for p in pk]), 2)} head after {fmt(stats([p['head_post'] for p in pk]), 1)}"
                  f" s after {fmt(stats([p['s_post'] for p in pk]), 1)}")
    out = {"metas": metas, "rows": rows, "summary": summ}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    if a.params:
        params = []
        for sch, d in summ.items():
            params.append({"name": f"{sch}_res_M3_max", "value": r(d["res_M3"].get("max"), 4), "n": d["n_presses"], "unit": "u/s",
                           "class": "meas", "note": "largest one-step residual of the unchanged M3/A1 lurch model on the press commands"})
            if d["turn"].get("n"):
                params.append({"name": f"{sch}_turn", "value": r(d["turn"]["mean"], 2), "sd": r(d["turn"]["sd"], 2), "n": d["turn"]["n"],
                               "unit": "deg", "class": "meas", "note": "heading change first press -> last press"})
                params.append({"name": f"{sch}_speed_ratio", "value": r(d["speed_ratio"]["mean"], 4), "n": d["speed_ratio"]["n"],
                               "unit": "ratio", "class": "meas"})
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(params, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
