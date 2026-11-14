# 07 镜头：事件型、持续型、组合规则、力度规律

hb-ch07 写（2026-11-14），分支 `handbook/ch07`，还没合并。数值表的逐项版本在 `tables/camera-events.tsv`（hb-tables 写，事件名和本章一样，见 §0.5）；本章的附件在 [07-camera/](07-camera/)。

## 白话说明

这一章讲第一人称镜头**怎么动**：落地时画面往下点一下、起跳时轻轻一沉、滑铲时眼睛降下去、视角斜着滑时画面往一边歪、挂在钩爪上时画面朝钩点那边倾……每一种怎么触发、动多少、多久回来，以及好几种同时发生时怎么加在一起。

读完能做出三样东西：

1. **一套共用的"镜头物理"**：两组弹簧（所有一次性的镜头动作都往里"踢一脚"）、几个线性进度（眼高、FOV）、一个追目标的平滑器（绳子横滚）。整章的效果都建在这三样上面。
2. **每一个具体效果**：事件型（起跳、落地等，§2）和持续型（眼高、倾斜、晃动、FOV，§3），每一项都给出触发条件、公式、数值和验收。
3. **组合规则和设计方法**（§4、§5）：每帧按什么顺序拼、同时来几个怎么加、为什么"瞄准"和"画面"分开存，以及以后自己设计一个新镜头效果时照什么步骤、力度取多大。

这套规则来自 Apex（本地 R5 构建）的反编译和逐帧实测，HSD 的 Unity 原生镜头（`NativeCameraFeedback`）已经按它实现并逐项对照过。两条总的设计理念先记住：

- **镜头只转不移；持续的克制，一次性的响亮**（P2）。画面的位置永远是眼睛的位置，眼睛只随身体姿态（蹲、冲刺、滑索）移动；持续状态几乎不动镜头（跑多快 FOV 都不变），一次性事件可以很大（900 u 高处落地画面往下点 30–44°），因为它很快结束，而且告诉你"这一下有多重"。
- **瞄准是真值**（P1、T3）。所有镜头效果都只改"画面"，不改"瞄准"。准星指向哪里，鼠标说了算。

**和别的章的分界**：身体怎么移动在 02–06 章，本章只读身体的状态，从不写回身体；枪的后坐图案、扩散、开镜动画在 09 章，本章只讲后坐**对画面**的那一部分；枪模和手臂的摆动在 08 章；防晕选项、屏幕后处理、声音同步、第三人称切换都没研究，只列在 §7。

### 本章出处缩写

| 缩写 | 路径（研究仓库根目录） | 在哪 |
|---|---|---|
| DP | `research/DESIGN-PHILOSOPHY.md`（P1–P9、T1–T9、§6 镜头规范、§9 新东西怎么做） | main；#122 大改 P1、T2、T3、§6.2、§6.5（分支 `r5gap/gun`）；#114 改 §6.6（分支 `research/philosophy-skill-sync`） |
| CR | `research/rea-native/camera/CAMERA-REFERENCE.md` | main（**§3.1 的站立眼高 64 过时，是 70**） |
| CI | `research/rea-native/camera/CAMERA-INVENTORY.md`（CAM-01 – 23） | main |
| C3 | `research/rea-native/camera/C3-CAPTURE.md` | main |
| NC | `research/rea-native/subsystems/N2-C-CAMERA.md` | main |
| CAM2 | `research/rea-native/cam2/CAM2-CAMERA.md` | main（§5 第 6 条的更正在 #93） |
| N10 | `research/rea-native/n10/N10-CAMERA.md` | main |
| DIFF | `R5-DIFF-ARCHIVE.md`（K-1 – K-8、C-12、CAM2、FND、D-75） | main |
| DEC | `DECISIONS.md`（D-xx） | main |
| RV | `research/combat/RECOIL-VIEW.md` | PR #93，还没合并（分支 `combat/recoil-view-measure`） |
| FG | `research/combat/gun-measure/F-GAPS.md` | PR #122，还没合并（分支 `r5gap/gun`） |
| EM | `research/combat/gun-measure/E-MOUSE.md` | PR #122，还没合并 |
| TPC | `tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md` | main |
| T3W | `tf2/wallrun/T3-REPORT.md`、`tf2/wallrun/WALLRUN-B-SPEC.md` §8 | main |
| B1 | `research/b1/B1-MANTLE-BOOST.md` §4（翻越镜头曲线） | main |
| D72 | `research/phase2-local/D72-REPORT.md` §8–§9 | main |
| SKILL | `HSD-Unity: .claude/skills/fps-camera-design/`（`SKILL.md` + `references/`） | HSD-Unity main（**还写着 DP 在 PR #94；子弹公式缺 punch1 和 drift**，以 FG 为准） |

Unity 路径：`HSD-Unity: Assets/HSD/Game/Runtime/Camera/Native/NativeCamera.cs` 简写成 **NC.cs**（类 `NativeCameraParams`、`NativeCameraFeedback`、`PunchAxis`、`PerlinNoise`），`HSD-Unity: Assets/HSD/R5Replay/Runtime/NativeEyeHeight.cs` 简写成 **Eye.cs**，`R5SharedRandom.cs`、`MantleBoostS27.cs` 在同一目录。测试在 `HSD-Unity: Assets/HSD/Game/Tests/Editor/`。以上都在 HSD-Unity main（`17260f2`）。

---

## 0. 约定

### 0.1 单位和符号

- 长度 u，`[m]` = u × 0.0254（[01 §2](01-units-body.md)）。参考身高 H = 72 u。
- **角度一律度（°），时间一律秒（s），不换算**。镜头里的大部分量都是角度、角速度（°/s）、时间、比例，所以三列表里很多行 `[m]` 和身高比例写"—"。
- 弹簧常数作用在角度上：刚度 k 单位 1/s²，阻尼 c 单位 1/s，不换算（[01 §2.2](01-units-body.md)）。
- **符号用 Source 的约定**（R5 和 Unity 原生镜头内部都用它）：俯仰 + = 向下看；横滚 + = 向右倾（右边低）；偏航向右转 = 偏航变小。Unity 的 `CameraPose.roll` + = 向左倾，所以输出时 **Unity 横滚 = −Source 横滚，Unity 偏航 kick = −Source 偏航**。
- FOV：R5 的 FOV 数是 **4:3 画面的水平 FOV**；Unity `Camera.fieldOfView` 是竖直 FOV。两者换算见 §3.10。

### 0.2 时间网格

- 身体模拟每秒 120 条命令（dt = 1/120 s）。**镜头的所有状态也只在命令上更新**（每条命令跑一次 §4.1 的 `Observe`），积分用精确解或按 dt 的线性步，所以和渲染帧率无关。
- 渲染帧在最近两条命令的镜头状态之间**线性插值**（§4.1 `Render`）。
- 事件"发生在哪条命令"以身体的标志为准：落地 = 这条命令把身体从空中变成着地；起跳 = 这条命令执行了原生地面跳；等等（每项的规则段写清楚）。

### 0.3 三种角（P1、T3）

镜头里同时有三种角，分开存，任何一种都不写回别的：

| 角 | 是什么 | 谁改它 |
|---|---|---|
| 瞄准角 `aim`（R5 叫 `eang`） | 鼠标转出来的方向，准星、钩爪射线、lurch、跳板方向都用它 | 只有鼠标（开枪时鼠标先抵消反向的武器 punch，见 §2.10） |
| 画面角 | 屏幕实际朝向 = 瞄准 + 本章所有效果 | 本章 |
| 子弹角 | 子弹飞的方向 | 09 章（画面角里除了 (1 − fraction) 以外的全部，§4.3） |

### 0.4 依据标签

沿用 DP §2.1：[实测] [反编译] [数据] [算] [推断] [设计]，TF2 来源写 [TF2 实测] [TF2 数据]。"R5"都指本地混合构建（S21 客户端 + S3 dedi + SDK）。镜头属于客户端，DP §10.3 判断客户端现象可以当正版学。

### 0.5 事件名

本章和 `tables/camera-events.tsv` 共用这些名字：

| 类 | 名字 |
|---|---|
| 事件型（§2） | `jump` 起跳、`double_jump` 二段跳、`land` 落地、`zip_detach` 下滑索、`mantle` 翻越（开始 → 结束）、`slide_start` 滑铲开始、`wall_kick` 蹬墙跳、`wallrun_start` / `wallrun_timeout` 跑墙开始 / 超时、`hit` 受击、`explosion` 爆炸、`fire` 开枪后坐、`melee` 近战、`ability` 放技能、`titan_embark` / `titan_eject` 泰坦登机 / 弹射 |
| 持续型（§3） | `eye_height` 眼高（站 / 蹲 / 滑）、`sprint_eye` 冲刺眼低、`step_bob` 跑步晃动、`view_drift` 站立漂移、`ads_drift` 开镜漂移、`weapon_sway` 枪的摆动、`slide_tilt` 滑铲倾斜、`sprint_tilt` 冲刺转向倾斜、`wallrun_tilt` 跑墙倾斜、`rope_roll` 钩爪 / 滑索横滚、`zip_eye_offset` 滑索眼睛偏移、`slide_fov` 滑铲 FOV、`ads_fov` 开镜 FOV |

---

## 1. 三个基础件

整章的效果都建在这三样上：**punch 弹簧**（一次性事件）、**线性进度 + 读者曲线**（定时过渡）、**SmoothCD**（追一个会动的目标）。外加一个**确定性随机数**，让同一条命令的随机 kick 每次都一样。

### 1.1 punch 弹簧（所有事件 kick 共用）

#### 原理

所有一次性的镜头动作（起跳、落地、二段跳、下滑索……）都不是"播一段动画"，而是**往同一组弹簧上踢一脚**：给弹簧一个角速度，弹簧自己把画面推出去再拉回来。这样做有三个好处：

1. 形状统一：所有事件都是"很快到峰、回弹一次、一秒内回正"，玩家学一次就懂。
2. 力度只是一个数：踢多大，画面就偏多大，事件之间可以直接比轻重。
3. 组合自动成立：两个事件同时来，就是踢两脚，弹簧是线性的，结果就是两个响应相加，不需要写"谁优先"（P8）。

弹簧是**欠阻尼**的：到峰值后会往反方向回弹约 12 %。这是被"打"一下的感觉；追目标的东西（§1.3）才用不回弹的临界阻尼（T9）。

#### 规则和公式

1. 有**两组**弹簧，每组三个轴（俯仰、偏航、横滚），每个轴存"角度 x"和"角速度 v"。
2. 每条命令每个轴按精确解推进一步（和帧率无关）：x'' = −k·x − c·v。
3. 一个事件 kick = 给第一组的角速度加冲量 J（°/s），**同时给第二组加 0.2 × J**。不直接改角度。
4. 画面上的 punch = 第一组角度 + 第二组角度（拿枪时第二组 × (1 − fraction)，见 §2.10）。
5. 冲量的写法统一为 `(基础 + 幅度 × r) × 20`，r ∈ [−0.5, 0.5]（§1.4）。"× 20"是 R5 代码里的固定系数，基础值就是"这一下有多重"（§4.5）。
6. 接近 0 时归零：DP T8 记 R5 的弹簧在 |x|² + |v|² < 0.001 时直接归零（武器弹簧实测过，RV §2.1）。**Unity 原生镜头的 `PunchAxis` 没有做这一步**（差别 < 0.03°，见 `_notes/hb-ch07.md`）。

冲量响应（一个轴，初速度 v₀，起点 x = 0）：

```
α = c/2 = 4.5 /s，  ω_d = √(k − α²) = 6.690 rad/s
x(t) = v₀ / ω_d · e^(−α t) · sin(ω_d t)
峰值时间 t_p = atan(ω_d / α) / ω_d = 0.146 s，  峰值 = 0.0642 · v₀
过零 π / ω_d = 0.470 s，  反向峰 0.616 s、为正峰的 −12 %
```

两组合计（第二组 0.2 倍）：**画面峰值 = 0.0771 × 俯仰冲量**，约 0.146 s 到峰（120 Hz 离散时 0.150 s、0.0770）。逐命令的单位冲量响应在 [07-camera/punch-response.tsv](07-camera/punch-response.tsv)。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 刚度 k（`viewpunch_base_springConstant` XYZ） | — | 65 /s² | — | 不改（所有事件共用；新事件不给自己的 k） | [反编译] [实测] |
| 阻尼 c（`viewpunch_base_springDamping` XYZ） | — | 9 /s | — | 不改 | [反编译] [实测] |
| 阻尼比 ζ = c / (2√k) | — | 0.558 | — | — | [算] |
| 第二组倍数 | — | 0.2 × | — | — | [反编译] [实测] |
| 冲量系数 | — | 20 × | — | — | [反编译] |
| 峰值时间 | — | 0.146 s | — | 实测 0.15–0.17 s | [算] [实测] |
| 过零 | — | 0.470 s | — | 实测 0.46–0.58 s | [算] [实测] |
| 反向峰 | — | −12 %，0.616 s | — | — | [算] [实测] |
| 两组合计峰值 / 俯仰冲量 | — | 0.0771 °/(°/s) | — | — | [算]，公式实测过 |

#### 实现模板

```
// 单位：°、°/s、s
struct Axis { x, v }
step(axis, k, c, dt):                       // 精确解，欠阻尼分支
    α = c/2; ωd = sqrt(k − α²); e = exp(−α dt)
    cs = cos(ωd dt); sn = sin(ωd dt)
    x' = e·(x·cs + (v + α x)/ωd · sn)
    v' = e·(v·cs − (α v + k x)/ωd · sn)
    (x, v) = (x', v')
    // R5：if x² + v² < 0.001: x = v = 0

kick(Jpitch, Jyaw, Jroll):                   // 一个事件
    p1.pitch.v += Jpitch; p1.yaw.v += Jyaw; p1.roll.v += Jroll
    p2.pitch.v += 0.2·Jpitch; p2.yaw.v += 0.2·Jyaw; p2.roll.v += 0.2·Jroll
```

每条命令里先把 6 个轴各 `step` 一次，**再**加这条命令上的所有 kick（参考实现的顺序；所以事件那条命令上角度还是 0，下一条命令才开始动）。

Unity 参考实现：NC.cs `PunchAxis.Step`（精确解，k、c 来自 `NativeCameraParams.springK` 65、`springC` 9、`secondSpring` 0.2、`kickGain` 20）；`NativeCameraFeedback` 的 `punchPitch / punchYaw / punchRoll`（第一组）和 `punch2Pitch / punch2Yaw / punch2Roll`（第二组）。

