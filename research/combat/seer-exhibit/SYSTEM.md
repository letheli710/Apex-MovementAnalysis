# Seer 大招 Exhibit（展示）· 系统记录

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`。

## 找脚本的过程

C0 2.3b 和 APEX-REPORT 2.4 都写"本地没有 Seer 大招的脚本"。原因是文件名不含 seer / exhibit。这次找到了：**`vscripts/weapons/mp_ability_echo_locator.nut`（2109 行）+ `weapons/mp_ability_echo_locator.txt`**。

| 证据 | 位置 |
|---|---|
| 标点系统在 `// Seer Exhibit` 注释下取 `ECHO_LOCATOR_SCRIPT_NAME` 的实体 | `vscripts/sh_ping.gnut:4792-4800` |
| 状态效果 `inside_echo_locator` | `status_effect_types.txt:161`；`.nut:164`、`.nut:867` |
| 统计 `seer_exhibit_enemies_inside` | `vscripts/sh_stats_characters.gnut:213`、`:980` |
| 模型和特效名用 Seer 的内部名 pariah / killroom：`pariah_heart.rmdl`、`P_killroom_*` | `.nut:31-45` |
| 声音 `Seer_Ultimate_*` | `.nut:47-54` |
| UI 里判断 `PAS_PARIAH`（Seer 被动）→ `playerIsSeer` | `.nut:1240-1247` |
| `.txt` `weapon_type_flags WPT_ULTIMATE`，`printname #WPN_ECHO_LOCATOR` | `.txt` |
| 本地化有 "Exhibit" / "Exhibit: Enemies Tracked"（键是哈希，无法和 `WPN_ECHO_LOCATOR` 直接对上） | `localization/localization_english.txt:5147`、`:11844`、`:16770`、`:21337` |

搜过的地方：`vscripts/` 全局搜 `exhibit`（命中 `sh_ping.gnut`、`sh_stats_*`、`mapeditor`）、`seer`、`echo_loc`；`weapons/*.txt`；`status_effect_types.txt`；`localization_english.txt` 搜 `Exhibit`。

Seer 战术 Focus of Attention 也有脚本：`vscripts/weapons/mp_ability_sonic_blast.nut`（C0 已列）。

## 0. 概要

- **技能**：Seer / 大招 / Exhibit / `mp_ability_echo_locator`。
- **一句话**：扔出一颗"心脏"，落地展开成半径 1350 u 的球形区域，持续 25 s；区域内的敌人只要**走动（不蹲走）或开枪**，Seer 一方就能看到他们的脚印、胸口锁定框和小地图位置；心脏有 125 血，可以被打掉。
- **分类**：可视化 ✔（脚印特效、锁定框、区域边界、屏幕强度随状态变、无人机群动画）、系统 ✔（"区域内 + 行为条件"的侦测规则；区域实体有血可被摧毁、被摧毁立即开始冷却）；好技能（效果）中：PvE 里是"区域侦测"，比全图透视更有玩法。
- **可拆出的部件**：
  - 投掷物落地展开成固定装置（script_mover，能被门推、能被打）→ 3.2.1 `OnEchoLocatorPlanted`
  - 球形区域：触发器粗筛 + 每 0.1 s 球形距离细判 → 状态效果 `inside_echo_locator` → 3.2.2 `EchoLocatorTriggerTouching_Thread`
  - 行为侦测：移动检查 + 开火检查 → 3.2.3 `DoesPlayerPassEchoLocatorMovementCheck` / `…WeaponDischargeCheck`
  - 脚印节奏：速度越快脚印越密；起跳 / 落地各一个 → 3.2.4 `EchoLocatorFootstepVFX_Thread`
  - 屏幕强度按"在谁的区域里、有没有暴露"渐变 → 3.3 `EchoLocator_UpdateIntensity_Thread`
  - 装置被毁立即开始冷却 → 3.2.1 `RestartEchoLocatorCooldown`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 扔出 | 可部署投掷物 `ThrowDeployable` + `OnProjectileCollision_weapon_deployable` | `.nut:186`；`.txt` 弹道字段 |
