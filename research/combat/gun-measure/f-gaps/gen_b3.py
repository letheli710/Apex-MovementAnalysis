#!/usr/bin/env python3
"""B3 cases: muzzle flash on screen. After each single shot the client waits k frames (counted from the frame the clip drops) and
takes an engine screenshot (r2/screenshots, no focus needed). One shot per k; a no-shot frame first as the baseline.
py -3 -I gen_b3.py > cases_b3.txt   (the bot is moved behind the player first)"""
L = []
ORG = "<-9949.0, -1488.0, 3856.2>"
RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ foreach ( pl in GetPlayerArray() ) if ( pl.IsBot() ) { pl.BotCmd_SetTrigger( false ) ~ pl.SetOrigin( p.GetOrigin() + <-600, 0, 0> ) } ~ AgentLink_Reply( "r" )'


def shots(ks, gap):
    arr = ", ".join(str(k) for k in ks)
    return ('cl void functionref() ss = void function() { try { entity p = GetLocalClientPlayer() ~ array<int> ks = [ ' + arr + ' ] ~ '
            'p.ClientCommand( "screenshot" ) ~ printt( "[RT] shot k=-1 t=" + Time() ) ~ wait 0.8 ~ '
            'foreach ( k in ks ) { entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand ) ~ int c0 = w.GetWeaponPrimaryClipCount() ~ '
            'p.ClientCommand( "+attack" ) ~ float ta = Time() ~ while ( w.GetWeaponPrimaryClipCount() == c0 && Time() - ta < 0.5 ) WaitFrame() ~ p.ClientCommand( "-attack" ) ~ float ts = Time() ~ '
            'for ( int i = 0 ~ i < k ~ i++ ) WaitFrame() ~ p.ClientCommand( "screenshot" ) ~ printt( format( "[RT] shot k=%d dt=%.4f t=%.4f", k, Time() - ts, Time() ) ) ~ wait ' + str(gap) + ' } '
            '} catch ( e ) { printt( "[RT] ss err " + string( e ) ) } } ~ thread ss() ~ AgentLink_Reply( "ss" )')


for gun, w, groups, gap in (("r301", "rspn101", [list(range(0, 9)), list(range(9, 18))], 0.7), ("wingman", "wingman", [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 14, 16, 18, 22, 26]], 0.9)):
    for gi, ks in enumerate(groups):
        for mode in ("hip",):
            L.append(f"b3_{gun}_{mode}_g{gi}|{w}|none|{RESET}; wait 0.5; {shots(ks, gap)}; wait {1.2 + len(ks) * (gap + 0.25)}|secs=14")
print("\n".join(L))
