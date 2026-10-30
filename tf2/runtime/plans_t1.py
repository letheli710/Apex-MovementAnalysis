"""T-1 (EPG rocket jump, real fire) and T-7 (thrown explosives' knockback), 2026-10-29.
Scenarios follow R5 research #64 (Apex-MovementAnalysis/research/epg/EPG-ROCKET-JUMP.md)
one-to-one where TF2 has the same thing. Imported into plans.py."""
from plans import C, U, W  # plans.py imports this module at its end
from plans_t5 import R, T, release

HP = C("hsd_hp 1000")  # EPG self-damage (90) would nearly kill a 100 hp pilot


def epg(mods=""):
    """fresh EPG (clip 5) with mods, then wait for it to be ready"""
    return [C(("hsd_weapon mp_weapon_epg " + mods).strip()), W(1.6)]


def fire():
    return [C("+attack"), W(0.05), C("-attack")]


def hold_fire():
    """after sprinting the weapon is still lowered and a short tap is lost: hold until it fires
    (fire_rate 1 / s, so still one shot)"""
    return [C("+attack"), W(0.6), C("-attack")]


def RP(pitch, y=-1864, vy=0):
    """reset on the spawn floor looking along +y at <pitch> (89 = at the feet)"""
    return C("hsd_setup 24 %g 2 0 %g 0 %g 90" % (y, vy, pitch))


def trial(name, mods, pre, act, settle=1.6):
    return T(name) + [HP] + epg(mods) + pre + act + [U("ground", 0, 4), W(settle)] + release()


def t1_probe():
    """tool check: one EPG shot per mode at the feet, one frag, one satchel, one gravity star"""
    s = [C("hsd_info")]
    for mods in ("", "jump_kit", "rocket_arena"):
        s += trial("p_epg_" + (mods or "base"), mods, [RP(89), W(0.4)], fire())
    for name, cls, fuse in (("p_frag", "mp_weapon_frag_grenade", 0.05), ("p_grav", "mp_weapon_grenade_gravity", 0.0)):
        s += T(name) + [HP, R(), W(0.5), C("hsd_throw %s %g" % (cls, fuse)), W(5.0)]
    s += T("p_satchel") + [HP, R(), W(0.5), C("hsd_throw mp_weapon_satchel 0"), W(1.5), C("hsd_detonate"), W(2.0)]
    s += T("-") + [W(1.0)]
    return s


def t1_epg():
    """T-1: EPG real fire. Modes: base (no impulse_force_explosions key), jump_kit (65000),
    rocket_arena (55000). Each case 3 times."""
    s = [C("hsd_info"), W(0.5)]
    for rep in range(3):
        # 2.1 force / mode, standing at the feet
        for mods in ("", "jump_kit", "rocket_arena"):
            s += trial("stand89_%s_%d" % (mods or "base", rep), mods, [RP(89), W(0.4)], fire())
        # base: jump + fire on the same frame (R5: 30000 only moved you in the air)
        s += trial("jumpfire89_base_%d" % rep, "", [RP(89), W(0.4)], [C("+jump")] + fire() + [C("-jump")])
        # 2.2 timing (jump_kit)
        s += trial("jumpfire89_jk_%d" % rep, "jump_kit", [RP(89), W(0.4)], [C("+jump")] + fire() + [C("-jump")])
        s += trial("fire_then_jump_jk_%d" % rep, "jump_kit", [RP(89), W(0.4)],
                   [C("+attack"), W(0.025), C("+jump"), W(0.05), C("-attack"), C("-jump")])
        for d in (0.05, 0.1, 0.2, 0.4):
            s += trial("jump_then_fire%03d_jk_%d" % (d * 1000, rep), "jump_kit", [RP(89), W(0.4)],
                       [C("+jump"), W(d)] + fire() + [C("-jump")])
        s += trial("jump_only_%d" % rep, "jump_kit", [RP(89), W(0.4)], [C("+jump"), W(0.05), C("-jump")])
        # 2.3 pitch (jump_kit)
        for p in (70, 45, 30, 20):
            s += trial("stand%d_jk_%d" % (p, rep), "jump_kit", [RP(p), W(0.4)], fire())
        for p in (70, 45):
            s += trial("jumpfire%d_jk_%d" % (p, rep), "jump_kit", [RP(p), W(0.4)], [C("+jump")] + fire() + [C("-jump")])
        # 2.4 with movement (jump_kit)
        s += trial("sprint89_jk_%d" % rep, "jump_kit", [RP(89), W(0.3), C("+speed"), C("+forward"), W(0.8)], fire())
        s += trial("sprintjump89_jk_%d" % rep, "jump_kit", [RP(89), W(0.3), C("+speed"), C("+forward"), W(0.8)],
                   [C("+jump")] + fire() + [C("-jump")])
        s += trial("sprintjump70_jk_%d" % rep, "jump_kit", [RP(70), W(0.3), C("+speed"), C("+forward"), W(0.8)],
                   [C("+jump")] + fire() + [C("-jump")])
        s += trial("slide89_jk_%d" % rep, "jump_kit", [RP(89), W(0.3), C("+speed"), C("+forward"), W(0.8),
                                                       C("+duck"), W(0.15)], fire())
        s += trial("backjump70_jk_%d" % rep, "jump_kit", [RP(70, y=-1500), W(0.3), C("+back"), W(0.6)],
                   [C("+jump")] + fire() + [C("-jump")])
    s += T("-") + [W(1.0)]
    return s


