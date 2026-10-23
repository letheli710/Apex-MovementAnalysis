# N1 原生移动系统骨架地图（dx12 客户端）

日期 2026-10-23。目标二进制 `r5apex_dx12.exe`（理由见 [N0-PILOT.md](N0-PILOT.md)）。只读：Ghidra headless 脚本跑在已分析好的工程上，没有改任何游戏文件。所有地址都是 dx12 版的。

**这是骨架，不是公式。** N1 回答"有哪些函数、各管什么、读哪些参数、谁调用谁"。每个函数里的公式是 N2 的事。

## 1. 数字

| 项 | 数量 | 文件 |
|---|---|---|
| 地图里的函数 | 2534 | [map/functions.csv](map/functions.csv) |
| 其中核心（移动代码区间内 + 已命名的起点） | 553 | 同上，`window` 非空或 `reason` = seed |
| 其中有名字的 | 96 个 SDK 名 + 66 个我们起的临时名 | 同上，`name_source`；临时名的依据在 [n1/names-dx12.tsv](n1/names-dx12.tsv) |
| ConVar 读取点 | 1749（约 1000 个不同的 ConVar，含调试和渲染类） | [map/reads.csv](map/reads.csv)，`kind` = convar |
| setfile 键描述符 | 671 个，其中 578 个有代码读取 | [map/setfile-keys.csv](map/setfile-keys.csv) |
| setfile 读取点（地图内） | 923 | [map/reads.csv](map/reads.csv)，`kind` = setfile |
| SDK 客户端钩子 | 70（66 个 detour + 4 处字节补丁），62 个已对上 dx12 地址 | [map/sdk-hooks.csv](map/sdk-hooks.csv) |
| 镜头效果 | 23 项 + 3 个边界项 | [camera/CAMERA-INVENTORY.md](camera/CAMERA-INVENTORY.md)、[map/camera-effects.csv](map/camera-effects.csv) |

**地图怎么划的**：
1. 三个地址区间里的所有函数（`n1/windows-dx12.tsv`）：
   - `gamemovement`：0x140a30000–0x140a60000，`CGameMovement` 一带；
   - `player`：0x140af0000–0x140b12000，`C_Player` 一带；
   - `zipline`：0x14073a000–0x14074e000。
2. 加上 SDK 命名函数和我们命名的函数作为起点。
3. 从这些函数往下追 2 层被调用者（工具函数），往上追 4 层调用者（入口链）。

追出来的 1981 个外围函数大多是数学、射线检测、网络这类通用代码，地图里保留，但不分类。

## 2. 两个关键的读法发现

这两点决定了以后怎么读代码，也改正了 N0 之前的一些假设。

**① ConVar 是从对象 +0x40 读的。** ConVar 注册时，名字写在对象 +0x18，默认值字符串在 +0x48，但移动代码读取时 88 / 88 次都读对象 +0x40（`n1/ConVarReaders.java`）。只认 +0x40 的引用，就能可靠找出每个 ConVar 被哪些函数读；其他偏移的命中是数据表字段造成的误报。

**② setfile 键不是按名字查的，而是通过"描述符"。** `.data` 里每个 setfile 键有一个描述符：
- +0x0：int32 索引，文件里是 −1，运行时才填；
- +0x4：类型（2 = float 418 个，5 = 字符串 156 个，0 = bool 70 个，另有 1、4、6、7）；
- +0x8：键名指针。

代码读描述符 +0x0 拿到索引，再去当前传奇的 setfile 里取值。所以"谁读描述符 +0x0"就是"谁读这个 setfile 键"（`n1/scan_setfile_desc.py`、`n1/SetfileReaders.java`）。census 的 158 个键全部找到了描述符；另外 **513 个键我们从来没读过值**，比如 `slideRequiredStartSpeedAir`、`wallrunJumpUpSpeed` 和全部镜头键。这些值可以用现有的 `bridge_classvar_get` 补读（运行时，N4）。

## 3. 每条 usercmd 的入口链

```
0x1407ea760  Pred_RunCommands?            （预测：逐条命令）
  0x14092ab70  Pred_RunCommand?
    0x140a33cf0  GameMovement_ProcessMovement?
      0x140a54e80  PlayerMove              （6962 字节；读 slide_auto_stand、airslowmo_*、freefall_*）
        0x140a4c810  FullWalkMove          （SDK 名；MOVE-TRACE 就挂在这里）
          ├─ Jump 0x140a3b550 / AirMove 0x140a48f90 / SetGroundEntity 0x140a51650
          ├─ WallRun_Move 0x140a4a7c0 / WallClimb_Move 0x140a4d4e0 / CategorizePosition? 0x140a51bc0
          ├─ Grapple 0x140a36130、0x140a3e4f0 / Tether 0x140a3f050
          └─ 地面加减速 0x140a36a90、0x140a36c20、0x140a4d040 …
```

