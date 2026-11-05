#!/usr/bin/env python3
"""Reload motion runs: fill the ammo pools, set the clip, press reload, log every frame until the animation has ended.
  py -3 -I rm_batch.py <cases> <runs dir>     cases: tag|weapon|clip|secs
Skips finished tags. Two failures in a row stop the batch, exit 3: a dead client shows as timeouts."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'
POOL = 'entity p = GetPlayerArray()[0]; p.AmmoPool_SetCapacity( 999 ); for ( int i = 0; i < 8; i++ ) { try { p.AmmoPool_SetCount( i, 300 ) } catch ( e1 ) { } }; AgentLink_Reply( "p" )'
CLIP = lambda n: 'try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( ' + str(n) + ' ) } catch ( e ) { printt( "[RT] rx err " + string( e ) ) }; AgentLink_Reply( "c" )'


def run(runs, tag, weap, clip, secs):
    code = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    for k, v in dict(weap=weap, mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
        code = code.replace("{{" + k + "}}", v)
    cl = open(os.path.join(HERE, "reload_client.nut"), encoding="utf-8").read().replace("SECS", secs)
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        s.eval(RESET, check=False)
        rep = s.eval(code, check=False).get("reply")
        pl.sleep(2.2)
        s.eval(RESET, check=False); s.eval(POOL, check=False); s.eval(CLIP(clip), check=False)
        pl.sleep(0.2)
        c.eval(cl, check=False)
        pl.sleep(0.4)
        c.eval('printt( "[RT] key +reload t=" + Time() ); GetLocalClientPlayer().ClientCommand( "+reload" ); AgentLink_Reply( "k" )', check=False)
        pl.sleep(0.05)
        c.eval('GetLocalClientPlayer().ClientCommand( "-reload" ); AgentLink_Reply( "k" )', check=False)
        deadline = time.time() + float(secs) + 3
        while not any(x.startswith("[RT] r end") for x in pl.lines["c"]):
            if time.time() > deadline: raise TimeoutError("client log did not end")
            pl.sleep(0.2)
    os.makedirs(runs, exist_ok=True)
    tmp = os.path.join(runs, tag + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} clip={clip} {time.strftime('%Y%m%d_%H%M%S')}\nreply: {rep}\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    os.replace(tmp, os.path.join(runs, tag + ".txt"))
    return pl


def main():
    cases, runs = sys.argv[1:3]
    fails = 0
    for l in open(cases, encoding="utf-8"):
        l = l.strip()
        if not l: continue
        tag, weap, clip, secs = l.split("|")
        if os.path.exists(os.path.join(runs, tag + ".txt")): continue
        try:
            pl = run(runs, tag, "mp_weapon_" + weap, clip, secs)
            n = sum(1 for x in pl.lines["c"] if x.startswith("[RT] r t="))
            rel = sum(1 for x in pl.lines["c"] if x.startswith("[RT] r t=") and " rel=1 " in x)
            bad = [x[:110] for x in pl.lines["c"] if " err" in x and "printt" not in x]
            print(tag, n, "rel", rel, bad[:1], flush=True)
            fails = 0
        except Exception as e:
            print(tag, "EXC", repr(e)[:160], flush=True)
            fails += 1
            if fails >= 2: print("HOST_DOWN", flush=True); sys.exit(3)
    print("BATCH_DONE", flush=True)


if __name__ == "__main__":
    main()
