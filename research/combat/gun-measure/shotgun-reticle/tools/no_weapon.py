import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr
r = sr.R5(sys.argv[1])
try:
    r.sv('entity p = GetPlayerArray()[0]; foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 ); p.SnapEyeAngles( <0, 180, 0> ); AgentLink_Reply( "taken" )'); r.pl.sleep(2.0)
    r.state("noweapon"); r.shot("noweapon")
    r.cl('array<string> o = []; foreach ( n in [ "crosshair_hidden", "hud_setting_showCrosshair", "cl_crosshair", "hud_setting_accessibleChat", "hud_setting_crosshairColor", "crosshair_color", "cl_crosshair_color", "hud_setting_reticleColor" ] ) { try { o.append( n + "=" + GetConVarString( n ) ) } catch ( e ) { o.append( n + "=?" ) } } AgentLink_Reply( o.join( " " ) )')
    print(r.cl('array<string> o = []; foreach ( n in [ "crosshair_hidden", "hud_setting_showCrosshair", "cl_crosshair" ] ) { try { o.append( n + "=" + GetConVarString( n ) ) } catch ( e ) { o.append( n + "=?" ) } } AgentLink_Reply( o.join( " " ) )'))
finally:
    r.close()