带 `?` 的是按调用位置和读取的参数起的临时名，N2 确认。命令计时（dt 怎么用、按键边沿怎么判）在这条链的上半段，是 N2-T 的起点。

## 4. 子系统划分（核心 553 个函数）

分类办法：先看函数读了哪些 ConVar / setfile 键，按名字归类；再看 SDK 名；都没有的，按调用方和被调用方多数的类别推断，标 `?`。可靠分类（不带 `?`）只有 160 个，其余 342 个是推断，51 个分不出来。

| 子系统 | 可靠 | 含推断 | 关键函数（dx12） |
|---|---|---|---|
| G 地面 | 18 | 73 | `Ground_GetAccelDecel` 0x140a36580（读 `acceleration`、`deceleration`、`sprintAcceleration`、`sprintDeceleration`、`slideDecel`、`slideWantToStopDecel`、`speed`）、`FullWalkMove`、`Duck`、打滑 0x140a36a90 / 0x140a36c20 |
| J 跳跃、空中、落地 | 24 | 69 | `Jump` 0x140a3b550（读 `skip_*`、`doubleJump`、`superjump*`）、`AirMove`、`AirAccelerate` 0x140a485e0（读 `player_extraairaccelleration`）、`SetGroundEntity`（读 `skip_time`、`landSlowdownDuration`）、`Fall_Check` 0x140a53180、`Land_PickAnim` 0x140a53990 |
| L lurch | 2 | 2 | `AirMove_TapStrafe` 0x140a48a30（读全部 `jump_grace_*`）、`TapStrafe_MultiTapDecay` 0x140a48810 |
| S 滑铲 | 4 | 5 | `Slide_TryBegin` 0x140a54890（读 `slideRequiredStartSpeed(Air)`、`slideSpeedBoost`、`player_slideBoost*`、`slide_max_angle_dot`）、`Slide_VelocityDecay` 0x140a4a280、`Slide_StepVelocityReduction` 0x140a47a40 |
| M 攀越、mantle、墙 | 27 | 88 | `TraversalMove` 0x140a45380、`AutoMantle_Try` 0x140a43060、`AutoMantle_Search` 0x140a40c90、`Traversal_Window` 0x140a42410、`WallRun_Move` 0x140a4a7c0、`WallRun_TryStart` 0x140a4e220、`WallClimb_Move` 0x140a4d4e0、`JumpOutOfWallRun` 0x140a50050 |
| P 钩爪 | 13 | 36 | `Grapple_SwingMove` 0x140a3cf80、`Grapple_AroundObstacle` 0x140a3e4f0、`Grapple_GravityFrac` 0x140a35d20、`Grapple_DetachGravity` 0x140a36130 |
| Z 滑索 | 24 | 83 | `Zipline_Use` 0x1407496a0、`Zipline_JumpOff` 0x14073f280、`Tether_Move` 0x140a3f050 |
| F 外力 | 4 | 7 | `JumpPad_Launch` 0x140a38a90、`GravityCannon_Launch` 0x140a3af30 |
| C 镜头 | 32 | 63 | 见 [镜头清单](camera/CAMERA-INVENTORY.md) |
| X 其他 | 12 | 76 | 近战冲刺 0x140a591d0、`MeleeWalkMove`、跳伞 0x140a56a00、闪避 |
| T 时序和输入 | — | — | 入口链（§3）；按键输入 `IN_JumpDown` / `IN_JumpUp` 被 SDK 挂了钩子，地址待补 |

## 5. SDK 钩子：客户端核心移动函数几乎都被改过

[map/sdk-hooks.csv](map/sdk-hooks.csv) 列出了 SDK 客户端代码里的 70 个钩子。和移动有关的：

