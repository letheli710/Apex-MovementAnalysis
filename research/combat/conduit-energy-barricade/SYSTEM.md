# Conduit 大招 Energy Barricade（能量屏障）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_conduit_shield_mines.nut`（777 行，发射器），`line.nut` = `vscripts/weapons/mp_ability_conduit_shield_mines_line.nut`（1055 行，地雷），`txt` / `line.txt` 同名 `.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Conduit / 大招 / Energy Barricade / `mp_ability_conduit_shield_mines`（玩家手上的）+ `mp_ability_conduit_shield_mines_line`（发射地雷的"轰炸武器"）。
- **一句话**：瞄准一点（最远 2000 u），发射两发弹（间隔 1.1 s），各自飞到目标点上空 4 m 处炸开，往**垂直于瞄准方向**的一条线上撒共 7 个干扰器（间距 380 u，整条线约 2280 u）；3 s 后激活，45 s 内每帧对半径 200 内的敌人造成范围伤害——每人每秒最多一次 10 伤害 + 1 s 减速 0.25。
- **分类**：好技能（大范围区域伤害 + 减速）；系统（"空爆 → 子弹按预定落点分撒"的投放方式，可复用到别的布雷 / 撒弹技能；预览弧线）；可视化（干扰器间的连线、半径圈、受击者到干扰器的电弧）。
- **可拆出的部件**：
  - 精确落点的弹道（`SolveBallisticArc` / `CalcProjectileTrajectory` 给定飞行时间）→ 3.2.1
  - 空爆分撒（线形落点表）→ 3.2.2 `GenerateMineLocations`
  - 地雷放置规则（贴墙反弹、离自己的地雷太近就作废、落地清掉范围内敌方地雷）→ 3.2.3
  - 区域伤害 + 每人冷却 + 短减速 → 3.2.4 `ShieldMine_OnDamageDealt`
  - 相邻地雷连线表现 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 发射 | `Grenade_Launch`，速度 = `SolveBallisticArc(起点, 1500×1.05, 目标+(0,0,157)±30 侧偏, sv_gravity)` | `nut:200-215`；`txt:29` |
| 两发 | `burst_fire_count 2`、`burst_fire_delay 1.1` | `txt:67-68`；第一发锁武器，第二发解锁（`nut:190-205`） |
| 空爆 | `BombFlightThread`：水平飞到离目标 < 50 u 时，hull trace 校正到目标点，`DeployShieldMineLine` | `nut:263-316` |
| 撒雷 | 从空爆点 `Grenade_Launch(line 武器, 速度 = CalcProjectileTrajectory(…, 1.25 s))`，自旋 `<0,500,0>` | `line.nut:127-165` |
| 地雷落地 | `PlantStickyEntityThatBouncesOffWalls(…, DOT_45DEGREE)`：墙面（法线和竖直夹角 > 45°）弹开，地面粘住 | `line.nut:285` |
| 地雷 | `CreatePropScript(SOLID_CYLINDER)`，血 200、重甲、AI 绕行（`SetAIObstacle`） | `line.nut:665-700` |
| 伤害 | 每帧 `RadiusDamage(10, 内外半径 200, 只被 brush 挡)`，不伤自己 | `line.nut:830-845` |
| 每人冷却 / 减速 | 伤害回调：玩家 `lastShieldMineDamageTime` 1 s；NPC 用电击免疫窗 1 s；`move_slow 0.25`，1 s，淡出 1 s | `line.nut:470-555` |
| NPC 电击 | `EMP_DamagedPlayerOrNPC` | `line.nut:500` |
| 受击电弧 | 粒子从受害者胸口连到地雷，持续 1 s | `line.nut:557-596` |

服务端 / 客户端：都在服务端；客户端画瞄准弧线和落点圈（`WeaponArcPreviewThread_Client`，`nut:370`）、手臂 pose 随仰角变化（`DoPoseParamLerp`）。

## 2. 流程

