# M8 扩展评估：Revenant、Vantage Echo、动态钩爪锚点与其他候选（案头评估，M8-PLAN 第 10 项）

范围：只读已有报告与源码，没有运行游戏或 Unity。成本是估计（S 约半天以内，M 约 1–2 天，L 更久），不是承诺。路径相对 `research/phase2-local/`，源码前缀 `P:` = `research-src/s21-platform/scripts/vscripts/`，`SDK:` = `research-src/s21-r5sdk/src/`。

证据标签：**[meas]** 本地 R5 实测；**[src]** 读过源码；**[comm]** 社区说法；**[unk]** 本地文件里查不到。
前提不变：这是 Movement 能力库，技能槽和角色分配以后再做；Loba、Alter 继续搁置（`SHELVED-ABILITIES.md`），本文不推荐，除非出现新事实。

## 1. Revenant：蓄力扑跃、长攀爬、墙面衔接

### 1.1 已测与已建

| 项 | 数值 / 结论 | 证据 | 出处 |
|---|---|---|---|
| 蓄力扑跃的公式 | v = (700 + 450·c)·forward(pitch − 35°)，**替换**速度；c = clamp((t_release − t_press − 0.9)/1.3, 0, 1) | [meas] pitch 0：仰角 35.000°，c0 速度 701.2，c13 速度 839.1（误差 +0.7） | `m4/valk_rev/VALK-REV-PRIMITIVES.md` §3.2 |
| 出手时机 | 点按 0.908–0.917 s 才出手（`toss_pullout_time` 0.9，提前松手也不能缩短）；0.9 s 后松手则 1 命令内出手；**满蓄力要按住 2.2 s** | [meas] 15 次；[src] | 同上 §3.1 |
| 飞行与落地 | g = 750，水平无阻力，落地**无减速**（Octane 规则系数 1），移速系数 6–14 命令后恢复 | [meas] 15 次 | 同上 §3.4 |
| 高角度规则（pitch < −15° 速度除以最多 1.5、抬角衰减到 0）、低头地面检查（≥ 20° 且 200 u 内有地 → 15°）、75° 上限、满蓄力 1150 | 只在源码里 | [src]，**未测** | `P:weapons/mp_ability_revenant_shadow_pounce_free.nut:48-67,344-394` |
| 墙面规则 | 蓄力期间 `disable_wall_run` 一直开着；出手后再禁用 0.75 s（`SHADOW_POUNCE_WALL_CLIMB_DISABLE_DURATION`），playlist 变量可改；`wallClimbOnlyFromWall` 默认 0 | [src] | 同 nut :63-65,124-128,154,215-226,409-423 |
| 长攀爬的唯一线索 | Revenant 的 setfile 与 T0 只差 `climbHeight` **1250**（普通角色 100）。这是普查读数，从没跑过 | [meas] 普查 | `VALK-REV-PRIMITIVES.md` §1 |
| 普通攀爬模型（对照基线） | 全程 0.849 s，从接触点只升 96.2 u（不是 100），终点在 floor + 147.06，**与墙顶无关**；速度线 Z0 = floor + 180.3；已测墙高 60–400；墙顶只是翻越触发（差 ≤ 约 80 u） | [meas] | `m6/a2_climb/A2-CLIMB.md` §2 |
| Unity 里已有 | `PounceAbility`（`ImpulseAbilities.cs`；M4 回放：c0 射程误差 6.9 u、c13 0.76 u，c0 出手早 2 命令）；`ClimbAbility` 已参数化（`endHeight`、`accel`、`speedLineK`、`speedLineZ0`、`zRef` = 起跳点）；M8-A `JumpArbitration`：发射会拒绝所有延迟申请 | 代码与 M4 / M8-A 报告 | `m4/unity/index.md`，`m8/unity/M8A-UNITY.md` §2 |

### 1.2 缺口

- 扑跃：满蓄力（2.2 s 按住）、非零 pitch（含高角度和低头地面检查）、带初速度起跳（替换还是叠加）、飞行中按键的空控、扑向墙面与墙面起扑（`fromWall`）。M4 的所有试验都从静止、pitch 0 开始（`VALK-REV` §4 第 5 条）。
- 长攀爬：**完全没有数据**。`climbHeight` 1250 是改变终点高度、速度线，还是只放宽封顶，本地文件看不出来。普通角色的 100 并不等于实测增益 96，所以不能直接拿 1250 当增益。攀爬是否有时间上限（`wallrun_timeLimit`、`wallrun_hangTimeLimit` 在 SDK 的字段表里，`SDK:game/server/wallclimb.cpp`）、终点的 jump-up、与墙顶翻越的衔接，也都未知。
- 墙面衔接：扑跃后 0.75 s 内的墙面禁用在 Unity 里是否实现，我只 grep 过，没读到（视为未建）。

