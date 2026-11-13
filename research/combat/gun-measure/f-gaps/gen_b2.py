#!/usr/bin/env python3
"""B2 cases: own-fire screen shake. Standing on the roof, one gun per weight class, hip and ADS; 1 s still before and after.
Positive control: client ClientScreenShake, to prove the Frida hook sees a shake. py -3 -I gen_b2.py > cases_b2.txt"""
L = []
ORG = "<-9949.0, -1488.0, 3856.2>"
RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "r" )'
AUTO = {"r97": 1.5, "rspn101": 1.5, "lmg": 1.5}
SEMI = {"wingman": 0.45, "energy_shotgun": 1.3, "dmr": 0.85, "sniper": 1.8}
for r in (1, 2):
    for w, d in AUTO.items():
        add = lambda tag, s: L.append(f"{tag}|{w}|none|{s}|secs=7")
        add(f"b2_{w}_hip_{r}", f"{RESET}; wait 1.0; hold attack {d}; wait 1.2")
        add(f"b2_{w}_ads_{r}", f"{RESET}; down zoom; wait 1.0; hold attack {d}; wait 1.2; up zoom")
    for w, d in SEMI.items():
        taps = "; ".join([f"tap attack; wait {d}"] * 3)
        L.append(f"b2_{w}_hip_{r}|{w}|none|{RESET}; wait 1.0; {taps}; wait 0.8|secs=9")
        L.append(f"b2_{w}_ads_{r}|{w}|none|{RESET}; down zoom; wait 1.0; {taps}; wait 0.8; up zoom|secs=9")
    L.append(f"b2_ctrl_shake_{r}|rspn101|none|{RESET}; wait 1.0; cl ClientScreenShake( 5.0, 10.0, 1.0, <0, 0, 0> ) ~ AgentLink_Reply( \"sh\" ); wait 1.6|secs=5")
print("\n".join(L))
