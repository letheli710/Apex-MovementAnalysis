# 04 滑铲、斜坡滑铲、翻越、蹲着翻越、superglide

由 hb-ch04 写（2026-11-14）。分支 `handbook/ch04`，还没合并。附件在 [04-slide-mantle/](04-slide-mantle/)：`slide_ref.py`（本章滑铲伪代码的独立实现，打印和 R5 实测对照的数）、`s27-curves.tsv`（S27 翻越加速的 8 条曲线）。

## 白话说明

这一章管三件事：

1. **滑铲**：冲刺中按下蹲，角色贴地滑出去，开头先被推快一下（"起滑加成"），之后慢慢变慢，慢到一定程度就变成蹲着走。滑铲中可以稍微转向、可以跳（"滑铲跳"），在坡上会被重力加速或减速。
2. **翻越（mantle）**：空中朝着一面墙按住前进，台沿够得着就自动翻上去；够不着就先往上爬一段墙（攀爬），爬到够得着再翻。蹲着翻越有自己的一套时长。
3. **superglide**：翻越快结束时按跳、再按蹲，角色带着滑铲的起滑加成从台沿上"飞"出去，速度比普通翻越快一半。还有一种从 Apex 后期赛季移植来的"翻越加速"（S27 mantle boost），只按跳，判定方式完全不同。

和别的章的分界：

- 每条命令的执行顺序、碰撞体、地面检测、台阶、**坡上的位置怎么走**（上坡步长、圆底）在第 02 章；本章只写滑铲在坡上的**速度**规则，用到坡上位置时指过去。
- 普通地面移动、蹲走的加速 / 摩擦、起跳（连跳惩罚、半步重力、+30 推墙）、空中加速、lurch 在第 03 章；本章只写滑铲跳和翻越跳里**不一样**的部分。
- 蹬墙跳（攀爬中按跳）、跑墙、挂墙在第 05 章；本章的攀爬只写到"爬上去翻越"为止。
- 滑铲和翻越的**镜头**（滑铲 FOV、滑铲倾斜、翻越俯仰曲线怎么叠加到镜头上）在第 07 章；本章写眼高过渡和翻越曲线本身的数（S27 判定要用）。

**读完能做出什么**：一个看不到 Unity 代码的工程师，照 §4.7 的逐命令伪代码和 §4.1–§4.6 的规则，加上第 02、03 章，能写出和 R5 逐命令一致的滑铲（附件 `slide_ref.py` 就是照本章写的，和 R5 实测对得上，见 §4.7 验收）；照 §4.9–§4.14 能写出翻越、蹲着翻越和两种 superglide。

**两个默认，先写清楚**（00-INVENTORY 04 章第 4 条）：

| 场合 | superglide 用哪套 | 出口 | 依据 |
|---|---|---|---|
| **游戏里**（练习场，菜单 "Mantle boost (B1, S27 port)" 默认开） | S27 翻越加速（§4.14），只按跳 | 388.7 / 367.42 u/s | D-20、D-32 |
| **配置本身、测试、回放、手感对照**（`MovementConfigs.Reference()` / `Fun()`） | 原生 superglide（§4.13），跳 + 蹲 | 460 / 289.82 u/s | D-32 |

两套互斥：S27 打开时拿不到 460（R5 实测也是这样）。

**本章出处缩写**（第一次出现时用；其余沿用 DESIGN-PHILOSOPHY §2.2）：

| 缩写 | 文件 |
|---|---|
| NS | `research/rea-native/subsystems/N2-S-SLIDE.md`（原生滑铲） |
| NG | `research/rea-native/subsystems/N2-G-GROUND.md`（原生地面，含滑铲摩擦） |
| NJ | `research/rea-native/subsystems/N2-J-JUMP-AIR.md`（原生起跳，含滑铲跳） |
| NM | `research/rea-native/subsystems/N2-M-TRAVERSAL.md`（原生翻越） |
| SM | `research/phase2-local/m2/slide/SLIDE-MODEL.md`（M2 滑铲实测） |
| SD1 | `research/phase2-local/m10/r_slide/SLIDE-D1-M10.md`（M10 松蹲、滑铲跳对滑铲时长） |
| N4C | `research/rea-native/n4/N4C-HOP-SLIDE.md`（冷却、转向实测） |
| R6 | `research/phase2-local/slope/SLOPE-SLIDE.md`（斜坡滑铲 133 次实测） |
| RPS | `research/phase2-local/rps/README.md`（回放电机滑铲改原生，D-47） |
| A2 | `research/phase2-local/m6/a2_climb/A2-CLIMB.md`（攀爬、翻越实测） |
| SG | `research/phase2-local/m8/r_sg/SG.md`（superglide 各高度实测） |
| D72 | `research/phase2-local/D72-REPORT.md`（蹲着翻越 610 次 + Frida 195 段） |
| B1 | `research/b1/B1-MANTLE-BOOST.md`（S27 翻越加速） |
| FEEL | `research/feel/FEEL.md`（R5 / Unity 叠图对照） |
| DIFF | `R5-DIFF-ARCHIVE.md` |
| U: | HSD-Unity 仓库；`U:…/` = `Assets/HSD/R5Replay/Runtime/` |

所有引用的文件都在研究仓库 main（`86ec5f1`）和 HSD-Unity main（`17260f2`）上，没有引用未合并的 PR。

---

## 4.0 记号和前提

- **命令**：一条 usercmd，Unity 里固定 1/120 s（第 02 章）。R5 每条命令按自己的帧时长 dt 走；本章所有规则都按 dt 写，和帧率无关。
- **now**：这条命令**开始**的时刻。"距离某事 t 秒"都用 now 减那件事所在命令的开始时刻。
- **pre / post**：命令执行前 / 后的状态。表里写的"速度"没注明就是水平速度 s = |v_h|（u/s）。
- **msc**：移动倍率（武器决定；空手 Gibraltar 1.15）。表里乘了 msc 的数会注明"× msc"，括号里给 msc = 1.15 的值。
- **dir**：水平速度方向 v_h / s。**wishvel**：前后轴 × 前向 + 左右轴 × 右向（第 03 章，原始轴，不归一化）。
- **按下 / 按住**：按下 = 这条命令新按下（上一条没按）；按住 = 这条命令按着。
- **ducked**（"蹲着"标志）= **上一条命令**按住了蹲。和冲刺标志一样晚一条命令（第 03 章）。
- 参考身高 H = 72 u（[01 §4.1](01-units-body.md)）。

---

## 4.1 起滑：条件和起滑加成

#### 原理

滑铲是"把冲刺的速度换成一段更快、但会慢慢衰减的贴地移动"。开头那一下加速（起滑加成）是滑铲的手感核心：按下蹲的那一瞬间角色明显一冲。为了不让玩家靠连续按蹲刷速度，加成有两条限制：**有上限**（起滑后最多 460 u/s，已经很快的不会更快），**有冷却**（2 s 内只给一次，而且冷却从"上一次开始滑铲"算，没拿到加成的滑铲也会刷新冷却）。这对应 DESIGN-PHILOSOPHY P3"动量是玩家的资产，只有明确规则才能收走 / 给予"和 P4"技巧窗口按时间算"。

另一个设计细节：起滑要求速度 ≥ 200 u/s，而走路上限是 173.5 × 1.15 = 199.525 u/s——**走路按蹲不能滑铲，必须冲刺**（或被别的东西推快）。

#### 规则和公式

1. **触发**：着地、不在滑铲中、这条命令**按下**蹲，并且：
   - pre 水平速度 s ≥ `slideRequiredStartSpeed`（不乘 msc）；
   - 地面法线 n_z > 0.7（坡度 < 约 45.6°，能站的坡都行）[反编译]；
   - 原生另有两条，Unity 没做：视角前向和速度方向的点积 ≥ `slide_max_angle_dot`；下蹲比例 < `slide_max_duck_frac_to_start`。**两个值都没读出来**（见 `_notes` 待研究）。
2. **加成**（在这条命令的移动**之前**加上）：距离上一次**开始滑铲**（任何一种开始：按蹲、落地续滑、换地面重新开始、superglide 的蹲，§4.4）≥ `slideBoostRearm` 才给：

   s_peak = min(s + `slideSpeedBoost` × msc, `slideSpeedBoostCap` × msc)

   记下 lastBoost = s_peak − s（滑铲早跳退还用，§4.6）、boostTime = now。方向不变。
3. 不管有没有加成：sliding = true；slideStartTime = now（刷新冷却）；记"下蹲过渡开始" = **下一条命令**的开始（now + dt，§4.6 退还用）；冲刺标志清掉。这条命令接着按滑铲走一次（§4.2），所以它的 post 已经衰减了一点（R5：pre 460.000、post 458.17–458.20）。
4. 原生的"空中起滑"（`slide_whileInAir`）默认关；空中只能靠落地续滑（§4.4）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 起滑最低速度 `slideRequiredStartSpeed` | 5.08 m/s | 200 u/s | 2.778 H/s | 必须高于走路 199.525 | [数据]（M2 入口 248 / 299 / 350 都能滑，200 本身没测） |
| 起滑加成 `slideSpeedBoost` × msc | 4.381 m/s | 150 × 1.15 = 172.5 u/s | 2.396 H/s | 实测只证明 ≥ 161 | [数据] [实测]（N4C 横向滑铲 255 → 427.5 是加法分支） |
| 加成上限 `slideSpeedBoostCap` × msc | 11.68 m/s | 400 × 1.15 = 460 u/s | 6.389 H/s | 实测 460.000，spread 0 | [数据] [实测] |
| 冲刺起滑的加成量（299 → 460） | 4.089 m/s | 161 u/s | 2.236 H/s | — | [实测]（15 / 15） |
| 冷却 `slideBoostRearm` | — | 2.0 s | — | 实测区间 (1.59, 2.09) s | [反编译] `player_slideBoostCooldown` 2 s；[实测] N4C 0 / 1.0 / 2.5 s 三次只有第一次加成 |
| 起滑地面法线下限 | — | n_z > 0.7（×） | — | — | [反编译] |

**和 HSD 旧版的差别**（都已改成 R5，D-17）：冷却以前是"距离上一次**加成** 1.8 s"，按那条规则 0 / 1.0 / 2.5 s 的第三次会有加成，R5 没有。旧值留在 `slideBoostCooldownFromStart = false`。

#### 实现模板

```
// 单位：u、s。在这条命令的地面移动之前
if grounded and not sliding and duckPressed and s >= slideRequiredStartSpeed and groundNormal.z > 0.7:
    if now - slideStartTime >= slideBoostRearm:            // slideStartTime 初值 = -∞
        peak      = min(s + slideSpeedBoost*msc, slideSpeedBoostCap*msc)
        lastBoost = peak - s
        boostTime = now
        s = peak;  v_h = dir * s
        boosted = true
    else:
        boosted = false
    sliding = true
    slideStartTime      = now
    duckTransitionStart = now + dt        // 下蹲过渡从下一条命令算
    sprinting = false
```

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.Move` 里"slide start (duck press, before the move)"一段，`R5MotorV2.SlideBoostPeak`。开关在 `R5MotorV2Params`：`slideBoostRearm` 2.0、`slideBoostCooldownFromStart` true、`slideDuckTransitionFromNextCommand` true（都是 `[NonSerialized]`，Reference 和回放电机都开；`LegacyM2()` 关回 M2 规则）。Unity 没检查 n_z > 0.7（坡 > 45.6° 本来站不住，第 02 章）。

#### 验收

- `R5MotorV2FormulaTests.SlideBoostCapAndGain`：299 → 460，lastBoost 161。
- `N7NativeReferenceTests.SlideBoostCooldownCountsFromTheLastSlideStart`：0 / 1.0 / 2.5 s 三次起滑，只有第一次 460，其余 299。
- `SlideM10DTests.ASecondSlideBeforeTheRearmGetsNoBoostAndItsJumpsKeepTheSpeed`。
- 对照数据：SM §2（15 次，peak 460.000，gain 161.000）、N4C §2（5 + 5 次）。
- 合格线：peak 和 min(s + 172.5, 460) 差 < 0.01 u/s；冷却按"上次开始"算，0 / 1.0 / 2.5 s 序列的加成次数 = 1。

#### 出处

- NS §1、§5 S-01 / S-02：触发条件、加成公式、冷却从上次开始算。main
- SM §2：起滑在按蹲那条命令的移动前，460 = 400 × 1.15。main
- N4C §2：冷却实测。main
- `research/phase2-local/static-values/STATIC-VALUES.md`：`slideRequiredStartSpeed` 200 等 census 值。main
- D-17（N7 改原生）、D-47（回放电机也改原生）；DIFF "RPS" 节。main
- [反编译] `Slide_TryBegin` 0x140a54890（调用者只有 `Duck` 两处和 `SetGroundEntity`）；加成的额外检查 0x140ac1d70 没读；"待退还"标志 player+0x2d76、加成量 +0x2d7c。

---

## 4.2 滑铲中的速度：衰减和转向

#### 原理

滑铲的速度按"一点固定的减速 + 按比例的衰减"往下掉：速度高时掉得快（比例部分大），速度低时主要靠固定减速。玩家感觉到的是"开头一冲，之后像在冰上慢慢停"。按住前进键**不会**让滑铲变快——滑铲中输入里和速度同方向的那部分被扔掉，只剩侧向的部分，所以滑铲只能**转向**，转得也很慢（1 s 大约转 10°）。这保证滑铲是"用掉"速度的动作，不能边滑边加速（坡除外，§4.5）。

#### 规则和公式

每条着地的滑铲命令（不是跳、不是被别的东西接管）：

1. **斜坡项**（§4.5）：地面倾斜时先加 g · n_z · n_h · dt。平地没有。
2. **摩擦**（先减后衰减）：

   s′ = max(0, (s − D · dt) · `slideVelocityDecay`^dt)

   D = `slideDecel`（按住蹲），松开蹲时 D = `slideWantToStopDecel`（§4.3）。D **不乘** msc。
3. **转向**（有移动输入时）：取 wishvel 里垂直于 dir 的部分 p；新方向 = normalize(dir · s′ + p̂ · a · dt)，a = `slideAccel` × msc；**速度大小不变**，只改方向。没有侧向输入（比如只按 W）时 p = 0，方向不变。
4. v_h = dir · s′；竖直速度 0；位置按第 02 章的地面移动走（平地 pos += v · dt）。
5. 然后检查结束（§4.3）。

步骤顺序有关系：先减后衰减和"先衰减后减"每条命令差 ≤ 0.002 u/s，一次滑铲累计约 0.5 u/s；精确的常微分形式 s′ = (s + D/k)·e^(−k·dt) − D/k（k = −ln 0.7 = 0.3567 /s）也可以，和帧率完全无关（SM §3.2）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 滑铲减速 `slideDecel`（按住蹲） | 2.54 m/s² | 100 u/s² | 1.389 H/s² | 拟合 99.61（99.01–100.06） | [数据] [实测] |
| 滑铲衰减 `slideVelocityDecay` | — | 0.7（每秒比例 ×/s） | — | 拟合 0.7001（0.6989–0.7010） | [数据] [实测] |
| 转向加速 `slideAccel` × msc | 1.46 m/s² | 50 × 1.15 = 57.5 u/s² | 0.799 H/s² | 实测横向增长 41.1 u/s² | [反编译] [实测] N4C §3 |
| 一次冲刺滑铲的时长（460 → 125，按住蹲） | — | 1.693 s（1.6923–1.6935） | — | 连续公式 1.689 s | [实测] SM §4 |

为什么实测横向增长是 41.1 而不是 57.5：转向后速度大小被压回原值，加上衰减，一部分侧向增量被吃掉；逐命令照上面 3 步算，和 R5 的误差 rms 0.001 u/s（N4C §3）。

原生还有两处 Unity 没做、平地上不起作用的项（[推断]，见 `_notes` 待研究）：衰减指数里有一个 (1 − 0.75·x) 的系数，x 来自一个查询函数，平地上推测为 0；某个标志（player+0x1dfc）为真时滑铲减速为 0。

#### 实现模板

```
// 单位：u、s
D = duckHeld ? slideDecel : slideWantToStopDecel
s = max(0, (s - D*dt) * pow(slideVelocityDecay, dt))
if hasMoveInput:
    along = dot2(wishvel, dir)
    p     = wishvel_h - along*dir                 // 垂直于速度的输入
    if |p| > 1e-9 and s > 1e-9:
        w   = dir*s + normalize(p) * (slideAccel*msc*dt)
        dir = normalize(w)
