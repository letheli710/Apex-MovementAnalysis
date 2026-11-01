#!/usr/bin/env python3
"""Server logger snippet + a timed client input schedule; writes runs/<stamp>_<tag>.txt.

  python -I run_sched.py <tag> <snippet.nut> <secs> "<schedule>" k=v ...
schedule: ';'-separated steps  wait <s> | down <key> | up <key> | tap <key>  (console +key / -key)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

tag, snippet, secs, sched = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
kv = dict(a.split("=", 1) for a in sys.argv[5:])
kv["secs"] = str(secs)
code = open(os.path.join(HERE, snippet), encoding="utf-8").read() % kv
stamp = time.strftime("%Y%m%d_%H%M%S")
out = [f"# {os.path.basename(snippet)} {stamp} sched={sched!r} args={kv}"]


def key(c, sign, k):
    c.eval(f'GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)


with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
    pl = Poller({"s": s, "c": c})
    out.append("server: " + str(s.eval(code, check=False).get("reply")))
    t0 = time.time()
    for step in [x.strip() for x in sched.split(";") if x.strip()]:
        op, arg = step.split(None, 1)
        if op == "wait":
            pl.sleep(float(arg))
        elif op == "down":
            key(c, "+", arg)
        elif op == "up":
            key(c, "-", arg)
        elif op == "tap":
            key(c, "+", arg); pl.sleep(0.05); key(c, "-", arg)
        out.append(f"# sched {time.time() - t0:.2f} {step}")
    pl.sleep(max(0.0, secs + 0.5 - (time.time() - t0)))
out += ["## server"] + pl.lines["s"] + ["## client"] + pl.lines["c"]
path = os.path.join(HERE, "runs", f"{stamp}_{tag}.txt")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(out[1][:300]); print(f"{len(pl.lines['s'])} server lines -> {path}")
