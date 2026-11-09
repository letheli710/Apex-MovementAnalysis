"""kit_d analysis: Scorch (final damage per 0.1 s on the titan target) and T-b (titan vs soldiers).
Usage: an_kit_d.py <run dir>"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_tools import Run  # noqa: E402

r = Run(sys.argv[1])
FIN = [[float(x[1]), x[2], float(x[3]), int(x[4]), x[5], int(x[6])] for x in r.other if x[0] == "KFIN" and len(x) >= 7]
print("tags:", " ".join(n for _, _, n in r.tags))


def fin(a, b, victim="foe"):
    return [f for f in FIN if r.sv(a) - 0.05 <= f[0] < r.sv(b) and f[1] == victim]


for n, key in (("th1", "+attack"), ("th2", "+attack"), ("trap_throw", "+offhand2"), ("trap_light", "+attack"), ("firewall", "+offhand0"),
               ("heatshield", "+offhand1"), ("flamecore", "+ability 1")):
    t = r.tag(n)
    if not t:
        continue
    a, b = t
    t0 = r.sv(r.cmd_after(a, key, b))
    fs = fin(a, b)
    by = collections.OrderedDict()
    for f in fs:
        k = round(f[0] - t0, 1)
        by.setdefault(k, []).append((int(f[2]), f[3], f[5] % 10000))
    print("\n-- %s: %d hits, sum %.0f, sources %s" % (n, len(fs), sum(f[2] for f in fs), sorted(set((f[3], f[4]) for f in fs))))
    for k, v in list(by.items())[:70]:
        print("   +%.1f  %s" % (k, v))

print("\n== T-b (soldier targets; NDMG = damage before final callbacks, KFIN = final)")
for a, b, n in r.tags:
    if not n.startswith("tb_"):
        continue
    nd = [x for x in r.NDMG if r.sv(a) - 0.05 <= x[0] < r.sv(b) + 0.5]
    fs = [f for f in FIN if r.sv(a) - 0.05 <= f[0] < r.sv(b) + 0.5 and f[1] == "npc_soldier"]
    dead = [x for x in r.other if x[0] == "NDEAD" and r.sv(a) <= float(x[2]) < r.sv(b) + 0.5]
    print("%-22s NDMG %s | KFIN %s | dead %d" % (n, [(round(x[0] - r.sv(a), 2), x[2], x[5]) for x in nd][:12],
          [(round(f[0] - r.sv(a), 2), f[2], f[3]) for f in fs][:12], len(dead)))
