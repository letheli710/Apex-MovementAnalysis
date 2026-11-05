// Weapon test 15: dormant hop-up on P2020: {{mod}} via scripted damage attributed to the weapon. Logs mods after each 100.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 )
	entity w = p.GiveWeapon( "mp_weapon_semipistol", WEAPON_INVENTORY_SLOT_PRIMARY_0, [ "{{mod}}" ] )
	p.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "mp_weapon_semipistol" )
	vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + <300, 0, 0> )
	entity n = CreateNPC( "npc_dummie", p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC, pos, <0, 180, 0> )
	SetSpawnOption_AISettings( n, "npc_dummie_combat" )
	n.SetScriptName( "rt_dorm" )
	DispatchSpawn( n )
	n.SetMaxHealth( 9000 )
	n.SetHealth( 9000 )
	void functionref() lf = void function() : ( p, w, n ) {
		try {
			for ( int i = 1; i <= 8; i++ ) {
				n.TakeDamage( 100.0, p, p, { weapon = w, damageSourceId = eDamageSourceId.mp_weapon_semipistol } )
				wait 0.2
				string m = ""
				foreach ( x in w.GetMods() ) m += x + ","
				printt( format( "[RT] dorm dealt=%d mods=%s", i * 100, m ) )
			}
			n.Destroy()
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
