# Legion（Ogre）：专属套件规格

2026-11-08，读脚本写成的规格（S 步）。实测（R 步）由主会话填第 8 节。

## 先说结论

- Legion 的整套技能都绕着一挺要"转管"的重机枪：**转管就是 ADS**，按开火也会自动转管；转满（1.5 s）才出第一发，转管期间走速降到 × 0.55。
- 四个技能都是改这挺枪的状态：强力射击（给枪临时加一个"蓄力一发"的参数包，蓄 0.75 s 打出霰弹或穿透弹）、枪盾（枪前挂一个 2500 血的小球盾，强制转管 6 s）、切换模式（近距 ↔ 远距两套弹药参数）、智能核心（12 s 自动锁定 + 这台泰坦所有伤害 × 1.2，不耗弹）。
- HSD 要做：一个 0 → 1 的"转管进度"（进 1.5 s、退 0.75 s，线性），开火门槛 = 进度到 1；四个技能按"加 / 删参数包"实现；强力射击的击退照原版是**恒定 500 u/s**（距离衰减因为运算优先级写错了，从来没生效）。
- 难点：(1) 强力射击、枪盾的冷却从哪一刻开始算，键值有歧义；(2) 切换模式的时长取自动画长度（`ammo_swap_seq`），文件里没有；(3) 智能核心的锁定和子弹导向是原生代码。
- 旧页"智能核心期间强力射击、枪盾回能 × 10"是错的：那来自被砍掉的"攻城模式"，商用版没有任何脚本会打开它（见第 0 节）。

## 0. 来源和可信度

路径缩写（都相对 `TF2-Research/`）：

| 缩写 | 路径 | 可信度 |
|---|---|---|
| W | `local/vpk/client_mp_common/scripts/vscripts/weapons/` | Respawn 原版，多人共用，最高 |
| WT | `local/vpk/client_mp_common/scripts/weapons/`（`.txt`，取 `MP_BASE`，丢 `SP_BASE` / `[$sp]`） | 同上 |
| P | `local/vpk/client_mp_common/scripts/players/mp/`（`.set`） | 同上 |
| V | `local/vpk/client_mp_common/scripts/vscripts/` | 同上 |
| FE | `local/vpk/client_frontend/scripts/vscripts/` | 同上 |
| SV | `local/vpk/client_sp_training/scripts/vscripts/`（零售服务端脚本，含 MP 分支） | Respawn 原版 |
| L | `local/vpk/client_frontend/resource/r1_english.txt`（UTF-16，行号按原文件） | 原版文字，只确认名字和意图 |
| NS 表 | `<TF2>/R2Northstar/mods/Northstar.CustomServers/mod/scripts/datatable/` | Northstar 从零售包导出的表；本地没有零售表可比对，标 [NS 表] |

- Legion 的武器脚本 Northstar 都没覆盖；MP 包和战役包两份完全相同。`Northstar.Custom` 带了一份 `mp_titanweapon_predator_cannon.txt`，比过：只是把几个键挪到 mod 外面好让社区 mod 有空间，数值不变（文件头注释也这么写）。本页用到的 SV 文件 Northstar 有覆盖版，`diff -w` 只差排版。所以 Northstar 私服上测到的 = 原版。
- 标记：[推断] 按代码推出、没实测；[未知] 文件里没有；[原生] 在 C++ 里；[NS 表] 见上。

**对旧页和 SCAN-1108 §3 的更正：**

| 旧说法（出处） | 更正 | 依据 |
|---|---|---|
| 智能核心期间"强力射击和枪盾回能 × 10"（`titans/LEGION.md`） | **错。** × 10 在 `SiegeMode` mod 里；商用版没有任何脚本给武器加 `SiegeMode`（W、V、SV、NS 全 grep 过，只有两处 `HasMod( "SiegeMode" )` 检查）。智能核心脚本只加 `Smart_Core` | WT/`mp_titanability_power_shot.txt:122–125`；WT/`mp_titanability_gun_shield.txt:68–71`；W/`mp_titancore_siege_mode.nut:145–152` |
| 强力射击"冷却 8 s"（旧页） | 回满 8 s，回能前等 1.0 s → 按下到再可用约 9 s | WT/`mp_titanability_power_shot.txt:59–60` |
| 枪盾"冷却 8 s"（旧页） | 回满 8 s；但这个技能带 `ammo_drains_to_empty_on_fire` + `fire_duration 6`，[推断] 能量条在护盾 6 s 里走空，之后才回 8 s → 按下到再可用约 14 s。要实测 | WT/`mp_titanability_gun_shield.txt:28–46` |
| 强力射击"蓄力 0.75 s"（旧页） | 0.75 s 是**转满之后**的蓄力。没转管时先被强制转管 1.5 s → 冷启动约 2.25 s [推断] | WT/`mp_titanweapon_predator_cannon.txt:157, 549, 561`；W/`mp_titanweapon_predator_cannon.nut:125–132` |
| "转管时间（`zoom_time_in`）未实测"（旧页） | 已测：腰射约 1.5 s 才出第一发；ADS 就是转管，转好立刻开火 | TF2-GAPS §4 |
| 击退"因为运算优先级，距离不起作用"（SCAN） | **对。** 补：实际速度恒为 500（方向从 Legion 指向目标），竖直至少 200，直接覆盖目标速度；只有近距模式有击退；只推非人形目标；不乘 Ogre 的 `pushbackScale 0.75`。算式见 2.4 | W/`mp_titanability_power_shot.nut:147–153`；SV/`_utility.gnut:3518–3529` |
| "近 / 远只看主武器有没有 `LongRangeAmmo`，强力射击跟着切"（SCAN） | 对。补：远距模式**每发耗 2 发弹药** | W/`mp_titanweapon_predator_cannon.nut:267–270`；W/`mp_titanability_power_shot.nut:50–70` |
| 枪盾"半径 105，2500 血"（SCAN） | 对。Bulwark 5000；客户端盾颜色仍按 2500 算 | W/`mp_titanability_gun_shield.nut:13–15, 233–239, 376` |
| 智能核心"自动锁定，伤害 +20 %"（SCAN） | 对。补：+20 % 是这台泰坦**造成的所有伤害**（含强力射击、拳）；**不免转管**；每目标锁 0.5 s，最多 6 个 | W/`mp_titancore_siege_mode.nut:110`；SV/`mp/_codecallbacks.gnut:220–228` |
| 用户清单"Siege Mode 被动" | 商用版没有。Legion 第 5 个被动是 Hidden Compartment（`pas_legion_chargeshot`，只是借用了 `legion_siege_mode` 图标）；Siege Mode 是砍掉的设计 | [NS 表] `titan_passives.csv:36`；L:2958–2964；FE/`sh_passives.gnut:213` |

