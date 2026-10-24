# N8-A：传送技能是不是共用一套系统

日期 2026-10-24。来源：R5Flowstate S21 的 Squirrel 脚本（`platform/scripts/vscripts/weapons/`，以及 `platform/scripts/weapons/*.txt` 的武器设置）。下面只写文件名、函数名和重新表述的规则，不贴源码。

**结论：大部分是共用的，分三层。** 最底下是同一个原生"相位"状态；中间有一套共用的脚本"相位隧道"引擎，三个技能都用它；最上面每个技能只换了"路径从哪来、有几个入口、放在哪"。看起来像但原理不同的有两个：Alter 战术是**瞬间传送**，Loba 是**瞬间传送而且不进相位**。

## 1. 三层

| 层 | 是什么 | 谁用 |
|---|---|---|
| **① 原生相位状态** | `PhaseShift(ent, warmup, duration, type)`（`sh_phase_shift.gnut`）调用原生的 `ent.PhaseShiftBegin(warmup, duration, type)`；结束用 `PhaseShiftCancel()`；引擎回调 `CodeCallback_EnterPhaseShift` / `ExitPhaseShift`。类型是一个枚举 `PHASETYPE_*` | 除 Loba 外全部 |
| **② 脚本相位隧道引擎** | `mp_weapon_phase_tunnel.nut` 里的 `PhaseTunnel_*` 函数：触发区、路径整理（按速度和最短 / 最长时间重采样）、`PhaseTunnel_PhaseEntity`（把玩家挂到一个脚本 mover 上，每帧 `NonPhysicsMoveTo` 到下一个路径点） | Wraith 大招、Ash 大招、Alter 大招 |
| **③ 每个技能自己的部分** | 路径从哪来、几个入口、放置规则、出口速度 | 各自的脚本 |

## 2. 相位类型

同一个 `PhaseShift` 函数，按类型只改这几样（`sh_phase_shift.gnut` 的 `PhaseShift` 和服务器线程）：

| 类型 | 技能 | 加速状态效果 | 能看到相位外的人 | 特效 / 声音 |
|---|---|---|---|---|
| `BALANCE` | Wraith 战术 Into the Void | 有（`speed_boost`，持续整个相位） | 能 | 冲刺消失特效 |
| `TUNNEL` | Wraith 大招 Dimensional Rift | 有 | 看开关（void vision） | 同上 |
| `BREACH` | Ash 大招 Phase Breach | 有 | 看开关 | 同上 + Ash 的结束声 |
| `TRANSPORT` | Alter 大招 Void Nexus | 有 | 能 | 自己的拖尾特效和声音 |
| `DOOR` | Alter 战术 Void Passage | **没有** | 能 | 没有消失特效，自己的声音 |
| `GATE` | 地图机关（Olympus 的门） | 有 | — | 自己的特效 |
| `DASH`、`DEFAULT` | 其他 / 默认 | — | — | 默认特效 |

所以"虚空里的样子"（看不到别人、加速、特效）基本是同一个状态，只按类型开关几个选项。

## 3. 每个技能怎么把人移过去

