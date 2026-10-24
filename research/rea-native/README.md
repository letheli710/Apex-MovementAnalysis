# REA 原生移动系统研究

这个文件夹专门存放用 REA（+ Ghidra）研究 R5Flowstate 原生代码的成果。建立于 2026-10-23。

**目标**：给原生移动系统画一张完整地图，把它当作**解释层**，和我们 M2–M10 的黑盒实测互相验证：

- 代码告诉我们公式长什么样、有哪些分支和条件；
- 实测确认这个公式在游戏里确实这样运行；
- 对不上的地方列进对照账本，再逐项细查。

## 文件

| 文件 | 内容 |
|---|---|
| [REA-PLAN-DRAFT.md](REA-PLAN-DRAFT.md) | 计划草稿（待用户审阅） |
| [TODO.md](TODO.md) | 本研究的待办，包括暂缓的研究方向（传送类机制） |
| [N0-PILOT.md](N0-PILOT.md) | N0 环境和试点：二进制检查、两个客户端的对比、定标、闸门结论 |
| [convar-defaults/](convar-defaults/README.md) | 35 个原生 ConVar 的默认值（会话「从 rea 获取精确数值」的成果，PR #28） |
| [NATIVE-MAP.md](NATIVE-MAP.md)、`map/*.csv` | N1 骨架地图：函数、参数读取、setfile 键、SDK 钩子 |
| [camera/CAMERA-INVENTORY.md](camera/CAMERA-INVENTORY.md)、`map/camera-effects.csv` | N1 / C1 第一人称镜头效果清单，见计划 §5.1 |
| `n0/`、`n1/` | 各阶段的脚本和输入（只有地址和名字） |
| `n4/` | N4 实测：[N4A-READBACK.md](n4/N4A-READBACK.md)（setfile 键补读）、[N4B-KEYTURN.md](n4/N4B-KEYTURN.md)（地面急转）和脚本 |
| `subsystems/N2-*.md` | N2 各子系统的公式提取（P1：G、L、J、S、T、M；P2：钩爪、滑索、跳板；镜头 C2） |
| `n2/` | N2 的反编译和标注工具（反编译输出只写进 `local/`） |
| [CROSSCHECK-LEDGER.md](CROSSCHECK-LEDGER.md)、[ledger.csv](ledger.csv) | N3 代码 × 实测 × Unity 对照账本（78 条） |
| [UNITY-CHANGE-PROPOSALS.md](UNITY-CHANGE-PROPOSALS.md) | 待用户决定的 Unity 修改建议（来自账本，实测后统一决定，不自动改） |
| `local/` | **只在本机**：反编译原文、Ghidra 导出、大段伪代码。不进 git（见 `.gitignore`） |

## 公开仓库规则

本仓库是**公开的**。反编译出来的是 Respawn 的代码，所以：

- 提交到 git 的只有：地址、函数名（我们起的）、用我们自己的话重写的公式、常量、分支条件，以及很短的必要摘录；
- 大段伪代码和汇编只放 `local/`；
- 和原始游戏日志的规则一样，本机路径和原始数据不进 git。

## 证据标签（在原有标签上新增）

| 标签 | 含义 |
|---|---|
| [native] | 从原生代码直接读出（常量、公式、分支），反编译结果清楚、没有歧义 |
| [native-inf] | 从原生代码读出，但需要推断（例如结构体字段含义、内联代码的边界、浮点常量的用途） |

原有标签 [meas] [fit] [src] [sdk-cvar] [census] [inf] [hyb] 照旧使用。

## 工具位置

REA 在 `C:\Tools\rea`，Ghidra 12.1.4 在 `C:\Tools\ghidra_12.1.4_PUBLIC`。工具不放进项目，分析产出放进项目。
