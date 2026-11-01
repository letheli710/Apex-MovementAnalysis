# 武器配件（瞄具、枪管、激光、弹匣、枪托）：系统记录

会话 wp1，2026-11-01，静态研究（只读脚本和数据，没进游戏）。

出处从 `research-src/s21-platform/` 开始。缩写：`loot` = `datatable/survival_loot.csv`，`wmods` = `datatable/survival_weapon_mods.csv`，`matrix` = `datatable/weapon_attachment_matrix.csv`，`groups` = `datatable/survival_loot_groups_new.csv`，`all` = `scripts/vscripts/sh_survival_loot_all.gnut`，`sh` = `scripts/vscripts/sh_survival_loot.gnut`，`sv` = `scripts/vscripts/survival_loot.gnut`，`wu` = `scripts/vscripts/weapons/_weapon_utility.nut`。`<武器>.txt` = `scripts/weapons/mp_weapon_<武器>.txt`，行号是 mod 名字所在行。`sdk` = `research-src/s21-r5sdk/src/game/`（SDK 的 `server.dll` 源码）。

下面"N 把"的统计不算 `*_og.txt`（见 [weapon-tiers](../weapon-tiers/SYSTEM.md) 第 3.3 节）。mod 语法（`*0.95`、`++2`）见 [W-MOD-SYSTEM](../_shared/W-MOD-SYSTEM.md)。散布和后坐见 [W-SPREAD-RECOIL](../_shared/W-SPREAD-RECOIL.md)，换弹见 [W-FIRE-RELOAD](../_shared/W-FIRE-RELOAD.md)。

## 0. 概要

- **对象**：`sight`、`barrel`、`mag`、`grip` 四个槽的配件，以及 `barrel_hemlok_elite`、`corrupted_*`。hop-up 另见 [hopups](../hopups/SYSTEM.md)。
- **一句话**：配件 = 地上的一个 loot + 武器文件里的同名 mod。三张表决定"能不能装"：枪的 `supportedAttachments`、配件的 `attachmentPoint`、`matrix`。效果全部是字段覆盖，同一件配件在不同枪上数值可以不同。
- **分类**：
  - 效果：枪管、激光、枪托、弹匣等级，加上 `corrupted`（有代价的强配件）。
  - 可视化：瞄具（FOV + ADS 动画 + 瞄具 RUI）、弹匣和枪管的 bodygroup。
  - 可复用系统：等级化配件表、三表过滤、"同名 mod 每把枪自己写数值"。
- **可拆出的部件**：
  - 三表过滤（能不能装）→ 3.2
  - 等级倍率表 → 第 4 节
  - 金色弹匣收枪换弹 → 3.2.3
  - 互斥（一把枪一件 corrupted）→ 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 所有数值 | 武器 mod 字段覆盖 | [W-MOD-SYSTEM](../_shared/W-MOD-SYSTEM.md) |
| 瞄具倍率 | `zoom_fov`、`zoom_toggle_fov`（变焦） | FOV 单位度。基础 `zoom_fov 70`（见 W-PARAM-COMPARE），瞄具覆盖 |
| 瞄具外观 | bodygroup、`uiN_enable`、`viewmodel_ads_rui_*` | 客户端 |
| 威胁瞄具 | `threat_scope_enabled 1` + `threat_scope_fadedist_*` | 引擎特性 |
| 激光 | `targeting_laser_enabled 1` | S3 没有这个字段；SDK 只把它**别名**到一个占位槽，让解析通过（`sdk/shared/weapon_script_vars.cpp:3255`）。推断激光由 S21 客户端画；颜色由 `wu:5407` 回调同步 |
| 换弹加速 | `reload_time*`、`reloadsegment_time_*` | 枪托 |
| 金弹匣收枪换弹 | 脚本 `GoldMagPerkThread`（`wu:5218`） | 等级 ≥ LEGENDARY 才启动 |

## 2. 流程

```
捡起或拖到枪上
→ CanAttachToWeapon（_utility_shared.nut:6128）
   枪是锁定套装 且 槽被锁（非瞄具） → 否（sh:7837）
   否则看 AttachmentData.compatibleWeapons
→ 枪加 mod，触发 Loot_AddCallback_OnWeaponAttachmentChanged
→ wu:609-613 的回调（金弹匣、Boosted Loader 等）
→ 卸下：mod 摘掉，配件回背包或丢地上（sv:7088）
丢枪：套装武器只保留 baseMods，把瞄具摘下（sv:4984-4985）
```

