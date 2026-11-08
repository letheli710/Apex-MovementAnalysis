# 泰坦怎么回护盾：给 HSD 选的选项（T-a）

2026-11-08，读脚本写成（S 步）。用户还没定 HSD 用哪种；HSD 暂时不做捡电池。这页把 TF2 里所有回盾的办法列成选项，第 4 节是给用户挑的总表。

## 先说结论

- **TF2 多人默认不会自动回盾。** 自动回复要 playlist `titan_shield_regen 1`，默认是 0；整个 playlist 文件里只有单人的 `solo` 打开了它（PL:106, 2309）。
- **而且多人泰坦出生时护盾是 0**（上限 2500）。`titan_base.set` 写着 `start_with_shields 0`，护盾线程一启动就把护盾清零（P/`titan_base.set:10`；SV/`titan/_titan_health.gnut:738–741`）。初扫说"生成时满"是错的。只有战役的 BT（`titan_buddy.set:12`）出生满盾。
- 多人玩家实际能用的回盾办法只有 3 类：**电池**（插上就回满）、**Monarch**（能量虹吸打人回盾、升级核心回满、给队友转盾）、**FD 升级**（Legion 挡伤转盾、Ronin 剑核心命中回盾、Monarch 烟雾回盾）。
- 代码里还有 4 个入口，但多人拿不到：快充被动 `PAS_SHIELD_REGEN`、核心护盾被动 `PAS_SHIELDED_CORE`（两个都不在多人装备表里）、过盾函数 `GiveOvershield`（没有任何地方调用）、`RestoreTitan`（只有战役存档点用）。
- HSD 现在的占位"脱战 8 s 后开始回，6 s 回满"，正好是 TF2 自动回复模式的两个数（`titan_regen_delay 8.0`、`TITAN_SHIELD_REGEN_TIME 6.0`）。区别是 TF2 的等待时间按受伤大小在 1–8 s 之间变（第 2.3 节）。
- 本页不做推荐，只写每种做法会带来什么玩法。

## 0. 来源和可信度

路径缩写（都相对 `TF2-Research/`）：

| 缩写 | 路径 | 可信度 |
|---|---|---|
| W | `local/vpk/client_mp_common/scripts/vscripts/weapons/` | Respawn 原版，最高 |
| WT | `local/vpk/client_mp_common/scripts/weapons/`（`.txt`，取 `MP_BASE`） | 同上 |
| P | `local/vpk/client_mp_common/scripts/players/mp/`（`.set`） | 同上 |
| V | `local/vpk/client_mp_common/scripts/vscripts/` | 同上 |
| FE | `local/vpk/client_frontend/scripts/vscripts/`（`sh_consts.gnut`、`sh_passives.gnut`） | 同上 |
| SV | `local/vpk/client_sp_training/scripts/vscripts/`（零售服务端脚本，含 MP 分支） | Respawn 原版 |
| NS | `<TF2>/R2Northstar/mods/Northstar.CustomServers/mod/scripts/vscripts/` | Northstar，部分是社区重写；只用来标出私服上能怎么测 |
| NS 表 | 同上 `.../mod/scripts/datatable/` | Northstar 从零售包导出的数据表 |
| PL | `<TF2>/R2Northstar/runtime/compiled/mod_original_playlists_v2.txt` | 原版 playlist 副本 |
| L | `local/vpk/client_frontend/resource/r1_english.txt`（UTF-16） | 原版文字 |

- SV 里的 `_titan_health`、`_rodeo_titan`、`_passives`，Northstar 都有覆盖版，逻辑相同、只差几行行号（例如 NS/`titan/_titan_health.gnut:740–743` = SV 的 738–741）。在 Northstar 私服上测到的 = 原版行为。
- 搜过的词（W、V、SV、NS 全部）：`SetShieldHealth`、`SetShieldHealthMax`、`shield_regen`、`ShieldRegen`、`GiveOvershield`、`start_with_shields`、`titan_shield_decay`、`battery_shield_frac`、`PAS_SHIELD*`。下面列出的就是全部入口。

## 1. 先读：护盾本身的规则

