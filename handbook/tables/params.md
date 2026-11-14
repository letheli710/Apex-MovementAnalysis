# 参数对照表

由 hb-tables 写（2026-11-14）。**原件是同目录的 [`params.tsv`](params.tsv)**（150 行，16 列，UTF-8，制表符分隔）；这一页由 TSV 生成表格部分，再手写说明。两边对不上时以 TSV 为准。

## 白话说明

这张表把手册里用到的**设计参数**放在一起：每个参数 R5 原来是多少、换成米是多少、相当于几个身高、TF2 是多少、Unity 现在用多少，以及两边一不一样、为什么不一样。只挑了做设计用得到的（移动、跳、滑铲、翻越、跑墙、滑索 / 钩爪 / 跳板、镜头、开镜和后坐的主要参数），Unity 的全部 13155 个参数值放在 [`unity-export/`](unity-export/) 作附件。

**为什么要这张表**：研究用 u，以后切到米。同一个数在两套单位下长得不一样（56 u = 1.4224 m），一旦有人在表里或代码里写错单位，数据就"串了"。所以：

1. 每一列都标了单位体系：`R5 原值 [u]`、`[m]`、`Unity 现在的值 [u]`……没有不带标记的长度、速度列。
2. `[m]` 列是算出来的（R5 原值 × 0.0254 的量纲次方），不是独立来源。
3. **校验脚本** [`check_params.py`](check_params.py) 把表和 Unity 的单位导出逐行对：参数还在不在、量纲变没变、Unity 的值变没变、`[m]` 和身高比例对不对、"和 R5 一致吗"有没有写错。对不上就报错。Unity 改了参数、重新导出以后先跑它（怎么跑见 [README](README.md)）。

**结论先说**：
- 150 个参数里，126 个和 R5 一致，**2 个不一致**，1 个近似，**2 个 R5 有、Unity 没实现**，4 个 R5 没测过，5 个只有 HSD（R5 没有这个功能），10 个开镜 / 后坐参数的 Unity 实现还在没合并的 PR 上。
- 回放电机（`preset.R5Reference`，用 R5 录像逐命令复现的那套）有 6 个参数故意停在旧规则上（D-66：回放电机只当尺子），见下面"回放电机"一节。游戏身体（Reference / Fun）用的是表里"Unity 现在的值"。

## 怎么读

| 列 | 意思 |
|---|---|
| 参数名(Unity 导出) | Unity 单位导出里的名字。`preset.Reference.*` 是游戏身体 Reference 配置；`preset.R5Reference.*` 是回放电机；`camera.native.*` 是原生镜头（默认）；`world.default.*` 是世界和碰撞体；`defaults.<类>.*` 是这个类的默认值。名字是"（没有：…）"的行不在导出里，校验脚本跳过 |
| 量纲 | 导出里的量纲（Length、Velocity、Acceleration、Time、Angle、Ratio……），决定 `[m]` 怎么换（[01 §2](../01-units-body.md)） |
| R5 原值 [u] | R5 的数，原样照抄。"没测过"= R5 里没量到；"—（R5 没有）"= HSD 自己的设计 |
| [m] | R5 原值 × 0.0254^k；角度、时间、比例写"—" |
| 身高比例 | R5 原值 ÷ 72^k，单位 H、H/s、H/s² |
| TF2 值 [u] | 有 TF2 对照的才写 |
| Unity 现在的值 [u] | 导出快照的值（HSD-Unity `units/switch` 84e7a4a（11-14 由 5c79a50 换新，表里的值没变），PR #88，还没合并；数值和 main 一样） |
| 回放电机 [u] | 同名参数在回放电机里的值（只对 `motor.*`） |
| 和 R5 一致吗 | 一致 / 不一致 / 近似 / Unity 没有 / 没测过 / 只有 HSD / 不在 main |
| 差别 | 不一致或有过改动的写 D-xx、R5-DIFF 条目 |
| R5 依据 | 依据标签（[数据] [实测] [反编译] [算] [推断] [设计]）和来源说明 |
| 出处 | 研究仓库里的文件和节 |


## 和 R5 不一致的

