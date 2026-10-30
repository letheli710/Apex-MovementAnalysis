# T3 报告：蹬墙跑、挂墙、二段跳

日期：2026-10-28。静态分析：TF2 用 `server.dll` 反编译，R5 用已有地图加只读 ConVar 读数，Unity 读 HSD-Unity 源码（主 checkout 当前在 `rud/replay-unduck-native` 分支，只读）。

## 1. 结论

1. **TF2 原版规则已经完整读出**，见第 2 节。蹬墙跑不是独立的移动模式，而是地面移动的一个分支：墙被当成"地面"，摩擦、加速走同一套函数，只是参数换成蹬墙跑的那一组。重力在外层每帧施加，随时间从 0 爬升到满。
2. **R5 里蹬墙跑代码几乎全在。** 函数结构和 TF2 对得上：起跑判定、起跑、维持和脱落、墙跳、重力爬升、同墙限制。TF2 的 38 个 `wallrun_*` ConVar 里：
   - 32 个在 R5 中仍是 ConVar，默认值完全相同；
   - 1 个不同：`wallrun_maxViewTilt`（R5 10°，TF2 15°）；
   - 5 个在 R5 里不再是 ConVar，改成了 setfile 键。

   Apex 关掉蹬墙跑只是因为 setfile 里 `wallrun = false`。
3. **"Apex 版蹬墙跑"可以从 R5 setfile 的残留值推出来**：比 TF2 慢得多、短一点、爬得低，还多了 Apex 自己的几条限制（`verticalGainCutoff_wallrun`、`wallrunCeilingLimit`、`wallrunDuckCausesFallOff`、`wallrunDecelerate*`）。这些新键的规则 T3 只看到了名字，没读公式。
4. **M7（Unity）是另一套设计**，和两边都不同。最大的区别在重力模型、起跑时的竖直速度、水平速度上限和墙跳方向，见第 4 节。

**待你决定（计划第 5 节问题 1）**：HSD 的蹬墙跑以哪个版本为准。选项见第 5 节。

## 2. TF2 原版规则（MP 铁驭）

数值来自 `pilot_mp.set` + 代码默认值 + ConVar（MP 模式下 `spmp.cfg` 覆盖两项）。地址都是 `server.dll` 的。

### 2.1 起跑（`CanWallRun` 0x180174890，`WallRun_Begin` 0x1801835c0）

| 条件 | 规则 |
|---|---|
| 状态 | 在空中；不在滑索或梯子上；职业有 `wallrun 1`；`wallrun_enable 1` |
| 计时 | player+0x2588 的某个时间戳不到 0.5 s 时不能起跑（这个字段是什么还没确认；推测是离地或上次蹬墙的时间） |
| 墙面 | 法线 z 在 [-0.35, 0.7]（太平的地面和太斜的天花板都不行） |
| 方向 | 必须朝墙移动：`wallrun_minAngle_air` 180° 换算成半角 90°，远离墙的速度不行 |
| 距离 | 脚离墙 ≤ `wallrun_allowed_wall_dist` 13 u（挂墙用手部距离 18 u） |
| 同一面墙 | 和上一面墙法线点积 > `sameWallDot` 0.9 算同一面墙。`sameWallSlope` 是 0，所以只要高于上次接触点就不能再贴；低于上次接触点可以 |
| 速度 | 没有最低速度要求，也不要求按前进键（代码里没看到） |
| 起跑时竖直速度 | 沿墙面"向上"方向的速度提到至少 `wallrun_upWallBoost` 250 u/s；已经更快就不变 |
| 重试 | 撞墙失败后每 `wallrun_retry_interval` 0.07 s 再判一次 |
| 二段跳 | `superjump_limitreset_onwallrun 1`：起跑就恢复二段跳 |

### 2.2 维持（`WalkMove` 墙面分支 0x180185230，重力 0x180186c70）

