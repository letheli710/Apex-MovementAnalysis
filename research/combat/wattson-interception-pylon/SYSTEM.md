# Wattson 大招 Interception Pylon（拦截塔）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_trophy_defense_system.nut`（3227 行），`txt` = `weapons/mp_weapon_trophy_defense_system.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Wattson / 大招 / Interception Pylon / `mp_weapon_trophy_defense_system`（内部叫 Trophy）。
- **一句话**：放一座塔（血 150）。半径 512 的球里，飞进来的投射物（手雷、火箭、技能弹）被电弧打掉；有视线的队友每 0.2 s 回 1 点护盾，总池 250；队友站在旁边时 Wattson 的电网回充 ×5。
- **分类**：待定（防御）。对 PvE 有两处可借：**系统**（"区域内按规则拦截投射物"——可做成反制敌人投掷物的道具；"塔给区域内友军持续回资源、有视线才回"）；**可视化**（拦截电弧光束）。
- **可拆出的部件**：
  - 投射物拦截球 → 3.2.2 `Trophy_InterceptProjectiles` + `Trophy_ShouldTargetProjectile`
  - 投射物的拦截白名单（`.txt` 字段 `trophy_system_ignores`）→ 3.2.3
  - 区域回护盾（共享资源池、视线、受伤延迟）→ 3.2.4 `Trophy_RepairShields`
  - 区域加快技能回充（给武器加 mod）→ 3.2.5
  - 视线判定（锥形 + 5 点 trace）→ 3.2.4 `Trophy_HasLOSToPlayer`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 塔 | `CreatePropScript(SOLID_OBB)`，包围盒 64×64×72，重型护甲，可攀爬（`AllowMantle`） | `nut:605-650` |
| 拦截 | `vortex_sphere` 实体（半径 512、bullet_fov 360），`Vortex_ConvertToVortexTriggerArea` 变成触发区；投射物进入时回调 `Trophy_OnProjectileHitVortexTrigger` | `nut:2070-2133`、`nut:2285`。子弹回调直接 return：**不挡子弹** |
| 拦截表现 | `info_particle_system` 光束从塔顶到投射物位置，0.3 s；投射物 `Destroy()`（不爆炸） | `nut:2324-2375` |
| 回护盾 | 触发器 `trigger_cylinder` 半径 512、上下各 256；每个进入的玩家起两条线程：视线记录 + 回盾 | `nut:770-780`、`nut:1159`、`nut:1285`、`nut:1493` |
| 回盾 HUD | 状态效果 `target_shields`（预计能回多少）、`trophy_tactical_charge`（电网加速提示） | `nut:1706`、`nut:1426` |
| 电网加速 | 给电网武器加 mod `interception_pylon_super_charge`（`regen_ammo_refill_rate *5`） | `nut:1600-1620`；`mp_weapon_tesla_trap.txt` Mods |
| 剩余护盾显示 | waypoint `WATTSON_TROPHY_LIFE`，每帧写剩余池 | `nut:2135` |
| 卡进物体 | 每 0.25 s hull trace，开始就在实体（移动平台 / 门）里 → 自爆 | `nut:2028` |

服务端 / 客户端：全部判定在服务端；客户端画 AR 范围球（`TROPHY_AR_EFFECT_SIZE 768`，`nut:54`）、HUD 图标、电网加速时第一人称特效。

可疑处：`Trophy_ShouldTargetProjectile` 里有一句没删的 `printt( ignore )`（`nut:2652` 附近）和 `projectile.GetOwner != null`（比较函数引用，永远为真，`nut:2389`）。前者像 SDK 调试残留，后者是原版也可能有的 bug。

## 2. 流程

```
按键 → 放置预览（距离 64–94，坡度点积 0.74，见 _shared/B-placement.md）
放下 → Trophy_Deploy
 ├ 0 s：生成塔，播 prop_trophy_expand；开始"卡进物体"检查
 ├ 1.0 s（TROPHY_DEPLOY_DELAY）：张开；建回盾触发器 + 提醒触发器；
 │        插入 owner.e.activeUltimateTraps，超过上限（1，升级后 2）就毁掉最旧的
 └ 开 Trophy_InterceptProjectiles：建 vortex 球 → 一直存在
运行中：
 ├ 投射物进球 → ShouldTargetProjectile → 有视线 → 电弧 + Destroy()
 ├ 玩家进圆柱 → 有视线、1 s 内没受伤 → 每 0.2 s +1 盾，从池里扣
 │                             → 是 Wattson 本人：电网回充 ×5
 └ 离开圆柱 → 等 1.0 s 再确认，才停
结束：被打掉（150 HP）/ 被 Crypto EMP 摧毁（playlist crypto_emp_destroy_wattson_trophy 默认 true）/ 放新塔挤掉 / 回合结束
```

