# 公共部件 I："玩家造成了伤害"钩子（进化护甲、吸血共用）

道具批次，会话 `i1-records`，2026-11-01。只读脚本。

和 [C-DAMAGE-MODIFIERS](../../_shared/C-DAMAGE-MODIFIERS.md) 的关系：那份讲"伤害结算前改数值"的几种挂法；这份讲"结算后，按实际打出的伤害发奖励"。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。

## 0. 概要

- **部件**：`Survival_PlayerDealtDamage`（`gamemodes/_gamemode_survival.nut:3624`）。
- **一句话**：伤害结算完，把"打掉多少血、多少盾、吸收多少"传给进化护甲和吸血。两个系统都不改伤害，只拿结果。
- **分类**：系统。PvE 成长系统、吸血、连击计数都该挂这种钩子。
- **可拆出的部件**：钩子本身 → 3.1；进化点数 → [evo-armor](../evo-armor/SYSTEM.md)；吸血 → [boost-lifesteal](../boost-lifesteal/SYSTEM.md)。

## 1. 实现手段

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 触发点 | 引擎伤害回调的末尾 | `mp/_codecallbacks.gnut:702-707` |
| 来源过滤 | `attackerIsPlayer`，且不是 `DF_DOOMED_HEALTH_LOSS` | **NPC 打人不进钩子** |
| 伤害拆分 | `healthDamage`、`effectiveShieldDamage`、吸收固定传 0 | `_codecallbacks.gnut:707` |
| 处决 | 单独一处调用，`DMG_MELEE_EXECUTION` | `melee/sh_melee_synced.gnut:923` |

## 2. 流程

```
伤害结算（原生 + 回调链）
  → _codecallbacks：攻击者是玩家？非濒死掉血？
  → Survival_PlayerDealtDamage( player, victim, weapon, healthDmg, shieldDmg, absorbed, damageType )
      ├ 受害者是玩家 → AddGameSummaryDamage
      ├ EvolvingArmor_PlayerDealtDamage
      ├ Lifesteal_PlayerDealtDamage
      └ 不同队 → DeadPeriodChecker_PlayerDeadPeriodEnd
```

## 3. 代码

### 3.1 `Survival_PlayerDealtDamage`（`gamemodes/_gamemode_survival.nut:3624-3639`）

顺序固定：先给进化点数，再吸血。受害者不限玩家，NPC 也进来，由下游决定算不算。

### 3.2 下游共有的过滤

| 过滤 | 进化护甲 | 吸血 |
|---|---|---|
| 处决不算 | 是 | 是 |
| 打自己不算 | 是 | 是 |
| 任一方流血倒地不算 | 是 | 是 |
| 非战斗 NPC 不算 | 是（`IsNonCombatAI`） | 是 |
| 打队友 | 脚本没过滤（推断：队友伤害本身被挡） | 过滤 |

## 4. 参数

没有独立参数。

## 5. 未解决和要实测的

- 伤害回调链里，`healthDamage` 是不是扣完护盾、限制到剩余血量之后的值。过量伤害算不算进度决定升级速度。实测：用一枪明显超过剩余血量的伤害打 dummy，读进度差。

## 6. HSD 实现

未实现。建议：`CombatSim.Damage` 结算后发一个事件 `OnDamageDealt( attacker, victim, hpDamage, shieldDamage, source )`。进化、吸血、连击都订阅这个事件，不进伤害计算。
