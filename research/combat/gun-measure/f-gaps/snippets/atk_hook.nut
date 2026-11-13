// F-GAPS: log every weapon attack with the code's attack origin and direction (run once per VM, server and client).
// [RT] atk t=<Time> w=<class> n=<ammoUsed> o=<origin> dP dY = VectorToAngles( attackDir ) ; eP eY = EyeAngles ; sp = spread ; zf
AddCallback_OnWeaponAttack( void function( entity player, entity weapon, string weaponName, int ammoUsed, vector attackOrigin, vector attackDir ) {
	try {
		vector da = VectorToAngles( attackDir )
		vector ea = player.EyeAngles()
		printt( format( "[RT] atk t=%.4f w=%s n=%d o=%.2f,%.2f,%.2f dP=%.4f dY=%.4f eP=%.4f eY=%.4f sp=%.3f zf=%.3f", Time(), weaponName, ammoUsed, attackOrigin.x, attackOrigin.y, attackOrigin.z, da.x, da.y, ea.x, ea.y, weapon.GetAttackSpreadAngle(), player.GetZoomFrac() ) )
	} catch ( e ) { printt( "[RT] atk err " + string( e ) ) }
} )
AgentLink_Reply( "atk hooked" )
