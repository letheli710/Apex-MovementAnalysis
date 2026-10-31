# Newcastle 大招 Castle Wall（城墙）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_armored_leap.nut`（8720 行，批次 B 最大），`txt` = `weapons/mp_ability_armored_leap.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Newcastle / 大招 / Castle Wall / `mp_ability_armored_leap`。
- **一句话**：瞄准一点（或一个 80 m 内的队友）→ 蹲 0.4 s → 跳起（或近距离时冲刺、空中时直接俯冲）→ 在空中悬停一下 → 砸地。砸地时把 350 u 内的敌方**玩家**击退（250–450 u/s，伤害 0）并在面前立起一面城墙：中间一块高墙，两侧各一条"蛇"沿地面爬出去铺低墙，3 s 后通电。通电后 120 s：敌人碰到墙前 5 u 厚的区域 → 20 电击伤害 + 2.5 s 减速 0.75 / 转向 0.75 / 屏幕 EMP；墙还会拦截 200 u 内的投射物。墙每块 750 HP。
- **分类**：好技能（PvE 里"跳进人堆 + 立墙 + 通电"）；系统（三种移动模式 + 引擎驱动的跳跃 / 俯冲；第三人称镜头编排；蛇形贴地铺墙）；可视化（落点预警、跳跃镜头、墙沿地面"长"出去）。
- **可拆出的部件**：
  - 跳跃落点选择（瞄准 → 找落点 / 墙沿 / 队友身边）→ 3.2.1 `GetArmoredLeapTargetInfo`（`nut:4160-4780` 一带）
  - 三种移动（冲刺 / 跳 / 空中俯冲）的参数和判定 → 3.2.2
  - 落地击退 → 3.2.3 `ArmoredLeap_ApplyKnockbackForce`
  - 蛇形贴地铺墙 → 3.2.4 `CastleWall_CreateSnakeWall_Thread`
  - 墙前通电区域（横放的圆柱触发器 + 距离 / 高度过滤）→ 3.2.5 `CastleWall_OnTriggerUpdate`
  - 墙拦截投射物（和 Wattson 拦截塔同一套 vortex 写法）→ 3.2.6
  - 跳跃时的第三人称镜头编排 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 跳跃运动 | **引擎**：`player.StartArmoredLeapJump(…)` / `StartArmoredLeapDash` / `StartArmoredLeapAirDive`，阶段变化回调 `CodeCallback_ArmoredLeapPhaseChange` | `nut:1150-1230`；playlist `newcastle_ult_code` 默认 true（`nut:8712`）。旧的 script mover 写法（`_Depricated`）留在代码里但不跑 |
| 镜头 | `player.SetTrackEntity(player)` + orbit 模式 + 每阶段 `SetTrackEntityOffset*OverTime` | `nut:960-985`、`nut:1095-1100` |
| 落点预警 | `ArmoredLeap_CreateWarningArea(终点, 1.5 s)` | `nut:2477` |
| 击退 | 遍历活着的**玩家**，`SetVelocity(水平方向 + 0.5 up) × 力`；`ViewPunch` | `nut:3955-4032`。NPC 不受影响 |
| 落地伤害 | `TakeDamage(0)`（`ARMORED_LEAP_DAMAGE = 0 //25`） | `nut:170-171` |
| 城墙 | `CreatePropScript(SOLID_OBB)`：中间高墙 + 两侧锚点 + 低墙板；蛇头是 script mover，`NonPhysicsMoveTo` 一步步走，后面线程沿路铺板 | `nut:5440-6175` |
| 通电区域 | 每块墙一个 `trigger_cylinder` **侧放**：半径 80 = 高度，上下 5 = 厚度 | `nut:7272-7368` |
| 通电效果 | 玩家：`castle_wall_emp`、`emp` 强度 1、`move_slow 0.75`、`turn_slow 0.75`，各 2.5 s；所有敌人 `TakeDamage(20, DF_ELECTRICAL, DF_STUN_AI)` | `nut:7470-7480` |
| NPC 电击 | 伤害回调 → 电击免疫窗 3 s → `Electricity_DamagedPlayerOrNPC(…, 2.5)` | `nut:7499-7511` |
| 拦截投射物 | `vortex_sphere` 半径 200，墙后偏移 | `nut:7698-7765`、`nut:7684` |
| 被打断退还 | 没立起墙就倒地 / 被打断 → 退还 85% 能量 | `nut:174`、`ArmoredLeap_OnAttemptFailed` `nut:2289` |
| 升级 | 落地给范围内队友 15 s 回盾（10/s，最多 100） | `nut:272-275`、`nut:3865` |

