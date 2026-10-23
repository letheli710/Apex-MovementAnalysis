# R5Flowstate 移动相关精确数值（静态来源汇总）

整理日期 2026-10-23。只读整理：没有启动游戏，没有改任何游戏、Unity 或 runner 文件。

**路径前缀**

| 前缀 | 含义 |
|---|---|
| `<game root>` | 已安装的 R5Flowstate 目录（build R5pc_r5-211_J12_CL6933961_2026-09-27） |
| `PS:` | `<game root>/platform/scripts/`（游戏实际加载的脚本和武器文件） |
| `SDK:` | `research-src/s21-r5sdk/src/`（R5Flowstate SDK 源码，社区代码，不是 Respawn 代码） |
| `data/<session>/` | 本目录 `phase2-local/data/` 下的本地会话（原始日志不进公开仓库） |

**来源标签**

| 标签 | 含义 |
|---|---|
| [setfile] | 玩家设置文件（setfile）里的值。setfile 是编译后的 rpak 资产，本地没有明文，这里的数是运行时读出来的（E0 census，见下文）。 |
| [script] | `PS:` 下的 `.nut` / `.gnut` 常量，或武器 `.txt` 键值。 |
| [sdk-cvar] | SDK 源码里注册的 ConVar 默认值。只对 SDK 自己加的机制有效（mantle boost、lurch 截断、ziprail 调参等）。 |
| [native-cvar] | 引擎原生 ConVar。默认值写在 exe 的代码里，静态方式**定不下来**（见 §5）。 |

> **关于 setfile 数值的出处。** Phase 1 已确认 setfile 不以文本形式存在（`../../phase1/Movement-Analysis.md` §0）。所以这份表里的 setfile 数值都来自 E0 census：每个会话开始时，用客户端命令 `bridge_classvar_get <key>`（`SDK:game/client/classvar_natives.cpp`）逐个读取当前传奇的 class var，结果写进 `data/<session>/report/census.csv`。读出来的就是 setfile 本身的值，没有拟合。M2 的实测和这些值的误差在 0.1 % 以内（`../m2/PARAMETER-TABLE.md`）。
>
> 完整的按传奇对照表在 [classvar-census-by-legend.csv](classvar-census-by-legend.csv)，共 158 个键、12 个传奇、28 个固定传奇的会话。未固定传奇的会话（M2 和最早的冒烟测试）没有计入。

---

## 1. 地面移动 [setfile]

所有传奇的值都一样，除非另有注明。

| 键 | 值 | 单位 | 备注 |
|---|---|---|---|
| `speed` | 173.5 | u/s | 走路上限 = speed × msc。空手时 msc = 1.15，即 199.525 |
| `sprintspeed` | 260 | u/s | 冲刺上限 299.0（空手） |
| `acceleration` | 450 | u/s² | 速度高于 lowSpeed 时使用 |
| `lowSpeed` | 120 | u/s | 低速段分界 |
| `lowAcceleration` | 2500 | u/s² | 低速段加速度 |
| `deceleration` | 1250 | u/s² | 无输入时减速（不乘 msc，M2 实测） |
| `sprintAcceleration` | 100；Wraith 102 | u/s² | 唯一在基础地面键上因传奇而异的值 |
| `sprintDeceleration` | 1250 | u/s² | |
| `speedScaleSide` / `speedScaleBack` | 1 / 1 | – | 侧移和后退不降速 |
| `stepHeight` | 22 | u | |
| `sprintStartDelay` | 0.2 | s | M2 没测到这几个 sprint 键有影响 |
| `sprintStartDuration` | 0.8 | s | |
| `sprintStartFastDuration` | 0.2 | s | |
| `sprintEndDuration` | 0.15 | s | |
| `landSlowdownDuration` | 1；Horizon 0 | s | 硬着陆减速时长 |

census 里没有蹲走速度这个键。M2 拟合出 80 u/s，减速 1500 u/s²（`../m2/PARAMETER-TABLE.md`）。

**移动倍率（msc）的来源 [script]：** 空手和近战武器的 `move_speed_modifier` 是 **1.15**，比如 `PS:weapons/mp_weapon_melee_survival.txt:27`，所有传奇的近战/传家宝武器都一样。枪械在 WeaponData 顶层没写这个键，引擎按 1.0 处理。所以拿枪时地面上限会回到 speed × 1.0。完整列表见 §4。

