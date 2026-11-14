# 00 资料盘点

hb0 写（2026-11-14）。研究仓库 main = `86ec5f1`（#96），HSD-Unity main = `17260f2`（#64）。

## 白话说明

这一页告诉各章会话：**写这一章要看哪些文件、它们在哪、已经有什么、还缺什么**。路径都核对过（`git cat-file -e`），可以直接打开。

缺的部分只标出来，这一轮**不做新实测**。要新测的放进 [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md)，表里的编号（如 B02-1）对应那里。

最大的几个缺口先说：

1. **手册最需要的战斗资料全在没合并的 PR 上**（09 章几乎全部，08 章的铁驭持枪，10 章的技能和道具）。而且是叠着的链，其中 #92 写着"等用户看"，挡着上面一整条。各章照引用 PR 的写法写，不要等合并。
2. **身体尺寸有两处 HSD 和 R5 对不上**：台阶 R5 22 u / HSD 18 u；碰撞体（站 72、蹲 48）都是 Source 默认值，R5 没量过（B01-1、B01-2）。
3. **时间窗口没有实测**：coyote time（走下台边还能跳多久）、跳跃缓冲（落地前按跳算不算），R5 都没量过，Unity 也没有（B03-1、B03-2）。
4. **TF2 跑墙还剩几个分支没实测**，墙跳排斥和上升中二段跳两条规则 HSD 和 TF2 实测不一样、还等用户定（B05-1 – B05-3）。
5. **敌人 AI 在 Unity 里是 0**，规格齐全但都是 TF2 的写法，要重写成引擎无关的规则（10 章）。
6. **没有一张合格线总表**，散在 FEEL §2、RPS / RUD 的逐字节规则、D-70、泰坦的 5 % / 5 mm（11 章）。

---

## 0. 怎么用这一页

### 0.1 路径写法

- 不加前缀的路径在**研究仓库**（`Apex-MovementAnalysis`），从仓库根目录算。
- `U:` = HSD-Unity 仓库。`U:…/` 省略的是 `Assets/HSD/R5Replay/Runtime/`（移动）；镜头、战斗、泰坦的 Unity 代码在 `Assets/HSD/Game/Runtime/` 下（泰坦是 `Assets/HSD/Game/Runtime/Titan/`），写全。
- `L:` = 工作区里的本地文件夹，**不在任何 git 仓库里**（`C:\Workspace\Playground\ReApex-DataAnalysis\` 下）：`L:TF2-Research/…`、`L:TECH-REPORT-1104/…`、`L:research-src/…`、`L:ghidra-projects/…`。
- "在哪"一列：`main`；`#93` = 研究仓库 PR #93 的分支，还没合并；`U#67` = HSD-Unity PR #67 的分支，还没合并；`本地`；`RawData` = 私有仓库 `letheli710/HSD-RawData`。

### 0.2 读 PR 分支上的文件

```
git -C Apex-MovementAnalysis-HB0 show origin/<分支>:<路径>
git -C HSD-Unity show origin/<分支>:<路径>
```

在 Git Bash 里读 `.claude/...` 这种路径，先 `export MSYS_NO_PATHCONV=1`。

**PR 叠法**（base 链）。注意：上层分支**不一定**包含下层最新的提交（比如 #123 的分支里没有 #95 后来加的 `hold-pose/`），一律按下表写的分支读。

| 线 | 链 |
|---|---|
| 战斗研究 | #86 → #88 → #92 → #93 → #95 → { #97 → #123 ；#99 → #103 ；#122 } |
| 决策记录 | #86 → #90 → #91 → #100 → #101 → #104 |
| 道具 | #86 → #87 → #89 |
| 泰坦模型 | #116 → { #117 ；#120 } |
| 直接对 main | #84、#85、#114、#115、#118、#119；#98、#102、#121 的 base 已合并，等于对 main |
| Unity 战斗 | U#53 → U#54–57 → U#58 → U#59 → U#60 → U#61 → U#63 → U#65 → { U#66 → U#70 ；U#67 → U#68 → U#69 → U#71 } |
| Unity 泰坦 | U#65 → U#66 → U#70 → `titan/walk-compare`（无 PR）→ U#72 → U#73–77 → U#78 → { U#82 → U#84 / U#85 / U#86 ；U#83 ；U#87 } |
| Unity 火箭跳 | U#52（对 main） |

研究 PR 逐个的情况和合并建议在 [`_notes/hb0-pr-merge-list.md`](_notes/hb0-pr-merge-list.md)。

### 0.3 各章都要用的资料

| 文件 | 在哪 | 内容 |
|---|---|---|
| `research/DESIGN-PHILOSOPHY.md` | main（11-02 版）；#122 大改（P1、T1–T3、§6–§7、§10–§12），#114 改 §6.6 | 设计哲学 P1–P9、技术理念 T1–T9、镜头规范 §6、枪械规范 §7、移动数字 §8.1、新东西怎么判 §9、不知道的事 §10。**§2.1 的依据标签手册沿用** |
| `DECISIONS.md` | main 只到 D-76 和 D-90 – D-93；D-77 在 #85，D-78 – D-80 在 #86，D-81 在 #90，D-82 – D-89 / D-94 / D-95 / D-113 – D-119 在 #91，D-96 – D-112 在 #98，D-103 – D-105 在 #100，D-124 – D-126 在 #101，D-128 / D-129 在 #104，D-130 – D-135 在 #102，D-138 以后在 #116 / #117 / #120 | 所有决定（选中和没选中的） |
| `R5-DIFF-ARCHIVE.md` | main；RJA 节在 #85，W3 节在 #91，枪模型 / 配装 / 霰弹在 #100 / #101 / #104 | 和 R5 的差别：一 已改（A-1、K-1 – K-4、C-12、R6U、RPS、RUD、GN、CAM2、G6、FND、D-75），二 未改，三 有意偏离 |
| `research/rea-native/CROSSCHECK-LEDGER.md`、`ledger.csv` | main | 代码对实测的账本（94 条）。§3.1 / §5 有过时处（见 04 章） |
| `research/rea-native/N-REPORT.md`、`NATIVE-MAP.md` | main | 原生研究总报告、函数地图。**NATIVE-MAP §3 有两个函数名过时**（0x140a4a7c0 是 `WalkMove` 不是 `WallRun_Move`；0x140a36130 是 `Gravity_HalfStep` 不是 `Grapple`），以 N2 为准 |
| `research/rea-native/convar-defaults/CONVAR-DEFAULTS.md` | main | 原生 ConVar 默认值（`sv_gravity` 750 等） |
| `research/phase2-local/static-values/STATIC-VALUES.md` | main | setfile / 脚本 / ConVar 的精确值 |
| `research/phase2-local/m2/PARAMETER-TABLE.md` | main | M2 实测参数 |
| `research/feel/FEEL.md` | main | R5 和 Unity 同输入叠图对照（F1 – F7），指标和容差 §2 |
| `research/phase2-local/data/` | main（216 个会话的曲线和摘要）；原始 rows 在 RawData | 实测数据 |
| `DEFERRED-DESIGN-TODO.md`、`SHELVED-ABILITIES.md` | main | 暂缓的设计（E1 – E3）、搁置的技能 |
| `workspace/TODO.md`、`RESEARCH-OVERVIEW.md` | main 停在 10-30；#84 到 10-31；工作区根目录的本地版更新（11-07） | 进度，**只作背景，过时处多** |
| `L:TECH-REPORT-1104/` | 本地 | 11-04 技术报告（方法论、复核问题、各专题），给人读的整理 |

**命名陷阱**：`U:…/ReferenceMotor.cs` 是 M1 的第一版模型；"Reference 配置"其实是 `MovementConfigs.Reference()`，跑的是 `R5MotorV2` + `R5MotorV2Params.R5Reference()` + N7 原生开关。手册写"参考实现"时指 `MovementConfigs.Reference()` 整套；`R5Reference()` 单独用是回放电机（D-66 的尺子）。（hb-integrate 11-14 按总控决定统一，见 README 写法规范第 4 条。）

---

## 01 单位与身体（hb0，已写）

见 [01-units-body.md](01-units-body.md)。资料：`U:…/SourceSpace.cs`、`U:…/World/MovementWorld.cs`、`U:…/NativeEyeHeight.cs`、`research/rea-native/n4/N4A-READBACK.md`、STATIC-VALUES、`research/phase2-local/m6/unity/A4-WORLD.md`、`research/phase2-local/m5/reference_config/README.md`、`tf2/expansion/titan/T0-REPORT.md`。

缺：B01-1（R5 碰撞体没量过）、B01-2（台阶 22 / 18）。

---

## 02 底层：时间步长、每帧顺序、碰撞体、地面检测、台阶、斜坡（hb-ch02）

### 资料在哪（都在 main）

