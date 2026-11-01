# Rampart Sheila 枪械调参：参数全表（自动生成）

由 `weapons/_tools/gen-params.mjs` 从 `research-src/s21-platform/scripts/weapons/*.txt` 生成，不要手改。`L` 是行号，字段名就是来源字段。全部是 S21 数据文件里的值；S3 dedi 的差异看同目录 `SYSTEM.md`。

## Sheila 手持（`weapons/mp_weapon_mobile_hmg.txt`）

**射击**：`fire_mode` offhandHybrid (L12)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_mobile_hmg (L47)；`fire_rate` 20 (L170)

**弹药**：`ammo_clip_size` 173 (L112)；`ammo_min_to_fire` 43 (L114)；`ammo_per_shot` 43 (L115)；`regen_ammo_refill_rate` 1.440000 (L116)；`regen_ammo_refill_start_delay` 0.000000 (L117)；`ammo_default_total` 0 (L128)；`ammo_stockpile_max` 173 (L129)；`ammo_no_remove_from_stockpile` 1 (L130)；`uses_ammo_pool` 0 (L131)；`reload_enabled` 0 (L196)；`empty_reload_only` 0 (L200)

**时间**：`zoom_time_in` 1.250000 (L171)；`zoom_time_out` 1.000000 (L172)；`zoom_fov` 70 (L173)；`deploy_time` 1.600000 (L178)；`holster_time` 0.400000 (L179)；`raise_time` 1.600000 (L180)；`lower_time` 0.400000 (L181)；`reload_time` 8.667000 (L182)；`reload_time_late1` 7.367000 (L183)；`reloadempty_time` 8.667000 (L188)；`reloadempty_time_late1` 7.367000 (L189)；`deployfirst_time` 1.450000 (L395)

**伤害**：`damage_flags` DF_BULLET (L22)；`pass_through_depth` 0 (L63)；`pass_through_damage_preserved_scale` 1 (L64)；`damage_type` bullet (L110)；`critical_hit_damage_scale` 1.500000 (L111)；`critical_hit` 1 (L124)；`damage_shield_scale` 1 (L125)；`damage_near_value` 14 (L133)；`damage_far_value` 14 (L134)；`damage_very_far_value` 14 (L135)；`damage_near_distance` 1500 (L140)；`damage_far_distance` 2500 (L141)；`damage_very_far_distance` 4000 (L142)；`damage_headshot_scale` 2.000000 (L143)；`damage_leg_scale` 1.000000 (L144)；`npc_damage_near_value` 2 (L146)；`npc_damage_far_value` 2 (L147)；`npc_damage_near_distance` <KEEP_DEFAULT> (L150)；`npc_damage_far_distance` <KEEP_DEFAULT> (L151)；`npc_min_engage_range` 100 (L152)；`npc_max_engage_range` 1500 (L153)；`npc_min_range` 0 (L156)；`npc_max_range` 3000 (L157)；`npc_min_burst` 15 (L158)；`npc_max_burst` 20 (L159)；`npc_rest_time_between_bursts_min` 5.000000 (L160)；`npc_rest_time_between_bursts_max` 6.000000 (L161)；`allow_headshots` 1 (L202)；`headshot_distance` 2500 (L203)

**弹道**：`bolt_hitsize` 0.000000 (L53)；`bolt_hitsize_grow1_time` 0.005000 (L54)；`bolt_hitsize_grow1_size` 0.100000 (L55)；`bolt_hitsize_grow2_time` 0.070000 (L56)；`bolt_hitsize_grow2_size` 0.100000 (L57)；`bolt_hitsize_growfinal_lerptime` 0.100000 (L58)；`bolt_hitsize_growfinal_size` 0.100000 (L59)；`bolt_gravity_enabled` 1 (L60)；`projectile_gravity_scale` 1.000000 (L61)；`bolt_zero_distance` 2750.000000 (L62)；`projectile_launch_speed` 25000 (L65)；`projectile_lifetime` 5.000000 (L66)

