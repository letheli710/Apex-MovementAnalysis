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

## 现在的状态（2026-10-28）

- **R5 实测和 Unity 复刻**：M0–M10 全部完成并合并。基础移动、lurch / tap strafe、攀爬 / 翻越 / superglide、滑索、各传奇能力（Pathfinder、Octane、Horizon、Valkyrie、Ash、Revenant、Vantage、Wraith、Zipline Gun）都在 Unity 里。
- **原生代码研究（N 系列）**：N0–N11 完成。用 Ghidra / Frida 读 r5apex 的原生移动代码，和实测逐项对照（对照表 [research/rea-native/CROSSCHECK-LEDGER.md](research/rea-native/CROSSCHECK-LEDGER.md)）。认可的差别都改进了 Reference。
- **B 系列**：B1（S27 翻越加速移植）完成。
- **手感对照（F 系列）**：不靠试玩，用同样的 R5 输入把 Unity 和 R5 叠在一起比指标。平地 511 / 513 项一致；攀爬 / 翻越 / superglide 1968 / 2221；技能 477 / 524（按每个片段每个指标的第一项算，同口径改之前是 473）；镜头 325 / 367（不含待定的 K-5 / K-6）。叠图页面：https://claude.ai/artifact/P1mjgrbW1Yoiu9HdukTbDv
- **基线数字**（RPS 起）：EditMode 2156 / 2156（GN + RUD），PlayMode 1 / 1；M2/M1、M3、M4 回放按新基线 [research/phase2-local/rps](research/phase2-local/rps/README.md)（回放电机滑铲按原生；`-legacyM2` 和旧基线逐字节相同）；真实按键演示 238 / 238；课程单圈 78.88 s。
- **以 R5 为复刻核心**（D-36）：对照里找到的差别原则上改成 R5；改之前那一版和 R5 的差别存在 [R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)。
- **10-27 – 10-28 新做完的**（详见时间线）：F6 按 R5 复刻、N12 钩爪横滚查清、F7 横滚平滑改原生 + 二段跳反馈 + FOV、EPG 火箭跳实测、R6 斜坡滑铲实测、R6U 斜坡按 R5 改、RPS 回放电机滑铲换原生、RUD 回放电机碰撞体和地面移动、GN 钩爪脱钩全部按原生。最新 build：`HSD-Build\GN`。
- **下一步候选**：G-6 钩爪撞上上抬加不加（D-50）〔10-28 已定：先关着、留作待定，见 D-51〕；回放电机的 `airUnduckDrop` 要不要开〔10-28 已做完：D-49〕；K-5 起跳镜头、K-6 翻越镜头要不要做；K-7 滑索横滚再测一次；《泰坦陨落2》研究（D-48）。见最后一节"还没结论的事"。

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
- 手感对照第 3 批（技能，38 个 M4 片段）：按 R5 测试脚本的场景摆好跳板、升梯、测试墙，装上对应传奇。Reference 479 / 536 项一致（89 %）。
  - 兴奋剂、跳板、升梯、Revenant 猛扑、Valkyrie 喷气基本全部一致。
  - **A-1** 钩爪往墙上拉时，R5 拉到末尾竖直速度更大，最高点比 Unity 高 15–22 u。等你决定是否先补研究。细节见 `research/feel/FEEL.md` §7。
- 手感对照第 4 批（镜头，39 个 N6 / N10 / C3 片段）：R5 的 Frida 镜头记录和 Unity 原生镜头比俯仰、横滚、眼高。107 / 149 项一致（72 %）。第 3、4 批的工具和结果已合并（HSD-Unity#40，research #62）；Unity 玩法没有改。
  - 落地 kick 的时间、滑铲（眼高、FOV、横滚）、转向横滚全部一致。
  - **K-1** 900 u 大落差落地的俯仰 kick，Unity 32° 比 R5 的 34–43° 小约 20 %。
  - **K-2** 96–400 u 落地的横滚，Unity 0.1–0.45° 比 R5 的 0.45–2° 小。
  - **K-3** 跑步晃动俯仰幅度三个 R5 会话彼此就不一样（0.53 / 0.60 / 0.73°，Unity 0.67°），先不算差别。
  - 翻越的镜头没有 R5 记录，要补测。细节见 `research/feel/FEEL.md` §8。

### 2026-10-27：按 R5 复刻（F6）
- 你的决定：A-1 先补研究；K-1、K-2 记下现在、R5、Unity 各是什么样，然后做一个以 R5 为复刻核心的版本，以后的 Unity 都用它；把现版本和 R5 不一样的地方存档；K-3 补测；把没覆盖到的（翻越镜头、滑索横滚、直线滑铲）补上对照。
  - **[D-34]** A-1 补研究后按 R5 改钩爪：原生拉力的横向刹车（向下和朝视线的部分不刹），钩子从真实眼高打出。最高点差距 15–22 u → 5–10 u。
  - **[D-35]** K-1 / K-2：落地 kick 用 R5 自己的随机数（落地命令号 → MD5 → 种子混合 → 随机数，Frida 在 R5 里 8 / 8 对上）。用 R5 的命令号重放时每次落地都对上。
  - **[D-36]** 以 R5 为复刻核心：以后对照找到的差别原则上改成 R5；改之前那一版和 R5 的差别存档在 [R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)。
  - **[D-37]** K-3 补测（同一会话 5 次直线冲刺）：每步峰峰 0.50°，三个旧会话其实一致（原来的指标把慢漂移算进去了）。按 D-36 改成 R5：幅度 0.335 → 0.25，第一步就有。
  - **[D-38]** 补对照时新发现 K-4 眼高：R5 站立 70、冲刺时降 6（Unity 原来一直 64）。按 D-36 改成 R5，钩爪也用这个眼高。
