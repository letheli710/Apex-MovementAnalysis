"""kit_b / kit_c analysis: Ion (energy, vortex, laser), Tone (marks, rockets, salvo), Monarch (upgrades, siphon,
rearm), Legion (spin-up, power shot, knockback, gun shield, modes, smart core). Usage: an_kit_bc.py <run dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_tools import Run  # noqa: E402

r = Run(sys.argv[1])
K = ["t", "titan", "phase", "energy", "grav", "act", "clip", "chg", "lvl", "zoom", "o0", "o1", "o2", "o3", "hp", "maxhp", "sh",
     "shmax", "upg", "ms", "ts", "ds", "vb", "vp", "fhp", "fsh", "ftrk", "fx", "fy", "fz", "fms", "fvx", "fvy", "fvz"]
KIT = [dict(zip(K, row)) for row in r.KIT]
names = [n for _, _, n in r.tags]
print("clock offset %.4f; tags: %s" % (r.offset, " ".join(names)))


def kit_in(a, b):
    return [k for k in KIT if r.sv(a) <= float(k["t"]) < r.sv(b)]


def kc_in(a, b):
    return [k for k in r.KC if a <= k[0] < b]


def dmg(a, b, victim=None, pad=0.0):
    return [d for d in r.KDMG if r.sv(a) - 0.05 <= d[0] < r.sv(b) + pad and (victim is None or d[1] == victim)]


def series(rows, f, step=0.1, t0=None):
    out, nxt = [], None
    for k in rows:
        t = k[0] if isinstance(k, list) else float(k["t"])
        if nxt is None or t >= nxt:
            out.append((round(t - (t0 if t0 is not None else rows[0][0] if isinstance(rows[0], list) else float(rows[0]["t"])), 2), f(k)))
            nxt = t + step
    return out


def T(n):
    for a, b, m in r.tags:
        if m == n:
            return a, b
    return None


def show(n, fn):
    t = T(n)
    if t:
        print("\n-- " + n)
        fn(*t)


# ---------------- Ion
def energy(a, b):
    print("   energy (client, every 0.1 s):", series(kc_in(a, b), lambda k: k[10], 0.1, a)[:60])


for n in ("en_idle", "en_ads", "en_laser", "en_trip", "vx_hold", "vx_long"):
    show(n, energy)


def vortex(a, b):
    ks = kit_in(a, b)
    print("   vortex bullets / projectiles / energy:", [(round(float(k["t"]) - r.sv(a), 1), k["vb"], k["vp"], k["energy"]) for k in ks][::3][:30])
    for d in dmg(a, b, "foe"):
        print("   foe hit +%.2f  %.1f  src %d  dtype %d  %s" % (d[0] - r.sv(a), d[2], d[5], d[6], d[7]))
    for d in dmg(a, b, "self")[:5]:
        print("   self hit +%.2f  %.1f  src %d  %s" % (d[0] - r.sv(a), d[2], d[5], d[7]))
    print("   self hits total", len(dmg(a, b, "self")))
    nd = [x for x in r.NDMG if r.sv(a) <= x[0] < r.sv(b)]
    print("   soldier hits (NDMG):", [(round(x[0] - r.sv(a), 2), x[2], x[5]) for x in nd][:20])


for n in ("vx_bullets", "vx_proj"):
    show(n, vortex)


def hits(a, b):
    ds = dmg(a, b, "foe")
    print("   %d foe hits, sum %.0f:" % (len(ds), sum(d[2] for d in ds)), [(round(d[0] - r.sv(a), 2), round(d[2])) for d in ds][:40])
    ks = kit_in(a, b)
    if ks and ks[0]["ms"] not in ("-",):
        print("   self move_slow / turn_slow:", [(round(float(k["t"]) - r.sv(a), 1), k["ms"], k["ts"]) for k in ks][::5][:16])


for n in ("en_laser", "lc"):
    show(n, hits)

# ---------------- Tone
for n in ("tm_0", "tm_1", "tm_2", "tm_3", "tr_fire", "tm_life", "tr_nomark", "sonar", "salvo"):
    def tone(a, b, n=n):
        ks = kit_in(a, b)
        print("   trackers on foe:", [(round(float(k["t"]) - r.sv(a), 1), k["ftrk"]) for k in ks][::2][:40])
        ds = dmg(a, b, "foe")
        print("   %d foe hits, sum %.0f:" % (len(ds), sum(d[2] for d in ds)), [(round(d[0] - r.sv(a), 2), round(d[2]), d[5]) for d in ds][:70])
    show(n, tone)

# ---------------- Monarch
for a, b, n in r.tags:
    if n.startswith("up") or n in ("reembark",):
        ks = kit_in(a, b)
        if ks:
            k0, k1 = ks[0], ks[-1]
            print("\n-- %s: upg %s -> %s, shield %s -> %s, hp %s/%s -> %s/%s" % (n, k0["upg"], k1["upg"], k0["sh"], k1["sh"], k0["hp"], k0["maxhp"], k1["hp"], k1["maxhp"]))
            ch = [(round(float(k["t"]) - r.sv(a), 1), k["upg"], k["sh"], k["maxhp"]) for i, k in enumerate(ks) if i == 0 or (k["upg"], k["sh"], k["maxhp"]) != (ks[i - 1]["upg"], ks[i - 1]["sh"], ks[i - 1]["maxhp"])]
            print("   changes:", ch[:8])
for x in r.other:
    if x[0] == "KINFO" and x[1] in ("pas", "soulpas", "setmods", "main", "offhand"):
        print("   ", " ".join(x[1:])[:200])


def siphon(a, b):
    ks = kit_in(a, b)
    print("   own shield / foe shield / foe hp / foe move_slow:", [(round(float(k["t"]) - r.sv(a), 1), k["sh"], k["fsh"], k["fhp"], k["fms"]) for k in ks][::2][:20])
    print("   KDMG:", [(round(d[0] - r.sv(a), 2), d[1], round(d[2]), d[4], d[5]) for d in dmg(a, b)])
    nd = [x for x in r.NDMG if r.sv(a) <= x[0] < r.sv(b)]
    print("   NDMG:", [(round(x[0] - r.sv(a), 2), x[2], x[5]) for x in nd])


for n in ("sip_titan", "sip_soldier"):
    show(n, siphon)


def rearm(a, b):
    print("   offhands o0/o1/o2 (client):", series(kc_in(a, b), lambda k: (k[7], k[8], k[9]), 0.25, a)[:12])
    print("   dodge power:", [(round(x[0] - r.sv(a), 1), round(x[2], 1)) for x in r.TT if r.sv(a) <= x[0] < r.sv(b)][::3][:12])


show("rearm", rearm)


# ---------------- Legion
def shots(a, b):
    kc = kc_in(a, b)
    st = [k[0] - a for i, k in enumerate(kc) if i and k[3] < kc[i - 1][3]]
    tz = [k[0] - a for k in kc if k[6] > 0.99][:1]
    att = r.cmd_after(a, "+attack", b)
    print("   +attack at %.3f; zoom 1 at %s; %d shots; first %s; gaps %s" % ((att - a) if att else -1, ["%.3f" % x for x in tz], len(st),
          ["%.3f" % x for x in st[:3]], ["%.3f" % (st[i + 1] - st[i]) for i in range(min(len(st) - 1, 12))]))
    ds = dmg(a, b, "foe")
    if ds:
        print("   foe hits %d, values %s" % (len(ds), sorted(set(round(d[2], 1) for d in ds))[:12]))


for n in ("lg_hip", "lg_hip_again", "lg_ads", "lg_adsquick", "lg_long_ads", "smart", "rl_monarch_melee_1", "rl_monarch_melee_1.9", "rl_monarch_offhand0_1", "rl_ronin_melee_1", "rl_legion_melee_1.5"):
    show(n, shots)


def power(a, b):
    print("   o0 (clip:charge) / zoom / primary charge:", series(kc_in(a, b), lambda k: (k[7], round(k[6], 2), round(k[4], 2)), 0.1, a)[:30])
    for d in dmg(a, b, "foe"):
        print("   foe hit +%.2f %.1f src %d" % (d[0] - r.sv(a), d[2], d[5]))
    ks = kit_in(a, b)
    print("   foe pos / vel:", [(round(float(k["t"]) - r.sv(a), 1), k["fx"], k["fz"], k["fvx"], k["fvz"]) for k in ks][::2][:20])


for n in ("ps_close", "ps_kb300", "ps_kb900", "ps_kb1300", "ps_long"):
    show(n, power)


def gunshield(a, b):
    print("   o1 clip:charge / zoom:", series(kc_in(a, b), lambda k: (k[8], round(k[6], 2)), 0.5, a)[:26])


show("gunshield", gunshield)
