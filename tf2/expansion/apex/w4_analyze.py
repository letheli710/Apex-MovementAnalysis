#!/usr/bin/env python3
"""Fit the [W4] trk lines of a w4_probe.py 'scripted' run: gravity from free-flight
segments, bounce speed ratios, lifetime (fuse / planting).

  python -I w4_analyze.py runs/<stamp>_scripted.txt
"""
import re
import sys
from collections import defaultdict

TRK = re.compile(r"trk (\S+) t=([\d.]+) o=([-\d.]+),([-\d.]+),([-\d.]+) v=([-\d.]+),([-\d.]+),([-\d.]+)")
END = re.compile(r"trk (\S+) end t=([\d.]+) valid=(\d)")


def main(path):
    tr, ends = defaultdict(list), {}
    for line in open(path, encoding="utf-8"):
        m = TRK.search(line)
        if m:
            tr[m.group(1)].append([float(x) for x in m.groups()[1:]])
            continue
        m = END.search(line)
        if m:
            ends[m.group(1)] = float(m.group(2))
    for name, rows in tr.items():
        print(f"== {name}: {len(rows)} samples, last t={rows[-1][0]:.3f}, end t={ends.get(name)}")
        g_est, events = [], []
        for a, b in zip(rows, rows[1:]):
            dt = b[0] - a[0]
            if dt <= 0:
                continue
            dvz = b[6] - a[6]
            sp_a = (a[4] ** 2 + a[5] ** 2 + a[6] ** 2) ** 0.5
            sp_b = (b[4] ** 2 + b[5] ** 2 + b[6] ** 2) ** 0.5
            dvh = abs(b[4] - a[4]) + abs(b[5] - a[5])
            if dvh < 1e-3 and dvz < 0:
                g_est.append(-dvz / dt)
            elif sp_a > 1:
                events.append((b[0], sp_a, sp_b, sp_b / sp_a, a[6], b[6]))
        if g_est:
            g_est.sort()
            print(f"   gravity (free flight) median={g_est[len(g_est) // 2]:.1f} u/s^2 n={len(g_est)}")
        for t, sa, sb, r, vza, vzb in events[:8]:
            print(f"   event t={t:.3f} |v| {sa:.1f} -> {sb:.1f} (x{r:.3f}) vz {vza:.1f} -> {vzb:.1f}")
        stop = next((r[0] for r in rows if (r[4] ** 2 + r[5] ** 2 + r[6] ** 2) ** 0.5 < 1), None)
        print(f"   first stationary sample t={stop}")


if __name__ == "__main__":
    main(sys.argv[1])
