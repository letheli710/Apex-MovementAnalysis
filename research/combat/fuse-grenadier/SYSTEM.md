# Fuse 被动 Grenadier（投掷专家）系统记录（补充）

来源根目录：`research-src/s21-platform/scripts/`。`pg` = `vscripts/pilot/_pilot_passive_grenadier.gnut`（151 行）。静态研究，2026-10-31，会话 combat-a。

**已有研究**：速度 ×1.7（实测 2210）、抛物线多画 1 次弹跳、每格多带 1 个、按键切换"远投 / 普通"见 [APEX-REPORT 2.7](../../../../TF2-Research/expansion/apex/APEX-REPORT.md)（下称 AR2.7）和 2.8。本文只补 AR2.7 没写的部分，按任务要求写短。

## 0. 概要

- **技能**：Fuse / 被动 / Grenadier / 被动 `PAS_FUSE` + 武器 mod `fuse_long_throw_passive`。
- **一句话**：投掷物的 mod 不只改速度，还**换成 Fuse 的发射器第一人称模型和发射声**；切换开关是"收回手里的投掷物再给一次"；另外几处零散规则（竞技场带弹 ×2、开爆炸物资库的专用动画、Maggie 被动交互）。
- **分类**：系统（"被动 = 给某类武器挂一个 mod"的写法）；可视化（同一个投掷物换一套持握模型和声音）。
- **可拆出的部件**：被动 → 全局武器 mod（`GiveExtraWeaponMod`）→ 3.1；切换时重新发武器 → 3.1。

## 1. 它用什么实现各种效果（只列 AR2.7 没有的）

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 远投 mod 的全部内容 | `projectile_launch_speed *1.7`；破片另加 `grenade_arc_indicator_bounce_count 2`；**每种都换 viewmodel 和声音** | 破片 `weapons/mp_weapon_frag_grenade.txt:272-280`（`ptpov_fuse_frag_grenade_held`、`Fuse_Ord_Launcher_Throw_FragGrenade_1P`）；电弧星 `mp_weapon_grenade_emp.txt:281-289`（`ptpov_fuse_shuriken_held_03`、只改速度不改弹跳次数）；铝热剂 `mp_weapon_thermite_grenade.txt:321-326`；另有 `mp_ability_emote_projector.txt:144`、`mp_weapon_ball_noncombat.txt:272` |
| 开关 | 客户端 `+scriptCommand5`（角色键）→ 服务端 `ClientCallback_ToggleThrowPower` | `pg:24-28`、`pg:64-96` |
| 切换的条件 | 有 `PAS_FUSE`；当前主手武器 = 反泰坦槽（投掷物槽）；背包里这种投掷物 ≥ 1 | `pg:66-81`；客户端还要求武器类型 `WPT_GRENADE`（`pg:115`） |
| 切换的做法 | `TakeWeaponByEntNow` → 增删玩家级 extra mod → `GiveWeapon` 回同一槽 → 设为当前武器 | `pg:83-95`。即 mod 挂在**玩家**上，以后拿到的所有投掷物都带 |
| 获得 / 失去被动 | 重新整理背包：失去时清掉超出上限的堆叠，得到时合并堆叠 | `pg:32-59` |
| 每格 +1 | `sh_survival_loot.gnut:7900-7905`（AR2.7 已有）：投掷物堆叠上限 = 基础 + playlist `boost_ordnance_stack_size` + 1 | |
| 竞技场 | 最多带的投掷物 ×2 | `vscripts/gamemodes/arenas/sh_arenas_buy_system.nut:679-685` |
| 爆炸物资库 | 开库时换一套 Fuse 专用面板动画和第一人称动画 | `vscripts/worldsystems/sh_explosive_loot_hold.nut:989-993`、`:1079` |
| 统计 | 10 s 内扔 5 个投掷物记一次 "Grenade Barrage" | `vscripts/weapons/_grenade.nut:268-290` |
| 和 Maggie 被动的交互 | 有 `PAS_FUSE` 时，Warlord's Ire 的高亮只在爆炸伤害时给、时长固定 1.0 s（"Fuse 升级"） | `vscripts/pilot/sh_pilot_passive_warlords_ire.gnut:11`、`:95`、`:116-120` |
| 提示 | 切换提示 `#FUSE_PASSIVE_TOGGLE_THROW_POWER` 被注释掉，不显示 | `pg:121-124` |

全部在服务端改武器；客户端只负责按键和模型。

## 2. 流程

```
拿着投掷物 → 按角色键
 └ 客户端检查（有被动、准备好、是手雷类）→ 发服务端
     └ 服务端检查（槽位、背包数量）→ 收回 → 切 mod → 重新给 → 切回
```

切换会**打断当前投掷动作**（武器被收回再给，推断：正在拉的手雷会取消）。

## 3. 代码

### 3.1 `ClientCallback_ToggleThrowPower`（`pg:64-96`）

```
mods = player.GetExtraWeaponMods()
player.TakeWeaponByEntNow(weapon)
if "fuse_long_throw_passive" in mods: 删掉; SetExtraWeaponMods
else: GiveExtraWeaponMod(player, "fuse_long_throw_passive")
GiveWeapon(name, ANTI_TITAN 槽); SetActiveWeaponByName
```

默认状态：脚本里没有在获得被动时自动加 mod（`Grenadier_PassiveToggle` 只整理背包）→ **默认是普通投掷，要按一次才是远投**（推断；AR2.7 实测 2210 是脚本直接加 mod 测的）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| projectile_launch_speed | ×1.7 | — | 各投掷物 `.txt` 的 mod | 见 AR2.7 |
| grenade_arc_indicator_bounce_count | 2（仅破片） | 次 | `mp_weapon_frag_grenade.txt:275` | 电弧星、铝热剂不改（AR2.8 说"Fuse 被动画 2 次"只对破片成立） |
| 堆叠 +1 | 1 | 个 / 格 | `sh_survival_loot.gnut:7904-7905` | |
| 竞技场上限倍率 | ×2 | — | `sh_arenas_buy_system.nut:681-682` | |
| Grenade Barrage 统计 | 5 个 / 10 s | — | `_grenade.nut:270-283` | |
| Warlord's Ire（Fuse） | 1.0 | s | `sh_pilot_passive_warlords_ire.gnut:11` | |

## 5. 未解决和要实测的

- 默认是否远投：选 Fuse 进训练场，不按键直接扔破片，runner 记初速（1300 还是 2210）。
- 切换是否取消正在拉的投掷物：拉着破片时按角色键。

## 6. HSD 实现

**部分已有**：`Throw.cs` 的 `Ballistics.Launch(…, speedScale)` 已有速度倍率参数，`ThrowParams.arcBounces` 已有抛物线弹跳数（注释里写了"Fuse passive 2"）。HSD 自创"投掷物发射器"可直接用：

- 被动做成 `CombatLoadout` 里一个开关（PlayerPrefs `hsd.tf2.x.grenadier`），开了所有投掷物 `speedScale = 1.7`；按 AR 2.8 的修正，`arcBounces = 2` 只给破片。
- 每格 +1：HSD 现在没有背包格子，跳过。
- 换持握模型 / 声音：HSD 目前全是几何体，跳过；以后做模型时按"同一投掷物两套表现"的结构留接口。