| 原生函数 | SDK 文件 | 用途（SDK 注释） |
|---|---|---|
| `FullWalkMove` | `move_sim_trace.cpp` | MOVE-TRACE 记录，前后还挂着自动连跳、source push、wall launch、slope launch、portal 预测、wall climb tap |
| `AirMove_TapStrafe` | `mantle_boost.cpp` | mantle boost 的客户端预测 |
| `TraversalMove` | `mantle_boost.cpp` | 同上 |
| `AirMove` | `trigger_cannon.cpp` | 重力炮空中控制锁 |
| `AirAccelerate`、`JumpOutOfWallRun` | `wall_launch.cpp` | Sparrow 墙面弹射的客户端预测 |
| `Jump` | `dodge_rules.cpp`、`double_jump_power.cpp` | 空中闪避规则；Sparrow 二段跳能量 |
| `TouchGround`、`SuitPowerUpdate` | `double_jump_power.cpp` | 同上 |
| `Duck` | `halfduck_zip_parity.cpp` | 滑索退出时半蹲状态的客户端/服务器一致 |
| `JumpPad_Launch` | `jumppad_predict.cpp` | 跳板发射状态的预测 |
| `GravityCannon_Launch` | `trigger_cannon.cpp` | 重力炮空中控制锁 |
| `MeleeWalkMove` | `melee_lunge_probe.cpp` | 近战冲刺的诊断 |
| `Zipline_Use`、`Zipline_JumpOff` | `zipline_disconnect.cpp` | 滑索跳离后重新抓取次数 |
| `IN_JumpDown`、`IN_JumpUp` | `dodge_bind.cpp` | 闪避键没绑定时把跳跃键接到闪避上 |

**这意味着**：我们在客户端测到的行为 = 原生代码 + 这些钩子的改动。很多钩子服务于 S21 之后的内容（Sparrow 等），或者只是诊断；但它们包在核心函数外面，**每个都要在 N2 确认三件事**：默认是否开启（很多由 `bridge_*` ConVar 控制）、开启时改了什么、对我们测过的场景有没有影响。账本里"原因 4：SDK 钩子改写"要用到这张表。

## 6. 已经可以记进账本的新发现

| 发现 | 依据 | 和实测的关系 |
|---|---|---|
| `sv_friction` 有两个读取点：0x140a50400（同时读 `sv_spec*`，像观战/穿墙移动）、0x140a507c0（同时读 `sv_maxspeed`） | `map/reads.csv` | M2 证明地面减速用 setfile `deceleration`。要确认 0x140a507c0 是否在普通地面路径上 |
| `sv_stopspeed`、`sv_airaccelerate` 在地图里**没有读取点** | 同上 | 符合"Source 遗留值，实际不用"的判断 |
| 地面加减速集中在一个函数（0x140a36580），同时读走路、冲刺、滑铲三套加减速键 | 同上 | N2-G 的第一目标：读出选键规则，对照 M2 的分速度段模型 |
| `AirAccelerate` 读 ConVar `player_extraairaccelleration` | 同上 | 可能和 M2 未解释的"空中残余增益 ≈1.4e-5·vz²"有关，N2-J 查 |
| 有 513 个 setfile 键从没读过值，包括 `slideRequiredStartSpeedAir`、`wallrunJumpUpSpeed` 等 | `map/setfile-keys.csv` | N4 用 `bridge_classvar_get` 补读，成本很低 |

## 7. 局限

- 函数名大多是临时名，分类有六成是推断（§4），N2 逐个确认。
- 只追了 2 层被调用者，深处的工具函数没有归类。
- ConVar 读取只认 +0x40。如果有代码通过别的方式读（比如先取对象指针再调虚函数），会漏掉。
- 编译器内联的代码（例如 lurch 在 AirMove 里）按所在函数记录，没有拆块。
- 8 个 SDK 钩子（`IN_JumpDown` / `IN_JumpUp`、`Glide_*`、`UseSelfCheck`、`WeaponWorldProxy_Update`、2 处字节补丁）的特征码写法和其他不同，地址还没对上。

## 8. 复现

```
analyzeHeadless <ghidra-projects> r5apex_dx12 -process r5apex_dx12.exe -noanalysis -readOnly ^
  -scriptPath n1 -postScript MapMovement.java n1/seeds-all-dx12.tsv n1/windows-dx12.tsv <raw>
analyzeHeadless ... -postScript ConVarReaders.java convar-defaults/ghidra/convar-names.txt <raw>/convar-readers.tsv
py -3 n1/scan_setfile_desc.py <r5apex_dx12.exe> > <raw>/setfile-descriptors.tsv
analyzeHeadless ... -postScript SetfileReaders.java <raw>/setfile-descriptors.tsv <raw>/setfile-readers.tsv
py -3 n1/build_map.py <raw> <s21-r5sdk/src> map
```

`<raw>` 是本机的 `local/n1-raw/`，不进 git（里面有字符串和浮点常量的原始导出）。提交的 `map/*.csv` 只有地址、函数名、参数名和计数。
