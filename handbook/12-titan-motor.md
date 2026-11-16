# 12 泰坦电机：加速、冲刺、dash、能量、转向、竖直、和铁驭的区别

hb-ch08 写（2026-11-14），分支 `handbook/ch08`，还没合并。总控 11-14 定：泰坦的移动电机单独成一章（原来在 08 章 §2.8 / §2.9 里只引用了几个数）。给总控的备注在 [`_notes/hb-ch08.md`](_notes/hb-ch08.md)。

## 白话说明

这一章讲泰坦**身体怎么移动**：按下前进多久到走速、再多久到冲刺跑速、松手多久停住、dash 推出去多远、能连着 dash 几次、多久回能、转身快不快、能不能跳、掉下去怎么落。第 08 章讲的是泰坦身体动画和驾驶舱镜头怎么**跟着**这些移动，本章是被跟的那一层。

泰坦电机和铁驭电机（02–06 章）是两套规则，不共用代码，只共用碰撞（墙、地面、台阶）。最重要的三点：

1. **响应快，但到"快"要等。** 从站着到走速只要 0.19–0.24 s（不拖手），可从走速爬到冲刺跑速要 0.56–1.06 s——冲刺加速度只有 120–180 u/s²，是起步的十分之一。"重"主要从这里来，不是从转向来。
2. **dash 是一下推出去的。** 按下当帧就到 dash 速度，保持 0.2 s，再按冲刺减速度降回走速，没有起步爬升。中型、重型只有一次，回满要 6–10 s；轻型两次。
3. **转向和铁驭完全一样。** 鼠标没有上限、没有平滑；只有手柄慢 25 %、起转慢。想让泰坦"转得慢"，TF2 的做法是临时缩放**输入**（技能、受控状态），不是限制角速度。

三种底盘（轻 = Stryder、中 = Atlas、重 = Ogre）用同一套规则，只换数。数全部来自 TF2（本地 Northstar 实测 + 设置文件），R5 没有泰坦。

**和别的章的分界**：身体动画、驾驶舱镜头在 08 章；落地镜头、受击镜头在 07 章；泰坦技能（Northstar 悬停、Ronin 相位冲刺、核心技能的减速）的规则归 10 章 / 泰坦套件工作线，本章 §3.3 只写"状态怎么缩放电机"这条通用规则；碰撞、台阶、地面检测的底层在 02 章（泰坦只换碰撞体尺寸和台阶高度）。

### 本章出处缩写

| 缩写 | 路径（研究仓库根目录） | 在哪 |
|---|---|---|
| T0 | `tf2/expansion/titan/T0-REPORT.md`（§2 转向、§3 底盘移动） | main。**§3.1 表的"走→冲刺跑"一列其实是从静止算的**，以 713 §9.3 为准（研究仓库这份副本没改） |
| 713 | `L:TF2-Research/expansion/titan/TITAN-713-RECORD.md` §9.3（电机规律和差异的查清） | 本地，不在 git |
| TFE | `tf2/expansion/titan/feel/TITAN-FEEL.md` §1、§5、§6.1 | PR #118，还没合并（分支 `titan/feel-doc`） |
| RG | `tf2/expansion/titan/anim/ref-gait/REF-GAIT-1109.md` §4（9° 坡上速度不变） | main |
| DP | `research/DESIGN-PHILOSOPHY.md` §8.1（铁驭移动的数字） | main |

Unity：`HSD-Unity: Assets/HSD/Game/Runtime/Titan/TitanMotor.cs`（`TitanMotor`、`TitanMotorInput`、`TitanDashPhase`；静态方法 `AlongStep`、`StopStep`）、`TitanChassis.cs`（`TitanChassis.Light / Medium / Heavy`，每个数带 `[meas T0]` / `[file]` / `[set]` / `[design]` / `[placeholder]`）。**在 HSD-Unity PR #78（分支 `titan/integration`，551b50e），还没合并**；PR #66（`titan/full`）引入。测试 `Assets/HSD/Game/Tests/Editor/TitanMotorTests.cs`。

---

## 0. 约定

- 长度、速度、加速度的身高比例按 **H_t = 235 u**（TF2 泰坦碰撞体高度，三种底盘相同，[01 §4.3](01-units-body.md)）。和铁驭对照时铁驭仍除以 H = 72 u，两列分开写。
- `[m]` 列 = u × 0.0254，是算出来的。时间秒，角度度。
- 依据标签同 README §5；TF2 来源写 [TF2 实测]（本地 Northstar 逐帧）、[TF2 数据]（设置文件、脚本）、[算]（由设置文件按规则算出，和实测对过）。HSD 自己定的写 [设计]，HSD 选的但没测过依据的写 [设定]（Unity 注释里的 `[set]`）。
- 三列数值表的"TF2 原值 [u]"一列写中型，轻 / 重写在"合理范围"一列。

---

## 1. 地面

### 1.1 地面速度律：两段加速、冲刺加速、两种减速

#### 原理

