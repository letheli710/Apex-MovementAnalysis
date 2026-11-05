#!/usr/bin/env python3
"""Hold-pose runs: give a weapon, put the player back, log every frame on the client, run a schedule. Keys are logged on the client clock.
  py -3 -I hp_batch.py <cases> <runs dir>
cases: tag|weapon|schedule|secs   schedule: wait <s> | down <key> | up <key> | tap <key> | sv <server squirrel, ~ for ;>
Skips tags with a finished run file. Two failures in a row stop the batch: a dead client shows as timeouts. Exit 3 then."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SetAngles( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'


def run(runs, tag, weap, sched, secs):
    code = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    for k, v in dict(weap=weap, mods="none", stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
        code = code.replace("{{" + k + "}}", v)
    cl = open(os.path.join(HERE, "hold_client.nut"), encoding="utf-8").read().replace("SECS", secs)
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        s.eval(RESET, check=False)
        rep = s.eval(code, check=False).get("reply")
        pl.sleep(2.2)  # the first deploy animation is up to 1.5 s
        s.eval(RESET, check=False)
        c.eval(cl, check=False)
        pl.sleep(0.6)  # the reset counts as a landing
        def key(sign, k):
            c.eval(f'printt( "[RT] key {sign}{k} t=" + Time() ); GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)
        for st in [x.strip() for x in sched.split(";") if x.strip()]:
            op, arg = st.split(None, 1)
            if op == "wait": pl.sleep(float(arg))
            elif op == "down": key("+", arg)
            elif op == "up": key("-", arg)
            elif op == "tap": key("+", arg); pl.sleep(0.05); key("-", arg)
            elif op == "sv": s.eval(arg.replace(" ~ ", "; "), check=False)
        # leave no key down for the next run
        for k in ("forward", "speed", "duck", "jump"):
            c.eval(f'GetLocalClientPlayer().ClientCommand( "-{k}" ); AgentLink_Reply( "k" )', check=False)
        deadline = time.time() + float(secs) + 3
        while not any(x.startswith("[RT] h end") for x in pl.lines["c"]):
            if time.time() > deadline: raise TimeoutError("client log did not end")
            pl.sleep(0.2)
    os.makedirs(runs, exist_ok=True)
    tmp = os.path.join(runs, tag + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} {sched} {time.strftime('%Y%m%d_%H%M%S')}\nreply: {rep}\n## server\n" + "\n".join(pl.lines["s"]) + "\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    os.replace(tmp, os.path.join(runs, tag + ".txt"))
    return rep, pl


def main():
    cases, runs = sys.argv[1:3]
    fails = 0
    for l in open(cases, encoding="utf-8"):
        l = l.strip()
        if not l or l.startswith("#"): continue
        tag, weap, sched, secs = [x.strip() for x in l.split("|")]
        if os.path.exists(os.path.join(runs, tag + ".txt")): continue
        try:
            rep, pl = run(runs, tag, "mp_weapon_" + weap, sched, secs)
            n = sum(1 for x in pl.lines["c"] if "[RT] h t=" in x)
            bad = [x[:110] for x in pl.lines["c"] + pl.lines["s"] if " err" in x]
            print(tag, str(rep)[:40], n, bad[:1], flush=True)
            fails = 0
        except Exception as e:
            print(tag, "EXC", repr(e)[:160], flush=True)
            fails += 1
            if fails >= 2: print("HOST_DOWN", flush=True); sys.exit(3)
    print("BATCH_DONE", flush=True)


if __name__ == "__main__":
    main()
