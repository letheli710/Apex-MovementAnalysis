"""Experiment plans for runner_wp.py (session tf2-weapons, 2026-11-08). Map mp_lf_stacks.

Geometry (runtime/data/20261029_003502_probe): spawn (24, -1864, 1). From the spawn, horizontal
traces at +20 run 1186 u at yaw 90 (wall at y = -678); at +240 / +400 they run 1968 u at yaw 120.
Static soldier targets (hsd_npc ... static) stand on the floor; the player's eye is ~60 above the feet
(checked in wp_smoke: PJNEW eye).
Weapon swap commands (scripts/kb_act.lst): +weaponCycle, weaponSelectPrimary0/1/2.
"""
import math

from plans import C, U, W  # noqa: F401

SPAWN = (24.0, -1864.0, 1.0)
EYE = 60.0          # standing eye height above the feet; corrected from wp_smoke if needed
S1 = (24.0, -1364.0, 1.0)   # soldier target 500 u ahead (yaw 90)


def setup(x=SPAWN[0], y=SPAWN[1], z=SPAWN[2], pitch=0.0, yaw=90.0):
    return C("hsd_setup %g %g %g 0 0 0 %.3f %.3f" % (x, y, z, pitch, yaw))


def aim(target, frm=SPAWN, eye=EYE):
    """pitch, yaw from the eye at frm (feet) to a world point."""
    dx, dy, dz = target[0] - frm[0], target[1] - frm[1], target[2] - (frm[2] + eye)
    return -math.degrees(math.atan2(dz, math.hypot(dx, dy))), math.degrees(math.atan2(dy, dx))


def setup_aim(target, frm=SPAWN):
    p, y = aim(target, frm)
    return setup(frm[0], frm[1], frm[2], p, y)


def tap(hold=0.05):
    return [C("+attack"), W(hold), C("-attack")]


def give(cls, *mods):
    """first draw of a new weapon takes ~1.6 s (wp_smoke: Double Take ready 1.57 s after the give);
    a trigger press before that is dropped, not buffered"""
    return [C(("hsd_weapon %s %s" % (cls, " ".join(mods))).strip()), W(2.2), C("hsd_wp_ammo"), W(0.1)]


def T(name):
    return C("hsd_tag " + name)


def soldier(pos=S1, hp=20000, yaw=-90):
    """quick-freeze soldier (hsd_wp_soldier). wp_a used W1's `hsd_npc soldier static`: it walked ~93 u
    (hits at y -1271 instead of -1364) before its 0.6 s freeze, and Double Take bolts passed through it."""
    return C("hsd_wp_soldier %g %g %g %g %d" % (pos[0], pos[1], pos[2], yaw, hp))


def soldier_w1(pos=S1, hp=20000, yaw=-90):
    return C("hsd_npc soldier static %g %g %g %g %d" % (pos[0], pos[1], pos[2], yaw, hp))


# ---------------------------------------------------------------- generic blocks

def blk_rate(cls, semi, n_tap=14, gap=0.06, hold=2.0, ads=False):
    """Fire rate: full clip, then hold the trigger (auto / burst) or tap every gap s (semi)."""
    s = [T("rate_" + ("ads" if ads else "hip")), setup(pitch=-3.0), C("hsd_wp_ammo"), W(0.3)]
    if ads:
        s += [C("+zoom"), W(0.6)]
    s += [C("hsd_wp_track %g" % (hold + 1.5))]
    if semi:
        for _ in range(n_tap):
            s += [C("+attack"), W(0.03), C("-attack"), W(gap)]
    else:
        s += [C("+attack"), W(hold), C("-attack")]
    s += [W(1.0)]
    if ads:
        s += [C("-zoom"), W(0.5)]
    return s


def blk_zoom():
    """ADS in / out timing (zoomfrac curve), standing still."""
    return [T("zoom"), setup(), W(0.4), C("+zoom"), W(1.0), C("-zoom"), W(1.0)]


