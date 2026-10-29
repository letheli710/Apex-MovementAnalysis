# G6：钩爪撞上时上抬（G-6）实测（D-52）

日期 2026-10-28 – 10-29。接 GN（[../gn/GN-GRAPPLE-NATIVE.md](../gn/GN-GRAPPLE-NATIVE.md)）留下的 G-6。

HSD-Unity 分支 `g6/impact-boost`；本仓库分支 `g6/impact-boost`。

## 1. 结论

- **原生代码**：S21 客户端在"接近脱钩"那一条命令里，钩在**世界几何**上（钩子没有父实体）时，会把 vz 抬到 min(vz + 300, 300)。
- **但 R5 实际的移动里没有这一下**：
  - 在世界墙上用 Frida 看到，pull step 里 vz 185.1 → **300**。
  - 同一条命令的 PlayerMove 却从上抬前的 185.1 开始算，算完是 **178.9**（只减了重力）。
  - 上抬（和接着的 ×0.677 缩放）都被丢掉了。
  - 8 条录像（不挂 Frida）里，世界墙和地面钩都没有跳。
- GN 看到的"vz 299"就是这个只在 pull step 里存在的中间值。
- 所以 Reference **默认仍关**。上抬做成**可选开关**（打开 = 照客户端代码加上，**不是 R5 的实际移动**）。
- 用户的决定："关留客选项开关在 decision markdown 里头记录一下"。

## 2. 原生规则 [native]

`Grapple_DetachSpeedLoss` `0x14066fb60`，接近脱钩分支 `0x14066fe4c`（Ghidra，r5apex_dx12）：

- **何时**：接近脱钩成立（距离 < 33，或 < 50 且在接近速度的斜坡阈值内），并且同时满足：
  - 正在拉（GrappleData +0x49）；
  - 钩子没有父实体（`FUN_1405ac0e0(hook) == 0`，就是 GN 用 Frida 读的 +0x148 为空）；
  - 有玩家；
  - vz < `grapple_impactVerticalMaxSpeed`（300）。
- **怎么加**：vz += `grapple_impactVerticalBoost`（300），再封顶 300。等价于 vz = min(vz + 300, 300)；vz ≥ 300 时不动。是"设到上限"，不是累加。
- **次数**：这个分支直接返回 1（这条命令脱钩），所以每次拉最多一次。
- **代码里没有"在地面上不加"的条件**。GN 版 Unity 代码里那个地面条件是推断，这次去掉了（打开开关时照代码加）。

## 3. 世界墙（不用摆道具）[meas]

[wall_scan.py](wall_scan.py) 在练习场里做水平射线，找到一面世界几何的墙（hitEnt = worldspawn）：

- 位置：x −11921.5、y ≈ 7280 – 7445，法线 (−0.996, −0.090, 0.001)。
- 高度：从地面（z 294.92，和测试跑道一样高）到 z ≈ 450 都是平的竖直面。
- 新日程（`hsd_trial.py`，用 `m10_g` 前缀，所以服务器的 GRS 记录也开着）：
  - `m10_g_ww400_p5` / `m10_g_ww400_p0`：从 x −12321.5、y 7400 出发，离墙 400，仰 5° / 0°；
  - `m10_g_ww_spr`：从 800 外冲刺过来再出钩。

## 4. 实测

### 4.1 录像（不挂 Frida）

会话 `20261028_231232_G6_wall`：Pathfinder，`--kit --m10-log`，120 fps，9 个里 8 个通过（23103 多跑 1 帧，没过）。用 [wall_detach.py](wall_detach.py) 读脱钩前后：

| 片段 | 客户端脱钩那帧前后的 vz（每帧） | 脱钩后 1 s 内比脱钩点高多少 |
|---|---|---|
| `ww400_p5` ×4（含热身、23103） | 181 → 175 – 185 → 179（每帧 −6.25，只有重力） | +19.5 – 21.0 u（抛物线，没有上抬） |
| `ww400_p0` ×2 | 46 → 39 | +1.0 u |
| `ww_spr` ×2 | 212 → 206、218 → 212 | +27.4 / +30.0 u |
| `g400_spr` ×2（地面钩） | 0，ground = 1（和 GN 一样） | 0 |

- 要是上抬生效，脱钩那帧 vz 应该跳到约 294，之后至少再升 50 u 左右。实际没有一个片段这样。
- 服务器的 GRS 记录两边时钟不同步，只拿来看形状：同样没有跳到 300。

### 4.2 Frida，只有客户端 [native + Frida]

会话 `20261028_231748_G6_frida`，脚本 [frida_impact.js](frida_impact.js)（只读），输出 [frida_impact_out.json](frida_impact_out.json)。第 2 个试验时客户端崩了，所以只有热身和 23201 两条：

