# Horizon 大招 Black Hole（黑洞 / N.E.W.T.）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_horizon_black_hole.nut`（1318 行），`txt` = `weapons/mp_ability_horizon_black_hole.txt`。拉力：`research-src/s21-r5sdk/src/game/server/trigger_gravity.cpp`（1389 行，SDK 的服务端实现）。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Horizon / 大招 / Black Hole / `mp_ability_horizon_black_hole`。
- **一句话**：扔出 N.E.W.T. 无人机（1300 u/s，重力 ×0.75），落地 1.75 s 后展开黑洞：半径 400、上下各 200 的圆柱，持续 0.8 s 强拉 + 10 s 普通拉。**对玩家**：每个移动 tick 把速度往中心加（外圈 300 / 内圈 400，强拉期 +200），速度上限 400；想往外跑时外向水平速度被压到 85–135。**对 NPC**：直接接管——挂到一个 mover 上，1.2 s 内拖到离中心 40 u 处，按住直到黑洞结束。不造成伤害。
- **分类**：好技能（PvE 聚怪价值最高）；系统（区域拉力 + 对 NPC 的强制定身；投射物也会被吸）；可视化（黑洞粒子、无人机推进器）。
- **可拆出的部件**：
  - 玩家拉力公式（拉 / 限速两个分支、强拉期、友军减半）→ 3.2.2 `TriggerGravity_ApplyBlackholeForce`
  - 拉力的视线门（11 个探测点、两段 trace）→ 3.2.2 `TriggerGravity_CanBlackholeSeePlayer`
  - NPC 定身拉拽（mover 接管）→ 3.2.3 `BLACKHOLE_InTriggerThread`
  - 投射物吸引 → 3.2.4 `BLACKHOLE_PullThrowableThread`
  - 部署体（可被打掉，爆炸伤害 ×1.5）→ 3.2.1

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 投掷 | `ThrowDeployable(weapon, params, 1.0, BLACKHOLE_ProjectileLanded, null, <0,0,400>)`；1300 u/s，仰 7°，重力 0.75，弹跳 0.7 / 0.1 / 0.01 | `nut:259-298`；`txt:62,112-117` |
| 落地 | 法线方向向下 32 trace 找表面，姿态贴表面；落在非世界的可粘实体上 → 跟着它 | `nut:1281-1318` |
| 无人机 | `CreatePropScript`，血 175（升级 90），可被打；爆炸伤害 ×1.5；Crypto EMP 秒杀 | `nut:327-385`、`nut:790-835` |
| 拉玩家 | `trigger_cylinder_heavy` + `SetTriggerType(TT_BLACKHOLE)` + `SetBlackholeParams(200, 300, 400, 85, 135, 100)` + `SetBlackholeIsStrongPulling(true)`（0.8 s 后 false） | `nut:647-708`。力在**引擎**；本地服务端由 SDK `trigger_gravity.cpp` 实现 |
| 拉 NPC / 医疗无人机 / Crypto 无人机 | 脚本：`CreateOwnedScriptMover(ent)` → `SetParent(mover)` → `NonPhysicsMoveTo(中心 + 40·方向, 1.2 s)` | `nut:942-1075` |
| 吸投射物 | 第二个实体 `vortex_sphere`（半径 400，`SF_ABSORB_CYLINDER \| SF_ABSORB_BULLETS`），手雷进入 → 每帧速度 += 指向中心 × 80 | `nut:576-645` |
| 状态 | `in_black_hole_field`（Endless），客户端开关 1P 特效 | `nut:977`、`nut:1202-1268` |
| 开门 | `TryOpenAndBreakDoors` | `nut:548` |
| 挡 ping | `CreateTraceBlockerVolume(上 55，半径 64)` | `nut:415` |

**可疑 / SDK**：玩家拉力在 S3 dedi 上是 SDK 用 C++ 重写的（`trigger_gravity.cpp` 头注释"Server-authoritative TT_GRAVITY_LIFT / TT_BLACKHOLE force"；常量注释"S21-folded constants"，即按 S21 客户端二进制里的折叠常量还原）。ConVar `bridge_trigger_blackhole` 的说明写着：关掉它时"服务端从不拉，玩家被拉回（rubber-band）"——说明 S21 客户端自己会预测同一套拉力，SDK 版本是为了和客户端对上。可信度较高，但仍是还原，第 5 节列为要实测。

