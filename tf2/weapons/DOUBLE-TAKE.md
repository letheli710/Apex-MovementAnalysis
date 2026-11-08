# D-2 Double Take（`mp_weapon_doubletake`）：一字排开的三颗弹

TF2 独有。Apex 的 Triple Take 是远亲（能量弹、收束 Hop-up），机制不同，见 [VARIANTS.md](VARIANTS.md) 3.23。会话 `tf2-weapons`，2026-11-08。

## 先说结论

一次开火打出**一字排开的 3 颗高速弹**（左右各偏 0.215°），扣 2 发弹药，0.5 s 一发。不衰减，每颗 30，爆头 × 2，对泰坦每颗 165。开镜后散布为 0，弹道还会按文件里的 `zoom_angle_shift` 往左上偏一点（0.65° / 0.3°），实测对上了。腰射散布 8° 起、每发 +4°。所有规则和数值都在文件和脚本里，实测和文件一致；唯一和键名不符的是**死神吃满额重甲伤害**（没有 × 0.35）。打人和爆头倍率见第 2 节 `wp_f`。

## 1. 规则（文件和脚本）

出处缩写：`txt` = `client_mp_common/scripts/weapons/mp_weapon_doubletake.txt`（数值见附录），`nut` = `client_mp_common/scripts/vscripts/weapons/mp_weapon_doubletake.nut`，都在 `TF2-Research/local/vpk/` 下。

### 1.1 一次开火

1. 半自动，射速上限 2 发 / s（`fire_rate 2.0`）。
2. **每次开火打出 3 颗弹，扣 2 发弹药**：`projectiles_per_shot 3`（txt），开火函数 `return 2`（nut:91）。`ammo_min_to_fire 2`：剩 1 发时打不出。名字叫 Double Take，实际是 3 颗：左、右两颗带拖尾，中间那颗是"减弱特效"版（`SetReducedEffects`，nut:80），也不能跳弹（`SetRicochetMaxCount(0)`，nut:81）。
3. 三颗弹的方向（nut:10–15, 57–75）：
   - 基础方向是开火方向（已含散布）；
   - 第 1、2 颗各加 `右向量 × (∓0.25 × s)`，第 3 颗不偏；
   - `s = Graph( zoomFrac, 0, 1, bolt_spread_max, bolt_spread_min )`，两个值都是 0.015，所以腰射、开镜一样。
   - 换成角度：左右两颗各偏 `atan(0.25 × 0.015)` = **0.2149°**，两颗之间 0.43°。在 1000 u 处左右相距 7.5 u。
   - 只有 `arc_net` mod 会把 s 放大 1.5 倍（本地文件里没有这个 mod 的定义）。
4. 弹体：`bolt_speed 10000`，重力 `bolt_gravity_amount 0.09`（nut:84 写进 `kv.gravity`），不继承玩家速度（`projectile_inherit_owner_velocity_scale 0`）。命中体积 0 → 3（0.035 s）→ 4（0.08 s）→ 6（0.18 s 内长满）。
5. 穿透：`pass_through_depth 32`，穿过后伤害保留 1.0。
6. 跳弹：默认 0 次；`ricochet` mod 2 次、反弹保留速度 0.7（txt Mods）。

### 1.2 伤害

| 项 | 值 | 出处 |
|---|---|---|
| 每颗 | 30，近 4500 / 远 15000 两端同值（不衰减） | txt `damage_near/far_*` |
| 一次开火（3 颗全中） | 90（算） | |
| 爆头 | × 2.0 | `damage_headshot_scale` |
| 对泰坦（重甲） | 每颗 165；`titanarmor_critical_hit_required 1` | txt |
| 非泰坦重甲（死神等） | 重甲值 × 0.35 | `damage_heavyarmor_nontitan_scale` |
| 牛仔骑乘 | 80 | `damage_rodeo` |
| 打击力 | 2500 | `impulse_force` |

### 1.3 弹药、换弹、切枪