| 心脏装置 | `script_mover`（`SOLID_VPHYSICS`、`MOVETYPE_FLY`）+ 模型 `pariah_heart.rmdl`，125 血 | `.nut:283-318`。用 mover 是为了和门互动（推门、挡滑门） |
| 小地图 | 另建空 `prop_script` 挂在心脏上画小地图圈（mover 不能上小地图），只本队可见 | `.nut:320-330`、`.nut:696-711` |
| 区域 | 服务端 `trigger_cylinder`（半径 = 上高 = 下高 = 1350）粗筛；每 0.1 s 用 `DistanceSqr(触发器中心, 实体脚底) < 1350²` 细判成球 | `.nut:951-995`、`.nut:747-945` |
| "在里面" | 状态效果 `inside_echo_locator`（无限期，出去时停）；敌我都会加 | `.nut:859-868`、`.nut:920-933` |
| 敌人有没有按移动键 | 服务端写玩家网络布尔 `echoLocatorPlayerHasMovementInput` | `.nut:155`、`.nut:889-893` |
| 侦测和显示 | **全在客户端**（Seer 一方的客户端）：每帧遍历"在里面的实体"，算速度、查开火，放脚印粒子、锁定框、小地图标记 | `.nut:1544-1906` |
| 敌人在小地图上看到这个区域 | 敌人进入区域时 `projectile.Minimap_AlwaysShow(0, ent)`，离开时隐藏 | `.nut:880-886`、`.nut:898-904` |
| 屏幕特效 | 驾驶舱粒子 `P_killroom_hud_static`，CP2 = 强度（每帧 ±0.01 逼近目标），CP3 = 友 / 敌色 | `.nut:1520-1542`、`.nut:1961-2040`、`.nut:2060-2086` |
| HUD | 驾驶舱 RUI `ui/echo_locator.rpak`：区域位置、是否在里面、里面几个敌人 | `.nut:1188-1256` |
| 无人机群 | 两个 `prop_script` 无人机群模型（友 / 敌各一份，按可见性分），按半径缩放，播开始 / 待机 / 最后 5% 震动 / 结束动画 | `.nut:617-693` |
| 心脏特效 | 友方 `P_killroom_heart`、敌方 `P_killroom_heart_enemy`、无人机 `P_killroom_heart_drone_cluster` | `.nut:596-604` |
| 声音 | 边界环境声、中心声、出入阈值声、结束声、摧毁声 | `.nut:1126-1185`、`.nut:1533`、`.nut:494` |
| 被打 | 伤害回调：近战固定 1/2.9 最大血（3 下打爆）、Crypto EMP 陷阱一下打爆、圈内毒圈伤害可免疫 | `.nut:402-444` |
| 被毁 / 被拦截 | 立即把大招弹夹设 0 → 开始冷却（不用等 25 s） | `.nut:500-524`；被 Wattson 塔打掉投射物也一样（`.nut:229-248`） |
| 被扫描 | `AddSonarDetectionForPropScript(echoLocator)`（敌人扫描能看到它） | `.nut:341`；见 `_shared/E-SONAR-HIGHLIGHT.md` |

## 2. 流程

```
按住（toss_pullout 0.4 s；手上心脏特效）→ 松开 → 扔出（1200 u/s，抬 15°，会弹）     (.txt)
落地 OnEchoLocatorPlanted（.nut:251-364）
   向下 32 u 找地面；建心脏 mover + 小地图 prop；挂到会动的东西上（可黏的话）
   thread DeployEchoLocator_Thread
DeployEchoLocator_Thread（.nut:526-615）
   展开动画（prop_pariah_heart_deploy）→ 待机动画
   无人机群 + 心脏特效（25 s 后 Kill）
   wait 0.4 → 建区域触发器（存活 25 s）
   wait 25 → 关闭：shutdown 动画 → Dissolve
客户端（每个客户端都收到 mover 创建回调）：
   环境声；wait 1.25 s；本队（或 Seer 自己）才起脚印线程 + HUD 线程
服务端每 0.1 s 对每个在触发器里的实体：
   在 1350 u 球内 → 加 inside_echo_locator；记录"按没按移动键"
   出了球 → 停状态效果
Seer 一方客户端每帧：对在友方区域里的敌人做 3.2.3 检查 → 3.2.4 显示
结束：25 s 到；心脏被打爆（立即冷却）；主人小队全灭（SquadEliminated）；回合结束
```

