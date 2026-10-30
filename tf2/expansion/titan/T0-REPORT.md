# 泰坦 T0：召唤、驾驶、转向、底盘移动

2026-10-30。本地 Northstar 私服 `mp_lf_stacks`，所有实测都通过 `runtime/runner.py` 跑，144 fps。7 台泰坦逐台实测，结果按泰坦给，不只按底盘。每台的武器和技能见 [titans/](titans/README.md)。

只借规则和数值，不用 TF2 的模型、声音、动画。

## 0. 结论先说

| 问题 | 答案 |
|---|---|
| 能不能召唤、驾驶 | 能。7 台都在本地私服召唤、上机、下机成功（第 1 节） |
| 泰坦转得比铁驭慢吗 | **鼠标和键盘：不慢。** 同样的输入，7 台泰坦和铁驭转的角度完全一样：真实鼠标 2000 计数都是 144.78°，键盘实测到 1500°/s。没有上限、没有平滑、没有加速曲线。**手柄：慢 25 %。** 泰坦有单独的手柄视角表，最大转速是铁驭的 0.75 倍，加速时间更长（第 2 节） |
| "机械感"从哪来 | 不是转速上限。来源有三个：手柄转速表、个别技能临时减速转向（`turn_slow`，例如 Ion 激光核心），以及镜头和视角弹簧（第 2.4 节） |
| 底盘移动 | 全部和设置文件一致。走 270 / 250 / 210，冲刺 400 / 380 / 310，冲刺（dash）800 / 700 / 600，次数 2 / 1 / 1（第 3 节） |

## 1. 召唤、上机、下机

### HSD 怎么做

- 泰坦当成一个可以进入的载具。上机有两种：动画上机（约 3.5 s）和瞬间上机。下机约 1.0–1.4 s，铁驭出现在泰坦上方或旁边。
- 研究工具可以直接用下面的命令，后面所有泰坦实测都靠它们。

### 命令（诊断模组 `hsd_diag_titan.gnut`）

| 命令 | 作用 |
|---|---|
| `hsd_titan <种类> x y z yaw [mods…]` | 召唤一台自动泰坦，归玩家所有。种类：`ion` `scorch` `northstar` `ronin` `tone` `legion` `monarch`，或直接写设置文件名。配置取游戏默认泰坦配置（`GetDefaultTitanLoadouts`），mods 是设置文件 mod，例如 `turbo_titan`（Turbo 引擎） |
| `hsd_embark 0` | 瞬间上机（`ForceScriptedEmbark`，和 Northstar 的 `RespawnAsTitan` 同一做法） |
| `hsd_embark 1` | 正常上机动画（`FindBestEmbark` + `PlayerEmbarksTitan`） |
| `hsd_disembark` | 正常下机（`PlayerDisembarksTitan`，同 `TitanDisembark` 客户端命令） |
| `hsd_titan_info` | 设置文件、mod、冲刺能量、血量、护盾、每个技能的弹药 / 充能 |
| `hsd_dodgepower <0..100>` | 设冲刺能量 |
| `hsd_core` | 核心充满（`SoulTitanCore_SetNextAvailableTime( soul, 1.0 )`） |
| `hsd_status <效果> <强度> <秒> [淡出]` | 给泰坦加状态效果：`turn_slow` `move_slow` `dodge_speed_slow` `speed_boost` |
| `hsd_lanes x0 y0 x1 y1 步长 [长度] [最小空地]` | 用泰坦体型（120 × 235）扫地图，找直线空地 |
| `hsd_mouse <名字> dx dy 次数 间隔ms` | 只做标记；runner 加 `--mouse` 时由 [titan_mouse.py](titan_mouse.py) 发真实鼠标移动 |

日志：`HSDDIAG TITAN …`（事件），`HSDDIAG TT`（服务端每帧：是否泰坦、冲刺能量、冲刺、血、护盾），`HSDDIAG CAM`（客户端每帧镜头角度和镜头相对脚底的偏移）。

### 证据

