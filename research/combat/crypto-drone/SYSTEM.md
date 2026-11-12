# Crypto 战术 Surveillance Drone（+ 被动 Neurolink）· 系统记录

批次 D，会话 `combat-d`，2026-10-31。只做了静态研究。

路径从 `research-src/s21-platform/scripts/` 开始。**CD** = `vscripts/weapons/mp_ability_crypto_drone.nut`（3659 行），**CD.txt** = `weapons/mp_ability_crypto_drone.txt`。

> 这份脚本**主体是 Respawn 原版**（有开发者署名注释 `(mk)`、`jordanh`、`dklein`，大量 R5DEV 工单号），但有几处 **SDK 社区改过**：Neurolink 的视野判断（CD:2854-2879，注释写明 S3 没有原生函数）、无人机"用"东西的部分（CD:935-1009，注释署名 Cafe）、被打退出视角（客户端回调是空的，CD:637-643）。改过的地方在正文里逐条标了。飞行物理在**引擎里**（`VEHICLE_FLYING_CAMERA`），脚本里看不到速度和加速度。

## 0. 概要

- **技能**：Crypto / 战术 / Surveillance Drone / `mp_ability_crypto_drone`。被动 Neurolink 在同一个文件里（`NeurolinkThink`）。
- **一句话**：扔出一架会飞的小无人机，可以切到它的视角操控着飞（最远约 201 m），在里面开门、开补给箱、放 EMP；无人机周围 30 m、看得到的敌人会被标出来。无人机 50 血，被打掉后战术进入冷却。
- **分类**：系统（主）、可视化（次）。效果（侦察）对 PvE 一般。
- **可拆出的部件**：
  - 可操控载具 + 视角切换（玩家"坐进"远处的实体，身体留在原地）→ 3.2.2 `CryptoDrone_CreateFlyingCameraVehicle` / 3.2.3 `SwapToCameraView_Thread` / `TransitionOutOfCamera`；共用文档 [`_shared/D-REMOTE-DRONE.md`](../_shared/D-REMOTE-DRONE.md)
  - 扔出 → 飞一段 → 自动停下（点按 / 长按两种）→ 3.2.1 `CryptoDrone_ProjectileMovementThink`
  - 召回（动画 → 销毁 → 回冷却）→ 3.2.4 `Drone_RecallThink`
  - 超距自动召回 + 越界提示 → 3.2.4、3.3
  - 视野内扫描标记（Neurolink）→ 3.2.5 `NeurolinkThink`
  - 设备登记表（EMP 能影响谁）→ 3.2.6；共用文档 [`_shared/D-DEVICE-REGISTRY.md`](../_shared/D-DEVICE-REGISTRY.md)
  - 无人机里自动换弹 → 3.2.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 / 来源 |
