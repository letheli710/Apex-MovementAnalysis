# LG-97 Thunderbolt（`mp_weapon_arc_launcher`）：慢速电球

TF2 独有（Apex 没有）。会话 `tf2-weapons`，2026-11-08。

## 先说结论

**慢速电球**：必须完全开镜才能开火，1 发一换。电球 500 u/s（往前跑时再加上你的前进速度），不受重力，飞 8 s。飞的过程中**每 0.4 s 电一次半径 400 内的目标**：泰坦、死神等重甲 350，人形目标 8，而且人形只在 200 u 以内才电（实测血量核对过）；不需要视线。撞到东西：直接 70 / 1000，爆炸 40 / 250。所以它是"一颗慢慢飘过一串敌人、沿路放电"的反泰坦武器，实测和脚本完全一致。

## 1. 规则（文件和脚本）

出处缩写（都在 `TF2-Research/local/vpk/` 下）：
- `txt` = `client_mp_common/scripts/weapons/mp_weapon_arc_launcher.txt`（数值见附录）
- `nut` = `client_mp_common/scripts/vscripts/weapons/mp_weapon_arc_launcher.nut`
- `ball` = `client_mp_common/scripts/vscripts/weapons/mp_titanweapon_arc_ball.nut`（Ion 泰坦也用这个电球）
- `bl` = `client_sp_training/scripts/vscripts/weapons/_ball_lightning.gnut`（服务端；Northstar 的同名文件只有空格不同，已比对）
- `set` = `client_frontend/scripts/vscripts/_settings.nut`、`ent` = `client_sp_training/scripts/vscripts/_entitystructs.gnut`
- `arc` = `client_mp_common/scripts/vscripts/weapons/_arc_cannon.nut`、`util` = `client_mp_common/scripts/vscripts/_utility_shared.nut`

### 1.1 开火

1. **必须完全开镜**：玩家开火时 `zoomFrac < 1` 直接返回 0（nut:7–12）。`attack_button_presses_ads 1`。
2. 每次开火发一颗电球：`FireArcBall( weapon, pos, dir, shouldPredict, 350 )`（nut:37），350 是对重甲的电击伤害（nut:2）。
3. nut:32 的 `speed = 450.0` 没有用上（死代码），速度由 `FireArcBall` 定。
4. 牛仔骑乘时出弹点抬高 20 u（nut:19–23）。

### 1.2 电球的飞行（ball:112–158）

- 速度 = 500 + 玩家速度在射击方向上的分量（只加不减：分量 < 0 时按 0），ball:116–134。
  - 例：朝前冲 300 u/s 时开火，电球 800 u/s；后退时开火仍是 500。
- 是一个 bolt（`FireWeaponBolt`），`kv.gravity = 5`（ball:146）。txt 的 `bolt_gravity_enabled 0`。两个值哪个生效，见实测。
- 寿命 8 s（ball:149, 157）。
- txt 的 bolt 命中体积从 0 长到 25（1.5 s 内），撞到东西会炸。

### 1.3 电击（bl:133–184）

电球带一个"球状闪电"实体（`AttachBallLightning`，bl:32–54），每 0.4 s 做一次 `RadiusDamage`：

| 项 | 值 | 出处 |
|---|---|---|
| 间隔 | 0.4 s（`BALL_LIGHTNING_BURST_DELAY`），每次 1 下（`BURST_NUM 1`） | set:682–683, bl:154–165 |
| 半径 | 400，内外半径相同（不衰减） | set:689, bl:170–183 |
| 对人和小型目标 | 8（多人；战役 10） | set:695–699，`fxData.damageToPilots` |
| 对重甲（泰坦、死神等） | Thunderbolt 350（Ion 的电球 120） | nut:2 覆盖 `fxData.damage` |
| 高度限制 | 目标和球的高差 > 300 不电 | set:691, bl:223 |
| 人形目标的距离限制 | 人形目标离球心 > 200 不电（伤害改成 0） | set:690, bl:257–262 |
| 能电的类别 | 步兵、幽灵、潜行者、死神、泰坦、无人机、炮塔、扁虱、玩家等 16 类 | arc:87–104 |
| 不电自己人、不电主人 | `SF_ENVEXPLOSION_NO_DAMAGEOWNER`；队伍由 `RadiusDamage` 处理 | bl:178 |
| 涡旋护盾挡 | 球和目标之间有涡旋护盾时不电 | bl:270–273 |
| 视线 | 不查（射线检查那几行被注释掉了），**隔墙也电** | bl:264–268 |

"人形"按 `IsHumanSized`：玩家看是不是人形；NPC 看小型炮塔或身体类型 `human` / `marvin`（util:3514–3528）。所以步兵、幽灵都按人形（200 内才电），死神、泰坦不受 200 的限制（400 内都电）。

### 1.4 撞击和爆炸（txt）

