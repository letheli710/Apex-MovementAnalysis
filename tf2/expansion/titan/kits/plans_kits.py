"""Titan kit plans (2026-11-08, tf2-titan-kits; mod script hsd_diag_kit.gnut). See README.md.

mp_lf_stacks titan lane: start (-800, -1400, 7) facing +x (yaw 0), about 1360 u clear toward +x
(plans_titan._move_block). The enemy titan target (hsd_kit_foe) stands in that lane facing -x.
Keys (t0_kit): +offhand0 = offensive (Q), +offhand1 = defensive (hold), +offhand2 = tactical,
+ability 1 = core, +ability 3 = dash, +zoom = ADS, +attack = fire, +melee = punch / sword.
"""
from plans import C, W, U  # noqa: F401
from plans_titan import _ride

LANE = "hsd_setup -800 -1400 7 0 0 0 0 0"
SKY = "hsd_kit_sky -1500 -2400 1500 1500 150"  # most headroom on the map floor; teleports there


def lane(x=-800, y=-1400, z=7, yaw=0, pitch=0):
    return C("hsd_setup %d %d %d 0 0 0 %g %g" % (x, y, z, pitch, yaw))


def foe(setfile="titan_atlas", x=-200, y=-1400, z=7, yaw=180, hp=100000, mode="static"):
    return C("hsd_kit_foe %s %d %d %d %d %d %s" % (setfile, x, y, z, yaw, hp, mode))


def tap(key, hold=0.12):
    return [C("+" + key), W(hold), C("-" + key)]


def out(cls):
    return [C("hsd_tag out_" + cls), C("hsd_kit_foe_kill"), C("hsd_disembark"), W(3.0)]


def kit_smoke():
    """does hsd_diag_kit load: info, an enemy titan, KIT lines, one phase dash, foe damage"""
    s = [C("hsd_kit_info")] + _ride("ronin") + [C("hsd_kit_info")]
    s += [lane(), W(0.8), foe(), W(1.5), C("hsd_kit_foe_shield 0"), C("hsd_tag sm_phase"), C("+forward"), W(0.3)] + tap("offhand2")
    s += [W(1.8), C("-forward"), W(0.5), lane(), W(0.8), C("hsd_tag sm_fire"), C("+attack"), W(0.1), C("-attack"), W(1.5)]
    return s + out("ronin") + [C("hsd_tag -")]



def _prep(hp=50000):
    """big health, no shield: every hit shows in hp; all offhands full"""
    return [C("hsd_kit_hp %d" % hp), C("hsd_shield 0"), C("hsd_kit_refill"), C("hsd_dodgepower 100")]


