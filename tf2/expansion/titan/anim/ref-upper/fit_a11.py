"""A11: fit measured HAND_L distance-from-rest (RC lines) to the 3P reload gesture's own HAND_L path
(clip_attach.py): clip time = k * (t - t_off), amplitude free. Usage: py -3 -I fit_a11.py <run dir>"""
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_ref import parse, fl, tag_span  # noqa: E402
from clip_attach import clip_path  # noqa: E402

SEQ = {"monarch": "mp_stand_gesture_xo16_vanguard", "tone": "mp_stand_gesture_40mm"}


def run(rundir):
    d, tags, ev = parse(rundir)
    rc = [(t, f) for t, f in d["RC"] if f[0] == "1" and len(f) >= 13]
    rows = []
    for cls, seq in SEQ.items():
        sp = tag_span(tags, "a11_%s_idle" % cls)
        if not sp:
            continue
        idle = [f for t, f in rc if sp[0] + 0.3 <= t < sp[1]]
        ref = [sum(fl(f[i]) for f in idle) / len(idle) for i in (10, 11, 12)]
        cp = clip_path(seq, "HAND_L")
        T = cp[-1][0]
        cd = [math.dist(c[1:], cp[0][1:]) for c in cp]

        def cdev(tc):
            if tc < 0 or tc > T:
                return 0.0
            i = tc * 30
            a = int(i)
            b = min(a + 1, len(cd) - 1)
            return cd[a] * (1 - (i - a)) + cd[b] * (i - a)

        for k in range(2):
            sp = tag_span(tags, "a11_%s_rl%d" % (cls, k))
            if not sp:
                continue
            seg = [(t, f) for t, f in rc if sp[0] <= t < sp[0] + 5.0]
            on = [t for t, f in seg if f[8] == "1"]
            if not on:
                continue
            r0, r1 = on[0], on[-1]
            m = [(t - r0, math.dist([fl(f[10]), fl(f[11]), fl(f[12])], ref)) for t, f in seg]
            back = next((t for t, v in m if t > r1 - r0 and v < 1.0), float("nan"))
            best = None
            for kk in [x / 100 for x in range(70, 241)]:
                for off in [x / 100 for x in range(-50, 51, 2)]:
                    xs = [(cdev(kk * (t - off)), v) for t, v in m if -0.3 <= t <= r1 - r0]
                    sxx = sum(a * a for a, _ in xs) or 1
                    amp = sum(a * b for a, b in xs) / sxx
                    err = sum((v - amp * c) ** 2 for c, v in xs) / len(xs)
                    if best is None or err < best[0]:
                        best = (err, kk, off, amp)
            err, kk, off, amp = best
            end_clip = kk * (r1 - r0 - off)
            rows.append(dict(cls=cls, trial=k, seq=seq, clip_s=round(T, 3), reload_s=round(r1 - r0, 3), k=kk, t_off=off,
                             rms_u=round(math.sqrt(err), 2), clip_s_at_reload_end=round(end_clip, 2),
                             clip_frac_at_end=round(end_clip / T, 3), dev_at_end_u=round(max(v for t, v in m if abs(t - (r1 - r0)) < 0.02), 1),
                             back_to_rest_after_end_s=round(back - (r1 - r0), 3)))
    return rows


if __name__ == "__main__":
    for r in run(sys.argv[1]):
        print(r)
