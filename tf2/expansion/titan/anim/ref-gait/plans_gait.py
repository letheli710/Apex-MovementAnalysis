"""ref-titan-gait plans (2026-11-09). Run with runner_gait.py. See REF-GAIT-1109.md.

mp_lf_stacks titan lane (plans_titan._move_block): start (-800, -1400, 7) facing +x, about 1360 u clear.
Speed control: the titan's top walk speed is 250 u/s; lower steady speeds come from
  a) hsd_status move_slow <severity> <duration> 0  (status effect on the soul, as phase dash / cores use)
  b) cl_forwardspeed <u/s> with +forward (Source input scaling)
The smoke run checks which of the two gives a steady speed and what it is.
"""
from plans import C, W  # noqa: F401
from plans_titan import _ride

LANE = "hsd_setup -800 -1400 7 0 0 0 0 0"


def lane(x=-800, y=-1400, z=7, yaw=0):
    return C("hsd_setup %d %d %d 0 0 0 0 %g" % (x, y, z, yaw))


def walk(tag, secs, pre=(), post=(), sprint=False):
    s = [lane(), W(1.2)] + [C(c) for c in pre] + [C("hsd_tag " + tag), C("+forward")]
    if sprint:
        s += [C("+speed")]
    s += [W(secs)]
    if sprint:
        s += [C("-speed")]
    s += [C("-forward"), W(2.0), C("hsd_tag -")] + [C(c) for c in post]
    return s


def gait_smoke():
    """APIs (activity, cycle), log rate, both speed controls, a floor height scan of the map"""
    s = [C("hsd_gait_acts")] + _ride("ion")
    s += walk("sm_walk", 2.5)
    s += walk("sm_ms30", 2.5, pre=["hsd_status move_slow 0.3 5 0"])
    s += walk("sm_ms60", 2.5, pre=["hsd_status move_slow 0.6 5 0"])
    s += walk("sm_fs175", 2.5, pre=["cl_forwardspeed 175"], post=["cl_forwardspeed 450"])
    s += walk("sm_sprint", 2.5, sprint=True)
    s += [C("hsd_gait_hmap -4000 -4000 4000 4000 64 1500"), W(2.0)]
    return s + [C("hsd_disembark"), W(2.0)]


def ms(speed, dur=12.0):
    """move_slow severity for a steady speed (250 * (1 - severity), checked in gait_smoke); it ends
    inside its own segment so effects never stack across segments"""
    return "hsd_status move_slow %.3f %.1f 0" % (1.0 - speed / 250.0, dur)


def seg(tag, secs, speed=None, stop_wait=3.0, sprint_after=None):
    """reset to the lane, optional slow, +forward for secs (optionally +speed after sprint_after s), release, record the stop"""
    s = [lane(), W(1.5)]
    if speed:
        s += [C(ms(speed, secs + 2.0)), W(0.2)]
    s += [C("hsd_tag " + tag), C("+forward")]
    if sprint_after is not None:
        s += [W(sprint_after), C("+speed"), W(secs - sprint_after), C("-speed")]
    else:
        s += [W(secs)]
    s += [C("hsd_tag stop_" + tag), C("-forward"), W(stop_wait), C("hsd_tag -")]
    return s


def gait_a():
    """F6 steady speeds, walk/run threshold sweep, A2 sprint acceleration, A6 stops (mp_lf_stacks lane)"""
    s = _ride("ion")
    s += seg("f6_100", 7.0, 100)
    s += seg("f6_175", 5.5, 175)
    s += seg("f6_250a", 4.5)
    s += seg("f6_250b", 4.5)
    for v in (125, 140, 150, 160, 200, 225):
        s += seg("thr_%d" % v, 4.5, v)
    s += seg("a2_s1", 3.6, sprint_after=1.6)
    s += seg("a2_s2", 3.6, sprint_after=1.6)
    s += seg("a2_s0", 3.4, sprint_after=0.0)   # sprint from standstill
    s += [C("hsd_gait_hmap -4000 -3600 1600 2800 48 300"), W(2.0)]
    return s + [C("hsd_disembark"), W(2.0)]


