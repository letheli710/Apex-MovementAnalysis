# Caustic 大招 Nox Gas Grenade（毒气手雷）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_grenade_gas.nut`（253 行），`txt` = `weapons/mp_weapon_grenade_gas.txt`。毒气云的伤害、减速、视觉**全部**见 [`_shared/A-gas-cloud.md`](../_shared/A-gas-cloud.md)；本文只写手雷本身和大招专属的部分。静态研究，2026-10-31，会话 combat-a。

## 0. 概要

- **技能**：Caustic / 大招 / Nox Gas Grenade / `mp_weapon_grenade_gas`。
- **一句话**：扔一颗毒气手雷，落到平地（或弹 10 次后）1 s 后炸开成大号毒气云（r375，15 s + 2 s 余留），伤害 / 减速规则和陷阱完全一样。
- **分类**：好技能（大面积持续伤害 + 减速 + 挡视线）；系统（复用公共毒气云）；可视化（手里手雷发光）。
- **可拆出的部件**：
  - 落地才激活的投掷罐 → `_shared/A-ground-canister.md`
  - 毒气云 → `_shared/A-gas-cloud.md`
  - 云跟随移动平台（云源挂父物体）→ 3.2
  - 毒气里回血（升级被动）→ 3.2.2

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 手雷 | `Grenade_OnWeaponToss(weapon, params, 1.0)`；1500 u/s，仰角 8° | `nut:86-92`；`txt:98-99` |
| 手里发光 | `P_wpn_grenade_gas_glow_FP/3P` 挂 `FX_TRAIL` | `nut:24-25`、`nut:75-84` |
| 落地 | `PlantStickyEntityOnWorldThatBouncesOffWalls(…, 0.7, ZERO, ignoreHullTrace = true)`；粘不上但已弹 ≥ 10 次也算 | `nut:116-123` |
| 预警 | 落地后哔声 `weapon_vortex_gun_explosivewarningbeep` | `nut:149` |
| 炸开 | `projectile.GrenadeExplode(<0,0,1>)`（特效表 `exp_grenade_gas`，`.txt` 伤害 0） | `nut:225`；`txt:226-231` |
| 云源 | `CreateScriptMover`，有父物体（移动平台）时挂上去 | `nut:229-242` |
| 云 | `CreateGasCloudLarge(dummyCloudSource, 15.0, offset (0,0,16))` | `nut:246` |
| 追踪视野 POI | `TrackingVision_CreatePOI(PLAYER_ABILITIES_GAS)`（Bloodhound 被动能看到痕迹） | `nut:244` |
| 毒气回血（升级） | 被动 `PAS_GAS_HP_REGEN`：吃到毒气伤害（被免疫成 0）时 `EntityHealResource_Add(2 HP/s)`；1 s 没再吃到就停；被缩圈伤害打到后 2 s 内不回 | `nut:40-71`、`nut:167-202`；调用处 `vscripts/mp/_codecallbacks.gnut:238-241` |

## 2. 流程

```
按大招（120/120）→ 拿出 0.7 s → 松开 → 0.45 s 出手（过头 0.75 s）
手雷弹跳（浅 0.53、陡 0.32）→ 平地（或第 10 次碰撞）→ 不再碰撞（NotSolid）、点燃
 └ DeployGas
     t=0.0  哔
     t=0.8  检查扔的人还在、队伍没被淘汰
            DeployGas_Internal: 手雷 GrenadeExplode
     t=1.0  生成云源 → 大号毒气云 15 s
     t=16 … 18  余留 2 s 后结束（_shared/A-gas-cloud.md）
```

`WEAPON_GAS_GRENADE_DELAY - 1.0 = 0` 的 wait（`nut:147`）是改过的遗留：原来延迟可能更长（推断）。扔的人销毁 → 云线程结束（`nut:224`）。

冷却：MP 120 / 1 每秒 = 120 s（`txt:213-224`）；SP（单人）是 4 发可拾取的普通手雷（`txt:235-254`）。

## 3. 代码

### 3.1 入口

- `OnWeaponTossReleaseAnimEvent_weapon_greande_gas`（`nut:86-92`，函数名拼写错误 greande 是原版的）。
- `OnProjectileCollision_weapon_grenade_gas`（`nut:95-130`）。

