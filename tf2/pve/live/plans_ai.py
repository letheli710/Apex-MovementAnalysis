"""tf2-ai-live plans (run with ai_runner.py). Map mp_lf_stacks; player spawns at
(24, -1864, 1) facing +y. NPC commands: ../../expansion/w1/TARGETS.md (hsd_npc*) and
mod/HSD.TF2AILive/mod/scripts/vscripts/hsd_ailive.gnut (hsd_ai_*)."""
from plans import C, W, U

PLANS = ["ai_scout"]


def jumps(n):
    """n standing jumps in a row (airborne most of the time)."""
    out = []
    for _ in range(n):
        out += [C("+jump"), W(0.05), C("-jump"), U("air", 0, 1.0), U("ground", 0, 2.0)]
    return out


def ai_scout():
    """First run: does the extra mod load (AI init, MISS, NSHOT lines), what lethality and
    proficiency are in force, and the open floor around the spawn and the west wall."""
    return [
        C("hsd_info"), C("hsd_ai_info"), C("hsd_npc_nav"), C("hsd_hp 5000"),
        C("hsd_tag probe"),
        C("hsd_probe 3000"), W(0.3),
        C("hsd_setup 0 -1450 40 0 0 0 0 90"), W(1.2), C("hsd_probe 3000"), W(0.3),
        C("hsd_setup -880 -950 300 0 0 0 0 0"), W(1.5), C("hsd_probe 3000"), W(0.3),
        C("hsd_setup 400 -950 300 0 0 0 0 180"), W(1.5), C("hsd_probe 3000"), W(0.3),
        C("hsd_setup 24 -1864 1 0 0 0 0 90"), W(0.8),
        # hostile soldier (R-201), held 464 u ahead; player stands still
        C("hsd_tag stand_r201"),
        C("hsd_npc soldier hostile 24 -1400 1 -90 5000"),
        W(1.0), C("hsd_ai_hold 1 1"), C("hsd_ai_info"),
        W(7.0),
        C("hsd_tag jump_r201"),
        *jumps(8),
        # same soldier with an L-STAR (npc_miss_fast_player 1)
        C("hsd_tag give_lstar"), C("hsd_ai_give 1 mp_weapon_lstar"), C("hsd_ai_info"), W(6.0),
        C("hsd_tag jump_lstar"),
        *jumps(8),
        C("hsd_tag kill"), C("hsd_npc_kill all"), W(0.5),
        C("hsd_tag -"),
    ]


# ---- L-1 hit rate: player in front of the west wall (x = -960), NPCs to the east ----
# The player moves along y in [-1300, -600] at x = -880 (wall runs at x = -942), so the
# NPCs see lateral motion. Three NPCs of one kind at three ranges, held on their spots.
NPC_SPOTS = [(-580, -950), (-80, -1150), (520, -750)]  # ~300 / ~800 / ~1400 u from x = -880
PX = -880


def R(x, y, z=1, vx=0, vy=0, vz=0, yaw=0):
    return C("hsd_setup %g %g %g %g %g %g 0 %g" % (x, y, z, vx, vy, vz, yaw))


RELEASE = [C(c) for c in ("-forward", "-back", "-moveleft", "-moveright", "-speed", "-duck", "-jump")]


def seg_stand(sec):
    return [C("hsd_tag stand"), R(PX, -950, yaw=0), W(sec)]


def seg_walk(sec):
    out = [C("hsd_tag walk"), R(PX, -1100, yaw=0), W(0.3)]
    for i in range(int(sec / 4)):
        out += [C("+moveleft"), W(2.0), C("-moveleft"), C("+moveright"), W(2.0), C("-moveright")]
    return out + RELEASE


def seg_sprint(sec):
    out = [C("hsd_tag sprint")]
    for i in range(int(sec / 5.6)):
        out += [R(PX, -1300, yaw=90), W(0.2), C("+speed"), C("+forward"), W(2.6), C("-forward"), C("-speed"),
                R(PX, -600, yaw=270), W(0.2), C("+speed"), C("+forward"), W(2.6), C("-forward"), C("-speed")]
    return out + RELEASE


