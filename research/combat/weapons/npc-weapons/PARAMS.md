# NPC 武器：参数全表（自动生成）

由 `weapons/_tools/gen-params.mjs` 从 `research-src/s21-platform/scripts/weapons/*.txt` 生成，不要手改。`L` 是行号，字段名就是来源字段。全部是 S21 数据文件里的值；S3 dedi 的差异看同目录 `SYSTEM.md`。

## NPC Hemlok（`weapons/npc_weapon_hemlok.txt`）

**射击**：`fire_mode` automatic (L19)；`is_semi_auto` 1 (L20)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_basic_bolt (L27)；`fire_rate` 15.500000 (L141)；`burst_fire_count` 3 (L142)；`burst_fire_delay` 0.150000 (L143)

**弹药**：`ammo_pool_type` highcal (L16)；`ammo_clip_size` 18 (L99)；`ammo_min_to_fire` 1 (L100)；`ammo_default_total` 180 (L102)；`ammo_stockpile_max` 180 (L103)；`ammo_no_remove_from_stockpile` 1 (L104)；`reload_enabled` 1 (L151)；`empty_reload_only` 0 (L153)

**时间**：`holster_time` 0.600000 (L94)；`lower_time` 0.300000 (L95)；`raise_time` 0.600000 (L96)；`deployfirst_time` 1.250000 (L97)；`deploy_time` 0.900000 (L98)；`reload_time` 2.400000 (L144)；`reload_time_late1` 1.540000 (L145)；`reloadempty_time` 2.850000 (L146)；`reloadempty_time_late1` 2.000000 (L147)

**伤害**：`damage_flags` DF_BULLET (L22)；`damage_type` none (L23)；`pass_through_depth` 0 (L34)；`pass_through_damage_preserved_scale` 0.500000 (L35)；`explosion_damage` 0 (L52)；`explosionradius` 0 (L53)；`npc_damage_near_value` 8 (L105)；`npc_damage_far_value` 8 (L106)；`npc_damage_near_distance` 1500 (L109)；`npc_damage_far_distance` 2500 (L110)；`npc_min_engage_range` 0 (L119)；`npc_max_engage_range` 1250 (L121)；`npc_min_range` 0 (L122)；`npc_max_range` 2000 (L123)；`allow_headshots` 1 (L155)

**弹道**：`projectile_lifetime` 5.000000 (L33)；`bolt_hitsize` 0.000000 (L60)；`bolt_hitsize_grow1_time` 0.005000 (L61)；`bolt_hitsize_grow1_size` 0.100000 (L62)；`bolt_hitsize_grow2_time` 0.070000 (L63)；`bolt_hitsize_grow2_size` 0.180000 (L64)；`bolt_hitsize_growfinal_lerptime` 0.100000 (L65)；`bolt_hitsize_growfinal_size` 0.250000 (L66)；`projectile_drag_coefficient` 0.002500 (L67)；`projectile_gravity_scale` 1.300000 (L68)；`bolt_zero_distance` 1968.500000 (L69)；`projectile_launch_speed` 2500 (L70)；`bolt_gravity_enabled` 0 (L71)；`projectile_ricochet_max_count` 0 (L72)；`projectile_bounce_damage_reduction_scale` 0.500000 (L74)；`projectile_speed_reduction_factor` 0.720000 (L75)

**后坐**：`viewkick_move_scale` 1.000000 (L49)；`viewkick_duck_scale` 1.000000 (L50)；`viewkick_air_scale_ads` 2.000000 (L51)

## NPC L-STAR（`weapons/npc_weapon_lstar.txt`）

**射击**：`fire_mode` automatic (L9)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_lstar (L27)；`fire_rate` 12.000000 (L95)

**弹药**：`ammo_clip_size` 60 (L51)；`ammo_min_to_fire` 1 (L53)；`ammo_no_remove_from_clip` 1 (L54)；`ammo_no_remove_from_stockpile` 1 (L55)；`reload_enabled` 1 (L106)；`empty_reload_only` 0 (L108)

