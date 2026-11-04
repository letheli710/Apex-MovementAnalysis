"""Shared helpers for the iron-sight probes: links, eval with try, engine screenshots (no mouse, no focus)."""
import glob, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")
RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SetAngles( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> ); AgentLink_Reply( "r" )'


class Link:
    def __init__(self):
        self.s = AgentLink("server", DEFAULT_GAME)
        self.c = AgentLink("client", DEFAULT_GAME)
        self.pl = Poller({"s": self.s, "c": self.c})

    def close(self):
        self.s.close(); self.c.close()

    def sleep(self, t):
        self.pl.sleep(t)

    def cl(self, code, wait=0.15):
        """Run client code inside try. Returns the [RT] lines it printed."""
        self.pl.lines["c"].clear()
        r = self.c.eval('try {\n' + code + '\n} catch ( e_ ) { printt( "[RT] ERR " + e_ ) }\nAgentLink_Reply( "ok" )', check=False)
        if r.get("error"):
            print("EVAL ERROR", r, flush=True)
        self.pl.sleep(wait)
        return list(self.pl.lines["c"])

    def sv(self, code, wait=0.15):
        self.pl.lines["s"].clear()
        r = self.s.eval('try {\n' + code + '\n} catch ( e_ ) { printt( "[RT] ERR " + e_ ) }\nAgentLink_Reply( "ok" )', check=False)
        if r.get("error"):
            print("EVAL ERROR", r, flush=True)
        self.pl.sleep(wait)
        return list(self.pl.lines["s"])

    def reset(self):
        self.s.eval(RESET, check=False)

    def give(self, weap, mods="none"):
        code = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
        for k, v in dict(weap=weap, mods=mods, stock="150", target="none", dist="150", yaw="0", snap="0", lift="0", heat="0.0", track="0", secs="1").items():
            code = code.replace("{{" + k + "}}", v)
        self.reset()
        r = self.s.eval(code, check=False).get("reply")
        self.pl.sleep(2.2)
        self.reset()
        self.pl.sleep(0.8)
        return r

    def shot(self, path, wait=1.2):
        """Engine screenshot to a PNG; returns the PIL image."""
        before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
        self.cl('GetLocalClientPlayer().ClientCommand( "screenshot" )', 0.05)
        t = time.time()
        new = []
        while time.time() - t < wait + 3:
            self.pl.sleep(0.2)
            new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
            if new:
                break
        if not new:
            raise TimeoutError("no screenshot")
        self.pl.sleep(0.3)
        im = Image.open(new[0]).convert("RGB")
        im.load()
        if path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path)
        return im
