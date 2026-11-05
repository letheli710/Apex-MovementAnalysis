#!/usr/bin/env python3
"""Writes cases for A2 (attachments in play). py -3 -I gen_a2.py > cases_a2.txt"""
AUTO = "down zoom; wait 0.7; hold attack 1.0; wait 0.8; up zoom; wait 0.3"
AUTOH = "wait 0.3; hold attack 1.0; wait 0.8"
def taps(n, gap): return "; ".join(["tap attack; wait %g" % gap] * n)
def semi(n, gap, ads=True): return ("down zoom; wait 0.8; " if ads else "wait 0.3; ") + taps(n, gap) + ("; wait 0.5; up zoom; wait 0.2" if ads else "; wait 0.5")
T = "target=body dist=150 snap=1 secs=12"
TH = "target=head dist=150 snap=1 secs=12"
L = []
def add(tag, w, m, s, k=T): L.append(f"{tag}|{w}|{m}|{s}|{k}")
# Rate and spin: Turbocharger
for g, w in (("havoc", "energy_ar"), ("devotion", "esaw"), ("nemesis", "nemesis")):
    for m in ("none", "hopup_turbocharger"):
        add(f"tb_{g}_{m}", w, m, "wait 0.3; hold attack 2.0; wait 0.8", "secs=8")
add("tb_chargerifle_none", "defender", "none", "wait 0.3; hold attack 2.0; wait 0.8", "secs=8")
add("tb_chargerifle_turbo", "defender", "hopup_turbocharger", "wait 0.3; hold attack 2.0; wait 0.8", "secs=8")
# Selectfire
for g, w in (("prowler", "pdw"), ("chargerifle", "defender")):
    for m in ("none", "hopup_selectfire", "hopup_selectfire,altfire_selectfire"):
        add(f"sf_{g}_{m.split(',')[-1]}", w, m, "wait 0.3; hold attack 1.4; wait 0.8", T)
# Anvil
for g, w in (("r301", "rspn101"), ("flatline", "vinson")):
    for m in ("none", "hopup_highcal_rounds", "hopup_highcal_rounds,altfire_highcal", "altfire"):
        add(f"av_{g}_{m.split(',')[-1]}", w, m, "wait 0.3; hold attack 1.2; wait 0.8", T)
# Double Tap
for g, w, gap in (("eva8", "shotgun", 0.9), ("g7", "g2", 0.5), ("alternator", "alternator_smg", 0.3)):
    for m in ("none", "hopup_double_tap", "hopup_double_tap,altfire_double_tap"):
        add(f"dt_{g}_{m.split(',')[-1]}", w, m, semi(4, gap, False), T)
# Hammerpoint, Skullpiercer
for g, w, gap in (("p2020", "semipistol", 0.2), ("re45", "autopistol", 0.1), ("mozambique", "shotgun_pistol", 0.5)):
    for m in ("none", "hopup_unshielded_dmg"):
        add(f"hp_{g}_{m}", w, m, semi(5, gap), T)
for g, w, gap in (("longbow", "dmr", 0.9), ("wingman", "wingman", 0.5), ("r3030", "3030", 0.9)):
    for m in ("none", "hopup_headshot_dmg"):
        add(f"sk_{g}_{m}", w, m, semi(4, gap), TH)
# Shatter
for g, w, gap in (("r3030", "3030", 0.9), ("bocek", "bow", 1.3)):
    for m in ("none", "hopup_shatter_rounds", "hopup_shatter_rounds,shatter_rounds_hipfire", "shatter_rounds_hipfire"):
        tag = m.split(",")[-1] + ("_both" if "," in m else "")
        add(f"st_{g}_{tag}_hip", w, m, semi(3, gap, False))
        add(f"st_{g}_{tag}_ads", w, m, semi(3, gap))
# Choke
for g, w, gap in (("peacekeeper", "energy_shotgun", 1.2), ("tripletake", "doubletake", 1.0)):
    for m in ("none", "choke", "kinetic_choke", "hopup_energy_choke", "hopup_kinetic_choke"):
        add(f"ck_{g}_{m}", w, m, semi(3, gap))