def gait_b():
    """walk/run threshold around 0.45 * 250 = 112.5 u/s (ref-titan-native's selector rule), start blends, repeats of the stop"""
    s = _ride("ion")
    for v in (105, 110, 115, 120, 112):
        s += seg("thr_%d" % v, 5.0, v)
    for i in range(3):
        s += seg("st_250_%d" % i, 3.0)          # start from idle + stop, full speed
    s += seg("st_110", 4.0, 110)               # start / stop on the walk clip
    s += [C("hsd_gait_hmap -4000 -3600 1600 2800 48 300"), W(2.0)]
    return s + [C("hsd_disembark"), W(2.0)]


def gait_scout():
    """mp_homestead: where the pilot spawns, and a world-brush height map of the whole map (F20 slopes, steps)"""
    s = [C("hsd_info"), W(0.5)]
    for y0 in range(-8000, 8000, 2000):
        s += [C("hsd_gait_hmap -8000 %d 8000 %d 64 5000 brush" % (y0, y0 + 1936)), W(1.0)]
    return s + [W(1.0)]


def gait_c():
    """F6 latch checks (ref-titan-native's dead band 0.15): 160 u/s reached from above (250 -> slow) vs from
    below; 50 u/s (min rate 0.25: v/gs 0.20); long sprint from the x = -880 end of the y = -1392 lane"""
    s = _ride("ion")
    # from above: full speed 1.5 s, then slow to 160 while walking
    s += [lane(), W(1.5), C("hsd_tag ab_160"), C("+forward"), W(1.5), C(ms(160, 5.5)), W(3.5), C("hsd_tag stop_ab_160"), C("-forward"), W(3.0), C("hsd_tag -")]
    s += seg("be_160", 5.0, 160)                # from below (as thr_160)
    s += [lane(), W(1.5), C("hsd_tag ab_125"), C("+forward"), W(1.5), C(ms(125, 5.5)), W(3.5), C("hsd_tag stop_ab_125"), C("-forward"), W(3.0), C("hsd_tag -")]
    s += seg("f6_050", 6.0, 50)
    s += seg("f6_075", 6.0, 75)
    # F20 step: an 11 u platform (x -736..-544 at y -1728, map of run gait_b); walk +x over it, a 194 u block
    # stops the titan near x -424 (~2 s at 250 u/s)
    for tag, v, secs in (("step250", None, 2.4), ("step100", 100, 5.5), ("step250b", None, 2.4)):
        s += [lane(x=-928, y=-1728), W(1.5)]
        if v:
            s += [C(ms(v, secs + 2.0)), W(0.2)]
        s += [C("hsd_tag " + tag), C("+forward"), W(secs), C("hsd_tag stop_" + tag), C("-forward"), W(2.0), C("hsd_tag -")]
    s += [lane(x=-880, y=-1392), W(1.5), C("hsd_tag f6_sprint"), C("+forward"), C("+speed"), W(5.0), C("-speed"),
          C("hsd_tag stop_f6_sprint"), C("-forward"), W(3.0), C("hsd_tag -")]
    return s + [C("hsd_disembark"), W(2.0)]


def _ride_at(x, y, z, yaw=0):
    """spawn the titan on the floor at (x, y, z) facing yaw, the pilot 150 u behind it, instant embark"""
    import math
    px, py = x - 150 * math.cos(math.radians(yaw)), y - 150 * math.sin(math.radians(yaw))
    return [C("hsd_tag spawn_ion"), C("hsd_titan ion %d %d %d %d" % (x, y, z, yaw)), W(1.5),
            C("hsd_setup %d %d %d 0 0 0 0 %d" % (px, py, z + 80, yaw)), W(0.6),
            C("hsd_embark 0"), W(3.0), C("hsd_titan_info")]


def slope(tag, x, y, z, yaw, secs=4.0, speed=None):
    # drop in from 60 u above the slope: at +10 the titan hull's corners start inside a 15 deg slope and the
    # titan cannot move (run 20261109_112149_gait_f20)
    s = [C("hsd_setup %d %d %d 0 0 0 0 %d" % (x, y, z + 60, yaw)), W(2.5)]
    if speed:
        s += [C(ms(speed, secs + 2.0)), W(0.2)]
    return s + [C("hsd_tag " + tag), C("+forward"), W(secs), C("hsd_tag stop_" + tag), C("-forward"), W(2.5), C("hsd_tag -")]


def gait_f20b():
    """gait_f20 again with the titans dropped in from 60 u (see slope())"""
    return gait_f20()