## 2. 跳跃、空中 [setfile]

| 键 | 值 | 单位 | 备注 |
|---|---|---|---|
| `gravityScale` | 1 | – | 有效重力 = sv_gravity × gravityScale |
| `jumpHeight` | 56 | u | V = √(2·750·56) = 289.82 u/s（M2 实测 289.823） |
| `airSpeed` | 60；Horizon 80 | u/s | 空中期望速度上限（再乘 msc） |
| `airAcceleration` | 500；Horizon 800 | u/s² | accelspeed = airAcceleration·dt（M2 已证实不乘 wishspeed） |
| `airFriction` / `airDrag` | 0 / 0 | – | |
| `antiMultiJumpHeightFrac` | 0.3 | – | 落地后立刻再跳，高度乘这个系数 |
| `doubleJump` | false；Sparrow true | – | |
| `superjumpMinHeight` | 112；Alter 56；Sparrow 150 | u | 二段跳参数 |
| `superjumpMaxHeight` | 200；Alter 56；Sparrow 150 | u | |
| `superjumpHorzSpeed` | 240；Alter 90；Sparrow 250 | u/s | |
| `superjumpLimit` | 1 | 次 | |
| `dodgeSpeed` | 750；Ash 600；Wraith 600；Sparrow 550 | u/s | |
| `dodgeDuration` | 0；Wraith 0.1 | s | |

## 3. 滑铲、攀爬、蹬墙、滑索 [setfile]

### 3.1 滑铲

| 键 | 值 | 单位 |
|---|---|---|
| `slideRequiredStartSpeed` | 200 | u/s |
| `slideRequiredStartSpeedAir` | 90 | u/s（只在 M10R 会话读到） |
| `slideSpeedBoost` | 150 | u/s |
| `slideSpeedBoostCap` | 400 | u/s |
| `slideAccel` | 50 | u/s² |
| `slideDecel` | 100 | u/s² |
| `slideVelocityDecay` | 0.7 | 每秒 |
| `slideStopSpeed` | 125 | u/s |
| `slideMaxStopSpeed` | 350 | u/s |
| `slideWantToStopDecel` | 400 | u/s² |
| `slideJumpHeight` | 50 | u |
| `slideMaxJumpSpeed` | 350 | u/s |
| `slideSuperJumpHeight` | 65；Alter 90 | u |
| `slideSuperJumpCooldown` | 2；Alter 5 | s |

### 3.2 攀爬（mantle 前的爬墙）

| 键 | 值 | 单位 |
|---|---|---|
| `climbEnabled` | true | – |
| `climbHeight` | 100；Revenant 1250 | u |
| `climbSpeedStart` | 200 | u/s |
| `climbFinalJumpUpHeight` | 28 | u |
| `mantleAngleScale` | 1 | – |

### 3.3 蹬墙跑（正式服默认关闭）

`wallrun` = false。playlist 变量 `survival_wallrun_enabled` 和 `survival_jumpkit_enabled` 都是 0（`<game root>/platform/playlists_r5_patch.txt:5261-5262`，后面几个 playlist 也一样）。

| 键 | 值 | 单位 |
|---|---|---|
| `wallrun_timeLimit` | 2 | s |
| `wallrun_hangTimeLimit` | 4 | s |
| `wallrunAccelerateHorizontal` | 200 | u/s² |
| `wallrunAccelerateVertical` | 450 | u/s² |
| `wallrunMaxSpeedHorizontal` | 225 | u/s |
| `wallrunMaxSpeedVertical` | 112 | u/s |
| `wallrunJumpOutwardSpeed` | 188 | u/s |
| `wallrunJumpUpSpeed` | 240 | u/s |
| `wallrunJumpInputDirSpeed` | 75 | u/s |

以下几个键只在 Gibraltar 和 Valkyrie 的会话里读到：

| 键 | 值 | 单位 |
|---|---|---|
| `wallrunUpWallBoost` | 250 | u/s |
| `verticalGainCutoff_wallrun` | 175 | u/s |
| `wallrunAllowedWallDistance` | 17 | u |
| `wallrunAllowedWallDistanceWallHang` | 18 | u |
| `wallrunCeilingLimit` | 0.5 | – |

### 3.4 滑索和 ziprail

只在 Gibraltar 和 Valkyrie 的会话里读到，两者的值相同。

