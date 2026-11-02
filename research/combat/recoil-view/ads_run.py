#!/usr/bin/env python3
"""ADS runs: give a weapon, start the client logger, run a key schedule, note wall-clock marks (same clock as frida_ads.js).
  py -3 -I ads_run.py <marks.tsv> <tag> <weapon> <attachment> "<schedule>" [secs=6]
schedule: ';'-separated  wait <s> | down <key> | up <key>"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402


def main():
    marks, tag, weap, att, sched = sys.argv[1:6]
    kv = dict(a.split("=", 1) for a in sys.argv[6:])
    code = open(os.path.join(HERE, "..", "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
    fill = dict(weap=weap, mods="none", stock="50", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1")
    for k, v in fill.items():
        code = code.replace("{{" + k + "}}", v)
    cl = open(os.path.join(HERE, "ads_client.txt"), encoding="utf-8").read().replace("SECS", kv.get("secs", "6")).replace("ATTACH", att)
    with AgentLink("server", DEFAULT_GAME) as s, AgentLink("client", DEFAULT_GAME) as c:
        pl = Poller({"s": s, "c": c})
        print(tag, s.eval(code, check=False).get("reply"))
        pl.sleep(1.2)
        print(c.eval(cl, check=False).get("reply"))
        rows = [(time.time(), "start")]
        for st in [x.strip() for x in sched.split(";") if x.strip()]:
            op, arg = st.split(None, 1)
            if op == "wait":
                pl.sleep(float(arg))
            else:
                sign = "+" if op == "down" else "-"
                c.eval(f'GetLocalClientPlayer().ClientCommand( "{sign}{arg}" ); AgentLink_Reply( "k" )', check=False)
                rows.append((time.time(), sign + arg))
        rows.append((time.time(), "end"))
        pl.sleep(float(kv.get("tail", "0.3")))
    with open(marks, "a", encoding="utf-8") as f:
        for t, m in rows:
            f.write(f"{tag}\t{t:.3f}\t{m}\n")
    runs = os.path.join(HERE, "runs")
    os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, f"{tag}.txt"), "w", encoding="utf-8") as f:
        f.write(f"# {tag} {weap} {att} {sched} {time.strftime('%Y%m%d_%H%M%S')}\n## server\n" + "\n".join(pl.lines["s"]) + "\n## client\n" + "\n".join(pl.lines["c"]) + "\n")
    ad = [l for l in pl.lines["c"] if "] ad " in l]
    print(tag, "client lines", len(ad), ad[:1], [l for l in ad if "err" in l][:1])


if __name__ == "__main__":
    main()