**时间**：`reload_time` 3.260000 (L96)；`reloadempty_time` 3.260000 (L97)；`deployfirst_time` 1.450000 (L98)；`deploy_time` 0.900000 (L99)；`holster_time` 0.400000 (L100)；`lower_time` 0.350000 (L101)；`raise_time` 0.750000 (L102)

**伤害**：`damage_flags` DF_BULLET \| DF_GIB (L25)；`critical_hit` 1 (L57)；`npc_damage_near_value` 15 (L59)；`npc_damage_far_value` 15 (L60)；`npc_damage_near_distance` 850 (L63)；`npc_damage_far_distance` 1750 (L64)；`npc_min_engage_range` 100 (L65)；`npc_max_engage_range` 1200 (L66)；`npc_min_range` 0 (L69)；`npc_max_range` 1750 (L70)；`allow_headshots` 1 (L110)；`headshot_distance` 2500 (L111)

**弹道**：`projectile_launch_speed` 1500 (L21)；`projectile_gravity_scale` 0.050000 (L22)；`projectile_drag_coefficient` 0.000000 (L23)；`projectile_lifetime` 4.000000 (L24)；`bolt_hitsize` 0.750000 (L48)；`bolt_gravity_enabled` 1 (L49)

**充能 / 热**：`charge_time` 2.400000 (L13)；`charge_cooldown_time` 2.450000 (L14)；`charge_cooldown_delay` 0.050000 (L15)；`charge_overheat_cooldown_time` 2.450000 (L16)；`charge_overheat_cooldown_delay` 0.050000 (L17)；`charge_overheats_when_full` 1 (L18)；`charge_remain_full_when_fired` 1 (L20)

**移动**：`primary_fire_does_not_block_sprint` 0 (L112)；`ads_move_speed_scale` 0.500000 (L113)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `death_spectre` | 126 | `projectile_launch_speed` 3000；`fire_rate` 30.000000；`bolt_hitsize` 0.500000；`npc_damage_near_value` 15；`npc_damage_far_value` 15；`npc_damage_near_value_titanarmor` 15；`npc_damage_far_value_titanarmor` 15；`npc_burst_radius_min_precision` 8.000000；`npc_burst_radius_max_precision` 6.000000；`npc_spread_cone_min_precision` 1.250000；`npc_spread_cone_max_precision` 0.850000；`npc_burst_radius_distribution_bias_min_precision` -0.250000；`npc_burst_radius_distribution_bias_max_precision` 0.750000；`npc_min_burst_min_precision` 3；`npc_max_burst_min_precision` 3；`npc_min_burst_max_precision` 3；`npc_max_burst_max_precision` 3 |

## NPC 霰弹（`weapons/npc_weapon_shotgun.txt`）

**射击**：`fire_mode` automatic (L11)；`is_semi_auto` 0 (L12)；`projectiles_per_shot` 8 (L28)；`blast_pattern` eva8 (L29)；`blast_pattern_zero_distance` 512.000000 (L30)；`blast_pattern_default_scale` 1.500000 (L31)；`fire_rate` 2.000000 (L66)；`burst_fire_delay` 1.500000 (L70)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_shotgun (L92)

**弹药**：`ammo_pool_type` shotgun (L14)；`ammo_min_to_fire` 1 (L15)；`ammo_per_shot` 1 (L16)；`ammo_clip_size` 8 (L17)

**时间**：`reload_time` 2.750000 (L67)；`reloadempty_time` 3.000000 (L68)；`deployfirst_time` 1.350000 (L69)

**伤害**：`damage_flags` DF_NO_SELF_DAMAGE (L18)；`damage_type` none (L19)；`npc_damage_near_value` 3 (L21)；`npc_damage_far_value` 3 (L22)；`npc_damage_near_distance` 256 (L25)；`npc_damage_far_distance` 512 (L26)；`critical_hit` 0 (L50)；`allow_headshots` 1 (L51)；`headshot_distance` 1500 (L52)；`npc_min_engage_range` 128 (L71)；`npc_max_engage_range` 384 (L72)；`npc_min_range` 128 (L75)；`npc_max_range` 512 (L76)；`npc_min_burst` 1 (L84)；`npc_max_burst` 2 (L85)；`npc_rest_time_between_bursts_min` 0.500000 (L86)；`npc_rest_time_between_bursts_max` 3.000000 (L87)