泰坦起步要快，否则会觉得"卡手"；但它是一台大机器，冲起来要时间。TF2 用"按当前速度分段的线性加速"把两件事分开：低速段加速度很大（0.19 s 就到走速），走速以上换成很小的冲刺加速度（要 0.56–1.06 s 才到冲刺跑速）。松手时也分两段：超过走速的部分按冲刺减速度慢慢收，走速以下按很大的减速度很快停。所以泰坦"一按就动、一松就停"，只有冲刺这一段让人等。

分段的结构（低速段 / 走速段 / 冲刺段）和铁驭一样（03 章 §3.2），差别在：铁驭是 Source 式 `Accelerate`（沿意图方向补速度差，先做摩擦，超速时不会被拉回上限），泰坦是**直接的线性速率**，没有摩擦项，超速时按 `sprintDeceleration` 拉回目标速度。

#### 规则和公式

沿着输入方向的速度分量 v（水平），目标速度 V_t = 走速（或冲刺跑速、蹲速）× 输入长度（≤ 1）：

1. 有输入、v < V_t：
   - v < `lowSpeed`：v += `lowAcceleration` · dt
   - `lowSpeed` ≤ v < 走速：v += `acceleration` · dt
   - v ≥ 走速（只在冲刺时目标更高）：v += `sprintAcceleration` · dt
   - 不超过 V_t。
2. 有输入、v > V_t（超速，比如松开冲刺键、dash 之后）：v −= `sprintDeceleration` · dt，不低于 V_t。
3. 没有输入：v > 走速时按 `sprintDeceleration`，否则按 `deceleration`，降到 0。
4. 后退、横移和前进一样快（`speedScaleSide` / `speedScaleBack` 1.0）。
5. 9° 坡上水平速度不变（上下坡都一样），更陡的坡没测；**没有爬坡减速**。
6. 由此算出（和实测对过）：

   | | 轻 | 中 | 重 |
   |---|---|---|---|
   | 0 → 走速 | 0.184 s（测 0.19） | 0.189 s（测 0.19） | 0.246 s（测 0.24） |
   | 走速 → 冲刺跑速 | 0.867 s（测 0.833） | 1.083 s（测 1.057–1.074） | 0.556 s（测 0.557） |
   | 静止 → 冲刺跑速 | 1.02 s | 1.25 s | 0.80 s |
   | 松手停（从走速） | 0.15 s | 0.167 s（测 0.17） | 0.175 s（测 0.18） |
   | 松手停（从冲刺跑速） | 约 0.37 s | 约 0.35 s | 约 0.34 s |

   注意"重型从走速到冲刺最快"（两速差只有 100，冲刺加速度 180 最大）。不要把每一项都按"越重越慢"去拉（TFE 结论 4）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 走速 `speed` | 6.35 m/s | 250 u/s | 1.064 H_t/s | 轻 270、重 210 | [TF2 数据] [TF2 实测] |
| 冲刺跑速 `sprintspeed` | 9.652 m/s | 380 u/s | 1.617 H_t/s | 轻 400、重 310 | [TF2 数据] [TF2 实测] |
| 低速段上限 `lowSpeed` | 5.08 m/s | 200 u/s | 0.851 H_t/s | 轻 230、重 160 | [TF2 数据] |
| 低速段加速 `lowAcceleration` | 38.1 m/s² | 1500 u/s² | 6.38 H_t/s² | 轻 1600、重 1400；实测 1398–1601 | [TF2 数据] [TF2 实测] |
| 走速段加速 `acceleration` | 22.86 m/s² | 900 u/s² | 3.83 H_t/s² | 轻 1000、重 380 | [TF2 数据] |
| 冲刺加速 `sprintAcceleration` | 3.048 m/s² | 120 u/s² | 0.511 H_t/s² | 轻 150、重 180 | [TF2 数据] [TF2 实测] |
| 停步减速 `deceleration` | 38.1 m/s² | 1500 u/s² | 6.38 H_t/s² | 轻 1800、重 1200；实测 1770 / 1498 / 1165 | [TF2 数据] [TF2 实测] |
| 超速减速 `sprintDeceleration` | 17.78 m/s² | 700 u/s² | 2.98 H_t/s² | 轻 600、重 600 | [TF2 数据] |
| 从冲刺跑松手的平均减速 | 27.3 m/s² | 1070 u/s² | 4.55 H_t/s² | 轻 1066、重 892 | [TF2 实测] |
| 0 → 走速 | — | 0.19 s | — | 轻 0.19、重 0.24 | [TF2 实测] [算] |
| 走速 → 冲刺跑速 | — | 1.06 s | — | 轻 0.83、重 0.56 | [TF2 实测] [算] |

#### 实现模板

```
// 单位：u、s
alongStep(v, Vt, crouch, dt):
    if v > Vt: return max(Vt, v - (crouch ? crouchDecel : sprintDecel) * dt)
    a = crouch ? crouchAccel : v < lowSpeed ? lowAccel : v < walkSpeed ? accel : sprintAccel
    return min(Vt, v + a * dt)
stopStep(v, crouch, dt):
    a = crouch ? crouchDecel : v > walkSpeed ? sprintDecel : decel
    return max(0, v - a * dt)
```

