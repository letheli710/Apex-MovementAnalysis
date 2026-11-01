// Item 6: Ash Arc Snare (mp_weapon_arc_bolt) vs a dummie. Spawns a combat dummie %(dist)s u ahead
// (same realm), aims the player at it (pitch %(pitch)s). The client throws (run_sched.py). When the
// dummie first takes damage, its position is the anchor; %(move_at)s s after that the player is moved
// %(far)s u past the dummie so the dummie walks after it. Logs every server frame for %(secs)s s:
// dummie distance to the anchor, health, parent, status effects.
entity p = GetPlayerArray()[0]
string out = ""
try {
	DevAbilities_RefillPlayer( p, true )
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = p.EyeAngles().y
	vector fwd = AnglesToForward( <0, yaw, 0> )
	vector pstart = p.GetOrigin()
	vector pos = NavMesh_GetClosestPoint( pstart + fwd * %(dist)s )
	entity n = CreateNPC( "npc_dummie", enemyTeam, pos, <0, yaw + 180, 0> )
	SetSpawnOption_AISettings( n, "npc_dummie_combat" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	p.SnapEyeAngles( <%(pitch)s, yaw, 0> )
	out += "dummie at " + pos + " tac=" + p.GetOffhandWeapon( OFFHAND_TACTICAL ).GetWeaponClassName()
	void functionref() lf = void function() : ( p, n, pos, pstart, fwd ) {
		try {
			float t0 = Time()
			int sh0 = n.GetShieldHealth()
			printt( "[RT] ash shield0=" + sh0 )
			vector anchor = <0, 0, 0>
			float thit = -1.0
			bool moved = false
			while ( Time() - t0 < %(secs)s && IsValid( n ) ) {
				float t = Time() - t0
				vector o = n.GetOrigin()
				if ( thit < 0 && ( n.GetHealth() < 5000 || n.GetShieldHealth() < sh0 ) ) { thit = t; anchor = o; printt( format( "[RT] ash hit t=%%.2f anchor=%%.1f,%%.1f,%%.1f", t, o.x, o.y, o.z ) ) }
				if ( thit >= 0 && !moved && t >= thit + %(move_at)s ) { p.SetOrigin( pos + fwd * %(far)s ); n.SetEnemy( p ); moved = true; printt( "[RT] ash player moved t=" + t ) }
				printt( format( "[RT] ash t=%%.2f hp=%%d sh=%%d o=%%.1f,%%.1f,%%.1f danchor=%%.1f dstart=%%.1f par=%%d emp=%%.2f slow=%%.2f", t, n.GetHealth(), n.GetShieldHealth(), o.x, o.y, o.z,
					thit >= 0 ? Distance2D( o, anchor ) : -1.0, Distance2D( o, pos ), IsValid( n.GetParent() ) ? 1 : 0,
					StatusEffect_GetSeverity( n, eStatusEffect.emp ), StatusEffect_GetSeverity( n, eStatusEffect.move_slow ) ) )
				if ( int( t * 10 ) %% 5 == 0 ) {
					string tr = "[RT] ash ents"
					foreach ( e in GetProjectileArrayEx( "any", TEAM_ANY, TEAM_ANY, o, 3000 ) ) tr += " proj:" + e.GetClassName() + "@" + Distance( e.GetOrigin(), o )
					foreach ( e in GetEntArrayByClass_Expensive( "prop_physics" ) ) if ( Distance( e.GetOrigin(), o ) < 600 ) tr += " phys@" + Distance2D( e.GetOrigin(), o )
					printt( tr )
				}
				WaitFrame()
			}
			if ( IsValid( n ) ) n.Destroy()
			p.SetOrigin( pstart )
		} catch ( err ) { printt( "[RT] ash err " + string( err ) ) }
		printt( "[RT] ash end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
