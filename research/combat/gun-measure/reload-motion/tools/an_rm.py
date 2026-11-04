#!/usr/bin/env python3
"""Reload motion. Per gun and type: a timed table about every 1/60 s, speed peaks of gun, hands and magazine point, ammo and unlock moments. Time 0 is the first reload frame.
  py -3 -I an_rm.py <runs dir> <out dir>
Writes tables/<gun>_<kind>.tsv, RM-SUMMARY.tsv, RM-PEAKS.tsv, RM-SEGMENTS.tsv, RM-MAG.tsv."""
import csv, glob, math, os, re, statistics as st, sys
from collections import defaultdict
import numpy as np

RX = re.compile(r"\[RT\] r t=([\d.]+) clip=(-?\d+) rel=(\d) m=(\S+?),(\S+?),(\S+) g=(\S+?),(\S+?),(\S+) l=(\S+?),(\S+?),(\S+) h=(\S+?),(\S+?),(\S+) q=(\S+?),(\S+?),(\S+) ca=(\S+?),(\S+?),(\S+) sq=(\S+)")
ang = lambda a: (a + 180) % 360 - 180


def load(p):
    F = []
    for l in open(p, encoding="utf-8", errors="replace"):
        g = RX.search(l)
        if g:
            v = g.groups(); n = lambda i: float(v[i])
            F.append(dict(t=n(0), clip=int(v[1]), rel=int(v[2]), m=(n(3), n(4), n(5)), g=(ang(n(6) - n(18)), ang(n(7) - n(19)), ang(n(8) - n(20))), l=(n(9), n(10), n(11)), h=(n(12), n(13), n(14)), sq=v[21].rsplit("/", 1)[-1].replace(".rseq", "")))
    F.sort(key=lambda r: r["t"])
    # the client clock can repeat a frame: keep increasing times
    out = []
    for r in F:
        if not out or r["t"] > out[-1]["t"]: out.append(r)
    return out


def scan_mag(path):
    """From the attachment scan: which attachments move against the gun's muzzle most, leaving out hands. Returns list of (index, peak distance change, time series)."""
    T = []
    cur = None
    for l in open(path, encoding="utf-8", errors="replace"):
        if l.startswith("[RT] s t="):
            g = re.match(r"\[RT\] s t=([\d.]+) clip=(-?\d+)", l)
            cur = dict(t=float(g[1]), clip=int(g[2]), p={}); T.append(cur)
        if cur is not None and l.startswith("[RT] s"):
            for i, x, y, z in re.findall(r" (\d+):(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)", l):
                cur["p"][int(i)] = (float(x), float(y), float(z))
    n = st.mode([len(t["p"]) for t in T]) if T else 0  # the first scan can catch the view model before the swap
    T = [t for t in T if len(t["p"]) == n and n >= 30]
    if len(T) < 5: return [], T
    ids = sorted(T[0]["p"])
    return ids, T


def resample(fr, key, dt=1 / 60):
    t = np.array([r["t"] for r in fr]); a = np.array([r[key] for r in fr], float)
    tt = np.arange(t[0], t[-1], dt)
    return tt, np.stack([np.interp(tt, t, a[:, i]) for i in range(a.shape[1])], axis=1)


def speed(tt, a, win=5):
    """Speed, smoothed over a short window to take frame noise out."""
    d = np.linalg.norm(np.diff(a, axis=0), axis=1) / np.diff(tt)
    k = np.ones(win) / win
    return np.convolve(np.r_[d, d[-1]], k, "same")


def peaks(tt, s, floor, gap=0.12):
    """Local speed maxima above floor, apart by at least gap. Returns list of time, speed, width at half."""
    out = []
    idx = [i for i in range(1, len(s) - 1) if s[i] >= s[i - 1] and s[i] > s[i + 1] and s[i] > floor]
    idx.sort(key=lambda i: -s[i])
    keep = []
    for i in idx:
        if all(abs(tt[i] - tt[j]) >= gap for j in keep): keep.append(i)
    for i in sorted(keep):
        a = i
        while a > 0 and s[a] > s[i] / 2: a -= 1
        b = i
        while b < len(s) - 1 and s[b] > s[i] / 2: b += 1
        out.append((float(tt[i]), float(s[i]), float(tt[b] - tt[a])))
    return out


