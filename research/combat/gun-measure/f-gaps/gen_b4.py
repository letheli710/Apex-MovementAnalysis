#!/usr/bin/env python3
"""B4 cases: a bot player (SDK SpawnBots + BotCmd program) really shoots the local player. Run snippets/dmg_hook.nut once and SpawnBots(1) first.
py -3 -I gen_b4.py > cases_b4.txt"""
L = []
ORG = "<-9949.0, -1488.0, 3856.2>"
RESET = 'sv entity p = GetPlayerArray()[0] ~ p.SetOrigin( ' + ORG + ' ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SnapEyeAngles( <0, 0, 0> ) ~ AgentLink_Reply( "r" )'


def bot(weap, dx, dy, interval):
    return ('sv entity p = GetPlayerArray()[0] ~ entity bot = null ~ foreach ( pl in GetPlayerArray() ) if ( pl.IsBot() ) bot = pl ~ '
            'p.SetMaxHealth( 100000 ) ~ p.SetHealth( 100000 ) ~ bot.RemoveFromAllRealms() ~ bot.AddToOtherEntitysRealms( p ) ~ '
            f'bot.SetOrigin( p.GetOrigin() + <{dx}, {dy}, 0> ) ~ bot.SetVelocity( <0, 0, 0> ) ~ foreach ( w0 in bot.GetMainWeapons() ) bot.TakeWeaponByEntNow( w0 ) ~ '
            f'entity w = bot.GiveWeapon( "{weap}", WEAPON_INVENTORY_SLOT_PRIMARY_0, [] ) ~ bot.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "{weap}" ) ~ '
            'w.SetWeaponPrimaryClipCount( w.GetWeaponPrimaryClipCountMax() ) ~ bot.SetMaxHealth( 100000 ) ~ bot.SetHealth( 100000 ) ~ bot.BotCmd_Face( p ) ~ '
            f'bot.BotCmd_SetMove( 0.0, 0.0, 0 ) ~ bot.BotCmd_SetFireProfile( 1, {interval}, 0.0 ) ~ AgentLink_Reply( "bot " + w.GetWeaponClassName() )')


TRIG = lambda on: 'sv foreach ( pl in GetPlayerArray() ) if ( pl.IsBot() ) pl.BotCmd_SetTrigger( ' + on + ' ) ~ AgentLink_Reply( "t" )'
for r in (1, 2):
    for bw, iv, n in (("mp_weapon_rspn101", 0.6, "r301"), ("mp_weapon_wingman", 0.8, "wingman"), ("mp_weapon_sniper", 1.0, "kraber")):
        for side, dx, dy in (("front", 300, 0), ("left", 0, 300)):
            if n == "kraber" and side == "left": continue
            sched = f"{RESET}; {bot(bw, dx, dy, iv)}; wait 0.6; {TRIG('true')}; wait 2.6; {TRIG('false')}; wait 0.8"
            L.append(f"b4_{n}_{side}_hip_{r}|rspn101|none|{sched}|secs=6")
            sched = f"{RESET}; down zoom; {bot(bw, dx, dy, iv)}; wait 0.6; {TRIG('true')}; wait 2.6; {TRIG('false')}; wait 0.8; up zoom"
            L.append(f"b4_{n}_{side}_ads_{r}|rspn101|none|{sched}|secs=6")
print("\n".join(L))