| 文件 | 内容 |
|---|---|
| `research/rea-native/subsystems/N2-T-TIMING-INPUT.md` | 命令执行链；dt = 那一帧的 frametime；按钮边沿；冲量队列和"低减速"窗口（T-01 – T-05）。T-05：冲到速度上限的时间在不同帧率下差 13 % |
| `research/rea-native/subsystems/N2-G-GROUND.md` §1 | FullWalkMove 的顺序：重力半步 → 跳 / 攀 / 钩 → Walk / Air → 着地判定 → 重力半步 → 去掉法向分量 |
| `research/rea-native/NATIVE-MAP.md` §3 | 入口链（函数名有两个过时，见 §0.3） |
| `research/phase2-local/m1/M1-REPORT.md`、`m1/sampling/SAMPLING-PHASE.md` | 每帧一条命令、采样相位 |
| `research/phase2-local/SESSION-BASELINE.md`、`m0/M0-REPORT.md` | 环境；D-02 固定 120 fps 实测 |
| `research/phase2-local/FINAL-REPORT.md`（约第 73、100 行） | 为什么 Unity 固定 120 Hz |
| `R5-DIFF-ARCHIVE.md` RUD 节 | 原生着地探测 `CategorizePosition`：向下 2.0 u；向上 > 140 u/s 算离地；`airUnduckDrop` 16.5；r1237 着地边界例外（D-49） |
| `research/phase2-local/m6/unity/A4-WORLD.md` | 碰撞体 32 × 32 × 72、蹲 48 [design]、上台阶 18；能站的坡 n_z ≥ 0.7 [src] |
| `research/phase2-local/slope/SLOPE-SLIDE.md`、`slope/R6U-COMPARE.md`、`slope/tables.md` | R6 斜坡 133 次实测；R5-DIFF "R6U 斜坡滑铲五条" U-1 – U-5（D-45 / D-46） |
| `research/phase2-local/m8/r_slope/SLOPE.md` | 只测了下坡，**拟合已作废** |
| `research/phase1/Movement-Analysis.md` §8 | 站立 / 下蹲碰撞体来自 setfile `poseSettings`；half-duck |
| `tf2/TF2-MOVEMENT-SUMMARY.md` §0、`tf2/ledger/T2-REPORT.md`、`tf2/static-values/T1-REPORT.md` | TF2 每帧流程、共用底层的差别 |

### Unity 参考实现（main）

- `U:Assets/HSD/Game/Runtime/PracticeSession.cs`：`PracticeSession.CommandRate` = 120，累加器，`MaxCommandsPerFrame` = 12。
- `U:…/Abilities/_Core/SkillBody.cs`（`SkillBody.Step`）。
- `U:…/R5MotorV2.cs`、`R5MotorV2Params.cs`：`groundProbe`、`slopeMovement`、`hullBottomRadius`、`SlideRebegin`。
- `U:…/World/MovementWorld.cs`（`hullRadius` 16、`hullHeight` 72、`crouchHullHeight` 48、`stepUp` 18、`standableNormalZ`、`MaxBumps` 8；`ProbeGround`、`ProbeLedge`）、`World/WorldGeometry.cs`、`World/IMovementWorld.cs`。
- 测试：`U:Assets/HSD/R5Replay/Tests/Editor/` 的 `MovementWorldTests`、`R5MotorV2Tests`、`R6USlopeTests`、`R5ReplayTests`；`U:Assets/HSD/Game/Tests/Editor/` 的 `WorldEquivalenceTests`、`R6UGameTests`。

### 已经有什么

每帧顺序、dt、着地探测：规则和数全。斜坡滑铲 5–40° 逐命令公式（残差 ≤ 0.19 u/s）。回放基线能逐字节回归。

### 缺什么

1. **台阶 22 / 18**（B01-2）：R5 setfile `stepHeight` 22（STATIC-VALUES §1、`tf2/TF2-VS-APEX.md` 约第 104 行、T1-REPORT），Unity `stepUp` 18（TF2 的值）；没实测，R5-DIFF 没记。
2. 蹲姿碰撞体 48 是 [design]（B01-1）。
3. **tick**：R5 是可变帧时长，Unity 固定 1/120；理由只在 FINAL-REPORT，**没有 D 号，也没进 R5-DIFF §三"有意偏离"**。写手册时两边都写，建议的 D 行写进 `_notes`。
4. 不滑铲时在坡上走（非冲刺）没单独测；坡上冲刺测过（299）。
5. 能站的最陡坡 0.7 只有 [src]，没实测。

### 要不要新实测

- R5 台阶梯（18 / 20 / 22 / 24 u）+ 蹲姿头顶间隙：要，便宜（B02-1，并入 B01-1 / B01-2）。
- tick：不测，定一个 D 号写成设计偏离。
- 坡上走路：可选（B02-2）。

---

## 03 地面、空中、跳跃、时间窗口、lurch / tap strafe（hb-ch03）

### 资料在哪（都在 main）

| 题目 | 文件 |
|---|---|
| 地面 | `research/rea-native/subsystems/N2-G-GROUND.md`（G-01 – G-15）；`research/rea-native/n4/N4B-KEYTURN.md`（按键急转逐命令吻合）；`research/phase2-local/m2/ground/GROUND-MODEL.md`；`research/rea-native/n5/REFERENCE-CHANGES.md`；`research/phase2-local/m10/unity/M10D4-UNITY.md`（ground redirect） |
| 空中、跳跃 | `research/rea-native/subsystems/N2-J-JUMP-AIR.md`（J-01 – J-10：skip、antiMultiJump、extra air accel 2.0、落地减速）；`research/phase2-local/m2/air_jump/AIR-JUMP-MODEL.md`；`research/rea-native/n4/N4A-READBACK.md`（antiMultiJump 0.15 / 0.75 / 0.3，落地减速 1 s、指数 2）；`research/rea-native/n4/N4C-HOP-SLIDE.md`（超速连跳 h − 100）；`research/feel/F2-STANDING-JUMP.md`（D-55）；`research/rea-native/ledger-open/LEDGER-OPEN-5.md`、`research/rea-native/n11/N11-OPEN-ITEMS.md`（起跳朝墙推 +30，D-23） |
| lurch | `research/rea-native/subsystems/N2-L-LURCH.md`；`research/phase2-local/m3/lurch/LURCH-MODEL.md`；`research/phase2-local/m6/a1_lurch/A1-LURCH.md`；`research/phase2-local/m8/r_lurch/LURCH.md`（A+D 抵消）；`research/rea-native/n4/N4D-REMAINING.md`（截断 1100）；`research/phase2-local/m8/d_techniques/TECHNIQUES.md`（LS / RAS，D-40）；CONVAR-DEFAULTS 的 `jump_grace_*` |
| 时间窗口 | `DEFERRED-DESIGN-TODO.md` E3（跳跃缓冲，暂缓，D-09）；coyote 只有间接证据：`research/phase2-local/m9/d_library/TECHNIQUE-LIBRARY.md` §3.9（wiki 写 0.2 s）、`research/phase2-local/m10/r_grapple/GRAPPLE-M10.md`（钩上后 0.15 s 内按跳有效、0.2 s 失效）、`research/phase2-local/m10/d_library/TECHNIQUE-LIBRARY-M10.md` R-13 |
| TF2 对照 | `tf2/TF2-MOVEMENT-SUMMARY.md`、`tf2/static-values/T1-REPORT.md` |

