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
  - [x] M 攀越、mantle、SG、墙 → `subsystems/N2-M-TRAVERSAL.md`（部分：SG 窗口 M-04 还没读通；1.1 × 299、402.009 已在 LEDGER-OPEN-5 / N11 解释；攀墙、自动 mantle 触发条件没读）
- [x] **N2** P2 子系统：P 钩爪、Z 滑索、F 跳板 → `subsystems/N2-P2-GRAPPLE-ZIPLINE-PADS.md`（遗留：P-08 ~ P-10；重力炮、升降梯、JetDrive、喷气没读）
- [ ] **C 第一人称镜头手感**（camera feel，用户 2026-10-23 加入，计划 §5.1）：随角色动作产生的**全部**镜头效果，不只是跑步晃动、落地震动、滑铲下沉；也包括墙跑、攀爬、跳跃、钩爪、滑索等
  - [x] C1 完整清单：一共有哪些效果、各叫什么、由什么触发、在哪里计算（原生 / 脚本 / 动画）→ `camera/CAMERA-INVENTORY.md`（23 项 + 3 个边界项；跑步晃动还没找到对应参数）
  - [x] C2（第一批）逐个弄清做法 → `subsystems/N2-C-CAMERA.md`：punch 弹簧（k 65、c 9）、落地 kick、横滚汇总（S21 只有滑铲 / 冲刺 / 钩爪滑索横滚生效）。遗留：滑铲倾斜精确公式、冲刺倾斜、眼高曲线、cockpit sway 是否动镜头、是否影响准星
  - [x] C3 逐帧实测 → `camera/C3-CAPTURE.md`：落地 kick（峰值 0.16 s、回弹一次、大小和公式一致）、punch 不动准星、滑铲眼高 0.21 s、滑铲倾斜、FOV × 1.1 都确认。新发现：× 0.2 的条件不是下蹲（CAM-02b）
    - [x] 查玩家 +0x1c7 是什么状态（CAM-02b）→ 水中标志（`PlayerMove` 每 0.05 s 检测，入水 / 出水音效），N2-C §8
    - [ ] cockpit sway / spring（CAM-18 / 19）是否动镜头；冲刺倾斜、钩爪 / 滑索横滚的逐帧实测
  - [x] C4 进对照账本（`CAM-`），和 M5.5 镜头对照，只给建议 → 账本 CAM-01 / 01b / 02 / 02b / 05 / 05b / 09 / 10；M5.5 差别记在 `n5/REFERENCE-CHANGES.md` §3
- [x] **N3**（P1 部分）对照账本 → `CROSSCHECK-LEDGER.md`、`ledger.csv`（60 条）
  - [x] P2 子系统和镜头 C2 的第一批条目补进账本（现在 78 条）
  - [ ] 用户决定账本 §3.2 的 Unity 修改建议（不自动改）：已记录在 `UNITY-CHANGE-PROPOSALS.md`，等 N4 实测后统一决定
- [x] **N4** 针对性验证 → `n4/`（A / B / C / D 四批；剩 P-07、P-08、P-10 需专门场景，C3 镜头单独做）
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
- [x] 蹲姿那一行的 `speed`、`deceleration`：代码按姿态取，M2 的 80 / 1500 即蹲姿那一行（N4-D）
- [x] 镜头键（N4A_classvars 已读，见 `n4/N4A-READBACK.md`）：`viewkickFallDistMin` / `Max` / `MaxScale`、`slideFOVScale` / `LerpInTime` / `LerpOutTime`、`sprinttiltMaxRoll`、`grapple_roll*`、`ziplineRoll*`（N2-C）
- [x] `ziplineJumpOffSpeed`：预期 **400**（N2-P2 Z-01）→ **命中**
- [x] ConVar `jumppad_vert_override_ducked_scalar`：客户端原生默认 **1**，本地生效 0.5（SDK dedi）[hyb]，预言只对了一半（F-02）
- [x] 其余 census 没读过的 setfile 键（Gibraltar 666 个全部读出，`n4/classvars-gibraltar.csv`）
- [x] 其他传奇再读一次 → 12 个传奇，`n4/classvars-by-legend.csv`（138 个键因传奇而异）

**B. 新的行为预言**（需要设计实验，用现有 runner）

- [x] **SG 窗口分界**（M-04）→ 用 M8 数据换算：分界是时间（结束前约 0.1 s），不是动画比例
- [ ] **钩爪脱钩细节**：P-09 已确认（M10 数据，从未触发 +200）；P-08 越过锚点、P-10 视线离开需要专门场景

