#!/usr/bin/env python3
"""B9 cases: the movement items B-STATES could not run.
  grapple  : Pathfinder grapple at the G6 world wall (x -11921.5), the scene where the hook really pulls; fire while pulled, hip / ADS; same schedule without grapple as baseline
  mantle   : the gen_b2 mantle wall; sprint, jump, (ADS pressed in the air), fire held through the mantle; a client thread logs IsMantling / zf / clip
  kinetic  : Peacekeeper + hopup_kinetic_loader, 3 shots then slide vs stand (clip changes logged by gun.nut)
  tempo    : Sentinel + hopup_marksmans_tempo, taps every 0.1 s for 9 s (intervals from the atk hook) vs no hopup
py -3 -I gen_b9.py > cases_b9.txt
Follow-ups written by hand from these templates: cases_b9b.txt (grapple, fire held 3.2 s from the press, to find when firing comes back),
cases_b9c.txt (mantle with fire held 4 s and the logger 6 s; the 2 s runs released forward before the mantle finished)."""
L = []
TP = lambda x, y, z, yaw=0, pitch=0: f"sv try {{ entity p = GetPlayerArray()[0] ~ p.SetOrigin( <{x}, {y}, {z}> ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SetAngles( <0, {yaw}, 0> ) ~ p.SnapEyeAngles( <{pitch}, {yaw}, 0> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( \"tp\" )"
WALL = 'sv try { foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo" ) ) e.Destroy() ~ asset m = $"mdl/rocks/rock_white_chalk_modular_wallrun_02.rmdl" ~ MapEdit_PrecacheModel( m ) ~ entity pr = CreatePropDynamic( m, <-13600, 6500, 294.92>, <0, 0, 0>, SOLID_VPHYSICS, 20000 ) ~ pr.AllowMantle() ~ pr.SetScriptName( "hsd_test_geo" ) ~ AgentLink_Reply( "wall" ) } catch ( e ) { AgentLink_Reply( "wall err " + string( e ) ) }'
GR = 'sv try { entity p = GetPlayerArray()[0] ~ p.TakeOffhandWeapon( OFFHAND_TACTICAL ) } catch ( e ) { } ~ try { GetPlayerArray()[0].GiveOffhandWeapon( "mp_ability_grapple", OFFHAND_TACTICAL, [] ) } catch ( e2 ) { printt( "[RT] ab err " + string( e2 ) ) } ~ AgentLink_Reply( "ab" )'
MT = lambda secs: ('cl void functionref() mtf = void function() { try { entity p = GetLocalClientPlayer() ~ float t0 = Time() ~ while ( Time() - t0 < ' + str(secs) +
                   ' ) { entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand ) ~ printt( format( "[RT] mt t=%.4f m=%d zf=%.3f clip=%d gr=%d", Time(), p.IsMantling() ? 1 : 0, p.GetZoomFrac(), IsValid( w ) ? w.GetWeaponPrimaryClipCount() : -1, p.IsOnGround() ? 1 : 0 ) ) ~ WaitFrame() } '
                   '} catch ( e ) { printt( "[RT] mt err " + string( e ) ) } } ~ thread mtf() ~ AgentLink_Reply( "mt" )')
ROOF = TP(-9949.0, -1488.0, 3856.2)
for r in (1, 2):
    # grapple
    for aim in ("hip", "ads"):
        zi = "down zoom; wait 0.5; " if aim == "ads" else ""
        zo = "; up zoom" if aim == "ads" else ""
        L.append(f"b9_grapple_{aim}_{r}|rspn101|none|{GR}; {TP(-12321.5, 7400, 294.92)}; wait 0.4; {zi}tap offhand1; wait 0.35; hold attack 0.9; wait 1.2{zo}|secs=6 settle=0.9")
        L.append(f"b9_grbase_{aim}_{r}|rspn101|none|{TP(-12321.5, 7400, 294.92)}; wait 0.4; {zi}wait 0.35; hold attack 0.9; wait 1.2{zo}|secs=6 settle=0.9")
    # mantle (hold fire through it); ADS pressed in the air
    for aim in ("hip", "ads"):
        zi = "down zoom; " if aim == "ads" else ""
        zo = "; up zoom" if aim == "ads" else ""
        for g, w in (("r301", "rspn101"), ("wingman", "wingman")):
            L.append(f"b9_mantle_{g}_{aim}_{r}|{w}|none|{WALL}; {TP(-13878, 6500, 294.92)}; wait 0.3; {MT(4)}; down forward; down speed; wait 0.25; tap jump; wait 0.12; {zi}down attack; wait 2.0; up attack; up speed; up forward; wait 0.6{zo}|secs=6 settle=0.9")
    # kinetic loader: 3 shots then slide or stand
    for st in ("slide", "stand"):
        mv = "down forward; down speed; wait 0.6; down duck; wait 1.4; up duck; up speed; up forward" if st == "slide" else "wait 2.0"
        L.append(f"b9_kinetic_{st}_{r}|energy_shotgun|hopup_kinetic_loader|{ROOF}; wait 0.4; tap attack; wait 1.3; tap attack; wait 1.3; tap attack; wait 0.4; {mv}; wait 1.5|secs=10 stock=30")
    # marksman's tempo
    taps = "; ".join(["tap attack; wait 0.1"] * 80)
    L.append(f"b9_tempo_on_{r}|sentinel|hopup_marksmans_tempo|{ROOF}; wait 0.4; {taps}; wait 0.3|secs=14 stock=60")
print("\n".join(L))
