# TF2 Frontier Defense：能读到的规则（FD-RULES）

会话 `tf2-ai-spec`，2026-11-08。任务来源：[../MUST-RUN-1108.md](../MUST-RUN-1108.md) 第 1 项（f）。敌人规格见 [AI-SPEC.md](AI-SPEC.md)。

性质：只读整理，没有开游戏　　用途：HSD（Unity PvE）照着搭 FD 的骨架。TF2 只当研究来源，只借规则和数字，不用模型、声音、UI 美术。

---

## 先说结论

1. **每一波刷什么敌人、刷多少、什么时候刷，本地没有任何文件。** FD 的服务端脚本是空壳（Northstar 只有 11 行的 `_gamemode_fd.nut` 和 12 个 8 字节的地图脚本），零售包里也没有多人 FD 模式脚本。下面所有内容都来自客户端 / 共享脚本、战役包里顺带的服务端共用脚本、数据表和 playlist。
2. **难度**：5 档（Easy / Regular / Hard / Master / Insane）。差别全在 playlist 变量：敌方泰坦血量 −5000 / −2500 / 0、死神血量 −2000 / −1000 / 0、玩家受伤倍率 1.0 / 1.0 / 1.5 / 2.5 / 2.5、每波给钱 700 / 700 / 600 / 600 / 600、采集器护盾 6000 / 6000 / 5000 / 4000 / 4000 等。这些变量怎么用（服务端代码）没有，含义按变量名推断。Insane 另外：小地图隐藏、只有一次机会、敌方泰坦头顶没有图标。Hard / Master / Insane 分别要任一泰坦 Aegis 等级达到 5 / 11 / 14 才解锁。
3. **一局的结构**：每张图 5 波（每图正好 5 个波次名）；波次状态 5 个（无 / 来袭 / 进行中 / 完成 / 波间）；波间开商店，默认 60 s，全员按"准备"可提前开打；采集器被打爆就整波重来，非 Insane 最多 3 次（推断：2 次重试），Insane 1 次。
4. **钱**：每人最多 5000；每波结束给 `fd_money_per_round`，另有三项各 100 的奖金（没死、本波 MVP、采集器没掉血）；可以 100 一次地存进 / 取出"团队储备"，或给队友 100。**按击杀给钱：文件里没有证据**（击杀有 1–5 的计分事件，但不是钱的证据）。
5. **商店 6 样东西**：增幅武器 100、强化电池 400、核弹骑乘 500、电弧陷阱 650、哨戒炮 1200（每人同时最多 2 个）、采集器护盾增强 1200（无敌 5 s）。SCAN-1108 列的"电浆炮塔 1200"在 FD 商店表里**没有上架**（见 §4.6）。
6. **采集器**：血 25000，护盾按难度 6000–4000；受伤 10 s 后开始回盾，10 s 回满；能用电池修（修多少没有）；被毁时给出"伤害最多的 3 类敌人 + 占比 + 提示"。
7. **泰坦 Aegis 升级**：每台泰坦 24 级，总经验 440；第 2 / 5 / 8 / 11 / 14 / 17 / 20 级各解锁 1 个升级（5 级必是加血 +2500，14 级必是护盾 ×1.5，20 级是终极升级），其余等级只给外观奖励。**每个升级的具体数值都在零售脚本和武器文件里，能逐条读到**（§6.3）。FD 里还有一组不靠升级、一直生效的平衡改动（`fd_balance`，§6.4）。
8. **能照做的**：难度表、状态机和计时、HUD 内容、经济和商店、FD 版敌人 / 炮塔 / 陷阱数值、采集器数值、Aegis 全表和数值、结算奖章。**缺的**：波次内容、按击杀的收入（如果有）、重试次数的确切来源、MVP 怎么算、采集器修理量、难度变量的具体用法、AI 泰坦的 FD 行为（除核弹泰坦）、Aegis 经验的具体发放公式（只有常量）。见 §8。

---

## 0. 资料来源和可信度

### 0.1 路径缩写

| 缩写 | 实际路径 | 是什么 | 可信度 |
|---|---|---|---|
| V | `TF2-Research/local/vpk/client_mp_common/scripts/vscripts/` | 零售多人客户端 / 共享脚本 | 零售原文 |
| F | `TF2-Research/local/vpk/client_frontend/scripts/vscripts/` | 零售前端 / 共享脚本（`sh_consts`、`_items`、商店、UI；部分文件带 `#if SERVER` 分支） | 零售原文 |
| SV | `TF2-Research/local/vpk/client_sp_training/scripts/vscripts/` | 战役包里的服务端共用脚本，带 `#if MP` 分支（Aegis 升级的实现就在这里） | 零售原文 |
| AS | `TF2-Research/local/vpk/client_mp_common/scripts/aisettings/` | NPC 设置 | 零售原文（与 Northstar 同名文件逐个比较过，17 个 FD 文件内容相同） |
| WT | `TF2-Research/local/vpk/client_mp_common/scripts/weapons/` | 武器 .txt（含 `fd_*` mod） | 零售原文 |
| PS | `TF2-Research/local/vpk/client_mp_common/scripts/players/mp/` | 泰坦 .set 文件 | 零售原文 |
| DD | `TF2-Research/local/vpk/client_mp_common/scripts/damage/damagedefs.txt` | 伤害定义 | 零售原文 |
| L | `TF2-Research/local/vpk/client_frontend/resource/r1_english.txt` | 英文本地化（UTF-16；行号按转成 UTF-8 后计，行数不变） | 零售原文 |
| DT | `HSD-RawData/tf2/northstar-1.31.14/mods/Northstar.CustomServers/mod/scripts/datatable/` | 数据表 CSV | Northstar 随包的 CSV；零售脚本读的是同名 `datatable/*.rpak`（如 F/burnmeter/sh_boost_store.gnut:89）。零售 rpak 本地没解包，**没逐字核对** |
| PL | `HSD-RawData/tf2/northstar-1.31.14/runtime/compiled/mod_original_playlists_v2.txt` | playlist（`versionNum 3246`，PL:4） | 文件名写着 original，推断是 Respawn 原版 playlist |
| NS | `HSD-RawData/tf2/northstar-1.31.14/mods/Northstar.CustomServers/mod/scripts/vscripts/` | Northstar 服务端脚本，部分是社区重写 | 标（Northstar） |
| NC | `<TF2>/R2Northstar/mods/Northstar.Client/mod/scripts/vscripts/`（这个 mod 没有存档，只有这一处引用，Northstar 开源可再下载） | Northstar 客户端 | 标（Northstar） |

### 0.2 FD 服务端是空壳（核对过）

