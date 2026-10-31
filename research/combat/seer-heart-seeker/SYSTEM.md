# Seer 被动 Heart Seeker（心跳探测）· 系统记录

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`。主脚本 `vscripts/weapons/mp_ability_heartbeat_sensor.nut`（1679 行），武器设置 `weapons/mp_ability_heartbeat_sensor.txt`。已有引用：APEX-REPORT 2.4 对照表"Seer 被动"一行（50 m、心跳条、小地图锥）。

## 0. 概要

- **技能**：Seer / 被动 / Heart Seeker / `mp_ability_heartbeat_sensor`（`.txt` `hud_icon passive_seer`；被动 `PAS_PARIAH` `.nut:161`）。
- **一句话**：开镜（ADS）时，准星周围出现一个环形心跳雷达：视野内 50 m 以内的敌人按血量快慢"跳动"（血越少跳越快），准星对准时亮起；视线内更远的敌人也显示但不出声；小地图画一个探测锥。
- **分类**：可视化 ✔（主要价值：环形心跳 HUD、按血量变速的节拍、对准锁定提示、小地图锥）；系统 中（"开镜才生效的被动"+ 客户端目标管理）；好技能（效果）弱：PvE 只是"找敌人"。
- **全部在客户端。** 目标搜索、节拍、HUD、音效都在 `#if CLIENT`；服务端只发被动武器、切换开关、记统计。
- **可拆出的部件**：
  - 开镜触发的被动"武器"（offhand 跟着 ADS 激活）→ 3.1
  - 视野内目标表：每 0.1 s 刷新，新目标起一个节拍线程，消失的发信号结束 → 3.2.1 `ManageVictims_Thread`
  - 按血量缩放的节拍（双拍 0.28 s + 间隔 0.4–1.65 s）→ 3.2.2 `DoVictimHeartbeat_Thread`
  - "准星对准"判定：近处按战术命中、远处按屏幕距离 → 3.2.3 `UpdateDataForHeartseekerRadarWaveformRadial`
  - 环形 HUD 数据：每帧把 10 个目标的位置 / 上次心跳时间 / 锁定写进 RUI → 3.3 `CL_HeartSeekerRUIThread`
  - 小地图探测锥 + 按最近心跳变色 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 开镜才生效 | 被动发一个 offhand 武器（`OFFHAND_EQUIPMENT` 槽，`.nut:55`、`.nut:207`），`.txt` `offhand_activates_on_zoom 1`、`offhand_active_slot altHand`、`cooldown_type vortex_drain` | ADS 时引擎激活这个武器 → `OnWeaponActivate` → 延迟后 `ActivateHeartbeatSensor`；退出 ADS → `OnWeaponDeactivate` |
| 关 / 开 | `+scriptCommand5` → 服务端切换武器 mod `disabled`（`offhand_activates_on_zoom 0`） | `.nut:139`、`.nut:467-511`；`.txt` Mods `disabled` |
| 找目标 | 原生 `player.GetPlayersInViewInfoArray(…, watchRange, FOV, 10, …, 自然范围)` + 训练场假人 + 敌方分身（脚本补） | `.nut:1096-1136` |
| 视线 | 只对脚本补的目标做 `TraceLine(BLOCKLOS)`，`fraction >= 0.99` 记 `hasLOS` | `.nut:1225-1226`；原生返回的目标里 `hasLOS` 怎么算看不到 |
| 铁磁墙 | `FerroWall_BlockScan` 挡 | `.nut:1148` |
| 心跳节拍 | 每个目标一个客户端线程：两次"拍"间隔 0.28 s，周期按血量 0.4–1.65 s | `.nut:1239-1339` |
| 心跳声 | 只有"最佳目标"（夹角最小、在 50 m 内）出声 `Seer_Passive_Heartbeat_3p`，挂在目标身上（3D 定位） | `.nut:1167-1171`、`.nut:1305-1313`；设置项 `player_setting_enable_heartbeat_sounds` |
| 环形 HUD | 驾驶舱 RUI `ui/heartbeat_sensor_waveform_radial.rpak` | `.nut:666`；画法在 RUI 资源里，脚本只喂数据 |
| 激活波 | 1P 粒子 `P_heart_sensor_pulse_1p`（最近开过枪或 3.5 s 内开过时用无前奏版 `P_heart_sensor_on_1p`），CP1.x = 范围 | `.nut:957-1007` |
| 小地图锥 | `Minimap_SetVisiblityCone(true, 范围, minimap_seer_tac_cone, 颜色)`；有目标在范围内时颜色按最近心跳插值 | `.nut:986`、`.nut:1535-1547` |
| 别人看到 | 3P 眼睛发光 `p_heart_sensor_eye_foe`（敌我都用 foe 版）+ 3P 循环声 | `.nut:714-740` |
| 开镜近战移速 | 近战武器时加 extra mod `seer_heartbeat_sensor_active` | `.nut:513-562` |
| 语音 | 客户端线程按冷却报"附近有敌人 / 安全" | `.nut:745-955`，和 HUD 无关，本文不展开 |

