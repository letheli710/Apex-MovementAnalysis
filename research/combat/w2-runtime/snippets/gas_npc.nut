// Item 3: Caustic gas vs an NPC dummie and vs the player.
// Dummie: spawned %(dist)s u ahead; a medium gas cloud (CreateGasCloudMediumAtOrigin, owner = player)
// sits on it for the whole run (pin=1: the dummie is put back on its spot every 0.1 s). Schedule: in cloud 0-%(out_at)s s, teleported 900 u away
// until %(back_at)s s, back in cloud until %(secs)s s. Logs hp, move_slow severity, gas fields, every 0.1 s.
// Player: a second player-owned cloud at the player's feet; the player then switches to team 20
// (SetBossPlayer needs a player attacker, so the dummie cannot own it). Team restored at the end.
entity p = GetPlayerArray()[0]
void functionref() gf = void function() : ( p ) {
	try {
	int myTeam = p.GetTeam()
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
	vector right = AnglesToRight( <0, p.EyeAngles().y, 0> )
	vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + fwd * %(dist)s )
	entity n = CreateDummy( enemyTeam, pos, <0, 0, 0> )
	n.SetScriptName( "rt_gas_dummie" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	printt( "[RT] gas dummie hp=" + n.GetHealth() + " at " + pos )
	entity src = CreateScriptMover_NEW( "rt_gas_src", pos, <0, 0, 0> )  // the cloud destroys its source at the end
	CreateGasCloudMediumAtOrigin( src, p, pos, %(secs)s + 2.0 )
	if ( %(player)s == 1 ) {
		p.SetMaxHealth( 5000 )
		p.SetHealth( 5000 )
		entity src2 = CreateScriptMover_NEW( "rt_gas_src2", p.GetOrigin(), <0, 0, 0> )
		CreateGasCloudMediumAtOrigin( src2, p, p.GetOrigin(), %(secs)s + 2.0 )
		SetTeam( p, 20 )  // the cloud keeps the creation team, so the player is now its enemy
	}
	vector away = pos + right * 900.0
	float t0 = Time()
	int phase = 0
	while ( Time() - t0 < %(secs)s && IsValid( n ) ) {
		float t = Time() - t0
		if ( phase == 0 && t >= %(out_at)s ) { n.SetOrigin( away ); phase = 1; printt( "[RT] gas OUT t=" + t ) }
		if ( phase == 1 && t >= %(back_at)s ) { n.SetOrigin( pos ); phase = 2; printt( "[RT] gas BACK t=" + t ) }
		if ( %(pin)s == 1 ) n.SetOrigin( phase == 1 ? away : pos )  // pin: the dummie AI would walk off
		printt( format( "[RT] gas t=%%.2f ph=%%d n_hp=%%d n_slow=%%.3f n_ent=%%.2f n_last=%%.2f n_off=%%.1f p_hp=%%d p_slow=%%.3f p_ent=%%.2f p_last=%%.2f", t, phase,
			n.GetHealth(), StatusEffect_GetSeverity( n, eStatusEffect.move_slow ), n.e.gasEnterTime - t0, n.e.gasLastExpoTime - t0, Distance2D( n.GetOrigin(), phase == 1 ? away : pos ),
			p.GetHealth(), StatusEffect_GetSeverity( p, eStatusEffect.move_slow ), p.e.gasEnterTime - t0, p.e.gasLastExpoTime - t0 ) )
		wait 0.1
	}
	printt( "[RT] gas end" )
	SetTeam( p, myTeam )
	if ( IsValid( n ) ) n.Destroy()
	} catch ( err ) { printt( "[RT] gas err " + string( err ) ); SetTeam( p, 15 ) }
}
thread gf()
AgentLink_Reply( "gas started" )
