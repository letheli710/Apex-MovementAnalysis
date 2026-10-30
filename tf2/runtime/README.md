# TF2 运行时测量工具（T5）

2026-10-29 交付。状态：**正式实验已完成**，结果见 [T5-REPORT.md](T5-REPORT.md)。下面第 5 节的限制大多已在 T5 中修掉。

## 1. 它做什么

一条命令完成一次实测，全程不用手动操作：

1. 先检查 R5 有没有在测：在测就等，等不到就放弃。
2. 拿共用锁，装模组，写入本次的实验表。
3. 通过 Steam 启动 TF2（Northstar），自动完成本地认证并进图。
4. 按实验表发按键和设置命令，客户端每帧记录一行。
5. 跑完自动退出，收集日志，恢复模组设置，释放锁。

## 2. 用法

```bash
C:/Users/<user>/AppData/Local/Programs/Python/Python311/python.exe -I runner.py smoke --timeout 420 --r5-wait 120
```

- 第一个参数是 [plans.py](plans.py) 或 [plans_t5.py](plans_t5.py) 里的实验名。实验由 `C("命令")`、`W(秒)` 和 `U(条件)` 组成。
- 实验表在**客户端线程**里执行（等入场动画结束后开始），`W` 是客户端游戏时间；每条命令打印 `HSDDIAG CMD <客户端时间>`。`U(cond, arg, timeout)` 逐帧等条件：`ground`、`air`、`wallrun`、`nowallrun`、`fall`、`hmin`、`hmax`、`zmin`。传送后要先等 `air`（见 `plans_t5.RA`）。
- 运行期间 `not_focus_sleep` 设为 0（退出时恢复），保证窗口在后台时仍是 144 fps。`meta.json` 的 `client_dt_median_ms` 应约为 7。
- `--map`：地图，默认 `mp_lf_stacks`。
- `--timeout`：最长运行秒数。
- `--r5-wait`：最多等 R5 空闲多少分钟。
- `--attach`：不启动新游戏，只接管一个已经开着的实例并收集日志。
- 输出在 `data/<时间>_<实验名>/`：
  - `diag.tsv`：所有 HSDDIAG 行；
  - `raw.log`：Northstar 原始日志，不进版本库；
  - `plan.gnut`：本次的实验表；
  - `meta.json`：结果，`outcome` 是 `exited`、`aborted_r5`、`timeout` 或 `no_game` 之一。
- 分析：[analyze_t5.py](analyze_t5.py)（按试次切段、逐帧打印）、[t5_metrics.py](t5_metrics.py)（各类指标）。

### 实验里可用的命令

| 命令 | 在哪执行 | 作用 |
|---|---|---|
| `+forward`、`-forward`、`+jump`、`+duck` 等 | 本地控制台 | 按键输入 |
| `hsd_tag <名字>` | 服务端 | 给后面的记录打标签，并记下服务器时间 |
| `hsd_setup ox oy oz vx vy vz pitch yaw` | 服务端 | 传送并设置速度和视角 |
| `hsd_kick vx vy vz` | 服务端 | 原地设置速度 |
| `hsd_query <setfile 键…>` | 服务端 | 读当前职业的设置值（只能读 global 表里的键） |
| `hsd_stim <秒>` | 服务端 | 兴奋剂效果（`StimPlayer`） |
| `hsd_weapon <类名>` | 服务端 | 切换（必要时给予）主武器 |
| `hsd_info` | 服务端 | 打印职业、武器、上报开关 |
| `hsd_probe [距离]`、`hsd_trace sx sy sz ex ey ez` | 服务端 | 射线探测，找墙面和地面 |

### 日志格式

- `HSDDIAG C <time> ox oy oz vx vy vz pitch yaw ground wallrun wallhang crouch fwd side buttons`
  - 客户端每帧一行（约 144 Hz），是预测后的玩家状态；`fwd`/`side` 是输入轴，`buttons` 位：1 跳、2 蹲、4 冲刺、8 瞄准、16 开火。
- `HSDDIAG CMD <客户端时间> <命令>`、`HSDDIAG UNTIL …`：实验表的执行记录。
- `HSDDIAG T …`
  - 服务端每 0.1 s 一行，多了滑铲和冲刺两个状态。
- `HSDDIAG TAG <名字> <服务器时间>`、`KICK`、`SETUP`、`Q`
  - 事件行。

## 3. 安全措施

