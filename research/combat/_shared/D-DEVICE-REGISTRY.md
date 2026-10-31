# 公共部件 D：设备登记表（"哪些东西能被 EMP / 扫描影响"）

批次 D 共用，会话 `combat-d`，2026-10-31。只读脚本。

来源：`research-src/s21-platform/scripts/vscripts/weapons/mp_ability_crypto_drone.nut`（CD:2717-2769、3142-3155）、`mp_ability_crypto_drone_emp.nut`（EMP:296-356、665-685）、`vscripts/sh_player_objects.gnut:6-41`。

## 0. 概要

- **部件**：三张脚本管理的实体表 + 一个按半径查询的函数 + 一个"按表分别处理"的函数。
- **一句话**：每个技能建出的装置（陷阱、护盾、分身、无人机……）在创建时自己登记"被 EMP 时：溶解 / 扣血 / 调我的关闭函数"；放 EMP 的一方只需要按半径查三张表，分别处理。互相不用知道对方。
- **分类**：系统。
- **谁能用**：任何"范围内对敌方装置生效"的技能（EMP、破坏、黑客、扫描显示装置）。PvE：敌人的护盾发生器、炮台、无人机、刷怪器。

## 1. 实现手段

| 表 | 登记函数 | 被命中时 |
|---|---|---|
| `empDestroy` | `AddEMPDestroyDevice( ent, 方式 )`：登记 + 开线程等信号 `EMP_Destroy`；方式 = 溶解（默认）或 `TakeDamage( 满血 )`。`AddEMPDestroyDeviceNoDissolve`：只登记，设备自己处理信号 | 发信号 `EMP_Destroy {owner, source}` |
| `empDamage` | `AddEMPDamageDevice( ent )` | `TakeDamage( 100 )` |
| `empDisable` | `AddEMPDisableDevice( ent, 回调 )` | 调回调 |

同类登记还有：`AddSonarDetectionForPropScript`（声呐扫描能看到）、`AddNeurolinkDetectionForPropScript`（本地是空函数，CD:2717-2720）。

通用接口：`sh_player_objects.gnut:20` 一个函数同时决定"能否被加固、EMP 扣血、EMP 摧毁、EMP 关闭回调、摧毁方式"。

## 2. 流程

```
装置创建时：登记到一张或几张表（可以同时在 Damage 和 Destroy 两张里，例如分身）
放 EMP（EMP_HitDevices( owner, source, range, damageSourceId )）：
   for 表 in [Destroy, Damage, Disable]:
      for dev in 表.在半径内( source, range ):
         跳过友方、不同 realm
         按表处理；计数
装置销毁时：引擎的脚本管理数组自动去掉无效实体
```

## 3. 代码

```
EMP_HitDevices                       EMP:296-356
GetNearbyEMP{Destroy,Damage,Disable}DeviceArray   CD:3142-3155
   = GetScriptManagedEntArrayWithinCenter( 表, TEAM_ANY, 中心, 半径 )
EMP_Destroy（等信号的线程）           EMP:665-685
```

## 4. 参数 / 谁登记了

| 表 | 登记者（本地 grep） |
|---|---|
| Destroy（溶解） | Mirage 分身、Crypto 无人机、Gibraltar 护罩（`mp_weapon_bubble_bunker`） |
| Destroy（不溶解，自己处理） | Lifeline 老治疗无人机 / Halo、Catalyst 尖刺图腾、Seer 飞镖、Loba 黑市、虚空环、弓箭大招核心 |
| Damage（扣 100） | Mirage 分身、跳板、空投发射器、地图无人机（广告 / 物资）、Revenant 暗影护盾、Shadow form 护盾、Newcastle 城墙 / 移动盾、Rampart 加强掩体、Horizon 黑洞小人、Wraith 传送门接收端、回声定位器、物资 tick |
| Disable（回调） | Newcastle 城墙（`CastleWall_OnEMPDisable`）；`sh_player_objects` 通用接口 |

扣血固定 100（EMP:322）。

## 5. 未解决

- 本地 Crypto EMP 对设备的半径用常量 1181.1，不随升级（EMP:288）。是否正版行为不确定，意义不大。

## 6. HSD 实现

未实现。建议 `DeviceRegistry`：
```
enum EmpReaction { Destroy, Damage, Disable }
Register( CombatUnit u, EmpReaction r, Action<CombatUnit> onDisable = null )
IEnumerable<CombatUnit> Query( Vec3d center, double radius, Team notTeam )
```
`CombatSim.itemUnits` 已经是"技能建的单位"列表，加一个 `empReaction` 字段就够，不必另建表。
