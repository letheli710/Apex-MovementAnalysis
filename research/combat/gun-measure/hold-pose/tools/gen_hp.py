#!/usr/bin/env python3
"""Hold-pose cases. py -3 -I gen_hp.py <repeats> [gun ...] > cases.txt. No gun named: all, Sheila last (firing it closes the client; here it does not fire)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from guns import GUNS
# Keep speed on for the length of the slide: the server resets the velocity every 0.1 s for 2.2 s while the player slides.
HOLD = 'sv thread void function() { entity p = GetPlayerArray()[0] ~ float t0 = Time() ~ while ( Time() - t0 < 2.2 ) { if ( !p.IsOnGround() ) { wait 0.1 ~ continue } ~ p.SetVelocity( <380, 0, p.GetVelocity().z> ) ~ wait 0.1 } }() ~ AgentLink_Reply( "h" )'
DROP = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( p.GetOrigin() + <0, 0, 250> ) ~ AgentLink_Reply( "d" )'
STATES = {
    "stand": ("wait 3.5", 6),
    "walk": ("down forward; wait 5; up forward; wait 1.5", 9),
    "sprint": ("down forward; down speed; wait 4.5; up speed; up forward; wait 1.5", 8.5),
    "crouch": ("down duck; wait 3.5; up duck; wait 1.5", 7.5),
    "crouchwalk": ("down duck; wait 0.8; down forward; wait 4.5; up forward; up duck; wait 1.5", 9.5),
    "slide": ("down forward; down speed; wait 1.2; down duck; wait 2.5; up duck; up speed; up forward; wait 1.5", 8),
    "slidehold": (f"down forward; down speed; wait 1.2; down duck; {HOLD}; wait 2.4; up duck; up speed; up forward; wait 1.5", 8.5),
    "jump": ("wait 1.0; tap jump; wait 2.5", 6),
    "drop": (f"wait 0.5; {DROP}; wait 3.5", 6.5),
}
n = int(sys.argv[1])
names = sys.argv[2:] or [g for g in GUNS if g not in ("vantage", "sheila")] + ["sheila"]
for g in names:
    for s, (sched, secs) in STATES.items():
        for r in range(1, n + 1):
            print(f"hp_{g}_{s}_{r}|{GUNS[g]}|{sched}|{secs}")
