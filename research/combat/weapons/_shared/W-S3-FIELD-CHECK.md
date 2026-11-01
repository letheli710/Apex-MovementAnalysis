# 公共部件 W：S21 武器字段在服务端归谁处理（静态核对）

自动生成：`_tools/field-check.mjs` + `_tools/gen-field-check-md.mjs`。2026-11-01，只读文件，没启动游戏。

**更正**：这份记录第一版只搜了 `r5apex_ds.exe`，得出"energize、heat 在 dedi 上推断不工作"。**这个结论错了**：SDK 的 `server.dll` 把它们补回来了。现在的版本三个二进制都搜。

**方法**：把所有 `mp_weapon_* / npc_weapon_* / melee_* / mp_ability_*` 的 `.txt` 字段名，在本地 `r5apex_ds.exe`（S3 dedi）、`server.dll`（SDK）、`r5apex.exe`（S21 客户端）里搜索，再看 `vscripts` 里有没有这个词。源码核对用 `research-src/s21-r5sdk/src/game/`（提交 10077bb）；**没有核对这份源码和已安装的 `server.dll` 是不是同一版**。

**怎么读**：
- "SDK 补的"这一组只代表字符串在 server.dll 里，可能只是读入或别名。上面关键结论里写了的才核对过源码。
- 这是字符串证据，不是行为证据。"SDK 补的"只说明有人写了代码，和 S21 正版一样不一样要进游戏测。见 `../W1-SUMMARY.md`。
- 已滤掉音效、特效、UI、`ap_*` 等非玩法字段。
- 数据只有一份：本地安装的 `platform/scripts/weapons/*.txt` 和 `research-src` 的玩法字段完全相同（`_tools/diff-builds.mjs`，330 个文件相同），差别只有 `research-src` 多 21 个 `*_og.txt`（本地安装没有）。`viewkick_patterns.txt`、`blast_patterns.txt`、`vscripts/weapons/` 忽略行尾后也完全相同。所以 S21 和 S3 的差异不在数据文件，在**服务端谁来执行这些字段**。

统计（玩法字段）：S3 引擎原生认 525；S3 不认、SDK 补 142；服务端都不认但脚本读 98；服务端都不认、脚本也不读 37。

## 关键结论

| 机制 | 证据 | 含义 |
|---|---|---|
| Energize（Rampage、Sentinel） | `energize.cpp`（`sdk_energize_bridge` 默认 1）；`ForceEnergizeState` 在 `server.dll` 里 | SDK 重写，待实测 |
| Heat（Nemesis） | `shared/weapon_heat.cpp:384-392` 读 `has_heat_decay`、`heat_per_bullet`、`heat_mod_var0`；`sdk_weapon_heat_modvar_write` 默认 1（`:38`） | SDK 重写，待实测。`mp_weapon_nemesis.txt:44` 的回调注释仍然成立 |
| 点射 | `bridge_burst_fire_seed` 注释说 S3 服务端自己不给 `m_burstFireCount` 赋值（`weapon_heat.cpp:44-47`） | **S3 原生的点射是缺的，SDK 补上**。默认开 |
| 满蓄力保持 | `bridge_charge_hold_when_full`（`weapon_heat.cpp:51`）：引擎没这个设置 | SDK 补 |
| 蓄力下限 | `bridge_charge_min_required`（`weapon_heat.cpp:56`） | SDK 补（Havoc 门槛靠它） |
| 过热冷却 | `bridge_charge_overheat_cooldown`（`weapon_heat.cpp:61`） | SDK 补，默认 1 |
| 扩散下限 | `server/weapon_kv_s21_ext.cpp:175` 读 `spread_min_kick`；`server/bridge_zoom_gate.cpp:757-766` 对 `spread_min_kick ≥ 0` 的武器打警告 "dedi cannot reproduce this S21 term" | SDK **只读入，没发现使用方**，唯一用到它的是这条警告。Sheila 的值是 −2.5，不触发警告，要实测 |
| 分段重力、空气阻力 | `weapon_kv_s21_ext.cpp` 读 `projectile_gravity_scale_2 / _final`、`projectile_air_friction*`（头文件写"S21-only weapon KV keys the dedi schema cannot hold"） | SDK 读进来，但这个文件之外**没发现使用方**（flGravityScale2、flAirFriction2、flGravityScaleFinal）。推断不影响 dedi 弹道，要实测 |
| 蓄力倍伤 | `charge_additional_damage_multiplier` 在 SDK 里只是别名（`shared/weapon_script_vars.cpp:3243-3246`） | **最可能的真差异**：30-30 ×1.4 推断没生效 |
| 图案数量 | S3 上限 8，SDK 提到 128（`server/r1/blast_pattern.h:15-16`）；`blast_patterns.txt` 有 14 个 | 排在第 8 之后的图案依赖这个补丁 |
| 转速爬升、三段衰减 | `fire_rate_max*`、`damage_very_far_value` 在 S3 原生认 | 原生 |
| 脚本实现的 hop-up | `kinetic_*`、`smart_reload_*`、`marksmans_tempo_*`、`projectile_spread_choke_frac_*`、`blast_pattern_ads_scale` 引擎都不认，脚本读 | 不依赖引擎版本 |

