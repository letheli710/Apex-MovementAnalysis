# EM-4 Cold War（`mp_weapon_pulse_lmg`）：四连发榴弹

TF2 独有。会话 `tf2-weapons`，2026-11-08。

## 先说结论

扣扳机后**先蓄 0.5 s**，然后 4 连发（0.083 s 一发），每组之后 0.5 s 才能再扣，所以一组到下一组约 1.27 s。榴弹 3500 u/s、重力 0.9（675 u/s²）、撞到就炸：直接 30 / 爆炸 30（半径 96 满伤，150 为 0），对重甲 175，爆头 × 1.25；按文件会炸到自己（没测）。开镜时连射倍率 2.5 也乘在永久后坐上（−0.125° / 发）。规则都对上了文件；不同的是腰射没有永久后坐、死神不打折。

## 1. 规则（文件和脚本）

出处缩写：`txt` = `client_mp_common/scripts/weapons/mp_weapon_pulse_lmg.txt`（数值见附录），`util` = `client_mp_common/scripts/vscripts/weapons/_weapon_utility.nut`，都在 `TF2-Research/local/vpk/` 下。

### 1.1 开火

1. 没有自己的脚本：开火函数是通用的 `OnWeaponPrimaryAttack_GenericBoltWithDrop_Player`（txt:24 → util:655–658），和 EPG 同一套。
2. 每发一颗 bolt：`FireWeaponBolt( pos, dir, 1, … )`，速度倍率 1 → `projectile_launch_speed 3500`；脚本把 `kv.gravity` 设成 1（util:632–653）。txt 另有 `projectile_gravity_scale 0.9`，哪个生效见实测。
3. txt：`fire_mode semi-auto`，`burst_fire_count 4`，`fire_rate 12`，`burst_fire_delay 0.5`，`ammo_min_to_fire 4`，弹匣 12（= 3 组）。另有 `charge_time 0.5`、`charge_cooldown_time 0.5`、`charge_end_forces_fire 1`、`charge_require_input 0`——蓄力键和连发怎么配合，原生代码，见实测。
4. 撞到东西就炸（bolt）。

### 1.2 伤害

| 项 | 对人 | 对重甲 | 出处 |
|---|---|---|---|
| 直接命中 | 30（近 1250 / 远 15000 同值） | 175 | txt `damage_*` |
| 爆头 | × 1.25（`headshot_distance 4500`） | | |
| 爆炸 | 30 | 175 | `explosion_damage(_heavy_armor)` |
| 爆炸半径 | 内 96，外 150 | | |
| 炸到自己 | 会（`explosion_damages_owner 1`） | | |
| 非泰坦重甲 | 重甲值 × 0.5 | | |
| 打击力 | 7000；`jump_kit` mod 爆炸打击力 27500 | | |

### 1.3 弹药、换弹、开镜、散布、后坐

- 换弹：战术 4.0 s，`late1` 2.4；空仓 4.6 s，`late1` 3.2、`late2` 1.7。掏枪 0.66（第一次 1.6），收枪 0.5。
- 开镜 0.2 / 0.15 s，FOV 45，开镜移速 × 0.75。
- 散布：腰射站 0.5°、跑 2.5°、冲刺 4.5°、空中 5.5°、蹲 0.5°、跑墙 / 挂墙 0.75°；开镜 0。每发加 0.075°（蹲 0.05、空中 0.15），上限 8°（蹲 5°）；停火 0.1 s 后每秒回 40°。
- 后坐：弹簧 `lstar`；俯仰 −0.05 ± 0.2，偏航 0 ± 0.4（内排除 0.15）；永久后坐俯仰 −0.05、偏航 0.025 ± 0.05；连射放大 `viewkick_scale` 腰射 3.5、开镜 2.5（每发 +1，5 发到顶）。另有一套 `cooldown_viewkick_*`（俯仰 −6 ± 0.5、偏航 −0.5 ± 1），名字看是蓄力冷却时的后坐，没查。

