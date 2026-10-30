# HSD 扩展：铁驭技能和道具清单（用户定稿 2026-10-29）

来源：用户笔记 `HSD-TF2 准备行研究.md`（My Drive / Think Center）的"抉择"列。数据出处：解出的游戏文件 `scripts/weapons/*.txt`、`sh_passives.gnut`、`pilot_mp.set`、Boost 列表。

**背景：** 研究标准（`TODO.md` TF2 一节）第 1 条是"HSD 要做、Apex 里没有原型"。用户 2026-10-29 把下面这些列进了 HSD 以后要做的范围，所以研究它们符合标准。

**规矩：** 只借用规则、数值、手感曲线、设计思路。TF2 的模型、贴图、声音、动画是版权资产，不进 HSD。每项研究的产出写清"可照做的规则"和"只作参考的样子"。

## 0. 第二轮决定和分工（2026-10-29）

用户回答 Leader 挑的刺之后定的，总体决定见 [DESIGN-LIST.md](DESIGN-LIST.md) 第 1 节：先研究机制、存档备用；Apex 有原型的用 Apex；简单项进设计清单。下面第 1 节的表保留原样作记录，**实际去向以这张表为准**：

| 去向 | 项 |
|---|---|
| **Apex（R5）研究**：[APEX-HANDOFF.md](APEX-HANDOFF.md)，用户交给另一个 Agent | 破片手雷、电弧手雷（Arc Star）、火焰星（铝热剂）、扫描、全息分身 + 全息新星（Mirage）、地图透视、投掷物发射器（Fuse）、抛物线显示是否 Apex 自带 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) （总表）。 |
| **设计清单**（不研究）：[DESIGN-LIST.md](DESIGN-LIST.md) | 能量电池、快速回血、增幅武器、地狱塔式武器、分身分支 B |
| **TF2 任务 W1：测试目标** | 在 Northstar 本地私服放不会动 / 会动的 AI 和假人，给 W2、W3 当目标（前提任务） |
| **TF2 任务 W2：技能和投掷物** | 隐身、A 型墙、重力星、炸药包、两者的投掷弹道、投掷专家的抛物线显示（做成开关）、悬停 |
| **TF2 任务 W3：增益和特殊武器** | 相位回溯、智能手枪、蜘蛛雷、哨戒炮（两种合一） |
| 泰坦 | 之后再处理（[TITAN-LIST.md](TITAN-LIST.md)） |

Leader 只分派和汇总，不做研究。W1–W3 是下属会话，名字和状态见 TODO T-12。

每项"要研究什么"是 Leader 拆的初稿，分给下属时再细化。研究方式：**静** = 读文件 / 脚本 / DLL；**测** = TF2 本地私服实测（共用一台机器，排队）。

## 1. 要做的

### 战术技能

| 项 | TF2 文件 | 用户的想法 | 要研究什么 | 方式 |
|---|---|---|---|---|
| 隐身 Cloak | `mp_ability_cloak` | 可以加 | 持续、冷却、透明度随动作变化（开火、受伤、移动是否破隐或变明显）、能量回复 | 静 + 测 |
| 扫描（来自脉冲刀） | `mp_weapon_grenade_sonar` | 刀没用，**扫描效果**有用 | 扫描半径、脉冲次数和间隔、现形时长、能否穿墙、敌人怎么显示（轮廓 / 小地图）、对扔的人自己有没有提示 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.4、2.6。 |
| A 型墙 A-Wall | `mp_weapon_deployable_cover` | 作为道具 | 尺寸、血量、持续、放置规则（地面 / 角度）、从里面打出去的伤害加成、子弹能否从外面穿过 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.9（Rampart 加强掩体对照）。 |
| 全息分身 Holo Pilot | `mp_ability_holopilot` | 嘲讽技能 / 道具 | 分身怎么动（沿视线直跑？会跑墙？）、持续、受击消失、外观怎么区分 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.5。 |
| 全息新星（分身升级分支 A） | `holopilot_nova`（Boost） | 一次放多个 | 数量、散开方式、持续 | 静 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.5（Mirage 大招：6 个、60° 环形散开、5 s）。 |
| 分身升级分支 B | — | 用户自创：**可多次释放单个分身** | 无 TF2 原型；只记设计（次数、冷却） | — |

### 投掷物

