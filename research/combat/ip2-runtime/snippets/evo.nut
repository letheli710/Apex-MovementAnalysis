// Item test 3: evolving armor. Scripted TakeDamage from the player on a 5000 hp dummie and then a low-hp one.
// Logs armor ref, shield, shield max and progress after every step.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
	foreach ( k in [ "passive_upgrade_core_enabled", "should_ai_reward_evo_pts", "evolving_armor_damage_requirement_tier1", "ai_prowler_evo_pt_percent" ] ) out += " " + k + "=" + GetCurrentPlaylistVarString( k, "<unset>" )
	out += " playlist=" + GetCurrentPlaylistName()
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	float yaw = p.EyeAngles().y
	vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + AnglesToForward( <0, yaw, 0> ) * 500 )
	entity n = CreateNPC( "npc_{{kind}}", enemyTeam, pos, <0, yaw + 180, 0> )
	SetSpawnOption_AISettings( n, "npc_{{kind}}{{ai}}" )
	n.SetScriptName( "rt_evo" )
	DispatchSpawn( n )
	n.RemoveFromAllRealms()
	n.AddToOtherEntitysRealms( p )
	n.SetMaxHealth( 5000 )
	n.SetHealth( 5000 )
	entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
	void functionref( string ) lg = void function( string what ) : ( p ) {
		LootData d = EquipmentSlot_GetEquippedLootDataForSlot( p, "armor" )
		printt( format( "[RT] evo %s ref=%s tier=%d sh=%d max=%d net=%d", what, d.ref, d.tier, p.GetShieldHealth(), p.GetShieldHealthMax(), p.GetPlayerNetInt( NV_EVOLVING_ARMOR_KILL_COUNT ) ) )
	}
	void functionref() lf = void function() : ( p, n, lg, w ) {
		try {
			lg( "before" )
			SURVIVAL_GivePlayerEquipment( p, "armor_pickup_lv1_evolving", 10 )
			wait 0.3
			lg( "equipped_lv1_sh10" )
			foreach ( int dmg in [ 60, 50, 500, 1500 ] ) {
				int hp0 = n.GetHealth()
				n.TakeDamage( float( dmg ), p, p, { weapon = w, damageSourceId = eDamageSourceId.mp_weapon_rspn101 } )
				wait 0.3
				lg( format( "dmg%d_hpLost%d", dmg, hp0 - n.GetHealth() ) )
			}
			SURVIVAL_GivePlayerEquipment( p, "armor_pickup_lv1_evolving", 10 )
			wait 0.3
			lg( "reequip_lv1" )
			n.SetHealth( 20 )
			n.TakeDamage( 90.0, p, p, { weapon = w, damageSourceId = eDamageSourceId.mp_weapon_rspn101 } )
			wait 0.3
			lg( "overkill_hp20_dmg90" )
			if ( IsValid( n ) ) n.Destroy()
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
