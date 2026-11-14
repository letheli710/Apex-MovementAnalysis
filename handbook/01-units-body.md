# 01 单位与身体

由 hb0 写（2026-11-14）。Unity 那边的单位开关由 hb-units 做（HSD-Unity 分支 `units/switch`，draft PR，还没合并）；这一章只写规范，开关的实现以那个 PR 为准。

## 白话说明

R5 和 TF2 用的长度单位是 Source 引擎的"单位"，手册里写 **u**。1 u 就是 1 英寸（0.0254 m）。我们研究时量到的每一个数（跳 56 u 高、冲刺 299 u/s、重力 750 u/s²）都是 u。Unity 场景里看到的是米，但 HSD 的移动模拟一直在 u 下算，只在画到屏幕上时才乘 0.0254。

这一章定四件事：

1. **哪些量要换算，哪些不换**。长度、速度、加速度换；角度、时间、比例、次数不换；组合量按长度的次方换（§2）。
2. **换算系数**定为 1 u = 0.0254 m，不按功能单独调（§3）。
3. **角色身体的尺寸**：碰撞体、眼高、台阶、翻越高度，u 和 m 各写一份，再定一个"参考身高 H"，手册里所有"身高比例"都除以它（§4）。
4. **u 模式和米模式**是什么，"研究状态"就是 u 模式；R5 对照永远在 u 模式下跑（§5）。

结论先说：**现在什么都不用改**。HSD 现在就是 u 模式；米模式只保留设计，等研究和实现都完成以后再切。手册每个数同时写 `[m]` 和 `[u]`，以后切换时不需要重新查资料。

---

## 1. 两套单位和坐标

| | Source / R5 / TF2 | Unity 场景 |
|---|---|---|
| 长度 | u（1 u = 0.0254 m，即 1 英寸） | m |
| 坐标轴 | +X 前（yaw 0 时），+Y 左，+Z 上，右手系 | +X 右，+Y 上，+Z 前，左手系 |
| 换算 | — | unity = (−y, z, x) × 0.0254 |
| 偏航 yaw | + = 往左转（从上往下看逆时针） | + = 往右转；unity_yaw = −source_yaw |
| 俯仰 pitch | + = 往下 | + = 往下（同号） |

Unity 参考实现：`HSD-Unity: Assets/HSD/R5Replay/Runtime/SourceSpace.cs`（`SourceSpace.DefaultMetersPerUnit` = 0.0254，`ToUnity` / `FromUnity` / `ToUnityYaw`）。录像格式 hsdmove-trial/2 每份录像自带 `metersPerUnit`（`Trial.metersPerUnit`，默认 0.0254）。

## 2. 哪些量换算，哪些不换

**规则**：一个量的单位里长度是几次方，就乘 0.0254 的几次方。长度在分母上就是负几次方。没有长度的量不换。

### 2.1 换算表

| 类别 | u 体系单位 | 米体系单位 | 乘以 | 例子（R5 原值 [u] → [m]） |
|---|---|---|---|---|
| 长度、位置、高度、半径、距离 | u | m | 0.0254 | `jumpHeight` 56 u → 1.422 m；`mantleHeight` 80 u → 2.032 m |
| 速度 | u/s | m/s | 0.0254 | `sprintspeed` 260 u/s → 6.604 m/s |
| 加速度、重力 | u/s² | m/s² | 0.0254 | `sv_gravity` 750 u/s² → 19.05 m/s² |
| 速度增量、冲量型的"给多少速度"（击退、跳板、lurch 的加速量） | u/s | m/s | 0.0254 | `skip_speed_reduce` 100 u/s → 2.54 m/s |
| 面积、长度的平方、速度的平方（比较 v² 的门槛） | u²、u²/s² | m²、m²/s² | 0.0254² = 6.4516 × 10⁻⁴ | 速度平方门槛 300² u²/s² → 58.06 m²/s² |
| 体积 | u³ | m³ | 0.0254³ = 1.6387 × 10⁻⁵ | 触发体积 |
| 每单位长度的量（长度在分母） | …/u | …/m | 1 / 0.0254 = 39.37 | 伤害衰减 x 点/u → 39.37·x 点/m |
| 每单位速度的量 | °/(u/s)、s/u | °/(m/s)、s/m | 39.37 | 落地 kick 按下落速度缩放的斜率；空中残余增益 ≈ 1.39 × 10⁻⁵·vz²（系数单位 s/u）→ 5.47 × 10⁻⁴ s/m |
| 英尺写的键 | ft | m | 0.3048（1 ft = 12 u） | `viewkickFallDistMin` 10 ft = 120 u = 3.048 m |

