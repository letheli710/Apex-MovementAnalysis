# 飞刀 系统记录

会话 `i1-records`，2026-11-01。静态记录。

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_throwingknife.nut`（165 行），`txt` = `weapons/mp_weapon_throwingknife.txt`。

## 0. 概要

- **道具**：主武器 / 飞刀 / `mp_weapon_throwingknife`（loot `survival_loot.csv:276`：type **`main_weapon`**，tier 5，lootTags `marksman`，不是军械）。
- **一句话**：占主武器槽的投掷武器。3700 u/s 直线飞出，命中造成 100 伤害（爆头 ×3），插在目标或地上 5 s 后消失。没有爆炸。
- **更正 filter**：filter 写"投掷类近战伤害"。**它不是近战**：`menu_category pistol`（`txt:12`）、`DF_BULLET`（`txt:64`），靠投掷物直接命中。
- **分类**：效果（高伤害单发直射投掷物）。
- **可拆出的部件**：
  - 投掷物直接命中当子弹 → 第 1 节
  - 命中后插在目标上跟随、定时消失 → 3.2 `OnProjectileCollision_weapon_throwingknife`、`CleanupKnife`
  - 不被跳板 / 黑洞吸走 → `_grenade.nut:260-263`
  - 被动带来开镜 → 3.1

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 出手 | 公共投掷流程，`is_toss_weapon 1` | `txt:11`、`txt:28-31`；[I-THROW-TOSS](../_shared/I-THROW-TOSS.md) |
| 飞行 | 重力 × 1.6，不继承玩家速度 | `txt:103`、`txt:108` |
| 伤害 | 投掷物碰撞伤害 `damage_near_value`（原生）；**推断**：脚本里没有 `TakeDamage`，`_grenade.nut:455` 把 `DF_BULLET` 传给碰撞伤害 | `txt:59-64` |
| 不爆炸 | 碰撞时 `SetDoesExplode( false )` | `nut:95` |
| 爆头 | `critical_hit 1`、`damage_headshot_scale 3`、`headshot_distance 2500` | `txt:51-52`、`txt:84-85` |
| 插住 | `PlantStickyEntity( ..., <90,0,0>, true )`，方向取飞行方向 | `nut:80-99` |
| 不弹 | 弹跳组全 0 | `txt:86-91` |
| 消失 | `CleanupKnife` 5 s，目标死亡提前 | `nut:129-165` |
| 被动开镜 | Seer 被动 `PAS_PARIAH` → mod `seer_passive_throwingknife`（`zoom_fov 60`） | `nut:20-28`、`txt:224-229` |

## 2. 流程

```
拿出（deploy_time 0）→ 按键 → 公共投掷流程（pullout 0.2 / toss 0.4）
飞行（寿命 15 s，projectile_lifetime）
碰撞：
  hitEnt 无效 → 销毁（服务端）
  扔的人自己 / 队友玩家 / 死亡图腾召回中 / 流血倒地 → ignoreTarget
  算插入方向；不再是实体（solid = 0）；不爆
  PlantStickyEntity 失败 或 ignoreTarget → 销毁（客户端先定住再瞬移）
  成功 → 停飞行音效；CleanupKnife：5 s 后或目标死亡 / 销毁时删除
回充：弹匣 1，regen 1/s（txt:207-214）→ 约 1 s 后可再扔（推断）
```

## 3. 代码

### 3.1 入口：`OnWeaponActivate_weapon_throwingknife`（`nut:7-32`）

只管 Seer 被动 mod。

注意 `nut:17` 先调 `player.IsNPC()` 再判 `IsValid`，顺序反了（原样记录）。

### 3.2 碰撞：`OnProjectileCollision_weapon_throwingknife`（`nut:35-127`）

客户端（7 参数）服务端（6 参数）共用一份函数体，内部 `#if`。S21 写法，和电弧星的双份不同。

**被 ignoreTarget 的情况也先调了 `PlantStickyEntity`**（`nut:99` 先调再判），之后才销毁。无所谓，顺手记下。

