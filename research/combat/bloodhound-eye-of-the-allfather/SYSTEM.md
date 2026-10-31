# Bloodhound 战术 Eye of the Allfather（全知之眼）· 系统记录

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`。主脚本 `vscripts/weapons/mp_ability_area_sonar_scan.nut`（796 行），武器设置 `weapons/mp_ability_area_sonar_scan.txt`，共用 `vscripts/weapons/sh_sonar.gnut`。
已有研究：`TF2-Research/expansion/apex/APEX-REPORT.md` 2.4（形状、范围、时长、冷却已写，本文引用并补全流程、代码、参数）。本文对 2.4 有**三处更正**（第 2 节末尾），其中两处影响 HSD 现有实现。

## 0. 概要

- **技能**：Bloodhound / 战术 / Eye of the Allfather / `mp_ability_area_sonar_scan`。
- **确认是 Bloodhound 的锥形扫描**：`.txt` `hud_icon "rui/hud/tactical_icons/tactical_bloodhound"`；脚本特效 `P_sonar_bloodhound` / `P_sonar_bloodhound_eyes`（`.nut:13-14`）；playlist 键 `bloodhound_scan_duration` / `bloodhound_scan_cone_fov`（`.nut:53`、`.nut:56`）；视图模型和大招共用 `ptpov_bloodhound_huntmode.rmdl`（`.txt` viewmodel）。是锥形（`AREA_SONAR_SCAN_CONE_FOV = 125` `.nut:23`）。
- **一句话**：按下瞬间朝视线方向做一次 125° 锥形、3000 u 的扫描，穿墙；扫到的敌人轮廓高亮 1.5 s、胸口锁定框 3 s；屏幕和世界里放一道扫描波。
- **分类**：可视化 ✔（扫描波、屏幕调色、锁定框）、系统 ✔（一次性锥形查询 + 高亮计数框架，可以拿去给别的"侦测"效果用）。好技能（效果）中：PvE 里"标出敌人"有用。
- **可拆出的部件**：
  - 一次性锥形范围查询（近距离放宽） → 3.2.1 `AreaSonarScan_CheckandScanValidTarget`
  - 每次扫描一个目标列表 + 两段计时（先关高亮，再关锁定框） → 3.2.2 `AreaSonarScan_SonarThink`
  - 声纳高亮的引用计数开 / 关 → `_shared/E-SONAR-HIGHLIGHT.md`（`SonarStart` / `SonarEnd`）
  - 扫描波特效（世界平面波 + 地面拖尾）→ 3.3、`_shared/E-SONAR-HIGHLIGHT.md` 第 3.3 节
  - HUD 计数用状态效果严重度传数字 → 3.2.3
  - 屏幕调色 0.5 s 淡入淡出 → `_shared/E-SCREEN-COLOR-CORRECTION.md`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 锥形扫描 | 服务端脚本：按下时遍历敌方玩家 + 全部 NPC + 登记过的道具，逐个算角度和 2D 距离 | `.nut:200-210`、`.nut:270-281`、`.nut:486-598`。默认"快速逻辑"（playlist `area_sonar_scan_faster_scan_logic` 默认 true `.nut:165`）；旧逻辑是建一个半径触发器（`.nut:237-260`） |
| 穿墙 | 不做视线检查；只查 Catalyst 铁磁墙 `FerroWall_BlockScan(眼睛, 目标中心)` | `.nut:567` |
| 敌人轮廓 | 高亮上下文 `HIGHLIGHT_BLOODHOUND_SONAR`，`HighlightEnableForTeam(我队)` | `sh_sonar.gnut:265`；`sh_highlight.gnut:100`（S3 兼容时名字是 `bloodhound_sonar_blockscan` `:160`） |
| 胸口锁定框 | 粒子 `P_ar_target_sonar` 挂 `CHESTFOCUS`，只本队和主人可见 | `sh_sonar.gnut:289-324` |
| 被扫者提示 | 状态效果 `sonar_detected`（无限，扫描结束时停）；客户端：自己的视图模型被高亮成 `HIGHLIGHT_COLOR_ENEMY` + 音效 | `sh_sonar.gnut:335-338`、`:635-689` |
| 隐身闪烁 | `SetCloakFlicker(0.5, −1)`（隐身的目标被扫时闪） | `sh_sonar.gnut:292` |
| 助攻 | 扫到即给扫描者记助攻（playlist `disable_sonar_assist` 可按角色关；本地补丁对 Bloodhound 关了） | `sh_sonar.gnut:231-251`、`:343-347`；`playlists_r5_patch.txt:45` |
| 两段时长 | 服务端线程：wait 1.5 → 关高亮；再 wait 到 3.0 → 关锁定框、停状态效果 | `.nut:395-409` |
| HUD 计数 | 状态效果 `device_detected`，严重度 = min(2 + n, 13) × 0.01，3 s | `.nut:380-384` |
| 屏幕效果 | 状态效果 `sonar_pulse_visuals`（3 s）→ 客户端驾驶舱粒子 `P_sonar` + 调色 `area_sonar_scan.raw_hdr` | `.nut:153`、`.nut:746-777` |
| 世界扫描波 | 服务端→所有同 realm 玩家：`ServerCallback_SonarPulseConeFromPosition` → 粒子 `P_ar_sonar_plane_CP` + （主人）地面拖尾 `P_sonar_ground_detect` | `.nut:454-462`；`sh_sonar.gnut:542-620` |
| 扫描者头部特效 | `P_sonar_bloodhound`（一次）+ `P_sonar_bloodhound_eyes`（10 s，敌我可见） | `.nut:370-378` |
| 声音 | 激活 1P/3P、首个目标"锁定开始"、结束"锁定结束"（有目标时） | `.nut:133-140`、`.nut:578-582`、`.nut:326-330` |

**服务端 / 客户端**：判定全在服务端；扫描波、屏幕、被扫者视图模型高亮在客户端。`sh_sonar.gnut` 里有 SDK 为 S3 dedi 改过的痕迹：`// S21: fx.SetLOSBlockScan( true ) — S3 has no entity method`（`:317`）、`// dual-arity: S21 (contextId, bitfield); S3 SERVER 1-arg bitfield only`（`:384-389`）；`.nut:155` `// S21: owner.Anim_PlayAttackGesture — S3 has no entity method`；`.nut:570` 去重注释提到 FR（火力训练场）假人。所以**服务端这条路径确定被改过**，第 5 节列实测。

