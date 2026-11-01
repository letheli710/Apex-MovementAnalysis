# W1 · 武器阶段第一波汇总（静态）

会话 wp1，2026-11-01。全部是静态研究：读脚本、武器数据、SDK 源码，搜二进制字符串。**没进游戏，下面所有行为结论都没有实测。** 过滤见 [W0-WEAPON-FILTER](../W0-WEAPON-FILTER.md)（Leader 草稿，等用户看）。

## 1. 记录索引

| 记录 | 内容 |
|---|---|
| [auto-ballistic](auto-ballistic/SYSTEM.md) | R-301、R-99、C.A.R.、Flatline、Spitfire、Alternator、RE-45、Volt、P2020 |
| [burst-fire](burst-fire/SYSTEM.md) | Hemlok、Hemlok Elite、Prowler、Nemesis |
| [shotgun-blast](shotgun-blast/SYSTEM.md) | EVA-8、Mastiff、Peacekeeper、Mozambique、Triple Take |
| [sniper-marksman](sniper-marksman/SYSTEM.md) | Kraber、Longbow、Sentinel、G7、Wingman、Charge Rifle |
| [charge-spinup](charge-spinup/SYSTEM.md) | Havoc、Devotion、Rampage、L-STAR、30-30、Bocek |
| [special-energy](special-energy/SYSTEM.md) | Buster、Ray Gun、Instagib、EPG、Gauntlet、Arc、Defender Sustained |
| [melee](melee/SYSTEM.md) | 拳头、传家宝、Titan Sword、Power Sword |
| [rampart-sheila-weapon](rampart-sheila-weapon/SYSTEM.md)、[vantage-sniper-weapon](vantage-sniper-weapon/SYSTEM.md)、[ballistic-sling](ballistic-sling/SYSTEM.md) | 从技能阶段移来的武器部分 |
| [npc-weapons](npc-weapons/SYSTEM.md) | 敌人开火节奏和命中率 |
| [hopups](hopups/SYSTEM.md)、[attachments](attachments/SYSTEM.md)、[ammo](ammo/SYSTEM.md)、[weapon-tiers](weapon-tiers/SYSTEM.md) | 模块、配件、弹药、档位 |
| `_shared/` | [W-BALLISTICS](_shared/W-BALLISTICS.md)、[W-SPREAD-RECOIL](_shared/W-SPREAD-RECOIL.md)、[W-DAMAGE](_shared/W-DAMAGE.md)、[W-FIRE-RELOAD](_shared/W-FIRE-RELOAD.md)、[W-MOD-SYSTEM](_shared/W-MOD-SYSTEM.md)、[W-S3-FIELD-CHECK](_shared/W-S3-FIELD-CHECK.md)、[W-PARAM-COMPARE](_shared/W-PARAM-COMPARE.md) |
| `<族>/PARAMS.md` | 每把枪的玩法字段 + 行号（`_tools/gen-params.mjs` 生成） |

## 2. 主要发现

### 2.1 武器系统

