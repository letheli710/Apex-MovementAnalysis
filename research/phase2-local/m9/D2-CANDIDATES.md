# M9-D2：S21 传奇机动候选库（案头研究，下一批开发的选题依据）

范围：只读已有报告、本地 S21 脚本，加上联网资料；没有运行游戏或 Unity，没有改任何其他文件。路径相对 `research/phase2-local/`；`P:` = `research-src/s21-platform/scripts/vscripts/`。成本是估计：S 约半天以内，M 约 1–2 天，L 更久。

## 0. 截止点、标签和三条前提

- **截止点**：官方 S21（Upheaval）= 2024-05-07 至 2024-08-06。名册以 S21 结束时为准：**26 名传奇**（首发 8 + Octane S1、Wattson S2、Crypto S3、Revenant S4、Loba S5、Rampart S6、Horizon S7、Fuse S8、Valkyrie S9、Seer S10、Ash S11、Mad Maggie S12、Newcastle S13、Vantage S14、Catalyst S15、Ballistic S17、Conduit S19、**Alter S21**）。赛季号来自 apextipsindia 的发布表、EA 帮助页和 G2A 清单；Ballistic、Alter 的赛季号只有一两个来源，另有搜索结果确认 Alter 随 S21 登场。
- **Alter 就是 S21 新传奇**，本来就在名册里，但已搁置（见 `SHELVED-ABILITIES.md`）。**Loba、Alter 本文不推荐重启**，没有出现新事实。
- **S21 之后的内容一律单独标 [post-S21]**，不进 Reference。本地构建能触发的后期内容集中记在 §3。
- 证据标签：**[meas]** 本地 R5 实测；**[src]** 读过 S21 脚本；**[wiki]** apexmovement.tech 现版（页面写明数字更新到 S27/S29，**不等于 S21 数值**）；**[comm]** 社区说法；**[unk]** 查不到。技巧库 = `m9/d_library/TECHNIQUE-LIBRARY.md`。
- HSD 状态定义：**done** = 已建且有实测；**partial** = 建了一部分，或只有设计值；**not impl** = 没建；**shelved** = 用户搁置；**n/a** = 与自身运动无关。
- 所有 HSD 数值仍是「真人手感未验收」；本表的 done 只说明数值和规则测试通过。

## 1. S21 名册与运动相关能力