def _ronin():
    s = _ride("ronin") + _prep() + [C("hsd_kit_info")]
    # phase dash on the ground: forward / right / back / no input (facing +y: does it go world +x?)
    for name, key, setup in (("f", "forward", lane()), ("r", "moveright", lane(yaw=90)), ("b", "back", lane(x=500)), ("n", None, lane(yaw=90))):
        s += [setup, W(0.8), C("hsd_kit_refill 2"), C("hsd_tag pd_" + name)]
        if key:
            s += [C("+" + key), W(0.3)]
        s += tap("offhand2") + [W(2.0)]
        if key:
            s += [C("-" + key)]
        s += [W(0.6)]
    # phase dash right after a normal dash, and in the air (falling from 250 u)
    s += [lane(), W(0.8), C("hsd_kit_refill 2"), C("hsd_dodgepower 100"), C("hsd_tag pd_afterdash"), C("+forward"), W(0.3)] + tap("ability 3", 0.08)
    s += [W(0.15)] + tap("offhand2") + [W(2.0), C("-forward"), W(0.5)]
    s += [lane(z=260), C("hsd_kit_refill 2"), U("air", 0, 0.5), C("hsd_tag pd_air"), C("+forward"), W(0.1)] + tap("offhand2") + [W(2.0), C("-forward"), W(0.5)]
    # sword block: the same 1000 bullet hit with the enemy titan standing at different angles (the block
    # is judged by the attacker's position against the PROPGUN attachment), without and with the block held
    s += [foe("titan_atlas", -400, -1400), W(1.2), lane(), W(0.8), C("hsd_kit_hp 50000")]
    s += [C("hsd_tag bk_none0"), C("hsd_kit_hurtfrom 1000 0 400"), W(0.4), C("hsd_tag bk_none180"), C("hsd_kit_hurtfrom 1000 180 400"), W(0.4)]
    s += [C("hsd_tag bk_hold"), C("+offhand1"), W(0.8)]
    for yaw in (0, 45, 90, 120, 140, 145, 150, 155, 160, 170, 180):
        s += [C("hsd_tag bk_%d" % yaw), C("hsd_kit_hurtfrom 1000 %d 400" % yaw), W(0.35)]
    s += [C("-offhand1"), W(0.5)]
    # leadwall pellets at 300 / 600 / 1000 u on an atlas target (shield 0)
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0")]
    for x, d in ((-500, 300), (-800, 600)):
        s += [lane(x=x), W(0.6), C("hsd_tag lw_%d" % d)] + tap("attack", 0.05) + [W(1.0)]
    s += [foe("titan_atlas", 200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.6), C("hsd_tag lw_1000")] + tap("attack", 0.05) + [W(1.0)]
    # arc wave: travel time to an idle target 600 u away, slow on it
    s += [foe("titan_atlas", -200, -1400, mode="idle"), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.6), C("hsd_tag aw_600")] + tap("offhand0") + [W(3.0)]
    # sword core: draw, block under core, sword hit, dash refills
    s += [foe("titan_atlas", -480, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.6), C("hsd_core"), W(0.3), C("hsd_tag sc_on")] + tap("ability 1") + [W(1.2)]
    s += [C("hsd_tag sc_block"), C("+offhand1"), W(0.6), C("hsd_kit_hurtfrom 1000 0 250"), W(0.4), C("-offhand1"), W(0.3)]
    s += [C("hsd_tag sc_sword")] + tap("melee", 0.1) + [W(1.2)]
    s += [C("hsd_tag sc_dash"), C("+moveright")] + tap("ability 3", 0.08) + [W(0.4)] + tap("ability 3", 0.08) + [W(2.5), C("-moveright")]
    s += [C("hsd_tag sc_wait"), W(8.0), C("hsd_kit_info")]
    return s + out("ronin")


def _northstar():
    s = _ride("northstar") + _prep() + [C("hsd_kit_info")]
    # the lf_stacks lane has a roof ~340 u above the titan (T0 hover flat at 340): hover where the sky is open
    s += [C("hsd_tag hv_ceiling_lane")] + tap("offhand2") + [W(4.5)]
    s += [C("hsd_tag sky"), C(SKY), W(3.0), C("hsd_tag hv_stand"), C("hsd_kit_refill 2"), W(0.5)] + tap("offhand2") + [W(5.5)]
    s += [C(SKY), W(3.0), C("hsd_kit_refill 2"), C("hsd_tag hv_fwd"), C("+forward"), W(0.3)] + tap("offhand2") + [W(4.5), C("-forward"), W(0.8)]
    s += [C(SKY), W(3.0), C("hsd_kit_refill 2"), C("hsd_dodgepower 100"), C("hsd_tag hv_dash")] + tap("offhand2") + [W(1.0), C("+moveright")] + tap("ability 3", 0.08) + [W(0.5), C("-moveright"), W(3.5)]
    # railgun: hold ADS for t, then fire, at a static atlas 600 u away (shield 0)
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.6)]
    for t in (0.05, 0.5, 1.0, 1.5, 2.3, 3.0):
        s += [C("hsd_tag rg_%g" % t), C("+zoom"), W(t)] + tap("attack", 0.05) + [W(0.3), C("-zoom"), W(1.6)]
    # cluster missile on the target: impact + sub-explosions over time
    s += [C("+reload"), W(0.05), C("-reload"), W(2.5), C("hsd_tag cm")] + tap("offhand0") + [W(6.0)]
    # tether trap thrown at an idle target 400 u away
    s += [foe("titan_atlas", -400, -1400, mode="idle"), W(1.2), lane(), W(0.6), C("hsd_tag tt")] + tap("offhand1") + [W(4.0)]
    # flight core: rise, move, rockets, landing
    s += [C("hsd_kit_foe_kill"), C(SKY), W(3.0), C("hsd_core"), W(0.3), C("hsd_tag fc")] + tap("ability 1") + [W(1.5), C("+forward"), W(2.0), C("-forward"), C("+attack"), W(1.5), C("-attack"), W(4.5)]
    return s + out("northstar")


