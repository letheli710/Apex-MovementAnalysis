# 进化护甲 + 护甲核心 系统记录

会话 `i1-records`，2026-11-01。静态记录。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`sl` = `sh_survival_loot.gnut`，`uc` = `pilot/sh_pilot_passive_upgrade_core.gnut`。

filter 写的位置是 `cl_survival_loot.nut`。那只是客户端显示；**逻辑在 `sl`**，filter 已更正这一处。

## 0. 概要

- **道具**：护甲 / 进化护甲 `armor_pickup_lv0/1/2/3/5_evolving`（`survival_loot.csv:258-262`）；护甲核心 `armor_core_pickup_lv1/2/3/5`（`csv:263-266`）。
- **一句话**：打出去的伤害按 1:1 累计；打够门槛（100 / 200 / 300 / 750），护甲换成下一级，盾上限 +25，溢出的点数带到下一级。打 NPC 默认 ×0.25。
- **分类**：系统（PvE 成长的现成参考）。
- **两套并存**：
  - 进化护甲：门槛表 + 换装备（本文主线）。
  - 升级核心（Upgrade Core）：同一份点数当 XP，升等级、选被动、顺带升护甲。按 playlist 开关，3.4 节。
- **可拆出的部件**：
  - 点数计算（按目标种类打折）→ 3.2.1 `EvolvingArmor_CalculateEvoPointsToGive`
  - 倒计时进度 + 升级 + 溢出递归 → 3.2.2 `EvolvingArmor_ApplyEvoPoints`
  - 升级表现（第一人称、第三人称广播、按等级的颜色）→ 3.3
  - 钩子 → [I-DEALT-DAMAGE-HOOK](../_shared/I-DEALT-DAMAGE-HOOK.md)

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 累计 | 伤害钩子 | `sl:6754`，由 `gamemodes/_gamemode_survival.nut:3630` 调 |
| 进度存储 | 服务端 `file.evoProgress[player]`，网络变量 `NV_EVOLVING_ARMOR_KILL_COUNT` | `sl:6640-6653`；**存的是还差多少**，倒数到 0 |
| 大数压缩 | 门槛超过属性上限时网络值存一半，客户端 ×2 | `sl:6616-6622`、`sl:6633-6634`、`sl:6649-6650` |
| 升级 | 直接换装备 `SURVIVAL_GivePlayerEquipment( player, 新 ref, 当前盾量 )` | `sl:6805` |
| 盾上限 | `GetPlayerSettingBaseShield + 按等级加值` | `sl:6497-6550` |
| 升级特效（第一人称） | cockpit 粒子，控制点 1 = 等级颜色 | `sl:6871-6889` |
| 升级特效（第三人称） | 5000 u 内广播 | `sl:6820-6838` |
| 音效 | 按等级 | `sl:6850-6866` |
| HUD | 进度条 RUI，`evoShieldDoubleDisplayAmount` | `gamemodes/cl_gamemode_survival.nut:1837-1862`、`cl_survival_inventory.nut:3265-3277` |

## 2. 流程

```
装备：进度 = 门槛（sh_armordata.gnut:57-58、sh_character_loadouts.nut:660）

玩家打出伤害 → 钩子 → 点数 = 血 + 盾 + 吸收
  处决 / 打自己 / 任一方倒地 → 0
  受害者是玩家 → ×1
  受害者是 NPC：
     Firing Range → ×1（不打折）
     不开 should_ai_reward_evo_pts → 0
     非战斗 AI → 0
     Prowler / 丛林蜘蛛 / 幽灵 → 各 playlist，默认 0.25
     其他 NPC → 0.25
  结果取整，至少 1
  ↓
EvolvingArmor_ApplyEvoPoints
  UpgradeCore_IncrementXP（不管穿什么护甲都加）
  没穿进化护甲 → 结束
  进度 −= 点数；算溢出
  进度到 0 且 tier ≤ 3：
     换 ref（tier 3 → lv5_evolving）；保留当前盾量
     进度 = 新等级门槛
     表现、统计
     溢出 > 0 → 递归
```

顶级：tier 5（`lv5_evolving`）`armorTier <= 3` 不成立，不再升。

**升级不回盾**（按代码）：`currentShield` 原样传进去（`sl:6794`、`sl:6805`），只有开了 `Armor_ShieldRegen` 才回（`sl:6840-6843`）。空出来的是新增上限。要实测确认，第 5 节。

没有退化。护甲丢掉或被替换走公共装备流程。

## 3. 代码

### 3.1 入口

`EvolvingArmor_PlayerDealtDamage`（`sl:6754-6760`）：算点数，0 就返回，否则应用。

### 3.2 核心

#### 3.2.1 `EvolvingArmor_CalculateEvoPointsToGive`（`sl:6660-6751`）

见第 2 节。`victim.IsNPC()` 分支里 `file.evoArmor_SquadPetsEnabled` 优先。注释说 TODO：这样写会把地图上所有 AI 都按宠物算（`sl:6676`）。

`maxint( 点数, 1 )`：只要进到这里，至少 1 点（`sl:6728`）。

