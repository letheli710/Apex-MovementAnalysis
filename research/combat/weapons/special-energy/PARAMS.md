# 特殊能量武器（模式 / 活动）：参数全表（自动生成）

由 `weapons/_tools/gen-params.mjs` 从 `research-src/s21-platform/scripts/weapons/*.txt` 生成，不要手改。`L` 是行号，字段名就是来源字段。全部是 S21 数据文件里的值；S3 dedi 的差异看同目录 `SYSTEM.md`。

## Buster Rifle（`weapons/mp_weapon_buster_rifle.txt`）

**射击**：`fire_mode` automatic (L11)；`is_semi_auto` 1 (L12)；`OnWeaponPrimaryAttack` BusterRifle_OnWeaponPrimaryAttack (L15)；`fire_rate` 5.000000 (L67)；`blast_pattern_default_scale` 2.250000 (L82)；`primary_attack_ignores_spread` 1 (L83)；`rechamber_time` 1.600000 (L191)

**弹药**：`ammo_clip_size` 4 (L59)；`ammo_stockpile_max` 12 (L60)；`ammo_default_total` 16 (L61)；`ammo_min_to_fire` 1 (L62)；`reload_enabled` 1 (L63)；`ammo_no_remove_from_stockpile` 0 (L64)；`uses_ammo_pool` 0 (L65)；`empty_reload_only` 0 (L69)

**时间**：`deployfirst_time` 0.800000 (L71)；`deploy_time` 0.800000 (L72)；`holster_time` 0.500000 (L73)；`raise_time` 0.700000 (L74)；`lower_time` 0.400000 (L75)；`zoom_time_in` 0.580000 (L153)；`zoom_time_out` 0.550000 (L154)；`zoom_fov` 13.312800 (L155)；`reload_time` 3.200000 (L184)；`reload_time_late1` 1.950000 (L185)；`reloadempty_time` 4.300000 (L187)；`reloadempty_time_late1` 3.130000 (L188)

**伤害**：`damage_type` bullet (L56)；`impulse_force` 1000 (L57)；`allow_headshots` 0 (L70)；`damage_near_value` 60 (L92)；`damage_far_value` 60 (L93)；`damage_very_far_value` 60 (L94)；`damage_near_distance` 3937 (L98)；`damage_far_distance` 5906 (L99)；`damage_very_far_distance` 15748 (L100)；`damage_leg_scale` 1.000000 (L101)；`damage_headshot_scale` 1.250000 (L102)；`headshot_distance` 11811 (L103)；`critical_hit_damage_scale` 1.250000 (L104)；`damage_flags` DF_SNIPER \| DF_GIB (L105)；`pass_through_depth` 0 (L106)；`npc_damage_near_value` 30 (L107)；`npc_damage_far_value` 35 (L108)；`npc_damage_near_distance` 200 (L111)；`npc_damage_far_distance` 15000 (L112)；`npc_min_engage_range` 100 (L113)；`npc_max_engage_range` 4000 (L114)；`npc_min_range` 0 (L117)；`npc_max_range` 5000 (L118)；`npc_min_burst` 1 (L119)；`npc_max_burst` 1 (L120)；`npc_rest_time_between_bursts_min` 2.500000 (L121)；`npc_rest_time_between_bursts_max` 2.500000 (L122)；`pass_through_damage_preserved_scale` 0.800000 (L168)；`critical_hit` 1 (L246)；`damage_shield_scale` 1 (L258)

**弹道**：`ballistic_type` hitscan (L58)；`projectile_launch_speed` 29500 (L173)；`bolt_hitsize_grow1_time` 0.133000 (L174)；`bolt_hitsize_grow1_size` 0.330000 (L175)；`bolt_hitsize_grow2_time` 0.267000 (L176)；`bolt_hitsize_grow2_size` 1.250000 (L177)；`bolt_hitsize_growfinal_lerptime` 0.400000 (L178)；`bolt_hitsize_growfinal_size` 2.000000 (L179)；`projectile_drag_coefficient` 0.003300 (L261)；`bolt_gravity_enabled` 1 (L262)；`projectile_gravity_scale` 1.400000 (L263)；`bolt_zero_distance` 1968.500000 (L264)；`bolt_hitsize` 0.000000 (L265)；`projectile_lifetime` 6.000000 (L266)；`projectile_ricochet_max_count` 0 (L374)；`projectile_bounce_damage_reduction_scale` 0.500000 (L376)；`projectile_speed_reduction_factor` 0.720000 (L377)

**扩散**：`spread_stand_hip` 4.000000 (L84)；`spread_stand_hip_run` 5.500000 (L85)；`spread_stand_hip_sprint` 6.000000 (L86)；`spread_crouch_hip` 3.250000 (L87)；`spread_air_hip` 6.000000 (L88)；`spread_stand_ads` 0.000000 (L89)；`spread_crouch_ads` 0.000000 (L90)；`spread_air_ads` 0.000000 (L91)；`spread_kick_on_fire_stand_hip` 1 (L272)；`spread_kick_on_fire_crouch_hip` 1 (L273)；`spread_kick_on_fire_air_hip` 1 (L274)；`spread_max_kick_stand_hip` 12.000000 (L275)；`spread_max_kick_crouch_hip` 10.000000 (L276)；`spread_max_kick_air_hip` 12.000000 (L277)；`spread_decay_rate` 4 (L278)；`spread_decay_delay` 0.100000 (L279)

**后坐**：`viewkick_spring` sniper (L192)；`viewkick_pitch_base` -1.610000 (L193)；`viewkick_pitch_random` 1.120000 (L194)；`viewkick_perm_pitch_base` 0.000000 (L195)；`viewkick_perm_pitch_random` 0.000000 (L196)；`viewkick_perm_pitch_random_innerexclude` 0.000000 (L197)；`viewkick_pitch_softScale` 1.000000 (L198)；`viewkick_pitch_hardScale` 0.900000 (L199)；`viewkick_yaw_base` -1.050000 (L200)；`viewkick_yaw_random` 1.140000 (L201)；`viewkick_perm_yaw_base` 0.000000 (L202)；`viewkick_perm_yaw_random` 0.000000 (L203)；`viewkick_perm_yaw_random_innerexclude` 0.000000 (L204)；`viewkick_yaw_softScale` 1.000000 (L205)；`viewkick_yaw_hardScale` 0.500000 (L206)

**充能 / 热**：`charge_time` 0.300000 (L76)；`charge_require_input` 1 (L77)；`charge_cooldown_time` 0.150000 (L78)；`charge_cooldown_delay` 0.100000 (L79)；`charge_attack_min_charge_required` 1.000000 (L80)

**移动**：`ads_move_speed_scale` 0.350000 (L152)；`primary_fire_does_not_block_sprint` 0 (L245)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `beam_charge` | 418 | `charge_time` 2.100000；`charge_require_input` 0；`charge_cooldown_time` 0.010000；`charge_cooldown_delay` 0.000000；`charge_end_forces_fire` 1；`charge_attack_min_charge_required` 1.000000；`charge_sound_1p` weapon_busterrifle_beam_charge_1p；`charge_sound_stop_when_full` 1；`charge_sound_seek_to_charge_fraction` 1；`charge_drain_sound_1p` weapon_busterrifle_winddown_1p；`charge_drain_sound_3p` weapon_busterrifle_winddown_3p；`charge_drain_sound_stop_when_empty` 1；`charge_drain_sound_seek_to_charge_fraction` 1；`charge_effect_3p` P_wpn_buster_charged_charge_3P；`viewkick_spring` titan_arc；`viewkick_pitch_base` -2.000000；`viewkick_pitch_random` 0.500000；`viewkick_pitch_softScale` 0.300000；`viewkick_pitch_hardScale` 2.000000；`viewkick_yaw_base` 0；`viewkick_yaw_random` 0.500000；`viewkick_yaw_softScale` 1；`viewkick_yaw_hardScale` 0 |
| `beam_sequence` | 476 | `reload_enabled` 0 |
| `amped_damage` | 497 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `ferro_damage` | 512 | `sustained_laser_damage_scale` *2；`damage_near_value` *0.5；`damage_far_value` *0.5；`damage_very_far_value` *0.5；`damage_near_value_titanarmor` *0.5；`damage_far_value_titanarmor` *0.5；`damage_very_far_value_titanarmor` *0.5 |
| `optic_ranged_aog_variable` | 527 | `zoom_time_in` 0.430000；`zoom_time_out` 0.370000；`zoom_fov` 38.590698 |
| `elevator_shooter` | 561 | `spread_air_hip` *0.8；`spread_air_hip_moving` 10.000000；`spread_air_ads` 0.250000；`spread_air_ads_moving` 8.000000；`spread_kick_on_fire_air_hip` 1；`spread_max_kick_air_hip` *0.8；`spread_kick_on_fire_air_ads` 0；`spread_max_kick_air_ads` 0；`viewdrift_ads_air_scale_pitch` 0.400000；`viewdrift_ads_air_scale_yaw` 0.300000；`viewdrift_hipfire_air_scale_pitch` 0.000000；`viewdrift_hipfire_air_scale_yaw` 0.000000 |
| `double_jump_spread` | 579 | `spread_air_hip` *1.15；`spread_air_hip_moving` *1.15；`spread_air_ads` *1.15；`spread_air_ads_moving` *1.15 |
| `auto_loader` | 589 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload` | 627 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload_fast_heals` | 649 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `matchmod_bonus_speed` | 671 | `move_speed_modifier` *2.0；`reload_time` *0.50；`reload_time_late1` *0.50；`reload_time_late2` *0.50；`reload_time_late3` *0.50；`reload_time_late4` *0.50；`reload_time_late5` *0.50；`reloadempty_time` *0.50；`reloadempty_time_late1` *0.50；`reloadempty_time_late2` *0.50；`reloadempty_time_late3` *0.50；`reloadempty_time_late4` *0.50；`reloadempty_time_late5` *0.50；`charge_cooldown_time` *0.50；`charge_overheat_cooldown_time` *0.50；`charge_overheat_cooldown_time_late1` *0.50；`charge_overheat_cooldown_time_late2` *0.50；`charge_overheat_cooldown_time_late3` *0.50 |
| `optic_ranged_hcog` | 694 | `zoom_fov` 26.275600 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`wildcard_event_weapon`、`standard_firing`、`beam_firing`、`beam_launch`、`beam_scan_increased`、`crate`、`optic_toggle`、`innate_threat_vision`、`hopup_ultimate_accelerator`、`dormant_hopup_ultimate_accelerator`