def kit_a():
    """Ronin (phase dash, block angles, leadwall falloff, arc wave, sword core) and
    Northstar (hover, railgun charge levels, cluster missile, tether, flight core)"""
    return _ronin() + _northstar() + [C("hsd_tag -")]


def _ion():
    s = _ride("ion") + _prep() + [C("hsd_kit_info"), C("hsd_kit_energy 1000")]
    # energy: idle, ADS split shots, regen, laser shot, tripwire, vortex held with nothing hitting it
    s += [lane(), W(0.8), C("hsd_tag en_idle"), W(1.0), C("hsd_tag en_ads"), C("+zoom"), W(0.5), C("+attack"), W(1.5), C("-attack"), C("-zoom"), W(3.0)]
    s += [foe("titan_atlas_tracker", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.5), C("hsd_kit_energy 1000"), C("hsd_tag en_laser")] + tap("offhand0") + [W(3.0)]
    s += [C("hsd_kit_energy 1000"), C("hsd_tag en_trip"), lane(pitch=20), W(0.3)] + tap("offhand2") + [W(3.0)]
    s += [lane(), W(0.5), C("hsd_kit_energy 1000"), C("hsd_tag vx_hold"), C("+offhand1"), W(3.0), C("-offhand1"), W(3.0)]
    s += [C("hsd_kit_energy 1000"), C("hsd_tag vx_long"), C("+offhand1"), W(12.0), C("-offhand1"), W(4.0)]
    # vortex under rifle fire from two soldiers just off the aim line; release at the target behind them
    s += [C("hsd_npc soldier hostile -420 -1520 7 160 1000"), C("hsd_npc soldier hostile -420 -1280 7 200 1000"), W(2.0)]
    s += [lane(), W(0.3), C("hsd_kit_energy 1000"), C("hsd_tag vx_bullets"), C("+offhand1"), W(4.0), C("-offhand1"), W(2.0), C("hsd_npc_kill all"), W(0.5)]
    # vortex against projectiles: the Tone target shoots 40 mm at us, release back at it
    s += [lane(), W(0.3), C("hsd_kit_foe_mode hostile"), C("hsd_kit_energy 1000"), W(1.0), C("hsd_tag vx_proj"), C("+offhand1"), W(4.0), C("-offhand1"), W(0.5), C("hsd_kit_foe_mode static"), W(2.5)]
    # laser core on the static target
    s += [lane(), W(0.5), C("hsd_core"), W(0.3), C("hsd_tag lc")] + tap("ability 1") + [W(7.0)]
    return s + out("ion")


def _tone():
    s = _ride("tone") + _prep() + [C("hsd_kit_info")]
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.5)]
    # marks: four 40 mm hits, then the tracker rockets
    for i in range(4):
        s += [C("hsd_tag tm_%d" % i)] + tap("attack", 0.05) + [W(0.8)]
    s += [C("hsd_tag tr_fire")] + tap("offhand0") + [W(4.0)]
    # one mark and its lifetime
    s += [C("hsd_tag tm_life")] + tap("attack", 0.05) + [W(16.5)]
    # rockets with no mark
    s += [C("hsd_kit_refill 0"), C("hsd_tag tr_nomark")] + tap("offhand0") + [W(2.0)]
    # sonar on the target, salvo core
    s += [C("hsd_tag sonar"), lane(pitch=5), W(0.2)] + tap("offhand2") + [W(4.0)]
    s += [lane(), W(0.5), C("hsd_core"), W(0.3), C("hsd_tag salvo")] + tap("ability 1") + [W(4.5)]
    return s + out("tone")