v_h = dir * s
```

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.SlideSpeedStep`、`R5MotorV2.SlideSteer`（`slideSteerAccel` 50）。

#### 验收

- `R5MotorV2FormulaTests.SlideDecayEndAndCrouchOverspeed`：460 按住蹲滑到 < 125 的命令数和 R5 一样。
- `N7NativeReferenceTests.SlideSteeringMatchesTheN4CLateralGrowth`：只按 D 1 s，横向速度约 41 u/s。
- 附件 `04-slide-mantle/slide_ref.py`：144 fps 从 299 起滑，第 243 条命令后 < 125（R5 244 条，1.6928 s；差一条来自 R5 的帧时长抖动）。
- 合格线：逐命令速度和 (s − 100·dt)·0.7^dt 差 < 0.01 u/s；1 s 侧向转向的横向速度 41 ± 1 u/s。

#### 出处

- NG §2.1（滑铲中去掉沿速度的意图）、§2.2（滑铲加速 = `slideAccel` × msc）、§2.3（摩擦和 `slideVelocityDecay`，x 系数）、§2.4（减速选择，0x1dfc 标志）。main
- SM §3（衰减律和步骤顺序的拟合）。main
- N4C §3（转向实测 41.1，原生公式逐命令 rms 0.001）。main
- [反编译] `Friction` 0x140a4a280；`Ground_GetAccel` 0x140a36450；`Ground_GetDecel` 0x140a36580；x 的查询函数 0x140abdc20。

---

## 4.3 滑铲结束和之后的蹲走

#### 原理

滑铲有两种"正常结束"：一直按着蹲，滑到很慢（125 u/s）自然变成蹲走；中途松开蹲，表示"我不想滑了"，但**高速时不立刻停**，而是用更强的减速刹到 350 u/s 以下再结束——这样高速滑铲中松蹲不会一下子丢掉大量速度，也不会还能一直滑。结束后如果还按着蹲，就是蹲走（上限 92 u/s），比站着走慢得多。

#### 规则和公式

1. **按住蹲，滑到慢**：这条命令的 post 速度 < `slideStopSpeed` → 滑铲在这条命令**之后**结束（这条命令本身按滑铲走完）。
2. **松开蹲**（这条命令没按蹲，仍在滑铲）：
   - pre 速度 ≤ `slideMaxStopSpeed` → 滑铲在这条命令**之前**结束，这条命令按**蹲走**处理（"蹲着"标志强制为真，用蹲走的减速 1500）；
   - pre 速度 > 350 → 继续滑，但减速改成 `slideWantToStopDecel`：s′ = (s − 400·dt)·0.7^dt。坡面项照样有（§4.5）。
3. **其他结束**：起跳（滑铲跳，§4.6）；走下台边离地（第 02 章：脚下 > 2 u 没有地面）；跳板 / 技能发射；翻越、攀爬、滑索等运动学动作接管。R5 原生还有：上滑索、近战冲刺、墙跑中。
4. **之后的蹲走**（不在滑铲、"蹲着"）：上限 `crouchSpeed` × msc = 92；高于上限按 `crouchDeceleration` 1500 u/s² 减到 92（不乘 msc）；蹲走的其余规则在第 03 章。按住 W：变成 92 的蹲走；什么都不按：减到 0 停住。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 结束速度 `slideStopSpeed`（按住蹲） | 3.175 m/s | 125 u/s | 1.736 H/s | 实测结束前 post 124.42–124.91 | [数据] [实测] |
| 松蹲结束速度 `slideMaxStopSpeed` | 8.89 m/s | 350 u/s | 4.861 H/s | 实测结束后约 335–336（= 结束那条蹲走命令再减 12.5） | [数据] [实测] SD1 |
| 松蹲后的滑铲减速 `slideWantToStopDecel` | 10.16 m/s² | 400 u/s² | 5.556 H/s² | 实测合减速 620–670 u/s²（含衰减） | [数据] [实测] SD1 |
| 蹲走上限 `crouchSpeed` × msc | 2.337 m/s | 80 × 1.15 = 92 u/s | 1.278 H/s | 实测 92.0 | [实测] |
| 蹲着超速减速 `crouchDeceleration` | 38.1 m/s² | 1500 u/s² | 20.83 H/s² | 拟合 1499.55（spread 0.04 %） | [实测] SM §4 |

两处旧文档的数现在解释得通（[推断]，见 `_notes`）：

- NS 的 S-05 写"按住蹲结束速度 R5 112，代码 125"：112 是滑铲结束**后第一条蹲走命令**的 post（124.75 − 1500/120 = 112.25），不是滑铲的结束速度。
- NS 的 S-04 写"松蹲后约 335 结束（≤ 350）"：同理，结束那条命令按蹲走减了 1500·dt。
- NS 写"D = 100 要按住蹲**且向前**"：R6 实测松开 W 和冲刺键、按住蹲，减速不变，"且向前"不成立（00-INVENTORY 过时表）。

#### 实现模板

```
// 单位：u、s。着地、不是跳的命令
releasing = sliding and not duckHeld
if releasing and s <= slideMaxStopSpeed:
    sliding = false
    ducked  = true                 // 这条命令按蹲走：上限 92，减速 1500
if sliding:
    ... §4.2（D = releasing ? 400 : 100）...
    if s < slideStopSpeed: sliding = false      // 这条命令已按滑铲走完
else:
    groundMove(ducked ? crouch : ...)           // 第 03 章
```

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.Move` 里 `releasing` 一段（开关 `slideReleaseEnds` true，值 `slideWantToStopDecel` 400、`slideMaxStopSpeed` 350）；走下台边结束滑铲在 `U:…/World/MovementWorld.cs` `MovementWorld.BeforeStep`。

#### 验收

- `SlideM10DTests.CrouchReleaseEndsTheSlideAtOrBelow350WithTheStrongerDecel`（松蹲时滑铲时长 0.10 / 0.25 / 0.50 / 1.00 s）。
- `R5MotorV2FormulaTests.SlideDecayEndAndCrouchOverspeed`（< 125 结束、之后 1500 减到 92）。
- 附件 `slide_ref.py`（120 fps）：松蹲于 0.10 s（434）→ 19 条命令后结束、post 336.3；0.25 s（397）→ 11 条后、335.6；0.50 / 1.00 s → 松开那条命令就结束。R5（SD1）：19 条 / 336、11 条 / 335、当条、当条。
- RPS：M3 两个 `e8_slide_chain` 录像（最后在约 132 u/s 时松蹲），速度误差 rms 7.48 → 0.15 u/s，事件时刻误差 12 → 0 条命令。
- 合格线：松蹲结束的命令和 R5 差 ≤ 1 条；结束后速度差 < 1 u/s。

#### 出处

- NS §4（三种结束，`WalkMove` / `Duck`）、§5 S-04 / S-05。main（S-05 的解释见本节，[推断]）
- SD1 TL;DR 第 1 行（松蹲实测 19 次）。main
- SM §4（125 结束、1500 蹲走减速、92）。main
- R6 结论 3（松开 W 不改减速）。main
- RPS（`slideReleaseEnds` 换进回放电机）、D-47。main
- [反编译] `WalkMove` 0x140a4a7c0（按住蹲的结束）；`Duck` 0x140a54080（松蹲的结束和其他结束）。

---

## 4.4 再次加速的规则：冷却、落地续滑、换地面重新起滑

#### 原理

滑铲加成是一种"每 2 s 一次"的资源。几种看起来是"新滑铲"的情况，规则统一成一句话：**每一次"开始滑铲"都刷新 2 s 冷却，只有冷却到了的那一次才给加成**。

- 滑铲跳落地时还按着蹲，角色**直接接着滑**，不丢速度（这是连续滑铲跳的基础），但这次续滑**不给加成**，而且算一次"开始"，会刷新冷却。
- 滑过两个不同物体的接缝时，原生代码会再走一次"开始滑铲"（这是 Apex 的一个隐藏机制）。2 s 冷却到了就再加一次速。
- superglide 用的也是这个加成（§4.13），所以刚滑过铲就做不出 superglide。

#### 规则和公式

1. **冷却**：见 §4.1，`slideBoostRearm` 2.0 s，从 slideStartTime（上一次任何"开始滑铲"）算。
2. **落地续滑**：空中命令结束时落地（第 03 章：竖直速度 < 0 且脚下 ≤ 2 u），如果这条命令按住蹲且水平速度 ≥ 200：
   - sliding = true，**不给加成**（boosted = false），不丢速度（落地减速对滑铲不起作用，SM §5.3）；
   - slideStartTime = 落地这条命令的 now（刷新冷却）；
   - 不重设"下蹲过渡开始"（滑铲跳退还只给按蹲开始、有加成的滑铲，§4.6）。
3. **换地面实体重新起滑**（R6U U-3）：着地、在滑铲中、按住蹲、上一条命令也着地、这条命令脚下的**地面实体**和上一条不同、s ≥ 200：
   - 距 slideStartTime ≥ 2 s 且 min(s + 172.5, 460) > s → 加成，boosted = true，lastBoost / boostTime 更新；
   - 超过 460 时**不降速**（R5 dn25 底部约 490 u/s 跨接缝速度不变）；
   - 不管加不加，slideStartTime = now；不重设"下蹲过渡开始"；没加成时 boosted 保持原值（没实测）。
   - **什么算一个地面实体**：Apex 的地形和关卡静态几何是同一个实体，只有道具单独算。HSD 照这个做（`SlideRebegin.Props`，默认）：静态关卡几何共用一个 id，跳板、平台、可动物体各自一个 id。另两档：`Off`（不重新起滑，旧版）、`EverySolid`（每个方块一个，关卡拼缝处都会触发）。
   - 落地不算"换实体"（原生 `SetGroundEntity` 落地也会调，但 Unity 没做，保守写法，没实测）。
4. **superglide 的蹲**算一次"开始滑铲"，刷新冷却（§4.13）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冷却 `slideBoostRearm` | — | 2.0 s | — | (1.59, 2.09) | [反编译] [实测] |
| 落地续滑最低速度（= `slideRequiredStartSpeed`） | 5.08 m/s | 200 u/s | 2.778 H/s | — | [实测] SM §5.3 |
| 实测重新起滑的时刻（距滑铲开始） | — | 2.10–3.49 s | — | Unity 2.09–3.45 s | [实测] R6 |
| 实测重新起滑的速度 | — | 398 → 461、301 → 461、255 → 428 | — | — | [实测] R6 |

#### 实现模板

```
// 单位：u、s
// (a) 每条命令开头，起滑判断之前
if groundEntityRebegin != Off and grounded and sliding and duckHeld and prevCommandGrounded
   and groundKey(now) != groundKey(prev) and s >= slideRequiredStartSpeed:
    peak = min(s + slideSpeedBoost*msc, slideSpeedBoostCap*msc)
    if now - slideStartTime >= slideBoostRearm and peak > s:
        lastBoost = peak - s; boostTime = now; s = peak; v_h = dir*s; boosted = true
    slideStartTime = now
// (b) 落地检查（空中命令末尾，第 03 章）
if landed and duckHeld and |v_h| >= slideRequiredStartSpeed:
    sliding = true; boosted = false; slideStartTime = now
```

groundKey：`Props` 档 = 地面实体 id（静态几何 0、道具各自 id）；`EverySolid` 档 = 每个方块的 id。

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.RebeginSlide`、`R5MotorV2.GroundKey`、`R5MotorV2.CheckLanding`；开关 `R5MotorV2Params.slideRebeginOnGroundChange`（`SlideRebegin`，Reference = `Props`，Fun 和回放电机 = `Off`）；游戏菜单 "Slide re-boost on a new ground"（PlayerPrefs `hsd.r6u.sliderebegin`）。地面实体 id 来自 `MovementWorld`（`ConvexSolid.prop`）。

#### 验收

