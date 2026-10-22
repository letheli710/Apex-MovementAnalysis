#!/usr/bin/env python3
"""M8 track R: superglide coverage over ledge heights, approach speeds and lateral approaches (R5Flowstate S21, local).

  py -3 sg_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py). stdlib only, no local paths. Schedules
m8_sg_<approach>_<var>_k<K> (tools/hsd_trial.py): the client thread waits for the traversal start (waittrav), then presses
jump (var mb), jump + crouch on the next frame (var sg) or nothing (var none) K frames later. Sessions run the native code
path (runner both_cvars mantle_boost_enabled=0) unless the runner says otherwise; the ledge height comes from the runner
geometry_wall_z (H = 232 - (294.92 - wall_z), M6-A2).

The traversal is the MOVE-TRACE gap (the mantle runs outside FullWalkMove, M6-A2 4); press timing comes from the client HSD
frames (in_jump / in_duck), relative to the last usercmd before the gap (traversal start) and the first after it (exit).
Classes as M6-A2 sg_trial (native): superglide (exit |v_h| > 380 and vz > 200), mantle_jump_fast (305 < |v_h| <= 380, vz > 200;
seen as 328.98 = 1.1 x 299 after a jump-only press when the approach touched the face first), mantle_jump (vz > 200), jump_on_top (a
ground jump after the exit), cut_no_jump (traversal cut short / airborne exit without a jump), mantle_only.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

IN_JUMP, IN_DUCK = 0x2, 0x4
FLOOR = 294.92
G = 750.0
NAME_RE = re.compile(r"m8_sg_(spr|walk|slide|ang|wd)_(sg|mb|none)_k(\d+)")


def r(x, n=3):
    return None if x is None else round(x, n)


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def edges(cmds, bit, start=1):
    return [i for i in range(max(start, 1), len(cmds)) if cmds[i]["buttons"] & bit and not cmds[i - 1]["buttons"] & bit]


def trial_row(T, H, fsm):
    cs = T["cmds"]
    m = NAME_RE.fullmatch(T["schedule"])
    app, var, K = m.group(1), m.group(2), int(m.group(3))
    R = {"run": T["run"], "schedule": T["schedule"], "H": H, "fsm": fsm, "approach": app, "var": var, "K": K, "fps": T["fps"],
         "join": [T["join"]["joined"], T["join"]["cmds"]]}
    js = edges(cs, IN_JUMP)
    if not js:
        R["class"] = "no_jump"
        return R
    j = js[0]
    R["approach_jump"] = {"pre_h": r(hs(cs[j], False)), "post_h": r(hs(cs[j])), "post_vz": r(cs[j]["pvz"]),
                          "dir": r(math.degrees(math.atan2(cs[j]["pvy"], cs[j]["pvx"])), 2), "duck": cs[j]["duck"], "slide": cs[j]["slide"]}
    gaps = [i for i in range(j + 1, len(cs)) if cs[i]["cmd"] - cs[i - 1]["cmd"] != 1]
    # wall contact (climb) before the traversal: v_h drops below 50 from > 150
    k = next((i for i in range(j + 1, len(cs)) if hs(cs[i], False) > 150 and hs(cs[i]) < 50), None)
    R["contact_h"] = r(hs(cs[k], False)) if k is not None else None
    if not gaps:
        R["class"] = "no_traversal"
        land = next((i for i in range(j + 1, len(cs)) if cs[i]["ground"] == 1), None)
        R["landed_z"] = r(cs[land]["oz"] - FLOOR, 2) if land is not None else None
        return R
    g = gaps[0]
    last, first = cs[g - 1], cs[g]
    t0, t1 = last.get("t"), first.get("t")
    R["trav"] = {"start_z": r(last["poz"] - FLOOR, 2), "start_vz": r(last["pvz"]), "start_h": r(hs(last)),
                 "duration": r(t1 - t0, 4) if (t0 is not None and t1 is not None) else None,
                 "exit_z": r(first["oz"] - FLOOR, 2), "rise": r(first["oz"] - last["poz"], 2)}
    fr = T["frames"]
    fj = [i for i in range(1, len(fr)) if fr[i]["in_jump"] and not fr[i - 1]["in_jump"]]
    fd = [i for i in range(1, len(fr)) if fr[i]["in_duck"] and not fr[i - 1]["in_duck"]]
    press = next((fr[i] for i in fj if t0 is not None and fr[i]["t"] > t0 + 1e-4), None)
    R["press_rel_start"] = r(press["t"] - t0, 4) if press and t0 is not None else None
    R["press_before_exit"] = r(t1 - press["t"], 4) if press and t1 is not None else None
    if press:
        dk = next((fr[i] for i in fd if fr[i]["t"] >= press["t"] - 1e-4), None)
        R["duck_minus_jump"] = r(dk["t"] - press["t"], 4) if dk else None
    R["exit"] = {"pre": [r(first["vx"]), r(first["vy"]), r(first["vz"])], "post": [r(first["pvx"]), r(first["pvy"]), r(first["pvz"])],
                 "pre_h": r(hs(first, False)), "post_h": r(hs(first)), "ground": first["ground"], "duck": first["duck"],
                 "fwd": first["fwd"], "side": first["sidemove"], "yaw": r(first.get("yaw"), 2),
                 "dir": r(math.degrees(math.atan2(first["vy"], first["vx"])), 2) if hs(first, False) > 1 else None}
    sv = T["sv"].get(first["cmd"])
    R["exit"]["sv_pre_h"] = r(math.hypot(sv["vx"], sv["vy"])) if sv else None
    R["exit"]["sv_pre_vz"] = r(sv["vz"]) if sv else None
    eh, ev = hs(first, False), first["vz"]
    jt = [i for i in edges(cs, IN_JUMP, g) if cs[i]["ground"] == 1 and cs[i]["oz"] > FLOOR + 30]
    if eh > 380 and ev > 200:
        cls = "superglide"
    elif eh > 305 and ev > 200:
        cls = "mantle_jump_fast"
    elif ev > 200:
        cls = "mantle_jump"
    elif jt:
        cls = "jump_on_top"
    elif first["ground"] == 0 or (R["trav"]["exit_z"] is not None and R["trav"]["exit_z"] < H - 5):
        cls = "cut_no_jump"
    else:
        cls = "mantle_only"
    R["class"] = cls
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
        wz = run.get("geometry_wall_z")
        H = round(232.0 - (FLOOR - wz)) if wz is not None else None
        fsm = (run.get("both_cvars") or {}).get("mantle_boost_enabled", "1") != "0"
        rej = [(t["run"], t["schedule"], t["why"]) for t in run["trials"] if not t.get("ok") and not t.get("warmup")]
        metas.append({"folder": s["folder"], "H": H, "fsm_on": fsm, "both_cvars": run.get("both_cvars"), "scored": len(s["trials"]),
                      "rejected": rej})
        for T in s["trials"]:
            if NAME_RE.fullmatch(T["schedule"]):
                rows.append(trial_row(T, H, fsm))
    P = print
    P("M8 R: superglide coverage")
    P("=" * 100)
    for m in metas:
        P(f"{m['folder']}: H {m['H']} fsm_on {m['fsm_on']} both_cvars {m['both_cvars']} scored {m['scored']} rejected {m['rejected']}")
    P()
    P("1. PER TRIAL (times in s; press = first in_jump frame edge after the traversal start)")
    P("-" * 100)
    for R in rows:
        tv, ex = R.get("trav"), R.get("exit")
        aj = R.get("approach_jump") or {}
        P(f"H{R['H']} r{R['run']} {R['schedule']:<20} {R['class']:<12} jump_h {aj.get('post_h')} contact_h {R.get('contact_h')}"
          f" trav {('start_z %s dur %s rise %s' % (tv['start_z'], tv['duration'], tv['rise'])) if tv else None}"
          f" press +{R.get('press_rel_start')} ({R.get('press_before_exit')} before exit) duck-jump {R.get('duck_minus_jump')}"
          f" exit {('pre %s post_h %s duck %d fwd %s side %s dir %s' % (ex['pre'], ex['post_h'], ex['duck'], ex['fwd'], ex['side'], ex['dir'])) if ex else None}")
    P()
    P("2. OUTCOME vs PRESS TIME, by height / approach / variant (press_before_exit, s)")
    P("-" * 100)
    groups = {}
    for R in rows:
        groups.setdefault((R["fsm"], R["H"], R["approach"], R["var"]), []).append(R)
    summary = []
    for key in sorted(groups, key=lambda k: (k[0], k[1] or 0, k[2], k[3])):
        rs = sorted(groups[key], key=lambda R: (R.get("press_before_exit") if R.get("press_before_exit") is not None else 99))
        fsm, H, app, var = key
        cls = {}
        for R in rs:
            cls[R["class"]] = cls.get(R["class"], 0) + 1
        nonep = [R["trav"]["duration"] for R in rs if R.get("trav") and R["trav"]["duration"] and R["var"] == "none"]
        P(f"  fsm {int(fsm)} H{H} {app:<5} {var:<4} n {len(rs)} classes {cls}" + (f" T(no press) {L.fmt(L.stats(nonep), 3)}" if nonep else ""))
        for R in rs:
            if R["var"] != "none":
                P(f"      K {R['K']:>3} press_before_exit {R.get('press_before_exit')} press_rel_start {R.get('press_rel_start')}"
                  f" -> {R['class']:<12} exit_h {R['exit']['pre_h'] if R.get('exit') else None} vz {R['exit']['pre'][2] if R.get('exit') else None}")
        sg = [R for R in rs if R["class"] == "superglide"]
        summary.append({"fsm_on": fsm, "H": H, "approach": app, "var": var, "n": len(rs), "classes": cls,
                        "sg_exit_h": L.stats([R["exit"]["pre_h"] for R in sg]),
                        "sg_exit_vz": L.stats([R["exit"]["pre"][2] for R in sg]),
                        "sg_press_before_exit": [R["press_before_exit"] for R in sg],
                        "other_press_before_exit": [(R["press_before_exit"], R["class"]) for R in rs if R["class"] != "superglide" and R["var"] != "none"],
                        "trav_duration": L.stats([R["trav"]["duration"] for R in rs if R.get("trav") and R["trav"]["duration"]]),
                        "approach_h": L.stats([R["approach_jump"]["post_h"] for R in rs if R.get("approach_jump")])})
    P()
    P("3. SUPERGLIDE WINDOW per height / approach: press time from the traversal start (s) and the time left to the end of an")
    P("   unpressed traversal (T0 = mean duration of the var 'none' trials of the same height and approach)")
    P("-" * 100)
    T0 = {}
    for R in rows:
        if R["var"] == "none" and R.get("trav") and R["trav"]["duration"]:
            T0.setdefault((R["fsm"], R["H"], R["approach"]), []).append(R["trav"]["duration"])
    T0 = {k: sum(v) / len(v) for k, v in T0.items()}
    for S in summary:
        if S["var"] != "sg":
            continue
        key = (S["fsm_on"], S["H"], S["approach"])
        rs = [R for R in rows if (R["fsm"], R["H"], R["approach"], R["var"]) == (S["fsm_on"], S["H"], S["approach"], "sg")]
        t0 = T0.get(key)
        for R in rs:
            R["press_left"] = r(t0 - R["press_rel_start"], 4) if (t0 is not None and R.get("press_rel_start") is not None) else None
        ok = sorted(R["press_rel_start"] for R in rs if R["class"] == "superglide" and R.get("press_rel_start") is not None)
        S["T0"] = r(t0, 4) if t0 else None
        S["sg_press_rel_start"] = ok
        S["by_class"] = {}
        for R in rs:
            S["by_class"].setdefault(R["class"], []).append(R.get("press_rel_start"))
        P(f"  fsm {int(S['fsm_on'])} H{S['H']} {S['approach']:<5}: SG {len(ok)}/{S['n']} T0 {S['T0']} exit_h {L.fmt(S['sg_exit_h'], 3)}"
          f" vz {L.fmt(S['sg_exit_vz'], 2)} approach |v_h| {L.fmt(S['approach_h'], 1)}")
        for cls, ts in sorted(S["by_class"].items()):
            ts = sorted(t for t in ts if t is not None)
            if ts:
                P(f"      {cls:<12} n {len(ts):>2} press_rel_start {ts[0]:.4f}..{ts[-1]:.4f}"
                  + (f"  (time left {t0 - ts[-1]:.4f}..{t0 - ts[0]:.4f})" if t0 else ""))
    out = {"metas": metas, "rows": rows, "summary": summary}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    if a.params:
        params = []
        for S in summary:
            if S["var"] == "sg" and S["sg_exit_h"].get("n"):
                ok = [x for x in S["sg_press_before_exit"] if x is not None]
                okr = S.get("sg_press_rel_start") or []
                params.append({"name": f"sg_exit_h_H{S['H']}_{S['approach']}_fsm{int(S['fsm_on'])}", "value": r(S["sg_exit_h"]["mean"], 3),
                               "sd": r(S["sg_exit_h"]["sd"], 3), "n": S["sg_exit_h"]["n"], "unit": "u/s", "class": "meas",
                               "note": (f"SG {len(okr)}/{S['n']}; SG presses {min(okr):.4f}..{max(okr):.4f} s after the traversal start; T0 {S.get('T0')}"
                                        if okr else "")})
            if S["var"] == "sg":
                params.append({"name": f"sg_rate_H{S['H']}_{S['approach']}_fsm{int(S['fsm_on'])}",
                               "value": {k: len(v) for k, v in S.get("by_class", {}).items()}, "n": S["n"], "unit": "count by class",
                               "class": "meas", "note": "press sweep, see analysis_output section 3"})
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(params, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
