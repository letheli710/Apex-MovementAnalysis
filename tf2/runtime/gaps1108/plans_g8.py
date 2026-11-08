"""GAPS-1108 plans (session tf2-pilot-gaps, 2026-11-08). Run with runner_g8.py (adds hsd_diag_g8.gnut).
Report: ../GAPS-1108.md. Helpers and coordinates are T5's (plans_t5.py) and W2's (plans_w2.py):
mp_lf_stacks spawn (24, -1864, 2) faces +y; west wall x = -960 (flat for y -1400..-500, z 150..600)."""
from plans import C, U, W
from plans_t5 import SPAWN, WALL_X, R, RA, T, WR, release
from plans_w2 import HP, tap

X, Y = SPAWN[0], SPAWN[1]
SOUTH_Y = -2043  # south wall face at z 250 for x 100..500 (probe2 run 20261029_003701)


def wjump():
    """wall jump: tap jump during the run"""
    return [C("+jump"), W(0.03), C("-jump")]


def g8_a():
    """Pilot gaps, run A (mp_lf_stacks): settings readout, window hints (correct GetWindowHint
    arguments), walk-off edge search; A6 double jump while rising fast; A5 wall-jump repel;
    A4 wall jump then another wall within 0.5 s; A1 walk off an edge (if an open edge exists);
    B wall hang with pas_wallhang and pas_wall_runner."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), W(0.3),
         C("g8_set wallrun_timeLimit wallrun_hangTimeLimit wallrunAdsType superjumpMinHeight superjumpLimit jumpHeight"),
         C("g8_hints"), W(0.2)]
    # GetWindowHint with velocity / look-ahead time / gravity (Script_GetWindowHint 0x18060a610)
    for vx, vy in ((0, 400), (400, 0), (0, -400), (-400, 0), (283, 283), (-283, 283)):
        s += [C("g8_winq %g %g 60 %g %g 250 0.8 600" % (X, Y, vx, vy)), W(0.12)]
    # south wall face for A4
    for z in (150, 200, 250, 300, 350):
        s += [C("hsd_trace 150 -1900 %d 150 -2300 %d" % (z, z)), C("hsd_trace 450 -1900 %d 450 -2300 %d" % (z, z)), W(0.25)]
    s += [C("g8_edges -1000 -2150 1500 2600 32 700 120 500"), W(6.0)]

    # A6: double jump while rising. dj_ctrl late (vz ~150) -> 300; dj_fast right after take-off (vz ~288);
    # dj_kV: kick vz to V, 0.08 s later double jump (vz at the press ~ V - 48)
    s += T("dj_ctrl") + [R(), W(0.4), C("+jump"), U("air", 0, 1), C("-jump"), W(0.25)] + tap("jump", 0.04) + [
        U("ground", 0, 3), W(0.3)]
    for i in range(2):
        s += T("dj_fast%d" % i) + [R(), W(0.4), C("+jump"), U("air", 0, 1), C("-jump"), W(0.015)] + tap("jump", 0.04) + [
            U("ground", 0, 3), W(0.3)]
    for v in (280, 330, 380, 450, 550):
        s += T("dj_k%d" % v) + [R(), W(0.4), C("+jump"), U("air", 0, 1), C("-jump"), W(0.03), C("hsd_kick 0 0 %d" % v),
                                W(0.08)] + tap("jump", 0.04) + [U("ground", 0, 4), W(0.3)]

    # A5: repel after a wall jump (west wall, facing +y: left = -x = toward the wall)
    s += T("rp_none") + [WR(), U("wallrun", 0, 1), W(0.3)] + wjump() + [W(1.0), U("ground", 0, 3), W(0.3)]
    s += T("rp_toward") + [WR(), U("wallrun", 0, 1), W(0.3)] + wjump() + [C("+moveleft"), W(1.0), C("-moveleft"),
                                                                         U("ground", 0, 3), W(0.3)]
    s += T("rp_away") + [WR(), U("wallrun", 0, 1), W(0.3)] + wjump() + [C("+moveright"), W(1.0), C("-moveright"),
                                                                       U("ground", 0, 3), W(0.3)]
    for dt in (0.07, 0.17, 0.27, 0.37, 0.5):
        s += T("rp_k%03d" % int(dt * 100)) + [WR(), U("wallrun", 0, 1), W(0.3)] + wjump() + [
            W(dt), C("hsd_kick -150 200 100"), W(0.7), U("ground", 0, 3), W(0.3)]

    # A4: wall jump off the west wall, then teleport onto the south wall run line dt later
    for dt in (0.1, 0.3, 0.6):
        s += T("ow_%03d" % int(dt * 100)) + [WR(), U("wallrun", 0, 1), W(0.3)] + wjump() + [
            W(dt), R(x=150, y=SOUTH_Y + 18, z=260, vx=300, vy=-40, vz=0, yaw=0), W(0.05), U("wallrun", 0, 0.6),
            U("ground", 0, 3), W(0.3)]
    s += T("ow_ground") + [R(), W(0.4), R(x=150, y=SOUTH_Y + 18, z=260, vx=300, vy=-40, vz=0, yaw=0), W(0.05),
                           U("wallrun", 0, 0.6), U("ground", 0, 3), W(0.3)]

    # A1 / A4: walk off an open edge found by g8_edges (no jump), then teleport to the west wall
    # dt after leaving the ground (state kept: a teleport writes no ground or jump state, T5 wr_*)
    for i, dt in enumerate((0.1, 0.3, 0.45, 0.6, 0.8)):
        s += T("wo_%03d" % int(dt * 100)) + [C("g8_goedge 0 40"), W(0.4), C("+forward"), U("air", 0, 2), C("-forward"),
                                             W(dt), WR(), W(0.05), U("wallrun", 0, 0.8), U("nowallrun", 0, 3),
                                             U("ground", 0, 3), W(0.3)]

    # B: wall hang. Control without the passive (ADS only zooms)
    s += T("wh_ctrl") + [WR(z=450), U("wallrun", 0, 1), W(0.3), C("+zoom"), W(1.5), C("-zoom"), U("ground", 0, 4), W(0.3)]
    s += [C("w2_mods pas_wallhang"), W(0.3), C("g8_set wallrun_timeLimit wallrun_hangTimeLimit wallrunAdsType")]
    for i in range(2):
        s += T("wh_hold%d" % i) + [WR(z=450), U("wallrun", 0, 1), W(0.3), C("+zoom"), W(6.0), C("-zoom"),
                                   U("ground", 0, 6), W(0.3)]
    s += T("wh_release") + [WR(z=450), U("wallrun", 0, 1), W(0.3), C("+zoom"), W(1.5), C("-zoom"), W(2.0),
                            U("ground", 0, 6), W(0.3)]
    s += T("wh_late") + [WR(z=450), U("wallrun", 0, 1), W(1.3), C("+zoom"), W(6.0), C("-zoom"), U("ground", 0, 6), W(0.3)]
    s += T("wh_fwd") + [C("+forward"), WR(z=450), U("wallrun", 0, 1), W(0.3), C("+zoom"), W(6.0), C("-zoom"),
                        C("-forward"), U("ground", 0, 6), W(0.3)]
    # B4: pas_wall_runner on top (+2.5 s run, +21 s hang)
    s += [C("w2_mods pas_wallhang pas_wall_runner"), W(0.3), C("g8_set wallrun_timeLimit wallrun_hangTimeLimit")]
    s += T("wh_runner") + [WR(z=500), U("wallrun", 0, 1), W(0.3), C("+zoom"), W(12.0), C("-zoom"), U("ground", 0, 6), W(0.3)]
    # run time with forward held high on the west wall (T5 wr_hi_fwd ended by the 1.75 s limit); the flat
    # wall ends at y -500, about 2.5 s at 375 u/s, so a longer limit shows as a NO_WALL end instead
    for tag in ("wr_runner", "wr_runner_b"):
        s += T(tag) + [C("+forward"), WR(z=420), U("wallrun", 0, 1), U("nowallrun", 0, 6), C("-forward"),
                       U("ground", 0, 4), W(0.3)]
    s += [C("w2_mods"), W(0.3)]
    s += T("wr_base") + [C("+forward"), WR(z=420), U("wallrun", 0, 1), U("nowallrun", 0, 6), C("-forward"),
                         U("ground", 0, 4), W(0.3)]
    s += T("-") + [W(1.0)]
    return s


def g8_b():
    """Pilot gaps, run B (mp_lf_stacks): D1 gravity star pull vs distance in the air (no ground
    friction); D2 can a Tick be escaped by jumping; D3 A-Wall outgoing damage bonus on a target."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), HP, W(0.5)]
    # D1: an enemy-team star planted on the floor d u ahead (as W2 grav_pull); 1.05 s later (strong
    # pull from ~0.9 s, star popped ~60 u) the player is put in the air at the star's height, vz 200
    for d in (160, 190, 220, 250, 280, 310, 340):
        s += T("ga_%d" % d) + [HP, C("w2_clear"), R(), W(0.4), C("w2_watch 4"),
                               C("w2_shoot mp_weapon_grenade_gravity 1 0 %g %g 20 0 0 -1" % (X, Y + d)), W(1.05),
                               R(z=26, vz=200), W(2.2), U("ground", 0, 3), W(0.5)]
    s += [C("w2_clear"), W(0.3)]
    # D2: Ticks. tk_bob: the player stays > 60 u above the floor (teleport up every 1 s, never lands)
    # for 11 s while a Tick comes from 250 u, then lands
    s += T("tk_bob") + [C("hsd_hp 3000"), R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 18"), C("hsd_w3_tick 0 250"), W(0.2)]
    for _ in range(11):
        s += [R(z=75, vz=300), W(1.0)]
    s += [W(5.0), C("hsd_w3_kill npc_frag_drone"), C("hsd_hp 3000"), W(0.5)]
    # tk_trig_jump: stand until it has stopped next to you (~2.1 s after spawn at 200 u), then jump and double jump
    s += T("tk_trig_jump") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 7"), C("hsd_w3_tick 0 200"), W(2.1)] + \
        tap("jump", 0.05) + [U("air", 0, 1), W(0.25)] + tap("jump", 0.05) + [W(4.0), C("hsd_w3_kill npc_frag_drone"),
                                                                            C("hsd_hp 3000"), W(0.5)]
    # tk_trig_up: same, then teleported 300 u up (outside the 200 inner radius) once it has stopped
    s += T("tk_trig_up") + [R(), W(0.3), C("hsd_w3_npclog npc_frag_drone 7"), C("hsd_w3_tick 0 200"), W(2.1),
                            R(z=300), W(4.0), C("hsd_w3_kill npc_frag_drone"), C("hsd_hp 3000"), W(0.5)]
    # D3: a static soldier 400 u ahead (1000 hp); single R-201 shots, re-aimed each time (pitch 2: chest)
    aim = R(z=2, yaw=90)
    aim = C("hsd_setup %g %g 2 0 0 0 2 90" % (X, Y))
    s += T("aw_ctrl") + [C("hsd_npc soldier static %g %g 1 -90 1000" % (X, Y + 400)), W(1.2)]
    for _ in range(6):
        s += [aim, W(0.25), C("+attack"), W(0.04), C("-attack"), W(0.35)]
    s += [C("hsd_npc_hp all"), W(0.3)]
    s += T("aw_wall") + [C("hsd_offhand mp_weapon_deployable_cover 1"), R(), W(0.4), C("w2_watch 6")] + \
        tap("offhand1", 0.5) + [W(2.0), C("hsd_weapon mp_weapon_rspn101"), W(0.8)]
    for _ in range(6):
        s += [aim, W(0.25), C("+attack"), W(0.04), C("-attack"), W(0.35)]
    s += [C("hsd_npc_hp all"), W(0.3), C("hsd_npc_kill all"), W(0.3)]
    s += T("-") + [W(1.0)]
    return s


