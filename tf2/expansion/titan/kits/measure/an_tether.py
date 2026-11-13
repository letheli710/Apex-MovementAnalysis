"""km_tether: the foe walks / runs away after the tether trap; per tag: tethered status, foe distance from its
start and horizontal speed every 0.1 s (server TF lines), break time. Usage: py -3 -I an_tether.py <run dir>"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run  # noqa: E402

r = Run(sys.argv[1])
for a, b, tag in r.tags:
    if not tag.startswith("tt_") or tag.endswith("_throw"):
        continue
    sa, sb = a + r.offset, b + r.offset
    th = r.tag(tag + "_throw")
    tf = [x for x in r.TF if sa - 0.05 <= x[0] < sb and x[1] == 0]
    if not tf:
        continue
    x0, y0 = tf[0][2], tf[0][3]
    print("\n== %s (throw at %s)" % (tag, "%.2f" % (th[0] + r.offset) if th else "-"))
    if th:
        pre = [x for x in r.TF if th[0] + r.offset <= x[0] < sa and x[1] == 0]
        on = next((x for x in pre if x[10] > 0), None)
        print("   tethered on before the walk order: %s" % ("+%.2f s after throw (dist %.0f)" % (on[0] - th[0] - r.offset, 0) if on else "no"))
    print("   t     dist   hspeed  tethered  move_slow")
    for x in tf[::3]:
        d = math.hypot(x[2] - x0, x[3] - y0)
        print("  %5.2f  %6.0f  %6.0f  %.3f  %.3f" % (x[0] - sa, d, math.hypot(x[5], x[6]), x[10], x[11]))
