### mp_weapon_smr 文件原值（`mp_weapon_smr.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_size` | 20 |  | extended_ammo=25 |
| `ammo_default_total` | 200 | 60 | extended_ammo=375 |
| `ammo_no_remove_from_clip` | 0 |  |  |
| `ammo_no_remove_from_stockpile` | 1 | 0 |  |
| `ammo_stockpile_max` | 200 | 100 | extended_ammo=375 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_rate` | 9 |  |  |
| `primary_fire_does_not_block_sprint` | — |  | pas_run_and_gun=1 |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 1 |  |  |
| `critical_hit` | 1 |  |  |
| `critical_hit_damage_scale` | 1.5 |  |  |
| `damage_far_distance` | 15000 |  |  |
| `damage_far_value` | 50 | 45 | burn_mod_smr=90 |
| `damage_far_value_titanarmor` | 115 | 175 | burn_mod_smr=250 |
| `damage_headshot_scale` | 1.25 |  |  |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 1800 |  |  |
| `damage_near_value` | 50 | 45 | burn_mod_smr=90 |
| `damage_near_value_titanarmor` | 115 | 175 | burn_mod_smr=250 |
| `damage_type` | bullet |  |  |
| `explosion_damage` | 15 |  |  |
| `explosion_damage_heavy_armor` | 150 |  |  |
| `explosion_inner_radius` | 1 |  |  |
| `explosionradius` | 16 |  |  |
| `impulse_force` | 1000 |  | jump_kit=1000 |
| `impulse_force_explosions` | — |  | jump_kit=65000 |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_drift_intensity` | 0.5 |  |  |
| `projectile_drift_windiness` | 10 |  |  |
| `projectile_launch_speed` | 3300 |  |  |
| `projectile_straight_radius_max` | 4 |  |  |
| `projectile_straight_radius_min` | 2 |  |  |
| `projectile_straight_time_max` | 2 |  |  |
| `projectile_straight_time_min` | 1.5 |  |  |
| `scripted_projectile_max_timestep` | 0.02 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.8 |  |  |
| `deployfirst_time` | 1.25 |  |  |
| `fast_swap_to` | 0 |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 3.0 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | 1.98 |  | pas_fast_reload=*0.7 |
| `reload_time_late2` | 1.36 |  |  |
| `reload_time_late3` | 0.80 |  |  |
| `reloadempty_time` | 3.0 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 1.98 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 1.36 |  |  |
| `reloadempty_time_late3` | 0.80 |  |  |

**开镜**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `zoom_fov` | 45 |  |  |
| `zoom_time_in` | 0.2 |  | pas_fast_ads=*0.5 |
| `zoom_time_out` | 0.15 |  | pas_fast_ads=*0.6 |

**散布**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `spread_air_ads` | 0.0 |  |  |
| `spread_air_hip` | 0.5 |  |  |
| `spread_crouch_ads` | 0.0 |  |  |
| `spread_crouch_hip` | 0.5 |  |  |
| `spread_decay_delay` | .2 |  |  |
| `spread_decay_rate` | 15 |  |  |
| `spread_kick_on_fire_air_ads` | 0.0 |  |  |
| `spread_kick_on_fire_air_hip` | 0.5 |  |  |
| `spread_kick_on_fire_crouch_ads` | 0.0 |  |  |
| `spread_kick_on_fire_crouch_hip` | 0.5 |  |  |
| `spread_kick_on_fire_stand_ads` | 0.0 |  |  |
| `spread_kick_on_fire_stand_hip` | 0.5 |  |  |
| `spread_max_kick_air_ads` | 5.0 |  |  |
| `spread_max_kick_air_hip` | 5.0 |  |  |
| `spread_max_kick_crouch_ads` | 5.0 |  |  |
| `spread_max_kick_crouch_hip` | 3.0 |  |  |
| `spread_max_kick_stand_ads` | 5.0 |  |  |
| `spread_max_kick_stand_hip` | 3.0 |  |  |
| `spread_stand_ads` | 0.0 |  |  |
| `spread_stand_hip` | 0.5 |  |  |
| `spread_stand_hip_run` | 0.5 |  |  |
| `spread_stand_hip_sprint` | 0.5 |  |  |

