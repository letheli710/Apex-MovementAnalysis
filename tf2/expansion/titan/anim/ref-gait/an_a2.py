"""A2: which clip plays at each steady speed, from the body shape (independent of the latched playback rate).

Per steady segment, over the re-posed frames: fore-aft swing of each foot relative to the origin (max - min of the
forward offset), pelvis-proxy (exp_torso_base) height range, and cycle phase coverage. The walk clip covers
278.9 u per cycle, run 332.5 u; the foot's fore-aft swing is a fixed property of each clip.
Usage: py -3 -I an_a2.py <run> [prefix] ...
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import anim_updates, between, load, speed2d, tag_windows  # noqa: E402
from an_f6 import cycle_rate, steady  # noqa: E402


def shape(G, yaw):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    out = {}
    for tg in ("footL", "footR"):
        f = [(g[tg][0] - g["o"][0]) * cy + (g[tg][1] - g["o"][1]) * sy for g in G]
        out[tg] = max(f) - min(f)
    tz = [g["torso"][2] - g["o"][2] for g in G]
    out["pelvis_dz"] = max(tz) - min(tz)
    cyc = sorted(g["cyc"] for g in G)
    gaps = [b - a for a, b in zip(cyc, cyc[1:])] + [1 - cyc[-1] + cyc[0]]
    out["cover"] = 1 - max(gaps)
    return out


def main():
    for arg in sys.argv[1:]:
        run_name, _, pre = arg.partition(":")
        run = load(run_name)
        for name, t0, t1 in tag_windows(run):
            if name.startswith("stop") or name.startswith("spawn") or not name.startswith(pre):
                continue
            C = between(run["C"], t0, t1)
            st = steady(C)
            if len(st) < 100:
                continue
            a, b = st[0]["t"] + 0.6, st[-1]["t"]
            G = anim_updates(between(run["GC"], a, b))
            v = sum(speed2d(r["v"]) for r in st) / len(st)
            s = shape(G, st[0]["yaw"])
            cr = cycle_rate(between(run["GC"], a, b))[0]
            clip = "run" if s["footL"] > 148 else "walk"
            print("%-22s v %5.1f  foot fwd swing L %5.1f R %5.1f  pelvis dz %4.1f  cycle covered %3.0f%%  cyc/s %.3f -> %s (rate %.3f)" % (
                run["dir"].name[9:15] + " " + name, v, s["footL"], s["footR"], s["pelvis_dz"], 100 * s["cover"], cr, clip,
                cr * (1.067 if clip == "run" else 1.133)))


if __name__ == "__main__":
    main()
