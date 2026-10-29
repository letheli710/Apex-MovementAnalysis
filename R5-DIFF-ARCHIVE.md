# 和 R5 不一样的地方（存档）

2026-10-27 起，项目以"按 R5 复刻"为核心（[DECISIONS.md](DECISIONS.md) D-36）：手感对照找到的差别，原则上都改成 R5 的样子，以后的 Unity 版本也用这一版。

这份文件把**改之前那一版**（下面叫"旧版"，即 2026-10-26 合并的 HSD-Unity#40 / research #62）和 R5 不一样的地方存下来，方便以后回头比较或切回去。每一项写：
- 旧版是什么样；
- R5 是什么样；
- 现在怎么处理（改了 / 还没改 / 不改）；
- 想切回旧版怎么做。

数字来自手感对照（[research/feel/FEEL.md](research/feel/FEEL.md)），叠图在 https://claude.ai/artifact/P1mjgrbW1Yoiu9HdukTbDv 。

---

## 一、这次按 R5 改了的（F6，HSD-Unity `f6/r5-faithful`）

### A-1 钩爪往墙上拉

| | 旧版 | R5 | 现在 |
|---|---|---|---|
| 钩子打在哪 | 从身体上方 60 u 处沿视线打出去 | 从真实眼睛打出去：站着 70、冲刺 64、蹲 / 滑 32（M10 的 72 次钩点都在这条线上，误差 2 u 以内） | 按 R5 |
| 横向刹车 | 只在沿绳速度追上目标、或按着方向键时刹（M10-A 拟合出来的） | 一直刹，但两部分不刹：向下的那部分（`grapple_dontFightGravity`），以及朝视线方向的那部分（原生 `Grapple_PullAccel`） | 按 R5 |
| 结果（M4 往墙上拉的 4 个片段） | 最高点比 R5 低 15–22 u | — | 低 5–10 u（剩下的见第二部分） |

切回旧版：`MovementConfigs.NativeGrapple()` 里把 `g.s21.nativeEye`、`g.s21.nativeCrossBrake` 设成 false。

### K-1 / K-2 落地 kick 的随机数

| | 旧版 | R5 | 现在 |
|---|---|---|---|
| kick 公式 | 和 R5 一样 | 强度按落地速度分段，俯仰 × (2 + 0.75·r₁)，横滚 × r₃ | 不变 |
| 随机数 r | Unity 自己的哈希，同一条命令号永远同一个值 | 用落地那条命令的命令号：MD5 → 种子混合 → 线性同余随机数（Frida 在 R5 里逐个对上） | 按 R5 |
| 结果 | 同一高度每次 kick 一样；900 u 落地 32°（R5 34–43°），中小落差横滚偏小 | 每次落地不同 | 用 R5 的命令号重放时逐次对上：俯仰峰值 32 / 34 一致，横滚 32 / 34 一致 |

切回旧版：原生镜头参数 `NativeCameraParams.r5Random = false`。

### K-3 跑步晃动（俯仰）

| | 旧版 | R5 | 现在 |
|---|---|---|---|
| 俯仰幅度 | 正弦幅度 0.335°（N6 带转向的片段量出来的，把转向混进去了） | 直线冲刺 0.22–0.26°（每步峰峰约 0.50°），三个会话一致 | 0.25° |
| 开始冲刺时 | 以每秒 4 的速度渐入，第一步只有一半 | 第一步就几乎是全幅 | 每秒 20 渐入 |

旧对照里"三个 R5 会话彼此不一样"是指标的问题：整段峰峰值把慢漂移算进去了。改成按步算以后三个会话一致。

切回旧版：`NativeCameraParams.swayPitchAmp = 0.335`、`swayFade = 4`。

### K-4 眼高（新发现）

| | 旧版 | R5 | 现在 |
|---|---|---|---|
| 站立 / 走路 | 64 | 70（setfile `viewheight` 0 0 70） | 70 |
| 冲刺 | 64 | 70 − 6·sin(冲刺比例·π/2)（`sprintViewOffset` −6，原生 `Sprint_ViewOffset`）；开始冲刺 0.16 s 后以每秒 1.25 降下去，停下 0.11 s 后以每秒 6.67 回来 | 按 R5 |
| 蹲 / 滑 | 32 | 32 | 32 |

