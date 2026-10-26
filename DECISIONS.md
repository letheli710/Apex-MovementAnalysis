# 项目日志：重要节点和决定

High Speed Doom × Apex 移动机制项目的总日志，写给人读的。这里记三类东西：

- **节点**：一个阶段做完了、一个大改动进了主线、基线数字变了；
- **决定**：你选了哪个方案、走哪个分支、改还是不改（编号 D-xx）；
- **还没结论的事**：记录里写着"等你决定"、后来没看到结论的。

怎么读：先看"现在的状态"，再按日期往下看时间线；想知道某个决定的来龙去脉和"去哪里改"，查"决定总表"。

怎么记（以后的规则）：
- 每次你做了决定，或者有大的节点，在同一个 PR 里追加到时间线和总表；越新越靠下，编号接着往下排，不改旧编号。
- 决定被推翻时**不删旧条目**：旧条目标"已被 D-xx 取代"，新的另起一条。
- "怎么改"写开关或文件的位置。游戏里能直接切的写菜单 / 按键；代码里的开关大多在 `HSD-Unity/Assets/HSD/R5Replay/Runtime/MovementConfig.cs` 的 `MovementConfigs.Reference()` / `Fun()`（下文简称"Reference / Fun"），Fun 默认继承 Reference。
- 技术细节不写在这里，写在各阶段报告和技能文件夹的 README，这里只放链接。

几个词：
- **Reference**：按 R5 实测和原生代码做的游戏身体，默认配置。**Fun**：在 Reference 上加 HSD 自己设计的东西（跑墙、二段跳等），数值是设计值。
- **回放电机**：用来逐命令复现 R5 录像的电机，和基线保持逐字节相同，一般不改。下面的改动除非特别说明，都只改游戏身体。
- **[meas] / [native] / [design]**：数值来自实测 / 原生代码 / 我们自己的设计。

更早、更细的技术过程（英文，2026-10-20 到 10-23）在 [EXECUTION-LOG.md](EXECUTION-LOG.md)；各阶段一览在 [research/phase2-local/STATUS.md](research/phase2-local/STATUS.md)。这两份从 2026-10-26 起不再更新，新的内容都记在这里。暂缓的设计问题：[DEFERRED-DESIGN-TODO.md](DEFERRED-DESIGN-TODO.md)；搁置的能力：[SHELVED-ABILITIES.md](SHELVED-ABILITIES.md)。

---

## 现在的状态（2026-10-26）

- **R5 实测和 Unity 复刻**：M0–M10 全部完成并合并。基础移动、lurch / tap strafe、攀爬 / 翻越 / superglide、滑索、各传奇能力（Pathfinder、Octane、Horizon、Valkyrie、Ash、Revenant、Vantage、Wraith、Zipline Gun）都在 Unity 里。
- **原生代码研究（N 系列）**：N0–N11 完成。用 Ghidra / Frida 读 r5apex 的原生移动代码，和实测逐项对照（对照表 [research/rea-native/CROSSCHECK-LEDGER.md](research/rea-native/CROSSCHECK-LEDGER.md)）。认可的差别都改进了 Reference。
- **B 系列**：B1（S27 翻越加速移植）完成。
- **手感对照（F 系列）**：不靠试玩，用同样的 R5 输入把 Unity 和 R5 叠在一起比指标。平地 511 / 513 项一致；攀爬 / 翻越 / superglide 1968 / 2221。叠图页面：https://claude.ai/artifact/P1mjgrbW1Yoiu9HdukTbDv
- **基线数字**：EditMode 2108 / 2108，PlayMode 1 / 1；M2/M1、M3、M4 回放和基线逐字节相同；真实按键演示 238 / 238；课程单圈 79.12 s。
- **下一步候选**：手感对照第 3 批（技能：跳板、升梯、钩爪、兴奋剂、Valkyrie）、第 4 批（镜头曲线）；见最后一节"还没结论的事"。

---

## 时间线