| id | 参数 | R5 [u] | Unity [u] | 说明 |
|---|---|---|---|---|
| B-04 | `world.default.stepUp` 能直接走上去的台阶高度 | 22 | 18 | 不一致。R5-DIFF 没有这一条：Unity 18 = TF2 的值（01 §4.2 已提，交 hb-ch02 核对） |
| G-07 | `preset.Reference.motor.sprintAcceleration` 冲刺段加速度（× msc） | 100 | 102 | 不一致。R5-DIFF 没有这一条：Unity 所有装备都用 102（M2 那次会话的传奇的值），其余传奇 R5 是 100 |
| S-17 | `（没有：slide_step_velocity_reduction）` 上台阶的滑铲减速 slide_step_velocity_reduction（× 台阶高度） | 10 | 没实现 | Unity 没有。Unity 没有这条规则（滑铲上台阶不减速）；R5-DIFF 没记 |
| S-18 | `（没有：slide_max_angle_dot）` 冲刺时能起滑的最大偏角（余弦）slide_max_angle_dot | 0.6 | 没实现 | Unity 没有。Unity 没有这条限制；R5-DIFF 没记 |
| F-09 | `defaults.StimParams.severity` 兴奋剂速度强度（0.15 量化成 38/255） | 0.15 | 0.14901960784313725 | 近似（差 0.65 %）。Unity 0.14902 = 38/255：按网络字节量化（近似，差 0.65 %） |

最重要的两个：

1. **台阶高度 B-04**：R5 setfile `stepHeight` 是 22 u（0.559 m），Unity 18 u（= TF2）。关卡里 18–22 u 之间的台阶在 R5 能走上去，在 HSD 要跳。R5-DIFF 里没有这一条，01 §4.2 已经交给 hb-ch02 核对；建议的 D 行见 `_notes/hb-tables.md`。
2. **冲刺加速度 G-07**：R5 只有 Wraith 是 102，其余传奇 100；Unity 所有装备都用 102（M2 那次会话的传奇）。差 2 %，从走路速度到冲刺上限多花约 0.02 s。

另外两条"Unity 没有"（S-17 上台阶的滑铲减速、S-18 冲刺起滑的角度限制）是 R5 的 ConVar 规则 Unity 里根本没写，也不在 R5-DIFF 里。

## 回放电机（故意停在旧规则，D-66）

| id | 参数 | 游戏身体 [u] | 回放电机 [u] |
|---|---|---|---|
| B-06 | `preset.Reference.motor.hullBottomRadius` | 16 | 0 |
| J-08 | `preset.Reference.motor.groundJumpSkipReduce` | 100 | 0 |
| J-11 | `preset.Reference.motor.extraAirAccel` | 2 | 0 |
| J-12 | `preset.Reference.motor.jumpSurfacePush` | 30 | 0 |
| L-04 | `preset.Reference.motor.lurchClampSprintFraction` | 0.7 | 0 |
| L-06 | `preset.Reference.motor.lurchCutoffSpeed` | 1100 | 0 |

这些不是错：回放电机只用来量 R5 录像（"尺子"），D-66 决定剩下的斜坡和 N7 项不换。手册的规则以游戏身体为准。

## 没测过的

- B-01 `world.default.hullRadius` 站立碰撞体半宽：[设计] Source 默认；R5 setfile poseSettings 没读出来
- B-02 `world.default.hullHeight` 站立碰撞体高度（参考身高 H）：[设计] 同上，H = 72 u 是 HSD 用的值
- B-03 `world.default.crouchHullHeight` 蹲姿碰撞体高度：[推断] 由 airUnduckDrop 16.5 推出 55.5 或 39，都不是 48
- M-15 `preset.Reference.superglideReducedBand` superglide 降速带（自然结束前 117.5 → 102.5 ms 出 425）：[实测] M8（F2 C-2）；原生规则没读通（M-04）

## 全表

### 身体

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| B-01 | `world.default.hullRadius` | 站立碰撞体半宽 | 没测过 | — | — | — | 16 | 没测过 |
| B-02 | `world.default.hullHeight` | 站立碰撞体高度（参考身高 H） | 没测过 | — | — | — | 72 | 没测过 |
| B-03 | `world.default.crouchHullHeight` | 蹲姿碰撞体高度 | 没测过 | — | — | — | 48 | 没测过 |
| B-04 | `world.default.stepUp` | 能直接走上去的台阶高度 | 22 u | 0.5588 m | 0.3056 H | 18 | 18 | 不一致 |
| B-05 | `world.default.standableNormalZ` | 能站住的最陡地面：法线 z 下限（0.7 ≈ 45.57°） | 0.7 | — | — | — | 0.7 | 一致 |
| B-06 | `motor.hullBottomRadius` | 坡上碰撞体底部按圆底算的半径 | 16 u | 0.4064 m | 0.2222 H | — | 16 | 一致 |
| B-07 | `motor.groundProbe` | 着地探测向下距离 | 2 u | 0.0508 m | 0.02778 H | — | 2 | 一致 |
| B-08 | `camera.native.eye.standEye` | 站立眼高 | 70 u | 1.778 m | 0.9722 H | 60 | 70 | 一致 |
| B-09 | `camera.native.eye.crouchEye` | 蹲 / 滑铲眼高 | 32 u | 0.8128 m | 0.4444 H | — | 32 | 一致 |
| B-10 | `camera.native.eye.sprintOffset` | 冲刺时眼高偏移 | -6 u | -0.1524 m | -0.08333 H | -6 | -6 | 一致 |
| B-11 | `camera.native.eye.duckTime` | 站 ↔ 蹲眼高过渡时间 | 0.4 s | — | — | — | 0.4 | 一致 |
| B-12 | `camera.native.eye.slideDuckTime` | 滑铲时眼高下沉时间 | 0.2 s | — | — | — | 0.2 | 一致 |
| B-13 | `motor.hullCrouchTime` | 按住下蹲多久碰撞体变矮 | 0.2 s | — | — | — | 0.2 | 一致 |
| B-14 | `motor.airUnduckDrop` | 空中松开下蹲时原点下降（头不动） | 16.5 u | 0.4191 m | 0.2292 H | — | 16.5 | 一致 |
| B-15 | `motor.airUnduckMinAfterTakeoff` | 起跳后多久才允许空中松蹲下降 | 0.08 s | — | — | — | 0.08 | 一致 |

