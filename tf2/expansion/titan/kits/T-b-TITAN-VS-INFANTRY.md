# 泰坦打步兵：踩、砸、拳、撞（T-b）

2026-11-08，读脚本和设置文件写成（S 步）。实测（R 步）由主会话的 `kit_d` 一批做，第 6 节列了要找的伤害源编号和要记的量。

## 先说结论

- **踩人有，是原生代码做的。** 伤害源 `damagedef_titan_step`（编号 5，讣告"被踩死"）。脚本里只有参数：伤害 `titan_footstep_damage`（默认 5000，说明写"每秒"）、泰坦至少要以 50 u/s 移动、受害者的包围盒要碰到泰坦高度最下面的 15 %、玩家泰坦每走 100 u 判一次（不看时间），NPC 泰坦每 1 s 且每 150 u 判一次。5000 是一次给还是按秒摊，文件里看不出。对 100 血的铁驭、50 血的步兵，无论哪种算法基本都是一碰就死 [推断]。
- **泰坦降落砸人：** 90 u 以内对铁驭 400（必死），90–120 u 衰减；对泰坦 23000、穿护盾。玩家泰坦站在 90 u 外只吃 15 %，并被推开 400 u/s。
- **拳：** 多人 500 伤害、距离 280、锥 20、挥拳 0.8 s。打到人当场碎尸，顺手把人往拳的方向推 800 u/s。没有前冲。锥里所有目标同一帧一起挨。剑 800（剑核心 2200），距离 325。
- **dash 撞人：** 脚本、伤害定义、设置键里都没有"撞击伤害"。dash 本身不造成伤害。但 dash 时泰坦在快速移动，原生的踩人判定**可能**照样触发——"dash 碾过步兵会不会死"只能实测。代码里还有一个没接上的"冲刺拳"状态（对泰坦推力 × 1.25），玩家触发不了。
- **对照：** 死神（Reaper）踩不死（`titanStompable 0`）；它自己的砸地 80 / 1800、半径 100–200，降落 400 / 23000、半径 90–256。AI 泰坦的拳打铁驭 150–300，冲撞拳 500–700。
- 初扫（SCAN-1108 §4）这一段的更正见第 0 节。

## 0. 来源和可信度

路径缩写（都相对 `TF2-Research/`）：

| 缩写 | 路径 | 可信度 |
|---|---|---|
| V | `local/vpk/client_mp_common/scripts/vscripts/` | Respawn 原版，最高 |
| WT | `local/vpk/client_mp_common/scripts/weapons/`（`.txt`，取 `MP_BASE`） | 同上 |
| P | `local/vpk/client_mp_common/scripts/players/mp/`（`.set`） | 同上 |
| AS | `local/vpk/client_mp_common/scripts/aisettings/` | 同上 |
| DD | `local/vpk/client_mp_common/scripts/damage/damagedefs.txt` | 同上 |
| FE | `local/vpk/client_frontend/scripts/vscripts/` | 同上 |
| SV | `local/vpk/client_sp_training/scripts/vscripts/`（零售服务端脚本，含 MP 分支） | Respawn 原版 |
| SS | `static-values/set-schema-server.tsv`（`server.dll` 里的玩家设置键表：默认值和说明） | 原生，从二进制导出 |
| AI | `local/ai-live/dig-8.txt`（`server.dll` 里的 AI 设置键表） | 同上 |
| CV | `local/convar-all-server.dll.txt`（`server.dll` 的控制台变量注册） | 同上；默认值字符串由本会话按地址从 `server.dll` 读出 |
| NS | `<TF2>/R2Northstar/mods/Northstar.CustomServers/mod/scripts/vscripts/` | Northstar，部分社区重写，标 [NS 社区版] |

标记：[推断] 按代码推出来、没实测；[未知] 文件里没有；[原生] 在 C++ 里，脚本只给参数。

本会话没有读 `server.dll` 的踩人函数：TF2 的 Ghidra 工程（`../ghidra-projects/tf2/`）正被别的会话占用（有锁文件）。

**对初扫（SCAN-1108 §4"泰坦打步兵"）的更正：**

