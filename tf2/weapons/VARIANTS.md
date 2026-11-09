# TF2 铁驭武器和 Apex（R5）同类枪：机制差别

2026-11-08，会话 `tf2-weapons`（由一个只读子任务对照文件写成，主会话核对过下面几条）。目的：看哪把 TF2 枪的机制和 R5 差得多，值得 HSD 单独写一页、照 TF2 重做；差得少的直接用 R5 的枪。这一页只比文件，**没有开游戏**；TF2 独有的 7 把枪才做了实测，见 [README.md](README.md)。

主会话核对过的：
- EVA-8 不发弹丸：`mp_weapon_shotgun.nut` 调 `ShotgunBlast`，`_weapon_utility.nut:497–580` 是"锥形内可见目标"查找，每个目标打一发"完美子弹"（`FireWeaponBullet_Special`，无散布）。✓
- Mastiff / Mozambique 是 3000 u/s 的 bolt，寿命随机 0.65–0.85 s（Mastiff，`mp_weapon_mastiff.nut:83–91`）、0.5–0.75 s（Mozambique，`mp_weapon_shotgun_pistol.nut:71–82`）。✓
- "即时命中（推断）"：实测核对见 README 的"即时命中核对"一节。

## 怎么读

| 简写 | 文件 |
|---|---|
| TF2 列 | `TF2-Research/weapons/data/wpn-values.tsv`，scope `mp`（多人模式铁驭拿到的值）。键名写在第一列 |
| R5 列 | 默认 `Apex-MovementAnalysis-RETICLE/research/combat/gun-measure/GUN-VARS.tsv` 的同名列 |
| AMD | 同目录 `A-MOD-DIFFS.tsv` 里"改前"的值（R5 裸枪的字段） |
| FIT | `research/combat/recoil-view/FIT-TABLE.tsv`（R5 弹簧、soft / hard、weaponFraction） |
| DSF | `gun-measure/D-STATIC-FIELDS.tsv` |
| DEXT | `gun-measure/D-EXTENSIONS.md` |
| CRS | `gun-measure/C-RELOAD-SUMMARY.tsv` |
| SR | `gun-measure/shotgun-reticle/SHOTGUN-RETICLE.md`；SCAT = 同目录 `scatter/SCATTER-300U.tsv`（HSD-Unity 按 R5 固定图案导出，SR §6 说和 R5 核对到 0.006°） |
| RV / AC | `research/combat/RECOIL-VIEW.md` / `ADS-CURVES.md` |
| .nut | `TF2-Research/local/vpk/client_mp_common/scripts/vscripts/weapons/` 下的脚本 |

- 多个键用 " / " 分开，值的顺序和键一样。
- **算** = 我用文件里的数算的。**推断** = 文件没有直接写。"R5 表里没有" = 上面几份 R5 表都找不到，没有从记忆补。
- 单位：两边都是 Source 单位（英寸）。
- **FOV 基准没查**。R5 的开镜 FOV = `zoom_fov` × `cl_fovScale`，腰射是 70 × `cl_fovScale`（AC §1）。TF2 只有一条文件线索：`scripts/weapons/mp_weapon_sniper.txt:219` 注释 `//3x zoom`，26.26° 按 tan 换算正好是 70° 的 3 倍（算）。只有这一条注释，不算查清，所以下面两边的 `zoom_fov` 只并排列，不比放大倍数。
- TF2 的 23 把枪**都没有腿部倍率键**（`wpn-values.tsv` 里搜不到 `leg`）。

## 1. 先说结论

| TF2 | Apex 同类 | 最大的差别 | 值得一页？ | 理由 |
|---|---|---|---|---|
| R-201 | R-301 | 即时命中（推断）+ 三段衰减 25 / 17 / 12；24 发 | 否 | 只是参数；共性差别见第 2 节 |
| R-101 | R-301 | 和 R-201 只差开镜后坐上限 2.0（R-201 2.5）、模型、默认 AOG | 否 | R-201 换皮 |
| Hemlok | Hemlok | 3 连发、组间 0.25 s、15.5 发/秒，和 R5 一样；伤害 33 / 25 / 20 对 20 | 否 | 同一机制 |
| G2A5 | G7 | 5.5 发/秒、14 发；腰射散布 5.5，冲刺 11 | 否 | 只是参数 |
| Flatline | Flatline | 后坐几乎全横向（俯仰 0 ± 0.1，偏航 −0.25 ± 1.125）；30 发 | 否 | 只是参数，后坐风格可以借鉴 |
| CAR | CAR | 14.1 发/秒、30 发；腰射散布 0 | 否 | 只是参数 |
| Alternator | Alternator | 伤害 35 / 18 / 14；双枪管交替的代码被注释掉了 | 否 | 只是参数 |
| Volt | Volt | 11 发/秒、33 发；没有能量弹体 | 否 | 只是参数 |
| R-97 | R-99 | 40 发；移动时后坐 ×2（`viewkick_move_scale`） | 否 | 只是参数 |
| Spitfire | Spitfire | 80 发；穿透 32 u；智能弹只在开发 mod 里 | 否 | 只是参数 |
| L-STAR | L-STAR | 35 发会自己回（9 发/秒），打空强制 6.03 s 换镜片；R5 是蓄力热量 | **是** | 两套过热做法，代码不能共用 |
| Devotion | Devotion | 5 → 15 发/秒用 1.75 s（R5 1.5 s）；55 发 | 否 | 同一机制 |
| Kraber | Kraber | 弹速 10000（R5 29500）；350 伤；1.85 发/秒；跳弹 mod | 否 | 只是参数；跳弹另记 |
| Longbow | Longbow | 弹体代码被注释掉，即时命中（推断）；3 发/秒 | 否 | 只是参数 |
| EVA-8 | EVA-8 | **不是弹丸**：锥形里每个目标吃一次伤害，200（100 u）→ 10（750 u）；开镜不收紧 | **是** | R5 是 8 颗固定图案弹丸，整套不同 |
| Mastiff | Mastiff | 8 颗**慢速弹**（3000 u/s），0.65–0.85 s 后消失；R5 是 5 颗 16000 u/s | **是** | 弹看得见、有射程上限，手感不同 |
| RE-45 | RE-45 | 伤害 20 / 13 / 9 三段；`zoom_fov` 70 | 否 | 只是参数 |
| P2016 | P2020 | 8 发/秒、12 发；爆头 ×2 | 否 | 只是参数 |
| B3 Wingman | Wingman | 伤害 40 到 1500 u 都不降（R5 50）、爆头 ×2；即时命中（推断） | 否 | 只是参数 |
| Wingman Elite | Wingman | 弹体 12000、所有姿态散布 0、穿透 32、跳弹 mod；75 / 55 / 35 | 也许 | 零散布 + 跳弹是 R5 没有的玩法 |
| Mozambique | Mozambique | 3 颗慢速弹 3000 u/s，0.5–0.75 s 消失；中心 + 下方两颗 | **是** | 和 Mastiff 同一套，合成一页 |
| Charge Rifle | Charge Rifle | 没弹匣、不能换弹、共 20 发；蓄满 1.3 s 才出；300 伤、不能爆头 | 也许 | 反泰坦设计；HSD 做泰坦对抗时再看 |
| Double Take | Triple Take | 3 颗弹一字排开、每发耗 2 发；散布开镜不变；10000 u/s | 也许 | 结构和 R5 接近，差在耗弹和没有收束 |

**一句话**：单把枪值得写的是 **EVA-8、Mastiff + Mozambique（合一页）、L-STAR**；也许的是 Charge Rifle、Double Take、Wingman Elite。其余都是参数不同。但第 2 节有三条**全体共有**的系统差别（即时命中、三段衰减、没有图案表的后坐），如果 HSD 想要"TF2 手感"，值得写一页系统说明，而不是每把枪一页。

## 2. 全体共有的差别（下面各节不再重复）