## 1. 主武器：掠食者机枪（`mp_titanweapon_predator_cannon`）

### 1.1 转管（所有模式共用）

**一句话：** 枪有一个"转管进度" z（就是 ADS 进度 `GetZoomFrac()`），按住瞄准或按住开火都会让 z 往 1 走，z 到 1 才能开火。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 静止 | z = 0 | 正常走速 | 按瞄准 / 按开火 / 被强制 ADS（枪盾、强力射击）→ 转管中 |
| 转管中 | z 在 0–1 之间上升 | z 每秒 + 1 / 1.5；走速在 1 和 × 0.55 之间按 z 变 [推断]；转管音效按 z 定位播放 | z = 1 → 转好；全松开 → 减速 |
| 转好 | z = 1 | 按住开火就出弹，15 发 /s；没按开火只是空转 | 松开瞄准和开火 → 减速 |
| 减速 | 松开 | z 每秒 − 1 / 0.75；中途再按就从当前 z 继续往上 | z = 0 → 静止 |

- 开火门槛在脚本里：玩家 `GetZoomFrac() < 1` 就不出弹（W/`mp_titanweapon_predator_cannon.nut:125–132`）。
- "按开火 = 按瞄准"由 `attack_button_presses_ads 1` 实现（WT `:181`）[原生]。
- NPC 不用 z：开火前等 `npc_pre_fire_delay` 1.0 s（W 同上 `:204–249`；WT `:381–382`）。

**时间线（冷启动按住开火）：** 0 s 按下，z 从 0 线性上升（实测 `GetZoomFrac` 严格线性）→ 1.5 s z = 1，同一帧出第一发（实测 0.007 s 内）→ 每 1/15 s 一发 → 松开后 0.75 s 内 z 降到 0。
**再按：** 松开 x 秒（x < 0.75）后再按，z = 1 − x / 0.75，重新转满要 (1 − z) × 1.5 = 2x 秒 [推断]。例：松开 0.3 s → 0.6 s 再出弹。

### 1.2 近距 / 远距两种弹

**一句话：** 默认近距（散布大、伤害距离近）；切换模式后加 `LongRangeAmmo` 参数包：ADS 散布 3.4° → 0.4°，满伤距离 1200 → 3000，ADS 放大到 FOV 40，但每发耗 2 发弹药。

| 项 | 近距（默认） | 远距（`LongRangeAmmo`） | 出处 |
|---|---|---|---|
| 射速 | 15 /s（实测 14.4） | 同 | WT/`mp_titanweapon_predator_cannon.txt:39`；TF2-GAPS §4 |
| 每发耗弹 | 1 | **2**（开火函数返回 2） | W/`mp_titanweapon_predator_cannon.nut:266–270` |
| 伤害 对铁驭 | 35 → 25 | 同 | WT `:43–44` |
| 伤害 对泰坦 | 100 → 72 | 同 | WT `:45–46` |
| 满伤 → 最低伤距离 | 1200 → 1800 | 3000 → 3250 | WT `:87–88, 487–490` |
| 散布 腰射 | 3.4° | 3.4° | WT `:184–188, 466–470` |
| 散布 ADS | 3.4°（空中 4.4°） | 0.4°（空中也 0.4°） | WT `:189–191, 472–474` |
| 每发散布增量 / 上限 / 回落 | +0.1° / +1.0° / 0.05 s 后 4.5°/s | 同 | WT `:193–208` |
| ADS FOV | 75（不放大） | 40 | WT `:159, 475` |
| 后坐 random（俯仰 / 左右） | 0.46 / 1.0 | 0.15 / 0.2 | WT `:215–223, 477–485` |
| NPC 命中倍率 | — | × 1.5 | WT `:504–505` |
| 弹道 | 即时命中，1 颗 `FireWeaponBullet` | 同 | W 同上 `:266` |
| 强力射击变成 | 近距霰弹 | 远距穿透弹 | 第 2 节 |

公共数值：

