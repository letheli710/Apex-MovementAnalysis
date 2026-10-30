"""W1 plans: test targets (hsd_diag_npc.gnut). See ../expansion/w1/TARGETS.md.
mp_lf_stacks spawn: player at (24, -1864, 1) facing yaw 90 (+y); ~570 u of open floor ahead."""
from plans import C, W, U


def w1_targets():
    """Spawn each target kind, shoot the static one, walk / slide / chase, hostile on/off, cleanup.
    ids in spawn order: 1 static soldier, 2 spectre (walk, then chase), 3 stalker (slide), 4 hostile soldier."""
    return [
        C("hsd_info"), C("hsd_npc_nav"), C("hsd_hp 1000"),
        C("hsd_tag spawn"),
        C("hsd_npc soldier static 24 -1600 1 -90 500"),
        C("hsd_npc spectre idle -300 -1350 1 -90"),
        C("hsd_npc stalker idle 300 -1450 1 -90"),
        W(1.5),
        C("hsd_npc_list"), C("hsd_npc_hp all"),
        C("hsd_npc_walk 2 300 -1350 1 1"),
        C("hsd_npc_slide 3 -300 -1450 1 150"),
        # shoot the static soldier: aim at its chest from the spawn point (264 u ahead)
        C("hsd_tag shoot"),
        C("hsd_weapon mp_weapon_rspn101"), W(1.5),
        C("hsd_setup 24 -1864 1 0 0 0 4 90"), W(0.5),
        C("+attack"), W(0.8), C("-attack"), W(0.5),
        C("hsd_npc_hp 1"),
        W(3.0),
        # hostile soldier: shoots the player; then passive
        C("hsd_tag hostile"),
        C("hsd_npc soldier hostile 400 -1600 1 -135 300"), W(6.0),
        C("hsd_npc_hp all"),
        C("hsd_tag passive"), C("hsd_npc_passive 4 1"), W(4.0),
        # the spectre leaves its path and chases the player
        C("hsd_tag chase"), C("hsd_npc_chase 2 1"), W(5.0),
        C("hsd_npc_stop all"), W(1.0),
        C("hsd_npc_list"),
        C("hsd_tag kill"), C("hsd_npc_kill all"), W(0.5), C("hsd_npc_list"),
        C("hsd_tag -"),
    ]


def w1_hostile():
    """Hostile soldier and spectre shoot the player (PDMG names the attacker id), passive stops
    them, active again resumes; then a passive spectre chases the player (who stands in the open)."""
    return [
        C("hsd_hp 5000"),
        C("hsd_setup 24 -1700 1 0 0 0 0 90"), U("air", 0, 0.5), U("ground"),
        C("hsd_tag hostile"),
        C("hsd_npc soldier hostile 300 -1400 1 -135 300"),
        C("hsd_npc spectre hostile -300 -1400 1 -45 300"),
        W(8.0), C("hsd_npc_hp all"), C("hsd_hp 5000"),
        C("hsd_tag passive"), C("hsd_npc_passive all 1"), W(8.0), C("hsd_npc_hp all"),
        C("hsd_tag active"), C("hsd_npc_passive all 0"), W(6.0),
        C("hsd_tag cleanup"), C("hsd_npc_kill all"), W(0.5),
        C("hsd_tag chase"),
        C("hsd_npc spectre idle -300 -1350 1 -90"), W(1.0),
        C("hsd_npc_chase 3 1 100"), W(6.0),
        C("hsd_setup 300 -1400 1 0 0 0 0 90"), U("air", 0, 0.5), U("ground"), W(6.0),
        C("hsd_npc_list"), C("hsd_npc_kill all"),
        C("hsd_tag -"),
    ]


def w1_passive():
    """Passive check after the weapon-taking fix: two hostile spectres and a soldier, passive, active.
    Also a passive (idle) spectre in view that must never shoot."""
    return [
        C("hsd_hp 5000"),
        C("hsd_setup 24 -1500 1 0 0 0 0 90"), U("air", 0, 0.5), U("ground"),
        C("hsd_tag hostile"),
        C("hsd_npc spectre hostile -300 -1350 1 -45 300"),
        C("hsd_npc spectre hostile 300 -1350 1 -135 300"),
        C("hsd_npc soldier hostile 0 -1300 1 -90 300"),
        C("hsd_npc spectre idle 200 -1550 1 180 300"),
        W(6.0), C("hsd_hp 5000"),
        C("hsd_tag passive"), C("hsd_npc_passive 1 1"), C("hsd_npc_passive 2 1"), C("hsd_npc_passive 3 1"), W(10.0),
        C("hsd_tag active"), C("hsd_npc_passive 1 0"), W(5.0),
        C("hsd_npc_list"), C("hsd_npc_kill all"),
        C("hsd_tag -"),
    ]
