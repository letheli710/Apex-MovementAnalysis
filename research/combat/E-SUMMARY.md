# 批次 E 汇总：可视化 / 状态 / 回溯类技能（静态）

会话 combat-e，2026-10-31。第一波：只读 `research-src/s21-platform/scripts/`，没进游戏，没改 HSD-Unity。每份记录按 `SYSTEM-RECORD-TEMPLATE.md` 0–6 节写。

## 1. 七项结论

| # | 技能 | 记录 | 一句话结论 | 分类 |
|---|---|---|---|---|
| 1 | Revenant 大招 Forged Shadows | [revenant-forged-shadows/SYSTEM.md](revenant-forged-shadows/SYSTEM.md) | 25 s；一个挂在胸口、75 血、可被打的护盾实体接住子弹 / 近战 / 爆炸，溢出伤害打到人；碎后 1 s 开始每**服务端帧** +1 回复，回满重建；击杀 +5 s（封顶 25）并立即重建护盾 | 可视化、系统 |
| 2 | Bloodhound 大招 Beast of the Hunt | [bloodhound-beast-of-the-hunt/SYSTEM.md](bloodhound-beast-of-the-hunt/SYSTEM.md) | 30 s（升级 40）一组状态效果：威胁视觉（原生画敌人）、加速 0.15、去色 + 调色（权重 = 视觉状态严重度，最后 5 s 淡出）；击杀延长**要升级 3**，按剩余时间 5–15 s；跟随玩家的扫描触发器**默认关** | 可视化、系统 |
| 3 | Bloodhound 战术 Eye of the Allfather | [bloodhound-eye-of-the-allfather/SYSTEM.md](bloodhound-eye-of-the-allfather/SYSTEM.md) | 已确认是 Bloodhound 的锥形扫描。**锥是 3D 的**（视线含俯仰、顶点在脚底），只有距离是 2D；近距放宽按距离平方插值且先截到 90°；轮廓 1.5 s / 框 3 s；扫描波 1300 u/s | 可视化、系统 |
| 4 | Seer 被动 Heart Seeker | [seer-heart-seeker/SYSTEM.md](seer-heart-seeker/SYSTEM.md) | 开镜才生效、全在客户端；50 m 内敌人按血量跳（0.4–1.65 s，双拍 0.28 s），视线内远处（5500–20000 u，随倍镜）也显示；对准判定近处按战术命中、远处按屏幕距离；**环形波形画法在 RUI 资源里，脚本只喂 10 个目标的位置 / 上次心跳 / 锁定** | 可视化 |
| 5 | Seer 大招 Exhibit | [seer-exhibit/SYSTEM.md](seer-exhibit/SYSTEM.md) | **找到脚本：`mp_ability_echo_locator`**（C0、APEX-REPORT 原说没有）。扔心脏（125 血）展开 1350 u 球区 25 s；区内敌人"没蹲着走"或开枪就被 Seer 方看到脚印 / 框 / 小地图点；**NPC 一律暴露** | 可视化、系统 |
| 6 | Revenant 旧大招 Death Totem | [revenant-death-totem/SYSTEM.md](revenant-death-totem/SYSTEM.md) | 标记 = 挂在图腾上的隐形分身（跟平台走）；暗影状态下**致死时**召回（时间到不召回）；召回：打断一切 → 安全落点 → 朝向 / 蹲姿复原、速度 0 → 0.25 s 无敌、1.5 s 减速 0.9、血 = min(50, 标记时)；掉出地图也召回 | 系统、可视化 |
| 7 | Revenant 旧战术 Silence | [revenant-silence/SYSTEM.md](revenant-silence/SYSTEM.md) | 10 s、约 150 u 的区域，每帧一次 damagedef 爆炸当"进入检测"；进区玩家沉默 15 s；**对玩家伤害被 Hack 设 0、对 NPC 不生效** | 效果（控制）、系统 |

## 2. 可拆出的公共部件

单独写成记录的（`_shared/`）：

| 部件 | 记录 | 谁用 | HSD 现状 |
|---|---|---|---|
| 状态效果框架（定时 / 无限期 / 淡出 / 延长 / 客户端开关回调） | [_shared/E-STATUS-EFFECT.md](_shared/E-STATUS-EFFECT.md) | 7 项全部 | 没有，每个道具自存时间戳。**建议最先做** |
| 屏幕调色 / 去色 / 驾驶舱粒子 | [_shared/E-SCREEN-COLOR-CORRECTION.md](_shared/E-SCREEN-COLOR-CORRECTION.md) | 1、2、3、5、6、7 | 没有 |
| 声纳高亮（三层引用计数、扫描波、可被扫描道具） | [_shared/E-SONAR-HIGHLIGHT.md](_shared/E-SONAR-HIGHLIGHT.md) | 2、3（及 5、6 的道具登记） | 部分（`outlinedUntil` 取最大，等价） |

写在单项记录里、以后可以单拆的：