## Ray Gun（`weapons/mp_weapon_raygun.txt`）

**射击**：`fire_mode` automatic (L11)；`is_semi_auto` 0 (L12)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_RayGun (L17)；`fire_rate` 3.000000 (L88)

**弹药**：`ammo_pool_type` highcal (L7)；`ammo_clip_size` 20 (L42)；`ammo_min_to_fire` 1 (L46)；`ammo_default_total` 160 (L47)；`ammo_stockpile_max` 160 (L48)；`ammo_no_remove_from_stockpile` 1 (L49)；`uses_ammo_pool` 0 (L51)；`reload_enabled` 1 (L207)；`empty_reload_only` 0 (L209)

**时间**：`reload_time` 2.500000 (L89)；`reload_time_late1` 1.750000 (L90)；`reloadempty_time` 2.100000 (L92)；`reloadempty_time_late1` 1.750000 (L93)；`deploy_time` 0.400000 (L95)；`holster_time` 0.360000 (L96)；`raise_time` 0.315000 (L97)；`lower_time` 0.270000 (L98)；`zoom_time_in` 0.180000 (L99)；`zoom_time_out` 0.160000 (L100)；`deployfirst_time` 1.450000 (L158)；`zoom_fov` 60 (L201)

**伤害**：`damage_flags` DF_BULLET \| DF_KNOCK_BACK (L14)；`damage_type` bullet (L41)；`damage_near_value` 90 (L53)；`damage_far_value` 90 (L54)；`damage_very_far_value` 90 (L55)；`damage_headshot_scale` 2.150000 (L60)；`damage_near_distance` 800 (L61)；`damage_far_distance` 1300 (L62)；`damage_very_far_distance` 1800 (L63)；`npc_damage_near_value` 10 (L64)；`npc_damage_far_value` 8 (L65)；`npc_damage_near_distance` 1000 (L66)；`npc_damage_far_distance` 1200 (L67)；`npc_min_engage_range` 0 (L68)；`npc_max_engage_range` 1000 (L69)；`npc_min_range` 0 (L72)；`npc_max_range` 8000 (L73)；`npc_min_burst` 1 (L74)；`npc_max_burst` 1 (L75)；`npc_rest_time_between_bursts_min` 0.250000 (L76)；`npc_rest_time_between_bursts_max` 0.600000 (L77)；`headshot_distance` 10000 (L103)；`impulse_force` 3000 (L104)；`damage_shield_scale` 1 (L193)；`damage_leg_scale` 0.900000 (L194)；`critical_hit` 1 (L195)；`critical_hit_damage_scale` 2 (L196)；`allow_headshots` 1 (L211)；`pass_through_depth` 0 (L254)；`pass_through_damage_preserved_scale` 1.000000 (L255)

**弹道**：`projectile_launch_speed` 2200 (L101)；`projectile_lifetime` 5.000000 (L102)；`projectile_gravity_scale` 0 (L163)；`projectile_drag_coefficient` 0.002500 (L243)；`projectile_ricochet_max_count` 0 (L248)；`bolt_hitsize` 10.000000 (L250)；`bolt_gravity_enabled` 0 (L251)；`bolt_zero_distance` 1378.000000 (L252)

**扩散**：`spread_stand_hip` 2.400000 (L144)；`spread_stand_hip_run` 3.000000 (L145)；`spread_stand_hip_sprint` 4.000000 (L146)；`spread_crouch_hip` 1.500000 (L147)；`spread_air_hip` 6.000000 (L148)；`spread_kick_on_fire_stand_hip` 2.500000 (L149)；`spread_kick_on_fire_crouch_hip` 2.000000 (L150)；`spread_kick_on_fire_air_hip` 3.000000 (L151)；`spread_max_kick_stand_hip` 5.500000 (L152)；`spread_max_kick_crouch_hip` 3.000000 (L153)；`spread_max_kick_air_hip` 4.500000 (L154)；`spread_decay_rate` 11.000000 (L155)；`spread_decay_delay` 0.260000 (L156)；`spread_stand_ads` 0.000000 (L232)；`spread_crouch_ads` 0.000000 (L233)；`spread_air_ads` 2.000000 (L234)；`spread_moving_increase_rate` 5.500000 (L235)；`spread_moving_decay_rate` 12 (L236)；`spread_max_kick_stand_ads` 0.000000 (L237)；`spread_max_kick_crouch_ads` 0.000000 (L238)；`spread_max_kick_air_ads` 0.000000 (L239)；`spread_kick_on_fire_stand_ads` 0.000000 (L240)；`spread_kick_on_fire_crouch_ads` 0.000000 (L241)；`spread_kick_on_fire_air_ads` 0.000000 (L242)

**后坐**：`viewkick_spring` wingman (L105)；`viewkick_pitch_base` -4.400000 (L106)；`viewkick_pitch_random` 0.800000 (L107)；`viewkick_pitch_softScale` 0.650000 (L108)；`viewkick_pitch_hardScale` 0.350000 (L109)；`viewkick_yaw_base` -0.600000 (L110)；`viewkick_yaw_random` -0.500000 (L111)；`viewkick_yaw_softScale` 0.800000 (L112)；`viewkick_yaw_hardScale` 0.400000 (L113)；`viewkick_perm_pitch_base` 0.000000 (L123)；`viewkick_perm_pitch_random` 0.000000 (L124)；`viewkick_perm_yaw_base` 0.000000 (L125)；`viewkick_perm_yaw_random` 0.000000 (L126)；`viewkick_air_scale_ads` 2.000000 (L214)

