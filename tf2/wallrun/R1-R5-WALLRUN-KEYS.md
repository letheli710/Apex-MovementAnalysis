# R-1：R5 里 Apex 新增的蹬墙跑键

日期：2026-10-29。用途：补齐 TF2-REPORT 提案 P-01 的 B 预设（TF2 规则 + R5 数值），同时关闭 T3 未解项 3。

## 做法

- 只读 R5 的 Ghidra 工程 `ghidra-projects/r5apex_dx12`（`-readOnly`），用研究仓库的 `n2/DecompileList.java` 反编译 8 个函数。
- 反编译原文在 `TF2-Research/local/r1/r1.c`，不进版本库。
- 函数、读取点和描述符名来自研究仓库 `research/rea-native/local/n1-raw/setfile-readers.tsv`、`setfile-descriptors.tsv`；浮点常量来自 `floats.tsv`；R5 数值来自 N4-A classvar 普查。
- 地址都是 `r5apex_dx12.exe` 的。`player+0x…` 偏移只在本文件内对照用。

## 结论

| 键（R5 值） | 读取位置 | 规则 |
|---|---|---|
| `wallrunDuckCausesFallOff`（true） | `WallClimb_Move` 0x140a4d4e0 | 跑墙中按下蹲键（按键位 0x4000004，蹲或切换蹲）就脱墙 |
| `verticalGainCutoff_wallrun`（175） | `WallRun_TryStart` 0x140a4e220；`WallClimb_Move`；0x140a4d470 | **起跑**：接触点高于"参考高度 + 175 − `climbFinalJumpUpHeight`（28）"时不能起跑，即约比参考高度高 147 以上就不行。从滑铲超级跳起跳时再加 `slideSuperJumpAdditionalVerticalGainCutoff`（200）。**跑墙 / 攀墙中**：`WallClimb_Move` 比较 min(player+0x2ad0, 参考高度 + 175 − 28 − `climbHeight` 100) + `climbHeight`，即参考高度 + 147；这是攀墙最终跳的目标高度上限，即 ≤ min(起跑高度 + 128, 参考高度 + 175)；跑墙爬升本身由 f 的高度门截止（见第 3 条）。参考高度是 player+0x2078，即最后一次站立时的地面高度（腾空后只降不升；跳板 / 重力炮时为弹道最高点），见 `D1-D2-REPORT.md` §2。值 < 0 时整条规则关闭 |
| `wallrunCeilingLimit`（0.5） | `WallRun_TryStart` | 墙面法线 z 下限 = −clamp(limit, 0, 1) = −0.5。也就是允许起跑的"内倾墙（悬垂）"比 TF2 更斜（TF2 写死 −0.35）。这条检查只在某个条件函数（0x140ac2320）≤ 0、且法线 z ≤ 0.7 时做，条件函数没读 |
| `wallrunDecelerateVertical`（300） | `WalkMove` 0x140a4a7c0 跑墙分支 | 沿墙"上下"方向的速度每秒线性减 300 × player+0x2af4，减到 0 为止；下坠时再乘 (1 − 重力系数) × (1 − 滑落量)。另外乘冲击后低减速的窗口系数（T-G09） |
| `wallrunDecelerateHorizontal`（500） | `WalkMove` 跑墙分支 | **没有移动输入时**，沿墙水平速度每秒线性减 500 × player+0x2af4（`wallstickEnabled` 时改为 100） |

另外确认的几点：

1. **R5 没有 `wallrunFriction` 键。** setfile 描述符表里只有 `airFriction`，普查里也没有。TF2 的指数摩擦（4/s，T5 实测）在 R5 里由上面两条线性减速代替。所以 **B 预设应该用 R5 的线性减速，不用 TF2 的摩擦 4**。
2. **起跑提速公式和 T5 实测一致**（`WallRun_Begin` 0x140a4f120）：
   - 沿墙向上分量 u < 250 × f 时，加上 250 × f − max(u, 0)；
   - 也就是向上慢时补到 250，下坠时加 250。
   - 这段由 setfile `wallrun` 开关控制（R5 是 false，所以 Apex 里不会触发）。
3. **提速和重力爬升共用一个系数 f。** 提速是 250 × f；重力系数是 1 − f × (1 − t / 爬升时间)（0x140a34560，R5 爬升时间 1 s）。f = 0 时，提速为 0、重力从第一帧就是满的，正好是 T5 里"传送起跑"的表现；跳起后起跑时 f = 1。
   - f 由 0x140a4fed0 计算（0x1407936f0 只是更新坐标）。disable 标志 +0x2ad8 ≠ 0 时为 0；z − 参考高度 ≥ `verticalGainCutoff_wallrun`（175）时为 0；其余情况按跑墙次数 +0x2ad4 和 `wallrun_strengthLossStart/End`（默认都是 1000）给 1，所以实际上 f 只有 0 或 1。disable 在着地时置 1，在地面起跳、墙跳时清 0；同一面墙再贴时，Begin 在算完提速后也会把它置 1。见 `D1-D2-REPORT.md` §1。
   - P-01 实现成：上次着地后做过地面起跳或墙跳，且 z − 参考高度 < 175，f = 1，否则 f = 0；重力系数每帧重新算 f。
4. `wallstickEnabled` 为 true 时，重力系数固定按 100 s 爬升，水平减速改为 100。R5 普查里这个键没有出现，按默认关处理。

## 对 B 预设的影响（已回写 TF2-REPORT 第 4 节）

| 项 | B 预设 |
|---|---|
| 水平 | 上限 225，加速 200；无输入时线性减速 500；朝后上限 50 |
| 竖直 | 上限 112，加速 450；线性减速 300（下坠时乘 (1 − 重力系数)(1 − 滑落)） |
| 摩擦 | 无（R5 没有 `wallrunFriction`） |
| 重力 | 1 − f × (1 − t / 1.0 s) |
| 起跑 | 提速 250 × f；接触点不能比参考高度高约 147（175 − 28）；法线 z ∈ [−0.5, 0.7]；贴墙距离 17 |
| 跑墙中 | 高出参考高度 175 时，f 当帧变 0、重力恢复满值，不再爬升；按蹲脱墙 |

## 未解

- ~~player+0x2078（参考高度）和系数 f 的来源~~：静态已解，见 `D1-D2-REPORT.md`；还要 TF2 实测确认掉落起跑、高度门、同墙再贴（报告 §4）。
- 天花板检查的前置条件函数 0x140ac2320。
- player+0x2af4 的含义（推测是墙面强度，正常为 1）。
