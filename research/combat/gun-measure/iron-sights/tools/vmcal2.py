#!/usr/bin/env python3
"""Second calibration: with cl_fovScale 1 the world's FOV is the weapon's own (70 at the hip, zoom_fov aimed). If the view model pass uses those same numbers, the held gun and the world prop on the same pose should lie on top of each other.
Also prints the world scale by moving a prop by a known distance. py -3 -I vmcal2.py <out dir> <gun> ..."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vmcal import *  # noqa
import numpy as np


def main2():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    L = Link()
    # world scale: known move, fov 89
    L.give(INFO["r301"]["id"])
    L.cl('SetConVarFloat( "cl_fovScale", 1.27 ); SetConVarInt( "r_drawviewmodel", 0 ); SetConVarInt( "mat_fullbright", 1 )')
    L.sv(f'entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_NOCLIP ); p.SetOrigin( <-11699, 512, 25000> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
    L.sleep(0.8)
    r = L.cl(f'''
var old = null
if ( "hsdP" in getroottable() ) old = getroottable().hsdP
if ( old != null ) {{ expect entity( old ); if ( IsValid( old ) ) old.Destroy() }}
entity q = CreateClientSidePropDynamic( <0, 0, 25000>, <0, 0, 0>, $"{INFO["r301"]["vm"]}" )
getroottable().hsdP <- q
vector c = GetLocalClientPlayer().CameraPosition()
printt( format( "[RT] cc %.3f,%.3f,%.3f fov=%.3f", c.x, c.y, c.z, GetLocalClientPlayer().GetFOV() ) )
''', 0.3)
    cam = [float(x) for x in re.search(r"cc (\S+?),(\S+?),(\S+)", next(x for x in r if " cc " in x)).groups()]
    print(r)
    pts = {}
    for name, dy, d in (("none", None, 0), ("a", 0, 25.0), ("b", 8, 25.0), ("c", 0, 50.0)):
        if dy is None:
            L.cl('var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Hide()', 0.1)
        else:
            L.cl(f'var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Show()\nq0.SetAngles( <0, 90, 0> )\nq0.SetOrigin( <{cam[0]+d}, {cam[1]-20+dy}, {cam[2]+14}> )', 0.1)
        p = os.path.join(out, f"cal_{name}.png")
        shot(L, p)
        pts[name] = np.asarray(Image.open(p), dtype=np.int16)
    def bb(a):
        m = np.abs(a - pts["none"]).max(axis=2) > 14
        m[:100] = False
        m[755:] = False
        ys, xs = np.where(m)
        return xs.min(), xs.max(), ys.min(), ys.max()
    ba, bb2, bc = bb(pts["a"]), bb(pts["b"]), bb(pts["c"])
    print("bbox", ba, bb2, bc)
    # +8 world y moves left on screen by 8 * f / d
    print("world f at fov 89, x shift:", (ba[0] - bb2[0]) * 25.0 / 8, (ba[1] - bb2[1]) * 25.0 / 8)
    print("world f from size ratio d=25 vs 50 (should be 2):", (ba[1] - ba[0]) / (bc[1] - bc[0]))
    # same pose, fov scale 1
    L.cl('SetConVarFloat( "cl_fovScale", 1.0 )', 0.2)
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
        a = re.search(r"ml (\S+?),(\S+?),(\S+) (\S+?),(\S+?),(\S+)", next(x for x in r if " ml " in x))
        ml, base = [float(a[k]) for k in (1, 2, 3)], [float(a[k]) for k in (4, 5, 6)]
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
            prop(L, info["vm"], v[0:3], v[3:6], base, v[6:9], ml)
            shot(L, os.path.join(out, f"{g}_{mode}_prop.png"))
            print(g, mode, "fov", v[9], "zf", v[10], "muzzle", v[0:3], flush=True)
        L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )\nSetConVarInt( "r_drawviewmodel", 1 )', 0.5)
        L.cl('var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Destroy()\ngetroottable().hsdP <- null', 0.1)
    L.cl('SetConVarFloat( "cl_fovScale", 1.27 )')


main2()
