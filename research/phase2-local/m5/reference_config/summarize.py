"""Summarise the M5 short-range windows (stdlib only).

    python summarize.py            -> RESULTS.md next to this file

Reads windows_baseline.csv (default replay motor) and windows_reference.csv (reference calibration config), both written by
HSD.R5Replay.Editor.ShortRangeBatch (run_eval.py). Per trial family and config: number of windows, median / p90 / max of the
window position RMS (3D, u) and velocity RMS (3D, u/s), and the pass fraction (a window passes when pos RMS <= 4 u AND
vel RMS <= 10 u/s). Every window is counted; nothing is dropped. Percentiles: nearest-rank on the sorted values.
"""
import csv
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
POS_LIMIT, VEL_LIMIT = 4.0, 10.0

FAMILIES = [
    ("M1 ground (walk/sprint, M1)", r"^M1_"),
    ("M2 e1 ground (walk, sprint, crouch, back, side, diag, turn)", r"^M2_e1_"),
    ("M2 e2 release / air strafe", r"^M2_e2_"),
    ("M2 e4 jumps (stand, hops)", r"^M2_e4_"),
    ("M2 e5 slide / slide jump", r"^M2_e5_"),
    ("M3 e3 lurch (tap strafe)", r"^M3_e3_"),
    ("M3 e8 hops / slide chain", r"^M3_e8_"),
    ("M4 controls (no ability)", r"^M4_(e2_|e4_|m4_ctrl_|m4_valk_ctrl)"),
    ("M4 stim", r"^M4_m4_stim_"),
    ("M4 jump pad", r"^M4_m4_pad_"),
    ("M4 gravity lift", r"^M4_m4_lift_"),
    ("M4 jets", r"^M4_m4_valk_jets"),
    ("M4 pounce", r"^M4_m4_pounce_"),
]


def family(tid):
    for name, rx in FAMILIES:
        if re.search(rx, tid):
            return name
    return "other"


