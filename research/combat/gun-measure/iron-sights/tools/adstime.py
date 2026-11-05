#!/usr/bin/env python3
"""When does the aimed gun settle? Log the muzzle every 0.1 s for 2.5 s after +zoom. py -3 -I adstime.py <out.tsv> gun ..."""
import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vmcal import *
out=sys.argv[1]
L=Link()
L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarFloat( "cl_fovScale", 1.27 )')
rows=["gun\tt\tzf\tF\tR\tU\tpitch"]
for g in sys.argv[2:]:
    L.give(INFO[g]["id"])
    L.sv('entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_WALK ); p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
    L.sleep(1.0)
    L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )',0.0)
    t0=time.time()
    while time.time()-t0<2.6:
        v=read(L)
        rows.append(f"{g}\t{time.time()-t0:.2f}\t{v[10]:.3f}\t{v[0]:.3f}\t{v[1]:.3f}\t{v[2]:.3f}\t{v[3]:.3f}")
    L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )',0.4)
    print(rows[-1],flush=True)
open(out,"w",newline="\n").write("\n".join(rows)+"\n")