#### 验收

- `NativeCameraTests.PunchSpringShapeMatchesC3`：峰值时间、过零、回弹形状。
- `NativeCameraTests.PunchAxisIsFrameRateIndependent`：不同 dt 推进同一段时间，结果相同。
- 合格线：单位冲量的两组合计峰值 0.0771 ± 0.0005，峰值时间 0.146 ± 0.01 s，过零 0.47 ± 0.01 s，反向峰 −12 % ± 1 %（对 [07-camera/punch-response.tsv](07-camera/punch-response.tsv)）。

#### 出处

- NC §1、§8：两组弹簧、k 65 c 9、"所有 punch 都是给角速度加量"。main
- CR §3.2：冲量响应公式和数值表；C3 §1–§2：0.15–0.17 s 到峰、0.46–0.58 s 过零。main
- DP T2、T8（#122 版）：两组弹簧进画面 / 子弹的规则、归零门槛。PR #122，还没合并
- [反编译] punch 弹簧 0x140a34170；第一组 player+0x2430 / +0x243c，第二组 +0x2448 / +0x2454；读 punch 0x140af1ed0。

### 1.2 线性进度 + 读者曲线（定时过渡）

#### 原理

所有"从一个状态过渡到另一个状态"的镜头变化（蹲下眼高、滑铲 FOV、冲刺眼低、翻越镜头淡入）都用同一个结构：一个按时间线性走的 0..1 进度，谁要用它，谁自己在读的时候加曲线。这样可以随时中断、反向（从当前值接着往回走，不重新开始），而且多个读者自动同步（T1）。

#### 规则和公式

```
进度 f：目标 1 时 f += dt / T_in，目标 0 时 f −= dt / T_out，夹在 [0, 1]
读者：y = a + (b − a) · C(f)
```

本章用到的读者曲线：

| 进度 | 读者 | 曲线 C | 位置 |
|---|---|---|---|
| 下蹲比例 | 眼高 | smoothstep `3f² − 2f³` | §3.1 |
| 冲刺比例 | 眼高下沉 | `sin(f·π/2)`，前面先等一段（T5） | §3.1 |
| 滑铲 FOV 比例 | FOV | 线性（反例） | §3.10 |
| 开镜 `zf` | FOV | smoothstep | §3.10、09 章 |
| 翻越开始后的时间 | 翻越镜头淡入 | smoothstep（t / 0.15 s） | §2.5 |

**不要给进度本身加缓动**，曲线只加在读者上（DP §9.5 把"给 `zf` 加 ease-in"判为不符合）。

#### 实现模板

```
moveToward(f, target, step) = f < target ? min(target, f + step) : max(target, f − step)
smoothstep(x) = clamp01(x)² · (3 − 2·clamp01(x))
```

Unity：NC.cs 和 Eye.cs 各有 `MoveToward`、`Smoothstep`。

#### 验收

由用到它的各项验收（§2.5、§3.1、§3.10）。共同检查：中途反向时输出连续（没有跳变）。

#### 出处

- DP T1、T5：线性进度 + 读者曲线；"等一段 + 线性走完"。main（#122 改了表里的灵敏度一行）

### 1.3 SmoothCD（追一个会动的目标）

#### 原理

有些镜头量是"跟着一个一直在变的目标走"，比如钩爪横滚跟着钩点相对视线的位置、滑索眼睛偏移跟着噪声。跟目标的东西**不能回弹**（目标在动，回弹会像晃），所以用临界阻尼的平滑器，R5 叫 SmoothCD。它同时存"值"和"速度"，所以目标切换时（钩爪换到滑索）输出连续（T9）。

#### 规则和公式

```
x = ω·dt;  e = 1 / (1 + x + 0.48x² + 0.235x³)
c = value − target
tmp = (rate + ω·c)·dt
rate  = (rate − ω·tmp)·e
value = target + (c + tmp)·e
if |target| < snap and |value| < snap: value = 0       // rate 不动
```

这是临界阻尼二阶系统的常用近似（指数用多项式近似）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 绳子横滚 ω | — | 6.6667 /s（float 20/3） | — | — | [反编译] [实测] |
| 绳子横滚归零门槛 snap | — | 0.001 ° | — | — | [反编译] |
| 滑索眼睛偏移 ω | — | 4 /s | — | — | [反编译] [实测] |

#### 实现模板

Unity：NC.cs `NativeCameraFeedback.SmoothCD(ref value, ref rate, target, omega, dt, snap)`。

#### 验收

`F7CameraTests.SmoothCDIsTheNativeCriticalSpring`：阶跃不过冲、和原生公式逐步一致。

#### 出处

- DIFF C-12：共用一个 SmoothCD（ω 6.667）、门槛 0.001；N12 实测钩爪 rms 0.24–0.45°。main
- CAM2 §4.2：滑索偏移 ω 4。main
- [反编译] `View_CalcRoll` 0x140afc480（状态 player+0x36d4 / +0x36d8），常数 0x1417f88f0（20/3）、0x1417f8380（0.001）。

### 1.4 确定性随机数

#### 原理

kick 里有随机项（同样高度落地，每次画面点头的深浅略有不同），但随机数**由命令号决定**：同一条命令重放时随机数一样，所以回放、联网、对照都能逐次重现（T7）。

#### 规则和公式

- 每个随机 kick 用三个 r ∈ [−0.5, 0.5]（俯仰、偏航、横滚各一个），每个轴一个"盐"，r = f(命令号, 盐)。
- 要和 R5 逐次一样，用 R5 的算法（Unity `R5SharedRandom`）：
  1. base = MD5(命令号的 4 字节小端) 的第 6–9 字节当 uint32，& 0x7fffffff；
  2. seed = Jenkins one-at-a-time 混合（base 的 8 字节（高 4 字节为 0）+ 盐的 4 字节），末尾 `h *= 9; h ^= h >> 11; h *= 0x8001`；
  3. next = 48271 · seed mod (2³¹ − 1)（Park–Miller），r = −0.5 + min(next / 2³¹, 0.99999988)（单精度）。
- 只要求"可重现、均匀"的新游戏，可以换成任何按命令号的哈希（Unity 旧版 `NativeCameraFeedback.Random`，SplitMix）；但这样就对不上 R5 的逐次录像。

| 事件 | 盐（俯仰 / 偏航 / 横滚） | 取哪条命令 |
|---|---|---|
| 落地 `land` | 0x76704c58 / 59 / 5a（'vpL X/Y/Z'） | 落地那条 |
| 起跳 `jump` | 0x76704a58 / 59 / 5a（'vpJ X/Y/Z'） | 起跳那条 |
| 二段跳 `double_jump` | 0x76444a58 / 59 / 5a（'vDJ X/Y/Z'） | 二段跳那条 |
| 下滑索 `zip_detach` | 和起跳同一组盐 | **下绳后的那一条**（冲量加在下绳那条） |

#### 实现模板

Unity：`HSD-Unity: Assets/HSD/R5Replay/Runtime/R5SharedRandom.cs`，`R5SharedRandom.Kick(command, salt)`；开关 `NativeCameraParams.r5Random`（false = 旧哈希）。

#### 验收

- DIFF K-1 / K-2：用 R5 的命令号重放，落地俯仰峰值和横滚 32 / 34 次一致。
- 回放基线逐字节不变（11 章）。

#### 出处

- DIFF K-1 / K-2，D-35：命令号 MD5 → 种子混合 → 线性同余，Frida 逐个对上（8 / 8 base、27 / 27 seed）。main
- [反编译] 种子混合 0x140ad55b0，均匀流 0x14059c5f0 / 0x14059c670。

---

## 2. 事件型

所有移动事件的 kick 汇总（第一组弹簧的冲量；第二组 × 0.2；画面峰值 ≈ 0.0771 × 俯仰冲量）：

| 事件 | 俯仰冲量（°/s） | 偏航 | 横滚 | 画面俯仰峰值 | 状态 |
|---|---|---|---|---|---|
| `jump` | (2 + r)·20 | r·20 | (0.9 + 0.5r)·20 | 2.3–3.9° | [反编译] [实测] |
| `double_jump` | (4.5 + r)·20 | r·20 | 2r·20 | 6.2–7.7° | [反编译]，没有录像 |
| `land` | s·(2 + 0.75r)·20 | 0 | s·r·20 | 0.89–44° | [反编译] [实测] |
| `zip_detach` | (10 + 3r)·20 | 10r·20 | 10r·20 | 14–18° | [反编译] [实测] |

### 2.1 起跳 `jump`（含滑铲跳）

#### 原理

起跳时画面轻轻往下沉一下（约 3°，0.15 s 到底，0.5 s 回来），同时略向右倾。这是"蹬地"的感觉，和跳多高、飞多久无关：短跳和从高台跳下去，起跳那一下一样。它是"平常动作"的力度基准（基础值 2，§4.5）。

#### 规则和公式

1. 触发：这条命令执行了**原生地面跳**（地面跳、滑铲跳）。跳板、弹射、击退等"发射"不触发；二段跳走 §2.2。
2. 冲量：俯仰 (2 + r₁)·20，偏航 r₂·20，横滚 (0.9 + 0.5·r₃)·20，第二组 × 0.2。
3. 横滚基础是正的，所以**总是向右倾**（1.0–1.8°）。
4. 和起跳速度、滞空时间无关。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 俯仰基础 | — | 2（× 20 = 40 °/s） | — | 随机 ±1（× 20） | [反编译] |
| 俯仰随机幅度 | — | 1 × r | — | — | [反编译] |
| 偏航随机幅度 | — | 1 × r | — | — | [反编译] |
| 横滚基础 / 随机 | — | 0.9 / 0.5 × r | — | — | [反编译] |
| 画面俯仰峰值 | — | 2.3–3.9 °，0.10–0.15 s | — | R5 实测 2.1–3.9° | [算] [实测] |
| 画面横滚峰值 | — | 1.0–1.8 °（向右） | — | 实测 1.0–1.6° | [算] [实测] |

#### 实现模板

```
if body.jumpedThisCommand:          // 原生地面跳 / 滑铲跳；不含 launch
    r1,r2,r3 = rand(cmd, SALT_JUMP)
    kick((2 + r1)·20, r2·20, (0.9 + 0.5·r3)·20)
```

Unity：NC.cs `Observe` 里 `p.jumpPunch && m.jumped`；`R5MotorV2.jumped`（只给镜头读）；参数 `jumpPitchBase` 2、`jumpPitchRandom` 1、`jumpYawRandom` 1、`jumpRollBase` 0.9、`jumpRollRandom` 0.5；开关 `NativeCameraParams.jumpPunch`（false = 改前没有起跳镜头）。

#### 验收

- `Cam2CameraTests.JumpAddsTheNativeImpulseToBothPunchSprings`、`JumpPunchShape`。
- 对照：CAM2_C 15 个片段，R5 / Unity 起跳俯仰峰值逐个差 ≤ 0.15°（例：原地跳 2.65 / 2.67、3.17 / 3.20）；镜头对照 K-5 指标 155 / 180（旧片段）、45 / 45（CAM2_C）。
- 对齐注意：R5 的镜头时间线比 usercmd 早约 0.04 s，指标要用各自镜头上的离地帧当起点和基准（CAM2 §6）。

#### 出处

- CAM2 §2：原生函数、Frida 拆分、对照数字；DIFF CAM2 K-5；D-53。main
- [反编译] `0x140a349c0`（由原生跳 `0x140a3b550` 调用）；写入第一组 player+0x243c / +0x2440 / +0x2444，第二组 +0x2454 / 58 / 5c。

### 2.2 二段跳 `double_jump`

#### 原理

空中再跳一次是"主动超出常规"的动作，画面往下沉的比普通起跳重一倍多（约 7°）。基础值 4.5 是本章力度规律的中档（§4.5）。

#### 规则和公式

1. 触发：一次二段跳（HSD 的三种：Octane 跳板二段跳、M7 二段跳、TF2 规则二段跳都用这一条，D-68）。
2. 冲量：俯仰 (4.5 + r₁)·20，偏航 r₂·20，横滚 2·r₃·20，第二组 × 0.2。横滚没有基础，左右随机。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 俯仰基础 / 随机 | — | 4.5 / 1 × r | — | — | [反编译] |
| 偏航随机 | — | 1 × r | — | — | [反编译] |
| 横滚随机 | — | 2 × r | — | — | [反编译] |
| 画面俯仰峰值 | — | 6.2–7.7 °，约 0.13–0.15 s | — | **没有 R5 录像** | [算] |

#### 实现模板

```
if ability.doubleJumpedThisCommand:
    r = rand(cmd, SALT_DOUBLE_JUMP)
    kick((4.5 + r1)·20, r2·20, 2·r3·20)
```

Unity：NC.cs `p.doubleJumpPunch`（读 `PadDoubleJumpAbility.padJumps`、`DoubleJumpAbility.airJumps` 的计数变化，只读）；参数 `doubleJumpPitchBase` 4.5 等。关掉 = F7 设计的 1.2° 小凸起（只在跳板二段跳，临界阻尼，`padJumpKickPitch` 1.2、`padJumpKickPeakTime` 0.10）。

#### 验收

- `FndCameraTests.AirJumpAddsTheNativeDoubleJumpImpulse`、`PadDoubleJumpUsesTheNativePunch`、`PreFndAirJumpHasNoPunch`。
- 只对了原生公式，没有 R5 录像（B07-1）。

#### 出处

- CAM2 §2.1、§7；DIFF FND；D-68（取代 D-43 的 1.2°）。main
- [反编译] `0x140a34c00`（`DoubleJump_Rumble`，原生跳的空中分支）。

### 2.3 落地 `land`（逐帧公式）

#### 原理

落地是镜头里最重要的反馈：画面往下点一下，**点多深告诉你摔得多重**。原地跳落地只有 2°，几乎察觉不到；从 400 u 高处落下是 20°；900 u 是 30–44°，非常明显，但 0.15 s 就到底、半秒回正，所以不会让人晕（P2：一次性的可以响亮）。

强度是分段线性的：低于"10 英尺落差的速度"时按比例变小；10 到 70 英尺之间从 1 倍涨到 12 倍；更高封顶 12 倍。所以小台阶几乎没有，中等落差涨得很快，太高也不会无限大。

#### 规则和公式

