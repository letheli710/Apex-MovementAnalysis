# 公共部件 E：声纳高亮（Sonar Highlight）

批次 E（combat-e），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/`。主文件 `vscripts/weapons/sh_sonar.gnut`（834 行）。用到它的：Bloodhound 战术（`bloodhound-eye-of-the-allfather`）、Bloodhound 大招的跟随扫描（默认关，`bloodhound-beast-of-the-hunt`）；Seer 战术、Crypto、Vantage、勘测信标也走这里（按施放者被动换锁定框特效，`sh_sonar.gnut:294-308`）。被登记为"可被扫描"的道具：Exhibit 心脏、Death Totem 图腾等（`AddSonarDetectionForPropScript`）。

## 0. 概要

- **部件**：`SonarStart(ent, pos, team, owner)` / `SonarEnd(ent, team, owner, endHighlight=true)` / `SonarEnd_EndHighlight`，加上扫描波特效和被扫者回调。
- **一句话**：给一个实体打上"某队可见的穿墙轮廓 + 胸口锁定框 + `sonar_detected` 状态效果"，用三层引用计数保证多个扫描源叠加、各自结束时不会互相关掉。
- **分类**：可视化 ✔（轮廓、锁定框、扫描波）、系统 ✔（多源叠加的引用计数；"可被扫描道具"登记表）。
- **可拆出的部件**：
  - 三层引用计数的开 / 关 → 3.2.1
  - 可被扫描道具登记表（含代理）→ 3.2.2
  - 扫描波：世界平面波 + 地面拖尾 → 3.3
  - 被扫者视图模型高亮 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 穿墙轮廓 | 高亮上下文 `HIGHLIGHT_BLOODHOUND_SONAR`，`HighlightEnableForTeam(上下文, 扫描队)`；S3 兼容名 `bloodhound_sonar_blockscan` | `sh_sonar.gnut:265`；`sh_highlight.gnut:100`、`:160` |
| 胸口锁定框 | 粒子挂 `CHESTFOCUS`（`FOLLOW_NOROTATE`），队伍 = 扫描队，只本队和主人可见；Crypto / Seer / Vantage / Sparrow 换特效 | `sh_sonar.gnut:282-325` |
| 被扫状态 | `sonar_detected` 无限期，计数到 0 时停 | `:327-351`、`:375-383` |
| 隐身闪烁 | `SetCloakFlicker(0.5, −1)`，结束时 `(0, 0)` | `:292`、`:391-392` |
| 助攻 | 扫到即记助攻（时间 9999 当"无限"），结束时改回正常时间；playlist `disable_sonar_assist` 可按角色关（本地补丁关了 Bloodhound，`playlists_r5_patch.txt:45`） | `:231-251`、`:343-347`、`:428-432` |
| 扫描开始回调 | `AddSonarStartCallback` 注册，第一次进入时调用 | `:147-150`、`:327-333` |
| 联盟模式 | 同联盟其他队也开高亮，但限近距离 | `:267-280`、`:819-832` |

## 2. 流程

```
SonarStart(ent, pos, team, owner)：
   diamonds[team][ent]++；sonar[team][ent]++；ent.inSonarTriggerCount++
   ent.HighlightEnableForTeam(SONAR, team)
   若 diamonds[team][ent] == 1 且 ent 是玩家 / NPC / 分身：更新高亮设置；隐身闪烁；建锁定框粒子
   若 inSonarTriggerCount == 1：跑开始回调；加 sonar_detected；记助攻

SonarEnd_EndHighlight(ent, team, owner)：               // 只关轮廓
   sonar[team][ent]--；inSonarTriggerCount--
   若 inSonarTriggerCount < sonar[team][ent] 或 任一 <= 0：HighlightDisableForTeam(SONAR, team)
   若 inSonarTriggerCount < 1：停 sonar_detected；清高亮队伍位；停隐身闪烁

SonarEnd(ent, team, owner, endHighlight)：
   [endHighlight] SonarEnd_EndHighlight
   diamonds[team][ent]--
   若 diamonds[team][ent] == 0：删这个队的锁定框粒子；助攻改回正常时间
