// Client: hold the given buttons for %(secs)s s, then release (keys: %(keys)s).
entity p = GetLocalClientPlayer()
array<string> keys = [ %(keys)s ]
void functionref() hf = void function() : ( p, keys ) {
	foreach ( k in keys ) p.ClientCommand( "+" + k )
	wait %(secs)s
	foreach ( k in keys ) p.ClientCommand( "-" + k )
	printt( "[RT] hold end" )
}
thread hf()
AgentLink_Reply( "holding" )