## 2. 流程

```
按住（toss_pullout 0.5）→ 预览落点和半径（ShowBlackHoleRadius）
松开（toss_time 1.0）→ 投出无人机（推进器特效）
落地 → BLACKHOLE_MainLifetimeThread：
 ├ 0 s：生成无人机（可被打），展开动画，START 特效（CP1 = 半径 400）
 ├ 0.75 s（= 1.75 − 1.0）：MAIN 黑洞特效开始（提前 1 s 预警）
 ├ 1.75 s（升级 0.9）：建吸投射物的 vortex；BLACKHOLE_PullTriggerThread：
 │     建 TT_BLACKHOLE 触发器（半径 400、上下 200），强拉开
 │     0.8 s 后强拉关
 │     再 10 s
 ├ 触发器销毁 → 所有被定住的 NPC 放开（ClearParent、停动画）
 └ 关特效 → 收起动画 → 溶解 1 s
被打掉：爆炸特效；退还 25% 能量（升级值，`nut:86,158`）
```

时间线：落地 → 1.75 s 开始拉 → 2.55 s 强拉结束 → 12.55 s 结束。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_weapon_black_hole`（`nut:259`）→ 落地回调 `BLACKHOLE_ProjectileLanded`（`nut:1281`）→ `BLACKHOLE_MainLifetimeThread`（`nut:387`）。

### 3.2 核心逻辑

#### 3.2.1 无人机

`CreateNewtProp`（`nut:327`）：血 = playlist `blackhole_trophy_health_amount` 或 175（升级 90）。`BLACKHOLE_NEWT_OnDamaged`（`nut:790`）：友军伤害无效；毒圈伤害在 ring_immunity 时无效；爆炸 ×1.5；Crypto EMP 陷阱 = 直接打满血量。

#### 3.2.2 玩家拉力（`trigger_gravity.cpp:1013` `TriggerGravity_ApplyBlackholeForce`）

参数（脚本传入顺序 `SetBlackholeParams(strongAddl, outerPull, innerPull, outerMove, innerMove, innerRadius)`）= (200, 300, 400, 85, 135, 100)；radius = 触发器半径 400。

每个玩家、每个移动 tick（在 `Hook_JumpPad_ApplyLaunchPass` 之后调用）：

```
d = 黑洞中心 − 玩家原点；dist = |d|；n = d / dist     // n 指向中心（3D）
if dist > 100 且 看不见（见下）→ 不施力
跳过：跳板后 1 s 内、相位免疫、traverse 移动、挂墙、跑墙、Newcastle 跳跃中
ally   = 同队
strong = 强拉期（前 0.8 s）
pullIn = 400, pullOut = 300
if strong 且 非 ally: pullIn += 200; pullOut += 200        // 600 / 500
capBranch = 钩爪拉人中 或（有移动输入 且（非 strong 或 ally））

if capBranch:                    // "想跑"分支：只限速，不加力
    ms = Graph(dist, 0→400, 135→85)                     // 中心 135，边缘 85
    ally → ms ×2；钩爪 → ms ×2.5
    if 速度方向背离中心（dot(v̂, n) < 0）且 水平速度 > ms:
        水平速度缩放到 ms
else:                            // "不动 / 强拉"分支：加力
    pull = dist ≥ 100 ? Graph(dist, 100→400, pullIn→pullOut) : 0
    v += n × pull                                       // 每 tick 加一次，不乘 dt
    clamp = 400（ally 200）                             // 用的是没加强拉的 innerPull
    |v| > clamp → 缩放到 clamp
    if 原 v.z ≤ 0: v.z = 原 v.z                         // 正在下落 / 站地时不改竖直速度