| | 钩子父实体（+0x148） | pull step 进 → 出的 vz | 钩爪更新返回后 | 同一条命令的 PlayerMove 进 → 出 |
|---|---|---|---|---|
| 23201（`ww400_p5`） | **空**（世界） | 185.1 → **300.0** | (412.8, 203.1)：整个速度 ×0.677 | **185.1 → 178.9** |
| 热身 90（`ww400_p5`） | 0x11fbc（有父实体） | 55.0 → 55.0（没上抬） | ×0.624 | 55.0 → 48.7 |

- 23201 之后 23 条移动都是 −6.25 / 命令，第 5 条撞墙（vx 609.8 → 5.2）。没有哪一条用到了 300。
- 所以上抬（以及钩爪更新里那个 ×0.62 – 0.68 的缩放）只写进了钩爪更新自己那一份速度；接下来的移动从玩家本来的速度开始，把它覆盖了。
- 在哪里被覆盖没有追（ProcessMovement 准备 movedata 时又拷了一次，或者钩爪更新在另一份 movedata 上跑），[inf]。结果是确定的：客户端自己预测的轨迹也没有上抬。
- **没解释的一点**：热身那一次钩在同一面墙上，父实体却是 0x11fbc（有实体），并且脱钩算了两遍（预测重跑）。23201 是空的。可能热身时钩到了墙前的什么实体，没有查。
- 和 GN 一样，Frida 挂着时这些试验不拿来对轨迹。

## 5. Unity 的改动

| 开关 | 默认 | 打开后 |
|---|---|---|
| `GrappleS21Params.impactBoost` | **关**（Reference、Fun 和所有配置） | 接近脱钩、钩在世界上（不是道具、绳子）、vz < 300 时 vz = min(vz + 300, 300)；**不再要求离开地面**（照原生代码）。不是 R5 的实际移动 |

- **怎么打开**：
  - 游戏 Esc 菜单 "Grapple impact boost (G-6)"：只在原生钩爪规则下显示；PlayerPrefs `hsd.g6.impact`，1 = 开，默认 0。演示和 smoke 固定关。
  - `FeelBatch -impactBoost`：两个游戏身体都打开。
  - 代码里直接设 `impactBoost = true`。
- **`SetGnDetach` 不动它**：GN 那组开关的旧版 / 原生切换和这个无关；`-preGn` 也一律不上抬。
- 测试：`GnGrappleTests.G6ImpactBoostIsOptInAndOnlyOnWorldHooks`。墙钩接近脱钩：关 = 只有重力；开 = 跳到 300 再减重力；钩在道具上 = 和关一样。

## 6. 回归

见 DECISIONS D-52（数字在那里）。默认关，所以游戏身体的输出应该和 GN 逐字节相同。

## 7. 没做到

- 热身那次的父实体 0x11fbc 是什么，没查。
- 上抬在哪一步被覆盖（静态没追）。
- 打开开关后的 Unity 对 R5：没有把这次的世界墙片段导成 Unity 的对照输入（钩点是世界几何，Unity 打开就会多一下上抬，R5 没有，方向已经清楚）。
- 《泰坦陨落2》有没有这一下（D-48 的研究里可以顺便看）。

## 8. 方法和文件

- 找墙：游戏开着时 `py -3 wall_scan.py -o walls.json`（只读，服务器脚本射线）。
- 录像：`hsd_session.py --label G6_wall --trials 9 --run-base 23101 --batch-base 23101 -- --schedule "m10_g_ww400_p5*3,m10_g_ww400_p0*2,m10_g_ww_spr*2,m10_g_g400_spr*2" --legend pathfinder --kit --m10-log --fps 120 --no-census`；再 `py -3 wall_detach.py <会话目录>`。
- Frida：`hsd_session.py --label G6_frida --trials 6 --run-base 23201 --batch-base 23201 --settle-s 150 -- --schedule "m10_g_ww400_p5*2,m10_g_ww_spr*2,m10_g_g400_spr*2" ...（同上）`。客户端起来后用 REA 的 `start_frida_session` 附加 r5apex_dx12，加载 `frida_impact.js`；`frida_summary.py <输出 json>` 按每次脱钩汇总。
- 反编译原文在本机 `research/rea-native/local/`，不进 git。GrappleAnimSelectSequence `0x140b0dea0` 这次也读了：脱钩后它拿速度的一份拷贝去处理，再写回 movedata。钩爪更新返回后那个 ×0.62 – 0.68 可能来自这里 [inf]；上抬是在它之后的移动里丢掉的。
