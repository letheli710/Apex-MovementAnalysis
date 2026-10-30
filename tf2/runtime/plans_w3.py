"""Worker W3 (2026-10-29): boosts research. Phase Rewind, Ticks and sentry turrets use the
player as the target (enemy-team Tick / turret), Smart Pistol uses W1's targets (hsd_npc).
Server commands in ../mod/HSD.TF2Diag/mod/scripts/vscripts/hsd_diag_w3.gnut."""
from plans import C, U, W  # plans.py imports this module at its end
from plans_t5 import R, RA, T, release


def w3_rewind():
    """Phase Rewind (Northstar _burnmeter.gnut): buffer, path, end spot, velocity and view after."""
    s = [C("hsd_info"), C("hsd_hp 1000"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # A: an L walked on the floor (+x 2 s, then +y 2 s), standing still when it fires
    s += T("rw_L") + [R(yaw=0), W(0.5), C("+forward"), W(2.0), C("-forward"), C("+moveleft"), W(2.0),
                      C("-moveleft"), W(0.3), C("hsd_w3_rewind"), W(4.0), C("hsd_w3_rwbuf"), W(0.5)]
    # B: the oldest sample is in the air (teleported to z 400, then walked): does it end mid-air?
    s += T("rw_air") + RA(z=400, yaw=0) + [C("+forward"), W(3.6), C("-forward"), C("hsd_w3_rewind"), W(4.0),
                                           U("ground", 0, 3), W(0.5)]
    # C: still holding forward (sprint) when it fires: speed and input right after
    s += T("rw_moving") + [R(yaw=0), W(0.3), C("+speed"), C("+forward"), W(2.5), C("hsd_w3_rewind"), W(3.0)] + \
        release() + [W(1.0)]
    # D: crouched at the oldest sample, standing at the end
    s += T("rw_crouch") + [R(yaw=0), W(0.3), C("+duck"), W(1.0), C("+forward"), W(1.0), C("-duck"), W(2.0),
                           C("-forward"), W(0.3), C("hsd_w3_rewind"), W(4.0)]
    # E: view turned during the history (yaw 0 -> 90 by teleport), looking 90 when it fires
    s += T("rw_view") + [R(yaw=0), W(0.3), C("+forward"), W(1.5), C("-forward"), W(0.2),
                         C("hsd_w3_rwbuf"), W(2.5), C("hsd_w3_rewind"), W(4.0)]
    s += T("-") + [W(1.0)]
    return s


def w3_rewind2():
    """Phase Rewind follow-up: the view turned inside the window, the oldest sample high in the air,
    and a rewind right after another (buffer refilled?). x ~ 160 is blocked at the lf_stacks spawn."""
    s = [C("hsd_hp 1000"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # view: yaw 0, then the same spot with yaw 90 (teleport), rewind 1 s later
    s += T("rv_yaw") + [R(yaw=0), W(1.5), R(yaw=90), W(1.0), C("hsd_w3_rewind"), W(3.5)]
    # air: teleport to z 400 (falls ~1.15 s), rewind 0.9 s later: oldest sample still high up
    s += T("rv_air") + [R(yaw=90), W(1.5)] + RA(z=400, yaw=90) + [W(0.9), C("hsd_w3_rewind"), W(3.5),
                                                                  U("ground", 0, 3), W(0.5)]
    # path along +y (open floor), then two rewinds back to back
    s += T("rv_twice") + [R(yaw=90), W(0.3), C("+forward"), W(2.5), C("-forward"), C("hsd_w3_rewind"), W(2.6),
                          C("hsd_w3_rewind"), W(3.0)]
    s += T("-") + [W(1.0)]
    return s


def w3_tick():
    """Ticks: an enemy-team Tick chases the player in the open +y lane of the lf_stacks spawn
    (navmesh: W1's chase works there)."""
    s = [C("hsd_info"), C("hsd_npc_nav"), C("hsd_hp 3000"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # A: player stands; Tick spawned 700 u ahead
    s += T("tk_still") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 10"), C("hsd_w3_tick 0 700"), W(10.0),
                          C("hsd_hp 3000")]
    # B: player backs away (173 u/s) from a Tick 400 u ahead
    s += T("tk_flee") + [R(y=-1500, yaw=-90), W(0.3), C("hsd_w3_npclog npc_frag_drone 10"), C("hsd_w3_tick 0 -364"),
                         W(0.5), C("+back"), W(4.5), C("-back"), W(5.0), C("hsd_hp 3000")]
    # C: player jumps twice as it arrives (the trigger ignores enemies > 40 u above or below)
    s += T("tk_jump") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 10"), C("hsd_w3_tick 0 500"), W(1.5),
                         C("+jump"), W(0.05), C("-jump"), W(0.9), C("+jump"), W(0.05), C("-jump"), W(0.9),
                         C("+jump"), W(0.05), C("-jump"), W(6.0), C("hsd_hp 3000")]
    # D: a Tick owned by the player with no enemy around (idle behaviour)
    s += T("tk_own") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 6"), C("hsd_w3_tick 0 300 own"), W(6.0),
                        C("hsd_w3_kill npc_frag_drone"), W(1.0)]
    s += T("-") + [W(1.0)]
    return s


def w3_turret():
    """Sentry turrets (burn-card AI settings) shooting at the player in the open +y lane:
    fire rate, damage, turn, yaw limit. The turret stands at (24, -1300) facing -y."""
    s = [C("hsd_info"), C("hsd_hp 20000"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    s += T("ap_564") + [R(), W(0.3), C("hsd_w3_turret ap 0 564 -90"), C("hsd_w3_npclog npc_turret_sentry 45"),
                        W(7.0)]
    # 90 deg off its facing (turn speed: 45 deg/s?), then behind it (yaw limit 90)
    s += T("ap_side") + [R(x=424, y=-1300, yaw=180), W(5.0)]
    s += T("ap_behind") + [R(x=24, y=-900, yaw=-90), W(5.0)]
    # back in front, at 300 u, then walking across its view (tracking)
    s += T("ap_300") + [R(y=-1600), W(4.0)]
    s += T("ap_cross") + [R(x=-300, y=-1700, yaw=0), W(0.3), C("+forward"), W(3.5), C("-forward"), W(1.0)]
    s += T("ap_kill") + [C("hsd_w3_kill npc_turret_sentry"), W(1.0)]
    # AT turret: pilots are not its targets (maxEnemyDist 0)?
    s += T("at_564") + [R(), W(0.3), C("hsd_w3_turret at 0 564 -90"), W(6.0), C("hsd_w3_kill npc_turret_sentry"),
                        W(1.0)]
    s += T("-") + [W(1.0)]
    return s


def w3_smart():
    """Smart Pistol lock-on on W1's static soldiers (hsd_npc): lock time vs distance and angle,
    targets per trigger pull, locks per target, damage. Player at the spawn facing +y."""
    s = [C("hsd_hp 5000"), C("hsd_weapon mp_weapon_smart_pistol"), W(1.0), C("hsd_info")]

    def one(name, x, y, hp=0, fire=False, extra=()):
        t = T(name) + [R(), W(0.2), C("hsd_npc soldier static %g %g 1 -90 %d" % (x, y, hp)), W(0.1),
                       C("hsd_w3_smart 3.5")] + list(extra) + [W(2.5)]
        if fire:
            t += [C("+attack"), W(2.0), C("-attack"), W(0.5)]
        return t + [C("hsd_npc_kill all"), W(0.6), C("hsd_weapon mp_weapon_smart_pistol"), W(0.6)]

    # distance: 300, 600, 1150 u straight ahead
    for d in (300, 600, 1150):
        s += one("sm_d%d" % d, 24, -1864 + d)
    # angle off the view at 400 u: 10, 20, 30, 40 deg (x offset 400 tan a)
    for a, dx in ((10, 71), (20, 146), (30, 231), (40, 336)):
        s += one("sm_a%d" % a, 24 - dx, -1464)
    # ADS lock (ads_smaller_lock_on mod; same 35 search angle) at 30 deg
    s += one("sm_ads30", 24 - 231, -1464, extra=(C("+zoom"),)) + [C("-zoom")]
    # fire at one default-health soldier, then at a 500 hp one (locks per target, shots per pull)
    s += one("sm_fire1", 24, -1464, fire=True)
    s += one("sm_fire500", 24, -1464, hp=500, fire=True)
    # three soldiers side by side at 400 u: max targets, burst split
    s += T("sm_multi") + [R(), W(0.2), C("hsd_npc soldier static -126 -1464 1 -90"),
                          C("hsd_npc soldier static 24 -1464 1 -90"), C("hsd_npc soldier static 174 -1464 1 -90"),
                          W(0.1), C("hsd_w3_smart 5"), W(2.5), C("+attack"), W(2.0), C("-attack"), W(0.5),
                          C("hsd_npc_hp all"), C("hsd_npc_kill all"), W(0.5)]
    # no target: fires straight
    s += T("sm_none") + [R(), W(0.3), C("+attack"), W(0.6), C("-attack"), W(0.5)]
    s += T("-") + [W(1.0)]
    return s


def w3_tick2():
    """Ticks follow-up: speed from far away (1164 u: speed scale 0.8 beyond 850?), and a player
    who keeps jumping while it arrives (no trigger while > 40 u above it?)."""
    s = [C("hsd_hp 3000"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    s += T("tk_far") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 14"), C("hsd_w3_tick 0 1164"), W(14.0),
                        C("hsd_w3_kill npc_frag_drone"), C("hsd_hp 3000"), W(0.5)]
    s += T("tk_hop") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 12"), C("hsd_w3_tick 0 600"), W(2.5)]
    for _ in range(10):
        s += [C("+jump"), W(0.05), C("-jump"), W(0.75)]
    s += [W(3.0), C("hsd_w3_kill npc_frag_drone"), W(0.5)]
    s += T("-") + [W(1.0)]
    return s


def w3_smart2():
    """Smart Pistol follow-up: three targets inside the cone (+-60 u at 400 u = 8.5 deg), the
    1250 u search limit (1286 u), 15 deg off the view, and a target sliding sideways at 250 u/s."""
    s = [C("hsd_hp 5000"), C("hsd_weapon mp_weapon_smart_pistol"), W(1.0)]
    s += T("sm2_multi") + [R(), W(0.2), C("hsd_npc soldier static -36 -1464 1 -90 200"),
                           C("hsd_npc soldier static 24 -1464 1 -90 200"), C("hsd_npc soldier static 84 -1464 1 -90 200"),
                           W(0.1), C("hsd_w3_smart 6"), W(2.5), C("+attack"), W(0.1), C("-attack"), W(1.5),
                           C("hsd_npc_hp all"), C("+attack"), W(2.0), C("-attack"), W(0.5),
                           C("hsd_npc_hp all"), C("hsd_npc_kill all"), W(0.5), C("hsd_weapon mp_weapon_smart_pistol"),
                           W(0.6)]
    s += T("sm2_d1286") + [R(y=-2000), W(0.2), C("hsd_npc soldier static 24 -714 1 -90"), W(0.1),
                           C("hsd_w3_smart 3"), W(3.0), C("hsd_npc_kill all"), W(0.5)]
    s += T("sm2_d1236") + [R(y=-1950), W(0.2), C("hsd_npc soldier static 24 -714 1 -90"), W(0.1),
                           C("hsd_w3_smart 3"), W(3.0), C("hsd_npc_kill all"), W(0.5)]
    s += T("sm2_a15") + [R(), W(0.2), C("hsd_npc soldier static -83 -1464 1 -90"), W(0.1),
                         C("hsd_w3_smart 3"), W(3.0), C("hsd_npc_kill all"), W(0.5)]
    s += T("sm2_slide") + [R(), W(0.2), C("hsd_npc soldier idle -60 -1464 1 -90 200"), W(1.2),
                           C("hsd_npc_slide 7 110 -1464 1 250"), W(0.1), C("hsd_w3_smart 5"), W(2.0),
                           C("+attack"), W(2.0), C("-attack"), W(0.5), C("hsd_npc_hp all"), C("hsd_npc_kill all")]
    s += T("-") + [W(1.0)]
    return s