- 补上的对照：翻越镜头用 B1 会话（已经有镜头记录，之前漏了）；直线滑铲 3 次（之前转换时被帧率检查挡掉）；滑索 11 次（Unity 那边加上了绳子）；新会话 F6_seed（8 次原地跳 + 5 次直线冲刺，同时用 Frida 记 kick 的种子）。
- 结果：镜头原来的 13 个指标 188 / 211 一致（之前 107 / 149）；眼高、滑索 137 / 156；技能 477 / 524。
- 另外三条决定（同一天，在另一个会话里）：
  - **[D-39]** 旧的 "Revenant-Wraith ground" 预设：当历史保留，配置不动；现在用的是 Revenant S21 / Wraith S21 两套。
  - **[D-40]** LS / RAS：没有具体要复现的视频，Reference 保持原生 lurch 模型（已经做完）。
  - **[D-41]** "N10 剩下的镜头项目"这条早就做完了（N10，research #56），从待定里划掉。
- 新的待定：**K-5** 起跳时镜头先向下再向上（跟着跳跃弧线），Unity 没有；**K-6** 翻越 120 u 墙时镜头向下约 5°，Unity 没有；**K-7** 两次 R5 会话的滑索横滚不一样。都没改，等你决定。细节见 `research/feel/FEEL.md` §9。

### 2026-10-27：钩爪 rodeo 横滚 13.9° 对 18.5° 查清（N12）
- 起因：N10 留下的待定"rodeo 实测 13.9°、公式 18.5°"，你让开会话去查。报告：[research/rea-native/n12/N12-RODEO-ROLL.md](research/rea-native/n12/N12-RODEO-ROLL.md)（research #66）。只做研究，Unity 没改。
  - **结论：差距来自我们自己的重算脚本，原生公式没有漏项，实测也没错。** 脚本有两处和原生不一样：
    - 平滑：脚本用一阶指数（每秒 6.667），原生是临界阻尼弹簧 SmoothCD（ω 6.667，带速度状态），同样的 6.667 跟得慢得多（到 63 % 要 0.32 s，一阶只要 0.15 s）。单改这一项 18.98 → 17.5–18.0°。
    - 门控：脚本从第一次挂上到最后一次挂上一直当作挂着；原生只在钩爪激活时算目标，脱钩那帧起目标是 0。单改这一项 → 17.8–17.9°。
    - 两项都按原生：13.69–13.87°，实测 13.86–13.94°，全程 rms 0.41–0.45°。12 次 rodeo 和"视线离开"试验全部对上。
  - 为什么"视线离开"那组以前看着一致：目标在 20° 封顶上停了约 0.5 s，弹簧追到了稳态，峰值差不多；rodeo 时视角 180 °/s 转，0.42 s 就因为"离开视角 90°"脱钩，弹簧没追上就没了目标。
  - **记录更正**：rodeo 不是"攀在对手身上"，是 M10 的 `m10_g_rodeo`：钩 M3 岩石后按住左移、视角左转绕钩点转圈。之前的日志写错了。钩到玩家的情况没测过；原生代码里没有针对玩家的分支，目标就是绳子末端那个点。
  - 原生：目标在 `Grapple_CameraRoll` 0x1407fac60（距离 0 → 150 u、视角 0 → 65°、封顶 20°）；门控和平滑在 `View_CalcRoll` 0x140afc480；钩爪、滑索、摆荡三个横滚共用一个平滑状态（玩家 +0x36d4 值、+0x36d8 速度）。滑索横滚用原生弹簧检验 rms 0.043°，Unity 当时的一阶 3.0 /s 是 0.083°。
  - 本地 S3 dedi 每约 0.1 s 把钩子重挂一次（N6 的"闪烁"），对这个峰值影响只有 0.2–0.3° [hyb]。
  - 带出的 Unity 建议（C-12：横滚平滑改原生）你批准了，在 F7 做（D-42）。

### 2026-10-27：横滚平滑改原生、二段跳反馈、FOV 设置（F7）
- 起因：N12（research #66）查清了钩爪 rodeo 横滚 13.9° 对 18.5° 的差距：是我们的平滑模型和门控不对，不是原生公式漏项。原生钩爪、滑索横滚共用一个临界阻尼弹簧。你批准按原生改。另外两件：跳板二段跳没有反馈；FOV 要能按 Apex 的数值调。
  - **[D-42]** 钩爪和滑索横滚的平滑改成原生：共用一个 SmoothCD 状态（ω 6.667），钩头飞行中也算目标，脱钩起目标为 0。旧版存档在 [R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)，开关 `nativeRollSmooth`。镜头对照新加了 14 个钩爪片段（N6、N12）：和 R5 的逐帧误差变小（rodeo rms 平均 4.8° → 3.0°，视线离开 8.6° → 6.7°），一致项数不变（钩爪 6 / 42、滑索 14 / 22、其他 333 / 367）。峰值现在比 R5 低（rodeo 11.4° 对 12.2–15.2°），原因是 Unity 的钩爪比 R5 早脱钩，不在镜头（镜头公式 N12 用 R5 自己的状态检验过，rms 0.24–0.45°）。细节 `research/feel/FEEL.md` §10。
  - **[D-43]** 跳板二段跳的反馈（只动表现层，数值不变）：准星下方显示倒计时 / `2J`（可用）/ `TOO EARLY`（按太早）/ `PAD 2J`（触发），触发时一声短音，原生镜头向下沉 1.2°（0.10 s 到最低，不回弹）。都是 [design]，等你试玩。
  - **[D-44]** FOV 设置：游戏菜单原来就能调，但显示的是竖直角（55–100）。改成按 Apex 的 FOV 数值显示和输入（4:3 水平角，70–110，整数），存 PlayerPrefs；默认仍是竖直 70°（= Apex 86）。原生滑铲 FOV 本来就是乘在 4:3 水平角上，跟着设置按比例走。
- Unity：EditMode 2123 / 2123，PlayMode 1 / 1；M2/M1、M3、M4 回放和基线逐字节相同（111 / 111 / 90，M4 114 / 114）；真实按键演示 238 / 238；课程单圈 79.12 s（不变）；build `HSD-Build\F7`。回放电机和游戏身体的物理都没变，三件事都只动镜头 / HUD。

