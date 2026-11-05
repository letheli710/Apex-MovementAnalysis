#!/usr/bin/env python3
"""Can the guns be grouped: cluster on the gun's angles and swing per state, then how far each gun sits from its group. Also the averaged one-cycle waves and their repeatability, and checks against the earlier table.
  py -3 -I an_hp3.py <hold-pose dir>
Writes HP-WAVE-MEAN.tsv, HP-GROUPS.tsv. Prints the rest."""
import csv, math, os, statistics as st, sys
from collections import defaultdict
import numpy as np

D = sys.argv[1]
rd = lambda n: list(csv.DictReader(open(os.path.join(D, n), encoding="utf-8"), delimiter="\t"))
P = {(r["gun"], r["state"]): r for r in rd("HP-POSE.tsv")}
guns = sorted({g for g, _ in P})
AX = ("mF", "mR", "mU", "gP", "gY", "gR")
num = lambda r, k: float(r[k]) if r.get(k) not in (None, "") else float("nan")

# Averaged waves: resample every run onto 32 phases, mean over runs
W = defaultdict(lambda: defaultdict(dict))
per = {}
for r in rd("HP-WAVE.tsv"):
    k = (r["gun"], r["state"]); per[k] = float(r["period"])
    W[k][int(r["run"])][round(float(r["phase"]) * 32)] = [float(r[a]) for a in AX]