## 3. 代码

### 3.1 入口

- `all:841-865`：配件的 loot 行从 `wmods` 查名字、`attachmentPoint`、`type`（风格）。
- `sh:1013-1026`：读 `wmods` 的 `toggleMod`。
- `sh:1033-1120`：读 `matrix`，算每件配件的 `compatibleWeapons`。

### 3.2 三表过滤

| 表 | 列 | 例子 | 含义 |
|---|---|---|---|
| `loot.supportedAttachments` | 枪行 | R-301：`sight mag barrel grip`（`loot:100`） | 枪有哪些槽 |
| `wmods.attachmentPoint` | 配件行 | 瞄具 `sight`；枪管和激光 `barrel`；弹匣和霰弹闩 `mag`；枪托 `grip`；hop-up `hopup` + 多槽（`wmods:48`） | 配件进哪个槽 |
| `matrix` | 配件 × 枪 | `laser_sight_l1`：9 把（`matrix:12`） | 这件配件能不能上这把枪 |

计算（`sh:1061-1122`）：

```
对每件配件（ref 存活且未禁用）：
  对每把枪：
    col = matrix 里 baseWeapon 这一列
    没列 且是 mod 枪 → 看枪文件有没有这个 mod（sh:1080-1093）
    没列 → 用 Weapon_GetBaseClassNameOrEmpty 找基类那一列（sh:1096-1104）
    matrix 为真 且 枪有这个槽 → compatibleWeapons.append
```

反向过滤（`sh:1219-1261`）：枪行写了某个槽，但 `matrix` 里这个槽没有任何可用配件 → 从 `supportedAttachments` 去掉，记 `disabledAttachments`。P2020、RE-45 这种 `barrel` 槽有激光才不会被去掉。

`matrix` 的列共 37 把枪（`matrix:1`），有些是 `_crate`（`lstar_crate`、`g2_crate`、`3030_crate`）。`_crate` 枪和套装的 `supportedAttachments` 写得很窄，所以只有瞄具能换（`loot:9`、`loot:11`）。

**数据和表不一致的地方（本地实际结论）**：

| 配件 | `matrix` | 说明 |
|---|---|---|
| `optic_cq_threat` | 全假（`matrix:6`） | 42 把枪有 mod 块，`loot:284` 存活，但只能靠 `baseMods`（`loot:59`） |
| `barrel_stabilizer_*` | 8 把（`matrix:16`） | 22 把枪有 mod 块。**SMG 和手枪的 `barrel` 槽放激光，不放枪管** |
| `laser_sight_*` | 9 把（`matrix:12`） | `car`、`r97`、`pdw`、`volt_smg`、`alternator_smg`、`wingman`、`semipistol`、`autopistol`、`autopistol_fusion` |
| `shotgun_bolt_*` | 4 把（`matrix:36`） | 无 `_crate` 列 |
| `corrupted_mag` | 24 把（`matrix:92`） | 不含 Alternator、C.A.R.、霰弹枪、DMR |
| `barrel_hemlok_elite` | 1 把（`matrix:19`） | 只有 `auto_hemlok`；`auto_hemlok*` 行自带（`loot:46`） |

C.A.R. 两种弹匣都认（`matrix:20`、`matrix:24`）。

`IsAttachmentAmbiguousForWeapon`（`sh:2412`）断言一件配件不能在同一把枪上同时属于两个槽。`GetAttachPointForAttachmentOnWeapon`（`sh:2372`）靠这条假设查槽。

### 3.2.1 Attachment L4 和 flash hider

- `loot` 有 `bullets_mag_l4`、`highcal_mag_l4`、`energy_mag_l4`、`sniper_mag_l4`、`shotgun_bolt_l4`、`laser_sight_l4`、`stock_sniper_l4`（`loot:297`、`301`、`305`、`309`、`313`、`317`、`324`），tier 4。掉落组里权重多为 0（`groups:46`、`groups:59`）。`stock_tactical` **没有** L4。
- `barrel_stabilizer_l4_flash_hider` 只在武器文件里（14 把），`wmods` 和 `loot` **没有这一行**，也不在 `matrix`，所以数据里拿不到。

### 3.2.2 corrupted

