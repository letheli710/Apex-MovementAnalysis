# HSD-Unity 参数：哪些 [fit] 可以升级为 [native]

日期 2026-10-23（N5）。对应计划 §4 N5 最后一条。

**这份表只列"出处"，不改 Unity。** 要不要把某个值改成原生值，或者改个注释，由用户决定（计划 §2）。行为要变的条目另见 [REFERENCE-CHANGES.md](REFERENCE-CHANGES.md)。

## 怎么读

- **Unity 位置**：HSD-Unity `Assets/HSD/R5Replay/Runtime/` 下的文件和字段。
  - `Params` = `R5MotorV2Params.cs`；
  - `Config` = `MovementConfig.cs` 的 `MovementConfigs.Reference()`。
- **现在的标签**：Unity 注释或 provenance 里写的出处。
- **原生出处**：账本 id 和 N2 / N4 文档。
- **升级结果**：
  - **A**：数值相同，只要把出处改成 [native]，行为不变；
  - **B**：原生是另一条规则，数值或行为会变，列进 [REFERENCE-CHANGES.md](REFERENCE-CHANGES.md)；
  - **C**：找到了原生出处，但值没直接读出来，或还有疑点，只能写 [native-inf]。

## 1. 地面、跳跃、滑铲（R5MotorV2 / Reference）

| Unity 位置 | 现在的值和标签 | 原生出处 | 升级 |
|---|---|---|---|
| `Params.stopSnapSpeed` | 1，M2 区间 (0.58, 1.58] 里假设的 Source 值 | `WalkMove`：摩擦和加速之后速度 < 1 就设为 0（G-06，N4-D） | **A** |
| `Params.multiJumpHoldT0` / `multiJumpRampT` | 0.15 / 0.60，M2 拟合 | setfile `antiMultiJumpTimeMin` 0.15、`antiMultiJumpTimeMax` 0.75，ramp = 0.75 − 0.15 = 0.60（J-02，N4-A 实读） | **A** |
| `Params.antiMultiJumpHeightFrac` | 0.3，census | 同一组 setfile 键（J-02） | **A**（已是 census） |
| `Params.crouchSpeed` / `crouchDeceleration` | 80 / 1500，M2 拟合 | `speed` / `deceleration` 按姿态取值，蹲姿那一行（G-05）。`bridge_classvar_get` 只能读到站姿那一行 | **C** |
| `Params.lurchLamMax` | 0.7，M3 拟合 | `jump_grace_strength`（L-02） | **A** |
| `Params.lurchFullEnd` / `lurchZero` | 0.2 / 0.5，M3 拟合 | `jump_graceperiodmin` / `max`（L-03） | **A** |
| `Params.lurchClamp` 209.3、`Config` `lurchClampSprintFraction` 0.7 | M3 / M4 拟合 | `jump_grace_max` × msc × `sprintspeed`（L-04、L-05） | **A** |
| `Config` `lurchCutoffSpeed` 1100 | M6-A1 [src]（SDK 的 `bridge_lurch_cutoff_speed`），没实测 | 客户端原生 `jump_grace_cutoff_speed` 1100；N4-D 实测 1090 有、1110 没有（L-10） | **A** |
| `Params.hullCrouchTime` | 0.2，M5 实测 | `Duck` 计时：滑铲中 200 ms，平时 400 ms（S-08、CAM-10；C3 眼高 0.21 s） | **A**（站立下蹲的 0.4 s 另记） |
| `Config` `slideWantToStopDecel` / `slideMaxStopSpeed` | 400 / 350，census + M10 拟合 | 同名 setfile 键（G-11、S-04） | **A** |
| `Params.slideStopSpeed` | 125，census | `slideStopSpeed`：移动后速度 < 125 结束（S-05） | **A** |
| `Params.slideBoostRefundWindow` | 回放 0.4（phase-1 源码）；`Config` 0.225 [fit，中点] | 0.4 s 内**并且**下蹲过渡（滑铲时 200 ms）还没完成（J-08） | **B** |
| `Config` `slideMaxJumpSpeedWindow` | 0.8 [fit，中点] | 没有时间窗：只把 297.5 < h < 350 的速度抬到 350（J-07） | **B** |
| `Config` `slideBoostRearm` 1.8 | [inf]，区间 (1.0, ~2.1) | `player_slideBoostCooldown` 2 s，从上一次**开始滑铲**算（S-02，N4-A 实读、N4-C 实测） | **B** |
| `Params.groundJumpClampToSprintCap` | min(v, 299)，M3 | max(299, h − 100)，只在 `skip_time` 内（J-04） | **B** |
| `Params.slideSlopeGravityScale` | 1，M6-A4 [design] | `Gravity_HalfStep` 的滑铲贴地项 g·n_h·n_z，系数就是 1（S-09） | **A** |
| `Config` `groundVectorRedirect` | M5 实测（"偏离部分按 1250 衰减"） | `Friction`：偏离部分按 D 衰减，意图方向保留到 wishspeed（G-07） | **A**（结构对；细节差见 REFERENCE-CHANGES §1） |

