"""Compact kit table: the gameplay keys that matter for each titan's kit (MP values, #base resolved),
plus the pas_* (kit upgrade) mods. Output: static/KEYS.txt. Source of every number: the weapon file named
on its line (scripts/weapons/<name>.txt in the unpacked client_mp_common VPK).

Usage: python -I summarize_kit.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_kit as E  # noqa: E402

KEYS = ["fire_mode", "damage_near_value", "damage_far_value", "damage_near_value_titanarmor", "damage_far_value_titanarmor",
        "damage_near_distance", "damage_far_distance", "explosion_damage", "explosion_damage_heavy_armor", "explosion_inner_radius",
        "explosionradius", "fire_rate", "burst_fire_count", "burst_fire_delay", "ammo_clip_size", "ammo_per_shot", "ammo_min_to_fire",
        "reload_time", "regen_ammo_refill_rate", "regen_ammo_refill_start_delay", "cooldown_type", "charge_time",
        "charge_cooldown_time", "charge_cooldown_delay", "charge_levels", "sustained_discharge_duration", "sustained_laser_range",
        "fire_duration", "core_build_time", "core_duration", "chargeup_time", "shared_energy_cost", "shared_energy_charge_cost",
        "projectile_launch_speed", "ads_move_speed_scale", "zoom_fov", "melee_damage", "melee_damage_heavyarmor", "melee_range",
        "critical_hit_damage_scale", "damage_headshot_scale", "smart_ammo_targeting_time_min", "smart_ammo_max_targets"]
EXTRA_MODS = ("Smart_Core", "arc_rounds", "missile_racks", "energy_transfer", "rapid_rearm", "maelstrom", "energy_field",
              "super_charged", "LongRangeAmmo", "LongRangePowerShot", "CloseRangePowerShot", "SiegeMode", "burst", "mortar_shots")


def main():
    out = []
    for titan, names in E.KITS.items():
        out.append("# " + titan)
        for n in names:
            b, m = E.load(n)
            out.append("  %s: %s" % (n, ", ".join("%s=%s" % (k, b[k]) for k in KEYS if k in b)))
            for k, v in m.items():
                if k.startswith("pas_") or k in EXTRA_MODS:
                    out.append("     [%s] %s" % (k, ", ".join("%s=%s" % x for x in v.items())))
    (E.OUT / "KEYS.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
