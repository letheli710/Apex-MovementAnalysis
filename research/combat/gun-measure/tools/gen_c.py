#!/usr/bin/env python3
"""Cases for C: reload, switching, melee, raise delays. py -3 -I gen_c.py > cases_c.txt"""
L = []
def add(tag, w, m, s, k="secs=12 stock=150"): L.append(f"{tag}|{w}|{m}|{s}|{k}")
CL1 = 'sv try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( 1 ) } catch ( e ) { } ~ AgentLink_Reply( "c1" )'
GIVE2 = 'sv try { entity p = GetPlayerArray()[0] ~ entity w2 = p.GiveWeapon( "mp_weapon_@@", WEAPON_INVENTORY_SLOT_PRIMARY_1, [] ) ~ w2.SetWeaponPrimaryClipCount( w2.GetWeaponPrimaryClipCountMax() ) } catch ( e ) { printt( "[RT] give err " + string( e ) ) } ~ AgentLink_Reply( "g2" )'
FULL = 'sv try { foreach ( w in GetPlayerArray()[0].GetMainWeapons() ) { w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() ) } } catch ( e ) { } ~ AgentLink_Reply( "f" )'
# Reload: tactical (two shots first) and empty (clip 1, one shot, then reload), per family.
RG = {"r301": "rspn101", "r99": "r97", "spitfire": "lmg", "p2020": "semipistol", "hemlok": "hemlok", "havoc": "energy_ar", "eva8": "shotgun", "mastiff": "mastiff", "peacekeeper": "energy_shotgun", "kraber": "sniper", "longbow": "dmr", "wingman": "wingman", "r3030": "3030", "lstar": "lstar", "devotion": "esaw", "bocek": "bow", "chargerifle": "defender", "volt": "volt_smg", "g7": "g2", "tripletake": "doubletake"}
for g, w in RG.items():
    for r in (1, 2):
        add(f"rt_{g}_emp_{r}", w, "none", f"{CL1}; wait 0.3; tap attack; wait 0.1; tap attack; wait 7; wait 0.3")
# +reload does nothing in this build through ClientCommand. A tactical reload is reached with Anvil: 2 ammo per shot, clip 1 is not empty but cannot fire.
for g, w, m in (("r301", "rspn101", "hopup_highcal_rounds,altfire_highcal"), ("flatline", "vinson", "hopup_highcal_rounds,altfire_highcal"), ("alternator", "alternator_smg", "hopup_double_tap,altfire_double_tap")):
    for r in (1, 2, 3):
        add(f"rt_{g}_tac_{r}", w, m, f"{CL1}; wait 0.3; tap attack; wait 7")
        add(f"rt_{g}_emp_{r}", w, "none", f"{CL1}; wait 0.3; tap attack; wait 0.1; tap attack; wait 7")
# Boosted Loader, Dual Shell, overload through the empty path
for g, w, ms in (("hemlok", "hemlok", ("hopup_smart_reload", "fast_reload_mod")), ("wingman", "wingman", ("hopup_smart_reload", "fast_reload_mod")), ("mastiff", "mastiff", ("hopup_dual_loader",)), ("r3030", "3030", ("hopup_dual_loader", "segmented_speed_load")), ("tripletake", "doubletake", ("hopup_smart_reload",))):
    for m in ms:
        add(f"rt_{g}+{m}_emp_1", w, m, f"{CL1}; wait 0.3; tap attack; wait 0.1; tap attack; wait 7")
# Reload cancels at 0.5 s: R-301, Spitfire, Mastiff (segmented), Wingman.
for g, w, late in (("r301", "rspn101", 1.9), ("mastiff", "mastiff", 1.5), ("wingman", "wingman", 1.5)):
    base = CL1 + "; wait 0.3; tap attack; wait 0.1; tap attack; wait "
    for at in (0.5, late):
        pre = base + f"{at}; "
        G2 = GIVE2.replace("@@", "wingman" if g != "wingman" else "rspn101")
        add(f"rc_{g}_sprint_{at}", w, "none", pre + "down forward; down speed; wait 1.2; up speed; up forward; wait 4")
        add(f"rc_{g}_swap_{at}", w, "none", G2 + "; " + pre + "cmd weaponSelectPrimary1; wait 1.2; cmd weaponSelectPrimary0; wait 4")
        add(f"rc_{g}_melee_{at}", w, "none", pre + "tap melee; wait 4")
        add(f"rc_{g}_jump_{at}", w, "none", pre + "tap jump; wait 4")
        add(f"rc_{g}_ads_{at}", w, "none", pre + "down zoom; wait 1; up zoom; wait 3")
        add(f"rc_{g}_fire_{at}", w, "none", pre + "tap attack; wait 3")