| 规则 | 内容 | 出处 |
|---|---|---|
| 上限 | 设置文件 `healthShield`，七台多人都是 2500 | P/`titan_ogre.set:50` 等 |
| 存在哪 | 泰坦的"灵魂"（soul）上，下机、上机都跟着 | V/`titan/sh_titan_soul.gnut:96–98` |
| 出生 | 先设成上限，紧接着护盾线程按 `start_with_shields` 清零 | V/`titan/sh_titan_soul.gnut:96–109`；SV/`titan/_titan_health.gnut:738–741` |
| 先扣盾 | 有盾时伤害先扣盾，盾扣完剩下的才扣血 | SV/`titan/_titan_health.gnut:212–217`；SV/`_utility.gnut:3733–3790` |
| 穿盾 | 带 `DF_BYPASS_SHIELD` 的不扣盾（例如泰坦降落砸人） | SV/`titan/_titan_health.gnut:200–201` |
| 盾从 0 变正 | 给骑在自己身上的友军铁驭加保护 | SV/`titan/_titan_health.gnut:757–764` |
| 濒死 | 护盾线程结束；救回（undoom）时线程重启，并**再次清零**护盾 | SV/`titan/_titan_health.gnut:70–97, 733, 738–741` |
| 帧率 | 护盾线程每个脚本帧跑一次（约 0.1 s），回复量按实际帧间隔折算 | SV/`titan/_titan_health.gnut:792–803` |

## 2. 每一种回盾办法

每项写：触发、回多少、时间、出处、做进 HSD 意味着什么。

### 2.1 出生满盾（`start_with_shields`）

- 触发：泰坦生成（召唤落地、AI 泰坦刷出）。
- 回多少：多人 0；战役 BT 满。
- 出处：P/`titan_base.set:10`（0）；P/`titan_buddy.set:12`（1）；SV/`titan/_titan_health.gnut:738–741`。
- 多人可用：是（就是默认的"出生 0"）。
- 做进 HSD：选"满"，每台新泰坦多一层 2500 的缓冲，第一次交火更宽松；选"0"，护盾完全是挣来的，其他回盾办法才有意义。

### 2.2 电池

- 触发：电池插进泰坦（牛仔骑乘塞进去，或泰坦自己捡）。
- 回多少（多人）：
  - 护盾**直接回满**。playlist 变量 `battery_shield_frac`（默认 1.0）被读了但没用上，所以永远是满。
  - 血 + 半段（0.5 × 每段血 2500 = 1250）。
  - 增幅电池：血 + 2 段；如果正濒死，先救回再回满盾。
  - 核心表 + 20 %。
  - Monarch 带 Survival of the Fittest（`pas_vanguard_doom`）时，濒死插电池先救回到 1 血。
- 时间：当场。
- 出处：SV/`rodeo/_rodeo_titan.gnut:1698–1786`（多人分支 1744–1779，变量 1751–1754，回满 1772、1777，核心 1756）；L:11332–11333。
- 多人可用：是。
- 做进 HSD：回盾变成"要去拿"的东西，引出铁驭和泰坦配合、抢电池的玩法。HSD 已决定暂时不做拾取循环，所以只适合以后做"补给点 / 掉落物"时再接。

### 2.3 自动回复（playlist `titan_shield_regen`）

- 触发：playlist `titan_shield_regen 1`，且 `titan_shield_decay 0`。
- 规则：
  1. 每次受伤都更新"可以开始回的时刻"（`nextRegenTime`）：
     - 大伤害（≥ 49，或暴击，或带 `DF_STOPS_TITAN_REGEN`）：等待 = 线性插值（伤害 100 → 1 s，伤害 1000 → 最长等待），新时刻 = max(现在 + 等待, 旧时刻 + 等待)，两者都封顶在 现在 + 最长等待。
     - 小伤害（< 49）：至少推迟到 现在 + 0.5 s。
  2. 最长等待 = 设置文件 `titan_regen_delay`：多人 8.0 s。
  3. 到了时刻以后线性回，**6 s 从 0 回到满**（每 0.1 s 回上限的 1/60）。
  4. 濒死时不回。