### 2026-10-20：搭环境，跑通第一个自动循环（M0–M3）
- **M0**：本地 R5Flowstate 跑通，基线定在训练场、Gibraltar、空手（移动倍率 1.15）。
- **[D-01]** Unity 工作改到工作区里的新工程，原来的 `High Speed Test 01` 只读、作废。
- **M1**：做出 AgentLink 自动跑测脚本，按帧发输入，不用抢窗口焦点；Unity 回放管线第一次跑通（误差 32 u）。新建私有仓库 `letheli710/HSD-Unity`。
- **M2**：17 种基础条件，每种至少 5 次有效数据，做出参数表（地面加速、减速、跳跃、滑铲）。Unity `R5MotorV2` 终速误差 0.000 %，M1 误差从 32 u 降到 1.4 u。
  - 发现训练场每次会话随机分配传奇，测试脚本改成固定 Gibraltar。
- **M3**：lurch 模型（0.2 s 全强度、0.5 s 消失、上限 209.3）、蹬墙、翻越、翻越加速窗口（最后 133 ms）。
  - **[D-02]**（主控定的）外部有约 138 fps 的帧率上限，从 M3 起客户端固定 120 fps，帧率当成实验变量。

### 2026-10-21：传奇能力、第一版可玩版本、镜头（M4–M6）
- **M4**：7 类传奇移动原件进 Unity（兴奋剂、跳板、升梯、喷气、钩爪、落地减速、Horizon 空中参数）。
  - **[D-03]** 加 M4b（你同意加）：测试脚本补上逐命令转视角，测钩爪摆动。结论：钩爪不是钟摆，是"沿绳加速 + 横向刹车"。
  - **[D-04]** 报告用词：研究对象是 R5Flowstate S21，不是官方版本；tap strafe 只算单次按键的 lurch；superglide 变种没测；墙和翻越只有公式和单元测试。
- **M5**：技能槽、Reference / Fun 两套配置、练习地图、第一版可玩版本 `HSD-Build\HSD-Practice.exe`。最终报告 FINAL-REPORT.md。
- 你试玩第一版：移动核心可以，但没有第一人称反馈，动作很难感觉到 → **M5.5** "移动反馈和可玩性"：镜头、滑铲反馈、钩爪状态、能力实体、一键演示。
  - **[D-05]** 你认可 M5.5 镜头（"自然、流畅…操控起来很舒服"），方法写成 `fps-camera-design` skill。
  - **[D-06]** M5.5 定为主线：两个仓库都从这里建 `main`。
- **M6-A**：lurch / tap strafe 细节、攀爬 / 翻越 / superglide（原生 460）、滑索（Super Jump 存在）。
- **M6-B 研究**：Valkyrie、Ash、Loba、Alter（Alter 在本地触发不了，只有源码结论）。
  - **[D-07]** 只做 Valkyrie 喷气和 Ash 相位突破；Loba、Alter 搁置。同时你加了要求：不再做新的逆向、Reference / Fun 严格分开、Ash / Valkyrie 边界测试、四个组合、两种验收标签分开写。
- **M6-C**：组合训练场（J–P 段）、自动驾驶跑圈 80.82 s、F9 / F10 反馈记录。

### 2026-10-22：HSD 原创动作和移动库（M7–M9）
- **M7-A**：跑墙、抓边悬挂、二段跳。
  - **[D-08]** R5 S21 都没有，算 HSD 设计：Reference 关、Fun 开，游戏内可以切。
- **M8**：移动库（跳跃键仲裁、斜坡滑铲、滑索修正、兔跳 / lurch / superglide、跳板二段跳、Horizon），同时三条线并行：R5 实测、资料研究、Unity。
  - 留给你的问题：LS / RAS 参考视频、跳跃输入缓冲、Fun 斜坡、两种二段跳、下一批（后三项见 D-09 / D-13）。
