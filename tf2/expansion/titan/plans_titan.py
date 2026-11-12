"""T0 titan plans (runner.py; mod script hsd_diag_titan.gnut). See T0-REPORT.md.
mp_lf_stacks spawn: player at (24, -1864, 1) facing yaw 90 (+y); ~570 u of open floor ahead.
Mouse steps (hsd_mouse) need `runner.py <plan> --mouse`; the runner sends the moves (titan_mouse.py).
"""
from plans import C, W, U


def M(name, dx, dy, count, interval_ms):
    """Scripted mouse burst: count moves of (dx, dy) counts, one every interval_ms (runner --mouse)."""
    return C("hsd_mouse %s %d %d %d %g" % (name, dx, dy, count, interval_ms))


def t0_smoke():
    """Tooling check: keyboard and mouse turn as pilot, spawn Ronin, animated embark, turn, dash,
    disembark; then Scorch with the instant embark."""
    return [
        C("hsd_info"), C("hsd_titan_info"),
        C("hsd_tag kb_pilot"), C("+right"), W(1.0), C("-right"), W(0.5),
        C("hsd_tag ms_pilot"), M("ms_pilot", 10, 0, 200, 5), W(3.0),
        C("hsd_tag spawn"), C("hsd_titan ronin 24 -1450 1 -90"), W(3.0),
        C("hsd_setup 24 -1650 1 0 0 0 0 90"), W(0.5),
        C("hsd_tag embark_anim"), C("hsd_embark 1"), W(8.0),
        C("hsd_titan_info"),
        C("hsd_tag kb_titan"), C("+right"), W(1.0), C("-right"), W(0.5),
        C("hsd_tag ms_titan"), M("ms_titan", 10, 0, 200, 5), W(3.0),
        C("hsd_tag dash"), C("+moveleft"), W(0.1), C("+dodge"), W(0.1), C("-dodge"), W(0.6), C("-moveleft"), W(1.0),
        C("hsd_titan_info"),
        C("hsd_tag disembark"), C("hsd_disembark"), W(6.0),
        C("hsd_info"),
        C("hsd_tag scorch"), C("hsd_titan scorch 300 -1450 1 90"), W(2.0),
        C("hsd_embark 0"), W(4.0), C("hsd_titan_info"),
        C("hsd_tag kb_scorch"), C("+right"), W(1.0), C("-right"), W(0.5),
        C("hsd_tag -"),
    ]


TITANS = ["ronin", "northstar", "ion", "tone", "monarch", "scorch", "legion"]


def _ride(cls, x=24, y=-1450):
    """spawn <cls> ahead of the player, instant embark, let the cockpit boot and the titan stand"""
    return [C("hsd_tag spawn_" + cls), C("hsd_titan %s %d %d 1 90" % (cls, x, y)), W(1.5),
            C("hsd_setup %d %d 1 0 0 0 0 90" % (x, y - 150)), W(0.3),
            C("hsd_embark 0"), W(3.0), C("+forward"), W(0.3), C("-forward"), W(1.5), C("hsd_titan_info")]


def _turn_block(name):
    """identical look input: keyboard yaw at 210 and 1500 deg/s, pitch, turn_slow 0.25, mouse burst"""
    return [
        C("hsd_tag kb_" + name), C("+right"), W(1.0), C("-right"), W(0.4),
        C("cl_yawspeed 1500"), C("hsd_tag kbfast_" + name), C("+left"), W(0.5), C("-left"), W(0.4), C("cl_yawspeed 210"),
        C("hsd_tag pitch_" + name), C("+lookdown"), W(0.4), C("-lookdown"), C("+lookup"), W(0.4), C("-lookup"), W(0.4),
        C("hsd_status turn_slow 0.25 2.5 0"), W(0.1), C("hsd_tag slow_" + name), C("+right"), W(1.0), C("-right"), W(1.6),
        C("hsd_tag ms_" + name), M("ms_" + name, 10, 0, 200, 5), W(2.5),
        C("hsd_tag msads_" + name), C("+zoom"), W(0.6), M("msads_" + name, 10, 0, 200, 5), W(2.5), C("-zoom"), W(0.5),
    ]