旧版的 64 是 C3 在冲刺中量的，被当成了站立眼高。这一项同时影响钩爪打出去的位置（A-1）。

切回旧版：原生镜头参数 `eye = NativeEyeParams.PreF4()`。

### C-12 钩爪和滑索横滚的平滑（F7，HSD-Unity `f7/roll-fov`，D-42）

"旧版"在这一项指 F6 那一版（HSD-Unity#41）。

| | 旧版 | R5 | 现在 |
|---|---|---|---|
| 平滑 | 钩爪、滑索各一个一阶平滑：钩爪每秒 6.667，滑索每秒 3.0（N10 拟合） | 两者**共用一个**临界阻尼弹簧（SmoothCD，值 + 速度，ω = 6.667，原生 `View_CalcRoll` 0x140afc480）；目标和当前都小于 0.001 时直接归零 | 按 R5 |
| 钩爪什么时候有目标 | 挂上以后（准备 + 拉动中） | 钩爪激活就有，钩头飞行中也算（朝飞行中的钩头）；脱钩那一帧起是 0 | 按 R5 |
| 结果：钩爪（N12，7 次） | 全程误差 rms 3.3–3.8°；rodeo（挂上后视角 180 °/s 转圈）峰值 19.0–19.3°，实测 13.9° | — | rms 0.24–0.45°，rodeo 峰值 13.7–13.9° |
| 结果：滑索（N10 Frida 1585 帧） | rms 0.083° | — | rms 0.043°（不拟合任何参数） |

手感对照管线里（Unity 自己的钩爪物理，14 个钩爪片段，FEEL.md §10）：和 R5 的逐帧误差 rodeo rms 平均 4.8° → 3.0°，视线离开 8.6° → 6.7°；旧版峰值 16.0–16.3°（rodeo）、17.2°（视线离开），现在 11.2–11.5°、12.8°，R5 12.2–15.2°、19.2°。现在峰值偏低是因为 Unity 的钩爪比 R5 早脱钩（还没改）。

体感上：钩爪横滚起得慢一些（到 63 % 要 0.32 s，旧版 0.15 s），快速转视角时峰值低 4–5°；稳态不变。滑索几乎看不出差别。

切回旧版：原生镜头参数 `NativeCameraParams.nativeRollSmooth = false`（旧的 `grappleRollRate` 6.667、`zipRollRate` 3.0 还在）。手感对照用 `CameraFeelBatch -preF7Roll` 跑旧版。

### R6U 斜坡滑铲五条（HSD-Unity `r6u/slope-native`，D-45 / D-46）

"旧版"在这一节指 F7 那一版（HSD-Unity#42）。差别来自 R6 实测（[research/phase2-local/slope/SLOPE-SLIDE.md](research/phase2-local/slope/SLOPE-SLIDE.md)），前后对照在 [R6U-COMPARE.md](research/phase2-local/slope/R6U-COMPARE.md)。五条都只改 Reference；**Fun 和回放电机不变**。开关都在 `R5MotorV2Params`（`[NonSerialized]`，`MovementConfigs.Reference()` 打开，`Fun()` 关回去）。

