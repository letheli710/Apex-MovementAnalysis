// Back to the spawn pad, facing {{yaw}}, standing, no NPCs of ours.
entity p = GetPlayerArray()[0]
foreach ( n0 in GetNPCArray() ) if ( n0.GetScriptName().find( "rt_" ) == 0 ) n0.Destroy()
vector o = <-11699.0, 512.0, 1700.0>
TraceResults tr = TraceLine( o, o + <0, 0, -800>, [ p ], TRACE_MASK_SOLID, TRACE_COLLISION_GROUP_NONE )
p.SetOrigin( tr.endPos + <0, 0, 2> )
p.SetVelocity( <0, 0, 0> )
p.SnapEyeAngles( <0, {{yaw}}, 0> )
p.SetMaxHealth( 100 )
p.SetHealth( 100 )
AgentLink_Reply( "at " + p.GetOrigin() )