| 项 | TF2 | R5 | 依据 |
|---|---|---|---|
| 命中方式 | 16 把枪 txt 里没有弹速键（`bolt_speed`、`projectile_launch_speed`），也没有开火脚本，或脚本调 `FireWeaponBullet`（`mp_weapon_lmg.nut`、`mp_weapon_alternator_smg.nut`、`mp_weapon_defender.nut`）→ **推断即时命中**。用弹体的只有 Kraber、Double Take、Wingman Elite、Mastiff、Mozambique、L-STAR | 每把枪都有 `projectile_launch_speed`；落差实测和弹体公式一致（DEXT §3） | 文件没写 `FireWeaponBullet` 一定即时，所以是推断 |
| 伤害衰减 | 14 把有 near / far / very_far 三段，近距离高很多 | `damage_near_value` = `far`（只有 Charge Rifle 反着升），DEXT §2 实测不衰减；`damage_very_far_value` 键也在，值等于 near（AMD） | |
| 部位 | 只有 `damage_headshot_scale`，没有腿部键；另有 `headshot_distance`（18 把，脚本没用到，含义没查） | `damage_headshot_scale` + `damage_leg_scale` | |
| 泰坦护甲 | `damage_*_value_titanarmor` 每把都有，比普通伤害高很多；`damage_heavyarmor_nontitan_scale` 多数 0.35；`damage_rodeo` | 键还在，值等于普通伤害（AMD） | 只 TF2 有用 |
| 后坐模型 | 每发 = `viewkick_*_base` ± `random`，连射时用 `viewkick_scale_min/max`、`valuePerShot` 放大；**没有图案表键**（原始 txt 搜不到 `viewkick_pattern`） | 自动枪 `viewkick_pitch_base` = 1（AMD），kick = 图案表这一行 × base（RV §4）；Wingman、P2020 没有图案 | TF2 的 base 是度数，R5 自动枪的 1 是倍率，**不能直接比** |
| 永久后坐 | `viewkick_perm_*`：Hemlok −0.35 ± 0.1，DMR / Double Take −0.47 ± 0.23，EVA −0.5 ± 1.1，Wingman 0 ± 1.0，P2016 0.1 ± 0.8 | R5 表里没有 | 按名字推断是"不回弹的那部分"，没查 |
| 弹簧 | `scripts/weapons/springs.txt`，每个条目一套，**没有 hot 条目**（搜 hot / heat 只命中 `shotgun` 这个名字） | 冷 / 热两套，按热度插值（RV §2.1、§4） | 例：TF2 `rspn101` 腰 k110 d10、镜 k160 d30；R5 `rspn101_vkp` 腰 40 / 20、镜 115 / 20，hot 镜 0 / 60（RV §4） |
| 后坐给枪还是给画面 | 步枪腰射 `viewkick_hipfire_weaponFraction` 0.5–0.65 | 步枪腰射 0.05–0.2（FIT） | R5 里画面 = (1 − fraction) × punch（RV §1）；推断 TF2 同义，即腰射约一半后坐不进画面 |
| 换弹分段键 | `reload_time_late1..2`、`reloadempty_time_late1..5` | 同名键 R5 也有（AMD），**很多枪和 TF2 的比例一样**（下表） | 含义别处在查，这里只列 |
| 只有 TF2 有 | `spread_wallrunning` / `spread_wallhanging`（6 把）；mod `pas_run_and_gun`（冲刺中开火）、`smart_lock`、`burn_mod_*`（伤害 ++10 这类） | R5 表里没有 | |

换弹分段：`late1 / reload_time`，`emptyLate1 / reloadempty_time`，`emptyLate2 / reloadempty_time`（全部算；R5 的 late 值来自 AMD）：

| 对 | TF2 | R5 | 一样？ |
|---|---|---|---|
| R-201 → R-301 | 0.750 / 0.815 / 0.500 | 0.750 / 0.816 / 0.500 | 一样 |
| Hemlok | 0.643 / 0.700 / 0.370 | 0.642 / 0.702 / 0.372 | 一样 |
| G2A5 → G7 | 0.527 / 0.606 / 0.390 | 0.525 / 0.607 / 0.390 | 一样 |
| Alternator | 0.448 / 0.593 / 0.370 | 0.447 / 0.592 / 0.372 | 一样 |
| Kraber | 0.608 / 0.729 / 0.485 | 0.609 / 0.728 / 0.484 | 一样（R5 `late2` 例外，见第 4 节） |
| Longbow、Wingman、P2016 → P2020 | 绝对值都一样 | 绝对值都一样 | 一样 |
| Flatline | 0.289 / 0.519 / 0.185 | 0.500 / 0.645 / 0.387 | 不一样 |
| Volt | 0.547 / 0.730 / 0.395 | 0.500 / 0.668 / 0.348 | 不一样 |

R5 的换弹动画很像是从 TF2 按比例拉长的（推断）。

## 3. 每一对

### 3.1 R-201 → R-301

| 项（键） | TF2 R-201 | R5 R-301 | 备注 |
|---|---|---|---|
| 开火 `fire_mode` · `fire_rate` | auto · 13.5（74 ms，算） | `is_semi_auto` 0 · 13.5（74 ms，算） | 一样 |
| 弹匣 `ammo_clip_size` | 24 | 21 | |
| 伤害 `damage_near / far / very_far_value` | 25 / 17 / 12 | 15 / 15 / 15（very_far 取 AMD） | |
| 距离 `damage_near / far / very_far_distance` | 1500 / 2000 / 3500 | 1000 / 2500 / R5 表里没有 | |
| 爆头 `damage_headshot_scale`（R5 加 `damage_leg_scale`） | 1.5，没有腿部键；`headshot_distance` 1400 | 1.3 / 腿 0.75 | |
| 泰坦 `damage_near / far_value_titanarmor` | 70 / 50 | 15 / 15（AMD） | |
| 命中 `projectile_launch_speed` / `_gravity_scale` / `_drag_coefficient` | 没有这些键，没有开火脚本 → 即时（推断） | 29000 / 1.3 / 0.0025 | |
| 换弹 `reload_time / reloadempty_time` | 2.2 / 2.92 | 2.4 / 3.2 | |
| 分段 `reload_time_late1`；`reloadempty_time_late1 / late2` | 1.65；2.38 / 1.46 | 1.8；2.61 / 1.6（AMD） | 比例一样 |
| 开镜 `zoom_time_in / out` · `zoom_fov` | 0.25 / 0.2 · 35 | 0.27 / 0.23 · 55 | FOV 基准没查 |
| 散布 `spread_stand_hip / spread_stand_ads` | 2.0 / 0 | 3 / 0 | TF2 跑、冲刺、空中都是 2.0，挂墙 6.5 |
| 散布增长 `spread_kick_on_fire_stand_hip` · `spread_max_kick_stand_hip` · `spread_decay_rate / delay` | 0.5 · 8.0 · 5 / 0.05 | 0.2（AMD）· R5 表里没有 · 100 / 0.25 | |
| 后坐 `viewkick_pitch_base ± random`，`yaw_base ± random` | −0.25 ± 0.5，0 ± 0.5 | 1 ± 1，1 ± 1（AMD，图案倍率） | 模型不同 |
| 分配 `pitch_hardScale / softScale`；`weaponFraction` 腰 / 镜 | 0.5 / 1；0.5 / 0.0 | 0.35 / 2.325；0.05 / 0（FIT） | |
| 倍率 `viewkick_scale_min–max` 腰 · 镜；`air_scale_ads` · `duck_scale` · `scale_firstshot_ads` | 1.5–2.0 · 1.5–2.5；2.0 · 0.9 · 1.25 | R5 表里没有；2 · 1 · 1 | |

### 3.2 R-101 → R-301

`wpn-values.tsv` 里 R-101（`mp_weapon_rspn101_og`）和 R-201 逐键比，机制键只差一项：`viewkick_scale_max_ads` 2.0（R-201 2.5）。其余是模型、图标、`viewmodel_offset_ads` "0 0 −0.85"（R-201 "0 0 0"）、`bodygroup6_name` `sight_aog_r1` = 1（默认带 AOG）。和 R5 的差别同 3.1。

### 3.3 Hemlok → Hemlok