- 例子：吃一发 300 → 等 1 + (300 − 100) / 900 × 7 ≈ 2.6 s 再回。吃一发 1000 以上 → 等 8 s。盾从 0 回满，最慢 8 + 6 = 14 s。
- 出处：
  - 开关：V/`_utility_shared.nut:3059–3067`；SV/`_utility.gnut:3017–3029`；PL:105–106、2286–2310（只有 `solo`）。
  - 等待：SV/`titan/_titan_health.gnut:34–35, 209–210, 826–843, 879–915`；变量 `variable_regen_delay` 默认 1（V/`_utility_shared.nut:3201–3204`，PL 里没写 → 用默认）。
  - 回复：SV/`titan/_titan_health.gnut:785–799, 807–816`；FE/`sh_consts.gnut:1063, 1068–1074`（多人等 6 / 回 6；战役 3 / 2）；P/`titan_base.set:6`。
- 多人可用：只有改 playlist。Northstar 私服的私人比赛菜单里有这个开关 [NS 社区版]（NS/`lobby/sh_private_lobby_modes_init.gnut:25`）——正好可以用来实测。
- 做进 HSD：泰坦可以"打一下、躲一下、再上"，节奏接近 Apex 的掩体回盾；泰坦更耐打，铁驭反泰坦要打出爆发才能破盾。按伤害大小变的等待，让"小刮小蹭"只推迟 0.5 s、"挨一炮"推迟到 8 s。

### 2.4 快充被动（`PAS_SHIELD_REGEN`）

- 触发：灵魂上有这个被动，且自动回复开着。
- 回多少：回满时间减半（6 → 3 s）；最长等待减 1 s（8 → 7 s）。
- 出处：SV/`titan/_titan_health.gnut:807–816, 834–835`；FE/`sh_passives.gnut:26, 131, 241`。
- 多人可用：**否**。多人装备表里没有它（NS 表 `titan_passives.csv` 只有 `pas_build_up_nuclear_core`、`pas_enhanced_titan_ai`、`pas_auto_eject`、`pas_hyper_core`、`pas_anti_rodeo`、`pas_mobility_dash_capacity`、`pas_warpfall`、`pas_bubbleshield` 和各泰坦专属）。
- 做进 HSD：可以做成一个可选芯片，让"回盾流"成为一种配装方向。

### 2.5 护盾加速被动（`PAS_SHIELD_BOOST`）

- 规则：等待固定 2 s；每 0.1 s 回 20（→ 200 /s）；开了衰减模式也照回。
- 出处：SV/`titan/_titan_health.gnut:789–790, 839–840`；SV/`_utility.gnut:3025–3026`；FE/`sh_consts.gnut:959`。
- 多人可用：**否**。没有装备表条目，也没有哪个核心发它（核心 `.txt` 的 `passive` 只有 `PAS_FUSION_CORE`、`PAS_SHIFT_CORE`、`PAS_SMART_CORE`）。是一代的遗留。
- 做进 HSD：固定速度的回复，比按比例回更好预测；可以给"重装 / 防御型"泰坦当特性。

### 2.6 衰减模式和过盾（`titan_shield_decay` + `GiveOvershield`）

- 衰减：playlist `titan_shield_decay 1` 时，护盾每个脚本帧掉 2（约 20 /s），除非正在"回复中"（见 2.3、2.5）。
  - 出处：SV/`titan/_titan_triple_health.gnut:36, 50–52, 513–524`；V/`_utility_shared.nut:3059–3062`；PL:105（默认 0）。
- 过盾：`GiveOvershield` 把护盾设满，并让衰减推迟 1 s。
  - 出处：V/`sh_passive_utility.gnut:100–109`；SV/`_utility.gnut:3031–3034`。
  - 多人可用：**否**。全部脚本（含 Northstar）里没有任何地方调用它。
- 做进 HSD："拿到一口大盾，随后慢慢漏掉"，鼓励拿到就马上打；配合击杀奖励、技能奖励很好用。衰减 20 /s 时，2500 要约 2 分钟漏完。

### 2.7 恢复泰坦（`RestoreTitan`）

- 回多少：护盾满；血不足 62.5 % 的补到 62.5 %；濒死的先救回。
- 出处：SV/`titan/_titan_health.gnut:99–115`。调用者只有战役存档点：SV/`sp/_savegame.gnut:359, 383`。
- 多人可用：否。
- 做进 HSD：适合关卡里的"检查点 / 补给站"，一次性大回复。

### 2.8 Monarch：能量虹吸（`mp_titanweapon_stun_laser`）

