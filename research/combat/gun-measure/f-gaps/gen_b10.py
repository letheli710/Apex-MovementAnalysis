#!/usr/bin/env python3
"""B10 cases: engine screenshots (no focus) of the crosshair and HUD per gun, hip and ADS, from the spawn pad facing the clear lane;
plus a hit-marker frame: one shot into a dummie 200 u ahead, screenshot 3 and 10 frames after the clip drops.
Each screenshot is announced by a [RT] ss line (gun, view) so the files can be matched in order. py -3 -I gen_b10.py > cases_b10.txt"""
GUNS = ["rspn101", "r97", "car", "vinson", "lmg", "alternator_smg", "autopistol", "volt_smg", "semipistol", "hemlok", "pdw", "nemesis", "auto_hemlok",
        "shotgun", "mastiff", "energy_shotgun", "shotgun_pistol", "doubletake", "sniper", "dmr", "sentinel", "g2", "wingman", "defender",
        "energy_ar", "esaw", "dragon_lmg", "lstar", "3030", "bow"]
L = []
SS = lambda gun, view: f'cl GetLocalClientPlayer().ClientCommand( "screenshot" ) ~ printt( "[RT] ss {gun} {view} t=" + Time() ) ~ AgentLink_Reply( "ss" )'
HIT = lambda gun: ('cl void functionref() hm = void function() { try { entity p = GetLocalClientPlayer() ~ entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand ) ~ int c0 = w.GetWeaponPrimaryClipCount() ~ '
                   'p.ClientCommand( "+attack" ) ~ float ta = Time() ~ while ( w.GetWeaponPrimaryClipCount() == c0 && Time() - ta < 1.5 ) WaitFrame() ~ p.ClientCommand( "-attack" ) ~ '
                   'for ( int i = 0 ~ i < 3 ~ i++ ) WaitFrame() ~ p.ClientCommand( "screenshot" ) ~ printt( "[RT] ss ' + gun + ' hit3 t=" + Time() ) ~ '
                   'for ( int i = 0 ~ i < 7 ~ i++ ) WaitFrame() ~ p.ClientCommand( "screenshot" ) ~ printt( "[RT] ss ' + gun + ' hit10 t=" + Time() ) '
                   '} catch ( e ) { printt( "[RT] hm err " + string( e ) ) } } ~ thread hm() ~ AgentLink_Reply( "hm" )')
for g in GUNS:
    L.append(f"b10_{g}|{g}|none|wait 0.6; {SS(g, 'hip')}; wait 0.4; down zoom; wait 1.0; {SS(g, 'ads')}; wait 0.4; up zoom; wait 0.6|secs=5 settle=1.4")
for g in ("rspn101", "wingman", "mastiff", "sniper"):
    L.append(f"b10_hit_{g}|{g}|none|wait 0.5; {HIT(g)}; wait 2.2|secs=5 settle=1.4 target=body dist=200")
print("\n".join(L))
