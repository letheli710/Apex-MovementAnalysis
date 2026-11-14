# 02 底层：时间步长、每帧顺序、碰撞体、地面检测、台阶、斜坡

由 hb-ch02 写（2026-11-14）。分支 `handbook/ch02`，还没合并。研究仓库 main = `86ec5f1`，HSD-Unity main = `17260f2`。

## 白话说明

这一章讲移动系统最底下的一层：**身体每一步怎么往前算、身体是个什么形状、它站在什么上面**。上面几章的跑、跳、滑铲、翻越、跑墙全都建在这一层上；这一层错了，上面每个数都会跟着偏。

读完这一章，应该能写出这样一个"空的"移动底层：

1. 一个**固定频率的命令循环**：不管画面是 30 帧还是 240 帧，身体都按每秒 120 条命令往前算，每条命令时长固定 1/120 s（§2.1）。
2. 每条命令里**固定的先后顺序**：读输入 → 看脚下 → 算速度 → 走一步 → 和墙地碰撞 → 判断落地（§2.2）。
3. 一套**和帧率无关的积分写法**：重力分两个半步、衰减写成"底数的 dt 次方"、时间窗口按秒算（§2.3）。
4. 一个**竖直的方盒碰撞体**：站着 32 × 32 × 72 u，蹲下 48 u 高；坡面上底部按半径 16 的圆底算（§2.4、§2.8）。
5. **扫掠碰撞**：每一步从起点到终点扫过去，撞到面就停在面上、去掉撞向面的速度，多快都穿不过墙（§2.5）。
6. **地面检测**：脚下 2 u 以内有能站的面、而且在往下走，就算落地；脚下的面一下子低了 2 u 以上，就算离地（§2.6）。
7. **上台阶**：比脚高不超过 18 u 的顶面不挡路，直接踩上去。R5 的值是 22 u，HSD 现在用的是 TF2 的 18 u，这是一处没有定下来的差别（§2.7）。
8. **斜坡**：法线 z ≥ 0.7（不陡于约 45.6°）的面能站，更陡的当墙；坡上速度保持水平，位置沿着坡走（§2.8）；下坡和凸转折处贴着坡走，平地的台边照样掉下去（§2.9）。

**和别的章怎么分界**：地面加速、摩擦、空中加速、起跳的数在第 03 章；滑铲（包括斜坡上的滑铲加速）在第 04 章；跑墙、天花板滑行（ceiling surf）、钩爪等外力在第 05 章；镜头怎么跟着平滑在第 07 章。本章只写它们共用的那一层，用到它们时只写"在哪一章"。

**一句话结论**：HSD 的底层大部分已经按 R5 做对了，而且有逐字节的回归测试守着。还没定的有三处：**台阶高度 18 / 22**、**蹲姿碰撞体高度**、**固定 120 Hz 这个设计偏离还没有 D 号**。另外读代码时发现两处 HSD 和 Source / R5 写法不同、R5 也没测过的地方（落地判断要求竖直速度向下；空中也能"迈上"18 u 以内的台面），都写在下面对应的条目里，并列进 `_notes/hb-ch02.md`。

### 本章出处缩写

| 缩写 | 文件 |
|---|---|
| NT | `research/rea-native/subsystems/N2-T-TIMING-INPUT.md` |
| NG | `research/rea-native/subsystems/N2-G-GROUND.md` |
| M1S | `research/phase2-local/m1/sampling/SAMPLING-PHASE.md` |
| GM | `research/phase2-local/m2/ground/GROUND-MODEL.md` |
| A4 | `research/phase2-local/m6/unity/A4-WORLD.md` |
| R6 | `research/phase2-local/slope/SLOPE-SLIDE.md` |
| DIFF | `R5-DIFF-ARCHIVE.md` |
| DP | `research/DESIGN-PHILOSOPHY.md` |
| SV | `research/phase2-local/static-values/STATIC-VALUES.md` |
| MA | `research/phase1/Movement-Analysis.md` |

Unity 路径前缀 `U:` = HSD-Unity 仓库；`U:…/` = `Assets/HSD/R5Replay/Runtime/`（同 00-INVENTORY §0.1）。Unity 的数全是 [u]。

### 参考实现是哪一个

本章说的"Unity 参考实现"都指**游戏身体的 Reference 配置**：`MovementConfigs.Reference()` 建出来的 `SkillBody`（`R5MotorV2` + `R5MotorV2Params.R5Reference()` + 本章的开关）+ `MovementWorld`。不是 M1 的 `ReferenceMotor.cs`。

还有一个"回放电机"（`R5MotorV2Params.R5Reference()` 单独用，回放 R5 录像当尺子），它是**平地电机**：`slopeMovement` 关、`hullBottomRadius` 0，没有世界碰撞。回放电机到此为止不再换规则（D-66）。本章写的斜坡、碰撞、台阶都只在游戏身体里。

---

### 2.1 时间步长：固定 120 Hz 命令

#### 原理

移动手感要和画面帧率无关：同样的手上操作，60 帧的电脑和 240 帧的电脑跑出来的路线应该一模一样，否则练出来的连招到别人机器上就不灵了（DP P4"技巧窗口按时间算"，T8"精确积分、帧率无关"）。

R5 自己的做法是**每画一帧发一条命令，命令时长就是那一帧的时长**，所以 R5 的移动其实随帧率有一点点变化。HSD 改成**固定频率的命令**：身体只按整条命令往前算，每条命令永远是 1/120 s。画面帧率只决定"这一帧要算几条命令"和"画面插值到哪儿"，不影响身体的轨迹。这是 HSD **有意和 R5 不一样**的地方。

为什么是 120：R5 研究的录像大多是客户端固定 120 fps 录的（D-02），用同样的步长回放误差最小；60 Hz 下连招链会漂移约 35 u/s（M5），太粗。

#### 规则和公式

1. 命令时长 dt = 1 / `CommandRate`，固定。身体的时钟 `time` 每条命令加 dt，所有"距离某事件多久"都用这个时钟（§2.3 第 4 条）。
2. 每个画面帧：累加器 acc += 帧时长；只要 acc ≥ dt 就跑一条命令、acc −= dt，最多跑 `MaxCommandsPerFrame` 条。
3. **卡顿**：一帧里跑满上限还剩 ≥ dt，就把剩下的时间扔掉（acc = 0）。身体会"慢一下"，但不会越补越多。
4. **插值**：画面上的身体位置 = 上一条命令后的位置和这一条命令后的位置之间，按 α = acc / dt 线性插值。两者相距超过 `TeleportNoInterp`（传送、重生）时不插值，直接用新位置。画面因此比模拟晚最多一条命令。
5. **输入采样**：鼠标视角每个画面帧读一次；同一帧里跑的几条命令用同一个视角。按键的"按下"在画面帧里先锁存，交给这一帧的第一条命令（这样两条命令之间的短按也不会丢）；"按住"每条命令都重新读。锁存只是把两条命令之间的短按变成"这条命令按着"；**按下沿仍只按 §2.2 第 0 步算**（按钮 & ~上一条的按钮），一直按着的键不会产生新的按下沿（重建检验 11-14 补，`rebuild-test/judge/REPORT.md`）。
6. R5 原值：dt = 客户端那一帧的 frametime（每帧一条命令）。研究录像的帧率：M1 / M2 144 fps ± 3 %（dt 6.7–7.2 ms），M3 起 120 fps ± 3 %。

| 量 | [m] | 原值 | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 命令频率 `CommandRate` | — | HSD 设计值 120 /s | — | 60 /s 太粗（连招漂移 ~35 u/s）；更高可以，但回放对照要重做 | [设计]，M5 |
| 命令时长 `CommandDt` | — | 1/120 s = 8.333 ms | — | — | [算] |
| R5 每条命令的 dt | — | = 那一帧的 frametime；研究里 6.7–7.2 ms（144 fps）或约 8.3 ms（120 fps） | — | 随帧率 | [反编译] NT §2，[实测] M1S、GM |
| 一帧最多跑几条命令 `MaxCommandsPerFrame` | — | HSD 设计值 12 条（= 0.1 s） | — | — | [设计] |
| 不插值的跳变距离 | 5.08 m | HSD 设计值 200 u | 2.78 H | 大于一条命令能走的最大距离即可 | [设计] |

#### 实现模板