### 1.3 本地 R5 的测量成本

| 内容 | 排期（每格 5 次） | 备注 |
|---|---|---|
| 长攀爬（优先） | `e6_climb`（M6-A2 已有）× Revenant × 墙高 232 / 400 / 700 / 1000 / 1300，共 25 次，外加普通角色 1 个高度做对照 | 复用 `a2_climb_analysis.py`。**风险**：A2 的岩石只测到 400 u，更高的墙要找地图上的悬崖面或能生成的更高实体，本地文件判断不了能否做到（[unk]）。可先用 `m3/map` 的扫描找候选墙 |
| 扑跃补全 | `m4_pounce_*` 加：满蓄力 hold 2.4 s；pitch −60 / −30 / +10 / +40（近地）各 1 格；冲刺中起扑；落点前有墙 | 约 6 格 30 次，M4 的 runner 和 `valk_rev_analysis.py` 可直接加参数 |
| 墙面衔接 | 扑向墙（有 / 无 0.75 s 窗口）、在墙面上蓄力后起扑 | 约 3 格；需要 `bridge_wallclimb_tap 1`（`m6/SOURCE-AUDIT.md`） |
| 合计 | 约 2 次会话，加分析 | 单实例规则：同时只能一个进程控制游戏 |

### 1.4 Unity 构建成本

- 扑跃补全：S。公式已在代码里，补 0.75 s 墙面禁用、满蓄力测试、非零 pitch 回放。
- 长攀爬：S（若只是参数档位）到 M（若有时间上限、新终点规则或高墙场景）。数据出来前不能定。需要新增高墙练习场和镜头检查。
- 墙面衔接：S–M。用 M7-A 的墙跑、抓边和 M8-A 仲裁，主要是写规则和测试。

### 1.5 独特性与复用

- 扑跃的独特处是**蓄力换速度、瞄准定方向**；与跳板和 zipline super jump（一次性冲量）相比，它是可控的弹道。中高独特性。
- 长攀爬本身不新（普通攀爬已有），但它把"高度"变成角色级能力：攀爬 → 翻越 → superglide 的链条（`m6/M6-C-DESIGN-NOTES.md` §2）在高墙上更长。中等独特性，复用价值高。
- 复用：`InstantImpulse`、`ClimbAbility`、M7-A 墙跑和抓边、`JumpArbitration`（发射拒绝申请的规则已就位）、`LandingSlowdown`（系数 1）。几乎没有新原语。

## 2. Vantage Echo（蝙蝠重定位）与动态钩爪锚点

### 2.1 Vantage 是否在这个构建里

**在。** 证据：`P:weapons/mp_ability_companion_launch.nut`（战术）、`P:weapons/sh_vantage_companion.nut`（2469 行的 Echo 伴侣）、`P:weapons/mp_weapon_vantage_recall.nut`（装备）、被动 `PAS_VANTAGE`；`m4/ABILITY-TRIGGERS.md` 的表格把它标为"Yes（S21 客户端原生 JetDriveAccel，复制 cvar）"。但**从没测过、也没跑过**（`m4/M4-REPORT.md` A2、`m4/p3_transitions/P3-TRANSITIONS.md`）。本地 dedi 上 Echo 的 AI 伴侣能否真的出现并寻路，没有证据（[unk]）。

### 2.2 机制（全部 [src]）

- **流程**：先把 Echo 派到一个点（`VANTAGE_COMPANION_RANGE_BASE` 40 m = 1575 u，最大 55 m，增强版 50 / 65 m；`sh_vantage_companion.nut:99-102`）。再按战术键，玩家被"喷气拖拽"到伴侣位置：`player.BeginJetDrive( 787, 1575, companion.GetOrigin(), companion, <0,0,-69>, timeout )`（路径速度 20 m，加速度 40 m，`mp_ability_companion_launch.nut:79-88,794-811`），超时 = 2·距离/速度。
- **目标是伴侣实体，不是固定点**：`BeginJetDrive` 的第四个参数是目标实体，也就是它天然在**追踪会移动的目标**，是"动态锚点"的现成样本。
- **到达后**：二段跳 `EnableJetDriveDoubleJump( <512, 0, 394>, 0.5, … )`，即前 13 m / 上 10 m 的速度（升级版 551 / 472），朝回头方向打 0.5 折（升级版 0.8）。进入时会取消已有的二段跳（`Signal "JumpPad_GiveDoubleJump"`，nut:793）。
- **发起条件**：伴侣需在视野 60° 内且视线无遮挡（`CanLaunchToCompanion`，nut:648-715）；忙于 context action、相位、skyward 等状态时拒绝。
- **dedi 注意**：dedi 上的 `VJetDrive` 是 SDK 社区从零重写（`SDK:game/server/jetdrive.cpp`），不是 S21 原码；S21 客户端的预测才是原生数学。M4 报告据此认为它不是"服务器真相"，所以测量应以**客户端 MOVE-TRACE** 为准，并记录两边偏差。

