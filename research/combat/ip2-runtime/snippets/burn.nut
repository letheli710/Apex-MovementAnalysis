// Item test 2: thermite on the ground; a {{kind}} held far away, moved onto the fire centre between
// {{in0}} and {{in1}} s after ignition (grenade gone). Logs every tick of damage with time since ignition and frame time.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = p.EyeAngles().y
	vector fwd = AnglesToForward( <0, yaw, 0> )
	vector c = p.GetOrigin() + fwd * 600
	TraceResults trc = TraceLine( c + <0, 0, 150>, c + <0, 0, -600>, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
	c = trc.endPos
	vector away = c + fwd * 500
	TraceResults tra = TraceLine( away + <0, 0, 150>, away + <0, 0, -600>, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
	away = tra.endPos
	entity n
	if ( "{{kind}}" == "prowler" ) { n = CreateProwler( enemyTeam, away, <0, yaw, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
	else { n = CreateNPC( "npc_dummie", enemyTeam, away, <0, yaw, 0> ); SetSpawnOption_AISettings( n, "npc_dummie_combat" ) }
	n.SetScriptName( "rt_burn" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	entity w = p.GetNormalWeapon( WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	if ( IsValid( w ) ) p.TakeWeaponByEntNow( w )
	w = p.GiveWeapon( "mp_weapon_thermite_grenade", WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	WeaponFireGrenadeParams fp
	fp.pos = c + <0, 0, 30>
	fp.vel = AnglesToForward( <80, yaw, 0> )
	fp.angVel = <0, 0, 0>
	fp.fuseTime = 0
	fp.scriptTouchDamageType = 0
	fp.scriptExplosionDamageType = 0
	fp.clientPredicted = false
	fp.lagCompensated = false
	fp.useScriptOnDamage = true
	entity g = w.FireWeaponGrenade( fp )
	table st = { tign = -1.0, total = 0.0, ticks = 0 }
	AddEntityCallback_OnDamaged( n, void function( entity e, var di ) : ( st ) {
		float a = DamageInfo_GetDamage( di )
		st.total = expect float( st.total ) + a
		st.ticks = expect int( st.ticks ) + 1
		float ti = expect float( st.tign )
		printt( format( "[RT] dmg sinceIgn=%.3f amt=%.2f total=%.1f n=%d src=%d type=%d hp=%d inflictor=%d", Time() - ti, a, expect float( st.total ), expect int( st.ticks ), DamageInfo_GetDamageSourceIdentifier( di ), DamageInfo_GetCustomDamageType( di ), e.GetHealth(), IsValid( DamageInfo_GetInflictor( di ) ) ? 1 : 0 ) )
	} )
	void functionref() lf = void function() : ( p, g, n, c, away, st ) {
		try {
			float t0 = Time()
			vector last = c
			bool inside = false
			while ( Time() - t0 < {{secs}} && IsValid( n ) ) {
				if ( IsValid( g ) ) last = g.GetOrigin()
				else if ( expect float( st.tign ) < 0 ) { st.tign = Time(); printt( format( "[RT] ignite t=%.3f at=%.1f,%.1f,%.1f ft=%.4f", Time() - t0, last.x, last.y, last.z, FrameTime() ) ) }
				float ti = expect float( st.tign )
				float si = ti > 0 ? Time() - ti : -1.0
				bool want = ti > 0 && si >= {{in0}} && si < {{in1}}
				n.SetOrigin( want ? last : away )
				if ( want != inside ) { inside = want; printt( format( "[RT] inside=%d sinceIgn=%.3f", want ? 1 : 0, si ) ) }
				WaitFrame()
			}
			if ( IsValid( n ) ) { printt( format( "[RT] final hp=%d total=%.1f ticks=%d", n.GetHealth(), expect float( st.total ), expect int( st.ticks ) ) ); n.Destroy() }
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
	out += "ok g=" + IsValid( g ) + " c=" + c
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