离散化：速率是常数，每条命令直接加减，没有半步积分的问题；分段边界（`lowSpeed`、走速）按本帧开始时的速度判断（帧长 1/144 s 时误差 < 0.01 s，Unity 测试按这个网格）。

Unity 参考实现：`TitanMotor.AlongStep`、`TitanMotor.StopStep`、`TitanMotor.Ground`（私有）；参数 `TitanChassis.Medium()` 等。分支 `titan/integration`（PR #78，还没合并）。

#### 验收

- `TitanMotorTests.NoughtToWalkSpeedAsT0`、`TheLowBandAccelerationIsT0s`、`BackAndSideAreTheWalkSpeed`、`LettingGoOfTheWalkStopsInT0sTime`、`SprintFromStandstillIsT0sTableColumn`、`SprintFromTheWalkSpeedIsTheCorrectedRow`、`LettingGoOfTheSprintStopsAtT0sAverage`、`ReleasingSprintComesBackToTheWalkAtSprintDeceleration`、`TheLawFitsTheOtherChassisToo`。
- 合格线：各时间和 T0 / 713 的实测差 ≤ 0.02 s（轻型走→冲刺差 0.034 s，713 §9.3 记了"不追"）。
- 写测试时分清"从静止"和"从走速"（T0 表的一列是从静止算的）。

#### 出处

- T0 §3.1、§3.2：7 台泰坦逐台实测和设置文件（运行 `20261030_015751_t0_move`）。main
- 713 §9.3：分段规则、dash 后按 `sprintDeceleration`、T0 "走→冲刺跑"是从静止算的。本地
- TFE §1 起步、走→冲刺、停步行；§5 底盘差别表。PR #118，还没合并
- RG §4：9° 坡速度不变。main
- [TF2 数据] `scripts/players/mp/titan_stryder.set` / `titan_atlas.set` / `titan_ogre.set`。

---

### 1.2 转弯时速度怎么转

#### 原理

T0 只测了直线。转弯（输入方向变了）时，HSD 的规则是：沿新方向的分量按 §1.1 的速度律走，垂直于新方向的分量按停步减速度衰减。效果是泰坦转弯时会被"甩"一下、很快收住，不会像铁驭空中那样保留侧向速度。这条是 HSD 选的，TF2 没测过。

#### 规则和公式

1. 输入方向单位向量 d。水平速度拆成 v_along = v · d、v_across = v − d · v_along。
2. v_across 的大小按 `deceleration`（蹲时 `crouchDeceleration`）每帧衰减到 0。
3. v_along < 0（往反方向走）：按 `deceleration` 往 0 收；否则按 §1.1 的 `alongStep`。
4. 合成 v = d · v_along + v_across。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 侧向分量衰减 | 38.1 m/s² | 1500 u/s²（= `deceleration`） | 6.38 H_t/s² | 未知 | [设定] TF2 没测转弯 |

#### 实现模板

```
ground(wish):
    if |wish| == 0: v = dir(v) * stopStep(|v|); return
    d = normalize(wish); Vt = target * |wish|
    along = dot(v, d); across = v - d * along
    across = shrink(across, decel * dt)
    along  = along < 0 ? min(0, along + decel * dt) : alongStep(along, Vt)
    v = d * along + across
```

Unity 参考实现：`TitanMotor.Ground`（类注释写明"How the velocity turns ([set])"）。分支 `titan/integration`。

#### 验收

- 没有专门的测试。建议补：走速 250 时输入转 90°，侧向分量 0.167 s 内到 0（250 / 1500）[设计]。
- TF2 补测：泰坦 90° 转弯的速度轨迹（`_notes` 待研究 B12-1）。

#### 出处

- `TitanMotor.cs` 类注释（`[set]`）。HSD-Unity PR #78，还没合并
- 713 §9.3：只有直线规律。本地

---

### 1.3 冲刺跑

#### 原理

冲刺跑只在向前时有效，进得慢（§1.1 的冲刺加速度），FOV 不变（08 §3.2 的镜头下沉代替）。dash 不打断冲刺。

#### 规则和公式

1. 冲刺状态 = 按着冲刺键 且 前进输入 > 0 且 着地 且 不在蹲。
2. 冲刺时目标速度 = `sprintspeed` × 输入长度；从走速往上按 `sprintAcceleration`（§1.1）。
3. 松开冲刺键（或不再向前）：超出走速的部分按 `sprintDeceleration` 收回走速。
4. dash 中按着冲刺键：dash 之后照样回到冲刺（dash 衰减到冲刺跑速就结束，§2.1）。
5. 冲刺下不能 ADS 时的走速缩放见 §3.3。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冲刺跑速 | 9.652 m/s | 380 u/s | 1.617 H_t/s | 轻 400、重 310 | [TF2 实测] |
| 冲刺条件 | — | 只能向前 | — | — | [TF2 实测] TFE §1 |

#### 实现模板