|---|---|---|
| 扔出 | 投掷物 `ThrowDeployable`，几乎无重力（`projectile_gravity_scale 0.001`），速度 400 u/s；无人机实体**挂在投掷物上**一起飞 | CD:734-759、CD.txt:42 |
| 无人机本体 | `player_vehicle` 实体，`VehicleSetType( VEHICLE_FLYING_CAMERA )`，`SOLID_BBOX`，可受伤，可被近战，AI 会打它（`EnableAttackableByAI( 5 )`） | CD:1210-1329 |
| 飞行 | 引擎的飞行相机载具，玩家坐进去后由玩家输入驱动（`VehicleSetDriver`） | CD:1713；速度不在脚本里（`CAMERA_FLIGHT_SPEED 450` 声明了没用，CD:94） |
| 挡子弹的护盾 | 一个半径 16 的 `vortex_sphere`，挂在无人机 `__illumPosition` | CD:1568-1600 |
| 视角切换 | 状态效果 `camera_view` + `ContextAction_SetInVehicle` + 隐藏主 HUD 的电影标志 | CD:1693-1695 |
| 切换过场 | 1P 粒子 `P_crypto_hud_boot`（快版 `_fast`）+ 全屏 RUI `camera_transition` 1.2 s | CD:520-609 |
| 无人机视角 HUD | 全屏 `ui/camera_view.rpak`：无人机血量、EMP 充能、召回进度、玩家位置朝向；小地图缩到 0.7、染绿 | CD:2263-2355 |
| 出视角 | 0.2 s 白色淡出 → 淡入；`AnimViewEntity` 0.3 s 回到身体 | CD:1949-2047 |
| 玩家身体上的效果 | 头上一个 3P 面罩粒子 `P_crypto_visor_ui`；背上的无人机模型隐藏（bodygroup `drone`） | CD:1762、1903-1916 |
| Neurolink | 服务端每帧：球形范围 + 视线 + 夹角 → `SonarStart`（敌人高亮）+ 敌方玩家加状态效果 `camera_detected`（他自己 HUD 上显示"被无人机看到"） | CD:2773-3025 |
| 被扫到的提示音 | 队友各自听到敌人位置上的 ping，同一个人 10 s 内不重复 | CD:2928-2940、3073-3083 |
| 召回 | 播 `drone_recall` 动画（期间状态效果 `crypto_camera_is_recalling`）→ 销毁 | CD:1076-1127 |
| 被打 | 伤害回调：友军伤害清零、电弧星非爆炸伤害 ×0.25；护盾受击粒子 0.3 s | CD:2100-2160 |
| 被毁 | 爆炸粒子 + 音效；战术弹药清零（进冷却） | CD:2162-2193 |
| 小地图图标 | 挂一个空模型 `prop_script`，只对本队显示 | CD:1275-1290 |
| 用东西 | 从无人机朝前 300 u 射线：门 / 补给箱 / 空投 / 死亡箱 / 重生信标 | CD:921-1036 |

客户端 / 服务端：实体、移动、Neurolink、召回都在服务端；客户端负责视角 HUD、过场、越界提示（CD:2463 起）。

## 2. 流程

```
战术键按下（弹夹满 30）
   │ TossPrep：武器加 mod crypto_drone_access，开线程盯着按键
   ▼
出手（toss_time 0.7）→ CryptoDrone_ReleaseCamera
   │ 投掷物 400 u/s 直飞，无人机挂在上面
   │ ProjectileMovementThink：
   │   出手 0.29 s 时还按着键 → 立刻停住（"长按放近处"）
   │   松开了（点按）→ 最多飞 2 s；或前方 0.25 s 内要撞墙（且准星点不在 670 u 内）→ 减速后停
   │   碰到东西 → CameraImpact：下一帧摆正朝向，解除挂接
   ▼
1.25 s 后（Crypto_FlyingCameraThink）：玩家加 crypto_has_camera，武器加 mod crypto_has_camera
   │ 如果此时还带 crypto_drone_access（= 一直按着）→ 自动进入无人机视角
   ▼
┌──────── 无人机待机（在场） ────────┐
│ Neurolink 每帧扫描                   │◄──── 出视角（再按战术键 / 被迫）
│ 每 0.5 s 查超距（> 9496 u）→ 召回    │
│ 再按战术键 → SwapToCameraView_Thread ─┼──► 无人机视角：飞、用东西、EMP、自动换弹
└───────────────────────────────────────┘
   │ 角色键 → 召回（播动画 → 销毁 → 回到"没有无人机"，战术立即可再扔）
   │ 被打掉 → 爆炸，战术弹药清零（冷却 30 s）
```

- **触发条件**（`OnWeaponAttemptOffhandSwitch`，CD:343-363）：不在无人机视角里、不在召回中、没有 `script_helper`（出视角后 0.25 s 防误入）、`PlayerCanUseCamera`（不在翻越 / 上下文动作 / 相位 / 倒地，也不在拿 Mirage 分身投射器，CD:2654-2688）。
- **无人机在场时再按战术键**：不扔新的，而是进入视角（CD:384-395、432-442）。
- **出视角**：进入后等你松开战术键，再按一次就出（`Crypto_TryAddExitViewCommand`，CD:1652-1660）。
- **打断**：
  - `SwapToCameraView_Thread` 的结束信号：玩家死亡 / 销毁、开始相位、开始倒地、跳伞（CD:1665-1669），无人机被毁。
  - 被打时：给战术键设 1.4 s 不能再用（`CRYPTO_DRONE_DAMAGED_REENTER_DEBOUNCE`，CD:95、726），并通知客户端 `ServerCallback_ShouldExitDrone`——但这个客户端函数在本地是**空的**（CD:637-643），所以**本地版本被打不会被踢出视角**（SDK 改动或缺失，5 节实测）。
