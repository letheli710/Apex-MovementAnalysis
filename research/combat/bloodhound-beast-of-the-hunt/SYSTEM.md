# Bloodhound 大招 Beast of the Hunt（狩猎野兽）· 系统记录

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`。主脚本 `vscripts/weapons/mp_ability_hunt_mode.nut`（782 行），武器设置 `weapons/mp_ability_hunt_mode.txt`。已有引用：`TF2-Research/expansion/apex/APEX-REPORT.md` 2.4 对照表"Bloodhound 大招"一行（30 s、威胁视觉、加速 0.15）。本文补全流程、代码和参数，并**更正**两点（见第 2 节"和 APEX-REPORT 的差别"）。

## 0. 概要

- **技能**：Bloodhound / 大招 / Beast of the Hunt / `mp_ability_hunt_mode`（`.txt:3` `#WPN_HUNT_MODE`，`hud_icon ultimate_bloodhound` `.txt:8`）。
- **一句话**：放出后 30 s（升级 40 s）：世界去饱和 + 专用调色、敌人被"威胁视觉"标红、自己加速 15%、战术冷却加快；击倒 / 击杀时战术充满、放一只乌鸦，带升级时延长时间、回血。
- **分类**：可视化 ✔（全屏去饱和 + 调色 + 敌人高亮，是 HSD"狂暴 / 猎杀模式"的现成样板）、系统 ✔（跟随玩家的扫描触发器、按剩余时间缩放的击杀延长）；好技能（效果）弱：加速和透视都很简单。
- **可拆出的部件**：
  - 一组状态效果当"模式"（同一时长、各自淡出）→ 3.2.1 `HuntMode_Start` / `_shared/E-STATUS-EFFECT.md`
  - 全屏去饱和 + 调色，权重跟状态效果严重度走 → 3.3 `HuntMode_UpdatePlayerScreenColorCorrection` / `_shared/E-SCREEN-COLOR-CORRECTION.md`
  - 跟着玩家走的圆柱触发器 + 进出回调 + 每个目标一个视线判断线程 → 3.2.2 `HuntMode_ScanTargets` / `TriggerTrackOwner` / `EntitySonarThink`
  - 击杀延长：剩得越少加得越多 → 3.2.3 `CalculateTimeExtension`
  - 声纳高亮（敌人轮廓 + 胸口锁定框）→ `_shared/E-SONAR-HIGHLIGHT.md`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 敌人标红（主效果） | 状态效果 `threat_vision`（无限期，严重度 1.0） | `.nut:275`。引擎原生按这个状态效果画敌人，脚本里没有画法（推断：和 Caustic 毒气视觉 `CAUSTIC_THREAT` 同一套，`highlight_context_drawfunc.txt:16`）。烟雾默认挡威胁视觉（`vscripts/superbar/smokescreen.nut:254-256` playlist `smoke_blocks_threat_vision`） |
