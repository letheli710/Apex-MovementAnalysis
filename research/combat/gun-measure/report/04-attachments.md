# 04 配件

[回到目录](README.md)

## 结论

1. **绝大多数配件都生效，而且按文件走。** 31 把枪、840 个"枪 + 配件"组合里，825 个装上了。
2. **配件几乎都是改字段，大多乘比例。** 下面的表就是这些比例。
3. **枪托影响最广：** 换弹、收枪、掏枪、抬枪、放下、开镜、开镜漂移全改。
4. **Hop-up 的 `hopup_*` 多数只是空标记**，真正改行为的是切换 mod（`altfire_*`、`choke`、`shatter_rounds_hipfire`、`energized`）。
5. **金色配件本地没有字段变化。** 补给箱版是另一把枪（`*_crate`），不是配件。

下面的比例表来自 [A-MOD-DIFFS.tsv](../A-MOD-DIFFS.tsv)，是运行时读回的字段变化 **[字段]**。那个文件有每个组合的全部字段（1175 个），这里只列影响手感的。一把枪时写从多少到多少，多把枪时写比例范围。写了 **[实测]** 的另外跑过行为。

## 1. 枪管（改后坐）

| 配件 | 枪数 | 变化（一把枪写从多少到多少，多把枪写比例） |
|---|---|---|
| `barrel_stabilizer_l1` | 11 | `viewkick_pitch_base` ×0.9 到 ×0.97；`viewkick_pitch_random` ×0.75 到 ×0.82；`viewkick_yaw_base` ×0.85 到 ×0.97；`viewkick_yaw_random` ×0.8 到 ×0.92 |
| `barrel_stabilizer_l2` | 11 | `viewkick_pitch_base` ×0.85 到 ×0.94；`viewkick_pitch_random` ×0.7 到 ×0.79；`viewkick_yaw_base` ×0.8 到 ×0.94；`viewkick_yaw_random` ×0.75 到 ×0.89 |
| `barrel_stabilizer_l3` | 11 | `viewkick_pitch_base` ×0.8 到 ×0.9；`viewkick_pitch_random` ×0.65 到 ×0.75；`viewkick_yaw_base` ×0.75 到 ×0.9；`viewkick_yaw_random` ×0.7 到 ×0.85 |
| `barrel_stabilizer_l4_flash_hider` | 11 | `viewkick_pitch_base` ×0.8 到 ×0.85；`viewkick_pitch_random` ×0.65 到 ×0.7；`viewkick_yaw_base` ×0.75 到 ×0.85；`viewkick_yaw_random` ×0.7 到 ×0.8 |
| `corrupted_barrel` | 7 | `viewkick_pitch_base` ×0.85；`viewkick_pitch_random` ×0.7；`viewkick_yaw_base` ×0.85；`viewkick_yaw_random` ×0.8；`spread_stand_hip` ×1.4；`spread_stand_hip_run` ×1.3；`spread_air_hip` ×1.3；`spread_crouch_hip` ×1.3；`damage_headshot_scale` ×1.2；`spread_kick_on_fire_stand_hip` ×1.5；`spread_decay_rate` ×1.3 |

R-301 实测的俯仰后坐比例 **[实测，3 次平均]**。

| 配件 | 字段 `pitch_base` | 实测比例 | 峰值俯仰 |
|---|---|---|---|
| 无 | 1 | 0.96 | 4.42° |
| L1 | 0.95 | 1.00 | 4.60° |
| L3 | 0.85 | 0.87 | 3.99° |
| L4 | 0.85 | 0.79 | 3.65° |
| `corrupted_barrel` | 见上 | 0.83 | 3.81° |

L1 看不出差别，3 次的随机差比 5 % 大。`corrupted_barrel` 同时把爆头倍率从 1.3 提到 1.56、腰射散布从 3 提到 4.2 **[字段]**。

## 2. 弹匣（改发数）