| 项（键） | TF2 Hemlok | R5 Hemlok | 备注 |
|---|---|---|---|
| 开火 `fire_mode` · `fire_rate` · `burst_fire_count / delay` | semi-auto · 15.5（65 ms，算）· 3 / 0.25 | `is_semi_auto` 1 · 15.5 · 3 / 0.25 | 完全一样；R5 按住只打一组（DEXT 结论 3） |
| `ammo_min_to_fire` | 3 | R5 表里没有 | TF2 剩不到 3 发不能开火 |
| 弹匣 | 24 | 21 | |
| 伤害 near / far / very_far | 33 / 25 / 20 | 20 / 20 / 20（AMD） | |
| 距离 | 1500 / 2000 / 3500 | 1000 / 2500 | |
| 爆头 | 1.5（`headshot_distance` 1400） | 1.4 / 腿 0.75 | |
| 泰坦 | 75 / 45 | 20 / 20（AMD） | |
| 命中 | 即时（推断） | 27500 / 1.3 / 0.0025 | |
| 换弹 · 分段 | 2.52 / 3；1.62；2.10 / 1.11 | 2.4 / 2.85；1.54；2 / 1.06（AMD） | 比例一样 |
| 开镜 | 0.25 / 0.2 · 35 | 0.27 / 0.23 · 55 | |
| 散布 腰 / 镜 | 5.5 / 0（跑 8，冲刺 11，蹲 4.5，空中 11） | 4 / 0 | |
| 散布增长 · 上限 · 回落 | 0.6 · 8.0 · 4 / 0.1 | 0.45（AMD）· R5 表里没有 · 18 / 0.3 | |
| 后坐 | −0.95 ± 0.5，0.1 ± 1.1；永久 −0.35 ± 0.1 | 1 ± 1，1 ± 1（AMD） | |
| 分配 | 1.0 / 0.65；0.65 / 0.1 | 0.4 / 1.75；0.2 / 0（FIT） | |
| 倍率 | 腰 0.1–0.6，镜 0.1–1.0，`scale_firstshot_hipfire` 1.2；空中 2 | 空中 2 · 蹲 1 · 第一发 1 | |

### 3.4 G2A5 → G7（远亲）

| 项（键） | TF2 G2A5 | R5 G7 | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 5.5（182 ms，算） | `is_semi_auto` 1 · 4.1（244 ms，算） | |
| 弹匣 | 14 | 10 | |
| 伤害 near / far | 40 / 35（没有 very_far） | 33 / 33 | |
| 距离 | 1500 / 2000 | 1000 / 2500 | |
| 爆头 | 1.5（1400） | 1.45 / 腿 0.75 | |
| 泰坦 | 140 / 110 | 33 / 33（AMD） | |
| 命中 | 即时（推断）；`damage_flags` 带 `DF_KNOCK_BACK` | 29000 / 1.4 / 0.0033 | |
| 换弹 · 分段 | 2.2 / 2.64；1.16 / 0.59；1.60 / 1.03 / 0.84 | 2.4 / 3；1.26 / 0.64；1.82 / 1.17 / 0.96（AMD） | 比例一样 |
| 开镜 | 0.25 / 0.2 · 35 | 0.32 / 0.25 · 55 | |
| 散布 腰 / 镜 | 5.5 / 0（跑 8，冲刺 11，空中 11）；开镜每发 +0.075 | 3 / 0 | |
| 散布增长 · 上限 · 回落 | 0.7 · 8.0 · 3 / 0.1 | 0.75（AMD）· R5 表里没有 · 6 / 0.24 | |
| 后坐 | −0.17 ± 0.17，0.1 ± 0.25 | 1 ± 1，1 ± 1（AMD） | |
| 分配 | 1.0 / 0.3；0.5 / 0.3 | 0.3 / 2.4；0.2 / 0（FIT） | |
| 倍率 | 腰 0.3–1.5，镜 0.3–0.5；空中 3.0；第一发镜 0.75 | 空中 1 · 蹲 1 · 第一发 1 | |

### 3.5 Flatline → Flatline

| 项（键） | TF2 Flatline（`vinson`） | R5 Flatline | 备注 |
|---|---|---|---|
| 开火 | auto · 10（100 ms，算） | 0 · 10 | 一样 |
| 弹匣 | 30 | 19 | |
| 伤害 | 30 / 20 / 15 | 20 / 20 / 20（AMD） | |
| 距离 | 1500 / 2000 / 3500 | 1000 / 2500 | |
| 爆头 | 1.5（1400） | 1.3 / 腿 0.75 | |
| 泰坦 | 100 / 80 | 20 / 20（AMD） | |
| 命中 | 即时（推断） | 24000 / 1.3 / 0.0025 | |
| 换弹 · 分段 | 2.073 / 2.7；0.6；1.4 / 0.5 | 2.4 / 3.1；1.2；2 / 1.2（AMD） | 比例不一样 |
| 开镜 | 0.25 / 0.2 · 35 | 0.27 / 0.23 · 55 | |
| 散布 腰 / 镜 | 1.0 / 0（空中 5，跑墙 5，挂墙 6.5） | 4.5 / 0 | TF2 腰射准很多 |
| 散布增长 · 上限 · 回落 | 0.5 · 2.0 · 4 / 0.1 | 0.2（AMD）· R5 表里没有 · 100 / 0.25 | |
| 后坐 | **0 ± 0.1，−0.25 ± 1.125** | 1 ± 1，1 ± 1（AMD） | TF2 几乎全是左右晃 |
| 分配 | **hard 0** / soft 1；0.65 / 0.0 | 0.45 / 2；0.1 / 0（FIT） | |
| 倍率 | 腰 1.5–2.0，镜 1.5–2.0；第一发腰 2、镜 0；`viewkick_hover_scale` 1.5 | 空中 2 · 蹲 1 · 第一发 1；hover R5 表里没有 | |

### 3.6 CAR → CAR

| 项（键） | TF2 CAR | R5 CAR | 备注 |
|---|---|---|---|
| 开火 | auto · 14.1（71 ms，算） | 0 · 15.5（65 ms，算） | |
| 弹匣 | 30 | 20 | |
| 伤害 | 25 / 13 / 10 | 14 / 14 / 14（AMD） | |
| 距离 | 1000 / 1500 / 3000 | 800 / 1500 | |
| 爆头 | 1.5（750） | 1.25 / 腿 0.8 | |
| 泰坦 | 70 / 35 | 14 / 14（AMD） | |
| 命中 | 即时（推断） | 18000 / 1.15 / 0.0025 | |
| 换弹 · 分段 | 1.8 / 2.53；0.82；1.46 / 0.79 | 1.7 / 2.13；0.82；1.26 / 0.75（AMD） | |
| 开镜 · `ads_move_speed_scale` | 0.2 / 0.15 · 45 · 0.8 | 0.2 / 0.2 · 60 · 0.75 | |
| 散布 腰 / 镜 | **0 / 0**（空中 1.5），不随开火增长 | 2 / 0.35 | |
| 回落 | 30 / 0.15 | 增长 0.18（AMD）；12 / 0.15 | |
| 后坐 | −0.2 ± 0.5，0 ± 1.0 | R5 表里没有 | |
| 分配 | 1.0 / 2.0；0.35 / 0.1 | 0.39 / 3.525；0.25 / 0.1（FIT） | |
| 倍率 | 腰 1.75–2，镜 0.5；第一发腰 0.6、镜 1.35；空中 1.5；开镜 view drift `viewdrift_ads_speed_pitch` 0.65 | 空中 2 · 蹲 1 · 第一发 1 | |

### 3.7 Alternator → Alternator