- **M9**：滑索修正（你报的问题：Reference 原来拒绝所有空中上绳，是 M6 的错规则）、身法资料库、Revenant、Vantage。
  - **[D-09]** E1 两种二段跳能否同时装备、E2 Fun 斜坡 1.6 倍加速度、E3 跳跃输入缓冲：先不决定，到游戏接近完成时再看。
- **M10 计划**：
  - **[D-10]** 跳板起飞后能不能 lurch：Reference 按 R5（不能），Fun 保留 M5.5 的行为。
  - **[D-11]** Ash 冲刺不做。
  - **[D-12]** Wraith 传送门做（M10-W）。

### 2026-10-23：M10 完成，开始原生代码研究
- **M10**：Pathfinder 钩爪按 72 次实测拟合、Zipline Gun、Octane（兴奋剂、跳板、天花板滑行）、滑铲规则修正、按键输入层、Wraith 传送门和相位。
  - **[D-13]**（主控定的规则，你可以推翻）S21 客户端和本地服务端结果不一致、又有社区证据时，Reference 跟客户端。
  - 课程单圈 80.82 → 80.55 s（松开下蹲结束滑铲的实测规则）→ 78.98 s（修了反向输入不减速的缺陷）。两次都有解释。
  - 回放电机没有换新滑铲规则，保持基线（见"还没结论的事"）。
- **[D-14]** M10-R：技能代码改成一个技能一个文件夹，每个文件夹一份中文 README，以后新技能也照这样。
- **[D-15]** 新的优先级：做完整的**原生移动系统地图**，用 REA / Ghidra 解释实测，对不上的进对照表。对 Unity 的修改建议先记下来，等实测确认后你再统一决定；Agent 不能自己改 Unity。
- N0–N5：原生地图、ConVar 默认值、对照表、修改建议清单。
- **[D-16]** 之后的顺序：N6 补测 → N7 把建议改进 Unity（每项你批准、只改 Reference）→ N8 传送研究放最后。

### 2026-10-24：按原版改 Reference，镜头换原生，S27 翻越加速
- N6 补测：钩爪"转开视角就脱钩"的规则、空中超时等。
- **[D-17]** N7：12 项修改建议全部按原版改（"全部改成原版"）。课程单圈 78.98 → 79.12 s。
- N7 试玩后你感觉不出差别 → 继续研究，开始 N8 传送。
- **[D-18]** N8-CAM：镜头默认改成原生，M5.5 镜头原样保留，可以切回去。
- N8：五个传送类能力共用一个原生相位状态；Alter 的绝招门要第二个玩家才能触发。
- **[D-19]** N8-E：相位中不被跳板弹起；重新进入间隔 1.0 s；旧传送门预设标成设计。
- **[D-20]** B1：把 S27 的翻越加速（准星上的 BOOST 圈）移植进来；你喜欢这个手感。之后加固：调参数也不会把它弄坏。
- 传奇选择页面（L 键），加了 Horizon、Valkyrie、Ash、Revenant 四套 S21 配置。
- N9：升梯、喷气、重力炮的原生代码。

### 2026-10-25：原生细节收尾，开始手感对照
- **[D-21]** N9 决定：相位中不受升梯影响；重力炮不做。
- **[D-22]** 蹲着翻越的时长按 R5（更长）。
- N11：superglide 402 的来源找到了（原生起跳时朝最后碰到的墙推 30 u/s）。
  - **[D-23]** J-1：按原版加上这 30 u/s。
- **[D-24]** N10 镜头：跑步晃动加偏航、滑索侧倾。
- **[D-25]** 手感不靠试玩了（没有动画，感觉不可靠），改成用同样的 R5 输入把 Unity 和 R5 叠在一起比指标。第 1 批（平地，67 个片段）。
  - **[D-26]** F-1：滑铲跳退还的时间边界按 R5 改。平地 511 / 513 一致。

