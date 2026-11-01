// Item 5: D.O.C. drone path. Logs every server frame for %(secs)s s: the follow_medic drone
// (FOLLOW_MEDIC_SCRIPT_NAME) origin / angles and the player's origin, eye yaw, velocity, crouch.
// The drone is deployed by the client (tap offhand1, run_sched.py) after this logger starts.
entity p = GetPlayerArray()[0]
DevAbilities_RefillPlayer( p, true )
void functionref() lf = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < %(secs)s ) {
			array<entity> ds = GetEntArrayByScriptName( "follow_medic" )
			vector o = p.GetOrigin()
			vector v = p.GetVelocity()
			string line = format( "[RT] doc t=%%.4f P o=%%.2f,%%.2f,%%.2f yaw=%%.2f v=%%.2f,%%.2f,%%.2f duck=%%d slide=%%d spr=%%d n=%%d", Time() - t0, o.x, o.y, o.z, p.EyeAngles().y, v.x, v.y, v.z,
				p.IsCrouched() ? 1 : 0, p.IsSliding() ? 1 : 0, p.IsSprinting() ? 1 : 0, ds.len() )
			if ( ds.len() > 0 ) {
				entity d = ds[0]
				vector dO = d.GetOrigin()
				vector dA = d.GetAngles()
				line += format( " D o=%%.2f,%%.2f,%%.2f a=%%.2f,%%.2f,%%.2f", dO.x, dO.y, dO.z, dA.x, dA.y, dA.z )
			}
			printt( line )
			WaitFrame()
		}
	} catch ( err ) { printt( "[RT] doc err " + string( err ) ) }
	printt( "[RT] doc end" )
}
thread lf()
AgentLink_Reply( "doc logger" )
