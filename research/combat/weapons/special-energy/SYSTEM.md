# 特殊能量武器：系统记录

武器阶段 W1，2026-11-01，静态研究（只读脚本，没进游戏）。按"可复用的部件"分组，不按枪分。

出处从 `research-src/s21-platform/scripts/` 开始。`stub` = `vscripts/weapons/_missing_callback_stubs.gnut`，`bu` = `weapons/mp_weapon_buster_rifle.txt`，`rg` = `weapons/mp_weapon_raygun.txt`，`rgn` = `vscripts/weapons/mp_weapon_raygun.nut`，`ig` = `weapons/mp_weapon_instagib.txt`，`cw` = `vscripts/weapons/mp_weapon_clickweapon.nut`，`igm` = `vscripts/gamemodes/fs_instagib/_gamemode_instagib.nut`，`ep` = `weapons/mp_weapon_epg.txt`，`ept` = `weapons/mp_weapon_epg_tethered.txt`，`cg` = `weapons/mp_weapon_charge_gauntlet.txt`，`cgn` = `vscripts/weapons/mp_weapon_charge_gauntlet.nut`，`ab` = `weapons/mp_weapon_arc_bolt.txt`，`abn` = `vscripts/weapons/mp_weapon_arc_bolt.nut`，`aw` = `weapons/mp_weapon_arc_wave.txt`，`ac` = `vscripts/weapons/_arc_cannon.nut`，`bl` = `vscripts/weapons/_ball_lightning.gnut`，`set` = `vscripts/_settings.nut`，`ds` = `weapons/mp_weapon_defender_sustained.txt`，`loot` = `datatable/survival_loot.csv`（从 `research-src/s21-platform/` 开始）。

逐字段全表：[`PARAMS.md`](PARAMS.md)。

## 0. 概要

- **武器**：Buster Rifle、Ray Gun、Instagib、EPG、EPG Tethered、Charge Gauntlet、Arc Bolt、Arc Wave、Defender Sustained，加两个脚本库 `_arc_cannon`、`_ball_lightning`。
- **一句话**：大部分是"数据还在、脚本没了"。真正能开枪的只有 Ray Gun、Instagib、Charge Gauntlet、Arc Bolt。但四种机制（慢速等离子球、爆炸投射物、电弧链、持续光束）都留下了足够的数值和代码，HSD 可以照着做。
- **分类**：
  - 效果：慢速大球（Ray Gun）、电弧链（`_arc_cannon`）对 PvE 成群的敌人值得做。
  - 可视化：Ray Gun 的环形弹体、Instagib 的光束。
  - 可复用系统：见下面四组。
- **可拆出的部件**：
  - 慢速等离子球 → 3.2.1（Ray Gun）
  - 爆炸投射物 → 3.2.2（EPG 数值）
  - 电弧链 → 3.2.3（`_arc_cannon`）
  - 持续范围电击 → 3.2.4（`_ball_lightning`）
  - 持续光束 → 3.2.5（Defender Sustained 数值）
  - 即时射线 + 光束表现 → 3.2.6（Instagib）

### 能不能用（本地）

"脚本"看有没有实现；"空壳"指回调在 `stub` 里（`stub:255` 打印 "[WEAPON-STUB] ... is not implemented in this build" 后返回 0，所以按开火不出弹）。模型是否在本地包里，静态读不了 rpak，除了注释明确写的 EPG，都没验证，第 5 节第 1 条。

