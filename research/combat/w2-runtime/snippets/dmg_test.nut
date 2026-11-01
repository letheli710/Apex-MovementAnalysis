// Can the player take damage at all (firing range)? Direct TakeDamage from a world attacker.
entity p = GetPlayerArray()[0]
int h0 = p.GetHealth()
int s0 = p.GetShieldHealth()
p.TakeDamage( 20, svGlobal.worldspawn, svGlobal.worldspawn, { damageSourceId = eDamageSourceId.damagedef_unknown } )
AgentLink_Reply( format( "before hp=%d sh=%d after hp=%d sh=%d inv=%d", h0, s0, p.GetHealth(), p.GetShieldHealth(), p.IsInvulnerable() ? 1 : 0 ) )
