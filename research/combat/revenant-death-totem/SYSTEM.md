# Revenant 旧大招 Death Totem（死亡图腾）· 系统记录

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`。主脚本 `vscripts/weapons/mp_ability_revenant_death_totem.nut`（1803 行），武器设置 `weapons/mp_ability_revenant_death_totem.txt`。S21 里 Revenant 的大招已经是 Forged Shadows（`revenant-forged-shadows/SYSTEM.md`），这个脚本还在、公共代码里还有很多调用点。

**HSD 关心的是"标记位置 → 召回"这套系统**，可以拿去做检查点式回溯。本文按这个重点写。

## 0. 概要

- **技能**：Revenant（旧）/ 大招 / Death Totem / `mp_ability_revenant_death_totem`（`.txt` `printname #ABL_DEATH_TOTEM`）。
- **一句话**：放一个图腾（可被打，100 血，至少存在 30 s）；队友（和敌人）去"使用"它，就在**使用时站的位置**留下一个标记，自己进入 25 s 的暗影状态：护盾不算、血量封顶 100；暗影期间受到致命伤害时**不死**，而是传送回标记点、血量设为 min(50, 使用时血量)、0.25 s 无敌、1.5 s 减速。时间到了就结束，不传送。
- **分类**：系统 ✔（**标记 + 致死触发召回 + 安全落点 + 无敌帧**，正是 HSD 检查点回溯需要的）、可视化 ✔（暗影皮肤、召回时一道影子从死亡点飞回标记点、全息标记人偶、屏幕特效）；好技能（效果）PvE 中："第二条命"。
- **可拆出的部件**：
  - 标记一个回溯点（位置、朝向、蹲姿、跟着移动平台走）→ 3.2.2 `DeathTotem_MarkLocation` / `DeathTotem_CreateHoloPilotRecallMarker`
  - 致死拦截：受伤管线里"这一下会死 → 问回调要不要救" → 3.2.3 `ShadowHealthUpdate` + `DeathTotem_OnShadowHealthExhausted`
  - 召回传送：打断一切交互 → 安全落点 → 设朝向 / 速度 0 / 蹲姿 → 状态效果 → 3.2.4 `DeathTotem_RecallPlayer`
  - 召回后无敌帧 → 3.2.5 `DeathTotem_InvincibilityFramesAfterRecall`
  - 影子飞行特效（死亡点 → 标记点 0.5 s）→ 3.2.6 `CreateShadowToRecallLocation`
  - 距离限制：离图腾太远就失去标记（默认关）→ 3.2.7 `DeathTotem_MarkEndOnDistanceUpdate`
  - 掉出地图也召回 → 3.4（`_trigger_functions.gnut:486`）
  - 放置预览（object placer）→ 3.1

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 放图腾 | `object_placer` 武器（`.txt` `object_placer 1`、预览模型 `revenant_totem.rmdl`、最远 75 u、离地 ≤ 5 u、悬空比例 ≤ 0.7、强制直立） | 引擎画预览、给落点；`OnWeaponPrimaryAttack` 检查 `ObjectPlacementHasValidSpot` |
| 图腾 | `prop_script`（`revenant_totem.rmdl`），100 血，可用（use）、可被打、可近战；在移动平台上时再套一个 script mover | `.nut:272-457` |
| 图腾存在时间 | 30 s，**且**一直延到最后一个标记过的人结束 | `.nut:448-456` |
| 使用图腾 | `SetUsable` + `USABLE_BY_TEAMMATES \| USABLE_BY_ENEMIES` + 使用回调 | `.nut:434-438`、`.nut:1431-1452`。敌人也能用 |
| 标记点 | 一个不可见、不能动、不受伤的玩家分身（`CreatePlayerDecoy`），挂在图腾上；召回目标 = 这个分身的位置 | `.nut:902-982`、`.nut:695` |
| 暗影状态 | 原生 `player.EnterShadowForm()` / `LeaveShadowForm()`；血量封顶 100 | `.nut:1062-1067`、`.nut:1128` |
| 暗影期间护盾不算 | 公共受伤管线：暗影中走 `ShadowHealthUpdate`，不走护盾 | `vscripts/mp/_codecallbacks.gnut:578-587` |
| 致死拦截 | `ShadowHealthUpdate`：这一下会把血打到 ≤0 → 逐个问 `entOnShadowHealthExhaustedCallbacks`，有一个返回 true 就把本次伤害设 0 | `vscripts/_health_regen.gnut:716-738`；`_codecallbacks.gnut:777-778` |
| 计时 | 状态效果 `death_totem_visual_effect`（25 s）+ 服务端线程 `wait` | `.nut:1357`、`.nut:1134-1162` |
| 召回传送 | 服务端：一串打断 + `PutPlayerInSafeSpot` + `SetAngles` + `SetVelocity(0)` + 强制蹲 / 站 0.2 s | `.nut:684-831` |
| 无敌帧 | `SetInvulnerable()` 0.25 s | `.nut:833-848` |
| 减速 | 状态效果 `move_slow`（0.9，1.5 s，淡出 0.5 s） | `.nut:813-818` |
| 召回屏幕特效 | 状态效果 `death_totem_recall`（0.25 s）→ 客户端驾驶舱粒子 `P_training_teleport_FP` | `.nut:820`、`.nut:1629-1671` |
| 影子飞回 | script mover + 粒子 `P_death_shadow_recall`，0.1 s 后 `NonPhysicsMoveTo` 0.5 s | `.nut:850-870` |
| 暗影外观 | 换成基础角色模型 + 暗影皮肤（`ShadowSquadApplyCharacterSkin`），身体 / 两眼粒子 | `.nut:1071-1092`、`.nut:1168-1219` |
| HUD | 全屏 RUI `ui/death_protection_status.rpak`（剩余时间）；队友头像框变暗影色 `<245,81,35>` | `.nut:1510-1570` |
| 1P 屏幕 | 驾驶舱粒子 `P_Bshadow_screen` | `.nut:1608-1627` |

