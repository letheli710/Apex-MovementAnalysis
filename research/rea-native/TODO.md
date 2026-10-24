# REA 原生研究 TODO

建立于 2026-10-23。分两部分：

- **当前**：这一轮要做的事，对应 [REA-PLAN-DRAFT.md](REA-PLAN-DRAFT.md) 的阶段；
- **暂缓**：用户认为值得研究、但明确说**现在不做**的方向。Agent 不得自行开工，等用户发话。

---

## 当前：原生移动系统地图（首要任务）

用户原话（2026-10-23）："我们现在的首要任务是将移动系统构建出一张全面的地图，让我们深刻地、仔细地、原生地了解这个移动系统。"

- [ ] 用户审阅计划草稿，回答 §10 的问题（2026-10-23 已答：Frida 允许、C3 改 MoveDiag 同意、Unity 建议先记录；名称、dedi 深度、viewmodel、节奏未答）
- [x] **N0** 环境和试点：检查二进制，跑 Ghidra 自动分析，用 `sv_gravity` = 750 和 SDK 命名函数定标，读出原生 ConVar 默认值（ConVar 部分见 `convar-defaults/`），结论见 `N0-PILOT.md`
- [x] **N1** 骨架地图：`NATIVE-MAP.md`、`map/functions.csv`、`map/reads.csv`、`map/sdk-hooks.csv`、`map/setfile-keys.csv`
  - [ ] N1 遗留：8 个 SDK 钩子的地址（`IN_JumpDown` / `IN_JumpUp`、`Glide_*` 等）；51 个没分类的核心函数
- [ ] **N2** P1 子系统公式提取：
  - [x] T 时序和输入 → `subsystems/N2-T-TIMING-INPUT.md`（部分：冲量队列的写入方、`PlayerMove` 分派没读）
  - [x] G 地面移动 → `subsystems/N2-G-GROUND.md`（遗留：吸附阈值位置 G-06、Friction 里的 x、几个结构体偏移）
  - [x] J 跳跃、空中、落地 → `subsystems/N2-J-JUMP-AIR.md`（M2 的空中残余增益、连跳惩罚、skip 削减都已解释；遗留 `AirMove` 本体、二段跳分支）
  - [x] L Lurch / tap-strafe → `subsystems/N2-L-LURCH.md`（209.3 夹紧出处已找到）
  - [x] S 滑铲 → `subsystems/N2-S-SLIDE.md`（遗留：斜坡项公式 S-09、按住下蹲时结束速度 125 vs 112 S-05）
  - [x] M 攀越、mantle、SG、墙 → `subsystems/N2-M-TRAVERSAL.md`（部分：SG 窗口 M-04、1.1 × 299、402.009 还没读通；攀墙、自动 mantle 触发条件没读）
- [x] **N2** P2 子系统：P 钩爪、Z 滑索、F 跳板 → `subsystems/N2-P2-GRAPPLE-ZIPLINE-PADS.md`（遗留：P-08 ~ P-10；重力炮、升降梯、JetDrive、喷气没读）
- [ ] **C 第一人称镜头手感**（camera feel，用户 2026-10-23 加入，计划 §5.1）：随角色动作产生的**全部**镜头效果，不只是跑步晃动、落地震动、滑铲下沉；也包括墙跑、攀爬、跳跃、钩爪、滑索等
  - [x] C1 完整清单：一共有哪些效果、各叫什么、由什么触发、在哪里计算（原生 / 脚本 / 动画）→ `camera/CAMERA-INVENTORY.md`（23 项 + 3 个边界项；跑步晃动还没找到对应参数）
  - [x] C2（第一批）逐个弄清做法 → `subsystems/N2-C-CAMERA.md`：punch 弹簧（k 65、c 9）、落地 kick、横滚汇总（S21 只有滑铲 / 冲刺 / 钩爪滑索横滚生效）。遗留：滑铲倾斜精确公式、冲刺倾斜、眼高曲线、cockpit sway 是否动镜头、是否影响准星
  - [ ] C3 逐帧实测：按渲染帧记录镜头位置、角度和 FOV（用户 2026-10-23 已同意改 HSD.MoveDiag）
  - [ ] C4 进对照账本（`CAM-`），和 M5.5 镜头对照，只给建议