```
// 单位：u、s
const dt = 1.0 / CommandRate            // 1/120
acc = 0

every rendered frame (frameDt):
    view = readMouse()                  // 每帧一次
    latchPresses()                      // GetKeyDown → latch
    acc += frameDt
    n = 0
    while acc >= dt - 1e-12 and n < MaxCommandsPerFrame:
        input = buildCommand(view, held keys, latched presses)   // latch 只给第一条命令
        clearLatches()
        body.step(input, dt)            // §2.2
        acc -= dt; n += 1
    if n == MaxCommandsPerFrame and acc >= dt: acc = 0   // 卡顿：丢掉
    alpha = acc / dt
    renderPos = (|cur - prev| > 200) ? cur : lerp(prev, cur, alpha)
    camera.update(renderTime, renderPos, view)  // 第 07 章：镜头的状态只在命令上更新（每条命令 Observe 一次），这里只在两条命令之间插值
```

Unity 参考实现：
- `U:Assets/HSD/Game/Runtime/PracticeSession.cs`：`PracticeSession.CommandRate` = 120、`CommandDt`、`MaxCommandsPerFrame` = 12、`Advance(frameDt, input)`（累加器、卡顿）、`Alpha`、`RenderPos()`（插值，200 u 不插值）、`RenderTime`。
- `U:Assets/HSD/Game/Runtime/PracticeGame.cs`：`Update()` 读鼠标、锁存按键、调 `Session.Advance(Time.deltaTime, …)`；`ReadInput()` 每条命令建一次输入并清掉锁存；`LateUpdate()` 用 `Session.RenderPos()` 和 `RenderTime` 更新镜头。
- 回放电机按录像里每条命令自己的 dt 走（R5 的做法），不经过这个循环。

#### 验收

- `U:Assets/HSD/Game/Tests/Editor/PracticeGameTests.cs`：
  - `SameCommandsAtAnyFrameRateGiveTheSameState`（30 / 60 / 75 / 144 / 240 fps，每帧时长再随机 ±20 %）：同样的命令数下位置、速度**逐位相同**。
  - `AdvanceAccumulatesAndInterpolates`：5 ms 一帧时 α = 0.6 → 0.2；插值点在前后两个位置之间；一帧 1 s 只跑 12 条、α 归零。
- `U:Assets/HSD/Game/Tests/Editor/MovementDemoTests.cs` `DemoIsFrameRateIndependent`：每个动作演示在两种随机帧率下逐命令位置、速度、事件相同，结论相同。
- 合格线：逐位相同。任何一个数不同就是有代码在模拟里读了画面帧时长。

#### 出处

- NT §1、§2、T-01：每条 usercmd 带自己的 frametime，dt = 那一帧的时长；时钟 curtime = tickbase。main
- M1S §2.1：帧数和命令数之比 0.9918，每帧一条命令。main
- GM 第 6 条限制：dt 6.7–7.2 ms，按速度段选加速度让"冲到上限的时间"随 dt 变 0.145–0.167 s（13 %）。main
- DECISIONS D-02：M3 起客户端固定 120 fps。main
- `research/phase2-local/m5/M5-REPORT.md` §6、`research/phase2-local/FINAL-REPORT.md` §3：60 Hz 连招漂移约 35 u/s，所以游戏固定 120 Hz。main
- **没有 D 号，也没进 DIFF §三"有意和 R5 不一样"**。建议的 D 行在 `_notes/hb-ch02.md`。
- [反编译] `Pred_RunCommand?` 0x14092ab70 设置 curtime；frametime 在 cmd + 0x218；`ProcessMovement?` 0x140a33cf0 乘玩家级倍率 player+0x3b8c。

---

### 2.2 每条命令的执行顺序

#### 原理

同一组规则，先后顺序换一下，结果就不一样：先判断落地再走，还是先走再判断落地；重力在加速度之前还是之后。R5 的顺序是 Source 引擎传下来的，HSD 照着做，因为研究里每一个"逐命令对得上"的数（起跳速度、着地那一帧、滑铲衰减）都依赖这个顺序。

#### 规则和公式

**R5 的顺序**（一条命令，`FullWalkMove`）：

1. dt = `AirSlowMo_TimeScale`（平时 1）× 这条命令的 frametime。
2. 重力前半步：v_z −= ½ · g · dt（g = `sv_gravity` × `gravityScale`；滑铲时这个半步还给水平速度加坡面项，第 04 章）。
3. 跳跃、攀爬 / 翻越、钩爪、推力等（第 03、04、05 章）。
4. 在地面 → 地面移动（摩擦 + 加速，第 03 章）；不在地面 → 空中移动。两者都在里面做碰撞（Source 的 TryPlayerMove / StepMove 那一套）。
5. 地面检测（§2.6）。
6. 重力后半步。
7. 在地面时，去掉速度沿地面法线的分量。

**HSD 的顺序**（一条命令，`SkillBody.Step`）：

| 步 | 做什么 | 对应 R5 |
|---|---|---|
| 0 | 输入：按钮、按下边沿 = 按钮 & ~上一条的按钮、前后左右轴、视角 | `ProcessMovement` 的按钮处理（NT §3） |
| 1 | 技能的 BeforeMove：可以改参数、重力倍率、时间倍率，或者整条命令改成"弹射"/"由技能直接摆位置"（第 05 章） | 各技能 |
| 2 | **世界·移动前**：定碰撞体高度（站 / 蹲，§2.4）；找脚下的支撑面、法线、地面实体（§2.6）；脚下低了 > 2 u 就离地；斜坡上的贴地（§2.9） | 上一条命令末尾的 CategorizePosition |
| 3 | **电机**：dt′ = dt × 时间倍率；下蹲碰撞体（§2.4）；滑铲开始；然后三选一：**起跳命令** / **地面命令** / **空中命令** | 第 2 – 6 步 |
| 3a | 地面命令：摩擦、加速（第 03 章）或滑铲（第 04 章）；v_z = 0；位置：平地 pos += v·dt′、z = 地面高度；坡上按 §2.8 | 第 4、7 步 |
| 3b | 空中命令：v_z −= ½g·dt′；空中加速、lurch（第 03 章）；pos += v·dt′；v_z −= ½g·dt′；**落地判断**（§2.6） | 第 2、4、5、6 步 |
| 3c | 起跳命令：v_z = 0；−½g·dt′；+V；−½g·dt′；空中加速；pos += v·dt′；−½g·dt′；落地判断（README 示范条目） | 第 2、3、4、6 步 |
| 4 | **世界·移动后**：从第 2 步时的位置扫到电机给的新位置（§2.5）；撞到的面去掉撞向它的速度；记下墙 / 天花板接触 | 第 4 步里的 TryPlayerMove |
| 5 | 技能的 AfterMove（只改速度）；收集这条命令的事件；时钟 += dt（真实 dt，不乘时间倍率） | — |

**和 R5 顺序的两处不同**（都是 HSD 现在的写法，R5 没有专门测过这两处的差别）：

1. **地面命令不加重力**。R5 地面命令也做两个重力半步，然后第 7 步去掉法线分量；HSD 直接令 v_z = 0、速度保持水平。平地上两者完全相同。坡上 R6 实测：不滑铲时速度保持水平，滑铲结束后在上坡上"向下坡方向的最大速度都是 0.00"（没有倒滑），和 HSD 的写法一致。
2. **碰撞在落地判断之后**。R5 的碰撞在移动里面、落地判断之前；HSD 的落地判断（3b / 3c 末尾）用的是第 2 步找到的"命令开始时脚下的地面"，碰撞（第 4 步）在后面。从高处落到一个**比原来脚下更高**的台面上时，HSD 先在第 4 步把脚放到台面上，下一条命令才算落地，最多晚一条命令（8.3 ms）。没有发现哪个对照因此变差，但这是写法上的差别，记在 `_notes`。

#### 实现模板

```
// 单位：u、s
body.step(input, dt):
    edges   = input.buttons & ~prevButtons;  prevButtons = input.buttons
    abilities.beforeMove(body, input)          // 可能设 mods：timeScale、gravityScale、launch、kinematic、参数
    world.beforeStep(motor)                    // §2.4 碰撞体高度，§2.6 支撑面，§2.9 贴地
    start = motor.pos
    motor.step(input, dt):
        dt2 = dt * mods.timeScale; g = svGravity * gravityScale * mods.gravityScale
        updateDuckHull()                       // §2.4
        if mods.kinematic: pos, vel, grounded = ability's; return
        if mods.launch:    vel = launch; airAccel; pos += vel*dt2; vel.z -= g*dt2/2; checkLanding(); return
        trySlideStart()                        // 第 04 章
        if grounded and edges.jump:  jumpCommand()          // 第 03 章 / README 示范条目
        elif grounded:               groundCommand()        // vel.z = 0; 平地 pos += vel*dt2, z = floorZ; 坡上 §2.8
        else:                        airCommand()           // 半步重力 / 空中加速 / pos / 半步重力 / checkLanding()
    world.afterStep(motor, start)              // §2.5 扫掠
    abilities.afterMove(body, input)
    motor.time += dt
```