```
sprinting = input.sprint and input.forward > 0 and grounded and not crouching
target = crouching ? crouchSpeed : sprinting ? sprintSpeed : walkSpeed
```

Unity 参考实现：`TitanMotor.Step`（`sprinting = i.sprint && i.forward > 0 && grounded && !crouching`）。分支 `titan/integration`。

#### 验收

- `TitanMotorTests.SprintNeedsForward`、`SprintFromTheWalkSpeedIsTheCorrectedRow`。

#### 出处

- TFE §1 冲刺跑条件行（PR #118，还没合并）；T0 §3.1。main

---

## 2. dash

### 2.1 dash 推力曲线

#### 原理

dash 是喷气推出去的（08 §2.9）：按下当帧就到 dash 速度，保持 0.2 s，然后像任何超速一样按冲刺减速度降回走速。没有起步爬升，所以手感是"一下"。四个方向速度相同；没有输入时朝视线前方。

#### 规则和公式

1. 触发：dash 键按下沿 且 着地 且 距上次 dash ≥ `dodgeInterval` 且 能量 ≥ 每次耗能（§2.2）。
2. 方向 = 移动输入方向（归一化）；没有输入时 = 视线水平前方。
3. 保持段（`dodgeDuration` 0.2 s）：水平速度直接设成 方向 × `dodgeSpeed`，竖直速度不变。
4. 衰减段：交给 §1.1 的地面速度律（超速 → `sprintDeceleration`），降到当前目标速度（走或冲刺跑）时 dash 结束。
5. 由此 dash 距离 = `dodgeSpeed` × 0.2 + (`dodgeSpeed`² − V_t²) / (2 · `sprintDeceleration`)。
6. 设置文件的 `dodgeStopSpeed`（450 / 450 / 350）和 `dodgeHeight` 5 u **不用**：实测曲线只用 `sprintDeceleration` 就能解释（T0 原写"按地面摩擦"不贴切），`dodgeHeight` 没有曲线。
7. 轻型设置文件 `dodgeDuration` 写 0.1，实测 0.19–0.20 s，以实测为准（所有泰坦 0.2 s）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| dash 速度 `dodgeSpeed` | 17.78 m/s | 700 u/s | 2.98 H_t/s | 轻 800、重 600 | [TF2 数据] [TF2 实测] |
| 保持时间 | — | 0.2 s | — | 实测 0.19–0.20，三种相同 | [TF2 实测] |
| dash 后 0.3 s 的速度 | 12.34 m/s | 486 u/s（算 490） | 2.07 H_t/s | 轻 620、重 416 | [TF2 实测] [算] |
| 一次 dash 距离（从走速） | 11.30 m | 约 445 u | 1.89 H_t | 轻 ≈ 633、重 ≈ 383 u | [算] |
| 一次 dash 用时（到走速） | — | 约 0.84 s | — | 轻 1.08、重 0.85 s | [算] |
| 两次 dash 最小间隔 `dodgeInterval` | — | 0.3 s | — | 轻 0.35、重 0.2 | [TF2 数据] |
| 不用的 `dodgeStopSpeed` / `dodgeHeight` | 11.43 m/s / 0.127 m | 450 u/s / 5 u | — | — | [TF2 数据] |

#### 实现模板

```
// 单位：u、s
if dashPressed and grounded and now >= dashAllowedAt and power >= drain:
    dir = |wish| > 0 ? normalize(wish) : flatForward(view)
    phase = Hold; holdUntil = now + 0.2
    dashAllowedAt = now + max(0.2, dodgeInterval)
    power -= drain; regenAt = now + dodgePowerDelay
if phase == Hold and now >= holdUntil: phase = Decay
if phase == Hold: vel.xy = dir * dodgeSpeed
else if grounded:
    ground(wish)                         // §1.1：超速按 sprintDecel
    if phase == Decay and |vel.xy| <= target: phase = None
```

Unity 参考实现：`TitanMotor.Step`（`TitanDashPhase.Hold / Decay`）；`TitanChassis`（`dodgeSpeed`、`dodgeDuration` 0.2、`dodgeInterval`；`dodgeStopSpeed`、`dodgeHeight` 留作记录不用）。分支 `titan/integration`。

#### 验收

- `TitanMotorTests.DashIsAtOnceHeldThenDownAtSprintDeceleration`、`DashGoesWhereTheKeysSayElseForward`、`HoldingTheKeyDoesNotDashAgain`。
- 合格线：dash 后 0.3 s 的速度和 T0 差 ≤ 5 u/s（620 / 486 / 416）。

#### 出处

- T0 §3.1、§3.2（dash 列）。main
- 713 §9.3（`sprintDeceleration` 更贴切）。本地
- TFE §1 dash 推力、距离行。PR #118，还没合并

---

### 2.2 dash 能量和次数

#### 原理

dash 是稀缺资源：中型、重型只有一次，用掉要 6–10 s 才回满；轻型两次、5 s 一格。这让 dash 成为"关键时刻才用"的决定，而不是移动的一部分（对比铁驭滑铲随时可用）。

#### 规则和公式

