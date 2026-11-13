"""Smart-ammo lock progress per tag: press time (CMD +offhand0), first SA frame, time each integer lock count is
reached, the maximum, release (-offhand0), missiles seen (client, stitched) and damage events.
Usage: py -3 -I an_lock.py <run dir> <tag> ..."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run  # noqa: E402
from an_expand import stitch  # noqa: E402

r = Run(sys.argv[1])
for tag in sys.argv[2:]:
    if not r.tag(tag):
        continue
    a, b = r.tag(tag)
    press = next((t for t, c in r.cmds if a <= t < b and c == "+offhand0"), None)
    rel = next((t for t, c in r.cmds if a <= t < b and c == "-offhand0"), None)
    rows = [x for x in r.SA if a <= x[0] < b and x[1] == -1]
    per = {}
    for t, slot, w, ts in rows:
        for h, fr, ac in ts:
            per.setdefault(h, []).append((t, fr))
    print("== %s press %.3f release %.3f (held %.3f)" % (tag, press or -1, rel or -1, (rel or 0) - (press or 0)))
    for h, xs in per.items():
        first = xs[0][0] - press
        marks = []
        for n in range(1, 13):
            hit = next((t for t, fr in xs if fr >= n - 1e-3), None)
            if hit is not None:
                marks.append("%d@%.3f" % (n, hit - press))
        mx = max(fr for t, fr in xs)
        slope = None
        mid = [(t, fr) for t, fr in xs if 1.2 < fr < 2.8]
        if len(mid) > 4:
            slope = (mid[-1][1] - mid[0][1]) / (mid[-1][0] - mid[0][0])
        print("  target %s first SA +%.3f max %.3f rate %s locks/s  %s" % (h, first, mx, "%.2f" % slope if slope else "-", " ".join(marks)))
    hs = r.client_proj_in(a, b)
    tr = stitch(r, hs)
    starts = sorted(x[0][0] for x in tr)
    print("  missiles: %d; launch times after release: %s" % (len(tr), " ".join("%.3f" % (s - rel) for s in starts) if rel else "-"))
    for d in r.TD:
        if a + r.offset <= d[0] < b + r.offset:
            print("  TD %.3f %s %.0f src %d" % (d[0] - r.offset - (rel or a), d[1], d[2], d[3]))