见 3.3。

### 3.2.3 金色弹匣

`wu:5161 OnWeaponAttachmentChanged_CheckForGoldMag`：

```
mag 槽配件 tier >= LEGENDARY（L4）：
  霰弹枪 → 走 Kinetic Loader（wu:5200-5206，见 hopups 3.2.4）
  其他 → thread GoldMagPerkThread
GoldMagPerkThread（wu:5218）：枪收起 且 不满 → 记时间，超过 5 s（wu:397）自动换满
```

### 3.3 Corrupted（`sh:7740-7792`）

- 5 件：`corrupted_mag`、`corrupted_barrel`、`corrupted_laser`、`corrupted_tactical_stock`、`corrupted_stock_sniper`（`loot:427-431`，tier 5，tag `corrupted_attachment`）。
- 掉落组 `corrupted_attachments`（`groups:1979-1984`）：各 21，狙击枪托 16。被 `honeypot`、空投（`care_package_2_L` 50、`care_package_3_L` 40）等引用（`groups:47`、`907`、`923`）。
- **一把枪只能一件**：playlist `has_exclusive_corrupted_attachments`，默认真（`sh:7742`）。`sh:7769-7791` 两个 Blocks 函数，`sh:4239`、`sh:4288`、`sh:7250-7290` 用它拒绝。
- 数值见第 4 节。特点是**加上一个等级装不到的上限，同时给一个代价**。

### 3.4 客户端表现

- 槽位空图标：`sh_survival_equipment_slot.gnut:70-108`。
- 激光：`targeting_laser_enabled`、`custom_laser_sight_color_enabled`，引擎画。
- 瞄具：`viewmodel_ads_rui_bottomleft_attachment` 指向瞄具 RUI，比如 `RUI_BL_CROSSHAIR_HCOG`（`rspn101.txt:587`）。

## 4. 参数

下表值是**大多数枪**的值，后面写例外。

### 4.1 瞄具（mod 字段，无等级）

| 配件 | loot | `zoom_fov` | `zoom_toggle_fov` | `matrix` | 备注 |
|---|---|---|---|---|---|
| `optic_cq_hcog_classic` | T1 `loot:280` | 60 | — | 33 把 | 1x |
| `optic_cq_hcog_bruiser` | T2 `loot:281` | 38.59 | — | 33 把 | 2x |
| `optic_cq_holosight` | T1 `loot:282` | 60 | — | 33 把 | 1x |
| `optic_cq_holosight_variable` | T2 `loot:283` | 60 | 38.59 | 32 把 | 1x-2x |
| `optic_cq_threat` | T4 `loot:284` | 60 | — | 0 | 威胁 `threat_scope_enabled 1`，`ads_force_firstperson 1`，淡出 984–2165 u |
| `optic_ranged_hcog` | T3 `loot:285` | 26.28 | — | 20 把 | 3x |
| `optic_ranged_aog_variable` | T3 `loot:286` | 38.59 | 19.86 | 19 把 | 2x-4x |
| `optic_sniper` | T2 `loot:287` | 13.31 | — | 4 把 | 6x |
| `optic_sniper_variable` | T3 `loot:288` | 19.86 | 10.0 | 4 把 | 4x-8x |
| `optic_sniper_threat` | T4 `loot:289` | 19.86 | 8.01 | 4 把 | 威胁，淡出 5905–11811 u |

倍数列是推断（按 FOV 和游戏里的名字）。`zoom_time_in/out` 每把枪写绝对值，比如 HCOG：手枪 0.22 / 0.20；步枪 0.29 / 0.25；机枪 0.36 / 0.32；SMG 0.24 / 0.22（各枪 `optic_cq_hcog_classic` 块，比如 `rspn101.txt:562`）。`threat_scope_fadedist_*` 字段只是威胁瞄具用，普通瞄具带着也无效果（推断）。

`ads_force_firstperson`：S3 没有，SDK 别名到占位槽（`sdk/shared/weapon_script_vars.cpp:3176`），推断只有客户端生效。

### 4.2 枪管（`barrel_stabilizer`，22 把有块，`matrix` 8 把）

