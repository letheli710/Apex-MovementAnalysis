"""F6: check the native playback-rate rule (ref-titan-native, PR #111) against every steady segment.

Rule: target = clamp(v / ground_speed(current clip), 0.25, 10) (sprint <= 1.25); the stored rate is replaced by
the target only when |target - rate| > 0.15. Clip from the native selector: v <= 0.5 idle, sprint flag -> sprint,
v >= 0.45 * 250 -> run, else walk. The speed trace is the client C line sampled at each body re-pose (~20 Hz) or
every client frame (--every-frame). Start rate 1.0 (idle). Usage: py -3 -I an_f6sim.py <run> [prefix]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import anim_updates, between, load, speed2d, tag_windows  # noqa: E402
from an_f6 import CLIPS, cycle_rate, steady  # noqa: E402

DEADBAND = 0.15


def clip_for(v, sprint):
    if v <= 0.5:
        return None
    if sprint:
        return "sprint"
    return "run" if v >= 0.45 * 250 else "walk"


def simulate(C, sprint_from=None, every=False, times=None):
    rate, hist = 1.0, []
    for c in C:
        if times is not None and not every and c["t"] not in times:
            continue
        v = speed2d(c["v"])
        clip = clip_for(v, sprint_from is not None and c["t"] >= sprint_from)
        if clip is None:
            continue
        dur, gs, mx = CLIPS[clip]
        target = min(max(v / gs, 0.25), mx)
        if abs(target - rate) > DEADBAND:
            rate = target
        hist.append((c["t"], clip, rate, target))
    return hist


def main():
    run = load(sys.argv[1])
    pre = sys.argv[2] if len(sys.argv) > 2 else ""
    every = "--every-frame" in sys.argv
    print("run", run["dir"].name, "deadband", DEADBAND, "speed samples:", "every client frame" if every else "body re-pose times")
    rows = []
    for name, t0, t1 in tag_windows(run):
        if name.startswith("stop") or name.startswith("spawn") or not name.startswith(pre):
            continue
        C = between(run["C"], t0, t1)
        st = steady(C)
        if len(st) < 100:
            continue
        a, b = st[0]["t"] + 0.3, st[-1]["t"]
        G = between(run["GC"], a, b)
        cr = cycle_rate(G)[0]
        t_sp = next((t for t, c in run["cmds"] if t0 <= t < t1 and c == "+speed"), None)
        ups = {g["t"] for g in anim_updates(between(run["GC"], t0, t1))}
        # map re-pose times onto the nearest client C rows
        times = set()
        for t in sorted(ups):
            c = min(between(C, t - 0.004, t + 0.004) or [C[0]], key=lambda c: abs(c["t"] - t))
            times.add(c["t"])
        hist = [h for h in simulate(C, t_sp, every, times) if h[0] <= b]
        clip, rate, target = hist[-1][1], hist[-1][2], hist[-1][3]
        dur = CLIPS[clip][0]
        meas = cr * dur
        v = sum(speed2d(r["v"]) for r in st) / len(st)
        print("%-10s v %5.1f %-6s measured rate %.3f  target v/gs %.3f  gap %.3f  sim %.3f  sim-meas %+.3f" % (
            name, v, clip, meas, target, target - meas, rate, rate - meas))
        rows.append((name, v, clip, meas, target, rate))
    if rows:
        err = [abs(r[5] - r[3]) for r in rows]
        print("segments %d, |sim - measured| mean %.3f max %.3f; all gaps < %.2f: %s" % (
            len(rows), sum(err) / len(err), max(err), DEADBAND, all(r[4] - r[3] < DEADBAND + 0.01 for r in rows)))


if __name__ == "__main__":
    main()
