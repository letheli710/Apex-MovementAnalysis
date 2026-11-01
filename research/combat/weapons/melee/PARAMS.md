# 近战：参数全表（自动生成）

由 `weapons/_tools/gen-params.mjs` 从 `research-src/s21-platform/scripts/weapons/*.txt` 生成，不要手改。`L` 是行号，字段名就是来源字段。全部是 S21 数据文件里的值；S3 dedi 的差异看同目录 `SYSTEM.md`。

## 拳头（持握）（`weapons/mp_weapon_melee_survival.txt`）

**射击**：`fire_mode` automatic (L12)；`is_semi_auto` 1 (L13)

**弹药**：`ammo_clip_size` 0 (L19)；`ammo_default_total` 0 (L20)；`ammo_stockpile_max` 0 (L21)；`reload_enabled` 0 (L32)

**时间**：`zoom_fov` 70 (L25)；`deployfirst_time` 1.250000 (L82)

**伤害**：`melee_angle` 30 (L90)；`melee_attack_animtime` 0 (L91)；`melee_damage` 30 (L92)；`melee_damage_heavyarmor` 30 (L93)；`melee_lunge_no_target_range` 60 (L94)；`melee_lunge_target_angle` 30 (L95)；`melee_lunge_target_range` 60 (L96)；`melee_lunge_time` 0.350000 (L97)；`melee_range` 40 (L98)；`melee_knockback_velocity_magnitude` 350 (L99)

**移动**：`primary_fire_does_not_block_sprint` 1 (L17)；`move_speed_modifier` 1.150000 (L27)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `pariah_ads_melee` | 107 | `zoom_fov` 60；`ads_move_speed_scale` 1.498500 |
| `seer_heartbeat_sensor_active` | 116 | `move_speed_modifier` 0.767384 |
| `vantage_ads_melee` | 123 | `zoom_fov` 26.275600；`ads_move_speed_scale` 0.950000 |
| `proto_door_kick` | 134 | `impulse_force` 20000 |

## 拳头（出招）（`weapons/melee_pilot_emptyhanded.txt`）

**射击**：`fire_mode` offhandMelee (L12)

**时间**：`deployfirst_time` 1.250000 (L47)

**伤害**：`melee_can_hit_humansized` 1 (L17)；`melee_can_hit_titans` 0 (L18)；`melee_raise_recovery_animtime_normal` 0.750000 (L19)；`melee_raise_recovery_animtime_quick` 0.400000 (L20)；`melee_range` 60 (L21)；`melee_rumble_on_hit` pilot_melee_hit (L22)；`melee_rumble_on_hit_partial` pilot_melee_hit_partial (L23)；`melee_freezelook_on_hit` 0.250000 (L24)；`damage_flags` DF_MELEE \| DF_KNOCK_BACK (L25)；`impulse_force` 0 (L27)；`melee_anim_1p` ACT_VM_MELEE_ATTACK2 (L30)；`melee_angle` 30 (L54)；`melee_attack_animtime` 0 (L55)；`melee_damage` 30 (L56)；`melee_damage_heavyarmor` 30 (L57)；`melee_lunge_no_target_range` 60 (L58)；`melee_lunge_target_angle` 30 (L59)；`melee_lunge_target_range` 60 (L60)；`melee_lunge_time` 0.350000 (L61)；`melee_knockback_velocity_magnitude` 350 (L62)

**后坐**：`viewkick_spring` melee (L32)；`viewkick_pitch_base` -1.750000 (L33)；`viewkick_pitch_random` 0.750000 (L34)；`viewkick_pitch_softScale` 2.300000 (L35)；`viewkick_pitch_hardScale` 2.500000 (L36)；`viewkick_yaw_base` 1.000000 (L37)；`viewkick_yaw_random` 0.380000 (L38)；`viewkick_yaw_softScale` 2.380000 (L39)；`viewkick_yaw_hardScale` 2.500000 (L40)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `data_knife` | 70 | `damage_flags` DF_BULLET；`viewkick_pitch_base` -0.500000；`viewkick_pitch_random` 0.750000；`viewkick_pitch_softScale` 1.300000；`viewkick_pitch_hardScale` 1.500000；`viewkick_yaw_base` 0.500000；`viewkick_yaw_random` 0.380000；`viewkick_yaw_softScale` 2.380000；`viewkick_yaw_hardScale` 2.500000 |
| `proto_door_kick` | 114 | `impulse_force` 20000 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`disable_lunge`、`shadow_form_hands`、`revenant_shadow_form_melee`

## Titan Sword（`weapons/mp_weapon_titan_sword.txt`）

**射击**：`fire_mode` automatic (L9)；`is_semi_auto` 0 (L10)；`fire_rate` 3 (L83)