- **召回**：角色键 `+scriptCommand5`（CD:236、622-635）。EMP 中、召回中、没有无人机时不响应（CD:647-668）。
- **结束和冷却**：`ammo_instant`，弹夹 30 / 每秒 1 = 30 s（CD.txt:104-112）。扔出就扣光（`OnWeaponToss` 返回 -1，CD:380）。召回不清弹药；被毁清零（CD:2180）。
- **升级**：
  - `upgrade_core_tac_cooldown_reduction`：弹夹 ×0.75（22.5 s，CD.txt mods）。
  - `PAS_PAS_UPGRADE_ONE`：Neurolink 范围 ×1.25（CD:3594-3605；注释说按玩家分开存，是社区修的 bug）。
  - 出视角加速 0.15、5 s（`CryptoDrone_TryExitCameraSpeedBoost`，CD:2050-2087）：本地没人调用 `CryptoDrone_TrySetAllowExitSpeedBoost`（grep 只有定义），**推断**是未接上的天赋。

## 3. 代码

### 3.1 入口

| 函数 | 行 | 做什么 |
|---|---|---|
| `MpAbilityCryptoDrone_Init` | CD:183-264 | playlist：`crypto_neurolink_range`（默认 1181.1）、`crypto_drone_health`（默认 **50**，`CRYPTO_DRONE_HEALTH_PROJECTILE`，不是 60）；状态效果回调；角色键 = 召回 |
| `OnWeaponTossPrep_ability_crypto_drone` | CD:459-474 | 加 `crypto_drone_access`，开 `CryptoDrone_WeaponInputThink`（松键就去掉这个 mod，CD:886-907） |
| `OnWeaponToss_ability_crypto_drone` | CD:365-397 | 没有无人机 → `CryptoDrone_ReleaseCamera`；有 → 不扣弹 |
| `OnWeaponTossReleaseAnimEvent_…` | CD:425-457 | 有无人机且不在视角 → `SwapToCameraView_Thread` |

### 3.2 核心逻辑

#### 3.2.1 扔出和停下（`CryptoDrone_ProjectileMovementThink`，CD:1439-1512；`Crypto_FlyingCameraThink`，CD:1363-1437）

```
出手时：pointInRange = 从眼睛沿视线 hull 扫 670 u 能碰到东西（CD:1408-1409）
每帧：
  t > 0.29 s 时检查一次：还按着战术键 → 速度 = 0，停在原地，线程挂起
  前看：从无人机中心沿 速度×0.25 s 扫 hull（±14 u，忽略所有玩家）
    碰到 且 !pointInRange → 速度 ×0.15，等 0.25 s，结束
  t ≥ 2 s → 速度 ×0.25，等 0.5 s，结束
结束时 Crypto_TryDestroyDroneProjectile：解除挂接，PutPlayerVehicleInSafeSpot（向下 20 u 探水面 / 地面，CD:1149-1186），删投掷物，速度清零
```
撞到东西（`CryptoDrone_CameraImpact_Thread`，CD:793-859）：等一帧（R5DEV-335323 的防御修复），朝向 = 碰撞面法线（法线太竖时改用扔出时的 yaw），然后同上。

**推断的手感**：点按 → 无人机向前飞约 400·2 + 400·0.25·0.5 ≈ 850 u（如果中途没撞墙）；长按 → 停在出手点前约 0.29·400 ≈ 115 u，1.25 s 后直接进视角。

#### 3.2.2 无人机实体（`CryptoDrone_CreateFlyingCameraVehicle`，CD:1210-1329）

