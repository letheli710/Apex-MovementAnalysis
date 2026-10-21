#!/usr/bin/env python3
"""Find long, flat, obstacle-free test lanes on the loaded map (dedi script traces over AgentLink).

1. floor grid: for every (x, y) on the grid, TraceLine straight down from z_top to z_bot with
   TRACE_MASK_PLAYERSOLID and record the floor height and surface normal z;
2. lanes: along +X at every grid y, the longest run of points whose floor stays within
   --flat-tol of the run's start height and whose normal z >= --min-nz;
3. clearance: for the best lanes, a TraceHull with the standing player hull (32x32x72, raised by
   --step) along the whole lane, plus the same hull shifted +/- --half-width sideways.

Output: JSON with the grid and the ranked lanes, so a trial origin/yaw can be chosen from data.
The game must be running with -devsdk (AgentLink); this only reads the world.

  py -3 map_scan.py --x0 -14000 --x1 -5000 --y0 -3000 --y1 4000 --step-xy 100 --z-top 2500 --z-bot 500 -o lanes.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agentlink import AgentLink, DEFAULT_GAME  # noqa: E402

ROW = r'''
string out = ""
for ( float x = %(x0)f; x <= %(x1)f; x += %(sxy)f )
{
	TraceResults tr = TraceLine( <x, %(y)f, %(zt)f>, <x, %(y)f, %(zb)f>, [], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER )
	if ( tr.fraction < 1.0 )
		out += format( "%%.0f %%.2f %%.3f;", x, tr.endPos.z, tr.surfaceNormal.z )
	else
		out += format( "%%.0f nan nan;", x )
}
AgentLink_Reply( out )
'''

HULL = r'''
vector a = <%(xa)f, %(y)f, %(z)f>
vector b = <%(xb)f, %(y)f, %(z)f>
TraceResults tr = TraceHull( a, b, <-16, -16, 0>, <16, 16, 72>, [], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER )
AgentLink_Reply( format( "%%.4f %%.1f", tr.fraction, tr.endPos.x ) )
'''


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--x0", type=float, required=True)
    ap.add_argument("--x1", type=float, required=True)
    ap.add_argument("--y0", type=float, required=True)
    ap.add_argument("--y1", type=float, required=True)
    ap.add_argument("--step-xy", type=float, default=100.0)
    ap.add_argument("--z-top", type=float, required=True)
    ap.add_argument("--z-bot", type=float, required=True)
    ap.add_argument("--flat-tol", type=float, default=1.0)
    ap.add_argument("--min-nz", type=float, default=0.999)
    ap.add_argument("--half-width", type=float, default=150.0)
    ap.add_argument("--step", type=float, default=4.0, help="hull lift above the floor (below stepHeight 22)")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)

    grid = {}
    with AgentLink("server", a.game, timeout=60) as s:
        y = a.y0
        while y <= a.y1:
            r = s.eval(ROW % dict(x0=a.x0, x1=a.x1, sxy=a.step_xy, y=y, zt=a.z_top, zb=a.z_bot))
            pts = []
            for cell in r.get("reply", "").split(";"):
                if cell.strip():
                    x, z, nz = cell.split()
                    pts.append((float(x), None if z == "nan" else float(z), None if nz == "nan" else float(nz)))
            grid[y] = pts
            y += a.step_xy

        lanes = []
        for y, pts in grid.items():
            i = 0
            while i < len(pts):
                x0, z0, n0 = pts[i]
                if z0 is None or n0 < a.min_nz:
                    i += 1
                    continue
                j = i
                while j + 1 < len(pts) and pts[j + 1][1] is not None and abs(pts[j + 1][1] - z0) <= a.flat_tol \
                        and pts[j + 1][2] >= a.min_nz:
                    j += 1
                lanes.append({"y": y, "x_start": x0, "x_end": pts[j][0], "length": pts[j][0] - x0, "z": z0})
                i = j + 1
        lanes.sort(key=lambda l: -l["length"])
        best = []
        for l in lanes[: a.top * 3]:
            clear = []
            for dy in (0.0, -a.half_width, a.half_width):
                r = s.eval(HULL % dict(xa=l["x_start"], xb=l["x_end"], y=l["y"] + dy, z=l["z"] + a.step))
                frac, endx = r.get("reply", "0 0").split()
                clear.append({"dy": dy, "fraction": float(frac), "end_x": float(endx)})
            l["clearance"] = clear
            l["clear_length"] = min(c["end_x"] for c in clear) - l["x_start"]
            best.append(l)
        best.sort(key=lambda l: -l["clear_length"])
    args = {k: v for k, v in vars(a).items() if k not in ("game", "out")}  # no local paths in the output
    out = {"args": args, "lanes": best[: a.top], "grid": {str(k): v for k, v in grid.items()}}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
    for l in best[: a.top]:
        print(f"y={l['y']:8.0f} x {l['x_start']:8.0f}..{l['x_end']:8.0f} len {l['length']:6.0f} z {l['z']:8.2f} "
              f"clear {l['clear_length']:6.0f}  " + " ".join(f"{c['dy']:+.0f}:{c['fraction']:.3f}" for c in l["clearance"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
