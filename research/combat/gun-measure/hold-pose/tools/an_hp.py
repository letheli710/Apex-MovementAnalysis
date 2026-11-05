#!/usr/bin/env python3
"""Hold pose: per gun and state the settled pose against standing, the swing and its period, one cycle of the waveform, and the transitions.
  py -3 -I an_hp.py <runs dir> <out dir>
Positions are in the camera's frame (F, R, U), muzzle and sight centre. Gun pitch and yaw come from the muzzle attachment's own angles against the camera, and from the line sight centre to muzzle where the gun has one.
Writes HP-POSE.tsv, HP-SWING.tsv, HP-WAVE.tsv, HP-TRANSITION.tsv, HP-SEQ.tsv."""
import glob, math, os, re, statistics as st, sys
from collections import defaultdict

RX = re.compile(r"\[RT\] h t=([\d.]+) spd=(\S+) vz=(\S+) gr=(\d) duck=(\d) spr=(\d) sl=(\d) m=(\S+?),(\S+?),(\S+) s=(\S+?),(\S+?),(\S+) ma=(\S+?),(\S+?),(\S+) ca=(\S+?),(\S+?),(\S+) c=\S+ sq=(\S*) zf=(\S+)")
RK = re.compile(r"\[RT\] key ([+-]\w+) t=([\d.]+)")
AX = ("mF", "mR", "mU", "sF", "sR", "sU", "gP", "gY", "gR", "lP", "lY")
PHASES = 32


def ang(a):
    return (a + 180) % 360 - 180


def load(p):
    F, K = [], []
    for l in open(p, encoding="utf-8", errors="replace"):
        g = RX.search(l)
        if g:
            v = g.groups()
            n = lambda i: float(v[i])
            r = dict(t=n(0), spd=n(1), vz=n(2), gr=int(v[3]), duck=int(v[4]), spr=int(v[5]), sl=int(v[6]), mF=n(7), mR=n(8), mU=n(9), sF=n(10), sR=n(11), sU=n(12), seq=v[19].rsplit("/", 1)[-1].replace(".rseq", ""), zf=n(20))
            # gun angles against the camera; the roll of the attachment is its own axis convention, kept as a difference from standing
            r["gP"] = ang(n(13) - n(16)); r["gY"] = ang(n(14) - n(17)); r["gR"] = ang(n(15) - n(18))
            dF, dR, dU = r["mF"] - r["sF"], r["mR"] - r["sR"], r["mU"] - r["sU"]
            has = abs(r["sF"]) + abs(r["sR"]) + abs(r["sU"]) > 0
            r["lP"] = math.degrees(math.atan2(dU, math.hypot(dF, dR))) if has else float("nan")
            r["lY"] = math.degrees(math.atan2(dR, dF)) if has else float("nan")
            F.append(r)
            continue
        k = RK.search(l)
        if k: K.append((k[1], float(k[2])))
    return F, K


def key(K, name, n=0):
    v = [t for k, t in K if k == name]
    return v[n] if len(v) > n else None


def window(state, F, K):
    """The settled stretch of each state. Returns the frames, or an empty list."""
    pick = lambda a, b, c=lambda r: True: [r for r in F if a <= r["t"] <= b and c(r)] if a is not None and b is not None else []
    if state == "stand":
        return pick(F[0]["t"] + 0.5, F[-1]["t"] - 0.2)
    if state == "walk":
        return pick((key(K, "+forward") or 0) + 1.0, key(K, "-forward"), lambda r: r["spd"] > 170)
    if state == "sprint":
        return pick((key(K, "+speed") or 0) + 1.2, key(K, "-speed"), lambda r: r["spr"] and r["spd"] > 255)
    if state == "crouch":
        return pick((key(K, "+duck") or 0) + 1.2, key(K, "-duck"), lambda r: r["duck"])
    if state == "crouchwalk":
        return pick((key(K, "+forward") or 0) + 1.2, key(K, "-forward"), lambda r: r["duck"] and r["spd"] > 75)
    if state in ("slide", "slidehold"):
        w = [r for r in F if r["sl"] and r["gr"]]
        return [r for r in w if r["t"] >= w[0]["t"] + 0.5] if w else []
    if state in ("jump", "drop"):
        return [r for r in F if not r["gr"]]
    return []


