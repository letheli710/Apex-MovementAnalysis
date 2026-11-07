"""Weapon camera and timing from g_weap. Usage: an_weap.py <run dir>
Spring sim: x += hard * kick, v += soft * 20 * kick each shot (R5 rule, RECOIL-VIEW.md), x'' = -k x - d x'.
View shows (1 - weaponFraction) * punch (same doc)."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from g_tools import load, tags
import numpy as np

W = {  # file values: spring (k,d) hip, ADS; pitch base, random, soft, hard; yaw same; weaponFraction hip, ads; scale
    "monarch": dict(cls="mp_titanweapon_xo16_vanguard", hip=(55, 8), ads=(55, 8), pb=-0.2, pr=0.5, ps=0.5, ph=0.0, yb=0.2, yr=0.15, ys=0.5, yh=0.0, wf=0.7, wfa=0.6, smin=0.6, smax=1.0, sa=(0.3, 0.8), lerp=(5, 50), rate=12),
    "legion": dict(cls="mp_titanweapon_predator_cannon", hip=(35, 12), ads=(55, 15), pb=0.0, pr=0.46, ps=0.65, ph=2.0, yb=0.0, yr=1.0, ys=1.1, yh=1.35, wf=0.7, wfa=0.6, smin=1.0, smax=1.0, sa=(1.0, 1.0), lerp=(1, 2), rate=15),
    "ronin": dict(cls="mp_titanweapon_leadwall", hip=(300, 30), ads=(300, 30), pb=-2.25, pr=1.0, ps=6.0, ph=1.0, yb=-0.95, yr=0.5, ys=0.5, yh=2.0, wf=0.1, wfa=0.1, smin=1.0, smax=1.0, sa=(1.0, 1.0), lerp=(1, 2), rate=2.5),
}


def sim(w, shots, ads, axis="p", dur=4.0, dt=1 / 600.0):
    k, d = w["ads" if ads else "hip"]
    b, s, h = (w["pb"], w["ps"], w["ph"]) if axis == "p" else (w["yb"], w["ys"], w["yh"])
    x = v = 0.0
    ts = np.arange(0, dur, dt)
    out = np.zeros(len(ts))
    i = 0
    val = 0
    for n, t in enumerate(ts):
        while i < len(shots) and shots[i] <= t:
            val += 1
            f = np.clip((val - w["lerp"][0]) / (w["lerp"][1] - w["lerp"][0]), 0, 1)
            mn, mx = w["sa"] if ads else (w["smin"], w["smax"])
            sc = mn + (mx - mn) * f
            x += h * b * sc
            v += s * 20 * b * sc
            i += 1
        v += (-k * x - d * v) * dt
        x += v * dt
        out[n] = x
    return ts, out * (1 - (w["wfa"] if ads else w["wf"]))


def wrap(a):
    return (a + 180) % 360 - 180


d, c = load(sys.argv[1])
CAM = np.array([x[:8] for x in d['CAM']])
GW = d['GW']
GK = np.array([x[:14] for x in d['GK'] if len(x) >= 14])
T = {n: (a, b) for a, b, n in tags(c)}
for cls, w in W.items():
    print("=====", cls)
    g = [x for x in GW if x[1] == w["cls"]]
    if not g:
        print("no GW lines")
        continue
    t = np.array([x[0] for x in g])
    clip = np.array([x[2] for x in g])
    rel = np.array([x[3] for x in g])
    zf = np.array([x[4] for x in g])
    ads = np.array([x[5] for x in g])
    fov = np.array([x[6] for x in g])
    vm = np.array([x[7:13] if len(x) >= 13 else [0] * 6 for x in g])
    mz = np.array([x[13:16] if len(x) >= 16 else [0] * 3 for x in g])

    def win(n):
        return T.get("wp_%s_%s" % (cls, n), (0, 0))

    # shots from clip drops
    def shots(a, b):
        s = (t >= a) & (t < b)
        ii = np.where(s)[0]
        return [t[i] for i in ii[1:] if clip[i] < clip[i - 1]]

    for n, ad in (("tap", False), ("burst", False), ("hold", False), ("adshold", True)):
        a, b = win(n)
        if not a:
            continue
        sh = shots(a, b)
        K = CAM[(CAM[:, 0] >= a) & (CAM[:, 0] < b)]
        tk = K[:, 0]
        p = K[:, 2] - K[0, 2]
        y = wrap(K[:, 3] - K[0, 3])
        r = K[:, 4] - K[0, 4]
        dx = np.abs(K[:, 5:8] - K[0, 5:8]).max(0)
        if not sh:
            print(n, "no shots")
            continue
        rate = (len(sh) - 1) / (sh[-1] - sh[0]) if len(sh) > 1 else 0
        tsim, ps = sim(w, [q - a for q in sh], ad, "p", dur=b - a)
        _, ys = sim(w, [q - a for q in sh], ad, "y", dur=b - a)
        i1 = np.where(tk > sh[-1])[0]
        rec = p[i1] if len(i1) else np.zeros(1)
        back = tk[i1][np.where(np.abs(rec) < 0.1)[0][0]] - sh[-1] if len(i1) and (np.abs(rec) < 0.1).any() else -1
        print(f"{n:8s} shots={len(sh)} first@{sh[0] - a:.3f} last@{sh[-1] - a:.3f} rate={rate:.1f}/s | pitch min {p.min():+.2f} @{tk[np.argmin(p)] - a:.2f} max {p.max():+.2f} end {p[-1]:+.2f} | yaw {y.min():+.2f}..{y.max():+.2f} | roll {r.min():+.2f}..{r.max():+.2f} | pos {np.round(dx, 2)} | sim pitch min {ps.min():+.2f} yaw {ys.min():+.2f}..{ys.max():+.2f} | back<0.1 after last {back:.2f}")
        Gk = GK[(GK[:, 0] >= a) & (GK[:, 0] < b)]
        if len(Gk):
            print("         cockpit CAMERA attach vs camera f r u p y r range", np.round(np.ptp(Gk[:, 2:8], axis=0), 2))
        s = (t >= a) & (t < b)
        if s.any():
            print("         vm f r u p y r range", np.round(np.ptp(vm[s], axis=0), 2), "muzzle rel cam mean", np.round(mz[s].mean(0), 1), "range", np.round(np.ptp(mz[s], axis=0), 2))
        if n == "tap" or n == "burst":
            i0 = np.searchsorted(tk, sh[0])
            ss = [f"{tk[j] - sh[0]:.2f}:{p[j]:+.2f}" for j in range(i0, min(i0 + 70, len(tk)), 7)]
            print("         curve", " ".join(ss))
            ss2 = [f"{tq:.2f}:{ps[np.searchsorted(tsim, tq + sh[0] - a)]:+.2f}" for tq in np.arange(0, 0.5, 0.05) if tq + sh[0] - a < tsim[-1]]
            print("         sim  ", " ".join(ss2))
    # reload
    on = [i for i in range(1, len(t)) if rel[i] and not rel[i - 1]]
    off = [i for i in range(1, len(t)) if not rel[i] and rel[i - 1]]
    for i in on:
        j = next((q for q in off if q > i), None)
        if j is None:
            continue
        full = next((q for q in range(i, j + 1) if clip[q] > clip[i]), None)
        print(f"reload start {t[i]:.2f} clip {clip[i]:.0f} -> flag off after {t[j] - t[i]:.3f} s, clip {clip[j]:.0f}; clip refilled at {(t[full] - t[i]) if full else -1:.3f} s")
    # zoom
    for n in ("adsin", "adsout"):
        a, b = win(n)
        s = (t >= a) & (t < b)
        if not s.any():
            continue
        tt = t[s] - a
        z = zf[s]
        mv = np.where(np.abs(np.diff(z)) > 1e-4)[0]
        if len(mv):
            print(f"{n}: zoomFrac {z[0]:.2f}->{z[-1]:.2f} moves {tt[mv[0]]:.3f}..{tt[mv[-1] + 1]:.3f} ({tt[mv[-1] + 1] - tt[mv[0]]:.3f} s), fov {fov[s][0]:.1f}->{fov[s][-1]:.1f}")
            idx = np.linspace(mv[0], mv[-1] + 1, 9).astype(int)
            print("   z:", " ".join(f"{z[i]:.2f}" for i in idx), "| ads:", " ".join(f"{ads[s][i]:.2f}" for i in idx), "| fov:", " ".join(f"{fov[s][i]:.1f}" for i in idx))
            print("   vm:", np.round(vm[s][mv[0]], 2), "->", np.round(vm[s][mv[-1] + 1], 2), "muzzle", np.round(mz[s][mv[0]], 1), "->", np.round(mz[s][mv[-1] + 1], 1))
    a, b = win("reloadcut")
    if a:
        s = (t >= a) & (t < b)
        ii = np.where(s)[0]
        ev = [(round(t[i] - a, 3), int(clip[i]), int(rel[i])) for i in ii[1:] if rel[i] != rel[i - 1] or clip[i] != clip[i - 1]]
        print("reloadcut events (t, clip, reloading):", ev[:16])
