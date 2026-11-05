#!/usr/bin/env python3
"""How big does R5 draw the held gun with an optic fitted? Same method as vmcal2.py:
  held gun picture, then the same .rmdl with the same bodygroups as a world prop on the same pose (world FOV known), then neither.
The scale between the held outline and the prop outline gives the view model's px/tan (optic_fit.py).
Also a side and a top view of each optic part in the sky, for where it sits on the gun.
  py -3 -I optic_probe.py <out dir> <gun> <mod> [<mod> ...]     mod = none for the iron sights
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vmcal import INFO, Link, shot, prop
from capture import basis, ANG

HERE = os.path.dirname(os.path.abspath(__file__))
OPT = {r["gun"] + "/" + r["mod"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "IS-OPTICS.tsv"), encoding="utf-8"), delimiter="\t")}
SKY = 25000


def sets(gun, mod):
    r = OPT[f"{gun}/{mod if mod != 'none' else '(iron)'}"]
    on = [x for x in r["bodygroup_on"].split(",") if x]
    off = [x for x in r["bodygroup_off"].split(",") if x]
    names = [k for k in INFO[gun]["bg"] if k.startswith(("sight", "scope"))]
    st = {k: int(INFO[gun]["bg"][k].get("set") or 0) for k in names}
    for k in off:
        if k in st:
            st[k] = 0
    for k in on:
        if k in st:
            st[k] = 1
    return st, r


def setbg(L, st):
    code = "var q0 = getroottable().hsdP\nexpect entity( q0 )\n"
    for k, v in st.items():
        code += f'q0.SetBodygroupModelByIndex( q0.FindBodygroup( "{k}" ), {v} )\n'
    L.cl(code, 0.1)


def read(L, center):
    r = L.cl(f'''
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
int j = vm.LookupAttachment( "{center}" )
vector e = vm.GetAttachmentOrigin( j ) - c
entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
string md = ""
foreach ( mn in w.GetMods() ) md += mn + ","
printt( format( "[RT] v m=%.3f,%.3f,%.3f g=%.3f,%.3f,%.3f c=%.3f,%.3f,%.3f fov=%.3f zf=%.3f e=%.3f,%.3f,%.3f", DotProduct( d, f ), DotProduct( d, rr ), DotProduct( d, u ), g.x, g.y, g.z, c.x, c.y, c.z, p.GetFOV(), p.GetZoomFrac(), DotProduct( e, f ), DotProduct( e, rr ), DotProduct( e, u ) ) )
printt( "[RT] w zoom_fov=" + w.GetWeaponSettingFloat( eWeaponVar.zoom_fov ) + " vm=" + w.GetWeaponSettingFloat( eWeaponVar.zoom_fov_viewmodel ) + " mods=" + md )
''', 0.3)
    print("  ", [x.split("[RT]")[-1] for x in r if "[RT]" in x or "ERR" in x], flush=True)
    m = next(x for x in r if " v m=" in x)
    a = re.search(r"m=(\S+?),(\S+?),(\S+) g=(\S+?),(\S+?),(\S+) c=(\S+?),(\S+?),(\S+) fov=(\S+) zf=(\S+) e=(\S+?),(\S+?),(\S+)", m)
    v = [float(a[k]) for k in range(1, 15)]
    w = next((x for x in r if " w zoom_fov=" in x), "")
    return v, w.split("[RT]")[-1].strip()


def make(L, gun):
    r = L.cl(f'''
var old = null
if ( "hsdP" in getroottable() ) old = getroottable().hsdP
if ( old != null ) {{ expect entity( old ); if ( IsValid( old ) ) old.Destroy() }}
entity q = CreateClientSidePropDynamic( <0, 0, 25000>, <0, 0, 0>, $"{INFO[gun]["vm"]}" )
getroottable().hsdP <- q
int i = q.LookupAttachment( "muzzle_flash" )
vector d = q.GetAttachmentOrigin( i ) - q.GetOrigin()
vector a = q.GetAttachmentAngles( i )
printt( format( "[RT] ml %.3f,%.3f,%.3f %.3f,%.3f,%.3f", d.x, d.y, d.z, a.x, a.y, a.z ) )
q.Hide()
''', 0.3)
    a = re.search(r"ml (\S+?),(\S+?),(\S+) (\S+?),(\S+?),(\S+)", next(x for x in r if " ml " in x))
    return [float(a[k]) for k in (1, 2, 3)], [float(a[k]) for k in (4, 5, 6)]


def sky(L, gun, st, ml, out, tag, cam):
    """Side and top views of the prop with these bodygroups, centred on F -22 at d = 40 (611 px/tan at cl_fovScale 1.27)."""
    Fc, Uc, d = -22.0, 2.0, 40.0
    res = {}
    for view in ("side", "top"):
        a = ANG[view]
        f, rt, u = basis(a)
        mlF, mlR, mlU = ml[0], -ml[1], ml[2]
        tg = (cam[0] + d, cam[1], cam[2])
        uc = Uc if view == "side" else 0
        o = [tg[k] - f[k] * (mlF + Fc) - rt[k] * mlR - u[k] * (mlU + uc) for k in range(3)]
        L.cl(f'var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Show()\nq0.SetModelScale( 1.0 )\nq0.SetAngles( <{a[0]}, {a[1]}, {a[2]}> )\nq0.SetOrigin( <{o[0]:.3f}, {o[1]:.3f}, {o[2]:.3f}> )', 0.15)
        setbg(L, st)
        shot(L, os.path.join(out, f"{tag}_{view}.png"))
        res[view] = dict(Fc=Fc, Uc=uc, d=d)
    return res


K = 3.0  # the prop is K times larger and K times further from the camera: same perspective, and nothing nearer than the world pass's near clip (7 u)


def far_prop(L, v, base, ml):
    m, g, c = v[0:3], v[3:6], v[6:9]
    a = [g[0] - base[0], g[1] - base[1], g[2] - base[2]]
    f, r, u = basis(a)
    w = [c[k] + (m[0] if k == 0 else 0) + (-m[1] if k == 1 else 0) + (m[2] if k == 2 else 0) for k in range(3)]
    o = [w[k] - (f[k] * ml[0] - r[k] * ml[1] + u[k] * ml[2]) for k in range(3)]
    off = [K * (o[k] - c[k]) for k in range(3)]
    # the camera shakes a little while the server holds the player in the air: a client loop keeps the prop on the camera, frame by frame
    L.cl(f"""var q0 = getroottable().hsdP
