# 交接：TF2 运行时实测（T5）

2026-10-29，交接方是"TF2 研究计划"会话。接手的会话从这里开始，不需要读之前的对话。

## 0. 先读这些（按顺序）

1. [TF2-PLAN.md](TF2-PLAN.md)：总计划和规则（第 0、4、5 节）。
2. [runtime/README.md](runtime/README.md)：测量工具的用法、安全措施、已知限制。**必读**。
3. [README.md](README.md)：各阶段报告索引。
4. 要核实的结论在这三处：[ledger/ledger.csv](ledger/ledger.csv)（T2 账本，"待定"项和标 [inf] 的项）、[wallrun/T3-REPORT.md](wallrun/T3-REPORT.md) 第 6 节、[unique/T4-REPORT.md](unique/T4-REPORT.md) 第 4 节。
5. 给人读的汇总：[TF2-VS-APEX.md](TF2-VS-APEX.md)、[TF2-MOVEMENT-SUMMARY.md](TF2-MOVEMENT-SUMMARY.md)。实测结果最后要回写到这两份里。

## 1. 现状

| 项 | 状态 |
|---|---|
| T0–T4 静态研究 | 完成 |
| 用户决定 | 蹬墙跑以 B 为基准（TF2 规则 + R5 残留数值），A（TF2 原版）做成可开关的预设；泰坦是否纳入未定 |
| T5 工具 | 已跑通并交付：runner、诊断模组、R5 守卫、共用锁 |
| 已有实测 | 只有冒烟测试 `runtime/data/20261029_002143_smoke`：加速 2500、减速 1500、走路上限 173.5、起跳约 298、144 fps 稳定 |
| 正式实验 | **未开始** |
| T6 报告与 Unity 提案 | 未开始 |

## 2. 不可违反的规则

1. **R5 优先，不能干扰 R5 实测。**
   - 只通过 `runner.py` 启动 TF2，它自带 R5 检测和共用锁 `ReApex-DataAnalysis/GAME-LOCK.txt`。
   - 不要绕过它手动开游戏做实验。
   - R5 会话（G-6、CAM2）已同意：启动前查锁、写 `r5 …`、跑完删除。
2. **不加任何认证绕过参数**。比如 `+ns_auth_allow_insecure`，自动模式的安全检查会拦，用户也没同意。
3. **启动方式不能改**：必须通过 Steam 启动，参数是 `-applaunch 1237970 -northstar -nojoy`。
   - 直接运行 NorthstarLauncher.exe 会认证失败（UNAUTHORIZED_GAME）。
   - 不要去掉 `-nojoy`。2026-10-28 一次启动触发了 `vjoy.sys` 2.1.9 的蓝屏（0x3B）。每次运行后都要在日志的 `Command line` 一行确认 `-nojoy` 在。
   - Steam 会丢掉过长的参数，`ns_startup_args.txt` 在这种启动方式下不会被读。所以运行参数靠 runner 写进 `mod.json` 的默认值，再由模组的 UI 脚本设置。
4. **只读**：游戏目录（允许写的只有 `R2Northstar/mods/HSD.TF2Diag` 和 `ns_startup_args.txt`）、R5 研究仓库、HSD-Unity、R5Flowstate。不改 Unity。
5. **只在本地私服做实验**，不连官方或公开服务器。
6. **意外关机或蓝屏后**，检查并清理两处残留：留下的 `GAME-LOCK.txt`（内容是 `tf2 …`），以及 `R2Northstar/mods/HSD.TF2Diag/mod.json` 里的 `hsd_autorun`，要改回 `"0"`。
7. 真正的 Python 是 `C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe`，运行时加 `-I`。

## 3. 正式实验前先修的三件事（runtime/README.md 第 5 节）

1. **切段方式。** `hsd_tag` 的时间戳比按键实际生效晚。冒烟测试里"起跳 243.9"的误判就是这样来的，实际约 298。
   - 推荐：分析时按状态变化切段，比如 `ground` 由 1 变 0 的帧、速度开始变化的帧。
   - 或者：在客户端记录按键发出的时间。
2. **UI 的 `wait` 和游戏时间不同步。** 冒烟测试中"前进"标签打出约 1.5 s 后才开始移动。需要精确时序的步骤，改到服务端计时（比如加一个服务端命令，在服务端按时间执行一串动作）。
3. **主服务器上报。** 服务端打印 `report=1`，UI 里设成 0 的命令可能没生效。先查 Northstar 日志确认本地服务器是否真的上报了。如果上报了，找一个不涉及认证绕过的关闭办法，再开始做大量实验。

## 4. 要做的实验（按优先级）

每项都写明要核实的结论出处。

### 4.1 共用底层抽查（T2 待定项）