## 2. 实测

运行：`runtime/data/20261108_034651_wp_a`（A），`runtime/data/20261108_132546_wp_b`（B，单个快冻步兵上补测命中和溅射）。每项 1–4 次。

| 项 | 实测 | 文件 / 脚本 | 对得上？ |
|---|---|---|---|
| 扣扳机到第一发 | **0.507 s**（5 次 0.5069–0.5084） | `charge_time 0.5` | ✓ 先蓄 0.5 s 再开火 |
| 一组 | 4 发，间隔 0.083–0.090 s；弹匣每发 −1 | `burst_fire_count 4`、`fire_rate 12`（0.0833） | ✓ |
| 一组到下一组 | 第 4 发到下一组第 1 发 1.02 s（= 组间 0.5 + 再蓄 0.5）；一组第 1 发到下一组第 1 发 1.27 s | `burst_fire_delay 0.5` + `charge_time 0.5` | ✓ 每组都要重新蓄 |
| 弹速 | 3500.0（出膛那一帧） | `projectile_launch_speed 3500` | ✓ |
| 重力 | **675 u/s²**（每 0.1 s 竖直速度少 67.5，4 发都一样） | `projectile_gravity_scale 0.9` × 750；脚本另写 `kv.gravity = 1` | ✓ 按 0.9；脚本那行不改变结果（推断它是倍率） |
| 阻力 | 水平速度 3423.6 → 3423.6（−12° 发射） | 没有 | 没有阻力 |
| 每发散布增长 | 腰射 0.5 → 0.575 → 0.65 → 0.725 → 0.8；开镜 0 → 0.075 … 0.3 | 每发 +0.075 | ✓ |
| 姿态散布 | 站 0.5、蹲 0.5、走到 2.5、冲刺 4.5、空中 5.5、开镜 0 | 同 | ✓ |
| 开镜时弹道偏移 | 第 1 发相对视线偏航 +0.96 / +0.99 / +0.98°，俯仰 −0.46 … +0.20°（3 次） | 没有 `zoom_angle_shift` 键 | 出弹点在眼睛，方向偏左约 1°，原因没查（推断是枪口对准修正） |
| 永久后坐 | 开镜 8 发共俯仰 −1.00°、偏航 +0.40°（−0.125 / +0.05 每发）；4 发 −0.50 / +0.26–0.30 | `viewkick_perm_pitch_base −0.05`、`yaw 0.025 ± 0.05`，× 连射倍率开镜 2.5 | ✓ **连射倍率也乘在永久后坐上** |
| 永久后坐（腰射） | 8 发共 0.000 | × 3.5 应是 −0.175 / 发 | ✗ 腰射没有永久后坐，原因没查 |
| 开镜 | 0.5 在 0.107–0.111 s，0.99 在 0.205–0.208 s | `zoom_time_in 0.2` | ✓ |
| 关镜 | 0.5 在 0.083–0.088 s，0.01 在 0.157–0.160 s | `zoom_time_out 0.15` | ✓ |
| 对泰坦 | 每发 175（4 发 −700） | 直接 175，爆炸重甲 175 | ✓，每发只记一次伤害 |
| 对死神 | 每发 175 | 重甲 175 × 0.5 = 87.5 | ✗ 非泰坦重甲倍率没生效（同 Double Take） |
| 爆头 | 37.5（hit group 1） | 30 × 1.25 | ✓ |
| 空仓换弹 | 补满 3.61 s，能开火 4.11 s | 4.6 | 见 README 换弹规则 |
| 战术换弹 | 补满 2.67 s，能开火 3.70 s | 4.0 | 同上 |
| 换弹中断 | 0.79 s 切走 → 再换 4.17 s；1.79 s → 2.68 s；3.06 s → 1.15 s | 节点 1.4 / 2.9，late1 3.2 / late2 1.7 | ✓ |

