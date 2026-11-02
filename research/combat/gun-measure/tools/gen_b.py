#!/usr/bin/env python3
"""Cases for B: each state, hip and ADS, firing and not. py -3 -I gen_b.py > cases_b.txt"""
PAD = "-11699, 512, 1577.05"
RESET = f"sv try {{ entity p = GetPlayerArray()[0] ~ p.SetOrigin( <{PAD}> ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SetAngles( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( \"reset\" )"
VEL = lambda z: f"sv try {{ GetPlayerArray()[0].SetVelocity( <0, 0, {z}> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( \"v\" )"
HIGH = lambda h: f"sv try {{ entity p = GetPlayerArray()[0] ~ p.SetOrigin( p.GetOrigin() + <0, 0, {h}> ) }} catch ( e ) {{ }} ~ AgentLink_Reply( \"h\" )"
STIM = "sv try { entity p = GetPlayerArray()[0] ~ p.GiveOffhandWeapon( \"mp_ability_heal\", OFFHAND_TACTICAL, [] ) } catch ( e ) { printt( \"[RT] stim err \" + string( e ) ) } ~ AgentLink_Reply( \"s\" )"
FORWARD = "down forward; wait 0.9"
SPRINT = "down forward; down speed; wait 1.2"
SLIDE = SPRINT + "; down duck; wait 0.12"
ENTER = {
    "stand": ("", ""),
    "walk": (FORWARD, "up forward"),
    "sprint": (SPRINT, "up speed; up forward"),
    "crouch": ("down duck; wait 0.5", "up duck"),
    "crouchwalk": ("down duck; down forward; wait 0.9", "up forward; up duck"),
    "slide": (SLIDE, "up duck; up speed; up forward"),
    "jump": ("tap jump; wait 0.05", ""),
    "rising": (VEL(900) + "; wait 0.05", ""),
    "falling": (HIGH(700) + "; wait 0.3", ""),
    "sprintjump": (SPRINT + "; tap jump; wait 0.05", "up speed; up forward"),
    "doublejump": ("tap jump; wait 0.35; tap jump; wait 0.05", ""),
    "landing": (HIGH(160) + "; wait 0.55", ""),
}
GUNS = {"r301": ("rspn101", "auto", 0.8), "wingman": ("wingman", "semi", 0.45), "spitfire": ("lmg", "auto", 0.8), "p2020": ("semipistol", "semi", 0.2), "mastiff": ("mastiff", "semi", 1.15), "flatline": ("vinson", "auto", 0.8)}
L = []
for g, (w, mode, x) in GUNS.items():
    for st, (a, z) in ENTER.items():
        for aim in ("hip", "ads"):
            zi = "down zoom; wait 0.5; " if aim == "ads" else ""
            zo = "; up zoom" if aim == "ads" else ""
            fire = f"hold attack {x}" if mode == "auto" else "; ".join([f"tap attack; wait {x}"] * 3)
            pre = (a + "; ") if a else ""
            # ads: aim first when the state is air-time limited, so the fire lands in the state
            if st in ("jump", "rising", "falling", "landing", "sprintjump", "doublejump") and aim == "ads":
                s = f"{RESET}; wait 0.3; {zi}{pre}{fire}"
            else:
                s = f"{RESET}; wait 0.3; {pre}{zi}{fire}"
            s += f"; wait 0.4; {z}{zo}; wait 0.8; {RESET}".replace("; ;", ";")
            L.append(f"st_{g}_{st}_{aim}|{w}|none|{s}|secs=8 settle=0.9")
# No fire: sway, bob, drift, ADS allowed. R-301 and Wingman.
for g, w in (("r301", "rspn101"), ("wingman", "wingman")):
    for st, (a, z) in ENTER.items():
        for aim in ("hip", "ads"):
            zi = "down zoom; wait 0.5; " if aim == "ads" else ""
            zo = "; up zoom" if aim == "ads" else ""
            pre = (a + "; ") if a else ""
            s = f"{RESET}; wait 0.3; {pre}{zi}wait 1.2; {z}{zo}; wait 0.5; {RESET}".replace("; ;", ";")
            L.append(f"sw_{g}_{st}_{aim}|{w}|none|{s}|secs=7 settle=0.9")
print("\n".join(L))