def main():
    runs, out = sys.argv[1:3]
    os.makedirs(os.path.join(out, "tables"), exist_ok=True)
    G = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(runs, "rm_*.txt"))):
        g = re.match(r"rm_(\w+?)_(tac|emp)_(\d)$", os.path.basename(p)[:-4])
        if g and g[3] != "0": G[g[1], g[2]].append(load(p))
    SUM, PK, SEG = [], [], []
    for (gun, kind), runs_ in sorted(G.items()):
        rowsets = []
        for rn, F in enumerate(runs_):
            # reload start: the sequence first leaves the idle one after the key; here the first frame whose sequence starts with reload
            # (Sentinel's has another name, so: the first frame that leaves the idle sequence, the sequence the log opens with)
            idx = next((i for i, r in enumerate(F) if r["sq"] != F[0]["sq"]), None)
            # Sentinel never leaves it in this log: fall back to the script's reload flag, which ends at the unlock
            if idx is None:
                idx = next((i for i, r in enumerate(F) if r["rel"]), None)
                if idx is None: continue
                end = max(i for i, r in enumerate(F) if r["rel"])
            else:
                end = max(i for i, r in enumerate(F) if r["sq"] != F[0]["sq"])
            t0 = F[idx]["t"]
            W = F[idx:end + 1]
            pre = F[max(0, idx - 30):idx]
            if len(W) < 20: continue
            rises = [(y["t"] - t0, y["clip"] - x["clip"]) for x, y in zip(F[idx:], F[idx + 1:]) if y["clip"] > x["clip"]]
            off = next((F[i]["t"] - t0 for i in range(idx + 1, len(F)) if F[i - 1]["rel"] and not F[i]["rel"]), float("nan"))
            seqs = []
            for r in W:
                if not seqs or seqs[-1][0] != r["sq"]: seqs.append([r["sq"], r["t"] - t0, r["t"] - t0])
                seqs[-1][2] = r["t"] - t0
            rowsets.append(dict(F=W, t0=t0, rises=rises, off=off, seqs=seqs, dur=W[-1]["t"] - t0, base={k: np.mean([r[k] for r in pre], axis=0) for k in ("m", "g", "l", "h")} if pre else None))
        if not rowsets: SUM.append(dict(gun=gun, kind=kind, runs=len(runs_), good=0)); continue
        R = rowsets[0]
        # table from the first run
        tt, m = resample(R["F"], "m"); _, g = resample(R["F"], "g"); _, l = resample(R["F"], "l"); _, h = resample(R["F"], "h")
        sM, sL, sH = speed(tt, m), speed(tt, l), speed(tt, h)
        sA = speed(tt, g)
        clip = np.interp(tt, [r["t"] for r in R["F"]], [r["clip"] for r in R["F"]])
        seqname = [next((q for q, a, b in R["seqs"] if a <= x - R["t0"] <= b + 0.01), "") for x in tt]
        with open(os.path.join(out, "tables", f"{gun}_{kind}.tsv"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# R5 local hybrid, first of two runs. t from the first reload frame, s. u and degrees, camera frame. speeds in u/s and deg/s, smoothed over 5 steps.\nt\tfrac\tclip\tseq\tmF\tmR\tmU\tgP\tgY\tgR\tlF\tlR\tlU\thF\thR\thU\tspeedMuzzle\tspeedAngle\tspeedL\tspeedR\n")
            for i, x in enumerate(tt):
                f.write(f"{x - R['t0']:.3f}\t{(x - R['t0']) / R['dur']:.3f}\t{int(round(clip[i]))}\t{seqname[i]}\t" + "\t".join(f"{v:.3f}" for v in (*m[i], *g[i], *l[i], *h[i])) + f"\t{sM[i]:.1f}\t{sA[i]:.1f}\t{sL[i]:.1f}\t{sH[i]:.1f}\n")
        rep = []
        for name, s, floor in (("L", sL, 40), ("R", sH, 40), ("muzzle", sM, 40), ("angle", sA, 80)):
            for tp, sp, w in peaks(tt - R["t0"], s, floor):
                # same peak in the other runs
                PK.append(dict(gun=gun, kind=kind, track=name, t=tp, frac=tp / R["dur"], speed=sp, width=w))
        SUM.append(dict(gun=gun, kind=kind, runs=len(runs_), good=len(rowsets), dur=st.mean(x["dur"] for x in rowsets), ammo=st.mean(x["rises"][0][0] for x in rowsets if x["rises"]) if any(x["rises"] for x in rowsets) else "", nammo=len(R["rises"]), unlock=st.mean(x["off"] for x in rowsets if x["off"] == x["off"]) if any(x["off"] == x["off"] for x in rowsets) else "", maxL=float(sL.max()), maxR=float(sH.max()), maxM=float(sM.max()), meanL=float(sL.mean()), meanR=float(sH.mean()), meanM=float(sM.mean()), peakOverMeanL=float(sL.max() / sL.mean()) if sL.mean() else "", seqs=" ".join(f"{q}:{a:.2f}-{b:.2f}" for q, a, b in R["seqs"])))
    wr = lambda n, rows, keys: _w(os.path.join(out, n), rows, keys)
    wr("RM-SUMMARY.tsv", SUM, ["gun", "kind", "runs", "good", "dur", "ammo", "nammo", "unlock", "maxL", "maxR", "maxM", "meanL", "meanR", "meanM", "peakOverMeanL", "seqs"])
    wr("RM-PEAKS.tsv", PK, ["gun", "kind", "track", "t", "frac", "speed", "width"])
    # the magazine point from the scans
    M = []
    for p in sorted(glob.glob(os.path.join(runs, "scan", "*.txt"))):
        gun = os.path.basename(p)[:-4]
        ids, T = scan_mag(p)
        if not ids: M.append(dict(gun=gun, note="no scan")); continue
        rise = next((T[i]["t"] for i in range(1, len(T)) if T[i]["clip"] > T[i - 1]["clip"]), None)
        key = next((float(x.split("t=")[1]) for x in open(p, encoding="utf-8") if "[RT] key" in x), T[0]["t"])
        # muzzle: the attachment that is farthest forward among those at rest with the gun: distances to it barely change for the gun body
        mz = max(ids, key=lambda i: st.median(t["p"][i][0] for t in T) if st.median(t["p"][i][0] for t in T) < 120 else -1)
        moved = []
        for i in ids:
            d = [math.dist(t["p"][i], t["p"][mz]) for t in T]
            base = st.median(d[:3])
            dev = [abs(x - base) for x in d]
            moved.append((max(dev), i, d))
        moved.sort(reverse=True, key=lambda x: x[0])
        for dv, i, d in moved[:8]:
            if dv < 1.0: break
            b = st.median(d[:3])
            away = [t["t"] - key for t, x in zip(T, d) if abs(x - b) > 0.5 * dv]
            pos = [T[k]["p"][i] for k in range(len(T))]
            M.append(dict(gun=gun, index=i, moved=dv, away_from=min(away) if away else "", away_to=max(away) if away else "", ammo=rise - key if rise else "", atRest=f"{st.median(p[0] for p in pos):.1f},{st.median(p[1] for p in pos):.1f},{st.median(p[2] for p in pos):.1f}", note=""))
    wr("RM-MAG.tsv", M, ["gun", "index", "moved", "away_from", "away_to", "ammo", "atRest", "note"])


def _w(path, rows, keys):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in keys) + "\n")


if __name__ == "__main__":
    main()
