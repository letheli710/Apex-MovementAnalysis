# 重投气球 系统记录

会话 `i1-records`，2026-11-01。静态记录。

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_redeploy_balloon.nut`（1565 行），`txt` = `weapons/mp_ability_redeploy_balloon.txt`，`ff` = `vscripts/sh_survival_freefall.gnut`。

## 0. 概要

- **道具**：工具 / 重投气球（内部名 Evac Tower）/ `mp_ability_redeploy_balloon`（`survival_loot.csv:370`，type `gadget`，tier 2）。
- **一句话**：选一个落点，火箭底座 3.85 s 冲到 3700 u 高，气球充气，一条垂直滑索从气球放回地面。玩家**自己沿滑索爬上去**（×1.4），到顶碰触发器进入跳伞，带 1315 u/s 前向速度。气球 25 s 后或被打爆时消失，有人在绳上就等到下来。
- **更正 filter**：filter 写"把人发射到高空"。**它不发射人**，是滑索 + 跳伞。和跳板不是一类，更接近"可部署的滑索"。
- **分类**：系统（可部署滑索、到顶转跳伞、到时扣血寿命）。
- **可拆出的部件**：
  - 部署序列（底座上升 → 充气 → 放绳）→ 3.2.1
  - 运行时创建滑索实体 → 3.2.2 `RedeployBalloon_DeployZipline_Thread`
  - 寿命用血条表现，有人在绳上不消失 → 3.2.3
  - 把人推开的三个触发器 → 3.2.4
  - 到顶转跳伞 → 3.2.5
  - 投掷式落点预览 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 选点 | **客户端脚本预览**（`USE_OBJECT_PLACER = false`，`nut:80`），模拟抛物线落点 | `nut:360-422`、`nut:1477-1547` |
| 落点校验 | 高度、距离、`TraceHull`、`VerifyAirdropPoint` | `nut:1510-1536` |
| 上升 | `CreateScriptMover` + `NonPhysicsMoveTo` | `nut:730`、`nut:779` |
| 气球 | `CreatePropScript`，1800 血，重甲，可被打 | `nut:556-600` |
| 绳 | 引擎 `zipline` / `zipline_end` 实体，脚本创建 | `nut:848-870` |
| 重物 | `CreateWeight`，随 mover 落下砸回起点 | `nut:893`、`nut:921` |
| 触发 | `trigger_cylinder`、`trigger_slip_sphere` | `nut:509`、`nut:602`、`nut:621` |
| 跳伞 | 走地图跳塔的触发器逻辑 | `ff:299`、`ff:590-600` |
| 寿命 | 每秒扣血，血到 0 消失 | `nut:1013-1050` |
| 受伤颜色 | 血量分档改颜色（绿 → 黄 → 红，推断） | `nut:1160-1198` |
| HUD | 路标 RUI + 绳上血条 | `nut:94-95`、`nut:1275-1398` |
| 留痕 | `TrackingVision_CreatePOI` | `nut:777` |

## 2. 流程

```
拿出（客户端开始预览）→ 按开火
RedeployBallon_PlaceBalloon：服务端确认物品在 gadget 槽 → StartSequence；扣 1
RedeployBalloon_Sequence_Thread：
  挡空投体积（半径 500）
  ├ AR 落点标记
  ├ 底座：t=0 → 3.85 s 升到 +3700（加速 0.75，减速 2.25）；空中推人触发器
  └ 气球：充气动画 → 放绳 1.15 s
       重物带着绳下落 → 地面震动 → Zipline_Enable
       每秒扣血（25 s 扣完）
玩家：
  上绳（ZiplineSpeedScale 1.4，垂直，保留速度）
  到顶进 skydive 触发器（半径 32，半高 80）→ 跳伞，前向 + 1315 u/s
消失：血到 0；有人在绳上保持 1 血，等下来
```

`TrapDestroyOnRoundEnd`（`nut:764`、`nut:818`）：回合结束清理。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_redeploy_balloon`（`nut:459`）→ `RedeployBallon_PlaceBalloon`（`nut:464-505`，**函数名就是拼错的**）。检查 `gadgetslot` 是否装着这个道具（`nut:482-487`）。

`OnWeaponPrimaryAttackAnimEvent_redeploy_balloon` 是空的，注释说动画事件要它（`nut:1447-1450`）。

### 3.2 核心

#### 3.2.1 序列（`nut:663-691`、`nut:720-782`、`nut:784-835`）

三段 `waitthread`，每段 `OnThreadEnd` 清自己的实体。

#### 3.2.2 滑索（`nut:838-1000`）

运行时建：`zipline` kv 设垂直、保留速度、不推开、速度 1.4、禁休息（`nut:852-868`）。先 `Zipline_Disable`，重物落地后 `Zipline_Enable`（`nut:887`、`nut:986`）。**HSD 如果有滑索，这就是运行时建索的字段表。**

#### 3.2.3 寿命（`nut:1013-1050`）

```
每秒 damagePerTick = ceil( 1800 / 25 ) = 72
目标血 ≤ 0：
  绳上有人 → 血 = 1，WaitFrame 等人走
  血 = 0，结束
```

绳上人数：`AddCallback_ZiplineMount` 加减（`nut:247`、`nut:1055-1081`）。

