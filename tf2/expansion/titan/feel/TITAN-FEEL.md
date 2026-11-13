# 泰坦第一人称手感清单（TITAN-FEEL）

2026-11-13，会话 `titan-feel-doc`。给接下来的设计和试玩版（`titan/feel-build`）调参用。只借 TF2 的规则和数值，不用它的模型、动画、声音、截图。这份文档没有改 Unity 代码，也没有开游戏，全部来自已有的实测、设置文件和脚本。

## 先说结论（白话）

用户定的方向：响应快但有份量；轻、中、重三种底盘要明显拉开；优先第一人称；参考 TF2。对照下来：

1. **TF2 的"重"不在转向上。** 鼠标转向和铁驭完全一样，没有上限、没有平滑、没有滞后（实测）。只有手柄慢 25 %，起转也慢（0.8 s 对 0.33 s）。试玩版要加"转向上限"或"镜头滞后"的话，TF2 的值是**关**，应该默认关，只当实验开关。
2. **"重"主要来自四件事：**
   - **冲刺要等。** 到走速只要 0.19–0.24 s（响应快），但从走速加到冲刺跑速要 0.56–1.06 s。
   - **dash 少、回得慢。** 中型、重型只有 1 次，回满一次要 6–10 s；轻型 2 次。
   - **镜头弹簧硬、事件少。** 走路镜头每 0.70 s 只沉 0.3 u 左右，几乎看不出来；转身和 dash 时舱框落后屏幕，约 0.37 s 才回位。落地时低头，重型弹簧最硬，所以低头最小、回得最快。
   - **声音。** 舱内有一直响的引擎底噪，脚步、液压和伺服声由动画事件触发。我们现在只有 13 个程序合成的占位音，没有引擎底噪，也没人听过。
3. **TF2 三种底盘在镜头上几乎没拉开。** 舱框晃动、受击、dash 滚转、冲刺下沉、走路节奏三种底盘都一样。差别只在移动数值、dash，以及两个小弹簧：落地弹簧 35/9、65/15、95/30，踏步冲量 −6/−5/−4。而且方向和直觉相反：**轻型晃得更多，重型更硬、更稳**，TF2 是靠"硬"来表现重的。要像用户说的"明显拉开"，得在 TF2 的基础上加我们自己的差别。第 5 节列了 TF2 一样的那些项，第 6 节给了候选开关，标 `[design]`，默认值仍是 TF2。
4. **TF2 也不是每一项都"越重越慢"。** 重型从走速到冲刺最快（0.56 s，因为冲刺加速度 180 最大、两速差只有 100），落地低头最小。调参时别把每一项都按"越重越慢"去拉。
5. **Unity 现在（`titan/integration` 551b50e）：**
   - 电机、镜头、舱框、开机、受击、落地都已经按 TF2 做了，带出处。
   - 只有中型能开：`PracticeGame.cs:211` 写死了默认的 `TitanChassis.Medium()`。轻型、重型只有参数。
   - 主要缺：手柄的泰坦视角表、舱内炮的走路摆动（bob / sway）、舱内引擎底噪和几类 1P 声音、三种底盘各自的舱框。
   - 只在少数几处要补测 TF2（第 7 节）。不补测也能先试玩。

**标记：** `[meas]` 本地 Northstar 逐帧实测；`[file]` 设置文件、脚本、ConVar；`[算]` 由实测或文件算出；`[guess]` 推测，没直接验证。Unity 状态：✅ 已做　◐ 部分　❌ 没有。

**单位：** 1 u = 2.54 cm。三种底盘：轻 = Stryder（Ronin、Northstar），中 = Atlas（Ion、Tone、Monarch），重 = Ogre（Scorch、Legion）。

**Unity 基准：** HSD-Unity `titan/integration` 551b50e（HSD-Unity #78，不合 main）。它已经包含 `titan/full` cc4cbaa、`titan/full-fix1` 6d2e8d0、`titan/cam` 9b802bc 等全部分支（`git merge-base --is-ancestor` 查过）。下面的路径都相对 `Assets/HSD/Game/Runtime/Titan/`。

**范围（11-13 lead 通知）：** 这份清单只管第一人称手感：移动、镜头、驾驶舱、声音。7 台套件、BT 和各底盘配哪些武器技能，归另开的"泰坦武器和技能"工作线。"开火后坐"只写镜头和手感的部分。表里涉及武器和技能的几行只留指向。

---

## 1. 操作响应

