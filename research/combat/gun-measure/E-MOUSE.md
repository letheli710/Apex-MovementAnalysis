# 真实鼠标和按键的三项补测（A 批）

会话 `r5gap-a`，2026-11-13。本地 R5Flowstate（S21 客户端 + S3 dedi + SDK 混合构建），火力训练场，离线，1600×900 窗口，约 140 fps（Frida 挂着）。用户让出了鼠标和窗口焦点，游戏实际跑了约 12 分钟。

## 先说结论

1. **鼠标往下压会吃掉后坐。** 开枪时 punch 把准星往上顶，这时往下拉鼠标，输入先一比一地减 punch，punch 减到 0 以后剩下的才进瞄准角，不会越过 0。往上拉（和 punch 同向）则全部进瞄准角。实际效果：压枪压掉的那部分后坐不会在停火后再弹回来，画面也不会被弹簧拉到比起点更低的地方。反编译看到的 `0x140a33ff0` 是对的。
2. **开镜过程中灵敏度一帧一帧跟着 FOV 走，关镜那一下直接跳回 ×1。** 开镜时每帧乘 `tan(FOV/2) / tan(89°/2)`（用上一帧的 FOV）；松开开镜的下一帧（约 7 ms）就是 ×1，这时画面 FOV 还几乎是开镜值。开镜开到一半松开也一样。
3. **Hop-up / 射击模式切换是 B 键（`+scriptCommand3`），可变倍率的第二档本地切不出来。** B 在 R-301、Hemlok 上切单发，在 Prowler（带 Selectfire）上切全自动；开镜时按 B 会先退出开镜做一个切换动作，再回到开镜。用脚本发 `+scriptCommand3` 不要焦点也能切。可变倍率瞄具按 B、X、滚轮、右键，FOV 都不变。

这三条都是 [实测]。第 1、2 条只涉及客户端，推断正版相同；第 3 条可变倍率那半是"本地测不了"，不是"R5 没有"。

## 1. 鼠标下压和 punch（A1）

### 1.1 方法

- 输入：Python `SendInput` 发相对鼠标移动（`MOUSEEVENTF_MOVE`），125 Hz 均匀发，`r5apex_dx12` 在前台（每步检查，没有丢过焦点）。开火、开镜用客户端 `ClientCommand("+attack")` / `+zoom`，和 RECOIL-VIEW 一样。
- 换算：先不开枪各拉一次，40 count 俯仰 4.40°，99 count 偏航 10.89°，即 **0.11°/count**（`mouse_sensitivity 5` × 0.022）。往下拉是俯仰变大，punch 往上是负。
- 记录：`e-mouse/frida_emouse.js`（从 `frida_recoil.js` 删减），每帧记画面角、瞄准角（进 `0x1407f3f90` 的眼睛角）、punch2（玩家 `+0x2448` / `+0x2454`）、zf、FOV。时间用同一个系统时钟和鼠标记录对齐。
- 枪：R-301，满匣 21 发，没有目标，每次运行前把视角归零。

| 运行 | 做什么 | 次数 |
|---|---|---|
| fire | 腰射按住 1 s，不动鼠标 | 3 |
| pull | 不开枪，下拉 30 count/s（3.3°/s）1 s | 3 |
| firepull | 腰射按住 1 s，同时下拉 30 count/s | 3 |
| fireafter | 腰射按住 1 s，松开后下拉 0.6 s | 3 |
| fireup | 腰射按住 1 s，同时上拉 30 count/s | 3 |
| adsfire / adsfirepull | 开镜后同上 | 各 3 |

### 1.2 结果

全部在 `e-mouse/A1-RUNS.tsv`，逐帧在 `A1-FRAMES.tsv`。

| 运行 | 鼠标输入 | 瞄准角最后动了多少 | 被吃掉 | 射击中瞄准角动了 | 停火时 punch |
|---|---|---|---|---|---|
| fire ×3 | 0 | 0 | 0 | 0 | −3.81 ~ −4.60° |
| pull ×3 | +3.30° | +3.30° | 0 | — | — |
| firepull ×3 | +4.29 ~ +8.14° | 0 ~ +2.48° | 4.23 ~ 5.66° | 0 ~ 0.06°（第 1 次见下） | −0.05 ~ 0.0° |
| fireafter ×3 | +1.98°（其中射击中 0.11°） | +0.09 ~ +0.44° | 1.54 ~ 1.89° | 0 | −3.0 ~ −4.1° |
| fireup ×3 | −3.96 ~ −4.07° | 等于输入 | 0 | −3.85 ~ −3.96° | −1.6 ~ −2.2° |
| adsfire ×3 | 0 | 0 | 0 | 0 | −4.27 ~ −4.52° |
| adsfirepull ×3 | +3.96 ~ +5.17° | 0 | 全部 | 0 | −0.42 ~ −0.87° |

