# Lifeline 大招 Care Package · 系统记录

批次 D，会话 `combat-d`，2026-10-31。只做了静态研究。重点是**空投舱下落的系统和表现**；物资生成简单写。

路径从 `research-src/s21-platform/scripts/` 开始。缩写：
- **CP** = `vscripts/weapons/mp_ability_care_package.nut`（507 行），**CP.txt** = `weapons/mp_ability_care_package.txt`
- **SHCP** = `vscripts/weapons/sh_care_package.nut`（344 行）：放置预览、落点计算
- **AD** = `vscripts/mp/sh_airdrops.gnut`：通用空投（`AirdropItems`）
- **DP** = `vscripts/ai/_droppod.gnut`：下落动画、落地冲击、推人；**还有一套 NPC 空投舱（刷兵）**
- **FP** = `vscripts/sh_flightpath_utility.gnut`：落点合法性 `VerifyAirdropPoint`

> 都是 Respawn 原版（R5DEV 工单、S3 注释 `// S3: SetCylinderRadius → SetRadius` 说明社区只做了 API 适配，DP:768）。**下落轨迹本身在动画里**（`droppod_loot_drop_lifeline_fast`，模型动画的根运动），脚本看不到高度和速度曲线，只能实测。

## 0. 概要

- **技能**：Lifeline / 大招 / Care Package / `mp_ability_care_package`。
- **一句话**：拿出大招时地上出现一个半透明的空投舱预览（绿 = 能放，红 = 不能）；按下后天上掉下一个空投舱，落地前地面有落点标记和"危险"指示，落地把正下方 72 u 内的东西压坏、把附近的人推开；落地后可以打开，3 个门里是按队伍装备算出来的物资。
- **分类**：系统（下落 + 落点合法性 + 落地冲击）、可视化（预览、落点标记、尘土、光柱）。物资生成对 HSD 没用。
- **可拆出的部件**：
  - 放置预览（抛物线找落点 + 合法 / 非法高亮）→ 3.2.1 `GetCarePackagePlacementInfo` / `DeployableCarePackagePlacement`
  - 落点合法性检查（天空通畅、坡度、边缘、脊、越界、禁放区）→ 3.2.2 `VerifyAirdropPoint`
  - 动画驱动的下落 + 落地事件 → 3.2.3 `AnimateAirdropPod`
  - 落地冲击（震屏、冲击特效、压死、推开）→ 3.2.4 `OnDroppodLanded` / `OnDroppodPushAway`
  - 落点预告（地面标记 + 威胁指示 + AI 禁区）→ 3.2.5
  - **NPC 空投舱刷兵**（同一套下落，落地开门放出最多 4 个 NPC）→ 3.2.7 `Spawn_DropPodSquadCustom`
  - 以上合成共用文档 [`_shared/D-DROP-POD.md`](../_shared/D-DROP-POD.md)

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 预览 | 客户端 `CreateClientSidePropDynamic`（空投舱模型，`rendermode 3`），每帧摆到算出的落点；能放用 `DeployableModelHighlight`，不能放用 `DeployableModelInvalidHighlight`；太近就隐藏 | SHCP:248-327 |
| 落点 | 从眼睛按"压缩过的俯仰角"抛一个虚拟物体（1600 u/s、重力 750、每 0.1 s 一段直线），第一次碰到东西的位置就是落点 | SHCP:126-205；`_utility_shared.nut:2582-2626` |
| 合法性 | `VerifyAirdropPoint`：从 +10000 u 往下扫 hull，再做一圈射线检查 | FP:928 起 |
| 空投舱实体 | `prop_dynamic`，模型 `droppod_loot_animated.rmdl`，solid；挂在一个 `script_mover` 上播动画 | AD:1214-1250；DP:628-653 |
| 下落 | **动画**：`droppod_loot_drop_lifeline_fast`（playlist `lifeline_res_slow_disabled` = true 时；否则慢版 `droppod_loot_drop_lifeline`） | CP:74-82；DP:650 |
| 下落时地面尘土 | `JetwashFX`：每 0.2 s 从舱体往下 60–2000 u 打射线，打到就在地上放 `dropship_dust` 冲击效果 | DP:776-794 |
| 落点标记 | 地面粒子 `FX_AIRDROP_GROUND_MARKER_DEFAULT_CP`（颜色控制点 1）+ 威胁指示 `GRENADE_INDICATOR_GENERIC` 半径 128（在落点上方 48 u），落地时消失 | AD:1901-1942 |
| AI 禁区 | `CreateAirdropBadPlace` 半径 196 | AD:1244；`_gamemode_survival.nut:207` |
| 落地 | 动画事件 `DroppodLanded`：震屏、`droppod_impact` 冲击效果表、72 u 内 1000 伤害（玩家免疫） | DP:655-694、711-717 |
| 推开 | 动画事件 `DroppodPushAway`：挂一个圆柱触发器（半径 100、上 256、下 32），里面的人 / NPC 每帧被设成 350 u/s 水平往外 | DP:719-774 |
| 光柱 | 落地后只给本队看的光柱 `FX_AIRDROP_BEAM_CP` | AD:1342-1343、1944-1990 |
| 开门 | 使用 → `droppod_loot_opening` 动画 → `droppod_loot_open_idle`；物品 0.8 s 后显形 | AD:2033-2087、1375 |
| 物资 | 落地那一刻按全队最低装备档算（`GenerateSmartCarePackageContents`） | CP:136-316 |

