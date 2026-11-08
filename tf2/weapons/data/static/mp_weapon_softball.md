### mp_weapon_softball 文件原值（`mp_weapon_softball.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_size` | 6 |  | extended_ammo=8 |
| `ammo_default_total` | 60 | 48 | extended_ammo=120 |
| `ammo_no_remove_from_clip` | 0 |  |  |
| `ammo_no_remove_from_stockpile` | 1 | 0 |  |
| `ammo_size_segmented_reload` | 1 |  |  |
| `ammo_stockpile_max` | 60 | 48 | extended_ammo=120 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_mode` | semi-auto |  |  |
| `fire_rate` | 2 |  |  |
| `primary_fire_does_not_block_sprint` | — |  | pas_run_and_gun=1 |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 0 |  |  |
| `critical_hit` | 0 |  |  |
| `critical_hit_damage_scale` | 1.5 |  |  |
| `damage_far_distance` | 1500 | 2000 |  |
| `damage_far_value` | 10 | 45 |  |
| `damage_far_value_titanarmor` | 0 | 45 |  |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 100 |  |  |
| `damage_near_value` | 10 | 45 |  |
| `damage_near_value_titanarmor` | 0 | 45 |  |
| `damage_type` | burn |  |  |
| `explosion_damage` | 90 | 80 | burn_mod_softball=150 |
| `explosion_damage_heavy_armor` | 330 | 170 | burn_mod_softball=530 |
| `explosion_inner_radius` | 50 |  |  |
| `explosionradius` | 150 |  |  |
| `impulse_force` | 7000 |  | jump_kit=7000 |
| `impulse_force_explosions` | — |  | jump_kit=65000 |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `grenade_bounce_extra_vertical_randomness` | 0.2 |  |  |
| `grenade_bounce_randomness` | 0.2 |  |  |
| `grenade_bounce_vel_frac_along_normal` | 0.5 |  |  |
| `grenade_bounce_vel_frac_shallow` | 0.47 |  |  |
| `grenade_bounce_vel_frac_sharp` | 0.28 |  |  |
| `grenade_roll_vel_frac_per_second` | 0.1 |  |  |
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_inherit_owner_velocity_scale` | 1 |  |  |
| `projectile_launch_speed` | 2500 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.63 |  |  |
| `fast_swap_to` | — |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_is_segmented` | 1 |  |  |
| `reload_time` | 0.95 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | — |  | pas_fast_reload=*0.7 |
| `reloadempty_time` | 0.95 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | — |  | pas_fast_reload=*0.7 |
| `reloadsegment_time_end` | 0.57 |  | pas_fast_reload=*0.7 |
| `reloadsegment_time_loop` | 0.82 |  | pas_fast_reload=*0.7 |
| `reloadsegmentempty_time_end` | 0.57 |  | pas_fast_reload=*0.7 |

**开镜**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `zoom_fov` | 45 |  |  |
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
| `npc_damage_far_value` | 0 | 20 |  |
| `npc_damage_far_value_titanarmor` | 0 | 20 |  |
| `npc_damage_near_value` | 0 | 20 |  |
| `npc_damage_near_value_titanarmor` | 0 | 20 |  |
| `npc_max_burst` | 1 |  |  |
| `npc_max_engage_range` | 2000 |  |  |
| `npc_max_engage_range_heavy_armor` | 3500 |  |  |
| `npc_max_range` | 8000 |  |  |
| `npc_min_burst` | 1 |  |  |
| `npc_min_engage_range` | 100 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_min_range` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 1 |  |  |
| `npc_rest_time_between_bursts_min` | 0.5 |  |  |
| `npc_self_explosion_safety` | 0 |  |  |
| `proficiency_average_spreadscale` | 10.0 |  |  |
| `proficiency_good_spreadscale` | 3.3 |  |  |
| `proficiency_poor_spreadscale` | 10.0 |  |  |
| `proficiency_very_good_spreadscale` | 3.3 |  |  |

**其他**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `show_grenade_indicator` | 1 |  |  |

