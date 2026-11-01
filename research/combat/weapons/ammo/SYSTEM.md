# 武器弹药：系统记录

会话 wp1，2026-11-01，静态研究（只读脚本和数据，没进游戏）。

出处从 `research-src/s21-platform/` 开始。缩写：`loot` = `datatable/survival_loot.csv`，`groups` = `datatable/survival_loot_groups_new.csv`，`all` = `scripts/vscripts/sh_survival_loot_all.gnut`，`sv` = `scripts/vscripts/survival_loot.gnut`，`wu` = `scripts/vscripts/weapons/_weapon_utility.nut`，`pool` = `scripts/weapons/constant_types/ammo_pool_types.txt`，`suck` = `scripts/weapons/ammo_suck_behaviors.txt`。`sdk` = `research-src/s21-r5sdk/src/game/`（SDK 的 `server.dll` 源码）。`<武器>.txt` = `scripts/weapons/mp_weapon_<武器>.txt`。

相关记录：[W-FIRE-RELOAD](../_shared/W-FIRE-RELOAD.md)（开火和换弹）、[W-S3-FIELD-CHECK](../_shared/W-S3-FIELD-CHECK.md)、[attachments](../attachments/SYSTEM.md)（弹匣）、[weapon-tiers](../weapon-tiers/SYSTEM.md)（空投枪）。

## 0. 概要

- **对象**：弹药种类、地上的弹药、背包堆叠、武器备弹字段、能量枪备弹回充。
- **一句话**：普通枪的备弹 = 玩家身上的公共弹药池（按种类）。空投枪和能量枪的备弹 = 枪自己的 `stockpile`。本地补丁把能量枪改成了"自己回充"，地上的能量弹被禁用。
- **分类**：
  - 效果：备弹回充（HSD 单人可以省掉捡弹）。
  - 可视化：无。
  - 可复用系统：公共池 + 枪内备弹两套模型；每次掉落数量 / 堆叠分开配置。
- **可拆出的部件**：
  - 公共弹药池 → 3.2.1
  - 枪内备弹（`uses_ammo_pool 0`）→ 3.2.2
  - 能量回充（本地重写）→ 3.2.3
  - 弹药掉落 → 3.2.4

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 弹药种类 | 引擎枚举 `eAmmoPoolType`，由 `pool` 生成 | 顺序就是整数值：bullet 0、highcal 1、special 2、shotgun 3、sniper 4、arrows 5（`pool`、`all:591-607`） |
| 公共池 | 引擎 `player.AmmoPool_GetCount( 类型 )` | 按种类存在玩家身上（`wu:6455`） |
| 枪内备弹 | `AMMOSOURCE_STOCKPILE` | `uses_ammo_pool 0` 的枪（`wu:6451`） |
| 弹药 loot | `loot` 行 `type=ammo` | `all:836-839` |
| 能量回充 | **脚本线程** `EnergyAmmoRegen_Think`（`wu:4822`） | 本地重写，3.2.3 |
| 大招式回充 | `regen_ammo_refill_rate` 等字段 | 大招和技能用（见 Sheila 记录），**主武器不用**（`rspn101.txt`、`energy_ar.txt`、`lstar.txt` 都没有） |

**混合构建问题（已明确）**：`all:572-575` 注释：武器 `.txt` 写字符串，S21 客户端解析成整数，S3 dedi 是字符串。读错类型会让 `SV_CL_Init` 中止。所以 `SURVIVAL_Loot_WeaponAmmoPool`（`all:567`）**同时接受字符串和整数**。这是本地补丁。

## 2. 流程

```
地上捡弹 → 背包（inventorySlotCount 决定一格多少）→ 公共池
开火：每发 ammo_per_shot 扣弹匣
换弹：
  uses_ammo_pool 1 → 从公共池拿
  uses_ammo_pool 0 → 从 stockpile 拿
丢枪（sv:3524-3527）：弹匣里的弹退回背包（放不下就落地）
```

没弹的语音：`gamemodes/_gamemode_survival.nut:7636-7660`，按种类。

## 3. 代码

### 3.1 入口

- `all:836-839`：弹药行读取，两个 playlist 倍率。
- `all:767`：枪行 `ammoType = SURVIVAL_Loot_WeaponAmmoPool`。
- `all:769-796`：`secondary_ammo_pool_type`。

### 3.2 核心逻辑

#### 3.2.1 公共池