## 2. 流程

```
按键（25/25，charge_time 0.01，charge_end_forces_fire）            (.txt charge_*)
 └─ OnWeaponPrimaryAttackAnimEvent（.nut:74-99）
      scanOrigin = HEADSHOT 骨骼点；dir = GetViewForward()（含俯仰）
      thread AreaSonarScan_SonarThink；0.4 s 后语音
      扣 25

AreaSonarScan_SonarThink（.nut:142-410）
 t=0  加 device_detected(0.01, 3 s) + sonar_pulse_visuals(1, 3 s)
      本次扫描编号 idx；targets[idx] = []
      遍历 敌方玩家、全部 NPC、登记过的道具（半径内）→ 合格的：SonarStart + 加进 targets[idx]
      激活声；广播扫描波；头部特效；device_detected 改成 (2+n)×0.01，3 s
 t=1.5（升级 3.0）对 targets[idx] 逐个 SonarEnd_EndHighlight（关轮廓）
 t=3.0  线程结束 → 对 targets[idx] 逐个 SonarEnd（不再关高亮，只关锁定框 / 状态效果），删 targets[idx]
       有目标时播"锁定结束"
打断：主人死亡 / 销毁 → 直接走结束清理（同时关高亮和锁定框）
```

- 锥只判断一次（按下的那一帧），之后目标跑出锥也照样高亮到时间结束；高亮跟着目标实时移动（高亮是挂在目标实体上的）。
- 连续扫描互不影响：每次扫描有自己的 `idx` 和目标表（`.nut:179-198`）；同一目标被多次扫描时，`SonarStart` 的引用计数保证先结束的那次不会把后一次的高亮关掉（`_shared/E-SONAR-HIGHLIGHT.md`）。
- **冷却**：弹夹 25，回 1/s → 25 s（`.txt` ammo_clip_size 25、regen 1）。`ult_active` mod：回充 30/s（大招期间，`.txt:88-95`）。
- **升级**：`PAS_TAC_UPGRADE_ONE`（`upgrade_increased_scan_duration`）高亮 1.5 → 3.0 s（`.nut:109-117`）。白乌鸦被扫到时触发乌鸦（被动系统，`.nut:527-548`），不在本批范围。

