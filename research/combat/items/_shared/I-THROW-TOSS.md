# 公共部件 I：投掷物的公共流程（举手、出手、引信、指示）

道具批次共用，会话 `i1-records`，2026-11-01。只读脚本。破片、电弧星、铝热剂、飞刀直接走这里；Revenant 手雷只共用举手，出手是自己一份。

来源根目录：`research-src/s21-platform/scripts/`。`gr` = `vscripts/weapons/_grenade.nut`。

落点规则见别处，不重复：落地才生效 → [A-ground-canister](../../_shared/A-ground-canister.md)；粘附 `PlantStickyEntity` → [B-placement](../../_shared/B-placement.md) 3.2。

## 0. 概要

- **部件**：`Grenade_OnWeaponTossPrep` → `Grenade_OnWeaponTossReleaseAnimEvent` → `Grenade_OnWeaponToss` → `Grenade_Launch`。
- **一句话**：武器 `.txt` 把这几个回调填上，投掷就成了；速度、弹跳、引信全是 `.txt` 字段，脚本只传方向。
- **分类**：系统。
- **可拆出的部件**：
  - 出手弹道公式 → 3.1（APEX-REPORT 2.1 的公式，这里只标来源）
  - 引信两种语义 → 3.2
  - 手雷警告和抛物线 → 3.3

## 1. 实现手段

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 举手 / 按住 | 引擎的 toss 状态机，回调 `OnWeaponTossPrep` | `gr:131` 记 `startChargeTime`，起两个线程 |
| 出手 | 动画事件回调 `OnWeaponTossReleaseAnimEvent` | `gr:301-318` |
| 生成投掷物 | `weapon.FireWeaponGrenade( params )` | `gr:460`。`vel` 传的是单位方向，引擎乘 `projectile_launch_speed`（推断：`gr:237` 传 `dir × 1`，APEX 实测 |v0| = 1300） |
| 旋转 | `angVel`：默认 `<10,-1600,10>`，飞盘 `<0,30,-2200>` | `gr:49-50`、`gr:446`；只是外观 |
| 碰撞伤害和爆炸伤害分开 | `scriptTouchDamageType = 伤害标记去掉 DF_EXPLOSION`、`scriptExplosionDamageType = 伤害标记` | `gr:455-456` |
| 记录出手方向 | `grenade.proj.savedDir = 视线方向` | `gr:248`；铝热剂靠它定火墙方向 |
| 死亡掉落 | `HACK_DropGrenadeOnDeath`：举着手雷死了，原地放一颗 | `gr:566-603` |
| 手雷警告 | `show_grenade_indicator`、`damage_indicator_model`（`.txt`，原生画） | 见各 `.txt` |
| 抛物线 | `grenade_arc_indicator_*`（`.txt`，原生画） | 见 APEX 2.8 |

全部双端跑（客户端预测投掷物）。`Grenade_Launch` 客户端只在 `ShouldPredictProjectiles` 时生成（`gr:420-423`）。

## 2. 流程

```
按键 → 引擎举手（toss_pullout_time）→ OnWeaponTossPrep
  ├ startChargeTime = now（gr:133）
  ├ 服务端 HACK_CookGrenade：max_cook_time 够小才等待（gr:519-555）
  └ 服务端 HACK_DropGrenadeOnDeath（gr:566）
松手 → 动画（toss_time；toss_overhead_time 推断是朝上扔的那一套）→ 动画事件
  └ Grenade_OnWeaponToss（gr:225）
      ├ 投掷声；Grenade_Launch
      ├ owner.Signal("ThrowGrenade")
      ├ PlayerUsedOffhand（开始冷却 / 扣数量，gr:245）
      └ savedDir = GetViewForward；飞刀额外忽略跳板、重力电梯、黑洞（gr:260-263）
投掷物飞行 → 碰撞回调（各武器自己的 OnProjectileCollision）或引信到点
```

Fuse 被动：`.txt` mod `fuse_long_throw_passive` 把出手速度 ×1.7。不在这里写，见 [fuse-grenadier](../../fuse-grenadier/SYSTEM.md)。

## 3. 代码

### 3.1 出手公式

APEX-REPORT 2.1 写过（`v0 = dir × launchSpeed + dir × 继承速度`，仰角偏移系数 `k`）。`launchSpeed` 和重力是实测；仰角系数和"只继承朝前"是 TF2 同源推断，R5 没测，见第 5 节。

### 3.2 引信：`Grenade_Launch`（`gr:418-497`）

```
fuseTime = weapon.GetGrenadeFuseTime()              // grenade_fuse_time
if fuseTime > 0 and not start_fuse_on_launch:
    fuseTime -= now - startChargeTime               // 拉环后就开始算（可烹饪）
    if fuseTime <= 0: fuseTime = 0.001
// fuseTime == 0：不会自己爆，靠碰撞回调（注释 gr:432）
```

两种"什么时候爆"：

| 语义 | 字段 | 例 |
|---|---|---|
| 飞行引信 | `grenade_fuse_time > 0` | 破片 3.5 s，`start_fuse_on_launch 1` |
| 点燃后延迟 | `grenade_fuse_time 0` + 碰撞时 `GrenadeIgnite()` + `grenade_ignition_time` | 电弧星 2.8 s、Revenant 手雷 1.2 s |

### 3.3 公共初始化：`Grenade_Init`（`gr:184-222`）

设队伍；`projectile_magnetic_force` 非空就开磁吸；`projectile_visible_to_smart_ammo` 决定能不能被打（默认 `DAMAGE_NO`）；`grenade.s.originalOwner` 给伤害回调用。

## 4. 参数

投掷物各自的值在各自 SYSTEM.md 第 4 节。这里只放公共常量。

| 参数 | 值 | 来源 | 作用 |
|---|---|---|---|
| `DEFAULT_FUSE_TIME` | 2.25 s | `gr:15` | 默认引信常量 |
| `DEFAULT_MAX_COOK_TIME` | 99999.9 | `gr:16` | 烹饪上限的"不限" |
| `GRENADE_ANG_VEL_DEFAULT` | `<10,-1600,10>` | `gr:49` | 飞行旋转 |
| `GRENADE_ANG_VEL_DISC` | `<0,30,-2200>` | `gr:50` | 飞盘旋转 |
| `sv_gravity` | 750 u/s² | APEX 2.1 实测 | 重力基准 |

## 5. 未解决和要实测的

- `max_cook_time -1` 走哪条分支：`GetMaxCookTime` 没读。破片 APEX 记成不能烹饪；手感实测里确认。
- 真实按键投掷（`+attack`）在 R5 里一直没触发（APEX 2.1 未解项）。仰角系数和继承速度要它才能测。W2-RUNTIME 的做法是否解决了这件事，实测时先看。

## 6. HSD 实现

已有：`HSD-Unity/Assets/HSD/Game/Runtime/Combat/Throw.cs`（`ThrowParams`、`ThrownItem`）。字段和 `.txt` 一一对应。

和 R5 的差别：HSD 不区分"碰撞伤害"和"爆炸伤害"两种标记（R5 见 `gr:455-456`）。PvE 暂时用不上。