| 初扫 | 更正 | 依据 |
|---|---|---|
| 踩踏：文件里没有数值 | 有设置键和默认值（见第 1 节）；只有伤害公式是原生的 | SS:240–244；P/`titan_base.set:90–93`；AS/`npc_titan.txt:135–138` |
| 落地砸人：对人 400、半径 90 | 90 是全伤半径，120 是外半径，中间衰减；对泰坦 23000 穿盾；玩家泰坦 90 外 × 0.15 并被推开 | DD:52–65；SV/`titan/_titan_hotdrop.gnut:713–748` |
| 拳击：500，距离 260，0.8 s | 260 是战役值；多人 **280**，锥 20（战役 30） | WT/`melee_titan_punch.txt:22–37` |
| 剑：625 / 800 | 625 是战役，多人 **800**；剑核心 +1400 = 2200 | WT/`melee_titan_sword.txt:26–41, 163–167` |
| dash 撞人：脚本和伤害定义里都没有 | 对；补：dash 时原生踩人可能触发；有一个用不到的冲刺拳状态 | 第 4 节 |

## 1. 踩人（`damagedef_titan_step`）

**一句话：** 泰坦移动时，脚下一块盒子里的小目标会挨"被踩"伤害，判定和伤害都在原生代码里。

**状态机（[推断]，按设置键的说明拼出来）：**

| 条件 | 内容 |
|---|---|
| 谁会踩 | 泰坦（玩家或 NPC），移动速度 ≥ `titan_footstep_damage_min_speed`（50） |
| 踩到谁 | 受害者的包围盒和"泰坦高度最下面 `height_check_ratio`（15 %）"的那一层相交 |
| 多久判一次 | 玩家泰坦：`interval -1`（不按时间）+ `dist_interval 100`（每走 100 u）；NPC 泰坦：1.0 s + 150 u。两条是"且"还是"或" [未知] |
| 伤害 | `titan_footstep_damage` 5000，"每秒"；怎么折成单次 [未知] |
| 进脚本 | 和普通伤害一样走 `CodeCallback_DamagePlayerOrNPC`，伤害源 5 |

**数值：**

| 项 | 玩家泰坦 | NPC 泰坦 | 出处 |
|---|---|---|---|
| `titan_footstep_damage` | 5000（没有任何文件改它） | 5000 | SS:240；AI:302（默认值字符串 `5000`） |
| 最低速度 | 50（键表默认 10） | 50 | P/`titan_base.set:91`；AS/`npc_titan.txt:136`；SS:241 |
| 高度比 | 0.15（键表默认 0.36） | 0.15 | P/`titan_base.set:90`；P/`titan_ctt.set:98`；AS/`npc_titan.txt:135`；SS:242 |
| 时间间隔 | −1.0 | 1.0 | P/`titan_base.set:92`；AS/`npc_titan.txt:137`；SS:243 |
| 距离间隔 | 100 | 150 | P/`titan_base.set:93`；AS/`npc_titan.txt:138`；SS:244 |
| 下骑后免踩 | 0.1 s（控制台变量 `titan_step_damage_rodeo_immunity_time`） | 同 | CV:1850–1852 |
| 调试 | `titan_step_damage_debug 1` 画出踩人判定盒 | 同 | CV:1846–1848 |
| 伤害定义 | `CODE_DAMAGE_ID_TITAN_STEP`，讣告 `#DEATH_STEPPED_ON`，没有伤害值 | | DD:26–30 |
| 伤害类型 | `DF_TITAN_STEP`（`damageTypes.titanStepCrush`） | | V/`sh_death_package.gnut:71` |

**谁不会被踩：**
- 正骑在这台泰坦身上的铁驭（SV/`mp/_base_gametype.gnut:424–429`）；刚跳下来 0.1 s 内（CV:1850）。
- 相位冲刺中的泰坦踩不了人；相位中的铁驭不受伤（SV/`mp/_base_gametype.gnut:343–346, 408–411`）。
- 队友（多人友军保护，SV/`mp/_base_gametype.gnut:206–227`）。自己的泰坦也踩不到自己的铁驭（同上 `:218–219`）。
- `titanStompable 0` 的 NPC：死神、巨型炮塔、`sentry_tday` 炮塔（AS/`npc_super_spectre.txt:162`；AS/`npc_turret_mega.txt:12`；AS/`npc_turret_sentry_tday.txt:17`）。默认是 1，其余 NPC 都能踩（AI:214）。