1. 能量上限 100。每次 dash 扣 `dodgePowerDrain`；能量 < 耗能时不能 dash。
2. dash 之后延迟 `dodgePowerDelay` 才开始回能，之后每秒回 `powerregenrate`，到 100 封顶。
3. **多人设置以每台泰坦的设置文件为准**（覆盖底盘文件）：底盘文件按 4 / 3 / 2 次算，多人实测是 2 / 1 / 1 次。
4. 配件（只记，不做）：Turbo 引擎、冲刺增强会改耗能 / 回能（T0 §3.2）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 能量上限 | — | 100 | — | — | [TF2 数据] |
| 每次耗能 | — | 100（中） | — | 轻 50、重 100 | [TF2 数据] [TF2 实测] |
| 回能速度 | — | 16.66 /s | — | 轻 10、重 9.9 | [TF2 数据] [TF2 实测] |
| 开始回能延迟 `dodgePowerDelay` | — | 0.2 s | — | 轻 0.2、重 0.3 | [TF2 数据] |
| 次数（满能量） | — | 1 | — | 轻 2、重 1 | [TF2 实测] |
| 回一格时间 | — | 6.0 s | — | 轻 5.0、重 10.1 s | [算] |

#### 实现模板

```
if now >= regenAt: power = min(100, power + regen * dt)
canDash = power >= drain
```

Unity 参考实现：`TitanMotor.Step`（`dashPower`、`regenAt`）、`TitanChassis`（`dodgePowerDrain`、`dodgePowerRegen`、`dodgePowerDelay`、`DodgePowerMax` 100）。HUD 怎么显示 dash 能量是 HSD 的设计。分支 `titan/integration`。

#### 验收

- `TitanMotorTests.MediumHasOneDashAndGetsItBackAtT0sRate`、`ChargesAreT0s`。

#### 出处

- T0 §3.1（"次数"列）、§3.2（多人覆盖）。main
- TFE §1 dash 次数 / 冷却行；§5。PR #118，还没合并

---

## 3. 蹲、转向、状态缩放

### 3.1 蹲

#### 原理

泰坦能蹲（降低碰撞体钻过去、降低眼高），蹲着走得慢。站起来要有空间，头顶有东西就站不起来。

#### 规则和公式

1. 蹲时用蹲的速度、加速、减速（单段，没有 `lowSpeed` 分段），碰撞体高 235 → 140 u，眼高 185 → 125 u。
2. 松开蹲时检查站立碰撞体能不能放下，放不下就继续蹲。
3. 眼高按 300 u/s 匀速变（[placeholder]，TF2 只知道"平滑"，过渡时长没测）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 蹲速 | 3.81 m/s | 150 u/s | 0.638 H_t/s | 轻 187、重 112 | [TF2 数据] |
| 蹲加速 / 减速 | 5.08 / 12.7 m/s² | 200 / 500 u/s² | 0.851 / 2.13 H_t/s² | 轻 250 / 625、重 150 / 375 | [TF2 数据] |
| 蹲碰撞体高 | 3.556 m | 140 u | 0.596 H_t | — | [TF2 数据] |
| 眼高 站 / 蹲 | 4.699 / 3.175 m | 185 / 125 u | 0.787 / 0.532 H_t | — | [TF2 实测] |
| 眼高变化速度（HSD） | 7.62 m/s | 300 u/s | 1.28 H_t/s | 没测 | [设计] 占位 |

#### 实现模板

```
wantCrouch = input.crouch or (crouching and blocked(standHull))
target/accel/decel = crouch set when crouching
eye = approach(eye, crouching ? 125 : 185, 300 * dt)
```

Unity 参考实现：`TitanMotor.Step`（`mw.Blocked(pos, c.hullHeight)`）、`TitanChassis`（`crouchSpeed`、`crouchAcceleration`、`crouchDeceleration`、`crouchHullHeight` 140、`eyeBlendRate` 300）。分支 `titan/integration`。

#### 验收

- `TitanMotorTests.CrouchIsTheFilesNumbers`、`CannotStandUpUnderACeiling`。
- 蹲起镜头过渡时长：B08-4（99-TODO）。

#### 出处

- T0 §3.2（蹲那一行）；TFE §1 蹲行（PR #118，还没合并）。main

---

### 3.2 转向

#### 原理

TF2 的泰坦"重"**不在转向上**。鼠标转向和铁驭完全一样：同样的输入转同样的角度，没有上限、没有平滑、松手当帧停。只有手柄用一张单独的泰坦视角表（最大转速 × 0.75、起转 0.8 s）。给鼠标加转速上限会让玩家觉得"卡手"而不是"重"。机械感用表现层做（舱框落后、弹簧更硬，08 §3）。

#### 规则和公式

