# N0 环境和试点

日期 2026-10-23。只读：没有改游戏文件，没有 patch exe，没有启动游戏（运行时 ConVar 核对是会话「从 rea 获取精确数值」做的）。

**脚本和输出**（`n0/`，只含地址和函数名，没有反编译内容）：
- `cmp_clients.py <SDK src> <exe A> <exe B>`：用 SDK 客户端特征码在两个 exe 里定位函数并逐字节比较（§2）；
- `CheckBounds.java`：Ghidra headless 脚本，`-process r5apex_dx12.exe -noanalysis -readOnly -postScript CheckBounds.java <命中表> <输出>`（§3）；
- `dx12-bounds.tsv`：§3 的核对结果。

## 1. 二进制检查（加壳、混淆）

| 二进制 | `.text` 大小 | `.text` 熵 | 入口 | 结论 |
|---|---|---|---|---|
| `r5apex_dx12.exe` | 19.9 MB | 6.62 | 在 `.text` 内 | 没有加壳 |
| `r5apex.exe` | 19.7 MB | 6.62 | 在 `.text` 内 | 没有加壳 |
| `r5apex_ds.exe` | 19.5 MB | 6.62 | 在 `.text` 内 | 没有加壳；带 `.ooa` 节（4 KB，EA 激活相关的残留）和高熵的 `_RDATA`（7.25，36 KB），都很小，不涉及移动代码 |

- 熵 6.6 是普通编译代码的水平。加壳或加密的代码段接近 8.0。
- 两个客户端都有一个 21 KB 的可写可执行节 `.l2`，内容相同大小。很小，不在移动代码区间里，暂不深究。
- `r5apex.exe` 的 Ghidra 日志里有 3 个函数出现"跳进不存在的内存"警告（0x140c09d70、0x140c14b50、0x140c24620）。它们都不在移动代码区间里（SDK 定位到的移动函数集中在 0x140230300–0x140adf530）。

## 2. dx12 客户端和 r5apex.exe 的移动代码是否相同

方法：用 SDK 客户端代码（`SDK:game/client/*.cpp`）里的 103 个特征码，在两个 exe 的 `.text` 里各找一次；再用 `.pdata` 的函数边界取出所在函数，逐字节比较。

| 结果 | 数量 |
|---|---|
| 特征码在两边都唯一命中 | 101 |
| 只在 dx12 命中 | 2（`SceneView_DrawScene`、`SceneView_AllocFrameMRTs`，DX12 渲染） |
| 两边都能取到函数边界 | 94 |
| 长度相同 | 93 |
| 长度相同、且差异只出现在 4 字节以内的连续段（地址、偏移字段） | **93 / 93** |
| 长度不同 | 1（`PortalSurf_Transparent`，渲染） |

比较过的移动函数包括 `Jump`（1644 字节）、`AirMove`、`AirMove_TapStrafe`、`AirAccelerate`、`FullWalkMove`、`Duck`、`TraversalMove`、`SetGroundEntity`、`TouchGround`、`JumpOutOfWallRun`、`MeleeWalkMove`、`JumpPadLaunch`、`ApplyGravityCannonLaunch`、`Zipline_Use` / `JumpOff`、`GetTraversalViewPosition`、`EyeAngles`。

**结论**：两个客户端是同一源码的两次构建，区别在渲染代码。移动代码除了地址以外相同。所以：
- 在 `r5apex.exe` 上得到的结论（包括 ConVar 默认值）可以用于 dx12 版；
- 但地图里的地址以 dx12 版为准，因为实验和以后的 Frida 观察都用 dx12 版。

注意：`.pdata` 给出的是"函数块"，有些大函数被拆成多块（比如 `FullWalkMove` 的入口块只有 31 字节）。这里比较的是特征码所在的那一块，不是整个函数。N1 用 Ghidra 的函数边界再全面比一次。

## 3. Ghidra 自动分析