| 项 | 值 | 出处 |
|---|---|---|
| 弹匣 | 100；`pas_legion_weapon` 140（默认装备就带，实测 140） | WT `:59, 667–670`；TF2-GAPS §4 |
| 备弹 | 6000，不扣 | WT `:90, 151–152` |
| 换弹 | 4.6 s（文件），`late1/2` 3.66 / 2.13；实测 4.11 s，弹药 3.62 s 到位；不能用开火打断 | WT `:160–165`；TF2-GAPS §4 |
| 爆头 / 弱点 | × 1.5 / × 1.5 | WT `:176–178, 148` |
| ADS 走速 | × 0.55（116）；`pas_legion_spinup` × 0.75（≈ 158） | WT `:155, 671–674`；T0 `t0_kit` |
| ADS 鼠标 | 转管时转得更快（实测 × 1.52，因为 FOV 不变） | T0-REPORT |
| 后坐弹簧 | `lmg`；实测俯仰 ±0.5°、左右 ±0.95°、滚转 ±0.82° | WT `:213`；TF2-GAPS §4 |
| 冲击力 | 5000 | WT `:147` |

**DPS（近距、全中）：** 对泰坦 15 × 100 = 1500。远距模式 DPS 相同，但 140 发只能打 70 发（4.7 s），近距 140 发（9.3 s）。

**边界情况：**
- 腰射散布 3.4° 可能永远用不上：开火时 z 一定是 1，此时武器多半算在 ADS [推断]。要实测远距模式腰射按住开火的散布是 3.4° 还是 0.4°、FOV 会不会变 40。
- 冲刺会不会打断转管 [原生，未知]。
- 远距模式的"每发 2 发"只在普通开火；智能核心下走智能弹药函数，返回值不是 2（但核心期间本来就不扣弹）。

### 1.3 要实测

- z（`player.GetZoomFrac()`）随时间：腰射、ADS、松开、松开 0.3 s 再按；第一发时刻（弹匣值第一次减少）。
- 走速随 z（`player.GetVelocity()` 水平长度）。
- 远距模式：每发弹匣减几（`weapon.GetWeaponPrimaryClipCount()`）；ADS FOV；腰射时的散布和 FOV。

## 2. 进攻：强力射击（`mp_titanability_power_shot`）

**一句话：** 按一下：强制转管，转满后主武器蓄力 0.75 s，自动打出一发——近距模式是 10° 锥里的霰弹（每个目标 2000，击退泰坦），远距模式是穿透弹（2000 + 爆炸 1800）。

### 2.1 状态机

强力射击这把"技能武器"自己**不开火**；它只给主武器加参数包，真正开火的是主武器（伤害来源是 `mp_titanweapon_predator_cannon`）。所以 `mp_titanability_power_shot.txt:62–77` 里的伤害键不用。

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 就绪 | 能量 80 / 80（Hidden Compartment：每发 40，可存 2 发） | — | 按下且条件都满足 |
| 准备 | 按下那一帧 | 关掉下机、主武器强制 ADS、关掉近战；近距：主武器 + `CloseRangePowerShot`；远距：主武器 − `LongRangeAmmo` + `LongRangePowerShot`（FD / 被动再各加一个，见下）；技能能量 − 80（− 40） | — |
| 转管 | 强制 ADS | z 往 1 走（已转好则跳过） | z = 1 |
| 蓄力 | z = 1 时自动开始（`zoomfrac_autoattack 1.0`）[推断] | 主武器蓄力 0.75 s，不用按住（`charge_require_input 0`）；期间不能换弹 | 蓄满自动开火（`charge_end_forces_fire 1`） |
| 开火 | 蓄满 | 见 2.2 / 2.3；播 3p 手势动作 | 同一帧收尾 |
| 收尾 | 开火后 | 恢复近战、下机；清掉强制 ADS（**枪盾还开着就不清**）；删掉强力射击参数包；远距再加回 `LongRangeAmmo` | → 冷却 |
| 冷却 | 按下那一帧起 | 1.0 s 后按 10 /s 回能（Hidden Compartment 5 /s） | 满 |

**按下不生效的条件**（不耗能量，W/`mp_titanability_power_shot.nut:16–37`）：在做上下机等动作；在近战；主武器无效；主武器在换弹；切换模式动画在播；主武器已经带着强力射击参数包；弹匣为 0；主武器处在换弹"中间进度"状态（`GetReloadMilestoneIndex() != 0`，即换弹被打断过还没换完 [推断]）。

**时间线：**
- 已转好：0 s 按下 → 0–0.75 s 蓄力（走速一直是 × 0.55）→ 0.75 s 开火 → 1.0 s 开始回能 → 9.0 s 能再用。
- 冷启动：0 s 按下 → 0–1.5 s 转管 → 1.5–2.25 s 蓄力 → 2.25 s 开火 [推断]。T0 实测"蓄力中"走速 139，约等于 z ≈ 0.75 时的走速，说明转管确实是边走边算的。
- Hidden Compartment：一发 40，回 5 /s → 一发 8 s；两发都用完从 0 回满 16 s。

### 2.2 近距强力射击（`CloseRangePowerShot`）