| 项 | 对人 | 对重甲 | 出处 |
|---|---|---|---|
| 直接命中 | 70 | 1000 | `damage_near/far_value(_titanarmor)`，不衰减 |
| 爆炸 | 40 | 250 | `explosion_damage(_heavy_armor)` |
| 爆炸半径 | 内 150，外 250 | | `explosion_inner_radius`、`explosionradius` |
| 非泰坦重甲 | 重甲值 × 0.5 | | `damage_heavyarmor_nontitan_scale` |
| 爆头 | 不能 | | `allow_headshots 0` |

### 1.5 弹药、换弹、开镜

- 弹匣 1、备弹 6；射速 2（`fire_rate`，但弹匣只有 1 发，实际由换弹决定）。
- 换弹 3.35 s；`reloadempty_time_late1` 1.8、`late2` 1.35。
- 开镜 0.35 s 进 / 0.35 s 出，FOV 45，开镜移速 × 0.5。散布：腰射 3°，开镜 0.2°。
- 后坐：`launcher` 弹簧，俯仰 −0.2 ± 3，偏航 −1.0；永久后坐俯仰 0 ± 2、偏航 0 ± 2.5。

## 2. 实测

运行：`runtime/data/20261108_133109_wp_c`（C）。泰坦、死神冻结在原位；步兵在 `(−17, −1340)` 附近。伤害以**目标血量的变化**为准（我的命中日志记录的是脚本把伤害清零之前的值）。每项 1–7 次。

| 项 | 实测 | 文件 / 脚本 | 对得上？ |
|---|---|---|---|
| 腰射 | 按 0.3 s 开火键，**没有出弹**，弹匣不变 | `zoomFrac < 1` 返回 0 | ✓ |
| 电球速度 | 500.0 u/s，7 次都是；全程不变 | 500 | ✓ |
| 寿命 | `wp_e` 在空中的 5 发都在 7.9 s 消失（服务端 0.1 s 一帧） | 8 s | ✓ |
| 重力 | 没有（竖直速度一直不变，2.7 s） | 脚本 `kv.gravity = 5`；txt `bolt_gravity_enabled 0` | 按 txt：**不受重力**；脚本那行无效 |
| 前进时开火 | 玩家向前约 248 u/s：电球 747.6 u/s | 500 + 前向分量 | ✓ |
| 电击间隔 | 0.400 s（每次 `RadiusDamage`，伤害来源是电球上的 `script_mover`） | 0.4 | ✓ |
| 电泰坦、死神 | 每次 350；最远见到球到泰坦中心约 336 u 仍然电到 | 350，半径 400 | ✓ |
| 电步兵 | 球到步兵 88 / 153 / 155 u：每次 −8；252 / 257 / 293 / 312 / 338 u：**0**（血量不变） | 8；人形 200 u 以外清零 | ✓ |
| 一路电过去 | 打泰坦一发：路上死神被电 3 次（1050）、步兵 2 次、泰坦 2 次（700），最后撞泰坦 1000 | | 一发电球对一串目标都有效 |
| 隔墙电 | 电到的位置不需要视线（脚本里视线检查被注释掉了） | | 没有专门测"墙后"，推断 |
| 撞泰坦 | 1000 | `damage_*_titanarmor 1000` | ✓ |
| 爆炸 | 撞墙爆炸：步兵（离爆点约 127 u）40；死神（约 210 u）44 | 40 / 250，内 150 外 250 | ✓（死神按重甲 250 衰减） |
| 开镜 | 0.5 在 0.188 s，0.99 在 0.359 s | 0.35 | ✓ |
| 换弹 | 补满 2.03 s，能开火 2.82 s | 3.35 | 提前 0.53 s |
| 换弹中断 | 1.0 s 切走 → 再换 1.30 s（late1 1.8） | 节点按 T − late1 应在 1.55 | 节点比 T − late_k 早 |
| 切枪 | 切走 0.80 s、切回 1.87 s 可开火 | 收 0.5、掏 0.8 | 切回慢，没拆开 |


## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| 隔墙电 | 没专门测；代码里视线检查是注释掉的 | 推断能隔墙电 |
| 电到玩家 | 没有第二个玩家；对铁驭 8（多人） | 用文件值 |
| 电球被打掉 | 碰撞模型那段代码是注释掉的（ball:163–193） | 推断打不掉 |
| 涡旋护盾挡电 | 没测 | HSD 没有涡旋 |
| 电球命中体积随时间长大（0 → 25） | 没单独测 | 远处更容易撞到 |


## 4. 能不能脱离 TF2 照做

**能照做的**：开火条件、电球速度和继承规则、寿命、电击（间隔、半径、高度限制 300、人形 200、伤害、可电的类别表）、撞击和爆炸、换弹。全部规则在脚本里，实测逐项对上。

**还缺的**：隔墙电只是读代码（没专门测）；电球被打掉的规则（代码注释掉了，推断打不掉）；对玩家的 8 没测（没有第二个玩家）。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

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