### 2026-10-27：EPG 火箭跳实测
- 起因：Fuse 集束炸弹对脚下打能飞（S28 Knuckle Jumper，本地 S21 没有），改测攻略里说能推人的 EPG-1。报告：[research/epg/EPG-ROCKET-JUMP.md](research/epg/EPG-ROCKET-JUMP.md)。只做研究，Unity 没改。
  - 本地加载不了能开火的 EPG（引擎没这把枪的武器信息、缺模型、开火回调是空桩），改用服务端模拟开火 + 真手雷对照，29 个条件、每个 ≥5 次。
  - 爆炸推人是引擎原生击退。EPG 原版推力（30000）站着打推不动；《泰坦陨落》留下的 `jump_kit` 模式（65000）朝脚下打 Δv ≈ 655，站着飞到 270 u，跳 + 开火同时按 486 u（普通跳 55 u）。
  - 护盾把伤害全吃掉就完全不推；会自伤（Gibraltar 55）；推力随距离和伤害一起衰减，速度上限约 1000。
  - 背景（网上资料）：Fuse 的 Knuckle Jumper 是 S28（2026-02-10）加的 2 级升级，Marked 中期（2026-09-14）改成基础技能并削弱了跳跃力；它是"在自己炸弹旁边按跳"的跳跃加成，不是爆炸冲击。本地 S21 的集束炸弹 `impulse_force` 为 0，测不了。EPG-1 是 S23 Split 2 的神话武器，攻略说"起跳同时朝地面开火"。
  - 时机（jump_kit，朝脚下 89°）：站着开火 270 u；同一帧跳 + 开火 486 u；先开火、3 帧后跳 492 u；跳后 0.05 / 0.1 / 0.2 / 0.4 s 开火分别 455 / 421 / 327 / 196 u。推力叠加在跳跃速度上，空中和地面一样大。
  - 角度和距离：俯视 89° 竖直 636 / 水平 174；70° 斜向后上方 490 / 441；45° 基本是水平冲刺（水平 525，只升 45 u）；30° 只剩一半；20°（落点离身体 198 u）为 0。离身体中心约 70 u 内满额，超过 180 u 为零。
  - 和移动组合：打在前进方向前面会刹车（冲刺跳 + 70°：297 → 126）；打在身后会加速（后退 + 70°：200 → 663）；滑铲中朝脚下打水平 363 → 680。
  - 地面门槛：推力 ≤ 31000 时站着的人一动不动，31500 起一下就是 266；EPG 原版 30000 刚好在门槛下面。护盾：只要有 1 点伤害进了血就全额推。
  - **[D-48]** 你决定：本地做不到"真的拿 EPG 开火"，这一项留到之后的《泰坦陨落2》研究里做（那边 EPG-1 是正常武器，用 Northstar 本地私服），和这次的模拟结果对照。《泰坦陨落2》的研究方向（铁驭机动、钩爪 slingshot、Gauntlet 训练场、和 Apex 的继承关系、战术技能、投掷物击退、泰坦机动、战役机制）先列在工作区根目录的 `TODO.md`，等 Apex 这边收尾后开始。

### 2026-10-27：斜坡滑铲实测（R6）
- R5 本地 133 次试验，5–40°，上坡 / 下坡 / 转折 / 横向：原生坡面公式 g·n_z·n_水平 逐命令成立，没有坡度门槛（M8 的拟合作废）；上坡减到 125 结束、不倒滑；转折处不离地；换地面实体时滑铲会再加速一次（原生 `SetGroundEntity` → `Slide_TryBegin`）。和 Unity 对照找到 5 条差别 U-1–U-5。报告：[research/phase2-local/slope/SLOPE-SLIDE.md](research/phase2-local/slope/SLOPE-SLIDE.md)（research #67）。
  - 起因：M8 只测过 29–41° 下坡、按住下蹲；上坡、小于 29° 的缓坡、坡度变化处都没测过。你让去补测。
  - 公式：滑铲贴地时水平速度每条命令 += g·dt·n_z·n_水平（沿坡 750·sinθ·cosθ），5–40°、上 / 下 / 横 / 斜、按住或松开下蹲都成立，残差 rms 0.001–0.19 u/s [native + meas]。M8 的 147 + 342·sinθ 只在 29–41° 凑得上（5° 时给 177，实测 65.1）。
  - 上坡：从约 400 u/s 冲上 10 / 20 / 30 / 40°，坡上滑 0.87 / 0.64 / 0.53 / 0.49 s、上行 222 / 165 / 136 / 124 u；减到 125 结束，按住 W 变成 92 蹲走，松开 W 原地停住，不倒滑。
  - 转折（平地↔下坡 5–30°、V 形、坡顶）：离地命令全部是 0。
  - 二次加成：换地面实体、距上次滑铲开始 ≥ 2 s 时再加速一次（实测 398 → 461、255 → 428）。调用 `Slide_TryBegin` 的只有 `Duck`（两处）和 `SetGroundEntity`（0x140a51650）。R5 的坡道全是道具拼的，所以每条接缝都算换实体；Apex 的地形和世界几何是同一个实体（推断，没测）。
  - Unity 差别：U-1 上坡步长（R5 cosθ、Unity cos²θ，40° 只走到 76 %）；U-2 坡上原点高度（R5 圆底 16·(1/cosθ − 1)，Unity 方盒 16·tanθ）；U-3 没有二次加成；U-4 坡面项有 2.56° 门槛；U-5 `slideSlopeNeedsDuck` 含义不对。另外记下但不在范围内：滑铲跳起跳后水平 R5 258.x、Unity 260.3。
  - 对照用的是一个只读编译 Unity 运行时源码的 dotnet 坡道 harness（`slope/harness/`），因为 FeelBatch 放不了坡道。Fun 的斜坡（暂缓的 E2）没动。

