# Newcastle 战术 Mobile Shield（移动护盾）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_shield_throw.nut`（2044 行），`txt` = `weapons/mp_ability_shield_throw.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Newcastle / 战术 / Mobile Shield / `mp_ability_shield_throw`。
- **一句话**：扔出一个小无人机，落地后离地 40 u 悬浮，两侧展开上下两片弧形护盾（各 500 HP），以 160 u/s 飞向扔出时瞄准的点；再按一次战术键就把目的地改成当前准星指的点（≤ 2000 u）。持续 20 s。
- **分类**：待定（防御）。**系统**价值高：这是一个"可指挥的地面移动体"——引擎的 `NonPhysicsTraversal`（前瞻、贴墙滑行、跨台阶、悬崖停、最低离地高度）+ 脚本只给目的地和朝向。PvE 里可以用来做伙伴单位 / 推进掩体 / 护送目标。
- **可拆出的部件**：
  - 可指挥的移动体（给目的地就自己走）→ 3.2.2 `MobileShield_EnableNonPhysicsTraversal`
  - 朝向规则（玩家在盾后面且朝同方向 → 盾面跟着玩家视线"平移"，否则转向目的地）→ 3.2.3 `MobileShield_Hover_Thread`
  - 指挥输入（再按一次 = 设新目的地）→ 3.2.4
  - 投掷 → 找更好起点（不卡墙）→ 3.2.1

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 投掷 | 引擎投掷物 500 u/s；重力 0（0–0.7 s）→ 0.6（0.7–2.8 s）→ 1.0 | `txt:100-109`。前 0.7 s 直飞 |
| 落地 | `OnDeployableShieldPlanted` → `DeployShieldOnGround_Thread` → `DeployMobileShield` | `nut:422-560` |
| 找起点 | 沿投掷记录的路径（`TrackProjetilePath`）往回 hull trace，找第一个不卡墙的点 | `nut:575-640` |
| 无人机 | `script_mover`，不实体、不可伤（`DAMAGE_NO`，"否则手雷会推它"） | `nut:640-700` |
| 护盾 | `CreateMobileShieldWall` × 2（上片、下片翻转 180°），每片血 500（升级 750） | `nut:800-805`、`nut:1249-1280` |
| 移动 | 引擎 `EnableNonPhysicsTraversal` + `SetMoveToPositionGroundNonPhysics(目的地, 地面实体)` | `nut:1179-1226`、`nut:1100-1110` |
| 朝向 | `SetDesiredYawDir(dir)` / `ClearDesiredYaw()`；转速 `SetYawAccelerationScale(180)` = 1 s 转一圈 | `nut:1120-1140` |
| 停住提示 | 引擎回调 `CodeCallback_ScriptMoverTraversalStopped(ent, isBlocked)` → HUD 显示"已停止" | `nut:1228` |
| 被动击退 | `PassiveNewcastle_StartShieldRepel`（升级"防线"：盾第一次碰到敌人时弹开他） | `nut:806` |
| 挡 ping | `CreateTraceBlockerVolume(半径 20)` | `nut:780` |
| 载具 | 主人在悬浮载具上时，盾挂在载具上 | `nut:705-720` |

## 2. 流程

```
按住（toss）→ 松开：
 ├ 目的地 = ShieldThrow_GetThrowDestination(fromInitialToss)：视线 trace ≤ 2000/cos(pitch)，pitch 限 ±70°
 ├ 记下目的地；开"按键提示"
 └ ThrowShield：500 u/s 投出；TrackProjetilePath 记录路径
落地 → DeployMobileShield：
 ├ 修正起点（向后 hull trace 出墙；或沿路径回退）
 ├ 无人机 mover + 上下两片护盾
 ├ MobileShield_Hover_Thread：EnableNonPhysicsTraversal（初速 = 投掷水平速度，≤ 300，2.5 s 内衰减到 160）
 └ 20 s：最后 3 s 警告特效 → 清理
运行中，再按战术键：
 ├ 客户端算目的地（PLAYERSOLID trace）→ ClientCallback_AttemptChangeShieldDirection
 ├ 若已停住 → 解除停住，并忽略悬崖检查 3 s
 └ Hover_Thread 下一帧：设新目的地 + 决定朝向
```

## 3. 代码

### 3.1 入口

`OnWeaponTossReleaseAnimEvent_ability_shield_throw`（`nut:230`）；按键 `AttemptChangeDirection`（客户端，`nut:1574`）→ `ClientCallback_AttemptChangeShieldDirection`（服务端，`nut:1611`）。

### 3.2 核心逻辑

#### 3.2.1 投掷与起点

`GetShieldThrowStartPos`：视点前 20、上 2.5（`nut:402`）。`GetShieldThrowVelocity`：朝向 × 力（`GraphCapped` 两端相同，等于没变，`nut:410`）。

#### 3.2.2 移动体参数（`MobileShield_EnableNonPhysicsTraversal`，`nut:1179`）