- 弹匣 12（= 6 次开火），备弹 120（多人不扣备弹，`ammo_no_remove_from_stockpile 1`）；`extended_ammo` 16。
- 换弹：战术 2.4 s，`reload_time_late1` 1.26；空仓 3.4 s，`reloadempty_time_late1` 2.26、`late2` 1.26。
- 收枪 0.45，掏枪 0.6，放下 0.25，抬起 0.3。

### 1.4 开镜、散布、后坐

- 开镜 0.4 s 进 / 0.3 s 出，`zoom_fov 26.26`，开镜移速 × 0.5，`trigger_snipercam 1`。
- 散布：腰射站 / 跑 / 空中 8°，蹲 6°，跑墙 8°，挂墙 11.75°；开镜全是 0。每发腰射加 4°，上限 18°（蹲 15°）；停火 0.1 s 后每秒回 4°。
- 后坐：弹簧 `semisniper`；俯仰 −0.61 ± 0.12，偏航 0.05 ± 0.14；永久后坐俯仰 −0.47 ± 0.23；腰射 40 % 给枪模、开镜 0 %。

## 2. 实测

运行：`runtime/data/20261108_034651_wp_a`（下称 A），`runtime/data/20261108_132546_wp_b`（下称 B，补测打步兵）。分析输出在各运行目录的 `analysis.txt`（[tools/analyze_wp.py](tools/analyze_wp.py)）。每项 1–3 次。