| 项 | TF2 怎么做 | 出处 | Unity 现状 | 三种底盘数据 | 缺口 |
|---|---|---|---|---|---|
| 走速 / 冲刺跑速 | 270 / 400、250 / 380、210 / 310 u/s；后退、横移和前进一样（`speedScaleSide/Back` 1.0） | [meas] T0 §3.1；[file] `titan_*.set` | ✅ `TitanChassis` | 齐 | — |
| 起步（0 → 走速） | 两段加速：低于 `lowSpeed`（230 / 200 / 160）用 `lowAcceleration`（1600 / 1500 / 1400），之后用 `acceleration`（1000 / 900 / 380）。到走速 0.19 / 0.19 / 0.24 s | [meas] T0 §3.1；规律 713-RECORD §9.3 | ✅ `TitanMotor.AlongStep`，测试对过 T0 | 齐 | — |
| 走 → 冲刺跑 | 走速以上用很慢的 `sprintAcceleration`：150 / 120 / 180 u/s²。从走速开始 0.83 / 1.06 / 0.56 s，从静止开始 1.02 / 1.25 / 0.80 s | [meas] 713-RECORD §9.3（注意 T0 表的秒数是从静止算的） | ✅ 同上 | 齐 | 写测试时分清"从静止"和"从走速" |
| 停步（松手） | 走速以下按 `deceleration` 1800 / 1500 / 1200 减速，实测 1770 / 1500 / 1165 u/s²，0.15 / 0.17 / 0.18 s 停住。从冲刺跑松手：先按 `sprintDeceleration` 减到走速，再按 `deceleration` 减到 0，约 0.37 / 0.35 / 0.34 s，平均 1066 / 1070 / 892 u/s² | [meas] T0 §3.1；[算] | ✅ `TitanMotor.StopStep` | 齐 | — |
| 身体比速度慢半拍 | 停步后约 0.2 s 换到待机姿势；起步时 0.2 s 混入走、0.55 s 换到跑；播放速度有 0.15 死区。第一人称看不到 | [meas] REF-GAIT §1、§3 | ◐ 身体走 B-沉 / 地形占位 v1，和第一人称无关 | — | 第一人称不受影响，不追 |
| 转向（鼠标） | 和铁驭完全一样：2000 计数都转 144.78°，**没有上限、没有平滑**，松手当帧停。ADS 用 `mouse_sensitivity_zoomed` × tan(zoom_fov / 2) ÷ tan(37.5°) | [meas] T0 §2.1、§2.5 | ✅ 用游戏本身的鼠标，没有加泰坦系数 | 三种底盘一样 | 试玩版要加的"转向上限"在 TF2 里**没有**，默认关（第 6 节 `turnRateCap`） |
| 转向（手柄） | 泰坦单独一张视角表 `looksensitivity_titan.txt`：最大转速 × 0.75；第 2、3 档起转时间 0.8 s（铁驭 0.33 / 0.3 s） | [file] T0 §2.2 | ❌ Titan 代码里没找到手柄的泰坦表 | 三种底盘一样 | 要做；见开关 `padTurnScale`、`padRampTime` |
| 临时转向减慢 | 只有技能和受控状态：`turn_slow` 缩放**输入**，约 × (1 − 2 × 强度)，不限角速度。Ion 激光核心 0.25 → 鼠标转速减半；被 EMP 0.35 | [meas] T0 §2.3、§2.5 | ❌（技能没做） | — | 规则留给"泰坦武器和技能"工作线；这里只记一条：要减慢就缩放输入 |
| dash 推力曲线 | 按下当帧到 `dodgeSpeed`（800 / 700 / 600），保持 0.2 s，然后按 `sprintDeceleration`（600 / 700 / 600）降回走速。dash 后 0.3 s 实测 620 / 486 / 416 u/s，和算的一致。**没有起步爬升**，是一下推出去 | [meas] T0 §3.1；规律 713-RECORD §9.3 | ✅ `TitanMotor`（`TitanDashPhase.Hold/Decay`） | 齐 | — |
| dash 距离 | 一次约 633 / 445 / 383 u，用时约 1.08 / 0.84 / 0.85 s（按上面的规律从走速算） | [算] | 同上 | 齐 | — |
| dash 次数 / 冷却 | 能量 100：每次耗 50 / 100 / 100，回能 10 / 16.66 / 9.9 每秒，用完后延迟 0.2 / 0.2 / 0.3 s 才开始回。所以轻型 2 次、每次 5 s 回一格，中型 1 次、6.0 s，重型 1 次、10.1 s。两次 dash 至少隔 0.35 / 0.3 / 0.2 s（`dodgeInterval`） | [meas] T0 §3.1；[file] 每台泰坦的设置文件覆盖底盘值 | ✅ `TitanChassis`（`dodgePower*`） | 齐 | dash 能量在 HUD 上怎么显示是我们的设计 |
| dash 方向 | 按移动方向；四个方向速度相同。左右 dash 有镜头滚转，前后没有（第 2 节） | [meas] POSE §4.2 | ✅ 没输入时向视线前方 | 齐 | — |
| 冲刺跑条件 | 只能向前；dash 不打断冲刺。冲刺跑时 FOV 不变 | [meas] POSE §4.1 | ✅ `sprinting = sprint && forward > 0` | 齐 | — |
| 蹲 | 速度 187 / 150 / 112，加速 250 / 200 / 150，减速 625 / 500 / 375；眼高 185 → 125；碰撞体 235 → 140；蹲下站起的高度平滑过渡 | [file] T0 §3.2、`titan_base.set` crouch 段；[meas] POSE §4.1 | ✅ 速度和碰撞体；◐ 眼高按 300 u/s 匀速变（`eyeBlendRate` `[placeholder]`） | 速度齐；眼高过渡曲线没测 | 过渡时长没测，现在 0.2 s 是占位 |
| 跳 | TF2 泰坦不能跳（`jump 0`）。我们加了一个推进器小跳，默认开 | [file]；PLAN 决定 1 `[design]` | ✅ `hopEnabled` | — | 是我们的设计，试玩时问用户 |
| 斜坡 | 9° 坡上水平速度不变（250 / 100 u/s 上下坡都一样）。更陡的坡没测成 | [meas] REF-GAIT §4 | ◐ 借铁驭的 `MovementWorld` 走坡，泰坦在坡上没验证 | 只有中型 9° | 13° 以上和最大坡度没测。"爬坡减速"在 TF2 至少 9° 以内**没有** |
| 台阶 | `stepheight` 80：碰撞体一个 tick 迈上去，画面平滑跟上 | [meas] REF-GAIT §4；[file] | ✅ `stepSmoothTime` 0.12 s `[placeholder]` | 齐 | 平滑时长没测 TF2 的镜头值（REF-GAIT 量的是骨盆） |
| 撞墙 | 没有专门的撞墙规则（设置文件没有） | [file] | ◐ 有 `wallHit` 事件，没有镜头反馈 | — | 要不要撞墙震一下是我们的设计 |

## 2. 镜头

TF2 的第一人称镜头**不挂在身体上**。身体动画在第一人称里看不见，镜头全部由程序算。只有上机、下机、弹射、近战这几个脚本序列由动画驱动（ANIM-FEEL §1.5）。