### 地面移动

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| G-01 | `motor.speed` | 走路上限（× moveScale = 199.525） | 173.5 u/s | 4.4069 m/s | 2.41 H/s | 173.5 | 173.5 | 一致 |
| G-02 | `motor.sprintspeed` | 冲刺上限（× moveScale = 299） | 260 u/s | 6.604 m/s | 3.611 H/s | 260 | 260 | 一致 |
| G-03 | `motor.moveScale` | 空手移动倍率 msc（拿枪 1.0） | 1.15 | — | — | — | 1.15 | 一致 |
| G-04 | `motor.acceleration` | 中速段加速度（× msc） | 450 u/s² | 11.43 m/s² | 6.25 H/s² | 2500 | 450 | 一致 |
| G-05 | `motor.lowSpeed` | 低速段分界（× msc = 138） | 120 u/s | 3.048 m/s | 1.667 H/s | -1（关） | 120 | 一致 |
| G-06 | `motor.lowAcceleration` | 低速段加速度（× msc） | 2500 u/s² | 63.5 m/s² | 34.72 H/s² | -1（关） | 2500 | 一致 |
| G-07 | `motor.sprintAcceleration` | 冲刺段加速度（× msc） | 100 u/s² | 2.54 m/s² | 1.389 H/s² | -1（关） | 102 | 不一致 |
| G-08 | `motor.deceleration` | 无输入减速（不乘 msc） | 1250 u/s² | 31.75 m/s² | 17.36 H/s² | -1（关） | 1250 | 一致 |
| G-09 | `motor.sprintDeceleration` | 冲刺时无输入减速 | 1250 u/s² | 31.75 m/s² | 17.36 H/s² | — | 1250 | 一致 |
| G-10 | `motor.speedScaleSide` | 侧移速度系数 | 1 | — | — | 1 | 1 | 一致 |
| G-11 | `motor.speedScaleBack` | 后退速度系数（sv_backspeed 0.6 不起作用） | 1 | — | — | 1 | 1 | 一致 |
| G-12 | `motor.crouchSpeed` | 蹲走上限（× msc = 92） | 80 u/s | 2.032 m/s | 1.111 H/s | — | 80 | 一致 |
| G-13 | `motor.crouchDeceleration` | 蹲姿减速 | 1500 u/s² | 38.1 m/s² | 20.83 H/s² | — | 1500 | 一致 |
| G-14 | `motor.stopSnapSpeed` | 低于这个速度直接归零 | 1 u/s | 0.0254 m/s | 0.01389 H/s | — | 1 | 一致 |

### 跳跃 · 空中

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| J-01 | `motor.svGravity` | 重力 sv_gravity | 750 u/s² | 19.05 m/s² | 10.42 H/s² | 750 | 750 | 一致 |
| J-02 | `motor.gravityScale` | 重力倍率 | 1 | — | — | 0.8（下落 600） | 1 | 一致 |
| J-03 | `motor.jumpHeight` | 起跳高度（起跳速度 √(2gH) = 289.83） | 56 u | 1.4224 m | 0.7778 H | 60 | 56 | 一致 |
| J-04 | `motor.antiMultiJumpHeightFrac` | 落地后马上再跳的高度系数下限 | 0.3 | — | — | — | 0.3 | 一致 |
| J-05 | `motor.multiJumpHoldT0` | 连跳系数开始恢复（antiMultiJumpTimeMin） | 0.15 s | — | — | — | 0.15 | 一致 |
| J-06 | `motor.multiJumpRampT` | 连跳系数恢复用时（TimeMax 0.75 − TimeMin 0.15） | 0.6 s | — | — | — | 0.6 | 一致 |
| J-07 | `motor.groundJumpSkipTime` | 超速削减窗口 skip_time | 1 s | — | — | 0.1 | 1 | 一致 |
| J-08 | `motor.groundJumpSkipReduce` | 超速削减量 skip_speed_reduce | 100 u/s | 2.54 m/s | 1.389 H/s | 12（扣到 450 为止） | 100 | 一致 |
| J-09 | `motor.airSpeed` | 空中期望速度上限（× msc） | 60 u/s | 1.524 m/s | 0.8333 H/s | 60 | 60 | 一致 |
| J-10 | `motor.airAcceleration` | 空中加速度（不乘 wishspeed） | 500 u/s² | 12.7 m/s² | 6.944 H/s² | 500 | 500 | 一致 |
| J-11 | `motor.extraAirAccel` | 空中额外加速 player_extraairaccelleration | 2 u/s² | 0.0508 m/s² | 0.02778 H/s² | 2.0 | 2 | 一致 |
| J-12 | `motor.jumpSurfacePush` | 起跳时朝上一帧撞到的墙加速 | 30 u/s | 0.762 m/s | 0.4167 H/s | — | 30 | 一致 |

