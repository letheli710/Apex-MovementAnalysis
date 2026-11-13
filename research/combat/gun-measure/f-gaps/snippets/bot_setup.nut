// B4: put the bot {{dist}} u in front of the player on the roof, same realm, R-301 full clip, facing the player; player gets lots of health and a damage log.
entity p = GetPlayerArray()[0]
entity bot = null
foreach ( pl in GetPlayerArray() ) if ( pl.IsBot() ) bot = pl
string o = ""
try {
	p.SetMaxHealth( 100000 ); p.SetHealth( 100000 )
	bot.RemoveFromAllRealms(); bot.AddToOtherEntitysRealms( p )
	bot.SetOrigin( p.GetOrigin() + <{{dist}}, 0, 0> ); bot.SetVelocity( <0, 0, 0> )
	foreach ( w0 in bot.GetMainWeapons() ) bot.TakeWeaponByEntNow( w0 )
	entity w = bot.GiveWeapon( "{{weap}}", WEAPON_INVENTORY_SLOT_PRIMARY_0, [] )
	bot.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "{{weap}}" )
	w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() )
	bot.SetMaxHealth( 100000 ); bot.SetHealth( 100000 )
	bot.BotCmd_Face( p )
	bot.BotCmd_SetMove( 0.0, 0.0, 0 )
	bot.BotCmd_SetFireProfile( {{mode}}, {{interval}}, 0.0 )
	o += "ok team=" + bot.GetTeam() + " w=" + w.GetWeaponClassName() + " clip=" + w.GetWeaponPrimaryClipCount()
} catch ( e ) { o += " err=" + string( e ) }
AgentLink_Reply( o )
