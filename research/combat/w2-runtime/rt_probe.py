#!/usr/bin/env python3
"""Combat wave-2 runtime probes in local R5Flowstate, over AgentLink.

Same approach as TF2-Research/expansion/apex/w4_probe.py: run a Squirrel snippet on the
server (or client), then collect every log line tagged [RT] for a while.

  python -I rt_probe.py launch                 # start dedi + client (GAME-LOCK is handled by the caller)
  python -I rt_probe.py run <snippet.nut> <secs> [server|client] [k=v ...]
                                               # %(k)s placeholders in the snippet are filled from k=v
  python -I rt_probe.py stop

Output: runs/<stamp>_<snippet>.txt next to this file (raw; copied to HSD-RawData).
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TOOLS = os.path.join(REPO, "research", "phase2-local", "tools")
sys.path.insert(0, TOOLS)
from agentlink import AgentLink, AgentLinkError, DEFAULT_GAME  # noqa: E402

RUNS = os.path.join(HERE, "runs")
PS = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(TOOLS, "hsd_launch.ps1")]


def wait_alive(game, timeout=900):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with AgentLink("client", game, timeout=10) as c, AgentLink("server", game, timeout=10) as s:
                cl = c.eval('entity p = GetLocalClientPlayer(); AgentLink_Reply( IsValid( p ) && IsAlive( p ) ? "alive" : "no" )', check=False)
                sv = s.eval('AgentLink_Reply( GetPlayerArray().len() > 0 && IsAlive( GetPlayerArray()[0] ) ? "alive" : "no" )', check=False)
                if cl.get("reply") == "alive" and sv.get("reply") == "alive":
                    return True
        except (OSError, AgentLinkError, FileNotFoundError):
            pass
        time.sleep(5)
    return False


class Poller:
    def __init__(self, links, tag="[RT]"):
        self.links, self.tag = links, tag
        self.cur = {k: l.info()["logSeq"] for k, l in links.items()}
        self.lines = {k: [] for k in links}

    def poll(self):
        for k, l in self.links.items():
            while True:
                r = l.log(self.cur[k], 500)
                for e in r.get("lines", []):
                    t = e.get("text", "")
                    if self.tag in t or "SCRIPT ERROR" in t or t.startswith(" -> ") or t.startswith("*FUNCTION"):
                        self.lines[k].append(e["text"].rstrip())
                nxt = r.get("next", self.cur[k])
                if nxt == self.cur[k] or not r.get("lines"):
                    self.cur[k] = nxt
                    break
                self.cur[k] = nxt

    def sleep(self, sec):
        end = time.time() + sec
        while time.time() < end:
            self.poll()
            time.sleep(0.05)
        self.poll()


def run(snippet, secs, side, kv, game):
    with open(snippet, encoding="utf-8") as fh:
        code = fh.read()
    if kv:
        code = code % kv
    os.makedirs(RUNS, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    name = os.path.splitext(os.path.basename(snippet))[0]
    tag = kv.get("tag", name)
    out = [f"# {name} {stamp} side={side} args={kv}"]
    with AgentLink("server", game) as s, AgentLink("client", game) as c:
        pl = Poller({"s": s, "c": c})
        link = s if side == "server" else c
        r = link.eval(code, check=False)
        out.append("reply: " + str(r.get("reply") if r.get("reply") is not None else r))
        pl.sleep(secs)
        sl, cl = pl.lines["s"], pl.lines["c"]
    out += ["## server"] + sl + ["## client"] + cl
    path = os.path.join(RUNS, f"{stamp}_{tag}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(out[1][:3000])
    print(f"... {len(sl)} server / {len(cl)} client lines -> {path}")


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    game = DEFAULT_GAME
    if argv[0] == "launch":
        subprocess.run(PS, check=True)
        print("alive" if wait_alive(game) else "NOT alive")
    elif argv[0] == "run":
        kv = dict(a.split("=", 1) for a in argv[4:])
        run(argv[1], float(argv[2]), argv[3] if len(argv) > 3 else "server", kv, game)
    elif argv[0] == "stop":
        subprocess.run(PS + ["-Stop"])
        print("stopped")


if __name__ == "__main__":
    main(sys.argv[1:])