def kit_b():
    """Ion (energy curve, vortex vs bullets / projectiles, laser shot, laser core) and Tone (marks, tracker rockets, salvo core)"""
    return _ion() + _tone() + [C("hsd_tag -")]


def _monarch_path(tag, p4, p5, p6):
    s = [C("hsd_kit_pas monarch 4 " + p4), C("hsd_kit_pas monarch 5 " + p5), C("hsd_kit_pas monarch 6 " + p6)]
    s += _ride("monarch") + _prep() + [C("hsd_kit_info")]
    for i in range(1, 5):
        s += [lane(), W(0.3), C("hsd_shield 0")]
        if i == 3:
            s += [C("hsd_kit_hp 10000"), C("hsd_hurt 3000 0"), W(0.3)]  # health below max before Superior Chassis
        s += [C("hsd_core"), W(0.3), C("hsd_tag %s_up%d" % (tag, i))] + tap("ability 1") + [W(2.0), C("hsd_kit_info")]
    return s


def _monarch():
    s = [C("hsd_kit_pas monarch 0 -")]  # prints the default upgrade choices
    s += _monarch_path("upA", "pas_vanguard_core1", "pas_vanguard_core5", "pas_vanguard_core8")
    # siphon on a titan target, then on a soldier; rearm after using both
    s += [C("hsd_tag reembark"), C("hsd_disembark"), W(4.0), C("hsd_embark 0"), W(3.5), C("hsd_kit_info")]
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 2500"), lane(), W(0.5), C("hsd_shield 0"), C("hsd_kit_refill"), C("hsd_tag sip_titan")] + tap("offhand1") + [W(3.0)]
    s += [C("hsd_kit_foe_kill"), C("hsd_npc soldier static -500 -1400 7 180 5000"), W(1.5), C("hsd_shield 0"), C("hsd_kit_refill"), C("hsd_tag sip_soldier")] + tap("offhand1") + [W(3.0), C("hsd_npc_kill all")]
    s += [C("hsd_tag salvo"), lane(pitch=3), W(0.3)] + tap("offhand0") + [W(1.0), C("hsd_dodgepower 0"), C("hsd_tag rearm")] + tap("offhand2") + [W(2.5), C("hsd_kit_info")]
    s += out("monarch")
    s += _monarch_path("upB", "pas_vanguard_core2", "pas_vanguard_core4", "pas_vanguard_core7")
    s += out("monarch")
    s += _monarch_path("upC", "pas_vanguard_core3", "pas_vanguard_core6", "pas_vanguard_core9")
    s += out("monarch") + [C("hsd_kit_pas monarch 4 pas_vanguard_core1"), C("hsd_kit_pas monarch 5 pas_vanguard_core4"), C("hsd_kit_pas monarch 6 pas_vanguard_core7")]
    return s


def _legion():
    s = _ride("legion") + _prep() + [C("hsd_kit_info")]
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.5)]
    s += [C("hsd_tag lg_hip"), C("+attack"), W(3.0), C("-attack"), W(2.0)]
    s += [C("hsd_tag lg_hip_again"), C("+attack"), W(0.6), C("-attack"), W(0.4), C("+attack"), W(1.0), C("-attack"), W(2.0)]
    s += [C("+reload"), W(0.05), C("-reload"), W(5.0)]
    s += [C("hsd_tag lg_ads"), C("+zoom"), W(2.0), C("+attack"), W(1.5), C("-attack"), C("-zoom"), W(2.0)]
    s += [C("hsd_tag lg_adsquick"), C("+zoom"), W(0.2), C("+attack"), W(2.0), C("-attack"), C("-zoom"), W(2.0)]
    # power shot: hold, release, on the static target; then knockback on an idle target near and far
    s += [C("hsd_kit_refill"), C("hsd_tag ps_close")] + tap("offhand0", 1.5) + [W(2.5)]
    for x, d in ((-500, 300), (100, 900), (500, 1300)):
        s += [foe("titan_atlas", x, -1400, mode="idle"), W(1.5), C("hsd_kit_foe_shield 0"), lane(), W(0.4), C("hsd_kit_refill"), C("hsd_tag ps_kb%d" % d)] + tap("offhand0", 1.5) + [W(2.5)]
    s += [lane(), W(0.4), C("hsd_kit_refill"), C("hsd_tag gunshield"), C("+offhand1"), W(3.0), C("-offhand1"), W(9.0)]
    s += [C("hsd_tag swap")] + tap("offhand2") + [W(2.5), C("hsd_kit_info")]
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag ps_long")] + tap("offhand0", 1.5) + [W(2.5)]
    s += [C("hsd_tag lg_long_ads"), C("+zoom"), W(1.8), C("+attack"), W(1.0), C("-attack"), C("-zoom"), W(1.0)]
    s += [C("+reload"), W(0.05), C("-reload"), W(5.0), C("hsd_core"), W(0.3), C("hsd_tag smart")] + tap("ability 1") + [W(0.8), C("+attack"), W(3.0), C("-attack"), W(1.0), C("hsd_kit_info")]
    return s + out("legion")


