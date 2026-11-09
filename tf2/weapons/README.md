# TF2 铁驭武器：Apex 没有的那些（必跑任务 3，2026-11-08）

会话 `tf2-weapons`。任务见 [../MUST-RUN-1108.md](../MUST-RUN-1108.md) 第 3 项。

## 先说结论

- TF2 的 31 把铁驭武器里，**Apex 没有的是 7 把**：Double Take、Cold War、Sidewinder SMR、Softball、MGL、Thunderbolt、Archer（EPG 和 Smart Pistol 以前做过）。7 把都做到了"规则 + 数值 + 实测对照"，每把一页（下面的总览表）。
- **文件和实测基本一致**。7 把枪的射速、弹速、重力、引信、开镜时间、散布规则、伤害值，实测都对上了文件和脚本。脚本里看不到的三块，这次从 `server.dll` 读出来了：**MGL 的磁吸**（只吸 `magneticRange` > 0 的敌人，进范围约 0.1 s 后以 1600 u/s 直冲目标）、**导弹的随机漂移**（Archer、SMR 共用，四个正弦之和）、**Archer 的锁定时间**（实测符合 1.05 + 0.5 × 距离 / 6500 s）。
- **和文件字面不符的几处**（照实测做）：
  1. 所有武器打死神都**不乘** `damage_heavyarmor_nontitan_scale`（死神吃满额重甲伤害）。
  2. Archer 的导弹速度上限 1400 **没有生效**（脚本读了没用），一直 1200。
  3. Thunderbolt 脚本写的重力 5 没有效果，电球不受重力。
  4. 换弹"能开火"比文件时长早 0.3–0.55 s；中途打断后，下次只换剩下的一段（`reload_time_late*` 的含义），但节点位置要逐把枪测（只有两把正好在 `T − late_k`）。
- **Apex 有对应的 22 把**里，按文件比较值得单独写页的是 4 把：EVA-8（不发弹丸）、Mastiff + Mozambique（慢速弹）、L-STAR（另一套过热）。这次没写页，只在 [VARIANTS.md](VARIANTS.md) 里列了差别。
- 打人和爆头倍率已补测（`wp_f`、`wp_g`：Double Take × 2、Cold War / SMR × 1.25，打腿不减伤）。没测成的：画面后坐弹簧（脚本读不到）、腰射散布的分布形状、几处原生细节。每页"不知道的"一节列全了。

## 研究清单（第一步）

来源：`local/vpk/client_mp_common/scripts/weapons/*.txt` 里所有能装进铁驭配装的武器（31 把，类名和英文名来自 `r1_english.txt`），对照 HSD 枪械用的 R5 枪表（研究仓库 `research/combat/gun-measure/GUN-VARS.tsv`，31 把）。数值是多人版（基础键再套 `MP_BASE`），全表在 [data/wpn-values.tsv](data/wpn-values.tsv)。

标记：
- **TF2 独有**：Apex 没有同类武器，本次逐把做到能照做。
- **Apex 有对应**：HSD 照 R5 做；最后一列写 TF2 版的机制差别，以及值不值得单独写一页（依据 [VARIANTS.md](VARIANTS.md)，只比了文件）。值得写的 4 把（EVA-8、Mastiff + Mozambique、L-STAR）这次**没有写页**：不在本任务范围（任务只要求 TF2 独有的），留作后续。
- **已做**：别的研究做过，不重复。

