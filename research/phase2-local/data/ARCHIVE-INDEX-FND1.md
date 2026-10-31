# phase2-local/data 补交数据的存档清单（FND-1，2026-10-30）

来源：研究仓库主 checkout `Apex-MovementAnalysis` 里 20 个未跟踪的数据文件夹（10-23 到 10-27）。其中能进 git 的部分本次提交；`.gitignore` 原来就排除的部分（`platform/` 原始日志、`report/rows.csv`）复制进存档目录。主 checkout 里的原文件没动。

## 超过 50 MB 的文件

**没有。** 最大的一个是 `research/phase2-local/data/20261024_161715_B1_h120/report/rows.csv`，18.88 MB。所以 50 MB 规则（以及 GitHub 100 MB 硬上限）这次没有挪走任何文件。

## 不进 git、放进存档目录的文件（按规则，不是按体积）

共 309 个文件，362.29 MB。存档位置：`C:\Workspace\Playground\ReApex-DataAnalysis\_archive\Apex-MovementAnalysis\`，下面的相对路径和原来相同（`Apex-MovementAnalysis\` 下的路径）。只是复制，原文件都还在原处；存档目录不删。

| 组 | 文件数 | 大小 | 为什么不进 git |
|---|---:|---:|---|
| `20261024_125404_N8_altertac/platform/` | 16 | 7.42 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_125404_N8_altertac/report/rows.csv` | 1 | 5.01 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_125610_N8_altertac2/platform/` | 16 | 6.67 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_125610_N8_altertac2/report/rows.csv` | 1 | 4.42 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_154014_UI_mantle/platform/` | 16 | 11.47 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_154014_UI_mantle/report/rows.csv` | 1 | 8.10 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_154642_UI_mantle2/platform/` | 17 | 22.32 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_154642_UI_mantle2/report/rows.csv` | 1 | 16.24 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_155159_UI_mantle3/platform/` | 16 | 11.60 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_155159_UI_mantle3/report/rows.csv` | 1 | 8.19 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_161004_B1_pilot/platform/` | 16 | 2.84 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_161004_B1_pilot/report/rows.csv` | 1 | 1.72 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_161205_B1_pilot2/platform/` | 16 | 5.76 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_161205_B1_pilot2/report/rows.csv` | 1 | 3.56 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_161715_B1_h120/platform/` | 17 | 29.95 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_161715_B1_h120/report/rows.csv` | 1 | 18.88 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_162037_B1_h60/platform/` | 16 | 18.59 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_162037_B1_h60/report/rows.csv` | 1 | 12.05 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_162243_B1_h80/platform/` | 16 | 8.80 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_162243_B1_h80/report/rows.csv` | 1 | 5.47 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_162441_B1_h100/platform/` | 16 | 8.72 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_162441_B1_h100/report/rows.csv` | 1 | 5.40 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_162701_B1_h160/platform/` | 16 | 13.17 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_162701_B1_h160/report/rows.csv` | 1 | 8.46 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_162924_B1_h200/platform/` | 16 | 13.31 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_162924_B1_h200/report/rows.csv` | 1 | 8.53 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_163231_B1_h300/platform/` | 17 | 22.40 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_163231_B1_h300/report/rows.csv` | 1 | 14.78 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261024_163538_B1_h120cr/platform/` | 16 | 11.77 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261024_163538_B1_h120cr/report/rows.csv` | 1 | 7.30 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261025_035833_N10_cam/platform/` | 16 | 6.83 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261025_035833_N10_cam/report/rows.csv` | 1 | 4.58 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261025_040112_N10_zip/platform/` | 16 | 5.70 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261025_040112_N10_zip/report/rows.csv` | 1 | 3.57 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |
| `20261027_195644_F6_seed/platform/` | 16 | 11.17 MB | platform/：R5 原始游戏日志，含本机路径和命令行（.gitignore 原规则） |
| `20261027_195644_F6_seed/report/rows.csv` | 1 | 7.56 MB | report/rows.csv：逐行合表，可由原始日志用 hsd_tel.py report 重建（.gitignore 原规则） |

逐个文件的路径、大小、sha256、存档位置：[ARCHIVE-INDEX-FND1.tsv](ARCHIVE-INDEX-FND1.tsv)（309 行）。

### report/rows.csv 逐个列出