| 配件 | 枪数 | 变化（一把枪写从多少到多少，多把枪写比例） |
|---|---|---|
| `bullets_mag_l1` | 8 | `ammo_clip_size` ×1.05 到 ×1.2 |
| `bullets_mag_l2` | 8 | `ammo_clip_size` ×1.15 到 ×1.4 |
| `bullets_mag_l3` | 8 | `ammo_clip_size` ×1.3 到 ×1.6 |
| `bullets_mag_l4` | 8 | `ammo_clip_size` ×1.3 到 ×1.6 |
| `highcal_mag_l1` | 7 | `ammo_clip_size` ×1.11 到 ×1.25 |
| `highcal_mag_l2` | 7 | `ammo_clip_size` ×1.21 到 ×1.5 |
| `highcal_mag_l3` | 7 | `ammo_clip_size` ×1.39 到 ×1.75 |
| `highcal_mag_l4` | 7 | `ammo_clip_size` ×1.39 到 ×1.75 |
| `energy_mag_l1` | 6 | `ammo_clip_size` ×1.1 到 ×1.2 |
| `energy_mag_l2` | 6 | `ammo_clip_size` ×1.2 到 ×1.4 |
| `energy_mag_l3` | 6 | `ammo_clip_size` ×1.33 到 ×1.67 |
| `energy_mag_l4` | 6 | `ammo_clip_size` ×1.33 到 ×1.67 |
| `sniper_mag_l1` | 4 | `ammo_clip_size` ×1.17 到 ×1.33 |
| `sniper_mag_l2` | 4 | `ammo_clip_size` ×1.33 到 ×1.67 |
| `sniper_mag_l3` | 4 | `ammo_clip_size` ×1.5 到 ×2 |
| `sniper_mag_l4` | 4 | `ammo_clip_size` ×1.5 到 ×2 |
| `corrupted_mag` | 21 | `ammo_clip_size` ×1.55 到 ×2.25；`reload_time` ×1.3 到 ×1.45；`reloadempty_time` ×1.3 到 ×1.45；`reloadsegment_time_loop` 0.4 → 0.46 |

- **普通弹匣不改换弹时间**：`bullets_mag_l3` 实测 2.40 s 不变。
- `corrupted_mag`：R-301 37 发，但换弹 2.4 → 3.24 s **[实测]**。

## 3. 枪托（改所有动作时间）

