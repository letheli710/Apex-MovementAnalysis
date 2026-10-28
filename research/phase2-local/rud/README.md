# RUD：回放电机的下蹲碰撞体和地面移动换成 Reference（2026-10-28，D-49）

## 结论

- Unity 的**回放电机**（用 R5 录像的 usercmd 逐命令复现 R5，M1–M4 的回归锚点）又往原生 / Reference 靠了一步，换了两样：
  - **下蹲碰撞体**（`airUnduckDrop` 16.5）：空中松开下蹲时，原点下降 16.5 u。
  - **有输入时的地面移动**：原生 WalkMove（`groundNativeFriction`，N7 G-07/G-08/G-14）。
  
  两样都和游戏身体 Reference 完全一样。没写新物理代码，只改了 `R5MotorV2Params.R5Reference()` 里的默认值。
- 105 个 R5 录像（M1/M2 37、M3 30、M4 38）里，**70 个逐命令轨迹不变，35 个变了。32 个变好或持平，3 个按判据算"变差"，都已查清原因，用户同意作为例外**（见下）。
  - M3 的 e3 侧向起跳整组大幅变好：位置误差 rms 例如 24.2 → 2.4 u（k60），速度误差 rms 56 → 5 u/s。
  - e3 滑铲跳 r650 / r651：位置误差 rms 7.26 → 2.54 / 7.05 → 1.09 u，着地时刻误差 10 → 0 条命令。
  - e8 连跳整组：位置误差 rms 8.0 → 0.6–1.4 u。
  - M4 空中控制、stim 空中、跳板下蹲也都变好。
- **旧电机存档在 "Legacy M2"**：`-legacyM2` 关掉这两样，和 RPS 的滑铲规则一起，仍然逐字节复现最老的回放基线（M2/M1 111/111、M1 首猜 111/111、M3 90/90、M4 114/114）。
- 游戏身体完全不变：105 个录像喂给 Reference / Fun 身体，轨迹和改前逐字节相同（各 105/105）。
- 原生着地探测距离查到了：`CategorizePosition`（r5apex_dx12 0x140a51bc0）向下探测 **2.0 u**（.rdata 0x1417f8698），向上速度大于 140 u/s（0x1417f8ad4）就离地。和 Unity 的 `groundProbe` 2 一样，不用改。

## 换了哪些开关

| 开关（`R5MotorV2Params`） | 现在（= Reference） | Legacy M2 / RPS 基线 | 来源 |
|---|---|---|---|
| `airUnduckDrop`（`airUnduckMinAfterTakeoff` 0.08、`hullCrouchTime` 0.2 两边一样） | 16.5：地上按住下蹲 0.2 s 后碰撞体变矮；空中松开（起跳 0.08 s 后起）原点下降 16.5 u，脚往下、头不动 | 0：没有下蹲碰撞体，空中松开不下降 | M5 reference_config [meas]，M3 e8 / e3 slide350 共 8 次 |
| `groundNativeFriction` | true：有输入的地面命令走原生 Friction + Accelerate（输入曲线 m(2−m)、和输入同向的速度在 wishspeed 内不受摩擦、分段加速、\|v\| ≤ max(\|v_旧\|, wishspeed)、< 1 归零） | false：M2 规则，速度方向立即转到输入方向 v = s·ŵ | N7 G-07/G-08/G-14 [native]，按键转向复现到 rms 0.002–0.046 u/s |
| `groundVectorRedirect` | true（被上一行盖过，和 Reference 一样设着） | false | M5 |

没动：斜坡（R6U U-1…U-5）和其余非滑铲的 N7 项（`extraAirAccel`、`sprintAccelFixedEdge`、`groundJumpSkipReduce`、`jumpSurfacePush`）。回放电机里它们仍是 M2/M3 规则。

## 先做过的第一版（M5 转向），为什么换成第二版

用户先选了"下蹲碰撞体 + 地面转向一起换"。第一版（HSD-Unity ac14658）换的是 M5 的 `groundVectorRedirect`：横向速度按减速度衰减，再沿输入方向加速。
- 第一版：变了 32 个。e3 整组大幅变好（r650 位置 rms 7.26 → 2.54、r651 7.05 → 1.36）。
- 但 M2 `e1_turn` r331 / r332 变差：鼠标转身时速度贴在 299 上限，M5 规则每条命令少约 0.044 u/s，速度误差 rms 0.1362 → 0.1372 / 0.0737 → 0.0756（R5 转身时速度一直是 299）。r1237 同下。
- 之后发现 Reference 里有输入的地面命令走的是 N7 原生 WalkMove（`groundNativeFriction`），它优先于 `groundVectorRedirect`；`MovementConfigs.Reference()` 的 provenance 写着 "superseded by groundNativeFriction"。

所以第二版把原生 WalkMove 一起打开，和 Reference 完全一致：
- e3 再好 20–40%（例如 k1 r601 0.69 → 0.47、r651 1.36 → 1.09）。
- e1_turn 的轨迹误差回到和改前一样。

用户的决定："第二版接受。既然他们的数据更相似，那就用第二版。"

对照表：第二版 `unity/before_after.md`，第一版 `unity/before_after_v1_m5redirect.md`。

## 改前 / 改后（逐录像，sim − R5）

改前 = RPS 基线（`../rps/unity/baseline_sha256.json`，重跑后 426/426 相同），改后 = 新默认。