| 武器 | 脚本 | loot 表 | 结论 |
|---|---|---|---|
| Buster Rifle | **空壳**（`stub:264`、`stub:285`、`stub:291`），全部回调都是；`vscripts/scripts.rson` 没有它的 `.nut` | 注释掉（`loot:435`："removed in S30, kept so nothing dangles"） | 不能开火 |
| Ray Gun | 有（`rgn`），Flowstate 移植（`rgn:1`："Flowstate raygun fire path (Cafe port)"） | `survival_loot.csv` 没有；`datatable/flowstate_mods.csv:2` 有，但读取代码被注释（`vscripts/sh_survival_loot_all.gnut:441-446`："Parked"） | 脚本能跑；只能 give，不能靠 loot（推断） |
| Instagib | 有（`cw`），Flowstate 写的 | 有（`loot:432-433`，isDisabled false） | 只在 `fs_instagib` 模式注册（`cw:35`） |
| EPG、EPG Tethered | **空壳**（`stub:1037`、`stub:1396`） | 注释掉（`loot:168-169`："mdl/weapons/epg is absent and S21 has no mdl/error.rmdl to fall back on"） | 不能用，模型也没有 |
| Charge Gauntlet | 有（`cgn`） | 大招武器，不走地面 | Sparrow 大招，能跑；角色是否在本地可选没查 |
| Arc Bolt | 有（`abn`） | 技能 | Ash 战术，能跑 |
| Arc Wave | **空壳**（`stub:407`、`stub:995`） | 没有 | 不能用 |
| Defender Sustained | **空壳**（`stub:344`、`stub:1031`） | 没有 | 不能用；`vscripts/weapons/mp_weapon_defender.nut` 是 railgun，不是这把 |
| `_arc_cannon` | 代码完整，`vscripts/_utility_shared.nut:210` 只调 `ArcCannon_Init` | 无 | **vscripts 里没有武器调用 `FireArcCannon`**（grep），死代码 |
| `_ball_lightning` | 代码完整，`vscripts/_utility_shared.nut:435` 只调 `BallLightning_Init` | 无 | **没有武器调用**（grep），死代码 |

### Buster Rifle 是真 hitscan 吗

- `bu:58` 写 `ballistic_type hitscan`。全部 `weapons/*.txt` 里只有两个文件有这个字段：`bu:58` 和 `weapons/mp_weapon_shotgun_pistol_energy.txt:8`。
- **脚本在哪**：没有。`BusterRifle_OnWeaponPrimaryAttack` 是 `stub:285` 的空壳，返回 0。S21 的实现已经被删掉。所以它不开枪，`ballistic_type` 这个字段的效果在本地看不到。
- 同时字段还留着弹速 29500、重力 1.4（`bu:173`、`bu:263`）——这份数据是从 Kraber 抄的（推断：字段值和 `mp_weapon_sniper.txt` 相同），不能证明 hitscan 时这些有没有作用。
- **本地真正 hitscan 的是 Instagib**：`cw:404` 直接 `weapon.FireWeaponBullet`（`cw:1` 注释 "Instagib hitscan rail"）。另外 `FireWeaponBullet` 还用在 `mp_weapon_alternator_smg.nut`、`mp_weapon_energy_ar.nut`、`_vortex.nut`、`sh_smart_ammo.gnut`、`_arc_cannon.nut`。

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 慢速球 | `FireWeaponBoltAndReturnEntity`，字段弹速 2200、无重力、`bolt_hitsize 10` | `rgn:64`、`rg:101`、`rg:163`、`rg:250` |
| 球的外观 | 服务端 `CreatePropDynamic` 两个环模型，绑到子弹上；拖尾粒子 | `rgn:69-85` |
| 爆炸投射物 | 字段 `explosion_damage`、`explosionradius` + `projectile`；脚本空壳 | `ep:77-81`、`stub:1396` |
| 电弧链 | 递归线程 `ZapTargetRecursive`，已打过的进表 | `ac:402-446` |
| 持续范围电击 | 跟随 mover + 每 0.4 s `RadiusDamage` | `bl:130-179`、`set:468` |
| 持续光束 | 引擎 `sustained_discharge_*` + `sustained_laser_*` 字段 | `ds:63-82` |
| 瞬时射线 | `FireWeaponBullet` | `cw:404` |
| Instagib 一枪死 | 模式层 `AddEntityCallback_OnDamaged`，伤害改 9999 | `igm:270-294` |
| 充能箭 | `ThrowDeployable` | `cgn:76` |

**S3 / S21 差异**（字符串证据，见 [`../_shared/W-S3-FIELD-CHECK.md`](../_shared/W-S3-FIELD-CHECK.md)）：

字段核对只搜了 exe；SDK 的 `server.dll` 另有实现（源码 `research-src/s21-r5sdk/src/game/`），所以"exe 里没有"不等于"dedi 上不工作"。下面引用 SDK 源码的地方是读过的；行为都待实测。