# Move speed while reloading
add("rm_r301_walk", "rspn101", "none", CL1 + "; wait 0.3; down forward; wait 0.9; tap attack; wait 0.1; tap attack; wait 3.4; up forward; wait 0.4")
add("rm_r301_sprint", "rspn101", "none", CL1 + "; wait 0.3; down forward; down speed; wait 1.0; tap attack; wait 0.1; tap attack; wait 3.4; up speed; up forward; wait 0.4")
# Switching: first deploy, repeat swaps, immediate fire after a swap.
for g, w, o in (("r301", "rspn101", "wingman"), ("wingman", "wingman", "rspn101"), ("p2020", "semipistol", "lmg"), ("spitfire", "lmg", "semipistol"), ("kraber", "sniper", "r97"), ("eva8", "shotgun", "r97"), ("r99", "r97", "sniper")):
    G2 = GIVE2.replace("@@", o)
    add(f"ws_{g}_swap", w, "none", G2 + "; wait 1.5; cmd weaponSelectPrimary1; wait 1.8; cmd weaponSelectPrimary0; wait 1.8; cmd weaponSelectPrimary1; wait 1.8; cmd weaponSelectPrimary0; wait 1.8")
    add(f"ws_{g}_swapfire", w, "none", G2 + "; wait 1.5; cmd weaponSelectPrimary1; down attack; wait 1.6; up attack; cmd weaponSelectPrimary0; down attack; wait 1.6; up attack; wait 0.5")
    add(f"ws_{g}_ads", w, "none", G2 + "; wait 1.5; down zoom; wait 0.8; cmd weaponSelectPrimary1; wait 1.6; up zoom; wait 0.8")
    add(f"ws_{g}_fireswap", w, "none", G2 + "; wait 1.5; down attack; wait 0.5; cmd weaponSelectPrimary1; wait 1.0; up attack; wait 0.6")
    add(f"ws_{g}_cycle", w, "none", G2 + "; wait 1.5; tap weaponcycle; wait 1.5; tap weaponcycle; wait 1.5")
# Melee and knife
for g, w in (("r301", "rspn101"), ("wingman", "wingman"), ("kraber", "sniper")):
    add(f"ml_{g}_tap", w, "none", "wait 1.0; tap melee; wait 2.5", "secs=9 target=body dist=50 snap=1")
    add(f"ml_{g}_fire", w, "none", "wait 1.0; tap melee; wait 0.1; down attack; wait 1.5; up attack; wait 0.5", "secs=9 target=body dist=50 snap=1")
    add(f"ml_{g}_miss", w, "none", "wait 1.0; tap melee; wait 2.5", "secs=8")
    add(f"ml_{g}_ads", w, "none", "down zoom; wait 0.8; tap melee; wait 1.5; up zoom; wait 0.5", "secs=8")
    add(f"ml_{g}_selmelee", w, "none", 'wait 0.5; cmd weaponSelectPrimary2; wait 2; cmd weaponSelectPrimary0; wait 1.5', "secs=8")
# Ordnance
GN = 'sv try { GetPlayerArray()[0].GiveOffhandWeapon( "mp_weapon_frag_grenade", OFFHAND_ORDNANCE, [] ) } catch ( e ) { printt( "[RT] gren err " + string( e ) ) } ~ AgentLink_Reply( "gn" )'
add("or_r301", "rspn101", "none", GN + "; wait 0.8; cmd weaponSelectOrdnance; wait 1.5; cmd weaponSelectPrimary0; wait 1.5", "secs=8")
# Raise delays: first shot after sprint, after slide, after a jump; the delay is first kick minus the press
for g, w in (("r301", "rspn101"), ("p2020", "semipistol"), ("spitfire", "lmg"), ("kraber", "sniper"), ("r99", "r97"), ("wingman", "wingman"), ("eva8", "shotgun"), ("mastiff", "mastiff")):
    for r in (1, 2, 3):
        add(f"ra_{g}_sprint_{r}", w, "none", "down forward; down speed; wait 1.3; down attack; wait 0.9; up attack; up speed; up forward; wait 0.4", "secs=7")
        add(f"ra_{g}_slide_{r}", w, "none", "down forward; down speed; wait 1.2; down duck; wait 0.25; down attack; wait 0.9; up attack; up duck; up speed; up forward; wait 0.4", "secs=7")
        add(f"ra_{g}_stand_{r}", w, "none", "wait 0.6; down attack; wait 0.7; up attack; wait 0.3", "secs=6")
        add(f"ra_{g}_adsprint_{r}", w, "none", "down forward; down speed; wait 1.3; down zoom; wait 0.8; up zoom; up speed; up forward; wait 0.4", "secs=7")
print("\n".join(L))
