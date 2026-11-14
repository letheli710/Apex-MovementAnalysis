# 03 地面、空中、跳跃、时间窗口、lurch / tap strafe

由 hb-ch03 写（2026-11-14）。分支 `handbook/ch03`，还没合并。写法照 [README.md](README.md) 的写法规范；单位和身高比例照 [01 单位与身体](01-units-body.md)（1 u = 0.0254 m，H = 72 u）。

## 白话说明

这一章讲铁驭（Apex 传奇）最基本的五件事：**在地上怎么跑、在空中怎么飘、怎么跳、哪些动作有时间窗口、起跳后怎么"拐一下"（lurch）**。滑铲、翻越、跑墙、钩爪这些更大的动作都建在这五件事上面，所以这一章是整个移动的地基。

结论先说，R5 的地面和空中只靠几条很短的规则：

1. **地上**：速度有上限（走 199.5、冲刺 299、蹲 92 u/s）。加速分三段，越快加得越慢；松手按固定 1250 u/s² 停下。转身时只削掉"偏离你想去的方向"的那部分速度，所以急转会掉速再回升，鼠标慢转几乎不掉速。
2. **空中**：没有空气阻力，已有的速度不会被磨掉；按方向键只能往"想去的方向"补到很小的 69 u/s，所以空中改方向很弱。
3. **跳**：每次跳到同样的高度（56 u）。刚落地又跳会跳得矮、超出冲刺速度的部分被削掉 100，这两条防止靠连跳刷速度和高度。
4. **时间窗口**：都按秒算，和帧率无关。落地后第一条命令就起跳不吃地面摩擦（兔跳保速）。R5 有没有"走下台边还能跳"（coyote time）和"落地前按跳也算"（起跳缓冲）**没测过**，HSD 现在两样都没有。
5. **lurch**：起跳后 0.5 s 内（前 0.2 s 最强）每按下一个新的方向键，水平速度的方向就朝按键方向转一下，大小不变，每次最多改 209.3 u/s。tap strafe 是同一条规则：按 W 的同时转视角。

读完这一章，一个工程师应该能写出和 R5 同样手感的跑、停、转、跳、空中控制和 lurch，并用本章列的测试和对照数据验收。

**和别章的分界**

| 内容 | 在哪一章 |
|---|---|
| 每帧的顺序、时间步长、碰撞体、地面检测（2 u 探测）、台阶、斜坡上的地面移动 | [02 底层](02-foundation.md)。本章只写"在地上 / 在空中"之后做什么 |
| 滑铲、滑铲跳、斜坡滑铲、翻越、superglide | [04](04-slide-mantle.md)。本章的起跳只写到"滑铲中改用 `slideJumpHeight`" |
| 跑墙、二段跳、蹬墙跳；跳板、击退等外力打开的 lurch 窗口 | [05](05-wall-external.md) |
| 动量总表、同一条命令上多个动作谁赢（跳 / 翻越 / 二段跳…）、按键到轴值的输入层（第一次按键 0.5 → 0.75） | [06](06-momentum-arbitration-input.md)。本章只写本章需要的那一小块，并指过去 |
| 落地镜头 kick、冲刺眼高下沉、冲刺横滚 | [07 镜头](07-camera.md) |

**本章出处缩写**（路径从研究仓库根目录算；都在 `main`）

| 缩写 | 文件 |
|---|---|
| NG | `research/rea-native/subsystems/N2-G-GROUND.md`（G-01 – G-15） |
| NJ | `research/rea-native/subsystems/N2-J-JUMP-AIR.md`（J-01 – J-10） |
| NL | `research/rea-native/subsystems/N2-L-LURCH.md`（L-01 – L-13） |
| N4A / N4B / N4C / N4D | `research/rea-native/n4/N4A-READBACK.md`、`N4B-KEYTURN.md`、`N4C-HOP-SLIDE.md`、`N4D-REMAINING.md` |
| N5 | `research/rea-native/n5/REFERENCE-CHANGES.md` |
| CVD | `research/rea-native/convar-defaults/CONVAR-DEFAULTS.md` |
| GM | `research/phase2-local/m2/ground/GROUND-MODEL.md` |
| AJ | `research/phase2-local/m2/air_jump/AIR-JUMP-MODEL.md` |
| LM | `research/phase2-local/m3/lurch/LURCH-MODEL.md` |
| A1 | `research/phase2-local/m6/a1_lurch/A1-LURCH.md` |
| RL | `research/phase2-local/m8/r_lurch/LURCH.md` |
| TQ | `research/phase2-local/m8/d_techniques/TECHNIQUES.md` |
| LIB9 | `research/phase2-local/m9/d_library/TECHNIQUE-LIBRARY.md` |
| M10D | `research/phase2-local/m10/unity/M10D-UNITY.md` |
| OCT | `research/phase2-local/m4/octane/OCTANE-PRIMITIVES.md` |
| DP | `research/DESIGN-PHILOSOPHY.md` |
| DEF | `DEFERRED-DESIGN-TODO.md` |
| TF | `tf2/TF2-MOVEMENT-SUMMARY.md` |
| TVA | `tf2/TF2-VS-APEX.md` |
| T1 | `tf2/static-values/T1-REPORT.md` |

---

## 3.0 共同约定

### 本章的"Unity 参考实现"指什么

HSD-Unity 里同一个电机 `R5MotorV2` 有两套参数，本章的规则**以游戏用的那套为准**：

| | 回放电机 | **Reference（本章的参考实现）** |
|---|---|---|
| 参数 | `R5MotorV2Params.R5Reference()` | `MovementConfigs.Reference()`：在 `R5Reference()` 上再打开一组原生规则 |
| 用途 | 逐条重放 R5 录像，当尺子用（D-66：到此为止，不再改） | 游戏、演示、练习地图 |
| 本章相关的差别 | 超速连跳 min(h, 299)；没有空中额外加速；冲刺加速边界用 M2 规则；起跳不朝墙推；lurch 上限固定 209.3、没有 1100 截断 | `groundJumpSkipReduce` 100、`extraAirAccel` 2、`sprintAccelFixedEdge`、`jumpSurfacePush` 30、`lurchClampSprintFraction` 0.7、`lurchCutoffSpeed` 1100 |
| 两套都有 | 原生地面摩擦 `groundNativeFriction`（D-49 起回放电机也开） | 同左 |

两套的文件都在 `HSD-Unity: Assets/HSD/R5Replay/Runtime/`：`R5MotorV2.cs`（电机）、`R5MotorV2Params.cs`（参数和 `R5Reference()`）、`MovementConfig.cs`（`MovementConfigs.Reference()`）。注意 `ReferenceMotor.cs` 是 M1 的第一版模型，不是参考实现（00-INVENTORY §0.3 的命名陷阱）。

### 移动倍率 msc

R5 的速度上限和加速度大多要乘一个**移动倍率 msc**（"拿什么武器、有没有兴奋剂"决定）。本章所有数都按 **空手 msc = 1.15** 写（Gibraltar 空手，M2 起全部实测都是这个值）。表里"R5 原值 [u]"一列写的是 setfile 原值，乘过 msc 的值另起一行或写在正文。规则里写明哪些乘 msc、哪些不乘，这是 R5 和 TF2 的一个主要区别（§3.2）。

Unity：`MotorInput.moveScale`（> 0 时用它，否则用 `R5MotorV2Params.moveScale` 1.15）。

### 命令和时间

一条"命令"就是一次移动模拟步（R5 的 usercmd，Unity 的 `R5MotorV2.Step(input, dt)`）。所有窗口按**秒**算（`now − 某个时刻`），不按帧数，和帧率无关（DP P4）。离散化细节（为什么用 dt、半步重力的位置）在 [02](02-foundation.md)；本章在需要的地方单独写明。

---

## 地面

### 3.1 速度上限和移动倍率

#### 原理

每种姿态有一个速度上限：站着走、冲刺、蹲着走。上限乘移动倍率，所以拿重武器、打兴奋剂时整个"多快"一起变，不用逐项改。往后退、往侧面走在 Apex 里和往前一样快（倍率都是 1），斜着走也不会更快（意图方向先归一化）。

#### 规则和公式

1. 不在滑铲、着地时，上限 `cap`：
   - 蹲着（上一条命令就按着蹲，见第 5 条）：`crouchSpeed` × msc；
   - 冲刺中（§3.3 的条件）：`sprintspeed` × msc；
   - 否则：`speed` × msc。
2. 往后（前后轴 < 0）再乘 `speedScaleBack`；只有侧向输入时乘 `speedScaleSide`。R5 两个都是 1。
3. **斜向输入归一化**：意图向量 = 前向 × f + 右向 × s，长度超过 1 就归一化，所以 W+D 的上限还是 199.5，不是 282。
4. 上限在加速时起作用（§3.2 的 `Accelerate` 上限）；超过上限时按 §3.4 的减速慢慢降回来，不会一步截断。
5. 姿态按"上一条命令"判断：这条命令开始时按下蹲，这条命令仍按站姿算，下一条才算蹲（Unity `ducked = prevDuckHeld`）。下蹲眼高、碰撞体变矮的时间在 [01 §4.2](01-units-body.md) 和 [02](02-foundation.md)。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 走路基础速度 `speed` | 4.407 m/s | 173.5 u/s | 2.410 H/s | TF2 相同 | [数据] |
| 走路上限（× 1.15） | 5.068 m/s | 199.525 u/s | 2.771 H/s | 实测 199.525（spread 0） | [实测] |
| 冲刺基础速度 `sprintspeed` | 6.604 m/s | 260 u/s | 3.611 H/s | TF2 相同 | [数据] |
| 冲刺上限（× 1.15） | 7.595 m/s | 299 u/s | 4.153 H/s | 实测 299.000 | [实测] |
| 蹲走基础速度 `crouchSpeed` | 2.032 m/s | 80 u/s | 1.111 H/s | TF2 80 | [实测拟合] [反编译：按姿态取值] |
| 蹲走上限（× 1.15） | 2.337 m/s | 92 u/s | 1.278 H/s | 实测 92.000 | [实测] |
| `speedScaleBack` / `speedScaleSide` | — | 1 / 1（×） | — | ≠ 1 时乘在上限上还是加速上没测 | [数据] |
| 移动倍率 msc（空手） | — | 1.15（×） | — | 随武器变 | [数据] [实测] |

**TF2 对比**：上限一样（173.5 / 260 / 80，× msc）。TF2 的 msc = 主武器 × 副武器倍率 × 状态效果（TF §2.6）。

#### 实现模板

```
// 单位：u、s
cap(ducked, sprinting, fwd, side, msc):
    c = ducked ? crouchSpeed*msc : sprinting ? sprintspeed*msc : speed*msc
    if fwd < 0:                 c *= speedScaleBack
    else if fwd == 0 and side != 0: c *= speedScaleSide
    return c
```

Unity：`R5MotorV2.GroundCap`（`R5MotorV2.cs`），参数 `speed`、`sprintspeed`、`crouchSpeed`、`speedScaleBack`、`speedScaleSide`、`moveScale`（`R5MotorV2Params.cs`，全部 [u]）。

#### 验收

- `R5MotorV2FormulaTests.CapsWalkSprintCrouch`：199.525 / 299 / 92。
- `R5MotorV2FormulaTests.HalfPressFirstStepTakesFullAccelAndDiagonalIsNormalized`：斜向上限仍是 199.525。
- 对照数据：GM §3.1、§3.5（7 种条件 × 5 次，终速 spread 0 %）。
- 合格线：稳定速度和上限差 < 0.01 u/s；FEEL §2"地面稳定速度"2 u/s 或 1 %。

#### 出处