```
按住大招 → 预览：模拟手雷落点（weapon.SimulateGrenadeImpactPos）
           若落点是墙（法线和竖直 > 45°）→ TraceFromWallToTop 找墙顶（后退 1 m、上 4 m）
开火 burst 0：
 ├ 计算落点，缓存；锁武器和消耗品
 ├ 空爆点 = 落点 + 向上 trace 157（4 m）；横向偏 +30
 └ 发射弹 0（负责 radiusMultiple[0..3] = −3, −2, −1, +3）
1.1 s 后 burst 1：
 ├ 用缓存落点；横向偏 −30；解锁武器
 └ 发射弹 1（负责 [4..6] = +2, +1, 0）
每发弹：飞到距空爆点水平 50 u 内 → 校正 → 空爆 → 每个落点发一颗地雷（飞 1.25 s）
每颗地雷落地：
 ├ 墙 → 弹开（反弹计数，超过退还——Deployable_CountBouncesAndRefund）
 ├ 打到友方地雷 → 以 300 u/s 向前上方弹开；打到敌方地雷 → 双双摧毁
 ├ 离自己已有地雷 < 180（0.9×200）→ 作废（播自毁特效）
 └ 否则：摧毁 200 内的敌方地雷 → ShieldMineLifetime_Thread
ShieldMineLifetime_Thread：
 ├ 生成；超过 14 个时挤掉最旧的（AddNewLimitedLegendObject）
 ├ 3 s 激活动画（升起 15 u）
 ├ 和 450 u（2.25×200）内先落地的自己地雷连线
 └ 45 s：每帧 RadiusDamage(10, r 200)
结束：45 s / 被打掉（200 HP）/ 被 EMP / 主人出局 → 降下 0.5 s + 结束动画 + 溶解
```

升级：
- `PAS_ULT_UPGRADE_ONE`：9 颗（`radiusMultiple` 加 ±4，`line.nut:195-200`）、最远射程 ×1.15（`nut:752`）、`upgrade_ult_one` 发射速度 ×1.15（`txt:180-184`）。
- `PAS_ULT_UPGRADE_TWO`：地雷半径 ×1.1 = 220（`line.nut:169-176`）；`upgrade_ult_two` 能量 120（`txt:186-192`）。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_ability_shield_mines`（`nut:154`），每发一次（burstIndex 0 / 1）。

### 3.2 核心逻辑

#### 3.2.1 精确落点弹道

```
发射：as = SolveBallisticArc(枪口, v = 1500*1.05, 目标, g = sv_gravity)   // 解速度方向
      Grenade_Launch(dir = as.fire_velocity / 1500)                      // 引擎再乘 1500
撒雷：v = CalcProjectileTrajectory(空爆点, 落点, t = 1.25 s)                // 给定飞行时间解速度
```

`CalcProjectileTrajectory` 是"已知起点、终点、时间求初速度"：`v = (Δ − ½·g·t²) / t`（推断，标准公式）。

#### 3.2.2 落点表（`GenerateMineLocations`，`line.nut:178`）

```
mult = [−3, −2, −1, +3, +2, +1, 0]   （升级：[−4,−3,−2,−1,+4,+3,+2,+1,0]）
right = 水平(空爆点 − 发射起点) 的右向量
for i in 弹 0 → 0..3, 弹 1 → 4..6:
    理想落点 = 空爆点 + mult[i]·1.9·200·right − (0,0,157)
```

注意：理想落点只是"比空爆点低 4 m 的那个高度"，真正落点由地雷物理决定（`simulateCollisions` 只在预览时用）。

#### 3.2.3 放置规则

- `PlantStickyEntityThatBouncesOffWalls(projectile, cp, DOT_45DEGREE)`（`line.nut:285`）。
- `PositionTooCloseToOtherMines`（`line.nut:598`）：和自己任何地雷距离 < 180 → 作废。
- `DestroyEnemyMinesInRange`（`line.nut:638`）：落点 200 内的敌方地雷全部摧毁。

#### 3.2.4 伤害回调（`ShieldMine_OnDamageDealt`，`line.nut:470`）

```
inflictor 不是地雷 → 不管
目标是地雷：友方 0；敌方 = 200（一击摧毁对方地雷）
队友 → 0
NPC：非战斗 NPC（除假人）→ 0；在电击免疫期（1 s 窗）→ 0；否则 EMP 电击
非玩家非 NPC → 0
玩家：1 s 内被地雷打过 → 0
      否则：10 伤害（原值）；move_slow 0.25，1 s，淡出 1 s；空中或滑铲 → 水平速度 ÷2；电弧特效 1 s