def blk_reload(clip_partial=2, empty=True):
    s = []
    if empty:
        s += [T("reload_empty"), C("hsd_wp_ammo"), W(0.2), C("hsd_wp_clip 0"), W(0.3), C("+reload"), W(0.1), C("-reload"), W(5.5)]
    s += [T("reload_tac"), C("hsd_wp_ammo"), W(0.2), C("hsd_wp_clip %d" % clip_partial), W(0.3), C("+reload"), W(0.1), C("-reload"), W(5.0)]
    return s


def blk_reload_cancel(cuts, empty=True):
    """Start a reload, swap weapons away at cut s, swap back, reload again: does the second reload
    start late (reload_time_late* / reloadempty_time_late*)?"""
    s = []
    for cut in cuts:
        s += [T("rcut_%s_%.2f" % ("e" if empty else "t", cut)), C("hsd_wp_ammo"), W(0.2),
              C("hsd_wp_clip %d" % (0 if empty else 2)), W(0.3),
              C("+reload"), W(0.05), C("-reload"), W(cut - 0.05),
              C("+weaponCycle"), W(0.05), C("-weaponCycle"), W(1.4),
              C("+weaponCycle"), W(0.05), C("-weaponCycle"), W(1.4),
              C("+reload"), W(0.05), C("-reload"), W(5.0)]
    return s


def blk_spread_states():
    """GetAttackSpreadAngle in each movement state (no firing)."""
    s = [T("sp_stand"), setup(), W(0.8),
         T("sp_crouch"), C("+duck"), W(0.8), C("-duck"), W(0.4),
         T("sp_walk"), setup(yaw=-90.0), C("+forward"), W(0.9), C("-forward"), W(0.4),
         T("sp_sprint"), setup(yaw=-90.0), C("+speed"), C("+forward"), W(1.0), C("-forward"), C("-speed"), W(0.5),
         T("sp_air"), setup(yaw=90.0), C("+jump"), W(0.05), C("-jump"), W(0.7), U("ground", 0, 2.0), W(0.4),
         T("sp_ads"), setup(), C("+zoom"), W(0.8), C("-zoom"), W(0.5)]
    return s


def blk_raise():
    """Swap away and back: deploy / raise time until ready."""
    return [T("swap"), C("+weaponCycle"), W(0.05), C("-weaponCycle"), W(1.5),
            C("+weaponCycle"), W(0.05), C("-weaponCycle"), W(1.5)]


def blk_hits(cls, shots, ads=True):
    """shots: list of (tag, world point) aimed at from the spawn, one shot each, ADS."""
    s = [C("hsd_wp_ammo"), W(0.1)]
    for name, pt in shots:
        s += [T(name), setup_aim(pt), W(0.15)]
        if ads:
            s += [C("+zoom"), W(0.7)]
        s += [C("hsd_wp_track 3"), W(0.03)] + tap() + [W(1.2)]
        if ads:
            s += [C("-zoom"), W(0.3)]
        s += [C("hsd_wp_ammo"), W(0.1)]
    return s


def hit_points(target=S1):
    x, y, z = target
    return [("hit_chest", (x, y, z + 40.0)), ("hit_head", (x, y, z + 62.0)), ("hit_legs", (x, y, z + 15.0))]


def splash_points(target=S1, offs=(32, 64, 96, 128, 160, 200)):
    """floor points in front of the target (toward the player)."""
    x, y, z = target
    return [("splash_%d" % d, (x, y - d, z)) for d in offs]


def blk_path(pitches=(0.0, -10.0, -25.0), yaw=90.0, wait=3.0, ads=True):
    s = []
    for p in pitches:
        s += [T("path_p%g" % p), setup(pitch=p, yaw=yaw), W(0.2)]
        if ads:
            s += [C("+zoom"), W(0.7)]
        s += [C("hsd_wp_track %g" % (wait + 0.5)), W(0.03)] + tap() + [W(wait)]
        if ads:
            s += [C("-zoom"), W(0.3)]
        s += [C("hsd_wp_ammo"), W(0.1)]
    return s