- [x] **N3**（P1 部分）对照账本 → `CROSSCHECK-LEDGER.md`、`ledger.csv`（60 条）
  - [x] P2 子系统和镜头 C2 的第一批条目补进账本（现在 78 条）
  - [ ] 用户决定账本 §3.2 的 Unity 修改建议（不自动改）：已记录在 `UNITY-CHANGE-PROPOSALS.md`，等 N4 实测后统一决定
- [ ] **N4** 针对性验证（Frida 用户已允许），待测清单见下一节
  - [x] N4-A 批量补读 setfile 键 → `n4/N4A-READBACK.md`（预言 5 / 5 命中）
  - [x] N4-B 地面按键急转 G-07 → `n4/N4B-KEYTURN.md`（原生公式逐命令吻合；Unity 瞬间转向不符）

### 后放的事（用户 2026-10-23："不要忘记后放的事情"）

N4-A / N4-B 做完后回来做，顺序可以再定：

- [x] 读 Horizon 升降梯、Vantage JetDrive、Valkyrie 喷气、重力炮的代码 → `N2-P2` §7（喷气、重力炮、JetDrive 启动已读；JetDrive 每帧推进、升降梯的移动代码没找到）
- [x] 镜头 C2 剩下的（→ `N2-C` §7；滑铲倾斜、眼高已读；是否影响准星、cockpit sway 留给 C3）：滑铲倾斜精确公式（0x140afc040）、冲刺倾斜、眼高曲线（CAM-10）、cockpit sway / spring 是否动镜头（CAM-18 / 19）、镜头效果是否影响准星
- [x] superglide 窗口（M-04）第二轮阅读 → `N2-M` §7：分界是动画里的"翻过沿"进度阈值，静态读不出，改成 N4 实验
- [x] 钩爪 P-08 ~ P-10 第一轮 → `N2-P2` §8：没读通，改成 N4 实验
- [x] N1 遗留 → `NATIVE-MAP` §9：钩子地址 66 / 70（其余 4 个静态定位不了）；51 个小函数暂不分类

---

## N4 待测预言和补读清单

代码读出来、但还没有实测确认的东西。每条都写明预期结果，测完在这里打勾并写上会话名。用户 2026-10-23 要求集中放在这里。

**A. 补读数值**（运行时 `bridge_classvar_get`，不需要设计实验，成本最低）

- [x] `antiMultiJumpTimeMin` / `antiMultiJumpTimeMax` / `antiMultiJumpHeightFrac`：预期 **0.15 / 0.75 / 0.3**（N2-J J-02）→ **命中**（N4A_classvars）
- [x] `player_slideBoostCooldown`：预期在 M8 测到的 1.6–2.1 s 范围内（N2-S S-02）→ **2**（N4A_classvars）
- [x] `landSlowdownDuration` / `Frac` / `HeightMin` / `HeightMax` / `TimePower` / `NoSprintFrac`（N2-J J-09）→ 1 / 0 / 300 / 800 / 2 / 0.7（N4A_classvars）
- [ ] 蹲姿那一行的 `speed`、`deceleration`：预期 80 / 1500（N2-G G-05）
- [x] 镜头键（N4A_classvars 已读，见 `n4/N4A-READBACK.md`）：`viewkickFallDistMin` / `Max` / `MaxScale`、`slideFOVScale` / `LerpInTime` / `LerpOutTime`、`sprinttiltMaxRoll`、`grapple_roll*`、`ziplineRoll*`（N2-C）
- [x] `ziplineJumpOffSpeed`：预期 **400**（N2-P2 Z-01）→ **命中**
- [x] ConVar `jumppad_vert_override_ducked_scalar`：客户端原生默认 **1**，本地生效 0.5（SDK dedi）[hyb]，预言只对了一半（F-02）
- [x] 其余 census 没读过的 setfile 键（Gibraltar 666 个全部读出，`n4/classvars-gibraltar.csv`）
- [ ] 其他传奇再读一次（按传奇不同的键：喷气、钩爪等）

**B. 新的行为预言**（需要设计实验，用现有 runner）

- [ ] **SG 窗口分界**（M-04）：记录按键时的攀越进度，测出"切断 / SG"的分界
- [ ] **钩爪脱钩细节**（P-08 ~ P-10）：越过锚点时的径向速度和距离、脱钩前后竖直速度、视线离开

