#!/usr/bin/env python3
"""Cases for C1-C5 + bonus. py -3 -I gen_cases.py > cases.txt   (format: tag|weapon|schedule|secs, read by an_run.py)
C1 reload during slide / zipline / grapple (R-301, both orders), C2 one gun per class, C3 sprint at several speeds (ramp / speed_boost / wall; move_slow cancels sprint),
C4 crouch-walk at several speeds, C5 crouch press/release (Wingman vs R-301), F fire for the overlay bytes."""
L = []
TP = lambda x, y, z, yaw=0: f"sv try {{ entity p = GetPlayerArray()[0] ~ p.SetOrigin( <{x}, {y}, {z}> ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SetAngles( <0, {yaw}, 0> ) ~ p.SnapEyeAngles( <0, {yaw}, 0> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( \"tp\" )"
AMMO = 'sv try { entity p = GetPlayerArray()[0] ~ p.AmmoPool_SetCapacity( 999 ) ~ for ( int i = 0 ~ i < 8 ~ i++ ) { try { p.AmmoPool_SetCount( i, 300 ) } catch ( e1 ) { } } } catch ( e ) { printt( "[RT] rx err " + string( e ) ) } ~ AgentLink_Reply( "rx" )'
CLIP = AMMO + '; sv try { entity w = GetPlayerArray()[0].GetActiveWeapon( eActiveInventorySlot.mainHand ) ~ w.SetWeaponPrimaryClipCount( 3 ) } catch ( e ) { } ~ AgentLink_Reply( "clip" )'
ZIP = 'sv try { foreach ( entity e in GetEntArrayByScriptName( "hsd_zip" ) ) e.Destroy() ~ array<entity> all ~ all.extend( CreateZipline( <-14600, 6800, 394.92>, <-12600, 6800, 394.92>, false, 100 ) ) ~ foreach ( entity e in all ) e.SetScriptName( "hsd_zip" ) ~ AgentLink_Reply( "zip " + all.len() ) } catch ( e ) { AgentLink_Reply( "zip err " + string( e ) ) }'
GR = 'sv try { entity p = GetPlayerArray()[0] ~ p.TakeOffhandWeapon( OFFHAND_TACTICAL ) } catch ( e ) { } ~ try { GetPlayerArray()[0].GiveOffhandWeapon( "mp_ability_grapple", OFFHAND_TACTICAL, [] ) } catch ( e2 ) { printt( "[RT] ab err " + string( e2 ) ) } ~ AgentLink_Reply( "ab" )'
HOLD = 'sv thread void function() { entity p = GetPlayerArray()[0] ~ float t0 = Time() ~ while ( Time() - t0 < 2.2 ) { if ( !p.IsOnGround() ) { wait 0.1 ~ continue } ~ p.SetVelocity( <380, 0, p.GetVelocity().z> ) ~ wait 0.1 } }() ~ AgentLink_Reply( "h" )'
SLOW = lambda x: f'sv try {{ StatusEffect_AddEndless( GetPlayerArray()[0], eStatusEffect.move_slow, {x} ) }} catch ( e ) {{ printt( "[RT] se err " + string( e ) ) }} ~ AgentLink_Reply( "slow {x}" )'
BOOST = lambda x: f'sv try {{ StatusEffect_AddEndless( GetPlayerArray()[0], eStatusEffect.speed_boost, {x} ) }} catch ( e ) {{ printt( "[RT] se err " + string( e ) ) }} ~ AgentLink_Reply( "boost {x}" )'
SPEED = lambda m: "" if m == "n" else (SLOW(m[1:]) if m[0] == "s" else BOOST(m[1:])) + "; "
ZTP = TP(-14500, 6800, 294.92)
GTP = TP(-12321.5, 7400, 294.92)

# C1: reload x movement, R-301 (tactical reload 2.4 s, unlock about 1.6 s)
for r in (1, 2):
    c = [
        ("stand", f"{CLIP}; wait 0.3; tap reload; wait 3.2", 6),
        ("walk", f"{CLIP}; down forward; wait 0.8; tap reload; wait 3.0; up forward", 6.5),
        ("slide_rl", f"{CLIP}; down forward; down speed; wait 1.2; down duck; wait 0.15; tap reload; wait 3.0; up duck; up speed; up forward", 7),
        ("slidehold_rl", f"{CLIP}; down forward; down speed; wait 1.2; down duck; {HOLD}; wait 0.15; tap reload; wait 3.0; up duck; up speed; up forward", 7),
        ("rl_slide", f"{CLIP}; down forward; down speed; wait 1.2; tap reload; wait 0.3; down duck; wait 3.0; up duck; up speed; up forward", 7),
        ("zip_rl", f"{ZIP}; {ZTP}; {CLIP}; wait 0.3; tap use; wait 0.5; tap reload; wait 3.0", 7),
        ("rl_zip", f"{ZIP}; {ZTP}; {CLIP}; wait 0.3; tap reload; wait 0.3; tap use; wait 3.0", 7),
        ("grapple_rl", f"{GR}; {GTP}; {CLIP}; wait 0.4; tap offhand1; wait 0.35; tap reload; wait 3.2", 7),
        ("rl_grapple", f"{GR}; {GTP}; {CLIP}; wait 0.4; tap reload; wait 0.3; tap offhand1; wait 3.5", 7),
        ("rl_grapple_late", f"{GR}; {GTP}; {CLIP}; wait 0.4; tap reload; wait 1.9; tap offhand1; wait 2.5", 7),
    ]
    for n, s, secs in c:
        L.append(f"c1_{n}_{r}|rspn101|{s}|{secs}")