**弹道**：`projectile_launch_speed` 16000 (L33)；`bolt_gravity_enabled` 1 (L34)；`projectile_gravity_scale` 1.000000 (L35)；`projectile_drag_coefficient` 0.001000 (L36)；`projectile_lifetime` 1.000000 (L38)；`bolt_zero_distance` 984.299988 (L41)；`bolt_hitsize` 0.250000 (L42)；`bolt_hitsize_grow1_time` 0.025000 (L43)；`bolt_hitsize_grow1_size` 0.600000 (L44)；`bolt_hitsize_grow2_time` 0.100000 (L45)；`bolt_hitsize_grow2_size` 1.000000 (L46)；`bolt_hitsize_growfinal_lerptime` 0.100000 (L47)；`bolt_hitsize_growfinal_size` 1.000000 (L48)

## NPC 能量霰弹（`weapons/npc_weapon_energy_shotgun.txt`）

**射击**：`fire_mode` automatic (L10)；`is_semi_auto` 1 (L11)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_weapon_energy_shotgun (L14)；`projectiles_per_shot` 4 (L34)；`blast_pattern` energy_shotgun (L96)；`blast_pattern_zero_distance` 512.000000 (L97)；`blast_pattern_default_scale` 1.500000 (L98)；`fire_rate` 4.000000 (L113)；`rechamber_time` 1.100000 (L114)；`projectile_spread_choke_frac_1` 0.800000 (L124)；`projectile_spread_choke_frac_2` 0.650000 (L125)；`projectile_spread_choke_frac_3` 0.450000 (L126)；`projectile_spread_choke_frac_4` 0.150000 (L127)

**弹药**：`ammo_default_total` 100 (L68)；`ammo_stockpile_max` 100 (L69)；`ammo_no_remove_from_stockpile` 1 (L70)；`ammo_min_to_fire` 1 (L71)；`ammo_clip_size` 8 (L72)；`ammo_per_shot` 1 (L73)

**时间**：`reload_time` 2.500000 (L115)；`reload_time_late1` 2.200000 (L116)；`reloadempty_time` 3.500000 (L117)；`reloadempty_time_late1` 2.500000 (L118)；`deployfirst_time` 1.400000 (L121)

**伤害**：`impulse_force` 20 (L67)；`npc_damage_near_value` 10 (L78)；`npc_damage_far_value` 10 (L79)；`npc_damage_near_distance` 600 (L82)；`npc_damage_far_distance` 1200 (L83)；`npc_min_engage_range` 0 (L84)；`npc_max_engage_range` 250 (L85)；`npc_min_range` 0 (L88)；`npc_max_range` 800 (L89)；`headshot_distance` 3940 (L122)

**弹道**：`projectile_lifetime` 1.000000 (L31)；`projectile_drag_coefficient` 0.001000 (L33)；`projectile_launch_speed` 7000 (L35)；`bolt_gravity_enabled` 0 (L36)；`bolt_hitsize` 1.000000 (L37)

**扩散**：`spread_stand_hip` 5.000000 (L128)；`spread_stand_hip_run` 5.000000 (L129)；`spread_stand_hip_sprint` 5.000000 (L130)；`spread_crouch_hip` 5.000000 (L131)；`spread_air_hip` 5.000000 (L132)；`spread_stand_ads` 5.000000 (L133)；`spread_crouch_ads` 5.000000 (L134)；`spread_air_ads` 5.000000 (L135)；`spread_wallrunning` 5.000000 (L136)；`spread_wallhanging` 5.000000 (L137)