def fundamental(t, x):
    """The strongest period between 0.15 and 1.5 s, by a Fourier scan on the frames. Returns period, amplitude, and the fit's share of the variance."""
    if len(t) > 300:
        k = len(t) // 300 + 1
        t, x = t[::k], x[::k]
    m = st.mean(x); y = [a - m for a in x]; v = sum(a * a for a in y) or 1e-12
    dur = t[-1] - t[0]
    if dur < 0.3: return (None, 0, 0)
    def at(p):
        w = 2 * math.pi / p
        c = sum(a * math.cos(w * b) for a, b in zip(y, t)); s = sum(a * math.sin(w * b) for a, b in zip(y, t))
        return 2 * math.hypot(c, s) / len(y)
    best = (0, None)
    p = 0.15
    while p < min(1.5, dur):
        best = max(best, (at(p), p), key=lambda z: z[0]); p *= 1.02
    if best[1] is None: return (None, 0, 0)
    c0 = best[1]
    for i in range(-10, 11):
        q = c0 * (1 + i * 0.002)
        best = max(best, (at(q), q), key=lambda z: z[0])
    return (best[1], best[0], (best[0] * best[0] * len(y) / 2) / v)


def transition(F, axis_keys, t0, base, target, span):
    """Time from a key to 90 % of the change in muzzle position, and the normalised curve in 20 steps."""
    w = [r for r in F if t0 <= r["t"] <= t0 + span]
    if len(w) < 5: return None
    tot = math.dist(base, target)
    if tot < 0.3: return dict(total=tot, t50=float("nan"), t90=float("nan"), curve="")
    pr = []
    for r in w:
        q = [r[k] for k in axis_keys]
        pr.append((r["t"] - t0, sum((a - b) * (c - b) for a, b, c in zip(q, base, target)) / (tot * tot)))
    t50 = next((a for a, b in pr if b >= 0.5), float("nan"))
    t90 = next((a for a, b in pr if b >= 0.9), float("nan"))
    cu = []
    for i in range(21):
        ta = i / 20 * span
        cu.append(f"{min(pr, key=lambda x: abs(x[0] - ta))[1]:.2f}")
    return dict(total=tot, t50=t50, t90=t90, curve=",".join(cu))


