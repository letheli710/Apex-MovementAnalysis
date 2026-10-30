"""N6 summary for night_grapple_match: per trial the horizontal speed at the fire command and
during the hook flight, the first pulled frame, |v| 0.5 / 1.0 s after it, the peak and the
heading change of the velocity (slingshot). Also prints the hsd_trace lines (lane check).

Usage: python -I night_match.py <run dir>
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_t5 import first, load, trials  # noqa: E402


def heading(f):
    return math.degrees(math.atan2(f.vy, f.vx))


def summary(run):
    fr_all, cmds, other = load(run)
    for p in other:
        if "TRACE" in " ".join(p):
            print(" ".join(p[1:]))
    print(f"{'trial':16} {'h_fire':>7} {'h_fly':>7} {'t_pull':>6} {'vz_att':>6} {'v+0.5':>6} {'v+1.0':>6} "
          f"{'vmax':>6} {'t_max':>5} {'hmax':>6} {'turn':>5} {'v_arr':>6} {'t_arr':>5} {'x_end':>7} {'y_end':>7}")
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        hits = [t for t, c in tc if c == "+offhand1"]
        if not hits or not fr:
            continue
        tf = hits[0]
        i0 = first(fr, lambda f: f.t >= tf)
        f0 = fr[i0]
        # hook flight: the next 0.12 s (well under every flight time here) shows the fire effect
        fly = [f for f in fr[i0:] if f.t <= tf + 0.12]
        h_fly = min(f.h for f in fly)
        # first pulled frame (floor starts): after 0.1 s the off-ground lift (50) raises vz by > 20
        ip = None
        for i in range(i0 + 1, len(fr)):
            a, b = fr[i - 1], fr[i]
            if b.t - tf < 0.1:
                continue
            if b.vz - a.vz > 20:
                ip = i
                break
        if ip is None:
            print(f"{name:16} {f0.h:7.1f} {h_fly:7.1f}  no pull")
            continue
        tp = fr[ip].t
        win = [f for f in fr[ip:] if f.t <= tp + 2.0]

        def at(dt):
            j = first(fr, lambda f: f.t >= tp + dt)
            return fr[j].s3 if j is not None else float("nan")

        fm = max(win, key=lambda f: f.s3)
        hm = max(f.h for f in win)
        hs = [heading(f) for f in win if f.h > 50]
        turn = 0.0
        for a, b in zip(hs, hs[1:]):
            d = (b - a + 180) % 360 - 180
            turn += d
        fe = win[-1]
        # arrival: the last frame before the speed collapses (> 40 % drop in one frame) at the wall
        arr = next((a for a, b in zip(win, win[1:]) if a.s3 > 150 and b.s3 < 0.6 * a.s3), None)
        v_arr, t_arr = (arr.s3, arr.t - tp) if arr else (float("nan"), float("nan"))
        print(f"{name:16} {f0.h:7.1f} {h_fly:7.1f} {tp - tf:6.3f} {fr[ip].vz:6.1f} {at(0.5):6.1f} {at(1.0):6.1f} "
              f"{fm.s3:6.1f} {fm.t - tp:5.2f} {hm:6.1f} {turn:5.0f} {v_arr:6.1f} {t_arr:5.2f} {fe.x:7.1f} {fe.y:7.1f}")


if __name__ == "__main__":
    summary(sys.argv[1])
