#!/usr/bin/env python3
"""Shotgun reticle + pellet hit dots in R5, through AgentLink. No mouse or focus: screenshots go through the engine command.

  py -3 -I sr.py <out dir> <experiment> [args]

experiments
  reticle <gun> ...        hip / crouch / ADS / move / air / after-fire screenshots of each gun's crosshair
  dots                     synthetic ui/projectile_hit_dot: a grid of ages and crit / not crit, one screenshot
  life                     how long one projectile_hit_dot lives (RuiIsAlive each frame)
  fire <gun> <target> <dist> [hook]  real shot at a hovering dummie; hook=1 adds R5's own hit-dot code (the firing range turns it off)
  turn                     a real hit, then turn the view: do the dots stay on the world point or on the screen?
"""
import glob, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
COMBAT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(COMBAT, "w2-runtime"))
from rt_probe import AgentLink, DEFAULT_GAME, Poller  # noqa: E402
from PIL import Image  # noqa: E402

SHOTDIR = os.path.expanduser("~/Games/R5Flowstate/r2/screenshots")
GUNS = {"eva8": "mp_weapon_shotgun", "mastiff": "mp_weapon_mastiff", "peacekeeper": "mp_weapon_energy_shotgun", "mozambique": "mp_weapon_shotgun_pistol",
        "tripletake": "mp_weapon_doubletake", "bocek": "mp_weapon_bow", "3030": "mp_weapon_3030", "alternator": "mp_weapon_alternator_smg", "r301": "mp_weapon_rspn101"}
YAW = os.environ.get("SR_YAW", "0")
ORIGIN = os.environ.get("SR_ORIGIN", "-11699, 512, 1579")
RESET = 'entity p = GetPlayerArray()[0]; p.SetOrigin( <' + ORIGIN + '> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <{pitch}, ' + YAW + ', 0> ); AgentLink_Reply( "r" )'
STATE = r'''
entity p = GetLocalClientPlayer()
entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
vector a = p.CameraAngles()
printt( format( "[RT] st t=%.3f fov=%.3f zf=%.3f spread=%.3f ca=%.2f,%.2f vel=%.1f gnd=%d duck=%d w=%s pps=%d", Time(), p.GetFOV(), p.GetZoomFrac(), IsValid( w ) ? w.GetAttackSpreadAngle() : -1.0, a.x, a.y, Length( p.GetVelocity() ), p.IsOnGround() ? 1 : 0, p.IsCrouched() ? 1 : 0, IsValid( w ) ? w.GetWeaponClassName() : "-", IsValid( w ) ? w.GetProjectilesPerShot() : -1 ) )
AgentLink_Reply( "st" )
'''
# R5's own code for the dots (cl_hud.gnut DamageFlyout -> ShouldShowProjectileHitDot), minus the firing-range gate. Logs each hit and the dot's life.
HOOK = r'''
AddLocalPlayerDidDamageCallback( void function( entity attacker, entity victim, vector pos, int dt, float amt ) {
	entity w = attacker.GetActiveWeapon( eActiveInventorySlot.mainHand )
	int pps = IsValid( w ) ? w.GetProjectilesPerShot() : -1
	bool crit = ( dt & DF_HEADSHOT ) != 0 || ( dt & DF_CRITICAL ) != 0
	vector c = attacker.CameraPosition()
	vector a = attacker.CameraAngles()
	vector d = pos - c
	printt( format( "[RT] hit h={{hook}} t=%.3f amt=%.2f crit=%d kill=%d shield=%d pps=%d pos=%.2f,%.2f,%.2f cam=%.2f,%.2f,%.2f fwd=%.3f right=%.3f up=%.3f", Time(), amt, crit ? 1 : 0, ( dt & DF_KILLSHOT ) != 0 ? 1 : 0, ( dt & DF_SHIELD_DAMAGE ) != 0 ? 1 : 0, pps, pos.x, pos.y, pos.z, c.x, c.y, c.z, DotProduct( d, AnglesToForward( a ) ), DotProduct( d, AnglesToRight( a ) ), DotProduct( d, AnglesToUp( a ) ) ) )
	if ( pps <= 1 || {{hook}} == 0 )
		return
	var r = RuiCreate( $"ui/projectile_hit_dot.rpak", clGlobal.topoFullScreen, RUI_DRAW_HUD, 0 )
	RuiSetResolutionToScreenSize( r )
	RuiSetGameTime( r, "startTime", Time() )
	RuiSetFloat3( r, "pos", pos )
	RuiSetBool( r, "isCrit", crit )
	void functionref() lf = void function() : ( r ) {
		float t0 = Time()
		while ( RuiIsAlive( r ) && Time() - t0 < 10.0 ) WaitFrame()
		printt( format( "[RT] dotlife %.3f alive=%d", Time() - t0, RuiIsAlive( r ) ? 1 : 0 ) )
	}
	thread lf()
} )
AgentLink_Reply( "hooked" )
'''
# Synthetic dots on world points in front of the camera; startTime in the past shows a dot at that age.
DOTS = r'''
entity p = GetLocalClientPlayer()
vector c = p.CameraPosition()
vector a = p.CameraAngles()
vector f = AnglesToForward( a )
vector rt = AnglesToRight( a )
vector up = AnglesToUp( a )
array<float> ages = [{{ages}}]
array<var> ruis = []
array<float> rages = []
int i = 0
foreach ( age in ages ) {
	for ( int k = 0; k < 2; k++ ) {
		var r = RuiCreate( $"ui/projectile_hit_dot.rpak", clGlobal.topoFullScreen, RUI_DRAW_HUD, 0 )
		RuiSetResolutionToScreenSize( r )
		RuiSetGameTime( r, "startTime", Time() - age )
		vector pos = c + f * {{dist}} + rt * ( ( i - ( ages.len() - 1 ) / 2.0 ) * {{step}} ) + up * ( k == 0 ? {{step}} : -{{step}} )
		RuiSetFloat3( r, "pos", pos )
		RuiSetBool( r, "isCrit", k == 1 )
		ruis.append( r )
		rages.append( age )
	}
	i++
}
// hold every dot at its age: startTime follows the clock for {{hold}} s, then the dots run out on their own
void functionref() lf = void function() : ( ruis, rages ) {
	float t0 = Time()
	while ( Time() - t0 < {{hold}} ) {
		for ( int j = 0; j < ruis.len(); j++ )
			if ( RuiIsAlive( ruis[j] ) ) RuiSetGameTime( ruis[j], "startTime", Time() - rages[j] )
		WaitFrame()
	}
	int alive = 0
	foreach ( r in ruis ) if ( RuiIsAlive( r ) ) alive++
	printt( "[RT] dots held, alive " + alive + "/" + ruis.len() )
}
thread lf()
AgentLink_Reply( "dots " + ages.len() )
'''
LIFE = r'''
entity p = GetLocalClientPlayer()
vector c = p.CameraPosition()
var r = RuiCreate( $"ui/projectile_hit_dot.rpak", clGlobal.topoFullScreen, RUI_DRAW_HUD, 0 )
RuiSetResolutionToScreenSize( r )
RuiSetGameTime( r, "startTime", Time() )
RuiSetFloat3( r, "pos", c + AnglesToForward( p.CameraAngles() ) * 300 )
RuiSetBool( r, "isCrit", {{crit}} == 1 )
void functionref() lf = void function() : ( r ) {
	float t0 = Time()
	while ( RuiIsAlive( r ) && Time() - t0 < 20.0 ) WaitFrame()
	printt( format( "[RT] dotlife %.3f alive=%d", Time() - t0, RuiIsAlive( r ) ? 1 : 0 ) )
}
thread lf()
AgentLink_Reply( "life" )
'''


