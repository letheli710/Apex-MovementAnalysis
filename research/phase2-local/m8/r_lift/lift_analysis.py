#!/usr/bin/env python3
"""M8 track R: Horizon gravity-lift gaps and the Horizon landing (R5Flowstate S21, local offline).

  py -3 lift_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py). stdlib only, no local paths. Schedules m8_lift*; the lift
centre is the trial origin + (120, 0) (m8_liftoff80/83: + (120, 80 / 83)), deployed by the reset (tools/hsd_trial.py).

Per trial (client first-time usercmds, t from the start of the entry usercmd):
- entry  = first usercmd with a grounded pre-state whose post vz is >= 250 (the lift sets vz = 300);
- hover  = first usercmd after the entry whose post vz is < 5 (the 0.5 -> -0.5 hover band, M4);
- eject  = first airborne usercmd after the entry whose velocity changes by > 100 u/s (3D) with post vz > 20 (eject 400 / 450, M4);
  scale_h = |v_h| / 400, scale_v = (post vz + g dt / 2) / 450 (M4 eject scale min(dwell / 0.5, 1));
- landing = the airborne usercmd whose next usercmd is grounded; f0 = post |v_h| / pre |v_h| on it;
- after the landing: speed and msc 0.1 / 0.25 / 0.5 / 1.0 s later, and the per-usercmd speed change.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

IN_JUMP = 0x2
FLOOR = 294.92


def r(x, n=3):
    return None if x is None else round(x, n)


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def ang(x, y):
    return math.degrees(math.atan2(y, x))


def angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def lift_offset(sch):
    if sch.startswith("m8_liftoff80"):
        return (120.0, 80.0)
    if sch.startswith("m8_liftoff83"):
        return (120.0, 83.0)
    return (120.0, 0.0)


def f0_model(vz):
    return min(1.0, max(0.0, 1.996467 - 1.6714e-6 * vz * vz))


def trial_row(T, origin, legend):
    cs = T["cmds"]
    sch = T["schedule"]
    off = lift_offset(sch)
    C = (origin[0] + off[0], origin[1] + off[1])
    R = {"run": T["run"], "schedule": sch, "legend": legend, "fps": T["fps"], "join": [T["join"]["joined"], T["join"]["cmds"]],
         "centre": [r(C[0], 2), r(C[1], 2)]}
    ie = next((i for i in range(1, len(cs)) if cs[i]["ground"] == 1 and cs[i]["pvz"] >= 250), None)
    R["entry"] = None
    if ie is None:
        return R
    tt = [0.0] * len(cs)
    for i in range(ie + 1, len(cs)):
        tt[i] = tt[i - 1] + dt_of(cs[i - 1])
    for i in range(ie - 1, -1, -1):
        tt[i] = tt[i + 1] - dt_of(cs[i])
    c = cs[ie]
    R["entry"] = {"idx": ie, "dist": r(math.hypot(c["ox"] - C[0], c["oy"] - C[1]), 2), "pre_h": r(hs(c, False)), "post_h": r(hs(c)),
                  "post_vz": r(c["pvz"])}
    ih = next((i for i in range(ie + 1, len(cs)) if cs[i]["pvz"] < 5 and cs[i]["ground"] == 0), None)
    ij = next((i for i in range(ie + 1, len(cs)) if cs[i]["ground"] == 0 and cs[i]["pvz"] > 20 and math.sqrt(
        (cs[i]["pvx"] - cs[i]["vx"]) ** 2 + (cs[i]["pvy"] - cs[i]["vy"]) ** 2 + (cs[i]["pvz"] - cs[i]["vz"]) ** 2) > 100), None)
    R["hover_t"] = r(tt[ih], 4) if ih is not None and (ij is None or ih < ij) else None
    R["hover_z"] = r(cs[ih]["oz"] - FLOOR, 2) if R["hover_t"] is not None else None
    R["eject"] = None
    if ij is not None:
        c = cs[ij]
        rad = ang(c["ox"] - C[0], c["oy"] - C[1])
        hdir = ang(c["pvx"], c["pvy"])
        R["eject"] = {"idx": ij, "t": r(tt[ij], 4), "dwell_after_hover": r(tt[ij] - tt[ih], 4) if R["hover_t"] is not None else None,
                      "z": r(c["oz"] - FLOOR, 2), "dist": r(math.hypot(c["ox"] - C[0], c["oy"] - C[1]), 2),
                      "pre": [r(c["vx"]), r(c["vy"]), r(c["vz"])], "post": [r(c["pvx"]), r(c["pvy"]), r(c["pvz"])],
                      "post_h": r(hs(c)), "post_vz_plus_half_g": r(c["pvz"] + 750.0 * dt_of(c) / 2, 3),
                      "scale_h": r(hs(c) / 400.0, 4), "scale_v": r((c["pvz"] + 750.0 * dt_of(c) / 2) / 450.0, 4),
                      "dir": r(hdir, 2), "radial": r(rad, 2), "yaw": r(c.get("yaw"), 2),
                      "dir_minus_radial": r(angdiff(hdir, rad), 2) if math.hypot(c["ox"] - C[0], c["oy"] - C[1]) > 40 else None, "dir_minus_yaw": r(angdiff(hdir, c.get("yaw") or 0.0), 2),
                      "fwd": c["fwd"], "side": c["sidemove"]}
    # presses after the entry: jumps (effect = residual dvz against the previous usercmd), first key edge after the eject
    jumps = []
    for i in range(ie + 1, len(cs)):
        if cs[i]["buttons"] & IN_JUMP and not cs[i - 1]["buttons"] & IN_JUMP:
            p = cs[i - 1]
            exp = (p["pvz"] - p["vz"]) * dt_of(cs[i]) / dt_of(p)
            jumps.append({"t": r(tt[i], 4), "in_lift": ij is None or i < ij, "pre": [r(cs[i]["vx"]), r(cs[i]["vy"]), r(cs[i]["vz"])],
                          "post": [r(cs[i]["pvx"]), r(cs[i]["pvy"]), r(cs[i]["pvz"])],
                          "resid_dvz": r((cs[i]["pvz"] - cs[i]["vz"]) - exp), "dvh": r(math.hypot(cs[i]["pvx"] - cs[i]["vx"], cs[i]["pvy"] - cs[i]["vy"]))})
    R["jumps"] = jumps
    # landing
    il = next((i for i in range((ij or ie) + 1, len(cs) - 1) if cs[i]["ground"] == 0 and cs[i + 1]["ground"] == 1), None)
    R["landing"] = None
    if il is not None:
        c = cs[il]
        ph = hs(c, False)
        after = {}
        for dtq in (0.1, 0.25, 0.5, 1.0, 1.5):
            k = next((q for q in range(il, len(cs)) if tt[q] - tt[il] >= dtq), None)
            after[str(dtq)] = [r(hs(cs[k]), 3), cs[k]["msc"], cs[k]["fwd"]] if k is not None else None
        win = [q for q in range(il + 1, len(cs)) if tt[q] - tt[il] <= 1.0]
        dec = [(hs(cs[q]) - hs(cs[q], False)) / dt_of(cs[q]) for q in win[:10]]
        R["landing"] = {"idx": il, "t": r(tt[il], 4), "z": r(c["poz"] - FLOOR, 2), "pre_vz": r(c["vz"]), "pre_h": r(ph), "post_h": r(hs(c)),
                        "f0_obs": r(hs(c) / ph, 5) if ph > 1 else None, "f0_model_m4": r(f0_model(c["vz"]), 5),
                        "msc_min_1s": min([cs[q]["msc"] for q in win] or [None]), "after": after,
                        "dvh_rate_first10": r(sum(dec) / len(dec), 2) if dec else None,
                        "w_held_after": any(cs[q]["fwd"] > 0 for q in win)}
    # air control after the eject: first move-key edge after the eject, components over time
    R["air"] = None
    if ij is not None:
        k0 = next((i for i in range(ij + 1, il if il else len(cs)) if (cs[i]["fwd"] != 0 or cs[i]["sidemove"] != 0)
                   and not (cs[i - 1]["fwd"] != 0 or cs[i - 1]["sidemove"] != 0)), None)
        if k0 is not None:
            v0 = (cs[k0]["vx"], cs[k0]["vy"])
            ser = {}
            for dtq in (0.1, 0.25, 0.5, 1.0, 1.5):
                k = next((q for q in range(k0, il or len(cs)) if tt[q] - tt[k0] >= dtq), None)
                ser[str(dtq)] = [r(cs[k]["pvx"] - v0[0], 3), r(cs[k]["pvy"] - v0[1], 3)] if k is not None else None
            dvs = [(cs[q]["pvx"] - cs[q]["vx"], cs[q]["pvy"] - cs[q]["vy"], dt_of(cs[q])) for q in range(k0, min(k0 + 12, il or len(cs)))]
            R["air"] = {"t": r(tt[k0], 4), "fwd": cs[k0]["fwd"], "side": cs[k0]["sidemove"], "v0": [r(v0[0]), r(v0[1])],
                        "dv_since_press": ser, "accel_first12": [r(math.hypot(a, b) / d, 1) for a, b, d in dvs[1:]],
                        "v_at_landing": [r(cs[il]["vx"]), r(cs[il]["vy"])] if il else None}
    return R


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    rows, metas = [], []
    for f in a.sessions:
        s = L.load(f)
        run = s["runner"]
        legend = (run.get("legend") or "").lower()
        org = {t["run"]: t.get("origin") for t in run["trials"]}
        rej = [(t["run"], t["schedule"], t["why"]) for t in run["trials"] if not t.get("ok") and not t.get("warmup")]
        metas.append({"folder": s["folder"], "legend": legend, "kit": run.get("kit_reply"), "reconstructed": bool(run.get("reconstructed")),
                      "scored": len(s["trials"]), "rejected": rej})
        for T in s["trials"]:
            if T["schedule"].startswith("m8_lift"):
                rows.append(trial_row(T, org[T["run"]], legend))
    P = print
    P("M8 R: Horizon gravity lift gaps and landing")
    P("=" * 100)
    for m in metas:
        P(f"{m['folder']}: legend {m['legend']} scored {m['scored']} rejected {m['rejected']} runner_reconstructed {m['reconstructed']}")
    P()
    P("1. PER TRIAL (t from the entry usercmd)")
    P("-" * 100)
    for R in rows:
        e, j, ld = R["entry"], R["eject"], R["landing"]
        P(f"r{R['run']} {R['schedule']:<18} {R['legend']:<9} entry {('d %.1f h %.2f->%.2f' % (e['dist'], e['pre_h'], e['post_h'])) if e else None}"
          f" hover t {R['hover_t']} z {R['hover_z']}")
        if j:
            P(f"    eject t {j['t']} (after hover {j['dwell_after_hover']}) z {j['z']} d {j['dist']} post {j['post']} |h| {j['post_h']}"
              f" vz+g/2 {j['post_vz_plus_half_g']} dir {j['dir']} radial {j['radial']} yaw {j['yaw']} (dir-radial {j['dir_minus_radial']},"
              f" dir-yaw {j['dir_minus_yaw']}) fwd {j['fwd']} side {j['side']} scale h/v {j['scale_h']}/{j['scale_v']}")
        for q in R["jumps"]:
            P(f"    jump t {q['t']} in_lift {q['in_lift']} pre {q['pre']} post {q['post']} resid_dvz {q['resid_dvz']} dvh {q['dvh']}")
        if R["air"]:
            x = R["air"]
            P(f"    air key t {x['t']} fwd {x['fwd']} side {x['side']} v0 {x['v0']} dv since press {x['dv_since_press']} v@land {x['v_at_landing']}")
            P(f"      accel per usercmd (first 12) {x['accel_first12']}")
        if ld:
            P(f"    landing t {ld['t']} z {ld['z']} vz {ld['pre_vz']} h {ld['pre_h']} -> {ld['post_h']} f0 {ld['f0_obs']} (M4 model {ld['f0_model_m4']})"
              f" msc_min {ld['msc_min_1s']} W {ld['w_held_after']} dvh/dt first10 {ld['dvh_rate_first10']} after {ld['after']}")
    P()
    P("2. SUMMARY BY SCHEDULE AND LEGEND")
    P("-" * 100)
    groups = {}
    for R in rows:
        groups.setdefault((R["legend"], R["schedule"]), []).append(R)
    summ = {}
    for (lg, sch), rs in sorted(groups.items()):
        ej = [R["eject"] for R in rs if R["eject"]]
        ld = [R["landing"] for R in rs if R["landing"]]
        d = {"n": len(rs),
             "eject_t": L.stats([x["t"] for x in ej]), "dwell_after_hover": L.stats([x["dwell_after_hover"] for x in ej]),
             "eject_z": L.stats([x["z"] for x in ej]), "eject_h": L.stats([x["post_h"] for x in ej]),
             "eject_vz": L.stats([x["post_vz_plus_half_g"] for x in ej]), "scale_h": L.stats([x["scale_h"] for x in ej]), "scale_v": L.stats([x["scale_v"] for x in ej]),
             "dir_minus_radial": L.stats([x["dir_minus_radial"] for x in ej]), "dir_minus_yaw": L.stats([x["dir_minus_yaw"] for x in ej]),
             "land_vz": L.stats([x["pre_vz"] for x in ld]), "land_f0": L.stats([x["f0_obs"] for x in ld]),
             "land_msc_min": L.stats([x["msc_min_1s"] for x in ld]),
             "land_z": L.stats([x["z"] for x in ld])}
        summ[f"{lg}:{sch}"] = d
        P(f"  {lg:<9} {sch:<18} n {len(rs)}")
        for k in ("eject_t", "dwell_after_hover", "eject_z", "eject_h", "eject_vz", "scale_h", "scale_v", "dir_minus_radial", "dir_minus_yaw", "land_vz",
                  "land_f0", "land_msc_min", "land_z"):
            if d[k].get("n"):
                P(f"      {k:<18} {L.fmt(d[k], 3)}")
    P()
    P("3. LANDING COMPARISON: lift ride (flat floor, no input) and land_w (W held after landing), per legend")
    P("-" * 100)
    for sch in ("m8_lift_ride", "m8_lift_land_w"):
        for lg in sorted(set(R["legend"] for R in rows)):
            ls = [R["landing"] for R in rows if R["schedule"] == sch and R["legend"] == lg and R["landing"] and abs(R["landing"]["z"]) < 5]
            if not ls:
                continue
            P(f"  {sch:<15} {lg:<9} n {len(ls)} vz {L.fmt(L.stats([x['pre_vz'] for x in ls]), 1)} f0 {L.fmt(L.stats([x['f0_obs'] for x in ls]), 4)}"
              f" msc_min {L.fmt(L.stats([x['msc_min_1s'] for x in ls]), 4)}")
            for key in ("0.1", "0.25", "0.5", "1.0", "1.5"):
                vals = [x["after"][key][0] for x in ls if x["after"].get(key)]
                mscs = [x["after"][key][1] for x in ls if x["after"].get(key)]
                P(f"      +{key:<4} s: |v_h| {L.fmt(L.stats(vals), 2)}  msc {L.fmt(L.stats(mscs), 4)}")
    P()
    P("4. EJECT SCALE FOR SHORT DWELL (eject before 0.5 s in the lift): scale vs t_eject (from the entry usercmd start)")
    P("-" * 100)
    short = [R["eject"] for R in rows if R["eject"] and R["eject"]["scale_h"] < 0.999 and R["eject"]["t"] < 0.6]
    for e in short:
        P(f"    t {e['t']} scale_h {e['scale_h']} scale_v {e['scale_v']} -> offset t - 0.5*scale = {r(e['t'] - 0.5 * e['scale_h'], 4)}")
    off = L.stats([e["t"] - 0.5 * e["scale_h"] for e in short])
    P(f"  offset {L.fmt(off, 4)}  (scale = (t_eject - offset) / 0.5)")
    summ["_short_dwell_offset"] = off
    out = {"metas": metas, "rows": rows, "summary": summ}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    if a.params:
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(build_params(rows, summ), fh, indent=1)
    return 0


def build_params(rows, summ):
    def p(name, s, unit, cls, note=""):
        return {"name": name, "value": r(s.get("mean"), 4) if isinstance(s, dict) else s, "sd": r(s.get("sd"), 4) if isinstance(s, dict) else None,
                "n": s.get("n") if isinstance(s, dict) else None, "unit": unit, "class": cls, "note": note}
    g = lambda k: summ.get(k, {})  # noqa: E731
    out = []
    ride = g("horizon:m8_lift_ride")
    if ride:
        out += [p("hover_to_eject", ride["dwell_after_hover"], "s", "meas", "hover band start -> eject, no input"),
                p("eject_h", ride["eject_h"], "u/s", "meas"), p("eject_vz", ride["eject_vz"], "u/s", "meas", "post vz + g*dt/2"),
                p("horizon_landing_f0_ride", ride["land_f0"], "ratio", "meas", "landing |vz| about 1347")]
    for t in ("05", "15", "30"):
        s = g(f"horizon:m8_lift_side_t{t}")
        if s:
            out.append(p(f"side_exit_t{t}_dir_minus_radial", s["dir_minus_radial"], "deg", "meas", "eject direction minus radial direction at exit"))
            out.append(p(f"side_exit_t{t}_eject_h", s["eject_h"], "u/s", "meas"))
    off = summ.get("_short_dwell_offset", {})
    if off.get("n"):
        out.append(p("short_dwell_scale_offset", off, "s", "fit", "eject scale = (t_eject - offset)/0.5 for t_eject < 0.5 s, t from the entry usercmd start"))
    for k in sorted(summ):
        if k.startswith("_"):
            continue
        if k.endswith(":m8_lift_ride") and not k.startswith("horizon"):
            out.append(p(f"{k.split(':')[0]}_landing_f0_ride", summ[k]["land_f0"], "ratio", "meas", "control legend, same lift eject fall"))
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