**和 APEX-REPORT 2.4 的差别（更正 / 补充）：**
1. **锥是 3D 的，不是水平角。** 角度用 `DotProduct(normalize(目标中心 − 脚底), normalize(视线方向))`（`.nut:510-514`），视线方向含俯仰（`GetViewForward()` `.nut:87`）。只有**距离**是 2D（`Distance2DSqr` `.nut:518`）。所以"楼上楼下都能扫到"只在高度差小于锥能覆盖的范围时成立：平视时，水平 500 u 外、高 1000 u 的目标与视线夹角 63.4° > 62.5°，扫不到；抬头就能扫到。
2. **角度的顶点是脚底（`owner.GetOrigin()`），不是眼睛。** 传入的 `scanOrigin`（头部）只用于扫描波特效和旧触发器逻辑（`.nut:86-87`、`.nut:163`、`.nut:368`）；铁磁墙判断用眼睛（`.nut:567`）。
3. **近距离放宽按距离平方插值，并且先被 `dot <= 0` 截断。** `matchAngle = GraphCapped(dist², 32², 128², 125, 62.5)`（`.nut:523`），且 `dot <= 0`（夹角 ≥ 90°）先返回（`.nut:512`）。结果：dist ≤ 约 98 u 时整个前半球（90°）都算，98 → 128 u 迅速收到 62.5°。APEX-REPORT 写的"32 → 128 u 之间逐渐收"没错，但 HSD 按距离线性插值（`Tacticals.cs:226-231`），在 32–128 u 之间比 R5 窄（例如 80 u：R5 90°，HSD 76.25°）。

## 3. 代码

### 3.1 入口

- `MpAbilityAreaSonarScan_Init`（`.nut:47-68`）：读 playlist（时长 3.0、半径 3000、锥角 125）；客户端注册调色 `materials/correction/area_sonar_scan.raw_hdr`，挂 `sonar_pulse_visuals` 开 / 关回调。
- `OnWeaponPrimaryAttackAnimEvent_ability_area_sonar_scan`（`.nut:74-99`）：见第 2 节。

### 3.2 核心逻辑

#### 3.2.1 锥形查询 `AreaSonarScan_CheckandScanValidTarget`（`.nut:486-598`）

```
不是敌队（且不是自己的白乌鸦）→ 返回
不同 realm / 已死 → 返回
d   = normalize(ent.center − owner.origin)               // 脚底为顶点
dot = DotProduct(d, normalize(coneDir))                   // 3D
dot <= 0 → 返回                                           // 背后半球一律不算
angle = DotToAngle(dot)
dist² = Distance2DSqr(ent.center, owner.origin)           // 水平距离
dist² > R² (3000²) → 返回
matchAngle = GraphCapped(dist², 32², 128², FOV, FOV/2)     // 125 → 62.5，按平方插值
angle > matchAngle → 返回
[白乌鸦分支]
FerroWall_BlockScan(眼睛, ent.center) → 返回
本次已扫过（NPC 和道具登记表可能重复，比如训练场假人）→ 返回     // SDK 注释 .nut:570
第一个目标：播"开始锁定"
IsHostileSonarTarget 且不是 TEAM_TICK → detections++        // 只计数用，不影响高亮
SonarStart(ent, ent.origin, 我队, 我)
targets[idx].push(ent)
```

`IsHostileSonarTarget`（`.nut:660-694`）：敌队、不是自己、活着、是 `CBaseAnimating`、类名不以 `prop_` 开头、不是"玩家拥有的假 AI"（有 BossPlayer 或 Owner 是玩家且不是玩家 / NPC / 分身）、不是 marvin、不是投射物。只决定 HUD 计数，不决定高亮：被登记的道具（陷阱等）会被高亮但不计数。

#### 3.2.2 两段计时 `AreaSonarScan_SonarThink`（`.nut:142-410`）

见第 2 节时间线。关键：用 `PassByReferenceBool hasRemovedHighlight` 记"高亮是否已经关过"，结束清理时 `SonarEnd(target, team, owner, endHighlight = !hasRemovedHighlight)`（`.nut:319-357`），避免高亮被重复减计数。

#### 3.2.3 HUD 计数（`.nut:380-384`）