### 3.3 客户端

命中后 `ProjectileTeleport( pos, plantAngles )`（`nut:108`、`nut:117`）：客户端删除有延迟，所以手动摆正。

### 3.4 依赖

[I-THROW-TOSS](../_shared/I-THROW-TOSS.md)。`_grenade.nut:260-263`：名字硬编码，飞刀忽略 `TT_JUMP_PAD | TT_GRAVITY_LIFT | TT_BLACKHOLE`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| `projectile_launch_speed` | 3700 | u/s | `txt:98` | | |
| `projectile_launch_pitch_offset` | 2 | ° | `txt:99` | | |
| `projectile_gravity_scale` | 1.6 | | `txt:103` | 1200 u/s² | |
| `projectile_inherit_owner_velocity_scale` | 0 | | `txt:108` | **不继承**（手雷是 1） | |
| `projectile_lifetime` | 15 | s | `txt:37` | 没命中的寿命 | |
| `projectile_first_person_offset_fraction` | 0.5 | | `txt:100` | | |
| `damage_near_value` / `far` | 100 / 100 | HP | `txt:59-60` | 不随距离衰减 | |
| `damage_near_distance` / `far` | 1000 / 3000 | u | `txt:57-58` | 值相同，不起作用 | |
| `damage_near_value_titanarmor` | 100 | HP | `txt:61` | | |
| `damage_headshot_scale` | 3 | | `txt:52` | 爆头 300 | |
| `headshot_distance` | 2500 | u | `txt:85` | 超过不算爆头（推断） | |
| `damage_flags` | `DF_BULLET` | | `txt:64` | | |
| `impulse_force` | 0 | | `txt:63` | | |
| `fire_rate` | 1 | /s | `txt:77` | | |
| `deploy_time` | 0 | s | `txt:78` | | |
| `toss_pullout_time` / `toss_time` / `toss_overhead_time` | 0.2 / 0.4 / 0.7 | s | `txt:95-97` | | |
| `ammo_clip_size` | 1 | | `txt:207` | | |
| `regen_ammo_refill_rate` | 1 | /s | `txt:214` | | |
| `ammo_stockpile_max` / `default_total` | 50 / 50 | | `txt:216-217` | | |
| `uses_ammo_pool` | 0 | | `txt:209` | 不吃子弹（`ammo_pool_type bullet` 只是分类，推断） | |
| `ammo_no_remove_from_stockpile` | 1 | | `txt:212` | 推断：实际等于无限 | |
| `KNIFE_DESPAWN_TIME` | 5 | s | `nut:5` | 插住后消失 | |
| `stick_*` | 全 1 | | `txt:109-112` | | |
| 弹跳组 | 全 0 | | `txt:86-91` | | |
| `npc_min_range` / `max` | 600 / 1200 | u | `txt:204-205` | | |
| Seer 开镜 `zoom_fov` | 60 | | `txt:227` | | |

## 5. 未解决和要实测的

- **伤害来源**：确认是碰撞伤害（100）不是别的路径。脚本发射打 dummy，看伤害和爆头。100 和爆头 300 都是 `.txt` 字面值，没实测。
- **数量是否无限**：看回充是否真的不扣总量。真实按键投掷才能看（公共未解项）。
- `headshot_distance 2500` 语义：3000 u 打头。
- 对 NPC：直接命中时 `critical_hit`、护甲。`npc_dummie` 打身 / 打头。
- 本地 loot 表有这一行但 S21 哪个模式用：没查，不影响 PvE。

## 6. HSD 实现

未实现。建议：`Throw.cs` 的 `ThrowParams` + `stick = true`，加"命中直接伤害"（`ThrownItem` 现在有 `OnStick`、`OnBounce`、`OnExpire`，没有带目标的命中伤害，`Throw.cs:240-244`）；插在目标上的跟随和 5 s 消失只是表现。

是否占主武器槽和武器阶段一起定。留给武器阶段合并考虑。