def base(cls, *mods):
    return [C("hsd_info"), C("hsd_hp 5000"), setup(), W(0.3), soldier(), W(1.2)] + give(cls, *mods)


def end():
    return [C("hsd_wp_kill"), C("hsd_npc_kill all"), T("-"), W(0.5)]


# ---------------------------------------------------------------- plans

def wp_smoke():
    """Tool check: projectile track, hit log, client weapon line, titan / reaper targets, Archer lock."""
    s = [C("hsd_info"), C("hsd_hp 5000"), setup(), W(0.4), soldier(hp=5000), W(1.2)]
    s += give("mp_weapon_doubletake")
    s += [T("dt_hip"), C("hsd_wp_track 2"), W(0.05)] + tap() + [W(1.0)]
    s += [T("dt_ads"), C("+zoom"), W(0.7), C("hsd_wp_track 2"), W(0.05)] + tap() + [W(1.0), C("-zoom"), W(0.4)]
    s += [T("dt_reload"), C("+reload"), W(0.1), C("-reload"), W(3.2)]
    s += [T("titan"), C("hsd_wp_titan 24 -900 1 -90"), W(2.0), C("hsd_wp_reaper -200 -1300 1 -60"), W(1.5)]
    s += give("mp_weapon_rocket_launcher")
    s += [T("ar_lock"), setup(pitch=-6.0), C("+zoom"), W(2.4), C("hsd_wp_track 4"), W(0.05)] + tap(0.1) + [W(3.0), C("-zoom"), W(0.3)]
    s += give("mp_weapon_mgl")
    s += [T("mgl"), setup(pitch=-5.0), C("hsd_wp_track 4"), W(0.05)] + tap() + [W(3.0)]
    s += end()
    return s


TITAN = (24.0, -1000.0, 1.0)      # behind the soldier; aim at its chest over the soldier's head
REAPER = (-200.0, -1300.0, 1.0)


def targets_heavy():
    return [C("hsd_wp_titan %g %g %g -90" % TITAN), W(0.6), C("hsd_wp_reaper %g %g %g -60" % REAPER), W(0.8)]


def heavy_points():
    return [("hit_titan", (TITAN[0], TITAN[1], 150.0)), ("hit_reaper", (REAPER[0], REAPER[1], 80.0))]


def suite(cls, semi, cuts, extra=(), rate_ads=True, empty_cut=True, partial=2, path_pitches=(0.0, -12.0)):
    s = base(cls)
    s += blk_rate(cls, semi)
    if rate_ads:
        s += blk_rate(cls, semi, ads=True)
    s += blk_zoom()
    s += blk_spread_states()
    s += blk_hits(cls, hit_points())
    s += list(extra)
    s += blk_path(path_pitches)
    s += blk_reload(partial)
    s += blk_reload_cancel(cuts, empty=empty_cut)
    s += blk_raise()
    return s


def wp_a():
    """Double Take + Cold War."""
    s = suite("mp_weapon_doubletake", True, (0.6, 1.3, 2.0, 2.6),
              extra=[T("dt_hipshot"), setup(pitch=0.0), W(0.2), C("hsd_wp_track 1.5"), W(0.03)] + tap() + [W(1.0)] + targets_heavy()
              + blk_hits("mp_weapon_doubletake", heavy_points()))
    s += [C("hsd_wp_kill"), W(0.3)]
    s += suite("mp_weapon_pulse_lmg", True, (0.8, 1.8, 2.8, 3.8),
               extra=blk_hits("mp_weapon_pulse_lmg", splash_points()) + targets_heavy()
               + blk_hits("mp_weapon_pulse_lmg", heavy_points()), partial=4)
    s += end()
    return s


