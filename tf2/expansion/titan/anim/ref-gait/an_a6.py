"""A6 / F7: what happens to the body when the titan stops. Usage: py -3 -I an_a6.py <run> [tag prefix]

For each "-forward" in a tagged segment:
  t_v0      first client frame with speed < 1 u/s (after the key release)
  t_seq     when the main sequence becomes the idle clip: the client cycle jumps and then advances at
            the idle rate 1 / 1.933 s = 0.517 /s
  D(t)      distance of the body from the idle pose: attachments (feet, pelvis proxy, chest, head)
            relative to the origin in the facing frame, root-sum-square over the five, against the mean
            of the last 0.8 s of the window
  settle    D < 1 u for good
The two candidate blends after t_seq: the walk sequence's own fade-out 0.55 s, or the idle
sequence's fade-in 0.2 s. Fit T of a linear fade D(t) = D(t_seq) * (1 - (t - t_seq) / T).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import TAGS, between, load, speed2d, tag_windows  # noqa: E402

IDLE_RATE = 1 / 1.933
MODEL_RMS = []


def rel(g, yaw):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    out = []
    for tg in TAGS:
        p = g[tg]
        dx, dy, dz = p[0] - g["o"][0], p[1] - g["o"][1], p[2] - g["o"][2]
        out.append((dx * cy + dy * sy, -dx * sy + dy * cy, dz))
    return out


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for pa, pb in zip(a, b) for x, y in zip(pa, pb)))


def seq_switch(G, t0):
    """first frame after t0 where the cycle jumps and the next 0.3 s advance at the idle rate"""
    for i in range(2, len(G) - 50):
        if G[i]["t"] < t0:
            continue
        a, b = G[i - 1]["cyc"], G[i]["cyc"]
        dt = G[i]["t"] - G[i - 1]["t"]
        prev = ((a - G[i - 2]["cyc"]) % 1.0) / max(G[i - 1]["t"] - G[i - 2]["t"], 1e-4)
        # deviation from continuing at the previous rate, wrapped to -0.5..0.5
        dev = ((b - a - prev * dt) + 0.5) % 1.0 - 0.5
        if abs(dev) > 0.01:
            j = i + 1
            while j < len(G) and G[j]["t"] < G[i]["t"] + 0.3:
                j += 1
            r = ((G[j]["cyc"] - G[i]["cyc"]) % 1.0) / (G[j]["t"] - G[i]["t"])
            if abs(r - IDLE_RATE) < 0.03:
                return G[i]["t"], a, b
    return None, None, None


def analyse(run, name, t_rel, t_end, out):
    C = between(run["C"], t_rel - 0.5, t_end)
    G = between(run["GC"], t_rel - 0.5, t_end)
    if len(G) < 100:
        return
    yaw = C[0]["yaw"]
    v_rel = speed2d(min(C, key=lambda c: abs(c["t"] - t_rel))["v"])
    t_v0 = next((c["t"] for c in C if c["t"] > t_rel and speed2d(c["v"]) < 1.0), None)
    t_seq, ca, cb = seq_switch(G, t_rel)
    idle = [rel(g, yaw) for g in G if g["t"] > t_end - 0.8]
    ref = [tuple(sum(p[k][j] for p in idle) / len(idle) for j in range(3)) for k in range(len(TAGS))]
    D = [(g["t"], dist(rel(g, yaw), ref)) for g in G]
    settle = None
    for t, d in reversed(D):
        if d >= 1.0:
            settle = t
            break
    fitT = None
    if t_seq:
        d0 = next(d for t, d in D if t >= t_seq)
        best = None
        for T in [x / 100 for x in range(5, 150)]:
            err = sum((d - max(0.0, d0 * (1 - (t - t_seq) / T))) ** 2 for t, d in D if t_seq <= t <= t_seq + 1.2)
            if best is None or err < best[0]:
                best = (err, T)
        fitT = best[1]
        half = next((t - t_seq for t, d in D if t >= t_seq and d <= d0 / 2), None)
        # candidate models of the old (walk/run) pose weight after the switch, D(t) = D0 * w(t)
        def ss(T):
            return lambda e: (lambda x: (3 - 2 * x) * x * x)(max(0.0, 1 - e / T))
        def lin(T):
            return lambda e: max(0.0, 1 - e / T)
        models = {"smooth0.20": ss(0.2), "smooth0.55": ss(0.55), "lin0.20": lin(0.2), "lin0.55": lin(0.55)}
        pts = [(t - t_seq, d / d0) for t, d in D if t_seq <= t <= t_seq + 0.8]
        rms = {k: math.sqrt(sum((d - m(e)) ** 2 for e, d in pts) / len(pts)) for k, m in models.items()}
        MODEL_RMS.append(rms)
    f = lambda x: "-" if x is None else "%.3f" % (x - t_rel)
    print("%-14s v_release %5.1f  v=0 at %s  seq->idle at %s (cycle %.3f->%.3f)  settle(D<1u) %s  D(seq) %.1f u  linear-fade T %s  half %s" % (
        name, v_rel, f(t_v0), f(t_seq), ca or 0, cb or 0, f(settle), next((d for t, d in D if t_seq and t >= t_seq), 0),
        "-" if fitT is None else "%.2f" % fitT, "-" if not t_seq or half is None else "%.3f" % half))
    if fitT is not None:
        print("%14s RMS of D/D0 vs model (0..0.8 s after the switch): %s" % ("", "  ".join("%s %.3f" % kv for kv in MODEL_RMS[-1].items())))
    out.append(dict(name=name, D=[(t - t_rel, d) for t, d in D], t_seq=None if t_seq is None else t_seq - t_rel,
                    t_v0=None if t_v0 is None else t_v0 - t_rel,
                    v=[(c["t"] - t_rel, speed2d(c["v"])) for c in C]))


def main():
    run = load(sys.argv[1])
    pre = sys.argv[2] if len(sys.argv) > 2 else ""
    out = []
    for name, t0, t1 in tag_windows(run):
        if not name.startswith(pre):
            continue
        t_rel = next((t for t, c in run["cmds"] if t0 <= t < t1 and c == "-forward"), None)
        if t_rel:
            analyse(run, name, t_rel, t1, out)
    if MODEL_RMS:
        print("mean RMS over %d stops: %s" % (len(MODEL_RMS), "  ".join("%s %.3f" % (k, sum(m[k] for m in MODEL_RMS) / len(MODEL_RMS)) for k in MODEL_RMS[0])))
    return out


if __name__ == "__main__":
    main()