# Disruptor against shield
SH = 'sv try { foreach ( n in GetNPCArray() ) if ( n.GetScriptName() == "rt_gun" ) { n.SetShieldHealthMax( 5000 ) ~ n.SetShieldHealth( 5000 ) } } catch ( e ) { } ~ AgentLink_Reply( "shield" ); '
for g, w, gap in (("alternator", "alternator_smg", 0.2), ("re45", "autopistol", 0.2), ("peacekeeper", "energy_shotgun", 1.2)):
    for m in ("none", "hopup_shield_breaker"):
        add(f"dr_{g}_{m}", w, m, SH + semi(5, gap))
# Reload behaviour
R = "wait 0.3; hold attack 0.5; wait 0.4; tap reload; wait 4; tap attack; wait 0.5"
RE = "hold attack 3.2; wait 5"
for g, w, ms in (("hemlok", "hemlok", ("none", "hopup_smart_reload", "fast_reload_mod", "overloaded_ammo")), ("wingman", "wingman", ("none", "hopup_smart_reload", "fast_reload_mod")),
                 ("mastiff", "mastiff", ("none", "hopup_dual_loader")), ("r3030", "3030", ("none", "hopup_dual_loader", "segmented_speed_load")), ("peacekeeper", "energy_shotgun", ("none", "hopup_kinetic_loader")), ("tripletake", "doubletake", ("none",))):
    for m in ms:
        add(f"rl_{g}_{m}", w, m, "wait 0.3; tap attack; wait 1.0; tap attack; wait 1.0; tap reload; wait 5.5; tap attack; wait 0.3", "secs=11 stock=120")
# Kinetic: slide with a part-empty gun
for g, w in (("peacekeeper", "energy_shotgun"),):
    add(f"kn_{g}", w, "hopup_kinetic_loader", "tap attack; wait 1.2; tap attack; wait 1.2; down forward; down speed; wait 1.2; tap duck; down duck; wait 1.5; up duck; up speed; up forward; wait 0.5", "secs=8 stock=120")
# Energize, tempo
add("en_sentinel_none", "sentinel", "none", semi(3, 2.2))
add("en_sentinel_energized", "sentinel", "energized", semi(3, 2.2))
add("en_rampage_energized", "dragon_lmg", "energized", AUTOH)
add("en_rampage_none", "dragon_lmg", "none", AUTOH)
add("tm_sentinel", "sentinel", "hopup_marksmans_tempo", semi(4, 1.2))
add("tm_bocek", "bow", "hopup_marksmans_tempo", semi(4, 0.9))
# Handling attachments in play: R-301 unless noted
for m in ("none", "barrel_stabilizer_l1", "barrel_stabilizer_l3", "barrel_stabilizer_l4_flash_hider", "corrupted_barrel"):
    for r in (1, 2, 3):
        add(f"bs_r301_{m}_{r}", "rspn101", m, AUTO, "secs=8")
for m in ("none", "stock_tactical_l1", "stock_tactical_l3", "corrupted_tactical_stock"):
    add(f"tk_r301_{m}", "rspn101", m, "down zoom; wait 0.8; up zoom; wait 0.8; hold attack 0.4; wait 0.3; tap reload; wait 3.5", "secs=9")
for m in ("none", "laser_sight_l1", "laser_sight_l3", "corrupted_laser"):
    add(f"ls_r99_{m}", "r97", m, "wait 0.3; hold attack 1.0; wait 0.8", "secs=6")
for m in ("none", "stock_sniper_l1", "stock_sniper_l3", "corrupted_stock_sniper"):
    add(f"sn_g7_{m}", "g2", m, "down zoom; wait 0.9; up zoom; wait 0.8; tap attack; wait 0.5", "secs=6")
# Optics: FOV path
for w, g, ms in (("rspn101", "r301", ("optic_cq_hcog_classic", "optic_cq_hcog_bruiser", "optic_cq_holosight", "optic_cq_holosight_variable", "optic_ranged_hcog", "optic_ranged_aog_variable", "optic_cq_threat")), ("g2", "g7", ("optic_sniper", "optic_sniper_variable", "optic_sniper_threat", "optic_ranged_aog_variable"))):
    for m in ("none",) + ms:
        add(f"op_{g}_{m}", w, m, "wait 0.3; down zoom; wait 1.1; up zoom; wait 0.8", "secs=5")
print("\n".join(L))