| 项 | TF2 怎么做 | 出处 | Unity 现状 | 三种底盘数据 | 缺口 |
|---|---|---|---|---|---|
| 走路起伏 | **定时器**：走每 0.70 s、冲刺跑每 0.417 s 一次，不跟动画步频（动画一步 0.585 s，会漂）。每步是一次竖直速度冲量 `cockpit_stepJolt` −6 / −5 / −4 u/s，打进舱体弹簧（k 65，d 9），下沉峰峰 0.42 / 0.35 / 0.28 u，0.146 s 到底，回弹 +12 %。按键后约 0.03 s 就有第一步。没有旋转 | [meas] GAPS §6；[file] `footstepInterval` 700、`footstepIntervalSprint` 415 | ✅ `TitanCamParams`（`stepWalk`、`stepSprint`、`stepJolt`） | 齐（实测三种底盘） | — |
| 蹲走起伏 | 设置文件写 `footstepInterval` 500 ms；Unity 实测幅度约一半（−0.16 u 对 −0.32 u），节奏用的是 0.70 | [file]；[meas] HANDOFF-1107 | ◐ `crouchStepScale` 0.5，节奏 0.70 | 只有中型 | 蹲走节奏 0.5 还是 0.7 没定，日志间隔不齐 |
| 冲刺下沉 | 冲刺跑时镜头下沉 25 u（`sprintViewOffset` −25），1.0 s 进、0.3 s 出；实测 25.6 / 25.6 / 25.4 u | [file] `sprintStartDuration` 1、`sprintEndDuration` 0.3；[meas] T0 §2.4 | ✅ `sprintDrop`、`sprintIn`、`sprintOut` | 齐 | — |
| 冲刺摆动 | 周期约 0.83 s（两步）：俯仰 −1.06…+0.51°，左右 ±1.1°，滚转 0…1.76°。设置文件 `sprinttiltMaxRoll` 4 / 3 / 2，但实测三种底盘都是 1.76° | [meas] POSE §4.2、T0 §2.4 | ✅ 傅里叶拟合（`SwayPitch/Yaw/Roll`，Ion 的日志） | ◐ 只拟合了中型；轻、重型只量了滚转 | 轻、重型的俯仰和左右摆动没拟合。按"三种相同"先用 |
| 落地 | 只有低头和一点随机滚转，**镜头不下沉**。落地速度 ≤ 381 u/s 没有，≥ 410 u/s 有。冲量 v₀ = 40 °/s × scale，scale 从 1（395 u/s）线性到 6（1450 u/s），每次 ±15 % 随机；打进 punch 弹簧 35/9、65/15、95/30。1068 u/s 落地时峰值 12.9 / 8.5 / 5.1°；1000 u/s 时滚转约 ±2° | [meas] GAPS §1；[file] `punch_titan_*`、`viewkickFallDistMaxScale` 6 | ✅ `landV0`、`landMinSpeed`、`punchK/D` 等 | 齐 | 1450 u/s 以上饱和是推断（样本 3 个） |
| 硬落地 | 没有软硬之分，只有一条连续曲线加一个门槛。`hardFallDist` 40 只触发"重落地"的**声音** | [file]；[meas] GAPS §1 | ◐ `hardFall` 标志有了，没接声音 | — | 硬落地声音（第 4 节） |
| dash 推背 | **左右 dash** 滚转 ∓8.5°，0.18 s 到顶，约 0.5 s 回零。**前后 dash 没有旋转，FOV 不变**。舱框整体下压（前 dash 上沿 +24 px，0.11 s 峰，0.43 s 回零）；镜头只沉 0.26–0.39 u | [meas] POSE §4.2、T-f §1.3；[file] `dodge_viewTilt*`、`dodge_cockpitTiltMax` 4、`dodge_cockpitOffsetMax` 3 | ✅ `dashRollPeak` 8.6、`dashFrameUnits`、`dashFrameRoll` | 齐（三种相同） | TF2 的"推背"只靠舱框动和声音，**没有 FOV 冲击**。试玩版要加的 dash FOV 是我们的设计，默认 0 |
| 受击 | 驾驶舱弹簧冲击：强度 = min(伤害 / 2000, 1)，旋转 7° × 强度，位移 7 u × 强度，朝来源方向。约 0.26 s 峰值，0.57 s 过零，反向过冲 +0.84°，约 1.4 s 平息。**三种底盘相同**。舱框跟着画面一起动（小伤害 300：舱框偏 5–10 px） | [meas] POSE §4.4、T-f §1.3；[file] `COCKPIT_MAX_JOLT_DAMAGE` 2000 | ✅ `hitDegrees`、`hitUnits`、`hitFullDamage` | 齐 | 右侧、背后、有高度差的来源没测，方向按推断 |
| 开火后坐 | 每把枪自己的弹簧，R5 同样的规律（`hardScale` 加角度、`softScale` × 20 加角速度，画面 = (1 − weaponFraction) × punch）。XO-16 镜头几乎不动（连射 3.3 s 俯仰最多 0.2°），Ronin 散弹一枪 −6.2…−8.2° 于 0.05 s，Legion ±0.5° | [meas] GAPS §4 | ✅ 有两套：`TitanRecoil.Designed`（我们的炮）和 `Xo16`；`recoilScale` 等 | 按武器，不按底盘 | — |
| 换弹镜头 | TF2 换弹时 1P 武器动画带着镜头角度摆（Monarch 俯仰 −1.2…+4.4°），位移 0 | [meas] GAPS §4 | ◐ 我们的炮换弹动作是自己的设计（决定 4），`cameraCues` 开关 | — | 只借幅度 |
| 转向时的滞后 | **视角没有滞后**（鼠标 1:1）。滞后的是**舱框**：转身时舱框向反方向落后，满速时 −33…−37 px（约屏宽 2.7 %），停下后时间常数约 0.37 s 回位；俯仰也一样（44 °/s 时 0.2 s 落后 8 px，还在增大）。三种底盘逐像素相同 | [meas] GAPS §5、T-f §1.2–1.3；[file] `cockpitSwayGain` 3、`cockpitSwayTurnAngleFactor` −4 | ✅ `swayTau` 0.37、`swayFullRate`、`swayUnits`、`swayDegrees` | 齐 | 俯仰的稳定值没拍到 |
| 近战、核心、弹射 | 近战约 0.8 s 动画镜头（左右 +22 / −14°）；核心启动小抖；弹射强制低头约 80° | [meas] POSE §4.5 | ◐ 近战、弹射有；核心没做 | — | 归"泰坦武器和技能"工作线 |
| FOV | 固定 75，所有状态都不变（冲刺、dash、受击） | [meas] POSE §4.1 | ✅ `TitanCamera.SourceFov` 75 | 齐 | — |
| 屏幕震动传给枪 | 只传 10 %（`shake_viewmodelFactor_titan` 0.10） | [file] ANIM-FEEL F13 | ❌ 舱框和炮在自己的相机上，不受震动 | — | 小项 |

