# 铝热剂手雷 系统记录

会话 `i1-records`，2026-11-01。静态记录，转写 APEX-REPORT 2.3 并补缺口，**有三处更正**（第 3 节标出）。

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_thermite_grenade.nut`，`txt` = `weapons/mp_weapon_thermite_grenade.txt`，`wu` = `vscripts/weapons/_weapon_utility.nut`。

## 0. 概要

- **道具**：军械 / 铝热剂 / `mp_weapon_thermite_grenade`（loot `survival_loot.csv:277`，tier 1）。
- **一句话**：扔到地面才点燃，横着铺一道贴地火墙（7 个火点，端点间 480 u），烧约 7.5 s；站在里面叠燃烧层，满层约 37 点/秒；AI 会躲。
- **分类**：效果、可视化（贴地蔓延的火墙）、系统（贴地铺开）。
- **可拆出的部件**：
  - 只在地面点燃 + 弹跳上限 → 3.1
  - 沿地面铺开一串点 → 3.2 `CreateSpreadPattern`
  - 一帧一个蔓延 → 3.3 `BurnSequence`
  - 燃烧层 → [I-BURN-STACK](../_shared/I-BURN-STACK.md)
  - AI 危险区 → 3.4
- **和 Fuse 大招的关系**：filter 说"沿地面走线和 Fuse 火焰环共用"。**不共用代码**。Fuse 有自己的 `FindValidEndPosForFireSegment`（`mp_weapon_mortar_ring_missile.nut:446`）和线段触发器；共用的只有 `TryApplyingBurnDamage`（只对道具）。

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 落点判定 | 碰撞回调，`normal.Dot(上) > 0.75`，否则弹开 | `nut:73-75` |
| 强制点燃 | 弹跳 > `projectile_ricochet_max_count` | `nut:64-71` |
| 不再爆炸 | `SetDoesExplode( false )` 后手动 `GrenadeExplode` | `nut:102`、`nut:154` |
| 火墙方向 | `Cross( 扔的水平方向, 法线 )` | `nut:95-97`、`nut:119-120` |
| 铺开 | 脚本 `TraceLine`，向前、向下 | `nut:381-497` |
| 蔓延 | 每段一个线程，段之间 `WaitFrame` | `nut:352-362` |
| 预燃 | 粒子 `mWall_CH_smoke_light`（服）/ `P_wpn_meteor_wall_preburn`（客），没伤害 | `nut:9-11`、`nut:369` |
| 燃烧 | 粒子 `P_wpn_meteor_wall`，控制点 1 = 上一个点 | `nut:13`、`nut:373`、`nut:508` |
| 伤害 | `FireSegment_DamageThink` | `nut:375`，见 I-BURN-STACK |
| AI 躲避 | `AI_CreateDangerousArea_Static` | `nut:374` |
| 环境声 | 只有开头、中段、结尾三段放声 | `nut:516-529` |
| 被烧音效 | 按伤害来源回调 `Thermite_DamagedPlayerOrNPC` | `_grenade.nut:117`、`wu:3991` |
| 手里发光 | `FadeModelIntensityOverTime` | `nut:35-52` |
| 落地小爆 | `explosion_damage 0`，半径 120 | `txt:61`、`txt:255`；只有效果 |

## 2. 流程

```
公共投掷流程（I-THROW-TOSS）
碰撞（不算扔的人自己）
  弹跳计数 +1
  法线朝上 或 超过 16 次 → 继续；否则按弹跳参数弹开
  PlantStickyEntity 失败且没到上限 → 返回（继续飞）
  点燃：
    inflictor = 共享 helper，寿命 burn_duration = 8 s   ← t=0
    方向 = Cross( 水平投掷方向, 法线 )
    一条 BeginFire 铺 +dir 4 步（含原点）
    一条 BeginFire 铺 −dir 4 步，去掉第一步
    GrenadeExplode