| 加速 15% | 状态效果 `speed_boost`（无限期，严重度 0.15） | `.nut:276`。结束时脚本手动停 |
| 计时 | 状态效果 `hunt_mode`（30 s，淡出 = 30 s）+ 服务端表 `huntModeEndTimes[player]` | `.nut:279`、`.nut:283-286`。真正决定结束的是服务端表（`.nut:574`），状态效果给客户端 HUD |
| 画面开关 / 强度 | 状态效果 `hunt_mode_visuals`（30 s，淡出 5 s） | `.nut:280`。客户端开关回调 + 每帧读严重度当调色权重 |
| 世界去饱和 | `GfxDesaturateOn/Off()`（原生） | `.nut:714`、`.nut:728`。高亮和标了 `PARTICLE_SCRIPT_FLAG_NO_DESATURATE` 的粒子不去色 |
| 调色 | `ColorCorrection_Register("materials/correction/ability_hunt_mode.raw_hdr")`，独占 | `.nut:47`、`.nut:647-686` |
| 1P 屏幕粒子 | `P_hunt_screen`，驾驶舱上，不受去色影响 | `.nut:734-759` |
| 3P 身体粒子 | `P_hunt_body` 挂 `HEADSHOT`，敌我可见（第三人称肩视角时自己也可见） | `.nut:580-642` |
| 键盘灯效 | `Chroma_StartHuntMode / EndHuntMode` | `.nut:715`、`.nut:729` |
| 结束前 2 s 换声音 | 服务端线程比对 `huntModeEndTimes` | `.nut:614-640` |
| 跟随玩家的扫描（**默认关**） | `trigger_cylinder` + 每帧 `SetOrigin(owner)` + 进出回调 → 视线判断 → `SonarStart/SonarEnd` | `.nut:293-296`、`.nut:319-464`。只有 playlist `bloodhound_ult_sonar_range > 0` 才开，默认 0（`.nut:36`），本地补丁 `playlists_r5_patch.txt` 没设 |
| 击杀奖励 | 击杀 / 倒地回调：战术充满、白乌鸦、升级时延长 / 回血 | `.nut:91-222` |
| 动作期间限制 | `LockWeaponsAndMelee`、`DisableMantle`、`Embark_Disallow`；2.1 s 禁跑墙 / 二段跳 | `.nut:226-243` |

**服务端 / 客户端**：状态效果是共享的（`HuntMode_Start` 不在 `#if SERVER` 里，`.nut:272-280`，推断：客户端预测时也加一份）；计时表、触发器、击杀奖励、身体粒子在服务端；去色、调色、屏幕粒子在客户端。

## 2. 流程

```
按键（150/150）
 └─ OnWeaponTossPrep（.nut:226-243）
      语音；禁上载具、禁攀爬、锁武器和近战；2.1 s 禁跑墙和二段跳
 └─ toss 动作 1.2 s → OnWeaponTossReleaseAnimEvent = OnWeaponPrimaryAttack_hunt_mode（.txt:17, :22；.nut:246-257）
      └─ HuntMode_Start（.nut:272-303）
           加 threat_vision(1.0, 无限) + speed_boost(0.15, 无限)
           加 hunt_mode(1.0, D, 淡出 D) + hunt_mode_visuals(1.0, D, 淡出 5)      D = 30 / 升级 40
           huntModeEndTimes[p] = now + D
           thread 身体特效 + 声音
           thread 状态效果守护（战术冷却 mod；到时停所有状态效果）
           [sonarRange > 0] thread 跟随扫描触发器
           放一只白乌鸦（TrackingVision）
 └─ OnWeaponDeactivate：解锁武器、攀爬、载具（.nut:260-269）

生效中：
   击倒 / 击杀敌人 → 战术充满；[升级3] 延长；[升级2] +50 HP；（击杀）没有乌鸦就放一只
   剩 2 s → 循环声换成结束声；延长后回到 >2 s 再换回来
结束：Time() >= huntModeEndTimes → 发 HuntMode_End，停全部状态效果
     或 死亡 / 倒地 / 换职业 / HuntMode_ForceAbilityStop（比赛决出胜者时 .nut:41, :763-773）
客户端：hunt_mode_visuals 关 → 关去色、关灯效、停调色线程（权重归 0）、停屏幕粒子
```

- **不能用**：`.txt` 里没有特殊限制；动作期间锁武器（`.nut:236`）。
- **冷却**：弹夹 150，每秒回 1 → 150 s（`.txt:68-74` MP_BASE）。
- **升级分支**（S21 传奇升级，脚本按被动判断）：
  - `PAS_ULT_UPGRADE_ONE`（`upgrade_bloodhound_extended_hunt`）：时长 40 s（playlist `bloodhound_ult_upgraded_duration`，`.nut:58-76`）。
  - `PAS_ULT_UPGRADE_TWO`（`upgrade_bloodhound_knock_regen_during_hunt`）：击倒 / 击杀时 +50 HP（不超上限，`.nut:80-88`）。
  - `PAS_ULT_UPGRADE_THREE`（`upgrade_bloodhound_knock_extends_ult`）：击倒 / 击杀延长时间（`.nut:103`、`.nut:174`）。
  - `PAS_TAC_COOLDOWN_REDUCTION`（`upgrade_bloodhound_ult_tac_cooldown_reduction`）：大招期间战术加 mod `tac_cd_in_ult`（`.nut:522-532`）。战术 `.txt` 里只看到 `ult_active` mod（回充 30/s），没有 `tac_cd_in_ult` 这个 mod 名（`weapons/mp_ability_area_sonar_scan.txt:84-95`）。要实测。

