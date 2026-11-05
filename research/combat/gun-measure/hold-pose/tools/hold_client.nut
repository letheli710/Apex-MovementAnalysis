void functionref() hpf = void function() {
	try {
		entity p = GetLocalClientPlayer()
		float t0 = Time()
		string centre = "-"
		int printed = 0
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
			if ( IsValid( w ) ) {
				wn = w.GetWeaponClassName()
				if ( centre == "-" ) { try { centre = w.GetWeaponSettingString( eWeaponVar.viewmodel_ads_centerpoint_attachment ) } catch ( e0 ) { centre = "" } }
			}
			vector d = <0, 0, 0>
			vector s = <0, 0, 0>
			vector ma = <0, 0, 0>
			if ( IsValid( vm ) ) {
				int mz = vm.LookupAttachment( "muzzle_flash" )
				if ( mz > 0 ) { d = vm.GetAttachmentOrigin( mz ) - c; ma = vm.GetAttachmentAngles( mz ) }
				if ( centre != "" && centre != "-" ) { int id = vm.LookupAttachment( centre ); if ( id > 0 ) s = vm.GetAttachmentOrigin( id ) - c }
			}
			bool sl = false
			try { sl = p.IsSliding() } catch ( e1 ) { }
			string sq = "-"
			if ( IsValid( vm ) ) { try { sq = vm.GetCurrentSequenceName() } catch ( e2 ) { } }
			printt( format( "[RT] h t=%.4f spd=%.1f vz=%.1f gr=%d duck=%d spr=%d sl=%d m=%.3f,%.3f,%.3f s=%.3f,%.3f,%.3f ma=%.3f,%.3f,%.3f ca=%.3f,%.3f,%.3f c=%.2f,%.2f,%.2f sq=%s zf=%.3f w=%s", Time(), Length( <v.x, v.y, 0> ), v.z, p.IsOnGround() ? 1 : 0, p.IsCrouched() ? 1 : 0, p.IsSprinting() ? 1 : 0, sl ? 1 : 0, DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), DotProduct( s, f ), DotProduct( s, r ), DotProduct( s, u ), ma.x, ma.y, ma.z, a.x, a.y, a.z, c.x, c.y, c.z, sq, p.GetZoomFrac(), wn ) )
			WaitFrame()
		}
		printt( "[RT] h centre=" + centre )
	} catch ( err ) { printt( "[RT] h err " + string( err ) ) }
	printt( "[RT] h end" )
}
thread hpf()
AgentLink_Reply( "g" )