Unity 参考实现：
- `U:…/Abilities/_Core/SkillBody.cs`：`SkillBody.Step`（按钮边沿、`world.BeforeStep` → `motor.Step` → `world.AfterStep`、事件）。
- `U:…/R5MotorV2.cs`：`R5MotorV2.Step`（BeforeMove / AfterMove、时钟）、`Move`（三选一）、`JumpCommand`、`AirMove`、`LaunchCommand`、`KinematicCommand`、`CheckLanding`。`CommandModifiers`（时间倍率、重力倍率、弹射、摆位置）。
- `U:…/World/MovementWorld.cs`：`BeforeStep`、`AfterStep`。

#### 验收

- `U:Assets/HSD/R5Replay/Tests/Editor/R5MotorV2Tests.cs`：`GravityHalfStep`（一条空中命令后 v_z = −750·dt，z = 500 − 750·dt²/2，误差 ≤ 1e-12）、`JumpRemovesOneAndAHalfGravitySteps`、`LandsWithinGroundProbeAndSnapsOnNextGroundCommand`（落地那条命令保持 z，下一条地面命令贴到地面）。
- 回放基线：回放电机（同一套顺序）对 R5 录像逐命令复现，回归按逐字节比较（RPS / RUD 的 `rps_check.py`、`rud_check.py`，第 11 章）。
- 合格线：顺序改动后，上面三个测试和回放基线逐字节不变；不然就是改了顺序。

#### 出处

- NG §1：`FullWalkMove` 的 7 步顺序；重力分 StartGravity / FinishGravity 两个半步。main
- NT §1、§3：命令执行链；按钮 movedata +0x24 / +0x28 / +0x2c（按下边沿 = 按钮 & ~旧按钮）。main
- `tf2/TF2-MOVEMENT-SUMMARY.md` §0：TF2 同样的顺序（TF2 跑墙也走地面移动函数）。main
- R6 结论第 1 条和"上坡"表下的说明：坡上不滑铲时没有倒滑。main
- `U:…/R5MotorV2.cs` 类注释（"Per command"一段）：HSD 每条命令的写法。main
- [反编译] `FullWalkMove` 0x140a4c810；`Gravity_HalfStep` 0x140a36130（NATIVE-MAP §3 把它误名为 `Grapple`，以 NG 为准）；`WalkMove` 0x140a4a7c0（NATIVE-MAP 误名 `WallRun_Move`）；`CategorizePosition` 0x140a51bc0；`PlayerMove` 0x140a54e80；`Duck` 0x140a54080。

---

### 2.3 和帧率无关的积分（T8）

#### 原理

"和帧率无关"有两层意思：

1. **积分本身是准的**：在一条命令里，加速度不变时，速度和位置用的公式算出来就是真实的抛物线、真实的匀减速、真实的指数衰减，不管这条命令长还是短。R5 的移动基本都是这样写的，所以 R5 在 120 fps 和 144 fps 下几乎一样。
2. **剩下的那一点差别也消掉**：有些判断只能"每条命令看一次"（这条命令开始时速度在哪一段、有没有着地、键是不是刚按下），所以事件总是落在命令的边界上，最多晚一条命令。R5 里这一点让"冲到速度上限的时间"在不同 dt 下差 13 %。HSD 用固定 120 Hz（§2.1）让这部分也逐位相同。

另外一条：**接近 0 的量直接归零，不留尾巴**（DP T8"最后归零"），否则速度永远停不干净。

#### 规则和公式

1. **恒定加速度（重力）用半步写法**：v += ½a·dt；x += v·dt；v += ½a·dt。等价于 x += v_前·dt + ½a·dt²，对恒定加速度是精确的。
2. **匀减速**：s ← max(0, s − D·dt)，到 0 为止精确。
3. **按比例衰减**：s ← s · k^dt（k 是"每秒保留的比例"，例如滑铲的 `slideVelocityDecay` 0.7）。**不要**写成 s · (1 − c·dt)，那个随帧率变。
4. **时间窗口按秒算**：事件时刻记"那条命令开始的时钟"；判断写成 (now − t_事件) 和秒数比较。不按命令数、不按帧数数。**时钟用 tick × dt 算**（或累加 dt 时比较加 10⁻⁹ 容差），比较照规则写的 < / ≥，**不另加容差**：120 Hz 下 0.2 s = 24 条整，好几个窗口（下蹲过渡 0.2 s、碰撞体变矮 0.2 s、退还 0.4 s）正好落在整条命令上，边界算哪边由 < 还是 ≤ 决定（例子见 04 §4.6）（重建检验 11-14 补，`rebuild-test/judge/REPORT.md`）。
5. **按"命令开始时的状态"做选择**：速度段、是否在地面、是否刚按键都在命令开始时判断一次。这会让事件最多晚 dt；固定 dt 下是确定的，可以重放。
6. **加到上限为止**：加速写成 s ← min(上限, s + a·dt)，或 Source 的 accelerate（加的量不超过"离想要的速度还差多少"），不会冲过头。
7. **归零**：地面速度 < `stopSnapSpeed` 就直接清零（第 03 章）；镜头的弹簧、平滑在目标和当前都 < 0.001 时清零（第 07 章）。
8. **镜头的状态只在命令上更新**（每条命令 `Observe` 一次，弹簧按 dt 的精确解推进），渲染帧只在最近两条命令的镜头状态之间插值，所以也和画面帧率无关（07 §0.2、§4.1）。Unity：`NativeCamera.Attach` 把 `Observe` 挂在 `PracticeSession.OnCommand`，`NativeCamera.Update(renderTime, …)` 只插值；M5.5 镜头 `CameraFeedback` 同样挂在 `OnCommand`。11-14 前这一条写的是"按画面帧算"，和 07 章矛盾，已按代码改正（重建检验 11-14 补，`rebuild-test/judge/REPORT.md`）。

| 量 | [m] | 原值 | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力 g（`svGravity` × `gravityScale`） | 19.05 m/s² | 750 u/s² × 1 | 10.42 H/s² | — | [数据] [实测]，README 示范条目 |
| 一条命令的重力速度增量 g·dt（120 Hz） | 0.1588 m/s | 6.25 u/s | 0.0868 H/s | — | [算] |
| 事件最晚多少（= dt，120 Hz） | — | 8.333 ms | — | — | [算] |
| R5 冲到上限的时间随 dt 的散布 | — | 0.145–0.167 s（13 %），dt 6.7–7.2 ms | — | — | [实测] GM |
| 固定步长下换命令频率的残差（25° 坡上走 3 s，60 / 144 / 240 Hz 对 120 Hz） | — | x ≤ 6 u、z ≤ 3 u | — | — | [实测] Unity 测试 |

#### 实现模板

```
// 单位：u、s
gravityHalf(v, g, dt):  v.z -= 0.5*g*dt
decelLinear(s, D, dt):  return max(0, s - D*dt)
decay(s, k, dt):        return s * pow(k, dt)          // k = 每秒保留的比例
windowFrac(now, tEvent, t0, T):                         // 例：连跳系数、lurch 强度
    return clamp((now - tEvent - t0) / T, 0, 1)
snap(s, eps):           return s < eps ? 0 : s
```

自查清单（每写一条新规则过一遍）：
- 有没有 `x *= 常数` 这种每条命令乘一次的写法？→ 改成 `pow(k, dt)`。
- 有没有"过了 N 条命令"？→ 改成秒。
- 有没有读画面帧时长（Unity 的 `Time.deltaTime`）？→ 模拟里只许用命令 dt。
- 有没有"差一点点永远到不了 0"？→ 加归零门槛。

Unity 参考实现：`U:…/R5MotorV2.cs`（`AirMove`、`JumpCommand` 的半步重力；`SlideSpeedStep` 的 (s − D·dt)·0.7^dt；`MultiJumpFrac` 按秒；`GroundSpeedStep` 的 `stopSnapSpeed`）。镜头的解析弹簧见第 07 章。

#### 验收