### 3.2 核心逻辑

#### 3.2.1 `DeployGas` / `DeployGas_Internal`（`nut:134-249`）

见第 2 节。`GetGasDuration`（`nut:204-215`）里升级时长 ×1.2（playlist `upgraded_caustic_gas_duration`）的分支被注释掉 → 恒 15 s。

#### 3.2.2 毒气回血升级（`nut:39-202`）

```
被动获得 → 挂伤害回调；记 nextAllowedHeal = now
受到 deathField（缩圈）伤害 → 停回血，nextAllowedHeal = now + 2
受到毒气伤害（_codecallbacks 里，伤害被置 0 前）→ StartHealing:
    没有回血句柄且 now > nextAllowed → EntityHealResource_Add(2.0, 2.0, …)
    1 s 内没再触发 → 移除句柄
```

本地化："Regen HP inside Nox Gas."（`localization_english.txt:20638`）。

### 3.3 客户端表现

手里发光；抛物线 `P_arc_green_bounce`（`txt:33-34`）；云的屏幕表现见共享记录 3.3。

### 3.4 依赖

`_shared/A-gas-cloud.md`、`_shared/A-ground-canister.md`、`Grenade_OnWeaponToss`（`vscripts/weapons/_grenade.nut`）、`EntityHealResource_*`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| WEAPON_GAS_GRENADE_DELAY | 1.0 | s | `nut:18` | 落地到出毒（实际 0 + 0.8 + 0.2） | |
| WEAPON_GAS_GRENADE_DURATION | 15.0 | s | `nut:19` | 云寿命 | |
| 升级时长倍率 | 1.2（注释掉） | × | `nut:162-165` | 不生效 | |
| WEAPON_GAS_GRENADE_OFFSET | (0,0,16) | u | `nut:20` | 云心抬高 | |
| 云半径 | 375 | u | `sh_gas.gnut:27` | | |
| 最多碰撞次数 | 10 | 次 | `nut:120` | 兜底 | |
| 出手速度 / 仰角 | 1500 / 8 | u/s / ° | `txt:98-99` | | |
| 弹跳 浅 / 陡 / 法向 / 随机 / 竖直随机 / 滚动 | 0.53 / 0.32 / 0.5 / 0.2 / 0.2 / 0.1 | — | `txt:87-92` | | |
| toss_pullout / toss / overhead | 0.7 / 0.45 / 0.75 | s | `txt:95-97` | | |
| grenade_ignition_time | 20 | s | `txt:76` | 点燃后引擎寿命上限（推断） | |
| UPGRADE_CAUSTIC_GAS_HP_REGEN_DELAY | 2.0 | s | `nut:7` | 缩圈伤害后多久不回血 | |
| 回血速率 | 2.0 HP/s | — | `nut:172`、`nut:179` | | |
| 回血停止 | 1.0 | s | `nut:190` | 多久没吃毒就停 | |
| 充能（MP） | 120，1/s | — | `txt:213-224` | 120 s | |

## 5. 未解决和要实测的

- 毒气云的所有实测项见 `_shared/A-gas-cloud.md` 第 5 节（NPC 减速、伤害上限、墙后伤害）。用大招测比陷阱方便（云大、15 s）。
- 落地到出毒的实际时间（1.0 s）：runner 记录手雷消失时刻和第一次 `gas_exposure` 伤害事件时刻。
- 毒气回血的条件里用的是 `deathField`（缩圈），看起来像"在毒里回血，但被圈打就暂停"——合理，但实现方式（挂在伤害回调里判断 sourceId）是 SDK 风格还是原版无法判断。HSD 不用这个升级，低优先级。

## 6. HSD 实现

**未实现**。`NoxGrenade : ThrownItem`（`ThrowParams{ launchSpeed = 1500, pitchOffset = 8, shallow 0.53, sharp 0.32, alongNormal 0.5 }`），`OnBounce` 用 `_shared/A-ground-canister.md` 的落地判定（另加"第 10 次也算"），落地 1.0 s 后生成 `GasCloud(r = 375, life = 15, linger = 2)`。全部伤害 / 减速走共享 `GasCloud.cs`。开关 `hsd.combat.ult.noxGrenade`。
