// Can we fire a real gun? Gives {{weap}}, spawns a dummie {{dist}} u ahead (5000 hp, same realm), aims at it.
// Logs every shot-visible change: clip, npc damage callback (amount, hitgroup, source), for {{secs}} s.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 )
	entity w = p.GiveWeapon( "{{weap}}", WEAPON_INVENTORY_SLOT_PRIMARY_0 )
	p.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "{{weap}}" )
	w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() )
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = p.EyeAngles().y
	vector fwd = AnglesToForward( <0, yaw, 0> )
	vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + fwd * {{dist}} )
	entity n = CreateNPC( "npc_dummie", enemyTeam, pos, <0, yaw + 180, 0> )
	SetSpawnOption_AISettings( n, "npc_dummie_combat" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	n.SetOrigin( pos )
	vector aim = VectorToAngles( ( n.GetOrigin() + <0, 0, 40> ) - p.EyePosition() )
	p.SnapEyeAngles( aim )
	AddEntityCallback_OnDamaged( n, void function( entity e, var di ) {
		printt( format( "[RT] dmg t=%.3f amt=%.2f hg=%d src=%d dist=%.1f type=%d hp=%d", Time(), DamageInfo_GetDamage( di ), DamageInfo_GetHitGroup( di ), DamageInfo_GetDamageSourceIdentifier( di ), DamageInfo_GetDistFromAttackOrigin( di ), DamageInfo_GetCustomDamageType( di ), e.GetHealth() ) )
	} )
	out += "w=" + w.GetWeaponClassName() + " clip=" + w.GetWeaponPrimaryClipCount() + " npc@" + pos + " aim=" + aim
	void functionref() lf = void function() : ( p, w, n ) {
		try {
			float t0 = Time()
			int c0 = -1
			while ( Time() - t0 < {{secs}} ) {
				int c = IsValid( w ) ? w.GetWeaponPrimaryClipCount() : -1
				if ( c != c0 ) { printt( format( "[RT] clip t=%.3f c=%d active=%s", Time() - t0, c, IsValid( p.GetActiveWeapon( eActiveInventorySlot.mainHand ) ) ? p.GetActiveWeapon( eActiveInventorySlot.mainHand ).GetWeaponClassName() : "-" ) ); c0 = c }
				WaitFrame()
			}
			if ( IsValid( n ) ) n.Destroy()
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