**后坐和视角**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `viewkick_ads_weaponFraction` | 0.1 |  |  |
| `viewkick_ads_weaponFraction_vmScale` | 0.5 |  |  |
| `viewkick_hipfire_weaponFraction` | 0.2 |  |  |
| `viewkick_hipfire_weaponFraction_vmScale` | 1.0 |  |  |
| `viewkick_pitch_base` | -0.25 |  |  |
| `viewkick_pitch_hardScale` | 1.0 |  |  |
| `viewkick_pitch_random` | 0.35 |  |  |
| `viewkick_pitch_softScale` | 0.65 |  |  |
| `viewkick_roll_base` | 0 |  |  |
| `viewkick_roll_hardScale` | 1.75 |  |  |
| `viewkick_roll_randomMax` | 0.25 |  |  |
| `viewkick_roll_randomMin` | 0.2 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_scale_firstshot_ads` | 0 |  |  |
| `viewkick_scale_firstshot_hipfire` | 0 |  |  |
| `viewkick_scale_max_ads` | 0.5 |  |  |
| `viewkick_scale_max_hipfire` | 0.65 |  |  |
| `viewkick_scale_min_ads` | 0.5 |  |  |
| `viewkick_scale_min_hipfire` | 0.65 |  |  |
| `viewkick_scale_valueDecayDelay` | 0.3 |  |  |
| `viewkick_scale_valueDecayRate` | 20 |  |  |
| `viewkick_scale_valueLerpEnd` | 15 |  |  |
| `viewkick_scale_valueLerpStart` | 0 |  |  |
| `viewkick_scale_valuePerShot` | 0.65 |  |  |
| `viewkick_spring` | low_springconstant_launcher |  |  |
| `viewkick_yaw_base` | 0.1 |  |  |
| `viewkick_yaw_hardScale` | 0.5 |  |  |
| `viewkick_yaw_random` | 0.65 |  |  |
| `viewkick_yaw_random_innerexclude` | 0.2 |  |  |
| `viewkick_yaw_softScale` | 0.75 |  |  |
| `viewpunch_multiplier` | 1.25 |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_aim_at_feet` | 0 |  |  |
| `npc_damage_far_distance` | 1200 |  |  |
| `npc_damage_far_value` | 25 |  |  |
| `npc_damage_far_value_titanarmor` | 150 | 100 |  |
| `npc_damage_near_distance` | 800 |  |  |
| `npc_damage_near_value` | 25 |  |  |
| `npc_damage_near_value_titanarmor` | 150 | 100 |  |
| `npc_lead_time_max_dist` | — |  |  |
| `npc_lead_time_min_dist` | — |  |  |
| `npc_lead_time_scale` | — |  |  |
| `npc_max_burst` | 11 |  |  |
| `npc_max_engage_range` | 1300 |  |  |
| `npc_max_engage_range_heavy_armor` | 3200 |  |  |
| `npc_max_range` | 8000 |  |  |
| `npc_min_burst` | 7 |  |  |
| `npc_min_engage_range` | 100 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_min_range` | 0 |  |  |
| `npc_miss_fast_player` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 0.6 |  |  |
| `npc_rest_time_between_bursts_min` | 0.4 |  |  |
| `proficiency_average_spreadscale` | 2 |  |  |
| `proficiency_good_spreadscale` | 1.4 |  |  |
| `proficiency_poor_spreadscale` | 3.0 |  |  |
| `proficiency_very_good_spreadscale` | 1.4 |  |  |

**其他**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `ignition_distance` | — |  | delayed_shot=35 |
| `ignition_effect` | — |  | delayed_shot=bullet_mastiff |
| `pre_ignition_damage` | — |  | delayed_shot=15 |
| `pre_ignition_damage_titanarmor` | — |  | delayed_shot=20 |
| `pre_ignition_impact_effect_table` | — |  | delayed_shot=exp_smr |
| `pre_ignition_npc_damage` | — |  | delayed_shot=80 |
| `pre_ignition_npc_damage_titanarmor` | — |  | delayed_shot=30 |
| `pre_ignition_speed` | — |  | delayed_shot=250 |
| `pre_ignition_trail_effect` | — |  | delayed_shot=bullet_mastiff |
| `show_grenade_indicator` | 0 |  |  |

