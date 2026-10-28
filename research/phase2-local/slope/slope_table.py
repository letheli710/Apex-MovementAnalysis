#!/usr/bin/env python3
"""R6: compact R5 | Unity tables from slope_analysis.py --json output (means over the trials of each condition).

  py -3 slope_table.py results.json > tables.md
"""
import json
import sys


def m(s, k, nd=1):
    v = s.get(k) if s else None
    if v is None:
        return "–"
    if isinstance(v, dict):
        return ("%." + str(nd) + "f") % v["mean"] + ("" if v["sd"] < 0.05 else " ±%.1f" % v["sd"])
    return str(v)


def main():
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    R, U = d["cond_r5"], d.get("cond_unity", {})
    print("## Uphill (R5 | Unity)\n")
    print("| condition | n | ramp entry speed | slide on ramp until end (s) | distance up the slope at end | crouch-walk after | most downhill vx after end | landing x from foot |")
    print("|---|---|---|---|---|---|---|---|")
    for k in sorted(R):
        if not k.startswith("r6_up") or "duckup" in k:
            continue
        r, u = R[k], U.get(k, {})
        print("| %s | %d | %s \\| %s | %s \\| %s | %s \\| %s | %s \\| %s | %s \\| %s | %s \\| %s |" % (
            k[3:], r["n"], m(r, "entry_h"), m(u, "entry_h"), m(r, "end_t_after_entry", 3), m(u, "end_t_after_entry", 3),
            m(r, "end_up_slope"), m(u, "end_up_slope"), m(r, "crouch_walk_h"), m(u, "crouch_walk_h"),
            m(r, "min_vx_after_end", 2), m(u, "min_vx_after_end", 2), m(r, "landing_x_from_foot"), m(u, "landing_x_from_foot")))
    print("\n## Joints (R5 | Unity): speed before, change across, airborne commands within ±0.3 s\n")
    print("| condition | joint | n | speed before | Δspeed (one command) | Δspeed −0.1 s → +0.1 s | sliding | airborne | max height above surface |")
    print("|---|---|---|---|---|---|---|---|---|")
    for k in sorted(R):
        for j, t in enumerate(R[k].get("transitions", [])):
            tu = (U.get(k, {}).get("transitions") or [None] * (j + 1))[j] if U.get(k, {}).get("transitions") and len(U[k]["transitions"]) > j else None
            print("| %s | %+d° → %+d° | %d | %s \\| %s | %s \\| %s | %s \\| %s | %d \\| %s | %s \\| %s | %.1f \\| %s |" % (
                k[3:], t["from_deg"], t["to_deg"], t["n"], m(t, "h_before"), m(tu, "h_before"), m(t, "dh", 2), m(tu, "dh", 2), m(t, "dh_m01_p01", 1), m(tu, "dh_m01_p01", 1),
                t["sliding"], tu["sliding"] if tu else "–", sum(t["airborne_cmds_pm03"]), sum(tu["airborne_cmds_pm03"]) if tu else "–",
                t["max_rise_above_surface_pm03"], "%.1f" % tu["max_rise_above_surface_pm03"] if tu else "–"))
    print("\n## Other conditions (R5 | Unity)\n")
    print("| condition | n | max speed | slide time | end speed | min speed | end heading | downhill drift | re-boosts (R5) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for k in sorted(R):
        r, u = R[k], U.get(k, {})
        rb = r.get("reboosts", [])
        print("| %s | %d | %s \\| %s | %s \\| %s | %s \\| %s | %s \\| %s | %s \\| %s | %s \\| %s | %s |" % (
            k[3:], r["n"], m(r, "max_h"), m(u, "max_h"), m(r, "slide_t", 2), m(u, "slide_t", 2), m(r, "end_h"), m(u, "end_h"),
            m(r, "min_h"), m(u, "min_h"), m(r, "end_heading"), m(u, "end_heading"), m(r, "dx_downhill"), m(u, "dx_downhill"),
            "; ".join("%.0f→%.0f @%.2fs" % (b["h0"], b["h1"], b["since_slide_start"]) for b in rb if b["since_slide_start"] and b["since_slide_start"] > 0.05)[:160] or "–"))
    print("\n## Native law per command (R5 | Unity)\n")
    print("| kind | slope | duck | n R5 | residual rms R5 | residual rms Unity | extra accel R5 | extra accel Unity | native g·n_z·(n_h·v̂) | M8 fit 147+342·sin |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    lu = {(q["kind"], q["slope_deg"], q["duck"]): q for q in d.get("law_unity", [])}
    for q in d["law_r5"]:
        u = lu.get((q["kind"], q["slope_deg"], q["duck"]))
        print("| %s | %.0f° | %d | %d | %.3f | %s | %.1f ±%.1f | %s | %.1f | %s |" % (
            q["kind"], q["slope_deg"], q["duck"], q["n"], q["res_rms"], "%.3f" % u["res_rms"] if u else "–",
            q["extra"]["mean"], q["extra"]["sd"], "%.1f" % u["extra"]["mean"] if u else "–", q["native_extra"],
            q["m8_fit_extra"] if q["m8_fit_extra"] is not None else "–"))


if __name__ == "__main__":
    main()