## 2. 流程

```
[Revenant] 按大招 → 预览图腾 → 有效落点时按开火（.nut:194-233）
     锁武器；动作期间禁跑墙 / 二段跳 / 挂边（直到武器收起）
     thread DeathTotem_DeployTotem（.nut:272）
         图腾 prop（落点上方 20 u，yaw +60°）、100 血、小地图本队可见、声纳可扫到
         展开动画 → 闪光 → 待机动画；开始可用、可被打
         0.3 s 一次检查有没有卡进几何体：0.2 s 内卡住 → 删图腾并退还大招（.nut:472-545）
         存在 30 s；之后只要还有人在用（标记中）就继续存在
         结束 / 被打爆（伤害 > 剩余血 → 血设 1，发 TotemDestroyed）→ 所有标记者 DeathTotem_ForceEnd → 收起动画、淡出、删除

[任何人] 对着图腾按使用（.nut:1431-1452）
     条件：没有标记中、不在倒地、不在相位、手上不是消耗品（.nut:1402-1428）
     用过并召回过的人不能再用同一个图腾（markedPlayerArray，.nut:1437-1439）
     → DeathTotem_MarkLocation（.nut:1353-1386）
         状态效果 death_totem_visual_effect 25 s
         在攀爬就打断攀爬
         记 RecallData：位置、朝向、速度、是否蹲、是否在交互动作中
         建标记分身（当前位置，挂在图腾上）
         thread DeathTotem_HandleUserDeathOrDesync：
             EnterShadowForm；savedTotemHealth = min(50, 当前血)；血封顶 100
             注册"暗影血耗尽"回调；暗影皮肤和粒子
             21 s 后（25 − 4）身上计时粒子 + 3P 警告声；23.25 s 后 1P 警告声；25 s 结束

暗影期间受到致死伤害 → ShadowHealthUpdate → DeathTotem_OnShadowHealthExhausted（.nut:671-682）
     能召回 → SetHealth(savedTotemHealth)；thread DeathTotem_RecallPlayer；返回 true（本次伤害 0）
DeathTotem_RecallPlayer（.nut:684-831）→ 发 DEATH_TOTEM_RECALL_SIGNAL → 上面的线程结束 → 清理标记、离开暗影

结束条件（HandleUserDeathOrDesync 的 EndSignal，.nut:1056-1060）：
     死亡 / 销毁 / 召回 / DeathTotem_ForceEnd（图腾没了、距离超限）/ 图腾销毁 / 25 s 到
     → 清理：取消皮肤、删标记分身、停状态效果、LeaveShadowForm、去掉回调
```