**打步兵**（`runtime/data/20261108_134638_wp_f`（F，步兵冻结后放回 `(24, −1500)`，离出生点 364 u，开镜各 1 发））：瞄胸 4 发每发 30（hit group 2 / 3 / 4，一发只记一次伤害：直接命中的目标不再另吃爆炸）；瞄腿的 3 发落在步兵前面 90 u 的地上，溅射照样 30（在内半径 96 以内），1 发打中腿 30（hit group 6）。爆头 37.5（hit group 1，`wp_a`，30 × 1.25）。

**溅射随距离**（`runtime/data/20261108_132546_wp_b`，地面爆点到步兵的水平距离；步兵位置用冻结后的日志位置）：

| 距离（u） | ≤ 110 | 117 | 119 | 128 | 138 | 144 | 149 | 155 |
|---|---|---|---|---|---|---|---|---|
| 伤害 | 30 | 30 | 28 | 23 | 18 | 13 | 11 | 8 |

线性下降，斜率约 0.56 / u（30 / 54），满伤到约 115 u，零点约 169 u：和文件的内 96 / 外 150 相比都远了约 19 u，即距离是从**步兵的碰撞盒边缘**算的（推断）。
<!--CW-HEAD-->



## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| 腰射没有永久后坐 | 实测 8 发 0.000；开镜 −0.125 / 发。原生后坐代码没读 | 照实测做 |
| 开镜时弹道偏左约 1° | 文件里没有 `zoom_angle_shift`；推断是出弹点 / 枪口方向修正 | 小，HSD 可以不做 |
| `cooldown_viewkick_*`（俯仰 −6 ± 0.5） | 名字看是蓄力冷却的后坐；这次没看到大幅后坐 | 没观察到效果 |
| 炸到自己的伤害 | 没测（`explosion_damages_owner 1`） | 近距离开火会伤自己 |
| `jump_kit` mod（爆炸推力 27500） | 没测；EPG 的同名 mod 见 [../epg/](../epg/T1-T7-REPORT.md) | 火箭跳 |
| 爆炸伤害随距离的形状 | 见第 2 节 B 的溅射数据；内半径内满伤、外半径 0，中间按线性推断 | |


## 4. 能不能脱离 TF2 照做

**能照做的**：蓄力 + 连发的时序、弹道（速度、重力 0.9、无阻力）、爆炸伤害随距离线性衰减（实测斜率 0.56 / u，和 96 → 150 一致）、散布、开镜、后坐（开镜）、换弹和中断（这把枪的节点正好在 T − late_k）。

**还缺的**：腰射不带永久后坐的原因；开镜时弹道偏左 1° 的原因；自伤、`jump_kit` 没测；`cooldown_viewkick_*` 没看到效果。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

