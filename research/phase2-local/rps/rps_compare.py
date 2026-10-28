"""RPS: per-trial replay error before (Legacy M2 slide rules) vs after (native slide rules), stdlib only.

    python rps_compare.py <before dir> <after dir> [--md out.md] [--json out.json]

<before>/<after>: each holds m2m1/ (BatchReplay -motor both over m2 + m1 trials), m3/ (-motor v2 over m3 trials) and m4/ (-motor v2
-scenarios m4/unity/scenarios.json over the m4 trials), as written by the RPS runner; before = -legacyM2. Per trial: is it unchanged
(steps.csv byte-identical and summary.json equal apart from model_choices, which gains the native slide-rule line), and the summary
error metrics before / after. A trial is "worse" when any listed metric grows by more than 1e-6 or the summed event step error grows.
"""
import json
import os
import sys

METRICS = [("pos_rms_3d_u", "overall"), ("pos_max_3d_u", "overall"), ("vel_rms_3d_ups", "overall"), ("vel_max_3d_ups", "overall"),
           ("spd2d_rms_ups", "overall"), ("jump_max_abs_takeoff_vz_err_ups", None), ("jump_max_abs_apex_err_u", None),
           ("grounded_mismatch_steps", "overall")]
EPS = 1e-6


def content(path):
    b = open(path, "rb").read()
    return b if path.endswith(".csv") else b.replace(b"\r\n", b"\n")


def metric(j, key, sec):
    v = (j.get(sec) or {}).get(key) if sec else j.get(key)
    return None if v is None else float(v)


def events(j):
    """Sum of |sim - ref| over the paired event step deltas (takeoff, land, stop, ...): a later / earlier event is a regression."""
    d = j.get("event_deltas_sim_minus_ref") or {}
    return sum(abs(v) for k, v in d.items() if k.endswith("_steps") and isinstance(v, (int, float)))


def trials(root, sub):
    d = os.path.join(root, sub)
    for t in sorted(os.listdir(d)):
        p = os.path.join(d, t)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "summary.json")):
            yield t, p


def main():
    a = sys.argv[1:]
    md = json_out = None
    if "--md" in a:
        i = a.index("--md"); md = a[i + 1]; del a[i:i + 2]
    if "--json" in a:
        i = a.index("--json"); json_out = a[i + 1]; del a[i:i + 2]
    before, after = a
    rows = []
    for sub in ("m2m1", "m3", "m4"):
        for t, pa in trials(after, sub):
            pb = os.path.join(before, sub, t)
            jb = json.load(open(os.path.join(pb, "summary.json"), encoding="utf-8"))
            ja = json.load(open(os.path.join(pa, "summary.json"), encoding="utf-8"))
            # unchanged = the same per-command trajectory and the same summary apart from model_choices (the native-rule line)
            same = content(os.path.join(pa, "steps.csv")) == content(os.path.join(pb, "steps.csv")) and \
                {k: v for k, v in ja.items() if k != "model_choices"} == {k: v for k, v in jb.items() if k != "model_choices"}
            m = {k: (metric(jb, k, s), metric(ja, k, s)) for k, s in METRICS}
            worse = [k for k, (x, y) in m.items() if x is not None and y is not None and y > x + EPS]
            eb, ea = events(jb), events(ja)
            broke = ["steps %g -> %g" % (eb, ea)] if ea > eb else []
            rows.append({"set": sub, "trial": t, "identical": same, "metrics": m, "worse": worse, "events_broken": broke,
                         "events_before": eb, "events_after": ea})
    changed = [r for r in rows if not r["identical"]]
    bad = [r for r in changed if r["worse"] or r["events_broken"]]
    lines = []
    for sub in ("m2m1", "m3", "m4"):
        rs = [r for r in rows if r["set"] == sub]
        lines.append(f"- {sub}: {len(rs)} trials, {sum(r['identical'] for r in rs)} unchanged, {sum(not r['identical'] for r in rs)} changed")
    lines.append(f"- changed: {len(changed)}; worse on any metric / event steps: {len(bad)}")
    lines.append("")
    lines.append("| set | trial | pos rms (u) | pos max (u) | vel rms (u/s) | vel max (u/s) | takeoff vz max (u/s) | apex max (u) | worse |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    def f(p):
        x, y = p
        return "–" if x is None else (f"{x:.3f}" if abs(x - y) < 5e-4 else f"{x:.3f} → **{y:.3f}**")
    for r in changed:
        m = r["metrics"]
        w = ", ".join(r["worse"] + ["events:" + e for e in r["events_broken"]]) or "no"
        lines.append(f"| {r['set']} | {r['trial']} | {f(m['pos_rms_3d_u'])} | {f(m['pos_max_3d_u'])} | {f(m['vel_rms_3d_ups'])} | "
                     f"{f(m['vel_max_3d_ups'])} | {f(m['jump_max_abs_takeoff_vz_err_ups'])} | {f(m['jump_max_abs_apex_err_u'])} | {w} |")
    text = "\n".join(lines)
    print(text)
    if md:
        open(md, "w", encoding="utf-8", newline="\n").write(text + "\n")
    if json_out:
        json.dump(rows, open(json_out, "w", encoding="utf-8"), indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