**移动**：`ads_move_speed_scale` 1.000000 (L202)；`primary_fire_does_not_block_sprint` 0 (L212)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `survival_finite_ammo` | 379 | `ammo_default_total` 0；`ammo_stockpile_max` 20；`ammo_no_remove_from_stockpile` 0；`low_ammo_fraction` 0.3；`uses_ammo_pool` 1 |
| `infinite_ammo` | 388 | `ammo_min_to_fire` 0；`ammo_no_remove_from_clip` 1；`ammo_no_remove_from_stockpile` 1；`low_ammo_fraction` 0.0 |
| `fast_reload_mod` | 402 | `reload_time` 1.400000 |
| `overloaded_ammo` | 408 | `ammo_clip_size` ++2 |
| `hopup_headshot_dmg` | 414 | `damage_headshot_scale` 2.250000 |
| `highcal_mag_l1` | 425 | `ammo_clip_size` 24 |
| `highcal_mag_l2` | 431 | `ammo_clip_size` 28 |
| `highcal_mag_l3` | 437 | `ammo_clip_size` 32 |
| `highcal_mag_l4` | 443 | `ammo_clip_size` 32 |
| `hopup_quickdraw_holster` | 449 | `zoom_time_in` *0.7；`zoom_time_out` *0.7；`deploy_time` *0.7；`holster_time` *0.7；`raise_time` *0.75；`lower_time` *0.75；`spread_stand_hip` *0.75；`spread_stand_hip_run` *0.9 |
| `elevator_shooter` | 462 | `spread_air_hip` *0.9；`spread_air_hip_moving` *0.9；`spread_air_ads` *0.9；`spread_air_ads_moving` *0.9 |
| `optic_cq_hcog_classic` | 472 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `optic_cq_hcog_bruiser` | 497 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 38.590698 |
| `optic_cq_holosight` | 524 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `optic_cq_holosight_variable` | 551 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `optic_cq_threat` | 583 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `amped_damage` | 615 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `auto_loader` | 630 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |
| `paintball` | 647 | `reload_time` *0.75；`reload_time_late1` *0.75；`reload_time_late2` *0.75；`reload_time_late3` *0.75；`reload_time_late4` *0.75；`reload_time_late5` *0.75；`reloadempty_time` *0.75；`reloadempty_time_late1` *0.75；`reloadempty_time_late2` *0.75；`reloadempty_time_late3` *0.75；`reloadempty_time_late4` *0.75；`reloadempty_time_late5` *0.75 |
| `laser_sight_l1` | 669 | `spread_stand_hip` *0.80；`spread_stand_hip_run` *0.80；`spread_stand_hip_sprint` *0.80；`spread_crouch_hip` *0.80；`spread_air_hip` *0.80；`spread_moving_increase_rate` *0.85；`spread_moving_decay_rate` *1.15；`spread_decay_rate` *1.20；`spread_decay_delay` *0.80；`spread_max_kick_stand_hip` *0.80；`spread_max_kick_crouch_hip` *0.80；`spread_max_kick_air_hip` *0.80；`spread_kick_on_fire_stand_hip` *0.80；`spread_kick_on_fire_crouch_hip` *0.80；`spread_kick_on_fire_air_hip` *0.80 |
| `laser_sight_l2` | 690 | `spread_stand_hip` *0.70；`spread_stand_hip_run` *0.70；`spread_stand_hip_sprint` *0.70；`spread_crouch_hip` *0.70；`spread_air_hip` *0.70；`spread_moving_increase_rate` *0.80；`spread_moving_decay_rate` *1.20；`spread_decay_rate` *1.30；`spread_decay_delay` *0.70；`spread_max_kick_stand_hip` *0.70；`spread_max_kick_crouch_hip` *0.70；`spread_max_kick_air_hip` *0.70；`spread_kick_on_fire_stand_hip` *0.70；`spread_kick_on_fire_crouch_hip` *0.70；`spread_kick_on_fire_air_hip` *0.70 |
| `laser_sight_l3` | 711 | `spread_stand_hip` *0.60；`spread_stand_hip_run` *0.60；`spread_stand_hip_sprint` *0.60；`spread_crouch_hip` *0.60；`spread_air_hip` *0.60；`spread_moving_increase_rate` *0.75；`spread_moving_decay_rate` *1.25；`spread_decay_rate` *1.40；`spread_decay_delay` *0.60；`spread_max_kick_stand_hip` *0.60；`spread_max_kick_crouch_hip` *0.60；`spread_max_kick_air_hip` *0.60；`spread_kick_on_fire_stand_hip` *0.60；`spread_kick_on_fire_crouch_hip` *0.60；`spread_kick_on_fire_air_hip` *0.60 |
| `hopup_paintball_elite` | 732 | `ammo_clip_size` ++2；`zoom_time_in` *0.7；`zoom_time_out` *0.7；`deploy_time` *0.7；`holster_time` *0.7；`raise_time` *0.75；`lower_time` *0.75；`spread_stand_hip` *0.75；`spread_stand_hip_run` *0.9；`spread_stand_hip_sprint` *0.75；`spread_crouch_hip` *0.75；`spread_air_hip` *0.75；`reload_time` *0.8；`reloadempty_time` *0.8；`reload_time_late1` *0.8；`reload_time_late2` *0.8；`reloadempty_time_late1` *0.8；`reloadempty_time_late2` *0.8 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`gold`、`hopup_smart_reload`、`dormant_hopup_paintball_elite`

## Instagib（`weapons/mp_weapon_instagib.txt`）

**射击**：`fire_mode` automatic (L11)；`is_semi_auto` 1 (L12)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_Clickweapon (L19)；`fire_rate` 2.800000 (L90)

**弹药**：`ammo_pool_type` sniper (L7)；`ammo_clip_size` 69 (L43)；`ammo_min_to_fire` 1 (L47)；`ammo_default_total` 69 (L48)；`ammo_stockpile_max` 69 (L49)；`ammo_no_remove_from_stockpile` 1 (L50)；`uses_ammo_pool` 0 (L52)；`ammo_per_shot` 1 (L54)；`reload_enabled` 1 (L210)；`empty_reload_only` 0 (L212)

**时间**：`reload_time` 2.100000 (L91)；`reload_time_late1` 1.750000 (L92)；`reloadempty_time` 2.100000 (L94)；`reloadempty_time_late1` 1.750000 (L95)；`deploy_time` 0.400000 (L97)；`holster_time` 0.360000 (L98)；`raise_time` 0.315000 (L99)；`lower_time` 0.270000 (L100)；`zoom_time_in` 0.180000 (L101)；`zoom_time_out` 0.160000 (L102)；`deployfirst_time` 1.450000 (L160)；`zoom_fov` 60 (L203)

**伤害**：`damage_flags` DF_BULLET \| DF_KNOCK_BACK (L14)；`damage_type` bullet (L42)；`damage_near_value` 50 (L56)；`damage_far_value` 50 (L57)；`damage_very_far_value` 50 (L58)；`damage_headshot_scale` 1.500000 (L63)；`damage_near_distance` 800 (L64)；`damage_far_distance` 1300 (L65)；`damage_very_far_distance` 1800 (L66)；`npc_damage_near_value` 10 (L67)；`npc_damage_far_value` 8 (L68)；`npc_damage_near_distance` 1000 (L69)；`npc_damage_far_distance` 1200 (L70)；`npc_min_engage_range` 0 (L71)；`npc_max_engage_range` 1000 (L72)；`npc_min_range` 0 (L75)；`npc_max_range` 8000 (L76)；`npc_min_burst` 1 (L77)；`npc_max_burst` 1 (L78)；`npc_rest_time_between_bursts_min` 0.250000 (L79)；`npc_rest_time_between_bursts_max` 0.600000 (L80)；`headshot_distance` 10000 (L105)；`impulse_force` 3000 (L106)；`damage_shield_scale` 1 (L195)；`damage_leg_scale` 0.900000 (L196)；`critical_hit` 1 (L197)；`critical_hit_damage_scale` 2 (L198)；`allow_headshots` 1 (L214)；`pass_through_depth` 0 (L257)；`pass_through_damage_preserved_scale` 1.000000 (L258)

**弹道**：`projectile_launch_speed` 18000 (L103)；`projectile_lifetime` 3.500000 (L104)；`projectile_gravity_scale` 1.200000 (L165)；`projectile_drag_coefficient` 0.002500 (L246)；`projectile_ricochet_max_count` 0 (L251)；`bolt_hitsize` 0.000000 (L253)；`bolt_gravity_enabled` 1 (L254)；`bolt_zero_distance` 1378.000000 (L255)

**扩散**：`spread_stand_hip` 2.400000 (L146)；`spread_stand_hip_run` 3.000000 (L147)；`spread_stand_hip_sprint` 4.000000 (L148)；`spread_crouch_hip` 1.500000 (L149)；`spread_air_hip` 6.000000 (L150)；`spread_kick_on_fire_stand_hip` 2.500000 (L151)；`spread_kick_on_fire_crouch_hip` 2.000000 (L152)；`spread_kick_on_fire_air_hip` 3.000000 (L153)；`spread_max_kick_stand_hip` 5.500000 (L154)；`spread_max_kick_crouch_hip` 3.000000 (L155)；`spread_max_kick_air_hip` 4.500000 (L156)；`spread_decay_rate` 11.000000 (L157)；`spread_decay_delay` 0.260000 (L158)；`spread_stand_ads` 0.000000 (L235)；`spread_crouch_ads` 0.000000 (L236)；`spread_air_ads` 2.000000 (L237)；`spread_moving_increase_rate` 5.500000 (L238)；`spread_moving_decay_rate` 12 (L239)；`spread_max_kick_stand_ads` 0.000000 (L240)；`spread_max_kick_crouch_ads` 0.000000 (L241)；`spread_max_kick_air_ads` 0.000000 (L242)；`spread_kick_on_fire_stand_ads` 0.000000 (L243)；`spread_kick_on_fire_crouch_ads` 0.000000 (L244)；`spread_kick_on_fire_air_ads` 0.000000 (L245)

**后坐**：`viewkick_spring` wingman (L107)；`viewkick_pitch_base` -4.400000 (L108)；`viewkick_pitch_random` 0.800000 (L109)；`viewkick_pitch_softScale` 0.650000 (L110)；`viewkick_pitch_hardScale` 0.350000 (L111)；`viewkick_yaw_base` -0.600000 (L112)；`viewkick_yaw_random` -0.500000 (L113)；`viewkick_yaw_softScale` 0.800000 (L114)；`viewkick_yaw_hardScale` 0.400000 (L115)；`viewkick_perm_pitch_base` 0.000000 (L125)；`viewkick_perm_pitch_random` 0.000000 (L126)；`viewkick_perm_yaw_base` 0.000000 (L127)；`viewkick_perm_yaw_random` 0.000000 (L128)；`viewkick_air_scale_ads` 2.000000 (L217)

