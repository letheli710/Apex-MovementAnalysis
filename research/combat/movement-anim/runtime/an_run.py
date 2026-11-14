#!/usr/bin/env python3
"""C1-C5 animation runs (copy of gun-measure/hold-pose/tools/hp_batch.py with wall-clock marks for the Frida frames).
  py -3 -I an_run.py <cases> <out dir>      -> <out>/runs/<tag>.txt, <out>/marks.tsv (tag, wall s, mark)
cases: tag|weapon|schedule|secs   schedule (';'-separated): wait <s> | down <key> | up <key> | tap <key> | sv <server squirrel, ~ for ;> | cl <client squirrel>
Each run: put the player back, give the weapon (full clip), reset again, start the client logger (anim_client.nut), run the schedule,
release every key and stop status effects / zipline. Skips tags with a finished run file. Two failures in a row stop the batch (exit 3)."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SetAngles( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'
CLEAN = ('entity p = GetPlayerArray()[0]; try { if ( p.IsZiplining() ) p.Zipline_Stop() } catch ( e ) { } '
         'try { StatusEffect_StopAllOfType( p, eStatusEffect.move_slow ); StatusEffect_StopAllOfType( p, eStatusEffect.speed_boost ) } catch ( e2 ) { } '
         'try { p.TakeOffhandWeapon( OFFHAND_TACTICAL ) } catch ( e3 ) { } AgentLink_Reply( "c" )')
KEYS = ("forward", "back", "moveleft", "moveright", "speed", "duck", "jump", "zoom", "attack", "reload", "use", "offhand1", "left", "right")


def run(out, tag, weap, sched, secs):
    code = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    for k, v in dict(weap=weap, mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
        code = code.replace("{{" + k + "}}", v)
    cl = open(os.path.join(HERE, "anim_client.nut"), encoding="utf-8").read().replace("SECS", secs)
    marks = []
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        s.eval(CLEAN, check=False)
        s.eval(RESET, check=False)
        rep = s.eval(code, check=False).get("reply")
        pl.sleep(2.2)
        s.eval(RESET, check=False)
        c.eval(cl, check=False)
        marks.append((time.time(), "logstart"))
        pl.sleep(0.6)
        def key(sign, k):
            c.eval(f'printt( "[RT] key {sign}{k} t=" + Time() ); GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)
            marks.append((time.time(), sign + k))
        for st in [x.strip() for x in sched.split(";") if x.strip()]:
            op, arg = st.split(None, 1)
            if op == "wait": pl.sleep(float(arg))
            elif op == "down": key("+", arg)
            elif op == "up": key("-", arg)
            elif op == "tap": key("+", arg); pl.sleep(0.05); key("-", arg)
            elif op == "sv":
                r = s.eval(arg.replace(" ~ ", "; "), check=False); marks.append((time.time(), "sv " + str(r.get("reply"))[:120]))
            elif op == "cl":
                r = c.eval(arg.replace(" ~ ", "; "), check=False); marks.append((time.time(), "cl " + str(r.get("reply"))[:120]))
        for k in KEYS:
            c.eval(f'GetLocalClientPlayer().ClientCommand( "-{k}" ); AgentLink_Reply( "k" )', check=False)
        marks.append((time.time(), "end"))
        deadline = time.time() + float(secs) + 3
        while not any(x.startswith("[RT] a end") for x in pl.lines["c"]):
            if time.time() > deadline: raise TimeoutError("client log did not end")
            pl.sleep(0.2)
        s.eval(CLEAN, check=False)
    os.makedirs(os.path.join(out, "runs"), exist_ok=True)
    with open(os.path.join(out, "marks.tsv"), "a", encoding="utf-8") as f:
        for t, m in marks: f.write(f"{tag}\t{t:.3f}\t{m}\n")
    tmp = os.path.join(out, "runs", tag + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} {sched} {time.strftime('%Y%m%d_%H%M%S')}\nreply: {rep}\n## server\n" + "\n".join(pl.lines["s"]) + "\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    os.replace(tmp, os.path.join(out, "runs", tag + ".txt"))
    return rep, pl


def main():
    cases, out = sys.argv[1:3]
    fails = 0
    for l in open(cases, encoding="utf-8"):
        l = l.strip()
        if not l or l.startswith("#"): continue
        tag, weap, sched, secs = [x.strip() for x in l.split("|")]
        if os.path.exists(os.path.join(out, "runs", tag + ".txt")): continue
        try:
            rep, pl = run(out, tag, "mp_weapon_" + weap, sched, secs)
            n = sum(1 for x in pl.lines["c"] if "[RT] a t=" in x)
            bad = [x[:110] for x in pl.lines["c"] + pl.lines["s"] if " err" in x or "SCRIPT ERROR" in x]
            print(tag, str(rep)[:40], n, bad[:1], flush=True)
            fails = 0
        except Exception as e:
            print(tag, "EXC", repr(e)[:160], flush=True)
            fails += 1
            if fails >= 2: print("HOST_DOWN", flush=True); sys.exit(3)
    print("BATCH_DONE", flush=True)


if __name__ == "__main__":
    main()
