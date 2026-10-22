#!/usr/bin/env python3
"""M8 track R2: Revenant long climb feasibility probe (R5Flowstate S21, local offline).

  py -3 revenant_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py). stdlib only, no local paths. Schedules m8r2_* on the lane-A
rock (tools/hsd_trial.py): geometry h<H> = one rock with its top H u above the floor, s<H> = rocks stacked 470 u apart
with the top one at H. The ledge (top surface) is at floor + H + ~6 (M6-A2).

Per trial (client first-time usercmds joined to client frames; climb state from the client [HSD-STATE] wr flag):
- climb segment  = first run of wr=true frames; start / end = first / last wr frame time; z from the usercmd post-origin
                   nearest in time; gain = z_end - z_start; duration = t_end - t_start;
- outcome        = mantle (trav=true within 0.5 s after the climb end), else top (trial ends on the ledge) or fall;
- profile        = post vz of the usercmds inside the climb, read at floor-relative heights 100, 200, ... (rising part);
- speed line     = least squares vz = k * (Z0 - z) over the usercmds after the vz peak (z floor-relative);
- wall jump      = m8r2_spw_jump (Sparrow probe and its Gibraltar control): the jump press while climbing (W held, into
                   the face): post velocity on the press usercmd (the face normal is -x, so outward = -vx), rise = apex z after
                   the press - z at the press, and the horizontal velocity 0.5 / 1.0 s later (edge air control toward the face);
- pounce trials  = release = first usercmd with post |v| > 400; contact = first usercmd after it whose post |v_h| falls
                   below 100 from a pre |v_h| > 300 (the face stops the horizontal motion); climb delay = wr start - release.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

FLOOR = 294.92
ROCK_TOP_ABOVE_ORIGIN = 232.0      # h<H>: rock origin z = floor - (232 - H) (tools/hsd_trial.py)
IN_FORWARD = 0x8
LEVELS = (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)


def r(x, n=3):
    return None if x is None else round(x, n)


def wall_H(runner):
    z = runner.get("geometry_wall_z")
    if z is None:
        return None
    top = max(z) if isinstance(z, list) else z
    return round(top - FLOOR + ROCK_TOP_ABOVE_ORIGIN, 1)


def segments(states, flag):
    out, cur = [], None
    for s in states:
        if s.get(flag):
            if cur is None:
                cur = [s["t"], s["t"]]
            else:
                cur[1] = s["t"]
        elif cur is not None:
            out.append(tuple(cur))
            cur = None
    if cur is not None:
        out.append(tuple(cur))
    return out


def cmd_at(cmds, t):
    best = None
    for c in cmds:
        if c.get("t") is None:
            continue
        if best is None or abs(c["t"] - t) < abs(best["t"] - t):
            best = c
    return best


def lin_fit(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    rms = math.sqrt(sum((a + b * x - y) ** 2 for x, y in zip(xs, ys)) / n)
    return a, b, rms


def sched_t(T, key, edge="down", nth=0):
    hits = [l for l in T["sched_lines"] if ("edge=%s" % edge) in l and ("key=%s " % key) in l]
    if len(hits) <= nth:
        return None
    return float(L._field(hits[nth], "t")) if hasattr(L, "_field") else float(
        [tok for tok in hits[nth].split() if tok.startswith("t=")][0][2:])


def trial_row(T, H, legend, session):
    cmds = [c for c in T["cmds"] if c.get("t") is not None]
    row = {"session": session, "run": T["run"], "schedule": T["schedule"], "legend": legend, "H": H, "fps": T["fps"],
           "join": T["join"]}
    segs = segments(T["states"], "wr")
    row["wr_segments"] = len(segs)
    if not segs or not cmds:
        row["outcome"] = "no_climb"
        row["z_max"] = r(max((c["poz"] for c in cmds), default=FLOOR) - FLOOR, 2)
        return row
    t0, t1 = segs[0]
    c0, c1 = cmd_at(cmds, t0), cmd_at(cmds, t1)
    inside = [c for c in cmds if t0 - 1e-6 <= c["t"] <= t1 + 1e-6]
    zmax_climb = max(c["poz"] for c in inside) if inside else c1["poz"]
    row.update(t_start=r(t0, 4), t_end=r(t1, 4), duration=r(t1 - t0, 4), z_start=r(c0["poz"] - FLOOR, 2),
               z_end=r(zmax_climb - FLOOR, 2), gain=r(zmax_climb - c0["poz"], 2), vz_end=r(c1["pvz"], 2))
    trav = [s for s in segments(T["states"], "trav") if s[0] >= t1 - 0.05]
    final_z = cmds[-1]["poz"] - FLOOR
    # W release edges (schedule), final jump-up (post vz rises by > 100 in one usercmd inside the last climb segment, after
    # 0.2 s), and face impacts (post vz falls by > 40 in one usercmd inside the first segment: the stacked-rock junctions)
    w_up = [float(tok[2:]) for l in T["sched_lines"] if "edge=up" in l and "key=forward " in l
            for tok in l.split() if tok.startswith("t=")]
    seg_last = segs[-1]
    ins_last = [c for c in cmds if seg_last[0] - 1e-6 <= c["t"] <= seg_last[1] + 0.02]
    ju = None
    for p, q in zip(ins_last, ins_last[1:]):
        if q["t"] - seg_last[0] > 0.2 and q["pvz"] - p["pvz"] > 100.0:
            ju = (p, q)
            break
    impacts = [(r(q["poz"] - FLOOR, 1), r(p["pvz"] - q["pvz"], 1)) for p, q in zip(inside, inside[1:]) if p["pvz"] - q["pvz"] > 40.0]
    row["impacts"] = impacts
    if ju is not None:
        p, q = ju
        row["jumpup"] = {"seg": len(segs), "t_after_seg_start": r(q["t"] - seg_last[0], 4), "z": r(q["poz"] - FLOOR, 2),
                         "seg_z0": r(ins_last[0]["poz"] - FLOOR, 2), "dvz": r(q["pvz"] - p["pvz"], 2), "vz_before": r(p["pvz"], 2)}
    w_end = any(0.0 <= seg_last[1] - tw <= 0.3 for tw in w_up)
    if trav and trav[0][0] - t1 <= 0.5:
        row["outcome"] = "mantle"
        row["trav_dur"] = r(trav[0][1] - trav[0][0], 3)
    elif H is not None and final_z >= H - 2:
        row["outcome"] = "top"
    elif ju is not None:
        row["outcome"] = "jumpup"
    elif w_end:
        row["outcome"] = "w_release"
    else:
        row["outcome"] = "detach"
    if w_up:
        row["climb_end_after_w_release"] = r(seg_last[1] - w_up[-1], 4)
    row["final_z"] = r(final_z, 2)
    # vz profile and speed line over the climb
    pts = [(c["poz"] - FLOOR, c["pvz"]) for c in inside]
    if pts:
        ipk = max(range(len(pts)), key=lambda i: pts[i][1])
        row["vz_peak"] = r(pts[ipk][1], 2)
        row["z_at_peak"] = r(pts[ipk][0], 2)
        rising = pts[ipk:]
        prof = {}
        for lv in LEVELS:
            for (za, va), (zb, vb) in zip(rising, rising[1:]):
                if za <= lv <= zb and zb > za:
                    prof[str(lv)] = r(va + (vb - va) * (lv - za) / (zb - za), 2)
                    break
        row["vz_at"] = prof
        z_imp = impacts[0][0] if impacts else 1e9
        tail = [p for p in rising if 100.0 <= p[0] <= min(400.0, z_imp - 10.0)]   # clean face: below the first junction
        f = lin_fit([p[0] for p in tail], [p[1] for p in tail])
        if f:
            a, b, rms = f
            row["line_k"] = r(-b, 5)
            row["line_Z0"] = r(-a / b, 2) if b else None
            row["line_rms"] = r(rms, 3)
        # vz as a function of time since the climb start (for the time-limit question)
        row["vz_t"] = {str(tt): r(cmd_at(inside, t0 + tt)["pvz"], 2) for tt in (0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0)
                       if t0 + tt <= t1}
    # server events
    ev = [(e["evt"], e["t"], e["oz"] - FLOOR, e["vz"]) for e in T["sv_evt"] if e["evt"] in ("BEGIN_WALLRUN", "END_WALLRUN")]
    if ev:
        b = next((e for e in ev if e[0] == "BEGIN_WALLRUN"), None)
        e2 = next((e for e in ev if e[0] == "END_WALLRUN"), None)
        if b and e2:
            row["sv_wallrun"] = {"dur": r(e2[1] - b[1], 4), "z_begin": r(b[2], 2), "z_end": r(e2[2], 2), "vz_end": r(e2[3], 2)}
    # wall jump while climbing (Sparrow wall launch probe)
    sch = T["schedule"]
    if sch == "m8r2_spw_jump":
        prev_b, press = None, None
        for c in cmds:
            if prev_b is not None and c["buttons"] & 0x2 and not prev_b & 0x2 and c["t"] > t0:
                press = c
                break
            prev_b = c["buttons"]
        if press:
            k = cmds.index(press)
            after = [c for c in cmds[k:] if c["t"] <= press["t"] + 2.0]
            apex = max(after, key=lambda c: c["poz"])
            w = {"t_in_climb": r(press["t"] - t0, 4), "z_press": r(press["oz"] - FLOOR, 2), "pre_v": [r(press["vx"], 2), r(press["vz"], 2)],
                 "post_v": [r(press["pvx"], 2), r(press["pvy"], 2), r(press["pvz"], 2)],
                 "post_vz_plus_half_g_dt": r(press["pvz"] + 0.5 * 750.0 * (press["dt"] or 1 / 120.0), 2),
                 "outward": r(-press["pvx"], 2), "rise": r(apex["poz"] - press["oz"], 2), "apex_t": r(apex["t"] - press["t"], 4)}
            for dtt in (0.5, 1.0):
                c = cmd_at(after, press["t"] + dtt)
                w["vx_%.1fs" % dtt] = r(c["pvx"], 2)
            row["walljump"] = w
    # pounce / jump-in timing
    if "pounce" in sch or "jumpin" in sch:
        rel = None
        if "pounce" in sch:
            rel = next((c for c in cmds if math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2) > 400.0), None)
        start = rel["t"] if rel else cmds[0]["t"]
        con = next((c for c in cmds if c["t"] > start and L.hs(c, post=False) > 300.0 and L.hs(c) < 100.0), None)
        if con is None and "jumpin" in sch:
            con = next((c for c in cmds if c["t"] > start and L.hs(c, post=False) > 150.0 and L.hs(c) < 60.0
                        and not c["ground"]), None)
        if rel:
            row["release_t"] = r(rel["t"], 4)
            row["release_v"] = [r(rel["pvx"], 2), r(rel["pvy"], 2), r(rel["pvz"], 2)]
            row["climb_after_release"] = r(t0 - rel["t"], 4)
        if con:
            row["contact_t"] = r(con["t"], 4)
            row["contact_z"] = r(con["poz"] - FLOOR, 2)
            if rel:
                row["contact_after_release"] = r(con["t"] - rel["t"], 4)
            row["climb_after_contact"] = r(t0 - con["t"], 4)
    return row


def stats(vals):
    return L.stats(vals)


def fmt(s, nd=3):
    return L.fmt(s, nd)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    rows, metas = [], []
    for folder in a.sessions:
        D = L.load(folder)
        H = wall_H(D["runner"])
        legend = D["runner"].get("legend")
        excl = [(t["run"], t["schedule"], t["why"]) for t in D["runner"]["trials"] if not t["ok"] and not t.get("warmup")]
        metas.append({"session": D["folder"], "H": H, "legend": legend, "scored": len(D["trials"]), "excluded": excl,
                      "fps": [r(min(t["fps"] for t in D["trials"]), 2), r(max(t["fps"] for t in D["trials"]), 2)]})
        for T in D["trials"]:
            rows.append(trial_row(T, H, legend, D["folder"]))

    print("M8 R2 Revenant long climb probe")
    print("=" * 72)
    print("\n1. Sessions")
    for m in metas:
        print("  %-34s H=%-6s legend=%-10s scored=%d fps %s..%s excluded=%s" % (m["session"], m["H"], m["legend"], m["scored"],
              m["fps"][0], m["fps"][1], m["excluded"] or "none"))

    print("\n2. Per trial (z floor-relative; t in s)")
    hdr = "  %-6s %-18s %-10s %6s %-9s %3s %7s %7s %7s %7s %7s %7s %8s %7s %6s  %s"
    print(hdr % ("run", "schedule", "legend", "H", "outcome", "seg", "z0", "z_end", "gain", "dur", "vz_pk", "Z0fit", "k", "final",
                 "W->end", "impacts (z, dvz) / jump-up"))
    for w in rows:
        ju = w.get("jumpup")
        extra = str(w.get("impacts", ""))
        if ju:
            extra += " JU seg%d t+%s z=%s dvz=%s" % (ju["seg"], ju["t_after_seg_start"], ju["z"], ju["dvz"])
        print(hdr % (w["run"], w["schedule"], w["legend"], w["H"], w["outcome"], w.get("wr_segments"), w.get("z_start"), w.get("z_end"),
                     w.get("gain"), w.get("duration"), w.get("vz_peak"), w.get("line_Z0"), w.get("line_k"), w.get("final_z"),
                     w.get("climb_end_after_w_release"), extra))

    groups = {}
    for w in rows:
        groups.setdefault((w["legend"], w["schedule"], w["H"]), []).append(w)
    summary = {}
    print("\n3. Groups")
    for key in sorted(groups, key=lambda k: (k[0] or "", k[1], k[2] or 0)):
        ws = groups[key]
        oc = {}
        for w in ws:
            oc[w["outcome"]] = oc.get(w["outcome"], 0) + 1
        g = {"n": len(ws), "outcomes": oc}
        for f in ("duration", "z_start", "z_end", "gain", "vz_peak", "line_Z0", "line_k", "line_rms", "climb_after_release",
                  "contact_after_release", "climb_after_contact", "contact_z", "climb_end_after_w_release"):
            s = stats([w.get(f) for w in ws])
            if s["n"]:
                g[f] = s
        prof = {}
        for lv in LEVELS:
            s = stats([w.get("vz_at", {}).get(str(lv)) for w in ws])
            if s["n"]:
                prof[str(lv)] = s
        g["vz_at"] = prof
        summary["%s|%s|%s" % key] = g
        print("  %s %s H=%s  n=%d outcomes=%s" % (key[0], key[1], key[2], len(ws), oc))
        for f in ("duration", "z_start", "z_end", "gain", "vz_peak", "line_Z0", "line_k", "line_rms", "climb_after_release",
                  "contact_after_release", "climb_after_contact", "contact_z", "climb_end_after_w_release"):
            if f in g:
                print("      %-26s %s" % (f, fmt(g[f], 4)))
        if prof:
            print("      vz at z (floor-rel): " + "  ".join("%s:%s" % (k, r(v["mean"], 1)) for k, v in prof.items()))

    # Revenant speed line on the clean face (z 100..400 before any junction impact), climbs from the sprint jump; how they end
    rev = [w for w in rows if w["legend"] == "revenant" and w["schedule"] in ("m8r2_climb", "m8r2_climb_long")]
    print("\n4. Revenant climbs from the sprint jump (contact ~50 u above the floor)")
    for f in ("vz_peak", "z_at_peak", "line_Z0", "line_k", "line_rms"):
        print("  %-10s %s" % (f, fmt(stats([w.get(f) for w in rev]), 4)))
    ends = {}
    for w in rev:
        ends[w["outcome"]] = ends.get(w["outcome"], 0) + 1
    print("  climb ends: %s" % ends)
    for w in rev:
        if w["outcome"] in ("jumpup", "detach") or w["schedule"] == "m8r2_climb_long":
            print("    r%s %s H=%s %s z_end=%s dur=%s impacts=%s jumpup=%s" % (w["run"], w["schedule"], w["H"], w["outcome"],
                  w.get("z_end"), w.get("duration"), w.get("impacts"), w.get("jumpup")))
    wr_end = [w.get("climb_end_after_w_release") for w in rows if w["outcome"] == "w_release"]
    print("  W release -> climb end (outcome w_release, all schedules): %s" % fmt(stats(wr_end), 4))
    vzt = {}
    for w in rev:
        if not w.get("impacts"):
            for k, v in w.get("vz_t", {}).items():
                vzt.setdefault(k, []).append(v)
    print("  vz at t after the climb start (climbs without impacts): " + "  ".join(
        "%s s:%s (n=%d)" % (k, r(stats(v)["mean"], 1), len(v)) for k, v in sorted(vzt.items(), key=lambda kv: float(kv[0]))))
    rev_free = rev

    wj = [w for w in rows if "walljump" in w]
    if wj:
        print("\n5. Jump press while climbing (m8r2_spw_jump, h480 rock; Sparrow wall launch probe)")
        for w in wj:
            j = w["walljump"]
            print("  r%s %-9s press t+%ss z=%s post v=%s (vz+g dt/2 %s) outward %s rise %s (apex +%ss) vx@0.5s %s vx@1.0s %s" % (
                w["run"], w["legend"], j["t_in_climb"], j["z_press"], j["post_v"], j["post_vz_plus_half_g_dt"], j["outward"], j["rise"],
                j["apex_t"], j["vx_0.5s"], j["vx_1.0s"]))
        for leg in sorted(set(w["legend"] for w in wj)):
            ws = [w["walljump"] for w in wj if w["legend"] == leg]
            print("  %s: rise %s; post vz+g dt/2 %s; outward %s; vx@1.0s %s" % (leg, fmt(stats([j["rise"] for j in ws]), 2),
                  fmt(stats([j["post_vz_plus_half_g_dt"] for j in ws]), 2), fmt(stats([j["outward"] for j in ws]), 2),
                  fmt(stats([j["vx_1.0s"] for j in ws]), 2)))

    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sessions": metas, "trials": rows, "groups": summary}, fh, indent=1)
    if a.params:
        P = build_params(summary, rev_free) + walljump_params(rows)
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(P, fh, indent=1)
    return 0


def _p(name, s, unit, cls, note=""):
    if not s or not s.get("n"):
        return None
    return {"name": name, "value": r(s["mean"], 4), "sd": r(s["sd"], 4), "n": s["n"], "unit": unit, "class": cls, "note": note}


def build_params(summary, rev_free):
    P = []
    free = {f: stats([w.get(f) for w in rev_free]) for f in ("line_Z0", "line_k", "vz_peak")}
    P.append(_p("rev_climb_vz_peak", free["vz_peak"], "u/s", "meas", "sprint-jump contact ~50 u above the floor"))
    P.append(_p("rev_speed_line_Z0", free["line_Z0"], "u above floor", "fit",
                "vz = k (Z0 - z) on the clean face z 100..400 (before any stacked-rock junction); Gibraltar control 180.4"))
    P.append(_p("rev_speed_line_k", free["line_k"], "1/s", "fit", "Gibraltar control 1.7454 (same wall, same approach)"))
    ju = [w["jumpup"] for w in rev_free if w.get("jumpup")]
    if ju:
        P.append({"name": "rev_climb_final_jumpup", "value": [{k: j[k] for k in ("z", "t_after_seg_start", "seg_z0", "dvz", "vz_before")}
                  for j in ju], "n": len(ju), "unit": "u above floor / s / u / u/s", "class": "meas",
                  "note": "climb ended by a final jump-up (only seen with W held 12 s); end rule not identified [unknown]"})
    creep = [w for w in rev_free if w["schedule"] == "m8r2_climb_long" and w["outcome"] == "w_release"]
    if creep:
        P.append({"name": "rev_climb_no_end_after_impact", "value": [{"z_end": w["z_end"], "dur": w["duration"], "impacts": w["impacts"]}
                  for w in creep], "n": len(creep), "unit": "u / s", "class": "meas",
                  "note": "after a junction impact the climb crept at ~10.8 u/s until the W release (no end) [unknown]"})
    for key, g in sorted(summary.items()):
        leg, sch, H = key.split("|")
        P.append({"name": "outcome_%s_%s_H%s" % (leg, sch, H), "value": g["outcomes"], "n": g["n"], "unit": "count",
                  "class": "meas", "note": "mantle = ledge reached and mantled"})
        if "pounce" in sch or "jumpin" in sch:
            for f in ("climb_after_release", "contact_after_release", "climb_after_contact"):
                if f in g:
                    P.append(_p("%s_%s_%s" % (leg, sch, f), g[f], "s", "meas"))
        if "duration" in g:
            P.append(_p("%s_%s_H%s_duration" % (leg, sch, H), g["duration"], "s", "meas", "wr flag span"))
    return [p for p in P if p]


def walljump_params(rows):
    P = []
    for leg in sorted(set(w["legend"] for w in rows if "walljump" in w)):
        ws = [w["walljump"] for w in rows if "walljump" in w and w["legend"] == leg]
        P.append(_p("walljump_%s_rise" % leg, stats([j["rise"] for j in ws]), "u", "meas",
                    "jump press 0.42 s into the climb, W held; apex - z at the press. SDK wall_launch_math.h max height 300"))
        P.append(_p("walljump_%s_post_vz" % leg, stats([j["post_vz_plus_half_g_dt"] for j in ws]), "u/s", "meas", "post vz + g dt / 2"))
        P.append(_p("walljump_%s_outward" % leg, stats([j["outward"] for j in ws]), "u/s", "meas", "SDK outward 150..450"))
        P.append(_p("walljump_%s_vx_1s" % leg, stats([j["vx_1.0s"] for j in ws]), "u/s", "meas",
                    "horizontal velocity 1 s after the press (+ = back toward the face, W held)"))
    return [p for p in P if p]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
