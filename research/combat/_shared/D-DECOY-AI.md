# 公共部件 D：分身 AI 和仇恨（让敌人把假目标当真）

批次 D 共用，会话 `combat-d`，2026-10-31。只读脚本。引用 APEX-REPORT 2.5（W4 实测分身速度）。

来源：`research-src/s21-platform/scripts/vscripts/weapons/mp_ability_holopilot.nut`（HP，Respawn 原版）。详细见 [mirage-decoy](../mirage-decoy/SYSTEM.md)、[mirage-ultimate](../mirage-ultimate/SYSTEM.md)。

## 0. 概要

- **部件**：分身实体（外观 = 主人）+ 三种移动模式 + AI 仇恨登记 + 被打结算 + 数量管理。
- **一句话**：分身是引擎实体 `player_decoy`，脚本只给它：血量、寿命、"AI 可攻击"（优先级和主人一样）、三个伤害回调；移动由引擎按"朝终点直跑 / 复制主人输入 / 播动画"三选一。
- **分类**：系统。
- **谁能用**：诱饵、替身、吸引火力的假目标、"多重影分身"、PvE 的仇恨管理（嘲讽类）。

## 1. 实现手段

| 部分 | 手段 | 来源 |
|---|---|---|
| 实体 | 引擎 `player_decoy` | HP:594、632、1163 |
| 外观 | 主人皮肤（`CharacterSkin_Apply`）、名字、默认敌人高亮——敌方看起来和真人一样 | HP:595、936-973 |
| 移动 | 引擎；脚本只选模式 | 见 3.2 |
| 仇恨 | `EnableAttackableByAI( 主人 aiEnemy_priority, 0, NONE )` | HP:567-573、599 |
| 寿命 | `SetTimeout`；主人死亡 / 换角色时溶解 | HP:601、575-590 |
| 被打 | `OnDamaged`（改伤害）、`OnPostDamaged`（标打手）、`OnKilled`（提示） | HP:613-625、666-778 |

## 2. 流程

```
创建（终点 / 模式 / 时长）→ 移动（引擎）
   被敌方玩家用子弹或近战打到（每人一次）→ 标记打手 3.5 s，主人得提示
   → 超时 / 血量归零 / EMP / 主人死 → 溶解 + 清理粒子和循环音
数量：每人上限（1 或 2，删最老的），全服上限（max_players + 36）
```

## 3. 代码

### 3.1 仇恨（HP:567-573）

```
priority = owner.GetPlayerSettingInt( "aiEnemy_priority" ) + EXTRA(0)
decoy.EnableAttackableByAI( priority, 0, AI_AP_FLAG_NONE )
```
引擎里的 AI 按优先级挑目标，同优先级时**推断**按距离 / 视线 / 最近受到的伤害。对照：Crypto 无人机写死 5（CD:1271）；`aisettings/npc_titan.txt:130` 50；`npc_super_spectre.txt:167` 20。

### 3.2 移动模式

| 模式 | 引擎方法 | 行为 |
|---|---|---|
| 直跑 | `CreateTargetedPlayerDecoy( 终点 )` | 跑到终点后继续同方向；≈260 u/s（APEX 2.5 实测）；贴地，会掉下台子，不跳 |
| 模仿 | `CreateMimicPlayerDecoy( yaw 差 )` | 每帧复制主人输入，方向旋转 yaw 差 |
| 自由 | `CreatePlayerDecoy( …, 0.75, true )` | 从模仿切回直跑时用 |
| 动画 | `CreateAnimatedPlayerDecoy( 动画 )` | 播一段动画 |

模式切换 = 删旧建新，保留位置 / 角度 / 血量 / 剩余时间（HP:1148-1234）。

### 3.3 多个分身的排布（HP:1081-1092）

第 i 个的 yaw 偏移：`i=0 → 0`；奇数 `+((i/2)+1)·SEG`；偶数 `−(i/2)·SEG`。SEG = 60° 时 6 个正好一圈。出生在主人原点 + 方向·30 u。

### 3.4 被打结算（HP:666-851）

- 只对**敌方玩家**打手生效（NPC 打不标）；每个打手只结算一次；S21 规则只认子弹和近战。
- 结算：打手头上跟随图标 + 锁定警告 + 状态效果，3.5 s。

## 4. 参数

| 参数 | 值 | 来源 |
|---|---|---|
| 血量 | 45 | HP:596 |
| 战术 / 大招寿命 | 60 / 5 s | HP:115、17 |
| 跑速 | ≈260 u/s | APEX-REPORT 2.5 |
| 标记 | 3.5 s | HP:20 |
| 多分身角度档 / 出生半径 | 60° / 30 u | HP:25、444 |
| 每人上限 | 1（天赋 2） | HP:23、304-310 |
| 全服上限 | max_players + 36 | HP:1316 |

## 5. 未解决和要实测的

- 分身被打是否一下消失（脚本 45 血）；AI 是否真的优先打分身；撞墙行为：见 mirage-decoy 第 5 节。

## 6. HSD 实现

**已有**：`Tacticals.cs:152-192`（`Decoy`）、`CombatSim.cs:249-254`（`ChaserTargets`：追玩家和 `AttractsAi` 的单位，选最近的）。

建议往通用化走：
- `CombatUnit` 加 `threatPriority`（int），AI 选目标 = 先比优先级，再比距离；分身默认 = 玩家的值。以后"嘲讽"技能就是临时调高优先级。
- 移动模式抽成接口 `IDecoyMover`：`RunStraight`（已有）、`Mimic`（复制玩家输入，用 HSD 移动系统）、`FollowOwner`（用 `D-FOLLOW-MOTION`）。
- PvE 差别：HSD 让 AI 打分身也标记打手（R5 只认玩家）——有意改动，进 `R5-DIFF-ARCHIVE.md`。