**移动**：`ads_move_speed_scale` 1.000000 (L204)；`move_speed_modifier` 1.800000 (L205)；`primary_fire_does_not_block_sprint` 0 (L215)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `fast_reload_mod` | 384 | `reload_time` 1.400000 |
| `overloaded_ammo` | 390 | `ammo_clip_size` 69 |
| `hopup_headshot_dmg` | 396 | `damage_headshot_scale` 1.920000 |
| `sniper_mag_l1` | 407 | `ammo_clip_size` 69 |
| `sniper_mag_l2` | 413 | `ammo_clip_size` 69 |
| `sniper_mag_l3` | 419 | `ammo_clip_size` 69 |
| `sniper_mag_l4` | 425 | `ammo_clip_size` 69 |
| `hopup_quickdraw_holster` | 438 | `zoom_time_in` *0.7；`zoom_time_out` *0.7；`deploy_time` *0.7；`holster_time` *0.7；`raise_time` *0.75；`lower_time` *0.75；`spread_stand_hip` *0.75；`spread_stand_hip_run` *0.9 |
| `elevator_shooter` | 451 | `spread_air_hip` *0.9；`spread_air_hip_moving` *0.9；`spread_air_ads` *0.9；`spread_air_ads_moving` *0.9 |
| `optic_cq_hcog_classic` | 461 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `optic_cq_hcog_bruiser` | 486 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 38.590698 |
| `optic_cq_holosight` | 513 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `optic_cq_holosight_variable` | 540 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `optic_cq_threat` | 572 | `zoom_time_in` 0.220000；`zoom_time_out` 0.200000；`zoom_fov` 60 |
| `amped_damage` | 604 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `auto_loader` | 619 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |
| `paintball` | 636 | `reload_time` *0.75；`reload_time_late1` *0.75；`reload_time_late2` *0.75；`reload_time_late3` *0.75；`reload_time_late4` *0.75；`reload_time_late5` *0.75；`reloadempty_time` *0.75；`reloadempty_time_late1` *0.75；`reloadempty_time_late2` *0.75；`reloadempty_time_late3` *0.75；`reloadempty_time_late4` *0.75；`reloadempty_time_late5` *0.75 |
| `laser_sight_l1` | 658 | `spread_stand_hip` *0.80；`spread_stand_hip_run` *0.80；`spread_stand_hip_sprint` *0.80；`spread_crouch_hip` *0.80；`spread_air_hip` *0.80；`spread_moving_increase_rate` *0.85；`spread_moving_decay_rate` *1.15；`spread_decay_rate` *1.20；`spread_decay_delay` *0.80；`spread_max_kick_stand_hip` *0.80；`spread_max_kick_crouch_hip` *0.80；`spread_max_kick_air_hip` *0.80；`spread_kick_on_fire_stand_hip` *0.80；`spread_kick_on_fire_crouch_hip` *0.80；`spread_kick_on_fire_air_hip` *0.80 |
| `laser_sight_l2` | 679 | `spread_stand_hip` *0.70；`spread_stand_hip_run` *0.70；`spread_stand_hip_sprint` *0.70；`spread_crouch_hip` *0.70；`spread_air_hip` *0.70；`spread_moving_increase_rate` *0.80；`spread_moving_decay_rate` *1.20；`spread_decay_rate` *1.30；`spread_decay_delay` *0.70；`spread_max_kick_stand_hip` *0.70；`spread_max_kick_crouch_hip` *0.70；`spread_max_kick_air_hip` *0.70；`spread_kick_on_fire_stand_hip` *0.70；`spread_kick_on_fire_crouch_hip` *0.70；`spread_kick_on_fire_air_hip` *0.70 |
| `laser_sight_l3` | 700 | `spread_stand_hip` *0.60；`spread_stand_hip_run` *0.60；`spread_stand_hip_sprint` *0.60；`spread_crouch_hip` *0.60；`spread_air_hip` *0.60；`spread_moving_increase_rate` *0.75；`spread_moving_decay_rate` *1.25；`spread_decay_rate` *1.40；`spread_decay_delay` *0.60；`spread_max_kick_stand_hip` *0.60；`spread_max_kick_crouch_hip` *0.60；`spread_max_kick_air_hip` *0.60；`spread_kick_on_fire_stand_hip` *0.60；`spread_kick_on_fire_crouch_hip` *0.60；`spread_kick_on_fire_air_hip` *0.60 |
| `hopup_paintball_elite` | 721 | `ammo_clip_size` 69；`zoom_time_in` *0.7；`zoom_time_out` *0.7；`deploy_time` *0.7；`holster_time` *0.7；`raise_time` *0.75；`lower_time` *0.75；`spread_stand_hip` *0.75；`spread_stand_hip_run` *0.9；`spread_stand_hip_sprint` *0.75；`spread_crouch_hip` *0.75；`spread_air_hip` *0.75；`reload_time` *0.8；`reloadempty_time` *0.8；`reload_time_late1` *0.8；`reload_time_late2` *0.8；`reloadempty_time_late1` *0.8；`reloadempty_time_late2` *0.8 |
| `laser_sight_l4` | 750 | `viewkick_scale_max_hipfire` 1.000000；`spread_kick_on_fire_stand_hip` -0.250000；`spread_kick_on_fire_crouch_hip` -0.250000；`spread_kick_on_fire_air_hip` -0.300000；`spread_decay_delay` *3.0；`spread_min_kick` -3.000000；`spread_stand_hip` *0.60；`spread_stand_hip_run` *0.60；`spread_stand_hip_sprint` *0.60；`spread_crouch_hip` *0.60；`spread_air_hip` *0.60；`spread_air_hip_moving` *0.60；`spread_wallrunning` *0.60；`spread_max_kick_stand_hip` *0.60；`spread_max_kick_crouch_hip` *0.60；`spread_max_kick_air_hip` *0.01；`spread_update_hipfire_in_ads` 1 |
| `corrupted_laser` | 775 | `spread_stand_hip` *0.60；`spread_stand_hip_run` *0.60；`spread_stand_hip_sprint` *0.60；`spread_crouch_hip` *0.60；`spread_air_hip` *0.60；`spread_moving_increase_rate` *0.75；`spread_moving_decay_rate` *1.25；`spread_decay_rate` *1.40；`spread_decay_delay` *0.60；`spread_max_kick_stand_hip` *0.60；`spread_max_kick_crouch_hip` *0.60；`spread_max_kick_air_hip` *0.60；`spread_kick_on_fire_stand_hip` *0.60；`spread_kick_on_fire_crouch_hip` *0.60；`spread_kick_on_fire_air_hip` *0.60；`reload_time` *0.6；`reload_time_late1` *0.6；`reload_time_late2` *0.6；`reload_time_late3` *0.6；`reload_time_late4` *0.6；`reload_time_late5` *0.6；`reloadempty_time` *0.6；`reloadempty_time_late1` *0.6；`reloadempty_time_late2` *0.6；`reloadempty_time_late3` *0.6；`reloadempty_time_late4` *0.6；`reloadempty_time_late5` *0.6；`reloadsegment_time_loop` *0.6；`reloadsegment_time_end` *0.6；`reloadsegmentempty_time_end` *0.6；`viewkick_pitch_base` *1.6；`viewkick_pitch_random` *1.6；`viewkick_yaw_base` *1.6；`viewkick_yaw_random` *1.6；`viewkick_scale_min_hipfire` *0.625；`viewkick_scale_max_hipfire` *0.625 |
| `corrupted_mag` | 820 | `ammo_clip_size` 69；`reload_time` *1.4；`reload_time_late1` *1.4；`reload_time_late2` *1.4；`reload_time_late3` *1.4；`reload_time_late4` *1.4；`reload_time_late5` *1.4；`reloadempty_time` *1.4；`reloadempty_time_late1` *1.4；`reloadempty_time_late2` *1.4；`reloadempty_time_late3` *1.4；`reloadempty_time_late4` *1.4；`reloadempty_time_late5` *1.4；`reloadsegment_time_loop` *1.3；`reloadsegment_time_end` *1.3；`reloadsegmentempty_time_end` *1.3 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`hopup_smart_reload`、`legendary1`、`dormant_hopup_paintball_elite`、`hopup_ultimate_accelerator`

## EPG（`weapons/mp_weapon_epg.txt`）

**射击**：`fire_mode` automatic (L12)；`is_semi_auto` 1 (L13)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_epg (L21)；`fire_rate` 0.900000 (L110)

**弹药**：`ammo_pool_type` special (L7)；`ammo_clip_size` 4 (L61)；`ammo_min_to_fire` 1 (L62)；`ammo_per_shot` 1 (L63)；`ammo_default_total` 28 (L64)；`ammo_stockpile_max` 28 (L65)；`ammo_no_remove_from_stockpile` 0 (L66)；`uses_ammo_pool` 0 (L68)；`empty_reload_only` 0 (L121)

**时间**：`zoom_time_in` 0.200000 (L103)；`zoom_time_out` 0.150000 (L104)；`zoom_fov` 55 (L105)；`reload_time` 3.700000 (L114)；`reload_time_late1` 2.550000 (L115)；`reloadempty_time` 4.000000 (L117)；`reloadempty_time_late1` 2.875000 (L118)；`deployfirst_time` 1.250000 (L306)

