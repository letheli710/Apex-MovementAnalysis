#!/usr/bin/env python3
"""Reload cases, second go. The first go left the player's ammo pools at 0, so guns that use a pool had nothing to reload from and neither +reload nor the empty path did anything.
Every case fills the pools first. Tactical uses the reload key. py -3 -I gen_c2.py cases_c.txt > cases_c2.txt"""
import re, sys
L = []
def add(tag, w, m, s, k="secs=12 stock=150"): L.append(f"{tag}|{w}|{m}|{s}|{k}")
POOL = 'sv try { entity p = GetPlayerArray()[0] ~ p.AmmoPool_SetCapacity( 999 ) ~ for ( int i = 0 ~ i < 8 ~ i++ ) { try { p.AmmoPool_SetCount( i, 300 ) } catch ( e1 ) { } } } catch ( e ) { printt( "[RT] rx err " + string( e ) ) } ~ AgentLink_Reply( "rx" )'
CLIP = lambda n: 'sv try { GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ).SetWeaponPrimaryClipCount( ' + str(n) + ' ) } catch ( e ) { } ~ AgentLink_Reply( "c" )'
GIVE2 = 'sv try { entity p = GetPlayerArray()[0] ~ entity w2 = p.GiveWeapon( "mp_weapon_@@", WEAPON_INVENTORY_SLOT_PRIMARY_1, [] ) ~ w2.SetWeaponPrimaryClipCount( w2.GetWeaponPrimaryClipCountMax() ) } catch ( e ) { printt( "[RT] give err " + string( e ) ) } ~ AgentLink_Reply( "g" )'
TAC = "wait 0.3; tap attack; wait 0.4; tap attack; wait 0.5; tap reload"
EMP = CLIP(1) + "; wait 0.3; tap attack; wait 0.1; tap attack"
seen = {}
for l in open(sys.argv[1], encoding="utf-8"):
    g = re.match(r"rt_(\w+?)_emp_1\|([^|]+)\|none\|", l)
    if g: seen[g[1]] = g[2]
seen.setdefault("flatline", "vinson"); seen.setdefault("alternator", "alternator_smg")
for g, w in seen.items():
    for r in (1, 2):
        add(f"rt_{g}_tac_{r}", w, "none", f"{POOL}; {TAC}; wait 7")
        add(f"rt_{g}_emp_{r}", w, "none", f"{POOL}; {EMP}; wait 7")
# Attachments that change the reload
for g, w, ms in (("hemlok", "hemlok", ("hopup_smart_reload",)), ("wingman", "wingman", ("hopup_smart_reload",)), ("mastiff", "mastiff", ("hopup_dual_loader",)), ("r3030", "3030", ("hopup_dual_loader", "segmented_speed_load")), ("peacekeeper", "energy_shotgun", ("hopup_kinetic_loader",)), ("r301", "rspn101", ("stock_tactical_l1", "stock_tactical_l3", "bullets_mag_l3", "corrupted_mag"))):
    for m in ms:
        add(f"rt_{g}+{m}_tac_1", w, m, f"{POOL}; {TAC}; wait 7")
        add(f"rt_{g}+{m}_emp_1", w, m, f"{POOL}; {EMP}; wait 7")
# Boosted Loader's window: reload from a low clip
for g, w in (("hemlok", "hemlok"), ("wingman", "wingman")):
    for n in (1, 3, 5):
        add(f"rb_{g}_clip{n}", w, "hopup_smart_reload", f"{POOL}; {CLIP(n)}; wait 0.3; tap reload; wait 5; tap attack; wait 0.5")
# Cancels: at 0.5 s, before the ammo goes in, and after
for g, w, ats in (("r301", "rspn101", (0.5, 1.9, 2.3)), ("spitfire", "lmg", (0.5, 2.0, 3.0)), ("mastiff", "mastiff", (0.5, 1.5)), ("wingman", "wingman", (0.5, 1.5))):
    G2 = GIVE2.replace("@@", "wingman" if g != "wingman" else "rspn101")
    for at in ats:
        pre = f"{POOL}; {TAC}; wait {at}; "
        add(f"rc_{g}_sprint_{at}", w, "none", pre + "down forward; down speed; wait 1.2; up speed; up forward; wait 4")
        add(f"rc_{g}_swap_{at}", w, "none", f"{G2}; " + pre + "cmd weaponSelectPrimary1; wait 1.2; cmd weaponSelectPrimary0; wait 4")
        add(f"rc_{g}_melee_{at}", w, "none", pre + "tap melee; wait 4")
        add(f"rc_{g}_jump_{at}", w, "none", pre + "tap jump; wait 4")
        add(f"rc_{g}_ads_{at}", w, "none", pre + "down zoom; wait 1; up zoom; wait 3")
        add(f"rc_{g}_fire_{at}", w, "none", pre + "tap attack; wait 3")
# Move speed and ADS during the reload
add("rm_r301_walk", "rspn101", "none", f"{POOL}; down forward; wait 0.5; tap reload; wait 0.1; {CLIP(5)}; wait 3.2; up forward; wait 0.4")
add("rm_r301_tacwalk", "rspn101", "none", f"{POOL}; {TAC}; down forward; wait 3.0; up forward; wait 0.6")
add("rm_r301_tacsprint", "rspn101", "none", f"{POOL}; down forward; down speed; wait 1.0; tap attack; wait 0.4; tap attack; wait 0.3; tap reload; wait 3.2; up speed; up forward; wait 0.4")
add("rm_wingman_tacwalk", "wingman", "none", f"{POOL}; wait 0.3; tap attack; wait 0.5; tap attack; wait 0.5; tap reload; down forward; wait 2.5; up forward; wait 0.6")
print("\n".join(L))