- `R5MotorV2FormulaTests.LandingWithDuckHeldResumesSlideWithoutBoost`。
- `R6USlopeTests.GroundEntityChangeRebeginsTheSlide`（三档）、`R6USlopeTests.RebeginNeverSlowsAFastSlide`。
- `D1M9CTests.TheSlideBoostClockGatesTheSuperglide`、`D1M9CTests.ASlideJumpApproachGivesNoSuperglide`（冷却挡住 superglide，§4.13）。
- 对照：R6 二次加成表（dn15 3.14 s、dn20 2.66 s、v20 2.64 s、crest 3.44–3.49 s、横向 2.12 s），Unity 改后 3.12–3.13 / 2.64–2.65 / 2.63–2.64 / 3.40–3.45 / 2.09–2.11 s。
- 合格线：二次加成时刻和 R5 差 ≤ 0.05 s，速度差 ≤ 2 u/s；2 s 内跨接缝不加速。

#### 出处

- R6 结论 5、"二次加成"表、"原生代码"节（`SetGroundEntity` 调 `Slide_TryBegin`，下蹲状态 ∈ {1, 2}）。main
- DIFF "R6U" 节 U-3 和末段"U-3 里没测到、按保守写的"。main
- SM §5.3（落地续滑无加成、无速度损失）。main
- `research/phase2-local/m9/r_d1/D1.md`（滑铲后 superglide 0 / 5：加成没恢复）。main
- D-46（U-3 三档，默认 R5）。main
- [反编译] `SetGroundEntity` 0x140a51650（下蹲状态 player+0x2a70 ∈ {1, 2} 时调 `Slide_TryBegin`，第三个参数 = "之前在空中"）。

---

## 4.5 斜坡滑铲（5–40° 的原生规律）

#### 原理

坡上的滑铲只多一条规则：**重力沿坡面的分量加到水平速度上**。下坡越滑越快，直到和摩擦平衡；上坡很快减速，减到 125 就结束，**不会倒滑**（滑铲结束后速度归零或变成蹲走）。规则没有坡度门槛（5° 的缓坡也有），也不看是否按着蹲。所以坡是关卡里"给滑铲续命"的工具：15° 以上的下坡能让滑铲一直维持，20° 下坡会稳定在约 395 u/s。

这一条只管速度。坡上的位置怎么走（上坡每步走多远、碰撞体底部是圆的）在第 02 章。

#### 规则和公式

1. **坡面项**：滑铲中、着地、地面法线 n 不是正上（n_z < 1 − 10⁻⁶，没有坡度门槛）时，每条命令在摩擦**之前**：

   v_h += g · n_z · n_h · dt

   n_h = (n_x, n_y) 是法线的水平分量，指向下坡，|n_h| = sinθ，n_z = cosθ。所以沿下坡的额外加速度 = g·sinθ·cosθ（g = 750 u/s²）。加完以后方向跟着速度走（横着滑会慢慢转向下坡）。
2. 摩擦、转向、结束照 §4.2 / §4.3 不变：按住蹲 D = 100，松开蹲 D = 400（坡面项照样有）。
3. **平衡速度**（下坡、按住蹲、直着滑）：v_eq = (g·sinθ·cosθ − 100) / k，k = −ln 0.7 = 0.3567 /s。v_eq < 125 的坡（≤ 约 11°）滑铲最终会结束。
4. **上坡**：同一个公式，坡面项为负。减到 125 结束。结束后按住 W 变 92 的蹲走继续上坡，不按就原地停住（速度 0）。
5. **坡度变化处**（平地 ↔ 坡、V 形、坡顶）：测过的转折都不离地、滑铲不中断（离地命令 0 / 133 次试验）。贴坡的规则在第 02 章（`StayOnGround`：脚下 ≤ 18 u 的坡面会把身体压回坡上）。
6. 冲刺在坡上不受影响（上下坡都是 299）。
7. **原生的离散方式**：原生把坡面项分成两个半步（移动前、移动后各 ½·dt），和重力半步放在一起；Unity 在摩擦前一次加满 dt。两者逐命令和 R5 的残差都 ≤ 0.19 u/s（Unity ≤ 0.005），可以任选。

| 坡度 θ | 额外加速度 g·sinθ·cosθ [u/s²] | [m/s²] | 平衡速度 v_eq [u/s] | R5 实测额外加速度 | 依据 |
|---|---|---|---|---|---|
| 5° | 65.1 | 1.654 | 无（< 125，坡上 2.27 s 后结束） | 65.1 | [反编译] [实测] |
| 10° | 128.3 | 3.259 | 79（< 125，会结束） | 128.2 | [实测] |
| 15° | 187.5 | 4.763 | 245 | 186.9 | [实测] |
| 20° | 241.0 | 6.121 | 395（实测停在 398） | 240.6 | [实测] |
| 25° | 287.3 | 7.297 | 525 | 286.9 | [实测] |
| 30° | 324.8 | 8.250 | 630 | 324.4 | [实测] |
| 40° | 369.3 | 9.380 | 755 | 367.8（上坡） | [实测] |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力 g（`sv_gravity` × `gravityScale`） | 19.05 m/s² | 750 u/s² | 10.42 H/s² | — | [数据] |
| 坡面项倍率 `slideSlopeGravityScale` | — | 1（×） | — | — | [反编译] |
| 实测坡度范围 | — | 5–40° | — | > 40° 没测；> 45.6° 站不住 | [实测] |

上坡实测（R5，坡脚约 400 u/s 冲上去）：10 / 20 / 30 / 40° 坡上滑 0.87 / 0.64 / 0.53 / 0.49 s，沿坡上行 222 / 165 / 136 / 124 u。

**作废的旧结论**：M8 的拟合"额外加速度 147 + 342·sinθ"只在 29–41° 成立，5° 时给 177（实际 65），作废（00-INVENTORY 过时表）。M9 D1 的"30° 上坡额外 −322 u/s²"和原生公式一致（−324.8）。

**HSD 的设计版（只在 Fun）**：Fun 配置有一个 HSD 自己的斜坡滑铲（`SlopeSlideParams`，按下降高度记能量、下坡少摩擦），是 [设计]，不是 R5；用户把它列为暂缓的设计问题（DEFERRED E2，Fun 1.6 倍）。Reference 不用它（`HsdMovementParams.Off()`）。

#### 实现模板

```
// 单位：u、s。§4.2 摩擦之前
n = groundNormal            // 单位向量，向上
if sliding and grounded and n.z < 1 - 1e-6:
    a = g * slideSlopeGravityScale * n.z * dt
    v_h += a * (n.x, n.y)
    s = |v_h|; dir = v_h / s
```

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.Move` 里 `slopeTerm` 一段；开关（Reference 打开，Fun 和回放电机关）：`slopeMovement` true、`slideSlopeAnyGrade` true（U-4，没有门槛）、`slideSlopeNeedsDuck` false（U-5）。坡上位置：`R5MotorV2.SlopeGroundMove`（U-1 `slopeUphillKeepStep`）和 `MovementWorld` 的圆底（U-2 `hullBottomRadius` 16），第 02 章。

#### 验收

- `R6USlopeTests.SlideSlopeTermOnAGentleSlope`（5° 也有坡面项）、`R6USlopeTests.ReferenceHasTheR5SlopeRulesAndFunAndTheReplayMotorKeepTheOldOnes`、`R6USlopeTests.UphillStepAndRestHeight`。
- `SlideM10DTests.TheReleaseOnASlopeKeepsTheSlopeTermNextToTheStrongerDecel`。
- `SlopeSlideTests.ReferenceSlopeSlideMatchesTheR5FitWhereItWasMeasured`（30 / 35 / 40°）。
- 对照：R6 的 133 次试验（逐命令残差、上坡距离、转折、横向；harness 在 `research/phase2-local/slope/harness/`）。改后上坡距离 223.0 / 166.2 / 137.3 / 124.8 u（R5 222.3 / 165.3 / 136.2 / 123.6）。
- 合格线：逐命令额外加速度和 750·sinθ·cosθ 差 < 1 u/s²；上坡滑行距离和 R5 差 < 2 u；转折处离地命令 0。

#### 出处

- R6 结论 1–7、"逐命令公式"表、"上坡"表、"坡度变化处"表、"原生代码"节。main
- DIFF "R6U" 节（U-1 – U-5 旧版 / R5 / 现在）。main
- `research/phase2-local/m9/r_d1/D1.md`（30° 上坡）。main
- D-45、D-46。main
- `DEFERRED-DESIGN-TODO.md` E2（HSD 斜坡滑铲设计）。main
- [反编译] `Gravity_HalfStep` 0x140a36130（滑铲标志 player+0x2d75、地面实体有效 +0x324 时，水平速度 += 半步 g·dt·n_x·n_z / n_y·n_z；法线在 +0x43dc – +0x43e4）。

---

## 4.6 滑铲跳

#### 原理

滑铲中起跳是保持速度的主要方法，但为了不让"按蹲马上跳"白拿加成，有两条规则：

1. **刚起滑就跳，加成要还回去**：起滑后约 0.2 s 内（下蹲动作还没做完）跳，水平速度减掉这次的加成量（冲刺起滑是 161）。所以"按蹲—立刻跳"不比直接冲刺跳快。
2. **晚一点跳，速度会被抬一下**：起跳时速度在 297.5–350 之间，抬到 350。这让"滑一会儿再跳"有一个稳定的出口速度。更快的（> 350）保持，更慢的（< 297.5）也保持。

滑铲跳比普通跳矮（50 u 对 56 u），配合空中松开蹲时脚往下伸（§4.8），落地很快又能接着滑。

#### 规则和公式

着地、在滑铲中、这条命令按下跳：

1. **水平速度**（只对**按蹲开始、有加成**的滑铲，即 boosted = true；落地续滑的、没拿到加成的滑铲保持原速）：
   1. 退还：now − boostTime < `slideBoostRefundWindow` **并且** now − 下蹲过渡开始 < `slideDuckTransitionTime`（下蹲过渡从起滑的**下一条**命令开始算，§4.1）→ s ← max(0, s − lastBoost)。实际起作用的是后一条（约 0.2 s）。
   2. 然后抬高：0.85 × `slideMaxJumpSpeed` < s < `slideMaxJumpSpeed` → s ← 350。退还后的速度一般 < 297.5，不会再被抬。
   3. 方向不变。每次滑铲最多处理一次。
2. **起跳高度** `slideJumpHeight`，连跳惩罚照第 03 章（frac）。竖直速度 V = √(2·g·50·frac)，半步重力顺序和普通跳一样（第 03 章，起跳那条命令一共扣 1.5·g·dt）。
3. 滑铲跳**不用**普通跳的"超速削减"（`skip_speed_reduce`，第 03 章）；+30 推墙（J-1）照普通跳。
4. 起跳后滑铲结束；空中可以照常 lurch（第 03 章，滑铲跳是起跳命令，打开 lurch 窗口）。
5. 空中松开蹲：碰撞体站起来、脚往下伸 16.5 u（§4.8）。落地时还按着蹲 → 接着滑（§4.4），不给加成。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 滑铲跳高度 `slideJumpHeight` | 1.270 m | 50 u | 0.694 H | 拟合 50.37（下蹲没完成）/ 49.90 | [数据] [实测] |
| 滑铲跳竖直速度 V（frac = 1） | 6.956 m/s | 273.86 u/s | 3.804 H/s | — | [算] |
| 退还窗口 `slideBoostRefundWindow` | — | 0.4 s | — | 实测边界在 (0.201, 0.597]；被下一条盖过 | [反编译] |
| 下蹲过渡 `slideDuckTransitionTime`（滑铲时） | — | 0.2 s（从起滑后下一条命令算） | — | R5 0.201 s 退、0.215 s 不退（144 fps） | [反编译] [实测] |
| 抬高目标 `slideMaxJumpSpeed` | 8.89 m/s | 350 u/s | 4.861 H/s | 实测 350.000–350.005 | [数据] [实测] |
| 抬高下限 `slideJumpFloorLowFrac` × 350 | 7.556 m/s | 0.85 × 350 = 297.5 u/s | 4.132 H/s | — | [反编译] [实测] |
| 冲刺起滑的退还量 | 4.089 m/s | 161 u/s | 2.236 H/s | 实测 160.992 | [实测] |

R5 实测（冲刺起滑、按住蹲，起跳前 → 起跳后水平速度）：

| 起滑后多久跳 | R5 | 本章规则（`slide_ref.py`） | 哪条规则 |
|---|---|---|---|
| 0.10 s（120 fps） | 434 → 273 | 434.1 → 273.1 | 退还 |
| 0.201 s（144 fps） | 408.76 → 247.77 | 408.71 → 247.71 | 退还 |
| 0.25 s | 397 → 397 | 396.9 → 396.9 | 过渡已完成，> 350 保持 |
| 0.40 s | 361.5 → 361.5 | 361.6 → 361.6 | > 350 保持 |
| 0.597 s（144 fps） | 318.15 → 350.005 | 318.02 → 350.00 | 抬到 350 |
| 0.60 s | 317 → 350.0 | 317.4 → 350.0 | 抬到 350 |
| 1.0 s | 236 → 236 | 238.0 → 238.0 | < 297.5 保持 |
| 落地续滑后再跳 | 250 → 250、188 → 188 | 保持 | 没有加成，不处理 |

（R5 的起跳后速度比表里的规则多 +0.005–0.008 u/s，是起跳那条命令的空中加速。）

**旧规则**（M2 的 H1：退还窗口只看 0.4 s，窗口外一律 max(s, 350)）和 M10-D1 的"0.8 s 窗口"都被原生规则取代，留在 `LegacyM2()` / `slideMaxJumpSpeedWindow`（D-47）。

#### 实现模板

```
// 单位：u、s。着地、jumpPressed、sliding
frac = multiJumpFrac(now - lastLandTime)          // 第 03 章
if boosted:
    if now - boostTime < slideBoostRefundWindow and now - duckTransitionStart < slideDuckTransitionTime:
        s = max(0, s - lastBoost)
    if slideJumpFloorLowFrac*slideMaxJumpSpeed < s < slideMaxJumpSpeed:
        s = slideMaxJumpSpeed
v_h = dir * s
sliding = false; boosted = false
V = sqrt(2 * g * slideJumpHeight * frac)
jumpCommand(V)                                    // 第 03 章：半步重力、+30 推墙、空中加速、移动
```

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.JumpCommand`（`sliding` 分支）、`R5MotorV2.SlideJumpSpeed`（5 参数版）；开关 `slideRefundNeedsDuckTransition` true、`slideJumpFloorLowFrac` 0.85、`slideJumpFloorOnlyAfterBoost` true、`slideDuckTransitionFromNextCommand` true。

