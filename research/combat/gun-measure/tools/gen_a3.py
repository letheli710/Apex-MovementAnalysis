#!/usr/bin/env python3
"""A3: charged hop-ups, mode toggles, shield read-back. py -3 -I gen_a3.py > cases_a3.txt"""
L = []
def add(tag, w, m, s, k="target=body dist=150 snap=1 secs=12"): L.append(f"{tag}|{w}|{m}|{s}|{k}")
RD = 'sv string o = "" ~ try { foreach ( x in GetNPCArray() ) if ( x.GetScriptName() == "rt_gun" ) o += " shield=" + x.GetShieldHealth() + " hp=" + x.GetHealth() ~ printt( "[RT] rd" + o ) } catch ( e ) { } ~ AgentLink_Reply( o )'
SH = 'sv try { foreach ( x in GetNPCArray() ) if ( x.GetScriptName() == "rt_gun" ) { x.SetShieldHealthMax( 5000 ) ~ x.SetShieldHealth( 5000 ) } } catch ( e ) { printt( "[RT] sh err " + string( e ) ) } ~ AgentLink_Reply( "sh" )'
MODS = 'sv string o = "" ~ try { entity w = GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ) ~ foreach ( m in w.GetMods() ) o += m + "," } catch ( e ) { } ~ printt( "[RT] mods " + o ) ~ AgentLink_Reply( o )'
# Bocek: draw then release
for m in ("none", "hopup_shatter_rounds", "hopup_marksmans_tempo", "hopup_shatter_rounds,altfire_shatter"):
    for aim, zi in (("hip", ""), ("ads", "down zoom; wait 0.5; ")):
        add(f"bk_{m.split(',')[-1]}_{aim}", "bow", m, zi + "; ".join(["hold attack 0.8; wait 0.4"] * 3) + "; wait 0.5")
add("bk_tempo_fast", "bow", "hopup_marksmans_tempo", "; ".join(["hold attack 0.35; wait 0.15"] * 6) + "; wait 0.5")
add("bk_base_fast", "bow", "none", "; ".join(["hold attack 0.35; wait 0.15"] * 6) + "; wait 0.5")
# Disruptor and plain guns against a big shield: read the shield after 5 shots
for g, w, gap in (("alternator", "alternator_smg", 0.2), ("re45", "autopistol", 0.2), ("peacekeeper", "energy_shotgun", 1.3)):
    for m in ("none", "hopup_shield_breaker"):
        add(f"d2_{g}_{m}", w, m, SH + "; down zoom; wait 0.8; " + "; ".join([f"tap attack; wait {gap}"] * 5) + "; " + RD + "; up zoom")
for g, w, gap, m in (("r301", "rspn101", 0.2, "none"), ("kraber", "sniper", 1.3, "none"), ("p2020", "semipistol", 0.2, "hopup_unshielded_dmg"), ("p2020", "semipistol", 0.2, "none")):
    add(f"d2_{g}_{m}", w, m, SH + "; down zoom; wait 0.9; " + "; ".join([f"tap attack; wait {gap}"] * 5) + "; " + RD + "; up zoom")
# Tempo: taps at the rate limit
add("tm2_sentinel_none", "sentinel", "none", "; ".join(["tap attack; wait 0.5"] * 9) + "; wait 0.3")
add("tm2_sentinel_tempo", "sentinel", "hopup_marksmans_tempo", "; ".join(["tap attack; wait 0.5"] * 9) + "; wait 0.3")
add("tm2_sentinel_active", "sentinel", "marksmans_tempo_active", "; ".join(["tap attack; wait 0.5"] * 9) + "; wait 0.3")
# Choke: hold ADS and draw the charge, then read the pattern
for g, w in (("peacekeeper", "energy_shotgun"), ("tripletake", "doubletake")):
    for m in ("none", "choke", "kinetic_choke", "hopup_energy_choke", "hopup_kinetic_choke"):
        add(f"c2_{g}_{m}", w, m, "down zoom; wait 0.8; hold attack 1.2; wait 1.0; hold attack 1.2; wait 1.0; hold attack 1.2; wait 0.5; up zoom")
# Mode toggle keys: does a key change the mods? Print mods before and after.
for tag, w, m in (("r301_base", "rspn101", "none"), ("r301_anvil", "rspn101", "hopup_highcal_rounds"), ("prowler", "pdw", "hopup_selectfire"), ("g7", "g2", "hopup_double_tap"), ("havoc", "energy_ar", "hopup_selectfire"), ("3030", "3030", "hopup_shatter_rounds")):
    for key in ("use_alt", "weaponcycle"):
        add(f"tg_{tag}_{key}", w, m, f"wait 0.6; {MODS}; tap {key}; wait 1.2; {MODS}; hold attack 0.4; wait 0.5; tap {key}; wait 1.2; {MODS}", "secs=9")
# Optics that exist on these guns
for w, g, ms in (("r97", "r99", ("optic_cq_threat",)), ("sniper", "kraber", ("optic_toggle",)), ("dmr", "longbow", ("optic_sniper", "optic_sniper_variable", "optic_sniper_threat"))):
    for m in ms:
        add(f"o2_{g}_{m}", w, m, "wait 0.3; down zoom; wait 1.2; up zoom; wait 0.8", "secs=5")
add("o2_longbow_none", "dmr", "none", "wait 0.3; down zoom; wait 1.2; up zoom; wait 0.8", "secs=5")
add("o2_kraber_none", "sniper", "none", "wait 0.3; down zoom; wait 1.2; up zoom; wait 0.8", "secs=5")
print("\n".join(L))