1. **触发**：这条命令身体从空中变成着地（落地）。下面这些**不是**落地、不触发：翻越结束（翻越把人放到台面上，CAM2 §3：8 / 8 没有落地 kick）；从没离地（v = 0）。
2. **下落速度 v**：落地**前一条命令**结束时的向下速度，v = max(0, −vz)。
3. **强度 s**（g = 750 u/s²，两个键是英尺，先 × 12 到 u）：

   ```
   v_min = √(2g · 12 · FallDistMin)   = √(2·750·120) = 424.26 u/s
   v_max = √(2g · 12 · FallDistMax)   = √(2·750·840) = 1122.50 u/s
   s = v / v_min                                   (v < v_min)
   s = 1 + (MaxScale − 1)·(v − v_min)/(v_max − v_min)   (v_min ≤ v ≤ v_max)
   s = MaxScale = 12                               (v > v_max)
   ```

4. **在水里落地**：s × 0.2（R5 有，HSD 没有水，没做）。**按住下蹲落地不减**（早期推断错了，C3 §3）。
5. **冲量**：俯仰 s·(2 + 0.75·r₁)·20，偏航 0，横滚 s·r₃·20；第二组 × 0.2。横滚左右随机，最大 s·0.5·20。
6. 落地那条命令同时有起跳（落地马上再跳）：两个 kick 都加（§4.2）。

**逐帧曲线**：画面俯仰（向下）= J · R(t)，J = s·(2 + 0.75·r₁)·20，R(t) 是 §1.1 两组弹簧合计的单位冲量响应：

```
R(t) = (1 + 0.2) · e^(−4.5 t) · sin(6.690 t) / 6.690      // t 从落地那条命令算，单位 s
```

离散版（120 Hz）逐命令的值在 [07-camera/punch-response.tsv](07-camera/punch-response.tsv) 的 `angle_both_deg` 列。例：400 u 落差（v = 769 u/s，s = 6.431），r₁ = 0，J = 257.2 °/s：

| 落地后 t（s） | 0 | 0.05 | 0.10 | 0.15 | 0.20 | 0.30 | 0.40 | 0.475 | 0.55 | 0.617 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 画面俯仰（°，+ 向下） | 0 | 12.09 | 18.24 | **19.81** | 18.25 | 10.84 | 3.43 | −0.20 | −1.99 | **−2.39** | −1.98 | −1.01 | −0.21 | +0.20 |

形状：0.15 s 到峰，0.47 s 过零，0.62 s 反向到峰值的 −12 %（往上抬约 2.4°），约 1 s 回正（之后还有 < 1.5 % 的第二次小回摆）。

各落差的峰值（[07-camera/landing-kick.tsv](07-camera/landing-kick.tsv)）：

| 场景 | v [m/s] | v [u/s] | s | 画面俯仰峰值（r₁ = −0.5 / 0 / +0.5） | 横滚最大 | R5 实测 |
|---|---|---|---|---|---|---|
| 小台阶 | 3.81 | 150 | 0.354 | 0.89 / 1.09 / 1.29° | 0.27° | — |
| 原地跳落地 | 7.01 | 276 | 0.651 | 1.63 / 2.00 / 2.38° | 0.50° | 1.85–2.54° |
| 96 u 落差 | 9.50 | 374 | 0.882 | 2.21 / 2.72 / 3.23° | 0.68° | 2.21–2.79° |
| 160 u 落差 | 12.22 | 481 | 1.894 | 4.74 / 5.83 / 6.93° | 1.46° | 6.07–6.82° |
| 400 u 落差 | 19.53 | 769 | 6.431 | 16.1 / 19.8 / 23.5° | 4.95° | 17.9–21.4° |
| 900 u 落差 | 29.36 | 1156 | 12（封顶） | 30.0 / 37.0 / 43.9° | 9.25° | 33.7–43.3° |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力 g | 19.05 m/s² | 750 u/s² | 10.42 H/s² | — | [数据] |
| `viewkickFallDistMin` | 3.048 m | 10 ft = 120 u | 1.667 H | — | [数据]（N4-A 读回） |
| `viewkickFallDistMax` | 21.34 m | 70 ft = 840 u | 11.67 H | — | [数据] |
| v_min | 10.78 m/s | 424.26 u/s | 5.893 H/s | — | [算] |
| v_max | 28.51 m/s | 1122.50 u/s | 15.59 H/s | — | [算] |
| `viewkickFallDistMaxScale` | — | 12 × | — | — | [数据] |
| 俯仰基础 / 随机 | — | 2 / 0.75 × r | — | — | [反编译] |
| 横滚随机 | — | 1 × r（× s） | — | — | [反编译] |
| 水中倍数 | — | 0.2 × | — | 没实测 | [反编译] |

#### 实现模板

```
// 单位：u、u/s、°、°/s；在 Observe 里，弹簧 step 之后
if body.landedThisCommand and sameBody:
    v = max(0, −prevCommandVelocity.z)
    s = kickScale(v)                         // 上面的分段式
    if inWater: s *= 0.2
    if s > 0:
        r1, _, r3 = rand(cmd, SALT_LAND)
        kick(s·(2 + 0.75·r1)·20, 0, s·r3·20)
```

要点：v 用**上一条命令**的速度（这条命令的速度已经被落地清掉）；`sameBody`（身体刚重建、传送后第一条命令）不加 kick。

Unity：NC.cs `NativeCameraParams.KickScale(v)`、`KickVMin` / `KickVMax`（`kickFallDistMinFt` 10、`kickFallDistMaxFt` 70、`kickMaxScale` 12、`gravity` 750、`kickPitchBase` 2、`kickPitchRandom` 0.75、`kickGain` 20）；`Observe` 里 `m.landed && sameBody` 那一段。

#### 验收

- `NativeCameraTests.LandingKickScaleMatchesTheC3Table`（s 曲线对 C3 表）、`DropLandingKickInTheGame`（游戏里 400 u 落差）。
- `Cam2CameraTests.LandingKickAndJumpPunchAdd`（落地马上再跳相加）。
- 对照：C3 每个高度的实测峰值都落在 r ∈ [−0.5, 0.5] 的预言范围内（上表最后一列）；用 R5 命令号重放时 32 / 34 次峰值一致（DIFF K-1）。
- 合格线：v 给定、r 给定时峰值和公式差 < 1 %；实测对照落在随机范围内。
- 已知例外：滑铲跳落地 CAM2_C 镜头日志里 R5 只有 1.1–1.7°，是片段撞墙造成的记录问题，不是差别（D-71 更正）。

#### 出处

- NC §2、§7、§8；CR §2.1、§3.2；C3 §2、§3（下蹲 × 0.2 是误读，+0x1c7 是水中标志）。main
- DP §6.2（落地强度律）、P2（2° → 20° → 30–44°）。main
- DIFF K-1 / K-2，D-35，D-71。main
- [反编译] `Land_ViewKick` 0x140a35750；水中标志 player+0x1c7（`PlayerMove` 0x140a54e80 每 0.05 s 向下 100 u 检测）。

### 2.4 下滑索 `zip_detach`

#### 原理

离开滑索是"退出一个大动作"：身体从绳子上的高速状态被放回自由落体，画面猛地往下点一下（14–18°），偏航和横滚也随机甩一下。基础值 10 是本章力度规律的最高档（§4.5）。

#### 规则和公式

1. 触发：离开滑索的那条命令（任何方式：跳下、到头、取消）。
2. 冲量：俯仰 (10 + 3·r₁)·20，偏航 10·r₂·20，横滚 10·r₃·20，第二组 × 0.2。
3. 随机数用起跳的盐，但取**下绳后那一条命令**的 r（实测 5 / 5 次的峰值排序和那条命令的 10 + 3r₁ 排序一致）；冲量仍加在下绳那条命令上。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 俯仰基础 / 随机 | — | 10 / 3 × r | — | — | [反编译] |
| 偏航 / 横滚随机 | — | 10 × r | — | — | [反编译] |
| 画面俯仰峰值 | — | 14.3–18.0 °，约 0.12–0.14 s | — | R5 16.82 / 14.36 / 15.16 / 17.45 / 17.69° | [实测] |
| 偏航 / 横滚峰值 | — | 1.5–6.6 ° / ±1–7 ° | — | — | [实测] |

#### 实现模板

```
if wasRiding and not riding:
    r = rand(cmd + 1, SALT_JUMP)       // 下一条命令的随机数
    kick((10 + 3·r1)·20, 10·r2·20, 10·r3·20)
```

Unity：NC.cs `p.zipDetachPunch`（`zipDetachPitchBase` 10、`zipDetachPitchRandom` 3、`zipDetachYawRandom` 10、`zipDetachRollRandom` 10、`zipDetachSeedOffset` 1）；骑乘状态读 `ZiplineAbility.phase == ZipPhase.Mounted`。

#### 验收

- `FndCameraTests.ZiplineExitAddsTheNativeImpulse`、`ZiplineExitPitchesTheViewDown`。
- 对照：N10_zip 5 次下绳，Unity 16.77 / 14.31 / 16.27 / 17.47 / 17.67° 对 R5 16.82 / 14.36 / 15.16 / 17.45 / 17.69°；下绳指标 17 / 20（r24101 差 1.1° 是 R5 晚一条命令下绳，运动时序，D-70 记录不追）。

#### 出处

- CAM2 §7 K-8；DIFF FND K-8、二节 K-8 下绳时刻；D-67、D-70。main
- [反编译] `Zipline_DetachFeedback` 0x140a35ac0（由下绳 0x14074ccf0 调用）。

### 2.5 翻越 `mantle`（开始 → 结束）

#### 原理

翻越不是 kick，而是**动画镜头**：翻越时画面跟着第一人称翻越动画里的镜头挂点走，先低头看台面（约 5°），翻上去再抬回来，整个过程约 0.5 s。开始时用 0.15 s 淡入，所以第一帧没有跳变；结束时自然回到 0，**不触发落地 kick**（不是摔下来的）。如果翻越是跳起来接上的，起跳的 punch 照样在跑，两者相加。

#### 规则和公式

1. 范围：从翻越开始到翻越结束（身体处于翻越 / mantle 状态）。60 u 以下的墙 R5 直接跳过去、不翻越，就没有。
2. 曲线按**翻越类别**选，在翻越开始时定一次：
   - 站姿时长 T（按 02 / 04 章的翻越时长公式）分三档：T < 0.390 s → h80；0.390 ≤ T < 0.519 s → h100；否则 h120+（三档的代表时长 0.313 / 0.467 / 0.571 s，边界取两两中点）。
   - 开始时是蹲姿 → 对应的 Crouch 曲线；蹲着到 h120 且从低的基础状态开始 → `CrouchH120Short`（D-75 B，04 章）。
3. 进度：u = (现在 − 翻越开始) / 翻越时长。曲线是两张表（[07-camera/traversal-curves.tsv](07-camera/traversal-curves.tsv)，每 0.05 一个点，线性插值）：
   - `anim(u)`：时间进度 → 动画进度；
   - `delta(a)`：动画进度 → 俯仰偏移（°，+ 向下）。
4. 站姿 h120 还按"视线和墙面的偏航夹角"混合：w = clamp(|夹角| / 45°)，delta = delta_H120 + (delta_H120Yaw45 − delta_H120)·w。
5. 淡入：俯仰偏移 × smoothstep((现在 − 翻越开始) / 0.15 s)。
6. 加进俯仰那一行（§4.1），不改瞄准。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 淡入 `traversal_viewLerpInDuration` | — | 0.15 s，smoothstep | — | 实测第一帧 −0.10 … +0.18° | [反编译] [实测] |
| 120 u 冲刺翻越峰值 | — | 4.86–5.01 °（Frida 8 次），约 0.49 s | — | 按类别 4.5–6.9° | [实测] |
| h80 冲刺峰值 / 到峰 | — | 6.0–6.9 °，0.32–0.33 s | — | — | [实测] |
| h100 冲刺峰值 | — | 5.2–6.3 ° | — | — | [实测] |
| 类别边界（站姿时长） | — | 0.390 s / 0.519 s | — | 跟着翻越时长走 | [实测] [算] |
| 偏航混合满值夹角 | — | 45 ° | — | 只量了 0° 和 45° | [实测] |

#### 实现模板

```
// 翻越开始时
curveClass = classify(standingTraversalTime, crouchedAtStart, lowBaseState)
// 每条命令（翻越中）
u     = (t − t0) / duration
a     = lerpTable(anim[curveClass], u)
delta = lerpTable(delta[curveClass], a)       // 站姿 h120 再按偏航夹角混合
mantlePitch = delta · smoothstep((t − t0) / 0.15)
// 翻越结束：mantlePitch = 0；不加落地 kick
```

Unity：NC.cs `Observe` 里 `traversing`、`lastMantlePitch`；`HSD-Unity: Assets/HSD/R5Replay/Runtime/MantleBoostS27.cs`（`MantleCurveClass`、`DeltaAtTime`、`ClassifyByTime`、两组表）；`ClimbAbility.MantleFraction`、`S27Delta`。开关 `NativeCameraParams.traversalCamera`（false = 只在 S27 翻越加速模式下有）、`traversalLerpIn` 0.15（0 = D-75 之前，第一帧直接加 +1.2 … +2.1°）。S27 翻越加速的判定读**没淡入的**曲线（04 章）。

#### 验收

- `Cam2CameraTests.EveryMantlePitchesTheViewByTheTraversalCurve`、`TheTraversalPitchFadesInFromTheMantleStart`；`NativeCameraTests.MantleBoostPitchesTheViewByTheTraversalCurve`。
- 对照（B1 片段，峰值 R5 / Unity）：h80 冲刺 6.0–6.9 / 7.4–7.8，h100 冲刺 5.2–6.3 / 5.9–6.2，h120 冲刺 4.5–5.3 / 4.6；K-6 指标 53 / 88。
- 已知差别：蹲着翻越 h120 R5 约 1/4 是短的那种，Unity 复现不了（亚 1 u 的起点差），S 类平均差 0.193 s；h120 M 类的窗口 0.45 / 0.28 s（DIFF 二节"D-75 剩下的"）。

#### 出处

- CAM2 §3、§5.1；CR §3.11；DIFF CAM2 K-6、D-75、二节 K-6 蹲姿；D-53、D-74、D-75。main
- B1 §4：曲线表和类别（61 次 R5 翻越平均）；D72 §8–§9：淡入。main
- [反编译] `C_PredictedFirstPersonProxy::GetTraversalViewPosition` 0x1406668a0；翻越状态机 `TraversalMove` 0x140a45380。

### 2.6 滑铲开始 `slide_start`

#### 原理

