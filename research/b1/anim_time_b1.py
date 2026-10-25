"""Average the traversal animation fraction against the traversal time fraction u = t / T per class (grid 0..1 step 0.05).
The curve table (curve-table.csv) is delta(anim); a replica that runs on time needs anim(u) to read it.
Usage: anim_time_b1.py <data_dir> [<data_dir> ...] -> writes anim-time.csv into the first dir and prints it."""
import csv, os, sys
from collections import defaultdict

from aggregate_b1_cls import cls

runs, curves = [], []
for d in sys.argv[1:]:
    runs += list(csv.DictReader(open(os.path.join(d, "runs.csv"), encoding="utf-8")))
    curves += list(csv.DictReader(open(os.path.join(d, "curves.csv"), encoding="utf-8")))
runs = [r for r in runs if int(r["run"]) >= 1000]          # as aggregate_b1.py: drop the per-session warm-up (run 90, ids collide)
curves = [c for c in curves if int(c["run"]) >= 1000]
rc = {r["run"]: cls(r) for r in runs}
G = [i / 20 for i in range(21)]
byrun = defaultdict(list)
for c in curves:
    t, rem = float(c["t"]), float(c["rem"])
    byrun[c["run"]].append((t / (t + rem), float(c["anim"])))
acc = defaultdict(lambda: defaultdict(list))
for run, pts in byrun.items():
    pts.sort()
    pts.append((1.0, 1.0))                                 # the traversal ends with the animation
    for g in G:
        lo = max((p for p in pts if p[0] <= g), default=None, key=lambda p: p[0])
        hi = min((p for p in pts if p[0] >= g), default=None, key=lambda p: p[0])
        if lo and hi:
            v = lo[1] if hi[0] == lo[0] else lo[1] + (hi[1] - lo[1]) * (g - lo[0]) / (hi[0] - lo[0])
            acc[rc[run]][g].append(v)
out = os.path.join(sys.argv[1], "anim-time.csv")
with open(out, "w", newline="") as fh:
    w = csv.writer(fh); ks = sorted(acc); w.writerow(["u"] + ks)
    for g in G:
        w.writerow([g] + [round(sum(acc[k][g]) / len(acc[k][g]), 3) if acc[k][g] else "" for k in ks])
print(open(out).read())
