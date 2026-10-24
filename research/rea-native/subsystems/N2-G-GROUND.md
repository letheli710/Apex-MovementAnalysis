# N2-G 地面移动

日期 2026-10-23。目标 `r5apex_dx12.exe`，地址都是 dx12 版。只读：Ghidra 反编译（`n2/DecompileList.java`），用 N1 的名字标注（`n2/annotate.py`）。反编译原文在本机 `local/n2/`，不进 git；这里只写我们自己重述的公式。

标签：**[native]** 直接从代码读出；**[native-inf]** 读出但含推断（例如结构体字段的含义）。字段偏移的含义大多来自它在哪里被读、和哪个 setfile 键一起出现，都算 [native-inf]。

## 1. 每条命令的地面流程

`FullWalkMove`（0x140a4c810）里和地面相关的顺序 [native]：

1. `dt` = `AirSlowMo_TimeScale`（平时为 1）× 全局 frametime。
2. **重力前半步** `Gravity_HalfStep`（0x140a36130）：v.z −= 0.5 × `sv_gravity` × `gravityScale` × 若干修正 × dt。
3. 跳跃、攀爬、钩爪、触发推力等（不在本文）。
4. 在地面上 → `WalkMove`（0x140a4a7c0）；不在地面 → `AirMove`。
5. 落地检测、`CategorizePosition`。
6. **重力后半步**（同一个函数再调一次）。
7. 在地面时，去掉速度沿地面法线的分量。

重力分前后两个半步是 Source 的 StartGravity / FinishGravity 写法。

## 2. `WalkMove` 的地面分支

### 2.1 输入 → 目标速度 [native]

- 原始输入 (f, s) 来自命令的前后、左右轴。
- 一个玩家标志（偏移 0x2a2c，和 `GetPoseSpeed_Sprint` 里选冲刺速度的是同一个，[native-inf]：**冲刺中**）为真时，(f, s) × 1.25。
- **输入曲线**：幅度 m = |(f, s)|。
  - m > 1：归一到 1；
  - 0 < m ≤ 1：幅度改成 m·(2 − m)。所以 0.5 → 0.75，1 → 1。
- 侧向 × `speedScaleSide`；向后（f < 0）× `speedScaleBack`（census 都是 1）。
- 意图向量 = 前向 × f + 右向 × s，投影到地面平面上。
- 附近有其他玩家或物理物体时，加一个推开量（`sv_pushaway_*`，不展开）。
- **滑铲中**：意图里和当前速度同向的分量被去掉。只剩下垂直于速度的分量，所以滑铲时**只能转向，不能沿速度方向加速** [native]。
- 目标速度 wishspeed = min(|意图|, 1) × 最大速度（movedata 的 maxspeed，[native-inf]）；方向 wishdir 归一化。

### 2.2 加速度选择 `Ground_GetAccel`（0x140a36450）[native]

h = 水平速度大小，msc = 移动速度倍率（玩家偏移 0x3278，[native-inf]）。

| 条件（按顺序） | 加速度 |
|---|---|
| 滑铲中 | `slideAccel` × k × msc |
| `sprintAcceleration` ≥ 0 且 h > msc × `speed` − 1 | `sprintAcceleration` × k × msc |
| h < msc × `lowSpeed` 且 `lowAcceleration` ≥ 0 | `lowAcceleration` × k × msc |
| 其他 | `acceleration` × k × msc |

- k = 玩家偏移 0x1e00 的倍率（[native-inf]，平时应为 1）。
- `speed`、`sprintspeed` 按姿态取值（站、蹲等各一行），其余键是通用的。
- **冲刺加速不检查"是否在冲刺"**，只看速度是否超过 msc × speed − 1。

### 2.3 摩擦 `Friction`（0x140a4a280）[native]

N1 起的名字是"滑铲速度衰减"，读完才知道它是整个地面摩擦。