## 2. 流程

```
有被动 PAS_PARIAH → 服务端给 offhand 武器（.nut:204-210）

ADS 开始
 ├─ PlayerZoomInCallback（客户端）：建 RUI（只建一次），起 CL_HeartSeekerRUIThread    (.nut:252-277, :662-674)
 │                    （服务端）：近战时加移速 mod
 └─ 引擎激活被动武器 → OnWeaponActivate（.nut:348-374）
      [playlist seer_heartbeat_sensor_unarmed_only] 只在空手 / 传家宝时生效
      DelayedActivateHeartbeatSensor_Thread：
          delay = 当前武器 raise_time × 0.5（有且不是近战）否则 0.4 s
          期间退出 ADS → 取消
      → ActivateHeartbeatSensor（.nut:677-742）
          本地：RUI enabled；激活波 + 小地图锥；起 ManageVictims_Thread、语音线程
          别人：眼睛发光 + 3P 声

ManageVictims_Thread 每 0.1 s：刷新目标表（3.2.1）；新目标 → DoVictimHeartbeat_Thread（3.2.2）
CL_HeartSeekerRUIThread 每帧：把表写进 RUI（3.3）

ADS 结束 → PlayerZoomOutCallback：EndHeartbeatSensorUI（RUI endTime）；服务端去移速 mod
        → OnWeaponDeactivate → DeactivateHeartbeatSensor：RUI disabled；EndHeartbeatSensorVictimManager；
          上报本次听到的心跳数（服务端按 激活时长 / 0.4 封顶 .nut:592-613）
丢被动 → 收回武器，DestroyHeartbeatSensor
被沉默（silenced）→ 不能切换；HUD 显示沉默（.nut:476、:1494-1495）
```

骑 Rampart 机枪时 ADS 不会激活 offhand，单独处理（`.nut:265-272`、`.nut:310-333`）。

## 3. 代码

### 3.1 入口

- `PassiveHeartbeatSensor_Init`（`.nut:119-164`）：范围 = 50 / 0.0254 = 1968.5 u（`.nut:126`）；注册信号、`+scriptCommand5` 切换、两个服务端远程函数；挂被动变化和 ADS 进出回调。语音用的距离：`commsResetRange = (1968.5 + 393.7) × 0.75`、`commsEnemyRemovalRange = … × 1.35`（`.nut:147-149`，`SONIC_BLAST_RANGE_EXTENSION = 10 m` `mp_ability_sonic_blast.nut:38`）。
- `HeartbeatSensor_OnPassiveChanged`（`.nut:169-235`）：得到 / 失去被动时给 / 收武器、清特效。
- `DelayedActivateHeartbeatSensor_Thread`（`.nut:376-415`）：激活延迟见第 2 节。

### 3.2 核心逻辑

#### 3.2.1 目标表 `ManageVictims_Thread`（`.nut:1058-1203`）+ `GeneratePlayersInViewInfo`（`.nut:1205-1229`）

