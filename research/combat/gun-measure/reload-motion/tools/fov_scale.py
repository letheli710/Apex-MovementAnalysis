#!/usr/bin/env python3
"""Does the gun on screen follow cl_fovScale: the same gun at three scales, screenshots, then restore. Also tries slowing time.
  py -3 fov_scale.py <out dir>"""
import glob, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")
RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    code = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    for k, v in dict(weap="mp_weapon_rspn101", mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
        code = code.replace("{{" + k + "}}", v)
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        s.eval(RESET, check=False); s.eval(code, check=False); pl.sleep(2.2); s.eval(RESET, check=False); pl.sleep(2.0)
        def cmd(x): c.eval(f'GetLocalClientPlayer().ClientCommand( "{x}" ); AgentLink_Reply( "s" )', check=False)
        orig = "1.27216005"
        for sc in ("1.0", "1.27216005", "1.5"):
            cmd(f"cl_fovScale {sc}"); pl.sleep(0.6)
            pl.lines["c"].clear()
            c.eval('printt( "[RT] fs " + GetConVarString( "cl_fovScale" ) + " fov=" + GetLocalClientPlayer().GetFOV() ); AgentLink_Reply( "x" )', check=False)
            before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
            cmd("screenshot"); pl.sleep(1.2)
            new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
            print(sc, [l for l in pl.lines["c"] if l.startswith("[RT] fs")][:1], bool(new), flush=True)
            if new: Image.open(new[0]).convert("RGB").save(os.path.join(out, f"fovscale_{sc[:4]}.png"))
        cmd(f"cl_fovScale {orig}"); pl.sleep(0.5)
        # Slow time, each route, then read how far the client clock moves in one real second
        for name, send in (("client", lambda: cmd("host_timescale 0.1")), ("server", lambda: s.eval('SetConVarFloat( "host_timescale", 0.1 ); AgentLink_Reply( "h" )', check=False))):
            send(); pl.sleep(0.4)
            pl.lines["c"].clear()
            c.eval('printt( "[RT] ts " + Time() + " " + GetConVarString( "host_timescale" ) ); AgentLink_Reply( "x" )', check=False); pl.sleep(1.0)
            c.eval('printt( "[RT] ts " + Time() + " " + GetConVarString( "host_timescale" ) ); AgentLink_Reply( "x" )', check=False); pl.sleep(0.2)
            print(name, [l for l in pl.lines["c"] if l.startswith("[RT] ts")], flush=True)
        cmd("host_timescale 1"); s.eval('SetConVarFloat( "host_timescale", 1.0 ); AgentLink_Reply( "h" )', check=False)


if __name__ == "__main__":
    main()