- **冷却**：弹夹 180，回 1/s → 180 s（`.txt`）；`upgrade_core_ult_cooldown_reduction` → 150（`.txt` Mods）。心脏被毁 → 立即从 0 开始回。
- **升级**：`PAS_ULT_UPGRADE_ONE`（`upgrade_seer_locator_tracking_extension`）：开火暴露的锁定框保留 3.0 s（playlist `seer_ult_extended_gunfire_tracking`，`.nut:1858-1861`、`.nut:2106-2109`），默认 1.25 s。`extended_throw_range` mod：投掷速度 1500。

## 3. 代码

### 3.1 入口

- `MpWeaponEchoLocator_Init`（`.nut:130-176`）：读 playlist（半径、血量、走速判定开关），模型缩放 = 半径 / 1050（`.nut:159`，模型按 1050 做的）；客户端挂 `inside_echo_locator` 开关回调、`script_mover` 创建回调；时长读 `.txt` 的 `fire_duration`（`.nut:169`）。
- `OnWeaponTossReleaseAnimEvent_WeaponEchoLocator`（`.nut:181-208`）：`ThrowDeployable`，记 `refundAmount`。

### 3.2 核心逻辑

#### 3.2.1 落地成装置 `OnEchoLocatorPlanted`（`.nut:251-364`）

```
trace 向下 32 u
echoLocator = script_mover(pariah_heart, VPHYSICS, 碰撞组 BLOCK_WEAPONS, MOVETYPE_FLY)
   realm 跟投射物；script name = echo_locator_script；BossPlayer = owner；同队
   血 125；能被打 / 近战；AI 不当威胁（AI_PRIORITY_NO_THREAT）；不能黏东西；不能在上面放东西
   受伤 / 受伤后 / 死亡回调；EMP 设备；破坏球 EMP；声纳可侦测；毒圈伤害检查；回合结束销毁
   能触发触发器（巨兽踩碎），不被重力电梯 / 黑洞吸
minimap = prop_script(空模型) 挂在心脏上；圈大小 = 半径 / SURVIVAL_MINIMAP_RING_SCALE；只本队显示
若 trace 打到可黏的非世界实体 → 挂上去；否则挂原父物体
thread DeployEchoLocator_Thread
```

`RestartEchoLocatorCooldown`（`.nut:511-524`）：`ultimateWeapon.SetWeaponPrimaryClipCount(0)`，让弹夹从 0 开始回（不然要等 `fire_duration` 结束）。

#### 3.2.2 区域判定 `CreateEchoLocatorTrigger_Thread`（`.nut:951-995`）+ `EchoLocatorTriggerTouching_Thread`（`.nut:747-945`）

```
trigger = 圆柱，半径 = 上高 = 下高 = R（1350）；挂在心脏上；过滤 NPC=all、玩家=all、非角色=1
进入回调 → thread Touching(ent)：只要 玩家 / 分身 / 训练场假人 / 战斗 NPC
   敌方玩家 → 记入"本次到访的敌人"（统计）
   while trigger.IsTouching(ent)，每 0.1 s：
       若 DistanceSqr(trigger 中心, ent 脚底) < R²：
           没有 inside_echo_locator → AddEndless(1.0)
           第一次进这个区域：insideList[ent] += trigger；敌方真人 → 他的小地图显示这个区域
           玩家 → 网络布尔 = (前后轴 != 0 || 左右轴 != 0)
       否则：
           敌方真人 → 隐藏小地图区域；insideList[ent] −= trigger
           insideList 空 → 停 inside_echo_locator，发 EchoLocator_Exit
           网络布尔 = false
   结束（离开触发器 / 死亡）：同样清理
```