1. 鼠标：度 / 计数 = 0.022 × `mouse_sensitivity`，和铁驭相同，泰坦没有额外系数。
2. ADS：`mouse_sensitivity_zoomed` × tan(zoom_fov / 2) ÷ tan(75° / 2)（泰坦 FOV 75）；不放大的武器（Legion 转管，zoom_fov 75）ADS 时反而转得更快。
3. 手柄：泰坦表 = 铁驭表的最大转速 × 0.75（各档 0.75–0.9），默认档 2、3 的起转时间铁驭 0.33 / 0.3 s → 泰坦 0.8 s；档 4 以上无起转。
4. 临时减慢（`turn_slow` 强度 s）：缩放**输入**，约 × (1 − 2s)；不限角速度，键盘转向不受影响。Ion 激光核心 0.25 → 鼠标转速减半；被 EMP 0.35。
5. 如果 HSD 要试"转向上限"，做成实验开关，默认关（TFE §6.1 `turnRateCap`）[设计]。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 鼠标度 / 计数（灵敏度 3.29） | — | 0.0724° | — | 和铁驭相同 | [TF2 实测] |
| 键盘转向实测（210 / 1500 °/s 输入） | — | 210.1–210.3 / 1499–1501 °/s | — | 7 台 + 铁驭相同 | [TF2 实测] |
| 手柄最大转速比例 | — | 0.75 × | — | 档 4–5 俯仰 0.85–0.9 | [TF2 数据] |
| 手柄起转时间（档 2） | — | 0.8 s（铁驭 0.33 s） | — | 档 4 以上 0 | [TF2 数据] |
| `turn_slow` 对鼠标 | — | × (1 − 2s)：s 0.25 → × 0.506，0.5 → × 0.004 | — | — | [TF2 实测] |

#### 实现模板

```
yawDelta = mouseCounts * 0.022 * sens * (ads ? zoomScale : 1) * max(0, 1 - 2 * turnSlow)
padRate  = titanLookTable[level] (= pilot * 0.75, ramp 0.8 s for level 2–3)
// 不对角速度做 clamp
```

Unity 参考实现：泰坦用游戏本身的鼠标转向（`PracticeGame`），没有泰坦系数；调参面板的转向上限钩子 `ITitanAimScale.TurnScale`（`TitanFeel.TurnHook`，PR #83 `titan/feel-build`，还没合并），默认不限。**手柄泰坦表没做**（TFE §7.1 #4）；`turn_slow` 归技能工作线。

#### 验收

- 鼠标：同样 2000 计数，泰坦和铁驭转角差 < 0.05°（TF2 144.78 / 144.78–144.79°）[TF2 实测]。
- `TitanCamTests.AimIsTheMouseWhateverTheLayersDo`（镜头层不改瞄准）。
- 手柄表做了以后：默认档最大 120 °/s、0.8 s 起转。

#### 出处

- T0 §2.1–§2.5（运行 `20261030_013127_t0_turn`、`20261030_023156_t0_turn`、`20261030_023602_t0_mouseslow`）。main
- [TF2 数据] `cfg/aimassist/looksensitivity_titan.txt`；ConVar `gamepad_custom_titan`。
- TFE §1 转向行、§6.1。PR #118，还没合并

---

### 3.3 状态对电机的缩放（ADS 走速、`move_slow`）

#### 原理

武器和技能不改电机规则，只按一个系数缩放目标速度。这样电机只有一套，所有"变慢"都走同一个入口，和 R5 铁驭的移动倍率（09 章）同一思路。

#### 规则和公式

1. ADS 时走速 × 武器的 `ads_move_speed_scale`（没写的默认 0.5）。
2. `move_slow` 强度 s：速度 × (1 − s)（实测 0.3 → 175.5、0.6 → 100.0，误差 < 0.5 u/s）。
3. 技能（核心减速、强制 ADS 等）只是给这两个入口一个值；具体值归 10 章 / 套件工作线（T0 §3.3 有表）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| ADS 走速（Ion，× 0.75） | 4.78 m/s | 188 u/s | 0.800 H_t/s | Monarch 100（× 0.40）、Legion 116、Ronin 135 | [TF2 实测] |
| `ads_move_speed_scale` 默认 | — | 0.5 × | — | — | [TF2 数据] |
| `move_slow` 规律 | — | × (1 − s) | — | 实测误差 < 0.5 u/s | [TF2 实测] RG §0 |

#### 实现模板

```
target = baseTarget * (ads ? weapon.adsMoveScale : 1) * (1 - moveSlow)
```

Unity 参考实现：泰坦电机里**没有**这两个入口（`TitanMotorInput` 只有方向、冲刺、蹲、dash、hop）；套件工作线（HSD-Unity PR #82 `titan/kits-core` 的电机接口、#87 `titan/playtest-v1`，都还没合并）在加。

#### 验收

- 做了以后：Ion ADS 走速 188 ± 1 u/s；`move_slow` 0.6 → 100 ± 0.5 u/s。

#### 出处

- T0 §3.3（运行 `20261030_020515_t0_kit`）；RG §0（`move_slow` 控速）。main

---

## 4. 竖直：重力、跳、下落、台阶

### 4.1 重力、跳（HSD 的推进器小跳）、下落和硬落地

#### 原理

