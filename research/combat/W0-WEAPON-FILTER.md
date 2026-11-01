# W0 · 战斗研究第三阶段：武器过滤（PvE）

状态：**Leader 自己定的草稿，等用户事后看**（2026-11-01）。用户 11-01 说过各阶段自己往下推，不用等他确认，所以这份过滤先按标准定下来，共享日志里记成 `pending`。

标准和技能、道具阶段一样（D-78）：每样看三样——**效果**（伤害 / 控制）、**可视化**、**可复用系统**——有一样有价值就留。武器按**机制族**分组：同机制写一份记录，每把枪的参数在 `weapons/<族>/PARAMS.md` 里单独列全。

来源：`research-src/s21-platform/datatable/survival_loot.csv`（`main_weapon` 235 行、`attachment` 86 行、`ammo` 6 行、5 个 `hopup_golden_horse_*`）、`scripts/weapons/*.txt`、`scripts/vscripts/weapons/`。`*_whiteset / blueset / purpleset / gold / crate` 是同一把枪的配件组合，不单独算，统一进 [weapon-tiers](weapons/weapon-tiers/SYSTEM.md)。

**R5 是混合构建**（S21 客户端 + S3 dedi + SDK）。过滤时已经核对过：本地安装的武器数据和 `research-src` 相同；S3 引擎不认的 S21 字段，多数由 SDK 的 `server.dll` 补（[W-S3-FIELD-CHECK](weapons/_shared/W-S3-FIELD-CHECK.md)）。下表"本地状态"一列就是这个意思："SDK 重写"表示不是原版代码，要实测。

## 1. 保留：研究 + 实现

HSD 现在只有占位的 `TestRifle`，所以每种开火机制都有价值。

| 族（记录） | 武器 | 三样里哪一样 | 为什么留 | 本地状态 |
|---|---|---|---|---|
| [auto-ballistic](weapons/auto-ballistic/SYSTEM.md) | R-301、R-99、C.A.R.、Flatline、Spitfire、Alternator、RE-45、Volt、P2020 | 效果、系统 | 基础枪械：弹道、扩散、后坐、衰减全在这里。C.A.R. 另有双弹种切换 | 正常 |
| [burst-fire](weapons/burst-fire/SYSTEM.md) | Hemlok、Prowler、Nemesis、Hemlok Elite | 效果、系统 | 点射节奏；Nemesis 的热量加速是可借的系统 | Nemesis 热量是 SDK 重写，待实测；点射计数也靠 SDK |
| [shotgun-blast](weapons/shotgun-blast/SYSTEM.md) | EVA-8、Mastiff、Peacekeeper、Mozambique、Triple Take | 效果、可视化 | 固定图案弹丸，打 PvE 怪群价值高；横排图案可视化好 | 正常 |
| [sniper-marksman](weapons/sniper-marksman/SYSTEM.md) | Kraber、Longbow、Sentinel、G7 Scout、Wingman、Charge Rifle | 效果、系统 | 精确射击、拉栓节奏、爆头距离；Charge Rifle 的蓄力光束 | Sentinel 充能是 SDK 重写，待实测 |
| [charge-spinup](weapons/charge-spinup/SYSTEM.md) | Havoc、Devotion、Rampage、L-STAR、30-30、Bocek | 效果、可视化、系统 | 蓄力门槛、射速爬升、过热、拉弓判定：武器手感差异都在这 | Rampage 充能是 SDK 重写，待实测；30-30 蓄力倍伤推断没生效 |
| [rampart-sheila-weapon](weapons/rampart-sheila-weapon/SYSTEM.md) | Sheila 手持和炮台 | 效果、系统 | 从技能阶段移来。越打越准的扩散、转速门槛 | `spread_min_kick` SDK 只读入，待实测 |
| [vantage-sniper-weapon](weapons/vantage-sniper-weapon/SYSTEM.md) | Vantage 大招狙击枪 | 效果 | 从技能阶段移来。标记增伤见 `vantage-snipers-mark` | 见记录 |
| [ballistic-sling](weapons/ballistic-sling/SYSTEM.md) | Ballistic 第三武器槽 | 系统 | 从技能阶段移来（Tempest 仍在 `ballistic-tempest`）。备用武器槽是通用部件 | 大招变金依赖 energize（SDK 重写），要实测 |
| [hopups](weapons/hopups/SYSTEM.md) | 全部有逻辑的 hop-up（含金马） | 效果、系统 | 改武器行为的模块：PvE 成长和掉落的现成参考 | 逐条写在记录里 |
| [attachments](weapons/attachments/SYSTEM.md) | 枪管、弹匣、枪托、瞄具、激光、霰弹栓 | 系统 | 等级配件 = 字段乘数，是最简单的成长系统 | 正常 |
| [ammo](weapons/ammo/SYSTEM.md) | 轻、重、能量、霰弹、狙击、箭 | 系统 | 弹药池和备弹决定节奏 | 正常 |
| [weapon-tiers](weapons/weapon-tiers/SYSTEM.md) | 白蓝紫金套装、补给箱版 | 系统 | 同一把枪分档 = 掉落品质 | OG 版本地安装没有 |

