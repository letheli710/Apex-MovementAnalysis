#!/usr/bin/env python3
"""Iron sights, one gun at a time. No mouse, no focus; every picture is the engine `screenshot` command.

  py -3 -I capture.py <out dir> <gun> [<gun> ...]     guns: short names of bg_scan.json, or "all"

Two parts per gun, written to <out dir>/<gun>/:

A. PROP. The gun's own view model file as a client-side prop, in the air above the map with the sky behind it, view model hidden.
   Any camera angle is possible, and each sight bodygroup can be switched, so sights are picked out by the difference of two pictures.
   states: base  = the weapon script's default bodygroups (irons up, no optic)
           off   = every iron-sight bodygroup at 0 (what the optics mods do)
           none  = the prop hidden (background, for the silhouette)
           optic = off + sight_hcog_og on, if the model has it
   views:  side_full top_full eye   then for each sight (found from the side_full difference): side_<n> top_<n> back_<n> q34_<n>

B. VIEW MODEL. The real gun held: hip and aimed, with every attachment logged in the camera's frame. Switching bodygroups on the held view model does not stay (tried on the R-301), so the aimed picture is only taken as it is.
   eye() rebuilds the aimed picture with the prop but is not called: the world pass clips everything nearer than about 4 u, so the rear sight disappears.

meta.json holds the numbers each picture needs: focus point, camera distance, angles, attachments.
Gun frame: F forward from the muzzle attachment, R right, U up, R5 units. The prop is straight in its file: forward is its local x. meta.json logs the muzzle angles to check that.
"""
import glob, json, math, os, re, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sl import Link, SHOTDIR, Image  # noqa: E402

FPX = 611.0   # px per unit tangent, 1600 x 900, cl_fovScale 1.27 (fov 89): checked by calib.py
SKY_Z = 25000
HERE = os.path.dirname(os.path.abspath(__file__))
IRON = ("sight_front", "sight_rear", "sight_rear_on", "sight", "sight_on", "mastiff_sight", "sight_hcog_og")  # sight_hcog_og only for the optic state
ANG = {"side": (0, 90, 0), "top": (0, 90, -90), "back": (0, 0, 0), "q34": (-25, 40, 0)}


def basis(a):
    p, y, r = [math.radians(x) for x in a]
    sp, cp, sy, cy, sr, cr = math.sin(p), math.cos(p), math.sin(y), math.cos(y), math.sin(r), math.cos(r)
    f = (cp * cy, cp * sy, -sp)
    rt = (-sr * sp * cy + cr * sy, -sr * sp * sy - cr * cy, -sr * cp)
    u = (cr * sp * cy + sr * sy, cr * sp * sy - sr * cy, cr * cp)
    return f, rt, u


