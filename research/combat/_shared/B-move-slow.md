# 公共部件 B：区域减速（陷阱 / 区域控制类的减速写法）

批次 B，会话 `combat-b`，2026-10-31。只读脚本。

**和别的共享记录的关系**：状态效果框架本身（`StatusEffect_AddTimed / AddEndless / Stop`、严重度含义）见 `_shared/E-STATUS-EFFECT.md`；电击类（固定时长 + 转向 + 屏幕）见 `_shared/B-electric-emp.md`。本文只整理批次 B 里"进区域减速"的几种写法和数值，便于 HSD 统一。

## 0. 概要

- **部件**：区域 + `move_slow` 状态效果 + （可选）进入时砍一半水平速度。
- **一句话**：B 批 6 个技能都有减速，写法分三种：在里面一直减（Endless + 引用计数）、碰一下减一段（Timed）、电击（固定时长 + 转向）。几乎都带"空中或滑铲进入 → 水平速度 ÷2"。
- **分类**：系统。

## 1. 一览

| 技能 | 写法 | 玩家强度 | NPC 强度 | 时长 | 砍速 | 来源 |
|---|---|---|---|---|---|---|
| Catalyst 尖刺 | Endless，离开尖刺就停 | 0.5 | 0.8 | 在里面 | 空中 / 滑铲 ÷2（进入时一次） | `mp_ability_spike_strip.nut:1660-1670` |
| Catalyst 黑幕 | Endless + 引用计数，离开墙厚度就停；NPC 出墙再 Endless 2 s | 0.5（Catalyst 本人 0） | 0.8 | 在墙里（NPC +2 s） | 空中 / 滑铲 ÷2 | `mp_weapon_ferro_wall.nut:1680-1742`、`:1772` |
| Conduit 屏障 | Timed，每次受伤 | 0.25 | （NPC 走电击） | 1 s + 淡出 1 s | 空中 / 滑铲 ÷2 | `mp_ability_conduit_shield_mines_line.nut:531-545` |
| Wattson 电网 | 电击（`B-electric-emp`） | 0.5 + 转向 0.7 | 电击击晕 | 3 + 1 s | 无 | `mp_weapon_tesla_trap.nut:2110` |
| Newcastle 城墙通电 | Timed，每 2.5 s | 0.75 + 转向 0.75 + 屏幕 | 电击击晕 | 2.5 s，淡出 1 s | 无 | `mp_ability_armored_leap.nut:7475-7478` |
| Newcastle 落地（自己） | Timed | 0.2 | — | 1.0 s，淡出 0.5 | — | `mp_ability_armored_leap.nut:2077` |
| Horizon 黑洞 | 不用减速，直接改速度（见 horizon 记录） | — | 定身 | — | — | — |
| Ash 电弧陷阱 | 不用减速，用拴住（本地被关） | — | 电击 | — | — | — |

## 2. 流程（三种写法）

```
A. 在里面一直减（尖刺 / 黑幕）
   进入判定成立 → 若表里没有：handle = AddEndless(move_slow, s)，refCount = 1；否则 refCount++
                  若空中或滑铲：v.xy /= 2（只这一下）
   离开判定 → refCount--；== 0 → Stop(handle)
B. 碰一下减一段（Conduit 屏障）
   每次有效伤害（1 s 冷却）→ AddTimed(move_slow, 0.25, 1 s, fade 1 s)；空中 / 滑铲 v.xy /= 2
C. 电击（电网 / 城墙）
   见 B-electric-emp：move_slow + turn_slow + emp 屏幕
```

## 3. 代码

- 引用计数表：黑幕 `file.moveSlowTable[ent] = {handle, refCount}`（`mp_weapon_ferro_wall.nut:1520-1535`），尖刺旧路径同名表（`mp_ability_spike_strip.nut:1755-1790`）。多根柱子 / 多块尖刺重叠时不会叠加强度，只记次数。
- 砍速的统一写法：`if (!IsOnGround() || IsSliding()) SetVelocity(<v.x/2, v.y/2, v.z>)`——**只砍一次**，不是持续。目的是防止滑铲 / 跳跃高速穿过（推断）。

## 4. 参数

见第 1 节表。强度含义（"0.5 = 速度 ×0.5"）APEX-REPORT 2.2 对电击实测过 0.498；**NPC 的 0.8 是"×0.2"还是"×0.8"未实测**（尖刺第 5 节第 1 条）。

实测（R5，2026-11-01）：强度 s → 速度 ×(1 − s)，玩家和 NPC 相同；NPC 0.8 = ×0.2；s ≥ ~0.06 玩家不能冲刺；多个取最大。见 W2-RUNTIME §1。

## 5. 未解决和要实测的

1. NPC 强度 0.8 的含义（尖刺、黑幕都用）。测法：dedi 上 spectre 走过尖刺，量速度。
2. 多个 move_slow 同时存在时取最大还是相乘：站在尖刺上再被屏障打。测法同上，读玩家冲刺速度。

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
1. ✅ NPC 0.8 = **速度 ×0.2**（只剩 20%）。[R5] prowler 347 → s 0.5：174 → s 0.8：69；dummie 191 → 96 → 30。玩家同样是 ×(1 − s)。
2. ✅ 多个 move_slow **取最大**：0.25 + 0.5 → 100.15（= 0.5 单独）。
3. 新发现：玩家 s ≥ ~0.06 时**不能冲刺**（0.05 还能，0.06 不能），按走速 199.5 乘。所以 0.5 的尖刺对冲刺玩家实际是 299 → 100（×0.33）。

## 6. HSD 实现

现有：`CombatUnit.slowScale / slowUntil`（`HSD-Unity/.../Combat/CombatCore.cs:76-86`）只有一个槽，后来的覆盖前面的。

建议：

- 改成一个小表 `List<(object source, double scale, double until)>`，`SpeedScale(now)` 取最小（或相乘，等第 5 节第 2 条定）。
- 写法 A（在里面）：每帧刷新 `until = now + dt`，source = 区域对象；写法 B / C：`until = now + t`。
- 砍速：`CombatSim` 加一个 `HalveOnEnter(unit)`，只对玩家且只在空中 / 滑铲时（写身体，开关 `hsd.combat.zone.halveOnEnter`）。