## 2. 技能（Abilities/）

| Unity 位置 | 现在的值和标签 | 原生出处 | 升级 |
|---|---|---|---|
| `LandingSlowdown/LandingSlowdown.cs` `duration` / `exponent` | 1.0 / 2，M4 Octane 拟合 | setfile `landSlowdownDuration` 1、`landSlowdownTimePower` 2（J-09，N4-A） | **A** |
| 同上 `a` / `b`（落地速度 → f0） | M4 拟合 | 原生按**下落高度**算：`landSlowdownHeightMin` 300、`HeightMax` 800、`Frac` 0、`NoSprintFrac` 0.7。两种写法是否等价还没对照 | **C** |
| `Zipline/ZiplineAbility.cs` `jumpOffCap` / `jumpOffVz` | 400 / 289.828，M9 实测 | `ziplineJumpOffSpeed` 400（N4-A）+ √(2g·`jumpHeight`) = 289.83（Z-01） | **A** |
| 同上 `speed` / `detachSpeed` | 600 / 600 | clamp(v·d, `ziplineSpeed`, `ziplineDetachSpeed`)（Z-02） | **A** |
| `Grapple/GrappleAbility.cs` `rampMin` / `rampMax` / `rampTime` | 50 / 800 / 1.5 | lerp(50, 800, t / 1.5)（P-01） | **A** |
| 同上 `decel` 425、`airAccel` 650 | M10 实测 | `grapple_decel` 425、`grapple_airAccel` 650 / `grapple_airSpeedMax` 420（P-02、P-04） | **A** |
| 同上 `releaseSpeedMin` / `releaseSpeedLoss` | 460 / 300 | `grapple_detachSpeedMin` / `SpeedLoss`（P-06） | **A** |
| 同上 `lowSpeed` / `lowSpeedTime` / `WallTime` / `GroundTime` | 250 / 1.5 / 1.2 / 0.7 | 低速脱钩计时（P-07）。代码一致，但**没实测** | **C** |
| 同上 `detachLength` 45 | M10 实测 35–53 u | `grapple_detachLengthMin` / `Max` 33 / 50（P-05）。原生是区间，Unity 用一个值 | **C** |
| 同上 `hopVz` 200 | M10 实测"挂上时上跳" | Pathfinder 的 setfile `grapple_attachVerticalBoost` 200，其他传奇 0（N4-A §4） | **A** |
| 同上 RF 模型 `alongAccel` 541.016、`crossBrake` 422.998 | M4b / M5 的 RF 拟合（旧模型，回放 M4 用；S21 路径用上面的 ramp 参数） | 原生 ramp 斜率 (800 − 50) / 1.5 = 500、切向制动 425（P-01、P-02）。RF 是另一种写法（沿绳加速度常数 + 重力分量），两组数不能直接替换 | **C**（只作对照，不建议改旧回放） |
| `Climb/ClimbAbility.cs` `nativeJumpWindow` | 0.1025，M6 / M8 拟合 | 结束前约 0.1 s，和 `automantle_jumpoff_duration` 0.1 一致（M-04） | **C**（机制是推断） |
| 同上 `slideBoostRearm` | 1.8（Reference 设置） | 同 §1 的 S-02 | **B** |
| 同上 `mantleTimeBase` / `PerUnit` | 0.1728 / 0.0055，M6 拟合 | setfile `mantleDurationBelow` / `Level` / `Above` / `High` 0.7 / 0.6 / 0.5 / 0.35、`mantleHeight` 80（N4-A）。怎么从这四个值得到"随高度线性"还没读出来 | **C** |
| `JumpPad/` 起跳 1150、V 2 | M4 拟合 | PUSH 1150、V 2.0（F-01） | **A** |
| 同上 蹲姿 V 1 | M4 拟合 | `jumppad_vert_override_ducked_scalar`：客户端默认 1，本地生效 0.5，来自 SDK dedi（F-02 [hyb]） | **C** |

## 3. 镜头（Game/Runtime/CameraFeedback.cs）

M5.5 的镜头是用户验收过的**设计**值，不是 [fit]，所以不在"升级"的范围里。原生值只作参考，见 [../subsystems/N2-C-CAMERA.md](../subsystems/N2-C-CAMERA.md) 和 [../camera/C3-CAPTURE.md](../camera/C3-CAPTURE.md)：
- punch 弹簧 k 65、c 9；
- 落地 kick：v_min 424、v_max 1122、MaxScale 12，在水里落地 × 0.2；
- 滑铲倾斜 15°；
- 滑铲 FOV × 1.1，进入和退出各 0.25 s；
- 冲刺倾斜 2°。

## 4. 统计

- **A**（只改出处）：20 项；
- **B**（行为会变）：5 项（S-02 在 §1 和 §2 各出现一次，算 4 条规则），都在 REFERENCE-CHANGES 里；
- **C**（出处找到，还要核对）：8 项。
