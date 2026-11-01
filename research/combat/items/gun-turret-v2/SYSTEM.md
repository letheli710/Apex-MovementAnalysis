# 炮台 v2 系统记录

会话 `i1-records`，2026-11-01。静态记录。**本地只有 `.txt`，没有服务端脚本**，公共证据见 [I-STUB-ITEMS](../_shared/I-STUB-ITEMS.md)。

来源根目录：`research-src/s21-platform/scripts/`。`txt` = `weapons/mp_ability_gun_turret_v2.txt`。

## 0. 概要

- **道具**：战术（`weapon_type_flags WPT_TACTICAL`，`txt:124`）/ `mp_ability_gun_turret_v2`。**不在 `survival_loot.csv`**。
- **一句话**：一个扔出去的战术：500 u/s 投出，落地后理应变成炮台。"变成炮台"这一步本地没有。
- **更正 filter**：filter 把它和 `.nut` 齐全的项放在一起，备注只写增益包"只有 .txt"。这项也是。
- **分类**：系统（参考）。
- **可拆出的部件**：本地无。放置炮台的真实代码在 Sheila。

## 1. 它用什么实现各种效果

| 效果 | 本地有什么 | 证据 |
|---|---|---|
| 投出 | **桩** `OnWeaponTossReleaseAnimEvent_GunTurret_v2` | `txt:18` → `vscripts/weapons/_missing_callback_stubs.gnut:1167` |
| 能否切换 | **桩** `OnWeaponAttemptOffhandSwitch_GunTurret_v2` | `txt:16` → `_missing_callback_stubs.gnut:562` |
| 举手 | 真函数 `Grenade_OnWeaponTossPrep` | `txt:17`，[I-THROW-TOSS](../_shared/I-THROW-TOSS.md) |
| 落地 | 真函数 `OnProjectileCollision_weapon_deployable_LDOV` | `txt:19`，`vscripts/weapons/sh_deployable.gnut:164-178`，[C-PLACEABLE-DEPLOYABLE](../../_shared/C-PLACEABLE-DEPLOYABLE.md) |
| 炮台实体、AI、开火 | **没有** | |
| 外形 | 投掷物 `mdl/weapons/rampart_turret/w_rampart_turret.rmdl`；手上是 Gibraltar 护罩模型 | `txt:23-25`（占位，推断） |

## 2. 流程

**写不出。不编。** 按字段只能到"举手 → 扔出 → 落地粘住"，而且"扔出"那一步是桩，实际扔不出来（推断）。

## 3. 代码

无。见第 1 节。

## 4. 参数

投掷部分（可参考）：

| 参数 | 值 | 单位 | 来源 |
|---|---|---|---|
| `projectile_launch_speed` | 500 | u/s | `txt:36` |
| `projectile_launch_pitch_offset` | 1 | ° | `txt:37` |
| `projectile_lifetime` | 20 | s | `txt:38` |
| `projectile_gravity_scale` | 1 | | `txt:40` |
| `grenade_disc_throw` | 1 | | `txt:39` |
| `stick_*` | 全 0 | | `txt:41-44` |
| 弹跳组 | 0.5 / 0.3 / 0.1 / 0.05 / 0 / 0.1 | | `txt:91-96` |
| `grenade_radius_vertical` / `horizontal` | 5 / 16 | u | `txt:97-98` |
| `grenade_view_launch_offset` | 15 0 0 | | `txt:99` |
| `explosion_inner_radius` / `explosionradius` | 250 / 450 | u | `txt:60-61`（伤害 0；用途不明） |
| 伤害 | 全 0 | | `txt:52-59` |
| `regen_ammo_refill_rate` / `ammo_per_shot` | 5 / 100 | /s | `txt:109`、`txt:107` → **20 s 冷却** |
| `deploy_time` / `lower_time` | 0.15 / 0.15 | s | `txt:77-78` |

炮台本身的血量、射速、伤害、射程：**没有**。

## 5. 未解决和要实测的

实测帮不上（桩函数）。

## 6. HSD 实现

**已有独立实现，不来自这里**：`HSD-Unity/.../Combat/Boosts.cs` `Turret`（`TurretKind.HighRate / HeavyShot`，来自 TF2 `burnmeter_ap / at_turret_weapon`，W3 第 4 节）。

filter 想要的"放置炮台"对照，用：

| 参考 | 内容 |
|---|---|
| [rampart-sheila](../../rampart-sheila/SYSTEM.md) 3.2.3 | 放置物炮台、上下、受伤规则、EMP 停机、捡回（玩家操作） |
| [C-PLACEABLE-DEPLOYABLE](../../_shared/C-PLACEABLE-DEPLOYABLE.md) | 放置生命周期 |
| TF2 W3 第 4 节 | 自动炮台（AI 开火） |

Sheila 是**人坐上去打**，TF2 哨戒炮是**自己打**。HSD 现有的是后者。