全部服务端，预览是客户端。

## 2. 流程

```
切到大招（弹夹满 210）
   │ OnWeaponActivate_care_package → 客户端开预览线程（每帧算落点，绿 / 红）
   │ 提示文字 3 s
   ▼
按开火：OnWeaponPrimaryAttack_care_package_medic（CP:58-128）
   落点不合法 → 返回 0，不扣弹药，什么都不发生
   合法 → CreateCarePackageAirdrop → AirdropItems（AD:1151 起）
   ▼
AirdropItems
   t=0   建空投舱（不可用 isBusy=true）、AI 禁区 196、地面标记 + 威胁指示、标记音
         AnimateAirdropPod：挂 mover、开 JetwashFX、注册动画事件，播下落动画（时长 = 动画长度）
           ├ 动画事件 DroppodPushAway → 推人触发器（直到落地）
           └ 动画事件 DroppodLanded   → 震屏 + 冲击效果 + 72 u 压死
         动画播完 → 信号 StopBraking：地面标记 / 威胁指示消失，尘土停
   落地后 算物资（delayedContentFunc）；可以使用；本队光柱；蒸汽音
   使用 → 开门动画 → 0.8 s 后物品可拿
```

- **触发条件**：大招满；落点合法（3.2.1、3.2.2）。
- **冷却**：`cooldown_type ammo`，弹夹 210 / 每秒 1 = 210 s（CP.txt:23-33）；升级 180 s（CP.txt mods）。
- **打断**：放出后没有打断，空投舱一定会落下。
- **升级**：`PAS_ULT_UPGRADE_ONE` 且标记了"下一次是空投"→ 金色物资（CP:95-111）。

## 3. 代码

### 3.1 入口

| 函数 | 行 | 做什么 |
|---|---|---|
| `OnWeaponActivate_care_package` | SHCP:100-110 | 客户端开预览 |
| `OnWeaponPrimaryAttack_care_package_medic` | CP:58-128 | 落点 → 空投 |
| `CreateCarePackageAirdrop` | SHCP:92-97 | 包一层，调 `AirdropItems` |
| `AirdropItems` | AD:1151-1346 | 通用空投（游戏系统的空投也走这里） |

### 3.2 核心逻辑

#### 3.2.1 落点（`GetCarePackagePlacementInfo`，SHCP:126-205）