逐帧看停火后下拉（`fireafter_1`，1.55–2.15 s）：每来 1 count，punch 多回 0.11°，瞄准角不动；punch 到 −0.004° 那一帧以后，后面的 4 count 一个一个进了瞄准角（0.44°）。punch 没有越过 0。

firepull 第 1 次：射击中瞄准角动了 2.48°，是因为这一次按住了 2.4 s（见"局限"），匣打空（21 发）后 punch 回到 0，剩下的输入才进了瞄准角。射击中 punch 不为 0 的那段，瞄准角一直是 0。

### 1.3 怎么理解

- 子弹 = 瞄准 + 完整 punch2，所以鼠标对**子弹**的作用一直是一比一，只是记账的地方不同：抵消期间记在 punch 上，抵消完记在瞄准角上。
- 画面 = 瞄准 + (1 − fraction) × punch2。腰射 R-301 fraction 约 0.05（画面 punch / punch2 = 0.95），所以抵消期间画面随鼠标走 0.95 倍；开镜 fraction 0，画面一比一。
- 差别在**停火之后**：不压枪时 punch 由弹簧拉回 0，画面回到起点；压枪时压掉的 punch 不会再回来。停火后接着下拉，前面那段只是在帮弹簧"回家"，画面最后只比起点低 0.09–0.44°，而不是低 1.98°。玩家的感觉是：压枪不会压过头。
- 同向（上拉）完全不抵消，所以这条规则只帮"反着后坐方向"的输入。横向没有单独测，`0x140a33ff0` 看起来按轴各算一次（[反编译]，没测横向）。

对 Unity：`ViewKick.cs` 如果按 R5 做，鼠标输入要先和 punch 反向抵消，再写瞄准角；现在 Unity 是直接写瞄准角。这里不改 Unity。

## 2. 开镜中和关镜那一下的灵敏度（A2）

### 2.1 方法

鼠标匀速右转 400 count/s（腰射 44°/s），转的途中 `+zoom` 按 1.2 s 再松开。R-301 机瞄 3 次、R-301 + 3x HCOG（`optic_ranged_hcog`）2 次、开镜 0.12 s 就松开 2 次、不开镜 1 次。每帧算瞄准偏航的增量：×1 时每帧正好是 3 或 4 count × 0.11°，缩放时是 count × 倍率，所以一帧就能读出倍率。

### 2.2 结果

逐帧在 `e-mouse/A2-QUANTA.tsv`（按键前 60 ms 到后 250 ms），60 ms 窗口平滑后的在 `A2-FRAMES.tsv` / `A2-RUNS.tsv`。

| 项 | 实测 | 预测（tan 比） |
|---|---|---|
| 不开镜 | 0.992–1.009 | 1 |
| R-301 机瞄到位（FOV 69.85） | 0.711（每帧 2.132 count / 3） | 0.7106 |
| 3x HCOG 到位（FOV 33.37） | 0.305（每帧 0.915 / 3） | 0.3050 |
| 开镜过程中逐帧 | 207 帧，和"上一帧 FOV 的 tan 比"中位误差 0 | |
| 关镜后第一帧（6.4–7.4 ms） | **×1.000**（每帧 3.000 count），这时 zf 0.968–0.975，FOV 还是 69.9 / 33.37 | 按 FOV 应是 0.711 / 0.305 |
| 开镜一半松开（zf 0.56–0.59） | 下一帧 ×1.000 | 按 FOV 应是 0.82 |

开镜开始后头几帧倍率还是 1，因为 FOV 的 smoothstep 在 `ads_fov_zoomfrac_start` 之前不动；倍率跟的是 FOV，不是 zf。

### 2.3 怎么理解

开镜：灵敏度跟着画面一起慢慢变低，所以开镜途中转的视觉速度（屏幕上）基本不变。关镜：一松手灵敏度就恢复，画面 FOV 要 0.15–0.55 s 才回到腰射，这段时间屏幕上的视觉转速比平时快（R-301 约 1.4 倍，3x 约 3.3 倍）。这和 ADS-CURVES §4.4 的反编译读法一致（"只在按住开镜时生效，松开直接回 ×1"），那里标的"不确定"现在可以去掉。

## 3. Hop-up 切换键和可变倍率（A3）

### 3.1 方法

本地默认键位（`cfg/config_default_pc.cfg`，用户 `settings.cfg` 相同）：B = `+scriptCommand3`（Cycle fire-mode），X = `+use_alt`，滚轮 = `+weaponcycle`，右键 = `+toggle_zoom`。用 `SendInput` 发真实按键扫描码，前后用服务端读 `GetMods()`，Frida 记 zf 和 FOV。

### 3.2 结果

`e-mouse/A3-EVENTS.tsv`（每次按键前后），`A3-BURSTS.tsv`（每次按住 0.6 s 打出几发）。