## 2. 流程

```
按住大招 → AR 预览（ArmoredLeap_AR_Placement_Thread，nut:3040）：
   瞄准 ≤ 2500 u 找落点；屏幕中心 0.95 点积内的队友（≤ 80 m）→ 跳到队友身边
开火：GetArmoredLeapTargetInfo 失败 → 不放；成功 → 能量回充暂停
ArmoredLeap_Master_Thread（nut:920）：
 ├ 落点预警 1.5 s；切第三人称镜头
 ├ 判类型：
 │   距离 ≤ 600 且高差 ≤ 250（IsInDashRange）→ DASH：蹲 0.6 s，冲刺 800–1500 u/s（按距离插值），加速度 12000
 │   在空中 → AIR_DIVE（水平 > 600 为 LONG）：预备 150 u/s，俯冲
 │   否则 → JUMP：蹲 0.4 s，起跳 1800–2500 u/s（加速 24000），悬停 320–400 u/s（加速 9000），俯冲（加速 9000）
 │   俯冲速度：空中点到落点距离 200→500 映射 2000→2500；500→80 m 映射 2500→3500
 ├ 等引擎信号 "ArmoredLeap_StartTravelGroundPhase" 或 "ArmoredLeap_Interrupted"
 ├ 收武器 → ArmoredLeap_SlamToGroundPosition
 └ 落地 → ArmoredLeap_Impact：建城墙 + 击退（+ 升级回盾）
落地后：0.75 s 不能动（RECOVERY_TIME），之后 move_slow 0.2 持续 1.0 s（淡出 0.5）；镜头 0.5 s 后回第一人称
城墙：
 ├ 中间高墙（展开动画）
 ├ 左右各一个蛇头：侧向 65 u 内没有空间 → 不出；否则每步 27 u 沿地面爬（爬 32、下 80，超过 100 找弯），每步转 8°，最多 4 段（省实体模式）或 6 段，最长 3 s；末端立一块高掩体（墙长 ≥ 32 才立）
 ├ 3.0 s 后：每块墙建通电区域 + 表面电弧特效；开始拦截投射物
 └ 通电 120 s（升级 +120 = 240 s）；墙本身被打掉 / 主人收起才消失
```

打断（引擎发 Interrupted）：撞到东西、上升气流（`ArmoredLeap_CheckForUpdraft_Thread`）、相位等。打断时如果离地面 ≤ 130 且位置合法 → 仍然落地立墙（`ArmoredLeap_Handle_Interrupted`，`nut:1535`），否则失败退还 85%。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_ability_armored_leap`（`nut:806`）→ `ArmoredLeap_Master_Thread`（`nut:920`）。

### 3.2 核心逻辑

#### 3.2.1 落点（`GetArmoredLeapTargetInfo` 一族，`nut:4160-5215`）

只记要点（代码很长）：最远 40 m（1575 u，升级 ×1.2），最高 25 m；对队友 80 m / 50 m。落点要离墙 ≥ 75；瞄到墙沿时向里收 100 找地面（`LEDGE_INSET`）；落点要有站人空间（`ArmoredLeap_HasValidHullRoom`）；起点和终点可以在移动平台上（终点平台速度 ≤ 12）。

#### 3.2.2 移动

引擎接口参数（`nut:1150-1225`）：

```
StartArmoredLeapDash(ignore, speed = Graph(dist, 0→600, 800→1500), accel 12000, crouch 0.6, recovery 0.75, endPoint, …)
StartArmoredLeapJump(ignore, jump = Graph(dist, 600→1575, 1800→2500), accel 24000,
                     hover = Graph(dist, 600→1575, 400→320), accel 9000,
                     dive = diveSpeed, accel 9000, crouch 0.4, …)
