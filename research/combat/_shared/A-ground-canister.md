# 公共部件 A：只在地面上"立住"的投掷罐（碰墙弹开、落地才激活）

批次 A 共用：Bangalore 滚雷信号弹、Gibraltar 轰炸信标、Caustic 毒气手雷。三者的 `OnProjectileCollision` 几乎一样，都调 `PlantStickyEntityOnWorldThatBouncesOffWalls(projectile, cp, 0.7)`，成功后 `GrenadeIgnite()` 并启动技能线程。Fuse 大招小炸弹、Thermite 用的是相近的"法线朝上才算落地"规则（`normal.z > 0.75`）。静态研究，2026-10-31，会话 combat-a。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`wu` = `weapons/_weapon_utility.nut`。

## 0. 概要

- **部件**：`PlantStickyEntityOnWorldThatBouncesOffWalls( ent, cp, bounceDot )`（`wu:1512-1540`）。
- **一句话**：碰到的面够平（法线·上 ≥ 0.7，约 ≤ 45.6° 坡）就粘住；碰到墙 / 陡坡先按武器的弹跳参数弹开，**除非**两次碰撞间位置几乎没动（≤ 5 u，卡在墙角）才强行粘住。只粘世界、移动平台、func_brush 和几种指定道具，不粘玩家 / NPC。
- **分类**：系统（投掷物"落地才生效"的通用规则）。
- **可拆出的部件**：落地判定 → 3.1；可粘目标白名单 → 3.2 `HitEntIsValidToStick`；卡住兜底 → 3.1。

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 平地判定 | `normal · (0,0,1) ≥ bounceDot`（三个调用方都给 0.7） | `wu:1517-1519` |
| 墙上弹开 | 返回 false → 引擎按 `.txt` 的 `grenade_bounce_*` 继续弹 | 调用方 `if (!result) return` |
| 卡墙角兜底 | 记上次碰撞位置，距离 ≤ `BOUNCE_STUCK_DISTANCE` 5 u 就粘 | `wu:1522-1532`、`wu:395` |
| 粘住 | `PlantStickyEntity`（设父物体、对齐法线、停物理） | `wu:1703` |
| 白名单 | 世界、有 pusher 祖先（移动平台）、func_brush、`ziprail_launcher_prop`、`jump_tower` 等 | `wu:1542-` |
| 只触发一次 | `projectile.GrenadeHasIgnited()` 为真就忽略后续碰撞 | 各调用方 |
| 不再爆炸 | `projectile.SetDoesExplode( false )` | Bangalore / Gibraltar |
| 毒气手雷兜底 | 第 10 次碰撞还没粘上也直接放毒（`projectileBounceCount < 10`），且 `ignoreHullTrace = true` | `mp_weapon_grenade_gas.nut:116-123` |

## 2. 流程

```
投掷物碰撞
 ├ 撞到自己 → 忽略
 ├ 已点燃 → 忽略
 ├ 目标不在白名单（玩家 / NPC / 普通道具）→ false（弹开）
 ├ 面太陡：第一次 → 记位置，false；之后 → 移动 > 5 u 则 false，否则粘
 └ 面够平 → PlantStickyEntity → true
true → GrenadeIgnite、技能线程（信号弹 / 信标 / 放毒）
```

## 3. 代码

### 3.1 `PlantStickyEntityOnWorldThatBouncesOffWalls`（`wu:1512-1540`）

见第 2 节伪代码。客户端分支直接 `return false`（墙面永远弹，`wu:1534`），只有服务端有卡住兜底。

### 3.2 `HitEntIsValidToStick`（`wu:1542-`）

白名单如第 1 节表；玩家、NPC 都不在里面 → 砸到人身上会弹开（Bangalore / Gibraltar 的 `.txt` 也写了 `stick_pilot 0`、`stick_npc 0`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| bounceDot | 0.7 | cos | 调用方字面量 | 能立住的最大坡 ≈ 45.6° | 大 → 只在很平的地上立住，弹得更多 |
| BOUNCE_STUCK_DISTANCE | 5.0 | u | `wu:395` | 卡住判定 | |
| 毒气手雷最多弹 | 10 次 | 次 | `mp_weapon_grenade_gas.nut:120` | 兜底 | |
| 弹跳参数 | 见各 `.txt`（Bangalore / Gibraltar / 毒气：浅 0.53、陡 0.32、法向 0.5、随机 0.2、竖直随机 0.2、滚动 0.1/s） | — | 各 `.txt` | 弹开后怎么走 | |

## 5. 未解决和要实测的

- 斜坡 45° 附近的分界：在训练场斜坡上扔 Gibraltar 信标，看是否立住。
- 扔到敌人身上：确认弹开（不粘）。

## 6. HSD 实现

**未实现，但几乎现成**：`Throw.cs` 的 `ThrownItem` 已有 `OnBounce(sim, normal)` 回调，`Ordnance.cs` 的 `Thermite.OnBounce` 就是 `normal.z > 0.75 || bounces >= 16` 才点燃。新技能写成：

```csharp
protected override bool OnBounce(CombatSim sim, Vec3d n)
{
    if (n.z >= 0.7 || StuckInCorner() || bounces >= 10) { Activate(sim); return true; }
    return false;
}
```

`StuckInCorner()` = 和上次碰撞点距离 ≤ 5 u。建议把这个判定提成 `ThrownItem` 的一个可选参数（`ThrowParams.groundOnlyDot = 0.7`），三项技能共用。
