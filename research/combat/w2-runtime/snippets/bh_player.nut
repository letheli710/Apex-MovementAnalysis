// Item 2a: black hole pull on the player. Builds the same TT_BLACKHOLE trigger as
// BLACKHOLE_PullTriggerThread (mp_ability_horizon_black_hole.nut:647-708) on team %(team)s
// (enemy / ally), %(dist)s u in front of the player, strong pull %(strong)s s, then %(hold)s s normal.
// The client holds the input given to hold.nut at the same time. Logs every server frame.
// The file constants are local to the weapon script, so their values are inlined (nut:69-91).
entity p = GetPlayerArray()[0]
void functionref() bf = void function() : ( p ) {
	entity trigger
	try {
		int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
		vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
		vector c = p.GetOrigin() + fwd * %(dist)s
		trigger = CreateEntity( "trigger_cylinder_heavy" )
		trigger.SetTriggerType( TT_BLACKHOLE )
		trigger.SetBlackholeIsStrongPulling( true )
		trigger.SetBlackholeParams( 200, GetCurrentPlaylistVarFloat( "blackhole_pull_outer_speed", 300.0 ), GetCurrentPlaylistVarFloat( "blackhole_pull_inner_speed", 400.0 ),
			GetCurrentPlaylistVarFloat( "blackhole_move_outer_speed", 85.0 ), GetCurrentPlaylistVarFloat( "blackhole_move_inner_speed", 135.0 ), 100 )
		trigger.SetCylinderRadius( 400 )
		trigger.SetAboveHeight( 200 )
		trigger.SetBelowHeight( 200 )
		trigger.SetOrigin( c )
		DispatchSpawn( trigger )
		trigger.Enable()
		trigger.RemoveFromAllRealms()
		trigger.AddToOtherEntitysRealms( p )
		trigger.Code_SetTeam( "%(team)s" == "ally" ? p.GetTeam() : enemyTeam )
		trigger.SearchForNewTouchingEntity()
		printt( format( "[RT] bh setup c=%%.1f,%%.1f,%%.1f team=%%d pteam=%%d pl_outer=%%.0f", c.x, c.y, c.z, trigger.GetTeam(), p.GetTeam(), GetCurrentPlaylistVarFloat( "blackhole_pull_outer_speed", -1 ) ) )
		float t0 = Time()
		bool strong = true
		while ( Time() - t0 < %(strong)s + %(hold)s ) {
			float t = Time() - t0
			if ( strong && t >= %(strong)s ) { trigger.SetBlackholeIsStrongPulling( false ); strong = false; printt( "[RT] bh strong_off t=" + t ) }
			vector o = p.GetOrigin()
			vector v = p.GetVelocity()
			vector d = c - o
			float dist = Length( d )
			vector n = d / max( dist, 0.01 )
			printt( format( "[RT] bh t=%%.4f dist=%%.2f dist2d=%%.2f spd=%%.2f spd2d=%%.2f vin=%%.2f vz=%%.2f gnd=%%d st=%%d touch=%%d", t, dist, Length2D( d ), Length( v ), Length2D( v ), DotProduct( v, n ), v.z, p.IsOnGround() ? 1 : 0, strong ? 1 : 0, trigger.IsTouching( p ) ? 1 : 0 ) )
			WaitFrame()
		}
	} catch ( err ) { printt( "[RT] bh err " + string( err ) ) }
	if ( IsValid( trigger ) ) trigger.Destroy()
	printt( "[RT] bh end" )
}
thread bf()
AgentLink_Reply( "bh player" )