```

要点：
- **强拉期（0.8 s）里敌人有没有输入都走加力分支**，所以前 0.8 s 无法逃；之后有移动输入就只被"限速"，没输入才被拉。
- 加力分支每 tick 加 300–600，几乎一两个 tick 就到上限 400，所以实际效果是"速度直接变成朝中心 400"（推断）。
- 友军也会被拉（ally 只是上限减半、逃跑速度 ×2）。
- 中心 100 内：不加力（pull = 0），只有 clamp。

视线门 `TriggerGravity_CanBlackholeSeePlayer`（`trigger_gravity.cpp:497`）：

```
base = 中心 + (0,0,64)
候选 = base + 32 × {(0,0,0),(0,0,2),(0,0,−1.5),(0,±2,0),(±2,0,0),(±1.4,±1.4,0)}   // 11 个
任一候选：候选→玩家胸 trace 通，且 候选→中心 trace 通 → 看得见
```

#### 3.2.3 NPC 定身（`BLACKHOLE_InTriggerThread`，`nut:967`）

```
进入触发器的 NPC / 医疗无人机 / Crypto 无人机（且没有 in_black_hole_field）:
    加 in_black_hole_field
    友方 → 撤状态，return
    mover = CreateOwnedScriptMover(ent)；ent.vel = 0；ent.SetParent(mover)
    目标 = 中心 + 水平(ent − 中心).normalized × 40
    mover.NonPhysicsMoveTo(目标, 1.2 s)
    之后每帧 NonPhysicsMoveTo(目标, 0.1 s)，直到黑洞结束