def kit_c():
    """Monarch (upgrade core, two paths; siphon; rearm) and Legion (spin-up, power shot, knockback, modes, smart core)"""
    return _monarch() + _legion() + [C("hsd_tag -")]


def _scorch():
    s = _ride("scorch") + _prep() + [C("hsd_kit_info")]
    s += [foe("titan_atlas", -300, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(pitch=4), W(0.5)]
    s += [C("hsd_tag th1")] + tap("attack", 0.05) + [W(7.0)]
    s += [C("hsd_tag th2")] + tap("attack", 0.05) + [W(2.7)] + tap("attack", 0.05) + [W(2.7)] + tap("attack", 0.05) + [W(7.0)]
    # incendiary trap at the target, then a thermite shot to light it
    s += [lane(pitch=8), W(0.3), C("hsd_tag trap_throw")] + tap("offhand2") + [W(2.5), lane(pitch=4), W(0.2), C("hsd_tag trap_light")] + tap("attack", 0.05) + [W(7.0)]
    s += [lane(), W(0.3), C("hsd_tag firewall")] + tap("offhand0") + [W(7.0)]
    s += [lane(x=-480), W(0.5), C("hsd_tag heatshield"), C("+offhand1"), W(4.5), C("-offhand1"), W(1.0)]
    s += [lane(), W(0.5), C("hsd_core"), W(0.3), C("hsd_tag flamecore")] + tap("ability 1") + [W(5.0)]
    return s + out("scorch")


def _tb(cls):
    """titan vs infantry: walk / sprint through static soldiers, punch, dash into one"""
    s = _ride(cls) + _prep() + [C("hsd_npc_kill all")]
    s += [C("hsd_npc soldier static -500 -1400 7 180 10000"), W(1.2), lane(), W(0.3), C("hsd_tag tb_walk_" + cls), C("+forward"), W(3.0), C("-forward"), W(1.0), C("hsd_npc_kill all")]
    s += [C("hsd_npc soldier static -400 -1400 7 180 10000"), W(1.2), lane(), W(0.3), C("hsd_tag tb_sprint_" + cls), C("+forward"), C("+speed"), W(3.0), C("-speed"), C("-forward"), W(1.0), C("hsd_npc_kill all")]
    # punch reach: soldier straight ahead at 150 / 250 / 280 / 300 u, and 250 u at 15 / 25 / 35 deg off the view
    for d, ang in ((150, 0), (250, 0), (280, 0), (300, 0), (250, 15), (250, 25), (250, 35)):
        import math
        x = -800 + d * math.cos(math.radians(ang))
        y = -1400 + d * math.sin(math.radians(ang))
        s += [C("hsd_npc soldier static %.0f %.0f 7 180 10000" % (x, y)), W(1.2), lane(), W(0.3), C("hsd_tag tb_punch%d_%d_%s" % (d, ang, cls))] + tap("melee", 0.1) + [W(1.3), C("hsd_npc_kill all")]
    s += [C("hsd_npc soldier static -450 -1400 7 180 10000"), W(1.2), lane(), W(0.3), C("hsd_dodgepower 100"), C("hsd_tag tb_dash_" + cls), C("+forward"), W(0.2)] + tap("ability 3", 0.08) + [W(1.5), C("-forward"), W(0.5), C("hsd_npc_kill all")]
    # default soldier health: does a step or a dash kill it
    s += [C("hsd_npc soldier static -450 -1400 7 180"), W(1.2), lane(), W(0.3), C("hsd_dodgepower 100"), C("hsd_tag tb_dash100_" + cls), C("+forward"), W(0.2)] + tap("ability 3", 0.08) + [W(1.5), C("-forward"), W(0.5), C("hsd_npc_kill all")]
    return s + out(cls)


def kit_d():
    """Scorch (thermite stacking, trap ignition, firewall, heat shield, flame core) and T-b titan vs infantry"""
    s = _scorch() + _tb("ion") + _tb("legion")
    # titanfall on a soldier (real call-in 500 u ahead)
    s += [C("hsd_npc soldier static %d -1350 1 -90 10000" % (24 + d)) for d in (0, 60, 90, 105, 120, 150)]
    s += [W(1.2), C("hsd_setup 24 -1850 1 0 0 0 -8 90"), W(0.6), C("hsd_tag tb_titanfall"), C("hsd_titanfall ion 500"), W(9.0), C("hsd_npc_kill all")]
    return s + [C("hsd_tag -")]


# --- T-f: reload_time_late, cockpit frame for light / heavy (dash, hit, pitch while moving) ---

def SHOT(n):
    return C("jpeg t1_%s 90" % n)


def _burst(name, n, gap=0.03):
    s = []
    for i in range(n):
        s += [SHOT("%s_%02d" % (name, i)), W(gap)]
    return s


def _reload_cut(cls, fire, cut_at, how, ads=False):
    """partial clip, reload, interrupt at cut_at s with <how>, then reload again: is the 2nd reload a late one?"""
    tag = "rl_%s_%s_%g" % (cls, how.replace(" ", ""), cut_at)
    s = [lane(), W(0.6)] + ([C("+zoom"), W(1.6)] if ads else [])
    s += [C("+attack"), W(fire), C("-attack")] + ([C("-zoom")] if ads else []) + [W(0.6), C("hsd_tag " + tag), C("+reload"), W(0.05), C("-reload"), W(cut_at)]
    s += tap(how, 0.1) + [W(1.2), C("hsd_tag %s_again" % tag), C("+reload"), W(0.05), C("-reload"), W(5.0)]
    return s


def _tf_frames(cls):
    from plans_titan import M
    s = [lane(), W(1.5), C("hsd_tag tf_idle_" + cls)] + _burst("tf_%s_idle" % cls, 2)
    for name, key, setup in (("f", "forward", lane()), ("r", "moveright", lane(yaw=90))):
        s += [setup, W(0.8), C("hsd_dodgepower 100"), W(0.2), C("hsd_tag tf_dash%s_%s" % (name, cls)), C("+" + key), W(0.3)] + tap("ability 3", 0.03)
        s += _burst("tf_%s_dash%s" % (cls, name), 12, 0.02) + [C("-" + key), W(1.0)]
    s += [lane(), W(1.0), C("hsd_shield 0"), C("hsd_tag tf_hit_" + cls), C("hsd_hurt 300 0")] + _burst("tf_%s_hit" % cls, 10, 0.03) + [W(1.0)]
    s += [lane(), W(1.0), C("hsd_tag tf_pu_" + cls), M("tf_pu_" + cls, 0, -3, 300, 5), W(0.4)] + _burst("tf_%s_pu" % cls, 8, 0.08) + [W(1.0)]
    s += [lane(pitch=-20), W(1.0), C("hsd_tag tf_pd_" + cls), M("tf_pd_" + cls, 0, 3, 300, 5), W(0.4)] + _burst("tf_%s_pd" % cls, 8, 0.08) + [W(1.0)]
    return s


def kit_e():
    """T-f (run with --mouse): reload interrupted by melee / ordnance at a late point, then a fresh reload;
    cockpit frame bursts for dash, hit and pitch-while-moving on light (Ronin), medium (Ion), heavy (Legion)"""
    s = _ride("monarch") + _prep()
    s += _reload_cut("monarch", 0.9, 1.0, "melee") + _reload_cut("monarch", 0.9, 1.9, "melee") + _reload_cut("monarch", 0.9, 1.0, "offhand0")
    s += out("monarch")
    s += _ride("ronin") + _prep() + _reload_cut("ronin", 0.9, 1.0, "melee")
    s += [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.6), C("hsd_kit_refill 0"), C("hsd_tag aw_static600")] + tap("offhand0") + [W(3.0)]
    s += _tf_frames("ronin") + out("ronin")
    s += _ride("legion") + _prep() + _reload_cut("legion", 1.0, 1.5, "melee", ads=True) + _tf_frames("legion") + out("legion")
    s += _ride("ion") + _prep() + _tf_frames("ion") + out("ion")
    return s + [C("hsd_tag -")]


