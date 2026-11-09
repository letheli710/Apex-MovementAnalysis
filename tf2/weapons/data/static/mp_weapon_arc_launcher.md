### mp_weapon_arc_launcher 文件原值（`mp_weapon_arc_launcher.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_size` | 1 |  | extended_ammo=1 |
| `ammo_default_total` | 6 | 7 | extended_ammo=9 |
| `ammo_min_to_fire` | 1 |  |  |
| `ammo_no_remove_from_stockpile` | 0 |  | at_unlimited_ammo=1 |
| `ammo_stockpile_max` | 6 | 7 | extended_ammo=9 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `attack_button_presses_ads` | 1 |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_rate` | 2 |  |  |
| `move_speed_modifier` | 1.0 |  |  |
| `primary_fire_does_not_block_sprint` | — |  | pas_run_and_gun=1 |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 0 |  |  |
| `critical_hit` | 0 |  |  |
| `damage_far_distance` | 15000 |  |  |
| `damage_far_value` | 70 | 250 | burn_mod_arc_launcher=90 |
| `damage_far_value_titanarmor` | 1000 | 800 | burn_mod_arc_launcher=1350 |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 1200 |  |  |
| `damage_near_value` | 70 | 250 | burn_mod_arc_launcher=90 |
| `damage_near_value_titanarmor` | 1000 | 800 | burn_mod_arc_launcher=1350 |
| `damage_type` | burn |  |  |
| `explosion_damage` | 40 | 75 | burn_mod_arc_launcher=60 |
| `explosion_damage_heavy_armor` | 250 |  | burn_mod_arc_launcher=350 |
| `explosion_inner_radius` | 150 |  |  |
| `explosionradius` | 250 |  |  |
| `impulse_force` | 1 |  |  |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `bolt_gravity_enabled` | 0 |  |  |
| `bolt_hitsize` | 0.0 |  |  |
| `bolt_hitsize_grow1_size` | 1.0 |  |  |
| `bolt_hitsize_grow1_time` | 0.075 |  |  |
| `bolt_hitsize_grow2_size` | 4.0 |  |  |
| `bolt_hitsize_grow2_time` | 0.5 |  |  |
| `bolt_hitsize_growfinal_lerptime` | 1.5 |  |  |
| `bolt_hitsize_growfinal_size` | 25.0 |  |  |
| `grenade_show_indicator_to_owner` | 0 |  |  |
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_straight_radius_max` | 1 |  |  |
| `projectile_straight_radius_min` | 0 |  |  |
| `projectile_straight_time_max` | 20 |  |  |
| `projectile_straight_time_min` | 0.5 |  |  |
| `scripted_projectile_max_timestep` | 0.3 |  |  |
| `scripted_projectile_velocity` | 1 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.8 |  |  |
| `fast_swap_to` | 0 |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 3.35 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | — |  | pas_fast_reload=*0.7 |
| `reloadempty_time` | 3.35 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 1.8 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 1.35 |  |  |

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
| `spread_stand_ads` | 0.2 |  |  |
| `spread_stand_hip` | 3 |  |  |

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
| `viewkick_pitch_base` | -.2 |  |  |
| `viewkick_pitch_hardScale` | 5.0 |  |  |
| `viewkick_pitch_random` | 3.0 |  |  |
| `viewkick_pitch_softScale` | 1.3 |  |  |
| `viewkick_roll_base` | 0.0 |  |  |
| `viewkick_roll_hardScale` | 6.0 |  |  |
| `viewkick_roll_randomMax` | 0.7 |  |  |
| `viewkick_roll_randomMin` | 0.5 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_spring` | launcher |  |  |
| `viewkick_yaw_base` | -1.0 |  |  |
| `viewkick_yaw_hardScale` | 1.0 |  |  |
| `viewkick_yaw_random` | 0.0 |  |  |
| `viewkick_yaw_softScale` | 1.3 |  |  |
| `viewpunch_multiplier` | 2.9 |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_damage_far_value` | 0 |  |  |
| `npc_damage_near_value` | 0 |  |  |
| `npc_explosion_damage` | 33 |  |  |
| `npc_explosion_damage_heavy_armor` | 250 |  |  |
| `npc_max_burst` | 1 |  |  |
| `npc_max_engage_range_heavy_armor` | 3000 |  |  |
| `npc_max_range` | 4000 |  |  |
| `npc_min_burst` | 1 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_min_range` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 4 |  |  |
| `npc_rest_time_between_bursts_min` | 3.5 |  |  |
| `npc_use_ads_move_speed_scale` | 0 |  |  |
| `npc_vortex_block` | 0 |  |  |
| `proficiency_average_spreadscale` | 2.5 |  |  |
| `proficiency_good_spreadscale` | 1.6 |  |  |
| `proficiency_poor_spreadscale` | 2.5 |  |  |
| `proficiency_very_good_spreadscale` | 1.6 |  |  |

