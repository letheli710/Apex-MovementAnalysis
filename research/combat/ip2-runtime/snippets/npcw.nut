// Weapon test 13: which weapon NPCs hold and its fields (read only; they do not fire locally).
entity p = GetPlayerArray()[0]
foreach ( ks in [ "npc_dummie_combat", "npc_dummie_shotgun", "npc_dummie_smg", "npc_dummie_lmg" ] ) {
	try {
		vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + <500, 0, 0> )
		entity n = CreateNPC( "npc_dummie", TEAM_IMC == p.GetTeam() ? TEAM_MILITIA : TEAM_IMC, pos, <0, 180, 0> )
		SetSpawnOption_AISettings( n, ks )
		DispatchSpawn( n )
		entity w = n.GetActiveWeapon( eActiveInventorySlot.mainHand )
		if ( IsValid( w ) ) printt( format( "[RT] npcw %s w=%s clip=%d max=%d", ks, w.GetWeaponClassName(), w.GetWeaponPrimaryClipCount(), w.GetWeaponPrimaryClipCountMax() ) )
		else printt( "[RT] npcw " + ks + " no weapon" )
		n.Destroy()
	} catch ( err ) { printt( "[RT] npcw " + ks + " err " + string( err ) ) }
}
AgentLink_Reply( "ok" )