def t0_turn():
    """Turn rate: pilot, then each of the 7 titans with the same inputs (_turn_block)."""
    steps = [C("hsd_tag kb_pilot"), C("+right"), W(1.0), C("-right"), W(0.4)]
    steps = _turn_block("pilot")
    for cls in TITANS:
        steps += _ride(cls) + _turn_block(cls) + [C("hsd_tag out_" + cls), C("hsd_disembark"), W(3.0)]
    return steps + [C("cl_yawspeed 210"), C("hsd_tag -")]


def _move_block(cls):
    """standing titan on a titan-hull lane: start (-800, -1400) toward +x, ~1360 u clear
    (hsd_lanes, run 20261030_015621_t0_lanes; thin line traces missed props and stopped the hull,
    runs 20261030_014323 / 014930_t0_move): walk, sprint key, back / side walk, dash keys, power regen"""
    lane = "hsd_setup -800 -1400 7 0 0 0 0 0"
    lane_back = "hsd_setup 500 -1400 7 0 0 0 0 0"   # facing +x, walks back toward -x
    lane_side = "hsd_setup -800 -1400 7 0 0 0 0 90"  # facing +y, strafes right toward +x
    return [
        C(lane), W(1.0),
        C("hsd_tag walk_" + cls), C("+forward"), W(2.0), C("-forward"), W(1.5),
        C(lane), W(1.0),
        C("hsd_tag sprint_" + cls), C("+forward"), C("+speed"), W(2.4), C("-speed"), C("-forward"), W(1.5),
        C(lane_back), W(1.0),
        C("hsd_tag back_" + cls), C("+back"), W(1.6), C("-back"), W(1.2),
        C(lane_side), W(1.0),
        C("hsd_tag side_" + cls), C("+moveright"), W(1.6), C("-moveright"), W(1.2),
        C(lane), W(0.5), C("hsd_dodgepower 100"), W(0.5),
        C("hsd_tag dodge_" + cls), C("+forward"), W(0.6), C("+dodge"), W(0.3), C("-dodge"), W(1.2), C("-forward"), W(1.0),
        C(lane_side), W(0.5), C("hsd_dodgepower 100"), W(0.5),
        C("hsd_tag dodgeside_" + cls), C("+moveright"), W(0.4), C("+dodge"), W(0.2), C("-dodge"), W(0.5),
        C("+dodge"), W(0.2), C("-dodge"), W(0.5), C("+dodge"), W(0.2), C("-dodge"), W(0.6), C("-moveright"),
        C("hsd_tag regen_" + cls), W(8.0),
        C("hsd_titan_info"),
    ]


def t0_move():
    """Chassis movement per titan: walk / sprint / back / side curves, dash speed and power, regen."""
    steps = [C("hsd_tag pilot_walk"), C("hsd_setup -800 -1400 7 0 0 0 0 0"), W(1.0), C("+forward"), W(2.0), C("-forward"), W(1.0)]
    for cls in TITANS:
        steps += _ride(cls) + _move_block(cls) + [C("hsd_tag out_" + cls), C("hsd_disembark"), W(3.0)]
    return steps + [C("hsd_tag -")]


PROBE_POINTS = [(24, -1650), (300, -1400), (0, -1000), (500, -1000), (-400, -1000), (800, -1400), (0, -500), (600, -500), (-500, -1450)]


def t0_probe():
    """Find a straight lane wide enough for a titan hull (120 x 235): horizontal traces from several floor points."""
    steps = []
    for x, y in PROBE_POINTS:
        steps += [C("hsd_setup %d %d 40 0 0 0 0 90" % (x, y)), U("air", 0, 0.5), U("ground", 0, 3.0), W(0.2), C("hsd_probe 3000"), W(0.3)]
    return steps


def t0_lanes():
    """titan-hull lane search over mp_lf_stacks (hsd_lanes); the t0_probe line traces missed props"""
    return [C("hsd_lanes -900 -2000 1400 -100 100 1500 650"), W(15.0)]


