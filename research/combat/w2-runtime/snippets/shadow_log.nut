// Item 4b: real Revenant ultimate in slot OFFHAND_ULTIMATE = %(ult)s (the client raises and fires it,
// run_sched.py). Logs every server frame for %(secs)s s: IsShadowForm, health / shield, ult clip,
// active weapon, nearby totem props. At t = %(dmg_at)s s the player takes %(dmg)s damage from the world
// (Forged Shadows: does the shadow shell absorb it; Death Totem: lethal hit -> recall?).
entity p = GetPlayerArray()[0]
string out = ""
try {
	entity w0 = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
	if ( !IsValid( w0 ) || w0.GetWeaponClassName() != "%(ult)s" ) {
		try { p.TakeOffhandWeapon( OFFHAND_ULTIMATE ) } catch ( e0 ) {}
		p.GiveOffhandWeapon( "%(ult)s", OFFHAND_ULTIMATE )
	}
	DevAbilities_RefillPlayer( p, true )
	p.SetHealth( 100 )
	p.SnapEyeAngles( <%(pitch)s, p.EyeAngles().y, 0> )
	out += "ult=" + p.GetOffhandWeapon( OFFHAND_ULTIMATE ).GetWeaponClassName()
	void functionref() lf = void function() : ( p ) {
		try {
			float t0 = Time()
			bool hit = false
			vector start = p.GetOrigin()
			while ( Time() - t0 < %(secs)s ) {
				float t = Time() - t0
				if ( !hit && t >= %(dmg_at)s ) {
					hit = true
					printt( format( "[RT] shf damage t=%%.2f hp=%%d sh=%%d sf=%%d", t, p.GetHealth(), p.GetShieldHealth(), p.IsShadowForm() ? 1 : 0 ) )
					p.TakeDamage( %(dmg)s, svGlobal.worldspawn, svGlobal.worldspawn, { damageSourceId = eDamageSourceId.damagedef_unknown } )
					printt( format( "[RT] shf after_damage hp=%%d sh=%%d alive=%%d", p.GetHealth(), p.GetShieldHealth(), IsAlive( p ) ? 1 : 0 ) )
				}
				entity w = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
				entity a = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
				vector o = p.GetOrigin()
				int totems = 0
				foreach ( e in GetEntArrayByClass_Expensive( "prop_script" ) ) if ( Distance( e.GetOrigin(), o ) < 600 && string( e.GetModelName() ).find( "totem" ) >= 0 ) totems++
				printt( format( "[RT] shf t=%%.2f sf=%%d hp=%%d/%%d sh=%%d alive=%%d clip=%%d act=%%s totems=%%d dstart=%%.1f o=%%.1f,%%.1f,%%.1f", t, p.IsShadowForm() ? 1 : 0, p.GetHealth(), p.GetMaxHealth(), p.GetShieldHealth(),
					IsAlive( p ) ? 1 : 0, IsValid( w ) ? w.GetWeaponPrimaryClipCount() : -1, IsValid( a ) ? a.GetWeaponClassName() : "-", totems, Distance( o, start ), o.x, o.y, o.z ) )
				WaitFrame()
			}
		} catch ( err ) { printt( "[RT] shf err " + string( err ) ) }
		printt( "[RT] shf end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