1. **几乎全是弹道子弹。** 写了 `ballistic_type hitscan` 的只有两个文件（`mp_weapon_buster_rifle.txt:58`、`mp_weapon_shotgun_pistol_energy.txt:8`）。Buster 的开火函数还是空桩（`_missing_callback_stubs.gnut:285`）。真正能用的命中扫描是 Instagib（`mp_weapon_clickweapon.nut:404`）。HSD 现在的 `TraceBullet` 是命中扫描，这是最大的差别。
2. **大部分枪没有自己的代码。** 脚本就是一句 `FireWeapon_Default`，有些枪 `.txt` 连回调都没绑（Spitfire、Alternator、Longbow、Kraber、Havoc）。`.nut` 里写的函数不一定跑：Havoc 的脚本门槛 `CanFire_EnergyAR` 就是死代码，真门槛是 `charge_attack_min_charge_required 1.0`。**读 `.nut` 必须先看 `.txt` 绑了什么。**
3. **Mods 是核心。** 配件、模式切换、增伤、换弹种都是字段覆盖（`*x`、`++x`、替换），只统计 `mp_weapon_*` 就有约 1.4 万条乘法覆盖。HSD 配件、掉落、成长都能挂在一个 mod 系统上（[W-MOD-SYSTEM](_shared/W-MOD-SYSTEM.md)）。
4. **S21 的伤害几乎不衰减。** 多数枪三段伤害相同（R-301 15 / 15 / 15）。距离的惩罚来自下坠、扩散和 `headshot_distance`（SMG 1500 u、步枪 11828 u、狙击 29528 u）。例外：Charge Rifle 越远越高，霰弹两段，补给箱版真衰减。
5. **NPC 打不了爆头**（`sh_damage_utility.gnut` `IsValidHeadShot`：攻击者不是玩家返回否）。PvE 敌人伤害不用管爆头。
6. **霰弹全走引擎。** `FireProjectileBlastPattern` 等脚本函数没人调，图案公式对引擎路径是推断。算出的最外偏移：EVA 1.72°、Mastiff 1.88°（开镜 1.50°）、Peacekeeper 2.22°（满收拢 1.00°）。
7. **传家宝是纯外观。** 41 个 `melee_*.txt` 里 37 个和拳头（30 伤害、60 u）没有玩法差别。
8. **可借的通用部件**：热量驱动字段插值（Nemesis）、节奏射击（Sentinel）、开火回调返回 0 = 门槛不扣弹、主武器挂冷却技能（Hemlok Elite）、第三武器槽（Sling）、备弹回充、休眠 hop-up（造成伤害解锁）、NPC 点射 + 休息节奏。

### 2.2 本地构建（S21 客户端 + S3 dedi + SDK）

**这是这一波最重要的方法结论。** 武器数据文件没有差异：本地安装和 `research-src` 的玩法字段相同，只缺 21 个 `*_og.txt`。差异全在"服务端谁来执行这些字段"（[W-S3-FIELD-CHECK](_shared/W-S3-FIELD-CHECK.md)）：

| 情况 | 例子 | 含义 |
|---|---|---|
| S3 引擎原生 | `fire_rate_max*`、`damage_very_far_*`、`viewkick_pattern`、`blast_pattern` | 可以当原版看 |
| SDK 重写 | 点射计数（`bridge_burst_fire_seed`：S3 服务端自己不赋值）、热量（`weapon_heat.cpp`）、Energize（`energize.cpp`）、蓄力门槛和保持、过热冷却、128 个图案（S3 只有 8 个）、双持（`server/akimbo.cpp`） | **不是原版代码，R5 实测的是 SDK 的行为** |
| 只读入，没有使用方 | `spread_min_kick`（只用于一条警告）、分段重力、空气阻力 | 推断 dedi 不生效 |
| 只是别名 | `charge_additional_damage_multiplier` 等（`shared/weapon_script_vars.cpp:3243-3246`） | **推断 30-30 ×1.4 蓄力伤害（43 → 60.2）没生效，最可能的真差异** |
| 只读顶层 | `weapon_heat.cpp:362-377` 只读 `WeaponData` 顶层 | 推断 Nemesis 涡轮的 `heat_per_bullet 0.125`（`mp_weapon_nemesis.txt:817`）服务端不用 |
| 回调没绑 | Titan Sword 攻击回调（`mp_weapon_titan_sword.txt:21-22`）、Nemesis `OnWeaponHeatStateChanged`、C.A.R. `OnWeaponReloadFailed` | 对应逻辑不跑 |

**更正留档**：这份核对的第一版只搜了 `r5apex_ds.exe`，把 energize 和 heat 判成"推断不工作"。子任务查 `server.dll` 和 SDK 源码后推翻了。现在是"SDK 重写，待实测"。**SDK 源码提交（10077bb）和已安装的 `server.dll` 是不是同一版没有核对。**

### 2.3 Hop-up