```
start = 眼睛；水平朝向 = 视线去掉俯仰
p = GraphCapped( 视角俯仰, −10°, 70°, 0, 1 )         # 抬头 10° 到低头 70° 映射到 0..1（快版）
p = PlacementEasing( p )                              # 前半段 QuadEaseOut 到 0.35，后半段 QuadEaseIn 到 1
pitch = GraphCapped( p, 0, 1, −10°, 70° )
v = AnglesToForward( <pitch, yaw, 0> ) · 1600 u/s     # 快版；慢版 800 u/s、角度 −20..75、时间 1.25 s
GetGravityLandData( start, v, 1.6 s )：每 0.1 s v.z −= 75，走一段直线，第一次碰到世界就停
没碰到 → 用最后一个点，失败
离玩家 < 72 u → 失败并隐藏预览
VerifyAirdropPoint 不过 → 失败
朝向 = 玩家水平朝向 +180°（门对着玩家）
```
`PlacementEasing`（SHCP:208-223）让平视附近的落点比较稳定（平视时 p 变化小），只有低头很多才会把落点拉到脚下。

#### 3.2.2 合法性（`VerifyAirdropPoint`，FP:928 起；空投包参数 `isCarePackage = true`）

| 检查 | 规则 | 失败码 |
|---|---|---|
| 禁放区 | 附近有别的空投禁区 | 0x40 |
| 天空 | 从落点 +10000 u 往下扫 hull（`AIRDROP_MINS/MAXS × 0.65` = ±52 u、高 166 u，FP:925-926） | — |
| 坡度 | 地面法线和竖直夹角 ≤ 55°（游戏空投 20°） | 0x1 |
| 地面 | 不能落在会动的实体上 | 0x2 |
| 起点 | hull 起点不能在实心里 | 0x200 |
| 贴地 | hull 落点离预定点 ≤ 16 u（天上有遮挡时这里会失败） | 0x4 |
| 脊 | 3 个方向、18 u 外往下的射线都要打到地 | 0x80 |
| 边缘 | 6 个方向、64 u 外从 +48 到 −48 的射线都要打到地 | 0x20 |
| 越界 | 不在 `trigger_slip` / 越界触发器里 | 0x100 |
| 门前空间 | 游戏空投才查；空投包跳过（`anglesToTest = []`，FP:1059） | 0x8 |

#### 3.2.3 下落（`AnimateAirdropPod`，DP:628-653）

```
JetwashFX 线程（落地前每 0.2 s 地面尘土）
注册动画事件：DroppodLanded、DroppodPushAway
mover = 在落点建 script_mover；空投舱 SetParent( mover )
waitthread PlayAnim( 空投舱, "droppod_loot_drop_lifeline_fast" )   ← 轨迹在动画里
信号 StopBraking
```
高度、下落时间、减速段都由动画决定。**推断**：动画从高空直落、末段有"刹车"（信号名 StopBraking、`SOUND_CARE_PACKAGE_HOVER_*` 推进器音，DP:22-27）。慢版 / 快版是两段不同的动画。

#### 3.2.4 落地冲击（DP:655-774）

```
DroppodLanded：
   往下 64→−256 u 打线找地面
   CreateShake( 地面, 振幅 16, 频率 150, 时长 1 s, 半径 4000 )，空中的人也震
   PlayImpactFXTable( 地面, "droppod_impact" )
   RadiusDamage( 地面, 1000, 内外半径 72, damageSourceId landing_zone )
     → DropPod_OnLandingZoneDamage：对玩家 ×0（DP:711-717）；NPC、道具、陷阱照吃
   唤醒压到的悬浮载具
DroppodPushAway（比落地早，时刻由动画事件定）：
   圆柱触发器 r=100、上 256、下 32，挂在舱体 REF 上
   进入的实体（玩家和 NPC 都算）：每帧速度 = 水平向外单位向量 × 350，直到离开或落地
```

