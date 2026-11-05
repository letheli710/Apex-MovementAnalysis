#!/usr/bin/env python3
"""From optic_probe.py's pictures: the view model's scale for each optic.

Scale of the held outline against the prop outline, about the screen centre. The prop is the same model on the same pose with a known world FOV,
so held px/tan = scale x prop px/tan. Fine search over scale and a small shift, top edge of the outline only: arms and hands are in the held picture and not in the prop,
but they never form the top edge in the middle of the screen.

Also S127_over_S1: the held outline at cl_fovScale 1.27 against itself at 1.0. Needs no prop. 1.00 = a fixed number, above 1 = follows the world's FOV.
  py -3 -I optic_fit.py <dir> <out.tsv>
"""
import json, math, os, sys
import numpy as np
from scipy import ndimage
from PIL import Image

D, OUT = sys.argv[1:3]
meta = json.load(open(os.path.join(D, "optic.json"), encoding="utf-8"))


def load(n):
    return np.asarray(Image.open(os.path.join(D, n + ".png")).convert("RGB"), dtype=np.int16)


def mask(a, b, th=7):
    """What differs from the same view with no gun, in the sky: the solid outline, specks removed, holes filled."""
    m = np.abs(a - b).max(axis=2) > th
    m[:90] = False  # the score board
    m[755:] = False  # HUD row
    m = ndimage.binary_opening(m, np.ones((3, 3), bool))
    m = ndimage.binary_closing(m, np.ones((5, 5), bool))
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n == 0:
        return m
    return lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))


def top_edge(m):
    """For each column, the first row of the largest vertical run of the outline, -1 if the column is empty."""
    out = np.full(m.shape[1], -1.0)
    for x in range(m.shape[1]):
        r = np.where(m[:, x])[0]
        if len(r) >= 6:
            # ignore specks above the body: first row that starts a run of 4
            for y in r:
                if m[y:y + 4, x].all():
                    out[x] = y
                    break
    return out


def fit(ea, eb, lo, hi, n=240):
    """Scale s and shift of edge b onto edge a: rows and columns about the centre. Median absolute error in pixels."""
    xs = np.arange(1600)
    best = (1e9, 1, 0, 0, 0)
    okb = eb >= 0
    bx, by = xs[okb] - 800.0, eb[okb] - 450.0
    if len(bx) < 20:
        return best
    for s in np.geomspace(lo, hi, n):
        px, py = bx * s + 800, by * s + 450
        for dx in range(-24, 25, 4):
            ix = np.round(px + dx).astype(int)
            k = (ix >= 0) & (ix < 1600)
            if k.sum() < 20:
                continue
            ya = ea[ix[k]]
            g = ya >= 0
            if g.sum() < 0.6 * k.sum():
                continue
            diff = ya[g] - py[k][g]
            dy = np.median(diff)
            e = np.median(np.abs(diff - dy))
            if e < best[0]:
                best = (e, s, dx, dy, int(g.sum()))
    return best


def warp(m, s):
    h, w = m.shape
    ys, xs = np.mgrid[0:h, 0:w]
    sx = ((xs - w / 2) / s + w / 2).round().astype(int)
    sy = ((ys - h / 2) / s + h / 2).round().astype(int)
    ok = (sx >= 0) & (sx < w) & (sy >= 0) & (sy < h)
    o = np.zeros_like(m)
    o[ok] = m[sy[ok], sx[ok]]
    return o