| 项 | 值 | 出处 |
|---|---|---|
| 方式 | `ShotgunBlast( 16 发, 半角 10° )`：在 10°（搜索时 × 1.1）锥里找可见实体，**每个实体吃一次**伤害，最多 16 个；没用完的"发数"打成最多 16 条视觉弹道 | W/`mp_titanweapon_predator_cannon.nut:166`；W/`_weapon_utility.nut:489–551` |
| 射程 | 1600（= 本模式的 `damage_far_distance`） | WT/`mp_titanweapon_predator_cannon.txt:540`；W/`_weapon_utility.nut:502–503` |
| 对泰坦 | 2000（近远相同）；Hidden Compartment × 0.85 = 1700 | WT `:537–538, 573–577` |
| 对其他 | 200（≤ 800 u）→ 50（1600 u）；打到非实体部分距离再 + 130 | WT `:535–536, 539–540`；W/`_weapon_utility.nut:584–590` |
| 伤害标记 | `DF_GIB` + `DF_EXPLOSION` + `DF_KNOCK_BACK`；FD Executioner 再加 `DF_SKIPS_DOOMED_STATE` | W/`mp_titanweapon_predator_cannon.nut:160–164` |
| 散布键 | 16°（只影响视觉弹道） | WT `:527–534` |
| 击退 | 见 2.4 | — |

### 2.3 远距强力射击（`LongRangePowerShot`）

| 项 | 值 | 出处 |
|---|---|---|
| 方式 | 一发 bolt，10000 u/s，脚本设 gravity −0.1；每个实体只伤一次；可穿透（`pass_through_depth 500`） | W/`mp_titanweapon_predator_cannon.nut:183–189`；WT `:637` |
| 直击 | 200 / 对泰坦 2000（无衰减）；Hidden Compartment 对泰坦 × 0.85 = 1700 | WT `:598–601, 649–653` |
| 爆炸 | 200 / 对泰坦 1800（**被动不减爆炸**）；内半径 50、外半径 150；**会炸到自己** | WT `:602–606` |
| 散布 | 0 | WT `:627–634` |
| ADS FOV | 40 | WT `:635` |
| 击退 | 没有（伤害标记里没有 `DF_KNOCK_BACK`） | W 同上 `:183` |
| FD Drill Shot | `pass_through_damage_preserved_scale 1.5`：每穿一个目标伤害 × 1.5 [推断，按键名和 L:11724] | WT `:658–661` |

对泰坦一发最多 2000 + 1800 = 3800（直击 + 爆炸都吃）[推断]。

### 2.4 击退（只在近距强力射击）

W/`mp_titanability_power_shot.nut:144–155`，每个被伤到的实体跑一次：

```
if ( 伤害带 DF_KNOCK_BACK && 目标不是人形 )
    distance = Legion 原点 到 目标原点 的距离
    pushback = Normalize( 目标原点 − Legion 原点 )
    pushback *= 500 * 1.0 - StatusEffect_Get( victim, pushback_dampen ) * GraphCapped( distance, 0, 1200, 1.0, 0.25 )
    PushPlayerAway( victim, pushback )
```

- 运算顺序：乘法先算，所以是 `500 − dampen × 曲线`。
- `pushback_dampen` 全部脚本里**没有任何地方设置**（只有这一处读），所以 dampen = 0，系数恒为 500。
- `PushPlayerAway` **直接覆盖**目标速度，竖直分量取 max(200, |原竖直分量|)（SV/`_utility.gnut:3518–3529`）。它不乘设置文件的 `pushbackScale`（那个只在 `PushEntWithVelocity` 里用，SV/`_utility.gnut:3430–3460`；Ogre 是 0.75，P/`titan_ogre.set:4`）。
- 非人形：玩家泰坦；NPC 里 bodyType 不是 human / marvin 的（泰坦、死神、无人机等）。铁驭、步兵、幽灵、小炮塔不推（V/`_utility_shared.nut:3514–3526`）。

| 距离（u） | 实际速度（平地，水平 / 竖直） | 本来想要的（`500 × (1 − dampen) × 曲线`） |
|---|---|---|
| 0 | 500 / 200 | 500 |
| 300 | 500 / 200 | 406 |
| 600 | 500 / 200 | 313 |
| 900 | 500 / 200 | 219 |
| 1200 | 500 / 200 | 125 |
| 1600（射程尽头） | 500 / 200 | 125 |

高低差大时，竖直分量 = 500 × 竖直方向分量，至少 200。

### 2.5 数值

| 项 | 值 | 出处 |
|---|---|---|
| 能量 / 每发 | 80 / 80，满了才能用 | WT/`mp_titanability_power_shot.txt:47–52` |
| 回能 | 10 /s，延迟 1.0 s | 同上 `:59–60` |
| Hidden Compartment | 每发 40、最少 40 才能用、回能 × 0.5；伤害（对泰坦）× 0.85 | 同上 `:126–131`；WT/`mp_titanweapon_predator_cannon.txt:573–577, 649–653` |
| 蓄力 | 0.75 s | WT/`mp_titanweapon_predator_cannon.txt:549, 612` |
| 转满才自动出手 | `zoomfrac_autoattack 1.0` | 同上 `:561, 636` |
| 每发耗主武器弹 | 1 [推断：开火函数返回 1] | W/`mp_titanweapon_predator_cannon.nut:170, 195` |

### 2.6 边界情况

- 蓄力期间不能下机（可以弹射；弹射时恢复近战和下机，W/`mp_titanability_power_shot.nut:76–87`）。
- 蓄力期间不能换弹（参数包 `reload_enabled 0`），也不能切换模式（切换模式会检查参数包）。
- 和枪盾同时开：强力射击收尾不清强制 ADS；枪盾结束时如果强力射击还在蓄力也不清。两个都结束才清。
- 智能核心期间用：强力射击走自己的分支，不走智能弹药（不锁定），但吃核心的 +20 %。
- 蓄力中死亡：参数包留在武器上，武器跟着泰坦没了，不影响。
- FD Executioner：近距强力射击带 `DF_SKIPS_DOOMED_STATE`，FD 回调把打到的毁灭状态泰坦伤害改成"血 + 1"→ 直接打死（W/`mp_titanweapon_predator_cannon.nut:26–27, 297–310`）。