StartArmoredLeapAirDive(ignore, prep 150, prepAccel 600, dive, dive/0.9, …)
空中点 airPoint 由落点选择给出：近处跳得高（≤ 800）、远处跳得低（500，距离 ≥ 1000 时）
```

超时保护：跳 2.75 s、俯冲 2.75 s、冲刺 2.5 s、跳到队友 3.25 s（`nut:127-130`）。

#### 3.2.3 击退（`ArmoredLeap_ApplyKnockbackForce`，`nut:3955`）

```
for 每个活着的玩家（同 realm）:
    自己 → ViewPunch(5)
    d² > 350² → 跳过
    force = Graph(d², 0→350², 450→250)
    v = 0; v += (水平(center − origin) + (0,0,0.5)) × force      // 队友也先被清零速度，但不加
    队友 → ViewPunch(15)，continue
    敌人 → SetVelocity(v)，ViewPunch(35)，TakeDamage(0)，打断复活 / 处决 / Valk 大招
```

注意：队友的速度也被 `SetVelocity(ZERO_VECTOR)` 清零了（`nut:3985`），推断是 bug。NPC 不在列表里，**不被击退**。

#### 3.2.4 蛇形铺墙（`CastleWall_CreateSnakeWall_Thread`，`nut:5591`）

```
侧向 65 u 有墙（法线和竖直 < 0.8）→ 这一侧不出
蛇头 mover 先移到侧边 39.25（或 15）
循环（墙长 < 27×段数，且 < 3 s）：
    下一点 = SnakeWall_GetNextValidPos：前进 64 测试，爬 ≤ 32，下 ≤ 80（> 100 则转弯）
    mover.NonPhysicsMoveTo(下一点, 0.4 s)；按地面法线转姿态（0.3 s）
    另一线程 CastleWall_TrackAndDeploy_SnakeWallPanels_Thread：蛇头每走 27 u 在身后放一块低墙板
末端：转回 −10°，墙长 ≥ 32 且前方 39 u 无墙 → 立高掩体（0.35 s 伸出）
```

#### 3.2.5 通电（`CastleWall_OnTriggerUpdate`，`nut:7393`）

```
只处理 玩家 或 战斗 NPC；友军直接 return
每帧（还在触发器里）:
  if 身上没有 castle_wall_emp（玩家）且不在相位:
     宽度 = 低墙 36 / 高墙 58；水平距离 > 宽度 或 墙底高于眼睛 → 不算
     玩家：castle_wall_emp / emp 1.0 / move_slow 0.75 / turn_slow 0.75，各 2.5 s（emp 淡出 0.2，减速淡出 1）
     TakeDamage(20, DF_ELECTRICAL | DF_STUN_AI)