### mp_weapon_pulse_lmg 文件原值（`mp_weapon_pulse_lmg.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 0 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_reload_max` | 200 |  |  |
| `ammo_clip_size` | 12 | 20 | extended_ammo=16 |
| `ammo_default_total` | 200 | 80 | extended_ammo=375 |
| `ammo_min_to_fire` | 4 |  |  |
| `ammo_no_remove_from_clip` | 0 |  |  |
| `ammo_no_remove_from_stockpile` | 1 | 0 |  |
| `ammo_stockpile_max` | 200 | 80 | extended_ammo=375 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `burst_fire_count` | 4 |  |  |
| `burst_fire_delay` | 0.5 |  |  |
| `charge_cooldown_delay` | 0.0 |  |  |
| `charge_cooldown_time` | 0.5 |  |  |
| `charge_end_forces_fire` | 1 |  |  |
| `charge_require_input` | 0 |  |  |
| `charge_time` | 0.5 |  |  |
| `cooldown_time` | 0.0 |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_mode` | semi-auto |  |  |
| `fire_rate` | 12.0 |  |  |
| `primary_fire_does_not_block_sprint` | 0 |  | pas_run_and_gun=1 |
| `regen_ammo_refill_rate` | 0.0 |  |  |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 1 |  |  |
| `critical_hit` | 0 |  |  |
| `critical_hit_damage_scale` | 1.5 |  |  |
| `damage_far_distance` | 15000 |  |  |
| `damage_far_value` | 30 | 90 | burn_mod_pulse_lmg=45 |
| `damage_far_value_titanarmor` | 175 | 150 | burn_mod_pulse_lmg=300 |
| `damage_flags` | DF_BULLET \| DF_GIB |  |  |
| `damage_headshot_scale` | 1.25 |  |  |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 1250 |  |  |
| `damage_near_value` | 30 | 90 | burn_mod_pulse_lmg=45 |
| `damage_near_value_titanarmor` | 175 | 150 | burn_mod_pulse_lmg=300 |
| `damage_rodeo` | 125 |  |  |
| `explosion_damage` | 30 | 25 | burn_mod_pulse_lmg=45 |
| `explosion_damage_heavy_armor` | 175 | 100 | burn_mod_pulse_lmg=300 |
| `explosion_damages_owner` | 1 |  |  |
| `explosion_inner_radius` | 96 |  |  |
| `explosionradius` | 150 |  |  |
| `headshot_distance` | 4500 |  |  |
| `impulse_force` | 7000 |  | jump_kit=7000 |
| `impulse_force_explosions` | — |  | jump_kit=27500 |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_gravity_scale` | 0.9 |  |  |
| `projectile_launch_speed` | 3500 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.66 |  |  |
| `deployfirst_time` | 1.6 |  |  |
| `fast_swap_to` | — |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 4.0 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | 2.4 |  | pas_fast_reload=*0.7 |
| `reloadempty_time` | 4.6 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 3.2 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 1.7 |  |  |

**开镜**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `ads_move_speed_scale` | 0.75 |  |  |
| `aimassist_adspull_zoomEnd` | 1.0 |  |  |
| `aimassist_adspull_zoomStart` | 0.05 |  |  |
| `zoom_fov` | 45 |  |  |
| `zoom_time_in` | 0.2 |  | pas_fast_ads=*0.5 |
| `zoom_time_out` | 0.15 |  | pas_fast_ads=*0.6 |

**散布**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `spread_air_ads` | 0.0 |  |  |
| `spread_air_hip` | 5.5 |  |  |
| `spread_crouch_ads` | 0.0 |  |  |
| `spread_crouch_hip` | 0.5 |  |  |
| `spread_decay_delay` | 0.1 |  |  |
| `spread_decay_rate` | 40 |  |  |
| `spread_kick_on_fire_air_ads` | 0.15 |  |  |
| `spread_kick_on_fire_air_hip` | 0.15 |  |  |
| `spread_kick_on_fire_crouch_ads` | 0.05 |  |  |
| `spread_kick_on_fire_crouch_hip` | 0.05 |  |  |
| `spread_kick_on_fire_stand_ads` | 0.075 |  |  |
| `spread_kick_on_fire_stand_hip` | 0.075 |  |  |
| `spread_max_kick_air_ads` | 6.0 |  |  |
| `spread_max_kick_air_hip` | 8.0 |  |  |
| `spread_max_kick_crouch_ads` | 3.0 |  |  |
| `spread_max_kick_crouch_hip` | 5.0 |  |  |
| `spread_max_kick_stand_ads` | 6.0 |  |  |
| `spread_max_kick_stand_hip` | 8.0 |  |  |
| `spread_stand_ads` | 0.0 |  |  |
| `spread_stand_hip` | 0.5 |  |  |
| `spread_stand_hip_run` | 2.5 |  |  |
| `spread_stand_hip_sprint` | 4.5 |  |  |
| `spread_wallhanging` | 0.75 |  |  |
| `spread_wallrunning` | 0.75 |  |  |

