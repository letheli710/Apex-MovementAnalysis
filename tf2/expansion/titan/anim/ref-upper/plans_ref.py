"""ref-titan-upper plans (2026-11-09; mod HSD.RefUpper + the shared HSD.TF2Diag). Run with ref_runner.py.

mp_lf_stacks titan lane: (-800, -1400, 7) facing +x, about 1360 u clear toward +x (plans_kits.py).
A11: thirdperson (needs hsd_cheats), fire part of the clip, reload, log HAND_L every client frame (RC).
A12: shield 0, big health; scripted hits through the normal damage path (TitanDamageFlinch ->
     TitanStagger / AddFlinch) with source mp_titanweapon_sticky_40mm (on the stagger list) or
     mp_titanweapon_xo16 (not on it); standing, walking, sprinting, backward; with shield; cooldown.
F21: pilot stands at the far end of the lane; an idle enemy NPC titan walks (AssaultPoint) toward
     him from 1200 u and back; CreateShake at known distances as the positive control.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # expansion/titan (plans_titan)
from plans import C, W  # noqa: E402
from plans_titan import _ride  # noqa: E402

PLANS = ["ru_smoke", "ru_a11a12", "ru_f21"]


def lane(x=-800, y=-1400, z=7, yaw=0):
    return C("hsd_setup %d %d %d 0 0 0 0 %g" % (x, y, z, yaw))


def tag(n):
    return C("hsd_tag " + n)


def ru_smoke():
    """does HSD.RefUpper load: RS / RC lines, Anim_GetActivity, a hit, a shake"""
    s = [C("hsd_ru_log 1"), tag("sm_pilot"), W(1.0), C("hsd_ru_shake 16 150 1 1000 300"), W(1.5)]
    s += _ride("monarch") + [C("hsd_ru_prep 50000"), lane(), W(0.8), tag("sm_hit"), C("hsd_ru_hit 600 0 xo16"), W(1.5)]
    s += [C("hsd_ru_foe titan_atlas 0 1200 180"), W(1.5), tag("sm_walkhit"), C("+forward"), W(0.8), C("hsd_ru_hit 1200 0 40mm"), W(2.0), C("-forward"), W(1.0), tag("-")]
    return s


def _reload_block(cls, fire):
    s = [lane(), W(1.0), C("thirdperson"), W(0.8), tag("a11_%s_idle" % cls), W(1.5)]
    for k in range(2):
        s += [lane(), W(0.6), C("+attack"), W(fire), C("-attack"), W(0.8), tag("a11_%s_rl%d" % (cls, k)),
              C("+reload"), W(0.05), C("-reload"), W(6.5)]
    return s


def _walk_hit(name, amount, src, yaw=0, key="forward", pre=0.8, post=2.6, sprint=False, x=-800):
    s = [lane(x=x), W(0.8), C("hsd_ru_prep 50000"), W(0.2), tag("a12_" + name), C("+" + key)]
    if sprint:
        s += [C("+speed")]
    s += [W(pre), C("hsd_ru_hit %d %d %s" % (amount, yaw, src)), W(post), C("-" + key)]
    if sprint:
        s += [C("-speed")]
    return s + [W(1.2)]


def ru_a11a12():
    s = [C("hsd_cheats"), W(0.5), C("hsd_ru_log 1")]
    # A11: Monarch XO-16 (3P gesture 4.8 s, measured reload 2.46 s), Legion (4.7 / 4.11), Tone (3.3)
    s += _ride("monarch") + _reload_block("monarch", 1.0)
    # A12 on Monarch: the foe is only the attacker entity (idle, far to the side)
    s += [C("hsd_ru_foe titan_atlas 0 1200 180"), W(1.5)]
    s += [lane(), W(0.8), C("hsd_ru_prep 50000"), C("thirdperson"), W(0.4)]
    for yaw in (0, 90, 180, 270):
        s += [tag("a12_stand600_%d" % yaw), C("hsd_ru_hit 600 %d xo16" % yaw), W(2.0)]
    s += [tag("a12_stand1200_40mm"), C("hsd_ru_hit 1200 0 40mm"), W(3.0)]
    s += [lane(), W(0.8), tag("a12_walk_nohit"), C("+forward"), W(3.4), C("-forward"), W(1.2)]
    s += _walk_hit("walk1200_40mm_f", 1200, "40mm", 0)
    s += _walk_hit("walk1200_40mm_r", 1200, "40mm", 90)
    s += _walk_hit("walk1200_xo16", 1200, "xo16", 0)
    s += _walk_hit("walk600_40mm", 600, "40mm", 0)
    s += [lane(), W(0.8), C("hsd_ru_prep 50000"), C("hsd_shield 2500"), W(0.3), tag("a12_walk1200_shield"), C("+forward"), W(0.8),
          C("hsd_ru_hit 1200 0 40mm"), W(2.6), C("-forward"), W(1.2)]
    s += [lane(), W(0.8), C("hsd_ru_prep 50000"), W(0.2), tag("a12_walk_cooldown"), C("+forward"), W(0.8), C("hsd_ru_hit 1200 0 40mm"),
          W(0.5), C("hsd_ru_hit 1200 0 40mm"), W(0.7), C("hsd_ru_hit 1200 0 40mm"), W(2.0), C("-forward"), W(1.2)]
    s += _walk_hit("sprint1200_40mm", 1200, "40mm", 0, pre=1.0, post=2.0, sprint=True)
    s += _walk_hit("back1200_40mm", 1200, "40mm", 0, key="back", x=400)
    s += [C("hsd_disembark"), W(3.0)]
    # A11 on Legion and Tone
    s += _ride("legion") + _reload_block("legion", 1.5) + [C("hsd_disembark"), W(3.0)]
    s += _ride("tone") + _reload_block("tone", 0.6) + [tag("-")]
    return s


def ru_f21():
    s = [C("hsd_ru_log 1"), lane(x=450, yaw=180), W(1.5), tag("f21_idle"), W(2.0)]
    # positive control: CreateShake (hover takeoff uses 16 / 150 / 1 s / 400; hotdrop 16 / 150 / 2 s / 1500)
    for d in (300, 800, 1200):
        s += [tag("f21_shake%d" % d), C("hsd_ru_shake 16 150 1 1000 %d" % d), W(2.0)]
    s += [C("hsd_ru_foe titan_atlas -1200 0 0"), W(2.5), tag("f21_near_idle"), W(1.5)]
    s += [tag("f21_walk_in"), C("hsd_ru_walk -160 0 0"), W(10.0), tag("f21_stand"), W(2.0)]
    s += [tag("f21_walk_out"), C("hsd_ru_walk -1100 0 0"), W(9.0)]
    s += [tag("f21_run_in"), C("hsd_ru_walk -160 0 1"), W(7.0), tag("f21_stand2"), W(2.0)]
    s += [tag("f21_out2"), C("hsd_ru_walk -1100 0 0"), W(7.0), tag("-")]
    # A12 small tier again: does the additive flinch need hit flags or a real projectile?
    s += _ride("monarch") + [C("hsd_cheats"), W(0.3), C("thirdperson"), C("hsd_ru_foe titan_atlas 0 1200 180"), W(1.5), lane(), W(0.8), C("hsd_ru_prep 50000")]
    for amt, src, fl_ in ((600, "xo16", "bullet"), (600, "40mm", "exp"), (900, "xo16", "0"), (700, "40mm", "bullet")):
        s += [tag("a12b_%d_%s_%s" % (amt, src, fl_)), C("hsd_ru_hit %d 0 %s %s" % (amt, src, fl_)), W(2.0)]
    # a real Tone (npc titan_atlas_tracker) firing its 40mm at us from 700 u, shield 0
    s += [lane(), W(0.5), C("hsd_ru_prep 50000"), C("hsd_ru_foe titan_atlas_tracker 700 0 180 hostile"), W(0.5), tag("a12b_real_tone"), W(9.0)]
    s += [C("hsd_ru_foe titan_atlas 0 3000 180"), W(0.5), tag("-")]
    return s