| 部件 | 位置 | 用途 |
|---|---|---|
| **致死钩子**（这一下会死 → 问回调要不要救） | Death Totem 3.2.3（`_health_regen.gnut:716`） | 检查点回溯、复活道具、无敌 buff |
| **锚点式检查点 + 召回**（安全落点、复原姿态、无敌帧、减速、影子轨迹） | Death Totem 3.2.2 / 3.2.4–3.2.6 | 检查点式回溯（用户点名） |
| 跟随玩家的可受击护盾实体 + 伤害重定向 + 溢出 | Forged Shadows 3.2.1–3.2.3 | 护盾类 buff、Boss 护盾 |
| 黏附物穿墙剥落 | Forged Shadows 3.2.4 | 任何会移动的可黏物体 |
| 跟随触发器 + 每目标线程 | Hunt Mode 3.2.2 | 光环类效果 |
| 按剩余时间缩放的击杀延长 | Hunt Mode 3.2.3 | 连杀奖励 |
| 一次性 3D 锥查询 | Eye of the Allfather 3.2.1 | 侦测、锥形技能 |
| 区域 + 行为条件侦测（移动 / 开火） | Exhibit 3.2.2–3.2.3 | PvE 侦测区域 |
| 按血量变速的心跳节拍 + 环形 HUD 数据 | Heart Seeker 3.2.2、3.3 | 感应 HUD |
| 每帧小爆炸当"进入区域"检测 | Silence 3.2.1 | 便宜的区域效果 |

## 3. 最重要的实测项（第二波）

1. **S3 dedi 有没有暗影状态**（`EnterShadowForm` / `EnterShadowFormFortified` / `IsShadowForm`）。SDK 在 `vscripts/mp/_staging_area.gnut:1843` 写了 `// S3: shadow form not available`。没有的话 Death Totem 整套、Forged Shadows 可能直接报错。测法见 Death Totem 第 5 节第 1 项。
2. **Forged Shadows 护盾回复速度**（每服务端帧 +1，回满时间取决于 tick 率）。见其第 5 节第 1 项。
3. **Bloodhound 扫描 3D 锥的上下覆盖和近距角度**（影响 HSD 现有 `Scan`）。见其第 5 节第 1–2 项。
4. **Heart Seeker 环形 HUD 的画法**（RUI 资源）：做 HSD 感应 HUD 前必须截图或解包。
5. **Exhibit 暴露规则**（站 / 走 / 蹲 / 开镜 / 开枪）和服务端脚底 vs 客户端眼睛的判定点差。
6. Silence 对玩家到底有没有伤害；Hunt Mode 击倒时战术充满写给了谁（疑似写给被击倒者）。

## 4. 遇到的问题

- **C0 和 APEX-REPORT 的两处更正**：① Seer 大招有脚本（`mp_ability_echo_locator.nut`，证据：`sh_ping.gnut:4792` 注释 "Seer Exhibit"、`status_effect_types.txt:161`、`sh_stats_characters.gnut:213`）；Seer 战术也有（`mp_ability_sonic_blast.nut`）。② APEX-REPORT 2.4 的 Bloodhound 扫描"只算水平"只对距离成立，角度是 3D 的；对照表"大招击倒 +5 s"在 S21 要升级、而且是 5–15 s。C0 本批没改（按任务要求），由 Leader 更新。
- **HSD 现有 `Scan` 和 R5 的差别**（3D 锥、近距插值），写在 Eye of the Allfather 第 6 节，没改代码。
- **SDK 改过的痕迹**：`sh_sonar.gnut:317`、`:384`；`mp_ability_area_sonar_scan.nut:155`、`:570`；`mp_ability_heartbeat_sensor.nut:157`；`mp_ability_echo_locator.nut:542`、`:836`；`_staging_area.gnut:1843`。
- **疑似原代码笔误**（按脚本原样记录，第二波实测确认）：Forged Shadows `assistTime` 读了 `extension_time` 的 playlist 键（`shadow_form.nut:154`）；Hunt Mode 倒地回调给被击倒者充战术（`hunt_mode.nut:205`）；Exhibit "首次锁定保留更久"永远不生效（`echo_locator.nut:1719`、`:1728`）；Death Totem 图腾血量常量 150 没用、实际 100（`death_totem.nut:49`、`:291`）；Silence 外观半径 175 和判定半径 150 不一致（`mp_ability_silence.nut:15`、`damagedefs.txt:419`）。
- 原生部分看不到：威胁视觉画法、去色、`EnterShadowForm*`、`GetPlayersInViewInfoArray`、所有 RUI 和 LUT 资源。

## 5. 共享日志

已写入（会话短名 `combat-e`）：`2026-10-31-combat-e-seer-exhibit-script`、`-shadow-form-static`、`-scan-cone-3d`、`-hunt-mode-static`、`-shadow-form-s3`、`-death-totem-static`、`-summary`。
