"""tf2-kits-measure plans (2026-11-13). Run with kitm_runner.py. See README.md in this folder.

Probe commands: measure/mod/HSD.KitMeasure (hsd_km_*); kit commands from the shared HSD.TF2Diag (hsd_kit_*).
mp_lf_stacks titan lane (plans_kits): start (-800, -1400, 7) facing +x, about 1360 u clear toward +x.
"""
import math
from plans import C, W, U  # noqa: F401
from plans_titan import _ride
from plans_kits import lane, tap, _prep, out


def kfoe(f, r=0, mode="static", yaw=180, setfile="titan_atlas"):
    return C("hsd_km_foe %s %d %d %d %s" % (setfile, f, r, yaw, mode))


CLEAR = C("hsd_km_foe_clear")


def _cores(n, tag):
    s = []
    for i in range(1, n + 1):
        s += [C("hsd_shield 0"), C("hsd_core"), W(0.3), C("hsd_tag %s_up%d" % (tag, i))] + tap("ability 1") + [W(1.8)]
    return s + [C("hsd_kit_info")]


def _salvo_shots():
    s = []
    for i, pitch in enumerate((0, 0, 0, -8)):
        s += [lane(pitch=pitch), W(0.5), C("hsd_kit_refill 0"), W(0.2), C("hsd_tag sv_%d" % i)] + tap("offhand0") + [W(2.5)]
    s += [lane(), W(0.4), kfoe(700), W(1.5), lane(), W(0.3), C("hsd_kit_refill 0"), C("hsd_tag sv_dmg")] + tap("offhand0") + [W(2.5), CLEAR]
    return s


def _multi(tag):
    s = [lane(), W(0.4), C("hsd_kit_refill 0"), W(0.3), C("hsd_tag %s_none" % tag)] + tap("offhand0", 0.6) + [W(3.0)]
    s += [lane(), W(0.4), kfoe(900), W(1.5), lane(), W(0.3)]
    for hold in (0.8, 3.0):
        s += [C("hsd_kit_refill 0"), W(0.3), C("hsd_tag %s_one%g" % (tag, hold))] + tap("offhand0", hold) + [W(3.0), C("hsd_km_foe_clear"), lane(), W(0.3), kfoe(900), W(1.5), lane(), W(0.3)]
    s += [kfoe(900, 300), W(1.5), lane(), W(0.3), C("hsd_kit_refill 0"), W(0.3), C("hsd_tag %s_two" % tag)] + tap("offhand0", 4.0) + [W(3.0), CLEAR]
    return s


def km_monarch():
    """Monarch: salvo rocket paths (client per frame) and damage; multi-target missiles (core 3 = core7) without
    and with Missile Racks: lock fractions per frame (SA), count and path with no lock, one and two targets."""
    s = [C("hsd_km_log 1")] + _ride("monarch") + _prep() + [C("hsd_kit_info")] + _salvo_shots() + out("monarch")
    s += [C("hsd_kit_pas monarch 4 pas_vanguard_core1"), C("hsd_kit_pas monarch 5 pas_vanguard_core5"), C("hsd_kit_pas monarch 6 pas_vanguard_core7")]
    s += _ride("monarch") + _prep() + [lane(), W(0.3)] + _cores(3, "mtA") + _multi("mt") + out("monarch")
    s += [C("hsd_kit_pas monarch 4 pas_vanguard_core2"), C("hsd_kit_pas monarch 5 pas_vanguard_core4")]
    s += _ride("monarch") + _prep() + [lane(), W(0.3)] + _cores(3, "mtB") + _multi("mr") + out("monarch")
    s += [C("hsd_kit_pas monarch 4 pas_vanguard_core1"), C("hsd_kit_pas monarch 5 pas_vanguard_core4"), C("hsd_kit_pas monarch 6 pas_vanguard_core7")]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")]


def _vx(tag, kind, n, gap, pitch_release=0, hold_after=1.2):
    """vortex up, the foe (index 0, straight ahead) fires n <kind> at the eye, release at pitch_release"""
    s = [lane(), W(0.3), C("hsd_kit_energy 1000"), C("hsd_tag %s" % tag), C("+offhand1"), W(0.3), C("hsd_km_fire 0 %s %d %g" % (kind, n, gap)),
         W(n * gap + hold_after)]
    if pitch_release:
        s += [lane(pitch=pitch_release), W(0.05)]
    return s + [C("-offhand1"), W(2.5)]