| 项（键） | TF2 Alternator | R5 Alternator | 备注 |
|---|---|---|---|
| 开火 | auto · 10（100 ms，算） | 0 · 10 | 一样 |
| 弹匣 | 20 | 18 | |
| 伤害 | 35 / 18 / 14 | 18 / 18 / 18（AMD） | |
| 距离 | 1000 / 1500 / 3000 | 900 / 1500 | |
| 爆头 | 1.5（750） | 1.25 / 腿 0.8 | |
| 泰坦 | 100 / 60 | 18 / 18（AMD） | |
| 命中 | `mp_weapon_alternator_smg.nut`：`FireWeaponBullet` 1 发；左右枪管交替偏移的代码被注释掉 → 即时（推断） | 19000 / 1.2 / 0.0025；`projectiles_per_shot` 1（AMD）；DSF 有第二枪口焰 `fx_muzzle_flash2_*` | |
| 换弹 · 分段 | 2.3 / 2.7；1.03；1.6 / 1.0 | 1.9 / 2.23；0.85；1.32 / 0.83（AMD） | 比例一样 |
| 开镜 | 0.2 / 0.15 · 45 | 0.22 / 0.2 · 60 | |
| 散布 腰 / 镜 · 回落 | 0 / 0（空中 1.5）· 30 / 0.15 | 2 / 0.35 · 增长 0.18（AMD）· 12 / 0.15 | |
| 后坐 | 0 ± 0.2，0 ± 1.8 | 1 ± 1，1 ± 1（AMD） | TF2 偏航为主 |
| 分配 | 1.0 / 2.0；0.2 / 0.25 | 0.35 / 1.6；0.15 / 0（FIT） | |

### 3.8 Volt → Volt

| 项（键） | TF2 Volt（`hemlok_smg`） | R5 Volt | 备注 |
|---|---|---|---|
| 开火 | auto · 11（91 ms，算） | 0 · 12（83 ms，算） | |
| 弹匣 | 33 | 20 | |
| 伤害 | 25 / 15 / 12 | 16 / 16 / 16（AMD） | |
| 距离 | 1000 / 1500 / 3000 | 800 / 1500 | |
| 爆头 | 1.5（750） | 1.25 / 腿 0.8 | |
| 泰坦 | 90 / 60 | 16 / 16（AMD） | |
| 命中 | 即时（推断） | 20000 / 1.05 / **0**；DSF `bolt_hitsize` 0.2，`impact_effect_table` `pulse_bullet` | R5 是能量弹体 |
| 换弹 · 分段 | 1.5 / 2.0；0.82；1.46 / 0.79 | 2 / 2.5；1；1.67 / 0.87（AMD） | 比例不一样 |
| 开镜 | 0.2 / 0.15 · 45 | 0.2 / 0.2 · 60 | |
| 散布 腰 / 镜 · 回落 | 0 / 0（空中 1.5）· 2.3 / 0.1 | 2 / 0.35 · 增长 0.15（AMD）· 12 / 0.15 | |
| 后坐 | −0.15 ± 0.35，0.1 ± 0.4；永久 −0.06 ± 0.395、偏航 0 ± 0.795 | 1 ± 1，1 ± 1（AMD） | |
| 分配 | 0.9 / 1.2；0.1 / 0.3 | 0.45 / 5.4；0.35 / 0.1（FIT） | |
| 其他 | `raise_from_sprint_time` 0 | GUN-VARS 同名列 0 | 一样 |

### 3.9 R-97 → R-99

| 项（键） | TF2 R-97 | R5 R-99 | 备注 |
|---|---|---|---|
| 开火 | auto · 18（56 ms，算） | 0 · 18 | 一样 |
| 弹匣 | 40 | 18 | |
| 伤害 | 20 / 12 / 10 | 12 / 12 / 12（AMD） | |
| 距离 | 1000 / 1500 / 3000 | 900 / 1500 | |
| 爆头 | 1.5（750） | 1.25 / 腿 0.8 | |
| 泰坦 | 65 / 35 | 12 / 12（AMD） | |
| 命中 | 即时（推断） | 19000 / 1.2 / 0.0025 | |
| 换弹 · 分段 | 1.8 / 2.35；0.76；1.35 / 0.73 | 1.8 / 2.45；0.82；1.45 / 0.83（AMD） | |
| 开镜 | 0.2 / 0.15 · 45 | 0.22 / 0.2 · 60 | |
| 散布 腰 / 镜 | 0 / 0（空中 1.5）；腰每发 +0.5 到 2.0，镜上限 0.4 | 2 / 0.35；增长 0.18（AMD） | |
| 回落 | 30 / 0.3 | 12 / 0.15 | |
| 后坐 | −0.2 ± 0.35，−0.1 ± 0.6 | 1.15 ± 1，1 ± 1（AMD） | |
| 分配 | 0.5 / 1.2；0.1 / 0.125 | 0.4 / 4.25；0.3 / 0.1（FIT） | |
| 倍率 | 腰 1.5，镜 1；第一发腰 1.5、镜 0.85；空中 1.5；**`viewkick_move_scale` 2.0** | 空中 2 · 蹲 1 · 第一发 1；move R5 表里没有 | |

### 3.10 Spitfire → Spitfire

| 项（键） | TF2 Spitfire（`lmg`） | R5 Spitfire | 备注 |
|---|---|---|---|
| 开火 | auto · 9.0（111 ms，算） | 0 · 9 | 一样 |
| 弹匣 | **80** | 35 | |
| 伤害 | 35 / 25 / 20 | 21 / 21 / 21（AMD） | |
| 距离 | 1800 / 2000 / 3000 | 1500 / 2500 | |
| 爆头 | 1.5（1800） | 1.25 / 腿 0.85 | |
| 泰坦 | 80 / 60 | 21 / 21（AMD） | |
| 命中 | `mp_weapon_lmg.nut`：`FireWeaponBullet`；只有 mod `smart_lock_dev` 才走智能弹、命中后标记目标 10 s。这个 mod 不在 `wpn-mods.tsv` 的 lmg 列表里 | 27500 / 1.4 / 0.0033 | |
| 穿透 `pass_through_depth` / `_damage_preserved_scale` | 32 / 0.5 | 0 / 1（DSF） | |
| 换弹 · 分段 | 2.8 / 3.33；1.8；2.33 / 1.23 | 3.4 / 4.2；2.4；3 / 1.83（AMD） | 比例不一样 |
| 开镜 · `ads_fov_zoomfrac_start / end` | 0.3 / 0.3 · 30 · 0.2 / 1.0 | 0.34 / 0.3 · 55 · 0 / 1 | |
| 散布 腰 / 镜 | 1.5 / 0（空中 5） | 3 / 0 | |
| 散布增长 · 上限 · 回落 | 1.5 · 7.0 · 15 / 0.2 | 0.25（AMD）· R5 表里没有 · 12 / 0.3 | |
| 后坐 | −1 ± 0.65，0 ± 0.92 | 1 ± 1，1 ± 1（AMD） | |
| 分配 | 0.2 / 1；0.0 / 0.05 | 0.3 / 2.9；0.2 / 0（FIT） | |
| 倍率 | 腰 1，镜 0.3–1.5；空中 3.0；蹲 0.8 | 空中 1 · 蹲 0.9 · 第一发 1 | |

### 3.11 L-STAR → L-STAR（值得一页）

