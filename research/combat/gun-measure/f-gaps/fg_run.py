#!/usr/bin/env python3
"""F-GAPS run (copy of tools/gm_run.py with track=, yaw= passed through). One gun run: give a weapon with mods, start the client logger (client.nut), run a schedule, note wall-clock marks.
  py -3 -I gm_run.py <marks.tsv> <runs dir> <tag> <weapon> <mods|none> "<schedule>" [secs=6] [target=none|body] [dist=150] [snap=0] [settle=1.6] [attach=NAME]
schedule: ';'-separated  wait <s> | down <key> | up <key> | tap <key> | hold <key> <s> | cmd <client command> | sv <server squirrel> | cl <client squirrel>
Run from anywhere; imports rt_probe from ../../w2-runtime."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402


def run(marks, runs, tag, weap, mods, sched, kv):
    code = open(os.path.join(HERE, "..", "..", "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    fill = dict(weap=weap, mods=mods, stock=kv.get("stock", "200"), target=kv.get("target", "none"), dist=kv.get("dist", "150"), yaw=kv.get("yaw", "0"), snap=kv.get("snap", "0"),
                lift=kv.get("lift", "0"), heat="0.0", track=kv.get("track", "0"), secs=kv.get("secs", "6"))
    for k, v in fill.items():
        code = code.replace("{{" + k + "}}", v)
    cl = open(os.path.join(HERE, "..", "tools", "client.nut"), encoding="utf-8").read().replace("SECS", kv.get("secs", "6")).replace("ATTACH", kv.get("attach", "muzzle_flash"))
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        rep = s.eval(code, check=False).get("reply")
        pl.sleep(float(kv.get("settle", "1.6")))
        if kv.get("clog", "1") == "1":
            c.eval(cl, check=False)
        rows = [(time.time(), "start")]
        for st in [x.strip() for x in sched.split(";") if x.strip()]:
            op, arg = st.split(None, 1)
            def key(sign, k):
                c.eval(f'GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )', check=False)
                rows.append((time.time(), sign + k))
            if op == "wait": pl.sleep(float(arg))
            elif op == "down": key("+", arg)
            elif op == "up": key("-", arg)
            elif op == "tap": key("+", arg); pl.sleep(0.05); key("-", arg)
            elif op == "hold":
                k, d = arg.split(); key("+", k); pl.sleep(float(d)); key("-", k)
            elif op == "cmd":
                c.eval(f'GetLocalClientPlayer().ClientCommand( "{arg}" ); AgentLink_Reply( "k" )', check=False); rows.append((time.time(), "cmd " + arg))
            elif op == "sv":
                r = s.eval(arg.replace(" ~ ", "; "), check=False); rows.append((time.time(), "sv " + str(r.get("reply"))[:200]))
            elif op == "cl":
                r = c.eval(arg.replace(" ~ ", "; "), check=False); rows.append((time.time(), "cl " + str(r.get("reply"))[:200]))
        rows.append((time.time(), "end"))
        pl.sleep(float(kv.get("tail", "0.3")))
    with open(marks, "a", encoding="utf-8") as f:
        for t, m in rows: f.write(f"{tag}\t{t:.3f}\t{m}\n")
    os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, f"{tag}.txt"), "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} {mods} {sched} {kv} {time.strftime('%Y%m%d_%H%M%S')}\nreply: {rep}\n## server\n" + "\n".join(pl.lines["s"]) + "\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    return rep, pl


if __name__ == "__main__":
    marks, runs, tag, weap, mods, sched = sys.argv[1:7]
    kv = dict(a.split("=", 1) for a in sys.argv[7:])
    rep, pl = run(marks, runs, tag, weap, mods, sched, kv)
    print(tag, str(rep)[:150], "lines", len(pl.lines["s"]), len(pl.lines["c"]), [l[:120] for l in pl.lines["c"] if "err" in l][:1])