滑铲开始**没有 kick**。滑铲的镜头感完全来自三个持续通道同时启动：眼睛在 0.2 s 内降到蹲姿高度、FOV 在 0.25 s 内放大 10 %、如果视角和滑行方向有夹角，画面往一边歪。这是"状态改变"而不是"冲击"，所以用过渡而不用弹簧（P2）。

#### 规则和公式

滑铲开始这条命令起：

1. 下蹲比例目标 1，速率改成滑铲的 1/0.2 s（§3.1）；
2. 滑铲 FOV 目标 1.1（§3.10）；
3. 滑铲倾斜的目标从 0 变成"按速度方向和大小"（§3.5）。

滑铲中起跳走 §2.1（滑铲跳），起跳后三个通道各自按退出速率回去。

#### 实现模板

无单独代码：三个通道读 `body.sliding` 自己切换。Unity 只在 `m.slideStarted` 时记一个 HUD 提示（`lastCue`）。

#### 验收

`NativeCameraTests.StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt`：直线滑铲 0.2 s 眼高到 32、FOV 到 × 1.1、横滚 ≈ 0。

#### 出处

- C3 §1（眼高 0.208–0.213 s、FOV 89 → 97.9、直线滑横滚 0.05°）；CR §3.1、§3.3、§3.6。main

### 2.7 蹬墙跳 `wall_kick`、跑墙开始 / 超时 `wallrun_start` / `wallrun_timeout`

#### 原理

R5 S21 关掉了跑墙，所以这三个事件**没有任何 R5 实测**。代码里有"跑墙开始"和"跑墙超时"两个 punch（Apex 新加，TF2 没有），但数值没读。蹬墙跳本身在 R5 和 TF2 都没有专门的镜头 kick；跑墙倾斜（§3.7）在蹬离墙后按速率回到 0，这就是蹬墙跳的镜头感。

HSD 现在的做法：原生镜头里蹬墙跳**不加 kick**（M7 的蹬墙跳不是原生地面跳，不触发 §2.1）。M5.5 旧版有横滚 kick 2.5° 和 FOV kick 2°，属于偏离（§6）。

#### 规则和公式

1. `wall_kick`：没有 kick。跑墙倾斜的目标变 0，按 §3.7 的速率回去。
2. `wallrun_start` / `wallrun_timeout`：R5 有 punch（结构同 §1.1，进同两组弹簧），**数值没读**（setfile `wallrun_viewpunch_onStart_base*` / `random*`、`onTimeout_*`）。HSD 没做。
3. 如果以后要加，按 §5 的步骤：开始是"平常动作"档（基础约 2），超时被甩下墙接近"退出大动作"但更轻（[设计]，要试玩）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 跑墙开始 punch | — | 未知（键名已知，值没读） | — | — | [反编译]（只有函数） |
| 跑墙超时 punch | — | 未知 | — | — | [反编译]（只有函数） |
| 蹬墙跳 kick | — | 0（没有） | — | M5.5 [设计] 横滚 2.5°、FOV 2° | [反编译] [TF2 数据] |

#### 实现模板

无（HSD 没做）。跑墙倾斜见 §3.7。

#### 验收

无：没有对照数据。要做时先补 R5 setfile 读值（B07-2），再按 §5.6 验收。

#### 出处

- CI CAM-03、CAM-04；CR §5；`tf2/TF2-VS-APEX.md` §3（"蹬墙跑起跑和超时的镜头抖动：TF2 没有，Apex 新加"）；T3W §2.2。main
- CR §4（M5.5 的墙跳横滚 kick 2.5、FOV kick 2）。main
- [反编译] 跑墙开始 punch 0x140a34e40、超时 0x140a35170。

### 2.8 受击 `hit`

#### 原理

**铁驭被子弹打中，第一人称画面完全不动**（R5 实测）。受伤的信息靠 HUD、声音、屏幕颜色，不靠镜头。这符合 P1：被打时准星和画面都不跳，玩家照样能还击。服务端的"受击 flinch"只给第三人称动画看（[推断]）。

泰坦不一样（TF2 实测）：驾驶舱被打会**旋转 + 后移**，方向远离伤害来源，强度按伤害。这是泰坦独有的规则，第 08 章泰坦部分会再用到。

#### 规则和公式

1. 铁驭：受击 kick = 0（两组 punch、画面、FOV 都 0）。
2. 泰坦（TF2 `JoltCockpit`）：

   ```
   强度 = min(伤害 / 2000, 1)
   旋转 7° × 强度、位移 7 u × 强度，方向远离伤害来源
   正面来袭：抬头 + 后退；侧面来袭：横滚和偏航同时偏
   ```

   曲线（2000 伤害）：0.15 s 内冲到，约 0.26 s 峰值，0.57 s 过零，反向过冲约 12 %（+0.84°，0.70 s），约 1.4 s 平息。三种底盘相同。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 铁驭受击 kick | — | 0 | — | 27 发全 0 | [实测，hyb] |
| 泰坦满强度伤害 | — | 2000 点 | — | — | [TF2 数据] [TF2 实测] |
| 泰坦最大旋转 | — | 7 ° | — | 实测 1000 → 3.5°、2000 → 7.0° | [TF2 实测] |
| 泰坦最大位移 | 0.1778 m | TF2 原值 7 u | 0.0972 H | — | [TF2 实测] |
| 泰坦峰值时间 / 过零 / 平息 | — | 0.26 s / 0.57 s / 1.4 s | — | — | [TF2 实测] |

泰坦的位移 kick 和 P2"只转不移"相反，这是 TF2 驾驶舱的规则，只用在泰坦上。

#### 实现模板

- 铁驭：什么都不做。测试里断言受击前后画面角不变。
- 泰坦：`HSD-Unity: Assets/HSD/Game/Runtime/Titan/Camera/TitanCockpitCamera.cs`（`TitanCockpitCamera : ITitanCameraLayer`），参数 `TitanCamParams.cs`（HSD-Unity PR #66 / #78，还没合并）。

#### 验收

- 铁驭：受击 N 次，画面角和瞄准角逐位不变。
- 泰坦：1000 / 2000 / 侧面 1500 三个输入的峰值（3.5° + 3.5 u、7.0° + 7.0 u、横滚 5.3° + 偏航 5.3°）差 < 5 %；时间形状对上（TF2 生成的参考表，见 11 章）。

#### 出处

- FG §3：bot 玩家真开枪 27 发，第一人称全 0。PR #122，还没合并
- DP §6.2、§9.5（#122 版）：受击抖动判为偏离。PR #122，还没合并
- TPC §4.4：泰坦 `JoltCockpit` 规则和曲线。main
- CI BND-03（受伤 punch 的脚本位置，早期登记）。main

### 2.9 爆炸 `explosion`

#### 原理

R5 的移动镜头里没有"自己的震屏"。震屏是**世界事件**：脚本或动画事件调用"在某点产生震动"，按距离衰减，附近所有玩家都会收到。爆炸、泰坦落地、起飞等用它。铁驭在 R5 里被爆炸震屏的具体数值**没测过**。

#### 规则和公式

1. 震屏不是 punch，不进 §1.1 的弹簧；它在画面拼好以后单独加角度和位移（R5 每帧视图设置的最后一步）。
2. 参数形式（TF2 `CreateShake(振幅, 频率, 时长, 半径)`）：例如泰坦落地 (16, 150, 2 s, 1500 u)，Hover 起飞 (16, 150, 1 s, 400 u)，核心爆发 (16, 5, 2 s, 1500 u)。实测 (16, 150, 1 s, 半径 1000 u) 在 300 u 处是 1.94° + 7.1 u。
3. 振幅和画面角度的换算、距离衰减曲线、R5 的爆炸是否调用：**没研究**（§7）。
4. 对比：泰坦走路对旁边铁驭只有竖直下沉 ≤ 0.7 u，不转（`0.68 u × (1 − (距离/1050)²)`，0.15 s 回零）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R5 铁驭爆炸震屏 | — | 未知 | — | — | 没测 |
| TF2 震屏样例：300 u 处 | 0.180 m | TF2 原值 7.1 u + 1.94° | 0.099 H | — | [TF2 实测] |
| 泰坦脚步对旁人的下沉（贴身） | 0.0173 m | TF2 原值 0.68 u | 0.0094 H | 1050 u 外 0 | [TF2 实测] |

#### 实现模板

无（HSD 铁驭没做）。要做时作为 §4.1 最后一步的单独加项，有自己的开关和强度组（§4.6）。

#### 验收

无。

#### 出处

- CI CAM-21（`ClientScreenShake` 的脚本位置）、CAM-23（上升气流震动，未定位）；N10 §2 第 5 步（屏幕震动在视图设置最后改镜头）、§3（实测震动一直 0）。main
- DP §6.5（自己的震屏是偏离）。main
- `tf2/expansion/titan/anim/ref-upper/REF-UPPER-1109.md` §2.4、`tf2/expansion/titan/anim/TITAN-ANIM-FEEL.md` F21：`CreateShake` 参数、300 u 的对照、脚步下沉公式。main

### 2.10 开枪后坐 `fire`（对画面的那一部分）

#### 原理

开枪时画面会跟着后坐往上走，停火后弹簧把它拉回原位。这一部分和移动 kick 是同一种物理：往弹簧加冲量（P8）。区别是武器 kick 进**第二组**弹簧，而且拿枪时第二组弹簧用**这把枪自己的弹簧常数**。画面只显示第二组的 (1 − fraction) 倍：fraction 是"这把枪的后坐有多少只给子弹、不给画面"。开枪**没有震屏**（7 把枪实测），想让单发枪"有分量"，R5 的做法是拉栓 / 泵动的**动画镜头**（同 §2.5 的动画挂点）。

后坐图案、随机、热度、开镜插值等全部在 **09 章**，这里只写画面怎么接。

#### 规则和公式

1. 每发：武器 kick 写进第二组弹簧：角度 += hard × K，角速度 += soft × 20 × K（K = 图案这一行 × 基础 + 随机，09 章）。
2. 第二组弹簧常数：拿枪时 = 这把枪当时的武器弹簧（冷 / 热按热度插值，再按开镜进度在腰射 / 开镜之间插值）；空手时 = 65 / 9。第一组永远 65 / 9。
3. 画面俯仰 / 偏航 += (1 − fraction) × 第二组角度；fraction 按开镜进度在腰射值和开镜值之间插值。**横滚全部进画面。**
4. 移动事件写第二组的那 0.2 倍，也走这把枪当时的武器弹簧，所以拿枪时移动事件在第二组的峰值比空手小（R-301 腰射是第一组的 0.13 倍，空手 0.20）。
5. 鼠标和 punch 反向时，鼠标输入先一比一抵消第二组的 punch，减到 0 才进瞄准角（EM §1）。
6. 子弹 = 瞄准 + punch1 + 完整 punch2（这一发 kick 之前）+ 开镜 drift + 扩散（§4.3）。
7. 拉栓 / 泵动 / 换弹动画带镜头：Peacekeeper 腰射泵动俯仰 5.2°、横滚 1.8°，Kraber 拉栓 4.9°，Longbow 腰射 0.4°，开镜多数压到 0–0.4°；开枪后零点几秒开始，平滑曲线。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 开枪震屏 | — | 0 | — | 7 把枪 × 腰射 / 开镜 | [实测] |
| 画面倍数 1 − fraction（R-301 腰射 / 开镜） | — | 0.95 / 1.00 | — | 29 把：腰射 fraction 0.05–0.35（连发）、0–0.5（单发） | [实测] [数据] |
| R-301 武器弹簧 腰射 / 开镜（俯仰 k / d） | — | 40 / 20、115 / 20 | — | 见 09 章 | [实测] [数据] |
| 空手第二组弹簧 | — | 65 / 9 | — | — | [实测] |
| R-301 停火回落到原位 | — | 腰射约 2.5 s，开镜约 1 s | — | — | [实测] |
| 拉栓镜头（Peacekeeper 腰射） | — | 俯仰 5.2 °、横滚 1.8 ° | — | 只量 3 把（B07-4） | [实测] |

**HSD 现在和 R5 不一样的地方**（写进 `_notes/hb-ch07.md`，没改）：

- Unity 的武器 punch（`ViewKick`，HSD-Unity PR #67，还没合并）和原生镜头的第二组是**两个独立的弹簧**；R5 是同一个第二组。所以 Unity 里移动事件的第二组一直用 65 / 9，也不乘 (1 − fraction)。
- Unity 的子弹 = 瞄准 + 武器 punch，**没有 punch1 和开镜 drift**（FG §1、§5 的 11-13 实测还没进 Unity）。
- 鼠标抵消 punch 没做（`ViewKick` 注释写明留在 R5-DIFF）。

#### 实现模板

```
// 每帧画面（§4.1）里的武器部分
f = lerp(fractionHip, fractionAds, zf)
viewPitch += punch1.pitch + (1 − f)·punch2.pitch
viewYaw   += punch1.yaw   + (1 − f)·punch2.yaw
viewRoll  += punch1.roll  + punch2.roll
```

Unity：`HSD-Unity: Assets/HSD/Game/Runtime/Combat/Arsenal/ViewKick.cs`（`ViewKick`、`KickStance`），`GunKick.cs`（HSD-Unity PR #67，还没合并；叠在 #60 等上）。09 章写全。

#### 验收

- 09 章。镜头这边：开枪前后 `aim` 只随鼠标变；腰射画面 / punch2 斜率 = 1 − fraction（RV §1.1 表：R-301 0.950、Spitfire 0.800、Wingman 0.600、P2020 1.000）。

#### 出处

- RV §1.1、§2、§4、§5：画面 = 瞄准 + (1 − fraction) × punch、回落曲线、hard / soft、腰射 / 开镜。PR #93，还没合并
- FG §1、§1.3、§2、§5：子弹含 punch1 和开镜 drift、拿枪时第二组用武器弹簧、没有开枪震屏、拉栓镜头。PR #122，还没合并
- EM §1：鼠标抵消 punch。PR #122，还没合并
- DP P1、T2、T3、§6.5（#122 版）。PR #122，还没合并
- [反编译] fraction 插值 0x140af0c90；武器 kick 0x140711ce0；鼠标抵消 0x140a33ff0；`m_vecPunchWeapon` player+0x2448 / +0x2454。

### 2.11 近战 `melee`

#### 原理

铁驭近战时镜头怎么动，**没研究**。R5 只量了近战的时间（按键后 0.367 s 最早能开火，不开火约 0.98 s 回到枪），没录镜头。泰坦近战（TF2）是动画驱动的大动作。

