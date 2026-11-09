"""F20 helper: floor height map from HSDDIAG GH lines (hsd_gait_hmap) -> slopes, steps, flat lanes.
Usage: py -3 -I an_hmap.py <run name>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import run_dir  # noqa: E402
STEP = 48.0


def read(name):
    H = {}
    global STEP
    for line in (run_dir(name) / "diag.tsv").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) > 5 and p[1] == "GH" and p[2] != "done":
            y, x0, st = float(p[2]), float(p[3]), float(p[4])
            STEP = st
            for k, v in enumerate(p[5:]):
                if v != "-":
                    z, nz = v.split(":")
                    H[(x0 + k * st, y)] = (float(z), int(nz) / 1000.0)
    return H


if __name__ == "__main__":
    H = read(sys.argv[1])
    st = STEP; xs = [min(k[0] for k in H) + i * st for i in range(int((max(k[0] for k in H) - min(k[0] for k in H)) / st) + 1)]; ys = sorted({k[1] for k in H})
    print("points", len(H), "x", xs[0], xs[-1], "y", ys[0], ys[-1], "step", st)
    import math
    slopes = [(k, v) for k, v in H.items() if 0.6 < v[1] < 0.985]
    print("slope points (5-53 deg):", len(slopes))
    # contiguous slope patches: group by 2-cell neighbourhood
    seen, patches = set(), []
    for k, v in slopes:
        if k in seen: continue
        stack, patch = [k], []
        seen.add(k)
        while stack:
            c = stack.pop(); patch.append(c)
            for dx in (-st, 0, st):
                for dy in (-st, 0, st):
                    n = (c[0] + dx, c[1] + dy)
                    if n in H and n not in seen and 0.6 < H[n][1] < 0.985:
                        seen.add(n); stack.append(n)
        if len(patch) >= 4:
            zs = [H[c][0] for c in patch]; ang = [math.degrees(math.acos(H[c][1])) for c in patch]
            patches.append((len(patch), min(c[0] for c in patch), max(c[0] for c in patch), min(c[1] for c in patch), max(c[1] for c in patch), min(zs), max(zs), sum(ang) / len(ang)))
    for p in sorted(patches, reverse=True)[:15]:
        print("patch n%3d x %6.0f..%6.0f y %6.0f..%6.0f z %5.0f..%5.0f mean %.1f deg" % p)
    # steps: flat cells next to flat cells with a 12..80 u height difference, along x or y
    steps = []
    for (x, y), (z, nz) in H.items():
        if nz < 0.985: continue
        for dx, dy in ((st, 0), (0, st)):
            n = H.get((x + dx, y + dy))
            if n and n[1] >= 0.985 and 12 <= abs(n[0] - z) <= 80:
                steps.append((x, y, dx, dy, z, n[0]))
    print("step edges (12-80 u):", len(steps))
    for s_ in sorted(steps, key=lambda s_: (s_[1], s_[0]))[:80]: print("  step", s_)
    # flat long lanes along +x at z ~ ground: longest run of cells with |dz|<4 and nz>0.99
    best = []
    for y in ys:
        run = []
        for x in xs:
            c = H.get((x, y))
            if c and c[1] > 0.99 and (not run or abs(c[0] - H[run[-1]][0]) < 4):
                run.append((x, y))
            else:
                if len(run) > 25: best.append((len(run) * st, run[0], run[-1], H[run[0]][0]))
                run = [(x, y)] if c and c[1] > 0.99 else []
        if len(run) > 25: best.append((len(run) * st, run[0], run[-1], H[run[0]][0]))
    for b in sorted(best, reverse=True)[:10]:
        print("flat x-lane %.0f u from %s to %s z %.0f" % b)
