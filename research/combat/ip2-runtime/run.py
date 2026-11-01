#!/usr/bin/env python3
"""IP2 runtime runner: server snippet + optional client input schedule; writes runs/<stamp>_<tag>.txt (raw, goes to HSD-RawData).

  python -I run.py <tag> <snippet.nut> <secs> "<schedule>" k=v ...
{{k}} in the snippet is replaced by v, so Squirrel format() strings need no escaping.
schedule: ';'-separated  wait <s> | down <key> | up <key> | tap <key> | hold <key> <s> | cl <client squirrel> | cc <console cmd>
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402


def key(c, sign, k):
    c.eval(f'GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)


def main():
    tag, snippet, secs, sched = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    kv = dict(a.split("=", 1) for a in sys.argv[5:])
    kv.setdefault("secs", str(secs))
    path = snippet if os.path.isabs(snippet) else os.path.join(HERE, "snippets", snippet)
    code = open(path, encoding="utf-8").read()
    for k, v in kv.items():
        code = code.replace("{{" + k + "}}", v)
    if "{{" in code:
        raise SystemExit("unfilled placeholder: " + code[code.index("{{"):][:40])
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = [f"# {os.path.basename(snippet)} {stamp} sched={sched!r} args={kv}"]
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        r = s.eval(code, check=False)
        out.append("server: " + str(r.get("reply") if r.get("reply") is not None else r))
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
            elif op == "hold":
                k, d = arg.split()
                key(c, "+", k); pl.sleep(float(d)); key(c, "-", k)
            elif op == "cl":
                out.append("client: " + str(c.eval(arg.replace(' | ', '; '), check=False)))
            elif op == "cc":
                c.cmd(arg)
            out.append(f"# sched {time.time() - t0:.2f} {step}")
        pl.sleep(max(0.0, secs + 0.5 - (time.time() - t0)))
    out += ["## server"] + pl.lines["s"] + ["## client"] + pl.lines["c"]
    os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
    p = os.path.join(HERE, "runs", f"{stamp}_{tag}.txt")
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(out[1][:1500])
    print(f"{len(pl.lines['s'])} server / {len(pl.lines['c'])} client -> {os.path.basename(p)}")
    return p


if __name__ == "__main__":
    main()