### 2.2 不换算的量

| 类别 | 单位 | 例子 |
|---|---|---|
| 角度、视野 | ° | FOV 89 → 97.9（× 1.1）、`sprinttiltMaxRoll` 2°、kick 的俯仰角 |
| 角速度、角加速度 | °/s、°/s² | 泰坦键盘转向 210 °/s、kick 往弹簧写的俯仰角速度 |
| 时间 | s | `antiMultiJumpTimeMax` 0.75 s、下蹲过渡 0.4 s |
| 频率、"每秒多少"的速率 | 1/s、Hz | 冲刺眼高下沉速率 1.25 /s、`sv_friction` 4（1/s）、`sv_airaccelerate` 10（1/s，乘的是想要的速度） |
| 弹簧常数（作用在角度上） | 刚度 1/s²、阻尼 1/s | `punch_pilot` 刚度 / 阻尼 65 / 9 |
| 比例、倍率、系数、指数 | × | `antiMultiJumpHeightFrac` 0.3、移动倍率 1.15、`landSlowdownTimePower` 2 |
| 每秒衰减的比例 | ×/s（写在指数上） | `slideVelocityDecay` 0.7（速度 × 0.7^dt） |
| 次数、帧数、计数 | 个 | 连发数、弹匣容量、命令数 |
| 质量、伤害、血量、护甲 | kg 或游戏内点数 | `physicsMass` 3000、伤害 |

### 2.3 容易弄错的组合量

- **"速度 ÷ 长度"不换算**。例：`slide_step_velocity_reduction` 10 的意思是"上一级台阶，速度减 10 × 台阶高度"，单位是 (u/s)/u = 1/s，换成米以后数还是 10。
- **"想要的速度 × 系数"的加速度**（Source 的 `accelerate`）：系数 1/s 不换，乘的那个速度换。
- **拟合出来的经验式**要先写清系数的单位，再换。例：空中残余增益 Δv ≈ k·vz²，Δv 是 u/s、vz² 是 u²/s²，所以 k 的单位是 s/u，换成米要**除以** 0.0254。
- **速度平方的门槛**乘 0.0254²，不是 0.0254。
- **英尺写的键**（R5 setfile 里少数几个，比如落地 kick 的 `viewkickFallDistMin` / `Max`）先 ×12 到 u，原生代码就是这样乘的（`research/rea-native/subsystems/N2-C-CAMERA.md` §2）。
- **角度不换，但"角度对应的弧长"要换**：比如"准星偏移 x 度"不换，"在 1000 u 外偏多远"要换。

### 2.4 对照表放在哪

- 上面的 §2.1、§2.2 就是换算对照表的原件。
- hb-tables 会在 `tables/` 下按这里的规则生成机器可读的 `units-conversion.tsv`（每一行：类别、u 单位、m 单位、乘数、例子），参数总表的每一行都要有"类别"一列，由它决定怎么换。表名和列名以 hb-tables 的为准。
- 新加一个量时：先在这里找到它的类别；找不到就写进 `_notes/<会话名>.md`，由整合会话补进这一节。

## 3. 换算系数怎么定

### 3.1 结论

**1 u = 0.0254 m，固定，不按功能、不按角色单独调。**

### 3.2 理由

1. **这是 Source 系引擎的约定**：Source、TF2、Apex 的"单位"都按 1 英寸设计，关卡、武器射程、移动数值都按这个尺度做。
2. **研究数据全按这个系数存**：HSD 的录像格式（hsdmove-trial/2）、`SourceSpace.DefaultMetersPerUnit`、Unity 测试（`R5ReplayTests` 里断言 `metersPerUnit` = 0.0254）、所有对比报告。换一个系数就要重算所有对照数据，得不偿失。
3. **按身高核对，结果合理**（§3.3）。

