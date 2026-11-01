# 公共部件 A：Nox 毒气云（伤害、减速、视觉）

批次 A 共用：Caustic 战术毒气陷阱（中号云 r282，11 s）和大招毒气手雷（大号云 r375，15 s）。伤害、减速、视觉逻辑**全在这一处**，两个技能的 SYSTEM.md 只写"怎么生成云"。静态研究，2026-10-31，会话 combat-a。

来源根目录：`research-src/s21-platform/scripts/`。`gas` = `vscripts/mp/sh_gas.gnut`（1456 行）。

## 0. 概要

- **部件**：`CreateGasCloudMediumAtOrigin` / `CreateGasCloudLarge` → `CreateGasExposureRadius`（服务端主循环）+ 两个伤害回调 + 客户端状态效果回调。
- **一句话**：在云心周围 24 个采样圆上，每 0.1 s 打一次"0 伤害的曝光"给进云时间计时，每 1.0 s 打一次真伤害，伤害 = 5 + floor(在云里秒数 / 2)，穿护盾；玩家进云 2 s 内减速线性升到 0.25，离开 2 s 内退掉；被毒的人对 Caustic 高亮（Nox Vision）。
- **分类**：好技能（持续伤害 + 减速 + 挡视线的区域）；系统（采样圆区域伤害 + 曝光计时 + 伤害按暴露时间递增）；可视化（屏幕毒气、调色、云粒子随墙裁剪）。
- **可拆出的部件**：
  - 采样圆区域 + 墙裁剪 → 3.2.1 `CreateGasExposureRadius`
  - 曝光计时（0 伤害探针）→ 3.2.2 `GasCloud_HandleGasExposure`
  - 暴露时间递增伤害 + 每攻击者每目标 1 s 节流 → 3.2.3 `GasCloud_RampDamageBasedOnExposureTime`
  - 减速随暴露时间升降 → 3.2.4 `GasExposureUpdate` / `GasExposure_ReapplyEffect`
  - 挡视线体积（挡 ping、挡钩爪）→ 3.2.1 `CreateTraceBlockerVolume`
  - 客户端表现（调色、屏幕粒子、可选景深）→ 3.3
  - 队友免疫光环（playlist 开关，默认关）→ 3.2.5

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 区域判定 | **不是触发器**：24 个点（离云心 r/2，每 15°）各打一次 `RadiusDamage(半径 r/2)` | `gas:760-786`、`gas:1068-1103`。并集覆盖半径 r 的圆盘 |
| 曝光 | `RadiusDamage(1.0, damageSourceId = damagedef_gas_exposure)`，攻击者 worldspawn，回调里把伤害设 0、记时间 | `gas:1068-1082`、`gas:236-280` |
| 伤害 | `RadiusDamage(1.0, damagedef_grenade_gas)`，回调里 `ScaleDamage(5 + floor(t/2))` | `gas:1088-1102`、`gas:503-572` |
| 穿护盾 | `DF_BYPASS_SHIELD`（另 `DF_NO_HITBEEP`、`DF_NO_SELF_DAMAGE`） | `gas:55` |
| 墙挡 | `SF_ENVEXPLOSION_MASK_BRUSHONLY`：只被世界刷子挡（引擎） | `gas:1077` |
| 粒子裁剪 | 每个采样方向从云心 TraceLine，撞墙的方向不生成 / 删掉粒子 | `gas:916-1048` |
| 挡视线 | `CreateTraceBlockerVolume`（盒 −20..35 × 100 高），内容 `BLOCK_PING | NOGRAPPLE | BLOCKLOS`，队伍 = Caustic 队 | `gas:962-963`、`gas:1016-1017` |
| 减速 | 状态效果 `move_slow`，严重度 0.25 × 暴露系数 | `gas:490`、`gas:497` |
| 转向减速 | 注释掉（原 0.3） | `gas:491`、`gas:498` |
| 屏幕 | 状态效果 `gas_cloud` → 客户端调色 `gas_cloud.raw_hdr` + 屏幕粒子 `P_caustic_gas_FP`；景深只在 playlist `caustic_gas_causes_DOF_blur`（默认 false） | `gas:120-122`、`gas:1218-1248` |
| 高亮 | 出生时给所有角色设 `Highlight_SetEnemyHighlight(ent,"enemy_sonar")`；状态变化时 `ManageHighlightEntity` | `gas:217-224`、`gas:1220`、`gas:1266` |
| 结束余留 | 云寿命到后再留 `DIRTY_BOMB_CLOUD_LINGER_TIME` 2 s（只伤害，不画粒子） | `gas:1113-1121`；常量在 `mp_weapon_dirty_bomb.nut:31` |
| 粒子提前消失 | 结束前 3.5 s 粒子和挡视线体积删掉 | `gas:1052-1065` |
| 声音 | 云体 `GasGrenade_GasCloud`；被毒 `gruntcooper_wounded_loop_1p`，有防毒（Caustic 自己）`Caustic_Gas_Breath_Loop_1p` | `gas:64-66`、`gas:354-369` |