| 路径 | 大小 | sha256 |
|---|---:|---|
| `research/phase2-local/data/20261024_125404_N8_altertac/report/rows.csv` | 5256909 | `69502f3018b53b2cee6f68307337696778de140f1aee926cea0301af05fff56f` |
| `research/phase2-local/data/20261024_125610_N8_altertac2/report/rows.csv` | 4631332 | `0a969419e6292986fe57e610cc7d6432f36830c27e9da3c552b98816873b0e45` |
| `research/phase2-local/data/20261024_154014_UI_mantle/report/rows.csv` | 8495853 | `d61dd66020c7e90a61e4782d058186c3116daf1a8270c17d72bddbd9911f59aa` |
| `research/phase2-local/data/20261024_154642_UI_mantle2/report/rows.csv` | 17031283 | `c99c22f21af6b13416a759531426283ff56364d669105a51d8bee335caad37ff` |
| `research/phase2-local/data/20261024_155159_UI_mantle3/report/rows.csv` | 8591148 | `7479ab54cafcddd0540c332d16827c22717cfe513ab3e64c0ac57a1fd0d0f954` |
| `research/phase2-local/data/20261024_161004_B1_pilot/report/rows.csv` | 1798671 | `60173d8a05e0997419cc39fdd1214c5400378d6e152fff2405b6d4b1f851285e` |
| `research/phase2-local/data/20261024_161205_B1_pilot2/report/rows.csv` | 3734339 | `24a3abc9f39a2267c9a350088bfaf0352bb3ccb578fe09d2bfa1039c80500be3` |
| `research/phase2-local/data/20261024_161715_B1_h120/report/rows.csv` | 19799693 | `24f6638bad809896e23bebcfba0d1fd5608b7f54fc9396f3266847a06272dca0` |
| `research/phase2-local/data/20261024_162037_B1_h60/report/rows.csv` | 12637381 | `c0db2243a95318b8cb58748fa4a0a8ac664b4c6c3564dd5056410a142dad7c14` |
| `research/phase2-local/data/20261024_162243_B1_h80/report/rows.csv` | 5732547 | `e77d31600662ba8c88b0bc7f1b19e476e15a6301cf3139e78333b9b65dcb2979` |
| `research/phase2-local/data/20261024_162441_B1_h100/report/rows.csv` | 5658973 | `fc709ed865bfc6541f933e0b0e1696380616b8e479768266e944b6546aef3727` |
| `research/phase2-local/data/20261024_162701_B1_h160/report/rows.csv` | 8866373 | `d552e85fde3128125f39f63895c4ba9d7a347fcc0bfb3cc57156398a757304e4` |
| `research/phase2-local/data/20261024_162924_B1_h200/report/rows.csv` | 8946551 | `df6c4535baeac3717815ea5619f426b32c266bf781af7b3cd23a964e27ea5246` |
| `research/phase2-local/data/20261024_163231_B1_h300/report/rows.csv` | 15493138 | `29493ad626a467ed1fc370c685308f8ee323ad2885321acffc63121e9897c2ac` |
| `research/phase2-local/data/20261024_163538_B1_h120cr/report/rows.csv` | 7659576 | `4246dc2ef68bde30249397fd16d0acc6df0d1f81092fcd5366ad788d4eb1b1f1` |
| `research/phase2-local/data/20261025_035833_N10_cam/report/rows.csv` | 4802205 | `34b296bb4c1f436a0be4b0e885e39487a0e056c1978969723346020cf9272aa3` |
| `research/phase2-local/data/20261025_040112_N10_zip/report/rows.csv` | 3741863 | `19afafaf1a666bb7b79a83c43e84a6d94a3b351e66a57a14c6e6c32d49cc41fa` |
| `research/phase2-local/data/20261027_195644_F6_seed/report/rows.csv` | 7926797 | `7e0c23c92e003a6d7bf79333e2d719890240c67524479f3562918af272fe8506` |

## 进 git 的部分

258 个文件，19.33 MB。复制时逐个比对了 sha256。

## 私有仓库（2026-10-30，D-76）

这里列出的不进 git 的文件，已经全部存进私有仓库 [`letheli710/HSD-RawData`](https://github.com/letheli710/HSD-RawData)（按本仓库的同一路径放：`apex/research/phase2-local/data/<run>/platform/` 和 `report/rows.csv`，前面多一个 `apex/`），附逐文件 sha256 清单 `MANIFEST.tsv`；从 GitHub 重新检出逐个核对过，不一致 0、缺失 0。要用的话从那里复制回本仓库的对应路径即可，`.gitignore` 仍然排除它们。工作区 `_archive` 保留不删。

## 怎么改主意

这些文件不进 git 是沿用原来的规则：仓库是**公开的**，原始日志带本机路径、命令行和玩家账号名，`local/` 里是解包的游戏文件和反编译原文。如果要放进 git（或改放私有仓库），从存档目录按同样的路径复制回来、删掉对应的 `.gitignore` 行再提交即可，sha256 可以用上面的清单核对。
