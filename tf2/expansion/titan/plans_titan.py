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