| 项 | 规则 |
|---|---|
| 重力 | 系数 = t / `wallrun_gravityRampUpTime`（MP 0.7 s），从 0 线性升到 1；之后是满重力（750 × 0.8） |
| 摩擦 | 每帧 \|v\| × (1 − `wallrunFriction` 4 × dt)，作用在 3D 速度上 |
| 水平驱动 | 输入映射到墙面上；朝 `wallrunMaxSpeedHorizontal` 420 以 `wallrunAccelerateHorizontal` 1500 u/s² 加速（× msc）。输入和视角朝后（点积 ≤ −0.6）时上限改为 `…Backward` 50 |
| 竖直驱动 | 按前进时额外加"向上输入" = 前进量 × 沿墙分量 × `wallrun_upwardAutoPush` 0.65；朝 `wallrunMaxSpeedVertical` 225 以 360 u/s² 加速，滑落越多加速越弱 |
| 滑落 | 跑满 `wallrun_slipstarttime`（MP 1.5 s）后开始，经 `slipduration` 1.0 s 线性到 1；没有输入时至少 `noInputSlipFrac` 0.7。滑落时下坠的速度不受摩擦 |
| 视角侧倾 | 最大 15°，速度 6；提前 0.25 s 预测并开始倾斜（client.dll） |

`wallrun_slipvel`、`wallrun_slipslowdown`、`wallrun_hangslipvel` 三个 ConVar 在两个 DLL 里都**没有任何读取**，是废弃项。

### 2.3 脱落（0x180186d60）

| 触发 | 规则 |
|---|---|
| 时间到 | 在墙上 > `wallrun_timeLimit` 1.75 s（`pas_wall_runner` 被动 +2.5 s） |
| 推离墙 | 朝外推 > `pushAwayFallOffTime` 0.05 s |
| 墙没了 | 失去墙面时沿法线推出 `fallAwaySpeed` 70 u/s |
| 墙顶 | 头顶上方没墙且在上升时，vz 每秒减 3000·k，防止冲出墙顶 |
| 挂墙 | 挂满 `wallrun_hangTimeLimit` 4 s 脱落；3 s 后开始滑（`hangslipstarttime`），0.5 s 内减速到停（`hangStopTime`） |

### 2.4 墙跳（`JumpOutOfWallRun` 0x180173a00）

1. 水平：沿输入方向 `wallrunJumpInputDirSpeed` 80，再把离墙速度补到至少 `wallrunJumpOutwardSpeed` 205。视角和输入都朝墙时，这个 205 最多减 80%。
2. 竖直：`vz = min(230, vz + 1.5 × 230)`。也就是正常情况下 vz 设为 230；在快速下坠时（vz < −115）是 vz + 345。
3. 加在原速度上（原来的沿墙速度保留）。
4. 记下这面墙：0.2–0.4 s 内有"排斥"（`wallrun_repel*`），不能马上贴回去。

### 2.5 挂墙

ADS 键触发（需要 `pas_wallhang` 被动，`wallrunAdsType "wallhang"`），手离墙 ≤ 18 u。挂墙时速度在 0.5 s 内降到 0，3 s 后开始下滑，4 s 掉落。

### 2.6 二段跳（`Jump` 0x180172870 的 superjump 分支）

| 项 | 规则 |
|---|---|
| 次数 | `superjumpLimit` 1；落地、蹬墙跑起跑时恢复 |
| 高度 | 目标高度 H = 60。正在上升时，如果"现有上升高度 + 0.25H"已经超过 H，就只叠加 0.25H；否则 vz 清零后按 H 起跳，即 vz = √(2·750·60) = 300（起跳不乘 gravityScale） |
| 水平 | 有输入时：从现有水平速度里扣掉 180，再沿输入方向加 180（`superjumpHorzSpeed`）。快的时候等于把 180 u/s 转向输入方向；慢于 180 时整个换成输入方向 × 180 |

## 3. R5 里的残留（"Apex 版蹬墙跑"）