#### 验收

- `N7NativeReferenceTests.SlideJumpFloorIsTheNativeSpeedBandAndTheRefundNeedsTheDuckTransition`、`N7NativeReferenceTests.OldSlidesInsideTheBandAreLiftedAndTheRefundEndsWithTheDuckTransition`。
- `SlideM10DTests.SlideJumpExitFollowsTheMeasuredAgeTable`（上表 M10 那几行）。
- `R5MotorV2FormulaTests.SlideJumpEarlyRefundsLateRaisesTo350`。
- `BunnyHopTests.SlideHopsKeepAnySpeedAndOnlyALateJumpPaysTheSlideFriction`、`BunnyHopTests.SlideJumpToHopToLandingSlideChainKeepsAndCapsTheSpeed`（在 `R5MotorM8BTests.cs`）。
- 附件 `slide_ref.py` 打印上表"本章规则"一列。
- 合格线：上表每一行起跳后水平速度和 R5 差 < 1 u/s（1.0 s 那行 R5 帧时长抖动大，< 3 u/s）；退还的边界在起滑后 0.201 / 0.215 s（144 fps）之间。
- 已知差别：R6 在坡道上看到滑铲跳起跳后水平速度 R5 258.x、Unity 260.3（平地也一样，+2 u/s），原因没查（见 `_notes` 待研究）。

#### 出处

- NJ §1.2、§5 J-07 / J-08：退还要求下蹲没完成且 0.4 s 内，然后 297.5–350 抬到 350。main
- SM §5（退还 161、抬到 350、H 50.37 / 49.90、落地续滑）。main
- SD1（滑铲时长 0.10 – 1.0 s 的滑铲跳表、续滑的跳保持速度）。main
- D-26（下蹲过渡从下一条命令算：0.201 退 / 0.215 不退）、D-17、D-47。main
- R6 "修改建议"表下面一段（258 对 260.3）。main
- [反编译] `Jump` 0x140a3b550（滑铲跳分支）；"待退还"标志 player+0x2d76、加成量 +0x2d7c；下蹲状态 +0x2a70。

---

## 4.7 滑铲逐命令伪代码（完整，重建检验用）

#### 原理

前面 6 项分开讲了滑铲的每条规则。这一项把它们按**一条命令里的执行顺序**排在一起，所有分支和常数都在里面。重建检验（阶段 4）就照这一段写滑铲：顺序错了（比如先移动后起滑、退还用按蹲那条命令算过渡），数会对不上 R5。

#### 规则和公式

常数（Reference，Gibraltar 空手；带 × msc 的按命令的 msc 算）：

| 名字（Unity 字段） | R5 原值 [u] | [m] | 身高比例 | 依据 |
|---|---|---|---|---|
| `slideRequiredStartSpeed` | 200 u/s | 5.08 m/s | 2.778 H/s | [数据] |
| `slideSpeedBoost` × msc | 150 × msc u/s（172.5） | 3.81 × msc m/s | 2.083 × msc H/s | [数据] |
| `slideSpeedBoostCap` × msc | 400 × msc u/s（460） | 10.16 × msc m/s | 5.556 × msc H/s | [数据] [实测] |
| `slideBoostRearm` | 2.0 s | — | — | [反编译] [实测] |
| `slideDecel` | 100 u/s² | 2.54 m/s² | 1.389 H/s² | [数据] [实测] |
| `slideWantToStopDecel` | 400 u/s² | 10.16 m/s² | 5.556 H/s² | [数据] [实测] |
| `slideVelocityDecay` | 0.7 ×/s | — | — | [数据] [实测] |
| `slideStopSpeed` | 125 u/s | 3.175 m/s | 1.736 H/s | [数据] [实测] |
| `slideMaxStopSpeed` | 350 u/s | 8.89 m/s | 4.861 H/s | [数据] [实测] |
| `slideSteerAccel`（`slideAccel`）× msc | 50 × msc u/s²（57.5） | 1.27 × msc m/s² | 0.694 × msc H/s² | [反编译] [实测] |
| `slideBoostRefundWindow` | 0.4 s | — | — | [反编译] |
| `slideDuckTransitionTime` | 0.2 s | — | — | [反编译] [实测] |
| `slideMaxJumpSpeed` | 350 u/s | 8.89 m/s | 4.861 H/s | [数据] [实测] |
| `slideJumpFloorLowFrac` | 0.85 × | — | — | [反编译] |
| `slideJumpHeight` | 50 u | 1.270 m | 0.694 H | [数据] [实测] |
| `slideSlopeGravityScale` | 1 × | — | — | [反编译] |
| `crouchSpeed` × msc | 80 × msc u/s（92） | 2.032 × msc m/s | 1.111 × msc H/s | [实测] |
| `crouchDeceleration` | 1500 u/s² | 38.1 m/s² | 20.83 H/s² | [实测] |
| g = `sv_gravity` × `gravityScale` | 750 u/s² | 19.05 m/s² | 10.42 H/s² | [数据] |
| 着地探测 `groundProbe` | 2 u | 0.0508 m | 0.0278 H | [反编译] |
| 起滑地面法线下限 | n_z > 0.7 | — | — | [反编译] |

#### 实现模板

```
// 单位：u、s。每条命令调用一次 Command(input, dt)。
// 状态（初值）：sliding=false, boosted=false, lastBoost=0, boostTime=-∞, slideStartTime=-∞,
//   duckTransitionStart=-∞, prevDuckHeld=false, prevSprintHeld=false, lastLandTime=-∞,
//   prevGrounded, prevGroundKey
Command(input, dt):
    now = time
    msc = input.moveScale (默认 1.15)
    wishvel = forward(yaw)*input.fwd + right(yaw)*input.side ; hasInput = |wishvel_h| > 0
    // ---- 0. 世界在命令前更新地面（第 02 章）
    n, floorZ, groundKey = world.support(pos)
    if grounded and pos.z - floorZ > 2:                    // 走下台边
        grounded = false; sliding = false
    // ---- 1. 本条命令的前置标志
    ducked    = prevDuckHeld
    sprinting = grounded and input.sprint and prevSprintHeld and input.fwd > 0
                and not ducked and not input.duckHeld and not sliding
    s = |v_h| ; dir = v_h / s (s = 0 时为 0)
    updateDuckHull(input, now)                              // §4.8
    // ---- 2. 被别的动作接管（翻越、攀爬、滑索、跳板发射…）
    if kinematic or launch:
        sliding = false; boosted = false; ... (第 03 / 05 章) ; goto END
    // ---- 3. 换地面实体重新起滑（§4.4）
    if rebeginMode != Off and grounded and sliding and input.duckHeld and prevGrounded
       and groundKey != prevGroundKey and s >= 200:
        peak = min(s + 150*msc, 400*msc)
        if now - slideStartTime >= 2.0 and peak > s:
            lastBoost = peak - s; boostTime = now; s = peak; v_h = dir*s; boosted = true
        slideStartTime = now
    // ---- 4. 按蹲起滑（§4.1）
    if grounded and not sliding and input.duckPressed and s >= 200 and n.z > 0.7:
        boosted = (now - slideStartTime >= 2.0)
        if boosted:
            peak = min(s + 150*msc, 400*msc)
            lastBoost = peak - s; boostTime = now; s = peak; v_h = dir*s
        sliding = true; slideStartTime = now; duckTransitionStart = now + dt
        sprinting = false
    // ---- 5. 起跳
    if grounded and input.jumpPressed:
        frac = multiJumpFrac(now - lastLandTime)            // 第 03 章
        if sliding:                                          // §4.6
            if boosted:
                if now - boostTime < 0.4 and now - duckTransitionStart < 0.2:
                    s = max(0, s - lastBoost)
                if 297.5 < s < 350: s = 350
            v_h = dir*s; sliding = false; boosted = false
            H = 50
        else:
            v_h = groundJumpSpeed(v_h, now - lastLandTime)  // 第 03 章（超速削减）
            H = 56
        jumpCommand(sqrt(2*g*H*frac), dt)                   // 第 03 章：半步重力、+30、空中加速、移动、落地检查
        goto END
    // ---- 6. 着地
    if grounded:
        releasing = sliding and not input.duckHeld
        if releasing and s <= 350:                          // §4.3
            sliding = false; boosted = false; ducked = true
        if sliding:
            if n.z < 1 - 1e-6:                              // §4.5 坡面项
                v_h += g * 1.0 * n.z * (n.x, n.y) * dt
                s = |v_h|; dir = v_h / s
            D = releasing ? 400 : 100                       // §4.2
            s = max(0, (s - D*dt) * 0.7^dt)
            if hasInput:                                    // §4.2 转向
                p = wishvel_h - dot2(wishvel_h, dir)*dir
                if |p| > 1e-9 and s > 1e-9: dir = normalize(dir*s + normalize(p)*(50*msc*dt))
            v_h = dir*s
            if s < 125: sliding = false                     // §4.3
        else:
            groundMove(input, ducked, sprinting, msc, dt)   // 第 03 章；蹲着：上限 80*msc，减速 1500
        v.z = 0
        moveOnGround(dt)                                    // 第 02 章：平地 pos += v*dt, z = floor；坡上 U-1
    // ---- 7. 空中
    else:
        airMove(input, msc, dt)                             // 第 03 章：半步重力、空中加速、lurch、移动
        if v.z < 0 and pos.z - floorZ <= 2:                 // 落地
            grounded = true; v.z = 0; lastLandTime = now
            if input.duckHeld and |v_h| >= 200:             // §4.4 落地续滑
                sliding = true; boosted = false; slideStartTime = now
  END:
    prevGroundKey = groundKey (这条命令开始时的); prevGrounded = (这条命令开始时 grounded)
    prevDuckHeld = input.duckHeld; prevSprintHeld = input.sprint
    time = now + dt
```

离散化要注意的地方：

1. **起滑在移动之前**：按蹲那条命令的 pre 已经是 460，post 已经衰减一次。先移动再起滑，起滑会晚一条命令。
2. **下蹲过渡从起滑的下一条命令开始**：用按蹲那条命令算，0.201 s 的退还在 144 fps 会变成不退。
3. **松蹲 ≤ 350 在移动之前结束**：那条命令按蹲走（1500），不是按滑铲（100 / 400）。
4. **按住蹲 < 125 在移动之后结束**：那条命令按滑铲走完。
5. **"蹲着"标志晚一条命令**（= 上一条按住了蹲），影响蹲走的上限和减速、空中最大速度（第 03 章）。

Unity 参考实现：`U:…/R5MotorV2.cs`，`R5MotorV2.Step` → `Move`（顺序同上）、`JumpCommand`、`AirMove`、`CheckLanding`；参数 `U:…/R5MotorV2Params.cs`（`R5Reference()`，以及 `U:…/MovementConfig.cs` `MovementConfigs.Reference()` 加的斜坡开关）。游戏身体和回放电机的滑铲规则一样（D-47）；斜坡规则只在 Reference（D-66）。旧规则一键切回：`R5MotorV2Params.LegacyM2()` / `WithLegacyM2Slide()`、`BatchReplay -legacyM2`。

#### 验收

- **重建检验的对照**：附件 `04-slide-mantle/slide_ref.py` 是照本节伪代码写的独立实现（只用 Python 标准库，平地、按住 W），运行 `py -3 slide_ref.py` 打印：

  | 项 | 本节伪代码 | R5 |
  |---|---|---|
  | 144 fps 冲刺起滑 peak | 460.000 | 460.000 |
  | 144 fps 按住蹲滑到结束 | 第 243 条命令后，post 124.34 | 第 244 条，post 124.75（R5 dt 抖动） |
  | 滑铲跳 0.2014 / 0.5972 s | 247.71 / 350.00 | 247.77 / 350.005 |
  | 120 fps 滑铲跳 0.10 / 0.25 / 0.40 / 0.60 / 1.0 s | 273.1 / 396.9 / 361.6 / 350.0 / 238.0 | 273 / 397 / 361.5 / 350.0 / 236 |
  | 120 fps 松蹲 0.10 / 0.25 s | 19 / 11 条后结束，336.3 / 335.6 | 19 / 11 条，336 / 335 |

  一个新的实现跑同样的输入，和这一列差 < 0.5 u/s、结束命令一样，就算通过。
- **Unity 回放基线**：`research/phase2-local/rud/rud_check.py`（M2/M1 222、M3 90、M4 114 个输出逐字节不变；RUD 是最新的回放基线，包含 RPS 的滑铲规则）。
- **单元测试**：§4.1 – §4.6 各节列的测试；`R5MotorV2ReplayTests`（回放电机对 M2 录像）。
- **手感对照**：FEEL §3（平地 511 / 513 个检查一致）。

#### 出处

- 本章 §4.1 – §4.6 的出处。
- `U:…/R5MotorV2.cs` 类注释（逐命令顺序）、`R5MotorV2.NativeSlideChoice`（原生滑铲规则一句话版）。main
- RPS、`research/phase2-local/rud/README.md`（回放基线）。main

---

## 4.8 蹲下 / 起身：眼高过渡和蹲姿碰撞体

#### 原理

蹲下有两件事：**眼睛**降下来（镜头）和**碰撞体**变矮（能钻过矮的地方）。眼睛的过渡要平滑，但滑铲时要快——滑铲开始时眼睛 0.2 s 就贴地，速度感来自这一下；平时蹲下用 0.4 s。碰撞体在地上按住蹲 0.2 s 才变矮。空中松开蹲时，碰撞体站起来是"头不动、脚往下伸"，所以滑铲跳在空中松开蹲，脚会往下伸 16.5 u，落地更早。

#### 规则和公式

**眼高**（眼睛在原点上方的高度）：