**附带效果：**
- 不放命中音、击杀音（V/`client/cl_player.gnut:814–818`）；不触发狙击镜头（SV/`mp/_codecallbacks.gnut:790`）。
- 潜行者（stalker）被踩死时背包大爆炸（`damagedef_stalker_powersupply_explosion_large_at`）（SV/`ai/_ai_stalker.gnut:57–66`）。
- 带 `PAS_WIFI_SPECTRE` 的玩家泰坦踩到幽灵会把它骇入，不造成伤害（SV/`_codecallbacks_common.gnut:155–185`；这个被动多人拿不到）。
- 死亡表现走"击退 / 踩"那一类（V/`sh_death_package.gnut:378`）。

**边界情况：**
- 站着不动（速度 < 50）压在步兵身上：不踩 [推断]。
- 15 % 的高度：泰坦约 200 多 u 高 → 脚下约 35 u 的一层 [推断，泰坦高度要量]。站在箱子上的步兵可能躲过。
- 玩家泰坦每走 100 u 判一次：以走速 210 算约每 0.48 s 一次，冲刺 310 约 0.32 s，dash 600 约 0.17 s [推断]。

**要实测：** 见第 6 节第 1–4 项。

## 2. 泰坦降落砸人（`damagedef_titan_fall`）

**一句话：** 召唤的泰坦落地那一帧，在落点做一次爆炸：小半径里的人必死，泰坦也会被砸。

**时间线：** 召唤 → 落点出现警告（120 u 内的敌人收到强警告，240 u 内收到弱警告）→ 泰坦落地动画的 `titan_impact` 事件 → 落地爆炸 + 震屏 + 512 u 的物理推力（只推物体）。

**数值：**

| 项 | 值 | 出处 |
|---|---|---|
| 对铁驭 / 步兵 | 400 | DD:54 |
| 对泰坦 | 23000 | DD:55 |
| 全伤半径 / 外半径 | 90 / 120；中间怎么衰减 [未知] | DD:56–57；FE/`sh_consts.gnut:1647–1648` |
| 推力 | 50000 | DD:58 |
| 标记 | 布娃娃、爆炸、**穿护盾**、跳过濒死；不伤自己 | DD:60–63 |
| 玩家泰坦在 90 u 外 | 伤害 × 0.15；身后 120 u 有空间就推开 400 u/s 并踉跄 | SV/`titan/_titan_hotdrop.gnut:713–748` |
| 触发 | 落地动画事件 `titan_impact` | SV/`titan/_titan_hotdrop.gnut:248, 474–516` |
| 物理推力 | 半径 512，只推物理物体，不伤人 | SV/`titan/_titan_hotdrop.gnut:509–515` |
| 警告 | 120 u 内强警告，240 u 内弱警告 | SV/`titan/_replacement_titans.gnut:924–940` |
| 伤害源 | `damagedef_titan_fall`（8） | V/`sh_damage_types.nut:28` |

**另一种落法（`damagedef_titan_hotdrop`）：** 铁驭坐在泰坦里一起落下时用：150 / 150，半径 80–250，不穿盾（DD:67–80；SV/`titan/_titan_hotdrop.gnut:153–158`）。Northstar 的"以泰坦身份重生"走这条 [NS 社区版]（NS/`mp/_base_gametype_mp.gnut:520, 598`）。

**边界情况：**
- 队友和自己的铁驭：友军保护，不受伤。
- 落地伤害不算"计时充能"（NS/`mp/_codecallbacks.gnut:38–43`）。

**要实测：** 第 6 节第 7 项。

## 3. 拳和剑

**一句话：** 泰坦近战在视线前方的锥里找目标；锥里的人和小 NPC 全部一起挨 500，碎尸，被推开。

**状态机：**

