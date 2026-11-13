"""km_ion: projectiles caught by the Ion vortex and fired back. Per tag: the foe's shots (owner npc_titan), the
refired ones (owner player): count, launch speed, direction off the view line at release (deg), vertical
acceleration, damage events on the foe. Usage: py -3 -I an_ion.py <run dir>"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from km_tools import Run, basis, dot, norm  # noqa: E402
from an_proj import fit_az  # noqa: E402

r = Run(sys.argv[1])
names = [n for a, b, n in r.tags if n.startswith(("vx_", "vs_"))]
for tag in names:
    a, b = r.tag(tag)
    rel = next((t for t, c in r.cmds if a <= t < b and c == "-offhand1"), None)
    hs = r.server_proj_in(a, b)
    foe = [h for h in hs if r.ps_new[h][3] == "npc_titan"]
    back = [h for h in hs if r.ps_new[h][3] == "player"]
    pc = r.pc_at(rel) if rel else None
    print("\n== %s: foe shots %d, fired back %d, release at %.3f (client)" % (tag, len(foe), len(back), rel or -1))
    if pc:
        f, rt, up = basis(pc[8], pc[9])
        print("   view pitch %.1f yaw %.1f eye %.0f %.0f %.0f" % (pc[8], pc[9], pc[10], pc[11], pc[12]))
    for h in back:
        pts = r.ps[h]
        v = pts[0][4:7]
        sp = norm(v)
        line = "   h=%d %s first +%.2f s after release, speed %.0f, n=%d" % (h, r.ps_new[h][1], pts[0][0] - r.offset - (rel or 0), sp, len(pts))
        if pc and sp > 1:
            yaw_off = math.degrees(math.atan2(dot(v, rt), dot(v, f)))
            pit_off = math.degrees(math.atan2(dot(v, up), dot(v, f)))
            line += ", dir off view: right %+.2f deg up %+.2f deg" % (yaw_off, pit_off)
        mv = [p for p in pts if norm(p[4:7]) > 50]
        if len(mv) >= 3:
            line += ", vz' %.1f" % fit_az(mv)
        line += ", start %.0f %.0f %.0f" % pts[0][1:4]
        print(line)
    for d in r.TD:
        if a + r.offset <= d[0] < b + r.offset:
            print("   TD +%.3f %s %.1f src %d inf %s type %d" % (d[0] - r.offset - (rel or a), d[1], d[2], d[3], d[4], d[6]))
    kit = [k for k in r.KIT if a + r.offset <= float(k[0]) < b + r.offset]
    if kit:
        vp = max(int(k[23]) for k in kit)
        vb = max(int(k[22]) for k in kit)
        en = [int(k[3]) for k in kit]
        print("   vortex max absorbed bullets %d projectiles %d; energy %d -> min %d" % (vb, vp, en[0], min(en)))