### Lurch / tap strafe

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| L-01 | `motor.lurchLamMax` | lurch 强度 jump_grace_strength | 0.7 | — | — | 0.7 | 0.7 | 一致 |
| L-02 | `motor.lurchFullEnd` | 起跳后满强度窗口 jump_graceperiodmin | 0.2 s | — | — | 0.2 | 0.2 | 一致 |
| L-03 | `motor.lurchZero` | 强度降到 0 的时刻 jump_graceperiodmax | 0.5 s | — | — | 0.5 | 0.5 | 一致 |
| L-04 | `motor.lurchClampSprintFraction` | lurch 上限 = 这个 × msc × sprintspeed（jump_grace_max） | 0.7 | — | — | 0.7 | 0.7 | 一致 |
| L-05 | `motor.lurchClamp` | lurch 固定上限（L-04 = 0 时用） | 209.3 u/s | 5.3162 m/s | 2.907 H/s | — | 209.3 | 一致 |
| L-06 | `motor.lurchCutoffSpeed` | 水平速度超过这个不触发 lurch | 1100 u/s | 27.94 m/s | 15.28 H/s | — | 1100 | 一致 |

### 滑铲

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| S-01 | `motor.slideRequiredStartSpeed` | 能开始滑铲的最低速度 | 200 u/s | 5.08 m/s | 2.778 H/s | 200 | 200 | 一致 |
| S-02 | `motor.slideSpeedBoost` | 滑铲加速（× msc = 172.5） | 150 u/s | 3.81 m/s | 2.083 H/s | 150 | 150 | 一致 |
| S-03 | `motor.slideSpeedBoostCap` | 加速后的上限（× msc = 460） | 400 u/s | 10.16 m/s | 5.556 H/s | 400 | 400 | 一致 |
| S-04 | `motor.slideSteerAccel` | 滑铲中转向加速 slideAccel（× msc） | 50 u/s² | 1.27 m/s² | 0.6944 H/s² | 50 | 50 | 一致 |
| S-05 | `motor.slideDecel` | 滑铲线性减速 | 100 u/s² | 2.54 m/s² | 1.389 H/s² | 50 | 100 | 一致 |
| S-06 | `motor.slideVelocityDecay` | 滑铲每秒比例衰减（v × 0.7^dt） | 0.7 | — | — | 0.7 | 0.7 | 一致 |
| S-07 | `motor.slideStopSpeed` | 按住下蹲时滑铲结束速度 | 125 u/s | 3.175 m/s | 1.736 H/s | 125 | 125 | 一致 |
| S-08 | `motor.slideMaxStopSpeed` | 松开下蹲时 ≤ 这个速度就结束 | 350 u/s | 8.89 m/s | 4.861 H/s | 350 | 350 | 一致 |
| S-09 | `motor.slideWantToStopDecel` | 松开下蹲后的减速 | 400 u/s² | 10.16 m/s² | 5.556 H/s² | 400 | 400 | 一致 |
| S-10 | `motor.slideJumpHeight` | 滑铲跳高度 | 50 u | 1.27 m | 0.6944 H | 50 | 50 | 一致 |
| S-11 | `motor.slideMaxJumpSpeed` | 滑铲跳水平速度的抬升线（297.5–350 抬到 350） | 350 u/s | 8.89 m/s | 4.861 H/s | 350 | 350 | 一致 |
| S-12 | `motor.slideJumpFloorLowFrac` | 抬到 350 的下限比例（0.85 × 350 = 297.5） | 0.85 | — | — | — | 0.85 | 一致 |
| S-13 | `motor.slideBoostRearm` | 滑铲加速冷却 player_slideBoostCooldown（从上次滑铲开始算） | 2 s | — | — | — | 2 | 一致 |
| S-14 | `motor.slideBoostRefundWindow` | 加速后多久内起跳退还加速 | 0.4 s | — | — | — | 0.4 | 一致 |
| S-15 | `motor.slideDuckTransitionTime` | 滑铲下蹲过渡（退还还要求它没完成） | 0.2 s | — | — | — | 0.2 | 一致 |
| S-16 | `motor.slideSlopeGravityScale` | 坡上滑铲的沿坡重力倍率 | 1 | — | — | — | 1 | 一致 |
| S-17 | `（没有：slide_step_velocity_reduction）` | 上台阶的滑铲减速 slide_step_velocity_reduction（× 台阶高度） | 10 1/s | — | — | 10 | 没实现 | Unity 没有 |
| S-18 | `（没有：slide_max_angle_dot）` | 冲刺时能起滑的最大偏角（余弦）slide_max_angle_dot | 0.6 | — | — | 0.6 | 没实现 | Unity 没有 |