- **时间到不召回**：25 s 线程正常结束只做清理（`.nut:1098-1132`），不传送。召回只发生在致死时（和掉出地图时，见 3.4）。
- **冷却**：弹夹 180，回 1/s → 180 s；图腾存在期间加 `ultimate_active` mod 回充 0（`.txt` Mods；`.nut:211`、`.nut:373-375` 结束时移除）。
- **使用期间不能用消耗品**：`DENY_DEATH_TOTEM`（`vscripts/weapons/mp_ability_consumable.nut:2681-2682`）。

## 3. 代码

### 3.1 入口

- `MpAbilityRevenantDeathTotem_Init`（`.nut:128-176`）：注册信号；客户端挂 `death_totem_visual_effect`、`death_totem_recall` 的回调和图腾创建回调；playlist `revenant_totem_buff_duration`（默认 25）、`revenant_totem_buff_use_ending_fx`（默认 true）。
- `OnWeaponPrimaryAttack_ability_revenant_death_totem`（`.nut:194-233`）：落点无效 → 空响；否则加 mod、锁武器、`DeathTotem_DeployTotem(owner, 预览落点, 预览角度, 预览父物体, 载具挂点)`。
- 放置预览：引擎的 object placer。脚本里另有一个没被调用的 `CalculateDeathTotemPosition`（`.nut:1722-1794`，理想距离 72 u，朝前移动时最多再加 144 u，按俯视角度夹住，坡面重算）——是旧的脚本放置算法（推断），留作参考。

### 3.2 核心逻辑

#### 3.2.1 图腾 `DeathTotem_DeployTotem`（`.nut:272-457`）

见第 2 节。要点：
- 生命周期 = `while (now < 部署 + 30) || 有人标记中`（`.nut:448-456`）："像 Lifeline 图腾，最后一个使用者结束前不会消失"（`.nut:55` 注释）。
- 血量写的是 100（`.nut:291-292`），常量 `DEATH_TOTEM_TOTEM_HEALTH = 150`（`.nut:49`）没用上。
- 被打：友方（非主人）伤害 ×0，友方 inflictor（如 Caustic 桶）×0（`.nut:590-617`）；致命一击时把伤害设 0、血设 1、不再受伤、发 `TotemDestroyed`（`.nut:632-660`），由收起流程播"摧毁"动画（`.nut:571-580`，血 ≤1 或在溶解时）。
- 卡几何体检测：`TraceHull(图腾原点, +up, (−8,−8,0)–(8,8,32))` startSolid 且命中世界 / 门 / mover 等 → 删除；0.2 s 内发生则退还大招（`.nut:472-545`）。

#### 3.2.2 标记 `DeathTotem_MarkLocation`（`.nut:1353-1386`）+ `DeathTotem_CreateHoloPilotRecallMarker`（`.nut:902-982`）