KEYS = [("off0", "+offhand0", "-offhand0"), ("off1", "+offhand1", "-offhand1"), ("off2", "+offhand2", "-offhand2"),
        ("ab6", "+ability 6", "-ability 6"), ("ab3", "+ability 3", "-ability 3")]


def _kit_block(cls):
    """kit items that change movement: ADS walk, walk while holding each key, each key tapped on its own
    (titan_info after each shows which offhand fired: clip / charge), then the core while walking."""
    lane = "hsd_setup -800 -1400 7 0 0 0 0 0"
    steps = [C(lane), W(1.0),
             C("hsd_tag adswalk_" + cls), C("+zoom"), W(0.6), C("+forward"), W(1.5), C("-forward"), C("-zoom"), W(1.0)]
    for name, down, up in KEYS:
        steps += [C(lane), W(0.8), C("hsd_dodgepower 100"),
                  C("hsd_tag key%s_%s" % (name, cls)), C("+forward"), W(0.4), C(down), W(0.15), C(up), W(1.6), C("-forward"),
                  W(1.5), C("hsd_titan_info"), W(2.5)]
    # hold the defensive (block / shield / vortex) while walking
    steps += [C(lane), W(0.8), C("hsd_tag holdoff1_" + cls), C("+offhand1"), W(0.5), C("+forward"), W(1.5), C("-forward"),
              C("-offhand1"), W(1.0)]
    steps += [C(lane), W(0.8), C("hsd_core"), W(0.3),
              C("hsd_tag core_" + cls), C("+forward"), W(0.3), C("+ability 1"), W(0.15), C("-ability 1"), W(7.0), C("-forward"),
              W(1.0), C("hsd_titan_info"), W(3.0)]
    return steps


def t0_kit():
    steps = []
    for cls in TITANS:
        steps += _ride(cls) + _kit_block(cls) + [C("hsd_tag out_" + cls), C("hsd_disembark"), W(3.0)]
    return steps + [C("hsd_tag -")]


def t0_mouseslow():
    """Real mouse (runner --mouse) under turn_slow: Ion, the same 2000-count burst with severity 0, 0.25, 0.5."""
    steps = _ride("ion")
    for sev in ("0", "0.25", "0.5"):
        tag = "msslow%s_ion" % sev.replace(".", "")
        if sev != "0":
            steps += [C("hsd_status turn_slow %s 3.5 0" % sev), W(0.1)]
        steps += [C("hsd_tag " + tag), M(tag, 10, 0, 200, 5), W(2.5), C("hsd_tag gap_" + tag), W(1.5)]
    return steps + [C("hsd_tag -")]


# --- pose / camera survey (2026-11-02, expansion/titan/pose/) ---

LANE = "hsd_setup -800 -1400 7 0 0 0 0 0"
SHOT = lambda n: C("jpeg t1_%s 90" % n)