### 翻越和 superglide

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| M-01 | `advanced.climb.nativeTraversal.height` | 翻越最大高度 mantleHeight | 80 u | 2.032 m | 1.111 H | — | 80 | 一致 |
| M-02 | `advanced.climb.ledge.maxHeight` | 台面探测的最高点（离脚） | 80 u | 2.032 m | 1.111 H | — | 80 | 一致 |
| M-03 | `advanced.climb.nativeTraversal.edge4` | 翻越分档：低于这个用 Below 动画 automantle_height_below | -10 u | -0.254 m | -0.1389 H | — | -10 | 一致 |
| M-04 | `advanced.climb.nativeTraversal.edge5` | 翻越分档 automantle_height_level | 10 u | 0.254 m | 0.1389 H | — | 10 | 一致 |
| M-05 | `advanced.climb.nativeTraversal.edge6` | 翻越分档 automantle_height_above | 30 u | 0.762 m | 0.4167 H | — | 30 | 一致 |
| M-06 | `advanced.climb.nativeTraversal.len4` | 翻越时长 状态 4（站姿 Level） | 0.6 s | — | — | — | 0.6 | 一致 |
| M-07 | `advanced.climb.nativeTraversal.len5` | 翻越时长 状态 5（Above） | 0.5 s | — | — | — | 0.5 | 一致 |
| M-08 | `advanced.climb.nativeTraversal.len6` | 翻越时长 状态 6（High） | 0.35 s | — | — | — | 0.35 | 一致 |
| M-09 | `advanced.climb.nativeTraversal.airDuckLift` | 空中蹲到底时探台面的起点抬高 | 16.5 u | 0.4191 m | 0.2292 H | — | 16.5 | 一致 |
| M-10 | `advanced.climb.fsm.poseSpeed` | 翻越自然结束的出口速度（冲刺上限） | 299 u/s | 7.5946 m/s | 4.153 H/s | — | 299 | 一致 |
| M-11 | `advanced.climb.fsm.boostSpeedScale` | S27 mantle boost 速度倍率（SDK bridge_mantle_boost_sprint_mult） | 1.3 | — | — | — | 1.3 | 一致 |
| M-12 | `advanced.climb.fsm.boostHeight` | S27 mantle boost 跳高（SDK） | 90 u | 2.286 m | 1.25 H | — | 90 | 一致 |
| M-13 | `advanced.climb.s27.sweetSpotAngle` | S27 boost 最佳俯仰角（SDK） | 1.5 deg | — | — | — | 1.5 | 一致 |
| M-14 | `advanced.climb.s27.minValidFrac` | S27 boost 最小有效翻越进度（SDK） | 0.5 | — | — | — | 0.5 | 一致 |
| M-15 | `superglideReducedBand` | superglide 降速带（自然结束前 117.5 → 102.5 ms 出 425） | 没测过 | — | — | — | 0.015 | 没测过 |