多个区域叠加时用 `insideList[ent]` 记在几个区域里，最后一个出去才停状态效果。

注意判定点不一致（推断，要实测）：服务端用**脚底**到心脏中心（`.nut:855`），客户端 `IsPlayerInsideEchoLocator` 用**眼睛**到心脏原点（`.nut:1314-1324`）。边界附近会有一段"服务端算在里面、客户端算在外面"。

#### 3.2.3 行为侦测（客户端）`DoesPlayerPassEchoLocatorMovementCheck`（`.nut:1401-1460`）+ `DoesPlayerPassEchoLocatorWeaponDischargeCheck`（`.nut:1462-1515`）

速度 `GetPlayerSpeedForEchoLocator`（`.nut:1327-1368`）：
- 分身：`|速度 − 地面实体速度|`；
- 训练场假人 / NPC：客户端自己按位置差算的水平速度（`Length2D(Δ位置) / Δt`，每帧更新 `.nut:1881-1901`；不用 Length 是因为上下楼梯会虚高）；
- 玩家：滑铲中 = 实际速度（下坡不按键也会滑）；否则没按移动键 = 0（避免站在火车上被算移动），按了 = `|GetVelocity()|`。

移动检查（速度 > 0 时）：

```
若 playlist seer_ult_speed_override（默认 false）：
    速度 >= 170（约持枪走路）且 没开镜 → 暴露
否则（默认）：
    训练场假人：速度 >= 100 → 暴露（实测蹲走 92，取 100 保险）
    战斗 NPC：一律暴露
    玩家 / 分身：没蹲 或 在滑铲 → 暴露           // 即"蹲走不暴露"
```

开火检查：`Time() − 上次开火 < max(rechamber_time + 1/fire_rate, 0.15)` → 暴露；假人看武器动作是否在 `ACT_RANGE_ATTACK1 … ACT_RANGE_ATTACK_SMG1`。

#### 3.2.4 显示 `EchoLocatorFootstepVFX_Thread`（`.nut:1544-1906`）

每帧：

```
在这个区域线程存活期间（25 s）：
   候选 = 所有带 inside_echo_locator 的实体中：玩家 / 分身 / 假人 / 战斗 NPC，不在相位中，
          是敌人，且在"对我友方"的某个区域里
   enemiesInside[区域] = 候选数（给 HUD）
   超过 12 个 → 按离我的距离排序取前 12
   对每个候选：
     在地面上（IsOnGround，不可靠时向下 trace 5 u）：
        若 移动检查 或 开火检查 通过：
            [开火 且 没有锁定框] 在胸口放锁定框：
                距上次脚印 > 3.0 s → 带入场动画的 P_killroom_lockon（Seer 自己还响"锁定"声）
                否则 → 无动画版 P_killroom_lockon_no_intro
            小地图加敌人标记（没有的话）
            wait = 移动 ? GraphCapped(速度, 100, 300, 0.25, 0.15) : max(开火间隔, 0.15)
            距上次脚印 > wait → 放一个脚印
        刚落地 且 距上次 > 0.15 → 放一个脚印
     在空中：清小地图标记；刚起跳 且 距上次 > 0.15 → 放一个脚印
   小地图标记：距上次脚印 > 0.75 s 删除，否则每帧更新位置和朝向
   锁定框：距上次开火 > 1.25 s（升级 3.0）删；或 距上次脚印 > 0.75 s 删；或 不在区域里了删
```

脚印 `EchoLocatorFootstepVFXClient`（`.nut:1924-1952`）：从脚底上方 20 u 向下 trace 200 u，贴地放粒子（玩家 / 分身 `P_killroom_ground_ping_CP`，AI `…_AI`），朝向贴合地面法线；打到会动的实体就挂在客户端 mover 上（2.5 s 后删）。CP1 = 颜色（玩家 / 假人 / 分身用 `ENEMY_COLOR_FX`，其他 AI 用 `NEUTRAL_COLOR_FX`）。不受去色影响。