### 3.3 按身高核对

| 量 | R5 原值 [u] | × 0.0254 [m] | 核对 |
|---|---|---|---|
| 站立碰撞体高度 | 72 u | 1.829 m | 成年男性偏高个子（Apex / TF2 都是英雄体型） |
| 站立眼高 | 70 u | 1.778 m | 真人眼高约为身高的 93–94 %，反推身高约 1.89–1.91 m |
| 蹲 / 滑铲眼高 | 32 u | 0.813 m | 真人蹲姿眼高约 1.0–1.2 m；R5 更低，是为了滑铲时贴地的速度感 |
| 冲刺速度上限（空手） | 299 u/s | 7.59 m/s ≈ 27.3 km/h | 接近短跑运动员的平均速度，属于"超人但不离谱" |
| 起跳高度 | 56 u | 1.42 m | 远高于真人（约 0.5 m），游戏里的设计值 |

结论：用 0.0254，角色身高在 1.83–1.91 m 之间，眼睛比真人略高（眼高 / 碰撞体高 = 0.97，真人约 0.93）。这是游戏的惯例（镜头放在碰撞体顶部附近，能翻上去的台子就能看见上面），不是系数错。**不为了让眼高"像真人"去改系数**：改系数会让 1.42 m 的跳跃、7.6 m/s 的冲刺一起变，而这些在 R5 里是按 u 调好的。

如果以后 HSD 想要"更像真人"的比例，应该改**眼高本身**（写成和 R5 不同的设计，进 R5-DIFF），而不是改换算系数。

### 3.4 什么时候会用到别的系数

- 只有一种情况：**导入外部美术资源**（Blender 模型、动作捕捉），它们本来就是米。导入时按米放，不经过 0.0254。
- 泰坦等更大的身体**不改系数**，用自己的尺寸（§4.3），身高比例按自己的 H 算。

## 4. 角色身体

### 4.1 参考身高 H

手册里所有"身高比例"一列都除以 **H = 72 u（1.829 m）**，即 R5 铁驭（Apex 传奇）的站立碰撞体高度。

为什么用碰撞体高度，不用眼高：碰撞体决定"能不能钻过去、能不能翻上去"，是关卡尺度的基准；眼高随站、蹲、冲刺变，不适合做基准。72 u 这个数本身还没有在 R5 里直接实测（§4.2 第 1 行），以后如果测出来不是 72，所有比例都要重算一次，所以比例列**只当辅助**，原值以 `R5 原值 [u]` 列为准。

### 4.2 R5 铁驭的身体尺寸