| 状态 | 进入 | 行为 | 离开 |
|---|---|---|---|
| 挥拳 | 按近战 | 动作 0.8 s；之后 1.0 s 收回 | 结束 |
| 判定 | 挥拳中的攻击帧 [原生，帧时刻未知] | 找锥里看得见的目标；第一帧找到就**全部**一起打，之后的帧不再打 | 打到或挥完 |

- 永远是普通拳（`PLAYER_MELEE_STATE_TITAN_MELEE_JAB`），见第 4 节"冲刺拳"（V/`melee/sh_melee_titan.gnut:17–48`）。
- 一帧里锥中所有目标都打（V/`melee/sh_melee_titan.gnut:87–88, 105–176`）。
- 打人（人形和小 NPC）：伤害 = 按护甲类型取值；加碎尸标记；目标速度 += 视线方向 × 800（目标在身后则反向）；铁驭若在骑别的泰坦，去掉骑乘保护（`:227–263`）。
- 打泰坦：推开（拳 510、剑 400、剑核心 100，向上 +100，竖直最多 550），自己被反推；够条件时转处决（`:265–363`；FE/`_settings.nut:796`）。
- 相位中的泰坦不能近战（`:91–92`）。涡旋不挡近战（playlist `vortex_blocks_melee 0`，`:122–136`）。
- 没打到目标时朝视线扫一条线，打到世界只出特效（`:178–200`）。

**数值：**

| 项 | 拳（七台除 Ronin） | 剑（Ronin） | 出处 |
|---|---|---|---|
| 伤害（人 / 泰坦） | 500 / 500 | 800 / 800；剑核心 +1400 → 2200 | WT/`melee_titan_punch.txt:45–46`；WT/`melee_titan_sword.txt:39–40, 163–167` |
| 距离 | 280（战役 260） | 325 | WT/`melee_titan_punch.txt:24, 32`；WT/`melee_titan_sword.txt:36` |
| 锥 | `melee_angle 20`（战役 30）；是半角还是全角 [未知] | 没写（剑核心 45） | WT/`melee_titan_punch.txt:27–28, 35–36`；WT/`melee_titan_sword.txt:173` |
| 动作 / 收回 | 0.8 s / 1.0 s | 0.9 s / 0.5 s | WT/`melee_titan_punch.txt:42–44`；WT/`melee_titan_sword.txt:37, 56–57` |
| 前冲 | 没有（另一个拳文件的注释写"Titan melee script doesn't lunge"） | `melee_lunge_time 0.5`、`lunge_target_range 100`、角度 45；是否真前冲 [未知] | WT/`melee_titan_punch_fighter.txt:9–10`；WT/`melee_titan_sword.txt:55, 75–76` |
| 打中定格视角 | 0.25 s | 0.25 s | WT/`melee_titan_punch.txt:50`；WT/`melee_titan_sword.txt:62` |
| 打人推力 | +800 u/s 沿视线 | 同 | V/`melee/sh_melee_titan.gnut:236–240` |
| 七台的拳 | 都 `#base melee_titan_punch.txt`，没改数 | — | WT/`melee_titan_punch_*.txt:1` |
| 伤害源 | `melee_titan_punch`（143）、`_ion` 144、`_tone` 145、`_legion` 146、`_scorch` 147、`_northstar` 148、`_fighter` 149、`_vanguard` 150 | `melee_titan_sword` 151、`_aoe` 152；剑核心中记为 `mp_titancore_shift_core`（81） | V/`sh_damage_types.nut:174–183`；V/`melee/sh_melee_titan.gnut:255–258` |

目标血量（对照）：铁驭 100（P/`pilot_base.set:28`）、步兵 50、幽灵 100、潜行者 150、死神 3500（AS/`npc_soldier.txt:52`、`npc_spectre.txt:170`、`npc_stalker.txt:116`、`npc_super_spectre.txt:68`）。拳 500 对这些小目标全是一击。

**AI 泰坦的近战（对照，不是玩家拳）：** NPC 泰坦的近战走 AI 设置，伤害源会被改成 `auto_titan_melee`（177）（SV/`mp/_codecallbacks.gnut:72–79`）。