## 2. 参考：只看系统 / 可视化

| 族（记录） | 武器 | 参考什么 | 备注 |
|---|---|---|---|
| [melee](weapons/melee/SYSTEM.md) | 拳头、传家宝（数据差异）、Titan Sword、Power Sword | 系统：近战突进、招式连段、格挡 | HSD 现在没有近战武器。传家宝只比数据。Titan Sword 的两个回调在 dedi 上没绑定（`mp_weapon_titan_sword.txt:21-22`） |
| [special-energy](weapons/special-energy/SYSTEM.md) | Buster Rifle、Ray Gun、Instagib、EPG、Charge Gauntlet、Arc Bolt、Arc Wave、Defender Sustained | 系统、可视化：慢速等离子球、爆炸弹、电弧连锁、持续光束 | 模式或活动武器。EPG 在 loot 表里注释掉了（模型缺失） |
| [npc-weapons](weapons/npc-weapons/SYSTEM.md) | `npc_weapon_*`、玩家枪上的 `npc_*` 字段 | 系统：敌人开火节奏和命中率 | PvE 敌人开火的直接参考。本地 NPC 不开火，只能静态研究 |
| RE-45 Fusion、Mozambique 愚人节版（`_light / _heavy / _sniper / _energy`）、OG 版 | 同族记录里的小节 | 数据变体 | 只记差异 |

## 3. 不要

| 东西 | 不要的原因 |
|---|---|
| 大部分 `melee_*` 传家宝和 `mp_weapon_*_primary` | 动画和外观不同，机制相同；只留一张数据差异表（melee 记录） |
| 双持（`*_akimbo_*`） | PvP 配平用途，机制是两把枪同时开火，PvE 不需要。loot 表注释"no dual-wield path on the S3 dedi"，但 SDK 有 `server/akimbo.cpp`，这条注释推断过时；weapon-tiers 记录里留了实测项 |
| 金马 hop-up 的掉落物 `hopup_golden_horse_*` 本身 | loot 表注释"no mod block defined by any weapon in either build, cannot attach"。脚本 `hopup_golden_horse.nut` 还在，进 hopups 记录当参考 |
| `hopup_paintball_elite`、`hopup_executioner` 的本地实测 | loot 表注释"no server script for hopups"，只做静态 |
| 训练场和编辑器工具（`mp_weapon_mapedit_tool`、`mp_weapon_ball_noncombat`、`mp_weapon_melee_boxing_ring`） | 模式工具，和战斗无关 |
| 道具阶段已归走的投掷物（手雷、飞刀）和技能阶段已研究的 `mp_weapon_*` 技能武器 | 不重复 |

## 4. 没选的分法（留档）

| 方案 | 结果 | 理由 |
|---|---|---|
| 按武器类型分（步枪 / SMG / LMG / 狙击） | 没选 | 官方分类是配平用的，同类机制几乎一样，差别只在数值。一份记录就够，不用 30 份 |
| 每把枪一份记录 | 没选 | 大部分枪的脚本就是 `FireWeapon_Default`，记录会几乎相同。参数改由 PARAMS.md 自动生成，每把枪都列全 |
| 按机制族分（**选中**） | 选中 | 对应 HSD 要做的部件，也符合"系统记录能改、能拆、能合"的目的 |
| "命中扫描 vs 弹道"作为一级分组 | 没选 | 字段上只有 Buster Rifle 和 `mp_weapon_shotgun_pistol_energy` 写了 `ballistic_type hitscan`，其余都走弹道子弹。放进公共部件 [W-BALLISTICS](weapons/_shared/W-BALLISTICS.md) |

## 5. 下一步

1. 静态记录（第 1、2 节）和汇总 [W1-SUMMARY](weapons/W1-SUMMARY.md)。
2. R5 实测列表见汇总。重点先测 SDK 重写的部分和最可能的真差异。
3. Unity 实现，叠在技能阶段的框架上。