def km_ion():
    """Ion vortex vs projectiles: the foe 900 u ahead fires each kind by script (it does not need its AI);
    release back at it (damage), and released 10 deg high past it (refire directions / spread at the far wall)."""
    s = [C("hsd_km_log 1")] + _ride("ion") + _prep(100000) + [C("hsd_kit_energy 1000"), lane(), W(0.3), kfoe(900, 0, "static"), W(1.6)]  # idle foes wander off the lane (021103)
    # (no control shots: the foe's scripted 40 mm hitting the player crashed server.dll, run 20261113_020328_km_ion)
    for kind in ("40mm", "meteor", "sniper", "leadwall", "salvo", "tracker"):
        s += _vx("vx_%s" % kind, kind, 3, 0.3)
    for kind in ("40mm", "sniper", "salvo"):
        s += _vx("vs_%s" % kind, kind, 8, 0.15, -10)
    return s + [CLEAR, C("hsd_km_log 0"), C("hsd_tag -")] + out("ion")


HOMESTEAD_START = (-3456, -2336, 0)  # the one titan start that moved in ref-gait (gait_f20d); ref-tail-a ta_hover


def km_hover():
    """Northstar hover / flight core height curves on mp_homestead (--map mp_homestead): die once (the dropship
    spawn locks the first embarked titan), titan at the open start, hover standing x2, flight core, hover forward."""
    from plans_tail import _ride_at
    x0, y0, _ = HOMESTEAD_START
    s = [W(2.0), C("hsd_km_log 1"), C("hsd_km_die"), W(9.0)]
    for dx in (-400, 0, 400):
        for dy in (-400, 0, 400):
            s += [C("hsd_km_head %d %d 300" % (x0 + dx, y0 + dy)), W(0.05)]
    s += _ride_at("northstar", x0, y0, 0, 180) + _prep() + [C("hsd_kit_info"), C("hsd_km_head")]
    s += [C("hsd_tag hv_stand")] + tap("offhand2") + [W(6.5), C("hsd_km_head")]
    s += [C("hsd_kit_refill 2"), W(0.3), C("hsd_tag hv_stand2")] + tap("offhand2") + [W(6.5)]
    s += [C("hsd_core"), W(0.3), C("hsd_tag fc_stand")] + tap("ability 1") + [W(9.5)]
    s += [C("hsd_kit_refill 2"), W(0.3), C("hsd_tag hv_fwd"), C("+forward"), W(0.3)] + tap("offhand2") + [W(4.5), C("-forward"), W(1.5)]
    s += [C("hsd_kit_refill 2"), W(0.3), C("hsd_tag hv_late"), C("+jump"), W(0.1), C("-jump"), W(0.3)] + tap("offhand2") + [W(6.0)]
    # long-range salvo drift (open map): Monarch at the same start, salvo level and 3 deg up
    s += [C("hsd_tag out_ns"), C("hsd_disembark"), W(3.0)] + _ride_at("monarch", x0, y0, 0, 180) + _prep()
    for i in range(2):  # no teleport: teleporting an embarked titan can lock it (ref-gait)
        s += [W(0.5), C("hsd_kit_refill 0"), C("hsd_tag svl_%d" % i)] + tap("offhand0") + [W(4.0)]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")]


def km_tether():
    """Northstar tether trap on an idle enemy titan 250 u ahead, which then walks / runs away (NPC pull rule)"""
    s = [C("hsd_km_log 1")] + _ride("northstar") + _prep()
    for tag, dx, dy in (("tt_x", 1100, 0), ("tt_y", 0, 500)):
        s += [lane(), W(0.3), kfoe(250, 0, "idle"), W(1.6), lane(pitch=25), W(0.3), C("hsd_kit_refill 1"), C("hsd_tag %s_throw" % tag)] + tap("offhand1") + [W(3.0)]
        s += [C("hsd_tag " + tag), C("hsd_km_walk 0 %d %d" % (dx, dy)), W(12.0), C("hsd_km_walk 0 0 0"), W(4.0), CLEAR]
    s += [lane(), W(0.3), kfoe(250, 0, "idle"), W(1.6), C("hsd_tag tt_ctrl"), C("hsd_km_walk 0 1100 0"), W(6.0), CLEAR]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")] + out("northstar")