### 2026-10-28：斜坡按 R5 改（R6U）
- 你："按照R5的改，U3的归档（在folder中可选）"。
  - **[D-45]** U-1 上坡步长、U-2 坡上圆底（半径 16）、U-4 坡面项没有门槛、U-5 `slideSlopeNeedsDuck` 清理，Reference 都改成 R5；Fun 和回放电机不变。用 R6 的 R5 试验重跑：上坡滑铲距离 10–40° 从 215 / 148 / 110 / 84 变成 223 / 166 / 137 / 125（R5 222 / 165 / 136 / 124），平地→下坡转折的速度差从 8–13 降到 2–5 u/s。对照 [R6U-COMPARE.md](research/phase2-local/slope/R6U-COMPARE.md)。
  - **[D-46]** U-3 换地面实体时重新开始滑铲（≥ 2 s 再加速一次，最多到 460，不降速），做成三档：R5（默认：静态关卡几何算一个实体，只有平台这类道具各算一个）、关（旧版）、每个方块都算。游戏菜单可切换（PlayerPrefs）。R6 的道具坡道上二次加成的时刻和 R5 相差 ≤ 0.04 s。
  - 旧版都存在 [R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)（R6U 一节），开关和切换写在 HSD-Unity `Abilities/SlopeSlide/README.md`。
  - 练习地图上 U-3（R5 档）会触发的只有平台和坡道相接的 4 处：J 发射坡顶的平台两头、L 滑索场的上坡道接平台、终点平台接 X 连招坡、ZG2 平台接坡道。贴地滑过去才算，而且只有滑铲已经超过 2 s 才会再加速；91 个 Reference 演示和课程单圈里一次都没有触发（"每个方块"档也没有）。
  - Unity：EditMode 2149 / 2149，PlayMode 1 / 1；M2/M1、M3、M4 回放和基线逐字节相同；真实按键演示 238 / 238，91 个 Reference 演示的轨迹和改前完全一样；课程单圈 79.12 → 78.88 s，来自 U-1（L 滑索场的上坡道走得快了；单关 U-1 回到 79.14）；build `HSD-Build\R6U`。