| 传奇 | 运动相关能力（战术 / 被动 / 终极） | HSD 状态 | 出处与备注 |
|---|---|---|---|
| Pathfinder | 战术 Grapple；终极 Zipline Gun（玩家布绳） | 钩爪 **partial**；布绳 **not impl** | 钩爪 RF 拉力律 [meas]（`m4/M4-REPORT.md` §5.2、`m4b/swing/SWING.md`）、接 Zipline 交接（`m6/a3_zip/GRAPPLE-ZIP.md`）。脱钩规则三轮没识别、垂直射程和对实体的行为没测。地图绳已做（M6-A/M8-A/M9-A），玩家布绳没有 |
| Octane | 战术 Stim；终极 Launch Pad；被动 Swift Mend（回血，无运动） | **done**（有小缺口） | Stim ×1.298、`stim_sprint`：`m4/octane/OCTANE-PRIMITIVES.md`；跳板二段跳：`m8/unity/M8C-UNITY.md`；落地再跳：`m4b/pad_rejump/PAD-REJUMP.md`。缺：跳板 ×1.2 升级、双发、天花板冲浪、Stim 再按锁定 |
| Horizon | 战术 Gravity Lift；被动 Spacewalk；终极 Black Hole（拉扯场） | 升梯和被动 **done**；Black Hole **not impl** | 升梯 + 被动 [meas]：`m4/lift_grapple/`、`m8/unity/M8C-UNITY.md`。缺：2 s 重进封锁、10 s 到期弹出。Black Hole 脚本有拉速 300/400 [src]，没测 |
| Wraith | 战术 Into the Void；终极 Dimensional Rift（成对传送门）；被动 Voices | 战术 **done**；传送门 **partial**（设计值） | 战术 ×0.8/1.17 s → ×1.388/2.77 s → 0.79 s 渐隐：`m4/p3_transitions/P3-TRANSITIONS.md`，在 `StimAbility` 里。传送门预设 = 出口 300 u/s + 0.3 s 锁，**来自源码，没实测**（`m5/SKILL-RULES.md`） |
| Ash | 终极 Phase Breach；被动（S21 只有死亡标记，无运动） | **done**（路线工具） | `m6/unity/M6B-UNITY.md`：冻结 0.152+0.1017·帧、0.401 s 起跳 [meas]，出口速度 0。**Ash 冲刺是 [post-S21]**，见 §3 |
| Valkyrie | 被动 VTOL 喷气；终极 Skyward Dive | 喷气 **done**；Skyward **not impl** | `m6/unity/M6B-UNITY.md`。Skyward 由 SDK 服务器权威模拟，`skyward.h` 写明 dedi 没有，**本地测不到** |
| Revenant | 战术 Shadow Pounce；被动长攀爬；终极 Shadow Form（死亡保护，无运动） | **done**（有设计值） | `m9/unity/M9B-UNITY.md`、`m9/r_rev/REVENANT.md`。结束规则是设计值（1250 u 或 7.4 s）；取消输入没找到；空中起扑没测 |
| Vantage | 战术 Echo Relocation；被动 Spotter's Lens、终极 Sniper's Mark（无运动） | **not impl**（已实测） | `m8/r2_vantage/VANTAGE-JETDRIVE.md`、`m9/r_vantage/VANTAGE.md`；Unity 文档里一个字都没提 Vantage。M9-C 待做 |
| Newcastle | 终极 Castle Wall（Armored Leap 冲向目标并落地砸墙）；战术 Mobile Shield 无自身运动 | **not impl** | `P:weapons/mp_ability_armored_leap.nut`：有地面冲刺（≤600 u）、空中起飞 1000 u/s、砸地 2000–2500 u/s [src]，**没测**。SDK 有 1500 行孪生 `armored_leap.cpp`（见 `m8/EXPANSION-ASSESSMENT.md` §3） |
| Bangalore | 被动 Double Time（被射击或子弹擦过 → 速度提升） | **not impl**（预设级） | 同类脚本 `_pilot_passive_adrenaline.gnut`：`speed_boost` 严重度 0.15、持续 2.0 s、渐隐 0.25 [src]，按 M4 公式即 ×1.30；[wiki] 现版写 40%，**与 S21 脚本不符**（Leader 核查：引用的 `cl_pilot_passive_adrenaline.gnut` 里没有直接看到 0.15，此条视为未核实；Bloodhound 的 `mp_ability_hunt_mode.nut:276` 已核实） |
| Bloodhound | 终极 Beast of the Hunt：`speed_boost` 0.15 持续生效 | **not impl**（预设级） | `P:weapons/mp_ability_hunt_mode.nut:276` [src]；同上 |
| Conduit | 被动：朝向需要救援的队友跑时加速（速度 ≥ 200、45° 视角锥） | **not impl**（预设级） | `P:pilot/sh_pilot_passive_conduit.gnut` [src]，加速幅度没读到 [unk]；依赖「队友倒地」事件 |
| Seer / Fuse | Seer 战术命中加速；Fuse Knuckle Cluster 命中加速、Motherlode 推力 | **n/a** | 全是战斗命中触发的加速或推力 [wiki]，HSD 没有战斗 |
| Mad Maggie | Riot Drill、Wrecking Ball（弹跳球，不位移玩家） | **n/a** | `P:weapons/mp_ability_wrecking_ball.nut`；速度垫是 S26.1 之后的改动 [post-S21] |
| Catalyst | Piercing Spikes（减速区）、Dark Veil | **n/a** | 减速区只作用于敌人，不是自身机动；可作为以后的「关卡减速带」参考，不算能力 |
| Ballistic | Whistler（追踪弹）、Tempest；被动 Sling | **n/a** | 无自身位移；[wiki] 称终极给 30% 加速，属预设级 |
| Mirage / Gibraltar / Caustic / Lifeline / Wattson / Rampart / Crypto | 无自身机动 | **n/a** | Rampart 墙、Wattson 灯塔、Caustic 陷阱在社区里是 SG/墙弹的**落脚平台** [wiki]，见 C12。Lifeline 滑翔 / drone rider 脚本是 [post-S21 待定]（`P:pilot/sh_pilot_passive_drone_rider.gnut`），来源不明 |
| **Loba** | Burglar's Best Friend（手环传送） | **shelved** | `SHELVED-ABILITIES.md`：与末影珍珠类能力重复。Unity 只有简化 `TeleportAbility`。**不重启** |
| **Alter** | Void Passage（穿墙传送门，唯一带速度的传送） | **shelved** | 同上：本地 0/34 次放出，只有源码。**不重启** |
| 非名册 | Sparrow（S25）、Axle（原名 Overdrive，S29）、Instagib 铁轨跳（限时模式） | 见 §3 | 都在本地脚本里，都不是 S21 内容 |

