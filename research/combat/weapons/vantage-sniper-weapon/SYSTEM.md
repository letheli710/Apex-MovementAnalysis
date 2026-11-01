# Vantage 大招狙击枪（只看枪）：系统记录

武器阶段 W1，2026-11-01，静态研究（只读脚本，没进游戏）。这里只写枪：伤害、下坠、弹量、倍镜、和 Kraber / Sentinel 比。标记、增伤、擦过、激光时机看 [`../../vantage-snipers-mark/SYSTEM.md`](../../vantage-snipers-mark/SYSTEM.md)。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_ability_sniper_ult.nut`，`txt` = `weapons/mp_ability_sniper_ult.txt`，`kr` = `weapons/mp_weapon_sniper.txt`（Kraber），`se` = `weapons/mp_weapon_sentinel.txt`。

逐字段全表：[`PARAMS.md`](PARAMS.md)。Kraber、Sentinel 的全表：`../sniper-marksman/PARAMS.md`。

## 0. 概要

- **武器**：Vantage / 大招槽 / `mp_ability_sniper_ult`。
- **一句话**：大招槽里的栓动狙，50 伤害（爆头 ×1.5），子弹 34000 u/s，弹匣按"大招能量"算，每发 40，1/s 回充。单发伤害比 Sentinel 低，靠标记 ×2.5 补上。
- **分类**：
  - 效果：高弹速狙击 + 击中标记（标记在主记录）。
  - 可视化：两档倍镜、敌方能看到的反光。
  - 可复用系统：弹量 = 技能能量（`cooldown_type ammo`）的枪；子弹命中体积随飞行时间变大。
- **可拆出的部件**：
  - 技能能量当弹药 → 3.2.1
  - 随飞行时间变大的命中体积 → 3.2.2
  - 没有下坠字段时的弹道 → 3.2.3
  - 两档倍镜 → 3.2.4

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 大招槽当主武器拿 | `fire_mode offhandHybrid` + `offhand_active_slot mainHand` | `txt:8`、`txt:12` |
| 能量当弹药 | `cooldown_type ammo`，回充 `regen_ammo_refill_rate 1` | `txt:68`、`txt:50` |
| 子弹 | `FireBallisticRoundWithDrop` | `nut:309` |
| 扣弹 | `ammoUsed = GetAmmoPerShot()`，`return ammoUsed` | `nut:296`、`nut:330` |
| 枪栓 | `rechamber_time 1.2` | `txt:70` |
| 两档倍镜 | `zoom_fov` + `zoom_toggle_fov`，0.3 s 过渡 | `txt:238-240` |
| 反光 | 武器 targeting laser（3P 特效） | `txt:207-216` |

**S3 / S21 差异**（见 [`../_shared/W-S3-FIELD-CHECK.md`](../_shared/W-S3-FIELD-CHECK.md)，字符串证据）：

字段核对只搜了 exe；SDK 的 `server.dll` 另有实现（源码 `research-src/s21-r5sdk/src/game/`），所以"exe 里没有"不等于"dedi 上不工作"。下面引用 SDK 源码的地方是读过的；行为都待实测。

- `txt:32`：`OnWeaponZoomFOVToggle` 注释 "Disabled on dedi"，所以 `OnWeaponZoomFOVToggle_ability_sniper_ult`（`nut:251-268`，切倍镜音效）这个回调不绑定。推断切倍镜没有音效；缩放本身是字段，不受影响。
- `targeting_laser_*`：exe 只有客户端有；SDK 做了名字映射（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3249-3250`），客户端另有处理（`research-src/s21-r5sdk/src/game/client/pred_authority.cpp:3070`）。反光表现待实测，第 5 节第 3 条。
- `ads_force_firstperson`（`txt:251`）：SDK 名字映射（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3176`）。
- `offhand_restore_after_melee`（`txt:11`）：SDK 预留槽 `custom_bool_3`（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3082`），脚本只在 `#if CLIENT` 里读（`vscripts/melee/sh_melee.gnut:1321-1324`）。
- `vantage_s25_1_buffs_enabled` 说明脚本混入了比 S21 新的逻辑（主记录已写）。

## 2. 流程

枪部分（标记流程看主记录）：

