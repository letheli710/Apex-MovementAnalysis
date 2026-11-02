#!/usr/bin/env python3
"""Follow-ups to D, run after C: flinch with a health read and with the player as attacker; P2020 ADS without a shot, for the drift baseline; table end past the clip by refilling. py -3 -I gen_e.py > cases_e.txt"""
L = []
def add(tag, w, m, s, k): L.append(f"{tag}|{w}|{m}|{s}|{k}")
HP = lambda a, who: 'sv try { entity p = GetPlayerArray()[0] ~ p.SetMaxHealth( 1000 ) ~ p.SetHealth( 1000 ) ~ p.TakeDamage( ' + str(a) + ', ' + who + ', ' + who + ', { damageSourceId = eDamageSourceId.mp_weapon_rspn101 } ) ~ printt( "[RT] hp " + p.GetHealth() ) } catch ( e ) { printt( "[RT] td err " + string( e ) ) } ~ AgentLink_Reply( "td" )'
for r in (1, 2, 3):
    for who, name in (("null", "none"), ("p", "self")):
        add(f"fl2_{name}_hip_{r}", "rspn101", "none", "wait 0.5; " + HP(60, who) + "; wait 1.5", "secs=5")
        add(f"fl2_{name}_ads_{r}", "rspn101", "none", "down zoom; wait 0.8; " + HP(60, who) + "; wait 1.2; up zoom", "secs=5")
for r in range(1, 7):
    add(f"fxn_p2020_{r}", "semipistol", "none", "down zoom; wait 1.7; up zoom", "secs=4")
CL = 'sv try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( 31 ) } catch ( e ) { printt( "[RT] cx err " + string( e ) ) } ~ AgentLink_Reply( "cx" )'
add("lp2_r301", "rspn101", "bullets_mag_l4", "down attack; wait 1.5; " + CL + "; wait 1.5; " + CL + "; wait 1.5; " + CL + "; wait 1.5; up attack; wait 0.5", "secs=10 stock=300")
add("lp2_flatline", "vinson", "highcal_mag_l4", "down attack; wait 2.0; " + CL.replace("31", "30") + "; wait 2.0; " + CL.replace("31", "30") + "; wait 1.5; up attack; wait 0.5", "secs=10 stock=300")
print("\n".join(L))