## 3. 驾驶舱和 HUD

| 项 | TF2 怎么做 | 出处 | Unity 现状 | 三种底盘数据 | 缺口 |
|---|---|---|---|---|---|
| 看得见什么 | 舱框（屏幕四边）、右下的手和枪、贴在舱框上的 HUD。**看不到自己的腿、脚、躯干** | [meas] POSE §5.1 | ✅ `TitanCockpitView`：灰盒舱框和炮，有自己的相机，深度上梁 110 u、柱 60 u | 三种底盘各一个舱模型（`pov_titan_light/medium/heavy_cockpit.mdl`），但晃动规则相同 | ❌ 只有一套舱框。三种底盘的舱框外形要不要不同，由我们设计 |
| 舱框相对屏幕 | 视角事件（落地、开火、受击）带着舱框一起动，舱框相对屏幕几乎不变；转身、俯仰、dash 才有明显相对运动（第 2 节）。走路时舱框有约 10 px 的持续偏移，单步起伏分辨不出 | [meas] GAPS §5 | ✅ `moveForwardYaw/Pitch` 等 | 齐（三种相同） | 横移数据不可靠 |
| 舱内枪的摆动 | 枪的 bob 周期 0.69 s，和舱内 0.70 s 同拍。通用值：`bob_vert_dist` 0.6、`bob_horz_dist` 0.1、`bob_max_speed` 150、`bob_pitch/yaw/roll` 0.75 / −1.7 / −1.2；sway 平移增益 4、旋转 7；前进时枪下沉 −2.7；转身时枪滚转 ±4、抬低头 ±3。重枪 Legion：bob 2 / 2.25、转身滚转 ±1 | [file] ANIM-FEEL F13、`anim/out/weapon_sway.csv` | ❌ 炮在舱框相机上不动，没有 bob / sway | 按武器 | **要做**。这是 TF2 舱内"在走路"的主要画面，比镜头起伏明显 |
| 视野 / FOV | 75°（Source 4:3 水平），驾驶时不变 | [meas] | ✅ 换算成 Apex FOV 设置 | 齐 | — |
| 眼高 | 185 u，蹲 125 u；三种底盘相同 | [meas] T0 §2.4 | ✅ `eyeHeight` | 齐 | 用户要拉开底盘的话，眼高是候选（第 6 节，`[design]`） |
| 开机 | 进舱前 0.40 s 开始变黑，0.17 s 起全黑；进舱后 0–0.25 s 近乎全黑，只有暗的线框和一条黄色进度块；然后整个画面分 5 块直接亮起：左 0.25、中 0.50、右 0.75（枪在这里出现）、上 1.00、下 1.25 s；约 1.4 s 稳定。没有色差。曝光 −6 闪 0.1 s 原版会调用，但落在黑场里看不出。LCD 开机特效 2.05 s 是材质 | [meas] GAPS §2；[file] T-f §2 | ✅ `TitanBoot`（时间都对上了，遮罩边缘是我们的设计）；❌ 曝光闪、LCD 2.05 s 特效 | 三种相同 | 曝光闪看不见，可不做。LCD 特效的样子是我们的设计 |
| 上机 / 下机 | 上机动画 3.33–3.45 s，其中约 3.25 s 是第一人称镜头动画（铁驭爬上去）；下机 1.03–1.42 s，切回铁驭后低头约 43°、约 1.6 s 落定 | [meas] T0 §1、POSE §4.5、GAPS §2 | ✅ `embarkSeconds` 3.45、`disembarkSeconds` 1.2，上机镜头路径按实测 | ◐ 每种底盘的上机时长没分开量 | 小项 |
| HUD 布局 | 小地图左上贴舱框；血条在顶部横梁；技能和弹药在左下 | [meas] POSE §5.1 | ✅ `TitanCockpitHud`，读数挂在舱框上一起晃 | — | 外观是我们的设计 |
| 受伤表现 | 护盾被打青闪、船体被打红闪、火花（每损失 1000 血按比例，濒死 20 束，6 处面板）、濒死舱框亮橙红（0.6, 0.06, 0）、EMP 碎屏；受击色差 0.2、受伤色差 0.4 | [meas] POSE §5.1；[file] GAPS §2 | ✅ `TitanDamageCockpit`、`TitanCockpitFx` | — | 受击色差没做（小项） |

## 4. 声音

**现状：** Unity 有 13 个程序合成的占位音（`Damage/TitanSynth.cs`）：脚步、伺服、开机、警报、dash、护盾受击、船体受击、爆炸、弹射、按键、炮、火箭、换弹咔哒。只验证过混音器有输出，没人听过，全部 `[placeholder]`。**舱内引擎底噪没有**，而 TF2 舱内声音最一直存在的就是它。

下面列 TF2 有哪些类别、由什么触发。**只列类别和触发方式，不用 TF2 的声音本身。** 声音名只用来说明出处。