| 项（键） | TF2 L-STAR | R5 L-STAR | 备注 |
|---|---|---|---|
| 开火 | auto · 12.0（83 ms，算） | 0 · 10（100 ms，算）；DEXT 实测 10.11 | |
| 弹药 | `ammo_clip_size` 35，`ammo_clip_reload_max` 35；停火 `regen_ammo_refill_start_delay` 0.2 s 后每秒回 `regen_ammo_refill_rate` 9 发 | `ammo_clip_size` 0 | **TF2 是弹匣自己回** |
| 过热 | 打空后 `empty_reload_only` 1：只能空仓换弹，`reloadempty_time` 6.03（`.nut` 叫 LensBurnout）；`ammo_min_to_fire` 9（剩 9 发时脚本播警告音）；`chance_for_bonus_last_shot_in_clip` 0.75；`cooldown_time` 0.6 | `charge_time` 2.2，`charge_cooldown_time` 1.19，`charge_cooldown_delay` 0.08，`charge_overheat_cooldown_time` 3.63（late1–3 2.55 / 2.07 / 1.16），`cooldown_time` 0.16（全 AMD）；`reload_time / reloadempty_time` 3.26 / 3.26 | **R5 是蓄力热量**；两边都没测曲线（DEXT §1） |
| 分段 | `reloadempty_time_late1–5` 4.7 / 3.5 / 2.5 / 1.43 / 0.56；没有 `reload_time` | R5 表里没有 | |
| 伤害 | 25 / 18（没有 very_far） | 19 / 19 / 19（AMD） | |
| 距离 | 1800 / 2000 | 1500 / 2500 | |
| 爆头 | 1.5（1800） | 1.25 / 腿 0.85 | |
| 泰坦 | 85 / 65 | 19 / 19（AMD） | |
| 弹道 | txt `projectile_launch_speed` 3500、`projectile_gravity_scale` 0.1；`.nut` 用 `FireGenericBoltWithDrop`，速度参数写 1（`PROJ_SPEED_SCALE`），`bolt.kv.gravity` = 1 | 24000 / 0.5 / 0 | **实际弹速没定**（第 4 节） |
| 爆炸 | `explosion_damage` 30，`explosion_inner_radius` 24，`explosionradius` 0，`explosion_damages_owner` 1 | R5 表里没有 | |
| 穿透 | 没有键 | 64 / 0.6（DSF） | |
| 命中体积 `bolt_hitsize_growfinal_size` | 7.0（0.18 s） | 0.4（DSF） | |
| 开镜 | 0.3 / 0.3 · 35 | 0.34 / 0.3 · 55 | |
| 散布 腰 / 镜 | 1 / 1（所有姿态 1，空中、跑墙 3） | 2.5 / 0 | TF2 开镜不收 |
| 后坐 | **+0.25** ± 0.10，0 ± 0.6；过热时 `cooldown_viewkick_pitch_base` 5.0 | 1.2 ± 1，1.1 ± 1（AMD） | TF2 符号和别的枪相反 |
| 分配 | 0.1 / 1.0；0.8 / 0.4 | 0.4 / 2.8；0.2 / 0.1（FIT） | TF2 后坐大部分进枪模 |
| 彩蛋 | `.nut` `CheckForRCEE`：掏枪时换弹停在第 4 段、又按住近战 + 蹲 + 跳，就加 mod `rcee` | — | 不做 |

### 3.12 Devotion → Devotion

| 项（键） | TF2 Devotion（`esaw`） | R5 Devotion | 备注 |
|---|---|---|---|
| 加速 `fire_rate` → `fire_rate_max` · `fire_rate_max_time_speedup` · `_time_cooldown` | 5 → 15 · 1.75 s · 0（200 → 67 ms，算） | 5 → 15 · 1.5 s（DEXT §1；1.5 也在 AMD）；实测间隔 0.203 → 0.062 s | 同一机制 |
| 弹匣 | 55 | 36 | |
| 伤害 | 25 / 20 / 15 | 16 / 16 / 16（AMD） | |
| 距离 | 1500 / 1800 / 2200 | 1500 / 2500 | |
| 爆头 | 1.5（1800） | 1.25 / 腿 0.85 | |
| 泰坦 | 80 / 60 | 16 / 16（AMD） | |
| 命中 | `OnWeaponPrimaryAttack_lmg`（同 Spitfire），即时（推断） | 33500 / 1.4 / 0 | |
| 穿透 | 32 / 0.5 | 0 / 1（DSF） | |
| 换弹 · 分段 | 2.8 / 3.63；1.8；2.63 / 1.20 | 3.2 / 4.1；2.1；2.83 / 1.43（AMD） | |
| 开镜 | 0.3 / 0.3 · 30 · zoomfrac 0.2 / 1.0 | 0.34 / 0.3 · 55 · 0 / 1 | |
| 散布 腰 / 镜 | 2.0 / 0.4（空中腰 5.0，镜蹲 0.2、空中 0.5），不随开火增长 | 2.5 / 0.1；增长 0.25（AMD） | |
| 回落 | 25 / 0.2 | 20 / 0.3 | |
| 后坐 | −0.17 ± 0.36，0 ± 0.6 | 1 ± 1，1 ± 1（AMD） | |
| 分配 | 0.35 / 1.4；0.65 / 0.1 | 0.45 / 1.8；0.2 / 0（FIT） | |
| 倍率 | 腰 min 3 / max 1.0、镜 1.0 / 0.5：按 RV §10.1 的公式是越打越小（推断 TF2 同一公式）；空中 2.0，蹲 0.8 | 空中 1 · 蹲 0.8 · 第一发 1 | |

### 3.13 Kraber → Kraber

| 项（键） | TF2 Kraber（`sniper`） | R5 Kraber | 备注 |
|---|---|---|---|
| 开火 `fire_rate` · `rechamber_time` | semi-auto · 1.85（541 ms，算）· 1.60 | 1 · 1.2（833 ms，算）· 1.6 | 两个时间怎么合成没查；R5 射速没测到（DEXT §1） |
| 弹匣 | 4 | 4 | |
| 伤害 | **350 / 350** | 150 / 150 / 150（AMD） | |
| 距离 | 2000 / 15000 | 7500 / 10000 | |
| 爆头 | 1.5 | 1.4 / 腿 0.8 | |
| 泰坦 | 430 / 430 | 150 / 150（AMD） | |
| 弹道 | `bolt_speed` **10000**，`bolt_gravity_amount` 0.25（`.nut` 写进 `bolt.kv.gravity`） | 29500 / 1.4 / 0.0033 | 1500 u 飞行 0.15 s 对 0.051 s（算）；重力基准不同，没比 |
| 穿透 · 跳弹 | 64 / 1；`projectile_ricochet_max_count` 0；mod `ricochet` 改成 2 次、`bolt_bounce_frac` 0.7 | 64 / 0.8，`bolt_bounce_frac` 0.44（DSF）；跳弹次数 R5 表里没有 | |
| 换弹 · 分段 | 2.5 / 3.61；1.52 / 0.63；2.63 / 1.75 / 0.55 | 3.2 / 4.3；1.95 / 1.95；3.13 / 2.08 / 0.65（AMD） | 比例一样，R5 `late2` 可疑 |
| 开镜 · zoomfrac | 0.4 / 0.3 · 26.26 · 0.5 / 0.9；`zoom_scope_frac` 0.2 / 0.7 | 0.58 / 0.55 · 13.3128 · 0.6 / 0.85 | |
| 散布 腰 / 镜 | 10 / 0（跑 12，蹲 8，空中 12） | 8 / 0 | |
| 后坐 | −0.5625 ± 0.0225，−0.135 ± 0.045 | R5 表里没有 | |
| 分配 | 2 / 0.8；0.4 / 0.0 | 0.9 / 1；0.2 / **0.75**（FIT） | R5 开镜后坐 75 % 进枪模 |

### 3.14 Longbow → Longbow

| 项（键） | TF2 Longbow（`dmr`） | R5 Longbow | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 3.0（333 ms，算） | 1 · 1.3（769 ms，算） | TF2 快一倍多 |
| 弹匣 | 6 | 6 | |
| 伤害 | 55 / 55 | 60 / 60 / 60（AMD） | |
| 距离 | 4500 / 4500 | 7500 / 10000 | |
| 爆头 | 2.0 | 1.8 / 腿 0.8 | |
| 泰坦 | 430 / 430 | 60 / 60（AMD） | |
| 命中 | `mp_weapon_dmr.nut` 第 81–119 行开火函数整段注释掉（里面原来是 15000 u/s 的弹体）→ 引擎默认，即时（推断） | 31000 / 1.3 / 0 | |
| 穿透 | 32 / 1.0 | 32 / 0.8（DSF） | |
| 换弹 · 分段 | 2.66 / 3.66；1.23；2.25 / 1.26 | 2.66 / 3.66；1.23；2.25 / 1.26（AMD） | **完全一样** |
| 开镜 · zoomfrac | 0.4 / 0.3 · 30 · 0.5 / 0.9；`zoom_scope_frac` 0.2 / 1.0 | 0.31 / 0.28 · 55 · 0 / 1 | |
| 散布 腰 / 镜 | 8 / 0.05（跑 10，蹲 6，空中 10；空中开镜 0.15） | 8 / 0 | |
| 后坐 | −0.61 ± 0.12，−0.5 ± 0.14；永久 −0.47 ± 0.23 | −0.9 ± 0.35，−0.4675 ± 0.28（AMD） | 两边都是度数，可以比 |
| 分配 | 0.9 / 1.2；0.4 / 0.0 | 0.9 / 1；0.2 / 0（FIT） | |