- `R5MotorV2Tests.GravityHalfStep`：精确到 1e-12。
- `PracticeGameTests.SameCommandsAtAnyFrameRateGiveTheSameState`、`MovementDemoTests.DemoIsFrameRateIndependent`：画面帧率不影响身体（逐位）。
- `U:Assets/HSD/R5Replay/Tests/Editor/MovementWorldTests.cs`：
  - `SlopeRunIsDeterministicAndCloseAcrossCommandRates`：同频率两次运行逐位相同；换命令频率 x 差 ≤ 6 u、z ≤ 3 u（这是"命令频率"的残差，不是画面帧率）。
  - `CeilingStopsTheJumpAtAnyCommandRate`（60 / 120 / 144 / 240 Hz）：头正好停在天花板上。
  - `NoTunnellingThroughThinWallsAndCeilings`（60 / 120 / 144 Hz）。
- 镜头：`CameraFeedbackTests.CameraIsFrameRateIndependent`、`SmootherIsFrameRateIndependent`、`NativeCameraTests.PunchAxisIsFrameRateIndependent`（第 07 章）。

#### 出处

- DP T8：弹簧按帧时间解析解、窗口按时间不按帧、接近 0 直接归零。main
- NT T-05：加速、摩擦都按 dt 线性，加速度按加速前速度选段，冲到上限的时间有 13 % 差异。main
- NG §2.3、§2.5：摩擦 max(0, s − D·ft)、滑铲 × `slideVelocityDecay`^ft；Accelerate 加完后 |v| ≤ max(原 |v|, wishspeed)。main
- GM 第 5、6 条限制：吸附阈值 (0.58, 1.58]，取 1；13 % 的来源。main
- `research/phase2-local/m5/M5-REPORT.md` §6：60 Hz 漂移约 35 u/s。main

---

### 2.4 碰撞体：站 / 蹲尺寸和切换

#### 原理

身体在碰撞里是一个**竖直的方盒**，不随视角转。方盒简单、确定，贴墙滑、过门、钻洞的结果都好预测。站着和蹲着高度不同，蹲下可以钻过矮的地方；钻进去以后头顶有东西就站不起来。

Apex 有一个容易感觉到的细节：**空中松开下蹲时，头不动、脚往下伸**（原点往下掉 16.5 u），这样滑铲跳、蹲跳以后松开下蹲，镜头不会突然往上弹。

#### 规则和公式

1. 碰撞体是以原点（脚底中心）为底面中心的方盒：半宽 r = `hullRadius`，高 h = `hullHeight`（站）或 `crouchHullHeight`（蹲）。
2. **地上下蹲**：按住下蹲满 `hullCrouchTime` 后碰撞体变矮，脚不动（头往下）。
3. **空中松开下蹲**：起跳后至少 `airUnduckMinAfterTakeoff` 才生效；碰撞体变高，原点往下移 `airUnduckDrop`（头不动，脚往下）；不低于地面。
4. **地上松开下蹲**：碰撞体变高，脚不动。头顶放不下站立碰撞体时**保持蹲姿**，直到能站起来。
5. 空中按下下蹲（收脚）：没有 R5 数据，HSD 没做（碰撞体保持原来的高度）。
6. 坡面上碰撞体底部按圆底算（§2.8）；平的顶面（台阶、边缘）仍按方盒。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 半宽 `hullRadius`（宽 × 深 = 32 × 32） | 0.406 m（宽 0.813 m） | HSD 设计值 16 u | 0.222 H | — | [设计] Source 默认；R5 的真值在 setfile `poseSettings`，没读出 |
| 站立高 `hullHeight` | 1.829 m | HSD 设计值 72 u | 1 H | — | [设计]，同上 |
| 蹲姿高 `crouchHullHeight` | 1.219 m | HSD 设计值 48 u | 0.667 H | 由 16.5 推出 55.5 或 39，见下 | [设计]，代码注释"R5 duck hull not measured" |
| 地上按住多久碰撞体变矮 `hullCrouchTime` | — | 0.2 s | — | R5 录像"已蹲下"在 0.21–0.24 s 亮 | [实测] M5 |
| 空中松开下蹲，原点下降 `airUnduckDrop` | 0.419 m | 16.5 u | 0.229 H | — | [实测] M5（M3 e8 / e3 slide350，8 次） |
| 起跳后多久才允许 `airUnduckMinAfterTakeoff` | — | 0.08 s | — | — | [实测] M5 |

**蹲姿高度没有定下来**：如果"原点下降 = 站立高 − 蹲姿高"，蹲姿高应该是 72 − 16.5 = 55.5 u；如果像 SDK 里 half-duck 那样是"差的一半"，就是 72 − 33 = 39 u。两种都不是 48。而且 HSD 现在两边**对不上**：空中站起时碰撞体长高 72 − 48 = 24 u，原点只下降 16.5 u，所以碰撞体的头顶其实往上长了 7.5 u（镜头不受影响，镜头的眼高是另一套，第 07 章）。在头顶刚好卡着天花板的地方，这会让"站不起来"的判断和 R5 不同。等 B01-1（R5 碰撞体实测）。

#### 实现模板

```
// 单位：u、s
updateDuckHull(input, now):                 // 每条命令，电机开头
    if input.duckHeld:
        if duckHeldSince == none: duckHeldSince = now
        if grounded and now - duckHeldSince >= hullCrouchTime: hullCrouched = true
        return
    duckHeldSince = none
    if not hullCrouched: return
    if grounded: hullCrouched = false; return
    if now - lastTakeoff < airUnduckMinAfterTakeoff: return
    pos.z = max(floorZ, pos.z - airUnduckDrop)
    hullCrouched = false

world.beforeStep:                           // 碰撞用的高度
    crouchedHull = motor.hullCrouched or (crouchedHull and blocked(pos, hullHeight))
    h = crouchedHull ? crouchHullHeight : hullHeight
```

Unity 参考实现：
- `U:…/World/MovementWorld.cs`：`hullRadius`、`hullHeight`、`crouchHullHeight`；`BeforeStep` 里的 `crouchedHull`、`lastHullHeight`；`Blocked(feet, h)`；`CeilingClearance(feet, h, maxUp)`。
- `U:…/R5MotorV2.cs`：`UpdateDuckHull`；`R5MotorV2Params.hullCrouchTime`、`airUnduckDrop`、`airUnduckMinAfterTakeoff`（`airUnduckDrop` = 0 时退回"蹲下标志就是碰撞体"的旧做法，`LegacyM2()` / `WithLegacyM2Rud()`）。

#### 验收

- `MovementWorldTests.CrouchedHullFitsUnderALowCeilingAndStaysCrouched`：60 u 的缝，蹲走能钻进去（48 放得下、72 放不下）；松开下蹲还是蹲着；头顶间隙 = 60 − 48。
- RUD 回放（`research/phase2-local/rud/README.md`，`rud_check.py`）：M3 e8 连跳位置误差 8.0 → 0.6–1.4 u，e3 滑铲跳 7.26 → 2.54 u 等，105 个录像里 70 个逐命令不变。
- 合格线：上面测试通过；RUD 基线逐字节不变。

#### 出处

- `research/phase2-local/m5/reference_config/README.md`：16.5 u、0.2 s、0.08 s 的实测。main
- DIFF RUD 节（D-49）：回放电机加上下蹲碰撞体；三个例外。main
- A4 §2：32 × 32 × 72、蹲 48 [design]；蹲着头顶有东西就保持蹲姿。main
- MA §8："Stand/duck hulls are cached from the settings `poseSettings`"；half-duck 存在。main
- `handbook/01-units-body.md` §4.2：身体尺寸表、55.5 / 39 两种推法。handbook/base
- SDK `research-src/s21-r5sdk/src/core/init_server.cpp` `VHalfDuckZipParity` 注释：(standHull − duckHull) × 0.5。本地，不在这个仓库
- [反编译] `Duck` 0x140a54080；下蹲状态 player+0x2a70。

---

### 2.5 碰撞：扫掠、贴墙滑、天花板、卡住

#### 原理

身体每走一步，都从起点**扫**到终点：中间碰到什么就停在什么上面，所以速度再快也穿不过薄墙。撞墙时只去掉"撞进墙里"的那部分速度，沿墙的速度保留，所以斜着撞墙会顺着墙滑走——这是 R5 钩爪撞墙实测的样子（撞墙后垂直墙的速度剩约 6 u/s，沿墙的速度不变）。

#### 规则和公式