def km_scorch():
    """Scorch thermite: fire spots (prop_physics, server 10 Hz) on flat ground at 300 / 700 u, a wall hit,
    an air burst; two shots on one static titan (same fire twice: one tick or two?)"""
    s = [C("hsd_km_log 1")] + _ride("scorch") + _prep()
    for tag, pitch in (("th_p12", 12), ("th_p6", 6), ("th_p3", 3), ("th_wall", 0), ("th_up", -25)):
        s += [lane(pitch=pitch), W(0.4), C("hsd_tag " + tag)] + tap("attack", 0.05) + [W(4.0), C("+reload"), W(0.05), C("-reload"), W(1.5)]
    s += [lane(), W(0.3), kfoe(450, 0, "static"), W(1.6), lane(pitch=4), W(0.3), C("hsd_tag th_one")] + tap("attack", 0.05) + [W(4.0), C("+reload"), W(0.05), C("-reload"), W(1.5)]
    s += [CLEAR, lane(), W(0.3), kfoe(400, 0, "idle"), W(1.6), lane(), W(0.3), C("hsd_shield 0")]
    # the foe's thermite at the player's feet: one shot, then two shots 0.3 s apart (same fire twice on one target)
    s += [C("hsd_tag th_foe1"), C("hsd_km_fire 0 meteor 1 0 -200"), W(4.0), lane(), W(0.3)]
    s += [C("hsd_tag th_foe2"), C("hsd_km_fire 0 meteor 2 0.3 -200"), W(4.5), CLEAR]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")] + out("scorch")


def km_proj():
    """Player-fired projectiles, client per frame: Tone 40 mm (level / 5 deg up), tracker rockets on a foe walking
    sideways (homing curve), salvo core; Northstar railgun uncharged, cluster missile, flight core rockets at a foe;
    Ronin leadwall at the far wall (pellet gravity)."""
    s = [C("hsd_km_log 1")] + _ride("tone") + _prep()
    for tag, pitch in (("mm_0", 0), ("mm_up5", -5)):
        s += [lane(pitch=pitch), W(0.5), C("hsd_tag " + tag)] + tap("attack", 0.05) + [W(1.5)]
    s += [lane(), W(0.3), kfoe(900, 0, "idle"), W(1.6), lane(), W(0.3)]
    for i in range(3):
        s += [C("hsd_tag mk_%d" % i)] + tap("attack", 0.05) + [W(0.7)]
    s += [C("hsd_km_walk 0 0 700"), W(0.8), C("hsd_tag tr_walk")] + tap("offhand0") + [W(3.5)]
    s += [CLEAR, lane(), W(0.3), kfoe(1100, 0, "idle"), W(1.6), lane(), W(0.3), C("hsd_core"), W(0.3), C("hsd_tag salvo_core")] + tap("ability 1") + [W(5.0), CLEAR]
    s += out("tone")
    s += _ride("northstar") + _prep()
    for tag, pitch in (("rg_0", 0), ("rg_up3", -3)):
        s += [lane(pitch=pitch), W(0.5), C("hsd_tag " + tag)] + tap("attack", 0.05) + [W(1.6)]
    s += [lane(pitch=-2), W(0.4), C("hsd_tag cluster")] + tap("offhand0") + [W(6.0)]
    s += [lane(), W(0.3), kfoe(1000, 300, "idle"), W(1.6), lane(), W(0.3), C("hsd_core"), W(0.3), C("hsd_tag fc_rockets")] + tap("ability 1") + [W(1.5), C("+attack"), W(1.5), C("-attack"), W(5.0), CLEAR]
    s += out("northstar")
    s += _ride("ronin") + _prep()
    for i in range(2):
        s += [lane(), W(0.5), C("hsd_tag lw_%d" % i)] + tap("attack", 0.05) + [W(1.0)]
    s += [lane(pitch=-6), W(0.5), C("hsd_tag lw_up6")] + tap("attack", 0.05) + [W(1.0)]
    s += [lane(), W(0.5), C("hsd_tag arcwave")] + tap("offhand0") + [W(2.5)]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")] + out("ronin")




