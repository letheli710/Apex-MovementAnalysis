#!/usr/bin/env python3
"""B6 cases: table end on Flatline and R-99 (hold past the last row, clip refilled by the server every 1.2 s), and Wingman
single shots (server and client attack direction against the client punch). py -3 -I gen_b6.py > cases_b6.txt"""
L = []
ORG = "<-9949.0, -1488.0, 3856.2>"
RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "r" )'
REFILL = 'sv try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( 28 ) } catch ( e ) { printt( "[RT] cx err " + string( e ) ) } ~ AgentLink_Reply( "cx" )'
for r in (1, 2):
    for w in ("vinson", "r97"):
        for mode in ("ads", "hip"):
            pre = "down zoom; wait 0.9; " if mode == "ads" else "wait 0.4; "
            post = "; up zoom" if mode == "ads" else ""
            L.append(f"b6_{w}_{mode}_{r}|{w}|none|{RESET}; {pre}down attack; wait 0.9; {REFILL}; wait 0.9; {REFILL}; wait 0.9; {REFILL}; wait 0.9; {REFILL}; wait 1.0; up attack; wait 0.6{post}|secs=9 stock=300")
    for gap in (0.4, 0.8):
        taps = "; ".join([f"tap attack; wait {gap}"] * 6)
        L.append(f"b6_wingman_ads_g{int(gap * 10)}_{r}|wingman|none|{RESET}; down zoom; wait 0.9; {taps}; up zoom|secs=9 stock=60")
print("\n".join(L))
# second pass, written to cases_b6m.txt (the server refill above did not reach the predicting client, so those runs stopped at the
# stock clip, 18 / 19 shots): mod corrupted_mag gives 35 (Flatline) / 33 (R-99) rounds, hold 4.0 / 2.4 s, no refill.
#   b6m_<gun>_ads_<r>|<gun>|corrupted_mag|RESET; down zoom; wait 0.9; hold attack <d>; wait 0.6; up zoom|secs=8 stock=300
#   b6m_<gun>_hip_<r>|<gun>|corrupted_mag|RESET; wait 0.4; hold attack <d>; wait 0.6|secs=8 stock=300
