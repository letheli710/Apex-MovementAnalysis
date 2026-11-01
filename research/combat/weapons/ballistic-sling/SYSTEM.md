# Ballistic 第三把武器 Sling（备用槽）：系统记录

武器阶段 W1，2026-11-01，静态研究（只读脚本，没进游戏）。大招 Tempest 的光环、buff 看 [`../../ballistic-tempest/SYSTEM.md`](../../ballistic-tempest/SYSTEM.md)；这里只写第三槽本身，可以当"备用槽"系统来复用。

出处从 `research-src/s21-platform/scripts/` 开始。`sling` = `vscripts/pilot/sh_pilot_passive_sling.gnut`，`ult` = `vscripts/weapons/mp_ability_portable_auto_loader.nut`，`slot` = `vscripts/sh_survival_equipment_slot.gnut`，`inv` = `vscripts/cl_survival_inventory.nut`，`loot` = `vscripts/survival_loot.gnut`，`clloot` = `vscripts/cl_survival_loot.nut`，`shloot` = `vscripts/sh_survival_loot.gnut`，`status` = `vscripts/client/rui/cl_weapon_status.gnut`，`consts` = `vscripts/sh_consts.gnut`。

## 0. 概要

- **武器**：Ballistic / 被动 `PAS_WEAPON_SLING` / 第三把主武器。
- **一句话**：多一个武器槽（内部编号 4），不进普通切枪循环，按专用键切出来。能放普通地面枪，放不进空投级。开大期间枪换成金色版，结束换回。
- **分类**：
  - 效果：多带一把枪。
  - 可视化：HUD 上的 Sling 面板（枪图标 + 弹药颜色 + 弹量）。
  - 可复用系统：**备用槽**（额外武器槽 + 装备槽 + 专用切换键 + 准入规则 + 临时替换枪）。
- **可拆出的部件**：
  - 第五个武器槽位 + 装备槽名 → 3.2.1
  - 准入规则 → 3.2.2
  - 切换键 → 3.2.3
  - 主槽和备用槽互换（保留弹量、转移配件）→ 3.2.4
  - 临时换金色、结束换回 → 3.2.5
  - HUD 面板 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 第三把枪 | 普通武器进 `WEAPON_INVENTORY_SLOT_PRIMARY_4`（值 4） | `sling:33`、`consts:77` |
| 背包界面的位置 | 装备槽 `sling_weapon`，`passiveRequired = PAS_WEAPON_SLING` | `sling:34`、`slot:546-563` |
| 有没有这个能力 | 被动 `PAS_WEAPON_SLING` | `sling:76` |
| 切枪 | 客户端命令 `weaponSelectSlingWeapon` | `sling:490`、`inv:422` |
| 槽互换 | `SwapPrimaryWeaponsInSlots`，再收枪重发 | `sling:284` |
| 枪的等级 | `SetWeaponLockedSet`（GOLD / PURPLESET / BLUESET / WHITESET） | `sling:354-382` |
| 枪的换发 | `TakeWeaponByEntNow` + `SpawnGenericLoot` + `SURVIVAL_GiveMainWeapon` + 销毁地面物 | `sling:202-230` |
| HUD | RUI `ui/gunzerker_tactical.rpak` | `sling:513` |

**S3 / S21 差异**：`sling` 文件里没有 S3 / S21 补丁注释（grep "S3 / S21 / dedi" 无结果）。SDK 补了脚本方法：`SwapPrimaryWeaponsInSlots`（`research-src/s21-r5sdk/src/game/server/entity_script_ext.cpp:265`、`:494`）、`SetWeaponLockedSet`（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:2052`）。客户端命令 `weaponSelectSlingWeapon`（`sling:490`）在 SDK 里 grep 不到，待实测（第 5 节第 1 条）。

## 2. 流程

```
拿到被动 → PassiveSling_OnPassiveChanged：记 storedPreSlingWeaponRefs[player] = ""（sling:191-197）
捡枪：Sling 空且枪符合规则 → 进 Sling（clloot:804、loot:3477）
切枪：+scriptCommand5
  在手里是 Sling → 切回上次的主槽（GetLastCycleSlot）
  否则 Sling 不空 → weaponSelectSlingWeapon + 音效
开大期间多一个键：+offhand4 也能切到 Sling（ult:78、ult:720-726）
背包拖拽：Sling ↔ 主槽 → ClientCallback_Sur_SlingToMainWeaponSlot
丢枪：DropSlingWeapon；开大期间不能丢（sling:234）
失去被动：收走枪，删记录（sling:173-188）
```

大招期间：

```
大招开始 → ConvertSlingWeaponToGold（ult:326）：每帧等到有 Sling
  记 alt_ammo；收走枪；用存好的 ref 重发（此时 lockedSet = GOLD）
  如果是能充能的枪（has_energized）：强制进入充能，到期时间 = energized_duration