1. "在蹲"= 在滑铲中，或"蹲着"标志（上一条命令按住蹲），或碰撞体是蹲着的。
2. 下蹲比例 d ∈ [0, 1]：每条命令朝目标（在蹲 = 1，否则 0）匀速移动，速率 1 / 0.4 s；**在滑铲中** 1 / 0.2 s。从起身中途再蹲下，按当前比例继续（不会跳变）。
3. 站立眼高带冲刺下沉：stand = 70 + (−6)·sin(f_sprint·π/2)，f_sprint 是冲刺比例（冲刺标志亮 0.16 s 后以 1.25 /s 上升；熄灭 0.11 s 后以 6.67 /s 下降；这一部分是镜头的事，第 07 章）。
4. eye = stand + (32 − stand)·smoothstep(d)，smoothstep(x) = x²(3 − 2x)。所以冲刺中起滑是从 64 降到 32。
5. 原生的下蹲状态：0 站、1 正在蹲下、2 已蹲下、3 正在起身；计时 400 ms，这次按蹲开始了滑铲则 200 ms。Unity 用比例 d 表示同一件事。

**碰撞体**（规则来自 RUD / M5，尺寸在 [01 §4.2](01-units-body.md)、第 02 章）：

1. 着地按住蹲 `hullCrouchTime` 0.2 s → 碰撞体变成蹲姿（HSD 设计高度 48 u，R5 没量过）。
2. 松开蹲：着地时直接站起来（脚不动；头顶被挡住就继续蹲着）；**在空中**、碰撞体是蹲姿、并且离地已 ≥ `airUnduckMinAfterTakeoff` 0.08 s → 原点下降 `airUnduckDrop` 16.5 u（头不动、脚往下），不低于地面。
3. **空中按蹲**（R5 有，Unity 只部分做了）：R5 空中按蹲 0.42 s 后"蹲到底"，原点**抬高** 16.5 u（脚往上收），眼高偏移 70 → 48.5（按 SimpleSpline，0.4 s）后跳成 32。Unity 不抬原点，只在翻越探测和蹲着翻越里用这条（§4.12）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 站立眼高 `standEye` | 1.778 m | 70 u | 0.972 H | — | [数据] setfile `viewheight` |
| 冲刺下沉 `sprintOffset` | −0.152 m | −6 u（冲刺中 64） | −0.083 H | — | [数据] [实测] |
| 蹲 / 滑铲眼高 `crouchEye` | 0.813 m | 32 u | 0.444 H | — | [实测] C3 |
| 下蹲过渡 `duckTime` / 滑铲 `slideDuckTime` | — | 0.4 s / 0.2 s | — | C3 滑铲下沉 0.208–0.213 s | [反编译] [实测] |
| 过渡形状 | — | smoothstep | — | 拟合 C3 ±1 u | [推断] |
| 碰撞体变矮要按住 `hullCrouchTime` | — | 0.2 s | — | R5 标志 0.21–0.24 s 后亮 | [实测] |
| 空中站起时原点下降 `airUnduckDrop` | 0.419 m | 16.5 u | 0.229 H | 实测 16.50（8 次）；跳板蹲着弹射 12.5（1 次） | [实测] |
| 空中站起最早在离地后 `airUnduckMinAfterTakeoff` | — | 0.08 s | — | 实测 0.076–0.083 s | [实测] |
| 空中蹲到底的时间（R5） | — | 0.42 s（0.40–0.43） | — | 地上明显快 | [实测] Frida D72 |
| 空中蹲到底时原点抬高（R5） | 0.419 m | 16.5 u | 0.229 H | — | [实测] Frida D72 |

**已知差别**（D-70 只记录不追）：滑铲眼高降到最低的时间 Unity 约 0.19 s、R5 约 0.167 s（差约 3 条命令）。注意 C3 测到的"滑铲下沉 0.208–0.213 s"是另一种量法（见 `_notes`，两处说法要统一）。

#### 实现模板

```
// 单位：u、s。每条命令在身体走完以后，用 post 状态更新一次
down = sliding or ducked or hullCrouched
rate = 1 / (sliding ? 0.2 : 0.4)
d    = moveToward(d, down ? 1 : 0, rate*dt)
stand = 70 + (-6) * sin(fSprint * PI/2)
eye   = stand + (32 - stand) * smoothstep(d)

// 碰撞体：每条命令开头（§4.7 第 1 步）
updateDuckHull(input, now):
    if input.duckHeld:
        if duckHeldSince is none: duckHeldSince = now
        if grounded and now - duckHeldSince >= 0.2: hullCrouched = true
        return
    duckHeldSince = none
    if not hullCrouched: return
    if grounded: hullCrouched = false (world 里头顶被挡就保持蹲姿); return
    if now - lastTakeoffTime < 0.08: return
    pos.z = max(floorZ, pos.z - 16.5); hullCrouched = false
```

Unity 参考实现：眼高 `U:…/NativeEyeHeight.cs`（`NativeEyeParams`、`NativeEyeHeight.Step` / `Height`），由 `HSD-Unity: Assets/HSD/Game/Runtime/Camera/Native/NativeCamera.cs`（`NativeCamera.Observe`）每条命令调用；碰撞体 `U:…/R5MotorV2.cs` `R5MotorV2.UpdateDuckHull`（`airUnduckDrop` 16.5、`airUnduckMinAfterTakeoff` 0.08、`hullCrouchTime` 0.2），`U:…/World/MovementWorld.cs` `MovementWorld.BeforeStep`（头顶被挡保持蹲姿）。

#### 验收

- `CameraFeelReplayTests.ASlideLowersTheEye`、`NativeCameraTests.StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt`。
- `NativeTraversalTests.TheEyeFollowsTheMeasuredDuckCurves`（空中下蹲 70 − 21.5·SimpleSpline(t/0.4)：0.1 s 66.64、0.2 s 59.25）。
- RUD 回放基线（`airUnduckDrop` 在回放电机里也开着）：M3 e3 滑铲跳 r650 / r651 位置误差 7.26 → 2.54 / 7.05 → 1.09 u。
- 合格线：滑铲开始后眼高 0.2 s 内到 32 ± 1 u；空中松蹲的原点下降 16.5 ± 0.1 u，在离地 0.08 s 以后。

#### 出处

- `research/rea-native/subsystems/N2-C-CAMERA.md` 眼高一行（`Duck` 计时 400 / 200 ms）；NS §3（下蹲状态 0–3）。main
- `research/phase2-local/m5/reference_config/README.md`（16.5 u、0.08 s、0.2 s）；`research/phase2-local/rud/README.md`。main
- D72 §8.2（空中下蹲 0.42 s、眼高曲线、原点抬 16.5）。main
- DIFF K-4（眼高 64 → 70）、§二"滑铲下沉"行（D-70）、"RUD"节。main
- [01 §4.2](01-units-body.md)（身体尺寸）。
- [反编译] `ViewHeight?` 0x140a53f30、`Duck` 0x140a54080（计时器 player+0x242c，状态 +0x2a70）、`Sprint_ViewOffset` 0x140af2370；眼高偏移 +0xf0（Frida）。

---

## 4.9 翻越的检测和高度范围

#### 原理

翻越是"空中碰到一面墙、上沿够得着，就自动翻上去"。三个设计选择：

1. **只在空中**：走路撞墙永远不翻越也不攀爬，避免贴墙走时被吸上去。
2. **要朝着墙**：视角或输入方向大致对着墙（35° 以内），并且按着前进键。
3. **够得着就翻，够不着就爬**：台沿在原点上方 18–80 u 之间直接翻；更高就先攀爬（§4.10），爬到够得着再翻；低于 18 u 的是台阶，跨过去就行。

#### 规则和公式

每条**空中**命令（翻越 / 攀爬都没在进行时）：

1. 前提：不在地面；前后轴 > 0（按住 W）；竖直速度 ≥ −`maxFallSpeed`（下落太快不抓）；没有别的动作在驱动身体；没有技能禁止翻越。
2. **墙**：这条命令或上一条（1.5 条命令以内）撞到了一面墙，墙的法线 |n_z| ≤ 0.5；视角前向或输入方向和墙的内法线夹角 ≤ `faceCone`。
3. **台沿探测**（沿内法线方向 dir）：
   1. 从碰撞体前面往前找墙，`reach` 以内要有墙，否则"没有墙"。
   2. 在墙面点往里 2·16 + `inset` = 22.4 u 的位置，向下找能站的面，只找到原点上方 `maxHeight`。
   3. 台面高度 h = 台面 − 原点 z：
      - h ≤ `minHeight` 18：如果原点上方 80 u 处放不下蹲姿碰撞体（严格的重叠检查）→ "太高"（去攀爬）；放得下 → "太矮"（台阶，什么都不做）。
      - 否则目标点 = (墙内 22.4 u, 台面)；目标处放不下**蹲姿**碰撞体 → "目标被挡"；从墙面点竖直升到台面、再水平到目标的路径被挡 → "上方被挡"；都通过 → **找到**。
4. 找到 → 开始翻越（§4.11）。"太高" → 开始攀爬（§4.10，一次落地只能爬一次）。其他 → 什么都不做，照常飞。
5. 空中已经蹲到底（R5：按蹲 0.42 s 后，原点抬高 16.5）且第一次没找到 → 从抬高 16.5 的原点再探一次（§4.12）。
6. 攀爬结束的"最后一跳"之后的空中，只要朝着墙（视角），每条命令都继续探台沿（H232 在这里翻上去）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 翻越最高台沿 `ledge.maxHeight`（= R5 `mantleHeight`） | 2.032 m | 80 u | 1.111 H | 实测触发到 79.9，76.0 也有没触发的 | [数据] [实测] A2 §2.4 |
| 最低台沿 `ledge.minHeight`（= HSD 台阶高度） | 0.457 m | HSD 18 u（R5 台阶 22 u） | 0.25 H | 见第 02 章台阶的差别 | [设计] |
| 找墙距离 `ledge.reach` | 0.610 m | 24 u | 0.333 H | — | [设计] |
| 目标点在墙里 2·16 + `ledge.inset` | 0.569 m | 32 − 9.6 = 22.4 u（出口原点在墙面里 6.4 u） | 0.311 H | 实测出口原点在墙面里 6.4 u | [实测] A2 §2.4 |
| 面向锥 `faceCone` | — | 35° | — | R5 测到视线偏 45° + W+D 也能翻 | [设计] [实测] |
| 墙法线 `maxWallNormalZ` | — | \|n_z\| ≤ 0.5 | — | — | [设计] |
| 最快下落 `maxFallSpeed` | 10.16 m/s | 400 u/s | 5.556 H/s | — | [设计] |

R5 实测结果（A2，冲刺跳到墙前约 100 u，按住 W）：

| 墙高 | 结果 |
|---|---|
| 60 | 直接落到墙顶，不爬不翻 |
| 90、120 | 碰墙那一刻直接翻越（台沿在原点上方 43.9 / 73.6 u） |
| 150、180 | 先爬 0.206 / 0.399 s，再翻越 |
| 232 | 爬满 0.849 s、最后一跳、在空中翻越 |
| 300、400 | 爬满、最后一跳、掉下来 |
| 任何高度，走路撞墙 | 不爬不翻 |

**和 R5 的差别**：

- R5 的探测在碰撞体撞到墙**之前**就开始（原生 `AutoMantle_Search`），Unity 要先撞到墙。影响 +30 推墙（J-1）的判断，Unity 用"上一条命令按着 W 朝着这面墙就当作 R5 已经探到"来对齐（§4.13）。
- **R5 的探测几何（距离、角度、高度）没读**：`AutoMantle_Try` / `AutoMantle_Search` 还没反编译（B04-1），Unity 的探测参数是 [设计]，按 A2 的实测结果校准过。原生 ConVar 还有 `automantle_cooldown` 0.25 s，Unity 没做。
- 曾经有一个死区 bug（台沿在 80–98 u 时既不翻也不爬，滑铲跳上墙时碰到），已修（C-1，D-27）。

#### 实现模板

```
// 单位：u、s。空中命令、翻越 / 攀爬都没在进行
if grounded or fwd <= 0 or v.z < -400 or otherDriving or mantleBlocked: return
if afterJumpUp:
    if facesView(wallNormal): lh = probeLedge(pos, -wallNormal); if lh.found: startMantle(lh)
    return
c = lastWallContact                       // 1.5 条命令以内
if not c or |c.normal.z| > 0.5: return
n = flat(c.normal)
if not (facesView(n) or facesWish(n)): return          // 35°
lh = probeLedge(pos, -n)
if not lh.found and nativeDuckedInAir: lh2 = probeLedge(pos + (0,0,16.5), -n); if lh2.found: lh = lh2
if lh.found: startMantle(lh)
elif lh.reason == TOO_HIGH and not climbUsedSinceLanding: startClimb(n)

probeLedge(feet, dir):
    w = findWall(feet, dir, reach=24)          ; if none: NO_WALL
    c = w.point + dir*(2*16 - 9.6)
    top = highestStandable(c, radius 16, up to feet.z + 80)
    if top - feet.z <= 18:
        return blockedStrict(c at feet.z+80, crouchHull) ? TOO_HIGH : TOO_LOW
    target = (c.x, c.y, top)
    if blocked(target, crouchHull): TARGET_BLOCKED
    if sweep(w.point -> (w.point.xy, top) -> target) blocked: BLOCKED_ABOVE
    return found(target, top, wallNormal)
```

Unity 参考实现：`U:…/Abilities/Climb/ClimbAbility.cs`，`ClimbAbility.TryStart`、`Faces` / `FacesWish`；探测 `U:…/World/MovementWorld.cs` `MovementWorld.ProbeLedge`，参数 `LedgeProbeParams`（`U:…/World/WorldGeometry.cs`；Reference 用 `ClimbParams.ledge`：18 / 80 / 24 / −9.6 / 2 / 64）。

#### 验收

- `A2Climb.H60LandsOnTopWithoutClimbOrMantle`、`A2Climb.InstantMantleAtContact`、`A2Climb.ShortClimbThenMantle`、`A2Climb.H232FullClimbJumpUpAndMantleFromTheAir`、`A2Climb.TallWallClimbJumpUpThenFall`、`A2Climb.WalkingIntoAFaceNeverClimbs`（都在 `R5MotorM6Tests.cs`）。
- `FeelReplayTests.TheLedgeProbeHasNoDeadZoneAboveTheReach`（85 / 94 / 150 u）、`FeelReplayTests.ATopWithinTheReachIsStillALedge`、`FeelReplayTests.ABodyMeetingTheFace94uBelowTheTopClimbsAtOnce`。
- 对照：FEEL §6（494 个攀爬片段，1969 / 2221 个检查一致，88.7 %；剩下的主要是 superglide 窗口两端）。
- 合格线：上表每个墙高的结果类别和 R5 一样；翻越开始的台沿高度和 R5 差 < 1 u。

