// Item 0b: can a spawned NPC acquire the player and shoot? Spawns %(kind)s %(dist)s u ahead,
// forces SetEnemy( player ) and logs enemy / player health / position-diff speed every 0.25 s.
entity p = GetPlayerArray()[0]
void functionref() sf = void function() : ( p ) {
	string k = "%(kind)s"
	int enemyTeam = p.GetTeam() == TEAM_IMC ? TEAM_MILITIA : TEAM_IMC
	vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
	vector pos = NavMesh_GetClosestPoint( p.GetOrigin() + fwd * %(dist)s )
	vector ang = VectorToAngles( p.GetOrigin() - pos )
	entity n
	if ( k == "prowler" ) { n = CreateProwler( enemyTeam, pos, <0, ang.y, 0> ); SetSpawnOption_AISettings( n, "npc_prowler" ) }
	else { n = CreateNPC( "npc_dummie", enemyTeam, pos, <0, ang.y, 0> ); SetSpawnOption_AISettings( n, k ) }
	DispatchSpawn( n )
	p.SetMaxHealth( 5000 )
	p.SetHealth( 5000 )
	string cv = ""
	foreach ( string c in [ "ai_disabled", "ai_ignoreplayers", "notarget" ] ) { try { cv += c + "=" + GetConVarInt( c ) + " " } catch ( e ) { cv += c + "=? " } }
	printt( "[RT] fight spawned " + k + " hp=" + n.GetHealth() + " " + cv )
	if ( %(ammo)s == 1 ) { entity nw = n.GetActiveWeapon( eActiveInventorySlot.mainHand ); if ( IsValid( nw ) ) { nw.SetWeaponPrimaryClipCount( nw.GetWeaponPrimaryClipCountMax() ); printt( "[RT] fight ammo max=" + nw.GetWeaponPrimaryClipCountMax() ) } }
	try { n.SetEnemy( p ) } catch ( e1 ) { printt( "[RT] fight setenemy_err " + e1 ) }
	vector last = n.GetOrigin()
	float t0 = Time()
	while ( Time() - t0 < %(secs)s && IsValid( n ) ) {
		vector o = n.GetOrigin()
		entity e = n.GetEnemy()
		printt( format( "[RT] fight t=%%.2f o=%%.1f,%%.1f,%%.1f spd=%%.1f dist=%%.0f enemy=%%s php=%%d psh=%%d seen=%%d clip=%%d inv=%%d", Time() - t0, o.x, o.y, o.z, Length2D( o - last ) / 0.25, Distance( o, p.GetOrigin() ),
			IsValid( e ) ? e.GetClassName() : "-", p.GetHealth(), p.GetShieldHealth(), n.CanSee( p ) ? 1 : 0, IsValid( n.GetActiveWeapon( eActiveInventorySlot.mainHand ) ) ? n.GetActiveWeapon( eActiveInventorySlot.mainHand ).GetWeaponPrimaryClipCount() : -1, p.IsInvulnerable() ? 1 : 0 ) )
		last = o
		wait 0.25
	}
	if ( IsValid( n ) ) n.Destroy()
	p.SetHealth( 100 )
	printt( "[RT] fight end" )
}
thread sf()
AgentLink_Reply( "fight" )
