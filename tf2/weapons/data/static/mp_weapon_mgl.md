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

