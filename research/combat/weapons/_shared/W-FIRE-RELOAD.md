# 公共部件 W：开火节奏、换弹、备弹回充

会话 wp1，2026-11-01，静态研究。出处从 `research-src/s21-platform/scripts/` 开始。`wu` = `vscripts/weapons/_weapon_utility.nut`。

## 0. 概要

- **部件**：扳机模式、射速、点射、拉栓、换弹时间、能量枪备弹回充。
- **一句话**：节奏几乎全是 `.txt` 字段，由引擎执行；脚本只在特殊武器上介入。`OnWeaponPrimaryAttack` 的**返回值就是扣的弹药数**，返回 0 就不扣（等于这次没打）。
- **分类**：系统。
- **可拆出的部件**：返回值当扣弹 → 3.1；点射 → 3.2；分段换弹 → 3.3；备弹回充 → 3.4。

## 1. 实现手段

| 效果 | 手段 | 来源 |
|---|---|---|
| 全自动 / 半自动 | `fire_mode`、`is_semi_auto` | Hemlok `is_semi_auto 1`（`mp_weapon_hemlok.txt:13`） |
| 点射 | `burst_fire_count`、`burst_fire_delay` | Hemlok 3 发 / 0.25 s（`mp_weapon_hemlok.txt:97-98`） |
| 拉栓 | `rechamber_time` | Kraber 1.6 s；Sentinel 1.6 s |
| 开火门槛 | 回调返回 0 | Charge Rifle（`mp_weapon_defender.nut`：`GetWeaponChargeFraction() < 1.0` 返回 0）；Sheila。Havoc 的 `CanFire_EnergyAR` 是死代码（`.txt` 没绑），真门槛是 `charge_attack_min_charge_required`（[charge-spinup](../charge-spinup/SYSTEM.md)） |
| 战术换弹 | `reload_time` + `reload_time_late1..5` | R-301 2.4 s，late1 1.8 s |
| 空仓换弹 | `reloadempty_time` + `_late*` | R-301 3.2 s |
| 分段换弹 | `reload_is_segmented`、`reloadsegment_time_loop` | Mastiff、30-30 |
| 备弹回充 | 脚本线程 `EnergyAmmoRegen_Think` | `wu:4822` |

## 2. 流程

```
按键 → 引擎检查：not reloading、弹量 ≥ ammo_min_to_fire、过了 1 / fire_rate
→ OnWeaponPrimaryAttack(params) → 返回 n → 弹匣 −= n
点射：S3 服务端不给 burst 计数赋值，SDK 补（`s21-r5sdk/src/game/shared/weapon_heat.cpp:44-47`）。fire_rate 是点射内的射速，打完 burst_fire_count 发后停 burst_fire_delay（推断）
换弹：reload_time 全长，late1 是"过了这个里程碑，打断也算换好"（推断，OnWeaponReload 有 milestoneIndex）
```

## 3. 代码

### 3.1 回调返回值

普通枪：`weapon.FireWeapon_Default(...); return weapon.GetWeaponSettingInt(eWeaponVar.ammo_per_shot)`（`mp_weapon_r97.nut`、`mp_weapon_rspn101.nut:27`）。C.A.R. 空仓时返回 0 并触发换弹种（`mp_weapon_car.nut:94-122`）。

### 3.2 点射实际射速

| 枪 | `fire_rate` | 发 | `burst_fire_delay` | 推断周期 | 推断每秒发数 |
|---|---|---|---|---|---|
| Hemlok | 15.5 | 3 | 0.25 | 3/15.5 + 0.25 = 0.444 s | 6.8 |
| Prowler | 21 | 5 | 0.23 | 5/21 + 0.23 = 0.468 s | 10.7 |
| Nemesis | 18 | 4 | 0.21 | 4/18 + 0.21 = 0.432 s | 9.3 |

名义 DPS（射速 × 伤害）对点射枪虚高，比较时看这一列。

### 3.3 弹匣和里程碑

`OnWeaponReload_xxx(weapon, milestoneIndex)` 是脚本钩子（`mp_weapon_defender.nut`、`mp_weapon_hemlok.nut`）。智能换弹靠它（[hopups](../hopups/SYSTEM.md)）。

### 3.4 能量枪备弹回充（`wu:4742-4875`）

```
EnergyAmmoRegen_Start：只在 SERVER，线程只开一次
每帧：
  备弹减少 或 正在开火 → readyTime = now + 0.1；carry = 0
  没到 readyTime 或满了 → carry = 0
  carry += RoundsPerSecond × dt；整数部分加到备弹
RoundsPerSecond：
  L-STAR（弹匣 0）：1.22，crate 1.27，弹匣配件有单独表
  其他：弹匣容量 / 18 s（crate / 22 s），按弹匣配件乘 scale
```

常量在 `wu:4766-4770`。用它的枪：Devotion（`mp_weapon_esaw.nut`）、Volt、Havoc（`mp_weapon_energy_ar.nut`）、Nemesis（`mp_weapon_nemesis.nut:91`）。

**注意**：这是**备弹**自己回涨，正版 Apex 没有。推断是这个社区构建加的，`ammo_regen_takes_from_stockpile` S3 引擎不认。PvE 里是现成的"能量枪不缺弹"机制。

## 4. 参数

见各族 `PARAMS.md` 的"射击 / 弹药 / 时间"。

## 5. 未解决和要实测的

- **`burst_fire_delay` 语义**：测 Hemlok 打两组的时间。
- **`late1` 语义**：在里程碑前后切枪，看弹量。
- **回充是否生效**：Havoc 开一匣看备弹涨速，期望容量 18 / 18 s = 1 发/s。

## 6. HSD 实现

**部分有。** `Weapon` 有 `mag / magSize / nextShot / reloadUntil`，`TestRifle` 空了自动换弹（`Weapons.cs`）。没有备弹、点射、拉栓、里程碑。

建议：把 `TestRifle.Step` 的节奏提到基类 `FiringCycle`，由数据驱动；开火函数返回扣弹数，和 R5 对齐。