def moving_shot(name, vx, vy, pitch=-5.0, yaw=90.0, ads=False, wait=2.5):
    """fire right after hsd_setup gave the player a velocity (inherit-owner-velocity test)."""
    s = [T(name), setup(pitch=pitch, yaw=yaw), W(0.3)]
    if ads:
        s += [C("+zoom"), W(0.7)]
    s += [C("hsd_wp_track %g" % (wait + 0.5)),
          C("hsd_setup %g %g %g %g %g 0 %g %g" % (SPAWN[0], SPAWN[1], SPAWN[2] + 2, vx, vy, pitch, yaw)), W(0.02)]
    s += tap() + [W(wait)]
    if ads:
        s += [C("-zoom"), W(0.3)]
    return s + [C("hsd_wp_ammo"), W(0.1)]


def side_points(target, offs, z):
    """aim points beside a target (x offset), at height z."""
    return [("side_%+d" % d, (target[0] + d, target[1], z)) for d in offs]


def wp_b():
    """Double Take recheck (wp_dtfix) + Sidewinder SMR + Softball."""
    s = wp_dtfix()[:-4] + [C("hsd_wp_kill"), C("hsd_npc_kill all"), W(0.3)]
    s += suite("mp_weapon_smr", False, (0.7, 1.3, 1.9, 2.5),
              extra=blk_hits("mp_weapon_smr", splash_points(), ads=False) + moving_shot("smr_move", 300, 0)
              + targets_heavy() + blk_hits("mp_weapon_smr", heavy_points()))
    s += [C("hsd_wp_kill"), W(0.3)]
    s += suite("mp_weapon_softball", True, (1.0, 2.0), partial=3, path_pitches=(0.0, -12.0, -25.0),
               extra=blk_hits("mp_weapon_softball", splash_points(offs=(32, 64, 96, 128, 160)))
               + moving_shot("sb_move_side", 300, 0) + moving_shot("sb_move_fwd", 0, 300)
               + targets_heavy() + blk_hits("mp_weapon_softball", heavy_points()))
    s += end()
    return s


def wp_c():
    """MGL + Thunderbolt."""
    s = base("mp_weapon_mgl") + targets_heavy()
    s += blk_rate("mp_weapon_mgl", True, n_tap=10, gap=0.08) + blk_rate("mp_weapon_mgl", False, hold=2.5)
    s += blk_zoom() + blk_spread_states()
    s += blk_hits("mp_weapon_mgl", hit_points()[:1] + heavy_points())
    s += blk_hits("mp_weapon_mgl", side_points(TITAN, (-260, -160, -90, 90, 160), 120.0))
    s += blk_hits("mp_weapon_mgl", side_points(S1, (-60, -30, 30), 40.0))
    s += blk_hits("mp_weapon_mgl", side_points(REAPER, (-90, 90), 80.0))
    s += blk_path((0.0, -15.0, 20.0), wait=3.0)
    s += blk_reload(2) + blk_reload_cancel((0.7, 1.4, 2.0, 2.6)) + blk_raise()
    s += [C("hsd_wp_kill"), W(0.3), soldier(), W(1.2)]
    s += give("mp_weapon_arc_launcher") + targets_heavy()
    s += [T("tb_hip_try"), setup(pitch=-3.0), W(0.2), C("hsd_wp_track 2")] + tap(0.3) + [W(1.5)]
    s += blk_rate("mp_weapon_arc_launcher", False, hold=2.0, ads=True)
    s += blk_zoom() + blk_spread_states()
    s += blk_hits("mp_weapon_arc_launcher", side_points(S1, (100, 180, 230), 40.0))
    s += blk_hits("mp_weapon_arc_launcher", hit_points()[:1] + heavy_points())
    s += blk_hits("mp_weapon_arc_launcher", side_points(TITAN, (250, 380), 120.0))
    s += moving_shot("tb_move_fwd", 0, 300, pitch=-3.0, ads=True, wait=3.0)
    s += blk_path((0.0, -10.0), wait=3.0)
    s += blk_reload(0, empty=True)[:9] + blk_reload_cancel((1.0, 1.8, 2.4)) + blk_raise()
    s += end()
    return s