| 二进制 | 耗时 | 工程 |
|---|---|---|
| `r5apex.exe` | 608 s（16 GB 堆） | `ReApex-DataAnalysis\ghidra-projects\r5apex.gpr`（会话「从 rea 获取精确数值」） |
| `r5apex_dx12.exe` | 590 s（16 GB 堆） | `ReApex-DataAnalysis\ghidra-projects\r5apex_dx12.gpr` |

工程在仓库外，不进 git。dx12 版的反编译警告同样只有 3 个函数（0x140c3b920、0x140c46760、0x140c56230），对应 `r5apex.exe` 里的那 3 个，不在移动代码里。

**函数边界核对**（Ghidra 脚本 `CheckBounds.java`，在 dx12 工程上只读运行）：103 个 SDK 特征码命中点里，**102 个正好是 Ghidra 识别出的函数入口**，也正好是 `.pdata` 的块起点。剩下 1 个（`PlaylistGetCurrentVar`，不是移动函数）Ghidra 没有在那里建函数。

Ghidra 给出的完整函数大小（dx12）：

| 函数 | 入口 | 大小（字节） |
|---|---|---|
| `CGameMovement::Jump` | 0x140a3b550 | 6434 |
| `TraversalMove` | 0x140a45380 | 6831 |
| `AirMove` | 0x140a48f90 | 4408 |
| `AirMove` 里的 tap-strafe 段 | 0x140a48a30 | 1372 |
| `FullWalkMove` | 0x140a4c810 | 2081 |

## 3.1 REA 本身的问题

用 REA 的 `open_binary` + `procedure_info` 打开 dx12 客户端，**连续两次超时**（`provider_timeout`，"Ghidra startup deadline elapsed"，时限 330 s）。

原因：REA 的 Ghidra 后端每次都在临时目录新建工程，把整个 exe 重新导入、重新分析一遍。这个 exe 全量分析要约 590 s，超过了时限。它不会复用我们已经分析好的工程。超时后没有残留进程。

**影响和对策**：
- 对 44 MB 的 exe，REA 目前不能直接用来做交互分析。
- N1 先改用**直接跑 Ghidra headless 脚本**（本次的 `CheckBounds.java`、另一个会话的 `DumpConVarRegistrations.java` 都是这样做的），复用 `ghidra-projects\` 里分析好的工程。只读、可以复现，输出写进我们的 CSV。
- REA 的 `open_binary` 支持导入分析快照（`snapshot_path`）。能不能用我们的工程做出快照、绕开重新分析，留作工具改进项，不阻塞 N1。

## 4. 定标

由会话「从 rea 获取精确数值」完成，结果见本文件夹 [convar-defaults/](convar-defaults/README.md)：
- 39 个名字里 35 个是 ConVar，默认值全部读出，并且和运行时读数全部一致；
- `sv_gravity` = 750、`jump_grace_cutoff_speed` = 1100、`skip_speed_reduce` = 100，三个已知值都对上。

计划 §6 已列出这批 ConVar 带来的第一批对照（lurch 强度和窗口一致；夹紧 209.3 没有 ConVar 出处；连跳惩罚对不上）。

## 5. 闸门：通过

| 条件 | 结果 |
|---|---|
| 二进制没有加壳、能分析 | 通过：三个 exe 的代码段熵都是 6.62；两个客户端的 Ghidra 全量分析都在 10 分钟左右完成 |
| 定标值对上 | 通过：`sv_gravity` 750 等三个已知值；35 个 ConVar 静态值和运行时一致 |
| SDK 命名函数的边界对上 | 通过：102 / 103 个特征码正好是 Ghidra 的函数入口 |
| 主目标确定 | `r5apex_dx12.exe`。它和 `r5apex.exe` 的移动代码除地址外相同（93 / 93），所以已有的 `r5apex.exe` 结果可以沿用 |

**需要注意**：REA 的 Ghidra 后端对这么大的 exe 会超时（§3.1），N1 先直接用 Ghidra headless 脚本。

可以进入 N1。按计划 §10 第 5 条，N0 做完先停下来汇报，等用户决定是否继续。