class Gun:
    def __init__(self, L, short, info, out):
        self.L, self.short, self.info, self.dir = L, short, info, os.path.join(out, short)
        os.makedirs(self.dir, exist_ok=True)
        self.meta = {"gun": short, "id": info["id"], "vm": info["vm"], "shots": {}, "attach": {}}

    # ---- prop
    def make_prop(self):
        L = self.L
        L.cl('SetConVarInt( "r_drawviewmodel", 0 ); SetConVarInt( "mat_fullbright", 1 ); SetConVarInt( "cl_drawhud", 0 )')
        L.sv(f'entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_NOCLIP ); p.SetOrigin( <-11699, 512, {SKY_Z}> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
        L.sleep(0.6)
        r = L.cl(f'''
var old = null
if ( "hsdP" in getroottable() ) old = getroottable().hsdP
if ( old != null ) {{ expect entity( old ); if ( IsValid( old ) ) old.Destroy() }}
entity q = CreateClientSidePropDynamic( <0, 0, {SKY_Z}>, <0, 0, 0>, $"{self.info["vm"]}" )
getroottable().hsdP <- q
vector o = q.GetOrigin()
for ( int i = 1 ; i < 90 ; i++ ) {{
	vector d = q.GetAttachmentOrigin( i )
	vector g = q.GetAttachmentAngles( i )
	if ( Length( d - o ) > 300.0 ) continue
	printt( format( "[RT] at i=%d p=%.3f,%.3f,%.3f g=%.2f,%.2f,%.2f", i, d.x - o.x, d.y - o.y, d.z - o.z, g.x, g.y, g.z ) )
}}
foreach ( n in {json.dumps(self.names())} ) printt( "[RT] name " + n + " " + q.LookupAttachment( n ) )
printt( "[RT] cam " + GetLocalClientPlayer().CameraPosition() )
''', 0.4)
        at, names = {}, {}
        for l in r:
            m = re.search(r"at i=(\d+) p=(\S+?),(\S+?),(\S+) g=(\S+?),(\S+?),(\S+)", l)
            if m:
                at[int(m[1])] = dict(p=[float(m[k]) for k in (2, 3, 4)], g=[float(m[k]) for k in (5, 6, 7)])
            m = re.search(r"name (\S+) (-?\d+)", l)
            if m:
                names[m[1]] = int(m[2])
            if "ERR" in l:
                print("  prop:", l, flush=True)
        self.meta["attach"] = at
        self.meta["attach_names"] = names
        self.muz = at[names["muzzle_flash"]]["p"] if names.get("muzzle_flash", -1) > 0 else None
        if self.muz is None:   # Sheila's mount and Vantage's ult: no muzzle_flash on the model, use the origin and say so
            for n in ("muzzle_flash_scoped", "muzzle", "barrel"):
                if names.get(n, -1) > 0:
                    self.muz = at[names[n]]["p"]; self.meta["muzzle_from"] = n; break
        if self.muz is None:
            self.muz = [0.0, 0.0, 0.0]; self.meta["muzzle_from"] = "model origin"
        self.meta["muz_local"] = self.muz
        cam = next(l for l in r if "cam <" in l)
        self.cam = [float(x) for x in re.search(r"<(.+?),(.+?),(.+?)>", cam).groups()]
        self.meta["cam"] = self.cam
        self.bg = {k: v["idx"] for k, v in self.info["bg"].items() if k in IRON or k == "scope_dcom"}
        self.dflt = {k: int(v["set"] or 0) for k, v in self.info["bg"].items() if k in self.bg}
        self.meta["bg"] = self.bg
        self.meta["bg_default"] = self.dflt

    def names(self):
        w = os.path.expanduser("~/Games/R5Flowstate/platform/scripts/weapons/")
        t = open(w + self.info["id"] + ".txt", encoding="utf-8", errors="replace").read().split('"Mods"')[0]
        n = set(re.findall(r'"[a-z_]*attachment[a-z_]*"\s+"([^"]+)"', t))
        n |= {"muzzle_flash", "muzzle_flash_scoped", "muzzle", "barrel", "SIGHT", "shell", "R_HAND", "L_HAND", "camera"}
        return sorted(n)

    def state(self, st):
        """Sets the prop's bodygroups. Default: 'base' = script defaults, optic off."""
        code = 'var q0 = getroottable().hsdP\nexpect entity( q0 )\nentity q = q0\n'
        if st == "none":
            code += "q.Hide()\n"
        else:
            code += "q.Show()\n"
            for k, i in self.bg.items():
                if st == "base":
                    v = self.dflt.get(k, 0)
                elif st == "off":
                    v = 0
                elif st == "optic":
                    v = 1 if k == "sight_hcog_og" else 0
                else:
                    v = 0
                code += f"q.SetBodygroupModelByIndex( {i}, {v} )\n"
        self.L.cl(code, 0.05)

    def has_iron(self):
        return any(k != "sight_hcog_og" and self.dflt.get(k) == 1 for k in self.bg)

    def pose(self, view, F, R, U, d, a=None):
        """Puts gun point (F, R, U) at distance d straight ahead of the camera, with the view's angles."""
        a = a or ANG[view]
        lx, ly, lz = self.muz[0] + F, self.muz[1] - R, self.muz[2] + U
        f, r, u = basis(a)
        o = [self.cam[k] + (d if k == 0 else 0) - (f[k] * lx - r[k] * ly + u[k] * lz) for k in range(3)]
        self.L.cl(f'var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.SetAngles( <{a[0]}, {a[1]}, {a[2]}> )\nq0.SetOrigin( <{o[0]:.4f}, {o[1]:.4f}, {o[2]:.4f}> )', 0.05)
        return dict(angles=a, focus=[F, R, U], d=d, origin=o)

    def snap(self, name, info):
        before = set(glob.glob(os.path.join(SHOTDIR, "*.tga")))
        self.L.sleep(0.12)
        self.L.cl('GetLocalClientPlayer().ClientCommand( "screenshot" )', 0.02)
        t, new = time.time(), []
        while time.time() - t < 6:
            self.L.sleep(0.1)
            new = [x for x in glob.glob(os.path.join(SHOTDIR, "*.tga")) if x not in before]
            if new:
                break
        if not new:
            raise TimeoutError("no screenshot " + name)
        self.L.sleep(0.25)
        im = Image.open(new[0]).convert("RGB")
        im.load()
        p = os.path.join(self.dir, name + ".png")
        im.save(p)
        os.remove(new[0])
        self.meta["shots"][name] = info
        return im

    def trio(self, name, info, states=("base", "off", "none")):
        ims = {}
        for st in states:
            if st == "off" and not self.has_iron():
                continue
            self.state(st)
            ims[st] = self.snap(f"{name}_{st}", dict(info, state=st))
        self.state("base")
        return ims

    def run_prop(self):
        self.make_prop()
        # first look: how long is the gun?
        v = self.pose("side", -30, 0, 0, 50)
        s = self.trio("side_wide", v, ("base", "none"))
        fmin, fmax = extent(s["base"], s["none"], 50, -30)
        self.meta["F_extent"] = [fmin, fmax]
        L = max(fmax - fmin, 6.0)
        # the world pass clips at about 7 u, so never closer than 12 to the gun's middle plane
        d = min(max(L * FPX / 1400.0, 12.0), 50.0)
        cF = (fmin + fmax) / 2
        v = self.pose("side", cF, 0, 0, d)
        side = self.trio("side_full", v)
        self.trio("top_full", self.pose("top", cF, 0, 0, max(d, 16.0)))
        self.meta["side_d"] = d
        # candidates: (1) what the sight bodygroups change in the outline, (2) where the outline comes up to the line of sight
        cl = []
        if "off" in side:
            cl = silhouette_clusters(side["base"], side["off"], side["none"], d, cF)
        self.meta["clusters"] = cl
        los = aim_line(self.meta)
        near = []
        if los:
            near = near_line(side["base"], side["none"], d, cF, los)
        self.meta["near_line"] = near
        foci = choose_foci(cl, near, MANUAL.get(self.short))
        self.meta["foci"] = foci
        print(f"  {self.short}: F {fmin:.1f}..{fmax:.1f} d {d:.1f} bg {cl} line {near} foci {foci}", flush=True)
        for k, fc in enumerate(foci):
            U = find_top(side["base"], side["none"], d, cF, fc[0], fc[1])
            self.meta.setdefault("focus_U", {})[str(k)] = U
            fm = (fc[0] + fc[1]) / 2
            dc = max(9.0, (fc[1] - fc[0]) * FPX / 1000.0)
            self.trio(f"side_{k}", self.pose("side", fm, 0, U - 0.8, dc))
            self.trio(f"top_{k}", self.pose("top", fm, 0, U, dc))
            self.trio(f"back_{k}", self.pose("back", fm, 0, U - 0.8, 11.0))
            self.state("base")
            self.snap(f"q34_{k}", dict(self.pose("q34", fm, 0, U - 0.5, 14.0), state="base"))
        if "sight_hcog_og" in self.bg:
            self.state("optic")
            self.snap("optic_side", dict(self.pose("side", cF, 0, 0, d), state="optic"))
            self.state("base")

    def eye(self):
        """The aimed picture rebuilt with the prop: the muzzle where the view model's muzzle is when aimed, straight, sky behind."""
        ads = self.meta.get("ads")
        names = self.meta.get("attach_names", {})
        if not ads or names.get("muzzle_flash", -1) not in ads:
            return
        m = ads[names["muzzle_flash"]]["p"]
        self.meta["aim_muzzle"] = m
        # gun point (0, 0, 0) at camera + (F, -R, U): the same as pose() with an offset
        f, r, u = basis(ANG["back"])
        lx, ly, lz = self.muz
        o = [self.cam[0] + m[0] - lx, self.cam[1] - m[1] + ly, self.cam[2] + m[2] - lz]
        self.L.cl(f"var q0 = getroottable().hsdP\nexpect entity( q0 )\nq0.SetAngles( <0, 0, 0> )\nq0.SetOrigin( <{o[0]:.4f}, {o[1]:.4f}, {o[2]:.4f}> )", 0.05)
        self.trio("eye", dict(angles=ANG["back"], origin=o, aim_muzzle=m))

    # ---- the real gun
    def run_vm(self, give=True):
        L = self.L
        if give:
            rep = L.give(self.info["id"])
            self.meta["give"] = rep
        L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 1 )')
        # on the ground and walking: ADS does not engage in noclip
        L.sv('entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_WALK ); p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
        L.sleep(1.2)
        SNAP = '''
entity p = GetLocalClientPlayer()
entity vm = p.GetViewModelEntity()
vector c = p.CameraPosition()
vector a = p.CameraAngles()
vector f = AnglesToForward( a )
vector r = AnglesToRight( a )
vector u = AnglesToUp( a )
printt( format( "[RT] st zf=%.3f fov=%.2f ca=%.2f,%.2f,%.2f model=", p.GetZoomFrac(), p.GetFOV(), a.x, a.y, a.z ) + vm.GetModelName() )
for ( int i = 1 ; i < 90 ; i++ ) {
	vector d = vm.GetAttachmentOrigin( i ) - c
	vector g = vm.GetAttachmentAngles( i )
	if ( Length( d ) > 300.0 ) continue
	printt( format( "[RT] at i=%d p=%.3f,%.3f,%.3f g=%.2f,%.2f,%.2f", i, DotProduct( d, f ), DotProduct( d, r ), DotProduct( d, u ), g.x - a.x, g.y - a.y, g.z - a.z ) )
}
'''
        def read():
            at, st = {}, ""
            for l in L.cl(SNAP, 0.3):
                m = re.search(r"at i=(\d+) p=(\S+?),(\S+?),(\S+) g=(\S+?),(\S+?),(\S+)", l)
                if m:
                    at[int(m[1])] = dict(p=[float(m[k]) for k in (2, 3, 4)], g=[float(m[k]) for k in (5, 6, 7)])
                if " st zf=" in l:
                    st = l.split("st ", 1)[1]
                if "ERR" in l:
                    print("  vm:", l, flush=True)
            return at, st
        self.meta["hip"], self.meta["hip_st"] = read()
        self.snap("vm_hip", dict(state="hip"))
        L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )', 0.1)
        t = time.time()
        zf = 0
        while time.time() - t < 3:
            r = L.cl('printt( "[RT] zf " + GetLocalClientPlayer().GetZoomFrac() )', 0.1)
            m = next((x for x in r if "zf " in x), "")
            try:
                zf = float(m.split("zf ")[1])
            except (IndexError, ValueError):
                zf = 0
            if zf >= 0.999:
                break
        L.sleep(0.5)
        self.meta["ads"], self.meta["ads_st"] = read()
        self.snap("vm_ads", dict(state="ads"))
        L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )', 0.3)
        L.sleep(0.5)

    def save(self):
        with open(os.path.join(self.dir, "meta.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.meta, f, indent=0)


# gun: [[F low, F high], ...] where the two lists above miss a sight or pick a rail. Placed by eye from the first run's pictures.
MANUAL = {
    "alternator": [[-5.2, -2.8], [-10.0, -8.2]],
    "bocek": [[-3.4, -0.3]],
    "chargerifle": [[-14.6, -12.3]],
    "flatline": [[-6.0, -2.0], [-14.0, -11.5], [-17.1, -14.9]],
    "havoc": [[-1.8, 1.0], [-20.5, -16.7]],
    "lstar": [[-1.8, 0.6], [-13.2, -11.0]],
    "re45": [[-1.8, 0.4], [-9.6, -7.4]],
    "tripletake": [[-25.5, -21.0], [-30.5, -26.0]],
    "r3030": [[-4.9, -3.5], [-29.9, -25.8]],
    "sheila": [[-24.0, -19.0], [-33.0, -27.0]],
    "mounted_turret": [[-24.0, -19.0], [-33.0, -27.0]],
    "vantage": [[-32.0, -22.0], [-16.0, -10.0]],
}


def diffmask(a, b, thr=14):
    import numpy as np
    A, B = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
    return (np.abs(A - B).max(axis=2) > thr)


def extent(base, none, d, cF):
    """F range of the gun in a side picture: column range of the difference to the empty sky, HUD lines ignored."""
    import numpy as np
    m = diffmask(base, none)
    m[:100] = False
    m[750:] = False
    cols = np.where(m.sum(axis=0) > 1)[0]
    x0, x1 = cols.min(), cols.max()
    s = FPX / d
    return cF - (x1 - 800) / s, cF - (x0 - 800) / s  # muzzle is to the left in a side view


def sight_clusters(base, off, d, cF, gap=1.2):
    """F ranges of the parts the iron bodygroups change, far ends first."""
    import numpy as np
    m = diffmask(base, off)
    m[:100] = False
    m[750:] = False
    cols = np.where(m.sum(axis=0) > 0)[0]
    if len(cols) == 0:
        return []
    s = FPX / d
    out, start, last = [], cols[0], cols[0]
    for x in cols[1:]:
        if (x - last) / s > gap:
            out.append((start, last))
            start = x
        last = x
    out.append((start, last))
    res = []
    for x0, x1 in out:
        if (x1 - x0) / s < 0.15:
            continue
        res.append([round(cF - (x1 - 800) / s, 2), round(cF - (x0 - 800) / s, 2)])
    return res


def find_top(base, none, d, cF, F0, F1=None):
    """Highest edge of the gun over the muzzle between F0 and F1 (side picture). The focus sits at U = 0."""
    import numpy as np
    m = diffmask(base, none)
    m[:100] = False
    m[755:] = False
    s = FPX / d
    F1 = F0 if F1 is None else F1
    x0, x1 = sorted((int(round(800 - (F0 - cF) * s)), int(round(800 - (F1 - cF) * s))))
    x0, x1 = max(x0 - 1, 0), min(x1 + 2, 1600)
    rows = np.where(m[:, x0:x1].sum(axis=1) > 0)[0]
    return 0.0 if len(rows) == 0 else float((450 - rows.min()) / s)


def spans(flags, s, cF, gap=0.8, minlen=0.15):
    """Runs of True columns, as [F low, F high]. gap and minlen in units."""
    import numpy as np
    cols = np.where(flags)[0]
    if len(cols) == 0:
        return []
    out, start, last = [], cols[0], cols[0]
    for x in cols[1:]:
        if (x - last) / s > gap:
            out.append((start, last))
            start = x
        last = x
    out.append((start, last))
    return [[float(round(cF - (x1 - 800) / s, 2)), float(round(cF - (x0 - 800) / s, 2))] for x0, x1 in out if (x1 - x0) / s >= minlen]


def silhouette_clusters(base, off, none, d, cF):
    """Where the outline changes with the iron bodygroups. Pixels inside the outline are not used: glow textures flicker between pictures (Peacekeeper, Sentinel)."""
    import numpy as np
    from scipy import ndimage as ndi
    a, b = diffmask(base, none, 18), diffmask(off, none, 18)
    m = a ^ b
    m[:100] = False
    m[755:] = False
    m = ndi.binary_opening(m, iterations=1)
    return spans(m.sum(axis=0) > 0, FPX / d, cF)


def aim_line(meta):
    n = meta.get("attach_names", {}).get("muzzle_flash", -1)
    ads = meta.get("ads") or {}
    m = ads.get(n) or ads.get(str(n))
    if not m:
        return None
    th = math.radians(m["g"][0])
    return (m["p"][0], m["p"][2], th)


def near_line(base, none, d, cF, los, margin=0.3):
    """Stretches of the gun whose top edge comes within margin of the line of sight, between the muzzle end and 3 u ahead of the eye."""
    import numpy as np
    m = diffmask(base, none, 18)
    m[:100] = False
    m[755:] = False
    s = FPX / d
    mF, mU, th = los
    tops = m.argmax(axis=0)
    has = m.any(axis=0)
    flags = np.zeros(1600, bool)
    for x in range(1600):
        if not has[x]:
            continue
        F = cF - (x - 800) / s
        if F < -(mF - 3):
            continue
        U = (450 - tops[x]) / s
        lineU = (-mU + F * math.sin(th)) / math.cos(th)
        flags[x] = U >= lineU - margin
    return spans(flags, s, cF, gap=0.6)


def choose_foci(cl, near, manual):
    """Close-up places, up to three, front first. Manual list wins; else long stretches are cut down to their two ends."""
    if manual:
        return manual
    pts = []
    for c in cl + near:
        if c[1] - c[0] > 8:   # a long rib: its two ends
            pts.append([c[1] - 3, c[1]])
            pts.append([c[0], c[0] + 3])
        else:
            pts.append(list(c))
    pts.sort(key=lambda c: -c[1])
    merged = []
    for c in pts:
        if merged and c[1] >= merged[-1][0] - 0.8:
            merged[-1] = [min(c[0], merged[-1][0]), max(c[1], merged[-1][1])]
        else:
            merged.append(list(c))
    if len(merged) > 3:
        merged = merged[:1] + sorted(merged[1:], key=lambda c: c[0] - c[1])[:1] + merged[-1:]
        merged.sort(key=lambda c: -c[1])
    return merged


def main():
    out = sys.argv[1]
    info = json.load(open(os.path.join(HERE, "bg_scan.json"), encoding="utf-8"))
    prior = None
    if sys.argv[2] == "--prior":   # keep the held-gun part of an earlier run: pictures and attachment logs
        prior = sys.argv[3]
        sys.argv = sys.argv[:2] + sys.argv[4:]
    guns = sys.argv[2:]
    if guns == ["all"]:
        guns = [g for g in info if g not in ("sheila", "mounted_turret", "vantage")]
    L = Link()
    for g in guns:
        if os.path.exists(os.path.join(out, g, "meta.json")):
            continue
        G = Gun(L, g, info[g], out)
        t = time.time()
        give = g not in ("mounted_turret", "vantage", "sheila")
        if give:
            L.give(info[g]["id"])   # precache the same way the game does
        try:
            if prior:
                pm = os.path.join(prior, g, "meta.json")
                if os.path.exists(pm):
                    old = json.load(open(pm, encoding="utf-8"))
                    for k in ("hip", "hip_st", "ads", "ads_st"):
                        if k in old:
                            G.meta[k] = old[k]
                    os.makedirs(G.dir, exist_ok=True)
                    for n in ("vm_hip", "vm_ads", "vm_ads_wall"):
                        src = os.path.join(prior, g, n + ".png")
                        if os.path.exists(src):
                            shutil.copyfile(src, os.path.join(G.dir, n + ".png"))
            elif give:
                G.bg = {k: v["idx"] for k, v in info[g]["bg"].items() if k in IRON}
                G.dflt = {k: int(v["set"] or 0) for k, v in info[g]["bg"].items() if k in G.bg}
                G.run_vm(give=False)
            G.run_prop()
        finally:
            G.save()
        print(g, "done", round(time.time() - t), "s", flush=True)
    L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 0 )')


if __name__ == "__main__":
    main()
