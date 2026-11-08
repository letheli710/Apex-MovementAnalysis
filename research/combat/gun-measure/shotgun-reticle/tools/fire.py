#!/usr/bin/env python3
"""Real shots at a hovering dummie (gun.nut: held by SetOrigin, eye snapped to it each frame), screenshots before and after.
  py -3 -I fire.py <out dir>
1. EVA-8 body 300 u with no hook: what the firing range itself shows (R5 turns the dots off there, cl_hud.gnut ShouldShowProjectileHitDot).
2. The hook: R5's own dot code (DamageFlyout), firing-range gate left out. Then shots per gun and target.
3. Turn: hit, then turn the view 6 degrees: do the dots stay on the world point?
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr  # noqa: E402

CASES = [  # gun, target, dist, delay after the shot
    ("eva8", "body", "300", 0.1), ("eva8", "body", "700", 0.1), ("eva8", "head", "300", 0.1),
    ("mastiff", "body", "300", 0.1), ("mastiff", "body", "900", 0.1),
    ("peacekeeper", "body", "300", 0.1), ("peacekeeper", "body", "500", 0.1),
    ("mozambique", "body", "300", 0.1), ("mozambique", "body", "500", 0.1),
    ("tripletake", "body", "600", 0.15), ("eva8", "body", "300", 0.5),
]


def shoot(r, tag, delay):
    r.pl.lines["c"].clear()
    r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack")
    r.pl.sleep(delay)
    r.shot(tag + "_after", crop=500)
    r.pl.sleep(1.0)
    hits = [l for l in r.pl.lines["c"] if l.startswith("[RT] hit") or "dotlife" in l]
    r.log.append(f"{tag} hits={sum(1 for l in hits if 'hit h=1' in l or ('hit h=0' in l and 'nohook' in tag))}")
    r.log.extend("  " + l for l in hits)


def main():
    out = sys.argv[1]
    r = sr.R5(out)
    try:
        r.give(sr.GUNS["eva8"], 0, target="body", dist="300", snap="1", secs="25")
        r.shot("eva8_body_300_nohook_before", crop=500)
        r.cl(sr.HOOK.replace("{{hook}}", "0"))          # logs hits only, no dot: the firing range as it is
        shoot(r, "eva8_body_300_nohook", 0.1)
        r.close()
        r = sr.R5(out)
        print(r.cl(sr.HOOK.replace("{{hook}}", "1")))   # a second callback that also draws the dots
        for gun, target, dist, delay in CASES:
            r.give(sr.GUNS[gun], 0, target=target, dist=dist, snap="1", secs="12")
            shoot(r, f"{gun}_{target}_{dist}_d{delay}", delay)
            print(r.log[-1] if not r.log[-1].startswith("  ") else "", flush=True)
        # turn test: no snap, aim straight at the chest, then turn
        r.give(sr.GUNS["eva8"], 0, target="body", dist="300", snap="1", secs="3")
        r.pl.sleep(3.2)
        r.sv('GetPlayerArray()[0].SnapEyeAngles( <0, ' + sr.YAW + ', 0> ); AgentLink_Reply( "a" )')
        r.give(sr.GUNS["eva8"], 0, target="body", dist="300", snap="0", secs="12")
        r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack"); r.pl.sleep(0.08)
        r.shot("turn_0", crop=500)
        r.sv('GetPlayerArray()[0].SnapEyeAngles( <0, ' + str(float(sr.YAW) + 6) + ', 0> ); AgentLink_Reply( "t" )'); r.pl.sleep(0.05)
        r.shot("turn_6", crop=500)
    finally:
        r.close()
        print("\n".join(l for l in r.log if "hits=" in l or "NO FILE" in l))


if __name__ == "__main__":
    main()
