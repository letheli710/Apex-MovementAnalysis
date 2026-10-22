# 延期设计决策清单（Deferred Design TODO）

这份清单长期保存**用户明确要求暂缓的设计决策**，和一般 Bug、开发任务、技术研究 TODO 分开管理。

- 处理时机：等游戏开发接近完成（约 80%），或进入正式技能配置和整体平衡阶段时，再集中复查。80% 只是粗略的复查节点，不需要计算项目完成度。
- **Agent 不得把这里的事项当作 Bug 自动修复，也不得在用户确认前擅自做出决定。**
- 开发期间保持各项能力可以独立开关，做必要的组合测试，确保状态正确。这不代表正式游戏一定这样配置。

建立于 M9（2026-10-22）。背景见 `research/phase2-local/m8/M8-REPORT.md` 的「需要你决定的事」，以及用户的 M9 计划 M9-E（`research/phase2-local/m9/M9-PLAN.md`）。

---

## [ ] E1. 不同二段跳能否同时装备

**状态**：暂缓（未决定）。最后更新：2026-10-22（M9 开始时）。

**背景和现有行为**
- 目前有两种二段跳：
  - **HSD 通用二段跳**（M7-A，HSD 设计）：Fun 配置默认开启；Reference 关闭，可以用游戏内按键 `9` 打开。
  - **Octane 跳板专属二段跳**（M8-C，按 R5 S21 实测）：Reference 和 Fun 的 Octane 配置都有，游戏内按键 `5` 开关。
- 两者同时开启时（Fun + Octane），跳跃键仲裁（`JumpArbitration`，M8-A）的规则是：
  - 跳板二段跳可用时优先（rank 300），通用二段跳判为 LOST，不扣次数；
  - 下一次按键再用通用二段跳；
  - 跳板二段跳还没生效（发射后 0.108 秒内）时，按键归通用二段跳。
- 和其他空中机动的关系：
  - Valkyrie 喷气：rank 250（喷气优先规则）或 100（二段跳优先规则），游戏内按键 `0` 切换；
  - Zipline Super Jump、墙跳、跑墙跳、抓边跳离都是直接接管按键的动作，优先于两种二段跳。

**已知数据、代码和配置位置**
- HSD-Unity：
  - `Assets/HSD/R5Replay/Runtime/Abilities/DoubleJumpAbility.cs`（`DoubleJumpParams`：`maxAirJumps` 1、`height` 45、`redirect` 0.5、`minSinceTakeoff` 0.1、各重置开关、`jetsRule`、`holdForJets` 0.25，全部是 [design]）；
  - `Assets/HSD/R5Replay/Runtime/Abilities/PadDoubleJumpAbility.cs`（`PadDoubleJumpParams`，[meas]/[fit]，数据见 `research/phase2-local/m8/r_pad_djump/`）；
  - `Assets/HSD/R5Replay/Runtime/Skills/JumpArbitration.cs`（优先级表）。
- 文档：`research/phase2-local/m8/unity/M8A-UNITY.md` §2、`M8C-UNITY.md`、`m7/unity/M7A-UNITY.md` §3.3。

**可考虑的未来方案**
1. 互斥：同一个角色只能装备一种二段跳（技能槽规则）。
2. 允许同时装备，保留当前仲裁规则（跳板二段跳优先，两种的次数各自独立）。
3. 共用一个"空中跳跃"资源池。
4. 通用二段跳只作为某些角色或模式的特性，不进入通用技能库。

**暂缓原因**：技能槽、角色分配和平衡还没有设计。现在定互斥规则会过早限制能力库。

**重新评估前需要的证据**
- 真人试玩：两者同时开启时，操作是否混乱；跳板二跳和通用二跳的按键时机是否容易区分。
- 技能槽设计方案出来之后。

---

## [ ] E2. Fun 斜坡滑铲的最终速度平衡

**状态**：暂缓，保留现有 Fun 参数，不做新的斜坡平衡调整。最后更新：2026-10-22。

**注意**：这里差的是**下坡滑铲的加速度**，在已有对照条件下约为 R5 实测的 1.6 倍。**不代表整个游戏的移动速度或最终速度是 Apex 的 1.6 倍。**

**现有行为**
- **Reference**：只在**按住下蹲**滑铲时有坡面加速（M8-B 按 R5 实测改的），30–40° 时和 R5 拟合相差 2–3 %。冲刺下坡保持 299，和 R5 一致。
- **Fun**：HSD 设计的斜坡滑铲（M8-A），游戏内按键 `6` 开关：
  - 沿坡面施加重力（`gravityScale` 1.0）；
  - 滑铲摩擦按坡度缩小：坡度 ≥ `fullFrictionGrade` 15° 时乘 `downhillFriction` 0.25；横向和上坡保持全摩擦；
  - **能量上限**：|v_h|² ≤ 2·g·(滑铲中下降的高度)，晚一帧记入，最多存 `energyBuffer` 24 u 的高度，离开"地面滑铲"状态就清零；
  - 坡面项不会把速度推高到 `maxSpeed` 760 u/s 以上（也不会降低已有速度）。

