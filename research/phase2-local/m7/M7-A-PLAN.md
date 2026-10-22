# M7-A：基础 Movement 补全（用户计划，2026-10-22）

本文件是用户给出的 M7-A 计划的存档，要点逐条保留。执行记录见仓库根目录 `EXECUTION-LOG.md`。

## 目标

在 M6-B 最新 Unity 工程（HSD-Unity main `199dde8`，已包含 M6-A/B/C）上补齐三项通用 Movement：

1. **Wall Running（跑墙）**：参考 Titanfall 式跑墙，实现沿墙奔跑、方向控制、主动跳离和自然退出，并与墙跳、攀爬、翻越协调，避免状态冲突和不合理叠速。
2. **Ledge Grab / Hang（抓边与悬挂）**：基于现有边缘检测，实现抓边、悬挂、爬上、放手和跳离。重点防止高速下意外吸附、卡在边缘或无法退出。
3. **Configurable Double Jump（可配置二段跳）**：独立的额外空中跳跃，可开关、可配置次数、落地正确重置，并兼容空控、Lurch、喷气和跳板。要特别处理跳跃键和 Valkyrie 喷气的冲突。不强制所有角色默认拥有，也不视为 Octane 跳板二段跳的复刻。

不要求精确复刻 Apex 或 Titanfall 的数值：先把功能做出来，参数可调，留待后期调整。

## 要求

- **先审核现有工程**：
  - 新机制与现有 Climb、Mantle、Wall Bounce 的关系；
  - 已有的输入、碰撞、运动状态、技能槽和仲裁；
  - M6-C 已有的课程、动作链、fuzz 和反馈系统。
  - 不重做 M6-C，不做不必要的底层重构。
- **整合与验证**：
  - 复用 M6-C 练习场和测试设施，只增加必需的测试区域；
  - 验证三项机制各自单独操作，以及与滑铲、墙跳、翻越、Tap Strafe、钩爪、Zipline 的典型组合；
  - 重点查输入冲突、状态中断、碰撞异常、卡死和错误叠速；
  - 用现有回归体系确保 M6 不退化。
- **交付**：
  - 三项机制的 Unity 实现；
  - 基础镜头反馈和简单视效；
  - 新测试和原有回归结果；
  - Windows 试玩构建和简短中文操作指南；
  - 完成情况、遗留问题和设计值清单。
- **原则**：
  - 复用现有架构，新参数可调；
  - 不新增传奇技能、战斗系统或正式美术；
  - 不为非关键边界问题无限扩大任务。
- **完成标准**：三项机制稳定可玩，能与现有 Movement 自然组合，主要回归通过，并提供 Windows 构建。

## Leader 审核记录（开工前）

- **Apex 原版是否有这三项**：都没有，三项都按 HSD 设计实现，数值全部标为 [design]。
  - **抓边/悬挂**：M6-A 实测（A2-CLIMB.md）R5 S21 **没有 ledge hang**。爬墙的结果是翻越或掉落，`ClimbAbility` 的注释写着 "No ledge hang exists [meas]"。
  - **跑墙**：Apex 只有爬墙和墙跳（引擎内部叫 `JumpOutOfWallRun`，数值来自 census 的 `wallrunJump*`），没有 Titanfall 式跑墙。
  - **二段跳**：Apex 只有 Octane 跳板发射后的二段跳（`pad.double_jump_delay` 0.1 s，Unity 里未建模），没有通用二段跳。
- **可复用的现有代码**：
  - `FunAbilities.cs` 里有一个 M5 时期的设计版 `WallRunAbility`（只在 Fun 配置中启用）；
  - `ClimbAbility`（M6-A，含 mantle、wall bounce、贴墙滑落）；
  - `WallBounce`；
  - `SkillArbiter` / `SkillRules`（优先级、驱动权互斥）；
  - `IMovementWorld`（边缘和法线查询）；
  - M6-C 的课程、fuzz、演示框架和 F9/F10 反馈。
- **配置策略**：
  - Reference 继续代表 R5 实测行为，三项默认关闭；
  - Fun 默认开启；
  - 游戏内可以单独开关，Reference 下也能打开试玩。
  - 这样 M6 的实测回归和 Reference 的含义都不受影响。
