// Item 2b: real Horizon ultimate (OnWeaponPrimaryAttack_weapon_black_hole, owner = player) vs NPCs.
// Two NPCs (prowler, dummie) spawn on the enemy team %(npcdist)s u ahead; the black hole is thrown
// at pitch %(pitch)s; 1 s later the player is moved %(away)s u back so it is outside the field.
// Logs every 0.1 s: projectile / newt position, each NPC origin, in_black_hole_field, parent, enemy.
entity p = GetPlayerArray()[0]
void functionref() bf = void function() : ( p ) {
	try {
		int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
		float yaw = p.EyeAngles().y
		vector fwd = AnglesToForward( <0, yaw, 0> )
		vector right = AnglesToRight( <0, yaw, 0> )
		vector pstart = p.GetOrigin()
		array<entity> npcs = []
		foreach ( int i, string k in [ "prowler", "npc_dummie_combat" ] ) {
			vector pos = NavMesh_GetClosestPoint( pstart + fwd * %(npcdist)s + right * ( i == 0 ? 120.0 : -120.0 ) )
			entity n
			if ( k == "prowler" ) { n = CreateProwler( enemyTeam, pos, <0, 0, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
			else { n = CreateNPC( "npc_dummie", enemyTeam, pos, <0, 0, 0> ); SetSpawnOption_AISettings( n, k ) }
			DispatchSpawn( n )
			n.SetScriptName( "rt_bh_" + k )
			npcs.append( n )
		}
		try { p.TakeOffhandWeapon( OFFHAND_INVENTORY ) } catch ( e0 ) {}
		p.GiveOffhandWeapon( "mp_ability_horizon_black_hole", OFFHAND_INVENTORY )
		entity w = p.GetOffhandWeapon( OFFHAND_INVENTORY )
		printt( "[RT] bhn weapon " + w )
		WeaponPrimaryAttackParams ap
		ap.pos = p.EyePosition()
		ap.dir = AnglesToForward( <%(pitch)s, yaw, 0> )
		ap.firstTimePredicted = true
		var r = OnWeaponPrimaryAttack_weapon_black_hole( w, ap )
		entity proj = w.w.lastProjectileFired
		printt( "[RT] bhn thrown r=" + r + " proj=" + proj )
		float t0 = Time()
		bool moved = false
		vector projLast = <0, 0, 0>
		while ( Time() - t0 < %(secs)s ) {
			float t = Time() - t0
			if ( !moved && t >= 1.0 ) { p.SetOrigin( pstart - fwd * %(away)s ); moved = true }
			if ( IsValid( proj ) ) projLast = proj.GetOrigin()
			string line = format( "[RT] bhn t=%%.2f proj=%%d pj=%%.1f,%%.1f,%%.1f", t, IsValid( proj ) ? 1 : 0, projLast.x, projLast.y, projLast.z )
			foreach ( n in npcs ) {
				if ( !IsValid( n ) ) { line += " | gone"; continue }
				vector o = n.GetOrigin()
				entity par = n.GetParent()
				entity e = n.GetEnemy()
				line += format( " | %%s o=%%.1f,%%.1f,%%.1f bh=%%.0f par=%%d en=%%s hp=%%d", n.GetScriptName(), o.x, o.y, o.z, StatusEffect_GetSeverity( n, eStatusEffect.in_black_hole_field ), IsValid( par ) ? 1 : 0, IsValid( e ) ? "y" : "-", n.GetHealth() )
			}
			printt( line )
			wait 0.1
		}
		foreach ( n in npcs ) if ( IsValid( n ) ) n.Destroy()
		p.SetOrigin( pstart )
	} catch ( err ) { printt( "[RT] bhn err " + string( err ) ) }
	printt( "[RT] bhn end" )
}
thread bf()
AgentLink_Reply( "bh npc" )