| # | TF2 武器 | 类名 | 位置 | Apex 对应 | 标记 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | D-2 Double Take | `mp_weapon_doubletake` | 主武器 / 狙击 | Triple Take（远亲） | **TF2 独有** | 每发 3 颗弹体、耗 2 发，水平排开；Triple Take 是能量枪 + 收束 |
| 2 | EM-4 Cold War | `mp_weapon_pulse_lmg` | 主武器 / 榴弹 | 无 | **TF2 独有** | 榴弹，每次扣扳机 4 发连发 |
| 3 | Sidewinder SMR | `mp_weapon_smr` | 主武器 / 榴弹 | 无 | **TF2 独有** | 全自动小火箭，弹道随机漂移 |
| 4 | R-6P Softball | `mp_weapon_softball` | 主武器 / 榴弹 | 无 | **TF2 独有** | 粘性榴弹，粘住 0.5 s 后炸；逐发装填 |
| 5 | MGL Mag Launcher | `mp_weapon_mgl` | 反泰坦 | 无 | **TF2 独有** | 磁吸榴弹，两连发，撞到"磁性目标"直接炸 |
| 6 | LG-97 Thunderbolt | `mp_weapon_arc_launcher` | 反泰坦 | 无 | **TF2 独有** | 慢速电球，每 0.4 s 电一次周围目标 |
| 7 | Archer | `mp_weapon_rocket_launcher` | 反泰坦 | 无 | **TF2 独有** | 锁定导弹；多人版必须锁定才能发射 |
| 8 | EPG-1 | `mp_weapon_epg` | 主武器 / 榴弹 | 无 | 已做（[../epg/](../epg/T1-T7-REPORT.md)） | 不在本次范围 |
| 9 | Smart Pistol | `mp_weapon_smart_pistol` | 主武器 / 手枪 | 无 | 已做（W3） | 不在本次范围 |
| 10 | R-201 Carbine | `mp_weapon_rspn101` | 主武器 / 步枪 | R-301 | Apex 有对应 | 只是参数（即时命中、三段衰减）；不单独写 |
| 11 | R-101 Carbine | `mp_weapon_rspn101_og` | 主武器 / 步枪 | R-301 | Apex 有对应 | R-201 换皮（开镜后坐上限 2.0、默认瞄具）；不单独写 |
| 12 | Hemlok BF-R | `mp_weapon_hemlok` | 主武器 / 步枪 | Hemlok | Apex 有对应 | 三连发 |
| 13 | G2A5 | `mp_weapon_g2` | 主武器 / 步枪 | G7 Scout（远亲） | Apex 有对应 | 半自动 5.5 / s、14 发；只是参数 |
| 14 | V-47 Flatline | `mp_weapon_vinson` | 主武器 / 步枪 | Flatline | Apex 有对应 | |
| 15 | CAR | `mp_weapon_car` | 主武器 / 冲锋枪 | CAR | Apex 有对应 | |
| 16 | Alternator | `mp_weapon_alternator_smg` | 主武器 / 冲锋枪 | Alternator | Apex 有对应 | |
| 17 | Volt | `mp_weapon_hemlok_smg` | 主武器 / 冲锋枪 | Volt | Apex 有对应 | |
| 18 | R-97 | `mp_weapon_r97` | 主武器 / 冲锋枪 | R-99 | Apex 有对应 | |
| 19 | Spitfire | `mp_weapon_lmg` | 主武器 / 机枪 | Spitfire | Apex 有对应 | |
| 20 | L-STAR | `mp_weapon_lstar` | 主武器 / 机枪 | L-STAR | Apex 有对应 | **值得一页**：35 发自动回、打空强制换镜片；和 R5 的蓄热是两套做法 |
| 21 | X-55 Devotion | `mp_weapon_esaw` | 主武器 / 机枪 | Devotion | Apex 有对应 | 射速爬升 |
| 22 | Kraber-AP | `mp_weapon_sniper` | 主武器 / 狙击 | Kraber | Apex 有对应 | 弹体 |
| 23 | Longbow-DMR | `mp_weapon_dmr` | 主武器 / 狙击 | Longbow | Apex 有对应 | |
| 24 | EVA-8 Auto | `mp_weapon_shotgun` | 主武器 / 霰弹 | EVA-8 | Apex 有对应 | **值得一页**：不发弹丸，锥形内每个目标吃一次伤害（R5 是 8 颗固定图案） |
| 25 | Mastiff | `mp_weapon_mastiff` | 主武器 / 霰弹 | Mastiff | Apex 有对应 | **值得一页**（和 Mozambique 合一页）：8 颗 3000 u/s 慢弹，0.65–0.85 s 消失 |
| 26 | Wingman Elite | `mp_weapon_wingman_n` | 主武器 / 手枪 | Wingman | Apex 有对应 | 也许：弹体、所有姿态散布 0、跳弹 mod |
| 27 | RE-45 Auto | `mp_weapon_autopistol` | 副武器 | RE-45 | Apex 有对应 | |
| 28 | Hammond P2016 | `mp_weapon_semipistol` | 副武器 | P2020 | Apex 有对应 | |
| 29 | B3 Wingman | `mp_weapon_wingman` | 副武器 | Wingman | Apex 有对应 | 即中（hitscan），Elite 是弹体 |
| 30 | SA-3 Mozambique | `mp_weapon_shotgun_pistol` | 副武器 | Mozambique | Apex 有对应 | **值得一页**（同 Mastiff）：3 颗 3000 u/s 慢弹 |
| 31 | Charge Rifle | `mp_weapon_defender` | 反泰坦 | Charge Rifle | Apex 有对应 | 也许：没弹匣、共 20 发，蓄满 1.3 s 才出；HSD 做泰坦对抗时再看 |

