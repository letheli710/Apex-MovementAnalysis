# 增益包：范围治疗 系统记录

会话 `i1-records`，2026-11-01。静态记录。**本地只有壳**，公共证据见 [I-STUB-ITEMS](../_shared/I-STUB-ITEMS.md)。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`vl` = `gamemodes/sh_gamemode_valentines_s15.nut`。

## 0. 概要

- **道具**：增益包 / `mp_ability_boost_kit_heal_radius`（`survival_loot.csv:412`，被注释，被动 `PAS_HEAL_RADIUS`，全局搜无引用）。
- **一句话**：意图是范围治疗（名字推断）。本地没有效果代码。filter 要的是"范围圈"可视化，这个在情人节模式里**有现成的**。
- **线索（推断）**：图标是 `icon_boostkit_date_night`（`.txt` 第 7–8 行）；吸血脚本用音效 `DateNight_AOE_*`（`weapons/_lifesteal.nut:28-30`）。两者都指向情人节 / Date Night 的范围治疗。
- **分类**：可视化（参考）。
- **可拆出的部件**：范围圈 → 3.2 `ValentinesRangeFXStart_Thread`。

## 1. 它用什么实现各种效果

| 效果 | 本地有什么 | 证据 |
|---|---|---|
| 物品壳 | 模板 `.txt` | `scripts/weapons/mp_ability_boost_kit_heal_radius.txt` |
| 范围圈 | 粒子 `P_ar_edge_ring_mid` 挂在实体上 | `vl:45`、`vl:847-853` |
| 圈的半径 | 控制点 1 = `<10, 半径 / TROPHY_AR_EFFECT_SIZE, 0>` | `vl:849` |
| 圈的颜色 | 控制点 2 = `COLORID_HUD_LOOT_TIER_SPECIAL` | `vl:850` |
| 可见范围 | 队友和自己 | `vl:853` |
| 范围判定 | `ValentinesIsPlayerInRangeForProximityBuff`；距离默认 12 m，可 2D | `vl:7`、`vl:26-28`、`vl:39` |

## 2. 流程

增益包：**写不出，不编。**

范围圈：读条开始时起线程，治疗成功或取消的信号结束，删特效（`vl:843-862`）。

## 3. 代码

### 3.2 `ValentinesRangeFXStart_Thread`（`vl:843-…`）

见第 1 节。`P_ar_edge_ring_mid` + 控制点缩放，和 Trophy 用同一个 `TROPHY_AR_EFFECT_SIZE` 常量（Wattson 拦截塔见 [wattson-interception-pylon](../../wattson-interception-pylon/SYSTEM.md)）：R5 的范围圈是一个共用粒子。

对照：治疗无人机治疗半径 `DEPLOYABLE_MEDIC_HEAL_RADIUS = 256`（`weapons/mp_ability_lifeline_follow_medic.nut:66`，见 [lifeline-heal-drone](../../lifeline-heal-drone/SYSTEM.md)）。光环逻辑见 [C-AURA-BUFF](../../_shared/C-AURA-BUFF.md)。

## 4. 参数

| 参数 | 值 | 来源 | 说明 |
|---|---|---|---|
| 增益包的治疗量、半径、时长 | **没有** | | |
| 情人节距离 | 12 m（约 472 u） | `vl:39` | 只是参考 |
| 圈厚度（推断） | 10 | `vl:849` | 控制点 X |

## 5. 未解决和要实测的

实测帮不上。

## 6. HSD 实现

未实现。范围圈在 Unity 里就是一个投影或环形网格，半径作为参数。需要时和治疗光环一起做（`C-AURA-BUFF`）。这一项单独做的价值很低。
