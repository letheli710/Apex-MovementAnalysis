# 破片手雷 系统记录

会话 `i1-records`，2026-11-01。静态记录，转写 APEX-REPORT 2.1 并补缺口；标 [实测] 的是 APEX 那次测的（`TF2-Research/expansion/apex/runs/20261029_202232_scripted.txt`）。

来源根目录：`research-src/s21-platform/scripts/`。`txt` = `weapons/mp_weapon_frag_grenade.txt`，`gr` = `vscripts/weapons/_grenade.nut`。**没有专属 `.nut`**，全走公共投掷代码。

## 0. 概要

- **道具**：军械 / 破片手雷 / `mp_weapon_frag_grenade`（loot `survival_loot.csv:278`，type `ordnance`，tier 1）。
- **一句话**：1300 u/s 出手，会弹会滚，出手起 3.5 s 爆，125 u 内 100 伤害，到 350 u 衰减到 0。
- **分类**：效果。
- **可拆出的部件**：
  - 公共投掷流程 → [I-THROW-TOSS](../_shared/I-THROW-TOSS.md)
  - 机械单位减半 → 3.2 `Frag_DamagedPlayerOrNPC`
  - 按表面弹跳的参数组 → 第 4 节
  - 手雷警告图标 → `show_grenade_indicator`（原生画）

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 飞行 | `FireWeaponGrenade`，引擎抛物线 | `gr:460`；重力 750 [实测] |
| 弹跳 / 滚动 | `.txt` 字段，原生结算 | `txt:98-103`；第一次撞墙 ×0.52 [实测] |
| 引信 | `grenade_fuse_time 3.5` + `start_fuse_on_launch 1` | `txt:84-85`、`gr:433-441`；3.5–3.6 s [实测] |
| 爆炸伤害 | `.txt` 的 `explosion_*`，原生范围伤害 | `txt:68-71` |
| 推力 | `impulse_force_explosions 50000` | `txt:73` |
| 屏幕震动 | `explosion_shake_*` | `txt:74-77` |
| 机械减半 | 按伤害来源注册回调 | `gr:118`、`gr:616-623` |
| 威胁提示 | `show_grenade_indicator 1`、`show_grenade_indicator_to_owner 1`、模型 `GRENADE_INDICATOR_FRAG_MODEL` | `txt:16-17`、`txt:39` |
| 抛物线 | `P_arc_red`，1 次弹跳 | `txt:31-35` |
| 拖尾 | `P_wpn_grenade_frag_trail` | `txt:43-44` |
| 爆炸特效 | impact 表 `exp_frag_grenade`（`scripts/impacts/exp_frag_grenade.txt`） | `txt:42` |
| 陷阱连锁 | `level.trapChainReactClasses` 含本武器 | `vscripts/weapons/_weapon_utility.nut:541` |
| 被 Wattson 拦截塔 | `trophy_system_ignores allowBounce` | `txt:112`，语义见第 5 节 |

服务端 / 客户端：出手双端（客户端预测），爆炸在服务端。

## 2. 流程

```
公共投掷流程（I-THROW-TOSS）→ 投掷物 fuse = 3.5（出手起算）
飞行 → 碰撞 → 反射 × 系数（浅角 0.6 / 陡角 0.4，法向再 × 0.3，随机 0.05）
碰到地面 → 滚动，每秒减速 5%
3.5 s 到 → 原地爆炸（空中也爆）
  伤害回调：Frag_DamagedPlayerOrNPC
```

打断：无。扔的人死在举手过程中，走 `HACK_DropGrenadeOnDeath` 原地掉一颗（`gr:566-603`）。

## 3. 代码

### 3.1 入口

`txt:23-29` 全部接公共回调：`Grenade_OnWeaponTossReleaseAnimEvent`、`Grenade_OnWeaponTossPrep`、`Grenade_OnWeaponTossCancelDrop`（返回 0，`gr:412`）、`Grenade_OnWeaponDeactivate`、`Grenade_OnWeaponActivate`、`Grenade_UpdateStats`；NPC 用 `Grenade_OnPlayerNPCTossGrenade_Common`（`txt:27`）。

### 3.2 `Frag_DamagedPlayerOrNPC`（`gr:616-623`）

```
玩家或泰坦 → 不改
ent.IsMechanical() → 伤害 × 0.5
```

**PvE 注意**：`IsMechanical()` 为真的敌人吃到一半（推断：幽灵、潜行者这类；原生取值，没实测）。

### 3.3 客户端表现

全部由 `.txt` 字段驱动，没有脚本。

### 3.4 依赖

