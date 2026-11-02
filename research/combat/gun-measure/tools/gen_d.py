#!/usr/bin/env python3
"""Cases for D: fire rate all guns, damage, drop, flinch, table end, jolt. py -3 -I gen_d.py > cases_d.txt"""
import sys
sys.path.insert(0, ".")
from guns import GUNS
L = []
def add(tag, w, m, s, k): L.append(f"{tag}|{w}|{m}|{s}|{k}")
SEMI = {"p2020", "wingman", "mozambique", "peacekeeper", "mastiff", "eva8x", "kraber", "longbow", "sentinel", "g7", "tripletake", "chargerifle", "r3030", "bocek", "hemlok"}
# 1. Rate, all guns: hold, then taps as fast as allowed
for g, w in GUNS.items():
    if g == "vantage": continue
    add(f"fr_{g}_hold", w, "none", "wait 0.3; hold attack 3.0; wait 0.8", "secs=8 stock=300")
    add(f"fr_{g}_taps", w, "none", "wait 0.3; " + "; ".join(["tap attack; wait 0.04"] * 12) + "; wait 0.8", "secs=8 stock=300")
    add(f"fr_{g}_adshold", w, "none", "down zoom; wait 0.8; hold attack 2.0; wait 0.8; up zoom", "secs=8 stock=300")
# 2. Falloff and groups: ADS, target at distance. Shots spaced so the spread settles.
DG = {"r301": ("rspn101", 0.25), "r99": ("r97", 0.25), "p2020": ("semipistol", 0.3), "wingman": ("wingman", 0.5), "longbow": ("dmr", 0.9), "kraber": ("sniper", 1.2), "havoc": ("energy_ar", 0.3), "eva8": ("shotgun", 0.9), "mastiff": ("mastiff", 1.2), "g7": ("g2", 0.45)}
for g, (w, gap) in DG.items():
    for d in (300, 800, 1500, 2500, 3500, 5000):
        s = "down zoom; wait 1.0; " + "; ".join([f"tap attack; wait {gap}"] * 5) + "; wait 0.5; up zoom"
        add(f"df_{g}_{d}", w, "none", s, f"target=body dist={d} snap=1 secs=10 lift={0.5 * 750 * 1.3 * (d / 29000) ** 2:.2f}")
    for tg in ("head", "leg"):
        s = "down zoom; wait 1.0; " + "; ".join([f"tap attack; wait {gap}"] * 4) + "; wait 0.5; up zoom"
        add(f"dg_{g}_{tg}", w, "none", s, f"target={tg} dist=300 snap=1 secs=10")
# 3. Shield and armour: dummie with shield
SH = lambda n: 'sv try { foreach ( x in GetNPCArray() ) if ( x.GetScriptName() == "rt_gun" ) { x.SetShieldHealthMax( ' + str(n) + ' ) ~ x.SetShieldHealth( ' + str(n) + ' ) } } catch ( e ) { printt( "[RT] sh err " + string( e ) ) } ~ AgentLink_Reply( "sh" )'
for g, w in (("r301", "rspn101"), ("kraber", "sniper"), ("mastiff", "mastiff")):
    add(f"sd_{g}", w, "none", SH(250) + "; down zoom; wait 0.9; tap attack; wait 1.2; tap attack; wait 1.2; tap attack; wait 0.5; up zoom", "target=body dist=200 snap=1 secs=9")
# 4. Drop and zeroing: fixed aim at the target's chest, no lift
for g, w in (("r301", "rspn101"), ("kraber", "sniper"), ("longbow", "dmr"), ("wingman", "wingman"), ("bocek", "bow")):
    for d in (1000, 2000, 3000, 4000, 6000):
        s = "down zoom; wait 1.0; " + "; ".join(["tap attack; wait 1.3"] * 6) + "; up zoom"
        add(f"dp_{g}_{d}", w, "none", s, f"target=body dist={d} snap=1 secs=14 lift={0.5 * 750 * 1.3 * (d / 29000) ** 2:.2f}")
# 5. Flinch: the player takes damage
TD = lambda a: 'sv try { entity p = GetPlayerArray()[0] ~ p.SetMaxHealth( 1000 ) ~ p.SetHealth( 1000 ) ~ p.TakeDamage( ' + str(a) + ', null, null, { damageSourceId = eDamageSourceId.mp_weapon_rspn101 } ) } catch ( e ) { printt( "[RT] td err " + string( e ) ) } ~ AgentLink_Reply( "td" )'
for r in (1, 2, 3):
    add(f"fl_hip_{r}", "rspn101", "none", "wait 0.5; " + TD(15) + "; wait 1.5; " + TD(60) + "; wait 1.5", "secs=7")
    add(f"fl_ads_{r}", "rspn101", "none", "down zoom; wait 0.8; " + TD(15) + "; wait 1.5; " + TD(60) + "; wait 1.2; up zoom", "secs=7")
# 6. Table end and loop: long clips
CLX = 'sv try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( 90 ) } catch ( e ) { printt( "[RT] cx err " + string( e ) ) } ~ AgentLink_Reply( "cx" )'
add("lp_r301", "rspn101", "bullets_mag_l4", CLX + "; wait 0.2; hold attack 5; wait 1", "secs=10 stock=300")
add("lp_spitfire", "lmg", "highcal_mag_l4", CLX + "; wait 0.2; hold attack 7; wait 1", "secs=12 stock=300")
add("lp_r99", "r97", "bullets_mag_l4", CLX + "; wait 0.2; hold attack 4; wait 1", "secs=9 stock=300")
add("lp_flatline", "vinson", "highcal_mag_l4", CLX + "; wait 0.2; hold attack 5; wait 1", "secs=10 stock=300")
# 7. P2020 ADS fraction and Wingman rise: already in st_ and sw_; add long-settle ADS single shots, no drift overlap is possible only by averaging
for r in range(1, 7):
    add(f"fx_p2020_{r}", "semipistol", "none", "down zoom; wait 1.0; tap attack; wait 0.7; up zoom", "secs=4")
print("\n".join(L))
