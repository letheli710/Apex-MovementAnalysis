# N6：钩爪，TF2 和 Apex 有什么区别

2026-10-29。用户验收夜间报告时决定"相当值得研究：机制和数值和 Apex 有什么区别"。

依据：
- **TF2**：夜间实测 [N2-GRAPPLE-BOOST.md](N2-GRAPPLE-BOOST.md) 第 1 节（`runtime/data/20261029_025647_night_grapple3`），设置值 `static-values/setfile-values.csv`、ConVar `static-values/convar-values.csv`。
- **Apex**：
  - Pathfinder 职业设置（`pilot_survival_grapple`，census `Apex-MovementAnalysis/research/phase2-local/data/20261023_203953_N4A_classvars_pathfinder`）；
  - M10 实测 `research/phase2-local/m10/r_grapple/GRAPPLE-M10.md`；
  - 原生脱钩 `research/rea-native/gn/GN-GRAPPLE-NATIVE.md`（GN 分支）；
  - 技能脚本表 `m10/d_library/TECHNIQUE-LIBRARY-M10.md` §3.21。
- **新读的 Apex ConVar 默认值**：今天用 Ghidra 读 `r5apex.exe`（sha256 3f44bf9a…），读法同 `rea-native/convar-defaults`，共 52 个 `grapple_*`。之前的 census 只读到职业设置，这些 ConVar 都没读到。

标注：**[meas]** 实测，**[src]** 设置 / ConVar / 脚本，**[inf]** 推断。

## 1. 一句话

拉动的核心是同一套代码：速度爬升 50 → 800 / 1.5 s、侧向减速 425、0.2 s 开拉延迟、方向键 650 / 420、重力系数、所有脱钩规则，两边数值都一样。区别在**出手和挂上那一下**，以及**次数**：

| | TF2 | Apex |
|---|---|---|
| 出手 | 钩子快（3000 u/s）、射得远（1100） | 慢（2000 u/s）、近（850） |
| 挂上瞬间 | 不弹，下坠速度留 40 %；地面发射也不清水平速度（第 2.7 节实测） | **固定弹起 200**，地面发射时**清掉水平速度** |
| 拉起的初速 | 约 75，从低处爬 | 明显更高（d400 0.73 s 就到 612），同样距离到墙 TF2 反而慢 0.3–0.4 s（第 2.7 节） |
| 接近钩点脱钩 | **总速度削到约 458，再给向上约 +190**（地面拉实测 10 次） | 保速，不弹（Apex 的撞上上抬被丢掉，G-6） |
| 拉力加速 | 1000 | 1500（但被爬升上限卡住，大多数时候看不出来） |
| 次数 | 一条能量拉两次，约 12 s 回一次 | 一次，冷却 10–30 s（按飞行距离算） |
| Apex 新增 | — | 第二次按技能键脱钩并限速 460、钩住时的镜头侧倾、摆荡系统（Pathfinder 关着）、钩住后自动翻越 |

手感上：**TF2 是"连续、快出手"的机动工具，但每次拉到头会被减速并向上送一下；Apex 是"一次性、先弹一下、拉得更快、到头保速、按距离罚冷却"的位移技能**。拉动规则相同，但同样几何下 Apex 起步更快，到墙更早。

## 2. 数值对照

### 2.1 出手和射程

| 项 | TF2 | Apex | 依据 |
|---|---|---|---|
| 钩子飞行速度 `grapple_shootVel` | 3000 | **2000** | [src] 两边 ConVar；[meas] TF2 660 u 用 0.224 s；Apex 261 / 410 / 713 u 用 0.125 / 0.200 / 0.350 s，正好是 ÷ 2000 |
| 射程 | 1100（水平、竖直） | **850**（`grapple_maxLength` / `Vert`，约 21.6 m） | [src] |
| 开拉延迟 `pullDelay_human` | 0.2 s | 0.2 s | [src]；[meas] 两边都吻合 |
| 发射到开拉（660 u） | **0.42 s** | **0.53 s**（按公式） | 距离 ÷ 速度 + 0.2 |
| 失误宽限 `gracePeriod`（钩空不扣次数） | 0.25 s | 0.25 s（ConVar 在；Apex 冷却由脚本扣，是否生效未查） | [src] |
| 自动瞄准角 | 无此键 | `grapple_autoAimAngle` 10° | [src] Apex 新增 |

### 2.2 挂上的瞬间

