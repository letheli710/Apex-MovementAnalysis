#!/usr/bin/env python3
"""Black hole run: server bh_real.nut, client taps +offhand4 (raise) then +attack (throw), then optionally
holds an input from --hold-at to the end. Writes runs/<stamp>_<tag>.txt like rt_probe.

  python -I run_bh.py <tag> <secs> <hold-key|none> <hold-at> k=v ...   (k=v go to bh_real.nut)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt_probe  # noqa: E402
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402

tag, secs, key, hold_at = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4])
kv = dict(a.split("=", 1) for a in sys.argv[5:])
kv["secs"] = str(secs)
code = open(os.path.join(HERE, "snippets", "bh_real.nut"), encoding="utf-8").read() % kv
stamp = time.strftime("%Y%m%d_%H%M%S")
out = [f"# bh_real {stamp} key={key} hold_at={hold_at} args={kv}"]
with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
    pl = Poller({"s": s, "c": c})
    out.append("server: " + str(s.eval(code, check=False).get("reply")))
    pl.sleep(0.5)
    # raise the ultimate (tap offhand4), then throw it with attack (press 0.3 s)
    c.eval('GetLocalClientPlayer().ClientCommand( "+offhand4" ); AgentLink_Reply( "d" )', check=False)
    pl.sleep(0.1)
    c.eval('GetLocalClientPlayer().ClientCommand( "-offhand4" ); AgentLink_Reply( "u" )', check=False)
    pl.sleep(0.8)
    c.eval('GetLocalClientPlayer().ClientCommand( "+attack" ); AgentLink_Reply( "d" )', check=False)
    pl.sleep(0.3)
    c.eval('GetLocalClientPlayer().ClientCommand( "-attack" ); AgentLink_Reply( "u" )', check=False)
    t0 = time.time()
    if key != "none":
        pl.sleep(max(0.0, hold_at))
        c.eval(f'GetLocalClientPlayer().ClientCommand( "+{key}" ); AgentLink_Reply( "d" )', check=False)
    pl.sleep(max(0.0, secs + 1.0 - (time.time() - t0)))
    if key != "none":
        c.eval(f'GetLocalClientPlayer().ClientCommand( "-{key}" ); AgentLink_Reply( "u" )', check=False)
    pl.sleep(0.5)
out += ["## server"] + pl.lines["s"] + ["## client"] + pl.lines["c"]
path = os.path.join(HERE, "runs", f"{stamp}_{tag}.txt")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(out[1][:500]); print(f"{len(pl.lines['s'])} server lines -> {path}")