要点（给 HSD 的"可操控载具"做模板）：
- 实体 `player_vehicle`，模型 `crypto_drone.rmdl`，`SOLID_BBOX`，碰撞组 `BLOCK_WEAPONS`（挡子弹不挡人）。
- 血量 50（playlist），能被近战，能被 AI 当成目标（优先级 5，`EnableAttackableByAI( 5, 0, … )`）。
- 能触发触发器（被 Leviathan 踩会死，CD:1303）；能被烧，不受毒气。
- 登记：声呐可扫到、`AddEMPDestroyDevice`（敌方 EMP 会直接溶解它，CD:1308）。
- 启动 `NeurolinkThink` 和"范围内敌方队伍数"线程（1 s 一次，CD:3027-3045）。
- 本队高亮 `crypto_camera_friendly`；小地图图标只对本队。

#### 3.2.3 视角切换（`SwapToCameraView_Thread` CD:1663-1901、`TransitionOutOfCamera` CD:1949-2047）

进：
```
解除投掷物挂接（如果还在飞）
记住玩家角度
加状态效果 camera_view；玩家进入"在载具里"的上下文动作；立刻隐藏主 HUD
无人机.VehicleSetDriver( 玩家 )；设无人机眼角
无人机和它的粒子改成"敌我都可见"（之前主人自己也能看）
换推进音效（1P 只给主人，3P 给别人）
注册按键：IN_ATTACK / IN_OFFHAND4 → EMP；IN_USE → 用东西；IN_USE_LONG → 重生信标
关掉第三人称肩视角（如果开着，出来时恢复）
循环（0.4 s 一次）：自动换弹，一次一把，先换最后用的那把，按该武器真实换弹时间算完成
           拿着手雷 / 道具时切回主武器
```
出：
```
注销按键
在地上且没相位 → 0.2 s 白色淡出
无人机改回"所有人可见"，播 drone_active_twitch；VehicleRemoveDriver
0.1 s 淡入；视角 0.3 s 插值回身体；恢复预测；去掉 camera_view、恢复 HUD
加 0.25 s script_helper（防止立刻再进）
```

#### 3.2.4 召回 / 超距（CD:1061-1127、1427-1436、2463 起）

- 召回：`drone_recall` 动画；状态效果 `crypto_camera_is_recalling` 时长 = `drone_EMP` 动画长度 / 3（注释说"不知道为什么要 /3"，CD:1086-1090）；播完原地放结束粒子，销毁无人机。**不扣弹药**。
- 动画占用中（EMP 或召回）不能再召回（`DroneHasActiveAnimation`，CD:3157-3168）。
- 超距：每 0.5 s 查一次，`|玩家 − 无人机| > 7913 × 1.2 = 9495.6 u`（≈241 m）或高度超上限 → 自动召回（CD:1430-1434）。
- 客户端提示：> 5906 u（150 m）开屏幕扭曲粒子；> 7913 u（201 m）粒子强度变满（CD:2463 起）。**注意**：`MAX_FLIGHT_RANGE` 注释说要和引擎 ConVar `crypto_cam_max_distance` 一致，引擎可能在 201 m 处直接限制飞行；脚本的 ×1.2 是兜底。

#### 3.2.5 Neurolink（`NeurolinkThink`，CD:2773-3025）

**SDK 改写**（CD:2854-2856 注释：S21 用原生 `VehicleGetPlayersInViewArray`，S3 没有，社区自己写）：
```
每帧：
  候选 = 球形 R 内所有玩家 + NPC（不含主人）       R = 1181.1 u（30 m），升级 ×1.25
  去掉：视线不通（无人机→目标中心，TRACE_MASK_VISIBLE）、
        水平夹角 dot2D(无人机前方, 方向) < cos120° = −0.5、不同 realm
  新进入的：SonarStart（高亮）；玩家 / NPC 播 ping（同一个 10 s 一次）；敌方玩家加 camera_detected
  已不在候选里的：linger 时间（playlist crypto_drone_scan_linger，默认 0）过了 → SonarEnd
```
- 夹角用的是 `NEUROLINK_VIEW_MINDOT_BUFFED = 120°`（CD:105），未升级的 80° 常量没用到 → 本地版本视野是 **240° 水平扇形**，比正版**推断**的 160° 宽。
- 注意它**不分敌我**（候选里有队友），只有 `camera_detected` 状态效果判了 `IsPlayer`；`SonarStart` 第三个参数是主人的队伍，**推断**引擎只给敌人上高亮。