每个点（一帧一个）：预燃 0.5 s → 燃烧特效 + AI 危险区 + 伤害线程
t=8 s：inflictor 销毁 → 所有伤害线程结束 → 火灭
```

结束不依赖扔的人活着：`BeginFire` 只监听 `owner.OnDestroy`（`nut:340`）。`CleanUpPlayerAbilities` 只打断还没铺完的段（`nut:355`）。

## 3. 代码

### 3.1 碰撞：`OnProjectileCollision_weapon_thermite_grenade`（`nut:55-155`）

客户端版本 `nut:157-196` 只做到"粘住、不爆"。铺火都在服务端。

`nut:185-186` 客户端有 `IsPVEMode()` 分支（NPC 扔的时候把 `hitEnt` 换成世界）。这个函数本地有实现，说明 S21 客户端带 PvE 模式代码，但只是这一行。

### 3.2 铺开：`CreateSpreadPattern`（`nut:381-497`）

```
第 1 步：起点就是落点
之后每步：
  traceStart = lastDownPos + (0,0,80)
  newPos = pos + dir × 80
  向前 trace 到 (newPos.xy, traceStart.z − 40)
  通了 → 向下最多 225 找地；没地：跳过这步；有地：放点，pos = 向前 trace 终点
  挡了 → 向上 trace 到 (newPos.xy, traceStart.z + 80 × tan30°)
        碰到世界 → 跳过这步（pos 不变，之后每步都原地重试，等于停了）
        没碰到 → 向下最多 1000 找地；放点
