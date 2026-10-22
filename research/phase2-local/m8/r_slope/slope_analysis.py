#!/usr/bin/env python3
"""M8 track R4 (time-boxed): slide and sprint down the spawn-side hillside of mp_rr_canyonlands_staging_mu1 (R5Flowstate
S21, local offline).

  py -3 slope_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

Uses the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py). stdlib only, no local paths. Schedules m8_slope_*: start on
the flat top (x -10900, y 550, z 1580.03) facing +X; the slope starts at x -10575 (probe: planar 29.4 deg ramp to x -10375,
then a 30-41 deg hillside). Per grounded usercmd the local slope is taken from the usercmd's own displacement
(atan(-dz / dxy) of the post-pre origin step) and the speed change is compared with the M2 flat slide law
s' = (s - 100*dt) * 0.7^dt (m2/slide/SLIDE-MODEL.md) applied to the 3D speed and to the horizontal speed.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

IN_DUCK = 0x4
X_SLOPE = -10575.0


def r(x, n=3):
    return None if x is None else round(x, n)


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def trial_row(T):
    cs = T["cmds"]
    R = {"run": T["run"], "schedule": T["schedule"], "fps": T["fps"], "join": [T["join"]["joined"], T["join"]["cmds"]]}
    tt, acc = [], 0.0
    for c in cs:
        tt.append(acc)
        acc += dt_of(c)
    rows = []
    for i, c in enumerate(cs):
        dx, dy, dz = c["pox"] - c["ox"], c["poy"] - c["oy"], c["poz"] - c["oz"]
        dxy = math.hypot(dx, dy)
        sh0, sh1 = math.hypot(c["vx"], c["vy"]), math.hypot(c["pvx"], c["pvy"])
        s30, s31 = math.sqrt(sh0 ** 2 + c["vz"] ** 2), math.sqrt(sh1 ** 2 + c["pvz"] ** 2)
        rows.append({"i": i, "t": tt[i], "x": c["ox"], "z": c["oz"], "ground": c["ground"], "slide": c["slide"], "duck": c["duck"],
                     "fwd": c["fwd"], "sh0": sh0, "sh1": sh1, "s30": s30, "s31": s31, "vz1": c["pvz"],
                     "slope_deg": math.degrees(math.atan2(-dz, dxy)) if dxy > 0.5 else None, "dt": dt_of(c), "msc": c["msc"],
                     "duck_btn": bool(c["buttons"] & IN_DUCK)})
    i_duck = next((q for q in range(1, len(cs)) if cs[q]["buttons"] & IN_DUCK and not cs[q - 1]["buttons"] & IN_DUCK), None)
    i_slide = next((q for q in range(len(cs)) if cs[q]["slide"]), None)
    i_slope = next((q for q in range(len(cs)) if cs[q]["ox"] > X_SLOPE), None)
    i_air = [q for q in range(1, len(cs)) if cs[q]["ground"] == 0 and cs[q - 1]["ground"] == 1]
    R["duck_idx"], R["slide_idx"], R["slope_idx"] = i_duck, i_slide, i_slope
    R["slide_start"] = {"t": r(tt[i_slide], 3), "x": r(cs[i_slide]["ox"], 1), "pre_h": r(rows[i_slide]["sh0"]), "post_h": r(rows[i_slide]["sh1"])} if i_slide is not None else None
    R["slope_entry"] = {"t": r(tt[i_slope], 3), "h": r(rows[i_slope]["sh0"]), "slide": cs[i_slope]["slide"]} if i_slope is not None else None
    R["airborne_cmds_after_slope"] = sum(1 for q in range(i_slope or len(cs), len(cs)) if cs[q]["ground"] == 0) if i_slope is not None else None
    R["first_airborne_after_slope"] = next((r(tt[q], 3) for q in i_air if i_slope is not None and q >= i_slope), None)
    # time series every 0.1 s from the slope entry
    ser = []
    if i_slope is not None:
        for k in range(0, 40):
            tq = tt[i_slope] + 0.1 * k
            q = next((j for j in range(i_slope, len(cs)) if tt[j] >= tq), None)
            if q is None:
                break
            w = rows[q]
            ser.append([r(tt[q] - tt[i_slope], 3), r(w["x"], 1), r(w["z"], 1), w["ground"], w["slide"], r(w["sh1"], 2), r(w["s31"], 2),
                        r(w["vz1"], 2), r(w["slope_deg"], 1)])
    R["series"] = ser
    # per-usercmd residuals against the flat slide law, grouped by surface (flat / slope), sliding and grounded only
    res = {"flat": [], "slope": []}
    acc_rows = {"flat": [], "slope": []}
    for w in rows:
        if not (w["ground"] and w["slide"]) or w["slope_deg"] is None:
            continue
        key = "slope" if w["slope_deg"] > 10 else ("flat" if abs(w["slope_deg"]) < 1 else None)
        if key is None:
            continue
        pred3 = (w["s30"] - 100 * w["dt"]) * 0.7 ** w["dt"]
        predh = (w["sh0"] - 100 * w["dt"]) * 0.7 ** w["dt"]
        res[key].append((w["s31"] - pred3, w["sh1"] - predh))
        acc_rows[key].append(((w["s31"] - w["s30"]) / w["dt"], w["slope_deg"], w["s30"], (w["s31"] - pred3) / w["dt"], w["duck_btn"]))
    R["flat_law_res"] = {k: {"n": len(v), "res3_mean": r(sum(a for a, _ in v) / len(v), 4) if v else None,
                             "resh_mean": r(sum(b for _, b in v) / len(v), 4) if v else None} for k, v in res.items()}
    R["accel_3d"] = {k: [[r(a, 1), r(s, 1), r(sp, 1), r(ex, 1), d] for a, s, sp, ex, d in v] for k, v in acc_rows.items()}
    R["max_speed"] = r(max(w["s31"] for w in rows), 2)
    R["max_h"] = r(max(w["sh1"] for w in rows), 2)
    R["slide_end_t"] = next((r(tt[q], 3) for q in range((i_slide or 0) + 1, len(cs)) if i_slide is not None and not cs[q]["slide"] and cs[q]["ground"]), None)
    return R


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
    rms = math.sqrt(sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / n)
    return a, b, rms


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    rows, metas = [], []
    for f in a.sessions:
        s = L.load(f)
        rej = [(t["run"], t["schedule"], t["why"]) for t in s["runner"]["trials"] if not t.get("ok") and not t.get("warmup")]
        metas.append({"folder": s["folder"], "scored": len(s["trials"]), "rejected": rej})
        for T in s["trials"]:
            if T["schedule"].startswith("m8_slope"):
                rows.append(trial_row(T))
    P = print
    P("M8 R4: slope slide (spawn-side hillside)")
    P("=" * 100)
    for m in metas:
        P(f"{m['folder']}: scored {m['scored']} rejected {m['rejected']}")
    P()
    P("1. PER TRIAL: slide start, slope entry, then every 0.1 s: [t, x, z, ground, slide, |v_h|, |v|, vz, local slope deg]")
    P("-" * 100)
    for R in rows:
        P(f"r{R['run']} {R['schedule']:<20} slide_start {R['slide_start']} slope_entry {R['slope_entry']} slide_end_t {R['slide_end_t']}"
          f" max |v| {R['max_speed']} max |v_h| {R['max_h']} airborne cmds after slope {R['airborne_cmds_after_slope']}"
          f" flat-law residual {R['flat_law_res']}")
        for row in R["series"]:
            P(f"    {row}")
    P()
    P("2. SLIDING ON THE SLOPE: d|v|/dt per grounded sliding usercmd vs local slope (all trials pooled)")
    P("-" * 100)
    pts = [(s, acc, sp) for R in rows for acc, s, sp, ex, d in R["accel_3d"]["slope"]]
    fl = [(s, acc, sp) for R in rows for acc, s, sp, ex, d in R["accel_3d"]["flat"]]
    exd = [(s, ex) for R in rows for acc, s, sp, ex, d in R["accel_3d"]["slope"] if d]
    exu = [(s, ex) for R in rows for acc, s, sp, ex, d in R["accel_3d"]["slope"] if not d]
    P(f"  flat sliding usercmds n {len(fl)}; slope sliding usercmds n {len(pts)}")
    if pts:
        fit = lin_fit([math.sin(math.radians(s)) for s, _, _ in pts], [acc for _, acc, _ in pts])
        if fit:
            P(f"  d|v|/dt = {fit[0]:.1f} + {fit[1]:.1f} * sin(slope)   rms {fit[2]:.1f} u/s^2   (gravity 750 would give +750*sin)")
        for lo, hi in ((10, 25), (25, 32), (32, 38), (38, 45)):
            sel = [acc for s, acc, _ in pts if lo <= s < hi]
            if sel:
                P(f"    slope {lo}-{hi} deg: n {len(sel)} mean d|v|/dt {sum(sel) / len(sel):.1f}")
    P("  extra acceleration beyond the M2 flat slide law, (|v|' - flat-law prediction)/dt, vs sin(slope):")
    for name, pp in (("duck held", exd), ("duck released (slide flag still on)", exu)):
        fit = lin_fit([math.sin(math.radians(s)) for s, _ in pp], [e for _, e in pp]) if len(pp) > 3 else None
        if fit:
            P(f"    {name}: n {len(pp)} extra = {fit[0]:.1f} + {fit[1]:.1f} * sin(slope)  rms {fit[2]:.1f}"
              f"   mean extra {sum(e for _, e in pp) / len(pp):.1f} u/s^2")
        elif pp:
            P(f"    {name}: n {len(pp)} mean extra {sum(e for _, e in pp) / len(pp):.1f} u/s^2")
    out = {"metas": metas, "rows": rows}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    if a.params:
        params = []
        if exd:
            fit = lin_fit([math.sin(math.radians(s)) for s, _ in exd], [e for _, e in exd])
            if fit:
                params.append({"name": "slope_slide_extra_accel_duck_held", "value": {"a": r(fit[0], 1), "b_sin": r(fit[1], 1), "rms": r(fit[2], 1)},
                               "n": len(exd), "unit": "u/s^2", "class": "fit",
                               "note": "acceleration beyond the M2 flat slide law on the slope, duck held; one hillside, one run-in speed"})
        if exu:
            params.append({"name": "slope_slide_extra_accel_duck_released", "value": r(sum(e for _, e in exu) / len(exu), 1), "n": len(exu),
                           "unit": "u/s^2", "class": "meas", "note": "slide flag still on after the duck release, on the 29.9 deg part"})
        if pts:
            fit = lin_fit([math.sin(math.radians(s)) for s, _, _ in pts], [acc for _, acc, _ in pts])
            if fit:
                params.append({"name": "slope_slide_accel_fit", "value": {"a": r(fit[0], 1), "b_sin": r(fit[1], 1), "rms": r(fit[2], 1)},
                               "n": len(pts), "unit": "u/s^2", "class": "fit", "note": "d|v|/dt = a + b*sin(slope) on grounded sliding usercmds"})
        for sch in sorted(set(R["schedule"] for R in rows)):
            rs = [R for R in rows if R["schedule"] == sch]
            params.append({"name": f"{sch}_max_speed", "value": r(sum(R["max_speed"] for R in rs) / len(rs), 2), "n": len(rs), "unit": "u/s",
                           "class": "meas", "note": "max 3D speed in the trial"})
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(params, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
