# 公共部件 I：燃烧层和地面火点（铝热剂、道具类火焰）

道具批次，会话 `i1-records`，2026-11-01。只读脚本。铝热剂直接用；Fuse 大招对道具 / 陷阱也调 `TryApplyingBurnDamage`（见 [fuse-motherlode](../../fuse-motherlode/SYSTEM.md) 第 1 节），对人走自己的 `BurnDamageThink`。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`wu` = `weapons/_weapon_utility.nut`。

## 0. 概要

- **部件**：`FireSegment_DamageThink`（火点触发器）+ `BurnDamageStack`（实体身上的燃烧层）+ `EntityBurnDamageThread`（结算）。
- **一句话**：站在火点里，隔一段时间往身上加一层；每层独立计时、独立跳伤害；离开火后层继续烧完。
- **分类**：系统。
- **可拆出的部件**：
  - 圆柱火点（触发器 + LOS + 敌我过滤）→ 3.1
  - 层的增加规则（防抖 + 上限）→ 3.2
  - 层的伤害节拍（首跳立即、余数补齐）→ 3.3
  - 整组火点共享的"每帧只伤一次"inflictor → 3.4

## 1. 实现手段

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 火点判定 | `CreateTriggerCylinderMultiple_Deprecated`，半径 + 高度，下方 0 | `wu:4202` |
| 每帧查人 | `GetAllEntitiesInTrigger_Deprecated` + `WaitFrame` | `wu:4230-4253` |
| 穿墙检查 | `PositionHasLOSToObject`（中心 → 脚 → 眼三条线，只算 brush），开关 `thermite_enable_LOS_check` 默认开 | `wu:4246`、`wu:4321-4346`、`wu:619` |
| 敌我 | 队友跳过（`noFriendlyFireProtection` 例外），**主人自己不跳过** | `wu:4243` |
| 燃烧资格 | `IsAlive`、不在相位、`ent.e.canBurn` | `wu:4291-4300` |
| 伤害 | `ent.TakeDamage( n, owner, inflictor, { damageSourceId, damageType = DMG_BURN } )` | `wu:4528` |
| 是否在烧 | `SetEntityIsBurning` | `wu:4446` |

`canBurn` 默认 false（`_entitystructs.gnut:433`）。玩家在 `mp/_base_gametype_mp.gnut:394` 打开，普通 NPC 在 `ai/_ai_spawn_content.gnut:278` 打开，放置物各自打开。

全部在服务端。

## 2. 流程

```
FireSegment_DamageThink（每个火点一个线程）
 每帧：对触发器里每个实体
   队友 → 跳过；没有 LOS → 跳过
   TryApplyingBurnDamage
     分身 → 直接加层（不查上限和防抖，wu:4310-4314）
     其他 → 已满 4 层，或最新一层不到 0.7 s → 不加
     AddEntityBurnDamageStack（第一层时开 EntityBurnDamageThread）
线程结束条件：特效消失、触发器消失、inflictor 消失（wu:4213-4215）

EntityBurnDamageThread（每个实体一个线程）
 每帧遍历所有层：
   到时间 → 记入移除；补上还没打完的余数
   没到时间且距上一跳 ≥ tickInterval → 打 damagePerTick
   本帧已经打出一跳 → break（inflictor 每帧只算一次，wu:4506-4508）
 没有层了 → 结束
```

## 3. 代码

### 3.1 `FireSegment_DamageThink`（`wu:4193-4254`）

火点父实体跟随时触发器也跟随（`wu:4203-4208`）。主线逻辑见第 2 节。

### 3.2 加层：`wu:4361-4402`

```
满 burn_stacks_max → 不加
任何一层 age < burn_stack_debounce → 不加
stack.endTime = now + burn_time
stack.tickInterval = burn_tick_rate / burn_time     // 注意是"比率"，不是间隔
numIntervals = int( burn_time / tickInterval )
stack.damagePerTick = burn_damage / numIntervals    // 整数除法
```