```
deviceCount = 2 + detections                 // "2 表示 0 个"
severity    = min(deviceCount, 13) × 0.01    // 最多 0.13 → 显示 10+（11 个）
StatusEffect_AddTimed(owner, device_detected, severity, 3.0, 0)
```

把一个整数编码进状态效果的严重度，HUD（RUI）读严重度解码。开始时先加一个 0.01 的（`.nut:152`）。

### 3.3 客户端表现

- `AreaSonarScan_StartScreenEffect`（`.nut:746-761`，`sonar_pulse_visuals` 开）：驾驶舱粒子 `P_sonar`；调色权重 0→1，0.5 s（本文件自带一份 `ColorCorrection_LerpWeight` `.nut:779-793`，和 Revenant 那份一样）。
- `AreaSonarScan_StopScreenEffect`（`.nut:763-777`）：停粒子；调色 1→0，0.5 s。
- 扫描波（`sh_sonar.gnut:542-598`）：`pulseSpeed = SONAR_PULSE_SPACE + SONAR_PULSE_SPEED × speedScale = 400 + 300 × 3.0 = 1300 u/s`（`sh_consts.gnut:800-801`，`speedScale = 3.0` `.nut:460`）；粒子 `P_ar_sonar_plane_CP`，角度 = 扫描方向，CP1 = (半径 / 速度, 半径 / 80, 0) = (2.31 s, 37.5, 0)。`hasDamageAmp` 两个分支用的是同一个粒子（`sh_sonar.gnut:578-589`）。
- 地面拖尾（只给扫描者，`showTrail = owner == player` `.nut:458`）：客户端 mover 从眼睛出发，`NonPhysicsMoveTo(眼睛 + dir × 半径, 2.31 s)`，挂 `P_sonar_ground_detect`，到了停粒子，2 s 后删（`sh_sonar.gnut:601-619`，时长夹在 0.05–5 s）。
- 被扫者：`sonar_detected` 开 → 视图模型（手臂、武器、第一人称代理）高亮成 `HIGHLIGHT_COLOR_ENEMY = <1, 0.36, 0.12>`（`sh_highlight.gnut:87`）+ 音效 `HUD_MP_EnemySonarTag_Activated_1P`（`sh_sonar.gnut:635-689`）。
- `CreateViemodelSonarFlash`（`.nut:698-744`）：红色 0.5 s 闪，本文件里没有调用点（推断：旧代码）。

### 3.4 依赖的公共代码

- `SonarStart` / `SonarEnd` / `SonarEnd_EndHighlight`、扫描波、被扫者回调：`vscripts/weapons/sh_sonar.gnut` → `_shared/E-SONAR-HIGHLIGHT.md`。
- 状态效果：`device_detected`、`sonar_pulse_visuals`、`sonar_detected` → `_shared/E-STATUS-EFFECT.md`。
- 调色 → `_shared/E-SCREEN-COLOR-CORRECTION.md`。
- `FerroWall_BlockScan`（`vscripts/weapons/mp_weapon_ferro_wall.nut:734`）。
- `GraphCapped`、`DotToAngle`、`Distance2DSqr`（全局工具）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| 半径 | 3000 | u（水平） | `.nut:20`；playlist `area_sonar_scan_radius_override`（`.nut:54`） | 最远距离 | |
| 锥角 | 125（全角，远处半角 62.5） | ° | `.nut:23`；playlist `bloodhound_scan_cone_fov`（`.nut:56`） | | |
| 近距放宽区间 | 32² → 128²（按平方插值） | u² | `.nut:523` | 32 u 内 matchAngle = 125，再被 dot>0 截到 90 | |
| 顶点 | 脚底 `owner.GetOrigin()` | — | `.nut:510`、`.nut:518` | | |
| 方向 | `GetViewForward()`（含俯仰） | — | `.nut:87` | | |
| 高亮时长 | 1.5（升级 3.0） | s | `.nut:22`、`.nut:109-117` | 轮廓 | |
| 扫描总时长 | 3.0 | s | playlist `bloodhound_scan_duration`（`.nut:53`） | 锁定框、被扫状态、屏幕效果 | |
| HUD 计数时长 | 3.0 | s | `.nut:21` | | |
| HUD 计数上限 | 13 → 显示 10+ | — | `.nut:382` | | |
| 扫描波速度 | 1300 | u/s | `400 + 300 × 3.0`；`sh_consts.gnut:800-801`、`.nut:460` | 波走完 3000 u 用 2.31 s | |
| 扫描波粒子尺寸基准 | 80 | u | `sh_sonar.gnut:483` AR_EFFECT_SIZE_CONE | CP1.y = 半径 / 80 | |
| 地面拖尾残留 | 2.0 | s | `sh_sonar.gnut:616` | | |
| 头部眼睛特效 | 10.0 | s | `.nut:378` | | |
| 调色淡入 / 淡出 | 0.5 / 0.5 | s | `.nut:760`、`.nut:776` | | |
| 调色文件 | `materials/correction/area_sonar_scan.raw_hdr` | — | `.nut:60` | | |
| 隐身闪烁 | 0.5，−1 | — | `sh_sonar.gnut:292` | | |
| 被扫者高亮色 | <1, 0.36, 0.12> | RGB 0–1 | `sh_highlight.gnut:87` | | |
| 冷却 | 25 / 回 1 每秒 | s | `.txt` ammo 25、regen 1 | 25 s | |
| `ult_active` 回充 | 30 | /s | `.txt:88-95` | | |
| charge_time | 0.01 | s | `.txt` | 几乎立刻 | |
| fire_rate / holster / deploy | 1.25 / 1.0 / 0.8 | — / s / s | `.txt:53-56` | | |
| minimap_reveal_distance | 32000 | u | `.txt` | 推断：用的时候在敌人小地图上暴露的距离 | |
| 语音延迟 | 0.4 | s | `.nut:88` | | |

