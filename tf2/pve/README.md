# TF2 PvE 研究：敌人 AI 和 Frontier Defense

2026-11-08 开始，来源 [../MUST-RUN-1108.md](../MUST-RUN-1108.md) 第 1、2 项。HSD 最终是 PvE（D-59），Apex 没有成套的敌人原型，所以从 TF2 读敌人和 FD 的规则。只借规则和数值，不用 TF2 的模型、声音、动画。

## 先说结论

- 敌人的数值、行为树、计划表都在文件里，而且是 Respawn 原版，读完就能照着搭（[AI-SPEC.md](AI-SPEC.md)）。每一步的具体做法（怎么找掩体、子弹怎么偏）在原生代码里，由实测和 Ghidra 补（[AI-LIVE.md](AI-LIVE.md)）。
- FD 只有客户端和数据表能读；**每一波刷什么，本地没有任何文件**（[FD-RULES.md](FD-RULES.md)）。

## 文件

| 文件 | 内容 | 谁写 |
|---|---|---|
| [AI-SPEC.md](AI-SPEC.md) | 敌人规格：图鉴、行为树、计划、感知、出场、命中规则；最后一节"能不能脱离 TF2" | `tf2-ai-spec`（读文件） |
| [FD-RULES.md](FD-RULES.md) | FD 能读到的规则：难度、波次状态机、经济和商店、采集器、泰坦升级 | `tf2-ai-spec` |
| [BEHAVIOR-TREES.md](BEHAVIOR-TREES.md) | 附录：全部 36 棵行为树的流程图和表、选择器词表（脚本生成） | `tools/bt_sched.py` |
| [SCHEDULES.md](SCHEDULES.md) | 附录：全部 126 个计划的任务和打断条件（脚本生成） | `tools/bt_sched.py` |
| [AI-LIVE.md](AI-LIVE.md)、`live/` | 敌人实测和原生代码 | `tf2-ai-live` |
| `data/` | 从游戏文件生成的表（见下） | `tools/` |
| `tools/` | 生成脚本 | `tf2-ai-spec` |

### `data/`

| 文件 | 内容 |
|---|---|
| `aisettings-resolved.tsv` | 145 种 NPC 的每个设置键，多人值 / 战役值 / 出处（`#base` 已展开） |
| `behavior-trees.tsv` | 每棵树每一项（块、顺序、条件、是否注释掉、行号） |
| `bt-users.tsv` | 每棵树被哪些 NPC 设置文件用（多人 / 战役） |
| `schedules.tsv` | 每个计划的每个任务和打断条件，带行号 |
| `weapon-npc-keys.tsv` | 111 把武器的 `npc_*` / `proficiency_*` 键和几个对照键，多人 / 战役 |

### `tools/`（都在 `pve/` 下用 `py -3 -I tools/<脚本> …` 跑，参数见 AI-SPEC 第 1 节）

| 脚本 | 做什么 |
|---|---|
| `kv_resolve.py` | 解析 `aisettings/*.txt`：`#base` 继承、`[$mp]` / `[$sp]` 标签、嵌套块 |
| `bt_sched.py` | 解析行为树和 `common_schedules.txt`，生成两份附录和三张表 |
| `bt_gloss.py` | 66 个选择器的中文名、做什么、可能返回的计划（全部按名字推断） |
| `weapon_npc_keys.py` | 解析武器 `.txt` 的 NPC 键（`MP_BASE` / `SP_BASE` 分开，跳过 `Mods`） |
| `key_table.py` | 从上面的 TSV 打印任意键 × 任意 NPC 的表 |
| `fill_spec.py` | 重新生成 AI-SPEC 里的表和流程图 |

## 原始文件在哪

- 游戏解包文件：`TF2-Research/local/vpk/`（私有仓库 `HSD-RawData` 的 `tf2/local/`）。
- Northstar 1.31.14 服务端 mod 和 playlist 表：私有仓库 `HSD-RawData` 的 `tf2/northstar-1.31.14/`（HSD-RawData#11）。
