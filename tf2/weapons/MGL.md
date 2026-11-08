# MGL Mag Launcher（`mp_weapon_mgl`）：磁吸榴弹

TF2 独有。会话 `tf2-weapons`，2026-11-08。

## 先说结论

**磁吸榴弹**，两连发（0.167 s），每组之间 0.7 s。榴弹 1200 u/s、向上抬 6°、普通重力、1.2 s 引信（从发射算）。**磁吸规则这次从原生代码读出来了**：只吸 `magneticRange` > 0 的敌人（泰坦 190，死神、幽灵、潜行者、无人机等 125；普通步兵和铁驭没有），进了范围后约 0.1 s 内就变成 1600 u/s 直冲目标中心，撞上就炸。实测死神、泰坦都被吸过去，步兵不吸、撞上也不炸。伤害：直接 20 / 330，爆炸 35 / 70。

## 1. 规则（文件和脚本）

出处缩写：`txt` = `client_mp_common/scripts/weapons/mp_weapon_mgl.txt`（数值见附录），`nut` = `client_mp_common/scripts/vscripts/weapons/mp_weapon_mgl.nut`，`consts` = `client_frontend/scripts/vscripts/sh_consts.gnut`，都在 `TF2-Research/local/vpk/` 下。

### 1.1 开火

1. 半自动**两连发**：`burst_fire_count 2`，两发之间按 `fire_rate 6`（1/6 s），一组之后 `burst_fire_delay 0.7` s。弹匣 6（= 3 组），备弹 30。
2. 每发一颗榴弹（`FireWeaponGrenade`，nut:55）：出膛 1200 u/s，**向上抬 6°**（`projectile_launch_pitch_offset 6`），重力按普通榴弹。
3. 引信 1.2 s（`grenade_fuse_time`），从发射算起（1.2 节）。弹跳键同 Softball：浅角 0.47、陡角 0.28、法向 0.5、滚动 0.1。
4. 发射后 `InitMagnetic( MGL_MAGNETIC_FORCE, … )`（nut:68），`MGL_MAGNETIC_FORCE = 1600`（consts:453）。磁吸的规律见 1.2。
5. 撞到东西时（nut:75–86）：对方是"磁性目标"（`IsMagneticTarget`，原生）而且不是同队 → **当场炸**；否则照常弹跳，等引信。
6. nut:14 的 `MAX_BONUS_VELOCITY 1250` 没有用上（死代码）。

### 1.2 磁吸（原生代码，`server.dll`，Ghidra 工程 `ghidra-projects/tf2`）

脚本只调 `InitMagnetic( 1600, 声音 )`。原生部分这次读出来了（反编译原文在私有仓库 `HSD-RawData` 的 `tf2/local/ghidra-weapons/`；地址是 Ghidra 基址）：

1. `InitMagnetic`（`FUN_1800f5970`）只把"开磁吸"标志和力 1600 存进榴弹（`+0x1cc8`、`+0x1ccc`），再记下吸附音效。
2. 榴弹每次思考（`FUN_1800f6d10`）：
   - 先看引信：**从发射算起**到 1.2 s 就爆（不是从第一次落地算）。
   - 开了磁吸就找目标（`FUN_1800f5ed0`）：先找玩家，再找 NPC；要求**不是同队**、活着，而且这个目标的 **`magneticRange` > 0**，榴弹到目标中心（`WorldSpaceCenter`）的距离 < `magneticRange`。找到的第一个就用。榴弹 1 u 内没动、队伍没变时沿用上次的结果。
   - 第一次找到目标时放一次吸附声。
   - 新速度（`FUN_1800f61c0` + `FUN_1800f5d20`）：
     ```
     m = 1600 × normalize( 目标中心 − 榴弹位置 )      // 大小恒为 1600，和距离无关
     k = powf( 1e-12, dt )                            // dt = 这一帧的时长
     新速度 = k × 旧速度 + (1 − k) × m
     ```
     k 很小（每 1/60 s 剩 0.63，每 0.1 s 剩 0.063），所以进了范围以后大约 0.1 s 内就变成"以 1600 u/s 直冲目标中心"。
3. `magneticRange` 是职业 / AI 设置里的键（schema 注释："Range for magnetic grenade attraction. 0 for off"；玩家设置 `+0x3b4`，AI 设置 `+0x1b14`）。本地文件里的值：

| 目标 | `magneticRange` | 出处 |
|---|---|---|
| 泰坦（NPC `npc_titan`、玩家泰坦 `titan_base.set`） | 190 | aisettings、players/mp |
| 运输机、炮艇、大炮塔 | 190 | aisettings |
| 死神、幽灵、潜行者、特种兵（`*_specialist`）、精英铁驭、无人机、扁虱 | 125 | aisettings |
| 哨戒炮 | 90 | aisettings |
| 工作无人机 | 30 | `npc_drone_worker` |
| Marvin | 60 | `npc_marvin` |
| **普通步兵 `npc_soldier`、铁驭（玩家）** | **没有这个键 = 0，不吸** | |

