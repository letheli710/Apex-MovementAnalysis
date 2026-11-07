#!/usr/bin/env python3
"""Crosshair size against the camera FOV (cl_fovScale) from sr.py "still" frames (<class>_fs<scale>_still_full.png, dark door behind).
  py -3 -I an_size.py <dir> [<dir> ...]
EVA-8 / Peacekeeper (ui/crosshair_shotgun): radius of the four arcs, from pixels within 20 deg of the diagonals (door lines are level or upright).
Mastiff (ui/crosshair_mastiff): half width of the level bar (outer end tick) and the inner gap.
Mozambique (ui/crosshair_tri_adjusted_alpha): the upright line above the centre (near and far end) and the two lower legs (distance of their far ends).
FOV per scale: 70 x scale (GetFOV read back in the log)."""
import glob, math, os, re, sys
from PIL import Image

CX, CY = 800, 450


def white(a, lo=150):
    return min(a) > lo and max(a) - min(a) < 30


def ring(im):
    rs = []
    for y in range(CY - 110, CY + 110):
        for x in range(CX - 110, CX + 110):
            dx, dy = x + 0.5 - CX, y + 0.5 - CY
            r = math.hypot(dx, dy)
            if r < 20 or r > 108 or abs(math.degrees(math.atan2(abs(dy), abs(dx))) - 45) > 20:
                continue
            if white(im.getpixel((x, y))):
                rs.append(r)
    best = max(((sum(1 for q in rs if lo <= q < lo + 6), lo) for lo in range(20, 104)), default=(0, 0))
    sel = [q for q in rs if best[1] <= q < best[1] + 6]
    return sum(sel) / len(sel) if sel else float("nan")


def mastiff(im):
    xs = [x - CX for x in range(CX - 140, CX + 140) if any(white(im.getpixel((x, y))) for y in range(CY - 1, CY + 2))]
    right = [x for x in xs if x > 0]
    return (max(right) if right else float("nan"), min(right) if right else float("nan"))


def moz(im):
    ys = [CY - y for y in range(CY - 140, CY - 2) if white(im.getpixel((CX, y))) or white(im.getpixel((CX - 1, y)))]
    legs = [math.hypot(x + 0.5 - CX, y + 0.5 - CY) for y in range(CY + 3, CY + 120) for x in range(CX + 3, CX + 140) if white(im.getpixel((x, y)))]
    return (max(ys) if ys else float("nan"), min(ys) if ys else float("nan"), max(legs) if legs else float("nan"), min(legs) if legs else float("nan"))


def main():
    rows = []
    for d in sys.argv[1:]:
        for p in sorted(glob.glob(os.path.join(d, "*_fs*_still_full.png"))):
            m = re.match(r"(.*)_fs([\d.]+)_still_full\.png", os.path.basename(p))
            if not m:
                continue
            gun, sc = m.group(1), float(m.group(2))
            fov = round(70 * sc, 3)
            im = Image.open(p).convert("RGB")
            if gun in ("shotgun", "shotgun_crate", "energy_shotgun"):
                rows.append((gun, fov, "ring_r", ring(im)))
            elif gun == "mastiff":
                o, i = mastiff(im)
                rows.append((gun, fov, "bar_outer", o)); rows.append((gun, fov, "bar_inner", i))
            elif gun == "shotgun_pistol":
                top_far, top_near, leg_far, leg_near = moz(im)
                rows.append((gun, fov, "top_far", top_far)); rows.append((gun, fov, "top_near", top_near))
                rows.append((gun, fov, "leg_far", leg_far)); rows.append((gun, fov, "leg_near", leg_near))
    print("gun\tfov\tpart\tpx\tpx_per_tan_deg\tangle_deg")
    for gun, fov, part, px in sorted(rows):
        k = (900 / 2) / (math.tan(math.radians(fov / 2)) * 0.75)
        print(f"{gun}\t{fov:g}\t{part}\t{px:.2f}\t{k:.1f}\t{math.degrees(math.atan(px / k)):.3f}")


if __name__ == "__main__":
    main()
