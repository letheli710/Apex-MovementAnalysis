#!/usr/bin/env python3
"""One step of the UI probe in local R5 (AgentLink, engine screenshots; no mouse, no focus).

  py -3 -I ui_rt.py sv|cl <file.nut | -c code> [wait]      run code on the server / client inside try, print the [RT] lines
  py -3 -I ui_rt.py shot <out.png> [delay]                 engine `screenshot` (HUD on), saved as PNG
  py -3 -I ui_rt.py seq <out prefix> <n> <gap> <cl code>   run client code, then n screenshots `gap` s apart (hit markers, fades)

The AgentLink helpers come from research/combat/w2-runtime (branch combat/w2-runtime and later): set HSD_RT to that folder.
Screenshots land in the game's r2/screenshots as .tga; this copies the new one and converts it.
"""
import glob, os, sys, time

RT = os.environ.get("HSD_RT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "combat", "w2-runtime")
sys.path.insert(0, RT)
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")


class Link:
    def __init__(self):
        self.s = AgentLink("server", DEFAULT_GAME)
        self.c = AgentLink("client", DEFAULT_GAME)
        self.pl = Poller({"s": self.s, "c": self.c})

    def run(self, side, code, wait=0.3):
        k, l = ("s", self.s) if side == "sv" else ("c", self.c)
        self.pl.lines[k].clear()
        r = l.eval('try {\n' + code + '\n} catch ( e_ ) { printt( "[RT] ERR " + e_ ) }\nAgentLink_Reply( "ok" )', check=False)
        if r.get("error"):
            print("EVAL ERROR", r, flush=True)
        self.pl.sleep(wait)
        return list(self.pl.lines[k])

    def shot(self, path, wait=4.0):
        before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
        self.c.eval('GetLocalClientPlayer().ClientCommand( "screenshot" ); AgentLink_Reply( "ok" )', check=False)
        t = time.time()
        new = []
        while time.time() - t < wait:
            time.sleep(0.1)
            new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
            if new:
                break
        if not new:
            raise TimeoutError("no screenshot")
        time.sleep(0.3)
        im = Image.open(new[0]).convert("RGB")
        im.load()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        im.save(path)
        os.remove(new[0])
        return im


def code_arg(a):
    return open(a[1], encoding="utf-8").read() if a[0] != "-c" else a[1]


def main():
    a = sys.argv[1:]
    L = Link()
    if a[0] in ("sv", "cl"):
        rest = a[1:]
        code = code_arg(rest)
        wait = float(rest[2]) if len(rest) > 2 else 0.3
        for x in L.run(a[0], code, wait):
            print(x)
    elif a[0] == "shot":
        if len(a) > 2:
            time.sleep(float(a[2]))
        im = L.shot(a[1])
        print("saved", a[1], im.size)
    elif a[0] == "seq":
        prefix, n, gap, code = a[1], int(a[2]), float(a[3]), a[4]
        L.c.eval('try {\n' + code + '\n} catch ( e_ ) { printt( "[RT] ERR " + e_ ) }\nAgentLink_Reply( "ok" )', check=False)
        t0 = time.time()
        for i in range(n):
            im = L.shot(f"{prefix}_{i:02d}.png")
            print(f"{prefix}_{i:02d}.png  t={time.time() - t0:.2f}", flush=True)
            time.sleep(gap)


main()
