"""Compact per-trial profiles for the overnight runs: |v|, v and z every 0.1 s after a command."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_t5 import first, load, trials  # noqa: E402


def profile(run, cmd="+offhand1", step=0.1, span=3.0, only=None):
    fr_all, cmds, _ = load(run)
    for name, (t0, t1, fr, tc) in trials(fr_all, cmds).items():
        if only and not name.startswith(only):
            continue
        hits = [t for t, c in tc if c == cmd]
        ref = hits[0] if hits else t0
        print(f"== {name} (t=0 at '{cmd if hits else 'tag'}')")
        k = 0.0
        while k <= span:
            i = first(fr, lambda f: f.t >= ref + k)
            if i is None:
                break
            f = fr[i]
            print(f"  {k:4.1f} |v|={f.s3:6.1f} h={f.h:6.1f} v=({f.vx:7.1f},{f.vy:7.1f},{f.vz:7.1f}) z={f.z:7.1f} "
                  f"x={f.x:7.1f} g{int(f.g)}{int(f.wr)} in({f.fwd:.0f},{f.side:.0f},{f.btn})")
            k = round(k + step, 3)


if __name__ == "__main__":
    a = sys.argv
    profile(a[1], a[2] if len(a) > 2 else "+offhand1", float(a[3]) if len(a) > 3 else 0.1,
            float(a[4]) if len(a) > 4 else 3.0, a[5] if len(a) > 5 else None)
