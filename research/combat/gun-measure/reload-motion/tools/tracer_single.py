#!/usr/bin/env python3
"""One shot at a time in very slow time, aimed at a dark part of the hall, with frames before and after. Standing, then sliding right.
  py -3 tracer_single.py <out dir> <timescale> [gun ...]"""
import glob, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")
WEAP = dict(r301="rspn101", p2020="semipistol", kraber="sniper")
AIM = "<-12, -35, 0>"
RESET = f'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( {AIM} ); AgentLink_Reply( "r" )'
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
    out, ts = sys.argv[1:3]; names = sys.argv[3:] or list(WEAP)
    os.makedirs(out, exist_ok=True)
    code0 = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        def key(x): c.eval(f'GetLocalClientPlayer().ClientCommand( "{x}" ); AgentLink_Reply( "s" )', check=False)
        def shot(name):
            before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
            pl.lines["c"].clear()
            c.eval(LOG, check=False)
            key("screenshot"); pl.sleep(0.12)
            for _ in range(10):
                new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
                if new: break
                pl.sleep(0.05)
            if new:
                time.sleep(0.03)
                Image.open(new[0]).convert("RGB").save(os.path.join(out, name + ".png"))
            pos = next((l for l in pl.lines["c"] if l.startswith("[RT] pos")), "")
            print(name, pos[9:], flush=True)
            return f"{name}\t{pos}"
        rows = []
        for gun in names:
            code = code0
            for k, v in dict(weap="mp_weapon_" + WEAP[gun], mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
                code = code.replace("{{" + k + "}}", v)
            for mode in ("stand", "slide"):
                s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2); s.eval(RESET, check=False); pl.sleep(1.2)
                if mode == "slide":
                    key("+forward"); key("+speed"); pl.sleep(1.0); key("+duck"); pl.sleep(0.25)
                    # keep sliding to the right for a few seconds so every frame is mid-slide
                    s.eval('void functionref() vf = void function() { entity p = GetPlayerArray()[0]; float t0 = Time(); while ( Time() - t0 < 8.0 ) { p.SetVelocity( AnglesToRight( p.EyeAngles() ) * 380.0 ); wait 0.1 } }; thread vf(); AgentLink_Reply( "v" )', check=False); key("-forward"); key("-speed")
                s.eval(TS(ts), check=False); pl.sleep(0.2)
                rows.append(shot(f"{gun}_{mode}_00before"))
                if gun == "r301":
                    for burst in (1, 2):
                        key("+attack")
                        for n in range(6):
                            rows.append(shot(f"{gun}_{mode}_b{burst}_{n}"))
                        key("-attack")
                        pl.sleep(0.5)
                else:
                    # a single shot per press: walk the delay from the press to the frame, the tracer lasts only moments
                    for n, d in enumerate((0, 0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.0, 0.02, 0.04, 0.06)):
                        key("+attack"); pl.sleep(d)
                        rows.append(shot(f"{gun}_{mode}_t{n}"))
                        key("-attack")
                        pl.sleep(1.8 if gun == "kraber" else 0.35)
                key("-duck")
                s.eval(TS(1.0), check=False); pl.sleep(0.6)
    open(os.path.join(out, "single_log.tsv"), "a", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