#### 3.2.5 落点预告（AD:1240-1275、1901-1942）

- 地面粒子标记（颜色 = 空投档次；Lifeline 用自己的颜色 `COLORID_AIRDROP_LIFELINE_COLOR`）；
- 威胁指示（和手雷落点提示同一种，半径 128）；
- AI 禁区 196 u（`CreateAirdropBadPlace`）；
- `isBusy = true`：落地前不能用（R5DEV-293895）；
- 地图有 Leviathan 时会转头看 10–16 s（AD:1285，彩蛋）。

#### 3.2.6 物资（简写，CP:136-497）

落地时才算：对全队每个活人，取每个装备槽（护甲、头盔、击倒护盾、背包）和每把枪的配件（枪管、弹匣、枪托）的**最低档**；每类给"最低档 +1，至少蓝"。三个门：左 = 一件装备 + 大回复；中 = 一个配件 + 大治疗包；右 = 护甲（或 50/50 装备 / 消耗品）。队友全死 → 3 个门都是移动重生信标。**HSD 不需要**，PvE 里换成"按玩家状态补给"的思路可以借。

#### 3.2.7 NPC 空投舱刷兵（DP:94-627；同一套"空投舱从天而降"）

PvE 最有用的部分。`Spawn_DropPodSquadCustom( spawnfuncs, …, team, spawnPoint, flags, doorOpenDelay )`（DP:512-534）：
```
建 droppod_fireteam 模型 + 物理门（DP:76-180）
LaunchAnimDropPod：沿动画 "pod_testpath" 落到 spawnPoint（DP:201-260）
   可选 "Warpfall"：先在 +5888 u 放跃迁特效，延迟后出现，从动画第 4 s 开始播
   动画事件 OnImpact → 震屏（7, 0.15, 1.75 s, 768）、变实心；
      flag SHOULD_PUSH_PLAYERS：point_push 半径 192、力 105
      flag SHOULD_DAMAGE_PLAYERS：压伤 RadiusDamage 128 u
等 doorOpenDelay → 按 spawnfuncs 生成 NPC → NPCsDeployFromDroppod：开门，最多 4 个按 4 套出舱动画出来
```
flag：`DISSOLVE_AFTER_DISEMBARKS`、`SHOULD_PUSH_PLAYERS`、`SHOULD_DAMAGE_PLAYERS`、`SHOULD_ALWAYS_EXPLODE_DOOR`、`TAKES_DAMAGE`（舱体 100 血，DP:31-39、94-114）。调用者：`ai/_ai_reinforcements.gnut:273`、`freelance/freelance_npcs.gnut:668`、`skits/system/_skit_npcs.gnut:741`。

### 3.3 客户端表现

- 预览模型：绿 / 红高亮，太近隐藏（SHCP:248-313）；放出后预览留 0.225 s 再删（SHCP:329-338），和服务端空投舱出现衔接。
- 提示文字 `#WPN_CARE_PACKAGE_PLAYER_HINT` 3 s。

### 3.4 依赖的公共代码

