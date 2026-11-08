# R-6P Softball（`mp_weapon_softball`）：粘性榴弹

TF2 独有。会话 `tf2-weapons`，2026-11-08。

## 先说结论

**粘性榴弹**：2500 u/s 发射、按普通重力下落、继承玩家速度，碰到世界、玩家或 NPC 就粘住，**0.5 s 后爆**。爆炸 90 / 重甲 330（半径 50 满伤，150 为 0），直接命中只有 10（对重甲 0）。半自动 2 发 / s，6 发；换弹**一发一发装**：第一发约 0.8 s，之后每 0.82 s 一发，中途打断不丢已经装进去的。开镜反而更散（0.35° 对腰射 0.25°）。实测全部对上文件。

## 1. 规则（文件和脚本）

出处缩写（都在 `TF2-Research/local/vpk/client_mp_common/scripts/` 下）：`txt` = `weapons/mp_weapon_softball.txt`（数值见附录），`nut` = `vscripts/weapons/mp_weapon_softball.nut`，`util` = `vscripts/weapons/_weapon_utility.nut`。

### 1.1 开火

1. 半自动，2 发 / s，弹匣 6，备弹 60（多人不扣备弹）。
2. 每发一颗榴弹（`FireWeaponGrenade`，nut:44）：出膛 2500 u/s（`projectile_launch_speed`），**继承玩家速度 × 1**（`projectile_inherit_owner_velocity_scale 1`）。自转随机（−1200…1200, 100, 0），只是外观（nut:40）。
3. nut:22–25 算了一个枪口偏移（腰射 30 / 6 / −4，开镜 30 / 0 / −3），**但没有用上**：`FireGrenade` 用的还是 `attackParams.pos`（死代码）。
4. 没粘住时按 txt 的弹跳键反弹：浅角保留 0.47、陡角 0.28、法向 0.5，滚动每秒 0.1，随机 0.2。txt 没有 `grenade_fuse_time`。

### 1.2 粘住和引爆（nut:58–85，util:869–922）

1. 撞到东西时 `PlantSuperStickyGrenade`：
   - 撞到**同队**的东西：不粘（util:871–872），继续弹。
   - 先把榴弹放到撞击点、朝向法线。
   - 撞到的不是世界、玩家或 NPC（比如道具、别的投射物）：不粘（util:889–890），继续弹。
   - 世界：停住物理（util:894–897）。玩家 / NPC：挂到命中的骨骼上（`SetParentWithHitbox`），跟着目标走；目标是玩家时，玩家相位移动就脱落（util:903–910, 926–939）。
2. 粘住以后 **0.5 s 爆**（`FUSE_TIME`，nut:10, 74, 79–85）。
3. 粘到玩家身上时，对那个玩家放 1P 提示声，其他人听 3P 声（nut:65–72）。

### 1.3 伤害

| 项 | 对人 | 对重甲 | 出处 |
|---|---|---|---|
| 直接命中 | 10（近 100 / 远 1500 同值） | 0 | txt `damage_*` |
| 爆炸 | 90 | 330 | `explosion_damage(_heavy_armor)` |
| 爆炸半径 | 内 50，外 150 | | |
| 非泰坦重甲 | 重甲值 × 0.5 | | |
| 爆头 | 不能 | | `allow_headshots 0` |
| 打击力 | 7000 | | `impulse_force` |

### 1.4 换弹：逐发装填

- `reload_is_segmented 1`、`ammo_size_segmented_reload 1`：一次装 1 发。
- 每发循环 0.82 s（`reloadsegment_time_loop`），结束动作 0.57 s（`reloadsegment_time_end`、`reloadsegmentempty_time_end`）；`reload_time` / `reloadempty_time` 0.95。
- 开镜 0.2 / 0.15 s，FOV 45。散布：腰射 0.25°，**开镜 0.35°（比腰射大）**。
- 后坐：`launcher` 弹簧，俯仰 −0.3 ± 0.1，偏航 0 ± 0.15；永久后坐俯仰 0 ± 0.3、偏航 0 ± 0.2。

## 2. 实测

运行：`runtime/data/20261108_132546_wp_b`（B）。每项 1–5 次。

