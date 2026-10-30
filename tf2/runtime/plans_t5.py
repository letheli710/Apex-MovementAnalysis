"""T5 formal experiments (2026-10-29). Imported into plans.py, so runner.py finds them by name.
Trial names go to hsd_tag; analyze_t5.py segments by the logged CMD times (client clock)
and by state changes, not by tag times."""
from plans import C, U, W  # plans.py imports this module at its end

SPAWN = (24, -1864, 2)  # mp_lf_stacks floor; 1186 u of open floor along +y (probe run)
WALL_X = -960  # west wall: plane x=-960 for y in [-1400, -500], z in [150, 600] (probe2 run)


def R(x=SPAWN[0], y=SPAWN[1], z=SPAWN[2], vx=0, vy=0, vz=0, yaw=90):
    return C("hsd_setup %g %g %g %g %g %g 0 %g" % (x, y, z, vx, vy, vz, yaw))


def T(name):
    return [C("hsd_tag " + name), W(0.05)]


def release():
    return [C(c) for c in ("-forward", "-back", "-moveleft", "-moveright", "-speed", "-duck", "-jump", "-zoom")]


def t5_ground():
    """T-G01/G03/G04 (ADS and stim as move-speed scales), sprint, stim (T4)."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), W(1.0)]
    for i in range(2):
        s += T("walk%d" % i) + [R(), W(0.4), C("+forward"), W(1.5), C("-forward"), U("hmax", 0.5, 2), W(0.3)]
    s += T("kick") + [R(), W(0.4), C("hsd_kick 0 300 0"), W(1.0)]
    s += T("ads_walk") + [R(), C("+zoom"), W(0.8), C("+forward"), W(1.5), C("-forward"), U("hmax", 0.5, 3), W(0.3)]
    s += T("ads_kick") + [R(), W(0.4), C("hsd_kick 0 300 0"), W(1.2), C("-zoom"), W(0.5)]
    for i in range(2):
        s += T("sprint%d" % i) + [R(), W(0.4), C("+speed"), C("+forward"), W(2.0), C("-forward"), C("-speed"),
                                  U("hmax", 0.5, 3), W(0.3)]
    s += T("stim_on") + [R(), W(0.3), C("hsd_stim 9"), W(0.3)]
    s += T("stim_walk") + [R(), W(0.3), C("+forward"), W(1.5), C("-forward"), U("hmax", 0.5, 2), W(0.2)]
    s += T("stim_kick") + [R(), W(0.3), C("hsd_kick 0 300 0"), W(1.0)]
    s += T("stim_sprint") + [R(), W(0.3), C("+speed"), C("+forward"), W(2.0), C("-forward"), C("-speed"),
                             U("hmax", 0.5, 3)]
    s += T("-") + [W(2.0)]
    return s


def t5_air():
    """T-L01/L02 lurch, T-J02 residual air accel, T-J03 skip."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # lurch: sprint forward, jump, then a new right press t s after take-off
    for name, t in (("lurch_none", None), ("lurch_010", 0.10), ("lurch_030", 0.30), ("lurch_045", 0.45),
                    ("lurch_060", 0.60), ("lurch_010b", 0.10)):
        s += T(name) + [R(), W(0.3), C("+speed"), C("+forward"), W(1.0), C("+jump"), U("air", 0, 1), C("-jump")]
        if t is not None:
            s += [W(t), C("+moveright")]
        s += [U("ground", 0, 3), W(0.05)] + release() + [U("hmax", 0.5, 3)]
    # right held from the ground (no new press in the air)
    s += T("lurch_held") + [R(), W(0.3), C("+speed"), C("+forward"), W(1.0), C("+moveright"), W(0.3), C("+jump"),
                            U("air", 0, 1), C("-jump"), U("ground", 0, 3), W(0.05)] + release() + [U("hmax", 0.5, 3)]
    # residual air accel: in the air at 300 u/s, no input vs right held vs forward held
    for name, key in (("air_none", None), ("air_right", "moveright"), ("air_fwd", "forward")):
        s += T(name)
        if key:
            s += [C("+" + key), W(0.1)]
        s += [R(z=400, vy=300), U("ground", 0, 3), W(0.05)] + release() + [U("hmax", 0.5, 3)]
    # slow air strafe (h < airSpeed 60)
    s += T("air_slow") + [C("+moveright"), W(0.1), R(z=300, vy=30), U("ground", 0, 3)] + release() + [W(0.3)]
    # skip: land at h, jump at once (< 0.1 s) or late (0.25 s)
    for name, h, late in (("skip_600", 600, 0), ("skip_460", 460, 0), ("skip_350", 350, 0),
                          ("skip_600_late", 600, 0.25), ("skip_600b", 600, 0)):
        s += T(name) + [R(y=-1800, z=30, vy=h, vz=-50), U("ground", 0, 2)]
        if late:
            s += [W(late)]
        s += [C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), U("ground", 0, 3), W(0.3)]
    s += T("-") + [W(1.0)]
    return s