| 键 | 值 | 单位 |
|---|---|---|
| `ziplineSpeed` | 600 | u/s |
| `ziplineDetachSpeed` | 600 | u/s |
| `ziplineMaxVerticalDetachSpeed` | 1500 | u/s |
| `ziprailAcceleration` | 150 | u/s² |
| `ziprailDetachSpeed` | 450 | u/s |
| `pathGravityAcceleration` | 400 | u/s² |
| `maxSpeedMultiplier` | 1.2 | – |
| `minSpeedFraction` | 0.57 | – |
| `maxJumpOffSpeed` | 550 | u/s |
| `minJumpOffSpeed` | 100 | u/s |
| `viewInfluenceOnJumpDirection` | 0.5 | – |
| `detachDirMaxDownAngle` | 10 | ° |
| `detachDirMaxUpAngle` | 26 | ° |

SDK 的 `sdk_ziprail_tune_*` ConVar 默认值和上表一致（`SDK:game/server/zipline_exit_parity.cpp:240-258`）。

### 3.5 Valkyrie 喷气背包（对照 Gibraltar）

| 键 | Valkyrie | Gibraltar |
|---|---|---|
| `jetpackEnabled` | true | false |
| `jetpackThrust` | 1.9 | 1.2 |
| `jetpackMeterRate` | 1 | 2 |
| `jetpackMeterOnActivation` | 1 | 0 |
| `jetpackThrustScaleOnActivation` | 1.8 | 1 |
| `jetpackThrustScaleTimeOnActivation` | 0.5 s | 0 |
| `jetpackPostEffectTime` | 3 s | 0 |
| `jetpackPostEffectGravity` | 0.45 | 1 |
| `jetpackPostEffectDrag` | 0.000125 | 0.02 |
| `jetpackTightnessUp` | 0.27 | 0.5 |
| `jetpackTightnessDown` | 0.1 | 0.5 |
| `jetpackTightnessSideways` | 0.11 | 0.5 |
| `jetpackTightnessForwardBack` | 0.14 | 1 |
| `glideDuration` | 8 s | 1.8 s |
| `glideRechargeOnlyInGroundedState` | false | true |

### 3.6 Pathfinder 钩爪（setfile，M10R 会话）

| 键 | 值 | 单位 |
|---|---|---|
| `grapple_accel` | 1500 | u/s² |
| `grapple_decel` | 425 | u/s² |
| `grapple_airAccel` | 650 | u/s² |
| `grapple_airSpeedMax` | 420 | u/s |
| `grapple_speedRampMin` / `Max` / `Time` | 50 / 800 / 1.5 | u/s, u/s, s |
| `grapple_attachVerticalBoost` | 200 | u/s |
| `grapple_impactVerticalBoost` / `MaxSpeed` | 300 / 300 | u/s |
| `grapple_detachVerticalBoost` / `MaxSpeed` | 200 / 200 | u/s |
| `grapple_detachHorizontalMaxSpeed` | 600 | u/s |
| `grapple_detachAwaySpeed` | 500 | u/s |
| `grapple_detachSpeedLoss` / `Min` | 300 / 460 | u/s |
| `grapple_detachGravityScale` / `Speed` / `Time` | 0.5 / 200 / 0 | –, u/s, s |
| `grapple_gravityFracMin` / `Max` | 0.25 / 0.7 | – |
| `grapple_detachLowSpeedThreshold` / `Time` | 250 / 1.5 | u/s, s |
| `grapple_swing` | false | – |
| `grapple_swingAccel` / `MaxSpeed` / `MinLength` | 2000 / 1000 / 150 | u/s², u/s, u |
| `grapple_power_regen_delay` / `rate` | 3 / 100 | s, 每秒 |

其余 `grapple_*` 键（`grapple_maxLength`、`grapple_shootVel`、`grapple_retractVel`……）在这个构建里读不到（census 显示 `-`）。完整列表见 CSV。

## 4. 武器移动倍率 [script]

来自 `PS:weapons/mp_weapon_*.txt`，只取 WeaponData 顶层的值，mod 里的覆盖值单列一栏。