```

**更正 APEX-REPORT 2.3 ①（爬高）**：APEX 写"最多爬高 46 u"。`80 × 0.577 = 46` 是**相对 traceStart** 的，而 traceStart 已经比上一个地面高 80。所以相对上一个地面，能翻过去的障碍高到约 **126 u**（推断，几何上的上限）。HSD 的 `ClimbMax = 46` 偏小。

向下的两条路长度不同：平路 225 u，翻越后 1000 u。

`staggerDegrees = 0`（`nut:395`），错位代码还在但没效果；所以是直线。

**实际点数**：起点 1 + 每边 3 = **7 点**，端点间 480 u。和 APEX 一致。`burn_segments 4` 指"每边 4 步，含原点"。

### 3.3 时序：`BurnSequence` / `DoSegment`（`nut:352-379`）

一帧一个。**更正 APEX-REPORT 2.3 ②（时长）**：

```
inflictor 寿命 8 s，从落地算（nut:142）
点开始烧 = 落地 + 0.5 s + 若干帧
FireSegment_DamageThink 监听 inflictor.OnDestroy（wu:4215），结束时 EffectStop
```

所以**实际燃烧约 7.5 s**，不是 8 s。外边的点还少几帧。燃烧特效自己的 Kill 定时（`0.5 + 8`，`nut:510-511`）比 inflictor 晚，不起作用。

**更正 ③（每层伤害）**：25–28，不是 24。见 [I-BURN-STACK](../_shared/I-BURN-STACK.md) 3.3。

### 3.4 AI 危险区（`nut:374`）

`AI_CreateDangerousArea_Static( burnEffect, inflictor, 半径 40, TEAM_INVALID, true, true, 点 )`。每个点一个，随特效消失。**PvE 有用**：火墙能真的把 NPC 挡开或逼走（语义原生，要实测）。

### 3.5 纵向火墙 mod

脚本里有 `vertical_firestar` 分支（`nut:115`：不转 90°、一条铺 8 步）。但 `.txt` 只有 `vertical_firestar_disabled`（`txt:314`，只改抛物线特效）。**本地这个 mod 不存在**，这条路走不到。HSD 的 `Thermite.alongThrow` 可以当升级，但 R5 里没有对照。APEX 2.3 写"有一个 mod"，要补这一句。

### 3.6 其他

`OnProjectileCollision_weapon_thermite_gun`（`nut:200-306`）：同一套铺火，给枪用，方向取法线水平分量。`npc_weapon_thermite_grenade.nut`：NPC 版，`savedDir = 敌人 − 自己`（第 40 行），NPC 投出来火墙横在目标方向。

### 3.7 依赖

[I-THROW-TOSS](../_shared/I-THROW-TOSS.md)、[I-BURN-STACK](../_shared/I-BURN-STACK.md)。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| `projectile_launch_speed` | 1300 | u/s | `txt:109` | | |
| `projectile_launch_pitch_offset` | 9 | ° | `txt:110` | | |
| `projectile_inherit_owner_velocity_scale` | 1 | | `txt:124` | | |
| `projectile_ricochet_max_count` | 16 | 次 | `txt:112` | 强制点燃 | |
| 地面判定 | 0.75 | 点积 | `nut:73` | ≈ 41° 坡 | 改小：陡坡也点燃 |
| 弹跳组 | 0.6 / 0.4 / 0.2 / 0.1 / 0.05 / 0.05 | | `txt:114-119` | | |
| `burn_segments` | 4 | 步/边 | `txt:69` | 火墙长度 | |
| `burn_segment_spacing_dist` | 80 | u | `txt:70` | 点距 | 大于 2×半径会有缝 |
| `burn_segment_radius` | 40 | u | `txt:67` | 火点半径 | 同时是 AI 危险区半径 |
| `burn_segment_height` | 48 | u | `txt:68` | 火点高度（底部 0） | 跳过去的高度 |
| `preburn_duration` | 0.5 | s | `txt:74` | 预燃 | |
| `burn_duration` | 8 | s | `txt:75` | **inflictor 寿命**，实际烧约 7.5 s | |
| `burn_damage` / `burn_time` / `burn_stacks_max` / `burn_stack_debounce` / `burn_tick_rate` | 25 / 2.8 / 4 / 0.7 / 1.2 | | `txt:76-80` | 见 I-BURN-STACK | |
| 下探（平路 / 翻越后） | 225 / 1000 | u | `nut:443`、`nut:474` | | |
| traceStart 抬高 | 80 | u | `nut:422` | | |
| 向前 trace 终点 | traceStart − 40 | u | `nut:423` | | |
| 向上 trace 终点 | traceStart + 46.2 | u | `nut:424` | | |
| `explosion_inner_radius` / `explosionradius` | 5 / 120 | u | `txt:60-61` | 小爆（无伤害） | |
| `explosion_damage` | 0 | | `txt:255` | | |
| `impulse_force` | 3000 | | `txt:62` | | |
| 屏幕震动 | 500 / 60 / 45 / 0.75 | | `txt:63-66` | | |
| `max_cook_time` / `grenade_ignition_time` | 4.5 / 6 | s | `txt:89`、`txt:92` | 写了但走不到（点燃时手动爆）；推断 | |
| `deploy_time` | 1.7 | s | `txt:95` | | |
| `toss_pullout_time` / `toss_time` / `toss_overhead_time` | 0.2 / 0.4 / 0.7 | s | `txt:106-108` | | |
| `stick_*` | 全 0 | | `txt:230-233` | 不粘人 | |
| `npc_min_range` / `max` | 500 / 1200 | u | `txt:226-227` | | |
| `npc_explosion_damage`（SP） | 10 | | `txt:284` | | |
| Fuse 被动 | 速度 × 1.7 | | `txt:323` | | |

## 5. 未解决和要实测的

- **对 NPC 的火**：`canBurn`、层数、DPS。`npc_dummie` 放进火里站 10 s，记血量曲线（I-BURN-STACK 的每层总伤害同时测）。
- **燃烧时长 7.5 还是 8**：记录每点特效存在时间。
- **AI 危险区对 NPC 的行为**：`npc_prowler` 追玩家，中间放一道火，看绕不绕。
- **火墙贴地形**（APEX 2.3 未解项）：台阶和坡上的实际形状；验证 126 u 翻越。
- 最后一刻入火后层是否继续打（I-BURN-STACK 第 5 节）。

## 6. HSD 实现

**已实现**：`Ordnance.cs` `Thermite`（`PointsPerSide 3`、`Spacing 80`、`PointRadius 40`、`PointHeight 48`、`Smoke 0.5`、`Burn 8`、`DropMax 225`、`ClimbMax 46`）。开关：`Thermite.alongThrow`（纵向，R5 本地没有）。

| 差别 | R5 | Unity | 差多少 |
|---|---|---|---|
| 燃烧时长 | 约 7.5 s（落地起 8 s 灭） | 每点预燃后完整 8 s（`Ordnance.cs:157`） | 约 0.5 s |
| 翻越高度 | 约 126 u（推断） | 46 u | 80 u，矮墙处差别明显 |
| AI 危险区 | 有 | 没有（要 AI 系统支持） | |
| 每层伤害 / 节拍 | 见 I-BURN-STACK 第 6 节 | | |

实测后再改，差别进 `R5-DIFF-ARCHIVE.md`。这份记录没改代码。
