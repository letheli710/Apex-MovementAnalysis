#!/usr/bin/env python3
"""Cut frames.csv / shots.csv by marks.tsv into cases; print per-case return metrics and replay the springs.txt model.
  py -3 -I analyze.py <dir with frames.csv shots.csv marks.tsv wall.txt> <springs.txt> [tag-prefix ...]"""
import csv, math, os, re, sys
from collections import defaultdict

def load(d):
    wall = int(open(os.path.join(d, "wall.txt")).read().strip()) / 1000
    def rows(fn):
        out = []
        for r in csv.DictReader(open(os.path.join(d, fn))):
            try: out.append({k: float(v) if v not in ("", None) and k != "w" else (v if k == "w" else float("nan")) for k, v in r.items() if k})
            except (ValueError, TypeError): pass
        return out
    F, S = rows("frames.csv"), rows("shots.csv")
    marks = defaultdict(list)
    for l in open(os.path.join(d, "marks.tsv"), encoding="utf-8"):
        t, ts, m = l.rstrip("\n").split("\t")
        marks[t].append((float(ts) - wall, m))
    return F, S, marks

def springs(path):
    txt = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'"(\w+)"\s*\{([^{}]*)\}', txt):
        out[m.group(1)] = {a: float(b) for a, b in re.findall(r'"(\w+)"\s+"([-\d.]+)"', m.group(2))}
    return out

def step(x, v, k, d, dt):
    """Exact solution of x'' = -k x - d v over dt: FUN_140521af0's form."""
    disc = d * d - 4 * k
    if abs(disc) < 1e-3:
        w = d / 2; c = v + w * x; e = math.exp(-w * dt); nx = x + c * dt
        return nx * e, (c - nx * w) * e
    if disc > 0:
        s = math.sqrt(disc); a, b = (-d + s) / 2, (-d - s) / 2
        A = (v - b * x) / (a - b); B = x - A
        return A * math.exp(a * dt) + B * math.exp(b * dt), A * a * math.exp(a * dt) + B * b * math.exp(b * dt)
    w = math.sqrt(-disc) / 2; e = math.exp(-d / 2 * dt)
    A = x; B = (v + d / 2 * x) / w; c, s = math.cos(w * dt), math.sin(w * dt)
    return e * (A * c + B * s), e * (-d / 2 * (A * c + B * s) + w * (-A * s + B * c))

def case(F, S, marks, tag):
    m = marks[tag]; t0, t1 = m[0][0], m[-1][0] + 0.25
    fr = [r for r in F if t0 <= r["t"] <= t1]; sh = [r for r in S if t0 <= r["t"] <= t1]
    return fr, sh

def return_metrics(fr, sh):
    """Last kick to the end: peak of |s2P| after it, then times to fractions of the peak (seconds from last kick)."""
    if not sh: return None
    tl = sh[-1]["t"]; after = [r for r in fr if r["t"] >= tl]
    if len(after) < 5: return None
    pk = max(after, key=lambda r: abs(r["s2P"]))
    p = abs(pk["s2P"]); res = dict(shots=len(sh), peak=p, tpk=pk["t"] - tl)
    pa = [r for r in after if r["t"] >= pk["t"]]
    for frac, nm in ((0.5, "t50"), (0.1, "t10"), (0.01, "t01")):
        res[nm] = next((r["t"] - tl for r in pa if abs(r["s2P"]) <= frac * p), float("nan"))
    sign = 1 if pk["s2P"] > 0 else -1
    res["over"] = max((-sign * r["s2P"] for r in pa), default=0.0)   # overshoot past 0, degrees
    res["end"] = pa[-1]["s2P"]
    res["zero"] = next((r["t"] - tl for r in pa if r["s2P"] == 0 and r["v2P"] == 0), float("nan"))
    res["fracview"] = float("nan")
    z = [r for r in after if abs(r["s2P"]) > 0.3]
    if z: res["fracview"] = sum(r["puP"] / r["s2P"] for r in z) / len(z)
    return res

def replay(fr, sh, W):
    """From the last kick's output state replay the spring with the observed k,d and frame times; return RMS against s2P."""
    if not sh: return float("nan"), float("nan")
    last = sh[-1]; x, v = last["s2P1"], last["v2P1"]; tprev = last["ct"]; err = []; err_n = []
    xn, vn = x, v
    for r in fr:
        if r["t"] <= last["t"]: continue
        dt = r["ct"] - tprev
        if dt <= 0: continue
        k, d = r["kP"], r["dP"]
        if k != k: continue
        x, v = step(x, v, k, d, dt); tprev = r["ct"]
        err.append(x - r["s2P"])
    return (math.sqrt(sum(e * e for e in err) / len(err)) if err else float("nan")), len(err)

def main():
    d, spf = sys.argv[1], sys.argv[2]; pre = sys.argv[3:]
    F, S, marks = load(d)
    print("case\tshots\tpeak\ttpk\tt50\tt10\tt01\tover\tend\tzero\tview/s2\treplayRMS")
    for tag in marks:
        if pre and not any(tag.startswith(p) for p in pre): continue
        fr, sh = case(F, S, marks, tag)
        m = return_metrics(fr, sh)
        if not m: print(tag, "no shots"); continue
        rms, n = replay(fr, sh, None)
        print(f"{tag}\t{m['shots']}\t{m['peak']:.3f}\t{m['tpk']:.3f}\t{m['t50']:.3f}\t{m['t10']:.3f}\t{m['t01']:.3f}\t{m['over']:.3f}\t{m['end']:.3f}\t{m['zero']:.3f}\t{m['fracview']:.3f}\t{rms:.4f}")

if __name__ == "__main__":
    main()