不算铁驭配装武器、不进清单的：`mp_weapon_arena1–3`（Coliseum 模式专用，L-STAR / EPG / "H.E.L.L."）、`mp_weapon_shotgun_doublebarrel`（本地化文件里没有名字，没进配装）、`mp_weapon_npc_rocket_launcher`（只给 NPC）、无人机 / 炮塔 / 炮艇武器、近战（Apex 有，走 R5）、技能和手雷（W2 / W3 已做）。

## 总览（7 把 TF2 独有武器，多人值）

文件值来自 [data/wpn-values.tsv](data/wpn-values.tsv)；"实测"列见各页第 2 节。伤害写"对人 / 对重甲"。

| 武器 | 页 | 开火 | 弹匣 | 直接命中 | 爆炸（半径 内 / 外） | 弹体 | 特殊机制 | 换弹 战术 / 空仓 | 开镜 进 / FOV |
|---|---|---|---|---|---|---|---|---|---|
| D-2 Double Take | [DOUBLE-TAKE.md](DOUBLE-TAKE.md) | 半自动 2 / s，每发 3 颗、耗 2 发 | 12 | 每颗 30 / 165，爆头 × 2 | — | bolt 10000 u/s，重力 0.09 | 3 颗水平排开 ±0.215° | 2.4 / 3.4 | 0.4 s / 26.26 |
| EM-4 Cold War | [COLD-WAR.md](COLD-WAR.md) | 扣扳机 0.5 s 后 4 连发 12 / s，组间 0.5 s | 12 | 30 / 175，爆头 × 1.25 | 30 / 175（96 / 150），炸自己 | bolt 3500 u/s，重力 0.9 | 先蓄 0.5 s 再连发 | 4.0 / 4.6 | 0.2 s / 45 |
| Sidewinder SMR | [SIDEWINDER-SMR.md](SIDEWINDER-SMR.md) | 全自动 9 / s | 20 | 50 / 115，爆头 × 1.25 | 15 / 150（1 / 16） | 导弹 3300 u/s | 直飞 1.5–2 s 后随机漂移；散布比准星小 1° | 3.0 / 3.0 | 0.2 s / 45 |
| R-6P Softball | [SOFTBALL.md](SOFTBALL.md) | 半自动 2 / s | 6 | 10 / 0 | 90 / 330（50 / 150） | 榴弹 2500 u/s，继承玩家速度 | 粘住 0.5 s 后炸；逐发装填 | 每发 0.82 + 收尾 0.57 | 0.2 s / 45 |
| MGL Mag Launcher | [MGL.md](MGL.md) | 半自动 2 连发 6 / s，组间 0.7 s | 6 | 20 / 330 | 35 / 70（50 / 100） | 榴弹 1200 u/s，上抬 6°，引信 1.2 s | 磁吸（原生），撞磁性目标即炸 | 3.75 / 3.75 | 0.2 s / 55 |
| LG-97 Thunderbolt | [THUNDERBOLT.md](THUNDERBOLT.md) | 必须开镜，1 发 | 1 | 70 / 1000 | 40 / 250（150 / 250） | 电球 500 u/s + 前进速度 | 每 0.4 s 电半径 400：人 8 / 重甲 350 | 3.35 / 3.35 | 0.35 s / 45 |
| Archer | [ARCHER.md](ARCHER.md) | 必须开镜且锁定（多人），1 发 | 1 | 100 / 2250 | 100 / 500（96 / 180） | 导弹 1200 u/s，追踪 125 | 锁定 1.05–1.55 s | 3.0 / 3.0 | 0.35 s / 45 |