#### 规则和公式

1. 铁驭：未知。HSD 不加 kick；如果加，按 §5 的流程，属于"主动动作"档，而且很可能应该是动画镜头（§2.5 的做法）而不是 kick（[推断]）。
2. 泰坦（TF2 实测，动画驱动，约 0.8 s）：Ion / Legion 偏航 +22 / −14°，横滚 −17 / +14°，俯仰 −4 / +14°，前冲 25 u，之后约 0.8 s 小幅余震（约 0.6°）；Ronin 剑温和得多：偏航 −16 / +7°，横滚 +5°，俯仰 ±5°，位移 6 u。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 铁驭近战镜头 | — | 未知 | — | — | 没测 |
| 泰坦近战前冲（Ion / Legion） | 0.635 m | TF2 原值 25 u | 0.347 H | Ronin 6 u | [TF2 实测] |

#### 实现模板

无。

#### 验收

无。

#### 出处

- `research/combat/gun-measure/C-MOTIONS.md` §6（近战时间，没录镜头）。PR #95，还没合并（分支 `combat/gun-measure`）
- TPC §4.5（泰坦近战）。main

### 2.12 放技能 `ability`

#### 原理

R5 里**放技能本身不动镜头**：没有技能 FOV、没有技能震屏（P2、DP §6.5）。技能的镜头感全部来自它引起的**移动**：钩爪 → 绳子横滚（§3.8）；滑索 → 眼睛偏移和下绳 kick（§3.9、§2.4）；Octane 跳板二段跳 → 二段跳 kick（§2.2）；翻越 → 动画镜头。也就是说，做一个新技能的镜头，先问"它让身体做了什么"，用那个动作已有的通道。

R5 代码里还有几个**移动类技能 punch**（跳板、重力炮、抓墙），和起跳一样进同两组弹簧，但**数值没读**，HSD 没做（CR §8）。跳板、弹射等"发射"不触发起跳 punch。

#### 规则和公式

1. 放技能：画面 0、FOV 0。
2. 技能引起的移动：用对应的移动通道。
3. 跳板 / 重力炮 / 抓墙 punch：结构 = §1.1 的冲量，数值未知（§7）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 技能 FOV | — | 0（没有） | — | M5.5 [设计] +2…+6° | [实测] [反编译] |
| 跳板 / 重力炮 / 抓墙 punch | — | 未知 | — | — | [反编译]（只知道存在） |

#### 实现模板

无单独代码。

#### 验收

开技能前后、技能持续中，FOV 和画面角只随它引起的移动通道变（`NativeCameraTests.TheSimulationIsUntouchedAndTheAimIsRaw` 的做法）。

#### 出处

- CR §1（技能 FOV：没有）、§8（kick 列表含跳板、重力炮、抓墙）；CAM2 §5 第 6 步。main
- DP §6.5、P2。main

### 2.13 泰坦登机 `titan_embark` / 弹射 `titan_eject`（TF2）

#### 原理

泰坦的上下机是**整段镜头动画**，不是 kick。上机时第一人称跟着铁驭爬上泰坦的动画（大幅横滚和俯仰），最后黑场切进驾驶舱；下机立刻切回铁驭，低头看舱门；弹射时视角被强制往下看着脚下的泰坦。这些都只有 TF2 实测，R5 没有泰坦。第一 / 第三人称切换、驾驶舱 ↔ 外部切换的过渡规则没研究（§7）。

#### 规则和公式

| 事件 | 镜头 | 时间 |
|---|---|---|
| 上机（动画） | 第一人称镜头动画，横滚可到 75°，俯仰 −30 … +64°；末尾黑场 0.2 s 切入驾驶舱；FOV 70 → 75 | 约 3.25 s（另一份测 3.45 s） |
| 开机 | 曝光补偿 −6 闪 0.1 s；舱体"开机中"1.3 s；屏幕效果约 2.05 s；HUD 分块亮起 | 进舱后 |
| 下机 | 立刻切到铁驭，FOV 70；低头看舱门（俯仰约 43°） | 约 1.6 s 落定 |
| 弹射 | 按三下，约 0.95 s 后弹出；视角强制低头约 80°，看脚下的泰坦；FOV 70 | 弹出后约 0.35 s 无敌 |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 泰坦眼高（站 / 蹲） | 4.699 / 3.175 m | TF2 原值 185 / 125 u | 2.569 / 1.736 H | 三种底盘相同 | [TF2 实测] |
| 泰坦 FOV / 铁驭 FOV | — | 75 ° / 70 °（TF2 设置） | — | 学比例，不学度数 | [TF2 实测] |
| 弹射强制俯仰 | — | 约 80 ° | — | — | [TF2 实测] |
| 弹射向上速度 | 38.1–43.2 m/s | TF2 原值 1500–1700 u/s | 20.8–23.6 H/s | 05 章 | [TF2 实测] [TF2 数据] |

#### 实现模板

Unity：`HSD-Unity: Assets/HSD/Game/Runtime/Titan/Camera/TitanCamKeys.cs`（`TitanBoot`）、`TitanCockpitCamera.cs`、`TitanCockpitView.cs`；`Titan/View/TitanCamera.cs`（`Compute(..., bool thirdPerson)`）（HSD-Unity PR #66 / #78，还没合并）。HSD 设计上机可以有动画上机和瞬间上机两种（`tf2/expansion/titan/T0-REPORT.md` §1）。

#### 验收

泰坦镜头的 TF2 参考表（11 章，`TitanCamTests`、`TitanFeelParity`，HSD-Unity PR #87，还没合并）。

#### 出处

- TPC §4.1、§4.5、§5.1。main
- `tf2/expansion/titan/feel/TITAN-FEEL.md` §3（上机 3.45 s、下机低头约 43°）。PR #118，还没合并
- `tf2/expansion/titan/kits/T-f-COCKPIT-RELOAD.md`（开机曝光闪、1.3 s）；`tf2/expansion/titan/T0-REPORT.md` §1。main

---

## 3. 持续型

持续通道的总原则（P2）：**能不动就不动，要动就按相对量动**。没有速度 FOV、没有侧移横滚、没有身体惯性；倾斜只按"速度相对视角的方向"或"转身速率"算，所以正着跑、正着滑都是 0。

### 3.1 眼高 `eye_height`、冲刺眼低 `sprint_eye`（站 / 冲刺 / 蹲 / 滑铲）

#### 原理

画面的位置永远是眼睛，眼睛只随身体姿态变：站着 70 u；冲刺时低 6 u（身体前倾）；蹲下或滑铲降到 32 u。蹲下用 0.4 s、滑铲只用 0.2 s（滑铲是快动作），曲线是 smoothstep，起止都平滑。冲刺的下沉要等 0.16 s 才开始、慢慢降下去，停下时 0.11 s 后很快回来，所以短暂的冲刺几乎看不到。

#### 规则和公式

```
下蹲比例 d：目标 = (下蹲 或 滑铲 或 碰撞体是蹲姿) ? 1 : 0
            速率 = 滑铲中 1/0.2 s，否则 1/0.4 s；moveToward
冲刺比例 q：冲刺标志变了就重新计时；
            标志为真且计时 ≥ 0.16 s：q += 1.25·dt（上限 1）
            标志为假且计时 ≥ 0.11 s：q −= 6.67·dt（下限 0）
站姿眼高 = 70 + (−6)·sin(q·π/2)
眼高     = 站姿眼高 + (32 − 站姿眼高)·smoothstep(d)
```

冲刺下沉先作用在站姿高度上，再和蹲姿混合：所以蹲着、滑着都是 32，不管有没有冲刺；从冲刺进滑铲是从 64 降到 32。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 站立眼高 `viewheight` | 1.778 m | 70 u | 0.972 H | **不是 64**（64 是冲刺中量的） | [数据] [实测] |
| 冲刺下沉 `sprintViewOffset` | −0.1524 m | −6 u | −0.0833 H | 冲刺眼高 64 u = 1.626 m | [数据] [实测] |
| 蹲 / 滑铲眼高 | 0.8128 m | 32 u | 0.444 H | — | [实测] |
| 下蹲时间 | — | 0.4 s | — | — | [反编译] |
| 滑铲下蹲时间 | — | 0.2 s | — | 实测 0.208–0.213 s | [反编译] [实测] |
| 下蹲曲线 | — | smoothstep | — | C3 吻合 ±1.5 u | [实测 + 推断] |
| 冲刺下沉等待 / 速率 | — | 0.16 s / 1.25 /s | — | 三次差 ≤ 0.01 s | [实测] |
| 冲刺回升等待 / 速率 | — | 0.11 s / 6.67 /s | — | — | [实测] |

#### 实现模板

```
// 单位：u、s；每条命令
eye.step(down = sliding||ducked||hullCrouched, sliding, sprinting, dt)
eyeHeight = eye.height()
cameraPos = bodyOrigin + (0, 0, eyeHeight) + zipOffset      // §3.9
```

眼高**同时用于**钩爪射线的起点（A-1：钩子从真实眼睛打出去），所以镜头和钩爪共用一个状态。

Unity：Eye.cs `NativeEyeParams`（`standEye` 70、`crouchEye` 32、`duckTime` 0.4、`slideDuckTime` 0.2、`sprintOffset` −6、`sprintRiseDelay` 0.16、`sprintRiseRate` 1.25、`sprintFallDelay` 0.11、`sprintFallRate` 6.67）、`NativeEyeHeight.Step` / `Height`；旧版 `NativeEyeParams.PreF4()`（站 64，没有冲刺项）。

#### 验收

- `NativeCameraTests.StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt`。
- 对照：C3 滑铲样本 0.052 s 59.3 u、0.103 s 49.3 u、0.154 s 39.3 u、0.205 s 32.2 u，smoothstep 在 ±1.5 u 内；N6 / N10 冲刺眼高三次差 ≤ 0.01 s、0.3 %。
- 合格线：站立 70、冲刺稳态 64、蹲 / 滑 32 精确；过渡曲线和实测差 ≤ 1.5 u。

#### 出处

- DIFF K-4、A-1；D-38。main
- CR §3.1（**眼高 64 过时，以 K-4 的 70 为准**）；C3 §1；NC §7。main
- [反编译] `ViewHeight?` 0x140a53f30、`Duck` 0x140a54080、`Sprint_ViewOffset` 0x140af2370；下蹲曲线形状 0x1409d9750 没读（所以 smoothstep 是 [推断]）。

### 3.2 跑步晃动 `step_bob`

#### 原理

冲刺时画面每一步轻轻点一下头（俯仰约 ±0.25°），左右脚交替时轻轻左右摆（偏航约 ±0.45°）。很小，是原版就有的，用户要求保留（P2 的反例：持续的也可以有，但必须很小）。它来自第一人称动画，不是弹簧也不是震屏；第一步就几乎是全幅。

#### 规则和公式

```
权重 w：目标 = (冲刺 且 着地 且 水平速度 > 200 u/s) ? 1 : 0，速率 20 /s
俯仰 = w · (−0.155 + 0.25 · sin(2π t / 0.280))     // 每步一个周期
偏航 = w · (+0.36  + 0.445 · sin(π t / 0.280))     // 每两步一个周期
```

t 用会话时钟（Unity 没有和真实脚步对齐，相位是推断，B07-5）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 步长周期 | — | 0.280 s | — | N6 0.27 s | [实测] |
| 俯仰中心 / 幅度 | — | −0.155 ° / 0.25 ° | — | 直跑 0.218–0.259° | [实测] |
| 偏航中心 / 幅度 | — | +0.36 ° / 0.445 ° | — | 实测 −0.085 … +0.806° | [实测] |
| 启用速度 | 5.080 m/s | 200 u/s | 2.778 H/s | — | [推断] |
| 渐入速率 | — | 20 /s | — | 旧版 4 /s 太慢 | [实测] |

#### 实现模板

Unity：NC.cs `swayPitchMid` −0.155、`swayPitchAmp` 0.25、`swayPeriod` 0.280、`swaySpeedMin` 200、`swayFade` 20、`swayYawMid` 0.36、`swayYawAmp` 0.445；`Observe` 里 `swayWeight`、`lastBobPitch`、`lastBobYaw`。旧值：`swayPitchAmp = 0.335`、`swayFade = 4`。

#### 验收

- `NativeCameraTests.ContinuousTermsStayInsideTheirMeasuredBounds`（俯仰、偏航上下限）。
- 对照：直线冲刺按步算的峰峰值约 0.50°（C3、N6、N10 三个会话一致）。

#### 出处

- N10 §4、§6 C-10；DIFF K-3；D-24、D-37。main
- CR §3.8（旧的 0.335 来自带转向的片段）。main

### 3.3 站立漂移 `view_drift`、开镜漂移 `ads_drift`

#### 原理

站着不动时画面极慢地漂（俯仰 ±0.2°，5 秒一个来回），像人在呼吸。开镜时也有漂移，而且开镜漂移会进子弹（09 章）。都很小。

#### 规则和公式

```
权重 w：目标 = (着地 且 水平速度 < 10 u/s) ? 1 : 0，速率 2 /s
俯仰 = w · 0.195 · sin(2π t / 5.2)
偏航 = w · 0.084 · sin(2π t / 3.2)
```

R5 原生有 40 个 drift 参数，只量了站着不动这一种，所以只用两条拟合正弦。开镜漂移：R-301 俯仰最大 0.29°、偏航 0.21°（09 章）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 俯仰幅度 / 周期 | — | 0.195 ° / 5.2 s | — | — | [实测] |
| 偏航幅度 / 周期 | — | 0.084 ° / 3.2 s | — | — | [实测] |
| 静止判定 | 0.254 m/s | 10 u/s | 0.139 H/s | — | [推断] |
| 渐入渐出 | — | 2 /s | — | — | [推断] |
| 开镜漂移（R-301） | — | 俯仰 0.29 °、偏航 0.21 ° | — | 按姿态缩放 | [实测] |

#### 实现模板

Unity：NC.cs `driftPitchAmp` 0.195、`driftPitchPeriod` 5.2、`driftYawAmp` 0.084、`driftYawPeriod` 3.2、`driftIdleSpeed` 10、`driftFade` 2。开镜漂移在武器层（09 章）。

#### 验收

`NativeCameraTests.ContinuousTermsStayInsideTheirMeasuredBounds`。

#### 出处

- CR §3.8；CI CAM-20；DIFF K-3（站立 drift ±0.195° 保留）。main
- RV §1.1、§5（开镜 drift）。PR #93，还没合并

