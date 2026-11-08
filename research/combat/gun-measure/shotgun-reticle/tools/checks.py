#!/usr/bin/env python3
"""Three checks after fire.py.  py -3 -I checks.py <out dir>   (the hook must already be in, or set SR_HOOK=1 to add it)
turn  synthetic dots held at one age, screenshot, turn the view 6 degrees, screenshot: world point or screen point?
dist  the same dot at 150, 300 and 1200 u: does its size follow distance?
head  real EVA-8 shot a little above the dummie's eye: crit pellets
ads   real EVA-8 shot while aimed: crosshair gone, dots still drawn?
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr  # noqa: E402


def held(r, ages, dist, step, hold="6.0"):
    r.cl(sr.DOTS.replace("{{ages}}", ages).replace("{{dist}}", dist).replace("{{step}}", step).replace("{{hold}}", hold))
    r.pl.sleep(0.4)


def main():
    out = sys.argv[1]
    r = sr.R5(out)
    try:
        if os.environ.get("SR_HOOK") == "1":
            r.cl(sr.HOOK.replace("{{hook}}", "1"))
        r.sv(sr.RESET.replace("{pitch}", "0")); r.pl.sleep(0.5)
        held(r, "0.2,0.2", "300", "30")
        r.shot("turn_held_0", crop=0)
        r.sv('GetPlayerArray()[0].SnapEyeAngles( <0, ' + str(float(sr.YAW) + 6) + ', 0> ); AgentLink_Reply( "t" )'); r.pl.sleep(0.3)
        r.shot("turn_held_6", crop=0)
        r.pl.sleep(6)
        r.sv(sr.RESET.replace("{pitch}", "0")); r.pl.sleep(0.5)
        for d in ("150", "1200"):
            held(r, "0.2,0.2", d, str(float(d) / 10))
            r.shot(f"dist_{d}", crop=0)
            r.pl.sleep(6)
        r.give(sr.GUNS["eva8"], 0, target="head", dist="300", snap="1", secs="10")
        r.pl.lines["c"].clear()
        code = open(os.path.join(sr.COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
        for lift in ("6", "10"):
            for k, v in dict(weap=sr.GUNS["eva8"], mods="none", stock="150", target="head", dist="300", yaw="0", snap="1", lift=lift, heat="0.0", track="0", secs="6").items():
                code_l = code if k != "weap" else code
            c = code
            for k, v in dict(weap=sr.GUNS["eva8"], mods="none", stock="150", target="head", dist="300", yaw="0", snap="1", lift=lift, heat="0.0", track="0", secs="6").items():
                c = c.replace("{{" + k + "}}", v)
            r.sv(c); r.pl.sleep(2.4)
            r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack"); r.pl.sleep(0.08)
            r.shot(f"head_lift{lift}", crop=500)
            r.pl.sleep(1.0)
            r.log.append(f"head lift {lift}: " + " | ".join(l[:90] for l in r.pl.lines["c"] if "hit h=1" in l))
            r.pl.lines["c"].clear()
            r.pl.sleep(4)
        r.give(sr.GUNS["eva8"], 0, target="body", dist="300", snap="1", secs="10")
        r.key("+", "zoom"); r.pl.sleep(1.0)
        r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack"); r.pl.sleep(0.08)
        r.shot("ads_fire", crop=500)
        r.key("-", "zoom")
    finally:
        r.close()
        print("\n".join(l for l in r.log if "head" in l or "NO FILE" in l))


if __name__ == "__main__":
    main()