- GM §2、§3.1、§3.5：上限、斜向归一化、后退和侧向。main
- NG §2.1、§2.2；N4D §1（G-05 蹲姿 `speed` / `deceleration` 按姿态取值，`bridge_classvar_get` 只读得到站姿一行）。main
- `research/phase2-local/static-values/STATIC-VALUES.md` §1、§2：`speed`、`sprintspeed`、移动倍率 1.15。main
- TF §1、§2.6。main
- [反编译] `WalkMove` 0x140a4a7c0；msc 在玩家偏移 0x3278 [native-inf]。

---

### 3.2 地面加速（三段）

#### 原理

起步很快、越快加得越慢：从静止到 138 u/s 几乎是瞬间（约 0.05 s），之后到走路上限约 0.12 s，冲刺再从 199.5 慢慢爬到 299 要将近 1 秒。这样"开始跑"很跟手，"跑到最快"需要持续冲刺，最高速是攒出来的。加速度乘移动倍率，所以重武器不只跑得慢，起步也慢。

#### 规则和公式

1. 加速度按**加速前**的水平速度 h 选段（一步可以越过段的边界，按开始时的段算）：

   | 条件（按顺序判断） | 加速度 a |
   |---|---|
   | 滑铲中 | 见第 04 章 |
   | h > msc × `speed` − 1（固定边界，**不检查是否在冲刺**） | `sprintAcceleration` × msc |
   | h < msc × `lowSpeed` | `lowAcceleration` × msc |
   | 其他 | `acceleration` × msc |

   冲刺段的边界不看冲刺状态，但不冲刺时上限只有 199.525，h 到不了 198.525 以上太久，所以实际只在冲刺时起作用。
2. Source 式 `Accelerate`（在 §3.4 的摩擦之后做）：
   - addspeed = wishspeed − v · ŵ；≤ 0 时不加；
   - v += min(addspeed, a · dt) · ŵ；
   - **加完以后 |v| ≤ max(加速前的 |v|, wishspeed)**：转向能改方向，但不能凭空提速，也不会把超速"拉回"到上限。
3. wishspeed = min(|意图|, 1) × cap（§3.1）。意图的大小经过输入曲线（§3.4 第 4 条）。
4. 加速度**乘** msc；减速度（§3.4）**不乘** msc。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 低速段边界 `lowSpeed`（× 1.15 = 138） | 3.048 m/s（3.505） | 120 u/s（138） | 1.667 H/s（1.917） | 实测边界 (136.38, 138.47] | [数据] [实测] |
| 低速段加速 `lowAcceleration`（× 1.15） | 63.50 m/s²（73.03） | 2500 u/s²（2875） | 34.72 H/s²（39.93） | 实测 2874.73 | [数据] [实测] |
| 中速段加速 `acceleration`（× 1.15） | 11.43 m/s²（13.14） | 450 u/s²（517.5） | 6.250 H/s²（7.188） | 实测 517.46 | [数据] [实测] |
| 冲刺段加速 `sprintAcceleration`（× 1.15） | 2.591 m/s²（2.979） | 102 u/s²（117.3） | 1.417 H/s²（1.629） | 实测 117.285；另一次 census 读到 100（→ 115），见正文 | [数据] [实测] |
| 冲刺段边界（msc × `speed` − 1） | 5.043 m/s | 198.525 u/s | 2.757 H/s | M2 区间 (197.97, 198.72] | [反编译] [实测] |
| 走路从 0 到上限 | — | 0.145 – 0.167 s | — | 随帧时长的分布变 | [实测] |
| 冲刺从按下到 299 | — | 1.00 – 1.02 s | — | — | [实测] |

`sprintAcceleration`：M2 复跑那次的 census 读到 102，用 102 时回放误差 0.005–0.03 u/s，用 100 是 0.39–0.96，所以这个构建用 102。DP §8.1 写的"冲刺 115 u/s²"是按 100 算的，以本表为准（写进 `_notes`）。

**TF2 对比**：TF2 MP 铁驭的 `lowAcceleration`、`sprintAcceleration` 都是 −1（关），加速**始终 2500 u/s²，不乘 msc**（63.50 m/s²，34.72 H/s²）。R5 加了三段，并让加速乘 msc（TF §2.1，T5 实测）。所以 TF2 起步到冲刺上限几乎是瞬间，R5 冲刺要攒 1 秒。

#### 实现模板

```
// 单位：u、s
groundAccelRate(h, msc):
    if h > speed*msc - 1:   return sprintAcceleration*msc     // 固定边界，不看冲刺
    if h < lowSpeed*msc:    return lowAcceleration*msc
    return acceleration*msc

accelerate(v, wishdir, wishspeed, a, dt):     // v 是摩擦之后的水平速度
    old = |v|
    add = wishspeed - dot(v, wishdir)
    if add <= 0: return v
    v += wishdir * min(add, a*dt)
    lim = max(old, wishspeed)
    if |v| > lim: v *= lim/|v|
    return v
```

注意 a 用**摩擦之前**的 h 选段（Unity `GroundNativeStep` 先算 `rate`，再做摩擦和加速）。

Unity：`R5MotorV2.GroundAccelRate`（`sprintAccelFixedEdge` 为真时用固定边界；Reference 打开，回放电机用 M2 规则"冲刺中且 s + a·dt ≥ msc·speed"，两者只差一条命令）；`R5MotorV2.GroundNativeStep` 的 Accelerate 部分。

#### 验收

- `R5MotorV2FormulaTests.AccelBandsFollowPreMoveSpeed`、`SprintRampUsesSprintAccelAboveWalkCap`、`SprintFlagSetOneCommandAfterThePress`。
- `N7NativeReferenceTests.SprintAccelBandStartsAtTheFixedEdge`。
- 对照数据：GM §3.1 的 35 次起步（每段加速 spread ≤ 0.10 %）、`research/phase2-local/m2/ground/curves_*.csv`。
- 合格线：开环每条命令误差 ≤ 0.015 u/s（GM §2）；FEEL §2"加速到 90 % 用时"3 帧或 5 %。

#### 出处

- NG §2.2（G-01 – G-04）、§2.5（G-14）：分段、固定边界、加速乘 msc、`Accelerate` 上限。main
- GM §3.1 – §3.3：三段加速度、边界、census 102 / 100。main
- N5 §2 #8（G-03）。main
- TF §2.1、§2.4。main
- [反编译] `Ground_GetAccel` 0x140a36450、`Accelerate` 0x140a4a0d0；倍率 k 玩家偏移 0x1e00、k′ 0x4060 [native-inf，平时为 1]。

---

### 3.3 冲刺

#### 原理

冲刺是"按住冲刺键往前跑"时更高的速度上限，加上一段很慢的加速（§3.2 的冲刺段）。它只在地上、往前、不蹲时成立；跳起来以后上限回到走路的 199.5，但已有的速度在空中不会被磨掉（§3.6），所以"冲刺跳"能把 299 带进空中。

#### 规则和公式

1. 一条命令算"冲刺中"，要同时满足：着地；这条和上一条命令都按着冲刺键；前后轴 > 0；不蹲（上一条和这一条都没按蹲）；不在滑铲。
   - "上一条也按着"的效果：按下冲刺后**下一条命令**上限才变成 299（M2 实测：MT 的 `ms` 晚一条命令从 199.525 跳到 299）。
2. 冲刺中输入的两个轴先 × 1.25 再进输入曲线（§3.4 第 4 条）。前进键按满时 1.25 被归一化回 1，所以只影响半按和斜向（G-09，只有代码）。
3. 冲刺中的加速见 §3.2；冲刺中的减速见 §3.4（h > msc × `speed` 时用 `sprintDeceleration`，R5 也是 1250，和普通减速分不开）。
4. **冲刺起步键没有作用**：`sprintStartDelay` 0.2 s、`sprintStartDuration` 0.8 s、`sprintStartFastDuration` 0.2 s 在速度上都看不到（M2：按下后 0.14–0.17 s 冲刺段已经开始，没有 0.2 s 的平台，也没有"快段"）。可能只管动画或镜头 [推断]。
5. 空中不冲刺：起跳以后上限是 `speed` × msc（199.525），但这个上限只影响空中加速的意图（§3.6），不削速度。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冲刺上限 | 7.595 m/s | 299 u/s | 4.153 H/s | — | [实测] |
| 冲刺时输入放大 | — | 1.25（×） | — | 只有代码 | [反编译] |
| `sprintDeceleration` | 31.75 m/s² | 1250 u/s² | 17.36 H/s² | 和 `deceleration` 相同，分不开 | [数据] |
| `sprintStartDelay` / `Duration` / `FastDuration` | — | 0.2 / 0.8 / 0.2 s | — | 对速度无影响 | [数据] [实测] |

冲刺时的眼高下沉、横滚在第 07 章。

**TF2 对比**：冲刺上限相同；TF2 冲刺不需要攒（加速始终 2500）。

#### 实现模板

```
sprinting = grounded and sprintHeld and prevSprintHeld and fwd > 0
            and not prevDuckHeld and not duckHeld and not sliding
```

Unity：`R5MotorV2.Move` 开头的 `sprinting = …` 一行；`sprintButtonMask`（`R5MotorV2Params`，冲刺键在 R5 录像里是第 15 位或 `IN_SPEED`）；1.25 在 `R5MotorV2.GroundNativeStep`。

"前后轴 > 0"这一条是 Unity 的写法，R5 斜后方、纯侧向时能不能冲刺没有单独测过（写进 `_notes`）。

#### 验收

- `R5MotorV2FormulaTests.SprintFlagSetOneCommandAfterThePress`、`SprintRampUsesSprintAccelAboveWalkCap`。
- 对照数据：GM §3.3（`e1_sprint`、`e1_turn`，各 5 次）。
- 合格线：从按下到 299 的时间和 R5 差 ≤ 3 帧；稳定速度 299.000。

#### 出处

- GM §3.3：冲刺上限、晚一条命令、冲刺段、起步键无影响。main
- NG §2.1（G-09，1.25）、§2.4（`sprintDeceleration`）。main
- [反编译] 冲刺标志玩家偏移 0x2a2c [native-inf]；`GetPoseSpeed_Sprint`。

---

### 3.4 地面摩擦、减速和转向

#### 原理

松开方向键，角色以**固定的减速度**停下（不是 Source 那种"越快减得越多"的摩擦），所以停下的距离和时间很好预判：走路 0.16 s 停住，冲刺 0.24 s。

按着方向键时，摩擦**只削掉偏离你想去方向的那部分速度**，顺着意图方向、不超过目标速度的那部分不受摩擦。效果：

- 鼠标慢慢转（每条命令只差零点几度）几乎不掉速；
- 按键急转（W → D、W → S）时旧方向的速度按 1250 u/s² 被削掉、新方向的速度按 §3.2 的加速度长起来，**中间会明显掉速再回升**。冲刺中 W → D 急转，速度从 299 掉到 131，0.23 s 后才转到新方向。

这让"转身"有重量，但不会惩罚正常的瞄准转动。

#### 规则和公式

每条着地、不滑铲的命令：

1. **没有方向输入**：h ← h − D · dt；h < `stopSnapSpeed`（1 u/s）时归零。方向不变。
2. **有方向输入**（原生 `Friction` + `Accelerate`）：
   1. 用加速前的 h 选好 §3.2 的加速度 a；
   2. **保护意图方向的速度**：p = v · ŵ。若 p > 0，保护部分 k = ŵ · p · min(1, p · wishspeed / h²)，即意图方向上的分量最多保护到 wishspeed；
   3. 剩余部分 r = v − k 的大小按 D 线性减：|r| ← max(0, |r| − D · dt)；
   4. v = k + r，然后做 §3.2 的 `Accelerate`；
   5. |v| < `stopSnapSpeed` 时归零。