**没有持续时间**：`DestroyTrophyAfterZap`（90 s 计时，`nut:2237`）和 `DestroyTrophyAfterZapCount`（拦截次数上限，`nut:2173`）定义了但本地脚本里没有调用。护盾池用完塔也还在，只是不再回盾，拦截继续。

升级（被动 `PAS_BATTERY_POWERED` + 天赋）：
- `PAS_ULT_UPGRADE_ONE`：最多 2 座（`nut:3215`）。
- `PAS_ULT_UPGRADE_TWO`：塔血 ×2、盾池 ×2（`nut:3187`、`nut:3201`）。
- `PAS_ULT_UPGRADE_THREE`：拦截敌方投射物时，1.5 s 冷却、最多同时 5 个，从塔顶向随机方向抛出一个**电弧星拾取物**（`Trophy_CreateArcStar`，`nut:2425`）。

## 3. 代码

### 3.1 入口

- `OnWeaponPrimaryAttack_weapon_trophy_defense_system`（`nut:314`）：放置信息合法 → `thread Trophy_Deploy`。
- `Trophy_Deploy`（`nut:605`）：见第 2 节。

### 3.2 核心逻辑

#### 3.2.1 塔实体

血 150（`TROPHY_HEALTH_AMOUNT`）、重型护甲、可被近战、AI 只把它当"无威胁"目标（`EnableAttackableByAI(AI_PRIORITY_NO_THREAT, 0, AI_AP_FLAG_SMART_AI_ONLY)`，`nut:660`）。自己的电网伤害和友方毒气 ×0（`nut:2763`）。

#### 3.2.2 拦截球

```
vortex_sphere: radius = height = 512, bullet_fov 360, 物理拉力全 0, 不挡主人武器
投射物进入 → OnProjectileHitVortexTrigger:
    同一 realm、没插在东西上（isPlanted）、ShouldTargetProjectile、塔顶→接触点视线通
    → 光束 + projectile.Destroy()（不触发爆炸）
```

#### 3.2.3 拦截规则 `Trophy_ShouldTargetProjectile`（`nut:2562`）

```
ignore = 投射物武器 .txt 的 trophy_system_ignores（缺省 "none"）
ignore == always → 不拦
ignore == friendlyOnly 且同队 → 不拦；enemyOnly 且敌队 → 不拦
.txt trophy_system_intercept_large == 1 → 一定拦（大投射物不看距离）
接触点距塔 ≥ 512 → 不拦
记下第一次接触位置和速度方向（方向变了就重记）
若第一次接触在半径内且方向没反转：
    沿速度预测 0.2 s：没碰到东西 → 不拦（还没要落进来）
                      碰到东西但落点 ≥ 512 → 不拦
                      碰到墙（法线 z ≤ 0.5）→ hitWall
ignore == allowBounce → 碰墙那一下不拦（让它弹）
否则拦
```

要点：**只拦"0.2 s 内会落在 512 以内"的东西**，飞过头顶的不拦。默认 `none` 意味着友军的投射物也会被拦（只有 `friendlyOnly` 才放过友军）——例：Mad Maggie 破坏球、Vantage 回声是 `friendlyOnly`；Ash 电弧陷阱、Horizon 黑洞、Ballistic 呼啸弹是 `none`；大部分枪是 `always`。

#### 3.2.4 回护盾

`Trophy_OnChargeTriggerEnter_Internal`（`nut:1285`），每帧：

```
离开圆柱 → 等 1 s，还在外面就结束
HasLOSToPlayer → 记进 trophyLoSToPlayers
CanHealPlayer（能被治疗、1.0 s 内没受伤、有视线）→ 把他设为回盾目标
满盾且 1 s 内有视线 → 状态效果 trophy_tactical_charge（HUD 提示）
```

`Trophy_RepairShields`（`nut:1493`），每帧：

```
1 s 内没视线 → 撤电网加速 mod、停回盾特效
不在倒地 → 电网武器加 interception_pylon_super_charge
盾没满、能治疗、在目标表里、池 > 0：
    每 0.2 s：盾 += 1（不超上限），池 -= 实际回的量
    HUD：target_shields = (池 / 目标人数) / 最大盾
```

`Trophy_HasLOSToPlayer`（`nut:1973`）：先 `FindVisibleEntitiesInCone(塔心, 指向玩家, 512, 45°)`，看不到再对玩家 5 个点（眼、眼和胸中点、中点左右各 8、胸）打 line trace，任一通就算看见。

`Trophy_PlayerOnDamage`（`nut:1925`）：受伤 → `recentlyDamaged = now + 1.0`（出界、毒圈、毒气不算）。

#### 3.2.5 技能回充加速

只认电网（`Trophy_GetAllowableWeaponsToCharge`，`nut:1949`）。机制是**给武器挂一个改 `regen_ammo_refill_rate` 的 mod**，离开就摘掉。这是"区域内改技能冷却"的通用写法。

### 3.3 客户端表现