def gait_f20():
    """F20 on mp_homestead (run with --map mp_homestead): slopes from the gait_scout brush map, up and down,
    run (250) and walk (100) clips; a prop-aware height map near the spawn for steps."""
    s = _ride_at(-4736, -912, 90, 180)   # the 9 deg line start (the pilot spawn sits on a building prop)
    # ~15 deg, 1344 u up along +x from (-4672, 3408) z 9; then down from the top
    s += slope("up15", -4672, 3408, 9, 0)
    s += slope("dn15", -3392, 3408, 358, 180)
    s += slope("up15w", -4672, 3408, 9, 0, 6.0, 100)
    # ~9 deg, up along -x from (-4736, -912) z 76; down from the top
    s += slope("up9", -4736, -912, 76, 180)
    s += slope("dn9", -5760, -912, 224, 0)
    # ~17 deg, 1280 u up along +x from (-6592, 1408) z 93
    s += slope("up17", -6592, 1408, 93, 0)
    for y0 in range(-3600, 4400, 800):
        s += [C("hsd_gait_hmap -6000 %d 800 %d 32 5000 above 250" % (y0, y0 + 784)), W(1.0)]
    return s + [W(1.0)]


def gait_f20c():
    """F20 on mp_homestead, third try (--map mp_homestead). The first spawn on homestead is a dropship drop and
    the titan embarked after it never moved (runs gait_f20 / gait_f20b); a pilot death + respawn first.
    Slope lines checked against both maps (brush 64 u and prop-aware 32 u agree, so no clip volume), x > -5400
    (the titan was killed out of bounds at x -5774 / -5895)."""
    s = [W(2.0), C("hsd_gait_die"), W(9.0), C("hsd_info")]
    s += _ride_at(-4352, -2336, -95, 0)
    # 9 deg, +x from (-4352, -2336) z -155 to (-3456, -2336) z -17
    s += slope("up9", -4352, -2336, -155, 0, 3.2)
    s += slope("dn9", -3456, -2336, -17, 180, 3.2)
    s += slope("up9w", -4352, -2336, -155, 0, 7.0, 100)
    # 17 deg, -y from (-5184, 2832) z 47 to (-5184, 2000) z 303
    s += slope("up17", -5184, 2832, 47, -90, 3.0)
    s += slope("dn17", -5184, 2000, 303, 90, 3.0)
    s += slope("up17w", -5184, 2832, 47, -90, 7.0, 100)
    # 13 deg, -y from (-2816, 3920) z 261 to (-2816, 3280) z 413
    s += slope("up13", -2816, 3920, 261, -90, 2.4)
    s += slope("dn13", -2816, 3280, 413, 90, 2.4)
    return s + [W(1.0)]


HOMESTEAD_PATHS = [  # (x, y, yaw, len): slope lines from the scans, a few lateral offsets each
    (-4352, -2336, 0, 960), (-4352, -2272, 0, 960), (-4352, -2208, 0, 960), (-4352, -2144, 0, 960), (-4288, -2400, 0, 960),
    (-5312, 2832, -90, 900), (-5248, 2832, -90, 900), (-5184, 2832, -90, 900), (-5120, 2832, -90, 900),
    (-2816, 3920, -90, 700), (-2752, 3920, -90, 700), (-2688, 3920, -90, 700), (-2560, 3920, -90, 700),
    (-1920, 2896, 90, 450), (-1984, 2896, 90, 450), (-2048, 2896, 90, 450),
    (-3456, -2336, 180, 960),
]


def gait_probe_h():
    """mp_homestead: titan-hull clearance along the candidate slope lines (hsd_gait_path); no titan needed"""
    s = [W(1.0)]
    for x, y, yaw, ln in HOMESTEAD_PATHS:
        s += [C("hsd_gait_path %d %d %d %d 32" % (x, y, yaw, ln)), W(0.4)]
    return s + [W(1.0)]


STACKS_STEP_PATHS = [  # the 11 u platform x -736..-544, y -1728..-1632 (map of run gait_b)
    (-640, -1950, 90, 450), (-688, -1950, 90, 450), (-592, -1950, 90, 450),
    (-880, -1728, 0, 500), (-860, -1680, 0, 500), (-860, -1696, 0, 500),
    (-400, -1680, 180, 450), (-440, -1700, 180, 450),
]