3. 减速度 D（**不乘 msc**）：蹲着 `crouchDeceleration`；h > msc × `speed` 时 `sprintDeceleration`；否则 `deceleration`。（`deceleration` < 0 时原生用 `acceleration` × 0.6，R5 不走这一支，TF2 走。）
4. **输入曲线**：意图幅度 m = |(f, s)|（冲刺时先 × 1.25）。m > 1 归一到 1；0 < m ≤ 1 时改成 m · (2 − m)，所以半按 0.5 → 0.75。wishspeed = min(m, 1) × cap。
   - 键盘在 R5 里按下那一条命令的轴值是 0.5（按键发生在帧中间），经过曲线变 0.75。HSD 游戏的按键输入第一条就给 1。这是输入层的差别，归第 06 章。
5. 超过上限时（例如落地时 350 u/s 而按着方向键），速度按 D 往上限降，不会一步截断（Accelerate 的上限是 max(原 |v|, wishspeed)，摩擦削的是偏离部分 + 超出 wishspeed 的部分）。
6. 原生 `Friction` 里另有一个"0.5 s 淡入"：D 在某个时刻 T 之前的 0.5 s 内从 0 升到 1（G-15）。T 是什么没读出来，平地实测里看不到它，Unity 没做。击退后的"一小段时间不减速"在第 05 / 06 章。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 减速 `deceleration`（不乘 msc） | 31.75 m/s² | 1250 u/s² | 17.36 H/s² | 实测 1249.90 | [数据] [实测] |
| 蹲姿减速 `crouchDeceleration` | 38.10 m/s² | 1500 u/s² | 20.83 H/s² | 实测 1499.76；不是 1250 × 1.15 | [实测] [反编译：按姿态取值] |
| 停止吸附 `stopSnapSpeed` | 0.0254 m/s | 1 u/s | 0.0139 H/s | 实测区间 (0.58, 1.58] | [反编译] [实测] |
| 输入曲线 | — | m(2 − m)；0.5 → 0.75 | — | — | [反编译] |
| 走路停下（199.525 → 0） | — | 0.160 s（23 条命令） | — | — | [实测] |
| 冲刺停下（299 → 0） | — | 0.243 s（35 条） | — | — | [实测] |
| 蹲走停下（92 → 0） | — | 0.063 s（9 条） | — | — | [实测] |
| 冲刺 W → D（90°）急转：转到 5° 以内 / 速度最低 | 3.317 m/s（最低） | 0.233 s / 130.6 u/s | 1.814 H/s | 5 次几乎一样 | [实测] |
| 冲刺 W → S（180°）：转到 / 最低 | — | 0.150 s / 0 u/s | — | — | [实测] |
| 走路 A → D（180°）：转到 / 最低 | — | 0.083 s / 8.4 u/s | — | — | [实测] |
| 冲刺中加按 D（45°）：转到 / 最低 | — | 0.158 s / 219.8 u/s | — | — | [实测] |

**为什么不用 Source 摩擦**：Source 的 drop = max(s, stopspeed) · f · dt 拟合 R5 停下误差 3.08 u/s 每条命令；固定减速 0.0046（GM §3.4）。`sv_friction` 在 R5 里只用于穿墙飞行和观战，不在普通地面路径上（NG §3）。

**TF2 对比**：同样的结构（保护意图方向 + 固定减速 + Accelerate 上限）。TF2 减速 = 2500 × 0.6 = **1500 u/s²**（38.10 m/s²），不乘 msc；另有"受冲击后低摩擦"乘在 D 上（TF §2.2 – §2.5，归第 06 章）。

**HSD 的历史版本**（都留开关，回放电机 `LegacyM2()` 能逐字节复现）：

- M2：每条命令 v = s · ŵ，转向瞬间完成。按键急转时和 R5 差两三个数量级（N4B §3），鼠标慢转时几乎一样。
- M5 `groundVectorRedirect`：偏离部分按 D 衰减、意图方向按段加速，按键急转 rms 0.11–0.60 u/s（N5 §1）。M10-D4 修过一次反向卡住的问题（`along = max(0, v·ŵ)`）。
- 现在（N7，D-49 起两套电机都用）`groundNativeFriction`：原生公式，按键急转 rms 0.002–0.046 u/s。它优先于 `groundVectorRedirect`。

#### 实现模板

```
// 单位：u、s；着地、不滑铲、本条命令不起跳
groundMove(v, f, s_axis, ducked, sprinting, cap, msc, dt):
    h = |v|
    if no input:
        D = ducked ? crouchDeceleration : deceleration
        h = h - D*dt;  if h < stopSnapSpeed: h = 0
        return dir(v) * h
    // 输入曲线
    (f, s_axis) *= sprinting ? 1.25 : 1
    m = |(f, s_axis)|
    if m > 1: normalize, m = 1  else: (f, s_axis) *= (2-m), m *= (2-m)
    wishspeed = min(m,1)*cap;  w = unit(forward*f + right*s_axis)
    a = groundAccelRate(h, msc)                        // §3.2，用摩擦前的 h
    // 摩擦：保护意图方向
    p = dot(v, w);  k = 0
    if p > 0 and h > 0: k = w * p * min(1, p*wishspeed/(h*h))
    r = v - k
    D = ducked ? crouchDeceleration : (h > msc*speed ? sprintDeceleration : deceleration)
    r *= max(0, |r| - D*dt) / |r|
    v = accelerate(k + r, w, wishspeed, a, dt)         // §3.2
    if |v| < stopSnapSpeed: v = 0
    return v
```

Unity：`R5MotorV2.GroundNativeStep`（有输入、`groundNativeFriction` 为真）；`R5MotorV2.GroundSpeedStep`（无输入）；`R5MotorV2.GroundVectorRedirect`（M5 版，留作开关）。

#### 验收

- `R5MotorV2FormulaTests.DecelIsConstantNotScaledAndSnapsBelowOne`。
- `N7NativeReferenceTests.NativeGroundStepTurnsGraduallyAndAppliesTheInputCurve`。
- `R5MotorV2FormulaTests.VelocityRedirectsInstantlyWithYaw`（测的是 M2 规则，回放电机 `LegacyM2()` 用）。
- 对照数据：GM §3.4（35 次停下）；N4B 的 20 次按键急转（`research/rea-native/n4/keyturn_analysis.py`）。
- 合格线：停下每条命令误差 ≤ 0.01 u/s；按键急转逐命令 rms ≤ 0.05 u/s（原生公式的水平）；FEEL §2"停下用时 / 距离"3 帧或 5 % / 2 u 或 5 %。

#### 出处

- NG §2.1、§2.3、§2.4（G-06 – G-08、G-13 – G-15）：输入曲线、摩擦、减速选择、0.5 s 淡入。main
- N4B §3 – §4：按键急转逐命令吻合、转向过程表。main
- N4D §1（G-06 吸附 < 1 在 `WalkMove` 里）。main
- GM §3.4：固定减速、蹲姿 1500、停下时间、Source 摩擦的拟合。main
- N5 §1（G-07 更正）、§2 #6。main
- `research/phase2-local/m10/unity/M10D4-UNITY.md`：M5 版反向卡住的修复。main
- `R5-DIFF-ARCHIVE.md` RUD 节、D-49：回放电机换成原生 WalkMove；D-66 回放电机到此为止。main
- TF §2.2 – §2.5。main
- [反编译] `Friction` 0x140a4a280、`Ground_GetDecel` 0x140a36580、`WalkMove` 0x140a4a7c0；淡入时刻 T 玩家偏移 0x2a50；三个减速倍率 0x1e00 / 0x4060 / 0x2af8 [native-inf]。

---

### 3.5 蹲走

#### 原理

蹲下以后又慢（92 u/s）又停得快（1500 u/s²），是一个"精确站位"的姿态。高速时按蹲不会进入蹲走，而是滑铲（第 04 章）；滑铲结束后如果还蹲着，就落到蹲走。

#### 规则和公式

1. 着地、不滑铲、上一条命令按着蹲 → 蹲姿：上限 `crouchSpeed` × msc，减速 `crouchDeceleration`。
2. 加速度照 §3.2 分段。92 < 138，所以蹲走只用到低速段（2875）。**蹲姿 138 u/s 以上的加速没测过**（比如从冲刺按蹲但速度不够滑铲的时候）。
3. 按下蹲、速度 ≥ `slideRequiredStartSpeed`（200 u/s）→ 滑铲（第 04 章），不是蹲走。
4. 下蹲过渡（眼高 0.4 s、碰撞体变矮 0.2 s）中的移动没测过；HSD 按"上一条命令按着蹲就是蹲姿"算。碰撞体在 [02](02-foundation.md)，眼高在 [01 §4.2](01-units-body.md) 和第 07 章。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 蹲走上限 | 2.337 m/s | 80 × 1.15 = 92 u/s | 1.278 H/s | TF2 80（× msc） | [实测] |
| 蹲姿减速 | 38.10 m/s² | 1500 u/s² | 20.83 H/s² | — | [实测] |
| 起滑最低速度 `slideRequiredStartSpeed` | 5.080 m/s | 200 u/s | 2.778 H/s | 见第 04 章 | [数据] |

#### 实现模板

同 §3.1、§3.4，`ducked = prevDuckHeld`。Unity：`R5MotorV2.Move`（`ducked`）、`GroundCap`、`GroundNativeStep`（D 的选择）。

#### 验收

- `R5MotorV2FormulaTests.CapsWalkSprintCrouch`、`DecelIsConstantNotScaledAndSnapsBelowOne`（含蹲姿 1500）。
- 对照数据：GM §3.5（`e1_crouch` 5 次）。
- 合格线：上限 92.000；停下 9 条命令。

#### 出处

- GM §3.4 – §3.5；N4D §1（G-05）。main
- `research/phase2-local/m2/ground/params.json`（`crouch_speed`、`crouch_deceleration`）。main

---

## 空中

### 3.6 空中加速和转向

#### 原理

空中**没有任何摩擦和阻力**：起跳带进来的速度一直保留到落地（DP P3"动量是玩家的资产"）。方向键在空中只能沿意图方向补到一个很小的速度（69 u/s），所以：

- 冲刺跳以后按着 W 不会更快，也不会变慢；
- 按着方向键、只转鼠标，几乎拐不了弯（0.25 s 只转 3°）；
- 想在空中大幅改方向，要用起跳后的 lurch（§3.12），而不是一直按着键。

这是 Source 系的"空中扫向"（air strafe）：只要速度在意图方向上的分量小于 69，就能补上去，所以边转视角边按侧向键可以慢慢拐弯、甚至略微提速，但效率很低。

#### 规则和公式

每条空中命令（不起跳、不在外力或攀爬中）：

1. wishspeed = min(|意图|, 1) × `speed` × msc（蹲着按 `crouchSpeed` × msc）；wishcap = min(wishspeed, `airSpeed` × msc) = 69 u/s。
2. addspeed = wishcap − v_h · ŵ。
3. **addspeed > 0**：v_h += min(addspeed, `airAcceleration` · dt) · ŵ。**不乘 wishspeed**（和 Quake / Source 的 `sv_airaccelerate` 写法不同）。
4. **addspeed ≤ 0**（意图方向上已经够快）：v += `extraAirAccel` · dt · ŵ，然后 **3D** |v| 限制在 max(加速前的 3D |v|, wishcap)。效果：竖直速度不为 0 时水平方向能"借"到一点点速度，竖直分量被同比例压一点，每跳约 +0.3 u/s（0.1 %）。
5. 空中没有摩擦、没有阻力（census `airFriction` 0、`airDrag` 0；实测无输入时水平速度每条命令变化 0.0000）。
6. 意图方向用这条命令自己的视角（不是上一帧的）。
7. 空中按方向键的新按下沿还会触发 lurch（§3.12），lurch 在空中加速**之后**做。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 空中意图上限 `airSpeed`（× 1.15） | 1.524 m/s（1.753） | 60 u/s（69） | 0.833 H/s（0.958） | 实测 [69.000, 69.000]；Horizon 80 | [数据] [实测] |
| 空中加速 `airAcceleration` | 12.70 m/s² | 500 u/s²（不乘 msc） | 6.944 H/s² | 实测 499.95；Horizon 800 | [数据] [实测] |
| 空中额外加速 `extraAirAccel` | 0.0508 m/s² | 2 u/s² | 0.0278 H/s² | 每跳 +0.30 u/s（模拟 0.316） | [反编译] [实测] |
| 空中摩擦 / 阻力 | — | 0 / 0 | — | 实测 0.0000 | [数据] [实测] |
| 按着 W 只转视角 0.25 s 的航向变化 | — | 3.1° | — | — | [实测] |