| 项 | 实测 | 运行 |
|---|---|---|
| 7 台都能召唤 + 瞬间上机 + 下机 | 全部成功，设置文件：Ronin `titan_stryder_leadwall`、Northstar `titan_stryder_sniper`、Ion `titan_atlas_stickybomb`、Tone `titan_atlas_tracker`、Monarch `titan_atlas_vanguard`（自带 `pas_vanguard_shield`）、Scorch `titan_ogre_meteor`、Legion `titan_ogre_minigun` | `20261030_013127_t0_turn` |
| 动画上机 | 距泰坦 200 u 起，3.45 s 后变成泰坦 | `20261030_012858_t0_smoke` |
| 下机 | 1.03–1.42 s；铁驭落点在泰坦上方 120–170 u | 同上和 `t0_turn` |
| 默认配置 | 每台的主武器和 5 个技能槽见 `hsd_titan_info`，和 [TITAN-LIST](../TITAN-LIST.md) 第 2 节一致 | `t0_turn` |

坑：

1. 诊断脚本里任何**客户端**初始化的脚本错误（例如读不存在的 ConVar `m_sensitivity`）会让客户端反复重连（`20261030_012337_t0_smoke`）。服务端编译错误会在主菜单弹窗（用户 2026-10-30 截图），脚本里多余的类型转换和不存在的实体方法都会编译失败。
2. `mp_lf_stacks` 的空地对铁驭够，对泰坦不够：泰坦宽 120，高 235，细射线测出的空地会被道具挡住（`20261030_014323` / `014930_t0_move` 撞停在 y −1340）。用 `hsd_lanes` 找到的直道：(−800, −1400) 朝 +x，约 1360 u（`20261030_015621_t0_lanes`）。
3. 键位（用户 `settings.cfg`）：`+offhand0` 进攻，`+offhand1` 防御，`+offhand2` 战术，`+ability 3`（空格）冲刺，`+ability 1`（V）核心，`+speed`（Shift）冲刺跑。`+dodge` 对泰坦**没有反应**（`t0_smoke` 能量一直 100）。

## 2. 转向速度（主要问题）

### HSD 怎么做

- **鼠标不要给泰坦加转速上限或平滑**，TF2 没有，加了会让玩家觉得"卡手"而不是"重"。
- **手柄给泰坦单独一张视角表**：最大转速 = 铁驭 × 0.75，加速时间更长（铁驭 0.33 s → 泰坦 0.8 s）。这是 TF2 唯一常驻的泰坦转向差异。
- **"机械感"用表现层做**：视角弹簧更硬更慢（重型更明显）、冲刺跑镜头下沉 25 u、走路镜头几乎不晃，以及个别技能临时 `turn_slow`（见 2.3）。
- 如果以后要做"泰坦转得更慢"，用一个按泰坦配置的状态系数缩放**输入**，不要限制角速度——TF2 的 `turn_slow` 就是这样做的（鼠标输入 × 约 (1 − 2 × 强度)，实测见 2.5）。
- ADS 时的鼠标转速按武器放大倍数缩放（`mouse_sensitivity_zoomed` × tan(zoom_fov / 2) ÷ tan(75 / 2)），铁驭和泰坦同一规则。

### 2.1 实测：同样的输入，转速完全一样

输入：键盘转向 `+right` / `+left`，`cl_yawspeed` 210 和 1500，引擎逐帧把同样的角度加到视角上；每台泰坦和铁驭都用同一段实验表（`plans_titan._turn_block`）。

| 角色 | 210°/s 输入：实测 | 1500°/s 输入：实测 | 起步 |
|---|---|---|---|
| 铁驭 | 210.1°/s | 1500.0°/s | 第一帧就满速 |
| Ronin | 210.1 | 1500.0 | 同上 |
| Northstar | 210.1 | 1499.3 | 同上 |
| Ion | 210.3 | 1500.0 | 同上 |
| Tone | 210.1 | 1500.0 | 同上 |
| Monarch | 210.3 | 1500.0 | 同上 |
| Scorch | 210.3 | 1500.7 | 同上 |
| Legion | 210.3 | 1500.7 | 同上 |