### 2.7 要实测

- 冷启动和已转好两种情况：按下 → 开火的时间；主武器 `GetWeaponChargeFraction()` 随时间（蓄力从 z = 1 才开始，还是和转管同时）。
- 击退：近距打一台不冻结的敌方泰坦，距离 300 / 900 / 1500，记命中后第一帧目标速度（`foe.GetVelocity()` 或 KIT 日志里的坐标差）。原版应该三档都是水平 500 + 竖直 200。最好也打一台玩家泰坦（NPC 的地面移动可能把速度吃掉）。
- 冷却：`offhand0` 弹匣值随时间（验证"按下起 1 s 后开始回"）。
- 主武器弹匣在强力射击后少几发。

## 3. 防御：枪盾（`mp_titanability_gun_shield`）

**一句话：** 在枪口前挂一个半径 105 的球形能量盾，6 s，挡子弹和投射物，盾有 2500 血；期间强制转管、不能近战。

### 3.1 状态机

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 就绪 | 能量 200 / 200 | — | 按下且不在做上下机等动作 |
| 等枪 | 按下 | 主武器强制 ADS（开始转管）、关近战；每 0.1 s 检查一次，等到"手里是掠食者且没在近战"**或者主武器在换弹**就往下走 | 条件满足 |
| 盾在 | 生成球盾 | 球盾挂在枪的 `gun_shield` 挂点上跟着枪动；血 2500（Bulwark 5000）；挡子弹和投射物；不回血 | 6 s 到 / 盾被打爆 / 死亡 / 下机 / 弹射 / 设置改变 / 被拉进同步动作（`ContextAction_SetBusy`） |
| 盾没了但时间没到 | 盾被打爆 | 播破盾特效；**强制 ADS 和禁近战照旧，直到 6 s 到**（这条线程不等"盾被毁"信号）[推断] | 6 s 到 |
| 结束 | — | 清强制 ADS（强力射击参数包在就不清）、恢复近战 | → 冷却 |

开着盾时可以照常开火（转满后）。

### 3.2 时间线

0 s 按下 → 同帧或 0.1 s 内生成盾（已经拿着枪的话）→ 0–1.5 s 转管（冷启动）→ 1.5 s 起可以边盾边打 → 6.0 s 盾消失、清强制 ADS。冷却见下（两种推断）。

### 3.3 数值

| 项 | 值 | 出处 |
|---|---|---|
| 半径 / 高 | 105 / 210 | W/`mp_titanability_gun_shield.nut:13, 212–214` |
| 血 | 2500；Bulwark 或 FD `fd_gun_shield` 5000 | 同上 `:14–15, 233–239` |
| 挡子弹的角度 | `bullet_fov` = 120 | 同上 `:225`；FE/`sh_consts.gnut:2118` |
| 持续 | 6.0 s（`fire_duration`） | WT/`mp_titanability_gun_shield.txt:46` |
| 能量 / 回能 | 200 / 25 /s（回满 8 s），延迟 0 | 同上 `:28–40` |
| 冷却算法 | `ammo_instant` + `ammo_drains_to_empty_on_fire 1` + `ammo_no_remove_from_clip 1`：[推断] 能量条在 6 s 里走空，之后回 8 s → 按下到再可用约 14 s；另一种读法是按下就开始回 → 8 s。用同一组键的还有铁驭隐身（MP `fire_duration 15`、回 10 /s），实测时可以一起对照 | 同上；WT/`mp_ability_cloak.txt:41–47` |
| 挡子弹扣多少 | 那发子弹的伤害（电弧弹 × 1.5） | V/`weapons/_vortex.nut:1621–1636` |
| 挡投射物扣多少 | 投射物武器的 `damage_near_value`（**不是对泰坦值、不含爆炸**） | 同上 `:1781–1790` |

### 3.4 边界情况

- 枪盾挡的是投射物和子弹；近战、范围伤害（爆炸绕过来的部分）、虹吸这种 `ShotgunBlast` 直接点名的伤害挡不挡 [原生，未知]。
- 客户端盾的颜色按 2500 算（`:376`），Bulwark 的 5000 盾在掉到 2500 以下前颜色一直是满的——外观 bug。
- 和强力射击可以同时开（见 2.6）。
- 换弹中按枪盾：等枪那一步会立刻放行（`!weapon.IsReloading()` 不成立），盾照样出。
- FD Redirect：盾吃的伤害 1:1 加到 Legion 护盾（到上限为止）（V/`weapons/_vortex.nut:1551–1564`）。
- NPC 专用 mod：`npc_infinite_shield`（无敌盾）、`npc_more_shield` 等，玩家没有。

### 3.5 要实测

- `offhand1` 弹匣值随时间：6 s 里是不是在走空、之后多久回满（定冷却算法）。
- 盾血（`weapon.GetWeaponUtilityEntity().GetHealth()`）被一种子弹、一种火箭打时每次扣多少。
- 盾被打爆后强制 ADS 还持续多久（`primary.GetForcedADS()`、走速）。

## 4. 战术：切换模式（`mp_titanability_ammo_swap`）