def t7_throw():
    """T-7: thrown explosives at the feet (frag, gravity star, satchel; thermite / electric smoke
    as no-knockback controls), standing and in the air. Each case 3 times."""
    s = [C("hsd_info"), W(0.5)]
    for rep in range(3):
        s += T("frag_stand_%d" % rep) + [HP, R(), W(0.5), C("hsd_throw mp_weapon_frag_grenade 0.05"), W(2.0)]
        s += T("frag_air_%d" % rep) + [HP, R(), W(0.5), C("+jump"), U("air", 0, 1), C("-jump"),
                                         C("hsd_throw mp_weapon_frag_grenade 0.02 0 0 -20"), U("ground", 0, 4), W(1.5)]
        s += T("grav_stand_%d" % rep) + [HP, R(), W(0.5), C("hsd_throw mp_weapon_grenade_gravity 0"), W(6.0)]
        s += T("satchel_stand_%d" % rep) + [HP, R(), W(0.5), C("hsd_throw mp_weapon_satchel 0"), W(1.2),
                                              C("hsd_detonate"), W(2.0)]
        s += T("satchel_jump_%d" % rep) + [HP, R(), W(0.5), C("hsd_throw mp_weapon_satchel 0"), W(1.2), C("+jump"),
                                             U("air", 0, 1), C("-jump"), C("hsd_detonate"), U("ground", 0, 4), W(1.5)]
        s += T("thermite_stand_%d" % rep) + [HP, R(), W(0.5), C("hsd_throw mp_weapon_thermite_grenade 0.05"), W(2.0)]
        s += T("elec_stand_%d" % rep) + [HP, R(), W(0.5), C("hsd_throw mp_weapon_grenade_electric_smoke 0.05"), W(2.0)]
    s += T("-") + [W(1.0)]
    return s


def t1_sky():
    """find open floor with headroom on mp_lf_stacks: grid of up / down traces"""
    s = []
    # <= ~17 commands/s: faster gets the player kicked ("Sent too many stringcmd commands")
    for x in range(-1200, 1801, 300):
        for y in range(-2400, 901, 300):
            s += [C("hsd_trace %d %d 60 %d %d 3000" % (x, y, x, y)), W(0.06), C("hsd_trace %d %d 60 %d %d -400" % (x, y, x, y)),
                  W(0.06)]
    return s


def t1_sprint():
    """Sprint cases redone: TF2 lowers the weapon while sprinting (the t1_epg sprint trials never
    fired). Release sprint before firing on the ground; in the air release it at the jump."""
    s = [C("hsd_info"), W(0.5)]
    for rep in range(3):
        s += trial("sprint_release89_jk_%d" % rep, "jump_kit", [RP(89), W(0.3), C("+speed"), C("+forward"), W(0.8),
                                                                C("-speed")], hold_fire())
        s += trial("sprintjump89_jk_%d" % rep, "jump_kit", [RP(89), W(0.3), C("+speed"), C("+forward"), W(0.8)],
                   [C("-speed"), C("+jump")] + hold_fire() + [C("-jump")])
        s += trial("sprintjump70_jk_%d" % rep, "jump_kit", [RP(70), W(0.3), C("+speed"), C("+forward"), W(0.8)],
                   [C("-speed"), C("+jump")] + hold_fire() + [C("-jump")])
        # sprint jump, fire on the way up (0.1 s), weapon raised by then
        s += trial("sprintjump89_late_jk_%d" % rep, "jump_kit", [RP(89), W(0.3), C("+speed"), C("+forward"), W(0.8)],
                   [C("-speed"), C("+jump"), W(0.1)] + hold_fire() + [C("-jump")])
    s += T("-") + [W(1.0)]
    return s


def t1_sweep():
    """knockback force sweep at the feet (R5 #64 §3): ground threshold and speed cap, standing and
    in the air (right after a jump)"""
    s = [C("hsd_info"), W(0.5)]
    for force in (10000, 17500, 25000, 30000, 31500, 35000, 40000, 50000, 65000, 80000, 100000, 150000, 200000):
        s += T("sw_stand_%d" % force) + [HP, R(), W(0.5), C("hsd_blast %d" % force), W(0.3), U("ground", 0, 5), W(1.0)]
    for force in (10000, 17500, 30000, 65000):
        s += T("sw_air_%d" % force) + [HP, R(), W(0.5), C("+jump"), U("air", 0, 1), C("-jump"), W(0.05),
                                         C("hsd_blast %d" % force), U("ground", 0, 5), W(1.0)]
    s += T("-") + [W(1.0)]
    return s
