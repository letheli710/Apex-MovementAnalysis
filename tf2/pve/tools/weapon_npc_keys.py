"""Extract NPC-related keys from TF2 weapon .txt files (WeaponData KeyValues).

Usage: py -3 -I weapon_npc_keys.py <weapons_dir> <out_tsv>

Top-level keys apply to both modes; keys inside MP_BASE / SP_BASE apply to MP / SP only and win
over top-level ones. The Mods block is skipped. "<KEEP_DEFAULT>" is kept as written.
Writes: weapon, key, mp, sp, mp_src, sp_src for keys starting with npc_ / proficiency_ and a few
context keys (damage, fire rate, clip, headshot / crit scales).
"""
import os
import re
import sys

CONTEXT = {"damage_near_value", "damage_far_value", "damage_near_distance", "damage_far_distance",
           "damage_near_value_titanarmor", "damage_far_value_titanarmor", "fire_rate",
           "ammo_clip_size", "damage_headshot_scale", "critical_hit_damage_scale", "critical_hit",
           "explosion_damage", "explosion_damage_heavy_armor", "explosion_inner_radius", "explosionradius",
           "projectile_launch_speed", "burst_fire_count", "burst_fire_delay", "spread_stand_hip",
           "spread_stand_hip_run", "damage_flags", "titanarmor_critical_hit_required"}
LINE = re.compile(r'^\s*"?([A-Za-z0-9_]+)"?\s+"([^"]*)"|^\s*"?([A-Za-z0-9_]+)"?\s+([^\s"/]+)')


def want(k):
    k = k.lower()
    return k.startswith("npc_") or k.startswith("proficiency_") or k in CONTEXT


def parse(path, fname):
    common, mp, sp = {}, {}, {}
    stack = []
    pending = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, raw in enumerate(f, 1):
            line = raw.split("//")[0].rstrip()
            s = line.strip()
            if not s:
                continue
            if s == "{":
                stack.append(pending or "")
                pending = None
                continue
            if s == "}":
                if stack:
                    stack.pop()
                continue
            m = LINE.match(line)
            if not m:
                pending = s.strip('"')
                continue
            key = m.group(1) or m.group(3)
            val = m.group(2) if m.group(1) else m.group(4)
            if "Mods" in stack:
                continue
            if not want(key):
                continue
            blk = stack[-1] if stack else ""
            target = mp if blk == "MP_BASE" else sp if blk == "SP_BASE" else common if len(stack) <= 1 else None
            if target is not None:
                target[key.lower()] = (key, val, f"{fname}:{ln}")
    return common, mp, sp


def main():
    d, out = sys.argv[1], sys.argv[2]
    rows = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        common, mp, sp = parse(os.path.join(d, fn), fn)
        allk = set(common) | set(mp) | set(sp)
        if not any(k.startswith("npc_") for k in allk):
            continue
        for k in sorted(allk):
            a = mp.get(k) or common.get(k)
            b = sp.get(k) or common.get(k)
            key = (a or b)[0]
            rows.append([fn[:-4], key, a[1] if a else "", b[1] if b else "", a[2] if a else "", b[2] if b else ""])
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("weapon\tkey\tmp\tsp\tmp_src\tsp_src\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(len(rows), "rows,", len({r[0] for r in rows}), "weapons")


if __name__ == "__main__":
    main()
