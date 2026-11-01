# 公共部件 W：一发子弹的伤害

会话 wp1，2026-11-01，静态研究。出处从 `research-src/s21-platform/scripts/` 开始。`du` = `vscripts/sh_damage_utility.gnut`，`gs` = `vscripts/gamemodes/_gamemode_survival.nut`。

后面的修正（标记增伤、递减、穿盾、溢出）不重复，见 [C-DAMAGE-MODIFIERS](../../_shared/C-DAMAGE-MODIFIERS.md)。这里只讲武器字段算出的基础伤害。

## 0. 概要

- **部件**：距离衰减、爆头、腿部、护盾比例、伤害标记。
- **一句话**：引擎按距离在近 / 远 / 极远三段取伤害，再按命中部位乘倍数，然后才进脚本的修正链。
- **分类**：系统（HSD 战斗层要有同样的字段）。
- **可拆出的部件**：三段衰减 → 3.1；爆头判定 → 3.2；部位倍数 → 3.3；头盔减爆头 → 3.4。

## 1. 实现手段

| 效果 | 手段 | 来源 |
|---|---|---|
| 距离衰减 | 引擎读 `damage_near/far/very_far_value` 和 `_distance` | `.txt`；脚本不读（`W-S3-FIELD-CHECK`） |
| 爆头判定 | `IsValidHeadShot` | `du:176-233` |
| 爆头倍数 | `damage_headshot_scale`（引擎），另有 `critical_hit_damage_scale` | `.txt` |
| 头盔 | `DF_HEADSHOT` + 把倍数拉回 | `gs:6145-6175` |
| 伤害类别 | `damage_flags`：`DF_BULLET`、`DF_SHOTGUN`、`DF_SNIPER`、`DF_KNOCK_BACK`、`DF_GIB`、`DF_EXPLOSION` | 每把枪 `.txt` |

## 2. 流程

```
命中 → 飞行距离 d
→ 三段插值出基础伤害（推断线性）
→ IsValidHeadShot？× damage_headshot_scale
→ 腿部？× damage_leg_scale（IsLegDamage，du:240 起）
→ 目标有盾？× damage_shield_scale；无盾 × damage_unshielded_scale（字段语义推断）
→ 修正链（C-DAMAGE-MODIFIERS）→ 扣血
```

## 3. 代码

### 3.1 三段衰减（推断）

```
d ≤ near_distance           → near_value
near < d ≤ far_distance     → near 到 far 线性
far < d ≤ very_far_distance → far 到 very_far 线性
d > very_far_distance       → very_far_value
```

S21 大部分枪**三段值相同**，所以实际不衰减：R-301 15 / 15 / 15（1000 / 2500 / 5000 u），R-99 12 / 12 / 12，Kraber 150 / 150 / 150。例外：

- Charge Rifle **越远越高**：近 75（2953 u）→ 远 99（7874 u）（`mp_weapon_defender.txt`）。
- 霰弹没有 `very_far`，只有两段（PARAMS）。
- 补给箱版常有真衰减：R-99 crate 15 / 14 / 13，距离 200 / 350 / 500（`mp_weapon_r97_crate.txt`）。

**所以"狙击枪的衰减"其实不靠伤害字段**，靠的是 `headshot_distance`、下坠和扩散。

### 3.2 爆头判定（`du:176-233`）

```
已带 DF_HEADSHOT → 是
victim.e.headshotImmunity → 否
攻击者是泰坦（目标不是 spectre）→ 否
hitGroup != HEAD → 否
攻击者不是玩家 → 否          // NPC 永远爆不了头
d > headshot_distance → 否
return weapon.GetAllowHeadShots()
```

**PvE 关键**：NPC 打玩家不算爆头。`headshot_distance` 是爆头的距离上限：SMG 1500 u，步枪 11828 u，狙击 29528 u。

### 3.3 部位倍数（代表值）

| 枪 | 爆头 | 腿 | `critical_hit_damage_scale` | `headshot_distance` |
|---|---|---|---|---|
| R-301 | 1.3 | 0.75 | 1.5 | 11828 |
| R-99 | 1.25 | 0.8 | 2 | 1500 |
| Longbow | 1.8 | 0.8 | — | 29528 |
| Kraber | 1.4 | 0.8 | 2 | 29528 |
| 霰弹（EVA-8、Mastiff、PK） | 1 | 1 | 1 | 1500 |

`critical_hit_damage_scale` 和 `damage_headshot_scale` 两个都在，**谁起作用不确定**：`_weapon_utility.nut:1186-1188` 把 `critical_hit_damage_scale` 传给 `TakeDamage` 的 `criticalHitScale`（命中扫描霰弹那条路）。第 5 节要测。

### 3.4 头盔（`gs:6145-6175`）

按头盔等级 1–4 取 playlist 值 `helmet_lv1..4`（默认 0.8 / 0.5 / 0.35 / 0.35），加 `DF_HEADSHOT`。**它属于生存模式代码，不是武器字段。** 道具阶段的头盔记录会用。

## 4. 参数

全部见各族 `PARAMS.md`"伤害"一段和 [W-PARAM-COMPARE](W-PARAM-COMPARE.md)。

| 字段 | 单位 | 作用 |
|---|---|---|
| `damage_{near,far,very_far}_value` | HP | 三段伤害 |
| `damage_{near,far,very_far}_distance` | u | 三段距离 |
| `damage_headshot_scale`、`damage_leg_scale` | 倍 | 部位 |
| `damage_shield_scale`、`damage_unshielded_scale` | 倍 | 对盾 / 无盾（配合 hop-up） |
| `critical_hit`、`critical_hit_damage_scale` | | 暴击 |
| `allow_headshots`、`headshot_distance` | | 爆头开关和上限 |
| `damage_flags`、`damage_type`、`impulse_force` | | 类别和击退 |
| `npc_damage_near_value` 等 | HP | NPC 用这把枪时的伤害（[npc-weapons](../npc-weapons/SYSTEM.md)） |

## 5. 未解决和要实测的

- **`critical_hit_damage_scale` 和 `damage_headshot_scale` 的关系**：同一把枪爆头打假人读数。R-301 期望 15 × 1.3 = 19.5。
- **插值是否线性**：Charge Rifle 打 4000 u，读数和线性比。
- **`damage_shield_scale`**：对有盾假人读数。
- **对 NPC 的爆头**：`npc_dummie` 有自己的回调（`vscripts/ai/_ai_dummie.gnut:1020-1036`），实测对 dummie 的倍数。

## 6. HSD 实现

**部分有。** `DamageInfo`（`CombatCore.cs`）有 `headshot`；`TestRifle` 有两段衰减和头部 ×1.5（占位）。框架分支 `claude/w2-framework-b44e35` 的 `DamageModifiers.cs` 提供修正链（Source / Attacker / Target 三段）。

建议：`Weapon` 用数据表（第 4 节字段）替换占位常量，基础伤害在进修正链之前算。
