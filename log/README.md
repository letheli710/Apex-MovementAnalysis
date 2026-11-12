# log/：共享实时日志的快照

所有会话共用的实时日志是"HSD 版本溯源"页面的数据库（collection `log`）：https://claude.ai/artifact/NCjBNDQZPUYoTwdfHdcNEa 。写法见 [../workspace/CLAUDE.md](../workspace/CLAUDE.md) 第 1 节。

这里的文件是那个数据库在某一时刻的**导出快照**，让日志有 git 里的版本记录（计划 1.4：以后每个日志 PR 附一份新的导出）。线上的数据库才是活的那一份，快照之后写的条目不在文件里。

| 文件 | 导出时间 | 条目数 |
|---|---|---:|
| [log-export-2026-10-30.json](log-export-2026-10-30.json) | 2026-10-30 03:10（FND-1） | 129 |
| [log-export-2026-10-31.json](log-export-2026-10-31.json) | 2026-10-31（记录对齐 10-31） | 183 |

格式：一个 JSON 数组，按文档 id（`_id`，即日志里的 `日期-会话短名-主题` 或早期的 `t01-01` 这类编号）排序；其余字段和数据库里一样（`topic`、`role`、`kind`、`phase`、`date`、`sortDate`、`order`、`name`、`data`、`why`、`sw`、`rec`、`session`、`ts`、`resolved`）。导出方法：`ArtifactData` 的 `list`（`limit` 1000，一页取完），每条存成文件后合并。