def _cam_block(cls):
    """every movement state, each tagged, on the titan lane; camera, cockpit, FOV and body logged per frame."""
    s = [C(LANE), W(1.0), C("hsd_tag idle_" + cls), W(2.0), SHOT("idle_" + cls), W(0.5)]
    s += [C(LANE), W(0.8), C("hsd_tag walk_" + cls), C("+forward"), W(1.5), SHOT("walk_" + cls), W(1.0), C("-forward"), W(1.2)]
    s += [C(LANE), W(0.8), C("hsd_tag sprint_" + cls), C("+forward"), C("+speed"), W(2.2), SHOT("sprint_" + cls), W(0.3), C("-speed"), C("-forward"), W(1.5)]
    s += [C("hsd_setup 500 -1400 7 0 0 0 0 0"), W(0.8), C("hsd_tag back_" + cls), C("+back"), W(1.5), C("-back"), W(1.0)]
    s += [C("hsd_setup -800 -1400 7 0 0 0 0 90"), W(0.8), C("hsd_tag strafe_" + cls), C("+moveright"), W(1.5), SHOT("strafe_" + cls), C("-moveright"), W(1.0)]
    for name, key, setup in (("f", "+forward", LANE), ("r", "+moveright", "hsd_setup -800 -1400 7 0 0 0 0 90"), ("b", "+back", "hsd_setup 500 -1400 7 0 0 0 0 0")):
        off = "-" + key[1:]
        s += [C(setup), W(0.6), C("hsd_dodgepower 100"), W(0.2), C("hsd_tag dash%s_%s" % (name, cls)), C(key), W(0.3), C("+ability 3"), W(0.08), SHOT("dash%s_%s" % (name, cls)), W(0.1), C("-ability 3"), W(1.0), C(off), W(1.0)]
    s += [C(LANE), W(0.6), C("hsd_tag crouch_" + cls), C("+duck"), W(1.5), SHOT("crouch_" + cls), W(0.3), C("+forward"), W(1.0), C("-forward"), C("-duck"), W(1.5)]
    s += [C(LANE), W(0.6), C("hsd_tag ads_" + cls), C("+zoom"), W(1.0), SHOT("ads_" + cls), W(0.3), C("-zoom"), W(1.0)]
    s += [C(LANE), W(0.6), C("hsd_tag fire_" + cls), C("+attack"), W(0.4), SHOT("fire_" + cls), W(1.1), C("-attack"), W(1.5)]
    s += [C("hsd_tag adsfire_" + cls), C("+zoom"), W(0.6), C("+attack"), W(1.0), C("-attack"), C("-zoom"), W(1.5)]
    s += [C(LANE), W(0.6), C("hsd_tag melee_" + cls), C("+melee"), W(0.2), SHOT("melee_" + cls), W(0.1), C("-melee"), W(1.5)]
    # turn in place, body logged: steps of yaw
    s += [C("hsd_tag turn30_" + cls), C("hsd_setup -800 -1400 7 0 0 0 0 30"), W(1.5), C("hsd_tag turn90_" + cls), C("hsd_setup -800 -1400 7 0 0 0 0 90"), W(1.5), C("hsd_tag turn180_" + cls), C("hsd_setup -800 -1400 7 0 0 0 0 180"), W(1.5)]
    return s


def _damage_block(cls):
    """shield hit, hull hits to each damage stage, doomed, EMP, eject."""
    s = [C(LANE), W(0.6), C("hsd_shield 2500"), W(0.2), C("hsd_tag hurtshield_" + cls), C("hsd_hurt 1000 0"), W(0.1), SHOT("hurtshield_" + cls), W(1.5), C("hsd_shield 0"), W(0.2)]
    s += [C("hsd_tag hurtbig_" + cls), C("hsd_hurt 2000 0"), W(0.05), SHOT("hurtbig_" + cls), W(1.5)]
    s += [C("hsd_tag hurtside_" + cls), C("hsd_hurt 1500 90"), W(1.5)]
    s += [C("hsd_tag emp_" + cls), C("hsd_emp 2"), W(0.3), SHOT("emp_" + cls), W(3.0)]
    s += [C("hsd_core"), W(0.3), C("hsd_tag core_" + cls), C("+ability 1"), W(0.15), C("-ability 1"), W(0.5), SHOT("core_" + cls), W(4.0)]
    s += [C("hsd_tag doom_" + cls), C("hsd_hurt 20000 0"), W(0.2), SHOT("doom_" + cls), W(1.5), C("+forward"), W(1.5), C("-forward"), W(1.0)]
    s += [C("hsd_tag eject_" + cls), C("hsd_eject"), W(0.5), SHOT("eject1_" + cls), W(2.0), SHOT("eject2_" + cls), W(1.0), SHOT("eject3_" + cls), W(5.0)]
    return s


