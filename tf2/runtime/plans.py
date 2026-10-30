"""Experiment plans for runner.py. Each returns a list of steps:
("cmd", "<console command>") or ("wait", seconds).
Server-side helpers (hsd_diag_sv.gnut): hsd_tag <name>, hsd_setup ox oy oz vx vy vz pitch yaw,
hsd_query <setfile keys...>."""


def C(c):
    return ("cmd", c)


def W(s):
    return ("wait", s)


def smoke():
    """Does the mod load, log every tick, read settings, and accept inputs?"""
    return [
        C("hsd_query speed sprintspeed acceleration deceleration airSpeed airAcceleration jumpHeight gravityScale "
          "wallrunAccelerateHorizontal wallrun_timeLimit"),
        C("hsd_tag idle"), W(1.5),
        C("hsd_tag forward"), C("+forward"), W(2.0), C("-forward"),
        C("hsd_tag stop"), W(1.5),
        C("hsd_tag jump"), C("+jump"), W(0.1), C("-jump"), W(1.5),
        # no input, 300 u/s along the view (yaw -90 at the lf_stacks spawn): decel only
        C("hsd_tag kick_decel"), C("hsd_kick 0 -300 0"), W(1.5),
        C("hsd_tag -"),
    ]


def U(cond, arg=0.0, timeout=5.0):
    """Wait (client frames) until cond: ground, air, wallrun, nowallrun, fall, hmin X, hmax X, zmin X."""
    return ("until", cond, arg, timeout)


def probe():
    """T5 tooling check (client-timed plan, input logging, report off) and wall search at spawn."""
    return [
        C("hsd_info"), C("hsd_probe 2500"), W(0.5),
        C("hsd_tag fwd"), C("+forward"), W(1.5), C("-forward"), U("hmax", 1.0, 3.0),
        C("hsd_tag jump"), C("+jump"), W(0.05), C("-jump"), U("air"), U("ground"), W(0.5),
        C("hsd_tag -"),
    ]


def probe2():
    """Wall search on mp_lf_stacks: floor and wall planes along the west (x=-960), east
    (x=1472) and south (y~-2048) walls the spawn probe found; plus tool check (fwd, jump)."""
    steps = [C("hsd_tag fwd"), C("+forward"), W(1.5), C("-forward"), U("hmax", 1.0, 3.0),
             C("hsd_tag jump"), C("+jump"), W(0.05), C("-jump"), U("air"), U("ground"), W(0.3), C("hsd_tag -")]
    for y in range(-1700, -99, 150):  # west wall
        steps += [C("hsd_trace -880 %d 900 -880 %d -600" % (y, y)), W(0.01)]
        for z in (10, 40, 80, 150, 250, 400, 600):
            steps += [C("hsd_trace -600 %d %d -1200 %d %d" % (y, z, y, z)), W(0.01)]
    for y in range(-1500, -999, 100):  # east wall
        steps += [C("hsd_trace 1400 %d 900 1400 %d -600" % (y, y)), W(0.01)]
        for z in (10, 40, 80, 150, 250, 400, 600):
            steps += [C("hsd_trace 1100 %d %d 1700 %d %d" % (y, z, y, z)), W(0.01)]
    for x in range(-900, 1301, 200):  # south
        steps += [C("hsd_trace %d -1950 900 %d -1950 -600" % (x, x)), W(0.01)]
        for z in (10, 40, 80, 150, 250, 400, 600):
            steps += [C("hsd_trace %d -1800 %d %d -2300 %d" % (x, z, x, z)), W(0.01)]
    return steps


from plans_t5 import bt_box, bt_ledge, bt_ledge2, bt_scan, t5_air, t5_air2, t5_slide2, t5_wall2, t5_djump, t5_ground, t5_slide, t5_wall  # noqa: E402,F401
from plans_t1 import t1_epg, t1_probe, t1_sky, t1_sprint, t1_sweep, t7_throw  # noqa: E402,F401

from plans_night import night_boost, night_grapple, night_grapple2, night_phase, night_phase2, night_grapple3, night_winscan, night_winscan_big, night_winscan_var, night_grapple_match  # noqa: E402,F401
from plans_w1 import w1_targets, w1_hostile, w1_passive  # noqa: E402,F401
from plans_w3 import w3_rewind, w3_rewind2, w3_smart, w3_smart2, w3_tick, w3_tick2, w3_turret  # noqa: E402,F401
from plans_w2 import w2_a, w2_b, w2_c, w2_d  # noqa: E402,F401

# titan T0 plans live with the titan research (../expansion/titan/)
import sys as _sys  # noqa: E402
from pathlib import Path as _Path  # noqa: E402
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "expansion" / "titan"))
from plans_titan import t0_smoke, t0_turn, t0_move, t0_probe, t0_lanes, t0_kit, t0_mouseslow  # noqa: E402,F401