服务端 / 客户端：判定、伤害、减速在服务端；屏幕和高亮在客户端。**SDK 痕迹**：`GasCloud_HandleGasExposure_Copy`、`GasCloud_RampDamageBasedOnExposureTime_Copy`（`gas:282`、`gas:575`）是给 Wattson 电桩用的复制版，带 "TeslaTrap: scalling damage" 调试输出和注释 "debug here for tesla trap, why dmg mult is so high"（`gas:619`）——很像社区补的；主函数里 `#if DEVELOPER printt` 也多。数值部分是否被改不确定，见第 5 节。

## 2. 流程

```
技能生成云（CreateGasCloud*）→ thread CreateGasExposureRadius
 ├ 生成两个 inflictor：曝光用（team = Caustic）、伤害用（scriptName "caustic_trap_gas"，boss = Caustic）
 └ 每 0.1 s：
     ├ 云心 = 来源实体位置（可随移动平台走）
     ├ 24 个方向：TraceLine 云心→采样点，生成 / 移动 / 删除粒子和挡视线体积
     ├ 每个采样点：RadiusDamage(曝光, r/2)
     ├ 距上次伤害 ≥ 1.0 s（或刚开始）：每个采样点 RadiusDamage(伤害, r/2)
     ├ 剩 3.5 s：删粒子
     └ 寿命到（或来源实体没了）：再延 2 s，然后结束
目标被"曝光"打到：
 ├ 第一次 → gasEnterTime = now，thread GasExposureUpdate
 └ 每次 → gasLastExpoTime = now
GasExposureUpdate（每帧，只对玩家有效，见 3.2.4）：
 ├ 在云里（距上次曝光 ≤ 0.2 s）：系数 = clamp((last-enter)/2, 0, 1) → gas_cloud(系数) + move_slow(0.25×系数)
 └ 离开：系数从 1 线性降到 0，用时 min(在云时间, 2.0)（有防毒 0.5）→ 到 0 结束，清零 enter/last
目标被"伤害"打到：
 ├ 有防毒（Caustic 被动 / 队友光环）→ 0
 ├ 不在云里 → 不改（即 1 点基础伤害，推断几乎不会发生）
 ├ 同一个攻击者对同一目标 1.0 s 内已结算过 → 0
 └ 伤害 = 1 × max(5, 5 + floor((last-enter)/2))
```

## 3. 代码

### 3.1 入口

| 函数 | 行 | 半径 | 粒子 | 说明 |
|---|---|---|---|---|
| `CreateGasCloudLarge( projectile, duration, offset )` | `gas:646-697` | `GAS_CLOUD_RADIUS_LARGE` 375 | `P_smokescreen_poison` ×4（偏移 ±275, 40） | ownerTeam = TEAM_UNASSIGNED，`fxPointCP1toCenter = true` |
| `CreateGasCloudMediumAtOrigin( source, player, origin, duration )` | `gas:699-739` | `GAS_CLOUD_RADIUS_MEDIUM` 282 | `P_gastrap_fill` ×1 | ownerTeam = 玩家队 |

两者都：`dpsPilot = 1`、`damageTickRate = 1.0`、`dangerousAreaRadius = r × 1.5`（字段赋值了，但 `CreateGasExposureRadius` 里没用到 AI 危险区，推断：AI 不躲毒气）、`blockLOS = true`。

### 3.2 核心逻辑