| # | 旧版 | R5 | 现在 | 差多少（旧版 → 现在，R5） | 切回旧版 |
|---|---|---|---|---|---|
| U-1 上坡步长 | 投影到坡面（Source 的做法）：水平前进 = \|v_h\|·dt·cos²θ | 投影后保持长度：水平前进 = \|v_h\|·dt·cosθ（比例 0.9862 / 0.9423 / 0.8693 / 0.7699，10–40°） | 按 R5 | 40° 上坡滑铲距离 84.4 → 124.8（R5 123.6）；比例 0.5868 → 0.7660（R5 0.7699） | `slopeUphillKeepStep = false` |
| U-2 坡上碰撞体底部 | 方盒：原点在坡面上方 16·tanθ（20° 5.82、40° 13.43），坡脚 / 坡顶按方盒角接触 | 相当于半径 16 的圆底：16·(1/cosθ − 1)（20° 1.03、40° 5.00） | 按 R5：圆底只用在坡面上，接触和法线按原点取；平顶（台阶、边缘）仍是方盒 | 坡上眼高低 4.8（20°）/ 8.5 u（40°）；上坡进入速度差 4–22 → −1…+4 u/s；平地→下坡转折速度差 8–13 → 2–5 u/s | `hullBottomRadius = 0` |
| U-3 换地面实体时重新开始滑铲 | 没有 | 原生 `SetGroundEntity` 换实体时调 `Slide_TryBegin`：距上次开始 ≥ 2 s 再加速 min(h + 172.5, 460)，计时重置（实测接缝、V 形谷底 398→461 等） | 按 R5，**可选三档**：`Props`（默认，静态关卡几何一个实体，平台算道具）、`Off`（旧版）、`EverySolid`（每个方块一个） | R6 道具坡道上的二次加成时刻 2.09–3.45 s，对 R5 2.10–3.49 s；旧版没有（横向滑铲结束速度 272 → 349，R5 351） | `slideRebeginOnGroundChange = SlideRebegin.Off`；游戏菜单 "Slide re-boost on a new ground" 也能切（PlayerPrefs `hsd.r6u.sliderebegin`） |
| U-4 坡面项坡度门槛 | n_z < 0.999（> 2.56°）才有滑铲坡面项 | 没有门槛 | 按 R5（移动本身的平地判断保留 0.999） | 只影响 < 2.56° 的缓坡（2° 时滑铲多 26 u/s² 加速）；实测坡度上不变 | `slideSlopeAnyGrade = false` |
| U-5 `slideSlopeNeedsDuck` | true（M8-B："松开下蹲 → 没有坡面项"） | 坡面项不看下蹲（`Gravity_HalfStep`） | false | 行为不变：松开下蹲后的变化本来就来自 `slideReleaseEnds` 的 400 减速 | `slideSlopeNeedsDuck = true` |

U-3 里没测到、按保守写的：落地不算换实体（落地的滑铲规则不变）；重新开始不算按下蹲（滑铲跳退还不重新计时）；超过 460 时不降速（R5 dn25 底部的逐命令残差说明不降）；没加速的那次不清掉"这次滑铲加速过"的标记。

### RPS 回放电机的滑铲规则（HSD-Unity `rps/replay-slide-native`，D-47）

"旧版"在这一节指 R6U 合并后的回放电机（HSD-Unity#43），也就是 M2 / M3 时定下、一直留作回放基线的滑铲规则，现在叫 **Legacy M2**。游戏身体（Reference / Fun）从 M10 / N7 起就是原生规则，这次没变；只是回放电机（用 R5 录像逐命令复现的那套）跟上。斜坡（R6U U-1…U-5）和非滑铲的 N7 项（地面摩擦、空中额外加速、冲刺加速边界、跳跃 skip reduce）回放电机里仍是旧规则，没动。

| 开关（`R5MotorV2Params`） | 旧版（Legacy M2） | R5（原生） | 现在 |
|---|---|---|---|
| `slideReleaseEnds` 松开下蹲 | 没有这条：松开下蹲照样滑，减速 100 | 速度 ≤ 350 时这条命令就结束滑铲；> 350 时减速 400（`slideWantToStopDecel`）代替 100（M10 r_slide 实测） | 按 R5 |
| `slideBoostRearm` + `slideBoostCooldownFromStart` 加速冷却 | 每次按下蹲都加速 | `player_slideBoostCooldown` 2 s，从上次滑铲**开始**算（落地续滑也算开始；N4-C：0 / 1.0 / 2.5 s 三次只有第一次加速） | 按 R5 |
| `slideRefundNeedsDuckTransition` 早跳退还（J-08） | 加速后 0.4 s 内跳就退还加速量 | 0.4 s 内**而且** 200 ms 下蹲过渡还没完成才退还 | 按 R5 |
| `slideDuckTransitionFromNextCommand`（F1-1） | 过渡从按下那条命令算 | 从下一条命令算（R5：按下后 0.201 s 退还，0.215 s 不退） | 按 R5 |
| `slideJumpFloorLowFrac` 350 下限（J-07） | 加速过的滑铲跳一律至少 350（规则 H1） | 只把 297.5–350 抬到 350，更慢的保持原速 | 按 R5 |
| `slideSteerAccel` 滑铲转向（G-12） | 0：不能转向 | `slideAccel` 50·msc（N4-C 横向 41.1 u/s²） | 按 R5 |

