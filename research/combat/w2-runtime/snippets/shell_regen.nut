// E-summary item 2: Forged Shadows shell regen. Damages the forged_shadows_shield prop near the player
// by %(dmg)s and logs its health every server frame for %(secs)s s.
entity p = GetPlayerArray()[0]
void functionref() lf = void function() : ( p ) {
	try {
		entity sh = null
		foreach ( e in GetEntArrayByScriptName( "forged_shadows_shield" ) ) if ( Distance( e.GetOrigin(), p.GetOrigin() ) < 150 ) sh = e
		if ( sh == null ) { printt( "[RT] shell none" ); return }
		sh.TakeDamage( %(dmg)s, svGlobal.worldspawn, svGlobal.worldspawn, { damageSourceId = eDamageSourceId.damagedef_unknown } )
		float t0 = Time()
		while ( Time() - t0 < %(secs)s && IsValid( sh ) ) {
			printt( format( "[RT] shell t=%%.3f hp=%%d/%%d tick=%%.4f", Time() - t0, sh.GetHealth(), sh.GetMaxHealth(), FrameTime() ) )
			WaitFrame()
		}
	} catch ( err ) { printt( "[RT] shell err " + string( err ) ) }
	printt( "[RT] shell end" )
}
thread lf()
AgentLink_Reply( "shell" )
