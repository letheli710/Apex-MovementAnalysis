"""Overnight experiments (2026-10-29 night, overnight/PLAN.md): grapple (N2), the cut
pilot_boost class (N2b) and phase shift (N3). Uses the T5 helpers; same runner rules."""
from plans import C, U, W  # plans.py imports this module at its end
from plans_t5 import R, RA, T, release

GRAPPLE = "hsd_offhand mp_ability_grapple 1"


def gr(name, setup, extra=(), fire_wait=0.0, dur=2.5):
    """one grapple trial: refill, set up, fire the tactical, record dur seconds"""
    s = T(name) + [C(GRAPPLE), W(0.2)] + setup + list(extra[:1])
    if fire_wait:
        s += [W(fire_wait)]
    s += [C("+offhand1"), W(0.1), C("-offhand1")] + list(extra[1:]) + [W(dur)] + release() + [
        U("ground", 0, 4), W(0.4)]
    return s


def night_grapple():
    """N2: TF2 grapple pull law. West wall x=-960 (plane z 150-600), aim from x=-300."""
    s = [C("hsd_weapon mp_weapon_rspn101"), C("hsd_info"), W(0.5)]
    # from the ground, aimed slightly up into the wall, 660 u away
    s += gr("g_ground", [R(x=-300, y=-1000, z=2, yaw=180), W(0.3)])
    s += gr("g_ground_b", [R(x=-300, y=-1000, z=2, yaw=180), W(0.3)])
    s += gr("g_ground_fwd", [R(x=-300, y=-1000, z=2, yaw=180), W(0.3)], extra=(C("+forward"),))
    # long pull (900 u) to see the 1.5 s speed ramp
    s += gr("g_far", [R(x=-60, y=-1000, z=2, yaw=180), W(0.3)], dur=3.0)
    # jump while pulling (grapple_jumpFrac)
    s += gr("g_jump", [R(x=-300, y=-1000, z=2, yaw=180), W(0.3)],
            extra=(W(0.0), W(0.7), C("+jump"), W(0.05), C("-jump")))
    # in the air moving sideways at 400 (slingshot): perpendicular decel 425
    s += gr("g_side", RA(x=-300, y=-1400, z=200, vy=400, yaw=180))
    s += gr("g_side_fast", RA(x=-300, y=-1500, z=200, vy=700, yaw=180))
    # in the air, falling, target below (gravity help): aim 40 deg down
    s += T("g_down_pre") + [C("hsd_setup -300 -1000 500 0 0 0 40 180"), W(0.05)]
    s += gr("g_down", [C("hsd_setup -300 -1000 500 0 0 0 40 180"), W(0.05), U("air", 0, 1)])
    # target above (looking under the grapple point + forward = more gravity)
    s += gr("g_up_fwd", [R(x=-500, y=-1000, z=2, yaw=180), C("hsd_setup -500 -1000 2 0 0 0 -35 180"), W(0.3)],
            extra=(C("+forward"),))
    s += gr("g_up", [C("hsd_setup -500 -1000 2 0 0 0 -35 180"), W(0.3)])
    # miss (aim at the open sky: pitch -80) to read the grace period / charge use
    s += T("g_miss") + [C(GRAPPLE), C("hsd_setup 24 -1864 2 0 0 0 -80 90"), W(0.3), C("+offhand1"), W(0.1),
                        C("-offhand1"), W(1.0), C("hsd_info"), W(0.5)]
    s += T("-") + [W(1.0)]
    return s


