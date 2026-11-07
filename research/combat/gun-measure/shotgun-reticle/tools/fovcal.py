#!/usr/bin/env python3
"""World pixels per tangent at each cl_fovScale: held hit dots at known angles to the right of the aim (1..8 degrees), one screenshot per scale.
  py -3 -I fovcal.py <out dir> <scale,scale,...>
Dots: ui/projectile_hit_dot at the camera + forward*300 rotated right by the angle (yaw only); then an_fovcal finds the red dots on row y=450."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr  # noqa: E402

CODE = r'''
entity p = GetLocalClientPlayer()
vector c = p.CameraPosition()
vector a = p.CameraAngles()
array<float> angs = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0]
array<var> ruis = []
foreach ( d in angs ) {
	var r = RuiCreate( $"ui/projectile_hit_dot.rpak", clGlobal.topoFullScreen, RUI_DRAW_HUD, 0 )
	RuiSetResolutionToScreenSize( r )
	RuiSetGameTime( r, "startTime", Time() - 0.2 )
	RuiSetFloat3( r, "pos", c + AnglesToForward( <a.x, a.y - d, 0> ) * 300 )
	RuiSetBool( r, "isCrit", false )
	ruis.append( r )
}
void functionref() lf = void function() : ( ruis ) {
	float t0 = Time()
	while ( Time() - t0 < 3.0 ) { foreach ( r in ruis ) if ( RuiIsAlive( r ) ) RuiSetGameTime( r, "startTime", Time() - 0.2 ); WaitFrame() }
}
thread lf()
printt( format( "[RT] cal fov=%.3f", p.GetFOV() ) )
AgentLink_Reply( "cal" )
'''


def main():
    out, scales = sys.argv[1], sys.argv[2].split(",")
    r = sr.R5(out)
    try:
        r.give(sr.GUNS["eva8"], 0)
        for sc in scales:
            r.cl(f'GetLocalClientPlayer().ClientCommand( "cl_fovScale {sc}" ); AgentLink_Reply( "f" )'); r.pl.sleep(0.8)
            r.sv(sr.RESET.replace("{pitch}", "0")); r.pl.sleep(0.3)
            r.cl(CODE); r.pl.sleep(0.3)
            r.shot(f"cal_fs{sc}", crop=0)
            r.pl.sleep(3.0)
        r.cl(f'GetLocalClientPlayer().ClientCommand( "cl_fovScale {scales[0]}" ); AgentLink_Reply( "f" )')
    finally:
        r.close()


if __name__ == "__main__":
    main()
