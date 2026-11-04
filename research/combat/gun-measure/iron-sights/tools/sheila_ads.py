#!/usr/bin/env python3
"""Sheila (mobile) and Vantage's rifle held: aimed picture and attachments, if the game lets them be held by a script. Does not fire: firing the mounted Sheila closes the client (IP2).
  py -3 -I sheila_ads.py <run dir> gun ..."""
import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vmcal import *
from capture import Gun
run=sys.argv[1]
L=Link()
L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 1 ); SetConVarFloat( "cl_fovScale", 1.27 )')
for g in sys.argv[2:]:
    print(g, L.give(INFO[g]["id"]), flush=True)
    G=Gun(L,g,INFO[g],run)
    G.bg={}; G.dflt={}
    G.run_vm(give=False)
    print(G.meta.get("hip_st"), G.meta.get("ads_st"))
    L.sv('entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_WALK ); p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 90, 0> )')
    L.sleep(0.8)
    L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )',0.1); L.sleep(1.3)
    shot(L,os.path.join(run,g,"vm_ads_wall.png"))
    L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )',0.3)
    with open(os.path.join(run,g,"vm_only.json"),"w",encoding="utf-8",newline="\n") as f:
        json.dump(dict(hip=G.meta.get("hip"),ads=G.meta.get("ads"),hip_st=G.meta.get("hip_st"),ads_st=G.meta.get("ads_st")),f)
L.sv('entity p = GetPlayerArray()[0]; p.SnapEyeAngles( <0, 0, 0> )')
