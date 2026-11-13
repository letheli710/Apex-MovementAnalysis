# Monarch（Atlas，内部名 Vanguard）：专属套件规格

2026-11-08，读脚本写成的规格（S 步）。实测（R 步）由主会话填第 8 节。

## 先说结论

- Monarch 是"越打越强"的泰坦：XO-16 机枪、火箭齐射、能量虹吸（打中敌人给自己回护盾，同时扣掉对方一半护盾上限并减速）、重新装填（一键把进攻、防御、dash 回满）。核心不是大招，而是**永久升级**。
- 升级核心每用一次：护盾回满，再按"第几次用"给一项升级。第 1 次给第 1 档、第 2 次给第 2 档、第 3 次给第 3 档；每档三选一，**出战前在装备栏选好**（passive4 / 5 / 6），战斗中不选。第 4 次起只回护盾。
- 九项升级全是"给武器加一个参数包（mod）"或"换一把武器"，没有新机制。HSD 要做的是：挂在泰坦身上的升级计数 + 9 个参数包 + 虹吸的命中规则 + 齐射的"先张开再收拢"弹道 + 多目标导弹的按住锁定。
- 难点三个：(1) 虹吸一次命中会触发几次伤害事件（直击和爆炸可能各算一次，回盾、扣盾都会翻倍），脚本看不出，要实测；(2) 齐射的漂移、XO-16 加速器的射速爬升、导弹锁定是原生代码，只有参数；(3) 虹吸 `.txt` 写的蓄力 3 s 和实际出手时间的关系不明。

## 0. 来源和可信度

路径缩写（都相对 `TF2-Research/`）：

| 缩写 | 路径 | 可信度 |
|---|---|---|
| W | `local/vpk/client_mp_common/scripts/vscripts/weapons/` | Respawn 原版，多人共用，最高 |
| WT | `local/vpk/client_mp_common/scripts/weapons/`（`.txt`，取 `MP_BASE`，丢 `[$sp]`） | 同上 |
| P | `local/vpk/client_mp_common/scripts/players/mp/`（`.set`） | 同上 |
| V | `local/vpk/client_mp_common/scripts/vscripts/` | 同上 |
| FE | `local/vpk/client_frontend/scripts/vscripts/`（`sh_consts.gnut`、`sh_passives.gnut`） | 同上 |
| SV | `local/vpk/client_sp_training/scripts/vscripts/`（零售服务端脚本，含 MP 分支） | Respawn 原版 |
| L | `local/vpk/client_frontend/resource/r1_english.txt`（UTF-16，行号按原文件） | 原版文字，只用来确认名字和设计意图 |
| NS 表 | `<TF2>/R2Northstar/mods/Northstar.CustomServers/mod/scripts/datatable/` | Northstar 从零售包导出的数据表；本地没有零售表可比对，标 [NS 表] |

- 本页用到的 SV 文件，Northstar 都有覆盖版（`_passives`、`_titan_health`、`_rodeo_titan`、`_weapon_utility`、`_vortex`、`smokescreen`），`diff -w` 比过：只差排版，逻辑相同。所以在 Northstar 私服上测到的 = 原版行为。武器脚本（`mp_titancore_upgrade.nut` 等）Northstar 没覆盖，MP 包和战役包两份完全相同。
- 标记：[推断] 按代码推出来、没实测；[未知] 文件里没有；[原生] 在 C++ 里，脚本只给参数；[NS 表] 见上。

**对旧页和 SCAN-1108 §3 的更正：**

| 旧说法（出处） | 更正 | 依据 |
|---|---|---|
| 虹吸冷却 12 s（`titans/MONARCH.md`） | 13 s：先等 1.0 s 再按 10 /s 回 120 | WT/`mp_titanweapon_stun_laser.txt:25–33` |
| 虹吸"打泰坦 +750，打其他 +250"（旧页、SCAN） | 数对，但每个**伤害事件**给一次；同时**扣目标护盾上限的 50 %**、减速；`pas_vanguard_shield` × 1.25 → 937 / 312 | W/`mp_titanweapon_stun_laser.nut:126–135`；W/`_weapon_utility.nut:3027, 3396–3401` |
| 齐射"6 s 回满"（旧页） | 最后一发后等 1.0 s，再 6 s → 约 7 s | WT/`mp_titanweapon_salvo_rockets.txt:86–87` |
| 多目标导弹"冷却 18 s"（旧页） | 整条 18 s，先等 2 s；一发占 1/6 条 → 一发约 3 s | WT/`mp_titanweapon_shoulder_rockets.txt:114–115` |
| 重新装填"升级 12 s"（旧页） | 12 s 是被动 Rapid Rearm（`pas_vanguard_rearm`）。核心第 2 档"Rearm and Reload"不改冷却，只把蓄力 0.5 → 0.2 s、XO-16 换弹 × 0.75 | WT/`mp_titanability_rearm.txt:103–113` |
| "高级底盘加多少血"未知（SCAN） | 最大血和当前血都 +5000；免弱点暴击 | FE/`sh_consts.gnut:460`；P/`titan_atlas_vanguard.set:49–52`；W/`mp_titancore_upgrade.nut:199–233` |
| "第 4 次起只回护盾"（SCAN） | 对；计数照样 +1 | W/`mp_titancore_upgrade.nut:269–277` |
| "升级生效时序"未测（SCAN） | 脚本：按下那一帧全部生效；核心"进行中"只有 0.5 s | W/`mp_titancore_upgrade.nut:38–40, 309–310, 334`；WT/`mp_titancore_upgrade.txt:28` |
| 用户清单把 Maelstrom、Rapid Rearm 当被动 | Maelstrom 是第 2 档升级（core5）；"Rapid Rearm"是被动 `pas_vanguard_rearm`；第 2 档的 core4 叫"Rearm and Reload"，它给的 mod 名字是 `rapid_rearm`，容易混 | L:11328–11330, 11355–11363 |

## 1. 主武器：XO-16（`mp_titanweapon_xo16_vanguard`）

**一句话：** 全自动弹丸机枪，每秒 12 发，40 发一匣；升级后可以变成电弧弹（打护盾 × 1.5）或加速器（越打越快，8 → 18 发 /s）。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 空闲 | — | — | 按住开火 → 开火 |
| 开火 | 按住开火且弹匣 > 0 | 每 1/12 s 一发弹丸（不是即时命中） | 松开 → 空闲；弹匣 0 → 换弹 |
| ADS | 按住瞄准 | 0.2 s 进 / 0.2 s 出，FOV 75 → 50；走速 × 0.40 | 松开 |
| 换弹 | 按换弹或打空 | 2.6 s（文件）/ 2.46 s（实测）；不能用开火打断 | 结束 |