| 配件 | 枪数 | 变化（一把枪写从多少到多少，多把枪写比例） |
|---|---|---|
| `stock_tactical_l1` | 18 | `reload_time` ×0.967；`reloadempty_time` ×0.967；`holster_time` ×0.85；`deploy_time` ×0.85；`raise_time` ×0.9；`lower_time` ×0.9；`zoom_time_in` ×0.85；`zoom_time_out` ×0.85；`reloadsegment_time_loop` 0.51 → 0.484；`viewdrift_ads_stand_scale_pitch` ×0.85；`viewdrift_ads_stand_scale_yaw` ×0.85 |
| `stock_tactical_l2` | 18 | `reload_time` ×0.933；`reloadempty_time` ×0.933；`holster_time` ×0.8；`deploy_time` ×0.8；`raise_time` ×0.85；`lower_time` ×0.85；`zoom_time_in` ×0.8；`zoom_time_out` ×0.8；`reloadsegment_time_loop` 0.51 → 0.446；`viewdrift_ads_stand_scale_pitch` ×0.75；`viewdrift_ads_stand_scale_yaw` ×0.75 |
| `stock_tactical_l3` | 18 | `reload_time` ×0.9；`reloadempty_time` ×0.9；`holster_time` ×0.75；`deploy_time` ×0.75；`raise_time` ×0.8；`lower_time` ×0.8；`zoom_time_in` ×0.75；`zoom_time_out` ×0.75；`reloadsegment_time_loop` 0.51 → 0.408；`viewdrift_ads_stand_scale_pitch` ×0.55；`viewdrift_ads_stand_scale_yaw` ×0.55 |
| `corrupted_tactical_stock` | 15 | `ammo_clip_size` ×0.75 到 ×0.81；`reload_time` ×0.9；`reloadempty_time` ×0.9；`holster_time` ×0.75；`deploy_time` ×0.75；`raise_time` ×0.8；`lower_time` ×0.8；`zoom_time_in` ×0.75；`zoom_time_out` ×0.75；`reloadsegment_time_loop` 0.51 → 0.408；`viewdrift_ads_stand_scale_pitch` ×0.55；`viewdrift_ads_stand_scale_yaw` ×0.55 |
| `stock_sniper_l1` | 7 | `reload_time` ×0.967；`reloadempty_time` ×0.967；`holster_time` ×0.75 到 ×0.85；`deploy_time` ×0.75 到 ×0.85；`raise_time` ×0.8 到 ×0.9；`lower_time` ×0.8 到 ×0.9；`zoom_time_in` ×0.8 到 ×0.9；`zoom_time_out` ×0.8 到 ×0.9；`reloadsegment_time_loop` 0.4 → 0.38；`viewdrift_ads_stand_scale_pitch` ×0.7 到 ×0.8；`viewdrift_ads_stand_scale_yaw` ×0.7 到 ×0.8 |
| `stock_sniper_l2` | 7 | `reload_time` ×0.933；`reloadempty_time` ×0.933；`holster_time` ×0.7 到 ×0.8；`deploy_time` ×0.7 到 ×0.8；`raise_time` ×0.75 到 ×0.85；`lower_time` ×0.75 到 ×0.85；`zoom_time_in` ×0.75 到 ×0.85；`zoom_time_out` ×0.75 到 ×0.85；`reloadsegment_time_loop` 0.4 → 0.35；`viewdrift_ads_stand_scale_pitch` ×0.5 到 ×0.6；`viewdrift_ads_stand_scale_yaw` ×0.5 到 ×0.6 |
| `stock_sniper_l3` | 7 | `reload_time` ×0.9；`reloadempty_time` ×0.9；`holster_time` ×0.65 到 ×0.75；`deploy_time` ×0.65 到 ×0.75；`raise_time` ×0.7 到 ×0.8；`lower_time` ×0.7 到 ×0.8；`zoom_time_in` ×0.7 到 ×0.8；`zoom_time_out` ×0.7 到 ×0.8；`reloadsegment_time_loop` 0.4 → 0.32；`viewdrift_ads_stand_scale_pitch` ×0.2 到 ×0.35；`viewdrift_ads_stand_scale_yaw` ×0.2 到 ×0.35 |
| `stock_sniper_l4` | 7 | `reload_time` ×0.9；`reloadempty_time` ×0.9；`holster_time` ×0.65 到 ×0.75；`deploy_time` ×0.65 到 ×0.75；`raise_time` ×0.7 到 ×0.8；`lower_time` ×0.7 到 ×0.8；`zoom_time_in` ×0.7 到 ×0.8；`zoom_time_out` ×0.7 到 ×0.8；`viewdrift_ads_stand_scale_pitch` ×0.2 到 ×0.35；`viewdrift_ads_stand_scale_yaw` ×0.2 到 ×0.35 |
| `corrupted_stock_sniper` | 5 | `ammo_clip_size` ×0.75 到 ×0.833；`reload_time` ×0.9；`reloadempty_time` ×0.9；`holster_time` ×0.75；`deploy_time` ×0.75；`raise_time` ×0.8；`lower_time` ×0.8；`zoom_time_in` ×0.8；`zoom_time_out` ×0.8；`fire_rate` ×1.2；`rechamber_time` ×0.8；`reloadsegment_time_loop` 0.4 → 0.32；`viewdrift_ads_stand_scale_pitch` ×0.2；`viewdrift_ads_stand_scale_yaw` ×0.2 |

R-301 和 G7 实测的开镜时间 **[实测]**：

| 配件 | 开镜 / 关镜（s） |
|---|---|
| R-301 无 | 0.270 / 0.230 |
| `stock_tactical_l1` | 0.229 / 0.196 |
| `stock_tactical_l3` | 0.203 / 0.173 |
| `corrupted_tactical_stock` | 0.203 / 0.172，弹匣 21 → 17 |
| G7 无 | 0.320 / 0.250 |
| `stock_sniper_l1` | 0.256 / 0.200 |
| `stock_sniper_l3` | 0.224 / 0.175 |
| `corrupted_stock_sniper` | 0.256 / 0.200，弹匣 10 → 8，射速 4.1 → 4.92 |

