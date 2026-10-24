# Reference 修改建议清单（N5）

日期 2026-10-23。对应计划 §4 N5 第二条。

**只列建议，不实施。** Agent 不改 Unity，每一条由用户决定（计划 §2；[../UNITY-CHANGE-PROPOSALS.md](../UNITY-CHANGE-PROPOSALS.md) 的"决定"一栏）。这份清单在 UNITY-CHANGE-PROPOSALS 的基础上做了两件事：
- 对着 HSD-Unity 现在的代码（`HSD-Unity` main，6b27c04，只读）逐条核对"Unity 现在"那一栏；
- 写出每条改动会影响到的回放、测试和演示。

## 0. 先说明两个电机

HSD-Unity 里有两套地面规则，账本过去没有分清：

| | 回放电机 | Reference |
|---|---|---|
| 是什么 | `R5MotorV2` 默认参数 | `MovementConfigs.Reference()`，游戏里的身体用它 |
| 用途 | 逐条重放 M2 / M3 的 R5 试验 | 游戏、演示、练习地图 |
| 规则 | 保持 M2 / M3 的输出**逐位不变** | 在回放电机上打开一组选项（M4–M10 加的） |

所以：
- **改动都应该只加在 Reference 上**，做成新选项，沿用现有写法（`R5MotorV2Params` 里的 `[NonSerialized]` 开关，由 `MovementConfigs.Reference()` 打开）；
- 回放电机不动，M2 / M3 的回放报告就不会变。

## 1. 核对后的更正

| id | 过去写的 | 实际（N5 核对） |
|---|---|---|
| **G-07** 地面转向 | "Unity 每条命令 v = s·wishdir，转向是瞬间的"，影响**高** | 只有回放电机是瞬间的。Reference 打开了 `groundVectorRedirect`（M5）：偏离意图方向的部分按 D 衰减，意图方向按加速段加速。这和原生 `Friction` 是同一个结构。用 N4-B 的 20 次按键急转逐命令对照：Reference 误差 rms **0.11–0.60 u/s**（最大 2.8），原生公式 0.002–0.046，瞬间模型 64–195（`n4/keyturn_analysis.py` 的 `vector` 列）。**Reference 这一条的影响降为低** |
| **S-09** 斜坡滑铲 | "Reference 用 M8 拟合 147 + 342·sinθ" | Reference 用的是 M6-A4 的 g·n_z·n_h（`slideSlopeGravityScale` 1），就是原生公式；M8-B 只加了"按住下蹲"的条件。M8 的拟合只写在文档里。**不需要改** |
| **L-10** lurch 截断 | 账本写 "not modelled" | Reference 有 `lurchCutoffSpeed` 1100（M6-A1，当时出处是 SDK），现在也有原生出处和实测。**不需要改** |
| **CAM-01b** punch 不动准星 | "M5.5 没查" | `CameraFeedback` 把瞄准和视觉 kick 分开，瞄准原样返回，和原生一样。**不需要改** |

## 2. 建议（按影响排序）

"影响到的"一栏列的是：用到这个参数或规则的 HSD-Unity 文件和测试。改动做成 Reference 选项后，回放电机的测试（`R5MotorV2Tests`、`R5ReplayTests`、M2 / M3 回放）不变；Reference 的测试和演示需要重跑，有些期望值要更新。