4. 撞到"磁性目标"（`IsMagneticTarget`，原生，没有单独读）而且不同队 → 当场炸（nut:79–84）。

### 1.3 伤害

| 项 | 对人 | 对重甲 | 出处 |
|---|---|---|---|
| 直接命中 | 20（近 70 / 远 1500 同值） | 330 | txt `damage_*` |
| 爆炸 | 35 | 70 | `explosion_damage(_heavy_armor)` |
| 爆炸半径 | 内 50，外 100 | | |
| 非泰坦重甲 | 重甲值 × 0.5 | | |
| 爆头 | 不能 | | |
| 打击力 | 700 | | |

### 1.4 弹药、换弹、开镜、后坐

- 换弹：战术 3.75 s，`late1` 2.75、`late2` 2.00、`late3` 1.5；空仓 3.75 s，`late1` 2.75、`late2` 2.00、`late3` 1.08。
- 掏枪 0.8，收枪 0.5。开镜 0.2 / 0.15 s，FOV 55。散布：腰射 0.25°，开镜 0.35°。
- 后坐：`launcher` 弹簧，俯仰 −0.3 ± 0.1，偏航 0 ± 0.15；永久后坐俯仰 0 ± 0.3、偏航 0 ± 0.2。

## 2. 实测

运行：`runtime/data/20261108_033208_wp_smoke`、`runtime/data/20261108_133109_wp_c`（C）。泰坦 `(24, −1000)`、死神 `(−200, −1300)` 生成 0.25 s 后冻结，位置没动；步兵在 `(−14, −1347)` 附近。每项 1–5 次。

| 项 | 实测 | 文件 / 规则 | 对得上？ |
|---|---|---|---|
| 两连发 | 两发间隔 0.1666–0.1684 s | `fire_rate 6` | ✓ |
| 组间 | 第 2 发到下一组第 1 发 0.784 s；按住不放只打一组 | `burst_fire_delay 0.7`；半自动 | ✓（多出约 0.08 s，没细查） |
| 出膛 | 1200 u/s；方向比视线**高 6.0°**（−20° 俯射时 −14.0°；第二发 −12.6°） | `projectile_launch_pitch_offset 6` | ✓ |
| 重力 | 750 u/s² | 1.0 × 750 | ✓ |
| 引信 | 没撞到磁性目标时，从发射起 1.1–1.2 s 爆；`wp_e` 在空中（没落地）的 10 发全部在 **1.20 s** 爆 | 1.2 s，从发射算（1.2 节） | ✓ 空中也照样爆 |
| 弹地 | 以 14° 斜撞地面：水平 1164 → 472（× 0.41），竖直 → +86 | 浅角 0.47、陡角 0.28、法向 0.5，随机 0.2 | 大致对得上，没拟合 |
| **磁吸：死神** | 瞄泰坦左侧 −260 / −160 的两组弹，路过死神（`magneticRange 125`）时**拐过去打中死神**；每发 330 + 70 | 死神 125 | ✓ |
| **磁吸：泰坦** | 瞄泰坦右侧 +160：两发都拐进去，0.7 s 打中泰坦，每发 330 + 70 | 泰坦 190 | ✓ |
| 磁吸：泰坦外侧 | 右侧 +90 那组飞到墙边弹开，没被吸（弹道在 y −1280 处先撞了墙） | | 没有干净的"范围外"对照 |
| **不吸步兵** | 瞄步兵左右 ±30 / −60：弹道不拐；直接打中步兵只记撞击 20，**不爆**，弹开后到引信时间才爆（35） | 步兵没有 `magneticRange` | ✓ |
| 对泰坦 / 死神 | 撞击 330 + 爆炸 70（两次伤害） | 330 / 70 | ✓（死神同样不打折） |
| 散布 | 腰射 0.25，开镜 0.35，开火那一帧 0.35 | 同 | ✓ |
| 永久后坐 | 4 发共俯仰 −0.47°、偏航 +0.01°；2 发 +0.04° / +0.13° | 俯仰 0 ± 0.3、偏航 0 ± 0.2 | ✓（随机，均值约 0） |
| 开镜 | 0.5 在 0.11 s，0.99 在 0.21 s | 0.2 / 0.15 | ✓ |
| 空仓换弹 | 补满 3.12 s，能开火 3.39 s | 3.75 | 提前 0.36 s |
| 战术换弹 | 补满 3.18 s，能开火 3.45 s | 3.75 | 提前 0.30 s |
| 换弹中断 | 0.69 s 切走 → 再换 2.48 s（late1 2.75）；1.66 s → 1.75 s（late2 2.00）；2.25 s → 0.90 s（late3 1.08）；2.85 s → 0.77 s（弹匣马上满） | 节点按 T − late_k 应在 1.00 / 1.75 / 2.67 | 每一档都比 T − late_k **早**到（见 README 换弹规则） |


## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| 磁吸目标点 | 原生用目标的 `WorldSpaceCenter`，另有一个附着点下标（`+0xde8`）时用附着点；没查哪些目标有 | 吸向身体中心还是某个部位 |
| 范围外不吸的干净对照 | 右侧 +90 那组先撞了墙 | 规则读代码已清楚 |
| `IsMagneticTarget`（撞上即炸） | 原生，没单独读；实测泰坦、死神撞上即炸，步兵不炸 | 推断 = `magneticRange > 0` |
| 组间多出的 0.08 s | 没细查 | 小 |
| 弹跳系数的准确形式 | 只有 1 次弹地 | 弹跳手感 |


## 4. 能不能脱离 TF2 照做

**能照做的**：开火时序、弹道、引信、磁吸（目标表、范围、速度混合公式 `k = powf(1e-12, dt)`、1600 u/s）、撞磁性目标即炸、伤害、换弹和中断。实测对照：本页第 2 节，`runtime/data/20261108_133109_wp_c`。

**还缺的**：磁吸瞄的是目标中心还是某个附着点（没查附着点下标）；弹跳系数只有一次弹地；`IsMagneticTarget` 按推断等于 `magneticRange > 0`。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

### mp_weapon_mgl 文件原值（`mp_weapon_mgl.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_size` | 6 |  | extended_ammo=8 |
| `ammo_default_total` | 30 | 36 | extended_ammo=40 |
| `ammo_min_to_fire` | 1 |  |  |
| `ammo_no_remove_from_stockpile` | 0 |  | at_unlimited_ammo=1 |
| `ammo_stockpile_max` | 30 | 36 | extended_ammo=40 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `burst_fire_count` | 2 |  |  |
| `burst_fire_delay` | 0.7 |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_mode` | semi-auto |  |  |
| `fire_rate` | 6 |  |  |
| `primary_fire_does_not_block_sprint` | — |  | pas_run_and_gun=1 |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 0 |  |  |
| `critical_hit` | 0 |  |  |
| `damage_far_distance` | 1500 |  |  |
| `damage_far_value` | 20 | 10 | burn_mod_mgl=50 |
| `damage_far_value_titanarmor` | 330 | 150 | burn_mod_mgl=480 |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 70 | 100 |  |
| `damage_near_value` | 20 | 10 | burn_mod_mgl=50 |
| `damage_near_value_titanarmor` | 330 | 150 | burn_mod_mgl=480 |
| `damage_type` | burn |  |  |
| `explosion_damage` | 35 | 45 | burn_mod_mgl=45 |
| `explosion_damage_heavy_armor` | 70 | 150 | burn_mod_mgl=125 |
| `explosion_inner_radius` | 50 |  |  |
| `explosionradius` | 100 |  |  |
| `impulse_force` | 700 |  |  |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `bounce_effect_table` | bounce_mgl |  |  |
| `grenade_bounce_extra_vertical_randomness` | 0.2 |  |  |
| `grenade_bounce_randomness` | 0.2 |  |  |
| `grenade_bounce_vel_frac_along_normal` | 0.5 |  |  |
| `grenade_bounce_vel_frac_shallow` | 0.47 |  |  |
| `grenade_bounce_vel_frac_sharp` | 0.28 |  |  |
| `grenade_fuse_time` | 1.2 |  |  |
| `grenade_roll_vel_frac_per_second` | 0.1 |  |  |
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_launch_pitch_offset` | 6 |  |  |
| `projectile_launch_speed` | 1200 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.8 |  |  |
| `fast_swap_to` | 0 |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 3.75 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | 2.75 |  | pas_fast_reload=*0.7 |
| `reload_time_late2` | 2.00 |  |  |
| `reload_time_late3` | 1.5 |  |  |
| `reloadempty_time` | 3.75 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 2.75 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 2.00 |  |  |
| `reloadempty_time_late3` | 1.08 |  |  |

**开镜**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `zoom_fov` | 55 |  |  |
| `zoom_time_in` | 0.2 |  | pas_fast_ads=*0.5 |
| `zoom_time_out` | 0.15 |  | pas_fast_ads=*0.6 |

