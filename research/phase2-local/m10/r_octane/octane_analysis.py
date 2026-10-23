#!/usr/bin/env python3
"""M10 track R (3) Octane: stim re-use / interactions, pad direction / arcs / upgrades, ceiling surf (R5Flowstate local hybrid:
S21 client + S3 dedi + SDK, offline, 120 fps).

  py -3 octane_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loader: ../r_grapple/m10_load.py (M6-A2 raw-log loader) + the dedi [M10-OCT] lines (health,
speed_boost and stim_visual_effect severities at 10 Hz; the traced ceiling heights).
- stim: msc per client usercmd (MOVE-TRACE msc): onset = first usercmd with msc > 1.16 after the tactical press, end of the
  plateau = last usercmd with msc within 0.001 of the plateau, back = first usercmd at msc 1.15 again; health from the dedi
- pad: the launch usercmd = the first usercmd whose post vz exceeds 500 after a grounded pre-state; launch vector = its post
  velocity (the pad replaces velocity, M4); apex = max post z - floor
- ceiling: after the launch, a usercmd is 'pinned' when it is airborne and its post z is within 0.5 u of the pre z while the pre
  vz > 0 or post vz > 0; surf = the pinned run from the first contact; exit = first usercmd after the run
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "r_grapple")))
import m10_load  # noqa: E402

IN_JUMP, IN_DUCK, IN_OFF1 = 0x2, 0x4, 0x200000
FLOOR = 294.92
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def r(x, n=2):
    return None if x is None else round(x, n)


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": m, "sd": sd, "min": min(vals), "max": max(vals)}


def fmt(s, nd=2):
    if not s or s.get("n", 0) == 0:
        return "n=0"
    if s["n"] == 1:
        return "%.*f (n=1)" % (nd, s["mean"])
    return "%.*f (sd %.*f, %.*f..%.*f, n=%d)" % (nd, s["mean"], nd, s["sd"], nd, s["min"], nd, s["max"], s["n"])


def press_idx(cs, bit):
    return [i for i in range(len(cs)) if cs[i]["buttons"] & bit and (i == 0 or not cs[i - 1]["buttons"] & bit)]


def oct_lines(folder):
    out, ceil = {}, {}
    for f in sorted(m10_load.L._files(folder, "server", "script")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[M10-OCT]" not in raw:
                    continue
                body = raw.split("[M10-OCT]", 1)[1]
                m = re.search(r"run=(\d+)", body)
                if not m:
                    continue
                run = int(m.group(1))
                if " ceiling" in body:
                    ceil[run] = {float(a): float(b) for a, b in re.findall(r" (-?\d+):(-?[\d.]+)", body.split("ceiling", 1)[1])}
                    continue
                kv = dict(re.findall(r"(\w+)=(\S+)", body))
                out.setdefault(run, []).append({"t": float(kv["t"]), "hp": int(kv["hp"]), "boost": float(kv["boost"]), "stimfx": float(kv["stimfx"])})
    return out, ceil


def stim_row(T, O):
    cs = T["cmds"]
    E = {"run": T["run"], "schedule": T["schedule"]}
    taps = press_idx(cs, IN_OFF1)
    if not taps:
        return E
    t0 = cs[taps[0]]["t"]
    on = next((i for i in range(taps[0], len(cs)) if cs[i]["msc"] > 1.16), None)
    if on is None:
        E["onset"] = None
        return E
    plat = cs[min(on + 5, len(cs) - 1)]["msc"]
    last = max(i for i in range(on, len(cs)) if abs(cs[i]["msc"] - plat) < 0.001)
    back = next((i for i in range(last, len(cs)) if cs[i]["msc"] <= 1.1501), None)
    E.update(onset_s=r(cs[on]["t"] - t0, 4), plateau_msc=r(plat, 6), plateau_s=r(cs[last]["t"] - cs[on]["t"], 3),
             back_s=r(cs[back]["t"] - cs[on]["t"], 3) if back is not None else None, taps=len(taps))
    if len(taps) > 1:
        t1 = cs[taps[1]]["t"]
        E["second_tap_s"] = r(t1 - t0, 3)
        # a refresh would extend the plateau past 6.0 s after the first onset or re-step msc
        E["msc_change_after_second_tap"] = r(max(abs(cs[i]["msc"] - cs[taps[1]]["msc"]) for i in range(taps[1], min(taps[1] + 40, len(cs)))), 6)
    hp = O.get(T["run"], [])
    if hp:
        E["hp_start"] = hp[0]["hp"]
        E["hp_end"] = hp[-1]["hp"]
        drops = [(b["t"], a["hp"] - b["hp"]) for a, b in zip(hp, hp[1:]) if b["hp"] < a["hp"]]
        E["hp_drops"] = [[r(t - hp[0]["t"], 2), d] for t, d in drops]
        on_b = next((q["t"] for q in hp if q["boost"] > 0), None)
        off_b = next((q["t"] for q in hp if on_b is not None and q["t"] > on_b and q["boost"] == 0), None)
        E["dedi_boost_s"] = r(off_b - on_b, 2) if on_b is not None and off_b is not None else None
        fx_on = next((q["t"] for q in hp if q["stimfx"] > 0), None)
        fx_off = next((q["t"] for q in hp if fx_on is not None and q["t"] > fx_on and q["stimfx"] == 0), None)
        E["dedi_stimfx_s"] = r(fx_off - fx_on, 2) if fx_on is not None and fx_off is not None else None
    return E


def launch_idx(cs):
    for i in range(1, len(cs)):
        if cs[i]["pvz"] > 500 and cs[i]["vz"] < 400:
            return i
    return None


def pad_row(T):
    cs = T["cmds"]
    E = {"run": T["run"], "schedule": T["schedule"]}
    i = launch_idx(cs)
    if i is None:
        E["launch"] = None
        return E
    c = cs[i]
    v = (c["pvx"], c["pvy"], c["pvz"])
    E["launch_v"] = [r(x, 2) for x in v]
    E["launch_speed"] = r(math.sqrt(sum(x * x for x in v)), 2)
    E["launch_elev_deg"] = r(math.degrees(math.atan2(v[2], math.hypot(v[0], v[1]))), 2)
    E["launch_az_deg"] = r(math.degrees(math.atan2(v[1], v[0])), 2) if math.hypot(v[0], v[1]) > 1 else None
    E["pre_v"] = [r(c["vx"], 2), r(c["vy"], 2), r(c["vz"], 2)]
    E["yaw"] = c.get("yaw")
    E["duck"] = c["duck"]
    E["keys"] = "%s%s%s%s%s" % ("W" if c["buttons"] & 0x8 else "", "S" if c["buttons"] & 0x10 else "", "A" if c["buttons"] & 0x200 else "",
                                "D" if c["buttons"] & 0x400 else "", "C" if c["buttons"] & IN_DUCK else "")
    seg = cs[i:]
    E["apex"] = r(max(q["poz"] for q in seg) - FLOOR, 1)
    # double jump: the first jump press after the launch
    js = [k for k in press_idx(cs, IN_JUMP) if k > i]
    if js:
        q = cs[js[0]]
        E["dj_dv"] = [r(q["pvx"] - q["vx"], 2), r(q["pvy"] - q["vy"], 2), r(q["pvz"] - q["vz"], 2)]
        E["dj_pre_vh"] = r(hs(q, False), 2)
        E["dj_post_v"] = [r(q["pvx"], 2), r(q["pvy"], 2), r(q["pvz"], 2)]
        # lateral (y) speed 0.5 s after the double jump: does holding D keep steering (air control)?
        t = q["t"]
        later = next((w for w in cs[js[0]:] if w.get("t") is not None and w["t"] - t >= 0.5), None)
        E["vy_05s_after_dj"] = r(later["pvy"], 2) if later else None
        E["vx_05s_after_dj"] = r(later["pvx"], 2) if later else None
    return E


def ceil_row(T, C):
    cs = T["cmds"]
    E = pad_row(T)
    E["ceiling"] = C.get(T["run"])
    i = E.get("launch_v") and launch_idx(cs)
    if not i:
        i = press_idx(cs, IN_JUMP)[0] if press_idx(cs, IN_JUMP) else None
        if i is None:
            return E
    pinned = []
    for k in range(i + 1, len(cs)):
        c = cs[k]
        if c["ground"] and c["vz"] <= 0:
            break
        # pinned: the client post z within 0.5 u of the pre z while the post vz exceeds 100 u/s (impossible in free flight)
        if abs(c["poz"] - c["oz"]) < 0.5 and c["pvz"] > 100:
            pinned.append(k)
    if not pinned:
        E["surf"] = False
        return E
    k0 = pinned[0]
    run = [k0]
    for k in pinned[1:]:
        if k == run[-1] + 1:
            run.append(k)
        else:
            break
    c0, c1 = cs[run[0]], cs[run[-1]]
    E["surf"] = True
    E["contact_s"] = r(c0["t"] - cs[i]["t"], 3) if c0.get("t") and cs[i].get("t") else None
    E["contact_z"] = r(c0["poz"] - FLOOR, 2)
    E["contact_vz_pre"] = r(c0["vz"], 2)
    E["contact_vz_post"] = r(c0["pvz"], 2)
    # the dedi row of the same usercmd (authority): S3 dedi vs the S21 client prediction
    sv = T["sv"].get(c0["cmd"])
    if sv:
        E["sv_contact_vz_post"] = r(sv["pvz"], 2)
        E["sv_contact_vh_post"] = r(math.hypot(sv["pvx"], sv["pvy"]), 2)
        E["sv_contact_z"] = r(sv["poz"] - FLOOR, 2)
    later = [T["sv"].get(cs[k]["cmd"]) for k in run]
    E["sv_pinned_cmds"] = sum(1 for q in later if q and abs(q["poz"] - q["oz"]) < 0.5 and q["pvz"] > 100)
    E["pinned_cmds"] = len(run)
    E["pinned_s"] = r(sum(cs[k]["dt"] or 1 / 120.0 for k in run), 3)
    E["pinned_vz_first_last"] = [r(c0["pvz"], 1), r(c1["pvz"], 1)]
    E["pinned_vh_first_last"] = [r(hs(c0), 1), r(hs(c1), 1)]
    E["pinned_dx"] = r(c1["pox"] - c0["ox"], 1)
    E["pinned_dy"] = r(c1["poy"] - c0["oy"], 1)
    E["pinned_x_end"] = r(c1["pox"], 1)
    if run[-1] + 1 < len(cs):
        c = cs[run[-1] + 1]
        E["exit_v"] = [r(c["pvx"], 1), r(c["pvy"], 1), r(c["pvz"], 1)]
        E["exit_z"] = r(c["poz"] - FLOOR, 1)
    E["apex_after"] = r(max(q["poz"] for q in cs[run[-1]:]) - FLOOR, 1)
    return E


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    res = {"stim": [], "pad": [], "ceiling": [], "interact": []}
    say("# M10 R3 Octane analysis")
    by = {}
    for f in a.sessions:
        S = m10_load.load(f)
        O, C = oct_lines(f)
        sc = [t for t in S["runner"]["trials"] if not t.get("warmup")]
        bad = [t for t in sc if not t.get("ok")]
        say("session %s: scored %d, excluded %d %s" % (S["folder"], len(S["trials"]), len(bad),
                                                        ["r%d %s (%s)" % (t["run"], t["schedule"], t["why"]) for t in bad]))
        for T in S["trials"]:
            by.setdefault(T["schedule"], []).append((T, O, C))
    say("\n## 1. Stim (msc from client usercmds; health / severities from the dedi at 10 Hz)")
    for n in sorted(k for k in by if k.startswith(("m10_o_stim", "m10_o_restim"))):
        rows = [stim_row(T, O) for T, O, C in by[n]]
        res["stim"].extend(rows)
        for E in rows:
            say("  r%d %-18s onset %s plateau msc %s plateau_s %s back_s %s 2nd tap %s msc change after 2nd %s | hp %s->%s drops %s | dedi boost %s s stimfx %s s" % (
                E["run"], n[6:], E.get("onset_s"), E.get("plateau_msc"), E.get("plateau_s"), E.get("back_s"), E.get("second_tap_s"),
                E.get("msc_change_after_second_tap"), E.get("hp_start"), E.get("hp_end"), E.get("hp_drops"), E.get("dedi_boost_s"), E.get("dedi_stimfx_s")))
    say("\n## 2. Stim with slide / hops vs controls (client usercmds)")
    for n in ("m10_o_stim_slide", "m10_o_ctrl_slide", "m10_o_stim_hop", "m10_o_ctrl_hop", "m10_o_stim_sprint"):
        vals = {"slide_start_post": [], "slide_peak": [], "slide_1s": [], "hop_vh": [], "sprint_cap": []}
        for T, O, C in by.get(n, []):
            cs = T["cmds"]
            i = next((k for k in range(len(cs)) if cs[k]["slide"]), None)
            if i is not None:
                vals["slide_start_post"].append(hs(cs[i]))
                seg = [c for c in cs[i:] if c["slide"]]
                vals["slide_peak"].append(max(hs(c) for c in seg))
                q = next((c for c in cs[i:] if c.get("t") and c["t"] - cs[i]["t"] >= 1.0), None)
                if q is not None:
                    vals["slide_1s"].append(hs(q))
            for k in press_idx(cs, IN_JUMP):
                vals["hop_vh"].append(hs(cs[k]))
            gr = [hs(c) for c in cs if c["ground"] and not c["slide"] and c["msc"] > 1.4]
            if gr:
                vals["sprint_cap"].append(max(gr))
        row = {k: stats(v) for k, v in vals.items()}
        res["interact"].append({"schedule": n, **{k: {q: r(w, 3) for q, w in s.items()} for k, s in row.items()}})
        say("  %-16s slide start %s | slide peak %s | slide +1 s %s | v_h at each jump %s | stim sprint cap %s" % (
            n[6:], fmt(row["slide_start_post"]), fmt(row["slide_peak"]), fmt(row["slide_1s"]), fmt(row["hop_vh"]), fmt(row["sprint_cap"])))
    say("\n## 3. Pad launch direction, arcs, upgrades, double jump")
    for n in sorted(k for k in by if k.startswith(("m10_o_pad", "m10_o_noceil"))):
        rows = [pad_row(T) for T, O, C in by[n]]
        res["pad"].extend(rows)
        g = {k: stats([E.get(k) for E in rows]) for k in ("launch_speed", "launch_elev_deg", "launch_az_deg", "apex")}
        say("  %-18s speed %s | elev %s | az %s | apex %s | keys %s | yaw %s | pre_v %s" % (
            n[6:], fmt(g["launch_speed"]), fmt(g["launch_elev_deg"]), fmt(g["launch_az_deg"]), fmt(g["apex"], 1),
            sorted(set(E.get("keys", "-") for E in rows)), sorted(set(E.get("yaw") for E in rows if E.get("yaw") is not None)),
            rows[0].get("pre_v") if rows else None))
        if any("dj_dv" in E for E in rows):
            for E in rows:
                say("      r%d dj dv %s pre_vh %s post %s | v 0.5 s after: x %s y %s" % (E["run"], E.get("dj_dv"), E.get("dj_pre_vh"), E.get("dj_post_v"),
                                                                                E.get("vx_05s_after_dj"), E.get("vy_05s_after_dj")))
    say("\n## 4. Ceiling surf")
    for n in sorted(k for k in by if k.startswith("m10_o_ceil")):
        for T, O, C in by[n]:
            E = ceil_row(T, C)
            res["ceiling"].append(E)
            say("  r%d %-18s ceil %s | launch %s elev %s | surf %s contact_z %s vz pre/post %s/%s pinned %s cmds %s s vz %s vh %s dx %s dy %s x_end %s exit_v %s apex_after %s" % (
                E["run"], n[6:], E.get("ceiling"), E.get("launch_speed"), E.get("launch_elev_deg"), E.get("surf"), E.get("contact_z"),
                E.get("contact_vz_pre"), E.get("contact_vz_post"), E.get("pinned_cmds"), E.get("pinned_s"), E.get("pinned_vz_first_last"),
                E.get("pinned_vh_first_last"), E.get("pinned_dx"), E.get("pinned_dy"), E.get("pinned_x_end"), E.get("exit_v"), E.get("apex_after")))
    say("\n## 5. Ceiling surf per group: contact vz, pinned time vs the vz-exhaustion time vz/600 (g 750 x the pad slow-mo 0.8),"
        " distance, exit")
    grp = {}
    for E in res["ceiling"]:
        grp.setdefault(E["schedule"], []).append(E)
    res["ceiling_groups"] = {}
    for n in sorted(grp):
        g = grp[n]
        pin = stats([E.get("pinned_s") for E in g])
        cvz = stats([E.get("contact_vz_post") for E in g])
        pred = stats([E["contact_vz_post"] / 600.0 if E.get("contact_vz_post") and E["contact_vz_post"] > 0 else None for E in g])
        dx = stats([E.get("pinned_dx") for E in g])
        ex = stats([E["exit_v"][2] for E in g if E.get("exit_v")])
        exh = stats([math.hypot(E["exit_v"][0], E["exit_v"][1]) for E in g if E.get("exit_v")])
        res["ceiling_groups"][n] = {k: {q: r(w, 3) for q, w in v.items()} for k, v in
                                    (("pinned_s", pin), ("contact_vz", cvz), ("vz_exhaust_s", pred), ("pinned_dx", dx), ("exit_vz", ex), ("exit_vh", exh))}
        svz = stats([E.get("sv_contact_vz_post") for E in g])
        svh = stats([E.get("sv_contact_vh_post") for E in g])
        svp = stats([E.get("sv_pinned_cmds") for E in g])
        res["ceiling_groups"][n].update({"sv_contact_vz": {q: r(w, 3) for q, w in svz.items()}, "sv_contact_vh": {q: r(w, 3) for q, w in svh.items()},
                                         "sv_pinned_cmds": {q: r(w, 3) for q, w in svp.items()}})
        say("  %-20s client pinned %s s | client contact vz %s | vz/600 %s s | dx %s | exit vz %s vh %s || dedi on the contact usercmd: vz %s vh %s, dedi pinned cmds %s" % (
            n[6:], fmt(pin, 3), fmt(cvz, 1), fmt(pred, 3), fmt(dx, 1), fmt(ex, 1), fmt(exh, 1), fmt(svz, 1), fmt(svh, 1), fmt(svp, 1)))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    if a.params:
        P = {"_scope": "Octane, R5Flowstate local hybrid (S21 client + S3 dedi + SDK), offline, 120 fps; octane_analysis.py"}
        stim = [E for E in res["stim"] if E.get("onset_s")]
        for key, field in (("stim.onset_s", "onset_s"), ("stim.plateau_msc", "plateau_msc"), ("stim.plateau_s", "plateau_s"), ("stim.back_s", "back_s")):
            st = stats([E.get(field) for E in stim])
            if st["n"]:
                P[key] = {"value": r(st["mean"], 4), "spread": {"sd": r(st["sd"], 4), "min": r(st["min"], 4), "max": r(st["max"], 4)}, "evidence": "meas", "n": st["n"]}
        P["stim.health_cost"] = {"value": 20, "evidence": "meas (dedi health drop per stim) + src STIM_HEALTH_COST", "n": len(stim)}
        pads = {}
        for E in res["pad"]:
            pads.setdefault(E["schedule"], []).append(E)
        for n, rows in sorted(pads.items()):
            for field in ("launch_speed", "launch_elev_deg", "apex"):
                st = stats([E.get(field) for E in rows])
                if st["n"]:
                    P["pad.%s.%s" % (n[6:], field)] = {"value": r(st["mean"], 3), "spread": {"sd": r(st["sd"], 3)}, "evidence": "meas", "n": st["n"]}
        for n, g in sorted(res["ceiling_groups"].items()):
            P["ceiling.%s" % n[6:]] = {"value": {"client_pinned_s": g["pinned_s"].get("mean"), "client_contact_vz": g["contact_vz"].get("mean"),
                                                 "dedi_contact_vz": g.get("sv_contact_vz", {}).get("mean"), "dedi_pinned_cmds": g.get("sv_pinned_cmds", {}).get("mean")},
                                       "evidence": "meas (client prediction vs dedi authority)", "n": g["pinned_s"].get("n")}
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