```

### 3.3 客户端表现

- 半径圈：友方 / 敌方两套粒子，CP1 = 半径 ×1.1（`line.nut:790-810`）。
- 连线：`ShieldMine_CreateConnectingRope`（`line.nut:871`），友方色 `<77,217,255>`、敌方色 `<255,188,137>`；只连 450 u 内、比自己先落地的地雷。
- 激活：模型升起 15 u（`ShieldMineAnim_AnimateZ`），结束降回。
- 预览：弧线 + 落点环（`MORTAR_RING_RADIUS_FX_DIVISOR 20`，`nut:381`），默认色 `<50,200,255>`。

### 3.4 依赖

- `SolveBallisticArc`、`CalcProjectileTrajectory`、`Grenade_Launch`、`VerifyBombardmentWeapon`（和 Gibraltar / Bangalore 轰炸同一套"隐形轰炸武器"写法，推断）。
- `PlantStickyEntityThatBouncesOffWalls`、`Deployable_CountBouncesAndRefund`。
- `Electricity_ShouldStunNPCAndAddImmunity`（`_shared/B-electric-emp.md`）、`EMP_DamagedPlayerOrNPC`。
- `_shared/B-move-slow.md`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 伤害 | 10 | HP | `line.nut:18` | | |
| 每人冷却 | 1.0 | s | `line.nut:17` | 玩家；NPC 用 1 s 电击免疫 | |
| 减速 | 0.25，1 s，淡出 1 s | 强度 / s | `line.nut:531` | 轻减速 | |
| 进入砍速 | ÷2 | 水平速度 | `line.nut:536-545` | 空中 / 滑铲被打 | |
| 地雷半径 | 200（升级 220） | u | `line.nut:23`、`line.nut:169-176` | | |
| 地雷数 | 7（升级 9） | 个 | `line.nut:20`、`line.nut:195` | | |
| 间距 | 1.9×200 = 380 | u | `line.nut:188` | 圈之间有 −20 u 重叠 | |
| 空爆高度 | 4 m = 157.5 | u | `nut:42` | | |
| 撒雷飞行时间 | 1.25 | s | `line.nut:26` | | |
| 激活时间 | 3 | s | `line.nut:15` | | |
| 持续 | 45（注释 `//5`） | s | `line.nut:16` | **可疑**，见第 5 节 | |
| 地雷血量 | 200 | HP | `line.nut:19` | 重甲 | |
| 每人上限 | 14 | 个 | `line.nut:21` | 两次大招 | |
| 最小间隔 | 180 | u | `line.nut:24` | | |
| 连线距离 | 450 | u | `line.nut:772` | 表现 | |
| 射程 | 120–2000（升级 ×1.15） | u | `nut:39-40`、`nut:748` | | |
| 发射速度 | 1500（×1.05 解弧线） | u/s | `txt:29`、`nut:207` | | |
| 两发间隔 | 1.1 | s | `txt:68` | | |
| 两发横向偏移 | ±30 | u | `nut:186-189` | | |
| 瞄准仰角 | −25° … 50° | | `nut:44-45` | | |
| 大招能量 | 150，每次 75 ×2 发，回充 1/s → 150 s | | `txt:70-75` | 升级二：120 | |

## 5. 未解决和要实测的

1. **持续 45 s 还是更短**：`SHIELD_MINE_LIFETIME = 45//5`，注释残留说明改过；正式服记忆里明显更短。测法：R5 runner 放一次大招，计时到地雷消失。
2. **10 伤害打护盾还是血**：名字叫 shield mines，脚本没有护盾特判。测法：dedi 上让 dummie 带护盾站进去，看护盾 / 血谁先掉。
3. 每帧 `RadiusDamage` 的开销：45 s × 7 个 × 每帧；HSD 实现时改成每 0.1 s 检查一次即可（伤害有 1 s 冷却）。
4. 空爆点在室内（上方 4 m 被天花板挡）时，`trUp.endPos` 会贴着天花板；落点表仍按"−157"算，结果未知。测法：室内放一次。

## 6. HSD 实现

**未实现。**

建议做法：

- `ConduitBarricade.cs`：
  - 发射：复用 `Throw.cs` 的投掷物；目标点已知，用"给定飞行时间求初速度"补一个 `Ballistics.VelocityForTime(from, to, t, g)`（HSD 已有抛物线预测，可加反解）。
  - 空爆：投掷物到达目标上空 157 u 时 `done = true`，生成 7 个子投掷物（`ThrownItem`，粘地、墙面弹开——`ThrowParams.stick` + `OnBounce` 判法线）。
  - 地雷：`ShieldMine : CombatUnit, ICombatEntity`，血 200；每 0.1 s 查 200 内敌人，`WorldClear` 挡则不伤；`Dictionary<CombatUnit,double>` 1 s 冷却；`slowScale = 0.75`（强度 0.25）1 s。
- 预览：`CombatSim.CurrentArc()`（`CombatSim.Items.cs:397`）已有抛物线显示，可直接画。
- 和 R5 的差：没有连线特效；持续时间等第 5 节第 1 条实测后定（先用开关 `hsd.combat.barricade.duration`，默认 45 照脚本）。写进 `R5-DIFF-ARCHIVE.md`。
