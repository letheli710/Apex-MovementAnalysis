# 公共部件 C：放置物（直接放 / 扔出去落地）的生命周期

批次 C（combat-c），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/vscripts/weapons/`。

用到它的（本批）：Rampart 加强掩体（`mp_weapon_cover_wall.nut`，`cw`）、Rampart Sheila 放置炮台（`mp_weapon_mounted_turret_placeable.nut`，`pl`）、Gibraltar 护罩（`mp_weapon_bubble_bunker.nut`，`bb`）、Ballistic Whistler 插墙子弹（`mp_ability_debuff_zone.nut`，`dz`）。对照：批次 D 的设备登记表（`D-DEVICE-REGISTRY.md`，EMP / 扫描对放置物的影响，本文不重复）。

## 0. 概要

- **部件**：放置（引擎 object placement 或投掷落地）→ 生成实体 → 展开（动画 / 延迟）→ 生效 → 受伤规则 → 结束（到时 / 打爆 / 回收 / 超数量顶掉）。
- **一句话**：R5 的放置物都按这个模板写，差别只在每一步的参数。
- **分类**：系统。
- **可拆出的部件**：
  - 两种放置方式 → 3.2.1
  - 数量上限（新的顶掉最早的）→ 3.2.2
  - 受伤规则表（近战半血、爆炸、特定武器倍数）→ 3.2.3
  - 回收和返还 → 3.2.4
  - 挂在移动物体上 → 3.2.5

## 1. 实现手段（对照表）

| 步骤 | 加强掩体 | Sheila 炮台 | 护罩 | Whistler 插墙 |
|---|---|---|---|---|
| 放置 | 引擎 object placement（`ObjectPlacementHasValidSpot`，`cw:503-526`） | 同左（`pl:315-336`） | `ThrowDeployable` 800 u/s 落地（`bb:183-210`） | 追踪弹 `PlantStickyEntity`（`dz:398`） |
| 实体 | `prop_script` 底座（重甲） | `script_mover`（`pl:385`） | `prop_dynamic` 底座 | `prop_script` |
| 展开 | 0.3 s + 2 s 升盾（动画分段） | 立即 | 展开动画播完 | 1 s 布防 |
| 持续 | 无限（直到打爆 / 回收） | 无限 | 12 s | 5 s（等第一个触发） |
| 数量 | 4（`cw:643`） | 3（`pl:534`） | 1（推断，冷却限制） | — |
| 禁止重生区 | 256（`cw:35`） | 256（`pl:62`） | — | — |
| 近战 | 半血（两下打爆，`cw:1241-1245`） | 半血（`pl:930-934`） | — | — |
| 回收 | 长按 0.5 s，满血才能收（`cw:390-428`） | 捡回 +50% 弹量（`pl:1086`） | — | — |
| EMP | 盾扣血 | 停机 15 s（`pl:754-800`） | 摧毁 | — |
| 回合结束清理 | `TrapDestroyOnRoundEnd` | 同 | 同 | — |

## 2. 流程

```
[放置] 引擎预览模型 + 有效点检查 / 或投掷物落地回调
→ [生成] 实体、队伍、realm、主人、血量、可攀爬 / 可近战 / 可粘
→ [登记] 主人的列表（超数量 → 打爆最早的）、禁止重生区、EMP 表（D-DEVICE-REGISTRY）
→ [展开] 动画 / wait
→ [生效] 碰撞、触发器、伤害线程
→ [结束] OnThreadEnd：特效、声音、从列表移除、删禁止重生区、销毁 / 溶解
```

## 3. 代码

### 3.2.1 放置

- 引擎 object placement：`.txt` 的 `object_placement_*`（距离、坡度、离地、离边缘比例，例 `weapons/mp_weapon_cover_wall.txt:32-47`）+ 脚本拿 `GetObjectPlacementOrigin/Angles/Parent`。
- 投掷：`ThrowDeployable(weapon, params, speed, onPlanted)`，落地回调里自己找地面法线（护罩：向下 32 u 射线，和原角度差太大就不转，`bb:229-246`）。

### 3.2.2 数量上限（`cw:642-648`、`pl:534-542`）

```
owner.list.insert(0, new)
while len > max: old = list.pop()；old.TakeDamage(满血 + 10)；old.Destroy()
```

### 3.2.3 受伤规则

在 `OnDamaged`（结算前）改伤害：近战 → 最大血 / 2；某些爆炸来源（Prowler、Shadow 手）→ 最大血 / 2；升级 → 爆炸 ×0.5。`OnPostDamaged`（结算后）做表现：半血以下冒烟、归零爆炸特效。

### 3.2.4 回收

使用键长按（`CoverWall_TrackContinuousUse`，`cw:1141`）；条件函数 `CanReclaimWall`；返还 = 弹量 / 充能。

### 3.2.5 挂在移动物体上

放置点的 parent（`GetObjectPlacementParent`）或投掷物的 parent → `SetParent`；Rampart 底座建 mover 作动画参考。S21 的悬浮载具接口在 S3 dedi 上不存在，本地补丁把它注释掉（`cw:555`、`bb:285-286`）。

## 4. 参数

见上表和各技能 SYSTEM.md 第 4 节。

## 5. 未解决和要实测的

- 本地 S3 dedi 上悬浮载具挂载被注释掉后，放在载具上会怎样。PvE 无载具，不测。

## 6. HSD 实现

**已有部分**：`Throw.cs` 投掷物基类 `ThrownItem`（落地、弹跳）；`AWall` 是"扔出去落地展开"的一个例子。

建议：抽一个 `Deployable : ICombatEntity` 基类，字段对应第 1 节表的每一行（`placeMode`、`deployTime`、`life`、`maxCount`、`meleeHalf`、`reclaim`、`onExpire`），Rampart 掩体、Sheila 炮台、护罩、Whistler 感应区都继承它。HSD 的 AI 要能打这些放置物（`Targetable`），否则 R5 里"近战两下打爆"这类规则没有意义。