## 方法

照 R5 枪的测法（研究仓库 `research/combat/gun-measure/`）做能做的部分。

**静态**：
- [tools/wpn_extract.py](tools/wpn_extract.py) 把 31 把枪的 `.txt` 解析成多人值（基础键再套 `MP_BASE`；平台标记只留 `[$WINDOWS]`），输出 [data/wpn-values.tsv](data/wpn-values.tsv)（另有战役值和每个 mod 的改动）和 [data/wpn-mods.tsv](data/wpn-mods.tsv)（`*0.7` 这类倍率已经算出多人值）。
- [tools/wpn_static_md.py](tools/wpn_static_md.py) 给每把枪生成分组的原值表，放在各页附录；只略去声音、特效、模型、晃动、UI 这类外观键，别的键一个不漏。
- 规则来自武器脚本（`scripts/vscripts/weapons/`）。服务端脚本以战役包 `client_sp_training` 为准（零售多人包不带服务端脚本）；用到 Northstar 版本时已逐个比对。

**实测**（本地 Northstar 1.31.14 私服，`mp_lf_stacks`，144 fps，铁驭 `pilot_grapple_male`，血量 5000）：
- 运行器 [tools/runner_wp.py](tools/runner_wp.py) 套在共用的 `runtime/runner.py` 外面：锁、R5 保护、收日志都是共用的。它只往**本次安装的**模组里加两个脚本（[mod/hsd_wp_sv.gnut](mod/hsd_wp_sv.gnut)、[mod/hsd_wp_cl.gnut](mod/hsd_wp_cl.gnut)），共用模组文件夹不动，别的会话的运行不会加载它们。实验表在 [tools/plans_wp.py](tools/plans_wp.py)，分析在 [tools/analyze_wp.py](tools/analyze_wp.py)。
- 记录：
  - 客户端每帧（约 144 Hz）`WC` 一行：弹匣、备弹、是否在换弹、开镜进度 `zoomFrac`、当前散布角 `GetAttackSpreadAngle`、蓄力、能否开火、智能锁定数和最高锁定进度；同一帧还有共用的 `C` 行（位置、速度、视角、按键）。
  - 服务端每个脚本帧（**0.1 s**）`PJ` 一行：玩家的每个投射物的位置、速度、是否粘住、导弹目标。所以快的弹体（Double Take 10000 u/s）只看得到终点，慢的（榴弹、电球）看得到整条弹道。
  - 每次命中 `WDMG` 一行：伤害、命中部位（hit group）、是否爆头、来源、伤害点。
- 靶子：冻结的步兵（W1 的 `hsd_npc … static`，20000 血），被动冻结的敌方 Atlas 泰坦和死神（本次新加的 `hsd_wp_titan`、`hsd_wp_reaper`）。
- 枪的换弹中断：换弹到一半用 `+weaponCycle` 切走再切回，再换一次，看第二次换弹要多久。切枪命令来自 `client_frontend/scripts/kb_act.lst`（`+weaponCycle`、`weaponSelectPrimary0–2`）。
- 原始日志（`raw.log`，含本机路径和账号名）进私有仓库 `HSD-RawData` 的 `tf2/runtime/data/`；`diag.tsv`、`meta.json`、`plan.gnut` 进研究仓库。

测不了的，各页单独写明。最主要的两条：
- **画面后坐（punch）**：TF2 脚本没有读取视角弹簧的接口，只能测"永久后坐"（视角本身的变化，`viewkick_perm_*`）。弹簧本身的参数在 `scripts/weapons/springs.txt`，已存档，可以照抄。
- **快弹体的弹道中段**：服务端脚本 0.1 s 一帧。

## 共用规则：换弹的三个时刻和"换弹中断"（实测）

TF2 每把枪都有 `reload_time` / `reloadempty_time`，还有 `reload_time_late1–3` / `reloadempty_time_late1–5`。以前对不上的两件事（TF2-GAPS：泰坦换弹"文件 2.6、实测 2.46"；`late` 键是什么意思），这次用 Double Take 和 Cold War 测清了（`runtime/data/20261108_034651_wp_a`，每个切点 1 次）。