**和 APEX-REPORT 2.4 的差别（更正）：**
1. APEX-REPORT 写"击倒 +5 s"。S21 脚本里**延长要有升级 3**（`.nut:103`、`.nut:174`），而且不是固定 +5：按剩余时间在 5–15 s 之间插值（见 3.2.3）。没升级时击杀只给战术充满 + 乌鸦。
2. APEX-REPORT 写"自己看到的，视野内，不穿墙"。标红来自 `threat_vision`（原生）；脚本里另有一套"视野 70°、视线不挡才标"的声纳扫描（`TargetShouldBeSonared`），但**默认关**（`bloodhound_ult_sonar_range` 默认 0）。威胁视觉本身是否要求视线、多远，脚本看不到，要实测。

## 3. 代码

### 3.1 入口

- `MpAbilityHuntModeWeapon_Init`（`.nut:29-55`）：服务端挂倒地、击杀回调，读 `bloodhound_ult_sonar_range`；注册信号；客户端注册调色、屏幕粒子，挂 `hunt_mode` 和 `hunt_mode_visuals` 的开 / 关回调（`hunt_mode` 的回调是空函数 `.nut:688-704`，画面全挂在 `hunt_mode_visuals` 上）。
- `MpAbilityHuntModeWeapon_OnWeaponTossPrep`（`.nut:226-243`）：动作开始时的锁定。`ACTIVATION_TIME = 2.1`（注释说是临时修复：防止跑墙时收枪出问题）。
- `OnWeaponPrimaryAttack_hunt_mode`（`.nut:246-257`）：`HuntMode_Start`，返回 `ammo_min_to_fire`（扣满 150）。

### 3.2 核心逻辑

#### 3.2.1 "模式" = 一组状态效果 `HuntMode_Start`（`.nut:272-303`）+ 守护线程 `HuntMode_HandleStatusEffects`（`.nut:466-578`）

```
ids = [ AddEndless(threat_vision, 1.0),
        AddEndless(speed_boost, 0.15),
        AddTimed(hunt_mode, 1.0, D, fadeout=D),
        AddTimed(hunt_mode_visuals, 1.0, D, fadeout=5.0) ]
endTimes[p] = now + D
守护线程：
    [升级] 战术加 mod tac_cd_in_ult
    while now < endTimes[p]: WaitFrame
    结束（含被信号打断）：去掉 mod；Signal HuntMode_End；StatusEffect_Stop 全部 ids
```

要点：无限期的状态效果（威胁视觉、加速）靠守护线程统一停；有时长的也一起停。延长时间改的是 `endTimes` 表 + 重加两个有时长的状态效果（3.2.3），无限期的不用动。

`AddTimed` 第 5 个参数是淡出时长（推断，见 `_shared/E-STATUS-EFFECT.md`）：`hunt_mode` 淡出 = 整段（严重度从 1 线性降到 0，推断用于 HUD 进度），`hunt_mode_visuals` 最后 5 s 淡出 → 调色权重最后 5 s 从 1 降到 0。

#### 3.2.2 跟随玩家的扫描触发器 `HuntMode_ScanTargets`（`.nut:319-358`）、`TriggerTrackOwner`（`.nut:360-370`）、`SonarTrigger_OnEnter/OnLeave`（`.nut:372-381`）、`EntitySonarThink`（`.nut:383-442`）、`TargetShouldBeSonared`（`.nut:444-464`）

默认关（`sonarRange` 默认 0）。打开时：

