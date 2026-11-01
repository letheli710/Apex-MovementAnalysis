# 增益包：吸血 系统记录

会话 `i1-records`，2026-11-01。静态记录。增益包本身只有壳（[I-STUB-ITEMS](../_shared/I-STUB-ITEMS.md)），**但吸血系统本地有完整实现**，这份主要记那个。

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/_lifesteal.nut`。

## 0. 概要

- **道具**：增益包 / `mp_ability_boost_kit_lifesteal_kit`（`survival_loot.csv:410`，被注释，被动 `PAS_LIFESTEAL_KIT`，全局搜无引用）。
- **一句话**：`weapons/_lifesteal.nut`：武器有字段 `lifesteal_heal_percent` 时，打出的伤害按比例回血，血满了回盾。
- **更正 filter**：filter 写"只有 .txt"。增益包是，但**系统不是**。filter 猜的"命中回血 → 伤害修正链的一个 hook"也要改：它不是修正链，是**结算后**的钩子。
- **分类**：系统。
- **可拆出的部件**：
  - 比例吸血 → 3.1 `Lifesteal_PlayerDealtDamage`
  - 先血后盾的分配 → 3.2 `TryHealPlayer`
  - 治疗反馈（屏幕、第三人称、数字）→ 3.3
  - 钩子 → [I-DEALT-DAMAGE-HOOK](../_shared/I-DEALT-DAMAGE-HOOK.md)

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 触发 | 伤害结算后钩子 | `vscripts/gamemodes/_gamemode_survival.nut:3632` |
| 比例 | 武器字段 `eWeaponVar.lifesteal_heal_percent` | `nut:147`；**本地用到的只有弓的 mod**，第 4 节 |
| 加血 / 加盾 | `SetHealth`、`SetShieldHealth` | `nut:69`、`nut:74`、`nut:89`、`nut:94` |
| 第三人称 | 粒子 `P_armor_3P_loop_CP`，控制点 2 = 颜色（血青色，盾按护甲等级），1 s | `nut:20`、`nut:110-130` |
| 第一人称 | 屏幕 `P_heal_loop_screen` / `P_armor_FP_charging_CP`，客户端函数 | `nut:18-19`、`nut:4` |
| 声音 | `DateNight_AOE_*` | `nut:28-30` |

`nut:17`、`nut:22` 注释：现在用的是情人节版特效，"bMat" 版注释掉。

## 2. 流程

```
玩家打出伤害 → 钩子
  处决 / 没武器 → 结束
  healSteal = 武器字段；≤ 0 → 结束
  打自己 / 非战斗 NPC / 队友 / 任一方倒地 → 结束
  heal = int( healSteal × (血 + 盾 + 吸收) )；≤ 0 → 结束
  TryHealPlayer：先补血，再补盾；有补就放特效
  有补 → 给敌人放 3P 音效
```

没有冷却（`VALENTINES_HEAL_DEBOUNCE_SEC = 10` 只声明了，`nut:15`）。

情人节模式还会分给搭档（`nut:187-207`），用不到。

## 3. 代码

### 3.1 `Lifesteal_PlayerDealtDamage`（`nut:134-209`）

见第 2 节。`nut:143-145` 注释掉的旧判断；现在靠字段值 ≤ 0 过滤。

### 3.2 `TryHealPlayer`（`nut:56-108`）

返回**没用完的治疗量**。调用方拿它判断"有没有治到"（`nut:181`）。

### 3.3 客户端

`ServerToClient_ShowLifesteal( bool 是否只有盾, int 量 )`（`nut:48`、`nut:103`），HUD 文字逗留 1.5 s（`nut:215`）。

### 3.4 依赖

[I-DEALT-DAMAGE-HOOK](../_shared/I-DEALT-DAMAGE-HOOK.md)。`hopup_golden_horse.nut:552`："Doesn't need anything, everything is built into _lifesteal"：绿色金马 hop-up 也用这个（留给武器阶段）。

## 4. 参数

| 参数 | 值 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|
| `lifesteal_heal_percent` | 0.5 | `weapons/mp_weapon_bow.txt:413`（mod `cupid`）；`mp_weapon_bow_crate.txt:449` | 回血比例 | |
| 增益包的比例 | **不知道** | `.txt` 没写，被动没实现 | | |
| 第三人称特效时长 | 1 | s | `nut:129` | |
| HUD 特效 / 逗留 | 1 / 1.5 s | `nut:214-215` | | |

## 5. 未解决和要实测的

- 比例取整、盾满溢出：Firing Range 用带 `cupid` mod 的弓打 dummy，读血量。低优先级，代码清楚。
- 增益包本身：实测帮不上。

## 6. HSD 实现

未实现。很小：订阅 `OnDamageDealt`（I-DEALT-DAMAGE-HOOK），`heal = int( percent × (hp + shield) )`，先血后盾。`percent` 放武器或 buff 上。过滤规则照抄 3.1。

现有 `CombatCore.cs` `Health` 没有盾，先只回血；有盾后再补分配。
