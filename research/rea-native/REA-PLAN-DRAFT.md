# 原生移动系统地图（REA 解释层）：计划草稿

**状态**：草稿，2026-10-23，Leader 起草，等用户审阅。阶段编号用 N0–N5（N = native），避免和 M 系列、track R 混淆；正式名称由用户定。
**路径约定**：本文中 `m2/…`–`m10/…`、`static-values/…`、`tools/…` 都相对于 `research/phase2-local/`；`SDK:` = `research-src/s21-r5sdk/src/`。
**基线**：研究仓库 main `fd15ee7`（含 static-values，PR #27）；HSD-Unity main `6b27c04`（M10-R）。

## 1. 为什么做

M2–M10 的数值大多是黑盒实测：设计输入、看输出、拟合公式。这些结果可信，但有三个局限：

1. **拟合出来的公式不一定是原生公式的形状。** 在测过的范围里吻合，换一个速度、角度、帧率或者组合就可能偏。例如：
   - 斜坡滑铲的 `147 + 342·sin(slope)` 只在 29–41° 成立，截距是拟合的副产品；
   - 滑铲跳出口随滑铲时长的变化（273 / 397 / 361.5 / 350 / 236）是一张实测表，背后的规则没有找到。
2. **手感上的差一点点，往往来自没测到的细节**：分支条件、阈值、执行顺序（先摩擦还是先加速）、每帧 dt 怎么用、按键边沿怎么判。
3. **还有一批直接标着 "unexplained" 或 "rule not identified"**，见 §6 的种子清单。

所以这一轮不再一点点扫参数，而是先读原生代码，画出完整的移动系统地图，再和实测逐项对照。

## 2. 原则

- **实测仍然是真值，代码是解释层。** 代码说明"为什么"和"公式长什么样"。实测确认"游戏里确实这样"。两边都有才算定论。
- **三方对照**：每个机制都对照三样东西：原生代码 [native]、R5 实测 [meas]/[fit]、HSD Unity 现状。
- **先定标，再外推。** 已经测到 0.1 % 的东西（地面加速、重力 750、跳跃 vz、lurch 夹紧 209.3）不用重新研究。但它们是最好的定标点：先在代码里找到它们，确认读法正确，再去读还不知道的东西。
- **分清目标二进制**：

  | 二进制 | 是什么 | 用途 |
  |---|---|---|
  | `r5apex_dx12.exe`（44 MB） | S21 客户端 DX12 版。**runner 实际启动的就是它**，所有 M 系列实测都来自它 | **主目标**。Reference 跟 S21 客户端；Frida 运行时观察也只能挂它 |
  | `r5apex.exe`（38 MB） | S21 客户端 DX11 版。和 dx12 版是同一源码的两次构建（PE 时间戳相差约 9 分钟），`.text` 大小差约 230 KB，哈希不同 | 对照用。已有 Ghidra 工程和 ConVar 结果（见 §4 N0）；移动函数是否和 dx12 版逐字节相同，要在 N0 确认 |
  | `r5apex_ds.exe`（42 MB） | S3 dedi，本地服务器的权威 | 解释混合构建里客户端和 dedi 的分歧 |
  | `client.dll` / `server.dll` | SDK（社区代码） | **不逆向**，我们有源码（`research-src/s21-r5sdk`） |

  （2026-10-23 修订：初稿把 `r5apex.exe` 当主目标是错的。会话「从 rea 获取精确数值」发现实验用的是 dx12 版。）

- **SDK 钩子要剔除。** SDK 在 `CGameMovement::FullWalkMove` 前后挂了很多钩子（mantle boost、tap-strafe dedi、自动连跳、source push、wall launch、slope launch、portal 预测等，见 `SDK:game/client/move_sim_trace.cpp`）。我们实测到的有些行为来自 SDK 钩子，不是原生代码。地图要标清每个行为属于"原生"还是"SDK 改写"。
- **混合拆分规则不变**：S21 客户端和 S3 dedi 不一致时，Reference 跟 S21 客户端（社区证据支持时），标 [S21-client; local dedi differs]。
- **只读**：不改游戏文件，不 patch exe，不改 Unity。对 Reference 的修改建议只进账本，由用户决定。
- **公开仓库规则**：大段伪代码只放 `local/`，见 [README.md](README.md)。
- **范围**：只研究 S21 已有的内容。二进制里有某个函数，不等于它属于 S21 的行为（同 M9 的"脚本存在 ≠ S21"）。
- **本轮不做传送类机制**（Alter、Wraith、Loba、Ash 等），记在 [TODO.md](TODO.md)。