**弹药**：`ammo_clip_size` 150 (L41)；`ammo_stockpile_max` 150 (L42)；`ammo_per_shot` 150 (L43)；`ammo_default_total` 0 (L44)；`ammo_drains_to_empty_on_fire` 0 (L45)；`ammo_no_remove_from_clip` 0 (L46)；`ammo_no_remove_from_stockpile` 0 (L47)；`uses_ammo_pool` 0 (L48)；`ammo_min_to_fire` 1 (L49)；`regen_ammo_refill_rate` 10 (L50)；`regen_ammo_refill_start_delay` 0.000000 (L51)；`reload_enabled` 0 (L52)；`empty_reload_only` 1 (L56)

**时间**：`reload_time` 2.330000 (L53)；`reloadempty_time` 2.330000 (L54)；`deployfirst_time` 2.150000 (L122)；`zoom_fov` 70 (L154)

**伤害**：`melee_block_scale` 0.150000 (L61)；`melee_block_scale_super` 0.050000 (L62)；`melee_block_min_damage` 1 (L63)；`melee_block_max_damage` 999 (L64)；`melee_block_charge_scale` 0.300000 (L65)；`melee_block_sword_knockback` 1150.000000 (L66)；`melee_block_sword_slow` 0.650000 (L67)；`melee_can_hit_humansized` 1 (L84)；`melee_can_hit_titans` 1 (L85)；`melee_angle` 80 (L86)；`melee_range` 100 (L87)；`melee_attack_animtime` 0.500000 (L88)；`melee_raise_recovery_animtime_normal` 0.200000 (L89)；`melee_raise_recovery_animtime_quick` 0.200000 (L90)；`melee_damage` 25 (L91)；`melee_damage_heavyarmor` 25 (L92)；`melee_knockback_velocity_magnitude` 150 (L93)；`melee_freezelook_on_hit` 0.250000 (L94)；`melee_anim_1p` ACT_VM_MELEE_LIGHT (L95)；`melee_anim_3p` ACT_MP_MELEE_LIGHT (L96)；`melee_allow_held` 1 (L97)；`melee_lunge_time` 0.400000 (L98)；`melee_lunge_target_range` 100 (L99)；`melee_lunge_target_angle` 45 (L100)；`melee_lunge_no_target_range` 0 (L101)；`damage_flags` DF_MELEE \| DF_KNOCK_BACK \| DF_GIB \| DF_EXPLOSION \| DF_RAGDOLL (L102)；`impulse_force` 5000 (L104)

**弹道**：`projectile_lifetime` 0.100000 (L26)；`projectile_launch_speed` 1500 (L27)；`projectile_gravity_scale` 0 (L28)；`bolt_hitsize` 12.000000 (L29)

**后坐**：`viewkick_spring` pistol (L107)；`viewkick_pitch_base` 0.000000 (L108)；`viewkick_pitch_random` 0.000000 (L109)；`viewkick_pitch_softScale` 0.000000 (L110)；`viewkick_pitch_hardScale` 0.000000 (L111)；`viewkick_yaw_base` 0.000000 (L112)；`viewkick_yaw_random` 0.000000 (L113)；`viewkick_yaw_softScale` 0.000000 (L114)；`viewkick_yaw_hardScale` 0.000000 (L115)

**充能 / 热**：`charge_time` 2.000000 (L38)

**移动**：`primary_fire_does_not_block_sprint` 1 (L11)；`ads_move_speed_scale` 1 (L33)；`move_speed_modifier` 1.150000 (L155)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `super` | 198 | `move_speed_modifier` *1.4 |
| `slam` | 218 | `melee_damage_heavyarmor` 60 |
| `heavy_melee` | 237 | `fire_rate` 3；`melee_damage_heavyarmor` 60 |
| `launcher` | 258 | `fire_rate` 3；`melee_damage_heavyarmor` 40 |
| `pariah_ads_melee` | 281 | `zoom_fov` 60；`ads_move_speed_scale` 1.498500 |
| `seer_heartbeat_sensor_active` | 290 | `move_speed_modifier` 0.767384 |
| `vantage_ads_melee` | 297 | `zoom_fov` 70；`ads_move_speed_scale` 1 |
| `proto_door_kick` | 308 | `impulse_force` 20000 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`infinite_ammo_clips`、`blocking`、`slam_ready`、`super_melee`

## Power Sword（`weapons/mp_weapon_power_sword.txt`）

**射击**：`fire_mode` automatic (L9)；`is_semi_auto` 0 (L10)；`fire_rate` 3 (L60)