### 3.4 枪的摆动 `weapon_sway`

#### 原理

转身、走动时**枪和手臂**在画面里晃，但**镜头本身不晃**。R5 的"cockpit sway"实测只作用在第一人称模型上（N10）；驾驶舱弹簧会动镜头，但 S21 里输入全是 0。所以对镜头来说，枪的摆动 = 0；怎么摆在 08 章。

#### 规则和公式

1. 镜头：0。
2. 枪模：08 章（主序列 + 程序层，开镜收掉程序层）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| cockpit sway 对镜头 | — | 0 | — | 冲刺时枪模 −0.02 … +0.01° | [反编译] [实测] |
| cockpit 弹簧对镜头（S21） | — | 0（`cockpit_stepJolt_*` 0 0 0） | — | 7000 帧一直 0 | [实测] |

#### 实现模板

镜头里不做。Unity 旧名"CAM-18 sway"已改成跑步晃动（§3.2）。

#### 验收

无（08 章验收枪模）。

#### 出处

- N10 §1–§3：sway 只动第一人称模型；CAM-19 在 S21 是 0。main
- `research/combat/MOVEMENT-ANIMATION.md` §12（#123 版）（08 章）。PR #123，还没合并

### 3.5 滑铲倾斜 `slide_tilt`

#### 原理

正着滑铲画面不歪；只有**视角和滑行方向有夹角**时，画面往一边倾（最多 15°）。这样滑铲中转头看侧面，会感到身体在往前冲、头在往旁边看。倾斜按速度缩放：滑慢了就不歪。

#### 规则和公式

```
目标 T（二维向量）：
    滑铲中：T = 水平速度方向 × clamp((|v_h| − 125) / (400 − 125))
    否则：  T = 0
状态 S 朝 T 移动，每条命令最多 step：
    step = (|T| > |S| ? 5 : 2.5) · dt          // 变大 5 /s，变小 2.5 /s
Source 横滚 = −15 · (S · r̂)，   r̂ = (sin yaw, −cos yaw) 是视角的右方向
```

速度在视角左边（视角向右转开）→ 横滚为正（向右倾）。稳态时倾斜 = 15 × |S| × sin(夹角)。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 最大倾斜 `slide_viewTiltSide` | — | 15 ° | — | — | [数据] [实测] |
| 开始倾斜的速度 `slideStopSpeed` | 3.175 m/s | 125 u/s | 1.736 H/s | — | [数据] |
| 满倾斜速度 `slide_viewTiltPlayerSpeed` | 10.16 m/s | 400 u/s | 5.556 H/s | — | [数据] |
| 增加 / 恢复速率 | — | 5 /s / 2.5 /s | — | — | [数据] |
| 转 30° 滑铲实测 | — | 6.35–6.36 ° | — | — | [实测] |

#### 实现模板

Unity：NC.cs `slideTiltSide` 15、`slideTiltStopSpeed` 125、`slideTiltFullSpeed` 400、`slideTiltIncrease` 5、`slideTiltDecrease` 2.5；`Observe` 里 `slideTiltX / slideTiltY`、`lastSlideRoll`。

#### 验收

- `NativeCameraTests.SlideWithTheViewTurnedTilts`（C3 场景：滑铲中 0.4 s 向右转约 30°，6.36 ± 1.2°）、`StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt`（直线 ≈ 0）。

#### 出处

- NC §3、§7；CR §2.2、§3.3；C3 §1。main
- [反编译] `SlideTilt_Update` 0x140afc040。

### 3.6 冲刺转向倾斜 `sprint_tilt`

#### 原理

冲刺中转弯，画面往转弯那一侧倾一点（最多 2°），像摩托车压弯。按**转身速率**算，不按速度；走路不倾。

#### 规则和公式

```
n 目标 = 冲刺中 ? clamp(−偏航速率 / 120 °/s, −1, 1) : 0     // Source：向右转偏航变小
n 的速度朝 sign(目标 − n)·2 /s 加速，加速度 35 /s²；到达目标就停（速度清 0）
Source 横滚 = 2° · n                                        // 向右转，向右倾
```

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 最大倾斜 `sprinttiltMaxRoll` | — | 2 ° | — | — | [数据] [实测] |
| 满倾转速 `sprinttilt_turnrange` | — | 120 °/s | — | 60 °/s → 1.0° | [数据] [实测] |
| 速度上限 `sprinttilt_maxvel` | — | 2 /s | — | — | [数据] |
| 加速度 `sprinttilt_accel` | — | 35 /s² | — | — | [数据] |
| 达到稳态 | — | 60 °/s 约 0.28 s，120 °/s 约 0.53 s | — | — | [算] [实测] |

#### 实现模板

Unity：NC.cs `sprintTiltMaxRoll` 2、`sprintTiltTurnRange` 120、`sprintTiltMaxVel` 2、`sprintTiltAccel` 35；`Observe` 里 `sprintTilt`、`sprintTiltVel`（偏航速率 = 相邻命令的瞄准偏航差 / dt，取 ±180° 余数）。R5 经动画姿态参数执行，镜头结果和公式一致。

#### 验收

- `NativeCameraTests.SprintTiltFollowsTheTurnRate`（60 / 120 / 240 °/s 和走路）、`StrafingDoesNotRoll`。
- 对照：N6 实测 60 °/s → 1.007°，120 °/s → 2.00°。

#### 出处

- CR §2.3、§3.4；NC §4。main
- [反编译] 0x140a5a430、0x140a5a630（经 PoseParameter）。

### 3.7 跑墙倾斜 `wallrun_tilt`

#### 原理

跑墙时画面朝**离开墙**的方向倾（墙在左，画面右边低），让玩家感到身体贴着墙、头往外。蹬离墙后按速率回 0。R5 S21 关了跑墙，所以这一项只有代码值；TF2 实测过 15°。

#### 规则和公式

1. 目标：跑墙中 ±最大倾角，方向远离墙；否则 0。
2. HSD 现在：每条命令 roll += (目标 − roll) × min(1, 6·dt)（一阶指数，"6"按速率理解是 [推断]）。
3. TF2 还会**提前 0.25 s** 开始倾（预测快要贴墙），HSD 没做。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 最大倾角 `wallrun_maxViewTilt` | — | 10 °（Apex） | — | TF2 15° | [数据] [TF2 数据] |
| 速率 `wallrun_viewTiltSpeed` | — | 6 | — | 含义 [推断] | [数据] |
| 提前预测 `wallrun_viewTiltPredictTime` | — | 0.25 s（TF2） | — | HSD 没做 | [TF2 数据] |

#### 实现模板

Unity：NC.cs `wallRunMaxTilt` 10、`wallRunTiltSpeed` 6；`Observe` 里 `WallRunAbility.running` 时按墙法线和视角右方向选正负。TF2 规则开关（P-05）：`w.p.tf2.viewTilt` 为真时用 `viewTiltMax`（B 10° / A 15°），默认关。

#### 验收

无 R5 对照。TF2 规则验收见 05 章（跑墙）。

#### 出处

- CR §3.7；NC §3。main
- T3W `T3-REPORT.md` §2.2、`WALLRUN-B-SPEC.md` §8（P-05）。main

### 3.8 钩爪和滑索横滚 `rope_roll`

#### 原理

挂在钩爪或滑索上时，画面朝"绳子拉你的那一点"倾斜：钩点在视线右上方，画面就往右歪。钩爪最多 20°，滑索最多 25° × 0.7。两者（还有摆荡）**三选一，共用一个平滑状态**，所以从钩爪接到滑索时画面不跳（T9）。平滑用 SmoothCD（§1.3），不回弹。

#### 规则和公式

一个共用的"朝一个点横滚"函数。d = 点 − 眼睛，f / r / u = 视线的前 / 右 / 上方向：

```
距离系数 sd = (distFull > 0) ? clamp(|d| / distFull) : 1
视线夹角 θ = angle(d, f)；θ < viewMin 时返回 0
视角系数 sa = clamp((θ − viewMin) / (viewMax − viewMin))
p = d 在垂直于 f 的平面上的单位方向；φ = angle(p, u)，(p × u)·f < 0 时取负
k = clamp((|φ| − 90°) / 90°)                 // 点在视线下方时淡出
项 = sd · sa · (1 − k) · strength · clamp(φ, ±max)
Source 横滚目标 = −项
```

| 参数 | 钩爪 | 滑索 |
|---|---|---|
| distFull | 150 u | 0（没有距离系数） |
| viewMin / viewMax | 0 / 65° | 30° / 50° |
| strength | 1 | 0.7 |
| max | 20° | 25° |
| 用哪个点 | 钩点；钩头飞行中用飞行中的钩头 | 绳上"头顶正上方"那一点：沿绳子方向按**水平投影**找参数，再取三维点 |

**三选一**：钩爪激活（含钩头飞行中）→ 钩爪的目标；否则在滑索上 → 滑索的目标；否则（摆荡，S21 没有）→ 0。共用状态按 SmoothCD（ω 6.6667，snap 0.001）追这个目标。脱钩那一帧起钩爪目标为 0。

滑索的横滚大小**完全来自眼睛相对绳子的左右偏移**（绳子在正上方时是 0），而这个偏移来自 §3.9 的滑索眼睛偏移。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 钩爪距离满值 | 3.810 m | 150 u | 2.083 H | — | [数据] |
| 钩爪视角满值 | — | 65 ° | — | — | [数据] |
| 钩爪最大 `grapple_rollMax` | — | 20 ° | — | rodeo 实测 13.9° | [数据] [实测] |
| 滑索视角 | — | 30–50 ° | — | — | [数据] |
| 滑索强度 / 最大 | — | 0.7 / 25 ° | — | 实测 −1.44 … +0.28° | [数据] [实测] |
| 共用平滑 ω | — | 6.6667 /s | — | 到 63 % 约 0.32 s | [反编译] [实测] |

#### 实现模板

```
target = 0
if grapple.active: target = −rollTerm(eye, grapple.point, aim, GRAPPLE)
elif zip.riding:   target = −rollTerm(eye, ropePointAboveEye(), aim, ZIP)
smoothCD(ropeRoll, ropeRollRate, target, 6.6667, dt, 0.001)
```

Unity：NC.cs `RopeRollTerm`、`GrappleRollTerm`、`ZiplineRollTerm`；`grappleRollDist` 150、`grappleRollView` 65、`grappleRollStrength` 1、`grappleRollMax` 20；`zipRollViewMin` 30、`zipRollViewMax` 50、`zipRollStrength` 0.7、`zipRollMax` 25；`ropeRollOmega` 6.6666665、`ropeRollSnap` 0.001；开关 `nativeRollSmooth`（false = 旧版各自一阶 6.667 / 3.0）、`zipRopeHorizontal`（false = 三维最近点）。

#### 验收

- `NativeCameraTests.GrappleRollTermFollowsTheNativeFormula`、`ZiplineRollTermFollowsTheNativeFormula`、`ZiplineRollRunsOnlyOnTheRope`；`F7CameraTests.GrappleRollUsesTheSharedSpringAndOnlyTheCamera`、`ZiplineRollDecaysOnTheSharedSpring`。
- 对照：N12 钩爪 7 次全程 rms 0.24–0.45°，rodeo 峰值 13.7–13.9°（实测 13.9°）；N10 滑索 1585 帧 rms 0.043°；N10_zip 5 个片段横滚峰值逐个差 ≤ 0.06°，滑索指标 10 / 10。
- 已知差别：游戏身体的钩爪比 R5 早脱钩，所以游戏里峰值偏低（FEEL §10）；rodeo 公式 18.5° 对实测 13.9° 没查（B07-3）。

#### 出处

- CR §3.5；N10 §5、§6 C-11；DIFF C-12、CAM2 K-7；D-24、D-42、D-54。main
- CAM2 §4.2（水平投影）。main
- [反编译] `Grapple_CameraRoll` 0x1407fac60、`Zipline_CameraRoll` 0x1407fb580（S21 只走分支 A）、`View_CalcRoll` 0x140afc480。

### 3.9 滑索眼睛偏移 `zip_eye_offset`

#### 原理

挂在滑索上时，眼睛相对握点慢慢下沉（一次 1–2 s 的滑行降 5–9 u），并且前后左右轻轻漂。这让"吊在绳子下面"有重量感，也让绳子不总在正上方，从而产生 §3.8 的滑索横滚。目标是一个慢变的噪声，用 SmoothCD 跟着，下绳后回到 0。

#### 规则和公式

```
// 在绳上（运动实体上的绳子）时，偏移目标（按偏航坐标：前、左、上；单位 u）
x, y, z = 身体原点 × 0.001            // 1/u
z'      = z + 0.02 × 游戏时间（s）
前 = 5 · N(x, y, z')
左 = 5 · N(z', x, y)
上 = 5 · N(y, z', x);  若 上 > −4：上 = −8 − 上          // 所以在 −13 … −4 之间
// 不在绳上：目标 0
每轴 SmoothCD（ω 4，snap 0）追目标
眼睛 += 前·forward_h + 左·left_h；眼高 += 上
```

N = Ken Perlin 2002 年的 improved noise（参考置换表、fade 6t⁵ − 15t⁴ + 10t³、12 边梯度），R5 用的表和参考表逐项相同。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 噪声幅度 | 0.127 m | 5 u | 0.0694 H | — | [反编译] |
| 上下目标范围 | −0.330 … −0.102 m | −13 … −4 u | −0.181 … −0.056 H | — | [反编译] |
| 折回基准 | −0.2032 m | −8 u | −0.111 H | — | [反编译] |
| 噪声空间频率 | 0.03937 /m | 0.001 /u | 0.072 /H | — | [反编译] |
| 噪声时间频率 | — | 0.02 /s | — | — | [反编译] |
| SmoothCD ω | — | 4 /s | — | — | [反编译] |
| 一次滑行结束时的眼高 | 1.55–1.68 m | 70 → 61–66 u | 0.85–0.92 H | 实测 65.5–65.9（N10） | [实测] |

#### 实现模板

Unity：NC.cs `PerlinNoise.Noise`、`zipViewOffset`（开关）、`zipOffsetNoise` 5、`zipOffsetZBase` −8、`zipOffsetZFold` −4、`zipOffsetOmega` 4、`zipNoiseScale` 0.001、`zipNoiseTime` 0.02；对照重放时 `noiseTimeOffset` 设成 R5 片段开头的游戏时间。

#### 验收