| 实验 | 核实什么 | 出处 |
|---|---|---|
| 换一把 `move_speed_modifier` ≠ 1 的武器，测地面加速和减速 | 减速是否乘移动倍率（player+0x1600 是什么） | T-G04 |
| 起跳后 0.2 s 内新按方向键，对比按住不放 | lurch 是否必须新按键；强度 0.7，窗口 0.2 / 0.5 s，上限 0.7 × 冲刺速度 | T-L01、T-L02 |
| 落地后 0.1 s 内再跳，速度分别为 > 450 和 < 450 | skip 规则：−12，最低 450，高度 ×0.75 | T-J03 |
| 冲刺状态下滑铲；2 s 内连续滑两次 | 加速 +150 封顶 400、是否乘移动倍率、冷却 2 s 从上次起滑算 | T-S01、T-S02 |
| 滑铲中起跳 | 滑铲跳高度 50、速度上限 350、是否返还加速 | T-S06 |
| 有速度时在空中按方向键（已超过 60） | 额外空中加速 2.0 和 3D 速度上限 | T-J02 |

### 4.2 蹬墙跑（T3 第 6 节，B/A 两套方案都要用到这些规则）

先在 `mp_lf_stacks`（或别的小图）找一面足够长、足够高的竖直墙。可以用服务端 `TraceLine` 写一个探测命令，打印墙面坐标和法线。然后用 `hsd_setup` 把玩家放到墙边并给初速度。

| 实验 | 核实什么 |
|---|---|
| 贴墙起跑，记录竖直速度 | 沿墙"向上"的速度提到 ≥ 250 |
| 不按键贴墙 vs 按住前进 | 重力在 0.7 s 内从 0 线性升到满；前进时额外向上 0.65、竖直上限 225 |
| 跑满时长 | 1.75 s 后脱落；1.5 s 开始滑落，1.0 s 到满 |
| 墙跳（按方向键 / 不按） | 输入方向 80 + 离墙 ≥ 205；vz = min(230, vz + 345) |
| 水平速度 | 上限 420、加速 1500；朝后上限 50；摩擦每秒 4 |
| 同一面墙再贴 | 只能在上次接触点以下；0.2–0.4 s 排斥 |
| 起跑前的 0.5 s 计时 | player+0x2588 计的是什么 |
| 二段跳 | vz 替换为 300；水平方向 180 u/s 转向输入（初值是推断的） |

### 4.3 T4 选中项

- 兴奋剂的速度倍率：脚本系数 0.4，推测约 ×1.8。
- 用作手感参考的项目，按需要再测。

## 5. 工具速查

```bash
cd C:/Workspace/Playground/ReApex-DataAnalysis/TF2-Research/runtime
C:/Users/<user>/AppData/Local/Programs/Python/Python311/python.exe -I runner.py <实验名> --timeout 420 --r5-wait 120
```

- 新实验写在 `plans.py`，用 `C("命令")` 和 `W(秒)` 组成。
  - 按键用 `+forward`、`+jump`、`+duck` 等，在本地控制台执行。
  - `hsd_tag`、`hsd_setup`、`hsd_kick`、`hsd_query` 由服务端处理。
- 要加新的服务端命令或日志字段，改 `../mod/HSD.TF2Diag/` 的源码。runner 每次运行都会把它复制进游戏目录。
- 写 Squirrel 时的坑（都已经踩过）：
  - 客户端（CLIENT）没有全局 `ClientCommand`；UI 有，而且是在本地控制台执行。
  - 服务端脚本的 `WaitFrame` 只有 10 Hz，逐帧记录要放在客户端。
  - 模组脚本看不到 `IsStryderAuthenticated`。
  - 在客户端，`IsSliding` 和 `IsSprinting` 不一定能用。
  - 引用别的文件里的全局函数前，那个文件必须在 `mod.json` 里排在前面。
  - 编译错误会弹窗，并写进 nslog（`COMPILE ERROR`）。
- 日志在 `R2Northstar/logs/nslog*.txt`。runner 会把 HSDDIAG 行抽到 `data/<运行>/diag.tsv`。
- 想在运行时盯进度，用 Monitor 过滤 `HSDDIAG (UI|AUTH|TAG|DONE)|COMPILE ERROR|Command line`。

## 6. 产出要求

1. 写 `runtime/T5-REPORT.md`：每个实验写做了什么、数据目录、实测值、对应静态结论是否成立、未解项。
2. 回写结论：
   - `ledger/ledger.csv`：证据一栏加上 T5 实测，"待定"改成确定的分类；
   - [TF2-VS-APEX.md](TF2-VS-APEX.md) 和 [TF2-MOVEMENT-SUMMARY.md](TF2-MOVEMENT-SUMMARY.md)：⚠ 项改成实测结论；
   - 和静态结论不一致的，像 2026-10-29 更正起跳速度那样注明更正日期和原因。
3. 原始日志（`raw.log`）留在本地，不进版本库。
4. T5 结束后才进入 T6（写 `TF2-REPORT.md` 和 Unity 改动提案）。T6 的提案要用户逐项批准，不在本计划里改 Unity。

## 7. 联系

- 交接方会话：TF2 研究计划 [f295bd]。
- 用户偏好：中文、结构化、给人读的 md；R5 是基准；需要用户决定的事情要停下来问。