**时间线（按住开火）：** 0 s 第一发（实测一帧内）→ 每 0.083 s 一发 → 3.33 s 打完 40 发 → 换弹 2.46 s（实测）。

**数值：**

| 项 | 值 | 出处 |
|---|---|---|
| 射速 | 12 /s（实测 11.7） | WT/`mp_titanweapon_xo16_vanguard.txt:89`；TF2-GAPS §4 |
| 弹匣 / 备弹 | 40 / 4040（备弹不扣） | 同上 `:91, :123, :23` |
| 伤害 对铁驭 | 45 → 40（1200 → 1800 u 线性） | 同上 `:95–98` |
| 伤害 对泰坦 | 120 → 100 | 同上 `:99–100` |
| 爆头 / 弱点 | 爆头 × 1.5（5000 u 内）；弱点暴击 × 1.5 | 同上 `:146–149, :120` |
| 弹速 | 12000 u/s，脚本发 bolt | W/`mp_titanweapon_xo16.nut:84–89` |
| 重力 | `.txt` 关掉（`bolt_gravity_enabled 0`），脚本又把 bolt 的 `gravity` 设成 −0.1；实际有没有下坠 [未知]，1800 u 内可忽略 | WT `:39`；W/`mp_titanweapon_xo16.nut:94` |
| 散布 | 腰射 2.0°，ADS 1.0°；每发 +0.2°（ADS +0.15°），最多 +2.5°（ADS +1.2°）；停火 0.15 s 后以 6.5°/s 回落 | WT `:152–169, :112–117` |
| ADS | 进 / 出 0.2 / 0.2 s，FOV 50，走速 × 0.40（100 u/s） | WT `:127–129, :31`；T0 `t0_kit` |
| 换弹 | 2.6 s（文件），`late1/2/3` 2.06 / 0.94 / 0.39；实测 2.46 s | WT `:130–136`；TF2-GAPS §4 |
| 后坐 | 弹簧 `titan_xo16`，俯仰 base −0.2 / random 0.5，左右 0.2 / 0.15；镜头几乎不动（实测 40 发俯仰最多 0.2°） | WT `:174–205`；TF2-GAPS §4 |
| 伤害标记 | `DF_STOPS_TITAN_REGEN`（打中会打断目标泰坦回盾） | WT `:41` |

**变体（升级、FD 给的 mod）：**

| mod | 谁给 | 改什么 | 出处 |
|---|---|---|---|
| `arc_rounds` 电弧弹 | 升级第 1 档 core1 | 弹匣 40 → 50，给的那一刻**当前弹匣 +10**；伤害带 `DF_ELECTRICAL` → 打泰坦护盾和所有涡旋类护盾（Legion 枪盾、Tone 粒子墙等）× 1.5；打 Ion 涡旋 / Scorch 热盾每发吸能 0.033 | WT `:383–402`；W/`mp_titancore_upgrade.nut:52–55`；SV/`_utility.gnut:3867–3873`；V/`weapons/_vortex.nut:1633–1635` |
| `battle_rifle` 加速器 | 升级第 3 档 core9 | 射速 8 /s 起，按住 3.0 s 爬到 18 /s，松开 2.15 s 回落 [原生，曲线形状未知]；伤害 × 1.25（铁驭 56.25 → 50，泰坦 150 → 125）；腰射散布 1.5°、ADS 0.5°；后坐放大（hip 1.5–2.0，ADS 0.6–1.6） | WT `:479–533` |
| `arc_rounds_with_battle_rifle` | core1 + core9 都选 | 上面两个合在一起（弹匣 50 + 加速器）；脚本先删 `arc_rounds` 再加它 | WT `:404–473`；W/`mp_titancore_upgrade.nut:243–249` |
| `rapid_reload` | 升级第 2 档 core4 | 换弹所有时间 × 0.75（2.6 → 1.95 s） | WT `:535–544` |
| `fd_balance` | FD 模式自动加 | 对泰坦伤害 × 0.8 | WT `:569–573`；SV/`_passives.gnut:265–268` |
| `fd_vanguard_weapon_1` | FD 升级 | 散布全部 × 0.5；可切换放大，FOV 25，0.2 s | WT `:551–564` |
| `fd_vanguard_weapon_2` | FD 升级 | 弱点暴击 × 2.0；ADS 时开"威胁镜"高亮 | WT `:565–568`；W/`mp_titanweapon_xo16.nut:169–193` |

**DPS（近距、全中、不算暴击）：** 对泰坦 12 × 120 = 1440；加速器满速 18 × 150 = 2700，起步 8 × 150 = 1200。

**边界情况：**
- 换弹不能用开火打断（实测）。
- 电弧弹的"+10 发"是加到当前弹匣，不管当时是不是空的。
- 电弧弹 × 1.5 是先乘再扣护盾：护盾被打穿时，溢出到血量的那部分也已经 × 1.5（SV/`_utility.gnut:3746–3747, 3801–3803`）。
- 下机时武器实体整个转给自动泰坦，mod 和弹匣都保留（SV/`mp/_titan_transfer.nut:68–99`）。

**要实测：**
- 加速器：按住开火时每发的间隔 vs 按住时长（8 → 18 /s 是线性还是别的曲线）、松开后多久回到 8 /s。
- 电弧弹对护盾的 × 1.5（打一台护盾 2500 的目标，记每发护盾掉多少）。

## 2. 进攻

### 2.1 火箭齐射（`mp_titanweapon_salvo_rockets`）

**一句话：** 按一下连发 6 枚无制导火箭，每枚先向外张开 5°，再向内收 10°，最后对准准星前方 5000 u 的点直飞；能量条必须满才能发。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 就绪 | 能量 120 / 120 | — | 按下（`charge_time 0.01`，等于立刻） |
| 连发 | 按下 | 每 1/12 s 一枚，共 6 枚（升级 Missile Racks：12 枚），每枚扣 20（Racks 扣 10） | 发完 → 冷却 |
| 冷却 | 连发结束 | 连发后 0.7 s 内不能再发（`burst_fire_delay`）；最后一发 1.0 s 后按 20 /s 回能 | 回到 120 → 就绪 |

**时间线：** 0 s 第 1 枚 → 0.083 s 一枚 → 0.42 s 第 6 枚（Racks：0.92 s 第 12 枚）→ +1.0 s 开始回能 → +6.0 s 满。按下到再次可用约 7.4 s（Racks 约 7.9 s）。

**弹道（每枚）**：第 k 枚（k 从 0 起）的方位角 a = 360° / 6 × k（Racks：30° × k），即每枚绕准星转 60°。

