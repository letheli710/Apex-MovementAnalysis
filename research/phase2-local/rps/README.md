# RPS：回放电机的滑铲规则换成原生（2026-10-28，D-47）

## 结论

- Unity 的**回放电机**（用 R5 录像的 usercmd 逐命令复现 R5 的那套，M1–M4 的回归锚点）以前一直用 M2 / M3 定下的滑铲规则；游戏身体（Reference / Fun）从 M10 / N7 起已经是原生规则。现在回放电机在**滑铲**上也按原生，和 Reference 一致。
- **没有任何一个录像变差。** 105 个 R5 录像（M1/M2 37、M3 30、M4 38）里 103 个逐命令轨迹逐字节相同；变了的只有 M3 两个 `e8_slide_chain`，都更接近 R5：水平速度误差 rms 7.48 → 0.15 u/s（M10 当时预计 7.5 → 0.15），事件时刻误差 12 → 0 条命令。
- **旧规则存档为 "Legacy M2"**，能逐字节复现改之前的全部回放输出（M2/M1 111/111、M1 首猜 111/111、M3 90/90、M4 114/114）。
- 游戏身体完全不变：105 个录像喂给 Reference / Fun 身体，轨迹和改前逐字节相同；真实按键演示和课程单圈见 HSD-Unity PR。

## 换了哪些开关

都是 `R5MotorV2Params` 的 `[NonSerialized]` 字段，这次只改默认值，没写新物理代码。Reference 本来就把它们设成这些值，这份清单和 `MovementConfigs.Reference()` 逐项核对过：Reference 打开、回放电机原来关着的滑铲项正好是这 7 个。

| 开关 | 原生（现在默认） | Legacy M2 | 来源 |
|---|---|---|---|
| `slideReleaseEnds`（值 `slideWantToStopDecel` 400、`slideMaxStopSpeed` 350 两边一样） | 松开下蹲：≤ 350 结束，> 350 减速 400 | 没有 | M10 r_slide [meas] |
| `slideBoostRearm` | 2.0 s | 0（每次都加速） | N7 S-02 [native] |
| `slideBoostCooldownFromStart` | true（从上次滑铲开始算） | false | N7 S-02 [native] |
| `slideRefundNeedsDuckTransition` | true（退还还要 200 ms 过渡没完） | false（只看 0.4 s 窗口） | N7 J-08 [native] |
| `slideDuckTransitionFromNextCommand` | true | false | F1-1 [meas] |
| `slideJumpFloorLowFrac` | 0.85（只抬 297.5–350） | 0（规则 H1：一律 ≥ 350） | N7 J-07 [native] |
| `slideSteerAccel` | 50·msc | 0 | N7 G-12 [native] |

没动的：斜坡开关（R6U U-1…U-5：`slopeUphillKeepStep`、`hullBottomRadius`、`slideRebeginOnGroundChange`、`slideSlopeAnyGrade`、`slideSlopeNeedsDuck`），非滑铲的 N7 项（`groundNativeFriction`、`extraAirAccel`、`sprintAccelFixedEdge`、`groundJumpSkipReduce`、`jumpSurfacePush`），以及 M5 的 `airUnduckDrop`（空中松开下蹲时原点下降 16.5 u，是下蹲碰撞体的规则，不算滑铲规则；Reference 开、回放电机关）。`slideBoostRefundWindow` 两边都是 0.4，`slideMaxJumpSpeedWindow` 两边都是 +∞。

## 改前 / 改后（逐录像，sim − R5）

改前 = Legacy M2（`BatchReplay -legacyM2`），改后 = 新默认。误差是逐命令对齐后的 rms / 最大值。

| 集合 | 录像数 | 逐命令轨迹不变 | 变了 | 变差 |
|---|---|---|---|---|
| M1 + M2（`-motor both`） | 37 | 37 | 0 | 0 |
| M3 | 30 | 28 | 2 | 0 |
| M4（`-scenarios`，带技能组） | 38 | 38 | 0 | 0 |