def t5_slide():
    """T-S01/S02 slide boost and cooldown, T-S06 slide jump."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # first slide (boost), second within 2 s (no boost), third > 2 s after the first (boost)
    s += T("slide_seq") + [R(), W(0.3), C("+speed"), C("+forward"), W(1.0), C("+duck"), W(0.4), C("-duck"), W(0.6),
                           C("+duck"), W(0.4), C("-duck"), W(1.6), C("+duck"), W(0.4), C("-duck"), W(0.3)] + release() + [
        U("hmax", 0.5, 3), W(0.3)]
    # slide held to the end (decay)
    s += T("slide_long") + [W(1.5), R(), W(0.3), C("+speed"), C("+forward"), W(1.0), C("+duck"), W(2.0)] + release() + [
        U("hmax", 0.5, 3), W(0.3)]
    # slide jump
    for i in range(2):
        s += T("slide_jump%d" % i) + [W(2.2), R(), W(0.3), C("+speed"), C("+forward"), W(1.0), C("+duck"), W(0.25),
                                      C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), C("-duck"), U("ground", 0, 3),
                                      W(0.05)] + release() + [U("hmax", 0.5, 3)]
    # slide from a fast kick (h 500): the 400 cap means no boost
    s += T("slide_fast") + [W(2.2), R(vy=500), C("+forward"), C("+duck"), W(1.0)] + release() + [U("hmax", 0.5, 3)]
    # slide under stim
    s += T("slide_stim") + [W(2.2), C("hsd_stim 6"), R(), W(0.3), C("+speed"), C("+forward"), W(1.0), C("+duck"),
                            W(1.0)] + release() + [U("hmax", 0.5, 3)]
    s += T("-") + [W(1.0)]
    return s


def WR(y=-1400, z=150, vx=-40, vy=300, vz=0, yaw=90):
    return R(x=WALL_X + 18, y=y, z=z, vx=vx, vy=vy, vz=vz, yaw=yaw)


def t5_wall():
    """T3 section 6: start boost, gravity ramp, duration, slip, wall jump, back cap, re-attach."""
    s = [C("hsd_weapon mp_weapon_rspn101"), C("hsd_trace -942 -1000 100 -942 -1000 1500"), W(0.5)]
    for i in range(2):
        s += T("wr_none%d" % i) + [WR(), U("wallrun", 0, 1), U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    for i in range(2):
        s += T("wr_fwd%d" % i) + [C("+forward"), WR(), U("wallrun", 0, 1), U("nowallrun", 0, 4), C("-forward"),
                                  U("ground", 0, 3), W(0.3)]
    s += T("wr_fall") + [WR(z=300, vz=-300), U("wallrun", 0, 1), U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    s += T("wr_slow") + [WR(vy=80), U("wallrun", 0, 1), U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    s += T("wr_fast") + [WR(vy=600), U("wallrun", 0, 1), U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    for name, key in (("wj_none", None), ("wj_fwd", "forward"), ("wj_right", "moveright")):
        s += T(name) + [WR(), U("wallrun", 0, 1), W(0.5)]
        if key:
            s += [C("+" + key), W(0.05)]
        s += [C("+jump"), W(0.05), C("-jump"), U("nowallrun", 0, 1), U("ground", 0, 3)] + release() + [W(0.3)]
    # wall jump early in the run (vz still high) and late (sliding down)
    for name, t in (("wj_early", 0.1), ("wj_late", 1.6)):
        s += T(name) + [WR(), U("wallrun", 0, 1), W(t), C("+jump"), W(0.05), C("-jump"), U("ground", 0, 3), W(0.3)]
    # facing backward (yaw 270) while moving +y; the back key pushes along +y
    s += T("wr_back") + [C("+back"), WR(yaw=270), U("wallrun", 0, 1), U("nowallrun", 0, 4), C("-back"),
                         U("ground", 0, 3), W(0.3)]
    # re-attach to the same wall after a wall jump: kick back toward it t s later
    for name, t, vz in (("re_025", 0.25, 0), ("re_060", 0.6, 0), ("re_100", 1.0, -100)):
        s += T(name) + [WR(), U("wallrun", 0, 1), W(0.3), C("+jump"), W(0.05), C("-jump"), U("nowallrun", 0, 1),
                        W(t), C("hsd_kick -250 250 %d" % vz), W(0.6), U("ground", 0, 3), W(0.3)]
    # start from the ground: sprint along the wall, jump, steer into it (the 0x2588 timer)
    for name, steer in (("gj_left", 0.0), ("gj_left_late", 0.4)):
        s += T(name) + [R(x=WALL_X + 30, y=-1450, z=2), W(0.3), C("+speed"), C("+forward"), W(0.8), C("+jump"),
                        U("air", 0, 1), C("-jump"), W(steer), C("+moveleft"), U("wallrun", 0, 1.5),
                        U("ground", 0, 4)] + release() + [W(0.3)]
    s += T("-") + [W(1.0)]
    return s


def t5_djump():
    """Double jump: height rule and the 180 u/s horizontal redirect."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    cases = (("dj_none", None, 0.3), ("dj_right", "moveright", 0.3), ("dj_back", "back", 0.3),
             ("dj_early", None, 0.05), ("dj_fall", None, 0.6), ("dj_right_slow", "moveright", 0.3))
    for name, key, t in cases:
        s += T(name) + [R(), W(0.3)]
        if name != "dj_right_slow":
            s += [C("+speed"), C("+forward"), W(1.0)]
        s += [C("+jump"), U("air", 0, 1), C("-jump"), W(t)]
        if key:
            s += [C("-forward"), C("+" + key), W(0.02)]
        s += [C("+jump"), W(0.05), C("-jump"), U("ground", 0, 3), W(0.05)] + release() + [U("hmax", 0.5, 3), W(0.2)]
    s += T("-") + [W(1.0)]
    return s