```

三层计数：`inSonarTriggerCount`（实体上，所有队合计，控制状态效果）、`teamSonarCount[team][ent]`（控制该队轮廓）、`teamSonarDiamondsCount[team][ent]`（控制该队锁定框）。Bloodhound 战术先在 1.5 s 调 `SonarEnd_EndHighlight`（只减前两层），3 s 再调 `SonarEnd(endHighlight=false)`（只减第三层），实现"轮廓先消失、框后消失"（`mp_ability_area_sonar_scan.nut:398-404`、`:343-346`）。

## 3. 代码

### 3.1 入口

`SonarShared_Init`（`sh_sonar.gnut:54-95`）：预载粒子；服务端建"可被扫描道具"托管数组；客户端挂 `sonar_detected`、`lockon_detected`、`sonar_blocked` 的回调。

### 3.2 核心逻辑

#### 3.2.1 计数开关

见第 2 节。代码：`sh_sonar.gnut:253-434`、计数工具 `:436-478`（减到 0 以下夹回 0）。

#### 3.2.2 可被扫描道具

- `AddSonarDetectionForPropScript(prop)`：开高亮、加入托管数组、同时登记 Crypto 神经连接（`:152-157`）。
- 代理：`AddSonarDetectionForPropScriptWithProxy(prop, proxy)`，扫到代理时换成真正的道具（`:165-183`）。
- 查询：`GetSonarRegisteredPropScripts(origin, radius)`（`:185-189`）。

### 3.3 客户端表现

- 扫描波 `ServerCallback_SonarPulseConeFromPosition(origin, range, dir, fov, team, speedScale, hasDamageAmp, showTrail)`（`:542-550`）→ `SonarPulseCone`（`:568-598`）：
  - `pulseSpeed = 400 + 300 × speedScale`（`SONAR_PULSE_SPACE` / `SONAR_PULSE_SPEED`，`sh_consts.gnut:800-801`）。
  - 粒子 `P_ar_sonar_plane_CP`，角度 = dir，CP1 = (range / speed, range / 80, 0)；`count` 夹在 0–8，间隔 0.25 s。
  - 地面拖尾（`showTrail`）：客户端 mover 从眼睛匀速移到 `眼睛 + dir × range`，用时 range / speed（夹在 0.05–5 s），挂 `P_sonar_ground_detect`，到了停粒子、2 s 后删（`:601-619`）。
  - 球形版 `SonarPulse`：`P_ar_sonar_CP`，CP1 = (range / speed, range / 192, 0)（`:552-566`）。
  - 有追踪视觉被动（Bloodhound）的玩家，扫描区域也登记给追踪视觉（`:548-549`）。
- 被扫者（`sonar_detected` 开，`:635-689`）：自己的手臂、武器、第一人称代理高亮成 `HIGHLIGHT_COLOR_ENEMY = <1, 0.36, 0.12>`（`sh_highlight.gnut:87`；受伤加成状态时纯红；Crypto 扫描时绿色；Mirage 特殊黑色），音效 `HUD_MP_EnemySonarTag_Activated_1P`。别人看到时走 `ClInitHighlight`。
- `sonar_blocked`：每 1.5 s 响一次 `HUD_MP_EnemySonarTag_Flashed_1P`（`:757`、`:804-816`）。

### 3.4 依赖

高亮系统 `sh_highlight.gnut`（上下文、颜色、`ManageHighlightEntity`）；状态效果框架；`SetCloakFlicker`（原生）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 |
|---|---|---|---|
| 扫描波速度 | 400 + 300 × speedScale（Bloodhound 战术 speedScale = 3 → 1300） | u/s | `sh_consts.gnut:800-801`；`mp_ability_area_sonar_scan.nut:460` |
| 平面波粒子基准尺寸 | 80 | u | `sh_sonar.gnut:483` |
| 球形波粒子基准尺寸 | 192 | u | `:482` |
| 多脉冲间隔 | 0.25 | s | `:536`、`:545` |
| 脉冲次数上限 | 8 | 次 | `:573` |
| 地面拖尾时长夹 | 0.05–5 | s | `:605` |
| 地面拖尾残留 | 2 | s | `:616` |
| 隐身闪烁 | 0.5 / −1 | — | `:292` |
| 被扫者高亮色 | <1, 0.36, 0.12> | RGB | `sh_highlight.gnut:87` |
| 被阻挡提示音间隔 | 1.5 | s | `:813` |

## 5. 未解决和要实测的

1. **SDK 改动**：`:317` `// S21: fx.SetLOSBlockScan( true ) — S3 has no entity method`（锁定框在 S21 会被视线挡，S3 上不会）；`:384-389` `HighlightSetTeamBitField` 两种参数个数。轮廓在 S3 dedi + S21 客户端上能不能正常穿墙画，要截图确认。
2. 高亮上下文的画法（颜色、粗细、穿墙方式）在 `highlight_context_drawfunc.txt` 和引擎里，没细看。

## 6. HSD 实现

**部分实现。** `CombatCore.cs:78-79` `outlinedUntil` / `markedUntil` + `CombatHud.cs:177-190` `Outlines`（屏幕框，占位）。HSD 用"到期时间取最大"代替引用计数（`Tacticals.cs:244-245` `Math.Max`），单一扫描源时等价；多个不同时长的源叠加时也等价（取最晚到期），比 R5 的计数更简单，**建议保留**，在 `R5-DIFF-ARCHIVE.md` 记一句"HSD 用到期时间取最大代替三层引用计数，效果相同"。

缺：扫描波特效（世界里的平面波 + 地面拖尾）、被扫者提示（PvE 可以做成敌人"警觉"）、可被扫描道具登记表（以后 HSD 有陷阱 / 装置时加）。