def night_boost():
    """N2b: the cut pilot_boost class (boost / glide / jetpack / hover)."""
    q = ("hsd_query jumpheight boostEnabled boostThrust boostDuration glideEnabled glideThrust glideDuration "
         "jetpackEnabled jetpackThrust hoverEnabled climbEnabled airStrafeEnabled airSpeed airAcceleration gravityScale")
    s = [C("hsd_class pilot_boost_male"), W(1.0), C(q), C("hsd_info"), W(0.5)]
    s += T("b_jump") + [R(), W(0.5), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), U("ground", 0, 4), W(0.5)]
    # second jump press in the air (boost?), tap
    s += T("b_tap") + [R(), W(0.5), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), W(0.35), C("+jump"), W(0.05),
                       C("-jump"), U("ground", 0, 6), W(0.5)]
    # second press held 3 s (jetpack / glide?)
    s += T("b_hold") + [R(), W(0.5), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), W(0.35), C("+jump"), W(3.0),
                        C("-jump"), U("ground", 0, 8), W(0.5)]
    # held from the ground (jump and keep holding)
    s += T("b_hold_ground") + [R(), W(0.5), C("+jump"), W(3.0), C("-jump"), U("ground", 0, 8), W(0.5)]
    # held with forward (horizontal thrust / strafe)
    s += T("b_hold_fwd") + [R(), W(0.5), C("+forward"), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), W(0.35),
                            C("+jump"), W(2.5)] + release() + [U("ground", 0, 8), W(0.5)]
    # ADS in the air (hover?)
    s += T("b_ads") + [R(), W(0.5), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), W(0.3), C("+zoom"), W(3.0),
                       C("-zoom"), U("ground", 0, 8), W(0.5)]
    # crouch held in the air (climb / dive?)
    s += T("b_duck_air") + [R(), W(0.5), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), W(0.3), C("+duck"), W(2.0),
                            C("-duck"), U("ground", 0, 8), W(0.5)]
    # fall from height, then hold jump (glide catching a fall)
    s += T("b_fall_hold") + RA(z=600) + [W(0.4), C("+jump"), W(2.5), C("-jump"), U("ground", 0, 8), W(0.5)]
    s += T("b_restore") + [C("hsd_class pilot_grapple_male"), W(1.0), C("hsd_info")]
    s += T("-") + [W(1.0)]
    return s


def night_phase():
    """N3: phase shift (mp_ability_shifter): speed during and after."""
    s = [C("hsd_weapon mp_weapon_rspn101"), C("hsd_offhand mp_ability_shifter 1"), W(0.5), C("hsd_info")]
    for name, keys in (("p_walk", ("+forward",)), ("p_sprint", ("+speed", "+forward")), ("p_still", ())):
        s += T(name) + [C("hsd_offhand mp_ability_shifter 1"), R(y=-1864), W(0.4)] + [C(k) for k in keys] + [
            W(0.6), C("+offhand1"), W(0.1), C("-offhand1"), W(4.0)] + release() + [U("hmax", 0.5, 3), W(0.3)]
    s += T("p_jump") + [C("hsd_offhand mp_ability_shifter 1"), R(), W(0.4), C("+speed"), C("+forward"), W(0.5),
                        C("+offhand1"), W(0.1), C("-offhand1"), W(0.3), C("+jump"), W(0.05), C("-jump"), W(3.0)] + \
        release() + [U("ground", 0, 3), W(0.3)]
    s += T("p_restore") + [C("hsd_offhand mp_ability_grapple 1")]
    s += T("-") + [W(1.0)]
    return s


