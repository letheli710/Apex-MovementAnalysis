# 09 章附件：每把枪的完整数值

第 09 章正文只写规则和代表枪，每把枪的数在这里。全部由 `make_tables.py` 从研究仓库的 PR 分支读出来生成（`git show origin/<分支>:<路径>`），**来源都是 2026-11-14 还没合并的 PR**。PR 合并或改动后，在研究仓库根目录重跑：

```
py -3 -I handbook/09-combat-feel/make_tables.py
```

每张表第一行是 `#` 开头的说明（含出处），第二行是列名。列名后的方括号是单位：`[s]` 秒、`[deg]` 度、`[x]` 比例、`[1/s]`、`[1/s2]` 弹簧常数（作用在角度上，不换算）、`[rounds]` 发。本目录没有长度列，所以没有 `[u]` / `[m]`。

| 文件 | 内容 | 来源（研究仓库路径，PR） | 正文 |
|---|---|---|---|
| `recoil-springs.tsv` | 31 把枪 × 腰射 / 开镜：俯仰的冷 / 热弹簧 k、d，热度 hold / fade，soft / hard，`weaponFraction`，回落拟合 D、T、t50、t10，图案 value 的 delay / rate | `research/combat/recoil-view/FIT-TABLE.tsv`（PR #93） | §2.1、§2.2、§2.4、§2.5 |
| `gun-weight.tsv` | 31 把枪：收枪 / 掏枪 / 第一次掏 / 抬 / 放、换弹、`zoom_fov`、开镜时间、开镜移速、FOV 和枪偏移的窗口、空中开镜 / 蹲后坐倍数、射速、拉栓、弹匣；8 把枪的冲刺 / 滑铲 / 站立到开火（实测中位数） | `research/combat/gun-measure/GUN-VARS.tsv`、`C-RAISE2.tsv`（PR #95） | §3.1、§4、§7.4 |
| `reload-moments.tsv` | 28 把枪 × 战术 / 空仓：动画长、加弹、解锁时刻和比例 | `research/combat/gun-measure/reload-motion/RM-SUMMARY.tsv`（PR #95；D-118 定的数据来源） | §7.1 |
| `spread.tsv` | 31 把枪：腰射各姿态扩散、每发累计、上限、回落、基础过渡速度；开镜各姿态扩散 | `research/combat/gun-measure/report/06-hipfire-spread.md` §3、§6（PR #95） | §5.1 |
| `ads-curves.tsv` | R-301、Spitfire、Wingman 开镜 / 关镜时枪的路径（每 0.05 zf） | `research/combat/recoil-view/ADS-CURVES.tsv`（PR #93），原样复制 | §3.4 |
| `make_tables.py` | 生成上面五张表 | — | — |

**用的时候注意**

- `recoil-springs.tsv` 只有俯仰轴的弹簧；偏航、横滚的 k、d 和全部字段在 `HSD-Unity: Assets/HSD/Game/Runtime/Combat/Arsenal/WeaponData.gen.cs`（`springs.txt` 和武器文件原样生成，HSD-Unity PR #60 起，还没合并）。后坐图案表本身也在那里，这里不搬。
- `recoil-springs.tsv` 的 `fit_*` 列是按弹簧公式算的 [算]，只有 R-301、Spitfire、Wingman、P2020 有实测回落（正文 §2.1 验收表）。
- `reload-moments.tsv`：Sentinel 的 `length` 只到解锁（日志里读不到换弹序列），动画全长按 C-MOTIONS 的 2.99 / 4.05 s；Mastiff、30-30 是逐发装填，三列时刻只是整段的起止，逐发时刻在正文 §7.3。**不要用** `research/combat/gun-measure/C-RELOAD-SUMMARY.tsv` 的 `flag` 列（D-118 作废）。
- `gun-weight.tsv` 的 `raise[s]` 是字段 `raise_time`，**不是**冲刺到开火的时间（两者不成比例，正文 §4.4）。
- `spread.tsv` 是 S21 文件的顶层值；SDK 重写过的枪（30-30、Nemesis 等）本地可能不同。霰弹的扩散读数不用于弹丸（正文 §5.3）。
