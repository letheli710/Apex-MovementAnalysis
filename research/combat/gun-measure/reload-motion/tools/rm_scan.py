#!/usr/bin/env python3
"""Every attachment of the view model about 10 times a second through an empty reload, in the camera's frame, to find what moves against the gun: the magazine, the hands.
  py -3 -I rm_scan.py <cases_rm.txt> <out dir>"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime")); sys.path.insert(0, HERE)
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from rm_batch import RESET, POOL, CLIP  # noqa: E402

SCAN = r'''
void functionref() sf = void function() {
	try {
		entity p = GetLocalClientPlayer()
		float t0 = Time()
		while ( Time() - t0 < SECS ) {
			entity vm = p.GetViewModelEntity()
			entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
			vector c = p.CameraPosition()
			vector a = p.CameraAngles()
			vector f = AnglesToForward( a )
			vector r = AnglesToRight( a )
			vector u = AnglesToUp( a )
			string s = format( "[RT] s t=%.4f clip=%d", Time(), w.GetWeaponPrimaryClipCount() )
			for ( int i = 1 ; i < 90 ; i++ ) {
				vector o = <0, 0, 0>
				try { o = vm.GetAttachmentOrigin( i ) } catch ( e3 ) { break }
				vector d = o - c
				s += format( " %d:%.2f,%.2f,%.2f", i, DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ) )
				if ( i % 30 == 0 ) { printt( s ); s = "[RT] s+" }
			}
			printt( s )
			wait 0.09
		}
	} catch ( err ) { printt( "[RT] s err " + string( err ) ) }
	printt( "[RT] s end" )
}
thread sf()
AgentLink_Reply( "g" )
'''


def main():
    cases, out = sys.argv[1:3]
    os.makedirs(out, exist_ok=True)
    code0 = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        for l in open(cases, encoding="utf-8"):
            tag, weap, clip, secs = l.strip().split("|")
            if not tag.endswith("_emp_1"): continue
            gun = tag.split("_")[1]
            p = os.path.join(out, gun + ".txt")
            if os.path.exists(p): continue
            code = code0
            for k, v in dict(weap="mp_weapon_" + weap, mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
                code = code.replace("{{" + k + "}}", v)
            s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2)
            s.eval(RESET, check=False); s.eval(POOL, check=False); s.eval(CLIP(clip), check=False); pl.sleep(0.2)
            pl.lines["c"].clear()
            c.eval(SCAN.replace("SECS", secs), check=False); pl.sleep(0.4)
            c.eval('printt( "[RT] key +reload t=" + Time() ); GetLocalClientPlayer().ClientCommand( "+reload" ); AgentLink_Reply( "k" )', check=False)
            pl.sleep(0.05)
            c.eval('GetLocalClientPlayer().ClientCommand( "-reload" ); AgentLink_Reply( "k" )', check=False)
            dl = time.time() + float(secs) + 3
            while not any(x.startswith("[RT] s end") for x in pl.lines["c"]) and time.time() < dl:
                pl.sleep(0.2)
            open(p, "w", encoding="utf-8").write("\n".join(x for x in pl.lines["c"] if x.startswith(("[RT] s", "[RT] key"))) + "\n")
            print(gun, sum(1 for x in pl.lines["c"] if x.startswith("[RT] s t=")), [x[:100] for x in pl.lines["c"] if " err" in x and "printt" not in x][:1], flush=True)


if __name__ == "__main__":
    main()
