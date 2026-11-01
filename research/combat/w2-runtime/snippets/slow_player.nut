// Item 1: move_slow severity -> player speed. The client holds sprint + forward (slow_hold.nut);
// every phase resets the player to the start, applies one severity (Endless) and logs the
// server horizontal speed each frame for %(phase)s s. Phase list: %(sevs)s
entity p = GetPlayerArray()[0]
vector start = p.GetOrigin()
vector ang = <0, p.EyeAngles().y, 0>
array<float> sevs = [ %(sevs)s ]
void functionref() sf = void function() : ( p, start, ang, sevs ) {
	foreach ( int k, float s in sevs ) {
		p.SetOrigin( start )
		p.SetVelocity( <0, 0, 0> )
		int h = -1
		if ( s > 0.0 ) h = StatusEffect_AddEndless( p, eStatusEffect.move_slow, s )
		float t0 = Time()
		while ( Time() - t0 < %(phase)s ) {
			vector v = p.GetVelocity()
			printt( format( "[RT] slow k=%%d sev=%%.2f t=%%.3f spd=%%.2f getsev=%%.3f sprint=%%d gnd=%%d", k, s, Time() - t0, Length2D( v ), StatusEffect_GetSeverity( p, eStatusEffect.move_slow ), p.IsSprinting() ? 1 : 0, p.IsOnGround() ? 1 : 0 ) )
			WaitFrame()
		}
		if ( h != -1 ) StatusEffect_Stop( p, h )
	}
	printt( "[RT] slow end" )
}
thread sf()
AgentLink_Reply( "start=" + start + " sevs=" + sevs.len() )
