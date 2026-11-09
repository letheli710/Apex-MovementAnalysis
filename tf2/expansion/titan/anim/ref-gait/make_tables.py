"""ref-titan-gait: summary tables for REF-GAIT-1109.md -> out/f6_segments.tsv.
Only statistics (no machine paths); the raw logs are in HSD-RawData. Usage: py -3 -I make_tables.py"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gaitlib import anim_updates, between, load, speed2d, tag_windows  # noqa: E402
from an_f6 import CLIPS, cycle_rate, plants, steady  # noqa: E402
from an_a2 import shape  # noqa: E402

RUNS = ["gait_smoke", "gait_a", "gait_b", "gait_c"]
SKIP = ("stop", "spawn", "step", "f6_sprint")


def f6_rows():
    rows = []
    for rn in RUNS:
        run = load(rn)
        for name, t0, t1 in tag_windows(run):
            if name.startswith(SKIP) or name == "sm_fs175":
                continue
            C = between(run["C"], t0, t1)
            vt = None
            if name.startswith("ab_"):
                vt = float(name[3:]) * 1.004
            st = steady(C, vtarget=vt)
            if len(st) < 100:
                continue
            a, b = st[0]["t"] + 0.6, st[-1]["t"]
            G = between(run["GC"], a, b)
            U = anim_updates(G)
            v = sum(speed2d(c["v"]) for c in st) / len(st)
            sh = shape(U, st[0]["yaw"])
            sprint = any(c == "+speed" for t, c in run["cmds"] if t0 <= t < t1)
            clip = "sprint" if sprint else ("run" if sh["footL"] > 148 else "walk")
            dur, gs, mx = CLIPS[clip]
            cr = cycle_rate(G)[0]
            rate = cr * dur
            target = min(max(v / gs, 0.25), mx)
            slide = []
            for foot in ("footL", "footR"):
                for s0, s1 in plants(U, foot, vmax=max(25.0, 0.3 * v)):
                    mid = [g for g in U if s0 + 0.03 <= g["t"] <= s1 - 0.03]
                    for g0, g1 in zip(mid, mid[1:]):
                        dt = g1["t"] - g0["t"]
                        if dt > 0.02:
                            slide.append(math.hypot(g1[foot][0] - g0[foot][0], g1[foot][1] - g0[foot][1]) / dt)
            rows.append(dict(run=run["dir"].name[:15], seg=name, v=v, clip=clip, steady_s=b - a, cyc_per_s=cr, period_s=1 / cr,
                             rate=rate, target=target, gap=target - rate, slide_pred=abs(v - rate * gs),
                             slide_meas=(sum(slide) / len(slide)) if slide else float("nan"),
                             foot_swing=sh["footL"], pelvis_bob=sh["pelvis_dz"]))
    return rows


def write(path, rows, keys):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join(("%.4f" % r[k]) if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n")


if __name__ == "__main__":
    rows = f6_rows()
    keys = ["run", "seg", "v", "clip", "steady_s", "cyc_per_s", "period_s", "rate", "target", "gap", "slide_pred", "slide_meas", "foot_swing", "pelvis_bob"]
    write(HERE / "out" / "f6_segments.tsv", rows, keys)
    for r in rows:
        print("%-16s %-9s v %5.1f %-6s period %.3f rate %.3f target %.3f gap %+.3f slide pred %.1f meas %.1f" % (
            r["run"], r["seg"], r["v"], r["clip"], r["period_s"], r["rate"], r["target"], r["gap"], r["slide_pred"], r["slide_meas"]))