class R5:
    def __init__(self, out):
        self.out = out
        os.makedirs(out, exist_ok=True)
        self.s = AgentLink("server", DEFAULT_GAME).__enter__()
        self.c = AgentLink("client", DEFAULT_GAME).__enter__()
        self.pl = Poller({"s": self.s, "c": self.c})
        self.log = []

    def sv(self, code):
        return self.s.eval(code, check=False)

    def cl(self, code):
        return self.c.eval(code, check=False)

    def key(self, sign, k):
        self.cl(f'GetLocalClientPlayer().ClientCommand( "{sign}{k}" ); AgentLink_Reply( "k" )')

    def state(self, tag):
        self.pl.lines["c"].clear()
        self.cl(STATE)
        self.pl.sleep(0.15)
        st = next((l for l in self.pl.lines["c"] if l.startswith("[RT] st")), "")
        self.log.append(f"{tag}\t{st}")
        return st

    def shot(self, name, crop=360):
        before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
        self.cl('GetLocalClientPlayer().ClientCommand( "screenshot" ); AgentLink_Reply( "s" )')
        t0 = time.time()
        new = []
        while time.time() - t0 < 4:
            self.pl.sleep(0.2)
            new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
            if new:
                break
        if not new:
            self.log.append(f"{name}\tNO FILE")
            return None
        self.pl.sleep(0.3)
        im = Image.open(new[0]).convert("RGB")
        im.save(os.path.join(self.out, name + "_full.png"))
        w, h = im.size
        if crop:
            im.crop((w // 2 - crop // 2, h // 2 - crop // 2, w // 2 + crop // 2, h // 2 + crop // 2)).save(os.path.join(self.out, name + ".png"))
        self.log.append(f"{name}\t{w}x{h}")
        return im

    def give(self, weap, pitch=0, target="none", dist="300", snap="0", mods="none", secs="60"):
        code = open(os.path.join(COMBAT, "ip2-runtime", "snippets", "gun.nut"), encoding="utf-8").read()
        for k, v in dict(weap=weap, mods=mods, stock="150", target=target, dist=dist, yaw="0", snap=snap, lift="0", heat="0.0", track="0", secs=secs).items():
            code = code.replace("{{" + k + "}}", v)
        self.sv(RESET.replace("{pitch}", str(pitch)))
        r = self.sv(code)
        self.log.append(f"give {weap}\t{r.get('reply')}")
        self.pl.sleep(2.4)
        self.sv(RESET.replace("{pitch}", str(pitch)))
        self.pl.sleep(0.6)

    def close(self):
        open(os.path.join(self.out, "log.txt"), "a", encoding="utf-8", newline="\n").write(
            "\n".join(self.log) + "\n## server\n" + "\n".join(self.pl.lines["s"]) + "\n## client\n" + "\n".join(self.pl.lines["c"]) + "\n")
        self.s.__exit__(None, None, None)
        self.c.__exit__(None, None, None)


def reticle(r, guns, pitch):
    for g in guns:
        r.give(GUNS[g], pitch)
        r.state(f"{g} still"); r.shot(f"{g}_still")
        r.key("+", "duck"); r.pl.sleep(0.8); r.state(f"{g} crouch"); r.shot(f"{g}_crouch"); r.key("-", "duck"); r.pl.sleep(0.6)
        r.key("+", "forward"); r.pl.sleep(0.8); r.state(f"{g} walk"); r.shot(f"{g}_walk"); r.key("-", "forward"); r.pl.sleep(0.8)
        r.sv(RESET.replace("{pitch}", str(pitch)))
        r.key("+", "jump"); r.pl.sleep(0.25); r.state(f"{g} air"); r.shot(f"{g}_air"); r.key("-", "jump"); r.pl.sleep(1.5)
        r.sv(RESET.replace("{pitch}", str(pitch)))
        r.key("+", "zoom"); r.pl.sleep(1.0); r.state(f"{g} ads"); r.shot(f"{g}_ads"); r.key("-", "zoom"); r.pl.sleep(0.8)
        r.key("+", "attack"); r.pl.sleep(0.06); r.key("-", "attack"); r.state(f"{g} fired"); r.shot(f"{g}_fired"); r.pl.sleep(1.2)
        print(g, "done", flush=True)


def main():
    out, exp = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    r = R5(out)
    try:
        if exp == "reticle":
            pitch = float(os.environ.get("SR_PITCH", "0"))
            reticle(r, args or ["eva8", "mastiff", "peacekeeper", "mozambique"], pitch)
        elif exp == "still":
            # args: weapon class names; SR_FOVSCALES: comma list of cl_fovScale values (restored to the first afterwards)
            scales = os.environ.get("SR_FOVSCALES", "").split(",") if os.environ.get("SR_FOVSCALES") else [""]
            for sc in scales:
                if sc:
                    r.cl(f'GetLocalClientPlayer().ClientCommand( "cl_fovScale {sc}" ); AgentLink_Reply( "f" )'); r.pl.sleep(0.6)
                for w in args:
                    r.give(w, 0)
                    r.state(f"{w} fs{sc}"); r.shot(f"{w.replace('mp_weapon_', '')}_fs{sc or 'x'}_still")
            if scales[0]:
                r.cl(f'GetLocalClientPlayer().ClientCommand( "cl_fovScale {scales[0]}" ); AgentLink_Reply( "f" )')
        elif exp == "dots":
            ages = os.environ.get("SR_AGES", "0.0,0.05,0.1,0.2,0.3,0.5,0.75,1.0,1.5")
            r.give(GUNS["eva8"], 0)
            r.cl(DOTS.replace("{{ages}}", ages).replace("{{dist}}", "300").replace("{{hold}}", "4.0").replace("{{step}}", os.environ.get("SR_STEP", "30")))
            r.pl.sleep(0.05)
            r.state("dots"); r.shot("dots_grid", crop=900)
        elif exp == "life":
            for crit in ("0", "1"):
                r.pl.lines["c"].clear()
                r.cl(LIFE.replace("{{crit}}", crit)); r.pl.sleep(12)
                r.log.append(f"life crit={crit}\t" + " | ".join(l for l in r.pl.lines["c"] if "dotlife" in l))
        elif exp == "fire":
            g, target, dist = args[0], args[1], args[2]
            hook = args[3] if len(args) > 3 else "1"
            r.give(GUNS[g], 0, target=target, dist=dist, snap="1", secs="30")
            if os.environ.get("SR_HOOKED") != "1":
                print(r.cl(HOOK.replace("{{hook}}", hook)))
            r.state(f"{g} before"); r.shot(f"fire_{g}_{target}_{dist}_before")
            r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack")
            r.pl.sleep(float(os.environ.get("SR_DELAY", "0.1")))
            r.shot(f"fire_{g}_{target}_{dist}_after")
            r.pl.sleep(3)
        elif exp == "turn":
            r.give(GUNS["eva8"], 0, target="body", dist="300", snap="0", secs="30")
            r.cl(HOOK.replace("{{hook}}", "1"))
            r.key("+", "attack"); r.pl.sleep(0.05); r.key("-", "attack"); r.pl.sleep(0.1)
            r.shot("turn_0")
            r.sv('GetPlayerArray()[0].SnapEyeAngles( <0, 6, 0> ); AgentLink_Reply( "t" )'); r.pl.sleep(0.1)
            r.shot("turn_6")
        else:
            raise SystemExit("unknown experiment " + exp)
    finally:
        r.close()
        print("\n".join(r.log[-40:]))


if __name__ == "__main__":
    main()
