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

## 7. 补充：外力类（"后放的事"第一项，2026-10-23）

| 机制 | 读到的 [native] | 没读通 |
|---|---|---|
| **重力炮** `GravityCannon_Launch` 0x140a3af30 | 过了触发器的启用时间，并且过了玩家的重复发射冷却（玩家 0x350）时：速度**直接替换**为触发器方向 × 触发器速度，清掉地面实体 | 空中控制锁由 SDK `trigger_cannon.cpp` 加在 `AirMove` 上 |
| **跳板和重力炮共用的冷却** | 跳板发射时把玩家 0x350 设为"现在 + 1 s"，重力炮检查同一个字段 | — 和 SDK 一致性代码里的 1.0 s 吻合 |
| **Vantage JetDrive** `BeginJetDrive_impl` 0x140b0d960 | 脚本接口 `BeginJetDrive(speed, accel, targetPos, targetEnt, targetEntOffset, timeOut)` 只把参数存进玩家结构，**开始时间 = 现在 + 0.2 s** | 每帧推进的函数（读这些字段的地方）还没找到 |
| **Valkyrie 喷气** `Jetpack_Thrust` 0x140aff150、`Jetpack_Vertical` 0x140afee50 | 推力分竖直（`jetpackThrust` × g）、水平移动（`jetpackHorizontalMoveThrust`）、加力（`jetpackAfterburnerThrust`）；启动时推力 × `ThrustScaleOnActivation`，在 `ThrustScaleTimeOnActivation` 内线性回到 1；上、下、侧、前后四个"紧度"是**半衰期**（代码用 −ln 2 / 紧度），速度按一阶指数逼近目标；结束后 `jetpackPostEffectTime` 内重力 × `jetpackPostEffectGravity` | 目标速度的完整公式；和 M4 VALK 实测的逐项对照 |
| **Horizon 升降梯** | 原生里只是一个触发器类型位 `TT_GRAVITY_LIFT` = 4（0x140b3bb40 注册） | 处理这个类型的移动代码没找到；本地 dedi 用的是 SDK 重写的 `trigger_gravity.cpp`。M4 已有实测模型。**N9 找到了**：`0x140a39420`（分发 `0x140a37390` 的类型 4），常量和 SDK 相同，见 `n9/N9-NATIVE.md` §2 |

Valkyrie census 值：推力 1.9、启动倍率 1.8 / 0.5 s、紧度 上 0.27 / 下 0.1 / 侧 0.11 / 前后 0.14 s、结束后 3 s 内重力 × 0.45、阻力 0.000125。

SDK 钩子补充：`Glide_Check` 0x140afe7b0、`Glide_Apply` 0x140afff90 在喷气代码区间里（`SDK:game/client/glide_flight.cpp`）。

## 8. 钩爪 P-08 ~ P-10（"后放的事"，第一轮没读通）

**N6 已查清**（`../n6/N6-MEASURE.md` §1）：P-08 = 接近规则（阈值随速度变大）+ 视线 90° 规则；P-10 = 0x14066f600 里的视线 90° 规则（S21 客户端有，S3 dedi 没有）；P-09 的上抬最多加到 200。

判断条件分散在 `Grapple_DetachRules`、`Grapple_DetachSpeedLoss` 和钩爪的大函数里，第一轮只确认了参数（§1.3）。建议改用实验确定：
- P-08：记录"越过锚点"那条命令的径向速度、和锚点的距离、视角，看是速度阈值（500）还是几何判断；
- P-09：比较各种脱钩方式脱钩前后的竖直速度，看什么时候加了 200；
- P-10：在 S21 客户端预测里找"视线离开"脱钩（客户端会、dedi 不会，M10 [hyb]）。