## S3 不认、SDK `server.dll` 补的

| 字段 | 用到的武器文件数 | S21 客户端 | 脚本读它 | 例子 |
|---|---|---|---|---|
| `ads_force_firstperson` | 59 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_alternator_smg` |
| `allow_zoom_on_raise` | 1 | 有 | 否 | `mp_weapon_mobile_hmg` |
| `alt_hand_3p_attach_name` | 7 | 有 | 否 | `mp_ability_ammosteal`、`mp_ability_debuff_zone` |
| `althand_allow_mainhand_on_zipline` | 2 | 有 | 否 | `mp_ability_heartbeat_sensor`、`mp_ability_octane_stim` |
| `ammo_regen_takes_from_stockpile` | 10 | 有 | 是 | `mp_ability_companion_launch_entry`、`mp_ability_edge_grapple` |
| `battle_chatter_event` | 35 | 有 | 是 | `mp_ability_area_sonar_scan`、`mp_ability_echo_locator` |
| `can_energize_when_energized` | 5 | 有 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `charge_additional_damage_multiplier` | 2 | 有 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `charge_allow_hold_when_full` | 8 | 有 | 否 | `mp_ability_conduit_arc_flash`、`mp_ability_thermal_denial` |
| `charge_attack_min_charge_required` | 17 | 有 | 否 | `mp_weapon_autopistol_fusion`、`mp_weapon_autopistol_fusion_crate` |
| `charge_cooldown_time_post_fire` | 8 | 有 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `charge_curve_coefficients` | 4 | 有 | 否 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `charge_delay_when_triggered_by_ADS` | 2 | 有 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `charge_finish_primary_attack_on_cancel` | 2 | 有 | 否 | `mp_ability_phase_walk`、`mp_weapon_vortex_shield_offhand` |
| `charge_overheat_cooldown_delay` | 4 | 有 | 否 | `mp_weapon_lstar`、`mp_weapon_lstar_crate` |
| `charge_overheat_cooldown_time` | 90 | 有 | 否 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `charge_overheat_cooldown_time_late1` | 89 | 有 | 否 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `charge_overheat_cooldown_time_late2` | 89 | 有 | 否 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `charge_overheat_cooldown_time_late3` | 89 | 有 | 否 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `clone_sync_to_player` | 7 | 有 | 否 | `melee_agnostic_breachbeamwhip`、`melee_agnostic_whip` |
| `deflect_missile_impacts` | 2 | 有 | 否 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `deflect_missile_impacts_dot` | 2 | 有 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `deploy_allow_ads` | 2 | 有 | 是 | `mp_weapon_seer_heirloom_primary`、`mp_weapon_throwingknife` |
| `does_player_overheat` | 3 | 无 | 否 | `mp_weapon_mounted_turret_weapon`、`mp_weapon_throwingknife` |
| `energize_activity_time` | 5 | 有 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `energized_duration` | 5 | 有 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `energized_time_consumed_per_shot` | 5 | 有 | 否 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `fire_to_redirect_projectile_mid_flight` | 1 | 有 | 否 | `mp_ability_translocation` |
| `force_has_weapon_clone` | 84 | 有 | 是 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `grenade_angle_dependant_throw_max_speed_angle` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_angle_dependant_throw_min_speed` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_angle_dependant_throw_min_speed_angle` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_arc_indicator_max_duration` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_arc_indicator_show_during_toss` | 4 | 有 | 否 | `mp_ability_conduit_shield_mines_line`、`mp_ability_lifeline_halo` |
| `grenade_arc_indicator_show_floor_impact` | 1 | 有 | 否 | `mp_ability_revenant_shadow_pounce_free` |
| `grenade_arc_indicator_show_in_sprint_if_ready` | 8 | 有 | 否 | `mp_ability_conduit_shield_mines`、`mp_ability_fuse_bunker_buster` |
| `grenade_arc_indicator_show_landing_position` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_arc_indicator_show_on_raise_if_ready` | 8 | 有 | 否 | `mp_ability_conduit_shield_mines`、`mp_ability_fuse_bunker_buster` |
| `grenade_arc_indicator_show_while_airborne` | 2 | 有 | 否 | `mp_ability_conduit_shield_mines_line`、`mp_ability_translocation` |
| `grenade_arc_indicator_smooth` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_arc_indicator_smooth_radius` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_drop_to_ground_bounce_vel_frac` | 2 | 有 | 否 | `mp_ability_translocation`、`mp_weapon_arc_bolt` |
| `grenade_drop_to_ground_on_bounce` | 2 | 有 | 否 | `mp_ability_translocation`、`mp_weapon_arc_bolt` |
| `grenade_drop_velocity` | 2 | 有 | 否 | `mp_ability_translocation`、`mp_weapon_arc_bolt` |
| `grenade_ignore_friendly_players` | 1 | 有 | 否 | `mp_ability_translocation` |
| `grenade_ignore_planted_grenades` | 4 | 有 | 否 | `mp_weapon_grenade_emp`、`mp_weapon_grenade_pathy_shell` |
| `grenade_mover_destroy_when_planted` | 3 | 有 | 是 | `mp_ability_fuse_bunker_buster`、`mp_ability_translocation` |
| `grenade_touch_triggers_on_impact` | 48 | 有 | 否 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `grenade_use_mask_ability` | 12 | 有 | 否 | `mp_ability_crypto_drone`、`mp_ability_horizon_black_hole` |
| `grenade_view_launch_offset` | 19 | 有 | 否 | `mp_ability_area_cloak`、`mp_ability_copycat_kit` |
| `has_energized` | 5 | 有 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `has_heat_decay` | 4 | 无 | 否 | `mp_weapon_melee_bat`、`mp_weapon_nemesis` |
| `heartbeat_sensor_size` | 133 | 有 | 是 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `heat_decay_delay` | 4 | 无 | 否 | `mp_weapon_melee_bat`、`mp_weapon_nemesis` |
| `heat_decay_time` | 4 | 无 | 否 | `mp_weapon_melee_bat`、`mp_weapon_nemesis` |
| `heat_mod_var0` | 2 | 无 | 否 | `mp_weapon_nemesis`、`mp_weapon_nemesis_crate` |
| `heat_mod_var0_end` | 2 | 无 | 否 | `mp_weapon_nemesis`、`mp_weapon_nemesis_crate` |
| `heat_mod_var0_start` | 2 | 无 | 否 | `mp_weapon_nemesis`、`mp_weapon_nemesis_crate` |
| `heat_per_bullet` | 3 | 有 | 否 | `mp_weapon_nemesis`、`mp_weapon_nemesis_crate` |
| `hideForSkydive` | 12 | 有 | 是 | `melee_agnostic_prorookie`、`melee_newcastle_heirloom` |
| `is_akimbo_weapon` | 2 | 有 | 是 | `mp_weapon_semipistol`、`mp_weapon_shotgun_pistol` |
| `is_artifact` | 25 | 有 | 是 | `melee_agnostic_breachbeamsaber`、`melee_agnostic_breachbeamwhip` |
| `is_clacker` | 4 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_care_package` |
| `is_consumable` | 1 | 有 | 否 | `mp_ability_consumable` |
| `is_heirloom` | 73 | 有 | 是 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `is_twohanded_consumable` | 1 | 有 | 否 | `mp_ability_consumable` |
| `l_trig_custom_mode` | 10 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_3030` |
| `l_trig_custom_str` | 10 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_3030` |
| `lifesteal_heal_percent` | 2 | 有 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `melee_allow_held` | 3 | 有 | 否 | `mp_weapon_melee_bat`、`mp_weapon_power_sword` |
| `melee_has_gesture` | 4 | 有 | 否 | `melee_agnostic_veloform`、`mp_weapon_agnostic_karambit_primary` |
| `melee_knockback_velocity_magnitude` | 84 | 有 | 是 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `object_placement_clearance_behind` | 6 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_cover_wall` |
| `object_placement_distance_max` | 9 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_phase_door` |
| `object_placement_distance_to_ground_max` | 8 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_redeploy_balloon` |
| `object_placement_drop_to_ground_offset_max` | 7 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_redeploy_balloon` |
| `object_placement_force_upright` | 2 | 有 | 否 | `mp_ability_redeploy_balloon`、`mp_ability_revenant_death_totem` |
| `object_placement_ground_penetration_max` | 7 | 有 | 是 | `mp_ability_beamstick_stave`、`mp_ability_redeploy_balloon` |
| `object_placement_hill_angle_max` | 6 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_cover_wall` |
| `object_placement_ignore_players` | 5 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_revenant_death_totem` |
| `object_placement_last_good_angle_max` | 8 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_phase_door` |
| `object_placement_last_good_distance_max` | 8 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_phase_door` |
| `object_placement_model` | 8 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_redeploy_balloon` |
| `object_placement_percent_off_ledge_max` | 7 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_revenant_death_totem` |
| `object_placement_run_mode` | 3 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_phase_door` |
| `object_placement_special` | 1 | 有 | 否 | `mp_ability_phase_door` |
| `object_placement_top_distance_pierce_max` | 6 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_cover_wall` |
| `object_placement_top_side_percent_pierce_max` | 6 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_cover_wall` |
| `object_placement_trace_through_turrets` | 1 | 有 | 否 | `mp_weapon_cover_wall` |
| `object_placement_use_top_trace` | 6 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_weapon_cover_wall` |
| `object_placement_vehicle_offset` | 1 | 有 | 否 | `mp_weapon_mounted_turret_placeable` |
| `object_placer` | 8 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_phase_door` |
| `offhand_allow_swap_to_on_zipline` | 15 | 有 | 否 | `mp_ability_armored_leap`、`mp_ability_drone_rider` |
| `offhand_allows_inpect` | 4 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_charge_gauntlet` |
| `offhand_cancelled_by_melee` | 103 | 有 | 是 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `offhand_clear_zoom_on_activate` | 1 | 有 | 否 | `mp_weapon_mobile_hmg` |
| `offhand_deactivate_on_jump_toggle_or_release` | 2 | 有 | 否 | `mp_ability_drone_rider`、`mp_ability_valk_jets` |
| `offhand_disable_other_offhands` | 4 | 有 | 否 | `mp_ability_area_sonar_scan`、`mp_ability_holopilot` |
| `offhand_holds_on_tactical` | 1 | 有 | 否 | `mp_ability_valk_jets` |
| `offhand_hybrid_alt_hand_uses_attack_button` | 2 | 有 | 否 | `mp_ability_stone_defense`、`mp_weapon_arc_bolt` |
| `offhand_hybrid_reset_shot_count_on_attack` | 5 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_charge_gauntlet` |
| `offhand_hybrid_tracks_projectiles` | 2 | 有 | 否 | `mp_ability_stone_defense`、`mp_weapon_arc_bolt` |
| `offhand_include_primary_activity_mods` | 7 | 有 | 否 | `mp_ability_black_market`、`mp_ability_fuse_bunker_buster` |
| `offhand_instant_swap_to_offhand` | 6 | 有 | 否 | `mp_ability_companion_launch`、`mp_ability_companion_launch_entry` |
| `offhand_interrupt_climbing` | 1 | 有 | 否 | `mp_ability_revenant_shadow_pounce_free` |
| `offhand_match_player_skin` | 100 | 有 | 否 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `offhand_only_swap_to_on_ground` | 1 | 有 | 否 | `mp_weapon_arc_wave` |
| `offhand_restore_after_melee` | 3 | 有 | 是 | `mp_ability_sniper_ult`、`mp_weapon_charge_gauntlet` |
| `offhand_switch_slot` | 1 | 有 | 否 | `mp_ability_valk_cluster_missile` |
| `offhand_wants_first_deploy` | 4 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_charge_gauntlet` |
| `player_overheat_per_bullet` | 21 | 无 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `projectile_air_friction` | 5 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_translocation` |
| `projectile_air_friction_2` | 9 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_shield_throw` |
| `projectile_air_friction_final` | 9 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_shield_throw` |
| `projectile_gravity_scale_2` | 11 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_shield_throw` |
| `projectile_gravity_scale_final` | 11 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_shield_throw` |
| `projectile_gravity_scale_time_2` | 12 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_shield_throw` |
| `projectile_gravity_scale_time_final` | 11 | 有 | 否 | `mp_ability_fuse_bunker_buster`、`mp_ability_shield_throw` |
| `projectile_inherit_base_velocity_scale` | 5 | 有 | 否 | `mp_weapon_bow_ult_missile`、`mp_weapon_grenade_pathy_shell` |
| `projectile_muzzle_offset_decay_max_time` | 1 | 有 | 否 | `mp_weapon_throwingknife` |
| `projectile_predict_move_to_impact` | 2 | 有 | 否 | `mp_ability_phase_door`、`mp_weapon_throwingknife` |
| `projectile_trail_start_from_origin` | 4 | 有 | 否 | `mp_ability_translocation`、`mp_weapon_bow_ult_missile` |
| `r_trig_custom_mode` | 36 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_black_market` |
| `r_trig_custom_str` | 49 | 有 | 否 | `mp_ability_beamstick_stave`、`mp_ability_black_market` |
| `regen_ammo_forced_delay` | 2 | 有 | 否 | `mp_ability_lifeline_follow_medic`、`mp_weapon_ferro_wall` |
| `reload_allow_ads` | 5 | 有 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `show_grenade_indicator_to_owner` | 31 | 有 | 否 | `mp_ability_ammosteal`、`mp_ability_debuff_zone` |
| `spread_air_ads_moving` | 81 | 有 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `spread_air_hip_moving` | 81 | 有 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `spread_min_kick` | 20 | 有 | 否 | `mp_weapon_alternator_smg`、`mp_weapon_alternator_smg_crate` |
| `spread_update_hipfire_in_ads` | 18 | 有 | 否 | `mp_weapon_alternator_smg`、`mp_weapon_alternator_smg_crate` |
| `targeting_laser_beam_length_1p` | 26 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_alternator_smg` |
| `targeting_laser_beam_length_3p_enemy` | 26 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_alternator_smg` |
| `targeting_laser_beam_length_3p_friendly` | 26 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_alternator_smg` |
| `targeting_laser_enabled` | 30 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_alternator_smg` |
| `targeting_laser_range` | 26 | 有 | 否 | `mp_ability_sniper_ult`、`mp_weapon_alternator_smg` |
| `tergeting_laser_use_forward_direction` | 22 | 有 | 否 | `mp_weapon_alternator_smg`、`mp_weapon_alternator_smg_crate` |
| `toss_has_post_loop` | 2 | 有 | 否 | `mp_ability_revenant_shadow_pounce_free`、`mp_ability_translocation` |
| `toss_hides_world_model` | 4 | 有 | 否 | `mp_ability_ammosteal`、`mp_ability_debuff_zone` |
| `update_player_last_fire_time` | 50 | 有 | 否 | `mp_ability_ammosteal`、`mp_ability_area_sonar_scan` |
| `use_akimbo_damage_source` | 2 | 无 | 否 | `mp_weapon_semipistol`、`mp_weapon_shotgun_pistol` |
| `weaponBaseClass` | 58 | 无 | 否 | `mp_weapon_3030_crate`、`mp_weapon_alternator_smg_crate` |