## 3. 已有的起点（不是从零开始）

| 起点 | 位置 | 能提供什么 |
|---|---|---|
| SDK 特征码 | `research-src/s21-r5sdk/src`，约 267 个文件调用 `LogFunAdr` | 已有名字的原生函数入口。S21 客户端日志显示 SDK 解析了 220/226 个符号（`[NETOBS-SYM] resolved 220`） |
| SDK 已命名的移动函数 | 同上 | `CGameMovement::` PlayerMove、FullWalkMove、AirMove、Jump、CheckJumpButton、Duck、TryBeginSlide、TraversalMove、CategorizePosition、SetGroundEntity、CanStandOn、CheckVelocity、CheckStuck、ApplyPlayerLaunch、SlipGetForceDir、MeleeWalkMove、FullTossMove；`CPlayer::` PlayerRunCommand、ProcessUserCmds、PhysicsSimulate、GetPlayerMoveMaxSpeed、GetRecentLandingMoveSpeedScale、IsInputCommandPressed、ClearWallRun、GrappleDetach、Zipline_*（5 个）、Player_BeginFreefall 等 |
| netvar 表 | `SDK:game/shared/s21_dt_schema.h`（2332 个字段名） | 结构体字段的名字和类型，比如 `m_traversal*`、`m_grapple*`、`m_jumpPadDebounceExpireTime` |
| 原生 ConVar | 本文件夹 [convar-defaults/CONVAR-DEFAULTS.md](convar-defaults/CONVAR-DEFAULTS.md) | 35 个移动相关原生 ConVar 的默认值和注册函数地址（`sv_*`、`skip_*`、`jump_grace_*`、`slide_*` 等），已和运行时读数核对。既是数值，也是字符串锚点 |
| setfile 键名 | `static-values/classvar-census-by-legend.csv`（158 个键） | 字符串锚点，可以顺着找到读取这些键的代码 |
| 实测模型 | `research/phase2-local/m2`–`m10` | 每个子系统的对照目标，见 §5 |

**已知的工具限制**：REA 的 Windows Ghidra 支持是实验性的，只有只读操作（25 个清单、内存和函数分析操作），**不能在 Ghidra 里改名、加注释**（见 `C:\Tools\rea\docs\windows-ghidra-p0.md`）。所以地图不存在 Ghidra 数据库里，而是存在我们自己的 CSV 和 Markdown 里。好处是只读分析可以并行。

