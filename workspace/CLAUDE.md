# HSD 项目：所有会话都要遵守的规则

工作区：`C:\Workspace\Playground\ReApex-DataAnalysis`。项目是 High Speed Doom（Unity）+ Apex R5 研究 + TF2 研究。

## 1. 共享日志（每个会话都要写）

项目有一份所有会话共用的实时日志，就是"HSD 版本溯源"页面的数据库：

- 页面：https://claude.ai/artifact/NCjBNDQZPUYoTwdfHdcNEa
- 写法：用 `ArtifactData` 工具（先用 ToolSearch `select:ArtifactData` 载入），`url` 填上面的地址，`collection` 填 `log`。
- 什么时候写：**做了一个决定、拿到一份数据、出了一个新版本、合并了一个 PR、发现一个问题**，当场写一条。不要等到会话结束。
- 文档 id：`日期-会话短名-主题`，例如 `2026-10-30-cam-k8`。新文档用 `set`，不带 `if_version`。
- 一个决定有几个选项，就**每个选项写一条**：选中的 `role: "version"`，没选的、旧版留开关的 `role: "parallel"`，还没定的 `role: "pending"`。没选的也要写数据和理由（留档）。
- "还要定"的事定下来以后：把原来那条 `update` 成 `"resolved": true`（先 `get` 拿到 version 再用 `if_version`），**不删**，再写一条新的 `version`。
- 不删任何条目。写错了就 `update` 改正，并在 `why` 里注明改过。

字段（全部是字符串，`order` 是数字，`resolved` 是布尔）：

```json
{
  "topic": "镜头",
  "role": "version",
  "kind": "decision",
  "phase": "U",
  "date": "10-30", "sortDate": "2026-10-30", "order": 1,
  "name": "一句话：做了什么 / 选了什么",
  "data": "数据：R5 多少、Unity 改前多少、改后多少",
  "why": "为什么这么选 / 为什么改",
  "sw": "开关或切回旧版的方法",
  "rec": "PR、D-xx、报告路径",
  "session": "会话短名",
  "ts": "ISO 时间",
  "resolved": false
}
```

- `topic` 用已有的功能名：地面移动、传奇能力、滑铲、翻越和 superglide、Lurch / tap strafe、手感怎么验收、斜坡、回放电机、钩爪、镜头、跑墙 · 二段跳、战斗和扩展道具、火箭跳。新功能可以起新名字，页面会自动多一条。
- `role`：`version`（这个功能新的现在版本）、`parallel`（平行保留 / 没选）、`pending`（还要定）、`note`（只进日志流，比如 PR 合并、计划、问题）。
- `kind`：`decision`、`data`、`version`、`milestone`、`issue`、`plan`。
- `phase`：`M` 正线 M0–M10、`N` REA 原生、`S` 副线、`R` 按 R5 复刻、`T` TF2、`U` 10-30 以后的新工作。
- `order`：同一天里的先后，用当前时间的毫秒数即可。

## 2. 留档规则（用户 2026-10-30）

- 留档指的是**决定和数据**，不是文件。每个决定都要记下选中的和没选中的，各自的数据和理由；每份数据都要标明属于哪个版本（R5 / Unity 改前 / Unity 改后）。
- 旧版本不删：代码里留开关，差别写进 `Apex-MovementAnalysis/R5-DIFF-ARCHIVE.md`。
- 结束的话题标"到此为止 + 日期 + 原因"，不删除。
- 拟合原则：尽量贴合 R5 native；差零点几个百分比可以不追，但要写出差在哪里、差多少。

## 3. 和 DECISIONS.md 的关系

- 共享日志是**实时的过程记录**，所有会话随时写。
- `Apex-MovementAnalysis/DECISIONS.md` 是进 git 的正式档案：你的 PR 里有决定时，照旧在同一个 PR 里加时间线和 D-xx 行，也按"选中 + 没选中 + 数据"的格式写。