def seg_slide(sec):
    out = [C("hsd_tag slide")]
    for i in range(int(sec / 4.4)):
        for y, yaw in ((-1300, 90), (-600, 270)):
            out += [R(PX, y, yaw=yaw), W(0.2), C("+speed"), C("+forward"), W(0.45), C("+duck"), W(1.3),
                    C("-duck"), C("-forward"), C("-speed"), W(0.25)]
    return out + RELEASE


def seg_wallrun(sec):
    out = [C("hsd_tag wallrun")]
    for i in range(int(sec / 5.0)):
        out += [R(-942, -1400, 150, -40, 300, 0, yaw=90), U("air", 0, 0.5), U("wallrun", 0, 1), U("nowallrun", 0, 4),
                U("ground", 0, 3), W(0.1),
                R(-942, -500, 150, -40, -300, 0, yaw=270), U("air", 0, 0.5), U("wallrun", 0, 1), U("nowallrun", 0, 4),
                U("ground", 0, 3), W(0.1)]
    return out + RELEASE


def seg_air(sec):
    return [C("hsd_tag air"), R(PX, -950, yaw=0), W(0.3)] + jumps(int(sec / 0.85)) + [W(0.3)]


def ai_hit(kind, weapon=None, sec=24):
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000"), C("hsd_tag setup"), R(PX, -950, yaw=0), W(0.5)]
    for x, y in NPC_SPOTS:
        s += [C("hsd_trace %d %d 60 %d -1300 60" % (x, y, PX)), C("hsd_trace %d %d 60 %d -600 60" % (x, y, PX)),
              C("hsd_trace %d %d 60 -942 -1400 250" % (x, y)), C("hsd_trace %d %d 60 -942 -500 250" % (x, y))]
    for i, (x, y) in enumerate(NPC_SPOTS):
        s += [C("hsd_npc %s hostile %d %d 1 180 50000" % (kind, x, y))]
    s += [W(1.0), C("hsd_ai_hold all 1")]
    if weapon:
        s += [C("hsd_ai_give all %s" % weapon)]
    s += [C("hsd_ai_info"), C("hsd_tag warmup"), W(12.0)]
    for seg in (seg_stand, seg_walk, seg_sprint, seg_slide, seg_wallrun, seg_air):
        s += seg(sec)
    s += [C("hsd_tag stand2"), R(PX, -950, yaw=0), W(8.0), C("hsd_npc_list"), C("hsd_ai_info"),
          C("hsd_tag kill"), C("hsd_npc_kill all"), W(0.3), C("hsd_tag -")]
    return s


def ai_hit_soldier():
    return ai_hit("soldier")


def ai_hit_spectre():
    return ai_hit("spectre")


def ai_hit_stalker():
    return ai_hit("stalker")


PLANS += ["ai_hit_soldier", "ai_hit_spectre", "ai_hit_stalker"]


# ---- L-3 / L-4 / L-5 perception ----
# A fresh soldier per case, spawned blind (senses off) at NPC_P facing +x, held on its spot;
# the player stands at the case position; senses go on at the "notice_*" tag. The NPC log
# (NENEMY / NSEE / NSTATE / NSCHED / NSHOT / NP yaw) gives notice, turn and first-shot times.
NPC_P = (-700, -950)


def _ring(dist, ang):
    import math
    return (NPC_P[0] + dist * math.cos(math.radians(ang)), NPC_P[1] + dist * math.sin(math.radians(ang)))


NOTICE_CASES = [  # name, distance, angle from the NPC's forward (deg), cloak seconds
    ("front250", 250, 0, 0), ("front800", 800, 0, 0), ("front1400", 1400, 0, 0),
    ("side45_500", 500, 45, 0), ("side60_500", 500, -60, 0), ("side100_400", 400, 100, 0),
    ("back180_200", 200, 180, 0),
    ("cloak_front400", 400, 0, 12), ("cloak_front900", 900, 0, 12),
]


def notice_case(name, dist, ang, cloak, wait=6.0):
    x, y = _ring(dist, ang)
    face = (ang + 180) % 360  # player looks at the NPC
    s = [C("hsd_tag place_" + name), R(x, y, yaw=face), W(0.3)]
    if cloak:
        s += [C("hsd_ai_cloak %d" % cloak), W(1.2)]
    s += [C("hsd_ai_class npc_soldier - %d %d 1 0 1" % NPC_P), W(1.5), C("hsd_ai_hold last 1"), W(0.3),
          C("hsd_tag notice_" + name), C("hsd_ai_sense last 1"), W(wait),
          C("hsd_ai_kill last"), W(0.3)]
    if cloak:
        s += [C("hsd_ai_cloak 0"), W(0.5)]
    return s


