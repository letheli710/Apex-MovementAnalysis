# 暂时搁置的能力

本文件记录已经研究过、但暂时不做进 High Speed Doom（Unity）的传奇能力：搁置了什么、为什么搁置、以后重启时从哪里接着做。

- 决定日期：2026-10-21，由用户在 M6-B 结束后决定。
- 同时确定的实现范围：只做 Valkyrie 喷气补全和 Ash 相位突破（作为路线工具）。

## Loba：Burglar's Best Friend（手环传送）

**搁置原因（用户）**：这个技能和很多游戏里已有的能力重复。最简单的例子就是 Minecraft 的末影珍珠：扔出一个投射物，落地后把自己传送过去。对 High Speed Doom 来说，它带来的新意不够。

**已经掌握的内容**，以后重启时可以直接用，详见 [M6-B-REPORT.md](research/phase2-local/m6/b_legends/M6-B-REPORT.md) 第 2 节和 [P3-TRANSITIONS.md](research/phase2-local/m4/p3_transitions/P3-TRANSITIONS.md)：

- **实测**：
  - 按键后约 1.21 s 才扔出手环。
  - 扔出 0.30 s 后再按一次可以提前落地（5/5），之后约 0.6 s 完成传送，其中 0.4 s 是脚本里固定的延迟。
  - 传送后速度一律为 0（M6 15/15，M4 6/6），之后没有锁操作。
- **源码**：
  - 抛射速度 1815（俯仰超过 50° 时为 1390）。
  - 提前落地有门槛：至少 0.24 s 后才能按，且只能按一次。
  - 落点要校验合法；失败会恢复原来的速度和视角，并退还一次充能。
- **没解决的问题**：精确的提前落地门槛、落点距离和按键时机的关系、失败时的退还路径。
- **Unity 能复用的部件**：`TeleportAbility` 的速度清零模式、`ProbeGround`。缺的是投射物和落点校验。
- **开发成本估计**：中。

**研究进度**：游戏内实测已做两轮（M4 一轮，M6-B 一轮），分析脚本和报告都已完成。Unity 里只有 M5 做的一个简化版传送（速度清零，传送距离是设计值），没有投射物、提前落地和落点校验。

**数据与文件位置**（相对本仓库根目录）：

| 内容 | 位置 |
|---|---|
| M6-B 游戏会话（25 次：提前落地时间 0.7 / 0.9 / 1.2 / 1.5 s 各 5 次，冲刺抛掷 5 次） | `research/phase2-local/data/20261021_180124_M6B_loba/`（`runner.json`、`report/rows.csv`、`report/census.csv`） |
| M4 游戏会话（12 次：冲刺和站立抛掷各 6 次） | `research/phase2-local/data/20261021_031416_M4_loba/` |
| M6-B 分析脚本与输出 | `research/phase2-local/m6/b_legends/`：`m6b_analysis.py`、`analysis_output.txt`、`results.json`、`params.json` |
| M6-B 结论 | `research/phase2-local/m6/b_legends/M6-B-REPORT.md` 第 2 节 |
| M4 结论与脚本 | `research/phase2-local/m4/p3_transitions/`：`P3-TRANSITIONS.md`、`p3_analysis.py` |
| 源码调查 | `research/phase2-local/m6/SOURCE-AUDIT.md`（M6-B → Loba） |
| 实验调度（可直接重跑） | `research/phase2-local/tools/hsd_trial.py`：`b_loba_*`、`m4_loba_*` |
| Unity 简化版 | HSD-Unity：`Assets/HSD/R5Replay/Runtime/Abilities/TransitionAbilities.cs`（`TeleportAbility`，Loba 模式） |

原始游戏日志（`platform/` 子目录）只保存在本机对应会话文件夹里，不上传 git。

## Alter：Void Passage（虚空通道，穿墙传送门）

**搁置原因**：