例（AJ §3.2，`e2_strafe`）：按侧向键并转视角时，v · ŵ > 69 的那段速度不变（253.5），转到 v · ŵ < 69 时升到 263.3，ŵ 转过速度方向 90° 以后降到约 194。

**TF2 对比**：完全相同的 `AirAccelerate`（60 / 500 / 额外 2.0，3D 上限）。TF2 引擎注释说额外加速是"帮助开始跑墙"：已经很快时也能慢慢把方向扳向墙（TF §3.1）。

#### 实现模板

```
// 单位：u、s
airAccelerate(v, w, wishspeed, msc, dt):
    wishcap = min(wishspeed, airSpeed*msc)
    if wishcap <= 0: return
    add = wishcap - dot(v.xy, w)
    if add > 0:
        v.xy += w * min(airAcceleration*dt, add)
    else if extraAirAccel > 0:
        before = |v|                           // 3D
        v.xy += w * extraAirAccel*dt
        lim = max(before, wishcap)
        if |v| > lim: v *= lim/|v|             // 3D 缩放，竖直分量也一起缩

airMove(dt):
    v.z -= 0.5*g*dt                            // 前半步重力（§3.7）
    airAccelerate(...)
    if 方向键新按下沿: lurch(...)              // §3.12
    pos += v*dt
    v.z -= 0.5*g*dt                            // 后半步重力
    checkLanding()                             // 第 02 章
```

Unity：`R5MotorV2.AirAccelerate`（静态，7 个参数的版本带 `extraAccel`）、`R5MotorV2.AirMove`、`R5MotorV2.AirMaxSpeed`；参数 `airSpeed`、`airAcceleration`、`extraAirAccel`（Reference 2，回放电机 0）。

#### 验收

- `R5MotorV2FormulaTests.AirAccelCappedAtAirSpeedTimesMoveScaleWithoutDrag`。
- `N7NativeReferenceTests.ExtraAirAccelAddsTwoAtTheCapUnderThe3DLimit`。
- 对照数据：AJ §3（1614 条空中命令；`e2_strafe` / `e2_noinput` / `e2_keepfwd` 各 5 次）。
- 合格线：每条空中命令 rms ≤ 0.005 u/s，最大 ≤ 0.015（AJ §3.2 的水平）；一次冲刺跳的水平净增 0.30 ± 0.05 u/s；FEEL §2"空中转向角 / 速度"2° / 3 u/s 或 1 %。

#### 出处

- AJ §3.1 – §3.2：没有空气摩擦、A · dt 不乘 wishspeed、上限 69、当前视角。main
- NJ §2（J-05、J-06）：额外加速 2.0 和 3D 上限，数值核对 0.316 vs 0.301。main
- A1 TL;DR、§4：只转视角 0.25 s 转 3.1°。main
- N4A §4：Horizon `airAcceleration` / `airSpeed` 800 / 80。main
- TF §3.1。main
- [反编译] `AirAccelerate` 0x140a485e0；`AirMove` 0x140a48f90（本体没读，见缺口）。

---

### 3.7 重力和半步积分

#### 原理

重力每条命令分成前后两半：前半步在移动前、后半步在移动后，位置用两者的平均速度推进。这样位置的轨迹和真实抛物线一致，和帧率几乎无关。起跳那一帧多一个半步（§3.8），所以跳的最高点比 `jumpHeight` 低约 1 u，而且和帧率有关。

#### 规则和公式

1. g = `svGravity` × `gravityScale` = 750 × 1 u/s²。
2. 空中每条命令：v.z −= ½ g dt；移动 pos += v dt；v.z −= ½ g dt。等价于 z 按 (vz_前 + vz_后)/2 · dt 推进。
3. 着地时去掉速度沿地面法线的分量（平地上 v.z = 0）。
4. 每条命令的完整顺序（重力前半步 → 跳 / 攀爬 / 外力 → 地面或空中移动 → 落地检测 → 重力后半步）是第 02 章的内容。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| `svGravity` | 19.05 m/s² | 750 u/s² | 10.42 H/s² | 实测 749.907 | [数据] [实测] |
| `gravityScale` | — | 1（×） | — | TF2 0.8 | [数据] |

**TF2 对比**：TF2 `gravityScale` 0.8，下落重力 600 u/s²（15.24 m/s²，8.333 H/s²）；但起跳速度用的是不乘 `gravityScale` 的 750（§3.8）。

#### 实现模板

见 §3.6 的 `airMove`。Unity：`R5MotorV2.AirMove`、`R5MotorV2Params.Gravity`（`svGravity × gravityScale`）。

#### 验收

- `R5MotorV2FormulaTests.GravityHalfStep`：一条空中命令后 vz = −750·dt，z = z₀ − 750·dt²/2。
- 对照数据：AJ §2.1（10 054 条空中命令，半步积分 Δz rms 0.00065 u；显式 / 半隐式 0.0184 u，排除）。
- 合格线：Δz 每条命令误差 ≤ 0.002 u。

#### 出处

- AJ §2.1：g 和半步积分的拟合。main
- NG §1：`FullWalkMove` 里重力前后两个半步。main
- CVD：`sv_gravity` 750。main
- TF §0、§4.1。main
- [反编译] `Gravity_HalfStep` 0x140a36130（NATIVE-MAP §3 把它误名为 `Grapple`，以 NG 为准）；`FullWalkMove` 0x140a4c810。

---

## 跳跃和落地

### 3.8 起跳（普通跳）

（README 示范条目搬过来，核对后补了：最高点和帧率的关系、连跳惩罚的开关标志、起跳朝墙推、`gravityScale` 的位置、TF2 对比。）

#### 原理

按下跳跃，角色总是跳到**同样的高度**：跳多高由一个高度值决定，起跳速度从高度反算出来。这样改重力时跳跃高度不变，关卡里"能不能跳上去"只看一个数。

有两条附加规则，都是为了不让玩家用连续起跳刷速度或高度（对应 DP P3"动量是玩家的资产，只有明确规则才能收走"和 P4"技巧窗口按时间算"）：

1. **刚落地又跳，跳得矮**：落地后 0.15 s 内再跳只有正常高度的 30 %，到 0.75 s 线性恢复到 100 %。连续兔跳会越来越矮，但正常的"落地—停一下—再跳"不受影响。
2. **刚落地又跳，超出冲刺速度的部分被削掉一点**：落地 1 s 内起跳、水平速度超过冲刺上限时，减 100 u/s，但不低于冲刺上限。高速连跳的速度会一跳一跳往冲刺速度收，不会无限保持。

滑铲中起跳用另一个较低的高度，滑铲跳的水平速度规则在第 04 章。

#### 规则和公式

1. 起跳只在**着地时、跳跃键按下的那一帧（按下沿）**触发。按住不放不会自动连跳（R5 SDK 的 `sv_autobunnyhopping` 默认 0）。空中按下的跳跃，没有二段跳等能力接手就直接丢掉（没有缓冲，§3.11）。
2. 高度 H_j：平时 `jumpHeight`，滑铲中 `slideJumpHeight`。
3. 连跳高度系数（t = 现在 − 上次落地时刻；从没落过地则 t = ∞）：

   frac(t) = clamp(f + (1 − f) · (t − T_min) / (T_max − T_min), f, 1)，f = `antiMultiJumpHeightFrac`

   原生代码里这条惩罚还要一个玩家标志为真才生效，这个标志什么时候为真没读出来（社区资料说地面跳、coyote 跳、攀爬跳、跳板跳会打开，滑索跳、翻越跳不会，未核实）。Unity 每次地面起跳都算。见本章"缺口"。
4. 起跳竖直速度 V = √(2 · g · H_j · frac)。竖直速度先清零再加 V（不叠加原来的竖直速度）。
   - 原生和 TF2 的代码里这里的 g 是 `sv_gravity`，**不乘 `gravityScale`**。R5 `gravityScale` = 1，没有区别；TF2 是 0.8，所以 TF2 实际跳得比 `jumpHeight` 高（60 u → 75 u）。HSD 现在用 `svGravity × gravityScale`，以后有人改 `gravityScale` 时要先定用哪一种（写进 `_notes`）。
5. 超速削减：t < `groundJumpSkipTime` 且水平速度 v_h > R（R = 冲刺上限 = `sprintspeed` × msc）时，v_h ← max(R, v_h − `groundJumpSkipReduce`)，方向不变。
   - 原生还有两个默认不起作用的键：`skip_jump_height_fraction` 1.0（v_h > `skip_jump_height_speed` 450 时高度再乘它）和 `skip_speed_retain` −1（−1 表示 R 用冲刺上限）。
6. **起跳朝墙推**：如果这条命令的意图方向推向上一次移动碰到的面（ŵ · n < 0），速度再加 `jumpSurfacePush` · (−n)（30 u/s）。平地上起跳不起作用；它主要影响翻越跳和 superglide（第 04 章，D-23）。
7. 起跳那一帧**不做地面摩擦和地面加速**，照常做空中加速（§3.6）。这就是兔跳能保速的原因（§3.10）。
8. 起跳那一帧积分：竖直速度一共扣 1.5 个 g · dt（见实现模板）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力 g（`svGravity` × `gravityScale`） | 19.05 m/s² | 750 u/s² × 1 | 10.42 H/s² | TF2 750 × 0.8 = 600 u/s² | [数据] [实测] |
| 起跳高度 `jumpHeight` | 1.422 m | 56 u | 0.778 H | TF2 60 u | [数据] |
| 滑铲跳高度 `slideJumpHeight` | 1.270 m | 50 u | 0.694 H | TF2 50 u | [数据] |
| 起跳速度 V（frac = 1） | 7.362 m/s | 289.83 u/s | 4.025 H/s | 实测 289.815–289.833 | [算] [实测] |
| 实测最高点（144 fps） | 1.396 m | 54.95 u | 0.763 H | 54.92–55.00；公式见实现模板 | [实测] |
| 滞空（起跳到落地，144 fps） | — | 0.763 s | — | 2V/g = 0.773 s | [实测] [算] |
| 到顶时间 V / g | — | 0.386 s | — | — | [算] |
| 连跳系数下限 f `antiMultiJumpHeightFrac` | — | 0.3（×） | — | — | [数据] [实测] |
| 系数开始恢复 T_min `multiJumpHoldT0`（R5 键 `antiMultiJumpTimeMin`） | — | 0.15 s | — | — | [数据] [实测] |
| 系数恢复到 1 T_max（R5 键 `antiMultiJumpTimeMax`；Unity 存的是 `multiJumpRampT` = T_max − T_min = 0.60） | — | 0.75 s | — | — | [数据] [实测] |
| 最矮的连跳速度（frac = 0.3） | 4.032 m/s | 158.74 u/s | 2.205 H/s | — | [算] [实测] |
| 超速削减窗口 `groundJumpSkipTime`（R5 键 `skip_time`） | — | 1.0 s | — | TF2 0.1 s | [数据] |
| 超速削减量 `groundJumpSkipReduce`（R5 键 `skip_speed_reduce`） | 2.54 m/s | 100 u/s | 1.389 H/s | TF2 12 u/s | [数据] [实测] |
| 超速削减下限 R（空手冲刺上限 260 × 1.15） | 7.595 m/s | 299 u/s | 4.153 H/s | 随武器的移动倍率变；TF2 固定 450 | [数据] [实测] |
| 起跳朝墙推 `jumpSurfacePush` | 0.762 m/s | 30 u/s | 0.417 H/s | — | [反编译] [实测] |