def night_grapple2():
    """N2 re-run in clean air: start at z 350, aim level at the wall plane x=-960 (y -950)."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    A = dict(x=-300, y=-950, z=350, yaw=180)
    cases = [("a_still", {}, ()), ("a_still_b", {}, ()), ("a_side400", dict(vy=400), ()),
             ("a_side700", dict(vy=700), ()), ("a_away300", dict(vx=300), ()), ("a_toward500", dict(vx=-500), ()),
             ("a_fall400", dict(vz=-400), ()), ("a_rise300", dict(vz=300), ())]
    for name, v, _ in cases:
        kw = dict(A); kw.update(v)
        s += gr(name, RA(**kw), dur=2.0)
    s += gr("a_fwd", RA(**A), extra=(C("+forward"),), dur=2.0)
    s += gr("a_back", RA(**A), extra=(C("+back"),), dur=2.0)
    s += gr("a_right", RA(**A), extra=(C("+moveright"),), dur=2.0)
    s += gr("a_jump", RA(**A), extra=(W(0.0), W(0.8), C("+jump"), W(0.05), C("-jump")), dur=1.5)
    s += gr("a_far", RA(x=100, y=-950, z=350, yaw=180), dur=2.5)
    s += gr("a_far_b", RA(x=100, y=-950, z=350, yaw=180), dur=2.5)
    s += gr("a_down45", [C("hsd_setup -300 -950 600 0 0 0 45 180"), W(0.05), U("air", 0, 1)], dur=2.0)
    s += gr("a_up30", [C("hsd_setup -300 -950 150 0 0 0 -30 180"), W(0.05), U("air", 0, 1)], dur=2.0)
    s += T("-") + [W(1.0)]
    return s


def night_phase2():
    """N3 re-run: confirm phase shift fires (hsd_info prints IsPhaseShifted) and measure speed
    during and right after it; the lane from the spawn is ~570 u, so start moving at activation."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    for name, keys in (("q_walk", ("+forward",)), ("q_sprint", ("+speed", "+forward")), ("q_still", ())):
        s += T(name) + [C("hsd_offhand mp_ability_shifter 1"), R(), W(0.5), C("+offhand1"), W(0.1), C("-offhand1"),
                        C("hsd_info"), W(0.3), C("hsd_info")] + [C(k) for k in keys] + [
            W(1.0), C("hsd_info"), W(0.9), C("hsd_info"), W(1.0), C("hsd_info")] + release() + [U("hmax", 0.5, 3),
                                                                                              W(0.3)]
    # sprint first, phase mid-run (exit while moving)
    s += T("q_midrun") + [C("hsd_offhand mp_ability_shifter 1"), R(), W(0.3), C("+speed"), C("+forward"), W(0.4),
                          C("+offhand1"), W(0.1), C("-offhand1"), C("hsd_info"), W(1.9), C("hsd_info"), W(0.3),
                          C("hsd_info")] + release() + [U("hmax", 0.5, 3)]
    s += T("q_restore") + [C("hsd_offhand mp_ability_grapple 1")]
    s += T("-") + [W(1.0)]
    return s


def gr3(name, setup, extra=(), dur=2.0):
    s = T(name) + [C("hsd_gpower 100"), W(0.1)] + setup + list(extra[:1]) + [
        C("+offhand1"), W(0.1), C("-offhand1"), C("hsd_gpower")] + list(extra[1:]) + [W(dur)] + release() + [
        U("ground", 0, 4), W(0.4)]
    return s


def night_grapple3():
    """N2 third run: grapple power refilled before every trial (power is per player: 100,
    one pull costs 50); clean air at z 350, level aim at the wall plane x=-960."""
    s = [C("hsd_weapon mp_weapon_rspn101"), C("hsd_gpower"), W(0.5)]
    A = dict(x=-300, y=-950, z=350, yaw=180)
    for name, v in [("c_still", {}), ("c_side400", dict(vy=400)), ("c_side700", dict(vy=700)),
                    ("c_away300", dict(vx=300)), ("c_toward500", dict(vx=-500)), ("c_fall400", dict(vz=-400)),
                    ("c_rise300", dict(vz=300))]:
        kw = dict(A); kw.update(v)
        s += gr3(name, RA(**kw))
    s += gr3("c_fwd", RA(**A), extra=(C("+forward"),))
    s += gr3("c_back", RA(**A), extra=(C("+back"),))
    s += gr3("c_right", RA(**A), extra=(C("+moveright"),))
    s += gr3("c_jump", RA(**A), extra=(W(0.0), W(0.8), C("+jump"), W(0.05), C("-jump")), dur=1.5)
    s += gr3("c_far", RA(x=100, y=-950, z=350, yaw=180), dur=2.5)
    s += gr3("c_down45", [C("hsd_setup -300 -950 600 0 0 0 45 180"), W(0.05), U("air", 0, 1)])
    s += gr3("c_up30", [C("hsd_setup -300 -950 150 0 0 0 -30 180"), W(0.05), U("air", 0, 1)])
    # power use and regen: two pulls back to back, then watch the power for 6 s
    s += T("c_power") + [C("hsd_gpower 100"), *RA(**A), C("+offhand1"), W(0.1), C("-offhand1"), W(1.6), C("hsd_gpower"),
                         *RA(**A), C("+offhand1"), W(0.1), C("-offhand1"), W(1.6), C("hsd_gpower")] + \
        sum([[W(1.0), C("hsd_gpower")] for _ in range(6)], [])
    s += T("-") + [W(1.0)]
    return s


