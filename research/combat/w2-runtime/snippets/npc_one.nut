// Item 0: spawn one NPC of kind %(kind)s, %(dist)s u in front of the player on the enemy team,
// then log position / health / enemy / player health every 0.25 s for %(secs)s s.
// Spawning runs in a thread so a script error in the spawn callbacks cannot eat the reply.
entity p = GetPlayerArray()[0]
void functionref() sf = void function() : ( p ) {
	string k = "%(kind)s"
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
	vector pos = p.GetOrigin() + fwd * %(dist)s
	try { pos = NavMesh_GetClosestPoint( pos ) } catch ( en ) { printt( "[RT] npc nav_err" ) }
	vector ang = VectorToAngles( p.GetOrigin() - pos )
	ang = <0, ang.y, 0>
	entity n
	if ( k == "spectre" ) n = CreateSpectre( enemyTeam, pos, ang )
	else if ( k == "prowler" ) { n = CreateProwler( enemyTeam, pos, ang ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
	else if ( k == "dummie" ) n = CreateDummy( enemyTeam, pos, ang )
	else if ( k == "soldier" ) { n = CreateSoldier( enemyTeam, pos, ang ); SetSpawnOption_AISettings( n, "npc_soldier" ) }
	else if ( k == "stalker" ) n = CreateStalker( enemyTeam, pos, ang )
	else if ( k == "training" ) { n = CreateNPC( "npc_dummie", enemyTeam, pos, ang ); SetSpawnOption_AISettings( n, "npc_training_dummy" ) }
	else { n = CreateNPC( "npc_dummie", enemyTeam, pos, ang ); SetSpawnOption_AISettings( n, k ) }
	n.SetScriptName( "rt_" + k )
	printt( "[RT] npc created " + k + " " + n )
	DispatchSpawn( n )
	entity w = n.GetActiveWeapon( eActiveInventorySlot.mainHand )
	printt( format( "[RT] npc spawned %%s cls=%%s hp=%%d alive=%%d w=%%s team=%%d", k, n.GetClassName(), n.GetHealth(), IsAlive( n ) ? 1 : 0, IsValid( w ) ? w.GetWeaponClassName() : "none", n.GetTeam() ) )
	float t0 = Time()
	while ( Time() - t0 < %(secs)s && IsValid( n ) ) {
		vector o = n.GetOrigin()
		vector v = n.GetVelocity()
		entity e = n.GetEnemy()
		printt( format( "[RT] npc t=%%.2f %%s o=%%.1f,%%.1f,%%.1f spd=%%.1f hp=%%d alive=%%d enemy=%%s php=%%d psh=%%d", Time() - t0, k, o.x, o.y, o.z, Length2D( v ), n.GetHealth(), IsAlive( n ) ? 1 : 0, IsValid( e ) ? e.GetClassName() : "-", p.GetHealth(), p.GetShieldHealth() ) )
		wait 0.25
	}
	printt( "[RT] npc end valid=" + IsValid( n ) )
}
thread sf()
AgentLink_Reply( "spawning" )