| 段 | 方向 | 时长 | 出处 |
|---|---|---|---|
| 张开 | 准星方向偏 5°，偏向 (right·cos a + up·sin a) | 0.20 s | W/`mp_titanweapon_salvo_rockets.nut:10–11`；W/`_weapon_utility.nut:2053–2070` |
| 过渡到收拢 | 插值 0.2 s | 0.2 s | 同上 `:12` |
| 收拢 | 准星方向偏 −10°（往对侧，交叉） | 0.10 s | 同上 `:13–14`；`_weapon_utility.nut:2056–2074` |
| 转直 | 插值到"飞向眼睛 + 准星 × 5000 u" | 0.1 s | 同上 `:15`；`_weapon_utility.nut:1941` |
| 漂移 | 随机漂移：风度 7、强度 0.96、直飞时间 0.9–1.2 s [原生，含义按键名推断] | — | WT/`mp_titanweapon_salvo_rockets.txt:24–29` |

段落的切换和插值由原生 `InitMissileExpandContract` 执行，上表的"段"是按参数名推断的 [推断]。

**数值：**

| 项 | 值 | 出处 |
|---|---|---|
| 一次几枚 / 每枚耗能 | 6 / 20（Racks 12 / 10） | WT/`mp_titanweapon_salvo_rockets.txt:103–104, 279–284` |
| 能量 | 120，满了才能发（`ammo_min_to_fire 120`） | 同上 `:77–81` |
| 回能 | 20 /s，延迟 1.0 s | 同上 `:86–87` |
| 连发射速 / 连发后间隔 | 12 /s / 0.7 s | 同上 `:131–132` |
| 弹速 | 2200 u/s（多人常数） | FE/`sh_consts.gnut:459`；W/`mp_titanweapon_salvo_rockets.nut:30` |
| 直击伤害 | 250（近远相同；没有单独的对泰坦值，[推断] 对泰坦也是 250） | WT `:105–108` |
| 爆炸 | 对铁驭 100 / 对泰坦 250；内半径 60，外半径 120 | WT `:72–73, :109–110` |
| 寿命 | 10 s，到时空爆 | WT `:18–19` |
| 每轮对泰坦最大伤害 | 6 × (250 + 250) = 3000 [推断：直击和爆炸都吃]；Racks 6000 | 计算 |
| FD | `fd_balance` 全部伤害 × 0.8 | WT `:285–291` |

**边界情况：**
- 能量没满按不出（不是按比例发）。
- 连发进行中不能用重新装填（W/`mp_titanability_rearm.nut:55–56`，文件头还留着"TODO: FIX REARM WHILE FIRING SALVO ROCKETS"）。但"dash 能量没满就可以"那条判断排在后面（`:63–64`），会把它改回可以——所以 dash 用过时，连发中也能按重新装填 [推断：漏洞]。
- 第 3 档选了多目标导弹后，齐射被整把换掉（见 2.2）。

**要实测：**
- 6 枚火箭每帧的位置（张开、收拢、转直的真实时刻和角度；漂移的幅度）。
- 6 枚是否都吃"直击 + 爆炸"两次伤害（对静止泰坦记每枚的伤害事件）。

### 2.2 多目标导弹（`mp_titanweapon_shoulder_rockets`，第 3 档 core7 换上）

**一句话：** 按住进攻键扫描，锁定重甲目标（每 0.3 s 加一把锁，同一目标最多 6 把），松开按锁数发追踪导弹；没锁就直接发无制导的。

**怎么换上：** 第 3 次用核心且选了 core7 时，删掉齐射，换上这把武器，mod 为 `upgradeCore_Vanguard`（之前选了 Missile Racks 就用 `upgradeCore_MissileRack_Vanguard`），FD 下保留 `fd_balance`。冷却进度照搬：新武器的"已用比例" = 1 − 旧齐射能量 / 120（W/`mp_titancore_upgrade.nut:183–197`）。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 可用 | 已用比例 ≤ 0.8 才能切到这把武器 | — | 按住 |
| 扫描 | 按住（只在按住时搜索，`smart_ammo_only_search_on_charge 1`） | 30° 锥、4000 u 内找"大型"目标（重甲）；第一把锁也要等 0.3 s；每把锁 0.3 s；同一目标最多 6 把（Racks 12）；最多 8 个目标；泰坦挡视线；隐身目标不锁 | 松开 → 发射 |
| 发射 | 松开 | 每把锁一枚追踪导弹，连发 12 /s；每发已用比例 + 1/6（Racks 1/12）；锁总数上限 6（Racks 12） | 发完 → 冷却 |
| 无锁发射 | 松开时没锁 | 走齐射那套"张开收拢"弹道发无制导导弹，枚数 = 剩余格数 [原生连发次数规则不清，见要实测] | — |
| 冷却 | 发射后 | 等 2 s，然后已用比例按"整条 18 s"往回走 | 比例回 0 |

**数值：**

| 项 | 值 | 出处 |
|---|---|---|
| 冷却类型 | `charged_shot`：整条 18 s，延迟 2 s；一格（1/6）约 3 s | WT/`mp_titanweapon_shoulder_rockets.txt:72, 113–117` |
| 每发占比 | 1 / `smart_ammo_max_targeted_burst`（6；Racks 版不改 → 12） | 同上 `:270, 332`；W/`mp_titanweapon_shoulder_rockets.nut:93–94, 110–114` |
| 锁定 | 角度 30°、距离 4000、锁时 0.3 s、新目标延迟 0.3 s（第一目标也算）、解锁去抖 0.2 s、类型 `large` | 同上 `:262–274, :330–348` |
| 同一重甲目标最多锁 | 6（Racks 12） | 同上 `:274, 333` |
| 最多目标数 | 8 | 同上 `:268` |
| 切换门槛 | 已用比例 ≤ 0.8 | W/`mp_titanweapon_shoulder_rockets.nut:38–41` |
| 弹速 / 追踪转速 | 2200 / 550（= 2200 / 1000 × 250） | W 同上 `:60–72`；FE/`sh_consts.gnut:459` |
| 弹道 | 张开 5°、0.2 s，收拢 −5°、0 s，转直 −0.2 | W 同上 `:14–20, 30–36` |
| 伤害 | 直击 250 / 对泰坦 350；爆炸 100 / 350；半径 120 | WT `:78–87` |
| 一轮满锁对泰坦 | 6 × (350 + 350) = 4200 [推断] | 计算 |

**边界情况：**
- 重新装填会把已用比例清 0（W/`mp_titanability_rearm.nut:21–22`）。
- 只锁重甲（"Hold Rocket Salvo to lock onto heavily armored targets"，L:11371）；对铁驭只能无锁乱发。