def night_winscan():
    """Find window hints on mp_lf_stacks with GetWindowHint (server scan, two heights)."""
    return [C("hsd_windows -1600 -2600 1600 600 200 60"), W(12.0), C("hsd_windows -1600 -2600 1600 600 200 260"),
            W(12.0), C("hsd_tag -"), W(0.5)]


def night_winscan_big():
    """GetWindowHint scan over a large map (Angel City), three heights."""
    s = []
    for z in (40, 200, 400):
        s += [C("hsd_windows -5000 -5000 5000 5000 400 %d" % z), W(20.0)]
    return s + [C("hsd_tag -"), W(0.5)]


def night_winscan_var():
    """GetWindowHint argument variants on Angel City (direction as velocity, longer reach, margin)."""
    s = []
    for vs, dist, grav, margin in ((400, 1000, 600, 0), (400, 2000, 750, 64), (1, 2000, 0, 64), (600, 0.8, 600, 32)):
        s += [C("hsd_windows -4800 -4800 4800 4800 600 150 %g %g %g %g" % (vs, dist, grav, margin)), W(10.0)]
    return s + [C("hsd_tag -"), W(0.5)]


def gm(name, setup, keys=(), dur=2.2, lead=()):
    """N6 matched trial: refill, set up, optional lead-in steps (sprint run-up), fire, hold keys"""
    s = T(name) + [C("hsd_gpower 100"), W(0.1)] + setup + list(lead) + [C("+offhand1"), W(0.1), C("-offhand1")]
    s += [C(k) for k in keys] + [W(dur)] + release() + [U("ground", 0, 4), W(0.4)]
    return s


def night_grapple_match():
    """N6 (2026-10-29, after review): TF2 grapple in the Apex M10 lane-A geometry. Player on the
    floor, hooking the west wall x=-960: d250 / d400 / d700, pitch 0 and -20, sprint / slide fire,
    W / S / A / D held, 45 deg yaw (slingshot). Two floor lanes (y -950, -850); traces first."""
    s = [C("hsd_weapon mp_weapon_rspn101"), C("hsd_gpower"), W(0.5)]
    for y in (-1000, -950, -900, -850, -800):
        for z in (10, 40, 70):
            s += [C("hsd_trace -150 %d %d -1000 %d %d" % (y, z, y, z)), W(0.05)]
    for y in (-950, -850):
        L = "y%d_" % -y
        G = lambda x, yaw=180, pitch=0: [C("hsd_setup %g %g 2 0 0 0 %g %g" % (x, y, pitch, yaw)), W(0.4)]
        for rep in ("r1", "r2"):  # 2026-10-29 run used "a"/"b": "a" collided with the A-key trial
            s += gm(L + "d400_" + rep, G(-560))
        s += gm(L + "d250", G(-710))
        s += gm(L + "d700", G(-260), dur=2.6)
        s += gm(L + "p20", G(-560, pitch=-20))
        for k, key in (("w", "+forward"), ("s", "+back"), ("a", "+moveleft"), ("d", "+moveright")):
            s += gm(L + "d400_" + k, G(-560), keys=(key,))
        for k, keys in (("none", ()), ("a", ("+moveleft",)), ("d", ("+moveright",))):
            s += gm(L + "yaw45_" + k, G(-560, yaw=135), keys=keys)
        # sprint run-up from x -150, fire after 0.8 s; keys released at the fire command
        run = [C("+speed"), C("+forward"), W(0.8)]
        s += gm(L + "sprint", G(-150), lead=run + [C("-forward"), C("-speed")])
        s += gm(L + "sprint_hold", G(-150), lead=run, keys=("+forward",))
        s += gm(L + "slide", G(-150), lead=run + [C("+duck"), W(0.25)], keys=())
    s += T("-") + [W(1.0)]
    return s