[I-THROW-TOSS](../_shared/I-THROW-TOSS.md)。伤害修正链见 [C-DAMAGE-MODIFIERS](../../_shared/C-DAMAGE-MODIFIERS.md) 的"按伤害来源注册"。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| `projectile_launch_speed` | 1300 | u/s | `txt:107`；[实测] | 出手速度 | 扔得更远 |
| `projectile_launch_pitch_offset` | 9 | ° | `txt:108` | 往上抬 | |
| `projectile_inherit_owner_velocity_scale` | 1 | | `txt:110` | 继承玩家速度 | |
| 重力 | 750 | u/s² | `sv_gravity`；[实测] | | |
| `grenade_fuse_time` | 3.5 | s | `txt:84` | 引信 | |
| `start_fuse_on_launch` | 1 | | `txt:85` | 出手起算 | 改 0：举手起算 |
| `max_cook_time` | −1 | | `txt:83` | 烹饪上限 | |
| `explosion_damage` / `_heavy_armor` | 100 / 100 | HP | `txt:68-69` | 爆炸伤害 | |
| `explosion_inner_radius` | 125 | u | `txt:70` | 满伤半径 | |
| `explosionradius` | 350 | u | `txt:71` | 外半径 | |
| `impulse_force_explosions` | 50000 | | `txt:73` | 爆炸推力 | |
| `impulse_force` | 500 | | `txt:72` | 直接撞击推力（推断） | |
| `damage_near_value` / `far` | 10 / 10 | HP | `txt:62-63` | 手雷直接砸中的伤害（推断，见第 5 节） | |
| `grenade_bounce_vel_frac_shallow` | 0.6 | | `txt:98` | 浅角保留速度 | |
| `grenade_bounce_vel_frac_sharp` | 0.4 | | `txt:99` | 陡角保留速度 | |
| `grenade_bounce_vel_frac_along_normal` | 0.3 | | `txt:100` | 法向再乘 | 改小：弹得更低 |
| `grenade_bounce_randomness` | 0.05 | | `txt:101` | | |
| `grenade_bounce_extra_vertical_randomness` | 0.05 | | `txt:102` | | |
| `grenade_roll_vel_frac_per_second` | 0.05 | /s | `txt:103` | 滚动减速 | |
| 屏幕震动 半径 / 幅度 / 频率 / 时长 | 500 / 60 / 45 / 0.75 | | `txt:74-77` | | |
| `toss_pullout_time` / `toss_time` / `toss_overhead_time` | 0.25 / 0.4 / 0.7 | s | `txt:87-89` | 动作 | |
| `deploy_time` | 0.6 | s | `txt:91` | | |
| `fire_rate` | 0.83 | | `txt:82` | | |
| 机械系数 | 0.5 | | `gr:622` | | |
| `npc_explosion_damage`（MP / SP） | 100 / 32 | HP | `txt:216`、`txt:235` | NPC 扔时的伤害 | |
| `npc_min_range` / `npc_max_range` | 600 / 1200 | u | `txt:203-204` | NPC 使用距离 | |
| `npc_dangerous_to_normal_armor` | 1 | | `txt:205` | AI 把它当危险 | |
| 携带数 | `inventorySlotCount` 1，`boost_ordnance_stack_size` 另加 | 个 | `csv:278`、`vscripts/sh_survival_loot.gnut:7891-7905` | | |
| Fuse 被动 | 速度 × 1.7，每格 +1 | | `txt:272-274`、`sh_survival_loot.gnut:7904` | | |
| 弹药（非生存） | 槽 100，回充 6.66/s（15 s 一颗） | | `txt:217-223` | 无限模式 | |

## 5. 未解决和要实测的

- **对 NPC 的实际伤害**：100 × 距离衰减 × 机械 0.5 × 护甲？R5 脚本发射，对 `npc_dummie`、`npc_prowler` 各打内半径内 / 外半径中点。W2 已确认这两种能刷（`W2-runtime-early` 笔记）。
- **衰减曲线**：125 → 350 线性是引擎惯例，没测（APEX 2.1）。同一个测试放三个距离。
- **直接砸中**：`damage_near_value 10` 和 `gr:455` 的"碰撞伤害"。砸中玩家是否多 10。脚本发射打 dummy。
- `trophy_system_ignores allowBounce` 含义：字段名推断；HSD 不做拦截塔的话不用测。
- 真实按键投掷（公共未解项）。

## 6. HSD 实现

**已实现**：`HSD-Unity/Assets/HSD/Game/Runtime/Combat/Ordnance.cs` `FragGrenade`（`Fuse 3.5`、`Damage 100`、`Inner 125`、`Outer 350`、`Impulse 50000`）。

差别：
- **没有机械 ×0.5**。HSD 敌人没有"机械"标记。要补就给 `CombatUnit` 加一个标记。
- 没有 NPC 单独的伤害字段（R5 是 `npc_explosion_damage`）。

开关：无。这份记录没改代码。