def main():
    runs, out = sys.argv[1:3]
    D = defaultdict(lambda: defaultdict(list))
    for p in sorted(glob.glob(os.path.join(runs, "hp_*.txt"))):
        g = re.match(r"hp_(\w+?)_(stand|walk|sprint|crouchwalk|crouch|slidehold|slide|jump|drop)_(\d)$", os.path.basename(p)[:-4])
        if g: D[g[1]][g[2]].append(load(p))
    P, SW, WV, TR, SQ, ST = [], [], [], [], [], []
    for gun, S in D.items():
        base = {}
        for F, K in S.get("stand", []):
            w = window("stand", F, K)
            for a in AX:
                vals = [r[a] for r in w if r[a] == r[a]]
                if vals: base.setdefault(a, []).append(st.mean(vals))
        base = {a: st.mean(v) for a, v in base.items()}
        for state, runs_ in S.items():
            per = []
            for i, (F, K) in enumerate(runs_):
                w = window(state, F, K)
                if len(w) < 20: continue
                per.append(({a: st.mean(r[a] for r in w if r[a] == r[a]) for a in AX if any(r[a] == r[a] for r in w)}, w))
            row = dict(gun=gun, state=state, runs=len(runs_), good=len(per))
            if per:
                row["secs"] = st.mean(x[1][-1]["t"] - x[1][0]["t"] for x in per)
                for a in AX:
                    v = [x[0][a] for x in per if a in x[0]]
                    if not v: continue
                    row[a] = st.mean(v)
                    row["d" + a] = st.mean(v) - base.get(a, float("nan"))
                row["repeat"] = max((math.dist([per[0][0][a] for a in AX[:3]], [x[0][a] for a in AX[:3]]) for x in per), default=0)
            P.append(row)
            if state in ("walk", "sprint", "crouchwalk", "slide", "slidehold", "stand", "crouch"):
                for a in ("mF", "mR", "mU", "gP", "gY", "gR"):
                    fit = []
                    for _, w in per:
                        t = [r["t"] for r in w]; x = [r[a] for r in w]
                        pe, amp, share = fundamental(t, x)
                        fit.append(dict(period=pe, amp=amp, share=share, half=(max(x) - min(x)) / 2))
                    if fit:
                        SW.append(dict(gun=gun, state=state, axis=a, half_range=st.mean(f["half"] for f in fit), amp=st.mean(f["amp"] for f in fit), period=st.mean(f["period"] for f in fit if f["period"]) if any(f["period"] for f in fit) else "", share=st.mean(f["share"] for f in fit), runs=len(fit), period_spread=(max(f["period"] or 0 for f in fit) - min(f["period"] or 0 for f in fit))))
                # waveform: fold on the right-left period, zero phase where the muzzle crosses its mean going right
                if state in ("walk", "sprint", "crouchwalk") and per:
                    t = [r["t"] for r in per[0][1]]
                    if fundamental(t, [r["mR"] for r in per[0][1]])[0]:
                        for rn, (_, w) in enumerate(per):
                            tt = [r["t"] for r in w]; mu = st.mean(r["mR"] for r in w)
                            pf = fundamental(tt, [r["mR"] for r in w])[0]  # each run its own: the fold must not drift
                            t0 = next((tt[i] for i in range(1, len(w)) if w[i - 1]["mR"] < mu <= w[i]["mR"]), tt[0])
                            bins = defaultdict(lambda: defaultdict(list))
                            for r in w:
                                b = int(((r["t"] - t0) / pf % 1) * PHASES)
                                for a in AX[:3] + AX[6:9]: bins[b][a].append(r[a])
                            for b in sorted(bins):
                                WV.append(dict(gun=gun, state=state, run=rn + 1, period=pf, phase=b / PHASES, **{a: st.mean(bins[b][a]) - st.mean(r[a] for r in w) for a in AX[:3] + AX[6:9]}))
            # when the state's own animations start and how long they run, from the key
            for F, K in runs_:
                seqs = []
                for r in F:
                    if not seqs or seqs[-1][0] != r["seq"]: seqs.append([r["seq"], r["t"], r["t"]])
                    seqs[-1][2] = r["t"]
                k0 = key(K, "+speed") if state in ("sprint", "slide", "slidehold") else key(K, "+duck")
                k1 = key(K, "-speed") if state == "sprint" else key(K, "+duck")
                for q, b0, b1 in seqs:
                    if q == "ads_out": continue
                    ST.append(dict(gun=gun, state=state, seq=q, start_after_key=round(b0 - k0, 3) if k0 else "", start_after_release=round(b0 - k1, 3) if k1 else "", length=round(b1 - b0, 3)))
            # the sequence list of the first run
            if runs_:
                F, K = runs_[0]
                seqs = []
                for r in F:
                    if not seqs or seqs[-1][0] != r["seq"]: seqs.append([r["seq"], r["t"], r["t"]])
                    seqs[-1][2] = r["t"]
                SQ.append(dict(gun=gun, state=state, seqs=" ".join(f"{a}:{c - b:.2f}" for a, b, c in seqs)))
        # transitions: pose target from the same run's settled window
        mk = ("mF", "mR", "mU")
        spec = [("stand_to_sprint", "sprint", "+speed", None, 1.5), ("sprint_to_stand", "sprint", "-speed", "stand", 1.5), ("stand_to_walk", "walk", "+forward", None, 1.0), ("walk_to_stand", "walk", "-forward", "stand", 1.0), ("duck_down", "crouch", "+duck", None, 1.0), ("duck_up", "crouch", "-duck", "stand", 1.0), ("sprint_to_slide", "slidehold", "+duck", None, 1.0), ("slide_to_stand", "slidehold", "-duck", "stand", 1.5)]
        for name, state, ks, tgt, span, mk in [x + (("mF", "mR", "mU"),) for x in spec] + [(x[0] + "_angle",) + x[1:] + (("gP", "gY", "gR"),) for x in spec]:
            res = []
            for F, K in S.get(state, []):
                w = window(state, F, K); t0 = key(K, ks)
                if len(w) < 20 or t0 is None: continue
                settled = [st.mean(r[a] for r in w) for a in mk]
                stand = [base.get(a, 0) for a in mk]
                if tgt == "stand":
                    b, c = settled, stand
                elif name.startswith("sprint_to_slide"):
                    # from the sprint pose of the same run, the frames just before the key
                    bw = [r for r in F if t0 - 0.2 <= r["t"] < t0]
                    if not bw: continue
                    b, c = [st.mean(r[a] for r in bw) for a in mk], settled
                else:
                    b, c = stand, settled
                x = transition(F, mk, t0, b, c, span)
                if x: res.append(x)
            if res:
                v = lambda k: [x[k] for x in res if x[k] == x[k]]
                TR.append(dict(gun=gun, name=name, runs=len(res), dist=st.mean(v("total")), t50=st.mean(v("t50")) if v("t50") else "", t90=st.mean(v("t90")) if v("t90") else "", span=span, curve=res[0]["curve"]))
        # the air and the landing: how far the gun goes and how long until it settles
        mk = ("mF", "mR", "mU")
        for state in ("jump", "drop"):
            for F, K in S.get(state, []):
                air = [r for r in F if not r["gr"]]
                if not air: continue
                tl = air[-1]["t"]
                land = [r for r in F if tl < r["t"] <= tl + 1.5]
                if not land: continue
                dist = [math.dist([r[a] for a in mk], [base.get(a, 0) for a in mk]) for r in land]
                pk = max(dist)
                settle = next((land[i]["t"] - tl for i in range(len(land) - 1, -1, -1) if dist[i] > max(0.1 * pk, 0.1)), 0)
                TR.append(dict(gun=gun, name=state + "_land", runs=1, dist=pk, t50=land[dist.index(pk)]["t"] - tl, t90=settle, span=air[-1]["t"] - air[0]["t"], curve=f"fall_speed={air[-1]['vz']:.0f}"))
    PK = ["gun", "state", "runs", "good", "secs", "repeat"] + list(AX) + ["d" + a for a in AX]
    w = lambda n, rows, keys: _write(os.path.join(out, n), rows, keys)
    w("HP-POSE.tsv", P, PK)
    w("HP-SWING.tsv", SW, ["gun", "state", "axis", "half_range", "amp", "period", "period_spread", "share", "runs"])
    w("HP-WAVE.tsv", WV, ["gun", "state", "run", "period", "phase", "mF", "mR", "mU", "gP", "gY", "gR"])
    w("HP-TRANSITION.tsv", TR, ["gun", "name", "runs", "dist", "t50", "t90", "span", "curve"])
    w("HP-SEQ.tsv", SQ, ["gun", "state", "seqs"])
    w("HP-SEQ-TIMES.tsv", ST, ["gun", "state", "seq", "start_after_key", "start_after_release", "length"])


def _write(path, rows, keys):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in keys) + "\n")


if __name__ == "__main__":
    main()
