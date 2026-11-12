# Sidewinder SMR（`mp_weapon_smr`）：全自动小火箭

TF2 独有。会话 `tf2-weapons`，2026-11-08。

## 先说结论

**全自动小火箭**，8.8 发 / s（文件 9），20 发。导弹 3300 u/s、没有重力、不继承玩家速度；先直飞 1.5–2 s，之后按"四个正弦之和"随机转向（原生代码读出来了，1.4 节）；实测前 1.8 s 偏离发射线 ≤ 2 u，之后 0.9 s 内偏到 145–434 u，约 2.9 s（约 9600 u）自己消失。直接命中 50 / 重甲 115，爆炸只有 15（半径 16），所以基本靠直接打中。出弹散布比准星小 1°，腰射 0.5° 起每发 +0.5° 到 3.5°。换弹 3.0 s；它的"换弹中断"节点和 Double Take / Cold War 不同。

## 1. 规则（文件和脚本）

出处缩写：`txt` = `client_mp_common/scripts/weapons/mp_weapon_smr.txt`（数值见附录），`nut` = `client_mp_common/scripts/vscripts/weapons/mp_weapon_smr.nut`，都在 `TF2-Research/local/vpk/` 下。

### 1.1 开火

1. 全自动（txt 没写 `fire_mode`，按缺省；实测见第 2 节），射速 9 发 / s，弹匣 20，备弹 200（多人不扣备弹）。
2. 每发一枚导弹（`FireWeaponMissile`，速度倍率 1.0 → `projectile_launch_speed 3300`），nut:29。
3. **散布比准星小 1°**：开火方向 = `ApplyVectorSpread( dir, GetAttackSpreadAngle() − 1.0 )`（nut:24）。文件里所有姿态的腰射散布都是 0.5°，开镜 0°，减 1 以后都 ≤ 0。负值怎么处理是原生代码；实测见第 2 节。
4. 发射后调用 `InitMissileForRandomDriftFromWeaponSettings`（nut:36）：先在半径 2–4 u 内直飞 1.5–2 s（`projectile_straight_radius_min/max`、`projectile_straight_time_min/max`），之后按漂移强度 0.5、"风" 10 随机偏（`projectile_drift_intensity`、`projectile_drift_windiness`）。漂移的具体公式是原生代码。
5. NPC 用的版本不漂移（nut:51 注释掉了）。

### 1.2 伤害

| 项 | 对人 | 对重甲 | 出处 |
|---|---|---|---|
| 直接命中 | 50（近 1800 / 远 15000 同值） | 115 | txt `damage_*` |
| 爆头 | × 1.25；`critical_hit 1`，暴击 × 1.5 | | txt |
| 爆炸 | 15 | 150 | `explosion_damage(_heavy_armor)` |
| 爆炸半径 | 内 1，外 **16**（几乎只有直接命中） | | `explosion_inner_radius`、`explosionradius` |
| 非泰坦重甲 | 重甲值 × 0.5 | | `damage_heavyarmor_nontitan_scale` |
| 打击力 | 1000 | | `impulse_force` |

### 1.3 弹药、换弹、开镜、后坐

- 换弹 3.0 s（战术和空仓相同）；`late1` 1.98、`late2` 1.36、`late3` 0.80（战术和空仓都有）。
- 掏枪 0.8，收枪 0.5。
- 开镜 0.2 / 0.15 s，FOV 45。
- 后坐：弹簧 `low_springconstant_launcher`；俯仰 −0.25 ± 0.35，偏航 0.1 ± 0.65（内排除 0.2）。

### 1.4 导弹的随机漂移（原生代码，Archer 和 Sidewinder 共用）

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

运行：`runtime/data/20261108_132546_wp_b`（B）；长距离漂移在 `wp_e`（`mp_angel_city`，见下）。每项 1–18 次。

| 项 | 实测 | 文件 / 脚本 | 对得上？ |
|---|---|---|---|
| 开火方式 | 按住连发（2 s 出 18 发） | 没写 `fire_mode` | 缺省是全自动 |
| 射速 | 间隔 0.111–0.118 s，平均 0.1137 s（8.8 发 / s，2 次各 17 个间隔） | `fire_rate 9`（0.111） | 慢约 2 %（R5 枪械测量也是 ±3 %） |
| 弹速 | 3300.0，全程不变 | `projectile_launch_speed 3300` | ✓ |
| 重力 | 没有（竖直速度不变） | 导弹 | ✓ |
| 直飞期偏离 | 1600 u 内偏离发射线 ≤ 6.5 u（其中约 5.5 u 是开火方向本身的 0.2°） | 半径 2–4，直飞 1.5–2 s | ✓（这张图只够飞 0.5 s，漂移段见 `wp_e`） |
| 继承玩家速度 | 横移 300 u/s 时开火，弹速仍是 3300.0，方向只差 0.45°（腰射散布内） | 没有 `projectile_inherit_owner_velocity_scale` | 不继承 |
| 腰射散布 | 站 0.5°，每发 +0.5°，到 3.5° 封顶；蹲、走、冲刺、空中都是 0.5 | 0.5（各姿态） | ✓；实际出弹按 散布 − 1°（nut:24），即腰射 0–2.5° |
| 开镜散布 | 0，连射不增长 | 0 | ✓ |
| 永久后坐 | 0（18 发视角不动） | 没有 `viewkick_perm_*` | ✓ |
| 开镜 | 0.5 在 0.111 s，0.99 在 0.208 s；关镜 0.5 在 0.083 s，0.01 在 0.159 s | 0.2 / 0.15 | ✓ |
| 对泰坦 / 死神 | 每发 115 / 115（只记一次伤害） | 直接 115；死神按键名应 × 0.5 | 死神同样不打折 |
| 打步兵（`wp_f`） | 胸 50（hit group 4），只记一次 | 直接 50，爆炸 15 | 直接命中的目标不再吃爆炸 |
| 爆头（`wp_g`） | z 54 / 57 / 60：**62.5**（hit group 1）；z 50：胸 50 | 50 × 1.25 | ✓ |
| 空仓换弹 | 补满 2.36 s，能开火 2.70 s | 3.0 | 提前 0.30 s |
| 战术换弹 | 补满 2.38 s，能开火 2.72 s | 3.0 | 同上（SMR 战术和空仓文件值相同） |
| 换弹中断 | 0.69 / 1.55 / 2.14 s 切走 → 再换都是 **1.54 s**（补满 1.20） | `late1` 1.98、`late2` 1.36、`late3` 0.80 | 都落在 late1（1.98 − 0.44）；**和 Double Take、Cold War 的"节点 = T − late_k"不一样**，SMR 的第一个节点早于 0.69 s，第二个晚于 2.14 s |

