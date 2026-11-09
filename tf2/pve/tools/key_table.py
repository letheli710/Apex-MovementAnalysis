"""Print a markdown table of chosen aisettings keys for chosen NPCs from aisettings-resolved.tsv.

Usage: py -3 -I key_table.py <resolved.tsv> <keys_regex> <npc1,npc2,...>
Cell = "mp" if mp == sp, else "mp / sp" (MP first). Empty = key not in any file (native default).
"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
tsv, kre, npcs = sys.argv[1], re.compile(sys.argv[2], re.I), sys.argv[3].split(",")
vals, keys = {}, []
for line in open(tsv, encoding="utf-8").read().splitlines()[1:]:
    npc, key, mp, sp, *_ = line.split("\t")
    if npc in npcs and kre.fullmatch(key):
        vals[(npc, key.lower())] = (mp, sp)
        if key.lower() not in [k.lower() for k in keys]:
            keys.append(key)
keys.sort(key=str.lower)
short = [n.replace("npc_", "").replace("soldier_", "") for n in npcs]
print("| 键 | " + " | ".join(short) + " |")
print("|---|" + "---|" * len(npcs))
for k in keys:
    cells = []
    for n in npcs:
        v = vals.get((n, k.lower()))
        if not v:
            cells.append("—")
        else:
            mp, sp = v
            cells.append(mp if mp == sp else f"{mp or '—'} / {sp or '—'}")
    print(f"| `{k}` | " + " | ".join(cells) + " |")
