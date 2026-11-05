// Weapon tests: give {{weap}} (mods {{mods}}, comma list or none), full mag, optional target wall/NPC, log every shot.
// target: {{target}} = none|body|head|leg with a dummie held {{dist}} u ahead; aim is re-snapped each frame when {{snap}} = 1.
// Logs: clip changes with server time (fire cadence), damage callbacks, heat / charge per frame change,
// projectiles (position + velocity at first sight) when {{track}} = 1.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 )
	array<string> mods = []
	if ( "{{mods}}" != "none" ) foreach ( m in split( "{{mods}}", "," ) ) mods.append( m )
	entity w = p.GiveWeapon( "{{weap}}", WEAPON_INVENTORY_SLOT_PRIMARY_0, mods )
	p.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "{{weap}}" )
	bool hasClip = true
	try { w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() ) } catch ( ec ) { hasClip = false; out += " noclip" }
	try { w.SetWeaponPrimaryAmmoCount( AMMOSOURCE_STOCKPILE, {{stock}} ) } catch ( es ) { out += " stockerr" }
	out += "w=" + w.GetWeaponClassName() + " clip=" + w.GetWeaponPrimaryClipCount() + " mods="
	foreach ( mn in w.GetMods() ) out += mn + ","
	out += " grav=" + w.GetWeaponSettingFloat( eWeaponVar.projectile_gravity_scale ) + " v=" + w.GetWeaponSettingFloat( eWeaponVar.projectile_launch_speed )
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = {{yaw}}
	vector fwd = AnglesToForward( <0, yaw, 0> )
	entity n = null
	vector npos = <0, 0, 0>
	if ( "{{target}}" != "none" ) {
		npos = p.GetOrigin() + fwd * {{dist}}
		npos = <npos.x, npos.y, p.EyePosition().z - 35.0>  // hovers: held by SetOrigin every frame, chest level with the eye, in the clear lane
		n = CreateNPC( "npc_dummie", enemyTeam, npos, <0, yaw + 180, 0> )
		SetSpawnOption_AISettings( n, "npc_dummie_combat" )
		n.SetScriptName( "rt_gun" )
		DispatchSpawn( n )
		n.RemoveFromAllRealms()
		n.AddToOtherEntitysRealms( p )
		n.SetMaxHealth( 9000 )
		n.SetHealth( 9000 )
		n.SetOrigin( npos )
		AddEntityCallback_OnDamaged( n, void function( entity e, var di ) {
			vector dp = DamageInfo_GetDamagePosition( di )
			printt( format( "[RT] dmg t=%.3f amt=%.2f hg=%d src=%d dist=%.1f type=%d pos=%.1f,%.1f,%.1f", Time(), DamageInfo_GetDamage( di ), DamageInfo_GetHitGroup( di ), DamageInfo_GetDamageSourceIdentifier( di ), DamageInfo_GetDistFromAttackOrigin( di ), DamageInfo_GetCustomDamageType( di ), dp.x, dp.y, dp.z ) )
		} )
	}
	void functionref() lf = void function() : ( p, w, n, npos, hasClip ) {
		try {
			float t0 = Time()
			int c0 = -1
			int s0 = -1
			string st0 = ""
			table<int, bool> seen = {}
			while ( Time() - t0 < {{secs}} ) {
				float t = Time() - t0
				if ( IsValid( n ) ) {
					n.SetOrigin( npos )
					if ( {{snap}} == 1 ) {
						vector aimAt = "{{target}}" == "head" ? n.EyePosition() : ( "{{target}}" == "leg" ? n.GetOrigin() + <0, 0, 12> : n.GetOrigin() + <0, 0, 35> )
						p.SnapEyeAngles( VectorToAngles( aimAt + <0, 0, {{lift}}> - p.EyePosition() ) )
					}
				}
				if ( !IsValid( w ) ) break
				if ( !hasClip ) { WaitFrame(); continue }
				int c = w.GetWeaponPrimaryClipCount()
				if ( c != c0 ) {
					entity a = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
					vector ea = p.EyeAngles()
					vector eo = p.EyePosition()
					printt( format( "[RT] clip t=%.3f c=%d ammo=%d reload=%d adsf=%.2f active=%s ea=%.3f,%.3f eo=%.1f,%.1f,%.1f spread=%.3f heat=%.3f charge=%.3f", t, c, w.GetWeaponPrimaryAmmoCount( AMMOSOURCE_STOCKPILE ), w.IsReloading() ? 1 : 0, p.GetZoomFrac(), IsValid( a ) ? a.GetWeaponClassName() : "-", ea.x, ea.y, eo.x, eo.y, eo.z, w.GetAttackSpreadAngle(), {{heat}}, w.GetWeaponChargeFraction() ) )
					c0 = c
				}
				int st = w.GetWeaponPrimaryAmmoCount( AMMOSOURCE_STOCKPILE )
				if ( st != s0 ) { printt( format( "[RT] stock t=%.3f s=%d reload=%d", t, st, w.IsReloading() ? 1 : 0 ) ); s0 = st }
				if ( {{track}} == 1 ) {
					foreach ( e in GetProjectileArrayEx( "any", TEAM_ANY, TEAM_ANY, p.GetOrigin(), 80000 ) ) {
						int id = e.GetEncodedEHandle()
						vector o = e.GetOrigin()
						vector v = e.GetVelocity()
						printt( format( "[RT] proj t=%.3f id=%d o=%.1f,%.1f,%.1f v=%.1f,%.1f,%.1f", t, id, o.x, o.y, o.z, v.x, v.y, v.z ) )
					}
				}
				WaitFrame()
			}
			if ( IsValid( n ) ) { printt( format( "[RT] final hp=%d", n.GetHealth() ) ); n.Destroy() }
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
