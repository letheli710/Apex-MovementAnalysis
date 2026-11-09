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