**要实测：**
- 锁定进度随时间（`weapon.SmartAmmo_GetTargets()` 每个目标的 `fraction`）；一个目标 6 把锁要多久（推断 0.3 + 5 × 0.3 ≈ 1.8 s）。
- 无锁时一次发几枚（`SetWeaponBurstFireCount` 的原生含义不清）。

## 3. 防御：能量虹吸（`mp_titanweapon_stun_laser`）

**一句话：** 打出一束细光束，只打中准星前第一个目标；打中敌人：给自己回护盾（重甲 750，其他 250）、扣对方护盾上限的 50 %、减速；升级后能给友方泰坦回盾、变成范围效果。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 就绪 | 能量 120 / 120 | — | 按下 |
| 出手 | 按下 | 蓄力键 `charge_time 3.0`、`charge_require_input 1`、`charge_end_forces_fire 1`（和 Ion 激光射击完全一样的键）；实际按下到出手多久 [未知，原生] | 发射 |
| 发射 | — | 一次 `ShotgunBlast(1 发)`：4000 u、锥半角 = 散布 1.5° 的一半 = 0.75°（搜索时 × 1.1）；只打第一个可见实体；没打中就发一颗打墙的子弹 | 冷却 |
| 冷却 | 发射 | 1.0 s 后按 10 /s 回 120 | 满 → 就绪 |

**时间线：** 按下 → 出手（[未知]）→ 命中当帧：回盾、扣对方盾、减速开始 → +1.0 s 开始回能 → +12 s 满。发射到可再用 13 s。

**命中规则（每个伤害事件跑一次，W/`mp_titanweapon_stun_laser.nut:71–139`、W/`_weapon_utility.nut:3021–3159`）：**

| 目标 | 伤害 | 给自己 | 对目标 |
|---|---|---|---|
| 自己 | 0 | — | — |
| 友方泰坦 | 0 | — | 有 Energy Transfer：目标护盾 +750（**检查的是目标身上有没有 `pas_vanguard_shield`**，有就 × 1.25） |
| 友方非泰坦 | 0 | — | — |
| 敌方重甲（泰坦等） | 直击 100，爆炸 100 | 护盾 +750（自己有 `pas_vanguard_shield` → 937） | 护盾 − 上限 × 50 %（2500 → −1250）；减速见下 |
| 敌方其他 NPC / 玩家 | 直击 20，爆炸 20；机械类 NPC × 2.05，人类 × 0.99 | 护盾 +250（→ 312） | 减速 / 硬直见下 |

减速和硬直：

| 目标 | 效果 | 出处 |
|---|---|---|
| NPC 泰坦 | 移速减 0.30、转向减 0.20，持续 2.5 s（最后 1.0 s 渐退）；命中率 × 0.5，2.5 s；护盾 −50 % 上限 | W/`_weapon_utility.nut:111–112, 3132–3139, 3412–3419` |
| 玩家泰坦 | 护盾 −50 % 上限；驾驶舱 EMP 画面（强度 × 0.1）；移速减 0.50、转向减 0.35，持续 1.5 + f 秒、最后 f 秒渐退（f 由命中点到目标中心距离定：≤ 64 u 为 1，≥ 128 u 为 0） | 同上 `:109–110, 3422–3469, 2423–2436`；FE/`sh_consts.gnut:711–715` |
| 铁驭玩家 | EMP 画面（× 0.1），减速同上 | 同上 |
| 步兵、幽灵、潜行者、死神 | 播 `ACT_STUNNED` 硬直动画（可打断的才播） | 同上 `:3051–3079` |
| 机械类 NPC（幽灵、无人机等） | 减速 0.30 / 0.20，2.5 s；伤害 × 2.05 | 同上 `:3140–3146` |
| 飞行无人机、炮艇 | 走 EMP 重启流程 | 同上 `:3085–3098` |

"减 0.30"是状态效果强度，[推断] 意思是速度 × (1 − 0.30)。

**数值：**

| 项 | 值 | 出处 |
|---|---|---|
| 能量 / 每次 | 120 / 120 | WT/`mp_titanweapon_stun_laser.txt:23–30` |
| 回能 | 10 /s，延迟 1.0 s → 13 s | 同上 `:32–33` |
| 射程 | 4000（伤害近远都是 4000） | 同上 `:52–53`；W/`_weapon_utility.nut:502–503` |
| 直击 | 20 / 100（铁驭 / 泰坦） | 同上 `:54–60` |
| 爆炸 | 20 / 100，半径 50（内外相同） | 同上 `:61–64` |
| Energy Field 爆炸半径 | 350（内外相同，满伤害） | 同上 `:335–342, 364–371` |
| 回盾 | 重甲 750 / 其他 250；× 1.25 取整 → 937 / 312 | W/`mp_titanweapon_stun_laser.nut:128–134` |
| 扣盾 | 目标护盾上限 × 0.5 | W/`_weapon_utility.nut:3396–3401` |
| 射速上限 | 1.5 /s（实际被能量限制） | WT `:138` |
| 不吃暴击 | `critical_hit 0` | WT `:66` |

**边界情况：**
- 一次命中会跑几个伤害事件 [未知]：脚本先 `TakeDamage` 一次（直击），武器本身又带爆炸参数（`explosionradius 50`），原生爆炸可能再打一次。每个事件都回一次盾、扣一次盾。如果是两次：打泰坦一次回 1500，扣对方 100 % 上限。**要实测。**
- 回盾有上限（到满为止）；扣盾到 0 为止。
- Energy Field：光束打中点的 350 u 内所有目标各算一次 → 打一群可以回很多盾。
- Energy Transfer 的 × 1.25 检查的是友方目标的被动，不是 Monarch 自己的（`:94` 用的是目标的 soul）——[推断] 是 bug，HSD 照原版做或改成看自己，要决定。
- Energy Transfer 回调里报给统计的"回了多少"算错了（`:98` 算的是"还差多少"），不影响玩法。
- 友军伤害本来不算，虹吸单独放行，为的是 Energy Transfer（SV/`mp/_base_gametype.gnut:296`）。
- 不是泰坦（没有 soul）的使用者不回盾。

**要实测：**
- 按下到光束出现的时间；按住和点按有没有区别（3 s 蓄力键的作用）。
- 打一台护盾 2500 的敌方泰坦一次：伤害事件数（`HSDDIAG KDMG` 行数）、自己护盾增量、对方护盾减量。
- 对方移速 / 转速状态值随时间（`StatusEffect_Get( foeSoul, eStatusEffect.move_slow / turn_slow )`）。
- 能量曲线：发射后 offhand1 的弹匣值随时间（验证 1 s 延迟 + 12 s）。

## 4. 战术：重新装填（`mp_titanability_rearm`）