### 3.15 EVA-8 → EVA-8（值得一页）

| 项（键） | TF2 EVA-8（`shotgun`） | R5 EVA-8 | 备注 |
|---|---|---|---|
| 开火 | auto · 2.75（364 ms，算） | 0 · 2.8（357 ms，算） | 两边都按住连发（DEXT §1） |
| 弹匣 | 6 | 8 | |
| **怎么打** | `mp_weapon_shotgun.nut` → `ShotgunBlast(…, 8, …)`（`_weapon_utility.nut:489`）：在锥形里找可见目标（`FindVisibleEntitiesInCone`），**每个目标吃一次伤害**，最多 8 个目标；剩下的"弹丸"用 `FireWeaponBullet_Special` 打出去 | 8 颗弹丸（SR §2 读 `GetProjectilesPerShot`），固定图案，脚本不看散布字段（SR §6） | 两套完全不同 |
| 锥形 / 图案大小 | 半角 = `GetAttackSpreadAngle` × 0.5；散布 8 → 4°（算，假定读回的就是 txt 的 8）；搜索用 × 1.1 | 腰射图案最外颗在 300 u 处 9.023 u → 1.72°（SCAT，算） | |
| 伤害 | `damage_near_value` **200**（`near_distance` 100）→ `far_value` 10（`far_distance` 750）；`damage_falloff_type` inverse，`damage_inverse_distance` 100；不是实心命中时距离 +130（`.nut:586`） | 每颗 7（GUN-VARS 7 / 7；DEXT §2 实测 7） | 曲线公式在引擎里，没查 |
| 最大伤害 | 一个目标一次：200（≤ 100 u） | 8 × 7 = 56（算） | |
| 爆头 | 1.25（`headshot_distance` 500）；ShotgunBlast 里算不算爆头没查 | 1 / 腿 1；`allow_headshots` 0（SR §2） | |
| 泰坦 | 300 / 10 | 7 / 7（AMD） | |
| 弹道 | 没有弹体 | 16000 / 1 / 0.001；`bolt_hitsize` 0.4 → 1（DSF） | |
| 换弹 · 分段 | 2.75 / 3.0；1.45 / 0.25；2 / 1 / 0.8 | 2.3 / 2.5；1.15 / 0.2；1.6 / 0.8 / 0.65（AMD） | |
| 开镜 · 移速 | 0.25 / 0.2 · 50 · 0.5 | 0.22 / 0.2 · 60 · 0.9 | |
| 散布 | **所有姿态都是 8**（腰、镜、跑、冲刺、蹲、空中、跑墙、挂墙）→ 开镜锥形不收 | 1.2 / 1.2，但脚本不用；`spread_decay_rate` 500 | |
| 后坐 | −1.75 ± 0.75，−0.65 ± 0.38；永久 −0.5 ± 1.1，偏航 0 ± 1.5 | −0.8 ± 0.5，−0.5 ± 0.3（AMD） | |
| 分配 | 1.5 / 0.3；0.1 / 0.35 | 1 / 0.3；0.1 / 0.35（FIT） | fraction 一样 |

### 3.16 Mastiff → Mastiff（值得一页，和 3.21 合并）

| 项（键） | TF2 Mastiff | R5 Mastiff | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 1.3（769 ms，算） | 1 · 1.1（909 ms，算） | |
| 弹匣 | 4 | 5 | |
| 弹丸 | `mp_weapon_mastiff.nut`：**8 颗**（`MASTIFF_MAX_BOLTS`，注释说是代码每帧上限），一字横排，右偏移 ±0.15 / ±0.3 / ±0.6 / ±1.2 × spreadFrac | 5 颗（SR §2），一字横排（SCAT） | |
| 图案宽度 | spreadFrac 按开镜比例 0.05 → 0.025：最外颗腰 3.43°、镜 1.72°（算，atan(1.2 × frac)） | 300 u 处最外颗腰 9.844 u → 1.88°，镜 7.875 u → 1.50°（SCAT，算） | TF2 腰射宽将近一倍 |
| 弹速 · 重力 | 脚本写死 **3000**，`bolt.kv.gravity` 0.09 | 16000 / 1 / 0.001 | 300 u 飞行 0.10 s 对 0.019 s（算） |
| 寿命 | `SetProjectileLifetime` 0.65–0.85 s 随机，开镜 > 0.8 时 × 1.25 → 射程 1950–2550 u，开镜 2438–3188 u（算） | R5 表里没有 | **TF2 有射程上限** |
| 伤害（每颗） | 20 / 12（near 350，far 750） | 19 / 19（near 450，far 850）；DEXT §2：头腿都 19 | |
| 最大伤害 | 8 × 20 = 160（算） | 5 × 19 = 95（算） | |
| 爆头 | 1.5（800） | 1 / 腿 1 | |
| 泰坦 | 33 / 10 | 19 / 19（AMD） | |
| 命中体积 | `bolt_hitsize` 0.5 → 5 → 10（0.025 / 0.18 s） | 0.4 → 0.6 → 1（DSF） | |
| 爆炸 | `explosionradius` 32，`explosion_inner_radius` 16，没有 `explosion_damage` | R5 表里没有 | 用途没查 |
| 换弹 | 按发：`reload_is_segmented` 1，`ammo_size_segmented_reload` 1，`reloadsegment_time_loop` 0.53，`_end` 0.67，`reloadsegmentempty_time_end` 0.67；`reload_time / reloadempty_time` 1.03 / 2.2 | 按发：字段 0.9 / 1.6；实测装 1 发 1.86 s、装 5 发 3.742 s（CRS） | |
| 开镜 | 0.25 / 0.2 · 50 | 0.22 / 0.2 · 60 | |
| 后坐 | −1.25 ± 1，−0.35 ± 0.5 | −1.25 ± 1，−0.35 ± 0.5（AMD） | **完全一样** |
| 分配 | 0.5 / 1.4；0.1 / 1.0；弹簧 `rspn101` | 2.5 / 1.4；0.1 / 0.1（FIT） | |

### 3.17 RE-45 → RE-45

| 项（键） | TF2 RE-45（`autopistol`） | R5 RE-45 | 备注 |
|---|---|---|---|
| 开火 | auto · 13（77 ms，算） | 0 · 13 | 一样 |
| 弹匣 | 20 | 20 | 一样 |
| 伤害 | 20 / 13 / 9 | 14 / 14 / 14（AMD） | |
| 距离 | 750 / 1000 / 2000 | 700 / 1200 | |
| 爆头 | 1.5（1000） | 1.25 / 腿 0.9 | |
| 泰坦 | 60 / 30 | 14 / 14（AMD） | |
| 命中 | 即时（推断）；`explosionradius` 250，没有 `explosion_damage` | 19500 / 1 / 0.0025 | |
| 换弹 · 分段 | 1.74 / 2.12；1 / 0.65；1.58 / 1.06 / 0.74 | 1.5 / 1.95；1.2 / 0.65；1.58 / 1.06 / 0.74（AMD） | 空仓分段绝对值一样 |
| 开镜 | 0.2 / 0.15 · **70** | 0.18 / 0.16 · 60 | |
| 散布 腰 / 镜 | 3 / 0（跑 4，冲刺 5，蹲 2.5，空中 7）；开镜每发 +0.15 | 3 / 0 | |
| 散布增长 · 上限 · 回落 | 0.4 · 4.0 · 12 / 0.1 | 0.3（AMD）· R5 表里没有 · 2.5 / 0.07 | |
| 后坐 | −0.34 ± 0.43，0.15 ± −0.43 | 1 ± 1，1 ± 1（AMD） | |
| 分配 | 0.7 / 1.5；0.5 / 0.0 | 0.2 / 1.8；0.15 / 0（FIT） | |