| 项 | 值 | 出处 |
|---|---|---|
| 普通拳 | 对人 150–300，对泰坦（多人自动泰坦）400–500；半径 120，距离 200 | AS/`npc_titan.txt:68–76`；AS/`npc_titan_auto.txt:13–28` |
| 冲撞拳 | 对人 500–700，对泰坦（多人自动泰坦）2000；距离 270，半径 150，高 150 | AS/`npc_titan.txt:77–83`；AS/`npc_titan_auto.txt:23–24` |
| 间隔 | 普通 2 s，冲撞 3 s，最多连 2 下 | AS/`npc_titan.txt:84–86` |

**要实测：** 第 6 节第 5–6 项。

## 4. dash 撞人

**一句话：** 文件里没有"dash 撞人"这条规则；如果撞了会死，只可能来自原生的踩人判定。

**搜过的地方和结果：**

| 找什么 | 结果 | 出处 |
|---|---|---|
| dash 时的脚本回调 | `CodeCallback_OnPlayerDodge` 只转发给"移动事件"回调；多人里唯一注册的是提示 | SV/`_codecallbacks_common.gnut:751–763`；SV/`titan/_titan_hints.gnut:53, 257` |
| 伤害定义 | 没有 dash / ram / impact 类条目；和撞有关的只有 `titan_step`、`crush`（`crush` 用于卡住处死和地图触发器） | DD 全文；V/`titan/sh_titan.gnut:895–899`；SV/`_global_entities.gnut:256–257` |
| 伤害源列表 | 有 `mp_weapon_dash_melee`，是铁驭近战用的（`sh_melee_human`），和泰坦无关 | V/`sh_damage_types.nut:149`；V/`melee/sh_melee_human.gnut:40` |
| 设置键 | `dodge*` 键只有速度、时长、高度、能耗；`impactSpeed 1000` 只决定播不播碰撞特效；`dodgeImpactTable` 是特效表 | P/`titan_ogre.set:29–39`；P/`titan_base.set:89, 99`；`local/set-schema-client.tsv:22` |
| 推物体 | 玩家泰坦能推 ≤ 5000 质量、≤ 200 u/s 的物理物体；NPC 泰坦撞飞物理物体，给物体 50 伤害（半径 100、速度 500） | P/`titan_base.set:71–75`；CV:1814–1836（默认值 300 / 50 / 2000 / 100 / 500） |
| 冲刺拳 | 有 `PLAYER_MELEE_STATE_TITAN_DASH_PUNCH` 分支（喷射特效、对泰坦推力 × 1.25），但出拳函数写死为普通拳，玩家触发不了 | V/`melee/sh_melee_titan.gnut:26, 35–39, 273, 307–308` |

**结论：** dash 本身不造成伤害 [文件层面确定]。[推断] dash 速度 600–800 u/s 远高于踩人的 50 u/s 门槛，走 100 u 只要约 0.15 s；如果原生踩人判定在 dash 时也在跑，dash 穿过步兵会触发 `damagedef_titan_step`（编号 5）。另外步兵可能只是被泰坦的碰撞推开，不掉血。

**要实测：** 第 6 节第 4 项。

## 5. 对照：死神和其他

| 项 | 值 | 出处 |
|---|---|---|
| 能不能被泰坦踩 | 不能（`titanStompable 0`） | AS/`npc_super_spectre.txt:162` |
| 砸地（常用近战） | 多人：对人 80，对泰坦 1800；内半径 100，外半径 200；向上推力 | DD:111–129；AS/`npc_super_spectre.txt:106` |
| 近战伤害（AI 键） | 多人：对人 50–70，对泰坦 1000–2000；冲撞对人 60–80 | AS/`npc_super_spectre.txt:111–119` |
| 近战范围 | 半径 120，距离 150，360°；冲撞半径 100、高 120，只对普通护甲 | 同上 `:107, 131–141` |
| 降落 | 对人 400，对泰坦 23000；内 90，外 256；穿盾 | DD:82–95；SV/`mp/_ai_superspectre.nut:720–725` |
| 会不会踩人 | AI 设置里没写踩人键，脚注 `footstepImpactTable` 被注释掉；[未知] | AS/`npc_super_spectre.txt:146` |

## 6. 要实测（按重要性排序）