# C2: one gun per class (+ R-301 / Wingman reference come from C1 / C5)
STATES = {
    "stand": ("wait 3.0", 5),
    "walk": ("down forward; wait 5; up forward; wait 1.0", 8),
    "crouch": ("down duck; wait 2.5; up duck; wait 1.5", 6),
    "crouchwalk": ("down duck; wait 0.8; down forward; wait 4.5; up forward; up duck; wait 1.5", 9),
    "sprint": ("down forward; down speed; wait 4.5; up speed; up forward; wait 1.5", 8.5),
    "slide": ("down forward; down speed; wait 1.2; down duck; wait 2.0; up duck; up speed; up forward; wait 1.0", 6.5),
    "jump": ("wait 0.8; tap jump; wait 2.2", 5),
    "adswalk": ("down zoom; wait 0.6; down forward; wait 3.5; up forward; up zoom; wait 0.8", 7),
    "reload": (f"{CLIP}; wait 0.3; tap reload; wait 4.5", 7),
    "reloadwalk": (f"{CLIP}; down forward; wait 0.8; tap reload; wait 4.5; up forward", 8),
}
for g, w in (("r99", "r97"), ("spitfire", "lmg"), ("peacekeeper", "energy_shotgun"), ("longbow", "dmr"), ("p2020", "semipistol"), ("g7", "g2")):
    for s, (sched, secs) in STATES.items():
        L.append(f"c2_{g}_{s}_1|{w}|{sched}|{secs}")

# C3: sprint and walk at several speeds (n = normal, s = move_slow, b = speed_boost)
for r in (1, 2):
    for g, w in (("r301", "rspn101"), ("wingman", "wingman")):
        # move_slow cancels sprint (tested), so speed is varied by the sprint ramp, speed_boost and a wall
        for m in ("n", "b0.1", "b0.3", "b0.6"):
            L.append(f"c3_{g}_sprint_{m}_{r}|{w}|{SPEED(m)}down forward; down speed; wait 4.0; up speed; up forward; wait 1.0|7.5")
        L.append(f"c3_{g}_sprint_wall_{r}|{w}|{TP(-12250, 7400, 294.92)}; wait 0.3; down forward; down speed; wait 4.0; up speed; up forward; wait 1.0|7.5")
        for m in ("s0.3", "s0.6"):
            L.append(f"c3_{g}_walk_{m}_{r}|{w}|{SPEED(m)}down forward; wait 4.5; up forward; wait 0.8|7.5")
# C4: crouch-walk at several speeds
for r in (1, 2):
    for g, w in (("r301", "rspn101"), ("wingman", "wingman")):
        for m in ("n", "s0.3", "s0.6", "b0.5"):
            L.append(f"c4_{g}_cw_{m}_{r}|{w}|{SPEED(m)}down duck; wait 0.9; down forward; wait 4.5; up forward; wait 0.8; up duck; wait 1.2|9.5")
# C5: crouch press / release
for r in (1, 2, 3):
    for g, w in (("r301", "rspn101"), ("wingman", "wingman")):
        L.append(f"c5_{g}_crouch_{r}|{w}|down duck; wait 2.0; up duck; wait 2.0|6")
        L.append(f"c5_{g}_tapduck_{r}|{w}|tap duck; wait 1.5; down duck; wait 0.3; up duck; wait 2.0|6")
# F: fire (overlay bytes), R-301 hold, Wingman taps
for r in (1, 2):
    L.append(f"f_r301_fire_{r}|rspn101|wait 0.3; down attack; wait 1.2; up attack; wait 1.0|4.5")
    L.append(f"f_wingman_fire_{r}|wingman|wait 0.3; tap attack; wait 0.5; tap attack; wait 0.5; tap attack; wait 1.0|4.5")
print("\n".join(L))
