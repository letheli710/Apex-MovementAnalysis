# REA 原生研究 TODO

建立于 2026-10-23。分两部分：

- **当前**：这一轮要做的事，对应 [REA-PLAN-DRAFT.md](REA-PLAN-DRAFT.md) 的阶段；
- **暂缓**：用户认为值得研究、但明确说**现在不做**的方向。Agent 不得自行开工，等用户发话。

---

## 当前：原生移动系统地图（首要任务）

用户原话（2026-10-23）："我们现在的首要任务是将移动系统构建出一张全面的地图，让我们深刻地、仔细地、原生地了解这个移动系统。"

- [ ] 用户审阅计划草稿，回答 §10 的问题
- [x] **N0** 环境和试点：检查二进制，跑 Ghidra 自动分析，用 `sv_gravity` = 750 和 SDK 命名函数定标，读出原生 ConVar 默认值（ConVar 部分见 `convar-defaults/`），结论见 `N0-PILOT.md`
- [x] **N1** 骨架地图：`NATIVE-MAP.md`、`map/functions.csv`、`map/reads.csv`、`map/sdk-hooks.csv`、`map/setfile-keys.csv`
  - [ ] N1 遗留：8 个 SDK 钩子的地址（`IN_JumpDown` / `IN_JumpUp`、`Glide_*` 等）；51 个没分类的核心函数
- [ ] **N2** P1 子系统公式提取：
  - [ ] T 时序和输入（N2-G 已发现输入曲线 m(2 − m) 和冲刺 × 1.25，从这里接着做）
  - [x] G 地面移动 → `subsystems/N2-G-GROUND.md`（遗留：吸附阈值位置 G-06、Friction 里的 x、几个结构体偏移）
  - [x] J 跳跃、空中、落地 → `subsystems/N2-J-JUMP-AIR.md`（M2 的空中残余增益、连跳惩罚、skip 削减都已解释；遗留 `AirMove` 本体、二段跳分支）
  - [x] L Lurch / tap-strafe → `subsystems/N2-L-LURCH.md`（209.3 夹紧出处已找到）
  - [x] S 滑铲 → `subsystems/N2-S-SLIDE.md`（遗留：斜坡项公式 S-09、按住下蹲时结束速度 125 vs 112 S-05）
  - [ ] M 攀越、mantle、SG、墙
- [ ] **N2** P2 子系统（看用户决定）：P 钩爪、Z 滑索、F 外力类
- [ ] **C 第一人称镜头手感**（camera feel，用户 2026-10-23 加入，计划 §5.1）：随角色动作产生的**全部**镜头效果，不只是跑步晃动、落地震动、滑铲下沉；也包括墙跑、攀爬、跳跃、钩爪、滑索等
  - [x] C1 完整清单：一共有哪些效果、各叫什么、由什么触发、在哪里计算（原生 / 脚本 / 动画）→ `camera/CAMERA-INVENTORY.md`（23 项 + 3 个边界项；跑步晃动还没找到对应参数）
  - [ ] C2 逐个弄清做法：触发条件、幅度、包络、叠加、帧率关系、是否影响准星 → `subsystems/N2-C-CAMERA.md`
  - [ ] C3 逐帧实测：按渲染帧记录镜头位置、角度和 FOV（要改 HSD.MoveDiag，先问用户）
  - [ ] C4 进对照账本（`CAM-`），和 M5.5 镜头对照，只给建议
- [ ] **N3** 对照账本，先放入计划 §6 的种子
- [ ] **N4** 针对性验证（按需；Frida 需用户批准）
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

- N1：513 个 setfile 键从没读过值（`map/setfile-keys.csv` 里 census 以外的键）。可以用 `bridge_classvar_get` 在运行时批量补读，放进 N4。
- N1：SDK 在客户端的核心移动函数上挂了很多钩子（`map/sdk-hooks.csv`）。N2 每个子系统都要先确认相关钩子默认是否开启、改了什么。
- N2-L：`convar-defaults/README.md` 里"夹紧 209.3 没有 ConVar 出处"已经过时（出处是 `jump_grace_max` × msc × `sprintspeed`）。那个文件属于 PR #28，合并后再改。
- N2-L：可测的新预言：lurch 夹紧随 msc 变化（stim、拿武器）。放进 N4。
- N2-J / N2-S：要用 `bridge_classvar_get` 补读的 setfile 键：`antiMultiJumpTimeMin` / `TimeMax` / `HeightFrac`（预测 0.15 / 0.75 / 0.3）、`player_slideBoostCooldown`、`landSlowdown*`。放进 N4，成本很低。
- N2-J：可测的新预言：以 450 连跳，出口应为 350（max(v − 100, 299)），不是 299。放进 N4。
