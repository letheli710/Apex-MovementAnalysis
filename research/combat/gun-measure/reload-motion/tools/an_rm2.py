#!/usr/bin/env python3
"""Rhythm of each reload, from the tables: how bunched the motion is, the fast events, the rests, and what is left after the unlock.
  py -3 -I an_rm2.py <reload-motion dir>
Writes RM-RHYTHM.tsv, RM-EVENTS.tsv. Prints a digest."""
import csv, glob, os, re, statistics as st, sys
from collections import defaultdict
import numpy as np

D = sys.argv[1]
S = {(r["gun"], r["kind"]): r for r in csv.DictReader(open(os.path.join(D, "RM-SUMMARY.tsv")), delimiter="\t")}


def table(p):
    L = [l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    k = L[0].rstrip("\n").split("\t")
    R = [dict(zip(k, l.rstrip("\n").split("\t"))) for l in L[1:]]
    a = {x: np.array([float(r[x]) for r in R]) for x in k if x not in ("seq",)}
    return a


rows, ev = [], []
for p in sorted(glob.glob(os.path.join(D, "tables", "*.tsv"))):
    gun, kind = os.path.basename(p)[:-4].rsplit("_", 1)
    a = table(p); s = S[gun, kind]
    t = a["t"]; dur = float(s["dur"]) if s.get("dur") else t[-1]
    ammo = float(s["ammo"]) if s.get("ammo") else float("nan"); unlock = float(s["unlock"]) if s.get("unlock") else float("nan")
    ang = a["speedAngle"]; L = a["speedL"]; M = a["speedMuzzle"]; R = a["speedR"]
    g0 = np.array([a["gP"][0], a["gY"][0], a["gR"][0]]); m0 = np.array([a["mF"][0], a["mR"][0], a["mU"][0]])
    # how far the gun is from where it started
    dg = np.linalg.norm(np.stack([a["gP"], a["gY"], a["gR"]], 1) - g0, axis=1)
    dm = np.linalg.norm(np.stack([a["mF"], a["mR"], a["mU"]], 1) - m0, axis=1)
    # bunching: the share of the path done in the fastest 20 % of the time, for gun angle and left hand; a linear motion gives 0.20
    def bunch(s_):
        o = np.sort(s_)[::-1]; n = max(1, len(o) // 5)
        return float(o[:n].sum() / o.sum()) if o.sum() else float("nan")
    # rests: 0.15 s or longer with the gun and the left hand both slow
    slow = (ang < 30) & (L < 25)
    rests = []; i = 0
    while i < len(t):
        if slow[i]:
            j = i
            while j + 1 < len(t) and slow[j + 1]: j += 1
            if t[j] - t[i] >= 0.15: rests.append((float(t[i]), float(t[j])))
            i = j + 1
        else: i += 1
    after = t >= unlock if unlock == unlock else np.zeros_like(t, bool)
    row = dict(gun=gun, kind=kind, dur=dur, ammo=ammo, unlock=unlock, ammo_frac=ammo / dur, unlock_frac=unlock / dur,
               peakAngle=float(ang.max()), tPeakAngle=float(t[ang.argmax()]), medAngle=float(np.median(ang)), peakL=float(L.max()), tPeakL=float(t[L.argmax()]), peakR=float(R.max()), tPeakR=float(t[R.argmax()]), peakM=float(M.max()), tPeakM=float(t[M.argmax()]),
               bunchAngle=bunch(ang), bunchL=bunch(L), bunchM=bunch(M), maxTilt=float(dg.max()), tMaxTilt=float(t[dg.argmax()]), maxOffset=float(dm.max()), tMaxOffset=float(t[dm.argmax()]),
               tiltAtUnlock=float(np.interp(unlock, t, dg)), offsetAtUnlock=float(np.interp(unlock, t, dm)), speedAfterUnlockMax=float(M[after].max()) if after.any() else float("nan"), angleAfterUnlockMax=float(ang[after].max()) if after.any() else float("nan"),
               tiltAtAmmo=float(np.interp(ammo, t, dg)), restCount=len(rests), restTotal=float(sum(b - a_ for a_, b in rests)), rests=" ".join(f"{a_:.2f}-{b:.2f}" for a_, b in rests))
    # nearest fast events to the ammo moment
    def near(tr, s_, floor):
        idx = [i for i in range(1, len(s_) - 1) if s_[i] >= s_[i - 1] and s_[i] > s_[i + 1] and s_[i] > floor]
        if not idx or ammo != ammo: return ""
        return float(t[min(idx, key=lambda i: abs(t[i] - ammo))] - ammo)
    row["nearestAnglePeakToAmmo"] = near("a", ang, 80); row["nearestLPeakToAmmo"] = near("l", L, 40)
    rows.append(row)
keys = list(rows[0])
with open(os.path.join(D, "RM-RHYTHM.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(keys) + "\n")
    for r in rows: f.write("\t".join((f"{r[k]:.3f}" if isinstance(r[k], float) else str(r[k])) for k in keys) + "\n")
print("gun kind dur ammo unlock | peakA@t medA bunchA | peakL@t bunchL | peakR@t | peakM@t | tilt@t offs@t | at unlock tilt offs angleSpeedAfter | rests")
for r in rows:
    print(f"{r['gun']:11s} {r['kind']} {r['dur']:.2f} {r['ammo']:.2f} {r['unlock']:.2f} | {r['peakAngle']:.0f}@{r['tPeakAngle']:.2f} {r['medAngle']:.0f} {r['bunchAngle']:.2f} | {r['peakL']:.0f}@{r['tPeakL']:.2f} {r['bunchL']:.2f} | {r['peakR']:.0f}@{r['tPeakR']:.2f} | {r['peakM']:.0f}@{r['tPeakM']:.2f} | {r['maxTilt']:.0f}@{r['tMaxTilt']:.2f} {r['maxOffset']:.1f}@{r['tMaxOffset']:.2f} | {r['tiltAtUnlock']:.1f} {r['offsetAtUnlock']:.1f} {r['angleAfterUnlockMax']:.0f} | {r['rests'][:40]}")
print("== medians")
for k in ("ammo_frac", "unlock_frac", "bunchAngle", "bunchL", "bunchM", "tiltAtUnlock", "offsetAtUnlock", "tiltAtAmmo", "nearestAnglePeakToAmmo", "nearestLPeakToAmmo", "restTotal", "restCount"):
    for kind in ("tac", "emp"):
        v = [r[k] for r in rows if r["kind"] == kind and isinstance(r[k], (float, int)) and r[k] == r[k]]
        print(k, kind, round(st.median(v), 3), round(min(v), 3), round(max(v), 3))