| 录像 | 位置 rms (u) | 位置最大 (u) | 速度 rms (u/s) | 速度最大 (u/s) | 水平速度 rms (u/s) | 事件时刻误差（命令） |
|---|---|---|---|---|---|---|
| M3_e8_slide_chain_120fps_r1015 | 2.225 → 0.815 | 5.765 → 1.293 | 7.480 → 0.233 | 66.298 → 0.646 | 7.478 → 0.146 | 12 → 0 |
| M3_e8_slide_chain_120fps_r1016 | 2.196 → 0.900 | 5.623 → 1.415 | 7.480 → 0.256 | 66.305 → 0.727 | 7.477 → 0.154 | 12 → 0 |

为什么这两个变：录像最后在滑铲中松开下蹲（约 132 u/s，r1015 第 676 条命令）。R5 这一条命令就结束滑铲、按蹲走减速，旧规则继续滑（只减速 100），速度误差从 0.26 涨到 38 u/s 以上、停下晚 6 条命令；原生的松开下蹲规则（`slideReleaseEnds`）和 R5 一致。其他录像里这 7 条规则要么没被触发，要么触发后和旧规则算出同样的结果（逐命令轨迹逐字节相同）。

"变差"的判据（`rps_compare.py`）：位置 / 速度 / 水平速度的 rms 和最大值、起跳竖直速度、最高点误差、着地状态不一致的命令数，任何一个增加超过 1e-6，或者事件时刻误差变大。

## 新基线和怎么检查

- **新基线（原生规则）**：`unity/baseline_sha256.json`，426 个输出文件的 sha256（M2/M1 222、M3 90、M4 114；`.md/.json` 先把 CRLF 换成 LF，`index.md` 不算）。变了的两个录像的完整输出在 `unity/changed/`，对照表在 `unity/before_after.md`。
  - 检查：`python rps_check.py <输出目录>`（目录里有 `m2m1/`、`m3/`、`m4/`，命令行同下）。
- **旧基线（Legacy M2）** 仍是 `../m3/unity/regression_m2_m1`、`../m3/unity`、`../m5/unity/m4_replay`：
  - `BatchReplay ... -legacyM2` 的输出用 `../m4/unity/regression_check.py` 和 `../m5/unity/m4_replay_check.py --base m4_replay` 检查，必须全部相同。
- 报告里的 `model_choices` 在原生规则下多一行 "Slide rules (RPS, D-47) …"，写明用了原生滑铲规则；Legacy M2 不加这一行，所以旧输出逐字节不变。这也是为什么改后"不变"的录像按 steps.csv + summary（除 `model_choices`）判断，而新基线的哈希包含这一行。

```
Unity.exe -batchmode -quit -projectPath <HSD-Unity> -executeMethod HSD.R5Replay.Editor.BatchReplay.Run \
    -trial <abs>/m2/trials/<each> -trial <abs>/m1/trials/<each> -out <dir>/m2m1 -motor both [-legacyM2] -logFile <log>
Unity.exe ... -trial <abs>/m3/trials/<each> -out <dir>/m3 -motor v2 [-legacyM2] -logFile <log>
Unity.exe ... -trial <abs>/m4/trials/<each, not *_REJECTED> -out <dir>/m4 -motor v2 -scenarios <abs>/m4/unity/scenarios.json [-legacyM2] -logFile <log>
python rps_compare.py <legacy dir> <native dir> --md before_after.md
python rps_check.py <native dir>
```

绝对路径必须传（BatchReplay 把相对路径解析到 Unity 项目目录）。

## 文件

| 文件 | 内容 |
|---|---|
| `rps_compare.py` | 改前 / 改后逐录像误差对照 |
| `rps_check.py` | 新基线的 sha256 清单检查（`--write` 重写清单） |
| `unity/baseline_sha256.json` | 新基线清单 |
| `unity/before_after.md` | 对照表（脚本输出） |
| `unity/changed/<trial>/` | 变了的两个录像的完整输出（report.md、summary.json、steps.csv） |

切回旧规则、开关细节：HSD-Unity `Assets/HSD/R5Replay/Runtime/Abilities/SlopeSlide/README.md`（RPS 一节），存档：根目录 `R5-DIFF-ARCHIVE.md`（RPS 一节）。
