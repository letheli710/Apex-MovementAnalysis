# Mirage 大招 Life of the Party · 系统记录

批次 D，会话 `combat-d`，2026-10-31。只做了静态研究。引用并补充 APEX-REPORT 2.5 的大招部分。

路径从 `research-src/s21-platform/scripts/` 开始。**MU** = `vscripts/weapons/mp_ability_mirage_ultimate.nut`（211 行），**MU.txt** = `weapons/mp_ability_mirage_ultimate.txt`，**HP** = `vscripts/weapons/mp_ability_holopilot.nut`。

> 本文件只写大招和战术**不同**的地方。分身实体、仇恨、被打结算全部和战术相同，见 [mirage-decoy](../mirage-decoy/SYSTEM.md) 和 [`_shared/D-DECOY-AI.md`](../_shared/D-DECOY-AI.md)。

## 0. 概要

- **技能**：Mirage / 大招 / Life of the Party / `mp_ability_mirage_ultimate`。
- **一句话**：按住蓄力 1 s（期间隐身、加速），满了自动放出 6 个分身，以自己为中心按 60° 一档往 6 个方向散开跑，各活 5 s；放完 5 s 内收起武器，可以提前按键取消。
- **分类**：系统（多分身散开的排布）、可视化（隐身闪烁）。
- **可拆出的部件**：
  - 环形散开排布（第 i 个的角度：0、+60、−60、+120、−120、180）→ 3.2.1 `CalculateAngleSegmentForDecoy`
  - 散开的出生点（贴着自己 30 u + 安全点修正）→ 3.2.1
  - 蓄力 → 满了才放、没满取消 → 3.2.2 `OnWeaponChargeEnd`
  - 释放后的短暂隐身 + 加速 + 锁武器 → 3.2.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 蓄力 | 武器 charge：1 s、3 级、松手不强制（`charge_require_input 0`、`charge_end_forces_fire 1`） | MU.txt:62-80 |
| 6 个分身 | `chargeLevel(3) × 2 = 6`（注释："想放 6 个，但蓄力显示绑在 3 级上"），调 `CreateHoloPilotDecoys( 6 )` 走"多个"路径 | HP:227-229、454-474 |
| 散开 | 每个分身一个 yaw 偏移，按偏移方向跑 | HP:1081-1092、460-466 |
| 隐身 | `EnableCloak( 1.1 s, 渐入 0.2 )` + `SetCloakFlicker( 0.5, 0.2 )` | MU:155-180 |
| 加速 | 状态效果 `speed_boost 0.15`、1.1 s、渐出 0.5 | MU:166 |
| 锁武器 | `HolsterAndDisableWeapons` + `LockWeaponsAndMelee`，`fire_duration` 5 s；结束时 0.5 s 慢速掏枪 | MU:122-151、MU.txt:61 |
| 取消提示 | 状态效果 `mirage_ultimate_cancel_hint` → 全屏 RUI | MU:28-46、131 |
| 大招分身音效 | 循环音换成 `Mirage_Vanish_Decoy_Sustain` 一套 | HP:957-962 |

## 2. 流程

```
按大招键（弹夹满 60）
   ▼
OnWeaponChargeBegin（MU:191-208）：音效、语音、MirageUltCloakThink(1.1, 0.2)：隐身 + 加速
   │ 蓄力 1 s（3 级）
   ▼
OnWeaponChargeEnd（MU:103-120）
   蓄力 < 满 → 发 CancelCloak 信号，结束（不放分身，弹药不扣？见 5 节）
   满了 → 弹夹清零 → OnWeaponPrimaryAttack_mirage_ultimate
            → OnWeaponPrimaryAttack_holopilot：chargeLevel 3 ×2 = 6 → CreateHoloPilotDecoys( 6 )
            → HolsterAndDisableWeaponsMirageUltimate( 5 s )
   ▼
6 个分身各自直跑 5 s；玩家 5 s 内武器收起（按换武器键或大招键可提前结束）
```

- **触发条件**：`PlayerCanUseDecoy`（MU:48-58）。
- **冷却**：`ammo_instant`，弹夹 60 / 每秒 1 = 60 s（MU.txt:30-47）；`upgrade_extra_ultimate_mod` 弹夹 30。
- **打断**：锁武器线程在死亡、处决、倒地、取消时结束（MU:124-128）；隐身线程同样。
- **升级**：`PAS_ULT_UPGRADE_ONE`：隐身 +1 s（playlist `upgrade_mirage_extra_cloak_duration`，MU:182-189）。

## 3. 代码

### 3.1 入口

| 函数 | 行 | 做什么 |
|---|---|---|
| `OnWeaponChargeBegin_ability_mirage_ultimate` | MU:191-208 | 隐身 + 加速 |
| `OnWeaponChargeEnd_ability_mirage_ultimate` | MU:103-120 | 满了就放，不满取消 |
| `OnWeaponPrimaryAttack_mirage_ultimate` | MU:60-68 | 调战术的放分身函数 + 锁武器 |

### 3.2 核心逻辑

#### 3.2.1 多个分身怎么散开（HP:454-474、1081-1092）