**充能 / 热**：`charge_time` 0.000000 (L19)；`charge_levels` 0 (L20)；`charge_level_base` 0 (L21)；`charge_cooldown_time` 1.000000 (L22)；`charge_cooldown_delay` 0.000000 (L23)；`charge_is_triggered_by_ADS` 1 (L24)；`charge_end_forces_fire` 0 (L25)；`charge_remain_full_when_fired` 0 (L26)

## Super Spectre 榴弹（`weapons/npc_weapon_super_spectre.txt`）

**射击**：`fire_mode` automatic (L7)；`fire_rate` 6.000000 (L56)

**弹药**：`ammo_stockpile_max` 350 (L37)；`ammo_clip_size` -1 (L38)；`ammo_default_total` 350 (L39)；`reload_enabled` 1 (L63)；`empty_reload_only` 0 (L65)

**时间**：`zoom_time_in` 0.100000 (L57)；`zoom_time_out` 0.100000 (L58)；`zoom_fov` 40 (L59)；`reload_time` 3.000000 (L60)

**伤害**：`damage_flags` DF_RAGDOLL \| DF_EXPLOSION (L14)；`explosion_inner_radius` 30 (L29)；`explosionradius` 80 (L30)；`damage_type` burn (L36)；`allow_headshots` 0 (L67)；`critical_hit` 0 (L68)

**弹道**：`bolt_hitsize` 30.000000 (L49)；`bolt_hitsize_grow1_time` 0.100000 (L50)；`bolt_hitsize_grow1_size` 30.000000 (L51)；`bolt_hitsize_grow2_time` 0.200000 (L52)；`bolt_hitsize_grow2_size` 40.000000 (L53)；`bolt_hitsize_growfinal_lerptime` 0.300000 (L54)；`bolt_hitsize_growfinal_size` 40.000000 (L55)

**扩散**：`spread_stand_hip` 0 (L70)；`spread_stand_ads` 0 (L71)；`spread_decay_rate` 5 (L72)；`spread_decay_delay` 0.200000 (L73)

**后坐**：`viewkick_spring` pistol (L75)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `aggressive_ai_fd` | 174 | `npc_damage_near_value_titanarmor` *0.7；`npc_damage_far_value_titanarmor` *0.7；`npc_damage_near_value` *0.7；`npc_damage_far_value` *0.7 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`aggressive_ai`

## Spider 喷吐（`weapons/npc_weapon_spider_jungle.txt`）

**射击**：`fire_rate` 0.667000 (L60)；`burst_fire_delay` 1.500000 (L61)

**伤害**：`damage_flags` DF_BULLET \| DF_NO_SELF_DAMAGE (L13)；`damage_type` none (L14)；`critical_hit` 0 (L36)；`allow_headshots` 1 (L37)；`headshot_distance` 600 (L38)；`npc_damage_near_value` 8 (L41)；`npc_damage_far_value` 6 (L42)；`npc_damage_near_distance` 208 (L45)；`npc_damage_far_distance` 600 (L46)；`npc_min_engage_range` 208 (L47)；`npc_max_engage_range` 832 (L48)；`npc_min_range` 208 (L51)；`npc_max_range` 832 (L52)；`npc_min_burst` 1 (L58)；`npc_max_burst` 3 (L59)

**弹道**：`projectile_launch_speed` 2250 (L9)；`projectile_gravity_scale` 0.050000 (L10)；`projectile_drag_coefficient` 0.000000 (L11)；`projectile_lifetime` 4.000000 (L12)；`bolt_hitsize` 1.250000 (L32)；`bolt_gravity_enabled` 1 (L33)；`bolt_zero_distance` 480 (L34)

## Boss 光束（`weapons/npc_weapon_boss_beam.txt`）

**射击**：`fire_mode` automatic (L12)；`is_semi_auto` 1 (L13)；`fire_rate` 8 (L80)

**弹药**：`ammo_stockpile_max` 200 (L14)；`ammo_clip_size` 200 (L15)；`ammo_default_total` 200 (L16)；`reload_enabled` 0 (L91)；`empty_reload_only` 0 (L93)