- 触发：虹吸的每个伤害事件。
- 回多少：
  - 打敌人：打重甲（泰坦等）自己 +750，打轻甲（铁驭、步兵等）+250；带 Shield Amplifier（`pas_vanguard_shield`）× 1.25 → 937 / 312。不超上限。
  - 打队友泰坦（升级核心给了 Energy Transfer）：队友 +750，不伤队友。× 1.25 看的是**队友**有没有 Shield Amplifier（原版写法，见 [MONARCH.md](MONARCH.md)）。
- 时间：命中当场。冷却：先等 1 s，再 12 s（120 能量，10 /s）。
- 出处：W/`mp_titanweapon_stun_laser.nut:71–139`（队友 80–104、敌人 126–135）；WT/`mp_titanweapon_stun_laser.txt:25–33`；L:11324–11325。
- 多人可用：是。
- 做进 HSD："打中才有盾"，奖励命中和贴近；打人多的场合回得多。HSD 可以把它做成任何泰坦都能有的"吸取"技能。

### 2.9 Monarch：升级核心（`mp_titancore_upgrade`）

- 触发：每次用升级核心（第 4 次起也一样）。
- 回多少：护盾回满。
- 时间：按下那一帧。核心基准充能 100 s。
- 出处：W/`mp_titancore_upgrade.nut:30–40, 298–310`；WT/`mp_titancore_upgrade.txt:26–28`。
- 多人可用：是。
- 做进 HSD：把回盾绑在核心上，核心变成"续命键"；节奏是长周期一次性。

### 2.10 核心护盾被动（`PAS_SHIELDED_CORE`）

- 触发：核心开始。
- 回多少：护盾设满；max(3 s, 核心时长) 以后**清零**（死亡、销毁时也清零）。
- 出处：W/`sh_titancore_utility.gnut:383–384, 566–583`；FE/`sh_passives.gnut:77, 172`。
- 多人可用：**否**（不在装备表）。
- 做进 HSD：核心期间的临时"无敌窗"，结束就没了，不影响长期耐久。

### 2.11 FD：Legion「Redirect」（`fd_gun_shield_redirect`）

- 触发：Legion 的枪盾挨打。
- 回多少：枪盾吃的伤害 1:1 加到 Legion 自己的护盾，不超上限。
- 时间：当场。
- 出处：W/`_vortex.nut:1551–1564`；SV/`_passives.gnut:642–647`；NS 表 `unlocks_fd_titan_level.csv:13`（11 级）。
- 多人可用：只在 FD / Aegis。
- 做进 HSD："举盾挡下来的变成自己的盾"，奖励时机对的防御。

### 2.12 FD：Ronin「Blademaster」（`fd_duration`）

- 触发：剑核心期间，每次剑命中（伤害源 `mp_titancore_shift_core`）。
- 回多少：打重甲 +500，打其他 +250，不超上限。剑核心时长也翻倍。
- 出处：W/`mp_titanweapon_sword.nut:20, 56–68`；SV/`_passives.gnut:175–179`；NS 表 `unlocks_fd_titan_level.csv:22`（20 级）；L:11681。
- 多人可用：只在 FD / Aegis。
- 做进 HSD：近战吸血式，奖励冲进去砍。

### 2.13 FD：Monarch「Energized Smoke」（`fd_vanguard_utility_1 / _2`）

- 触发：Monarch 的电烟每跳一次（每 0.1 s），烟里的自己（1 档）/ 队友泰坦（2 档）。
- 回多少：每跳 +35，不超上限。烟默认 5 s、放出 1 s 后才开始跳 → 一颗烟最多约 40 跳 ≈ 1400 [推断]。
- 出处：W/`mp_titanability_smoke.nut:98, 136–155`；SV/`superbar/smokescreen.nut:17, 185, 209–235`；SV/`_passives.gnut:282, 288`；NS 表 `unlocks_fd_titan_level.csv:4, 13`（2、11 级）；L:11659–11660。
- 多人可用：只在 FD / Aegis。2 档对队友是否真能生效，要看友军保护有没有放行这种伤害，[未知]。
- 做进 HSD："站在区域里回盾"，适合守点、团队支援。

### 2.14 FD：护盾升级（防御 2 档，各台都有）

- 不是回盾，是**加上限**：护盾上限 × 1.5（2500 → 3750）；当前值不变。
- 出处：SV/`_passives.gnut:159–161, 220–222, 291–293, 441–443, 503–505, 565–567, 632–635`；NS 表 `unlocks_fd_titan_level.csv:16`（14 级）。
- 做进 HSD：成长线上的一档；和任何回盾办法都能叠。