- `Cam2CameraTests.ZiplineViewOffsetLowersTheEyeOnTheRope`、`PerlinNoiseMatchesTheReference`。
- 对照：N10 5 个片段眼高 R5 / Unity 65.70 / 65.70、65.88 / 65.87、65.47 / 65.57、65.54 / 65.54、65.58 / 65.58。

#### 出处

- CAM2 §4.2–§4.4；CR §3.12；DIFF CAM2 K-7；D-54。main
- [反编译] 写偏移 0x140b110c0（player+0x2f78），加到眼睛 0x140af24b0；Perlin 0x140521e90，置换表 0x14167c490；绳子挂在运动实体上的判断 0x140749e20。

### 3.10 FOV：滑铲 `slide_fov`、开镜 `ads_fov`；冲刺和加速没有

#### 原理

R5 的移动里 FOV **只在滑铲时变**：放大 10 %，0.25 s 线性进出。跑多快、冲刺、Octane 兴奋剂、钩爪拉人，FOV 都不变（P2）。开镜是另一套（09 章），镜头这边只管它怎么和滑铲 FOV 拼起来。

#### 规则和公式

1. 滑铲 FOV 比例 m：目标 = 滑铲中 1.1，否则 1.0；线性走，进出各 0.25 s（每秒 0.4）。
2. m 乘的是 **4:3 画面的水平 FOV**。Unity 用竖直 FOV，所以：

   ```
   h  = 2·atan(tan(v/2) × 4/3)          // 竖直 → 4:3 水平
   v' = 2·atan(tan(m·h/2) × 3/4)        // 乘 m 再回到竖直
   ```

3. 开镜 FOV（09 章）：R = 基础 + (zoom_fov × S − 基础) × smoothstep(zf)，zf 线性。度数是本地设置，**要学的是比例**（R-301 tan 比 0.712）。
4. 拼法：FOV = 基础 + 开镜（smoothstep）；滑铲 × 1.1（DP §6.1）。
5. 冲刺 FOV、速度 FOV、技能 FOV、加速（兴奋剂）FOV：**没有**。做了就是偏离（§6）。
6. FOV 设置：菜单按 Apex 的数（4:3 水平，70–110）显示和输入；默认竖直 70° = Apex 86（D-44）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 滑铲 FOV 倍数 `slideFOVScale` | — | 1.1 × | — | 实测 89 → 97.9 | [数据] [实测] |
| 进 / 出时间 | — | 0.25 s / 0.25 s，线性 | — | — | [数据] [实测] |
| 冲刺 / 速度 / 技能 FOV | — | 0（没有） | — | — | [实测] |
| 默认 FOV | — | 竖直 70 ° = Apex 86 °（4:3 水平） | — | 70–110（Apex 数） | [设计] D-44 |

#### 实现模板

Unity：NC.cs `slideFovScale` 1.1、`slideFovLerpIn` 0.25、`slideFovLerpOut` 0.25、`fovAspect` 4/3、`VerticalFov(vfov, scale)`；`CameraFeedbackSettings.VerticalFromApex` / `ApexFov`（`Camera/M55/CameraFeedback.cs`）。开镜在武器层（09 章）。

#### 验收

- `NativeCameraTests.StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt`；`F7CameraTests.FovSettingIsApexFov`。
- 对照：C3 89 → 97.9（× 1.1）。

#### 出处

- CR §2.4、§3.6；C3 §1；NC §7；D-44。main
- DP §6.4（开镜）、P2（没有速度 FOV）。main

---

## 4. 组合规则

### 4.1 每帧的叠加顺序

#### 原理

镜头每帧按固定顺序拼出来，每一行都是"相加"。新效果只能**加进某一行**，不能改前面已经算好的值。这保证：(1) 任何效果都不会改到瞄准；(2) 加一个新效果不会改变旧效果的样子。

#### 规则和公式

```
位置       = 身体原点（插值） + 眼高（下蹲比例、冲刺下沉） + 滑索眼睛偏移
俯仰、偏航 = 瞄准 + 翻越动画镜头 + rodeo 平滑 + punch1 + (1 − f)·punch2 + drift / 跑步晃动
横滚       = 侧移（R5 为 0） + 跑墙 + 闪避（S21 没有） + 滑铲倾斜 + 冲刺倾斜 + 绳子横滚（三选一） + punch 横滚
             → 按 360° 取模折回 ±180°，不封顶
FOV        = 基础 + 开镜（smoothstep）；滑铲 × 1.1
（之后）     屏幕震动（世界事件，§2.9）
```

R5 原生 CalcView 的步骤（CAM2 §5）：1 眼睛位置；2 眼睛角度 = 瞄准；3 观看实体 slerp（过场 / 处决，唯一的覆盖式，移动里不出现）；4 翻越动画镜头；5 rodeo 平滑；6 punch；7 drift / 跑步晃动；8 横滚汇总。之后视图设置再做驾驶舱弹簧（S21 为 0）、屏幕震动。

#### 实现模板

参考实现分两段：每条命令一次 `Observe`（只读身体），每个渲染帧一次 `Render`（插值）。

```
// 单位：u、°、s；Source 符号
Observe(body, aim, cmd):                     // 身体这条命令跑完以后
    dt = 1/120
    // 1. 眼高
    eye.step(down, sliding, sprinting, dt); h = eye.height()
    // 2. 弹簧：先推进，再加 kick
    for axis in p1, p2: axis.step(65, 9, dt)
    if landed:        kick(land …)                    // §2.3
    if jumped:        kick(jump …)                    // §2.1
    if doubleJumped:  kick(double_jump …)             // §2.2
    if leftZipline:   kick(zip_detach …)              // §2.4
    // 3. 横滚各项
    slideRoll  = slideTilt.step(…)                    // §3.5
    sprintRoll = sprintTilt.step(yawRate(aim), …)     // §3.6
    zipOff     = zipOffset.step(…); h += zipOff.up    // §3.9
    ropeRoll   = ropeRoll.step(target(eyePos, aim))   // §3.8
    wallRoll  += (wallTarget − wallRoll)·min(1, 6·dt) // §3.7
    // 4. FOV
    fovScale   = moveToward(fovScale, sliding ? 1.1 : 1, 0.4·dt)   // §3.10
    // 5. 小的持续项
    drift, driftYaw = …; bobPitch, bobYaw = …          // §3.2、§3.3
    mantle = traversalPitch(…)                         // §2.5
    // 6. 拼起来（强度组 §4.6）
    pitch = (p1.pitch.x + p2.pitch.x + drift + bobPitch + mantle) · heightI
    yaw   = (p1.yaw.x + p2.yaw.x + driftYaw + bobYaw) · heightI
    roll  = wrap180(slideRoll + sprintRoll + ropeRoll + wallRoll + p1.roll.x + p2.roll.x) · rollI
    fov   = 1 + (fovScale − 1) · fovI
    prev = cur; cur = {time, h, zipOff.xy, pitch, yaw, roll, fov}

Render(renderTime, bodyPosInterp, aimYaw, aimPitch):
    a = clamp01((renderTime − prev.time) / (cur.time − prev.time))
    L(x) = prev.x + (cur.x − prev.x)·a
    cameraPos   = bodyPosInterp + (L(dx), L(dy), L(h))
    cameraRot   = aimRotation(aimYaw, aimPitch) ∘ visualRotation(L(pitch), −L(yaw), −L(roll))   // Unity 符号
    fieldOfView = verticalFov(baseFov, L(fov))
```

要点：

- 镜头**只读**身体：不写电机、能力、输入、命令循环（SKILL 规则 1）。镜头需要的事实（"这条命令起跳了""二段跳计数"）由能力暴露只读字段，且不能改变任何模拟输出。
- **画面旋转挂在瞄准枢轴的子节点上**：瞄准枢轴只吃鼠标，画面效果是它下面的一层，所以从结构上保证不写回瞄准。画面中心偏离瞄准时，准星画在真实瞄准线上（`CameraRig`）。
- 身体重建 / 传送后的第一条命令（`!sameBody`）：所有状态直接设成目标值、弹簧清零、不加 kick。

Unity：NC.cs `NativeCameraFeedback.Observe`（每条命令，由 `PracticeSession.OnCommand` 调用）、`Update(renderTime, renderPos, aimYaw, aimPitch)`（渲染插值，返回 `CameraPose`）；`HSD-Unity: Assets/HSD/Game/Runtime/CameraRig.cs`（`AimPivot` 下挂画面旋转）；模型切换 `Camera/CameraModels.cs`（`CameraModel`、`ICameraFeedback`）。

#### 验收

- `NativeCameraTests.TheSimulationIsUntouchedAndTheAimIsRaw`：镜头开到最大和不要镜头，两种配置 × 3 套装备，模拟输出逐位相同，瞄准是鼠标原值。
- `NativeCameraTests.CommandStatesDoNotDependOnTheRenderRate`：30 / 60 / 144 / 240 Hz 渲染，命令状态相同。
- 回放基线：M1–M4 报告和 N7 逐字节相同（11 章）。

#### 出处

- CAM2 §5；N10 §2；CR §3.9、§8；DP §6.1。main
- SKILL `SKILL.md` 规则 1、2、4；`references/channels-and-composition.md`。HSD-Unity main
- [反编译] CalcView 0x1407f2bb0 / 0x1407ee480；视图设置 0x140838830；rodeo 平滑 0x1407f0de0。

### 4.2 同时来几个效果：相加、不封顶、单项上限、三选一

#### 原理

R5 没有"哪个效果优先"的规则。所有 kick 都进同两组线性弹簧，所以两个事件同时来，就是两个响应相加；横滚所有项相加，没有总上限。之所以不会失控，是因为**每一项自己有上限**（P8）。唯一的例外是互斥的东西（钩爪 / 滑索 / 摆荡的绳子横滚），它们共用一个状态，三选一。

#### 规则和公式

1. **kick 相加**：同一条命令上的多个 kick 都加；前一个没衰减完的继续衰减。没有取消、没有上限。
2. **横滚相加后折回**：横滚 = 各项之和，按 360° 取模折回 ±180°；**不夹 ±40°**（`maxCameraRoll` 40 只封滑索分支 B 自己那一项，S21 不走）。
3. **单项上限**：滑铲 15°、冲刺 2°、钩爪 20°、滑索 25° × 0.7、跑墙 10°（TF2 15°）。总和实际很少超过 40°。
4. **三选一**：绳子横滚只取一个来源，共用一个 SmoothCD 状态，切换时连续。
5. **控制效果不叠，反馈效果叠**：状态效果（减速等）取最大；镜头反馈都相加（DP P8 反例）。
6. **一个事件替换另一个事件**不是优先级：例如自己按出来的下砸落地不想用落地律，就在这次落地上换一个 kick（用一个只读字段关掉原触发），同一条命令上的其他 kick 照样相加（SKILL `channels-and-composition.md`）。

实测的组合：

| 组合 | R5 | Unity（现在） |
|---|---|---|
| 落地马上再跳（落地那条或下一条起跳） | 4.96–5.56°（落地 + 起跳相加） | 5.01–5.56° |
| 跳下 232 u 岩石 | 起跳 2.67–3.64°；落地 12.3–15.6° | 2.66–3.64°；12.4–14.1° |
| 翻越（起跳 punch + 翻越镜头，120 u 冲刺） | 起跳约 3°，0.49 s 时 4.5–5.3° | 约 3°；4.6° |
| 冲刺转向 + 钩爪（rodeo） | 横滚 = 冲刺倾斜 + 钩爪横滚 | 相同 |

#### 实现模板

见 §4.1：`kick()` 只做 `v +=`；横滚 `wrap180(sum)`。

Unity：NC.cs `rollWrap`（true = 折回；false = 旧版夹 ±40，`maxRoll` 40）。

#### 验收

- `Cam2CameraTests.RollSumIsWrappedNotCapped`、`LandingKickAndJumpPunchAdd`。
- 写新效果时：列出它能真实同时发生的组合，测总和"还能接受"（DP §9.2 镜头清单），而不是给总和加夹子。

#### 出处

- CAM2 §5、§5.1；CR §8；DIFF CAM2"横滚合成"；D-53。main
- DP P8。main

### 4.3 瞄准、画面、子弹分开存（P1、T3）

#### 原理

玩家要能信任"我瞄的地方"。镜头可以跳，瞄准不跟着跳。所以三种角分开存，任何路径都不把画面写回瞄准。画面偏离准星时，要说清楚子弹去哪（P1）。

#### 规则和公式

```
瞄准 aim    = 只来自鼠标（鼠标先抵消反向的武器 punch，减到 0 为止，剩下的进 aim）
画面        = aim + 翻越动画 + punch1 + (1 − f)·punch2 + drift / 跑步晃动；横滚另算
子弹        = aim + punch1 + 完整 punch2（这一发 kick 之前） + 开镜 drift + 扩散
```

- 落地 26 次瞄准角变化 0.0；起跳、翻越眼睛角度全程 0（实测）。
- **移动 punch 也进子弹**：落地 0.1 s 后开枪，400 u 落地时子弹低 16–17°，差 ≤ 0.28°（FG §1，11-13 推翻了"移动 punch 不进子弹"的推断）。也就是说开镜（fraction 0）时子弹永远打在屏幕中心。
- 准星：开镜 fraction 0 的枪准星和子弹一体；fraction 大的枪（Kraber 0.75 等）准星和子弹有差，由 fraction 决定谁承担差距，要写明。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 镜头效果对瞄准角的影响 | — | 0（26 次落地全 0） | — | — | [实测] |
| 子弹 − (aim + punch1 + punch2) | — | ≤ 0.28 ° | — | — | [实测] |

**HSD 现在**：Unity 的画面和瞄准分开存（逐位测试过）；子弹还是 aim + 武器 punch，**没有 punch1 和开镜 drift**（§2.10，写进 `_notes`）。

#### 实现模板

见 §4.1（画面挂在瞄准枢轴下）和 09 章（子弹方向）。

#### 验收

- `NativeCameraTests.TheSimulationIsUntouchedAndTheAimIsRaw`（瞄准逐位等于鼠标，包括 kick 进行中的帧）。
- 子弹：落地后立即开枪，子弹方向 = aim + punch1 + punch2（09 章，HSD 还没做）。

#### 出处

- DP P1、T3（#122 版）；FG §1、§5；EM §1。PR #122，还没合并
- C3 §1；CAM2 §2.2。main

### 4.4 镜头只转不移；持续的克制，一次性的响亮（P2）

#### 原理

