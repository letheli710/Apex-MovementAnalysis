# TF2 REA 计划

状态：用户已确认（2026-10-28）。执行者按本文件工作，所有 TF2 研究产出都放在本文件夹里。

## 0. 定位：R5 是基准，TF2 只用来补

- **手感基准仍然是 R5。** 受众是 Apex 玩家。凡是 R5 已有、且已测过的数值或规则，一律以 R5 为准，TF2 不覆盖。
- **TF2 只做三件事：**
  1. **补 R5 缺的原版实现。** 首先是蹬墙跑、挂墙、二段跳：M7 当时没有原版可对照，是我们自己设计的。
  2. **验证共用底层。** 确认两边同源的移动代码哪些一样、哪些被 Apex 改过。改动本身能说明 Apex 为什么"这样调"。
  3. **列出 TF2 独有的设计**，供 HSD 选用（作为可开关的模块，默认关）。
- **和 R5 工作并行，互不影响。** R5 的研究仓库、HSD-Unity 仓库、R5Flowstate 都只读，不改任何东西。

## 1. 已知前提

- TF2（2016）和 Apex（2019）都是 Respawn 魔改的 Source 引擎。Apex 的代码从 TF2 分出来，移动代码、playersettings（`.set`）、ConVar 体系同源。
- 安装路径：`C:\SteamLibrary\steamapps\common\Titanfall2`，`gameversion.txt` 是 v2.0.11.0。Northstar 已装好（`NorthstarLauncher.exe`、`R2Northstar\`）。
- 逻辑分散在几个 DLL 里：根目录的 `server.dll`，以及 `bin\x64_retail\` 下的 `client.dll`、`engine.dll` 等。比 R5 的单个 exe 好拆。
- 资源包在 `vpk\` 目录。

## 2. 阶段

### T0 盘点与环境
- 记录版本号、DLL 清单、Northstar 版本。
- **解包 VPK：用社区现成的 VPK 工具**（用户已批准，2026-10-28）。TF2 的 VPK 用 LZHAM 压缩，选一个能处理 LZHAM 的知名工具。从工具的官方发布页下载，下载前告诉用户工具名、来源和大小；在报告里记录来源和版本。工具放在 `C:\Tools\` 下，不放进本文件夹。
- **配置测试画面**（见第 3 节）。
- 产出：文件清单、`.set` 和 `.nut` 的位置图、T0 报告。

### T1 静态参数
- 读取铁驭（pilot）的 playersettings：速度、加速度、摩擦、跳跃、蹬墙跑、二段跳、滑铲。
- 从 DLL 读取 ConVar 默认值，复用 R5 的 Ghidra 方法和脚本（只读引用，复制到本文件夹再改）。
- 产出：`static-values/`，每项带一列"R5 对应值"。

### T2 共用底层差异表
- 以 R5 的 `NATIVE-MAP` 为索引，在 TF2 里找每个函数的对应实现（靠字符串、ConVar 名、调用结构定位）。
- 每项分成四类：相同 / 改过 / R5 已删除 / TF2 没有。
- 重点看：地面摩擦和加速、空中加速、滑铲和 slide hop 叠速、跳跃、攀爬和翻越、落地，以及镜头（落地踢、晃动、侧倾）。
- 产出：差异账本，格式沿用 R5 的 ledger。

### T3 蹬墙跑专项（重点）
- TF2 原版的蹬墙跑、挂墙、二段跳：贴墙条件、速度规则、重力衰减、持续时间、离墙跳的方向和速度、镜头侧倾。
- 查 R5 里还剩多少蹬墙跑代码（可能还在，只是关掉了）。如果有残留，就能知道"Apex 版蹬墙跑"会长什么样。
- 和 Unity 的 M7 实现逐项对照，列出差异。

### T4 TF2 独有设计清单
初步候选，待 T0 到 T2 补全：
- **铁驭移动**：蹬墙跑、挂墙、二段跳、slide hop 叠速、更高的地速和空中控制。
- **铁驭技能**：钩爪（和 Pathfinder 版对照）、兴奋剂、相位移动、脉冲刀、A-Wall、全息诱饵、隐身。
- **其他**：泰坦移动（冲刺 dash）、骑乘泰坦（rodeo）、Gauntlet 训练场的计时设计。

每项标成三档：可移植进 HSD / 只作手感参考 / 不做。泰坦是否纳入，等研究后由用户决定，T4 先只列出、不深挖。

### T5 运行时测量（Northstar）
- 写一个诊断模组（相当于 R5 的 HSD.MoveDiag），每帧记录位置、速度、状态和镜头。
- 搭一个测试 runner：本地私服，自己一个人，用脚本驱动。机器人能否驱动实验待验证，不行就改成录制输入再回放。
- 测两类：共用基础项（核实 T2 的结论），以及蹬墙跑和 T4 选中的项目。
- 规则：只在本地私服做调试和注入，不碰官方服务器。

### T6 报告与 Unity 提案
- 写 `TF2-REPORT.md`，列出 Unity 改动提案（每项由用户批准，之后另外安排，不在本计划里改 Unity）。
- TF2 独有功能的提案都写成开关，默认关，不影响 R5 基准。

## 3. 测试画面设置（帧率优先）

做法和 R5 一样：窗口化、低分辨率、低画质，保持帧率稳定，方便测量和挂调试工具。

- **窗口化 + 固定分辨率**：优先用启动参数，例如 `-windowed -width 1280 -height 720 -novid`。Northstar 可以把启动参数写进游戏目录里的 `ns_startup_args.txt`（文件名和位置待 T0 核实）。
- **画质全低**：TF2 的画面设置一般存在用户文档目录 `Documents\Respawn\Titanfall2\local\` 下（例如 `videoconfig.txt`，待 T0 核实）。改之前先把原文件备份到 `local/backup/`，研究结束后可以恢复。
- **帧率**：关掉垂直同步，设一个固定帧率上限，并记录实际帧率。R5 的经验是帧率不稳会让测量失真，附加 Frida 这类工具也会拖慢帧率。
- 把最终用的设置和启动参数写进 T0 报告，之后所有测量都用同一套设置。
- 这些设置会影响用户自己玩原版 TF2 时的画面。T0 报告里写清楚怎么恢复。

## 4. 交接说明（给执行的 Agent）

**文件夹**
- 本文件夹：`C:\Workspace\Playground\ReApex-DataAnalysis\TF2-Research`，TF2 的所有产出都放在这里。
- `local/` 放解包文件、反编译代码、游戏脚本原文、备份和大文件（已写入 `.gitignore`）。其余放笔记、报告、脚本、表格。
- 建议目录：`t0/`、`static-values/`、`ledger/`、`wallrun/`、`unique/`、`runtime/`、`mod/`，每个阶段一份报告。
- 现在不建 GitHub 仓库，也不提交到 R5 的研究仓库。以后要不要公开，由用户决定。

**环境**
- 游戏目录**只读**。允许写的只有：`R2Northstar\mods\` 下我们自己的模组文件夹，以及第 3 节的启动参数文件。
- 真正的 Python 是 `C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe`（直接敲 `python` 会打开 WindowsApps 的占位程序）。
- Ghidra 12.1.4 在 `C:\Tools\ghidra_12.1.4_PUBLIC`，REA 在 `C:\Tools\rea`。大文件用 headless 分析（`analyzeHeadless`，`GHIDRA_MAXMEM=16G`）。TF2 的 Ghidra 工程放在 `ReApex-DataAnalysis\ghidra-projects\tf2\` 下，不要动已有的 R5 工程。

**可复用的 R5 资料（只读）**
- `Apex-MovementAnalysis/research/rea-native/NATIVE-MAP.md`、`map/*.csv`、`ledger.csv`：原生代码地图和对照账本，T2 的索引。
- `Apex-MovementAnalysis/research/rea-native/convar-defaults/` 和 `n1/`、`n2/` 下的脚本：读 ConVar 默认值和 setfile 的方法。
- `Apex-MovementAnalysis/research/phase2-local/static-values/`：R5 静态值，T1 对照用。
- M7 蹬墙跑的 Unity 实现在 HSD-Unity 仓库，T3 对照用。
- 这两个仓库的主 checkout 可能停在别的分支上，只读文件，不要切分支、不要提交。

**规则**
- 不改 Unity、不改 R5 相关的任何仓库或游戏目录。
- 下载外部工具前，先告诉用户工具名、来源和大小，得到同意再下载。
- 只在 Northstar 本地私服做调试和注入，不连官方服务器。
- 第 5 节没定的事，执行时按"做法"一栏处理，并在报告里注明。
- 每个阶段结束都写一份简短报告：做了什么、发现了什么、还有哪些未解项。

## 5. 用户决定

| 问题 | 决定 / 做法 |
|---|---|
| 1. 蹬墙跑以哪个版本为准 | **已定（2026-10-28）**：B = TF2 规则 + R5 残留数值，作为基准；A = TF2 原版规则和 MP 数值，做成可开关的预设。依据见 `wallrun/T3-REPORT.md` 第 5 节 |
| 2. 泰坦内容要不要纳入 | 研究后再定。T4 只列出，不深挖 |
| 3. VPK 解包 | 用社区现成的 VPK 工具（已批准） |
| 4. R5 收尾和 TF2 先后 | 并行，互不影响 |
