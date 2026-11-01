# Vantage 大招狙击枪：参数全表（自动生成）

由 `weapons/_tools/gen-params.mjs` 从 `research-src/s21-platform/scripts/weapons/*.txt` 生成，不要手改。`L` 是行号，字段名就是来源字段。全部是 S21 数据文件里的值；S3 dedi 的差异看同目录 `SYSTEM.md`。

## Sniper Mark（`weapons/mp_ability_sniper_ult.txt`）

**射击**：`fire_mode` offhandHybrid (L8)；`is_semi_auto` 1 (L10)；`OnWeaponPrimaryAttack` OnWeaponPrimaryAttack_ability_sniper_ult (L28)；`fire_rate` 3.000000 (L56)；`rechamber_time` 1.200000 (L70)

**弹药**：`ammo_clip_size` 240 (L41)；`ammo_default_total` 40 (L42)；`ammo_min_to_fire` 40 (L43)；`ammo_per_shot` 40 (L44)；`ammo_stockpile_max` 200 (L45)；`ammo_drains_to_empty_on_fire` 0 (L46)；`ammo_no_remove_from_clip` 0 (L47)；`ammo_no_remove_from_stockpile` 1 (L48)；`regen_ammo_refill_rate` 1.000000 (L50)；`regen_ammo_refill_start_delay` 0.000000 (L51)；`reload_enabled` 0 (L62)；`empty_reload_only` 0 (L63)

**时间**：`holster_time` 0.400000 (L57)；`deploy_time` 1.100000 (L58)；`lower_time` 0.400000 (L59)；`raise_time` 1.100000 (L60)；`zoom_fov` 19.858299 (L238)；`zoom_time_in` 0.500000 (L254)；`zoom_time_out` 0.500000 (L255)

**伤害**：`allow_headshots` 1 (L66)；`impulse_force` 5000 (L69)；`damage_near_value` 50 (L182)；`damage_far_value` 50 (L183)；`damage_very_far_value` 50 (L184)；`damage_near_distance` 7500 (L188)；`damage_far_distance` 10000 (L189)；`damage_very_far_distance` 12000 (L190)；`headshot_distance` 29528 (L191)；`damage_headshot_scale` 1.500000 (L192)；`damage_flags` DF_SNIPER \| DF_BULLET \| DF_KNOCK_BACK (L193)

**弹道**：`projectile_launch_speed` 34000 (L197)；`bolt_hitsize` 1 (L198)；`bolt_hitsize_grow1_time` 0.040000 (L199)；`bolt_hitsize_grow1_size` 5 (L200)；`bolt_hitsize_grow2_time` 0.100000 (L201)；`bolt_hitsize_grow2_size` 7 (L202)；`bolt_hitsize_growfinal_lerptime` 0.160000 (L203)；`bolt_hitsize_growfinal_size` 10 (L204)

**扩散**：`spread_stand_hip` 15 (L269)；`spread_stand_hip_run` 18 (L270)；`spread_stand_hip_sprint` 20 (L271)；`spread_crouch_hip` 15 (L272)；`spread_air_hip` 20 (L273)；`spread_stand_ads` 0 (L274)；`spread_crouch_ads` 0 (L275)；`spread_air_ads` 6.000000 (L276)；`spread_kick_on_fire_stand_hip` 1 (L277)；`spread_kick_on_fire_crouch_hip` 1 (L278)；`spread_kick_on_fire_air_hip` 1 (L279)；`spread_max_kick_stand_hip` 14.000000 (L280)；`spread_max_kick_crouch_hip` 12.000000 (L281)；`spread_max_kick_air_hip` 14.000000 (L282)；`spread_decay_rate` 1200 (L283)；`spread_decay_delay` 0.000000 (L284)

**后坐**：`viewkick_spring` doubletake (L73)；`viewkick_pitch_base` -0.800000 (L74)；`viewkick_pitch_random` 0.150000 (L75)；`viewkick_perm_pitch_base` 0.000000 (L76)；`viewkick_perm_pitch_random` 0.000000 (L77)；`viewkick_perm_pitch_random_innerexclude` 0.000000 (L78)；`viewkick_pitch_softScale` 1.200000 (L79)；`viewkick_pitch_hardScale` 0.900000 (L80)；`viewkick_yaw_base` 0.200000 (L81)；`viewkick_yaw_random` 0.150000 (L82)；`viewkick_perm_yaw_base` 0.000000 (L83)；`viewkick_perm_yaw_random` 0.000000 (L84)；`viewkick_perm_yaw_random_innerexclude` 0.000000 (L85)；`viewkick_yaw_softScale` 1.300000 (L86)；`viewkick_yaw_hardScale` 1.000000 (L87)

**Mods 的玩法覆盖**（`*x` 乘、`++x` 加，其余直接替换）：

| mod | 行 | 覆盖 |
|---|---|---|
| `arenas_tac_max_cooldown` | 306 | `ammo_regen_takes_from_stockpile` 1；`ammo_default_total` 200；`ammo_stockpile_max` 200 |
| `ultimates_charge_over_time_disabled` | 314 | `regen_ammo_refill_rate` 0 |
| `survival_armor_cooldown_mod` | 326 | `regen_ammo_refill_rate` *1.25 |
| `survival_armor_cooldown_extra_mod` | 332 | `regen_ammo_refill_rate` *1.5 |
| `survival_ammo_regen_paused` | 338 | `regen_ammo_refill_rate` *0.0 |
| `ability_in_effect_regen_paused` | 344 | `regen_ammo_refill_rate` *0.0 |
| `survival_ammo_regen_staging` | 350 | `regen_ammo_refill_rate` *5.0 |
| `amped_damage` | 356 | `sustained_laser_damage_scale` *0.83333；`damage_near_value` *1.2；`damage_far_value` *1.2；`damage_very_far_value` *1.2；`damage_near_value_titanarmor` *1.2；`damage_far_value_titanarmor` *1.2；`damage_very_far_value_titanarmor` *1.2 |
| `auto_loader` | 371 | `reload_time` *0.60；`reload_time_late1` *0.60；`reload_time_late2` *0.60；`reload_time_late3` *0.60；`reload_time_late4` *0.60；`reload_time_late5` *0.60；`reloadempty_time` *0.60；`reloadempty_time_late1` *0.60；`reloadempty_time_late2` *0.60；`reloadempty_time_late3` *0.60；`reloadempty_time_late4` *0.60；`reloadempty_time_late5` *0.60 |

没有玩法字段的 mod（只改外观或靠脚本 `HasMod`）：`ultimate_active`、`copycat_mod`