**差多少**（R5 录像回放，逐命令和 R5 比，全表 [research/phase2-local/rps/README.md](research/phase2-local/rps/README.md)）：M1/M2 37 个、M3 30 个、M4 38 个里，只有 M3 两个 `e8_slide_chain` 变了：速度误差 rms 7.48 → 0.23 / 0.26 u/s，位置误差 rms 2.2 → 0.8 / 0.9 u，最大速度误差 66.3 → 0.6 / 0.7 u/s（录像最后在滑铲中约 132 u/s 时松开下蹲：R5 当即结束滑铲，旧版继续滑，停下晚 6 条命令）。其余 103 个的逐命令轨迹逐字节相同，没有一个变差。

切回旧版：`R5MotorV2Params.LegacyM2()`（或对任意参数调 `WithLegacyM2Slide()`）；批量回放加 `-legacyM2`，输出和改前的回放基线逐字节相同（`m4/unity/regression_check.py`、`m5/unity/m4_replay_check.py` 仍按旧基线检查这一档）。

### RUD 回放电机的下蹲碰撞体和地面移动（HSD-Unity `rud/replay-unduck-native`，D-49）

"旧版"在这一节指 RPS 合并后的回放电机（HSD-Unity#44）。游戏身体（Reference / Fun）早就是右列的规则，这次没变，只是回放电机跟上。

| 开关（`R5MotorV2Params`） | 旧版（Legacy M2 / RPS） | R5 / Reference | 现在 |
|---|---|---|---|
| `airUnduckDrop` 下蹲碰撞体 | 0：没有。空中松开下蹲，高度不变 | 地上按住下蹲 0.2 s 碰撞体变矮；空中松开（起跳 0.08 s 后起）原点下降 16.5 u，头不动（M5 实测，M3 e8 / e3 slide350 共 8 次） | 按 R5 |
| `groundNativeFriction` 有输入时的地面移动 | M2 规则：速度方向立即转到输入方向（v = s·ŵ） | 原生 WalkMove：Friction + Accelerate，侧向输入着地后 0.1–0.3 s 慢慢转过去（N7 G-07/G-08/G-14） | 按 R5 |
| `groundVectorRedirect` | false | Reference 设着，但被上一行盖过 | 和 Reference 一样设为 true |

**差多少**（全表 [research/phase2-local/rud/README.md](research/phase2-local/rud/README.md)）：105 个录像里 70 个逐命令轨迹不变，35 个变了。
- M3 e3 侧向起跳整组：位置误差 rms 例如 24.2 → 2.4 u。
- e3 滑铲跳 r650 / r651：7.26 → 2.54 / 7.05 → 1.09 u。
- e8 连跳：8.0 → 0.6–1.4 u。
- M4 空中控制 / stim：10–20 → 1–2 u。

三个例外（用户同意）：
- M2 e1_turn ×2：只有"最高速度在第几条命令"变了（299 平台上的浮点噪声），轨迹误差不变。
- M3 r1237：沙盘比 R5 高约 0.5 u，离地面 2.075 u，刚超出原生 2.0 u 着地探测，晚一条命令着地，丢了一次连跳。

先做过只换 M5 `groundVectorRedirect` 的第一版：e1_turn 速度误差略升，后来按 Reference 实际走的原生 WalkMove 换成现在的版本。

原生着地探测（`CategorizePosition` 0x140a51bc0）：向下 2.0 u，向上速度 > 140 u/s 离地，和 Unity 的 `groundProbe` 2 相同，没改。