#### 3.2.4 三个推人触发器（`nut:101-114`、`nut:739`、`nut:791`、`nut:908`）

| 触发器 | 半径 | 半高 | 力 | 目的 |
|---|---|---|---|---|
| 空中（底座上升时） | 320 | 420 | 300 | 把空域的东西推开 |
| 重物落点 | 20 | 80 | 180 | 别砸人 |
| 气球（`trigger_slip_sphere`，跟随气球） | 300 | — | 常量 350 未用（推断） | 让人滑开，不站在气球上 |

都对 NPC 和玩家生效（`nut:608-609`）。

#### 3.2.5 到顶转跳伞（`ff:586-600`）

`initialVelocity += 前向 × RedeployBalloon_GetSkydiveVelOverride()`。**S3 dedi / S21 混合**：跳伞本身的可用性按模式走，Firing Range 下可能不可用。第 5 节。

### 3.3 客户端

`RedeployBalloon_GetPlacementInfo`（`nut:1477-1547`）：`GetGravityLandData( 起点, 速度, 物体速度, deployTraceTime )`，1280 u/s 抛物线 1.6 s 找落点；太近隐藏（`nut:1516`）；上方 `TraceHull` 查空域；`VerifyAirdropPoint`。代理模型高亮绿 / 红（`nut:395-400`）。

提示字符串 `#REDEPLOY_BALLOON_USE_PROMPT`、`#REDEPLOY_BALLOON_INVALID_PLACEMENT`。

### 3.4 依赖

放置生命周期见 [C-PLACEABLE-DEPLOYABLE](../../_shared/C-PLACEABLE-DEPLOYABLE.md)。推人触发器 `PushOutOfTrigger`（没读，在 `sh_` 公共）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| `REDEPLOY_BALLOON_HEIGHT` | 3700 | u | `nut:63`；playlist `redeploy_balloon_height` | 气球高度 | |
| `REDEPLOY_BALLOON_HEALTH` | 1800 | HP | `nut:64`；playlist | | |
| `REDEPLOY_BALLOON_LIFETIME_SEC` | 25 | s | `nut:70`；playlist | ≤ 0 永久（`nut:1013`） | |
| `REDEPLOY_BALLOON_LIFETIME_MIN_HEALTH` | 1 | HP | `nut:71` | 有人时保持 | |
| `REDEPLOY_BALLOON_BASE_DEPLOY_SEC` | 3.85 | s | `nut:122` | 上升时间 | |
| 上升加速 / 减速 | 0.75 / 2.25 | s | `nut:123-124` | | |
| `REDEPLOY_BALLOON_ZIPLINE_DEPLOY_SEC` | 1.15 | s | `nut:121` | 放绳 | |
| `REDEPLOY_BALLOON_ZIPLINE_SCALE` | 1.4 | | `nut:118`；playlist | 爬绳速度 | |
| `REDEPLOY_BALLOON_SKYDIVE_VEL` | 1315 | u/s | `nut:126`；playlist | 到顶前向速度（0 关） | |
| `REDEPLOY_BALLOON_SKYDIVE_TRIGGER_RADIUS` / `HALF_HEIGHT` | 32 / 80 | u | `nut:98-99` | | |
| `REDEPLOY_BALLOON_DEPLOY_VEL` | 1280 | u/s | `nut:67` | 落点抛物线 | |
| `REDEPLOY_BALLOON_DEPLOY_TRACE_TIME` | 1.6 | s | `nut:68` | 最远约 2048 u（推断） | |
| `REDEPLOY_BALLOON_NO_AIRDROP_RADIUS` | 500 | u | `nut:65` | | |
| `REDEPLOY_BALLOON_WEIGHT_BURY_DIST` | −21 | u | `nut:77` | | |
| 推人力 | 见 3.2.4 | | `nut:101-114` | | |
| 受伤分档 | 0.66 / 0.33 | 比例 | `nut:1176-1177` | | |
| `.txt` 放置字段 `object_placement_*` | 1100 等 | | `txt:27-34` | `USE_OBJECT_PLACER false`，用不到 | |
| `deploy_time` / `holster_time` / `lower_time` / `raise_time` | 0.25 / 0.15 / 0.25 / 0.2 | s | `txt:64-67` | | |
| `ammo_clip_size` | 1 | | `txt:41` | 一次性 | |

## 5. 未解决和要实测的

- **能不能在本地跑起来**：`mp/_staging_area.gnut:1216` 给 Firing Range 放了这个道具，所以可以测。按键需求和公共未解项同，可以用 `DEV_DeployRedeployBalloon( player, origin )`（`nut:1440`）。
- 爬绳实际速度（×1.4 的基准是引擎滑索速度，没读）。
- 到顶后的跳伞起始状态（速度、高度），和 HSD 运动层的对接。
- 优先级低。filter 里也只是参考。

## 6. HSD 实现

未实现。HSD 暂时没有滑索。

- 想要"快速上高处"：跳板（TF2 / Octane）更简单。这个的价值是"部署 + 全队能用"，PvE 单人不需要。
- 想要"到顶转滑翔"：`ff` 的跳伞不是这项的重点。
- 可以借的小部件：**寿命做成血条 + 有人在用就不消失**（3.2.3），放置物通用。

建议维持"参考"，不实现。