### 2026-10-26：手感对照第 2 批（攀爬、翻越、superglide）
- 494 个 R5 片段，找到 C-1 到 C-5 五处差别。
  - **[D-27]** C-1 台沿探测死区：修（是 bug）。
  - **[D-28]** C-5 走路翻越出口：按 R5（走路速度 199.5）。
  - **[D-29]** C-2 superglide 窗口前沿：先决定保持简化。**已被 D-31 取代。**
  - **[D-30]** C-3、C-4：不改。
  - **[D-31]** C-2 推翻 D-29：按 R5 做减量 superglide（原来的判断用错了时钟，见总表后的说明）。
  - **[D-32]** 两种 superglide 都保留：原生（跳 + 蹲，460）和 S27 翻越加速（只按跳，388.7），菜单里切。
- **[D-33]** 建这份日志：以后所有节点和决定都记在这里。

---

## 决定总表

| # | 日期 | 主题 | 决定 | 怎么改 | 记录 |
|---|---|---|---|---|---|
| D-01 | 10-20 | Unity 工程位置 | 在工作区里新建 Unity 工程；原来的 `High Speed Test 01` 只读，作废 | — | EXECUTION-LOG 10-20 |
| D-02 | 10-20 | 实测帧率（主控定的） | 客户端固定 120 fps（外部约 138 fps 上限之下，稳定）；帧率当实验变量 | `research/phase2-local/tools/hsd_launch.ps1` 的启动参数；会话里的 `fps_max` | EXECUTION-LOG 10-20 |
| D-03 | 10-21 | 加 M4b | 加：测试脚本补上逐命令转视角，测钩爪摆动 | — | M4-REPORT §5 |
| D-04 | 10-21 | 研究范围和用词 | 以 R5Flowstate S21 为准，不是官方版本；tap strafe 只算单次按键 lurch | — | M4-REPORT |
| D-05 | 10-21 | M5.5 镜头 | 认可；方法写成 `fps-camera-design` skill，以后每个新动作可以有自己的镜头语言（复用方法，不复用数值） | 镜头模型见 D-18 | HSD-Unity#6、#7 |
| D-06 | 10-21 | 主线 | M5.5 定为主线，两个仓库都从这里建 `main` | — | EXECUTION-LOG 10-21 |
| D-07 | 10-21 | 做哪些传奇能力（M6-B） | 只做 Valkyrie 喷气和 Ash 相位突破；Loba、Alter 搁置。不再做新的逆向（后来被 D-15 改了）；Reference / Fun 严格分开 | — | SHELVED-ABILITIES.md，HSD-Unity#10 |
| D-08 | 10-22 | 跑墙、抓边悬挂、二段跳（M7-A） | R5 S21 没有，算 HSD 设计：Reference 关，Fun 开 | 游戏内 `7` / `8` / `9`；`MovementConfig.hsd`（`HsdMovementParams.Off()` / `.Fun()`） | HSD-Unity#11 |
| D-09 | 10-22 | 三个设计问题暂缓 | E1 两种二段跳能否同时装备、E2 Fun 斜坡滑铲 1.6 倍加速度、E3 跳跃输入缓冲：先不决定 | 见清单 | DEFERRED-DESIGN-TODO.md |
| D-10 | 10-22 | 跳板起飞后能不能 lurch | Reference 按 R5：不能；Fun 保留 M5.5 的"跳板 → lurch" | `padLaunchOpensLurchWindow`：Reference false，Fun true | HSD-Unity#18 |
| D-11 | 10-22 | Ash 冲刺 | 不做 | — | M10-REPORT |
| D-12 | 10-22 | Wraith 传送门 | 做（M10-W） | — | HSD-Unity#22 |
| D-13 | 10-23 | S21 客户端和本地服务端不一致时（主控规则，你可以推翻） | Reference 跟 S21 客户端（有社区证据时），标 [S21-client] | 天花板滑行：`p.ceilingSurf`（Reference true）；钩爪转开视角脱钩 | M10-REPORT |
| D-14 | 10-23 | 技能代码结构（M10-R） | 一个技能一个文件夹，每个文件夹一份中文 README；新技能也照这样 | `Assets/HSD/R5Replay/Runtime/Abilities/<技能>/` | HSD-Unity#24 |
| D-15 | 10-23 | 原生代码研究 | 做完整的原生移动系统地图解释实测；对 Unity 的建议先记下，实测确认后统一决定，Agent 不能自己改 Unity | 建议清单 `research/rea-native/UNITY-CHANGE-PROPOSALS.md` | research #29–#40 |
| D-16 | 10-23 | 原生研究的顺序 | N6 补测 → N7 把建议改进 Unity（每项批准，只改 Reference）→ N8 传送研究最后 | — | research rea-native |
| D-17 | 10-24 | N7：12 项修改建议 | 全部改成原版：地面摩擦和加速、空中额外加速、滑铲加成冷却 2 s（从上次滑铲开始算）、滑铲跳下限、滑铲转向等 | 各项都是 Reference 里的 `[NonSerialized]` 开关，清单见 `research/rea-native/n7/N7-UNITY.md` | HSD-Unity#25，research #43 |
| D-18 | 10-24 | 镜头改成原生（N8-CAM） | 默认用原生镜头；M5.5 镜头原样保留在 `Camera/M55/`，可以切回去 | 游戏菜单"Camera model"（PlayerPrefs `hsd.m55.` 下）；代码 `Game/Runtime/Camera/CameraModels.cs` | HSD-Unity#26，research #46 |
| D-19 | 10-24 | 传送类能力（N8-E） | E-1 相位中的身体不被跳板弹起；E-2 / E-3 重新进入的间隔 1.0 s；E-6 旧传送门预设标成设计；E-4、E-5 保持不变 | `padPhasedNoLaunch`（Reference true）；`DimensionalRiftAbility` 的 `reuseDebounce` 1.0；`PhaseBreachParams.reentryDebounce` 1.0 | HSD-Unity#27，research #49 |
| D-20 | 10-24 | S27 翻越加速（B1） | 移植进来；你喜欢这个手感 | 游戏菜单"Mantle boost (B1, S27 port)"，默认开（PlayerPrefs `hsd.b1.mantleboost`），只影响正在玩的身体；`SuperglideMode.MantleBoostS27` | HSD-Unity#28、#29，research #50、#51 |
| D-21 | 10-25 | 重力升梯和相位（N9） | 相位中的身体不受升梯影响；标签改成 [native]；重力炮不做（项目里用不到） | `liftPhasedNoLift`（Reference true） | HSD-Unity#32，research #53、#54 |
| D-22 | 10-25 | 蹲着翻越的时长 | 按 R5：蹲姿开始的翻越更长（0.517 / 0.625 / 0.813 s） | `crouchedMantleTime`（Reference true，Fun 继承） | HSD-Unity#32 |
| D-23 | 10-25 | J-1：起跳朝墙推 30 u/s | 按原版：起跳时朝最后碰到的墙面推 30 u/s（superglide 402 的来源） | 电机 `p.jumpSurfacePush`（Reference 30，回放电机 0） | HSD-Unity#33，research #55 |
| D-24 | 10-25 | N10 镜头 | C-10 跑步晃动加偏航（步长 0.280 s）；C-11 滑索侧倾按原版 A 分支 | 原生镜头 `Game/Runtime/Camera/Native/` | HSD-Unity#34，research #56 |
| D-25 | 10-25 | 手感怎么验收 | 不靠真人试玩，改成用同样的 R5 输入把 Unity 和 R5 叠在一起比指标 | 叠图页面（见"现在的状态"）；脚本 `research/feel/` | HSD-Unity#35，research #57 |
| D-26 | 10-25 | F-1：滑铲跳退还的时间边界 | 按 R5：下蹲过渡从下一条命令开始算（0.201 s 退还，0.215 s 不退还） | `p.slideDuckTransitionFromNextCommand`（Reference true） | HSD-Unity#35 |
| D-27 | 10-26 | C-1：台沿探测死区 | 修（是 bug）：墙顶在 80–98 u 时不再"既不翻越也不攀爬" | 没有开关，`MovementWorld.ProbeLedge`，所有游戏身体都受影响 | HSD-Unity#37，research #59 |
| D-28 | 10-26 | C-5：走路翻越的出口速度 | 按 R5：没按冲刺时出口是走路速度 199.525 | `mantleExitWalkSpeed`（Reference true，Fun 继承） | HSD-Unity#37 |
| D-29 | 10-26 | C-2：superglide 窗口前沿（第一次） | 保持简化，不做斜坡。**已被 D-31 取代** | — | research #59 |
| D-30 | 10-26 | C-3、C-4 | 都不改：C-3 翻越时长公式和 R5 一致；C-4 走路 superglide 402 由命令内部碰墙时刻决定，模拟不了，取多数结果 200 | — | research `feel/FEEL.md` §6.4 |
| D-31 | 10-26 | C-2：superglide 窗口前沿（推翻 D-29） | 按 R5 做减量 superglide：离翻越结束 102.5–117 ms 按跳且按着蹲，照样起跳，水平 385 → 425；Fun 不做 | `superglideReducedBand`：Reference 0.015，Fun 0（0 = 关） | HSD-Unity#38，research #60 |
| D-32 | 10-26 | 两种 superglide | 都保留：原生（跳 + 蹲，460）和 S27 翻越加速（只按跳，388.7）。两者互斥，S27 打开时拿不到 460 | 同 D-20 的菜单开关；测试、回放、手感对照都按原生 | HSD-Unity#39 |
| D-33 | 10-26 | 项目日志 | 所有重要节点和决定都记在这份文件；EXECUTION-LOG 和 STATUS 不再更新 | 本文件 | research #61 |