**扩散**：`spread_stand_hip` 3.000000 (L216)；`spread_stand_hip_run` 3.000000 (L217)；`spread_stand_hip_sprint` 3.000000 (L218)；`spread_crouch_hip` 3.000000 (L219)；`spread_air_hip` 5.500000 (L220)；`spread_stand_ads` 3.000000 (L221)；`spread_crouch_ads` 3.000000 (L222)；`spread_air_ads` 5.500000 (L223)；`spread_kick_on_fire_stand_hip` 0.000000 (L224)；`spread_kick_on_fire_crouch_hip` 0.000000 (L225)；`spread_kick_on_fire_air_hip` 0.000000 (L226)；`spread_kick_on_fire_stand_ads` -0.180000 (L227)；`spread_kick_on_fire_crouch_ads` -0.180000 (L228)；`spread_kick_on_fire_air_ads` -0.080000 (L229)；`spread_max_kick_stand_hip` 8.000000 (L230)；`spread_max_kick_crouch_hip` 8.000000 (L231)；`spread_max_kick_air_hip` 8.000000 (L232)；`spread_max_kick_stand_ads` 0.000000 (L233)；`spread_max_kick_crouch_ads` 0.000000 (L234)；`spread_max_kick_air_ads` 0.000000 (L235)；`spread_min_kick` -2.500000 (L236)；`spread_decay_delay` 0.100000 (L237)；`spread_decay_rate` 12 (L396)

**后坐**：`viewkick_air_scale_ads` 4.000000 (L162)；`viewkick_pattern` rampart_turret (L240)；`viewkick_spring` lmg_vkp (L241)；`viewkick_yaw_base` 1.000000 (L246)；`viewkick_yaw_random` 1.000000 (L247)；`viewkick_yaw_softScale` 0.450000 (L249)；`viewkick_yaw_hardScale` 0.200000 (L250)；`viewkick_perm_pitch_base` 0 (L273)；`viewkick_perm_pitch_random` 0 (L274)；`viewkick_perm_yaw_base` 0 (L275)；`viewkick_perm_yaw_random` 0 (L276)；`viewkick_perm_yaw_random_innerexclude` 0.000000 (L277)；`viewkick_pitch_base` 2.000000 (L281)；`viewkick_pitch_random` 1.000000 (L282)；`viewkick_pitch_softScale` 0.250000 (L283)；`viewkick_pitch_hardScale` 0.200000 (L284)

**移动**：`ads_move_speed_scale` 0.400000 (L204)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `amped_damage` | 460 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `rampart_gunner` | 475 | `ammo_clip_size` 173；`reload_time` *0.75；`reload_time_late1` *0.75；`reload_time_late2` *0.75；`reload_time_late3` *0.75；`reload_time_late4` *0.75；`reload_time_late5` *0.75；`reloadempty_time` *0.75；`reloadempty_time_late1` *0.75；`reloadempty_time_late2` *0.75；`reloadempty_time_late3` *0.75；`reloadempty_time_late4` *0.75；`reloadempty_time_late5` *0.75；`ammo_clip_reload_max` *1.15 |
| `mobile_hmg_active` | 494 | `ammo_min_to_fire` 1；`regen_ammo_refill_rate` 0 |
| `survival_armor_cooldown_mod` | 509 | `regen_ammo_refill_rate` *1.25 |
| `upgrade_core_ult_cooldown_reduction` | 515 | `regen_ammo_refill_rate` *1.3333 |
| `upgrade_core_modify_spinup_time` | 521 | `zoom_time_in` 1.000000；`zoom_time_out` 0.800000；`ads_move_speed_scale` 0.600000；`raise_time` 1.200000 |
| `ultimates_charge_over_time_disabled` | 530 | `regen_ammo_refill_rate` 0 |
| `survival_armor_cooldown_extra_mod` | 542 | `regen_ammo_refill_rate` *1.5 |
| `survival_ammo_regen_paused` | 548 | `regen_ammo_refill_rate` *0.0 |
| `ability_in_effect_regen_paused` | 554 | `regen_ammo_refill_rate` *0.0 |
| `survival_ammo_regen_staging` | 560 | `regen_ammo_refill_rate` *5.0 |
| `elevator_shooter` | 566 | `spread_air_hip` *0.7；`spread_air_hip_moving` *0.7；`spread_air_ads` *0.7；`spread_air_ads_moving` *0.7 |
| `optic_cq_hcog_classic` | 576 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 60 |
| `optic_cq_hcog_bruiser` | 601 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 38.590698 |
| `optic_cq_holosight` | 626 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 60 |
| `optic_cq_holosight_variable` | 652 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 60 |
| `optic_ranged_hcog` | 681 | `zoom_time_in` 0.420000；`zoom_time_out` 0.360000；`zoom_fov` 26.275600 |
| `optic_ranged_aog_variable` | 709 | `zoom_time_in` 0.420000；`zoom_time_out` 0.360000；`zoom_fov` 38.590698 |
| `auto_loader` | 740 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`mobile_hmg_fast_switch`、`copycat_mod`

