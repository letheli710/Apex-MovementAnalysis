# N2-C 第一人称镜头手感（C2）

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。效果清单见 [camera/CAMERA-INVENTORY.md](../camera/CAMERA-INVENTORY.md)（C1），这里逐个写做法。

**这一轮读了最核心的几项**：punch 弹簧、落地 view kick、横滚汇总（含滑铲倾斜）。其余只确认了参数和默认值。

## 1. View punch 弹簧（CAM-01）[native]

- 玩家身上有**两组 punch**，每组 3 个轴，各有"角度"和"角速度"两个状态（玩家 0x2430 / 0x243c 一组，0x2448 / 0x2454 一组）。
- 每条命令做一次阻尼弹簧积分：角加速度 = −k × 角度 − c × 角速度。
- k、c 平时来自 ConVar：`viewpunch_base_springConstant` X/Y/Z = **65**，`viewpunch_base_springDamping` X/Y/Z = **9**。某些情况下（[native-inf]：手持武器有自己的弹簧设置时）改用一张表里的值，按一个比例插值。
- 换算：固有频率 ω = √65 ≈ 8.06 rad/s（约 1.28 Hz），阻尼比 ζ = 9 / (2·√65) ≈ **0.56**。**欠阻尼**：踢一下以后会稍微回弹一次；包络按 e^(−ζωt) ≈ e^(−4.5t) 衰减，约 0.5 s 后剩一成左右。
- 各种 punch（落地、墙跑）都是给**角速度**加一个量，不直接改角度。

## 2. 落地 view kick（CAM-02）[native]

`Land_ViewKick`（0x140a35750），输入是落地时的下落速度 v：

1. v_min = √(2g × 12 × `viewkickFallDistMin`)，v_max = √(2g × 12 × `viewkickFallDistMax`)。× 12 说明这两个键的单位是**英尺**。
2. 强度 s：
   - v < v_min：s = v / v_min；
   - v_min ≤ v ≤ v_max：从 1 线性升到 `viewkickFallDistMaxScale`；
   - v > v_max：s = MaxScale；
   - 下蹲落地：s × **0.2**。
3. 三个随机数 r ∈ [−0.5, 0.5]（种子来自命令号，客户端和服务器一致）：
   - 第一组弹簧：俯仰角速度 += s × (2 + 0.75·r₁) × 20，横滚角速度 += s × r₃ × 20；
   - 第二组弹簧：俯仰角速度 += s × (2 + 0.75·r₁) × 0.2 × 20，横滚 += s × r₃ × 0.2 × 20。
4. v > √(2g × 12) 时触发手柄震动，按高度分软 / 硬。

这三个 setfile 键不在 census 里，值要在 N4-A 补读。

## 3. 横滚汇总（CAM-05）[native]

`View_CalcRoll`（0x140afc480）把下面几项加在一起：

| 来源 | 做法 | 默认参数 |
|---|---|---|
| Source 侧移横滚 | `sv_rollangle` × 侧向速度 / `sv_rollspeed` | **`sv_rollangle` = 0，默认关闭** |
| 墙跑倾斜 | 墙跑中按速率追目标 | `wallrun_maxViewTilt` 10°、`wallrun_viewTiltSpeed` 6。S21 墙跑关闭，不起作用 |
| 闪避倾斜 | 闪避后按衰减时间回落 | `dodge_viewTiltMax` 10。闪避是 S21 之后的内容（Sparrow 等），不起作用 |
| **滑铲倾斜** | 状态 s：滑铲中目标 1，否则 0；按速度在 `slideStopSpeed` 到 `slide_viewTiltPlayerSpeed` 之间缩放；以"增加 / 恢复"速率追目标；横滚 = s × `slide_viewTiltSide` × 侧向分量（[native-inf]） | 15°、400 u/s、增加 5、恢复 2.5 |
| 冲刺倾斜 | setfile `sprinttiltMaxRoll`，和 `sprinttilt_*`（CAM-07）配合 | `sprinttilt_accel` 35、`maxvel` 2、`turnrange` 120 |
| 钩爪 / 摆荡 / 滑索横滚 | 三者取一：钩爪中用钩爪横滚（CAM-11），在滑索上按类型选摆荡（CAM-12）或滑索（CAM-13） | setfile `grapple_roll*`、`swingRoll*`、`ziplineRoll*` |

钩爪 / 滑索横滚的结果以 6.667 × ft 的速率平滑过去，所以大约 0.15 s 跟上。

**结论**：S21 里真正起作用的横滚只有**滑铲倾斜、冲刺倾斜、钩爪 / 滑索横滚**。侧移横滚、墙跑倾斜、闪避倾斜在 S21 默认都不生效。

## 4. 其他效果的参数（只确认了默认值或读取位置）

| id | 效果 | 已知 |
|---|---|---|
| CAM-07 | 冲刺倾斜 | `sprinttilt_accel` 35、`maxvel` 2、`turnrange` 120°；结果写进 PoseParameter，由动画执行 |
| CAM-09 | 滑铲 FOV | setfile `slideFOVScale`、`slideFOVLerpInTime`、`slideFOVLerpOutTime`（值待 N4-A） |
| CAM-16 | 攀越视角过渡 | `traversal_viewLerpInDuration` 0.15 s，`traversal_viewLerpOut` = 1（开） |
| CAM-20 | view drift | `viewDrift` = 1（开），40 个振幅 / 频率 / 相位参数 |

## 5. 和实测、HSD 对照（初表）

R5 镜头**没有实测**（C3 还没做），所以只能和 HSD M5.5 的设计对照。M5.5 是用户验收过的设计，这里的结论只是参考。

| id | 项 | 原生 | HSD M5.5 | 结论 |
|---|---|---|---|---|
| CAM-01 | punch 弹簧 | k 65、c 9，ζ ≈ 0.56，欠阻尼 | `CameraFeedback.cs` 的 CriticalSmoother（临界阻尼平滑） | **结构差**：原生有一次回弹，HSD 没有。只是参考，不改 |
| CAM-02 | 落地 kick | 按落地速度分段缩放，下蹲 × 0.2，有随机 | M5.5 有落地反馈（读落地减速的起点） | **待对照**：要先读出三个 `viewkickFallDist*` 键 |
| CAM-05 | 侧移横滚 | 默认关闭 | 未查 | **只有代码**：S21 侧移时镜头不横滚 |
| CAM-05 | 滑铲倾斜 | 15°，按速度缩放，增加 5 / 恢复 2.5 | M5.5 有滑铲镜头 | **待对照** |

## 6. 还没做的

- 各效果的 setfile 值（`viewkickFallDist*`、`slideFOV*`、`sprinttiltMaxRoll`、`grapple_roll*` 等），N4-A 补读。
- 滑铲倾斜函数 0x140afc040 的精确公式、冲刺倾斜、眼高变化曲线（CAM-10）、cockpit sway / spring（CAM-18 / 19 是否动镜头）。
- C3 逐帧实测（要改 HSD.MoveDiag，先问用户）。
