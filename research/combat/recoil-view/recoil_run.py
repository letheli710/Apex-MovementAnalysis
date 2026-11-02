#!/usr/bin/env python3
"""Recoil runs: give a weapon (full clip, no target or a held dummie), run a client key schedule, note wall-clock marks so the Frida CSV can be cut.

  py -3 -I recoil_run.py <marks.tsv> <tag> <weapon> "<schedule>" [target=none|body] [dist=150] [secs]
schedule: ';'-separated  wait <s> | down <key> | up <key> | tap <key> | hold <key> <s> | cc <client console cmd>
Every key step is noted with time.time(), the same clock as Date.now() in frida_recoil.js.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402


def main():
    marks, tag, weap, sched = sys.argv[1:5]
    kv = dict(a.split("=", 1) for a in sys.argv[5:])
    code = open(os.path.join(HERE, "..", "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    fill = dict(weap=weap, mods=kv.get("mods", "none"), stock="500", target=kv.get("target", "none"), dist=kv.get("dist", "150"),
                yaw=kv.get("yaw", "0"), snap=kv.get("snap", "0"), lift=kv.get("lift", "0"), heat="0.0", track="0", secs=kv.get("secs", "20"))
    for k, v in fill.items():
        code = code.replace("{{" + k + "}}", v)
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        r = s.eval(code, check=False)
        print(tag, r.get("reply"))
        pl.sleep(float(kv.get("settle", "1.5")))
        rows = [(time.time(), "start", "")]
        for st in [x.strip() for x in sched.split(";") if x.strip()]:
            op, arg = st.split(None, 1)
            def key(sign, k):
                c.eval(f'GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)
                rows.append((time.time(), sign + k, ""))
            if op == "wait": pl.sleep(float(arg))
            elif op == "down": key("+", arg)
            elif op == "up": key("-", arg)
            elif op == "tap": key("+", arg); pl.sleep(0.05); key("-", arg)
            elif op == "cc": c.cmd(arg); rows.append((time.time(), "cc " + arg, ""))
            elif op == "hold":
                k, d = arg.split(); key("+", k); pl.sleep(float(d)); key("-", k)
        rows.append((time.time(), "end", ""))
        pl.sleep(0.3)
    with open(marks, "a", encoding="utf-8") as f:
        for t, m, _ in rows:
            f.write(f"{tag}\t{t:.3f}\t{m}\n")
    runs = os.path.join(HERE, "runs"); os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, f"{tag}.txt"), "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} {sched} {kv} {time.strftime('%Y%m%d_%H%M%S')}\n## server\n" + "\n".join(pl.lines["s"]) + "\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    print(tag, "lines", len(pl.lines["s"]), len(pl.lines["c"]), [l for l in pl.lines["s"] if "clip" in l][-1:] )


if __name__ == "__main__":
    main()