#### 3.2.6 设备登记表（CD:2717-2769）

三张脚本管理的实体表：`empDamage`（受 EMP 时扣 100 血）、`empDestroy`（受 EMP 时溶解或满伤）、`empDisable`（受 EMP 时调回调）。别的技能建实体时自己登记。EMP 怎么用这张表见 [crypto-drone-emp](../crypto-drone-emp/SYSTEM.md)。完整列表见 `_shared/D-DEVICE-REGISTRY.md`。

### 3.3 客户端表现

- 切换过场（CD:520-609）：动画事件 `screen_transition` 触发，1.2 s，长版 / 快版两套（已有无人机时用快版）。
- 视角 HUD（CD:2263-2355）：`empFrac`、`recallFrac`、`beaconFrac`、`playerHealthFrac`（无人机血）、玩家位置朝向；EMP 充能比例和回充速度；提示文字区分手柄。
- 小地图：缩 0.7、染绿 `< .21, .79, .34 >`、偏移、隐藏指南针，加一个"玩家身体"图标（CD:2327-2334）。
- 越界提示（CD:2463 起）：见 3.2.4。还显示准星离无人机的距离 `crossDist`、前方 300 u 可交互物体的提示文字。
- 3P：玩家头上的面罩粒子；无人机身上一束只有主人看得到的视线光束 `P_drone_scan_SML_no_streaks`（主人进视角后隐藏，CD:2787-2792、2844-2850）。

### 3.4 依赖的公共代码

- 引擎：`player_vehicle`、`VEHICLE_FLYING_CAMERA`、`VehicleSetDriver / RemoveDriver`、`Vehicle_SetEyeAngles`、`PutPlayerVehicleInSafeSpot`、`vortex_sphere`。
- 脚本：`ThrowDeployable`、`SonarStart / SonarEnd`（`sh_sonar.gnut`）、`ScreenFade`、`AddCinematicFlag`、`AddButtonPressedPlayerInputCallback`、`StatusEffect_*`。
- 状态效果：`camera_view`、`crypto_has_camera`、`crypto_camera_is_recalling`、`crypto_camera_is_emp`、`camera_detected`、`script_helper`（`status_effect_types.txt`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 扔出速度 | 400 | u/s | CD:104、400-405 | | |
| 投掷物重力 | ×0.001 | — | CD.txt:42 | 几乎直线 | |
| 继承玩家速度 | 0.3 | — | CD.txt:46 | | |
| 投掷物 hull | ±10 | u | CD.txt:44-45 | | |
| 长按判定 | 0.29 | s | CD:1477 | 出手后还按着就原地停 | |
| 自由飞行时间 | 2.0 | s | CD:1445 | | |
| 到时减速 | ×0.25，再飞 0.5 s | — | CD:1443-1444 | | |
| 要撞墙减速 | ×0.15，再飞 0.25 s | — | CD:1441-1442 | 前看 0.25 s | |
| 准星近点判定 | 670 | u | CD:107、1408 | 点在 670 内就不做"撞墙减速" | |
| 无人机 hull（检测） | ±14，高 0–14 | u | CD:110-111 | | |
| 进入视角延迟 | 1.25 | s | CD:1418 | 出手到可进视角 | |
| 过场时长 | 1.2 | s | CD:586 | | |
| 无人机血量 | 50 | HP | CD:106、205（playlist `crypto_drone_health`） | `CRYPTO_DRONE_HEALTH 60` 没用 | |
| 升级血量 | 100 | HP | CD:209（`crypto_drone_upgraded_health`） | 注释"not called yet" | |
| AI 攻击优先级 | 5 | — | CD:1271 | | |
| 电弧星对无人机 | 非爆炸部分 ×0.25 | — | CD:2117-2122 | | |
| 护盾球 | 半径 16、高 16 | u | CD:1574-1575 | 挡子弹 | |
| 飞行最远 | 7913（≈201 m） | u | CD:92 | 引擎 ConVar `crypto_cam_max_distance` | |
| 警告距离 | 5906（150 m） | u | CD:93 | | |
| 自动召回距离 | 7913 × 1.2 = 9495.6 | u | CD:1430 | 每 0.5 s 查 | |
| 高度上限 | 100000（地图可改） | u | CD:173、3618 | | |
| 召回状态时长 | `drone_EMP` 动画长 / 3 | s | CD:1086-1090 | 未知，要实测 | |
| 被打后不能再进 | 1.4 | s | CD:95、726 | | |
| 出视角防误入 | 0.25 | s | CD:2035 | | |
| 出视角淡出 / 淡入 | 0.2 / 0.1 | s | CD:1961-1962、2022 | | |
| 视角插值回身体 | 0.3 | s | CD:2025 | | |
| 自动换弹检查 | 0.4 | s | CD:1874 | 关掉时 1.0 s | |
| 用东西射线 | 300 | u | CD:927 | | |
| Neurolink 范围 | 1181.1（30 m） | u | CD:86、204 | playlist `crypto_neurolink_range` | |
| Neurolink 升级 | ×1.25 | — | CD:88、3599 | | |
| Neurolink 夹角 | 120°（水平半角） | ° | CD:105、2856 | 本地用"增强"值；80° 未用 | |
| ping 防重 | 10 | s | CD:2930 | | |
| scan linger | 0 | s | CD:1198 | 离开视野立即取消标记 | |
| 范围内敌方队伍数 | 7913 半径，1 s 一次 | u / s | CD:1920、3043 | 进视角 HUD 显示 | |
| 冷却 | 30（弹夹 30 / 1 每秒） | s | CD.txt:104-112 | | |
| 冷却升级 | ×0.75 | — | CD.txt mods | | |
| 出手 | pullout 0.25、toss 0.7（已有无人机：0.2 / 0.6） | s | CD.txt:88-90、mods | | |
| 出视角加速（未接） | +0.15、5 s | — | CD:89-90 | | |

