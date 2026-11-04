#!/usr/bin/env python3
"""Standing hip screenshots through the engine command: no focus or mouse. Also logs muzzle and sight centre in the camera's frame at the shot, for working out the view model FOV.
  py -3 -I shots.py <out dir>"""
import glob, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")
GUNS = (("r301", "rspn101"), ("r99", "r97"), ("spitfire", "lmg"), ("p2020", "semipistol"), ("wingman", "wingman"), ("mastiff", "mastiff"), ("longbow", "dmr"), ("kraber", "sniper"))
RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'
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
printt( format( "[RT] pos muzzle=%.3f,%.3f,%.3f fov=%.2f ca=%.2f,%.2f,%.2f zf=%.2f", DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), p.GetFOV(), a.x, a.y, a.z, p.GetZoomFrac() ) )
AgentLink_Reply( "l" )
'''


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    code0 = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        rows = []
        for gun, weap in GUNS:
            code = code0
            for k, v in dict(weap="mp_weapon_" + weap, mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
                code = code.replace("{{" + k + "}}", v)
            s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2); s.eval(RESET, check=False); pl.sleep(2.0)
            before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
            pl.lines["c"].clear()
            c.eval(LOG, check=False)
            c.eval('GetLocalClientPlayer().ClientCommand( "screenshot" ); AgentLink_Reply( "s" )', check=False)
            pl.sleep(1.2)
            new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
            pos = next((l for l in pl.lines["c"] if l.startswith("[RT] pos")), "")
            if new:
                im = Image.open(new[0]).convert("RGB")
                im.save(os.path.join(out, f"{gun}_stand_hip.png"))
                rows.append(f"{gun}\t{im.size[0]}x{im.size[1]}\t{pos}")
            else:
                rows.append(f"{gun}\tNO FILE\t{pos}")
            print(rows[-1], flush=True)
    open(os.path.join(out, "shots.tsv"), "w", encoding="utf-8", newline="\n").write("gun\tsize\tlog\n" + "\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
