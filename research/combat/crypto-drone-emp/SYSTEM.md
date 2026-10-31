# Crypto 大招 Drone EMP · 系统记录

批次 D，会话 `combat-d`，2026-10-31。只做了静态研究。

路径从 `research-src/s21-platform/scripts/` 开始。**EMP** = `vscripts/weapons/mp_ability_crypto_drone_emp.nut`（686 行），**EMP.txt** = `weapons/mp_ability_crypto_drone_emp.txt`，**CD** = `vscripts/weapons/mp_ability_crypto_drone.nut`。

> 主体是 Respawn 原版（工单号注释、`StatsHook_*`），有两处社区改动：地上护甲扣耐久的实现（EMP:465-507，注释署名 Cafe，用全图遍历代替缺失的原生查询）和警告粒子的移除循环（EMP:541-566，`R5RDEV-1` 标记）。

## 0. 概要

- **技能**：Crypto / 大招 / Drone EMP / `mp_ability_crypto_drone_emp`。必须先有战术无人机（[crypto-drone](../crypto-drone/SYSTEM.md)）。
- **一句话**：无人机原地蓄力 2.5 s，然后以无人机为中心 30 m 球形放 EMP：敌人护盾最多扣 50，玩家减速 0.35、转向变慢 0.7、屏幕干扰、小地图失灵 2 s；范围内敌方的陷阱 / 装置被溶解、扣血或关闭。友军也会被减速（Crypto 自己也会）。
- **分类**：好技能（控制 + 破盾）、系统（设备登记表 + 预警）。
- **可拆出的部件**：
  - 蓄力 + 范围预警（被波及的人提前看到 / 听到警告）→ 3.2.1 `DroneEMP` / `EMP_WarningFX`
  - 球形范围的效果结算（破盾 + 状态效果）→ 3.2.2
  - 设备登记表的三种反应（溶解 / 扣血 / 回调关闭）→ 3.2.3 `EMP_HitDevices`；共用文档 [`_shared/D-DEVICE-REGISTRY.md`](../_shared/D-DEVICE-REGISTRY.md)
  - 无人机被毁时退还大招 → 3.2.1 `OnThreadEnd`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 蓄力 | 脚本线程 `wait 2.5`；无人机播 `drone_EMP` 动画、挂蓄力粒子 `P_emp_chargeup` + 半径粒子 `P_emp_charge_radius_MDL`（控制点 5 = 0.49，推断是半径缩放）；蓄力音 | EMP:126-141 |
| 主人的状态 | 状态效果 `crypto_camera_is_emp` 2.5 s（HUD 进度）+ 网络布尔 `isDoingEMPSequence`（防重复） | EMP:138-141 |
| 预警 | 每帧找范围内的玩家：给他们加状态效果 `crypto_emp_warning`（客户端屏幕粒子 `P_emp_screen_player` + 脚下粒子 + 音效 `Wattson_Ultimate_G`）、身上挂 3P 粒子 `P_emp_body_human`（敌我都可见）；敌方队伍各播一次"EMP 要来了"语音（剩 1 s 以上才播） | EMP:509-613、617-660 |
| 爆炸 | 冲击效果表 `exp_drone_emp` + 世界粒子 `P_emp_explosion`（1.5 s 后删） | EMP:174-178、290-293 |
| 破盾 | 直接 `SetShieldHealth( 护盾 − min(50, 护盾 + 临时护盾) )`，**不是伤害**（伤害调用被注释掉了） | EMP:250-268 |
| 减速 / 转向慢 / 干扰 / 小地图 | 状态效果 `move_slow 0.35`、`turn_slow 0.7`、`emp 1.0`、`minimap_jammed`，都 2 s，前三个最后 1 s 渐出 | EMP:233-238 |
| 身上电流粒子 | `EMP_FX( P_emp_body_human, CHESTFOCUS, 1.5 s )`；悬浮载具挂 `driver` 用泰坦版 | EMP:212-226 |
| 设备 | 三张登记表（CD:2717-2769）：溶解 / 扣 100 血 / 调回调 | EMP:296-356 |
| 地上刚掉的护甲 | 15 s 内掉在地上的护甲耐久也扣 ≤50 | EMP:481-507 |

全部在服务端；客户端只有预警屏幕效果（EMP:617-660）。

## 2. 流程

```
大招满（180） + 有无人机 + 不在召回 + 不在 EMP 中
   │  两个入口：
   │   ① 本体按大招键 → OnWeaponPrimaryAttack（EMP:84-108）
   │   ② 在无人机视角里按开火 / 大招键 → Drone_TryEMP（CD:1038-1059）
   ▼
DroneEMP（EMP:111-294）
   0.0 s  蓄力开始：动画、粒子、音、主人状态；EMP_WarningFX 开始每帧更新预警名单
   2.5 s  爆炸：对范围内每个目标结算（3.2.2）；地上护甲；设备（3.2.3）
          无人机动画回 idle（主人在视角里）或 twitch
   4.0 s  删爆炸粒子
中途无人机被毁 / 主人离开 → OnThreadEnd：大招弹药退回满（EMP:147-163）
```