mean = {}
qc = {}
with open(os.path.join(D, "HP-WAVE-MEAN.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("gun\tstate\tperiod\tphase\t" + "\t".join(AX) + "\n")
    for k, runs in W.items():
        arr = []
        for rn, ph in runs.items():
            a = np.array([ph.get(i, [np.nan] * 6) for i in range(32)])
            arr.append(a)
        arr = np.array(arr)
        m = np.nanmean(arr, axis=0)
        mean[k] = m
        qc[k] = float(np.nanmax(np.abs(arr[0, :, :3] - arr[-1, :, :3]))) if len(arr) > 1 else float("nan")
        for i in range(32):
            f.write(f"{k[0]}\t{k[1]}\t{per[k]:.3f}\t{i / 32:.4f}\t" + "\t".join(f"{x:.3f}" for x in m[i]) + "\n")


def cluster(names, feat, thr):
    """Single link on Euclidean distance."""
    lab = {n: n for n in names}
    for a in names:
        for b in names:
            if a < b and np.linalg.norm(feat[a] - feat[b]) < thr:
                la, lb = lab[a], lab[b]
                for n in names:
                    if lab[n] == lb: lab[n] = la
    G = defaultdict(list)
    for n in names: G[lab[n]].append(n)
    return sorted(G.values(), key=len, reverse=True)


rows = []
for state, thr in (("sprint", 8.0), ("crouch", 8.0), ("slide", 8.0), ("slidehold", 8.0), ("crouchwalk", 8.0), ("walk", 2.0), ("jump", 3.0), ("drop", 3.0)):
    names = [g for g in guns if (g, state) in P and P[g, state].get("dgP")]
    # features: the gun's mean angles, in degrees, plus the swing of the angles where there is a wave
    feat = {}
    for g in names:
        r = P[g, state]
        v = [num(r, "dgP"), num(r, "dgY"), num(r, "dgR")]
        if (g, state) in mean: v += list(np.nanmax(mean[g, state][:, 3:], axis=0) - np.nanmin(mean[g, state][:, 3:], axis=0))
        feat[g] = np.array(v)
    C = cluster(names, feat, thr)
    print(f"== {state}: {len(C)} groups (threshold {thr} deg)")
    for i, c in enumerate(C):
        rs = [P[g, state] for g in c]
        ms = {a: st.mean(num(r, "d" + a) for r in rs) for a in AX}
        sd = {a: (st.pstdev(num(r, "d" + a) for r in rs) if len(rs) > 1 else 0) for a in AX}
        print(f"  G{i + 1} n={len(c)}: {' '.join(c)}")
        print("     mean  " + " ".join(f"{a}={ms[a]:.1f}" for a in AX))
        print("     sd    " + " ".join(f"{a}={sd[a]:.2f}" for a in AX))
        if (c[0], state) in mean and len(c) > 1:
            # wave shape: correlation of each gun's angle wave with the group's
            gm = np.nanmean([mean[g, state] for g in c if (g, state) in mean], axis=0)
            resid = [float(np.nanmax(np.abs(mean[g, state][:, 3:] - gm[:, 3:]))) for g in c if (g, state) in mean]
            residm = [float(np.nanmax(np.abs(mean[g, state][:, :3] - gm[:, :3]))) for g in c if (g, state) in mean]
            print(f"     wave: worst angle gap to group {max(resid):.1f} deg (median {st.median(resid):.1f}); worst muzzle gap {max(residm):.1f} u (median {st.median(residm):.1f})")
        for g in c:
            rows.append(dict(state=state, group=i + 1, gun=g, **{a: num(P[g, state], "d" + a) for a in AX}))
with open(os.path.join(D, "HP-GROUPS.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("state\tgroup\tgun\t" + "\t".join("d" + a for a in AX) + "\n")
    for r in rows:
        f.write(f"{r['state']}\t{r['group']}\t{r['gun']}\t" + "\t".join(f"{r[a]:.2f}" for a in AX) + "\n")

print("== wave repeat, worst muzzle gap between runs (u)")
for s in ("sprint", "walk", "crouchwalk"):
    v = [x for k, x in qc.items() if k[1] == s and x == x]
    print(s, f"median {st.median(v):.2f} max {max(v):.2f}", [k[0] for k, x in qc.items() if k[1] == s and x > 2][:8])
print("== slide natural against held speed, muzzle and angles")
d = []
for g in guns:
    a, b = P.get((g, "slide")), P.get((g, "slidehold"))
    if a and b and a.get("mF") and b.get("mF"):
        d.append((math.dist([num(a, k) for k in AX[:3]], [num(b, k) for k in AX[:3]]), g, max(abs(num(a, k) - num(b, k)) for k in AX[3:])))
print("muzzle gap median", round(st.median(x[0] for x in d), 2), "max", sorted(d, reverse=True)[:4])
print("secs: slide", round(st.mean(num(P[g, "slide"], "secs") for g in guns), 2), "hold", round(st.mean(num(P[g, "slidehold"], "secs") for g in guns), 2), "sprint", round(st.mean(num(P[g, "sprint"], "secs") for g in guns), 2), "walk", round(st.mean(num(P[g, "walk"], "secs") for g in guns), 2), "crouchwalk", round(st.mean(num(P[g, "crouchwalk"], "secs") for g in guns), 2))
print("== repeat of mean pose (u): state median max")
for s in ("stand", "walk", "sprint", "crouch", "crouchwalk", "slide", "slidehold", "jump", "drop"):
    v = [num(P[g, s], "repeat") for g in guns if (g, s) in P and P[g, s].get("repeat")]
    print(s, round(st.median(v), 3), round(max(v), 3))
print("== standing muzzle against D-VIEWMODEL")
VM = {r["gun"]: r for r in rd("../D-VIEWMODEL.tsv") if r["mode"] == "hip"}
gaps = [(math.dist([num(P[g, "stand"], "m" + a) for a in "FRU"], [float(VM[g]["muzzle" + a]) for a in "FRU"]), g) for g in guns if g in VM and (g, "stand") in P]
print("median", round(st.median(x[0] for x in gaps), 3), "max", sorted(gaps, reverse=True)[:4])
print("== standing: muzzle F R U and gun angles")
for g in guns:
    r = P[g, "stand"]
    print(f"  {g:12s} {num(r, 'mF'):6.1f} {num(r, 'mR'):5.1f} {num(r, 'mU'):5.1f}  {num(r, 'gP'):6.2f} {num(r, 'gY'):6.2f} {num(r, 'gR'):7.1f}  centre={'yes' if r.get('sF') and float(r['sF']) else 'no'}")
print("== transitions, medians over guns (t50 t90 s)")
T = rd("HP-TRANSITION.tsv")
for n in sorted({r["name"] for r in T}):
    v = [r for r in T if r["name"] == n]
    a = [float(r["t50"]) for r in v if r["t50"]]; b = [float(r["t90"]) for r in v if r["t90"]]; dd = [float(r["dist"]) for r in v]
    print(f"  {n:24s} n={len(v)} dist {st.median(dd):.1f} t50 {st.median(a) if a else 0:.2f} t90 {st.median(b) if b else 0:.2f} range t90 {min(b) if b else 0:.2f}-{max(b) if b else 0:.2f}")
print("== turn: muzzle right and yaw while turning")
for r in rd("HP-TURN.tsv")[:40]:
    print(f"  {r['gun']:12s} L dR {float(r['left_dR']):.2f} dY {float(r['left_dY']):.2f} back90 {r['left_back90']} R dR {float(r['right_dR']):.2f} dY {float(r['right_dY']):.2f} back90 {r['right_back90']}")
