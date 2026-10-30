# D-1 / D-2：蹬墙系数 f 和参考高度 player+0x2078

日期：2026-10-29。范围：只做 R5 静态研究（`r5apex_dx12.exe` 的 Ghidra 工程，headless `-noanalysis -readOnly`），没有开游戏，也没改 Unity 和 R5 研究仓库。反编译、反汇编原文在 `TF2-Research/local/d1d2/`（不进版本库）。

## 结论

- **D-1：f 是"强度 × 高度门"，实际只取 0 或 1。** 之前的推断"上次着地后起跳过（含墙跳）→ f = 1"**基本正确**。但真正的机制是一个"禁用"标志：**着地时置 1，地面起跳或墙跳时清 0**。另外还有一道高度门：离参考高度 ≥ 175 时 f = 0，而且每帧都会重新判断。
- **D-2：player+0x2078 是"这次腾空的参考地面高度"。** 站在地面上时它跟着脚底高度走；腾空后不再抬高，只在往下掉时跟着降低。跳板 / 重力炮发射时，它直接写成弹道最高点。攀墙时会被扣掉 `wallclimb_vertical_gain_reduction`。
- player+0x207c：开着喷射包（`jetpackEnabled`）、并且最近 0.5 s 内用过喷射包时置 1，置 1 后关掉高度上限。
- player+0x2ad0：**本次跑墙起跑时的高度**（起跑那帧的 z 坐标），作为攀墙最终跳的高度上限之一。

置信度：f 的公式、各写入点**高**，都是直接从反汇编读出来的。0x2078 的含义**中高**：写入点已全部找到，但个别调用者（0x140a3b310、0x140a39b80 的触发场景）没有逐一确认。

## 1. D-1：系数 f（0x140a4fed0）

Ghidra 的反编译把这个函数显示成 `void`，并且漏掉了返回值；上面那个推断也是从这份错误的反编译来的。这里改读反汇编（`local/d1d2/dis.txt`）。**0x1407936f0 不是计算 f 的函数**：它是更新实体绝对坐标的通用函数（检查 dirty 位 `+0x88 & 0x800`，然后重算 +0x17c..0x184 的 origin），调用它只是为了读取最新的 z（+0x184）。

逐条写成伪代码：

```
float WallRun_Strength(player):
  if player.disable(+0x2ad8) != 0:            return 0
  c = setfile.verticalGainCutoff_wallrun        // R5 = 175
  if c >= 0:
      h = player.z(+0x184) - player.refZ(+0x2078)
      if h >= c:                                 return 0   // 高度门
  n = (float) player.wallrunCount(+0x2ad4)
  A = wallrun_strengthLossStart                  // ConVar，R5 默认 "1000"
  B = wallrun_strengthLossEnd                    // ConVar，R5 默认 "1000"
  if n <= A:                                     return 1.0
  if n >= B:                                     return 0
  return (n - A) / (B - A)
```

- 两个 ConVar 的名字：初始化函数 0x1401a6a20 / 0x1401a6bf0 把 "wallrun_strengthLossStart" / "wallrun_strengthLossEnd" 写进 0x1427cae40 / 0x1427cb700 指向的对象；默认字符串都在 0x14164bb24，内容是 "1000"。TF2 里这两个 ConVar 同名，默认值也都是 1000。TF2 对它们的说明是："Number of wall runs allowed before starting to lose upward strength (scales upWallBoost, jumpUpSpeed, and gravityRampUpTime)"。
- **次数衰减实际不起作用**：两个默认值都是 1000，连跑 1000 次以内 f 都是 1。按反汇编，中间段的公式是 (n−A)/(B−A)，是递增的，跟说明里的"逐渐失去"方向相反；不过默认值下走不到这一段，所以不影响结果，B 版可以直接忽略。
- 所以实际上 **f = (disable == 0) 且 (c < 0 或 z − refZ < 175)**，结果只会是 0 或 1。

### 1.1 用到 f 的地方

| 地址 | 用法 |
|---|---|
| `WallRun_Begin` 0x140a4f120 | 先 `++wallrunCount`（0x140a4f5ba），再调用 f（0x140a4f5f3），然后用它乘起跑提速（`upWallBoost` 250） |
| 0x140a34560（重力系数） | 每帧调用：t < `wallrunGravityRampUpTime` 时，重力 = (1 − f·(1 − t/T)) × 基础系数；`wallstickEnabled` 时 T 取 100 |
| `JumpOutOfWallRun` 0x140a50050 | 先把 disable 清 0，再调用 f，乘墙跳的 `wallrunJumpUpSpeed` |

