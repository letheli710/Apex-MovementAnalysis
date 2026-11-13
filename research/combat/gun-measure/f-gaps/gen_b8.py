#!/usr/bin/env python3
"""B8 cases: long range at 50 / 100 / 200 / 300 m (1969 / 3937 / 7874 / 11811 u) from the spawn pad down the clear yaw-0 lane.
A dummie is held at chest height; the server re-aims each frame at the chest + the predicted drop (snap=1, lift=drop) so the
round lands on it. Three ADS single shots, 1.3 s apart; the [RT] atk hook gives the exact launch direction, the damage event the hit point.
py -3 -I gen_b8.py > cases_b8.txt"""
L = []
PAD = "<-11699.0, 512.0, 1577.05>"
RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + PAD + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "r" )'
G = {"rspn101": (29000, 1.3), "r97": (19000, 1.2), "wingman": (18000, 1.2), "dmr": (31000, 1.3), "sniper": (29500, 1.4)}
for w, (v, gs) in G.items():
    for m in (50, 100, 200, 300):
        d = m * 39.37
        drop = 0.5 * 750 * gs * (d / v) ** 2
        L.append(f"b8_{w}_{m}m|{w}|none|down zoom; wait 1.0; tap attack; wait 1.3; tap attack; wait 1.3; tap attack; wait 1.2; up zoom|secs=7 target=body dist={d:.0f} snap=1 lift={drop:.1f} stock=60")
# run RESET once on the server before the batch (player on the spawn pad); the cases keep it there
print("\n".join(L))