| 枪 | 按 B 以后 | 0.6 s 按住打出 |
|---|---|---|
| R-301 | 加上 `altfire`；再按去掉 | 9 → 1 → 7 发 |
| Hemlok | 加上 `altfire` | 3（一组点射）→ 1 → 3 |
| Prowler + `hopup_selectfire` | 加上 `altfire_selectfire` | 点射 → 全自动（发数见局限） |
| 脚本 `ClientCommand("+scriptCommand3")`，R-301 | 同样加上 `altfire` | 9 → 1 |

- 开镜时按 B：zf 1 → 0、FOV 回 89，画面有一个约 +1.1° / −0.29°（俯仰）的切换动作，约 0.7 s 后仍按着开镜就重新开镜。腰射按 B 也有同样大小的动作。
- 客户端脚本 `cl_gamemode_survival.nut` `ToggleFireSelect` 就是 B 的处理：先看 Shatter，再看配件切换表，再切 `altfire`（有 `hopup_selectfire` 时不切），再是 CAR、Firestar、double link、双持。以前试的 `use_alt`、`weaponcycle` 不是这个命令，所以没反应。

可变倍率：

| 枪 + 瞄具 | 开镜 FOV | B | X | 滚轮上 / 下 | 右键（按住开镜时 / 右键开镜时） |
|---|---|---|---|---|---|
| R-301 + `optic_cq_holosight_variable` | 76.2 | 切 altfire 并退出开镜 | 不变 | 不变 | — |
| R-301 + `optic_ranged_aog_variable` | 49.01 | 同上 | 不变 | 不变 | — |
| Longbow + aog_variable | 49.01 | 不变 | 不变 | — | 不变 / 右键再按是关镜 |
| G7 Scout + aog_variable | 49.01 | 不变 | 不变 | — | — |
| Wingman + holosight_variable | 76.2 | 不变 | 不变 | — | — |

武器文件里有第二档（R-301 aog_variable：`zoom_toggle_fov` 19.86，`zoom_toggle_lerp_time` 0.15），引擎字符串里有 `m_zoomToggleOnStartTime`、`zoomToggleFrac`，但这些键都没把它触发。客户端脚本里也没找到注册给可变倍率的按键回调。**本地测不了**，原因是找不到触发它的命令；不能说明 R5 正版没有。

## 4. 局限

- **混合构建**：同 RECOIL-VIEW。A1、A2 只在客户端，推断和正版相同。
- **A1 按住时长不齐**：第一批运行里鼠标线程忙等，抢了 Python 的锁，`firepull_1` 按住了 2.44 s（打空），`firepull_2/3`、`fireup`、`adsfirepull` 是 1.2–1.5 s；`fire`、`fireafter`、`adsfire` 是 1.02 s。所以"停火时 punch"在有拉和没拉之间不是严格同条件；"射击中 punch 不为 0 时瞄准角不动"这条不受影响。A2 前已改成 `sleep`。
- **横向**没有测：只拉了俯仰。
- **A3 发数**是按服务端弹匣日志按顺序配对的，Prowler 第 3 次按住时匣快空了（20 发打到 0），那一格不能用。
- **只测了 sensitivity 5、`m_acceleration 0`**，也没有测 `mouse_use_per_scope_sensitivity_scalars` 打开的情况（本地是 0）。
- 鼠标输入是 `SendInput` 注入的，不是物理鼠标。游戏照单全收（标定误差 0），但物理鼠标的抖动、采样率没有测。

## 5. 文件

公开仓库（本分支 `r5gap/gun`）`research/combat/gun-measure/e-mouse/`：

| 文件 | 内容 |
|---|---|
| `frida_emouse.js` | 只读 Frida 探针，每帧一行（`OUT_DIR_HERE` 运行前替换） |
| `emouse_run.py` | 给枪 + 真实鼠标 / 按键 + 客户端命令的运行器；记录写到 marks 和 `runs/` |
| `analyze_a1.py` → `A1-RUNS.tsv`、`A1-FRAMES.tsv` | 下压和 punch |
| `analyze_a2.py` → `A2-RUNS.tsv`、`A2-FRAMES.tsv`；`analyze_a2q.py` → `A2-QUANTA.tsv` | 灵敏度 |
| `analyze_a3.py` → `A3-EVENTS.tsv`、`A3-BURSTS.tsv` | 按键切换 |
| `slice.py` | 按运行切 Frida 帧，看用 |

原始数据在私有仓库 `HSD-RawData` 的 `apex/research/combat/gun-measure/e-mouse/`：`frida/frames.csv`（全部帧）、`marks.tsv`（按键和每次鼠标发送的时间）、`runs/`（42 次运行的服务端日志）。复算：`py -3 -I analyze_a1.py <frames.csv> <marks.tsv> .`，A2、A3 同理（A3 还要 `runs/` 目录）。

已补进 `research/DESIGN-PHILOSOPHY.md`：P1、T1、T3、§6.4、§9.5、§10.2 第 1、7 条、§11、§12。共享日志：`2026-11-13-r5gap-a-mouse-punch`、`-ads-sens`、`-hopup-key`。