| 字段 | L1 | L2 | L3 | 例外 |
|---|---|---|---|---|
| `viewkick_pitch_base` | `*0.95` | `*0.9` | `*0.85` | L-STAR `*0.97 / *0.94 / *0.9`；Nemesis `*0.9 / *0.85 / *0.8` |
| `viewkick_pitch_random` | `*0.8` | `*0.75` | `*0.7` | L-STAR `*0.82 / *0.79 / *0.75`；Nemesis `*0.75 / *0.7 / *0.65` |
| `viewkick_yaw_base` | `*0.95` | `*0.9` | `*0.85` | 4 把 `*0.85 / *0.8 / *0.75`；L-STAR `*0.97 / *0.94 / *0.9` |
| `viewkick_yaw_random` | `*0.9` | `*0.85` | `*0.8` | Alternator `*0.8 / *0.75 / *0.7`；L-STAR `*0.92 / *0.89 / *0.85`；Nemesis `*0.85 / *0.8 / *0.75` |

来源：`rspn101.txt:854`（L1）、`rspn101.txt:876`（L3）。`barrel_stabilizer_l4_flash_hider`（`rspn101.txt:515`）数值 = L3，加枪口特效。`barrel_hemlok_elite`（`auto_hemlok.txt:530`）是空块，只表示这把枪的枪管槽被占。

### 4.3 激光（`laser_sight`，`matrix` 9 把）

| 字段 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| `spread_*_hip`（站 / 跑 / 冲刺 / 蹲 / 空中） | `*0.80` | `*0.70` | `*0.60` | `*0.60` |
| `spread_moving_increase_rate` | `*0.85` | `*0.80` | `*0.75` | — |
| `spread_moving_decay_rate` | `*1.15` | `*1.20` | `*1.25` | — |
| `spread_decay_rate` | `*1.20` | `*1.30` | `*1.40` | — |
| `spread_decay_delay` | `*0.80` | `*0.70` | `*0.60` | — |
| `spread_max_kick_*_hip`、`spread_kick_on_fire_*_hip` | `*0.80` | `*0.70` | `*0.60` | 绝对值：`kick -0.1 / -0.25`、`spread_min_kick -3` |

**全部武器一样**（19–20 把，无例外）。来源：`r97.txt:798`（L1）、`r97.txt:844`（L3）、`r97.txt:886`（L4）。L4 的 `spread_min_kick`：SDK 只读入（`sdk/server/weapon_kv_s21_ext.cpp:175`），唯一用途是对 ≥ 0 的值发警告（`sdk/server/bridge_zoom_gate.cpp:756`），L4 是 -3，不触发。激光只影响腰射，不影响开镜。

### 4.4 弹匣（每把枪写绝对值或 `++`）

| 枪 | 基础弹匣 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| R-301（`rspn101.txt:50`） | 21 | 23 | 28 | 31 | 31 |
| R-99 | 18 | 21 | 24 | 27 | 27 |
| Alternator | 18 | ++2 | ++4 | ++8 | ++8 |
| Spitfire | 35 | 40 | 45 | 50 | 50 |
| G7 | 10 | 12 | 14 | 16 | 16 |
| P2020 | 9 | ++1 | ++2 | ++3 | ++3 |
| RE-45 | 20 | 21 | 23 | 26 | 26 |
| C.A.R. | 20 | ++3 | ++6 | ++10 | ++10 |
| Flatline | 19 | ++4 | ++8 | ++10 | ++10 |
| Hemlok | 21 | ++3 | ++6 | ++9 | ++9 |
| Hemlok Elite | 18 | ++2 | ++4 | ++7 | ++7 |
| Prowler | 20 | 25 | 30 | 35 | 35 |
| 30-30 | 6 | 7 | 8 | 10 | 10 |
| Rampage | 28 | 32 | 34 | 40 | 40 |
| Longbow | 6 | ++2 | ++4 | ++6 | ++6 |
| Charge Rifle | 6 | 7 | 8 | 9 | 9 |
| Wingman | 5 | ++1 | ++2 | ++3 | ++3 |
| Sentinel | 4 | 5 | 6 | 7 | 7 |
| Havoc（能量，备弹同步加） | 18 / 备 54 | ++3 / ++9 | ++7 / ++21 | ++11 / ++33 | 同 L3 |
| Devotion | 36 / 备 108 | ++4 / ++12 | ++8 / ++24 | ++12 / ++36 | 同 L3 |
| Nemesis | 20 / 备 60 | ++4 / ++12 | ++8 / ++24 | ++12 / ++36 | 同 L3 |
| Volt | 20 / 备 40 | ++2 / ++4 | ++4 / ++8 | ++7 / ++14 | 同 L3 |
| Triple Take | 6 / 备 12 | ++1 / ++2 | ++2 / ++4 | ++4 / ++8 | 同 L3 |
| RE-45 Fusion | 15 / 备 30 | ++3 / ++6 | ++6 / ++12 | ++9 / ++18 | 同 L3 |
| L-STAR（`clip_size 0`，弹量是 stockpile） | 0 / 备 88 | `*1.25` / ++8 | `*1.5` / ++16 | `*2` / ++24 | 同 L3 |