```
statusID = AddTimed(death_totem_visual_effect, 1.0, 25, 0)
[服务端]
  在攀爬 → ClearTraverse
  图腾的使用者表 += player
  data = { origin, angles, velocity, wasCrouched, wasInContextAction, statusID, totem }
  decoy = player.CreatePlayerDecoy(..., 不移动)           // 当前位置、当前姿势
      不碰撞、不受伤、不能近战、不超时、对所有人不可见、不当目标
      SetParent(totem)                                     // 图腾在移动平台上时标记跟着走
  base（隐藏的底座模型）向下 100 u 找地面，可黏就挂上去
  两个半径模型（只主人可见），只有 playlist revenant_totem_has_distance_limit 开时显示
  data.holoMarker = decoy …；markedLocation[player] = data
  thread DeathTotem_HandleUserDeathOrDesync
```

召回时的目标点：`recallOrigin = holoMarker 有效 ? holoMarker.GetOrigin() : totem.GetOrigin()`（`.nut:695`）。`data.origin` 记了但召回不用它；`data.velocity` 记了，召回时那一行被注释掉（`.nut:693`），召回后速度一律 0。

对 HSD 的意义：标记点存的是"一个挂在锚点上的实体"，不是一个死坐标，所以锚点（图腾）移动时标记点跟着动。

#### 3.2.3 致死拦截 `ShadowHealthUpdate`（`_health_regen.gnut:716-738`）+ `DeathTotem_OnShadowHealthExhausted`（`.nut:671-682`）

```
公共受伤管线（_codecallbacks.gnut:578-587）：
   玩家在暗影中 → save = ShadowHealthUpdate(ent, dmg)      // 不走护盾
   …
   save → 本次伤害 = 0（_codecallbacks.gnut:777-778）

ShadowHealthUpdate：
   dmg == 0 → false
   加 DF_SHADOW_DAMAGE
   若 health − dmg <= 0：对每个 entOnShadowHealthExhaustedCallbacks 回调：返回 true → save = true
   返回 save

DeathTotem_OnShadowHealthExhausted(player)：
   能召回（有标记且活着）→ SetHealth(savedTotemHealth)；thread RecallPlayer；返回 true
   否则 false（照常死）
```

这是一个**通用的"致死前问一声"钩子**：任何系统都可以 `AddEntityCallback_OnShadowHealthExhausted`（`_codecallbacks_common.gnut:882-903`）注册，返回 true 就救下这一次。暗影僵尸模式也用它（`sh_ability_shadow_zombie.nut:544-555`、`:809`）。限制：只在 `IsShadowForm()` 时生效。

#### 3.2.4 召回传送 `DeathTotem_RecallPlayer`（`.nut:684-831`）

```
读 markedLocation：朝向、标记分身、图腾、是否蹲
recallOrigin = 标记分身位置（没有就图腾位置）
强制结束救人动画；身上黏的投射物全部脱落（改成受重力下落）
totemRecallTime = now
thread 影子从当前位置（身体中心）飞到 recallOrigin + (0,0,40)
声音、语音
[在工作台合成 → 等脱离]
PreparePlayerForPositionReset
打断：Valk 升空 / 跟随、相位隧道（使用 / 放置）、钩爪、喷气、Newcastle 跳跃；清近战锁定
蹲 → 强制蹲 0.2 s；否则强制站 0.2 s                   // 先改碰撞盒再找落点
PutPlayerInSafeSpot(player, 忽略图腾, …, recallOrigin, recallOrigin)
   失败 → SetOrigin(图腾位置)；离目标 ≥ 20 u → 打警告
SetAngles(标记时朝向)；SetVelocity(0)
move_slow 0.9，1.5 s，淡出 0.5 s                       // playlist 可调
death_totem_recall 状态效果 0.25 s（客户端屏幕特效）
熄火；Server_InvalidateLagCompensationRecords（注释："极其危险，用前问引擎组"）
Signal DEATH_TOTEM_RECALL_SIGNAL
thread 无敌帧
结束跳伞；Signal SIGNAL_TELEPORTED
```

