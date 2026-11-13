"""km_hover: Northstar hover / flight core height curves from the client per-frame player log (PC).
Per tag: start time = the +offhand2 / +ability 1 press, z and vz every 0.1 s, peak height and when, landing.
Also prints the KM head (headroom) lines. Usage: py -3 -I an_hover.py <run dir> [step]"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run  # noqa: E402

r = Run(sys.argv[1])
step = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
for k in r.KM:
    if k[0] == "head":
        print("head", " ".join(k[1:]))
for a, b, tag in r.tags:
    if not (tag.startswith("hv_") or tag.startswith("fc_")):
        continue
    key = "+ability" if tag.startswith("fc_") else "+offhand2"
    press = next((t for t, c in r.cmds if a <= t < b and c.startswith(key)), None)
    if press is None:
        continue
    pcs = [p for p in r.PC if press - 0.2 <= p[0] < b]
    z0 = next(p for p in pcs if p[0] >= press)[4]
    peak = max(pcs, key=lambda p: p[4])
    land = next((p for p in pcs if p[0] > peak[0] and p[4] <= z0 + 2), None)
    print("\n== %s press %.3f z0 %.1f peak %.1f (+%.1f u) at +%.3f s; back on the floor at %s" % (
        tag, press, z0, peak[4], peak[4] - z0, peak[0] - press, "+%.3f s" % (land[0] - press) if land else "-"))
    print("   t      z-z0    vz     hspeed")
    nxt = 0.0
    for p in pcs:
        t = p[0] - press
        if t + 1e-6 >= nxt:
            print("  %5.2f  %6.1f  %6.1f  %6.1f" % (t, p[4] - z0, p[7], (p[5] ** 2 + p[6] ** 2) ** 0.5))
            nxt += step
