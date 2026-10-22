#!/usr/bin/env python3
"""M8 track R: Octane jump-pad double jump (R5Flowstate S21, local offline).

  py -3 pad_djump_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py: client first-time MOVE-TRACE usercmds joined to the client
HSD frames, dedi MOVE-TRACE rows by cmd number, runner filter ok=true and warmup=false). stdlib only, no local paths.

Per trial (schedules m8_pad*, m8_padc_*, m8_padw_*, m8_djctrl):
- launch  = first usercmd whose post vz exceeds its pre vz by > 400 u/s (the pad impulse; M4 1150*normalize(h + V*up));
- air jump presses = IN_JUMP press edges on usercmds whose pre-state is airborne;
- residual dvz of a press = (post vz - pre vz) - the gravity step of the previous airborne usercmd scaled by dt
  (slow-mo flight integrates on 0.8*dt, M4); a double jump (DJ) is a residual > 50 u/s;
- t since launch = sum of usercmd dt from the start of the launch usercmd to the start of the press usercmd;
- landing = the airborne usercmd whose next usercmd is grounded; f0 = post |v_h| / pre |v_h| on it, compared with the
  M4 landing law clamp(1.996467 - 1.6714e-6 vz^2, 0, 1) (OCTANE-PRIMITIVES.md 4.2).
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

IN_JUMP, IN_FORWARD, IN_BACK, IN_LEFT, IN_RIGHT = 0x2, 0x8, 0x10, 0x200, 0x400
G = 750.0
SLOWMO = 0.8
DJ_RESID = 50.0


def r(x, n=3):
    return None if x is None else round(x, n)


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def f0_model(vz):
    return min(1.0, max(0.0, 1.996467 - 1.6714e-6 * vz * vz))


def edges(cmds, bit, start=1):
    return [i for i in range(max(start, 1), len(cmds)) if cmds[i]["buttons"] & bit and not cmds[i - 1]["buttons"] & bit]


def press_info(T, i, i_launch):
    cs = T["cmds"]
    c, p = cs[i], cs[i - 1]
    g_prev = (p["pvz"] - p["vz"]) * dt_of(c) / dt_of(p) if not p["ground"] else -G * SLOWMO * dt_of(c)
    resid = (c["pvz"] - c["vz"]) - g_prev
    t_l = sum(dt_of(cs[k]) for k in range(i_launch, i)) if i_launch is not None else None
    sv = T["sv"].get(c["cmd"])
    dvx, dvy = c["pvx"] - c["vx"], c["pvy"] - c["vy"]
    hz = None
    if (c["fwd"] != 0 or c["sidemove"] != 0) and resid > DJ_RESID:
        yaw = math.radians(c.get("yaw") or 0.0)
        f, rt = (math.cos(yaw), math.sin(yaw)), (math.sin(yaw), -math.cos(yaw))
        sf = (1 if c["fwd"] > 0 else -1 if c["fwd"] < 0 else 0)
        ss = (1 if c["sidemove"] > 0 else -1 if c["sidemove"] < 0 else 0)
        wv = (f[0] * sf + rt[0] * ss, f[1] * sf + rt[1] * ss)
        wn = math.hypot(*wv)
        w = (wv[0] / wn, wv[1] / wn)
        sp = math.hypot(c["vx"], c["vy"])
        u = (c["vx"] / sp, c["vy"] / sp)
        keys = IN_FORWARD | IN_BACK | IN_LEFT | IN_RIGHT
        new_edge = bool((c["buttons"] & keys) & ~(p["buttons"] & keys))
        # air acceleration on the same usercmd: when the post velocity along the wish is below the 60*msc cap, take the
        # next usercmd's horizontal change as the size of one AirAccelerate step (it keeps adding until the cap)
        nx = T["cmds"][i + 1] if i + 1 < len(T["cmds"]) else None
        along_post = c["pvx"] * w[0] + c["pvy"] * w[1]
        aa = (nx["pvx"] - nx["vx"], nx["pvy"] - nx["vy"]) if (nx is not None and along_post < 60 * c["msc"] - 0.5) else (0.0, 0.0)
        D = (c["pvx"] - c["vx"] - aa[0], c["pvy"] - c["vy"] - aa[1])
        det = -u[0] * w[1] + u[1] * w[0]
        if abs(det) > 0.05:
            a = (D[0] * w[1] - w[0] * D[1]) / det
            b = (-u[0] * D[1] + u[1] * D[0]) / det
            ab = None
        else:
            a = b = None
            ab = D[0] * w[0] + D[1] * w[1]
        pred = (c["vx"] - 240.0 * u[0] + 240.0 * w[0] + aa[0], c["vy"] - 240.0 * u[1] + 240.0 * w[1] + aa[1])
        hz = {"wish": [r(w[0], 4), r(w[1], 4)], "new_key_edge": new_edge, "aa_same_cmd": [r(aa[0]), r(aa[1])],
              "loss_along_u": r(a), "gain_along_w": r(b), "parallel_net_along_w": r(ab),
              "pred_240": [r(pred[0]), r(pred[1])], "err_240": r(math.hypot(pred[0] - c["pvx"], pred[1] - c["pvy"]), 4)}
    return {"hz": hz, "idx": i, "cmds_after_launch": (i - i_launch) if i_launch is not None else None, "t_since_launch": r(t_l, 4),
            "pre_ground": c["ground"], "duck": c["duck"], "fwd": c["fwd"], "side": c["sidemove"], "yaw": r(c.get("yaw"), 2),
            "pre": [r(c["vx"]), r(c["vy"]), r(c["vz"])], "post": [r(c["pvx"]), r(c["pvy"]), r(c["pvz"])],
            "gravity_step": r(g_prev, 4), "resid_dvz": r(resid), "dj": resid > DJ_RESID,
            "post_plus_g": r(c["pvz"] - g_prev, 3), "dvh": [r(dvx), r(dvy)], "dvh_mag": r(math.hypot(dvx, dvy)),
            "pre_h": r(hs(c, False)), "post_h": r(hs(c)),
            "sv_post": [r(sv["pvx"]), r(sv["pvy"]), r(sv["pvz"])] if sv else None,
            "sv_resid_dvz": r((sv["pvz"] - sv["vz"]) - g_prev) if sv else None,
            "sv_dj": ((sv["pvz"] - sv["vz"]) - g_prev > DJ_RESID) if sv else None,
            "sv_diff": r(max(abs(sv["pvx"] - c["pvx"]), abs(sv["pvy"] - c["pvy"]), abs(sv["pvz"] - c["pvz"])), 4) if sv else None}


def trial_row(T):
    cs = T["cmds"]
    sch = T["schedule"]
    R = {"run": T["run"], "schedule": sch, "fps": T["fps"], "join": T["join"]}
    il = next((i for i in range(1, len(cs)) if cs[i]["pvz"] - cs[i]["vz"] > 400), None)
    R["launch"] = None
    if il is not None:
        c = cs[il]
        R["launch"] = {"idx": il, "pre_ground": c["ground"], "pre": [r(c["vx"]), r(c["vy"]), r(c["vz"])],
                       "post": [r(c["pvx"]), r(c["pvy"]), r(c["pvz"])], "post_h": r(hs(c)), "z": r(c["oz"]), "duck": c["duck"]}
    # first ground jump (control and jump-in)
    gj = [i for i in edges(cs, IN_JUMP) if cs[i]["ground"] == 1 and cs[i]["pvz"] > 100]
    R["ground_jump_idx"] = gj[0] if gj else None
    anchor = il if il is not None else (gj[0] if gj else None)
    R["air_presses"] = [press_info(T, i, anchor) for i in edges(cs, IN_JUMP) if cs[i]["ground"] == 0 and anchor is not None and i > anchor]
    # held press: IN_JUMP held across the launch (jump-in hold)
    if il is not None:
        R["jump_held_at_launch"] = bool(cs[il]["buttons"] & IN_JUMP)
        held = []
        k = il
        while k < len(cs) and cs[k]["buttons"] & IN_JUMP:
            held.append(k)
            k += 1
        R["held_cmds_after_launch"] = len(held)
        R["held_dj"] = [press_info(T, q, il) for q in held[1:] if press_info(T, q, il)["dj"]]
    # landing(s) after the anchor
    lands = []
    if anchor is not None:
        for i in range(anchor + 1, len(cs) - 1):
            if cs[i]["ground"] == 0 and cs[i + 1]["ground"] == 1:
                c = cs[i]
                ph = hs(c, False)
                lands.append({"idx": i, "t_since_launch": r(sum(dt_of(cs[k]) for k in range(anchor, i)), 4), "pre_vz": r(c["vz"]),
                              "pre_h": r(ph), "post_h": r(hs(c)), "f0_obs": r(hs(c) / ph, 5) if ph > 1 else None,
                              "f0_model": r(f0_model(c["vz"]), 5), "x": r(c["pox"], 1), "msc_next": cs[i + 1]["msc"]})
    R["landings"] = lands
    # lurch press (moveright edge) after the launch
    rr = [i for i in edges(cs, IN_RIGHT) if anchor is not None and i > anchor and cs[i]["ground"] == 0]
    R["lurch"] = None
    if rr:
        i = rr[0]
        c, p = cs[i], cs[i - 1]
        R["lurch"] = {"idx": i, "t_since_launch": r(sum(dt_of(cs[k]) for k in range(anchor, i)), 4),
                      "dv": [r(c["pvx"] - c["vx"]), r(c["pvy"] - c["vy"])], "pre": [r(c["vx"]), r(c["vy"])],
                      "post": [r(c["pvx"]), r(c["pvy"])], "prev_dv": [r(p["pvx"] - p["vx"]), r(p["pvy"] - p["vy"])],
                      "next_dv": [[r(cs[q]["pvx"] - cs[q]["vx"]), r(cs[q]["pvy"] - cs[q]["vy"])] for q in range(i + 1, min(i + 4, len(cs)))]}
    # horizontal drift over the 0.5 s after a DJ (input held on the DJ command: moveright / backward / forward)
    djs = [p for p in R["air_presses"] if p["dj"]]
    R["dj_followup"] = None
    if djs:
        i = djs[0]["idx"]
        k = i
        tsum = 0.0
        while k + 1 < len(cs) and tsum < 0.5 and cs[k + 1]["ground"] == 0:
            k += 1
            tsum += dt_of(cs[k])
        R["dj_followup"] = {"t": r(tsum, 4), "v_after_dj": [r(cs[i]["pvx"]), r(cs[i]["pvy"])],
                            "v_after_0p5": [r(cs[k]["pvx"]), r(cs[k]["pvy"])],
                            "input_cmds": sum(1 for q in range(i, k + 1) if cs[q]["fwd"] != 0 or cs[q]["sidemove"] != 0)}
    return R


def stats(vals, nd=3):
    s = L.stats(vals)
    return {k: (round(v, nd) if isinstance(v, float) else v) for k, v in s.items()}


def fmt(vals, nd=3):
    return L.fmt(L.stats(vals), nd)


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
        rej = [(t["run"], t["schedule"], t["why"]) for t in run["trials"] if not t.get("ok") and not t.get("warmup")]
        metas.append({"folder": s["folder"], "legend": run.get("legend_reply"), "kit": run.get("kit_reply"),
                      "scored": len(s["trials"]), "rejected": rej})
        for T in s["trials"]:
            if T["schedule"].startswith(("m8_pad", "m8_djctrl")):
                rows.append(trial_row(T))
    P = print
    P("M8 R: Octane jump-pad double jump")
    P("=" * 100)
    for m in metas:
        P(f"{m['folder']}: scored {m['scored']} rejected {m['rejected']} kit {m['kit']}")
    P()
    P("1. PER TRIAL")
    P("-" * 100)
    for R in rows:
        la = R["launch"]
        P(f"r{R['run']} {R['schedule']:<20} launch {('idx %d pre_ground %d post %s' % (la['idx'], la['pre_ground'], la['post'])) if la else None}"
          f" join {R['join']['joined']}/{R['join']['cmds']}")
        for p in R["air_presses"]:
            P(f"    press +{p['cmds_after_launch']} cmds t {p['t_since_launch']} pre {p['pre']} post {p['post']} resid_dvz {p['resid_dvz']}"
              f" DJ cl {p['dj']} sv {p['sv_dj']} post+g {p['post_plus_g']} dvh {p['dvh']} fwd {p['fwd']} side {p['side']} yaw {p['yaw']} sv_diff {p['sv_diff']}")
        if R.get("jump_held_at_launch") is not None and R.get("held_cmds_after_launch"):
            P(f"    jump held at launch {R['jump_held_at_launch']} for {R['held_cmds_after_launch']} cmds; DJ while held {len(R['held_dj'])}")
        if R["lurch"]:
            P(f"    lurch press t {R['lurch']['t_since_launch']} dv {R['lurch']['dv']} prev_dv {R['lurch']['prev_dv']} next_dv {R['lurch']['next_dv']}")
        if R["dj_followup"]:
            P(f"    after DJ: v {R['dj_followup']['v_after_dj']} -> {R['dj_followup']['v_after_0p5']} over {R['dj_followup']['t']} s"
              f" (input on {R['dj_followup']['input_cmds']} cmds)")
        for ld in R["landings"][:2]:
            P(f"    landing t {ld['t_since_launch']} vz {ld['pre_vz']} h {ld['pre_h']} -> {ld['post_h']} f0 {ld['f0_obs']} (model {ld['f0_model']})"
              f" x {ld['x']}")
    P()
    P("2. GRANT TIMING: first air press after a pad launch, by schedule")
    P("-" * 100)
    groups = {}
    for R in rows:
        if R["launch"] and R["launch"]["pre_ground"] == 1 and R["air_presses"]:
            groups.setdefault(R["schedule"], []).append(R["air_presses"][0])
    timing = []
    for sch in sorted(groups, key=lambda s: groups[s][0]["t_since_launch"]):
        ps = groups[sch]
        n_dj = sum(p["dj"] for p in ps)
        n_sv = sum(bool(p["sv_dj"]) for p in ps)
        P(f"  {sch:<20} t {fmt([p['t_since_launch'] for p in ps], 4)}  DJ client {n_dj}/{len(ps)} dedi {n_sv}/{len(ps)}"
          f"  t(DJ) {[p['t_since_launch'] for p in ps if p['dj']]}  t(no) {[p['t_since_launch'] for p in ps if not p['dj']]}")
        timing.append({"schedule": sch, "n": len(ps), "dj": n_dj, "dj_sv": n_sv, "t": [p["t_since_launch"] for p in ps],
                       "dj_flags": [p["dj"] for p in ps], "sv_dj_flags": [p["sv_dj"] for p in ps]})
    allp = [p for R in rows if R["launch"] and R["launch"]["pre_ground"] == 1 for p in R["air_presses"][:1]]
    t_yes = [p["t_since_launch"] for p in allp if p["dj"]]
    t_no = [p["t_since_launch"] for p in allp if not p["dj"]]
    lo = max([t for t in t_no if t < (min(t_yes) if t_yes else 9)] or [None]) if t_no else None
    hi = min(t_yes) if t_yes else None
    overlap = sorted(set(t for t in t_no if hi is not None and t >= hi))
    P(f"  latest first-press without DJ before the earliest DJ: {lo}; earliest DJ: {hi}; no-DJ presses at/after the earliest DJ: {overlap}")
    P()
    P("3. DOUBLE-JUMP VELOCITY (all DJ presses)")
    P("-" * 100)
    dj = [p for R in rows for p in R["air_presses"] if p["dj"] and p["sv_dj"]]
    P(f"  DJ presses confirmed on client and dedi: {len(dj)} (client-only DJs are mispredictions, section 2/4)")
    add_rows = [p for p in dj if abs(p["post_plus_g"] - p["pre"][2] - 201.81) < 1.0]
    set_rows = [p for p in dj if abs(p["post_plus_g"] - 409.25) < 1.0 and p not in add_rows]
    other = [p for p in dj if p not in add_rows and p not in set_rows]
    add = [p["post_plus_g"] - p["pre"][2] for p in add_rows]
    setv = [p["post_plus_g"] for p in set_rows]
    P(f"  add branch:   post + g step - pre vz = {fmt(add, 3)}  pre vz {fmt([p['pre'][2] for p in add_rows], 2)}")
    P(f"  floor branch: post + g step = {fmt(setv, 3)}  pre vz {fmt([p['pre'][2] for p in set_rows], 2)}")
    P(f"  neither: {[(p['pre'][2], p['post_plus_g']) for p in other]}")
    lo_add = min([p["pre"][2] for p in add_rows] or [None])
    hi_set = max([p["pre"][2] for p in set_rows] or [None])
    P(f"  branch boundary on pre vz: highest floor-branch pre vz {hi_set}, lowest add-branch pre vz {lo_add}")
    noinput = [p for p in dj if p["fwd"] == 0 and p["side"] == 0]
    P(f"  horizontal change on the DJ cmd, no input: |dvh| {fmt([p['dvh_mag'] for p in noinput], 4)}")
    for p in dj:
        if p["fwd"] != 0 or p["side"] != 0:
            P(f"  with input fwd {p['fwd']} side {p['side']} yaw {p['yaw']}: pre {p['pre']} post {p['post']} dvh {p['dvh']}")
    P("  horizontal rule with a move key on the DJ cmd: v_h' = v_h - a*u + b*w (u = v_h/|v_h|, w = wish), model a = b = 240")
    for edge in (False, True):
        hs_ = [p for p in dj if p.get("hz") and p["hz"]["new_key_edge"] == edge]
        P(f"    key {'pressed on the DJ cmd (new edge)' if edge else 'already held (no edge)'}: n {len(hs_)}"
          f" a {fmt([p['hz']['loss_along_u'] for p in hs_ if p['hz']['loss_along_u'] is not None], 3)}"
          f" b {fmt([p['hz']['gain_along_w'] for p in hs_ if p['hz']['gain_along_w'] is not None], 3)}"
          f" parallel net {fmt([p['hz']['parallel_net_along_w'] for p in hs_ if p['hz']['parallel_net_along_w'] is not None], 3)}"
          f" err(240 model) {fmt([p['hz']['err_240'] for p in hs_], 4)}")
    P(f"  client/dedi max diff on DJ cmds: {max([p['sv_diff'] for p in dj if p['sv_diff'] is not None] or [None])}")
    second = [R["air_presses"][1] for R in rows if len(R["air_presses"]) > 1 and R["air_presses"][0]["dj"]]
    P(f"  second press after a DJ: DJ {sum(p['dj'] for p in second)}/{len(second)} resid {fmt([p['resid_dvz'] for p in second], 3)}")
    el = [R for R in rows if R["schedule"] == "m8_pad_early_late"]
    P(f"  early (no-DJ) press then later press: later DJ {sum(1 for R in el if len(R['air_presses']) > 1 and R['air_presses'][1]['dj'])}/{len(el)}")
    P()
    P("4. CONTROLS AND RESETS")
    P("-" * 100)
    ctrl = [R["air_presses"][0] for R in rows if R["schedule"] == "m8_djctrl" and R["air_presses"]]
    P(f"  m8_djctrl (normal jump, air press 0.3 s later): DJ {sum(p['dj'] for p in ctrl)}/{len(ctrl)} resid {fmt([p['resid_dvz'] for p in ctrl], 3)}")
    lj = [R for R in rows if R["schedule"] == "m8_pad_land_jump"]
    for R in lj:
        P(f"  r{R['run']} land_jump: ground jump idx {R['ground_jump_idx']} presses {[(p['cmds_after_launch'], p['pre_ground'], p['dj'], p['resid_dvz']) for p in R['air_presses']]}")
    P()
    P("5. LANDING AFTER A DJ (M4 landing law)")
    P("-" * 100)
    for name, sel in (("no DJ", lambda R: not any(p["dj"] for p in R["air_presses"])), ("with DJ", lambda R: any(p["dj"] for p in R["air_presses"]))):
        ls = [R["landings"][0] for R in rows if R["launch"] and R["launch"]["pre_ground"] == 1 and R["landings"] and sel(R)
              and R["schedule"] not in ("m8_djctrl",)]
        P(f"  {name}: n {len(ls)} vz {fmt([x['pre_vz'] for x in ls], 1)} f0 obs {fmt([x['f0_obs'] for x in ls], 4)}"
          f" model {fmt([x['f0_model'] for x in ls], 4)} air time {fmt([x['t_since_launch'] for x in ls], 3)}")
    P()
    P("6. LURCH AFTER THE DJ vs WITHOUT")
    P("-" * 100)
    for sch in ("m8_pad_dj_lurch", "m8_pad_lurch"):
        ls = [R["lurch"] for R in rows if R["schedule"] == sch and R["lurch"]]
        P(f"  {sch}: n {len(ls)} |dv| on press {fmt([math.hypot(*x['dv']) for x in ls], 3)} t {fmt([x['t_since_launch'] for x in ls], 3)}")
    P()
    P("7. ENTRY VARIANTS AND JUMP-IN")
    P("-" * 100)
    for sch in ("m8_padc_dj", "m8_padw_dj", "m8_pad_dj_f60", "m8_pad_jumpin", "m8_pad_jumpin_hold"):
        rs = [R for R in rows if R["schedule"] == sch]
        if not rs:
            continue
        P(f"  {sch}: n {len(rs)} launch pre_ground {[R['launch']['pre_ground'] if R['launch'] else None for R in rs]}"
          f" launch post {[R['launch']['post'] if R['launch'] else None for R in rs][:1]}"
          f" first-press DJ {[R['air_presses'][0]['dj'] if R['air_presses'] else None for R in rs]}"
          f" t {[R['air_presses'][0]['t_since_launch'] if R['air_presses'] else None for R in rs]}")
    out = {"metas": metas, "rows": rows, "timing": timing}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    if a.params:
        params = build_params(rows, timing, add, setv, ctrl, second, hi_set, lo_add, dj)
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(params, fh, indent=1)
    return 0


def build_params(rows, timing, add, setv, ctrl, second, hi_set, lo_add, dj):
    def p(name, value, unit, cls, n, note=""):
        return {"name": name, "value": value, "unit": unit, "class": cls, "n": n, "note": note}
    first = [R["air_presses"][0] for R in rows if R["launch"] and R["launch"]["pre_ground"] == 1 and R["air_presses"]
             and R["schedule"] != "m8_pad_land_jump"]
    sv_yes = sorted(x["t_since_launch"] for x in first if x["sv_dj"])
    sv_no = sorted(x["t_since_launch"] for x in first if x["sv_dj"] is False)
    cl_no_sv_yes = [x["t_since_launch"] for x in first if x["sv_dj"] and not x["dj"]]
    sa, ss = L.stats(add), L.stats(setv)
    held = [x for x in dj if x.get("hz") and not x["hz"]["new_key_edge"]]
    edge = [x for x in dj if x.get("hz") and x["hz"]["new_key_edge"]]
    ld = [R["landings"][0] for R in rows if R["launch"] and R["landings"] and any(q["dj"] and q["sv_dj"] for q in R["air_presses"])]
    lj = [q for R in rows if R["schedule"] == "m8_pad_land_jump" for q in R["air_presses"]]
    lu = [R["lurch"] for R in rows if R["schedule"] == "m8_pad_dj_lurch" and R["lurch"]]
    lc = [R["lurch"] for R in rows if R["schedule"] == "m8_pad_lurch" and R["lurch"]]
    hold = [R for R in rows if R["schedule"] == "m8_pad_jumpin_hold"]
    el = [R for R in rows if R["schedule"] == "m8_pad_early_late"]
    return [
        p("dj_grant_dedi_refused_latest", max([x for x in sv_no if not sv_yes or x < max(sv_yes)] or [None]), "s after the launch usercmd start", "meas", len(sv_no),
          "first press after a ground pad launch; dedi (authoritative) MOVE-TRACE"),
        p("dj_grant_dedi_accepted_earliest", min(sv_yes) if sv_yes else None, "s", "meas", len(sv_yes),
          "presses at 0.108 s: 3/5 accepted; at 0.133 s 5/5; source note says 0.1 s [src]"),
        p("dj_client_mispredicted_refusals", len(cl_no_sv_yes), "count (client refused, dedi accepted)", "meas", len(first),
          "times " + ", ".join("%.4f" % x for x in cl_no_sv_yes)),
        p("dj_vz_add", r(sa.get("mean"), 3), "u/s engine (pad slow-mo: world = 0.8 x engine)", "meas", sa.get("n", 0),
          f"post vz + gravity step - pre vz; sd {r(sa.get('sd'), 3)}"),
        p("dj_vz_floor", r(ss.get("mean"), 3), "u/s engine", "meas", ss.get("n", 0), f"post vz + gravity step when pre vz is low; sd {r(ss.get('sd'), 3)}"),
        p("dj_vz_branch_boundary", [hi_set, lo_add], "u/s engine pre vz bracket (floor at or below, add at or above)", "meas", len(dj),
          "discontinuous: not max(vz + add, floor)"),
        p("dj_horizontal_no_input", 0.0, "u/s change", "meas", sum(1 for x in dj if not x.get("hz")), "view direction irrelevant without a move key"),
        p("dj_horizontal_held_key_rule", 240.0, "u/s: v_h' = v_h - 240*v_hat + 240*wish_hat (then AirAccelerate)", "fit", len(held),
          f"max error {max([x['hz']['err_240'] for x in held] or [0]):.4f} u/s over fwd/back/right/diag and two launch speeds"),
        p("dj_horizontal_new_edge_same_cmd", {"right_a": r(L.stats([x['hz']['loss_along_u'] for x in edge if x['hz']['loss_along_u'] is not None]).get('mean'), 2),
                                              "right_b": r(L.stats([x['hz']['gain_along_w'] for x in edge if x['hz']['gain_along_w'] is not None]).get('mean'), 2),
                                              "back_net": r(L.stats([x['hz']['parallel_net_along_w'] for x in edge if x['hz']['parallel_net_along_w'] is not None]).get('mean'), 2)},
          "u/s", "meas", len(edge), "key pressed on the DJ usercmd itself: not explained by the held-key rule plus the lurch model (open)"),
        p("dj_once_per_launch", sum(x["dj"] for x in second), "DJ count on the second air press", "meas", len(second)),
        p("dj_early_press_does_not_consume", sum(1 for R in el if len(R["air_presses"]) > 1 and R["air_presses"][1]["sv_dj"]), "later DJ after a refused early press", "meas", len(el)),
        p("dj_held_jump_no_trigger", sum(len(R.get("held_dj") or []) for R in hold), "DJ while the jump key is held through the launch", "meas", len(hold),
          "a new press after release then DJs: " + str(sum(1 for R in hold if R["air_presses"] and R["air_presses"][0]["sv_dj"])) + "/" + str(len(hold))),
        p("dj_after_landing_dedi", sum(1 for q in lj if q["sv_dj"]), "dedi DJ on an air press after landing + ground jump (unused grant)", "meas", len(lj),
          "client predicted a DJ in " + str(sum(1 for q in lj if q["dj"])) + " (corrected by the dedi)"),
        p("dj_normal_jump_control", sum(x["dj"] for x in ctrl), "DJ after a normal jump", "meas", len(ctrl)),
        p("dj_landing_f0_err", r(max([abs(x["f0_obs"] - x["f0_model"]) for x in ld if x["f0_obs"] is not None] or [0]), 5),
          "max |f0 obs - M4 law|", "meas", len(ld), "landings after a DJ (impacts to |vz| 1336)"),
        p("dj_lurch_after", r(L.stats([math.hypot(*x["dv"]) for x in lu]).get("mean"), 3), "|dv| u/s of a moveright edge 0.025 s after the DJ", "meas", len(lu),
          "control without DJ at the same time: " + str(r(L.stats([math.hypot(*x["dv"]) for x in lc]).get("mean"), 3)) + " (pad-launch window over); the DJ re-anchors the lurch window"),
    ]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