切回旧版：`R5MotorV2Params.LegacyM2()`（= `R5Reference()` 加 `WithLegacyM2Slide()` 和 `WithLegacyM2Rud()`），或者对任意参数调 `WithLegacyM2Rud()`。
批量回放加 `-legacyM2`，输出和最老的回放基线逐字节相同（111/111/90/114）。RPS 那一档（原生滑铲 + 旧地面 / 没有碰撞体）= `R5Reference().WithLegacyM2Rud()`。

### GN 钩爪脱钩规则（HSD-Unity `gn/grapple-native`，D-50）

"旧版"在这一节指 RPS 合并后的 Reference / Fun 钩爪（HSD-Unity#44），也就是 M10-A 定下、N7 改过一次的脱钩规则，现在叫 **pre-GN**。依据 N13（[research/rea-native/n13/N13-GRAPPLE-DETACH.md](research/rea-native/n13/N13-GRAPPLE-DETACH.md)）和 GN 的 Frida 实测（[research/rea-native/gn/GN-GRAPPLE-NATIVE.md](research/rea-native/gn/GN-GRAPPLE-NATIVE.md)）。Reference 和 Fun 都改（Fun 从 Reference 建，没有自己的钩爪值）；回放电机不用 S21 钩爪，不变。开关都在 `GrappleS21Params`。

| # | 旧版（pre-GN） | R5（原生） | 现在 | 差多少（旧版 → 现在，R5） | 切回旧版 |
|---|---|---|---|---|---|
| G-1 接近距离 | 钩点到身体竖线段 [原点, 原点 + 72] 的距离；wind-up 里 ≤ 45 就脱 | min(\|P − 原点\|, \|P − 眼睛\|)，挂上后每条命令都查（`0x14066fb60`） | 按 R5，眼睛 = 当前眼高 | 往墙上拉晚 1 条命令脱钩（hold 241 → 242，同一场景） | `nativeProxDistance = false` |
| G-2 接近斜坡 | 接近速度除以 800 | 除以 `grapple_speedRampMax_human` 400 | 按 R5 | 接近速度 267–533 u/s 时阈值大最多 17 u，慢慢贴近会早脱；测过的片段都不在这个区间，没变化 | `detachRampMax = 800` |
| G-3 方向 | 视线规则从原点 + 70 量钩点；速度朝原点 + 36 量 | 都按绳子方向 d = P + (0, 0, `grapple_lift` 25) − (原点 + (0, 0, h + 1))，h = 22（Frida），也就是从原点上方 23 指向钩点上方 25；往下看时 d 和"眼睛 → 钩点"的水平部分都要在水平前方后面 | 按 R5 | 视线离开 ×4、rodeo ×8：脱钩时刻不变（1.058 / 0.450–0.465 s）。钩点很高（仰角约 50°）时一直仰着头转身不再脱钩，要把视角放平（演示 `m10a_look_away` 因此改成边转边放平） | `nativeRopeDir = false` |
| G-4 低速 | \|v\| < 250 开始计时 | 朝绳子的径向速度 v·d̂ ≤ 250 开始计时（拉动开始前算"好"） | 按 R5 | 绕着钩点横飞、贴着挡板横移（\|v\| 大、径向小）现在会超时；直线被挡住时不变 | `nativeLowSpeed = false` |
| #7 低速时限 | 碰到墙 / 天花板 1.2 s，在地面高度 0.7 s，其余 1.5 s | 有地面实体时 0.7（沿墙跑时 1.2），否则 1.5；R5 拉动时一直 ground = 0，所以实际一律 1.5 | 拉动中一律 1.5 | N6 天花板 ×8：拉动 → 脱钩 1.200–1.208 → 1.500–1.508 s（R5 1.508–1.517） | `nativeLowSpeedTimer = false` |
| G-5 远离 > 500 | 一直生效 | 只在钩子没有父实体时生效：钩在世界几何上生效，钩在道具 / 绳子上不生效（Frida：钩岩石时 +0x148 = 那块 prop，钩地面时为空） | 按 R5（`ConvexSolid.prop`、绳子算道具） | 测过的片段都没触发 | `awayOnlyWorldHooks = false` |
| G-6 撞上上抬 | 没有 | 客户端代码：钩在世界上、接近脱钩时 vz = min(vz + 300, 300)；Frida 在地面钩看到 vz 299，但录下来的轨迹没有跳（混合版本） | **没加**（`impactBoost` 开关做了，都关） | — | 待定 |