| 项 | TF2 | Apex | 依据 |
|---|---|---|---|
| 竖直 | 下坠速度留 40 %（`initialSlowFracVert_human` 0.4）：−292 → −108，−688 → −221 | **vz 固定变成约 200**（`grapple_attachVerticalBoost` 200）：不论地面、空中、冲刺、滑铲，挂上后都是 193.7（= 200 − 一帧重力） | [meas] 两边；Apex 的 0.4 ConVar 仍在，但被这一下盖掉 [inf] |
| 水平 | 侧速大部分保留（400 → 358，700 → 558）（`initialSlowFrac_human` 1）；**地面发射也保留**：按住冲刺发射，钩子飞行中一直 260（第 2.7 节） | **空中保留，地面发射时清零**：冲刺 297 → 0，滑铲 421 → 362（滑铲还在滑） | [meas] 两边 |
| 朝钩点的初速 | `initialImpulse_human` 350；实测只看到约 60–70 | 同一个 ConVar 350；被 200 弹起和清速盖掉，看不出 | [src] 两边相同；[meas] TF2 |
| 离地冲量 `initialImpulseOffGround_human` | 50 | 50 | [src] |

**这是两边手感差最大的地方。** Apex 每次挂上都"先弹一下"，所以钩爪也能当小跳用（grapple hop：往脚下钩，弹 200 再叠一次跳，最高 146–155 u），也就有了 Jump Grapple 这类技巧。TF2 挂上时保留原来的运动，没有这一下。

### 2.3 拉动中

| 项 | TF2 | Apex | 依据 |
|---|---|---|---|
| 速度爬升 | 50 → 800，1.5 s（每秒 +500） | 同（职业设置 `speedRampMin/Max/Time` 50 / 800 / 1.5） | [src]；[meas] Apex d\|v\|/dt 500.0–502.7；TF2 每秒约 +500–600（含重力和侧速） |
| 拉力加速度 | `grapple_accel_human` **1000** | 职业设置 `grapple_accel` **1500**（ConVar 仍是 1000，被职业设置覆盖） | [src]。速度被爬升上限卡住时，加速度只决定"多快贴到上限"，两边差别小 [inf] |
| 侧向减速（不朝钩点的速度） | 425 | 425 | [src]；[meas] Apex 423 |
| 方向键空中加速 / 上限 | 650 / 420 | 650 / 420（× 移动速度倍率，实测 483） | [src] 两边相同 |
| 重力系数 | 0.25 – 0.7 | 0.25 – 0.7 | [src] |
| 不和重力对抗 / 朝下拉时重力帮忙 | `dontFightGravity` 1、`letGravityHelpCosAngle` 0.8 | 同 | [src]；Apex 的 Jump Grapple 出口 1000–1030 就靠这条 |
| 看向钩点下方时加重力 | `gravityPushUnderContribution` 2 | 2 | [src] |
| 绕障碍加速 | 1000 | 1000 | [src] |
| **按后退** | 明显**减速**：空中 1 s 时 424（不按 695）；**同几何**（平地拉墙 400 u）到墙 523（不按 648），爬升从每秒 500 降到约 340 | 反而**加速**：740（不按 612） | [meas]。同几何确认两边方向相反；设置相同，原因没查清 [inf] |
| 按前进 | 水平速度被卡在 **420** 一段（`airSpeedMax`），提前到墙（0.88 s 对 1.11 s），到墙 531 | 同一条卡速：483（= 420 × 移动速度倍率 1.15） | [meas] 两边，同一规则 |
| 按侧移 / 甩人 | 空中带侧速：1 s 时 711 / 930（起始侧速 400 / 700）。**同几何**：平拉按 D 最高 673（不按 648，+4 %）；转 45° 按 D 795（不按 778，+2 %），按 A 623 | 平拉按 D 784（不按 612，+28 %）；45–50° 按 A / D 938–945（不按 796，+18 %）；Slingshot 854 / 911 | [meas]。规则相同（侧向加速 650 对侧向减速 425），但 **TF2 从方向键得到的额外速度小得多**；原因没查清（Apex 拉力 1500、移动速度倍率 1.15 可能有关）[inf] |
| 摆荡 | 没有这些键 | `grapple_swing*` 一整套（加速 2000、上限 1000、最短绳长 150……），**Pathfinder 关着**（`grapple_swing false`） | [src] Apex 新增但没用 |

### 2.4 脱钩