#### 3.2.2 `EvolvingArmor_ApplyEvoPoints`（`sl:6762-6818`）

见第 2 节。`newTier == 4` 特判映射到 `lv5_evolving`（`sl:6800-6801`），也就是"tier 4"这一级数据上是 tier 5。

`EvolvingArmor_GetRequirementForEvolution` 用 `case 0..3`（`sl:6593-6614`），default 0。

### 3.3 客户端表现

见第 1 节。`EvolvingArmor_SetEvolutionRuiAnimTime`（`gamemodes/cl_gamemode_survival.nut:5414`）驱动 HUD 动画。

### 3.4 升级核心（Upgrade Core）

- 是否启用：`passive_upgrade_core_enabled`，代码默认 **true**（`uc:537`）；本地 `playlists_r5_patch.txt:1321` 等多处写 0。当前 playlist 的实际值要实测。
- XP 来源：同一份点数（`sl:6767`），外加扶起、击倒等固定值（`uc:539-552`）。
- 门槛：三级 `"450 1350 2000"`，双人 `"400 1100 1700"`，四级 `"450 750 800 1000"`（`uc:414-416`）。`UPGRADE_CORE_TOTAL_LEVELS = 3`（`uc:410`）。
- 升级：`UpgradeCore_LevelUp`（`uc:2329-2376`）：`curEquipData.tier < 玩家等级对应 tier` 才换核心，保留盾量，播同一个升级特效。
- 等级到 tier：level 4 → tier 5（`uc:3096-3103`）。
- 捡护甲时转换：捡到核心按当前等级发（`survival_loot.gnut:4919-4921`）。

### 3.5 依赖

[I-DEALT-DAMAGE-HOOK](../_shared/I-DEALT-DAMAGE-HOOK.md)。伤害修正链见 [C-DAMAGE-MODIFIERS](../../_shared/C-DAMAGE-MODIFIERS.md)（这里只读结果，不改伤害）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| tier 0→1 门槛 | 100 | 点 | `sl:446`；playlist `evolving_armor_damage_requirement_tier1` | | |
| tier 1→2 门槛 | 200 | 点 | `sl:447` | | |
| tier 2→3 门槛 | 300 | 点 | `sl:448` | | |
| tier 3→4(5) 门槛 | 750 | 点 | `sl:449` | | |
| 进化盾量 tier 0 / 1 / 2 / 3 / 4–5 | 0 / 50 / 75 / 100 / 125 | HP | `sl:6552-6591` | 叠在基础盾上 | |
| 普通盾量 tier 0 / 1 / 2 / 3–4 | 25 / 50 / 75 / 100 | HP | `sl:6366-6402` | 对照（tier 0 普通 25，进化 0） | |
| NPC 倍率：Prowler | 0.25 | | `sl:1285`；`ai_prowler_evo_pt_percent`，patch `:3305` | | |
| NPC 倍率：丛林蜘蛛 | 0.25 | | `sl:1294`；patch `:3304` | | |
| NPC 倍率：幽灵 | 0.25 | | `sl:1297` | | |
| NPC 倍率：其他 | 0.25 | | `sl:6715`（硬编码） | | |
| 飞鸟 | 0.25 | | `sl:1286` | | |
| 宠物 | 0.25 | | `sl:1284` | | |
| 暗影 | 0.5 | | `sl:1303` | | |
| `should_ai_reward_evo_pts` | 默认 true；patch 里 1 | | `sl:1283`、patch `:3295` | NPC 给不给点 | |
| 第三人称广播距离 | 5000 | u | `sl:6820` | | |
| 核心 XP 门槛 | 见 3.4 | | `uc:414-416` | | |

**按这些数算（打 NPC，×0.25）**：满级要 1350 点 = **5400 点实际伤害**。PvE 直接搬，升得太慢；打玩家才是 1350。HSD 要按敌人血量重新定倍率。

## 5. 未解决和要实测的

- **升级是否回盾**：R5 Firing Range 打 dummy（那里 ×1）。穿 `armor_pickup_lv1_evolving`，先掉盾，打够 100 点，读盾量和上限（`GetShieldHealth`、`GetShieldHealthMax`）。
- **进度曲线**：一次大伤害跨两级（溢出递归）。读 `NV_EVOLVING_ARMOR_KILL_COUNT`。
- **Upgrade Core 在本地 playlist 开不开**：读 `passive_upgrade_core_enabled`，决定护甲换成哪种 ref。
- **过量伤害算不算**：见 I-DEALT-DAMAGE-HOOK 第 5 节。
- `npc_dummie` 在非 Firing Range 模式下的倍率。

## 6. HSD 实现

未实现。建议：

- 订阅 `OnDamageDealt`（I-DEALT-DAMAGE-HOOK）。
- 配置表：门槛、盾量、按敌人种类的倍率。
- **有意差别**：PvE 的倍率不能照搬 0.25。R5 这个 0.25 是防止玩家靠打野怪升级；PvE 里打怪是主线。这是设计决定，定的时候进共享日志和 `R5-DIFF-ARCHIVE.md`。
- 表现可以直接学：换级时屏幕粒子 + 上限条变色。

和技能阶段没有重复部件。