**时间**：`zoom_time_in` 0.100000 (L81)；`zoom_time_out` 0.100000 (L82)；`zoom_fov` 35 (L83)；`reload_time` 3.500000 (L84)；`reloadempty_time` 3.500000 (L85)；`holster_time` 0.010000 (L86)；`deploy_time` 0.010000 (L87)；`lower_time` 0.010000 (L88)；`raise_time` 0.010000 (L89)

**伤害**：`damage_flags` DF_GIB (L9)；`damage_type` bullet (L66)；`damage_near_distance` 15000 (L67)；`damage_far_distance` 15000 (L68)；`damage_near_value` 10 (L69)；`damage_far_value` 10 (L70)；`explosion_damage` 10 (L73)；`explosionradius` 100 (L76)；`impulse_force` 5000 (L77)；`critical_hit` 0 (L78)；`critical_hit_damage_scale` 2.700000 (L79)；`allow_headshots` 0 (L95)；`npc_min_range` 500 (L183)；`npc_max_range` 3200 (L184)；`npc_min_burst` 1 (L185)；`npc_max_burst` 1 (L186)；`npc_rest_time_between_bursts_min` 30 (L187)；`npc_rest_time_between_bursts_max` 45 (L188)；`npc_pre_fire_delay` 3.500000 (L189)；`npc_pre_fire_delay_interval` 3 (L190)

**扩散**：`spread_stand_hip` 3.000000 (L100)；`spread_stand_hip_run` 3.000000 (L101)；`spread_stand_ads` 0.350000 (L102)；`spread_stand_hip_sprint` 3 (L103)；`spread_crouch_hip` 3.000000 (L104)；`spread_crouch_ads` 0.350000 (L105)；`spread_air_hip` 3.000000 (L106)；`spread_air_ads` 0.500000 (L107)

**后坐**：`viewkick_spring` titan_arc (L109)；`viewkick_pitch_base` -1 (L110)；`viewkick_pitch_random` 0.500000 (L111)；`viewkick_pitch_softScale` 1 (L112)；`viewkick_pitch_hardScale` 0 (L113)；`viewkick_yaw_base` 0 (L114)；`viewkick_yaw_random` 0.500000 (L115)；`viewkick_yaw_softScale` 1 (L116)；`viewkick_yaw_hardScale` 0 (L117)

**充能 / 热**：`sustained_discharge_pulse_frequency` 0.100000 (L29)；`sustained_discharge_allow_melee` 0 (L30)；`sustained_discharge_require_input` 0 (L31)；`sustained_laser_enabled` 1 (L32)；`sustained_laser_radius` 40 (L35)；`sustained_laser_range` 6000 (L36)；`charge_time` 1.100000 (L43)；`charge_cooldown_time` 1.000000 (L44)；`charge_cooldown_delay` 1.000000 (L45)；`charge_end_forces_fire` 1 (L46)；`charge_require_input` 0 (L47)；`sustained_discharge_duration` 5 (L50)

## Boss 炮台火箭（`weapons/npc_weapon_boss_turret_rockets.txt`）

**射击**：`fire_mode` automatic (L6)；`is_semi_auto` 0 (L7)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_boss_turret_rockets (L9)；`fire_rate` 20 (L56)；`burst_fire_count` 16 (L57)

**弹药**：`ammo_no_remove_from_clip` 1 (L65)；`ammo_clip_size` 20 (L121)；`ammo_min_to_fire` 1 (L122)；`ammo_default_total` 40 (L140)；`ammo_stockpile_max` 40 (L141)；`ammo_no_remove_from_stockpile` 0 (L142)；`uses_ammo_pool` 0 (L144)；`reload_enabled` 1 (L178)；`empty_reload_only` 0 (L180)