```
每 0.1 s：
   fov = 当前视野 FOV（开镜后的）
   watchRange = GraphCapped(fov, 55, 8.01, 5500, 20000)       // 倍镜越大看越远；55° 及以上 5500 u，10 倍镜 20000 u
   list = 原生 GetPlayersInViewInfoArray(true, true, watchRange, fov, 10, false, 自然范围)
   [火力训练场] 补假人；补敌方分身（普通 + 操控）：
       dot = Dot(normalize(目标中心 − 眼睛), 视线)；dot < cos(fov) 或 距离 > watchRange → 跳过
       hasLOS = TraceLine(眼睛 → 中心, BLOCKLOS).fraction >= 0.99
   对每个目标：
       铁磁墙挡 → 跳过
       记 viewportInfo[目标] = 本次数据
       新目标 → HeartseekerAddWatchTarget → thread DoVictimHeartbeat_Thread
       dot 最大且在自然范围内 → 最佳目标（出声的那个）
   上次在表里、这次不在 → Signal StopWatchingHeartbeatSensorVictim，移出
```

注意 `deg_cos(viewportFOV)`（`.nut:1099`）把整个 FOV 当半角用（推断：判定比画面宽）。

两种距离：
- **自然范围（50 m = 1968.5 u）**：在这里面 = "在战术范围内"（`IsVicitmInTacRange` `.nut:1369-1375`），出心跳声、走"战术会不会命中"的锁定判定，计入统计。不要求视线（推断：原生按距离给，穿墙；APEX-REPORT 写"穿墙 是"）。
- **观察范围（5500–20000 u）**：自然范围外、视线内（`hasLOS`）的目标也显示，但不出声、锁定按屏幕距离判（3.2.3）。没视线的就从 HUD 表里删掉（`.nut:1331-1334`）。

#### 3.2.2 节拍 `DoVictimHeartbeat_Thread`（`.nut:1239-1339`）

```
wait random(0.1, 0.4125)                     // 0.4×0.25 到 1.65×0.25，错开多个目标同时开始
循环：
   hp% = 倒地中 ? 25 / maxHP : HP / maxHP
   [分身] 用分身主人的血量比例（避免露馅）；主人血量异常时当满血
   period = Graph(hp%, 0, 1, 0.4, 1.65)       // 血越少越快：空血 0.4 s，满血 1.65 s（Graph 不夹，超过 1 会更慢）
   若 在自然范围内：
       [最佳目标] 计数 +1，播心跳声（设置允许时）
       写 HUD（第一拍）；wait 0.28；写 HUD（第二拍）
   否则若 有视线：
       写 HUD（不出声）；wait 0.28；写 HUD
   否则：从 HUD 表删除
   wait period − 0.28
```

节拍 = "咚-咚"两拍间隔 0.28 s（`HEARTBEAT_SOUND_BAR_WAIT_TIME` `.nut:41`），整周期 0.4–1.65 s。`Graph`（不夹）意味着血量超上限（有护甲加成时？推断）周期会超过 1.65 s。

#### 3.2.3 "对准"判定 `UpdateDataForHeartseekerRadarWaveformRadial`（`.nut:1377-1430`）

```
若 在自然范围内：                                       // 判断 Seer 战术现在放会不会打中
   start = 胸口 + 视线 × 20
   end   = start + 视线 × 战术射程                       // 战术射程 = 自然范围 + 10 m = 2362 u（升级时 = 75 m）
   isLocked = ShouldBlastHitVictim(start, end, …)       // 目标眼睛到线段距离 <= 200 u 且在前方（mp_ability_sonic_blast.nut:827-852）
否则：                                                  // 远处管状判定太细，改成屏幕距离
   offset = HUD 中心圈尺寸（按瞄具，见下）
   distOnScreen = sqrt(dx² + dy²)                       // 目标中心到屏幕中心的像素距离
   isLocked = distOnScreen <= 屏幕宽 × offset / 1920 × 0.75
写 BarData{ lastGameTimeBeat = now, inTacRange, isLocked }
```

HUD 中心圈尺寸 `GetHeartbeatSensorUISizeForWeapon`（`.nut:1555-1638`）：无瞄具 = 武器 `.txt` 的 `heartbeat_sensor_size`（如 `mp_weapon_3030.txt:14` = 75）；大部分瞄具 84；可变倍狙镜 110；× (16/9 ÷ 屏幕宽高比)；手枪类（P2020、Wingman、Mozambique）无瞄具 ×0.9、有瞄具 ×0.75。

### 3.3 客户端表现：环形 HUD 怎么画

`CL_HeartSeekerRUIThread`（`.nut:1437-1553`）是 HUD 的全部数据来源；**波形的形状、环的半径、动画曲线在 RUI 资源 `ui/heartbeat_sensor_waveform_radial.rpak` 里，脚本看不到**。脚本喂给 RUI 的：

