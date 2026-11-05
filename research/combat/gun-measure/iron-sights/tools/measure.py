#!/usr/bin/env python3
"""Numbers from the capture.py pictures. Measured from differences of engine pictures of the gun's own model; nothing is decoded from a game file.

  py -3 measure.py <run dir> <out dir>     writes IS-MEASURED.tsv and IS-PROFILES.json

Gun frame: F forward from the muzzle attachment, R right, U up from the muzzle attachment, R5 units.
Scale of a picture: FPX / distance for the plane at that distance. FPX checked by a known move (vmcal2.py: 616 to 625 against 611 by formula; 1 to 2 %).
Each sight place ("part") comes from meta["foci"]. In a part:
  F, U           raised piece: outline with irons up minus outline with irons off (bodygroup guns), or the outline above its neighbours (fixed sights)
  base_U         the gun's top under it with irons off, or beside it
  los_U          line of sight at that F (aimed muzzle and pitch on the held gun); cam_F: how far ahead of the eye when aimed
  back_profile   top edge seen from behind, (R, U): a notch shows as a dip. Anything further forward on the line (the other sight) shows through at its own smaller scale
  gap_at_los     see-through width round R = 0 at the height of the line of sight, from behind
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FPX = 611.0
THR = 18


def load(d, n):
    p = os.path.join(d, n + ".png")
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16) if os.path.exists(p) else None


def mask(a, b, thr=THR):
    m = np.abs(a - b).max(axis=2) > thr
    m[:100] = False
    m[755:] = False
    return m


def clean(m, keep=25, frac=0.06):
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n == 0:
        return m
    sizes = ndi.sum(m, lab, range(1, n + 1))
    k = np.zeros(n + 1, bool)
    k[1:] = sizes >= max(keep, sizes.max() * frac)
    return k[lab]


def side_xy(F, U, sh):
    s = FPX / sh["d"]
    fF, _, fU = sh["focus"]
    return 800 - (F - fF) * s, 450 - (U - fU) * s


def side_FU(x, y, sh):
    s = FPX / sh["d"]
    fF, _, fU = sh["focus"]
    return fF - (x - 800) / s, fU + (450 - y) / s


def bbox(m):
    ys, xs = np.where(m)
    return (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else None


def dp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    v = b - a
    L = np.hypot(*v) or 1.0
    d = [abs(v[0] * (p[1] - a[1]) - v[1] * (p[0] - a[0])) / L for p in pts]
    i = int(np.argmax(d))
    if d[i] < eps:
        return [pts[0], pts[-1]]
    return dp(pts[: i + 1], eps)[:-1] + dp(pts[i:], eps)


def outline_side(m, sh):
    ys, xs = np.where(m)
    if len(xs) == 0:
        return []
    top, bot = [], []
    for x in range(xs.min(), xs.max() + 1):
        r = np.where(m[:, x])[0]
        if len(r):
            top.append((x, r.min()))
            bot.append((x, r.max() + 1))
    pts = [side_FU(x, y, sh) for x, y in top] + [side_FU(x, y, sh) for x, y in reversed(bot)]
    return [[round(a, 3), round(b, 3)] for a, b in dp(pts, 0.03)]


def los_of(meta):
    n = meta.get("attach_names", {}).get("muzzle_flash", -1)
    ads = meta.get("ads", {}) or {}
    m = ads.get(str(n))
    if not m:
        return None
    mF, mR, mU = m["p"]
    th = math.radians(m["g"][0])
    return dict(mF=mF, mR=mR, mU=mU, pitch=m["g"][0], yaw=m["g"][1], at=lambda F: (-mU + F * math.sin(th)) / math.cos(th))


def part(d, meta, k, L):
    sh = meta["shots"].get(f"side_{k}_base")
    c = meta["foci"][k]
    out = dict(foc=c)
    if not sh:
        return out
    base, none = load(d, f"side_{k}_base"), load(d, f"side_{k}_none")
    off = load(d, f"side_{k}_off")
    sil_b = mask(base, none)
    sil_o = mask(off, none) if off is not None else None
    x0, _ = side_xy(c[1] + 0.25, 0, sh)
    x1, _ = side_xy(c[0] - 0.25, 0, sh)
    x0, x1 = max(int(x0), 0), min(int(x1) + 1, 1600)
    raised = None
    if sil_o is not None:
        r = np.zeros_like(sil_b)
        r[:, x0:x1] = (sil_b & ~sil_o)[:, x0:x1]
        r = ndi.binary_opening(r, iterations=1)
        if r.sum() > 60:
            raised = clean(r)
            out["source"] = "bodygroup"
    if raised is None:
        # a fixed sight: what stands above the gun's top line just outside this stretch
        tops = sil_b.argmax(axis=0)
        has = sil_b.any(axis=0)
        s = FPX / sh["d"]
        pad = int(1.2 * s)
        side_cols = [x for x in list(range(max(x0 - pad, 0), x0)) + list(range(x1, min(x1 + pad, 1600))) if has[x]]
        y_line = int(np.median(tops[side_cols])) if side_cols else 0
        r = np.zeros_like(sil_b)
        r[:y_line, x0:x1] = sil_b[:y_line, x0:x1]
        if r.sum() > 40:
            raised = clean(r)
        out["source"] = "outline"
    if raised is None or not raised.any():
        return out
    bb = bbox(raised)
    f1, u1 = side_FU(bb[0], bb[2], sh)
    f0, u0 = side_FU(bb[1] + 1, bb[3] + 1, sh)
    out.update(F=[round(f0, 2), round(f1, 2)], U=[round(u0, 2), round(u1, 2)])
    refm = sil_o if out.get("source") == "bodygroup" else sil_b
    t = []
    for x in range(bb[0], bb[1] + 1):
        rr = np.where(refm[:, x])[0]
        if len(rr):
            t.append(rr.min())
    out["base_U"] = round(side_FU(800, float(np.max(t)) if t else 450, sh)[1], 2)
    out["outline_side"] = outline_side(raised, sh)
    fm = (f0 + f1) / 2
    if L:
        out["los_U"] = round(L["at"](fm), 3)
        out["cam_F"] = [round(L["mF"] + f0, 2), round(L["mF"] + f1, 2)]
        out["top_over_los"] = round(u1 - L["at"](fm), 2)
    # from behind
    sb = meta["shots"].get(f"back_{k}_base")
    if sb:
        bb0, nb = load(d, f"back_{k}_base"), load(d, f"back_{k}_none")
        sil = clean(mask(bb0, nb), 25, 0.002)
        sc = FPX / sb["d"]
        fU = sb["focus"][2]
        tops = sil.argmax(axis=0)
        has = sil.any(axis=0)
        span = int(3.5 * sc)
        prof = [((x - 800) / sc, fU + (450 - tops[x]) / sc) for x in range(800 - span, 800 + span) if has[x]]
        out["back_profile"] = [[round(a, 3), round(b, 3)] for a, b in dp(prof, 0.03)] if prof else []
        if L:
            y = int(round(450 - (L["at"](fm) - fU) * sc))
            row = sil[y]
            left = next((x for x in range(800, 0, -1) if row[x]), None)
            right = next((x for x in range(800, 1599) if row[x]), None)
            out["gap_at_los"] = [None if left is None else round((left - 800) / sc, 2), None if right is None else round((right - 800) / sc, 2)]
            spans = []
            xs = np.where(row)[0]
            if len(xs):
                st = la = xs[0]
                for x in xs[1:]:
                    if x != la + 1:
                        spans.append([round((st - 800) / sc, 2), round((la + 1 - 800) / sc, 2)])
                        st = x
                    la = x
                spans.append([round((st - 800) / sc, 2), round((la + 1 - 800) / sc, 2)])
            out["solid_at_los"] = spans
        rows = np.where(sil[:, 800 - span:800 + span].any(axis=1))[0]
        if len(rows):
            xspan = np.where(sil[rows.min():rows.min() + int(0.8 * sc), :].any(axis=0))[0]
            if len(xspan):
                out["top_width"] = [round((xspan.min() - 800) / sc, 2), round((xspan.max() + 1 - 800) / sc, 2)]
    return out


def main():
    run, out = sys.argv[1:3]
    rows, prof = [], {}
    for g in sorted(os.listdir(run)):
        d = os.path.join(run, g)
        mp = os.path.join(d, "meta.json")
        if not os.path.exists(mp):
            continue
        meta = json.load(open(mp, encoding="utf-8"))
        L = los_of(meta)
        names = meta.get("attach_names", {})
        ml = meta.get("muz_local", [0, 0, 0])
        ads_center, ads_cam = None, None
        for n, i in names.items():
            if n.startswith("ADS_CENTER") and i > 0 and str(i) in meta["attach"]:
                p = meta["attach"][str(i)]["p"]
                ads_center = [round(p[0] - ml[0], 3), round(-(p[1] - ml[1]), 3), round(p[2] - ml[2], 3)]
                a = (meta.get("ads") or {}).get(str(i))
                ads_cam = a["p"] if a else None
        parts = [part(d, meta, k, L) for k in range(len(meta.get("foci", [])))]
        prof[g] = dict(id=meta["id"], vm=meta["vm"], F_extent=meta.get("F_extent"), clusters=meta.get("clusters"), near_line=meta.get("near_line"), ads_center=ads_center, ads_center_cam=ads_cam,
                       los=None if not L else dict(mF=L["mF"], mR=L["mR"], mU=L["mU"], pitch=L["pitch"], yaw=L["yaw"], U_at_eye=round(L["at"](-L["mF"]), 3)), bodygroups=meta.get("bg_default"), parts=parts)
        for i, p in enumerate(parts):
            if "F" not in p:
                continue
            rows.append(dict(gun=g, part=i, source=p.get("source", ""), F0=p["F"][0], F1=p["F"][1], U0=p["U"][0], U1=p["U"][1], base_U=p.get("base_U", ""), los_U=p.get("los_U", ""), top_over_los=p.get("top_over_los", ""),
                             camF0=p.get("cam_F", ["", ""])[0], camF1=p.get("cam_F", ["", ""])[1], gapL=(p.get("gap_at_los") or ["", ""])[0], gapR=(p.get("gap_at_los") or ["", ""])[1],
                             topW0=(p.get("top_width") or ["", ""])[0], topW1=(p.get("top_width") or ["", ""])[1]))
    keys = ["gun", "part", "source", "F0", "F1", "U0", "U1", "base_U", "los_U", "top_over_los", "camF0", "camF1", "gapL", "gapR", "topW0", "topW1"]
    with open(os.path.join(out, "IS-MEASURED.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    with open(os.path.join(out, "IS-PROFILES.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(prof, f, indent=0)
    print(len(prof), "guns", len(rows), "parts")


if __name__ == "__main__":
    main()
