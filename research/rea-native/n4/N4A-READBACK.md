# N4-A setfile 键批量补读

日期 2026-10-23。会话 `phase2-local/data/20261023_200358_N4A_classvars`（本机，原始日志不进 git）：R5Flowstate 本地，Gibraltar，120 fps（实测 119.85），1 次 basic 试验。

**方法**：把 N1 找到的全部 setfile 键描述符（`n1/scan_setfile_desc.py`）生成一个 cfg [hsd_n4a_classvars.cfg](hsd_n4a_classvars.cfg)，每行一条 `bridge_classvar_get <键>`，在客户端执行。用现有 runner：

```
py -3 tools/hsd_session.py --label N4A_classvars --trials 1 --run-base 20001 --batch-base 20001 -- \
    --schedule basic --fps 120 --legend gibraltar --warmup 0 --client-exec user/hsd_n4a_classvars
```

**结果**：669 个键（去重后）读出 666 个，0 个未知键。全部值在 [classvars-gibraltar.csv](classvars-gibraltar.csv)（键、值、类型、运行时偏移）。

## 1. 代码推出的预言：全部命中

| 键 | 来源 | 预言 | 实读 |
|---|---|---|---|
| `antiMultiJumpTimeMin` | N2-J J-02 | 0.15 | **0.15** |
| `antiMultiJumpTimeMax` | N2-J J-02 | 0.75 | **0.75** |
| `antiMultiJumpHeightFrac` | N2-J J-02 | 0.3 | **0.3** |
| `player_slideBoostCooldown` | N2-S S-02 | M8 实测的 1.6–2.1 s 之内 | **2** |
| `ziplineJumpOffSpeed` | N2-P2 Z-01 | 400 | **400** |

M2 的连跳惩罚 frac = clamp(0.3 + 0.7·(t − 0.15)/0.60, 0.3, 1) 现在三个参数都有出处了。

## 2. 新读到、可以直接用的值

| 组 | 键 = 值 | 对照 |
|---|---|---|
| 落地减速 | `landSlowdownDuration` 1、`TimePower` 2、`Frac` 0、`HeightMin` 300、`HeightMax` 800、`NoSprintFrac` 0.7 | M4 Octane 拟合的硬着陆恢复是 (t/1.0)²：**时长 1 s、指数 2 都对上** |
| 落地 view kick | `viewkickFallDistMin` 10、`Max` 70（英尺）、`MaxScale` 12 | N2-C §2 |
| 滑铲 FOV | `slideFOVScale` 1.1、`LerpInTime` 0.25、`LerpOutTime` 0.25 | N2-C |
| 横滚 | `sprinttiltMaxRoll` 2、`grapple_rollStrength` 1、`grapple_rollMax` 20、`ziplineRollMax` 25、`maxCameraRoll` 40 | N2-C §3 |
| 滑铲 | `slideRequiredStartSpeedAir` 90、`slideStopSpeed` 125、`slideMaxStopSpeed` 350、`slideSpeedBoostCap` 400 | N2-S |
| mantle | `mantleHeight` 80；`mantleDurationBelow` / `Level` / `Above` / `High` = 0.7 / 0.6 / 0.5 / 0.35 | N2-M；M8 测到的 T0 0.42–0.60 s |
| 其他 | `viewheight` (0, 0, 70)、`airSlowMoSpeed` 0.15、`ziplineJumpOffDampScale` 1、`viewPunchSpring` "punch_pilot"、`wallrun` false | |

## 3. 还没读的

- ~~ConVar `jumppad_vert_override_ducked_scalar`~~：已用 Ghidra 读出，客户端原生默认 1，本地生效 0.5（来自 SDK dedi）[hyb]。
- ~~只读了 Gibraltar~~：已补读其余 11 个传奇，见 §4。

## 4. 12 个传奇的补读（2026-10-23）

又开了 11 次游戏（会话 `N4A_classvars_<legend>`），每次 1 个传奇，方法同上（`--no-census`）。合并表 [classvars-by-legend.csv](classvars-by-legend.csv)（[classvars_by_legend.py](classvars_by_legend.py) 生成）：12 个传奇 × 666 个键，**138 个键因传奇而异**，去掉音效、特效、模型等之后，和移动有关的约 100 个。

和以前的实测对得上的：

| 键 | 值 | 对照 |
|---|---|---|
| `grapple_attachVerticalBoost` | Pathfinder **200**（其他 0） | M10：钩爪挂上时的"200 上跳"（grapple hop），这次找到出处 |
| `airAcceleration` / `airSpeed` | Horizon 800 / 80，其他 500 / 60 | census 已有 |
| `climbHeight` / `climbHorzSpeed` | Revenant 1250 / 300，其他 100 / 100 | M8 R2 Revenant 攀爬 |
| `jetpack*`、`airStrafeAcceleration` 200 | Valkyrie | M4 / M6-B Valkyrie |

S21 之后的内容（按规则不计入 S21，只记录）：Sparrow 的 `doubleJump` = true 和另一套钩爪参数（`grapple_decel` 2500、`speedRampMin/Max` 1500 等），Ash 的 `dodge` = true。