### 跑墙 · 二段跳

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| W-01 | `hsd.wallRun.maxDuration` | M7 跑墙最长时间（HSD 设计，游戏默认规则） | —（R5 没有） | — | — | 1.75（wallrun_timeLimit） | 1.6 | 只有 HSD |
| W-02 | `hsd.wallRun.runSpeed` | M7 跑墙速度（HSD 设计） | —（R5 没有） | — | — | 420（MaxSpeedHorizontal） | 300 | 只有 HSD |
| W-03 | `hsd.wallRun.gravityScale` | M7 跑墙重力倍率（HSD 设计） | —（R5 没有） | — | — | — | 0.15 | 只有 HSD |
| W-04 | `hsd.wallRun.tf2.timeLimit` | TF2 规则跑墙最长时间（预设 B：R5 残留值） | 2 s | — | — | 1.75 | 2 | 一致 |
| W-05 | `hsd.wallRun.tf2.maxSpeedHorizontal` | TF2 规则跑墙水平上限（预设 B） | 225 u/s | 5.715 m/s | 3.125 H/s | 420 | 225 | 一致 |
| W-06 | `hsd.wallRun.tf2.accelerateHorizontal` | TF2 规则跑墙水平加速（预设 B） | 200 u/s² | 5.08 m/s² | 2.778 H/s² | 1500 | 200 | 一致 |
| W-07 | `hsd.wallRun.tf2.maxSpeedVertical` | TF2 规则跑墙竖直上限（预设 B） | 112 u/s | 2.8448 m/s | 1.556 H/s | 225 | 112 | 一致 |
| W-08 | `hsd.wallRun.tf2.accelerateVertical` | TF2 规则跑墙竖直加速（预设 B） | 450 u/s² | 11.43 m/s² | 6.25 H/s² | 360 | 450 | 一致 |
| W-09 | `hsd.wallRun.tf2.jumpOutwardSpeed` | TF2 规则蹬墙跳向外速度（预设 B） | 188 u/s | 4.7752 m/s | 2.611 H/s | 205 | 188 | 一致 |
| W-10 | `hsd.wallRun.tf2.jumpUpSpeed` | TF2 规则蹬墙跳向上速度（预设 B） | 240 u/s | 6.096 m/s | 3.333 H/s | 230 | 240 | 一致 |
| W-11 | `hsd.wallRun.tf2.jumpInputDirSpeed` | TF2 规则蹬墙跳按键方向速度（预设 B） | 75 u/s | 1.905 m/s | 1.042 H/s | 80 | 75 | 一致 |
| W-12 | `hsd.wallRun.tf2.upWallBoost` | TF2 规则贴墙上冲（预设 B） | 250 u/s | 6.35 m/s | 3.472 H/s | 250 | 250 | 一致 |
| W-13 | `hsd.wallRun.tf2.heightCutoff` | TF2 规则竖直增益截止 verticalGainCutoff_wallrun（预设 B） | 175 u | 4.445 m | 2.431 H | — | 175 | 一致 |
| W-14 | `hsd.doubleJump.height` | HSD 二段跳高度（设计） | —（R5 没有） | — | — | 60（superjumpMin/MaxHeight 60 / 60） | 45 | 只有 HSD |
| W-15 | `hsd.doubleJump.horizontalSpeed` | HSD 二段跳水平速度（设计） | —（R5 没有） | — | — | 180 | 180 | 只有 HSD |

### 滑索

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| Z-01 | `advanced.zipline.speed` | 滑索速度 ziplineSpeed | 600 u/s | 15.24 m/s | 8.333 H/s | — | 600 | 一致 |
| Z-02 | `advanced.zipline.detachSpeed` | 端点脱离速度 ziplineDetachSpeed | 600 u/s | 15.24 m/s | 8.333 H/s | — | 600 | 一致 |
| Z-03 | `advanced.zipline.maxVerticalDetachSpeed` | 竖直脱离速度上限 | 1500 u/s | 38.1 m/s | 20.83 H/s | — | 1500 | 一致 |
| Z-04 | `advanced.zipline.jumpOffCap` | 跳离滑索沿绳速度上限 ziplineJumpOffSpeed | 400 u/s | 10.16 m/s | 5.556 H/s | — | 400 | 一致 |
| Z-05 | `advanced.zipline.jumpOffVz` | 跳离滑索竖直速度（= 起跳速度） | 289.828 u/s | 7.3616 m/s | 4.025 H/s | — | 289.828 | 一致 |
| Z-06 | `advanced.zipline.rideAccel` | 滑索上加速 pathGravityAcceleration | 400 u/s² | 10.16 m/s² | 5.556 H/s² | — | 400 | 一致 |

