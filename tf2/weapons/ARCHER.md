# Archer（`mp_weapon_rocket_launcher`）：锁定导弹

TF2 独有（Apex 没有锁定火箭）。会话 `tf2-weapons`，2026-11-08。

## 先说结论

**锁定导弹**。多人里必须完全开镜**并且锁定**才能发射（腰射、不锁、锁到一半都打不出）。只锁"大型"目标：泰坦、死神能锁，步兵不能。锁定时间 = 1.05 + 0.5 × 距离 / 6500 s（实测 864 u 1.11 s、400 u 1.07 s；`fast_lock` 0.55 s），和这个公式对上到 0.01 s。导弹 1200 u/s，不会加速（文件写的上限 1400 在代码里没有用上），追着目标转向；一发 2250（对重甲），死神同样 2250。换弹约 2.6 s 可以再打。

## 1. 规则（文件和脚本）

出处缩写：`txt` = `scripts/weapons/mp_weapon_rocket_launcher.txt`（数值见 [附录](#附录文件原值)），`nut` = `scripts/vscripts/weapons/mp_weapon_rocket_launcher.nut`，`sa` = `scripts/vscripts/weapons/sh_smart_ammo.gnut`，都在 `TF2-Research/local/vpk/client_mp_common/` 下。

### 1.1 什么时候能开火

1. **必须完全开镜**：`zoomFrac < 1` 时开火函数直接返回 0，不出弹、不扣弹（nut:122–124）。腰射按扳机没有任何效果。`attack_button_presses_ads 1`：按开火键会自动开镜。
2. **多人版必须锁定**：`SmartAmmo_SetAllowUnlockedFiring( weapon, !IsMultiplayer() )`（nut:69）。多人里没锁上时 `SmartAmmo_FireWeapon` 记一次"开火失败"后返回 0（sa:96–102, 177–181）。战役里可以不锁直接打。
3. 发射以后清掉锁定目标（`SmartAmmo_SetUnlockAfterBurst( weapon, true )`，nut:98），下一发要重新锁。

### 1.2 锁定

| 项 | 值 | 出处 |
|---|---|---|
| 锁定类型 | `large`，最多 1 个目标 | txt `smart_ammo_lock_type`、`smart_ammo_max_targets` |
| 找目标 | NPC 和玩家都找（`search_npcs 1`、`search_players 1`），不找投射物 | txt |
| 搜索角 / 距离 | 9°，6500 u | txt `smart_ammo_search_angle`、`smart_ammo_search_distance` |
| 屏幕框 | x 0.31–0.68，y 0.38–0.63（屏幕比例） | txt `smart_ammo_screen_*` |
| 锁定时间 | 1.05–1.55 s（`fast_lock` 配件 0.5–0.9 s） | txt `smart_ammo_targeting_time_min/max` |
| 丢锁宽限 | 0.5 s | txt `smart_ammo_unlock_debounce_time` |
| 泰坦挡视线 | 是 | txt `smart_ammo_titans_block_los` |
| 隐身目标 | 不追踪 | txt `smart_ammo_track_cloaked_targets 0` |
| 泰坦锁定点 | 躯干前、躯干后、左右腿、躯干底、头、左右臂（8 个） | txt `smart_ammo_titan_lock_point0–7` |
| 提醒 NPC | 锁到 0.8 时通知 NPC | txt `smart_ammo_alert_npc_fraction` |

锁定时间在 1.05 和 1.55 之间怎么取、"large"具体包括哪些目标，是原生代码，脚本里没有。下面第 3 节实测。

### 1.3 导弹

- 速度：多人 1200 u/s（nut:88），转向速度 125（nut:89）。导弹寿命 10 s（sa:307）。
- **"速度上限 1400"没有生效**：nut:94 设了 `SmartAmmo_SetMissileSpeedLimit( weapon, 1400 )`，但 sa:285 只把它读进一个局部变量，之后没有用。实测速度一直是 1200 左右（第 3 节）。
- 发射时调用 `InitMissileForRandomDriftFromWeaponSettings`（sa:296），用 txt 的漂移键：直飞 0.4–1.2 s、半径 40–65，之后漂移强度 0.8、"风" 2.25。有锁定目标时同时追踪目标（`SetHomingSpeeds( 125, 125 )`，sa:315）。
- 牛仔骑乘时出弹点抬高 20 u（nut:130–131），HSD 不做牛仔，记一笔。
- 导弹靠近玩家 1536 u 以内时，给目标玩家放一次"导弹接近"警告声（nut:43–48）。
- 战役版不同：速度 1750、转向 70、上限 900（nut:72–84）；可以不锁直接打。

### 1.4 伤害

| 项 | 对人 / 小型 | 对泰坦（重甲） | 出处 |
|---|---|---|---|
| 直接命中 | 100 | 2250 | txt `damage_near/far_value(_titanarmor)`，近 1200 / 远 15000 不衰减（两端同值） |
| 爆炸 | 100 | 500 | txt `explosion_damage(_heavy_armor)` |
| 爆炸半径 | 内 96，外 180 | | txt `explosion_inner_radius`、`explosionradius` |
| 非泰坦重甲（死神等） | 重甲值 × 0.5 | | txt `damage_heavyarmor_nontitan_scale` |
| 爆头 | 不能（`allow_headshots 0`） | | txt |
| 炸到自己 | 不会（`explosion_damages_owner 0`） | | txt |

### 1.5 弹药、换弹、开镜

- 弹匣 1，备弹 7（`extended_ammo` 9）。
- 换弹 3.0 s；`reloadempty_time_late1` 3.0、`late2` 1.5（含义见 [README 的"换弹中断"](README.md)）。
- 开镜 0.35 s 进、0.35 s 出，FOV 45；开镜移动速度 × 0.5。
- 散布：腰射 3°，开镜 0.2°。
- 后坐：`viewkick_spring launcher`；俯仰 −4 ± 3，偏航 0 ± 3；永久后坐俯仰 0 ± 2、偏航 0 ± 2.5。

### 1.6 导弹的随机漂移（原生代码，Archer 和 Sidewinder 共用）

`InitMissileForRandomDriftFromWeaponSettings`（`FUN_1806720c0` → `FUN_180675690`、`FUN_1806755e0`）记下发射点、发射方向、一个随机相位 `r`（0–1），再把武器的 6 个漂移键抄进导弹，然后每帧跑 `MissileVelocityThink`（`FUN_1806761f0` → `FUN_1806758b0` → `FUN_180675ce0`）。导弹有追踪目标时不走这一段（Archer 锁定后按追踪飞）。

每帧（t = 发射后的时间，dt = 帧长，W = 风，I = 强度）：

```
a  = (t − 0.5·dt) × W
x1 = a + 1000·r                 x2 = a + 2000·r + 100
n(x) = sin(x) + sin(0.762x) + sin(0.363x) + sin(0.084x)
方向 = normalize( v/|v| + 右 × 0.25·I·dt·n(x1) + 上 × 0.25·I·dt·n(x2) )
速度 = 方向 × |v|                 // 只转方向，速率不变
```

直飞期（t < `projectile_straight_time_max`）：另外把导弹拉回发射线。允许偏离的半径在 `straight_time_min` 之前是一个端点值，之后到 `straight_time_max` 线性变到另一个端点（`projectile_straight_radius_min/max`，最小按 1 算）；超出半径时速度里加一个指回发射线的分量，乘 dt × I 后再保持速率。

**不确定的地方**：6 个键在导弹里的排列（`+0x1d00…+0x1d14`）是按函数里的用法对上的，"W 是频率、I 是幅度"是按键名推断的；半径是从大到小还是从小到大没有分清。常数是读出来的（`0.762`、`0.363`、`0.084`、`1000`、`2`、`100`、`0.25`、`0.5`）。实测对照见第 2 节。

## 2. 实测

运行：`runtime/data/20261108_033208_wp_smoke`、`runtime/data/20261108_133543_wp_d`（D）。泰坦冻结在 `(24, −1000)`（离出生点 864 u），死神在 `(−200, −1300)`。每项 1–6 次。

| 项 | 实测 | 文件 / 脚本 | 对得上？ |
|---|---|---|---|
| 腰射 | 按开火 0.3 s：不出弹，不扣弹 | `zoomFrac < 1` 返回 0 | ✓ |
| 不锁定开火（对着墙，开镜） | 不出弹 | 多人禁止不锁定开火 | ✓ |
| 锁步兵 | 开镜对准 2.6 s，**没有锁定目标** | `lock_type large` | ✓ 步兵不算"大型" |
| 锁泰坦、死神 | 都能锁 | | ✓ |
| 锁定没完成就开火 | 开镜 0.9 s 后按开火：不出弹 | 必须锁满（fraction 1） | ✓ |
| 开始锁定 | 开镜满（0.356 s）后约 0.21 s 出现目标（7 次 0.566–0.575 s，从按开镜算） | `smart_ammo_*_search_tick_interval 6` | 推断是搜索间隔 |
| **锁定时间** | 864 u：1.111 s（3 次 1.095–1.113）；400 u：1.074 s；`fast_lock` 864 u：0.552 s | 1.05–1.55；`fast_lock` 0.5–0.9 | ✓ 符合 **锁定时间 = lerp( min, max, 距离 / 6500 )**：864 u 算 1.116 / 0.553，400 u 算 1.081 |
| 偏离中心 | 偏 6°：照样锁泰坦；偏 20°：锁到了另一个方向上的死神 | 搜索角 9°、屏幕框 | 没测到"偏多少丢锁" |
| 导弹速度 | 1200.0，全程 1193.7–1199.9 | 1200；上限 1400 没生效 | ✓（上限确实没用） |
| 追踪 | 偏 6° 发射：0.6 s 内横向拐 86 u 打中目标 | 转向 125 | 有追踪；转向率没拟合 |
| 对泰坦 | 每发 2250（只记一次伤害） | 直接 2250，爆炸重甲 500 | ✓；直接命中的目标不再吃爆炸 |
| 对死神 | 每发 2250，两发打死（3500） | 2250 × `damage_heavyarmor_nontitan_scale 0.5` = 1125 | ✗ 死神不打折（其他武器同样） |
| 开镜 | 0.5 在 0.182–0.188 s，0.99 在 0.355–0.359 s | 0.35 | ✓ |
| 换弹（打完自动换） | 补满 2.01–2.04 s，能开火 2.54–2.65 s（7 次） | 3.0 | 提前 0.35–0.46 s |
| 换弹中断 | 0.80 s 切走 → 再换 2.55 s | `reloadempty_time_late1` 3.0（= T） | 分不出节点（late1 和 T 相同） |


## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| "large"包括哪些 | 原生；实测泰坦、死神能锁，步兵不能 | 幽灵、潜行者、无人机没测 |
| 丢锁的角度 | 6° 锁得住，20° 换了目标，中间没测 | 锁定手感 |
| 追踪转向率 125 的单位 | 原生 `SetHomingSpeeds`；只有一次 86 u 拐弯 | 打移动目标 |
| 漂移（1.6 节）在有目标时还生不生效 | 锁定后导弹按追踪飞；没有不锁定的多人发射可测 | 战役版才有不锁定发射 |
| 锁定 HUD、提示音时序 | 没截屏 | |
| 导弹接近警告（1536 u） | 只对玩家目标；没有第二个玩家 | |


## 4. 能不能脱离 TF2 照做

**能照做的**：开火条件、锁定目标类型（泰坦、死神）、锁定时间公式、导弹速度、伤害、换弹时刻。实测对照：本页第 2 节，`runtime/data/20261108_133543_wp_d`。

**还缺的**：追踪转向率 125 的单位和转向曲线（只有一次拐弯）；丢锁角度；"large"是否包括幽灵、潜行者、无人机；锁定 HUD。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

### mp_weapon_rocket_launcher 文件原值（`mp_weapon_rocket_launcher.txt`，`wpn-values.tsv`）

**开火和弹药**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_empty_click` | 1 |  |  |
| `allow_empty_fire` | 0 |  |  |
| `ammo_clip_size` | 1 |  | extended_ammo=1 |
| `ammo_default_total` | 7 | 3 | extended_ammo=9 |
| `ammo_min_to_fire` | 1 |  |  |
| `ammo_no_remove_from_stockpile` | 0 |  | at_unlimited_ammo=1 |
| `ammo_stockpile_max` | 7 | 12 | extended_ammo=9 |
| `ammo_suck_behavior` | primary_weapons |  |  |
| `attack_button_presses_ads` | 1 |  |  |
| `empty_reload_only` | 0 |  |  |
| `fire_rate` | 1 |  |  |
| `primary_fire_does_not_block_sprint` | — |  | pas_run_and_gun=1 |
| `reload_enabled` | 1 |  |  |

**伤害**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `allow_headshots` | 0 |  |  |
| `critical_hit` | 0 |  |  |
| `damage_far_distance` | 15000 |  |  |
| `damage_far_value` | 100 | 250 | burn_mod_rocket_launcher=200; fd_mortar_mode=*0.0 |
| `damage_far_value_titanarmor` | 2250 | 1250 | burn_mod_rocket_launcher=3250; fd_mortar_mode=*0.15 |
| `damage_heavyarmor_nontitan_scale` | 0.5 | 1 |  |
| `damage_near_distance` | 1200 |  |  |
| `damage_near_value` | 100 | 250 | burn_mod_rocket_launcher=200; fd_mortar_mode=*0.0 |
| `damage_near_value_titanarmor` | 2250 | 1250 | burn_mod_rocket_launcher=3250; fd_mortar_mode=*0.15 |
| `damage_type` | burn |  |  |
| `explosion_damage` | 100 | 150 | burn_mod_rocket_launcher=150; fd_mortar_mode=*0.0 |
| `explosion_damage_heavy_armor` | 500 |  | burn_mod_rocket_launcher=700; fd_mortar_mode=*0.15 |
| `explosion_damages_owner` | 0 | 1 |  |
| `explosion_inner_radius` | 96 |  | fd_mortar_mode=*0 |
| `explosionradius` | 180 |  | fd_mortar_mode=*0 |
| `impulse_force` | 10000 |  |  |

**弹体**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `projectile_adjust_to_gun_barrel` | 1 |  |  |
| `projectile_drift_intensity` | 0.8 |  |  |
| `projectile_drift_windiness` | 2.25 |  |  |
| `projectile_straight_radius_max` | 65 |  |  |
| `projectile_straight_radius_min` | 40 |  |  |
| `projectile_straight_time_max` | 1.2 | 1.8 |  |
| `projectile_straight_time_min` | 0.4 | 1.5 |  |
| `scripted_projectile_max_timestep` | 0.2 |  |  |
| `scripted_projectile_velocity` | 1 |  |  |

**换弹和切枪**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `deploy_time` | 0.8 |  |  |
| `fast_swap_to` | 0 |  | pas_fast_swap=1 |
| `holster_time` | 0.5 |  |  |
| `lower_time` | 0.25 |  |  |
| `raise_time` | 0.3 |  |  |
| `reload_time` | 3.0 |  | pas_fast_reload=*0.7 |
| `reload_time_late1` | — |  | pas_fast_reload=*0.7 |
| `reloadempty_time` | 3.0 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late1` | 3.0 |  | pas_fast_reload=*0.7 |
| `reloadempty_time_late2` | 1.5 |  |  |

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
| `spread_stand_ads` | 0.2 |  | fd_mortar_mode=0 |
| `spread_stand_hip` | 3 |  | fd_mortar_mode=0 |

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
| `viewkick_pitch_base` | -4 |  |  |
| `viewkick_pitch_hardScale` | 5.0 |  |  |
| `viewkick_pitch_random` | 3.0 |  |  |
| `viewkick_pitch_softScale` | 1.3 |  |  |
| `viewkick_roll_base` | 0.0 |  |  |
| `viewkick_roll_hardScale` | 6.0 |  |  |
| `viewkick_roll_randomMax` | 0.7 |  |  |
| `viewkick_roll_randomMin` | 0.5 |  |  |
| `viewkick_roll_softScale` | 0.2 |  |  |
| `viewkick_spring` | launcher |  |  |
| `viewkick_yaw_base` | 0.0 |  |  |
| `viewkick_yaw_hardScale` | 1.0 |  |  |
| `viewkick_yaw_random` | 3.0 |  |  |
| `viewkick_yaw_softScale` | 1.3 |  |  |
| `viewpunch_multiplier` | 2.9 |  |  |

**智能锁定**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `smart_ammo_alert_npc_fraction` | 0.8 |  |  |
| `smart_ammo_allow_ads_lock` | 1 |  |  |
| `smart_ammo_bounds_search_tick_interval` | 6 |  |  |
| `smart_ammo_hud_lock_style` | pilot_launcher |  |  |
| `smart_ammo_lock_type` | large |  |  |
| `smart_ammo_max_targets` | 1 |  |  |
| `smart_ammo_npc_use` | 0 |  |  |
| `smart_ammo_points_search_tick_interval` | 6 |  |  |
| `smart_ammo_screen_max_x` | 0.68 |  |  |
| `smart_ammo_screen_max_y` | 0.63 |  |  |
| `smart_ammo_screen_min_x` | 0.31 |  |  |
| `smart_ammo_screen_min_y` | 0.38 |  |  |
| `smart_ammo_search_angle` | 9 |  |  |
| `smart_ammo_search_distance` | 6500 |  |  |
| `smart_ammo_search_npcs` | 1 |  |  |
| `smart_ammo_search_players` | 1 |  |  |
| `smart_ammo_search_projectiles` | 0 |  |  |
| `smart_ammo_targeting_time_max` | 1.55 |  | fast_lock=0.9 |
| `smart_ammo_targeting_time_min` | 1.05 |  | fast_lock=0.5 |
| `smart_ammo_titan_lock_point0` | SMART_AMMO_TORSO_FRONT |  |  |
| `smart_ammo_titan_lock_point1` | SMART_AMMO_TORSO_BACK |  |  |
| `smart_ammo_titan_lock_point2` | SMART_AMMO_LEG_LEFT |  |  |
| `smart_ammo_titan_lock_point3` | SMART_AMMO_LEG_RIGHT |  |  |
| `smart_ammo_titan_lock_point4` | SMART_AMMO_TORSO_BASE |  |  |
| `smart_ammo_titan_lock_point5` | SMART_AMMO_HEAD |  |  |
| `smart_ammo_titan_lock_point6` | SMART_AMMO_ARM_LEFT |  |  |
| `smart_ammo_titan_lock_point7` | SMART_AMMO_ARM_RIGHT |  |  |
| `smart_ammo_titans_block_los` | 1 |  |  |
| `smart_ammo_track_cloaked_targets` | 0 |  |  |
| `smart_ammo_unlock_debounce_time` | 0.5 |  |  |
| `smart_ammo_weapon_type` | homing_missile |  |  |

**NPC 使用**

| 键 | 多人 | 战役（不同时） | 改它的 mod |
|---|---|---|---|
| `npc_accuracy_multiplier_pilot` | 0.2 |  |  |
| `npc_damage_far_value` | 80 |  |  |
| `npc_damage_far_value_titanarmor` | 800 |  |  |
| `npc_damage_near_value` | 80 |  |  |
| `npc_damage_near_value_titanarmor` | 800 |  |  |
| `npc_explosion_damage` | 100 | 80 |  |
| `npc_explosion_damage_heavy_armor` | 400 |  |  |
| `npc_max_burst` | 1 |  |  |
| `npc_max_engage_range` | 2000 |  |  |
| `npc_max_engage_range_heavy_armor` | 2500 |  |  |
| `npc_max_range` | 8000 |  |  |
| `npc_min_burst` | 1 |  |  |
| `npc_min_engage_range` | 100 |  |  |
| `npc_min_engage_range_heavy_armor` | 500 |  |  |
| `npc_min_range` | 0 |  |  |
| `npc_rest_time_between_bursts_max` | 4 |  | fd_mortar_mode=*2.0 |
| `npc_rest_time_between_bursts_min` | 3.5 |  | fd_mortar_mode=*1.25 |
| `npc_use_ads_move_speed_scale` | 0 |  |  |
| `npc_vortex_block` | 0 |  |  |
| `proficiency_average_spreadscale` | 2.5 |  |  |
| `proficiency_good_spreadscale` | 2.0 |  |  |
| `proficiency_poor_spreadscale` | 3.0 |  |  |
| `proficiency_very_good_spreadscale` | 1.6 |  |  |


