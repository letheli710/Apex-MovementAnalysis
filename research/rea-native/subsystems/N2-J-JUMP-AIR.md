# N2-J 跳跃、空中、落地

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。

**结论先说**：M2 留下的三个"没解释"的问题，这次都在代码里找到了答案。
1. 连跳惩罚来自三个 census 没读过的 setfile 键 `antiMultiJump*`，不是 `skip_time`；
2. 空中残余增益来自 `player_extraairaccelleration`（2.0）加上按 3D 速度做的上限，数值模拟和 M2 实测吻合；
3. `skip_speed_reduce` 的生效条件：落地 1.0 s 内、水平速度超过冲刺上限时，减 100，但不低于冲刺上限。

## 1. 起跳 `Jump`（0x140a3b550）[native]

`Jump` 有 6434 字节，大部分是二段跳、超级跳、闪避、音效。这里只写普通起跳和滑铲跳。

### 1.1 高度

1. H = `jumpHeight`（census 56）；滑铲中改用 `slideJumpHeight`（50）。
2. **skip**（落地后很快起跳）：t = 现在 − 落地时刻（玩家偏移 0x3680）。t < `skip_time`（1.0）且不在墙跑时：
   - 水平速度 > `skip_jump_height_speed`（450）时，H × `skip_jump_height_fraction`（1.0，默认无效果）；
   - 上限 R = `skip_speed_retain`；默认 −1，表示用 `GetMaxSprintSpeed`（msc × `sprintspeed` = 299）；
   - 水平速度 > R 时：水平速度 = max(R, 水平速度 − `skip_speed_reduce`)（100）。
3. **anti-multi-jump**（连跳高度惩罚）：t < `antiMultiJumpTimeMax`，并且一个标志（0x36a9）为真时：
   - f = 1（t ≤ `antiMultiJumpTimeMin` 时），否则 f = (t − TimeMax) / (TimeMin − TimeMax)；
   - H × (1 − (1 − `antiMultiJumpHeightFrac`) × f)。
4. 起跳竖直速度 V = √(2 × `sv_gravity` × H)，沿"上"方向加到速度上。钩爪中再乘 `grapple_jumpFrac`。

### 1.2 滑铲跳

只在滑铲中、且"滑铲加成待退还"标志（0x2d76）为真时：
1. 如果**下蹲动作还没完成**（下蹲状态 ≠ 2），并且距离滑铲开始不到 0.4 s：水平速度减去本次滑铲的加成量（0x2d7c）。
2. 然后，如果 0.85 × `slideMaxJumpSpeed` < 水平速度 < `slideMaxJumpSpeed`（census 350，即 297.5 到 350 之间）：水平速度抬到 350。
3. 清掉标志，所以每次滑铲最多处理一次。

下蹲状态和计时在 `Duck` 里（见 [N2-S-SLIDE.md](N2-S-SLIDE.md) §3）：滑铲时下蹲过渡是 200 ms，所以第 1 条实际只在滑铲开始约 0.2 s 内起作用。

## 2. 空中加速 `AirAccelerate`（0x140a485e0）[native]

参数：wishdir、wishcap（M2：`airSpeed` × msc = 69）、加速度 A（`airAcceleration` 500）、dt。

- addspeed = wishcap − v·wishdir。
- **addspeed > 0**：v += min(addspeed, A × dt) × wishdir。不乘 wishspeed，和 M2 拟合一致。
- **addspeed ≤ 0**（沿意图方向已经达到上限）：
  - v += `player_extraairaccelleration`（2.0）× ft × wishdir；
  - 然后 |v| 不超过 max(加速前的 **3D** |v|, wishcap)。

第二条的效果：竖直速度不为 0 时，3D 上限比水平速度大，所以水平方向能"借"到一点点速度，同时竖直分量被同比例压缩一点。

**数值核对**（按代码顺序模拟：重力半步 → `AirAccelerate` → 重力半步；h = 299，起跳 V = √(2·750·56)，dt = 1/144，按住 W）：

| 量 | 模拟 | M2 实测（e2_keepfwd） |
|---|---|---|
| 整段跳跃的水平净增 | 0.316 u/s | **0.301 u/s** |
| 拟合成 c·vz² 的系数 c | 1.36e-5 | **1.39e-5** |

在 M2 测量精度内吻合。M2 的 §3.1 和开放问题 6 可以关闭。

## 3. 落地

### 3.1 `SetGroundEntity`（0x140a51650）[native]

- 落地时记录落地时刻（0x3680），作为 skip、anti-multi-jump 和落地减速的计时起点。
- 二段跳恢复：`skip_replenish_double_jump`（默认 1）为真，或者距离上次落地 ≥ `skip_time` 时，调用 `TouchGround` 恢复二段跳等能力。默认情况下每次落地都恢复。