**长距离飞行**（`runtime/data/20261108_133923_wp_e`，`mp_angel_city` 出生点，四周 12000 u 内没有遮挡；5 发：1 发朝上 85°，4 发 45° 朝四个方向；逐帧偏离见该目录的 `sky.txt`，由 [tools/analyze_sky.py](tools/analyze_sky.py) 生成）：

| t（s） | 0.3 | 0.9 | 1.5 | 1.8 | 2.1 | 2.4 | 2.7 | 3.0 |
|---|---|---|---|---|---|---|---|---|
| 偏离发射线（横 / 竖，u），第 4 发 | −2 / 0 | 0.4 / 0.2 | 1.0 / 2.0 | 1.6 / −0.7 | −39 / −18 | −157 / −31 | −315 / −107 | −434 / −162 |
| 偏离（横 / 竖，u），第 2 发 | −3 / 11 | −5 / 25 | −9 / 41 | −9 / 46 | −38 / 41 | −85 / 90 | −103 / 196 | −145 / 265 |

- 前 1.8 s 贴着发射线（第 4 发 ≤ 2 u，符合半径 2–4 u 的直飞走廊；第 2 发的"竖"线性增长是参考方向偏了约 0.3°，不是漂移）。
- 1.8–2.1 s 之间开始漂（`straight_time` 1.5–2 s 随机），之后偏离越来越快，0.9 s 内到 145–434 u。速率一直 3300（只转方向）。
- **导弹在约 2.85–3.0 s 自己消失**（5 发都是，飞了 9400–9800 u）；文件里没有寿命键，推断是导弹的缺省寿命。



## 3. 不知道的

| 项 | 为什么不知道 | 影响 |
|---|---|---|
| 漂移公式里 6 个键的对应 | 反编译只看到槽位，按用法和键名对上（1.4 节） | 用 `wp_e` 的长距离弹道核对 |
| 换弹节点 | 3 个切点都是 late1；更早 / 更晚的切点没测 | 换弹打断后的时长 |
| 散布 − 1° 后的负值 | 原生 `ApplyVectorSpread` 没读；推断负值按 0 | 腰射前 2 发是不是完全没散布 |
| 爆炸半径 16 的实际作用 | 太小，没单独测 | 几乎只有直接命中 |


## 4. 能不能脱离 TF2 照做

**能照做的**：射速、弹道（速度、无重力、不继承）、直飞走廊和漂移公式（常数已读出，键的对应按用法推断）、散布规则、伤害、换弹时刻。长距离漂移的实测对照：`runtime/data/20261108_133923_wp_e`（本页第 2 节下方）。

**还缺的**：漂移 6 个键的槽位对应只是推断（要么拿 `wp_e` 的弹道拟合，要么继续读反编译）；换弹节点只有 3 个切点；打人的伤害和爆头倍率见 `wp_f`。

**11-12 原生（`ref-native-tail`，N3 / N4）：**
- 6 个漂移键的槽位已确定：+0x1d00 `windiness`、+0x1d04 `intensity`、+0x1d08 / +0x1d0c `straight_time_min` / `max`、+0x1d10 / +0x1d14 `straight_radius_min` / `max`（小于 1 按 1）。依据是原生 `InitMissileForRandomDrift` 按参数顺序写这 6 格，被注释掉的旧脚本版给出了每个参数的名字。直飞半径从 `radius_min` 开始，到 `straight_time_max` 时涨到 `radius_max`。
- 散布 −1° 之后的负值：`ApplyVectorSpread` 是脚本，负值只是让偏移翻个方向。所以腰射的实际散布是 |0.5 − 1| = 0.5°，开镜是 1°，**不是**按 0 算。
详见 [REF-NATIVE-1112.md §3、§4](../ref-native-tail/REF-NATIVE-1112.md)。

## 附录：文件原值

由 [tools/wpn_static_md.py](tools/wpn_static_md.py) 从 [data/wpn-values.tsv](data/wpn-values.tsv) 生成；略去了声音、特效、模型、晃动、UI 这类外观键（全表在 tsv 里）。

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


