// Weapon test 8: energize. Gives {{weap}}, adds {{item}} x3 to the inventory; the client holds +reload (runner schedule).
// Logs energize state, end time, item count, clip each change, and shot times; {{force}} = 1 forces the state from script.
entity p = GetPlayerArray()[0]
string out = ""
try {
	foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 )
	entity w = p.GiveWeapon( "{{weap}}", WEAPON_INVENTORY_SLOT_PRIMARY_0 )
	p.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "{{weap}}" )
	w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() )
	SURVIVAL_AddToPlayerInventory( p, "{{item}}", 3 )
	out += "isEnergize=" + w.IsEnergizeWeapon() + " have=" + SURVIVAL_CountItemsInInventory( p, "{{item}}" ) + " clip=" + w.GetWeaponPrimaryClipCount()
	if ( {{force}} == 1 ) w.ForceEnergizeState( ENERGIZE_ENERGIZED )
	void functionref() lf = void function() : ( p, w ) {
		try {
			float t0 = Time()
			int s0 = -9
			int i0 = -9
			int c0 = -9
			while ( Time() - t0 < {{secs}} && IsValid( w ) ) {
				int s = w.GetEnergizeState()
				int i = SURVIVAL_CountItemsInInventory( p, "{{item}}" )
				int c = w.GetWeaponPrimaryClipCount()
				if ( s != s0 || i != i0 || c != c0 ) {
					printt( format( "[RT] en t=%.3f state=%d items=%d clip=%d endIn=%.2f frac=%.3f firing=%d", Time() - t0, s, i, c, w.GetEnergizedEndTime() - Time(), w.GetEnergizeFrac(), w.IsWeaponActivelyFiring() ? 1 : 0 ) )
					s0 = s; i0 = i; c0 = c
				}
				WaitFrame()
			}
		} catch ( err ) { printt( "[RT] err " + string( err ) ) }
		printt( "[RT] end" )
	}
	thread lf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
