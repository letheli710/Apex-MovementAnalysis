# N2-P2 钩爪、滑索、跳板

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。

这三个子系统已经有比较充分的实测（M4、M4b、M9、M10），HSD 里也有对应实现。这一轮主要确认：实测拟合出来的规则在代码里是什么形状，有没有漏掉的规则。

## 1. 钩爪（P）

### 1.1 位置

钩爪的核心代码不在 `CGameMovement` 区间里，而是在 0x14066xxxx–0x140676xxx 一带（N1 地图之外），另外有几个函数在 `gamemovement` 区间里：

| 函数 | 内容 |
|---|---|
| `Grapple_SpeedRamp` 0x1406752b0 | 拉力目标速度的时间斜坡 |
| `Grapple_PullAccel` 0x1406755c0 | 每条命令的速度更新 |
| `Grapple_DetachRules` 0x14066f600 | 脱钩判定 |
| `Grapple_DetachSpeedLoss` 0x14066fb60 | 脱钩时的速度处理、撞击上抬 |
| `Grapple_DetachLength` 0x140a3ce80 | 读脱钩的长度和低速阈值 |
| `Gravity_HalfStep` 0x140a36130 | 脱钩后的重力（`grapple_detachGravity*`） |
| `AirMove` 0x140a48f90 | 钩爪中的空中加速（`grapple_airAccel`、`grapple_airSpeedMax`） |

### 1.2 拉力 [native]

S21 Pathfinder 的 `grapple_swing` = false，所以走非摆荡分支。

1. **目标速度** = (1 − x) × k × lerp(`grapple_speedRampMin`, `grapple_speedRampMax`, clamp(t / `grapple_speedRampTime`, 0, 1))：
   - census：50 → 800，1.5 s；
   - t 从挂上（或某个更晚的事件）开始算；
   - x 是一个状态效果的强度（和 `Friction` 里的 x 用的是同一个查询函数，[native-inf]），平时为 0；
   - k 只在摆荡时不为 1。
2. 速度先换成**相对锚点**的速度（锚点会动时要减掉锚点的速度），再分解成沿绳分量 a 和切向分量 t。
3. **切向**：|t| −= `grapple_decel`（425）× dt，不低于 0。
4. **沿绳**：a < 目标时，a = min(a + `grapple_accel`（1500）× dt, 目标)。
5. 某些情况下，切向里朝着某个方向（[native-inf]：竖直向上）的分量单独保留，不参与第 3 步；`grapple_dontFightGravity` 处理竖直分量。

### 1.3 脱钩 [native]

| 规则 | 参数（census） |
|---|---|
| 接近锚点 | `grapple_detachLengthMin` / `Max` = 33 / 50 |
| 离开锚点的速度过大 | `grapple_detachAwaySpeed` = 500 |
| **低速超时**：速度 < `grapple_detachLowSpeedThreshold`（250）持续一段时间 | 空中 `detachLowSpeedTime` 1.5 s、地面 `GroundTime` 0.7 s、墙上 `WallTime` 1.2 s、近战 `MeleeTime` 1 s；摆荡阈值另算 |
| 脱钩时竖直上抬 | `grapple_detachVerticalBoost` 200，封顶 `detachVerticalMaxSpeed` 200 |
| 水平封顶 | `grapple_detachHorizontalMaxSpeed` 600 |
| 速度损失 | `grapple_detachSpeedLoss` 300、`detachSpeedLossMin` 460 |
| 撞击上抬 | `grapple_impactVerticalBoost` / `MaxSpeed` 300 / 300 |
| 脱钩后重力 | `grapple_detachGravityScale` 0.5，速度 ≤ `detachGravitySpeed` 200 时生效 |

## 2. 滑索（Z）[native]

| 规则 | 公式 | 参数 |
|---|---|---|
| 跳离 | 沿绳速度乘 `ziplineJumpOffDampScale` 衰减，大小 ≤ `ziplineJumpOffSpeed`；再加 √(2g·`jumpHeight`) 的竖直速度 | 289.8 = √(2·750·56) |
| 端点自动脱离 | 沿端点方向的速度夹在 [`ziplineSpeed`, `ziplineDetachSpeed`] | 600 / 600 |
| 竖直脱离速度上限 | `ziplineMaxVerticalDetachSpeed` | 1500 |
| 曲线滑索（ziprail） | 另一套 `minJumpOffSpeed` / `maxJumpOffSpeed`、`ziprailDetachSpeed`；`ziprail_duck_detach` 时按蹲用最小值 | |
| 加速 | `ziplineAcceleration`，目标 = 速度倍率 × `ziplineSpeed` | |

## 3. 跳板（F）[native]

