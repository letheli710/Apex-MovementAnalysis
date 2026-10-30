"""Expansion worker W2 (2026-10-29, expansion/w2/W2-REPORT.md): cloak, A-Wall, gravity star,
satchel, grenade throws and the ADS hover kit. Server helpers in hsd_diag_w2.gnut (w2_*).
Same runner rules as T5; mp_lf_stacks spawn floor runs 1186 u along +y."""
from plans import C, U, W  # plans.py imports this module at its end
from plans_t5 import SPAWN, R, RA, T, release

HP = C("hsd_hp 1000")
X, Y = SPAWN[0], SPAWN[1]


def tap(key, hold=0.1):
    return [C("+" + key), W(hold), C("-" + key)]


def look(pitch, yaw=90, x=X, y=Y, z=2, vx=0, vy=0, vz=0):
    return C("hsd_setup %g %g %g %g %g %g %g %g" % (x, y, z, vx, vy, vz, pitch, yaw))


def w2_a():
    """Cloak (duration, regen, moving, firing, damage), A-Wall (size, health, life, one-way
    shots, recharge) and the pas_ads_hover class mod (trigger, duration, input, recharge)."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), W(0.5),
         C("w2_cvars gravity_grenade_decel gravity_grenade_projectile_min_speed offhandTossOverheadPitchThreshold sv_gravity"),
         W(0.3)]
    # cloak: idle 3 s, walk 2 s, sprint 2 s, then stand until it ends and the charge refills
    s += T("cloak_move") + [C("hsd_offhand mp_ability_cloak 1"), R(), W(0.4), C("w2_watch 42")] + tap("offhand1") + [
        W(3.0), C("+forward"), W(2.0), C("-forward"), W(1.0), C("+speed"), C("+forward"), W(2.0)] + release() + [W(33.0)]
    # firing the main weapon breaks it
    s += T("cloak_fire") + [C("w2_refill"), R(), W(0.4), C("w2_watch 8")] + tap("offhand1") + [W(2.0)] + \
        tap("attack", 0.15) + [W(5.5)]
    # taking damage (no knockback)
    s += T("cloak_dmg") + [HP, C("w2_refill"), R(), W(0.4), C("w2_watch 8")] + tap("offhand1") + [W(2.0),
                                                                                                 C("hsd_blast 0 5 0 0 2"), W(5.5)]
    # A-Wall thrown ahead (+y); shoot it from the thrower's side, then from the far side
    s += T("awall") + [C("hsd_offhand mp_weapon_deployable_cover 1"), R(), W(0.4), C("w2_watch 40")] + \
        tap("offhand1", 0.5) + [W(2.0)] + tap("attack", 1.0) + [W(1.0), C("hsd_weapon mp_weapon_rspn101"), W(0.8),
                                                                 R(y=Y + 420, yaw=270), W(0.6)] + tap("attack", 1.0) + [
        W(1.0), C("hsd_weapon mp_weapon_rspn101"), W(0.8), R(y=Y + 420, yaw=270), C("+duck"), W(0.6)] + \
        tap("attack", 1.0) + [C("-duck"), W(31.0)]
    # second wall at once (both live?) is not possible: one charge (100 per throw, clip 100)
    # hover kit
    s += T("hover_on") + [C("w2_mods pas_ads_hover"), W(0.5), C("hsd_query hoverEnabled hoverMeterRate hoverSafety "
                                                                 "hoverStrafeScale hoverTightnessHorizontal hoverTightnessVertical"), W(0.3)]
    # jump, ADS at the top for 6 s
    s += T("hv_jump") + [R(), W(0.5)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"), W(6.0), C("-zoom"),
                                                             U("ground", 0, 6), W(1.0)]
    # same again right away (charge left?), then after 6 s of rest
    s += T("hv_again") + [R(), W(0.2)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"), W(6.0), C("-zoom"),
                                                              U("ground", 0, 6)]
    s += T("hv_rest6") + [W(6.0), R(), W(0.3)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"), W(6.0),
                                                                   C("-zoom"), U("ground", 0, 6), W(8.0)]
    # ADS held from take-off (hoverSafety 0.25 s)
    s += T("hv_early") + [R(), W(0.5), C("+zoom"), W(0.1)] + tap("jump", 0.05) + [U("air", 0, 1), W(3.0), C("-zoom"),
                                                                                  U("ground", 0, 6), W(8.0)]
    # strafe and forward while hovering
    s += T("hv_strafe") + [R(), W(0.5)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"), W(0.6),
                                                               C("+moveright"), W(1.5), C("-moveright"), C("+forward"),
                                                               W(1.5), C("-forward"), W(1.0), C("-zoom"), U("ground", 0, 6),
                                                               W(8.0)]
    # moving fast into a hover (sprint jump at 400 forward): horizontal ease-in
    s += T("hv_fast") + RA(y=Y, z=150, vy=400) + [W(0.3), C("+zoom"), W(3.0), C("-zoom"), U("ground", 0, 6), W(8.0)]
    # falling into a hover (vertical ease-in), then jump / duck while hovering
    s += T("hv_fall") + RA(y=Y + 300, z=500) + [W(0.4), C("+zoom"), W(2.0), C("+duck"), W(0.8), C("-duck"), W(0.4)] + \
        tap("jump", 0.05) + [W(1.0), C("-zoom"), U("ground", 0, 6), W(1.0)]
    s += T("hover_off") + [C("w2_mods"), W(0.3), C("hsd_query hoverEnabled")]
    s += T("-") + [W(1.0)]
    return s


def grav_pull(name, d, extra=()):
    """enemy gravity star planted on the floor d u ahead of the standing player"""
    return T(name) + [HP, C("w2_clear"), R(), W(0.4), C("w2_watch 5"),
                      C("w2_shoot mp_weapon_grenade_gravity 1 0 %g %g 20 0 0 -1" % (X, Y + d))] + list(extra) + [
        W(4.5)] + release() + [U("ground", 0, 4), W(0.5)]


def w2_b():
    """Gravity star pull law (enemy-team star vs the player), its effect on a projectile,
    satchel (throw, detonate, max deployed, falloff), real throws of both (speed, gravity,
    inherited velocity)."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), C("w2_cvars gravity_grenade_decel "
                                                            "gravity_grenade_projectile_min_speed sv_gravity"), W(0.5)]
    for d in (80, 150, 220, 290, 360):
        s += grav_pull("gp_%d" % d, d)
    s += grav_pull("gp_200_fwd", 200, (W(1.0), C("+back")))  # walking away from it
    s += grav_pull("gp_200_jump", 200, (W(1.0),) + tuple(tap("jump", 0.05)))  # airborne during the strong pull
    # projectile through a star: frag shot across +x at z 62, 60 u in front of the star
    shot = "w2_shoot mp_weapon_frag_grenade %s 2.5 -400 %g 70 700 0 0" % ("%s", Y + 600)
    s += T("gproj_ctrl") + [C("w2_clear"), R(), W(0.3), C("w2_watch 3"), C(shot % "1"), W(3.0)]
    s += T("gproj_enemy") + [C("w2_clear"), R(), W(0.3), C("w2_watch 5"),
                             C("w2_shoot mp_weapon_grenade_gravity 0 0 %g %g 20 0 0 -1" % (X, Y + 600)), W(1.2),
                             C(shot % "1"), W(3.5)]
    s += T("gproj_own") + [C("w2_clear"), R(), W(0.3), C("w2_watch 5"),
                           C("w2_shoot mp_weapon_grenade_gravity 0 0 %g %g 20 0 0 -1" % (X, Y + 600)), W(1.2),
                           C(shot % "0"), W(3.5)]
    # FireWeaponGrenade's velocity argument: a unit vector or a velocity?
    s += T("fire_arg") + [C("w2_clear"), C("w2_watch 2"),
                          C("w2_shoot mp_weapon_satchel 0 0 %g %g 300 0 1 0" % (X, Y + 100)), W(0.3),
                          C("w2_shoot mp_weapon_satchel 0 0 %g %g 300 0 300 0" % (X + 50, Y + 100)), W(1.5)]
    # real throws: gravity star (pitch 0 / -20 / -45, in the air moving +y at 400) and satchel
    for cls, slot_name in (("mp_weapon_grenade_gravity", "gt"), ("mp_weapon_satchel", "st")):
        s += [C("w2_clear"), C("hsd_offhand %s 0" % cls), W(0.5)]
        for p in (0, -20, -45):
            s += T("%s_p%d" % (slot_name, -p)) + [C("w2_clear"), C("w2_refill"), look(p), W(0.4), C("w2_watch 4")] + \
                tap("offhand0", 0.45) + [W(3.0)]
        s += T("%s_air400" % slot_name) + [C("w2_clear"), C("w2_refill"), look(0, z=200, vy=400), W(0.05), U("air", 0, 1),
                                           C("w2_watch 4")] + tap("offhand0", 0.3) + [U("ground", 0, 4), W(2.5)]
        s += T("%s_side400" % slot_name) + [C("w2_clear"), C("w2_refill"), look(0, z=200, vx=400), W(0.05), U("air", 0, 1),
                                            C("w2_watch 4")] + tap("offhand0", 0.3) + [U("ground", 0, 4), W(2.5)]
    # satchel detonation: attack with the clacker / ordnance again / script
    s += T("sd_attack") + [HP, C("w2_clear"), C("w2_refill"), look(-20), W(0.4), C("w2_watch 5")] + tap("offhand0", 0.45) + \
        [W(1.5)] + tap("attack", 0.1) + [W(2.5)]
    s += T("sd_offhand") + [HP, C("w2_clear"), C("w2_refill"), look(-20), W(0.4), C("w2_watch 5")] + tap("offhand0", 0.45) + \
        [W(1.5)] + tap("offhand0", 0.1) + [W(2.5)]
    # three throws (refill between): how many stay; then script detonation stagger
    s += T("sd_three") + [HP, C("w2_clear"), look(-20), W(0.3), C("w2_watch 9")]
    for i in range(3):
        s += [C("w2_refill"), look(-20 + 8 * i, 90 - 15 + 15 * i), W(0.3)] + tap("offhand0", 0.45) + [W(1.2)]
    s += [W(1.0), C("hsd_detonate"), W(3.0)]
    # damage falloff: one planted satchel at the feet + d along +y, script detonation
    for d in (0, 60, 120, 180, 240, 300):
        s += T("sf_%d" % d) + [HP, C("w2_clear"), R(), W(0.4), C("w2_watch 3"), C("hsd_throw mp_weapon_satchel 0 0 %d 0" % d),
                               W(1.0), C("hsd_detonate"), W(2.0)] + [U("ground", 0, 4), W(0.3)]
    # hover follow-ups (w2_a): control without the kit, re-ADS within one jump, re-hover right
    # after landing, forward input while hovering
    s += T("hv_ctrl") + [C("w2_mods"), W(0.5), R(), W(0.5)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"),
                                                                              W(2.5), C("-zoom"), U("ground", 0, 6), W(1.0)]
    s += [C("w2_mods pas_ads_hover"), W(0.5)]
    s += T("hv_split") + [R(), W(6.0)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"), W(0.6), C("-zoom"),
                                                              W(0.4), C("+zoom"), W(3.0), C("-zoom"), U("ground", 0, 6)]
    s += T("hv_reland") + [W(0.3)] + tap("jump", 0.05) + [U("air", 0, 1), W(0.35), C("+zoom"), W(3.0), C("-zoom"),
                                                          U("ground", 0, 6), W(6.0)]
    s += T("hv_fwd") + RA(y=Y - 300, z=300) + [W(0.3), C("+zoom"), W(0.4), C("+forward"), W(2.0), C("-forward"),
                                               C("-zoom"), U("ground", 0, 6), W(1.0)]
    s += [C("w2_mods")]
    s += T("-") + [C("w2_clear"), W(1.0)]
    return s