L4 数值 = L3，额外效果只有 3.2.3（金弹匣）。L-STAR 能量弹匣还改 `charge_time`（L1 2.4、L3 2.8）和冷却（L3 `*0.9`、`_crate *0.7`，`lstar.txt:543`）。

能量弹匣改备弹，是因为能量枪不用公共弹药池，见 [ammo](../ammo/SYSTEM.md)。

### 4.5 霰弹闩（`mag` 槽）

| 枪 | L1 | L2 | L3 | L4 | 来源 |
|---|---|---|---|---|---|
| Mastiff `fire_rate` | `*1.1` | `*1.15` | `*1.2` | 同 L3 | `mastiff.txt:382` |
| EVA `fire_rate` | `*1.08` | `*1.15` | `*1.2` | 同 L3 | `shotgun.txt:380` |
| Mozambique `fire_rate` | `*1.05` | `*1.09` | `*1.129` | 同 L3 | `shotgun_pistol.txt:612` |
| Peacekeeper `rechamber_time` | `*0.925` | `*0.87` | `*0.84` | 同 L3 | `energy_shotgun.txt:609`（`fire_rate *1.0`） |

EVA 开 Double Tap 时走 `shotgun_bolt_l#_double_tap`，见 [hopups](../hopups/SYSTEM.md) 3.2.6。

### 4.6 枪托

战术枪托（`stock_tactical`，36 把，无 L4，全部武器相同）：

| 字段 | L1 | L2 | L3 | 来源 |
|---|---|---|---|---|
| `zoom_time_in/out` | `*0.85` | `*0.8` | `*0.75` | `rspn101.txt:726`、`rspn101.txt:790` |
| `deploy_time`、`holster_time` | `*0.85` | `*0.8` | `*0.75` | 同上 |
| `raise_time`、`lower_time` | `*0.9` | `*0.85` | `*0.8` | |
| `viewdrift_ads_*_scale_*` | `*0.85` | `*0.75` | `*0.55` | |
| `reload_time*`、`reloadempty_time*` | `*0.967` | `*0.933` | `*0.9` | |
| `reloadsegment_time_*` | `*0.95` | `*0.875` | `*0.8` | |

狙击枪托（`stock_sniper`，14–15 把，有 L4）有**两档**：

| 字段 | 轻型（8 把）L1 / L2 / L3 / L4 | 重型（7 把）L1 / L2 / L3 / L4 |
|---|---|---|
| `zoom_time_in/out` | `*0.8 / *0.75 / *0.7 / *0.7` | `*0.9 / *0.85 / *0.8 / *0.8` |
| `deploy_time`、`holster_time` | `*0.75 / *0.7 / *0.65 / *0.65` | `*0.85 / *0.8 / *0.75 / *0.75` |
| `raise_time`、`lower_time` | `*0.8 / *0.75 / *0.7 / *0.7` | `*0.9 / *0.85 / *0.8 / *0.8` |
| `viewdrift_ads_*_scale_*` | `*0.8 / *0.6 / *0.35 / *0.35` | `*0.7 / *0.5 / *0.2 / *0.2` |
| `viewdrift_ads_speed_*` | `*0.9 / *0.8 / *0.75 / *0.75` | `*0.9 / *0.85 / *0.8 / *0.8` |
| `reload_time*` | `*0.967 / *0.933 / *0.9 / *0.9` | 同左 |

`reloadsegment_time_*` 只有 30-30、Bocek 这些有分段的（`*0.95 / *0.875 / *0.8`）。来源 `g2.txt:589`（L1）、`g2.txt:651`（L3）、`g2.txt:795`（L4）。两档按数值分：左列 30-30、Bocek、Triple Take、G7（含 `_crate`）；右列 Charge Rifle、Longbow、Sentinel（含 `_crate`）和 `defender_sustained`。"轻型 / 重型"是这里起的名字。

