# Catalyst 大招 Dark Veil（黑幕）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_ferro_wall.nut`（2475 行），`txt` = `weapons/mp_weapon_ferro_wall.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Catalyst / 大招 / Dark Veil / `mp_weapon_ferro_wall`。
- **一句话**：在脚前选一点，沿视线水平方向每 0.05 s "长"出一根铁磁柱子，每根间隔 88 u，共 20 根（≈ 1760 u 长）；每根先等 1.2 s，再 0.6 s 从 0 放大到 1，立 15 s，0.85 s 缩回。柱子挡视线、挡 ping、不挡子弹；敌人穿过 → 移动 ×0.5（在墙里时）+ 7 s 致盲（屏幕变暗、只看得清 200 u 内）。
- **分类**：好技能（控制：致盲 + 减速）；**可视化**（一根根柱子依次长出的墙，柱子按头顶净空选大中小三种高度，坡上自动换斜面模型）；系统（"穿越检测"：线段近邻 + 左右侧翻转）。
- **可拆出的部件**：
  - 依次生长的柱子墙（贴地爬坡、按净空选高度、延迟放大）→ 3.2.1 `CreateWallThread` + 3.2.2 `CreateFerroWallPillar`
  - 穿越检测（在墙厚度 15 内 = "在墙里"；从一侧到另一侧 = "穿过"）→ 3.2.3 `FerroWallTiggerEnterThread`
  - 致盲 + 减速（`AttemptToApplyDarkStatus`）→ 3.2.4
  - 致盲屏幕效果（调色 + 暗角 + "手电筒"可视距离）→ 3.3
  - 挡视线不挡子弹的实体 → 1 节 `CONTENTS_BLOCKLOS` + `PTF_NO_DMG_ON_PASS_THROUGH`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 选点 | 引擎 object placer（`txt object_placer 1`、`distance_max 100`、`drop_to_ground_offset_max 400`），失败就向前 75、向下 400 找地 | `nut:530-555` |
| 柱子 | `CreateResinShard(模型, 血 125, CONTENTS_BLOCK_PING \| CONTENTS_BLOCKLOS \| CONTENTS_WINDOW)`，碰撞组 BLOCK_WEAPONS，`SetPassThroughFlags(PTF_ADDS_MODS \| PTF_NO_DMG_ON_PASS_THROUGH)`、厚度 0 | `nut:1152-1162`。子弹穿过不掉伤害（推断：`PTF_ADDS_MODS` 给子弹加"穿过黑幕"的 mod，用于穿过特效） |
| 生长 | `SetModelScale(0)` → 等 1.2 s → `GraphCapped` 0.6 s 线性到 1 | `nut:1170`、`nut:1330-1345` |
| 消失 | 15 s 后 0.85 s 线性缩到 0 | `nut:1390-1410` |
| 高低 | 每根从地面向上 trace 360，净空 ≥ 335 用大号（3×120）、≥ 215 中号、否则小号 | `nut:1010-1020` |
| 坡 | 大号柱子和上一根高差 25–100 → 两根都换成斜面模型，朝向高的一边 | `nut:1180-1205` |
| 判定 | 每根一个 `trigger_cylinder`：半径 44（步长一半）、高 120×(尺寸+1)，**在放大开始时才建** | `nut:1300-1318` |
| 减速 | `move_slow` Endless，玩家 / 假人 0.5，NPC 0.8，Catalyst 本人 0；引用计数，离开墙厚度就撤 | `nut:1680-1690` |
| 致盲 | 状态效果 `ferro_darkvision`（敌人）/ `ferro_darkvision_team`（队友），客户端回调画屏幕 | `nut:321-324`、`nut:1753-1880` |
| 身上黑雾 | 粒子 `FERRO_WALL_DARK_ZONE_SHROUD_FX` 挂在胸口，所有人可见 | `nut:1775-1782` |
| 空中 / 滑铲进入 | 水平速度 ÷ 2 | `nut:1738-1742` |
| 锁武器 | 放大招时 `LockWeaponsAndMelee` | `nut:620` |

另有两种没用的部署方式（playlist 切换）：`DEPLOY_PROJECTILE`（扔一个弹，飞行中每 88 u 在下方长一根，`GetProjectileVelocity_weapon_ferro_wall` `nut:663`）和 `LEFT_TO_RIGHT`（以选点为中心左右各 8 根，间隔 0.1 s）。默认是"向前"。