## 2. 未实现和部分实现候选的逐项评估

评分列：独特性（H/M/L）、证据（meas/src/wiki/unk）、成本（R5 实测 + Unity）、本地 R5 可触发性。

### C1 Vantage Echo 喷气拖拽（S14 引入，S21 为官方内容）
- **独特原理**：连续受控的运动学路径飞行，追踪**会移动的目标实体**，保留 500–800 u/s，到达后接一次替换速度的二段跳。和被搁置的 Loba 不同：不是瞬移，没有速度清零。
- **社区技巧**（库 §3.19）：Echo 位移、到达二跳、下蹲取消。**Echo dash、Echo TS、Echolevator 是 [post-S21]**；S21 的 60° 视野 + 视线检查在 S22（2024-08-06）被移除，本地脚本里还在，**Reference 必须保留**。Bat Bending（飞行中召回 Echo 绕弯，S25 移除）出现在 S21 期间，但只有一句描述 [wiki]，输入细节不足。
- **可复用**：`IJumpClaimant`（M8-A 为跳板二段跳预留）、`InstantImpulse`、驱动互斥规则、Lurch 窗口（二跳后重新锚定，M8 R1）。
- **新增**：运动学路径驱动（目标可为点或实体）、Echo 目标系统（沿瞄准飞出，到墙或 50 m 停，悬停约 246 u 高）、60° + 视线门、固定约 1.82 s 的起飞前摇、拖拽末端的二跳窗口（约 0.84 s 起，距目标约 115 u）。
- **证据**：**meas 充分**。起飞 943.5、巡航 787、末端刹车约 180 u、二跳 vz 394 / 水平约 500、下蹲 ×0.8、追踪移动目标（M8 R2）；放置、视野门、视线门、无距离门（M9 R）。窗口晚端和几处非单调结果是 [unk]，用设计值。
- **成本**：R5 已够；Unity **M**。**本地可触发**：真实战术和 EVAL 捷径都能用。

### C2 Pathfinder 钩爪：技巧核验和精修（S0 引入）
- **独特原理**：玩家主导的拉拽与出手时机，社区技巧极多（技巧库目前**一条都没收**，这是资料缺口）。
- **社区技巧**（apexmovement.tech 钩爪页，现版 [wiki]，输入都有文字，发现时间都早于 S21）：
  - **Jump / Drag Grapple**：打地面远点；连接后进入 coyote 窗口再跳（Titanfall 2 起，2016）。
  - **Slingshot**：约 45° 上方挂点，过中点时反向转视角和平移；wiki 称好的 Slingshot 峰值约 1200 u/s（2016-12 TF2 发现）。
  - **Grapple Hop**（2019-11 最早片段）、**Slide Grapple**（2021-07，Mokeysniper）、**Momentum Carry**。
  - **Super Grapple**：在钩子**回收途中**连接，拉力加速曲线变化，早段更快；**Rodeo Grapple**：绕细物体转圈。
  - 墙面 20 u 内不连接，20–27 u 自动脱钩 [wiki]。
