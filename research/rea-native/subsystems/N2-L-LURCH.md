# N2-L Lurch / tap-strafe

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。

**结论先说**：M3 的 lurch 模型（方向插值、0.2 / 0.5 s 窗口、209.3 夹紧）在原生代码里**每一项都有出处**。M3 和 M8 的大部分实测现象都能直接从代码推出来。

## 1. 位置

- `AirMove_TapStrafe`（0x140a48a30，SDK 名）：只在 S21 客户端有。`jump_grace_*` ConVar 在 S3 dedi 上不存在（convar-defaults），dedi 上的 lurch 是 SDK 重写的 `SDK:game/server/tapstrafe.cpp`。
- 辅助：`TapStrafe_MultiTapDecay`（0x140a48810）、`GetMaxSprintSpeed`（0x140b09c00）、`TapStrafe_WindowHint`（0x140a58ec0）。

## 2. 公式 [native]

ConVar 默认值来自 [convar-defaults/CONVAR-DEFAULTS.md](../convar-defaults/CONVAR-DEFAULTS.md)；`max_decay` 是 N2 补读的。

### 2.1 触发条件（全部满足才执行）

1. 这条命令上有**方向键的按下边沿**：前、后、左、右（按钮位 0x8 / 0x10 / 0x200 / 0x400 的"本条命令按下"）。`jump_grace_require_tap` = 0 时不要求边沿。
2. 距离最后一次使用手柄 ≥ `jump_grace_controller_disable_duration`（默认 −1，等于不限制）。
3. t − t₀ < `jump_graceperiodmax`（0.5 s）。t₀ 是起跳时刻：`jump_grace_jump` = 1（默认）时用玩家偏移 0x3670 的时间，否则用 0x366c（[native-inf]：两种"跳跃时刻"，比如普通起跳和更广义的起跳）。
4. 距离上一次 lurch > `jump_grace_min_tap_period`（默认 0）。
5. 本次空中的 lurch 次数 < `jump_grace_max_tap_count`（默认 1000）。
6. 水平速度 h ≤ `jump_grace_cutoff_speed`（1100，含等于）。

### 2.2 意图方向

`require_tap` = 1（默认）时用**数字按键**，不是轴向值：
- 前后 = (前键 ? 1 : 0) − (后键 ? 1 : 0)；
- 左右 = (右键 ? 1 : 0) − (左键 ? 1 : 0)；

再用视角的前向、右向合成意图方向 w，归一化。

`jump_grace_limit_to_90`（默认 0）打开时，会去掉 w 里和速度相反的分量。

### 2.3 强度 λ

- s = clamp((t − t₀ − 0.5) / (0.2 − 0.5), 0, 1)：0.2 s 内为 1，到 0.5 s 线性降到 0；
- 多次 tap 衰减系数 m：每次 lurch 前乘 (1 − 速度衰减)。速度衰减由 `TapStrafe_MultiTapDecay` 按速度算，但 `..._velocity_based_max_decay` 默认是 0，所以**默认不衰减**；
- λ = s × m × `jump_grace_strength`（0.7）。

### 2.4 改方向

- d = 当前水平速度方向；
- 目标方向 d′ = d + (w − d) × λ；|d′| ≤ 0.01 时不执行；
- 次数 +1；次数 ≥ `jump_grace_decay_start_tap_count`（1000）后 m × `jump_grace_multi_tap_decay`（1.0）。默认情况下这一步不起作用；
- 想要的新速度 = h × d′ / |d′|（**大小不变**，只换方向）；
- Δv = 想要的新速度 − 当前水平速度；**|Δv| ≤ `jump_grace_max` × msc × `sprintspeed`(站姿)**；
- 水平速度 += Δv，竖直速度不变；
- 最后对新速度跑一次 `WindowHint`（窗户辅助）。