- **在本地 R5Flowstate S21 上测不到。**
  - 服务器端的放置逻辑是 SDK 社区重写的，在我们的测试墙上始终给不出有效落点：放置有效 = false，坐标为 `<0,0,0>`。
  - 把 SDK 留的 3 个修正开关全部打开后重试，出口被算到墙后 2538 u，超过 30 m 的上限，仍然失败。
  - 两次共 34 次试验，0 个传送门。
- **继续追查成本高、收益低**：只能去调试 SDK 的原生放置代码，属于止损原则里"高成本、低收益"的情况。
- **只能凭源码设计**：如果要做，它的数值完全来自源码，没有实测对照，和项目"实测优先"的原则不符。
- 用户决定暂时搁置。

**已经掌握的内容（全部来自源码，未实测）**，详见 [M6-B-REPORT.md](research/phase2-local/m6/b_legends/M6-B-REPORT.md) 第 1 节和 [SOURCE-AUDIT.md](research/phase2-local/m6/SOURCE-AUDIT.md) M6-B 部分：

- 出口速度：沿出口法线方向，大小为 clamp(v·n, 50, 300)。这是四个候选里**唯一能保留部分速度的传送**，也是唯一的穿墙能力，独特性最高。
- 地板或天花板上的出口，方向直接朝上或朝下。
- 传送门存在 15 s，放置延迟 0.7 s，同一个门 1.35 s 内不能再进，墙厚上限 30 m，穿过后有 1 s 相位状态。
- **没解决的问题**：放置在哪一步被拒绝；换成更薄的墙，或者用地图自带的墙面，能否放出来；实际的出口速度和传送后状态。
- **Unity 能复用的部件**：`TeleportAbility`、`ResolveTeleport`、发射类冲量。缺的是墙厚查询和成对的传送门。
- **开发成本估计**：中到大。

**研究进度**：源码调查已完成。游戏实测尝试了三次（正式一次、按键方式试验一次、打开 SDK 开关一次），都没能放出传送门，所以没有任何速度或状态的实测数据，只有放置失败的诊断日志。Unity 里完全没有实现。

**数据与文件位置**（相对本仓库根目录）：

| 内容 | 位置 |
|---|---|
| 正式会话（15 次：冲刺、走路、站立各 5 次，均未成功） | `research/phase2-local/data/20261021_175730_M6B_alter/` |
| 按键方式试验（6 次：长按 1.2 s、按住加攻击、点按加攻击） | `research/phase2-local/data/20261021_181108_M6B_pilot_alter/` |
| 打开 3 个 SDK 开关后的重试（13 次，仅作诊断） | `research/phase2-local/data/20261021_185338_M6B_alter_sdkfix/` |
| SDK 放置诊断日志（`[OPL-SRV]` 行：入口修正失败、深度不足、出口 2538 u） | 上面各会话的 `platform/logs/server/` 下（只在本机，不上传 git） |
| 分析脚本与结论 | `research/phase2-local/m6/b_legends/`：`m6b_analysis.py`；`M6-B-REPORT.md` 第 1 节（含第二次重试的说明） |
| 源码调查（出口速度、门寿命、厚度上限等，带文件行号） | `research/phase2-local/m6/SOURCE-AUDIT.md`（M6-B → Alter） |
| 相关源码 | `research-src/s21-platform/scripts/vscripts/weapons/mp_ability_phase_door.nut`；SDK 放置 `research-src/s21-r5sdk/src/game/server/vscript_server_placement.cpp`（开关约在第 2936–2946 行） |
| 实验调度（可直接重跑） | `research/phase2-local/tools/hsd_trial.py`：`b_alter_*`、`bp_alter_*`；SDK 开关用 `--both-cvar` 传入 |

`research-src` 是本机固定版本的源码克隆，和本仓库在同一个工作区目录下，不在本仓库里。

## 重启条件

满足以下任一条件时可以重新评估：

- 有了新的设计需求，例如 HSD 需要一种"带速度穿墙"的原创能力。这时可以只借鉴 Alter 的规则，自己设计数值。
- 本地构建更新后 Alter 能正常放置，可以补实测。
- Loba 有了明确不同于末影珍珠类能力的新玩法。