- **冲突风险**：M4b 的 RF 模型说「没有钟摆，侧向速度被制动，没有 W 时转视角几乎不转向」，实测释放速度 474 / 612 / 804 u/s（244 / 394 / 694 u）。wiki 的 Slingshot 1200 峰值和 Rodeo「连续绕圈」与此**至少在量级上冲突**，不能直接信，也不能直接否定（现版 S27+ 数字、不同拉力参数）。
- **可复用**：`GrappleAbility`（RF 模型）、coyote 窗口、Zipline 交接、滑铲和 Lurch。
- **新增**：钩子回收状态（Super Grapple 需要）、钩爪触发 coyote 跳（需核验）、脱钩规则（仍未识别）、**动态锚点**（见下）。
- **动态锚点**：`BeginJetDrive` 已证明引擎能追踪移动实体；钩爪对移动实体、玩家的行为**未测**；Unity 需要「每命令更新目标 + 移动平台坐标系」，motor 目前没有站在移动平台上的能力 [unk]。数值只能是设计值。
- **证据**：静态锚点 meas；技巧 wiki（A 级文字，无 S21 数值）；动态锚点 unk。
- **成本**：R5 约 1 个会话（Jump/Drag Grapple 的 coyote、Super Grapple 回收中连接、Slingshot 峰值与 RF 对照、一个 Rodeo 圈）；Unity **S–M**（若 RF 与 wiki 冲突成立则需修模型，M）。**本地可触发**：原生钩爪，M4/M4b 已跑过；唯一风险是回收中连接要靠移动 + 瞄准精确触发。

### C3 Pathfinder Zipline Gun：玩家布绳（S0 终极）
- **独特原理**：玩家自己搭路线，不是单次冲量；把 M6-A/M8-A/M9-A 已经测透的 Zipline 骑乘规则（挂点、方向、重挂、跳离）直接变成**可部署设施**。和 Ash 路线工具、Octane 跳板是同一类「布置—使用」。
- **社区技巧**：Zip jump / crouch / carry、超级跳、Mid Air Interact、Mantle crouch、Float jump（库 §3.13–3.16，全是 S21 前，输入有文字）。**这些在地图绳上已经能做**，布绳只是让它们出现在任意位置。Zip dash、Stacked Zip dash、Grapple Hyper jump 属「已移除」页，**是否活到 S21 页面没说** [unk]，不要写进 Reference。
- **脚本事实 [src]**：`P:weapons/mp_weapon_zipline.nut` 726 行：同时最多 10 条、3 s 退还时间、端点自动脱钩距离 100 u。绳长上限、部署延迟在武器 `.txt`，**未读**。
- **可复用**：全部 `ZiplineAbility` 与地图 Rail；M9-A 的「抓点 + 提示 + 空中挂载」。
- **新增**：运行时创建 Rail（两端点校验：地面 / 墙、最大长度、遮挡）、部署 UI、数量上限、与 Octane 跳板共用一个「放置设施」基础类（还能给 C12 用）。
- **证据**：骑乘 meas 充分；部署规则只有源码，没测。**够像就行**，部署用设计值。
- **成本**：R5 约半个会话（可选：部署范围、绳长、挂载后和地图绳是否一致）；Unity **M**。**本地可触发**：[unk]；脚本绳由服务器创建，`Zipline_Find` 对脚本绳是否同样生效没验证，需要 1 个探针。

### C4 Newcastle Armored Leap / Castle Wall（S13 引入）
- **独特原理**：玩家指定落点的**路径式冲刺**（空中起飞 → 悬停 0.55 s → 砸向目标，砸地 2000–2500 u/s，被打断保留 35% 速度）[src]，同时在落点生成大墙。HSD 里没有「锁定目标点」的瞬发位移。
- **社区技巧**：没有成体系的运动技巧；[wiki] 只把终极墙列为 SG / 墙弹落脚平台（速度表 2453）。**证据不足**。
- **可复用**：C1 的运动学路径驱动（做完 C1 后成本大降）、`PhaseBreachAbility` 的瞄准流程、`TeleportAbility.ResolveTeleport`。
- **新增**：目标点选取（40 m 内、高度差上限）、三阶段状态、墙设施（与 C12 共用）。
- **证据**：src only；meas 无。**成本**：R5 约 1 个会话（若能触发）；Unity **M–L**。**本地可触发**：[unk]（SDK 孪生存在，需要装备终极并给目标）。
- **价值**：中；与 C1 相似度高，建议 C1 之后再看。