def iou_fit(a, b, lo, hi, n=70):
    """Scale of the prop's outline b onto the held outline a. Rows below 640 are left out: hands. Returns (1 - IoU, s, dx, dy, pixels)."""
    a2, b2 = a[::2, ::2].copy(), b[::2, ::2]
    a2[320:] = False
    best = (2, 1, 0, 0, 0)
    for s in np.geomspace(lo, hi, n):
        w0 = warp(b2, s)
        w0[320:] = False
        for dy in range(-16, 17, 4):
            for dx in range(-16, 17, 4):
                w1 = np.roll(np.roll(w0, dy, 0), dx, 1)
                u = (a2 | w1).sum()
                v = 1 - (a2 & w1).sum() / u if u else 2
                if v < best[0]:
                    best = (float(v), float(s), dx * 2, dy * 2, int(u))
    s0 = best[1]
    for s in np.linspace(s0 * 0.985, s0 * 1.015, 13):
        w0 = warp(b2, s)
        w0[320:] = False
        for dy in range(best[3] // 2 - 4, best[3] // 2 + 5):
            for dx in range(best[2] // 2 - 4, best[2] // 2 + 5):
                w1 = np.roll(np.roll(w0, dy, 0), dx, 1)
                u = (a2 | w1).sum()
                v = 1 - (a2 & w1).sum() / u if u else 2
                if v < best[0]:
                    best = (float(v), float(s), dx * 2, dy * 2, int(u))
    return best


def f4(fov):
    return 600.0 / math.tan(math.radians(fov) / 2)


def code_fov(R, Rb, vmf):
    """What the decompiled code says: a written zoom_fov_viewmodel is used as it is, otherwise the hip's 70 follows the world's tangent ratio."""
    if vmf > 0:
        return f4(vmf)
    return 600.0 / (math.tan(math.radians(35)) * math.tan(math.radians(R) / 2) / math.tan(math.radians(Rb) / 2))


rows = []
for mod, st in meta.items():
    if mod.startswith("_") or "--extents" in sys.argv:
        continue
    held = {}
    for key, r in st.items():
        tag = f"{mod}_{key}"
        vm, no, pr = load(tag + "_vm"), load(tag + "_none"), load(tag + "_prop")
        mv, mp = mask(vm, no), mask(pr, no)
        held[key] = mv
        R = r["fov"]
        Rb = 70.0 if r["S"] == 1.0 else 89.0
        vmf = float(r["weapon"].split(" vm=")[1].split()[0]) if " vm=" in r["weapon"] else 0
        ads = key.startswith("ads")
        fw = f4(R)
        # search wide around every number the gun could be using, so the answer is not assumed
        cand = [f4(70) / fw, code_fov(R, Rb, vmf) / fw, f4(float(r["weapon"].split("zoom_fov=")[1].split()[0])) / fw]
        if vmf > 0:
            cand.append(f4(vmf) / fw)
        e, s, dx, dy, n = iou_fit(mv, mp, min(cand) * 0.8, max(cand) * 1.2)
        rows.append(dict(mod=mod, state=key, S=r["S"], world_fov=R, zf=r["zf"], world_f=fw, scale_vs_prop=s, err_px=e, shift=f"{dx},{dy}", n=n, vm_f=s * fw,
                         code_f=(code_fov(R, Rb, vmf) if ads else f4(70)), zoom_fov_f=f4(float(r["weapon"].split("zoom_fov=")[1].split()[0])) if ads else f4(70),
                         vm_fov=2 * math.degrees(math.atan(600 / (s * fw))), vm_vertical=2 * math.degrees(math.atan(450 / (s * fw))),
                         muzzle="/".join(str(x) for x in r["muzzle"]), center="/".join(str(x) for x in r["center"]), weapon=r["weapon"]))
    for mode in ("hip", "ads"):
        a, b = held.get(f"{mode}_S1.27"), held.get(f"{mode}_S1.0")
        if a is not None and b is not None:
            e, s, dx, dy, n = iou_fit(a, b, 0.9, 1.15, 30)
            for x in rows:
                if x["mod"] == mod and x["state"] == f"{mode}_S1.27":
                    x["S127_over_S1"] = s
                    x["S_err"] = e
keys = ["mod", "state", "S", "world_fov", "zf", "world_f", "scale_vs_prop", "err_px", "shift", "n", "vm_f", "code_f", "zoom_fov_f", "vm_fov", "vm_vertical", "S127_over_S1", "S_err", "muzzle", "center", "weapon"]
with open(OUT if "--extents" not in sys.argv else os.devnull, "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(keys) + "\n")
    for r in rows:
        f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in keys) + "\n")
for r in rows:
    print(f'{r["mod"]:30s} {r["state"]:10s} R {r["world_fov"]:6.2f} s {r["scale_vs_prop"]:.3f} 1-IoU {r["err_px"]:.2f} n {r["n"]:4d} vm_f {r["vm_f"]:6.0f} code {r["code_f"]:6.0f} zoom {r["zoom_fov_f"]:6.0f} vert {r["vm_vertical"]:5.1f} shift {r["shift"]:8s} S-ratio {r.get("S127_over_S1", 0):.3f}')

# where the optic sits: side and top views from the sky, this state minus all sights off
sky = meta["_sky"]
off = {v: load(f"sky_alloff_{v}") for v in ("side", "top")}
s = 611.0 / sky["side"]["d"]
print("extents (F from the muzzle, U, R) of what this state adds to the gun with all sights off")
ex = {}
for mod in meta:
    if mod.startswith("_"):
        continue
    a, b = load(f"sky_{mod}_side"), load(f"sky_{mod}_top")
    ms, mt = np.abs(a - off["side"]).max(axis=2) > 10, np.abs(b - off["top"]).max(axis=2) > 10
    for q in (ms, mt):
        q[:90] = False
        q[755:] = False
    if mod != "none":  # the iron state is two separate parts
        for q in (ms, mt):
            lab, n = ndimage.label(ndimage.binary_opening(q, np.ones((2, 2), bool)))
            if n:
                q[:] = lab == 1 + int(np.argmax(ndimage.sum(q, lab, range(1, n + 1))))
    ys, xs = np.where(ms)
    yt, xt = np.where(mt)
    if len(xs) == 0:
        print(mod, "nothing differs")
        continue
    Fc, Uc = sky["side"]["Fc"], sky["side"]["Uc"]
    F = (Fc - (xs.max() + 1 - 800) / s, Fc - (xs.min() - 800) / s)
    U = (Uc + (450 - ys.max() - 1) / s, Uc + (450 - ys.min()) / s)
    Rr = ((450 - yt.max() - 1) / s, (450 - yt.min()) / s) if len(yt) else (0, 0)
    ex[mod] = dict(F=[round(float(x), 2) for x in F], U=[round(float(x), 2) for x in U], R=[round(float(x), 2) for x in Rr])
    print(mod, ex[mod])
json.dump(ex, open(os.path.join(D, "optic_extents.json"), "w"), indent=1)