1. 把速度分成平行于地面的部分 u 和法线部分。
2. **保护意图方向的速度**：u 在 wishdir 上的投影里，不超过 wishspeed 的那部分被单独拿出来，不参与摩擦。所以按住方向键时，摩擦只减掉偏离意图方向的那部分速度。
3. 剩余部分的大小 s：
   - s′ = max(0, s − D × ft)，D 由 `Ground_GetDecel` 给出（见 2.4），ft 是全局 frametime；
   - **滑铲中**再乘 `slideVelocityDecay` ^ ((1 − 0.75·x) × ft)。x 来自一个查询函数（0x140abdc20），平地上推测为 0，[native-inf]。
4. 速度 = 保护部分 + 剩余部分 × (s′ / s)。

### 2.4 减速度选择 `Ground_GetDecel`（0x140a36580）[native]

| 条件（按顺序） | 减速度 D |
|---|---|
| 滑铲中，且某个标志（0x1dfc）为真 | 0 |
| 滑铲中，按住下蹲（或另一标志 0x1dfd），且速度朝着某个参考方向（[native-inf]：滑铲方向） | `slideDecel` |
| 滑铲中，其他情况（松开下蹲，或速度反向） | `slideWantToStopDecel` |
| 不在滑铲，h > msc × `speed` | `sprintDeceleration`（< 0 时用 `sprintAcceleration`） |
| 其他 | `deceleration`；< 0 时用 `acceleration` × 0.6 |

然后 D 还要乘：
- 一个淡入系数：在某个时间点 T（玩家偏移 0x2a50）之前的 0.5 s 里从 0 线性升到 1，更早时为 0（[native-inf]：T 的含义未知）；
- 三个玩家倍率（0x1e00、0x4060、0x2af8，平时应为 1）。

**D 不乘 msc**。

### 2.5 `Accelerate`（0x140a4a0d0）[native]

Source 的写法，多一条上限：
- addspeed = wishspeed − v·wishdir；≤ 0 时不加；
- accelspeed = min(addspeed, a × ft × k′)（k′ = 玩家偏移 0x4060）；
- v += accelspeed × wishdir；
- **加完之后，|v| 不超过 max(加速前的 |v|, wishspeed)**。

## 3. `sv_friction` 和其他 Source 遗留 ConVar

| ConVar | 读取位置 | 结论 |
|---|---|---|
| `sv_friction` | `NoclipMove` 0x140a507c0、`SpectatorMove` 0x140a50400 | 只用于穿墙飞行和观战，**不在普通地面路径上** [native] |
| `sv_maxspeed` | `NoclipMove` | 同上 |
| `sv_stopspeed`、`sv_airaccelerate` | 无 | 没有任何代码读 |

## 4. SDK 钩子

地面路径上 `FullWalkMove` 被 SDK 包了一层（`SDK:game/client/move_sim_trace.cpp`），前后各挂几个函数。默认情况：

| 钩子 | 开关（默认） | 我们的测试里是否起作用 |
|---|---|---|
| MOVE-TRACE 记录 | `move_sim_trace` | 只记录，不改状态 |
| 自动连跳 | `sv_autobunnyhopping` = 0 | 否 |
| 斜坡弹射 | `sv_slope_launch` = 0 | 否 |
| 墙面攀爬 tap | `bridge_wallclimb_tap` = 0 | 否 |
| Sparrow 墙面弹射 | `bridge_wall_launch` = 1，但要脚本开启 | 否（不是 Sparrow） |
| Source trigger_push | `sv_source_push_boost` = 1，只在地图有 push 区域时 | 否 |
| portal 预测 | 只在穿过传送门时 | 否 |

结论：**M2 的地面实测反映的是原生代码**，没有被 SDK 改写。