**数据来源**
| 项 | 来源 | 数值 |
|---|---|---|
| 下坡滑铲额外加速度（按住下蹲） | **R5 实测** [fit]，`research/phase2-local/m8/r_slope/`，只覆盖 29–41° 坡，n 15 个试次 | 147 + 342·sin(坡度) u/s²，rms 10 |
| 冲刺下坡 | R5 实测 | 保持 299 |
| 地面上 vz | R5 实测 | 0 |
| 上坡滑铲 | **未实测**（M9-D1 可能补数据，但不据此调整 Fun） | – |
| Fun 坡面模型的全部参数（`gravityScale`、`downhillFriction`、`fullFrictionGrade`、`maxSpeed`、`energyBuffer`） | HSD [design] | 见上 |
| 差异 | M8-B 对照（`m8/unity/M8B-UNITY.md`） | Fun 额外加速度 538–586 u/s²，R5 拟合 318–367 u/s²，约 1.6 倍 |

**代码和配置位置**：HSD-Unity `Assets/HSD/R5Replay/Runtime/Traversal/HsdMovement.cs`（`SlopeSlideParams`，属于 `HsdMovementParams`），`R5MotorV2.SlopeSlideStep`，配置资源 `Presets/Configs/FunConfig.asset` / `ReferenceConfig.asset`。文档：`m8/unity/M8A-UNITY.md` §3、`M8B-UNITY.md`。

**可考虑的未来方案**
1. 保持现状：Fun 更快更爽。
2. 把 `downhillFriction` 设为 1.0，加速度就贴近 R5 拟合（M8-B 估算）。
3. 取中间值。
4. 按地图或模式分别设置。

**暂缓原因**：用户目前无法决定 Fun 应该更快，还是更接近 Apex。需要真人试玩和整体速度平衡来判断。

**重新评估前需要的证据**
- 真人在斜坡区（V 坡、W 变坡链）分别用两种设置试玩的反馈；
- 整体速度平衡（地图尺度、其他能力的速度上限）确定之后；
- 可选：上坡和 < 29° 坡的 R5 数据。

---

## [ ] E3. Jump Buffering（跳跃输入缓冲）

**状态**：暂缓，不新增也不调整跳跃缓冲。最后更新：2026-10-22。**不得因为之前的计划提到过缓冲，就自动开发这个机制。**

**现有行为**（M8-B 审核，`m8/unity/M8B-UNITY.md` §bunny hop / gaps）
- **没有任何跳跃缓冲。** 跳跃只看当帧的按键边沿。
- **Reference**：落地前一帧按下的跳跃会被丢掉。落地那一帧按跳，就是兔跳的正常时机：出口速度 min(v0, 299)，跳跃高度受反多跳规则限制。
- **Fun**：落地前一帧的按键会被**通用二段跳接管**（只要二段跳还有次数，并且离起跳已超过 0.1 秒），变成一次空中跳跃。
- 仲裁层（`JumpArbitration`）规定被拒绝的按键直接丢弃，不保留到下一帧。M8-A 遗留问题里写着 "a refused press is dropped; there is no input buffer"。

**已知数据（R5）**
- 反多跳规则：frac = clamp(0.3 + 0.7·(t − 0.15)/0.60, 0.3, 1)，t 为落地后的时间（`research/phase2-local/m2/PARAMETER-TABLE.md`）；
- 跳跃那一帧的摩擦约等于 0，所以兔跳能保住速度（M2）；
- R5 本身是否有缓冲没有专门测过。从"落地前按跳会丢失"这个 Reference 行为看，是按 R5 实测模型复刻的，但没有单独的缓冲实验。

**代码位置**：HSD-Unity `Assets/HSD/R5Replay/Runtime/Skills/JumpArbitration.cs`（按键的接管和申请协议）、`R5MotorV2.cs`（地面起跳）、`Abilities/DoubleJumpAbility.cs`（Fun 下的接管）。

**可考虑的未来方案**
1. 不加（贴近 R5 的严格时机）。
2. 只在 Fun 加一个短缓冲（例如 1–3 帧），落地时补发起跳。
3. 缓冲和通用二段跳的优先关系可配置：落地前几帧的按键优先算作落地跳，而不是二段跳。
4. 先做 R5 缓冲实验：在落地前 1–6 帧按跳，看是否起跳。

**暂缓原因**：缓冲会改变兔跳、二段跳、Super Jump 等所有时机类技巧的难度和手感，属于整体操作手感决策。

**重新评估前需要的证据**
- 真人试玩中"按了跳没反应"的频率；
- 可选：上面方案 4 的 R5 缓冲实验；
- 技能配置阶段确定通用二段跳是否保留。
