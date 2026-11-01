// Weapon test 17: can each class be given? One try per class; reports clip size, gravity, speed, mods.
entity p = GetPlayerArray()[0]
string out = ""
foreach ( string wn in [ {{list}} ] ) {
	try {
		foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 )
		entity w = p.GiveWeapon( wn, WEAPON_INVENTORY_SLOT_PRIMARY_0 )
		printt( format( "[RT] load %s ok clip=%d grav=%.2f v=%.0f", wn, w.GetWeaponPrimaryClipCountMax(), w.GetWeaponSettingFloat( eWeaponVar.projectile_gravity_scale ), w.GetWeaponSettingFloat( eWeaponVar.projectile_launch_speed ) ) )
	} catch ( err ) { printt( "[RT] load " + wn + " FAIL " + string( err ) ) }
}
AgentLink_Reply( "done" )