| 类别 | TF2 由什么触发 | 例子（出处） | 我们现在 | 要做的 |
|---|---|---|---|---|
| 舱内引擎底噪（循环） | 身份换成泰坦时开始循环，下机或死亡时停；同时各播一下进舱、出舱提示音 | `titan_<泰坦名>_int_engine`、`sse_titancockpit_enter` / `_exitdefault`（`client/cl_titan_cockpit_sounds.gnut:75–101`）[file] | ❌ | **要做**。每种底盘一条，音高和音量可以用来拉开底盘（`[design]`） |
| 开机（上电） | **上机动画的事件**里调 `play_startup_sound` 回调；直接以泰坦身份出生时就听不到 | 脚本注释 `cl_titan_cockpit_sounds.gnut:75`；事件 `AE_SV_VSCRIPT_CALLBACK play_startup_sound`（`anim/ref-upper/out/ev_opts_*.csv`）[file] | ◐ 进舱那一刻播"boot" | 改成跟上机时间线走（舱门关、进舱、分块亮起） |
| 舱门 | 上机动画事件 | `titan_embark_hatch_close` [file] | ❌ | 要做 |
| 脚步（自己的，第一人称） | 设置文件有 `footstepInterval` 和 `footstepWalkSoundRadius` / `footstepRunSoundRadius`（700 / 1000），`footstep_type`（atlas / ogre…）按底盘选声音。Source 的玩家脚步声一般跟这个定时器走 | [file] `titan_base.set` stand 段、`titan_*.set`；"跟定时器"是 [guess] | ◐ 跟身体动画的落脚事件播"step"，自己时音量 0.55 | **要定**：跟镜头定时器（和画面同拍）还是跟动画。TF2 的第一人称到底用哪个没验证。开关 `stepSoundSource` |
| 脚步（别人看到的，第三人称） | 动画事件：每步 `AE_FOOTSTEP_L/R`，加上 `AE_CL_PLAYSOUND_FOR_TYPE` 的走 / 跑 / 冲刺 / 蹲层（`Jog.Generic_3P`、`Sprint.Generic_3P`、`Crouch.Generic_3P`、`shuffle_generic_3p`） | `anim/ref-upper/out/ev_opts_medium.csv`（中型约 900 个脚步事件）[file] | ✅ 跟动画落脚事件 | 声音本身要做；脚步声比完全踩实早约 0.07 s（ANIM-FEEL F8） |
| 液压 / 伺服 / 关节 | 动画事件，和脚步分开的几层：`exo_servo`、`exo_hip`、`exo_knee`、`exo_stomp`，走路的 `jog_servo_3p`、`jog_movement_3p` | 同上 [file] | ◐ 换步态时播一下"servo"（`TitanDamageView.cs:158–162`） | 要做：至少"伺服"和"踏地"两层，跟动画事件 |
| dash | 设置文件按底盘：`sound_dodge_1p` / `_3p`（轻 `stryder_dash_*`、中 `tone_dash_*`、重 `ogre_dash_*`），dash 失败另有一个；落地段动画再播一次冲刺脚步层 | `titan_stryder/atlas/ogre.set` [file] | ◐ 一个"dash" | 要分 1P / 3P，每种底盘一个；能量不够时的失败音 |
| 蹲下 / 站起 | 设置文件按底盘：`sound_standToCrouch` / `sound_crouchToStand` | 同上 [file] | ❌ | 要做 |
| 落地 | `sound_groundImpact`（`Titan.GroundImpact`）；`hardFallDist` 40 以上另有重落地声 | [file] | ❌（落地只有镜头） | 要做，按落地速度分轻重 |
| 下机 | 动画事件（`disembark_kneel`、`*_disembark_stand`） | [file] | ❌ | 要做 |
| 低血量警报 | HUD 循环：没有护盾、血量低时每隔"声音长度 + 0.25 s"响一次 `titan_damage_beep`；濒死另换一套 | `titan/cl_titan_hud.gnut:378–410` [file] | ◐ 濒死时持续"alarm" | 加"护盾没了、血低"这一档的间隔提示音 |
| 护盾 | 护盾打空 `titan_energyshield_down`、恢复 `titan_energyshield_up` | `weapons/_weapon_utility.nut:3408` 等 [file] | ◐ 有护盾受击音，没有打空 / 恢复 | 要做 |
| 受击 | 子弹打到护盾、打到船体各有一类；暴击给攻击者 `titan_damage_crit` | [file] | ◐ shield / hull 两个 | 够用 |
| 威胁提示 | 被锁定 `Titan_Cockpit_TitanLocking_Warning`；火箭接近 `titan_cockpit_missile_close_warning` | `weapons/cl_smart_ammo.gnut:13`、`mp_weapon_rocket_launcher.nut:47` [file] | ❌ | 有敌方火箭以后再做 |
| 武器 | 武器文件里的开火 1P / 3P、换弹分段（`Wpn_XO16_3P_Reload_Pt1…9` 跟换弹动画事件）、空仓 `titan_dryfire` | [file] | ◐ 炮、火箭、换弹咔哒 | 归"泰坦武器和技能"工作线（换弹按我们自己的三个时刻分段） |
| 弹射 | 一串：按键提示、警报、推进、上升、顶点、下落 | `client/cl_titan_cockpit.nut:996–1179` [file] | ◐ 按键、发射 | 小项 |
| 核心、技能 | 每个核心有启动、循环、结束音 | [file] | ❌（技能没做） | 归"泰坦武器和技能"工作线 |
| 语音（泰坦 OS） | 对话系统（`conversation/`）按事件播语音 | [file] 只确认了系统存在 | ❌ | 要不要语音是我们的设计 |

**触发方式归纳：**

| 触发方式 | TF2 里用它的 |
|---|---|
| 身份切换 / 进舱出舱 | 引擎底噪、进舱出舱提示 |
| 动画事件 | 开机上电、舱门、第三人称脚步、液压伺服、dash 落地、下机、第三人称换弹 |
| 设置文件里的引擎事件 | dash、蹲起、落地、（多半还有）第一人称脚步 |
| 脚本回调 | 受击、护盾、威胁提示、弹射 |
| HUD 循环 | 低血量警报 |

## 5. 三种底盘差别表

"TF2 同"表示三种底盘在 TF2 里数值相同。"缺"是没有数据。