- **Charge Gauntlet 用了分段重力和空气阻力**：`projectile_gravity_scale_2 1.5`、`_final 2.0`、`projectile_air_friction_2 3000`、`_final 6000`（`cg:71-76`）。exe 只有客户端有；SDK 读这些键（`research-src/s21-r5sdk/src/game/server/weapon_kv_s21_ext.cpp:161-174`），但 grep `flGravityScale2`、`flAirFriction2`、`flGravityScaleFinal` 在这个文件之外没有使用者。落点是否一致待实测，第 5 节第 3 条。
- Charge Gauntlet 的 `charge_curve_coefficients`（`cg:115`）、`charge_allow_hold_when_full`（`cg:108`）、`charge_attack_min_charge_required`（`cg:110`）：exe 只有客户端有；SDK 解析它们（`research-src/s21-r5sdk/src/game/shared/weapon_heat.cpp:402-416`），后两个有开关 `bridge_charge_hold_when_full`、`bridge_charge_min_required`（同文件 `:51-59`）。
- Arc Bolt 的 `grenade_drop_*`：exe 只有客户端有，SDK 没查；`shock_damage`（`ab:60`）两个引擎都不认，脚本读（`abn:238`）。
- `sustained_discharge_*` 和 `sustained_laser_range` 两个二进制都认。所以持续光束的引擎底子在 dedi 上有（行为要测）。Defender Sustained 不能用是因为回调空壳，不是引擎不支持。
- 可能重要的：`stub` 这个文件本身就是"按 S3 / S21 分别写"的补丁（文件头注释："A few callbacks take different arguments on the two engines"）。
- Arc Bolt：`abn` 里的 `SetConVarFloat( "tether_*" )` 大多被注释，只留 `tether_maxvel`（`abn:220-227`），详见 `../../ash-arc-snare/SYSTEM.md`。

## 2. 流程

各武器差异大，这里只写能跑的和机制本身。

```
Ray Gun：开火 → 发声 → FireWeaponBolt（speed 参数 1，弹速由字段）→ 服务端绑模型和拖尾 → 碰撞走引擎 → return 1
Instagib：开火 → 防抖 0.35 s → FireWeaponBullet → 模式层把伤害改 9999；光束在客户端按射线画 0.45 s
电弧链：开火 → GetFirstArcCannonTarget（锥 2°，距离 = damage far）→ 有目标才链，没目标放空
         ZapTarget → 伤害 → EMP → 找 400 u 内的下一个 → 每跳 ×0.75（最多 5 跳，NPC 2 跳）
球形闪电：挂到投射物 / prop → 每 0.4 s RadiusDamage → 伤害回调里判有效 → 画连接电弧
持续光束（数据）：开火 → 1.25 s 内每 0.104 s 一跳 → 最后一发进入 primary attack
```

## 3. 代码

### 3.1 入口

- `OnWeaponPrimaryAttack_RayGun`（`rgn:33`），NPC 版 `OnWeaponNpcPrimaryAttack_RayGun`（`rgn:39`）；`MpWeaponRayGun_Init`（`rgn:16`）。
- `OnWeaponPrimaryAttack_Clickweapon`（`cw:354`），`Clickweapon_Init`（`cw:33`）。
- `FireArcCannon`（`ac:199`）。
- `CreateBallLightning`（`bl:71`）、`AttachBallLightning`（`bl:31`）。

### 3.2 核心逻辑

#### 3.2.1 慢速等离子球（Ray Gun）

`FireRayGun`（`rgn:45-90`）：

```
FireWeaponBoltAndReturnEntity( pos, dir, speed = 1 )
服务端：给子弹加拖尾 P_skydive_trail_CP（颜色 89 255 136，1 s 后关）
        两个 prop 绑到子弹：环 ar_marker_ringwobble、核 energy_ring_core_fx，缩放 0.3
return 1
```

`speed = 1` 推断是比例，真实弹速看 `rg:101` 的 2200（其他枪的调用也传 1）。特点：慢（2200 u/s）、直（`projectile_gravity_scale 0`、`bolt_gravity_enabled 0`）、大（`bolt_hitsize 10`）、**没有爆炸**。一枪 90、爆头 ×2.15（`rg:53`、`rg:60`），3 发/s（`rg:88`）。

HSD 现在的 `PlasmaBolt`（`Boosts.cs`）已经是同一类东西。

#### 3.2.2 爆炸投射物（EPG 数值）

脚本是空壳，只有数：直击 40、爆炸 65、内半径 52、外半径 180、弹速 2000、无重力（`ep:69`、`ep:81`、`ep:77-78`、`ep:87-88`），0.9 发/s（`ep:110`）。4 发一匣（`ep:61`）。没有爆头（`ep:111`）。

`ept` 是同一份数据改弹量：3 发一匣、备弹 6（`ept:4-8`）。没有 tether 相关字段，脚本也不存在（`ept:28` 指向同一个空壳），"tethered" 的行为查不到。