结束：ClearParent，停动画，撤状态
```

和玩家完全不同：**NPC 没有物理拉力，直接被搬到 40 u 圈上并定死 ~10 s**，不看视线、不看高度差（只要碰到触发器）。这对 PvE 聚怪非常强。

#### 3.2.4 投射物（`nut:610-645`）

vortex 球只对 `grenade` 类投射物起线程：每帧 `v += 指向中心 × 80`，直到和中心高度差 < 10。没有上限、不乘 dt（推断：帧率相关）。

### 3.3 客户端表现

- 预览：落点 + 半径圈（`ShowBlackHoleRadius`，`nut:221`）。
- 无人机：3 个推进器 + 核心光；START 特效（CP1 = <400,0,255>、CP2 = <50,40,125>），提前 1 s 换 MAIN 特效（CP2 红）。
- 1P：`in_black_hole_field` 开 → `Blackhole_Start1PFX`（`nut:1202`）屏幕特效。
- 受伤特效间隔 0.25 s（`nut:38`）。

### 3.4 依赖

- 引擎 `TT_BLACKHOLE`（S21 客户端预测 + SDK 服务端 `trigger_gravity.cpp`）。
- `CreateOwnedScriptMover`、`NonPhysicsMoveTo`。
- `ThrowDeployable`。
- 同文件结构和 Wattson 拦截塔很像（变量名 `TROPHY_*`、动画 `prop_trophy_*`），推断是从拦截塔改出来的。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 半径 / 上下高度 | 400 / 200 / 200 | u | `nut:69-71` | 作用范围 | |
| 内圈半径 | 100 | u | `nut:72` | 内圈不加力 | |
| 外圈 / 内圈拉速 | 300 / 400 | u/s（每 tick 加） | `nut:76-77`；playlist `blackhole_pull_outer/inner_speed` | | |
| 强拉附加 | +200 | | `nut:668` `SetBlackholeParams(200,…)` | 仅非友军 | |
| 速度上限 | 400（友军 200） | u/s | `trigger_gravity.cpp:1209-1212` | | |
| 逃跑速度上限 外 / 内 | 85 / 135（友军 ×2） | u/s | `nut:78-79`；playlist `blackhole_move_outer/inner_speed` | | 改大 = 更容易跑掉 |
| 强拉时长 | 0.8 | s | `nut:90`；playlist `blackhole_pull_time` | | |
| 稳定时长 | 10 | s | `nut:91`；playlist `blackhole_stable_time` | | |
| 激活延迟 | 1.75（升级 0.9） | s | `nut:84-85` | | |
| 特效提前 | 1.0 | s | `nut:88` | | |
| NPC 拖拽 | 1.2 s 到 40 u 圈 | | `nut:94-97` | | |
| 投射物吸力 | 80 / 帧 | u/s | `nut:74` | | |
| 视线探测 | 中心 +64，11 点间距 32 | u | `trigger_gravity.cpp:73-89` | | |
| 无人机血量 | 175（升级 90） | HP | `nut:67-68` | | |
| 爆炸伤害倍率 | ×1.5 | | `nut:82` | | |
| 被毁退还 | 25% | | `nut:86` | | |
| 投掷 | 1300 u/s，仰 7°，重力 0.75 | | `txt:62,112-113` | | |
| 落地爆炸（`.txt`） | 10 伤害，200 / 600 | | `txt:78-81` | 脚本没用到（推断） | |
| 能量 | 180，回充 1/s → 180 s | | `txt:184-188` | | |

实测对照（R5，2026-11-01）：敌人被拉 390–391 u/s（脚本 clamp 400），友军 191（200），强拉后逃跑限速 127 / 115 / 103（d = 98 / 206 / 304；脚本 122.8 / 109.3 / 97.0）；落地到开拉 1.7–1.8 s（1.75）。NPC 定身本地不生效。见 W2-RUNTIME §2。

## 5. 未解决和要实测的

1. **SDK 拉力 vs 原版**：本地服务端的拉力是 SDK 还原。测法：R5 runner 站在黑洞边缘不按键 / 按后退，逐帧记录速度（移动研究的逐帧记录 runner 直接可用）；看是否 ≈ 400 朝中心、后退时外向速度 ≈ 85–135。可再对照客户端的预测（客户端位置不应回弹）。
2. **"每 tick 加力不乘 dt"**：tick 率影响拉力手感，测法同上，比较 20 / 60 tick。
3. **NPC 定身**：dedi 上刷 spectre，看是否被搬到 40 u 圈并定住 10 s；被定住时是否还能开枪（脚本只 `SetParent`，没禁用武器）。
4. **友军被拉**：两人测试。
5. `.txt` 的落地爆炸 10 伤害是否生效。

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
1. ✅ **拉力 ≈ 公式**（真大招，落地后 1.7–1.8 s 开始拉）。敌人不按键：水平速度直接 = **390–391 u/s 向心**（公式 clamp 400，差 −2.4%，推断是同 tick 的地面摩擦），冲过中心后停在 ~70 u。强拉 0.8 s 内按后退无效（仍 390 向心）。之后按后退：向外 127.0 / 114.8 / 102.9（d = 98 / 206 / 304；公式 122.8 / 109.3 / 97.0，**高 4–6 u/s**）。友军不按键 191（公式 200）。
2. 20 / 60 tick 对比没做（本地服务端帧 0.05–0.1 s）。
3. ❌ **本地 NPC 不定身**：prowler / dummie 在范围里（触发器 `IsTouching` = 1、同 realm），`in_black_hole_field` 一直 0、不挂 mover、照常走动。"定住时能否开枪"测不了（还有：本地 NPC 本来就不开火）。HSD 照脚本做（搬到 40 u 定 10 s），没有实测对照。
4、5 没测。

## 6. HSD 实现

**未实现。** HSD 已有一个最接近的东西：重力星（`MovementItems.cs`，"地面 200 左右能吸动"，W2 §3）。

建议做法：

- `BlackHole : ICombatEntity`（新文件，或放进 `MovementItems.cs` 旁边的 `Ordnance.cs`）：
  - 投掷：`ThrowParams { launchSpeed = 1300, pitchOffset = 7, gravityScale = 0.75, shallow = 0.7, sharp = 0.1, alongNormal = 0.01 }`。
  - 时间线：1.75 / 0.8 / 10 照 R5。
- 对玩家（写身体，开关 `hsd.combat.blackhole.pullPlayer`）：每个移动 tick 照 3.2.2 的两个分支改速度，视线用 `CombatSim.WorldClear` 探 11 个点。注意 HSD 的移动 tick 和 R5 一致时，"每 tick 加力"才对得上（第 5 节第 2 条）。
- 对 NPC（`Dummy`）：照 3.2.3，进入后线性插值 1.2 s 到 40 u 圈，然后 `pos` 锁住、`vel = 0` 到结束——比玩家拉力简单得多，PvE 先做这个。
- 吸投射物：对 `ThrownItem` 每帧 `vel += toCenter.normalized × 80`（建议乘 dt×60 换成和帧率无关，写进 `R5-DIFF-ARCHIVE.md`）。
- 和 R5 的差：HSD 没有护盾、没有门。