**一句话：** 播一段换弹动作，播完后近距 ↔ 远距切换；不换弹匣、不补弹。

### 4.1 状态机

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 就绪 | 能量 200 / 200 | — | 按下且条件满足 |
| 换模式 | 按下 | 标记"切换中"；播 1p 自定义动作和 3p 手势；关近战 | 视图模型 `ammo_swap_seq` 序列播完 |
| 生效 | 动作播完（或中途死亡 / 下机 / 弹射 / 设置改变——**照样切**） | 主武器切换 `LongRangeAmmo`；本技能切换 `ammo_swap_ranged_mode`、强力射击切换 `power_shot_ranged_mode`（只换图标）；驾驶舱颜色：近距黄、远距红、智能核心中隐藏；恢复近战 | → 冷却 |

**按下不生效的条件**（W/`mp_titanability_ammo_swap.nut:110–131`）：在做上下机等动作；在近战；手里不是掠食者（`IsPredatorCannonActive(owner, false)`，不要求转好）；主武器在换弹；主武器带着强力射击参数包。生效时如果强力射击参数包在，就不切（防御性修补，`:230–232`）。

### 4.2 数值

| 项 | 值 | 出处 |
|---|---|---|
| 切换时长 | 视图模型序列 `ammo_swap_seq` 的长度 [未知，动画里] | W/`mp_titanability_ammo_swap.nut:192–198` |
| 能量 / 回能 | 200 / 100 /s，延迟 0 → 2 s；同样带 `drains_to_empty`、`fire_duration 0.1` → [推断] 约 2.1 s | WT/`mp_titanability_ammo_swap.txt:29–42` |
| 不挡冲刺 | `primary_fire_does_not_block_sprint 1` | 同上 `:47` |

### 4.3 边界情况

- 切换期间按强力射击：不生效（`ammoSwapPlaying`）。
- 转管状态、弹匣数都不变 [推断]。
- 下机时正在切：线程结束时照样执行切换（`OnThreadEnd` 里切）。

### 4.4 要实测

- `player.GetViewModelEntity().GetSequenceDuration( "ammo_swap_seq" )`（服务端能直接读）；按下到 `HasMod( "LongRangeAmmo" )` 变化的时间。
- 切换前后弹匣数、z 是否变化；冷却曲线（`offhand2`）。

## 5. 核心：智能核心（`mp_titancore_siege_mode`）

**一句话：** 12 s 里主武器变成智能武器：腰射和 ADS 都能自动锁定最多 6 个目标，子弹打向锁点，不耗弹；这台泰坦造成的所有伤害 × 1.2。

### 5.1 状态机

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 充能 | — | 核心表涨（时间模式 150 s） | 满 |
| 可用 | 满，且通用条件（见 Monarch 页 5.1）+ 有 soul + 主武器有效且**没在换弹** | — | 按下 |
| 进行中 | 按下 | 主武器 + `Smart_Core`；玩家加 `smartCore` 状态（HUD：剩余时间、击杀数、锁定标记）；驾驶舱颜色隐藏；soul 加 `titan_damage_amp 0.20`；掠食者在手时枪口加激光瞄准特效 | 12 s（Sensor Array 18 s）到 / 死亡 / 下机 / 弹射 |
| 结束 | — | 删 `Smart_Core`、恢复驾驶舱颜色、删伤害加成、核心表重新开始 | → 充能 |

`Smart_Core` 参数包（WT/`mp_titanweapon_predator_cannon.txt:507–519`）：允许 ADS 锁定、允许腰射锁定、开火时继续搜索；`ammo_no_remove_from_clip 1`（不耗弹）；涡旋吸能 0.033；关辅助瞄准。

### 5.2 锁定和开火

| 项 | 值 | 出处 |
|---|---|---|
| 搜索 | 角度 60（全角还是半角 [原生，未知]）、距离 3000；铁驭、NPC 都锁；不锁投射物；泰坦挡视线 | WT/`mp_titanweapon_predator_cannon.txt:413–418` |
| 目标数 | 最多 6 | 同上 `:420` |
| 每目标锁时 | 0.5 s；新目标无额外延迟 | 同上 `:419, 424–425` |
| 重甲每个目标几把锁 | 1 | 同上 `:426` |
| 泰坦锁点 | 躯干前 / 后、左右腿、躯干底、头、左右臂（8 个） | 同上 `:437–444` |
| 没锁也能开火 | 是（`SmartAmmo_SetAllowUnlockedFiring( weapon, true )`） | W/`mp_titanweapon_predator_cannon.nut:100` |
| 锁中后 | 每发按发数轮流打向各锁定目标的锁点，用"无散布"的特殊子弹；锁点处于"主动射击"状态时算爆头 | W/`sh_smart_ammo.gnut:183–256` |
| 转管 | **照样要转满才开火**（开火门槛检查在智能弹药之前） | W/`mp_titanweapon_predator_cannon.nut:125–132, 260–263` |
| 伤害加成 | 这台泰坦造成的所有伤害 × 1.20（主武器、强力射击、拳） | W/`mp_titancore_siege_mode.nut:110`；SV/`mp/_codecallbacks.gnut:220–228` |

### 5.3 数值

