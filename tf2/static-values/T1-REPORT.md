# T1 报告：静态参数

日期：2026-10-28。全部是静态读取，没有启动游戏。

## 1. 来源和方法

TF2 的数值有三层，后一层覆盖前一层：

| 层 | 来源 | 怎么读 | 产物 |
|---|---|---|---|
| ① 代码默认值（`.set` 没写时生效） | `server.dll` 里内置的 playersettings schema 表：每条 0x30 字节，含键名、默认值字符串、说明文字、类型、结构体偏移 | [tools/scan_set_schema.py](tools/scan_set_schema.py) 直接扫 `.data` | [set-schema-server.tsv](set-schema-server.tsv)（约 276 个真实键；`client.dll` 有同一张表，默认值除 1 项泰坦脚步外全部一致） |
| ② `.set` 文件 | VPK 里的 `scripts/players/mp/*.set`，带 `#base` 继承 | [set_resolve.py](set_resolve.py) 解析继承链 | `local/pilot-sets-resolved.csv`（不进版本库，含原文） |
| ③ ConVar | `server.dll` / `client.dll` 的注册调用 `Register(&obj, "name", &default, flags[, "help"])`；`cfg/spmp.cfg` 按 MP/SP 覆盖 | Ghidra 12.1.4 headless + 复制来的 [ghidra/DumpConVarRegistrations.java](ghidra/DumpConVarRegistrations.java)，再用 [ghidra/parse_convar_dump.py](ghidra/parse_convar_dump.py) 从 DLL 里读默认值字符串 | [ghidra/convar-defaults.tsv](ghidra/convar-defaults.tsv) |

汇总表（含"R5 对应值"列，由 [build_tables.py](build_tables.py) 生成）：

- [setfile-values.csv](setfile-values.csv)：149 个移动相关的 `.set` 键。列包括 MP 值、SP 值、coliseum 值、代码默认值，以及 R5 census 值。
- [convar-values.csv](convar-values.csv)：199 个 ConVar。列包括默认值、注册位置、引擎说明、cfg 覆盖、R5 原生 ConVar 值。

二进制：`server.dll` sha256 `a5ca3a25…661af`。Ghidra 工程在 `ghidra-projects/tf2/`（server.dll + client.dll，已自动分析）。反编译原文在 `local/`，不进版本库。

**R5 的 Ghidra 脚本要改。** TF2 的 ConVar 注册是一次函数调用，默认值是第三个参数；R5 是静态初始化里先复制字面量。原脚本照用，只把默认值的提取挪到了 Python 里。

**和 R5 的一个区别**：R5 的 setfile 是编译后的 rpak，只能运行时读（census）。TF2 的 `.set` 是明文，代码默认值也有完整的表，**全部可以静态读出**。

## 2. 代表职业

MP 的 16 个蹬墙跑铁驭职业（grapple、stalker、geist、medium、nomad、heavy、light，各分男女）在移动键上**完全一样**（都继承自 `pilot_mp.set`，只是模型和音效不同）。表里用 `pilot_grapple_male` 代表。职业差别只在：

- `pilot_boost_*`（subclass boost，没有二段跳）：`speed` 160、`sprintspeed` 240、`jumpheight` 100、开 hover；
- `pilot_coliseum_*`（Coliseum 模式）：明显更快；
- 单人战役 `pilot_solo*`：`speed` 162.5、`sprintspeed` 243、`gravityscale` 0.75、`wallrunMaxSpeedHorizontal` 340；
- 战术技能、被动（`pas_wall_runner`、`pas_wallhang` 等）通过 ClassMods 改数值，见 `setfile-values.csv` 以外的解析表。

## 3. 和 R5 的对照：相同的部分

R5 从 TF2 继承后**没改**的值（这些可以看作"共用底层"的证据）：

| 组 | 键 | 值 |
|---|---|---|
| 地面上限 | `speed` / `sprintspeed` | 173.5 / 260 |
| 冲刺镜头时序 | `sprintStartDelay` / `sprintStartDuration` / `sprintStartFastDuration` / `sprintEndDuration` | 0.2 / 0.8 / 0.2 / 0.15 |
| 空中 | `airSpeed` / `airAcceleration`（TF2 是代码默认值，R5 setfile 里是同一个值） | 60 / 500 |
| 侧移后退 | `speedScaleSide` / `speedScaleBack` | 1 / 1 |
| 滑铲 | `slideRequiredStartSpeed` 200、`slideSpeedBoost` 150、`slideSpeedBoostCap` 400、`slideAccel` 50、`slideStopSpeed` 125、`slideMaxStopSpeed` 350、`slideMaxJumpSpeed` 350、`slideWantToStopDecel` 400、`slideJumpHeight` 50、`slideVelocityDecay` 0.7 | 全部相同 |
| ConVar | `sv_gravity` 750、`sv_friction` 4、`sv_stopspeed` 100、`sv_maxspeed` 320、`sv_airaccelerate` 10、`sv_backspeed` 0.6、`jump_graceperiod` 0.2、`slide_max_angle_dot` 0.6、`slide_step_velocity_reduction` 10、`slide_auto_stand` 0 | 全部相同 |
| lurch | TF2 的 `jump_keyboardgrace_strength` / `_max` = 0.7 / 0.7、`jump_keyboardgraceperiodmin` / `max` = 0.2 / 0.5 | **数值和 R5 的 `jump_grace_*` 完全一样**，只是改了名字。R5 多出的 `require_tap`、`cutoff_speed`、多次连按衰减这些项，TF2 里没有 |
| 钩爪 | `grapple_*` 的 detach / impact / gravityFrac 一组共 18 个 | 除 `grapple_power_regen_rate`（TF2 3，R5 100，单位制不同，待 T4 看）外都相同 |

