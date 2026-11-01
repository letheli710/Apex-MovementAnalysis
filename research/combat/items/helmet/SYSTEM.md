# 头盔 系统记录

会话 `i1-records`，2026-11-01。静态记录。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`gs` = `gamemodes/_gamemode_survival.nut`，`dm` = `ai/_ai_dummie.gnut`。

## 0. 概要

- **道具**：头盔 `helmet_pickup_lv1/2/3`、`lv4_abilities`、`lv4_armor_upgrade`、`lv5_armor_upgrade`、`lv5_sunglasses`（`survival_loot.csv:246-252`）。filter 写的 `lv1–5` 是简称。
- **一句话**：只削**爆头多出来的那一部分**：`伤害 = 基础 + 系数 × (爆头伤害 − 基础)`。系数白 0.8、蓝 0.5、紫 0.35、金 0.35。
- **分类**：系统（给敌人做"头部护甲"的现成公式）。
- **可拆出的部件**：
  - 爆头加成缩放公式 → 3.2
  - 无视头盔的武器例外 → 3.2
  - 头盔带被动（金、红）→ 第 4 节

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 钩子 | `AddHeadshotCallback( "player", OnPlayerTookHeadshot )` | `gs:6030`；**只对玩家** |
| 判爆头 | `IsValidHeadShot` | `gs:6112`，`sh_damage_utility.gnut:176` |
| 爆头倍数 | `GetHeadshotDamageMultiplierFromDamageInfo`：投掷物读投掷物武器设置，否则读武器 | `mp/_base_gametype.gnut:455-472` |
| 缩放 | 回调里 `DamageInfo_SetDamage` | `gs:6175-6187` |
| 全局爆头倍率 | `file.headshotDamageScale`，playlist | `gs:6189`；`dm:1056` 是 `survival_headshot_damage_scale`，默认 1 |
| 击中反馈 | `DF_HEADSHOT` | `gs:6155` 等 |
| 头盔被动 | loot 表 `passive` 列 | `csv:249-251` |
| 假人版本 | 同样写法，按 `Dummie_Helmets_Match_Shields` 选头盔 | `dm:977-1058` |

只在服务端。客户端只显示物品。

## 2. 流程

```
命中头部，引擎已把伤害 × 爆头倍数
  → OnPlayerTookHeadshot
  不是玩家 / 泰坦 → 结束
  濒死掉血 → 结束
  不是有效爆头 → 结束
  武器有 Skullpiercer Elite mod → 设为固定值，无视头盔；结束（Amped 墙另算）
  按头盔 tier 取系数
  系数 > 0 → 缩放
  × 全局爆头倍率
```

## 3. 代码

### 3.1 入口

`gs:6104`。开头注释说明前提："伤害此时已经乘过基础爆头倍数"（`gs:6103`）。

### 3.2 公式（`gs:6175-6187`）

```
crit    = 武器爆头倍数
基础    = 伤害 / crit
多出    = 伤害 − 基础
伤害    = 基础 + 系数 × 多出
```

例：一枪 20，爆头 ×2 = 40。

| 头盔 | 系数 | 结果 |
|---|---|---|
| 无 | — | 40 |
| 白 | 0.8 | 36 |
| 蓝 | 0.5 | 30 |
| 紫 / 金 | 0.35 | 27 |

飞刀（100，×3）紫头：100 + 0.35 × 200 = 170。

**tier 5 没有 case**（`gs:6152-6173` 只有 1–4）。`lv5_*` 走不进任何分支，`headshotScalar = −1`，**完全不减**。可能是这份构建少了，也可能是 lv5 系列本来如此。列为实测。

### 3.3 假人版本的默认值不同（`dm:1016-1039`）

`helmet_lv2` 默认 0.6、`lv3` 0.5、`lv4` 0.5，`case 0` 也算 lv4。注释里写着 `//0.50`、`//0.35`，说明是旧值。playlist 写了 0.8 / 0.5 / 0.35 / 0.35（`playlists_r5_patch.txt:47-50`），那个 playlist 下两边一致。

`dm:1055` 注释 `// S3: Survival_GetHeadshotDamageScale not available, use playlist var directly`：**这里是 SDK 改的**。

### 3.4 依赖

伤害修正链：这是其中一种"按受害者注册的回调"，见 [C-DAMAGE-MODIFIERS](../../_shared/C-DAMAGE-MODIFIERS.md)。

## 4. 参数

| 参数 | 值 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|
| `helmet_lv1` | 0.8 | `gs:6156`；patch `:47` | 白 | 系数越小爆头越不疼 |
| `helmet_lv2` | 0.5 | `gs:6161`；patch `:48` | 蓝 | |
| `helmet_lv3` | 0.35 | `gs:6166`；patch `:49` | 紫 | |
| `helmet_lv4` | 0.35 | `gs:6171`；patch `:50` | 金 | |
| lv5 | 无 | `gs:6152-6173` | 不减（代码如此） | |
| 全局爆头倍率 | playlist，默认 1（假人那条） | `dm:1056`、`gs:6189` | | |

被动（`csv:249-251`）：

| 头盔 | 被动 |
|---|---|
| `lv4_abilities` | `PAS_REDUCED_COOLDOWNS_TAC_ULT` |
| `lv4_armor_upgrade` | `PAS_GOLD_ARMOR_UPGRADE` |
| `lv5_armor_upgrade` | `PAS_RED_ARMOR_UPGRADE` |

## 5. 未解决和要实测的

- **lv5 是否真的不减**：戴 `helmet_pickup_lv5_armor_upgrade` 被爆头打，比基础值。低优先级，HSD 不一定有 lv5。
- 公式验证：Firing Range 假人有头盔选项（`mp/firing_range.gnut`），改 `FRSetting_DummieHelmetMatchShields`，打爆头读伤害。
- 伤害修正顺序（Amped Cover、Vantage 标记）和头盔谁先谁后：这个回调属于爆头回调，和 `AddDamageCallback` 的先后是原生决定的。

## 6. HSD 实现

未实现。建议：`CombatUnit` 加 `headCritScale`（默认 1）。结算：`dmg = base + headCritScale × (base × crit − base)`。

敌人的"戴头盔"就是这一个字段，给精英怪用。玩家戴不戴看 PvE 设计，字段相同。
