# Handoff：HSD 扩展项里 Apex 有原型的部分（在 R5 研究）

写给接手的 Agent。写于 2026-10-29，作者是 TF2 研究的 Leader 会话。用户会把这份交给你。

## 1. 背景

- **HSD（High Speed Doom）** 是 Unity 做的 Apex 手感游戏，**最终是 PvE**。现在只有移动和移动技能，**没有血量、伤害、武器、敌人**。
- 用户 2026-10-29 决定扩展 HSD：以后要做一批技能、投掷物、增益和 3–4 台泰坦。清单在 `TF2-Research/expansion/`：
  - 铁驭清单 [PILOT-LIST.md](PILOT-LIST.md)；
  - 设计清单 [DESIGN-LIST.md](DESIGN-LIST.md)，含用户的总体决定，先读第 1 节。
- 用户定的原则：**Apex 有原型的，用 Apex 做参考**。下面这些交给你在本地 R5 研究；没有 Apex 原型的在 TF2 那边做，不归你。
- **目标是"先研究、存档备用"**：先把**机制怎么实现**研究清楚（规则、状态、时序、范围、和移动的交互）。数值照样记下来，但不用为数值做大量重复试验；HSD 战斗框架建好后会再回来调。
- **只借规则和数值**，不用 Apex 的模型、贴图、声音、动画。

## 2. 研究项

每项回答"它怎么运作"，写成 HSD 能照着实现的规则：触发、持续、范围、形状、对谁生效、和移动 / 视线 / 掩体的关系、冷却和充能。数值标来源：脚本行号、武器 `.txt`、ConVar、实测。

| # | Apex 项 | 对应 HSD 清单项 | 重点 |
|---|---|---|---|
| 2.1 | **破片手雷** Frag | 破片手雷 | 投掷弹道（出手速度、重力、反弹、继承玩家速度）、引信、伤害半径曲线、自伤和击退 |
| 2.2 | **电弧星** Arc Star | 电弧手雷（EMP 类） | 黏附规则、引爆延迟、减速 / 致盲效果的半径和时长 |
| 2.3 | **铝热剂手雷** Thermite | 火焰星 | 火墙形状（方向、长度）、持续、伤害区 |
| 2.4 | **扫描**：Bloodhound 战术；可对照 Seer 战术 / 心跳传感器、Crypto 无人机 | 扫描效果 | 扫描形状（锥形 / 球形）、范围、穿墙、现形时长、敌人怎么显示（轮廓 / 标记 / 小地图）、对扫描者的提示 |
| 2.5 | **分身**：Mirage 战术（可操控分身）、Mirage 大招（多分身） | 全息分身、"一次放多个"升级分支 | 分身的移动规则（照搬玩家动作？沿视线跑？会不会跳、滑铲）、持续、被打消失、操控方式、多分身怎么散开 |
| 2.6 | **全图透视类**：Bloodhound 大招、Crypto、Seer 大招等 | 地图透视 buff | 挑最接近"看见所有敌人"的一个：显示方式、范围、持续、刷新频率 |
| 2.7 | **Fuse**：被动（投掷物扔得更远、多带一个）、战术指节集束弹 | 用户自创"投掷物发射器" | 被动让投掷物的出手速度 / 射程变了多少；集束弹的发射弹道。**先确认本地 R5（S21）里有没有 Fuse** |
| 2.8 | **抛物线显示** | 抛物线显示开关 | **先确认 Apex 有没有投掷物的弹道预测线**（用户记得有，Leader 不确定）。有的话：怎么算（步长、反弹、落点标记）、什么时候显示；没有就写"没有"，TF2 那边会研究 |
| 2.9（可选） | Rampart 加强掩体 Amped Cover | A 型墙（TF2 那边也在做） | 有余力再做：尺寸、血量、从后面打出去的伤害加成。可以只做静态对照 |

## 3. 环境和规矩（沿用 HSD 研究的惯例）

- **游戏：** 本地 R5Flowstate `C:\Users\<user>\Games\R5Flowstate`。它是 S21 客户端 + S3 dedi + SDK 的混合构建，注意客户端和 dedi 的差别（见既有报告的 [hyb] 标注）。只在本地离线，不碰官方服务器。
- **共用机器：** R5 和 TF2 实验轮流用这台机器。启动 r5apex 前先看 `C:\Workspace\Playground\ReApex-DataAnalysis\GAME-LOCK.txt`：第一个词是 `tf2` 就等它删掉；然后写 `r5 <会话名> <时间>`，全部结束、游戏关掉后删掉。TF2 研究的下属会话这段时间也在排队用游戏。
- **工具：**
  - 自动化 runner `Apex-MovementAnalysis/research/phase2-local/tools/hsd_session.py` / `hsd_trial.py`；
  - 脚本源码 `research-src/s21-platform`；
  - 静态值惯例 `research/phase2-local/static-values/`；
  - Ghidra 工程 `ghidra-projects/r5apex.gpr`，读 ConVar 默认值的脚本在 `research/rea-native/convar-defaults/ghidra/`。
- **Python：** 用 `C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe -I`。
- **不改 Unity**（HSD-Unity），这次只研究。
- **产出（用户 2026-10-29 改定）：**
  - 研究成果放在 **`TF2-Research/expansion/apex/`**，不放 Apex 仓库，也不开 PR。用户的说法："虽然是从 Apex 来的，但它还是隶属于 TF2"。
  - 主报告 `APEX-REPORT.md`，中文，每项一节，每节先写"HSD 怎么做"再写依据。开头标注：**来源：Apex（本地 R5），归属：TF2 扩展研究**。
  - 自己写的脚本、实验表、分析工具也放在这个文件夹。实测数据如果由 `hsd_session.py` 写进 Apex 仓库的 `data/`，报告里写清路径即可。
  - **不改 `Apex-MovementAnalysis` 仓库里的已有文件。** 万一必须改 runner 或日志工具，先停下来告诉 Leader。
  - 报告写完后，在 [DESIGN-LIST.md](DESIGN-LIST.md) 或 [PILOT-LIST.md](PILOT-LIST.md) 对应行补一句"Apex 研究见 …"。

## 4. 做完的标准

- 2.1 – 2.8 每项都有"机制规则 + 数值 + 来源"，或写清"本地构建里没有 / 测不了"及原因；
- 投掷弹道（2.1）给出 HSD 能直接用的公式和参数；
- 报告在 `TF2-Research/expansion/apex/APEX-REPORT.md`，开头带来源和归属的标注。