**一句话：** 0.5 s 蓄力后，把进攻、防御的能量和 dash 能量一次回满。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 就绪 | 能量 200 / 200 | — | 按下且"有东西可回"（见下） |
| 蓄力 | 按下 | 0.5 s（core4 后 0.2 s），不用按住（`charge_require_input 0`） | 蓄满自动发 |
| 生效 | 蓄满那一帧 | 进攻武器弹匣 = 上限；如果进攻是"蓄力类"（多目标导弹）就把已用比例清 0；防御武器弹匣 = 上限；玩家 dash 能量 = 100；自己能量清 0（跳过开火动画） | 冷却 |
| 冷却 | 生效 | 立即按 11.333 /s 回（`pas_vanguard_rearm`：16.66 /s） | 满 → 就绪 |

**能不能按（W/`mp_titanability_rearm.nut:43–78`）：** 进攻和防御都满 → 不能；进攻连发进行中 → 不能；但进攻是蓄力类且已用比例 > 0 → 能；dash 能量 < 100 → 能（这条最后判，优先级最高）。不能时弹提示、播空响。

**时间线：** 0 s 按下 → 0.5 s（0.2 s）回满 → 冷却 17.65 s（被动 12.0 s）→ 按下到再可用约 18.15 s（被动 12.5 s；core4 再减 0.3 s）。

**数值：**

| 项 | 值 | 出处 |
|---|---|---|
| 能量 / 每次 | 200 / 200，`ammo_instant` | WT/`mp_titanability_rearm.txt:23–29` |
| 回能 | 11.333 /s，无延迟 → 17.65 s | 同上 `:31–32` |
| `pas_vanguard_rearm` | 16.66 /s → 12.0 s | 同上 `:103–107` |
| 蓄力 | 0.5 s；`rapid_rearm`（core4）0.2 s | 同上 `:58–63, 109–113` |
| dash 回满 | `Server_SetDodgePower( 100.0 )`，只对玩家 | W/`mp_titanability_rearm.nut:28–31` |

**边界情况：**
- 不回：主武器子弹、电烟、核心、自己。
- 脚本里"只在有 rapid_rearm 时才回 dash"的判断被注释掉了，所以**任何时候都回 dash**（`:29, 61–65`）。
- 下机后自动泰坦也能用（NPC 走同一个函数），但不回 dash。

**要实测：**
- 按下到回满的时间（offhand0 / offhand1 弹匣、`player.GetDodgePower()` 跳变的时刻）。
- 冷却曲线（offhand2 弹匣值随时间）。

## 5. 核心：升级核心（`mp_titancore_upgrade`）

**一句话：** 核心充满后按下：护盾立刻回满，泰坦按"这是第几次"永久获得一项升级；第 4 次起只回护盾。

### 5.1 状态机

计数器 `upgradeCount` 是**泰坦灵魂（soul）上的网络变量**，初值 0（V/`_remote_functions_mp.gnut:889`）。

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 充能 | 生成 / 上次用完 | 核心表涨（规则见下） | 满 |
| 可用 | 满且 `CheckCoreAvailable` 通过 | — | 按下 |
| 生效（同一帧） | 按下 | ① 护盾 = 上限；② 按 `upgradeCount` 给升级（表 5.3）；③ `upgradeCount` + 1；④ 机体 bodygroup `states` = 1（外观变）；⑤ 播语音和横幅 | 进入"进行中" |
| 进行中 | — | 0.5 s（`core_duration`）；给 `PAS_FUSION_CORE`（只影响驾驶舱特效） | 0.5 s 后 / 死亡 / 下机 / 弹射 |
| 结束 | — | 核心表重新开始充 | → 充能 |

`CheckCoreAvailable`（W/`sh_titancore_utility.gnut:178–209`）：是泰坦；没在做上下机这类动作；没在处决；没被挂在别的东西上；有 soul；没在弹射；核心表满。

核心表怎么涨：playlist `titan_core_from_titan_damage` ≠ 0 时按伤害积分（Energy Thief × 1.10）；否则按时间，`core_build_time` 100 s（V/`_utility_shared.nut:3211–3216`；W/`sh_titancore_utility.gnut:212–247`；WT/`mp_titancore_upgrade.txt:26`）。

### 5.2 时间线

- 0 s（按下那一帧，服务端）：线程 `UpgradeCoreThink` 先跑到第一个 `wait` 为止——回满护盾；然后同一帧里给升级、计数 + 1（W/`mp_titancore_upgrade.nut:38–40, 297–335`）。
- 0 s：客户端驾驶舱播"护盾上升"粒子；横幅显示升级名（`ServerCallback_VanguardUpgradeMessage`）。
- 0.5 s：核心结束，表重置。
- 没有"延迟生效"：所有改动都在按下那一帧。

### 5.3 每次给什么

选项来自出战装备：passive4（第 1 档：core1 / 2 / 3）、passive5（第 2 档：core4 / 5 / 6）、passive6（第 3 档：core7 / 8 / 9）。类型见 [NS 表] `titan_passives.csv:44–52`。默认装备是 core1 / core4 / core7（[NS 表] `default_titan_loadouts.csv:8`）。脚本按 `if / else if` 查，同一档只给一项。

| `upgradeCount` 按下时 | 选项 | 名字 | 改什么 | 出处 |
|---|---|---|---|---|
| 0 | core1 | Arc Rounds 电弧弹 | 主武器 + `arc_rounds`，当前弹匣 + 10（见第 1 节） | W/`mp_titancore_upgrade.nut:44–64` |
| 0 | core2 | Missile Racks 导弹架 | 进攻 + `missile_racks`：齐射 12 枚、每枚 10 能量 | 同上 `:65–80`；WT/`mp_titanweapon_salvo_rockets.txt:279–284` |
| 0 | core3 | Energy Transfer 能量转移 | 防御 + `energy_transfer`：打友方泰坦给它 +750 护盾 | 同上 `:81–96`；第 3 节 |
| 1 | core4 | Rearm and Reload | 战术 + `rapid_rearm`（蓄力 0.2 s），主武器 + `rapid_reload`（换弹 × 0.75） | 同上 `:100–126` |
| 1 | core5 | Maelstrom 漩涡 | 电烟 + `maelstrom`：对铁驭 45 → 90 /s，对泰坦 450 → 1350 /s | 同上 `:127–142`；W/`mp_titanability_smoke.nut:84–97` |
| 1 | core6 | Energy Field 能量场 | 防御 + `energy_field`（爆炸半径 50 → 350）；已有 Energy Transfer 就换成 `energy_field_energy_transfer`（两者合一） | 同上 `:143–169`；WT/`mp_titanweapon_stun_laser.txt:335–383` |
| 2 | core7 | Multi-Target Missiles 多目标导弹 | 进攻换成多目标导弹（见 2.2） | 同上 `:173–198` |
| 2 | core8 | Superior Chassis 高级底盘 | 见下 | 同上 `:199–234` |
| 2 | core9 | XO-16 Accelerator 加速器 | 主武器 + `battle_rifle` + `battle_rifle_icon`；已有电弧弹就换成 `arc_rounds_with_battle_rifle` | 同上 `:235–267` |
| ≥ 3 | — | — | 什么都不给，只回护盾、播"护盾补满"语音；计数照样 + 1 | 同上 `:269–277` |