```
trigger = trigger_cylinder，只放进主人的 realm
  半径 = 上高 = 下高 = sonarRange           // 下高也设，因为判断的是脚底，脚可能陷进地面一点
  过滤：所有 NPC、pilot 玩家、非角色 = 0；IMC / Militia / Other 队都要（"对 survival 很关键"）
  进入回调 → trigger.e.attachedEnts.append(ent)；thread EntitySonarThink
  离开回调 → attachedEnts.remove(ent)
DispatchSpawn；thread TriggerTrackOwner；SearchForNewTouchingEntity（把已在里面的也算进来）

TriggerTrackOwner：每帧 trigger.SetOrigin(owner.GetOrigin())

EntitySonarThink(ent)：
   不同 realm / 自己 / 友方 → 返回
   sonared = false
   每帧：
     ent 不在 attachedEnts（且不是门）→ 结束
     !sonared 且 TargetShouldBeSonared → SonarStart(ent, ent.origin, 我队, 我)；sonared = true
     sonared 且 !TargetShouldBeSonared → SonarEnd；sonared = false
   结束时若 sonared → SonarEnd

TargetShouldBeSonared(ent, looker)：
   dot2D(视线方向, normalize(ent.center − 眼睛)) >= cos(DEFAULT_FOV=70°)    // 注意是 2D 点积
   且 TraceLine(眼睛 → ent.center, 忽略 looker 和 ent, VISIBLE).fraction >= 0.99
```

注意：`DotProduct2D` 用的是没归一化的 3D 方向向量的 xy 分量（推断：目标在正上 / 正下方时 xy 分量变短，点积变小，所以上下方向的判定比 70° 窄）。`DEFAULT_FOV = 70`（`vscripts/sh_consts.gnut:2`）当成**半角**用（`deg_cos(70)`），即左右各 70°。

这是一个可以单独拿走的"**跟随触发器 + 每目标线程**"部件：触发器只做粗筛（圆柱范围），细判断（视角、视线）在每个目标自己的线程里每帧做，进出状态变化时调 `SonarStart/End`。

#### 3.2.3 击杀延长 `CalculateTimeExtension`（`.nut:159-166`）和两个回调（`.nut:91-157`、`.nut:168-222`）

```
extension(剩余 r) = GraphCapped(r, 10, 2, 5, 5×3)
   r >= 10 s → +5 s；r <= 2 s → +15 s；之间线性
endTimes[p] += extension
停掉 hunt_mode / hunt_mode_visuals，重加：
   hunt_mode(1.0, r + ext, fadeout = D)           // 淡出参数仍是 D，不是新时长（推断：严重度曲线不再从 1 开始线性到 0）
   hunt_mode_visuals(1.0, r + ext, fadeout = 5)
HUD 提示 "+int(ext) 秒"
```

- 没有上限（和 Revenant 暗影不同，Revenant 封顶初始时长）。
- 击杀回调 `HuntMode_OnPlayerKilled`：只算对方**不在倒地中**的直接击杀（`.nut:100`），倒地中的补刀不算（已经在击倒时算过）。
- 倒地回调 `HuntMode_OnPlayerStartBleedout`：战术充满写的是 `player.GetOffhandWeapon(OFFHAND_TACTICAL)`，`player` 是**被击倒的人**（`.nut:205`），击杀回调写的是 `attacker`（`.nut:139`）。像是倒地分支的笔误（推断：击倒时充满的是对方的战术，不是 Bloodhound 的）。在 S21 原版还是 SDK 改出来的不确定，要实测。
- 两个回调最后都会停掉**被击倒 / 被杀的人**自己的狩猎状态（`.nut:152-156`、`.nut:217-221`）。

### 3.3 客户端表现

- `HuntMode_StartVisualEffect`（`.nut:706-718`，`hunt_mode_visuals` 开）：`GfxDesaturateOn()`、`Chroma_StartHuntMode()`、thread 调色、thread 屏幕粒子。只对本地视角玩家。
- `HuntMode_UpdatePlayerScreenColorCorrection`（`.nut:647-686`）：