def _soldier_at(f, r=0, mode="static", hp=10000, yaw=180):
    """enemy soldier f ahead / r right of the lane start (-800, -1400) facing back (lane faces +x)"""
    return C("hsd_npc soldier %s %d %d 7 %d %d" % (mode, -800 + f, -1400 - r, yaw, hp))


def km_shared():
    """Shared titan actions: punch on infantry (distance / view pitch / frozen vs idle, titan control),
    electric smoke on a titan and soldiers at several distances, nuclear ejection on titans at 300-760 u."""
    s = [C("hsd_km_log 1")] + _ride("ion") + _prep(100000)
    for tag, f, pitch, mode in (("pu_250_p0", 250, 0, "static"), ("pu_250_p15", 250, 15, "static"), ("pu_250_p28", 250, 28, "static"),
                                ("pu_200_p35", 200, 35, "static"), ("pu_250_p28_idle", 250, 28, "idle"), ("pu_280_p28", 280, 28, "static"),
                                ("pu_320_p28", 320, 28, "static"), ("pu_150_p45", 150, 45, "static")):
        s += [lane(), W(0.2), _soldier_at(f, 0, mode), W(1.2), lane(pitch=pitch), W(0.4), C("hsd_tag " + tag)] + tap("melee", 0.1) + [W(1.4), C("hsd_npc_kill all"), W(0.2)]
    s += [lane(), W(0.3), kfoe(250, 0, "static"), W(1.6), lane(), W(0.3), C("hsd_tag pu_titan")] + tap("melee", 0.1) + [W(1.4), CLEAR]
    # electric smoke: titan 150 ahead, soldiers at 300 / 340 / 360 / 390 from the titan's spot, one soldier 300 up?
    s += [lane(), W(0.3), kfoe(150, 0, "static"), W(1.6)]
    for f, r in ((140, 300), (140, -340), (440, 0), (140 + 360, 0), (140, 390)):
        s += [_soldier_at(f, r, "static", 100000)]
    s += [W(1.2), lane(), W(0.3), C("hsd_km_smoke_give"), W(0.3), C("hsd_kit_info"), C("hsd_tag smoke")] + tap("ability 6", 0.15) + [W(7.0), C("hsd_kit_info"), C("hsd_npc_kill all"), CLEAR]
    s += out("ion")
    # nuclear ejection (titan kit passive1); doomed first, then eject; titans at 300 / 450 / 600 / 760 u
    s += [C("hsd_kit_pas ion 1 pas_build_up_nuclear_core")] + _ride("ion") + [C("hsd_kit_info"), lane(), W(0.3)]
    for i, f in enumerate((300, 450, 600, 760)):
        s += [kfoe(f, (i - 1.5) * 200, "static")]
    s += [W(1.6), lane(), W(0.3), C("hsd_shield 0"), C("hsd_kit_hp 3000"), C("hsd_tag nuke_doom"), C("hsd_hurt 3500 0"), W(1.5), C("hsd_tag nuke_eject"), C("hsd_eject"), W(9.0), CLEAR]
    s += [C("hsd_kit_pas ion 1 -")]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")]



def km_nuke():
    """Nuclear ejection: passive given to the player directly, doomed, eject; titans at 300 / 450 / 600 / 760 u,
    one of them with full shield; pilot path from PC"""
    s = [C("hsd_km_log 1")] + _ride("ion") + [lane(), W(0.3)]
    for i, f in enumerate((300, 450, 600, 760)):
        s += [kfoe(f, (i - 1.5) * 200, "static")]
    s += [W(1.6), C("hsd_kit_foe_shield 0"), lane(), W(0.3), C("hsd_km_nukepas"), C("hsd_shield 0"), C("hsd_kit_hp 3000"), C("hsd_tag nuke_doom"), C("hsd_hurt 3500 0"), W(1.0)]
    s += [C("hsd_tag nuke_eject"), C("hsd_eject"), W(10.0), CLEAR]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")]


def _marks(n=3):
    s = []
    for i in range(n):
        s += [C("hsd_tag mk")] + tap("attack", 0.05) + [W(0.75)]
    return s


