#!/usr/bin/env python3
"""Read the camera and view model FOV settings on the client, try the engine screenshot command. py -3 -I fov_probe.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

READ = r'''
entity p = GetLocalClientPlayer()
entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
printt( "[RT] fov GetFOV=" + p.GetFOV() + " w=" + w.GetWeaponClassName() )
foreach ( n in ["viewmodelfov", "viewmodel_fov", "cl_viewmodelfov", "cl_fovScale", "cl_fovscale", "fov", "default_fov", "cl_fov", "base_fov", "r_viewmodelfov", "viewmodel_fov_scale", "r_nearz", "viewmodel_znear", "mat_setvideomode", "cl_gun_x", "viewmodel_offset_x"] ) {
	try { printt( "[RT] fov cvar " + n + " = " + GetConVarString( n ) ) } catch ( e ) { printt( "[RT] fov cvar " + n + " missing" ) }
}
foreach ( n in ["viewmodel_fov", "viewmodelfov", "zoom_fov", "zoom_fov_viewmodel", "viewmodel_offset_hip", "viewmodel_offset_ads"] ) {
	try { printt( "[RT] fov weapon " + n + " = " + w.GetWeaponSettingFloat( eWeaponVar[n] ) ) } catch ( e1 ) { printt( "[RT] fov weapon " + n + " none: " + string( e1 ) ) }
}
AgentLink_Reply( "f" )
'''

with AgentLink("client", DEFAULT_GAME) as c:
    pl = Poller({"c": c})
    r = c.eval(READ, check=False)
    pl.sleep(0.5)
    for l in pl.lines["c"]:
        if "[RT] fov" in l and "printt" not in l: print(l[:150])
    if not r.get("ran"): print(str(r.get("log"))[:500])
    for cmd in ("screenshot",):
        c.eval(f'GetLocalClientPlayer().ClientCommand( "{cmd}" ); AgentLink_Reply( "s" )', check=False)
        pl.sleep(1.0)