大招结束 → 换回普通版，保留弹匣、能量状态、alt_ammo（ult:197-228，主记录 3.2.4）
```

## 3. 代码

### 3.1 入口

`ShPassiveSling_Init`（`sling:50-72`）：服务端加击杀统计和被动变化回调；客户端注册 `+scriptCommand5`、HUD 创建 / 销毁回调；注册远程调用 `ClientCallback_Sur_SlingToMainWeaponSlot`（参数范围 0 到 `WEAPON_INVENTORY_SLOT_PRIMARY_1`）。

### 3.2 核心逻辑

#### 3.2.1 槽位

- 武器：`SLING_WEAPON_SLOT = WEAPON_INVENTORY_SLOT_PRIMARY_4`，`GetNormalWeapon(4)` 拿枪（`sling:33`、`sling:81`）。
- 装备：`RegisterEquipslot(SLING_EQUIPMENT_SLOT_NAME, SLING_WEAPON)`，自带特殊丢弃函数（`slot:546`、`slot:561`）。
- 同步：每次变动 `UpdateWeaponSlingEquipmentSlot` 把 ref 写进 `Inventory_SetPlayerEquipment`（`sling:243-256`）。
- 下一把枪的计算：手里是 Sling 时，"另一把"按 `GetLastCycleSlot` 算（`shloot:2677`）。

#### 3.2.2 准入规则（`sling:84-121`）

```
CanPlayerEquipWeaponRefToSling(ref, doPlayerChecks):
  if doPlayerChecks and 大招开着 and Sling 不空: false
  data = 查 loot 表
  if lootType != MAINWEAPON: false
  if tier > 4: false
  true