Power Sword 的投射物（`weapons/mp_weapon_power_sword.txt:155`、`:158`，半径 180、爆炸 45）用同一模板。

`jump_kit` mod（`ep:395`）：`impulse_force_explosions 65000`。名字看是火箭跳用的，对 HSD 的火箭跳话题有参考（推断）。

`npc_damage_near_value 99`（`ep:324`）是泰坦世界观遗留（推断）。

#### 3.2.3 电弧链（`_arc_cannon`）

选第一个目标（`ac:225` 起）：锥角 2°（`ac:230`），距离 `GetMaxDamageFarDist`（`ac:228`）。

```
FireArcWithTargets（ac:356-400）：
  半径、宽度按充能插值
  maxChains：玩家 = Graph( 充能, 0, 1, 5, 5 )；NPC = 2；burn mod 100 / 10
  zappedTargets 表防重复

ZapTargetRecursive（ac:402-446）：
  chainNum > maxChains → return
  等 ZapTarget 完
  找 ARC_CANNON_RANGE_CHAIN 内的其他目标（泰坦 900）
  每个新目标 chainNum + 1（打导弹不加），thread 递归

ZapTarget（ac:453）：
  伤害 = 按充能或距离插值（ac:543-554）
  伤害 × 0.75^( chainNum − 1 )（ac:556-559）
  > 0 时给 EMP，时长 0.1–1.8 s（ac:567）
```

可复用：链的结构（目标表 + 递归 + 每跳衰减）。这份代码直接给出链的三个数：400 u、5 跳、×0.75。

电和 EMP 的表现看 `../../_shared/B-electric-emp.md`。

#### 3.2.4 持续范围电击（`_ball_lightning`）

```
CreateBallLightning：script mover + BallLightningThink（bl:71-79）
Think：while true：RadiusDamage( 400 u, 对人 8, 对重甲 120 )；wait 0.4（bl:149-160、bl:163-179）
RegisterBallLightningDamage → OnBallLightningDamage：
    IsTargetEntValid 不过 → 伤害改 0
    否则画连接电弧（bl:86-128）
```

`AttachBallLightning` 把它绑在投射物上（`bl:50`），`AttachBallLightningToProp` 绑在 prop 上（`bl:63`）。所以球形闪电 = "挂到任何会动的东西上的光环伤害"。HSD 的 Ray Gun 球 + 这个 = 飞行中持续放电的慢球（TF2 的 Arc Ball 就是这样，推断）。

判定用 `set:474-480`。对人 8 / 0.4 s = 20 DPS（推断）。

#### 3.2.5 持续光束（Defender Sustained 数据）

字段（`ds:63-82`）：`sustained_discharge_duration 1.25`、`sustained_discharge_pulse_frequency 0.104`、`sustained_laser_radius 18`、`sustained_laser_range 19685`、`sustained_discharge_ends_in_primary_attack 1`、`sustained_discharge_require_input 0`。每跳 `damage_near_value 5`（`ds:84`），推断 12 跳 ≈ 60 伤害 + 收尾一发；回调都是空壳（`stub:344`、`stub:1031`）。

引擎路径：`OnWeaponSustainedDischargeBegin` → 引擎每跳打射线（半径 18）→ `OnWeaponSustainedDischargeEnd`。`sustained_laser_use_deferred_traces 0`（`ds:82`）。

`amped_damage` mod 里普遍有 `sustained_laser_damage_scale *0.83333`（`ep:369` 等，几乎所有枪都有），说明这个系统是通用的。

HSD 的 `InfernoBeam` 是另一路（伤害随时间爬升），可以共用光束实现。

#### 3.2.6 Instagib

`cw:354-404`：`OverrideNextAttackTime( now + 0.35 )`（`cw:19-20` 注释：略小于 1/2.8 s，让引擎 `fire_rate` 当上限）；`FireWeaponBullet( pos, dir, 1, flags )`。

光束是客户端自己打射线画的（`cw:234-265`，`P_tesla_trap_link_CP` 两端 mover，停留 0.45 s `cw:21`），敌方玩家走 `ServerCallback_CreatesLaserFXFromServer`（`cw:195`）。

一枪死是模式层改的（`igm:292`），`ig:56` 的 50 只是字段。Rail jump：`LGUN_DoRailJump`（`cw:74-123`），向下看、400 u 内（`cw:22`），冲量 = −视线 × 850 × (1 − 距离比)，走 `KnockBack`（`cw:103-104`）。`ig:205` 移动 ×1.8。

