# 增益包：相位回溯 系统记录

会话 `i1-records`，2026-11-01。静态记录。**本地只有壳**，公共证据见 [I-STUB-ITEMS](../_shared/I-STUB-ITEMS.md)。

来源根目录：`research-src/s21-platform/scripts/`。`bk` = `weapons/mp_ability_boost_kit_phase_rewind.txt`，`off` = `weapons/mp_ability_boost_kit_phase_rewind_offhand.txt`。

## 0. 概要

- **道具**：增益包 / `mp_ability_boost_kit_phase_rewind`（`survival_loot.csv:409`，被注释，被动 `PAS_PHASE_REWIND`）。
- **一句话**：意图是回到几秒前的位置（名字推断）。本地效果代码不存在。
- **分类**：系统（参考）。
- **可拆出的部件**：本地无。实际可用的回溯部件在 TF2 记录和 Death Totem。

## 1. 它用什么实现各种效果

| 效果 | 本地有什么 | 证据 |
|---|---|---|
| 物品壳 | 模板 `.txt` | `bk`（字段见 I-STUB-ITEMS 第 2 节） |
| 激活武器 | `off`：`fire_mode offhand`，`offhand_active_slot altHand`，`viewmodel ptpov_burn_card` | `off:12`、`off:55-56` |
| 开火 | **桩函数** | `off:9-11` → `vscripts/weapons/_missing_callback_stubs.gnut:592`、`:917`、`:965` |
| 伤害钩子 | 注释掉的 `BurnCard_PhaseRewind_OnDamage` | `vscripts/weapons/sh_phase_shift.gnut:199` |
| 信号 | `PhaseRewindCrouchPlayer`、`PhaseRewindStop`，注册了但没人用 | `sh_phase_shift.gnut:195-196` |
| 常量 | `RECONSTRUCT_REWIND_TICK 0.1`、`RECONSTRUCT_REWIND_COUNT 100`，全局搜没有使用者 | `sh_phase_shift.gnut:99-100` |

`viewmodel ptpov_burn_card` 和常量名说明它继承自 TF2 的"强化卡"（推断）。

## 2. 流程

**写不出。不编。** `off` 只告诉我们：副手、按一下就开火、弹匣 1。

## 3. 代码

无。见第 1 节。

## 4. 参数

| 参数 | 值 | 来源 | 说明 |
|---|---|---|---|
| `off` `fire_rate` | 1 | `off:63` | |
| `off` `deploy_time` / `holster_time` / `lower_time` / `raise_time` | 0.25 / 0.6 / 0.6 / 0.25 s | `off:15-18` | 动作，可参考 |
| `off` `fire_anim_rate` | 0.65 | `off:13` | |
| `off` 声音 | `cosmicbox_phaserewind_activate_1p/3p` | `off:22`、`off:24` | 名字可参考 |
| `off` `cooldown_type` | `ammo_instant` | `off:69` | |
| 回溯时长、记录密度 | **没有** | | `RECONSTRUCT_REWIND_*` 不能确认属于它 |

## 5. 未解决和要实测的

R5 实测帮不上（桩函数）。见 I-STUB-ITEMS 第 4 节。

## 6. HSD 实现

**不需要从这里实现**。有两个现成参考：

| 参考 | 内容 | 差别 |
|---|---|---|
| TF2 `burnmeter_phase_rewind`（`TF2-Research/expansion/w3/W3-REPORT.md` 第 1 节） | 环形缓冲 + 倒放路径，2 s，相位中 | **原路倒放**，完整 |
| [revenant-death-totem](../../revenant-death-totem/SYSTEM.md) | 标记 + 致死触发召回 + 安全落点 + 无敌帧 | **瞬移回标记点**，不是倒放 |

filter 的对照结论成立，只是 R5 这一方没有数据。