1. **把墙加厚，把身体缩成一个点**：每个凸体的每个面 n·p ≤ d 都按碰撞体外扩（闵可夫斯基和）：d′ = d + r·(|n_x| + |n_y|) + max(0, −n_z)·h。原点在所有外扩面里面 ⇔ 碰撞体和这个凸体重叠。
2. 能站的顶面（n_z ≥ `standableNormalZ`）在"挡不挡路"时再往下降 `stepUp`·n_z（这就是上台阶，§2.7）。
3. **扫掠**：把这一步从起点到终点的线段对每个凸体求最早进入点（Cyrus–Beck），取所有凸体里最早的一个。
4. 进入了哪个面，就把终点投影到这个面上；速度去掉撞向这个面的分量（v ← v − min(0, v·n)·n）。从投影后的点继续扫剩下的部分，最多 `MaxBumps` 次。
5. 面的种类按法线分：
   - 侧面或太陡的坡（−0.7 < n_z < 0.7）→ **墙**：记下墙接触（跑墙、蹬墙跳、翻越用，第 04、05 章）；
   - 朝下（n_z ≤ −0.7）→ **天花板**：头停在天花板上，v_z 变成 ≤ 0；不算墙接触；
   - 能站的顶面从上面进入 → **地面**：脚放到顶面上。
6. **卡住**：扫完以后终点还在某个凸体里面，就退回本次扫掠的上一个点，再不行退回命令开始的位置。
7. 一条命令开始时已经在凸体里面（被别的东西推进去）：沿穿透最少的面推出来，先试侧面。
8. **技能直接摆位置**（传送、出传送门）不扫掠，由技能自己检查终点（`ResolveTeleport`，8 u 一步往回找空位）。
9. 天花板滑行（Octane 等在天花板下保留速度）是一个开关，规则在第 05 章。

| 量 | [m] | 原值 | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 一条命令最多碰几次 `MaxBumps` | — | HSD 设计值 8 次 | — | Source TryPlayerMove 是 4 次 | [设计] |
| 墙 / 天花板 / 地面的法线分界 | — | n_z 0.7（= `standableNormalZ`） | — | — | [数据] SDK |
| R5 撞墙后垂直墙的速度 | 0.152 m/s | 6.0 ± 1.9 u/s | 0.083 H/s | — | [实测] SWING §5 |
| 撞墙后沿墙速度的变化 | 0.0013 m/s | 0.05 ± 3.1 u/s | — | — | [实测] SWING §5 |
| 传送找空位的步长 | 0.203 m | HSD 设计值 8 u | 0.111 H | — | [设计] |

#### 实现模板

```
// 单位：u
expandedOffset(plane, h, forBlocking):
    o = plane.d + r*(|n.x| + |n.y|)          // 坡面在圆底模式下改用 §2.8 的写法
    if n.z < 0:                         o -= n.z * h
    elif forBlocking and n.z >= 0.7:    o -= stepUp * n.z
    return o

afterStep(motor, start):
    from = start; to = motor.pos; v = motor.vel; bumps = 0
    while bumps < MaxBumps and sweep(from, to) hits (solid, plane, t, embedded):
        bumps += 1
        kind = wall | ceiling | floor (by plane.n.z)
        hit  = embedded ? to : from + (to - from)*t
        to   = projectOnto(to, plane, kind == floor ? topOffset : expandedOffset)
        vn = dot(v, n); if vn < 0: v -= vn*n
        record contact(kind)
        from = embedded ? to : hit
    if blocked(to): to = blocked(from) ? start : from      // 卡住就退回
    motor.pos = to; motor.vel = v
```

Unity 参考实现：`U:…/World/MovementWorld.cs`：`Offset`、`Inside`、`Enter`（Cyrus–Beck）、`LeastPenetration`、`Kind`、`Sweep`、`Project`、`AfterStep`、`lastCeiling`、`lastBumps`、`lastStuck`、`ResolveTeleport`；凸体 `U:…/World/WorldGeometry.cs`（`ConvexSolid`：方盒、坡道、绕竖轴转的方盒）；接口 `U:…/World/IMovementWorld.cs`。

#### 验收

`MovementWorldTests`：
- `NoTunnellingThroughThinWallsAndCeilings`：2 u 厚的墙和天花板，900 / 20 000 u/s，60 / 120 / 144 Hz，正好停在面上（x = 500 − 16，z = 900 − 72）。
- `InsideCornerStopsBothAxesExactly`、`SlidesAlongAWallMadeOfTwoBoxesWithoutSnagging`（两块方盒拼的墙，每条命令 y 都在增加，不卡接缝）。
- `CeilingStopsTheJumpAtAnyCommandRate`、`SteepSlopeIsAWall`、`OrientedBoxFaceContactAndRaycast`。
- `MixedWorldFuzzKeepsTheHullFree`（4 个种子，40 s 随机乱按）：每条命令后碰撞体都不在凸体里、不低于地面、不卡死。
- `U:Assets/HSD/Game/Tests/Editor/WorldEquivalenceTests.cs`：和冻结的 M5.5 BoxWorld 比，20 万个点的支撑 / 阻挡查询相同；烟雾路线、每种配置 × 装备 30 s、每个动作演示逐位相同。
- 合格线：全部通过。

#### 出处

- A4 §2：外扩写法、Cyrus–Beck、8 次、面的种类、卡住的处理、不穿墙。main
- `research/phase2-local/m4b/swing/SWING.md` §5：R5 撞墙 v_n → 约 6 u/s、沿墙速度保留。main
- SDK `slope_launch_math.h`：0.7 / 0.999（A4 引用）。本地 `L:research-src/`
- R5 自己的碰撞代码（TryPlayerMove、碰几次、碰撞体形状）**没有读**，见 `_notes` 待研究。

---

### 2.6 地面检测：站在什么上、什么时候离地 / 落地

#### 原理

"在地上"决定了用地面规则还是空中规则（摩擦、加速、能不能跳）。规则要满足两点：走路时不会因为一点点起伏就判成离地；跳起来、被弹起来时立刻判成离地。R5 的做法是"脚下 2 u 以内有能站的面就算着地，但往上走得快（> 140 u/s）就不算"。

#### 规则和公式

**R5 的规则**（`CategorizePosition`，每条命令末尾）：

1. 竖直速度 v_z > `NonJumpVelocity`（140 u/s）→ 离地。
2. 否则从脚底往下探 `groundProbe`（2 u），碰到能站的面（n_z ≥ 0.7）→ 着地，记下地面实体和法线；碰不到 → 离地。

**HSD 现在的写法**（游戏身体，`MovementWorld` + `R5MotorV2`）：

1. **支撑面**（每条命令开始，§2.2 第 2 步）：在碰撞体脚印（32 × 32）下面，找比脚高不超过 `stepUp` 的、最高的能站的顶面；没有就是基础地面。给出高度、法线、表面 id、地面实体（道具算单独的实体，静态关卡几何算一个，第 04 章滑铲二次加成用）。
2. **离地**：在地面上、而脚下的支撑面低了 > `groundProbe` → 离地（滑铲同时结束）。斜坡例外见 §2.9。
3. **落地**（空中命令、起跳命令、弹射命令的末尾）：v_z < 0 **而且** 脚离支撑面 ≤ `groundProbe` → 着地：v_z = 0，这一条命令的 z 不动，下一条地面命令再贴到地面上；"上次落地时刻" = 这条命令开始的时钟（连跳惩罚、超速削减用，第 03 章）；按着下蹲且水平速度 ≥ `slideRequiredStartSpeed` → 接着滑铲（第 04 章）。
4. 起跳、弹射命令自己令"不在地面"，不走离地判断。

**和 R5 的差别**：HSD 落地要求 v_z < 0；R5 是 v_z ≤ 140 就可以着地。平地上看不出来（离开地面后 v_z 只会从正变负）；可能有差别的是**上坡时被抛起来、v_z 是小的正值又碰到坡面**的情况（例如冲上坡顶又落回坡上、跳板弹到斜面上）。R5 没测过，DIFF 里没有这一条，写进 `_notes`。

| 量 | [m] | 原值 | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 着地探测距离 `groundProbe` | 0.0508 m | 2 u | 0.0278 H | — | [反编译] [实测]：原生 2.0 u；M2 拟合；r1237 离地 2.075 u 时晚一条命令着地 |
| 往上多快算离地（R5） | 3.556 m/s | 140 u/s | 1.944 H/s | Source `NON_JUMP_VELOCITY` 同值 | [反编译] [数据] |
| 能站的面 `standableNormalZ` | — | 0.7（≤ 45.57°） | — | — | [数据] SDK，见 §2.8 |
| 上次落地时刻 | — | 落地那条命令**开始**的时钟 | — | — | [实测] M2（README 示范条目） |

#### 实现模板

