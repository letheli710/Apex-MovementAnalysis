// Item 1b: move_slow on an NPC. A prowler / dummie is spawned %(dist)s u ahead and chases the
// player (SetEnemy). Severity %(sev)s is applied from the spawn (0 = baseline). The player is
// teleported back and forth every 2 s so the NPC keeps running. Speed from position deltas, 0.1 s.
entity p = GetPlayerArray()[0]
void functionref() sf = void function() : ( p ) {
	string k = "%(kind)s"
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
	vector pstart = p.GetOrigin()
	vector pos = NavMesh_GetClosestPoint( pstart + fwd * %(dist)s )
	entity n
	if ( k == "prowler" ) { n = CreateProwler( enemyTeam, pos, <0, 0, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
	else { n = CreateNPC( "npc_dummie", enemyTeam, pos, <0, 0, 0> ); SetSpawnOption_AISettings( n, k ) }
	DispatchSpawn( n )
	float sev = %(sev)s
	if ( sev > 0.0 ) StatusEffect_AddEndless( n, eStatusEffect.move_slow, sev )
	n.SetEnemy( p )
	vector last = n.GetOrigin()
	float t0 = Time()
	int flip = 0
	while ( Time() - t0 < %(secs)s && IsValid( n ) ) {
		float t = Time() - t0
		if ( int( t / 3.0 ) != flip ) { flip = int( t / 3.0 ); p.SetOrigin( flip %% 2 == 1 ? pos + fwd * 700.0 : pstart ) }
		vector o = n.GetOrigin()
		printt( format( "[RT] snpc t=%%.2f k=%%s sev=%%.2f getsev=%%.3f spd=%%.1f dist=%%.0f", t, k, sev, StatusEffect_GetSeverity( n, eStatusEffect.move_slow ), Length2D( o - last ) / 0.1, Distance2D( o, p.GetOrigin() ) ) )
		last = o
		wait 0.1
	}
	if ( IsValid( n ) ) n.Destroy()
	p.SetOrigin( pstart )
	printt( "[RT] snpc end" )
}
thread sf()
AgentLink_Reply( "slow npc" )
