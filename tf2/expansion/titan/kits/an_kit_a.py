"""kit_a analysis: Ronin (phase dash, block, leadwall, arc wave, sword core) and Northstar (hover, railgun,
cluster missile, tether, flight core). Usage: an_kit_a.py <run dir>"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_tools import Run  # noqa: E402

r = Run(sys.argv[1])
K = ["t", "titan", "phase", "energy", "grav", "act", "clip", "chg", "lvl", "zoom", "o0", "o1", "o2", "o3", "hp", "maxhp", "sh",
     "shmax", "upg", "ms", "ts", "ds", "vb", "vp", "fhp", "fsh", "ftrk", "fx", "fy", "fz", "fms", "fvx", "fvy", "fvz"]
KIT = [dict(zip(K, row)) for row in r.KIT]
print("clock offset (server - client) %.4f s" % r.offset)


def tagrange(n):
    t = r.tag(n)
    if t is None:
        print("-- missing tag", n)
    return t


def phase_window(a, b):
    """client times the KC phase flag is on inside [a, b)"""
    on = [k[0] for k in r.KC if a <= k[0] < b and k[1] == 1]
    return (on[0], on[-1]) if on else (None, None)


def dash_curve(name, key="+offhand2"):
    tr = tagrange(name)
    if not tr:
        return
    a, b = tr
    t0 = r.cmd_after(a, key, b)
    rows = [c for c in r.C if t0 - 0.05 <= c[0] < min(b, t0 + 2.2)]
    if not rows:
        return
    x0, y0, z0 = rows[0][1:4]
    vmax = max(math.hypot(c[4], c[5]) for c in rows)
    p0, p1 = phase_window(t0 - 0.1, t0 + 2.0)
    print("%s: tap %.3f | phase %s..%s (%.3f s) | peak vh %.0f" % (name, t0, None if p0 is None else "%.3f" % (p0 - t0),
          None if p1 is None else "%.3f" % (p1 - t0), (p1 - p0) if p0 else 0, vmax))
    for dt in (0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
        c = min(rows, key=lambda c: abs(c[0] - t0 - dt))
        d = math.hypot(c[1] - x0, c[2] - y0)
        ang = math.degrees(math.atan2(c[2] - y0, c[1] - x0)) if d > 1 else float("nan")
        print("   %5.2f s  disp %6.1f u  dir %6.1f deg  dz %6.1f  vh %6.1f  vz %7.1f" % (dt, d, ang, c[3] - z0, math.hypot(c[4], c[5]), c[6]))


def dmg_in(name, victim=None, pad=0.0):
    tr = tagrange(name)
    if not tr:
        return []
    a, b = tr
    return [d for d in r.KDMG if r.sv(a) - 0.05 <= d[0] < r.sv(b) + pad and (victim is None or d[1] == victim)]


print("\n== Ronin phase dash")
for n in ("pd_f", "pd_r", "pd_b", "pd_n", "pd_afterdash", "pd_air"):
    dash_curve(n)

print("\n== Ronin sword block (hit 1000 from the enemy titan at relYaw)")
for a, b, n in r.tags:
    if n.startswith("bk_") and n != "bk_hold":
        ds = dmg_in(n, "self")
        hp = [x for x in r.other if x[0] == "KINFO" and len(x) > 1 and x[1] == "hurtfrom" and r.sv(a) - 0.05 <= float(x[-1]) < r.sv(b)]
        print("%-10s dmg events %s | after: %s" % (n, [round(d[2], 1) for d in ds], " ".join(hp[0][2:6]) if hp else "-"))

print("\n== Ronin leadwall (pellets on the atlas, shield 0)")
for n in ("lw_300", "lw_600", "lw_1000"):
    ds = dmg_in(n, "foe")
    print("%-8s %d hits: %s  sum %.0f" % (n, len(ds), sorted(round(d[2]) for d in ds), sum(d[2] for d in ds)))

print("\n== Ronin arc wave (idle atlas 600 u)")
tr = tagrange("aw_600")
if tr:
    t0 = r.cmd_after(tr[0], "+offhand0", tr[1])
    ds = dmg_in("aw_600", "foe")
    for d in ds:
        print("   hit +%.3f s  dmg %.0f  src %d" % (d[0] - r.sv(t0), d[2], d[5]))
    ms = [(float(k["t"]) - r.sv(t0), k["fms"]) for k in KIT if r.sv(t0) <= float(k["t"]) < r.sv(tr[1]) and k["fms"] not in ("-", "0.000")]
    print("   foe move_slow:", ms[:3], "...", ms[-3:])

print("\n== Ronin sword core")
for n in ("sc_on", "sc_block", "sc_sword", "sc_dash", "sc_wait"):
    tr = tagrange(n)
    if not tr:
        continue
    acts = []
    last = None
    for k in r.KC:
        if tr[0] <= k[0] < tr[1] and k[2] != last:
            acts.append((round(k[0] - tr[0], 3), k[2]))
            last = k[2]
    print("%-9s weapons %s" % (n, acts[:6]))
    for d in dmg_in(n):
        print("    dmg %s %.0f src %d at +%.2f" % (d[1], d[2], d[5], d[0] - r.sv(tr[0])))
tr = tagrange("sc_dash")
if tr:
    tt = [x for x in r.TT if r.sv(tr[0]) <= x[0] < r.sv(tr[1])]
    print("   dodge power after the two dashes:", [(round(x[0] - r.sv(tr[0]), 1), round(x[2], 1)) for x in tt[::3]][:14])

print("\n== Northstar hover (z above the start, vz)")
for x in r.other:
    if x[0] == "KSKY":
        print("   sky:", " ".join(x[1:]))
for n in ("hv_ceiling_lane", "hv_stand", "hv_stand2", "hv_fwd", "hv_dash", "fc"):
    tr = tagrange(n)
    if not tr:
        continue
    key = "+ability 1" if n == "fc" else "+offhand2"
    t0 = r.cmd_after(tr[0], key, tr[1])
    rows = [c for c in r.C if t0 - 0.05 <= c[0] < tr[1]]
    if not rows:
        continue
    z0 = rows[0][3]
    zmax = max(rows, key=lambda c: c[3])
    land = next((c for c in rows if c[0] > zmax[0] and c[9] == 1), None)
    print("%s: peak %.1f u at %.2f s; ground again %s; max vh %.0f" % (n, zmax[3] - z0, zmax[0] - t0, None if land is None else "%.2f s" % (land[0] - t0),
          max(math.hypot(c[4], c[5]) for c in rows)))
    for dt in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.25, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0):
        c = min(rows, key=lambda c: abs(c[0] - t0 - dt))
        if abs(c[0] - t0 - dt) < 0.05:
            print("   %4.2f s  z %6.1f  vz %7.1f  vh %6.1f  ground %d" % (dt, c[3] - z0, c[6], math.hypot(c[4], c[5]), c[9]))

print("\n== Northstar railgun (hold ADS t, then fire; atlas 600 u, shield 0)")
for a, b, n in r.tags:
    if not n.startswith("rg_"):
        continue
    tf = r.cmd_after(a, "+attack", b)
    kc = min((k for k in r.KC if k[0] <= tf), key=lambda k: abs(k[0] - tf))
    ds = dmg_in(n, "foe")
    print("%-7s charge at fire %.3f zoom %.2f | dmg %s" % (n, kc[4], kc[6], [round(d[2]) for d in ds]))

print("\n== Northstar cluster missile")
tr = tagrange("cm")
if tr:
    t0 = r.sv(r.cmd_after(tr[0], "+offhand0", tr[1]))
    ds = dmg_in("cm", "foe")
    print("   %d hits, sum %.0f" % (len(ds), sum(d[2] for d in ds)))
    print("   ", [(round(d[0] - t0, 2), round(d[2])) for d in ds])

print("\n== Northstar tether (idle atlas 400 u)")
tr = tagrange("tt")
if tr:
    rows = [k for k in KIT if r.sv(tr[0]) <= float(k["t"]) < r.sv(tr[1])]
    for k in rows[::5]:
        print("   %.1f foe %s %s v %s %s ms %s" % (float(k["t"]) - r.sv(tr[0]), k["fx"], k["fy"], k["fvx"], k["fvy"], k["fms"]))