| 集合 | 录像数 | 逐命令轨迹不变 | 变了 | 判据上变差 |
|---|---|---|---|---|
| M1 + M2（`-motor both`） | 37 | 32 | 5 | 2（e1_turn，例外 1） |
| M3 | 30 | 6 | 24 | 1（r1237，例外 2） |
| M4（`-scenarios`） | 38 | 32 | 6 | 0 |

完整表在 `unity/before_after.md`（`rud_compare.py` 的输出）。几个代表：

| 录像 | 位置 rms (u) | 速度 rms (u/s) | 事件时刻误差（命令） |
|---|---|---|---|
| M3 e3_right_k60 r627 | 24.23 → 2.43 | 56.30 → 5.25 | 47 → 47 |
| M3 e3_right_k25 r1112 | 23.77 → 3.26 | 55.32 → 7.13 | 17 → 17 |
| M3 e3_right_slide350 r650 | 7.26 → 2.54 | 35.71 → 3.98 | 20 → 0 |
| M3 e3_right_slide350 r651 | 7.05 → 1.09 | 35.73 → 3.78 | 20 → 0 |
| M3 e8_hop350_d0 r1236 | 8.02 → 0.62 | 62.21 → 5.73 | 16 → 0 |
| M3 e8_fast_hops r943 | 4.86 → 1.09 | 23.47 → 0.27 | 16 → 0 |
| M4 m4_stim_air r1516 | 20.50 → 1.85 | 32.45 → 2.93 | 26 → 24 |
| M4 m4_pad_crouch r1537 | 6.02 → 1.37 | 36.96 → 25.91 | 161 → 145 |

"变差"的判据（`rud_compare.py`）：位置 / 高度 / 速度 / 水平速度 / 竖直速度的 rms 和最大值，起跳竖直速度、最高点误差，着地 / 滑铲 / 冲刺 / 上限速度状态不一致的命令数，其中任何一个增加超过 1e-6；或者事件时刻误差的总和变大。

## 接受的三个例外（用户同意）

1. **M2 e1_turn r331 / r332：事件时刻误差 28 → 182、50 → 196 条命令。**
   - 唯一变的是"最高速度出现在第几条命令"。这段速度贴在 299 的平台上，取最大值落在哪一条由 1e-13 级的浮点噪声决定（R5 自己也只是 299.0005 的噪声）。
   - 轨迹误差和改前一样：位置 rms 0.739 / 0.576、速度 rms 0.136 / 0.074，到 0.001 都不变。物理上不算变差。
2. **M3 e8_hop350_d0 r1237：位置最大误差 20.2 → 26.6 u，最高点误差 16.7 → 17.1 u，起跳竖直速度误差 53 → 68 u/s。**
   - 位置 rms 7.92 → 6.26、速度 rms 61.7 → 40.6 是变好的。
   - 原因：连跳中 R5 第 498 条命令着地、499 立即起跳。沙盘第 498 条离自己的地面 2.075 u，刚超出原生的 2.0 u 着地探测（沙盘比 R5 高约 0.5 u），晚一条命令着地，那次紧接着的起跳就丢了。
   - 同条件的 r1236 从 8.02 变成 0.62。改前整段高 16.5 u，本来就晚 8 条命令着地。
   - 探测距离本身和原生一致，这是亚单位高度误差碰上的边界情况，不调参数掩盖。

## 新基线和怎么检查

- **新基线**：`unity/baseline_sha256.json`，426 个输出文件的 sha256（M2/M1 222、M3 90、M4 114；规则同 `../rps/rps_check.py`）。
  - 检查：`python rud_check.py <输出目录>`（目录里有 `m2m1/`、`m3/`、`m4/`，命令行见 `../rps/README.md`，不加 `-legacyM2`）。
  - RPS 基线（`../rps/unity/`）是 D-47 时的回放电机，现在没有开关能单独复现它（代码里是 `R5Reference().WithLegacyM2Rud()`）；它在这里只作为"改前"留档。
- **旧基线（Legacy M2）**：`BatchReplay ... -legacyM2` 的输出用 `../m4/unity/regression_check.py` 和 `../m5/unity/m4_replay_check.py --base m4_replay` 检查，必须全部相同。
- 报告的 `model_choices` 在新默认下多两行：一行写明地面移动用原生 WalkMove，一行写明用了下蹲碰撞体。`parameters` 多了 `groundVectorRedirect`、`airUnduckDrop`、`airUnduckMinAfterTakeoff`、`hullCrouchTime`。Legacy M2 都不加。
- 例外和代表录像的完整输出在 `unity/changed/`（e1_turn ×2、e3 slide350 ×2、r1237）。

## 文件

| 文件 | 内容 |
|---|---|
| `rud_compare.py` | 改前 / 改后逐录像误差对照 |
| `rud_check.py` | 新基线的 sha256 清单检查（`--write` 重写清单） |
| `unity/baseline_sha256.json` | 新基线清单 |
| `unity/before_after.md` | 第二版（采用）对照表 |
| `unity/before_after_v1_m5redirect.md` | 第一版（M5 转向，没采用）对照表 |
| `unity/changed/<trial>/` | 例外和代表录像的完整输出 |

切回旧电机、开关细节：HSD-Unity `Assets/HSD/R5Replay/Runtime/Abilities/SlopeSlide/README.md`（RUD 一节）。存档：根目录 `R5-DIFF-ARCHIVE.md`（RUD 一节）。