| 项 | 轻 | 中 | 重 | 出处 | 备注 |
|---|---|---|---|---|---|
| 走速 | 270 | 250 | 210 | [meas] T0 | 铁驭 173.5 |
| 冲刺跑速 | 400 | 380 | 310 | [meas] | |
| 0 → 走速 | 0.19 s | 0.19 s | 0.24 s | [meas] | |
| `acceleration`（lowSpeed 到走速） | 1000 | 900 | 380 | [file] | 重型这一段很慢 |
| 走速 → 冲刺跑速 | 0.83 s | 1.06 s | 0.56 s | [meas] | **重型最快** |
| 松手减速 | 1770 | 1500 | 1165 u/s² | [meas] | |
| dash 速度 | 800 | 700 | 600 | [meas] | |
| dash 距离 | ≈ 633 u | ≈ 445 u | ≈ 383 u | [算] | |
| dash 次数 | 2 | 1 | 1 | [meas] | 多人设置；底盘文件本身写的是 4 / 3 / 2 |
| 每格回能时间 | 5.0 s | 6.0 s | 10.1 s | [算] 耗能 ÷ 回能 | |
| 蹲速 | 187 | 150 | 112 | [file] | |
| 落地 punch 弹簧 k / d | 35 / 9 | 65 / 15 | 95 / 30 | [file] | 轻型软、有过冲；重型硬 |
| 落地低头（1068 u/s） | 12.9° | 8.5° | 5.1° | [meas] | 冲量相同，差别全在弹簧 |
| 踏步冲量 | −6 | −5 | −4 u/s | [file] | 轻型起伏最大 |
| 走路镜头起伏（峰峰） | 0.42 u | 0.35 u | 0.28 u | [meas] | |
| `sprinttiltMaxRoll` 设置 / 实测 | 4 / 1.76° | 3 / 1.76° | 2 / 1.76° | [file] / [meas] | 设置值不起作用 |
| 冲刺下沉 | 25.6 u | 25.6 u | 25.4 u | [meas] | TF2 同 |
| 冲刺摆动 俯仰 / 左右 | 缺 | −1.06…+0.51° / ±1.1° | 缺 | [meas] 中型 | 按 TF2 同处理 |
| 步伐定时器 | 0.70 / 0.417 s | 同 | 同 | [meas] | TF2 同 |
| 舱框晃动（转身、俯仰、dash） | 同 | 同 | 同 | [meas] T-f §1 | TF2 同 |
| 受击镜头 | 同 | 同 | 同 | [meas] | TF2 同 |
| dash 滚转 | 8.5° | 8.5° | 8.5° | [meas] | TF2 同 |
| 眼高 / 碰撞体 | 185 / 120 × 235 | 同 | 同 | [meas] | TF2 同 |
| FOV | 75 | 75 | 75 | [meas] | TF2 同 |
| 鼠标转速 | × 1 | × 1 | × 1 | [meas] | TF2 同 |
| 手柄转速 | × 0.75 | × 0.75 | × 0.75 | [file] | TF2 同 |
| 舱模型 | 轻 | 中 | 重 | [file] | 外形不同，晃动相同；外形没看过（不看截图） |
| 引擎底噪 | 按泰坦名 | 按泰坦名 | 按泰坦名 | [file] | 声音不同，内容不借 |
| dash、蹲起声 | stryder | tone / ion | ogre / scorch | [file] | 每种底盘一套 |
| 脚步声类型 | 按底盘 | `atlas` | `ogre` | [file] | |
| 上机时长 | 缺 | 3.33–3.45 s | 缺 | [meas] 中型 | |
| 登场动画长 | 6.433 s | 6.667 s | 6.667 s | [file] | |
| ADS 走速（武器决定） | Ronin 135 | Ion 188、Monarch 100 | Legion 116 | [meas] T0 §3.3 | 按武器；归武器和技能工作线 |
| 身体：走路周期 | 1.0 s | 1.133 s | 1.133 s | [file] 动画 | 第一人称看不到 |
| 身体：上身跟随滞后（300 °/s） | 20.7° | 27° | 40° | [meas] GAPS §8 | 第三人称才看得到 |

**要明显拉开，可以拉的地方（我们的设计，不是 TF2）：** 表里"TF2 同"的项里，对第一人称影响最大的是走路起伏、舱框晃动、冲刺摆动、眼高和引擎底噪。第 6 节给这些项各留了一个按底盘的倍数，默认 1（等于 TF2）。

## 6. 建议的可调开关（给试玩版）

**规则：**
- 默认值一律等于 TF2（或 Unity 现在的值，它本来就按 TF2 做）。
- 每种底盘一套值。表里写"轻 / 中 / 重"的是三套不同的默认值，只写一个数的是三种相同。
- 没有 TF2 依据的开关标 `[design]`，默认关或为 0，只当实验用。
- 名字按现有代码的写法；代码里已有的写出字段名，没有的写"新"。

### 6.1 操作响应