TF2 的泰坦**不能跳**（`jump 0`），不能蹬墙、不能滑铲；离地只有两种：走下台边、技能（悬停）。HSD 加了一个推进器小跳（约 50 u 高），默认开，是我们的设计（PLAN 决定 1），试玩时问用户。空中没有转向控制，只有重力。

#### 规则和公式

1. 重力 = `sv_gravity` 750 u/s²（`titan_base.set` 没有重力倍率）；空中按梯形积分位置（v 平均）。
2. 空中：水平速度不变（没有空中加速），只受重力 [设定]。
3. HSD 小跳：hop 键按下沿 且 着地 且 距上次 ≥ 冷却：竖直速度 = `hopSpeed`。
4. 落地：记录落地竖直速度（给 07 章落地镜头、08 章身体落地）和下落高度（从最高点算）；下落高度 > `hardFallDist` 40 u 记为"硬落地"，**只触发声音**（TF2 没有软硬两套镜头）。
5. 台阶：碰撞体一次迈上 ≤ 80 u（`stepheight`），画面平滑跟上（08 §2.6）。
6. 碰撞体宽 120（半宽 60）、高 235 u；离墙 60 u 停住。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力 | 19.05 m/s² | 750 u/s² | 3.19 H_t/s² | 铁驭同 750（10.42 H/s²） | [TF2 数据] |
| 跳 | — | 不能（`jump 0`） | — | — | [TF2 数据] |
| HSD 小跳起跳速度 `hopSpeed` | 6.96 m/s | 274 u/s | 1.166 H_t/s | 约 50 u 高 = √(2·750·50) | [设计] |
| HSD 小跳高度 | 1.27 m | 约 50 u | 0.213 H_t | — | [设计] |
| HSD 小跳冷却 | — | 1.0 s | — | — | [设计] |
| 硬落地高度 `hardFallDist` | 1.016 m | 40 u | 0.170 H_t | 只管声音 | [TF2 数据] |
| 台阶 `stepheight` | 2.032 m | 80 u | 0.340 H_t | — | [TF2 数据] |
| 碰撞体 宽 × 高（蹲高） | 3.048 × 5.969 m（3.556） | 120 × 235 u（140） | 0.511 × 1 H_t（0.596） | 三种相同 | [TF2 数据] [TF2 实测] |
| 物理质量 `physicsMass` | — | 3000 | — | 没用 | [TF2 数据] |

#### 实现模板

```
// 单位：u、s
if hopPressed and grounded and hopEnabled and now >= hopAllowedAt:
    vel.z = hopSpeed; grounded = false; hopAllowedAt = now + 1.0
if not grounded:
    vz0 = vel.z; vel.z -= 750 * dt; pos.z += (vz0 + vel.z) * 0.5 * dt
    fallTop = max(fallTop, pos.z)
if not grounded and vel.z <= 0 and pos.z <= floor:
    landSpeed = -vel.z; hardFall = (fallTop - floor) > 40; grounded = true
```

Unity 参考实现：`TitanMotor.Step`（`hop`、`gravity`、`landed`、`hardFall`、`landSpeed`、`fallDistance`、`stepOffset`）、`TitanChassis`（`gravity` 750、`hopEnabled`、`hopSpeed` 274、`hopCooldown` 1.0、`hardFallDistance` 40、`stepHeight` 80、`hullRadius` 60、`hullHeight` 235、`stepSmoothTime` 0.12 [placeholder]）。碰撞借铁驭的 `MovementWorld`（每条命令换成泰坦尺寸，再换回去）。分支 `titan/integration`。

#### 验收

- `TitanMotorTests.HopIsShortAndLands`、`TheHopCanBeSwitchedOff`、`TheOnlyJumpIsTheHop`、`WalkingOffAnEdgeFallsAndLandsAtTheMeasuredGravity`、`StepsUpToEightyNotMore`、`AHullThisWideStopsSixtyUnitsFromAWall`、`TheWorldGoesBackToThePilotsHullEveryCommand`、`TheParkedPilotMotorStaysClean`。

#### 出处

- T0 §3.2（`titan_base.set` 通用行）。main
- TFE §1 跳、斜坡、台阶、撞墙行（PR #118，还没合并）；GAPS §1（落地，PR #98，还没合并）。
- `TitanChassis.cs` 注释（`[design]` 小跳、`[placeholder]` 平滑）。HSD-Unity PR #78，还没合并

---

## 5. 和铁驭电机的区别

### 5.1 泰坦 vs 铁驭

#### 原理

两套电机的差别本身就是设计：铁驭电机为"技巧"服务（动量保留、空中控制、连跳、滑铲、翻越，P3"动量是玩家的资产"），泰坦电机为"份量"服务（快起快停，但冲刺要等、dash 稀缺、不能跳）。按身高比例看，泰坦相对自己身体走得**更慢**（1.06 H_t/s 对铁驭 2.41 H/s），这是"大"的感觉；绝对速度又更快（250 对 173.5 u/s），所以在同一张地图上泰坦仍然有压迫感。

#### 规则和公式