#### 3.2.1 `CreateGasExposureRadius`（`gas:750-1123`）

```
offset = r / 2
pts = [ center + polar(15°·k, offset) for k in 0..23 ]
loop every 0.1 s until endTime (+2 s linger):
    doDamage = now - lastDamage ≥ 1.0  or 第一帧
    for each pt:
        tr = TraceLine(center, pt, ignore 其他毒气源, MASK_SOLID)
        粒子 / 挡视线体积：tr 没撞墙才放（k = 0 的方向从不放粒子，推断是 bug：i 从 1 开始建表 gas:789）
        RadiusDamage(pt, worldspawn, expoInflictor, 1, r=offset, BRUSHONLY, gas_exposure)
        if doDamage: RadiusDamage(pt, caustic, dmgInflictor, 1, r=offset, BRUSHONLY, grenade_gas)
```

- 伤害球心是 **pt 本身**（不受墙裁剪），只有 `BRUSHONLY` 的 LOS 让墙挡（`gas:1070`）。粒子按裁剪位置画 → 墙后可能"看不到毒但吃伤害"或反过来（推断）。
- inflictor 带 `onlyDamageEntitiesOncePerTick = true`（`gas:804`、`gas:834`）：同一帧 24 个球只算一次（推断，引擎 / `_damage` 里用）。

#### 3.2.2 曝光：`GasCloud_HandleGasExposure`（`gas:236-280`）

伤害设 0；跳过 `caustic_trap`、`tesla_trap`；只处理玩家、NPC、电桩；同一帧只记一次；第一次进云时开 `GasExposureUpdate` 线程。

#### 3.2.3 伤害：`GasCloud_RampDamageBasedOnExposureTime`（`gas:503-572`）

```
if 目标是毒气罐 / 电桩: 不改（= 1 点，罐本身另有过滤）
if 玩家且有防毒: ×0
if !IsEntInGas(目标): return
if now - attacker.sharedGasDamageHelper[目标] < 1.0: ×0      // 同一 Caustic 的多朵云不叠
mult = max(5, 5 + floor((lastExpo - enterTime) / 2))
×mult；记 gasLastDamageTime；记 helper 时间
```

**每秒伤害**：第 0–1 s 5、2–3 s 6、4–5 s 7……（t 秒时 5 + ⌊t/2⌋）。`GAS_CLOUD_DMG_MAX = 10`（`gas:51`）定义了但没用 → **没有上限**。在 11 s 陷阱里一直站着，总伤害 ≈ 5+5+6+6+7+7+8+8+9+9+10(+2 s 余留 10+11) ≈ 101（推断，按公式）。

#### 3.2.4 减速：`GasExposureUpdate`（`gas:330-446`）+ `GasExposure_ReapplyEffect`（`gas:448-501`）

```
友军（emitterTeam 和目标同队）：只加 gas_cloud 视觉，不减速
每帧（只当 target.IsPlayer()）:
    inGas = now - lastExpo ≤ 0.2
    inGas:  k = clamp((last - enter) / 2.0, 0, 1)
    !inGas: wear = min(tInGas, 2.0)（有防毒 0.5，最少 0.1）
            k = GraphCapped(now - last, wear, 0, 0, 1)        // 从 1 线性到 0
            k == 0 → 线程结束，enter/last/damage 时间清回 -1
    ReapplyEffect: 停掉旧句柄，加 gas_cloud(k)、move_slow(0.25k)（玩家有防毒则不减速）
```

**NPC 问题（重要）**：循环体整个包在 `if ( target.IsPlayer() )` 里（`gas:416`）。NPC：
- 不吃减速（ReapplyEffect 里有 NPC 分支 `gas:494-499`，但根本不会被调到）；
- 线程永远不退出 → `gasEnterTime` 永不清零 → `IsEntInGas` 一直 true、暴露时间一直从第一次进云算 → **NPC 离开毒气再进来，伤害从更高的倍率开始**；而且离开后只要被任何毒气伤害球扫到就按旧计时算。
是原版还是 SDK 改的不确定（第 5 节）。

#### 3.2.5 队友免疫光环（`gas:129-215`）

Caustic 有 `PAS_GAS_GEAR` 且 playlist `caustic_teammate_protection`（默认 false）时，身边 368 / 400 u 两个圆柱触发器给队友 `PAS_GAS_PROTECTION`。默认关。