```
for i in 0..5:
   Δyaw = angle(i)      angle(0)=0
                         i 奇数：+((i/2)+1)·60   → 1:+60  3:+120  5:+180
                         i 偶数：−(i/2)·60        → 2:−60  4:−120
   a      = 玩家角度 + <0, Δyaw, 0>（只改 yaw，规范化）
   f      = AnglesToForward(a)
   终点   = 从玩家眼睛沿 f 画 100 u 的线，碰到东西就停（TRACE_MASK_PLAYERSOLID）
   decoy  = CreateDecoy( 终点, …, 时长 5 s )     ← 引擎让它朝"终点"跑，到了继续往前
   decoy.角度 = a
   出生点 = 玩家原点 + f·30（被墙卡住时 PutEntityInSafeSpot 从玩家原点往出生点找空位）
```
所以 6 个分身**同时**出生在玩家周围半径 30 u 的圆上，每个面朝自己的方向直跑。俯仰不影响（用的是玩家 `GetAngles`，推断只有 yaw）。

坐载具时出生点基准改成 `玩家位置 + (0,0,32) + 视线·64 + (0,0,25)`（HP:232-239、469）。

#### 3.2.2 蓄力规则（MU:103-120）

- 蓄力没满就松手 → 只取消隐身，不放分身。
- 满了（1 s）自动放（`charge_end_forces_fire`）。
- 放之前先把弹夹清零（MU:116），再走战术的发射函数（战术函数的返回值不扣弹药，因为已经清零了）。

#### 3.2.3 释放时的玩家状态（MU:122-180）

- 隐身 1.1 s（升级 2.1 s），开始 0.2 s 内闪烁强度 0.5；
- 加速 +0.15，1.1 s；
- 武器收起并锁定 5 s，按 `IN_WEAPON_CYCLE` 或 `IN_OFFHAND4`（大招键）提前结束，结束时 0.5 s 慢掏枪。

### 3.3 客户端表现

- 取消提示 RUI（MU:28-46）。
- 隐身闪烁由引擎处理（`SetCloakFlicker`）。

### 3.4 本地没用上的代码

- `MIRAGE_ULT_MAX_DECOYS = 5`、`CLOAK_TRIGGER_RADIUS = 240`、`MirageUltimate_GetMaxKaleidoscopeDecoys`、`ShouldDoKaleidoscopeUltimate`（MU:7-10、210-227）：S21 "Kaleidoscope" 版大招的残留，本地没有调用者（grep 只有定义）。**推断**正版 S21 大招已经是另一套（分身围着队友），本地 dedi 跑的是老版"6 个散开"。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 分身数 | 3 级 ×2 = 6 | 个 | MU.txt:63、HP:228-229 | | 改 charge_levels 会变成 2/4/6… |
| 角度档 | 60 | ° | HP:25（`HOLOPILOT_ANGLE_SEGMENT`） | 6 个正好一圈 | 数量 ≠ 6 时会叠或留缺口 |
| 出生半径 | 30 | u | HP:444 | | |
| 终点射线 | 100 | u | HP:464 | | |
| 分身时长 | 5 | s | HP:17（`ULTIMATE_DECOY_DURATION`） | | |
| 分身血量 | 45 | HP | HP:596 | 同战术 | |
| 蓄力 | 1.0 | s | MU.txt:62 | | |
| 隐身 | 1.1（升级 +1） | s | MU:205、182-189 | | |
| 隐身渐入 | 0.2 | s | MU:162 | | |
| 闪烁 | 强度 0.5、0.2 s | — | MU:163、205 | | |
| 加速 | +0.15、1.1 s、渐出 0.5 | — | MU:166 | | |
| 锁武器 | 5 | s | MU.txt:61（`fire_duration`） | | |
| 掏枪 | 0.5 | s | MU:145 | | |
| 冷却 | 60 | s | MU.txt:30-47 | | |
| 冷却升级 | 30（弹夹） | s | MU.txt mods | | |

## 5. 未解决和要实测的

| 问题 | 为什么不确定 | 怎么测 |
|---|---|---|
| 蓄力没满松手扣不扣弹药 | 只看到取消隐身，弹药扣除在引擎 charge 逻辑 | 训练场点一下大招，看大招条 |
| 隐身 1.1 s 和 APEX-REPORT 的"1.1 s"一致；正版 S21 是不是 Kaleidoscope | 本地有残留常量 | 对照正版录像 |
| 6 个分身贴墙时的位置 | `PutEntityInSafeSpot` 引擎 | 背靠墙放大招，记 6 个分身位置 |

## 6. HSD 实现

**已有（TF2X，10-29）**：分支 A = `DecoyBranch.BranchAMany`，`CombatSim.Items.cs:215-227`：角度 `{0, 60, −60, 120, −120, 180}`，出生在 `player.pos + dir·30`，墙里就放在玩家脚下，5 s。PlayerPrefs `hsd.tf2.x.decoy = 1`。冷却占位 `Charges(1, 30)`（`CombatSim.Items.cs:93`）。

和 R5 的差别：

| 项 | R5 | HSD | 建议 |
|---|---|---|---|
| 排布 | 一样 | 一样 | — |
| 出生点被墙挡 | 安全点搜索 | 退回玩家脚下 | 可接受 |
| 蓄力 1 s + 隐身 + 加速 + 锁武器 | 有 | 没有，立即放 | 分支 A 是"多分身"设计，不一定要照搬隐身；如要贴合，加 1 s 蓄力和 1.1 s 隐身 |
| 冷却 | 60 s | 30 s（占位） | 记进差异档 |

想让分身数可变（比如升级到 8 个）：把角度档改成 `360 / N`，序号规则照 3.2.1 交替左右，就能保持对称。