| 项 | 铁驭（R5，msc 1 / 1.15） | 泰坦（TF2 中型） | 依据 |
|---|---|---|---|
| 加速方式 | 三段（低速 / 走速 / 冲刺）+ Source 式 `Accelerate` + 摩擦；超速不拉回（03 章 §3.2、§3.4） | 三段线性速率，没有摩擦；超速按 `sprintDeceleration` 拉回（§1.1） | [反编译] [实测] / [TF2 实测] |
| 走速 | 173.5 u/s（2.41 H/s）；msc 1.15 时 199.5 | 250 u/s（1.06 H_t/s） | DP §8.1；T0 |
| 冲刺 | 260 u/s（3.61 H/s）；冲刺加速 115 u/s²（msc 1.15） | 380 u/s（1.62 H_t/s）；冲刺加速 120 u/s² | DP §8.1；T0 |
| 起步加速 | < 138 u/s 时 2875，以上 517.5 u/s²（msc 1.15） | < 200 u/s 时 1500，以上 900 u/s² | DP §8.1；T0 |
| 无输入减速 | 1250 u/s²（不乘 msc） | 1500 u/s²（超速部分 700） | DP §8.1；T0 |
| 空中 | 有空中加速（03 章），可以 lurch / tap strafe | 没有空中控制 [设定] | 03 章；T0 |
| 跳 | 56 u，连跳惩罚，二段跳（技能） | 不能跳；HSD 小跳 50 u [设计] | README 示范条目；T0 |
| 滑铲 / 翻越 / 跑墙 | 有（04、05 章） | 没有 | T0 §3.2 |
| 冲刺爆发 | 无（滑铲、技能代替） | dash：700 u/s 保持 0.2 s，1 次，6 s 回能 | §2 |
| 转向 | 鼠标 1:1 | 鼠标 1:1（相同）；手柄 × 0.75、起转 0.8 s | T0 §2 |
| 重力 | 750 u/s² | 750 u/s²（相同） | DP §8.1；T0 |
| 台阶 | 22 u（HSD 现在 18 u，01 章） | 80 u | 01 §4.2；T0 |
| 碰撞体 | 32 × 32 × 72 u | 120 × 120 × 235 u | 01 §4 |
| 眼高 | 70 u（0.97 H） | 185 u（0.79 H_t） | 01 §4；08 §3.1 |

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 走速 铁驭 / 泰坦 | 4.41 / 6.35 m/s | 173.5 / 250 u/s | 2.41 H/s / 1.06 H_t/s | — | [实测] [TF2 实测] |
| 0 → 走速 铁驭（msc 1.15）/ 泰坦 | — | 约 0.17 s / 0.19 s | — | 铁驭见 03 章 §3.2 | [算] [TF2 实测] |
| 冲刺 铁驭 / 泰坦 | 6.60 / 9.65 m/s | 260 / 380 u/s | 3.61 H/s / 1.62 H_t/s | — | [实测] [TF2 实测] |

（铁驭 0 → 走速：138 / 2875 ≈ 0.048 s，再 (199.5 − 138) / 517.5 ≈ 0.119 s，合计约 0.17 s，不算摩擦和输入曲线，准确值以 03 章为准。两者起步时间差不多，"泰坦重"不在起步上。）

#### 实现模板

```
// 两个电机，一个世界
pilot:  R5MotorV2 (+ R5MotorV2Params.R5Reference())   // 02–06 章
titan:  TitanMotor (TitanChassis)                      // 本章
world:  MovementWorld shared; titan swaps hull/step per command and restores
```

Unity 参考实现：铁驭 `MovementConfigs.Reference()`（`R5MotorV2`）；泰坦 `TitanMotor`，"Its own rules, not R5MotorV2's; the pilot's motor is not changed and only lends its collision calls"（类注释）。上机时铁驭电机停在原地（parked carrier）。分支 `titan/integration`。

#### 验收

- `TitanMotorTests.TheParkedPilotMotorStaysClean`、`TheWorldGoesBackToThePilotsHullEveryCommand`：泰坦电机不改铁驭电机和世界。
- 铁驭回放基线（11 章）在泰坦分支上不变（titan 线的 movement hash 744 / 741，`hsd-terrain-heavy` 记录）。

#### 出处

- DP §8.1：铁驭移动的数字。main
- T0 §2、§3；713 §9.3（本地）；TFE §1（PR #118，还没合并）。
- 01 §4（身体尺寸）。handbook/base

---

## 6. 待研究（本章）

- **B12-1**：泰坦转弯时速度怎么转（§1.2 是 HSD 的设定，TF2 只测了直线）。TF2 runner，便宜。
- **B12-2**：泰坦在空中有没有水平控制（走下台边、悬停以外）。TF2 runner。
- **B12-3**：13° 以上斜坡的速度和最大可站坡度（RG 没测成，TFE §7.2）。
- **B12-4**：轻型 走速 → 冲刺 实测和算差 0.034 s 的原因（713 记"不追"）。
- **B12-5**：`dodgeHeight` 5 u 到底有没有作用（dash 起步的竖直位移）。
- 蹲起眼高过渡时长：B08-4。