**D-29 → D-31（C-2 为什么推翻）**：第一次决定时以为 Unity 的 102.5 ms 窗口已经盖住了 R5 的减量段，所以"简化 = 不改代码"。后来按 Unity 自己的翻越时钟重排（Unity 的翻越比 R5 长约 25 ms），发现减量段其实在窗口外面，原来的 Reference 在这段是"切到台面"，并不是"给完整 460"。你随后要求继续做 C-2 并合并。细节见 `research/feel/FEEL.md` §6.4 和 `Climb/README.md`。

**D-20 / D-32 和 D-31 的关系**：游戏里默认开着 S27 翻越加速，这时 superglide 走 S27 规则，D-31 的减量段看不到；在菜单里关掉 S27 才是原生 superglide。

**D-07 和 D-15**：M6-B 时你说过不再做新的逆向；10-23 你把原生代码研究定成新的优先级，之后的 N 系列就是按这个做的。

---

## 还没结论的事

记录里写着"等你决定"、后来没看到明确结论的。要么还没定，要么定了没记下来，回顾时请确认：

- **回放电机要不要换成 M10 的新滑铲规则**：换了会让 2 个 M3 滑铲连招片段更准，但回放基线会变。（M10）
- **F-2**：一次原地跳 Unity 比 R5 高 1.8 u（两套电机都是）。（F1）
- **LS / RAS**：有没有具体想复现的视频？社区对这两个名字的定义不一致。资料库里有"待看清单"，如果你看了告诉我实际按键，可以提高证据等级。（M8、M9）
- **旧的 "Revenant-Wraith" 配置**要不要升级到新的 Revenant 能力？（M9）
- **N10 剩下的镜头项目**：CAM-18 / 19、冲刺和钩爪侧倾的补测。
- **钩爪侧倾**：钩爪攀在对手身上（rodeo）时，实测侧倾 13.9°，公式给 18.5°，差距没查。（N10）
- **手感对照的下一批**：技能（跳板、升梯、钩爪、兴奋剂、Valkyrie）、镜头曲线。
- 暂缓清单里的 E1–E3 见 [DEFERRED-DESIGN-TODO.md](DEFERRED-DESIGN-TODO.md)。