```
SetExclusive(cc, true)；SetWeight(cc, 1.0)
每帧：
   w = StatusEffect_GetSeverity(player, hunt_mode_visuals)       // 最后 5 s 从 1 淡到 0
   w = GraphCapped(now − start, 0, 0.0125, 0, w)                  // 淡入 0.0125 s（注释：hack，状态效果没有淡入）
   SetWeight(cc, w)
结束：SetWeight(cc, 0)；SetExclusive(cc, false)
```

  `FOV_SCALE = 1.2` 定义了没用（`.nut:668`）。
- `HuntMode_PlayActivationScreenFX`（`.nut:734-759`）：驾驶舱粒子 `P_hunt_screen`，`PARTICLE_SCRIPT_FLAG_NO_DESATURATE`（不被去色），一直到 `HuntMode_StopActivationScreenFX`。
- `HuntMode_StopVisualEffect`（`.nut:720-732`）：反向全部关掉。
- 白乌鸦 `TrackingVision_CreateWhiteRavenInFlight`（`.nut:299`、`.nut:128`）：Bloodhound 被动的乌鸦系统，不在本批范围，只记调用点。

### 3.4 依赖的公共代码

- 状态效果框架：`threat_vision`、`speed_boost`、`hunt_mode`、`hunt_mode_visuals`（`status_effect_types.txt:20, :24-25`）→ `_shared/E-STATUS-EFFECT.md`。
- 屏幕调色 + 去色 → `_shared/E-SCREEN-COLOR-CORRECTION.md`。
- 声纳高亮 `SonarStart / SonarEnd`（`vscripts/weapons/sh_sonar.gnut:253-434`）→ `_shared/E-SONAR-HIGHLIGHT.md`。
- 原生：`threat_vision` 的画法、`GfxDesaturateOn/Off`、`trigger_cylinder`。
- `DEFAULT_FOV = 70`（`sh_consts.gnut:2`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| HUNT_MODE_DURATION | 30 | s | `.nut:12` | 持续 | |
| 升级时长 | 40 | s | playlist `bloodhound_ult_upgraded_duration`（`.nut:60`） | `PAS_ULT_UPGRADE_ONE` | |
| fire_duration | 25 | s | `.txt:76` | 武器设置里的值，和脚本 30 s 不一致；脚本不读它（推断：HUD 用脚本的状态效果） | |
| speed_boost 严重度 | 0.15 | 比例 | `.nut:276` | 移速 +15%（推断：严重度直接当倍率加成） | |
| threat_vision 严重度 | 1.0 | — | `.nut:275` | | |
| hunt_mode 淡出 | = D | s | `.nut:279` | | |
| hunt_mode_visuals 淡出 | 5.0 | s | `.nut:280`、`.nut:111`、`.nut:182` | 调色最后 5 s 淡出 | 大：更早开始变淡 |
| 调色淡入 | 0.0125 | s | `.nut:669` | 实际等于瞬间开 | |
| 调色文件 | `materials/correction/ability_hunt_mode.raw_hdr` | — | `.nut:47` | | |
| 结束声提前 | 2.0 | s | `.nut:615` FADE_DURATION | | |
| ACTIVATION_TIME | 2.1 | s | `.nut:239` | 动作期间禁跑墙 / 二段跳 | |
| toss_time | 1.2 | s | `.txt:17` | 按键到生效（推断：动画事件触发点在这之内） | |
| 击杀延长基数 | 5.0 | s | `.nut:13` HUNT_MODE_KNOCKDOWN_TIME_BONUS | | |
| 延长插值起点 | 10.0 | s 剩余 | playlist `bloodhound_ult_extension_start_time`（`.nut:161`） | 剩 ≥10 s 时 +5 | |
| 延长插值终点 | 2.0 | s 剩余 | playlist `bloodhound_ult_extension_end_time`（`.nut:162`） | 剩 ≤2 s 时 +15 | |
| 延长最大倍数 | 3.0 | × | playlist `bloodhound_ult_extension_max_multiplier`（`.nut:163`） | 最多 5×3 = 15 s | |
| 击倒回血（升级 2） | 50 | HP | `.nut:14` | | |
| 跟随扫描半径 | 0（关） | u | playlist `bloodhound_ult_sonar_range`（`.nut:36`） | >0 才建触发器；半径 = 上高 = 下高 | |
| 跟随扫描视角 | 70（半角） | ° | `DEFAULT_FOV`，`sh_consts.gnut:2`；`.nut:446` | | |
| 跟随扫描视线阈值 | 0.99 | trace fraction | `.nut:460` | | |
| 冷却 | 150 / 回 1 每秒 | s | `.txt:68-74` | 150 s | |
| 护甲回充 mod | ×1.25 / ×1.5 | — | `.txt:110-117` | | |
| 战术 `ult_active` mod | 回充 30/s、fire_rate 1.25、收 / 拿 0.5 / 0.4 s | — | `weapons/mp_ability_area_sonar_scan.txt:88-95` | 推断：大招期间战术几乎立刻充满（25/30 ≈ 0.83 s）。本脚本里没有加这个 mod 的代码，只加 `tac_cd_in_ult`（升级） | |
| 烟挡威胁视觉 | true | 开关 | playlist `smoke_blocks_threat_vision`（`smokescreen.nut:256`） | | |