## Sheila 炮台（`weapons/mp_weapon_mounted_turret_weapon.txt`）

**射击**：`fire_mode` automatic (L13)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_mounted_turret_weapon (L45)；`fire_rate` 20 (L160)

**弹药**：`ammo_clip_size` 150 (L109)；`ammo_default_total` 300 (L116)；`ammo_stockpile_max` 300 (L117)；`ammo_no_remove_from_stockpile` 1 (L118)；`uses_ammo_pool` 0 (L119)；`ammo_min_to_fire` 1 (L120)；`reload_enabled` 1 (L186)；`empty_reload_only` 0 (L190)

**时间**：`zoom_time_in` 1.250000 (L161)；`zoom_time_out` 1.000000 (L162)；`zoom_fov` 70 (L163)；`deployfirst_time` 1.860000 (L167)；`deploy_time` 1.200000 (L168)；`holster_time` 0.600000 (L169)；`raise_time` 0.750000 (L170)；`lower_time` 0.350000 (L171)；`reload_time` 8.667000 (L172)；`reload_time_late1` 7.367000 (L173)；`reloadempty_time` 8.667000 (L178)；`reloadempty_time_late1` 7.367000 (L179)

**伤害**：`damage_flags` DF_BULLET (L20)；`pass_through_depth` 0 (L59)；`pass_through_damage_preserved_scale` 1 (L60)；`damage_type` bullet (L107)；`critical_hit_damage_scale` 1.500000 (L108)；`critical_hit` 1 (L112)；`damage_shield_scale` 1 (L113)；`damage_near_value` 14 (L123)；`damage_far_value` 14 (L124)；`damage_very_far_value` 14 (L125)；`damage_near_distance` 1500 (L130)；`damage_far_distance` 2500 (L131)；`damage_very_far_distance` 4000 (L132)；`damage_headshot_scale` 2.000000 (L133)；`damage_leg_scale` 1.000000 (L134)；`npc_damage_near_value` 2 (L136)；`npc_damage_far_value` 2 (L137)；`npc_damage_near_distance` <KEEP_DEFAULT> (L140)；`npc_damage_far_distance` <KEEP_DEFAULT> (L141)；`npc_min_engage_range` 100 (L142)；`npc_max_engage_range` 1500 (L143)；`npc_min_range` 0 (L146)；`npc_max_range` 3000 (L147)；`npc_min_burst` 15 (L148)；`npc_max_burst` 20 (L149)；`npc_rest_time_between_bursts_min` 5.000000 (L150)；`npc_rest_time_between_bursts_max` 6.000000 (L151)；`allow_headshots` 1 (L192)；`headshot_distance` 2500 (L193)

**弹道**：`bolt_hitsize` 0.000000 (L49)；`bolt_hitsize_grow1_time` 0.005000 (L50)；`bolt_hitsize_grow1_size` 0.100000 (L51)；`bolt_hitsize_grow2_time` 0.070000 (L52)；`bolt_hitsize_grow2_size` 0.100000 (L53)；`bolt_hitsize_growfinal_lerptime` 0.100000 (L54)；`bolt_hitsize_growfinal_size` 0.100000 (L55)；`bolt_gravity_enabled` 1 (L56)；`projectile_gravity_scale` 1.000000 (L57)；`bolt_zero_distance` 2750.000000 (L58)；`projectile_launch_speed` 25000 (L61)；`projectile_lifetime` 5.000000 (L62)