def _outside_block(cls):
    """pilot watching an auto-titan: body effects per damage stage, which the player's own view hides."""
    s = [C("hsd_tag ext_spawn_" + cls), C("hsd_titan %s 24 -1450 1 -90" % cls), W(4.0), C("hsd_setup 24 -1850 1 0 0 0 -8 90"), W(1.0), SHOT("ext0_" + cls), W(0.5)]
    s += [C("hsd_shield 2500"), W(0.5), C("hsd_tag ext_shield_" + cls), C("hsd_hurtpet 500"), W(0.15), SHOT("extshield_" + cls), W(1.0), C("hsd_shield 0"), W(0.5)]
    for frac in (1, 2, 3):
        s += [C("hsd_tag ext_stage%d_%s" % (frac, cls)), C("hsd_hurtpet 2500"), W(1.5), SHOT("extstage%d_%s" % (frac, cls)), W(0.5)]
    s += [C("hsd_tag ext_doom_" + cls), C("hsd_hurtpet 3000"), W(1.5), SHOT("extdoom_" + cls), W(2.0), SHOT("extdoom2_" + cls), W(2.0)]
    s += [C("hsd_tag ext_dead_" + cls), C("hsd_hurtpet 20000"), W(0.4), SHOT("extdead1_" + cls), W(0.8), SHOT("extdead2_" + cls), W(4.0)]
    return s


def t1_camsmoke():
    """tooling check for the survey: one titan, screenshots, damage, EMP, eject"""
    return _ride("ion") + [C("hsd_tag idle"), W(1.0), SHOT("smoke"), W(1.0), C("thirdperson"), W(1.0), SHOT("smoke3p"), W(1.0), C("firstperson"), C("hsd_tag hurt"), C("hsd_hurt 3000 0"), W(1.0), C("hsd_tag emp"), C("hsd_emp 2"), W(2.5), C("hsd_tag doom"), C("hsd_hurt 20000 0"), W(1.5), C("hsd_tag eject"), C("hsd_eject"), W(6.0), C("hsd_tag -")]


def t1_cam():
    """pose/camera survey, one titan per chassis plus an animated embark and disembark"""
    steps = []
    for cls in ("ronin", "ion", "legion"):
        steps += [C("hsd_tag spawn_" + cls), C("hsd_titan %s 24 -1450 1 90" % cls), W(1.5), C("hsd_setup 24 -1650 1 0 0 0 0 90"), W(0.5),
                  C("hsd_tag embarkanim_" + cls), C("hsd_embark 1"), W(1.0), SHOT("embark1_" + cls), W(1.0), SHOT("embark2_" + cls), W(1.0), SHOT("embark3_" + cls), W(4.0)]
        steps += _cam_block(cls)
        steps += [C("hsd_tag disembark_" + cls), C("hsd_disembark"), W(0.5), SHOT("disembark1_" + cls), W(0.7), SHOT("disembark2_" + cls), W(3.0)]
        steps += _ride(cls) + _damage_block(cls) + [W(3.0)]
        steps += _outside_block(cls)
    return steps + [C("hsd_tag -")]


def _ext_views(cls):
    """auto-titan seen from a fixed offset; the pilot is re-placed before each picture because it follows"""
    w = lambda r=30: C("hsd_watch 480 %d 60" % r)
    s = [C("hsd_tag ext_spawn_" + cls), C("hsd_titan %s 24 -1450 7 90" % cls), W(5.0)]
    for name, rel in (("front", 0), ("q34", 40), ("side", 90), ("back", 180)):
        s += [w(rel), W(0.4), SHOT("ext2_%s_%s" % (name, cls)), W(0.3)]
    s += [C("hsd_shield 2500"), W(0.3), w(), W(0.2), C("hsd_tag ext_shield_" + cls), C("hsd_hurtpet 500"), W(0.12), SHOT("ext2_shield_" + cls), W(1.0), C("hsd_shield 0"), W(0.3)]
    hp = {"ronin": 2200, "ion": 2900, "legion": 3600}[cls]
    for st in (1, 2, 3):
        s += [C("hsd_tag ext_stage%d_%s" % (st, cls)), C("hsd_hurtpet %d" % hp), W(0.15), w(), W(0.25), SHOT("ext2_hit%d_%s" % (st, cls)), W(1.5), w(), W(0.3), SHOT("ext2_stage%d_%s" % (st, cls)), W(0.3)]
    s += [C("hsd_tag ext_doom_" + cls), C("hsd_hurtpet 9000"), W(0.15), w(), W(0.3), SHOT("ext2_doomhit_" + cls), W(1.5), w(), W(0.3), SHOT("ext2_doom_" + cls), W(1.0), w(150), W(0.3), SHOT("ext2_doomback_" + cls), W(0.5)]
    s += [w(), W(0.2), C("hsd_tag ext_dead_" + cls), C("hsd_hurtpet 20000"), W(0.25), SHOT("ext2_dead1_" + cls), W(0.5), SHOT("ext2_dead2_" + cls), W(1.5), SHOT("ext2_dead3_" + cls), W(3.0)]
    return s


