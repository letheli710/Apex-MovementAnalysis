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

- ConVar（不是 setfile 键）：`jumppad_vert_override_ducked_scalar`（F-02，预期 0.5），用 Ghidra 离线读即可。
- 只读了 Gibraltar。按传奇不同的键（喷气、钩爪等）要用对应传奇再读一次。