**高级底盘（core8）细节：**

| 情况 | 做什么 | 出处 |
|---|---|---|
| 玩家、没毁灭 | 记下缺的血 m；给玩家设置加 mod `core_health_upgrade`（`health 5000++ [$mp]`：10000 → 15000）；血 = max(新上限 − m, 5000)，等于当前血 + 5000；把 mod 记进 soul 的装备（下机后自动泰坦、脱离毁灭时用） | W/`mp_titancore_upgrade.nut:208–218`；P/`titan_atlas_vanguard.set:49–52` |
| 玩家、毁灭中 | 只把血设成当前上限（毁灭状态的上限 = 毁灭血 2500，即回满毁灭血条）；**不加上限、不记 mod** | 同上 `:219–222`；SV/`titan/_titan_health.gnut:607, 634` |
| NPC、没毁灭 | 上限 + 5000，血 + 5000 | 同上 `:224–231`；FE/`sh_consts.gnut:460` |
| NPC、毁灭中 | 不加 | 同上 |
| 所有情况 | `soul.SetPreventCrits( true )`：此后不吃弱点暴击 | 同上 `:232–233` |

**Maelstrom 细节：** 给的是电烟槽位（`OFFHAND_INVENTORY`）的武器。如果那时身上没有电烟武器，mod 不会加上；以后系统新发一个电烟时，若 `upgradeCount ≥ 2` 且有 core5，会补上 mod（SV/`earn_meter/sv_earn_meter.gnut:470–497`）。电烟本身：内半径 320、外半径 375，1.0 s 后开始伤害，每 0.1 s 一跳，持续 5 s（W/`mp_titanability_smoke.nut:84–98`；SV/`superbar/smokescreen.nut:17, 185–188, 209–235`）。

### 5.4 存续

| 事件 | 结果 | 出处 |
|---|---|---|
| 下机 / 再上机 | 计数在 soul 上，跟着走；武器是整件实体转移，mod 保留；血量上限转移（`TransferHealth`）；下机时自动泰坦用玩家当前设置 mod 生成，`core_health_upgrade` 跟过去，再上机时用回 [推断] | SV/`mp/_titan_transfer.nut:68–99, 251–256, 281–290, 384–412, 573–585` |
| 泰坦被毁 / 换新泰坦 | 新 soul，计数从 0 开始，所有升级没了 | soul 是每台泰坦一个 |
| soul 死亡 | 机体 bodygroup `states` = 2（残破外观） | SV/`titan/_titan_health.gnut:67, 1060–1072` |
| 核心进行中下机 / 弹射 / 死亡 | 进行中只有 0.5 s；升级已在第 0 帧生效，不会撤回 | W/`mp_titancore_upgrade.nut:299–334` |

### 5.5 数值

| 项 | 值 | 出处 |
|---|---|---|
| 充能 | `core_build_time` 100 s（时间模式） | WT/`mp_titancore_upgrade.txt:26` |
| 进行中 | 0.5 s，蓄力 0 | 同上 `:27–28` |
| 回盾 | 到 `GetShieldHealthMax()`（默认 2500；FD 护盾升级后 3750） | W/`mp_titancore_upgrade.nut:310`；SV/`_passives.gnut:291–294` |
| 高级底盘 | +5000 | FE/`sh_consts.gnut:460` |
| 最多有效升级 | 3 次（"Apex Titan"第 4 档被动未实现，L:11336–11338） | — |

### 5.6 边界情况

- NPC 自动泰坦也能用核心并升级（`OnWeaponNpcPrimaryAttack_UpgradeCore`），升级看的是 soul 的被动，所以下机后的自动泰坦照样升级。
- 档位只按次数走：比如 passive5 是空的，第 2 次用就什么都不给，但计数照样 + 1，第 3 次照常给第 3 档。
- 第 1 档选 core2（导弹架）再选 core7：多目标导弹用 12 枚版本。
- 第 1 档 core3 + 第 2 档 core6：防御变成"范围 + 友方回盾"。
- 第 1 档 core1 + 第 3 档 core9：电弧弹 + 加速器。
- FD 的 Apex Titan 会在出生时**额外**随机给一项别的第 1 档升级，不加计数（见第 7 节）。

### 5.7 要实测

- 每次按核心那一帧前后：护盾、`player.GetMaxHealth()` / `GetHealth()`、`soul.GetTitanSoulNetInt( "upgradeCount" )`、主武器 / 进攻 / 防御 / 电烟的 `GetMods()`——确认"同一帧生效"。
- 高级底盘：受伤后用（例如 7000 / 10000），看是否变成 12000 / 15000；毁灭状态下用，看是否只回满毁灭血。
- 下机再上机后：最大血是否还是 15000、`GetPlayerSettingsMods()` 里是否还有 `core_health_upgrade`。
- 第 4 次：只回盾，计数到 4。

## 7. 专属被动和 FD 升级

### 7.1 Monarch 专属被动（passive2，四选一，[NS 表] `titan_passives.csv:40–43`）

默认装备是 Shield Amplifier（[NS 表] `default_titan_loadouts.csv:8`）。

| 被动 | 名字 | 改什么 | 数值 | 出处 |
|---|---|---|---|---|
| `pas_vanguard_shield` | Shield Amplifier | 虹吸回盾 × 1.25；也是一个空的设置文件 mod（不改属性）；对 Energy Transfer 的 × 1.25 看的是**目标**有没有这个被动 | 750 → 937，250 → 312 | W/`mp_titanweapon_stun_laser.nut:94, 132–133`；P/`titan_atlas_vanguard.set:44–47`；FE/`sh_passives.gnut:329`；L:11324–11326 |
| `pas_vanguard_coremeter` | Energy Thief | 核心积分 × 1.10；泰坦处决换成 `execution_vanguard_kit`，处决后偷一块电池 | × 1.10 | SV/`titan/_titan_health.gnut:987–988`；SV/`melee/_melee_synced_titan.gnut:255–256, 1019–1024`；L:11320–11322 |
| `pas_vanguard_rearm` | Rapid Rearm | 重新装填回能 11.333 → 16.66 /s | 17.65 → 12.0 s | WT/`mp_titanability_rearm.txt:103–107`；SV/`_passives.gnut:879–884` |
| `pas_vanguard_doom` | Survival of the Fittest | 毁灭状态下捡电池：先脱离毁灭（1 段）并把血设为 1，再按普通电池加 2500 × 0.5 = 1250（强化电池 × 2.0 = 5000）→ 约 1251 / 5001。没有这个被动时，普通电池在毁灭状态只加毁灭血，强化电池才脱离毁灭。（护盾回满、核心 +20 % 是所有电池都有的） | 见左 | SV/`rodeo/_rodeo_titan.gnut:1705–1709, 1744–1778` |

