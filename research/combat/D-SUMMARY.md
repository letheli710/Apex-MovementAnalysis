# 批次 D 汇总：伙伴 / 无人机 / 分身（静态研究）

会话 `combat-d`，2026-10-31。第一波：只读 `research-src/s21-platform/scripts/`，没开游戏、没改 HSD-Unity。模板：`SYSTEM-RECORD-TEMPLATE.md`；过滤表：`C0-ABILITY-FILTER.md`。

## 1. 每项一行

| # | 技能 | 记录 | 一句话结论 | 分类 |
|---|---|---|---|---|
| 1 | Lifeline 战术 D.O.C. | [lifeline-heal-drone/SYSTEM.md](lifeline-heal-drone/SYSTEM.md) | 一套完整的"指派 + 跟随 + 瞬移 + 范围治疗绳"系统；**服务端是 SDK 社区重写的**，公式可用但不等于 S21 正版。更正了两条已有要点：速度上限是 `1.6·\|v_t\| + 120 + 3·dist`；跟随点在目标**右后方** 72.5 u、高 70，不是正头顶。`mp_ability_lifeline_halo` 是 Revived 大招（地面护盾区 + 快速治疗），只共用模型 / 粒子 / 清理信号，和战术无逻辑关系 | 系统、可视化 |
| 2 | Crypto 战术 Surveillance Drone | [crypto-drone/SYSTEM.md](crypto-drone/SYSTEM.md) | "玩家坐进远处的实体"的完整模板（建载具、进 / 出视角、按键重绑、淡出淡入、自动换弹、召回、超距）；飞行物理在引擎，速度未知；Neurolink 视野判断是社区补写的（240° 扇形）；本地被打不会被踢出视角 | 系统、可视化 |
| 3 | Crypto 大招 Drone EMP | [crypto-drone-emp/SYSTEM.md](crypto-drone-emp/SYSTEM.md) | 2.5 s 蓄力 + 预警 → 30 m 球形：破盾 ≤50、玩家减速 0.35 / 转向 0.7 / 2 s、敌方装置按登记表溶解 / 扣血 / 关闭；**一般 NPC 只破盾不减速**；友军（含 Crypto 本人）也会被减速 | 好技能、系统 |
| 4 | Mirage 战术 Psyche Out | [mirage-decoy/SYSTEM.md](mirage-decoy/SYSTEM.md) | 分身 = 引擎 `player_decoy`，移动全在引擎；仇恨 = 和主人同一个 AI 优先级；**只有敌方玩家打分身才会被标记**（NPC 不会）；三种移动模式、删旧建新式的模式切换、全服数量上限 | 系统 |
| 5 | Mirage 大招 Life of the Party | [mirage-ultimate/SYSTEM.md](mirage-ultimate/SYSTEM.md) | 1 s 蓄力（隐身 1.1 s + 加速 0.15）后 6 个分身按 0 / ±60 / ±120 / 180° 交替排在身边 30 u 处各自往外跑 5 s；本地还残留 S21 "Kaleidoscope" 版的常量但没接上 | 系统、可视化 |
| 6 | Lifeline 大招 Care Package | [lifeline-care-package/SYSTEM.md](lifeline-care-package/SYSTEM.md) | 抛物线选点 + 9 项地形检查 + 动画驱动下落 + 预告（地面标记 / 威胁指示 / AI 禁区）+ 落地冲击（压坏 72 u、推开 350 u/s、震屏）；**同文件夹的 `ai/_droppod.gnut` 有一套 NPC 空投舱刷兵**（落地开门放 ≤4 个 NPC），PvE 刷怪可以直接照搬 | 系统、可视化 |

## 2. 可拆出的公共部件（`_shared/`）