**白话**：换弹分几段。换到一半切走，已经过了的那一段不会丢，下次从那一段接着换。另外，能开火比文件写的换弹时间早约半秒。

### 规则

设文件换弹时间为 T（战术 `reload_time` 或空仓 `reloadempty_time`），`late_k` 为对应的 `…_late{k}`：

1. 换弹动作里有几个节点（动画上的点）。Double Take 和 Cold War 的节点正好在 **T − late_k**（文件时间，从按下换弹算）；**SMR 不是**：0.69 s、1.55 s、2.14 s 切走，下次都是 late1，说明它的第一个节点早于 0.69 s（T − late1 = 1.02），第二个晚于 2.14 s（T − late2 = 1.64）。所以节点位置要逐把枪测或读动画，不能都用 T − late_k 算。
2. 换弹中途被打断（这次用切枪 `+weaponCycle`）时，记住已经过了的**最后一个节点 k**。下次换弹只要 **late_k**；一个节点都没过，从头来（T）。弹匣在打断时**不会**加弹。
3. 一次换弹里有三个时刻（实测，从这次换弹开始算）：
   - 弹匣补满：比这次换弹的文件时长（T 或 late_k）的结尾早 **1.0–1.2 s**；
   - 能开火（`IsReadyToFire` 和 `IsReloading` 同时翻转）：比结尾早 **0.41–0.55 s**；
   - 文件时长的结尾：之后没有可见的变化（推断是收尾动画）。

### 数据

| 枪 | 情况 | 文件时长 | 补满 | 能开火 | 文件 − 能开火 |
|---|---|---|---|---|---|
| Double Take | 空仓，完整 | 3.40 | 2.17 | 2.94 | 0.46 |
| Double Take | 战术，完整 | 2.40 | 1.68 | 2.12 | 0.28 |
| Double Take | 空仓 1.29 s 时切走 → 再换（late1） | 2.26 | 1.08 | 1.85 | 0.41 |
| Double Take | 空仓 0.61 s 时切走 → 再换（没过节点 1.14） | 3.40 | 2.20 | 2.97 | 0.43 |
| Cold War | 空仓，完整 | 4.60 | 3.61 | 4.11 | 0.49 |
| Cold War | 战术，完整 | 4.00 | 2.67 | 3.70 | 0.30 |
| Cold War | 空仓 0.79 s 切走 → 再换（没过节点 1.4） | 4.60 | 3.67 | 4.17 | 0.43 |
| Cold War | 空仓 1.79 s 切走 → 再换（late1，节点 1.4） | 3.20 | 2.07 | 2.68 | 0.52 |
| Cold War | 空仓 3.06 s 切走 → 再换（late2，节点 2.9） | 1.70 | 0.52 | 1.15 | 0.55 |
| Archer（smoke） | 空仓，完整 | 3.00 | 2.04 | 2.45 | 0.55 |
| SMR | 空仓，完整 | 3.00 | 2.36 | 2.70 | 0.30 |
| SMR | 0.69 / 1.55 / 2.14 s 切走 → 再换（都是 late1） | 1.98 | 1.20 | 1.54 | 0.44 |
| Softball | 逐发装填，见 [SOFTBALL.md](SOFTBALL.md) | — | — | — | — |

- Double Take、Cold War 的每个切点都和"节点 = T − late_k"一致；SMR 不一致（见规则 1）。
- 战术换弹的"文件 − 能开火"小一些（0.28–0.30）。
- 节点处的准确时刻（比如 1.14 到底在 1.0 还是 1.2）只用了两侧各一个切点夹住，没有细扫。
- 换弹不需要一直按着；空仓时打开火键会自动开始换弹（这次 `hsd_wp_clip 0` 后有几次自动开始）。

R5 的 `late` 键和 TF2 在多把枪上比例相同（[VARIANTS.md](VARIANTS.md) 第 2 节），R5 枪械测量里"每把枪不同的加弹时刻、解锁时刻"很可能是同一套机制。这是推断，没有在 R5 里切枪验证。

