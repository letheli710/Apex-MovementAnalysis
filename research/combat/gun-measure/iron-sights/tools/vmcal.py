#!/usr/bin/env python3
"""How big does the engine draw the view model, against the world? Same frame, same pose, two pictures:
  A  the held gun (view model pass)
  B  view model hidden, the same .rmdl as a world prop placed where the attachments say the held gun is (world pass, whose FOV is known)
The ratio of sizes between A and B is the view model pass's scale against the world pass. Run for hip and aimed.

  py -3 -I vmcal.py <out dir> <gun> [<gun> ...]
"""
import json, math, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl import Link, SHOTDIR, Image  # noqa: E402
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
INFO = json.load(open(os.path.join(HERE, "bg_scan.json"), encoding="utf-8"))


def shot(L, path):
    before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
    L.sleep(0.12)
    L.cl('GetLocalClientPlayer().ClientCommand( "screenshot" )', 0.02)
    t, new = time.time(), []
    while time.time() - t < 6:
        L.sleep(0.1)
        new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
        if new:
            break
    L.sleep(0.25)
    im = Image.open(new[0]).convert("RGB")
    im.load()
    im.save(path)
    os.remove(new[0])


def read(L):
    r = L.cl('''
entity p = GetLocalClientPlayer()
entity vm = p.GetViewModelEntity()
vector c = p.CameraPosition()
vector a = p.CameraAngles()
vector f = AnglesToForward( a )
vector rr = AnglesToRight( a )
vector u = AnglesToUp( a )
int i = vm.LookupAttachment( "muzzle_flash" )
vector d = vm.GetAttachmentOrigin( i ) - c
vector g = vm.GetAttachmentAngles( i )
printt( format( "[RT] v m=%.3f,%.3f,%.3f g=%.3f,%.3f,%.3f c=%.3f,%.3f,%.3f fov=%.3f zf=%.3f", DotProduct( d, f ), DotProduct( d, rr ), DotProduct( d, u ), g.x, g.y, g.z, c.x, c.y, c.z, p.GetFOV(), p.GetZoomFrac() ) )
''', 0.25)
    m = next(x for x in r if " v m=" in x)
    a = re.search(r"m=(\S+?),(\S+?),(\S+) g=(\S+?),(\S+?),(\S+) c=(\S+?),(\S+?),(\S+) fov=(\S+) zf=(\S+)", m)
    return [float(a[k]) for k in range(1, 12)]


def prop(L, vm, m, g, base, c, ml):
    """Prop with the muzzle at camera + m (F, R, U), gun angles = muzzle angles - the model's own muzzle angles (small angles: fine for this)."""
    a = [g[0] - base[0], g[1] - base[1], g[2] - base[2]]
    th, ya, ro = [math.radians(x) for x in a]
    # local muzzle in world, from the angles
    from capture import basis
    f, r, u = basis(a)
    w = [c[k] + (m[0] if k == 0 else 0) + (-m[1] if k == 1 else 0) + (m[2] if k == 2 else 0) for k in range(3)]
    o = [w[k] - (f[k] * ml[0] - r[k] * ml[1] + u[k] * ml[2]) for k in range(3)]
    L.cl(f'var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Show()\nq0.SetAngles( <{a[0]:.3f}, {a[1]:.3f}, {a[2]:.3f}> )\nq0.SetOrigin( <{o[0]:.3f}, {o[1]:.3f}, {o[2]:.3f}> )', 0.1)
    return a


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    L = Link()
    res = {}
    for g in sys.argv[2:]:
        info = INFO[g]
        L.give(info["id"])
        L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 1 )')
        L.sv('entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_WALK ); p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
        L.sleep(1.0)
        r = L.cl(f'''
var old = null
if ( "hsdP" in getroottable() ) old = getroottable().hsdP
if ( old != null ) {{ expect entity( old ); if ( IsValid( old ) ) old.Destroy() }}
entity q = CreateClientSidePropDynamic( <0, 0, 25000>, <0, 0, 0>, $"{info["vm"]}" )
getroottable().hsdP <- q
foreach ( nk in {json.dumps([k for k in info["bg"] if k in ("sight_front","sight_rear","sight_rear_on","sight","sight_on","mastiff_sight")])} ) q.SetBodygroupModelByIndex( q.FindBodygroup( nk ), 1 )
int i = q.LookupAttachment( "muzzle_flash" )
vector d = q.GetAttachmentOrigin( i ) - q.GetOrigin()
vector a = q.GetAttachmentAngles( i )
printt( format( "[RT] ml %.3f,%.3f,%.3f %.3f,%.3f,%.3f", d.x, d.y, d.z, a.x, a.y, a.z ) )
q.Hide()
''', 0.3)
        m0 = next(x for x in r if " ml " in x)
        a = re.search(r"ml (\S+?),(\S+?),(\S+) (\S+?),(\S+?),(\S+)", m0)
        ml, base = [float(a[k]) for k in (1, 2, 3)], [float(a[k]) for k in (4, 5, 6)]
        # the prop's world numbers: x forward; local y is left, already what GetAttachmentOrigin gives at zero angles
        ml2 = ml
        res[g] = {}
        for mode in ("hip", "ads"):
            L.cl('SetConVarInt( "r_drawviewmodel", 1 )\nvar q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Hide()', 0.1)
            if mode == "ads":
                L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )', 0.1)
                L.sleep(1.5)
            else:
                L.sleep(0.8)
            v = read(L)
            shot(L, os.path.join(out, f"{g}_{mode}_vm.png"))
            L.cl('SetConVarInt( "r_drawviewmodel", 0 )', 0.05)
            pa = prop(L, info["vm"], v[0:3], v[3:6], base, v[6:9], ml2)
            shot(L, os.path.join(out, f"{g}_{mode}_prop.png"))
            res[g][mode] = dict(muzzle=v[0:3], g=v[3:6], cam=v[6:9], fov=v[9], zf=v[10], prop_angles=pa)
            print(g, mode, res[g][mode], flush=True)
        L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )\nSetConVarInt( "r_drawviewmodel", 1 )', 0.5)
        L.cl('var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Destroy()', 0.1)
    with open(os.path.join(out, "vmcal.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