`kit_d` 批次：泰坦走、冲刺跑、出拳、dash 撞向静止步兵，记 `NDMG`（伤害、伤害源编号）。

**要找的伤害源编号**（原版和 Northstar 的枚举相同，按 V/`sh_damage_types.nut:13–251` 和 `<TF2>/R2Northstar/mods/Northstar.Custom/mod/scripts/vscripts/sh_damage_types.nut` 逐个数出）：

| 编号 | 名字 | 来自 |
|---|---|---|
| 5 | `damagedef_titan_step` | 踩人（含可能的 dash 碾压） |
| 6 | `damagedef_crush` | 卡住处死；出现说明有别的挤压规则 |
| 8 / 9 | `damagedef_titan_fall` / `damagedef_titan_hotdrop` | 降落砸人 |
| 143–150 | `melee_titan_punch` 系列（Scorch 147、Monarch 150、Ion 144、Tone 145、Legion 146、Northstar 148） | 玩家拳 |
| 151 / 152 / 81 | 剑 / 剑 aoe / 剑核心中的剑 | Ronin |
| 177 | `auto_titan_melee` | AI 泰坦的拳 |
| 206 / 208 | `fall` / `crushed` | 摔落、挤压（出现要记下） |
| −1 / 0 | 原生、没设伤害源 | 任何意外的碰撞伤害 |

**怎么记：** 现有的 `NDMG`（`HSD.TF2Diag` 的 `hsd_diag_npc.gnut:262–278`）挂在 `AddEntityCallback_OnDamaged` 上，在按伤害源的回调之前；T-b 的这些伤害源没有会改伤害的源回调（降落只改玩家泰坦），所以够用。建议每条再加三项：攻击者速度 `DamageInfo_GetAttacker( d ).GetVelocity()` 的长度、攻击者和目标的水平距离和高度差、目标受伤后一帧的速度（看推力）。步兵的血调到很高（如 100000），否则第一下就死，数不出间隔。

| # | 测什么 | 怎么摆 | 记什么 | 回答什么 |
|---|---|---|---|---|
| 1 | 走过步兵 | 平地，步兵站在泰坦正前方路线上；以走速 210 直线穿过 | 编号 5 的每次伤害值、时刻、当时泰坦走过的距离 | 单次伤害多大（5000？按帧摊？）；100 u 的间隔是不是对的 |
| 2 | 冲刺跑过步兵 | 同上，310 | 同上 | 间隔随速度怎么变 |
| 3 | 压着不动 / 慢走 | 泰坦贴着步兵站住，再蹲走 | 有没有编号 5 | 50 u/s 门槛 |
| 4 | **dash 穿过步兵** | 同上，Ogre 600 / Atlas 700 / Stryder 800 各做 | 有没有编号 5、−1、6；步兵被推了多少 | dash 撞人到底有没有伤害 |
| 5 | 拳的距离 | 步兵在正前方 150、250、280、300 u | 编号 143–150 的伤害、步兵速度变化 | 280 的边界（量到中心还是包围盒）；800 推力 |
| 6 | 拳的角度 | 步兵在 250 u、偏离视线 10°、20°、30°、40° | 同上 | 20 是半角还是全角；锥里多个目标是否同时挨 |
| 7 | 降落砸人 | 步兵在落点 60、90、105、120、150 u | 编号 8 的伤害值 | 90–120 之间的衰减曲线 |
| 8 | 高度 | 步兵站在 20、40、60 u 高的箱子上，泰坦走过 | 编号 5 | 15 % 高度层有多厚 |
| 9 | 铁驭目标 | 用 `npc_pilot_elite` 当人形目标重复第 1、4 项 | 同上 | 铁驭和步兵是否一样 |

## 6.5 实测（11-08，运行 `20261108_142447_kit_d`）

靶子是冻结的敌方步兵（`hsd_npc soldier static`），血量设成 10000 以便看到每一次伤害；另有一组用默认血量。伤害读最终伤害回调（`KFIN`，在所有脚本回调之后），伤害源编号按 `sh_damage_types.nut` 的枚举换成名字。泰坦：Ion（中型）、Legion（重型）。