| 状态 | 哪些 |
|---|---|
| 本地能用 | 涡轮（Havoc、Devotion）、选择射击（Prowler、Charge Rifle）、双发、Hammerpoint、Energy Choke、Skullpiercer Elite（爆头固定 95）、`corrupted_*` |
| 只内置在少数枪 | Boosted Loader、Kinetic Loader、Shield Breaker、Skullpiercer、Shatter |
| 只有数据 | Ultimate Accelerator（17 个金色行引用，无脚本）、Gunshield、Executioner、`lstar_crate`、`car_crate`、`mythicset_vinson` |
| 够不着 | Dual Loader、Quickdraw、Paintball、Highcal Rounds、`magic_pixel` |
| 金马 | 三重封死：playlist 没开、loot 行注释掉、没有 mod 块。只有蓝色的吸血代码能通过 Cupid 弓测 |

详见 [hopups](hopups/SYSTEM.md)。

## 3. 参数比较

全武器（`.txt` 同名字段，S21 数据）。点射和霰弹的名义 DPS 不能直接比；点射实际发数见 [W-FIRE-RELOAD](_shared/W-FIRE-RELOAD.md) 3.2。

| 族 | 武器 | 射速 | 近伤 | 远伤 | 极远伤 | 近距 u | 远距 u | 爆头 | 腿 | 弹匣 | 弹种 | 换弹 s | 空换 s | 弹速 u/s | 重力 | 点射 | 弹丸 | 名义 DPS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| auto-ballistic | R-301 | 13.5 | 15 | 15 | 15 | 1000 | 2500 | 1.3 | 0.75 | 21 | bullet | 2.4 | 3.2 | 29000 | 1.3 | — | — | 203 |
| auto-ballistic | R-99 | 18 | 12 | 12 | 12 | 900 | 1500 | 1.25 | 0.8 | 18 | bullet | 1.8 | 2.45 | 19000 | 1.2 | — | — | 216 |
| auto-ballistic | C.A.R. | 15.5 | 14 | 14 | 14 | 800 | 1500 | 1.25 | 0.8 | 20 | highcal | 1.7 | 2.13 | 18000 | 1.15 | — | — | 217 |
| auto-ballistic | Flatline | 10 | 20 | 20 | 20 | 1000 | 2500 | 1.3 | 0.75 | 19 | highcal | 2.4 | 3.1 | 24000 | 1.3 | — | — | 200 |
| auto-ballistic | Spitfire | 9 | 21 | 21 | 21 | 1500 | 2500 | 1.25 | 0.85 | 35 | bullet | 3.4 | 4.2 | 27500 | 1.4 | — | — | 189 |
| auto-ballistic | Alternator | 10 | 18 | 18 | 18 | 900 | 1500 | 1.25 | 0.8 | 18 | bullet | 1.9 | 2.23 | 19000 | 1.2 | — | — | 180 |
| auto-ballistic | RE-45 | 13 | 14 | 14 | 14 | 700 | 1200 | 1.25 | 0.9 | 20 | bullet | 1.5 | 1.95 | 19500 | 1 | — | — | 182 |
| auto-ballistic | RE-45 Fusion（活动） | 25 | 16 | 16 | 16 | 700 | 1200 | 1.25 | 0.9 | 15 | special | 1.9 | 2.3 | 22000 | 1.05 | 3 | — | 400 |
| auto-ballistic | Volt | 12 | 16 | 16 | 16 | 800 | 1500 | 1.25 | 0.8 | 20 | special | 2 | 2.5 | 20000 | 1.05 | — | — | 192 |
| auto-ballistic | P2020 | 7 | 24 | 24 | 24 | 700 | 1200 | 1.25 | 0.9 | 9 | bullet | 1.25 | 1.25 | 18500 | 1 | — | — | 168 |
| burst-fire | Hemlok | 15.5 | 20 | 20 | 20 | 1000 | 2500 | 1.4 | 0.75 | 21 | highcal | 2.4 | 2.85 | 27500 | 1.3 | 3 | — | 310 |
| burst-fire | Hemlok Elite（auto_hemlok） | 7.7 | 21 | 21 | 21 | 1000 | 2500 | 1.4 | 0.75 | 18 | highcal | 2.3 | 2.55 | 27500 | 1.3 | 0 | — | 162 |
| burst-fire | Prowler | 21 | 16 | 16 | 16 | 900 | 1500 | 1.25 | 0.8 | 20 | highcal | 2 | 2.6 | 18000 | 1.2 | 5 | — | 336 |
| burst-fire | Nemesis | 18 | 17 | 17 | 17 | 1000 | 2500 | 1.3 | 0.75 | 20 | special | 2.7 | 3 | 31000 | 1.15 | 4 | — | 306 |
| shotgun-blast | EVA-8 | 2.8 | 7 | 7 | — | 250 | 850 | 1 | 1 | 8 | shotgun | 2.3 | 2.5 | 16000 | 1 | — | 8 | 20 |
| shotgun-blast | Mastiff | 1.1 | 19 | 19 | — | 450 | 850 | 1 | 1 | 5 | shotgun | 0.9 | 1.6 | 16000 | 1 | — | 5 | 21 |
| shotgun-blast | Peacekeeper | 4 | 11 | 11 | — | 100 | 750 | 1 | 1 | 5 | shotgun | 2.5 | 3.5 | 20000 | 1 | — | 9 | 44 |
| shotgun-blast | Mozambique | 2.8 | 17 | 17 | 17 | 500 | 1000 | 1.25 | 1 | 5 | shotgun | 1.9 | 2.3 | 10000 | 1 | — | 3 | 48 |
| shotgun-blast | Triple Take | 1.3 | 22 | 22 | 22 | 1000 | 2500 | 1.5 | 0.9 | 6 | special | 2.6 | 3.4 | 31000 | 1.4 | — | 3 | 29 |
| sniper-marksman | Kraber | 1.2 | 150 | 150 | 150 | 7500 | 10000 | 1.4 | 0.8 | 4 | — | 3.2 | 4.3 | 29500 | 1.4 | — | — | 180 |
| sniper-marksman | Longbow | 1.3 | 60 | 60 | 60 | 7500 | 10000 | 1.8 | 0.8 | 6 | sniper | 2.66 | 3.66 | 31000 | 1.3 | — | — | 78 |
| sniper-marksman | Sentinel | 3.1 | 70 | 70 | 70 | 7500 | 10000 | 1.8 | 0.9 | 4 | sniper | 3 | 4 | 31000 | 1.4 | — | — | 217 |
| sniper-marksman | G7 Scout | 4.1 | 33 | 33 | 33 | 1000 | 2500 | 1.45 | 0.75 | 10 | bullet | 2.4 | 3 | 29000 | 1.4 | — | — | 135 |
| sniper-marksman | Wingman | 2.8 | 50 | 50 | 50 | 800 | 1300 | 1.5 | 0.9 | 5 | sniper | 2.1 | 2.1 | 18000 | 1.2 | — | — | 140 |
| sniper-marksman | Charge Rifle | 1.3 | 75 | 99 | 99 | 2953 | 7874 | 1.8 | 0.9 | 6 | sniper | 3.5 | 4.6 | 33999 | 1.15 | — | — | 98 |
| charge-spinup | Havoc | 11.2 | 20 | 20 | 20 | 1000 | 2500 | 1.3 | 0.75 | 18 | special | 3.2 | 3.2 | 30500 | 1.15 | — | — | 224 |
| charge-spinup | Devotion | 5 | 16 | 16 | 16 | 1500 | 2500 | 1.25 | 0.85 | 36 | special | 3.2 | 4.1 | 33500 | 1.4 | — | — | 80 |
| charge-spinup | Rampage | 5 | 29 | 29 | 29 | 1500 | 2500 | 1.25 | 0.85 | 28 | highcal | 3.1 | 4 | 26500 | 1.4 | — | — | 145 |
| charge-spinup | L-STAR | 10 | 19 | 19 | 19 | 1500 | 2500 | 1.25 | 0.85 | 0 | special | 3.26 | 3.26 | 24000 | 0.5 | — | — | 190 |
| charge-spinup | 30-30 Repeater | 3.85 | 43 | 43 | 43 | 1000 | 2500 | 1.4 | 0.85 | 6 | highcal | 0.33 | 0.75 | 28000 | 1.4 | — | — | 166 |
| charge-spinup | Bocek | 2.5 | 35 | 35 | 35 | 1000 | 2500 | 1.5 | 0.8 | 0 | — | 2.15 | 3 | 10000 | — | — | — | 88 |
| special-energy | Buster Rifle | 5 | 60 | 60 | 60 | 3937 | 5906 | 1.25 | 1 | 4 | — | 3.2 | 4.3 | 29500 | 1.4 | — | — | 300 |
| special-energy | Ray Gun | 3 | 90 | 90 | 90 | 800 | 1300 | 2.15 | 0.9 | 20 | highcal | 2.5 | 2.1 | 2200 | 0 | — | — | 270 |
| special-energy | Instagib | 2.8 | 50 | 50 | 50 | 800 | 1300 | 1.5 | 0.9 | 69 | sniper | 2.1 | 2.1 | 18000 | 1.2 | — | — | 140 |
| special-energy | EPG | 0.9 | 40 | 40 | — | 2000 | 2500 | 1.25 | — | 4 | special | 3.7 | 4 | 2000 | 0 | — | — | 36 |
| special-energy | EPG Tethered | 0.9 | 40 | 40 | — | 2000 | 2500 | 1.25 | — | 3 | special | 3.7 | 4 | 2000 | 0 | — | — | 36 |
| special-energy | Charge Gauntlet | 1.3 | 15 | 15 | 15 | 1970 | 11820 | — | — | 180 | — | 3.5 | 4.6 | 6000 | 0 | — | — | 20 |
| special-energy | Arc Bolt | 5 | 0 | 0 | — | 0 | 2048 | — | — | 20 | — | — | — | 1200 | 0 | — | — | 0 |
| special-energy | Arc Wave | 1 | 15 | 15 | — | — | — | — | — | 20 | — | — | — | — | — | — | — | 15 |
| special-energy | Defender Sustained | 1 | 5 | 5 | — | 7500 | 10000 | 1.8 | 0.9 | 4 | special | 2 | 2 | — | 1.4 | — | — | 5 |
| rampart-sheila-weapon | Sheila 手持 | 20 | 14 | 14 | 14 | 1500 | 2500 | 2 | 1 | 173 | — | 8.667 | 8.667 | 25000 | 1 | — | — | 280 |
| rampart-sheila-weapon | Sheila 炮台 | 20 | 14 | 14 | 14 | 1500 | 2500 | 2 | 1 | 150 | — | 8.667 | 8.667 | 25000 | 1 | — | — | 280 |
| vantage-sniper-weapon | Sniper Mark | 3 | 50 | 50 | 50 | 7500 | 10000 | 1.5 | — | 240 | — | — | — | 34000 | — | — | — | 150 |