def RA(**kw):
    """teleport into the air and wait until the client sees it (U("ground") right after a
    teleport otherwise passes on the stale pre-teleport frame: t5_air run, 2026-10-29)"""
    return [R(**kw), W(0.05), U("air", 0, 1)]


def t5_air2():
    """Re-run of the air strafe and skip trials with the teleport race fixed; skip delays
    bracket the 0.1 s window."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    for name, key, h in (("air_none", None, 300), ("air_right", "moveright", 300), ("air_fwd", "forward", 300),
                         ("air_back", "back", 300), ("air_slow_right", "moveright", 30), ("air_slow_fwd", "forward", 30)):
        s += T(name)
        if key:
            s += [C("+" + key), W(0.1)]
        s += RA(z=400, vy=h) + [U("ground", 0, 3), W(0.05)] + release() + [U("hmax", 0.5, 3)]
    for h, delays in ((600, (0.0, 0.05, 0.08, 0.12, 0.2)), (460, (0.0,)), (440, (0.0,)), (350, (0.0, 0.2))):
        for d in delays:
            s += T("skip_%d_%03d" % (h, d * 1000)) + RA(y=-1800, z=30, vy=h, vz=-50) + [U("ground", 0, 2)]
            if d:
                s += [W(d)]
            s += [C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), U("ground", 0, 3), W(0.3)]
    # normal jump from standing, for the logged take-off vz offset
    s += T("jump_stand") + [R(), W(0.3), C("+jump"), W(0.05), C("-jump"), U("air", 0, 1), U("ground", 0, 3), W(0.3)]
    s += T("-") + [W(1.0)]
    return s


GJ = (WALL_X + 30, -1250)  # clear floor next to the west wall (probe2: no clutter at y=-1250)


def t5_wall2():
    """Follow-up to t5_wall: teleported starts showed full gravity and no up-boost, so test
    starts shortly after leaving the ground (jump, then kick into the wall), rising starts,
    long runs at z 400 (time limit / slip), and re-attach above the last contact point."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # jump from the ground next to the wall, kick into it t s after take-off
    for name, t, vz in (("gk_000", 0.0, 280), ("gk_010", 0.1, 230), ("gk_030", 0.3, 100), ("gk_060", 0.6, -60),
                        ("gk_000b", 0.0, 280)):
        s += T(name) + [R(x=GJ[0], y=GJ[1], z=2), W(0.4), C("+jump"), U("air", 0, 1), C("-jump")]
        if t:
            s += [W(t)]
        s += [C("hsd_kick -150 250 %d" % vz), U("wallrun", 0, 1.2), U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    # same kick from a teleport in the air (no recent ground contact)
    s += T("tk_280") + RA(x=GJ[0], y=GJ[1], z=40) + [C("hsd_kick -150 250 280"), U("wallrun", 0, 1.2),
                                                       U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    # teleported rising starts
    for vz in (100, 200, 300):
        s += T("wr_up%d" % vz) + [WR(vz=vz), U("wallrun", 0, 1), U("nowallrun", 0, 4), U("ground", 0, 3), W(0.3)]
    # long runs high on the wall: time limit and slip
    s += T("wr_hi_none") + [WR(z=420), U("wallrun", 0, 1), U("nowallrun", 0, 4), U("ground", 0, 4), W(0.3)]
    for i in range(2):
        s += T("wr_hi_fwd%d" % i) + [C("+forward"), WR(z=420), U("wallrun", 0, 1), U("nowallrun", 0, 4),
                                     C("-forward"), U("ground", 0, 4), W(0.3)]
    # ground start with forward held (the in-game way): jump, kick, hold forward
    s += T("gk_fwd") + [R(x=GJ[0], y=GJ[1], z=2), W(0.4), C("+forward"), C("+jump"), U("air", 0, 1), C("-jump"),
                        C("hsd_kick -150 250 280"), U("wallrun", 0, 1.2), U("nowallrun", 0, 4), C("-forward"),
                        U("ground", 0, 4), W(0.3)]
    # re-attach above the last contact: wall jump, then kick back up into the wall
    for name, t, vz in (("re_up_020", 0.2, 250), ("re_up_045", 0.45, 250), ("re_dn_045", 0.45, -250)):
        s += T(name) + [WR(z=300), U("wallrun", 0, 1), W(0.3), C("+jump"), W(0.05), C("-jump"), U("nowallrun", 0, 1),
                        W(t), C("hsd_kick -250 200 %d" % vz), W(0.8), U("ground", 0, 4), W(0.3)]
    s += T("-") + [W(1.0)]
    return s


def t5_slide2():
    """Slide boost returning after the 2 s cooldown (teleports keep the lane short) and the
    slide jump below and above slideMaxJumpSpeed 350."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    # slides at 0, then 1.5 s, 1.9 s, 2.1 s after it; each from a fresh 260 u/s sprint
    s += T("cool_seq") + [C("+speed"), C("+forward")]
    for gap in (0.0, 1.5, 0.4, 0.2):  # cumulative 0, 1.5, 1.9, 2.1
        if gap:
            s += [W(gap - 0.25)]
        s += [R(vy=260), W(0.2), C("+duck"), W(0.05), C("-duck")]
    s += [W(0.3)] + release() + [U("hmax", 0.5, 3), W(2.5)]
    s += T("cool_25") + [C("+speed"), C("+forward"), R(vy=260), W(0.2), C("+duck"), W(0.05), C("-duck"), W(2.25),
                         R(vy=260), W(0.2), C("+duck"), W(0.05), C("-duck"), W(0.3)] + release() + [U("hmax", 0.5, 3), W(2.5)]
    # slide jump at lower speed: slide from 260 and let it decay before jumping
    for name, wait in (("sj_late", 0.9), ("sj_late2", 0.9)):
        s += T(name) + [C("+speed"), C("+forward"), R(vy=260), W(0.2), C("+duck"), W(wait), C("+jump"), W(0.05),
                        C("-jump"), U("air", 0, 1), C("-duck"), U("ground", 0, 3), W(0.05)] + release() + [
            U("hmax", 0.5, 3), W(2.2)]
    # slide jump from a fast slide (kicked to 480 on the ground)
    s += T("sj_fast") + [C("+forward"), R(vy=480), W(0.03), C("+duck"), W(0.15), C("+jump"), W(0.05), C("-jump"),
                         U("air", 0, 1), C("-duck"), U("ground", 0, 3), W(0.05)] + release() + [U("hmax", 0.5, 3)]
    s += T("-") + [W(1.0)]
    return s


def bt_scan():
    """BT-2 (contact far above the take-off point: does TF2 have a height gate?) and a floor scan
    near the west wall to find a ledge for BT-1. <= ~17 commands/s (stringcmd quota)."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    for i, vz in enumerate((500, 700, 500)):
        s += T("bt2_%d_%d" % (vz, i)) + [R(x=GJ[0], y=GJ[1], z=2), W(0.4), C("+jump"), U("air", 0, 1), C("-jump"),
                                         C("hsd_kick -150 250 %d" % vz), U("wallrun", 0, 1.5), U("nowallrun", 0, 4),
                                         U("ground", 0, 4), W(0.3)]
    for x in range(-950, -549, 50):
        for y in range(-2400, -1449, 50):
            s += [C("hsd_trace %d %d 400 %d %d -400" % (x, y, x, y)), W(0.07)]
    s += T("-") + [W(1.0)]
    return s


def bt_ledge():
    """BT-1: walk off the pit edge south-west of the west wall (floor 0 -> -128) without jumping
    and steer into the wall (prediction: no boost, no ramp), with a jump-off control; BT-2b:
    contact ~280 above the take-off (kick up first, then into the wall)."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    for y in (-1850, -1950, -2050):
        for z in (-100, -60, -20):
            s += [C("hsd_trace -900 %d %d -1100 %d %d" % (y, z, y, z)), W(0.07)]
    # facing -y (yaw 270): right = -x = into the wall at x -960
    for i in range(3):
        s += T("bt1_walk_%d" % i) + [R(x=-935, y=-1700, z=2, yaw=270), W(0.4), C("+forward"), C("+moveright"),
                                     U("air", 0, 2), U("wallrun", 0, 1.5), U("nowallrun", 0, 3), U("ground", 0, 3)] + release() + [W(0.3)]
        s += T("bt1_jump_%d" % i) + [R(x=-935, y=-1700, z=2, yaw=270), W(0.4), C("+forward"), C("+moveright"),
                                     W(0.15), C("+jump"), U("air", 0, 1), C("-jump"), U("wallrun", 0, 1.5),
                                     U("nowallrun", 0, 3), U("ground", 0, 3)] + release() + [W(0.3)]
    for i in range(3):
        s += T("bt2b_%d" % i) + [R(x=GJ[0] + 20, y=GJ[1], z=2), W(0.4), C("+jump"), U("air", 0, 1), C("-jump"),
                                 C("hsd_kick 0 0 700"), W(0.5), C("hsd_kick -200 250 0"), U("wallrun", 0, 1.5),
                                 U("nowallrun", 0, 4), U("ground", 0, 4), W(0.3)]
    s += T("-") + [W(1.0)]
    return s


def bt_ledge2():
    """BT-1 retry: the t5 bt_ledge walk start was blocked at the edge (stuck at -941, -1741).
    Walk south-west (yaw 225) off the diagonal pit edge from several starts, toward the pit's west
    wall (x -992, normal +x), no jump; jump-off control from the same start."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    for sx, sy in ((-820, -1720), (-760, -1800), (-700, -1880)):
        for kind in ("walk", "jump"):
            s += T("bt1b_%s_%d_%d" % (kind, -sx, -sy)) + [R(x=sx, y=sy, z=2, yaw=225), W(0.4), C("+forward")]
            if kind == "jump":
                s += [W(0.25), C("+jump"), U("air", 0, 1), C("-jump")]
            s += [U("air", 0, 3), U("wallrun", 0, 1.5), U("nowallrun", 0, 3), U("ground", 0, 3)] + release() + [W(0.3)]
    s += T("-") + [W(1.0)]
    return s


def bt_box():
    """BT-1, third try: the pit edge has an invisible railing (walkers stop, jumpers pass). Land on
    the z~268 box (x -700..-650, y -1550..-1500), walk off its west edge, and on the first air
    frame kick toward the west wall (a kick is not a jump); control: jump off the same edge."""
    s = [C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    for i in range(3):
        for kind in ("walk", "jump"):
            s += T("bt1c_%s_%d" % (kind, i)) + [R(x=-665, y=-1525, z=300, yaw=180), U("ground", 0, 3), W(0.5),
                                                C("+forward")]
            if kind == "jump":
                s += [W(0.12), C("+jump")]
            s += [U("air", 0, 3), C("-jump"), C("hsd_kick -350 200 %d" % (0 if kind == "walk" else 250)),
                  U("wallrun", 0, 1.5), U("nowallrun", 0, 3), U("ground", 0, 3)] + release() + [W(0.3)]
    s += T("-") + [W(1.0)]
    return s