**后坐和视角**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `cooldown_viewkick_hardScale` | 1.0 |  |  |
| `cooldown_viewkick_pitch_base` | -6.0 |  |  |
| `cooldown_viewkick_pitch_random` | 0.5 |  |  |
| `cooldown_viewkick_pitch_random_innerexclude` | 0.0 |  |  |
| `cooldown_viewkick_softScale` | 1.5 |  |  |
| `cooldown_viewkick_yaw_base` | -0.5 |  |  |
| `cooldown_viewkick_yaw_random` | 1.0 |  |  |
| `cooldown_viewkick_yaw_random_innerexclude` | 0.0 |  |  |
| `viewkick_ads_weaponFraction` | 0.9 |  |  |
| `viewkick_ads_weaponFraction_vmScale` | 0.5 |  |  |
| `viewkick_duck_scale` | 1.0 |  |  |
| `viewkick_hipfire_weaponFraction` | 0.75 |  |  |
| `viewkick_hipfire_weaponFraction_vmScale` | 0.75 |  |  |
| `viewkick_perm_pitch_base` | -0.05 |  |  |
| `viewkick_perm_pitch_random` | 0.0 |  |  |
| `viewkick_perm_yaw_base` | 0.025 |  |  |
| `viewkick_perm_yaw_random` | 0.05 |  |  |
| `viewkick_pitch_base` | -0.05 |  |  |
| `viewkick_pitch_hardScale` | 1.0 |  |  |
| `viewkick_pitch_random` | 0.2 |  |  |
| `viewkick_pitch_softScale` | 2.0 |  |  |
| `viewkick_roll_base` | 0 |  |  |
| `viewkick_roll_hardScale` | 1.85 |  |  |
| `viewkick_roll_randomMax` | 0.3 |  |  |
| `viewkick_roll_randomMin` | 0.2 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_scale_max_ads` | 2.5 |  |  |
| `viewkick_scale_max_hipfire` | 3.5 |  |  |
| `viewkick_scale_min_ads` | 2.5 |  |  |
| `viewkick_scale_min_hipfire` | 3.5 |  |  |
| `viewkick_scale_valueDecayDelay` | 0.3 |  |  |
| `viewkick_scale_valueDecayRate` | 40 |  |  |
| `viewkick_scale_valueLerpEnd` | 5 |  |  |
| `viewkick_scale_valueLerpStart` | 0 |  |  |
| `viewkick_scale_valuePerShot` | 1.0 |  |  |
| `viewkick_spring` | lstar |  |  |
| `viewkick_yaw_base` | 0.0 |  |  |
| `viewkick_yaw_hardScale` | 0.8 |  |  |
| `viewkick_yaw_random` | 0.4 |  |  |
| `viewkick_yaw_random_innerexclude` | 0.15 |  |  |
| `viewkick_yaw_softScale` | 2.2 |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_damage_far_value` | 16 |  |  |
| `npc_damage_far_value_titanarmor` | 0 |  |  |
| `npc_damage_near_value` | 26 |  |  |
| `npc_damage_near_value_titanarmor` | 0 |  |  |
| `npc_max_burst` | 4 |  |  |
| `npc_max_engage_range` | 2500 |  |  |
| `npc_max_engage_range_heavy_armor` | 3000 |  |  |
| `npc_max_range` | 4000 |  |  |
| `npc_min_burst` | 4 |  |  |
| `npc_min_engage_range` | 0 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_rest_time_between_bursts_max` | 1.5 |  |  |
| `npc_rest_time_between_bursts_min` | 1.0 |  |  |
| `proficiency_average_spreadscale` | 5.0 |  |  |
| `proficiency_good_spreadscale` | 4.0 |  |  |
| `proficiency_poor_spreadscale` | 7.0 |  |  |
| `proficiency_very_good_spreadscale` | 2.5 |  |  |


