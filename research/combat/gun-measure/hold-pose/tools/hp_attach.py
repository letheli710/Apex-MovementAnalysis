#!/usr/bin/env python3
"""Which view model attachments move as one body: read every attachment index in the camera's frame while standing and sprinting, then compare distances between pairs. Also tries turning the view for the sway lag.
  py -3 -I hp_attach.py <out dir>"""
import itertools, json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

SNAP = r'''
try {
	entity p = GetLocalClientPlayer()
	entity vm = p.GetViewModelEntity()
	vector c = p.CameraPosition()
	vector a = p.CameraAngles()
	vector f = AnglesToForward( a )
	vector r = AnglesToRight( a )
	vector u = AnglesToUp( a )
	for ( int i = 1 ; i < 90 ; i++ ) {
		vector o = vm.GetAttachmentOrigin( i )
		vector g = vm.GetAttachmentAngles( i )
		vector d = o - c
		if ( Length( d ) > 300.0 ) continue
		printt( format( "[RT] at TAG i=%d p=%.3f,%.3f,%.3f g=%.2f,%.2f,%.2f", i, DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), g.x - a.x, g.y - a.y, g.z - a.z ) )
	}
	foreach ( n in ["muzzle_flash", "muzzle_flash_scoped", "shell", "R_HAND", "L_HAND", "SIGHT", "ADS_CENTER_SIGHT_R301", "ADS_CENTER_SIGHT_WINGMAN", "ADS_CENTER_SIGHT_SPITFIRE", "ADS_CENTER_SIGHT_R99", "CHARGE", "LASER", "FLASHLIGHT", "ammo", "PROPGUN", "camera"] ) printt( "[RT] at TAG name " + n + " " + vm.LookupAttachment( n ) )
} catch ( e ) { printt( "[RT] at err " + string( e ) ) }
printt( "[RT] at TAG done" )
AgentLink_Reply( "s" )
'''
RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'
TURN = r'''
void functionref() tf = void function() { entity p = GetPlayerArray()[0]; float t0 = Time(); while ( Time() - t0 < 0.8 ) { p.SnapEyeAngles( <0, ( Time() - t0 ) * 90.0, 0> ); WaitFrame() } }
thread tf()
AgentLink_Reply( "t" )
'''


def main():
    out = sys.argv[1]
    res = {}
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        code0 = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
        for gun, weap in (("r301", "rspn101"), ("wingman", "wingman"), ("spitfire", "lmg"), ("p2020", "semipistol")):
            code = code0
            for k, v in dict(weap="mp_weapon_" + weap, mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
                code = code.replace("{{" + k + "}}", v)
            s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2); s.eval(RESET, check=False); pl.sleep(0.6)
            c.eval(SNAP.replace("TAG", gun + "_stand"), check=False); pl.sleep(0.2)
            key = lambda k: c.eval(f'GetLocalClientPlayer().ClientCommand( "{k}" ); AgentLink_Reply( "k" )', check=False)
            key("+forward"); key("+speed"); pl.sleep(1.8)
            for n in range(3):
                c.eval(SNAP.replace("TAG", f"{gun}_sprint{n}"), check=False); pl.sleep(0.14)
            key("-speed"); key("-forward"); pl.sleep(1.0)
        # Turn tests on R-301, logging the muzzle
        code = code0
        for k, v in dict(weap="mp_weapon_rspn101", mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
            code = code.replace("{{" + k + "}}", v)
        s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2); s.eval(RESET, check=False); pl.sleep(0.6)
        cl = open(os.path.join(HERE, "hold_client.nut"), encoding="utf-8").read().replace("SECS", "7")
        c.eval(cl, check=False); pl.sleep(0.5)
        c.eval('printt( "[RT] key snap t=" + Time() ); AgentLink_Reply( "k" )', check=False); s.eval(TURN, check=False); pl.sleep(1.5)
        for k in ("left", "right"):
            c.eval(f'printt( "[RT] key +{k} t=" + Time() ); GetLocalClientPlayer().ClientCommand( "+{k}" ); AgentLink_Reply( "k" )', check=False); pl.sleep(0.8)
            c.eval(f'GetLocalClientPlayer().ClientCommand( "-{k}" ); AgentLink_Reply( "k" )', check=False); pl.sleep(0.8)
        pl.sleep(3)
        s.eval(RESET, check=False)
        lines = pl.lines["c"]
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "attach_scan.txt"), "w", encoding="utf-8").write("\n".join(l for l in lines if "[RT] at" in l) + "\n")
    open(os.path.join(out, "turn_test.txt"), "w", encoding="utf-8").write("\n".join(l for l in lines if "[RT] h " in l or "[RT] key" in l) + "\n")
    print(len(lines))
    print("\n".join(l[:200] for l in lines if " err" in l and "printt" not in l)[:800])


if __name__ == "__main__":
    main()