其他系统读 `totemRecallTime`：太空电梯 1 s 内不触发（`vscripts/mp/sh_space_elevator.gnut:961`），相位隧道 2 s 内不触发（`vscripts/weapons/mp_weapon_phase_tunnel.nut:1843`）；Fuse 火圈的伤害线程在召回时结束（`mp_weapon_mortar_ring_missile.nut:819`）。

#### 3.2.5 无敌帧 `DeathTotem_InvincibilityFramesAfterRecall`（`.nut:833-848`）

`SetInvulnerable()` → `wait 0.25`（`SCREEN_FX_STATUS_EFFECT_DURATION`）→ `ClearInvulnerable()`（OnThreadEnd 保证清掉）。时长和召回屏幕特效共用一个常量。

#### 3.2.6 影子飞回 `CreateShadowToRecallLocation`（`.nut:850-870`）

script mover 在起点（只放进玩家的 realm），挂 `P_death_shadow_recall`，3P 飞行声（不给本人）；`wait 0.1` → `NonPhysicsMoveTo(终点, 0.5, 0, 0)`（匀速）→ `wait 0.5` → 删除。玩家本人在 0.1 s 前已经被传送（同一帧，推断），影子是给别人看的"轨迹"。

#### 3.2.7 距离限制 `DeathTotem_MarkEndOnDistanceUpdate`（`.nut:1262-1313`，默认关）

playlist `revenant_totem_has_distance_limit`（默认 false，`.nut:968`）打开时：每帧算头部到图腾的 **2D** 距离²；≥2500² 开始响警告，在外面待的时间超过 `GraphCapped(d², 2500², 3000², 5, 0)` 就失去标记（越远越快：2500 u 处 5 s，3000 u 处立刻）。

### 3.3 客户端表现

- `death_totem_visual_effect` 开（`.nut:1510-1538`）：`hasMark = true`；全屏 RUI `ui/death_protection_status.rpak`（`maxDuration` 25、`timeRemaining` 跟踪状态效果）；驾驶舱粒子 `P_Bshadow_screen`（CP1 = 1,1,1）+ 1P 激活 / 循环声；刷新队伍头像框（暗影状态 + 颜色 245,81,35）。
- 关（`.nut:1572-1606`）：反向清理。
- `death_totem_recall` 开（`.nut:1629-1671`）：驾驶舱粒子 `P_training_teleport_FP`（CP1 = 1, 999, 0），0.25 s。
- 使用提示文字：能召回时空；用过的显示 `#DEATH_TOTEM_TOTEM_USED`；使用后 2 s 内隐藏（避免状态效果到达前提示闪错，`.nut:1454-1500`）。
- 背包 UI、小地图头像用暗影框（`cl_survival_inventory.nut:3311`、`cl_minimap.gnut:1973`）。

### 3.4 依赖的公共代码