| 风险 | 措施 |
|---|---|
| 干扰 R5 实测 | [r5_guard.py](r5_guard.py) 检测四类信号：r5apex 进程、hsd_session/hsd_trial 等 runner、AgentLink 端口 37019/37020、R5 的锁。R5 在测时不启动；运行中一旦检测到 R5，3 秒内关掉 TF2 游戏 |
| 两边抢机器 | 共用锁 `ReApex-DataAnalysis/GAME-LOCK.txt`，一方在跑另一方等，6 小时以上的锁算失效。R5 的两个会话（G-6、CAM2）已确认遵守 |
| 两个 TF2 会话同时拿锁 | 2026-10-30 修（FND-1）：10-29 11:34 W1 遇到过两个等锁的 runner 同时看到锁空、都写了锁。现在 `take_lock` 用独占创建（`O_CREAT\|O_EXCL`），只有一个能建成；建完再读回确认 `pid=` 是自己。没拿到就回去接着等（`runner.acquire`），拿到后再查一次有没有游戏或 R5 混进来，有就放锁再等。失效锁（>6 h）先原子改名挪开再建，两个会话同时清也只有一个成功。测试：[lock_race_test.py](lock_race_test.py)（不启动游戏，用临时锁路径）：5 轮 × 8 个进程同时抢，每轮恰好 1 个拿到；失效锁 8 个抢 1 个拿到；6 个完整 `acquire` 排队，持锁时间 0 次重叠 |
| 端口冲突 | TF2 本地服务器用 37115。R5 的启动脚本要求 37015 空闲 |
| vJoy 蓝屏 | 2026-10-28 一次 TF2 启动触发了 `vjoy.sys` 2.1.9 的蓝屏（0x3B）。现在启动参数带 `-nojoy`，日志的 Command line 一行可以核对 |
| 影响手动游玩 | 模组的自动运行开关平时是 0，只在 runner 运行期间写成 1，结束后改回。手动打开游戏时模组什么都不做 |
| 认证 | 不用任何绕过参数。走和 "Launch Northstar" 按钮相同的流程；Atlas 同意书由用户自己给，模组读不到同意就退出 |

## 4. 冒烟测试结果（2026-10-29，`mp_lf_stacks`，空手铁驭）

| 项 | 实测 | 静态预测 | 结论 |
|---|---|---|---|
| 客户端帧率 | 143.9 fps，p95 帧时间 7.0 ms | 上限 144 | 稳定 |
| 地面加速 | 2498.8 u/s² | 2500 | ✓ T-G01 |
| 走路速度上限 | 173.50 | 173.5 | ✓ |
| 松手减速 | 1501 u/s² | 2500 × 0.6 = 1500 | ✓ T-G03 |
| 无输入减速 | 1500.4 u/s² | 1500 | ✓ |
| 起跳竖直速度 | 约 298 | √(2·750·60) = 300 | ✓。它纠正了 T1 的 268.3：起跳不乘 gravityScale |
| 设置值读取 | airAcceleration 500、airSpeed 60、gravityScale 0.8、jumpHeight 60 | 同 T1 | ✓ |

## 5. 已知限制（2026-10-29 T5 后的状态）

1. ~~标签时间和输入时间对不齐~~：已修。分析按客户端记录的 CMD 时间和状态变化切段。
2. ~~UI 的 `wait` 和游戏时间不同步~~：冒烟测试里的 1.5 s 其实是开局入场动画冻结了玩家。现在实验表在客户端执行，并等入场结束。
3. `hsd_query` 读不到按站姿区分的键（`speed`、`acceleration` 等）和第二张表的键（`wallrun*`），会返回 null。仍然如此。
4. ~~主服务器上报~~：已修。`autoexec_ns_server.cfg` 会在服务器启动时把它设回 1，现在由服务端脚本关掉；日志里不再出现注册尝试。
5. ~~墙面坐标~~：西墙 x = −960（y −1400 … −500，z 150 … 600）。出生点朝 +y 只有约 570 u 空地。
6. 主服务器偶尔返回 "Invalid or expired masterserver token"，本地认证失败，脚本会退出，重跑即可。
7. 客户端日志的速度是帧末值：起跳后第一帧的 vz 比理论值低约 6.3（见 T5-REPORT 第 2 节）。

## 6. 文件

| 文件 | 作用 |
|---|---|
| [runner.py](runner.py) | 一次实测的全流程 |
| [plans.py](plans.py) | 实验表 |
| [r5_guard.py](r5_guard.py) | R5 检测和共用锁（独占创建） |
| [lock_race_test.py](lock_race_test.py) | 锁竞争测试：`python -I lock_race_test.py <runtime 目录> <临时目录>` |
| [analyze_smoke.py](analyze_smoke.py) | 冒烟测试分析 |
| [plans_t5.py](plans_t5.py) | T5 正式实验表 |
| [analyze_t5.py](analyze_t5.py)、[t5_metrics.py](t5_metrics.py) | T5 分析 |
| [T5-REPORT.md](T5-REPORT.md) | T5 报告 |
| [../mod/HSD.TF2Diag/](../mod/HSD.TF2Diag) | 诊断模组源码。runner 每次会复制到 `R2Northstar/mods/` |