**规律**：全自动 DPS 都挤在 170–220，配平靠弹匣和换弹。弹速分层清楚：手枪和 SMG 约 18000–20000，步枪 24000–31000，狙击约 30000。

## 4. R5 实测提案

下面只是提案，还没跑。按对 HSD 决策的价值排序。工具沿用 `research/combat/W2-RUNTIME.md` 的 runner（在 Apex-MovementAnalysis#88 分支上，这里还没有）；场景：火力训练场 `mp_rr_canyonlands_staging_mu1`，离线。

**已知限制**：本地 `npc_dummie`、`npc_prowler` 不开火，`npc_spectre` 会卡死 dedi。**NPC 开火的测试都做不了**，只能读字段（第 13 项）。

| # | 测什么 | 怎么测 | 期望 / 判据 | 为什么 | 记录 |
|---|---|---|---|---|---|
| 0 | SDK 版本 | 核对 `server.dll` 和 `s21-r5sdk` 的提交 | 同版 | 所有 SDK 结论的前提 | W-S3-FIELD-CHECK |
| 1 | 弹道 | R-301、R-99、Kraber 打 2000 / 5000 u，记落点和时间 | 公式 `0.5 g (d/v)²` + 归零 | HSD 要从命中扫描改过来，先定积分方式 | W-BALLISTICS |
| 2 | 后坐图案 | R-301 开镜连开一匣打墙，和 `rspn101_2` 比 | 四列含义和单位 | 语义全是推断 | W-SPREAD-RECOIL |
| 3 | 扩散 | R-301、R-99 腰射 / 开镜 / 跳 / 跑，每种 30 发 | 基础值、kick、回落单位 | 同上 | W-SPREAD-RECOIL |
| 4 | 伤害结算 | R-301、Charge Rifle、Kraber 打 `npc_dummie` 身 / 头 / 腿，多距离 | R-301 15 / 19.5 / 11.25；Charge Rifle 插值线性 | `damage_headshot_scale` 和 `critical_hit_damage_scale` 谁起作用 | W-DAMAGE |
| 5 | 30-30 蓄力伤害 | 开镜满档和腰射各 10 枪打 `npc_dummie` | S21 60.2 vs 43；推断本地都是 43 | 最可能的真差异 | charge-spinup |
| 6 | 点射 | Hemlok、Prowler 两组之间的时间；关 `bridge_burst_fire_seed` 对比 | 0.444 s、0.468 s | 点射靠 SDK | W-FIRE-RELOAD |
| 7 | Nemesis 热量 | 连打 30 发，每发读 `GetHeatValue`、记每组间隔；再装涡轮 | 0.31 → 0.19；涡轮推断不变 | SDK 重写 | burst-fire、hopups |
| 8 | Energize | Rampage 喂铝热：3.7 s 动画，铝热 −1，每发扣 0.74 s，射速 5 → 6.5；Sentinel 喂小电池：伤害 88，每发扣 14 s | | SDK 重写；灼烧推断没接 | charge-spinup、sniper-marksman |
| 9 | 过热 | L-STAR 按住到过热，开关 `bridge_charge_overheat_cooldown` 对比 | 锁定约 3.69 s | SDK 补 | charge-spinup |
| 10 | 转速和蓄力 | Devotion 射速曲线；Havoc 到第一发的时间（0.42 s，涡轮 0.01 s）；Bocek 4 种拉弓时长的弹速和伤害 | 满弓 26891 还是 27000 u/s | 曲线形状 | charge-spinup |
| 11 | 霰弹图案 | 512 u 平墙，EVA、Mozambique、Triple Take；Peacekeeper 按收拢档位 | EVA 最外 15.4 u | 公式是推断；第 8 个之后的图案靠 SDK | shotgun-blast |
| 12 | Sheila | 持续开火 0.3 / 0.7 / 1 / 3 s 的扩散；一匣发数 | 收紧到 0.5° 还是 0°；173 发 | `spread_min_kick` 没使用方 | rampart-sheila-weapon |
| 13 | NPC 武器（只读） | `npc_dummie` 的 `GetActiveWeapon()` 和字段 | 确认用哪把枪 | 开火测不了 | npc-weapons |
| 14 | 近战 | 拳头触及距离（40 还是 60）、击退；Titan Sword 按全部输入 | 哪些招式有入口 | 回调没绑 | melee |
| 15 | hop-up | Boosted Loader `hemlok_crate`（低于 8 发换弹，1.75 s，21 + 9）；Kinetic `lmg_crate`（滑铲，换瞄具前后）；休眠 hop-up P2020 打 425 伤害解锁；`3030_crate` 腰射 Shatter | | 脚本实现，但有缺口 | hopups |
| 16 | 备弹回充 | Havoc 打一半看备弹涨速 | 约 1 发/s | 确认是否社区加的 | W-FIRE-RELOAD、ammo |
| 17 | 能不能加载 | `give` Ray Gun、Buster、Defender、`mp_weapon_rspn101_og`、双持金色 P2020；看 `[WEAPON-STUB]` 和模型错误 | | 决定哪些能测 | special-energy、weapon-tiers |
| 18 | Sling 和 C.A.R. | Sling 拾取、切换、Tempest 变金再变回；C.A.R. 备弹清零后开到空，看是否自动换弹种 | | 回调没绑 | ballistic-sling、auto-ballistic |
| 19 | Vantage | 3000 / 7500 u 下坠、拉栓间隔 | `.txt` 没写重力，走引擎默认 | | vantage-sniper-weapon |