**TF2 对比**（TF §4.1 – §4.2，T5 实测）：
- 高度 60 u，起跳速度 √(2 · 750 · 60) = 300 u/s（7.620 m/s），下落按 600，最高点约 75 u（1.905 m，1.042 H）。
- 没有连跳高度惩罚（`antiMultiJump*` 是 Apex 加的）。
- skip 规则是"落地 0.1 s 内起跳：高度 × 0.75；h > 450 时 h = max(450, h − 12)"。R5 把窗口拉长到 1 s、不降高度、下限改成冲刺上限、削减量加大到 100。

#### 实现模板

```
// 单位：u、s
on command(dt):
    if grounded and jumpPressedThisFrame:
        t     = now - lastLandTime              // 从没落地过 = ∞；测试工具的重置不算落地（D-55）
        frac  = clamp(f + (1-f)*(t - Tmin)/(Tmax - Tmin), f, 1)
        H     = sliding ? slideJumpHeight : jumpHeight
        if sliding:  slideJumpHorizontal()      // 第 04 章
        else if t < skipTime and vh > R:  vh = max(R, vh - skipSpeedReduce)
        V = sqrt(2 * g * H * frac)
        vel.z  = 0
        vel.z -= 0.5*g*dt        // 本帧开始的半步重力
        vel.z += V
        vel.z -= 0.5*g*dt        // 起跳自己的半步重力
        if dot(wish, lastHitNormal) < 0: vel -= lastHitNormal * jumpSurfacePush
        airAccelerate(...)       // §3.6；不做地面摩擦
        pos   += vel * dt
        vel.z -= 0.5*g*dt        // 本帧结束的半步重力
        grounded = false
        jumpTime = now           // lurch 窗口从这里算（§3.12）
```

离散化要注意：R5 按"半步重力"积分，起跳那一帧竖直速度一共扣了 1.5 个 g·dt。所以起跳后第一帧记录到的竖直速度不是 289.8，而是 V − 1.5·g·dt（144 fps 时约 282.0 u/s）；位移用的是 V − g·dt。照这个顺序做，最高点 = V²/2g − V·dt/2 + g·dt²/8，144 fps 时约 55.0 u，比 `jumpHeight` 低约 1 u（−V·dt/2），**帧率越低越矮**（60 fps 约 53.6 u）。这是 R5 本身的行为，不是误差，照做才能和 R5 录像对上。

Unity 参考实现：`HSD-Unity: Assets/HSD/R5Replay/Runtime/R5MotorV2.cs`，`R5MotorV2.JumpCommand`、`MultiJumpFrac`、`JumpSpeed`、`GroundJumpSpeed`（带 `tSinceLanding` 的版本）、`SurfacePush`；参数在 `R5MotorV2Params.cs`（`jumpHeight`、`slideJumpHeight`、`antiMultiJumpHeightFrac`、`multiJumpHoldT0` = 0.15、`multiJumpRampT` = 0.60、`groundJumpSkipReduce`、`groundJumpSkipTime`、`jumpSurfacePush`，全部 [u]）。回放电机 `groundJumpSkipReduce` = 0 时用旧规则 min(h, 299)（`groundJumpClampToSprintCap`），只在落地速度 > 399 时和原生不同。

#### 验收

- 单元测试（Unity EditMode，`Assets/HSD/R5Replay/Tests/Editor/`）：
  - `R5MotorV2FormulaTests.JumpRemovesOneAndAHalfGravitySteps`：V = 289.828，起跳后 vz = V − 1.5·g·dt，位移用 V − g·dt。
  - `R5MotorV2FormulaTests.MultiJumpPenaltyFraction`：frac(0) = frac(0.15) = 0.3，frac(0.45) = 0.65，frac(0.75) = 1，最矮 158.74。
  - `R5MotorV2FormulaTests.JumpRightAfterLandingIsPenalisedAndFirstJumpIsNot`：片段开头不算落地。
  - `N7NativeReferenceTests.OverCapHopLosesAHundredWithinTheSkipTime`。
  - `J1SurfacePushTests.AGroundJumpPushesIntoTheLastHitSurface`、`SurfacePushNeedsInputIntoTheSurface`。
  - R5MotorV2 没有"最高点"测试；README 示范里列的 `R5ReplayTests.JumpApexMatchesJumpHeight`（类 `ReferenceMotorTests`）测的是 M1 的 `ReferenceMotor`，容差 0.25 u，不适用于 `R5MotorV2`。建议补一个（`_notes`）。
- 对照数据：M2 的 42 次首跳，拟合起跳速度 289.823 u/s（sd 0.005）；最高点 54.951 u（sd 0.026，n = 37）；连跳每一跳的系数（AJ §2.2、§2.3、§4）；N4C §1 超速连跳 405.1 → 305.1（d0 组 5 次）。
- 合格线：起跳速度和 289.83 u/s 差 < 0.05 u/s；144 fps 最高点和 54.95 u 差 < 0.1 u；连跳系数和 frac(t) 差 < 0.01；超速连跳出口和 max(299, h − 100) 差 < 0.01 u/s；FEEL §2"跳跃高度"1 u 或 2 %；回放基线（第 11 章）不变。
- 已知例外：测试工具在 dedi 上重置玩家会被算成一次落地，重置后 0.75 s 内的第一跳会被降高（D-55）。对照 R5 录像时，重置后等 0.75 s 以上再跳。

#### 出处

- NJ §1.1、§5 J-01 – J-04：起跳高度、连跳惩罚、超速削减、`skip_*` 键、开关标志。main
- N4A §1：`antiMultiJumpTimeMin` / `Max` / `HeightFrac` = 0.15 / 0.75 / 0.3 运行时读回。main
- N4C §1：超速连跳 max(299, h − 100) 的实测（M3 分不开的那一种）。main
- AJ §2.2 – §2.4、§4：起跳速度、1.5 个半步、最高点公式、连跳系数、重置被算成落地。main
- `research/phase2-local/static-values/STATIC-VALUES.md` §2：`jumpHeight` 56、`gravityScale` 1。main
- CVD：`sv_gravity` 750。main
- `research/rea-native/ledger-open/LEDGER-OPEN-5.md`、`research/rea-native/n11/N11-OPEN-ITEMS.md`、D-23：起跳朝墙推 30。main
- D-55、`research/feel/F2-STANDING-JUMP.md`：原地跳高 1.8 u 是测试工具的重置。main
- LIB9 §3.10：社区资料里哪些跳会触发连跳惩罚（未核实）。main
- TF §4.1 – §4.2；T1；TVA（"反复跳的高度惩罚：TF2 没有"）。main
- `R5-DIFF-ARCHIVE.md` 第二部分"回放电机"一行：Reference 有 `groundJumpSkipReduce` 100 / `jumpSurfacePush` 30 / `extraAirAccel` 2.0 / `sprintAccelFixedEdge` / lurch 上限 0.7，回放电机保留 M2 / M3 规则（D-66 到此为止）。main
- [反编译] `Jump` 0x140a3b550；上次落地时刻 player+0x3680；连跳惩罚的开关标志 player+0x36a9；钩爪中 V 再乘 `grapple_jumpFrac`（第 05 章）。

---

### 3.9 落地

#### 原理

落地本身不吃速度：普通跳、冲刺跳落地，水平速度原样保留（落地那一帧还在空中算，下一帧才开始地面摩擦）。落地做三件事：记下落地时刻（连跳惩罚、超速削减从这里计时）、恢复二段跳等空中能力、太高处摔下来时短暂降速。

**硬着陆降速**是唯一一条"落地吃速度"的规则：从很高的地方摔下来，水平速度和速度上限先被压低，再在 1 s 内按平方曲线恢复。普通跳（落地竖直速度约 290 u/s）完全碰不到它，只有跳板、高处坠落才会触发。

#### 规则和公式

1. **什么时候算落地**：下落中（v.z < 0）、脚下 `groundProbe`（2 u）以内有可站的地面。具体判定在第 02 章。落地那条命令仍是空中命令（已经做了空中移动），v.z 清零；下一条命令开始走地面规则。
2. 落地时记 `lastLandTime` = 这条命令开始的时刻。传送、测试工具的重置**不算**落地（D-55；R5 的 dedi 会把重置算成落地，那是测试工具的副作用，不学）。
3. 落地时按住蹲、速度 ≥ `slideRequiredStartSpeed` → 接着滑铲（不加速，第 04 章）。
4. 二段跳恢复：原生 `skip_replenish_double_jump` = 1，每次落地都恢复（第 05 章）。
5. **硬着陆降速**（研究里有两种写法，**还没对上**，两种都写）：

   - **Unity 现在用的（M4 实测拟合，15 次硬着陆，rms 1e-4）**：落地那条命令，以落地前的竖直速度 vz：f0 = clamp(a + b · vz², 0, 1)；f0 < 1 时水平速度 × f0；之后移动倍率 × [f0 + (1 − f0) · (t / T)²]，直到 t ≥ T。f0 = 1 在 |vz| = 772.1 u/s，f0 = 0 在 1092.9 u/s。
   - **原生代码读出来的（NJ §3.2，没有实测）**：落地后 `landSlowdownDuration` 内，若下落高度 > `landSlowdownHeightMin`：a = clamp((高度 − 300)/(800 − 300), 0, 1)，b = (t / 1)²，倍率 = 1 − (1 − b) · a · (1 − `landSlowdownFrac`)，用作速度上限的倍率 [native-inf]。另有 `landSlowdownNoSprintFrac` 0.7（可能管落地后能不能冲刺，没读）。
   - **两者的差别**：把 vz 换成自由落体高度 h = vz² / 2g，Unity 的拟合是 f0 = 1.9965 − 0.002507 · h：从 h ≈ 397 u 开始降、到 796 u 降到 0；原生读法是从 300 u 开始降、到 800 u 降到 0。终点一致，起点差约 100 u，斜率不同。时间恢复部分（1 s、平方）两者一致。差别可能来自"下落高度"的定义（玩家偏移 0x3684 记的是什么高度）。要用 B03-3 的实测分开（从 300 / 500 / 800 u 落下）。**手册暂以 Unity 的实测拟合为准**（它对过 15 次 R5 落地），原生读法留档。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 落地探测距离 `groundProbe` | 0.0508 m | 2 u | 0.0278 H | 实测落地命令离地 0.255–1.982 u | [推断：Source] [实测] |
| 降速开始的落地竖直速度（Unity 拟合） | 19.61 m/s | 772.1 u/s | 10.72 H/s | — | [实测拟合] |
| 降到 0 的落地竖直速度（Unity 拟合） | 27.76 m/s | 1092.9 u/s | 15.18 H/s | — | [实测拟合] |
| 拟合系数 a / b | — / −2.591 × 10⁻³ (m/s)⁻² | 1.996467 / −1.6714 × 10⁻⁶ (u/s)⁻² | — | b 按速度平方的倒数换算（÷ 0.0254²） | [实测拟合] |
| 恢复时间 `landSlowdownDuration`（Unity `duration`） | — | 1 s（Horizon 0 = 不降速） | — | 拟合 0.998 | [数据] [实测] |
| 恢复指数 `landSlowdownTimePower`（Unity `exponent`） | — | 2（×） | — | — | [数据] [实测] |
| 原生 `landSlowdownHeightMin` / `HeightMax` | 7.620 / 20.32 m | 300 / 800 u | 4.167 / 11.11 H | 只有代码 | [数据] [反编译] |
| 原生 `landSlowdownFrac` / `NoSprintFrac` | — | 0 / 0.7（×） | — | 只有代码 | [数据] |

**TF2 对比**：TF2 没有硬着陆降速（TVA："硬着陆减速：TF2 没有"）。