def w2_c():
    """Follow-ups: projectiles through a star (w2_shoot's velocity argument is a direction
    scaled by projectile_launch_speed: frag 1100, satchel 750), the grounded pull edge
    (pulled at 200, not at 220 in w2_b) and forward input while hovering."""
    s = [C("hsd_info"), C("hsd_weapon mp_weapon_rspn101"), W(0.5)]
    sy = Y + 600
    star = "w2_shoot mp_weapon_grenade_gravity 0 0 %g %g 20 0 0 -1" % (X, sy)
    for name, cls, team, dy in (("pp_frag", "mp_weapon_frag_grenade", "1", 60), ("pp_frag_own", "mp_weapon_frag_grenade", "0", 60),
                                ("pp_satchel", "mp_weapon_satchel", "1", 60), ("pp_frag_far", "mp_weapon_frag_grenade", "1", 200)):
        shot = "w2_shoot %s %s 3.0 -500 %g 70 1 0 0" % (cls, team, sy + dy)
        s += T(name + "_ctrl") + [C("w2_clear"), R(), W(0.3), C("w2_watch 2.5"), C(shot), W(2.5)]
        s += T(name) + [C("w2_clear"), R(), W(0.3), C("w2_watch 3.5"), C(star), W(1.2), C(shot), W(2.5)]
    for d in (170, 185, 200, 210, 200):
        s += grav_pull("gq_%d" % d, d)
    s += [C("w2_mods pas_ads_hover"), W(0.5)]
    s += T("hv_fwd2") + RA(y=Y, z=150) + [W(0.3), C("+zoom"), W(0.4), C("+forward"), W(1.5), C("-forward"),
                                          C("-zoom"), U("ground", 0, 6), W(1.0)]
    s += T("hv_back2") + [W(4.0)] + RA(y=Y + 500, z=150) + [W(0.3), C("+zoom"), W(0.4), C("+back"), W(1.5), C("-back"),
                                                           C("-zoom"), U("ground", 0, 6), W(1.0)]
    s += [C("w2_mods")] + T("-") + [C("w2_clear"), W(1.0)]
    return s


def w2_d():
    """Projectile through a star, fired from beside the player (w2_c's shots from x -500 were
    respawned near the player and passed 400 u from the star): star on the floor 300 u ahead,
    frag along +y 40 u to the side at eye height, fired 1.2 s after the star (strong pull)."""
    s = [C("hsd_info"), W(0.5)]
    star = "w2_shoot mp_weapon_grenade_gravity 0 0 %g %g 20 0 0 -1" % (X, Y + 300)
    for name, team, dx in (("pd_enemy", "1", 40), ("pd_own", "0", 40), ("pd_enemy100", "1", 100)):
        shot = "w2_shoot mp_weapon_frag_grenade %s 3.0 %g %g 62 0 1 0" % (team, X + dx, Y + 40)
        s += T(name + "_ctrl") + [C("w2_clear"), R(), W(0.3), C("w2_watch 2"), C(shot), W(2.0)]
        s += T(name) + [C("w2_clear"), R(), W(0.3), C("w2_watch 3.5"), C(star), W(1.2), C(shot), W(2.3)]
    s += T("-") + [C("w2_clear"), W(1.0)]
    return s