## 5. HSD 已有什么，缺什么

现状依据：`HSD-Unity/Assets/HSD/Game/Runtime/Combat/`（主线，TF2X 占位框架）和分支 `claude/w2-framework-b44e35`（[HSD-Unity#53](https://github.com/letheli710/HSD-Unity/pull/53)，未合并）。

| 系统 | HSD 现状 | 要新做 | 对应记录 |
|---|---|---|---|
| 武器基类和节奏 | 有：`Weapon`（弹匣、`nextShot`、`reloadUntil`）、`TestRifle` 占位（`Weapons.cs`） | 数据驱动的 `FiringCycle`：点射、拉栓、半自动、回调返回扣弹数 | W-FIRE-RELOAD |
| 命中扫描 | 有：`CombatSim.TraceBullet`，带爆头判定和 A 型墙 | — | W-BALLISTICS |
| 弹道子弹 | **无**（`Throw.cs` 的投掷物积分可复用） | `BallisticRound`：初速、重力、归零、命中盒 | W-BALLISTICS |
| 扩散 | **无** | `SpreadState` | W-SPREAD-RECOIL |
| 后坐 | **无**（只有落地的 view kick，`NativeCamera.cs`） | `RecoilPattern` + 通道 | W-SPREAD-RECOIL |
| 伤害 | 有：`DamageInfo`、`headshot`、爆炸衰减；分支有修正链 `DamageModifiers.cs` | 三段衰减、部位倍数、护盾比例字段 | W-DAMAGE |
| 状态效果和减速 | 分支有：`StatusEffects.cs`、`MoveSlow.cs` | — | `_shared/E-STATUS-EFFECT` |
| 蓄力、转速、热量 | 部分：`InfernoBeam` 有写死的伤害爬升，`SmartPistol` 有锁定 | 通用 `HeatDriver`、蓄力门槛 | charge-spinup、burst-fire |
| 霰弹 | **无** | 图案表、每弹丸结算 | shotgun-blast |
| Mod / 配件 / hop-up | **无** | `WeaponDef` + `WeaponMod` | W-MOD-SYSTEM、attachments、hopups |
| 弹药池 | **无**（只有弹匣） | 备弹、回充 | ammo |
| 档位和掉落 | **无**（`CombatLoadout.cs` 只是选装备） | 武器 + mod 组合 | weapon-tiers |
| 近战 | **无**（`DamageKind.Melee` 枚举在） | 突进、范围、击退 | melee |
| 多武器槽 | **无**（`WeaponKind` 一把） | 槽位、切换时间 | ballistic-sling |
| 放置和炮台 | 有：`Boosts.cs` 哨戒炮；分支 `Deployable.cs`、`Placement.cs` | 可上的炮台 | `rampart-sheila` |
| 敌人开火 | **无**（`Dummy` 不开火，`Boosts.cs` 的炮台除外） | 点射 + 休息 + 命中率 | npc-weapons |

**建议顺序**：Mod 系统 + 数据驱动基础枪（R-301 校准）→ 弹道 → 扩散后坐 → 霰弹、点射 → 蓄力 / 热量 → 配件和 hop-up → 敌人开火 → 近战。这是建议，**没定**，等实测和用户。

## 6. 留给用户看的

1. 过滤草稿（W0）：`pending`，尤其是"传家宝只留数据表""双持不要"。
2. Nemesis 和 Energize 这类 SDK 重写的东西，HSD 按 **S21 字段设计**还是按 **R5 本地实测**？拟合原则是贴 R5 native，但本地的代码不是原版。两边不一致时要有个规矩，建议按 S21 字段做、差异写进 `R5-DIFF-ARCHIVE.md`。
3. 引用是逐行核过的（子任务打印了每条出处，散文里的少量引用只目测过），但**都是静态**。
