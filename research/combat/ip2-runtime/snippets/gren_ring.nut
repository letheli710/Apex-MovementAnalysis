// Item test 1: one grenade at the centre of a ring of NPCs held in place at known distances.
// {{weap}} grenade, {{kind}} = dummie|prowler, distances {{ds}} (comma list), fuse {{fuse}} (0 = stick/ignite path).
// Logs each damage callback with the victim's distance to the last grenade position.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	p.SetHealth( 100 )
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = p.EyeAngles().y
	vector fwd = AnglesToForward( <0, yaw, 0> )
	vector c = p.GetOrigin() + fwd * {{cdist}}
	TraceResults trc = TraceLine( c + <0, 0, 150>, c + <0, 0, -600>, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
	c = trc.endPos
	array<string> dl = split( "{{ds}}", "," )
	array<entity> ns = []
	array<vector> ps = []
	table<entity, float> dist = {}
	int i = 0
	foreach ( ds in dl ) {
		float d = ds.tofloat()
		float a = 360.0 * i / dl.len() + 15.0
		vector np = c + AnglesToForward( <0, a, 0> ) * d
		TraceResults tr = TraceLine( np + <0, 0, 150>, np + <0, 0, -600>, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
		np = tr.endPos
		entity n
		if ( "{{kind}}" == "prowler" ) { n = CreateProwler( enemyTeam, np, <0, a, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
		else { n = CreateNPC( "npc_dummie", enemyTeam, np, <0, a, 0> ); SetSpawnOption_AISettings( n, "npc_dummie_combat" ) }
		n.SetScriptName( "rt_ring" )
		DispatchSpawn( n )
		n.RemoveFromAllRealms()
		n.AddToOtherEntitysRealms( p )
		n.SetMaxHealth( 5000 )
		n.SetHealth( 5000 )
		n.SetOrigin( np )
		ns.append( n )
		ps.append( np )
		i++
	}
	out += "c=" + c + " n=" + ns.len() + " mech=" + ( ns[0].IsMechanical() ? 1 : 0 ) + " cls=" + ns[0].GetAISettingsName() + " sh=" + ns[0].GetShieldHealth()
	entity w = p.GetNormalWeapon( WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	if ( IsValid( w ) ) p.TakeWeaponByEntNow( w )
	w = p.GiveWeapon( "{{weap}}", WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	WeaponFireGrenadeParams fp
	fp.pos = c + <0, 0, 30>
	fp.vel = <0, 0, -1>
	fp.angVel = <0, 0, 0>
	fp.fuseTime = {{fuse}}
	fp.scriptTouchDamageType = 0
	fp.scriptExplosionDamageType = {{dtype}}
	fp.clientPredicted = false
	fp.lagCompensated = false
	fp.useScriptOnDamage = true
	entity g = w.FireWeaponGrenade( fp )
	if ( IsValid( g ) ) g.SetVelocity( <0, 0, -50> )
	table st = { last = c }
	foreach ( idx, n in ns ) {
		float d0 = Distance( ps[idx], c )
		AddEntityCallback_OnDamaged( n, void function( entity e, var di ) : ( st, d0 ) {
			vector o = expect vector( st.last )
			printt( format( "[RT] dmg t=%.3f set=%.0f d2d=%.1f d3d=%.1f amt=%.2f src=%d type=%d hp=%d slow=%.3f", Time(), d0, Distance2D( e.GetOrigin(), o ), Distance( e.GetOrigin(), o ), DamageInfo_GetDamage( di ), DamageInfo_GetDamageSourceIdentifier( di ), DamageInfo_GetCustomDamageType( di ), e.GetHealth(), StatusEffect_GetSeverity( e, eStatusEffect.move_slow ) ) )
		} )
	}
	out += " g=" + IsValid( g ) + " tick0=" + Time()
	void functionref() lf = void function() : ( p, g, ns, ps, st ) {
		try {
			float t0 = Time()
			bool ended = false
			while ( Time() - t0 < {{secs}} ) {
				if ( IsValid( g ) ) st.last = g.GetOrigin()
				else if ( !ended ) { ended = true; vector l = expect vector( st.last ); printt( format( "[RT] gren gone t=%.3f last=%.1f,%.1f,%.1f", Time() - t0, l.x, l.y, l.z ) ) }
				foreach ( i, n in ns ) if ( IsValid( n ) ) { n.SetOrigin( ps[i] ) }
				WaitFrame()
			}
			foreach ( n in ns ) if ( IsValid( n ) ) { printt( format( "[RT] final hp=%d", n.GetHealth() ) ); n.Destroy() }
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
