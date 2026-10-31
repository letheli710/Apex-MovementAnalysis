# Mirage 战术 Psyche Out · 系统记录

批次 D，会话 `combat-d`，2026-10-31。只做了静态研究。引用并补充 `TF2-Research/expansion/apex/APEX-REPORT.md` 2.5（W4，10-29，含一次分身速度实测）。

路径从 `research-src/s21-platform/scripts/` 开始。**HP** = `vscripts/weapons/mp_ability_holopilot.nut`（1390 行），**HP.txt** = `weapons/mp_ability_holopilot.txt`。

> 脚本是 Respawn 原版（S21 的 `mirage_rework_enabled` 分支、工单号、`StatsHook_*`）。**分身的移动 AI 全在引擎里**：`CreateTargetedPlayerDecoy`、`CreateMimicPlayerDecoy`、`CreatePlayerDecoy` 都是原生方法，脚本只设参数。所以"分身怎么跑"只能靠实测（APEX-REPORT 2.5 测过一次平地）。

## 0. 概要

- **技能**：Mirage / 战术 / Psyche Out / `mp_ability_holopilot`。大招 Life of the Party 复用本文件（见 [mirage-ultimate](../mirage-ultimate/SYSTEM.md)）。
- **一句话**：放出一个和自己一模一样的全息分身，朝准星点跑过去（60 s，45 血）；长按 0.3 s 或按角色键可以切成"跟着你的操作同步动"的操控模式；敌方玩家打中分身会被标出 3.5 s。
- **分类**：系统（主：分身 AI、仇恨、被打结算）、可视化（次）。
- **可拆出的部件**：
  - 分身实体（外观复制、血量、超时、清理）→ 3.2.1 `CreateDecoy` / `SetupDecoy_Common`；共用文档 [`_shared/D-DECOY-AI.md`](../_shared/D-DECOY-AI.md)
  - 三种移动模式（直跑 / 操控同步 / 播动画）→ 3.2.2
  - 仇恨：让 AI 把分身当成玩家打 → 3.2.3 `GetThreatPriorityForHolopilot`
  - 被打结算（标记打手、提示、天赋）→ 3.2.4 `HoloPilot_OnDecoyDamaged`
  - 数量管理（每人上限、全服上限、删最老的）→ 3.2.5
  - 模式切换（自动 ↔ 操控）→ 3.2.6 `ConvertHolosToMimics`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 分身本体 | 引擎实体 `player_decoy`，由 `player.CreateTargetedPlayerDecoy( 终点, … )` 生成，带玩家的模型和皮肤（`CharacterSkin_Apply`） | HP:592-628 |
| 直跑 AI | 原生：朝终点跑，`moveForwardDefault` 参数（脚本里传了 true，但 `CreateDecoy` 没把它传给引擎，HP:592-594）；APEX-REPORT 实测约 260 u/s，贴地，走出边缘会掉 | HP:594；APEX-REPORT 2.5 |
| 操控模式 | 原生 `CreateMimicPlayerDecoy( yaw 差 )`：分身复制玩家每帧的输入 | HP:1163 |
| 被 AI 当目标 | `EnableAttackableByAI( 优先级, 0, AI_AP_FLAG_NONE )`，优先级 = 主人玩家设置里的 `aiEnemy_priority` | HP:599、567-573 |
| 血量 / 超时 | `SetMaxHealth( 45 )`、`SetTimeout( 60 )` | HP:596-601 |
| 被打 | `AddEntityCallback_OnDamaged / OnPostDamaged / OnKilled` 三个回调 | HP:613-625 |
| 标记打手 | 打手头上 `CreateWaypoint_TrackEnt` 图标（跟着人走，只给 Mirage 一队）+ 打手 `LockOnWarningStart` + 状态效果 `mirage_detected` 3.5 s | HP:781-851 |
| 拖尾 | 胸口挂 `P_ar_holopilot_trail`，只有友方看得见 | HP:1017-1021；`_weapon_utility.nut:622` |
| 高亮 | 友方 `HIGHLIGHT_FRIENDLY_PLAYER_DECOY`；敌方用默认敌人高亮（和真人一样） | HP:970-973 |
| 名字 | 敌我都显示名字（和真人一样） | HP:936-938 |
| 闪烁 | `SetDecoyRandomPulseRateMax( 0.5 )`（每秒最多 0.5 次随机闪） | HP:939 |
| 身上道具的复制 | 主人身上挂的电池 / 旗子，复制一份挂到分身同一挂点 | HP:978-1015 |
| 循环音效 | 友方 / 敌方各一条 | HP:956-968 |
| 落点提示（客户端） | 准星射线 5000 u 落点 → 往下 2000 u 找地 → AR 粒子 `P_ar_ping_squad_CP` 1 s | HP:387-416 |
| 被 EMP | 登记为 `empDestroy`（溶解）和 `empDamage` | HP:610、947 |
| 能被扫到 | 声呐 / Neurolink 登记 | HP:945-946 |