### 2.15 看起来像、但不是"泰坦护盾"的东西

| 东西 | 为什么不算 | 出处 |
|---|---|---|
| 降落后的穹顶护盾（Dome Shield / `pas_bubbleshield`） | 是单独的罩子实体，不加灵魂的护盾值 | SV/`titan/_titan_hotdrop.gnut:376, 440` |
| Legion 枪盾、Tone 粒子墙、Ion 涡旋 | 单独的实体，有自己的血 | 各自页面 |
| 铁驭护甲（`GiveArmor`） | 只给铁驭，泰坦直接返回 | V/`sh_powerup.gnut:251–261` |
| 战役 Boss 泰坦的血量档 | 把护盾设成 0，换成血 | SV/`ai/_ai_boss_titan.gnut:698–735` |
| 采集器、炮塔护盾 | 不是泰坦 | NS `_harvester.gnut`、Northstar.Custom `_gamemode_fw.nut` |

会**减**护盾的（做回盾时要一起考虑）：电弧炮吸盾（W/`_arc_cannon.nut:230–250`）、电磁伤害扣上限一半（W/`_weapon_utility.nut:3396–3401`，Monarch 虹吸也走这里）、强制击杀清零（SV/`titan/_titan_health.gnut:194–197`）。

## 3. 对初扫（SCAN-1108 §4）的修正

| 初扫 | 修正 | 依据 |
|---|---|---|
| 1. 生成时满 | 多人出生 **0**；只有战役 BT 满 | P/`titan_base.set:10`；SV/`titan/_titan_health.gnut:738–741` |
| 2. 电池：护盾回满，血补分段血 × 0.5 | 对。另外核心 +20 %；增幅电池血 + 2 段、可救回濒死；`battery_shield_frac` 读了没用 | SV/`rodeo/_rodeo_titan.gnut:1751–1777` |
| 3. 自动回复，默认 0，被动减半 | 对。补：等待 1–8 s 按伤害变；6 s 回满；只有 `solo` playlist 打开；减半的被动多人拿不到 | 第 2.3、2.4 节 |
| 4. `RestoreTitan`：回满、血到 62.5 % | 数对，但只有战役存档点调用，多人没有 | SV/`sp/_savegame.gnut:359, 383` |
| 5. Monarch 虹吸和升级核心 | 对。补：虹吸 +750 / +250（× 1.25）、Energy Transfer 给队友 +750；升级核心每次回满 | 第 2.8、2.9 节 |
| 6. `PAS_SHIELDED_CORE` | 规则对，但多人装备表里没有 | FE/`sh_passives.gnut:77`；NS 表 `titan_passives.csv` |
| 7. `GiveOvershield`：回满，推迟 1 s 衰减 | 规则对，但**没有任何地方调用**，是死代码 | 全文搜索 |
| 8. FD：Legion 1:1、Ronin +500 / +250、Monarch 烟雾 +35 | 对。补：烟是每 0.1 s 一跳；Ronin 只在剑核心期间 | 第 2.11–2.13 节 |
| 漏掉的 | `PAS_SHIELD_BOOST`（固定 200 /s，拿不到）；衰减模式；FD 护盾上限 × 1.5；救回濒死会把护盾清零 | 第 1、2.5、2.6、2.14 节 |

## 4. 选项总表（给用户挑）