def _look_block(cls):
    """real key turns (body lag, foot steps), pitch limit at both ends"""
    s = [C("hsd_setup -800 -1400 7 0 0 0 0 0"), W(1.2), C("cl_yawspeed 30"), C("hsd_tag ts30_" + cls), C("+right"), W(4.0), C("-right"), W(1.5)]
    s += [C("cl_yawspeed 90"), C("hsd_tag ts90_" + cls), C("+left"), W(2.0), C("-left"), W(1.5)]
    s += [C("cl_yawspeed 300"), C("hsd_tag ts300_" + cls), C("+right"), W(0.6), C("-right"), W(2.0), C("cl_yawspeed 210")]
    s += [C("hsd_setup -800 -1400 7 0 0 0 0 0"), W(0.8), C("cl_pitchspeed 90"), C("hsd_tag pitchup_" + cls), C("+lookup"), W(2.0), SHOT("pitchup_" + cls), W(0.3), C("-lookup"), W(0.5)]
    s += [C("hsd_tag pitchdn_" + cls), C("+lookdown"), W(3.5), SHOT("pitchdn_" + cls), W(0.3), C("-lookdown"), W(0.5), C("hsd_setup -800 -1400 7 0 0 0 0 0"), W(0.8)]
    s += [C("hsd_tag dashl_" + cls), C("hsd_dodgepower 100"), C("hsd_setup 500 -1400 7 0 0 0 0 -90"), W(0.6), C("+moveleft"), W(0.3), C("+ability 3"), W(0.08), C("-ability 3"), W(1.0), C("-moveleft"), W(1.0)]
    s += [C("hsd_tag walkturn_" + cls), C("hsd_setup -800 -1400 7 0 0 0 0 0"), W(0.6), C("+forward"), W(0.8), C("cl_yawspeed 60"), C("+right"), W(1.0), C("-right"), C("-forward"), W(1.0), C("cl_yawspeed 210")]
    return s


def t1_ext():
    """body effects from outside, real key turns, view pitch limits"""
    steps = [C("hsd_tag pilot_pitch"), C("cl_pitchspeed 90"), C("+lookup"), W(2.0), C("-lookup"), C("+lookdown"), W(3.5), C("-lookdown"), W(0.5)]
    for cls in ("ronin", "ion", "legion"):
        steps += _ride(cls) + _look_block(cls) + [C("hsd_tag out_" + cls), C("hsd_disembark"), W(4.0)]
        steps += _ext_views(cls)
    return steps + [C("hsd_tag -")]


def t1_pitch():
    """view pitch limit and upper-body follow: ask for pitch beyond the limit on pilot and titan; left dash"""
    steps = []
    def block(n):
        out = []
        for p in (-89, -70, -45, 0, 45, 70, 89):
            out += [C("hsd_setup -800 -1400 7 0 0 0 %d 0" % p), W(0.5), C("hsd_tag pitch%d_%s" % (p, n)), W(0.8)]
        return out
    steps += block("pilot")
    for cls in ("ronin", "ion", "legion"):
        steps += _ride(cls) + block(cls)
        steps += [C("hsd_dodgepower 100"), C("hsd_setup 500 -1400 7 0 0 0 0 90"), W(0.6), C("hsd_tag dashl_" + cls), C("+moveleft"), W(0.3), C("+ability 3"), W(0.1), C("-ability 3"), W(1.0), C("-moveleft"), W(0.6)]
        steps += [C("hsd_tag out_" + cls), C("hsd_disembark"), W(4.0)]
    return steps + [C("hsd_tag -")]
