# 07 镜头的附件

| 文件 | 内容 | 怎么来的 |
|---|---|---|
| `punch-response.tsv` | punch 弹簧（k 65、c 9，精确解，dt 1/120 s）的单位冲量响应：第一组冲量 1 °/s、第二组 0.2 °/s，逐命令的画面俯仰。乘事件的俯仰冲量就是画面曲线（07 §1.1、§2.3） | `py -3 -I gen_spring_tables.py <本目录>` |
| `landing-kick.tsv` | 落地强度 s、俯仰冲量、r = −0.5 / 0 / +0.5 的画面俯仰峰值、横滚峰值上限，12 个下落速度（07 §2.3） | 同上 |
| `traversal-curves.tsv` | 翻越镜头的俯仰偏移曲线：8 个类别 × (时间进度 → 动画进度，动画进度 → 俯仰)，每 0.05 一个点（07 §2.5） | `py -3 -I gen_traversal_curves.py <HSD-Unity>/Assets/HSD/R5Replay/Runtime/MantleBoostS27.cs <本目录>`（从 HSD-Unity main 17260f2 的表抄出，B1 的 R5 实测平均） |

单位：角度 °、时间 s、速度 u/s（`landing-kick.tsv` 另有 m/s 列）。符号：俯仰 + = 向下（Source）。