**伤害**：`damage_flags` DF_BULLET \| DF_GIB \| DF_EXPLOSION (L26)；`damage_near_value` 40 (L69)；`damage_far_value` 40 (L70)；`damage_near_distance` 2000 (L74)；`damage_far_distance` 2500 (L75)；`explosion_inner_radius` 52 (L77)；`explosionradius` 180 (L78)；`impulse_force` 5000 (L79)；`explosion_damage` 65 (L81)；`allow_headshots` 0 (L111)；`headshot_distance` 1000 (L112)；`damage_headshot_scale` 1.250000 (L113)；`critical_hit` 1 (L308)；`critical_hit_damage_scale` 1.500000 (L309)；`npc_damage_near_value` 99 (L324)；`npc_damage_far_value` 99 (L325)；`npc_damage_near_distance` 2000 (L328)；`npc_damage_far_distance` 15000 (L329)；`npc_min_engage_range` 500 (L330)；`npc_max_engage_range` 2000 (L331)；`npc_min_range` 0 (L334)；`npc_max_range` 3000 (L335)；`npc_min_burst` 1 (L336)；`npc_max_burst` 2 (L337)；`npc_rest_time_between_bursts_min` 0.500000 (L344)；`npc_rest_time_between_bursts_max` 0.800000 (L345)

**弹道**：`projectile_launch_speed` 2000 (L87)；`projectile_gravity_scale` 0.000000 (L88)；`projectile_lifetime` 10.000000 (L93)；`bolt_hitsize` 0.000000 (L96)；`bolt_hitsize_grow1_time` 0.075000 (L97)；`bolt_hitsize_grow1_size` 3.000000 (L98)；`bolt_hitsize_grow2_time` 0.180000 (L99)；`bolt_hitsize_grow2_size` 5.000000 (L100)；`bolt_hitsize_growfinal_lerptime` 0.180000 (L101)；`bolt_hitsize_growfinal_size` 5.000000 (L102)

**扩散**：`spread_stand_hip` 0 (L122)；`spread_stand_hip_run` 0 (L123)；`spread_stand_hip_sprint` 0 (L124)；`spread_crouch_hip` 0 (L125)；`spread_air_hip` 0 (L126)；`spread_stand_ads` 0.000000 (L127)；`spread_crouch_ads` 0.000000 (L128)；`spread_air_ads` 0.000000 (L129)；`spread_kick_on_fire_stand_hip` 0 (L130)；`spread_kick_on_fire_crouch_hip` 0 (L131)；`spread_kick_on_fire_air_hip` 0 (L132)；`spread_kick_on_fire_stand_ads` 0 (L133)；`spread_kick_on_fire_crouch_ads` 0 (L134)；`spread_kick_on_fire_air_ads` 0 (L135)；`spread_max_kick_stand_hip` 0 (L136)；`spread_max_kick_crouch_hip` 0 (L137)；`spread_max_kick_air_hip` 0 (L138)；`spread_max_kick_stand_ads` 0 (L139)；`spread_max_kick_crouch_ads` 0 (L140)；`spread_max_kick_air_ads` 0 (L141)；`spread_wallrunning` 0 (L142)；`spread_wallhanging` 0 (L143)；`spread_decay_delay` 0.100000 (L144)；`spread_decay_rate` 40 (L145)

**后坐**：`viewkick_spring` lstar (L147)；`viewkick_pitch_base` -0.050000 (L148)；`viewkick_pitch_random` 0.200000 (L149)；`viewkick_pitch_softScale` 2.000000 (L150)；`viewkick_pitch_hardScale` 1.000000 (L151)；`viewkick_yaw_base` 0.000000 (L152)；`viewkick_yaw_random` 0.400000 (L153)；`viewkick_yaw_softScale` 2.200000 (L155)；`viewkick_yaw_hardScale` 0.800000 (L156)；`viewkick_perm_pitch_base` -0.050000 (L177)；`viewkick_perm_pitch_random` 0.000000 (L178)；`viewkick_perm_yaw_base` 0.025000 (L179)；`viewkick_perm_yaw_random` 0.050000 (L180)；`viewkick_duck_scale` 1.000000 (L181)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `amped_damage` | 365 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `ferro_damage` | 380 | `sustained_laser_damage_scale` *2；`damage_near_value` *0.5；`damage_far_value` *0.5；`damage_very_far_value` *0.5；`damage_near_value_titanarmor` *0.5；`damage_far_value_titanarmor` *0.5；`damage_very_far_value_titanarmor` *0.5 |
| `jump_kit` | 395 | `impulse_force` 17500；`impulse_force_explosions` 65000 |
| `delayed_shot` | 410 | `pre_ignition_damage_titanarmor` 20；`pre_ignition_npc_damage_titanarmor` 30 |
| `slammer` | 427 | `impulse_force` 35000 |
| `pas_fast_ads` | 433 | `zoom_time_in` *0.5；`zoom_time_out` *0.6 |
| `burn_mod_epg` | 446 | `damage_near_value` ++30；`damage_far_value` ++30；`damage_near_value_titanarmor` 900；`damage_far_value_titanarmor` 900；`explosion_damage` 90；`explosion_damage_heavy_armor` 900 |
| `pas_fast_reload` | 474 | `reload_time` *0.7；`reload_time_late1` *0.7；`reloadempty_time` *0.7；`reloadempty_time_late1` *0.7 |
| `slowProjectile` | 483 | `projectile_launch_speed` 1750 |
| `auto_loader` | 489 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload` | 527 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload_fast_heals` | 549 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `matchmod_bonus_speed` | 571 | `move_speed_modifier` *2.0；`reload_time` *0.50；`reload_time_late1` *0.50；`reload_time_late2` *0.50；`reload_time_late3` *0.50；`reload_time_late4` *0.50；`reload_time_late5` *0.50；`reloadempty_time` *0.50；`reloadempty_time_late1` *0.50；`reloadempty_time_late2` *0.50；`reloadempty_time_late3` *0.50；`reloadempty_time_late4` *0.50；`reloadempty_time_late5` *0.50；`charge_cooldown_time` *0.50；`charge_overheat_cooldown_time` *0.50；`charge_overheat_cooldown_time_late1` *0.50；`charge_overheat_cooldown_time_late2` *0.50；`charge_overheat_cooldown_time_late3` *0.50 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`crate`、`pro_screen`、`pas_fast_swap`、`tactical_cdr_on_kill`、`pas_run_and_gun`、`innate_threat_vision`、`hopup_ultimate_accelerator`、`dormant_hopup_ultimate_accelerator`

## EPG Tethered（`weapons/mp_weapon_epg_tethered.txt`）

**射击**：`fire_mode` automatic (L19)；`is_semi_auto` 1 (L20)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_epg (L28)；`fire_rate` 0.900000 (L111)

**弹药**：`ammo_clip_size` 3 (L4)；`ammo_min_to_fire` 1 (L5)；`ammo_per_shot` 1 (L6)；`ammo_default_total` 6 (L7)；`ammo_stockpile_max` 6 (L8)；`ammo_no_remove_from_stockpile` 0 (L9)；`ammo_pool_type` special (L14)；`uses_ammo_pool` 0 (L69)；`empty_reload_only` 0 (L122)

**时间**：`zoom_time_in` 0.200000 (L104)；`zoom_time_out` 0.150000 (L105)；`zoom_fov` 55 (L106)；`reload_time` 3.700000 (L115)；`reload_time_late1` 2.550000 (L116)；`reloadempty_time` 4.000000 (L118)；`reloadempty_time_late1` 2.875000 (L119)；`deployfirst_time` 1.250000 (L307)

**伤害**：`damage_flags` DF_BULLET \| DF_GIB \| DF_EXPLOSION (L33)；`damage_near_value` 40 (L70)；`damage_far_value` 40 (L71)；`damage_near_distance` 2000 (L75)；`damage_far_distance` 2500 (L76)；`explosion_inner_radius` 52 (L78)；`explosionradius` 180 (L79)；`impulse_force` 5000 (L80)；`explosion_damage` 65 (L82)；`allow_headshots` 0 (L112)；`headshot_distance` 1000 (L113)；`damage_headshot_scale` 1.250000 (L114)；`critical_hit` 1 (L309)；`critical_hit_damage_scale` 1.500000 (L310)；`npc_damage_near_value` 99 (L325)；`npc_damage_far_value` 99 (L326)；`npc_damage_near_distance` 2000 (L329)；`npc_damage_far_distance` 15000 (L330)；`npc_min_engage_range` 500 (L331)；`npc_max_engage_range` 2000 (L332)；`npc_min_range` 0 (L335)；`npc_max_range` 3000 (L336)；`npc_min_burst` 1 (L337)；`npc_max_burst` 2 (L338)；`npc_rest_time_between_bursts_min` 0.500000 (L345)；`npc_rest_time_between_bursts_max` 0.800000 (L346)

**弹道**：`projectile_launch_speed` 2000 (L88)；`projectile_gravity_scale` 0.000000 (L89)；`projectile_lifetime` 10.000000 (L94)；`bolt_hitsize` 0.000000 (L97)；`bolt_hitsize_grow1_time` 0.075000 (L98)；`bolt_hitsize_grow1_size` 3.000000 (L99)；`bolt_hitsize_grow2_time` 0.180000 (L100)；`bolt_hitsize_grow2_size` 5.000000 (L101)；`bolt_hitsize_growfinal_lerptime` 0.180000 (L102)；`bolt_hitsize_growfinal_size` 5.000000 (L103)