### C5 Octane 补全（Stim 细节、跳板细节）
- **已有**：Stim、跳板、二段跳、落地再跳。**缺口**：
  - 跳板升级 ×1.2（1150 → 1380）[src `sh_jump_pads.gnut`]，与「传奇升级」S20 引入有关；
  - 双发 / 再扔一块（现版基础，S21 是否有 [unk]，**当作 post-S21**）；
  - **天花板冲浪**（Mokeysniper，2021-01 前发现，S21 存在）和**跳板贴墙 / 跑墙**（现版写作「wallbug」）[wiki, comm]；
  - Stim 再按的锁定 [src `:115-125`]、`stim_sprint` 里 sprintspeed 282 已实测。
- **输入**：跳板的基本输入有文字；冲浪「朝天花板发射后按住前进，蹲下提高稳定性」，没有时间窗和角度数据 [comm B]。
- **可复用**：全部已有。**新增**：天花板碰撞响应（是否自然成立，取决于 motor 的碰撞滑动）。
- **成本**：R5 约半个会话（扔垫到低天花板下）；Unity **S**。**可触发**：M4 已用 EVAL 创建跳板，可触发。

### C6 Wraith Dimensional Rift（S0 终极）
- **原理**：成对静态传送门，穿过后沿 Wraith 原路径高速回放（脚本回放，关闭预测 [src]）。[wiki] 称加速随距离从 22% 升到 74%，且穿门保留二段跳（仅现版数字）。
- **风险**：玩家已因「和其他游戏能力重复」搁置 Loba；传送门和 Portal 类游戏更像。**建议先问用户**，不要先投入。
- **证据**：src + wiki，meas 无；dedi 回放不是 S21 原码（客户端不预测），MOVE-TRACE 不是物理真值（`m4/ABILITY-TRIGGERS.md` §4）。
- **成本**：R5 M；Unity M（成对设施 + `PhaseBreach` 路径 + `StimAbility` 加速）。

### C7 Ash 冲刺（Predator's Pursuit）— [post-S21]
- 官方在 S24（2025 年）加入；2025-02 冷却翻倍、S25 减到 8 s、S26.1 增到 12 s 并削弱方向、S29 回到 10 s 且速度 425 → 450 [wiki, 搜索摘要]。**S21 的 Ash 没有这个能力。**
- 本地脚本 `P:weapons/mp_ability_ash_dash.nut` 有 `ash_dash` 设置 mod、冲刺条；数值在 setfile，未读。M4 评估为「可触发，用 `+dodge` / 空中跳」。
- 原理：空中水平冲刺，通用度高，和 HSD 已有的 Fun 二段跳同类。**成本**：R5 S（1 个会话）；Unity S。需要用户明确同意以 [post-S21] 标签放进 Fun，**不进 Reference**。

### C8 Revenant 遗留（不是新候选，只记缺口）
- 取消输入没找到（脚本有 `OnWeaponTossCancel`）；空中起扑没测；长攀爬结束规则（光滑面 ≥ 1300 u 没找到，3 种设计都失败）；横向攀爬重挂 ×9、mini-bounce 未测 [wiki]。成本 S–M，收益低。

### C9 Horizon 遗留
- 升梯：2 s 重进封锁、10 s 到期弹出（M8-C 未建），S。**Black Hole** 是拉扯场（外圈 300 / 内圈 400 u/s 拉速 [src]），主要作用敌人，对自身位移的行为未知，**跳过**。

