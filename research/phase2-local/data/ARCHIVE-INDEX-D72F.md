# D-74 B Frida 会话原始数据存档清单（2026-10-30，会话 d72-crouch-mantle）

7 个 Frida 会话（`*_D72F_*`，100 fps，Frida 挂在客户端上）文件夹里 `.gitignore` 排除的部分（`platform/` 原始游戏日志：含本机路径、命令行和账号名；`report/rows.csv`：逐行合表，可用 hsd_tel.py report 从原始日志重建），和 Frida 探针逐帧输出 `trav_<高度>.csv`（探针脚本 [frida_d72_trav.js](../d72/frida_d72_trav.js)，汇总 [frida_d72_summary.py](../d72/frida_d72_summary.py) → `d72/out/frida/sum_*.csv`），复制到工作区存档目录 `_archive\Apex-MovementAnalysis-D72\`。会话文件的相对路径和仓库里相同；探针 CSV 在存档的 `frida/` 下（仓库里没有）。逐个文件的大小和 sha256：[ARCHIVE-INDEX-D72F.tsv](ARCHIVE-INDEX-D72F.tsv)。

共 139 个文件，495.0 MB。

## 超过 50 MB 的文件

- 没有。

## 按会话

| 会话 | 组 | 文件数 | 大小 |
|---|---|---:|---:|
| `20261030_163420_D72F_h120` | `platform/` | 21 | 69.14 MB |
| `20261030_163420_D72F_h120` | `report/rows.csv` | 1 | 43.46 MB |
| `20261030_164054_D72F_h130` | `platform/` | 17 | 39.09 MB |
| `20261030_164054_D72F_h130` | `report/rows.csv` | 1 | 24.72 MB |
| `20261030_164751_D72F_h80` | `platform/` | 18 | 42.06 MB |
| `20261030_164751_D72F_h80` | `report/rows.csv` | 1 | 26.55 MB |
| `20261030_165250_D72F_h130x` | `platform/` | 17 | 29.15 MB |
| `20261030_165250_D72F_h130x` | `report/rows.csv` | 1 | 18.63 MB |
| `20261030_165952_D72F_h120x` | `platform/` | 18 | 42.83 MB |
| `20261030_165952_D72F_h120x` | `report/rows.csv` | 1 | 27.00 MB |
| `20261030_170559_D72F_h100` | `platform/` | 17 | 37.36 MB |
| `20261030_170559_D72F_h100` | `report/rows.csv` | 1 | 23.73 MB |
| `20261030_171203_D72F_h80x` | `platform/` | 17 | 36.98 MB |
| `20261030_171203_D72F_h80x` | `report/rows.csv` | 1 | 23.54 MB |
| `frida` | `probe CSV` | 7 | 10.75 MB |
