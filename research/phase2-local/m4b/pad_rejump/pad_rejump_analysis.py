"""M4b: re-jump 3 frames after an Octane jump-pad landing, without and with W held.

usage:
  py -3 pad_rejump_analysis.py <session> [<session> ...] [--json results.json] [--params params.json]

Trials: runner.json ok=true and warmup=false, schedules m4b_pad_rejump / m4b_pad_rejump_w only.
Physics: client first-time MOVE-TRACE commands joined to the client HSD frames (M2 loader, reused via the M4
lg_load wrapper without changes). The dedi (sv) MOVE-TRACE rows of the same usercmd are compared on every
command from the pad landing to 0.5 s after the hop landing; the dedi is authoritative.

Models tested (no refit unless stated):
  landing   OCTANE-PRIMITIVES 4.2/4.3: v_h *= f0 on the landing cmd, f0 = clamp(1.996467 - 1.6714e-6 vz^2, 0, 1);
            msc = 1.15 * (f0 + (1 - f0) (t/1.0)^2) afterwards
  ground    M2: no-input / above-cap decel 1250 u/s^2 (not x msc)
  jump      M2 AIR-JUMP 4.2: V = sqrt(2 g 56 frac), frac = clamp(0.3 + 0.7 (t - 0.15)/0.60, 0.3, 1);
            M3: ground-jump horizontal cap; tested as sprintspeed*msc and walk speed*msc
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
from lg_load import IN_JUMP, stats, fmt  # noqa: E402

G = 750.0
MSC0 = 1.15
F0_A, F0_B, REC_T = 1.996467, -1.6714e-6, 1.0     # OCTANE-PRIMITIVES params
WALK, SPRINT, JUMP_H, AMJ = 173.5, 260.0, 56.0, 0.3
SCHEDS = ("m4b_pad_rejump", "m4b_pad_rejump_w")
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def h(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def dtc(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def f0_model(vz):
    return max(0.0, min(1.0, F0_A + F0_B * vz * vz))


def census(folder):
    p = os.path.join(folder, "report", "census.csv")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return {r["key"]: r["cl_classvar"] for r in csv.DictReader(fh)}


def analyse_trial(t):
    cm = t["cmds"]
    sv = {r["cmd"]: r for r in t["sv_mt"]}
    n = len(cm)
    # pad launch: one-command vz step (pre vz of the next command > 900)
    la = next((i for i in range(1, n) if cm[i]["ground"] == 0 and cm[i]["vz"] > 900 and cm[i - 1]["vz"] < 100), None)
    if la is None:
        return None
    la -= 1  # the launch command is the one whose post-state carries the impulse
    # pad landing command: airborne pre-state, post vz = 0, after a fall faster than 500 u/s
    L = next((i for i in range(la + 2, n) if cm[i]["vz"] < -500 and cm[i]["pvz"] == 0.0), None)
    J = next((i for i in range(L + 1, n) if lg_load.aj_load.pressed(cm, i, IN_JUMP)), None) if L else None
    if L is None or J is None:
        return None
    L2 = next((i for i in range(J + 2, n) if cm[i]["vz"] < 0 and cm[i]["pvz"] == 0.0), None)
    c_l, c_j = cm[L], cm[J]
    tl = c_l["t_cmd"]
    r = {"run": t["run"], "sched": t["schedule"], "fps": t["fps"], "launch_cmd": la, "land_cmd": L, "jump_cmd": J,
         "hop_land_cmd": L2}
    r["launch_h"] = h(cm[la])
    r["launch_vz"] = cm[la]["pvz"]
    r["pre_land_h"] = h(c_l, post=False)
    r["pre_land_vz"] = c_l["vz"]
    r["f0_obs"] = h(c_l) / r["pre_land_h"]
    r["f0_model"] = f0_model(c_l["vz"])
    r["post_land_h"] = h(c_l)
    # ground commands between landing and jump
    gd = []
    for i in range(L + 1, J):
        c = cm[i]
        gd.append({"i": i, "ground": c["ground"], "h_pre": h(c, False), "h_post": h(c), "decel": (h(c, False) - h(c)) / dtc(c),
                   "msc": c["movescale"], "maxspeed": c["maxspeed"], "fwd": c["fwd"]})
    r["ground_cmds"] = gd
    r["n_ground_cmds"] = J - L - 1
    r["t_land_to_jump"] = c_j["t_cmd"] - tl
    # msc recovery check: client movescale vs 1.15*(f0 + (1-f0)(t/T)^2), t from the start of the landing command
    f0 = r["f0_obs"]
    err = []
    for i in range(L + 1, (L2 if L2 else n)):
        tt = cm[i]["t_cmd"] - tl
        if tt >= REC_T:
            break
        err.append(cm[i]["movescale"] - MSC0 * (f0 + (1 - f0) * (tt / REC_T) ** 2))
    r["msc_model_err"] = stats([abs(e) for e in err])
    # jump command
    r["jump_h_pre"] = h(c_j, False)
    r["jump_h_post"] = h(c_j)
    r["jump_msc"] = c_j["movescale"]
    r["jump_maxspeed"] = c_j["maxspeed"]
    msc_j = c_j["maxspeed"] / WALK          # 3-decimal maxspeed = 173.5*msc (walk state) -> msc to 2e-5
    r["jump_msc_from_maxspeed"] = msc_j
    r["cap_sprint"] = SPRINT * msc_j
    r["cap_walk"] = WALK * msc_j
    # the jump command applies no friction (M2); the M3 cap is min(v_h, cap)
    r["jump_h_err_sprintcap"] = r["jump_h_post"] - min(r["jump_h_pre"], r["cap_sprint"])
    r["jump_h_err_walkcap"] = r["jump_h_post"] - min(r["jump_h_pre"], r["cap_walk"])
    r["jump_h_err_299"] = r["jump_h_post"] - min(r["jump_h_pre"], 299.0)
    V = c_j["pvz"] + 1.5 * G * dtc(c_j)
    r["jump_V"] = V
    r["jump_frac_obs"] = V * V / (2 * G * JUMP_H)
    tj = c_j["t_cmd"] - tl
    r["jump_frac_model"] = max(AMJ, min(1.0, AMJ + (1 - AMJ) * (tj - 0.15) / 0.60))
    r["carry_over_vs_launch"] = r["jump_h_post"] / r["launch_h"]
    r["carry_over_vs_preland"] = r["jump_h_post"] / r["pre_land_h"]
    # counterfactual without the landing slowdown: friction on the ground cmds, then the 299 cap
    cf = r["pre_land_h"]
    for g in gd:
        cf -= 1250.0 * dtc(cm[g["i"]])
    r["no_slowdown_counterfactual"] = min(cf, SPRINT * MSC0)
    # air after the jump: horizontal change per command
    if L2:
        air = [(h(cm[i]) - h(cm[i], False)) / dtc(cm[i]) for i in range(J + 1, L2)]
        r["air_dh_dt"] = stats(air)
        r["hop_airtime"] = cm[L2]["t_cmd"] - c_j["t_cmd"]
        r["hop_land_vz"] = cm[L2]["vz"]
        r["hop_land_h_pre"] = h(cm[L2], False)
        r["hop_land_h_post"] = h(cm[L2])
        r["msc_before_hop_land"] = cm[L2]["movescale"]
        r["msc_after_hop_land"] = cm[L2 + 1]["movescale"] if L2 + 1 < n else None
        r["sprint_after_hop_land"] = cm[L2 + 1]["sprint"] if L2 + 1 < n else None
        # W: time from the hop landing until v_h reaches 299 (sprint cap)
        k = next((i for i in range(L2, n) if h(cm[i]) >= 298.999), None)
        r["t_hop_land_to_299"] = (cm[k]["t_cmd"] - cm[L2]["t_cmd"]) if k else None
        # no input: time to stop
        k0 = next((i for i in range(L2, n) if h(cm[i]) == 0.0), None)
        r["t_hop_land_to_stop"] = (cm[k0]["t_cmd"] - cm[L2]["t_cmd"]) if k0 else None
    # client / dedi parity from the pad landing to 0.5 s after the hop landing
    end = n if not L2 else min(n, L2 + 60)
    dmax, msc_d, miss = 0.0, 0.0, 0
    for i in range(L - 5, end):
        s = sv.get(cm[i]["cmd"])
        if not s:
            miss += 1
            continue
        dmax = max(dmax, max(abs(cm[i][k] - s[k]) for k in ("pox", "poy", "poz", "pvx", "pvy", "pvz")))
        if s.get("movescale") is not None and cm[i].get("movescale") is not None:
            msc_d = max(msc_d, abs(cm[i]["movescale"] - s["movescale"]))
    r["sv_max_state_diff"] = dmax
    r["sv_max_msc_diff"] = msc_d
    r["sv_missing_cmds"] = miss
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json", default=None)
    ap.add_argument("--params", default=None)
    a = ap.parse_args()
    rows = []
    say("=== M4b pad re-jump (Octane jump pad at reset origin + (300,0,0), lane C, 120 fps) ===")
    for f in a.sessions:
        S = lg_load.load(f)
        cz = census(f)
        sel = [t for t in S["trials"] if t["schedule"] in SCHEDS]
        say(f"session {S['folder']}: {len(sel)} scored pad trials (ok, not warm-up), parse errors {S['parse_errors']}")
        if cz:
            say("  census: " + ", ".join(f"{k} {cz.get(k)}" for k in ("sprintspeed", "speed", "jumpHeight",
                                                                      "antiMultiJumpHeightFrac", "landSlowdownDuration",
                                                                      "deceleration")))
        for t in sel:
            j = t["join"]
            r = analyse_trial(t)
            if r is None:
                say(f"  r{t['run']} {t['schedule']}: events not found -> not used")
                continue
            r["session"] = S["folder"]
            r["join_cmds"], r["join_ok"], r["join_bad"] = j["cmds"], j["cmds_with_dt"], j["state_bad"]
            rows.append(r)
    say("\n--- 1. Per trial (client commands; t from the start of the pad landing command) ---")
    say(f"{'run':>5s} {'schedule':17s} {'fps':>6s} {'launch_h':>8s} {'vz_land':>8s} {'f0 obs':>7s} {'f0 mdl':>7s} "
        f"{'h_land':>7s} {'gnd':>3s} {'h_preJ':>7s} {'h_postJ':>7s} {'260msc':>7s} {'err':>7s} {'frac':>6s} {'carry%':>6s} "
        f"{'msc_hop':>7s} {'sv_dmax':>7s}")
    for r in rows:
        say(f"{r['run']:5d} {r['sched']:17s} {r['fps']:6.2f} {r['launch_h']:8.3f} {r['pre_land_vz']:8.2f} {r['f0_obs']:7.5f} "
            f"{r['f0_model']:7.5f} {r['post_land_h']:7.3f} {r['n_ground_cmds']:3d} {r['jump_h_pre']:7.3f} {r['jump_h_post']:7.3f} "
            f"{r['cap_sprint']:7.3f} {r['jump_h_err_sprintcap']:7.3f} {r['jump_frac_obs']:6.4f} "
            f"{100 * r['carry_over_vs_launch']:6.2f} {str(r.get('msc_after_hop_land')):>7s} {r['sv_max_state_diff']:7.3f}")
    res = {"trials": rows, "groups": {}}
    say("\n--- 2. Group statistics ---")
    for sc in SCHEDS:
        rr = [r for r in rows if r["sched"] == sc]
        if not rr:
            continue
        g = {}
        for k in ("launch_h", "pre_land_h", "pre_land_vz", "f0_obs", "f0_model", "post_land_h", "n_ground_cmds",
                  "t_land_to_jump", "jump_h_pre", "jump_h_post", "jump_msc_from_maxspeed", "cap_sprint", "cap_walk",
                  "jump_h_err_sprintcap", "jump_h_err_walkcap", "jump_h_err_299", "jump_V", "jump_frac_obs",
                  "jump_frac_model", "carry_over_vs_launch", "carry_over_vs_preland", "no_slowdown_counterfactual",
                  "hop_airtime", "hop_land_vz", "msc_before_hop_land", "msc_after_hop_land", "t_hop_land_to_299",
                  "t_hop_land_to_stop", "sv_max_state_diff", "sv_max_msc_diff"):
            g[k] = stats([r.get(k) for r in rr])
        g["ground_decel"] = stats([gd["decel"] for r in rr for gd in r["ground_cmds"]])
        g["ground_cmd_fwd"] = sorted({gd["fwd"] for r in rr for gd in r["ground_cmds"]})
        g["msc_model_err_max"] = max(r["msc_model_err"]["max"] for r in rr if r["msc_model_err"].get("n"))
        g["air_dh_dt"] = stats([r["air_dh_dt"]["mean"] for r in rr if r.get("air_dh_dt", {}).get("n")])
        res["groups"][sc] = g
        say(f"\n[{sc}] n={len(rr)}")
        say("  pad launch |h| (u/s):                 ", fmt(g["launch_h"]))
        say("  impact vz on the landing cmd (u/s):   ", fmt(g["pre_land_vz"], 2))
        say("  landing f0 observed (post/pre |h|):   ", fmt(g["f0_obs"], 5), " model clamp(a+b vz^2):", fmt(g["f0_model"], 5))
        say("  |h| after the landing cmd (u/s):      ", fmt(g["post_land_h"]))
        say("  ground cmds before the jump cmd:      ", fmt(g["n_ground_cmds"], 0), " W on them:", g["ground_cmd_fwd"],
            " decel (u/s^2):", fmt(g["ground_decel"], 1))
        say("  landing -> jump cmd (s):              ", fmt(g["t_land_to_jump"], 4))
        say("  msc model (OCTANE recovery) max |err| from landing to the hop landing:", f"{g['msc_model_err_max']:.5f}")
        say("  jump cmd: |h| pre                     ", fmt(g["jump_h_pre"]))
        say("  jump cmd: |h| post                    ", fmt(g["jump_h_post"]))
        say("  jump cmd msc (maxspeed/173.5):        ", fmt(g["jump_msc_from_maxspeed"], 5))
        say("  cap tests, post - min(pre, cap):  sprintspeed*msc", fmt(g["jump_h_err_sprintcap"], 4),
            "| walk*msc", fmt(g["jump_h_err_walkcap"], 3), "| 299", fmt(g["jump_h_err_299"], 3))
        say("  jump V (pvz + 1.5 g dt):              ", fmt(g["jump_V"], 3), " frac obs", fmt(g["jump_frac_obs"], 5),
            " M2 model", fmt(g["jump_frac_model"], 3))
        say("  carry-over |h| after jump / pad launch |h|:", fmt(g["carry_over_vs_launch"], 4))
        say("  counterfactual without landing slowdown (friction, then 299 cap):", fmt(g["no_slowdown_counterfactual"], 2))
        say("  air after the jump, d|h|/dt (u/s^2):  ", fmt(g["air_dh_dt"], 3))
        say("  hop air time (s):", fmt(g["hop_airtime"], 4), " hop landing vz:", fmt(g["hop_land_vz"], 2))
        say("  msc on the hop landing cmd -> next cmd:", fmt(g["msc_before_hop_land"], 4), "->", fmt(g["msc_after_hop_land"], 4))
        if sc.endswith("_w"):
            say("  W: hop landing -> |h| 299 (s):        ", fmt(g["t_hop_land_to_299"], 3))
        else:
            say("  no input: hop landing -> stop (s):    ", fmt(g["t_hop_land_to_stop"], 3))
        say("  client vs dedi, max |state diff| (u, u/s):", fmt(g["sv_max_state_diff"], 4), " max |msc diff|:",
            fmt(g["sv_max_msc_diff"], 4))
    say("\n--- 3. Hop landing (the soft landing after the re-jump): msc and sprint state ---")
    for r in rows:
        if r.get("hop_land_cmd"):
            say(f"  r{r['run']} {r['sched']:17s} hop landing vz {r['hop_land_vz']:8.2f}  |h| {r['hop_land_h_pre']:7.3f} -> "
                f"{r['hop_land_h_post']:7.3f}  msc {r['msc_before_hop_land']:.4f} -> {r['msc_after_hop_land']:.4f}  "
                f"sprint after {r['sprint_after_hop_land']}  fps {r['fps']:.2f}")
    say("\n--- 4. W-held drift in the air after the re-jump (rejump_w) ---")
    for r in rows:
        if r["sched"].endswith("_w") and r.get("air_dh_dt"):
            say(f"  r{r['run']}: d|h|/dt {fmt(r['air_dh_dt'], 3)}; wish cap 60*msc ~ {60 * r['jump_msc_from_maxspeed']:.1f} "
                f"< |h| {r['jump_h_post']:.1f} -> AirAccelerate adds nothing")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(build_params(res), fh, indent=1)


def build_params(res):
    def P(value, unit, source, s=None, note=""):
        d = {"value": value, "unit": unit, "source": source}
        if s and s.get("n"):
            d["n"] = s["n"]
            d["spread"] = {"sd": round(s["sd"], 6), "min": round(s["min"], 6), "max": round(s["max"], 6)}
        if note:
            d["note"] = note
        return d
    out = {"_scope": "Octane, R5Flowstate S21 client / S3 dedi, 120 fps, lane C; sessions M4b_octane (m4b_pad_* only) + "
                     "M4b_octane2; values computed by pad_rejump_analysis.py"}
    for sc, g in res["groups"].items():
        k = "w" if sc.endswith("_w") else "noinput"
        out[f"{k}.landing_f0"] = P(round(g["f0_obs"]["mean"], 6), "-", "observed post/pre |h| on the landing cmd; "
                                   "OCTANE model clamp(1.996467 - 1.6714e-6 vz^2, 0, 1) = "
                                   f"{g['f0_model']['mean']:.5f}", g["f0_obs"])
        out[f"{k}.ground_decel_before_jump"] = P(round(g["ground_decel"]["mean"], 2), "u/s^2",
                                                 "observed on the 3 ground cmds (not x msc)", g["ground_decel"])
        out[f"{k}.jump_cap_rule"] = P("min(|h|, sprintspeed 260 * msc)", "u/s",
                                      "observed post - prediction on the jump cmd", g["jump_h_err_sprintcap"],
                                      "walk*msc and 299 rejected (see results.json)")
        out[f"{k}.h_after_rejump"] = P(round(g["jump_h_post"]["mean"], 3), "u/s", "observed", g["jump_h_post"])
        out[f"{k}.carry_over_fraction"] = P(round(g["carry_over_vs_launch"]["mean"], 5), "-",
                                            "|h| after the re-jump / pad launch |h|", g["carry_over_vs_launch"])
        out[f"{k}.rejump_height_frac"] = P(round(g["jump_frac_obs"]["mean"], 5), "-",
                                           "observed V^2/(2 g 56); M2 multi-jump rule gives 0.3", g["jump_frac_obs"])
        out[f"{k}.msc_after_hop_landing"] = P(round(g["msc_after_hop_land"]["mean"], 4), "-",
                                              "observed: the soft hop landing replaces the slowdown (f0 = 1)",
                                              g["msc_after_hop_land"])
    return out


if __name__ == "__main__":
    main()
    # analysis_output.txt is the stdout of this script (redirect it)
