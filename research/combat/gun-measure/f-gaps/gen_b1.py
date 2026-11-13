#!/usr/bin/env python3
"""B1 cases: drop from H u, one tap shot D s after the client sees the ground; and drops without a shot for the spring fit.
py -3 -I gen_b1.py > cases_b1.txt   (run with ../tools/batch.py-style runner fg_batch.py)"""
L = []
ORG = "<-9949.0, -1488.0, 3856.2>"  # flat roof with open sky (spawn pad has a roof 390 u up), firing range


def add(tag, w, m, s, k):
    L.append(f"{tag}|{w}|{m}|{s}|{k}")


RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "r" )'
DROP = lambda h: 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' + <0, 0, ' + str(h) + '> ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "d" )'
EMPTY = 'sv entity p = GetPlayerArray()[0] ~ foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 ) ~ AgentLink_Reply( "e" )'


def fire_after_land(d):
    wait = f"wait {d}" if d > 0 else "WaitFrame()"
    return ('cl void functionref() ff = void function() { try { entity p = GetLocalClientPlayer() ~ float t0 = Time() ~ '
            'while ( p.IsOnGround() && Time() - t0 < 1.5 ) WaitFrame() ~ while ( !p.IsOnGround() && Time() - t0 < 6.0 ) WaitFrame() ~ '
            'printt( "[RT] land t=" + Time() ) ~ ' + (f'wait {d} ~ ' if d > 0 else '') +
            'p.ClientCommand( "+attack" ) ~ printt( "[RT] fire t=" + Time() ) ~ WaitFrame() ~ WaitFrame() ~ p.ClientCommand( "-attack" ) '
            '} catch ( e ) { printt( "[RT] ff err " + string( e ) ) } } ~ thread ff() ~ AgentLink_Reply( "ff" )')


for r in (1, 2):
    add(f"b1_base_ads_{r}", "rspn101", "none", f"{RESET}; down zoom; wait 0.9; tap attack; wait 1.2; up zoom", "secs=4 target=body dist=60")
    for h in (96, 400, 900):
        for d in (0, 0.05, 0.1, 0.2, 0.3):
            add(f"b1_h{h}_d{int(d*1000):03d}_ads_{r}", "rspn101", "none",
                f"{RESET}; down zoom; wait 0.9; {fire_after_land(d)}; {DROP(h)}; wait {2.4 if h == 900 else 1.8}; up zoom", "secs=5 target=body dist=60")
# spring fit: no shot
for r in (1, 2):
    for h in (400, 900):
        add(f"b1s_h{h}_hip_{r}", "rspn101", "none", f"{RESET}; wait 0.5; {DROP(h)}; wait 2.6", "secs=4")
        add(f"b1s_h{h}_ads_{r}", "rspn101", "none", f"{RESET}; down zoom; wait 0.9; {DROP(h)}; wait 2.6; up zoom", "secs=4")
        add(f"b1s_h{h}_empty_{r}", "rspn101", "none", f"{RESET}; {EMPTY}; wait 0.6; {DROP(h)}; wait 2.6", "secs=4")
        add(f"b1s_h{h}_p2020_{r}", "semipistol", "none", f"{RESET}; wait 0.5; {DROP(h)}; wait 2.6", "secs=4")
print("\n".join(L))
