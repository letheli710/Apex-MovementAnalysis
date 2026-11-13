// B4: log every damage to the local player (run once on the server).
entity p = GetPlayerArray()[0]
AddEntityCallback_OnDamaged( p, void function( entity e, var di ) {
	try {
		entity a = DamageInfo_GetAttacker( di )
		printt( format( "[RT] pdmg t=%.4f amt=%.2f src=%d type=%d att=%s hp=%d", Time(), DamageInfo_GetDamage( di ), DamageInfo_GetDamageSourceIdentifier( di ), DamageInfo_GetCustomDamageType( di ), IsValid( a ) ? a.GetPlayerName() : "-", e.GetHealth() ) )
	} catch ( x ) { printt( "[RT] pdmg err " + string( x ) ) }
} )
AgentLink_Reply( "dmg hooked" )
