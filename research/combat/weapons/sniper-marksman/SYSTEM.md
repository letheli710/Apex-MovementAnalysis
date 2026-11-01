# 狙击 / 精确射手：系统记录

会话 wp1，2026-11-01，静态研究（只读脚本和数据，没进游戏）。出处从 `research-src/s21-platform/scripts/` 开始。`.nut` 在 `vscripts/weapons/`，`.txt` 在 `weapons/`，`wu` = `vscripts/weapons/_weapon_utility.nut`。参数全表：[PARAMS.md](PARAMS.md)。

## 0. 概要

- **武器**：Kraber `mp_weapon_sniper`、Longbow `mp_weapon_dmr`、Sentinel `mp_weapon_sentinel`、G7 Scout `mp_weapon_g2`、Wingman `mp_weapon_wingman`、Charge Rifle `mp_weapon_defender`。Vantage 的枪见 [vantage-sniper-weapon](../vantage-sniper-weapon/SYSTEM.md)。
- **一句话**：单发高伤。**"狙击衰减"不靠伤害字段**：三段伤害值相同（Charge Rifle 例外，越远越高），靠爆头距离、下坠和极大的腰射扩散。特色系统是 Sentinel 的**节奏射击**（Marksman's Tempo）和蓄力开火门槛。
- **分类**：效果（高伤点杀）＋ 系统（节奏射击、拉栓、蓄力门槛、弹匣外备弹）。
- **可拆出的部件**：
  - 节奏射击 → 3.1 `MarksmansTempo_*`
  - 蓄力门槛（回调返回 0）→ 3.2
  - 拉栓 → 3.3
  - 消耗物品强化（Sentinel energize）→ 3.4
  - 弹种重设（G7 双发）→ 3.5

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 开火 | Sentinel、Charge Rifle、G7 脚本调 `FireWeapon_Default`；Kraber、Longbow、Wingman 的 `.txt` 没绑 `OnWeaponPrimaryAttack`（grep） | `mp_weapon_sentinel.nut:113`、`mp_weapon_defender.nut:64`、`mp_weapon_g2.nut:28` |
| 拉栓 | `rechamber_time`（Kraber 1.6、Sentinel 1.6） | `.txt` |
| 节奏射击 | 脚本 mod：`marksmans_tempo_active`、`marksmans_tempo_buildup`；状态存 `SetScriptInt1 / SetScriptTime1` | `wu:214-240`；`mp_weapon_sentinel.txt:181-186`、`:433-440` |
| 蓄力门槛 | `GetWeaponChargeFraction() < 1.0` 返回 0；`charge_time 0.85`、`charge_require_input 1` | `mp_weapon_defender.nut`、`mp_weapon_defender.txt:80-86` |
| Sentinel 强化 | `has_energized 1`，消耗小电池 `health_pickup_combo_small`，mod `energized` 伤害 88 | `mp_weapon_sentinel.txt:25-27`、`:446-453` |
| 开镜特效 | `IsOwnerViewPlayerFullyADSed` 时不播枪口烟 | `mp_weapon_dmr.nut`、`mp_weapon_sniper.nut:44` |
| 反弹 | `projectile_ricochet_max_count` + 碰撞计数 | `mp_weapon_sniper.nut:97-104` |
| 彩蛋 mod | Kraber `4d_ult` 转去调 Flatline 开火 | `mp_weapon_sniper.nut:72-73` |

**混合构建**：

- Sentinel energize：S3 引擎没有，SDK 重写（`s21-r5sdk/src/game/server/energize.cpp`，`sdk_energize_bridge` 默认 1；[W-S3-FIELD-CHECK](../_shared/W-S3-FIELD-CHECK.md)）。`sentinel_use_energize` playlist 默认开（`mp_weapon_sentinel.nut:7`、`:74`）。要实测。
- 节奏射击：`marksmans_tempo_*` 两个引擎都不认，全靠脚本读，`MarksmansTempo_*` 不依赖 S21 引擎。推断能跑。但 `mp_weapon_sentinel.nut:74-75` 关掉 energize 时会提前 return，顺序在节奏射击之后。
-

## 2. 流程

### Sentinel 节奏射击

```
每发（MarksmansTempo_OnFire，wu）：
  去 buildup；中止淡出线程
  graceTime = 已激活 ? 1.25 : 1.0
  now ≤ 完美时刻 + graceTime：
      shots = min(shots + 1, required)
      shots ≥ required → 加 active（rechamber_time 1.25）
      否则加 buildup
  否则：清空

完美时刻（mp_weapon_sentinel.nut:132-135）=
  now + 1 / fire_rate + rechamber_time × (50 / 63)
```

"50 / 63"就是拉栓动画里可以开火的帧（`mp_weapon_sentinel.nut:14`）。

### Charge Rifle

```
按住 → 充能 0.85 s → charge = 1 → 开火（回调放行，FireWeapon_Default）
没充满 → 回调返回 0，不扣弹不发射
松手冷却 1.1 s
```

## 3. 代码

### 3.1 节奏射击（`wu`，`MarksmansTempo_OnFire` 等）