- **致死钩子**：`ShadowHealthUpdate`（`vscripts/_health_regen.gnut:716`）、`AddEntityCallback_OnShadowHealthExhausted`（`vscripts/_codecallbacks_common.gnut:882`）、受伤管线 `vscripts/mp/_codecallbacks.gnut:575-587, :777`。
- **掉出地图也召回**：`vscripts/_trigger_functions.gnut:486-487`：坠落触发器里，能召回就 `DeathTotem_RecallPlayer`，否则 `KillPlayer(fall)`。
- **安全落点**：`PutPlayerInSafeSpot`、`PreparePlayerForPositionReset`（公共工具，没读实现）。
- 原生：`EnterShadowForm / LeaveShadowForm / IsShadowForm`、`CreatePlayerDecoy`、`SetInvulnerable`、`PushForcedStance`、`Server_InvalidateLagCompensationRecords`、object placer。
- 状态效果 `death_totem_visual_effect`、`death_totem_recall`、`move_slow`、`disable_wall_run`、`disable_double_jump`、`disable_automantle_hang`（`status_effect_types.txt:10, :94-95`）→ `_shared/E-STATUS-EFFECT.md`。
- 声纳可扫描：`AddSonarDetectionForPropScript(totem)`（`.nut:326-327`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| 标记 / 暗影持续 | 25 | s | `.nut:59`；playlist `revenant_totem_buff_duration`（`.nut:174`） | 标记有效期 | 必须 > 4（警告提前量），有 Assert（`.nut:1135`） |
| 图腾最短存在 | 30 | s | `.nut:55` | 之后等最后一个使用者结束 | |
| 图腾血量 | 100（常量 150 未用） | HP | `.nut:291-292`、`.nut:49` | | |
| 暗影血量上限 | 100 | HP | `.nut:56` | 使用时血量高于 100 截到 100 | |
| 召回后血量 | min(50, 使用时血量) | HP | `.nut:57`、`.nut:1063`、`.nut:675` | | |
| 无敌帧 | 0.25 | s | `.nut:65`、`.nut:847` | | |
| 召回屏幕特效 | 0.25，淡出 0.25 | s | `.nut:65-66`、`.nut:820` | | |
| 召回减速 | 0.9（严重度），1.5 s，淡出 0.5 s | — / s / s | playlist `revenant_totem_recall_slow_amount / _duration / _easeOut`（`.nut:813-818`） | 刚回来几乎走不动 | 0 关掉 |
| 召回后速度 | 0 | u/s | `.nut:811` | 保存的速度不用 | |
| 召回后姿势 | 按标记时蹲 / 站，强制 0.2 s | s | `.nut:764-774`、`.nut:1222-1258` | | |
| 落点偏差警告 | 20 | u | `.nut:793` | 安全落点离目标超过 20 u 打警告 | |
| 影子飞行 | 起飞延迟 0.1，飞 0.5，终点抬高 40 | s / s / u | `.nut:861-864`、`.nut:712` | | |
| 警告（3P / 身上计时粒子） | 结束前 4.0 | s | `.nut:61`；粒子 CP1 = 4 | | |
| 警告（1P） | 结束前 1.75 | s | `.nut:60` | | |
| 距离限制开关 | false | 开关 | playlist `revenant_totem_has_distance_limit`（`.nut:968`） | | |
| 距离限制区间 | 2500 → 3000（2D） | u | `.nut:43-44` | | |
| 超距失效时间 | 5 → 0 | s | `.nut:46`、`.nut:1300` | | |
| 图腾放置 | 最远 75，离地 ≤5，悬空 ≤0.7，强制直立 | u / u / 比例 | `.txt` object_placement_* | | |
| 图腾偏移 | 落点上方 20，yaw +60° | u / ° | `.nut:286-288` | | |
| 卡几何体检测 | 每 0.3 s；hull (−8,−8,0)–(8,8,32)；0.2 s 内卡住退还大招 | s / u / s | `.nut:487`、`.nut:509`、`.nut:543` | | |
| 冷却 | 180 / 回 1 每秒；图腾在时 0 | s | `.txt` MP_BASE、`ultimate_active` | | |
| fire_rate / deploy_time | 0.57 / 0.03 | — / s | `.txt` | | |
| 旧脚本放置：理想距离 | 72（+ 前进速度 0–300 映射 0–144） | u | `.nut:75`、`.nut:1734-1738` | 未调用 | |
| 召回后其他系统冷静期 | 太空电梯 1 s，相位隧道 2 s | s | `sh_space_elevator.gnut:961`、`mp_weapon_phase_tunnel.nut:1843` | | |

## 5. 未解决和要实测的

