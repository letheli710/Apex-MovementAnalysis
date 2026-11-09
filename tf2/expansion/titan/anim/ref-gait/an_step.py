"""F20 step: the 11 u platform on mp_lf_stacks (run gait_step). Usage: py -3 -I an_step.py [run]

The titan walks +y from (-620, -1950); the floor is z 1, the platform top z ~11.6 (its south edge from where the
origin rises). Per segment: how the origin climbs (one tick or spread), the pelvis proxy and head height over
the floor through the step, and each sole's height above the floor it is over during stance (first person: no
foot IK; third person: rendered body).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import anim_updates, between, load, speed2d, tag_windows  # noqa: E402
from an_f6 import plants  # noqa: E402

FLOOR, TOP = 1.0, 11.6


def main():
    run = load(sys.argv[1] if len(sys.argv) > 1 else "gait_step")
    for name, t0, t1 in tag_windows(run):
        if not name.startswith("st"):
            continue
        C = between(run["C"], t0, t1 + 0.3)
        if not C:
            continue
        # the origin's climb: first and last frame strictly between floor and top
        mid = [c for c in C if FLOOR + 0.3 < c["o"][2] < TOP - 0.3]
        up = next((c for c in C if c["o"][2] > FLOOR + 0.3), None)
        top = next((c for c in C if c["o"][2] > TOP - 0.3), None)
        edge_y = up["o"][1] if up else None
        climb = "%.3f s over %.1f u (%d frames between)" % (top["t"] - up["t"], top["o"][1] - up["o"][1], len(mid)) if up and top else "-"
        v = speed2d(C[len(C) // 3]["v"])
        G = anim_updates(between(run["GC"], t0, t1))
        def floor_at(y):
            return TOP if edge_y is not None and y >= edge_y else FLOOR
        # pelvis / head over the floor under the origin, before and after the edge
        def over(ts):
            p = [g["torso"][2] - floor_at(g["o"][1]) for g in ts]
            h = [g["head"][2] - floor_at(g["o"][1]) for g in ts]
            return (sum(p) / len(p), sum(h) / len(h)) if p else (float("nan"),) * 2
        before = [g for g in G if edge_y is not None and g["o"][1] < edge_y - 150]
        after = [g for g in G if edge_y is not None and g["o"][1] > edge_y + 80]
        pb, hb = over(before)
        pa, ha = over(after)
        # pelvis jump at the edge: max |dz| per second around the edge
        near = [g for g in G if edge_y is not None and abs(g["o"][1] - edge_y) < 100]
        rates = [abs((b["torso"][2] - a["torso"][2]) / (b["t"] - a["t"])) for a, b in zip(near, near[1:]) if b["t"] - a["t"] > 0.004]
        line = "%-12s v %5.1f edge y %s  origin climb %s | pelvis over floor %.1f -> %.1f  head %.1f -> %.1f  max pelvis dz/dt near edge %.0f u/s" % (
            name, v, "-" if edge_y is None else "%.0f" % edge_y, climb, pb, pa, hb, ha, max(rates) if rates else float("nan"))
        print(line)
        for foot in ("footL", "footR"):
            res = []
            for s0, s1 in plants(G, foot, vmax=max(25.0, 0.3 * v)):
                gs = [g for g in G if s0 + 0.03 <= g["t"] <= s1 - 0.03]
                if not gs:
                    continue
                y = sum(g[foot][1] for g in gs) / len(gs)
                z = sum(g[foot][2] for g in gs) / len(gs)
                res.append("y%.0f:%s%+.1f" % (y, "P" if edge_y is not None and y >= edge_y else "F", z - floor_at(y)))
            print("%14s %s stance (y, P=platform/F=floor, sole z - floor): %s" % ("", foot, " ".join(res)))


if __name__ == "__main__":
    main()