## 5. 未解决和要实测的

1. **3D 锥的上下覆盖**：测法：火力训练场，在台子上 / 下放假人（高度差 500、1000 u，水平 500、1500 u），平视和抬头各扫一次，看哪些被高亮（AgentLink 读 `ent.e.inSonarTriggerCount` 或 `sonar_detected` 状态效果）。
2. **近距 32–128 u 的角度**：测法：假人放在玩家侧面 80 u、角度 80°，扫描看是否命中（R5 推断命中，HSD 现有实现不命中）。
3. **SDK 改动范围**：`sh_sonar.gnut` 有 S3 兼容改动（`SetLOSBlockScan`、`HighlightSetTeamBitField`）。高亮在 S3 dedi 上是否和 S21 一样能穿墙要看画面。测法：墙后假人，扫描后截图。
4. **训练场假人是否算 NPC**：`.nut:570` 注释说 NPC 和道具登记表都可能返回同一个假人。测法：扫描假人，看 HUD 计数是 1 不是 2。

## 6. HSD 实现

**已实现（简化）**：`HSD-Unity/Assets/HSD/Game/Runtime/Combat/Tacticals.cs:219-249` `Scan`（照 APEX-REPORT 2.4）。`CombatCore.cs:78-79` `outlinedUntil` / `markedUntil`，`CombatHud.cs:177-190` 画框。

和 R5 的差别（应进 `R5-DIFF-ARCHIVE.md`，由第二波实现时改或留开关）：

| 项 | R5 脚本 | HSD 现在 | 影响 |
|---|---|---|---|
| 锥的维度 | 3D：视线方向含俯仰，夹角按 3D 算 | 只算水平角（`Tacticals.cs:240-241`，用 yaw） | HSD 上下无限；R5 平视时高处 / 低处远一点的目标扫不到 |
| 顶点 | 脚底 | 玩家 `pos`（`Tacticals.cs:238`，也是脚底） | 一致 |
| 近距放宽 | 按距离平方插值 125→62.5，且先截到 90 | 按距离线性 90→62.5（`Tacticals.cs:226-231`） | 32–128 u 之间 HSD 更窄，最大差约 14°（80 u 处 90° vs 76.25°）。实际影响小（这么近的敌人基本在视野里） |
| 两段时长 | 1.5 s 轮廓 / 3 s 框 | 一致 | — |
| 铁磁墙 | 挡 | 没有 | HSD 没有铁磁墙 |
| 屏幕调色 / 扫描波 | 有 | 没有 | 外观 |
| HUD 计数 | 3 s，上限 10+ | `CombatHud.cs:113` 3 s | 一致 |

建议：加一个开关 `hsd.combat.scan.cone3d`（默认按 R5 = 3D），把 `HalfAngle` 改成按距离平方插值，旧版留开关。这是第二波的事，本批不改代码。