**扩散**：`spread_stand_hip` 0 (L123)；`spread_stand_hip_run` 0 (L124)；`spread_stand_hip_sprint` 0 (L125)；`spread_crouch_hip` 0 (L126)；`spread_air_hip` 0 (L127)；`spread_stand_ads` 0.000000 (L128)；`spread_crouch_ads` 0.000000 (L129)；`spread_air_ads` 0.000000 (L130)；`spread_kick_on_fire_stand_hip` 0 (L131)；`spread_kick_on_fire_crouch_hip` 0 (L132)；`spread_kick_on_fire_air_hip` 0 (L133)；`spread_kick_on_fire_stand_ads` 0 (L134)；`spread_kick_on_fire_crouch_ads` 0 (L135)；`spread_kick_on_fire_air_ads` 0 (L136)；`spread_max_kick_stand_hip` 0 (L137)；`spread_max_kick_crouch_hip` 0 (L138)；`spread_max_kick_air_hip` 0 (L139)；`spread_max_kick_stand_ads` 0 (L140)；`spread_max_kick_crouch_ads` 0 (L141)；`spread_max_kick_air_ads` 0 (L142)；`spread_wallrunning` 0 (L143)；`spread_wallhanging` 0 (L144)；`spread_decay_delay` 0.100000 (L145)；`spread_decay_rate` 40 (L146)

**后坐**：`viewkick_spring` lstar (L148)；`viewkick_pitch_base` -0.050000 (L149)；`viewkick_pitch_random` 0.200000 (L150)；`viewkick_pitch_softScale` 2.000000 (L151)；`viewkick_pitch_hardScale` 1.000000 (L152)；`viewkick_yaw_base` 0.000000 (L153)；`viewkick_yaw_random` 0.400000 (L154)；`viewkick_yaw_softScale` 2.200000 (L156)；`viewkick_yaw_hardScale` 0.800000 (L157)；`viewkick_perm_pitch_base` -0.050000 (L178)；`viewkick_perm_pitch_random` 0.000000 (L179)；`viewkick_perm_yaw_base` 0.025000 (L180)；`viewkick_perm_yaw_random` 0.050000 (L181)；`viewkick_duck_scale` 1.000000 (L182)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `amped_damage` | 366 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `ferro_damage` | 381 | `sustained_laser_damage_scale` *2；`damage_near_value` *0.5；`damage_far_value` *0.5；`damage_very_far_value` *0.5；`damage_near_value_titanarmor` *0.5；`damage_far_value_titanarmor` *0.5；`damage_very_far_value_titanarmor` *0.5 |
| `jump_kit` | 396 | `impulse_force` 17500；`impulse_force_explosions` 65000 |
| `delayed_shot` | 411 | `pre_ignition_damage_titanarmor` 20；`pre_ignition_npc_damage_titanarmor` 30 |
| `slammer` | 428 | `impulse_force` 35000 |
| `pas_fast_ads` | 434 | `zoom_time_in` *0.5；`zoom_time_out` *0.6 |
| `burn_mod_epg` | 447 | `damage_near_value` ++30；`damage_far_value` ++30；`damage_near_value_titanarmor` 900；`damage_far_value_titanarmor` 900；`explosion_damage` 90；`explosion_damage_heavy_armor` 900 |
| `pas_fast_reload` | 475 | `reload_time` *0.7；`reload_time_late1` *0.7；`reloadempty_time` *0.7；`reloadempty_time_late1` *0.7 |
| `slowProjectile` | 484 | `projectile_launch_speed` 1750 |
| `auto_loader` | 490 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload` | 528 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload_fast_heals` | 550 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `matchmod_bonus_speed` | 572 | `move_speed_modifier` *2.0；`reload_time` *0.50；`reload_time_late1` *0.50；`reload_time_late2` *0.50；`reload_time_late3` *0.50；`reload_time_late4` *0.50；`reload_time_late5` *0.50；`reloadempty_time` *0.50；`reloadempty_time_late1` *0.50；`reloadempty_time_late2` *0.50；`reloadempty_time_late3` *0.50；`reloadempty_time_late4` *0.50；`reloadempty_time_late5` *0.50；`charge_cooldown_time` *0.50；`charge_overheat_cooldown_time` *0.50；`charge_overheat_cooldown_time_late1` *0.50；`charge_overheat_cooldown_time_late2` *0.50；`charge_overheat_cooldown_time_late3` *0.50 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`crate`、`pro_screen`、`pas_fast_swap`、`tactical_cdr_on_kill`、`pas_run_and_gun`、`innate_threat_vision`、`hopup_ultimate_accelerator`、`dormant_hopup_ultimate_accelerator`

## Charge Gauntlet（`weapons/mp_weapon_charge_gauntlet.txt`）

**射击**：`fire_mode` offhandHybrid (L7)；`is_semi_auto` 1 (L9)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_charge_gauntlet (L29)；`fire_rate` 1.300000 (L91)；`blast_pattern_default_scale` 2.250000 (L119)；`primary_attack_ignores_spread` 1 (L120)

**弹药**：`ammo_clip_size` 180 (L77)；`ammo_default_total` 180 (L78)；`ammo_min_to_fire` 180 (L79)；`ammo_per_shot` 180 (L80)；`ammo_stockpile_max` 180 (L81)；`ammo_drains_to_empty_on_fire` 0 (L82)；`ammo_no_remove_from_clip` 0 (L83)；`ammo_no_remove_from_stockpile` 1 (L84)；`regen_ammo_refill_rate` 1.000000 (L86)；`regen_ammo_refill_start_delay` 0.000000 (L87)；`reload_enabled` 0 (L93)；`empty_reload_only` 0 (L95)

**时间**：`zoom_fov` 45 (L92)；`reload_time` 3.500000 (L97)；`reloadempty_time` 4.600000 (L98)；`deployfirst_time` 1.500000 (L100)；`deploy_time` 0.800000 (L101)；`holster_time` 0.300000 (L102)；`raise_time` 0.900000 (L103)；`lower_time` 0.000000 (L104)

**伤害**：`damage_type` burn (L65)；`impulse_force` 5000 (L66)；`critical_hit` 1 (L67)；`allow_headshots` 1 (L96)；`damage_near_value` 15 (L136)；`damage_far_value` 15 (L137)；`damage_very_far_value` 15 (L138)；`damage_near_distance` 1970 (L142)；`damage_far_distance` 11820 (L143)；`damage_very_far_distance` 11828 (L144)；`damage_flags` DF_SNIPER \| DF_GIB \| DF_KNOCK_BACK (L145)；`pass_through_depth` 0 (L146)；`pass_through_damage_preserved_scale` 0.000000 (L147)

**弹道**：`projectile_launch_speed` 6000 (L68)；`projectile_gravity_scale` 0.000000 (L69)；`projectile_drag_coefficient` 0.000010 (L70)；`bolt_hitsize` 2 (L129)；`bolt_hitsize_grow1_time` 0.040000 (L130)；`bolt_hitsize_grow1_size` 7 (L131)；`bolt_hitsize_grow2_time` 0.100000 (L132)；`bolt_hitsize_grow2_size` 10 (L133)；`bolt_hitsize_growfinal_lerptime` 0.160000 (L134)；`bolt_hitsize_growfinal_size` 15 (L135)

**扩散**：`spread_stand_hip` 0 (L121)；`spread_stand_hip_run` 0 (L122)；`spread_stand_hip_sprint` 0 (L123)；`spread_crouch_hip` 0 (L124)；`spread_air_hip` 0 (L125)；`spread_stand_ads` 0.000000 (L126)；`spread_crouch_ads` 0.000000 (L127)；`spread_air_ads` 0 (L128)

