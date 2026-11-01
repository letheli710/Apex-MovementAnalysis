# 点射枪：系统记录

会话 wp1，2026-11-01，静态研究（只读脚本和数据，没进游戏）。出处从 `research-src/s21-platform/scripts/` 开始。`.nut` 在 `vscripts/weapons/`，`.txt` 在 `weapons/`。参数全表：[PARAMS.md](PARAMS.md)。

## 0. 概要

- **武器**：Hemlok `mp_weapon_hemlok`、Hemlok Elite `mp_weapon_auto_hemlok`、Prowler `mp_weapon_pdw`、Nemesis `mp_weapon_nemesis`。G7 的双发 hop-up 也是点射，放在 [sniper-marksman](../sniper-marksman/SYSTEM.md)。
- **一句话**：点射由 `burst_fire_count` 和 `burst_fire_delay` 两个字段实现。切全自动 / 单发就是一个 mod。Nemesis 多一个"越打越快"的热量；Hemlok Elite 多一个发射爆破弹的替代开火。
- **分类**：效果（节奏）＋ 系统（Nemesis 热量爬升、Elite 替代开火冷却）＋ 可视化（Nemesis 枪身随热度发光）。
- **可拆出的部件**：
  - 点射节奏 → [W-FIRE-RELOAD](../_shared/W-FIRE-RELOAD.md) 3.2
  - 模式切换 mod → 3.1
  - 热量驱动字段插值 → 3.2
  - 主武器上的冷却替代开火（榴弹）→ 3.3
  - 视觉：控制点接热度 → 3.4

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 点射 | `fire_rate` + `burst_fire_count` + `burst_fire_delay` | Hemlok `mp_weapon_hemlok.txt:96-98`；Prowler `mp_weapon_pdw.txt:85-87`；Nemesis `mp_weapon_nemesis.txt:115-117` |
| 单发模式 | Hemlok mod：`is_semi_auto 1`、`fire_rate 6.4`、`burst_fire_count 0` | `mp_weapon_hemlok.txt:433-436` |
| 全自动模式 | Prowler mod：`fire_rate 13.25`、`burst 0`、`viewkick_pattern pdw_auto_2` | `mp_weapon_pdw.txt:881-890` |
| 热量爬升 | `has_heat_decay 1`、`heat_per_bullet 0.04167`、`heat_mod_var0 burst_fire_delay` 从 0.31 到 0.19；满热 mod `fully_heated`（`burst_fire_delay 0.18`） | `mp_weapon_nemesis.txt:21-31`、`:428-430` |
| 热量表现 | `GetHeatValue` 驱动粒子控制点和 RUI，全在 CLIENT | `mp_weapon_nemesis.nut:82-83`、`:205-250` |
| 爆破弹 | mod `altfire` + `Grenade_Launch`，`damageSourceId mp_weapon_auto_hemlok_breach_charge`，碰撞即炸 | `mp_weapon_auto_hemlok.nut:62-86`、`:105-117`；`mp_weapon_auto_hemlok.txt:446` 起 |
| 替代开火冷却 | 线程 + `SetScriptTime0`，playlist `auto_hemlok_cooldownTime`，默认 30 s | `mp_weapon_auto_hemlok.nut:12`、`:124-158` |
| 智能换弹 | `hopup_smart_reload`：`OnWeaponActivate_Smart_Reload` | `mp_weapon_hemlok.nut`；见 [hopups](../hopups/SYSTEM.md) |
| 备弹回充 | `EnergyAmmoRegen_Start` | `mp_weapon_nemesis.nut:91` |

**混合构建（重要）**（[W-S3-FIELD-CHECK](../_shared/W-S3-FIELD-CHECK.md)）：

- **点射本身就靠 SDK**：`bridge_burst_fire_seed` 的注释说 S3 服务端自己不给 `m_burstFireCount` 赋值，SDK 从 KV 补（`s21-r5sdk/src/game/shared/weapon_heat.cpp:44-47`，默认 1）。关掉后每种点射枪都打满长度。
- **热量是 SDK 重写**：S3 引擎没有这些字段和方法，`weapon_heat.cpp:384-392` 读 `has_heat_decay`、`heat_per_bullet`、`heat_mod_var0`；插值写入有开关 `sdk_weapon_heat_modvar_write`（`:38`，默认 1）。`GetHeatValue`、`HasHeatDecay` 在 `server.dll` 里。
- `mp_weapon_nemesis.txt:44` 注释 `OnWeaponHeatStateChanged` 在 dedi 上没绑定，所以这个回调的逻辑不会跑。

所以 R5 本地的 Nemesis 爬升**不是原版代码**，曲线要实测。

## 2. 流程

点射枪：

```
按住 → 打 burst_fire_count 发（间隔 1 / fire_rate）→ 等 burst_fire_delay → 重复（半自动的要重新按）
```