**时间**：`zoom_time_in` 0.200000 (L161)；`zoom_time_out` 0.150000 (L162)；`zoom_fov` 55 (L163)；`reload_time` 3.000000 (L164)；`reload_time_late1` 1.980000 (L165)；`reloadempty_time` 3.000000 (L168)；`reloadempty_time_late1` 1.980000 (L169)；`holster_time` 0.500000 (L172)；`deploy_time` 0.800000 (L173)；`lower_time` 0.250000 (L174)；`raise_time` 0.300000 (L175)；`deployfirst_time` 1.250000 (L341)

**伤害**：`damage_type` burn (L28)；`npc_pre_fire_delay` 1.000000 (L39)；`npc_pre_fire_delay_interval` 2.000000 (L40)；`npc_damage_near_distance` 800 (L44)；`npc_damage_far_distance` 1200 (L45)；`npc_damage_near_value` 8 (L46)；`npc_damage_far_value` 8 (L47)；`npc_min_range` 256 (L50)；`npc_max_range` 20000 (L51)；`npc_min_burst` 16 (L52)；`npc_max_burst` 16 (L53)；`npc_rest_time_between_bursts_min` 1.000000 (L54)；`npc_rest_time_between_bursts_max` 2.000000 (L55)；`allow_headshots` 0 (L58)；`explosionradius` 200 (L59)；`impulse_force` 1 (L60)；`npc_min_engage_range` 256 (L61)；`npc_max_engage_range` 20000 (L62)；`critical_hit_damage_scale` 1.500000 (L116)；`explosion_inner_radius` 1 (L120)；`damage_shield_scale` 1 (L123)；`damage_near_value` 45 (L145)；`damage_far_value` 45 (L146)；`explosion_damage` 10 (L149)；`damage_near_distance` 1800 (L151)；`damage_far_distance` 15000 (L152)；`damage_headshot_scale` 1 (L160)；`critical_hit` 1 (L182)

**弹道**：`projectile_launch_speed` 1 (L18)

**扩散**：`spread_stand_hip` 0.500000 (L185)；`spread_stand_hip_run` 0.500000 (L186)；`spread_stand_hip_sprint` 0.500000 (L187)；`spread_crouch_hip` 0.500000 (L188)；`spread_air_hip` 0.500000 (L189)；`spread_stand_ads` 0.000000 (L190)；`spread_crouch_ads` 0.000000 (L191)；`spread_air_ads` 0.000000 (L192)；`spread_kick_on_fire_stand_hip` 0.500000 (L193)；`spread_kick_on_fire_crouch_hip` 0.500000 (L194)；`spread_kick_on_fire_air_hip` 0.500000 (L195)；`spread_kick_on_fire_stand_ads` 0.000000 (L196)；`spread_kick_on_fire_crouch_ads` 0.000000 (L197)；`spread_kick_on_fire_air_ads` 0.000000 (L198)；`spread_max_kick_stand_hip` 3.000000 (L199)；`spread_max_kick_crouch_hip` 3.000000 (L200)；`spread_max_kick_air_hip` 5.000000 (L201)；`spread_max_kick_stand_ads` 5.000000 (L202)；`spread_max_kick_crouch_ads` 5.000000 (L203)；`spread_max_kick_air_ads` 5.000000 (L204)；`spread_decay_rate` 15 (L205)；`spread_decay_delay` 0.200000 (L206)