- [x] ~~lurch 夹紧随 msc 变化~~：M4 Octane 已经测过（stim 下 294.67 = 0.7 × 冲刺上限），和原生公式一致（N2-L L-05）
- [x] **地面按键急转**（N3 高影响 G-07）→ 已确认（N4B_keyturn）：冲刺中 A↔D、W→D 急转，看速度方向是渐进还是瞬间。原生预期：偏离部分按 1250 减速，意图方向按加速度增长
- [x] **超速连跳**（N4C：405 → 305，确认 max(v − 100, 299)）：落地 1.0 s 内以 450 起跳，出口应为 **350**（max(v − 100, 299)），不是 299（N2-J J-04）
- [x] **lurch 高速截断**（N4D_lurchcut：1090 有、1110 没有）：水平速度 > 1100 时不再 lurch（S21 客户端原生，N2-L L-10）
- [x] **按住方向键时的摩擦**（N4-B 已覆盖）：意图方向上不超过目标速度的那部分速度不受摩擦，减速只作用在偏离部分（N2-G G-07），用 M2 的 e2 数据先查
- [x] **第一条命令的输入是 0.75，不是 0.5**（N4B 急转里随原生公式一起吻合）：输入曲线 m(2 − m)（N2-G G-08），用 M2 起步数据先查
- [x] **滑铲中只能转向**（N4C：侧向 41.1 u/s²，原生公式逐命令吻合）：滑铲时按 W 不加速，只有侧向分量起作用（N2-G G-12 / N2-S S-07）
- [x] **滑铲加成冷却被每次滑铲刷新**（N4C：确认）：连续短滑铲时加成迟迟不恢复（N2-S S-02）
- [x] **钩爪低速超时脱钩**（N6 第四次场景测出：空中 1.5 s 一致，`n6/N6-MEASURE.md` §1.3）：速度低于 250 持续 1.5 s（空中）/ 0.7 s（地面）后自动脱钩（N2-P2 P-07）

**C. 还对不上、要细查的**

- [x] 按住下蹲时滑铲的结束速度：在移动后速度 < 125 时结束；112 是下一条蹲走命令（N4-D）
- [x] 地面停止吸附在哪里 → `WalkMove`：移动后速度 < 1 归零（N4-D）
- [x] 斜坡滑铲项的公式 → g·sinθ·cosθ，和 M8 拟合差 3 % 以内（N4-D）
## N5 之后的阶段顺序（用户 2026-10-23 决定）

1. [x] **N6 补测**（`n6/N6-MEASURE.md`）：P-08、P-10 查清；P-07 第四次场景测出（Gibraltar + 台阶 + 天花板：空中超时 1.5 s）；CAM-05 / 07 / 11 / 20 实测一致，CAM-13 未定，CAM-18 [inf]。原计划：钩爪 P-07（低速超时）、P-08（越过锚点）、P-10（视线离开脱钩）；镜头 CAM-18 / 19（cockpit sway / spring）、冲刺倾斜、钩爪和滑索横滚的逐帧实测
2. [x] **N7 用到 Unity 上**（`n7/N7-UNITY.md`）：用户 2026-10-24 决定 12 条全部按原版改；HSD-Unity 分支 `n7/native-reference`；只改 Reference，回放逐字节不变；待用户试玩（`n7/PLAYTEST-GUIDE-N7.md`）
3. [x] **N8 传送机制研究**（Alter、Wraith、Loba、Ash）：A 共用系统、B 规则、C 原生相位、D 实测、E Unity 对照都完成（`n8/`）；E 用户已决定（2026-10-24）：E-1 / E-2 / E-3 改、E-6 标明设计值、E-4 / E-5 不改，已在 HSD-Unity `n8e/teleport-native` 实现（`n8/N8-E-UNITY.md` §4–5）

- [x] **N5** 汇总报告和 Reference 修改建议 → `N-REPORT.md`、`n5/REFERENCE-CHANGES.md`、`n5/FIT-TO-NATIVE.md`（核对 Unity 后更正 G-07、S-09、L-10、CAM-01b）
  - [x] 更新 `STATIC-VALUES.md` 和 `convar-defaults/`（PR #28 已合并，2026-10-24）
  - [ ] 用户决定 Reference 修改建议（`UNITY-CHANGE-PROPOSALS.md` 的"决定"一栏）

---

## N9 升梯、喷气、重力炮（用户 2026-10-24）

- [x] 原生代码 + SDK 对照 → `n9/N9-NATIVE.md`：升梯原生函数找到（常量和 SDK 相同）；喷气原生常量和 SDK `ApplyJetpack` 相同，Unity 一致；重力炮只做替换速度 + 共享 1 s 冷却，没有相位检查和空中控制锁。账本 F-03 ~ F-07
- [x] 用户决定（2026-10-25）：L-1 按原版改、L-2 改、C-1 不做（不加重力炮）；Unity 实现见 `n9/N9-NATIVE.md` §7
- [x] **N11** 用户提出的两组遗留（2026-10-25）→ `n11/N11-OPEN-ITEMS.md`：superglide 402 / 1.1 × 299 = 原生 `Jump` 的 +30 u/s（LEDGER-OPEN-5 已解释，补读了法线谁写）；升梯跳过条件 +0x4838 = Newcastle 城墙跳阶段，`0x140a393b0` = 玩家发射系统
- [x] J-1（用户决定 2026-10-25：做）：Unity 加 +30 u/s 起跳规则 → HSD-Unity#33

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
