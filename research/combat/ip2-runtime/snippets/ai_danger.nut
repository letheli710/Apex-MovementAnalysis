// Item test 5: does a chasing {{kind}} route around thermite? NPC 900 u ahead chases the player; a fire line is planted
// across its path 450 u ahead, thrown sideways, when {{fire}} = 1. Logs lateral offset from the straight path, hp.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	vector fwd = <1, 0, 0>
	vector start = NavMesh_GetClosestPoint( p.GetOrigin() + fwd * 900 )
	entity n
	if ( "{{kind}}" == "prowler" ) { n = CreateProwler( enemyTeam, start, <0, 180, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
	else { n = CreateNPC( "npc_dummie", enemyTeam, start, <0, 180, 0> ); SetSpawnOption_AISettings( n, "npc_dummie_combat" ) }
	n.SetScriptName( "rt_ai" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	AddEntityCallback_OnDamaged( n, void function( entity e, var di ) {
		printt( format( "[RT] dmg t=%.2f amt=%.1f", Time(), DamageInfo_GetDamage( di ) ) )
	} )
	if ( {{fire}} == 1 ) {
		vector c = p.GetOrigin() + fwd * 450
		TraceResults trc = TraceLine( c + <0, 0, 150>, c + <0, 0, -600>, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
		c = trc.endPos
		entity w = p.GetNormalWeapon( WEAPON_INVENTORY_SLOT_ANTI_TITAN )
		if ( IsValid( w ) ) p.TakeWeaponByEntNow( w )
		w = p.GiveWeapon( "mp_weapon_thermite_grenade", WEAPON_INVENTORY_SLOT_ANTI_TITAN )
		WeaponFireGrenadeParams fp
		fp.pos = c + <0, 0, 30>
		fp.vel = AnglesToForward( <80, 90, 0> )
		fp.angVel = <0, 0, 0>
		fp.fuseTime = 0
		fp.scriptTouchDamageType = 0
		fp.scriptExplosionDamageType = 0
		fp.clientPredicted = false
		fp.lagCompensated = false
		fp.useScriptOnDamage = true
		w.FireWeaponGrenade( fp )
		out += " fire c=" + c
	}
	void functionref() lf = void function() : ( p, n, start ) {
		try {
			wait 0.4
			n.SetEnemy( p )
			float t0 = Time()
			while ( Time() - t0 < {{secs}} && IsValid( n ) ) {
				vector o = n.GetOrigin()
				printt( format( "[RT] ai t=%.2f x=%.1f lat=%.1f dplayer=%.0f hp=%d", Time() - t0, o.x - p.GetOrigin().x, o.y - start.y, Distance2D( o, p.GetOrigin() ), n.GetHealth() ) )
				wait 0.2
			}
			if ( IsValid( n ) ) n.Destroy()
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