```
moveSpeed       = 160（升级 250）
checkDist       = 5      // 离目的地 5 u 内算到达
lookahead       = 75     // 前瞻距离
sideVelocity    = moveSpeed
maxWidthCorrect = 50     // 宽度修正速度
traceOffset     = 18
initialSpeed    = min(|投掷水平速度|, 300)，2.5 s 内衰减到 moveSpeed
decel           = 距目的地 150 内减速到 25
yawAccelScale   = 180（1 s 转 180°？注释说"full turn takes 1 second"）
ledge           = 悬崖检测：步长 64，落差 > 200 → 停；"忽略悬崖"3 s
sliding         = 贴墙滑行：最多 400，8 次边缘探测，目标 30，点积 0.999，深 100
stepOver        = 跨越 ≤ 40 高，检测 100，目标 15
minHeight       = 离地 40（检测 3000 内的地面）
gravity         = 0.125（高于最低高度时下落，也决定跨台阶的速度）
不和玩家、NPC 碰撞
```

这些全是引擎 `script_mover` 的能力，脚本只设参数。

#### 3.2.3 朝向规则（`MobileShield_Hover_Thread`，`nut:1013`）

每次有新目的地时判断一次：

```
dirToDest   = 盾 → 目的地（水平）
dirPlayerToDest = 玩家 → 目的地
dirToPlayer = 盾 → 玩家
if dot(dirToPlayer, 盾前向) < 0.2:          // 玩家在盾的背面
    if dot(dirToDest, dirPlayerToDest) > 0.85:   // 玩家和盾去同一方向
        dotView = dot(玩家视线, 盾前向)
        if dotView > 0.9:  strafe，朝向 = 玩家视线
        elif dotView < -0.4: strafe，保持盾当前朝向
        else: 不 strafe（转向目的地）
    else: strafe，保持当前朝向
else: 不 strafe（盾转向目的地）
strafe → SetDesiredYawDir(朝向)；否则 ClearDesiredYaw（引擎让盾面朝运动方向）
```

意思是：躲在盾后面推着走时，盾面一直挡在你前面；你跑到前面去指挥时，盾转头朝目的地走。

#### 3.2.4 指挥

- 目的地：`ShieldThrow_GetThrowDestination`（`nut:1780`），之后再往下 2000 找地面。
- 每次指挥都 `SetMoveToPositionGroundNonPhysics(dest, groundEnt)`；地面实体是移动平台时跟着平台走（ConVar `script_mover_traversal_mover_support`）。

### 3.3 客户端表现

- 目的地 AR 标记 `P_ar_ping_squad_CP`（`nut:1821` `ShieldThrow_CreateDestinationMarker`）。
- Waypoint 显示剩余时间；指挥提示 RUI；停住状态提示。
- 盾颜色友 `<40,210,255>` / 敌 `<255,100,12>`；无人机引擎、投影特效；最后 3 s 警告特效。

### 3.4 依赖

- 引擎 `script_mover` 非物理移动（`EnableNonPhysicsTraversal` 等）。
- `PassiveNewcastle_StartShieldRepel`（被动）。
- `trophy_system_ignores always`（拦截塔不拦它，`txt`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| 持续 | 20（最后 3 s 警告） | s | `nut:29-30`；playlist `newcastle_mobile_shield_duration` | |
| 移动速度 | 160（升级 250） | u/s | `nut:50,53` | |
| 初速上限 / 衰减 | 300 / 2.5 s | | `nut:1189-1190` | |
| 离地 | 40 | u | `nut:35` | |
| 护盾血量 | 每片 500（升级 750），共 2 片 | HP | `nut:49,52` | |
| 无人机血量 | 150（不可伤） | | `nut:48` | |
| 目的地距离 | 2000 / cos(pitch)，pitch ±70° | u | `nut:75`、`nut:1790` | |
| 悬崖 | 步长 64、落差 200、忽略 3 s | | `nut:33-34,76` | |
| 跨台阶 | 40 | u | `nut:1206` | |
| 贴墙滑行 | 400 | u | `nut:1200` | |
| 投掷 | 500 u/s；重力 0 → 0.6（0.7 s）→ 1.0（2.8 s） | | `txt:100-109` | |
| 冷却 | 弹匣 20、每次 20、回充 1/s → 20 s | | `txt:180-186` | |

## 5. 未解决和要实测的

1. **非物理移动的细节**（前瞻、滑行、跨越的实际效果）在引擎里。测法：R5 runner 里扔盾，指向墙角 / 台阶 / 悬崖，记录盾的位置轨迹。
2. 朝向转速：注释"1 秒转一圈"和参数 180 的单位（度/秒？）对不上，实测转身用时。
3. 上下两片护盾的形状和覆盖高度：模型 `newcastle_tac_hex_shield.rmdl`，要看模型或实测挡子弹的范围。

## 6. HSD 实现

**未实现。**

建议做法：

- `MobileShield : ICombatEntity`：位置、目的地、朝向、两片 `IWallBlocker`（复用 `AWall` 的平板判定，`Tacticals.cs:78`，宽高按模型实测后定）。
- 移动：每帧向目的地走 160 u/s；前方 75 u 有墙 → 沿墙切线方向滑；前方台阶 ≤ 40 → 抬高；前方落差 > 200 → 停。用 `CombatSim.WorldRay` 做这几条 trace。
- 朝向：照 3.2.3 的判断写，规则不依赖引擎。
- 指挥：战术键再按一次 → 准星 trace 2000 → 新目的地。
- 这套"给目的地就走"的移动体可以直接给以后的 PvE 伙伴 / 护送目标用；建议写成 `GroundMover` 公共类。
- 开关：`hsd.combat.mobileShield.*`。