## 3. 和实测对照（初表）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| L-01 | 方向插值 | d′ = d + (w − d)·λ，大小保持 | M3：朝"速度方向和意图方向的插值"转，速度保持 | **一致** |
| L-02 | 满强度 0.7 | λ = s × `jump_grace_strength`(0.7) | M3：λ = 0.70000（n = 44） | **一致** |
| L-03 | 窗口 0.2 / 0.5 s，线性，按时间算 | `graceperiodmin` / `max` = 0.2 / 0.5，按时间 | M3：0.2 s 满强度，线性到 0.5 s 为 0，按时间不按帧，±1 ms | **一致** |
| L-04 | **夹紧 209.3** | `jump_grace_max`(0.7) × msc(1.15) × `sprintspeed`(260) = **209.3** | M3、M8：209.30，不随入口速度变化 | **一致，出处找到**（convar-defaults 里这一项原来写着"没有 ConVar 出处"） |
| L-05 | 夹紧随 msc 变化 | 公式里有 msc | 只测过 msc = 1.15 | **新预言**：stim、拿武器等改变 msc 时，夹紧应按比例变化。N4 可测 |
| L-06 | 用按键不用轴向 | `require_tap` = 1 时按键合成 | M8 b1：W+A 时方向是等权 45°，不是第一条命令的轴（0.5, −1） | **一致** |
| L-07 | 相反按键没有 lurch | A+D 时左右 = 0，前后也为 0 → w = 0 → d′ = d·(1 − λ)，方向不变 | M8 b2：A 按住再按 D，没有 lurch | **一致** |
| L-08 | 窗口只由跳跃打开 | t₀ 是起跳时刻；走下台阶不更新 t₀ | M8 d：走下台阶后不会 lurch | **一致** |
| L-09 | 连续 tap 不衰减 | `max_tap_count` / `decay_start_tap_count` = 1000，`multi_tap_decay` = 1.0，速度衰减默认 0 | M8 c：720°/s 下 15 次 tap，每次都有效 | **一致** |
| L-10 | 高速截断 1100 | 客户端原生就有，h ≤ 1100 时才执行 | 客户端没测过；dedi 上是 SDK 的 `bridge_lurch_cutoff_speed` = 1100 | **只有代码**（客户端）。M3 的 dedi 一致性 101 / 102 是 SDK 重写的效果 |
| L-11 | M8 b1 残差 11.6 u/s | lurch 本身没有额外项 | M8 b1 残差 11.6 | **未定**：可能来自同一条命令里的 `AirAccelerate`（见 N2-J 和 N2-G G-08 的输入曲线） |
| L-12 | 反向连按停在约 156° | 每次 tap 都是独立的插值，λ 随时间降低 | M8 a：间隔 0.05 s 时 156.4°，0.1 s 时 104.6° | **一致**（定性）：后面的 tap 落在衰减段，λ 越来越小 |

## 4. SDK 钩子

`AirMove_TapStrafe` 被 `SDK:game/client/mantle_boost.cpp` 的 `Hook_AirMove_TapStrafe` 包着：

| 情况 | 效果 | 默认 |
|---|---|---|
| 重力炮飞行锁定中 | 不执行 lurch | 只在重力炮触发时 |
| mantle boost 状态 = 4（mantle boost 刚生效） | 不执行 lurch | `mantle_boost_enabled` = 1、`mantle_boost_disables_tap_strafes` = 1，**默认开** |
| 其他 | 直接调用原生函数 | |

**影响**：M3 / M8 的普通 lurch 测试没有经过 mantle boost，结果是原生的。但凡是 mantle 之后的 lurch（M8 R3 的 SG 测试、mantle boost 相关路线），都受这个 SDK 规则影响，不能当原生行为。

## 5. 对 Unity 的意义（只是建议，不改代码）

- HSD 的 lurch 模型和原生公式的形状一致，可以把参数标签从 [fit] 升级为 [native]。
- 夹紧值目前是常数 209.3。按原生公式应该是 0.7 × msc × sprintspeed（L-05）。
- "按键合成意图"和"相反按键抵消"在 HSD 里已经按 M8 做了（M10-D2），可以对照 §2.2 再核一遍。