| 项 | 实测 | 文件 / 脚本 | 对得上？ |
|---|---|---|---|
| 射速（连按） | 两发间隔 0.505 / 0.500 s（腰射），0.502 / 0.505 s（开镜） | `fire_rate 2.0` → 0.5 s | ✓ |
| 每发耗弹 | 弹匣每次 −2 | `return 2` | ✓ |
| 每发弹数 | 3 个 `crossbow_bolt` | `projectiles_per_shot 3` | ✓ |
| 弹速 | 10000.0 u/s（出膛那一帧） | `bolt_speed 10000` | ✓ |
| 重力（`wp_e` 长距离，45° 发射 2 s、20000 u） | 垂直于发射线下坠 95.4 u（2 s）→ 47.7 u/s² = 67.5 × cos 45°；速率 9994 → 9899（重力分量） | `bolt_gravity_amount 0.09` × 750 = 67.5 | ✓，没有阻力 |
| 3 颗之间的角度 | 开镜：偏航 +0.427 / +0.642 / +0.857°（相对视线），左右两颗离中间 **±0.215°** | 0.2149° | ✓ |
| 开镜时弹道偏移 | 中间那颗比视线**偏左 0.64°、偏上 0.24–0.29°**（3 次） | `zoom_angle_shift_yaw 0.65`、`_pitch 0.3` | ✓（开镜时弹道按这个角度偏开） |
| 出弹点 | 开镜时就在眼睛处（`pos − eye` = 0） | `projectile_adjust_to_gun_barrel 1` | 开镜时不从枪口出 |
| 腰射散布 | 站立 8.000°；第 1 发后 12.0，0.5 s 后第 2 发 14.35，第 3 发 16.75 | 8 + 每发 4，0.1 s 后每秒回 4°，上限 18 | ✓（12 → 12 − 0.4×4 + 4 = 14.4 → 16.8） |
| 姿态散布 | 站 8，蹲 6，走 8，冲刺 8，空中 8，开镜 0 | 同 | ✓ |
| 腰射 3 颗的实际偏差 | 3 发分别偏 1.3°、0.5°、5.6°（相对准星，散布 12 / 14.4 / 16.7） | `ApplyVectorSpread` 原生 | 只有 3 个点，分布形状没测 |
| 永久后坐（不动鼠标） | 腰射 3 发共俯仰 −1.53°（−0.51 / 发），开镜 3 发共 −1.33°（−0.44 / 发）；单发 −0.40、−0.43、−0.48 | `viewkick_perm_pitch_base −0.47`，随机 ±0.23 | ✓ |
| 开镜 | `zoomFrac` 线性：0.5 在 0.208–0.213 s，0.99 在 0.405–0.410 s | `zoom_time_in 0.4` | ✓ |
| 关镜 | 0.5 在 0.158–0.164 s，0.01 在 0.306–0.310 s | `zoom_time_out 0.3` | ✓ |
| 对泰坦 | 每颗 165，3 颗都中 = 495 | 165 | ✓ |
| 对死神 | 每颗 **165**（3500 → 3005） | 重甲 165 × `damage_heavyarmor_nontitan_scale 0.35` = 57.75 | ✗ **非泰坦重甲倍率没有生效**（Cold War 同样） |
| 空仓换弹 | 补满 2.17 s，能开火 2.94 s | `reloadempty_time 3.4` | 规则见 [README](README.md#共用规则换弹的三个时刻和换弹中断实测) |
| 战术换弹 | 补满 1.68 s，能开火 2.12 s | `reload_time 2.4` | 同上 |
| 换弹中断 | 0.61 s 切走 → 再换要 2.97 s（从头）；1.29 s 切走 → 再换 1.85 s | 节点 1.14 s，`reloadempty_time_late1 2.26` | ✓ |
| 第一次拿出来 | 给枪后约 1.57 s 才能开火；之前按的开火键**直接丢掉**，不会缓存（smoke） | 没有 `deployfirst_time` 键 | 实测值 |
| 切枪 | 切到副武器 0.74 s 可开火，切回来 0.83 s | 收 0.45 + 对方掏枪；对方收 + 掏 0.6 | 大体相加，没拆开测 |

<!--DT-SOLDIER-->


## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| 腰射散布的分布形状（`ApplyVectorSpread`，原生） | 只有 3 发的偏差（1.3°、0.5°、5.6°） | 腰射手感；HSD 可以先按"圆锥内均匀"做，标 `[placeholder]` |
| 画面后坐（弹簧 `semisniper`） | 脚本读不到视角弹簧；弹簧参数在 `springs.txt` | 只能照抄参数，没有实测曲线 |
| 为什么死神不吃 `damage_heavyarmor_nontitan_scale 0.35` | 原生伤害代码没读；可能这个倍率只用在别的"重甲非泰坦"（比如玩家的某些状态） | 要做死神时得定：照实测（不乘）还是照键名（乘 0.35） |
| 跳弹 mod `ricochet`（2 次，保留 0.7） | 没测 | 配件，HSD 未必要 |
| 穿透 `pass_through_depth 32` | 没测 | 打穿薄掩体 / 多个敌人 |
| 弹体命中体积随时间变大（0 → 6） | 没测（快弹体只看得到终点） | 远距离更容易命中 |
| 第一次拿出 1.57 s 从哪来 | 文件没有 `deployfirst_time`，推断是缺省值 | 只影响刚捡起 / 刚出生 |


## 4. 能不能脱离 TF2 照做

**能照做的**：开火（3 颗弹的方向公式、耗弹、射速）、弹速和重力、散布（各姿态、每发增长、回落）、开镜（线性 0.4 / 0.3 s、弹道偏移）、永久后坐、伤害和重甲值、换弹三个时刻和中断规则、第一次掏枪 1.6 s。实测对照：本页第 2 节和 `runtime/data/20261108_034651_wp_a` 等的 `analysis.txt`。

**还缺的**：画面后坐弹簧的实测曲线（只有 `springs.txt` 参数）；腰射散布的分布形状（3 个点）；跳弹、穿透没测；死神不打折的原因（照实测做即可）。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

### mp_weapon_doubletake 文件原值（`mp_weapon_doubletake.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_random_loss_on_npc_drop_chunksize` | 2 |  |  |
| `ammo_clip_size` | 12 |  | extended_ammo=16 |
| `ammo_default_total` | 120 | 36 | extended_ammo=240 |
| `ammo_min_to_fire` | 2 |  |  |
| `ammo_no_remove_from_stockpile` | 1 | 0 |  |
| `ammo_per_shot` | 2 |  |  |
| `ammo_stockpile_max` | 120 | 60 | extended_ammo=240 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_mode` | semi-auto |  |  |
| `fire_rate` | 2.0 |  |  |
| `projectiles_per_shot` | 3 |  |  |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 1 |  |  |
| `critical_hit` | 1 |  |  |
| `critical_hit_damage_scale` | 1 |  |  |
| `damage_far_distance` | 15000 |  |  |
| `damage_far_value` | 30 | 50 | burn_mod_doubletake=35 |
| `damage_far_value_titanarmor` | 165 | 50 | burn_mod_doubletake=265 |
| `damage_flags` | DF_BULLET \| DF_KNOCK_BACK \| DF_DISMEMBERMENT |  |  |
| `damage_headshot_scale` | 2.0 |  |  |
| `damage_heavyarmor_nontitan_scale` | 0.35 | 1 |  |
| `damage_near_distance` | 4500 |  |  |
| `damage_near_value` | 30 | 50 | burn_mod_doubletake=35 |
| `damage_near_value_titanarmor` | 165 | 50 | burn_mod_doubletake=265 |
| `damage_rodeo` | 80 |  |  |
| `damage_type` | bullet |  |  |
| `impulse_force` | 2500 |  |  |
| `titanarmor_critical_hit_required` | 1 |  |  |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `bolt_bounce_frac` | 0.000 |  | ricochet=0.7 |
| `bolt_gravity_amount` | 0.09 |  |  |
| `bolt_gravity_enabled` | 1 |  |  |
| `bolt_hitsize` | 0.0 |  |  |
| `bolt_hitsize_grow1_size` | 3.0 |  |  |
| `bolt_hitsize_grow1_time` | 0.035 |  |  |
| `bolt_hitsize_grow2_size` | 4.0 |  |  |
| `bolt_hitsize_grow2_time` | 0.08 |  |  |
| `bolt_hitsize_growfinal_lerptime` | 0.18 |  |  |
| `bolt_hitsize_growfinal_size` | 6.0 |  |  |
| `bolt_speed` | 10000 |  |  |
| `bolt_spread_max` | 0.015 |  |  |
| `bolt_spread_min` | 0.015 |  |  |
| `pass_through_damage_preserved_scale` | 1.0 |  |  |
| `pass_through_depth` | 32 |  |  |
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_damage_reduction_per_bounce` | 0.0 |  | ricochet=0.0 |
| `projectile_damages_owner` | 0 |  | ricochet=0 |
| `projectile_do_predict_impact_effects` | 1 |  |  |
| `projectile_inherit_owner_velocity_scale` | 0.0 |  |  |
| `projectile_ricochet_max_count` | 0 |  | ricochet=2 |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.6 |  |  |
| `fast_swap_to` | — |  | pas_fast_swap=1 |
| `holster_time` | 0.45 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 2.4 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | 1.26 |  | pas_fast_reload=*0.7 |
| `reloadempty_time` | 3.4 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 2.26 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 1.26 |  |  |

**开镜**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `ads_fov_zoomfrac_end` | 0.6 |  | scope_4x=0.7; threat_scope=0.7 |
| `ads_fov_zoomfrac_start` | 0.0 |  | scope_4x=0.5; threat_scope=0.5 |
| `ads_move_speed_scale` | 0.5 |  |  |
| `zoom_angle_shift_pitch` | 0.3 |  |  |
| `zoom_angle_shift_yaw` | 0.65 |  |  |
| `zoom_fov` | 26.26 |  |  |
| `zoom_scope_frac_end` | 1.0 |  |  |
| `zoom_scope_frac_start` | 0.2 |  |  |
| `zoom_time_in` | 0.4 |  | pas_fast_ads=*0.5 |
| `zoom_time_out` | 0.3 |  | pas_fast_ads=*0.6 |
| `zoom_toggle_fov` | — | 7 | scope_4x=7 |
| `zoom_toggle_lerp_time` | — | 0.2 | scope_4x=0.2 |

**散布**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `spread_air_ads` | 0 |  |  |
| `spread_air_hip` | 8 |  |  |
| `spread_crouch_ads` | 0 |  |  |
| `spread_crouch_hip` | 6 |  |  |
| `spread_decay_delay` | 0.1 |  |  |
| `spread_decay_rate` | 4 |  |  |
| `spread_kick_on_fire_air_hip` | 4 |  |  |
| `spread_kick_on_fire_crouch_hip` | 4 |  |  |
| `spread_kick_on_fire_stand_hip` | 4 |  |  |
| `spread_max_kick_air_hip` | 18.0 |  |  |
| `spread_max_kick_crouch_hip` | 15.0 |  |  |
| `spread_max_kick_stand_hip` | 18.0 |  |  |
| `spread_stand_ads` | 0 |  |  |
| `spread_stand_hip` | 8 |  |  |
| `spread_stand_hip_run` | 8 |  |  |
| `spread_wallhanging` | 11.75 |  |  |
| `spread_wallrunning` | 8 |  |  |

**后坐和视角**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `viewkick_ads_weaponFraction` | 0.0 |  |  |
| `viewkick_ads_weaponFraction_vmScale` | 0.0 |  |  |
| `viewkick_hipfire_weaponFraction` | 0.4 |  |  |
| `viewkick_hipfire_weaponFraction_vmScale` | 0.55 |  |  |
| `viewkick_perm_pitch_base` | -0.47 |  |  |
| `viewkick_perm_pitch_random` | 0.23 |  |  |
| `viewkick_perm_pitch_random_innerexclude` | 0.0 |  |  |
| `viewkick_perm_yaw_base` | 0.0 |  |  |
| `viewkick_perm_yaw_random` | 0.0 |  |  |
| `viewkick_perm_yaw_random_innerexclude` | 0.0 |  |  |
| `viewkick_pitch_base` | -0.61 |  |  |
| `viewkick_pitch_hardScale` | 0.9 |  |  |
| `viewkick_pitch_random` | 0.12 |  |  |
| `viewkick_pitch_softScale` | 1.2 |  |  |
| `viewkick_roll_base` | 0 |  |  |
| `viewkick_roll_hardScale` | 1.75 |  |  |
| `viewkick_roll_randomMax` | 0.5 |  |  |
| `viewkick_roll_randomMin` | 0.5 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_spring` | semisniper |  |  |
| `viewkick_yaw_base` | 0.05 |  |  |
| `viewkick_yaw_hardScale` | 1.0 |  |  |
| `viewkick_yaw_random` | 0.14 |  |  |
| `viewkick_yaw_softScale` | 1.3 |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_accuracy_multiplier_pilot` | 1.0 | 3.0 |  |
| `npc_damage_far_value` | 7 | 30 |  |
| `npc_damage_far_value_titanarmor` | 100 |  |  |
| `npc_damage_near_value` | 7 | 30 |  |
| `npc_damage_near_value_titanarmor` | 100 |  |  |
| `npc_max_burst` | 1 |  |  |
| `npc_max_engage_range` | 2500 | 8000 |  |
| `npc_max_engage_range_heavy_armor` | 2500 | 8000 |  |
| `npc_max_range` | 2800 | 8000 |  |
| `npc_min_burst` | 1 |  |  |
| `npc_min_engage_range` | 500 |  |  |
| `npc_min_engage_range_heavy_armor` | 750 | 500 |  |
| `npc_min_range` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 4.0 | 3.0 |  |
| `npc_rest_time_between_bursts_min` | 2.0 |  |  |
| `npc_suppress_lsp_allowed` | 0 |  |  |
| `proficiency_average_spreadscale` | 3.0 | 2.2 |  |
| `proficiency_good_spreadscale` | 2.0 |  |  |
| `proficiency_poor_spreadscale` | 3.0 |  |  |
| `proficiency_very_good_spreadscale` | 1.5 |  |  |

**其他**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `is_sniper` | 1 |  |  |


