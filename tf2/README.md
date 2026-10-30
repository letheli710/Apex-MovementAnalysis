> **这个文件夹是什么（FND-1，2026-10-30 加）**
>
> - 这里是工作区 `C:\Workspace\Playground\ReApex-DataAnalysis\TF2-Research\` 在 2026-10-30 03:00 的完整副本（T0–T6、T-1/T-7、W1–W5、夜间研究 N1–N6、TF2X 扩展、泰坦 T0 `expansion/titan/`、runner 工具和全部实测数据 `runtime/data/`），不含 `__pycache__`。
> - **这个 PR 合并之前，工作区的 `TF2-Research` 仍是正在用的工作副本**；合并以后，新会话应改在研究仓库的 `tf2/` 里工作（runner 的锁路径 `GAME-LOCK.txt` 是绝对路径，不受影响）。
> - 不进 git 的部分（`local/` 解包文件和反编译原文、各次实测的 `raw.log` 原始日志，仓库是公开的）复制在 `C:\Workspace\Playground\ReApex-DataAnalysis\_archive\tf2\`，逐个文件的大小和 sha256 见 [ARCHIVE-INDEX.md](ARCHIVE-INDEX.md)。没有超过 50 MB 的文件。
> - 报告从下面的索引进：总报告 [TF2-REPORT.md](TF2-REPORT.md)、和 Apex 对照 [TF2-VS-APEX.md](TF2-VS-APEX.md)、实测 [runtime/T5-REPORT.md](runtime/T5-REPORT.md)、泰坦 [expansion/titan/T0-REPORT.md](expansion/titan/T0-REPORT.md)、扩展清单 [expansion/](expansion/)。
> - 有些链接指向工作区里仓库以外的地方（`../ghidra-projects/tf2/`、`C:\Tools\`），在仓库里打不开，按原样保留。
>
> 下面是原 `TF2-Research/README.md` 的原文。

# TF2 研究：索引

计划：[TF2-PLAN.md](TF2-PLAN.md)。

**总报告：[TF2-REPORT.md](TF2-REPORT.md)**（结论 + Unity 改动提案和批准表）

**下一步：[ROADMAP.md](ROADMAP.md)**（成果、已批准要做的事、实践前要补的研究 D-1–D-8；用户 2026-10-29 决定先研究、后实践）

**夜间研究（2026-10-29）：[overnight/OVERNIGHT-REPORT.md](overnight/OVERNIGHT-REPORT.md)**：TF2 里还值得研究的设计（窗户辅助、钩爪实测、被砍掉的 Boost 职业、Gauntlet 等）

**给人读的汇总**
- [TF2-VS-APEX.md](TF2-VS-APEX.md)：TF2 和 Apex 的规则对照，以及 Apex 改了什么。
- [TF2-MOVEMENT-SUMMARY.md](TF2-MOVEMENT-SUMMARY.md)：TF2 每个动作怎么实现、用了哪些数值。

**接手 T5 实测的会话从 [HANDOFF-T5.md](HANDOFF-T5.md) 开始。**

**决定**：蹬墙跑基准用 B（TF2 规则 + R5 残留数值），A（TF2 原版）做成可开关的预设（2026-10-28）。

各阶段报告：

| 阶段 | 状态 | 报告 | 主要产出 |
|---|---|---|---|
| T0 盘点与环境 | 完成（2026-10-28） | [t0/T0-REPORT.md](t0/T0-REPORT.md) | 二进制清单、VPK 解包、`.set`/`.nut` 位置图、测试画面 |
| T1 静态参数 | 完成 | [static-values/T1-REPORT.md](static-values/T1-REPORT.md) | `setfile-values.csv`、`convar-values.csv`（含 R5 对应值）、`.set` schema 表 |
| T2 共用底层差异 | 完成（T5 后只剩 T-M01 待定） | [ledger/T2-REPORT.md](ledger/T2-REPORT.md) | `ledger.csv`（41 项） |
| T3 蹬墙跑 | 完成（静态），等你选版本 | [wallrun/T3-REPORT.md](wallrun/T3-REPORT.md) | TF2 原版规则、R5 残留、M7 对照 |
| T4 独有设计 | 完成（初稿） | [unique/T4-REPORT.md](unique/T4-REPORT.md) | 分档清单 |
| T5 运行时测量 | 完成（2026-10-29） | [runtime/T5-REPORT.md](runtime/T5-REPORT.md) | 共用底层、蹬墙跑、二段跳、兴奋剂实测；工具说明 [runtime/README.md](runtime/README.md) |
| T-1 / T-7 EPG 火箭跳、投掷物击退 | 完成（2026-10-29），只研究 | [epg/T1-T7-REPORT.md](epg/T1-T7-REPORT.md) | 真实开火实测，和 R5 #64 逐项对照 |
| T6 报告与提案 | 完成（2026-10-29），提案等你逐项批准 | [TF2-REPORT.md](TF2-REPORT.md) | 总结论、蹬墙跑 A / B / M7 数值表、提案 P-01–P-06 和批准表 |

`local/` 放解包文件、反编译原文和备份，不进版本库。Ghidra 工程在 `../ghidra-projects/tf2/`。工具在 `C:\Tools\`：`tf2vpk\`、`go1.27.3\`、`tf2vpk-src\`。