### 3.3 客户端表现

- `GasCloud_StartVisualEffect`（`gas:1218-1248`）：高亮刷新；本地玩家：调色线程（0.25 s 淡入到严重度，`gas:1137-1170`）、无防毒时屏幕粒子（控制点 1 = 严重度）、可选景深（sin(4t) 振荡，`gas:1172-1216`）、Chroma 灯效。
- `GasCloud_StopVisualEffect_Thread`（`gas:1255-1286`）：有 `PAS_GAS_HIGHLIGHT` 时高亮多留 5 s（`GAS_ENEMY_HIGHLIGHT_TIME_UPGRADE`）。
- 队友免疫 HUD + 地面光圈（`gas:1317-1438`）。

### 3.4 依赖

`RadiusDamage`（引擎）、`CreateTraceBlockerVolume`、`CreateScriptRef`、状态效果 `gas_cloud`、`move_slow`、被动 `PAS_GAS_GEAR`、`PAS_GAS_PROTECTION`、`PAS_GAS_HIGHLIGHT`。`DIRTY_BOMB_CLOUD_LINGER_TIME` 定义在 `mp_weapon_dirty_bomb.nut:31`（文件间耦合）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| GAS_CLOUD_RADIUS_LARGE | 375 | u | `gas:27` | 大招云半径 | |
| GAS_CLOUD_RADIUS_MEDIUM | 282 | u | `gas:28` | 陷阱云半径 | |
| GAS_CLOUD_RADIUS_SMALL | 128 | u | `gas:29` | 未用 | |
| 采样点 | 24 个，离心 r/2，每 15° | — | `gas:760-786` | 判定形状 | 少 → 边缘有缝 |
| 采样球半径 | r/2 | u | `gas:760` | | |
| GAS_CLOUD_EXPOSURE_TICK_RATE | 0.1 | s | `gas:57` | 曝光 / 主循环间隔 | |
| "在云里"判定 | 0.2（= 2 × 0.1） | s | `gas:419` | 多久没曝光算离开 | |
| GAS_CLOUD_DMG_TICK_RATE | 1.0 | s | `gas:46` | 伤害间隔 + 每攻击者节流 | |
| 基础伤害 | 1 | HP | `gas:1093`（`dpsPilot` 未用） | × 倍率 | |
| GAS_CLOUD_DMG_MIN / FLAT | 5 / 5 | — | `gas:49-50` | 倍率起点 / 下限 | |
| GAS_CLOUD_DMG_EXPOSURE_INTERVAL | 2.0 | s | `gas:48` | 每 2 s 倍率 +1 | 小 → 涨得快 |
| GAS_CLOUD_DMG_MAX | 10 | — | `gas:51` | **未用**（无上限） | |
| GAS_CLOUD_DMG_DELAY | 1.0 | s | `gas:47` | 未用 | |
| GAS_CLOUD_MOVE_SLOW_EFFECT_WEIGHT | 0.25 | 严重度 | `gas:39` | 满减速 | |
| GAS_CLOUD_TURN_SLOW_EFFECT_WEIGHT | 0.3 | 严重度 | `gas:40` | 未用 | |
| GAS_CLOUD_EFFECT_BUILD_TIME | 2.0 | s | `gas:42` | 减速 / 屏幕升满用时 | |
| GAS_CLOUD_WEAR_OFF_NORMAL / GAS_GEAR | 2.0 / 0.5 | s | `gas:43-44` | 离开后退掉用时（上限） | |
| GAS_CLOUD_SLOW_DURATION | 2.0 | s | `gas:52` | 未用 | |
| GAS_CLOUD_FADE_TIME | 3.5 | s | `gas:60` | 粒子提前消失 | |
| DIRTY_BOMB_CLOUD_LINGER_TIME | 2.0 | s | `mp_weapon_dirty_bomb.nut:31` | 结束后余留伤害 | |
| 伤害 flags | NO_HITBEEP, BYPASS_SHIELD, NO_SELF_DAMAGE | — | `gas:55` | 穿盾 | |
| 挡视线盒 | (−20,−20,−16)–(35,35,100) | u | `gas:963` | | |
| GAS_TEAMMATE_PROTECTION_RADIUS | 400 | u | `gas:20` | 默认关 | |
| GAS_ENEMY_HIGHLIGHT_TIME_UPGRADE | 5.0 | s | `gas:54` | 被动升级 | |
| GAS_CLOUD_RADIUS_MULTIPLIER_UPGRADE | 1.2 | × | `gas:53` | 未用 | |
| damagedef_grenade_gas / gas_exposure | 1 dmg，r400 | — | `damage/damagedefs.txt:332-357` | 只给 sourceId 用 | |