设置结构 `MarksmansTempoSettings`（`wu:214`）：`requiredShots`、`graceTimeBuildup`、`graceTimeInTempo`、`fadeoffMatchGraceTime`、`fadeoffOnPerfectMomentHit`、`fadeoffOnFire`。Sentinel 在 `OnWeaponActivate` 里读 `.txt`（`mp_weapon_sentinel.nut:61-69`）。

**HSD 可借**：节奏连击。可以直接用在 PvE 的"连续命中加速"玩法上。

### 3.2 开火门槛

`OnWeaponPrimaryAttack_weapon_defender_railgun`（`mp_weapon_defender.nut`）：

```
if chargeFraction < 1: return 0
return FireDefender(...)      // FireWeapon_Default + ammo_per_shot
```

### 3.3 拉栓

引擎按 `rechamber_time` 卡下一发。Sentinel 把 RUI 进度放在 `DisplayRechamberRui`（`mp_weapon_sentinel.nut:149` 起）。`disable_zoomed_rechamber` 字段让部分枪开镜不能拉栓（只有部分武器有）。

### 3.4 Energize（设计）

靠近武器长按、消耗一个小电池 → `energized` mod → 伤害 70 → 88，持续 `energized_duration` 150 s，每发消耗 `energized_time_consumed_per_shot` 14 s（`mp_weapon_sentinel.txt:45-46`）。Rampage 用同一套（[charge-spinup](../charge-spinup/SYSTEM.md)）。

### 3.5 G7 双发

`hopup_double_tap` / `altfire_double_tap`：`fire_rate 15`、`burst_fire_count 2`、`burst_fire_delay 0.4`、`viewkick_pattern g2_double_tap`（`mp_weapon_g2.txt:378-382`）。还有一个 mod `fire_rate *1.2`（`:905`）。金马钩子 `GoldenHorsePurple_*`（`mp_weapon_g2.nut`）。

## 4. 参数

**全部参数看 [PARAMS.md](PARAMS.md)。**

| 枪 | `fire_rate` | `damage_near_value` | 爆头 / 腿 | `headshot_distance` | 弹匣 | 换弹 / 空换 | 拉栓 | 弹速 | 重力 | `zoom_time_in` |
|---|---|---|---|---|---|---|---|---|---|---|
| Kraber | 1.2 | 150 | 1.4 / 0.8 | 29528 | 4 | 3.2 / 4.3 | 1.6 | 29500 | 1.4 | 0.58 |
| Longbow | 1.3 | 60 | 1.8 / 0.8 | 29528 | 6 | 2.66 / 3.66 | — | 31000 | 1.3 | 0.31 |
| Sentinel | 3.1 | 70（充能 88） | 1.8 / 0.9 | 29528 | 4 | 3 / 4 | 1.6（节奏 1.25） | 31000 | 1.4 | 0.31 |
| G7 Scout | 4.1 | 33 | 1.45 / 0.75 | 17716 | 10 | 2.4 / 3 | — | 29000 | 1.4 | 0.32 |
| Wingman | 2.8 | 50 | 1.5 / 0.9 | 10000 | 5 | 2.1 / 2.1 | — | 18000 | 1.2 | 0.18 |
| Charge Rifle | 1.3 | 75 近 → 99 远 | 1.8 / 0.9 | 29528 | 6 | 3.5 / 4.6 | — | 33999 | 1.15 | 0.2 |

腰射扩散：Kraber、Longbow、Sentinel 基础 8°（`spread_stand_hip`）、开镜 0；Wingman 2.4°、每发 +2.5°。Kraber 补给箱：伤害 200、备弹 40（`mp_weapon_sniper.txt:367-369`）。Kraber 弹药不走弹药池（`uses_ammo_pool 0`，`mp_weapon_sniper.txt:66`），备弹 `ammo_stockpile_max 8`。

| 节奏射击字段（Sentinel） | 值 | 来源 |
|---|---|---|
| `marksmans_tempo_required_shots` | 1 | `mp_weapon_sentinel.txt:181` |
| `marksmans_tempo_grace_time` | 1.0 s | `:182` |
| `marksmans_tempo_grace_time_in_tempo` | 1.25 s | `:183` |
| `marksmans_tempo_fadeoff_on_perfect_moment` | 0.5 s | `:185` |

## 5. 未解决和要实测的

- **Sentinel 强化（SDK 重写）**：按键消耗小电池，看是否进入强化、伤害是否 88、每发是否扣 14 s。
- **节奏射击**：踩点连开，读 `rechamber_time` 是否变 1.25。
- **Charge Rifle 伤害曲线**：实测 2000 / 4000 / 8000 u。
- **Kraber 对 NPC 打头**：dummie 倍数（W-DAMAGE 第 5 节）。

## 6. HSD 实现

**未实现。** 建议：单发枪走数据表；节奏射击做成 `TempoTracker`（独立组件，给 Sentinel 也给 HSD 自己的武器）；蓄力门槛和 `FiringCycle` 的"返回 0 不扣弹"一起。Energize 按 S21 设计做 mod，消耗物走道具阶段的使用流程。差异进 `R5-DIFF-ARCHIVE.md`。