| 项 | TF2 | Apex | 依据 |
|---|---|---|---|
| 太近脱钩 `detachLengthMin / Max` | 33 / 50 | 33 / 50 | [src] |
| 远离脱钩 `detachAwaySpeed` | 500 | 500（Apex 只在钩世界几何时开，GN） | [src] |
| 低速脱钩 | 250 u/s 下：空中 1.5 s、墙上 1.2 s、地面 0.7 s | 同（Apex 拉动中实际一律 1.5 s，GN #7） | [src] |
| 撞上上抬 `impactVerticalBoost / MaxSpeed` | 300 / 300；**实测生效**：空中拉到墙时 vz 抬到约 288（= 300 减一帧重力） | 300 / 300；R5 客户端做、录像里没有，HSD 默认关（G-6，D-52） | [src] + [meas] TF2（`night_grapple3` 的 c_still / c_toward500 / c_rise300） |
| 地面拉到头的脱钩 | 离墙约 33 u 时脱钩：总速度削到约 458（`detachSpeedLossMin` 460），vz 变成约 +190–220；更快时（782–859）少 250–300（`detachSpeedLoss` 300） | 接近脱钩保速、不弹（M10：只有第二次按键才限速 460） | [meas] TF2 10 次（第 2.7 节）；Apex M10 |
| 越过钩点上抬 `detachVerticalBoost / MaxSpeed` | 200 / 200 | 200 / 200 | [src] |
| 脱钩减速 `detachSpeedLoss / Min` | 300 / 460 | 300 / 460 | [src] |
| 绳子过长 `detachExtraAllowedLength` | 没读到（TF2 ConVar 表里没有） | 256 | [src] |
| 起跳 | 立即脱钩，普通跳（vz 296）；`jumpFrac` 1 | 挂上弹起后 0.15 s 内再跳会叠加普通跳（+280）；`jumpFrac` 1 | [meas] 两边 |
| 第二次按技能键 | 没有这个键 | **脱钩**，快于 460 时限到 460（`detachOnGrapple` true，0.5 s 防抖） | [src] + [meas] Apex |
| 按蹲 | 未测 | 脱钩 | [meas] Apex |
| 视线离开钩点 | 未测 | 客户端规则约 100°（本地 dedi 不做，混合版本） | [meas] Apex |
| 钩住敌人 | 脱钩时自动近战、视角转向目标（`autoMeleeOnDetach` 1） | ConVar 一样在，Pathfinder 实际不用（HSD 没有目标） | [src] |
| 脱钩后 | — | `detachHorizontalMaxSpeed` 600、`detachGravityScale / Speed / Time` 0.5 / 200 / 0（Time 0 = 不生效） | [src] Apex 新增 |

### 2.5 次数和冷却

| 项 | TF2 | Apex |
|---|---|---|
| 资源 | 玩家身上的钩爪能量：每条 100，一次 50，**能连拉两次** | 武器弹匣 300，**一次用完**（`grapple_power_required` 100） |
| 回复 | 3 s 后开始，约 4.05 / s（满条约 25 s，每次约 12 s） [meas] | 10 / s；扣量 = 100 + 按距离最多再 300 → **冷却 10–30 s**（飞得越远越久；拉完后速度 > 500 的飞行也算） [src] |
| 后来的版本 | — | 2026-06 起改成两次、固定 20 s（S21 之后，HSD 不用） |

TF2 的设计让钩爪成了随时能用的移动手段；Apex 按距离罚冷却，把它限制成"偶尔一次的大位移"。

### 2.6 Apex 新增、TF2 没有的

| 项 | 值 | HSD 现状 |
|---|---|---|
| 挂上弹起 `attachVerticalBoost` | 200 | 已有（Reference） |
| 第二次按键脱钩 + 限速 460 | 0.5 s 防抖 | 已有 |
| 钩住时镜头侧倾 `grapple_roll*` | 最大 20°，距离 0–150，视角 0–65° | 已有（F-1，12.8°） |
| 摆荡系统 `grapple_swing*` | Pathfinder 关 | 不做 |
| 自动翻越 `grapple_autoMantle` | 0.25（ConVar） | 没查 |
| 绳子上抬 `grapple_lift` | 25 | 已有（GN G-3） |
| 拉完滑索冷却 `lastZiplineCooldown` | 0.5 s | — |

另外，Apex 还保留着 `grapple_windowCheckDist` 150（钩到窗户附近时送你穿过去），但 TF2 的 `window_hint_*` 那一组 ConVar 在 R5 里没有了。这条代码在 Apex 里是不是还生效，没查 [inf]。

### 2.7 同几何补测（2026-10-29 上午）

运行 `runtime/data/20261029_092610_night_grapple_match`（`plans_night.night_grapple_match`，144 fps，本地私服，结束后锁已释放）。仿照 Apex M10 的 A 道：站在地上，平视钩西墙（墙面 x = −962），距离 250 / 400 / 700 u；另有仰 20°、按住 W / S / A / D、转 45°（甩人）、冲刺 / 滑铲中发射。分析：`runtime/night_match.py`（每次一行）、`runtime/night_release.py`（脱钩那一帧）。

- **两条道只用 y −950。** y −850 那条有道具挡路（笔刷检测看不到道具），多数试次没拉到墙，全部不用。y −950 的 `d400_a` 是按 A 的试次（命名和第一次重复，计划已改名），中途撞到道具，也不用。
- 同一距离的 Apex 数字来自 M10（`m10/r_grapple/analysis_output.txt`，Pathfinder，120 fps）。Apex 的"脱钩速度"是松开那一刻；TF2 用脱钩前一帧。