| RUI 参数 | 值 | 来源 |
|---|---|---|
| `startTime` / `endTime` | 建立 / 销毁时刻 | `.nut:667`、`.nut:1454` |
| `alternateMode` | true | `.nut:668` |
| `heartbeatSensorEnabled` | 开 / 关 | `.nut:654-658`、`.nut:699`、`.nut:1021` |
| `heartbeatSensorADSOverride` | 从战术触发时强制显示（战术不开镜，adsFrac 为 0） | `.nut:701-705` |
| `weaponFireDelay` | 1 / fire_rate + 0.3 | `.nut:1470-1481`（推断：开枪后 HUD 暂时淡出） |
| `offset` | 中心圈尺寸（见 3.2.3） | `.nut:1482` |
| `heartbeatSensorNaturalRange` | 1968.5 u | `.nut:1483` |
| `screenSize` | 屏幕宽高 | `.nut:1484` |
| `lastFireTime` | 跟踪武器最后开火时间 | `.nut:1486` |
| `bleedoutEndTime` / `reviveEndTime` | 跟踪网络变量 | `.nut:1487-1488` |
| `isSilenced` | 每帧 | `.nut:1494-1495` |
| `target1..10` | 目标世界坐标（中心） | `.nut:1505` |
| `target{i}GameTimeBeat` | 最近一拍的时间；没有目标 = −1 | `.nut:1506`、`.nut:1530` |
| `target{i}Locked` | 是否对准 | `.nut:1507` |

推断 RUI 的画法（要看资源确认）：把每个目标的世界坐标投到屏幕，取相对准星的方向角，在环上该角度处画一个波形；`now − GameTimeBeat` 驱动波形的跳起和衰减（每拍写一次，所以两拍 0.28 s 产生"咚-咚"）；`Locked` 时高亮。`BarData.angle` 字段（`.nut:81`）定义了但没赋值。

小地图锥（`.nut:1535-1547`）：有目标在自然范围内时，颜色 = `GraphCappedVector(最近一拍过去的时间, 0, 1.52 − 0.28, 范围内色, 默认色)`——刚跳完是"范围内"色，1.24 s 内渐回默认色；没目标时回默认色。

### 3.4 依赖的公共代码