## 4. 和 R5 的对照：不同的部分

| 键 | TF2 MP | R5 | 说明 |
|---|---|---|---|
| `acceleration` | 2500（代码默认） | 450 | TF2 只有一个加速度 |
| `lowSpeed` / `lowAcceleration` | -1 / -1 | 120 / 2500 | R5 的"低速段"在 TF2 里是关的（-1）。-1 的确切含义（比如回退到 `acceleration`）要在 T2 读代码确认 |
| `sprintAcceleration` / `sprintDeceleration` / `deceleration` | -1 / -1 / -1 | 100 / 1250 / 1250 | 同上。**T2 第一优先项**：TF2 的 -1 表示用哪个值、地面减速是不是改用 `sv_friction` 4 |
| `jumpheight` × `gravityscale` | 60 × 0.8 | 56 × 1.0 | 起跳速度 = √(2 · sv_gravity · H) = √(2·750·60) = **300**（Jump 0x180172870 不乘 gravityScale；T5 实测约 298），下落用 750 × 0.8 = 600。R5 是 289.8、下落 750。TF2 起跳更快、下落更慢，所以跳得更高、滞空更久（理论高度 75 u，R5 56 u）。2026-10-29 更正：原文写 268.3，那是误把 gravityScale 算进了起跳 |
| `stepheight` | 18 | 22 | |
| `slideDecel` | 50 | 100 | |
| `superjumpMin/MaxHeight`、`superjumpHorzSpeed` | 60 / 60 / 180 | 112 / 200 / 240 | TF2 二段跳更矮。R5 默认没有二段跳（只有 Sparrow） |
| `skip_time` | 0.1 s | 1.0 s | 连跳惩罚窗口。TF2 只罚落地后 0.1 s 内的跳 |
| `skip_speed_reduce` / `retain` | 12 / 450 | 100 / -1 | TF2 每次只扣 12，扣到 450 为止。**这就是 TF2 的 bhop 保速**：Apex 把它改成每次扣 100、没有下限 |
| `skip_jump_height_fraction` | 0.75 | 1.0 | |
| `sv_maxvelocity` | 12100 | 34000 | |
| `player_extraairaccelleration` | 2.0（"帮助开始蹬墙跑"） | R5 里有这个 ConVar，值未记录 | T2 看 |
| `wallrun` | 1 | false（关） | |

**蹬墙跑（T3 的输入）**：

| 键 | TF2 MP | TF2 代码默认 | R5 setfile 残留 |
|---|---|---|---|
| `wallrun_timeLimit` | 1.75 s | — | 2 |
| `wallrun_hangTimeLimit` | 4 s | — | 4 |
| `wallrunAccelerateHorizontal` | 1500 | — | 200 |
| `wallrunAccelerateVertical` | 360 | — | 450 |
| `wallrunMaxSpeedHorizontal` | 420 | — | 225 |
| `wallrunMaxSpeedVertical` | 225 | 300 | 112 |
| `wallrunMaxSpeedHorizontalBackward` | 50（代码） | 50 | 未读 |
| `wallrunFriction` | 4（代码） | 4 | 未读 |
| `wallrunJumpOutwardSpeed` | 205 | 250 | 188 |
| `wallrunJumpUpSpeed` | 230 | 320 | 240 |
| `wallrunJumpInputDirSpeed` | 80 | 100 | 75 |
| `wallrun_upWallBoost`（TF2 ConVar） | 250 | — | `wallrunUpWallBoost` 250（setfile） |
| `wallrun_allowed_wall_dist`（ConVar） | 13 | — | `wallrunAllowedWallDistance` 17 |
| `wallrun_allowed_wall_dist_wallhang` | 18 | — | 18 |

R5 把一部分 TF2 的 ConVar 改成了 setfile 键（`upWallBoost`、`allowedWallDistance`），这说明 Apex 的蹬墙跑代码不是原封不动保留的。T3 会对照两边的代码。

蹬墙跑相关的 TF2 ConVar 共 38 个（`wallrun_*`），全部带引擎说明，见 `convar-values.csv`。其中 MP 模式下 `cfg/spmp.cfg` 改了两项：`wallrun_gravityRampUpTime` 改为 0.7（代码默认 1.0），`wallrun_slipstarttime` 设为 1.5。

## 5. 未解项

1. `-1` 的含义（`deceleration`、`lowAcceleration`、`sprintAcceleration` 等）：留到 T2 读地面加速代码。
2. 有 13 个键在 schema 里没有默认值（`<none>`），`.set` 必须写，例如 `jumpHeight`、`stepHeight`。另有一张没有默认值的表，放的是 `speed`、`sprintspeed`、`wallrunAccelerate*` 等键。MP 铁驭的这些键 `.set` 都写了，所以对结果没有影响。
3. `grapple_power_regen_rate`：TF2 是 3、R5 是 100，两边单位不一致，留到 T4。
4. 运行时核对（Northstar 本地跑 `GetPlayerSettingsField` 和 `GetConVarString`）留到 T5。
5. 镜头晃动类（`bob_*`）不是 ConVar，是武器文件的键，留到 T2 镜头部分。