```

玩家靠 `castle_wall_emp` 的 2.5 s 当冷却；NPC 没有这个状态，每帧都打，但伤害回调里的电击免疫窗（3 s）把多余的伤害 ×0 → **NPC 每 3 s 吃一次 20**，玩家每 2.5 s。

#### 3.2.6 拦截

vortex 球半径 200，规则 `CastleWall_ShouldTargetProjectile`（`nut:7946`）和拦截塔类似；`newcastle_allow_friendly_intercepts` 默认 true → 友军投射物也拦（`nut:8052`）。持续 = 通电时长 − 0.5 s。

### 3.3 客户端表现

- 第三人称跳跃镜头：距离 75 → 空中 115 → 俯冲 45 → 结束 85；右偏 −35（结束 −15）；高 10 / 35 / 15 / 4.5（`nut:152-165`）；蹲伏时间内对数插值。
- 落点 AR 标记、队友目标 HUD、"视觉模式"（`ArmoredLeap_VisionMode_Thread`）：跳跃时高亮落点附近的敌人（`ArmoredLeap_TrackEnemyAtLandingZone_Thread`，`nut:3629`；playlist `newcastle_hasVisorThreat`）。
- 墙：敌我颜色、表面电弧、威胁指示线（`BuildThreatLines`，`nut:8647`）。

### 3.4 依赖

- 引擎 ArmoredLeap 系列（C++，SDK 未实现源码）。
- `_shared/B-electric-emp.md`（NPC 电击）、`_shared/B-move-slow.md`。
- `PassiveNewcastle_*`（被动，护盾击退升级）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| 跳跃距离 | 40 m = 1575（升级 ×1.2） | u | `nut:72`、`nut:6659` | |
| 跳到队友 | 80 m / 高 50 m | | `nut:73,76` | |
| 最高 | 25 m | | `nut:75` | |
| 冲刺范围 | ≤ 600、高差 ≤ 250 | u | `nut:84-85` | |
| 冲刺速度 | 800–1500，加速 12000 | u/s | `nut:103-105` | |
| 起跳速度 | 1800–2500，加速 24000 | u/s | `nut:107-112` | |
| 悬停速度 | 320–400，加速 9000 | u/s | `nut:109-113` | |
| 俯冲速度 | 2000 / 2500 / 最大 3500，加速 9000 | u/s | `nut:88-89,102,114` | |
| 空中点高度 | 近 200 … 最高 800；远（≥ 1000）500 | u | `nut:78-81` | |
| 蹲伏 | 跳 0.4，冲刺 0.6 | s | `nut:92-93` | |
| 落地硬直 | 0.75 s 不能动，再 1.0 s 减速 0.2 | s | `nut:141,143`、`nut:2077` | |
| 击退半径 / 力 | 350 / 450→250 | u, u/s | `nut:167-169` | |
| 落地伤害 | 0（原 25 / 5） | | `nut:170-171` | |
| 退还 | 85% | | `nut:174` | |
| 墙血量 | 750（升级 +500） | HP | `nut:177`、`nut:6649` | |
| 通电延迟 | 3.0 | s | `nut:192` | |
| 通电时长 | 120（升级 +120） | s | `nut:193`、`nut:6654` | |
| 通电伤害 / 间隔 | 20 / 2.5（NPC 实际 3） | HP / s | `nut:190-191` | |
| 通电减速 / 转向 | 0.75 / 0.75，2.5 s | 强度 | `nut:7477-7478` | |
| 通电区域 | 高 80，厚 5，宽 低 36 / 高 58 | u | `nut:223-226` | |
| 蛇：段长 / 段数 / 转角 / 最长时间 | 27 / 4（或 6）/ 8° / 3 s | | `nut:203-213`、`nut:5735` | |
| 蛇：爬 / 下 / 下限 | 32 / 80 / 100 | u | `nut:230-232` | |
| 拦截半径 | 200 | u | `nut:7684` | |
| 升级回盾 | 10/s，最多 100，15 s，受伤停 2 s | | `nut:272-275` | |
| 能量 | 120，回充 1/s → 120 s | | `txt:46-53` | |

## 5. 未解决和要实测的

1. **引擎跳跃轨迹**：`StartArmoredLeapJump` 的路径（加速到 jump 速度、到空中点、悬停、俯冲）在 C++ 里。测法：R5 runner 记录 Newcastle 一次跳跃的逐帧位置和速度（移动研究的 runner 已有逐帧记录），反推出四段。
2. **落地伤害 0**：正式服记忆有伤害；本地 `0 //25`。测法：dedi 上跳到 dummie 旁边看伤害。
3. **击退不影响 NPC**：只遍历玩家。PvE 要自己加。
4. **队友速度被清零**：测法：两人，一人站在落点旁看是否被定住一下。

## 6. HSD 实现

**未实现。** 跳跃部分和移动研究相关（HSD 已有完整的移动身体），城墙部分可以复用 A 型墙。

建议做法：

- 跳跃：在 `PracticeSession` 里加一个"脚本驱动移动"状态（类似相位回溯写身体的方式，README "战斗层只在这几处写移动身体"再加一处），按 3.2.2 参数做四段：蹲伏（速度 0）→ 加速到空中点 → 悬停 → 加速俯冲到落点。轨迹等第 5 节第 1 条实测数据再精调。
- 镜头：HSD 有 `CameraRig`，加一个临时第三人称偏移（75/115/45/85）。
- 击退：`CombatSim.Push`（`CombatSim.cs:306`）已有，对 350 内敌人按 450→250 推（**包括 NPC**，和 R5 不同，写进 `R5-DIFF-ARCHIVE.md`）。
- 城墙：复用 `AWall`（`Tacticals.cs:78`，`IWallBlocker`）做中间墙；两侧"蛇"先简化成沿地面每 27 u 一块的低墙，贴地用 `CombatSim.WorldRay`。
- 通电：墙前 5 u 内的敌人，每 2.5 s（NPC 3 s）20 伤害 + `slowScale = 0.25`（强度 0.75）2.5 s。
- 开关：`hsd.combat.castle.*`。