### 3.18 P2016 → P2020

| 项（键） | TF2 P2016（`semipistol`） | R5 P2020 | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 8（125 ms，算） | 1 · 7（143 ms，算） | |
| 弹匣 | 12 | 9 | |
| 伤害 | 30 / 20 / 15 | 24 / 24 / 24（AMD） | |
| 距离 | 750 / 1000 / 2000 | 700 / 1200 | |
| 爆头 | **2**（1000） | 1.25 / 腿 0.9 | |
| 泰坦 | 100 / 70 | 24 / 24（AMD） | |
| 命中 | 即时（推断）；`explosionradius` 250，没有 `explosion_damage` | 18500 / 1 / 0.0025 | |
| 换弹 · 分段 | 1.25 / 1.25；1；1 | 1.25 / 1.25；1；1（AMD） | **完全一样** |
| 开镜 | 0.2 / 0.15 · **70**；`zoom_fov_viewmodel` 0 | 0.18 / 0.16 · 60 | |
| 散布 腰 / 镜 | 2.5 / 0（跑 3.5，冲刺 4.5，蹲 2，空中 6.5） | 4.4 / 0 | |
| 散布增长 · 上限 · 回落 | 0.4 · 3.5 · 12 / 0.17 | 0（AMD）· R5 表里没有 · 2.5 / 0.07 | |
| 后坐 | −0.85 ± −0.5，0.1 ± 0.8；永久 0.1 ± 0.8，偏航 0.1 ± 0.4 | −0.95 ± −0.12，0.2 ± 0.5（AMD） | 都是度数 |
| 分配 | 0.9 / 1.0；0.5 / 0.0 | 0.5 / 0.5；0 / 0.2（FIT） | |

### 3.19 B3 Wingman → Wingman

| 项（键） | TF2 B3 Wingman | R5 Wingman | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 2.6（385 ms，算） | 1 · 2.8（357 ms，算） | |
| 弹匣 | 6 | 5 | |
| 伤害 | 40 / 40 / 30 | 50 / 50 / 50（AMD） | TF2 到 1500 u 不降 |
| 距离 | 1000 / 1500 / 2500 | 800 / 1300 | |
| 爆头 | **2.0**（1400） | 1.5 / 腿 0.9 | |
| 泰坦 | 250 / 200 | 50 / 50（AMD） | |
| 命中 | 即时（推断）；`impulse_force` 3000 | 18000 / 1.2 / 0.0025 | |
| 换弹 · 分段 | 2.1 / 2.1；1.75 / 0.60；1.75 / 0.65 | 2.1 / 2.1；1.75 / 0.6；1.75 / 0.65（AMD） | **完全一样** |
| 开镜 | 0.2 / 0.15 · 55 | 0.18 / 0.16 · 60 | |
| 散布 腰 / 镜 | 1.0 / 0（跑 3，冲刺 4，蹲 0.5，空中 6） | 2.4 / 0 | |
| 散布增长 · 上限 · 回落 | 2.5 · 4.5 · 11 / 0.21 | 2.5（AMD）· R5 表里没有 · 11 / 0.26 | 增长、回落速率一样，延迟不同 |
| 后坐 | −2.5 ± 1，−0.5 ± −1.0；永久 0 ± 1.0，偏航 0.1 ± 1.0 | −4.4 ± 0.8，−0.6 ± −0.5（AMD） | 都是度数 |
| 分配 | 2.0 / 0.4；0.25 / 0.35；弹簧 `magnum` | 0.35 / 0.65；0.4 / 0.3（FIT） | |

### 3.20 Wingman Elite → Wingman（也许）

只写和 3.19（TF2 B3 Wingman）不同的键。射速 2.6、弹匣 6、换弹、开镜时间都一样。

| 项（键） | TF2 Wingman Elite（`wingman_n`） | 对照 | 备注 |
|---|---|---|---|
| 命中 | `OnWeaponPrimaryAttack_weapon_sniper`（和 Kraber 同一个函数），`bolt_speed` 12000，`bolt_gravity_amount` 0.25 | B3 即时（推断）；R5 18000 / 1.2 | |
| 伤害 · 距离 | 75 / 55 / 35 · 1500 / 2000 / 3500 | B3 40 / 40 / 30；R5 50 | |
| 泰坦 | 300 / 250 | B3 250 / 200 | |
| 散布 | **所有姿态、所有开火增长都是 0** | B3 腰 1.0；R5 2.4 | |
| 穿透 · 跳弹 | 32 / 1；mod `ricochet` 2 次、`bolt_bounce_frac` 0.7 | R5 Wingman 穿透 0（DSF） | |
| 后坐 | −0.5 ± 0.2，0.05 ± 0；没有永久后坐 | B3 −2.5 ± 1 | |
| 开镜 `zoom_fov` | 35 | B3 55；R5 60 | |
| 其他 | `impulse_force` 10，没有 `headshot_distance` | B3 3000 | |

### 3.21 Mozambique → Mozambique（值得一页，和 3.16 合并）

| 项（键） | TF2 Mozambique（`shotgun_pistol`） | R5 Mozambique | 备注 |
|---|---|---|---|
| 开火 | auto · 3.0（333 ms，算） | 0 · 2.8（357 ms，算） | 两边按住连发 |
| 弹匣 | 6 | 5 | |
| 弹丸 | `mp_weapon_shotgun_pistol.nut`：3 颗，偏移（上 −0.2，右 ±0.4）两颗 + 中心一颗，× spreadFrac 0.05 → 0.025 | 3 颗（SR §2）；300 u 处上方 (0, 2.93)，左下 / 右下 (±3.516, −3.809)（SCAT） | 形状不同：TF2 中心 + 两颗在下，R5 上一颗 + 下两颗 |
| 图案大小 | 下方两颗离中心腰 1.28°、镜 0.64°（算） | 下方两颗腰 0.99°（SCAT，算） | |
| 弹速 · 重力 · 寿命 | 3000，`kv.gravity` 0.09；0.5–0.75 s 后删掉（开镜 > 0.8 × 1.25）→ 射程 1500–2250 u，开镜 1875–2813 u（算） | 10000 / 1 / 0.0025；寿命 R5 表里没有 | |
| 伤害（每颗） | 30 / 25（750 / 1000） | 17 / 17 / 17（500 / 1000；very_far 取 AMD） | |
| 最大伤害 | 3 × 30 = 90（算） | 3 × 17 = 51（算） | |
| 爆头 | 1.5（1400） | 1.25 / 腿 1 | |
| 泰坦 | 30 / 20 | 17 / 17（AMD） | |
| 命中体积 · 爆炸 | `bolt_hitsize` 0.5 → 7.5；`explosionradius` 32 / inner 16，没有伤害键 | `growfinal_size` 7.5（DSF） | |
| 换弹 · 分段 | 2.1 / 2.1；1.05；1.05 | 1.9 / 2.3；0.95；2（AMD） | |
| 开镜 | 0.2 / 0.15 · 55 | 0.2 / 0.18 · 60 | |
| 散布 | 0（脚本只用固定偏移） | 2 / 2，脚本不用（SR §6） | |
| 后坐 | −2.25 ± 1，−0.95 ± 0.5 | −1.25 ± 0.5，−0.5 ± 0.25（AMD） | |
| 分配 | 0.5 / 1.4；0.1 / 1.0 | 0.5 / 1.4；0.1 / 0.1（FIT） | hard / soft 一样 |
| 其他 | mod `arc_net`：弹之间连电弧，弹不删 | — | |

### 3.22 Charge Rifle → Charge Rifle（也许）