全部服务端，客户端只有落点提示和"分身被非子弹打掉"的提示文字（HP:1366-1374）。

## 2. 流程

```
按战术键（弹夹满 150；charge 0.15 s）
   ▼
OnWeaponPrimaryAttack_holopilot（HP:219-301）
   chargeLevel = 1（战术只有 1 级）
   CreateHoloPilotDecoys( 1 ) → 战术路径（HP:491-517）：
       终点 = 准星射线 5000 u 的落点（第三人称时用 attack focus）
       分身从玩家脚下生成，朝终点跑
   数量：没有"多一个"天赋 → 删掉所有旧分身；有 → 超过上限删最老的
   TryAutoConvertToMimic：0.3 s 内还按着 → 高亮变 sp_objective_outline，松开时切成操控模式
   ▼
┌─── 自动模式（直跑） ───┐  角色键 ⇄  ┌─── 操控模式（同步主人输入） ───┐
└────────────────────────┘           └──────────────────────────────────┘
   结束：60 s 超时 / 血量归零 / 被 EMP / 主人死亡或换角色 / 回合结束 / 全服上限被挤掉
```

- **触发条件**：`PlayerCanUseDecoy`（HP:1135-1145）——不在上下文动作里（滑索时例外）。
- **切换**：角色键 `+scriptCommand5` → `ClientCallback_ToggleDecoys`（HP:360-368、1350-1363），沉默状态（`AreAbilitiesSilenced`）不能切。切换防抖 0.3 s（HP:376-380）。
- **冷却**：`ammo_instant`，弹夹 150 / 每秒 10 = 15 s（HP.txt:30-36）。
- **升级**：
  - `PAS_TAC_UPGRADE_ONE`："多一个分身"，上限 2（playlist `upgrade_mirage_tactical_decoy_max`，HP:304-310）；`upgrade_mirage_tactical_mod` 弹夹 300（推断 = 存 2 次，HP.txt:108-112）。
  - `PAS_TAC_UPGRADE_TWO`：分身被敌方玩家打中 → 战术立即充满（HP:753-761）。
- **结束时**（`OnHoloPilotDestroyed`，HP:157-187）：主人是 Mirage 时播结束音；**`state == 0` 时战术弹药直接补满**（HP:168-181）。`state` 是引擎传的分身状态，含义不明（见 5 节）。

## 3. 代码

### 3.1 入口

| 函数 | 行 | 做什么 |
|---|---|---|
| `Decoy_Init` | HP:84-119 | playlist：`mirage_decoy_duration` 60、`mirage_sonar_*`、`mirage_decoy_cloak_*`、`mirage_flashbang_decoys` |
| `OnWeaponPrimaryAttack_holopilot` | HP:219-301 | 生成、数量管理、自动切操控 |
| `CreateHoloPilotDecoys` | HP:435-538 | 三条路径：多个（大招）/ 动画（被动用）/ 单个（战术） |

### 3.2 核心逻辑

#### 3.2.1 分身实体（`CreateDecoy` HP:592-628、`SetupDecoy_Common` HP:931-1029）

```
decoy = 主人.CreateTargetedPlayerDecoy( 终点, settings="", model="", 0, 0 )
套主人皮肤；血 45；AI 可攻击（优先级 = 主人的 aiEnemy_priority）；可近战；超时 = duration
主人死亡 / 换角色 → 溶解（DecoyDestroyOnPlayerDeathOrClassChange）
三个伤害回调
Setup_Common：死亡通知、名字可见、闪烁、BossPlayer = 主人、相位中也可见、
             声呐 / Neurolink / EMP 登记、可选"离主人太远就消失"（playlist mirage_decoy_distance_limit，默认 0 = 关）、
             循环音、高亮、拖尾、复制挂件、关友军伤害、SetKillOnCollision(false)
```

#### 3.2.2 三种移动模式