- **触发条件**：`OnWeaponAttemptOffhandSwitch`（EMP:54-81）——有 `crypto_has_camera`、不在召回、`isDoingEMPSequence` 为假。没有无人机时给提示"无人机没准备好"。
- 同一架无人机正在播 `drone_EMP` 动画时再调用直接返回（EMP:118-120）。
- **冷却**：`cooldown_type ammo`，弹夹 180、每秒 1 → 180 s（EMP.txt:19-29）；升级 `upgrade_core_ult_cooldown_reduction` → 150（EMP.txt mods）。
- **打断**：只有无人机被毁或主人销毁会中断，中断时退还大招。蓄力中主人可以离开视角，EMP 照常放。

## 3. 代码

### 3.1 入口

| 函数 | 行 | 做什么 |
|---|---|---|
| `MpAbilityCryptoDroneEMP_Init` | EMP:35-51 | 预缓存；注册 `isDoingEMPSequence`；客户端预警回调 |
| `OnWeaponPrimaryAttack_ability_crypto_drone_emp` | EMP:84-108 | 检查后 `thread DroneEMP` |
| `Drone_TryEMP`（在 CD） | CD:1038-1059 | 视角里按键：弹夹满才放，手动清零弹夹 |

### 3.2 核心逻辑

#### 3.2.1 蓄力和预警（EMP:111-170、509-613）

```
蓄力 2.5 s（写死在 EMP:140，不是 .txt）
预警名单 = 每帧 CryptoDrone_GetNearbyTargetsForEMPRange( 无人机 ) 里的玩家
  新进来的：加 crypto_emp_warning，挂 3P 粒子；敌方队伍首次进来且剩余 > 1 s → 语音
  出去的：去掉状态效果和粒子
  （NPC 不进预警名单，EMP:570）
```

#### 3.2.2 目标结算（EMP:180-278）

目标 = `CryptoDrone_GetNearbyTargetsForEMPRange`（CD:3085-3110）：
- 以**无人机**为中心，球形半径 = Neurolink 范围（1181.1 u；有被动升级时 ×1.25）；
- 玩家 + NPC；不同 realm 的去掉；不是人形大小、也不是战斗 NPC 的去掉；
- **不检查视线**（推断：隔墙也会中，要实测）。

对每个目标：
```
跳过：相位中（但 Alter 的"门"相位可以被打中，playlist crypto_emp_hits_alter_tac）、免疫技能
友军规则（playlist enable_emp_trap_friendly_fire，默认 true）：
   友方非玩家（友方陷阱等）跳过
   友方玩家：只吃状态效果，不扣盾      ← Crypto 自己也一样
   （开关为 false 时：友方全部跳过，只有 Crypto 自己吃状态效果）
状态效果（只给玩家；NPC 里只有训练假人吃减速）：
   turn_slow 0.7 / 2 s / 渐出 1 s（在载具里不加）
   emp       1.0 / 2 s / 渐出 1 s
   minimap_jammed 1.0 / 2 s
   move_slow 0.35 / 2 s / 渐出 1 s
破盾（敌方玩家和 NPC）：
   扣 = min( 50, 护盾 + 临时护盾 )；新护盾 = max( 护盾 − 扣, 0 )
NPC 没有护盾时：TakeDamage( 0 ) 发一个伤害事件（推断：让 AI 知道被攻击、转仇恨）
```

**对 PvE 最重要的一点**：一般 NPC **只被破盾，不被减速**（EMP:239-242 只给 `IsTrainingDummie` 加 `move_slow`）。HSD 要让 EMP 控制 AI 敌人，得自己加。

#### 3.2.3 设备（`EMP_HitDevices`，EMP:296-356；`EMP_Destroy`，EMP:665-685）

半径用**常量 `EMP_RANGE` 1181.1**（不随升级变，EMP:288）。只影响**敌方**、同 realm：

| 表 | 反应 | 谁登记了（grep 结果） |
|---|---|---|
| `empDestroy` | 发信号 `EMP_Destroy` → 登记时选的方式：溶解（默认，播 `Lifeline_Drone_Dissolve`）或 `TakeDamage( 满血 )`。`NoDissolve` 版只进表，不开监听线程，要设备自己处理信号 | 分身、Crypto 无人机、Gibraltar 护罩、Lifeline 治疗无人机 / Halo、Catalyst 尖刺图腾、Seer 飞镖、Loba 黑市、虚空环、弓箭大招核心 |
| `empDamage` | `TakeDamage( 100 )`，damageSourceId `mp_ability_crypto_drone_emp_trap` | 分身、跳板、空投发射器、Revenant 暗影护盾、Newcastle 城墙 / 移动盾、Rampart 掩体、Horizon 黑洞、Wraith 传送门、回声、地图无人机 |
| `empDisable` | 调登记时给的回调 | Newcastle 城墙（`CastleWall_OnEMPDisable`）；`sh_player_objects.gnut:20-41` 的通用接口 |