### C10 Valkyrie 遗留
- 喷气升级 mod（`glide_extra_fuel`、`extra_thruster`、`better_handling`）在脚本里 [src]，没测；**Skyward Dive 本地测不到**（dedi 无，服务器权威），**不建议**。

### C11 速度提升预设（Bangalore、Bloodhound、Conduit、Ballistic、Fuse、Seer）
- 全是 `StimAbility` 参数行：严重度 0.15 → ×1.30（M4 公式）。**缺的是触发事件**（被射击、命中敌人、队友倒地），HSD 无战斗。若要做，只能由「手动键 / 威胁区」触发。独特性 L，成本 S，**只作为预设表里的备注，不排期**。

### C12 可部署的运动落脚平台（Rampart 墙、Wattson 灯塔、Newcastle 墙、Caustic 陷阱）
- [wiki]：社区用它们做 SG、墙弹、Mantle cancel、取消落地硬直，输入沿用已有技巧。**没有新的运动原理**，只是「放置的碰撞体」。若做 C3 / C4，应该把放置基础类设计成能放通用碰撞体，这样几乎零成本。单独不排期。

### C13 Sparrow 墙面弹射 / 二段跳 — [post-S21，已部分使用]
- M8 R2 [meas]：攀爬中按跳 vz 670.82（升 300 u）、外弹 442.8，Gibraltar 对照只是普通墙跳。HSD 已用这组数字做 Revenant 的 **Fun 墙面弹射**（`m9/unity/M9B-UNITY.md`），二段跳与 M7-A 通用二段跳重叠。
- Sparrow 官方为 S25，**不是 S21**；Reference 里 Revenant 仍用 M3 弹跳。没有必要再单独做，只需把「ledge 感知高度」留作未测。

## 3. 历史与来源备注（后期内容、本地可触发）

| 内容 | 官方时间 | 本地构建 | 记录要求 |
|---|---|---|---|
| Ash 冲刺（Predator's Pursuit） | S24（2025），冷却和速度数次调整 | 脚本、`ash_dash` mod、冲刺条都在；M4 估计可触发 | 进库时标 [post-S21]，来源 wiki + 脚本；S24 原值 [unk] |
| Sparrow（二段跳、攀爬跳） | S25（2025） | `PAS_SPARROW` 脚本 + SDK `wall_launch_math.h`；M8 R2 已测 | 本地实测值可用，但标 [post-S21]；SDK 是社区重写，不是官方原码 |
| Axle（原名 Overdrive）：Nitro Gate、滑铲被动 | S29（2026-05-05） | `P:weapons/mp_ability_overdrive_tac_slide_gate.nut`、`PAS_OVERDRIVE`、SDK `slide_super_jump.cpp`；**从未测** | 不评估；以后若要滑铲族新原语，才回头看 |
| Echo 免视线、Echo dash / TS / Echolevator | S22（2024-08-06）及以后 | 本地脚本仍是 S21 门（60° + 视线，默认开） | Reference 保持 S21 门；后期技巧只放 Fun 或不做 |
| 官方 Mantle Boost | S27（2025-11） | R5 的 SDK 状态机里有（M8：SG 出口 388.7 与原生 460 之分） | 已记为回移植（技巧库 §1） |
| 钩爪第二发、Pathfinder Landing Gear、跳板双发、三段跳 | 2026 年（S29 中期、冬季活动） | 本地无证据 | 现版 wiki 说法，**不是 S21** |
| 传奇升级系统 | S20（2024-02） | `PAS_ULT_UPGRADE_ONE` 等已在脚本里（跳板 ×1.2） | S21 存在；做成参数层可行，不要把现版整合的升级写成基础 |
| 钩爪冷却 / 第二发、Wraith Void Jumper 二段跳、Seer 终极二段跳 | 后期 | wiki 提及 | 不进 S21 Reference |
| Instagib 铁轨跳（`mp_ability_instagib_railjump`） | 限时模式 | 脚本存在 | 非传奇，不评估 |