| 武器组 | `move_speed_modifier` | `ads_move_speed_scale` | 出处示例 |
|---|---|---|---|
| 空手、近战、传家宝 | 1.15 | – | `mp_weapon_melee_survival.txt:27` |
| 手枪（P2020、RE-45、Wingman、Mozambique） | 1.0（缺省） | 1.0 | `mp_weapon_semipistol.txt:176` |
| 冲锋枪（R-99、Alternator、Volt、Prowler、CAR） | 1.0 | 0.75 | `mp_weapon_r97.txt:195` |
| 霰弹枪（Peacekeeper、Mastiff、EVA-8） | 1.0 | 0.9 | `mp_weapon_shotgun.txt:215` |
| 突击步枪（R-301、Flatline、Hemlok、Havoc、Nemesis） | 1.0 | 0.5 | `mp_weapon_rspn101.txt:203` |
| 轻机枪（Spitfire、Devotion、L-STAR、Rampage） | 1.0 | 0.4 | `mp_weapon_lmg.txt:151` |
| 精确射手武器（G7、30-30、Triple Take） | 1.0 | 0.425 | `mp_weapon_g2.txt:182` |
| Bocek | 1.0 | 0.85 | `mp_weapon_bow.txt:60` |
| 狙击枪（Longbow、Sentinel、Charge Rifle、Kraber） | 1.0 | 0.35 | `mp_weapon_dmr.txt:150` |
| 手雷（举起时） | 1.0 | 0.55 | `mp_weapon_thermite_grenade.txt:87` |
| Wattson 电网（`mp_weapon_tesla_trap`） | 1.07 | – | `mp_weapon_tesla_trap.txt:106` |
| instagib 模式枪（社区模式） | 1.8 | 1.0 | `mp_weapon_instagib.txt:205` |

mod 覆盖值有两种：近战类的某些 mod 把倍率改成 0.767384；几把狙击枪和精确射手武器（Sentinel、Longbow、G7、30-30、Triple Take、Charge Rifle、Bocek）的某个 mod 把倍率设成 1.15。具体是哪个 mod 没有展开，需要时可以去对应文件里查。

SDK 说明了倍率怎么进入移动：`SetupMove` 里是 `modifier(w) × modifier(w)`（`SDK:game/server/movescale_weapon_parity.cpp:1-5`）。M2 实测空手 msc = 1.15，所以这个乘积怎么解读还要核实，原文没有展开。

## 5. ConVar

### 5.1 SDK 注册的 ConVar [sdk-cvar]

这些默认值写在 SDK 源码里，可以作为精确值。它们只管 SDK 自己实现或修补的机制。

| ConVar | 默认值 | 作用 | 出处 |
|---|---|---|---|
| `bridge_lurch_cutoff_speed` | 1100 | 水平速度超过它就不触发 lurch（只在 dedi 上） | `SDK:game/server/tapstrafe.cpp:33` |
| `mantle_boost_enabled` | 1 | mantle boost FSM 开关 | `SDK:game/server/mantle_boost.cpp:79` |
| `bridge_mantle_boost_sweet_spot_angle` | 1.5 | ° | `mantle_boost.cpp:90` |
| `mantle_boost_require_decreasing_view_angle` | 1 | | `mantle_boost.cpp:95` |
| `mantle_boost_min_valid_traversal_frac` | 0.5 | | `mantle_boost.cpp:97` |
| `bridge_mantle_boost_exit_speed` | 260 | u/s，拿不到 sprint 速度时的后备值 | `mantle_boost.cpp:101` |
| `bridge_mantle_boost_sprint_mult` | 1.3 | | `mantle_boost.cpp:103` |
| `bridge_mantle_boost_jump_height` | 90 | u | `mantle_boost.cpp:105` |
| `bridge_mantle_boost_gravity` | 750 | u/s² | `mantle_boost.cpp:108` |
| `mantle_boost_disables_tap_strafes` | 1 | | `mantle_boost.cpp:119` |
| `mantle_boost_input_setting` | 1（jump） | | `mantle_boost.cpp:86` |
| `bridge_slide_super_jump_height` | 150 | u，`boosted_slide_jump` mod 的值；基础 setfile 是 65（§3.1） | `SDK:game/server/slide_super_jump.cpp:45` |
| `bridge_slide_super_jump_cooldown` | 2 | s | `slide_super_jump.cpp:47` |
| `bridge_slide_gate_debounce` | 1.0 | s | `SDK:game/server/slide_gate_launch.cpp:50` |
| `jetdrive_initial_speed_mult` | 1.2 | | `SDK:game/server/jetdrive.cpp:75` |
| `jetdrive_decel_doublejump_time_window` | 0.75 | s | `jetdrive.cpp:67` |
| `jetdrive_stuck_speed` | 100 | u/s | `jetdrive.cpp:79` |
| `portal_teleport_min_speed` / `max_speed` | 300 / 1000 | u/s | `SDK:game/shared/portal/portal_shared.cpp:17-19` |
| `bridge_zip_cooldown_enable` | 0 | 滑索再上限次的冷却默认关闭 | `SDK:game/server/zipline_cooldown.cpp:30` |
| `sv_autobunnyhopping` | 0 | 社区功能（CS:GO 式自动连跳） | `SDK:game/server/autobunnyhop.cpp:14` |
| `sv_slope_launch` | 0 | 社区功能 | `SDK:game/server/slope_launch.cpp:25` |
| `sv_source_push_boost` | 1 | 社区功能（Source 式 trigger_push） | `SDK:game/server/source_push.cpp:30` |