**A-1 和对照场景**（同时改了对照场景 S-1 / S-2：岩石挡身体的面 x −13704.6、后倾 1.86°，钩点在过记录钩点 x −13697.9 的平行面上，岩石是道具）：

| 片段 | R5 脱钩 / 最高点 | 旧版（旧场景） | 现在（新场景） |
|---|---|---|---|
| hold 1701 | 244 / 155.3 | 241 / 145.0 | 245 / 155.7 |
| hold 1702 | 243 / 154.9 | 241 / 145.0 | 245 / 155.7 |
| near 2101 | 201 / 117.3 | 199 / 111.3 | 202 / 116.3 |
| near 2102 | 201 / 116.8 | 199 / 111.8 | 202 / 116.6 |

切回旧版：`GrappleS21Params.SetGnDetach(false)`（6 个开关一起回去；单个开关也能分别改）；游戏 Esc 菜单 "Grapple detach rules (GN)"（PlayerPrefs `hsd.gn.grapple`）；`FeelBatch` / `CameraFeelBatch` 加 `-preGn`。旧版的输出和改前逐字节相同（M4 钩爪 4 个片段的 reference / fun / replay，镜头片段 19 个）。


### CAM2 镜头：起跳 punch、翻越镜头、滑索眼睛偏移、横滚合成（HSD-Unity `cam2/camera-combo`，D-53 / D-54）

"旧版"在这一节指 GN 合并后 main 上的原生镜头（`NativeCameraFeedback`），现在叫 **pre-CAM2**。依据 [research/rea-native/cam2/CAM2-CAMERA.md](research/rea-native/cam2/CAM2-CAMERA.md)。只改镜头（视觉层），模拟、瞄准、两套电机的输出都不变；M5.5 镜头不动。开关都在 `NativeCameraParams`。

| # | 旧版（pre-CAM2） | R5（原生） | 现在 | 差多少（旧版 → 现在，R5） | 切回旧版 |
|---|---|---|---|---|---|
| K-5 起跳 | 起跳时镜头不动 | 每次地面跳 / 滑铲跳往两组 punch 弹簧加冲量（`0x140a349c0`）：俯仰 (2 + r₁)·20、偏航 r₂·20、横滚 (0.9 + 0.5·r₃)·20，第二组 × 0.2，随机数按跳跃命令号 | 按 R5（多了 punch 的偏航轴） | 起跳俯仰峰值 0 → 2.5–3.7°（R5 2.4–3.9°，CAM2_C 15 个片段逐个差 ≤ 0.15°） | `jumpPunch = false` |
| K-6 翻越 | 只有 S27 翻越加速模式下才有翻越镜头 | 每次翻越都跟着第一人称翻越动画镜头（`GetTraversalViewPosition`） | 每次翻越都按 B1 的翻越镜头曲线 | 120 u 冲刺翻越峰值 0 → 4.6°（R5 4.5–5.3°）；K-6 指标 5 / 88 → 53 / 88 | `traversalCamera = false` |
| K-7 滑索眼高 | 眼高 70（站立） | 眼睛加一个滑索视角偏移（Perlin 噪声目标，ω 4 弹簧）：一次 1–2 s 滑行降 5–9 u，左右偏 0–1.5 u | 按 R5 | N10 5 个片段眼高 70 → 65.5–65.9（R5 65.5–65.9） | `zipViewOffset = false` |
| K-7 滑索横滚 | 绳上点 = 三维最近点；眼睛在绳子正下方，横滚 0 | 绳上点 = 水平投影（头顶正上方）；横滚来自上面那点左右偏移 | 按 R5 | N10 5 个片段横滚峰值 0 → −1.41 … +0.34°（R5 −1.44 … +0.28°）；滑索指标 2 / 10 → 10 / 10 | `zipRopeHorizontal = false`（和上面一起） |
| 横滚合成 | 各项相加后夹在 ±40° | 相加后折回 ±180°，不封顶（`View_CalcRoll`） | 按 R5 | 正常玩法里总和到不了 40°，对照里没有变化 | `rollWrap = false` |