```
// 单位：u
world.beforeStep(m):
    g = support(m.pos, hullRadius, maxTop = m.pos.z + stepUp)   // 最高的能站顶面，或基础地面
    drop = m.pos.z - g.height
    if slopeStick(m, g, drop): m.pos.z = g.height; drop = 0       // §2.9
    m.floorZ = g.height; m.groundNormal = g.normal; m.groundEntity = g.entity
    if m.grounded and drop > groundProbe:
        m.grounded = false; endSlide()

motor.checkLanding(now):                                          // 空中 / 起跳 / 弹射命令末尾
    if vel.z < 0 and pos.z - floorZ <= groundProbe:
        if pos.z < floorZ: pos.z = floorZ
        vel.z = 0; grounded = true; lastLandTime = now           // now = 这条命令开始的时钟
        if duckHeld and |vel_h| >= slideRequiredStartSpeed: resumeSlide()   // 第 04 章
```

Unity 参考实现：`U:…/World/MovementWorld.cs`（`Support`、`TopUnder`、`BeforeStep`、`ProbeGround`、`SupportHeight`、`ResetBody`）；`U:…/R5MotorV2.cs`（`CheckLanding`、`floorZ`、`groundNormal`、`groundEntity`、`groundSurface`、`lastLandTime`、`landed` / `tookOff` 事件）；`R5MotorV2Params.groundProbe`。

#### 验收

- `MovementWorldTests.GroundProbeOnBoxRampAndSteepRamp`：方盒顶 40；26.6° 坡上按脚印较高的角支撑（方盒模式）；63.4° 的坡不支撑（脚下是地面）；脚在 21.9 时 40 高的顶面不算支撑（40 − 21.9 > 18），脚在 22 时算。
- `R5MotorV2Tests.LandsWithinGroundProbeAndSnapsOnNextGroundCommand`。
- RUD 回放：M3 r1237 是已知例外（沙盘比 R5 高约 0.5 u，离地 2.075 u，刚超出 2.0 u，晚一条命令着地，丢一次连跳；用户同意）。
- 合格线：测试通过；回放基线逐字节不变。

#### 出处

- MA §8：140 u/s"on both engines"（`slope_launch_math.h:12-13`），和 Source `NON_JUMP_VELOCITY` 相同；`m_hGroundEntity == -1` 表示在空中。main
- DIFF RUD 节："原生着地探测（`CategorizePosition` 0x140a51bc0）：向下 2.0 u，向上速度 > 140 u/s 离地，和 Unity 的 `groundProbe` 2 相同"；r1237 例外。main
- `research/phase2-local/m2/air_jump/AIR-JUMP-MODEL.md` §2.3：落地 = v_z < 0 且移动后脚下 2 u 以内；z 保持，下一条地面命令贴地。main
- R6 原生代码一节：`SetGroundEntity` 换地面实体（第 04 章滑铲二次加成）。main
- [反编译] `CategorizePosition` 0x140a51bc0；`SetGroundEntity` 0x140a51650；地面实体 player+0x324（客户端）/ +0x3C4（dedi）；地面法线 player+0x43dc–0x43e4；上次落地时刻 player+0x3680。

---

### 2.7 上台阶（R5 22 u，HSD 18 u）

#### 原理

走路时碰到不高的台阶、路沿，应该直接走上去，不用跳，也不减速。能"走上去"的最大高度就是台阶高度。这个数直接决定关卡：低于它的东西是地面的一部分，高于它的东西是墙，要跳或者翻越。

**这里 HSD 和 R5 不一样，而且没有定下来**：R5（Apex）的台阶高度是 **22 u**，HSD 现在用的是 **18 u**——这是 TF2 和 Source 的默认值。18 是 M5 第一版世界时随手沿用的，从来没有按 R5 改过，也没进 DIFF。

#### 规则和公式

**HSD 现在的规则**：

1. 能站的顶面（n_z ≥ 0.7），只要比脚高不超过 `stepUp`，就**不挡路**：碰撞体可以水平走进它上方 `stepUp` 那一层（§2.5 第 2 条）。
2. 下一条命令开始时，支撑面查找（§2.6）把它当成脚下的地面；地面命令令 z = 地面高度，**一条命令内直接抬上去**，水平速度不变。
3. 高于 `stepUp` 的顶面，它的侧面就是墙。
4. **空中也一样**：只要脚离顶面不超过 `stepUp`，空中的身体也能水平"越过"台面的侧面；往下落时在下一条命令落地、被放到台面上。R5 里这种情况大概率是翻越（第 04 章）或者撞墙——Source 的空中移动只碰撞不迈台阶。这是 HSD 写法带来的行为，**R5 没测过**，写进 `_notes`。
5. 下台阶（走下路沿）不是这一条，见 §2.9。

**R5 的值和差别**：

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 台阶高度，R5 setfile `stepHeight` | 0.559 m | R5 原值 22 u | 0.306 H | — | [数据] SV §2、T1-REPORT（Apex 列） |
| 台阶高度，TF2 `stepheight` | 0.457 m | TF2 原值 18 u | 0.250 H | — | [TF2 数据] T1-REPORT |
| 台阶高度，HSD 现在 `stepUp` | 0.457 m | HSD 设计值 18 u | 0.250 H | 18 – 22 待定 | [设计]，等于 TF2 |
| 滑铲上台阶减速 `slide_step_velocity_reduction` | —（(u/s)/u = 1/s，不换算） | 10（每 1 u 台阶减 10 u/s） | — | — | [数据] ConVar 默认值；R5 是否真的读它**没查**；Unity **没有做** |

**差别会在哪里显出来**：高度在 18 u 到 22 u 之间（0.46–0.56 m）的台阶、路沿、箱子边。R5 里直接走上去，HSD 里是墙，要跳。还有空中"迈台面"的范围（第 4 条）、坡上贴地的范围（§2.9）也跟着这个数。

**R5 自己怎么上台阶没读过**：Source 的做法（StepMove）是"先抬起 `stepHeight` 再水平走再落下，和不抬的走法比，取走得远的那个"，速度不变。R5 是不是这样、镜头会不会把这一下抬高平滑掉，都不知道。

**建议**（写进 `_notes`，由用户定）：先做 B02-1 实测（R5 台阶梯 18 / 20 / 22 / 24 u，走、冲刺、滑铲、空中贴着台边），确认 22 真的生效后按"尽量贴合 R5"把 `stepUp` 改成 22，18 留开关（关卡里 18–22 u 之间的东西要一起看）。

#### 实现模板

```
// 单位：u
// 挡路时：能站的顶面在碰撞体空间里下降 stepUp（§2.5 expandedOffset 的第三行）
// 支撑时：support() 只认 top <= feet.z + stepUp 的顶面（§2.6）
// 地面命令：pos.z = floorZ        → 一条命令内抬上去，速度不变
```

如果改成 R5 的 22：只改 `MovementWorld.stepUp`（它同时管挡路、支撑、坡上贴地三处）。滑铲上台阶减速要另外加：在地面命令里检测这条命令抬高了多少 Δz（> 0），滑铲中 s ← max(0, s − 10·Δz)——这是按 ConVar 说明推的写法，**没有 R5 实测**。

Unity 参考实现：`U:…/World/MovementWorld.cs`：`stepUp` = 18；`Offset(q, h, step)`（挡路时降低）；`Support(p, r, maxTop)`（`maxTop` = 脚 + `stepUp`）。

#### 验收

- `MovementWorldTests.GroundProbeOnBoxRampAndSteepRamp` 里的台阶边界：顶面比脚高 18.1 u 不支撑，正好 18 u 支撑。
- `WorldEquivalenceTests.SupportAndBlockedMatchTheM55BoxWorldOnTheMap`：和 M5.5 的方盒规则（顶面 ≤ 脚 + 18 是台阶）在 20 万个点上相同。
- **缺**：没有"走上台阶"的整段测试（18 u 走上去、18.01 u 挡住、速度不变、空中贴着台边的行为）。如果改成 22，要加这一组，并且合格线要按 B02-1 的 R5 实测定。

#### 出处

- SV §2 表：`stepHeight` 22 u。main
- `tf2/static-values/T1-REPORT.md` 第 58 行（TF2 18、Apex 22）；`tf2/TF2-VS-APEX.md` 约第 104 行。main
- A4 §2："step-up 18 (unchanged)"；`MovementWorld` 类注释"a top at most 18 u above the feet is a step"。main
- MA §8：`stepHeight` 是 class var。main
- `research/rea-native/convar-defaults/CONVAR-DEFAULTS.md`：`slide_step_velocity_reduction` 10，"Velocity reduction when going up a step (is multiplied by step height)"；`tf2/TF2-MOVEMENT-SUMMARY.md` §5.2。main
- `handbook/00-INVENTORY.md` 02 章"缺什么"第 1 条、`99-TODO-RESEARCH.md` B01-2。handbook/base
- [反编译] 没有：R5 的 StepMove / TryPlayerMove 没读；ConVar `slide_step_velocity_reduction` 注册在 0x1401af930。