服务端 / 客户端：柱子、触发、状态效果在服务端；屏幕效果在客户端（状态效果的开 / 关回调）。服务端有两处 `printt("Ferrofluid targetorigin…")`（`nut:538`、`nut:548`），像 SDK 调试残留。

## 2. 流程

```
按键 → 预览（CreatePlacementWall 客户端画预览柱，nut:2262）
开火 → FerroWallAttack_Common
 ├ 选点（放置器 or 前 75 下 400；都失败 → 提示"没有地面"，不扣能量）
 ├ 锁武器和近战，加 ABILITY_USED_MOD
 └ CreateWallThread(选点, 视线方向, 20 根, 0.05 s)
CreateWallThread（nut:886）：
 ├ 每人最多 1 堵（maxWallsPerPlayer），放新的删旧的
 ├ i = 0..19，每次 wait 0.05：
 │   从上一点 +95 高沿方向走 88（第一根走 0、起点 +80）→ 被挡就升 80.75 再试一次，还挡 → 停
 │   向下 500 找地；找不到 → 停
 │   向上 360 测净空 → 选大中小；随机外形（不和上一根相同）；水里另一套特效
 │   thread CreateFerroWallPillar
 └ 标记最后一根
CreateFerroWallPillar（每根）：
 ├ 生成（缩放 0，已经实体、挡视线——推断：缩放 0 的碰撞体积也是 0）
 ├ 1.2 s 等待（地面上有液体特效）
 ├ 建触发器 → 0.6 s 放大
 ├ 15 s（升级 20 s）
 └ 0.85 s 缩小 → 删除
穿越（每个碰到触发器的人一个线程）：见 3.2.3
```

时间线：第 1 根 t=0，第 20 根 t=0.95；墙完全长好 ≈ 0.95+1.2+0.6 = 2.75 s；全部消失 ≈ 0.95+1.2+0.6+15+0.85 = 18.6 s。

升级：`upgrade_catalyst_ult_length` → 27 根、持续 20 s（`nut:158,167`），强制回充延迟 22 s（`txt:248-251`）；`upgrade_core_ult_cooldown_reduction` → 能量 120（`txt:254-259`）。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_weapon_ferro_wall`（`nut:518`）→ `FerroWallAttack_Common`（`nut:523`）。

### 3.2 核心逻辑

#### 3.2.1 墙的路径（`CreateWallThread`，`nut:886`）

```
dir = 水平(视线前向)；柱子朝向 = dir 绕 up 转 90°（墙面和前进方向平行）
traceStart = 选点 + (0,0,80); step = 0（第一根就在选点）
for i in 0..N-1:
  fwd = Trace(traceStart → traceStart + dir*step)
  if 挡住: up = Trace(撞点 → 撞点 + 80.75); 从 up 终点再走剩下的距离；还挡 → break
  down = Trace(fwd终点 → 向下 500); 没打到 → break
  h = min(Trace(地面 → 地面+360) 长度, 360)
  size = h ≥ 335 ? 大 : h ≥ 215 ? 中 : 小
  CreateFerroWallPillar(model[类型][size], 地面, …)
  traceStart = 地面 + (0,0,95)
  step = 88
  wait 0.05
```

所以墙能爬上 ≤ 95 u 的台阶、跨过 ≤ 500 u 的落差，碰到高墙就停。

#### 3.2.2 柱子（`CreateFerroWallPillar`，`nut:1152`）

见第 1 节表。触发器在 1.2 s 等待**之后**才建（`nut:1300`），所以前 1.2 s 墙看得见、挡视线（推断）但没有致盲减速。

#### 3.2.3 穿越检测（`FerroWallTiggerEnterThread`，`nut:1511`）

```
每帧（还在圆柱里）:
  if 相位中: 标记, continue
  线段 = 柱心 ± 44·right（right = 墙的走向）
  p = 线段上离单位脚底最近的点
  if 水平距离(单位, p) ≤ 15:            // 在墙厚度里
      第一次进墙 → AttemptToApplyDarkStatus(ent, trigger, 减速=true)
      致盲结束时间 = now + (敌人 7 / 队友 1 / NPC 2)
      每 0.5 s 一个溅射特效
  else:
      刚离开墙 → 减速引用计数 -1
      没进过墙：side = sign(dot(墙法线, 单位 - p))
                side 翻转了（且不是第一帧、上一帧没相位）→ 穿过 → AttemptToApplyDarkStatus(减速=false)，刷新致盲