| 量 | [m] | R5 原值 [u] | 身高比例 | 依据和说明 |
|---|---|---|---|---|
| 站立碰撞体 宽 × 深 × 高 | 0.813 × 0.813 × 1.829 m | 32 × 32 × 72 u（半宽 16） | 0.444 × 0.444 × 1 H | [设计] Source 默认尺寸，HSD 一直这样用（`MovementWorld.hullRadius` 16、`hullHeight` 72）。R5 的真实值在 setfile `poseSettings` 里，**没读出来** |
| 蹲姿碰撞体高度（HSD 现在用的） | 1.219 m | 48 u | 0.667 H | [设计] `MovementWorld.crouchHullHeight` 48，代码注释写明"R5 duck hull not measured" |
| 空中松开下蹲时原点下降 `airUnduckDrop` | 0.419 m | 16.5 u | 0.229 H | [实测] M5（M3 e8 / e3 slide350，8 次）；头不动、脚往下 |
| 由上一行推出的蹲姿碰撞体高度 | 1.410 m 或 0.991 m | 55.5 u 或 39 u | 0.771 或 0.542 H | [推断] 如果"原点下降 = 站立高 − 蹲高"，蹲高 = 72 − 16.5 = 55.5；如果是 half-duck 那种"差的一半"（SDK `VHalfDuckZipParity` 注释），蹲高 = 72 − 33 = 39。**两种都和 HSD 的 48 对不上**，见 99-TODO |
| 下蹲到碰撞体变矮要按住多久 `hullCrouchTime` | — | 0.2 s | — | [实测] M5；R5 录像里"已蹲下"标志在 0.21–0.24 s 后亮 |
| 站立眼高 | 1.778 m | 70 u | 0.972 H | [数据] setfile `viewheight` (0, 0, 70)，N4-A 运行时读回 |
| 冲刺时眼高 | 1.626 m | 64 u（70 − 6） | 0.889 H | [数据] `sprintViewOffset` −6；[实测] C3 冲刺中量到 64（旧版把它当成了站立眼高，R5-DIFF K-4） |
| 蹲 / 滑铲眼高 | 0.813 m | 32 u | 0.444 H | [实测] C3 |
| 下蹲眼高过渡（站 ↔ 蹲） | — | 0.4 s；滑铲时 0.2 s | — | [反编译] `Duck` 计时器；[实测] C3 滑铲下沉 0.208–0.213 s；形状按 smoothstep 拟合，±1 u [推断] |
| 冲刺下沉的时间 | — | 冲刺开始 0.16 s 后以 1.25 /s 下沉；停止 0.11 s 后以 6.67 /s 回来 | — | [实测] N6 / N10 镜头录像，3 次以内差 0.01 s |
| 台阶高度 `stepHeight`（R5） | 0.559 m | 22 u | 0.306 H | [数据] setfile census |
| 台阶高度（HSD 现在用的） | 0.457 m | 18 u | 0.250 H | `MovementWorld.stepUp` 18，等于 **TF2** 的 `stepheight` 18，**不是 R5 的 22**；R5-DIFF 里没有这一条。交给 hb-ch02 核对（99-TODO） |
| 翻越最大高度 `mantleHeight` | 2.032 m | 80 u | 1.111 H | [数据] setfile，N4-A 读回 |
| 起跳高度 `jumpHeight` / 滑铲跳 `slideJumpHeight` | 1.422 m / 1.270 m | 56 u / 50 u | 0.778 / 0.694 H | [数据] [实测]，见 README 示范条目 |
| 可站立的最陡坡（地面法线 z ≥） | — | 0.7（约 45.6°） | — | [数据] SDK `slope_launch_math.h`；`MovementWorld` 同 |
| 坡上碰撞体底部按圆底算的半径 `hullBottomRadius` | 0.406 m | 16 u | 0.222 H | [实测] R6，R5-DIFF U-2（D-45 / D-46） |

### 4.3 别的身体（对照用）

| 身体 | 眼高 [u] | 碰撞体 [u] | 台阶 [u] | 依据 |
|---|---|---|---|---|
| R5 铁驭 | 70（冲刺 64，蹲 32） | 32 × 32 × 72 [设计] | 22 | 上表 |
| TF2 铁驭 | 60（冲刺下沉 6） | 没读 | 18 | `tf2/expansion/titan/T0-REPORT.md` §2.4；`tf2/static-values/T1-REPORT.md` |
| TF2 泰坦（3 种底盘） | 185（Stryder 蹲 125） | 宽 120，高 235 | 80 | T0-REPORT §2.4、§1；`titan_base.set` |
| HSD 泰坦（全部模型） | 185 | 按底盘（`TitanDims`，HSD-Unity PR #72，还没合并） | 80 | 设计规范见第 08 章 |

泰坦的身高比例按它自己的 H 算（建议 H_titan = 235 u），不要除以 72。

## 5. u 模式和米模式

### 5.1 定义

| | **u 模式（研究状态）** | **米模式（保留设计，现在不用）** |
|---|---|---|
| 参数存什么 | R5 原值，单位 u、u/s、u/s² | 米：m、m/s、m/s² |
| 模拟在什么单位下算 | u（双精度，`R5MotorV2`、`MovementWorld`、`PracticeMap` 都是 u） | m |
| Unity 场景 | 显示时 × 0.0254（`SourceSpace`） | 不再乘，直接是米 |
| 调参面板、日志、HUD 速度 | 显示 u（可以另外显示 km/h，`PracticeSession.Kmh`） | 显示 m |
| R5 对照测试、回放对比 | **只能在这个模式下跑** | 不允许跑（先切回 u 模式） |
| 什么时候用 | 现在，直到研究和实现都完成 | 用户决定切换以后 |