## 5. 未解决和要实测的

| 问题 | 为什么不确定 | 怎么测 |
|---|---|---|
| 飞行速度、加速度、能不能穿过小缝 | 在引擎载具代码里；`CAMERA_FLIGHT_SPEED 450` 没被用 | 火力训练场进无人机视角，按住前进；AgentLink 每 0.05 s 记无人机位置（scriptname `crypto_camera`）。分别测水平、上升、下降、按住冲刺键（`IN_ZOOM` 在客户端被读成"飞行模式"，CD:2499，含义不明） |
| 201 m 是硬限制吗 | 引擎 ConVar | 一直往外飞，看停在哪里，还是飞到 241 m 被召回 |
| 被打会不会被踢出视角 | 客户端回调是空的（SDK 缺失） | 让训练场假人 / 第二客户端打 Crypto 本体 |
| Neurolink 视野 | 本地社区实现用 240°；正版是原生函数 | 无人机朝一个方向，假人放在 90°、130°、170° 方向，看是否高亮。和正版录像比 |
| Neurolink 标不标队友 | `SonarStart` 内部按队伍过滤是推断 | 同上，带一个友方 bot |
| 召回时长 | 动画长度 / 3 | 记 `crypto_camera_is_recalling` 状态效果持续时间 |
| 点按飞行距离 ≈ 850 u | 推断 | 空地点按，记最终位置 |

## 6. HSD 实现

**未实现。** HSD 没有载具 / 远程视角系统。

建议做法（只拿系统，不做侦察效果本身）：
- `RemoteDrone`：一个飞行实体 + "接管视角"开关。接管时：玩家身体冻结、输入转给无人机（复用 HSD 现有 `MovementInput` 结构，只读 forward / right / up / look）、相机挂到无人机上，HUD 换皮。出来时淡出淡入。详细接口见 `_shared/D-REMOTE-DRONE.md`。
- 飞行手感先用"最大速度 + 加速度"两个参数，等 5 节实测后填值。
- PvE 用途：远程侦察 + 远程触发（开门、启动机关、放 EMP），以及以后"操控炮台 / 操控伙伴"的统一接口。
- 开关：`hsd.tf2.x.remoteDrone`（PlayerPrefs）。