#### 实现模板

```
// Unity 现在的写法（单位：u、s）
on landing command:  f0 = clamp(a + b*vz_pre^2, 0, 1)
                     if f0 < 1: vel.xy *= f0; tLand = now
following commands:  t = now - tLand
                     if t < T: moveScale *= f0 + (1-f0)*(t/T)^exponent
```

Unity：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/LandingSlowdown/LandingSlowdown.cs`（`LandingSlowdown`、`LandingSlowdownParams`，是游戏身体上的一个"能力"，不在 `R5MotorV2` 里；每个身体按传奇设 `duration`，Horizon 为 0）；落地判定 `R5MotorV2.CheckLanding`。

#### 验收

- `R5MotorV2FormulaTests.LandsWithinGroundProbeAndSnapsOnNextGroundCommand`。
- `LandingSlowdownTests.ImpactFactorMatchesTheFit`（vz −1025.149 → f0 0.2399）、`HardLandingCutsTheSpeedThenRecoversQuadratically`、`SoftLandingAndZeroDurationDoNothing`（`R5MotorM4AbilityTests.cs`）。
- 对照数据：OCT §4（跳板硬着陆，例 r1531：514.947 → 123.528 u/s）；AJ §2.3（落地命令 112/113 吻合）。
- 合格线：落地命令和 R5 同一条（差 ≤ 1 条命令）；硬着陆后的速度和拟合差 ≤ 0.5 %。

#### 出处

- NJ §3.1 – §3.2（J-09、J-10）：落地时刻、二段跳恢复、原生落地降速公式。main
- N4A §2：`landSlowdown*` 的值（1、2、0、300、800、0.7）。main
- OCT §4：硬着陆拟合 f0 = clamp(a + b·vz², 0, 1)、恢复 (t/T)²。main
- AJ §2.3：2 u 探测、落地命令离地高度。main
- D-55：重置不算落地。main
- TVA §2 对照表。main
- [反编译] `SetGroundEntity` 0x140a51650、`LandSlowdown_Scale` 0x140b09a60、`landSlowdownNoSprintFrac` 读取方 0x140b02ca0（未读）；落地时刻 player+0x3680、下落高度 player+0x3684。

---

## 时间窗口

### 3.10 落地马上再跳（兔跳的时机）

#### 原理

落地后**第一条地面命令**就起跳，这条命令不做地面摩擦（§3.8 第 7 条），所以速度几乎不丢；晚一条命令起跳，就先吃了一条命令的地面减速。这是 R5 兔跳的全部"技巧"：时机对了保速，但高度被连跳惩罚压低、超出冲刺上限的部分每跳削 100，所以兔跳只能"保住"冲刺速度附近的速度，不能刷速度。

#### 规则和公式

1. 落地命令是空中命令（§3.9 第 1 条）。下一条命令是第一条地面命令。
2. 第一条地面命令上按下跳 → 起跳，这条命令不做地面摩擦；水平速度只经过 §3.8 第 5 条的超速削减。
3. 晚 k 条命令起跳 → 先做 k 条地面命令（有输入时按 §3.4 削偏离部分、超速部分按 D 降；无输入时按 D 降）。
4. 高度按 §3.8 第 3 条：落地后 0.15 s 内起跳都是 30 %。

| 情况 | R5 实测 | 依据 |
|---|---|---|
| 落地后第一条命令起跳，落地前 405.0–405.1 u/s | 起跳后 305.0–305.1（= 405 − 100） | [实测] N4C d0，5 次 |
| 落地后隔一条命令起跳 | 落地后那条地面命令先降到 393.2–394.7，起跳后 299.0（393 − 100 < 299） | [实测] N4C d1，5 次 |
| 冲刺 299 兔跳（按住 W 和冲刺） | 第 2–5 跳出口 298.84（295.3–299.0），落地和起跳都不丢速；高度系数随每次在地上停的时间变（0.30 – 0.55） | [实测] AJ §4.1 `e4_hop0` |

**TF2 对比**：TF2 也是"落地帧起就有正常地面摩擦（约 1500），只有落地当帧起跳才几乎不丢速"（TF §4.2）。

#### 实现模板

无新代码：是 §3.8（起跳那条命令跳过地面移动）和 §3.9（落地那条命令仍是空中命令）的组合。Unity：`R5MotorV2.Move` 里 `if (grounded && input.jumpPressed) JumpCommand(...) else if (grounded) …地面移动…`。

#### 验收

- `N7NativeReferenceTests.OverCapHopLosesAHundredWithinTheSkipTime`；`R5MotorM3JumpChainTests.GroundJumpLeavesAtMinOfSpeedAndSprintCap`（回放电机的旧规则）。
- 对照数据：N4C §1（d0 / d1）；AJ §4（`e4_hop0` / `e4_hop3` / `e4_hop43`）。
- 合格线：同 §3.8。

#### 出处

- N4C §1；AJ §4；DEF E3"现有行为"（起跳那一帧摩擦约 0）。main
- DP P3 表（"连跳那条命令跳过摩擦"）。main
- TF §4.2。main

---

### 3.11 起跳缓冲（落地前按跳）

#### 原理

很多游戏会把"落地前几帧按下的跳"留到落地那一刻再执行，让兔跳更容易。R5 有没有这样做**没测过**。HSD 现在**没有缓冲**：跳跃只看这一条命令的按下沿，落地前按下的跳被丢掉（Reference）或者被二段跳接走（Fun）。这个问题用户 10-22 定为"先不决定，到游戏接近完成时再看"（D-09，DEF E3）。

#### 规则和公式

HSD 现在的规则（Reference 和 Fun 都没有缓冲）：

1. 跳跃按下沿只在这一条命令有效。着地 → 起跳；不着地 → 交给空中的跳跃使用者（二段跳、跑墙跳、滑索 super jump…，按第 06 章的仲裁），都不要就丢掉，**不留到下一条命令**。
2. Reference：落地前一条命令按跳 → 丢掉，落地后要重新按。
3. Fun：落地前一条命令按跳 → 只要二段跳还有次数、离起跳 > 0.1 s，就变成一次二段跳（第 05 章）。

R5：未知。原生有没有缓冲、缓冲几帧，都没有实验（B03-2）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 起跳缓冲时长 | — | **未测**（HSD 现在 0） | — | 常见设计 1–3 帧（DEF E3 方案 2），[设计] | — |

DEF E3 的四个方案（留档）：1 不加；2 只在 Fun 加 1–3 帧；3 缓冲和二段跳的优先关系可配置；4 先做 R5 实验（落地前 1–6 帧按跳）。

#### 实现模板

现在没有。如果以后要加，建议的位置（[设计]，没实现）：在第 06 章的跳跃仲裁 `JumpArbitration` 里记"被拒绝的按下沿"的时刻，落地那条命令之后的第一条地面命令上，如果这个时刻离现在 < 缓冲时长，就当作这条命令按下了跳。注意这会改变兔跳（§3.10）、二段跳、super jump 所有时机类技巧的难度。

Unity 相关位置：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/_Core/JumpArbitration.cs`（`JumpPressRecord`：每条命令的按下记录，"refused press is dropped"）；DEF E3 写的 `Runtime/Skills/JumpArbitration.cs` 已经搬到 `Abilities/_Core/`。

#### 验收

- HSD 现在：落地前一条命令按跳不起跳（Reference）。现有测试里没有专门断言这一条（`_notes` 建议补）。
- R5：B03-2 实验做完以后才有合格线。

#### 出处

- DEF E3（现有行为、四个方案、暂缓原因）；D-09。main
- `research/phase2-local/m8/unity/M8B-UNITY.md`（bunny hop / gaps 一节：Reference 丢掉、Fun 被二段跳接管）。main
- 99-TODO-RESEARCH B03-2。handbook/base

---

### 3.12 coyote time（走下台边还能跳）

#### 原理

"走出台边的一小段时间内仍然可以起跳"，让玩家不会因为晚按一帧掉下去。R5 里有一个 ConVar `jump_graceperiod` = 0.2，引擎自带的说明正是"从台边掉下后的额外起跳时间"，社区 wiki 也写 0.2 s。但**研究没有追到谁读这个值，也没有实测**（B03-1）。HSD 现在**没有通用的 coyote time**。

#### 规则和公式

HSD 现在：只有着地时才能起跳（§3.8 第 1 条）。走下台边的第一条空中命令起，地面跳就不可能了。

已知的相关事实（都不是 coyote 本身）：

| 现象 | 数 | 是什么 | 依据 |
|---|---|---|---|
| `jump_graceperiod` | 0.2 s | 说明文字是 coyote；读取方没追；和 lurch 窗口的 `jump_graceperiodmin` 0.2 只是数值相同 | [数据] CVD |
| 社区 wiki 的 coyote | 0.2 s；滑索、技能不打断，开始攀爬会打断 | 未核实 | LIB9 §3.9 |
| 走下台边不打开 lurch 窗口 | 离开后 0.017 – 0.4 s 按 D 都没有 lurch | lurch 的计时只从起跳算，不说明能不能跳 | [实测] RL d |
| 滑索 super jump 窗口 | 跳离后第 3–8 条命令内再按跳有效，≥ 63 条无效，中间没测 | 滑索专用（第 05 章） | [实测] LIB9 §3.9 / R-13 |
| 钩爪挂上后的"附加跳" | 挂上后 0.15 s（18 条命令）内按跳加一次普通跳，0.2 s（24 条）以后无效 | 钩爪专用（第 05 章）；文档推测是 coyote 0.2 s | [实测] GRAPPLE-M10 |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| coyote 时长 | — | **未测**（候选 `jump_graceperiod` 0.2 s；HSD 现在 0） | — | 常见设计 0.1–0.2 s，[设计] | [数据] [推断] |

#### 实现模板

现在没有。如果 B03-1 证实 R5 有，建议（[设计]，没实现）：记"最后一次着地的时刻"`lastGroundedTime`（走下台边时更新，起跳时清掉），空中按下沿时若 now − `lastGroundedTime` < coyote 且这段时间没有起跳过，就按地面跳处理（高度、连跳惩罚、超速削减照 §3.8，lurch 窗口从这一刻开始）。要同时定：coyote 跳算不算打开连跳惩罚（社区说算）、和二段跳谁优先（第 06 章仲裁）。

Unity：无。滑索的 `superJumpWindow` 0.2、钩爪的附加跳在第 05 章，不要拿来当通用 coyote。

#### 验收

无：R5 数据还没有。B03-1（走下台边后第 k = 1 – 30 条命令按跳）做完以后补。

#### 出处

- CVD 第 31 行、§"解读"第 1 条：`jump_graceperiod` 0.2 的说明文字，和 lurch 窗口的区别。main
- LIB9 §3.9、R-13。main
- RL d（走下 232 u 台边不 lurch）。main
- `research/phase2-local/m10/r_grapple/GRAPPLE-M10.md`（Jump Grapple 0.15 / 0.2 s）。main
- 99-TODO-RESEARCH B03-1。handbook/base

---

### 3.13 时间窗口总表

#### 原理

R5 的技巧窗口都按**时间**算，和帧率无关，所以能练（DP P4"技巧窗口按时间算，地板低、天花板高"）："地板低"是指什么都不按也能正常跑跳，窗口只给会操作的人多一点；"天花板高"是指 lurch、兔跳、滑铲跳这些窗口叠起来，高手能做出远超普通玩家的路线。防滥用的窗口（连跳惩罚、超速削减）也按时间算，而且只"收"超出部分，不碰正常操作。

#### 规则和公式

本章涉及的窗口（别章的列出来方便对照）：