---

### 2.8 斜坡：能站的上限、坡上走、圆底

#### 原理

不太陡的坡可以站、可以走，走的时候**速度保持水平、位置沿着坡**：上坡不会把速度变小、下坡不会把人加速（除非在滑铲，第 04 章），速度表上一直是同一个数（R5 实测冲刺上下坡都是 299 u/s）。太陡的坡站不住，当墙。

Apex 的身体在坡上"坐得低一点"：按方盒算，坡上会被较高的那个角撑起来、离坡面很高；R5 实测更像一个半径 16 的圆底，贴着坡面。

#### 规则和公式

1. **能站**：法线 n_z ≥ `standableNormalZ`（0.7，约 45.57°）。更陡的面不支撑、当墙（§2.5）。
2. **平地**：n_z ≥ `FlatNormalZ`（0.999，约 2.56°）当平地，走平地的规则（坡上的位置规则只在 n_z < 0.999 时用；滑铲坡面项没有这个门槛，第 04 章）。
3. **速度**：在地面上速度保持水平（v_z = 0），摩擦、加速都按水平速度算（第 03 章）。
4. **上坡的一步**（这一步的水平位移 d = v_h·dt 和坡面法线 n 的水平分量反向，d·n < 0）：先把 d 投影到坡面（d −= (d·n)·n），**再把这一步的长度补回 |v_h|·dt**。所以水平前进 = |v_h|·dt·cosθ，沿坡的三维步长 = |v_h|·dt。
5. **下坡的一步**：水平位移不变（= |v_h|·dt），高度跟着坡面往下：Δz = −(d·n)/n_z。
6. **坡上的原点高度（圆底）**：原点在坡面上方 R·(1/n_z − 1)，R = `hullBottomRadius`；接触点和法线都取原点正下方的坡面。只用在坡面上；平的顶面（台阶、边缘、平台）还是方盒。
7. **凸转折**（平顶的边缘下面接下坡、上坡上面接平台的边）：原点已经在坡上、但方盒的脚印还搭在平顶上时，高度先按方盒留在平顶上（最多 r·tanθ），法线、表面、地面实体按坡取。

| 量 | [m] | 原值 | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 能站的最陡 `standableNormalZ` | — | 0.7（45.57°） | — | 实测只到 40°；45.6° 本身没测 | [数据] SDK |
| 平地门槛 `FlatNormalZ` | — | 0.999（2.56°） | — | — | [数据] SDK |
| 圆底半径 `hullBottomRadius` | 0.406 m | 16 u | 0.222 H | 0 = 方盒（旧版 / Fun） | [实测] R6 |
| 坡上原点高度 R·(1/cosθ − 1)：10° / 20° / 30° / 40° | 0.006 / 0.026 / 0.063 / 0.124 m | 公式 0.25 / 1.03 / 2.48 / 4.89 u；R5 实测 0.22 / 1.03 / 2.51 / 5.00 u | — | 方盒 16·tanθ：2.82 / 5.82 / 9.24 / 13.43 u | [实测] R6 [算] |
| 上坡水平步长比例 cosθ：10° / 20° / 30° / 40° | — | 0.9848 / 0.9397 / 0.8660 / 0.7660；R5 实测 0.9862 / 0.9423 / 0.8693 / 0.7699 | — | 只投影（Source）cos²θ：0.9698 / 0.8830 / 0.7500 / 0.5868 | [实测] R6 |
| 下坡水平步长比例 | — | 1.0000；R5 实测 0.9976 | — | — | [实测] R6 |
| 冲刺上下坡的速度 | 7.595 m/s | 299 u/s（和平地一样） | 4.153 H/s | — | [实测] R6 |

R5 实测和公式差 ≤ 0.11 u（高度）、≤ 0.004（比例），按拟合原则不追。

#### 实现模板

```
// 单位：u、s
slopeGroundMove(dt):                       // 地面命令、n.z < FlatNormalZ 时
    n = groundNormal
    d = (vel.x*dt, vel.y*dt); k = d·n_h
    if k < 0:                              // 上坡
        L0 = |d|
        d -= k*n_h; dz = -k*n.z            // 投影到坡面
        if slopeUphillKeepStep: (d, dz) *= L0 / |(d, dz)|   // 补回长度（R6U U-1）
    else:                                   // 下坡
        dz = -k / n.z
    pos.xy += d; pos.z = floorZ + dz

roundedTop(ramp, origin):                  // R6U U-2，hullBottomRadius > 0
    if origin over the face:  height = plane(origin) + R*(1/n.z - 1); normal = face normal
    elif beyond the high edge: height = edge; normal = up
    elif concave corner (contact point origin - R*n_h on the face): as over the face
    else: none
```

Unity 参考实现：
- `U:…/R5MotorV2.cs`：`SlopeGroundMove`；`FlatNormalZ` = 0.999。
- `U:…/R5MotorV2Params.cs`：`slopeMovement`（坡上规则总开关，回放电机关、游戏身体开）、`slopeUphillKeepStep`（U-1）、`hullBottomRadius`（U-2，Reference 16，Fun 和回放电机 0）、`slideSlopeAnyGrade`（U-4，第 04 章）。这些开关 `[NonSerialized]`，`MovementConfigs.Reference()` 打开，`Fun()` 关回旧版。
- `U:…/World/MovementWorld.cs`：`standableNormalZ` = 0.7、`hullBottomRadius`、`RoundedTop`、`Offset`（圆底时坡面的外扩写法）、`Support`（凸转折的处理）。

#### 验收

- `U:Assets/HSD/R5Replay/Tests/Editor/R6USlopeTests.cs`：
  - `UphillStepAndRestHeight`（20° / 40°，Reference / Fun）：Reference 比例 = cosθ、原点高度 = 16·(1/cosθ − 1)，误差 ≤ 1e-6；Fun = cos²θ、16·tanθ。
  - `ConvexJointTakesTheSlopeNormalAtTheOrigin`；`ReferenceHasTheR5SlopeRulesAndFunAndTheReplayMotorKeepTheOldOnes`。
- `MovementWorldTests.SlopeOptionWalksUpAndDownGroundedWithFlatVelocity`（20° 坡上每条命令都着地、速度水平、离坡面 ≤ 1e-6 u）、`SteepSlopeIsAWall`（60° 爬不上，空中撞上去按坡面法线）、`SlopeOptionChangesNothingOnFlatGroundAndBoxes`（平地上开关开 / 关逐位相同）。
- `U:Assets/HSD/Game/Tests/Editor/R6UGameTests.cs` `DemoTrajectoriesAndLapVersusPreR6U`。
- 对照数据：R6 133 次实测（`research/phase2-local/slope/tables.md`、`results.json`），前后对照 `R6U-COMPARE.md`。
- 合格线：比例和高度按公式到 1e-6；对 R5 实测高度差 ≤ 0.2 u、比例差 ≤ 0.005。

#### 出处

- R6 "坡上移动比例和原点高度"表、限制一节（没测 < 5° 和 > 40°；超过 45.6° 不能站；U-2 的碰撞体形状没读原生代码）。main
- DIFF R6U 节 U-1、U-2、U-4（D-45 / D-46）：旧版、R5、现在、切回旧版的开关。main
- A4 §2、§3：0.7 / 0.999 [src]；速度保持水平（SDK 注释"Apex keeps grounded velocity flat and only slides the position along the slope"）。main
- `R6U-COMPARE.md`：改前改后对照。main
- 不滑铲时在坡上**走路**（非冲刺）没单独测（B02-2）。

---

### 2.9 贴地：下坡、凸转折、走下台边

#### 原理

冲下坡、从平地冲进下坡时，身体应该贴着坡面走，不应该每一步都"飞起来一点再落下"——那样会频繁丢掉地面状态，跳不起来、滑铲断掉。但在平地上走下一个路沿、台边，应该真的掉下去（有一小段空中），这样落地的镜头、落地减速才有意义。

#### 规则和公式

**HSD 现在的规则**（`slopeMovement` 开时）：

1. 一条地面命令开始时，脚下支撑面低了 drop：
   - drop ≤ `groundProbe`（2 u）：照常在地面（§2.6）。
   - `groundProbe` < drop ≤ `stepUp`，**而且**原来的地面或新的支撑面是坡（n_z < 0.999）：**贴下去**，z = 新支撑面高度，继续在地面上。
   - 其他（平地落差，或 drop > `stepUp`）：离地，开始下落。
