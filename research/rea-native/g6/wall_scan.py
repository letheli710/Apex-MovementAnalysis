#!/usr/bin/env python3
"""G-6: find a world-geometry wall (no entity) near the firing-range test lanes for a grapple pull into it.

Horizontal TraceLines at chest height (floor + 36 and + 70) from a grid of start points, in 16 directions, up to
--range u; reports hits whose surface is near vertical (|normal z| < 0.1) and whose hit entity is the world
(worldspawn). Read-only: dedi script traces over AgentLink; the game must be running.

  py -3 wall_scan.py --x0 -15400 --x1 -12000 --y0 5400 --y1 7400 --step 400 -o walls.json
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "phase2-local", "tools"))
from agentlink import AgentLink, DEFAULT_GAME  # noqa: E402

CODE = r'''
string out = ""
vector s = <%(x)f, %(y)f, %(z)f>
TraceResults d = TraceLine( s + <0, 0, 100>, s + <0, 0, -400>, [], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER )
float fz = d.fraction < 1.0 ? d.endPos.z : -99999.0
out += format( "F %%.2f;", fz )
for ( int i = 0; i < 16; i++ )
{
	float a = i * 22.5 * 3.14159265 / 180.0
	foreach ( float h in [ 36.0, 70.0 ] )
	{
		vector a0 = <s.x, s.y, fz + h>
		vector a1 = a0 + <cos( a ), sin( a ), 0> * %(r)f
		TraceResults tr = TraceLine( a0, a1, [], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER )
		if ( tr.fraction < 1.0 )
		{
			string cls = IsValid( tr.hitEnt ) ? tr.hitEnt.GetClassName() : "none"
			bool world = IsValid( tr.hitEnt ) && tr.hitEnt.IsWorld()
			out += format( "H %%d %%.0f %%.1f %%.1f %%.1f %%.3f %%.3f %%.3f %%s %%d;", i, h, tr.endPos.x, tr.endPos.y, tr.endPos.z,
				tr.surfaceNormal.x, tr.surfaceNormal.y, tr.surfaceNormal.z, cls, world ? 1 : 0 )
		}
	}
}
AgentLink_Reply( out )
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--x0", type=float, default=-15400)
    ap.add_argument("--x1", type=float, default=-12000)
    ap.add_argument("--y0", type=float, default=5400)
    ap.add_argument("--y1", type=float, default=7400)
    ap.add_argument("--z", type=float, default=300)
    ap.add_argument("--step", type=float, default=400)
    ap.add_argument("--range", type=float, default=1500)
    ap.add_argument("-o", "--out", default="walls.json")
    a = ap.parse_args()
    rows = []
    with AgentLink("server", a.game, timeout=30) as s:
        y = a.y0
        while y <= a.y1 + 1e-6:
            x = a.x0
            while x <= a.x1 + 1e-6:
                r = s.eval(CODE % {"x": x, "y": y, "z": a.z, "r": a.range})
                txt = r.get("reply", "")
                fz = None
                for tok in txt.split(";"):
                    t = tok.split()
                    if not t:
                        continue
                    if t[0] == "F":
                        fz = float(t[1])
                    elif t[0] == "H":
                        i, h = int(t[1]), float(t[2])
                        px, py, pz, nx, ny, nz = map(float, t[3:9])
                        rows.append({"sx": x, "sy": y, "floor": fz, "dir": i * 22.5, "h": h, "hit": [px, py, pz],
                                     "n": [nx, ny, nz], "cls": t[9], "world": int(t[10])})
                x += a.step
            y += a.step
    walls = [r for r in rows if abs(r["n"][2]) < 0.1]
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"args": vars(a), "hits": rows}, f, indent=1)
    print("%d hits, %d near-vertical; world: %d" % (len(rows), len(walls), sum(r["world"] for r in walls)))
    for r in sorted(walls, key=lambda r: (not r["world"], ((r["hit"][0] - r["sx"]) ** 2 + (r["hit"][1] - r["sy"]) ** 2)))[:40]:
        d = ((r["hit"][0] - r["sx"]) ** 2 + (r["hit"][1] - r["sy"]) ** 2) ** 0.5
        print("start %.0f %.0f floor %s dir %5.1f h %2.0f  hit %8.1f %8.1f %7.1f  n %6.3f %6.3f %6.3f  d %6.0f  %s w=%d"
              % (r["sx"], r["sy"], r["floor"], r["dir"], r["h"], *r["hit"], *r["n"], d, r["cls"], r["world"]))


if __name__ == "__main__":
    main()