运行 `20261030_013127_t0_turn`，`analyze_titan.py` 逐帧算（中位数；1 s 内 144 帧全部在转）。松手当帧停，没有拖尾。结论：引擎和移动代码**没有**按职业限制角速度，也没有平滑。

### 2.2 静态：泰坦唯一常驻的转向差异是手柄表

`client.dll` 按职业加载 `cfg/aimassist/looksensitivity_titan.txt`（铁驭用 `looksensitivity.txt`）。各档（游戏里的"视角灵敏度"0–7）：

| 档 | 铁驭 yaw / pitch (°/s) | 泰坦 yaw / pitch | 比例 | 加速时间 铁驭 → 泰坦 |
|---|---|---|---|---|
| 2（默认） | 160 / 120 | 120 / 90 | 0.75 | 0.33 → 0.8 s |
| 3 | 240 / 200 | 180 / 135 | 0.75 | 0.3 → 0.8 s |
| 4 | 380 / 240 | 285 / 215 | 0.75 / 0.9 | 0 → 0 |
| 5 | 450 / 300 | 340 / 255 | 0.76 / 0.85 | 0 → 0 |
| 6–7 | 500 / 500 | 375 / 375 | 0.75 | 0 → 0 |

另外 `gamepad_custom_pilot` / `gamepad_custom_titan` 两个 ConVar 让自定义手柄设置也分开。

设置文件里**没有**转向上限键。`titan_base.set` 的 `aimAngle*` 是身体动画的瞄准角度范围，`pitchOffsetScale` 是视角模型偏移。`client.dll` / `server.dll` 字符串里也没有按职业的鼠标灵敏度：只有 `mouse_sensitivity`、`mouse_sensitivity_zoomed`（用户值 3.29 / 5，`LOOKCFG` 日志）。

### 2.3 技能和状态造成的临时转向减慢（`turn_slow`）

| 来源 | 强度 | 时长 | 出处 |
|---|---|---|---|
| Ion 激光核心（自己） | 0.25（同时 `move_slow` 0.25） | 核心 3.5 s + 淡出 2 s | `mp_titancore_lasercannon.nut` 12–13、193–194 行 |
| 被电弧 / EMP 打中 | 0.35（`move_slow` 0.5） | 按武器 | `_weapon_utility.nut` 109–110、`GiveEMPStunStatusEffects` |
| 被激光眩晕 | 0.20（`move_slow` 0.3） | 按武器 | `_weapon_utility.nut` 111–112 |
| 电弧球蓄力（`ChargeBall`） | 0.35 | 蓄力期间 | `_weapon_utility.nut` 2589–2590 |
| Amp 核心（未上线核心） | 0.25 | 核心期间 | `mp_titancore_amp_core.nut` 47 |

实测：`hsd_status turn_slow 0.25 2.5` 后键盘转向**仍是 210°/s**（7 台都一样，`t0_turn` 的 `slow_*` 段）。所以 `turn_slow` 不限制角速度，只缩放**鼠标**（很可能还有手柄）输入，键盘转向 `+right` 绕过它。鼠标实测见 2.5：强度 0.25 时鼠标转速减半。

### 2.4 镜头

| 项 | 铁驭 | Stryder | Atlas | Ogre | 出处 |
|---|---|---|---|---|---|
| 视角弹簧（被打 / 开火的视角晃动）刚度 / 阻尼 | 65 / 9 | 35 / 9 | 65 / 15 | 95 / 30 | `weapons/springs.txt` `punch_*`；设置文件 `viewPunchSpring` |
| 眼高 | 60 | 185（蹲 125） | 185 | 185 | 设置文件 `viewheight`；`CAM` 日志 dz |
| 冲刺跑时镜头下沉 | 6 | 25.6 实测（−25） | 25.6 | 25.4 | `sprintViewOffset`；`t0_move` |
| 冲刺跑侧倾 | 2° | 1.76° 实测（设置 4°） | 1.76–1.81°（设置 3°） | 1.76°（设置 2°） | `sprinttiltMaxRoll`；`CAM` 日志 |
| 走路镜头上下晃 | — | 0.42 u | 0.36 u | 0.29 u | `CAM` 日志，`t0_move`（`cockpit_stepJolt_origin` −6 / −5 / −4 作用在驾驶舱模型，不在镜头） |