# window hints on mp_lf_stacks (g8_a, 2026-11-08): hint 6 = opening x -736..-640, z 268..392 in the plane
# y -1476 (hint 7 the same at y -1492); hint 4/5 = x -724..-652, z 164..236. The box under it: x -700..-650,
# y -1550..-1500, top z ~268 (bt_box).
WIN_X, WIN_Y_N, WIN_Y_S = -688, -1476, -1492


def g8_c():
    """Pilot gaps, run C (mp_lf_stacks): C2/C3 window assist. Geometry traces and engine queries first;
    then jumps through the hint-6 window: (1) ground jumps from the box top below it (south side, walking +y),
    (2) mid-air double jumps from the north side toward it (-y), (3) controls without a jump event."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), W(0.3), C("g8_hints"), W(0.3)]
    for x, y in ((-688, -1530), (-688, -1510), (-660, -1520), (-715, -1520), (-688, -1320), (-688, -1250)):
        s += [C("hsd_trace %d %d 650 %d %d -50" % (x, y, x, y)), W(0.15)]
    for z in (200, 250, 300, 330, 380, 420):
        s += [C("hsd_trace -688 -1250 %d -688 -1700 %d" % (z, z)), W(0.15)]
    for x in (-740, -730, -650, -636):
        s += [C("hsd_trace %d -1250 330 %d -1700 330" % (x, x)), W(0.15)]
    # engine queries at the trial starts (velocity after the jump, look-ahead 0.8 s, gravity 600)
    for x0, y0, z0, vy, vz in ((-688, -1540, 270, 173, 300), (-648, -1540, 270, 173, 300), (-688, -1326, 219, -300, 300),
                               (-688, -1326, 179, -300, 300), (-648, -1326, 219, -300, 300)):
        s += [C("g8_winq %g %g %g 0 %g %g 0.8 600" % (x0, y0, z0, vy, vz)), W(0.15)]
    # (1) box top: land on it, walk +y 0.12 s, jump. dx = offset from the window centre; yaw 180 = control
    for name, dx, yaw in (("wb_c", 0, 90), ("wb_c2", 0, 90), ("wb_r40", 40, 90), ("wb_l45", -45, 90), ("wb_side", 0, 180)):
        s += T(name) + [R(x=WIN_X + dx, y=-1543, z=320, yaw=yaw), U("air", 0, 1), U("ground", 0, 2), W(0.4),
                        C("+forward"), W(0.12), C("+jump"), U("air", 0, 1), C("-jump"), W(0.6), C("-forward"),
                        U("ground", 0, 3), W(0.4)]
    # (2) north side, in the air 150 u from the window plane moving -y at 300, view at the window; double jump at once
    for name, dx, z0 in (("wa_c", 0, 219), ("wa_low40", 0, 179), ("wa_high40", 0, 259), ("wa_r40", 40, 219),
                         ("wa_l45", -45, 219), ("wa_c2", 0, 219)):
        s += T(name) + RA(x=WIN_X + dx, y=WIN_Y_N + 150, z=z0, vy=-300, yaw=270) + tap("jump", 0.03) + [
            U("ground", 0, 3), W(0.4)]
    # (3) controls: same starts, no jump (no assist event): the path stays ballistic
    for name, dx, z0 in (("wn_c", 0, 294), ("wn_r40", 40, 294)):
        s += T(name) + RA(x=WIN_X + dx, y=WIN_Y_N + 150, z=z0, vy=-300, yaw=270) + [U("ground", 0, 3), W(0.4)]
    s += T("-") + [W(1.0)]
    return s


def g8_d():
    """Pilot gaps, run D: D2 Tick trials redone on the navmesh (g8_b spawned them off it: 'nav none').
    Player at (0, -1550), Tick 150-250 u ahead (navmesh x -300..300, y -1600..-1300, W1 TARGETS)."""
    px, py = 0, -1550
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    s += T("tk_bob") + [C("hsd_hp 3000"), R(x=px, y=py), W(0.3), C("hsd_w3_npclog npc_frag_drone 16"), C("hsd_w3_tick 0 250"), W(0.2)]
    for _ in range(10):
        s += [R(x=px, y=py, z=75, vz=300), W(1.0)]
    s += [W(4.0), C("hsd_w3_kill npc_frag_drone"), C("hsd_hp 3000"), W(0.5)]
    s += T("tk_trig_jump") + [R(x=px, y=py), W(0.3), C("hsd_w3_npclog npc_frag_drone 7"), C("hsd_w3_tick 0 150"), W(2.2)] + \
        tap("jump", 0.05) + [U("air", 0, 1), W(0.25)] + tap("jump", 0.05) + [W(4.0), C("hsd_w3_kill npc_frag_drone"),
                                                                            C("hsd_hp 3000"), W(0.5)]
    s += T("tk_trig_up") + [R(x=px, y=py), W(0.3), C("hsd_w3_npclog npc_frag_drone 7"), C("hsd_w3_tick 0 150"), W(2.2),
                            R(x=px, y=py, z=400), W(4.0), C("hsd_w3_kill npc_frag_drone"), C("hsd_hp 3000"), W(0.5)]
    s += T("tk_stand") + [R(x=px, y=py), W(0.3), C("hsd_w3_npclog npc_frag_drone 7"), C("hsd_w3_tick 0 150"), W(5.0),
                          C("hsd_w3_kill npc_frag_drone"), C("hsd_hp 3000"), W(0.5)]
    s += T("-") + [W(1.0)]
    return s