只有 `uses_ammo_pool 1` 的枪走它。来源：`.txt` 字段（统计存活的枪行，`loot` + `.txt`）：

| 池 | 枪 |
|---|---|
| bullet（8）| G7、Alternator、R-99、Spitfire、R-301、P2020、RE-45、Mozambique light 活动 |
| highcal（8）| Flatline、Hemlok、Hemlok Elite、Prowler、30-30、Rampage、C.A.R.、Mozambique heavy 活动 |
| shotgun（4）| Mastiff、EVA、PK、Mozambique |
| sniper（5）| Longbow、Charge Rifle、Wingman、Sentinel、Mozambique sniper 活动 |
| special（1）| Mozambique energy 活动 |

C.A.R. 文件只有一个 `ammo_pool_type`，切换弹种走 `alt_ammo` mod（`car.txt:410`、`car_crate.txt:436`），见 [W-MOD-SYSTEM](../_shared/W-MOD-SYSTEM.md)。S3 引擎不允许 mod 改这个字段，SDK 为每个实体克隆一份 WeaponInfo 来实现（`sdk/server/weapon_ammo_pool_mod.h`）。

**全部能量枪都不用公共池**（下一节）。所以 `loot:190` `special` 禁用不影响它们。

#### 3.2.2 枪内备弹

`uses_ammo_pool 0`：全部 `_crate` 枪、能量枪（Havoc、Devotion、L-STAR、Triple Take、Volt、Nemesis、RE-45 Fusion）、Kraber、Bocek、Instagib、飞刀。

- 地上时：`ent.SetClipCount( ammo_default_total )`（`sv:3118-3125`），还存 `specialAmmoCounts`。
- 捡起时：`stockpile` 拉满（`sv:3805-3809`）。
- 能量枪特殊：`stock = pickup.clip - weapon.clip`，夹在 0..max（`sv:3817-3821`）。
- 空投枪 Boosted Loader 退弹回 `stockpile`（`wu:6451`）。

**字段不同的例子**：

| 枪 | `ammo_pool_type` | `uses_ammo_pool` | 弹匣 | `ammo_stockpile_max` | `ammo_default_total` | 来源 |
|---|---|---|---|---|---|---|
| R-301 | bullet | 1 | 21 | 44 | 0 | `rspn101.txt:8`、`50-56` |
| R-301 空投 | bullet | 0 | 21 | 248 | 217 | `rspn101_crate.txt:4-8`、`20` |
| Havoc | special | 0 | 18 | 54 | 72 | `energy_ar.txt:8`、`66-73` |
| L-STAR | special | 0 | 0 | 88 | 88 | `lstar.txt:16`、`277-282` |
| Bocek | 无 | 0 | 0 | 40 | 40 | `bow.txt:94-97` |
| Bocek 空投 | arrows | 0 | 0 | 40 | 40 | `bow_crate.txt:121-125` |
| Kraber | 无 | 0 | 4 | 8 | 12 | `sniper.txt:60-66` |
| Wingman | sniper | 1 | 5 | 20 | 0 | `wingman.txt:7`、`42-51` |
| EVA | shotgun | 1 | 8 | 18 | 0 | `shotgun.txt:8`、`62-67` |

`.txt` 注释（`pool`）："不写 ammo_pool_type 的枪用第一种"（bullet）。但 `all:569` 对 `uses_ammo_pool` 假的枪直接返回空，不走这条。

`ammo_stockpile_max` 对 `uses_ammo_pool 1` 的枪的含义：公共池上限来自背包格，**不来自**这个字段。推断它只用于 HUD 或 mod 累加（`W-S3-FIELD-CHECK` 没列入差异，两边都认）。

`ammo_no_remove_from_stockpile`：两边都认，脚本里没有引用。`mp_weapon_*` 全部 193 个文件里 25 个为 1（比如 `g2`、`hemlok`、`r97`、`pdw`、`3030`、`energy_shotgun`、`instagib`、`mobile_hmg`）。这些枪多数 `uses_ammo_pool 1`，所以推断只影响"不扣 stockpile"，**具体语义要实测**。

#### 3.2.3 能量备弹回充（`wu:4742-4885`）

**本地重写，不是原版**（推断：`energy_ar`、`esaw` 等改成 `uses_ammo_pool 0` 才需要它；OG 版本是 `uses_ammo_pool 1`，见 [weapon-tiers](../weapon-tiers/SYSTEM.md) 3.3）。

