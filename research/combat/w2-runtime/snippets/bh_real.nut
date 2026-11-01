// Item 2: real Horizon ultimate thrown by the client (tap offhand4, then attack; run_bh.py).
// Server side: gives mp_ability_horizon_black_hole as the ultimate with full charge, aims the
// player at pitch %(pitch)s, spawns %(npcs)s NPCs %(npcdist)s u ahead, then a logger thread waits for
// the throw (weapon.w.lastProjectileFired) and logs every server frame for %(secs)s s:
//   player dist / velocity to the projectile's last position (the landing point = field centre),
//   each NPC's origin, in_black_hole_field, parent.
// mode=npc: player moved %(away)s u back 0.5 s after the throw.  mode=enemy: right after the
// projectile lands the player switches to another team, so the field (team = owner team at
// landing) treats the player as an enemy; restored at the end.  mode=ally: player stays on team.
entity p = GetPlayerArray()[0]
string out = ""
try {
	float yaw = p.EyeAngles().y
	p.SnapEyeAngles( <%(pitch)s, yaw, 0> )
	entity w0 = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
	if ( !IsValid( w0 ) || w0.GetWeaponClassName() != "mp_ability_horizon_black_hole" ) {
		try { p.TakeOffhandWeapon( OFFHAND_ULTIMATE ) } catch ( e0 ) {}
		p.GiveOffhandWeapon( "mp_ability_horizon_black_hole", OFFHAND_ULTIMATE )
	}
	DevAbilities_RefillPlayer( p, true )
	entity w = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
	w.w.lastProjectileFired = null
	out += "w=" + w + " clip=" + w.GetWeaponPrimaryClipCount() + " team=" + p.GetTeam()
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	vector fwd = AnglesToForward( <0, yaw, 0> )
	vector right = AnglesToRight( <0, yaw, 0> )
	vector pstart = p.GetOrigin()
	array<entity> npcs = []
	for ( int i = 0; i < %(npcs)s; i++ ) {
		vector pos = NavMesh_GetClosestPoint( pstart + fwd * %(npcdist)s + right * ( i %% 2 == 0 ? 150.0 : -150.0 ) )
		entity n
		if ( i %% 2 == 0 ) { n = CreateProwler( enemyTeam, pos, <0, 180, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
		else { n = CreateNPC( "npc_dummie", enemyTeam, pos, <0, 180, 0> ); SetSpawnOption_AISettings( n, "npc_dummie_combat" ) }
		DispatchSpawn( n )
		n.RemoveFromAllRealms()
		n.AddToOtherEntitysRealms( p )
		n.SetScriptName( "rt_bh_" + i )
		npcs.append( n )
	}
	int myTeam = p.GetTeam()
	void functionref() lf = void function() : ( p, w, npcs, pstart, fwd, myTeam ) {
		try {
			float tw = Time()
			while ( !IsValid( w.w.lastProjectileFired ) && Time() - tw < 10.0 ) WaitFrame()
			entity proj = w.w.lastProjectileFired
			printt( "[RT] bhr thrown proj=" + proj + " wait=" + ( Time() - tw ) )
			float t0 = Time()
			vector c = IsValid( proj ) ? proj.GetOrigin() : <0, 0, 0>
			bool moved = false
			bool switched = false
			float tland = -1.0
			while ( Time() - t0 < %(secs)s ) {
				float t = Time() - t0
				if ( IsValid( proj ) ) c = proj.GetOrigin()
				else if ( tland < 0 ) { tland = t; printt( "[RT] bhr landed t=" + t ) }
				if ( "%(mode)s" == "npc" && !moved && t >= 0.5 ) { p.SetOrigin( pstart + fwd * %(away)s ); moved = true }
				if ( "%(mode)s" == "enemy" && !switched && tland >= 0 ) { SetTeam( p, myTeam == TEAM_IMC ? 20 : TEAM_IMC ); switched = true; printt( "[RT] bhr team -> " + p.GetTeam() ) }
				vector o = p.GetOrigin()
				vector v = p.GetVelocity()
				vector d = c - o
				vector n2 = Normalize( <d.x, d.y, 0> )
				string line = format( "[RT] bhr t=%%.4f land=%%d c=%%.1f,%%.1f,%%.1f P d=%%.2f d2=%%.2f spd2=%%.2f vin2=%%.2f vz=%%.2f gnd=%%d bh=%%.0f", t, tland >= 0 ? 1 : 0, c.x, c.y, c.z,
					Length( d ), Length2D( d ), Length2D( v ), DotProduct( <v.x, v.y, 0>, n2 ), v.z, p.IsOnGround() ? 1 : 0, StatusEffect_GetSeverity( p, eStatusEffect.in_black_hole_field ) )
				foreach ( n in npcs ) {
					if ( !IsValid( n ) ) { line += " | gone"; continue }
					vector no = n.GetOrigin()
					line += format( " | %%s d2=%%.1f dz=%%.1f bh=%%.0f par=%%d hp=%%d", n.GetScriptName(), Length2D( no - c ), no.z - c.z, StatusEffect_GetSeverity( n, eStatusEffect.in_black_hole_field ), IsValid( n.GetParent() ) ? 1 : 0, n.GetHealth() )
				}
				printt( line )
				if ( int( t * 10 ) %% 10 == 0 ) {
					string dg = format( "[RT] bhr diag t=%%.1f", t )
					foreach ( tr in GetEntArrayByClass_Expensive( "trigger_cylinder_heavy" ) ) {
						if ( Distance2D( tr.GetOrigin(), c ) > 200.0 ) continue
						dg += format( " trig team=%%d touchP=%%d", tr.GetTeam(), tr.IsTouching( p ) ? 1 : 0 )
						foreach ( n in npcs ) if ( IsValid( n ) ) dg += format( " touch%%s=%%d share=%%d", n.GetScriptName(), tr.IsTouching( n ) ? 1 : 0, n.DoesShareRealms( tr ) ? 1 : 0 )
					}
					printt( dg )
				}
				WaitFrame()
			}
		} catch ( err ) { printt( "[RT] bhr err " + string( err ) ) }
		if ( p.GetTeam() != myTeam ) SetTeam( p, myTeam )
		foreach ( n in npcs ) if ( IsValid( n ) ) n.Destroy()
		printt( "[RT] bhr end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