```

所以：只看 loot 类型和 tier，不限枪种。tier ≤ 4 是"能进"的唯一等级限制；空投枪是不是 tier 5 要看 loot 表（推断）。

#### 3.2.3 切换键

`AttemptWeaponSlingSwap`（`sling:475-500`）：

```
if 手里是 Sling: 切回 GetLastCycleSlot 对应的枪；return
if Sling 不空: ClientCommand("weaponSelectSlingWeapon")；播 Ballistic_Passive_EquipSling_1P；刷新 HUD
```

键位：

- 平时 `+scriptCommand5`（`sling:64`），先过 `TryCharacterButtonCommonReadyChecks`（`sling:469`）。
- 大招期间额外 `+offhand4`（`ult:78`）：只负责切到 Sling，已经拿着就不动（`ult:720-726`）。

注意 `+offhand4` 只有大招期间才是切换键，平时是 `+scriptCommand5`。

#### 3.2.4 互换（`sling:258-352`）

```
记两边弹匣数
SwapPrimaryWeaponsInSlots(4, slot)
新主槽里的枪：收走，用存的 ref（或 baseWeapon）重发，弹匣 = 原 Sling 弹量，去掉倍镜
新 Sling 里的枪：把更好的配件转给另外两把枪；卸掉配件；收走，按 ref 重发，弹匣 = 原主枪弹量
刷新皮肤、背包、装备槽
```

Sling 里的枪**不带配件**（`sling:325` 卸掉；`sling:209` 去倍镜）。它是"裸枪"，所以开大变金才有意义（推断）。

#### 3.2.5 金色转换

`ConvertSlingWeaponToGold`（`ult:326-371`）。金色靠 `SetWeaponLockedSetForSlingWeapon`：`IsBallisticUltActive` → GOLD，否则按升级 PURPLESET / BLUESET / WHITESET（`sling:354-382`）；调用方是 `survival_loot.gnut:3834`（主记录）。升级路径 `GetSlingWeaponRefForPlayerUpgradeLevel`（`sling:148-168`）拼 ref 后缀。

能充能的枪强制充能（`ult:350-357`）：SDK 有 `ForceEnergizeState`（`research-src/s21-r5sdk/src/game/server/energize.cpp:663`），行为待实测。

#### 3.2.6 大招期间的限制

Sling 已有枪就不能换（`sling:88`）；不能丢（`sling:234`）；背包拖拽也挡（`inv:434`、`inv:1623`、`shloot:5114`）。Sling 空着时大招期间可以捡（推断：`sling:88` 只在不空时拦）。

### 3.3 客户端表现（HUD）

`CreateSlingPassiveRui_Internal`（`sling:507`）建 `ui/gunzerker_tactical.rpak`，`TrackSlingRui`（`sling:533`）监视枪变化，`UpdateSlingPassiveRui`（`sling:554`）写入：

| RUI 字段 | 内容 | 来源 |
|---|---|---|
| `isInUlt` | 大招是否开着 | `sling:603` |
| `weaponIcon` | 枪图标 | `sling:604` |
| `ammoColor`、`ammoIcon`、`backgroundColor` | 弹药类型颜色 | `sling:605-608` |
| `stockAmmoFrac`、`clipAmmoFrac`、`maxMagAmmo`、`maxAmmo` | 用 `RuiTrackFloat` 绑定枪 | `sling:610-613` |
| `chargeFrac`、`readyFrac`、`refillRate` | 同上 | `sling:619-621` |

开大时颜色改黄 `<1, 0.91765, 0.15294>`（`sling:599-600`）。其他 HUD：主武器状态判断 `isSlingWeapon`（`status:506`、`status:642`、`status:1392`）。

### 3.4 依赖的公共代码

`SURVIVAL_GiveMainWeapon`、`SURVIVAL_DropMainWeapon`、`SURVIVAL_TransferBetterModsToOtherWeapon`、`Inventory_SetPlayerEquipment`。配件和 mod：`../_shared/W-MOD-SYSTEM.md`。

## 4. 参数

没有武器字段，全是脚本常量和规则。

| 参数 | 值 | 来源 | 作用 / 改了会怎样 |
|---|---|---|---|
| `SLING_WEAPON_SLOT` | 4 | `sling:33` | 槽位号 |
| `SLING_EQUIPMENT_SLOT_NAME` | `sling_weapon` | `sling:34` | 背包槽名 |
| 准入 `lootType` | `MAINWEAPON` | `sling:114` | 放宽可以放别的 |
| 准入 `tier` | ≤ 4 | `sling:117` | 改小就只能放低级枪 |
| 切换键 | `+scriptCommand5` | `sling:64` | |
| 大招切换键 | `+offhand4` | `ult:78` | |
| 大招等级 | `eWeaponLockedSet.GOLD` | `sling:361` | 换等级就是换强度 |
| 升级等级 | ≥ 2 PURPLESET，= 1 BLUESET，否则 WHITESET | `sling:366-376` | |
| ref 后缀 | `WEAPON_LOCKEDSET_SUFFIX_PURPLESET` / `_BLUESET` | `sling:158-164` | |
| 大招时长、加速 | 看主记录 | `../../ballistic-tempest/SYSTEM.md` | |

## 5. 未解决和要实测的

1. **第三槽在 dedi 上能不能跑**。SDK 有 `SwapPrimaryWeaponsInSlots`，但 `weaponSelectSlingWeapon`（`sling:490`）查不到实现。测：用 Ballistic 进火力训练场，地上捡第三把枪，按键切换，再背包拖拽互换，看是否切枪、弹量是否保留、console 有没有报错。
2. **`SetWeaponLockedSet` 和金色转换**。测：开大前后读 Sling 的 mods，看是否满配件；结束是否换回、弹量是否保留。
3. **`has_energized` 强制充能**（`ult:350-357`）：走 SDK 的 `research-src/s21-r5sdk/src/game/server/energize.cpp`。测：Sling 放 Sentinel 再开大，看是否报错。
4. **键位绑定**：`+scriptCommand5` 在本地客户端绑在哪；`+offhand4` 在大招外是否被别的东西占。
5. **空投枪 tier**：`tier > 4` 能否挡住 Kraber，读 `survival_loot.csv` 或捡一下。

## 6. HSD 实现

**未实现**。`CombatLoadout.cs` 持有武器和技能，`WeaponKind` 只有 Rifle、SmartPistol、Inferno（`Weapons.cs`）。分支 `origin/claude/w2-framework-b44e35` 里 grep `Sling`、`reserve`：没有。

建议做法（备用槽，不绑定 Ballistic）：

1. `CombatLoadout` 加 `Weapon reserve`，单独的切换输入，不进普通切枪循环。记 `lastMainSlot`，切回用它。
2. 准入规则做成委托：`Func<WeaponKind, bool> canHoldInReserve`，默认拒绝空投级。
3. 临时替换：`ReserveOverride { WeaponKind temp; float until; }`。开始时存弹匣，结束恢复。R5 是收枪重发，HSD 单机不需要，直接换引用（和 R5 的差别进 `R5-DIFF-ARCHIVE.md`）。
4. HUD 加一块 Sling 面板，内容照 3.3 的字段。

开关建议：`hsd.combat.reserveSlot.enabled`，默认关，随 Ballistic 打开。