| 项 | TF2 MP | R5（S21 setfile / ConVar） | 说明 |
|---|---|---|---|
| 开关 | `wallrun 1` | `wallrun false`；playlist `survival_wallrun_enabled 0` | 关掉的方式只有这个 |
| 水平上限 / 加速 | 420 / 1500 | 225 / 200 | Apex 慢很多 |
| 竖直上限 / 加速 | 225 / 360 | 112 / 450 | |
| 时长 | 1.75 s | 2 s | |
| 起跑竖直提速 | 250（ConVar） | 250（setfile `wallrunUpWallBoost`） | 值相同，改为 setfile |
| 贴墙距离 | 13（ConVar） | 17（setfile） | |
| 墙跳 离墙 / 向上 / 输入方向 | 205 / 230 / 80 | 188 / 240 / 75 | |
| 视角侧倾 | 15° | 10° | ConVar |
| Apex 新增 | — | `verticalGainCutoff_wallrun` 175、`wallrunCeilingLimit` 0.5、`wallrunDuckCausesFallOff`、`wallrunDecelerateHorizontal/Vertical`、`wallclimb_vertical_gain_reduction` 128、起跑和超时的镜头 punch（`wallrun_viewpunch_onStart/onTimeout_*`） | 和 Apex 的攀墙（climb）共用一个函数 `WallClimb_Move`。新增键的规则还没读 |
| 其余 `wallrun_*` ConVar（32 个） | | 和 TF2 默认值相同 | 用 R5 Ghidra 工程只读读出，原始输出在 `local/t3-r5-convar-dump.txt`。另外 `player_extraairaccelleration` 2.0、`superjump_*`、`automantle_wallrun_maxangle_view` 45 也相同 |

R5 的 `wallrunGravityRampUpTime`、`wallrunSameWallHeight` 是 setfile 键，census 没读过，值未知。

## 4. 和 Unity M7 的逐项对照

M7 = `HSD-Unity/Assets/HSD/R5Replay/Runtime/Abilities/WallRun/WallRunAbility.cs`、`DoubleJump/DoubleJumpAbility.cs`，所有数值都标着 [design]。

| 项 | TF2 原版 | M7 | 差异 |
|---|---|---|---|
| 起跑输入 | 不需要按键，朝墙移动即可 | 必须按住前进 | M7 更严 |
| 起跑速度 | 无下限 | 沿墙 ≥ 200 u/s | M7 更严 |
| 起跑视角 | 无要求（只看移动方向） | 不在 35° 攀墙锥内，且和跑动方向差 ≤ 75° | M7 为了和攀墙分开 |
| 下坠中起跑 | 允许（法线 z、移动方向满足即可） | 下坠 > 450 u/s 不行 | |
| 起跑竖直速度 | 沿墙向上提到 ≥ 250 | vz 夹到 [60, 150] | **TF2 起跑时向上冲得多** |
| 重力 | 0 → 1 线性爬升 0.7 s，之后满重力 | 恒定 0.15 g | **最大的手感差别**：TF2 是先平后坠的弧线，M7 是几乎水平的线 |
| 按前进时向上 | 额外向上输入 0.65，竖直上限 225 | 无 | TF2 可以沿墙往上跑 |
| 水平上限 / 加速 | 420 / 1500（× msc） | 300 / 400（× msc） | TF2 快且几乎立刻到速 |
| 超速处理 | 摩擦 4/s 作用在 \|v\| 上（指数衰减） | 超过 300 时以 60 u/s² 线性下降 | |
| 时长 | 1.75 s，之后滑落 | 1.6 s 后结束 | 接近 |
| 滑落 | 1.5 s 开始，1 s 内到满 | 无（到时直接结束） | |
| 松开前进 | 没有专门规则（无输入时滑落至少 0.7） | 0.15 s 结束 | |
| 推离或转开 | 推离 0.05 s 脱落 | 视角背离 > 30° 或侧移键朝外：结束并推出 80 | |
| 墙跳 水平 | 输入方向 80 + 离墙 ≥ 205，加在原速度上（沿墙速度保留） | 沿墙保留 × 1.0 + 法线 280，水平上限 480 | M7 离墙更猛；TF2 没有上限 |
| 墙跳 竖直 | vz = min(230, vz + 345) | vz = 300 | |
| 同一面墙 | 高于上次接触点就不能再贴；0.2–0.4 s 排斥 | 落地前不能再贴（含共面） | M7 更严 |
| 视角侧倾 | 15°，提前 0.25 s | M5.5 相机自己的设计（不在本对照） | T6 再看 |
| 挂墙 | ADS + 被动，4 s | M7 是"抓边"（ledge hang），不是挂墙 | 不同机制 |
| 二段跳高度 | vz = 300（或已在上升时叠加 0.25H） | vz = max(vz, 259.8) | TF2 更高；TF2 会**替换**下坠速度，M7 也是 |
| 二段跳水平 | 180 u/s 转向输入 | 水平方向向输入转一半，速度大小不变 | 规则不同 |
| 二段跳恢复 | 落地、蹬墙起跑 | 落地、蹬墙起跑、抓边、滑索 | |
| 二段跳最早时机 | 没看到限制 | 离地 0.1 s 后 | |

