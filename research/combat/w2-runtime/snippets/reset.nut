// Put the player back on the firing-range spawn pad, facing +x, full health.
entity p = GetPlayerArray()[0]
p.SetOrigin( <%(x)s, %(y)s, %(z)s> )
p.SetVelocity( <0, 0, 0> )
p.SnapEyeAngles( <0, %(yaw)s, 0> )
p.SetMaxHealth( 100 )
p.SetHealth( 100 )
AgentLink_Reply( "at " + p.GetOrigin() + " gnd=" + p.IsOnGround() )
