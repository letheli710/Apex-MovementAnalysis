void functionref() acf = void function() {
	try {
		entity p = GetLocalClientPlayer()
		float t0 = Time()
		while ( Time() - t0 < SECS ) {
			entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
			entity vm = p.GetViewModelEntity()
			vector c = p.CameraPosition()
			vector a = p.CameraAngles()
			vector v = p.GetVelocity()
			vector f = AnglesToForward( a )
			vector r = AnglesToRight( a )
			vector u = AnglesToUp( a )
			string wn = "-"
			int clip = -1
			bool rel = false
			if ( IsValid( w ) ) { wn = w.GetWeaponClassName(); clip = w.GetWeaponPrimaryClipCount(); rel = w.IsReloading() }
			vector d = <0, 0, 0>
			vector ma = <0, 0, 0>
			string sq = "-"
			if ( IsValid( vm ) ) {
				int mz = vm.LookupAttachment( "muzzle_flash" )
				if ( mz > 0 ) { d = vm.GetAttachmentOrigin( mz ) - c; ma = vm.GetAttachmentAngles( mz ) }
				try { sq = vm.GetCurrentSequenceName() } catch ( e2 ) { }
			}
			bool sl = false
			bool zp = false
			bool ga = false
			try { sl = p.IsSliding() } catch ( e1 ) { }
			try { zp = p.IsZiplining() } catch ( e3 ) { }
			try { ga = p.IsGrappleActive() } catch ( e4 ) { }
			printt( format( "[RT] a t=%.4f spd=%.1f vz=%.1f gr=%d duck=%d spr=%d sl=%d zp=%d ga=%d rel=%d clip=%d m=%.3f,%.3f,%.3f ma=%.3f,%.3f,%.3f ca=%.3f,%.3f,%.3f sq=%s zf=%.3f w=%s", Time(), Length( <v.x, v.y, 0> ), v.z, p.IsOnGround() ? 1 : 0, p.IsCrouched() ? 1 : 0, p.IsSprinting() ? 1 : 0, sl ? 1 : 0, zp ? 1 : 0, ga ? 1 : 0, rel ? 1 : 0, clip, DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), ma.x, ma.y, ma.z, a.x, a.y, a.z, sq, p.GetZoomFrac(), wn ) )
			WaitFrame()
		}
	} catch ( err ) { printt( "[RT] a err " + string( err ) ) }
	printt( "[RT] a end" )
}
thread acf()
AgentLink_Reply( "g" )