def kit_ns():
    """Northstar hover / flight core on an open map (run with --map mp_homestead): mp_lf_stacks has a ceiling
    ~340 u above the titan everywhere (hsd_kit_sky found 332 u at most, run 20261108_131828_kit_a)"""
    big = "hsd_kit_sky -4000 -4000 4000 4000 200 auto 1100"  # nearest spot to the player with 1100 u headroom
    s = [W(1.0), C("hsd_tag ns_sky"), C(big), W(5.0), C("hsd_kit_titanhere northstar 250"), W(2.0), C("hsd_embark 0"), W(3.5)]
    s += _prep() + [C("hsd_kit_info")]
    s += [C(big), W(5.0), C("hsd_tag hv_stand")] + tap("offhand2") + [W(6.0)]
    s += [C(big), W(5.0), C("hsd_kit_refill 2"), C("hsd_tag hv_fwd"), C("+forward"), W(0.3)] + tap("offhand2") + [W(5.0), C("-forward"), W(0.8)]
    s += [C(big), W(5.0), C("hsd_kit_refill 2"), C("hsd_tag hv_sprint"), C("+forward"), C("+speed"), W(1.0)] + tap("offhand2") + [W(5.0), C("-speed"), C("-forward"), W(0.8)]
    s += [C(big), W(5.0), C("hsd_core"), W(0.3), C("hsd_tag fc")] + tap("ability 1") + [W(2.0), C("+forward"), W(2.0), C("-forward"), W(5.0)]
    return s + [C("hsd_tag -")]