- AR 范围球（模型尺寸 768）、冷却圈（200–3000 u 内显示）、waypoint 显示剩余护盾 / 计时。
- 电网加速：`TacticalChargeFXThink`（`nut:2911`）第一人称特效。
- 被拦截的投射物：光束 `Trophy_GetZapFX` + 爆炸特效 `Trophy_InterceptProjectileExplosion`（`nut:2715`）。

### 3.4 依赖

- 引擎 `vortex_sphere` + `Vortex_ConvertToVortexTriggerArea`（同 Gibraltar 护罩、Newcastle 盾的拦截写法，推断）。
- `FindVisibleEntitiesInCone`、`Player3pHealFXAddRequest`、`CanBeHealedByDroneMedic`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 拦截 / 回盾半径 | 512（min 498） | u | playlist `wattson_trophy_interceptProjectileRange`，默认 512（`nut:241-242`） | 球半径 = 圆柱半径 | |
| 回盾圆柱高度 | 上下各 256 | u | `nut:772-773` | | |
| 预测时间 | 0.2 | s | `nut:2618` | 只拦会落进来的 | 改大 = 更早拦 |
| 塔血量 | 150（升级 ×2） | HP | `nut:106`、`nut:3187` | | |
| 护盾池 | 250（升级 ×2） | 盾 | `nut:134`，playlist `wattson_trophy_shieldPoolAmount` | 所有人共用 | |
| 回盾量 / 间隔 | 1 / 0.2 | 盾 / s | `nut:116-117`（旧 1 / 0.5，`nut:113-114`） | = 5 盾/s | |
| 受伤后暂停 | 1.0 | s | `nut:118` | | |
| 视线超时 | 1.0 | s | `nut:119` | | |
| 视线锥 | 45° | | `nut:1985` | | |
| 数量上限 | 1（升级 2） | 座 | `nut:115`、`nut:250`、`nut:3215` | | |
| 展开延迟 | 1.0（动画 0.66） | s | `nut:103`、`nut:770` | | |
| 放置距离 | 64–94 | u | `nut:87-88`；`txt object_placement_distance_max 94` | | |
| 坡度限制 | 0.74 | 点积（推断） | `nut:102` | | |
| 电网回充倍率 | ×5 | | `mp_weapon_tesla_trap.txt` `interception_pylon_super_charge` | | |
| 电弧星转换 | 冷却 1.5 s、最多 5 个、抛速 100–300、仰 30° | | `nut:2377-2378`、`nut:2430-2433` | 升级三 | |
| 充能 | 弹匣 180，每次 180，回充 1 /s → 180 s | | `txt MP_BASE` | 大招冷却 | |
| 大招冷却（SP_BASE） | 100 / 2 → 50 s | | `txt SP_BASE` | SP 版本 | |
| 计时自毁（未调用） | 90 | s | playlist `wattson_trophy_destroy_cooldown` | 没生效 | |

## 5. 未解决和要实测的

1. **友军投射物会不会被拦**：按脚本，`trophy_system_ignores none` 的友军投射物也会拦。测法：R5 runner 里两个同队 bot（或自己），在自己的塔旁扔电弧陷阱 / 黑洞，看是否被打掉。注意 `SF_BLOCK_OWNER_WEAPON` 只放过主人自己。
2. **塔没有持续时间**：本地脚本没调用计时自毁。测法：放下等 3 分钟。
3. **大招冷却 180 s** 是否被 playlist 改过：在 dedi 上放一次看回充。
4. 对 NPC：NPC 投掷物（如 spectre 的手雷）是投射物，按规则会被拦。PvE 里这是"反制敌人投掷物"的主要用途。测法：dedi 上刷带手雷的 NPC。

## 6. HSD 实现

**未实现。**

建议做法：

- 新文件 `Pylon.cs`：`Pylon : CombatUnit, ICombatDrawable`（血 150）。
- 拦截：每帧遍历 `sim.entities` 里的 `ThrownItem`（`Throw.cs`）。HSD 投掷物都是自己算弹道的，可以直接用 `Ballistics` 的抛物线预测 0.2 s 后的位置（`Throw.cs` 已有预测函数）；落点在 512 内且 `CombatSim.WorldClear(塔顶, 投射物)` → `done = true`，画一条 0.3 s 光束（`CombatSim.tracers` 已有）。
- 白名单：给 `ThrowParams` 加一个 `pylonIgnore`（`None / Always / FriendlyOnly / EnemyOnly / AllowBounce`），照 R5 字段。
- 回盾：HSD 目前只有统一血量，没有护盾（`CombatCore.Health`）。在加护盾之前，可以改成"回血，池 250，每 0.2 s 1 点"，开关 `hsd.combat.pylon.healHp`。
- 回充加速：`Charges.Step(dt, rateScale)` 已经有倍率参数（`CombatCore.cs:254`），塔范围内传 ×5。
- 和 R5 的差：没有视线锥（直接 trace）；回血代替回盾。写进 `R5-DIFF-ARCHIVE.md`。