### 2.5 真实鼠标实测

[titan_mouse.py](titan_mouse.py) 用 `SendInput` 发和真实鼠标一样的移动：每 5 ms 发 10 个计数，共 200 次，即 1 s 内 2000 计数。只在 TF2 窗口在前台时发，用户在跑的时候保持了窗口在前台。`mouse.json` 里 16 + 3 次都是 `ok`，每次都发满 200 次。

**腰射（不瞄准）：所有角色完全一样。**

| 角色 | 2000 计数转了 | 度 / 计数 | 转动持续 |
|---|---|---|---|
| 铁驭 | 144.78° | 0.0724 | 1.002 s |
| Ronin、Northstar、Ion、Tone、Monarch、Scorch、Legion | 144.78–144.79° | 0.0724 | 0.993–1.002 s |

- 0.0724 = 0.022 × `mouse_sensitivity` 3.29（Source 的 `m_yaw` 默认值乘灵敏度），泰坦没有任何额外系数。
- 输入停下当帧就停，没有拖尾、没有平滑；转动时长等于输入时长（输入 0.995 s）。
- 逐帧速率在 105 和 210°/s 之间交替，是 200 Hz 的输入和 144 fps 的帧对不齐造成的，平均 145°/s，和输入一致。
- 运行 `20261030_023156_t0_turn` 的 `ms_*` 段。

**瞄准（ADS）：按武器的放大倍数缩放，铁驭和泰坦用同一条规则。**

| 角色 | 武器 `zoom_fov` | 2000 计数转了 | 相对腰射 |
|---|---|---|---|
| Legion | 75（不放大） | 220.0° | × 1.52 |
| Ronin、Ion | 55 | 149.25° | × 1.03 |
| Northstar、Tone、Monarch、Scorch | 50 | 133.69° | × 0.92 |
| 铁驭（R-201） | — | 99.07° | × 0.68 |

- 规则：ADS 用 `mouse_sensitivity_zoomed`（用户值 5），再乘 tan(zoom_fov / 2) ÷ tan(75 / 2)。5 ÷ 3.29 = 1.52；50° 时 × 0.608、55° 时 × 0.678，和实测一致到 0.1°。
- Legion 转管不放大视角，所以**转管时反而转得更快**；其他泰坦 ADS 时转速和腰射差不多。
- 运行 `20261030_023156_t0_turn` 的 `msads_*` 段。

**`turn_slow` 对鼠标的作用：很大。** 同样 2000 计数，Ion，三种强度：

| `turn_slow` 强度 | 转了 | 相对 |
|---|---|---|
| 0 | 144.78° | × 1.00 |
| 0.25 | 73.24° | × 0.506 |
| 0.5 | 0.57° | × 0.004（几乎转不动） |

- 近似为 × (1 − 2 × 强度)。
- 所以 Ion 激光核心（0.25）期间，鼠标转速大约减半；被 EMP（0.35）打中时只剩约 0.3。
- 键盘转向不受影响（2.3 节）。
- 运行 `20261030_023602_t0_mouseslow`。

## 3. 底盘移动（逐台）

### HSD 怎么做

- 三种底盘一套参数，同底盘的泰坦**移动完全一样**（实测逐台对过）。差别只在冲刺（dash）次数：多人里 Stryder 2 次，Atlas / Ogre 1 次（设置文件按泰坦覆盖了底盘值）。
- 加速分两段：低于 `lowSpeed` 用 `lowAcceleration`（快），之上用 `acceleration`。冲刺跑从走速再以很慢的 `sprintAcceleration` 爬到冲刺速度——这是"重"的主要来源之一。
- 冲刺（dash）：瞬间到 `dodgeSpeed`，保持约 0.2 s，然后按地面摩擦降回走速。

### 3.1 实测表

运行 `20261030_015751_t0_move`（走、冲刺跑、冲刺），后退和侧移来自 `20261030_014930_t0_move` 的 (24, −1450) 段。脚本 [analyze_move.py](analyze_move.py)。