- [x] ~~lurch 夹紧随 msc 变化~~：M4 Octane 已经测过（stim 下 294.67 = 0.7 × 冲刺上限），和原生公式一致（N2-L L-05）
- [x] **地面按键急转**（N3 高影响 G-07）→ 已确认（N4B_keyturn）：冲刺中 A↔D、W→D 急转，看速度方向是渐进还是瞬间。原生预期：偏离部分按 1250 减速，意图方向按加速度增长
- [ ] **超速连跳**：落地 1.0 s 内以 450 起跳，出口应为 **350**（max(v − 100, 299)），不是 299（N2-J J-04）
- [ ] **lurch 高速截断**：水平速度 > 1100 时不再 lurch（S21 客户端原生，N2-L L-10）
- [ ] **按住方向键时的摩擦**：意图方向上不超过目标速度的那部分速度不受摩擦，减速只作用在偏离部分（N2-G G-07），用 M2 的 e2 数据先查
- [x] **第一条命令的输入是 0.75，不是 0.5**（N4B 急转里随原生公式一起吻合）：输入曲线 m(2 − m)（N2-G G-08），用 M2 起步数据先查
- [ ] **滑铲中只能转向**：滑铲时按 W 不加速，只有侧向分量起作用（N2-G G-12 / N2-S S-07）
- [ ] **滑铲加成冷却被每次滑铲刷新**：连续短滑铲时加成迟迟不恢复（N2-S S-02）
- [ ] **钩爪低速超时脱钩**：速度低于 250 持续 1.5 s（空中）/ 0.7 s（地面）后自动脱钩（N2-P2 P-07）

**C. 还对不上、要细查的**

- [ ] 按住下蹲时滑铲的结束速度：代码 125，实测 112（N2-S S-05）
- [ ] 地面停止吸附在哪里（N2-G G-06）
- [ ] 斜坡滑铲项的公式，对照 M8 的 147 + 342·sin(坡度)（N2-S S-09）
- [ ] **N5** 汇总报告和 Reference 修改建议

---

## 暂缓：传送类机制（值得研究，现在不做）

**用户决定（2026-10-23）**：Apex 里好几个角色都有传送机制，值得研究，但不是现在。现在先做移动系统地图。

**范围**：所有把玩家从一处移到另一处的机制，按形态分三类：

| 形态 | 角色和技能 | 已有成果 |
|---|---|---|
| 虚空传送门 / 双端门 | Wraith 战术 Into the Void（相位）和大招 Dimensional Rift（传送门） | M10-W 已做 Unity 实现，R5 实测见 `phase2-local/m10/r_wraith/WRAITH-M10.md`、`m10/r2_wraith/PORTAL-R2.md` |
| 贴在表面、穿墙过去 | Alter 战术 Void Passage | 搁置，本地 S21 上 34 次试验 0 个传送门；源码数值见根目录 `SHELVED-ABILITIES.md` 和 `phase2-local/m6/b_legends/M6-B-REPORT.md` §1 |
| 扔出去或拉一条通道过去 | Loba 战术（手环）、Ash 大招 Phase Breach、Alter 大招 Void Nexus | Loba 已实测两轮（搁置，见 `SHELVED-ABILITIES.md`）；Ash 大招、Alter 大招未研究 |

**重启时 REA 能帮什么**：
- Alter：本地放置失败的原因。SDK 的放置代码是社区重写的，可以和 S21 客户端的原生放置代码对照，看是在哪一步拒绝的。
- 传送后的速度规则：Alter 出口 clamp(v·n, 50, 300) 是唯一保留部分速度的；Wraith 出口速度 0；Loba 速度一律 0。确认这些规则在原生代码里的写法。
- 共用部件：传送门的进入判定、冷却、相位状态（SDK `portal_shared.cpp` 有 `portal_teleport_min_speed` / `max_speed` 300 / 1000）。

**重启前要先确认**：
- 每个技能是不是 S21 已有（Alter 是 S21 新传奇；Ash 大招自 S11 起就有）。
- 和根目录 `SHELVED-ABILITIES.md` 的搁置决定一致：Loba 是因为"新意不够"被搁置的，重启前要先问用户。

---

## 其他发现（工作中记下的，不自动开工）

- N1：SDK 在客户端的核心移动函数上挂了很多钩子（`map/sdk-hooks.csv`）。N2 每个子系统都要先确认相关钩子默认是否开启、改了什么。
- N2-L：`convar-defaults/README.md` 里"夹紧 209.3 没有 ConVar 出处"已经过时（出处是 `jump_grace_max` × msc × `sprintspeed`）。那个文件属于 PR #28，合并后再改。
- 可测预言和补读清单已集中到上面的"N4 待测预言和补读清单"。