**扩散**：`spread_air_hip` 11.000000 (L153)；`spread_stand_hip` 3.000000 (L206)；`spread_stand_hip_run` 3.000000 (L207)；`spread_stand_hip_sprint` 4.000000 (L208)；`spread_crouch_hip` 3.000000 (L209)；`spread_stand_ads` 3.000000 (L210)；`spread_crouch_ads` 3.000000 (L211)；`spread_air_ads` 6.000000 (L212)；`spread_kick_on_fire_stand_hip` 0.000000 (L213)；`spread_kick_on_fire_crouch_hip` 0.000000 (L214)；`spread_kick_on_fire_air_hip` 0.000000 (L215)；`spread_kick_on_fire_stand_ads` -0.180000 (L216)；`spread_kick_on_fire_crouch_ads` -0.180000 (L217)；`spread_kick_on_fire_air_ads` 0.000000 (L218)；`spread_max_kick_stand_hip` 8.000000 (L219)；`spread_max_kick_crouch_hip` 8.000000 (L220)；`spread_max_kick_air_hip` 8.000000 (L221)；`spread_max_kick_stand_ads` 0.000000 (L222)；`spread_max_kick_crouch_ads` 0.000000 (L223)；`spread_max_kick_air_ads` 0.000000 (L224)；`spread_min_kick` -2.500000 (L225)；`spread_decay_rate` 3 (L226)；`spread_decay_delay` 0.100000 (L227)

**后坐**：`viewkick_air_scale_ads` 4.000000 (L152)；`viewkick_pattern` rampart_turret (L230)；`viewkick_spring` lmg_vkp (L231)；`viewkick_pitch_base` 1.000000 (L236)；`viewkick_pitch_random` 1.000000 (L237)；`viewkick_pitch_softScale` 0.275000 (L238)；`viewkick_pitch_hardScale` 0.200000 (L239)；`viewkick_yaw_base` 1.000000 (L240)；`viewkick_yaw_random` 1.000000 (L241)；`viewkick_yaw_softScale` 0.450000 (L243)；`viewkick_yaw_hardScale` 0.200000 (L244)；`viewkick_perm_pitch_base` 0 (L267)；`viewkick_perm_pitch_random` 0 (L268)；`viewkick_perm_yaw_base` 0 (L269)；`viewkick_perm_yaw_random` 0 (L270)；`viewkick_perm_yaw_random_innerexclude` 0.000000 (L271)

**充能 / 热**：`does_player_overheat` 0 (L22)

**移动**：`ads_move_speed_scale` 0.400000 (L194)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `amped_damage` | 437 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `rampart_gunner` | 452 | `reload_time_late1` 4.933000；`reload_time_late2` 3.867000；`reload_time_late3` 2.333000；`reload_time_late4` 1.567000；`reloadempty_time_late1` 4.933000；`reloadempty_time_late2` 3.867000；`reloadempty_time_late3` 2.333000；`reloadempty_time_late4` 1.567000；`reload_time` *0.75；`reload_time_late5` *0.75；`reloadempty_time` *0.75；`reloadempty_time_late5` *0.75；`ammo_clip_size` *1.15；`ammo_clip_reload_max` *1.15 |
| `upgrade_ult_one` | 471 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |
| `auto_loader` | 488 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |
| `elevator_shooter` | 505 | `spread_air_hip` *0.7；`spread_air_hip_moving` *0.7；`spread_air_ads` *0.7；`spread_air_ads_moving` *0.7 |
| `optic_cq_hcog_classic` | 515 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 60 |
| `optic_cq_hcog_bruiser` | 540 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 38.590698 |
| `optic_cq_holosight` | 565 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 60 |
| `optic_cq_holosight_variable` | 591 | `zoom_time_in` 0.360000；`zoom_time_out` 0.320000；`zoom_fov` 60 |
| `optic_ranged_hcog` | 620 | `zoom_time_in` 0.420000；`zoom_time_out` 0.360000；`zoom_fov` 26.275600 |
| `optic_ranged_aog_variable` | 648 | `zoom_time_in` 0.420000；`zoom_time_out` 0.360000；`zoom_fov` 38.590698 |

