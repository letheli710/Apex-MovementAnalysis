"""Fill generated blocks in AI-SPEC.md from the parsed game files.

Usage: py -3 -I fill_spec.py <AI-SPEC.md> <aibehavior_dir> <aisettings-resolved.tsv> <weapon-npc-keys.tsv>

Blocks:
  <!-- chart:behavior_x --> ... <!-- /chart -->   behaviour tree chart (bt_sched.tree_mermaid)
  <!-- kt:name --> ... <!-- /kt -->               key table, definitions in TABLES below
Cell = "MP" if MP == SP, else "MP / SP". "—" = key not in any file for that NPC (native default);
"（空）" = key written with an empty value.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_sched  # noqa: E402

ENEMIES = ["npc_soldier", "npc_soldier_shield_captain", "npc_soldier_specialist", "npc_soldier_drone_summoner",
           "npc_spectre", "npc_spectre_mortar", "npc_stalker", "npc_stalker_crawling", "npc_super_spectre",
           "npc_frag_drone", "npc_drone", "npc_pilot_elite", "npc_pilot_elite_assassin", "npc_titan"]
INF_W = ["mp_weapon_rspn101", "mp_weapon_lmg", "mp_weapon_lstar", "mp_weapon_semipistol", "mp_weapon_r97",
         "mp_weapon_dmr", "mp_weapon_super_spectre", "mp_weapon_spectre_spawner", "mp_weapon_droneplasma",
         "mp_weapon_dronerocket", "mp_weapon_dronebeam", "mp_weapon_frag_grenade"]

TABLES = {
    "perception": ("settings", r"(FOV_.*|Notice.*|LookDist.*|aiEnemy_.*|react.*Chance.*|reactSurprised_.*|enemyAimAtMe.*|missileAwareness.*|suppressLSP.*)", ENEMIES),
    "combat": ("settings", r"(.*[Cc]ombat.*Pct|.*ChangeRate.*|dodge(Period|ForwardThreshold|BackwardThreshold)|maxDodgePerPeriod|minConsecutiveDodgeTime|StrafeDodgeDamage|lockOnDodgeHealthThreshold|circleStrafe.*|chaseStop.*|chaseOnlyReachable|takeCoverFromEnemyRadius|longJump.*|blockPeriod|maxBlockPerPeriod|tauntInterval|crouchCombat.*|shootingCoverFightRadius|faceEnemy.*|AimAngularSpeed|MoveYawSpeed|YawSpeed|specialRangeAttack.*|allow(Flee|UseCover|Patrol|Investigate|Signals|Cower))", ENEMIES),
    "health": ("settings", r"(Health|ArmorType|mechanical|DefaultWeapon|GrenadeWeaponName|AdditionalScriptWeapon|SummonDrone|PersonalShield|BehaviorSelector|PainOn.*|RepeatDamageTimeInterval|breakOutOfPainDamageThreshold|heavyPainMinInterval|lightPainMinInterval|fallDeathHeight|Melee(Damage(Min|Max|Radius|MinHeavyArmor|MaxHeavyArmor)|Range|Charge(DamageMin|DamageMax|DamageRadius|Range|Interval|CosAngleRange|OnlyPlayers)|CosAngleRange|MaxCombo)|meleeInterval|leechMaxDist|titanStompable|SmartAmmoLockType|HullType|nuke_on_death|enable_frag_drones|assaultHarvester|crawlingSettingsWrapper|ScriptSpawnAsCrawler|SpawnLimping|explode_on_death|suicideExplosion.*|SuicideChaseTime|canCloak|decloakOnShoot|drone_type|hoverHeight|maxFlyingSpeed.*|minSpeedScale|maxSpeedScale|npc_titan_player_settings)", ENEMIES),
    "weapons": ("weapons", r"(npc_.*|proficiency_.*|damage_headshot_scale|damage_near_value|damage_far_value|fire_rate|ammo_clip_size)", INF_W),
}


def load(tsv):
    vals, order = {}, {}
    for line in open(tsv, encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        name, key, mp, sp, mps, sps = (p + [""] * 6)[:6]
        vals[(name, key.lower())] = (mp, sp, mps, sps)
        order.setdefault(key.lower(), key)
    return vals, order


def table(vals, order, kre, names):
    kre = re.compile(kre, re.I)
    keys = sorted({k for (n, k) in vals if n in names and kre.fullmatch(order[k])}, key=str.lower)
    short = [n.replace("npc_", "").replace("soldier_", "").replace("mp_weapon_", "") for n in names]
    out = ["| 键 | " + " | ".join(f"`{s}`" for s in short) + " |", "|---|" + "---|" * len(names)]
    for k in keys:
        cells = []
        for n in names:
            v = vals.get((n, k))
            if not v:
                cells.append("—")
            else:
                mp, sp = (x if x != "" else "（空）" for x in (v[0], v[1]))
                cells.append(mp if mp == sp else f"{mp} / {sp}")
        out.append(f"| `{order[k]}` | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    md, bdir, settings, weapons = sys.argv[1:5]
    data = {"settings": load(settings), "weapons": load(weapons)}
    s = open(md, encoding="utf-8").read()

    def rep(m):
        name = m.group(2)
        src, kre, names = TABLES[name]
        vals, order = data[src]
        return m.group(1) + table(vals, order, kre, names) + "\n" + m.group(3)
    s, n = re.subn(r"(<!-- kt:(\w+) -->\n).*?(<!-- /kt -->)", rep, s, flags=re.S)
    open(md, "w", encoding="utf-8", newline="\n").write(s)
    print("filled", n, "key tables")
    trees = bt_sched.parse_trees(bdir)
    bt_sched.fill_charts(md, trees)


if __name__ == "__main__":
    main()