**弹药**：`ammo_default_total` 0 (L44)；`ammo_clip_size` 100 (L45)；`ammo_stockpile_max` 100 (L46)；`ammo_min_to_fire` 0 (L47)；`ammo_per_shot` 0 (L48)；`ammo_drains_to_empty_on_fire` 0 (L49)；`ammo_no_remove_from_clip` 0 (L50)；`ammo_no_remove_from_stockpile` 0 (L51)；`uses_ammo_pool` 0 (L52)；`regen_ammo_refill_rate` 0.500000 (L55)；`regen_ammo_refill_start_delay` 0.000000 (L56)；`reload_enabled` 0 (L57)；`empty_reload_only` 0 (L59)

**时间**：`deployfirst_time` 1.800000 (L105)；`zoom_fov` 70 (L179)；`lower_time` 0.300000 (L212)；`holster_time` 0.300000 (L213)

**伤害**：`melee_can_hit_humansized` 1 (L61)；`melee_can_hit_titans` 1 (L62)；`melee_angle` 80 (L63)；`melee_range` 150 (L64)；`melee_attack_animtime` 0.500000 (L65)；`melee_raise_recovery_animtime_normal` 0.200000 (L66)；`melee_raise_recovery_animtime_quick` 0.200000 (L67)；`melee_damage` 40 (L68)；`melee_damage_heavyarmor` 40 (L69)；`melee_knockback_velocity_magnitude` 150 (L70)；`melee_freezelook_on_hit` 0.250000 (L71)；`melee_anim_1p` ACT_VM_MELEE_ATTACK2 (L72)；`melee_anim_3p` ACT_MP_MELEE_LIGHT (L73)；`melee_allow_held` 0 (L74)；`melee_lunge_time` 0.400000 (L75)；`melee_lunge_target_range` 200 (L76)；`melee_lunge_target_angle` 60 (L77)；`melee_lunge_no_target_range` 0 (L78)；`damage_flags` DF_MELEE \| DF_KNOCK_BACK \| DF_GIB \| DF_EXPLOSION \| DF_RAGDOLL (L79)；`melee_block_scale` 0.150000 (L82)；`melee_block_scale_super` 0.050000 (L83)；`melee_block_min_damage` 1 (L84)；`melee_block_max_damage` 999 (L85)；`melee_block_charge_scale` 0.300000 (L86)；`melee_block_sword_knockback` 1150.000000 (L87)；`melee_block_sword_slow` 0.650000 (L88)；`explosion_inner_radius` 52 (L154)；`explosionradius` 180 (L155)；`impulse_force` 5000 (L156)；`explosion_damage` 45 (L158)；`damage_near_value` 25 (L160)；`damage_far_value` 25 (L161)；`damage_near_distance` 2000 (L165)；`damage_far_distance` 2500 (L166)

**弹道**：`projectile_lifetime` 10.000000 (L130)；`projectile_launch_speed` 1700 (L131)；`projectile_gravity_scale` 0.000000 (L132)；`bolt_hitsize` 0.000000 (L133)

**后坐**：`viewkick_spring` pistol (L91)；`viewkick_pitch_base` 0.000000 (L92)；`viewkick_pitch_random` 0.000000 (L93)；`viewkick_pitch_softScale` 0.000000 (L94)；`viewkick_pitch_hardScale` 0.000000 (L95)；`viewkick_yaw_base` 0.000000 (L96)；`viewkick_yaw_random` 0.000000 (L97)；`viewkick_yaw_softScale` 0.000000 (L98)；`viewkick_yaw_hardScale` 0.000000 (L99)

**移动**：`primary_fire_does_not_block_sprint` 1 (L12)；`ads_move_speed_scale` 1 (L38)；`move_speed_modifier` 1.150000 (L180)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `blocking_util` | 219 | `regen_ammo_refill_rate` 0 |
| `ultimate` | 227 | `regen_ammo_refill_rate` 0 |
| `charging` | 234 | `regen_ammo_refill_rate` 7 |
| `seer_heartbeat_sensor_melee` | 252 | `zoom_fov` 60；`ads_move_speed_scale` 1.498500 |
| `vantage_ads_melee` | 263 | `zoom_fov` 26.275600；`ads_move_speed_scale` 0.950000 |
| `loba_ads_melee` | 276 | `zoom_fov` 60 |
| `pas_extra_melee_damage` | 290 | `melee_damage_heavyarmor` ++40 |
| `proto_door_kick` | 297 | `impulse_force` 20000 |
| `matchmod_bonus_speed` | 313 | `move_speed_modifier` *2.0；`reload_time` *0.50；`reload_time_late1` *0.50；`reload_time_late2` *0.50；`reload_time_late3` *0.50；`reload_time_late4` *0.50；`reload_time_late5` *0.50；`reloadempty_time` *0.50；`reloadempty_time_late1` *0.50；`reloadempty_time_late2` *0.50；`reloadempty_time_late3` *0.50；`reloadempty_time_late4` *0.50；`reloadempty_time_late5` *0.50；`charge_cooldown_time` *0.50；`charge_overheat_cooldown_time` *0.50；`charge_overheat_cooldown_time_late1` *0.50；`charge_overheat_cooldown_time_late2` *0.50；`charge_overheat_cooldown_time_late3` *0.50 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`force_zoom_in`、`force_zoom_out`、`pas_extra_melee_knockback`、`proto_melee_knocked`