| 项（键） | TF2 Charge Rifle（`defender`） | R5 Charge Rifle | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 1（1000 ms，算）；`bypass_semiauto_hold_protection` 1 | 1 · 1.3（769 ms，算）；射速没测到（DEXT §1） | |
| 蓄力 | `charge_time` 1.3；`.nut`：蓄力比例 < 1 就不开火（返回 0）；`charge_end_forces_fire` 0（蓄满不自动打）；`charge_cooldown_time` 1.0，`_delay` 0 | `charge_time` 0.85，`charge_cooldown_time` 1.1，`_delay` 0.1，`charge_cooldown_time_post_fire` 0.6（AMD）；曲线没测（DEXT §1） | |
| 弹药 | **`ammo_clip_size` 0，`reload_enabled` 0**；`ammo_default_total` / `ammo_stockpile_max` 20；`reload_time` 3.5 留着但不用 | 6 发；3.5 / 4.6，实测 3.593 / 4.65（CRS） | |
| 伤害 | 300 / 300（4800 / 5300） | **75 → 99，越远越高**（2953 / 7874） | |
| 爆头 | `allow_headshots` 0；`critical_hit_damage_scale` 1.25 | 1.8 / 腿 0.9 | |
| 泰坦 | 1025 / 725；`damage_heavyarmor_nontitan_scale` 0.5 | 75 / 99（AMD） | |
| 命中 | `.nut`：`FireWeaponBullet`，伤害标记 `DF_GIB \| DF_EXPLOSION` → 即时（推断） | 33999 / 1.15 / 0；`bolt_hitsize` 0.5 → 3.25（DSF） | |
| 穿透 | 96 / 0.5 | 20000 / 0.8（DSF） | |
| 开镜 | 0.2 / 0.15 · 45；`trigger_snipercam` 1 | 0.2 / 0.15 · 55 · zoomfrac 0.25 / 0.75 | |
| 散布 腰 / 镜 | 3.0 / 0.35（空中开镜 0.5） | 2.25 / 0 | |
| 后坐 | −1 ± 1.5，0 ± 0.5；腰射和开镜都有 view drift（`viewdrift_hipfire_*`、`viewdrift_ads_*`） | `viewkick_pitch_random` 0.5（AMD），其余 R5 表里没有 | |
| 分配 | hard 3 / soft 0；0.5 / 0.6；弹簧 `titan_arc` | 2 / 0.3；0.5 / 0.6（FIT） | fraction 一样 |

### 3.23 Double Take → Triple Take（远亲，也许）

| 项（键） | TF2 Double Take（`doubletake`） | R5 Triple Take | 备注 |
|---|---|---|---|
| 开火 | semi-auto · 2.0（500 ms，算） | 1 · 1.3（769 ms，算） | |
| 弹药 | `ammo_clip_size` 12，`ammo_per_shot` 2，`ammo_min_to_fire` 2，`.nut` 返回 2 → 每匣 6 发（算） | 6，`ammo_per_shot` 1 | |
| 弹丸 | `projectiles_per_shot` 3；`.nut`：右偏移 −0.25 / +0.25 / 0，一字横排；中心那颗特效减弱、不跳弹 | 3 颗（SR §2）；排法 R5 表里没有 | |
| 弹丸间距 | spreadFrac = `bolt_spread_max` 0.015 → `bolt_spread_min` 0.015，**开镜不变**；两边颗离中心 0.21°（算） | 默认不收；mod `choke` 加 `charge_levels` 4、`charge_time` 0.85（AMD）= 蓄力收束 | |
| 弹速 · 重力 | `bolt_speed` 10000，`bolt_gravity_amount` 0.09 | 31000 / 1.4 / 0 | |
| 伤害（每颗） | 30 / 30（4500 / 15000）；最多 90（算） | 22 / 22（1000 / 2500）；最多 66（算） | |
| 爆头 | 2.0 | 1.5 / 腿 0.9 | |
| 泰坦 | 165 / 165 | 22 / 22（AMD） | |
| 穿透 · 跳弹 | 32 / 1.0；mod `ricochet` 2 次 | 0 / 0.65，`bolt_bounce_frac` 0.44（DSF） | |
| 换弹 · 分段 | 2.4 / 3.4；1.26；2.26 / 1.26 | 2.6 / 3.4；1.32；2.26 / 1.26（AMD） | 空仓一样 |
| 开镜 · zoomfrac | 0.4 / 0.3 · 26.26 · 0.0 / 0.6；`zoom_scope_frac` 0.2 / 1.0 | 0.3 / 0.26 · 55 · 0.2 / 0.9 | |
| 散布 腰 / 镜 | 8 / 0（蹲 6，挂墙 11.75）；腰每发 +4 到 18 | 2.5 / 0；回落 10 / 0.1 | 腰射散布是否加在弹丸方向上没查 |
| 后坐 | −0.61 ± 0.12，0.05 ± 0.14；永久 −0.47 ± 0.23 | R5 表里没有 | |
| 分配 | 0.9 / 1.2；0.4 / 0.0；弹簧 `semisniper` | 0.9 / 1.2；0.2 / 0（FIT） | hard / soft 一样 |

## 4. 没解决的

1. **TF2 FOV 基准**：游戏里没查。只有 `mp_weapon_sniper.txt:219` 的 `//3x zoom` 指向 70°。另：`TF2-Research/expansion/titan/T0-REPORT.md` 算开镜灵敏度用的是 tan(zoom_fov / 2) ÷ tan(75 / 2)，那是灵敏度，不是 FOV 基准。
2. **即时命中**：没有开火脚本的 TF2 枪、调 `FireWeaponBullet` 的枪是不是即时命中，文件没写，是推断。
3. **重力单位**：TF2 `bolt.kv.gravity`（0.25、0.09）和 R5 `projectile_gravity_scale`（DEXT §3 公式里 × 750）是不是同一个基准，没查。
4. **L-STAR 弹速**：txt 3500 / 重力 0.1，脚本传速度参数 1、重力设 1，互相打架。`explosion_damage` 30 配 `explosionradius` 0 的意思也没查。
5. **EVA-8**：`damage_falloff_type inverse` 的公式在引擎里；`ShotgunBlast` 最后那次 `FireWeaponBullet_Special`（打剩下的弹丸）会不会造成伤害，参数含义没查；爆头算不算没查；锥形半角 4° 假定 `GetAttackSpreadAngle` 读回 8。
6. **`headshot_distance`**（18 把）：脚本没用到，含义没查。
7. **`viewkick_perm_*`**：按名字推断是不回弹的后坐，没查。
8. **Kraber**：`fire_rate` 1.85 和 `rechamber_time` 1.6 怎么合成实际间隔，没查（R5 也没测到）。
9. **TF2 Charge Rifle**：没有 `ammo_per_shot` 键，每发扣几颗、20 发打完怎么办，没查。
10. **Double Take**：腰射散布 8 是否先加在 `attackParams.dir` 上，再加固定偏移，没查。
11. **`explosionradius`**：RE-45、P2016 是 250，Mastiff、Mozambique 是 32，都没有 `explosion_damage`，用途没查。
12. **R5 L-STAR**：`reload_time` 3.26 和 `charge_overheat_cooldown_time` 3.63 哪个是真的过热锁定，R5 没有实测（CRS 4 次 0 次成功）。
13. **TF2 L-STAR** `viewkick_pitch_base` +0.25，符号和别的枪相反，方向没查。
14. R5 CAR、Kraber、Triple Take、Charge Rifle 的 `viewkick_*_base` 在 R5 表里没有；R5 Mastiff、Mozambique、Double Take 弹丸寿命在 R5 表里没有。
15. `reload_time_late*` 的含义别处在查；这里只发现多数对的比例和 TF2 相同，Flatline、Volt、Spitfire、RE-45 不同。

**输入里看着不对的**：

- `GUN-VARS.tsv` 的表头有两列 `rechamber_time`（第 7 列和第 27 列）。
- `GUN-VARS.tsv` 的 `fire_mode` 31 把枪全是 0，半自动枪也是 0；真正区分的是 `is_semi_auto`。
- `A-MOD-DIFFS.tsv` 的 Kraber `reload_time_late1` 和 `late2` 都是 1.95。其他分段和 TF2 比例对得上，只有这一个对不上（TF2 是 0.63，比例 0.252），可能是读错或抄错。
- TF2 R-201 的 mod `pas_fast_reload` 只把 4 个键 × 0.7，没改 `reloadempty_time_late2`（原始 txt 第 565 行起也是这样，不是提取的问题）。