**后坐**：`viewkick_spring` low_springconstant_launcher (L208)；`viewkick_pitch_base` -0.250000 (L209)；`viewkick_pitch_random` 0.350000 (L210)；`viewkick_pitch_softScale` 0.650000 (L211)；`viewkick_pitch_hardScale` 1.000000 (L212)；`viewkick_yaw_base` 0.100000 (L213)；`viewkick_yaw_random` 0.650000 (L214)；`viewkick_yaw_softScale` 0.750000 (L216)；`viewkick_yaw_hardScale` 0.500000 (L217)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `jump_kit` | 367 | `impulse_force` 1000；`impulse_force_explosions` 65000 |
| `extended_ammo` | 381 | `ammo_clip_size` ++15 |
| `delayed_shot` | 387 | `pre_ignition_damage_titanarmor` 20；`pre_ignition_npc_damage_titanarmor` 30 |
| `pas_fast_reload` | 404 | `reload_time` *0.7；`reload_time_late1` *0.7；`reloadempty_time` *0.7；`reloadempty_time_late1` *0.7 |
| `burn_mod_smr` | 413 | `damage_near_value` 90；`damage_far_value` 90；`damage_near_value_titanarmor` 250；`damage_far_value_titanarmor` 250 |
| `pas_fast_ads` | 427 | `zoom_time_in` *0.5；`zoom_time_out` *0.6 |
| `sp_s2s_settings` | 452 | `ammo_default_total` 1500；`ammo_stockpile_max` 1500；`ammo_no_remove_from_stockpile` 1 |
| `sp_hope_test` | 465 | `explosion_inner_radius` 50；`explosionradius` 150；`impulse_force` 10000；`impulse_force_explosions` 650000；`damage_near_value` 500；`damage_far_value` 500；`damage_near_value_titanarmor` 500；`damage_far_value_titanarmor` 500；`explosion_damage` 500；`explosion_damage_heavy_armor` 1000；`projectile_launch_speed` 5000；`ammo_no_remove_from_clip` 1 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`slammer`、`pro_screen`、`pas_fast_swap`、`tactical_cdr_on_kill`、`pas_run_and_gun`

## 等离子炮（`weapons/npc_weapon_plasma_cannon_overcharged.txt`）

**射击**：`fire_mode` automatic (L11)；`fire_rate` 5.500000 (L89)

**弹药**：`ammo_pool_type` special (L8)；`ammo_clip_size` 9999 (L36)；`ammo_size_segmented_reload` 1 (L37)；`ammo_min_to_fire` 1 (L39)；`ammo_default_total` 60 (L40)；`ammo_stockpile_max` 60 (L41)；`ammo_no_remove_from_clip` 0 (L42)；`ammo_no_remove_from_stockpile` 1 (L43)；`reloadsegment_time_loop` 0.820000 (L91)；`reloadsegment_time_end` 0.570000 (L92)；`reloadsegmentempty_time_end` 0.570000 (L93)；`reload_enabled` 1 (L101)；`reload_is_segmented` 1 (L102)；`empty_reload_only` 0 (L104)

**时间**：`reload_time` 0.950000 (L90)；`reloadempty_time` 0.950000 (L94)；`holster_time` 0.500000 (L95)；`deploy_time` 0.630000 (L96)；`lower_time` 0.250000 (L97)；`raise_time` 0.300000 (L98)

**伤害**：`damage_type` burn (L32)；`critical_hit` 0 (L34)；`critical_hit_damage_scale` 1.500000 (L35)；`damage_shield_scale` 1 (L38)；`npc_damage_near_value` 0 (L44)；`npc_damage_far_value` 0 (L45)；`npc_damage_near_distance` 0 (L48)；`npc_damage_far_distance` 0 (L49)；`explosion_inner_radius` 20 (L51)；`explosionradius` 50 (L52)；`impulse_force` 17000 (L57)；`npc_min_engage_range` 100 (L58)；`npc_max_engage_range` 3000 (L59)；`npc_min_range` 0 (L62)；`npc_max_range` 5000 (L63)；`allow_headshots` 0 (L106)

**弹道**：`projectile_launch_speed` 1000 (L113)；`projectile_gravity_scale` 0.350000 (L114)；`projectile_drag_coefficient` 0.005000 (L115)；`projectile_lifetime` 6.000000 (L116)；`bolt_gravity_enabled` 1 (L117)

**扩散**：`spread_stand_hip` 0.250000 (L122)；`spread_stand_hip_run` 0.250000 (L123)；`spread_stand_ads` 0.350000 (L124)；`spread_stand_hip_sprint` 0.250000 (L125)；`spread_crouch_hip` 0.250000 (L126)；`spread_crouch_ads` 0.350000 (L127)；`spread_air_hip` 0.250000 (L128)；`spread_air_ads` 0.350000 (L129)