| 模式 | 创建 | 怎么动 | 用在 |
|---|---|---|---|
| 直跑 | `CreateTargetedPlayerDecoy( 终点 )` | 引擎：跑向终点，到了继续同方向跑（APEX-REPORT 实测）。约 260 u/s，贴地，会掉下台子，不跳不滑 | 战术、大招 |
| 操控（mimic） | `CreateMimicPlayerDecoy( yawOffset )` | 引擎：复制主人每帧输入，方向按 `分身 yaw − 主人 yaw` 旋转 | 战术切换后 |
| 从操控切回 | `CreatePlayerDecoy( …, 0.75, true )`（HP:632） | 引擎：继承速度（参数里的 `inheritedDecoyVelocity` 没传进引擎，0.75 的含义未知） | 操控 → 自动 |
| 动画 | `CreateAnimatedPlayerDecoy( 动画名 )` | 播一段动画，血 2000，不可近战，5 s 后清理 | 被动 / 处决（本批不用） |

#### 3.2.3 仇恨（`GetThreatPriorityForHolopilot`，HP:567-573）

```
priority = 主人.GetPlayerSettingInt( "aiEnemy_priority" ) + 0     （主人无效时 10）
decoy.EnableAttackableByAI( priority, 0, AI_AP_FLAG_NONE )
```
意思：**分身和主人本人一样招 AI 恨**。AI 怎么在多个同优先级目标之间选，是引擎里的（推断：距离 / 视线 / 最近伤害）。对照：Crypto 无人机优先级写死 5（CD:1271）；`aisettings` 里泰坦 / 炮艇 50、超级幽灵 20（`aisettings/npc_titan.txt:130` 等）。玩家自己的值在玩家设置文件里，本地仓库没有这些 `.set` 文件，**数值未知**。

#### 3.2.4 被打结算（HP:666-851）

```
PreDamaged：DetermineDecoyDamageOutcome
   打手无效 / 友方 / NPC → 正常伤害
   开了"升级分身"（sonar 或 cloak 的 playlist > 0）且不是子弹（或是 Wattson 电网）→ 伤害清零
PostDamaged：HoloPilot_OnDecoyDamaged
   打手必须是【敌方玩家】，否则什么都不做          ← NPC 打分身不会被标记
   每个打手只结算一次（decoy.e.attachedEnts）
   伤害 ≤ 0 的不算（Ash 电弧陷阱插上了的例外）
   S21 规则（mirage_rework_enabled）：只有 DMG_BULLET / DMG_MELEE_ATTACK 才标记
   → PingForDecoyTriggered：
        主人听到提示音；打手头上挂跟随图标（+50 u）；打手 LockOnWarning + mirage_detected 3.5 s
        分身对敌人播"被骗了"语音；去掉分身的主人高亮
        可选：打手被声呐高亮 1.5–8 s（按分身活了多久插值，playlist 默认 0 = 关）
        可选：闪光弹（playlist mirage_flashbang_decoys，默认关）
        可选：Mirage 隐身（playlist mirage_decoy_cloak_duration，默认 0）
   天赋 TWO：战术充满
Killed：敌方用非子弹 / 非近战打死 → 主人看到"分身被摧毁"提示
```
**分身会不会一碰就消失**：脚本里没有"被打就删"的代码，45 血是真血量；APEX-REPORT 和游戏体验里"一枪就散"推断是引擎在 `player_decoy` 受伤时触发 `CodeCallback_PlayerDecoyDie`（HP:189-194）。要实测。

#### 3.2.5 数量管理（HP:243-286、1279-1342）

- 每人：没有天赋时每次放新的就删光旧的（只留 1 个）；有天赋时超过上限删最老的。数组 `weapon.w.holoEntities`。
- 全服：被动 / 大招 / 战术三张表；`在世玩家 + 现有分身 + 新分身 > max_players + 36` 时按 被动 → 大招 → 战术 的顺序删最老的（playlist `use_holopilot_limit` 可关）。

#### 3.2.6 模式切换（`ConvertHolosToMimics`，HP:1148-1234）

不是改实体，而是**删旧建新**：保留位置、角度、血量、剩余时长、出生时间；换 scriptname（`controllable_decoy` ⇄ `controlled_decoy`）。操控版高亮 `sp_objective_entity`。

### 3.3 客户端表现

- 落点 AR 标记 1 s（HP:387-416）。
- 被非子弹打掉的提示（HP:1366-1374）。
- 发射器手上 5 个灯 `FX_EMITTER_L_01..05`（HP:1378-1390）。

### 3.4 依赖的公共代码