| 项 | 值 | 出处 |
|---|---|---|
| 持续 | 12 s；`pas_legion_smartcore` 18 s | WT/`mp_titancore_siege_mode.txt:27, 67–70` |
| 充能 | `core_build_time` 150 s（时间模式；伤害模式见 Monarch 页 5.1） | 同上 `:25` |
| 蓄力 | 0 | 同上 `:26` |
| 核心期间被动 | `PAS_SMART_CORE`（只用于客户端击杀计数） | 同上 `:28`；V/`client/cl_player.gnut:909` |

### 5.4 边界情况

- 下机直接结束核心（剩余时间作废）。
- 换弹中不能开核心；核心中能换弹（但不耗弹，基本用不着）。
- 核心期间切换模式：可以，远距 / 近距的散布和伤害距离照常生效（智能弹药只改方向）；HUD 记录当前模式。
- `SiegeMode` 参数包不会被加上（第 0 节），技能回能不变。

### 5.5 要实测

- 锁定进度（`weapon.SmartAmmo_GetTargets()` 的 `fraction`）随时间：一个目标多久锁满、6 个目标多久。
- 锁中后子弹是否全中、伤害是否 × 1.2（KDMG 行）、弹匣是否不变。
- 核心中腰射是否仍要转 1.5 s。

## 7. 专属被动和 FD 升级

### 7.1 Legion 专属被动（passive2，五选一，[NS 表] `titan_passives.csv:15, 31–33, 36`）

默认装备是 Enhanced Ammo Capacity（[NS 表] `default_titan_loadouts.csv:7`）。被动在泰坦生成时按 soul 的被动给武器加 mod（SV/`_passives.gnut:800–828`），Bulwark 例外（盾生成时查 soul）。

| 被动 | 名字 | 改什么 | 数值 | 出处 |
|---|---|---|---|---|
| `pas_legion_weapon` | Enhanced Ammo Capacity | 主武器 + mod；给的时候把弹匣填满 | 弹匣 100 → 140 | WT `:667–670`；SV/`_passives.gnut:800–807`；L:2823–2825 |
| `pas_legion_spinup` | Light-Weight Alloys | 转管时走速倍率 0.55 → 0.75；**不缩短转管时间** | ADS 走速 116 → ≈ 158 | WT `:671–674`；L:2827–2829 |
| `pas_legion_gunshield` | Bulwark | 枪盾血翻倍 | 2500 → 5000 | W/`mp_titanability_gun_shield.nut:233–239`；L:2831–2833 |
| `pas_legion_smartcore` | Sensor Array | 智能核心变长 | 12 → 18 s | WT/`mp_titancore_siege_mode.txt:67–70`；L:2835–2837 |
| `pas_legion_chargeshot` | Hidden Compartment | 强力射击两发；回能减半；对泰坦直击伤害 × 0.85（爆炸不减） | 80 能量 / 每发 40 / 5 /s；2000 → 1700 | WT/`mp_titanability_power_shot.txt:126–131`；W/`mp_titanability_power_shot.nut:57–58, 67–68`；L:2962–2964 |

**被砍掉的 Siege Mode：** 本地化有"Siege Mode：Long-Range mode replaced by Siege. Movement locked in exchange for much faster cooldowns on abilities."（L:2958–2960），枚举里有 `PAS_LEGION_SIEGE`（FE/`sh_passives.gnut:213`），但被动表里没有它。残留：`SiegeMode` mod（转管 × 0.9、强力射击和枪盾回能 × 10）、`mp_titanweapon_predator_cannon_siege.txt`（不用转管、弹匣自动回 60 /s、不能换弹、射速 10、举枪 2.5 s，WT/`mp_titanweapon_predator_cannon_siege.txt:14–22`）、两处"带 SiegeMode 就不清强制 ADS"的检查。都不会生效。HSD 如果想做"架炮模式"，这些是现成的设计草稿。

### 7.2 FD（Aegis）升级

只在 playlist `aegis_upgrades` = 1 时生效。等级按 [NS 表] `unlocks_fd_titan_level.csv:4–22`。

| 等级 | 升级 | 改什么 | 出处 |
|---|---|---|---|
| 2 | Piercing Rounds | 主武器 `fd_piercing_shots`：子弹穿透深度 0 → 500 | SV/`_passives.gnut:636–641`；WT `:675–678` |
| 5 | Chassis Upgrade | 设置 mod `fd_health_upgrade`：血 +2500（12500 → 15000） | SV/`_passives.gnut:603–605`；P/`titan_ogre_minigun.set:43–46` |
| 8 | Executioner | `fd_closerange_helper` → 近距强力射击带 `DF_SKIPS_DOOMED_STATE`，打到毁灭状态的泰坦直接打死 | SV/`_passives.gnut:620–625`；W/`mp_titanweapon_predator_cannon.nut:161–162, 297–310` |
| 11 | Redirect | 主武器 `fd_gun_shield_redirect`：枪盾吃的伤害 1:1 加到 Legion 护盾 | SV/`_passives.gnut:642–647`；V/`weapons/_vortex.nut:1551–1564` |
| 14 | Shield Upgrade | 护盾上限 × 1.5（2500 → 3750） | SV/`_passives.gnut:632–635` |
| 17 | Drill Shot | `fd_longrange_helper` → 远距强力射击每穿一个目标伤害 × 1.5 [推断] | SV/`_passives.gnut:626–631`；WT `:658–661`；L:11724 |
| 20 | Dreadnought | 一次给齐：弹匣 140（并填满）、轻合金、Sensor Array、Hidden Compartment、枪盾 5000（用 `fd_gun_shield` mod，不是 Bulwark 被动） | SV/`_passives.gnut:648–680`；L:11729 |