**充能 / 热**：`charge_time` 0.600000 (L106)；`charge_require_input` 1 (L107)；`charge_allow_hold_when_full` 1 (L108)；`charge_remain_full_when_fired` 1 (L109)；`charge_attack_min_charge_required` 0.100000 (L110)；`charge_cooldown_time` 0.210000 (L111)；`charge_cooldown_delay` 0.100000 (L112)；`charge_levels` 6 (L113)；`charge_level_base` 1 (L114)；`charge_curve_coefficients` 1.4205 -1.1607 .7338 (L115)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `upgrade_core_ult_cooldown_reduction` | 294 | `ammo_clip_size` 150；`ammo_min_to_fire` 150；`ammo_per_shot` 150 |
| `instant_holster` | 302 | `holster_time` 0.000000 |
| `alt_mode_sparrow_ult` | 308 | `ammo_clip_size` 270；`ammo_default_total` 90；`ammo_min_to_fire` 90；`ammo_per_shot` 90；`ammo_stockpile_max` 270 |
| `ultimates_charge_over_time_disabled` | 318 | `regen_ammo_refill_rate` 0 |
| `arenas_ammo_regen_off` | 324 | `regen_ammo_refill_rate` *0.0 |
| `survival_armor_cooldown_mod` | 330 | `regen_ammo_refill_rate` *1.25 |
| `survival_armor_cooldown_extra_mod` | 336 | `regen_ammo_refill_rate` *1.5 |
| `survival_armor_cooldown_v2_mod` | 342 | `regen_ammo_refill_rate` *1.33 |
| `survival_ammo_regen_paused` | 348 | `regen_ammo_refill_rate` *0.0 |
| `ability_in_effect_regen_paused` | 354 | `regen_ammo_refill_rate` *0.0 |
| `survival_ammo_regen_staging` | 360 | `regen_ammo_refill_rate` *5.0 |
| `matchmod_bonus_speed` | 366 | `move_speed_modifier` *2.0；`reload_time` *0.50；`reload_time_late1` *0.50；`reload_time_late2` *0.50；`reload_time_late3` *0.50；`reload_time_late4` *0.50；`reload_time_late5` *0.50；`reloadempty_time` *0.50；`reloadempty_time_late1` *0.50；`reloadempty_time_late2` *0.50；`reloadempty_time_late3` *0.50；`reloadempty_time_late4` *0.50；`reloadempty_time_late5` *0.50；`charge_cooldown_time` *0.50；`charge_overheat_cooldown_time` *0.50；`charge_overheat_cooldown_time_late1` *0.50；`charge_overheat_cooldown_time_late2` *0.50；`charge_overheat_cooldown_time_late3` *0.50 |
| `matchmod_quick_charge` | 389 | `regen_ammo_refill_rate` *2 |
| `amped_damage` | 395 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `ferro_damage` | 410 | `sustained_laser_damage_scale` *2；`damage_near_value` *0.5；`damage_far_value` *0.5；`damage_very_far_value` *0.5；`damage_near_value_titanarmor` *0.5；`damage_far_value_titanarmor` *0.5；`damage_very_far_value_titanarmor` *0.5 |
| `auto_loader` | 425 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload` | 463 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `endorsement_fast_reload_fast_heals` | 485 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60；`charge_cooldown_time` *0.60；`charge_overheat_cooldown_time` *0.60；`charge_overheat_cooldown_time_late1` *0.60；`charge_overheat_cooldown_time_late2` *0.60；`charge_overheat_cooldown_time_late3` *0.60 |
| `optic_cq_hcog_classic` | 507 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 60 |
| `optic_cq_hcog_bruiser` | 534 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 38.590698 |
| `optic_cq_holosight` | 561 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 60 |
| `optic_cq_holosight_variable` | 589 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 60 |
| `optic_ranged_hcog` | 620 | `zoom_time_in` 0.430000；`zoom_time_out` 0.370000；`zoom_fov` 26.275600 |
| `optic_ranged_aog_variable` | 650 | `zoom_time_in` 0.430000；`zoom_time_out` 0.370000；`zoom_fov` 38.590698 |
| `optic_sniper` | 683 | `zoom_time_in` 0.480000；`zoom_time_out` 0.420000；`zoom_fov` 13.312800 |
| `optic_sniper_variable` | 712 | `zoom_time_in` 0.510000；`zoom_time_out` 0.450000；`zoom_fov` 19.858299 |
| `optic_sniper_threat` | 744 | `zoom_time_in` 0.530000；`zoom_time_out` 0.470000；`zoom_fov` 19.858299 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`innate_threat_vision`、`hopup_ultimate_accelerator`、`dormant_hopup_ultimate_accelerator`

## Arc Bolt（`weapons/mp_weapon_arc_bolt.txt`）

**射击**：`fire_mode` offhand (L9)；`fire_rate` 5.000000 (L22)

**弹药**：`regen_ammo_refill_rate` 1.000000 (L20)；`reload_enabled` 0 (L21)；`ammo_clip_size` 20 (L45)；`ammo_per_shot` 20 (L46)；`ammo_min_to_fire` 20 (L47)；`ammo_default_total` 20 (L48)

**时间**：`deploy_time` 1.500000 (L40)；`holster_time` 0.150000 (L41)；`raise_time` 1.500000 (L42)；`lower_time` 0.150000 (L43)

**伤害**：`damage_type` none (L27)；`damage_flags` DF_RAGDOLL \| DF_EXPLOSION \| DF_ELECTRICAL (L28)；`damage_near_distance` 0 (L54)；`damage_far_distance` 2048 (L55)；`damage_near_value` 0 (L56)；`damage_far_value` 0 (L57)；`allow_headshots` 0 (L62)

**弹道**：`bolt_gravity_enabled` 0 (L24)；`projectile_gravity_scale` 0 (L25)；`projectile_launch_speed` 1200 (L51)；`projectile_lifetime` 6 (L52)；`projectile_ricochet_max_count` 5 (L53)

**后坐**：`viewkick_spring` pistol (L126)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `survival_armor_cooldown_mod` | 153 | `regen_ammo_refill_rate` *1.25 |
| `upgrade_tac_one` | 164 | `ammo_clip_size` *2；`ammo_default_total` *2；`ammo_stockpile_max` *2 |
| `survival_armor_cooldown_extra_mod` | 172 | `regen_ammo_refill_rate` *1.5 |
| `survival_ammo_regen_paused` | 178 | `regen_ammo_refill_rate` *0.0 |
| `ability_in_effect_regen_paused` | 184 | `regen_ammo_refill_rate` *0.0 |
| `survival_ammo_regen_staging` | 190 | `regen_ammo_refill_rate` *5.0 |
| `arenas_tac_max_cooldown` | 196 | `ammo_regen_takes_from_stockpile` 1；`ammo_stockpile_max` 10000 |
| `survival_armor_cooldown_v2_mod` | 202 | `regen_ammo_refill_rate` *1.33 |
| `matchmod_bonus_speed` | 207 | `move_speed_modifier` *2.0；`reload_time` *0.50；`reload_time_late1` *0.50；`reload_time_late2` *0.50；`reload_time_late3` *0.50；`reload_time_late4` *0.50；`reload_time_late5` *0.50；`reloadempty_time` *0.50；`reloadempty_time_late1` *0.50；`reloadempty_time_late2` *0.50；`reloadempty_time_late3` *0.50；`reloadempty_time_late4` *0.50；`reloadempty_time_late5` *0.50；`charge_cooldown_time` *0.50；`charge_overheat_cooldown_time` *0.50；`charge_overheat_cooldown_time_late1` *0.50；`charge_overheat_cooldown_time_late2` *0.50；`charge_overheat_cooldown_time_late3` *0.50 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`survival_finite_ordnance`

## Arc Wave（`weapons/mp_weapon_arc_wave.txt`）

**射击**：`fire_mode` offhand (L10)；`fire_rate` 1.000000 (L38)

**弹药**：`ammo_clip_size` 20 (L33)；`ammo_default_total` 20 (L34)；`ammo_min_to_fire` 20 (L35)；`ammo_per_shot` 20 (L36)；`ammo_stockpile_max` 20 (L37)；`regen_ammo_refill_rate` 1 (L39)；`regen_ammo_refill_start_delay` 0.000000 (L40)；`reload_enabled` 0 (L50)；`empty_reload_only` 0 (L51)

**伤害**：`damage_type` none (L41)；`damage_near_value` 15 (L43)；`damage_far_value` 15 (L44)；`allow_headshots` 0 (L54)

**移动**：`primary_fire_does_not_block_sprint` 1 (L56)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `ultimates_charge_over_time_disabled` | 77 | `regen_ammo_refill_rate` 0 |
| `survival_armor_cooldown_mod` | 89 | `regen_ammo_refill_rate` *1.25 |
| `survival_armor_cooldown_extra_mod` | 95 | `regen_ammo_refill_rate` *1.5 |
| `survival_ammo_regen_paused` | 101 | `regen_ammo_refill_rate` *0.0 |
| `ability_in_effect_regen_paused` | 107 | `regen_ammo_refill_rate` *0.0 |
| `survival_ammo_regen_staging` | 113 | `regen_ammo_refill_rate` *5.0 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`survival_finite_ordnance`、`copycat_mod`

## Defender Sustained（`weapons/mp_weapon_defender_sustained.txt`）

**射击**：`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_defender_sustained (L12)；`fire_rate` 1 (L48)；`fire_mode` automatic (L206)；`is_semi_auto` 1 (L207)

**弹药**：`uses_ammo_pool` 1 (L39)；`ammo_pool_type` special (L40)；`ammo_clip_size` 4 (L41)；`ammo_default_total` 24 (L42)；`ammo_stockpile_max` 24 (L43)；`ammo_no_remove_from_stockpile` 0 (L44)；`ammo_min_to_fire` 1 (L45)；`ammo_per_shot` 1 (L46)；`reload_enabled` 1 (L52)；`empty_reload_only` 0 (L54)

**时间**：`zoom_time_in` 0.200000 (L49)；`zoom_time_out` 0.150000 (L50)；`zoom_fov` 55 (L51)；`reload_time` 2.000000 (L57)；`reloadempty_time` 2.000000 (L58)；`holster_time` 0.500000 (L59)；`deploy_time` 0.800000 (L60)；`lower_time` 0.250000 (L61)；`raise_time` 0.300000 (L62)