2. 地面命令走完以后，如果在坡上而 z 低于脚下能站的顶面，抬到顶面上（不陷进坡里）。

**这几条是 HSD 设计**（A4 标 [design]），R5 只测过结果：
- R5 平地 → 下坡 5–30°（403 u/s）、下坡 → 平地（566 u/s）、V 形、坡顶都没有离地（R6）。HSD 的规则在这些情况下也不离地，对上了。
- **R5 走下平地台边是贴下去还是掉下去，没测过**。Source 的 StayOnGround 在平地上也会把 `stepHeight` 以内的落差贴下去；HSD 现在平地的落差 > 2 u 就掉下去。如果 R5 是 Source 的做法，走下 22 u 以内的路沿 R5 不离地，HSD 离地——跳得起来的时机、落地镜头都会不同。写进 `_notes`（B02-4）。
- 更快的速度、更大的折角会不会离地，R5 没测。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 坡上贴地的最大落差（= `stepUp`） | 0.457 m | HSD 设计值 18 u | 0.250 H | 改台阶高度时一起变 | [设计] |
| 平地上多大的落差算离地（= `groundProbe`） | 0.0508 m | 2 u | 0.0278 H | R5 平地行为没测 | [设计] / [反编译] 探测距离 |
| 120 Hz 下冲刺一条命令的水平位移 | 0.0633 m | 2.49 u（299 u/s × dt） | 0.0346 H | — | [算] |

用后两行估算：45° 以内的坡，冲刺一条命令的落差最多 2.49 u，远小于 18 u，所以能站的坡上贴地永远成立；滑铲 600 u/s 时一条命令 5 u，也够。

#### 实现模板

```
// 单位：u
slopeStick(m, g, drop):                   // world.beforeStep 里，§2.6
    return slopeMovement and m.grounded and groundProbe < drop <= stepUp
           and (m.groundNormal.z < FlatNormalZ or g.normal.z < FlatNormalZ)

afterStep 末尾:
    if slopeMovement and m.grounded:
        g = support(to)
        if (startedOnSlope or g.normal.z < FlatNormalZ) and to.z < g.height: to.z = g.height
```

Unity 参考实现：`U:…/World/MovementWorld.cs`：`BeforeStep`（"stay on the slope (StayOnGround)"那几行）、`AfterStep` 末尾的"never below a walkable top"、`stepSloped`；开关 `R5MotorV2Params.slopeMovement`。

#### 验收

- `MovementWorldTests.SlopeOptionWalksUpAndDownGroundedWithFlatVelocity`：20° 坡上下每条命令都着地。
- `MovementWorldTests.WithoutTheSlopeOptionTheBodyHopsDownASteepRamp`：40° 坡，开关关时 > 20 条命令离地，开时 0 条。
- R6 转折实测（"坡度变化处"表）：平地 → 下坡、坡顶冲刺 299 不离地，Unity 同。
- **缺**：平地走下路沿（2 / 8 / 16 / 22 u）的测试和 R5 对照（B02-4）。

#### 出处

- A4 §3 "Staying on the ground"：落差 ≤ 18 u、只在原来或新的地面是坡时贴地，[design]；平地落差照样掉。main
- R6 结论第 4 条、"坡度变化处"表：测过的转折都没有离地。main
- Source `gamemovement.cpp` `StayOnGround`（Source 2013 SDK 公开代码）：在平地上也把 `stepsize` 以内的落差贴下去。[推断]，R5 没读
- [反编译] 没有：R5 的贴地代码没读。

---

## 2.10 本章参数一览（给 tables/ 用）

参数名照 Unity 导出（`HSD-Unity: Docs/units/units-params.tsv`，HSD-Unity PR #88，还没合并；分支 `units/switch`）的写法。"路径"一列是导出里的 `param` 前缀；游戏身体的值在 `body.Reference.<装备>.motor.p.<名字>`，回放电机在 `preset.R5Reference.<名字>`。

| 名字 | 导出路径 | 量纲 | [m] | [u] / 原值 | R5 原值 | 本章 |
|---|---|---|---|---|---|---|
| `CommandRate` | `HSD.Game.PracticeSession`（常量，registry） | Rate | — | 120 /s | 可变（= 帧率） | §2.1 |
| `CommandDt` | 同上 | Time | — | 1/120 s | = frametime | §2.1 |
| `MaxCommandsPerFrame` | 同上（常量，未导出） | 次数 | — | 12 | — | §2.1 |
| `svGravity` | `preset.R5Reference.svGravity` | Acceleration | 19.05 m/s² | 750 u/s² | 750 | §2.3 |
| `gravityScale` | `preset.R5Reference.gravityScale` | Ratio | — | 1 | 1 | §2.3 |
| `stopSnapSpeed` | `preset.R5Reference.stopSnapSpeed` | Velocity | 0.0254 m/s | 1 u/s | (0.58, 1.58] | §2.3（第 03 章） |
| `hullRadius` | `world.default.hullRadius` | Length | 0.4064 m | 16 u | 没读 | §2.4 |
| `hullHeight` | `world.default.hullHeight` | Length | 1.8288 m | 72 u | 没读 | §2.4 |
| `crouchHullHeight` | `world.default.crouchHullHeight` | Length | 1.2192 m | 48 u | 没读（推 55.5 或 39） | §2.4 |
| `hullCrouchTime` | `preset.R5Reference.hullCrouchTime` | Time | — | 0.2 s | 0.2 | §2.4 |
| `airUnduckDrop` | `preset.R5Reference.airUnduckDrop` | Length | 0.4191 m | 16.5 u | 16.5 | §2.4 |
| `airUnduckMinAfterTakeoff` | `preset.R5Reference.airUnduckMinAfterTakeoff` | Time | — | 0.08 s | 0.08 | §2.4 |
| `MaxBumps` | `MovementWorld`（常量，未导出） | 次数 | — | 8 | 没读 | §2.5 |
| `groundProbe` | `preset.R5Reference.groundProbe` | Length | 0.0508 m | 2 u | 2.0 | §2.6 |
| （离地竖直速度） | 无（Unity 没有这个参数） | Velocity | 3.556 m/s | — | 140 u/s | §2.6 |
| `stepUp` | `world.default.stepUp` | Length | 0.4572 m | 18 u | **22 u** | §2.7、§2.9 |
| （滑铲上台阶减速） | 无（Unity 没做） | 1/s | — | — | 10 | §2.7 |
| `standableNormalZ` | `world.default.standableNormalZ` | Ratio | — | 0.7 | 0.7 | §2.8 |
| `FlatNormalZ` | `HSD.R5Replay.R5MotorV2`（常量，registry） | Ratio | — | 0.999 | 0.999 | §2.8 |
| `hullBottomRadius` | `body.Reference.*.motor.p.hullBottomRadius`（16）；`preset.R5Reference`、`world.default` 是 0 | Length | 0.4064 m | 16 u | 16（实测） | §2.8 |
| `slopeMovement`、`slopeUphillKeepStep` | 布尔开关，导出里没有 | — | — | Reference 开 | — | §2.8、§2.9 |

---

## 2.11 本章里 HSD 和 R5 的差别（汇总）

| # | 项 | R5 | HSD 现在 | 状态 |
|---|---|---|---|---|
| 1 | 命令时长 | = 每帧 frametime | 固定 1/120 s | 有意偏离，**没有 D 号**（建议见 `_notes`） |
| 2 | 台阶高度 | 22 u | 18 u（TF2 值） | **待定**，没实测，DIFF 没记（B02-1） |
| 3 | 蹲姿碰撞体 | 没读；由 16.5 推 55.5 或 39 | 48 [设计] | 待测（B01-1）；和 16.5 对不上 |
| 4 | 落地条件 | v_z ≤ 140 且 2 u 内 | v_z < 0 且 2 u 内 | 读代码发现，没测，DIFF 没记 |
| 5 | 空中迈台面 | 推断没有（Source 空中不迈台阶） | 脚离台面 ≤ 18 u 能越过 | 读代码发现，没测 |
| 6 | 平地走下台边 | 没测（Source 会贴下去） | 落差 > 2 u 就离地 | 没测（B02-4） |
| 7 | 碰撞和落地判断的先后 | 碰撞在前 | 落地判断在前（用命令开始时的地面） | 写法差别，最多晚一条命令，没测到影响 |
| 8 | 滑铲上台阶减速 | ConVar 10，是否生效没查 | 没做 | 没测 |
| 9 | 坡上走、圆底、上坡补步长 | — | 已按 R5（R6U U-1、U-2，D-45 / D-46） | 已改，Fun 保留旧版 |