**散布**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `spread_air_ads` | 0.35 |  |  |
| `spread_air_hip` | 0.25 |  |  |
| `spread_crouch_ads` | 0.35 |  |  |
| `spread_crouch_hip` | 0.25 |  |  |
| `spread_decay_delay` | .1 |  |  |
| `spread_decay_rate` | 5 |  |  |
| `spread_kick_on_fire_air_ads` | .1 |  |  |
| `spread_kick_on_fire_air_hip` | .1 |  |  |
| `spread_kick_on_fire_crouch_ads` | .05 |  |  |
| `spread_kick_on_fire_crouch_hip` | 0.1 |  |  |
| `spread_kick_on_fire_stand_ads` | .075 |  |  |
| `spread_kick_on_fire_stand_hip` | 0.1 |  |  |
| `spread_max_kick_air_ads` | 0.0 |  |  |
| `spread_max_kick_air_hip` | 5.0 |  |  |
| `spread_max_kick_crouch_ads` | 0.0 |  |  |
| `spread_max_kick_crouch_hip` | 1.0 |  |  |
| `spread_max_kick_stand_ads` | 0.0 |  |  |
| `spread_max_kick_stand_hip` | 2.0 |  |  |
| `spread_stand_ads` | 0.35 |  |  |
| `spread_stand_hip` | 0.25 |  |  |
| `spread_stand_hip_run` | 0.25 |  |  |
| `spread_stand_hip_sprint` | 0.25 |  |  |

**后坐和视角**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `viewdrift_ads_speed_pitch` | 0.63 |  |  |
| `viewdrift_ads_speed_yaw` | 0.6 |  |  |
| `viewdrift_hipfire_air_scale_pitch` | 0.5 |  |  |
| `viewdrift_hipfire_air_scale_yaw` | 0.22 |  |  |
| `viewdrift_hipfire_crouch_scale_pitch` | 0.275 |  |  |
| `viewdrift_hipfire_crouch_scale_yaw` | 0.10 |  |  |
| `viewdrift_hipfire_speed_pitch` | 0.6 |  |  |
| `viewdrift_hipfire_speed_yaw` | 1.22 |  |  |
| `viewdrift_hipfire_stand_scale_pitch` | 0.325 |  |  |
| `viewdrift_hipfire_stand_scale_yaw` | 0.12 |  |  |
| `viewkick_ads_weaponFraction` | 0.3 |  |  |
| `viewkick_ads_weaponFraction_vmScale` | 0.5 |  |  |
| `viewkick_hipfire_weaponFraction` | 0.8 |  |  |
| `viewkick_hipfire_weaponFraction_vmScale` | 1.0 |  |  |
| `viewkick_perm_pitch_base` | 0.0 |  |  |
| `viewkick_perm_pitch_random` | 0.3 |  |  |
| `viewkick_perm_yaw_base` | 0.0 |  |  |
| `viewkick_perm_yaw_random` | 0.2 |  |  |
| `viewkick_pitch_base` | -0.3 |  |  |
| `viewkick_pitch_hardScale` | 6.75 |  |  |
| `viewkick_pitch_random` | 0.1 |  |  |
| `viewkick_pitch_softScale` | 1.2 |  |  |
| `viewkick_roll_base` | 0.0 |  |  |
| `viewkick_roll_hardScale` | 1.7 |  |  |
| `viewkick_roll_randomMax` | 0.7 |  |  |
| `viewkick_roll_randomMin` | 0.5 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_spring` | launcher |  |  |
| `viewkick_yaw_base` | 0.0 |  |  |
| `viewkick_yaw_hardScale` | 1.0 |  |  |
| `viewkick_yaw_random` | 0.15 |  |  |
| `viewkick_yaw_softScale` | 1.3 |  |  |
| `viewpunch_multiplier` | 1.25 |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_damage_far_distance` | 1500 |  |  |
| `npc_damage_far_value` | 0 |  |  |
| `npc_damage_far_value_titanarmor` | 0 |  |  |
| `npc_damage_near_distance` | 100 |  |  |
| `npc_damage_near_value` | 0 |  |  |
| `npc_damage_near_value_titanarmor` | 0 |  |  |
| `npc_max_burst` | 3 | 1 |  |
| `npc_max_engage_range` | 2000 |  |  |
| `npc_max_engage_range_heavy_armor` | 3500 |  |  |
| `npc_max_range` | 8000 |  |  |
| `npc_min_burst` | 3 | 1 |  |
| `npc_min_engage_range` | 100 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_min_range` | 0 |  |  |
| `npc_miss_fast_player` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 3.5 | 1 |  |
| `npc_rest_time_between_bursts_min` | 2.0 | 0.5 |  |
| `npc_self_explosion_safety` | 0 |  |  |
| `proficiency_average_spreadscale` | 10.0 |  |  |
| `proficiency_good_spreadscale` | 3.3 |  |  |
| `proficiency_perfect_spreadscale` | 2.0 |  |  |
| `proficiency_poor_spreadscale` | 10.0 |  |  |
| `proficiency_very_good_spreadscale` | 3.3 |  |  |


