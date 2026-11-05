// From the player's eye, the clear flat distance in 24 yaw directions (world only), to choose long shooting lanes.
entity p = GetPlayerArray()[0]
string out = "eye=" + p.EyePosition() + " ang=" + p.EyeAngles() + "\n"
for ( int a = 0; a < 360; a += 15 ) {
	vector d = AnglesToForward( <0, float( a ), 0> )
	TraceResults tr = TraceLine( p.EyePosition(), p.EyePosition() + d * 20000, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
	out += a + ":" + int( tr.fraction * 20000 ) + " "
}
AgentLink_Reply( out )
