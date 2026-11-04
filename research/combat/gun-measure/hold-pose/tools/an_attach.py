#!/usr/bin/env python3
"""From attach_scan.txt: the largest set of attachments whose distances do not change between standing and sprinting is the gun's rigid body. Fit the rotation from that set and compare it with the muzzle's own angles and with the line sight centre to muzzle.
  py -3 -I an_attach.py <attach_scan.txt>"""
import itertools, math, re, sys
from collections import defaultdict
RX = re.compile(r"\[RT\] at (\w+?)_(stand|sprint\d) i=(\d+) p=(\S+?),(\S+?),(\S+) g=(\S+?),(\S+?),(\S+)")
D = defaultdict(lambda: defaultdict(dict))
N = defaultdict(dict)
for l in open(sys.argv[1], encoding="utf-8"):
    g = RX.search(l)
    if g: D[g[1]][g[2]][int(g[3])] = (tuple(map(float, g.groups()[3:6])), tuple(map(float, g.groups()[6:9])))
    n = re.search(r"\[RT\] at (\w+?)_stand name (\S+) (-?\d+)", l)
    if n: N[n[1]][n[2]] = int(n[3])


def rigid_set(a, b, tol=0.02):
    ids = sorted(set(a) & set(b))
    best = []
    for seed in ids:
        s = [i for i in ids if abs(math.dist(a[seed][0], a[i][0]) - math.dist(b[seed][0], b[i][0])) < tol]
        s2 = [i for i in s if sum(abs(math.dist(a[i][0], a[j][0]) - math.dist(b[i][0], b[j][0])) < tol for j in s) >= len(s) * 0.9]
        if len(s2) > len(best): best = s2
    return best


def fit_axis(a, b, ids):
    """Direction of the gun's long axis from the two points farthest apart in the set; returns pitch and yaw change."""
    p, q = max(itertools.combinations(ids, 2), key=lambda x: math.dist(a[x[0]][0], a[x[1]][0]))
    if a[p][0][0] > a[q][0][0]: p, q = q, p
    def py(s):
        d = [s[q][0][k] - s[p][0][k] for k in range(3)]
        return math.degrees(math.atan2(d[2], math.hypot(d[0], d[1]))), math.degrees(math.atan2(d[1], d[0]))
    A, B = py(a), py(b)
    return p, q, math.dist(a[p][0], a[q][0]), B[0] - A[0], B[1] - A[1]


for gun, S in D.items():
    st_ = S["stand"]
    print("==", gun, "attachments", len(st_), "named", {k: v for k, v in N[gun].items() if v > 0})
    # near the muzzle: the attachment closest to the sight centre name, read by index when present
    for snap in sorted(k for k in S if k != "stand"):
        b = S[snap]
        ids = rigid_set(st_, b)
        p, q, L, dP, dY = fit_axis(st_, b, ids)
        mz = N[gun].get("muzzle_flash", -1)
        ga = st_[ids[0]][1]
        print(snap, f"rigid {len(ids)}/{len(st_)}", f"axis i{p}-i{q} {L:.1f}u  rigid dPitch={dP:.2f} dYaw={dY:.2f}", "muzzle in set" if mz in ids else "muzzle NOT in set", f"muzzle attach dP={b[mz][1][0] - st_[mz][1][0]:.2f} dY={b[mz][1][1] - st_[mz][1][1]:.2f}" if mz in b else "")
        for nm, i in N[gun].items():
            if nm.startswith("ADS") and i > 0:
                print("   ", nm, i, "in set" if i in ids else "NOT in set", "stand", st_[i][0], "now", b[i][0], "g", b[i][1])