**能脱离 TF2 照做**：规则 + 每把枪的 T、late_k（文件）+ 补满 / 能开火相对结尾的提前量（上表；没测的枪按 1.1 s / 0.45 s 估，标 `[placeholder]`）。

## 即时命中核对（VARIANTS 里"推断即时命中"的抽查）

`runtime/data/20261108_133543_wp_d`，每把 1 发（开镜，对着 500 u 外的步兵方向）。即时命中的枪不生成投射物实体，服务端 `PJ` 记录里什么都没有；弹体枪会出现 `crossbow_bolt`。

| 枪 | 投射物 | 结论 |
|---|---|---|
| R-201、Longbow-DMR、B3 Wingman、G2A5 | 没有 | 和"即时命中"一致 |
| EVA-8 | 没有；步兵 −31，伤害来源是武器本身 | 锥形查找 + 一发"完美子弹"，即时 |
| Mastiff | 有，3000.4 u/s | 慢弹 bolt（VARIANTS 3.16） |
| Wingman Elite | 没看到 | **没测成**：12000 u/s 的 bolt 在一个 0.1 s 服务端帧里就打到墙了，看不到不代表是即时命中 |

## 测量里的两个坑（给以后的会话）

1. **冻结步兵会先滑开。** 不管是 W1 的 `hsd_npc … static`（0.6 s 后冻结）还是本次的 `hsd_wp_soldier`（0.25 s），步兵生成后都会横移 25–45 u 才停住。按生成点瞄准，弹体会擦身而过（Double Take、SMR 的直接命中一直没打中）。`wp_f` 起，`hsd_wp_soldier` 冻结后把步兵放回生成点。泰坦、死神 0.25 s 冻结时不动。
2. **`mp_lf_stacks` 出生点正前方 y ≈ −1275 有一面薄墙**（x 24–86，z 到 90 左右都撞到过）：Cold War、Softball、MGL 都在那里爆炸 / 粘住 / 弹开；Double Take 的弹体有时穿过去（`pass_through_depth 32`），有时停在那里。`hsd_probe` 的射线（只查笔刷）看不到它。离它远一点放靶子（`wp_f` 用 y −1500）。
3. 命中日志 `WDMG` 记的是伤害回调里的值，在脚本把伤害改成 0 之前（Thunderbolt 电人形目标超过 200 u 时）。判断伤害要看下一行的血量。

## 能脱离 TF2 照做的 / 还缺的

**能照做（规则 + 数值 + 实测对照都有）**：
- 7 把武器的开火时序（半自动、连发、蓄力连发、全自动、开镜才能打、锁定才能打）、弹道（速度、重力、继承玩家速度、引信、粘住、磁吸、电球、漂移）、伤害（直接 / 爆炸 / 重甲 / 爆炸衰减）、散布、开镜、永久后坐、换弹三个时刻和中断。
- 原值全表 [data/wpn-values.tsv](data/wpn-values.tsv)（31 把枪的多人 / 战役 / mod 值），每页附录有分组表。
- 实测对照：`runtime/data/` 下 9 次运行（smoke × 2、`wp_a`–`wp_g`）的 `diag.tsv`、`analysis.txt`、`sky.txt`；原始日志在 `HSD-RawData`。
- 原生代码：MGL 磁吸、导弹漂移的反编译原文在 `HSD-RawData` 的 `tf2/local/ghidra-weapons/`，读法写在各页。

**还缺**：
- 画面后坐（视角弹簧）只有 `scripts/weapons/springs.txt` 的参数，没有 TF2 里的实测曲线（脚本读不到 punch）。
- 腰射散布的分布形状（`ApplyVectorSpread`，原生）只有几个点。
- 导弹漂移 6 个键在原生结构里的对应是按用法推断的；SMR 的长距离弹道可以用来拟合核对（`wp_e/sky.txt`）。
- 换弹节点：每把枪只用 2–4 个切点夹住。
- 对玩家的效果（Softball 粘人、Thunderbolt 电人、Archer 锁玩家、导弹接近警告）：本地只有一个玩家。
- Apex 有对应的 4 把"值得一页"的枪（EVA-8、Mastiff + Mozambique、L-STAR）只有文件比较，没有实测。