### 钩爪

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| P-01 | `grapple.range` | 钩爪最远距离 grapple_maxLength | 850 u | 21.59 m | 11.81 H | — | 850 | 一致 |
| P-02 | `grapple.s21.rampMin` | 拉力速度斜坡起点 grapple_speedRampMin | 50 u/s | 1.27 m/s | 0.6944 H/s | — | 50 | 一致 |
| P-03 | `grapple.s21.rampMax` | 拉力速度斜坡终点 grapple_speedRampMax | 800 u/s | 20.32 m/s | 11.11 H/s | — | 800 | 一致 |
| P-04 | `grapple.s21.rampTime` | 斜坡用时 grapple_speedRampTime | 1.5 s | — | — | — | 1.5 | 一致 |
| P-05 | `grapple.s21.accel` | 沿绳加速 grapple_accel | 1500 u/s² | 38.1 m/s² | 20.83 H/s² | — | 1500 | 一致 |
| P-06 | `grapple.s21.decel` | 切向刹车 grapple_decel | 425 u/s² | 10.795 m/s² | 5.903 H/s² | — | 425 | 一致 |
| P-07 | `grapple.s21.airAccel` | 钩爪中侧键空中加速 grapple_airAccel | 650 u/s² | 16.51 m/s² | 9.028 H/s² | — | 650 | 一致 |
| P-08 | `grapple.wishCap` | 钩爪中空中速度上限 grapple_airSpeedMax | 420 u/s | 10.668 m/s | 5.833 H/s | — | 420 | 一致 |
| P-09 | `grapple.hopVz` | 挂上时上抬 grapple_attachVerticalBoost | 200 u/s | 5.08 m/s | 2.778 H/s | — | 200 | 一致 |
| P-10 | `grapple.s21.gravityFrac` | 拉的时候保留的重力比例 grapple_gravityFracMin | 0.25 | — | — | — | 0.25 | 一致 |
| P-11 | `grapple.s21.detachLengthMin` | 接近脱钩距离下限 | 33 u | 0.8382 m | 0.4583 H | — | 33 | 一致 |
| P-12 | `grapple.s21.detachLengthMax` | 接近脱钩距离上限 | 50 u | 1.27 m | 0.6944 H | — | 50 | 一致 |
| P-13 | `grapple.s21.detachAwaySpeed` | 离开锚点速度超过这个脱钩 grapple_detachAwaySpeed | 500 u/s | 12.7 m/s | 6.944 H/s | — | 500 | 一致 |
| P-14 | `grapple.s21.releaseSpeedLoss` | 按键脱钩扣速 grapple_detachSpeedLoss | 300 u/s | 7.62 m/s | 4.167 H/s | — | 300 | 一致 |
| P-15 | `grapple.s21.releaseSpeedMin` | 按键脱钩扣速下限 grapple_detachSpeedLossMin | 460 u/s | 11.684 m/s | 6.389 H/s | — | 460 | 一致 |
| P-16 | `grapple.s21.lowSpeed` | 低速超时脱钩的速度线 | 250 u/s | 6.35 m/s | 3.472 H/s | — | 250 | 一致 |
| P-17 | `grapple.s21.lowSpeedTime` | 低速超时（空中） | 1.5 s | — | — | — | 1.5 | 一致 |
| P-18 | `grapple.s21.impactBoostSpeed` | 撞上上抬 grapple_impactVerticalBoost | 300 u/s | 7.62 m/s | 4.167 H/s | — | 300 | 一致 |

### 跳板

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| F-01 | `defaults.JumpPadParams.push` | 跳板推力 JUMP_PAD_PUSH_VELOCITY | 1150 u/s | 29.21 m/s | 15.97 H/s | — | 1150 | 一致 |
| F-02 | `defaults.JumpPadParams.vertOverride` | 跳板竖直权重（v = 1150·normalize(ĥ + 2ẑ)） | 2 | — | — | — | 2 | 一致 |
| F-03 | `defaults.JumpPadParams.duckedVertScale` | 蹲着上跳板的竖直权重倍率 | 0.5 | — | — | — | 0.5 | 一致 |

### 升降机

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| F-04 | `defaults.GravityLiftParams.upSpeed` | Horizon 升降机上升速度 | 300 u/s | 7.62 m/s | 4.167 H/s | — | 300 | 一致 |
| F-05 | `defaults.GravityLiftParams.ejectUp` | 升降机弹出竖直速度 | 450 u/s | 11.43 m/s | 6.25 H/s | — | 450 | 一致 |
| F-06 | `defaults.GravityLiftParams.ejectHorizontal` | 升降机弹出水平速度 | 400 u/s | 10.16 m/s | 5.556 H/s | — | 400 | 一致 |
| F-07 | `defaults.GravityLiftParams.lifetime` | 升降机持续时间 | 10 s | — | — | — | 10 | 一致 |

### 兴奋剂

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| F-08 | `defaults.StimParams.fullDuration` | Octane 兴奋剂持续时间 STIM_DURATION | 6 s | — | — | — | 6 | 一致 |
| F-09 | `defaults.StimParams.severity` | 兴奋剂速度强度（0.15 量化成 38/255） | 0.15 | — | — | — | 0.14901960784313725 | 近似（差 0.65 %） |

