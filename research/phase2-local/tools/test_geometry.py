#!/usr/bin/env python3
"""Spawn, measure and remove test geometry (walls, ledges) on the loaded map over the dedi AgentLink.

The firing range field (m2/map) is flat and has no vertical walls next to it, so climb, wall-jump
and mantle experiments place props the way the Flowstate map editor does
(s21-platform/scripts/vscripts/mapeditor/_mapeditor.nut:428-433: CreatePropDynamic with
SOLID_VPHYSICS, then AllowMantle). Props carry the script name 'hsd_test_geo' so they can be
removed again. `measure` profiles a prop with horizontal traces (face position per height).

  py -3 test_geometry.py spawn --model mdl/rocks/rock_white_chalk_modular_wallrun_02.rmdl --origin -13600 6500 294.92 --yaw 0
  py -3 test_geometry.py measure --x0 -13900 --x1 -13300 --y 6500 --z0 300 --z1 700 --dz 20
  py -3 test_geometry.py clear
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agentlink import AgentLink, DEFAULT_GAME  # noqa: E402

# M3 test wall: face at x ~ -13706 (normal -X), y ~ 6380..6620, top ~ 232 u above the field floor.
M3_WALL_MODEL = "mdl/rocks/rock_white_chalk_modular_wallrun_02.rmdl"
M3_WALL_ORIGIN = (-13600.0, 6500.0, 294.92)

SPAWN = r'''
string out = ""
try
{
	asset m = $"%(model)s"
	// The script PrecacheModel refuses new models after level init (and an uncaught server script
	// error shuts the host game down, as happened in M3); MapEdit_PrecacheModel is the SDK's late
	// precache (s21-r5sdk/src/game/server/mapedit_paks.cpp:257-293).
	bool pre = ModelIsPrecached( m ) || MapEdit_PrecacheModel( m )
	out = "precached=" + pre
	if ( pre )
	{
		entity prop = CreatePropDynamic( m, <%(x)f, %(y)f, %(z)f>, <0, %(yaw)f, 0>, SOLID_VPHYSICS, -1.0 )
		if ( IsValid( prop ) )
		{
			prop.SetScriptName( "hsd_test_geo" )
			prop.AllowMantle()
			out += " prop=" + prop.GetEntIndex() + " mins=" + prop.GetBoundingMins() + " maxs=" + prop.GetBoundingMaxs()
		}
		else
			out += " prop=invalid"
	}
}
catch ( err )
{
	out += " error=" + string( err )
}
AgentLink_Reply( out )
'''

CLEAR = r'''
int n = 0
try
{
	foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo" ) )
	{
		e.Destroy()
		n++
	}
}
catch ( err ) { }
AgentLink_Reply( "removed=" + n )
'''

MEASURE = r'''
string out = ""
for ( float z = %(z0)f; z <= %(z1)f; z += %(dz)f )
{
	TraceResults tr = TraceLine( <%(x0)f, %(y)f, z>, <%(x1)f, %(y)f, z>, [], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER )
	out += format( "%%.0f %%.4f %%.1f %%.3f;", z, tr.fraction, tr.endPos.x, tr.surfaceNormal.x )
}
AgentLink_Reply( out )
'''


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=DEFAULT_GAME)
    sub = ap.add_subparsers(dest="op", required=True)
    sp = sub.add_parser("spawn")
    sp.add_argument("--model", required=True)
    sp.add_argument("--origin", type=float, nargs=3, required=True)
    sp.add_argument("--yaw", type=float, default=0.0)
    sub.add_parser("clear")
    me = sub.add_parser("measure")
    for k in ("x0", "x1", "y", "z0", "z1", "dz"):
        me.add_argument("--" + k, type=float, required=True)
    a = ap.parse_args(argv)
    with AgentLink("server", a.game, timeout=60) as s:
        if a.op == "spawn":
            x, y, z = a.origin
            r = s.eval(SPAWN % dict(model=a.model, x=x, y=y, z=z, yaw=a.yaw), check=False)
        elif a.op == "clear":
            r = s.eval(CLEAR, check=False)
        else:
            r = s.eval(MEASURE % vars(a), check=False)
            rows = [c.split() for c in r.get("reply", "").split(";") if c.strip()]
            r["profile"] = [{"z": float(z), "fraction": float(f), "hit_x": float(hx), "normal_x": float(nx)} for z, f, hx, nx in rows]
    print(json.dumps({k: r.get(k) for k in ("ok", "reply", "message", "profile") if r.get(k) is not None}, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