| 技能 | 武器设置（printname） | 移动方式 | 路径从哪来 | 入口 | 能穿墙吗 |
|---|---|---|---|---|---|
| **Wraith 战术** | `mp_ability_phase_walk`（`#WPN_PHASE_WALK`） | **不传送**：只进相位，玩家用正常移动在虚空里跑 | — | — | **不能**：相位只改可见 / 伤害 / 加速，世界碰撞照旧（M10-W 实测：照常跑、照常撞墙；原生层待 N8-C 确认） |
| **Wraith 大招** | `mp_weapon_phase_tunnel`（`#WPN_PHASE_TUNNEL`） | **挂在 mover 上回放路径** | **Wraith 放置时自己跑过的路**（每个路径点记录位置、速度、是否下蹲、是否在动作中），旅行时逐点回放，玩家速度设成录下的速度 | **两端都有**，两个方向都能走，持续期间可以反复进 | **不能**：路是她真跑过的 |
| **Ash 大招** | `mp_weapon_phase_breach`（`#WPN_PHASE_BREACH`） | **同一套 mover 回放**（直接调用 `PhaseTunnel_*`） | **生成的直线**：起点到目标点按固定步长切成路径点；目标点要通过出口检查（包括视线检查） | **只有起点一个**，单向 | **不能选墙后的点**（目标要有视线）；旅途中 mover 不做碰撞 |
| **Alter 大招** | `mp_ability_transport_portal`（`#ABL_ULT_TRANSPORT_PORTAL`；数据板 `ALTERULTDATAPAD`） | **同一套 mover 回放** | **生成的抬高路径**：起点到 Nexus 每 150 u 一个点，每个点向上探测抬高越过障碍，再做平滑；旅行时间 = 路径帧数 × 0.1 + 0.1 s，受 `portalSpeed` 和最短 / 最长时间限制 | 队友身边一个入口，**单向回到 Nexus** | 路径越过障碍，不是穿过 |
| **Alter 战术** | `mp_ability_phase_door`（`#ABL_TAC_PHASE_DOOR`） | **瞬间传送**：进触发器 → `TeleportPlayerFromPortalTrigger` → `TeleportPlayerNoInterp`，可选传送后短暂相位（`doPostPortalPhaseShift`） | 没有路径 | **两端都有**，有防抖 `reEnterDebounce` | **能**：这个技能就是穿墙用的，墙厚上限 30 m（`wallThicknessMax`），可以穿天花板 / 地板 |
| **Loba 战术** | `mp_ability_translocation` | **瞬间传送**，**不进相位** | 手环抛物线落点 | — | 不能（手环要真的飞到那里） |

出口速度：
- Alter 战术：出口方向 × clamp(进门速度在门方向上的分量, `exitVelocityMin` 50, `exitVelocityMax` 300)。
- Wraith / Ash / Alter 大招：每帧的速度来自路径点，离开时的速度取决于最后一个路径点。M10-W 测到 Wraith 出口速度 0，原因待 N8-B 读路径整理函数确认。

## 4. 回答用户的几个问题

- **是不是共用一套？** 是。五个技能共用原生相位状态；三个大招还共用同一套"挂在 mover 上沿路径走"的引擎（Ash 的脚本直接调用 Wraith 的 `PhaseTunnel_*` 函数）。
- **为什么有的能穿墙、有的不能？** 不是相位系统决定的，是**路径从哪来**决定的：
  - Wraith 大招的路是她真跑过的；
  - Ash 的终点要有视线；
  - Alter 大招的路会抬高越过障碍；
  - 只有 Alter 战术**根本没有路径**，是两点之间的瞬间传送，所以能穿墙。
- **为什么有的能反复进、有的不能？** 是触发器的数量决定的：
  - 两端都有触发器的（Wraith 大招、Alter 战术）可以来回走；
  - 只有起点有触发器的（Ash 大招、Alter 大招）是单向的。
- **"在虚空里跑"的是哪个？** 只有 Wraith 战术：它只进相位、不移动玩家，玩家用正常移动跑。
- **只是效果像、原理不同的**：
  - Alter 战术（瞬间传送 + 可选的短暂相位）；
  - Loba（瞬间传送，不进相位）。

## 5. 下一步

- **N8-B**：每个技能单独写规则，包括时间线、路径整理（速度、最短 / 最长时间）、出口速度。先做 Wraith 大招，解释 M10-W 测到的出口速度 0。
- **N8-C**：用 Ghidra 查原生的 `PhaseShiftBegin`：相位到底改了什么（碰撞组、可见性、移动代码里有没有分支）；再查玩家挂在 mover 上时移动代码是不是整个跳过。
- **待确认**：Flowstate 的脚本有社区改动，S21 原版是否一样要靠实测核对（N8-D）。