未实现：`GEAR_VANGUARD_UPGRADE` "Apex Titan：(Not Yet Implemented) Enables a fourth and final upgrade"（L:11336–11338），不在被动表里。

### 7.2 升级核心的九项

见 5.3。

### 7.3 FD（Aegis）升级

只在 playlist `aegis_upgrades` = 1 时生效（SV/`_passives.gnut:888–891`）。等级按 [NS 表] `unlocks_fd_titan_level.csv:4–22`（`titan_fd_upgrades.csv` 的 `unlockLevel` 列是另一套数 2 / 4 / 6 / 8 / 10 / 12 / 14，以 unlocks 表为准）。FD 下还**总是**给主武器和进攻加 `fd_balance`（× 0.8，SV/`_passives.gnut:265–273`）。

| 等级 | 升级 | 改什么 | 出处 |
|---|---|---|---|
| 2 | Energized Smoke | 自己的电烟打到自己时不扣血，每跳（0.1 s）+35 护盾（≈ 350 /s）；需要主武器带 `fd_vanguard_utility_1` | SV/`_passives.gnut:279–284`；W/`mp_titanability_smoke.nut:142–173` |
| 5 | Chassis Upgrade | 设置 mod `fd_health_upgrade`：血 +2500 | SV/`_passives.gnut:252–254`；P/`titan_atlas_vanguard.set:53–56` |
| 8 | XO-16 Sniper Configuration | `fd_vanguard_weapon_1`：散布 × 0.5，可切换放大 FOV 25 | SV/`_passives.gnut:295–300`；WT/`mp_titanweapon_xo16_vanguard.txt:551–564` |
| 11 | Energized Smoke Lvl 2 | 友方泰坦在 Monarch 的电烟里也每跳 +35 | SV/`_passives.gnut:285–290`；W/`mp_titanability_smoke.nut:144` |
| 14 | Shield Upgrade | 护盾上限 × 1.5（2500 → 3750） | SV/`_passives.gnut:291–294` |
| 17 | XO-16 Critical Hit | `fd_vanguard_weapon_2`：暴击 × 2.0，ADS 威胁镜 | SV/`_passives.gnut:301–306`；WT `:565–568` |
| 20 | Apex Titan | 出生时按已选第 1 档，从另外两项里 50 / 50 随机再给一项（给电弧弹时弹匣直接填满）；不加计数 | SV/`_passives.gnut:307–388`；L:11665 |

## 8. 实测

本地私服 `mp_lf_stacks`，运行 `20261108_141857_kit_c`（分析 `an_kit_bc.py`）。升级路线用 `hsd_kit_pas monarch 4/5/6 <被动>` 在出生前改装备栏。护盾、血量读服务端（10 Hz）。

### 8.1 升级核心

| 路线（第 1 / 2 / 3 档） | 第 1 次 | 第 2 次 | 第 3 次 | 第 4 次 |
|---|---|---|---|---|
| A：电弧弹 / 漩涡 / 高级底盘 | XO-16 加 `arc_rounds`，弹匣 40 → 50 | （漩涡不加在主武器和三个技能上，在其他槽） | 设置文件加 `core_health_upgrade`：**血上限 10000 → 15000** | 只回护盾 |
| B：导弹架 / 快速装填 / 多目标导弹 | 火箭齐射加 `missile_racks` | XO-16 加 `rapid_reload`，重新装填加 `rapid_rearm` | 火箭齐射换成 `upgradeCore_MissileRack_Vanguard`（多目标导弹） | 只回护盾 |
| C：能量转移 / 能量场 / 战斗步枪 | 虹吸加 `energy_transfer` | 虹吸改成 `energy_field_energy_transfer` | XO-16 加 `battle_rifle`、`battle_rifle_icon` | 只回护盾 |

- **生效时刻：** 升级计数、护盾、mod 都在按键后第一个服务端帧（≤ 0.1 s）里变好。没有蓄力、没有延迟。
- **护盾：** 每次（含第 4 次）都把护盾从 0 回到 2500。
- **高级底盘的血：** 上限 +5000（10000 → 15000）。当前血 = max(新上限 − 原来缺的血, 5000)。这次因为测试把上限临时设成 50000，缺 43000，所以当前血落到保底的 5000，正好验证了保底值。
- **下机再上机：** 高级底盘的 15000 上限和 `core_health_upgrade` 都还在。
- **测试副作用（不是游戏行为）：** 高级底盘的脚本把 `core_health_upgrade` 追加到泰坦装备的 `setFileMods` 上；本地测试里这份装备就是默认装备表本身，所以后面两条路线出生时也带着它。真实对局里每个玩家有自己的装备副本。

### 8.2 能量虹吸（打冻结的敌方泰坦，对方护盾 2500）

- 一次命中只有**一个**伤害事件：对方掉 100 血（伤害），对方护盾 2500 → 1150（−1250 = 上限的 50 %，再 −100 伤害被护盾吃掉的部分）。
- 自己护盾 0 → **937**（750 × 1.25，默认带 `pas_vanguard_shield`）。
- 对方 `move_slow` 0.298（约 0.3），保持约 2.0 s，然后 1.0 s 内淡出。
- 打步兵那一项没打中（靶子是 5000 血的冻结步兵，虹吸射线没有记到伤害），`+250` 没有实测。

### 8.3 重新装填

- 按键后约 0.55 s 开始蓄力，约 0.5 s 蓄满（比例 0.45 → 0.96 / 0.25 s），按键后约 1.2 s 生效：进攻、防御弹药 0 / 31 → 120 / 120，dash 能量 0.5 → 100，同一帧。
- 之后重新装填自己的弹药从 2 开始，每 0.25 s 约 +3（约 11.3 /s，200 要约 17.6 s）。


### 8.4 火箭齐射的真实弹道（11-13 补测，`tf2-kits-measure`）