### 镜头

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| C-01 | `camera.native.springK` | punch 弹簧刚度 punch_pilot | 65 | — | — | — | 65 | 一致 |
| C-02 | `camera.native.springC` | punch 弹簧阻尼 | 9 1/s | — | — | — | 9 | 一致 |
| C-03 | `camera.native.kickFallDistMinFt` | 落地 kick 起始下落距离（英尺，×12 = 120 u） | 10 | — | — | — | 10 | 一致 |
| C-04 | `camera.native.kickFallDistMaxFt` | 落地 kick 封顶下落距离（英尺，×12 = 840 u） | 70 | — | — | — | 70 | 一致 |
| C-05 | `camera.native.kickMaxScale` | 落地 kick 最大倍率 | 12 | — | — | — | 12 | 一致 |
| C-06 | `camera.native.slideFovScale` | 滑铲 FOV 倍率 | 1.1 | — | — | — | 1.1 | 一致 |
| C-07 | `camera.native.slideTiltSide` | 滑铲侧倾 slide_viewTiltSide | 15 deg | — | — | — | 15 | 一致 |
| C-08 | `camera.native.sprintTiltMaxRoll` | 冲刺转向横滚上限 sprinttiltMaxRoll | 2 deg | — | — | — | 2 | 一致 |
| C-09 | `camera.native.maxRoll` | 横滚总上限（**待核**：N2-C §7 说 40°，CAM2 §5 / CR §3.9 说没有总上限；见 99 B07-12） | 40 deg | — | — | — | 40 | 一致 |
| C-10 | `camera.native.grappleRollMax` | 钩爪横滚上限 | 20 deg | — | — | — | 20 | 一致 |
| C-11 | `camera.native.zipRollMax` | 滑索横滚上限 | 25 deg | — | — | — | 25 | 一致 |
| C-12 | `camera.native.traversalLerpIn` | 翻越镜头淡入 traversal_viewLerpInDuration | 0.15 s | — | — | — | 0.15 | 一致 |

### 开镜

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| A-01 | `（武器表：ads_move_speed_scale SMG）` | 开镜移速倍率 ads_move_speed_scale：SMG | 0.75 | — | — | — | 见 HSD-Unity PR #60（还没合并）的 Arsenal 表 | 不在 main |
| A-02 | `（武器表：ads_move_speed_scale 步枪）` | 开镜移速倍率：突击步枪 | 0.5 | — | — | — | 同上 | 不在 main |
| A-03 | `（武器表：ads_move_speed_scale 机枪）` | 开镜移速倍率：轻机枪 | 0.4 | — | — | — | 同上 | 不在 main |
| A-04 | `（武器表：ads_move_speed_scale 狙击）` | 开镜移速倍率：狙击枪 | 0.35 | — | — | — | 同上 | 不在 main |
| A-05 | `（武器表：zoom_time_in 步枪）` | 开镜时间 zoom_time_in：突击步枪 | 0.27 s | — | — | — | 同上 | 不在 main |
| A-06 | `（武器表：zoom_time_in 手枪）` | 开镜时间 zoom_time_in：手枪 | 0.18 s | — | — | — | 同上 | 不在 main |
| A-07 | `（规则：ADS 曲线）` | 开镜 FOV 曲线（进度 zf 线性，FOV 用 smoothstep 3t²−2t³） | 没测过 | — | — | — | 同上 | 不在 main |

### 后坐

| id | 参数名 | 含义 | R5 原值 [u] | [m] | 身高比例 | TF2 [u] | Unity [u] | 一致吗 |
|---|---|---|---|---|---|---|---|---|
| A-08 | `（规则：后坐弹簧回落 R-301 腰射）` | 后坐回落：R-301 腰射时间常数 | 0.46 s | — | — | — | 见 HSD-Unity PR #67（还没合并）ViewKick.cs | 不在 main |
| A-09 | `（规则：后坐弹簧回落 R-301 开镜）` | 后坐回落：R-301 开镜时间常数 | 0.14 s | — | — | — | 同上 | 不在 main |
| A-10 | `（武器表：viewkick_air_scale_ads）` | 空中开镜 kick 倍率 viewkick_air_scale_ads（18 把枪，G7 是 1） | 2 | — | — | — | 同上 | 不在 main |

## 出处

每一行的出处在 TSV 的"出处"列。主要来源：

- `research/phase2-local/static-values/STATIC-VALUES.md`：setfile（E0 census）和脚本常量。main
- `research/rea-native/convar-defaults/CONVAR-DEFAULTS.md`：原生 ConVar 默认值（Ghidra + 运行时）。main
- `research/rea-native/subsystems/N2-*.md`：原生规则（地面、跳跃、滑铲、lurch、翻越、钩爪 / 滑索 / 跳板、镜头）。main
- `R5-DIFF-ARCHIVE.md`：和 R5 不一样的地方的存档。main
- `tf2/static-values/T1-REPORT.md`：TF2 对照值。main
- `research/DESIGN-PHILOSOPHY.md` §9、P5–P7：开镜和后坐。main；细节在 `research/combat/RECOIL-VIEW.md`、`ADS-CURVES.md`（PR #93，还没合并）
- Unity 值：`unity-export/units-params.tsv`（HSD-Unity `units/switch` 84e7a4a（11-14 由 5c79a50 换新，表里的值没变） 的 `Docs/units/` 快照，PR #88，还没合并）