```

翻转检测是为了"一帧跳过 15 u 厚度"的高速穿越。

#### 3.2.4 `AttemptToApplyDarkStatus(ent, trigger, applyMoveSlow)`（`nut:1647`）

```
isCatalyst = 玩家且有被动 PAS_LOCKDOWN
teamVision = 同队 或 isCatalyst
if 已有致盲数据:
    原来是队友版、现在是敌人 → 换成敌人版；反之换成队友版
elif teamVision: 玩家 → 队友版（1 s 轻微变暗）
else: 统计 + 非 Catalyst → DarkVisionVisualsThread_Server（敌人版）
if 第一次 && applyMoveSlow:
    move_slow Endless, 玩家/假人 0.5, NPC 0.8, Catalyst 0
    —— 注意：队友也会被减速（没有判断队伍），见第 5 节
声音（敌我两套）
if 非 Catalyst 的玩家 且（空中 或 滑铲）: v.xy /= 2
```

`DarkVisionVisualsThread_Server`（`nut:1753`）：

```
玩家 → ferro_darkvision 状态效果 Endless 强度 1
非假人 NPC → 额外 move_slow 0.8，持续到致盲结束（2 s）
结束时间 = now + 7（玩家/假人）或 2（NPC）
胸口挂黑雾粒子
每帧等结束时间（离结束 X 秒播"结束"音）
```

所以：**玩家**只在墙里减速、出墙后 7 s 致盲；**NPC** 墙里减速，出墙后再减速 2 s（没有屏幕可以致盲）。

### 3.3 客户端表现

- 致盲屏幕（`FerroWallDarkVision_UpdatePlayerScreenVFX_Thread`，`nut:1932`）：
  - 调色 `ColorCorrection` 独占，权重 = 状态强度 × 0.5；
  - 暗角粒子 `FERRO_WALL_DARKEYE_VIGNETTE_FX` 挂在相机，透明度 0 → 0.9（敌人）/ 0.3（队友、Catalyst）；
  - "可视距离球" `FERRO_WALL_DEBUG_SPHERE_VISION_LIMIT_FX`：半径 200（`FERRO_WALL_DARKVISION_DISTANCE`），不透明度 0.7×0.5×4，只给非 Catalyst 的敌人——这就是"只看得见身边 200 u"；另有 450 / 700 两圈（`nut:2085-2095`）。
  - 淡入淡出 0.5 s（`nut:1975`）。
- 柱子特效：底座液体粒子 CP1 = <45, 0, 0.85>、敌我颜色 `<100,160,255>` / `<223,66,30>`（`nut:190-191`）；消失时换 finished 特效。
- 音效：三个 script mover（地面 / 放大 / 缩小）沿着柱子生成顺序移动，`NonPhysicsMoveTo(下一根, 0.05 s)`——一个声音"跑"过整面墙（`nut:1265-1290`）。这是一个值得借的表现技巧。
- 预览：客户端 `CreatePlacementWall`（`nut:2262`）用同样的步进画代理模型。

### 3.4 依赖

- `CreateResinShard`（和尖刺共用）。
- 状态效果 `ferro_darkvision` / `ferro_darkvision_team` / `move_slow`。
- `_shared/B-move-slow.md`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 柱子数 | 20（升级 27） | 根 | `nut:165,167`；playlist `catalyst_wall_numSegments` | 墙长 ≈ 根数×88 | |
| 间距 | 88 | u | `nut:144` | | |
| 生成间隔 | 0.05 | s | `nut:161`；playlist `catalyst_wall_forwardDelay` | 墙"长"出去的速度 = 1760 u/s | 改大 = 更慢更有戏 |
| 放大前等待 | 1.2 | s | `nut:160`；playlist `catalyst_wall_scaleUpDelay` | | |
| 放大时间 | 0.6 | s | `nut:163` | | |
| 持续 | 15（升级 20） | s | `nut:156,158`；playlist `catalyst_wall_duration` | | |
| 缩小时间 | 0.85 | s | `nut:164` | | |
| 柱高 | 120 / 240 / 360 | u | `nut:152`（×尺寸） | 触发高度 | |
| 尺寸阈值 | 净空 ≥ 335 / ≥ 215 | u | `nut:171`（buffer 25） | | |
| 爬坡 | 首根 +80，之后 +95，被挡再试 +80.75 | u | `nut:146-149` | 能爬的台阶 | |
| 向下找地 | 500 | u | `nut:150` | 能下的落差 | |
| 触发半径 | 44 | u | `nut:145` | | |
| 墙厚度（"在墙里"） | 15 | u | `nut:153` | | |
| 柱子血量 | 125 | HP | `nut:170` | 可打碎 | |
| 斜面模型高差 | 25–100 | u | `nut:201-202` | | |
| 减速（玩家 / 假人） | 0.5 | 强度 | `nut:173`；playlist `catalyst_wall_slowServerityPlayer` | 只在墙里 | |
| 减速（NPC） | 0.8 | 强度 | `nut:174` | 墙里 + 出墙 2 s | |
| 致盲时长 敌人 / 队友 / NPC | 7 / 1 / 2 | s | `nut:183-184,175` | | |
| 致盲暗角 敌人 / 队友 / Catalyst | 0.9 / 0.3 / 0.3 | 透明度 | `nut:178-180` | | |
| 可视距离 | 200（+250、+500 两圈） | u | `nut:181` | | |
| 可视圈不透明度 | 0.7 × 0.5 | | `nut:182,185` | | |
| 进入砍速 | ÷2 | 水平速度 | `nut:1738-1742` | 空中 / 滑铲 | |
| 选点距离 | 100（失败退回 75） | u | `txt:21`；`nut:151` | | |
| 每人墙数 | 1 | | `nut:206` | | |
| 大招能量 | 150，回充 1/s → 150 s；强制延迟 17 s（升级 22） | | `txt:111,177-183` | | |

## 5. 未解决和要实测的

1. **队友会不会被减速**：`AttemptToApplyDarkStatus` 对减速没有判断队伍，只排除 Catalyst 本人。测法：R5 runner 里需要两个同队玩家；或用一个同队 dummie 走过墙看速度。
2. **缩放 0 时的碰撞**：前 1.2 s 柱子已 `Solid()` 但缩放 0，挡不挡人 / 视线要实测。测法：放墙后立刻往柱子位置走。
3. **致盲对 NPC 的作用**：NPC 没有屏幕，只有 2 s 减速。原版 AI 是否因 `CONTENTS_BLOCKLOS` 失去目标要在 dedi 上看（spectre 隔墙是否还开枪）。
4. **子弹穿过**：`PTF_NO_DMG_ON_PASS_THROUGH` 推断为"不掉伤害"。测法：隔墙打 dummie，看伤害数字。

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
- NPC 减速 0.8 = ×0.2（同 `_shared/B-move-slow.md`）。
- 3（致盲对 NPC）测不了：本地 NPC 不开火（W2-RUNTIME §0）。1、2、4 没测。

## 6. HSD 实现

**未实现。**

建议做法：

- 新文件 `DarkVeil.cs`：`FerroPillar`（位置、尺寸、生成时间、血 125）+ `DarkVeil : ICombatEntity`（柱子列表）。
- 路径：照 3.2.1 用 `CombatSim.WorldRay` 做前、上、下三条 trace；每 0.05 s 生成一根。
- 表现：`CombatDraw.Capsule`（`CombatVisuals.cs:88`）画柱子，缩放从 0 到 1；颜色敌我两种。
- 挡视线：做成 `IWallBlocker`（`CombatCore.cs:140`），`PassAmp` 返回 1（子弹穿过不减伤），`BlocksExplosions = false`；AI 的视线检查（`PlayerVisibleToAi`，`CombatSim.Items.cs:41`）再加一条"线段穿过黑幕 → 看不见"。
- 穿越：每帧对每个单位按 3.2.3 的"线段近邻 ≤ 15 / 侧翻转"判。
- 效果：敌人 `slowScale 0.5` 只在墙里；NPC 出墙再 2 s ×0.8（强度含义见尖刺第 5 节第 1 条）；玩家被自己的墙不影响。对玩家的致盲（敌人的墙，PvE 里大概用不上）：做屏幕暗角 + 雾距 200，开关 `hsd.combat.veil.blindPlayer`。
- 和 R5 的差：没有斜面模型、没有声音跑动；写进 `R5-DIFF-ARCHIVE.md`。
