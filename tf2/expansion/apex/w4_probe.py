#!/usr/bin/env python3
"""W4 (Apex items) probes in local R5Flowstate, over AgentLink.

Uses the HSD runner's launcher and AgentLink client read-only (imports them from the
Apex-MovementAnalysis repo; nothing there is changed). Every probe writes the server and
client log lines tagged [W4] to runs/<timestamp>_<probe>.txt next to this file.

  python -I w4_probe.py launch            # GAME-LOCK, start dedi + client, wait alive
  python -I w4_probe.py probe info        # characters, ConVars, weapon settings
  python -I w4_probe.py probe frag_real   # +attack throw attempt (did not fire in this build; see APEX-REPORT 2.1)
  python -I w4_probe.py probe frag_move   # same, player pushed forward at 300 u/s at the release
  python -I w4_probe.py probe frag_fuse   # same with the Fuse passive mod fuse_long_throw_passive
  python -I w4_probe.py probe scripted    # FireWeaponGrenade with a unit direction (frag, arc star, thermite)
  python -I w4_probe.py probe arcself     # arc star planted at the player's feet, status effects sampled
  python -I w4_probe.py probe decoy       # CreateTargetedPlayerDecoy, decoy path sampled
  python -I w4_probe.py stop              # stop the game, delete GAME-LOCK
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TOOLS = os.path.join(WS, "Apex-MovementAnalysis", "research", "phase2-local", "tools")
sys.path.insert(0, TOOLS)
from agentlink import AgentLink, AgentLinkError, DEFAULT_GAME  # noqa: E402

LOCK = os.path.join(WS, "GAME-LOCK.txt")
RUNS = os.path.join(HERE, "runs")
PS = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(TOOLS, "hsd_launch.ps1")]

# ---------------------------------------------------------------- Squirrel snippets
LOGGER = r'''
entity p = GetPlayerArray()[0]
void functionref() w4lf = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < %(dur).1f ) {
			vector ea = p.EyeAngles()
			vector eo = p.EyePosition()
			vector v = p.GetVelocity()
			printt( format( "[W4] %(tag)s t=%%.4f P eo=%%.2f,%%.2f,%%.2f ea=%%.3f,%%.3f v=%%.2f,%%.2f,%%.2f",
				Time() - t0, eo.x, eo.y, eo.z, ea.x, ea.y, v.x, v.y, v.z ) )
			foreach ( e in GetProjectileArrayEx( "any", TEAM_ANY, TEAM_ANY, p.GetOrigin(), 60000 ) ) {
				vector o = e.GetOrigin()
				vector pv = e.GetVelocity()
				printt( format( "[W4] %(tag)s t=%%.4f G id=%%d cls=%%s o=%%.2f,%%.2f,%%.2f v=%%.2f,%%.2f,%%.2f",
					Time() - t0, e.GetEncodedEHandle(), e.GetClassName(), o.x, o.y, o.z, pv.x, pv.y, pv.z ) )
			}
			WaitFrame()
		}
	} catch ( err ) { printt( "[W4] %(tag)s err " + string( err ) ) }
	printt( "[W4] %(tag)s logger end" )
}
thread w4lf()
AgentLink_Reply( "logger %(tag)s" )
'''

GIVE = r'''
entity p = GetPlayerArray()[0]
string out = ""
try {
	try { SURVIVAL_AddToPlayerInventory( p, "%(weap)s", 4 ) } catch ( e0 ) { out += " inv_err=" + string( e0 ) }
	try { p.TakeNormalWeaponByIndexNow( WEAPON_INVENTORY_SLOT_ANTI_TITAN ) } catch ( e1 ) { out += " take_err" }
	if ( %(fuse)d == 1 ) {
		try { GiveExtraWeaponMod( p, "fuse_long_throw_passive" ) } catch ( e2 ) { out += " mod_err=" + string( e2 ) }
	} else {
		try { array mods = p.GetExtraWeaponMods(); if ( mods.contains( "fuse_long_throw_passive" ) ) { mods.fastremovebyvalue( "fuse_long_throw_passive" ); p.SetExtraWeaponMods( mods ) } } catch ( e3 ) { out += " unmod_err" }
	}
	entity w = p.GiveWeapon( "%(weap)s", WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	p.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "%(weap)s" )
	p.SetOrigin( p.GetOrigin() )
	try { p.SnapEyeAngles( <%(pitch).1f, p.EyeAngles().y, 0> ) } catch ( e4 ) { out += " snap_err" }
	out += " w=" + w.GetWeaponClassName() + " speed=" + w.GetWeaponSettingFloat( eWeaponVar.projectile_launch_speed )
	out += " mods=" + w.GetMods().len() + " clip=" + w.GetWeaponPrimaryClipCount()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
'''

INFO = r'''
string out = ""
try {
	foreach ( ItemFlavor c in GetAllCharacters() ) out += ItemFlavor_GetHumanReadableRef( c ) + " "
} catch ( e0 ) { out += " chars_err=" + string( e0 ) }
out += " | sv_gravity=" + GetConVarFloat( "sv_gravity" )
foreach ( string wn in [ "mp_weapon_frag_grenade", "mp_weapon_grenade_emp", "mp_weapon_thermite_grenade", "mp_weapon_cluster_bomb_launcher", "mp_weapon_cluster_bomb", "mp_ability_holopilot", "mp_ability_mirage_ultimate", "mp_ability_area_sonar_scan", "mp_ability_hunt_mode", "mp_ability_heartbeat_sensor", "mp_ability_crypto_drone", "mp_weapon_cover_wall" ] ) {
	try { out += " | " + wn + "=" + GetWeaponInfoFileKeyField_GlobalString( wn, "printname" ) } catch ( e1 ) { out += " | " + wn + "=MISSING" }
}
try { out += " | pas_fuse=" + ePassives.PAS_FUSE } catch ( e2 ) { out += " | pas_fuse=MISSING" }
AgentLink_Reply( out )
'''

SCRIPTED = r'''
entity p = GetPlayerArray()[0]
string out = ""
foreach ( string wn in [ "mp_weapon_frag_grenade", "mp_weapon_grenade_emp", "mp_weapon_thermite_grenade" ] ) {
	try {
		try { p.TakeNormalWeaponByIndexNow( WEAPON_INVENTORY_SLOT_ANTI_TITAN ) } catch ( e1 ) {}
		entity w = p.GiveWeapon( wn, WEAPON_INVENTORY_SLOT_ANTI_TITAN )
		float yaw = p.EyeAngles().y + ( wn == "mp_weapon_frag_grenade" ? 0.0 : ( wn == "mp_weapon_grenade_emp" ? 30.0 : -30.0 ) )
		vector dir = AnglesToForward( <-10.0, yaw, 0> )
		WeaponFireGrenadeParams fp
		fp.pos = p.EyePosition() + dir * 40.0
		fp.vel = dir
		fp.angVel = <0, 0, 0>
		fp.fuseTime = w.GetGrenadeFuseTime()
		fp.scriptTouchDamageType = 0
		fp.scriptExplosionDamageType = 0
		fp.clientPredicted = false
		fp.lagCompensated = false
		fp.useScriptOnDamage = true
		entity g = w.FireWeaponGrenade( fp )
		vector gv = IsValid( g ) ? g.GetVelocity() : <0, 0, 0>
		if ( IsValid( g ) ) {
			string tg = wn
			void functionref() tf = void function() : ( g, tg ) {
				float t0 = Time()
				while ( IsValid( g ) && Time() - t0 < 8.0 ) {
					vector o = g.GetOrigin()
					vector v = g.GetVelocity()
					printt( format( "[W4] trk %s t=%.4f o=%.2f,%.2f,%.2f v=%.2f,%.2f,%.2f", tg, Time() - t0, o.x, o.y, o.z, v.x, v.y, v.z ) )
					WaitFrame()
				}
				printt( format( "[W4] trk %s end t=%.4f valid=%d", tg, Time() - t0, IsValid( g ) ? 1 : 0 ) )
			}
			thread tf()
		}
		out += format( " %s: valid=" + IsValid( g ) + " fuse=%.2f speed=%.1f grav=%.2f v0=%.1f,%.1f,%.1f |v0|=%.1f", wn, fp.fuseTime,
			w.GetWeaponSettingFloat( eWeaponVar.projectile_launch_speed ), w.GetWeaponSettingFloat( eWeaponVar.projectile_gravity_scale ),
			gv.x, gv.y, gv.z, Length( gv ) )
	} catch ( err ) { out += " " + wn + " err=" + string( err ) }
}
AgentLink_Reply( out )
'''

ARCSELF = r'''
entity p = GetPlayerArray()[0]
string out = ""
try {
	try { p.TakeNormalWeaponByIndexNow( WEAPON_INVENTORY_SLOT_ANTI_TITAN ) } catch ( e1 ) {}
	entity w = p.GiveWeapon( "mp_weapon_grenade_emp", WEAPON_INVENTORY_SLOT_ANTI_TITAN )
	vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
	WeaponFireGrenadeParams fp
	fp.pos = p.GetOrigin() + fwd * 60.0 + <0, 0, 20>
	fp.vel = <0, 0, -1>
	fp.angVel = <0, 0, 0>
	fp.fuseTime = 0.0
	fp.scriptTouchDamageType = 0
	fp.scriptExplosionDamageType = DF_RAGDOLL | DF_EXPLOSION | DF_ELECTRICAL | DF_STUN_AI
	fp.clientPredicted = false
	fp.lagCompensated = false
	fp.useScriptOnDamage = true
	entity g = w.FireWeaponGrenade( fp )
	out += " fired=" + IsValid( g )
	void functionref() sf = void function() : ( p ) {
		float t0 = Time()
		while ( Time() - t0 < 6.0 ) {
			printt( format( "[W4] arcself t=%.3f hp=%d sh=%d slow=%.3f turn=%.3f emp=%.3f v=%.1f", Time() - t0, p.GetHealth(), p.GetShieldHealth(),
				StatusEffect_GetSeverity( p, eStatusEffect.move_slow ), StatusEffect_GetSeverity( p, eStatusEffect.turn_slow ), StatusEffect_GetSeverity( p, eStatusEffect.emp ), Length( p.GetVelocity() ) ) )
			wait 0.1
		}
	}
	thread sf()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
'''

DECOY = r'''
entity p = GetPlayerArray()[0]
string out = ""
try {
	vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
	entity d = p.CreateTargetedPlayerDecoy( p.GetOrigin() + fwd * 3000.0, $"", $"", 0, 0 )
	d.SetTimeout( 6.0 )
	d.SetOwner( p )
	out += " decoy=" + IsValid( d ) + " cls=" + d.GetClassName()
	void functionref() df = void function() : ( d, p ) {
		float t0 = Time()
		try {
			while ( IsValid( d ) && Time() - t0 < 6.5 ) {
				vector o = d.GetOrigin()
				vector v = d.GetVelocity()
				printt( format( "[W4] decoy t=%.3f o=%.1f,%.1f,%.1f v=%.1f,%.1f,%.1f spd2d=%.1f", Time() - t0, o.x, o.y, o.z, v.x, v.y, v.z, Length2D( v ) ) )
				WaitFrame()
			}
		} catch ( err ) { printt( "[W4] decoy err " + string( err ) ) }
		printt( "[W4] decoy end valid=" + IsValid( d ) )
	}
	thread df()
} catch ( err ) { out += " err=" + string( err ) }
AgentLink_Reply( out )
'''

PUSH = r'''
entity p = GetPlayerArray()[0]
vector fwd = AnglesToForward( <0, p.EyeAngles().y, 0> )
p.SetVelocity( fwd * 300.0 + <0, 0, p.GetVelocity().z> )
AgentLink_Reply( "pushed" )
'''


def wait_alive(game, timeout=900):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with AgentLink("client", game, timeout=10) as c, AgentLink("server", game, timeout=10) as s:
                cl = c.eval('entity p = GetLocalClientPlayer(); AgentLink_Reply( IsValid( p ) && IsAlive( p ) ? "alive" : "no" )', check=False)
                sv = s.eval('AgentLink_Reply( GetPlayerArray().len() > 0 && IsAlive( GetPlayerArray()[0] ) ? "alive" : "no" )', check=False)
                if cl.get("reply") == "alive" and sv.get("reply") == "alive":
                    return True
        except (OSError, AgentLinkError, FileNotFoundError):
            pass
        time.sleep(5)
    return False


class Poller:
    """The server log ring is flooded by [MOVE-TRACE]; poll it while waiting."""
    def __init__(self, links):
        self.links = links
        self.cur = {k: l.info()["logSeq"] for k, l in links.items()}
        self.lines = {k: [] for k in links}

    def poll(self):
        for k, l in self.links.items():
            while True:
                r = l.log(self.cur[k], 500)
                for e in r.get("lines", []):
                    if "[W4]" in e.get("text", ""):
                        self.lines[k].append(e["text"].rstrip())
                nxt = r.get("next", self.cur[k])
                if nxt == self.cur[k] or not r.get("lines"):
                    self.cur[k] = nxt
                    break
                self.cur[k] = nxt

    def sleep(self, sec):
        end = time.time() + sec
        while time.time() < end:
            self.poll()
            time.sleep(0.05)
        self.poll()


def probe(name, game):
    os.makedirs(RUNS, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = [f"# probe {name} {stamp}"]
    with AgentLink("server", game) as s, AgentLink("client", game) as c:
        pl = Poller({"s": s, "c": c})
        if name == "info":
            out.append("server: " + s.eval(INFO, check=False).get("reply", "?"))
        elif name in ("frag_real", "frag_move", "frag_fuse", "arc_real", "thermite_real"):
            weap = {"arc_real": "mp_weapon_grenade_emp", "thermite_real": "mp_weapon_thermite_grenade"}.get(name, "mp_weapon_frag_grenade")
            fuse = 1 if name == "frag_fuse" else 0
            out.append("give: " + s.eval(GIVE % dict(weap=weap, fuse=fuse, pitch=-10.0), check=False).get("reply", "?"))
            pl.sleep(1.5)
            out.append("logger: " + s.eval(LOGGER % dict(tag=name, dur=7.0), check=False).get("reply", "?"))
            c.eval('GetLocalClientPlayer().ClientCommand( "+attack" ); AgentLink_Reply( "d" )', check=False)
            pl.sleep(1.5)
            if name == "frag_move":
                out.append(s.eval(PUSH, check=False).get("reply", "?"))
            c.eval('GetLocalClientPlayer().ClientCommand( "-attack" ); AgentLink_Reply( "u" )', check=False)
            pl.sleep(7.5)
        elif name == "scripted":
            out.append("logger: " + s.eval(LOGGER % dict(tag=name, dur=6.0), check=False).get("reply", "?"))
            out.append("fire: " + s.eval(SCRIPTED, check=False).get("reply", "?"))
            pl.sleep(7.0)
        elif name == "arcself":
            out.append("fire: " + s.eval(ARCSELF, check=False).get("reply", "?"))
            pl.sleep(7.0)
        elif name == "decoy":
            out.append("decoy: " + s.eval(DECOY, check=False).get("reply", "?"))
            pl.sleep(7.5)
        else:
            raise SystemExit(f"unknown probe {name}")
        pl.sleep(0.5)
        sl, cl = pl.lines["s"], pl.lines["c"]
    out += ["## server"] + sl + ["## client"] + cl
    path = os.path.join(RUNS, f"{stamp}_{name}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out[:6]))
    print(f"... {len(sl)} server / {len(cl)} client lines -> {path}")


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    game = DEFAULT_GAME
    if argv[0] == "launch":
        if os.path.exists(LOCK):
            with open(LOCK, encoding="utf-8") as fh:
                raise SystemExit("GAME-LOCK held: " + fh.read().strip())
        with open(LOCK, "w", encoding="utf-8") as fh:
            fh.write("r5 tf2-w4-apex " + time.strftime("%Y-%m-%d %H:%M") + "\n")
        subprocess.run(PS, check=True)
        print("alive" if wait_alive(game) else "NOT alive")
    elif argv[0] == "probe":
        probe(argv[1], game)
    elif argv[0] == "stop":
        subprocess.run(PS + ["-Stop"])
        if os.path.exists(LOCK):
            os.remove(LOCK)
        print("stopped, lock removed")
    elif argv[0] == "rawlog":
        with AgentLink(argv[1], game) as l:
            print(l.log(int(argv[2]) if len(argv) > 2 else 0, 5))


if __name__ == "__main__":
    main(sys.argv[1:])
