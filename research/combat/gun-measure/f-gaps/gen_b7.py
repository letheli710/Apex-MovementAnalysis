#!/usr/bin/env python3
"""B7 cases: real fire intervals and charge curves. Shots come from the [RT] atk hook (server and client); a client thread logs
charge fraction every frame ([RT] ch). Taps every 0.1 s for the bolt / charge guns, holds for the ramp guns.
py -3 -I gen_b7.py > cases_b7.txt"""
L = []
ORG = "<-9949.0, -1488.0, 3856.2>"
RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "r" )'
CH = lambda secs: ('cl void functionref() chf = void function() { try { entity p = GetLocalClientPlayer() ~ float t0 = Time() ~ while ( Time() - t0 < ' + str(secs) +
                   ' ) { entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand ) ~ printt( format( "[RT] ch t=%.4f c=%.4f clip=%d", Time(), w.GetWeaponChargeFraction(), w.GetWeaponPrimaryClipCount() ) ) ~ WaitFrame() } '
                   '} catch ( e ) { printt( "[RT] ch err " + string( e ) ) } } ~ thread chf() ~ AgentLink_Reply( "ch" )')
for r in (1, 2):
    for w in ("sniper", "sentinel", "defender", "3030", "energy_shotgun"):
        taps = "; ".join(["tap attack; wait 0.1"] * 40)
        L.append(f"b7_{w}_taps_{r}|{w}|none|{RESET}; wait 0.5; {CH(7)}; {taps}; wait 0.5|secs=9 stock=60")
        L.append(f"b7_{w}_hold_{r}|{w}|none|{RESET}; wait 0.5; {CH(5)}; hold attack 4.0; wait 0.5|secs=7 stock=60")
    for w in ("energy_ar", "esaw", "lstar", "dragon_lmg", "defender"):
        L.append(f"b7_{w}_hold2_{r}|{w}|none|{RESET}; wait 0.5; {CH(5)}; hold attack 3.5; wait 0.6|secs=7 stock=300")
    for hold in (0.3, 0.6, 1.0, 1.5):
        L.append(f"b7_bow_draw{int(hold * 10)}_{r}|bow|none|{RESET}; wait 0.5; {CH(3)}; hold attack {hold}; wait 1.2|secs=5 stock=30")
print("\n".join(L))