### 3.2 落地减速 `LandSlowdown_Scale`（0x140b09a60）[native]

落地后 `landSlowdownDuration` 内，如果下落高度（0x3684）> `landSlowdownHeightMin`：
- 高度系数 a = clamp((高度 − HeightMin) / (HeightMax − HeightMin), 0, 1)；
- 时间系数 b = (t / Duration) ^ `landSlowdownTimePower`；
- 返回 1 − (1 − b) × a × (1 − `landSlowdownFrac`)，用作速度上限的倍率（[native-inf]：调用方是 `GetRecentLandingMoveSpeedScale` 一带）。

另一个函数（0x140b02ca0）读 `landSlowdownNoSprintFrac`，可能决定落地后能否冲刺，未读。

## 4. SDK 钩子

| 钩子 | 文件 | 我们的测试里 |
|---|---|---|
| `Jump` | `dodge_rules.cpp`（空中闪避规则）、`double_jump_power.cpp`（Sparrow 二段跳能量） | 不是 Sparrow，也没有闪避键，**不起作用**（N2 只看了钩子的说明和开关，没有逐行读） |
| `TouchGround`、`SuitPowerUpdate` | `double_jump_power.cpp` | 同上 |
| `AirMove` | `trigger_cannon.cpp` | 只在重力炮飞行锁定时 |
| `AirAccelerate` | `wall_launch.cpp` | 只在 Sparrow 墙面弹射时；否则直接调原生函数（已读源码确认） |

## 5. 和实测对照（初表）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| J-01 | 起跳速度 V = √(2gH)，惩罚作用在高度上 | §1.1 | M2：V = √(2·g·jumpHeight·frac)，按高度线性优于按速度线性 | **一致** |
| J-02 | **连跳惩罚参数** | `antiMultiJumpTimeMin` / `TimeMax` / `HeightFrac`；H × (1 − (1 − frac)·f) | M2：frac(t) = clamp(0.3 + 0.7·(t − 0.15)/0.60, 0.3, 1)，"census 里没有对应的键" | **形状一致**。预测这三个键是 0.15 / 0.75 / 0.3。它们不在 census 里，N4 用 `bridge_classvar_get` 读出确认 |
| J-03 | `skip_time` 是不是连跳惩罚 | 不是。`skip_time` 管的是超速削减（§1.1 第 2 条）和二段跳恢复 | 计划 §6 曾记为"对不上（1.0 s vs 0.75 s）" | **矛盾消除**：两者是不同机制 |
| J-04 | 超速连跳削减 | 落地 1.0 s 内、h > 299 时：h = max(299, h − 100) | M3：350 时连跳一律出 299；数据分不开 min(v, 299) 和 max(v − 100, 299) | **一致**，而且代码给出了 M3 分不开的那个答案：**max(v − 100, 299)**。预言：450 连跳出 350 |
| J-05 | 空中残余增益 | extra air accel 2.0 + 3D 上限（§2） | M2：+0.301 u/s / 跳，≈1.39e-5·vz² | **一致**（模拟 0.316，1.36e-5） |
| J-06 | 空中加速不乘 wishspeed | addspeed > 0 时 min(addspeed, A·dt) | M2：A·dt，上限 69 | **一致** |
| J-07 | 滑铲跳抬到 350 | 297.5 < h < 350 时抬到 350 | M10：0.60 s，317 → 350.0（sd 0）；0.25 s 397、0.40 s 361.5、1.0 s 236 都保持 | **一致**：397 和 361.5 > 350 不动，236 < 297.5 不动 |
| J-08 | 滑铲早跳扣加成 | 滑铲开始 0.4 s 内且下蹲未完成（滑铲时下蹲过渡 200 ms）：减去加成量 | M10：0.10 s 434 → 273（扣约 161）；0.25 s 不扣。M2：退还窗口在 (0.201, 0.597] | **一致**：两组实测都在约 0.2 s 的边界两侧 |
| J-09 | 落地减速 | §3.2 的公式 | M2：没测（需要从高处落下） | **只有代码** |
| J-10 | 每次落地都恢复二段跳 | `skip_replenish_double_jump` = 1 | M7 / M8 的二段跳实验 | **一致**（定性） |

## 6. 还没读的

- `AirMove`（0x140a48f90）本体：`airSpeed` / `airAcceleration` 怎么取、`airDrag`、`airFriction`、钩爪空中加速。
- 二段跳、超级跳、闪避在 `Jump` 里的分支。
- `antiMultiJump` 生效需要的标志 0x36a9 何时为真。
- 0x140b02ca0（落地后能否冲刺）。
