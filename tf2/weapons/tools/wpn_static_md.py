"""Grouped markdown tables of one TF2 weapon's file values (session tf2-weapons, 2026-11-08).

Usage: python -I wpn_static_md.py <data_dir> <weapon class> [<weapon class> ...] > out.md
Reads data/wpn-values.tsv (from wpn_extract.py). Every row: key, multiplayer value, campaign value
when it differs, and the mods that change the key. Cosmetic keys (sounds, effects, models, sway,
bob, UI, depth of field, menu stats) are left out; they are still in wpn-values.tsv. Every other
key that no group takes goes to a last group "其他", so nothing mechanical is dropped.
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

GROUPS = [
    ("开火和弹药", r"^(fire_mode|fire_rate|is_semi_auto|burst_|rechamber|ammo_|projectiles_per_shot|charge_(time|cooldown|end|require|is_triggered|levels|remain|full|wave)|regen_ammo|cooldown_time|allow_empty|reload_enabled|empty_reload_only|primary_fire_does_not_block_sprint|attack_button_presses_ads|looping_sounds|fire_duration|chargeup|charge_attack|move_speed_modifier)"),
    ("伤害", r"^(damage_|explosion|impulse_force|critical_hit|allow_headshots|headshot_distance|titanarmor_critical|crit)"),
    ("弹体", r"^(bolt_|projectile_(?!trail|killreplay|chasecam|first_person)|grenade_(?!arc_)|scripted_projectile|pass_through|bounce_)"),
    ("换弹和切枪", r"^(reload|reloadempty|reloadsegment|deploy|holster_time|raise_time|lower_time|fast_swap|deployfirst)"),
    ("开镜", r"^(zoom_|ads_(?!dof)|aimassist_adspull_zoom)"),
    ("散布", r"^spread_"),
    ("后坐和视角", r"^(viewkick_|viewpunch|viewdrift_|cooldown_viewkick)"),
    ("智能锁定", r"^smart_ammo_(?!looping)"),
    ("NPC 使用", r"^(npc_|proficiency_)"),
]
COSMETIC = re.compile(
    r"^(sway|bob_|fx_|sound|fire_sound|dof|bodygroup|ui[0-9]|clip_bodygroup|menu|stat_|vortex_|impact_effect|hud|"
    r"viewmodel|playermodel|printname|shortprintname|description|longdesc|low_ammo|pickup|tracer|projectile_trail|"
    r"projectilemodel|anim|rui|active_crosshair|sprintcycle|leveled|minimap|holster_type|holstermodel|entity_color|"
    r"charge_effect|charge_rumble|charge_drain_sound|chargeup_sound|charge_sound|fire_rumble|rumble|gamepad|aimassist|"
    r"red_crosshair|body_type|net_optimize|weaponClass|weaponSubClass|activitymodifier|OnWeapon|OnProjectile|OnClient|"
    r"burst_or_looping|grenade_arc_|crosshair|ads_dof|projectile_killreplay|projectile_chasecam|projectile_first_person|"
    r"bounce_effect|smart_ammo_looping|smart_ammo_hud|sprint_fractional|enable_highlight|is_burn_mod|ammo_display|"
    r"ammo_suck|trigger_snipercam|zoom_effects|threat_scope|mesh)", re.I)
HEADER = ["| 键 | 多人 | 战役（不同时） | 改它的 mod |", "|---|---|---|---|"]


def cell(x):
    return x.replace("|", r"\|")


def load(data_dir):
    mp, sp, mods = {}, {}, defaultdict(list)
    with open(Path(data_dir) / "wpn-values.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            key = (r["weapon"], r["key"])
            if r["scope"] == "mp":
                mp[key] = r["value"]
            elif r["scope"] == "sp":
                sp[key] = r["value"]
            else:
                mods[key].append("%s=%s" % (r["scope"][4:], r["value"]))
    return mp, sp, mods


def mod_text(m):
    first = [x for x in m if not x.startswith(("sp_", "burn_mod", "fd_", "at_unlimited"))]
    last = [x for x in m if x.startswith(("burn_mod", "fd_", "at_unlimited"))]
    return "; ".join(first + last)


def row(weapon, k, mp, sp, mods):
    return "| `%s` | %s | %s | %s |" % (k, cell(mp.get((weapon, k), "—")), cell(sp.get((weapon, k), "")),
                                        cell(mod_text(mods.get((weapon, k), []))))


def emit(weapon, mp, sp, mods):
    keys = sorted({k for (w, k) in list(mp) + list(sp) + list(mods) if w == weapon})
    print("### %s 文件原值（`%s.txt`，`wpn-values.tsv`）\n" % (weapon, weapon))
    used = set()
    for title, pat in GROUPS:
        rows = [k for k in keys if re.search(pat, k) and k not in used and "sound" not in k]
        if not rows:
            continue
        used.update(rows)
        print("**%s**\n" % title)
        print("\n".join(HEADER))
        for k in rows:
            print(row(weapon, k, mp, sp, mods))
        print()
    rest = [k for k in keys if k not in used and not COSMETIC.search(k) and "sound" not in k]
    if rest:
        print("**其他**\n")
        print("\n".join(HEADER))
        for k in rest:
            print(row(weapon, k, mp, sp, mods))
        print()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mp, sp, mods = load(sys.argv[1])
    for w in sys.argv[2:]:
        emit(w, mp, sp, mods)


if __name__ == "__main__":
    main()