**伤害**：`damage_type` bullet (L36)；`impulse_force` 2000 (L37)；`critical_hit` 1 (L38)；`allow_headshots` 1 (L55)；`damage_flags` DF_GIB (L83)；`damage_near_value` 5 (L84)；`damage_far_value` 5 (L85)；`npc_damage_near_value` 2 (L89)；`npc_damage_far_value` 2 (L90)；`npc_damage_near_distance` 200 (L93)；`npc_damage_far_distance` 15000 (L94)；`npc_min_engage_range` 100 (L95)；`npc_max_engage_range` 4000 (L96)；`npc_min_range` 0 (L99)；`npc_max_range` 5000 (L100)；`npc_min_burst` 1 (L101)；`npc_max_burst` 1 (L102)；`npc_rest_time_between_bursts_min` 2.500000 (L103)；`npc_rest_time_between_bursts_max` 2.500000 (L104)；`headshot_distance` 29528 (L218)；`damage_headshot_scale` 1.800000 (L219)；`damage_leg_scale` 0.900000 (L220)；`damage_shield_scale` 1 (L221)；`critical_hit_damage_scale` 2 (L222)；`damage_near_distance` 7500 (L223)；`damage_far_distance` 10000 (L224)；`damage_very_far_distance` 12000 (L225)；`pass_through_depth` 32 (L227)；`pass_through_damage_preserved_scale` 0.800000 (L228)

**弹道**：`projectile_drag_coefficient` 0.003300 (L230)；`bolt_gravity_enabled` 1 (L231)；`projectile_gravity_scale` 1.400000 (L232)；`bolt_zero_distance` 1968.500000 (L233)；`bolt_hitsize` 0.000000 (L234)；`projectile_lifetime` 6.000000 (L235)；`projectile_ricochet_max_count` 0 (L338)；`projectile_bounce_damage_reduction_scale` 0.500000 (L340)；`projectile_speed_reduction_factor` 0.720000 (L341)

**扩散**：`spread_stand_hip` 4.000000 (L140)；`spread_stand_hip_run` 5.000000 (L141)；`spread_stand_ads` 0.000000 (L142)；`spread_stand_hip_sprint` 6.000000 (L143)；`spread_crouch_hip` 3.750000 (L144)；`spread_crouch_ads` 0.000000 (L145)；`spread_air_hip` 8.000000 (L146)；`spread_air_ads` 0.000000 (L147)；`spread_kick_on_fire_stand_hip` 1 (L242)；`spread_kick_on_fire_crouch_hip` 1 (L243)；`spread_kick_on_fire_air_hip` 1 (L244)；`spread_max_kick_stand_hip` 12.000000 (L245)；`spread_max_kick_crouch_hip` 10.000000 (L246)；`spread_max_kick_air_hip` 12.000000 (L247)；`spread_decay_rate` 4 (L248)；`spread_decay_delay` 0.100000 (L249)

**后坐**：`viewkick_spring` titan_arc (L167)；`viewkick_pitch_base` -1 (L168)；`viewkick_pitch_random` 1.500000 (L169)；`viewkick_pitch_softScale` 0 (L170)；`viewkick_pitch_hardScale` 3 (L171)；`viewkick_yaw_base` 0 (L172)；`viewkick_yaw_random` 0.500000 (L173)；`viewkick_yaw_softScale` 1 (L174)；`viewkick_yaw_hardScale` 0 (L175)

**充能 / 热**：`sustained_discharge_duration` 1.250000 (L63)；`sustained_discharge_pulse_frequency` 0.104000 (L64)；`sustained_discharge_allow_melee` 0 (L65)；`sustained_discharge_require_input` 0 (L66)；`sustained_discharge_updates_charge` 1 (L67)；`sustained_discharge_ends_in_primary_attack` 1 (L68)；`sustained_laser_enabled` 1 (L69)；`sustained_laser_radius` 18 (L72)；`sustained_laser_range` 19685 (L73)；`charge_cooldown_time` 1.000000 (L115)；`charge_cooldown_delay` 0.000000 (L116)

**移动**：`primary_fire_does_not_block_sprint` 0 (L200)；`ads_move_speed_scale` 0.350000 (L205)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `optic_sniper` | 400 | `charge_effect_attachment` muzzle_flash_scoped；`charge_effect2_attachment` muzzle_flash_scoped；`zoom_time_in` 0.480000；`zoom_time_out` 0.420000；`zoom_fov` 13.312800 |
| `optic_sniper_variable` | 429 | `charge_effect_attachment` muzzle_flash_scoped；`charge_effect2_attachment` muzzle_flash_scoped；`zoom_time_in` 0.510000；`zoom_time_out` 0.450000；`zoom_fov` 19.858299 |
| `optic_sniper_threat` | 461 | `charge_effect_attachment` muzzle_flash_scoped；`charge_effect2_attachment` muzzle_flash_scoped；`zoom_time_in` 0.530000；`zoom_time_out` 0.470000；`zoom_fov` 19.858299 |
| `elevator_shooter` | 498 | `spread_air_hip` *0.8；`spread_air_hip_moving` 10.000000；`spread_air_ads` 0.250000；`spread_air_ads_moving` 8.000000；`spread_kick_on_fire_air_hip` 1；`spread_max_kick_air_hip` *0.8；`spread_kick_on_fire_air_ads` 0；`spread_max_kick_air_ads` 0；`viewdrift_ads_air_scale_pitch` 0.400000；`viewdrift_ads_air_scale_yaw` 0.300000；`viewdrift_hipfire_air_scale_pitch` 0.000000；`viewdrift_hipfire_air_scale_yaw` 0.000000 |
| `amped_damage` | 516 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `auto_loader` | 531 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |
| `optic_cq_hcog_classic` | 548 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 60 |
| `optic_cq_hcog_bruiser` | 573 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 38.590698 |
| `optic_cq_holosight` | 598 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 60 |
| `optic_cq_holosight_variable` | 624 | `zoom_time_in` 0.370000；`zoom_time_out` 0.330000；`zoom_fov` 60 |
| `optic_ranged_hcog` | 653 | `zoom_time_in` 0.430000；`zoom_time_out` 0.370000；`zoom_fov` 26.275600 |
| `optic_ranged_aog_variable` | 681 | `zoom_time_in` 0.430000；`zoom_time_out` 0.370000；`zoom_fov` 38.590698 |
| `stock_sniper_l1` | 712 | `zoom_time_in` *0.9；`zoom_time_out` *0.9；`deploy_time` *0.85；`holster_time` *0.85；`raise_time` *0.9；`lower_time` *0.9；`viewdrift_ads_stand_scale_pitch` *0.7；`viewdrift_ads_stand_scale_yaw` *0.7；`viewdrift_ads_crouch_scale_pitch` *0.7；`viewdrift_ads_crouch_scale_yaw` *0.7；`viewdrift_ads_air_scale_pitch` *0.7；`viewdrift_ads_air_scale_yaw` *0.7；`viewdrift_ads_speed_pitch` *0.9；`viewdrift_ads_speed_yaw` *0.9；`reload_time` *0.967；`reload_time_late1` *0.967；`reload_time_late2` *0.967；`reload_time_late3` *0.967；`reload_time_late4` *0.967；`reload_time_late5` *0.967；`reloadempty_time` *0.967；`reloadempty_time_late1` *0.967；`reloadempty_time_late2` *0.967；`reloadempty_time_late3` *0.967；`reloadempty_time_late4` *0.967；`reloadempty_time_late5` *0.967 |
| `stock_sniper_l2` | 743 | `zoom_time_in` *0.85；`zoom_time_out` *0.85；`deploy_time` *0.8；`holster_time` *0.8；`raise_time` *0.85；`lower_time` *0.85；`viewdrift_ads_stand_scale_pitch` *0.5；`viewdrift_ads_stand_scale_yaw` *0.5；`viewdrift_ads_crouch_scale_pitch` *0.5；`viewdrift_ads_crouch_scale_yaw` *0.5；`viewdrift_ads_air_scale_pitch` *0.5；`viewdrift_ads_air_scale_yaw` *0.5；`viewdrift_ads_speed_pitch` *0.85；`viewdrift_ads_speed_yaw` *0.85；`reload_time` *0.933；`reload_time_late1` *0.933；`reload_time_late2` *0.933；`reload_time_late3` *0.933；`reload_time_late4` *0.933；`reload_time_late5` *0.933；`reloadempty_time` *0.933；`reloadempty_time_late1` *0.933；`reloadempty_time_late2` *0.933；`reloadempty_time_late3` *0.933；`reloadempty_time_late4` *0.933；`reloadempty_time_late5` *0.933 |
| `stock_sniper_l3` | 774 | `zoom_time_in` *0.8；`zoom_time_out` *0.8；`deploy_time` *0.75；`holster_time` *0.75；`raise_time` *0.8；`lower_time` *0.8；`viewdrift_ads_stand_scale_pitch` *0.2；`viewdrift_ads_stand_scale_yaw` *0.2；`viewdrift_ads_crouch_scale_pitch` *0.2；`viewdrift_ads_crouch_scale_yaw` *0.2；`viewdrift_ads_air_scale_pitch` *0.2；`viewdrift_ads_air_scale_yaw` *0.2；`viewdrift_ads_speed_pitch` *0.8；`viewdrift_ads_speed_yaw` *0.8；`reload_time` *0.9；`reload_time_late1` *0.9；`reload_time_late2` *0.9；`reload_time_late3` *0.9；`reload_time_late4` *0.9；`reload_time_late5` *0.9；`reloadempty_time` *0.9；`reloadempty_time_late1` *0.9；`reloadempty_time_late2` *0.9；`reloadempty_time_late3` *0.9；`reloadempty_time_late4` *0.9；`reloadempty_time_late5` *0.9 |