```
按大招（弹量 ≥ 40）→ deploy 1.1 s
开镜 0.5 s → zoom_fov 19.86（窄档 10.0，0.3 s）
开枪：扣 40；子弹 34000 u/s；拉栓 1.2 s
弹量每秒 +1，40 s 回一发
收起 0.4 s（holster）；近战可打断，`offhand_restore_after_melee` 让它结束后恢复（txt:11）
```

弹量（推断，要测）：`ammo_clip_size 240` ÷ 40 = 满 6 发；`ammo_default_total 40` 是起始总量；`ammo_stockpile_max 200`（`txt:45`）和 `ammo_no_remove_from_stockpile 1`（`txt:48`）的语义不清楚。满 6 发要 240 s。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_ability_sniper_ult`（`txt:28` 绑定，`nut:296-330`）。

### 3.2 核心逻辑

#### 3.2.1 能量弹药

```
ammoUsed = GetAmmoPerShot()   // 40
if 满弹匣: PlayerUsedOffhand   // 记作用了大招（nut:298-301）
生成子弹
return ammoUsed
```

对比 Sheila：Sheila `ammo_per_shot 43` 但脚本返回 1；这里脚本返回的就是 `ammo_per_shot`。同一种字段两种用法，抄的时候看返回值（`../rampart-sheila-weapon/SYSTEM.md` 3.2.3）。

#### 3.2.2 命中体积

`bolt_hitsize 1` → 0.04 s 变 5 → 0.1 s 变 7 → 0.16 s 内到 10（`txt:198-204`）。Kraber、Sentinel 最终只有 2（`kr:59`、`se:71`）。按 34000 u/s，0.16 s 飞了 5440 u（推断）。大招枪容错是别的狙的 5 倍（半径单位是推断）。

#### 3.2.3 下坠

`txt` 里**没有** `projectile_gravity_scale`、`bolt_gravity_enabled`、`projectile_drag_coefficient`（grep 只命中 `txt:412` 的 UI 绑定 `boltZeroDistance`）。Kraber 和 Sentinel 都写了 `bolt_gravity_enabled 1` + `projectile_gravity_scale 1.4`（`kr:200-201`、`se:239-240`）。

所以这把枪用的是引擎默认值，默认值脚本里看不到（推断）。主记录说"有下坠"的依据只是函数名 `FireBallisticRoundWithDrop`（`nut:309`）。

估算（**推断**，假设 g = 750 u/s²、不算阻力、默认 scale = 1）：`drop = 0.5 × g × scale × (d / v)²`。

| 距离 | 大招枪（34000，scale 1） | Kraber（29500，scale 1.4） | Sentinel（31000，scale 1.4） |
|---|---|---|---|
| 3000 u | 3 u | 5 u | 5 u |
| 7500 u | 18 u | 34 u | 31 u |

#### 3.2.4 倍镜

`zoom_fov 19.86`、`zoom_toggle_fov 10.0`（`txt:238-239`）；Kraber 13.31 / 8.01（`kr:24-25`）；Sentinel 基础 55，倍镜靠配件（`se:215`）。大招枪两档都自带，没有配件槽。

### 3.3 客户端表现

反光、背上的枪：看主记录 3.3。

### 3.4 依赖的公共代码

- `../_shared/W-BALLISTICS.md`、`../_shared/W-DAMAGE.md`、`../_shared/W-FIRE-RELOAD.md`。
- 标记增伤：`../../_shared/C-DAMAGE-MODIFIERS.md`。

## 4. 参数

| 字段 | 大招枪 | Kraber | Sentinel |
|---|---|---|---|
| `damage_near_value` | 50（`txt:182`） | 150（`kr:37`） | 70（`se:58`） |
| `damage_very_far_value` | 50（`txt:184`） | 150（`kr:39`） | 70（`se:60`） |
| `damage_headshot_scale` | 1.5（`txt:192`） | 1.4（`kr:47`） | 1.8（`se:227`） |
| 爆头（推断） | 75 | 210 | 126 |
| 被标记 ×2.5（`nut`，主记录） | 125 | 不适用 | 不适用 |
| 被标记爆头（推断，顺序要测） | 187.5 | 不适用 | 不适用 |
| Sentinel 充能 `damage_very_far_value` | 不适用 | 不适用 | 88（`se:450`） |
| `fire_rate` | 3（`txt:56`） | 1.2（`kr:19`） | 3.1（`se:49`） |
| `rechamber_time` | 1.2（`txt:70`） | 1.6（`kr:77`） | 1.6（`se:98`） |
| `projectile_launch_speed` | 34000（`txt:197`） | 29500（`kr:53`） | 31000（`se:64`） |
| `projectile_gravity_scale` | 没写 | 1.4（`kr:201`） | 1.4（`se:240`） |
| `projectile_drag_coefficient` | 没写 | 0.0033（`kr:199`） | 0（`se:65`） |
| `bolt_hitsize_growfinal_size` | 10（`txt:204`） | 2（`kr:59`） | 2（`se:71`） |
| `ammo_clip_size` | 240 = 6 发（`txt:41`） | 4（`kr:60`） | 4（`se:79`） |
| `ammo_per_shot` | 40（`txt:44`） | 没写 | 1（`se:83`） |
| `regen_ammo_refill_rate` | 1（`txt:50`） | 无 | 无 |
| `reload_enabled` | 0（`txt:62`） | 换弹 3.2 s（`kr:68`） | 换弹 3.0 s（`se:92`） |
| `zoom_time_in` | 0.5（`txt:254`） | 0.58（`kr:22`） | 0.31（`se:51`） |
| `impulse_force` | 5000（`txt:69`） | 4000（`kr:20`） | 4000（`se:50`） |
| `damage_flags` | DF_SNIPER、BULLET、KNOCK_BACK（`txt:193`） | 同左 + DF_GIB（`kr:44`） | 同大招枪（`se:235`） |
| `headshot_distance` | 29528（`txt:191`） | 29528（`kr:191`） | 29528（`se:226`） |

读法：三把都不随距离衰减。大招枪胜在弹速、命中体积、不用换弹和拉栓短。单枪 50 不高，对 HSD 的 AI 来说要配标记才值。

调参：`ammo_per_shot` 决定能打几发、多久回一发；`bolt_hitsize_growfinal_size` 决定容错；`rechamber_time` 决定节奏。

## 5. 未解决和要实测的

1. **下坠和默认重力**。`txt` 没写 gravity 字段，推断用引擎默认值。测：火力训练场开枪打 3000 / 7500 u 外的靶，准星对靶心，量落点高度差，和 Kraber 比。
2. **实际发数和起始弹量**。`ammo_clip_size 240`、`ammo_default_total 40`、`ammo_stockpile_max 200` 的语义不清。测：满能量连开，记发数；刚开局看能开几发。
3. **`targeting_laser_*`（SDK 名字映射）**：dedi 上反光对敌方是否可见、`SetTargetingLaserEnabled`（`nut:139`）是否有效。测：两个客户端，一个开镜，看另一个能不能看到反光。单机时用第三人称看自己。
4. **拉栓和射速的关系**。`fire_rate 3` + `rechamber_time 1.2`，推断实际间隔是 max(1/3, 1.2)，也可能相加。Kraber 同问题。测：连按开火，读两发间隔。
5. **标记 ×2.5 和爆头 ×1.5 的顺序**：伤害回调拿到的是否已含爆头。测：标记后打头，读实际伤害。
6. **切倍镜音效**：`txt:32` 被关，确认没声音、FOV 正常切换。

## 6. HSD 实现

**未实现**。现有：`Combat/Weapons.cs` 里 `Weapon` 基类和 `TestRifle`；伤害修正链在分支 `origin/claude/w2-framework-b44e35` 的 `DamageModifiers.cs`（有 `IDamageModifier`、`MarkAmp`），标记增伤应该复用，不重写。HSD 现在的子弹是 `TraceBullet` 即时射线（`Weapons.cs` `Shoot`），没有飞行时间。

建议做法：

1. 新建 `VantageSniper : Weapon`，弹量字段和大招充能共用，`perShot = 40`、`maxAmmo = 240`、`regen = 1/s`。
2. 子弹：要下坠就走公共弹道（`../_shared/W-BALLISTICS.md`）；先用 34000 u/s、scale 1。这项和 R5 的差别（默认重力是假设）进 `R5-DIFF-ARCHIVE.md`。
3. 命中体积：按飞行时间插值半径（1 → 5 → 7 → 10）。
4. 命中时加 `MarkAmp`（分支里已有），倍数 2.5。

开关建议：`hsd.combat.vantage.sniper.gravityScale`、`hitsizeFinal`。