### 3.3 结算：`wu:4441-4518`

`lastDamageTime` 默认 **−1**（`sh_consts.gnut:2838`），所以第一跳在加层当帧就打（`wu:4485`）。层到时间时，`burn_damage − damageDealt` 大于 0 才补（`wu:4474-4475`）。

铝热剂数值代入：`tickInterval = 1.2 / 2.8 = 0.4286`，`numIntervals = 6`，`damagePerTick = 25 / 6 = 4`。

| 服务端帧率（推断） | 实际间隔 | 跳数 | 每层总伤害 |
|---|---|---|---|
| 10 Hz | 0.5 s | 6 跳 = 24，到时补 1 | **25** |
| 20 Hz | 0.45 s | 7 跳（0、0.45 … 2.7） | **28** |
| 30 Hz | 0.433 s | 7 跳（0 … 2.6） | **28** |

**更正 APEX-REPORT 2.3**："每层 24"不对，是静态算的，没算首跳和余数。按代码是 25–28，取决于帧率。站满 4 层仍约 37 点/秒（4 × 4 / 0.4286）。要实测，见第 5 节。

`break` 的副作用：同一帧有两层都到点，后一层拖到下一帧。多层时平均节拍略慢（推断，影响很小）。

### 3.4 inflictor：`CreateOncePerTickDamageInflictorHelper( lifetime )`（`wu:4069-4077`）

一个 `info_target`，`onlyDamageEntitiesOncePerTick = true`，`lifetime` 后销毁。一颗铝热剂的所有火点共用一个：站在多个火点交界处，同帧也只算一次。

## 4. 参数

各字段的值在使用者的 `.txt`。结构体见 `BurnDamageSettings`。

| 参数 | 铝热剂的值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| `burn_damage` | 25 | HP | `mp_weapon_thermite_grenade.txt:76` | 每层名义总伤害 | 整除后才是每跳 |
| `burn_time` | 2.8 | s | `.txt:77` | 每层时长 | 改大：离开火后烧更久 |
| `burn_stacks_max` | 4 | 层 | `.txt:78` | 同时层数上限 | DPS 上限 |
| `burn_stack_debounce` | 0.7 | s | `.txt:79` | 加层最短间隔 | 改小：更快到满层 |
| `burn_tick_rate` | 1.2 | 比率 | `.txt:80` | `tickInterval = rate / time` | 名字误导：改大是**间隔变大** |
| `thermite_enable_LOS_check` | true | 开关 | `wu:619` | 穿墙检查 | playlist |

## 5. 未解决和要实测的

- **每层到底多少**：25 还是 28。R5：把一个 dummy 放进火点 1 帧就移走，读总伤害，同时记录 `sv` 帧率。
- **inflictor 消失以后，层还打不打**：`wu:4528` 把已销毁的 inflictor 传给 `TakeDamage`。脚本里看不出来是报错、照打还是不打。实测：最后一刻走进火里，看第 8 s 之后还掉不掉血。
- `TakeDamage` 带 `DMG_BURN` 对护盾 / 血量的分配是原生。

## 6. HSD 实现

已有：`Ordnance.cs` 的 `BurnTracker`（`LayerTime 2.8`、`TickEvery 0.43`、`TickDamage 4`、`NewLayerEvery 0.7`、`MaxLayers 4`）。

| 差别 | R5（脚本） | Unity 现在 | 差多少 |
|---|---|---|---|
| 首跳 | 加层当帧 | `now + 0.43` | 晚 0.43 s |
| 每层总伤害 | 25–28 | 24 | 少 1–4（≤ 14%） |
| 结算单位 | 每层独立计时 | 所有层共用一个节拍，跳伤 × 层数 | DPS 相同，时序不同 |
| 余数补齐 | 有 | 没有 | |
| 同帧只伤一次 | 有 | 没有 | 多层交界时才有差别 |

实测定下来后改，差别进 `R5-DIFF-ARCHIVE.md`。这份记录没改代码。