| 文件 | 部件 | 来源技能 | 谁能复用 |
|---|---|---|---|
| [D-FOLLOW-MOTION](_shared/D-FOLLOW-MOTION.md) | 跟随运动：偏移目标点 + 比例速度 + 继承目标速度 + 一阶平滑 + 超距 / 断视线瞬移 + 速度→姿态 | D.O.C. | 伙伴、宠物、护盾球、跟随扫描器 |
| [D-TARGET-ASSIGN](_shared/D-TARGET-ASSIGN.md) | 锥内选最正对象（0.1 s 扫描 + 网络变量）、改派 / 召回、没有就给自己 | D.O.C.（对照 Conduit，未读） | 给伙伴下令、锁定类技能 |
| [D-REMOTE-DRONE](_shared/D-REMOTE-DRONE.md) | 可操控载具：进 / 出视角、身体冻结、按键重绑、HUD 换皮、召回 / 超距 / 被毁 | Crypto 无人机 | 遥控无人机、操控炮台 / 伙伴 |
| [D-DEVICE-REGISTRY](_shared/D-DEVICE-REGISTRY.md) | 装置登记表（Destroy / Damage / Disable 三种反应）+ 半径查询 | Crypto EMP | 所有"范围内影响敌方装置"的技能 |
| [D-DECOY-AI](_shared/D-DECOY-AI.md) | 分身：外观 = 主人、AI 优先级 = 主人、三种移动模式、被打结算、数量上限、环形排布 | Mirage 两项 | 诱饵、嘲讽、影分身 |
| [D-DROP-POD](_shared/D-DROP-POD.md) | 空投舱：选点、合法性、动画下落、预告、落地冲击、内容（补给 / NPC） | Care Package + `_droppod` | 补给、**刷敌人**、砸地类技能 |

和别的批次的交叉：EMP 的状态效果和批次 B 的 [`B-electric-emp.md`](_shared/B-electric-emp.md) 是同一组（`move_slow` / `turn_slow` / `emp`），但 Crypto EMP 不走 `Electricity_DamagedPlayerOrNPC`，所以不击晕 NPC。

## 3. 最重要的实测项（第二波，按价值排）

| # | 测什么 | 为什么重要 | 怎么测 |
|---|---|---|---|
| 1 | D.O.C. 无人机实际轨迹（站 / 走 / 冲刺 / 滑铲 / 转身） | 跟随运动是本批最想复用的部件；脚本是社区重写的，要确认本地行为 = 公式，并找正版录像比"像不像" | 训练场，AgentLink 每 0.05 s 记 scriptname `follow_medic` 实体和玩家位置（改 W4 `w4_probe.py`），对照 lifeline-heal-drone 3.2.2 |
| 2 | 空投舱下落曲线和两个动画事件的时刻 | 下落全在动画里，脚本没有数字；PvE 刷怪表现要用 | 训练场放大招，记舱体位置；站在落点上记被推时刻 |
| 3 | Crypto 无人机飞行速度 / 加速度 / 最远距离 | 引擎载具，脚本里没有 | 进视角按住前进 / 上升 / 下降，记 `crypto_camera` 位置 |
| 4 | 分身被打是不是一下消失、AI 会不会优先打分身 | 决定 HSD 分身"血量制"还是"一碰就散"，以及仇恨模型 | 训练场 P2020 打一枪；能刷 NPC 的话看 NPC 开火目标 |
| 5 | EMP 减速曲线（Crypto 自己会被减速） | 验证 0.35 → ×0.65 和 2 s + 1 s 渐出 | 无人机放脚边放 EMP，记冲刺速度 |

## 4. 遇到的问题

1. **SDK 重写**：D.O.C.（`mp_ability_lifeline_follow_medic.nut`）和 Halo（`mp_ability_lifeline_halo.nut`）几乎可以确定是社区重写的：Flowstate 专属逻辑、英文解释注释、5 个声明了不用的 S21 常量、治疗 / 绳参数和 S3 老无人机完全一样。git 只有一次提交，没法从历史确认。Crypto 无人机的 Neurolink 视野、无人机"用东西"、EMP 的地上护甲部分也是社区补的（注释写明）。已写进共享日志。
2. **引擎行为看不到**：分身移动、Crypto 飞行、空投舱下落都在引擎或动画里，静态研究只能给结构，数字要等实测。
3. **对 PvE 不友好的原版规则**：EMP 不减速一般 NPC；分身只标记玩家打手。HSD 应该有意改掉，记成"有意差别"进 `R5-DIFF-ARCHIVE.md`（现有 HSD 分身已经是"任何攻击者都标"）。
4. **本地是混合版本**：Mirage 大招是老版"6 个散开"，但文件里有 S21 Kaleidoscope 版常量没接上；Crypto 出视角加速天赋函数存在但没人调用。
5. 没找到 `aiEnemy_priority` 的玩家值（玩家设置文件不在本地仓库），分身的 AI 优先级只能写"和主人相同"。
6. 共享 worktree：按要求没 commit、没切分支，只写了本批文件夹和 `_shared/D-*`。
