"""First-person weapon bob / sway / timing keys of the titan primary weapons (TF2 weapon .txt).

Numbers only. Output: out/weapon_sway.csv (one row per key, one column per weapon).
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WDIR = os.path.join(HERE, "..", "..", "..", "local", "vpk", "client_mp_common", "scripts", "weapons")
WEAPONS = {
    "Ion": "mp_titanweapon_particle_accelerator", "Scorch": "mp_titanweapon_meteor", "Northstar": "mp_titanweapon_sniper",
    "Ronin": "mp_titanweapon_leadwall", "Tone": "mp_titanweapon_sticky_40mm", "Legion": "mp_titanweapon_predator_cannon",
    "Monarch": "mp_titanweapon_xo16_vanguard",
}
KEY = re.compile(r'^\s*"((?:bob|sway)_[a-z_]+|deploy_time|holster_time|raise_time|lower_time|zoom_time_in|zoom_time_out|zoom_fov|viewmodel_offset_[a-z]+|viewkick_[a-z_]+|sprintcycle_time|fire_rate)"\s+"([^"]*)"', re.I)


def top_level(path):
    """Keys outside Mods blocks (depth 1)."""
    out = {}
    depth = 0
    for line in open(path, encoding="utf-8", errors="replace"):
        s = line.split("//")[0]
        if depth == 1:
            m = KEY.match(s)
            if m and m.group(1) not in out:
                out[m.group(1)] = m.group(2)
        depth += s.count("{") - s.count("}")
    return out


def main():
    data = {t: top_level(os.path.join(WDIR, w + ".txt")) for t, w in WEAPONS.items()}
    keys = sorted({k for d in data.values() for k in d}, key=lambda k: (not k.startswith("bob"), not k.startswith("sway"), k))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    with open(os.path.join(HERE, "out", "weapon_sway.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key"] + list(WEAPONS))
        for k in keys:
            w.writerow([k] + [data[t].get(k, "") for t in WEAPONS])
    print(len(keys), "keys")


if __name__ == "__main__":
    main()