| 项 | TF2 文件 | 用户的想法 | 要研究什么 | 方式 |
|---|---|---|---|---|
| 公共：投掷弹道 | 所有投掷物 | — | 出手速度、重力、反弹、继承玩家速度、短按 / 长按（如有） | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.1（公式）。 |
| 破片手雷 Frag | `mp_weapon_frag_grenade` | 肯定需要 | 引信时间（拉环是否开始计时）、伤害和半径曲线、自伤；击退已测（推 484，T-7） | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.1。 |
| 电弧手雷 Arc | `mp_weapon_grenade_emp` | EMP 类，可以 | 致盲 / 干扰效果的半径、时长、对护盾和机械的效果 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.2。 |
| 火焰星 Firestar | `mp_weapon_thermite_grenade` | 可以有 | 黏附规则、燃烧区大小、持续、每秒伤害 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.3（铝热剂）。 |
| 重力星 Gravity Star | `mp_weapon_grenade_gravity` | 非常有意思 | 吸力曲线（力和距离）、半径、吸多久再爆、对投射物和自己的作用（对自己无作用已测） | 静 + 测 |
| 炸药包 Satchel | `mp_weapon_satchel` | 挺重要 | 黏附、遥控引爆、同时存在几个、伤害半径；击退已测（推 484） | 静 + 测 |

### 铁驭装备（被动）

| 项 | TF2 内部名 | 用户的想法 | 要研究什么 | 方式 |
|---|---|---|---|---|
| 能量电池 Power Cell | `pas_power_cell` | 好实现 | 已知：技能回复 ×1.35。只需列出它影响哪些技能 | 静 |
| 快速回血 Fast Regen | `pas_fast_health_regen` | 好实现 | 普通回血延迟和速率、装备后的值 | 静 |
| 投掷专家：**抛物线显示** | `pas_ordnance_pack` | 抛物线非常重要 | 抛物线怎么算和画（预测步长、反弹、落点标记）、多一个投掷物 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.8（Apex 默认就有）。 |
| 抛掷专家附属（发射器） | — | 用户自创：像 Apex 暴雷（Fuse）那样把投掷物发射得更远 | 无 TF2 原型。Fuse 是 S8 加入的，本地 R5（S21）里应该有他（待确认），可以读他的被动"投掷物扔得更远"和战术"指节集束弹"的发射速度、射程，属于 Apex 原生研究 | R5 静 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.7（本地有 Fuse；被动速度 ×1.7）。 |
| 相位上机 Phase Embark | `pas_fast_embark` | 跟泰坦一起研究 | 归到泰坦清单 | — |
| 悬停 Hover | `pas_ads_hover` | 可以研究 | 时长、悬停时的速度和输入、能量和恢复、触发条件（空中按瞄准）；和被砍掉的 Boost 职业 `hover*` 键同一套 | 静 + 测 |

### Boost / 增益 / 特殊武器

| 项 | TF2 内部名 | 用户的想法 | 要研究什么 | 方式 |
|---|---|---|---|---|
| 增幅武器 | `burnmeter_amped_weapons` | 做成技能或 buff | 伤害倍率、时长、对哪些武器生效 | 静 |
| 地狱塔式武器 | — | 用户自创：对同一目标打得越久伤害越高 | 无 TF2 原型；只记设计（爬升曲线、换目标重置） | — |
| 蜘蛛雷 Ticks | `burnmeter_ticks` / `mp_weapon_frag_drone` | 道具或技能 | 追踪 AI（找目标、跳跃、速度）、引爆距离、伤害 | 静 + 测 |
| 哨戒炮（两种合一） | `burnmeter_ap_turret_weapon` / `at_turret_weapon` | HSD 伤害不分泰坦和士兵；分两种：高射速低伤、低射速高伤 | 两种炮塔的射速、伤害、转速、索敌范围和视野、持续、放置规则 | 静 + 测 |
| 地图透视 Map Hack | `burnmeter_maphack` | 做成 buff，像透视 | 显示方式（轮廓 / 小地图 / 脉冲）、持续、刷新频率 | 静 + 测 Apex 研究见 [apex/APEX-REPORT.md](apex/APEX-REPORT.md) 2.6。 |
| 智能手枪 Smart Pistol | `burnmeter_smart_pistol` | 很有意思：弹道显示、选中框 | 锁定规则（锁定时间、每目标几发、同时几个目标、视锥）、锁定框怎么画、子弹追踪、伤害 | 静 + 测 |
| 相位回溯 Phase Rewind | `burnmeter_phase_rewind` | 要加，非常有意思 | 回到几秒前、位置怎么记录（采样间隔、落在实体里的处理）、速度保不保留、相位效果时长 | 静 + 测 |

## 2. 不做（pass）

| 项 | 原因（用户） |
|---|---|
| 钩爪 | 已经按 Apex 做过 |
| 兴奋剂 | 加速、回血太容易实现 |
| 相位移动 | 已有（Wraith 虚空） |
| 脉冲刀的"刀"本身 | 没用，只留扫描效果 |
| 电烟雾 | 无聊 |
| 挂墙 | 继续 T-10 留存，现在不研究 |
| 击杀回报、低调 | 没太大用 |
| 雷达干扰、备用电池、掷骰子、加倍经验 | pass |

## 3. 下一步

泰坦清单见 [TITAN-LIST.md](TITAN-LIST.md)（等用户填"抉择"列）。两份清单都定稿后，Leader 拆成任务分给下属会话，Leader 自己不做。