def km_homing():
    """Homing per client frame: Tone tracker rockets on a static foe at 900 / 1500 u and on a foe sliding sideways
    at 300 u/s; salvo core on a static foe; Northstar cluster missile (straight + drift) and flight core rockets at a
    static foe; cluster missiles aimed past a static foe at 700 u with lateral offsets (graze: missile hit size)."""
    s = [C("hsd_km_log 1")] + _ride("tone") + _prep()
    for tag, f, r, slide in (("tr_fix900", 900, 0, None), ("tr_fix1500", 1500, 0, None), ("tr_slide", 900, 300, "0 300 6"), ("tr_slide_fast", 900, 400, "0 600 3")):
        s += [CLEAR, lane(), W(0.3), kfoe(f, r, "static"), W(1.6), C("hsd_kit_refill 0"), C("hsd_km_aimfoe 0"), W(0.3)] + _marks()
        if slide:
            s += [C("hsd_km_slide 0 " + slide), W(0.3)]
        s += [C("hsd_tag " + tag)] + tap("offhand0") + [W(3.5)]
    s += [CLEAR, lane(), W(0.3), kfoe(1100, 0, "static"), W(1.6), lane(), W(0.3), C("hsd_core"), W(0.3), C("hsd_tag salvo_core")] + tap("ability 1") + [W(4.5), CLEAR]
    s += out("tone")
    s += _ride("northstar") + _prep()
    s += [lane(pitch=-1), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag cl_wall")] + tap("offhand0") + [W(2.0)]
    s += [CLEAR, lane(), W(0.3), kfoe(1000, 0, "static"), W(1.6), lane(), W(0.3), C("hsd_core"), W(0.3), C("hsd_tag fc_fix")] + tap("ability 1") + [W(1.5), C("+attack"), W(1.5), C("-attack"), W(5.0), CLEAR]
    s += [lane(), W(0.3), kfoe(700, 0, "static"), W(1.6)]
    for d in (0, 60, 80, 90, 100, 110, 120, 130, 140, 160):
        yaw = -math.degrees(math.atan2(d, 700))  # aim to the left of the foe (lane faces +x; positive yaw = left)
        s += [lane(yaw=-yaw), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag gz_%d" % d)] + tap("offhand0") + [W(1.4)]
    return s + [CLEAR, C("hsd_km_log 0"), C("hsd_tag -")] + out("northstar")


def km_tether2():
    """Player tethered: the foe (static, 450 u ahead) throws a tether trap at the player's feet; after it arms the
    player walks back (away) for 6 s, then forward; per-frame player path (PC) and tethered status (TS)."""
    s = [C("hsd_km_log 1")] + _ride("ion") + _prep(100000) + [lane(), W(0.3), kfoe(450, 0, "static"), W(1.6), lane(), W(0.3)]
    for i in range(2):
        s += [C("hsd_tag tp_throw%d" % i), C("hsd_km_fire 0 tether 1 0 -170"), W(2.8), C("hsd_tag tp_back%d" % i), C("+back"), W(6.0), C("-back"), W(1.0),
              C("hsd_tag tp_side%d" % i), C("+moveleft"), W(4.0), C("-moveleft"), W(2.0), lane(), W(0.5)]
    s += [C("hsd_tag tp_ctrl"), C("+back"), W(4.0), C("-back"), W(0.5), CLEAR]
    return s + [C("hsd_km_log 0"), C("hsd_tag -")] + out("ion")



def km_homing2():
    """Follow-up of km_homing: the lf_stacks lane is only ~180 u wide each side and ~1360 u long, so targets stay
    inside it. Tracker rockets at 600 / 1200 u and on a foe sliding across the lane (150 u right -> left at 250 u/s);
    flight core rockets at a static foe 1000 u; cluster missiles passing a static foe at 700 u with 10 - 60 u offsets."""
    s = [C("hsd_km_log 1")] + _ride("tone") + _prep()
    for tag, f, r, slide in (("tr_fix600", 600, 0, None), ("tr_fix1200", 1200, 0, None), ("tr_slide", 900, 150, "0 250 1.4")):
        s += [CLEAR, lane(), W(0.3), kfoe(f, r, "static"), W(1.6), C("hsd_kit_refill 0"), C("hsd_km_aimfoe 0"), W(0.3)] + _marks()
        if slide:
            s += [C("hsd_km_slide 0 " + slide), W(0.1)]
        s += [C("hsd_tag " + tag)] + tap("offhand0") + [W(3.0)]
    s += [CLEAR] + out("tone")
    s += _ride("northstar") + _prep()
    s += [lane(), W(0.3), kfoe(1000, 0, "static"), W(1.6), lane(), W(0.3), C("hsd_core"), W(0.5), C("hsd_tag fc_fix")] + tap("ability 1") + [W(1.3), C("+attack"), W(1.5), C("-attack"), W(5.0), CLEAR]
    s += [lane(), W(0.3), kfoe(700, 0, "static"), W(1.6)]
    for d in (10, 20, 30, 40, 50, 60):
        yaw = math.degrees(math.atan2(d, 700))
        s += [lane(yaw=yaw), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag gz_%d" % d)] + tap("offhand0") + [W(1.4)]
    return s + [CLEAR, C("hsd_km_log 0"), C("hsd_tag -")] + out("northstar")



def km_graze():
    """Missile hit size, refined: cluster missiles past a static titan at 700 u. In km_homing2 an aim offset d gave a
    lateral pass of about d - 43 u at chest height; here d = 75..110 (pass ~32..67 u), then vertical: aim over the
    head (pitch up) so the missile passes 0..80 u above the 235 u top."""
    s = [C("hsd_km_log 1")] + _ride("northstar") + _prep() + [lane(), W(0.3), kfoe(700, 0, "static"), W(1.6)]
    for d in (75, 80, 85, 90, 95, 100, 105, 110):
        yaw = math.degrees(math.atan2(d, 700))
        s += [lane(yaw=yaw), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag gz_%d" % d)] + tap("offhand0") + [W(1.6)]
    for up in (40, 60, 70, 80, 90, 100, 120):
        pitch = -math.degrees(math.atan2(up, 700))
        s += [lane(pitch=pitch), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag gv_%d" % up)] + tap("offhand0") + [W(1.6)]
    return s + [CLEAR, C("hsd_km_log 0"), C("hsd_tag -")] + out("northstar")



def km_tether3():
    """Player tethered, pulling away down the open lane: player at x = -300 facing +x, the foe 450 u behind throws the
    trap at the player's feet; after it arms the player holds forward 6 s. Control: the same walk with no trap."""
    s = [C("hsd_km_log 1")] + _ride("ion") + _prep(100000)
    s += [lane(x=-300), W(0.3), kfoe(-450, 0, "static", 0), W(1.6), lane(x=-300), W(0.3), C("hsd_tag tq_ctrl"), C("+forward"), W(5.0), C("-forward"), W(1.0)]
    for i in range(2):
        s += [lane(x=-300), W(0.5), C("hsd_tag tq_throw%d" % i), C("hsd_km_fire 0 tether 1 0 -170"), W(2.8), C("hsd_tag tq_fwd%d" % i), C("+forward"), W(6.0), C("-forward"), W(2.5)]
    return s + [CLEAR, C("hsd_km_log 0"), C("hsd_tag -")] + out("ion")



def km_graze2():
    """Graze with a fixed foe and the player shifted sideways (yaw 0): pass offsets about -90..+90 u in 15 u steps at
    chest height; then over the head: pitch so the missile passes 150..230 u above the foe's feet."""
    s = [C("hsd_km_log 1")] + _ride("northstar") + _prep() + [lane(), W(0.3), kfoe(700, 0, "static"), W(1.6)]
    for dy in (-90, -75, -60, -45, -30, 30, 45, 60, 75, 90):
        s += [lane(y=-1400 + dy), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag gs_%d" % dy)] + tap("offhand0") + [W(1.6)]
    for up in (-30, -20, -10, 0, 10, 20, 30):
        pitch = -math.degrees(math.atan2(up, 700))
        s += [lane(y=-1440, pitch=pitch), W(0.4), C("hsd_kit_refill 0"), C("hsd_tag gh_%d" % up)] + tap("offhand0") + [W(1.6)]
    return s + [CLEAR, C("hsd_km_log 0"), C("hsd_tag -")] + out("northstar")


PLANS = [n for n in list(globals()) if n.startswith("km_")]