### 2.3 研究成本、构建成本、独特性

| 项 | 评估 |
|---|---|
| 研究成本 | M。捷径：用服务器 EVAL 直接 `BeginJetDrive` 到固定点或脚本 mover（`ABILITY-TRIGGERS.md` 已给出命令形式），绕开 Echo AI。需测：速度–距离曲线（3 个距离）、加速段与到达减速（`JET_DRIVE_PATH_DECEL_*`，5 m 内）、到达速度和交接、二段跳窗口（`JetDriveWindowBegin`）和方向、下蹲取消、超时。约 2 次会话。动态目标需要一个会移动的脚本实体（SDK 有 `script_mover_traversal.cpp`），能否生成未验证 |
| 构建成本 | M。喷气拖拽 = 运动学路径（像 zipline / Breach 的 `kinematic`），目标是"放置点或移动实体"；到达后的二段跳可直接接 M8-A 为 Octane 预留的 `IJumpClaimant`（rank 300 附近）。放置对象（Echo）可先简化为瞄准点加射线，不做 AI 寻路 |
| 独特性 | 中。"先放一个点，再飞过去"和被搁置的 Loba（丢出去，传过去）流程相似，而用户搁置 Loba 的理由正是"和很多游戏的能力重复"。差别：Echo 是**连续受控的路径飞行（787 u/s）**，保留速度，到达后有二段跳，而不是瞬移加速度清零。如果做，要强调这条差别 |
| 组合潜力 | 高（有条件）。M8 R1 实测"二段跳会重新锚定 lurch 窗口"，所以 Echo 到达 → 二段跳 → lurch / tap strafe 是现成的链；拖拽期间与钩爪、喷气互斥（驱动互斥规则已有） |

### 2.4 动态钩爪锚点（移动或附着的锚点）

- **Apex 侧**：Pathfinder 钩爪是引擎原生 `player.Grapple(dir)`，脚本只处理弹药和回调（`ABILITY-TRIGGERS.md` §2.1；`P:weapons/mp_ability_grapple.nut:105-127,201-263`）。回调带 `hitent`，所以引擎知道命中的实体；`AddEntityCallback_OnGrappled` 目前只给杠杆用（`m6/b_legends/M6-B-REPORT.md` §5）。
- **已有结论**：对移动实体、玩家和可部署物的交互**全部未测**；源码线索只有"prowler 在 > 400 u/s 时脱钩"（[src]）。核心拉拽律 RF 模型是对静止墙面拟合的（`m4b/swing/SWING.md`），脱钩规则经三轮仍未识别。
- **本地能否测**：需要一个会动的实体。能生成 `script_mover` 并让钩爪命中它，**只是推测**，没有证据。建议先做 0.5 天的可行性探针。
- **Unity 侧**：`GrappleAbility` 现在只认 `IGrappleSurface.Raycast`（静态平面 / 网格），锚点在附着时锁定（目标 = 命中点 + 31.9 u）。支持动态锚点要加：每命令更新目标、相对运动坐标系下的速度继承、锚点消失时的脱钩。成本 S–M，但**前提是 motor 支持站在或贴着移动平台**，目前没有证据显示已有（[unk]）。
- **数值**：Apex 对移动锚点没有实测数据，只能是 HSD 设计值；这与"实测优先"不合，但也意味着不依赖 R5。
- **独特性与组合**：中到高。关卡层面的价值大于角色层面：移动平台、摆荡的挂点、被 Echo 携带的锚点。与 Echo 拖拽共享"追踪移动目标"的代码，建议放在 Vantage 之后一起做。

## 3. 其他候选（简述）