已知问题（推断）：`initialLock` 两个分支都设成 false（`.nut:1719`、`.nut:1728`），所以 `ECHO_LOCATOR_INITIAL_MARKER_DURATION = 1.25`（"首次锁定保留更久"）从来不会用到。锁定框只在**开火**时创建，单纯走动只出脚印 + 小地图点。

### 3.3 客户端表现

- 进区域（`inside_echo_locator` 开，`.nut:1520-1542`）：阈值声；驾驶舱粒子 `P_killroom_hud_static`；两个线程：
  - `EchoLocatorScreenFXThink`（`.nut:2060-2086`）：每帧 CP1 = (1, 999, 0)。
  - `EchoLocator_UpdateIntensity_Thread`（`.nut:1961-2040`）：

```
在敌方区域里：CP3 = 敌色；目标强度 = 自己正在暴露（移动且在地面 / 开火）? 1.0 : 0.1
在友方区域里：CP3 = 友色；目标强度 = 区域里有敌人 ? 0.5 : 0.1
都不在：0
每帧 当前强度 向 目标 走 0.01，写 CP2.x
```

  每帧 0.01：从 0.1 到 1.0 要 90 帧（60 fps 约 1.5 s）。和帧率耦合。
- 出区域：阈值声；`EchoLocator_Exit` 停上面两个线程和粒子（`.nut:2042-2058`）。
- HUD `EchoLocatorRUI_Thread`（`.nut:1188-1256`）：RUI `ui/echo_locator.rpak`，`pos` 跟踪心脏、`insideEchoLocator`、`enemiesInside`、`playerIsSeer`、字幕设置、屏幕尺寸，每 0.1 s。
- 环境声（`.nut:1126-1185`）：展开动画结束后开始循环；时长 95% 时播结束声；心脏播 shutdown 动画时提前结束（服务端信号不传客户端，所以客户端靠看动画序列名判断 `.nut:1172-1174`）。
- 无人机群（`.nut:649-693`）：start 动画 → idle（友 / 敌两套）→ 时长 95% 后 vibrate → end 动画 → 销毁。

### 3.4 依赖的公共代码