def lock_try(name, frm, target_pt, hold=2.6, fire=True, yaw_off=0.0):
    p, y = aim(target_pt, frm)
    s = [T(name), setup(frm[0], frm[1], frm[2], p, y + yaw_off), W(0.2), C("+zoom"), W(hold),
         C("hsd_wp_track 4"), W(0.03)]
    if fire:
        s += tap(0.1)
    s += [W(3.0), C("-zoom"), W(0.3), C("hsd_wp_ammo"), W(0.1)]
    return s


def wp_d():
    """Archer: lock rules, missile flight, damage, reload."""
    s = base("mp_weapon_rocket_launcher")
    s += [T("ar_hip_try"), setup(pitch=-3.0), W(0.2)] + tap(0.3) + [W(1.0)]
    s += lock_try("ar_soldier", SPAWN, (S1[0], S1[1], 40.0))
    s += lock_try("ar_wall_unlocked", SPAWN, (24.0, -678.0, 200.0), hold=1.0)
    s += blk_zoom() + blk_spread_states()
    s += [C("hsd_wp_kill"), W(0.3)] + targets_heavy()
    s += lock_try("ar_titan_864", SPAWN, (TITAN[0], TITAN[1], 150.0))
    s += lock_try("ar_titan_400", (24.0, -1400.0, 1.0), (TITAN[0], TITAN[1], 150.0))
    s += lock_try("ar_titan_off6", SPAWN, (TITAN[0], TITAN[1], 150.0), yaw_off=6.0)
    s += lock_try("ar_titan_off11", SPAWN, (TITAN[0], TITAN[1], 150.0), yaw_off=11.0, fire=False)
    s += lock_try("ar_titan_off20", SPAWN, (TITAN[0], TITAN[1], 150.0), yaw_off=20.0)
    s += lock_try("ar_reaper", SPAWN, (REAPER[0], REAPER[1], 80.0))
    s += lock_try("ar_titan_short", SPAWN, (TITAN[0], TITAN[1], 150.0), hold=0.9)
    s += [C("hsd_weapon mp_weapon_rocket_launcher fast_lock"), W(2.2), C("hsd_wp_ammo"), W(0.1)]
    s += lock_try("ar_fastlock_titan", SPAWN, (TITAN[0], TITAN[1], 150.0))
    s += [C("hsd_weapon mp_weapon_rocket_launcher"), W(2.2), C("hsd_wp_ammo"), W(0.1)]
    s += [T("reload_empty"), C("hsd_wp_clip 0"), W(0.3), C("+reload"), W(0.1), C("-reload"), W(4.5)]
    s += blk_reload_cancel((0.8, 1.6, 2.2)) + blk_raise()
    # VARIANTS-DRAFT: 16 guns have no projectile keys -> hitscan (inferred). A hitscan shot creates no
    # projectile entity (PJNEW) but still hits the soldier (WDMG); bolt guns create one.
    s += [soldier(), W(1.2)]
    for cls in ("mp_weapon_rspn101", "mp_weapon_dmr", "mp_weapon_wingman", "mp_weapon_g2", "mp_weapon_wingman_n",
                "mp_weapon_shotgun", "mp_weapon_mastiff"):
        s += give(cls) + [T("hitscan_" + cls[10:]), setup_aim((S1[0], S1[1], 40.0)), W(0.2), C("+zoom"), W(0.6),
                          C("hsd_wp_track 1.5"), W(0.03)] + tap() + [W(1.2), C("-zoom"), W(0.3)]
    # wp_b: Double Take never hit the soldier. Retest per bolt at the measured body position.
    s += give("mp_weapon_doubletake")
    # wp_a / wp_b: projectile hits on the frozen soldier cluster at x 24-32, y -1271..-1283 (a Softball
    # stuck there; a hit at z 92 was hit group 1), ~90 u behind its logged origin. Aim there.
    body = (28.0, -1277.0, 1.0)
    s += blk_hits("mp_weapon_doubletake", [("dt2_z%d" % z, (body[0], body[1], float(z))) for z in (30, 50, 70, 88)])
    s += end()
    return s


