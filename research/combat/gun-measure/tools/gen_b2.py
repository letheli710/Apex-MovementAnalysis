#!/usr/bin/env python3
"""Cases for B, the states that need geometry or abilities. py -3 -I gen_b2.py > cases_b2.txt"""
TP = lambda x, y, z, yaw=0: f"sv try {{ entity p = GetPlayerArray()[0] ~ p.SetOrigin( <{x}, {y}, {z}> ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SetAngles( <0, {yaw}, 0> ) ~ p.SnapEyeAngles( <0, {yaw}, 0> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( \"tp\" )"
WALL = 'sv try { foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo" ) ) e.Destroy() ~ asset m = $"mdl/rocks/rock_white_chalk_modular_wallrun_02.rmdl" ~ MapEdit_PrecacheModel( m ) ~ entity pr = CreatePropDynamic( m, <-13600, 6500, 294.92>, <0, 0, 0>, SOLID_VPHYSICS, 20000 ) ~ pr.AllowMantle() ~ pr.SetScriptName( "hsd_test_geo" ) ~ AgentLink_Reply( "wall" ) } catch ( e ) { AgentLink_Reply( "wall err " + string( e ) ) }'
ZIP = 'sv try { foreach ( entity e in GetEntArrayByScriptName( "hsd_zip" ) ) e.Destroy() ~ array<entity> all ~ all.extend( CreateZipline( <-14600, 6800, 394.92>, <-13000, 6800, 394.92>, false, 100 ) ) ~ foreach ( entity e in all ) e.SetScriptName( "hsd_zip" ) ~ AgentLink_Reply( "zip " + all.len() ) } catch ( e ) { AgentLink_Reply( "zip err " + string( e ) ) }'
ZIPOFF = 'sv try { entity p = GetPlayerArray()[0] ~ if ( p.IsZiplining() ) p.Zipline_Stop() } catch ( e ) { } ~ AgentLink_Reply( "zo" )'
GR = 'sv try { entity p = GetPlayerArray()[0] ~ p.TakeOffhandWeapon( OFFHAND_TACTICAL ) } catch ( e ) { } ~ try { GetPlayerArray()[0].GiveOffhandWeapon( "@@", OFFHAND_TACTICAL, [] ) } catch ( e2 ) { printt( "[RT] ab err " + string( e2 ) ) } ~ AgentLink_Reply( "ab" )'
HP = lambda h: f'sv try {{ GetPlayerArray()[0].SetHealth( {h} ) }} catch ( e ) {{ }} ~ AgentLink_Reply( "hp" )'
VEL = lambda x, z: f'sv try {{ GetPlayerArray()[0].SetVelocity( <{x}, 0, {z}> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( "v" )'
PAD = TP(-11699, 512, 1577.05)
L = []
for g, w, f in (("r301", "rspn101", "hold attack 0.9"), ("wingman", "wingman", "tap attack; wait 0.45; tap attack; wait 0.45; tap attack; wait 0.1")):
    for aim in ("hip", "ads"):
        zi = "down zoom; wait 0.45; " if aim == "ads" else ""
        zo = "; up zoom" if aim == "ads" else ""
        k = "secs=9 settle=0.9"
        L.append(f"s2_{g}_mantle_{aim}|{w}|none|{WALL}; {TP(-13878, 6500, 294.92)}; wait 0.3; {zi}down forward; down speed; wait 0.25; tap jump; wait 0.3; {f}; wait 1; up speed; up forward{zo}; wait 0.5; {PAD}|{k}")
        L.append(f"s2_{g}_wallrun_{aim}|{w}|none|{WALL}; {TP(-13950, 6330, 294.92, 25)}; wait 0.3; {zi}down forward; down speed; wait 0.7; tap jump; wait 0.25; {f}; wait 1; up speed; up forward{zo}; wait 0.5; {PAD}|{k}")
        L.append(f"s2_{g}_zipline_{aim}|{w}|none|{ZIP}; {TP(-14500, 6800, 294.92)}; wait 0.3; tap use; wait 0.4; {zi}{f}; wait 0.8{zo}; {ZIPOFF}; wait 0.3; {PAD}|{k}")
        L.append(f"s2_{g}_grapple_{aim}|{w}|none|{GR.replace('@@', 'mp_ability_grapple')}; {WALL}; {TP(-14000, 6650, 294.92, 36.87)}; wait 0.5; tap offhand1; wait 0.45; {zi}{f}; wait 0.8{zo}; wait 1; {PAD}|{k}")
        L.append(f"s2_{g}_stim_{aim}|{w}|none|{GR.replace('@@', 'mp_ability_octane_stim')}; {PAD}; wait 0.5; tap offhand1; wait 0.5; down forward; {zi}{f}; wait 0.5{zo}; up forward; wait 0.3; {PAD}|{k}")
        L.append(f"s2_{g}_launch_{aim}|{w}|none|{PAD}; wait 0.3; {zi}{VEL(600, 1100)}; wait 0.1; {f}; wait 0.5{zo}; wait 1.5; {PAD}|{k}")
        L.append(f"s2_{g}_lowhp_{aim}|{w}|none|{PAD}; {HP(10)}; wait 0.3; {zi}{f}; wait 0.5{zo}; {HP(100)}|secs=6 settle=0.9")
print("\n".join(L))
