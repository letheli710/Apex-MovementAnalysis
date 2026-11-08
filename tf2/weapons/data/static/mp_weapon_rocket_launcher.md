### mp_weapon_rocket_launcher 文件原值（`mp_weapon_rocket_launcher.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_size` | 1 |  | extended_ammo=1 |
| `ammo_default_total` | 7 | 3 | extended_ammo=9 |
| `ammo_min_to_fire` | 1 |  |  |
| `ammo_no_remove_from_stockpile` | 0 |  | at_unlimited_ammo=1 |
| `ammo_stockpile_max` | 7 | 12 | extended_ammo=9 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `attack_button_presses_ads` | 1 |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_rate` | 1 |  |  |
| `primary_fire_does_not_block_sprint` | — |  | pas_run_and_gun=1 |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 0 |  |  |
| `critical_hit` | 0 |  |  |
| `damage_far_distance` | 15000 |  |  |
| `damage_far_value` | 100 | 250 | burn_mod_rocket_launcher=200; fd_mortar_mode=*0.0 |
| `damage_far_value_titanarmor` | 2250 | 1250 | burn_mod_rocket_launcher=3250; fd_mortar_mode=*0.15 |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 1200 |  |  |
| `damage_near_value` | 100 | 250 | burn_mod_rocket_launcher=200; fd_mortar_mode=*0.0 |
| `damage_near_value_titanarmor` | 2250 | 1250 | burn_mod_rocket_launcher=3250; fd_mortar_mode=*0.15 |
| `damage_type` | burn |  |  |
| `explosion_damage` | 100 | 150 | burn_mod_rocket_launcher=150; fd_mortar_mode=*0.0 |
| `explosion_damage_heavy_armor` | 500 |  | burn_mod_rocket_launcher=700; fd_mortar_mode=*0.15 |
| `explosion_damages_owner` | 0 | 1 |  |
| `explosion_inner_radius` | 96 |  | fd_mortar_mode=*0 |
| `explosionradius` | 180 |  | fd_mortar_mode=*0 |
| `impulse_force` | 10000 |  |  |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_drift_intensity` | 0.8 |  |  |
| `projectile_drift_windiness` | 2.25 |  |  |
| `projectile_straight_radius_max` | 65 |  |  |
| `projectile_straight_radius_min` | 40 |  |  |
| `projectile_straight_time_max` | 1.2 | 1.8 |  |
| `projectile_straight_time_min` | 0.4 | 1.5 |  |
| `scripted_projectile_max_timestep` | 0.2 |  |  |
| `scripted_projectile_velocity` | 1 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.8 |  |  |
| `fast_swap_to` | 0 |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 3.0 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | — |  | pas_fast_reload=*0.7 |
| `reloadempty_time` | 3.0 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 3.0 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 1.5 |  |  |

**开镜**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `ads_fov_zoomfrac_end` | 1.0 |  |  |
| `ads_fov_zoomfrac_start` | 0.4 |  |  |
| `ads_move_speed_scale` | 0.5 |  |  |
| `zoom_fov` | 45 |  |  |
| `zoom_time_in` | 0.35 |  | pas_fast_ads=*0.5 |
| `zoom_time_out` | 0.35 |  | pas_fast_ads=*0.6 |

**散布**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `spread_stand_ads` | 0.2 |  | fd_mortar_mode=0 |
| `spread_stand_hip` | 3 |  | fd_mortar_mode=0 |

