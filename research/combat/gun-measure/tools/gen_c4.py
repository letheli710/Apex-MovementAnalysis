#!/usr/bin/env python3
"""Reload for the guns the shot-then-reload route missed: slow guns were not ready for the second press, charge guns did not fire from a tap. The clip is set directly and the reload key pressed.
Also ADS and fire timing inside the reload, and the first fire point on more guns. py -3 -I gen_c4.py > cases_c4.txt"""
L = []
def add(tag, w, m, s, k="secs=12 stock=150"): L.append(f"{tag}|{w}|{m}|{s}|{k}")
POOL = 'sv try { entity p = GetPlayerArray()[0] ~ p.AmmoPool_SetCapacity( 999 ) ~ for ( int i = 0 ~ i < 8 ~ i++ ) { try { p.AmmoPool_SetCount( i, 300 ) } catch ( e1 ) { } } } catch ( e ) { printt( "[RT] rx err " + string( e ) ) } ~ AgentLink_Reply( "rx" )'
CLIP = lambda n: 'sv try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( ' + str(n) + ' ) } catch ( e ) { printt( "[RT] rx err " + string( e ) ) } ~ AgentLink_Reply( "c" )'
G = {"havoc": ("energy_ar", 9), "chargerifle": ("defender", 3), "bocek": ("bow", 0), "lstar": ("lstar", 5), "eva8": ("shotgun", 4), "mastiff": ("mastiff", 2), "kraber": ("sniper", 2), "longbow": ("dmr", 3), "tripletake": ("doubletake", 3), "sentinel": ("sentinel", 2), "rampage": ("dragon_lmg", 10), "car": ("car", 10), "re45": ("autopistol", 8), "nemesis": ("nemesis", 10), "prowler": ("pdw", 10), "ehemlok": ("auto_hemlok", 10), "mozambique": ("shotgun_pistol", 2)}
for g, (w, half) in G.items():
    for r in (3, 4):
        add(f"rt_{g}_emp_{r}", w, "none", f"{POOL}; {CLIP(0)}; wait 0.3; tap reload; wait 7")
        if half: add(f"rt_{g}_tac_{r}", w, "none", f"{POOL}; {CLIP(half)}; wait 0.3; tap reload; wait 7")
# Is the gun ready before the animation ends: press fire at steps through the reload, R-301 and Wingman
for g, w, ats in (("r301", "rspn101", (1.2, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0, 2.2)), ("wingman", "wingman", (1.3, 1.5, 1.6, 1.7, 1.8, 2.0)), ("spitfire", "lmg", (2.0, 2.4, 2.7, 2.9, 3.1))):
    for at in ats:
        add(f"rf_{g}_{at}", w, "none", f"{POOL}; {CLIP(5)}; wait 0.3; tap reload; wait {at}; down attack; wait 0.6; up attack; wait 1")
# ADS pressed in the reload: does the view zoom
add("ra2_r301_ads", "rspn101", "none", f"{POOL}; {CLIP(5)}; wait 0.3; tap reload; wait 0.5; down zoom; wait 3; up zoom; wait 0.5")
add("ra2_wingman_ads", "wingman", "none", f"{POOL}; {CLIP(3)}; wait 0.3; tap reload; wait 0.5; down zoom; wait 3; up zoom; wait 0.5")
print("\n".join(L))