HIDE_SPOTS = [(-650, -1650), (-500, -200), (-1100, -950)]


def ai_percept():
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000"), C("hsd_tag setup"), R(-300, -950, yaw=180), W(0.5)]
    for hx, hy in HIDE_SPOTS:
        s += [C("hsd_trace %d %d 60 %d %d 40" % (NPC_P[0], NPC_P[1], hx, hy)),
              C("hsd_trace %d %d 60 %d %d 40" % (-300, -950, hx, hy))]
    for case in NOTICE_CASES:
        s += notice_case(*case)
    # L-4 forget: engaged soldier (not held), player breaks line of sight at a hide spot
    for i, (hx, hy) in enumerate(HIDE_SPOTS):
        s += [C("hsd_tag engage%d" % i), R(-300, -950, yaw=180), W(0.3),
              C("hsd_ai_class npc_soldier - %d %d 1 0 0" % NPC_P), W(7.0),
              C("hsd_tag hide%d" % i), R(hx, hy, 40, yaw=0), W(14.0),
              C("hsd_tag back%d" % i), R(-300, -950, yaw=180), W(5.0),
              C("hsd_ai_kill last"), W(0.3)]
    s += [C("hsd_tag -")]
    return s


PLANS += ["ai_percept"]


# ---- L-6 reference recordings (+ L-7 elite pilot) ----
# Player on the navmesh near the spawn (x -300..300, y -1600..-1300 is meshed); each enemy
# spawns 600-700 u away, unheld, and fights for REF_SEC while the player stands, strafes and
# jumps; NP (10 Hz positions, yaw), NSCHED, NSHOT, PDMG are the reference.
REF_KINDS = [  # tag, class, ai settings
    ("soldier", "npc_soldier", "-"), ("spectre", "npc_spectre", "-"),
    ("stalker", "npc_stalker", "-"), ("reaper", "npc_super_spectre", "-"),
    ("drone", "npc_drone", "npc_drone_plasma"), ("tick", "npc_frag_drone", "-"),
]
PLAYER_REF = (200, -1450)


def ref_moves(sec):
    """stand / strafe / jump loop for about sec seconds"""
    out = []
    t = 0.0
    while t < sec:
        out += [W(3.0), C("+moveleft"), W(1.5), C("-moveleft"), C("+moveright"), W(1.5), C("-moveright")]
        out += jumps(2)
        t += 7.7
    return out


def ai_ref_kind(tag, cls, aiset, sec=22, spawn=(-400, -1350)):
    return [C("hsd_tag ref_" + tag), R(PLAYER_REF[0], PLAYER_REF[1], yaw=180), W(0.3),
            C("hsd_ai_class %s %s %d %d 1 0 0" % (cls, aiset, spawn[0], spawn[1]))] + ref_moves(sec) + [
            C("hsd_ai_kill all"), W(0.5)]


def ai_ref_a():
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000"), C("hsd_npc_nav")]
    for k in REF_KINDS[:4]:
        s += ai_ref_kind(*k)
    return s + [C("hsd_tag -")]


def ai_ref_a2():
    """rerun of ai_ref_a without the shield captain / specialist (their models are not precached on mp_lf_stacks;
    spawning one is a server script error that ends the run, 20261108_135601)"""
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000")]
    for k in REF_KINDS[1:2]:
        s += ai_ref_kind(*k)
    return s + [C("hsd_tag -")]


def ai_entr2():
    return ai_entr()


def ai_ref_b():
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000"), C("hsd_npc_nav")]
    for k in REF_KINDS[4:]:
        s += ai_ref_kind(*k)
    # L-7: elite pilot, longer, player keeps moving around the meshed area
    s += [C("hsd_tag ref_elite"), R(PLAYER_REF[0], PLAYER_REF[1], yaw=180), W(0.3),
          C("hsd_ai_class npc_pilot_elite - -400 -1350 1 0 0")] + ref_moves(40) + [C("hsd_ai_kill all"), W(0.5)]
    return s + [C("hsd_tag -")]


