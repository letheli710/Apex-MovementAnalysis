"""T5 per-family metrics on top of analyze_t5 (trial segmentation by client-logged commands)."""
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_t5 import first, load, rate, trials


def ramp(fr, i0, lo, hi, rising=True):
    """slope of h over the frames after i0 while h is between lo and hi (accel or decel band)"""
    idx = []
    for i in range(i0, len(fr)):
        h = fr[i].h
        if lo <= h <= hi:
            idx.append(i)
        elif idx:
            break
    if len(idx) < 3:
        return float("nan"), 0
    return rate(fr, idx[0], idx[-1], "h"), len(idx)


def ground(run):
    fr_all, cmds, _ = load(run)
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        out = [name]
        # acceleration: first frame with input (fwd != 0), h between 20 and 0.9 * plateau
        i_in = first(fr, lambda f: f.fwd != 0)
        rel = [t for t, c in tc if c == "-forward"]
        if i_in is not None:
            i_rel = first(fr, lambda f: f.fwd == 0, after=fr[i_in].t)
            plate = statistics.median(f.h for f in fr[i_rel - 40:i_rel - 1])
            a, n = ramp(fr, i_in + 1, 20, plate * 0.9)
            d, m = ramp(fr, i_rel, 10, plate - 5)
            out.append(f"plateau {plate:.2f}  accel {a:.0f} ({n} fr)  release-decel {-d:.0f} ({m} fr)")
            # sprint: accel profile above walk speed
            if plate > 200:
                a2, n2 = ramp(fr, i_in + 1, 180, plate * 0.95)
                out.append(f"accel above walk {a2:.0f} ({n2} fr)")
        kick = [t for t, c in tc if c.startswith("hsd_kick")]
        if kick:
            ik = first(fr, lambda f: f.h > 250, after=kick[0])
            if ik is not None:
                d, m = ramp(fr, ik, 10, 290)
                out.append(f"kick h0 {fr[ik].h:.1f} no-input decel {-d:.0f} ({m} fr)")
        print("  ".join(out))


def v(f):
    return f"({f.vx:.1f},{f.vy:.1f},{f.vz:.1f}) h={f.h:.1f}"


def air(run):
    """lurch (side press after take-off), residual air accel, skip"""
    fr_all, cmds, _ = load(run)
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        if name.startswith("lurch"):
            jt = [t for t, c in tc if c == "+jump"][0]
            ia = first(fr, lambda f: not f.g, after=jt)
            il = first(fr, lambda f: f.g, after=fr[ia].t)
            ip = first(fr, lambda f: f.side != 0 and not f.g, after=fr[ia].t)
            line = f"{name}: take-off {v(fr[ia])}  landing-1 {v(fr[il - 1])}"
            if ip is not None:
                b, a = fr[ip - 1], fr[min(ip + 3, il - 1)]
                line += (f"  press at +{fr[ip].t - fr[ia].t:.3f}s: before {v(b)} after(+3fr) {v(a)}"
                         f"  dvx {a.vx - b.vx:+.1f} dvy {a.vy - b.vy:+.1f} dh {a.h - b.h:+.1f}")
            print(line)
        elif name.startswith("air_"):
            st = [t for t, c in tc if c.startswith("hsd_setup")][0]
            i0 = first(fr, lambda f: f.h > 20 and not f.g, after=st)
            il = first(fr, lambda f: f.g, after=fr[i0].t) if i0 is not None else None
            if il is None:
                print(f"{name}: no clean air segment")
                continue
            a, b = fr[i0 + 2], fr[il - 1]
            dt = b.t - a.t
            print(f"{name}: {v(a)} -> {v(b)} over {dt:.3f}s  dvx/dt {(b.vx - a.vx) / dt:.2f}  dvy/dt {(b.vy - a.vy) / dt:.2f}"
                  f"  |v3| {a.s3:.1f}->{b.s3:.1f}")
        elif name.startswith("skip") or name == "jump_stand":
            st = [t for t, c in tc if c.startswith("hsd_setup")][0]
            jt = [t for t, c in tc if c == "+jump"][0]
            if name == "jump_stand":
                ia = first(fr, lambda f: not f.g, after=jt)
                print(f"{name}: take-off {v(fr[ia])} next {v(fr[ia + 1])} dt {fr[ia + 1].t - fr[ia].t:.4f}")
                continue
            i_up = first(fr, lambda f: not f.g, after=st)  # the teleport into the air
            ig = first(fr, lambda f: f.g, after=fr[i_up].t)
            ia = first(fr, lambda f: not f.g, after=jt)
            vzmax = max(f.vz for f in fr[ia:ia + 5])
            print(f"{name}: pre-land {v(fr[ig - 1])} landed {v(fr[ig])}  last-ground {v(fr[ia - 1])}"
                  f"  take-off {v(fr[ia])} (+{fr[ia].t - fr[ig].t:.3f}s after landing)  vz first-air {fr[ia].vz:.1f} max {vzmax:.1f}")


def slide(run):
    fr_all, cmds, _ = load(run)
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        print(f"== {name}")
        for t, c in tc:
            if c in ("+duck", "+jump"):
                i = first(fr, lambda f: f.t >= t)
                pre = fr[i - 1]
                post = max(fr[i:i + 15], key=lambda f: f.h)
                print(f"  {c} at {t - t0:.3f}: before {v(pre)}  peak next 15fr {v(post)} (+{post.t - t:.3f}s)")
                if c == "+jump":
                    ia = first(fr, lambda f: not f.g, after=t)
                    print(f"     take-off {v(fr[ia])}  next {v(fr[ia + 1])}  vz max {max(f.vz for f in fr[ia:ia + 5]):.1f}")


def wall(run):
    fr_all, cmds, _ = load(run)
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        iw = first(fr, lambda f: f.wr)
        if iw is None:
            print(f"{name}: no wall-run")
            continue
        ie = first(fr, lambda f: not f.wr, after=fr[iw].t)
        dur = (fr[ie].t if ie else fr[-1].t) - fr[iw].t
        pre = fr[iw - 1]
        print(f"{name}: start +{fr[iw].t - t0:.3f}  pre {v(pre)}  first {v(fr[iw])}  next {v(fr[iw + 1])}  dur {dur:.3f}s"
              f"  end {v(fr[ie - 1]) if ie else ''}")


if __name__ == "__main__":
    globals()[sys.argv[1]](sys.argv[2])
