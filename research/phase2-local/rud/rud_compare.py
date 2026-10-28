"""RUD: per-trial replay error before (RPS baseline: no duck hull, instant ground redirect) vs after (duck hull airUnduckDrop 16.5 and
groundVectorRedirect on, as Reference), stdlib only.

    python rud_compare.py <before dir> <after dir> [--md out.md] [--json out.json]

<before>/<after>: each holds m2m1/, m3/ and m4/ as written by the RPS runner (../rps/README.md); before = the RPS replay motor (HSD-Unity
main before RUD, checked by ../rps/rps_check.py), after = the RUD default. Per trial: is it unchanged (steps.csv byte-identical and summary.json
equal apart from model_choices, parameters and parameter_provenance, which gain the two RUD lines / airUnduckDrop, airUnduckMinAfterTakeoff,
hullCrouchTime, groundVectorRedirect), and the summary error metrics before / after. A trial is "worse" when any listed metric grows by more than 1e-6 or the summed
event step error grows (the same rule as ../rps/rps_compare.py, plus the z error and the flag mismatches).
"""
import json
import os
import sys

METRICS = [("pos_rms_3d_u", "overall"), ("pos_max_3d_u", "overall"), ("pos_rms_z_u", "overall"), ("pos_max_abs_z_u", "overall"),
           ("vel_rms_3d_ups", "overall"), ("vel_max_3d_ups", "overall"), ("spd2d_rms_ups", "overall"), ("vz_rms_ups", "overall"),
           ("jump_max_abs_takeoff_vz_err_ups", None), ("jump_max_abs_apex_err_u", None), ("grounded_mismatch_steps", "overall"),
           ("sliding", "flag_mismatch_steps"), ("sprinting", "flag_mismatch_steps"), ("maxspeed", "flag_mismatch_steps")]
IGNORED = ("model_choices", "parameters", "parameter_provenance")
RUD_KEYS = {"airUnduckDrop", "airUnduckMinAfterTakeoff", "hullCrouchTime", "groundVectorRedirect"}
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
    rows, param_drift = [], []
    for sub in ("m2m1", "m3", "m4"):
        for t, pa in trials(after, sub):
            pb = os.path.join(before, sub, t)
            jb = json.load(open(os.path.join(pb, "summary.json"), encoding="utf-8"))
            ja = json.load(open(os.path.join(pa, "summary.json"), encoding="utf-8"))
            # the only parameter changes allowed are the two RUD switches (the v2 motor; the M1 first guess has none)
            ka = {k: v for k, v in (ja.get("parameters") or {}).items() if k not in RUD_KEYS}
            if ka != (jb.get("parameters") or {}):
                param_drift.append(f"{sub}/{t}")
            same = content(os.path.join(pa, "steps.csv")) == content(os.path.join(pb, "steps.csv")) and \
                {k: v for k, v in ja.items() if k not in IGNORED} == {k: v for k, v in jb.items() if k not in IGNORED}
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
    lines.append(f"- parameters other than the RUD switches changed: {len(param_drift)}" + (" (" + ", ".join(param_drift) + ")" if param_drift else ""))
    lines.append("")
    lines.append("| set | trial | pos rms (u) | pos max (u) | z rms (u) | z max (u) | vel rms (u/s) | vel max (u/s) | apex max (u) | events (steps) | worse |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")

    def f(p):
        x, y = p
        return "–" if x is None else (f"{x:.3f}" if abs(x - y) < 5e-4 else f"{x:.3f} → **{y:.3f}**")
    for r in changed:
        m = r["metrics"]
        w = ", ".join(r["worse"] + ["events:" + e for e in r["events_broken"]]) or "no"
        ev = f"{r['events_before']:g}" if r["events_before"] == r["events_after"] else f"{r['events_before']:g} → **{r['events_after']:g}**"
        lines.append(f"| {r['set']} | {r['trial']} | {f(m['pos_rms_3d_u'])} | {f(m['pos_max_3d_u'])} | {f(m['pos_rms_z_u'])} | "
                     f"{f(m['pos_max_abs_z_u'])} | {f(m['vel_rms_3d_ups'])} | {f(m['vel_max_3d_ups'])} | {f(m['jump_max_abs_apex_err_u'])} | {ev} | {w} |")
    text = "\n".join(lines)
    print(text)
    if md:
        open(md, "w", encoding="utf-8", newline="\n").write(text + "\n")
    if json_out:
        json.dump(rows, open(json_out, "w", encoding="utf-8"), indent=1)
    return 1 if bad or param_drift else 0


if __name__ == "__main__":
    sys.exit(main())