重力系数**每帧**都会重新算 f，所以跑到参考高度 + 175 时，f 当帧就变成 0、重力恢复满值，人不再往上爬。这条就是跑墙的"爬升上限"。

### 1.2 disable 标志 +0x2ad8 的全部写入点

| 地址 | 函数 | 写入值 | 意思 |
|---|---|---|---|
| 0x140b09478 | `Player_TouchGround` 0x140b09440 | 1 | **着地**（0x140b04b30 返回 0 时，推测是"不在跑墙 / 挂墙状态"） |
| 0x140a3c826 | `Jump` 0x140a3b550 地面起跳分支 | 0 | **地面起跳**，同时把 `wallrunCount` 清 0 |
| 0x140a50342 | `JumpOutOfWallRun` | 0 | **墙跳**（在计算墙跳上升速度前清掉） |
| 0x140a4f962 | `WallRun_Begin` | 1 | 新墙法线与之前记录的墙法线（+0x1f34 列表）点积 > `wallrun_sameWallDot` 时，判定为同一面墙。注意：写入发生在起跑提速**之后**，所以只影响这次跑墙的重力爬升 |
| 0x140a4e093 | `WallClimb_Move` | 1 | 进入攀墙最终跳之后 |
| 0x1404581ec | 0x140458050 | 0（qword 写入，同时清 +0x2ad4..+0x2adb） | 初始化 / 重置（推测是出生时） |
| 0x140b809ab | 0x140b80830 | word 拷贝 | 推测是网络同步或预测状态拷贝，没细读 |

`wallrunCount` +0x2ad4 只有三个写入点：`WallRun_Begin` 里加 1，地面起跳时清 0，初始化时清 0。**墙跳不会清它**。

### 1.3 和 TF2 实测（T5 §5.1）对照

| 情况 | 预测 | T5 实测 |
|---|---|---|
| 地面起跳后贴墙 | disable = 0、count = 1 → f = 1 | 有提速、有爬升 ✓ |
| 墙跳后贴另一面墙 | 墙跳清了 disable；count = 2 ≤ 1000 → f = 1 | 有 ✓ |
| 传送到空中贴墙 | 传送前站在地面，disable = 1 → f = 0；如果传送得很高，高度门也会让 f = 0 | 两者都没有 ✓ |
| 从边缘走下去再贴墙（没跳） | disable 是着地时置的 1 → **f = 0** | 未测 |
| 同一面墙再贴 | 起跑提速照算，但 Begin 随后把 disable 置 1 → 本次没有重力爬升 | T5 有"同墙再贴"记录，没对照这一项 |
| 跳起后在高于起跳点 175 以上的地方贴墙 | 高度门 → f = 0 | 未测 |

结论：B 版的规则可以写成"**f = 1，当且仅当上次着地后做过地面起跳或墙跳，且当前高度 < 参考高度 + 175**"。另外，同墙再贴时这一次不给爬升。

## 2. D-2：参考高度 player+0x2078

`FindOffsetRefs 0x2078` 一共找到 36 处引用，去掉栈变量和其他类型的对象后，玩家相关的写入点如下：