# ---- L-8 entrances (Northstar _ai_gamemodes.gnut helpers) + animation lengths (AI-SPEC 6.13) ----
SEQ_TITAN = "at_hotdrop_drop_2knee_turbo+titan_impact+second_stage "             "at_hotdrop_drop_2knee_turbo_upgraded+titan_impact+second_stage at_hotdrop_quickstand at_hotdrop_01"
SEQ_SOLDIER = "pt_dp_exit_a pt_dp_exit_b pt_dp_exit_c pt_dp_exit_d pt_zipline_ready2slide pt_zipline_slide_idle "               "pt_zipline_dismount_standF pt_zipline_dismount_crouchF pt_zipline_dismount_crouch180 "               "pt_zipline_dismount_breakright pt_zipline_land st_widow_spawner_leap st_widow_spawner_leap_short "               "st_widow_spawner_leap_long st_widow_spawner_fall st_widow_spawner_land st_medbay_drop_armed"


def seq_cmds(sel, anims, per=3):
    """hsd_ai_seq commands, a few animations each (client commands are length-limited)"""
    a = anims.split()
    return [C("hsd_ai_seq %s %s" % (sel, " ".join(a[i:i + per]))) for i in range(0, len(a), per)]


def ai_entr():
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000"), R(24, -1864, yaw=90), W(0.5),
         C("hsd_tag seq_pod"), C("hsd_ai_seq pod pod_testpath+OnImpact")]
    for kind, pos, extra, wait in (("pod", (0, -1450), "npc_soldier", 16.0), ("reaper", (100, -1450), "", 14.0),
                                   ("titan", (0, -1300), "titan_atlas_tracker", 14.0)):
        s += [C("hsd_tag entr_" + kind), C("hsd_ai_entrance %s %d %d 1 -90 %s" % (kind, pos[0], pos[1], extra)), W(wait)]
        if kind == "titan":
            s += seq_cmds("c.npc_titan", SEQ_TITAN)
        s += [C("hsd_ai_kill all"), W(1.0)]
    # animation lengths on fresh, blind NPCs far from the player
    for cls, aiset, anims in (("npc_soldier", "-", SEQ_SOLDIER),
                              ("npc_spectre", "-", "sp_med_bay_drop_A sp_med_bay_drop_unarmed pt_dp_exit_a pt_dp_exit_b"),
                              ("npc_frag_drone", "-", "sd_closed_to_open+frag_drone_armed"),
                              ("npc_drone", "npc_drone_plasma", "dr_activate_drone_spin dr_activate_drone_spin_indoor"),
                              ("npc_super_spectre", "-", "sspec_idle_to_speclaunch sspec_speclaunch_fire sspec_speclaunch_to_idle")):
        s += [C("hsd_tag seq_" + cls), C("hsd_ai_class %s %s 600 -900 1 0 1" % (cls, aiset)), W(1.0)]
        s += seq_cmds("c." + cls, anims) + [C("hsd_ai_kill all"), W(0.5)]
    return s + [C("hsd_tag -")]


PLANS += ["ai_ref_a", "ai_ref_a2", "ai_ref_b", "ai_entr", "ai_entr2"]


def ai_ref_c():
    """elite pilot (60 s), soldier and stalker spawned INSIDE the meshed area (W1: x -300..300,
    y -1600..-1300), player 450 u away also on the mesh, so they can path (ai_ref_a/b spawned at
    x -400, just off the mesh, and never moved)."""
    s = [C("hsd_info"), C("hsd_ai_info"), C("hsd_hp 60000"), C("hsd_npc_nav")]
    for tag, cls, sec in (("elite", "npc_pilot_elite", 60), ("soldier", "npc_soldier", 25), ("stalker", "npc_stalker", 25)):
        s += [C("hsd_tag ref_%s_mesh" % tag), R(250, -1450, yaw=180), W(0.3),
              C("hsd_ai_class %s - -200 -1450 1 0 0" % cls)] + ref_moves(sec) + [C("hsd_ai_kill all"), W(0.5)]
    return s + [C("hsd_tag -")]


PLANS += ["ai_ref_c"]
