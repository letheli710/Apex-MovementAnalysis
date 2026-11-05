void functionref() gmf = void function() {
	try {
		entity p = GetLocalClientPlayer()
		float t0 = Time()
		while ( Time() - t0 < SECS ) {
			entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
			entity vm = p.GetViewModelEntity()
			vector c = p.CameraPosition()
			vector v = p.GetVelocity()
			float sp = 0.0
			int clip = -1
			bool rel = false
			string wn = "-"
			if ( IsValid( w ) ) { sp = w.GetAttackSpreadAngle(); clip = w.GetWeaponPrimaryClipCount(); rel = w.IsReloading(); wn = w.GetWeaponClassName() }
			vector m = <0, 0, 0>
			if ( IsValid( vm ) ) { int a = vm.LookupAttachment( "ATTACH" ); if ( a > 0 ) { m = vm.GetAttachmentOrigin( a ) } }
			printt( format( "[RT] g t=%.4f zf=%.3f fov=%.2f sp=%.3f clip=%d rel=%d spd=%.1f vz=%.1f gr=%d duck=%d spr=%d wr=%d m=%.2f,%.2f,%.2f c=%.2f,%.2f,%.2f w=%s", Time(), p.GetZoomFrac(), p.GetFOV(), sp, clip, rel ? 1 : 0, Length( <v.x, v.y, 0> ), v.z, p.IsOnGround() ? 1 : 0, p.IsCrouched() ? 1 : 0, p.IsSprinting() ? 1 : 0, p.IsWallRunning() ? 1 : 0, m.x, m.y, m.z, c.x, c.y, c.z, wn ) )
			WaitFrame()
		}
	} catch ( err ) { printt( "[RT] g err " + string( err ) ) }
	printt( "[RT] g end" )
}
thread gmf()
AgentLink_Reply( "g" )