def kit_b2():
    """Tone (the kit_b Tone part died on a log bug) and the Ion laser core on a static target"""
    s = _tone()
    s += _ride("ion") + _prep() + [foe("titan_atlas", -200, -1400), W(1.2), C("hsd_kit_foe_shield 0"), lane(), W(0.5)]
    s += [C("hsd_core"), W(0.3), C("hsd_tag lc2")] + tap("ability 1") + [W(7.0)] + out("ion")
    return s + [C("hsd_tag -")]


def kit_ns2():
    """Northstar hover / flight core at the pilot spawn of an open map, no teleport (kit_ns got stuck after
    hsd_kit_sky teleports, run 20261108_143412_kit_ns). Run with --map mp_homestead."""
    s = [W(1.0), C("hsd_tag ns_spawn"), C("hsd_kit_titanhere northstar 300"), W(2.0), C("hsd_embark 0"), W(3.5)] + _prep() + [C("hsd_kit_info")]
    s += [C("hsd_tag hv_stand")] + tap("offhand2") + [W(6.0), C("hsd_kit_refill 2")]
    s += [C("hsd_tag hv_stand2")] + tap("offhand2") + [W(6.0), C("hsd_kit_refill 2")]
    s += [C("hsd_core"), W(0.3), C("hsd_tag fc")] + tap("ability 1") + [W(9.0)]
    return s + [C("hsd_tag -")]


# only the kit_* plans are exported into runtime/plans.py
__all__ = [n for n in list(globals()) if n.startswith("kit_")]