### 2026-10-28：回放电机的滑铲规则换成原生（RPS）
- 你："你建议（主要的贴合原生的）老的归档"，确认"对，合并后派"。
  - **[D-47]** 回放电机（R5 录像逐命令复现用的那套）的 7 个滑铲开关改成原生，和 Reference 一致：松开下蹲、2 s 加速冷却（从上次开始算）、早跳退还要下蹲过渡没完、过渡从下一条命令算、350 下限只抬 297.5–350、滑铲转向 50。斜坡（R6U）和非滑铲的 N7 项没动。旧规则存成 **Legacy M2**（`R5MotorV2Params.LegacyM2()`、`BatchReplay -legacyM2`），能逐字节复现改前全部回放输出。
  - 105 个 R5 录像重跑：103 个逐命令轨迹不变，M3 两个 `e8_slide_chain` 更接近 R5（水平速度误差 rms 7.48 → 0.15 u/s，事件时刻误差 12 → 0 条命令；原因是录像最后的松开下蹲），没有变差的。新基线和对照：[research/phase2-local/rps/README.md](research/phase2-local/rps/README.md)；存档：[R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)（RPS 一节）。
  - 游戏身体不变：105 个录像喂给 Reference / Fun 身体，轨迹和改前逐字节相同；真实按键演示 238 / 238，smoke 输出和 R6U 逐行相同，课程单圈 78.88 s 不变。Unity：EditMode 2149 / 2149，PlayMode 1 / 1；build `HSD-Build\RPS`；HSD-Unity [#44](https://github.com/letheli710/HSD-Unity/pull/44)。

### 2026-10-28：回放电机的下蹲碰撞体和地面移动换成 Reference（RUD）
- 你：先同意把 RPS 留下的边界项 `airUnduckDrop`（空中松开下蹲时原点下降 16.5 u）也换到回放电机（"第一个，我完全同意，就像你说的"）。
  - 只换这一项时，105 个录像里 7 个变好、3 个按判据变差，所以停下来查原因：
    - M3 e3 滑铲跳 r650 / r651：着地时刻对了，但水平位置误差 rms 4.0 → 8.4 / 3.7 → 9.1。原因是这时露出了回放电机的另一条旧规则：着地那一条命令速度方向就直接转到按键方向（R5 用约 30 条命令慢慢转过去）。改前着地晚 10 条命令，正好把这个差别盖住了。
    - M3 r1237：见下面例外 2。
- 你选了 B："一起换转向"。
  - **第一版**（HSD-Unity ac14658，没采用）：再换 M5 的 `groundVectorRedirect`（横向速度按减速度衰减）。
    - e3 整组大幅变好：r650 位置误差 rms 7.26 → 2.54 u、r651 7.05 → 1.36 u，k25 / k58 / k60 这几个从 23–26 u 降到约 2 u。
    - M2 `e1_turn` r331 / r332 变差：鼠标转身时速度贴在 299 上限，M5 规则每条命令少约 0.044 u/s，速度误差 rms 0.1362 → 0.1372、0.0737 → 0.0756（R5 转身时一直是 299）。
    - r1237 同下。
  - 查的时候发现，Reference 里有输入的地面命令走的其实是 N7 的原生 WalkMove（`groundNativeFriction`，G-07/G-08/G-14），它优先于 M5 的 `groundVectorRedirect`；Reference 的参数来源也写着 "superseded by groundNativeFriction"。所以"原生的转向"就是 `groundNativeFriction`。
  - **第二版**（采用）：回放电机打开 `groundNativeFriction`，和 Reference 完全一致。
    - e3 比第一版再好 20–40%（例如 r651 1.36 → 1.09，k1 r601 0.69 → 0.47）。
    - e1_turn 的轨迹误差回到和改前一样。
- 你："第二版接受。既然他们的数据更相似，那就用第二版。"，并要求把第一版和三个例外都记下来。
  - **[D-49]** 回放电机的两项默认值改成 Reference，没写新物理代码，只改 `R5MotorV2Params.R5Reference()`：
    - 下蹲碰撞体 `airUnduckDrop` 16.5：地上按住下蹲 0.2 s 后碰撞体变矮；空中松开（起跳 0.08 s 后起）原点下降 16.5 u。
    - 有输入时的地面移动 `groundNativeFriction`：原生 WalkMove。
    - `groundVectorRedirect` 也和 Reference 一样设着（被上一项盖过）。
    - 斜坡（R6U）和其余 N7 项（空中额外加速、冲刺加速边界、跳跃 skip reduce、+30 推墙）没动。
  - 旧电机仍是 **Legacy M2**：`LegacyM2()` = RPS 的旧滑铲规则 + `WithLegacyM2Rud()`（关掉这两项）；`BatchReplay -legacyM2` 仍逐字节复现最老的回放基线（M2/M1 111/111、M1 首猜 111/111、M3 90/90、M4 114/114）。
  - 105 个录像重跑（改前 = RPS 基线）：70 个逐命令轨迹不变，35 个变了；32 个变好或持平。
    - M3 e3 侧向起跳整组：位置误差 rms 例如 24.2 → 2.4 u，速度误差 rms 56 → 5 u/s。
    - e3 滑铲跳 r650 / r651：7.26 → 2.54 / 7.05 → 1.09 u，着地时刻误差 10 → 0 条命令。
    - e8 连跳：8.0 → 0.6–1.4 u。
    - M4 空中控制 / stim 空中：10–20 → 1–2 u。
    - M4 跳板下蹲：8.1 → 3.9、6.0 → 1.4 u。
  - **接受的三个例外**（按判据算"变差"，原因都查清了）：
    1. M2 `e1_turn` r331 / r332：事件时刻误差 28 → 182、50 → 196 条命令。唯一变的是"最高速度出现在第几条命令"：速度贴在 299 的平台上，取最大值落在哪一条由 1e-13 级的浮点噪声决定。轨迹误差和改前一样（位置 rms 0.739 / 0.576、速度 rms 0.136 / 0.074 不变）。
    2. M3 `e8_hop350_d0` r1237：位置最大误差 20.2 → 26.6 u，最高点误差 16.7 → 17.1 u（位置 rms 7.92 → 6.26 是变好的）。连跳中 R5 第 498 条命令着地、下一条就起跳；沙盘比 R5 高约 0.5 u，离地面 2.075 u，刚超出原生 2.0 u 的着地探测，晚一条命令着地，那次起跳就丢了。同条件的 r1236 8.02 → 0.62 u。不调参数去掩盖。
  - 原生着地探测查清：`CategorizePosition`（r5apex_dx12 0x140a51bc0）向下探测 **2.0 u**，向上速度 > 140 u/s 就离地，和 Unity 的 `groundProbe` 2 相同，没改。
  - 新基线和对照：[research/phase2-local/rud/README.md](research/phase2-local/rud/README.md)（`rud_check.py`；第一版的对照表也在那里）；存档：[R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)（RUD 一节）。
  - 游戏身体不变：105 个录像喂给 Reference / Fun 身体，轨迹和改前逐字节相同（各 105 / 105）。
    - Unity 回归：真实按键演示 238 / 238，smoke 输出和 RPS build 逐行相同，课程单圈 78.88 s 不变；EditMode 2150 / 2150（多 1 个检查报告行的新测试），PlayMode 1 / 1；build `HSD-Build\RUD`；HSD-Unity [#45](https://github.com/letheli710/HSD-Unity/pull/45)。

### 2026-10-28：钩爪脱钩全部按原生（GN）
- 你："我说对于'勾爪'这一块，我们全部按原生的去做。1. 对于现版本，以及原生和现版本转换带来的影响，这些都放在 decision 里头。2. 对原先代码进行归档。这样如果以后还要用，或者觉得不适合的话，我们还有更改的余地。"
  - **[D-50]** Reference（Fun 从 Reference 建，一起变）的钩爪脱钩规则全部换成原生。依据 N13（research #72）和这次的 Frida 实测。旧规则叫 **pre-GN**，每条一个开关，`GrappleS21Params.SetGnDetach(false)` 一次全切回去；游戏 Esc 菜单 "Grapple detach rules (GN)" 也能切（PlayerPrefs `hsd.gn.grapple`）。切回旧版时，105 个录像喂给游戏身体的 315 个输出文件和改前逐字节相同。回放电机不用这套钩爪，不变。
  - **现版本（旧）和原生，逐条**：
    - **G-1 接近脱钩的距离**：旧版量钩点到身体竖线段 [原点, 原点 + 72] 的距离（挂上后 wind-up 里 ≤ 45 就脱）；原生量钩点到"原点"和"眼睛"两个点的较近距离，挂上后每条命令都查。钩点在身体高度范围内时线段距离更小，所以旧版早脱。**影响**：往墙上拉晚 1 条命令脱钩（M4 hold 241 → 242，同一个场景）。
    - **G-2 接近斜坡**：阈值 33 u，接近越快放得越早，最多 50 u；旧版接近速度除以 800，原生除以 400（ConVar `grapple_speedRampMax_human`）。**影响**：只在接近速度 267–533 u/s 时不同（阈值最多大 17 u），慢慢贴近钩点会早一点放；测过的片段都不在这个速度区间，没变化。
    - **G-3 方向**：旧版视线规则从"原点 + 70"看钩点，速度朝"原点 + 36"量；原生都按绳子方向，从原点上方 23（Frida 读到的 h = 22，再加 1）指向钩点上方 25。**影响**：视线离开、rodeo 的脱钩时刻不变。钩点很高（仰角约 50°）时，仰着头原地转 180° 不再脱钩，要把视角放平；演示 `m10a_look_away` 因此改成边转边放平。演示里绕钩点的 tether 多绕了一段（198° → 313°），侧键、跳钩的峰值 / 出口速度多 2–12 u/s。
    - **G-4 低速超时**：旧版是"速率 |v| < 250"持续一段时间就脱；原生是"朝绳子的径向速度 ≤ 250"。**影响**：绕着钩点横飞、贴着挡板横移（速度大但不朝钩点）现在会超时脱钩，以前不会；直线被挡住时不变。
    - **#7 低速时限**（这次另外找出来的）：旧版碰到墙 / 天花板用 1.2 s、在地面高度用 0.7 s、其余 1.5 s；原生按"有没有地面实体"选，R5 拉动时一直没有地面（ground = 0），所以一律 1.5 s。**影响**：N6 天花板 8 个片段，拉动到脱钩 1.20 s → 1.50 s（R5 1.508–1.517 s）。
    - **G-5 "远离钩点 > 500 u/s"脱钩**：旧版一直开着；原生只在钩子没有父实体时开。Frida 实测：钩在岩石（脚本建的道具）上时父实体就是那块岩石，钩在地面（世界几何）上时为空。所以**钩在世界上开、钩在道具或绳子上关**（N13 原来推断的正好反了）。**影响**：测过的片段都没触发。练习地图上只有平台类方块和绳子算道具。
    - **G-6 撞上时上抬**：原生客户端代码在世界钩点接近脱钩时把竖直速度抬到 300（Frida 在地面钩上看到 vz 299）；但本地录下来的轨迹没有跳（混合版本：本地 S3 服务器或这一条命令的移动把它抹掉了），世界上的墙没测过。**按任务没加**，开关 `impactBoost` 做好了、都关着，见"还没结论的事"。
  - **对照场景也按 R5 改了**（N13 的 S-1 / S-2）：岩石挡身体的面 x −13704.6、后倾 1.86°，钩点在过实测钩点（x −13697.9）的平行面上，算道具。只给手感对照用，回放电机的场景文件不动。镜头对照的 R5 横滚，视线离开 / rodeo 改用"只有客户端"的模型（N13 F-1）。
  - **结果**（R5 / 改前 / 现在）：
    - A-1 往墙上拉，脱钩命令 244, 243, 201, 201 / 241, 241, 199, 199 / **245, 245, 202, 202**；最高点 155.3, 154.9, 117.3, 116.8 / 145.0, 145.0, 111.3, 111.8 / **155.7, 155.7, 116.3, 116.6**。比预计（244, 244, 201, 201）晚 1 条：同一个新场景用旧规则就是 244, 244, 202, 202，这 1 条出在场景和拉力的近似上，没有调。没有一个片段离 R5 更远。
    - 视线离开 ×4 横滚峰值：R5 只有客户端 12.75–13.0°（实测 19.2° 是混合版本），Unity 12.8°（不变）；rodeo ×8：11.0–11.9° 对 11.2–11.5°。
    - N6 天花板：1.20 → 1.50 s（R5 1.51 s）。
  - 回归：回放电机和 RPS 基线逐字节相同；EditMode 2155 / 2155（GN 分支），和 RUD（#45）合在一起 2156 / 2156；PlayMode 1 / 1；真实按键演示 238 / 238（数值变化见上）；课程单圈 78.88 s 不变（地面路线不用钩爪）；build `HSD-Build\GN`。
  - 文档：[research/rea-native/gn/GN-GRAPPLE-NATIVE.md](research/rea-native/gn/GN-GRAPPLE-NATIVE.md)；存档 [R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)（GN 一节）；开关说明 HSD-Unity `Abilities/Grapple/README.md`；HSD-Unity [#46](https://github.com/letheli710/HSD-Unity/pull/46)，research [#74](https://github.com/letheli710/Apex-MovementAnalysis/pull/74)。

### 2026-10-28：F-2 原地跳高 1.8 u 查清（不是移动代码）
- 你："检测是不是底层上导致的，如果不是记录一下就好"
  - **[D-55]** 不是底层，Unity 不改。R5 那次跳得矮，是测试工具每个片段开头在 dedi 上重置玩家：dedi 把重置算成一次落地，0.72 s 后起跳，原生"刚落地又跳"的高度惩罚（`antiMultiJump`，0.75 s 内生效）把起跳速度从 282.0 压到 277.3。客户端预测不知道这次落地，按完整高度跳，起跳后第 8 条命令被 dedi 纠正，录下来的就矮了。
  - 证据：这个 session 的 4 次原地跳，dedi 上"重置到起跳"的时间和用起跳速度反推的"距上次落地"每次差不到 1 ms；从 dedi 的起跳状态往下算，最高点和 R5 录像差 0.001 u。重置后 0.84 s 才跳的 M4 原地跳（2 次）没有惩罚，最高点 54.80 u，Unity 完全重合。全部 99 次 R5 跳跃里只有这两次 M2 原地跳被纠正。
  - 起跳速度、重力半步、贴地、原点 / 眼睛、帧率、采样这几项都逐条核过，两边一样。
  - 文档：[research/feel/F2-STANDING-JUMP.md](research/feel/F2-STANDING-JUMP.md)。

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
| D-34 | 10-27 | A-1 钩爪往墙上拉 | 先补研究，再按 R5 改：横向刹车照原生（向下和朝视线的部分不刹，一直刹，不再"追上目标才刹"）；钩子从真实眼高（70 / 冲刺 64 / 蹲 32）打出 | `MovementConfigs.NativeGrapple()` 的 `s21.nativeCrossBrake`、`s21.nativeEye`（Reference 和 Fun 都开） | HSD-Unity `f6/r5-faithful` |
| D-35 | 10-27 | K-1 / K-2 落地 kick 的随机数 | 用 R5 自己的随机数（`R5SharedRandom`：命令号 MD5 → 种子混合 → 随机数） | 原生镜头 `NativeCameraParams.r5Random`（true；false = 旧哈希） | HSD-Unity `f6/r5-faithful` |
| D-36 | 10-27 | 复刻原则 | 以 R5 为复刻核心：对照找到的差别原则上改成 R5，以后的 Unity 都用这一版；改之前和 R5 不一样的地方存档 | 存档 [R5-DIFF-ARCHIVE.md](R5-DIFF-ARCHIVE.md)（每项写了怎么切回旧版） | research `f6/r5-faithful` |
| D-37 | 10-27 | K-3 跑步晃动（按 D-36） | 俯仰幅度 0.335 → 0.25，渐入每秒 4 → 20 | `NativeCameraParams.swayPitchAmp`、`swayFade` | HSD-Unity `f6/r5-faithful` |
| D-38 | 10-27 | K-4 眼高（按 D-36） | 站立 64 → 70；冲刺时降 6（原生 `sprintViewOffset`），蹲 / 滑 32 不变；镜头和钩爪共用 | `NativeEyeParams`（`R5Replay/Runtime/NativeEyeHeight.cs`）；旧值 `NativeEyeParams.PreF4()` | HSD-Unity `f6/r5-faithful` |
| D-39 | 10-27 | 旧的 "Revenant-Wraith ground" 预设 | 当历史保留，配置不动；在用的是 Revenant S21 / Wraith S21（你："我们现在已经有一个新版本来替代这个老的了…就把老的当做历史，把配置保留掉，然后继续使用这套新的"） | 不改代码 | — |
| D-40 | 10-27 | LS / RAS | 没有具体要复现的视频；Reference 保持原生 lurch 模型（对照 L-11 一致，M9 反向 lurch 在 3° 以内）（你："没有具体要实现的…尽可能符合这个原生的版本…之前这个已经做完了"） | 不改代码 | — |
| D-41 | 10-27 | "N10 剩下的镜头项目"这条待定 | 早已完成（CAM-18 / 19 在 N10 查清），划掉；rodeo 钩爪侧倾那条还开着 | — | research #56 |
| D-42 | 10-27 | 钩爪 / 滑索横滚平滑（N12 C-12，你批准） | 改成原生：两者共用一个临界阻尼弹簧（ω 6.667），钩头飞行中也算目标；旧版（各自一阶 6.667 / 3.0）存档 | `NativeCameraParams.nativeRollSmooth`（默认 true；false = 旧版） | HSD-Unity#42，research #68 |
| D-43 | 10-27 | 跳板二段跳反馈 | 只动表现层：准星下方的可用 / 倒计时 / 按太早 / 触发提示，触发音，原生镜头向下沉 1.2°（[design]，等试玩） | `HsdHud.PadCentre`、`PadJumpCue`、`NativeCameraParams.padJumpKickPitch` | HSD-Unity#42，research #68 |
| D-44 | 10-27 | FOV 设置 | 菜单按 Apex 的 FOV 数值（4:3 水平，70–110）显示和输入；默认不变（竖直 70° = Apex 86） | `CameraFeedbackSettings.VerticalFromApex` / `ApexFov`，PlayerPrefs 键不变 | HSD-Unity#42，research #68 |
| D-45 | 10-28 | 斜坡 U-1 / U-2 / U-4 / U-5（R6 实测） | Reference 按 R5：上坡步长保持长度、坡上圆底半径 16（接触和法线按原点）、滑铲坡面项没有门槛、`slideSlopeNeedsDuck` = false；Fun、回放电机不变；旧版存档 | `R5MotorV2Params.slopeUphillKeepStep` / `hullBottomRadius` / `slideSlopeAnyGrade` / `slideSlopeNeedsDuck` | HSD-Unity#43，research #69 |
| D-46 | 10-28 | 斜坡 U-3：换地面实体时重新开始滑铲 | 按 R5（≥ 2 s 再加速一次，不降速），可选三档：R5（默认，关卡几何一个实体、平台是道具）/ 关（旧版）/ 每个方块 | `R5MotorV2Params.slideRebeginOnGroundChange`（`SlideRebegin`）、`ConvexSolid.prop`；菜单 PlayerPrefs `hsd.r6u.sliderebegin` | HSD-Unity#43，research #69 |
| D-47 | 10-28 | 回放电机要不要换成 M10 / N7 的滑铲规则（"还没结论的事"里的一条） | 换成原生（和 Reference 一致），只换 7 个滑铲开关；旧规则存成 Legacy M2，可逐字节复现旧回放基线；回放基线重定（只有 2 个 M3 滑铲连招变了，更接近 R5） | `R5MotorV2Params` 滑铲开关默认值、`LegacyM2()` / `WithLegacyM2Slide()`、`BatchReplay -legacyM2` | HSD-Unity#44，research #70 |
| D-48 | 10-27 | EPG 真实开火的火箭跳 | 本地 R5 加载不了能开火的 EPG，只做了服务端模拟 + 真手雷对照；真实开火留到之后的《泰坦陨落2》研究（Northstar 本地私服）里做，和模拟结果对照 | — | research #64；工作区 `TODO.md` 的 TF2 研究 T-1 |
| D-49 | 10-28 | 回放电机的下蹲碰撞体和地面转向（RPS 留下的边界项） | 换成 Reference：`airUnduckDrop` 16.5 + 原生 WalkMove（`groundNativeFriction`）；先做的 M5 `groundVectorRedirect` 版（第一版）没采用；旧电机仍是 Legacy M2；回放基线重定（35 个变，3 个例外：e1_turn ×2 平台噪声、r1237 着地探测边界） | `R5MotorV2Params.R5Reference()`、`WithLegacyM2Rud()`、`BatchReplay -legacyM2` | HSD-Unity `rud/replay-unduck-native`（#45） |
| D-50 | 10-28 | 钩爪脱钩规则（N13 的 G-1…G-6） | 全部按原生：接近距离取原点 / 眼睛较近者、斜坡 400、视线和速度按绳子方向量、低速按径向速度、拉动中低速时限一律 1.5 s、远离 > 500 只在世界钩点；撞上上抬（G-6）没加、待定；旧版存档可切回 | `GrappleS21Params.SetGnDetach(false)`（或单个开关 `nativeProxDistance` / `detachRampMax` / `nativeRopeDir` / `nativeLowSpeed` / `nativeLowSpeedTimer` / `awayOnlyWorldHooks`）；Esc 菜单 "Grapple detach rules (GN)"（PlayerPrefs `hsd.gn.grapple`）；`FeelBatch` / `CameraFeelBatch -preGn` | HSD-Unity `gn/grapple-native` （[#46](https://github.com/letheli710/HSD-Unity/pull/46)）；research [#74](https://github.com/letheli710/Apex-MovementAnalysis/pull/74) |
| D-51 | 10-28 | 钩爪撞上时上抬（G-6，GN 留下的） | 先关着、留作待定：原生客户端在世界钩点会抬到 300，但本地录像是混合版本看不到，世界上的墙也没测过，没法对照；等有只有客户端的实测或《泰坦陨落2》的对照再定 | 不改（`GrappleS21Params.impactBoost` 保持关） | 本表；R5-DIFF-ARCHIVE 二节 G-6 行 |
| D-55 | 10-28 | F-2 原地跳 Unity 比 R5 高 1.8 u | 不是移动代码，不改：测试工具的重置在 dedi 上算成落地，0.72 s 后起跳触发原生 antiMultiJump 降高（282.0 → 277.3 u/s），客户端被纠正；真实玩的时候没有这种重置 | 不改（Unity 两套电机都按"片段开头的重置不算落地"） | [research/feel/F2-STANDING-JUMP.md](research/feel/F2-STANDING-JUMP.md)；本表 |

**D-29 → D-31（C-2 为什么推翻）**：第一次决定时以为 Unity 的 102.5 ms 窗口已经盖住了 R5 的减量段，所以"简化 = 不改代码"。后来按 Unity 自己的翻越时钟重排（Unity 的翻越比 R5 长约 25 ms），发现减量段其实在窗口外面，原来的 Reference 在这段是"切到台面"，并不是"给完整 460"。你随后要求继续做 C-2 并合并。细节见 `research/feel/FEEL.md` §6.4 和 `Climb/README.md`。

**D-20 / D-32 和 D-31 的关系**：游戏里默认开着 S27 翻越加速，这时 superglide 走 S27 规则，D-31 的减量段看不到；在菜单里关掉 S27 才是原生 superglide。

**D-07 和 D-15**：M6-B 时你说过不再做新的逆向；10-23 你把原生代码研究定成新的优先级，之后的 N 系列就是按这个做的。

---

## 还没结论的事

记录里写着"等你决定"、后来没看到明确结论的。要么还没定，要么定了没记下来，回顾时请确认：

- ~~回放电机要不要换成 M10 的新滑铲规则~~：10-28 换了，见 D-47。回放电机里斜坡和非滑铲的 N7 项（地面摩擦、空中额外加速等）仍是旧规则，要不要也换没定。
- **F-2**：一次原地跳 Unity 比 R5 高 1.8 u（两套电机都是）。（F1）〔10-28 查了：不是移动代码。测试工具的重置在 dedi 上算成落地，0.72 s 后起跳触发原生 antiMultiJump 降高，客户端被 dedi 纠正；Unity 不改，见 D-55〕
- ~~LS / RAS~~：10-27 定了，见 D-40。
- ~~旧的 "Revenant-Wraith" 配置~~：10-27 定了，当历史保留，见 D-39。
- ~~N10 剩下的镜头项目~~：N10（research #56）已经做完，见 D-41。
- ~~钩爪侧倾~~：N12 查清（rodeo 是钩岩石后转圈，不是攀在对手身上；差距来自我们的平滑模型和门控），F7 按原生改了，见 D-42。
- ~~A-1、K-1、K-2、K-3、翻越镜头~~：10-27 已处理，见 D-34 – D-38。
- ~~A-1 剩下的部分~~：10-28 查清（N13：脱钩距离规则 + 对照场景的钩点和斜面）并按原生改了，见 D-50。最高点差 0.4–1.0 u，脱钩晚 1–2 条命令（场景近似）。
- **K-5 起跳时的镜头动作**：R5 起跳后镜头先向下 1.3–2.5°（0.10 s）、再向上约 1.7°（0.57 s），横滚 +0.5–1.1°，Unity 没有。只量过短滞空，长滞空时什么样不知道。做不做？（F6）
- **K-6 翻越时的镜头动作**：R5 翻 120 u 的墙时镜头向下约 5°（撞墙后约 0.2 s），Unity 没有（只有 S27 翻越加速打开时有）。做不做？（F6）
- **K-7 滑索横滚**：两次 R5 会话不一样（N6 没有，N10 转开 30–60° 时 −0.7 … −1.4°），Unity 是 0；滑索上 R5 眼高约 65.5，Unity 70。要再测一次。（F6）
- ~~钩爪比 R5 早脱钩~~：10-28 查清（N13：R5 的"挂到 1.5 s"是本地 dedi 重挂，只有客户端时 Unity 一致）并把脱钩规则全部按原生改了，见 D-50。
- **G-6 钩爪撞上时上抬**：原生客户端在世界钩点（不是道具）接近脱钩时把竖直速度抬到 300，本地轨迹看不到，世界上的墙没测过。要不要加（开关 `impactBoost`，现在都关）等你定。（GN）〔10-28 你定了：先关着，留作待定；等有能对照的实测（只有客户端的录像、或《泰坦陨落2》）再说。见 D-51〕
- **HSD 要不要做火箭跳**：A. EPG 式物理击退（爆点推向身体中心，随距离衰减，和现有速度相加，上限 1000），或 B. Fuse Knuckle Jumper 式跳跃加成（在自己炸弹旁边按跳给固定的起跳速度）。研究建议先做 A，用 jump_kit 数值，护盾规则和地面门槛先不做。见 [research/epg/EPG-ROCKET-JUMP.md](research/epg/EPG-ROCKET-JUMP.md) §7。（EPG）
- **回放电机的 `airUnduckDrop`**（空中松开下蹲时原点下降 16.5 u，下蹲碰撞体规则）：Reference 开着、回放电机关着。RPS 只换了滑铲开关，这一项算不算滑铲由你定，回放电机要不要也开？（RPS）〔10-28 已做完：回放电机开了，地面移动也一起换成原生 WalkMove，见 D-49〕
- **《泰坦陨落2》研究**：第一步装 Northstar 并验证能自动跑测，第一个实验是 EPG 真实开火（D-48）。什么时候开始等你定。
- 暂缓清单里的 E1–E3 见 [DEFERRED-DESIGN-TODO.md](DEFERRED-DESIGN-TODO.md)。