换弹实测见 [01 §4](01-reload.md)。枪托还按比例减小开镜漂移：战术 L3 约 ×0.55，狙击 L3（G7）约 ×0.35。

## 4. 激光（改腰射散布）

| 配件 | 枪数 | 变化（一把枪写从多少到多少，多把枪写比例） |
|---|---|---|
| `laser_sight_l1` | 8 | `spread_stand_hip` ×0.8；`spread_stand_hip_run` ×0.8；`spread_air_hip` ×0.8；`spread_crouch_hip` ×0.8；`spread_kick_on_fire_stand_hip` ×0.8；`spread_decay_rate` ×1.2 |
| `laser_sight_l2` | 8 | `spread_stand_hip` ×0.7；`spread_stand_hip_run` ×0.7；`spread_air_hip` ×0.7；`spread_crouch_hip` ×0.7；`spread_kick_on_fire_stand_hip` ×0.7；`spread_decay_rate` ×1.3 |
| `laser_sight_l3` | 8 | `spread_stand_hip` ×0.6；`spread_stand_hip_run` ×0.6；`spread_air_hip` ×0.6；`spread_crouch_hip` ×0.6；`spread_kick_on_fire_stand_hip` ×0.6；`spread_decay_rate` ×1.4 |
| `laser_sight_l4` | 8 | `spread_stand_hip` ×0.6；`spread_stand_hip_run` ×0.6；`spread_air_hip` ×0.6；`spread_crouch_hip` ×0.6；`spread_kick_on_fire_stand_hip` ×-0.667 到 ×-0.1 |
| `corrupted_laser` | 6 | `reload_time` ×0.6；`reloadempty_time` ×0.6；`viewkick_pitch_base` ×1.6；`viewkick_pitch_random` ×1.6；`viewkick_yaw_base` ×1.6；`viewkick_yaw_random` ×1.6；`spread_stand_hip` ×0.6；`spread_stand_hip_run` ×0.6；`spread_air_hip` ×0.6；`spread_crouch_hip` ×0.6；`spread_kick_on_fire_stand_hip` ×0.6；`spread_decay_rate` ×1.4 |

R-99 腰射散布上限实测 **[实测]**：无 4.0° → L1 3.2° → L3 2.4° → `corrupted_laser` 2.4°。

L4 的每发 kick 是**负的**：越打越准（`spread_kick_on_fire_stand_hip` −0.1）**[字段，没跑]**。`corrupted_laser` 同时把换弹 ×0.6、后坐 ×1.6。

## 5. 霰弹枪栓（改射速）

| 配件 | 枪数 | 变化（一把枪写从多少到多少，多把枪写比例） |
|---|---|---|
| `shotgun_bolt_l1` | 4 | `fire_rate` ×1.05 到 ×1.1；`rechamber_time` 1.1 → 1.018 |
| `shotgun_bolt_l2` | 4 | `fire_rate` ×1.09 到 ×1.15；`rechamber_time` 1.1 → 0.957 |
| `shotgun_bolt_l3` | 4 | `fire_rate` ×1.13 到 ×1.2；`rechamber_time` 1.1 → 0.924 |
| `shotgun_bolt_l4` | 4 | `fire_rate` ×1.13 到 ×1.2；`rechamber_time` 1.1 → 0.924 |

EVA-8 射速实测读回 2.8 → L1 3.02 → L3 3.36。

## 6. 瞄具

见 [03 §4](03-ads-optics.md)。多数枪上瞄具还会小幅减小后坐基数，比如 `optic_cq_hcog_bruiser` `viewkick_pitch_base` ×0.64 到 ×0.8 **[字段]**，这条要看具体枪，见 A-MOD-DIFFS。

## 7. 改玩法的 Hop-up

全部 **[实测]**。"只给标记"是只装 `hopup_*`；"给生效 mod"是直接把切换 mod 给上。**玩家按键切换这一步没测到**，按键没找到。

