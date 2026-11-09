"""F20 helper: straight test lines on the brush height map (gait_scout, mp_homestead).
Slope lines: along +-x or +-y, >= 9 cells (576 u), every cell a slope 6..28 deg with the same sign of rise and
no jump > 24 u between cells. Stair runs: >= 3 rises of 8..40 u within 6 cells, flat in between.
Usage: py -3 -I an_lines.py <run> [cx cy radius]"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import an_hmap  # noqa: E402

H = an_hmap.read(sys.argv[1])
st = an_hmap.STEP
cx, cy, R = (float(a) for a in sys.argv[2:5]) if len(sys.argv) > 4 else (-2802, -213, 3500)
ang = lambda nz: math.degrees(math.acos(max(-1, min(1, nz))))
lines, stairs = [], []
for (x, y) in list(H):
    if math.hypot(x - cx, y - cy) > R:
        continue
    for dx, dy in ((st, 0), (-st, 0), (0, st), (0, -st)):
        if (x - dx, y - dy) in H and 6 <= ang(H[(x - dx, y - dy)][1]) <= 28 and H[(x, y)][0] - H[(x - dx, y - dy)][0] > 3:
            continue  # not the start of a line
        pts, k = [], 0
        while True:
            p = (x + k * dx, y + k * dy)
            if p not in H:
                break
            if pts:
                dz = H[p][0] - H[pts[-1]][0]
                if not (3 < dz < 24) or not (6 <= ang(H[p][1]) <= 28):
                    break
            pts.append(p)
            k += 1
        if len(pts) >= 9:
            z0, z1 = H[pts[0]][0], H[pts[-1]][0]
            run = (len(pts) - 1) * st
            lines.append((len(pts) * st, pts[0], (dx / st, dy / st), z0, z1, math.degrees(math.atan2(z1 - z0, run)),
                          max(ang(H[p][1]) for p in pts) - min(ang(H[p][1]) for p in pts)))
        # stairs: count rises 8..40 along this direction within the next 8 cells, flat elsewhere
        zs = [H.get((x + k * dx, y + k * dy), (None, 0)) for k in range(9)]
        if all(z[0] is not None for z in zs):
            d = [b[0] - a[0] for a, b in zip(zs, zs[1:])]
            rises = [r for r in d if 8 <= r <= 40]
            if len(rises) >= 3 and all(r > -2 for r in d) and all(z[1] > 0.98 for z in zs):
                stairs.append((len(rises), (x, y), (dx / st, dy / st), zs[0][0], zs[-1][0], [round(r) for r in d]))
lines.sort(reverse=True)
print("slope lines (len, start, dir, z0, z1, mean deg, deg spread), best per band:")
for lo, hi in ((6, 10), (10, 15), (15, 20), (20, 28)):
  for l in [l for l in lines if lo <= l[5] < hi][:6]:
    print("  %4.0f u from (%6.0f,%6.0f) dir %s z %5.0f->%5.0f  %.1f deg  spread %.1f" % (l[0], l[1][0], l[1][1], l[2], l[3], l[4], l[5], l[6]))
print("stair runs:")
for s in sorted(stairs, reverse=True)[:25]:
    print("  %d rises from (%6.0f,%6.0f) dir %s z %4.0f->%4.0f %s" % (s[0], s[1][0], s[1][1], s[2], s[3], s[4], s[5]))