切回旧版：`NativeCameraParams.SetCam2(false)`（5 个开关一起回去）；`CameraFeelBatch -preCam2`。旧版的输出和 main 在 166 个旧镜头片段上逐字节相同。

---

## 二、还和 R5 不一样、没有改的

| 编号 | 内容 | 旧版 = 现在 | R5 | 状态 |
|---|---|---|---|---|
| ~~A-1 剩余~~ | 钩爪拉到墙边 | GN 起：脱钩规则按原生、对照场景按 R5 的岩石；现在晚 1–2 条命令（245 / 245 / 202 / 202 对 244 / 243 / 201 / 201），最高点差 0.4–1.0 u | — | 见第一部分 GN（D-50）。剩下 1 条命令出在场景 / 拉力的近似，同一场景旧规则也是 244 / 244 / 202 / 202 |
| G-6 | 世界钩点接近脱钩时的撞上上抬 | 没有 | S21 客户端代码有（Frida 实测 vz → 299），本地录到的轨迹没有（混合版本）；世界上的墙没测过 | 待定（`impactBoost`） |
| ~~K-5~~ | 起跳时的镜头动作 | — | — | 10-29 按原生做了，见第一部分 CAM2（D-53）。F6 写的"0.57 s 向上 1.7°"是指标基准的问题，原生就是一个 punch |
| ~~K-6~~ | 翻越时的镜头动作 | — | — | 10-29 按原生做了，见第一部分 CAM2（D-53） |
| K-6 蹲姿 | 蹲着翻越的翻越镜头时刻 | h120 蹲 0.29 s 到峰；h160 蹲没有驼峰 | h120 蹲 0.52–0.60 s；h160 蹲 0.99 s | B1 已知的蹲姿翻越时间问题，CAM2 没动 |
| ~~K-7~~ | 滑索横滚、滑索上的眼高 | — | — | 10-29 复测并按原生做了，见第一部分 CAM2（D-54）。N6 的那几个片段 R5 根本没上绳 |
| K-8 | 下滑索时的镜头 punch | 没有 | `0x140a35ac0`：俯仰 (10 + 3·r₁)·20、偏航 / 横滚 10·r·20；实测第一组峰值 12–14° 向下、横滚 ±1–5° | 新发现（CAM2），没改，等你决定 |
| 二段跳 punch | 跳板二段跳的镜头 | F7 设计：向下 1.2° 的小凸起（不回弹） | `0x140a34c00`：俯仰 (4.5 + r₁)·20（约 3.9–6.2°）、横滚 2·r₃·20，弹簧形状 | 新发现（CAM2），没改，等你决定 |
| 滑铲跳落地 kick | 滑铲跳落地时的 kick | 1.5–2.1°（改前），1.7–2.3°（CAM2 起跳 punch 的尾巴让基准低 0.2°） | 1.1–1.7° | 改前就大约 1.5 倍，原因没查（CAM2） |
| 滑铲下沉 | 眼高降到最低的时间 | 约 0.19 s | 约 0.167 s | 小差别，记下 |
| F-2 | 原地跳高度 | 比 R5 高 1.8 u（两套电机） | — | 早先记下，没查（F1） |
| 回放电机 | M2 / M3 回放用的电机 | 滑铲规则（RPS）、下蹲碰撞体和有输入的地面移动（RUD）已按原生 / Reference（见第一部分）；斜坡（R6U）和其余 N7 项（空中额外加速、冲刺加速边界、跳跃 skip reduce、+30 推墙）仍是 M2 / M3 规则 | — | 已换滑铲（D-47）、碰撞体和地面移动（D-49）；其余要不要换没定 |

---

## 三、有意和 R5 不一样（设计，不算差别）

- **Fun 配置**：跑墙、抓边悬挂、二段跳、飞行、重力切换（D-08），都是 HSD 设计。
- **S27 翻越加速**（D-20、D-32）：游戏里默认开，是从 S27 移植的，不是 S21。关掉它就是原生 superglide。
- **M5.5 镜头**（D-18）：原样保留，可以在菜单里切回去。