**N0 发现的第二个限制**：REA 每次打开都会把 exe 重新分析一遍，44 MB 的客户端要约 590 s，超过 REA 的 330 s 时限，结果超时。所以 N1 起先**直接跑 Ghidra headless 脚本**，复用 `ReApex-DataAnalysis\ghidra-projects\` 里分析好的工程（见 [N0-PILOT.md](N0-PILOT.md) §3.1）。

## 4. 阶段

### N0 环境和试点（闸门）

先确认这条路走得通，再投入。

**已经完成的部分**（会话「从 rea 获取精确数值」，2026-10-23，已核对产出）：
- `r5apex.exe` 的 Ghidra 全量自动分析：**608 秒**（初稿估计"一个多小时"，偏保守）。工程在 `ReApex-DataAnalysis\ghidra-projects\r5apex.gpr`（仓库外，本机）。
- 原生 ConVar 默认值：查了 39 个名字，35 个是 ConVar 注册，读出了默认值；每个值都带字面量地址和注册函数地址。成果在本文件夹 [convar-defaults/](convar-defaults/README.md)（脚本、名字表、数值表），研究仓库 PR #28。
- **定标通过**：`sv_gravity` = 750（实测 749.91）、`jump_grace_cutoff_speed` = 1100、`skip_speed_reduce` = 100，三个已知值都对上。
- **运行时核对一致**：35 个值和运行时读数全部一致（dedi 用 `help`，dx12 客户端用 `GetConVarString`）。工具 `tools/hsd_cvar_help.py`。
- `jump_grace_*` 只存在于 S21 客户端，dedi 上没有这些 ConVar。

**还要做的**：
1. 检查 `r5apex_dx12.exe` 和 `r5apex_ds.exe`：PE 结构、节区、熵、有没有加壳或混淆。`r5apex.exe` 的分析日志里有少量"跳进不存在的内存"的反编译警告（8 处），要看它们是不是保护代码、会不会出现在移动函数里。
2. 对 `r5apex_dx12.exe` 跑 Ghidra 全量自动分析（主目标）。
3. 用 SDK 特征码找到 dx12 版的 `FullWalkMove`、`AirMove`、`Jump`，确认函数边界；再确认这些函数在 dx12 版和 `r5apex.exe` 里逐字节相同（只差地址），这样已有的 `r5apex.exe` 结果就能直接用。
4. 读出的 ConVar 值进入账本（见 §6 的定标项和新种子）。

**闸门**：
- 通过：定标值对上，自动分析能完成 → 进入 N1。
- 不通过（加壳、无法分析、定标对不上）→ 停下来报告，和用户讨论替代办法（比如运行时 dump，或者只用 Frida 做运行时观察）。

**产出**：`N0-PILOT.md`。

### N1 骨架地图

**状态（2026-10-23）：骨架完成**，见 [NATIVE-MAP.md](NATIVE-MAP.md)。2534 个函数，其中核心 553 个；ConVar 和 setfile 的读取关系都已导出；SDK 钩子 70 个；镜头清单 C1 同时完成。setfile 键是通过"描述符"读的，不是按名字查（见 NATIVE-MAP §2）。

从入口一路往下，把移动相关的函数都找出来、分类、命名（只在我们的表里）。

- 起点：`CPlayer::PlayerRunCommand` → `ProcessUserCmds` → `PlayerMove` → `FullWalkMove` → 各分支。
- 锚点：SDK 特征码、ConVar 字符串、setfile 键名字符串、netvar 名、脚本原生函数名（`player.Grapple`、`BeginJetDrive` 等）。
- 每个函数记录：
  - 客户端地址、dedi 地址（如果找到）；
  - 我们起的名字和置信度（SDK 命名 / 字符串锚点 / 调用关系推断）；
  - 所属子系统；
  - 读写了哪些 setfile 键、ConVar、netvar；
  - 对应哪个实测模型文档。
- **覆盖要求**：§5 的每个子系统都要找到入口函数，找不到的明确标"未找到"。

**产出**：
- `NATIVE-MAP.md`：调用树、子系统划分、一张总图；
- `map/functions.csv`：每个函数一行；
- `map/reads.csv`：函数 × 键/ConVar/netvar 的读写关系；
- `map/sdk-hooks.csv`：SDK 钩子清单，每个钩子改了哪个原生行为。

### N2 子系统公式提取

**状态（2026-10-23）**：P1 的六个子系统（G、L、J、S、T、M）都有文档，见 [subsystems/](subsystems/)。T 和 M 是部分完成（M 的 SG 窗口、T 的冲量来源没读通），遗留项写在各文档末尾。P2（钩爪、滑索、跳板）和镜头 C2 的第一批也已完成（`N2-P2-GRAPPLE-ZIPLINE-PADS.md`、`N2-C-CAMERA.md`）；重力炮、升降梯、JetDrive、喷气和镜头的其余效果还没读。工具：`n2/DecompileList.java` 反编译到本机 `local/`，`n2/annotate.py` 把 setfile 描述符、ConVar 和函数换成 N1 的名字。

逐个子系统读代码，用我们自己的话写出：
- 公式；
- 输入（键、ConVar、状态）；
- 分支条件和阈值；
- 执行顺序；
- dt 的用法。

每个子系统一个文件 `subsystems/N2-<名字>.md`，末尾附一张"和实测对照"的初表。子系统清单和要回答的问题见 §5。

### N3 对照账本

**状态（2026-10-23）**：见 [CROSSCHECK-LEDGER.md](CROSSCHECK-LEDGER.md) 和 [ledger.csv](ledger.csv)。P1 + P2 + 镜头第一批共 78 条：一致 45、结构差 7、数值差 2、只有代码 13、未定 11；代码和实测之间没有矛盾，差别主要在 Unity 的写法。高影响 3 条：G-07 地面转向、M-04 SG 窗口、M-08 原生 SG 和 SDK mantle boost。原因分类在原有 5 类之外加了 U（Unity 实现和原生不同）。

把 N2 的每一条结论和实测、Unity 逐项对齐，写进 `CROSSCHECK-LEDGER.md` 和 `ledger.csv`。每行：

| 字段 | 含义 |
|---|---|
| id | 例如 `SLD-03` |
| 子系统、项目 | |
| 代码 | 公式或数值 [native]/[native-inf]，加地址 |
| 实测 | 数值 [meas]/[fit]，加出处文档 |
| Unity 现状 | 参数值和代码位置，配置是 Reference 还是 Fun |
| 结论 | 一致 / 数值差 / 结构差（公式形状不同）/ 只有代码（没测过）/ 只有实测（代码没找到）/ 未定 |
| 对手感的影响 | 高 / 中 / 低 |
| 下一步 | |

**对不上的地方，先按这五类排查原因**：
1. 代码读错了（反编译歧义、内联、浮点常量用途看错）；
2. 实测条件问题（帧率、起始状态、样本太少）；
3. 混合构建分歧（S21 客户端 vs S3 dedi）；
4. SDK 钩子改写了原生行为；
5. 真正的未知 → 进 N4。

### N4 针对性验证（按需）

只针对账本里 N3 解决不了的条目。两种手段：

- **代码引导的实验**：用代码里读到的分支阈值设计实验，直接测边界两侧，不再全范围扫描。沿用现有 runner（`tools/hsd_trial.py`、`hsd_session.py`）。
- **运行时观察**（**需要用户批准**）：用 REA 的 Frida 工具在本机离线客户端上挂钩原生函数，读一条 usercmd **内部**的中间值，比如摩擦之后、加速之前的速度。这能定下"执行顺序"类的问题，也能拿到脚本读不到的 command number（M1 的老问题）。

**产出**：账本条目更新；新会话的分析文档。

### N5 汇总

- `N-REPORT.md`（中文）：地图概览、账本统计、关键发现；
- **Reference 修改建议清单**：只列建议、影响到的旧回放和演示，不实施，由用户决定；
- 更新 `STATIC-VALUES.md`（新发现的 setfile 键）和 `convar-defaults/CONVAR-DEFAULTS.md`（ConVar 的用途）；
- 对 HSD-Unity 中可以把 [fit] 升级为 [native] 的参数列表。

## 5. 子系统清单

优先级按对手感的影响排：P1 是核心移动，先做；P2 是技能类；P3 以后再说。

| # | 子系统 | 优先级 | 主要原生入口 | 要回答的问题 | 实测对照 |
|---|---|---|---|---|---|
| T | 时序和输入 | P1 | PlayerRunCommand、ProcessUserCmds、PhysicsSimulate、IsInputCommandPressed | 每条 usercmd 里各步的执行顺序；dt 怎么用（M2 发现速度带边缘的超调随 dt 变化）；按键边沿怎么判；第一条命令上轴向值为什么是 0.5；fps 依赖 | `m1/sampling/SAMPLING-PHASE.md`、`m2/ground` §4.6 |
| G | 地面移动 | P1 | FullWalkMove、Friction / Accelerate（待找）、GetPlayerMoveMaxSpeed、CategorizePosition | 低速段 lowSpeed 的分段规则；加速乘 msc、减速不乘；停止吸附阈值（实测只知道在 0.58–1.58 之间，现在假设 1）；蹲姿 1500/80（拟合值）；冲刺时序键为什么测不出效果；`sv_friction`、`sv_stopspeed` 是否参与 | `m2/ground/GROUND-MODEL.md` |
| J | 跳跃、空中、落地 | P1 | Jump、CheckJumpButton、AirMove、SetGroundEntity、GetRecentLandingMoveSpeedScale | 连跳惩罚 t0 0.15 / T 0.60 对应的 ConVar（是不是 `skip_time`）；`skip_speed_reduce` 的生效条件；`jump_grace_*`（coyote）；空中残余增益 ≈1.4e-5·vz²；落地减速 landSlowdown | `m2/air_jump/AIR-JUMP-MODEL.md` §7 |
| L | Lurch / tap-strafe | P1 | AirMove 内联部分（M3：dedi 上是原生内联） | 方向插值和 209.3 夹紧的原生写法；窗口只由跳跃打开；相反按键抵消；按键 vs 轴向的意图方向；1100 截断在客户端上是否存在；M8 b1 里 11.6 u/s 的残差 | `m3/lurch`、`m6/a1_lurch`、`m8/r_lurch` |
| S | 滑铲 | P1 | TryBeginSlide、Duck | 加成 160 和上限 460；衰减律 (s − 100·dt)·0.7^dt；加成重新可用的规则（约 1.6–2.1 s）；0.10 s 的削减（434 → 273）；0.60 s 抬到 350（`slideMaxJumpSpeed`）；松蹲后约 335 结束；坡面项；`slideRequiredStartSpeed` 等没测过的键 | `m2/slide`、`m10/r_slide`、`m8/r_slope` |
| M | 攀越、mantle、SG、墙 | P1 | TraversalMove、`m_traversal*`、ClearWallRun | SG 窗口（最后约 0.085 s）；出口 460；未解释的 402.009；mantle 跳 328.98 ≈ 1.1×299；墙跑、悬挂、墙跳（M7）；原生 mantle 和 SDK mantle boost FSM 的区别 | `m3/wall_mantle`、`m8/r_sg`、`m6/a2_climb` |
| P | 钩爪 | P2 | `player.Grapple`、GrappleDetach、`m_grapple*`（DT_GrappleData） | 拉力斜坡 50→800 / 1.5 s 和 decel 425 的原生写法；四条脱钩规则；视线离开脱钩的客户端规则；swing / retract / 绕绳状态（S21 里 `grapple_swing = false`）；Super Grapple 是否有原生依据；M10-A 里拟合的"未知原生分支" | `m10/r_grapple`、`m4b/swing`、`m4/lift_grapple` |
| Z | 滑索 | P2 | Zipline_MoveUpdateMount、MoveAlongRope、CheckAutoDetach、MoveStop | 上索锥角（33.2–35.9°）和距离（约 120 u）；空中重新上索锁定约 0.35 s；端点反向；跳离规则 | `m9/r_zip`、`m6/a3_zip` |
| F | 外力类 | P2 | ApplyPlayerLaunch、SlipGetForceDir、TT_GRAVITY_LIFT、JetDriveAccel | 跳板发射公式（拟合为 PUSH·normalize(ĥ + V·ẑ)）；升降梯每条命令 +0.0126 的爬升；Vantage JetDrive；天花板 surf（客户端和 dedi 有差异） | `m4/octane`、`m8/r_lift`、`m8/r2_vantage`、`m10/r_octane` |
| C | 第一人称镜头手感（camera feel，用户 2026-10-23 加入） | P2 | CPlayer::ApplyViewPunch、ViewPunchBase、CGameMovement::DecayPunchAngles、SetDuckedEyeOffset、EyePosition / EyeAngles（SDK 已有名字） | 随角色动作产生的**全部**镜头效果：先列完整清单，再逐个弄清触发、公式、包络和是否影响准星。详见 §5.1 | M5.5 镜头设计（`m55/CAMERA-FEEDBACK.md`，HSD 设计值）；目前没有 R5 实测 |
| X | 其他传奇移动 | P3 | 待找 | Valkyrie 喷气、Revenant 攀爬、Newcastle 跃进、Octane stim 的 msc | `m4/valk_rev`、`m8/r2_revenant`、`m10/r2_*` |

### 5.1 C 第一人称镜头手感（camera feel）

**目标**（用户 2026-10-23）：完整研究 Apex 里随角色动作产生的第一人称镜头效果，统称"镜头手感"。Respawn 代码里至少有一部分叫 ViewPunch。

- 范围是**这一整类**，不只是跑步晃动、落地震动、滑铲下沉。墙跑、攀爬、mantle、跳跃、钩爪、滑索、跳板、冲刺起停等动作时镜头的任何变化都算。
- 顺序：**先摸清一共有哪些效果、各自叫什么、由什么触发，列一张完整清单；再逐个弄清楚是怎么做的。**

**"镜头效果"的定义**：玩家没有动鼠标，第一人称画面却变了。按通道分：
- 位置：眼高、前后左右偏移；
- 角度：俯仰、偏航、横滚（roll）；
- FOV；
- 抖动（shake）。

**范围边界**：
- **在范围内**：由玩家自己的移动或动作触发的效果。
- **只登记、不深挖**：
  - 第一人称手臂和武器模型的晃动（viewmodel bob/sway）。它不是镜头，但会影响手感。清单里单独标出来，要不要研究由用户定。
  - 非移动来源：武器后坐力（`viewkick_*` 武器键、`m_vecPunchWeapon_*`）、受伤和被技能打中的 punch（例如 Newcastle 对敌人的 `ViewPunch`、伤害的 `viewPunchMultiplier`）、地图和事件引起的震动（轰炸、空投舱等）。这些只在清单里登记，以便把镜头系统的边界划清楚，不研究。

**已经找到的线索**（2026-10-23 粗查，不完整，N1 时补全）：

| 来源 | 线索 | 可能对应的效果 |
|---|---|---|
| SDK 已命名的原生函数 | `CPlayer::ApplyViewPunch`、`ViewPunchBase`、`CGameMovement::DecayPunchAngles`、`SetDuckedEyeOffset`、`EyePosition`、`EyeAngles`、`GetConvarFoVScale` | punch 的施加和衰减、蹲伏/滑铲眼高、FOV 缩放 |
| netvar（`SDK:game/shared/s21_dt_schema.h`） | `m_vecPunchBase_Angle` / `_AngleVel`（角度 + 角速度，像弹簧）；`m_punchHardAmount`、`m_punchSoftAmount`、`m_punchRandomBoost` | 移动类 view punch（落地等）的状态 |
| netvar | `m_sprintTiltFrac` / `_Vel` / `_PoseParameter` | 冲刺倾斜。带 PoseParameter，说明代码算一个值、交给动画去用 |
| netvar | `m_ziprailBankTiltFrac` / `_Vel` / `_PoseParameter`；`m_ziplineViewOffsetPosition` / `_Velocity` | 滑索倾斜、滑索视角偏移 |
| netvar | `m_leanState`；`m_updraftMin/MaxShakeActivationHeight` | 侧身状态（待确认和镜头的关系）；上升气流的震动 |
| setfile 键（census 已读到） | `grapple_rollStrength`、`grapple_rollMax`、`grapple_rollDistanceMin/Max`、`grapple_rollViewAngleMin/Max`；`ziplineViewOffset`；`mantleAngleScale`（待确认是不是镜头） | 钩爪拉动时的镜头横滚；滑索视角；mantle |
| 游戏脚本 | `ClientScreenShake` 出现在 `client/cl_player.gnut:624`、`sh_anim_events.gnut:433`、`sh_survival_freefall.gnut:2241` | 玩家相关的震动；**动画事件驱动的震动**（参数写在动画里）；跳伞 |

census 只读了 158 个预选的键，setfile 里很可能还有没读过的镜头类键。N1 要在 exe 里扫一遍 setfile 键名字符串，补全清单。

**难点：有一部分效果不在代码里，在动画资产里。**
- 带 PoseParameter 的倾斜，代码只算一个比例，镜头怎么动由动画决定；
- 动画事件可以直接触发震动；
- 第一人称镜头可能挂在动画的某个骨骼上（待 C1 确认）。

动画在编译后的 rpak 资产里，REA 读不到。这一部分只能靠**逐帧实测**拿曲线。所以镜头这一项和别的子系统不同，实测不是只用来验证代码，而是主要数据来源之一。

**研究步骤**（挂在已有的 N 阶段上，方法不变）：

| 步骤 | 阶段 | 做什么 | 产出 |
|---|---|---|---|
| C1 清单 | N1 | 从四个方向找全部效果：①原生代码，从上表的函数和 netvar 出发查 xrefs，找到客户端算第一人称视图的函数（`EyePosition` 的调用方，类似 Source 的 CalcView），把所有往镜头位置、角度、FOV 上叠加的量都找出来；②exe 里的 setfile 键名；③游戏脚本；④动画驱动的部分（只登记来源，不读资产）。每个效果记录：名字（原生名或我们起的名）、触发动作、通道、在哪里计算（原生 / 脚本 / 动画 / SDK）、参数、是不是 S21 已有 | `camera/CAMERA-INVENTORY.md`、`map/camera-effects.csv` |
| C2 逐个弄清做法 | N2 | 对代码里能读到的效果，写出：触发条件；幅度和输入的关系（下落速度、移动速度、动作类型）；包络（punch 的弹簧常数和阻尼、持续时间）；叠加和打断规则；按渲染帧还是按 usercmd 更新、和帧率的关系；**是否影响准星**（`EyeAngles` 和最终镜头角度是否不同） | `subsystems/N2-C-CAMERA.md` |
| C3 逐帧实测 | N4 | 客户端脚本能读 `CameraPosition()` / `CameraAngles()`，SDK 能读 `EyePosition` / `EyeAngles`。给 HSD.MoveDiag 加一路**按渲染帧**的镜头记录（位置、角度、FOV，以及两者之差），用现有 runner 跑脚本化的动作：站立、走、跑、冲刺起停、不同高度落地、跳跃、滑铲、墙跑、mantle、钩爪、滑索、跳板。至少两种帧率。动画驱动的效果只能这样测；代码读到的效果用它来验证 | 新会话的分析文档、实测曲线 |
| C4 对照 | N3 | 进账本（id 前缀 `CAM-`），三方对照：代码 / R5 实测 / HSD M5.5 镜头 | 账本条目 |

**和 HSD 现有镜头的关系**：M5.5 的镜头是用户试玩验收过的 HSD 设计（`m55/CAMERA-FEEDBACK.md`，HSD-Unity `.claude/skills/fps-camera-design/`），不是 R5 实测。用户的原则是每个新动作都可以有自己的镜头语言。所以这一项的结论只作为**参考和建议**进账本，不自动改 Unity 镜头，也不把 M5.5 的数值当错误。

## 6. 账本种子（N3 开工时先放进去的条目）

这些是现有文档里已经写明"没解释"或"规则未确认"的点：

| 种子 | 出处 |
|---|---|
| 连跳惩罚 t0 = 0.15 s、T = 0.60 s 对应什么 | `m2/air_jump` §7.1 |
| 空中残余增益 ≈1.4e-5·vz² | `m2/air_jump` §7.6 |
| 停止吸附阈值（假设为 1） | `m2/ground` §4.5 |
| 蹲姿减速 1500、蹲速 80（拟合） | `m2/ground` §4.3 |
| 滑铲加成重新可用的规则 | `m2/slide` §7.4、`m8/r_sg` |
| 滑铲跳 0.10 s 削减、0.60 s 抬到 350 | `m10/r_slide` |
| 斜坡滑铲的坡面项公式 | `m8/r_slope` |
| 走路起跳 SG 时出口 402.009 | `m8/r_sg` |
| mantle 跳 328.98 ≈ 1.1 × 299 | `m8/r_sg` |
| lurch b1 残差 11.6 u/s；相反按键抵消 | `m8/r_lurch` |
| 1100 截断在 S21 客户端上是否起作用（ConVar 存在、默认 1100，但没测过） | `convar-defaults/CONVAR-DEFAULTS.md`、`SDK:game/server/tapstrafe.cpp` |
| 钩爪"未知原生分支"、视线离开脱钩 | `m10/unity/M10A-UNITY.md`、`m10/r_grapple` |
| 升降梯爬升 +0.0126 / 命令 | `m4/lift_grapple` |
| 跳板发射公式 | `m4/ABILITY-TRIGGERS.md`、`m4/octane` |
| 原生 ConVar 默认值 | 已读出，见 `convar-defaults/` 和 N0 |

**N0 读出的 ConVar 已经带来的对照**（第一批账本条目，N3 正式录入）：

| 项 | 代码 [native] | 实测 | 初步结论 |
|---|---|---|---|
| lurch 强度 | `jump_grace_strength` / `jump_grace_max` = 0.7 | M3 拟合：插值权重 λ 满强度 0.7 | 一致 |
| lurch 夹紧 | `jump_grace_max` × msc × `sprintspeed` = 0.7 × 1.15 × 260（N2-L 读出） | 209.3 u/s（M3、M8：不随入口速度变化） | **一致，出处已找到**，见 [subsystems/N2-L-LURCH.md](subsystems/N2-L-LURCH.md) L-04 |
| lurch 窗口 | `jump_graceperiod` = 0.2 s（min 0.2 / max 0.5） | M3 拟合：0.2 s 内全强度，之后线性衰减到 0.5 s 为 0（±1 ms） | 一致：0.2 / 0.5 正好是 min / max |
| lurch 高速截断 | `jump_grace_cutoff_speed` = 1100 | 客户端未测；SDK dedi 用 1100 | 只有代码 |
| 连跳惩罚 | `skip_time` = 1.0 s，`skip_speed_retain` = −1，`skip_jump_height_speed` = 450 | AIR-JUMP 拟合：高度比例 clamp(0.3 + 0.7·(t − 0.15)/0.60, 0.3, 1)，0.75 s 后完全恢复 | **矛盾已消除**（N2-J）：连跳惩罚来自 setfile `antiMultiJump*`；`skip_*` 管超速削减，见 [subsystems/N2-J-JUMP-AIR.md](subsystems/N2-J-JUMP-AIR.md) J-02 ~ J-04 |
| Source 遗留值 | `sv_friction` 4、`sv_stopspeed` 100、`sv_airaccelerate` 10、`sv_maxspeed` 320 | M2：实际减速用 setfile `deceleration` | 要在代码里确认这些值还有没有被用到 |

## 7. 分工建议

- **Leader**：亲自做 N0（闸门和定标）、合并地图、维护账本、对照结论的最终核验。
- **N1**：客户端和 dedi 各派一个 Subagent，可以并行（只读分析，不会冲突）。dedi 地图只需要覆盖客户端地图里的函数，不必独立全量。
- **N2**：按子系统派 Subagent。P1 的 6 个子系统先做，可以并行。每个 Subagent 只写自己的 `subsystems/N2-*.md`，地图和账本由 Leader 合并。
- **C 镜头手感**：单独派一个 Subagent，只看客户端 `r5apex.exe`（镜头只在客户端算，dedi 没有对应部分）。C1 清单和 N1 同时做；C3 实测排在 N4，和其他游戏内实验排队。
- **N4**：游戏内实验遵守现有的单实例规则，一次只开一个游戏。Frida 运行时观察需要用户先批准。
- 分支和 PR 沿用现有规则，目标分支 `main`。

## 8. 验收标准

1. N0 定标通过（`sv_gravity` 读出 750，SDK 命名函数的边界对上）。
2. §5 的 P1 子系统全部有入口函数和公式提取文档。
3. 账本覆盖 §6 的全部种子；每条都有结论分类。
4. 已经测到 0.1 % 的定标项，代码读出的公式能逐条复现实测数值（证明读法可靠）。
5. 所有对不上的条目都有原因分类和下一步。
6. 公开仓库里没有大段反编译原文。
7. 镜头清单（§5.1 C1）里每个效果都有名字、触发动作、通道和计算位置；每个移动类效果都有公式，或者标为"动画驱动"并有逐帧实测曲线。

## 9. 风险

| 风险 | 应对 |
|---|---|
| exe 加壳、混淆或被保护 | N0 闸门先查；不通过就停下来讨论 |
| Ghidra 分析大 exe 太慢或内存不够 | 实际 `r5apex.exe` 只要 608 秒（16 GB 堆）；和游戏同时跑会抢内存，所以分析不和游戏内实验同时进行 |
| 分析的二进制和实验用的不是同一个 | 主目标改为 `r5apex_dx12.exe`；用 `r5apex.exe` 得到的结果要先确认函数相同 |
| 没有符号，只能靠 SDK 特征码和字符串锚点 | 置信度分级写进 `functions.csv` |
| 编译器内联（lurch 就是内联在 AirMove 里） | 按代码块而不是按函数做地图；标 [native-inf] |
| 反编译读错 | 每条结论都必须和实测对照；定标项先行 |
| REA Windows Ghidra 支持是实验性的、只读 | 地图存在我们自己的文件里；遇到工具问题记录下来，不硬绕 |
| 把 S21 之后的内容当成 S21 | 只对照实测过的 S21 行为；来源标清 |
| 镜头效果有一部分在动画资产里，REA 读不到 | 清单里标"动画驱动"，改用逐帧实测（§5.1 C3） |

## 10. 需要用户决定的事

1. 这一轮的正式名称（M11，还是单独的 N 系列）。
2. N4 的 Frida 运行时观察是否允许。
3. dedi（`r5apex_ds.exe`）要做到多深：只对照有分歧的函数，还是完整对照。
4. P2 / P3 子系统是否放进这一轮。
5. 节奏：N0 做完先停下来汇报，还是闸门通过就直接往下做。
6. 镜头手感（§5.1）：
   - 第一人称手臂和武器模型的晃动（viewmodel）只登记，还是也研究；
   - 是否同意为 C3 给 HSD.MoveDiag 加一路按渲染帧的镜头记录。