| 地址 | 函数 | 写入 | 条件 / 意思 |
|---|---|---|---|
| 0x140b12888 / 0x140b1295d | 0x140b12850（每帧后处理，被 0x1407e54e0、0x140b12970 调用） | z | 当 +0x1d3c ≠ 1 时：如果 z < refZ，就跟着降低；或者站在地面实体上、地面法线 z ≥ 0.7、不在跑墙状态（+0x2bb9 = 0，0x140b04b30 = 0）时，令 refZ = z。也就是站立时跟着脚底高度走，腾空后不再抬高，只在下落时跟着降低 |
| 0x140a3931a | `JumpPadLaunch` 0x140a38a90 | z + v²/(2g) | **弹道最高点**；同时 +0x1d3c = 1，这样每帧那条规则就不会把它改回去 |
| 0x140a3b2e9 | `ApplyGravityCannonLaunch` 0x140a3af30 | z + v²/(2g) | 同上，重力炮的情况 |
| 0x140a39bd7 | 0x140a39b80（和上面两个都由 0x140a37390 调用） | z | +0x2bba == 1 时，推测是发射结束或被打断 |
| 0x140a3b505 | 0x140a3b310（由 `FullWalkMove` 调用） | z | 一种由 +0x2cb8 / +0x2cb9 触发的推送，同时 +0x1d3c = 2；没确认具体是哪种机制 |
| 0x140a4f4cc | `WallRun_Begin` | z | 当 +0x1d3c == 2 时，起跑时把 refZ 改成当前高度，并把 +0x1d3c 清 0 |
| 0x140b0db80 | 0x140b0da50 | z | 初始化 / 重置 |
| 0x140b0e015 | 0x140b0dea0（抓钩动画选择，有多个调用者） | z | 条件分支里写入，同时 +0x1d3c = 0 |
| 0x140a4e192 | `WallClimb_Move` | refZ − `wallclimb_vertical_gain_reduction` | 攀墙最终跳 |
| 0x140a5018c | `JumpOutOfWallRun` | refZ − `wallclimb_vertical_gain_reduction` | 从攀墙状态跳出时 |

读取点：f 的高度门（0x140a4fed0）；`TryStart` 的起跑高度门（0x140a4e44a）；0x140a4d470 的攀墙上限；`WallClimb_Move`；`Jump` 0x140a3c0a0 里的 setfile 0x141ac1c08（≥ 0 时用 refZ + 它 − z 限制起跳速度，没细读）。

**含义：refZ 是"最后一次稳定站立时的地面高度"；从跳板 / 重力炮发射时，改成发射弹道的最高点。** 普通地面起跳时它就等于起跳点高度，这和之前的推测一致。但它不是在起跳那一刻写入的，而是站在地面上时每帧更新。走下边缘往下掉时，它会一路跟着降低。

### 2.1 相关的两个字段

- **+0x207c**（`WallRun_Begin` 0x140a4faa4 / 0x140a4faad）：setfile `jetpackEnabled` 打开、并且 当前时间 − player+0x1dd4 ≤ 0.5 s 时为 1，否则为 0。这里推测 +0x1dd4 是最近一次用喷射包的时间。值为 1 时，0x140a4d470 和 `WallClimb_Move` 不再用 refZ 限制高度。普通 R5 角色不会触发，B 版可以不实现。
- **+0x2ad0**：`WallRun_Begin` 把 mv+0x118..0x120（也就是本帧 origin）拷进 +0x2ac8..+0x2ad0，所以 +0x2ad0 是**起跑高度 z**。0x140a4d470 返回 min(起跑高度, refZ + 175 − `climbFinalJumpUpHeight` − `climbHeight`)；`WallClimb_Move` 在这个值上加 `climbHeight` 和 `climbFinalJumpUpHeight`，作为最终跳的目标高度。结果是攀墙最终跳的目标不高于"起跑高度 + 128"，也不高于"refZ + 175"。

## 3. 对 B 版（P-01 / P-02）的影响

1. f 用两个状态就够了：`boostArmed`（着地 → false；地面起跳、墙跳 → true）和 `refZ`（站立时跟着脚底，腾空只降不升，跳板时写成最高点）。f = boostArmed && (z − refZ < 175)，**每帧都重新算**。
2. 同一面墙再贴时：起跑提速照给，但这次跑墙的爬升关掉。
3. `wallrun_strengthLoss*` 不用实现（默认 1000）。

## 4. 仍未解 / 需要 TF2 实测

不开游戏这里无法确认，留给 TF2 会话：

- **掉落起跑**：从边缘走下去（不跳），再贴墙。预测：没有提速，也没有爬升。
- **高度门**：跳起后贴一面顶端比起跳点高很多的墙，看爬升是否在高出起跳点约 175 处停住。TF2 有自己的 `verticalGainCutoff_wallrun`，测前先查 TF2 setfile 里的值。
- **同墙再贴的爬升**：同一面墙墙跳后再贴，看起跑提速是否还在、爬升是否没了。
- 静态方面还没确认：0x140b04b30 具体是什么（推测是"跑墙或挂墙中"）；0x140a3b310 的推送是什么机制；0x140a39b80 的 +0x2bba 标志；`Jump` 里 setfile 0x141ac1c08 的名字和作用。这几项都不影响上面的 f 规则。