def gait_probe_s():
    """mp_lf_stacks: hull clearance on the approaches to the 11 u platform"""
    s = [W(1.0)]
    for x, y, yaw, ln in STACKS_STEP_PATHS:
        s += [C("hsd_gait_path %d %d %d %d 16" % (x, y, yaw, ln)), W(0.4)]
    return s + [W(1.0)]


def turn180():
    """keyboard turn 180 deg in place (cl_yawspeed 180 for 1 s), then let the legs catch up"""
    return [C("cl_yawspeed 180"), C("+left"), W(1.0), C("-left"), W(1.2), C("cl_yawspeed 210")]


def walk_here(tag, secs, speed=None):
    s = []
    if speed:
        s += [C(ms(speed, secs + 2.0)), W(0.2)]
    return s + [C("hsd_tag " + tag), C("+forward"), W(secs), C("hsd_tag stop_" + tag), C("-forward"), W(2.0), C("hsd_tag -")]


def chain9(sfx):
    """the 9 deg line without teleports: from its top (-3456, -2336) down, turn, up, at 250 and 100"""
    s = [C("hsd_setup -3456 -2336 43 0 0 0 0 180"), W(2.5)]
    s += walk_here("dn9" + sfx, 2.6) + turn180() + walk_here("up9" + sfx, 2.6) + turn180()
    s += walk_here("dn9w" + sfx, 6.0, 100) + turn180() + walk_here("up9w" + sfx, 6.0, 100)
    return s


def gait_f20d():
    """F20 on mp_homestead, fourth try (--map mp_homestead). Teleports to some free points still lock the titan
    (gait_f20c), so the 9 deg line is walked both ways from the one start that worked; the 17 / 13 deg tops
    are tried at three drop heights; then the 9 deg chain again in third person (rendered body, foot IK?)."""
    s = [W(2.0), C("hsd_gait_die"), W(9.0)]
    s += _ride_at(-3456, -2336, 0, 180)
    s += chain9("")
    for z in (323, 403, 463):   # 17 deg top (-5184, 2000), floor 303
        s += [C("hsd_setup -5184 2000 %d 0 0 0 0 90" % z), W(2.5)] + walk_here("dn17_%d" % z, 2.8) + turn180() + walk_here("up17_%d" % z, 2.8)
    for z in (433, 513):        # 13 deg top (-2816, 3280), floor 413
        s += [C("hsd_setup -2816 3280 %d 0 0 0 0 90" % z), W(2.5)] + walk_here("dn13_%d" % z, 2.4) + turn180() + walk_here("up13_%d" % z, 2.4)
    s += [C("hsd_cheats"), W(0.3), C("thirdperson"), W(1.0)] + chain9("_3p") + [C("firstperson"), W(0.5)]
    return s + [W(1.0)]


def gait_step():
    """F20 step on mp_lf_stacks: the 11 u platform (x -736..-544, y -1728..-1632) from the south, facing +y;
    a container wall north of it stops the titan near y -1600. Three drop heights (teleports can lock the
    titan). Then the flat lane in first vs third person (is the body re-posed / IK'd differently when drawn?)."""
    s = _ride("ion")
    for z in (8, 40, 80):
        for tag, v, secs in (("st100_%d" % z, 100, 4.0), ("st250_%d" % z, None, 2.0)):
            s += [C("hsd_setup -620 -1950 %d 0 0 0 0 90" % z), W(2.0)]
            if v:
                s += [C(ms(v, secs + 2.0)), W(0.2)]
            s += [C("hsd_tag " + tag), C("+forward"), W(secs), C("hsd_tag stop_" + tag), C("-forward"), W(1.5), C("hsd_tag -")]
    s += seg("fp_160", 4.5, 160) + seg("fp_250", 4.0)
    s += [C("hsd_cheats"), W(0.3), C("thirdperson"), W(1.0)]
    s += seg("tp_160", 4.5, 160) + seg("tp_250", 4.0) + seg("tp_075", 5.0, 75)
    for z in (8, 40, 80):
        s += [C("hsd_setup -620 -1950 %d 0 0 0 0 90" % z), W(2.0), C(ms(100, 6.0)), W(0.2), C("hsd_tag st100tp_%d" % z),
              C("+forward"), W(4.0), C("hsd_tag stop_st100tp_%d" % z), C("-forward"), W(1.5), C("hsd_tag -")]
    s += [C("firstperson"), W(0.5)]
    return s + [C("hsd_disembark"), W(2.0)]
