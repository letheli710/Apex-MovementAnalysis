"""T-1 / T-7 analysis: knockback per trial, metrics as in R5 research #64.
- dv: largest single-frame velocity jump in the client log within 1.5 s after the shot / throw
  (the teleport at the trial start is before that window); vertical / horizontal parts of it.
- h_before / h_after: horizontal speed on the frame before and 0.15 s after the jump.
- peak: highest feet z in the 2 s after it, from the floor (z 1.03). mp_lf_stacks has a roof everywhere
  (feet cap ~503 at the spawn), so peak_calc = z + vz^2 / (2 * 600) from the frame after the jump is
  also given (gravity 600, no air drag: T5); compare both where the roof is not hit.
- dmg, force: from the server's HSDDIAG DMG lines in the trial (self-damage and |damage force|).
Prints a per-trial table and a per-case summary (mean ± sd over the repetitions).
Usage: python -I analyze_t1.py <run dir> [<run dir> ...]"""
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_t5 import load, trials  # noqa: E402

FLOOR = 1.03
TRIGGERS = ("+attack", "hsd_throw", "hsd_detonate", "hsd_blast")


def server_events(run):
    """(server tag marks, DMG rows) from diag.tsv"""
    tags, dmg = [], []
    for line in (Path(run) / "diag.tsv").read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) > 3 and p[1] == "TAG":
            tags.append((float(p[3]), p[2]))
        elif len(p) > 14 and p[1] == "DMG":
            fx, fy, fz = map(float, p[4:7])
            dmg.append((float(p[2]), float(p[3]), math.sqrt(fx * fx + fy * fy + fz * fz), p[14]))
    return tags, dmg


def dmg_by_trial(tags, dmg):
    out = defaultdict(list)
    for i, (t0, name) in enumerate(tags):
        t1 = tags[i + 1][0] if i + 1 < len(tags) else 1e9
        out[name] += [d for d in dmg if t0 <= d[0] < t1]
    return out


def metrics(fr, tc):
    trig = [t for t, c in tc if c.split()[0] in TRIGGERS]
    if not trig:
        return None
    t0 = trig[-1] if any(c == "hsd_detonate" for _, c in tc) else trig[0]
    win = [f for f in fr if t0 - 0.02 <= f.t <= t0 + 1.5]
    best, pair = 0.0, None
    for a, b in zip(win, win[1:]):
        dv = math.sqrt((b.vx - a.vx) ** 2 + (b.vy - a.vy) ** 2 + (b.vz - a.vz) ** 2)
        if dv > best:
            best, pair = dv, (a, b)
    if pair is None:
        return dict(dv=0.0, dvz=0.0, dvh=0.0, h_before=float("nan"), h_after=float("nan"), peak=0.0, peak_calc=0.0,
                    z_at=float("nan"))
    a, b = pair
    after = [f for f in fr if b.t <= f.t <= b.t + 0.15]
    peak = max(f.z for f in fr if b.t - 0.5 <= f.t <= b.t + 2.0) - FLOOR
    small = best < 30  # no real knockback: report the jump's own peak and no dv
    return dict(dv=0.0 if small else best, dvz=0.0 if small else b.vz - a.vz,
                dvh=0.0 if small else math.hypot(b.vx - a.vx, b.vy - a.vy),
                h_before=a.h, h_after=after[-1].h if after else b.h, peak=peak,
                peak_calc=(b.z - FLOOR) + max(b.vz, 0.0) ** 2 / 1200.0, z_at=a.z - FLOOR)


def case(name):
    return name.rsplit("_", 1)[0] if name.rsplit("_", 1)[-1].isdigit() else name


def main():
    rows = []
    for run in sys.argv[1:]:
        frames, cmds, _ = load(run)
        tags, dmg = server_events(run)
        dm = dmg_by_trial(tags, dmg)
        for name, (t0, t1, fr, tc) in trials(frames, cmds).items():
            m = metrics(fr, tc)
            if m is None:
                continue
            ds = dm.get(name, [])
            m.update(name=name, case=case(name), dmg=sum(d[1] for d in ds), force=max((d[2] for d in ds), default=0.0),
                     src=",".join(sorted({d[3] for d in ds})) or "-")
            rows.append(m)
    print(f"{'trial':28s} {'dv':>6s} {'dvz':>6s} {'dvh':>6s} {'h0':>6s} {'h1':>6s} {'peak':>6s} {'calc':>6s} {'z@':>5s} {'dmg':>5s} {'force':>6s} src")
    for r in rows:
        print(f"{r['name']:28s} {r['dv']:6.0f} {r['dvz']:6.0f} {r['dvh']:6.0f} {r['h_before']:6.0f} {r['h_after']:6.0f} "
              f"{r['peak']:6.1f} {r['peak_calc']:6.1f} {r['z_at']:5.0f} {r['dmg']:5.0f} {r['force']:6.0f} {r['src']}")
    print("\nper case: mean ± sd (n)")
    by = defaultdict(list)
    for r in rows:
        by[r["case"]].append(r)
    for c, rs in by.items():
        def ms(k):
            v = [r[k] for r in rs if not math.isnan(r[k])]
            if not v:
                return "  -"
            return f"{statistics.fmean(v):.0f}" + (f"±{statistics.stdev(v):.0f}" if len(v) > 1 and statistics.stdev(v) >= 1 else "")
        print(f"{c:24s} n={len(rs)}  dv {ms('dv')}  dvz {ms('dvz')}  dvh {ms('dvh')}  h {ms('h_before')}->{ms('h_after')}"
              f"  peak {ms('peak')} calc {ms('peak_calc')}  dmg {ms('dmg')}  force {ms('force')}")


if __name__ == "__main__":
    main()
