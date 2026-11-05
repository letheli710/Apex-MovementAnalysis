void functionref() rmf = void function() {
	try {
		entity p = GetLocalClientPlayer()
		float t0 = Time()
		int mz = -1
		int lh = -1
		int rh = -1
		array<int> mags = []
		string magn = ""
		float cy = -1.0
		while ( Time() - t0 < SECS ) {
			entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
			entity vm = p.GetViewModelEntity()
			if ( !IsValid( vm ) || !IsValid( w ) ) { WaitFrame(); continue }
			if ( mz < 0 ) {
				mz = vm.LookupAttachment( "muzzle_flash" )
				lh = vm.LookupAttachment( "L_HAND" )
				rh = vm.LookupAttachment( "R_HAND" )
				foreach ( n in ["mag", "MAG", "magazine", "MAGAZINE", "clip", "CLIP", "ammo", "AMMO", "AMMO_COUNTER", "ammo_counter", "shell", "SHELL", "bolt", "BOLT", "charge", "CHARGE", "mag_attach", "MAG_ATTACH", "reload", "ammo_clip", "AMMO_CLIP", "battery", "BATTERY", "FX_MAG", "fx_mag", "shell_eject", "SCREEN", "VDU"] ) {
					int id = vm.LookupAttachment( n )
					if ( id > 0 ) { printt( "[RT] rl attach " + n + " " + id ); if ( magn == "" && n != "shell" && n != "SHELL" && n != "VDU" && n != "SCREEN" && n != "ammo_counter" && n != "AMMO_COUNTER" ) { magn = n; mags.append( id ) } }
				}
			}
			vector c = p.CameraPosition()
			vector a = p.CameraAngles()
			vector f = AnglesToForward( a )
			vector r = AnglesToRight( a )
			vector u = AnglesToUp( a )
			vector d = vm.GetAttachmentOrigin( mz ) - c
			vector g = vm.GetAttachmentAngles( mz )
			vector l = lh > 0 ? vm.GetAttachmentOrigin( lh ) - c : <0, 0, 0>
			vector h = rh > 0 ? vm.GetAttachmentOrigin( rh ) - c : <0, 0, 0>
			vector q = mags.len() > 0 ? vm.GetAttachmentOrigin( mags[0] ) - c : <0, 0, 0>
			string sq = "-"
			try { sq = vm.GetCurrentSequenceName() } catch ( e2 ) { }
			printt( format( "[RT] r t=%.4f clip=%d rel=%d m=%.3f,%.3f,%.3f g=%.3f,%.3f,%.3f l=%.3f,%.3f,%.3f h=%.3f,%.3f,%.3f q=%.3f,%.3f,%.3f ca=%.3f,%.3f,%.3f sq=%s", Time(), w.GetWeaponPrimaryClipCount(), w.IsReloading() ? 1 : 0, DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), g.x, g.y, g.z, DotProduct( l, f ), DotProduct( l, r ), DotProduct( l, u ), DotProduct( h, f ), DotProduct( h, r ), DotProduct( h, u ), DotProduct( q, f ), DotProduct( q, r ), DotProduct( q, u ), a.x, a.y, a.z, sq ) )
			WaitFrame()
		}
		printt( "[RT] r magname=" + magn )
	} catch ( err ) { printt( "[RT] r err " + string( err ) ) }
	printt( "[RT] r end" )
}
thread rmf()
AgentLink_Reply( "g" )