- 原生 `GetPlayersInViewInfoArray`（视野内玩家，带 dot / 距离 / 视线）。
- `ShouldBlastHitVictim`、`GetSonicBlastRange`、`SONIC_BLAST_*`（`vscripts/weapons/mp_ability_sonic_blast.nut:36-38`、`:827`、`:1101`）。
- `FerroWall_BlockScan`、`Minimap_SetVisiblityCone / Color`、`GetScreenSpaceData`、`CreateCockpitRui`。
- 状态效果 `silenced`（Revenant 沉默会关掉它，见 `revenant-silence/SYSTEM.md`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| 自然范围 | 50 m = 1968.5 u | m / u | `.nut:27`；playlist `seer_passive_range`（`.nut:1643`） | 出声、计入"范围内"、战术锁定判定 | |
| 升级范围 | 75 m = 2952.8 u | m / u | `.nut:29`；playlist `seer_passive_extended_range_upgraded`；`PAS_PAS_UPGRADE_ONE` | | |
| 观察范围 | 5500 → 20000 | u | `.nut:44-45`、`.nut:1086` | 视线内的远处目标也显示 | |
| 观察范围的 FOV 区间 | 55 → 8.01 | ° | `.nut:42-43` | 腰射 / 1 倍是 5500，10 倍镜 20000 | |
| 最多目标 | 10 | 个 | `.nut:56` | HUD 槽位 | |
| 刷新目标表 | 0.1 | s | `.nut:1201` | | |
| 激活延迟 | raise_time × 0.5，否则 0.4 | s | `.nut:31`、`.nut:382-395` | | |
| 节拍周期 | 0.4（空血）→ 1.65（满血） | s | `.nut:32-33`、`.nut:1292` | | 区间越大，血量越好分辨 |
| 双拍间隔 | 0.28 | s | `.nut:41` | | |
| 起始随机延迟 | 0.1 → 0.4125 | s | `.nut:34-35`、`.nut:1267` | 错开节拍 | |
| 倒地血量当作 | 25 | HP | `.nut:1272` | 倒地的人按 25 HP 算节拍 | |
| 战术锁定：起点前移 | 20 | u | `mp_ability_sonic_blast.nut:37` | | |
| 战术锁定：射程 | 自然范围 + 10 m = 2362 u（升级 = 75 m） | u | `mp_ability_sonic_blast.nut:38`、`:1101-1107` | | |
| 战术锁定：管半径 | 200 | u | `mp_ability_sonic_blast.nut:36`；playlist `seer_tac_radius` | | |
| 远处锁定半径 | 屏幕宽 × offset / 1920 × 0.75 | px | `.nut:1404-1405` | | |
| HUD 中心圈 offset | 无瞄具 = 武器 `heartbeat_sensor_size`；瞄具 84；可变狙镜 110；手枪 ×0.9 / ×0.75 | RUI px | `.nut:1557-1635` | | |
| weaponFireDelay | 1 / fire_rate + 0.3 | s | `.nut:1470-1479` | | |
| 小地图锥变色时间 | 1.52 − 0.28 = 1.24 | s | `.nut:1538` | | |
| 激活波防抖 | 开过枪 2.0 s 内 / 上次激活 3.5 s 内 → 无前奏 | s | `.nut:46-47`、`.nut:975-978` | | |
| 语音冷却 | 35（全局 3.5，清除 15，报告延迟 1.65，监听 2.0，队友显示 6.0） | s | `.nut:48-54` | | |
| `.txt` 切换动作 | holster / lower 0.9，deploy / raise 0.5 | s | `.txt` | | |
| `.txt` fire_rate | 20 | — | `.txt` | 无实际开火（`OnWeaponPrimaryAttack` 返回 0 `.nut:448-451`） | |
| playlist 只空手 | false | 开关 | `seer_heartbeat_sensor_unarmed_only`（`.nut:369`） | | |
| playlist 只武器 | false | 开关 | `seer_heartbeat_sensor_weapons_only`（`.nut:245`） | 去掉 ADS 近战 mod | |

已知不一致：`GetHeartbeatSensor_Range_Sqr`（`.nut:1661-1679`）没升级时返回 Init 时按常量算好的平方，不读 playlist `seer_passive_range`；`GetHeartbeatSensorRange` 读。playlist 改了范围时两者会不一致（推断：原代码小问题）。

## 5. 未解决和要实测的

1. **RUI 波形画法**（环半径、波形形状、跳起 / 衰减曲线、锁定样式）：脚本看不到。测法：游戏里开镜对假人截图 / 录屏；或解包 `ui/heartbeat_sensor_waveform_radial.rpak` 看 RUI 定义。HSD 做 HUD 时最需要这一项。
2. **原生 `GetPlayersInViewInfoArray` 的过滤**：穿不穿墙、角度怎么算、`hasLOS` 怎么填。测法：墙后 30 m 的假人，开镜看 HUD 有没有它、有没有声音。
3. **满血以上（加护甲）节拍会不会更慢**：`Graph` 不夹。测法：给假人不同护甲 / 血量，录 HUD 节拍间隔。
4. 本模块全在客户端，SDK 改服务端的风险小；但 `.nut:157` 注释"Register remotes on both sides; client early-return was a regression"说明这里也被改过。

## 6. HSD 实现

**未实现。** HSD Combat 没有感应类 HUD（只读查 `CombatHud.cs`：扫描框、地图透视小地图）。

建议做法：
- 目标表：每 0.1 s 取视野内敌人（`CombatSim.Enemies`），近处（自然范围）不要求视线，远处要求射线不挡。
- 节拍：每个目标记 `nextBeat`，周期 `lerp(0.4, 1.65, hp%)`，每次跳写 `lastBeat = now`，0.28 s 后再写一次。
- HUD：在 `CombatHud` 里以准星为圆心画环，目标方向角 = `atan2(屏幕 dy, dx)`，在该角度画一个高度 = `f(now − lastBeat)` 的尖峰（衰减曲线待第 5 节第 1 项测出）；对准时变色。
- 开关建议：`hsd.combat.heartSeeker.*`（范围、周期区间、只在开镜时）。