## 8. 实测

本地私服 `mp_lf_stacks`，运行 `20261108_141857_kit_c`（分析 `an_kit_bc.py`）。射击时刻从客户端每帧的弹匣变化读；伤害是最终伤害（`KFIN`）。靶子是敌方 Atlas NPC 泰坦，600 u，护盾 0。

### 8.1 转管和射速

| 情况 | 实测 |
|---|---|
| 腰射按住（冷枪） | 自动转管，转管进度（`GetZoomFrac`）1.50 s 到 1，**第一发在按下后 1.509 s**；之后每 0.071 s 一发（约 14.1 /s） |
| 先 ADS 2 s 再开火 | ADS 1.50 s 转满；开火后 0.007 s 出第一发 |
| ADS 0.2 s 就按开火 | 等转满：第一发在 ADS 后 1.508 s |
| 按 0.6 s、松 0.4 s、再按 1.0 s | **一发也没打出来**：0.6 s 没转满，松开时进度回落，再按的 1.0 s 也不够 |
| 近距模式每发 | 对泰坦 100（600 u） |
| 远距模式每发 | 对泰坦 150（600 u），弹匣大约每发 −2 |
| 智能核心 | 每发 180（= 150 × 1.2），20 发 |

### 8.2 强力射击

| 项 | 实测 |
|---|---|
| 按下 | 进攻弹药 80 → 0；强制转管，1.5 s 转满 |
| 蓄力 | 转满后主武器蓄力 0 → 约 0.9，约 0.75 s |
| 出手 | 按下后约 2.25 s（冷枪：1.5 转管 + 0.75 蓄力） |
| 伤害（近距模式） | 600 u：2000；300 u：3000 |
| 伤害（远距模式） | 600 u：3000 |
| 击退（近距模式） | 敌方泰坦被打后水平速度约 **400–466 u/s**、竖直 +87…+162，**300 / 600 / 900 / 1300 u 都一样**，约 1 s 内被地面摩擦停下，推出约 300–500 u |
| 击退（远距模式） | 没有，靶子不动 |
| 冷却 | 按下时弹药清零；按下后约 1.1 s（还在转管）就开始回，每 0.1 s +1（10 /s，8 s 满）。所以冷却从按下后约 1.1 s 算，不是从出手算 |

- **距离不衰减已实测确认**（脚本里运算优先级写错，见第 2 节）。速度是 10 Hz 位置采样算的，比脚本的 500 略低，是采样时地面摩擦已经开始〔推断〕。

### 8.3 枪盾

- 按住 3 s 后松开：枪盾仍然持续到 6 s（防御弹药 200 → 2，每 0.5 s −17），期间强制转管（1.5 s 转满）。
- 6 s 结束后弹药从 2 回升，约 25 /s，**8 s 回满**。冷却从枪盾结束开始算。

### 8.4 切换模式

- 切到远距：主武器加 `LongRangeAmmo`，强力射击加 `power_shot_ranged_mode`，切换技能加 `ammo_swap_ranged_mode`。切换动作的时长没量到（武器没换，客户端日志看不出）。



## 9. 能脱离 TF2 照做的 / 还缺的

**能照做的：**
- 转管：0 → 1 线性进 1.5 s、出 0.75 s，开火门槛 z = 1，按开火 = 按瞄准，走速 × 0.55（被动 0.75）。
- 近 / 远两套弹的全部参数（射速、每发耗弹 1 / 2、伤害、距离、散布、FOV、后坐）。
- 强力射击的触发条件、参数包切换、蓄力 0.75 s、近距霰弹（10° 锥、每目标一次、2000 / 200 → 50、1600 u）、远距穿透弹（2000 + 1800 爆炸、穿透、炸自己）、击退（恒 500 + 竖直 ≥ 200，覆盖速度，只推非人形）、收尾规则。
- 枪盾的尺寸、血量、6 s、强制转管、禁近战、和强力射击的叠加规则、投射物扣血规则。
- 切换模式的条件和生效内容。
- 智能核心的持续、锁定参数、不耗弹、伤害 × 1.2、结束条件。
- 五个被动、七个 FD 升级。

**还缺的（要实测或要拍板）：**
- 强力射击：蓄力是转满后才开始还是同时开始（冷启动 2.25 s 还是 1.5 s）。
- 枪盾和切换模式的冷却从哪一刻算（14 s 还是 8 s；2.1 s 还是 2 s）。
- 切换模式动画长度（`ammo_swap_seq`）。
- 盾被打爆后强制转管是否持续到 6 s。
- 远距模式腰射时的散布和 FOV。
- 智能核心：锁定搜索角的含义、子弹导向细节（原生）。
- 击退对 NPC 泰坦和玩家泰坦的实际位移（`SetVelocity` 对 NPC 地面移动的效果）。
- 要拍板：击退照原版做成恒 500，还是按本意做成 500 → 125 的距离衰减。

**11-08 实测补上的（见第 8 节）：** 转管 1.50 s、射速 14.1 /s；冷启动强力射击 2.25 s（转管 1.5 + 蓄力 0.75，回答了"蓄力是转满后才开始"）；击退约 400–466 u/s、300–1300 u 不衰减，只有近距模式有；枪盾 6 s、结束后 8 s 回满（冷却从结束算）；强力射击冷却从按下后约 1.1 s 算；智能核心每发 × 1.2。**仍缺：** 切换模式的动作时长。
