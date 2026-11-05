#!/usr/bin/env python3
"""The aimed picture against a plain lit wall, no world clutter in the sight line. py -3 -I adswall.py <run dir> [guns]"""
import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vmcal import *
run=sys.argv[1]
guns=sys.argv[2:] or [g for g in INFO if g not in ("sheila","mounted_turret","vantage")]
L=Link()
L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 1 ); SetConVarFloat( "cl_fovScale", 1.27 )')
for g in guns:
    p=os.path.join(run,g,"vm_ads_wall.png")
    if os.path.exists(p): continue
    L.give(INFO[g]["id"])
    L.sv('entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_WALK ); p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 90, 0> )')
    L.sleep(0.8)
    L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )',0.1); L.sleep(1.3)
    os.makedirs(os.path.dirname(p),exist_ok=True)
    shot(L,p)
    r=L.cl('printt( "[RT] zf " + GetLocalClientPlayer().GetZoomFrac() + " fov " + GetLocalClientPlayer().GetFOV() )',0.1)
    L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )',0.3)
    print(g,r,flush=True)
L.sv('entity p = GetPlayerArray()[0]; p.SnapEyeAngles( <0, 0, 0> )')