#### 出处

- A2 §2.1（各高度结果）、§2.4（触发高度、出口在墙面里 6.4 u）。main
- NM §1（`mantleHeight`、`automantle_*` ConVar）、§6（`AutoMantle_Try` / `Search` 没读）。main
- `research/rea-native/n4/N4A-READBACK.md` §2（`mantleHeight` 80）。main
- FEEL §6.3 C-1、§6.4（死区修复）；D-27。main
- `research/phase2-local/m8/r_sg/SG.md`（视线偏 45°、W+D 也能翻：`faceConeAlsoWish`）。main

---

## 4.10 攀爬（台沿够不着时）

#### 原理

台沿太高时，角色先贴着墙往上爬一段（Apex 的 climb），爬的过程中一直找台沿，够得着就翻越。攀爬的高度**按起跳的地面算**，不按墙算：不管墙多高，爬到起跳点上方约 147 u 就到头，最后往上一蹿，还够不着就掉下来。所以"能翻上多高的墙"是固定的（约 232 u 的墙），关卡可以按这个尺度设计。

攀爬中按蹲会立刻放弃攀爬（R5 原生规则），所以蹲着够不着的墙就翻不上去。

#### 规则和公式

1. **开始**（§4.9 判"太高"，一次落地只能爬一次）：这条命令水平速度清零，竖直速度 += 9.6 − ½·g·dt。
2. **每条命令**（按住 W）：
   - 按跳 → 蹬墙跳（第 05 章）；
   - 按住蹲（开始后的下一条命令起）→ 攀爬结束，身体照常在空中飞（D-75 E）；
   - 松开 W → 贴墙下滑（下面第 4 条）；
   - 找台沿：找到 → 翻越；墙没了 → 结束；
   - 原点到 z_ref + `endHeight`（z_ref = 最后一次着地的高度）→ 最后一跳：vz += 208 − 584·dt，向外 68.1 − 500·dt；之后空中继续找台沿；
   - 竖直速度：先把开始时多余的（> 100）按重力减掉，然后 vz = min(vz + 490·dt, 1.735·(z_ref + 180.4 − z))（"速度线"）；
   - 按侧向键：沿墙横移，加速度 113·(1 − v/102.6) u/s²。
3. 1.000 s（从接触算）还没结束 → 脱离：向外 69.97 u/s，保留当时的竖直速度。
4. **贴墙下滑**（松开 W）：dvz/dt = −320 − 727·t_c（vz > 0）/ +72 − 806·t_c（vz ≤ 0），t_c = 距接触的时间；按后退 0.060 s 后脱离（期间多 −310 u/s²）；按跳 = 蹬墙跳；到底着地；1.000 s 脱离。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 接触时竖直加速 `contactDvz` | 0.244 m/s | 9.6 u/s | 0.133 H/s | — | [实测] M3 |
| 攀爬加速 `accel` | 12.45 m/s² | 490 u/s² | 6.806 H/s² | 499 → 486 | [拟合] |
| 速度线斜率 `speedLineK` | — | 1.735 /s | — | 最大误差 ≤ 1.8 u/s | [拟合] |
| 速度线零点 `speedLineZ0`（起跳面上方） | 4.582 m | 180.4 u | 2.506 H | 180.3–180.4 | [拟合] |
| 攀爬终点 `endHeight`（起跳面上方） | 3.735 m | 147.06 u | 2.042 H | 146.95–147.17 | [实测] |
| 最后一跳 `jumpUpDvz` / `jumpUpOut` | 5.283 / 1.730 m/s | 208 − 584·dt / 68.1 − 500·dt u/s | 2.889 / 0.946 H/s | 120 fps：+202.8 / 64.3 | [实测] |
| 侧向漂移 `climbSideAccel` / `climbSideMax` | 2.870 m/s² / 2.606 m/s | 113 u/s² / 102.6 u/s | 1.569 H/s² / 1.425 H/s | — | [拟合] |
| 脱离时间 / 推力 `detachAfterContact` / `detachPush` | — / 1.777 m/s | 1.000 s / 69.97 u/s | — / 0.972 H/s | — | [实测] |
| 满爬时长 | — | 0.849 s | — | sd 0.001 | [实测] A2 |

**HSD 自己的东西不在这里**：抓边悬挂（`LedgeHangParams`）是 HSD 设计，Reference 关着，第 05 章。Revenant 的长攀爬是同一个状态机上的另一组参数（`RevenantProfile`），技能章。

#### 实现模板

```
// 单位：u、s
startClimb(n):  v_h = 0; v.z += 9.6 - 0.5*g*dt; contactTime = now; wallNormal = n
stepClimb():
    if jumpPressed: wallJump(); return                       // 第 05 章
    if crouchHeld and now > contactTime: endClimb(); return  // D-75 E
    if fwd <= 0: enterWallSlide(); return
    lh = probeLedge(pos, -wallNormal); if lh.found: startMantle(lh); return
    if lh.reason == NO_WALL: endClimb(); return
    if pos.z >= zRef + 147.06: jumpUp(); return
    if now - contactTime >= 1.0: detach(69.97); return
    if not accelerating and v.z > 100: v.z -= g*dt
    else: accelerating = true; v.z = min(v.z + 490*dt, 1.735*(zRef + 180.4 - pos.z))
    lateral drift by side key; move kinematically (no gravity)
```

Unity 参考实现：`U:…/Abilities/Climb/ClimbAbility.cs`，`ClimbAbility.StartClimb`、`StepClimb`、`JumpUp`、`StepSlide`、`Detach`；参数 `ClimbParams`（climb 一段）。

#### 验收

- `A2Climb.ShortClimbThenMantle`、`A2Climb.H232FullClimbJumpUpAndMantleFromTheAir`、`A2Climb.ClimbIsFrameRateIndependent`（60 / 144 fps）、`A2Climb.ReleaseOnTheWallSlidesAndDetachesAtOneSecond`、`A2Climb.BackOnTheSlideDetachesEarly`、`A2Climb.SideKeyWhileClimbingDriftsAlongTheFace`、`A2Climb.JumpUpStillFiresWithWReleasedJustBeforeTheEnd`。
- `NativeTraversalTests.CrouchHeldEndsTheWallClimb`。
- 对照：A2 §2.2（满爬 0.849 s，终点 z 442.17）；D72 §3（h160 / h200 蹲着 0 / 116 上去）。
- 合格线：满爬时长和 R5 差 ≤ 0.01 s；终点高度差 ≤ 0.2 u。

#### 出处

- A2 §2.2、§2.3（终点按起跳面、不按台沿）、§9（第 2b 轮：下滑、脱离、侧移）。main
- `research/phase2-local/m3/wall_mantle/WALL-MANTLE-MODEL.md` §2.2（接触 9.6、速度线、最后一跳的 dt 律）。main
- D72 §3（蹲着取消爬墙）；D-75 E。main
- [反编译] `WallRun_TryStart` 0x140a4e220（下蹲键位 0x4000004 按着不开始）、`WallClimb_Move` 0x140a4d4e0。

---

## 4.11 翻越的路径、时长、出口和取消

#### 原理

翻越是一段**脚本化的路径**：先几乎竖直地升到台面高度，最后一段往前移到台面上。时长随要升的高度线性变化（矮的快、高的慢），翻越中不受重力和输入影响。结束时如果还按着前进，角色带着冲刺速度（或走路速度）直接往前跑，不需要重新加速——这是翻越"流畅"的来源。翻越前半段松开前进键可以取消，退回原处掉下来。

#### 规则和公式

1. **开始**：rise = 台面 − 原点 z；起点 = 当前原点；目标 = 探测给的目标点（墙里 22.4 u、台面高度）。水平方向 = 起点到目标的水平方向。
2. **时长**（站着开始）：T = `mantleTimeBase` + `mantleTimePerUnit` · rise。蹲着开始的走 §4.12。
3. **路径**（u = 已过时间 / T）：
   - 竖直：z = z₀ + (z_top − z₀)·smoothstep(u / 0.75)（u = 0.75 时升完）；
   - 水平：xy = xy₀ + (xy_目标 − xy₀)·smoothstep((u − 0.6) / 0.4)（u = 0.6 才开始往前）；
   - 每条命令把身体放到 PathAt(u₁)，速度 = (PathAt(u₁) − PathAt(u₀)) / dt。不加重力。
   - 路径形状是 [设计]（A2 只知道"先慢慢升，再几乎竖直，最后往前"）。被世界推离路径 > 4 u → 中止翻越（保证出得来）。
4. **自然结束**（u ≥ 1，没有按跳）：身体放到目标点，着地。
   - 按住 W：速度 = 输入方向 × 姿态速度：按住冲刺 299（`sprintspeed` × msc），没按冲刺 199.525（`speed` × msc）；
   - 没按 W：速度 0。
5. **取消**：翻越前 `cancelFrac` · T 以内，前后轴 < 1（松开 W，或按住 W 再按后退）→ 倒着退回去，用时 −0.007 + 1.053·τ（τ = 已翻的时间），然后放回起点、速度 0、往下掉。从悬挂开始的翻越不能取消。
6. **翻越中按跳**：见 §4.13 / §4.14。
7. 翻越开始时清掉"翻越加速后禁 lurch"标志（§4.14）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 时长基数 `mantleTimeBase` | — | 0.1728 s | — | R5 直接翻越拟合 0.1743 | [拟合] A2 / FEEL C-3 |
| 每 u 高度的时长 `mantleTimePerUnit` | 0.2165 s/m | 0.0055 s/u | 0.396 s/H | R5 0.00543 | [拟合] |
| 例：rise 43.9 / 73.6 u 的时长 | — | 0.414 / 0.578 s | — | R5 0.414 / 0.578 | [实测] A2 |
| 出口：冲刺 / 走路姿态速度 | 7.595 / 5.068 m/s | 299 / 199.525 u/s | 4.153 / 2.771 H/s | — | [实测] FEEL C-5 |
| 取消窗口 `cancelFrac` | — | 0.5 × T | — | 实测区间 (0.395, 0.685] | [设计] |
| 取消退回用时 | — | −0.007 + 1.053·τ s | — | rms 0.008 s | [拟合] |
| 路径：升完 / 开始前移 `mantleRiseEnd` / `mantleForwardStart` | — | 0.75 / 0.6 × T | — | — | [设计] |
| 偏离中止 `pathTolerance` | 0.102 m | 4 u | 0.056 H | — | [设计] |

**已知差别**：

- Unity 的站姿翻越比 R5 约长 25 ms（D72 §2.1 站姿 +0.01–0.05 s；FEEL C-3：直接翻越的公式两边差 < 1 ms，单次差是 R5 自己 1–2 条命令的散布；先攀爬再翻越的高墙 h232 Unity 晚 25–42 ms，D-30 不改）。
- R5 的 h90 / h120 直接翻越结束后第 2 条命令是 290、Unity 299（R5 还有一条命令在加速，差 9 u/s；A2 §2.4 的 24 / 65 次"掉 9.46 u/s"原因不明）。
- 原生站姿翻越的时长也可以用 §4.12 的原生进度算（h80 0.311 / h100 0.467 / h120 0.57 s，R5 0.317 / 0.466 / 0.562）；Unity 站姿仍用上面的拟合公式（逐位不变），只有蹲着时才用原生进度。

#### 实现模板

```
// 单位：u、s
startMantle(lh):
    start = pos; target = lh.target; top = lh.top; rise = max(0, top - pos.z)
    T = 0.1728 + 0.0055*rise          // 蹲着：§4.12
    mdir = flat(target - start)
stepMantle(tau):                      // tau = now - mantleStart
    if |pos - expected| > 4: abort
    if jumpPressed: §4.13 / §4.14
    if fwd < 1 and tau <= 0.5*T and not fromHang: startCancel(tau); return
    u0 = tau/T; u1 = (tau+dt)/T
    if u1 >= 1: finish(); return
    a = path(u0); b = path(u1); kinematicMove(to b, vel (b-a)/dt)
path(u): z = z0 + (ztop - z0)*smooth(u/0.75); xy = xy0 + (xyT - xy0)*smooth((u-0.6)/0.4)
finish(): pos = target; grounded = true
    v = W held ? (wish or mdir) * (sprintHeld ? 299 : 199.525) : 0
```

Unity 参考实现：`U:…/Abilities/Climb/ClimbAbility.cs`，`ClimbAbility.StartMantle`、`StepMantle`、`PathAt`、`FinishMantle`、`StepCancel`；`ClimbParams.mantleExitWalkSpeed`（由 `MovementConfig.mantleExitWalkSpeed` 打开，D-28）。

#### 验收

- `A2Climb.InstantMantleAtContact`（rise 和时长对 R5）、`A2Climb.ReleaseEarlyInTheMantleCancelsIt`、`A2Climb.BackWithWHeldCancelsTooAndLateReleaseCompletesAtRest`、`A2Climb.MantleExitFollowsTheInputDirection`。
- `FeelReplayTests.TheMantleEndLeavesAtTheStanceSpeed`（299 / 199.525）。
- `NativeTraversalTests.AStandingMantleKeepsItsTime`（站姿时长不受蹲姿规则影响）。
- 合格线：翻越时长和 R5 差 ≤ 0.03 s；出口速度 299 / 199.525 ± 0.01。

#### 出处

- A2 §2.4（时长拟合、出口、W 松开出口为 0）、§3（取消）、§9（第 2b 轮取消的拟合）。main
- NM §2.1、§2.3（原生出口 = 姿态最大速度 × 前向）、§5 M-01。main
- FEEL §6.3 C-3 / C-5、§6.4；D-28、D-30。main
- D72 §2.1（站姿 Unity +0.01–0.05 s）、§8.2（原生站姿进度）。main
- [反编译] `TraversalMove` 0x140a45380。

---

## 4.12 蹲着翻越（原生翻越状态）

#### 原理

R5 的翻越是一个按动画状态推进的状态机：开始时按"眼睛比台面高多少"选一种动画（低翻越、平、略高、高），翻越中途**蹲到底的那一刻**换成蹲姿版本的动画，推进速率跟着眼睛的高度变。所以蹲着翻越的时长不是一个数，而是随"什么时候按的蹲"连续变化。这个设计让蹲着翻越"慢一点、矮一点"，并且和下蹲动作自然衔接。