| 事实 | 出处 |
|---|---|
| Northstar 的 FD 服务端只有两个空函数：`GamemodeFD_Init` 只预载一个模型，`RateSpawnpoints_FD` 是空的 | NS/gamemodes/_gamemode_fd.nut:1-11 |
| 12 个 FD 地图脚本每个 8 字节，只有一行注释：angel_city、black_water_canal、colony02、drydock、forwardbase_kodai、glitch、grave、homestead、relic02、rise、thaw、wargames | NS/mp/levels/*_fd.nut |
| Northstar 客户端把 `fd_easy`–`fd_insane` 列为"未完成"，在模式菜单里屏蔽 | NC/ui/menu_mode_select.nut:19-24 |
| Northstar 写的采集器脚本只有"生成"，没有回盾、修理、失败判定 | NS/_harvester.gnut:1-79（Northstar） |
| Northstar 写的商店物品回调，注释自己说 FD 不支持 | NS/burnmeter/_burnmeter.gnut:51（Northstar） |

结论：**波次内容（每波哪些敌人、几个、怎么出场、间隔）、波次推进的服务端逻辑、钱和 MVP 的计算、采集器修理，本地都没有。**

---

## 1. 难度

### 1.1 五档的 playlist 变量（全表）

`fd` 是基础块（PL:627-710），五档都 `inherit fd`，只覆盖下表里列出的变量。没覆盖的沿用 `fd` 的值。

| 变量 | fd 基础 | easy | normal（Regular） | hard | master | insane | 含义 |
|---|---|---|---|---|---|---|---|
| `fd_difficulty` | —（defaults 0，PL:118） | 0（PL:722） | 1（PL:748） | 2（PL:774） | 3（PL:800） | 4（PL:827） | 难度序号，客户端用（V/gamemodes/sh_gamemode_fd.nut:662-686；枚举 F/sh_consts.gnut:2733-2740） |
| `fd_titan_health_adjust` | 0（PL:662） | −5000（PL:724） | −2500（PL:750） | 0（PL:776） | 0（PL:803） | 0（PL:832） | 敌方泰坦血量加减（推断） |
| `fd_reaper_health_adjust` | 0（PL:663） | −2000（PL:725） | −1000（PL:751） | 0（PL:777） | 0（PL:804） | 0（PL:833） | 死神血量加减（推断） |
| `fd_mortar_spectre_setup_time` | 5（PL:664） | 10（PL:726） | 10（PL:752） | 5（PL:778） | 5（PL:805） | 5（PL:834） | 迫击炮幽灵就位到开火的准备秒数（推断） |
| `fd_grunt_at_weapon_users` | 0（PL:665） | 0（PL:727） | 0（PL:753） | 2（PL:779） | 4（PL:806） | 4（PL:835） | 步兵里拿反泰坦武器的人数（推断） |
| `fd_grunt_shield_captains` | 0（PL:666） | 0（PL:728） | 0（PL:754） | 0（PL:780） | 1（PL:807） | 1（PL:836） | 是否出盾兵队长（推断） |
| `fd_player_damage_scalar` | 1.0（PL:667） | 1.0（PL:729） | 1.0（PL:755） | 1.5（PL:781） | 2.5（PL:808） | 2.5（PL:837） | 玩家受伤倍率（推断） |
| `fd_harvester_health` | 25000（PL:668） | — | — | — | — | — | 采集器血量（推断） |
| `fd_harvester_shield` | 6000（PL:669） | 6000（PL:732） | 6000（PL:758） | 5000（PL:784） | 4000（PL:811） | 4000（PL:840） | 采集器护盾（推断） |
| `fd_harvester_regen_delay` | 10.0（PL:670） | — | — | — | — | — | 受伤后开始回盾的延迟 s（推断；与 F/sh_consts.gnut:1691 `GENERATOR_SHIELD_REGEN_DELAY = 10.0` 一致） |
| `fd_harvester_regen_time` | 10.0（PL:671） | — | — | — | — | — | 护盾从空回满的时间 s（推断；与 F/sh_consts.gnut:1692 一致） |
| `fd_money_per_round` | 600（PL:672） | 700（PL:730） | 700（PL:756） | 600（PL:782） | 600（PL:809） | 600（PL:838） | 每波结束的"本波完成"奖金。**客户端确实读它**：设成 `FDTeamWave` 计分事件的值（V/gamemodes/sh_gamemode_fd.nut:118-120，取不到时默认 500）。同文件另有常量 `FD_MONEY_PER_ROUND` 700 / `_HARD` 600（V/gamemodes/sh_gamemode_fd.nut:78-79），客户端没用到 |
| `fd_wave_buy_time` | 60.0（PL:673） | — | — | — | — | — | 波间购物时间 s。客户端只用它算"下波敌人列表"的显示时长（V/gamemodes/cl_gamemode_fd.nut:1123-1124）；商店实际开多久由服务端定（推断就是这个值） |
| `fd_pro_titan_shields` | 0（PL:674） | 0（PL:731） | 0（PL:757） | 0（PL:783） | 1（PL:810） | 1（PL:839） | 敌方泰坦护盾加强（推断） |
| `fd_at_unlimited_ammo` | 1（PL:675） | 1（PL:733） | 1（PL:759） | 1（PL:785） | 0（PL:812） | 0（PL:841） | 反泰坦武器无限弹药（推断；对象是玩家还是 AI 不清楚） |
| `boost_store_team_reserve` | —（未设，UI 默认 0） | 1（PL:723） | 1（PL:749） | 1（PL:775） | 1（PL:801） | 1（PL:828） | 开团队储备（存取钱）。UI 读（F/ui/menu_boost_store.nut:272-295, 317, 350） |
| `earn_meter_pilot_multiplier` | 0.5（PL:683） | 0.7（PL:735） | 0.7（PL:761） | 0.7（PL:787） | 0.7（PL:814） | 0.5（PL:843） | 铁驭攒泰坦进度的倍率（SV/earn_meter/sv_earn_meter.gnut:70-76, 206-210） |
| `riff_minimap_state` | 0（defaults，PL:80） | — | — | — | — | 1（PL:829） | 1 = `eMinimapState.Hidden`（F/sh_consts.gnut:1372-1378），小地图不画（V/client/cl_main_hud.nut:864-869） |
| `roundscorelimit` | 3（PL:639） | — | — | — | — | 1（PL:830） | 局数上限。客户端用它判断"重试用完"（V/gamemodes/cl_gamemode_fd.nut:2102-2108 的 `HasRoundScoreLimitBeenReached`）。推断：非 Insane 共 3 次机会，Insane 1 次 |

难度显示名：EASY / REGULAR / HARD / MASTER / INSANE（L:11510-11514）。playlist 一句话说明（PL:4175-4187，英文原文是短句，这里意译）：Easy 碾压对手；Regular 推荐有经验的玩家；Hard 需要技术；Master 只有最强的人能过；Insane 你活不下来。

### 1.2 `fd` 基础块里的其他变量（五档共用）

| 变量 | 值 | 出处 | 含义 |
|---|---|---|---|
| `max_players` / `max_teams` | 4 / 1 | PL:643, 653 | 4 人合作，一个队 |
| `respawn_delay` | 4 | PL:650 | 铁驭死后重生延迟 s（推断） |
| `riff_wave_spawn` | 4 | PL:654 | `eWaveSpawnType.DROPSHIP`（F/sh_consts.gnut:1326-1333）：乘运输机成批重生 |
| `wave_spawn_interval` | 25 | PL:655 | 成批重生的间隔 s（F/_settings.nut:926-927 读它；FIXED_INTERVAL 的注释说"每隔 N 秒"） |
| `titan_build_time` / `titan_rebuild_time` | 240 / 240 | PL:647-648 | 泰坦首次 / 再次可用的建造时间 s（推断） |
| `earn_meter_tick_frac` | 0 | PL:659 | 泰坦进度不随时间自动涨（推断） |
| `earn_meter_titan_multiplier` | 0.5 | PL:682 | 泰坦攒核心的倍率（SV/titan/_titan_health.gnut:60, 990） |
| `riff_team_share_earn_meter` / `…_scale` | 2 / 0.25 | PL:680-681 | 2 = `OwnedOnly`（F/sh_consts.gnut:1316-1324）：自己攒到的泰坦进度，按 0.25 分给活着的队友（SV/earn_meter/sv_earn_meter.gnut:153-175） |
| `pick_loadout_extension` | 30.0 | PL:634 | 选配装时间延长 s（推断） |
| `tts_menu_join_in_progress` / `tts_menu_show_score` | 1 / 0 | PL:637-638 | 中途加入也弹选泰坦菜单、选泰坦菜单不显示分数（推断） |
| `roundtimelimit` / `timelimit` / `scorelimit` / `suddendeath_timelimit` | 60.0 / 30 / 2500 / 2 | PL:640, 651, 645, 646 | 通用局时上限，FD 里怎么用不清楚 |
| `spawn_zone_enabled` | 1 | PL:649 | |
| `ai_attack_tethers` | 0 | PL:660 | AI 不打系留陷阱（推断） |
| `waiting_for_players_percentage_desired` | 100 | PL:661 | 等满人才开（推断） |
| `boost_store_mode` | fd | PL:656 | 商店只上 `modes` 含 `fd` 的物品（F/burnmeter/sh_boost_store.gnut:174-192） |
| `aegis_upgrades` | 1 | PL:678 | 开 Aegis 升级（SV/_passives.gnut:47-48, 889-890） |
| `override_boost_cost_…`（6 项） | −1 | PL:685-690 | −1 表示用表里的价格（F/burnmeter/sh_boost_store.gnut:737-745：只有 >0 才覆盖） |
| `ingame_menu_fd_mode` | 1 | PL:633 | |
| `color` | 0 184 254 255 | PL:677 | |

地图池（8 张，五档相同）：`mp_forwardbase_kodai`、`mp_black_water_canal`、`mp_homestead`、`mp_wargames`、`mp_rise`、`mp_thaw`、`mp_drydock`、`mp_angel_city`（PL:701-708；各难度列表 PL:1718-1790 一样）。另有一个对外 playlist `fd_insane` 只放 `mp_homestead`（PL:2184-2211，`promo_note #MP_HOMESTEAD`，推断是限时推广）。`fd_dev` = `fd_hard` 去掉选配装延长（PL:2214-2221）。

### 1.3 解锁门槛

| 难度 | 条件 | 出处 |
|---|---|---|
| Easy / Regular | 无 | — |
| Hard | 统计 `fd_stats.highestTitanFDLevel` ≥ 5（任一泰坦的最高 Aegis 等级） | F/_items.nut:1771 |
| Master | ≥ 11 | F/_items.nut:1772 |
| Insane | ≥ 14 | F/_items.nut:1773 |

选泰坦时每台泰坦另有锁定状态（由服务端写进持久数据 `titanClassLockState`）：可用 / 建议等级 / 锁定 / 需要等级 / 已被队友选用（F/sh_consts.gnut:2697-2701；F/sh_loadouts.nut:4006-4012）。菜单显示"本难度需要 / 建议 Aegis 等级 N"和"这台泰坦已被使用"，N 取上表的门槛值（F/ui/menu_team_titan_select.nut:500-535；L:11497-11500）。什么时候判"需要"、什么时候判"建议"由服务端定。

### 1.4 各难度的额外规则

| 规则 | 哪几档 | 出处 |
|---|---|---|
| 小地图隐藏 | Insane | PL:829 + V/client/cl_main_hud.nut:864-869 |
| 只有一次机会（局数上限 1） | Insane | PL:830 |
| 敌方 AI 泰坦头顶不显示类型图标 | Insane（`difficulty < INSANE` 才加） | V/gamemodes/cl_gamemode_fd.nut:644-650 |
| 铁驭攒泰坦进度 0.5（其他四档 0.7） | Insane | PL:843 |
| 开场音乐分三档：Easy/Regular、Hard、Master/Insane | — | V/gamemodes/cl_gamemode_fd.nut:2135-2168, 2185-2218 |
| 结算 Aegis 经验倍率：Hard ×2、Master ×3、Insane ×4 | — | L:11881-11883；F/sh_consts.gnut:2703-2707（§7.4） |

---

## 2. 波次状态机

### 2.1 状态常量

| 值 | 名字 | 出处 |
|---|---|---|
| 0 | `WAVE_STATE_NONE` | V/gamemodes/sh_gamemode_fd.nut:72 |
| 1 | `WAVE_STATE_INCOMING` | :73 |
| 2 | `WAVE_STATE_IN_PROGRESS` | :74 |
| 3 | `WAVE_STATE_COMPLETE` | :75 |
| 4 | `WAVE_STATE_BREAK` | :76 |

HUD 里能用的状态文字：Incoming / Complete（L:11561-11562），"Next Wave"、"Wave N in: …"（L:11556-11558）。状态之间怎么切由服务端决定，客户端只显示 `FD_waveState`（V/gamemodes/cl_gamemode_fd.nut:520）。

### 2.2 网络变量（服务端写、客户端读）

全部在 V/_remote_functions_mp.gnut:380-445 注册：

| 变量 | 类型 | 用途 |
|---|---|---|
| `FD_waveState` | 全局 int | 上表状态 |
| `FD_waveActive` | 全局 bool | 波次是否进行中（进行中不能给队友钱、能用护盾增强） |
| `FD_totalWaves` / `FD_currentWave` | 全局 int | 总波数 / 当前波（0 起；显示时 +1） |
| `FD_activeHarvester` | 全局 entity | 当前采集器 |
| `FD_restartsRemaining` | 全局 int | 剩余重试次数 |
| `FD_AICount_<类型>`（12 个） | 全局 int | 各类敌人剩余数（§3.1） |
| `FD_AICount_Current` / `FD_AICount_Total` | 全局 int | 本波剩余 / 总数 |
| `FD_wavePoints` / `FD_wavePoints256` | 全局 uint | 团队本波分数（客户端读了但没用，cl_gamemode_fd.nut:287-288） |
| `FD_harvesterInvulTime` | 全局 time | 采集器无敌到何时 |
| `FD_nextWaveStartTime` | 全局 time | 下一波开始时刻（HUD 倒计时） |
| `FD_readyForNextWave` | 每人 bool | 是否已准备 |
| `boostStoreOpen` | 全局 bool | 商店是否开 |
| `FD_money` / `FD_money256` | 每人 uint | 钱 = money256 × 256 + money（F/burnmeter/sh_boost_store.gnut:337-347, 676-680） |
| `numSuperRodeoGrenades` / `numHarvesterShieldBoost` | 每人 int | 核弹骑乘 / 护盾增强的持有数 |
| `playerHasBatteryBoost` | 每人 bool | V/_remote_functions_mp.gnut:435 |
| `burn_turretLimit` | 全局 int，默认 5 | V/_remote_functions_mp.gnut:915 |

### 2.3 一波的流程（客户端能看到的部分）

服务端触发什么事件、客户端怎么反应，是读得到的；事件的先后是按代码推断的（推断）。

| 顺序 | 服务端发给客户端 | 客户端表现 | 计时 | 出处（V/gamemodes/cl_gamemode_fd.nut） |
|---|---|---|---|---|
| 开局 | 进入 Playing | 7 s 后弹"采集器"教学卡（首次） | 7 s | 2286-2291 |
| 波间开始 | `FD_AnnounceWaveEnd`（上一波结束时） | 大字"WAVE COMPLETE"；放胜利音乐后转"等待下一波"循环音乐；第一波结束 4 s 后弹"波间"教学卡 | 4 s | 1304-1325 |
| 结算奖金 | `FD_NotifyWaveBonusIncoming` | 列出 4 项奖金（本波完成 / 没死 / 本波 MVP / 采集器没掉血），拿到的打绿勾并显示钱数；保持 20 s | 20 s，每项间隔 0.25 s | 1334-1404, 1423-1433, 1501-1511 |
| | `ServerCallback_FD_MoneyFly( 玩家, 数额 )` | 在该玩家头上飘出数字 | — | 1683-1696 |
| | `ServerCallback_FD_NotifyMVP( 玩家 )` | MVP 那一项改成"Wave MVP - 名字" | — | 2473-2482 |
| 商店开 | `boostStoreOpen` 变 true；`ServerCallback_FD_NotifyStoreOpen` | 商店图标出现并闪 10 s；状态栏加"Armory Open"；出现"按键准备"框 | 闪 10 s，每 0.5 s 一次 | 366-382, 412-433, 1513-1557, 1641-1644 |
| 准备 | 玩家按 `+scriptCommand1` → `FD_ToggleReady` | 切换准备；队友都准备而你没有时，2 s 后播"你还没准备"的语音（≥2 人时） | 2 s；准备音效 3 s 节流 | 435-500, 2025-2042 |
| 下波预告 | `ServerCallback_FD_AnnouncePreParty( 最多 9 个类型 id )` | 屏幕侧边逐行列出下一波的敌人类型和数量（每行晚 0.75 s）；记分板同步列出；商店开着时保持 `fd_wave_buy_time × 2` = 120 s，否则 10 s | 120 s / 10 s | 907-965, 1117-1198 |
| 商店将关 | `FD_StoreClosing` | 横幅"Armory Closing"3.5 s；状态栏倒数"Armory Closing in… N"，从 4 s 倒数 | 4 s | 1646-1681 |
| 开打 | `FD_AnnounceWaveStart` | 横幅"Wave N"或"Final Wave"，副标题是本图本波名字（§2.8），12 s；按总波数逐个响刻度音；音乐按第一波 / 中间 / 最后一波分三种 | 12 s；刻度 1.5 s 后开始，每个 0.15 s | 1218-1302 |
| | 开打 12 s 后 | 对本波首次出现的敌人类型弹教学卡（每次只弹一张，10 s） | 12 s / 10 s | 1232-1234, 1269-1274, 244-253 |
| 进行中 | `ServerCallback_FD_UpdateWaveInfo` | 刷新记分板上的敌人类型和剩余数 | — | 861-905 |
| 最后一波开打 | `FD_waveActive` 变 true 且是最后一波 | 隐藏钱数显示（推断：最后一波后没有商店） | — | 395-410 |
| 波中提示 | `ServerCallback_FD_PingMinimap( x, y, 时长, 散布, 半径, 颜色 )` | 在小地图上随机抖动地连续打点，每 0.6–1.0 s 一次 | — | 1435-1471 |

教学卡的完整列表：Frontier Defense、商店、商店介绍、团队储备、Hard / Master / Insane、波间、采集器、电弧陷阱、哨戒炮、核弹骑乘，以及 11 类敌人（F/sh_consts.gnut:2743-2768）。是否看过存在持久数据 `fdTutorialBits`（V/gamemodes/cl_gamemode_fd.nut:190, 236）。买完东西后会按"电弧陷阱 → 哨戒炮 → 核弹骑乘"的顺序弹一张没看过的卡（V/gamemodes/cl_gamemode_fd.nut:982-1032）。

### 2.4 HUD 显示了什么

| 位置 | 内容 | 出处 |
|---|---|---|
| 顶部模式栏（`ui/gamestate_info_fd.rpak`） | 采集器护盾比例、采集器血量、剩余敌人 / 总数、护盾增强剩余时间、下一波开始时刻、当前波 / 总波数、波次状态、剩余重试、难度名、"Armory Open / Closing in N"、是否已准备、是否重来过 | V/gamemodes/cl_gamemode_fd.nut:507-526, 1641-1681, 502-505 |
| 钱数 | `FD_money` 实时显示；最后一波隐藏 | :305-308, 395-410 |
| 采集器头顶图标 | 贴屏幕边缘显示方向，96×96 | :535-540 |
| 采集器受击 | 记分板图标闪：有盾时蓝色、大小 3；没盾时按血量 100 %→50 % 从敌方色渐变到纯红，大小 6 | :545-583 |
| 敌方泰坦 | 头顶类型图标（Insane 没有）；小地图用类型图标 | :644-650, 785-801 |
| 小型敌人 | 小地图一直显示小点；死神用铁驭图标；隐身无人机专用图标 | :803-824 |
| 物件图标 | 弹药箱、商店、电池交换点、迫击炮点位（带进度弧）、采集器修理口 | :652-680 |
| 我的炮塔 | 每台一条：击杀数、是否在线（血量 > 1 才算在线） | :585-642 |
| 记分板 | 难度、"Wave N / Final Wave"、地图名；本波敌人图标和实时剩余数；每人最多 6 个道具图标（炮塔、护盾增强、核弹骑乘） | :174-178, 861-905, 2449-2471 |
| 队友状态 | 商店开着时显示"已准备 / 未准备" | :2044-2054 |
| 小地图 | 缩放 3.0，尺寸 1.5 | :96-97 |

### 2.5 失败和重试

| 事 | 规则 | 出处 |
|---|---|---|
| 失败条件 | 采集器被毁（客户端只看到结果：`ServerCallback_FD_DisplayHarvesterKiller`） | V/gamemodes/cl_gamemode_fd.nut:1917-2011 |
| 失败画面 | "Harvester Destroyed" 2 s → 伤害报告：最多 3 类敌人，各自图标和占采集器总伤害的百分比（向下取整；占比为 0 的不列），加一条提示，加剩余重试。报告在横幅之后再等 2 s 出现，持续 `GAME_WINNER_DETERMINED_WAIT`（6.0 s，F/_settings.nut:579）+ 2 s = 8 s；每列一类敌人间隔 0.75 s 响一声 | :1943-1997, 2013-2023 |
| 没有凶手时 | 等 6 s 后显示"Try Again!"和剩余重试，4 s | :1998-2010 |
| 重试 | `FD_WaveRestart`：横幅"Wave Restarting"+ 剩余次数，3.5 s；有剩余时播"重来"语音，否则播"最后一次"语音 | :1473-1491 |
| 剩余次数 | 全局 `FD_restartsRemaining`，服务端 `FD_SetNumAllowedRestarts` 设、`FD_DecrementRestarts` 减 | V/gamemodes/sh_gamemode_fd.nut:598-623 |
| 是否重来过 | `GetRoundsPlayed() > 0`（每次重来是新的一局 round） | :588-591 |
| 游戏结束 | 民兵队（玩家）赢，或进入"胜负已定"且没有剩余重试 | :626-635 |
| 重试时的运输机 | 不是开局的三段随机动画之一，换成专用的"重来"动画和三组随机对白 | V/gamemodes/cl_gamemode_fd.nut:1733-1771, 1797-1818 |
| 重试次数的值 | 文件里没有。推断：`roundscorelimit` 3 → 2 次重试，Insane 1 → 0 次（§1.1） | — |

本地化有"剩余 N 次 / 1 次 / 没有"三种说法（L:3819-3821）。

### 2.6 胜利和结算

| 事 | 内容 | 出处 |
|---|---|---|
| 胜利音乐 / 失败音乐 | 胜：通关；负且还有重试：本波失败；负且没重试：整局失败 | V/gamemodes/cl_gamemode_fd.nut:2084-2112 |
| 结算画面 | `ServerCallback_ShowGameStats`：每人一张奖章卡（§7.5），每张晚 0.75 s | :2241-2279 |
| 胜负提示 | 胜："保住了采集器并击溃了敌军"；负："没保住采集器"（意译） | L:11550-11551 |
| 结算常量 | 胜 / 负公告 13 s；公告到星级 8 s；星级显示 5 s，间隔 1 s | F/sh_consts.gnut:1685-1689（是否用于 TF2 FD 不确定，可能是 TF1 合作模式遗留） |

### 2.7 每张图几波

- 波数由服务端设 `FD_totalWaves`，本地没有。
- 每张图在本地化里正好有 5 个波次名（`<地图>_FD_WAVE_1`–`5`），客户端按这个键取名（V/gamemodes/cl_gamemode_fd.nut:1238）。**推断每张图 5 波。**
- 最后一波显示"Final Wave"，其余显示"Wave N"（V/gamemodes/cl_gamemode_fd.nut:1907-1915；L:3812-3813）。

### 2.8 波次名（L:11955-12019）

地图池里的 8 张：

| 地图 | 第 1 波 | 第 2 波 | 第 3 波 | 第 4 波 | 第 5 波 | 出处 |
|---|---|---|---|---|---|---|
| Forwardbase Kodai | King of the Hill | Vantage Point | Over, Under, and Around | Valley of the Blind | All Your Forward Base | L:11997-12001 |
| Black Water Canal | Enemy at the Gate | Besieged | Into the Breach | Divide and Conquer | Might and Main | L:11961-11965 |
| Homestead | Welcome Home | Country Roads | The Hornet's Nest | Home is Where the Hurt is | The Nuclear Family | L:12015-12019 |
| Wargames | Not a Drill | Escalation | Shock and Awe | War is Not a Game | Rolling Thunder | L:12009-12013 |
| Rise | Containment | Repositioning | 100% SNAFU | Wind Blows, Fire Burns, Rain Falls | Veni, vidi, vici | L:11979-11983 |
| Thaw | Not a Drill | Escalation | Shock and Awe | War is Not a Game | Rolling Thunder | L:11985-11989 |
| Drydock | Not a Drill | They've Got No Bullets | Blinded by Science | War is Not a Game | Wind blows, fire burns, rain falls | L:11991-11995 |
| Angel City | Not a Drill | Escalation | Shock and Awe | War is Not a Game | Rolling Thunder | L:11955-11959 |

不在地图池里、但有波次名的：Colony（L:11967-11971）、Glitch（L:11973-11977）、Eden（L:12003-12007，名字后面带 `[temp]`）。Grave、Relic 有 Northstar 地图脚本空壳但没有波次名。

另有一批 `WAVE_NAME_*`（L:4055-4118，如 Angel City / Colony / Fracture / Overlook…），按命名和地图推断是 TF1 合作模式的遗留，TF2 FD 的客户端不读它们（`AddWaveName` 在客户端没有任何调用，V/gamemodes/sh_gamemode_fd.nut:554）。

---

## 3. 敌人

### 3.1 `eFD_AITypeIDs` 全表（V/gamemodes/sh_gamemode_fd.nut:42-64）

| id | 枚举 | 服务端用的别名（`FD_GetAITypeID_ByString`，:406-484） | 按 NPC 标题对应（:96-116） | 剩余数变量（:153-184） | 教学卡（cl_gamemode_fd.nut:1035-1074） | 击杀计分事件（:131-151 + F/sh_consts.gnut:2078-2089） |
|---|---|---|---|---|---|---|
| 0 | TITAN | `titan`、`sniperTitan` | — | `FD_AICount_Titan` | 无 | FDTitanKilled = 5 |
| 1 | TITAN_NUKE | `nukeTitan`、`npc_titan_nuke` | `#NPC_TITAN_AUTO_NUKE` | `FD_AICount_Titan_Nuke` | 有 | 同上（按 npc_titan） |
| 2 | TITAN_ARC | `empTitan`、`npc_titan_arc` | `#NPC_TITAN_ARC` | `FD_AICount_Titan_Arc` | 有 | 同上 |
| 3 | TITAN_MORTAR | `mortarTitan`、`npc_titan_mortar` | `#NPC_TITAN_MORTAR` | `FD_AICount_Titan_Mortar` | 有 | 同上 |
| 4 | GRUNT | `grunt` | `#NPC_SOLDIER` | `FD_AICount_Grunt` | 有 | FDGruntKilled = 1 |
| 5 | SPECTRE | `spectre` | `#NPC_SPECTRE` | `FD_AICount_Spectre` | 有 | FDSpectreKilled = 1 |
| 6 | SPECTRE_MORTAR | `mortar_spectre` | `#NPC_SPECTRE_MORTAR` | `FD_AICount_Spectre_Mortar` | 有 | 同上（按 npc_spectre） |
| 7 | STALKER | `stalker` | `#NPC_STALKER` | `FD_AICount_Stalker` | 有 | FDStalkerKilled = 2 |
| 8 | REAPER | `reaper` | `#NPC_SUPER_SPECTRE` | `FD_AICount_Reaper` | 有 | FDSuperSpectreKilled = 3 |
| 9 | TICK | `tick` | `#NPC_SPECTRE_SUICIDE` | `FD_AICount_Ticks` | 有 | 无（`npc_frag_drone` 不在表里） |
| 10 | DRONE | `drone` | `#NPC_DRONE_PLASMA` | `FD_AICount_Drone` | 有 | FDAirDroneKilled = 1 |
| 11 | DRONE_CLOAK | `cloakedDrone` | `#NPC_DRONE_CLOAKED` | `FD_AICount_Drone_Cloak` | 有 | 同上 |
| 12 | RONIN | `npc_titan_stryder_leadwall(_boss_fd)` | `#NPC_TITAN_STRYDER_LEADWALL` | 无 | 无 | FDTitanKilled |
| 13 | NORTHSTAR | （别名改成返回 TITAN_SNIPER，原返回值被注释掉，:470-476） | `#NPC_TITAN_STRYDER_SNIPER` | 无 | 无 | 同上 |
| 14 | SCORCH | `npc_titan_ogre_meteor(_boss_fd)` | `#NPC_TITAN_OGRE_METEOR` | 无 | 无 | 同上 |
| 15 | LEGION | `npc_titan_ogre_minigun(_boss_fd)` | `#NPC_TITAN_OGRE_MINIGUN` | 无 | 无 | 同上 |
| 16 | TONE | `npc_titan_atlas_tracker(_boss_fd)` | `#NPC_TITAN_ATLAS_TRACKER` | 无 | 无 | 同上 |
| 17 | ION | `npc_titan_atlas_stickybomb(_boss_fd)` | `#NPC_TITAN_ATLAS_STICKYBOMB` | 无 | 无 | 同上 |
| 18 | MONARCH | `npc_titan_atlas_vanguard(_boss_fd)` | `#NPC_TITAN_ATLAS_VANGUARD` | 无 | 无 | 同上 |
| 19 | TITAN_SNIPER | `npc_titan_stryder_sniper(_boss_fd)`、`npc_titan_sniper`、`npc_titan_sniper_tone` | `#NPC_TITAN_SNIPER_FD`（"Sniper Titan"，L:11519） | 无 | 无 | 同上 |

- 计分事件的数值（1 / 2 / 3 / 5）是计分板分数还是钱，文件里没说。FD 的计分板三栏是"总分 / 战斗分 / 支援分"（F/gamemodes/sh_gamemodes.gnut:408-411）。
- 7 台英雄泰坦（12–18）和狙击泰坦（19）没有剩余数变量，只有图标（V/gamemodes/sh_gamemode_fd.nut:263-403）。狙击泰坦用 Northstar 的图标；提示说狙击泰坦有 Tone 和 Northstar 两种（L:11591）。
- 采集器伤害报告按"标题 → 类型"这张表（:96-116）找名字（cl_gamemode_fd.nut:1934-1936）。

### 3.2 客户端怎么计数和播报

| 机制 | 规则 | 出处 |
|---|---|---|
| 下波预告 | 服务端一次发最多 9 个类型 id；每行显示图标、类型名、`FD_AICount_<类型>` 的当前值 | V/gamemodes/cl_gamemode_fd.nut:907-947, 1164-1193 |
| 记分板 | 同一组类型，数字实时跟踪对应的剩余数变量；彩色图标 / 灰色图标两套 | :861-905 |
| 顶栏 | 本波剩余 / 总数（`FD_AICount_Current` / `Total`） | :514-515 |
| 首次遭遇 | 每类敌人第一次出现时弹一张教学卡（10 s），已看过的不再弹 | :950-964, 1269-1274 |
| 泰坦头顶图标 | IMC 泰坦按 targetname 取类型图标，隐身时隐藏；Insane 不加 | :644-650, 754-783 |
| 提示文字 | 每类敌人一到三条提示（失败画面随机给一条），如核弹泰坦靠近采集器自爆伤害巨大、电弧陷阱能拖住核弹泰坦、电弧泰坦能快速打掉采集器护盾且不受电弧陷阱影响、迫击炮泰坦要尽早处理、迫击炮幽灵在屋顶、扁虱会冲向采集器自爆、无人机能躲开大部分陷阱、隐身无人机本身不攻击但让下方的敌人隐身（意译） | L:11572-11615 |

### 3.3 FD 版 NPC 设置和基础版的差别

所有 FD 版文件与 Northstar 同名文件逐字相同（见 §0.1）。"—"表示基础文件没写这个键。

| FD 设置 | 继承自 | 改了什么（FD 值 / 基础值） | 出处 |
|---|---|---|---|
| `npc_drone_plasma_fd` | `npc_drone_plasma` → `npc_drone` | 最高飞行速度 400 / 600；非战斗 300 / 150；路点容差 400 / 16；随机悬停 1 / 3；停下用时 0.0 / 0.5；转向速度 75 / 35；移动转向 65 / 15；智能弹药锁定类型 small / any。血量不改（继承 100） | AS/npc_drone_plasma_fd.txt:1-20；AS/npc_drone.txt:6, 16, 56-57, 92-96 |
| ↳ 它的武器 | `mp_weapon_droneplasma` 的 `fd_damage` mod | 打泰坦护甲 150（近）/ 130（远）；近 / 远距离 1000 / 3000；打普通 20 / 15；爆炸伤害 0，打重甲 100。谁给它加这个 mod 在服务端（推断：FD 里的电浆无人机） | WT/mp_weapon_droneplasma.txt:182-192 |
| `npc_frag_drone_fd`（扁虱） | `npc_frag_drone` | 追击时长 10 s（多人；基础 —）；血 100 / 110；不跳向泰坦；速度倍率 2.0–2.5 / 0.8–1.5；自爆距离 200（相同）；爆炸改用 `damagedef_frag_drone_explode_FD` | AS/npc_frag_drone_fd.txt:4-22；AS/npc_frag_drone.txt:12-13, 28-29, 91 |
| ↳ 爆炸 | FD / 普通 | 伤害 130 / 60（多人），对重甲 600 / 300；内半径 200 / 200，外半径 350 / 300；`impulse_force` 2000（相同），FD 多人另有 `impulse_force_explosions` 50000（含义没查） | DD:145-172 |
| `npc_stalker_fd` | `npc_stalker` | 目标半径 16 / 1600；断腿后变成 `npc_stalker_crawling_fd` | AS/npc_stalker_fd.txt:1-6；AS/npc_stalker.txt:28, 37 |
| `npc_stalker_crawling_fd` | `npc_stalker_crawling` | 目标半径 16 | AS/npc_stalker_crawling_fd.txt:1-5 |
| `npc_super_spectre_fd`（死神） | `npc_super_spectre` | 不放扁虱 0（多人基础也是 0）；`assaultHarvester` 0；目标半径 64 / 256；强制走路距离 0 / 1500，对重甲 0 / 150；血 3500（相同）；目标信息框改成赏金死神样式 | AS/npc_super_spectre_fd.txt:1-17；AS/npc_super_spectre.txt:68, 159-160, 175, 202-203 |
| `npc_titan_stryder_sniper_fd`、`npc_titan_atlas_tracker_fd_sniper` | Northstar / Tone 的 NPC 设置 | 标题"Sniper Titan"；目标半径 100 / 256（`npc_titan`）；`assaultHarvester` 0 | AS/npc_titan_stryder_sniper_fd.txt:1-7；AS/npc_titan_atlas_tracker_fd_sniper.txt:1-7；AS/npc_titan.txt:127 |
| 7 个 `npc_titan_*_boss_fd` | 对应的英雄泰坦 NPC 设置 | **AI 数值完全相同**（逐行 diff 过），只多了涂装 / 贴花 / 皮肤编号三个外观键 | AS/npc_titan_*_boss_fd.txt；对比 AS/npc_titan_*.txt |
| `npc_turret_sentry_burn_card_ap_fd`（FD 哨戒炮） | `npc_turret_sentry` | 见 §4.5 | |
| `npc_turret_sentry_burn_card_at_fd`（FD 电浆炮塔） | `npc_turret_sentry` | 见 §4.5 | |
| `npc_turret_mega_frontierdefense` | `npc_turret_mega` | 血 10000（注释里原来是 15000）；预热 0；索敌 3000 / 0，对重甲 8000 / 5000；近 / 远视野分界 360 / 180、4028 / 1000；转向 70 / 25，瞄准 70 / 30；两轮射击间隔 3；开局即激活 1 / 0；回血速率 100；死亡爆炸 1；泰坦以外也能智能锁定。FD 里谁用它、站哪边，文件里没有（计分 `FD_SCORE_MEGATURRET = 0`，F/sh_consts.gnut:2080；V/gamemodes/sh_gamemode_fd.nut:214-215 有一段注释掉的图标） | AS/npc_turret_mega_frontierdefense.txt:1-42；AS/npc_turret_mega.txt:25-34, 51-52, 67-68 |

`assaultHarvester 0` 出现在：迫击炮幽灵、FD 死神、两种 FD 狙击泰坦、迫击炮泰坦（AS/npc_spectre_mortar.txt:7；AS/npc_super_spectre_fd.txt:5；AS/npc_titan_stryder_sniper_fd.txt:6；AS/npc_titan_atlas_tracker_fd_sniper.txt:6；AS/npc_titan_atlas_tracker_mortar.txt:8）。读这个键的代码不在本地；按名字推断是"不直接冲采集器"。

### 3.4 FD 里出现的特种泰坦（设置文件）

AI 泰坦的血量**不用** NPC 设置里的 8000，而是取它对应玩家 .set 文件的血量（有 `fd_health_upgrade` 时再 +2500），然后设成 NPC 的血（SV/ai/_ai_spawn_content.gnut:564-573）。`fd_titan_health_adjust` 在这之后怎么加减，代码没有（推断）。

| 类型 | NPC 设置（按标题对应，推断） | 玩家设置文件 | 多人血 / 护盾 | 出处 |
|---|---|---|---|---|
| 核弹泰坦 | `npc_titan_ogre_meteor_nuke`、`npc_titan_ogre_minigun_nuke`（标题 `#NPC_TITAN_AUTO_NUKE`，目标半径 32；后者换核弹专用行为树） | `titan_ogre_meteor_nuke` / `titan_ogre_minigun_nuke` | 15000 / 2500；12500 / 2500 | AS/npc_titan_ogre_meteor_nuke.txt:1-6；AS/npc_titan_ogre_minigun_nuke.txt:1-8；PS/titan_ogre_meteor_nuke.set:18-21；PS/titan_ogre_minigun_nuke.set:18-21 |
| 电弧泰坦 | `npc_titan_stryder_leadwall_arc`（标题 `#NPC_TITAN_ARC`）、`npc_titan_arc` | `titan_stryder_leadwall_arc` | 7500 / **0** | AS/npc_titan_stryder_leadwall_arc.txt:1-6；PS/titan_stryder_leadwall_arc.set:11-14 |
| 迫击炮泰坦 | `npc_titan_atlas_tracker_mortar`（标题 `#NPC_TITAN_MORTAR`，目标半径 32，`assaultHarvester` 0）、`npc_titan_mortar` | `titan_atlas_tracker_mortar` | 7500 / 2500 | AS/npc_titan_atlas_tracker_mortar.txt:1-8；PS/titan_atlas_tracker_mortar.set:13-17 |
| 英雄泰坦（boss） | `npc_titan_*_boss_fd` | 玩家同款 .set | Atlas 系 10000、Ogre 系 12500、Stryder 系 7500；护盾都是 2500 | PS/titan_atlas.set:48, 51；PS/titan_ogre.set:47, 50；PS/titan_stryder.set:55, 58 |

**核弹泰坦的行为（零售服务端，读得到）**：

- 只认 `npc_titan_ogre_meteor_nuke` 生成（注释说生成后再改设置会让它降落到地图外）（SV/ai/_ai_nuke_titans.gnut:18-28）。
- 降落完成后，等"到达采集器"或"寻路失败"信号，然后在采集器周围 400 范围内找导航点，以 100 的目标半径逼近，每 0.5 s 检查一次，进入 400 后自爆弹射（:31-72）。
- 一进入濒死状态就立刻核爆（受伤回调里判断），保证死前一定爆（:74-113）。
- 发现玩家的距离常量 500（:7）。

**电弧陷阱对特种泰坦**：电弧泰坦在能力开着时不吃电弧陷阱伤害；迫击炮泰坦被电弧陷阱打中会中断攻击；其他 NPC 泰坦被打中会跪地 2 s（V/weapons/mp_weapon_arc_trap.nut:366-428）。

**和采集器伤害有关的常量**（注释说"采集器伤害回调有时会调整 AI 武器的伤害"，回调本身不在本地）：核心伤害 ×0.25、迫击炮火箭 ×0.8（注释：每门迫击炮现在只打 7 发）（F/sh_consts.gnut:1717-1719）。

**迫击炮幽灵的武器**：火箭筒的 `fd_mortar_mode` mod——对人伤害 ×0、对泰坦护甲 ×0.15、爆炸半径 ×0、散布 0、两轮之间的休息 ×1.25–×2.0（WT/mp_weapon_rocket_launcher.txt:500-520）。谁加这个 mod 在服务端（推断：FD 的迫击炮幽灵）。

**多人模式里其他相关常量**（可能是 TF1 合作模式遗留，TF2 FD 服务端是否使用无法确认）：同时最多 8 台泰坦（注释写过 10）、最多 3 架隐身无人机、出生保护 3 s（F/sh_consts.gnut:1676-1679）；隐身无人机速度 1800、加速度 1.75、转向 150（:1744-1746）；电弧泰坦电场半径 330 / 内 150（:1736-1739）。

---

## 4. 经济和商店

### 4.1 钱的规则

| 规则 | 值 | 出处 |
|---|---|---|
| 每人上限 | 5000（存钱时夹在 0–5000） | F/burnmeter/sh_boost_store.gnut:44, 337-339 |
| 每波结束给 | `fd_money_per_round`（700 / 700 / 600 / 600 / 600），作为"本波完成"奖金 | V/gamemodes/sh_gamemode_fd.nut:118-120；PL（§1.1） |
| 每波另三项奖金 | "没死" 100、"本波 MVP" 100、"采集器没掉血（Flawless Defense）" 100 | F/sh_consts.gnut:2090（`FD_SCORE_MVP`）、:2093（`FD_SCORE_TEAM_FLAWLESS_WAVE`）、:2095（`FD_SCORE_DIDNT_DIE`）；事件和常量的对应见 DT/score_events.csv:205, 208, 212；模式说明说这三项给"奖励金"（L:12023） |
| 奖金展示 | 4 项按"本波完成 / 没死 / MVP / 采集器没掉血"排列，拿到的打勾并显示钱数 | V/gamemodes/cl_gamemode_fd.nut:1374-1399, 1423-1432 |
| 中途加入 | 服务端可累加一笔"中途加入奖金"，每个 UID 只给一次 | F/burnmeter/sh_boost_store.gnut:142-145, 162-171（每次累加多少由服务端调用，没有；推断是按已过的波数补钱） |
| 存入团队储备 | 一次 min(自己的钱, 100)；团队储备本身没有上限 | F/burnmeter/sh_boost_store.gnut:46, 288-306 |
| 从团队储备取出 | 一次 min(储备, 100)；自己已有 5000 时不能取 | :309-330 |
| 储备开关 | `boost_store_team_reserve` = 1 才能存取（五档都是 1）；第一次开商店时弹一次"团队储备"说明 | F/ui/menu_boost_store.nut:261-295, 315-366；PL:723 等 |
| 给队友钱 | 对着队友长按使用键："给 $N"，N = min(自己的钱, 100)；只在 Playing 状态、波次没在进行时可用 | V/gamemodes/cl_gamemode_fd.nut:707-727；L:11524-11525。服务端怎么转账没有 |
| 收到钱的提示 | 击杀信息栏"从某人那里得到 $N" | V/gamemodes/cl_gamemode_fd.nut:1631-1634 |
| 买东西的提示 | 全队击杀信息栏"某人买了某物" | :1625-1629；F/burnmeter/sh_boost_store.gnut:279 |

### 4.2 商店物品（FD 上架的 6 样）

商店只上 `modes` 列含 `fd` 的行，按价格从低到高排（F/burnmeter/sh_boost_store.gnut:174-206）。

| 物品 ref | 显示名 | 价格 | 买了立即生效？ | 限制 / 失败提示 | 解锁条件 | 效果 | 出处 |
|---|---|---|---|---|---|---|---|
| `burnmeter_amped_weapons_permanent` | Amped Weapons | 100 | 是 | 已经生效时不能买（"Already active"） | 无 | 主副武器增伤（意译 L:9364）。持续到什么时候文件里没有（名字是 permanent）。Northstar 的实现：给所有主武器加增幅 mod（NS/burnmeter/_burnmeter.gnut:587-609，Northstar） | DT/burn_meter_store.csv:21；DT/burn_meter_rewards.csv:21；F/burnmeter/sh_boost_store.gnut:119, 705-712；L:11910 |
| `burnmeter_instant_battery` | Amped Battery | 400 | 是（直接背上一块强化电池） | 身上已有电池不能买（"Limit 1 carried per player"） | 无 | 给泰坦插：血 + 分段血 × 2.0（普通电池 × 0.5）、护盾回满、核心 +0.2（所有电池都给），能把濒死泰坦拉回来（零售：SV/rodeo/_rodeo_titan.gnut:1347-1359, 1705-1778） | DT/burn_meter_store.csv:20；L:11906, 11915 |
| `burnmeter_rodeo_grenade` | Nuke Rodeo | 500 | 是（+1 次） | — | `fd_stats.rodeos` ≥ 3（F/_items.nut:3397） | 骑上敌方 NPC 泰坦时按使用键，让它核爆弹射；骑手被朝上方（俯仰 270° 再偏 5°）甩开，速度 1900–2100 × 重力倍率 × 0.95（SV/rodeo/_rodeo_titan.gnut:2355-2447；只在 FD 模式生效，:2357-2359） | DT/burn_meter_store.csv:19；L:11759-11763 |
| `burnmeter_arc_trap` | Arc Trap | 650 | 否（进背包，手动放） | — | 无 | 见 §4.5 | DT/burn_meter_store.csv:16 |
| `burnmeter_ap_turret_weapon_infinite` | Sentry Turret | 1200 | 否（进背包，手动放） | 同时最多 2 台（"Limit 2 active per player"）；检查的是 `burn_numTurrets < burn_turretLimit` | `fd_stats.arcMinesPlaced` ≥ 2（F/_items.nut:3396） | 见 §4.5 | DT/burn_meter_store.csv:18；F/burnmeter/sh_boost_store.gnut:113-116, 687-694；L:11742, 11913 |
| `burnmeter_harvester_shield` | Harvester Shield Boost | 1200 | 是（+1 次，按键使用） | — | `fd_stats.wavesComplete` ≥ 3（F/_items.nut:3398） | 采集器无敌 5 s（§5） | DT/burn_meter_store.csv:15；L:11739-11741 |

- 限 2 台的数字只在本地化里；网络变量 `burn_turretLimit` 默认 5（V/_remote_functions_mp.gnut:915），UI 默认也是 5（F/burnmeter/sh_boost_store.gnut:75）。FD 里服务端设成几没有文件。
- 被锁住的物品显示另一套"锁定"图标（DT/burn_meter_store.csv 的 `lockedStoreIcon` 列），服务端拒绝购买（F/burnmeter/sh_boost_store.gnut:258-259）。

### 4.3 购买规则（零售共享脚本的服务端分支）

F/burnmeter/sh_boost_store.gnut:235-286：

1. 相位中、死了、在泰坦里，都不能买。
2. "商店是否开着"的检查被注释掉了（:237-238），实际靠商店箱子只在开着时可用来限制。
3. 物品被锁 → 不能买。
4. 钱够，且通过额外检查（炮塔数量、没有电池、没有增幅）。
5. 扣钱 → 立即生效的直接执行效果；其他进背包。
6. 播购买音效，通知全队。

### 4.4 商店的位置和开关

| 事 | 规则 | 出处 |
|---|---|---|
| 商店是什么 | 地图上的箱子，开着时"友方铁驭"可用；长按使用键打开商店菜单 | F/burnmeter/sh_boost_store.gnut:352-414, 525-546；L:11522-11523 |
| 开 / 关 | `OpenBoostStores` / `CloseBoostStores` 切箱子状态和 `boostStoreOpen`；关着时小地图不显示 | :387-391, 465-477 |
| 泰坦靠近 | 半径 300、高 200 的触发区；泰坦进入时提示"下机才能用商店"，每 3.5 s 一次 | :45, 426-463, 550-608；L:11746 |
| 运输机里 | 重生运输机里按 A / 空格也能开商店 | :619-644；L:11521 |
| 收回已放的东西 | 放下的炮塔 / 陷阱可以由主人收回背包（"Hold to refund"），炮塔的击杀数保留 | :484-523 |
| 波间能做什么 | 换配装、买东西、放哨戒炮和电弧陷阱（意译） | L:11947-11948 |

### 4.5 FD 版炮塔和陷阱

**哨戒炮**：放下时用哪套 NPC 设置由服务端按玩家设（默认是普通 burn card 版），FD 用 `_fd` 版是按文件名推断的（V/weapons/mp_ability_turretweapon.nut:18-19, 217-222, 261-286）。

| 键 | FD 哨戒炮（`…_ap_fd`） | 普通 burn card 哨戒炮（`…_ap`） | `npc_turret_sentry` | 出处 |
|---|---|---|---|---|
| 血（多人） | 300 | 1250 | 1200 | AS/npc_turret_sentry_burn_card_ap_fd.txt:17；AS/npc_turret_sentry_burn_card_ap.txt:11；AS/npc_turret_sentry.txt:15 |
| 存在时长 | 0 = 不消失 | 60 s | — | AS/…_ap_fd.txt:19；AS/…_ap.txt:13 |
| 局间清理 | 0 = 重来一波也不清 | — | — | AS/…_ap_fd.txt:20 |
| 索敌距离 普通 / 重甲 | 2000 / 1200 | 2000 / 0（不打泰坦） | 2000 / 2000 | AS/…_ap_fd.txt:8-11；AS/…_ap.txt:8 |
| `maxEnemyDistForAttacker`（推断：对攻击自己的目标的索敌距离）普通 / 重甲 | 8000 / 2000 | 继承 8000 / 8000 | 8000 / 8000 | 同上 |
| 转向 / 瞄准速度 | 35 / 35 | 继承 45 / 45 | 45 / 45 | AS/…_ap_fd.txt:13-14 |
| 水平转角 | 360 | 继承 90 | 90 | AS/…_ap_fd.txt:22 |
| 武器 | `mp_weapon_yh803_bullet` | 同 | 同 | |
| 放下时精度倍率 | 2.0（所有可部署炮塔） | | | F/sh_consts.gnut:1703；V/weapons/mp_ability_turretweapon.nut:175 |
| 掉线 / 修理 | 血量 ≤ 1 时 HUD 显示"离线"（不是消失），有"某人修好了你的炮塔"的提示和语音，修炮塔计分 25，结算有"修炮塔最多"奖章 | | | V/gamemodes/cl_gamemode_fd.nut:325-331, 628-630, 1598-1623；F/sh_consts.gnut:2094；DT/fd_awards.csv:7。怎么修、修多少没有（推断：服务端让 FD 炮塔停在 1 血等人修） |

**电浆炮塔（FD 版设置存在，但商店不卖）**：`npc_turret_sentry_burn_card_at_fd` 血 400（普通 burn card 版 2500），不消失、不局间清理，索敌 2000（普通版 0），水平转角 360（AS/npc_turret_sentry_burn_card_at_fd.txt:8-16；AS/npc_turret_sentry_burn_card_at.txt:8-13）。

**电弧陷阱**（V/weapons/mp_weapon_arc_trap.nut）：

| 项 | 值 | 行 |
|---|---|---|
| 存在时长 | 不消失（局末清理那一行被注释掉）；本地化也写"永久陷阱" | :123；L:11753 |
| 触发区 | 圆柱，半径 250（= 电击半径 × 0.5），向上 100、向下 20；只被敌方触发 | :199-211, 257-265 |
| 电击半径 | 500 | :24, 355-356 |
| 一次电击 | 升起 0.5 s → 放电 0.6 s → 落下 0.5 s | :19-21, 329-363 |
| 冷却 | 12 s | :22, 293 |
| 伤害 | 电球伤害 10，对铁驭 1；附带 EMP 效果 | :357-358, 395 |
| 对泰坦 | 电弧泰坦能力开着时免疫；迫击炮泰坦被打断；其他 NPC 泰坦跪地 2 s | :366-428 |
| 收回 | 商店模式下，闲置时主人可以收回 | :191-192, 230-234 |
| 放置角度 | 贴地面，斜面法线和原朝向夹角的余弦 < 0.55 时不贴 | :13, 111-120 |

### 4.6 和 SCAN-1108 §2 不一样的地方

1. **电浆炮塔不在 FD 商店里**：`burnmeter_at_turret_weapon_infinite` 的 `modes` 是空的（DT/burn_meter_store.csv:17），只有 `burnmeter_ap_turret_weapon_infinite` 标了 `fd`（:18）；`fd` playlist 的价格覆盖列表也只有 6 项，不含电浆炮塔（PL:685-690）。它的 FD 版 NPC 设置和解锁条件（F/_items.nut:3395）都在，但按这张表不上架。
2. "每人 2 个"只来自本地化文字；网络变量默认 5。
3. 商店解锁条件（放过 2 次电弧陷阱、骑过 3 次泰坦、完成过 3 波）SCAN 没写。

### 4.7 文件里没有的

- **按击杀给钱**：没有。击杀有计分事件（1 / 1 / 1 / 2 / 3 / 5），但看不出是钱；客户端的钱只跟 `FD_money` 走（V/gamemodes/cl_gamemode_fd.nut:305-308）。模式说明只提到波末奖金（L:12022-12023）。
- 本波 MVP 怎么评。
- "没死""采集器没掉血"的判定细节。
- 给队友钱、存取储备之外，有没有别的进账。

---

## 5. 采集器

| 项 | 值 / 规则 | 出处 |
|---|---|---|
| 血量 | 25000 | PL:668 |
| 护盾 | 6000 / 6000 / 5000 / 4000 / 4000 | PL:732, 758, 784, 811, 840 |
| 回盾 | 受伤 10 s 后开始，10 s 从空回满（推断线性，即 600 / 500 / 400 每秒） | PL:670-671；F/sh_consts.gnut:1691-1692 |
| 护盾增强 | 商店 1200 买次数；按记分板聚焦键使用；采集器无敌 5 s；只能在波次进行中、且当前不在无敌期时用（否则提示"护盾已满"）；使用后全队横幅"某人用了护盾增强"；记 150 分 | DT/burn_meter_store.csv:15；V/gamemodes/cl_gamemode_fd.nut:155-156, 2378-2447, 1585-1596；F/burnmeter/sh_burnmeter.gnut:384-398；L:11740, 11781；F/sh_consts.gnut:2096 |
| 无敌剩余时间 | 全局 `FD_harvesterInvulTime`，顶栏显示 | V/_remote_functions_mp.gnut:406；cl_gamemode_fd.nut:516 |
| 修理 | 采集器旁的"修理口"（`harvesterBoostPort`），身上有电池才能用（"需要电池才能修理"），用后全队横幅"某人修好了采集器" | V/gamemodes/cl_gamemode_fd.nut:675-677, 729-740, 1573-1583；L:11528-11530, 11537 |
| 修多少 | **没有** | — |
| 谁会打它 | 服务端定。Northstar 生成时：AI 可攻击（优先级参数 30）、能被近战、能被智能弹药锁定（NS/_harvester.gnut:30-33，Northstar） | |
| 各敌人对它的威胁（提示） | 核弹泰坦自爆、电弧泰坦拆盾、Scorch 近身拆血、扁虱冲脸自爆、电浆无人机绕图射击、迫击炮单位远程打（意译） | L:11572-11615 |
| 失败 | 被毁 → 伤害报告（§2.5） | |
| 威胁警告常量 | 伤害连击超时 10 s；全局连击 10000 警告；泰坦 2500 距离内警告；迫击炮泰坦连击 4000、自爆幽灵连击 1500（注释：每次 150）才警告；步兵 1500 距离内 16 人警告 | F/sh_consts.gnut:1694-1701（可能是 TF1 遗留） |
| 其他状态文字 | "Harvester Health: Perfect / OK / Damaged / Heavy Damage" 等 | L:3865-3875, 3904-3906（可能是 TF1 遗留） |
| 结算图 | 采集器血量随时间的曲线，20 个点 | F/sh_consts.gnut:1732；L:3893 |

---

## 6. 泰坦 Aegis 升级

### 6.1 等级和经验

- 每台泰坦单独计 `fdTitanXP[泰坦]`（F/sh_titan_xp.gnut:328-335），只有一代（`FD_TITAN_MAX_GEN = 1`，:49）。
- 每级所需经验（DT/xp_per_fd_titan_level.csv:2-25，F/sh_titan_xp.gnut:98-116 读它）：

| 等级 | 这一级要的经验 | 到达这一级的累计经验 |
|---|---|---|
| 1 | 12 | 0 |
| 2 | 12 | 12 |
| 3 | 14 | 24 |
| 4 | 14 | 38 |
| 5 | 16 | 52 |
| 6 | 16 | 68 |
| 7 | 18 | 84 |
| 8 | 18 | 102 |
| 9 | 20 | 120 |
| 10–24 | 每级 20 | 10 级 140，之后每级 +20，24 级 420 |

满经验 440（= 24 级的 420 + 24 级自身的 20，F/sh_titan_xp.gnut:349-357）。难度门槛 5 / 11 / 14 级对应累计 52 / 160 / 220。

HUD：泰坦开机 2 s 后显示 Aegis 等级和已装升级（V/client/cl_titan_cockpit.nut:325-345）；等级写成"FR1.N"（L:11858）。

### 6.2 解锁表（以 `unlocks_fd_titan_level.csv` 为准）

**生效的是 `unlocks_fd_titan_level.csv`**：行号 = 等级，每格的 ref 按等级解锁（F/_items.nut:5435-5469）。`titan_fd_upgrades.csv` 也有一列 `unlockLevel`，但读它的那行被注释掉了（F/_items.nut:5430），而且数字和这张表对不上（例如 Ion 武器 1 级写 2、实际 11 级），**不要用**。

升级是被动的：解锁了就自动装上，没有"选"的环节（SV/_passives.gnut:59-122 把所有未锁的升级都加上；UI 每台固定 7 格，F/ui/menu_fd_titan_upgrade.nut:6, 95-110）。`cost`（1 / 2 / 3）和 `slot`（0–6，菜单里的格子位置）两列不影响解锁。

其余等级（3、4、6、7、9、10、12、13、15、16、18、19、21–23）写的是 `random`，即一份随机外观奖励（F/_random_unlocks.gnut:260-266, 284-319）；24 级给一个专属呼号牌（DT/unlocks_fd_titan_level.csv:26）。

| 等级 | Ion | Scorch | Northstar | Ronin | Tone | Legion | Monarch（vanguard） |
|---|---|---|---|---|---|---|---|
| 2 | Split Shot Power（武器 2） | Double Threat（武器 1） | Explosive Traps（功能 1） | Sword Mastery（武器 1） | 40mm: Splasher Rounds（武器 1） | Piercing Rounds（武器 1） | Energized Smoke（功能 1） |
| 5 | Chassis Upgrade（防御 1） | Chassis | Chassis | Chassis | Chassis | Chassis | Chassis |
| 8 | Energy Storage（功能 2） | Hot Streak（功能 1） | Plasma Railgun: Quick Charge（武器 1） | Ghost in the Machine（功能 1） | Sonar Weak Points（功能 2） | Executioner（功能 1） | XO-16: Sniper Configuration（武器 1） |
| 11 | Laser Shot Power（武器 1） | Roaring Flames（功能 2） | Trap Mastery（功能 2） | Kinetic Transfer（武器 2） | 40mm: Extended Ammo（武器 2） | Redirect（武器 2） | Energized Smoke Lvl 2（功能 2） |
| 14 | Shield Upgrade（防御 2） | Shield | Shield | Shield | Shield | Shield | Shield |
| 17 | Energy Regen（功能 1） | Triple Threat（武器 2） | Plasma Railgun: Critical Hit（武器 2） | Wraith（功能 2） | Signal Strength（功能 1） | Drill Shot（功能 2） | XO-16: Critical Hit（武器 2） |
| 20 | Reflex Cannon（终极） | Explosive Barrels（终极） | Twin Cluster（终极） | Blademaster（终极） | Salvo Core Barrage（终极） | Dreadnought（终极） | Apex Titan（终极） |

出处：等级 DT/unlocks_fd_titan_level.csv:4-22；名字 L:11619-11729；ref 和类别 DT/titan_fd_upgrades.csv:2-50。

### 6.3 每个升级的数值

两条通用的：

| 升级 | 做法 | 数值 | 出处 |
|---|---|---|---|
| Chassis Upgrade（5 级） | 设置文件 mod `fd_health_upgrade` | 血 +2500：Ion / Tone / Monarch 10000 → 12500，Scorch / Legion 12500 → 15000，Ronin / Northstar 7500 → 10000 | SV/_passives.gnut:124-135 等各 `ApplyDerived…`；PS/titan_atlas_stickybomb.set:60-63、titan_atlas_tracker.set:46-49、titan_atlas_vanguard.set:53-56、titan_ogre_meteor.set:43-46、titan_ogre_minigun.set:43-46、titan_stryder_leadwall.set:43-46、titan_stryder_sniper.set:45-48；底盘血 PS/titan_atlas.set:48、titan_ogre.set:47、titan_stryder.set:55。NPC 泰坦同样 +2500（SV/ai/_ai_spawn_content.gnut:564-566），脱离濒死时最大血也加一段（SV/titan/_titan_health.gnut:81-82） |
| Shield Upgrade（14 级） | 护盾上限 × 1.5 | 2500 → 3750 | SV/_passives.gnut:159-161（Ronin）、220-222、291-293、441-443、503-505、565-567、632-634；底盘护盾 PS/titan_atlas.set:51 等 |

**Ion**（SV/_passives.gnut:392-466）

| 等级 | 升级 | 效果（意译） | 数值（FD / 原版） | 出处 |
|---|---|---|---|---|
| 2 | Split Shot Power | 分裂射击更省能、伤害更高 | 每发能量 20 / 30；开镜分裂射击的伤害倍率 ×1.0 / ×0.7（带 Ion 开镜被动时 ×0.7 / ×0.55） | WT/mp_titanweapon_particle_accelerator.txt:41, 61, 462-487, 489-514, 530-576；V/weapons/mp_titanweapon_particle_accelerator.nut:57-75 |
| 8 | Energy Storage | 能量上限提高 | 1250 / 1000 | PS/titan_atlas_stickybomb.set:37, 68-71 |
| 11 | Laser Shot Power | 激光对弱点伤害更高 | 暴击倍率 2.0 / 1.5 | WT/mp_titanweapon_laser_lite.txt:71, 104, 347-350 |
| 17 | Energy Regen | 能量回复快 25 % | 每秒 100 / 80（多人） | PS/titan_atlas_stickybomb.set:40, 64-67 |
| 20 | Reflex Cannon | 激光核心期间击杀延长核心 | 杀泰坦 +2.5 s、杀死神 +1.5 s、杀其他 +0.5 s；核心时长基准 3.0 s（带核心被动 5.0 s），总长不超过基准 | V/weapons/mp_titancore_lasercannon.nut:56-75 |

**Tone**（SV/_passives.gnut:468-528）

| 等级 | 升级 | 效果 | 数值 | 出处 |
|---|---|---|---|---|
| 2 | Splasher Rounds | 40mm 爆炸范围变大 | 内 / 外半径 100 / 225（多人原版 17 / 150） | WT/mp_titanweapon_sticky_40mm.txt:50-51, 535-540 |
| 8 | Sonar Weak Points | 被声呐标出的敌人受伤 +25 % | 状态效果"受伤倍率" +0.25，声呐结束时去掉 | V/weapons/mp_titanability_sonar_pulse.nut:66-69, 110-133 |
| 11 | Extended Ammo | 弹匣翻倍 | 24 / 12，装上时补满弹匣 | WT/mp_titanweapon_sticky_40mm.txt:140, 541-544；SV/_passives.gnut:513-519 |
| 17 | Signal Strength | 声呐时长翻倍 | 10 s / 5 s（声呐半径 1250 不变） | V/weapons/mp_titanability_sonar_pulse.nut:11-13, 136-142 |
| 20 | Salvo Core Barrage | 齐射核心导弹更多 | 30 / 20 发 | WT/mp_titancore_salvo_core.txt:191, 369-372 |

**Northstar**（SV/_passives.gnut:185-244）

| 等级 | 升级 | 效果 | 数值 | 出处 |
|---|---|---|---|---|
| 2 | Explosive Traps | 系留陷阱断开时爆炸 | 伤害 1000，对重甲 1000，半径 350 | DD:282-294；SV/mp/_titan_tether.gnut:93-97；V/weapons/mp_weapon_tether.nut:121-124 |
| 8 | Quick Charge | 狙击炮蓄力快 | 蓄力时间 ×0.6（2.25 → 1.35 s） | WT/mp_titanweapon_sniper.txt:176, 501-505 |
| 11 | Trap Mastery | 系留陷阱两次 | 每次消耗 100 / 200，回复 5 / 10 每秒（每次 20 s，两次 40 s） | WT/mp_titanability_tether_trap.txt:52-61, 141-148 |
| 17 | Critical Hit | 狙击炮暴击更高 | 暴击时额外伤害 ×2.0 / ×1.5 | V/weapons/mp_titanweapon_sniper.nut:63-70；WT/mp_titanweapon_sniper.txt:64, 506-509 |
| 20 | Twin Cluster | 集束导弹一次两发 | 每轮 2 发；每发的子爆炸次数 ×0.7（20 → 14）、持续 ×0.7（5.0 → 3.5 s）；两发左右各偏 0.25–0.35 × 0.1 | WT/mp_titanweapon_dumbfire_rockets.txt:198, 247-263；V/weapons/_weapon_utility.nut:1576-1580；F/sh_consts.gnut:478, 486；V/weapons/mp_titanweapon_dumbfire_rockets.nut:47-65 |

**Ronin**（SV/_passives.gnut:124-183）

| 等级 | 升级 | 效果 | 数值 | 出处 |
|---|---|---|---|---|
| 2 | Sword Mastery | 近战伤害提高 | ×1.25（625 → 781） | WT/melee_titan_sword.txt:31-32, 177-181 |
| 8 | Ghost in the Machine | 相位冲刺两次 | 每次消耗 100 / 200，回复 ×0.6（16 → 9.6 每秒；每次约 10.4 s，原版一次 12.5 s） | WT/mp_titanability_phase_dash.txt:45-54, 193-201 |
| 11 | Kinetic Transfer | 格挡挡下的伤害充核心 | 核心 += 原伤害 ×（1 − 格挡倍率）× `CORE_BUILD_PERCENT_FROM_TITAN_DAMAGE_INFLICTED` × 0.015 × `earn_meter_titan_multiplier`；该常量 0.0100 或 0.0070（两个编译分支） | V/weapons/mp_titanability_basic_block.nut:311-316；F/_settings.nut:764, 766 |
| 17 | Wraith | 相位冲刺更远 | 冲刺速度 ×1.5（1000 → 1500，竖直 200 不变） | V/weapons/mp_titanability_phase_dash.nut:8, 57-66 |
| 20 | Blademaster | 剑核心时长翻倍，剑核心命中回护盾 | 核心 24 s / 12 s；核心期间剑命中重甲 +500、其他 +250 护盾 | WT/mp_titancore_shift_core.txt:32-37, 68-72；V/weapons/mp_titanweapon_sword.nut:20, 56-68 |

**Scorch**（SV/_passives.gnut:530-595）

| 等级 | 升级 | 效果 | 数值 | 出处 |
|---|---|---|---|---|
| 2 | Double Threat | 铝热发射器两发再换弹 | 弹匣 2 / 1；射速 1.2 / 1.7；分段换弹 1.6 s（循环 1.2、收尾 0.8）/ 原版 2.4 s；备弹 40 | WT/mp_titanweapon_meteor.txt:149-157, 407-428 |
| 8 | Hot Streak | 铝热伤害攒核心倍率 | 每次铝热伤害：计数 += 伤害 / 10000 × 0.5；≥ 0.5 时直接记满 1.0，然后 30 s 线性降到 0；计数 ≥ 0.5 时泰坦核心获取 ×1.5 | SV/_passives.gnut:31-32, 1644-1657；SV/titan/_titan_health.gnut:991-997；F/sh_consts.gnut:1757 |
| 11 | Roaring Flames | 火焰伤害提高 | ×1.2（铝热发射器、火墙、火焰核心、燃烧陷阱都乘） | F/sh_consts.gnut:1756；V/weapons/mp_titanweapon_meteor.nut:114-117、mp_titanweapon_flame_wall.nut:231-234、mp_titancore_flame_wave.nut:258-261、mp_titanability_slow_trap.nut:567-574 |
| 17 | Triple Threat | 三发再换弹 | 弹匣 3（其余同 Double Threat，替换掉它） | WT/mp_titanweapon_meteor.txt:429-450；SV/_passives.gnut:569-586 |
| 20 | Explosive Barrels | 燃烧陷阱点燃时先爆一下 | 伤害 100，对重甲 500，半径 350 | DD:269-280；V/weapons/mp_titanability_slow_trap.nut:85-88, 224 |

**Legion**（SV/_passives.gnut:597-683）

| 等级 | 升级 | 效果 | 数值 | 出处 |
|---|---|---|---|---|
| 2 | Piercing Rounds | 转管炮子弹穿透 | 穿透深度 +500（原版 0） | WT/mp_titanweapon_predator_cannon.txt:448, 675-678 |
| 8 | Executioner | 近距强力射击无视濒死 | 打中濒死的泰坦时伤害设为它的剩余血 +1（直接打死） | V/weapons/mp_titanability_power_shot.nut:61-70；V/weapons/mp_titanweapon_predator_cannon.nut:26-27, 160-164, 297-310 |
| 11 | Redirect | 枪盾吸收的伤害回到泰坦护盾 | 1:1（注释"可能要调"），不超过上限 | V/weapons/_vortex.nut:1551-1564；mod 加在主武器上（SV/_passives.gnut:642-646） |
| 17 | Drill Shot | 远距强力射击每穿一个敌人伤害更高 | 穿透后保留伤害倍率 1.5 | WT/mp_titanweapon_predator_cannon.txt:658-661；V/weapons/mp_titanability_power_shot.nut:50-59 |
| 20 | Dreadnought | 全部套件 | 加上 Legion 的武器、转速、智能核心、强力射击四个被动 mod，再加 `fd_gun_shield`：枪盾血 5000 / 2500 | SV/_passives.gnut:648-680；V/weapons/mp_titanability_gun_shield.nut:14-15, 231-239 |

**Monarch**（SV/_passives.gnut:246-390）

| 等级 | 升级 | 效果 | 数值 | 出处 |
|---|---|---|---|---|
| 2 | Energized Smoke | 电烟给自己回护盾 | 每次电烟伤害判定 +35 护盾（不超过上限） | V/weapons/mp_titanability_smoke.nut:142-155 |
| 8 | XO-16: Sniper Configuration | 收紧散布、可切换放大 | 放大视野 25，切换 0.2 s；所有散布 ×0.5 | WT/mp_titanweapon_xo16_vanguard.txt:551-564 |
| 11 | Energized Smoke Lvl 2 | 电烟也给友方泰坦回护盾 | 同上 +35 | V/weapons/mp_titanability_smoke.nut:144 |
| 17 | XO-16: Critical Hit | 弱点伤害更高 | 暴击倍率 2.0 / 1.5；开镜时加"威胁瞄准镜"高亮 | WT/mp_titanweapon_xo16_vanguard.txt:120, 565-568；V/weapons/mp_titanweapon_xo16.nut:169-193 |
| 20 | Apex Titan | 开局多一个随机一级核心升级 | 在 Arc Rounds / Missile Racks / Energy Transfer 三个一级升级里，已选的之外两个各 50 % | SV/_passives.gnut:307-387 |

### 6.4 FD 里一直生效的平衡 mod（`fd_balance`，不靠升级）

开了 `aegis_upgrades` 就给 Ion 和 Monarch 加上（SV/_passives.gnut:265-273, 417-435）：

| 泰坦 | 武器 | 改动 | 出处 |
|---|---|---|---|
| Ion | 分裂枪（particle accelerator） | 全部伤害 ×1.1 | WT/mp_titanweapon_particle_accelerator.txt:577-583 |
| Ion | 激光（laser shot） | 对泰坦护甲 ×1.25 | WT/mp_titanweapon_laser_lite.txt:341-346 |
| Ion | 激光核心 | 全部伤害 ×1.45 | WT/mp_titancore_laser_cannon.txt:316-324 |
| Monarch | XO-16 | 对泰坦护甲 ×0.8 | WT/mp_titanweapon_xo16_vanguard.txt:569-573 |
| Monarch | 火箭齐射 | 全部伤害 ×0.8 | WT/mp_titanweapon_salvo_rockets.txt:285-291 |
| Monarch | 升级核心换上的多目标导弹 | 全部伤害 ×0.8（升级时把这个 mod 带过去） | WT/mp_titanweapon_shoulder_rockets.txt:368-376；V/weapons/mp_titancore_upgrade.nut:183-197 |

### 6.5 其他

- Aegis 升级不只用在 FD：`aegis_upgrades 1` 还出现在 Aegis LTS、Aegis Titan Brawl 两个 playlist（PL:1110-1123, 1335-1341；说明 PL:4250-4267）。
- 每台泰坦的 FD 定位：Ion 进攻 / 游走，Tone 进攻 / 支援，Monarch 支援，Northstar 进攻，Ronin 游走，Legion 坦克，Scorch 坦克（L:11798-11805；选泰坦菜单读 `fdRole` 列，F/ui/menu_team_titan_select.nut:451-458）。
- Northstar 写了一个 `AddFDTitanXP` 帮手函数（NS/titan_xp.gnut:33-45，Northstar），但没有任何地方调用。

---

## 7. 玩家侧规则

### 7.1 重生

| 规则 | 值 | 出处 |
|---|---|---|
| 重生方式 | 运输机成批重生（`eWaveSpawnType.DROPSHIP`） | PL:654；F/sh_consts.gnut:1326-1333 |
| 重生间隔 | 25 s（推断是成批的间隔） | PL:655；F/_settings.nut:927 |
| 死亡延迟 | 4 s（推断） | PL:650 |
| 运输机里 | 有指挥官对白动画；能开商店 | V/gamemodes/cl_gamemode_fd.nut:1773-1849；F/burnmeter/sh_boost_store.gnut:619-630 |
| 倒地 / 队友救援 | 本地没有 FD 专用的规则 | — |

### 7.2 泰坦

| 规则 | 值 | 出处 |
|---|---|---|
| 首次 / 再次建造 | 240 / 240 s（推断） | PL:647-648 |
| 自己攒的进度分给队友 | 只分"已拥有"部分，× 0.25 | PL:680-681；SV/earn_meter/sv_earn_meter.gnut:153-175 |
| 选泰坦 | 第 1 波后锁定（模式说明）；同一台已被队友选用时不能选（锁定状态 INUSE） | L:12024；F/ui/menu_team_titan_select.nut:534-535；L:11500 |
| 全员不同泰坦 | 结算有"阵容"经验奖励（"All Unique Titans"） | F/sh_xp.gnut:56；F/ui/panel_pve.nut:432-435；L:11885-11886 |
| 记分板状态栏 | FD 显示 4 个友方、0 个敌方 | V/client/cl_gamestate.gnut:594-600 |

### 7.3 每波奖励（计分事件）

DT/score_events.csv:198-221 的 `pointValue` 列引用 F/sh_consts.gnut:2078-2104 的常量：

| 事件 | 值 | 备注 |
|---|---|---|
| FDTeamWave（本波完成） | 被改成 `fd_money_per_round` | V/gamemodes/sh_gamemode_fd.nut:118-120 |
| FDWaveMVP | 100 | 显示"Wave MVP - 名字" |
| FDDidntDie | 100 | |
| FDTeamFlawlessWave（采集器没掉血） | 100 | |
| FDShieldHarvester（用护盾增强） | 150 | |
| FDRepairTurret | 25 | |
| FDTeamFinalWave、FDEnemiesKilled、FDSonarPulse、FDArcTrapTriggered、FDTetherTriggered、FDArcWave、FDTeamHeal、FDDamageBonus、FDHealingBonus、FDSupportBonus | 0 | 只做提示 / 计数 |
| 各类击杀 | 见 §3.1 | |

只有前四项在"波次奖金"列表里展示（V/gamemodes/cl_gamemode_fd.nut:1374-1379）。

### 7.4 Aegis 经验结算

经验分 11 类（F/sh_xp.gnut:44-60），结算界面逐类列出（F/ui/panel_pve.nut:376-437）：

| 类 | 结算显示 | 说明 |
|---|---|---|
| EASY / NORMAL / HARD / MASTER / INSANE_VICTORY | "X Difficulty — Victory" | 按难度的胜利奖励 |
| WAVES_COMPLETED | "Waves Complete N / M" | |
| WAVES_ATTEMPTED | "Wave Milestones N / M"，副标"消灭本波 50 % 的敌人"（意译） | L:11891-11892 |
| DIFFICULTY_BONUS | 难度加成，副标"Hard ×2 / Master ×3 / Insane ×4" | L:11879-11883 |
| RETRIES_REMAINING | "Retries Remaining N / M" | L:11888 |
| PERFECT_COMPOSITION | 全员不同泰坦 | |
| WARPAINT_BONUS | Frontier 涂装：给自己和队友每人 +1，最多叠 4 次（意译） | L:12042 |

常量（F/sh_consts.gnut:2703-2731；客户端没有用到，服务端怎么组合没有）：

| 常量 | Easy | Normal | Hard | Master | Insane |
|---|---|---|---|---|---|
| `FD_XP_*_BONUS_SCALE` | 1 | 1 | 2 | 3 | 4 |
| `FD_XP_*_WIN` | 1 | 1 | 2 | 3 | 4 |
| `FD_XP_VICTORY` + `FD_XP_VICTORY_*_BONUS` | 1 | 1 | 1+1 | 1+2 | 1+3 |
| `FD_XP_WAVE` + `FD_XP_*_WAVE_BONUS` | 1+0 | 1+0 | 1+1 | 1+2 | 1+3 |
| `FD_XP_*_MILESTONE` | 0 | 1 | 1 | 1 | 1 |

### 7.5 结算奖章（DT/fd_awards.csv:2-15；F/gamemodes/sh_all_gamemode_fd.nut:37-73 读它，按 priority 从高到低排）

每人一张（`ServerCallback_UpdateGameStats` 每人一条，V/gamemodes/cl_gamemode_fd.nut:2241-2251）。门槛列是 `validityCheck = greater_than` 的值，比较方式都是"最高者"。

| ref | 名字（L:11807-11836） | 统计什么 | 门槛（大于） | 必须是最高 | priority |
|---|---|---|---|---|---|
| mvp | Most Valuable Player | 本局当 MVP 的波数 | 2 | 是 | 13 |
| titanKills | Titan Hunter | 杀泰坦数 | 30 | 是 | 12 |
| heals | Titan Support | 给队友回复量 | 5000 | 是 | 11 |
| turretKills | Turret Strategist | 炮塔击杀 | 10 | 是 | 10 |
| longestTitanLife | Titan Efficiency | 泰坦最长存活 s | 100 | 是 | 9 |
| coresUsed | Extreme Measures | 用核心次数 | 1 | 是 | 8 |
| turretsRepaired | Repairman | 修炮塔次数 | 5 | 是 | 7 |
| moneyShared | Make it Rain | 给出去的钱 | 100 | 是 | 6 |
| harvesterHeals | Harvester Support | 给采集器加盾次数 | 1 | 是 | 5 |
| moneySpent | Big Spender | 花的钱 | 2000 | 是 | 4 |
| mortarUnitsKilled | Mortar Hunter | 杀迫击炮单位数 | 1 | 是 | 3 |
| timeNearHarvester | Homeland Security | 在采集器附近的时间 s | 200 | 是 | 2 |
| damageDealt | Power Play | 伤害 | −1 | 否 | 1 |
| longestLife | Defensive Player | 最长存活 s | 200 | 是 | 0 |

谁拿哪张（同一人满足多张时怎么选）由服务端定。

### 7.6 弹药箱（零售服务端）

SV/mp/_loadout_crate.nut：长按使用键打开配装菜单（:106-118, 162-170）；站在 96 范围内、视线通，每 10 s 补一次弹药（不在泰坦里），离开 384 后重置（:121-160）；同一张图最多 10 个（F/sh_consts.gnut:1713；:22）。客户端有"Ammo Refilled"提示（V/gamemodes/cl_gamemode_fd.nut:1493-1499）。

### 7.7 解锁和统计

`fd_stats` 记：放电弧陷阱数、放炮塔数、骑泰坦数、核弹骑乘数、电弧陷阱电到数、炮塔击杀、护盾增强次数、完成波数、各难度胜场、最高 Aegis 等级（F/sh_stats.gnut:343-358）。用途：难度解锁（§1.3）、商店物品解锁（§4.2）、各难度胜 10 场给头像图标（F/_items.nut:1766-1769）、FD 胜 10 场解锁经典音乐（F/_items.nut:3393）。

### 7.8 其他

- 标记（ping）敌人时，FD 里会高亮被标的敌人（NS/_ping.gnut:98-99，Northstar 文件，来源是否原版不清楚）。

---

## 8. 哪些已经能脱离 TF2 照做 / 还缺什么

### 8.1 能照做（数据齐）

| 部分 | 依据 |
|---|---|
| 五档难度的全部 playlist 数值、解锁门槛、Insane 的三条额外规则 | §1 |
| 波次状态常量、客户端事件顺序、所有计时（12 s 开场横幅、20 s 奖金、60 s 购物、4 s 关店倒数、3.5 s 重来横幅、6 s 失败等待…） | §2.3, §2.5 |
| HUD 每块显示什么 | §2.4 |
| 每张图 5 个波次名、地图池 8 张 | §2.7-2.8 |
| 20 类敌人的编号、计数、播报、教学卡；FD 版敌人设置和基础版的差别 | §3 |
| 核弹泰坦冲采集器自爆的完整行为 | §3.4 |
| 钱的上限、存取、给队友、每波奖金；6 样商品的价格、限制、解锁、效果 | §4 |
| FD 版哨戒炮、电弧陷阱的全部数值 | §4.5 |
| 采集器血、盾、回盾、护盾增强 | §5 |
| Aegis：等级经验表、7 台泰坦 × 7 个升级的解锁等级和**全部数值**，以及常驻平衡改动 | §6 |
| 结算奖章、重生方式、弹药箱 | §7 |

### 8.2 还缺（本地没有任何文件）

| 缺什么 | 为什么缺 | 现在只知道 |
|---|---|---|
| **每张图每波刷什么敌人、多少、什么时候、从哪里出** | FD 服务端和地图脚本是空壳 | 敌人种类全集（§3.1）、每波最多同时预告 9 类（§3.2） |
| 波次推进的服务端逻辑（什么时候算一波结束、`FD_waveState` 怎么切） | 同上 | 客户端事件顺序（§2.3，部分推断） |
| 难度变量的具体用法（泰坦 / 死神血量怎么加减、反泰坦步兵、盾兵队长、`fd_pro_titan_shields`、`fd_at_unlimited_ammo` 的对象） | 服务端代码没有 | 变量值（§1.1），含义靠名字推断 |
| 重试次数的确切值 | 服务端 `FD_SetNumAllowedRestarts` 的调用不在本地 | 推断 2 / 0（由 `roundscorelimit` 3 / 1） |
| 按击杀给钱（如果有） | 服务端 | 击杀计分 1–5，不能确认是钱 |
| 本波 MVP、"没死"、"采集器没掉血"的判定 | 服务端 | 奖金各 100 |
| 中途加入补多少钱 | 服务端调用 `SetJoinInProgressBonus` 的地方不在本地 | 机制存在 |
| 采集器修理量、修理口位置 | 服务端 / 地图 | 需要电池 |
| 采集器伤害回调（对各类 AI 伤害的调整） | 服务端 | 两个倍率常量 0.25 / 0.8（§3.4） |
| 哨戒炮 FD 上限的实际值、炮塔离线和修理 | 服务端 | 本地化写 2；离线 = 血 ≤ 1 |
| 英雄 / 特种泰坦（除核弹泰坦）在 FD 里的专用行为 | 服务端 | 设置文件和行为树名（§3.3-3.4） |
| `assaultHarvester` 的作用 | 读它的代码不在本地 | 哪些敌人设成 0 |
| Aegis 经验的实际发放公式 | 服务端 | 常量和 11 类条目（§7.4） |
| 增幅武器"permanent"持续多久 | 零售服务端没有，只有 Northstar 写的版本 | — |
| 数据表与零售 rpak 是否逐字相同 | 零售 rpak 没解包 | 用的是 Northstar 随包的 CSV |
| 采集器位置、商店箱子位置、修理口、迫击炮点位、敌人出生点 | 地图 / 服务端 | 客户端认识这些物件的名字（§2.4） |