"研究状态"就等于 u 模式：所有参数是 R5 原值（或 R5-DIFF 里记过的 HSD 设计值），单位是 u，回放基线和测试都能直接跑。

### 5.2 对开关的要求（给 hb-units，实现以 HSD-Unity `units/switch` 为准）

1. **一键回到研究状态**：一个开关把单位、参数全部恢复成 u 模式的 R5 参考值，不需要逐项改。
2. **随时看得出当前是哪个模式**：游戏里、调参面板、日志文件头、测试输出都要写出当前模式。
3. **R5 对照永远在 u 模式下跑**：回放对比、R5 对照测试在米模式下要直接报错，不能悄悄换算以后再比。
4. **切到米模式时数值完全等价**：切换那一刻，每个参数 = u 值 × §2 的乘数。切换前后同一个回放的结果在浮点误差以内一样。之后在米模式下调的新值，要能反算回 u 存档。
5. **用米的地方都要标出来**：变量名、字段、表格列、文档都标 `[m]`；u 标 `[u]`（README 写法规范第 4 条）。
6. **对照表只有一份**：换算乘数从 §2 的类别来，代码里不要散写 0.0254；Unity 现在已经统一用 `SourceSpace.DefaultMetersPerUnit`，新代码也照这个做。

### 5.3 现在要注意的事

- HSD-Unity 里有少数地方已经混着用米（例如 `R5MotorM9CTests` 里 `echoRange = 40 * 39.37`，意思是 40 m 换成 u）。这种写法要带注释标 `[m]`，hb-units 盘点时一起找出来。
- 泰坦、枪模、美术资源是按米导入的（§3.4），它们和 u 体系的接口（比如眼高 185 u、枪模位置）要在第 08、09 章写清楚哪一边是哪个单位。

## 6. 出处

- `HSD-Unity: Assets/HSD/R5Replay/Runtime/SourceSpace.cs`：坐标轴和 0.0254。main
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/World/MovementWorld.cs`（`hullRadius` 16、`hullHeight` 72、`crouchHullHeight` 48、`stepUp` 18，注释"R5 duck hull not measured"）；`research/phase2-local/m6/unity/A4-WORLD.md`（"32 × 32 × 72 standing, 48 crouched [design]"）。main
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/NativeEyeHeight.cs`（`NativeEyeParams`：站 70、蹲 32、冲刺 −6、过渡 0.4 / 0.2 s、冲刺下沉时间）。main
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/R5MotorV2Params.cs`（`airUnduckDrop`、`hullCrouchTime`、`hullBottomRadius`）；`research/phase2-local/m5/reference_config/README.md`（16.5 u 的实测）。main
- `research/rea-native/n4/N4A-READBACK.md` §2：`viewheight` (0, 0, 70)、`mantleHeight` 80。main
- `research/phase2-local/static-values/STATIC-VALUES.md` §1、§2：`stepHeight` 22、`jumpHeight` 56、`sprintspeed` 260、移动倍率 1.15。main
- `research/rea-native/subsystems/N2-C-CAMERA.md` §2、眼高一行：英尺 ×12、`Duck` 计时器 400 / 200 ms。main
- `R5-DIFF-ARCHIVE.md` K-4（眼高 64 → 70）、U-2（圆底 16）。main
- `research/phase1/Movement-Analysis.md` §8：碰撞体来自 setfile `poseSettings`，half-duck 存在。main
- `tf2/static-values/T1-REPORT.md`（TF2 `stepheight` 18、`jumpheight` 60）、`tf2/expansion/titan/T0-REPORT.md` §2.4（TF2 铁驭眼高 60、泰坦 185 / 蹲 125、宽 120 高 235）。main
- SDK `research-src/s21-r5sdk/src/core/init_server.cpp`（`VHalfDuckZipParity` 注释里的 (standHull − duckHull) × 0.5）。本地，不在这个仓库
- [反编译] 眼高 `ViewHeight?` 0x140a53f30、`Duck` 0x140a54080、`Sprint_ViewOffset` 0x140af2370。
