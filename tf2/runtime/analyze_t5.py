"""T5 analysis helpers. Segments a run into trials by the client-logged "hsd_tag" commands
(HSDDIAG CMD, client clock = the per-frame HSDDIAG C clock), and finds events by state
changes (take-off, landing, wall-run start/end) and by the first frame an input shows up
in the logged input axes / buttons, never by server TAG times.

Usage:
  python -I analyze_t5.py <run dir>                 summary of every trial
  python -I analyze_t5.py <run dir> <trial> [t0 t1] frame dump of one trial (relative times)
"""
import math
import statistics
import sys
from pathlib import Path


class F:
    __slots__ = ("t", "x", "y", "z", "vx", "vy", "vz", "pitch", "yaw", "g", "wr", "wh", "cr", "fwd", "side", "btn")

    def __init__(self, p):
        self.t, self.x, self.y, self.z, self.vx, self.vy, self.vz, self.pitch, self.yaw = map(float, p[2:11])
        self.g, self.wr, self.wh, self.cr = (p[i] == "1" for i in range(11, 15))
        self.fwd = float(p[15]) if len(p) > 15 else 0.0
        self.side = float(p[16]) if len(p) > 16 else 0.0
        self.btn = int(p[17]) if len(p) > 17 else 0

    @property
    def h(self):
        return math.hypot(self.vx, self.vy)

    @property
    def s3(self):
        return math.sqrt(self.vx ** 2 + self.vy ** 2 + self.vz ** 2)


def load(run):
    frames, cmds, other = [], [], []
    for line in (Path(run) / "diag.tsv").read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) < 2:
            continue
        if p[1] == "C" and len(p) >= 15:
            frames.append(F(p))
        elif p[1] == "CMD":
            cmds.append((float(p[2]), " ".join(p[3:])))
        else:
            other.append(p)
    return frames, cmds, other


def trials(frames, cmds):
    """{name: (t0, t1, frames, cmds)} split at the client time of each 'hsd_tag <name>' command."""
    marks = [(t, c.split()[1]) for t, c in cmds if c.startswith("hsd_tag ")]
    out = {}
    for i, (t0, name) in enumerate(marks):
        t1 = marks[i + 1][0] if i + 1 < len(marks) else 1e9
        if name == "-":
            continue
        out[name] = (t0, t1, [f for f in frames if t0 <= f.t < t1], [(t, c) for t, c in cmds if t0 <= t < t1])
    return out


def cmd_time(tcmds, text, n=0):
    hits = [t for t, c in tcmds if c == text]
    return hits[n] if len(hits) > n else None


def first(fr, pred, after=-1e9):
    for i, f in enumerate(fr):
        if f.t >= after and pred(f):
            return i
    return None


def rate(fr, i0, i1, key):
    """least-squares slope of key over frames i0..i1"""
    xs = [fr[i].t for i in range(i0, i1 + 1)]
    ys = [getattr(fr[i], key) for i in range(i0, i1 + 1)]
    if len(xs) < 3:
        return float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else float("nan")


def dump(fr, t0, a=-1e9, b=1e9, every=1):
    print("   t      x        y        z       vx       vy       vz       h     g wr wh cr  fwd  side btn yaw")
    for i, f in enumerate(fr):
        rt = f.t - t0
        if a <= rt <= b and i % every == 0:
            print(f"{rt:7.4f} {f.x:8.1f} {f.y:8.1f} {f.z:8.2f} {f.vx:8.2f} {f.vy:8.2f} {f.vz:8.2f} {f.h:7.2f}  "
                  f"{int(f.g)}  {int(f.wr)}  {int(f.wh)}  {int(f.cr)} {f.fwd:5.2f} {f.side:5.2f} {f.btn:3d} {f.yaw:6.1f}")


def summary(name, t0, fr, tc):
    """state-change events of one trial"""
    print(f"== {name}: {len(fr)} frames")
    for t, c in tc:
        if not c.startswith("hsd_tag"):
            print(f"   cmd {t - t0:7.4f} {c}")
    prev = None
    for f in fr:
        st = (f.g, f.wr, f.wh, f.cr, f.fwd != 0, f.side != 0, f.btn)
        if prev is not None and st != prev:
            print(f"   {f.t - t0:7.4f} g{int(f.g)} wr{int(f.wr)} wh{int(f.wh)} cr{int(f.cr)} in({f.fwd:.2f},{f.side:.2f},{f.btn}) "
                  f"v=({f.vx:.1f},{f.vy:.1f},{f.vz:.1f}) h={f.h:.1f} z={f.z:.1f}")
        prev = st


def main():
    run = sys.argv[1]
    frames, cmds, other = load(run)
    tr = trials(frames, cmds)
    if len(sys.argv) > 2:
        t0, t1, fr, tc = tr[sys.argv[2]]
        a = float(sys.argv[3]) if len(sys.argv) > 3 else -1e9
        b = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
        every = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        summary(sys.argv[2], t0, fr, tc)
        dump(fr, t0, a, b, every)
        return
    dts = [b.t - a.t for a, b in zip(frames, frames[1:]) if b.t > a.t]
    print(f"{len(frames)} frames, median dt {statistics.median(dts) * 1000:.2f} ms; trials: {', '.join(tr)}")
    for p in other:
        if p[1] in ("INFO", "Q", "TR", "STIM", "WEAPON", "UNTIL"):
            print("  ", " ".join(p[1:]))
    for name, (t0, t1, fr, tc) in tr.items():
        summary(name, t0, fr, tc)


if __name__ == "__main__":
    main()
