# tables/：手册的三张总表

由 hb-tables 写（2026-11-14，分支 `handbook/tables`，还没合并）。

## 白话说明

手册正文讲规则；这里放"查一个数"用的表。每张表有一个 **TSV 原件**（机器读、校验脚本查）和一个 **md**（给人看）。改数先改 TSV。

| 表 | 原件 | 给人看 | 内容 |
|---|---|---|---|
| 参数对照表 | [`params.tsv`](params.tsv) | [`params.md`](params.md) | 150 个设计参数：R5 原值 [u]、[m]、身高比例、TF2、Unity 现在的值、一致吗、差别、出处 |
| 镜头事件表 | [`camera-events.tsv`](camera-events.tsv) | [`camera-events.md`](camera-events.md) | 76 行：每个镜头事件 × 通道的触发、力度、时长、叠加规则、R5 和 Unity 的值 |
| 关卡尺度表 | [`level-scale.tsv`](level-scale.tsv) | [`level-scale.md`](level-scale.md) | 38 行：跳多高多远、能翻多高的墙、台阶、斜坡、滑铲距离、跑墙、二段跳、跳板，全部由移动代码跑出来 |
| 单位换算 | [`units-conversion.tsv`](units-conversion.tsv) | [01 §2](../01-units-body.md) | 每种量纲乘多少（[01 §2.4](../01-units-body.md) 要的机器可读版） |

附件：

- [`unity-export/`](unity-export/)：Unity 单位导出的全量快照（`units-params.tsv` 13155 行参数值、`units-registry.tsv` 1945 个字段的量纲标记）。来自 HSD-Unity `units/switch` 5c79a50 的 `Docs/units/`（PR #88，还没合并），sha256 `b3fe6533…`（params）、`d4acbfc5…`（registry）。
- [`level_scale_harness/`](level_scale_harness/)：算关卡尺度的程序、它的原始输出和滑铲跳时机扫描。

## 防止 u 和米串了：校验脚本

```
py -3 handbook/tables/check_params.py                 # 用 unity-export/ 里的快照
py -3 handbook/tables/check_params.py --export <新的 units-params.tsv>
```

它检查：表里的参数名还在导出里、量纲和单位没变、"Unity 现在的值"等于导出、导出自己的 [m] = [u] × 0.0254^k、表里的 [m] 和身高比例是从 R5 原值算对的、"和 R5 一致吗"和两个数对得上；关卡尺度表和镜头事件表的 [m] 也查。对不上就打印每一处并退出码 1。

2026-11-14 结果：**通过**（params 150 行，其中 138 行对导出；level-scale 38 行；camera-events 76 行里 23 处 "u = m" 换算）。故意改坏三处（导出里一个量纲、一个值，表里一个 [m]）时报 4 处错误、退出码 1。

**什么时候跑**：HSD-Unity 合并了动参数的 PR、或者改了单位标记以后，重新导出一次再跑：

1. 在任意 HSD-Unity checkout（要有 `units/switch` 的代码）上：
   `Unity.exe -batchmode -quit -projectPath <工作树> -executeMethod HSD.Game.Editor.UnitsExport.Run -out <目录> -logFile <目录>\export.log`
2. `py -3 handbook/tables/check_params.py --export <目录>/units-params.tsv`
3. 每个报错：Unity 有意改的，改 `params.tsv`（值、一致吗、差别写 D-xx）；串了的，修 Unity。
4. 通过以后把新导出复制进 `unity-export/`，提交。

不要按进程名杀 Unity（别的会话可能在用同一个编辑器），用 `-quit` 让它自己退。

## 写法

- 列名都带单位体系：`[u]`、`[m]`；身高比例除以 H = 72 u（[01 §4.1](../01-units-body.md)）。
- R5 的函数地址只出现在"出处 / 依据"列。
- 引用没合并的 PR 写"PR #xx，还没合并"。