```
条件（wu:4754）：弹药池 special 且 uses_ammo_pool 0 且 ammo_stockpile_max > 0
启动：OnWeaponActivate 调 EnergyAmmoRegen_Start（energy_ar.nut:77、esaw.nut:21、
      lstar.nut:189、doubletake.nut:116、volt_smg.nut:15、nemesis.nut:91、basic_bolt:34）
线程（wu:4822，每帧，服务端）：
  stockpile 下降 或 按着开火 → readyTime = now + 0.1，清进度
  满了 或 没到 readyTime → 清进度
  carry += 回充速率 × dt；取整写回 stockpile
```

回充速率（`wu:4786`）：

```
弹匣 <= 0（L-STAR）：
  空投 1.27；能量弹匣 L1 1.34 / L2 1.44 / L3 1.56 / L4 1.56；无 1.22
否则：
  rate = 弹匣 / 18（空投 / 22）
  能量弹匣：L1 × 1.5，L2 × 2.0，L3 × 2.5，L4 × 2.5
```

例：Havoc 基础弹匣 18 → 1 发/s；L3（弹匣 29）→ 29 / 18 × 2.5 ≈ 4 发/s。线程在枪上，只要枪活着（包括收起）都在跑，激活时启动一次。

相关字段 `ammo_regen_takes_from_stockpile`：S3 没有，SDK 别名到占位槽（`sdk/shared/weapon_script_vars.cpp:3205`），主武器没用到（只有技能）。SDK 另有 `sdk/server/weapon_regen.h`（`regen_ammo_forced_delay`，弹匣回充）和 `sdk/server/weapon_stockpile_bonus.h`（给单把枪加备弹上限，注释举 Sparrow 的 Bocek +10）。

#### 3.2.4 弹药 loot 和掉落

| ref | `countPerDrop` | `inventorySlotCount` | tier | 状态 | 来源 |
|---|---|---|---|---|---|
| `bullet` | 20 | 60 | 1 | 存活 | `loot:189` |
| `special` | 18 | 54 | 1 | **禁用** | `loot:190` |
| `shotgun` | 10 | 20 | 1 | 存活 | `loot:191` |
| `highcal` | 20 | 60 | 1 | 存活 | `loot:192` |
| `sniper` | 14 | 28 | 1 | 存活 | `loot:193` |
| `arrows` | 16 | 32 | 1 | **禁用** | `loot:194` |
| `arrowsBundle` | 1 | 1 | 1 | `custom_pickup` | `loot:195` |

- `countPerDrop` = 地上一包多少发。`inventorySlotCount` = 背包一格放多少。
- 倍率：`loot_ammo_scale_per_drop`、`inventory_ammo_scale_stacksize`（`all:837-838`）。
- 枪落地时附带弹：`sv:2845` 起（`ammoMin 1`、`ammoMax 2` 包），每包 `countPerDrop × scale`（`sv:2902`）。
- 生成流程：`SpawnGenericLoot( ref, ..., count )`（`sv:2922`），`sv:7310-7319` 把大包按 `countPerDrop` 拆开。
- 掉落组 `ammo`（`groups:692-697`）：bullet 26、shotgun 6、highcal 28、special 23、sniper 17。**special 还有权重，但行禁用**，推断掉落时走 `Disabled` 过滤，不一定按比例重新分配，要实测。

Bocek 箭在禁用后用 `arrowsBundle`（自定义捡拾）。

#### 3.2.5 suck 行为

`suck` 文件：4 组加 `disabled`：

| 组 | 允许 | `FORCE_SAME_WEAPON` |
|---|---|---|
| `primary_weapons` | rifle、pistol、anti-titan | 1 |
| `special_weapons` | special | 1 |
| `offhand_weapons` | ordnance（tactical 0） | 1 |
| `melee_weapons` | melee 0 | 1 |
| `disabled` | `FORCE_NO_SUCK 1` | |

字段 `ammo_suck_behavior`：101 个 `mp_weapon_*` 用 `primary_weapons`，29 个 `offhand_weapons`，3 个 `melee_weapons`（比如 `rspn101.txt:193`）。`vscripts` 里**没有** `FORCE_SAME_WEAPON` 或 `ammo_suck` 的脚本逻辑（grep 无结果）。这是 Titanfall 武器掉落吸弹的残留，推断在 Apex 里不起作用。

### 3.3 客户端表现

