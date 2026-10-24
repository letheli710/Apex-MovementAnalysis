# N8-C：原生相位状态到底改了什么

日期 2026-10-24。二进制 `r5apex_dx12.exe`（S21）。方法：
- 先用 Ghidra 找到脚本绑定名字符串的引用，找到绑定函数（`n8/StringUse.java`、`n8/DumpIns.java`）；
- 再列出所有读写相位字段的指令（`n2/FindOffsetRefs.java`）；
- 反编译只放在 `local/n8/`，这里只写地址和重新表述的规则。

标记：**[native]** 读代码确认；**[native-inf]** 读到了分支，但被跳过的东西是什么是推断出来的。

## 1. 结论

**相位本身只是实体上的一个"时间窗口"，`PhaseShiftBegin` 不做任何别的事。** 移动代码在十几处检查"现在在不在窗口里"，在窗口里时就**跳过和其他东西的互动**：跳板和其他发射区、玩家之间的推挤、和玩家碰撞组的碰撞、被子弹 / 智能锁定选中。

**和世界几何的碰撞、走路 / 空中的加速和摩擦都不变。** 所以 Wraith 战术在虚空里还是会撞墙。虚空里变快，是脚本另外加的 `speed_boost` 状态效果，不是相位本身。

## 2. 绑定函数（脚本 → 原生）

注册表在 `0x14084fc00`（实体脚本方法），每个方法一条：名字 + 参数个数 + 原生函数指针。

| 脚本方法 | 原生函数 | 做什么 [native] |
|---|---|---|
| `PhaseShiftBegin(warmup, duration, type)` | `0x1408ac780` | 只写三个字段：类型 → `+0x19dc`；开始时间 = 当前时间 + warmup → `+0x19e0`；结束时间 = 开始时间 + duration → `+0x19e4` |
| `PhaseShiftCancel()` | `0x1408ac640` | 把类型和结束时间清零（窗口立刻关闭） |
| `GetPhaseShiftType()` | `0x1408ac840` | 返回 `+0x19dc` |
| `IsPhaseShiftedOrPending()` | `0x1408ac8e0` | `+0x690` 标志没设 **并且** 当前时间 ≤ 结束时间（warmup 期间也算） |
| `EnablePhaseShiftFlags()` / `DisablePhaseShiftFlags()` | `0x1408ac710` / `0x1408ac6a0` | 设置 / 清除实体标志字 `+0x3e0` 的 0x40000 位 |

引擎回调 `CodeCallback_EnterPhaseShift` / `CodeCallback_ExitPhaseShift`：在原生回调表里（名字字符串的引用在 `0x141986d30` / `0x141986d50`），参数是实体。

"**在相位中**"的判断在各处都内联成同一个条件：`+0x690` 标志没设 **并且** 开始时间 ≤ 当前时间 ≤ 结束时间。

## 3. 谁读这个窗口

`+0x19e0` / `+0x19e4` 一共有约 60 个函数读（`local/n8/off-19e0.tsv`、`off-19e4.tsv`）。下表是移动、碰撞和触发器相关的那些：