Rail jump 对 HSD 火箭跳话题可以参考，但这是 Flowstate 社区写的，**不是 Respawn 手感**。

### 3.3 客户端表现

- Ray Gun：全在服务端绑 prop，客户端看到的就是 prop（`rgn:66-87`）。
- Charge Gauntlet：落点标记 `ShowUltArrowImpactSpot`（`cgn:122`）。
- `_ball_lightning` 的连接电弧：`BallLightningZapConnectionFX`（`bl:276`）。
- Arc Cannon 光束：`CreateArcCannonBeam`，颜色 `150 190 255`（`ac:47`）。

### 3.4 依赖的公共代码

- `../_shared/W-BALLISTICS.md`、`../_shared/W-DAMAGE.md`、`../_shared/W-FIRE-RELOAD.md`、`../_shared/W-MOD-SYSTEM.md`、`../_shared/W-S3-FIELD-CHECK.md`。
- 电：`../../_shared/B-electric-emp.md`。
- 技能本身：Arc Bolt 看 `../../ash-arc-snare/SYSTEM.md`。Charge Gauntlet 是 Sparrow 大招，`mp_weapon_bow_ult_missile` 的说明看 `../../vantage-snipers-mark/SYSTEM.md` 第 7 节。

## 4. 参数

| 字段 | Buster（空壳） | Ray Gun | Instagib | EPG（空壳） | Charge Gauntlet | Arc Bolt | Defender Sust.（空壳） |
|---|---|---|---|---|---|---|---|
| `damage_near_value` | 60（`bu:92`） | 90（`rg:53`） | 50（`ig:56`） | 40（`ep:69`） | 15（`cg:136`） | 0（`ab:56`） | 5（`ds:84`） |
| `fire_rate` | 5（`bu:67`） | 3（`rg:88`） | 2.8（`ig:90`） | 0.9（`ep:110`） | 1.3（`cg:91`） | 5（`ab:22`） | 1（`ds:48`） |
| `projectile_launch_speed` | 29500（`bu:173`） | 2200（`rg:101`） | 18000（`ig:103`） | 2000（`ep:87`） | 6000（`cg:68`） | 1200（`ab:51`） | 没写 |
| `projectile_gravity_scale` | 1.4（`bu:263`） | 0（`rg:163`） | 1.2（`ig:165`） | 0（`ep:88`） | 0（`cg:69`） | 0（`ab:25`） | 1.4（`ds:232`） |
| `ammo_clip_size` | 4（`bu:59`） | 20（`rg:42`） | 69（`ig:43`） | 4（`ep:61`） | 180（`cg:77`） | 20（`ab:45`） | 4（`ds:41`） |
| `damage_flags` | DF_SNIPER、GIB（`bu:105`） | DF_BULLET、KNOCK_BACK（`rg:14`） | 同左（`ig:14`） | BULLET、GIB、EXPLOSION（`ep:26`） | SNIPER、GIB、KNOCK_BACK（`cg:145`） | RAGDOLL、EXPLOSION、ELECTRICAL（`ab:28`） | GIB（`ds:83`） |

机制专用：

| 参数 | 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| `ARC_CANNON_RANGE_CHAIN` | 400 | u | `ac:25` | 下一跳距离，大了链得开 |
| `ARC_CANNON_CHAIN_COUNT_MAX` | 5 | 跳 | `ac:28` | |
| `ARC_CANNON_CHAIN_COUNT_NPC` | 2 | 跳 | `ac:29` | NPC 用时少 |
| `ARC_CANNON_FORK_COUNT_MAX` | 1 | 分叉 | `ac:30` | 改大变树 |
| `ARC_CANNON_FORK_DELAY` | 0.1 | s | `ac:31` | 每跳延迟 |
| `ARC_CANNON_DAMAGE_FALLOFF_SCALER` | 0.75 | ×/跳 | `ac:62` | |
| `ARC_CANNON_DAMAGE_CHARGE_RATIO` | 0.85 | 比例 | `ac:63` | 满伤需要的充能 |
| `ARC_CANNON_EMP_DURATION_MAX` | 1.8 | s | `ac:54` | |
| `ARC_CANNON_BEAM_LIFETIME` | 0.75 | s | `ac:48` | |
| `BALL_LIGHTNING_BURST_DELAY` | 0.4 | s | `set:468` | 电击间隔 |
| `BALL_LIGHTNING_ZAP_RADIUS` | 400 | u | `set:474` | |
| `BALL_LIGHTNING_ZAP_HUMANSIZE_RADIUS` | 200 | u | `set:475` | 对人的半径 |
| `BALL_LIGHTNING_DAMAGE` | 120 | HP | `set:478` | 重甲 |
| `BALL_LIGHTNING_DAMAGE_TO_PILOTS` | 8 | HP | `set:480` | 人 |
| `sustained_discharge_duration` | 1.25 | s | `ds:63` | |
| `sustained_discharge_pulse_frequency` | 0.104 | s | `ds:64` | 跳间隔 |
| `sustained_laser_radius` | 18 | u | `ds:72` | |
| `sustained_laser_range` | 19685 | u | `ds:73` | |
| `explosion_damage` | 65 | HP | `ep:81` | |
| `explosionradius` | 180 | u | `ep:78` | |
| `explosion_inner_radius` | 52 | u | `ep:77` | |
| `shock_damage` | 10 | HP | `ab:60` | Arc Bolt 电击 |
| `LG_MAX_DISTANCE_RAILJUMP_TRACE` | 400 | u | `cw:22` | rail jump 距离 |