def wp_e():
    """Long free flights on mp_angel_city (run with --map mp_angel_city): the player stays at the
    spawn; sky traces first (hsd_wp_up), then each launcher at pitch -85 and at -45 in four yaws."""
    s = [C("hsd_info"), C("hsd_hp 5000"), W(0.3), C("hsd_wp_up 12000"), W(0.3)]
    for cls, n, ads in (("mp_weapon_smr", 5.0, False), ("mp_weapon_doubletake", 2.0, True),
                        ("mp_weapon_pulse_lmg", 4.0, False), ("mp_weapon_mgl", 3.5, False),
                        ("mp_weapon_softball", 4.0, False), ("mp_weapon_arc_launcher", 8.5, True)):
        s += give(cls)
        if ads:
            s += [C("+zoom")]
        for p, yaws in ((-85.0, (0,)), (-45.0, (0, 90, 180, 270))):
            for yaw in yaws:
                s += [T("sky_%s_p%g_y%d" % (cls[10:], p, yaw)), C("hsd_wp_look %g %d" % (p, yaw)), W(0.8 if ads else 0.3),
                      C("hsd_wp_track %g" % (n + 0.5)), W(0.03)] + tap() + [W(n), C("hsd_wp_ammo"), W(0.1)]
        if ads:
            s += [C("-zoom"), W(0.3)]
    s += [T("-"), W(0.5)]
    return s


def wp_dtfix():
    """Double Take against the quick-freeze soldier (wp_a's W1 soldier was not hit by bolts), plus
    an idle (unfrozen) W1 soldier for comparison."""
    s = [C("hsd_info"), C("hsd_hp 5000"), setup(), W(0.3), soldier(), W(1.5)] + give("mp_weapon_doubletake")
    s += blk_hits("mp_weapon_doubletake", hit_points())
    s += [C("hsd_wp_kill"), W(0.3), C("hsd_npc soldier idle %g %g %g -90 20000" % S1), W(1.5), C("hsd_npc_list")]
    s += blk_hits("mp_weapon_doubletake", [("idle_" + n, p) for n, p in hit_points()])
    s += [C("hsd_npc_kill all"), W(0.3), soldier_w1(), W(1.5), C("hsd_npc_list")]
    s += blk_hits("mp_weapon_doubletake", [("w1static_" + n, p) for n, p in hit_points()[:1]])
    s += [C("hsd_npc_kill all"), C("hsd_wp_kill"), W(0.3), soldier(), W(1.5)]
    s += give("mp_weapon_pulse_lmg") + blk_hits("mp_weapon_pulse_lmg", hit_points() + splash_points())
    s += end()
    return s


S2 = (24.0, -1500.0, 1.0)   # 364 u ahead; clear of the thin map wall at y ~ -1275 (wp_a..wp_d)


def wp_f():
    """Body / head / legs against a soldier that is put back on its spawn point after the freeze (wp_f):
    headshot and limb multipliers per weapon. Soldier at S2, 364 u from the spawn."""
    s = [C("hsd_info"), C("hsd_hp 5000"), setup(), W(0.3), soldier(pos=S2), W(1.5)]
    pts = [("chest", (S2[0], S2[1], 40.0)), ("head", (S2[0], S2[1], 62.0)), ("legs", (S2[0], S2[1], 15.0))]
    for cls in ("mp_weapon_doubletake", "mp_weapon_pulse_lmg", "mp_weapon_smr", "mp_weapon_softball", "mp_weapon_mgl",
                "mp_weapon_rspn101"):
        s += give(cls) + blk_hits(cls, [("%s_%s" % (cls[10:], n), pt) for n, pt in pts])
    s += end()
    return s
