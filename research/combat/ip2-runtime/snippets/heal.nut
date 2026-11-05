// Item test 4: consumable channel. Drops health/shield, adds the item, calls Consumable_UseItemByType-style trigger.
// Logs state changes each server frame: isHealing, active weapon, charge fraction, health, shield, item count, speed.
// {{hit}} = time after start to apply scripted world damage (<0 none). {{item}} = eConsumableType member.
// Client holds movement keys via the runner schedule when testing speed.
entity p = GetPlayerArray()[0]
string out = ""
try {
	p.SetMaxHealth( 100 )
	p.SetHealth( 40 )
	SURVIVAL_GivePlayerEquipment( p, "armor_pickup_lv3", 0 )
	p.SetShieldHealth( 0 )
	string ref = "{{ref}}"
	int have0 = SURVIVAL_CountItemsInInventory( p, ref )
	SURVIVAL_AddToPlayerInventory( p, ref, 3 )
	out += "have0=" + have0 + " have=" + SURVIVAL_CountItemsInInventory( p, ref )
	void functionref() lf = void function() : ( p, ref ) {
		try {
			float t0 = Time()
			int h0 = -1
			int s0 = -1
			int c0 = -1
			string a0 = ""
			bool hb0 = false
			bool hit = false
			vector prev = p.GetOrigin()
			float tp = Time()
			while ( Time() - t0 < {{secs}} ) {
				float t = Time() - t0
				if ( {{hit}} >= 0 && !hit && t >= {{hit}} ) { hit = true; p.TakeDamage( 5.0, svGlobal.worldspawn, svGlobal.worldspawn, { damageSourceId = eDamageSourceId.damagedef_unknown } ); printt( format( "[RT] heal t=%.2f scripted_damage hp=%d", t, p.GetHealth() ) ) }
				entity a = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
				string an = IsValid( a ) ? a.GetWeaponClassName() : "-"
				int c = SURVIVAL_CountItemsInInventory( p, ref )
				bool hb = p.GetPlayerNetBool( "isHealing" )
				float dt = Time() - tp
				float sp = dt > 0 ? Distance2D( p.GetOrigin(), prev ) / dt : 0.0
				float chg = IsValid( a ) && an == "mp_ability_consumable" ? a.GetWeaponChargeFraction() : -1.0
				if ( p.GetHealth() != h0 || p.GetShieldHealth() != s0 || c != c0 || an != a0 || hb != hb0 || int( t * 2 ) != int( ( t - dt ) * 2 ) ) {
					printt( format( "[RT] heal t=%.2f hp=%d sh=%d items=%d active=%s isHealing=%d charge=%.3f sp=%.1f sprint=%d slow=%.3f turbo=%.3f", t, p.GetHealth(), p.GetShieldHealth(), c, an, hb ? 1 : 0, chg, sp, p.IsSprinting() ? 1 : 0, StatusEffect_GetSeverity( p, eStatusEffect.move_slow ), StatusEffect_GetSeverity( p, eStatusEffect.speed_boost ) ) )
					h0 = p.GetHealth(); s0 = p.GetShieldHealth(); c0 = c; a0 = an; hb0 = hb
				}
				prev = p.GetOrigin()
				tp = Time()
				WaitFrame()
			}
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