- `ammoPoolVisible` = `uses_ammo_pool`（`client/rui/cl_weapon_status.gnut:2025`）。
- `low_ammo_fraction`：低弹 HUD 和语音。Boosted Loader 也读它（见 [hopups](../hopups/SYSTEM.md) 3.2.3）。
- 背包：`cl_survival_inventory.nut:1136`。

### 3.4 依赖的公共代码

- `Weapon_FillClipAmmoFromStock`（`wu:6887` Kinetic 用）。
- `GetInfiniteAmmo`（`wu:6428`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| `countPerDrop` | bullet 20、highcal 20、shotgun 10、sniper 14 | 发/包 | `loot:189-193` | 一包多少 | 多了不缺弹 |
| `inventorySlotCount` | 60 / 60 / 20 / 28 | 发/格 | `loot:189-193` | 堆叠 | 带得多 |
| `ammo_stockpile_max`（Havoc） | 54 | 发 | `energy_ar.txt:71` | 枪内上限 | |
| 能量弹匣 ++备弹 | 3 倍弹匣增量 | 发 | `energy_ar.txt:621-636` | 上限随弹匣 | |
| `ENERGY_RESERVE_REGEN_START_DELAY` | 0.1 | s | `wu:4766` | 回充延迟 | |
| `ENERGY_RESERVE_REGEN_SECONDS_PER_CLIP` | 18（空投 22） | s/弹匣 | `wu:4767-4768` | 回满一弹匣 | |
| `ENERGY_MAG_RESERVE_REGEN_SCALE` | L1 1.5、L2 2、L3 2.5、L4 2.5 | × | `wu:4772-4777` | 弹匣加回充 | |
| `LSTAR_RESERVE_REGEN_ROUNDS_PER_SEC` | 1.22（空投 1.27）；L1 1.34、L2 1.44、L3 1.56 | 发/s | `wu:4769-4784` | | |
| `loot_ammo_scale_per_drop` | 1.0（默认） | × | `all:837` | playlist | |
| `inventory_ammo_scale_stacksize` | 1.0（默认） | × | `all:838` | playlist | |
| Boosted Loader 超载退弹 | 超出原上限的部分 | 发 | `wu:6403-6407` | | |

每把枪的弹匣和备弹见 `../_shared/W-PARAM-COMPARE.md`。

## 5. 未解决和要实测的

1. **能量回充**（`wu:4822`）：本地重写。**测**：Havoc 打空弹匣后不动，`GetWeaponPrimaryAmmoCount( AMMOSOURCE_STOCKPILE )` 随时间变化，按公式是否 1 发/s。
2. **`ammo_no_remove_from_stockpile`**：**测**：`hemlok`（1）和 `rspn101`（0）开火时公共池变化；换弹时变化。
3. **`special` 在掉落组的权重**：**测**：跑若干次开局统计地上弹药种类，有没有 `special`，比例怎样。
4. **Bocek 箭**：`loot:194` 禁用后，地上有没有 `arrowsBundle`，捡了是否回 stockpile。
5. **字符串 / 整数**（`all:572-575`）：现在两种都处理。**测**：dedi 和 client 的 `data.ammoType` 打印是否一致。
6. **mod 改 `ammo_pool_type`**：`alt_ammo`（C.A.R.）走 SDK 的 `VWeaponAmmoPoolMod`。**测**：切弹种后 `GetWeaponAmmoPoolType()`、换弹从哪个池扣；dedi 上是字符串还是整数。

## 6. HSD 实现

**未实现**。`Combat/` 没有弹药池。`Weapon` 基类和 `TestRifle` 的弹量是简单计数（要看实现）。

建议做法：

1. **先只做"枪内备弹"模型**：PvE 单人，弹匣 + 备弹 + 回充最简单。`uses_ammo_pool` 这一套多人经济可以不做，记 `R5-DIFF-ARCHIVE.md`。
2. **回充**：照搬 3.2.3 的公式：`rate = 弹匣 / 18`，开火或刚用过等 0.1 s，再按 `scale` 加速。这个公式本来就是 R5F 补丁，和原版 Apex 的能量枪不一样，要写明出处。
3. **要做公共池时**：`Dictionary<AmmoType, int>`，`Weapon.Reload` 先查 `usesAmmoPool`；Boosted Loader 的退弹在这里实现。
4. **掉落**：表里两个数（一包、一格）分开，对 HSD 有意义。

开关建议：`CombatLoadout` 增 `ammoModel = StockpileRegen | SharedPool`，默认 `StockpileRegen`。

和 R5 的差别：还没有实现，暂无。