## 5. 和实测、Unity 对照（初表，N3 正式录入）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| G-01 | 加速乘 msc，减速不乘 | §2.2、§2.4 | M2：三个加速度正好是 census × 1.1499，减速 × 1.0000 | **一致** |
| G-02 | 低速段边界 | h < msc × `lowSpeed` = 138 | M2：边界在 (136.38, 138.47] | **一致** |
| G-03 | 中速 → 冲刺加速的边界 | **固定在 msc × speed − 1 = 198.525**，不检查冲刺状态 | M2 选了"s0 + a冲刺·dt ≥ speed·msc"这条规则，同时注明"(197.97, 198.72] 里任意固定边界也能拟合" | **结构差**：代码是更简单的固定边界，且在 M2 给的区间里。Unity 可以改用固定边界 |
| G-04 | 加速度按"加速前的速度"选段 | §2.2 在加速前计算 | M2："按加速前速度选段，一步可能越过边界" | **一致** |
| G-05 | 蹲姿减速 1500、蹲速 80 | `speed` 按姿态取值；`deceleration` 也从一个可能按姿态区分的设置块读（[native-inf]） | M2 拟合 1500 / 80，census 只读了站姿 | **待确认**：N4 用 census 读蹲姿那一行 |
| G-06 | 停止吸附（小于约 1 u/s 归零） | `Friction` 里**没有**吸附，只有 max(0, …)；`NoclipMove` 里有"< 1 归零" | M2：吸附阈值在 (0.58, 1.58] 之间，假设为 1 | **未定**：吸附在别处（`CheckVelocity` 或 `CategorizePosition`），继续找 |
| G-07 | 按住方向键时的摩擦 | 意图方向上不超过 wishspeed 的速度不受摩擦（§2.3） | M2 有 keepfwd / noinput 两组实测 | **待核**：用 M2 的 e2 数据检查有输入时减速是否只作用在偏离部分。N3 补充：Unity 回放电机每条命令直接设 v = s·wishdir，转向是瞬间的。鼠标慢转时两者几乎一样（偏离部分每条命令都被减速清掉），**按键急转时会明显不同**，账本列为高影响 |
| G-08 | 输入曲线 m(2 − m) | 0.5 → 0.75 | M2 / M1：第一条命令的轴向值是 0.5 | **新发现**：第一条命令的实际输入是 0.75。要核对 M2 起步第一条命令的加速量，和 Unity 的输入层（M10-D2）对照 |
| G-09 | 冲刺时输入 × 1.25 | 冲刺标志为真时 (f, s) × 1.25，再进曲线 | M4b：冲刺使按键转向 × 0.67 | **待核**：可能和斜向输入、转向有关 |
| G-10 | 滑铲衰减律 | s′ = max(0, s − `slideDecel`·ft) × `slideVelocityDecay`^((1 − 0.75x)·ft)，census 100 / 0.7 | M2 在两种顺序里选了"先减速再衰减"：(v − 100·dt)·0.7^dt | **一致**（含顺序）。x 的含义待 N2-S |
| G-11 | 松开下蹲后滑铲减速变强 | 改用 `slideWantToStopDecel` = 400 | M10：松蹲后减速变强，到约 335 结束 | **一致**（定性）。结束条件留给 N2-S（`slideMaxStopSpeed` 350？） |
| G-12 | 滑铲中只能转向 | 意图沿速度方向的分量被去掉 | 无专门实测 | **只有代码**。Unity 要核对 |
| G-13 | `sv_friction` 是否参与地面减速 | 不参与（§3） | M2：地面减速用 `deceleration` | **一致** |
| G-14 | 加速后的速度上限 | max(原速度, wishspeed) | 无 | **只有代码**：解释了为什么在地面上加速不会把超速状态"拉回"或"推高" |
| G-15 | 减速的 0.5 s 淡入 | 时间点 T 前 0.5 s 内从 0 升到 1 | 无 | **只有代码**：T 是什么还不知道（可能和落地减速有关），N2-J 查 |

## 6. 还没读的

- `WalkMove` 里墙跑、攀爬的分支，以及 `WalkMove` 调用的 7 个小函数里的大部分（`n1` 地图里列着）。
- 吸附阈值的位置（G-06）。
- `Friction` 里 x 的来源（0x140abdc20）。
- 结构体偏移 0x1e00、0x4060、0x2af8、0x2a50、0x1dfc、0x1dfd 的含义。可以用 SDK 的 netvar 表或运行时读取确认。