| 泰坦 | 走速 | 0→走速 | 加速 <lowSpeed / >lowSpeed | 松手停 | 后退 / 侧移 | 冲刺跑速 | 走→冲刺跑 | 冲刺跑松手停 | dash 速度 | dash 保持 | dash 后 0.3 s | 每次耗能 | 回能 /s | 次数 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ronin | 270 | 0.19 s | 1600 / 840* | 1770 u/s²，0.15 s | 270 / 270 | 400 | 150 u/s²，1.02 s | 1066 u/s² | 800 | 0.19 s | 620 | 50 | 10.0 | 2 |
| Northstar | 270 | 0.19 | 1601 / 786* | 1770，0.15 | 270 / 270 | 400 | 150，1.02 | 1063 | 800 | 0.20 | 620 | 50 | 10.0 | 2 |
| Ion | 250 | 0.19 | 1500 / 801* | 1498，0.17 | 250 / 250 | 380 | 120，1.26 | 1074 | 700 | 0.20 | 486 | 100 | 16.6 | 1 |
| Tone | 250 | 0.19 | 1501 / 834* | 1500，0.17 | 250 / 250 | 380 | 120，1.24 | 1072 | 700 | 0.20 | 486 | 100 | 16.6 | 1 |
| Monarch | 250 | 0.19 | 1500 / 827* | 1481，0.17 | 250 / 250 | 380 | 120，1.25 | 1063 | 700 | 0.20 | 486 | 100 | 16.6 | 1 |
| Scorch | 210 | 0.24 | 1400 / 351* | 1162，0.18 | 210 / 210 | 310 | 180，0.79 | 892 | 600 | 0.20 | 416 | 100 | 9.9 | 1 |
| Legion | 210 | 0.24 | 1398 / 380* | 1165，0.18 | 210 / 210 | 310 | 180，0.80 | 892 | 600 | 0.20 | 417 | 100 | 9.9 | 1 |
| 铁驭（对照） | 173.5 | — | 2500 | 1500 | — | — | — | — | — | — | — | — | — | — |

\* lowSpeed 以上只剩 40 u/s，帧数少，斜率偏低；按设置文件是 1000 / 900 / 380。

"次数"= 能量满时连按 3 次（间隔 0.7 s）实际冲出几次（`dodgeside_*` 段）。

### 3.2 设置文件（出处）

`scripts/players/mp/titan_stryder.set` / `titan_atlas.set` / `titan_ogre.set`（底盘）和每台泰坦的设置文件（覆盖冲刺能量）。

| 键 | Stryder | Atlas | Ogre |
|---|---|---|---|
| `speed`（站） | 270 | 250 | 210 |
| `acceleration` / `deceleration` | 1000 / 1800 | 900 / 1500 | 380 / 1200 |
| `lowSpeed` / `lowAcceleration` | 230 / 1600 | 200 / 1500 | 160 / 1400 |
| `sprintspeed` / `sprintAcceleration` / `sprintDeceleration` | 400 / 150 / 600 | 380 / 120 / 700 | 310 / 180 / 600 |
| 蹲 `speed` / `acceleration` / `deceleration` | 187 / 250 / 625 | 150 / 200 / 500 | 112 / 150 / 375 |
| `speedScaleSide` / `speedScaleBack` | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 |
| `dodgeSpeed` / `dodgeStopSpeed` | 800 / 450 | 700 / 450 | 600 / 350 |
| `dodgeDuration` / `dodgeInterval` / `dodgePowerDelay` | 0.1 / 0.35 / 0.2 | 0.2 / 0.3 / 0.2 | 0.2 / 0.2 / 0.3 |
| `dodgeHeight` | 5 | 5 | 5 |
| `friction` | 2 | 2 | 2 |
| 多人每次冲刺耗能 / 回能（泰坦设置文件） | Ronin、Northstar：50 / 10 | Ion、Tone、Monarch：100 / 16.66 | Scorch、Legion：100 / 10 |
| Turbo 引擎（`turbo_titan`）/ 冲刺增强（`pas_mobility_dash_capacity`） | 33 / 16.5；33 / 6.6 → 3 次 | 50 / 20.825；50 / 8.33 → 2 次 | 回能 50；回能 20（耗能不变 → 1 次，回得快） |
| `sprinttiltMaxRoll` | 4 | 3 | 2 |
| 通用（`titan_base.set`） | 不能跳（`jump 0`）、不能蹬墙、不能滑铲、`stepheight` 80、`hardFallDist` 40、`physicsMass` 3000、`footstep` 伤害最低速度 50 |