| 开关 | 范围 | 默认（TF2） | 代码里 | 为什么能体现份量 |
|---|---|---|---|---|
| `walkSpeed` | 150–350 u/s | 270 / 250 / 210 | `TitanChassis` | 顶速低是最直接的"重" |
| `sprintSpeed` | 220–480 u/s | 400 / 380 / 310 | 同上 | 同上 |
| `lowAcceleration` | 600–3000 u/s² | 1600 / 1500 / 1400 | 同上 | 决定起步第一下有多"跟手"，响应快就靠它 |
| `acceleration` | 200–1500 u/s² | 1000 / 900 / 380 | 同上 | lowSpeed 到走速这一小段的拖拽感；重型 380 是"推不动"的感觉 |
| `sprintAcceleration` | 60–400 u/s² | 150 / 120 / 180 | 同上 | **"重"最大的来源**：按了冲刺要等 0.5–1 s 才拉满 |
| `deceleration` | 600–3000 u/s² | 1800 / 1500 / 1200 | 同上 | 松手还滑一段 = 惯性；太小会觉得滑，不是重 |
| `sprintDeceleration` | 300–1500 u/s² | 600 / 700 / 600 | 同上 | 同时决定 dash 后多久收住、冲刺松手滑多远 |
| `dodgeSpeed` | 400–1000 u/s | 800 / 700 / 600 | 同上 | dash 冲出去的那一下 |
| `dodgeDuration` | 0.1–0.4 s | 0.2 | 同上 | 推力保持多久；越长越像被推着走 |
| `dodgePowerDrain` | 25–100 | 50 / 100 / 100 | 同上 | 决定能连 dash 几次 |
| `dodgePowerRegen` | 5–30 /s | 10 / 16.66 / 9.9 | 同上 | dash 稀缺 = 每次 dash 都是一个决定 |
| `dodgePowerDelay` | 0–1 s | 0.2 / 0.2 / 0.3 | 同上 | |
| `crouchSpeed` | 80–250 u/s | 187 / 150 / 112 | 同上 | |
| `mouseTurnScale` | 0.5–1.0 | 1.0 | 新 | TF2 = 1。只缩放输入，不限角速度（照 `turn_slow`）。小于 1 是实验，T0 认为会"卡手" |
| `turnRateCap` | 0（关）–720 °/s | 0（关） | 新，feel-build 计划中 | TF2 没有。`[design]`，只当对比实验 |
| `viewTurnLag` | 0–0.3 s | 0 | 新，feel-build 计划中 | TF2 视角没有滞后，滞后的是舱框（见 `swayTau`）。`[design]`，默认 0 |
| `padTurnScale` | 0.5–1.0 | 0.75 | 新 | TF2 唯一常驻的泰坦转向差异（只对手柄） |
| `padRampTime` | 0–1.2 s | 0.8 | 新 | 手柄推满到满速的时间，铁驭是 0.33 |
| `hopEnabled` / `hopSpeed` | 开关 / 150–400 u/s | 开 / 274 | `TitanTuning` | TF2 没有，`[design]`（PLAN 决定 1） |

### 6.2 镜头

| 开关 | 范围 | 默认（TF2） | 代码里 | 为什么能体现份量 |
|---|---|---|---|---|
| `stepWalk` / `stepSprint` | 0.4–1.2 s / 0.3–0.8 s | 0.70 / 0.417 | `TitanCamParams` | 步子慢 = 大机器。TF2 三种底盘相同；按底盘拉开是 `[design]` |
| `stepJolt` | 0 到 −20 u/s | −6 / −5 / −4 | 同上 | 每步的"咚"。TF2 是轻型最大。要"重型更沉"就反过来调，`[design]` |
| `cockpitK` / `cockpitD` | 20–200 / 3–40 | 65 / 9 | 同上 | 舱体弹簧：硬 = 金属感，软 = 晃荡 |
| `punchK` / `punchD` | 20–200 / 3–40 | 35 / 9、65 / 15、95 / 30 | 同上 | 落地低头的大小和回弹：重型硬、回得快 |
| `landV0` | 0–80 °/s | 40 | 同上 | 落地低头的总量 |
| `landMinSpeed` | 200–600 u/s | 395 | 同上 | 多高掉下来才有反应 |
| `sprintDrop` | 0–40 u | 25 | 同上 | 冲刺时"压低身子"的感觉 |
| `sprintIn` / `sprintOut` | 0.2–2 s / 0.1–1 s | 1.0 / 0.3 | 同上 | 进得慢 = 有份量的加速 |
| `sprintSwayScale` | 0–2 | 1.0 | 新（乘在拟合曲线上） | 冲刺摆动的幅度；TF2 三种相同，按底盘拉开是 `[design]` |
| `dashRollPeak` | 0–15° | 8.6 | 同上 | 左右 dash 被甩出去的感觉 |
| `dashFrameUnits` / `dashFrameRoll` | 0–15 u / 0–8° | 7.3 / 4 | 同上 | dash 时舱框被压下去 = 推背感 |
| `dashFovKick` | 0–10° | 0 | 新，feel-build 计划中 | TF2 没有，`[design]` |
| `hitDegrees` / `hitUnits` | 0–15° / 0–15 u | 7 / 7 | 同上 | 挨打时整个舱被撞一下 |
| `swayTau` | 0.1–1.0 s | 0.37 | 同上 | 舱框转身后多久回位：越大越像大质量跟不上 |
| `swayUnits` / `swayDegrees` | 0–8 u / 0–4° | 3 / 1.5 | 同上 | 舱框最多落后多少（`cockpitSwayGain` 3 × 文件值） |
| `swayGainScale` | 0–2 | 1.0 | 新（乘在上面两项上） | 按底盘拉开舱框晃动，`[design]` |
| `fov` | 60–90 | 75 | `TitanCamera.SourceFov`（常量） | TF2 固定；做成可调只为了试 |

### 6.3 驾驶舱和枪

| 开关 | 范围 | 默认（TF2） | 代码里 | 为什么能体现份量 |
|---|---|---|---|---|
| `gunBob`（开关） | 开 / 关 | 开 | 新 | 舱内炮跟着步子晃，是第一人称里最能看出"在走"的东西 |
| `gunBobCycle` | 0.4–1.2 s | 0.69 | 新 | 和镜头 0.70 同拍 |
| `gunBobVert` / `gunBobHorz` | 0–3 / 0–3 | 0.6 / 0.1（重枪 2 / 2.25） | 新 | 重武器晃得大、转得少 |
| `gunBobMaxSpeed` | 50–400 u/s | 150 | 新 | 多快开始晃满 |
| `gunSwayTurnRoll` | 0–6° | 4（重枪 1） | 新 | 转身时枪滚转；重枪只有 1，"拖不动" |
| `gunSwayGain`（平移 / 旋转） | 0–10 | 4 / 7 | 新 | 枪跟视角的拖拽 |
| `gunShakeShare` | 0–1 | 0.10 | 新 | 屏幕震动传给枪多少 |
| `eyeHeight` | 150–260 u | 185 | `TitanChassis` | TF2 三种相同；按底盘拉开（比如轻 175、重 200）是 `[design]`，要同步看碰撞体 |
| `bootExposureFlash` | 开 / 关 | 开（−6，0.1 s） | 新 | 原版有，但落在黑场里看不见；可以不做 |

