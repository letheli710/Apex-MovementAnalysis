"""N6: the release event of each pulled trial (first frame after the pull start where vz jumps
by > 100 in one frame): speed, horizontal speed and vz just before / after, distance to the
wall plane x = -962. Usage: python -I night_release.py <run dir>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_t5 import first, load, trials  # noqa: E402

WALL_X = -962.0


def main(run):
    fr_all, cmds, _ = load(run)
    print(f"{'trial':16} {'t_rel':>5} {'v_pre':>6} {'h_pre':>6} {'vz_pre':>6} {'h_post':>6} {'vz_post':>7} {'dvz':>6} {'dx_wall':>7} {'z':>6}")
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        hits = [t for t, c in tc if c == "+offhand1"]
        if not hits:
            continue
        tf = hits[0]
        ip = next((i for i in range(1, len(fr)) if fr[i].t - tf >= 0.1 and fr[i].vz - fr[i - 1].vz > 20), None)
        if ip is None:
            continue
        ir = next((i for i in range(ip + 5, len(fr)) if fr[i].vz - fr[i - 1].vz > 100), None)
        if ir is None:
            print(f"{name:16} no release kick")
            continue
        a, b = fr[ir - 1], fr[ir]
        print(f"{name:16} {a.t - fr[ip].t:5.2f} {a.s3:6.1f} {a.h:6.1f} {a.vz:6.1f} {b.h:6.1f} {b.vz:7.1f} {b.vz - a.vz:6.1f} "
              f"{a.x - WALL_X:7.1f} {a.z:6.1f}")


if __name__ == "__main__":
    main(sys.argv[1])
