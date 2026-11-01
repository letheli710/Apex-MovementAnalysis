// Item 4: does the S3 dedi have the shadow-form natives? Each call in its own try; IsShadowForm is
// read after each. %(mode)s: plain = EnterShadowForm, fortified = EnterShadowFormFortified.
entity p = GetPlayerArray()[0]
string out = ""
try { out += "before=" + p.IsShadowForm() } catch ( e0 ) { out += "IsShadowForm_err=" + string( e0 ) }
if ( "%(mode)s" == "plain" ) {
	try { p.EnterShadowForm(); out += " enter=ok" } catch ( e1 ) { out += " enter_err=" + string( e1 ) }
} else {
	try { p.EnterShadowFormFortified(); out += " enterF=ok" } catch ( e2 ) { out += " enterF_err=" + string( e2 ) }
}
try { out += " after=" + p.IsShadowForm() } catch ( e3 ) { out += " after_err=" + string( e3 ) }
try { out += format( " hp=%%d/%%d sh=%%d", p.GetHealth(), p.GetMaxHealth(), p.GetShieldHealth() ) } catch ( e4 ) {}
try { p.LeaveShadowForm(); out += " leave=ok" } catch ( e5 ) { out += " leave_err=" + string( e5 ) }
try { out += " end=" + p.IsShadowForm() } catch ( e6 ) { out += " end_err=" + string( e6 ) }
AgentLink_Reply( out )