### 4.7 Corrupted

| 配件 | 上限提高 | 代价 | 例外 | 来源 |
|---|---|---|---|---|
| `corrupted_mag` | 弹匣绝对值：R-301 37、R-99 33 | `reload_time* *1.35`–`*1.45`，分段 `*1.15`–`*1.35` | L-STAR 改 `charge_time 3.4`、`ammo_stockpile_max ++48`、冷却 `*1.3`；30-30 12 发 | `rspn101.txt:939` |
| `corrupted_barrel` | 后坐同枪管 L3 + `damage_headshot_scale *1.2` | 腰射 `spread *1.3`–`*1.4`，`kick *1.5`，`moving_increase *2` | 全部 8 把一样 | `rspn101.txt:916` |
| `corrupted_laser` | 同激光 L3，**腰射强** | 无明显代价（Fusion 例外加 `viewkick_*_base *1.8`） | | `r97.txt:913` |
| `corrupted_tactical_stock` | 同战术 L3 | `ammo_clip_size *0.8`（9 把）或 `--4` 等 | L-STAR `charge_time --0.4`、备弹 `--16` | `r97.txt:979` |
| `corrupted_stock_sniper` | 同狙击 L3（重型档） | 同上推断 | | `g2.txt:874` |

等级和倍率来自 `.txt`，上面"同 L3"是比对字段得出。

## 5. 未解决和要实测的

- **S3 dedi 字段差异**（`W-S3-FIELD-CHECK`）：`targeting_laser_enabled`、`ads_force_firstperson` 是占位别名，`spread_min_kick` 只读入。散布倍率字段本身两边都认。**测**：激光 L1 / L3 腰射散布是否变小（`GetAttackSpreadAngle`）；激光 L4 的负 kick 和 -3 下限有没有效果；激光线在 dedi 上看不看得到。
- **枪托 viewdrift**：`viewdrift_ads_*` 两边都认。**测**：Sentinel 开镜时抖动幅度比无枪托小多少，对应 `*0.35` / `*0.2`。
- **Havoc 能量弹匣备弹**：`ammo_stockpile_max ++` 是否即时生效，以及 3.2.3 对能量枪的影响。**测**：Havoc 换 L3 弹匣读 `GetWeaponPrimaryAmmoCountMax`。
- **金弹匣**：L4 掉落权重基本是 0，手动给 `bullets_mag_l4`。**测**：R-301 打几发收枪 5 s 后是否满。
- **`optic_cq_threat`**：`matrix` 全假（只给空投 `alternator_smg_crate`）。**测**：`threat_scope_enabled` 是否在 dedi 正常。
- **corrupted**：**测**：装一件后试图再装，提示和返回。

## 6. HSD 实现

**未实现**。`HSD-Unity/Assets/HSD/Game/Runtime/Combat/` 没有配件系统，`CombatLoadout.cs` 只选装备。

建议做法：

1. **`WeaponMod` 资产**：字段名 + 运算（`=`、`*`、`++`、`--`）列表。和 `Weapon` 的 `WeaponStats` 结构一一对应。R5 把"同名 mod 每把枪都写一份"，HSD 用**默认表 + 每把枪覆盖**更省：第 4 节的全部武器相同的（激光、战术枪托）放默认表；弹匣每把枪写。
2. **三表过滤改成两层**：武器资产列槽位；配件资产列 `slot` 和 `allowedFamilies`（狙 / 步 / SMG）。不需要 37 × 90 的矩阵。
3. **第一批**：弹匣 L1-3、枪管 L1-3、枪托 L1-3。瞄具 FOV（`zoom_fov` 直接换算）。后续做 corrupted（风险 / 收益），和 mod 叠加的先后见 `W-MOD-SYSTEM` 3.3。
4. **激光和枪管共槽**这种 R5 规定可以不抄。R5 这么做是为了限制 SMG；HSD 单人 PvE 没有这个平衡压力，建议分开，差别进 `R5-DIFF-ARCHIVE.md`。

开关建议：`CombatLoadout` 增加 `attachments` 字典；PlayerPrefs `hsd.combat.weapon.attach.<slot>`。

和 R5 的差别：还没有实现，暂无。