**后坐和视角**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `viewdrift_ads_speed_pitch` | 0.6 |  |  |
| `viewdrift_ads_speed_yaw` | 1.2 |  |  |
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
| `viewkick_hipfire_weaponFraction` | 0.5 |  |  |
| `viewkick_hipfire_weaponFraction_vmScale` | 0.5 |  |  |
| `viewkick_perm_pitch_base` | 0.0 |  |  |
| `viewkick_perm_pitch_random` | 2.0 |  |  |
| `viewkick_perm_yaw_base` | 0.0 |  |  |
| `viewkick_perm_yaw_random` | 2.5 |  |  |
| `viewkick_pitch_base` | -4 |  |  |
| `viewkick_pitch_hardScale` | 5.0 |  |  |
| `viewkick_pitch_random` | 3.0 |  |  |
| `viewkick_pitch_softScale` | 1.3 |  |  |
| `viewkick_roll_base` | 0.0 |  |  |
| `viewkick_roll_hardScale` | 6.0 |  |  |
| `viewkick_roll_randomMax` | 0.7 |  |  |
| `viewkick_roll_randomMin` | 0.5 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_spring` | launcher |  |  |
| `viewkick_yaw_base` | 0.0 |  |  |
| `viewkick_yaw_hardScale` | 1.0 |  |  |
| `viewkick_yaw_random` | 3.0 |  |  |
| `viewkick_yaw_softScale` | 1.3 |  |  |
| `viewpunch_multiplier` | 2.9 |  |  |

**智能锁定**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `smart_ammo_alert_npc_fraction` | 0.8 |  |  |
| `smart_ammo_allow_ads_lock` | 1 |  |  |
| `smart_ammo_bounds_search_tick_interval` | 6 |  |  |
| `smart_ammo_hud_lock_style` | pilot_launcher |  |  |
| `smart_ammo_lock_type` | large |  |  |
| `smart_ammo_max_targets` | 1 |  |  |
| `smart_ammo_npc_use` | 0 |  |  |
| `smart_ammo_points_search_tick_interval` | 6 |  |  |
| `smart_ammo_screen_max_x` | 0.68 |  |  |
| `smart_ammo_screen_max_y` | 0.63 |  |  |
| `smart_ammo_screen_min_x` | 0.31 |  |  |
| `smart_ammo_screen_min_y` | 0.38 |  |  |
| `smart_ammo_search_angle` | 9 |  |  |
| `smart_ammo_search_distance` | 6500 |  |  |
| `smart_ammo_search_npcs` | 1 |  |  |
| `smart_ammo_search_players` | 1 |  |  |
| `smart_ammo_search_projectiles` | 0 |  |  |
| `smart_ammo_targeting_time_max` | 1.55 |  | fast_lock=0.9 |
| `smart_ammo_targeting_time_min` | 1.05 |  | fast_lock=0.5 |
| `smart_ammo_titan_lock_point0` | SMART_AMMO_TORSO_FRONT |  |  |
| `smart_ammo_titan_lock_point1` | SMART_AMMO_TORSO_BACK |  |  |
| `smart_ammo_titan_lock_point2` | SMART_AMMO_LEG_LEFT |  |  |
| `smart_ammo_titan_lock_point3` | SMART_AMMO_LEG_RIGHT |  |  |
| `smart_ammo_titan_lock_point4` | SMART_AMMO_TORSO_BASE |  |  |
| `smart_ammo_titan_lock_point5` | SMART_AMMO_HEAD |  |  |
| `smart_ammo_titan_lock_point6` | SMART_AMMO_ARM_LEFT |  |  |
| `smart_ammo_titan_lock_point7` | SMART_AMMO_ARM_RIGHT |  |  |
| `smart_ammo_titans_block_los` | 1 |  |  |
| `smart_ammo_track_cloaked_targets` | 0 |  |  |
| `smart_ammo_unlock_debounce_time` | 0.5 |  |  |
| `smart_ammo_weapon_type` | homing_missile |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_accuracy_multiplier_pilot` | 0.2 |  |  |
| `npc_damage_far_value` | 80 |  |  |
| `npc_damage_far_value_titanarmor` | 800 |  |  |
| `npc_damage_near_value` | 80 |  |  |
| `npc_damage_near_value_titanarmor` | 800 |  |  |
| `npc_explosion_damage` | 100 | 80 |  |
| `npc_explosion_damage_heavy_armor` | 400 |  |  |
| `npc_max_burst` | 1 |  |  |
| `npc_max_engage_range` | 2000 |  |  |
| `npc_max_engage_range_heavy_armor` | 2500 |  |  |
| `npc_max_range` | 8000 |  |  |
| `npc_min_burst` | 1 |  |  |
| `npc_min_engage_range` | 100 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_min_range` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 4 |  | fd_mortar_mode=*2.0 |
| `npc_rest_time_between_bursts_min` | 3.5 |  | fd_mortar_mode=*1.25 |
| `npc_use_ads_move_speed_scale` | 0 |  |  |
| `npc_vortex_block` | 0 |  |  |
| `proficiency_average_spreadscale` | 2.5 |  |  |
| `proficiency_good_spreadscale` | 2.0 |  |  |
| `proficiency_poor_spreadscale` | 3.0 |  |  |
| `proficiency_very_good_spreadscale` | 1.6 |  |  |