| 函数 | 已知名字 | 在相位中时 | 标记 |
|---|---|---|---|
| `0x140a38a90` | `JumpPadLaunch` | 函数一开头就返回：**跳板（Octane 跳板）不发射** | [native] |
| `0x140a37390` | 移动触发区分发（按区域类型：1 跳板、4、8、0x20 重力炮） | 类型 8 的处理只在**不在**相位时调用；类型 4 的处理 `0x140a39420` 在相位中一开头就返回 | [native]；类型 4 / 8 是什么区域 [native-inf]，未识别 |
| `0x140a3a620` | 类型 8 的处理 | 相位中一开头就返回 | [native] |
| `0x140a32df0`、`0x140a33110` | 玩家之间的推挤（遍历附近实体，要求 realm 掩码相交、对方有推挤半径 `+0x3b90`） | **相位中的对方不算**：不推人，也不被推 | [native-inf] |
| `0x140a4a7c0` | `WalkMove` | 两处"把重叠的玩家推开"的速度项（推力 20 或 100 × 帧时间），只在**不在**相位时加 | [native-inf] |
| `0x140a4c810` | `FullWalkMove` | 一段遍历实体列表、可能清掉地面实体的检查，只在**不在**相位时做 | [native-inf] |
| `0x140a48f90` | `AirMove` | Skyward 部署（`CodeCallback_PlayerSkywardDeployBegin`，Valkyrie / 跳塔的升空）检查，在相位中被挡住 | [native] |
| `0x140a39b80` | 移动触发区之后的一个方向推力 | 只在**不在**相位时做 | [native-inf] |
| `0x140b07e20` | 玩家的 ShouldCollide（碰撞组 + 内容掩码） | 在相位中时，对**碰撞组 0x10** 返回"不碰撞"；其他组照常 | [native]；0x10 是玩家 / 角色组 [native-inf] |
| `0x140855530` | 一个按实体遍历的射线 / 可见性检查（带 `r_visualizetraces`） | 相位中的实体被跳过 | [native-inf] |
| `0x140af00b0` | 智能弹药锁定（`smartAmmoLockType`） | 相位中的目标不能被锁定 | [native-inf] |
| `0x1409fbac0` | 触发器接触过滤（`trigger_ignore_nonsolids`） | 相位中走另一条分支（和 `+0x3e0` 标志一起决定能不能碰触发器） | [native-inf] |
| `0x1407980d0` | 客户端触发器接触缓存（`always_touch_triggers_cl`） | 相位剩余时间跨过 0.025 s 时重新计算接触 | [native] |
| `0x14070d3f0` | 给速度的函数（带 `sv_maxvelocity` 限制） | 来源实体在相位中时跳过 | [native-inf] |
| `0x140afd380` | 玩家重置 | 清零类型和结束时间 | [native] |

**没有读这个窗口的**（和 N1 的函数名表对过）：`Friction`、`Accelerate`、`AirAccelerate`、`Duck`、`PlayerMove`。走路、下蹲和空中加速在相位里**不变**。`TryPlayerMove` 和重力在我们的名字表里没有，所以没有逐个核对；但世界碰撞只经过上面的 ShouldCollide 过滤，而它只对碰撞组 0x10 有分支。

## 4. 回答 N8-A 留下的问题

- **相位为什么不能穿墙**：碰撞过滤只对碰撞组 0x10 关掉碰撞，世界几何不在这个组里。[native]
- **虚空里为什么变快**：原生相位不改速度。加速来自脚本（`sh_phase_shift.gnut`）按类型加的 `speed_boost` 状态效果；Alter 战术（`DOOR`）不加，所以 Alter 传送后不加速。
- **相位里不能用跳板**：`JumpPadLaunch` 在相位中直接返回。Octane 跳板 + Wraith 战术不能组合。[native]
- **warmup**：`IsPhaseShiftedOrPending` 在 warmup 期间就返回真；移动代码的内联检查要求"开始时间 ≤ 当前时间"，所以**移动上的效果从 warmup 结束才开始**。[native]
- **类型对原生代码没有影响**：类型只被存下来给脚本读（`GetPhaseShiftType`），移动代码只看时间窗口。五个技能在原生层是**同一个状态**。[native]

## 5. 对 Unity 的意义（建议，不自动改）

Unity 的 M10-W Wraith 实现，可以按原生的样子把相位做成"时间窗口 + 互动开关"：
- 相位中：跳板不触发、不和其他玩家碰撞 / 推挤、不能被锁定；
- 世界碰撞和移动规则不变；
- 加速由技能单独给。

这一条要先和 M10-W 现有实现对照，由用户决定（N8-E）。

## 6. 待做

- 类型 4 / 8 的移动触发区是什么（候选：升空气流、Horizon 升降梯）。
- `+0x690` 标志是什么（为真时相位无效）。
- 碰撞组 0x10 的名字：从 `ShouldCollide` 的调用者或碰撞组表确认。
- 实测（N8-D）：Wraith 战术中踩 Octane 跳板，应该不发射。