| # | id | 内容 | Reference 现在 | 原生 | 影响 | 影响到的 |
|---|---|---|---|---|---|---|
| 1 | **G-12 / S-07** | 滑铲中转向 | 完全不能转向（`vel = dir·s`） | 意图方向里垂直于速度的部分按 `slideAccel`·msc 加速；N4-C 实测侧向 41.1 u/s²，原生公式逐命令 rms 0.001 u/s | **中**：滑铲中按 A / D 能改方向，是滑铲手感的一大块 | `R5MotorV2.cs` 滑铲分支；`R5MotorM10CTests`、`M10CGameTests`；`MovementDemosM10C` 的滑铲演示；练习地图里含滑铲的路线和圈速（M10 记录 78.98） |
| 2 | **S-02** | 滑铲加成冷却 | `slideBoostRearm` 1.8 s，从上一次**加成**算；`ClimbAbility.slideBoostRearm` 同值（superglide） | `player_slideBoostCooldown` **2 s**，从上一次**开始滑铲**算，没加成的滑铲也刷新（N4-A 实读，N4-C 实测） | **中**：连续短滑铲时第三次有没有加成会不同；superglide 前的滑铲也受影响（M-07） | `MovementConfig.cs`、`ClimbAbility.cs`；`R5MotorM10CTests`、`R5MotorM9CTests`、`M9CGameTests`、`PracticeGameTests` |
| 3 | **J-07** | 滑铲跳抬到 350 | `slideMaxJumpSpeedWindow` 0.8 s 以内一律抬到 350 | 不看时间，只把 297.5 < h < 350 的速度抬到 350 | **中**：0.8 s 以后、速度在 297.5–350 的滑铲跳会被抬；0.8 s 以内、速度低于 297.5 的不再被抬 | `R5MotorV2.cs`；`R5MotorM10CTests` |
| 4 | **J-08** | 滑铲早跳扣加成 | `slideBoostRefundWindow` 0.225 s（区间中点） | 0.4 s 内**并且**下蹲过渡（滑铲时 200 ms）没完成 | **中**：分界从 0.225 s 变成"下蹲过渡完成"，约 0.2 s；以后如果改了下蹲时间，分界会跟着变 | `R5MotorV2.cs`；`R5MotorM10CTests`；`MovementDemo.cs`、`MovementDemosM10C` |
| 5 | **J-04** | 超速连跳 | `groundJumpClampToSprintCap`：min(h, 299) | `skip_time` 内 max(299, h − 100) | **低**：只在落地速度 > 399 时不同（例如 450 落地：原生 350，Reference 299） | `R5MotorV2.cs`；`R5MotorM3Tests`（回放电机，保持不变） |
| 6 | **G-07** | 地面转向的剩余细节 | 见 §1：结构已对 | ① 意图方向的速度只保留到 wishspeed（按 proj·wishspeed / h² 的比例）；② 加速后上限 max(\|v_old\|, wishspeed)；③ 输入曲线 m(2 − m)、冲刺 × 1.25（只在 m < 1 时起作用） | **低**：按键急转逐命令 0.1–0.6 u/s | `R5MotorV2.GroundVectorRedirect`；`PracticeGameTests` |
| 7 | **J-05** | 空中残余增益 | 没有 | extra air accel 2.0 + 三维速度上限，每跳约 +0.3 u/s | **低**（每跳 0.1 %） | `R5MotorV2.AirMove`；所有空中测试的期望值都会小幅变化 |
| 8 | **G-03** | 冲刺加速边界 | M2 规则 s + a·dt ≥ speed·msc | 固定边界 msc·speed − 1 | **低**：只差一条命令 | `R5MotorV2.GroundAccelRate`（回放电机共用，只能做成 Reference 选项） |

## 3. 不是改动、但 Reference 需要写清楚的

| id | 内容 |
|---|---|
| **M-08** | 原生 superglide（出口 460）和 SDK 的 mantle boost 状态机（出口 388.7 / 367.42）是两套行为。Reference 跟的是原生那一套（M8 / M9 的数据是关掉 SDK 后测的），应在 Reference 说明里写明 |
| **L-13** | SDK 在 mantle boost 状态里屏蔽 lurch。Reference 不需要跟 |
| **F-02** | 蹲姿跳板的 V 1.0 来自本地 SDK dedi 的 0.5 [hyb]；S21 正式服务器的值不知道 |
| **CAM-01 / CAM-02** | 镜头只作参考，M5.5 是用户验收过的设计。差别记在这里：原生落地 kick 是欠阻尼弹簧，约 0.16 s 到峰值，回弹一次，大小 2–43°（随落地速度变化）；M5.5 是临界阻尼，0.06 s 到峰值，不回弹，大小 0.8°（硬着陆 2.0°） |

## 4. 建议的顺序

如果用户决定要改，建议按这个顺序，每条单独一个提交，方便回退：
1. **#2 → #3 → #4**：滑铲加成冷却、350 抬升、早跳扣加成。这三条都是 M10-D1 那组滑铲规则，改的是同一段代码，测试也是同一个文件（`R5MotorM10CTests`）；
2. **#1**：滑铲转向。改动最大，会影响路线和圈速；
3. **#5–#8**：低影响，可以一起做，也可以不做。
