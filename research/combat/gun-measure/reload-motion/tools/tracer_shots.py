#!/usr/bin/env python3
"""Frames right after a shot, in slow time. Standing hip, and sliding to the right. Saves PNGs and a log of muzzle position, slide flag and clock for each.
  py -3 tracer_shots.py <out dir> [gun ...]"""
import glob, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")
WEAP = dict(r301="rspn101", p2020="semipistol", kraber="sniper")
RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'
TS = lambda v: f'SetConVarFloat( "host_timescale", {v} ); AgentLink_Reply( "h" )'
LOG = r'''
entity p = GetLocalClientPlayer()
entity vm = p.GetViewModelEntity()
vector c = p.CameraPosition()
vector a = p.CameraAngles()
vector f = AnglesToForward( a )
vector r = AnglesToRight( a )
vector u = AnglesToUp( a )
int mz = vm.LookupAttachment( "muzzle_flash" )
vector d = vm.GetAttachmentOrigin( mz ) - c
vector v = p.GetVelocity()
printt( format( "[RT] pos t=%.4f muzzle=%.3f,%.3f,%.3f ca=%.2f,%.2f,%.2f sl=%d vx=%.0f vy=%.0f clip=%d", Time(), DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), a.x, a.y, a.z, p.IsSliding() ? 1 : 0, v.x, v.y, p.GetActiveWeapon( eActiveInventorySlot.mainHand ).GetWeaponPrimaryClipCount() ) )
AgentLink_Reply( "l" )
'''


def main():
    out = sys.argv[1]; names = sys.argv[2:] or list(WEAP)
    os.makedirs(out, exist_ok=True)
    code0 = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        def key(x): c.eval(f'GetLocalClientPlayer().ClientCommand( "{x}" ); AgentLink_Reply( "s" )', check=False)
        rows = []
        for gun in names:
            code = code0
            for k, v in dict(weap="mp_weapon_" + WEAP[gun], mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
                code = code.replace("{{" + k + "}}", v)
            for mode in ("stand", "slide"):
                s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2); s.eval(RESET, check=False); pl.sleep(1.2)
                if mode == "slide":
                    key("+forward"); key("+speed"); pl.sleep(1.0); key("+duck"); pl.sleep(0.25)
                    # to the right, with the view still ahead
                    s.eval('entity p = GetPlayerArray()[0]; p.SetVelocity( <0, -420, 0> ); AgentLink_Reply( "v" )', check=False); key("-forward"); key("-speed")
                    pl.sleep(0.1)
                s.eval(TS(0.05), check=False); pl.sleep(0.1)
                key("+attack")
                for n in range(10):
                    before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
                    pl.lines["c"].clear()
                    c.eval(LOG, check=False)
                    key("screenshot"); pl.sleep(0.35)
                    new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
                    pos = next((l for l in pl.lines["c"] if l.startswith("[RT] pos")), "")
                    if new:
                        Image.open(new[0]).convert("RGB").save(os.path.join(out, f"{gun}_{mode}_{n}.png"))
                    rows.append(f"{gun}\t{mode}\t{n}\t{pos}")
                    print(rows[-1][:125], flush=True)
                key("-attack"); key("-duck")
                s.eval(TS(1.0), check=False); pl.sleep(0.5)
    open(os.path.join(out, "tracer_log.tsv"), "a", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