### 5.2 引擎原生 ConVar [native-cvar]：静态无法确定

`sv_gravity`、`skip_time`、`skip_speed_reduce`、`skip_speed_retain`、`skip_jump_height_fraction`、`skip_jump_height_speed`、`jump_grace_jump`、`jump_grace_cutoff_speed`、`sv_friction`、`sv_stopspeed`、`sv_airaccelerate`、`sv_maxspeed`、`sv_maxvelocity`。这些名字都在 `<game root>/r5apex.exe` 里，大部分也在 `r5apex_ds.exe` 里（`jump_grace_*` 只在客户端）。

默认值是在代码里注册的，不在数据表里。我试过两种静态方法：
1. 扫字符串相邻关系；
2. 扫注册代码附近 RIP 相对的 `lea`。

两种方法给出的值都对不上已知事实，比如 `sv_gravity` 对上的是 "100"，而 M2 实测重力是 749.91 ± 0.71。所以这里**一个数也不报**。要拿精确值有两条路：
- 运行时在控制台执行 `help <cvar>`，或者用 runner 读取。这是最快的办法。
- 配置 Ghidra，再用 REA 反编译注册函数。

已经由别的证据确定的只有这些：

| 项 | 值 | 证据 |
|---|---|---|
| `sv_gravity` | 750 | M2 实测 749.91；SDK 后备值 750（`SDK:game/server/slide_super_jump.cpp:57`） |
| `skip_speed_reduce` | 100（"stock"） | 脚本注释（`PS:vscripts/sh_surf_movement.gnut:88-89`）。属于转述，不是读出的默认值 |
| `jump_grace_cutoff_speed` | 1100（推断） | SDK 注释说 `bridge_lurch_cutoff_speed` 是照它设的（`SDK:game/server/tapstrafe.cpp:31-36`） |

### 5.3 cfg 文件里的设置

| 文件 | 内容 | 说明 |
|---|---|---|
| `<game root>/platform/cfg/system/autoexec_server_dev.cfg:18-19` | `sv_updaterate_mp 20`、`base_tickinterval_mp 0.05` | 服务器 20 tick |
| `<game root>/platform/cfg/system/autoexec_client_dev.cfg:17-18` | `cl_updaterate_mp 20`、`base_tickinterval_mp 0.05` | |
| `<game root>/platform/cfg/speed.cfg` | `airSpeed 10000`、`slideSpeedBoost 1000`、`landSlowdownDuration 0` 等 | **调试用的娱乐覆盖**，不是默认值，不要当作 Apex 数值 |

## 6. 技能脚本常量 [script]