| 测法 | 结果 |
|---|---|
| 走路（Ion 250 u/s）直直撞上步兵 | `damagedef_titan_step`（5）**每次 5000**；Ion 两次（相隔约 0.4 s），Legion 一次。10000 血的靶子被 Ion 两次踩死 |
| 冲刺跑撞上 | 同样 5000 一次 |
| **dash 撞上**（Ion、Legion 各两次） | 同样是 `damagedef_titan_step` 5000；默认血量的步兵当场死。**没有单独的"撞击伤害"**，dash 撞人 = 快速移动时的踩人 |
| 拳（150 / 250 / 280 / 300 u 正前方；250 u 偏 15° / 25° / 35°） | **一次都没打中**冻结步兵（同一轮里剑打泰坦是正常的，见 RONIN 8.3）。原因没查明：可能是拳的判定高度对着胸口，步兵太矮；也可能冻结的 NPC 不进近战判定 `[要再测]` |
| 呼叫降落砸在步兵中间（偏 0 / 60 / 90 / 105 / 120 / 150 u 各一个） | `damagedef_titan_fall`（8）：400、400、400、286、154，150 u 那个没受伤；另外落地后的穹顶护盾（`bubble_shield`，201）对罩里的 6 个步兵反复造成伤害，36 跳，每跳越来越高（34 → 41 → … → 67 → 86 → 109） |

要点：

- **踩人 = 一次 5000**，不是"每秒 5000 分摊"。对任何步兵都是一碰就死。脚本写的"玩家泰坦每走 100 u 判一次"和实测两次相隔约 0.4 s × 250 u/s = 100 u 对得上。
- **dash 撞人不是新规则**：TF2 没有撞击伤害，只是 dash 时移动快，踩人判定照样触发。
- 降落砸人：90 u 内满 400；105 u 约 286、120 u 约 154，和脚本"90 内满额、90–120 线性衰减"大致一致（按线性算 105 u 应是 200，实测 286，衰减形状待定）。150 u 外没有伤害。

## 7. 能脱离 TF2 照做的 / 还缺的

**能照做的：**
- 降落砸人：伤害、半径、穿盾、对玩家泰坦的 15 % 和推开、警告半径。
- 拳和剑：伤害、距离、动作时间、推力、"一帧打完锥里所有人"、碎尸、对泰坦的推开和反推。
- AI 泰坦和死神的近战、砸地、降落数值。
- 踩人的规则框架：速度门槛、高度层比例、按距离判定、所有豁免（骑乘、相位、队友、不可踩的 NPC）。

**还缺的：**
- 踩人的伤害公式和判定盒大小（原生）——第 6 节第 1、8 项。HSD 也可以直接自己定一个数（比如"碰到即死"），因为对 100 血的目标结果一样。
- dash 撞人有没有伤害——第 6 节第 4 项。没有的话，要不要给 HSD 加，用户拍板。
- 拳的锥是半角还是全角、攻击帧在动作的第几秒。
- 降落 90–120 u 的衰减曲线。

**11-08 实测补上的（见第 6.5 节）：** 踩人一次 5000（每走约 100 u 一次）；dash 撞人就是踩人，没有单独伤害；降落砸人 0–90 u 400、105 u 286、120 u 154、150 u 0。**仍缺：** 拳打步兵一次都没打中冻结靶子，原因没查明。

**11-12 原生（`ref-native-tail`，N6）：** 踩人的公式和判定盒读到了（server `0x180661360` → `0x180660c80`）：
- 什么时候判：泰坦每走 `dist_interval`（玩家 100，NPC 150），且速度 ≥ 50，判一次。
- 判定盒：受害者的盒要和泰坦碰撞盒相交，并且碰到泰坦盒最下面 15 % 的高度；两个盒中心之间的盒追踪要畅通。
- 每个受害者单独计时：玩家泰坦间隔 −1（不限），NPC 泰坦 1 s。从 rodeo 跳下 0.1 s 内免疫。
- 伤害：**一次 5000**，不按秒算。dash 也会踩，代码里没有排除。
详见 [REF-NATIVE-1112.md §6](../../../ref-native-tail/REF-NATIVE-1112.md)。
