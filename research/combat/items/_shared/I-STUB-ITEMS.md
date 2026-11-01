# 公共部件 I：只有壳的道具（增益包模板、回调桩）

道具批次，会话 `i1-records`，2026-11-01。只读脚本。5 个增益包和炮台 v2 都引用这份。**这不是一个可用部件，是一份缺口说明。**

来源根目录：`research-src/s21-platform/`。`bk` = `scripts/weapons/mp_ability_boost_kit_<名字>.txt`，`stub` = `scripts/vscripts/weapons/_missing_callback_stubs.gnut`。

## 0. 概要

- **一句话**：这几样道具在本地构建里只有设置文件。增益包 `.txt` 是同一个模板，炮台 `.txt` 的回调指向 SDK 写的空函数。效果代码不在本地。
- **分类**：无。只记字段和意图。
- **不能做的事**：不能从这里还原流程。各记录第 2 节只写已知的部分。

## 1. 证据

**① 5 个增益包 `.txt` 内容相同。** `phase_rewind`、`lifesteal_kit`、`map_hack`、`nessie_summon`、`heal_radius` 互相 `diff`，只有第 3–8 行不同（名字和图标）。没有一个效果字段。

**② 这些 `.txt` 没有效果回调。** 只有 `OnWeaponRegenEnd = OnWeaponRegenEndGeneric`（`bk:23`）。没有 `OnWeaponPrimaryAttack`。

**③ loot 表整行注释掉。** `datatable/survival_loot.csv:407-414`，前缀 `// needs model port and server script:`。

**④ 被动在脚本里不存在。** 表里的 `passive` 列分别是 `PAS_PHASE_REWIND`、`PAS_LIFESTEAL_KIT`、`PAS_MAP_HACK`、`PAS_NESSIE_SUMMON`、`PAS_HEAL_RADIUS`。全局搜 `scripts/vscripts/`，这五个名字没有任何引用。

**⑤ 桩函数。** `stub` 文件头说明：武器设置引用了本构建没实现的回调，引擎否则拒绝预载，所以放空函数，第一次运行时打印 `[WEAPON-STUB] … is not implemented in this build`（`stub:249-256`）。相关条目：

| 回调 | 位置 | 属于 |
|---|---|---|
| `OnWeaponPrimaryAttack_ability_phase_rewind` | `stub:965` | `mp_ability_boost_kit_phase_rewind_offhand.txt:9` |
| `OnWeaponPrimaryAttackAnimEvent_ability_phase_rewind` | `stub:917` | 同上 `:10` |
| `OnWeaponAttemptOffhandSwitch_ability_phase_rewind` | `stub:592` | 同上 `:11` |
| `OnWeaponTossReleaseAnimEvent_GunTurret_v2` | `stub:1167` | `mp_ability_gun_turret_v2.txt:18` |
| `OnWeaponAttemptOffhandSwitch_GunTurret_v2` | `stub:562` | 同上 `:16` |

## 2. 增益包模板的字段（5 个相同）

| 字段 | 值 | 位置 |
|---|---|---|
| `weapon_type_flags` | `WPT_GRENADE` | `bk:11` |
| `fire_mode` | `automatic` | `bk:13` |
| `is_toss_weapon` | 0 | `bk:15` |
| `offhand_toss_activates_on_attack` | 1 | `bk:19` |
| `projectilemodel` | `mdl/weapons/void_ring/projectile_void_ring.rmdl` | `bk:24`（**是 Void Ring 的模型，推断：模板复制来的**） |
| `ammo_clip_size` / `ammo_per_shot` | 1 / 1 | `bk:28`、`bk:32` |
| `regen_ammo_refill_rate` | 0 | `bk:38` |
| `damage_type` | `none`，伤害全 0 | `bk:40-45` |
| `fire_rate` / `fire_duration` | 10 / 12 s | `bk:48-49` |
| `deploy_time` / `lower_time` / `raise_time` | 1.6 / 0.25 / 0.2 s | `bk:50-52` |
| `cooldown_type` | `ammo` | `bk:63` |

**不能读成这些道具的真实数值。** `fire_duration 12` 和 `deploy_time 1.6` 是 5 个不同效果共用的模板值。

## 3. 能找到的相关代码

| 道具 | 本地有的相关系统 | 见 |
|---|---|---|
| 吸血 | **有完整实现** `weapons/_lifesteal.nut`（按武器字段触发） | [boost-lifesteal](../boost-lifesteal/SYSTEM.md) |
| Nessie 召唤 | **有完整实现** `weapons/hopup_golden_horse.nut`（红色金马 hop-up），`sh_player_pet.nut` | [boost-nessie-summon](../boost-nessie-summon/SYSTEM.md) |
| 范围治疗 | 只有情人节模式的范围圈和音效 | [boost-heal-radius](../boost-heal-radius/SYSTEM.md) |
| 相位回溯 | 只有信号名和常量 | [boost-phase-rewind](../boost-phase-rewind/SYSTEM.md) |
| 地图透视 | 只有状态效果和客户端显示 | [boost-map-hack](../boost-map-hack/SYSTEM.md) |
| 炮台 v2 | 只有落地回调 | [gun-turret-v2](../gun-turret-v2/SYSTEM.md) |

## 4. 要实测的

R5 实测帮不上：脚本不存在，装备了也只会打印桩函数。想补只能走客户端反编译（REA，S21 `client` 里可能有一半）或公开资料。优先级低，因为 HSD 里这些都能照 TF2 / 技能阶段的部件做。

## 5. HSD 实现

见各记录第 6 节。
