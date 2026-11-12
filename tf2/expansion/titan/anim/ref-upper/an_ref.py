"""ref-titan-upper analysis: A11 (3P reload scaling), A12 (which hit reaction plays), F21 (nearby pilot shake).

Usage: py -3 -I an_ref.py <run dir> [<run dir> ...]
Reads raw.log of runs made with ref_runner.py (HSD.RefUpper lines RC / RS / RF / RN / RU, TAG).
Only the first match of a run is used (a server script error restarts the match and the plan).
Prints the tables used in ref-upper/REF-UPPER-1109.md and writes out/<run>_<kind>.tsv summaries.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def parse(run):
    """-> dict kind -> list of (t, fields), tags [(t, name)], events [(t, text)]"""
    out = {"RC": [], "RS": [], "RF": [], "RN": []}
    tags, events = [], []
    last_sv = -1.0
    for line in open(os.path.join(run, "raw.log"), encoding="utf-8", errors="replace"):
        i = line.find("HSDDIAG ")
        if i < 0:
            continue
        p = line[i:].split()
        k = p[1]
        if k == "RU" and p[2] == "init" and last_sv > 0:
            break  # match restarted
        if k == "TAG":
            tags.append((float(p[3]), p[2]))
            last_sv = float(p[3])
        elif k == "RU":
            try:
                t = float(p[-1])
            except ValueError:
                t = last_sv
            events.append((t, " ".join(p[2:])))
        elif k in out:
            try:
                t = float(p[2])
            except ValueError:
                continue
            out[k].append((t, p[3:]))
            if k == "RS":
                last_sv = t
    return out, tags, events


def tag_span(tags, name):
    for j, (t, n) in enumerate(tags):
        if n == name:
            return t, tags[j + 1][0] if j + 1 < len(tags) else 1e9
    return None


def fl(x):
    try:
        return float(x)
    except ValueError:
        return float("nan")


def a11(d, tags, events, cls):
    """reload windows from the client 'reloading' flag; HAND_L deviation from the idle mean"""
    rc = [(t, f) for t, f in d["RC"] if f[0] == "1" and len(f) >= 19]
    sp = tag_span(tags, "a11_%s_idle" % cls)
    if not sp:
        return []
    idle = [f for t, f in rc if sp[0] + 0.3 <= t < sp[1]]
    if not idle:
        return []
    ref = [sum(fl(f[k]) for f in idle) / len(idle) for k in (10, 11, 12)]
    res = []
    for k in range(2):
        sp = tag_span(tags, "a11_%s_rl%d" % (cls, k))
        if not sp:
            continue
        seg = [(t, f) for t, f in rc if sp[0] - 0.2 <= t < sp[1]]
        on = [t for t, f in seg if f[8] == "1"]
        if not on:
            continue
        r0, r1 = on[0], on[-1]
        dev = [(t, math.dist([fl(f[10]), fl(f[11]), fl(f[12])], ref)) for t, f in seg]
        thr = 2.0
        moving = [t for t, v in dev if v > thr]
        m0 = moving[0] if moving else float("nan")
        m1 = moving[-1] if moving else float("nan")
        peak = max(dev, key=lambda x: x[1])
        at_end = max((v for t, v in dev if r1 - 0.05 <= t <= r1 + 0.02), default=float("nan"))
        after = [(t, v) for t, v in dev if r1 < t <= r1 + 0.6]
        res.append({"cls": cls, "k": k, "reload_s": round(r1 - r0, 3), "hand_move_start": round(m0 - r0, 3),
                    "hand_move_end": round(m1 - r0, 3), "hand_move_s": round(m1 - m0, 3), "peak_u": round(peak[1], 1),
                    "peak_at": round(peak[0] - r0, 3), "dev_at_reload_end_u": round(at_end, 1),
                    "dev_0.2s_after_u": round(min((v for t, v in after if t >= r1 + 0.2), default=float("nan")), 1),
                    "curve": [(round(t - r0, 3), round(v, 1)) for t, v in dev[:: max(1, len(dev) // 60)]]})
    return res


def a12(d, tags, events):
    """per trial: hit time, client main-sequence cycle rate before / after, server speed, HAND_L / CHEST deviation"""
    rc = [(t, f) for t, f in d["RC"] if f[0] == "1" and len(f) >= 19]
    rs = [(t, f) for t, f in d["RS"] if f[0] == "1"]
    hits = [(t, e) for t, e in events if e.startswith("hit ")]
    res = []
    for j, (t0, name) in enumerate(tags):
        if not name.startswith("a12_"):
            continue
        t1 = tags[j + 1][0] if j + 1 < len(tags) else 1e9
        hs = [(t, e) for t, e in hits if t0 <= t < t1]
        seg = [(t, f) for t, f in rc if t0 <= t < t1]
        sv = [(t, f) for t, f in rs if t0 <= t < t1]
        res.append({"name": name, "hits": hs, "rc": seg, "rs": sv})
    return res


def cycle_events(seg):
    """split the client cycle series into runs; a run ends where the cycle jumps back by more than 0.3
    (loop wrap) or forward by more than 0.3 (new sequence). Returns [(t_start, t_end, rate per s, c0, c1)]"""
    runs = []
    if not seg:
        return runs
    st = 0
    for i in range(1, len(seg)):
        c_prev, c = fl(seg[i - 1][1][7]), fl(seg[i][1][7])
        if abs(c - c_prev) > 0.3:
            runs.append((st, i - 1))
            st = i
    runs.append((st, len(seg) - 1))
    out = []
    for a, b in runs:
        ta, tb = seg[a][0], seg[b][0]
        ca, cb = fl(seg[a][1][7]), fl(seg[b][1][7])
        rate = (cb - ca) / (tb - ta) if tb > ta else float("nan")
        out.append((round(ta, 3), round(tb, 3), round(rate, 4), round(ca, 3), round(cb, 3)))
    return out


def f21(d, tags, events):
    rc = [(t, f) for t, f in d["RC"] if f[0] == "0"]
    rn = d["RN"]
    res = []
    for j, (t0, name) in enumerate(tags):
        if not name.startswith("f21_"):
            continue
        t1 = tags[j + 1][0] if j + 1 < len(tags) else 1e9
        seg = [(t, [fl(x) for x in f[1:7]]) for t, f in rc if t0 <= t < t1]
        near = [(t, fl(f[0]), fl(f[4]), fl(f[5])) for t, f in rn if t0 <= t < t1]
        if not seg:
            continue
        mx = [max(abs(v[k]) for t, v in seg) for k in range(6)]
        dmin = min((x[1] for x in near), default=float("nan"))
        dmax = max((x[1] for x in near), default=float("nan"))
        res.append({"name": name, "n": len(seg), "max_ang": mx[:3], "max_pos": mx[3:], "dist_min": dmin, "dist_max": dmax,
                    "seg": seg, "near": near})
    return res


if __name__ == "__main__":
    for run in sys.argv[1:]:
        d, tags, events = parse(run)
        print("==", os.path.basename(run), {k: len(v) for k, v in d.items()}, "tags", len(tags))
        for cls in ("monarch", "legion", "tone"):
            for r in a11(d, tags, events, cls):
                print("A11", {k: v for k, v in r.items() if k != "curve"})
        for r in a12(d, tags, events):
            ce = cycle_events(r["rc"])
            sp = [math.hypot(fl(f[9]), fl(f[10])) for t, f in r["rs"]]
            print("A12", r["name"], [e for t, e in r["hits"]])
            print("    cycle runs", ce)
            print("    speed", [round(x) for x in sp])
        for r in f21(d, tags, events):
            print("F21", r["name"], r["n"], "ang", [round(x, 3) for x in r["max_ang"]], "pos", [round(x, 3) for x in r["max_pos"]],
                  "dist", "%.0f-%.0f" % (r["dist_min"], r["dist_max"]))