#### 规则和公式

只在**按着蹲**时启用（翻越开始就按着，或翻越中途按下那一刻起）；站着的翻越按 §4.11，不受影响。

1. **眼高偏移 e**（相对原点，蹲着翻越专用的曲线，Frida 实测）：
   - 没按蹲：70；
   - 翻越**前**在空中按的蹲：e = 70 − 21.5·SimpleSpline(t / 0.4)（t = 按蹲以来的时间），蹲到底（t ≥ 0.42 s）后 e = 32，同时原点抬高 16.5（所以眼睛的世界高度是原点 + 48.5）；
   - 翻越**中**才按的蹲：e = 70 − 38·SimpleSpline(t / 0.4)，蹲到底后 32（不抬原点）。
   - SimpleSpline(x) = smoothstep = x²(3 − 2x)。
2. **基础状态**（翻越开始时只选一次）：h = 眼睛的世界高度 − 台面 + 0.06：
   - h < −10 → 3（低翻越），但还要求眼睛离台面点水平 < 20 u（= 碰撞体半宽 16 + 4），否则 4；
   - −10 ≤ h < 10 → 4；10 ≤ h < 30 → 5；h ≥ 30 → 6。
3. **起始进度** f₀ = 0.7964 − 0.01002·rise（rise = 台面 − 原点；空中已蹲到底的用 rise − 16.5），限制在 [0, 0.95]。站蹲一样：h80 约 0.45、h100 约 0.25、h120 以上约 0.03。矮的台子翻越短，就是因为从中间开始。
4. **每条命令**：进度 f += rate(基础状态, e) · dt，到 1 结束。
   - 状态 3：rate = 1 / 0.7（和眼高无关）；
   - 状态 b = 4 / 5 / 6：rate = (1 − ((C_b − e + 80) / 80)·k) / len_b，C = −10 / 10 / 30，len = 0.6 / 0.5 / 0.35，k = 0.788。
   - 蹲到底（按蹲后 0.42 s）以后，状态 + 4（3 → 7 … 6 → 10，换蹲姿动画和镜头 / S27 曲线），rate 仍按**基础状态**的公式，只是 e 变成 32——速率变慢来自 e，不是来自 +4。
   - 例：站姿 h120（状态 4，e = 70）rate = 1 / 0.6 = 1.667；状态 8（e = 32）rate = 1.043。
5. **翻越中途按蹲**：从当前进度接上，速率乘一个比例，让按下那一刻的推进速度和站姿一样（不跳变）；按跳之后再按的蹲（superglide 的蹲）不改进度。
6. **路径**：路径 u = (f − f₀) / (1 − f₀)，仍用 §4.11 的 PathAt；镜头和 S27 用的"时间进度"按每条命令重新预测的总时长算。
7. **空中蹲到底的身体探台沿**从抬高 16.5 的原点开始（§4.9 第 5 条）：R5 h140 蹲着只有翻越前已经蹲到底的才上得去（15 / 15，其余 0 / 35）；h160 起蹲着都上不去（蹲着不能爬，§4.10）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 蹲到底时间 `duckFullTime` | — | 0.42 s | — | 0.40–0.43 | [实测] Frida |
| 眼高曲线时长 `duckEyeTime` | — | 0.4 s | — | 逐位对上 | [实测] Frida |
| 站 / 空中下蹲末端 / 蹲到底眼高 `eyeStand` / `eyeDuckingEnd` / `eyeDucked` | 1.778 / 1.232 / 0.813 m | 70 / 48.5 / 32 u | 0.972 / 0.674 / 0.444 H | — | [实测] Frida |
| 空中蹲到底原点抬高 `airDuckLift` | 0.419 m | 16.5 u | 0.229 H | — | [实测] Frida |
| 状态分界 `edge4` / `edge5` / `edge6` | −0.254 / 0.254 / 0.762 m | −10 / 10 / 30 u | −0.139 / 0.139 / 0.417 H | — | [反编译] ConVar `automantle_height_below / level / above` |
| 台面点在台面下 `pointAboveTop` | −0.0015 m | −0.06 u | — | — | [实测] Frida |
| 低翻越水平限制 `lowMaxDistance`（台面点在墙里 `pointPastFace`） | 0.508 m（0.112 m） | 20 u（4.4 u） | 0.278 H（0.061 H） | — | [反编译] [实测] |
| 速率公式的 H `height` | 2.032 m | 80 u | 1.111 H | — | [反编译] setfile |
| 动画长度 `len3` – `len6` | — | 0.7 / 0.6 / 0.5 / 0.35 s | — | — | [反编译] setfile |
| 速率系数 `k` | — | 0.788 × | — | 0.757–0.790 | [实测] Frida |
| 起始进度 `startFracA` / `startFracB` | — / 0.3945 /m | 0.7964 / 0.01002 /u | — / 0.721 /H | 残差 sd 0.005 | [拟合] Frida 55 段 |

R5 蹲着翻越的时长（D72，按蹲时刻不同）：h80 0.41–0.58 s 连续、h100 0.60–0.69、h120 四种（0.55 / 0.65 / 0.69–0.79 / 0.80–0.89）、h130 0.77–0.91 连续。

**HSD 复现不了的部分**（D-70 拟合原则，记下）：Unity 的翻越总从离墙面 16 u（离台面点 20.4 u）开始，按规则总是状态 4（长的）。R5 起点离台面点 19.4–20.5 u，跨过 20 的分界，h120 蹲着约 1 / 4 是状态 3（短 0.656 s），Unity 给 0.849 s（S 类平均差 0.193 s）；A 类（空中已蹲到底，0.551 s）Unity 0.77 s（差 0.218 s）。h120 M 类（4 → 8 中途切换）R5 的 S27 窗口 0.28 s，Unity 仍约 0.45 s（要每个状态一条曲线，没量）。

**旧版**（副版本，开关在）：B1 的单一蹲姿时长（站姿 0.313 / 0.467 / 0.571 s → 蹲姿 0.517 / 0.625 / 0.813 s 三点插值，`crouchedMantleTime`，D-22）。00-INVENTORY 过时表：B1 里"短的只在蹲下没完成时出现"被 D72 推翻。

#### 实现模板

```
// 单位：u、s
eyeOffset(duckSince, now, travStart):
    if duckSince is none: return 70
    t = now - duckSince
    if t >= 0.42: return 32
    end = (duckSince < travStart) ? 48.5 : 32
    return 70 - (70 - end)*smooth(t/0.4)
eyeWorldAtStart = ducked(t>=0.42) ? 48.5 : eyeOffset(...)
baseState(h = pos.z + eyeWorldAtStart - top + 0.06, toFace):
    if h < -10: return (toFace + 4.4 < 20) ? 3 : 4
    if h < 10: return 4
    return h < 30 ? 5 : 6
rate(b, e): b == 3 ? 1/0.7 : (1 - ((C[b] - e + 80)/80)*0.788) / len[b]     // C = {4:-10, 5:10, 6:30}, len = {4:0.6, 5:0.5, 6:0.35}
f0 = clamp(0.7964 - 0.01002*(rise - (duckedAtStart ? 16.5 : 0)), 0, 0.95)
each command: f = min(1, f + rate(base, eyeOffset(...))*scale*dt); u = (f - f0)/(1 - f0)
```

Unity 参考实现：`U:…/Abilities/Climb/NativeTraversal.cs`（`NativeTraversalParams`、`NativeTraversal.EyeOffset` / `EyeWorld` / `Ducked` / `BaseState` / `StartFraction` / `Rate` / `Remaining`）；接入在 `ClimbAbility.StartMantle` / `StepMantle`（`travBase`、`travFrac`、`travScale`）和 `ClimbAbility.TryStart`（抬高探测）。开关 `ClimbParams.nativeTraversalStates`（`MovementConfig.nativeTraversalStates`，Reference 和 Fun 开）；一次切回改前：`MovementConfig.SetD75(false)`、`FeelBatch` / `CameraFeelBatch -preD72`（单项 `-preD72B`）。

#### 验收

- `NativeTraversalTests.TheEyeFollowsTheMeasuredDuckCurves`、`NativeTraversalTests.TheBaseStateIsPickedFromTheEyeAndTheDistanceToTheLedge`、`NativeTraversalTests.AStandingMantleKeepsItsTime`、`NativeTraversalTests.ACrouchedH120MantleRunsOnTheNativeStates`。
- 对照：D72 §9.1 同一批 606 个 R5 输入：全部蹲姿时长平均 |Unity − R5| 0.061 → 0.043 s；h80 A 0.020、h100 S 0.019、h120 M 0.033、h140 L 0.026 s；站姿逐位不变。数据 `research/phase2-local/d72/out/compare_d75.md`。
- 原生模型本身：195 段 Frida 翻越里 177 段帧数差 ≤ 1 帧（D72 §8.2）。
- 合格线：按类平均时长差 ≤ 0.05 s（h120 S / A 类除外，已知复现不了）；站姿翻越时长不变。

#### 出处

- D72 §2（610 次蹲姿时长）、§8（Frida 读到的原生规则、常数、模型检查）、§9（Unity 改动和前后对比）。main
- DIFF "D-75"节、§二"D-75 剩下的"三行。main
- D-22、D-74、D-75（B）。main
- NM §2.1（下蹲完成时状态 + 4）。main
- [反编译] `TraversalMove` 0x140a45380（状态 player+0x2b34、进度 +0x2b7c、k = +0x2b60）；`Traversal_PickAnim` 0x140a41af0；台面点 P = `0x140b05910`、方向 D = `0x140b05ca0`；动画切换 `FUN_1409e5cc0`（活动号 = 状态 + 0x244）；setfile 偏移 2228 / 2236 / 2240 / 2244 / 2248。

---

## 4.13 superglide（原生 S21）

#### 原理

superglide 不是一个单独设计的技能，而是两条规则凑在一起的结果：**翻越快结束时按跳**，翻越会变成一次起跳，水平速度设成姿态速度（299）；**紧接着按蹲**，这次起跳的同时又触发了一次"开始滑铲"，于是吃到起滑加成，299 → 460。玩家感觉到的是从台沿上贴着飞出去、速度比冲刺快一半。窗口很窄（翻越最后约 0.1 s），这是它成为高难技巧的原因。

因为它用的是滑铲的起滑加成，所以也受 2 s 冷却管：刚滑过铲（或刚做过 superglide）就做不出来。

#### 规则和公式

1. **按跳**（翻越中，不是第一条命令）：记下按键时的已过时间 τ_p，翻越在**下一条命令**结算（不管按得早晚）。
2. **结算**（下一条命令）：剩余 r = T − τ_p（T 是这次翻越的时长，蹲着翻越用预测值）：
   - r > 窗口 + 减量段 → **切断**：身体放到 max(当前 z, 台面) 高度，空中，水平速度 = 输入方向 × h，不起跳（竖直 0）；
   - 窗口 < r ≤ 窗口 + 减量段，且这条命令按着蹲 → **减量 superglide**（下面第 4 条按比例）；没按蹲 → 切断；
   - r ≤ 窗口 → **起跳**（翻越跳或 superglide）。
   - 翻越已经自然结束才按 → 在台上普通起跳（第 03 章，299；碰过墙 329）。
3. **起跳**：
   - h = 按住 W ? min(299, 接近速度) : 0。接近速度 = 上次着地以来的最大水平速度（所以走路接近是 199.5）。
   - 方向 = 输入方向（按 W 时）；没有输入用翻越方向。Fun 的设计：按侧向键也给 h（横向 superglide，R5 没测）。
   - +30 推墙（J-1）：输入朝着"翻越开始前最后一次撞到的墙"→ 加 30 u/s（越过台沿）。
   - **滑铲加成**：这条命令按着蹲，并且 h ≥ 200，并且距上一次"开始滑铲"（含上一次 superglide 的蹲）≥ 2 s → h = min(h + 150·msc, 400·msc)。按着蹲但没拿到加成：只是翻越跳。按着蹲本身算一次"开始滑铲"（刷新冷却）。
   - 竖直：V = √(2·g·56) = 289.82（普通跳），起跳命令的半步重力顺序同普通跳（post vz = V − 1.5·g·dt）。
   - 落地还按着蹲 → 接着滑（§4.4）。
4. **减量段**（Reference）：h 先按第 3 条算出加成后的值，再乘一个从 385/460 到 425/460 线性变化的比例（离窗口越近越大）；加成被拒（冷却、速度不够）→ 切断。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 起跳窗口 `nativeJumpWindow`（剩余时间） | — | 0.1025 s | — | R5 最后 0.005–0.085 s 100 % 成功，0.086–0.12 s 混合 | [实测] SG、A2 |
| 减量段 `superglideReducedBand` | — | 0.015 s（窗口前 102.5–117.5 ms） | — | R5 14 次里 9 次减量 | [实测] FEEL C-2 |
| 减量比例 `nativeReducedEdgeFrac` / `NearFrac` | — | 385/460 → 425/460 | — | R5 344–429 | [实测] |
| superglide 出口水平 | 11.68 m/s | 460 u/s（299 + 161 封顶） | 6.389 H/s | 实测 460.000 | [实测] |
| 翻越跳竖直 V `nativeJumpHeight` 56 | 7.361 m/s | 289.82 u/s（post 286.2–286.7） | 4.025 H/s | — | [实测] |
| 走路接近碰过墙的 superglide | 10.21 m/s | 199.5 + 30 + 172.5 = 402.0 u/s | 5.583 H/s | R5 3 / 15 | [反编译] [实测] |
| 只按跳、碰过墙的翻越跳 | 8.357 m/s | 299 + 30 = 329 u/s | 4.569 H/s | R5 3 / 12 | [反编译] [实测] |

R5 各高度的窗口（SG，冲刺接近，按键时刻从翻越开始算）：

| 墙高 | 翻越时长 | 切断（剩余） | superglide 460（剩余） |
|---|---|---|---|
| 90 | 0.418 s | 0.093–0.143 s | 0.005–0.108 s |
| 120 | 0.581 | 0.106–0.123 | 0.006–0.118 |
| 150 | 0.602 | 0.086–0.136 | 0.019–0.119 |
| 180 | 0.600 | 0.108 | 0.008–0.092 |
| 232 | 0.587 | 0.095–0.128 | 0.027–0.095 |

