// Item 0: can NPCs be spawned, move and fire? Spawns each class 500 u in front of the player
// on the enemy team, then logs position / health / enemy / weapon every 0.25 s for 12 s.
entity p = GetPlayerArray()[0]
string out = ""
int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
out += "pteam=" + p.GetTeam() + " eteam=" + enemyTeam
vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
vector right = AnglesToRight( <0, p.EyeAngles().y, 0> )
array<entity> npcs = []
array<string> kinds = [ "spectre", "prowler", "dummie", "soldier", "stalker" ]
int i = 0
foreach ( string k in kinds ) {
	vector pos = p.GetOrigin() + fwd * 600.0 + right * ( ( i - 2 ) * 150.0 )
	try { pos = NavMesh_GetClosestPoint( pos ) } catch ( en ) { out += " nav_err" }
	vector ang = VectorToAngles( p.GetOrigin() - pos )
	ang = <0, ang.y, 0>
	try {
		entity n
		if ( k == "spectre" ) n = CreateSpectre( enemyTeam, pos, ang )
		else if ( k == "prowler" ) { n = CreateProwler( enemyTeam, pos, ang ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
		else if ( k == "dummie" ) n = CreateDummy( enemyTeam, pos, ang )
		else if ( k == "soldier" ) { n = CreateSoldier( enemyTeam, pos, ang ); SetSpawnOption_AISettings( n, "npc_soldier" ) }
		else if ( k == "stalker" ) n = CreateStalker( enemyTeam, pos, ang )
		DispatchSpawn( n )
		n.SetScriptName( "rt_" + k )
		npcs.append( n )
		entity w = n.GetActiveWeapon( eActiveInventorySlot.mainHand )
		out += format( " | %s ok cls=%s hp=%d alive=%d w=%s", k, n.GetClassName(), n.GetHealth(), IsAlive( n ) ? 1 : 0, IsValid( w ) ? w.GetWeaponClassName() : "none" )
	} catch ( err ) { out += " | " + k + " err=" + string( err ) }
	i++
}
void functionref() lf = void function() : ( npcs, p ) {
	float t0 = Time()
	while ( Time() - t0 < 12.0 ) {
		foreach ( n in npcs ) {
			if ( !IsValid( n ) ) continue
			vector o = n.GetOrigin()
			vector v = n.GetVelocity()
			entity e = n.GetEnemy()
			printt( format( "[RT] npc t=%.2f %s o=%.1f,%.1f,%.1f spd=%.1f hp=%d enemy=%s php=%d psh=%d", Time() - t0, n.GetScriptName(), o.x, o.y, o.z, Length2D( v ), n.GetHealth(), IsValid( e ) ? e.GetClassName() : "-", p.GetHealth(), p.GetShieldHealth() ) )
		}
		wait 0.25
	}
	printt( "[RT] npc end" )
}
thread lf()
AgentLink_Reply( out )
