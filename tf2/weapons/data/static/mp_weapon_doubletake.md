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