## Goliath 投掷（`weapons/npc_weapon_goliath_throw.txt`）

**射击**：`fire_mode` offhand (L9)；`fire_rate` 2 (L61)

**弹药**：`reload_enabled` 0 (L65)；`empty_reload_only` 0 (L67)

**时间**：`deploy_time` 0.500000 (L62)

**伤害**：`damage_type` burn (L41)；`damage_near_distance` 1000 (L42)；`damage_far_distance` 3000 (L43)；`damage_near_value` 10 (L44)；`damage_far_value` 10 (L45)；`damage_flags` DF_RAGDOLL \| DF_EXPLOSION (L48)；`critical_hit` 0 (L49)；`explosion_inner_radius` 5 (L50)；`explosionradius` 320 (L51)；`impulse_force` 500 (L52)；`npc_min_range` 400 (L88)；`npc_max_range` 6000 (L89)

**弹道**：`projectile_launch_speed` 1100 (L80)；`projectile_gravity_scale` 0.700000 (L91)

**后坐**：`viewkick_spring` pistol (L86)

## Nessie（`weapons/npc_weapon_nessie.txt`）

**射击**：`fire_rate` 0.667000 (L62)；`burst_fire_delay` 0.250000 (L63)

**伤害**：`damage_flags` DF_BULLET \| DF_NO_SELF_DAMAGE (L13)；`damage_type` none (L14)；`critical_hit` 0 (L36)；`allow_headshots` 1 (L37)；`headshot_distance` 600 (L38)；`npc_damage_near_value` 24 (L41)；`npc_damage_far_value` 24 (L42)；`npc_damage_near_distance` 64 (L45)；`npc_damage_far_distance` 600 (L46)；`npc_min_engage_range` 32 (L47)；`npc_max_engage_range` 832 (L48)；`npc_min_range` 0 (L51)；`npc_max_range` 832 (L52)；`npc_min_burst` 1 (L60)；`npc_max_burst` 3 (L61)

**弹道**：`projectile_launch_speed` 2800 (L9)；`projectile_gravity_scale` 0.050000 (L10)；`projectile_drag_coefficient` 0.000000 (L11)；`projectile_lifetime` 5.000000 (L12)；`bolt_hitsize` 4 (L32)；`bolt_gravity_enabled` 1 (L33)；`bolt_zero_distance` 480 (L34)

## NPC 铝热（`weapons/npc_weapon_thermite_grenade.txt`）

**射击**：`fire_mode` offhand (L74)；`fire_rate` 0.680000 (L100)

**弹药**：`ammo_clip_size` 4 (L75)；`ammo_default_total` 1 (L76)；`ammo_min_to_fire` 1 (L78)；`ammo_per_shot` 1 (L79)；`ammo_stockpile_max` 4 (L80)；`regen_ammo_refill_rate` 0 (L81)；`regen_ammo_refill_start_delay` 0.000000 (L82)；`reload_enabled` 0 (L107)；`empty_reload_only` 0 (L109)

**时间**：`deployfirst_time` 1.700000 (L101)；`deploy_time` 1.700000 (L102)

**伤害**：`damage_type` burn (L48)；`damage_flags` DF_RAGDOLL \| DF_EXPLOSION (L49)；`critical_hit` 0 (L51)；`explosion_inner_radius` 5 (L52)；`explosionradius` 120 (L53)；`impulse_force` 3000 (L54)；`damage_near_distance` 1000 (L83)；`damage_far_distance` 3000 (L84)；`damage_near_value` 0 (L85)；`damage_far_value` 0 (L86)；`explosion_damage` 0 (L89)；`npc_min_range` 500 (L133)；`npc_max_range` 1200 (L134)；`allow_headshots` 0 (L135)

**弹道**：`projectile_launch_speed` 1300 (L116)；`projectile_ricochet_max_count` 16 (L119)

**充能 / 热**：`preburn_duration` 0.500000 (L66)