| 窗口 | 从什么时候算 | 时长 | 效果 | 状态 | 章节 |
|---|---|---|---|---|---|
| 兔跳保速 | 落地后第一条地面命令 | 1 条命令 | 这条命令起跳不吃地面摩擦 | [实测] | §3.10 |
| 连跳高度惩罚 | 上次落地 | 0.15 s 平台（× 0.3），到 0.75 s 线性恢复到 × 1 | 起跳高度 | [实测 + 反编译] | §3.8 |
| 超速削减 | 上次落地 | 1.0 s | 起跳时 v_h > 299 → max(299, v_h − 100) | [实测 + 反编译] | §3.8 |
| 硬着陆恢复 | 落地 | 1 s，平方 | 速度上限 | [实测 + 反编译] | §3.9 |
| lurch 强度 | 最近一次起跳命令开始 | 0.2 s 满（0.7），到 0.5 s 线性到 0 | 起跳后改方向 | [实测 + 反编译] | §3.14 |
| coyote time | 走下台边 | **未测**（`jump_graceperiod` 0.2？）；HSD 无 | 台边外还能跳 | 缺 | §3.12 |
| 起跳缓冲 | 落地前按跳 | **未测**；HSD 无 | 落地前的按键算数 | 缺（D-09 暂缓） | §3.11 |
| 冲刺生效 | 按下冲刺 | 1 条命令 | 上限 199.5 → 299 | [实测] | §3.3 |
| 滑铲早跳退还 | 按下蹲的下一条命令 | 0.2 s 下蹲过渡（且 0.4 s 内） | 退还滑铲加成 | [实测 + 反编译] | 第 04 章 |
| 滑铲加成冷却 | 上次开始滑铲 | 2 s | 不加速 | [实测 + 反编译] | 第 04 章 |
| superglide | 翻越结束前 | 约 0.1 s | 翻越跳变 superglide | [反编译] | 第 04 章 |

"地板低、天花板高"在本章怎么体现：

- **地板**：不会兔跳、不会 lurch 的玩家，跑、跳、停都正常，没有任何惩罚落到他们身上（连跳惩罚只在 0.75 s 内连续起跳时出现，超速削减只碰 299 以上的速度）。
- **天花板**：lurch 每次按下沿独立生效、没有次数上限和冷却（§3.14），起跳后 0.5 s 里按得越快、越准，能改的方向越多；兔跳时机对了能把冲刺速度一直带着走。

#### 实现模板

所有窗口都写成"时刻 + 时长"的比较（`now − t0 < T`），不要写成帧计数。Unity 里时刻都是 `R5MotorV2.time`（秒），各窗口的起点字段：`lastLandTime`（落地）、`jumpTime`（起跳）、`slideStartTime` / `boostTime` / `slideDuckPressTime`（滑铲）。

#### 验收

- `R5MotorM3LurchTests.WindowIsTimeBasedAt60_120_144`：同一个时间点在 60 / 120 / 144 fps 下 lurch 强度相同。
- 其余见各项。

#### 出处

- DP P4 表、§8.1。main
- 各项的出处。

---

## lurch 和 tap strafe

### 3.14 lurch（起跳后的方向修正）

#### 原理

起跳以后空中加速很弱（§3.6），但起跳后的半秒内，**每按下一个新的方向键**，水平速度的方向就朝按键方向转一下，大小不变。前 0.2 s 最强（每次朝按键方向插值 70 %），到 0.5 s 线性降到 0。每次改的速度量（向量差）最多 209.3 u/s，所以冲刺速度下一次最多拐约 41°；想拐更多要按好几下，而且都得在窗口里。

它让"起跳后马上改方向"成为一个有时间压力、有上限、可以练的技巧（DP P4），同时不给速度（只换方向，DP P3）。反向键（S）会被当成"往回拐"，但 209.3 的上限让它变成一次直线刹车。

#### 规则和公式

触发条件（**全部满足**才执行，每条命令最多一次）：

1. 在空中，这条命令上有**方向键的新按下沿**（W / S / A / D 中有一个"这条命令按着、上一条没按"）。松开键不算。起跳前就按着的键不算。
2. t = 这条命令开始的时刻 − 最近一次起跳命令开始的时刻，t < `lurchZero`（0.5 s）。"起跳"包括地面跳、滑铲跳、蹬墙弹跳等真正的跳；**走下台边不算**（不打开窗口）；跳板、升降梯弹出、击退在 Reference 里也不打开窗口（第 05 章）。
3. 这条命令开始时水平速度 ≤ `lurchCutoffSpeed`（1100 u/s）。
4. 意图方向不为零（见下面第 5 条，相反键抵消时为零 → 不执行）。

计算（在这条命令的空中加速**之后**）：

5. 意图方向 w 用**数字按键**合成，不用轴值：前后 = W − S，左右 = D − A（各取 0 / 1），再用视角的前向、右向合成并归一化。所以 W+A 是等权 45°；A 按住再按 D → 左右为 0 → 没有 lurch。
6. 强度 λ = `lurchLamMax` × clamp((`lurchZero` − t) / (`lurchZero` − `lurchFullEnd`), 0, 1)：0.2 s 内为 0.7，到 0.5 s 线性降到 0。
7. d = 当前水平速度方向；目标方向 d′ = normalize((1 − λ) · d + λ · w)；|(1 − λ) · d + λ · w| 太小（≤ 0.01）时不执行。
8. Δv = |v_h| · d′ − v_h；若 |Δv| > C，Δv 按比例缩到 C。C = `lurchClampSprintFraction` × `sprintspeed` × msc = 0.7 × 299 = 209.3 u/s（随移动倍率变：兴奋剂下 294.67）。
9. v_h += Δv；竖直速度不变。
10. **每个新按下沿都独立执行**：没有次数上限、没有冷却、没有衰减，每次都用自己的 λ(t) 和自己的上限 C（不是累计上限）。一次跳里可以有三次被夹紧的 lurch，共 627.9 u/s 的速度变化（A1）。
11. 每一次真正的起跳都重新开始窗口（包括蹬墙弹跳；Unity 里还有二段跳、跑墙跳、滑索跳离，第 05 章）。

几个结果（都是上面规则的直接推论，并有实测）：

| 情况 | 结果 | 依据 |
|---|---|---|
| 冲刺跳（299）后 0.2 s 内按 D（90°） | 被夹紧，航向转约 41°，速度不变 | [实测] M3、M8 |
| 按 S（反向） | 209.3 的直线刹车，方向不变 | [实测] M3 |
| 按 W（已经沿视角飞） | 什么都不发生 | [实测] M3 |
| A 按住、再按 W | 朝 W+A 的 45° 方向（实测 35.0°，预测 35.0°） | [实测] RL b1 |
| A 按住、再按 D | 没有 lurch（只有空中加速 3.5–4.2） | [实测] RL b2 |
| 起跳后 1090 u/s 时按 D | 有 lurch（212.79 = 209.3 + 空中加速） | [实测] N4D |
| 起跳后 1110 u/s 时按 D | 没有（4.17 = 只有空中加速） | [实测] N4D |
| 350 u/s 滑铲跳后按 D | 仍是 209.3（上限不随入口速度变），只是转得少（37.3° vs 44.7°） | [实测] RL e |
| 反向连按 W → W+D → D → S+D → S，每 0.05 s 一下 | 转到 156.4°，到不了 180°（后面的按下落在衰减段） | [实测] RL a |
| 同上，每 0.1 s 一下 | 104.6° | [实测] RL a |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 满强度 `lurchLamMax`（R5 `jump_grace_strength`） | — | 0.7（×） | — | 实测 0.70000（n = 44） | [反编译] [实测] |
| 满强度结束 `lurchFullEnd`（`jump_graceperiodmin`） | — | 0.2 s | — | ±1 ms | [反编译] [实测] |
| 强度到 0 `lurchZero`（`jump_graceperiodmax`） | — | 0.5 s | — | ±1 ms | [反编译] [实测] |
| 上限比例 `lurchClampSprintFraction`（`jump_grace_max`） | — | 0.7（× 冲刺上限） | — | — | [反编译] [实测] |
| 上限 C（空手：0.7 × 260 × 1.15） | 5.316 m/s | 209.3 u/s | 2.907 H/s | 兴奋剂下 294.67 u/s | [算] [实测] |
| 高速截断 `lurchCutoffSpeed`（`jump_grace_cutoff_speed`） | 27.94 m/s | 1100 u/s | 15.28 H/s | 实测在 (1090, 1110) | [反编译] [实测] |
| 冲刺速度下一次 lurch 最多改的航向 | — | 约 41°（2 · asin(209.3 / 598)） | — | — | [算] |

原生还有一组默认不生效的键（留档，不实现）：`jump_grace_require_tap` 1（0 时不要求按下沿）、`jump_grace_limit_to_90` 0、`jump_grace_min_tap_period` 0、`jump_grace_max_tap_count` 1000、`jump_grace_decay_start_tap_count` 1000、`jump_grace_multi_tap_decay` 1.0、按速度衰减的 `max_decay` 0、`jump_grace_controller_disable_duration` −1（手柄没测）。DP P4 的反例里提到"多次 tap 衰减做了又关了，原因不知道"。

**TF2 对比**：TF2 叫"keyboard grace"，四个数完全一样（0.2 / 0.5 s、0.7、0.7 × msc × 冲刺速度），T5 实测吻合，起跳前按住的键同样不触发。R5 多出来的是 `require_tap`、1100 截断和多次 tap 衰减这组键（T1）。

**SDK 的影响**（只在本地混合构建里，不学）：S3 dedi 上没有原生 lurch，是 SDK 重写的（`tapstrafe.cpp`，截断用 `bridge_lurch_cutoff_speed` 1100）；SDK 在 mantle boost 状态里屏蔽 lurch（`mantle_boost_disables_tap_strafes`）。翻越之后的 lurch 实测因此不能当原生行为（NL §4，第 04 章）。

#### 实现模板

```
// 单位：u、s；在 airMove 里、空中加速之后
lurch(v, keys, keysPrev, yaw, now, jumpTime, msc):
    if not anyNewPress(keys, keysPrev): return          // W/S/A/D 的按下沿
    if cutoff > 0 and |v.xy at command start| > cutoff: return
    t = now - jumpTime                                  // 从最近一次起跳命令开始算；走下台边不更新 jumpTime
    lam = lamMax * clamp((tZero - t)/(tZero - tFullEnd), 0, 1)
    if lam <= 0: return
    w = unit(forward(yaw)*(W-S) + right(yaw)*(D-A))     // 数字按键；相反键抵消
    if w == 0: return
    s = |v.xy|;  d = v.xy/s
    l = (1-lam)*d + lam*w
    if |l| <= 0.01: return
    D = s*unit(l) - v.xy
    C = clampFrac * sprintspeed * msc
    if |D| > C: D *= C/|D|
    v.xy += D
```

Unity：`R5MotorV2.AirMove`（触发条件：`input.moveKeyPressed`、`lurchSuppressed`、`mods.suppressLurch`、`lurchCutoffSpeed`）、`R5MotorV2.LurchLambda`、`R5MotorV2.Lurch`、`R5MotorV2.LurchClamp`；参数 `lurchLamMax`、`lurchFullEnd`、`lurchZero`、`lurchClamp`（回放电机的固定 209.3）、`lurchClampSprintFraction`（Reference 0.7）、`lurchCutoffSpeed`（Reference 1100）。按键输入：游戏侧 `SkillInput.WithKeys` / `DirKeys`（M10-D2：每个键独立，轴值 = W − S、D − A，`moveKeyPressed` = 有键这条按着、上一条没按），回放侧 `Replayer` 用录像里的 `buttons & 0x618` 新位。哪些起跳打开窗口、哪些外力不打开：`MovementConfig.liftEjectOpensLurchWindow` / `padLaunchOpensLurchWindow`（Reference false），第 05 章。

#### 验收