实测（R5，2026-11-01，NPC）：每跳 5 + floor(t / 2)，无上限，离开不重置；NPC 不减速。见 W2-RUNTIME §3。

## 5. 未解决和要实测的

1. **NPC 在毒气里：减速有没有、伤害倍率会不会离开后还在涨**（最重要，PvE 的敌人全是 NPC）。测法：火力训练场刷一个 `npc_dummie`（它在出生回调列表里，`gas:108`），扔大招毒气，用 runner 每 0.1 s 记录 dummy 血量、速度；让 dummy 走出 10 s 后再走进，看第一跳伤害是 5 还是更高。
2. **伤害倍率无上限是否原版**：同上，站在云里 15 s 记录每跳伤害，看到 12 s 后是不是 11、12。对照：Apex 官方补丁说明里 Nox 毒气是"5 起、每跳 +1、上限 10"（**记忆，未查证**），如果实测超过 10，就是 SDK 漏了上限。
3. 墙后裁剪：一半云穿进墙时，墙另一侧是否吃伤害（伤害球不裁剪，只靠 BRUSHONLY LOS）。
4. `onlyDamageEntitiesOncePerTick` 是否真把 24 个球去重：站在云心（会被多个球覆盖）看单跳伤害是否 5（不是 5 × 球数）。
5. 移动减速 0.25 的实际速度倍率：同 `A-shellshock.md` 第 5 节。

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
1. ✅ **NPC 不减速**（move_slow 全程 0）；✅ **离开再进来接着涨**：dummie 在云里 25 s 后移出 10 s，回来第一跳 23（= 5 + floor(37 / 2)），`gasEnterTime` 一直不重置。
2. ✅ **没有上限**：每 1 s 一跳 5, 5, 6, 6, …, 25 s 时 17，49 s 时 29。和"上限 10"不符。只测了 NPC；玩家这边本地测不了（只有一个玩家，自己的云不打自己）。
3、4 没测。5 见 `A-shellshock.md`（0.25 = ×0.75）。
注意：`CreateGasCloudMediumAtOrigin` 结束时 `Destroy()` 它的 source；云主必须是玩家（`SetBossPlayer`）。

## 6. HSD 实现

**未实现**。建议：

- 新建 `Runtime/Combat/GasCloud.cs`：`GasCloud : ICombatEntity`（中心、半径、寿命、余留、来源单位）+ 每个单位一个 `GasExposure` 记录（`enter`、`last`），**放在 `CombatUnit` 上**（加两个字段），不要做成全局表。
- 判定直接用"点到云心水平距离 ≤ r 且高度在 [z−16, z+100]"，再加一条 `CombatSim.WorldClear(云心, 单位中心)`，比 24 个采样球简单，结果几乎一样（差在边缘的花瓣形，差多少要等第 5 节 3 的实测）。差别写进 `R5-DIFF-ARCHIVE.md`。
- 伤害公式照 3.2.3，但 **给上限 10**（开关 `hsd.combat.gasDmgCap`，默认开，关掉 = 按本地脚本无上限）；**NPC 和玩家走同一条曝光 / 退出逻辑**（修掉 3.2.4 的 NPC 问题；开关 `hsd.combat.gasNpcR5Bug` 默认关）。
- 减速复用 `CombatUnit.slowScale`，每帧按 `k` 设 `slowScale = 1 − 0.25k`（待 `move_slow` 换算确认）。
- 穿护盾：`DamageInfo` 加一个 `bypassShield` 标志（HSD 目前统一血量，暂时不用）。
- 视觉：`CombatVisuals` 画半透明绿色圆柱；玩家在云里时 `CombatHud` 叠绿色调色，强度 = k。