| Hop-up | 枪 | 只给标记 | 给生效 mod |
|---|---|---|---|
| Turbocharger | Havoc | 按键到第一发 0.434 → 0.024 s | 不需要 |
| Turbocharger | Devotion | 起步间隔 0.20 → 0.15 s，后面相同 | 不需要 |
| Turbocharger | Nemesis | 没变 | |
| Selectfire | Prowler | 不变，连发间隔 0.049 s | `altfire_selectfire`：全自动 13.1 发/s，伤害 16 → 17 |
| Selectfire | Charge Rifle | 不变 | 两发间隔 0.96 s，45 / 74 伤害（只有 2 发） |
| Anvil | R-301 | 不变，15 伤害 | `altfire_highcal`：32 伤害，每发 2 弹，半自动 |
| Anvil | Flatline | | 39 伤害，半自动 |
| 单发模式 | R-301、Flatline | | `altfire`：半自动，伤害不变 |
| Double Tap | EVA-8 | 不变 | `altfire_double_tap`：两发间隔 0.149 s，伤害不变 |
| Double Tap | G7 | 不变 | 0.069 s，伤害 33 不变 |
| Double Tap | Alternator | 不变 | 每次扣 2 弹、2 个命中，伤害 18 → 14 |
| Hammerpoint | P2020 / RE-45 / Mozambique | 标记就生效：24 → 26、14 → 18、17 → 19（无盾假人）。打盾没有加成 | |
| Skullpiercer | Longbow / Wingman / 30-30 | 头部 98 → 115、70 → 87、57 → 67，身体不变 | |
| Shatter | 30-30 | 不变（43） | `shatter_rounds_hipfire`：7 × 8，最外约 2.3°（150 u），腰射开镜都一样 |
| Shatter | Bocek | 不变（60） | `shatter_rounds_hipfire` 给不上 |
| Choke | Peacekeeper | 不变 | `choke` 按住蓄力：半径 1.28° → 0.72° |
| Choke | Triple Take | 不变 | `choke`：0.22° → 0.14° |
| Disruptor | Alternator / RE-45 / Peacekeeper | 标记就生效，打盾 5 发：90 → 110、73 → 80、495 → 540 | |
| Energize | Sentinel | | `energized`：70 → 88 |
| Energize | Rampage | | `energized`：5 → 6.5 发/s（触发入口没找到） |
| Marksman's Tempo | Sentinel、Bocek | 不变 | 没测到提速，要脚本累积 |
| Boosted、Dual Shell、Kinetic | | 见 [01 §4](01-reload.md) | |

## 8. 其他字段变化

| 配件 | 枪数 | 变化（一把枪写从多少到多少，多把枪写比例） |
|---|---|---|
| `hopup_headshot_dmg` | 3 | `damage_headshot_scale` ×1.19 到 ×1.28 |
| `elevator_shooter` | 30 | `spread_air_hip` ×0.7 到 ×0.9；`viewkick_air_scale_ads` ×0.6 到 ×0.8 |
| `amped_damage` | 31 | `damage_near_value` ×1.14 到 ×1.22 |
| `fast_reload_mod` | 4 | `reload_time` ×0.538 |
| `auto_loader` | 31 | `reload_time` ×0.6；`reloadempty_time` ×0.6 |

`elevator_shooter` 空中散布变小，**推断**是 S21 的新机制。这些是给上 mod 后读回的字段，行为没单独跑。

## 9. 给了没上的

| 枪 | Mod | 结果 |
|---|---|---|
| Triple Take | `hopup_kinetic_loader` | **服务器关闭**（2 次）。Peacekeeper 正常 |
| Hemlok、Hemlok Elite、Wingman | `fast_reload_mod`、`overloaded_ammo` | 没报错，字段不变 |
| EVA-8 | `shotgun_bolt_l1..l4_double_tap` | 同上 |
| Peacekeeper | `hopup_kinetic_choke`、`kinetic_choke` | 同上 |
| 30-30 | `charged`、`in_ads` | 同上 |
| Bocek | `shatter_rounds_hipfire` | 同上 |

**推断**和 mod 个数上限有关，没查。

## 10. 还要确认

"刚配的那种配件"这句话有歧义。这次按 S21 最新的 `corrupted_*` 系列测了，也测了金色。另一种读法是"刚装上时有没有延迟或动画"，**[没测]**：脚本直接给枪带配件，走不到拾取流程。