## 5. 未解决和要实测的

1. **模型在不在**。静态只确认了 EPG 没有（`loot:168`）。Buster `mdl/weapons/at_rifle`、Ray Gun `mdl/Weapons/ptpov_raygun`、Defender `mdl/weapons/defender`、Arc Wave `mdl/weapons/bolo_sword`。测：`give` 每一把，看 console。Buster / Defender / Arc Wave 预期出现 `[WEAPON-STUB]`。注意 `S21 没有 mdl/error.rmdl`（`loot:168`），缺模型可能直接报错，先在非主力配置测。
2. **Ray Gun 能否 give、伤害**。`loot` 没这一行，`rgn:1` 注释又要求有这一行。测：`give mp_weapon_raygun`，打假人读 90；量弹速。
3. **Charge Gauntlet 分段重力在 dedi 上的表现**（`cg:71-76`，SDK 读键但没找到使用者）。测：Sparrow 大招打一发，对比客户端落点标记和实际落点。如果差很多就是预测不一致。没有 Sparrow 时跳过。
4. **`FireArcCannon` 能不能借用**。没有武器绑定，需要写自定义武器才能测，优先级低。HSD 直接用常量。
5. **`ballistic_type` 的实际作用**：Buster 不开枪，测不了。`mp_weapon_shotgun_pistol_energy` 也有这个字段（`:8`）但 `OnWeaponActivate_weapon_shotgun_pistol` 是空壳，如果它的开火回调能跑，可以用它测（量命中是否瞬时）。

## 6. HSD 实现

现有（`HSD-Unity/Assets/HSD/Game/Runtime/Combat/`）：

| 机制 | 现状 | 差别 |
|---|---|---|
| 慢速球 | `PlasmaBolt`（`Boosts.cs`）有 | 用在重炮台，不是玩家枪 |
| 持续光束 | `InfernoBeam`（`SpecialWeapons.cs`）：DPS 20 → 200，4 s 爬升 | 和 R5 Defender 机制不同，保留 |
| 电弧链 | 未实现 | `ArcStar`（`Ordnance.cs`）是投掷物 |
| 范围电击 | 未实现 | |
| 爆炸投射物 | `FragGrenade` 等走抛物线 | 没有直线爆炸弹 |

分支 `origin/claude/w2-framework-b44e35`：有 `StatusEffects.cs`、`DamageModifiers.cs`。没有 chain / beam 公共部件。

建议做法：

1. **`Projectile` 基类**（公共，`../_shared/W-BALLISTICS.md`）：速度、重力、半径、寿命、碰撞回调。`PlasmaBolt`、Ray Gun、EPG 都基于它，爆炸是一个可选组件。
2. **`ArcChain` 工具类**：`Fire( first, range = 400, maxJumps = 5, falloff = 0.75, jumpDelay = 0.1 )`，目标表防重复。用途：武器和技能共用。NPC 用 2 跳。
3. **`PulseAura`**：跟随任意实体，每 0.4 s 范围伤害（人 8，半径 200）。挂到慢球上就是 Arc Ball。
4. Instagib 的 rail jump 不直接搬，它是社区手感，记录已写，要用走"火箭跳"话题单独拟合。
5. Buster / EPG / Defender：数据只作参考，代码没有。按 R5 字段拟合后，写清"没有 R5 脚本依据"。

开关建议：`hsd.combat.special.*`。