def load(cfg):
    p = os.path.join(HERE, f"windows_{cfg}.csv")
    if not os.path.exists(p):
        return None
    with open(p, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in ("pos_rms_3d_u", "vel_rms_3d_ups", "pos_max_3d_u", "vel_max_3d_ups", "duration_s", "t0_s"):
            r[k] = float(r[k])
        r["pass"] = r["pass"] == "1"
        r["family"] = family(r["trial_id"])
    return rows


def pct(vals, q):
    v = sorted(vals)
    if not v:
        return float("nan")
    k = max(0, min(len(v) - 1, math.ceil(q * len(v)) - 1))
    return v[k]


def stats(rows):
    pos = [r["pos_rms_3d_u"] for r in rows]
    vel = [r["vel_rms_3d_ups"] for r in rows]
    n = len(rows)
    return {
        "n": n,
        "pos_med": pct(pos, 0.5), "pos_p90": pct(pos, 0.9), "pos_max": max(pos),
        "vel_med": pct(vel, 0.5), "vel_p90": pct(vel, 0.9), "vel_max": max(vel),
        "pos_pass": sum(p <= POS_LIMIT for p in pos) / n, "vel_pass": sum(v <= VEL_LIMIT for v in vel) / n,
        "pass": sum(r["pass"] for r in rows) / n, "n_pass": sum(r["pass"] for r in rows),
    }


def f(x, d=2):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def table(rows, title):
    out = [f"### {title}", "",
           "| family | windows | pos RMS median / p90 / max (u) | vel RMS median / p90 / max (u/s) | pos ≤ 4 | vel ≤ 10 | **both (pass)** | verdict (p90 ≤ limits) |",
           "|---|---|---|---|---|---|---|---|"]
    fams = [n for n, _ in FAMILIES if any(r["family"] == n for r in rows)]
    for name in fams + ["ALL"]:
        sub = rows if name == "ALL" else [r for r in rows if r["family"] == name]
        s = stats(sub)
        ok = s["pos_p90"] <= POS_LIMIT and s["vel_p90"] <= VEL_LIMIT
        label = "**all families**" if name == "ALL" else name
        out.append(f"| {label} | {s['n']} | {f(s['pos_med'])} / {f(s['pos_p90'])} / {f(s['pos_max'])} | "
                   f"{f(s['vel_med'])} / {f(s['vel_p90'])} / {f(s['vel_max'])} | {s['pos_pass']*100:.1f} % | {s['vel_pass']*100:.1f} % | "
                   f"**{s['n_pass']}/{s['n']} = {s['pass']*100:.1f} %** | {'PASS' if ok else 'FAIL'} |")
    out.append("")
    return out


def before_after(rows_b, rows_r):
    out = ["### Before (baseline) → after (reference config), per family", "",
           "| family | windows | pass | pos RMS p90 (u) | vel RMS p90 (u/s) | worst pos / vel RMS | reference verdict |",
           "|---|---|---|---|---|---|---|"]
    fams = [n for n, _ in FAMILIES if any(r["family"] == n for r in rows_b)]
    for name in fams + ["ALL"]:
        b = rows_b if name == "ALL" else [r for r in rows_b if r["family"] == name]
        r = rows_r if name == "ALL" else [x for x in rows_r if x["family"] == name]
        sb, sr = stats(b), stats(r)
        ok = sr["pos_p90"] <= POS_LIMIT and sr["vel_p90"] <= VEL_LIMIT
        label = "**all families**" if name == "ALL" else name
        out.append(f"| {label} | {sb['n']} | {sb['pass']*100:.1f} % → **{sr['pass']*100:.1f} %** | {f(sb['pos_p90'])} → {f(sr['pos_p90'])} | "
                   f"{f(sb['vel_p90'])} → {f(sr['vel_p90'])} | {f(sb['pos_max'])} / {f(sb['vel_max'])} → {f(sr['pos_max'])} / {f(sr['vel_max'])} | "
                   f"{'PASS' if ok else 'FAIL'} |")
    out.append("")
    return out


def per_trial(rows_b, rows_r):
    out = ["### Per trial (windows passing, worst window pos / vel RMS): baseline → reference", "",
           "| trial | family | windows | pass baseline → reference | worst pos RMS (u) | worst vel RMS (u/s) |", "|---|---|---|---|---|---|"]
    ids = sorted({r["trial_id"] for r in rows_b}, key=lambda t: ([n for n, _ in FAMILIES].index(family(t)) if family(t) != "other" else 99, t))
    for t in ids:
        b = [r for r in rows_b if r["trial_id"] == t]
        rr = [r for r in rows_r if r["trial_id"] == t] if rows_r else []
        pb = sum(r["pass"] for r in b)
        pr = sum(r["pass"] for r in rr) if rr else None
        wp = f"{f(max(r['pos_rms_3d_u'] for r in b))} → {f(max(r['pos_rms_3d_u'] for r in rr)) if rr else '–'}"
        wv = f"{f(max(r['vel_rms_3d_ups'] for r in b))} → {f(max(r['vel_rms_3d_ups'] for r in rr)) if rr else '–'}"
        out.append(f"| {t} | {family(t)} | {len(b)} | {pb} → {pr if pr is not None else '–'} | {wp} | {wv} |")
    out.append("")
    return out


def failing(rows, cfg):
    bad = [r for r in rows if not r["pass"]]
    out = [f"### Failing windows ({cfg}): {len(bad)}", "",
           "| trial | window | t0 (s) | kind | start grounded | start |v_h| | pos RMS | pos max | vel RMS | vel max |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(bad, key=lambda r: (r["family"], r["trial_id"], int(r["window"]))):
        out.append(f"| {r['trial_id']} | {r['window']} | {f(r['t0_s'])} | {r['kind']} | {r['start_grounded']} | {f(float(r['start_speed_ups']), 1)} | "
                   f"{f(r['pos_rms_3d_u'])} | {f(r['pos_max_3d_u'])} | {f(r['vel_rms_3d_ups'])} | {f(r['vel_max_3d_ups'])} |")
    out.append("")
    return out


def main():
    b, r = load("baseline"), load("reference")
    lines = ["# M5 short-range accuracy: generated tables", "",
             "Generated by `summarize.py` from `windows_baseline.csv` / `windows_reference.csv` (see README.md for the definition). "
             "Pass = window pos RMS ≤ 4 u **and** vel RMS ≤ 10 u/s. Family verdict: p90 of both within the limits.", ""]
    if b and r:
        lines += before_after(b, r)
    if b:
        lines += table(b, "Baseline: default replay motor (R5MotorV2/m3, M4 kits)")
    if r:
        lines += table(r, "Reference calibration config")
    if b:
        lines += per_trial(b, r)
    if r:
        lines += failing(r, "reference")
    if b:
        lines += failing(b, "baseline")
    with open(os.path.join(HERE, "RESULTS.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    for cfg, rows in (("baseline", b), ("reference", r)):
        if rows:
            s = stats(rows)
            print(f"{cfg}: {s['n_pass']}/{s['n']} windows pass ({s['pass']*100:.1f} %); pos p90 {s['pos_p90']:.2f} u, vel p90 {s['vel_p90']:.2f} u/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