`EMP_Explosion_Common`（EMP:358-458）是一个"以任意实体为中心"的同款结算，本地**没有调用者**（推断：给 EMP 陷阱类用的，留着备用）。

### 3.3 客户端表现

- 被预警的玩家：屏幕粒子（控制点 1 = <1,1,1>）+ 脚下粒子 + 音效，直到爆炸或离开范围（EMP:617-660）。
- 被击中：`emp` 状态效果驱动屏幕干扰（引擎 / 公共代码，不在本文件）；`minimap_jammed` 让小地图失灵。
- Crypto 视角 HUD：`empFrac` 跟着 `crypto_camera_is_emp`（CD:2303）。

### 3.4 依赖的公共代码

- `CryptoDrone_GetNearbyTargetsForEMPRange`、`GetNearbyEMP*DeviceArray`、`GetNeurolinkRange`（CD）。
- `EMP_FX`（`vscripts/weapons/_weapon_utility.nut:3436`，在目标挂点上挂粒子若干秒；电弧星也用 `P_emp_body_human`）。
- 状态效果：`move_slow`、`turn_slow`、`emp`、`minimap_jammed`、`crypto_emp_warning`。电弧星（APEX-REPORT 2.2）和 Wattson 电网（批次 B，[`_shared/B-electric-emp.md`](../_shared/B-electric-emp.md)）用的是同一组状态效果。区别：电网 / 电弧星走 `Electricity_DamagedPlayerOrNPC`，会**击晕 NPC**；Crypto EMP 不走这条路，NPC 只被破盾。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 蓄力 | 2.5 | s | EMP:140 | 写死 | |
| 半径（人） | 1181.1（30 m） | u | CD:86、204、3087 | 球形，以无人机为中心 | |
| 半径升级 | ×1.25 | — | CD:88、3599 | 只对人，不对设备 | |
| 半径（设备） | 1181.1 | u | EMP:288 | | |
| 最大破盾 | 50 | 盾 | EMP:181（playlist `crypto_emp_damage`） | 含临时护盾 | |
| 移动减速 | 0.35 | 严重度 | EMP:237 | = 速度 ×0.65（电弧星 0.5 实测 ×0.498，APEX-REPORT 2.2，见 `_shared/B-electric-emp.md`） | |
| 转向减速 | 0.7 | 严重度 | EMP:234 | | |
| 效果时长 | 2.0 | s | EMP:234-237 | | |
| 渐出 | 1.0（小地图 0） | s | EMP:234-237 | | |
| 身上粒子 | 1.5 | s | EMP:226 | | |
| 设备扣血 | 100 | HP | EMP:322 | | |
| 地上护甲 | 掉落 15 s 内 | s | EMP:495 | | |
| 预警语音最晚 | 剩 1.0 s | s | EMP:530 | | |
| 爆炸粒子 | 1.5 | s | EMP:290 | | |
| 友军伤害开关 | true | — | playlist `enable_emp_trap_friendly_fire` | | |
| 打中 Alter 门相位 | true | — | playlist `crypto_emp_hits_alter_tac` | | |
| 冷却 | 180 | s | EMP.txt:19-29 | | |
| 冷却升级 | 150 | s | EMP.txt mods | | |
| fire_rate | 1.3 | — | EMP.txt:39 | | |

## 5. 未解决和要实测的

| 问题 | 为什么不确定 | 怎么测 |
|---|---|---|
| 减速 0.35 = 速度 ×0.65？ | 状态效果严重度到速度的映射在引擎 | 训练场：Crypto 自己会被 EMP 减速（友军规则包括本人）→ 无人机放在脚边放 EMP，记玩家冲刺速度随时间变化（2 s + 渐出 1 s 曲线） |
| 穿墙 | 目标查询没视线 | 无人机放在墙后，假人在墙这边，看假人护盾 |
| 训练假人减速 | 只有假人吃减速 | 同上，记假人位置变化（假人会走动的那种） |
| 预警粒子半径对不对 | 控制点 5 = 0.49 含义推断 | 看画面 |

## 6. HSD 实现

**未实现。** HSD 已有电弧星（`Ordnance.cs`，README 说"对玩家只做转向变慢和屏幕干扰，没做移动减速"）。

建议做法：
- 做成通用的 `EmpBurst( center, radius, chargeTime )`：蓄力期间给范围内的单位挂"预警"标记（AI 可以用来躲避——PvE 的有趣点），到点结算：破盾、减速、关掉敌方装置。
- 和 R5 的差别（要写进 `R5-DIFF-ARCHIVE.md`）：**HSD 应该给 AI 敌人加减速**（R5 只给玩家和训练假人），这是有意改动。
- 设备登记表照 `_shared/D-DEVICE-REGISTRY.md`：敌人的护盾发生器、炮台、无人机登记成"可被 EMP"，三种反应。
- 开关：`hsd.tf2.x.empSlowsAi`（默认 1）。