- `GetGravityLandData`（`_utility_shared.nut:2582`）：通用抛物线落点，重力 750，步长 0.1 s。投掷物抛物线显示也能用。
- `PlayAnim`、`AddAnimEvent`、`CreateShake`、`PlayImpactFXTable`、`RadiusDamage`、`CreateThreatIndicator`、`CreateAirdropBadPlace`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 预览抛射速度（快 / 慢） | 1600 / 800 | u/s | SHCP:130、134 | 决定能放多远 | 大 = 更远 |
| 俯仰范围（快） | −10° 到 70° | ° | SHCP:132-133 | 慢版 −20 到 75 | |
| 模拟时长（快 / 慢） | 1.6 / 1.25 | s | SHCP:135、137 | 超时没落地 = 失败 | |
| 模拟步长 | 0.1 | s | `_utility_shared.nut:2589` | | |
| 重力 | 750 | u/s² | `_utility_shared.nut:2591` | | |
| 缓动中点 | 0.35 | — | SHCP:217 | 平视附近落点稳定度 | |
| 最近距离 | 72 | u | SHCP:138 | | |
| 合法 hull | ±52 × 高 166 | u | FP:925-926 ×0.65 | 舱的占地 | |
| 天空检查高度 | 10000 | u | FP:944 | | |
| 最大坡度 | 55 | ° | FP:937 | 游戏空投 20 | |
| 贴地容差 | 16 | u | FP:930 | | |
| 脊检查 | 3 向 × 18 | u | FP:987-1001 | | |
| 边缘检查 | 6 向 × 64，±48 高 | u | FP:936、1007 起 | | |
| AI 禁区半径 | 196 | u | `_gamemode_survival.nut:207` | | |
| 威胁指示 | 半径 128，+48 高 | u | AD:1907 | | |
| 下落动画 | `droppod_loot_drop_lifeline_fast` | — | CP:76 | 时长待测 | |
| 尘土间隔 / 射线 | 0.2 s / 60–2000 u | — | DP:787、791 | | |
| 落地压伤 | 1000，半径 72（玩家免疫） | HP / u | DP:672-694、711-717 | | |
| 落地震屏 | 振幅 16、频率 150、1 s、半径 4000 | — | DP:665 | | |
| 推人触发器 | r 100、上 256、下 32 | u | DP:724-726 | | |
| 推人速度 | 350 | u/s | DP:771 | | |
| 物品显形延迟 | 0.8 | s | AD:1375 | | |
| 冷却 | 210 | s | CP.txt:23-33 | | |
| 冷却升级 | 180 | s | CP.txt mods | | |
| NPC 舱震屏 | 7、0.15、1.75 s、768 | — | DP:273 | | |
| NPC 舱推力 | 半径 192、力 105 | — | DP:294-295 | | |
| NPC 舱跃迁高度 | 5888 | u | DP:246 | | |
| NPC 数 | ≤ 4 | 个 | DP:578 | | |

## 5. 未解决和要实测的

| 问题 | 为什么不确定 | 怎么测 |
|---|---|---|
| 下落时间、起始高度、速度曲线（快 / 慢版） | 在动画里 | 训练场放大招，AgentLink 每 0.05 s 记 scriptname `CARE_PACKAGE_SCRIPTNAME` 的实体位置（它挂在 mover 上，读 `GetOrigin` 应是世界坐标）；拟合"高度 – 时间"曲线，标出 `DroppodPushAway` / `DroppodLanded` 两个事件的时刻（在服务端加 `printt` 或看推人效果开始时间） |
| 推人什么时候开始 | 动画事件时刻 | 站在落点上，记玩家被推的时刻和速度 |
| 1000 伤害对 NPC | 推断 NPC 会被压死 | 有 NPC 的环境下放在 NPC 头上 |
| NPC 空投舱 `pod_testpath` 时长 | 动画 | `GetDropPodAnimDuration()` 在 `DropPod_Init` 里算过（DP:70-72），可以用控制台打印 |

## 6. HSD 实现

**未实现。**

建议做法（只拿系统）：
- `DropPod`：给一个落点 + 一条"高度 – 时间"曲线（先用占位：从 +3000 u 以 2.5 s 落下，末 0.5 s 减速，等实测替换），落地触发 `OnLanded`，带三件套：落点预告（地面圈 + AI 避让区）、落地压伤 / 推开、震屏。
- 用途 1：**刷敌人**（照 3.2.7：落地 → 延迟 → 开门 → 放出 ≤4 个敌人）。这是 PvE 刷怪点很好的表现方式。
- 用途 2：补给舱（玩家技能）。
- 落点合法性照 3.2.2 简化成：天空通畅、坡度 ≤55°、四周有地。
- 详细接口见 `_shared/D-DROP-POD.md`。开关：`hsd.tf2.x.dropPod`。
