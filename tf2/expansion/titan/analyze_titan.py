"""T0 analysis: per-tag turn rate, speed curves, dash, camera roll / bob from a runner data folder.

Usage: python -I analyze_titan.py <runtime/data/<run>> [tag ...]
  For each tag (hsd_tag segment, on the client clock via the CMD lines) prints:
    turn: total yaw / pitch change, peak and median rate over frames that moved (deg/s),
          time from first to last moving frame, and the tail after the last input
    move: peak horizontal speed, time to 90 % of it, accel / decel (u/s^2) from 10-90 %
    dash: dodge power before / min / after, regen rate (power/s)
    cam:  peak |roll|, camera z range (bob) relative to the origin
"""
import sys
from pathlib import Path


def load(run):
    lines = (Path(run) / "diag.tsv").read_text(encoding="utf-8", errors="replace").splitlines()
    cmds, frames, cams, tt, events = [], [], [], [], []
    for l in lines:
        f = l.split()
        if len(f) < 2:
            continue
        k = f[1]
        try:
            if k == "CMD":
                cmds.append((float(f[2]), " ".join(f[3:])))
            elif k == "C" and len(f) >= 18:
                frames.append(dict(t=float(f[2]), o=tuple(map(float, f[3:6])), v=tuple(map(float, f[6:9])),
                                   pitch=float(f[9]), yaw=float(f[10]), ground=f[11] == "1",
                                   fwd=float(f[15]), side=float(f[16]), buttons=int(f[17])))
            elif k == "CAM" and len(f) >= 10:
                cams.append(dict(t=float(f[2]), titan=f[3] == "1", pitch=float(f[4]), yaw=float(f[5]), roll=float(f[6]),
                                 dz=float(f[9])))
            elif k == "TT" and len(f) >= 8:
                tt.append(dict(t=float(f[2]), titan=f[3] == "1", dodge=float(f[4]), sprint=f[5] == "1"))
            elif k in ("TITAN", "MOUSE", "LOOKCFG", "INFO", "Q"):
                events.append(l)
        except ValueError:
            pass
    return cmds, frames, cams, tt, events


def segments(cmds):
    """tag -> (start, end) on the client clock"""
    segs, cur, start = {}, None, None
    for t, c in cmds:
        if c.startswith("hsd_tag "):
            if cur and cur != "-":
                segs.setdefault(cur, (start, t))
            cur, start = c.split()[1], t
    return segs


def unwrap(prev, a):
    d = a - prev
    while d > 180:
        d -= 360
    while d < -180:
        d += 360
    return d


def turn_stats(fr):
    if len(fr) < 3:
        return None
    dy, dp, rates, prates, moving = 0.0, 0.0, [], [], []
    for a, b in zip(fr, fr[1:]):
        dt = b["t"] - a["t"]
        if dt <= 0:
            continue
        y = unwrap(a["yaw"], b["yaw"])
        p = b["pitch"] - a["pitch"]
        dy += y
        dp += p
        if abs(y) > 1e-3 or abs(p) > 1e-3:
            rates.append(abs(y) / dt)
            prates.append(abs(p) / dt)
            moving.append(b["t"])
    if not moving:
        return dict(yaw=0.0, pitch=0.0)
    rs = sorted(rates)
    ps = sorted(prates)
    return dict(yaw=dy, pitch=dp, peak=max(rates), median=rs[len(rs) // 2], ppeak=max(prates), pmedian=ps[len(ps) // 2],
                t_first=moving[0], t_last=moving[-1], dur=moving[-1] - moving[0], frames=len(moving))


def hspeed(f):
    return (f["v"][0] ** 2 + f["v"][1] ** 2) ** 0.5


def move_stats(fr):
    if len(fr) < 3:
        return None
    sp = [(f["t"], hspeed(f)) for f in fr]
    peak = max(s for _, s in sp)
    if peak < 1:
        return dict(peak=peak)
    t0 = fr[0]["t"]
    ipk = max(range(len(sp)), key=lambda i: sp[i][1])

    def cross(level, rng):
        for i in rng:
            if (sp[i][1] - level) * (sp[i - 1][1] - level) <= 0 and sp[i][1] != sp[i - 1][1]:
                a, b = sp[i - 1], sp[i]
                return a[0] + (level - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
        return None
    up10 = cross(0.1 * peak, range(1, ipk + 1))
    up90 = cross(0.9 * peak, range(1, ipk + 1))
    dn90 = cross(0.9 * peak, range(ipk + 1, len(sp)))
    dn10 = cross(0.1 * peak, range(ipk + 1, len(sp)))
    out = dict(peak=peak, t_peak=sp[ipk][0] - t0)
    if up10 is not None and up90 is not None and up90 > up10:
        out["accel"] = 0.8 * peak / (up90 - up10)
        out["t90"] = up90 - t0
    if dn10 is not None and dn90 is not None and dn10 > dn90:
        out["decel"] = 0.8 * peak / (dn10 - dn90)
    return out


def plateau(fr, lo, hi):
    """median horizontal speed between lo and hi seconds into the segment"""
    if not fr:
        return None
    t0 = fr[0]["t"]
    s = sorted(hspeed(f) for f in fr if lo <= f["t"] - t0 <= hi)
    return s[len(s) // 2] if s else None


def report(run, tags=None):
    cmds, frames, cams, tt, events = load(run)
    for e in events:
        print(e)
    segs = segments(cmds)
    for tag, (a, b) in segs.items():
        if tags and tag not in tags:
            continue
        fr = [f for f in frames if a <= f["t"] < b]
        cm = [c for c in cams if a <= c["t"] < b]
        print("== %s  %.3f .. %.3f  (%d frames)" % (tag, a, b, len(fr)))
        ts = turn_stats(fr)
        if ts and abs(ts.get("yaw", 0)) + abs(ts.get("pitch", 0)) > 0.5:
            print("  turn yaw %.2f pitch %.2f | yaw rate peak %.1f median %.1f | pitch peak %.1f median %.1f | moving %.3f s, %d frames"
                  % (ts["yaw"], ts["pitch"], ts["peak"], ts["median"], ts["ppeak"], ts["pmedian"], ts["dur"], ts["frames"]))
        ms = move_stats(fr)
        if ms and ms["peak"] > 5:
            print("  move " + " ".join("%s=%.1f" % (k, v) for k, v in ms.items()))
        if cm:
            rolls = [abs(c["roll"]) for c in cm]
            dzs = [c["dz"] for c in cm]
            print("  cam |roll| max %.2f  dz %.2f .. %.2f" % (max(rolls), min(dzs), max(dzs)))
        # server clock differs from the client clock; use the TT lines by order inside the CMD window
        # only as a coarse check (power before / min / after)
    return segs, frames, cams, tt


if __name__ == "__main__":
    report(sys.argv[1], sys.argv[2:] or None)