Nemesis 设计流程（S21）：

```
每发 heat += 0.04167（24 发满）
burst_fire_delay = lerp(0.31, 0.19, heat)
heat = 1 → fully_heated，burst_fire_delay = 0.18
停火 heat_decay_delay 8 s 后，按 heat_decay_time 8 s 回落
```

Hemlok Elite 替代开火：

```
切到 altfire → 按开火 → 没冷却就发一枚榴弹，RemoveMod(altfire)，开始冷却（默认 30 s）→ 命中即炸
```

## 3. 代码

### 3.1 模式切换

和 auto-ballistic 3.2 相同。Hemlok 的 `fireMode` 是 RUI 参数（`mp_weapon_hemlok.txt:970`，`eWeaponVar.burst_fire_count`），准星按它显示。

### 3.2 热量（设计，见上方怀疑点）

**HSD 可借的是这个模型**：一个 0–1 的状态值 + 每发增量 + 延迟回落 + 用它插值**任意字段**（`heat_mod_var0`）+ 满值 mod。比写死的"射速爬升"更通用；Devotion 的 `fire_rate_max` 是它的特例（[charge-spinup](../charge-spinup/SYSTEM.md)）。

### 3.3 替代开火（`mp_weapon_auto_hemlok.nut:62-90`）

```
if HasMod(altfire):
    if 冷却中: return 0
    p = Grenade_Launch(...)
    p.damageSourceId = breach_charge
    thread 冷却
    RemoveMod(altfire)
    return 0                  // 不扣弹匣
FireWeapon_Default(...)
```

`altfire` 的 `ammo_per_shot -1`、`damage_near_value 0`、`explosion_damage 38`、`grenade_fuse_time 5`（`mp_weapon_auto_hemlok.txt:446-485`）。**PvE 可借**：给主武器挂一个技能。

### 3.4 客户端表现

`UpdateFX_Client`（`mp_weapon_nemesis.nut:96` 起）：粒子控制点 15 = 热度（`:205-220`）；`UpdateHeat_Client`（`:275` 起）更新 RUI。

## 4. 参数

**全部参数看 [PARAMS.md](PARAMS.md)。**

| 枪 | `fire_rate` | `burst_fire_count` | `burst_fire_delay` | 推断周期 / 每秒发数 | 伤害 | 爆头 / 腿 | 弹匣 | 换弹 / 空换 | 弹速 | 后坐图案 |
|---|---|---|---|---|---|---|---|---|---|---|
| Hemlok | 15.5 | 3 | 0.25 | 0.444 s / 6.8 | 20 | 1.4 / 0.75 | 21 | 2.4 / 2.85 | 27500 | `hemlok_2` |
| Hemlok 单发 | 6.4 | 0 | 0 | — / 6.4 | 20 | 同上 | | | | |
| Hemlok Elite | 7.7 | 0 | — | — / 7.7 | 21 | 1.4 / 0.75 | 18 | 2.3 / 2.55 | 27500 | 见 PARAMS |
| Prowler | 21 | 5 | 0.23 | 0.468 s / 10.7 | 16 | 1.25 / 0.8 | 20 | 2 / 2.6 | 18000 | `pdw_burst_2` |
| Prowler 全自动 | 13.25 | 0 | — | — / 13.25 | 16 | 同上 | | | | `pdw_auto_2` |
| Nemesis | 18 | 4 | 0.21（0.31 → 0.19，满 0.18） | 0.432 s / 9.3 | 17 | 1.3 / 0.75 | 20 | 2.7 / 3 | 31000 | `burstenergyar` |

| Nemesis 热量字段 | 值 | 来源 |
|---|---|---|
| `heat_per_bullet` | 0.04167（约 24 发满） | `mp_weapon_nemesis.txt:24` |
| `heat_decay_delay` / `heat_decay_time` | 8 / 8 s | `:22-23` |
| `heat_mod_var0_start` / `_end` | 0.31 / 0.19 | `:30-31` |

## 5. 未解决和要实测的

- **Nemesis 爬升曲线**：按住连打 30 发，记录每组之间的时间，和第 2 节公式比（SDK 重写，可能和 S21 不同）。同时看客户端和服务端是否对得上。
- **Hemlok 点射周期**：验证 0.444 s。见 W-FIRE-RELOAD 第 5 节。
- **Elite 爆破弹**：伤害 38 和半径实测（打 `npc_dummie`）。

## 6. HSD 实现

**未实现。** 建议：点射放进 `FiringCycle`；热量做成通用组件 `HeatDriver`（状态值 + 字段插值），Nemesis 和 Devotion 共用。实测曲线和 S21 字段不一致时写进 `R5-DIFF-ARCHIVE.md`。替代开火挂到 `Throw.cs` 投掷物。
