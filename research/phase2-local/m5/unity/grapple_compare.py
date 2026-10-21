"""Grapple replay before (M4 model F1) vs after (M5 model RF) on the four M4 grapple trials (stdlib only).

    python grapple_compare.py [--write grapple_compare.md]

Inputs (relative to this folder):
  ../../m4/unity/<trial>/steps.csv                  before: M4 build, F1 pull, recorded release step (scenarios.json)
  ../../m4/unity/before_plain_v2/<trial>/steps.csv  plain motor (no grapple), as in the M4 index
  m4_replay/<trial>/steps.csv                       after: M5 build, RF pull, recorded release step
  grapple_envelope/<trial>/steps.csv                after: M5 build, RF pull, release by the 34.1 u detach envelope
  ../../m4/unity/scenarios.json                     recorded release steps
Window and events as ../../m4/unity/make_index.py ev_grapple: reference attach = TAKEOFF, pull start = first step after it with
|Δvx| > 0.5, pull window = [pull start, recorded release). Errors are sim − ref per step (u, u/s).
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M4U = os.path.join(HERE, "..", "..", "m4", "unity")
TRIALS = ["M4_m4_grapple_hold_r1701", "M4_m4_grapple_hold_r1702", "M4_m4_grapple_near_r2101", "M4_m4_grapple_near_r2102"]
WALL_X = -13706.0


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        d = {"ref_ev": r["ref_events"].split("|") if r["ref_events"] else [],
             "sim_ev": r["sim_events"].split("|") if r["sim_events"] else []}
        for s in ("ref", "sim"):
            d[s + "_p"] = tuple(num(r[f"{s}_pos_{a}"]) for a in "xyz")
            d[s + "_v"] = tuple(num(r[f"{s}_vel_{a}"]) for a in "xyz")
        out.append(d)
    return out


def dist(a, b, h=False):
    k = 2 if h else 3
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(k)))


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def first(rows, pred, start=0):
    return next((i for i in range(max(start, 1), len(rows)) if pred(i)), None)


def window(rows, a, b):
    return (rms([dist(rows[i]["sim_p"], rows[i]["ref_p"]) for i in range(a, b)]),
            rms([dist(rows[i]["sim_p"], rows[i]["ref_p"], True) for i in range(a, b)]),
            max(dist(rows[i]["sim_p"], rows[i]["ref_p"]) for i in range(a, b)),
            rms([dist(rows[i]["sim_v"], rows[i]["ref_v"]) for i in range(a, b)]))


def heading_err(rows, i):
    """Angle (deg) between the sim and ref velocity on step i (3D)."""
    a, b = rows[i]["sim_v"], rows[i]["ref_v"]
    la, lb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    c = sum(a[k] * b[k] for k in range(3)) / (la * lb)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def f(v, fmt="{:.2f}"):
    return "–" if v is None or (isinstance(v, float) and math.isnan(v)) else fmt.format(v)


def main():
    with open(os.path.join(M4U, "scenarios.json"), encoding="utf-8") as fh:
        sc = json.load(fh)
    lines = []
    w = lines.append
    w("| trial | pull window (steps) | pull-window pos RMS 3D: plain / F1 (M4) / RF (M5) | RMS horizontal F1 → RF | max 3D F1 → RF | vel RMS F1 → RF | "
      "at release: pos err F1 → RF | speed err F1 → RF | vel err F1 → RF | velocity direction err F1 → RF (deg) |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    env = []
    for t in TRIALS:
        rel = sc["trials"][t]["grapple_release_step"]
        after = load(os.path.join(HERE, "m4_replay", t, "steps.csv"))
        before = load(os.path.join(M4U, t, "steps.csv"))
        plain = load(os.path.join(M4U, "before_plain_v2", t, "steps.csv"))
        ar = next(i for i, r in enumerate(after) if "TAKEOFF" in r["ref_ev"])
        pr = first(after, lambda i: abs(after[i]["ref_v"][0] - after[i - 1]["ref_v"][0]) > 0.5, ar + 1)
        wa, wb, wp = window(after, pr, rel), window(before, pr, rel), window(plain, pr, rel)
        r = rel - 1

        def at(rows):
            sv, rv = rows[r]["sim_v"], rows[r]["ref_v"]
            return (dist(rows[r]["sim_p"], rows[r]["ref_p"]),
                    math.sqrt(sum(x * x for x in sv)) - math.sqrt(sum(x * x for x in rv)),
                    dist(sv, rv), heading_err(rows, r))
        ra, rb = at(after), at(before)
        w(f"| {t} | {pr}..{rel - 1} ({rel - pr}) | {f(wp[0])} / {f(wb[0])} / **{f(wa[0])}** | {f(wb[1])} → {f(wa[1])} | {f(wb[2])} → {f(wa[2])} | "
          f"{f(wb[3])} → {f(wa[3])} | {f(rb[0])} → {f(ra[0])} | {f(rb[1], '{:+.2f}')} → {f(ra[1], '{:+.2f}')} | {f(rb[2])} → {f(ra[2])} | {f(rb[3])} → {f(ra[3])} |")
        # sim attach / pull start
        sa = next((i for i, x in enumerate(after) if any(e.startswith("GRAPPLE_ATTACH") for e in x["sim_ev"])), None)
        sp = next((i for i, x in enumerate(after) if any(e.startswith("GRAPPLE_PULL") for e in x["sim_ev"])), None)
        envr = load(os.path.join(HERE, "grapple_envelope", t, "steps.csv"))
        se = next((i for i, x in enumerate(envr) if any(e.startswith("GRAPPLE_RELEASE") for e in x["sim_ev"])), None)
        sev = next((e for e in envr[se]["sim_ev"] if e.startswith("GRAPPLE_RELEASE")), "") if se is not None else ""
        we = window(envr, pr, min(rel, se if se is not None else rel))
        env.append((t, ar, sa, pr, sp, rel, se, sev, envr, we))
    w("")
    w("Event steps (reference / sim) and the detach envelope run (`grapple_envelope/`, release by the model):")
    w("")
    w("| trial | attach ref/sim | pull start ref/sim | release: recorded / envelope (Δ steps) | envelope event | ref gap to the face at the start of the recorded release command (u) | "
      "pos RMS 3D up to the earlier release, envelope run |")
    w("|---|---|---|---|---|---|---|")
    for (t, ar, sa, pr, sp, rel, se, sev, envr, we) in env:
        prev = envr[rel - 1]["ref_p"][0] if rel >= 1 else float("nan")
        gap_pre = WALL_X - prev
        w(f"| {t} | {ar}/{sa} | {pr}/{sp} | {rel} / {se} ({'+' if se - rel >= 0 else ''}{se - rel}) | {sev} | {f(gap_pre)} | {f(we[0])} |")
    out = "\n".join(lines) + "\n"
    print(out)
    if "--write" in sys.argv:
        with open(os.path.join(HERE, sys.argv[sys.argv.index("--write") + 1]), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