| 候选 | 证据 | 评价 |
|---|---|---|
| **Sparrow 墙面高跳（"climb high jump"）与二段跳被动** | [src] `SDK:game/shared/wall_launch_math.h`（最大高度 300、外推 150–450 u/s、边缘空控 320 / 加速 800，需要贴墙并探测墙顶，每次接地一次）；`P:pilot/sh_pilot_passive_sparrow.gnut`（`enable_sparrow_wall_launch`、`enable_sparrow_double_jump`、翻越增益高度 ×1.667、冲刺 ×0.667）。SDK 注释说"两个引擎都没有 climb high jump"，`research/phase1/Movement-Analysis.md` 把它列为**社区新增**。**未测** | 复用价值高：它直接建立在攀爬 / 墙跳 / 翻越上，与 Revenant 长攀爬同族，可以用同一堵墙、同一套脚本一起探。风险：来源是 SDK 社区重写，本地能否出现 S21 行为未知；二段跳部分与 M7-A 通用二段跳重叠，不值得再做 |
| **Overdrive 的 Nitro 滑铲门与滑铲超级跳**（`boosted_slide_jump`） | [src] `P:weapons/mp_ability_overdrive_tac_slide_gate.nut`；`SDK:game/server/slide_super_jump.cpp`（滑铲跳后 0.3 s 内再按跳，补一个竖直冲量）、`slide_gate_launch.cpp`。**未测**，M4–M8 报告都没评估过 | 滑铲家族的新原语，与现有滑铲、斜坡滑铲、兔跳链直接相连。冲量大小和窗口只能实测。需要用户先确认这个传奇算不算"运动型" |
| Pathfinder 钩爪收尾 | [meas] 释放、接 zipline 已完成（`M6-B` §5）；未解决：脱钩规则、垂直射程、对玩家 / 实体的行为 | 小修补，并入动态锚点那一批 |
| Wraith Into the Void | [meas] n = 7：部署 ×0.8 持续 1.17 s，加速 ×1.388 持续 2.77 s，渐隐 0.79 s（`m4/p3_transitions/P3-TRANSITIONS.md`） | 已能用 `StimAbility` 参数表达，S，独特性低，可当回归样本 |
| Ash 被动冲刺 | [src] `mp_ability_ash_dash.nut` + setfile mod `ash_dash`，数值未知，未测 | 要先读到 mod 值才能判断，不排期 |
| Newcastle Armored Leap（终极技） | [src] 1500 行 SDK 孪生 `armored_leap.cpp`，路径跟随式冲刺，带阻挡检测 | 实现复杂、依赖目标点，先不做 |
| Valkyrie skyward / skydive | `skyward.h` 写明"dedi 没有"，本地测不到 | 不适合本地研究 |
| Seer、Catalyst 等 | 本地文件里没有任何运动证据 | 不评估（[unk]） |

## 4. 排序建议（下一批）

证据列：M = 实测，S = 源码，C = 社区，U = 未知。「实测成本」指在本地 R5 拿到可信数据的成本。

| 排名 | 候选 | 独特性 | 复用价值 | Unity 成本 | 实测成本 / 可行性 | 已有证据 | 建议 |
|---|---|---|---|---|---|---|---|
| 1 | **Revenant 套件**：扑跃补全 + 长攀爬 + 墙面衔接 | 中高 | 高（攀爬、冲量、仲裁、墙跑都复用） | S–M | 低–中；高墙可行性是主要风险 | 扑跃 M；长攀爬 U（仅有 setfile 数值）；墙规则 S | **推荐，先做长攀爬的可行性探针** |
| 2 | **Vantage Echo 喷气拖拽**（先不做 AI 伴侣） | 中（须与 Loba 区分） | 中高（运动学路径、二段跳申请者、动态目标） | M | 中；先走 `BeginJetDrive` 捷径 | S；M 无 | **推荐，第二批，先做 EVAL 捷径测量** |
| 3 | **Sparrow 墙面高跳** | 中 | 高（与攀爬 / 翻越同族） | S–M | 中；真假未知，要先探一次 | S，C | **有条件推荐：与 1 同一堵墙一并探，测不出 S21 行为就放弃** |
| 4 | **动态钩爪锚点** | 中高（关卡层面） | 中（依赖移动平台能力） | S–M，另加移动平台前提 | 中，且数值只能是设计值 | U（Apex 侧）；M（静止锚点） | 在 2 之后做，作为 HSD 原创；不必等 R5 数据 |
| 5 | Nitro 滑铲门 / 滑铲超级跳 | 中 | 中（滑铲家族） | S–M | 中 | S | 先向用户确认是否纳入；暂缓 |
| 6 | Wraith Void | 低 | 低 | S | 低（已测） | M | 填补用，不单独成批 |
| – | Ash 冲刺、Armored Leap、Skyward | 未知 | – | M–L | 高或不可行 | S / U | 暂不排期 |
| – | Loba、Alter | – | – | – | – | – | **继续搁置**，无新事实 |

## 5. 不确定之处

1. 高墙：本地地图上是否有 ≥ 700 u 且可爬的墙面，我不能从现有文件判断。它决定长攀爬能否实测。
2. `climbHeight` 1250 的含义未知（见 §1.2），只能靠实测。
3. 本地 dedi 上 Vantage 的 Echo AI 能否运行未知；dedi 的喷气拖拽是社区重写，不是 S21 原码，所以第 2 名的数据只能以客户端为准。
4. Unity 的 `PounceAbility` 里是否有 0.75 s 墙面禁用，我只做了 grep，没有通读。
5. 所有 Unity 成本是估计。HSD 的数值全部是设计值，没有人试玩过（「真人手感未验收」）。