## 5. 未解决和要实测的

1. **威胁视觉的范围和视线**：原生实现，脚本看不到。测法：开大招，在训练场放假人（墙后 / 视野外 / 远近不同），截图看哪些被标红；或读客户端高亮状态。
2. **大招期间战术冷却**：`ult_active`（30/s）有没有被加上、由谁加（脚本里没找到）；`tac_cd_in_ult` 这个 mod 在 `.txt` 里不存在，加上会不会报错。测法：开大招后放一次战术，记战术回满时间。
3. **加速 0.15 的实际效果**：测法：开大招前后在平地冲刺，读水平速度（R5 冲刺约 300 u/s，推断开后约 345）。
4. **击倒时战术充满写的是谁**（`.nut:205` 用了被击倒者）：测法：两个玩家 / bot，Bloodhound 先放空战术，开大招击倒 bot，看自己战术有没有充满。
5. **延长需不需要升级**：本地构建玩家有没有 `PAS_ULT_UPGRADE_THREE`；没升级时击杀是否真的不加时。测法：开大招击杀假人 / bot，看剩余时间。
6. **去色 `GfxDesaturateOn` 的强度和例外**（高亮、标了不去色的粒子之外还有什么）：原生，只能看画面。

## 6. HSD 实现

**未实现。** `HSD-Unity/Assets/HSD/Game/Runtime/Combat/` 有扫描（`Tacticals.cs:222` `Scan`）和地图透视（`Tacticals.cs:197` `MapReveal`），没有"模式"类状态、去色调色、跟随触发器。

建议做法：
- **模式** = 一组状态效果（威胁视觉、加速、视觉强度），共用一个到期时间；见 `_shared/E-STATUS-EFFECT.md`。HSD 移动层的加速走 R5 移动模型（`R5MotorV2`）的速度倍率；加速 15% 要在移动层留一个"外部倍率"入口，属于移动层的改动，要另开任务（本批只记录）。
- **画面**：URP Volume（Color Adjustments 饱和度 −100 + LUT），权重 = 视觉状态的严重度；敌人高亮用描边 / 穿墙材质，不受去色影响。
- **敌人标红**：PvE 里可以简化成"视野内的敌人每帧加 `outlinedUntil = now + 一帧`"，复用 `CombatCore.cs:79` 的 `outlinedUntil` 字段和 `CombatHud.cs:178` 的 `Outlines`。
- **跟随扫描触发器**：HSD 没有物理触发器，直接每帧遍历敌人做距离 + 视角 + 射线判断即可（R5 用触发器只是为了性能）。
- **击杀延长**：`ext = lerp(5, 15, (10 − r) / 8)`，夹在 [5, 15]；是否要求"升级"做成开关。
- 开关建议：`hsd.combat.huntMode.*`（时长、加速、延长开关、延长曲线、视觉强度）。