运行 `runtime/data/20261113_015656_km_monarch`（私有仓库 HSD-RawData），客户端每帧（约 144 Hz）记每枚火箭的位置，分析 [measure/an_expand.py](measure/an_expand.py)。平地、视线水平、朝 +x，4 轮 × 6 枚。"径向角" = 速度方向偏离准星线、朝这枚火箭自己方位的角度（+ 向外，− 向内）。时刻从这枚火箭出现算起。

| 段 | 时刻 | 径向角 | 位置（离准星线 / 前方） |
|---|---|---|---|
| 外张 | 0 – 0.17 s | +5.2°（单枚 +4.6 … +6.0°，`applyRandSpread` 的随机） | 0.17 s 时外偏 34 u |
| 转向收拢 | 0.17 – 0.40 s | 从 +5° **线性**转到 −10°（约 0.23 s） | 0.25 s 外偏最大 40 – 55 u，前方约 550 u |
| 收拢 | 0.40 – 0.47 s | −10°（−8.8 … −10.4°） | 0.44 s 穿过准星线（前方约 970 u） |
| 转直 | 0.47 – 0.59 s | 从 −10° 转回 0° | 0.58 s 内偏最大 33 – 39 u（前方约 1280 u） |
| 直飞 | 0.59 – 0.83 s | +0.6 … +0.8°（对准"眼睛 + 准星 × 5000 u"那一点，所以是慢慢收回准星线） | 内偏从 34 u 慢慢减小 |
| 漂移 | 0.83 s 起 | 随机偏转，1.0 s 时 +3 … +9° | 本图 2270 u 处有墙，漂移只看到 0.2 s |

- 速度全程 2200 u/s，转向时只差 1 %（2180），转向只改方向不改速率。
- 6 枚的方位角 0°、60°、120°、180°、−120°、−60°（右、右上、左上、左、左下、右下），间隔 0.083 s（12 /s）；连发 0.43 s 发完。
- 各段时长和脚本参数（外张 0.20、过渡 0.2、收拢 0.10、转直 0.1）大体对上，但外张实测只有约 0.17 s。客户端看到的是本地预测的火箭（前 0.1 s）接服务端的火箭，时刻可能差一两帧。**HSD 照做：** 0.17 / 0.23 / 0.07 / 0.12 s 四段，用线性插值方向。
- **伤害：** 700 u 外的冻结泰坦，6 枚中 4 枚打中，每枚只有**一个**伤害事件 250（冲击类），没有另外的爆炸事件。所以一轮对泰坦最多 6 × 250 = 1500，不是第 2.1 节推断的 3000。

### 8.5 多目标导弹的锁定和发射（11-13 补测）

同一次运行，路线 core1 / core5 / core7（普通版）和 core2 / core4 / core7（带导弹架）。分析 [measure/an_lock.py](measure/an_lock.py)，锁定数读客户端 `SmartAmmo_GetTargets()` 的 `fraction`（就是锁的把数）。靶子是 900 u 外正前方的冻结泰坦。

| 项 | 普通版 | 导弹架版 |
|---|---|---|
| 按下到目标进列表 | 0.37 s | 0.37 s |
| 第 1 把锁 | 0.417 s | 0.417 s |
| 之后 | 每 0.15 s 一把（6.67 把 /s，连续增长，不是跳变） | 同左 |
| 上限 | 6 把（1.16 s 锁满） | 12 把（2.06 s 锁满） |
| 按住 0.8 s 松手 | 3 把 → 3 枚 | 3 把 → 3 枚 |
| 第二个靶子（同距离、右偏 300 u = 18.4°） | 一直没锁上 | 一直没锁上 |
| 没有目标，按住 0.6 s 松手 | 5 枚 | 11 枚 |
| 每枚对泰坦 | 350，一个伤害事件 | 350 |

- 锁的节奏：第 1 把等 0.42 s，之后 0.15 s 一把。设置里 `smart_ammo_targeting_time` 0.3 s 对不上实测的 0.15 s；按实测做。
- 锁定锥：偏 18.4° 的靶子锁不上，半角 < 18°。设置的 30° 按全角算，半角 15° 和实测相符 [推断]。
- **没有锁时**发的枚数比满格少 1（5 / 11），弹道和火箭齐射完全一样：外张 +5°、收拢 −10°、再转直（`an_expand.py mt_none`）。
- **有锁时**：前 0.15 s 外张 +5.3°，然后追踪；900 u 外的靶子 0.38 – 0.41 s 打中。发射间隔 0.083 – 0.09 s（12 /s）。

## 9. 能脱离 TF2 照做的 / 还缺的

**能照做的（规则 + 数都有）：**
- 升级核心的状态机：计数、三档选项、同帧生效、回盾、第 4 次起只回盾、存续规则。
- 九项升级的参数包（电弧弹、导弹架、能量转移、快速装填、漩涡、能量场、多目标导弹的锁定参数、高级底盘 +5000 和免暴击、加速器的射速端点和伤害倍率）。
- XO-16 的射速、弹匣、伤害距离、散布、ADS、换弹（用实测 2.46 s）。
- 火箭齐射的枚数、方位角规则、张开 / 收拢角度和时长、弹速、伤害、冷却。
- 虹吸的目标分类、回盾量、扣盾比例、各类目标的减速参数、冷却。
- 重新装填：能不能按的判断、回什么、蓄力和冷却。
- 四个被动、七个 FD 升级。

**还缺的（要实测或要拍板）：**
- 虹吸一次命中的伤害事件数（决定回盾 / 扣盾是否翻倍）；按下到出手的时间。
- ~~齐射的原生漂移和"张开 → 收拢 → 转直"的真实曲线。~~ 11-13 补测（§8.4）：曲线测到；漂移只测到开始的 0.2 s（0.83 s 起，1.0 s 时 3 – 9°），远距离的漂移幅度还缺。
- 加速器射速爬升 / 回落曲线。
- ~~多目标导弹的锁定进度曲线、无锁时的枚数。~~ 11-13 补测（§8.5）：0.42 s 第 1 把，之后每 0.15 s 一把，上限 6 / 12；无锁 5 / 11 枚。
- 状态效果"减 0.30"的确切含义（× 0.7 还是别的）。
- 高级底盘在下机再上机后是否保留（代码路径推断保留）。
- 要拍板：Energy Transfer × 1.25 看目标的被动（原版 bug）——照抄还是改。

**11-08 实测补上的（见第 8 节）：** 三条升级路线 9 项都在按键当帧生效；每次回满护盾；高级底盘 +5000（10000 → 15000）、保底 5000、下机后保留；虹吸一次命中只有一个伤害事件（自己 +937、对方护盾 −1250、对方减速 0.3 约 3 s）；重新装填按键后约 1.2 s 回满进攻、防御和 dash。**仍缺：** 虹吸打步兵的 +250；齐射弹道曲线。