以上「本地脚本」说明：本地所谓 `s21-platform` 脚本明显含后期内容（Axle、Sparrow、frag drone、perks），所以**脚本里有 ≠ S21 内容**，每个候选都要回到官方时间核对。

## 4. 下一批排序建议（前 5）

| 排名 | 候选 | 理由 | 成本 | 主要不确定 |
|---|---|---|---|---|
| 1 | **C1 Vantage Echo**（M9-C，已在计划里） | 证据是候选里最完整的；独特（受控路径飞行，追踪移动目标）；产出的运动学路径驱动是 C4、动态钩爪锚点的共用底座 | R5 已够；Unity M | 二跳窗口晚端、非单调点用设计值；Echo 目标系统做简化版（无 AI） |
| 2 | **C2 Pathfinder 钩爪技巧核验 + 精修** | 技巧库的最大缺口；先做 A3 式核验（同输入是否出同轨迹），RF 与 wiki 冲突很可能暴露物理模型问题，价值高；不新增状态 | R5 约 1 会话；Unity S–M | wiki 数字非 S21；Super Grapple 回收中连接能否稳定触发 |
| 3 | **C3 Zipline Gun 玩家布绳** | 复用 M9-A 全部 Zipline 成果；设施化后所有 Zipline 技巧在任意位置可练；和 Ash 路线工具、跳板同族 | M；先做 1 个 R5 探针 | 本地脚本绳是否走同一套 Find；部署参数只有设计值 |
| 4 | **C5 Octane 补全** | 便宜（S），全是已有部件；天花板冲浪是真技巧（S21 前存在）；顺手把「传奇升级」做成参数层 | S | 冲浪是否由 motor 碰撞自然产生 |
| 5 | **C4 Newcastle Armored Leap**（有条件） | 在 C1 完成后成本降到 M；独特（指定点位移）；但证据只有源码 | M–L | 本地能否触发；价值不确定。**建议 C1 完成、用户确认后再决定** |

**需要先问用户的**：C6 Wraith 传送门（可能因与其他游戏重复被否）；C7 Ash 冲刺（post-S21，是否接受以 Fun 标签放入）。

**明确搁置或跳过**：
- Loba、Alter：继续搁置，无新事实（Alter 唯一的新信息是它确实是 S21 新传奇，不改变搁置理由）。
- Valkyrie Skyward、Horizon Black Hole：本地测不到或主要作用敌人，跳过。
- Axle / Overdrive、Sparrow 作为独立传奇：后期内容，不做；Sparrow 的数字只保留为 Revenant 的 Fun 参数。
- Bangalore、Bloodhound、Conduit、Fuse、Seer、Ballistic 的加速：没有触发事件，只在预设表里备注（C11）。
- Catalyst、Maggie、Mirage、Gibraltar、Caustic、Lifeline、Wattson、Rampart、Crypto：无自身机动；Rampart / Wattson / Newcastle 的墙作为落脚平台归 C12，不单做。
- Lifeline 滑翔 / drone rider：来源和版本不明，先不评估。

## 5. 不确定之处

1. 赛季号：Ballistic（S17）、Alter（S21）只有 1–2 个来源（另有多个报道确认 S21 登场 Alter），Sparrow S25 / Axle S29 / Ash 冲刺 S24 来自搜索摘要，没逐条核官方补丁说明。
2. apexmovement.tech 是现版 wiki（2026）；Super Grapple、Rodeo、Slingshot 的文字没有 S21 数值，发现时间只给「首发前几天」。我没有看任何视频。
3. 技巧库原文不含钩爪、Octane、Wraith、Horizon、Valkyrie；C2、C5 的技巧来自本次直接读到的 wiki 页，**没有进库**，需要 D 轨补条目（作者、时间、证据级）。
4. 本地可触发性：C3、C4、C6 标 [unk]，没有证据，建议排期前各做一个 0.5 天探针。
5. Conduit 被动的加速幅度、跳板双发是否 S21 存在、Lifeline 滑翔的版本，都没查到。
6. 成本是估计，没有读 HSD-Unity 源码，只读了研究仓库里的 Unity 说明文档。