- `ThrowDeployable`、`OnProjectileCollision_weapon_deployable`（可部署投掷物框架，C 批次 / 道具阶段会写）。
- 状态效果 `inside_echo_locator` → `_shared/E-STATUS-EFFECT.md`。
- `AddSonarDetectionForPropScript` → `_shared/E-SONAR-HIGHLIGHT.md`。
- `Minimap_AddEnemyToMinimap / CommonCleanup / AlwaysShow / Hide`、`CreateCockpitRui`、`AnglesOnSurface`、`PropCheckDamageFromDeathfield`、`TrapDestroyOnRoundEnd`、`AddEMPDamageDevice`、`AddToUltimateRealm`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| 半径 | 1350 | u | `.nut:6`；playlist `seer_ult_radius`（`.nut:2092`） | 球形区域 | 模型按 半径/1050 缩放 |
| 心脏血量 | 125 | HP | `.nut:7`；playlist `seer_ult_hp` | | |
| 持续 | 25 | s | `.txt` `fire_duration` | | |
| 展开后启用延迟 | 0.4 | s | `.nut:17` | 展开动画结束后再等 0.4 s 才建触发器 | |
| 客户端显示延迟 | 1.25 | s | `.nut:18` | | |
| 服务端判定间隔 | 0.1 | s | `.nut:11` TICK_RATE | | |
| 最多显示目标 | 12 | 个 | `.nut:8` | | |
| 脚印间隔 | 0.25（速度 100）→ 0.15（速度 300） | s | `.nut:12-16`、`.nut:1743` | | |
| 开火暴露最短间隔 | 0.15 | s | `.nut:14` | | |
| 锁定框重新带动画 | 距上次 > 3.0 | s | `.nut:22` | | |
| 锁定框 / 小地图防抖 | 0.75 | s | `.nut:23-24` | 多久没新脚印就删 | |
| 锁定框寿命（开火后） | 1.25（升级 3.0） | s | `.nut:25`；playlist `seer_ult_extended_gunfire_tracking` | | |
| 首次锁定保留 | 1.25 | s | `.nut:21` | 代码里实际用不到（见 3.2.4） | |
| 走速判定开关 | false | 开关 | playlist `seer_ult_speed_override`（`.nut:2102`） | true = 速度 ≥170 且没开镜才暴露 | |
| 走速阈值 | 170 | u/s | `.nut:28` | 开关打开时用 | |
| 假人速度阈值 | 100 | u/s | `.nut:29` | | |
| 屏幕强度目标 | 暴露 1.0 / 静止 0.1 / 友方区域有敌 0.5 | — | `.nut:1970-1972` | | |
| 屏幕强度步长 | 0.01 | /帧 | `.nut:1973` | 和帧率耦合 | |
| 动画：待机占比 | 0.95 | × 时长 | `.nut:20` | 最后 5% 震动 + 结束声 | |
| 近战伤害 | 最大血 / 2.9 ≈ 43 | HP | `.nut:442-443` | 3 下打爆 | |
| Crypto EMP 陷阱 | 一下打爆 | — | `.nut:436-440` | | |
| 投掷速度 | 1200（mod 1500） | u/s | `.txt` | | |
| 投掷抬角 | 15 | ° | `.txt` projectile_launch_pitch_offset | | |
| 重力 | 1.0 | × | `.txt` | | |
| 弹跳 | 浅角 0.5 / 陡角 0.3 / 沿法线 0.1 / 随机 0.05；滚动 0.1/s | — | `.txt` grenade_bounce_* | | |
| 投射物碰撞盒 | (−9,−9,−1) → (9,9,24) | u | `.txt` grenade_hull_* | | |
| toss_pullout_time | 0.4 | s | `.txt` | | |
| 冷却 | 180 / 回 1 每秒（升级 150） | s | `.txt` | | |
| `.txt` 爆炸半径 | 内 250 / 外 450，伤害 0 | u | `.txt` | 不造成伤害；推断是给"可部署"框架或 AI 用的占位 | |

## 5. 未解决和要实测的

1. **蹲走是否真的不暴露、站着开镜呢**：默认判定是"没蹲就暴露（只要速度 > 0 且按了移动键）"。测法：两客户端或 bot；Seer 开大招，另一方在圈里分别站立、慢走、蹲走、滑铲、开枪，看 Seer 一方的脚印和锁定框。
2. **服务端脚底 vs 客户端眼睛的判定点差**：测法：在边界附近慢慢走进 / 走出，记状态效果变化的位置和 HUD "在里面"的位置。
3. **"首次锁定保留更久"不生效**是 S21 原样还是 SDK 改的：只能对照原版行为（第二波实测时注意锁定框持续时间）。
4. **RUI `ui/echo_locator.rpak` 和屏幕粒子的样子**：截图。
5. NPC（PvE 敌人）在区域里**一律暴露**（`.nut:1444-1445`），HSD 做 PvE 时这正好是想要的；假人按速度 ≥100。

## 6. HSD 实现

**未实现。**

建议做法（PvE）：
- 心脏 = 一个 `CombatUnit`（125 血，可被敌人打），由投掷物落地生成（复用 `Throw.cs` 的投掷物基类）。
- 区域：每 0.1 s 遍历敌人，`|pos − center| < 1350` → 在里面。HSD 的敌人都是 AI，按 R5 规则"NPC 一律暴露"就等于"圈里的敌人全显示"；如果想保留"静止不暴露"的玩法，就用 R5 给假人的规则（速度 ≥ 100 才暴露）。
- 显示：脚印 = 地面贴花，间隔 `lerp(0.25, 0.15, (v − 100) / 200)`；开火 → 胸口框 1.25 s；HUD 显示圈内敌人数。可以复用 `CombatCore.cs` 的 `outlinedUntil / markedUntil`。
- 心脏被毁 → 立即开始冷却。
- 开关建议：`hsd.combat.exhibit.*`（半径、时长、血量、暴露规则：全部 / 按速度 / 按 R5 玩家规则）。
