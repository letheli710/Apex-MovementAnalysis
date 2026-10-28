#!/usr/bin/env python3
"""R6 slope-slide course (research/phase2-local/slope): planar lanes built from tilted copies of a solid block, in the empty
void north of the firing range (mp_rr_canyonlands_staging_mu1; traces found nothing from z 16000 down to -30000 at
y >= 24000, x -12000..12000, and a player standing there is not killed for being out of bounds).

Tile: mdl/canyonlands/firing_range_towerblock_01.rmdl (map-editor catalog mask has the firing-range bit, so the late
precache does not hang the dedi). Probed with down traces: the collision is a box, top 512.03 above the origin, footprint
+-511.5 (hits at +-511, none at +-512). Source angles <pitch, yaw, roll>: pitch +p tilts the top normal to (sin p, 0, cos p),
so the top descends along +X (probe: pitch 20 gave normal (0.342, 0, 0.940)).

A lane is a chain of planar segments along +X: (rise_deg, length along the surface, align). Tiles of one segment are
coplanar and cover it; `align` says which end must be exact. Overhang is allowed only where the neighbour surface lies
above the overhang (concave joints) or at a free end; convex joints (flat -> down, crest) must be exact ('a' = the start,
'b' = the end, 'both' = both ends; 'both' needs length >= one tile).

  py -3 slope_geo.py               # print the lanes, start points and prop count
  py -3 slope_geo.py --json out    # the world description used by the analysis and the Unity harness
"""
import argparse
import json
import math

MODEL = "mdl/canyonlands/firing_range_towerblock_01.rmdl"
TOP = 512.03      # top face above the origin
HALF = 511.5      # half footprint of the collision box
TILE = 2 * HALF
ZB = 3000.0       # height of the lowest flat of every lane

# name: (x0, y, z0 of the first segment start, width along Y, [(rise_deg, length, align), ...])
_C1, _C2 = -9000.0, 1000.0
_Y = lambda k: 26000.0 + 1700.0 * k   # noqa: E731
LANES = {}
for _k, _th in enumerate((10, 20, 30, 40)):          # uphill: flat run-in, then one tile up
    LANES["up%d" % _th] = (_C1, _Y(_k), ZB, TILE, [(0, TILE, "both"), (_th, TILE, "a")])
for _k, _th in enumerate((5, 10, 15, 20, 25, 30)):   # downhill: top flat, two tiles down, bottom flat
    _drop = 2 * TILE * math.sin(math.radians(_th))
    LANES["dn%d" % _th] = (_C2, _Y(_k), ZB + _drop, TILE, [(0, TILE, "both"), (-_th, 2 * TILE, "both"), (0, TILE, "a")])
LANES["v20"] = (_C1, _Y(4), ZB + TILE * math.sin(math.radians(20)), TILE,
                [(0, TILE, "both"), (-20, TILE, "both"), (20, TILE, "a")])
# crest: flat, a short 10 deg rise (its tile reaches under the flat), over the top onto 20 deg down, bottom flat
_CREST_UP = 500.0
_cz = ZB + 2 * TILE * math.sin(math.radians(20)) - _CREST_UP * math.sin(math.radians(10))
LANES["crest"] = (_C1, _Y(5), _cz, TILE, [(0, TILE, "both"), (10, _CREST_UP, "b"), (-20, 2 * TILE, "both"), (0, TILE, "a")])
# lateral / diagonal: one 20 deg ramp (down +X) two tiles along the slope, three tiles wide
LANES["lat20"] = (_C2, _Y(7) + 600.0, ZB + 2 * TILE * math.sin(math.radians(20)), 3 * TILE, [(-20, 2 * TILE, "both")])


def segments(name):
    """Planar segments of a lane: dicts xa, xb, za, zb, rise_deg, y0, y1."""
    x, y, z, w, segs = LANES[name]
    out = []
    for rise, length, align in segs:
        t = math.radians(rise)
        xb, zb = x + length * math.cos(t), z + length * math.sin(t)
        out.append({"xa": x, "xb": xb, "za": z, "zb": zb, "rise_deg": rise, "len": length, "align": align,
                    "y0": y - w / 2, "y1": y + w / 2})
        x, z = xb, zb
    return out


def surface_z(name, x):
    """Top height of the lane at x (None outside), and the segment's rise angle."""
    for s in segments(name):
        if s["xa"] - 1e-6 <= x <= s["xb"] + 1e-6:
            return s["za"] + (x - s["xa"]) * math.tan(math.radians(s["rise_deg"])), s["rise_deg"]
    return None, None


def tiles(name):
    """(model, x, y, z, pitch, yaw, roll) props of a lane."""
    x0, y, z0, w, _ = LANES[name]
    ny = max(1, int(round(w / TILE)))
    ys = [y + (j - (ny - 1) / 2.0) * TILE for j in range(ny)]
    props = []
    for s in segments(name):
        t = math.radians(s["rise_deg"])
        L = s["len"]
        n = int(math.ceil(L / TILE - 1e-9))
        if s["align"] == "both":
            if L < TILE - 1e-6:
                raise ValueError("%s: 'both' needs a segment of at least one tile" % name)
            s0s = [min(i * TILE, L - TILE) for i in range(n)]
        elif s["align"] == "a":
            s0s = [i * TILE for i in range(n)]
        else:
            s0s = [L - TILE - i * TILE for i in range(n)]
        nx, nz = -math.sin(t), math.cos(t)          # top normal of a surface rising along +X
        for s0 in s0s:
            sc = s0 + HALF
            tx, tz = s["xa"] + sc * math.cos(t), s["za"] + sc * math.sin(t)
            for yy in ys:
                props.append((MODEL, round(tx - TOP * nx, 3), round(yy, 3), round(tz - TOP * nz, 3), -float(s["rise_deg"]), 0.0, 0.0))
    return props


def all_props():
    return [p for name in LANES for p in tiles(name)]


def world(name):
    """The lane as trial.json `world` data: planar segments (Source units)."""
    return {"lane": name, "segments": segments(name)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    for name in LANES:
        segs = segments(name)
        print(name, len(tiles(name)), "tiles;", " | ".join("x %.0f..%.0f z %.1f..%.1f %+d deg" % (s["xa"], s["xb"], s["za"], s["zb"], s["rise_deg"]) for s in segs))
    print("props:", len(all_props()))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"model": MODEL, "top": TOP, "half": HALF, "lanes": {n: world(n) for n in LANES}}, fh, indent=1)


if __name__ == "__main__":
    main()