| 项 | 实测 | 文件 / 脚本 | 对得上？ |
|---|---|---|---|
| 射速 | 两发间隔 0.500 / 0.507 s（腰射），0.500 / 0.504 s（开镜） | `fire_rate 2` | ✓ |
| 出膛 | 2500.0 u/s，方向就是视线（开镜、腰射都在眼睛处出弹） | 2500 | ✓ |
| 重力 | **750 u/s²**（每 0.1 s 竖直速度少 75） | 榴弹，缺省 1.0 × 750 | ✓ |
| 阻力 | 水平速度不变 | | 没有 |
| 继承玩家速度 | 向前约 248 u/s 时开火，出膛 2747.9（= 2500 + 248） | `projectile_inherit_owner_velocity_scale 1` | ✓（横移那次玩家速度没生效，没测成） |
| 粘住 → 爆炸 | 每次都是粘住（`planted 1`）后 **0.50 s** 爆（5 次：墙、天花板、泰坦、步兵） | `FUSE_TIME 0.5` | ✓ |
| 粘在泰坦上 | 粘住后爆炸，泰坦 −330 | 爆炸重甲 330 | ✓（直接命中重甲是 0） |
| 爆炸伤害随距离 | 落在步兵脚下 68 u：90；地面 175 / 196 / 218 u（到推测的身体位置）：45 / 27 / 8 | 内 50 满伤，外 150 为 0 | 线性下降、斜率约 0.86 / u（文件 0.9）；距离的零点受靶子位置不准影响 |
| 散布 | 腰射各姿态 0.25，开镜 0.35；开火那一帧读到 0.35 | 腰射 0.25、开镜 0.35 | ✓（开镜反而更散） |
| 开镜 | 0.5 在 0.111–0.112 s，0.99 在 0.209–0.211 s；关镜 0.5 在 0.084 s，0.01 在 0.158–0.160 s | 0.2 / 0.15 | ✓ |
| 逐发装填 | 从空：第 1 发 +0.79 s，之后每 **0.82 s** 一发（0.816 / 0.826 / 0.824 / 0.824），6 发装满 +4.90 s 可开火 | `reloadsegment_time_loop 0.82` | ✓ |
| 逐发装填（从 3 发） | 第 1 发 +0.84 s，装满 +2.48 s 可开火 | | 同上 |
| 装填中能开火 | 每装进 1 发后有约 0.12 s 可以开火（`IsReadyToFire` 闪成 1） | 逐发装填 | 推断：这时按开火会打断装填 |
| 中途切走 | 已装进去的保留（切走时 1 发 → 回来接着从 1 发装；2 发 → 从 2 发装） | | ✓ |
| 切枪 | 切走 0.80 s、切回 0.94 s 可开火 | 收 0.5、掏 0.63 | 大体相加 |

**长距离飞行**（`runtime/data/20261108_133923_wp_e`）：朝上 85° 和 45° 发射的 5 发，在空中飞了 4.4–6.3 s 都**没有爆**，落地粘住后 0.5 s 才爆（朝上那发 6.6 s 落回附近，7.1 s 爆）。所以没粘住时没有引信（至少 6 s 内不会自己爆）。



## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| 一直不粘会不会最终消失 | `wp_e` 里 6.3 s 不爆；再长没测 | 打到天上的弹 |
| 收尾 0.57 s（`reloadsegment_time_end`） | 装满后很快就能开火，没看到 0.57 s 的停顿 | 收尾动作 |
| 横向继承速度 | 测的那次玩家速度没生效 | 推断和向前一样 × 1 |
| 粘在玩家身上 | 没有第二个玩家 | 规则读文件（1.2 节） |
| 打人直接命中 10 | 冻结步兵的受击位置不可靠 | 用文件值 |


## 4. 能不能脱离 TF2 照做

**能照做的**：发射、重力、继承速度、粘住规则（谁能粘、粘在骨骼上、0.5 s 引信）、爆炸伤害、逐发装填的时序和打断规则、散布、开镜。

**还缺的**：没粘住时会不会自己爆（文件没写引信，这次每发都粘住了）；横向继承速度没测成；粘到玩家身上的情况。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

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