expect entity( q0 )
q0.Show()
q0.SetModelScale( {K} )
q0.SetAngles( <{a[0]:.3f}, {a[1]:.3f}, {a[2]:.3f}> )
getroottable().hsdOff <- <{off[0]:.3f}, {off[1]:.3f}, {off[2]:.3f}>
if ( !( "hsdLoop" in getroottable() ) ) {{
    getroottable().hsdLoop <- 1
    void functionref() lf = void function() {{
        try {{
            float t0 = Time()
            while ( Time() - t0 < 1500.0 ) {{
                var q1 = getroottable().hsdP
                var o1 = getroottable().hsdOff
                if ( q1 != null && o1 != null ) {{
                    expect entity( q1 )
                    expect vector( o1 )
                    if ( IsValid( q1 ) ) q1.SetOrigin( GetLocalClientPlayer().CameraPosition() + o1 )
                }}
                WaitFrame()
            }}
        }} catch ( e3 ) {{ printt( "[RT] loop " + e3 ) }}
    }}
    thread lf()
}}""", 0.2)


def main():
    out, gun = sys.argv[1:3]
    os.makedirs(out, exist_ok=True)
    L = Link()
    info = INFO[gun]
    res = {}
    L.give(info["id"])
    ml, base = make(L, gun)
    L.cl('getroottable().hsdOff <- null', 0.05)
    print("ml", ml, base, flush=True)
    # sky views first: every state, plus all sights off as the reference
    L.cl('SetConVarFloat( "cl_fovScale", 1.27 ); SetConVarInt( "r_drawviewmodel", 0 ); SetConVarInt( "mat_fullbright", 1 ); SetConVarInt( "cl_drawhud", 0 )')
    L.sv(f'entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_NOCLIP ); p.SetOrigin( <-11699, 512, {SKY}> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
    L.sleep(0.8)
    r = L.cl('vector c = GetLocalClientPlayer().CameraPosition()\nprintt( format( "[RT] cc %.3f,%.3f,%.3f", c.x, c.y, c.z ) )', 0.3)
    cam = [float(x) for x in re.search(r"cc (\S+?),(\S+?),(\S+)", next(x for x in r if " cc " in x)).groups()]
    names = [k for k in info["bg"] if k.startswith(("sight", "scope"))]
    res["_sky"] = sky(L, gun, {k: 0 for k in names}, ml, out, "sky_alloff", cam)
    L.cl('var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Hide()', 0.1)
    shot(L, os.path.join(out, "sky_noprop.png"))
    for mod in sys.argv[3:]:
        st, _ = sets(gun, mod)
        sky(L, gun, st, ml, out, f"sky_{mod}", cam)
    L.cl('var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Hide()', 0.1)
    # held, at both FOV scales: the code has two branches and only one of them depends on the world's FOV
    for mod in sys.argv[3:]:
        st, row = sets(gun, mod)
        center = row["viewmodel_ads_centerpoint_attachment"] or OPT[f"{gun}/(iron)"]["viewmodel_ads_centerpoint_attachment"]  # sniper scopes keep the gun's own
        L.give(info["id"], mod)
        L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 1 ); SetConVarInt( "cl_drawhud", 0 )')
        # walking physics (aiming does not engage in noclip) but held in the sky: a clean background, no depth of field edges against the world
        L.sv(f'''entity p = GetPlayerArray()[0]
p.SetPhysics( MOVETYPE_WALK )
p.SnapEyeAngles( <0, 0, 0> )
void functionref() lf = void function() : ( p ) {{
    try {{
        float t0 = Time()
        while ( Time() - t0 < 130.0 ) {{
            p.SetOrigin( <-11699, 512, {SKY}> )
            p.SetVelocity( <0, 0, 0> )
            WaitFrame()
        }}
    }} catch ( e2 ) {{ }}
}}
thread lf()''')
        L.sleep(1.0)
        setbg(L, st)
        res[mod] = {}
        for S in (1.0, 1.27):
            L.cl(f'SetConVarFloat( "cl_fovScale", {S} )', 0.3)
            for mode in ("hip", "ads"):
                tag = f"{mod}_{mode}_S{S}"
                L.cl('SetConVarInt( "r_drawviewmodel", 1 )\nvar q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.Hide()', 0.1)
                if mode == "ads":
                    L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )', 0.1)
                    L.sleep(1.6)
                else:
                    L.sleep(0.8)
                v, wl = read(L, center)
                shot(L, os.path.join(out, f"{tag}_vm.png"))
                L.cl('SetConVarInt( "r_drawviewmodel", 0 )', 0.1)
                shot(L, os.path.join(out, f"{tag}_none.png"))
                far_prop(L, v, base, ml)
                shot(L, os.path.join(out, f"{tag}_prop.png"))
                res[mod][f"{mode}_S{S}"] = dict(S=S, muzzle=v[0:3], g=v[3:6], fov=v[9], zf=v[10], center=v[11:14], weapon=wl, sets=st)
                print(gun, tag, "fov", v[9], "zf", v[10], "muzzle", v[0:3], "center", v[11:14], flush=True)
            L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )\nSetConVarInt( "r_drawviewmodel", 1 )', 0.5)
            L.sleep(0.6)
    L.cl('SetConVarFloat( "cl_fovScale", 1.27 ); SetConVarInt( "cl_drawhud", 1 ); SetConVarInt( "mat_fullbright", 0 )')
    with open(os.path.join(out, "optic.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)


main()