示范条目"起跳"已经写在 [README.md](README.md#示范条目起跳普通跳)，hb-ch03 直接搬进来并核对。

### Unity 参考实现（main）

- `U:…/R5MotorV2.cs`：WalkMove（`groundNativeFriction`）、输入曲线 m(2 − m)、`AirAccelerate`、`extraAirAccel`、`JumpCommand`、`groundJumpSkipReduce`、`jumpSurfacePush`、lurch。
- `U:…/MovementConfig.cs`：`MovementConfigs.Reference()` / `Fun()`，每个参数带 `provenance` 出处。
- `U:…/Abilities/LandingSlowdown/LandingSlowdown.cs`、`U:…/Abilities/_Core/JumpArbitration.cs`。
- 测试：`R5MotorV2Tests`、`R5MotorN7Tests`、`R5MotorM3Tests`、`R5MotorJ1Tests`、`FeelReplayTests`、`R5MotorM10DTests`（`InputM10DTests`、`PadLurchM10DTests`）。

### 已经有什么

地面、空中、跳、连跳、lurch：规则和数全，代码和实测逐命令吻合，叠图齐（FEEL §3）。

### 缺什么

1. **coyote time 没实测**（B03-1）。`jump_graceperiod` 0.2 的说明文字是"从台边掉下后的额外起跳时间"，但研究只把 `graceperiodmin` / `max` 当 lurch 窗口用过，`jump_graceperiod` 的读取方没追。Unity 没有通用 coyote（钩爪的 0.2 s 是起拉前的准备时间；滑索有 `superJumpWindow` 0.2）。
2. **R5 有没有跳跃缓冲没测**（B03-2；E3 方案 4）。Unity 没有缓冲。
3. G-09（冲刺 × 1.25 对按键转向的影响）只有代码。
4. `AirMove` 本体（`airDrag` / `airFriction`）没读；实测是 0。
5. `sprintStartDelay` 等冲刺起步键"M2 没测到影响"。
6. 落地减速（J-09）只有代码，M2 没从高处跳下测过（B03-3）。连跳惩罚的开关标志 player+0x36a9 什么时候为真没读（NJ §6）。

### 要不要新实测

- R5：走下台边后第 k 条命令按跳（k = 1 – 30），同时回答 coyote 和 `jump_graceperiod`（B03-1）。
- R5：落地前 1 – 6 帧按跳，测缓冲（B03-2）。
- R5：从 300 / 500 / 800 u 高处落下测落地减速（B03-3，低）。
- 这三个是手册"时间窗口"表里的空格，其余读现有文件即可。

---

## 04 滑铲、斜坡滑铲、翻越、蹲着翻越、superglide（hb-ch04）

### 资料在哪（都在 main）

| 题目 | 文件 |
|---|---|
| 滑铲 | `research/rea-native/subsystems/N2-S-SLIDE.md`；`research/phase2-local/m2/slide/SLIDE-MODEL.md`；`research/phase2-local/m10/r_slide/SLIDE-D1-M10.md`（松蹲 400、≤ 350 结束）；`research/rea-native/n4/N4C-HOP-SLIDE.md`（冷却从开始算 2 s、侧向 41.1）；R5-DIFF RPS 节（D-47）、`research/phase2-local/rps/README.md`；D-17、D-26（退还窗口 0.201 / 0.215） |
| 斜坡滑铲 | `research/phase2-local/slope/SLOPE-SLIDE.md` + R6U（D-45 / D-46）；`research/phase2-local/m9/r_d1/D1.md`（上坡滑铲、滑铲后 SG）；DEFERRED E2（Fun 1.6 倍） |
| 翻越 / 攀爬 | `research/rea-native/subsystems/N2-M-TRAVERSAL.md`（M-01 – M-09，§7 SG 窗口第二轮）；`research/phase2-local/m3/wall_mantle/WALL-MANTLE-MODEL.md`；`research/phase2-local/m6/a2_climb/A2-CLIMB.md`；`research/phase2-local/m8/r2_revenant/REVENANT-CLIMB.md`；FEEL §6（C-1 – C-5，D-27 / D-28 / D-30） |
| 蹲着翻越 | `research/phase2-local/D72-REPORT.md` §2 – §9（R5 610 次 + Frida 195 段）、`research/phase2-local/d72/out/`；D-22、D-72、D-74、D-75；R5-DIFF "D-75" 节和 §二 "D-75 剩下的" 三行 |
| superglide | `research/phase2-local/m8/r_sg/SG.md`（原生 460；SDK FSM 388.7 / 367.42）；`research/rea-native/n11/N11-OPEN-ITEMS.md`（+30 → 402）；FEEL §6.4（D-29 → D-31 减量段，D-32）；`research/b1/B1-MANTLE-BOOST.md`（S27 翻越加速，D-20） |

### Unity 参考实现（main）

- `U:…/R5MotorV2.cs` 滑铲部分；开关在 `R5MotorV2Params`（`slideReleaseEnds`、`slideBoostRearm`、`slideSteerAccel`、`slideRebeginOnGroundChange` …）。
- `U:…/Abilities/SlopeSlide/SlopeSlideParams.cs`（M8-A 的 HSD 设计）。
- `U:…/Abilities/Climb/ClimbAbility.cs`（`ClimbParams`：`nativeTraversalStates`、`crouchEndsClimb`、`crouchedMantleTime`、`mantleExitWalkSpeed`、`superglideReducedBand`；`SuperglideMode`、`LedgeHangParams`）、`Abilities/Climb/NativeTraversal.cs`（`NativeTraversalParams`）。
- `U:…/MantleBoost.cs`（SDK FSM）、`U:…/MantleBoostS27.cs`；`World/MovementWorld.ProbeLedge`（C-1 修复）；`Abilities/Revenant/RevenantProfile.cs`。
- 测试：`NativeTraversalTests`、`MantleBoostS27Tests`、`R6USlopeTests`、`R5MotorM6Tests`、`R5MotorM8Tests`（`SlopeSlideTests`）、`R5MotorJ1Tests`。

### 已经有什么

滑铲和斜坡滑铲：规则、数、实测曲线全。蹲着翻越：时长按原生状态机。superglide 两套规则和数全。叠图在 FEEL §6、D72-REPORT。

### 缺什么

1. 翻越的触发几何没读：`AutoMantle_Try` / `AutoMantle_Search` 的距离、角度、高度，`WallClimb_Move`（N2-M §6）。Unity 的台沿探测参数是 [design]（B04-1）。
2. 复现不了或没量的：h120 蹲姿短的那种（状态 3）Unity 复现不了；h120 M 类的 S27 窗口（0.45 对 0.28 s）没改；滑铲下沉 0.19 对 0.167 s（D-70，只记录）。
3. 没测：> 40° 的坡、> 30° 的坡度折角、更高速时会不会离地（B04-2）。
4. **手册要先写清两个默认**：游戏里默认 S27 翻越加速（388.7，D-20）；测试和回放按原生（460，D-32）。
5. **过时**：N2-M §3 / §5 仍把 M-04 写成"未定"（N4D 和账本已确认窗口按时间算，约 0.1 s）；CROSSCHECK-LEDGER §2 写"未定 1"、§5 又列 11 条；N2-S 写"D = 100 要按住蹲且向前"已被 R6 更正；M8 斜坡拟合 147 + 342·sinθ 作废；B1 里"短的只在蹲下没完成时出现"被 D72 推翻。

### 要不要新实测

主体不需要。可选：Ghidra 读一次 `AutoMantle_Search`，必要时 R5 接近角 / 距离扫描（B04-1）。

---

## 05 跑墙、挂墙、二段跳、蹬墙跳；滑索、钩爪、跳板、击退 / 火箭跳、传送门（hb-ch05）

### 资料在哪

| 题目 | 文件 | 在哪 |
|---|---|---|
| TF2 跑墙 / 二段跳 / 挂墙 | `tf2/TF2-MOVEMENT-SUMMARY.md` §4、§6、§11；`tf2/wallrun/T3-REPORT.md`；`tf2/wallrun/WALLRUN-B-SPEC.md`（B 版实现规格）；`tf2/wallrun/R1-R5-WALLRUN-KEYS.md`、`tf2/wallrun/D1-D2-REPORT.md`（R5 残留键、175 高度门）；`tf2/runtime/T5-REPORT.md` §5、§8；`tf2/runtime/GAPS-1108.md`（A1 – A6 跑墙分支、B1 – B4 挂墙、C 窗户辅助）；`tf2/runtime/PRESET-DIFF-1109.md`（M-1 / M-2 / M-3，等用户定）；`tf2/TF2-REPORT.md` §4 – §7（P-01 – P-06）；`tf2/TF2-VS-APEX.md`；D-08、D-57、D-58、D-69 | main |
| HSD 自己的 M7 跑墙 | `research/phase2-local/m7/M7-A-PLAN.md`、`m7/unity/M7A-UNITY.md`、`m8/unity/M8B-UNITY.md`（墙链） | main |
| 墙跳排斥是死代码 | `tf2/ref-native-tail/REF-NATIVE-1112.md` N1（其余 12 项是武器和泰坦；那里的"drift"是导弹漂移，不是移动） | #115 |
| 跑墙剩下的补测 | `L:TF2-Research/REF-TESTS-1112.md` P1 – P3（0.5 s 计时、直角墙角、窗户辅助其他触发）；`L:TF2-Research/runtime/ref-pilot-ai/README.md`（11-12 做到一半，结果没写；原始数据 `L:TF2-Research/runtime/data/20261112_*_rp_pilot`）；`L:TF2-Research/REBUILD-GAP-1107.md`、`RESEARCH-BACKLOG-1107.md`（P-a 清单 11-07 写，已被 GAPS-1108 盖过）；`L:TF2-Research/MUST-RUN-1108.md` | 本地 |
| 滑索 | `research/rea-native/subsystems/N2-P2-GRAPPLE-ZIPLINE-PADS.md` §2（Z-01 跳离 400）；`research/phase2-local/m6/a3_zip/A3-ZIPLINE.md`、`m6/a3_zip/GRAPPLE-ZIP.md`；`m9/r_zip/ZIPLINE-A1.md`；`m10/r_zipgun/ZIPGUN-M10.md`；`m8/unity/M8A-UNITY.md` §4 | main |
| 钩爪 | N2-P2 §1、§8；`research/rea-native/n6/N6-MEASURE.md`、`n13/N13-GRAPPLE-DETACH.md`、`gn/GN-GRAPPLE-NATIVE.md`、`g6/G6-IMPACT-BOOST.md`、`n12/N12-RODEO-ROLL.md`；`research/phase2-local/m4/lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md`、`m4b/swing/SWING.md`、`m55/GRAPPLE-RANGE.md`、`m10/r_grapple/GRAPPLE-M10.md`；TF2 对照 `tf2/overnight/N6-GRAPPLE-TF2-VS-APEX.md`、`N2-GRAPPLE-BOOST.md`；D-34、D-50、D-52 | main |
| 跳板 | N2-P2 §3、§7（跳板不走冲量队列；和重力炮共用 1 s 冷却）；`research/phase2-local/m4/octane/OCTANE-PRIMITIVES.md`、`m4b/pad_rejump/PAD-REJUMP.md`、`m8/r_pad_djump/PAD-DJUMP.md`；D-10、D-43、D-68 | main |
| 击退 / 火箭跳 | `research/epg/EPG-ROCKET-JUMP.md`、`tf2/epg/T1-T7-REPORT.md` | main |
| 击退完整规格（D-77） | `research/epg/ROCKET-JUMP-A-SPEC.md`（÷100、沿连线到身体表面线性衰减、上限 1000、地面门槛 312.5、击退后 \|Δv\| × 0.003 s 内不减速）；同分支的 DECISIONS D-77 和 R5-DIFF RJA 节 | #85 |
| 传送门 | `research/rea-native/n8/N8-A-SHARED-SYSTEM.md`、`N8-B-RULES.md`（§6 各技能出口速度）、`N8-C-PHASE-NATIVE.md`、`N8-D-MEASURE.md`、`N8-E-UNITY.md`；`research/phase2-local/m10/r_wraith/WRAITH-M10.md`、`m10/r2_wraith/PORTAL-R2.md`、`m10/unity/M10W-UNITY.md`；`m4/p3_transitions/P3-TRANSITIONS.md`；D-12、D-19；`SHELVED-ABILITIES.md` | main |

### Unity 参考实现（`U:…/` 下，main，除非注明）

- 跑墙 / 蹬墙跳 / 二段跳：`Abilities/WallRun/WallRunAbility.cs`（`WallRunParams`、`WallRunRules`、`Tf2WallRunParams.B()` / `A()`，`repelTime` 0.2、`heightCutoff` 175 / −1）、`Abilities/WallJump/WallJumpAbility.cs`、`Abilities/DoubleJump/DoubleJumpAbility.cs`（`DoubleJumpRule`）、`Abilities/DoubleJumpTf2/Tf2SuperJump.cs`（`MinHeightFraction` 0.25）、`WallBounce.cs`、`Abilities/_Core/WallRunLock.cs`。**TF2 挂墙没做**（P-06）；`ClimbAbility.LedgeHangParams` 是 M7 的抓边悬挂，不是 TF2 挂墙。
- 滑索：`Abilities/Zipline/ZiplineAbility.cs`、`Abilities/ZiplineGun/ZiplineGunAbility.cs`。
- 钩爪：`Abilities/Grapple/GrappleAbility.cs`（`GrappleS21Params`：`SetGnDetach`、`impactBoost`）、`Abilities/_Core/GrappleSurface.cs`。
- 跳板：`Abilities/JumpPad/JumpPadAbility.cs`、`OctaneParams.cs`、`Abilities/PadDoubleJump/PadDoubleJumpAbility.cs`、`Abilities/_Core/InstantImpulse.cs`。
- 传送：`Abilities/DimensionalRift/DimensionalRiftAbility.cs`（`RiftParams.reuseDebounce`）、`Abilities/IntoTheVoid/`、`Abilities/PhaseBreach/`、`Abilities/Teleport/`。
- 击退：main 只有 TF2X 的 `U:Assets/HSD/Game/Runtime/Combat/CombatSim.cs` `Explode`（冲量 / 质量）。R5 原生击退在 **U#52**（`rj/knockback-a`）：`U:…/KnockbackParams.cs`、`R5MotorV2.cs`（+46 行）、`U:Assets/HSD/Game/Runtime/Combat/Epg.cs`（`EpgLauncher`、`EpgBolt`）、`U:Assets/HSD/Game/Tests/Editor/RjaKnockbackTests.cs`。
- 测试：`R5MotorTf2WallRunTests`、`R5MotorM7Tests`、`Tf2SuperJumpTests`、`R5MotorM6ZiplineTests`、`R5MotorM8Tests`（`ZiplineM8Tests`）、`GnGrappleTests`、`R5MotorM4AbilityTests`、`R5MotorM10A/B/C/WTests`、`R5MotorN8ETests`、`M10WGameTests`。

### 已经有什么

滑索、钩爪、跳板：原生规则 + R5 实测齐。TF2 跑墙：B / A 两套数值齐。挂墙：数据够照着做（GAPS B1 – B4）。击退：规格完整，但只在 #85。

### 缺什么

1. **跑墙 P-a 还有三项没实测**（B05-1）：0.5 s 计时（代码读清了，从没见到它起作用）；墙跳后马上贴另一面墙；窗户辅助的地面起跳 / 墙跳 / lurch 三种触发。
2. **墙跳排斥**（B05-2）：B-SPEC 和 Unity `repelTime` 0.2 有；GAPS A5 实测无效；#115 查出是死代码；PRESET-DIFF M-2 建议默认关。**等用户定**。
3. **快速上升时的二段跳**（B05-3）：Unity 是 √(vz² + 22500)（静态 0.25H）；TF2 实测是 vz + 150（GAPS A6）。PRESET-DIFF M-1，**等用户定**。
4. **0.5 s 计时说法不一**：TF2-MOVEMENT-SUMMARY §11、TF2-VS-APEX §5、B-SPEC 约第 38 行说"T5 已排除'离地时间'"，GAPS A4 说"代码确认是'不跳而离地'的时刻"。**以 GAPS-1108 为准**，前三份过时。GAPS §6 说"HSD 没做墙跳后打开 lurch 窗口"是错的，PRESET-DIFF 已更正。
5. 击退：EPG-ROCKET-JUMP §7 建议不做地面门槛，A-SPEC（#85）决定做，以 A-SPEC 为准；`workspace/TODO.md` 约第 126 行还写"D-56 没定"（已定为 A）。没测：被炸时正在跑墙 / 钩爪 / 滑索 / 翻越；门槛的精确值（B05-4）。
6. 传送门：离开后 1.0 s 不能再进没实测（只测到 0.5 s 时还能进，B05-5）。

### 要不要新实测

- TF2（小）：P1 – P3 由 ref-pilot-ai 做完（B05-1）。TF2 从 11-12 起每次启动都是 `no_game`，要先修。
- M-1 / M-2：不测，等用户定。
- 击退"状态中被炸"：可选（R5 或 TF2）。其余读文件。

---

## 06 动量规则、动作仲裁、输入（hb-ch06，等 03 – 05 写完）

### 资料在哪（都在 main）

| 题目 | 文件 |
|---|---|
| 动量 | DESIGN-PHILOSOPHY P3、P8、§8.2；`research/phase2-local/m4/p3_transitions/P3-TRANSITIONS.md`（传送后速度去留）；N8-B §6；N2-T §5（冲量低减速）；`research/phase2-local/m5/SKILL-RULES.md`（BoostStacking、交互规则）；`research/phase2-local/m6/M6-C-DESIGN-NOTES.md`；技巧库 `m9/d_library/TECHNIQUE-LIBRARY.md`、`m10/d_library/TECHNIQUE-LIBRARY-M10.md`；击退后的不减速窗口在 #85 |
| 仲裁 | `research/phase2-local/m8/unity/M8A-UNITY.md` §2（JumpArbitration 协议和优先级表）、`m8/unity/M8B-UNITY.md`；DEFERRED E1 / E3；D-10 |
| 输入 | N2-T §3 – §4（T-02 / T-03）；N2-G G-08 / G-09；N2-L §2.2（数字键）；`research/phase2-local/m10/unity/M10D-UNITY.md`（D2 按键独立输入、D3 跳板 lurch）；`m8/r_lurch/LURCH.md`（A+D 抵消） |

### Unity 参考实现（`U:…/`，main）

- `Abilities/_Core/SkillArbiter.cs`（`SkillArbiter`、`SkillSlotSystem`）、`SkillRules.cs`（`BoostStacking`、`SkillTraits`）、`JumpArbitration.cs`（`IJumpClaimant`、`JumpRank`、`JumpPressRecord`）、`MovementAbility.cs`（`AbilityTiming`、`CommandModifiers`）、`SpeedBoost.cs`、`IMantleBlocker.cs`、`SkillBody.cs`（`DirKeys`、`SkillInput`）、`IMotor.cs`（`R5Buttons`、`MotorInput`）、`HsdMovement.cs`、`FunFeatureParams.cs`。
- 游戏侧：`U:Assets/HSD/Game/Runtime/PracticeGame.cs`（`ReadInput`）、`TapKey.cs`、`ScriptedInput.cs`。
- 测试：`R5MotorM8Tests`（`JumpArbitrationTests`）、`R5MotorM5SkillTests`、`InputM10DTests`；Game 侧 `M10DGameTests`、`M10D4GameTests`。
- 路径注意：DEFERRED E3 和 M8A-UNITY 写的 `R5Replay/Runtime/Skills/JumpArbitration.cs` 已经搬到 `Abilities/_Core/JumpArbitration.cs`。

### 已经有什么

按键独立输入、lurch 边沿和 R5 一致。动量的单项规则齐，但散在 P3、§8.1、RJA、N8-B 各处。

### 缺什么

1. **没有一张"动量规则总表"**（哪些规则会收走速度、上限多少、豁免条件）——这正是 06 章要做的汇总。
2. Unity 的仲裁优先级是 HSD 自己设计的（M8-A）；R5 同一条命令上多个动作谁赢（翻越 / 跳 / 滑铲 / 钩爪）只在 SG 和翻越跳里零散测过（B06-1）。
3. **第一次按方向键轴值 0.5 → 0.75（T-03）**〔11-14 hb-ch06 更正：m(2 − m) 曲线和冲刺 × 1.25 在游戏 Reference / Fun 都开着，只有 0.5 这个**输入值**是回放才有（录像直送），见 06 §6.12〕原来写的是：只在回放电机里有；游戏输入 `DirKeys` 第一条就给 1，没见到实现，要核对（不用测，要定 Unity 改不改）。
4. 手柄没测（`jump_grace_controller_disable_duration` −1）。

### 要不要新实测

读文件为主。同帧仲裁：可选 R5 小测（B06-1）。

---

## 07 镜头：事件型、持续型、组合规则、力度规律（hb-ch07）

### 资料在哪

| 文件 | 在哪 | 内容 |
|---|---|---|
| `research/DESIGN-PHILOSOPHY.md` T1 – T9、§6.1 – §6.6、§9.4 – §9.5、§10 | main；§6.2 kick 表在 #122 加了两行；§6.6 在 #114 更正 | 拼接顺序、kick 表、落地强度律、持续通道、开镜、R5 没有的东西、和技能的关系 |
| `research/rea-native/camera/CAMERA-INVENTORY.md` | main（BND-02 的更正在 #93） | CAM-01 – 23、BND-01 – 03；逐条数据在 `research/rea-native/map/camera-effects.csv` |
| `research/rea-native/camera/CAMERA-REFERENCE.md` | main | 原版和 M5.5 两版全部通道的公式和数值；§3.9 合成、§8 多效果同时触发。**§3.1 眼高 64 过时**（K-4 已改 70） |
| `research/rea-native/camera/C3-CAPTURE.md` | main | 落地 kick 逐帧实测；下蹲 × 0.2 条件的更正 |
| `research/rea-native/subsystems/N2-C-CAMERA.md` | main | 反编译：punch 两组弹簧 k 65 / c 9、落地 kick、横滚汇总 |
| `research/rea-native/cam2/CAM2-CAMERA.md` | main（§5 第 6 条的更正在 #93） | K-5 起跳、K-6 翻越、K-7 滑索；§5 合成规则（D-53、D-54） |
| `research/rea-native/n10/N10-CAMERA.md` | main | 视图拼接 5 步；CAM-18 cockpit sway 只动枪模、CAM-19 在 S21 是 0；跑步晃动偏航（C-10）、滑索横滚（C-11）；D-24 |
| `research/phase2-local/m55/CAMERA-FEEDBACK.md`、`ACCEPTANCE-M55.md` | main | M5.5 设计语言（速度 FOV、位置 kick、惯性、速度线、强度设置）；D-05。现在是平行保留的旧版 |
| `research/feel/FEEL.md` §8 – §10、`research/feel/camera_compare.py` | main | 镜头叠图批次、F6 K-1 – K-4、F7 C-12 |
| `R5-DIFF-ARCHIVE.md` K-1 – K-8、C-12、CAM2、FND、D-75、§二 K-6 蹲姿 | main | |
| `DECISIONS.md` D-05、D-18、D-24、D-35、D-37、D-38、D-41 – D-44、D-53、D-54、D-67、D-68、D-71、D-72、D-74、D-75 | main | |
| `research/combat/gun-measure/F-GAPS.md` §2、§3 | #122 | 开枪没有震屏、拉栓 / 泵动动画会带镜头；真实中弹第一人称是 0 |
| 泰坦镜头：`tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md` §4、§5；`tf2/expansion/titan/kits/T-f-COCKPIT-RELOAD.md`；`tf2/expansion/titan/T0-REPORT.md` §2.4 | main | 驾驶舱、开机、弹簧刚度 / 阻尼、眼高 185 |
| `tf2/expansion/titan/feel/TITAN-FEEL.md` §2、§6.2、§7 | #118 | 泰坦第一人称手感清单 |
| `tf2/expansion/titan/full/TF2-GAPS.md` §1、§5、§6 | #98（本地也有） | 落地、舱框、走路时机 |
| `L:TF2-Research/expansion/titan/full/HANDOFF-TITAN-1107.md`、`L:TF2-Research/expansion/titan/TITAN-713-RECORD.md`、`L:TECH-REPORT-1104/泰坦设计姿态与镜头研究/B3-镜头驾驶舱开机.md`、`L:TECH-REPORT-1104/移动攻击技能与道具研究/A7-设计哲学-动画融合-镜头技能.md` | 本地 | 给人读的整理 |

注意："N8-CAM"是里程碑名（D-18），对应文档就是 CAMERA-REFERENCE；`research/rea-native/n8/` 是传送机制，和镜头无关。

### Unity 参考实现

- main：`U:Assets/HSD/Game/Runtime/Camera/Native/NativeCamera.cs`（`NativeCameraParams` 各通道开关如 `jumpPunch`、`traversalCamera`、`zipDetachPunch`；`NativeCameraFeedback`、`PunchAxis`、`PerlinNoise`）；`Camera/M55/CameraFeedback.cs`（`CriticalSmoother`、`CameraFeedbackSettings`、`CameraFeedbackDesign`）；`Camera/CameraModels.cs`（`CameraModel`、`ICameraFeedback`、`M55Camera`）；`CameraRig.cs`；`Camera/CameraFeelReplay.cs`；`U:…/NativeEyeHeight.cs`。测试 `U:Assets/HSD/Game/Tests/Editor/` 的 `NativeCameraTests`、`Cam2CameraTests`、`F7CameraTests`、`FndCameraTests`。
- 技能：`U:.claude/skills/fps-camera-design/SKILL.md` 和 `references/`（channels-and-composition、curves-and-damping、transitions-and-interrupts、verification、design-brief、toolkit），按 U#62 默认走 R5。**两处过时**：还写 DESIGN-PHILOSOPHY 在 PR #94（已合并）；规则 2 的子弹公式漏了 punch1 和 drift（和 #122 冲突）。
- 泰坦镜头（U#66 引入，U#78 最全）：`U:Assets/HSD/Game/Runtime/Titan/Camera/` 的 `TitanCamModel.cs`、`TitanCamParams.cs`、`TitanCockpitCamera.cs`（`TitanCockpitCamera : ITitanCameraLayer`）、`TitanCockpitView.cs`、`TitanCockpitFx.cs`、`TitanCockpitHud.cs`、`TitanCamKeys.cs`（`TitanBoot`）；`Titan/View/TitanCamera.cs`、`TitanGameView.cs`；调参面板 `Titan/Feel/TitanFeel*.cs`（U#83）。

### 已经有什么

拼接顺序（反编译 + 实测）；kick 表（起跳、二段跳、落地、下滑索），落地强度律（424 u/s 以下线性，424 – 1122 u/s 从 1 到 12，再快封顶 12）；弹簧（ζ 0.558，峰值 0.146 s，峰值 = 0.0771 × 冲量）；持续通道公式和范围（眼高 70 / 32、冲刺 −6、滑铲倾斜 15°、冲刺转向 2°、钩爪 / 滑索横滚、drift、冲刺 sway、翻越镜头）；强度规律（解读：平常动作 2、主动超常 4.5、退出大动作 10）；组合 = 线性相加、无优先级、无总上限（P8，CAM2 §5.1 实测）；单项开关已在 Unity。泰坦镜头 TF2 实测齐，三种底盘几乎一样。

### 缺什么

B07-1 二段跳 punch 没录像；B07-2 墙跑 punch 只有函数；B07-3 rodeo 钩爪横滚 13.9° 对公式 18.5°；蹲着翻越镜头时刻（D-72 / D-74 部分没结论）；B07-5 跑步晃动相位是推断；B07-4 拉栓带镜头只量 3 把枪；DESIGN-PHILOSOPHY §6.6 在 main 上不对（等 #114）。

### 要不要新实测

核心规则不用。墙跑镜头只有 HSD 做墙跑镜头时才要（TF2）。其余"有更好"。

---

## 08 身体动画：持枪和移动叠加、泰坦步态 / 脚 / 地形 / 惯性（hb-ch08）

### 资料在哪

| 文件 | 在哪 | 内容 |
|---|---|---|
| `research/combat/MOVEMENT-ANIMATION.md` | 原版 #97；**以 #123（`r5gap/anim`）为准** | §12 读代码：bob 不读 `bob_*` 字段、过渡 = min(旧淡出, 新淡入)、14 个 pose parameter；§13 实测：换弹 × 滑铲 / 滑索 / 钩爪、6 把枪、冲刺循环不跟速度、一个 bob 来回 = 固定距离、开火用叠加层 0。#97 版 §2、§4 已被更正 |
| `research/combat/gun-measure/hold-pose/HOLD-POSE.md` | **#95**（#123 的分支里没有这个文件） | 31 把枪 × 9 种跑法；冲刺两种持枪法；走路各枪相同（0.80 s）；蹲和滑铲同一姿态；§7 转视角枪滞后 2.44°、0.4 – 0.8 s 回到 10 % |
| `research/combat/gun-measure/report/02-draw-swap.md`、`08-states-gaps.md`、`09-unity-gap.md`；`research/combat/gun-measure/C-MOTIONS.md` | #95 | 抬枪、切枪、冲刺到开火 |
| `research/rea-native/n10/N10-CAMERA.md` | main | CAM-18：sway 只作用在枪模 |
| DESIGN-PHILOSOPHY §7.11 | main | 腰射枪身角度（D-123） |
| 泰坦：`tf2/expansion/titan/anim/TITAN-ANIM-FEEL.md`（结构、骨骼权重、腿落后 60° / 400 °/s、§4.2 约束表、§5 缺口；数据 `anim/out/weapon_sway.csv`、`walkphase.csv`、`walkevents.csv`）；`anim/ref-gait/REF-GAIT-1109.md`（播放速度 = v ÷ 地速，死区 0.15；跑片段门槛 0.45×；9° 坡、11 u 台阶）；`anim/ref-native/REF-NATIVE-1109.md`（原地转身、序列混合队列）；`anim/ref-upper/REF-UPPER-1109.md`（3P 换弹 × 1.8、踉跄）；`tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md` §2、§3 | main（#110 – #113） | TITAN-ANIM-FEEL 结论 5 的"0.95 s"已被 REF-GAIT 更正 |
| `tf2/expansion/titan/feel/TITAN-FEEL.md` §3、§5 | #118 | 舱内枪的摆动 |
| 泰坦地形 / 模型决定：D-138 – D-171、D-180 – D-187（#116）；D-172、D-188、D-189（#117）；D-92、D-98、D-111、D-127、D-136（#98） | PR | D-187 地形"到此为止" |
| `L:TF2-Research/expansion/titan/full/WALK-DEEP-DIVE.md`、`L:TF2-Research/expansion/titan/anim/REF-TESTS-1109.md`、`L:TECH-REPORT-1104/泰坦设计姿态与镜头研究/B4-身体动画.md` | 本地 | |

### Unity 参考实现

- 铁驭持枪（都在 `U:Assets/HSD/Game/Runtime/Combat/Arsenal/`）：`HoldPose.cs`（`HoldState`、`HoldWave`、`HoldBlend`、`HoldData`，U#65）；`HeldMotion.cs`（`HeldMotion`、`ReloadShow`，U#65）；`HeldModels.cs`（`HeldModelView`，独立 `GunCamera`，U#61；注释写"no sway, bob"）；`GunKick.cs`（`GunKickView`、`GunLag`，U#67）。
- 泰坦身体（U#66 引入，U#78 最全，`U:Assets/HSD/Game/Runtime/Titan/`）：`Animation/TitanBodyAnimator.cs`、`TitanBodyCore.cs`（`TerrainPlantAnchor`）、`TitanFeet.cs`（`TitanFoot`）、`TitanClips*.cs`、`TitanDims*.cs`（U#72）、`TitanWalkKeyPoses*.cs`；`Weapon/TitanGunMotion.cs`（`SpringFollower`）；地形测试场 `U:Assets/HSD/Game/Editor/TitanTerrainCourse.cs`（U#77）。

### 已经有什么

两层结构（主序列 + 程序层，相加）；手是资源，解锁后能被抢；开镜收掉程序层；切序列 smoothstep 过渡（482 次实测）；冲刺循环 0.556 s；镜头和枪同一脚步节奏，镜头零点几度、枪几度；每把枪的冲刺姿态实测表。泰坦：周期 1.133 s、起停混合 0.2 / 0.55 s、惯性 = 身体比速度慢半拍、脚 IK 踩实窗口。

### 缺什么

B08-1 R5 走路 bob 从哪来没找到；叠加层进度 / 权重、开镜横滚、手臂骨骼读不到（B08-3）；B08-2 转视角滞后只测一个转速、俯仰没测；**Unity 铁驭没有 bob 和 sway**（MOVEMENT-ANIMATION §9）；泰坦 13° 以上斜坡、轻 / 重冲刺摆动、蹲起镜头过渡（占位）、舱内炮 bob / sway（B08-4）。

### 要不要新实测

R5 转视角滞后多转速 + 俯仰：要，便宜（B08-2）。bob 来源：读代码（B08-1）。TF2 那几项先不测。

---

## 09 战斗手感：后坐、开镜、枪的重量、扩散、命中反馈（hb-ch08）

**这一章的资料几乎全在没合并的 PR 上。**

### 资料在哪

| 文件 | 在哪 | 内容 |
|---|---|---|
| `research/combat/RECOIL-VIEW.md` | #93（#95 加了 §10） | 画面和子弹的关系、回落、value 倒数、soft / hard、开镜和腰射 |
| `research/combat/ADS-CURVES.md`；数据 `research/combat/recoil-view/ADS-CURVES.tsv`、`FIT-TABLE.tsv` | #93 | FOV 走 smoothstep、枪偏移走余弦、3 把枪的开镜动画、灵敏度 |
| `research/combat/gun-measure/`：`INDEX.md`（覆盖表、Unity 该改什么）、`A-ATTACHMENTS.md`、`B-STATES.md`（空中开镜 × 2）、`C-MOTIONS.md`（换弹、切枪、近战、抬枪）、`D-EXTENSIONS.md`（射速、伤害、弹道、枪模跳动、punch roll、表尾）、`report/README.md` + `report/01 – 09`、`reload-motion/RELOAD-MOTION.md`、`reload-motion/SCREEN-TRACER.md` | #95 | 全枪械实测。**`INDEX.md` 第 9 条还建议用作废的 D-VIEWMODEL**，#99 改过来了 |
| `research/combat/gun-measure/iron-sights/IRON-SIGHTS.md`、`D-VIEWMODEL.STALE.md` | #99 | 基瞄规格、枪模 FOV 两条代码分支（D-120）、装瞄具时枪往前推；D-121 作废 D-VIEWMODEL |
| `research/combat/gun-measure/shotgun-reticle/SHOTGUN-RETICLE.md` | #103 | 霰弹准心和命中点（D-128、D-129、D-137） |
| `research/combat/gun-measure/E-MOUSE.md`、`F-GAPS.md`、`workspace/R5-GAP-TESTS-1113.md` | #122 | 鼠标下压吃 punch；开镜灵敏度按 tan 比、关镜那一帧回 × 1；子弹 = eang + punch1 + punch2 + 开镜 drift；第二组弹簧拿枪时用武器弹簧；表尾停在最后一行；蓄力线性；没有归零；枪口焰寿命 |
| `research/combat/gun-measure/B5-ADS-RECOVERY.md` | #123 | R-301 开镜回落慢 0.04 s（原因没查清） |
| `research/ui/UI-INVENTORY.md`、`UI-PLAN.md` | #102 | H-01 命中 X、H-04 霰弹命中点、H-05 累加伤害数字（都只来自脚本）；D-130 – D-135 等用户定 |
| `DECISIONS.md` / `R5-DIFF-ARCHIVE.md` 的战斗决定：瞄准后坐开镜 D-87 – D-89、后坐缩放 D-94 / D-95、换弹切枪 D-113 – D-118（#91）；枪模型 D-103 – D-105（#100）；配装页 D-124 – D-126（#101）；霰弹 D-128（#104）；D-122 / D-123 见 DESIGN-PHILOSOPHY §7.10 – §7.11 | PR | |
| `tf2/ref-native-tail/REF-NATIVE-1112.md` §3、§5 | #115 | TF2 腰射散布三角分布；punch 弹簧两条积分路径 |
| `research/combat/weapons/_shared/W-SPREAD-RECOIL.md` 等、`weapons/<族>/SYSTEM.md`、`PARAMS.md` | #90 | 武器静态记录 |
| DESIGN-PHILOSOPHY P1、P5、P6、P7、§7；`research/design-philosophy/WEAPON-FIELDS.md`、`tools/spring_sim.py` | main | 枪的重量轴、后坐可学、字段表 |
| `tf2/weapons/README.md` + 各枪页 | main | TF2 独有枪；TF2 的 `springs.txt` 没实测 |
| 泰坦炮：`tf2/expansion/titan/kits/T-f-COCKPIT-RELOAD.md`（main）；D-100、D-101（#98） | | |
| `L:TECH-REPORT-1104/移动攻击技能与道具研究/A5-瞄准-后坐-开镜.md`、`A6-枪械实测-换弹切枪持枪曳光.md`；`L:TECH-REPORT-1104/枪械模型优化/`；`L:TECH-REPORT-1104/02-复核发现的问题.md` | 本地 | |

### Unity 参考实现（`U:Assets/HSD/Game/Runtime/Combat/Arsenal/`，都在 PR 上）

U#60：`FiringCycle.cs`（`FireRateRamp`、`WeaponCharge`、`HeatDriver`）、`SpreadRecoil.cs`（`RecoilPattern`、`SpreadState`）、`ArsenalWeapon.cs`、`ArsenalHud.cs`。U#63：`ViewKick.cs`（`ViewKick`、`KickStance`）、`AdsCurves.cs`。U#65：`ReloadMoments.cs`。U#67：`GunKick.cs`。U#68：`GunSights.cs`。U#69：`GunOpticView.cs`。U#71：`ShotgunReticle.cs`（`PelletDot`）。main 上通用的命中 X 和伤害数字是 IMGUI 占位：`U:Assets/HSD/Game/Runtime/Combat/CombatHud.cs`、`CombatCore.cs`。泰坦：`Titan/Weapon/TitanCannon.cs`、`TitanReload.cs`（U#66）。

### 已经有什么

一发子弹的完整流程和次序；后坐数值范围（29 把）；图案表写法；扩散结构；开镜三层曲线；枪模 FOV 公式；换弹三个时刻（解锁用 RM-SUMMARY）；切枪先走收枪时间、掏枪中途能开火；冲刺到开火 0.14 – 0.25 s；枪模跳动和 punch roll（30 把）；配件按比例缩放字段；鼠标抵消和灵敏度、开枪 / 中弹不震屏（#122 实测）。

### 缺什么

B09-1 开镜动画只测 3 把；B09-3 蹲 / 走 / 滑铲 kick 缩放靠字段；B09-5 可变倍率第二档、Kinetic Loader、枪口焰亮度；B09-2 命中标记截图没认出来、伤害数字只有脚本；音频完全没有（A-3）；B09-4 B5 的 0.04 s；Unity 和研究的差距：`ViewKick.cs` 写鼠标抵消"未实测"所以没做（现在测到了），子弹还没加 punch1 和 drift；B09-6 TF2 铁驭枪画面弹簧没实测。

### 要不要新实测

多几把枪的开镜动画：要（R5 runner）。命中 X 截图：要（射击场打开"显示命中标记"）。音频：先定方法。其余按字段走。

---

## 10 技能设计结构、敌人 AI（hb-ch10）

### 资料在哪

| 题目 | 文件 | 在哪 |
|---|---|---|
| 技能结构 | DESIGN-PHILOSOPHY §4 P9（威力换预告、夺控短、玩家和 NPC 数值分开）、§8.3、§9.1 – §9.2；D-14（一个技能一个文件夹 + README）、D-59（PvE，机制先存档、数值以后定）；`SHELVED-ABILITIES.md`、`DEFERRED-DESIGN-TODO.md` | main |
| 41 份技能记录 | `research/combat/SYSTEM-RECORD-TEMPLATE.md`、`C0-ABILITY-FILTER.md`（保留 20、防御待定 5、参考 15、不要 6）、`A-SUMMARY.md` – `E-SUMMARY.md`、`_shared/`（26 个公共部件，控制相关：`E-STATUS-EFFECT.md`、`B-move-slow.md`、`C-DAMAGE-MODIFIERS.md`、`B-targeting.md`、`D-DECOY-AI.md`）、`<技能>/SYSTEM.md`；D-78 – D-80 | #86。**main 上 DESIGN-PHILOSOPHY 引用的 `_shared/` 文件只在这里，main 上点不开** |
| 技能实测 | `research/combat/W2-RUNTIME.md` + `w2-runtime/*.py`（move_slow、黑洞夺键 0.8 s / 限速 127 → 103、毒气对 NPC、D.O.C.、Ash 拴住） | #88 |
| 道具 | `research/combat/I0-ITEM-FILTER.md`（#87，D-84 在 #91）；`research/combat/items/I1-SUMMARY.md`、`items/_shared/`、16 份记录（#89）；`research/combat/IP2-RUNTIME.md` + `ip2-runtime/`（#92） | PR |
| 武器（含 NPC 武器） | `research/combat/W0-WEAPON-FILTER.md`、`weapons/W1-SUMMARY.md`、`weapons/npc-weapons/`；D-81 | #90 |
| TF2 铁驭技能和道具 | `tf2/expansion/PILOT-LIST.md`、`DESIGN-LIST.md`、`APEX-HANDOFF.md`；`tf2/expansion/w2/W2-REPORT.md`、`w3/W3-REPORT.md`、`apex/APEX-REPORT.md`；`tf2/weapons/`（7 把 TF2 独有枪） | main |
| 敌人 AI | `tf2/pve/README.md`；`tf2/pve/AI-SPEC.md`（设置文件、行为树、计划表三层；§7 命中和打偏规则，快速铁驭命中机会 =（强度档 + 1）× 0.125）；`BEHAVIOR-TREES.md`、`SCHEDULES.md`；`data/aisettings-resolved.tsv` 等；`tools/*.py`（#105）；`tf2/pve/AI-LIVE.md`（原生 N-1 – N-7、实测 L-1 – L-8 命中率表 / 发现时间 / 断视线；`data-live/`、`live/`，#108）；`tf2/pve/FD-RULES.md` | main |
| AI 发现进度原生规则 | `tf2/ref-native-tail/REF-NATIVE-1112.md` §2（扫描间隔 0.15 s、Near / Far 插值、外围 30°、遗忘 0.3 s / 5 s） | #115 |
| 泰坦套件（当技能看） | `tf2/expansion/titan/kits/README.md`、7 页 `ION / LEGION / MONARCH / NORTHSTAR / RONIN / SCORCH / TONE.md`、`T-a-SHIELD-OPTIONS.md`、`T-b-TITAN-VS-INFANTRY.md`、`T-f-COCKPIT-RELOAD.md`、`static/`、`TITAN-LIST.md`（main，#109）；`kits/PROJECTILES.md`、`SHARED-ACTIONS.md`、`kits/measure/`（#121）；原生补充（#115）；HSD 套件外观 `kits-design/LIGHT-HEAVY.md`（#119）、`MEDIUM.md`（#120） | |
| 本地 | `L:TF2-Research/REBUILD-GAP-1107.md`（"删 TF2 演习"）、`RESEARCH-BACKLOG-1107.md`、`MUST-RUN-1108.md`、`SCAN-1108.md` §1、`REF-TESTS-1112.md`（AI1 – AI6）、`L:TF2-Research/runtime/ref-pilot-ai/`（**AI1 – AI6 没结果**） | 本地 |

### Unity 参考实现

- main：`U:Assets/HSD/Game/Runtime/Combat/`（TF2X 占位战斗层：`CombatSim`、`Tacticals`、`Ordnance`、`Throw`、`Boosts`、`MovementItems`）；移动技能 `U:…/Abilities/_Core/`（`MovementAbility`、`SkillArbiter`、`SkillRules`、`SkillLoadoutAsset`）。
- U#53：公共框架 `StatusEffects.cs`（`StatusEffect`、`SeverityCombine`）、`MoveSlow.cs`、`DamageModifiers.cs`、`Deployable.cs`、`Placement.cs`、`TargetPicker.cs`，测试 `CombatFrameworkTests`。U#58：`Control/*`、`Systems/DecoySystem.cs`、`SkillConfig.cs`、`Resources/HSD/combat-systems.json`。U#59、U#60：道具、武器；`CombatSim.Arsenal.cs` 的 `EnemyGun` 是假人枪手，**没按 AI 规格写**。
- 泰坦套件：U#82 `U:Assets/HSD/Game/Runtime/Titan/Kits/Core/KitDefs.cs`（`AbilityDef`、`KitDef`、`KitCatalog`）、`KitHost.cs`、`KitTypes.cs`、`TitanKitHost.cs`、`Kits/README.md`；U#84 – U#86 各套件；U#87 `KitMotorBody.cs`。
- **敌人 AI：Unity 里没有任何实现**（PROJECT-STATUS-1112：研究 85 %、Unity 0 %）。

### 已经有什么

技能结构规则（状态效果、同类取最大、修正链、预告、夺控时长）+ 41 份记录；AI 三层规格 + 原生规则（打偏、散布收拢、发现进度）+ 能直接当验收数据的命中率表；7 台泰坦套件规格和实测曲线。

### 缺什么

依赖的文档全在没合并的 PR 上；B10-1 P9 证据弱；B10-2 没有跨 R5 / TF2 的统一技能模板；AI 在 Unity 是 0，寻路、出场、行为调度没有引擎无关的写法（10 章要写成规则 + 状态图）；B10-3 AI1 / AI2 没结果。

### 要不要新实测

技能结构不用（可选 R5 核对 2 – 3 个技能的预告时长）。AI：可选 TF2（目前 TF2 启动不了）。泰坦套件不用。

---

## 11 手感怎么验收（hb-ch10）

### 资料在哪

| 题目 | 文件 | 在哪 |
|---|---|---|
| 原则 | D-25（不靠真人试玩，同输入叠图比指标）、D-36（R5 为复刻核心）、D-66（回放电机到此为止，只当回归尺子）、D-70（差零点几个百分比可以不追，但要写出差多少）、D-35（`R5SharedRandom`） | main |
| 叠图对照 | `research/feel/FEEL.md` §2（指标和容差：速度 2 u/s 或 1 %、高度 1 u 或 2 %、帧数 1.5 帧；四档：一致 / 接近（3 倍容差内）/ 不一致 / 次数不同）、§6 攀爬、§8 镜头 13 个指标、§9 F6；脚本 `research/feel/feel_metrics.py`、`feel_compare.py`、`camera_compare.py`、`camera_to_trial.py`、`climb_to_trial.py`、`frida_kick_seed.js`；`research/feel/data/scorecard.json`、`trials.json`。叠图页面是 claude.ai artifact，不在 git | main |
| 回放回归和哈希 | `research/phase2-local/rud/rud_check.py`（**现行基线**，426 个文件 sha256，三个例外经用户同意）、`rud_compare.py`；`research/phase2-local/rps/README.md`、`rps_check.py`、`rps_compare.py`、`unity/baseline_sha256.json`、`before_after.md`；旧检查 `m4/unity/regression_check.py`、`m5/unity/m4_replay_check.py`；`m4b/view_check.py`、`m55/grapple_range_check.py`、`slope/r6u_compare.py`；D-47、D-49、D-66 | main |
| 流水线验收 | `research/phase2-local/m1/M1-REPORT.md` §1（A1 – A4）、`m1/acceptance/`；`m0/M0-REPORT.md`；`research/phase2-prep/run_checks.py`、`tests/`、`VALIDATION-REPORT.md`、`UNITY-DATA-CONTRACT.md`、`TELEMETRY-SCHEMA.md` | main |
| 账本 | `research/rea-native/ledger.csv`、`CROSSCHECK-LEDGER.md`、`UNITY-CHANGE-PROPOSALS.md`（历史） | main |
| M5.5 验收 | `research/phase2-local/m55/ACCEPTANCE-M55.md` | main |
| TF2 | `tf2/runtime/t5_metrics.py`、`night_metrics.py`、`night_match.py`；`tf2/TF2-VS-APEX.md`、`tf2/ledger/ledger.csv`；`tf2/runtime/PRESET-DIFF-1109.md`（Tf2 预设 3 处对不上，修复只在本地 `HSD-Unity-PRESETFIX`，没推送） | main |
| AI 验收数据 | `tf2/pve/AI-LIVE.md` L-1、`data-live/hit_*.tsv` | main |
| 泰坦验收线 | D-143、D-148（骨长偏差 5 %）、D-155（关节表面距离 ≤ 5 mm）、D-180、D-186（地形"过线"计数） | #116 / #117 |
| 泰坦 | `tf2/expansion/titan/anim/TITAN-ANIM-FEEL.md`、`anim/ref-gait/`（main）；`TITAN-FEEL.md`（#118） | |
| 本地 | `L:TECH-REPORT-1104/01-方法论和工具.md` §4"判断真假"、§6"防止改坏"；`02-复核发现的问题.md` | 本地 |

### Unity 参考实现（main，除非注明）

叠图 `U:…/FeelReplay.cs`（`FeelReplay.GameBody`）、`U:Assets/HSD/R5Replay/Editor/FeelBatch.cs`（`FeelBatch.Run`，`-preD72` / `-preGn` 等）；回放 `U:Assets/HSD/R5Replay/Editor/BatchReplay.cs`（`-legacyM2`）、`ShortRangeBatch.cs`；镜头 `U:Assets/HSD/Game/Runtime/Camera/CameraFeelReplay.cs`、`U:Assets/HSD/Game/Editor/CameraFeelBatch.cs`；预设 `U:Assets/HSD/R5Replay/Editor/PresetAssets.cs`；测试 `U:Assets/HSD/R5Replay/Tests/Editor/`（33 个 `.cs`，另有 `TestData/synthetic_*`）、`U:Assets/HSD/Game/Tests/Editor/`（33 个 `.cs`）、`U:Assets/HSD/Game/Tests/PlayMode/PracticeGamePlayModeTests.cs`；跑圈 `U:Assets/HSD/Game/Runtime/CombinationCourse.cs`、`CourseAutopilot.cs`、`M6CourseTests`；泰坦导入 `TitanImportTests`。U#87：`U:Assets/HSD/Game/Editor/TitanFeelParity.cs`、`TitanCamReference.gen.cs`、`TitanCamTests` 等。U#58 以后：`CombatControlTests`、`CombatSkillTests`、`CombatSystemsTests`（引用 W2、IP2 实测值）。

### 已经有什么

移动有"同输入叠图 + 指标容差 + 逐字节哈希回归 + 例外留档"一整套；镜头 13 个指标；TF2 和泰坦有生成的参考表。

### 缺什么

**没有合格线总表**（11 章的主要产出）；B11-1 跑圈没有 R5 参照；B11-2 技能 / 道具 / AI 没有叠图验收；枪械对照都在 PR 上；B11-3 预设修复没推送；叠图页面不在仓库。

### 要不要新实测

不用（AI 验收表可选补 AI1）。

---

## 附录 A 研究方法（hb-ch10）

### 资料在哪

| 题目 | 文件 | 在哪 |
|---|---|---|
| Ghidra 工程 | `L:ghidra-projects/r5apex.gpr`（+ `.rep`）、`r5apex_dx12.gpr`、分析日志、`r5apex-convar-dump.txt`；`L:ghidra-projects/tf2/tf2.gpr`（server.dll、client.dll） | 本地 |
| 反编译脚本 | `research/rea-native/convar-defaults/ghidra/DumpConVarRegistrations.java` + `CONVAR-DEFAULTS.md`、`README.md`；`research/rea-native/n0/CheckBounds.java`、`cmp_clients.py`、`dx12-bounds.tsv`；`research/rea-native/n1/*.java`、`n2/*.java`、`n8/*.java`；`tf2/ledger/ghidra/`、`tf2/static-values/ghidra/`、`tf2/pve/live/ghidra/AiDig.java`、`tf2/weapons/tools/ghidra/`、`tf2/runtime/gaps1108/ghidra/GapsDump.java` | main |
| 反编译方法 | `research/rea-native/N0-PILOT.md`（加壳检查、两个客户端是否相同、定标、闸门）、`README.md`、`NATIVE-MAP.md`、`REA-PLAN-DRAFT.md`、`N-REPORT.md` | main |
| TF2 原生补充 | `tf2/ref-native-tail/AiDig.java`、`vastr.py` | #115 |
| Frida | `research/feel/frida_kick_seed.js`、`research/phase2-local/d72/frida_d72_trav.js`、`research/rea-native/cam2/frida_cam2_stages.js`、`g6/frida_impact.js`、`gn/frida_hook_parent.js`、`n6/frida_grapple_detach.js`、`n10/frida_n10_camera.js`、`ledger-open/frida_zipline_roll.js`。用法只写在各报告里（`n6/N6-MEASURE.md`、GN、D72-REPORT），**没有独立方法文档** | main |
| R5 跑测流水线 | `research/phase2-local/tools/`（`agentlink.py`、`hsd_session.py`、`hsd_trial.py`、`hsd_launch.ps1`、`hsd_input.ps1`、`hsd_cvar_help.py`、`map_scan.py`）；`research/phase2-local/SESSION-BASELINE.md`、`STATUS.md`；`m0/M0-REPORT.md`、`m1/`；`research/phase2-prep/`（`LOCAL-SETUP.md`、`TELEMETRY-SCHEMA.*`、`tools/hsd_tel.py`、`hsdtel/`）；`research/phase1/mod/hsd_movediag/`、`phase1/tools/` | main |
| 战斗实测 runner | `research/combat/w2-runtime/rt_probe.py`（#88）；`research/combat/ip2-runtime/run.py`、`relaunch.sh`（#92） | PR |
| 机器轮流 | 工作区根目录 `GAME-LOCK.txt`（R5 和 TF2 共用一台机器，规则在工作区 `CLAUDE.md` 和记忆里） | 本地 |
| 源码 | `L:research-src/s21-platform`（Squirrel 脚本）、`s21-r5sdk`、`launcher` | 本地 |
| TF2 Northstar 跑测 | `tf2/mod/HSD.TF2Diag/`；`tf2/runtime/runner.py`、`r5_guard.py`、`lock_race_test.py`、`plans*.py`、`README.md`、`T5-REPORT.md`；`tf2/HANDOFF-T5.md`；`tf2/pve/live/ai_runner.py`、`tf2/weapons/tools/runner_wp.py`、`tf2/runtime/gaps1108/runner_g8.py`；每次运行 `tf2/runtime/data/<run>/`；本地 `L:TF2-Research/local/` | main / 本地 |
| 原始数据存档 | 私有仓库 HSD-RawData（本地 `HSD-RawData` 是指向 D 盘的 junction，**不要递归删除**）：`README.md`、`MANIFEST.tsv`（约 7 220 行：路径、大小、sha256、来源、恢复位置、类别）、`MANIFEST-EARLY.tsv`、`apex/`、`apex-early/`、`tf2/`、`indexes/`；规则 D-76；开着的 RawData PR #1 – #10、#20 – #22。公开仓库里的索引 `tf2/ARCHIVE-INDEX.md`、`ARCHIVE-INDEX.tsv`、`REDACTED.tsv` | RawData / main |
| 方法总结 | `L:TECH-REPORT-1104/01-方法论和工具.md`（最接近一份整体方法文档） | 本地 |

### 已经有什么 / 缺什么

工具都在，每次运行有存档，sha256 清单齐。缺：整体方法文档（BA-2）、Frida 方法文档（BA-1）；坑散在各报告（REA 打开 44 MB 的 exe 会超时，改用 Ghidra headless；R5 读 ConVar 默认值在 +0x40，TF2 在 +0x38）。**研究仓库是公开的**："只提交地址和公式，原始日志和解包文件进 HSD-RawData"（D-76）这条要在附录里写明。不用新实测。

---

## 附：盘点时发现的过时文档和矛盾（汇总）

各章写的时候以右边一列为准，并在本章的 `_notes` 里写一句。

| 文档 | 过时的说法 | 以什么为准 |
|---|---|---|
| `research/rea-native/NATIVE-MAP.md` §3 | 0x140a4a7c0 = `WallRun_Move`、0x140a36130 = `Grapple` | N2-G：`WalkMove`、`Gravity_HalfStep` |
| `research/rea-native/camera/CAMERA-REFERENCE.md` §3.1 | 站立眼高 64 | 70（R5-DIFF K-4） |
| `research/rea-native/subsystems/N2-M-TRAVERSAL.md` §3 / §5、`CROSSCHECK-LEDGER.md` §2 / §3.1 / §5 | M-04 "未定" | 窗口按时间算，约 0.1 s（N4D、账本 §6） |
| `research/rea-native/subsystems/N2-S-SLIDE.md` | D = 100 要按住蹲且向前 | R6（`SLOPE-SLIDE.md`） |
| `research/phase2-local/m8/r_slope/SLOPE.md` | 斜坡拟合 147 + 342·sinθ | 作废，用 R6U |
| `research/b1/B1-MANTLE-BOOST.md` | 短的只在蹲下没完成时出现 | D72-REPORT |
| `tf2/TF2-MOVEMENT-SUMMARY.md` §11、`tf2/TF2-VS-APEX.md` §5、`tf2/wallrun/WALLRUN-B-SPEC.md` | 0.5 s 计时：T5 排除了"离地时间" | `tf2/runtime/GAPS-1108.md` A4："不跳而离地"的时刻 |
| `tf2/runtime/GAPS-1108.md` §6 | HSD 没做墙跳后打开 lurch 窗口 | `tf2/runtime/PRESET-DIFF-1109.md` |
| `research/epg/EPG-ROCKET-JUMP.md` §7 | 建议不做地面门槛 | `ROCKET-JUMP-A-SPEC.md`（#85）：做 |
| `workspace/TODO.md` 约第 126 行 | D-56 没定 | D-56 定为 A（D-77，#85） |
| `research/combat/MOVEMENT-ANIMATION.md`（#97 版）§2、§4 | bob 按 `bob_*` 字段算 | #123 版 §12 |
| `research/combat/gun-measure/INDEX.md`（#95）第 9 条 | 用 D-VIEWMODEL | 作废（D-121，#99） |
| `research/combat/gun-measure/` 的 `C-RELOAD-SUMMARY.tsv` | `flag` 列 | 作废（D-118） |
| DESIGN-PHILOSOPHY §6.6（main） | 没有改技能 | 技能已按 U#62 改（#114） |
| `U:.claude/skills/fps-camera-design/SKILL.md` | DESIGN-PHILOSOPHY 在 PR #94；子弹公式没有 punch1、drift | 已在 main；`F-GAPS.md`（#122） |
| `tf2/expansion/titan/anim/TITAN-ANIM-FEEL.md` 结论 5 | 0.95 s | REF-GAIT-1109 |
| `research/rea-native/TODO.md`、`N-REPORT.md` §6 | 暂缓传送类 | N8 已做 |
| `research/rea-native/convar-defaults/README.md` | 209.3 没有出处 | 已有出处 |
| DEFERRED E3、`m8/unity/M8A-UNITY.md` | `R5Replay/Runtime/Skills/JumpArbitration.cs` | `Abilities/_Core/JumpArbitration.cs` |
| D-57 / D-58 正文 | `TF2-Research/wallrun/T3-REPORT.md` | 仓库里是 `tf2/wallrun/T3-REPORT.md` |
| `DECISIONS.md` | 正文提到 D-56，表里没有这一行 | 时间线正文 |
