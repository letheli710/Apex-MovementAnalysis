"""F6 / A2: steady-speed segments -> foot period (every client frame), main-sequence cycle rate,
which clip it matches. Usage: py -3 -I an_f6.py <run name> [tag prefix]

Clip table (titan_medium_mp_core, ../out/seqgraph_medium.csv): cycle duration, ground speed.
Predicted cycle rate (cycles/s) at speed v for a clip = rate(v) / duration, rate = v / ground speed
clamped to [0.25, 10] (sprint <= 1.25)  -- the TITAN-ANIM-FEEL.md §1.2 rule.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import anim_updates, between, load, speed2d, tag_windows  # noqa: E402

CLIPS = {"walk": (1.133, 246.1, 10.0), "run": (1.067, 311.6, 10.0), "sprint": (0.833, 437.6, 1.25)}


def pred_rate(clip, v):
    dur, gs, mx = CLIPS[clip]
    return min(max(v / gs, 0.25), mx) / dur


def steady(rows, vtarget=None, tol=0.02):
    """longest run of C rows within tol of the segment's top speed"""
    sp = [speed2d(r["v"]) for r in rows]
    if not sp:
        return []
    top = vtarget or max(sp)
    best, cur = [], []
    for r, s in zip(rows, sp):
        if abs(s - top) <= tol * top:
            cur.append(r)
        else:
            best, cur = (cur if len(cur) > len(best) else best), []
    return cur if len(cur) > len(best) else best


def cycle_rate(G):
    """least squares slope of the unwrapped client cycle; also counts wraps / jumps"""
    t = [g["t"] for g in G if g["cyc"] is not None]
    c = [g["cyc"] for g in G if g["cyc"] is not None]
    if len(c) < 10:
        return None
    u, off = [c[0]], 0.0
    jumps = 0
    for a, b in zip(c, c[1:]):
        d = b - a
        if d < -0.5:
            off += 1.0
        elif d < -0.02 or d > 0.1:
            jumps += 1
        u.append(b + off)
    n = len(t)
    mt, mu = sum(t) / n, sum(u) / n
    k = sum((x - mt) * (y - mu) for x, y in zip(t, u)) / sum((x - mt) ** 2 for x in t)
    return k, jumps


def foot_period(G, yaw):
    """period of foot_L forward offset (relative to origin, along yaw): mean spacing of its maxima,
    plus autocorrelation estimate"""
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    t, f = [], []
    for g in G:
        if g["footL"] is None:
            continue
        dx, dy = g["footL"][0] - g["o"][0], g["footL"][1] - g["o"][1]
        t.append(g["t"])
        f.append(dx * cy + dy * sy)
    if len(t) < 50:
        return None
    # resample at 240 Hz
    dt = 1 / 240.0
    ts = [t[0] + i * dt for i in range(int((t[-1] - t[0]) / dt))]
    j, fs = 0, []
    for x in ts:
        while t[j + 1] < x:
            j += 1
        a = (x - t[j]) / (t[j + 1] - t[j])
        fs.append(f[j] + a * (f[j + 1] - f[j]))
    m = sum(fs) / len(fs)
    fs = [x - m for x in fs]
    best, bl = -1, None
    vals = {}
    for lag in range(int(0.5 / dt), min(int(2.6 / dt), len(fs) // 2)):
        r = sum(a * b for a, b in zip(fs, fs[lag:])) / (len(fs) - lag)
        vals[lag] = r
    # first strong peak
    lags = sorted(vals)
    for i in range(1, len(lags) - 1):
        L = lags[i]
        if vals[L] > vals[lags[i - 1]] and vals[L] >= vals[lags[i + 1]] and vals[L] > 0.3 * (sum(x * x for x in fs) / len(fs)):
            a, b, c = vals[lags[i - 1]], vals[L], vals[lags[i + 1]]
            dl = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) else 0
            bl = (L + dl) * dt
            break
    amp = max(fs) - min(fs)
    return bl, amp, ts[-1] - ts[0]


def plants(G, foot, vmax=25.0, hold=0.12):
    """onset times of the foot being planted: world horizontal foot speed < vmax u/s for >= hold s"""
    on, start, prev = [], None, None
    for g in G:
        p = g[foot]
        if prev is not None and p is not None:
            dt = g["t"] - prev[0]
            if dt > 0:
                v = math.hypot(p[0] - prev[1][0], p[1] - prev[1][1]) / dt
                if v < vmax:
                    if start is None:
                        start = prev[0]
                elif start is not None:
                    if prev[0] - start >= hold:
                        on.append((start, g["t"]))
                    start = None
        prev = (g["t"], p) if p is not None else prev
    return on


def plant_period(G):
    """mean interval between onsets of the same foot (both feet pooled), the stance length, and the
    phase of R onset after L onset as a fraction of the period"""
    res = {}
    for foot in ("footL", "footR"):
        on = plants(G, foot)
        res[foot] = on
    iv = [b[0] - a[0] for foot in res for a, b in zip(res[foot], res[foot][1:])]
    if not iv:
        return None
    per = sum(iv) / len(iv)
    stance = [e - s for foot in res for s, e in res[foot]]
    return per, len(iv), min(iv), max(iv), sum(stance) / len(stance), res


def main():
    run = load(sys.argv[1])
    pre = sys.argv[2] if len(sys.argv) > 2 else ""
    print("run", run["dir"].name)
    for name, t0, t1 in tag_windows(run):
        if not name.startswith(pre):
            continue
        C = between(run["C"], t0, t1)
        st = steady(C)
        if len(st) < 100:
            continue
        a, b = st[0]["t"] + 0.3, st[-1]["t"]
        G = between(run["GC"], a, b)
        S = between(run["GS"], a, b)
        v = sum(speed2d(r["v"]) for r in st) / len(st)
        cr = cycle_rate(G)
        fp = foot_period(G, st[0]["yaw"])
        preds = {k: pred_rate(k, v) for k in CLIPS}
        best = min(preds, key=lambda k: abs(preds[k] - cr[0])) if cr else "-"
        print("%-14s v %6.1f  steady %.2f s  cyc/s %.4f (jumps %d)  pred walk %.4f run %.4f sprint %.4f -> %s (%+.1f%%)" % (
            name, v, b - a, cr[0], cr[1], preds["walk"], preds["run"], preds["sprint"], best, 100 * (cr[0] / preds[best] - 1)))
        pp = plant_period(anim_updates(G))
        if pp:
            print("%14s plant period %.3f s (%d intervals, %.3f..%.3f) -> %.4f cyc/s, stride %.1f u, stance %.3f s (%.0f%% of period)" % (
                "", pp[0], pp[1], pp[2], pp[3], 1 / pp[0], v * pp[0], pp[4], 100 * pp[4] / pp[0]))
        if fp and fp[0]:
            print("%14s foot_L period %.3f s (%.3f cyc/s), fwd swing %.1f u, over %.2f s; stride %.1f u" % (
                "", fp[0], 1 / fp[0], fp[1], fp[2], v * fp[0]))
        if S:
            print("%14s server cyc/s %.4f" % ("", ((S[-1]["cyc"] - S[0]["cyc"]) % 1 + (int((S[-1]["t"] - S[0]["t"]) * (cr[0] if cr else 0)))) / (S[-1]["t"] - S[0]["t"])))


if __name__ == "__main__":
    main()
