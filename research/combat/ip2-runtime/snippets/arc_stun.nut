// Item test 1b: arc star against a chasing {{kind}}: baseline chase 1.5 s, then held at the start with a star planted
// 60 u aside; released when damaged; a second star is stuck on it {{gap}} s after the first blast. Logs position-diff speed.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = p.EyeAngles().y
	vector fwd = AnglesToForward( <0, yaw, 0> )
	vector start = NavMesh_GetClosestPoint( p.GetOrigin() + fwd * 1100 )
	entity n
	if ( "{{kind}}" == "prowler" ) { n = CreateProwler( enemyTeam, start, <0, yaw + 180, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
	else { n = CreateNPC( "npc_dummie", enemyTeam, start, <0, yaw + 180, 0> ); SetSpawnOption_AISettings( n, "npc_dummie_combat" ) }
	n.SetScriptName( "rt_stun" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	n.SetEnemy( p )
	entity w = p.GetNormalWeapon( WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	if ( IsValid( w ) ) p.TakeWeaponByEntNow( w )
	w = p.GiveWeapon( "mp_weapon_grenade_emp", WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	table st = { hit = 0, thit = -1.0 }
	AddEntityCallback_OnDamaged( n, void function( entity e, var di ) : ( st ) {
		printt( format( "[RT] dmg t=%.3f amt=%.2f type=%d", Time(), DamageInfo_GetDamage( di ), DamageInfo_GetCustomDamageType( di ) ) )
		if ( DamageInfo_GetDamage( di ) > 15 ) { st.hit = expect int( st.hit ) + 1; if ( expect float( st.thit ) < 0 ) st.thit = Time() }
	} )
	void functionref( vector ) plant = void function( vector pos ) : ( w ) {
		WeaponFireGrenadeParams fp
		fp.pos = pos
		fp.vel = <0, 0, -1>
		fp.angVel = <0, 0, 0>
		fp.fuseTime = 0
		fp.scriptTouchDamageType = 0
		fp.scriptExplosionDamageType = DF_RAGDOLL | DF_EXPLOSION | DF_ELECTRICAL | DF_STUN_AI
		fp.clientPredicted = false
		fp.lagCompensated = false
		fp.useScriptOnDamage = true
		entity g = w.FireWeaponGrenade( fp )
		if ( IsValid( g ) ) g.SetVelocity( <0, 0, -50> )
		printt( format( "[RT] planted t=%.3f ok=%d", Time(), IsValid( g ) ? 1 : 0 ) )
	}
	void functionref() lf = void function() : ( p, n, start, plant, st ) {
		try {
			float t0 = Time()
			vector prev = n.GetOrigin()
			float tp = t0
			bool planted = false
			bool second = false
			while ( Time() - t0 < {{secs}} && IsValid( n ) ) {
				float t = Time() - t0
				if ( t > 1.5 && !planted ) { planted = true; n.SetOrigin( start ); plant( start + AnglesToForward( <0, 90, 0> ) * 60 + <0, 0, 30> ); prev = start }
				if ( planted && expect int( st.hit ) == 0 ) { n.SetOrigin( start ); prev = start }
				float thit = expect float( st.thit )
				if ( !second && thit > 0 && Time() - thit > {{gap}} && {{gap}} > 0 ) { second = true; plant( n.GetOrigin() + <0, 0, 90> ) }
				vector o = n.GetOrigin()
				float dt = Time() - tp
				float sp = dt > 0 ? Distance2D( o, prev ) / dt : 0.0
				printt( format( "[RT] st t=%.2f sinceHit=%.2f sp=%.1f dplayer=%.0f slow=%.3f turn=%.3f emp=%.3f anim=%d hp=%d", t, thit > 0 ? Time() - thit : -1.0, sp, Distance2D( o, p.GetOrigin() ), StatusEffect_GetSeverity( n, eStatusEffect.move_slow ), StatusEffect_GetSeverity( n, eStatusEffect.turn_slow ), StatusEffect_GetSeverity( n, eStatusEffect.emp ), n.Anim_IsActive() ? 1 : 0, n.GetHealth() ) )
				prev = o
				tp = Time()
				WaitFrame()
			}
			if ( IsValid( n ) ) n.Destroy()
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
	out += "ok mech=" + ( n.IsMechanical() ? 1 : 0 )
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