## Wraith 传家宝（持握，代表）（`weapons/mp_weapon_wraith_kunai_primary.txt`）

**射击**：`fire_mode` automatic (L77)；`is_semi_auto` 1 (L78)

**弹药**：`ammo_clip_size` 0 (L84)；`ammo_default_total` 0 (L85)；`ammo_stockpile_max` 0 (L86)；`reload_enabled` 0 (L93)

**时间**：`deployfirst_time` 1.900000 (L19)；`zoom_fov` 70 (L88)

**伤害**：`melee_angle` 30 (L105)；`melee_attack_animtime` 0 (L106)；`melee_damage` 30 (L107)；`melee_damage_heavyarmor` 30 (L108)；`melee_lunge_no_target_range` 60 (L109)；`melee_lunge_target_angle` 30 (L110)；`melee_lunge_target_range` 60 (L111)；`melee_lunge_time` 0.350000 (L112)；`melee_range` 40 (L113)；`melee_knockback_velocity_magnitude` 350 (L114)

**移动**：`primary_fire_does_not_block_sprint` 1 (L82)；`move_speed_modifier` 1.150000 (L90)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `pariah_ads_melee` | 121 | `zoom_fov` 60；`ads_move_speed_scale` 1.498500 |
| `seer_heartbeat_sensor_active` | 130 | `move_speed_modifier` 0.767384 |
| `vantage_ads_melee` | 137 | `zoom_fov` 26.275600；`ads_move_speed_scale` 0.950000 |
| `proto_door_kick` | 148 | `impulse_force` 20000 |

## Wraith 传家宝（出招，代表）（`weapons/melee_wraith_kunai.txt`）

**射击**：`fire_mode` offhandMelee (L17)

**时间**：`deployfirst_time` 1.250000 (L49)

**伤害**：`melee_can_hit_humansized` 1 (L20)；`melee_can_hit_titans` 0 (L21)；`melee_raise_recovery_animtime_normal` 0.750000 (L22)；`melee_raise_recovery_animtime_quick` 0.400000 (L23)；`melee_range` 60 (L24)；`melee_rumble_on_hit` pilot_melee_hit (L25)；`melee_rumble_on_hit_partial` pilot_melee_hit_partial (L26)；`melee_freezelook_on_hit` 0.250000 (L27)；`damage_flags` DF_MELEE \| DF_KNOCK_BACK (L28)；`impulse_force` 0 (L29)；`melee_anim_1p` ACT_VM_MELEE_ATTACK2 (L32)；`melee_angle` 30 (L56)；`melee_attack_animtime` 0 (L57)；`melee_damage` 30 (L58)；`melee_damage_heavyarmor` 30 (L59)；`melee_lunge_no_target_range` 60 (L60)；`melee_lunge_target_angle` 30 (L61)；`melee_lunge_target_range` 60 (L62)；`melee_lunge_time` 0.350000 (L63)；`melee_knockback_velocity_magnitude` 350 (L64)

**后坐**：`viewkick_spring` melee (L34)；`viewkick_pitch_base` -1.750000 (L35)；`viewkick_pitch_random` 0.750000 (L36)；`viewkick_pitch_softScale` 2.300000 (L37)；`viewkick_pitch_hardScale` 2.500000 (L38)；`viewkick_yaw_base` 1.000000 (L39)；`viewkick_yaw_random` 0.380000 (L40)；`viewkick_yaw_softScale` 2.380000 (L41)；`viewkick_yaw_hardScale` 2.500000 (L42)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `data_knife` | 72 | `damage_flags` DF_BULLET；`viewkick_pitch_base` -0.500000；`viewkick_pitch_random` 0.750000；`viewkick_pitch_softScale` 1.300000；`viewkick_pitch_hardScale` 1.500000；`viewkick_yaw_base` 0.500000；`viewkick_yaw_random` 0.380000；`viewkick_yaw_softScale` 2.380000；`viewkick_yaw_hardScale` 2.500000 |
| `proto_door_kick` | 116 | `impulse_force` 20000 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`disable_lunge`、`shadow_form_hands`、`revenant_shadow_form_melee`