### 6.4 声音

| 开关 | 范围 | 默认 | 代码里 | 为什么能体现份量 |
|---|---|---|---|---|
| `engineLoopVolume` / `engineLoopPitch` | 0–1 / 0.5–1.5 | 0.5 / 1.0，`[placeholder]` | 新 | 一直在的低频底噪是"坐在机器里"的主要感觉；重型音高低一些是 `[design]` |
| `stepSoundSource` | `timer` / `anim` | `anim`（现在的做法） | 新 | `timer` 时脚步声和镜头的"咚"同拍；TF2 第一人称用哪个没验证 |
| `stepVolumeOwn` | 0–1 | 0.55 | 现在写死在 `TitanDamageView.cs:125` | 舱内听自己的脚步 |

## 7. 缺口汇总

### 7.1 Unity 要做的（按对试玩的影响排）

| # | 项 | 层 | 谁做 |
|---|---|---|---|
| 1 | 三种底盘都能开、能切换（`PracticeGame.cs:211` 写死中型；模型也要按底盘加载） | 全部 | feel-build（已在计划） |
| 2 | 舱内炮的 bob / sway（TF2 武器表） | 3 | 新 |
| 3 | 舱内引擎底噪、进舱出舱提示、按底盘的 dash / 蹲起 / 落地声 | 4 | 新（占位声音即可） |
| 4 | 手柄泰坦视角表（× 0.75，0.8 s 起转） | 1 | 新 |
| 5 | 调参面板接上第 6 节的开关 | 6 | feel-build（已在计划） |
| 6 | 开机声音跟上机时间线（舱门、上电、分块亮起） | 4 | 新 |
| 7 | 低血量间隔警报、护盾打空 / 恢复 | 4 | 新 |
| 8 | 三种底盘各自的舱框外形 | 3 | 设计（外形是我们的） |
| 9 | 泰坦在斜坡上的验证（借的铁驭 `MovementWorld`） | 1 | feel-build 的试驾场 |
| 10 | 蹲走节奏 0.5 还是 0.7 | 2 | 待定 |

### 7.2 要补测 TF2 才知道的（这次没测，要测先问 lead，并遵守 `GAME-LOCK.txt`）

| 项 | 为什么要 | 能不能先不测 |
|---|---|---|
| 13° 以上斜坡的速度和最大坡度 | "爬坡减速"有没有 | 能，先按"9° 不减速"做 |
| 轻、重型冲刺摆动的俯仰和左右 | 拟合只有中型 | 能，先按三种相同 |
| 第一人称脚步声跟定时器还是动画 | 决定 `stepSoundSource` 的默认 | 能，两种都做成开关 |
| 轻、重型的上机时长 | 时间线 | 能 |
| 蹲下 / 站起镜头高度的过渡时长 | `eyeBlendRate` 现在是占位 | 能 |
| 舱框俯仰晃动的稳定值 | 只拍到前 0.25 s | 能 |

### 7.3 要用户定的

| 项 | 默认 | 说明 |
|---|---|---|
| 三种底盘在镜头上要拉多开 | 等于 TF2（几乎不拉开） | 第 5 节末尾；试玩后用 `stepJolt`、`swayGainScale`、`sprintSwayScale`、`eyeHeight`、引擎音高去拉 |
| 重型更"沉"还是更"硬" | TF2：更硬（弹簧硬、晃动小） | 用户说的"有份量"可能想要更沉（起伏更大），两种都能调出来 |
| 推进器小跳留不留 | 开 | TF2 没有 |
| 转向上限、镜头滞后、dash FOV 这三个实验开关 | 关 | TF2 都没有 |

## 8. 出处

研究仓库（本文档所在仓库，路径相对 `tf2/expansion/titan/`）：

| 简称 | 文件 |
|---|---|
| T0 | `T0-REPORT.md` |
| POSE | `pose/TITAN-POSE-CAMERA.md` |
| ANIM-FEEL | `anim/TITAN-ANIM-FEEL.md`（research #110） |
| REF-GAIT | `anim/ref-gait/REF-GAIT-1109.md`（research #113） |
| T-f | `kits/T-f-COCKPIT-RELOAD.md`（research #109） |
| 武器摆动表 | `anim/out/weapon_sway.csv` |
| 动画事件表 | `anim/ref-upper/out/ev_opts_light/medium/heavy.csv`（research #112，还没合并；本地 `TF2-Research/expansion/titan/` 下同一路径有） |

只在本地、不在 git 的（工作区 `TF2-Research/expansion/titan/`）：

| 简称 | 文件 |
|---|---|
| GAPS | `full/TF2-GAPS.md` |
| 713-RECORD | `TITAN-713-RECORD.md` §9 |
| PLAN | `full/PLAN.md` |
| HANDOFF-1107 | `full/HANDOFF-TITAN-1107.md` |

TF2 设置文件和脚本：`scripts/players/mp/titan_base.set`、`titan_stryder.set`、`titan_atlas.set`、`titan_ogre.set`；`scripts/vscripts/client/cl_titan_cockpit_sounds.gnut`、`titan/cl_titan_hud.gnut` 等。解包文件不进公开仓库，这里只引用键名和行号。

Unity（HSD-Unity `titan/integration` 551b50e，路径相对 `Assets/HSD/Game/Runtime/Titan/`）：`TitanMotor.cs`、`TitanChassis.cs`、`Camera/TitanCamParams.cs`、`Camera/TitanCamModel.cs`、`Camera/TitanCamKeys.cs`（`TitanBoot`）、`Camera/TitanCockpitView.cs`、`Camera/TitanCockpitHud.cs`、`Damage/TitanSynth.cs`、`Damage/TitanDamageView.cs`、`Integration/TitanConfig.cs`（`TitanTuning`）、`Integration/TitanWiring.cs`；`../PracticeGame.cs:211`。
