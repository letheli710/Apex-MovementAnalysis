"""Long flights from wp_e (mp_angel_city): deviation of each projectile from its launch line over time
(session tf2-weapons, 2026-11-08).

Usage: python -I analyze_sky.py <run dir> [--every N]
For each projectile first seen in a sky_* segment: launch speed and direction, then per server frame
t, distance along the launch line, sideways (right +) and vertical (up +) deviation from that line,
speed. A gravity-free straight flight stays at 0 / 0; SMR / Archer drift shows as sideways and
vertical wander; grenades show the parabola in "up".
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_wp import parse, projectiles, segments  # noqa: E402


def main():
    run = Path(sys.argv[1])
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 1
    ev = parse(run / "diag.tsv")
    _, segs = segments(ev)
    for name, t0, t1, st in segs:
        if not name.startswith("sky_"):
            continue
        off = (st - t0) if st is not None else 0.0
        for p in projectiles(ev, t0 + off, t1 + off):
            pts = p["path"]
            if len(pts) < 2:
                continue
            v = p["vel"]
            sp = math.sqrt(sum(c * c for c in v))
            if sp < 1:
                # bolts report no velocity on the first frame: use the first two positions
                a, b = pts[0], pts[1]
                v = tuple((b[i + 1] - a[i + 1]) / (b[0] - a[0]) for i in range(3))
                sp = math.sqrt(sum(c * c for c in v))
            f = tuple(c / sp for c in v)
            # right = f x up(0,0,1) normalised; up' = right x f
            r = (f[1], -f[0], 0.0)
            rn = math.hypot(r[0], r[1]) or 1.0
            r = (r[0] / rn, r[1] / rn, 0.0)
            u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
            o = pts[0][1:4]
            print("== %s %s %s launch |v| %.1f pitch %.2f yaw %.2f samples %d end %s" % (
                name, p["cls"], p["wcls"], sp, -math.degrees(math.asin(max(-1, min(1, f[2])))),
                math.degrees(math.atan2(f[1], f[0])), len(pts),
                "t+%.2f" % (p["end"][0] - pts[0][0]) if p["end"] else "-"))
            for i, q in enumerate(pts):
                if i % every:
                    continue
                d = (q[1] - o[0], q[2] - o[1], q[3] - o[2])
                along = sum(a * b for a, b in zip(d, f))
                side = sum(a * b for a, b in zip(d, r))
                up = sum(a * b for a, b in zip(d, u))
                spd = math.sqrt(q[4] ** 2 + q[5] ** 2 + q[6] ** 2)
                print("   t %.2f along %8.1f side %7.1f up %8.1f speed %7.1f z %7.1f%s" % (
                    q[0] - pts[0][0], along, side, up, spd, q[3], " planted" if q[7] == "1" else ""))


if __name__ == "__main__":
    main()