1. **本地 S3 dedi 有没有暗影状态**：SDK 在 `vscripts/mp/_staging_area.gnut:1843` 注释了 `// S3: shadow form not available`（那一段把暗影伤害分支注释掉了）。但 `_codecallbacks.gnut:580-582` 的同一分支没注释。如果 S3 引擎没有 `EnterShadowForm` / `IsShadowForm`，Death Totem 的暗影 + 致死召回整套跑不起来，Forged Shadows 的 `EnterShadowFormFortified` 也一样。测法：AgentLink 在服务端给玩家 `EnterShadowForm()` 看报不报错、`IsShadowForm()` 返回什么；再用 `DeathTotem_*` 走一遍：放图腾、使用、受致死伤害，看是否召回。**这是本批最重要的实测项。**
2. **时间到是否召回**：S21 脚本是不召回。早期 Apex 的行为记不清，不能用来对照；按脚本记。实测确认即可。
3. **`PutPlayerInSafeSpot` 的落点规则**（搜索范围、失败条件）：没读实现。测法：在窄缝 / 斜坡上标记，召回后记偏差（脚本会打 20 u 警告）。
4. **召回同一帧发生了什么顺序**：影子 0.1 s 后才飞，玩家是不是立刻到位。测法：录 10 Hz 位置（w4_probe 方式）。
5. **暗影期间移动 / 其他变化**（原生 `EnterShadowForm` 里）：脚本看不到。

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
1. ✅ **S3 dedi 有暗影状态**：`EnterShadowForm()` 可用，`IsShadowForm` false → true，`LeaveShadowForm()` 后 false。❌ 但 **Death Totem 武器本地没加载**：`GiveOffhandWeapon( "mp_ability_revenant_death_totem" )` 报 "Can't find weapon … may need to be precached"。所以放图腾 → 使用 → 致死召回整套本地测不了；按脚本做。
2–5 因此都没测。

## 6. HSD 实现

**未实现。** 最接近的是 `HSD-Unity/Assets/HSD/Game/Runtime/Combat/MovementItems.cs:55-160` `PhaseRewind`（相位回溯：按时间记录、倒回 2 s、1.8 s 放完、结束速度 0、蹲姿抬 20 u、找空位）。两者对比：

| | R5 Death Totem | HSD PhaseRewind |
|---|---|---|
| 回到哪里 | 使用图腾时站的点（挂在图腾上，跟着平台走） | 2 s 前的位置（时间环） |
| 何时触发 | 致死伤害 / 掉出地图（被动） | 按键（主动） |
| 路径 | 瞬移 + 给别人看一道 0.5 s 的影子 | 沿记录路径倒放 1.8 s，期间相位 |
| 结束状态 | 速度 0、恢复蹲 / 站、朝向回到标记时、0.25 s 无敌、1.5 s 减速 0.9、血 = min(50, 标记时血) | 速度 0、蹲姿抬 20 u、找空位 |

建议做法（检查点式回溯）：
- **检查点** = `{ 锚点实体, 相对锚点的偏移, 朝向, 是否蹲, 血量快照 }`，锚点可以是关卡里的检查点物体或移动平台；没有锚点就存世界坐标。
- **致死钩子**：在 `CombatSim` 的伤害入口加"这一下会死 → 依次问注册的回调，有一个救就把这次伤害设 0"，和 R5 `ShadowHealthUpdate` 一样，不限于暗影状态。死亡检查点、复活道具、无敌 buff 都能挂在这上面。
- **召回**：复用 `PhaseRewind` 结束时的"找空位"逻辑（`MovementItems.cs:55-58` 描述）；按 R5 设朝向、速度 0、蹲姿，之后 0.25 s 无敌、1.5 s 减速（减速要在移动层留入口，同 Bloodhound 加速）。
- **画面**：死亡点到检查点画一道 0.5 s 的拖尾；屏幕 0.25 s 传送特效。
- 开关建议：`hsd.combat.checkpointRecall.*`（有效期、召回血量、无敌帧、减速、是否时间到也召回）。
- 和 R5 的差别实现时进 `R5-DIFF-ARCHIVE.md`（例如 HSD 要不要"时间到也召回"）。