| 选项 | 回多少 | 什么时候 | 适合 HSD 的哪种玩法 | 代价 / 注意 |
|---|---|---|---|---|
| A 不回（TF2 默认），出生 0 | 0 | — | 护盾全靠下面的"挣"；泰坦是消耗品，打一架就少一截 | 单独用的话，护盾这个系统等于没有 |
| B 出生满盾 | 满 | 每台新泰坦一次 | 召唤即有缓冲，第一波交火宽松 | 只管第一次；后面仍要配别的 |
| C 自动回复（TF2 playlist 版） | 6 s 回满 | 受伤后等 1–8 s（按伤害大小） | 打了躲、躲了打；掩体战 | 泰坦变耐打，铁驭反泰坦要爆发；HSD 现占位就是这个的简化版 |
| C′ 自动回复 + 快充 | 3 s 回满 | 等 0–7 s | 做成可选芯片的"回盾流" | 同上，更强 |
| D 固定速度回复（`PAS_SHIELD_BOOST` 式） | 200 /s | 等 2 s | 防御型泰坦的特性 | 和按比例回相比，上限高的泰坦回得相对慢 |
| E 过盾 + 衰减 | 一次回满，之后约 20 /s 漏掉 | 触发时（击杀、技能、补给） | 拿到马上打，进攻节奏 | 要配触发条件；不触发就一直往下掉 |
| F 电池 / 补给拾取 | 满盾 + 1250 血 + 20 % 核心 | 拿到并插上 | 铁驭泰坦配合、地图资源争夺 | HSD 现在不做拾取循环 |
| G 打中回盾（虹吸式） | 每次命中 +750（打泰坦）/ +250（打步兵） | 命中当场；技能冷却约 13 s | 奖励命中和贴近；PvE 打步兵也能回 | 打步兵多的关卡回得很快，要看敌人密度调 |
| H 核心回满 | 满 | 每次用核心 | 核心当"续命键"，长周期 | 核心充能慢的话几乎感觉不到 |
| I 核心期间临时满盾 | 满，结束清零 | 核心期间（至少 3 s） | 核心是短暂的无敌窗 | 不提高长期耐久 |
| J 挡伤转盾（Redirect 式） | 挡下的伤害 1:1 | 举盾挡住时 | 奖励时机对的防御 | 要有一个可举的盾 |
| K 近战命中回盾（Blademaster 式） | +500 / +250 每次 | 某个状态里近战命中 | 冲进去砍的近战流 | 要有近战为主的泰坦 |
| L 区域回盾（电烟式） | +35 每 0.1 s（约 350 /s） | 站在自己（或队友）的区域里 | 守点、团队支援 | 区域要有时长和冷却 |
| M 检查点恢复（RestoreTitan 式） | 满盾，血到 62.5 % | 关卡检查点 / 补给站 | 关卡制 PvE | 只适合有关卡结构的模式 |
| 上限加成（FD 护盾升级） | 上限 × 1.5 | 成长 / 升级 | 成长线 | 不是回复，和任何一项叠 |

这些选项可以组合，比如 A + G + H（TF2 Monarch 的多人体验），或 B + C（Apex 式）。

## 5. 要实测

只在用户挑中某项以后才需要。私服能直接测的：
- 自动回复（私人比赛打开 `titan_shield_regen`）：
  - 受伤到开始回的时间，对伤害 50、100、300、600、1000、2000 各测一次（验证 1–8 s 插值和"取较晚者"）。
  - 回满时间（期望 6 s）和曲线是否线性。
  - 连续小伤害（< 49）能不能一直压着不让回。
- 出生护盾：召唤一台泰坦，上机后记护盾值（期望 0 / 2500）。
- 电池：插一个普通电池前后的护盾、血、核心表。
- 虹吸：打一台 NPC 泰坦一次，记自己护盾增加多少、是一次还是几次伤害事件（[MONARCH.md](MONARCH.md) 第 3 节也列了）。

记录用服务端 `AddDamageFinalCallback( "player", f )` 和每 0.1 s 读一次 `soul.GetShieldHealth()`。

## 6. 能脱离 TF2 照做的 / 还缺的

**能照做的：**
- 护盾的存放、上限、先扣盾、穿盾、濒死时的规则。
- 每一种回盾办法的触发、数量、时间（第 2 节全有出处）。
- 自动回复的完整公式（等待插值、取较晚者、小伤害 0.5 s、线性回复）。
- 衰减模式的速度、过盾的推迟。

**还缺的：**
- 用户拍板：HSD 用哪几项（第 4 节）。
- 自动回复公式的实测确认（脚本帧率会影响"每帧回多少"，但脚本按实际帧间隔折算，总时间应不受影响）。
- 电烟 2 档对队友是否生效 [未知]（FD 专属，不影响 HSD 选择）。

**11-08 实测补上的：** 多人泰坦出生时护盾是 0 / 2500（每次 `hsd_kit_info` 都是 `shield=0/2500`，运行 `20261108_131828_kit_a` 等），和第 1 节一致；Monarch 虹吸 +937、升级核心回满 2500，见 [MONARCH.md](MONARCH.md) 第 8 节。