注意：[TITAN-LIST](../TITAN-LIST.md) 第 1 节表里的冲刺次数（4 / 3 / 2）是按底盘设置文件算的，**多人里实际是 2 / 1 / 1**（每台泰坦的设置文件覆盖了 `dodgePowerDrain` / `powerregenrate`），已实测。

### 3.3 和移动有关的技能（实测）

运行 `20261030_020515_t0_kit`。

| 项 | 实测 | 出处 |
|---|---|---|
| ADS（瞄准）走速 | Ronin 135、Northstar 135、Ion 188、Tone 125、Monarch 100、Scorch 105、Legion 116 | 武器 `ads_move_speed_scale`：Ion 0.75、Monarch 0.40、Legion 0.55、Ronin 0.5，没写的默认 0.5 |
| Northstar 悬停 | 1.8 s 升到离地 340 u（竖直速度最高 400），悬停到 3.0 s，然后下落，约 4.0 s 落地；悬停中水平速度上限 300 | `mp_titanability_hover.nut` `FlyerHovers`：`RISE_VEL` 450，3 s，`airSpeed` 250（+50），重力 0 |
| Northstar 飞行核心 | 升到 340 u，6 s 内在 334–340 u 之间起伏，水平上限 250，约 7.0 s 落地 | `mp_titancore_flight_core.nut`：6 s，水平 200（+50） |
| Ronin 相位冲刺 | 按下当帧水平 967 u/s，1.3 s 内线性降回走速（约 590 u/s²），相位 1 s | `mp_titanability_phase_dash.nut`：`PHASE_DASH_SPEED` 1000，`PhaseShift` 1 s，`move_slow` 0.6 |
| Ion 激光核心 | 走速 250 → 188（×0.75），约 5 s，再 2 s 回到 250 | `move_slow` / `turn_slow` 0.25 |
| Tone 齐射核心 | 蓄力 0.5 s 内走速 250 → 75（×0.3） | `SEVERITY_SLOWMOVE_SALVOCORE` 0.7 |
| Scorch 火焰核心 | 蓄力约 0.75 s 内 210 → 84（×0.4），不能冲刺 | `move_slow` / `dodge_speed_slow` 0.6 |
| Legion 枪盾 / 强力射击 | 强制 ADS → 116 | `SetForcedADS` + `ads_move_speed_scale` 0.55 |
| Legion、Monarch 核心；Ronin 格挡；Ion 涡旋；Scorch 热盾 | 走速不变 | — |

## 4. 文件

| 文件 | 作用 |
|---|---|
| [plans_titan.py](plans_titan.py) | 实验表：`t0_smoke`、`t0_turn`、`t0_move`、`t0_probe`、`t0_lanes`、`t0_kit` |
| [analyze_titan.py](analyze_titan.py) | 按标签切段：转速、速度曲线、镜头 |
| [analyze_move.py](analyze_move.py) | 第 3 节的移动表 |
| [titan_mouse.py](titan_mouse.py) | runner `--mouse` 用的鼠标输入 |
| [extract_kit.py](extract_kit.py)、[summarize_kit.py](summarize_kit.py) | 读武器文件，生成 `static/<泰坦>.txt` 和 `static/KEYS.txt` |
| [titans/](titans/README.md) | 每台泰坦一页 + 对比表 |
| `../../mod/HSD.TF2Diag/mod/scripts/vscripts/hsd_diag_titan.gnut`、`hsd_diag_titan_cl.gnut` | 诊断模组的泰坦命令和日志 |
| `../../runtime/runner.py` | 加了 `--mouse` 开关（不加时行为不变） |