`JumpPad_Launch`（0x140a38a90，SDK 名）：
- 跳板没有固定方向时：方向 = normalize(ĥ + V·ẑ)。ĥ 是玩家水平速度方向，V 是跳板的竖直参数（脚本 `JUMP_PAD_VERT_OVERRIDE` 2.0）；
- **下蹲中 V × `jumppad_vert_override_ducked_scalar`**；
- 速度 = 方向 × 跳板推力（1150，强化后 × 1.2）；
- 清掉地面实体，记下预测的顶点高度，打开跳板二段跳窗口（`superjump_jumppad_enable_time`）。

**跳板不走冲量队列**：代码里没看到写入 N2-T §5 的冲量事件，所以"跳板后有低减速窗口"的猜测（T-04）没有得到支持。

重力炮（`GravityCannon_Launch` 0x140a3af30）和升降梯（Horizon 战术）这一轮没读。

## 4. SDK 钩子

| 钩子 | 文件 | 我们的测试里 |
|---|---|---|
| `JumpPad_Launch` | `jumppad_predict.cpp` | 跳板发射状态的预测。**dedi 上的跳板是 SDK 的一致性代码**（`SDK:game/server/jumppad_parity.cpp`），客户端是原生加预测 |
| `GravityCannon_Launch`、`AirMove` | `trigger_cannon.cpp` | 只在重力炮触发时 |
| `Zipline_Use`、`Zipline_JumpOff` | `zipline_disconnect.cpp` | 跳离后重新抓取的次数计数 |
| `GrappleAnimSelectSequence` 等 | 多个 | 动画选择，不影响速度 |

## 5. 和实测、Unity 对照（初表）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| P-01 | 拉力速度斜坡 | lerp(50, 800, t/1.5) | M10：d\|v\|/dt 500.0–502.7 | **一致** |
| P-02 | 切向刹车 | \|t\| −= 425·dt | M10：切向刹车 = `grapple_decel` 425 | **一致** |
| P-03 | 没有摆荡 | `grapple_swing` = false → 非摆荡分支 | M10：没有钟摆 | **一致** |
| P-04 | 侧键 = 空中加速 | `AirMove` 读 `grapple_airAccel` 650、`grapple_airSpeedMax` 420 | M10：侧键是空中 strafe，650 > 425 | **一致** |
| P-05 | 接近脱钩 | 33 / 50 | M10：35–53 u，没有单一阈值，"和 33 / 50 吻合" | **一致** |
| P-06 | 按键脱钩夹到 460 | `detachSpeedLoss` 300、`Min` 460 | M10：580 → 458.7，675 → 458.5 | **一致**（M10 已对上这两个键） |
| P-07 | 低速超时脱钩 | < 250 持续 1.5 / 0.7 / 1.2 s | 没测 | **只有代码** |
| P-08 | 离开锚点速度 > 500 脱钩 | `detachAwaySpeed` 500 | M10："越过锚点后 1 条命令脱钩，径向 −28..−214 u/s" | **未定**：M10 测到的径向速度远小于 500，"越过锚点"可能是另一条规则（几何判断），要细读 |
| P-09 | 脱钩上抬 200 | 条件触发 | M10："四条脱钩规则都保持动量（除了按键夹紧）" | **未定**：要读清上抬的触发条件 |
| P-10 | 视线离开脱钩（S21 客户端） | 没找到具体位置 | M10：客户端会，S3 dedi 不会 [hyb] | **未定** |
| Z-01 | 跳离速度 | 衰减 + 封顶 + 289.8 竖直 | M9 / M10；HSD："沿绳 min(v, 400) + 289.828"，残差 0 | **一致**。`ziplineJumpOffSpeed` 应为 400，N4-A 补读 |
| Z-02 | 端点脱离 600 | clamp(v·d, 600, 600) | HSD [meas + src]，残差 0 | **一致** |
| F-01 | 跳板公式 | 1150 · normalize(ĥ + 2.0·ẑ) | M4：v = PUSH·normalize(ĥ + V·ẑ) | **一致** |
| F-02 | 下蹲跳板 | V × `jumppad_vert_override_ducked_scalar` | SDK 一致性代码 0.5；M4 下蹲跳板实测 | **一致**（默认值待 N4-A 读） |
| F-03 | 跳板后的低减速窗口 | 跳板不写冲量队列 | — | T-04 的猜测不成立；低减速窗口来自别的冲量事件 |

## 6. 还没读的

- P-08 ~ P-10 的细节；钩爪发射、挂上时的上抬（`grapple_attachVerticalBoost`）。
- 重力炮、Horizon 升降梯、Vantage JetDrive、Valkyrie 喷气（setfile `jetpack*` 一大组，函数在 0x140afe000–0x140b02000）。
