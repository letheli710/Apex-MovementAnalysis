"""T0 movement metrics per titan from a t0_move run (and back / side from an earlier run).

Usage: python -I analyze_move.py <t0_move run> [<run with valid back/side segments>]
Prints one row per titan:
  walk: top speed, time to top, accel below / above lowSpeed (piecewise slopes), stop decel and stop time
  sprint: top speed, ramp rate walk->sprint (u/s^2), time to top, stop decel
  dash: peak speed, time held at peak, speed 0.3 s after the dash, power used per dash (TT log),
        regen rate (power/s, TT log), dashes possible from 100
  cam: walk bob (camera z range), sprint camera drop and max roll, dash max roll
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_titan as A  # noqa: E402

TITANS = ["ronin", "northstar", "ion", "tone", "monarch", "scorch", "legion"]


def seg(segs, frames, tag):
    if tag not in segs:
        return []
    a, b = segs[tag]
    return [f for f in frames if a <= f["t"] < b]


def cmd_time(cmds, segs, tag, cmd):
    a, b = segs[tag]
    for t, c in cmds:
        if a <= t < b and c == cmd:
            return t
    return None


def slope(fr, lo, hi):
    """mean accel between the first frames at speed >= lo and >= hi"""
    tl = th = None
    for f in fr:
        s = A.hspeed(f)
        if tl is None and s >= lo:
            tl = (f["t"], s)
        if th is None and s >= hi:
            th = (f["t"], s)
            break
    if tl and th and th[0] > tl[0]:
        return (th[1] - tl[1]) / (th[0] - tl[0])
    return None


def stop(fr, t_release):
    """decel from release: speed at release and time to < 1 u/s"""
    after = [f for f in fr if f["t"] >= t_release]
    if not after:
        return None, None
    v0 = A.hspeed(after[0])
    for f in after:
        if A.hspeed(f) < 1.0:
            dt = f["t"] - after[0]["t"]
            return (v0 / dt if dt > 0 else None), dt
    return None, None


def walk_metrics(cmds, segs, frames, cams, cls):
    fr = seg(segs, frames, "walk_" + cls)
    if not fr:
        return {}
    top = max(A.hspeed(f) for f in fr)
    t0 = fr[0]["t"]
    t_top = next(f["t"] for f in fr if A.hspeed(f) >= top - 0.5) - t0
    rel = cmd_time(cmds, segs, "walk_" + cls, "-forward")
    dec, dt = stop(fr, rel)
    cm = [c for c in cams if t0 + 0.5 <= c["t"] < rel]
    bob = (max(c["dz"] for c in cm) - min(c["dz"] for c in cm)) if cm else None
    return dict(top=top, t_top=t_top, acc_lo=slope(fr, 5, 0.8 * top * 0.85), acc_hi=slope(fr, 0.9 * top, top - 0.5),
                dec=dec, t_stop=dt, bob=bob)


def sprint_metrics(cmds, segs, frames, cams, cls, walk_top):
    fr = seg(segs, frames, "sprint_" + cls)
    if not fr:
        return {}
    top = max(A.hspeed(f) for f in fr)
    t0 = fr[0]["t"]
    t_top = next(f["t"] for f in fr if A.hspeed(f) >= top - 0.5) - t0
    rel = cmd_time(cmds, segs, "sprint_" + cls, "-forward")
    dec, dt = stop(fr, rel)
    cm = [c for c in cams if t0 + 1.5 <= c["t"] < rel]
    return dict(top=top, t_top=t_top, ramp=slope(fr, walk_top + 5, top - 5), dec=dec, t_stop=dt,
                cam_dz=min(c["dz"] for c in cm) if cm else None, roll=max(abs(c["roll"]) for c in cm) if cm else None)


def dash_metrics(cmds, segs, frames, cams, tt, cls):
    tag = "dodge_" + cls
    fr = seg(segs, frames, tag)
    if not fr:
        return {}
    t_press = cmd_time(cmds, segs, tag, "+dodge")
    after = [f for f in fr if f["t"] >= t_press]
    peak = max(A.hspeed(f) for f in after)
    at_peak = [f["t"] for f in after if A.hspeed(f) >= peak - 1]
    held = at_peak[-1] - at_peak[0] if at_peak else None
    t_end = at_peak[-1] if at_peak else t_press
    v03 = next((A.hspeed(f) for f in after if f["t"] >= t_end + 0.3), None)
    a, b = segs[tag]
    cm = [c for c in cams if t_press <= c["t"] < t_press + 1.0]
    # dash power: server TT lines inside the dodge and regen segments
    pw = [x for x in tt if a <= x["t"] < b]
    used = (max(x["dodge"] for x in pw) - min(x["dodge"] for x in pw)) if pw else None
    regen = None
    if "regen_" + cls in segs:
        ra, rb = segs["dodgeside_" + cls][0], segs["regen_" + cls][1]
        rs = [x for x in tt if ra <= x["t"] < rb]
        lo = min(rs, key=lambda x: x["dodge"]) if rs else None
        if lo:
            rising = [x for x in rs if x["t"] > lo["t"] and x["dodge"] < 99.9]
            if len(rising) > 3:
                regen = (rising[-1]["dodge"] - rising[0]["dodge"]) / (rising[-1]["t"] - rising[0]["t"])
    side = seg(segs, frames, "dodgeside_" + cls)
    n_side = 0
    prev = 0
    for f in side:
        s = A.hspeed(f)
        if s >= peak - 1 and prev < peak - 1:
            n_side += 1
        prev = s
    return dict(peak=peak, held=held, v_after03=v03, used=used, regen=regen, dashes_of_3=n_side,
                roll=max(abs(c["roll"]) for c in cm) if cm else None, delay=(at_peak[0] - t_press) if at_peak else None)


def main(run, run_bs=None):
    cmds, frames, cams, tt, _ = A.load(run)
    segs = A.segments(cmds)
    bs = None
    if run_bs:
        c2, f2, _, _, _ = A.load(run_bs)
        bs = (A.segments(c2), f2)
    fmt = lambda v, p=1: "-" if v is None else ("%.*f" % (p, v))  # noqa: E731
    print("titan | walk top / t_top / acc<low / acc>low / stop decel / t_stop / bob | sprint top / ramp / t_top / stop decel / cam dz / roll"
          " | dash peak / held / v+0.3s / power used / regen / dashes(of 3 presses) / roll | back / side")
    for cls in TITANS:
        w = walk_metrics(cmds, segs, frames, cams, cls)
        s = sprint_metrics(cmds, segs, frames, cams, cls, w.get("top", 0))
        d = dash_metrics(cmds, segs, frames, cams, tt, cls)
        back = side = None
        if bs:
            fb = seg(bs[0], bs[1], "back_" + cls)
            fs = seg(bs[0], bs[1], "side_" + cls)
            back = max((A.hspeed(f) for f in fb), default=None)
            side = max((A.hspeed(f) for f in fs), default=None)
        print("%s | %s / %s / %s / %s / %s / %s / %s | %s / %s / %s / %s / %s / %s | %s / %s / %s / %s / %s / %s / %s | %s / %s" % (
            cls, fmt(w.get("top")), fmt(w.get("t_top"), 3), fmt(w.get("acc_lo"), 0), fmt(w.get("acc_hi"), 0), fmt(w.get("dec"), 0),
            fmt(w.get("t_stop"), 3), fmt(w.get("bob"), 2),
            fmt(s.get("top")), fmt(s.get("ramp"), 0), fmt(s.get("t_top"), 2), fmt(s.get("dec"), 0), fmt(s.get("cam_dz"), 1), fmt(s.get("roll"), 2),
            fmt(d.get("peak")), fmt(d.get("held"), 3), fmt(d.get("v_after03"), 0), fmt(d.get("used"), 1), fmt(d.get("regen"), 2),
            d.get("dashes_of_3"), fmt(d.get("roll"), 2), fmt(back), fmt(side)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
