# 增益包：召唤 Nessie 系统记录

会话 `i1-records`，2026-11-01。静态记录。增益包本身只有壳（[I-STUB-ITEMS](../_shared/I-STUB-ITEMS.md)），**但本地有两套真实的"召唤伙伴"代码**。这份记入口和关键值，详细读留给武器阶段（金马 hop-up）。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`gh` = `weapons/hopup_golden_horse.nut`，`ne` = `ai/_ai_nessie.gnut`，`pet` = `sh_player_pet.nut`。

## 0. 概要

- **道具**：增益包 / `mp_ability_boost_kit_nessie_summon`（`survival_loot.csv:411`，被注释，被动 `PAS_NESSIE_SUMMON`，全局搜无引用）。
- **一句话**：增益包没代码。同样的东西在红色金马 hop-up 里：`CreateSummonNPC` 刷一只 `npc_nessie`，绑定主人，走"宠物跟随 + 自动打敌人"。
- **更正 filter**：filter 写"只有 .txt，和跟随运动对照"。系统实际在 `gh` 和 `pet`。**本地 NPC 能不能真的打人存疑**：W2 实测 `npc_prowler` 不开火不近战（`CanSee` 恒 0）。
- **分类**：系统（伙伴 AI）。
- **可拆出的部件**：
  - 刷 NPC + 绑定主人 → 3.1 `Nessie_SpawnNPC`
  - 配置成宠物（常警觉、敌人距离、改模型、称号、高亮）→ 3.2 `CreateSummonNPC`
  - 跟随 / 战斗切换 → 3.3 `PetStartFollowingOwner` + `OnEnemyChanged`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 实体 | `CreateNPCFromAISettings( "npc_nessie", team, ... )` | `ne:515` |
| 主人 | `SetBossPlayer( owner )`，`noOwnerFriendlyFire = true` | `ne:517`、`ne:522` |
| 跟随 | 引擎 AI 的跟随目标 + 容差（**不是脚本算位置**） | `pet:476`，和 [D-FOLLOW-MOTION](../../_shared/D-FOLLOW-MOTION.md) 的脚本追踪不同 |
| 切状态 | `SetEnemyChangeCallback( OnEnemyChanged )`：没敌人 → 回去跟随 | `gh:1573`、`gh:1770-1779` |
| 发现敌人 | `kv.alwaysalert = true`、`SetMaxEnemyDistOverride` | `gh:1569`、`gh:1577-1579` |
| 可交互 | `CreateUsableNessie`（playlist `golden_horse_red_allow_use`） | `gh:1581` |
| 高亮 | `Highlight_SetEnemyHighlight( summon, "enemy_ai" )` | `gh:1587` |
| 出场 | 粒子 `P_Rmat_warp_spawn`，声音 `materia_red_nessie_spawn_3P` | `gh:117`、`gh:131` |
| 地图卸载 | `HACK_SummonKill_Thread` | `gh:1538-1554` |

## 2. 流程

增益包：**写不出，不编。**

金马（只记大框）：

```
触发 → 等 GOLDEN_HORSE_RED_SUMMON_SPAWN_TIME_SEC（1 s）
  → CreateSummonNPC → 跟随主人
有敌人 → 引擎 AI 战斗
敌人没了 → OnEnemyChanged → PetStartFollowingOwner
上限每人 2 只；冷却 15 s
```

## 3. 代码

### 3.1 `Nessie_SpawnNPC`（`ne:513-530`）

队伍、主人、位置；`SF_NPC_NO_PLAYER_PUSHAWAY`；`SetChanceToHitEnabled( true )`；`SetupDoorCollision`。

### 3.2 `CreateSummonNPC`（`gh:1556-1590`）

见第 1 节。

### 3.3 `PetStartFollowingOwner`（`pet:476-…`，`gh:1799` 另有一份）

读容差 playlist（`player_pet_follow_move_tolerence`、`player_pet_follow_combat_tolerence`、`player_pet_follow_goal_tolerence`），可选清敌人和记忆（`squad_pet_force_clear_enemy`）。**两份同名函数没有比较。** 第 5 节。

### 3.4 依赖

伙伴运动对照 [D-FOLLOW-MOTION](../../_shared/D-FOLLOW-MOTION.md)；NPC 仇恨 [D-DECOY-AI](../../_shared/D-DECOY-AI.md)；刷兵 [D-DROP-POD](../../_shared/D-DROP-POD.md)。

## 4. 参数

| 参数 | 值 | 来源 | 说明 |
|---|---|---|---|
| 增益包专属值 | **没有** | | |
| `GOLDEN_HORSE_RED_MAX_SUMMON_PER_PLAYER` | 2 | `gh:90` | 金马 |
| `GOLDEN_HORSE_RED_SUMMON_SPAWN_TIME_SEC` | 1 s | `gh:91` | 金马 |
| `GOLDEN_HORSE_RED_SUMMON_COOLDOWN_TIME_SEC` | 15 s | `gh:92` | 金马 |
| `GOLDEN_HORSE_RED_ENEMY_DIST` | 150 m | `gh:101` | 金马 |
| 跟随目标容差 | playlist | `pet:476` 之后 | |
| 跟随非战斗容差 | 512 u（默认） | `sh_player_pet.nut` `player_pet_follow_goal_tolerence` | |

Nessie 的血量和伤害在 AI 设置文件（`npc_nessie`），本次没读。

## 5. 未解决和要实测的

- **`npc_nessie` 在 dedi 上能不能刷、会不会打人**：W2 记录 `npc_dummie`、`npc_prowler` 能刷会追但不打，spectre 把 dedi 卡死。脚本刷一只 `Nessie_SpawnNPC( 玩家队, 玩家, 位置 )`，放一个敌队 dummy。先小心，可能和 spectre 一样卡死。优先级中，和武器阶段的金马一起。
- `gh:1799` 和 `pet:476` 哪份在跑，有没有差别。
- `npc_nessie` 的 AI 设置。

## 6. HSD 实现

未实现。建议：伙伴用 [D-FOLLOW-MOTION](../../_shared/D-FOLLOW-MOTION.md) 的脚本追踪（飞行）或 Unity NavMesh（地面）。**"有敌人打敌人，没敌人回主人身边"这个切换**用 `OnEnemyChanged` 的写法：一个回调，一个跟随入口。
