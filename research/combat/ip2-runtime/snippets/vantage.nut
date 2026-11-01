// Weapon test 19: Vantage ult sniper as an offhand. Hovering dummie {{dist}} u down the clear lane, aim re-snapped with lift {{lift}}.
// The client raises it with +offhand4 and fires with +attack (schedule). Logs damage and offhand clip.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	entity old = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
	if ( IsValid( old ) ) p.TakeOffhandWeapon( OFFHAND_ULTIMATE )
	p.GiveOffhandWeapon( "mp_ability_sniper_ult", OFFHAND_ULTIMATE )
	entity w = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
	w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() )
	out += "clipmax=" + w.GetWeaponPrimaryClipCountMax() + " grav=" + w.GetWeaponSettingFloat( eWeaponVar.projectile_gravity_scale ) + " v=" + w.GetWeaponSettingFloat( eWeaponVar.projectile_launch_speed )
	vector npos = p.GetOrigin() + <{{dist}}, 0, 0>
	npos = <npos.x, npos.y, p.EyePosition().z - 35.0>
	entity n = CreateNPC( "npc_dummie", p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC, npos, <0, 180, 0> )
	SetSpawnOption_AISettings( n, "npc_dummie_combat" )
	n.SetScriptName( "rt_van" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 9000 )
	n.SetHealth( 9000 )
	AddEntityCallback_OnDamaged( n, void function( entity e, var di ) {
		vector dp = DamageInfo_GetDamagePosition( di )
		printt( format( "[RT] dmg t=%.3f amt=%.2f hg=%d dist=%.1f pos=%.1f,%.1f,%.1f", Time(), DamageInfo_GetDamage( di ), DamageInfo_GetHitGroup( di ), DamageInfo_GetDistFromAttackOrigin( di ), dp.x, dp.y, dp.z ) )
	} )
	void functionref() lf = void function() : ( p, w, n, npos ) {
		try {
			float t0 = Time()
			int c0 = -1
			while ( Time() - t0 < {{secs}} && IsValid( n ) ) {
				n.SetOrigin( npos )
				p.SnapEyeAngles( VectorToAngles( npos + <0, 0, 35 + {{lift}}> - p.EyePosition() ) )
				int c = IsValid( w ) ? w.GetWeaponPrimaryClipCount() : -1
				if ( c != c0 ) { printt( format( "[RT] van t=%.3f c=%d", Time() - t0, c ) ); c0 = c }
				WaitFrame()
			}
			if ( IsValid( n ) ) n.Destroy()
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