| 试次 | TF2 发射 → 开拉 | TF2 发射 → 脱钩 | TF2 脱钩前速度 | Apex 发射 → 脱钩 | Apex 脱钩速度 |
|---|---|---|---|---|---|
| 250 u | 0.281 s | 1.11 s | 512 | 0.85 s | 473 |
| 400 u | 0.346 s | 1.46 s | 648 | 1.125 s | 612 |
| 700 u | 0.448 s | 1.98 s | 859 | 1.55 s | 804 |
| 400 u 仰 20° | 0.347 s | — | 620（最高） | 1.175 s | 635 |

- **开拉时刻**完全符合"距离 ÷ 3000 + 0.2 s"。
- **起步**：TF2 开拉时离地 vz ≈ 50（`initialImpulseOffGround` 50），水平速度从约 75 起，每秒 +500 爬升。Apex 挂上就弹 200，开拉后 0.73 s 已到 612，起步明显更高（`initialImpulse` 350 在 Apex 里看来生效了，在 TF2 里只看到约 75）[inf]。所以**钩子快 1.5 倍的 TF2，到墙反而慢 0.26–0.43 s**，到墙时速度高 36–55。
- **地面发射**：按住冲刺时发射，钩子飞行中水平速度一直 260，挂上后接着拉，**TF2 不清水平速度**。发射时松开按键，0.2 s 内停下，那是普通地面减速。滑铲 353 → 333 是滑铲本身的减速。
- **脱钩**（新发现）：地面拉到离墙约 33 u（`detachLengthMin` 33）时脱钩，同一帧**总速度削到约 458，vz 变成 +190–220**：
  - 400 u：648 → 水平 417 + vz 189；
  - 250 u：512 → 403 + 218；
  - 按 W、按 S、滑铲：都到约 458；
  - 冲刺（782）、700 u（859）：少 250–300。

  这就是 `detachSpeedLoss` 300 / `Min` 460 加上竖直上抬，在 TF2 里拉到头的接近脱钩上生效。Apex（M10）的接近脱钩保速，只有第二次按技能键才限速 460。空中拉到墙时 vz 被抬到约 288，是撞上上抬 `impactVerticalBoost`。
- **按后退 / 前进 / 侧移**：见第 2.3 节。后退在同几何下确实减速；前进被 420 卡住；侧移只多 2–4 %，Apex 多 18–28 %。

**和 G-6 的关系**：TF2 本地私服的客户端和服务端是同一个程序，没有 R5 那种混合版本问题。这里撞上上抬确实生效，可以作为"原版设计里这一下是存在的"证据。但 R5 本身丢掉了它，HSD 现在的 D-52（默认关、可开）不用改。

## 3. 对 HSD 的意义

1. **HSD 现在的钩爪就是 Apex 原生规则**（M10 + GN），不用因为 TF2 改。
2. 如果以后想要"TF2 手感的钩爪"预设，只需要换出手、挂上、次数三处，拉动和脱钩可以原样复用：

   | 键 | 改成 |
   |---|---|
   | 钩子速度 / 射程 | 3000 / 1100 |
   | 挂上弹起 | 关；竖直留 40 % |
   | 地面发射 | 不清水平速度（已实测） |
   | 拉力 / 起步 | 1000；起步约 75（不用 350 的初速） |
   | 接近脱钩 | 总速度削到 460（快时减 300），竖直上抬约 200 |
   | 方向键加速 | 侧移得到的额外速度只有 Apex 的零头（原因没查清，先按实测调） |
   | 次数 | 两次，每次约 12 s |
   | 第二次按键脱钩 | 关 |

   这只是数值和三个开关，工作量小。要不要做由你决定；我的看法是现在不急，等钩爪关卡需要更"连续"的手感时再说。
3. **同几何补测已做**（第 2.7 节）。还没解释的：
   - 为什么按后退在 TF2 减速、在 Apex 加速；
   - 为什么 TF2 侧移加速小得多；
   - TF2 起步初速为什么只有约 75。

   三项都要读两边的拉动函数（TF2 `server.dll` `0x18016fa80`，R5 `0x1406755c0`）才能定。只影响"TF2 预设"，不影响 HSD 现在的 Reference。

## 4. 方法

- Apex ConVar 默认值：Ghidra headless，`ghidra-projects/r5apex.gpr`，脚本 `Apex-MovementAnalysis/research/rea-native/convar-defaults/ghidra/DumpConVarRegistrations.java`；名单是 `rea-native/local/n1-raw/convars.tsv` 里出现的 52 个 `grapple_*`。`grapple_disable`、`grapple_max_len` 没解析出默认值（不影响上表）。原始输出在本机，不进版本库（含反编译代码）。
- Apex 飞行时间来自 `m10/r_grapple/analysis_output.txt` 的 `att_s` 列。
- TF2 数据和分析脚本见 N2 第 1 节。
