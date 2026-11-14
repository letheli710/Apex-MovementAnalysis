// B3: natural lifetime of each muzzle-flash particle system, played once on the view model's muzzle_flash attachment (client).
// Prints [RT] fx <name> life=<s> frames=<n>; the effect is the same asset the weapon plays (fx_muzzle_flash_view / _world).
array<asset> fxs = [ $"wpn_muzzleflash_assault_FP", $"wpn_muzzleflash_smg_FP", $"wpn_muzzleflash_lmg_FP", $"wpn_muzzleflash_wingman_FP", $"P_mflash_nrg_shotgun_FP", $"wpn_muzzleflash_snp_hmn_FP", $"wpn_muzzleflash_pistol_FP", $"mflash_shotgun_fp_FULL", $"P_defender_railgun_muzzleflash_FP", $"wpn_muzzleflash_assault_sup_FP", $"wpn_muzzleflash_assault", $"wpn_muzzleflash_smg", $"wpn_muzzleflash_lmg", $"wpn_muzzleflash_pistol", $"wpn_muzzleflash_snp_hmn" ]
array<string> fxn = [ "wpn_muzzleflash_assault_FP", "wpn_muzzleflash_smg_FP", "wpn_muzzleflash_lmg_FP", "wpn_muzzleflash_wingman_FP", "P_mflash_nrg_shotgun_FP", "wpn_muzzleflash_snp_hmn_FP", "wpn_muzzleflash_pistol_FP", "mflash_shotgun_fp_FULL", "P_defender_railgun_muzzleflash_FP", "wpn_muzzleflash_assault_sup_FP", "wpn_muzzleflash_assault", "wpn_muzzleflash_smg", "wpn_muzzleflash_lmg", "wpn_muzzleflash_pistol", "wpn_muzzleflash_snp_hmn" ]
void functionref() fl = void function() : ( fxs, fxn ) {
	entity p = GetLocalClientPlayer()
	for ( int i = 0; i < fxs.len(); i++ ) {
		try {
			entity vm = p.GetViewModelEntity()
			int a = vm.LookupAttachment( "muzzle_flash" )
			int idx = GetParticleSystemIndex( fxs[i] )
			int fx = StartParticleEffectOnEntity( vm, idx, FX_PATTACH_POINT_FOLLOW, a )
			float t0 = Time()
			int n = 0
			while ( EffectDoesExist( fx ) && Time() - t0 < 5.0 ) { WaitFrame(); n++ }
			printt( format( "[RT] fx %s life=%.4f frames=%d", fxn[i], Time() - t0, n ) )
		} catch ( e ) { printt( "[RT] fx " + fxn[i] + " err " + string( e ) ) }
		wait 0.3
	}
	printt( "[RT] fx done" )
}
thread fl()
AgentLink_Reply( "fx" )