- 引擎：`player_decoy` 实体和三个创建方法、`Decoy_Dissolve`、`CodeCallback_PlayerDecoy*`。
- `CreateWaypoint_TrackEnt`、`LockOnWarningStart`、`SonarStart`、`EnableCloak`、`FlashBang_Flash`。
- `AddEMPDestroyDevice / AddEMPDamageDevice`（CD）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 持续 | 60 | s | HP:115（`mirage_decoy_duration`） | | |
| 血量 | 45 | HP | HP:596（`mirage_decoy_health`） | | |
| 跑速 | ≈260 | u/s | APEX-REPORT 2.5 [实测] | 引擎 | |
| 落点射线 | 5000 | u | HP:29、506 | | |
| 落点标记 | 往下 2000 找地、显示 1 s | u / s | HP:410、414 | | |
| 长按切操控 | 0.3 | s | HP:320 | | |
| 切换防抖 | 0.3 | s | HP:379 | | |
| 标记打手 | 3.5 | s | HP:20、795、922 | `mirage_rework_enabled` 关时 2.5 | |
| 打手图标高度 | +50 | u | HP:791 | | |
| 声呐标记（可选） | 1.5–8（按分身存活 1–2 s 插值） | s | HP:15-16、879；playlist 默认 0 | | |
| AI 优先级 | 主人的 `aiEnemy_priority`（+0） | — | HP:567-573 | | 加 EXTRA_PRIORITY 可让分身更招恨 |
| 闪烁 | 0.5 | 次/s | HP:939 | | |
| 淡出距离 | 16000 | u | HP:14 | | |
| 每人上限 | 1；天赋 2 | 个 | HP:23、304-310 | | |
| 全服上限 | max_players + 36 | 个 | HP:1316 | | |
| 冷却 | 15（150 / 10 每秒） | s | HP.txt:30-36 | | |
| 天赋弹夹 | 300 | — | HP.txt:108-112 | | |
| charge | 0.15 | s | HP.txt:60 | | |

## 5. 未解决和要实测的

| 问题 | 为什么不确定 | 怎么测 |
|---|---|---|
| 被打一下就消失吗 | 脚本 45 血；消失推断是引擎行为 | 训练场用 P2020 打分身一枪（伤害 < 45），看是否消失；再用近战 |
| `OnHoloPilotDestroyed` 的 `state == 0` 补满战术 | `state` 是引擎枚举，代码块前后被预处理器清空（HP:167、182），看不出原意 | 放分身后等它超时 / 打掉，各记一次战术弹药 |
| 分身跑速是否随地形 / 冲刺变化 | 引擎 | APEX-REPORT 2.5 的方法：AgentLink 记分身位置；加上坡、楼梯、撞墙 |
| 撞墙行为 | 引擎 | 正对墙放，记位置 |
| 操控模式的同步细节 | 引擎 | 放后切操控，玩家做跳、蹲、滑铲、开火，看分身 |
| AI 会不会优先打分身 | 引擎，`aiEnemy_priority` 未知 | 本地 dedi 刷几个会开火的 NPC（spectre / prowler），玩家躲在掩体后放分身，记 NPC 开火目标。需要能刷 NPC 的地图 / 指令，要先确认可行 |

## 6. HSD 实现

**已有（TF2X，10-29）**：`HSD-Unity/Assets/HSD/Game/Runtime/Combat/Tacticals.cs:152-192` 类 `Decoy`；`CombatSim.Items.cs:213-239` `CastDecoys`；`CombatSim.Items.cs:296-305` 被打处理；`CombatSim.cs:249-254` `ChaserTargets`（AI 追玩家和分身）。分支选项 `DecoyBranch`（Single / BranchAMany / BranchBSeveral），PlayerPrefs `hsd.tf2.x.decoy`（`CombatLoadout.cs:47`）。

和 R5 的差别（建议写进 `R5-DIFF-ARCHIVE.md`）：

| 项 | R5 | HSD 现在 | 差多少 / 建议 |
|---|---|---|---|
| 被打即消失 | 脚本 45 血，"一枪就散"待实测 | 子弹 / 近战打中直接 hp = 0 | 等实测 |
| 谁打会被标 | **只有敌方玩家**；NPC 不标 | 任何攻击者（含 AI）都被描边 3.5 s | **PvE 需要的改动**，保留，记为有意差别 |
| 标记方式 | 头上图标 + 锁定警告 + 状态效果 | `outlinedUntil` 描边 | 表现差别，可接受 |
| AI 选目标 | 引擎：分身 = 和玩家同优先级 | 追最近的（玩家或分身） | 近似；以后做多 AI 时按 `_shared/D-DECOY-AI.md` 的优先级 + 距离 |
| 撞墙 | 引擎，未测 | 原地"站着跑" | 等实测 |
| 操控模式 | 有 | 没做（README） | 可以复用移动系统，把玩家输入复制给分身 |
| 数量 | 1（天赋 2），删旧的 | Single 1 / 分支 B 3 | 分支 B 是用户设计 |
