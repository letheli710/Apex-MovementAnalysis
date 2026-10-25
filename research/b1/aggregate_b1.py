"""Group B1 traversals into classes and average the delta(anim) curve per class (grid 0..1 step 0.05).
Usage: aggregate_b1.py <data_dir> [<data_dir> ...] -> prints classes.csv / curve-table.csv into the first dir."""
import csv, math, os, sys
from collections import defaultdict

from aggregate_b1_cls import cls

runs, curves = [], []
for d in sys.argv[1:]:
    runs += list(csv.DictReader(open(os.path.join(d, "runs.csv"), encoding="utf-8")))
    curves += list(csv.DictReader(open(os.path.join(d, "curves.csv"), encoding="utf-8")))
runs = [r for r in runs if int(r["run"]) >= 1000]          # drop the per-session warm-up (run 90, ids collide)
curves = [c for c in curves if int(c["run"]) >= 1000]
rc = {r["run"]: cls(r) for r in runs}
G = [i / 20 for i in range(21)]
acc = defaultdict(lambda: defaultdict(list))
byrun = defaultdict(list)
for c in curves:
    byrun[c["run"]].append((float(c["anim"]), float(c["delta"])))
for run, pts in byrun.items():
    pts.sort()
    for g in G:
        # linear interpolation of delta at anim g
        lo = max((p for p in pts if p[0] <= g), default=None, key=lambda p: p[0])
        hi = min((p for p in pts if p[0] >= g), default=None, key=lambda p: p[0])
        if lo and hi:
            v = lo[1] if hi[0] == lo[0] else lo[1] + (hi[1] - lo[1]) * (g - lo[0]) / (hi[0] - lo[0])
            acc[rc[run]][g].append(v)
out = sys.argv[1]
summ = defaultdict(list)
for r in runs:
    summ[rc[r["run"]]].append(r)
rows = []
for k, rs in sorted(summ.items()):
    f = lambda key: [float(r[key]) for r in rs if r[key] not in ("", "None")]
    m = lambda xs: sum(xs) / len(xs) if xs else float("nan")
    sd = lambda xs: (sum((x - m(xs)) ** 2 for x in xs) / max(1, len(xs) - 1)) ** 0.5 if len(xs) > 1 else 0
    rows.append(dict(cls=k, n=len(rs), T=round(m(f("duration")), 3), T_sd=round(sd(f("duration")), 3), peak=round(m(f("peak_delta")), 2),
                     peak_anim=round(m(f("peak_anim")), 3), open_anim=round(m(f("win_open_anim")), 3), open_anim_sd=round(sd(f("win_open_anim")), 3),
                     open_rem=round(m(f("win_open_rem")), 3), open_rem_min=round(min(f("win_open_rem")), 3), open_rem_max=round(max(f("win_open_rem")), 3)))
with open(os.path.join(out, "classes.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open(os.path.join(out, "curve-table.csv"), "w", newline="") as fh:
    w = csv.writer(fh); ks = sorted(acc); w.writerow(["anim"] + ks)
    for g in G:
        w.writerow([g] + [round(sum(acc[k][g]) / len(acc[k][g]), 3) if acc[k][g] else "" for k in ks])
for r in rows: print(r)
print(open(os.path.join(out, "curve-table.csv")).read())