## 服务端都不认，脚本读

| 字段 | 用到的武器文件数 | S21 客户端 | 脚本读它 | 例子 |
|---|---|---|---|---|
| `ads_dof_disable` | 53 | 无 | 是 | `mp_ability_overdrive_tac_slide_gate`、`mp_weapon_agnostic_breachbeamsaber_primary` |
| `affected_by_gravity_lift` | 1 | 无 | 是 | `mp_weapon_arc_bolt` |
| `airburst_distance` | 3 | 无 | 是 | `mp_weapon_semipistol`、`mp_weapon_semipistol_crate` |
| `airburst_pattern_scale` | 3 | 无 | 是 | `mp_weapon_semipistol`、`mp_weapon_semipistol_crate` |
| `airburst_pellet_count` | 3 | 无 | 是 | `mp_weapon_semipistol`、`mp_weapon_semipistol_crate` |
| `allow_gibraltar_shield` | 105 | 无 | 是 | `melee_agnostic_breachbeam`、`melee_agnostic_breachbeamsaber` |
| `battle_chatter_event_fuse` | 6 | 无 | 是 | `mp_weapon_ball_noncombat`、`mp_weapon_frag_grenade` |
| `blast_pattern_ads_scale` | 10 | 无 | 是 | `mp_weapon_mastiff`、`mp_weapon_mastiff_crate` |
| `burn_damage` | 11 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_duration` | 5 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_segment_height` | 5 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_segment_radius` | 5 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_segment_spacing_dist` | 4 | 无 | 是 | `mp_ability_thermal_denial`、`mp_weapon_mortar_ring` |
| `burn_segments` | 4 | 无 | 是 | `mp_ability_thermal_denial`、`mp_weapon_mortar_ring` |
| `burn_stack_debounce` | 11 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_stacks_max` | 11 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_tick_rate` | 11 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `burn_time` | 11 | 无 | 是 | `mp_ability_fire_wave`、`mp_ability_thermal_denial` |
| `center_dot_helper_min_charge_level` | 2 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `chargeup_time` | 1 | 无 | 是 | `npc_weapon_boss_beam` |
| `damage_indicator_model` | 7 | 无 | 是 | `mp_ability_fuse_bunker_buster`、`mp_weapon_ball_noncombat` |
| `disguise_ability` | 9 | 无 | 是 | `mp_ability_copycat_kit`、`mp_ability_copycat_kit_ash_phase_blade` |
| `does_not_interrupt_cloak` | 60 | 无 | 是 | `mp_ability_area_cloak`、`mp_ability_area_sonar_scan` |
| `drops_on_death` | 51 | 无 | 是 | `mp_ability_area_cloak`、`mp_ability_armored_leap` |
| `energized_consumable` | 5 | 无 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `energized_consumable_needed_amount` | 5 | 无 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `energized_max_reenergize_frac` | 5 | 无 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `energized_reenergize_prompt_frac` | 5 | 无 | 是 | `mp_weapon_bow_crate`、`mp_weapon_dragon_lmg` |
| `fuel_cooldown_sec` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `grenade_disc_throw` | 47 | 无 | 是 | `mp_ability_area_cloak`、`mp_ability_crypto_drone` |
| `is_hmg_weapon` | 2 | 无 | 是 | `mp_weapon_mobile_hmg`、`mp_weapon_mounted_turret_placeable` |
| `is_Melee_Weapon` | 59 | 无 | 是 | `melee_artifact_dagger`、`melee_artifact_sword` |
| `is_turret_weapon` | 1 | 无 | 是 | `mp_weapon_mounted_turret_weapon` |
| `kinetic_ammo_to_load` | 18 | 无 | 是 | `mp_weapon_energy_shotgun`、`mp_weapon_energy_shotgun_crate` |
| `kinetic_load_additive_delay` | 18 | 无 | 是 | `mp_weapon_energy_shotgun`、`mp_weapon_energy_shotgun_crate` |
| `kinetic_load_delay` | 18 | 无 | 是 | `mp_weapon_energy_shotgun`、`mp_weapon_energy_shotgun_crate` |
| `kinetic_load_max_delay` | 18 | 无 | 是 | `mp_weapon_energy_shotgun`、`mp_weapon_energy_shotgun_crate` |
| `kinetic_load_sfx` | 18 | 无 | 是 | `mp_weapon_energy_shotgun`、`mp_weapon_energy_shotgun_crate` |
| `launcher_vel_z` | 2 | 无 | 是 | `mp_weapon_melee_bat`、`mp_weapon_titan_sword` |
| `leveled_pickup` | 203 | 无 | 是 | `mp_ability_area_cloak`、`mp_ability_area_sonar_scan` |
| `marksmans_tempo_fadeoff_match_grace_time` | 4 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `marksmans_tempo_fadeoff_on_fire` | 4 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `marksmans_tempo_fadeoff_on_perfect_moment` | 4 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `marksmans_tempo_grace_time` | 4 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `marksmans_tempo_grace_time_in_tempo` | 4 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `marksmans_tempo_required_shots` | 4 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `melee_block_charge_scale` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `melee_block_max_damage` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `melee_block_min_damage` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `melee_block_scale` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `melee_block_scale_super` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `melee_block_sword_knockback` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `melee_block_sword_slow` | 2 | 无 | 是 | `mp_weapon_power_sword`、`mp_weapon_titan_sword` |
| `offhand_allow_player_interact` | 5 | 无 | 是 | `mp_ability_sniper_ult`、`mp_weapon_charge_gauntlet` |
| `owner_damage_scale` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `owner_damage_scale_fort` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `owner_damage_scale_super` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `owner_damage_scale_super_fort` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `passive` | 1 | 无 | 是 | `npc_weapon_boss_beam` |
| `preburn_duration` | 4 | 无 | 是 | `mp_ability_thermal_denial`、`mp_weapon_mortar_ring` |
| `projectile_ignores_vortex` | 61 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `projectile_launch_speed_full_charge` | 2 | 无 | 是 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `projectile_launch_speed_full_charge_shatter_arrows` | 1 | 无 | 是 | `mp_weapon_bow` |
| `projectile_spread_choke_frac_1` | 7 | 无 | 是 | `mp_weapon_doubletake`、`mp_weapon_doubletake_crate` |
| `projectile_spread_choke_frac_2` | 7 | 无 | 是 | `mp_weapon_doubletake`、`mp_weapon_doubletake_crate` |
| `projectile_spread_choke_frac_3` | 7 | 无 | 是 | `mp_weapon_doubletake`、`mp_weapon_doubletake_crate` |
| `projectile_spread_choke_frac_4` | 7 | 无 | 是 | `mp_weapon_doubletake`、`mp_weapon_doubletake_crate` |
| `script_optic_toggle_name` | 3 | 无 | 是 | `mp_weapon_buster_rifle`、`mp_weapon_sniper` |
| `secondary_ammo_pool_type` | 95 | 无 | 是 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `shock_damage` | 1 | 无 | 是 | `mp_weapon_arc_bolt` |
| `shock_radius` | 1 | 无 | 是 | `mp_weapon_arc_bolt` |
| `should_destroy_doors` | 2 | 无 | 是 | `mp_ability_wrecking_ball`、`mp_weapon_mobile_hmg` |
| `skullpiercer_elite_damage` | 1 | 无 | 是 | `mp_weapon_wingman_crate` |
| `slam_damage_max` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_damage_min` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_damage_scale` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_force_max` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_force_min` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_height_required` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_radius_inner` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_radius_outer` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `slam_vel_z` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `smart_reload_overload_ammo_required` | 14 | 无 | 是 | `mp_weapon_auto_hemlok`、`mp_weapon_auto_hemlok_crate` |
| `sonic_blast_delay` | 1 | 无 | 是 | `mp_ability_sonic_blast` |
| `start_fuse_on_launch` | 45 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_debuff_zone` |
| `stick_drone` | 60 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `stick_npc` | 61 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `stick_pilot` | 61 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `stick_titan` | 58 | 无 | 是 | `mp_ability_area_cloak`、`mp_ability_beamstick_stave` |
| `super_active_sec` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `super_cooldown_sec` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `super_max` | 1 | 无 | 是 | `mp_weapon_titan_sword` |
| `trophy_system_ignores` | 140 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_area_cloak` |
| `trophy_system_intercept_large` | 4 | 无 | 是 | `mp_weapon_creeping_bombardment_weapon`、`mp_weapon_defensive_bombardment_triple_weapon` |
| `vortex_refire_behavior` | 155 | 无 | 是 | `mp_ability_ammosteal`、`mp_ability_armored_leap` |
| `wave_max_count` | 1 | 无 | 是 | `mp_weapon_arc_wave` |
| `wave_step_dist` | 1 | 无 | 是 | `mp_weapon_arc_wave` |
| `weaponSubClass` | 80 | 无 | 是 | `mp_weapon_3030`、`mp_weapon_3030_crate` |

## 服务端都不认，脚本也不读（数据里写了，服务端推断无效；客户端可能用）

| 字段 | 用到的武器文件数 | S21 客户端 | 脚本读它 | 例子 |
|---|---|---|---|---|
| `akimbo_deploy_holsters_althand` | 2 | 无 | 否 | `mp_weapon_semipistol`、`mp_weapon_shotgun_pistol` |
| `arc_switch_activator` | 6 | 无 | 否 | `mp_weapon_flash_shield`、`mp_weapon_handheld_breach` |
| `bob_tilt_angle` | 7 | 无 | 否 | `mp_weapon_shotgun_pistol`、`mp_weapon_shotgun_pistol_crate` |
| `burn_damage_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_damage_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_duration_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_duration_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_segment_height_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_segment_height_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_segment_radius_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_segment_radius_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_stack_debounce_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_stack_debounce_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_stacks_max_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_stacks_max_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_tick_rate_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_tick_rate_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_time_detonate` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `burn_time_running` | 1 | 无 | 否 | `mp_ability_self_destruct` |
| `center_dot_helper_min_charge_level_optic_clamp` | 2 | 无 | 否 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `dev_menu_type` | 11 | 无 | 否 | `mp_ability_echo_locator`、`mp_ability_horizon_black_hole` |
| `dialog_core_activated` | 1 | 无 | 否 | `npc_weapon_boss_beam` |
| `dialog_core_online` | 1 | 无 | 否 | `npc_weapon_boss_beam` |
| `entity_uses_emissive_events` | 13 | 无 | 否 | `melee_hook_sword`、`melee_seer_heirloom` |
| `fully_heated_mod` | 3 | 无 | 否 | `mp_weapon_melee_bat`、`mp_weapon_nemesis` |
| `grenade_inherit_owner_velocity` | 24 | 无 | 否 | `mp_ability_area_cloak`、`mp_ability_crypto_drone` |
| `hammer_point_bullet` | 2 | 无 | 否 | `mp_weapon_3030`、`mp_weapon_3030_crate` |
| `item_flags` | 1 | 无 | 否 | `mp_weapon_mapedit_tool` |
| `npc_lead_time_max_dist` | 1 | 无 | 否 | `npc_weapon_super_spectre` |
| `npc_lead_time_min_dist` | 1 | 无 | 否 | `npc_weapon_super_spectre` |
| `npc_lead_time_scale` | 1 | 无 | 否 | `npc_weapon_super_spectre` |
| `npc_use_normal_duration` | 1 | 无 | 否 | `mp_ability_gibraltar_shield` |
| `offhand_switch_on_charge_end_no_attack` | 3 | 无 | 否 | `mp_weapon_bow_ult_missile`、`mp_weapon_mortar_ring` |
| `projectile_9.0_scale` | 2 | 无 | 否 | `mp_weapon_bow`、`mp_weapon_bow_crate` |
| `realtime_mod_can_ads` | 13 | 有 | 否 | `mp_weapon_3030_crate`、`mp_weapon_alternator_smg` |
| `trigger_snipercam` | 197 | 无 | 否 | `mp_ability_area_cloak`、`mp_ability_area_sonar_scan` |
| `viewdrift_ads_delay_debounce_time` | 95 | 无 | 否 | `mp_ability_gibraltar_shield`、`mp_ability_sniper_ult` |