- `R5MotorM3LurchTests`：`LambdaPlateauFadeAndZero`、`PlateauReproducesDocConditions`、`ClampOnlyAboveTheTurnLength`、`FadeKeepsSpeedOnceUnclamped`、`BackIsAStraightBrake`、`ForwardRePressIsANoOp`、`WindowIsTimeBasedAt60_120_144`、`LurchAppliesAfterAirAccelerateOnThePressCommandOnly`、`NoLurchOnGroundOrWithoutAJump`。
- `M6LurchTests.StackingSameKeyLurchesOnEveryEdgeWithItsOwnClamp`、`ClimbBounceReAnchorsTheLurchWindow`（`R5MotorM6Tests.cs`）。
- `InputM10DTests.OpposingKeysCancelAndReleasesAreNotEdges`、`HeldKeyPlusNewKeyAimsAtTheEqualWeightDiagonal`、`ThreeKeyCombinationsFollowTheMeasuredRule`（`R5MotorM10DTests.cs`）。
- `PadLurchM10DTests.TheReferencePadLaunchOpensNoLurchWindowAndFunKeepsIt`。
- 对照数据：LM（102 次，60 / 120 / 144 fps）；A1（395 个按下沿，17 种条件）；RL（105 次）；N4D §2（截断）；M10D §1.4（三键组合 R-1a、R-1b）。
- 合格线：窗口外逐命令误差 ≤ 0.01 u/s，衰减段内 ≤ 0.35 u/s（A1：0.5 ms 时钟偏差的水平）；FEEL §2"空中转向角 / 速度"2° / 3 u/s 或 1 %。

#### 出处

- NL §2（公式、触发条件、默认不生效的键）、§3（L-01 – L-12）、§4（SDK 钩子）。main
- LM TL;DR、§1 – §2：插值模型、按时间的窗口、只作用于按下沿那一条命令、反向是直线刹车。main
- A1 TL;DR、§6：每个按下沿独立、没有预算、蹬墙弹跳重开窗口。main
- RL：反向连按、按住键 + 新键、相反键、走下台边、350 入口。main
- N4D §2：1100 截断实测。main
- M10D §1：按键独立输入、三键组合。main
- CVD：`jump_grace_*` 默认值和"只在 S21 客户端有"。main
- `research/phase2-local/m4/octane/OCTANE-PRIMITIVES.md`：兴奋剂下上限 294.67。main
- TF §3.2；T1。main
- D-40（LS / RAS 保持原生 lurch 模型）。main
- [反编译] `AirMove_TapStrafe` 0x140a48a30（SDK 名）、`TapStrafe_MultiTapDecay` 0x140a48810、`GetMaxSprintSpeed` 0x140b09c00、`TapStrafe_WindowHint` 0x140a58ec0；起跳时刻 player+0x3670（`jump_grace_jump` = 1）/ 0x366c。

---

### 3.15 tap strafe 和 lurch 连招（LS / RAS）

#### 原理

tap strafe 不是一条新规则，是 lurch 的一个用法：起跳后**一边转视角、一边反复按 W**（常把 W 绑到滚轮上，一次滚动就是一个按下沿）。每次 W 的按下沿把速度方向朝"现在的视角方向"拉 70 %，所以速度跟着视角转，大小不变。只转视角不按键几乎拐不动（§3.6），所以"转视角 + 连按 W"成了空中急转的办法。

社区说的 lurch strafe（LS）、RAS strafe 等，是**不转视角、用不同方向键连按**的 lurch 序列（比如 A → S → D，把速度往回扳）。它们都只是 §3.14 的规则一次次执行，HSD 不需要额外实现（D-40）。

#### 规则和公式

1. 和 §3.14 完全相同，按键是 W（或任何键），意图方向 = 这条命令的视角。
2. 每个 W 按下沿让速度方向和视角的夹角缩小约 70 %（满强度时；夹角大时受 209.3 上限限制）。
3. 所有按下沿都要在最近一次起跳后的 0.5 s 内，强的在前 0.2 s。

| 情况 | R5 实测 | 依据 |
|---|---|---|
| 360 °/s 转视角 + 连按 W | 速度航向转 81.0°（视角 88.6°），速度 × 1.0002 | [实测] A1 |
| 180 °/s | 40.5°（视角 44.3°） | [实测] A1 |
| 720 °/s，每 2 条命令一个 W 按下沿，15 次，0.25 s | 视角转约 176°，航向到 −161.2°（± 2.0），速度 × 1.0002 | [实测] RL c |
| 1440 °/s | 视角转一整圈，航向在后面追，最后落后约 30° | [实测] RL c |
| 只转视角不按键（对照） | 航向 0.0° 变化 | [实测] RL c |
| 一次反向需要的按下沿 | 约 5 个，都在起跳后约 0.25 s 内；0.1 s 一个时停在约 105° | [实测 + 算] TQ §2、RL a |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 参数 | — | 同 §3.14 | — | — | — |

**TF2 对比**：同一条规则，TF2 也能 tap strafe（keyboard grace 四个数相同）。

#### 实现模板

无新代码，§3.14。输入层要保证"一次滚轮滚动 = 一个按下沿"：游戏侧每个方向键有自己的按下锁存和滚轮队列（`HSD-Unity: Assets/HSD/Game/Runtime/TapKey.cs`，`PracticeGame.ReadInput`，M6-A1 / M10-D2），归第 06 章。

#### 验收

- `M6LurchTests.TapStrafeTurnsTheVelocityWithTheView`（`R5MotorM6Tests.cs`）。
- `TechniqueM9ATests.R1LurchCombos`、`R2LurchlessAirStrafe`（`R5MotorM9ATechniqueTests.cs`）。
- 对照数据：A1 §4（180 / 360 °/s）；RL c（720 / 1440 °/s，每次最大残差 0.14 / 0.28 u/s）。
- 合格线：同 §3.14；tap strafe 一段（0.25 s）的最终航向和 R5 差 ≤ 2°。

#### 出处

- A1 TL;DR、§4、§9。main
- RL a、c。main
- TQ §1 – §3（LS / RAS 的含义、都归结为 lurch）。main
- D-40。main

---

## 本章参数总表

参数名用 Unity 导出里的字段名（`HSD-Unity-UNITS/Docs/units/units-params.tsv` 的 `preset.Reference.motor.<字段>`，HSD-Unity PR #88，还没合并），R5 setfile / ConVar 的键名写在括号里。数值是 Reference 的值，全部 [u]。

| Unity 字段 | R5 键 | R5 原值 [u] | [m] | 本章 |
|---|---|---|---|---|
| `speed` | `speed`（站姿） | 173.5 u/s | 4.407 m/s | §3.1 |
| `sprintspeed` | `sprintspeed` | 260 u/s | 6.604 m/s | §3.1、§3.3 |
| `crouchSpeed` | `speed`（蹲姿） | 80 u/s | 2.032 m/s | §3.5 |
| `moveScale` | 移动倍率 | 1.15（×） | — | §3.0 |
| `speedScaleBack` / `speedScaleSide` | 同名 | 1 / 1（×） | — | §3.1 |
| `lowSpeed` | `lowSpeed` | 120 u/s | 3.048 m/s | §3.2 |
| `lowAcceleration` | `lowAcceleration` | 2500 u/s² | 63.50 m/s² | §3.2 |
| `acceleration` | `acceleration` | 450 u/s² | 11.43 m/s² | §3.2 |
| `sprintAcceleration` | `sprintAcceleration` | 102 u/s² | 2.591 m/s² | §3.2 |
| `sprintAccelFixedEdge`（开关） | — | true | — | §3.2 |
| `deceleration` | `deceleration`（站姿） | 1250 u/s² | 31.75 m/s² | §3.4 |
| `sprintDeceleration` | `sprintDeceleration` | 1250 u/s² | 31.75 m/s² | §3.4 |
| `crouchDeceleration` | `deceleration`（蹲姿） | 1500 u/s² | 38.10 m/s² | §3.4、§3.5 |
| `stopSnapSpeed` | （代码里的 1） | 1 u/s | 0.0254 m/s | §3.4 |
| `groundNativeFriction`（开关） | — | true | — | §3.4 |
| `airSpeed` | `airSpeed` | 60 u/s | 1.524 m/s | §3.6 |
| `airAcceleration` | `airAcceleration` | 500 u/s² | 12.70 m/s² | §3.6 |
| `extraAirAccel` | `player_extraairaccelleration` | 2 u/s² | 0.0508 m/s² | §3.6 |
| `svGravity` | `sv_gravity` | 750 u/s² | 19.05 m/s² | §3.7 |
| `gravityScale` | `gravityScale` | 1（×） | — | §3.7 |
| `jumpHeight` | `jumpHeight` | 56 u | 1.422 m | §3.8 |
| `slideJumpHeight` | `slideJumpHeight` | 50 u | 1.270 m | §3.8 |
| `antiMultiJumpHeightFrac` | 同名 | 0.3（×） | — | §3.8 |
| `multiJumpHoldT0` | `antiMultiJumpTimeMin` | 0.15 s | — | §3.8 |
| `multiJumpRampT` | `antiMultiJumpTimeMax` − `TimeMin` | 0.60 s | — | §3.8 |
| `groundJumpSkipTime` | `skip_time` | 1.0 s | — | §3.8 |
| `groundJumpSkipReduce` | `skip_speed_reduce` | 100 u/s | 2.54 m/s | §3.8 |
| `jumpSurfacePush` | （`Jump` 代码里的 30） | 30 u/s | 0.762 m/s | §3.8 |
| `groundProbe` | （Source 的 2） | 2 u | 0.0508 m | §3.9 |
| `LandingSlowdownParams.a` / `b` | （拟合） | 1.996467 / −1.6714 × 10⁻⁶ (u/s)⁻² | — / −2.591 × 10⁻³ (m/s)⁻² | §3.9 |
| `LandingSlowdownParams.duration` | `landSlowdownDuration` | 1 s | — | §3.9 |
| `LandingSlowdownParams.exponent` | `landSlowdownTimePower` | 2（×） | — | §3.9 |
| `lurchLamMax` | `jump_grace_strength` | 0.7（×） | — | §3.14 |
| `lurchFullEnd` | `jump_graceperiodmin` | 0.2 s | — | §3.14 |
| `lurchZero` | `jump_graceperiodmax` | 0.5 s | — | §3.14 |
| `lurchClampSprintFraction` | `jump_grace_max` | 0.7（×） | — | §3.14 |
| `lurchClamp`（回放电机） | — | 209.3 u/s | 5.316 m/s | §3.14 |
| `lurchCutoffSpeed` | `jump_grace_cutoff_speed` | 1100 u/s | 27.94 m/s | §3.14 |

注意 `b` 的单位是 (u/s)⁻²，换成米要**除以** 0.0254²（[01 §2.3](01-units-body.md)"长度在分母"的规则）。

---

## 本章缺口（详细在 `_notes/hb-ch03.md`）

1. **coyote time 没实测**，`jump_graceperiod` 0.2 的读取方没追；HSD 没有（§3.12，B03-1）。
2. **R5 有没有起跳缓冲没测**；HSD 没有，D-09 暂缓（§3.11，B03-2）。
3. **硬着陆降速有两种写法对不上**（Unity 实测拟合从 397 u 开始降，原生读法从 300 u）（§3.9，B03-3）。
4. 连跳惩罚的开关标志什么时候为真没读；Unity 每次地面跳都惩罚（§3.8）。
5. `AirMove` 本体（`airDrag` / `airFriction` 怎么取）没读，实测是 0（§3.6）。
6. 冲刺 × 1.25 对按键转向的影响只有代码（G-09）；斜后方、纯侧向能不能冲刺没单独测（§3.3）。
7. 蹲姿 138 u/s 以上的加速、下蹲过渡中的移动没测（§3.5）。
8. 原生摩擦里"0.5 s 淡入"的时刻 T 是什么没读（§3.4）。
9. lurch：按住一个键再按另一个不同的键（A 按住、按 S）只测了 W；手柄没测；M8 b1 有 11.6 u/s 的残差没解释（§3.14）。