| 技能 | 常量 | 值 | 出处 |
|---|---|---|---|
| Octane 兴奋剂 | `STIM_DURATION` | 6.0 s | `PS:vscripts/weapons/mp_ability_octane_stim.nut:6` |
| | `STIM_HEALTH_COST` | 20 | `mp_ability_octane_stim.nut:7` |
| | `STIM_EFFECT_DEFAULT_SEVERITY`（`speed_boost`） | 0.15。注释说按 extraScale 2.0 计算，即 ×1.30 | `PS:vscripts/weapons/sh_stim.gnut:12,63` |
| | setfile mod `stim_sprint` | 内容在 rpak 里，没有读到 | `sh_stim.gnut:58` |
| Octane 跳板 | `JUMP_PAD_PUSH_VELOCITY` | 1150 u/s | `PS:vscripts/mp/sh_jump_pads.gnut:27` |
| | `JUMP_PAD_VERT_OVERRIDE` | 2.0 | `sh_jump_pads.gnut:28` |
| | `JUMP_PAD_ANGLE_LIMIT` | 0.70 | `sh_jump_pads.gnut:39` |
| 地图跳板（World's Edge） | `JUMP_PAD_PUSH_VELOCITY` | 2000 u/s | `PS:vscripts/mp/levels/mp_rr_desertlands_common.nut:19` |
| Horizon 重力升降机 | `SPACEELEVATOR_TUNING_UP_SPEED` | 300 u/s | `PS:vscripts/mp/sh_space_elevator.gnut:54` |
| | `SPACEELEVATOR_TUNING_UP_ACCEL` | 100000 u/s² | `sh_space_elevator.gnut:55` |
| | `SPACEELEVATOR_TUNING_HORIZ_SPEED` / `ACCEL` | 170 u/s / 2000 u/s² | `sh_space_elevator.gnut:56-57` |
| | `SPACEELEVATOR_TUNING_EJECT_UP_SPEED` / `HORIZ_SPEED` | 450 / 400 u/s | `sh_space_elevator.gnut:62-63` |
| | `SPACEELEVATOR_TUNING_LIFETIME` | 10 s | `sh_space_elevator.gnut:71` |
| Wraith 传送门 / 相位 | `PHASE_EXIT_VELOCITY` | 140 u/s（沿朝向） | `PS:vscripts/mp/sh_warp_gates.gnut:64,1081` |
| Valkyrie 喷气背包 | `VALK_JETPACK_SPEED` | 250 | `PS:vscripts/weapons/mp_ability_valk_jets.nut:26` |
| Valkyrie 升空 | `SKYWARD_MAX_HEIGHT` | 4500 u | `PS:vscripts/weapons/mp_ability_valk_skyward.nut:49` |
| | `SKYWARD_WAIT_TIME_BEFORE_LAUNCH` | 1.5 s | `mp_ability_valk_skyward.nut:51` |
| | `SKYWARD_LAUNCH_TIME` | 5.0 s | `mp_ability_valk_skyward.nut:33` |
| Pathfinder 钩爪（武器 `.txt`） | `grapple_power_required` | 100 | `PS:weapons/mp_ability_grapple.txt:47` |
| | `regen_ammo_refill_rate` | 10 | `mp_ability_grapple.txt:57` |
| Newcastle 被动 | `BOOP_PUSH_SPEED` / `LIFT` | 550 / 250 u/s | `PS:vscripts/pilot/_pilot_passive_newcastle.gnut:23-24` |
| 软着陆被动 | `HARD_LANDINGS_Z_VELOCITY_THRESHOLD` | −800 u/s | `PS:vscripts/pilot/_pilot_passive_soft_landings.gnut:63` |
| Sparrow mantle boost | 高度 / sprint 缩放 | 1.6666667 / 0.6666667 | `PS:vscripts/pilot/sh_pilot_passive_sparrow.gnut:92-93` |

Phase 2 的 M4、M6、M10 已经逐个审过技能的触发和代码路径：`../m4/ABILITY-TRIGGERS.md`、`../m6/SOURCE-AUDIT.md`、`../m10/*/`。这一节只把数值收在一起。

## 7. 适用范围和注意事项

1. **版本。** 这些全是 R5Flowstate 这个构建的值。R5Flowstate 把 S21 的客户端、S3 的 dedi 和 SDK 补丁混在一起，不等于 S21 正式服。
2. **设置会被覆盖。** 运行时，playlist、class mod（比如 `stim_sprint`、`boosted_slide_jump`）和脚本里的 `player.kv.*` 都可能改掉 setfile 的值。比如风洞会把 `airSpeed` / `airAcceleration` 临时改成 80/800（`PS:vscripts/_script_movers.gnut:2180-2192`）。
3. **数值不等于公式。** 加速曲线、摩擦公式、lurch 的窗口和强度这类规则写在原生代码里。目前的规则来自 M2、M3、M10 的测量模型，不来自这份表。
4. **census 覆盖范围。** 只有 M6 以后的部分会话读了扩展键（滑索、喷气背包），只有 M10R 读了钩爪键。在 CSV 里，没读过的格子是空的，读不到的键没有收录。
