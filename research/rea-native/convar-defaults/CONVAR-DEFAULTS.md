# 原生 ConVar 默认值（r5apex.exe，Ghidra + 运行时核对）

日期 2026-10-23。来自会话「从 rea 获取精确数值」。原先在 `phase2-local/static-values/STATIC-VALUES.md` §5.2，已整体移到这里。
路径约定：`phase2-local/…` 和 `phase1/…` 都相对于 `research/`；`<game root>` 是已安装的 R5Flowstate 目录。

默认值写在 exe 的静态初始化函数里：先把一个字符串字面量复制进 ConVar 对象作为默认值，再赋名字和 flags。每个值都有两份独立证据：

- **静态（Ghidra）：** 对象是 `<game root>/r5apex.exe`，SHA-256 `3f44bf9aec8a18e7fa578b8a4927d8d27bba5ab8980119be9935137adcd04cb5`，镜像基址 `0x140000000`。用 Ghidra 12.1.4 headless 做默认自动分析，再用脚本 [ghidra/DumpConVarRegistrations.java](ghidra/DumpConVarRegistrations.java) 处理 [ghidra/convar-names.txt](ghidra/convar-names.txt) 里的名字：找到名字字符串，跟到引用它的注册函数，反编译，读出默认值字面量。每个值的复制长度都等于字符串长度加 1，说明读到的就是被复制的那个字面量。完整的反编译输出包含游戏代码，留在本地（`ReApex-DataAnalysis/ghidra-projects/r5apex-convar-dump.txt`），不进仓库。
- **运行时：** 2026-10-23 用 [phase2-local/tools/hsd_cvar_help.py](../../phase2-local/tools/hsd_cvar_help.py) 启动游戏（firing range，无 cfg 覆盖）。
  - 在 dedi（`r5apex_ds.exe`，S3）上执行 `help <cvar>`；
  - 在实验实际用的客户端（`r5apex_dx12.exe`）上用脚本 `GetConVarString` 读值，因为客户端的 `help` 输出不经 AgentLink 回传。
  - 原始回复在本地 `phase2-local/data/20261023_173829_cvar_help/` 和 `phase2-local/data/20261023_174106_cvar_help/`。

**结果：所有名字的静态值和两边的运行时值完全一致，没有例外。** 注意 `r5apex.exe` 和 `r5apex_dx12.exe` 是不同的构建（SHA-256 不同），这里只是两者的数值一致。下表中"—"表示该进程里没有这个 ConVar。

