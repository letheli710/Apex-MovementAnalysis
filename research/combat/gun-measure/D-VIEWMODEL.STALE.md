# `D-VIEWMODEL.tsv` 已作废（2026-11-05）

**文件留档不删，不要再用它定枪口点。**

| 用途 | 改用 |
|---|---|
| 腰射枪口 | [`hold-pose/HP-POSE.tsv`](hold-pose/HP-POSE.tsv)，`state` = `stand` |
| 开镜枪口（机瞄） | [`iron-sights/data/IS-GUNS.tsv`](iron-sights/data/IS-GUNS.tsv)，`aim_F`、`aim_R`、`aim_U` |
| 开镜枪口（装瞄具） | [`iron-sights/data/IS-OPTIC-FOV.tsv`](iron-sights/data/IS-OPTIC-FOV.tsv)（只测了 R-301，Sentinel 只有枪口和挂点） |

## 哪里错了

开镜 30 行里 14 行的 U 差 0.43–1.12 u（Mastiff、Triple Take、Kraber、Longbow、Sentinel、G7、Wingman、Charge Rifle、Havoc、Devotion、Rampage、L-STAR、30-30、Bocek）。逐把的数字在 [`iron-sights/data/D-VM-PITCH.tsv`](iron-sights/data/D-VM-PITCH.tsv)。

## 原因

**之前写的"开镜动画没停"是错的，已改正。** 那是没看原始日志时的推断。现在看了同一次运行的逐帧日志：

- 旧表的窗口里枪已经停了。Wingman 在日志 1.90–2.44 s 一直是 F 21.2、U −1.33，变化 0.00。除 Kraber 外，这 11 把在日志 1.95–2.35 s 内变化都不超过 0.11 u。Kraber 开镜要 0.58 s，这个固定窗口里还在动，旧表用的窗口比它晚。
- **真正的原因是眼睛不水平，而旧脚本按世界坐标轴相减。** `an_d.py` 的 F、R、U 是 `m - c` 的 x、y、z，没有转到镜头坐标。Triple Take 之后的运行，日志里眼睛俯仰是 −1.175°（`ea=-1.175`）。枪口在前方 F 处，于是 U 多了 F × tan(1.175°)。
- 转到镜头坐标后：有俯仰记录的 11 把（Triple Take、Kraber、Longbow、Sentinel、G7、Wingman、Charge Rifle、Havoc、Devotion、Rampage、30-30）和新值只差 −0.01 到 +0.14 u，中位数 0.03 u。俯仰是 0 的 16 把，除 Mastiff 外本来就只差 0.07 u 以内。**[实测 + 计算]**

## 没查清的

- **L-STAR、Bocek**：日志没有 `clip` 行，读不到俯仰。要解释差值需要 1.23°、0.91°，L-STAR 接近 1.175°，这是推断。Bocek 的 F 还差 1.08 u，不是俯仰能解释的，原因没查。
- **Mastiff**：俯仰是 0，日志窗口里 U 是 −2.37，和新值一样，但旧表写 −1.40。旧表的时间窗取到了别处，具体怎么取到的没查。
- **为什么是 −1.175°**：没查。这批运行之间没有把视角复位，看起来是前面的运行留下的，这是推断。

## 影响

- **腰射行有同样的错**：同一批枪的腰射 U 也带这个误差。和 `HP-POSE` 比差 0.44–1.83 u，Bocek 4.73 u。`HOLD-POSE.md` 记过这个差别但当时没查原因，转正后还剩一部分，没有逐把解释。
- **同一批运行的其他表**：`D-JOLT` 是相对开火前的差，不受这个影响。其他从 `fr_*` 算绝对位置的表没有逐一复查。
- **枪模**：`HSD-Unity-GUNMODEL/Docs/tools/gun-models/extract_r5_dims.py` 读的是 `HP-POSE` 和 `IS-GUNS`，不读这张表，不受影响。
