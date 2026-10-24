# N8 计划：传送机制

日期 2026-10-24。按用户定的顺序（N6 补测 → N7 用到 Unity → N8 传送），N8 是最后一个阶段。范围和"重启前要先确认"的问题见 [../TODO.md](../TODO.md) 的"暂缓：传送类机制"。

## 0. 先看到的一个关键事实

和 N2–N6 的移动系统不同，**传送技能的主要逻辑在 Squirrel 脚本里，源码可读**（`R5Flowstate/platform/scripts/vscripts/weapons/`）。原生代码只提供少数几个底层调用。所以 N8 的工作重心和以前反过来：

- **脚本层**：规则、数值、出口速度都直接写在脚本里，读源码就能得到；
- **原生层**：只需要查脚本调用的那几个原生函数做了什么（相位状态对移动的影响、无插值传送、安全落点搜索、挂在 mover 上时移动代码是否跳过）；
- **实测**：核对脚本规则在 S21 里是否真是这样运行的（Flowstate 的脚本有社区改动，例如 `phase_door` 里有"auto-reporting has no backing implementation here"的注释）。

仓库是公开的：脚本和反编译代码一样，**只提交文件名、函数名、行号和重新表述的公式**，不贴原文。

## 1. 技能 → 脚本

| 技能 | 脚本（`weapons/` 下） | 行数 | 传送方式（读脚本得到） |
|---|---|---|---|
| Wraith 战术 Into the Void | `mp_ability_phase_walk.nut` + `sh_phase_shift.gnut` | 236 + 1062 | 原生相位：`PhaseShiftBegin(warmup, duration, style)` / `PhaseShiftCancel()`；脚本里有一段注释掉的 400 水平限速原型 |
| Wraith 大招 Dimensional Rift | `mp_weapon_phase_tunnel.nut` | 2584 | **回放录下的路径**：每帧用 `NonPhysicsMoveTo` 把 mover 移到下一个路径点，并把玩家速度设成录下的速度；还回放下蹲 |
| Alter 战术 Void Passage | `mp_ability_phase_door.nut` | 2322 | 触发器 → `TeleportPlayerFromPortalTrigger` → `TeleportPlayerNoInterp`；出口速度 = 出口方向 × clamp(v·dir, exitVelocityMin, exitVelocityMax) |
| Alter 大招 Void Nexus | `mp_ability_transport_portal.nut`（`void_ring` 是生存模式道具，不是 Alter） | 3142 | 生成抬高路径，用同一套隧道引擎 |
| Ash 大招 Phase Breach | `mp_weapon_phase_breach.nut` | 1926 | 生成直线路径，用 Wraith 大招的隧道引擎 |
| Loba 战术 | `abilities/loba_tactical_translocation.nut` | — | **已搁置**（`SHELVED-ABILITIES.md`），重启前先问用户 |

共用关系的答案见 [N8-A-SHARED-SYSTEM.md](N8-A-SHARED-SYSTEM.md)；原生相位状态见 [N8-C-PHASE-NATIVE.md](N8-C-PHASE-NATIVE.md)。

## 2. 阶段

| 阶段 | 做什么 | 产出 |
|---|---|---|
| **N8-A 清单** | 确认每个技能的脚本、S21 是否有、武器设置文件里的调参值（`exitVelocityMin/Max`、持续时间、冷却）；列出每个脚本调用的原生函数 | `n8/N8-A-INVENTORY.md`、`map/teleport-calls.csv` |
| **N8-B 脚本规则** | 每个技能写一份规则：进入判定、时间线、落点、出口速度、相位期间的移动 | `n8/N8-B-<技能>.md`（重新表述，不贴源码） |
| **N8-C 原生调用** | 用 Ghidra 查脚本绑定表里的原生函数：`PhaseShiftBegin` / `PhaseShiftCancel`、`TeleportPlayerNoInterp`（或 `SetOrigin` + 无插值标志）、`PutEntityInSafeSpot`、`NonPhysicsMoveTo` 的 mover 挂载时玩家移动是否跳过、相位状态在 `ProcessMovement` 里的分支 | 地图新增行；账本新增 T-xx 行 |
| **N8-D 实测核对** | 先用已有数据（M10-W Wraith、`PORTAL-R2.md`）核对；再补 Ash Phase Breach 和 Wraith 战术的出入口速度；Alter 先查清 34 次放置都失败的原因（对照原生放置代码），能放出来再测 | `n8/N8-MEASURE.md` |
| **N8-E Unity 建议** | 和 Unity 现有实现（M10-W 传送门、M6-B Ash）对照，列出差别；**每条由用户决定** | `n8/TELEPORT-CHANGES.md` |

## 3. 先做哪个

建议顺序：**Wraith（两个技能）→ Ash → Alter**。
- Wraith 已经有 Unity 实现和 R5 实测，最容易核对；大招"回放录下的路径"这条，可以直接解释 M10-W 测到的出口速度 0 和路径形状。
- Ash 大招和 Wraith 大招结构相似（触发器 + 传送），而且 S11 起就有。
- Alter 卡在本地放置失败，需要先查原因。

## 4. 需要用户决定的

- Loba：按 `SHELVED-ABILITIES.md` 是因为"新意不够"搁置的。N8 是否包括 Loba？默认**不包括**。
- 每条 Unity 改动和 N7 一样，先列出来，由用户逐条决定。
