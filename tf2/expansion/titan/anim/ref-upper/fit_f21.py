"""F21: pilot camera vs a walking npc titan. Per titan footstep (a sole attachment comes down to the ground:
height < 8 u after being > 15 u), the pilot camera's largest vertical offset (camera - eye, RC field u) and
largest rotation in the 0.6 s after it, with the titan's distance. Usage: py -3 -I fit_f21.py <run dir>"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_ref import parse, fl  # noqa: E402


def run(rundir, t_end=66.0):
    d, tags, ev = parse(rundir)
    rc = [(t, [fl(x) for x in f[1:7]]) for t, f in d["RC"] if f[0] == "0" and t < t_end]
    rn = [(t, fl(f[0]), fl(f[4]), fl(f[5])) for t, f in d["RN"] if t < t_end]
    steps = []
    for k, side in ((2, "L"), (3, "R")):
        up = False
        for t, dist, *feet in rn:
            h = feet[k - 2]
            if h > 15:
                up = True
            elif up and h < 8:
                steps.append((t, side, dist))
                up = False
    steps.sort()
    rows = []
    for t0, side, dist in steps:
        win = [v for t, v in rc if t0 - 0.1 <= t <= t0 + 0.6]
        pre = [v for t, v in rc if t0 - 0.6 <= t < t0 - 0.1]
        if not win:
            continue
        pk = max(win, key=lambda v: abs(v[5]))
        t_pk = next(t for t, v in rc if t0 - 0.1 <= t <= t0 + 0.6 and v is pk)
        rows.append(dict(t=round(t0, 2), foot=side, dist=round(dist), cam_u_peak=round(pk[5], 3), at=round(t_pk - t0, 3),
                         cam_rot_max=round(max(max(abs(v[0]), abs(v[1]), abs(v[2])) for v in win), 3),
                         cam_fr_max=round(max(max(abs(v[3]), abs(v[4])) for v in win), 3),
                         before_u=round(max((abs(v[5]) for v in pre), default=0), 3)))
    return rows


if __name__ == "__main__":
    for r in run(sys.argv[1]):
        print(r)


def dips(rundir, t_end=66.0):
    """every local camera dip (u < -0.03, lowest within +-0.2 s): time, depth, titan distance then, and the
    rebound (highest u in the next 0.25 s) and settle time (|u| < 0.02)"""
    d, tags, ev = parse(rundir)
    rc = [(t, fl(f[6])) for t, f in d["RC"] if f[0] == "0" and t < t_end]
    rn = [(t, fl(f[0])) for t, f in d["RN"] if t < t_end]
    out = []
    for i, (t, u) in enumerate(rc):
        if u > -0.03:
            continue
        nb = [v for tt, v in rc if abs(tt - t) <= 0.2]
        if u > min(nb):
            continue
        dist = min(rn, key=lambda x: abs(x[0] - t))[1] if rn else float("nan")
        after = [(tt, v) for tt, v in rc if t < tt <= t + 0.5]
        reb = max((v for tt, v in after if tt <= t + 0.25), default=0)
        settle = next((tt - t for tt, v in after if tt > t + 0.15 and abs(v) < 0.02), float("nan"))
        out.append(dict(t=round(t, 3), dip_u=round(u, 3), dist=round(dist), rebound_u=round(reb, 3), settle_s=round(settle, 3)))
    return out


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "dips":
    for r in dips(sys.argv[1]):
        print(r)