## 5. 给用户的选项（问题 1：以哪个版本为准）

| 选项 | 内容 | 好处 | 代价 |
|---|---|---|---|
| A. TF2 原版 | 用第 2 节的规则和 MP 数值 | 有原版依据；手感是 Titanfall 玩家熟悉的 | 速度 420、起跑向上冲 250，比 Apex 的地面节奏快很多，和 R5 基准反差大 |
| B. TF2 规则 + R5 残留数值（"Apex 版"） | 第 2 节规则，换成第 3 节的 R5 值（225 / 200、112 / 450、2 s、墙跳 188 / 240 / 75，侧倾 10°） | 规则有原版依据，数值有 Apex 依据，和 R5 基准最协调 | Apex 新增的 5 个键的规则还没读，要补一步（R5 侧，读 `WallClimb_Move`） |
| C. 保留 M7，按 TF2 校正个别项 | 例如只换重力模型（0→1 爬升）和起跑竖直速度 | 改动最小 | 仍然是设计值，没有完整依据 |

我的建议是 **B**：它最符合计划第 0 节"R5 是基准，TF2 只用来补"的定位。A 可以作为开关里的另一套预设。

**用户决定（2026-10-28）：采用 B 作为基准，A 做成可开关的预设。** 因此第 6 节第 3、4 项（R5 新增键的公式、两个未知的 R5 setfile 值）变成 B 的前置工作，在 T6 提案之前补上。

## 6. 未解项

**T5 实测结果（2026-10-29）见 [../runtime/T5-REPORT.md](../runtime/T5-REPORT.md) 第 5 节。** 第 2 项已关闭；第 1 项排除了"离地时间"但仍未知；第 6 项全部核对，其中起跑提速更正为 vz + 250（最多到 250），并且只在跳起后贴墙时出现。

1. player+0x2588 那个 0.5 s 计时是什么（起跑条件）。T5 运行时确认。
2. 二段跳水平重定向的初值（`fVar29` 的初始值）是推断的。T5 实测。
3. R5 新增的 `verticalGainCutoff_wallrun`、`wallrunCeilingLimit`、`wallrunDuckCausesFallOff`、`wallrunDecelerate*` 的公式没读。选 B 时需要读，这是 R5 侧的工作。**已关闭（R-1，2026-10-29）**：见 [R1-R5-WALLRUN-KEYS.md](R1-R5-WALLRUN-KEYS.md)。
4. R5 的 `wallrunGravityRampUpTime`、`wallrunSameWallHeight` 值未知（R5 运行时用 `bridge_classvar_get` 就能读到）。**已关闭（T6，2026-10-29）**：N4-A classvar 普查里有，分别是 1 和 0。
5. 墙面强度衰减（`strengthLoss*`）的公式看起来有反转，可能是 TF2 的 bug，但阈值 1000 次，实际不会触发。
6. 以上都是静态读出的。T5 用实测核对：起跑竖直速度、0.7 s 重力爬升、1.75 s 时长、墙跳速度。