斜 30° 接近：15 / 15 superglide，沿视线 / 输入方向出去；视线偏 45° + W+D：14 / 15，沿输入方向（垂直于墙）。滑铲跳接近：0 / 15（加成在冷却中）。

**为什么起跳后还能吃到滑铲加成**（原生滑铲要求着地）：[推断] `Duck` 调起滑时用的是"上一次的地面法线"，起跳后一两条命令里还没更新（NM §3）。没验证。

**窗口的原生规则没完全读通**（M-04）：原生按跳的执行时机是"进度 > 0.5 时下一条命令，否则按键 0.1 s 后"（NM §7），"切断 / superglide"的分界推测是动画里一个"翻过沿"的进度阈值，静态读不出（00-INVENTORY 过时表：账本里"未定"的说法过时，窗口按时间算、约 0.1 s 已确认）。Unity 用实测的剩余时间做窗口。

#### 实现模板

```
// 单位：u、s
onJumpPressInMantle(tau): if tau > 0: pendingExit = true; tauPress = tau
nextCommand: if pendingExit:
    w    = fwd > 0
    pose = min(sprintspeed*msc, approachSpeed)          // 299 或 199.5
    h    = w ? pose : 0
    dirX = hasInput ? wishDir : mantleDir
    r    = T - tauPress
    reduced = r > 0.1025 and duckHeld and r <= 0.1025 + 0.015
    if r > 0.1025 and not reduced: cut(dirX, h); return
    (h, dirX) = surfacePush(h, dirX, +30)               // J-1，第 03 章
    boost = duckHeld and h >= 200 and now - max(slideStartTime, boostTime) >= 2.0
    if reduced and not boost: cut(...); return
    if duckHeld: slideStartTime = now
    if boost: h = min(h + 150*msc, 400*msc)
    if reduced: h *= lerp(385/460, 425/460, (0.1175 - r)/0.015)
    launch(v = dirX*h + (0, 0, sqrt(2*g*56) - g*dt))    // 起跳命令：再扣 ½g·dt 两次 → post V - 1.5 g dt
cut(dirX, h): pos.z = max(pos.z, top); v = dirX*h; airborne
```

Unity 参考实现：`U:…/Abilities/Climb/ClimbAbility.cs`，`ClimbAbility.StepMantle`（`SuperglideMode.Native` 分支）、`NativeExit`、`Cut`、`NativeJumpWindow`；参数 `ClimbParams`：`nativeJumpWindow` 0.1025、`nativeJumpHeight` 56、`superglideNeedsSlideSpeed` true、`superglideExit` `InputWithW`（Fun `Input`）、`nativeExitSpeedFromApproach` true、`slideBoostRearm` 2.0（Reference 在 `MovementConfigs.Reference()` 里设）、`nativeReducedBand`（由 `MovementConfig.superglideReducedBand` 在建身体时设：Reference 0.015、Fun 0；所以导出表里 `preset.Reference.advanced.climb.nativeReducedBand` 显示 0）。+30：`R5MotorV2.SurfacePush`、`R5MotorV2.lastMoveSurface`、`ClimbAbility.WouldHaveProbed`。

#### 验收

- `A2Climb.NativeMantleJumpLeavesAt299AndTheGroundJumpLaw`、`A2Climb.NativeSuperglideWithCrouchLeavesAt460`、`A2Climb.NativeEarlyPressCutsToTheLedgeHeight`。
- `SuperglideM8BTests.SprintSuperglideLeavesAt460AtEveryMeasuredHeight`（90 / 120 / 150 / 180 / 232）、`TheTimeLeftDecidesCutSuperglideOrPlainJump`、`AnAngledApproachLeavesAlongTheInputInReference`、`AWalkApproachLeavesAtTheWalkSpeedWithoutASuperglide`、`NoForwardInputGivesNoBoostFromRest`、`ACrouchPressJustBeforeTheWindowGivesAReducedSuperglideAsInR5`、`WithoutCrouchOrInFunAnEarlyPressStillCuts`、`SuperglideThenLandingSlideKeepsTheSpeedAndTheLurchFiresNatively`。
- `D1M9CTests.ASlideJumpApproachGivesNoSuperglide`、`D1M9CTests.TheSlideBoostClockGatesTheSuperglide`。
- `J1SurfacePushTests.AMantleJumpAfterTouchingTheFaceGainsThirty`、`J1SurfacePushTests.AWalkApproachThatTouchedTheFaceSuperglides`。
- 对照：FEEL §6（窗口中间 112 个片段两边都是 460）；SG 的 102 次 superglide。
- 合格线：窗口中间按键出口 460.000 ± 0.01、竖直 V 按普通跳；切断 / 起跳的分界在剩余 0.1025 s（R5 混合区 0.086–0.12 s 内）；滑铲后 < 2 s 不给加成。
- 已知差别：减量段 R5 是散的（344–429，有时切断），Unity 给平均线；走路接近 402 在 R5 是命令内碰墙时刻决定的（1 / 5），Unity 给多数结果 200（D-30）。

#### 出处

- SG（全部：窗口表、斜向、走路、滑铲跳、FSM 对照）。main
- NM §2.2、§3、§5 M-01 – M-08、§7（第二轮阅读）。main
- `research/rea-native/n11/N11-OPEN-ITEMS.md` §2、§4、§5（+30 推墙，J-1）。main
- `research/phase2-local/m9/r_d1/D1.md`（滑铲后 superglide 的冷却）。main
- A2 §4.1（原生 FSM 关时的 superglide）。main
- FEEL §6.3 C-2 – C-4、§6.4（减量段、时钟用 Unity 的剩余时间）；D-29（被取代）、D-30、D-31、D-32。main
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/Climb/README.md`"两种 superglide"一节。main
- [反编译] `TraversalMove` 0x140a45380（按跳时刻 player+0x2ba8；`automantle_jumpoff_duration` 0.1 s、`automantle_jumpoff_anim_maxfrac` 0.5）；`Jump` 0x140a3b550（+30，常量在 .rdata；表面法线 +0x3630）。

---

## 4.14 S27 翻越加速（mantle boost，游戏里默认）

#### 原理

这是 Apex 第 27 赛季官方加入的"翻越加速"，我们在 S21 上看到它是因为社区 SDK 移植了。它不按时间判定，而按**镜头角度**判定：翻越动画会让镜头先低头再回正，镜头快回正（和准心差不到 1.5°）、并且正在往回走的那一段里按跳，就是成功。屏幕上画一个圆环和准心，镜头回到圈里就是窗口打开，所以玩家能**看着**按，比原生 superglide 好学。成功的出口更高、水平慢一些（388.7 / 367.42），像一个大跳。用户试玩后喜欢这个手感，所以游戏里默认开（D-20）。

#### 规则和公式

1. **判定**（翻越中按跳的那一刻，每次翻越只判一次；翻越第一条命令的按键不算），按顺序：
   1. δ ≥ 0，并且 δ ≤ 上一条命令的 δ（正在回落）；否则失败（dec）；
   2. |δ| < 1.5°；否则失败（angle）；
   3. 动画进度 > 0.5；否则失败（frac）。
   都满足 → BOOST。
2. **δ**（镜头俯仰偏移，°，+ = 向下）：按翻越类别查表（附件 `04-slide-mantle/s27-curves.tsv`，8 条）。查法：时间进度 u = 已过时间 / T → 该类的动画进度 a = interp(anim 表, u) → δ = interp(delta 表, a)，都是 0.05 一格的线性插值。
3. **类别**：按**站姿**时长 T_stand = 0.1728 + 0.0055·rise 分三档（< 0.390 s → h80；< 0.519 s → h100；其余 h120+，分界 = R5 三类时长 0.313 / 0.467 / 0.571 的中点）；翻越开始时蹲着（"蹲着"标志）→ 对应的蹲姿类；蹲姿 h120+ 且原生基础状态是 3 → 短的蹲姿曲线。站姿 h120+ 按视线和墙内法线的夹角在"正对"和"偏 45°"两条曲线之间插值（w = clamp(|夹角| / 45°, 0, 1)）。
4. **结果在翻越结束时给**（不是按键时）：

   | 结果 | 水平（沿翻越方向） | 竖直 |
   |---|---|---|
   | BOOST | 姿态速度 × 1.3 = 299 × 1.3 = 388.7 | √(2·g·90) = 367.42 |
   | 失败 | 299 | √(2·g·56) = 289.83 |
   | 没按 | 299（冲刺）/ 199.525（走路），W 松开 0 | 0 |

   BOOST 后到落地前，lurch / tap-strafe 被禁掉；下一次翻越开始时也清掉。
5. 不看蹲、不看滑铲冷却。跳 + 蹲也一样是 BOOST（R5 实测：S27 打开时拿不到 460）。
6. 圆环：半径 = 1.5° 换算到屏幕（0.5·sin 1.5° / (cos 1.5°·tan(半竖直视场))），画在视野中心；窗口打开变琥珀色，按键后绿 = BOOST、红 = 失败，留 0.25 s。δ 同时加到镜头俯仰上（第 07 章）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 角度阈值 `sweetSpotAngle` | — | 1.5° | — | 实测分界在 1.39（成）和 1.84（败）之间 | [数据] SDK [实测] |
| 最小动画进度 `minValidFrac` | — | 0.5 | — | — | [数据] SDK |
| BOOST 水平倍率 `boostSpeedScale` | — | 1.3 ×（388.7 u/s = 9.873 m/s） | — | 实测 388.700 | [数据] SDK [实测] |
| BOOST 跳高 `boostHeight` | 2.286 m | 90 u（竖直 367.42 u/s = 9.332 m/s） | 1.25 H | 实测 367.42 | [数据] SDK [实测] |
| 类别分界（站姿时长） | — | 0.390 / 0.519 s | — | — | [实测] 中点 |
| 偏角插值满值 `yawCurveFull` | — | 45° | — | 只测了 30°、45° | [实测] |
| 圆环保留 `ringPersist` | — | 0.25 s | — | — | [数据] SDK |

R5 各类的窗口（B1 §4.2、D72 §5，开窗时离结束的剩余时间）：站姿 h80 0.138 s、h100 0.156 s、h120+ 0.144 s（0.125–0.158，36 次）；蹲姿 h80 0.206 s、h100 0.289 s、h120 短 0.16 s、h120 M 0.28 s、h120 长 0.46 s。

**第三种**：`SuperglideMode.SdkFsm` 是 M3 的 SDK 状态机原型（最后 133 ms 按跳即 BOOST，不看角度），只用于研究对照，游戏里不用。

**来源说明**：阈值 1.5°、× 1.3、90 u 是 SDK 作者定的，不保证和官方 S27 一样（B1 §6）。这一项在 DIFF §三"有意和 R5 不一样"。

#### 实现模板

```
// 单位：u、s、°
onJumpPressInMantle(tau):                        // tau >= dt，每次翻越一次
    u  = tau / T
    d  = delta(cls, anim(cls, u), yawOff)
    dp = delta(cls, anim(cls, (tau - dt)/T), yawOff)
    if not (d >= 0 and dp >= d): outcome = FAILED
    elif |d| >= 1.5:          outcome = FAILED
    elif anim(cls, u) <= 0.5: outcome = FAILED
    else:                     outcome = BOOST
onMantleEnd():
    if outcome == BOOST:  v = mdir*(299*1.3) + (0,0,sqrt(2*g*90)); lurchSuppressed = true
    elif outcome == FAILED: v = mdir*299 + (0,0,sqrt(2*g*56))
    else: §4.11 自然结束
    pos = target; airborne (下一条命令自己扣重力)
```

Unity 参考实现：`U:…/MantleBoostS27.cs`（`MantleBoostS27Params`、`MantleCurveClass`、`MantleBoostS27.Gate` / `Delta` / `Anim` / `ClassifyByTime` / `DeltaAtTime`）；`U:…/MantleBoost.cs`（`MantleBoostParams`、`MantleBoost.ExitVelocity`，出口和 SDK FSM 共用）；`ClimbAbility.StepMantle`（`SuperglideMode.MantleBoostS27` 分支）、`FinishMantle`、`S27Delta` / `S27Anim`。游戏开关：`HSD-Unity: Assets/HSD/Game/Runtime/PracticeGame.cs` `PracticeGame.ApplyMantleBoostChoice`，菜单 "Mantle boost (B1, S27 port)"，PlayerPrefs `hsd.b1.mantleboost`（默认开，只改正在玩的身体；配置、测试、回放都是原生）。

#### 验收

- `MantleBoostS27Tests.TheWindowOpensWhereR5OpensIt`、`TheStandingWindowIsTheLast0_13To0_16Seconds`、`TheClassComesFromTheRiseAndTheCrouch`、`TheClassFollowsTheMantleTiming`、`TheWindowInSecondsIsR5sPerClass`、`TheLiveConfigsKeepTheStandingWindowInTheR5Range`、`TheLiveConfigsKeepTheCrouchedWindowInTheR5Range`、`ACrouchedMantleTakesR5sCrouchedTime`。
- `A2Climb.S27ModeBoostsInsideTheAngleWindowOnly`（H232：窗口内 388.7 / 367.41；早按失败 299 / 289.82）、`A2Climb.S27WindowSitsWhereTheCurveSaysOnTheLiveMantle`。
- `Cam2CameraTests.TheTraversalPitchFadesInFromTheMantleStart`（镜头淡入只动镜头，判定读的曲线不变）。
- 合格线：每一类窗口秒数在 R5 ± 0.02 s 以内；站姿窗口 0.09–0.18 s，蹲姿 0.15–0.50 s（守护测试，调参以后也要过）。

#### 出处

- B1 §0 – §10（判定规则、曲线、窗口、Unity 复刻、调参不失效、蹲姿时长）。main
- D72 §5（蹲姿各类的 S27 窗口）、§9.3。main
- `research/b1/data/curve-table.csv`（δ 曲线）、`anim-time.csv`（时间 → 动画进度）、`classes.csv`（各类时长）。main
- D-20、D-32；DIFF §三。main
- [反编译] 无：`r5apex_dx12.exe` 里没有 mantle boost 字符串，规则来自 SDK `game/client/mantle_boost.cpp`、`mantle_boost_rui.cpp`（本地 `L:research-src/`，不在仓库）；原生只提供 `GetTraversalViewPosition` 0x1406668a0。
