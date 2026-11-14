# 重建检验：出题和评分（hb-judge）

分支 `handbook/rebuild-judge`（从 `origin/handbook/base`）。**重建方（hb-rebuild）不应该看这个文件夹**，它只看 `handbook/*.md` 和 `handbook/tables/`。

## 文件

| 文件 | 内容 |
|---|---|
| [PROBLEMS.md](PROBLEMS.md) | 题目原文，以及标准答案用的精确读法（文字有歧义的地方）、关键数 |
| `answers/<题号>.csv` | 标准答案：S1 – S5、L1_50 / 100 / 200 / 400、L2，每条命令一行 |
| `harness/` | 生成标准答案的 dotnet 工程：只读编译 HSD-Unity main（17260f2）的 `R5Replay/Runtime` 和 `Game/Runtime`，跑 `MovementConfigs.Reference()`（msc 1）+ 原生镜头 `NativeCameraFeedback` |
| `ref_slide.py` / `ref_slide.md` | 用 04 章 §4.7 的伪代码（msc 1、带坡面项）逐命令重算每一段滑铲，和 Unity 答案对照 |
| `compare.py` | 评分脚本（合格线见脚本开头） |
| `REPORT.md` | 评分报告（重建方交卷后写） |

## 怎么重跑

```
dotnet build handbook/rebuild-test/judge/harness -c Release -o <out>     # 读 ../../../../../HSD-Unity，可用 -p:HsdUnity=<path> 改
<out>/JudgeHarness.exe handbook/rebuild-test/judge/answers
py -3 handbook/rebuild-test/judge/ref_slide.py
py -3 handbook/rebuild-test/judge/compare.py                       # 读 origin/handbook/rebuild-build 上的 build/out/<题号>.csv
py -3 handbook/rebuild-test/judge/compare.py --build-dir <folder>  # 或本地文件夹
```

没有改 HSD-Unity 的任何文件，没有开 Unity。编译产物放在仓库外。

## 两份答案的差（Unity 对 04 章伪代码）

`ref_slide.md`：7 段滑铲（S1、S2、S3 两段、S4、S5 两段），逐命令水平速度最大差 0.0001 u/s，结束的 tick 全部一样，加成有无一样。S3 起跳那一行 Unity 多 0.006 u/s（起跳命令的空中加速，03 章）。

## 自检

- `compare.py --build-dir answers`：10 / 10 过。
- 把 S1 的 `slide_end` 挪一条命令：基本过；把 L1_200 的镜头放大 2 %：不过（峰值差 0.18°）。
