# convar-defaults：原生 ConVar 默认值

这是会话「从 rea 获取精确数值」（2026-10-23）的成果，交给 `rea-native` 的后续工作使用。对应 [../REA-PLAN-DRAFT.md](../REA-PLAN-DRAFT.md) N0 里"读出原生 ConVar 默认值"这一项，也可以直接作为 N1 的字符串锚点。

## 结果一句话

从 `r5apex.exe` 读出 35 个移动相关原生 ConVar 的默认值，每个都带注册函数地址。它们和运行时读数（dedi `help`、dx12 客户端 `GetConVarString`）**全部一致**。完整表格见 [CONVAR-DEFAULTS.md](CONVAR-DEFAULTS.md)。

## 关键发现

| 发现 | 依据 | 对后续工作的意义 |
|---|---|---|
| Lurch 参数：`jump_grace_strength` / `max` = 0.7，`jump_graceperiodmin` / `max` = 0.2 / 0.5 s，`require_tap` 1，`cutoff_speed` 1100 | Ghidra 静态值 + dx12 客户端运行时读数 | 和 M3 实测完全吻合（λ = 0.7；0.2 s 满强度、0.5 s 降到 0）。M3 模型的四个数里只剩夹紧 209.3 u/s 没有 ConVar 出处，留给 N2-L 去代码里找 |
| `jump_grace_*` 只存在于 S21 客户端，dedi（S3）上没有 | dedi 回复 "no cvar or command named …" | 支持"lurch 是 S21 客户端原生、dedi 靠 SDK 移植"。地图上 lurch 应只看客户端 |
| Skip（落地后再跳）：`skip_time` 1.0，`skip_speed_reduce` 100，`skip_speed_retain` -1，`skip_jump_height_fraction` 1.0，`skip_jump_height_speed` 450 | 静态 + 两边运行时 | 和计划 §6 "连跳惩罚对不上"那一条有关，是对照账本的输入。引擎自带说明在表里 |
| `sv_friction` 4、`sv_stopspeed` 100、`sv_airaccelerate` 10、`sv_maxspeed` 320 是 Source 遗留值 | 引擎说明写着 "Equivalent player setting is in player settings files" | 实际减速和空中加速来自 setfile（M2 已证明）。N2-G 读地面代码时可以确认这些 ConVar 是不是根本没被读 |
| `player_slideBoost*`、`player_slideSuperJumpEnabled` 不是 ConVar；`slide_super_jump_enabled` 是一次带回退值 1 的设置查询（`0x140a099b0`） | 代码里没有注册引用，两边都读不到 | 它们是 setfile 键，要从 setfile 读取的代码那边找 |

## 方法（可复现）

1. **Ghidra 工程：** `ReApex-DataAnalysis\ghidra-projects\r5apex.gpr`，在仓库外、只在本机。Ghidra 12.1.4 headless，默认自动分析，608 秒，`GHIDRA_HEADLESS_MAXMEM=16G`。
2. **提取脚本：** [ghidra/DumpConVarRegistrations.java](ghidra/DumpConVarRegistrations.java) 处理 [ghidra/convar-names.txt](ghidra/convar-names.txt) 里的名字。对每个名字：找到字符串，跟到引用它的静态初始化函数，反编译，读出复制进 ConVar 对象的默认值字面量。
   - 字面量的复制长度都等于字符串长度加 1，可用来自检。
   - 输出开头记录 exe 的 SHA-256、镜像基址和 Ghidra 版本。

   ```
   analyzeHeadless <ghidra-projects> r5apex -process r5apex.exe -noanalysis -readOnly ^
     -scriptPath <this folder>\ghidra -postScript DumpConVarRegistrations.java <names.txt> <out.txt>
   ```

3. **运行时核对：** [../../phase2-local/tools/hsd_cvar_help.py](../../phase2-local/tools/hsd_cvar_help.py)。它启动游戏（firing range），在 dedi 上执行 `help <cvar>`，在客户端上用脚本 `GetConVarString` 读值，然后退出。客户端控制台的 `help` 输出不经 AgentLink 回传，所以客户端只能用脚本读。

## 留在本机、不进 git 的东西

| 内容 | 位置 | 原因 |
|---|---|---|
| 完整反编译输出 | `ReApex-DataAnalysis\ghidra-projects\r5apex-convar-dump.txt` | 包含 Respawn 代码。规则见 [../README.md](../README.md)。以后也可以放进 `../local/` |
| Ghidra 工程 | `ReApex-DataAnalysis\ghidra-projects\` | 体积大（约 500 MB），而且是本机产物 |
| 运行时原始回复 | `phase2-local/data/20261023_173829_cvar_help/`、`…/20261023_174106_cvar_help/` | 原始游戏日志，规则和其他原始数据相同 |

## 注意

- 静态值来自 `r5apex.exe`，实验用的是 `r5apex_dx12.exe`，两者是不同构建。不过 [../N0-PILOT.md](../N0-PILOT.md) §2 已证明两边的移动代码除地址外相同，这里的运行时核对也确认 dx12 客户端的值一致。**这里的函数地址是 `r5apex.exe` 的**；地图以 dx12 为准时，地址需要换算。
- 默认值不等于任何模式下的生效值：playlist、cfg、class mod 都可能覆盖。这次核对是在 firing range 下做的，所有值都等于默认值。
