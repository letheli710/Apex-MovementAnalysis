// Item test 8: Nessie_SpawnNPC. Runs in a thread so a callback error cannot eat the reply; logs position and hp.
entity p = GetPlayerArray()[0]
void functionref() sf = void function() : ( p ) {
	try {
		vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + <300, 0, 0> )
		printt( "[RT] nessie spawning at " + pos )
		entity n = Nessie_SpawnNPC( p.GetTeam(), p, pos, <0, 0, 0> )
		printt( "[RT] nessie created " + n )
		if ( !n.IsValidInternal() ) return
		float t0 = Time()
		while ( Time() - t0 < {{secs}} && IsValid( n ) ) {
			vector o = n.GetOrigin()
			printt( format( "[RT] nessie t=%.1f o=%.1f,%.1f,%.1f hp=%d team=%d cls=%s ai=%s dplayer=%.0f", Time() - t0, o.x, o.y, o.z, n.GetHealth(), n.GetTeam(), n.GetClassName(), n.GetAISettingsName(), Distance2D( o, p.GetOrigin() ) ) )
			wait 1.0
		}
		if ( IsValid( n ) ) n.Destroy()
	} catch ( err ) { printt( "[RT] nessie err " + string( err ) ) }
	printt( "[RT] end" )
}
thread sf()
AgentLink_Reply( "spawning" )