| ConVar | 默认值 | 注册函数 | 默认值字面量 | dedi | dx12 客户端 | 引擎说明（dedi `help`） |
|---|---|---|---|---|---|---|
| `sv_gravity` | 750 | `0x1401b7f20` | `0x1414b9158` | 750 | 750 | World gravity. |
| `sv_friction` | 4 | `0x1401b9310` | `0x1413d2488` | 4 | 4 | World friction. (Equivalent player setting is in player settings files) |
| `sv_stopspeed` | 100 | `0x1401b80f0` | `0x1413cfbf4` | 100 | 100 | Minimum stopping speed when on ground. (Equivalent player setting is in player settings files) |
| `sv_maxspeed` | 320 | `0x1401b8830` | `0x141429798` | 320 | 320 | |
| `sv_backspeed` | 0.6 | `0x1401b9880` | `0x1413ea63c` | 0.6 | 0.6 | How much to slow down backwards motion |
| `sv_airaccelerate` | 10 | `0x1401b8a00` | `0x1413c7b54` | 10 | 10 | |
| `sv_maxvelocity` | 34000 | `0x1401b96b0` | 函数内联字面量 | 34000 | 34000 | Maximum speed any ballistically moving object is allowed to attain per axis. |
| `skip_time` | 1.0 | `0x14019ad80` | `0x1413ce4b8` | 1.0 | 1.0 | Time after landing that is considered "skipping" if the player jumps again |
| `skip_speed_reduce` | 100 | `0x14019b690` | `0x1413cfbf4` | 100 | 100 | Speed lost when skipping |
| `skip_speed_retain` | -1 | `0x14019b860` | `0x1413c67b4` | -1 | -1 | Speed loss doesn't go below this |
| `skip_jump_height_fraction` | 1.0 | `0x14019b2f0` | `0x1413ce4b8` | 1.0 | 1.0 | Jump height fraction when skipping |
| `skip_jump_height_speed` | 450 | `0x14019b4c0` | `0x1413c6920` | 450 | 450 | Jump height loss only applies above this speed |
| `skip_replenish_double_jump` | 1 | `0x14019af50` | `0x1413c53d8` | 1 | 1 | Whether the player can double jump after skipping |
| `jump_graceperiod` | 0.2 | `0x14019cc50` | `0x1413c67cc` | 0.2 | 0.2 | Extra time during which a player can jump after falling off a ledge |
| `jump_graceperiodmin` | 0.2 | `0x14019ce20` | `0x1413c67cc` | — | 0.2 | |
| `jump_graceperiodmax` | 0.5 | `0x14019cff0` | `0x1413d1c58` | — | 0.5 | |
| `jump_grace_jump` | 1 | `0x14019e040` | `0x1413c53d8` | — | 1 | |
| `jump_grace_strength` | 0.7 | `0x14019d1c0` | `0x1413e1e60` | — | 0.7 | |
| `jump_grace_max` | 0.7 | `0x14019d390` | `0x1413e1e60` | — | 0.7 | |
| `jump_grace_cutoff_speed` | 1100 | `0x14019e210` | `0x1414ddd40` | — | 1100 | |
| `jump_grace_require_tap` | 1 | `0x14019d560` | `0x1413c53d8` | — | 1 | |
| `jump_grace_limit_to_90` | 0 | `0x14019de70` | `0x1413c6578` | — | 0 | |
| `jump_grace_min_tap_period` | 0.0 | `0x14019d730` | `0x1413dca3c` | — | 0.0 | |
| `jump_grace_max_tap_count` | 1000 | `0x14019dca0` | `0x1413d23f4` | — | 1000 | |
| `jump_grace_decay_start_tap_count` | 1000 | `0x14019d900` | `0x1413d23f4` | — | 1000 | |
| `jump_grace_multi_tap_decay` | 1.0 | `0x14019dad0` | `0x1413ce4b8` | — | 1.0 | |
| `jump_grace_multi_tap_decay_velocity_based_max_speed` | 900 | `0x14019e5b0` | `0x1413d40a8` | — | 900 | |
| `jump_grace_multi_tap_decay_velocity_based_easing_type` | 1 | `0x14019e780` | `0x1413c53d8` | — | 1 | |
| `jump_grace_controller_disable_duration` | -1.0 | `0x14019e950` | `0x1413fac14` | — | -1.0 | |
| `slide_auto_stand` | 0 | `0x1401afb00` | `0x1413c6578` | 0 | 0 | Automatically stand when slide ends |
| `slide_max_angle_dot` | 0.6 | `0x1401af760` | `0x1413ea63c` | 0.6 | 0.6 | Cosine of max angle from forward that you can slide when sprinting |
| `slide_max_duck_frac_to_start` | 1.0 | `0x1401af590` | `0x1413ce4b8` | — | 1.0 | |
| `slide_step_velocity_reduction` | 10 | `0x1401af930` | `0x1413c7b54` | 10 | 10 | Velocity reduction when going up a step (is multiplied by step height) |
| `slide_whileInAir` | 0 | `0x1401afcd0` | `0x1413c6578` | 0 | 0 | Allows beginning a slide (including the boost) while still in the air |
| `player_movementBounds_predictionShare` | 1 | `0x14019abb0` | `0x1413c53d8` | 1 | 1 | |

**怎么读这些值**

1. **`jump_grace_*` 是 lurch（tap strafe）的参数，只存在于 S21 客户端，dedi 上没有。** 这和 Phase 1 记录的矛盾相吻合：dedi 上原生 lurch 的情况说不清，SDK 是另外移植过去的（`../../phase1/Movement-Analysis.md` §4.4）。这些参数分别是：
   - 强度和上限：0.7 / 0.7
   - 必须是新按下的方向键：`require_tap` 1
   - 速度超过 1100 不触发：`cutoff_speed`
   - 多次连按的衰减，速度相关的衰减上限 900
   - 窗口：`jump_graceperiodmin` / `max` = 0.2 / 0.5 s。

   这些值和 M3 的实测模型完全吻合（`../../phase2-local/m3/lurch/LURCH-MODEL.md:28,252-253`）。实测 λ = 0.70000（n = 44），对应 strength / max 0.7；窗口在起跳后 0.200 s 内是满强度，之后线性降到 0.5 s 为 0，对应 min / max 0.2 / 0.5。所以 M3 拟合出的四个数里，有三个现在有了引擎里的出处。唯一没有对应 ConVar 的是限速 209.3 u/s。注意 `jump_graceperiod` 本身（0.2，"走下边缘后仍可起跳"，即 coyote time）是另一个机制，只是数值碰巧和 min 相同。
2. **`skip_*` 是落地后立刻再跳的规则。** 落地后 1.0 s 内再跳算 skip，扣 100 水平速度，`retain` -1 表示扣到多低都可以。跳跃高度系数 1.0，即高度不变；系数只在速度高于 450 时才生效。M2 测的 hop 都在 299 u/s 以下，没有触发它。
3. **`sv_friction` 4、`sv_stopspeed` 100、`sv_airaccelerate` 10、`sv_maxspeed` 320 是 Source 遗留值。** 引擎自己的说明就写着"Equivalent player setting is in player settings files"。M2 已证明地面减速是 setfile 的 `deceleration` 1250，空中加速是 `airAcceleration` 500，不是这些 ConVar。
4. **不是 ConVar 的名字：** `player_slideBoostEnabled`、`player_slideBoostCooldown`、`player_slideSuperJumpEnabled` 在代码里没有被引用，两边也都读不到，应该是 setfile 键。`slide_super_jump_enabled` 不是注册，而是一次带回退值 1 的设置查询调用（在 `0x140a099b0`）。