画面的位置来自身体，所以位移永远可信：玩家看到自己在哪，就真的在哪。持续状态几乎不动镜头，让人能长时间看清楚；一次性事件可以很大，因为很快结束，而且告诉你"这一下有多重"。

#### 规则和公式

| 类 | 允许 | 不允许（做了就是偏离） |
|---|---|---|
| 位置 | 眼睛随身体姿态：蹲 / 滑（32）、冲刺（−6）、滑索（−4 … −13） | 位置 kick（落地往下沉几 u、起跳往上抬）、身体惯性滞后 |
| 持续旋转 | 只按相对量：滑铲倾斜（速度对视角）、冲刺倾斜（转速）、绳子横滚（点对视线）；极小的 drift ±0.2°、跑步晃动 ±0.25° / ±0.45° | 侧移横滚、按速度的倾斜、明显的持续摆动 |
| 持续 FOV | 只有滑铲 × 1.1 | 速度 FOV、冲刺 FOV、技能 FOV、速度线 |
| 一次性 | 进弹簧的 kick，可以很大（落地最多约 44°、下滑索 18°）；动画镜头（翻越 5°、拉栓 5°） | 自己的震屏（震屏是世界事件） |

量级对比：最大的持续项（滑铲倾斜 15°）只在斜着滑时出现；正常跑动时持续项合计不到 1°。一次性事件 2–44°。

#### 实现模板

新效果先判它属于哪类，再选通道（§5 第 3 步）。

#### 验收

`NativeCameraTests.ContinuousTermsStayInsideTheirMeasuredBounds`（持续项上下限钉死）。DP §9.2 镜头清单"有位置 kick、速度 FOV、自己的震屏吗？有的话写成偏离"。

#### 出处

- DP P2、§6.5。main（#122 补了开枪 / 受击没有震屏）
- CR §1（总表：两版对比）。main

### 4.5 新事件的力度规律：平常 2、主动超常 4.5、退出大动作 10

#### 原理

R5 的几个移动 kick 的基础值排成一个清楚的梯子：**平常的动作 2**（起跳），**主动超出常规的 4.5**（二段跳），**退出一个大动作 10**（下滑索）。只有落地随速度变（因为落地是"摔"，轻重由物理决定）。随机项约为基础的 ±10–25 %。设计新事件时，先定它在梯子上的位置，再在两个相邻锚点之间取基础值。这是**解读**，不是 Respawn 的说法。

#### 规则和公式

```
俯仰冲量 = (基础 + 随机幅度 × r) × 20，r ∈ [−0.5, 0.5]
画面峰值 ≈ 0.0771 × 基础 × 20 = 1.542° × 基础
```

| 档 | 例子 | 基础 | 随机幅度（相对基础） | 画面俯仰峰值（r = 0） |
|---|---|---|---|---|
| 平常的动作 | 起跳、滑铲跳 | 2 | 1（±25 %） | 3.1° |
| 主动超出常规 | 二段跳 | 4.5 | 1（±11 %） | 6.9° |
| 退出大动作 | 下滑索 | 10 | 3（±15 %） | 15.4° |
| 摔（随速度） | 落地 | s × 2，s = 0–12 | 0.75（±19 %） | 0–37° |
| [设计] 示范 | 地面冲击落地（DP §9.4） | 8 | 2（±12.5 %） | 12.3° |

其他规律：

- 偏航随机幅度和俯仰随机幅度同量级（起跳、二段跳 1，下滑索 10）；横滚可以有基础（起跳 0.9，总向一侧）或纯随机。
- 准备动作可以反向（往上抬，负冲量），比主动作小（DP §9.4 示范：按键时 −(1 + 0.5r)·20，约 −1.5°）。
- 主动按出来、频率高的动作**不用落地律**，用固定基础值（R5 里主动动作都是固定基础）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 平常档基础 | — | 2 | — | — | [反编译]，规律是解读 |
| 主动超常档基础 | — | 4.5 | — | — | [反编译]，规律是解读 |
| 退出大动作档基础 | — | 10 | — | — | [反编译]，规律是解读 |
| 峰值 / 基础 | — | 1.542 ° | — | — | [算] |

#### 实现模板

新事件写成 `NativeCameraParams` 里的一组 `xxxPitchBase` / `xxxPitchRandom` / `xxxYawRandom` / `xxxRollRandom` + 开关 + 自己的盐，在 `Observe` 的 kick 段加一行（照 `jumpPunch` 抄）。

#### 验收

见 §5 第 6 步。

#### 出处

- DP §6.2"写新事件的规律"、§9.4（地面冲击示范）。main
- CAM2 §2.1、§7（三个基础值的反编译）。main

### 4.6 强度设置和开关

#### 原理

每个镜头效果都要能被玩家调小到 0（防晕），也要能被开发者单独切回旧版（留档规则）。R5 菜单里的防晕选项具体有哪些没研究（§7），HSD 先按三组强度做。

#### 规则和公式

| 强度组 | 乘在哪 | 1 = |
|---|---|---|
| 高度强度 `heightIntensity` | 俯仰、偏航的全部 kick 和持续项（punch、drift、跑步晃动、翻越） | 原生 |
| 横滚强度 `rollIntensity` | 横滚总和 | 原生 |
| FOV 强度 `fovIntensity` | 滑铲 FOV 的 (m − 1) | 原生 |

- 每个新效果必须属于一个强度组（或新开一组），强度 0 时**精确为 0**，"Off"预设下关闭（SKILL 规则 5）。
- 每个改动都有开关回到旧版（本章各项"实现模板"里写了开关名）。整批切回：`NativeCameraParams.SetCam2(false)`、`SetFnd(false)`；`CameraFeelBatch -preCam2` / `-preFnd` / `-preF7Roll` / `-preD72` 等。
- 镜头模型：原生（默认，D-18）/ M5.5（保留，菜单"Camera model"）。

#### 实现模板

Unity：`CameraFeedbackSettings`（`heightIntensity`、`rollIntensity`、`fovIntensity`、`baseFov`、`MaxIntensity`，`Camera/M55/CameraFeedback.cs`）；NC.cs `Observe` 末尾 `hI`、`rI`、`settings.fovIntensity`。

#### 验收

`NativeCameraTests.IntensityZeroIsTheBareCamera`（强度 0 = 只有眼高的裸镜头）、`M55IsKeptBehindTheInterface`。

#### 出处

- CR §6、§7；D-18。main
- SKILL 规则 5；`references/verification.md`。HSD-Unity main

---

## 5. 设计一个新镜头效果（步骤）

用户的标准：新加的东西，手感和设计方法也要符合 R5。照下面的步骤做，第 1 步写简报，写完再碰代码。

### 5.1 写简报，找两个 R5 锚点

- 这个动作每个阶段（开始 / 持续 / 结束 / 被打断）身体应该感到什么？
- 哪个物理量驱动手感：速度、落地 |vz|、蓄力、绳子张力、离墙距离？先读这个动作的实测模型（02–06 章），把效果绑到真实门槛上。
- 找**两个强度相近的 R5 锚点**，带数字（§2 的 kick 表、§3 的持续通道）。找不到任何锚点就停下来问（判定会是偏离）。

### 5.2 判定：在 R5 里 / 有锚点的延伸 / 明确偏离

按 DP §9.2 的通用清单和镜头清单逐条过，把结论写进简报：

- 有位置 kick、速度 FOV、自己的震屏、侧移横滚、身体惯性、速度线吗？有 → 明确偏离（§6）。
- 持续效果是不是按相对量？有没有自己的上限？
- 写瞄准了吗？写了 → 不行。
- 同时发生的组合，总和还能接受吗？

明确偏离可以做，但要标成偏离、放在开关后面，默认不开，先问用户。

### 5.3 选通道

| 想要的 | 用 | 不要 |
|---|---|---|
| 一次性的"这一下有多重" | 往 punch 弹簧加冲量（§1.1），不新建弹簧、不给自己的 k / c | 专门写一段动画曲线、写优先级 |
| 一段姿态变化（降低、升高） | 现有的下蹲比例（§3.1），或一个线性进度 + 读者曲线（§1.2） | 新的位置通道 |
| 跟着一个会动的东西倾斜 | 一个"朝点横滚"的项 + SmoothCD（§3.8），互斥的来源共用一个状态 | 一阶 lerp、各用各的平滑器 |
| 有动画的动作（翻越、拉栓） | 动画镜头挂点，0.15 s 淡入（§2.5） | kick 冒充动画 |
| FOV | 先问自己 R5 有没有。移动里只有滑铲 × 1.1 | 速度 / 技能 FOV（偏离） |

新效果只能**加进** §4.1 的某一行。

### 5.4 定数值和形状

- kick：基础值按 §4.5 的梯子，在两个锚点之间取；随机幅度取基础的 ±10–25 %；偏航、横滚随机和俯仰同量级。
- 定时过渡：从动作自己的时长出发（例如滑铲 0.2 s 下蹲），曲线加在读者上。
- 追目标：ω 先用现有的（绳子 6.667、滑索偏移 4）。
- 所有新值标 [设计]，直到用户试玩过。

### 5.5 打断表

列一张表：这个状态被跳、发射、别的驱动、传送、身体重建打断时，每个通道怎么办（kick 继续衰减；进度从当前值往回走；目标变 0 由 SmoothCD 收回；身体重建时全部直接归位、不加 kick）。

### 5.6 实现和验收

1. 按 §4.1 只读身体；需要的事实由能力暴露只读字段，模拟输出逐位不变。
2. 测试（照 `NativeCameraTests` / `Cam2CameraTests` 抄）：
   - kick：峰值、峰值时间、回到静止、和已有事件同命令相加；
   - 持续项：上下限钉在 `ContinuousTermsStayInsideTheirMeasuredBounds`；
   - 镜头开到最大 vs 不要镜头，两种配置 × 3 套装备，模拟逐位相同，瞄准等于鼠标（含效果进行中的帧）；
   - 30 / 60 / 144 / 240 Hz 命令状态相同；
   - 强度 0 精确为 0，Off 预设关闭；
   - 回放基线逐字节不变；构建 smoke。
3. 不为了通过测试放宽上限；上限本身错了，写明为什么错。

### 5.7 留档

- 共享日志写一条：选中的、没选的，各自的数据和理由。
- PR 里有决定的，同一个 PR 加 DECISIONS 时间线和 D-xx 行；和 R5 不同的写进 R5-DIFF-ARCHIVE；旧版留开关。

### 5.8 示范：地面冲击（DP §9.4，全部 [设计]）

空中按键，高速下砸，落地有重量感。R5 没有这个动作。

| 阶段 | 做法 | 依据 |
|---|---|---|
| 按键 | kick：俯仰 −(1 + 0.5r)·20（抬一下），峰值约 −1.5° | 准备动作，比起跳小；反向 kick 武器一直在用 |
| 下砸 | **不加任何持续效果**：不动 FOV、不加速度线 | P2 |
| 姿态 | 下蹲比例目标 1，用滑铲的 0.2 s，smoothstep | 现有通道 |
| 落地 | kick：俯仰 (8 + 2r)·20，偏航 3r·20，横滚 4r·20；峰值 12.3° ± 1.5° | 锚点：二段跳 6.9°、下滑索 15.4°；主动动作，在两档之间 |
| 不用落地律 | 这次落地关掉 §2.3 的触发（一个只读字段），换成上面的 kick | 落地律是"摔"；1100 u/s 时会到约 36° |
| 叠加 | 同一条命令滑铲跳就相加 | P8 |
| 瞄准 | 不动，逐位测试 | P1 |

判定：有锚点的延伸。**8 这个基础值没有 R5 数据**，只有上下锚点，要试玩。

#### 出处（§5 整节）

- DP §9.1、§9.2、§9.4、§9.5。main（#122 改了 §9.5 两行）
- SKILL `SKILL.md`（流程 1–7、何时停下来问）、`references/design-brief.md`、`curves-and-damping.md`、`transitions-and-interrupts.md`、`verification.md`。HSD-Unity main

---

## 6. R5 没有的东西（做了就要写成偏离）

| 效果 | R5 | HSD 里在哪 |
|---|---|---|
| 速度 FOV | 没有 | M5.5：+8° × clamp((v − 200)/500) [设计] |
| 技能 FOV（钩爪、兴奋剂、喷气等） | 没有 | M5.5：+2 … +6° [设计] |
| 速度线 | 没有 | M5.5：330 → 650 u/s [设计] |
| 身体惯性（眼睛落后身体） | 没有 | M5.5：0.006 × 速度误差，最多 1.5 u [设计] |
| 位置 kick（lift / dip） | 没有 | M5.5：起跳 lift 1 u、落地 dip 4–8 u 等 [设计] |
| 侧移横滚 | 没有（`sv_rollangle` 0） | M5.5：1.5° × min(1, v/300) [设计] |
| 自己的屏幕震动 | 没有（震屏是世界事件）；开枪、受击都没有 | — |
| 受击镜头（铁驭） | 没有 | — |

M5.5 是用户 10-21 认可过的另一种好语言（D-05），10-24 改成默认原生（D-18），代码保留在 `HSD-Unity: Assets/HSD/Game/Runtime/Camera/M55/CameraFeedback.cs`（`CriticalSmoother`、`CameraFeedbackDesign`），菜单可以切回。M5.5 的 kick 是临界阻尼"鼓包"（不回弹），这是和 R5 最大的结构差别。

出处：CR §1、§4；DP P2、§6.5、§9.5；D-05、D-18。main

---

## 7. 待研究

这些都没研究，本章不展开，清单和要测什么在 [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md)：

- **A-1 防晕和可关闭选项**：R5 菜单有哪些、关掉后哪些通道归零；"关掉"以后落地轻重的信息怎么补。
- **A-2 屏幕效果**：暗角、速度线、后处理和镜头通道的先后。
- **A-3 音效和镜头同步**：落地 / 起跳 / 滑铲声音和 kick 的时间差，开枪声和后坐的先后。
- **A-4 第三人称 / 驾驶舱切换**：过渡曲线、碰撞避让、FOV。

本章另外发现的缺口（建议进 99，写在 `_notes/hb-ch07.md`）：B07-1 二段跳没录像；B07-2 跑墙开始 / 超时 punch 的值没读；B07-3 rodeo 钩爪横滚 13.9° 对公式 18.5°；B07-4 拉栓镜头只量 3 把；B07-5 跑步晃动相位是推断；**新**：跳板 / 重力炮 / 抓墙 punch 的值没读；铁驭爆炸震屏没测；铁驭近战镜头没测。
