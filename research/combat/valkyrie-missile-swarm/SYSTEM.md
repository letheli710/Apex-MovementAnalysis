# Valkyrie 战术 Missile Swarm 导弹群：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

出处路径从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_ability_valk_cluster_missile.nut`，`txt` = `weapons/mp_ability_valk_cluster_missile.txt`，`upg` = `vscripts/weapons/mp_ability_valk_cluster_missile_upgraded.nut`，`wu` = `vscripts/weapons/_weapon_utility.nut`。

## 0. 概要

- **技能**：Valkyrie / 战术 / Missile Swarm / `mp_ability_valk_cluster_missile`（升级见 `upg`）。
- **一句话**：举起肩炮瞄准，前方地面出现一组目标圈；按开火后 12 枚小导弹先"抛"出去 0.55–0.85 s，再点火沿弯曲路线飞向各自的目标圈，每枚爆炸 15 伤害、半径 150 u；被打中的人或 NPC 晕眩 2 s（移动 ×0.75 → 淡出 1.5 s），给 Valk 高亮 1.5 s。同一个人 5 s 内再被打中只吃 20% 伤害。
- **分类**：**好技能**（区域伤害 + 控制，对 AI 一样有用）＋ **可视化**（地面目标圈预览、"抛—点火—弯飞"的导弹路径、敌方威胁指示）＋ **系统**（"网格目标点 + 按行列错开到达时间"的齐射调度；"抛射体 → 导弹"两段式投射物；对同一目标的递减伤害）。
- **可拆出的部件**：
  - 网格落点生成（前方 N 行 × M 列，贴地）→ 3.2.1 `GetValkTacTargets`
  - 齐射时间表（距离→飞行时间对数映射，再按行 / 列加延迟）→ 3.2.2
  - 两段式投射物（惰性抛射 → 点火导弹，"展开—收拢"弯路径 + 摆动）→ 3.2.3 `Thread_WaitForIgnition`
  - 同目标递减伤害（5 s 内后续命中 ×0.2）→ 3.2.4 `ValkTac_OnEntityDamagedByPlayer`
  - EMP 晕眩（move_slow / turn_slow 带淡出）→ 3.4，公共部件见 `_shared/B-electric-emp.md`（同一个 `GiveEMPStunStatusEffects`）和 `_shared/E-STATUS-EFFECT.md`
  - 落点预览圈 + 对敌威胁指示 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 瞄准时的目标圈 | 客户端粒子 `P_valk_rckt_AR_marker`，每帧移到落点 | `nut:317-363`，只画给自己 |
| 锁定后的目标圈 | 服务端粒子实体 `P_valk_rckt_AR_lock`，只加进 Valk 的 realm | `nut:386-426`，最多 5 s |
| 第一段"抛射" | `FireWeaponGrenade`，`MOVETYPE_FLYGRAVITY`，寿命 = 抛射时间；**这一段碰撞无效** | `nut:816-830`、`nut:1066` |
| 第二段导弹 | 抛射体销毁时在它的位置 `FireWeaponMissile`，用引擎的 `InitMissileExpandContract` 弯路径 + `InitMissileWiggleSettings` 摆动 | `nut:875-971` |
| 爆炸伤害 | 脚本 `Explosion()`，内外半径都 150，伤害 15，damageSourceId `mp_ability_valk_cluster_missile` | `nut:1087` |
| 递减伤害 | 按 damageSourceId 注册的伤害回调，记录"Valk → 目标 → 上次命中时间" | `nut:148`、`nut:162-195` |
| 晕眩 / 减速 | 状态效果 `emp`（0.2）+ `move_slow` 0.75 + `turn_slow` 0.0，2 s，淡出 1.5 s | `nut:203-204`、`wu:2866-2887` |
| 身上电流特效 | `EMP_FX( FX_EMP_BODY_HUMAN, …, "CHESTFOCUS", 2 )` | `nut:209` |
| 高亮被打中的人 | 状态效果 `valk_tac_scan` 1.5 s + 客户端只在攻击者有 `PAS_VALK` 时高亮 | `nut:210`、`nut:219-246` |
| 对敌预警 | 服务端在落点 +55 u 放一个只对 Valk realm 可见的 prop，targetname `valk_tac_warning_entity`；客户端看到它就开威胁箭头 | `nut:438-467`、`nut:495-643` |
| 尾焰 | 抛射段 `P_valk_rckt_stg1`、导弹段 `P_valk_rckt_stg2`，挂 `exhaust` 点 | `nut:131-132`、`nut:1038-1053` |
| 屏幕震动 | 开火时客户端 `ClientScreenShake(10,100,0.5)`；每次爆炸 `CreateShake(pos,16,140,0.25,800)` | `nut:669`、`nut:1088` |
| 声音 | 开火 `Valk_ShoulderRocket_Fire_Comp_1P/3P`；第一枚点火 `blastoff`；爆炸 `Explo_Valk_ShoulderRocket_Impact_Sustained`（5 s 防抖）；被打中的玩家 `Arcstar_visualimpair` | `nut:670-684`、`nut:912-914`、`nut:1081`、`nut:207` |

**客户端 / 服务端**：落点预览、威胁箭头、高亮判断是客户端；抛射、导弹、爆炸、伤害回调、锁定圈是服务端。开火函数两边都跑（客户端只做预测的第一次）。

**怀疑点**：`nut` 带大量 Respawn 原注释（`Dklein`、R5DEV 单号）、`nut:847-852` 有被剥掉的 `#if` 空行，像是官方源码直接带过来，不像 SDK 重写。网格点生成 `GetWeaponMissileMultipleTargets` 和导弹弯路径 `InitMissileExpandContract` 是**引擎原生函数**，脚本里看不到实现，见第 5 节。

## 2. 流程

```
切出战术 ──(OnWeaponAttemptOffhandSwitch: ValkCanFireTactical == YES)──▶ 瞄准
瞄准：客户端每帧画 N 个目标圈；服务端每 0.1 s 检查还能不能放，不能就收起
按开火（burst 12 枚，fire_rate 25 → 每 0.04 s 一枚，共约 0.48 s）
  burstIndex 0：锁定落点表（weapon.w.valkTac_targetData），结束瞄准线程，加 block_melee 模组
               服务端：画锁定圈、喊话、TrackingVision POI
  每一枚：抛射体（0.55–0.85 s，惰性）→ 销毁时点火 → 导弹弯飞 → 碰撞 → 爆炸
  最后一枚：返回当前弹量（一次扣光）
冷却：弹匣 300，回充 12/s → 25 s；必须回满才能再放
```

- **触发条件**（`ValkCanFireTactical`，`nut:1011-1035`）：弹匣必须是满的；不在相位中；没在 `skyward_embark`（大招起飞）状态；头顶净空 ≥ playlist `valk_tac_verticalClearanceRequired`（默认 0 = 不检查，检查时向上打 300 u 射线）。净空不够时提示 `#CLUSTER_MISSILE_CLEARANCE_FAIL` 并放音效（`nut:998-1003`）。
- **瞄准中被打断**：`ValkTac_CheckForReasonToDeactivate`（`nut:271-296`）每 0.1 s 查一次，条件不满足就清掉副手 / 切回主武器。倒地（`BleedOut_OnStartDying`）、销毁结束线程。
- **近战取消**：`offhand_cancelled_by_melee 1`（`txt:15`）；开火后加 `block_melee_when_shooting` 模组把它改成 0（`txt:144-148`、`nut:666`），也就是**开火后近战不能中断齐射**，停用时移除（`nut:310-311`）。
- **跳伞中**：射程 250 m、飞行时间 0.3–5 s（`nut:20-22`、`nut:379`、`nut:786-787`）。
- **升级**（被动 `PAS_EXTRA_SWARM_MISSILE`，`upg:12-40`）：给武器加 `upgrade_core_valk_tac_increase_missiles_1` 模组（同时有战术冷却被动则换成 `_2` 并移除冷却模组），按原百分比换算弹量；网格从 2 侧步 × 4 前步变成 3 × 4，扇出系数 0.1 → 0.06（`nut:23-26`、`nut:373-377`、`nut:737`）。
- **结束**：`ShowFinalLocsThread` 在还有导弹在飞时保留锁定圈，最多 5 s（`nut:420-425`）。

## 3. 代码

### 3.1 入口

- `MpAbilityValkClusterMissile_Init`（`nut:135-159`）：预载模型 / 粒子；服务端按 damageSourceId 注册伤害回调；客户端注册警告实体创建回调、本地造成伤害回调、`valk_tac_scan` 状态效果开关回调。
- 武器回调（`txt:36-42`）：`OnWeaponAttemptOffhandSwitch`、`OnWeaponActivate`、`OnWeaponDeactivate`、`OnWeaponPrimaryAttack`、`OnProjectileCollision`、`OnClientAnimEvent`。

### 3.2 核心逻辑

#### 3.2.1 网格落点 `GetValkTacTargets`（`nut:366-382`）

```
attackPos, attackDir = 武器开火点和方向
(forwardSteps, sideSteps) = 有升级 ? (4, 3) : (4, 2)
maxRange = 跳伞 ? 250 m : 125 m (4921 u)
targets = weapon.GetWeaponMissileMultipleTargets(attackPos, attackDir, owner,
           forwardSteps, sideSteps, STEP_FORWARD=185, STEP_SIDE=163.16, STEP_HEIGHT=250,
           INITIAL_DELAY=0.75, IN_ROW_DELAY=0.05, ROW_TO_ROW_DELAY=0.15, maxRange, MIN=400)
每个 target：pos、normal、delay
```

- 原生函数，返回贴地的点（推断：从准星落点出发，按"先上 250 再横 / 前走"的步进找地面，`nut:31` 注释"how far we step up before stepping to the side or forward"）。
- 注释写总数 = `(1 + sideSteps*2) * (forwardSteps+1)`（`nut:30`），= 5 × 5 = 25（默认）/ 7 × 5 = 35（升级），**但只用前 `burst_fire_count` 个**（12 / 20，`nut:704`）。本地化写的是"4x3 改成 3x5"（`localization_english.txt:9545`），和脚本的行列算法对不上，见第 5 节。

#### 3.2.2 齐射时间表（`nut:777-813`）

```
rocketsInRow = 1 + sideSteps*2            // 5（默认）/ 7（升级）
row = burstIndex / rocketsInRow；indexInRow = burstIndex % rocketsInRow
distance = |target - attackPos|
travelTime = GraphCapped( ln(distance), ln(400), ln(maxRange), tMin, tMax )   // 地面 2–4 s，跳伞 0.3–5 s
travelTime += row*0.15 + indexInRow*0.05
lob = 0.75 + U(-0.2, 0.1)                  // 抛射时间 0.55–0.85 s
rocketTime = travelTime - lob
speed = (distance - 200) / rocketTime * 3  // "200" 是抛射段大约走的距离（nut:798 注释）
phase2Time = 0.1·rocketTime；phase2To3Time = 0.16·rocketTime；phase3ToTarTime = 0.1·rocketTime；phase1 = phase1To2 = 0.01
```

意思：远的落点飞得久，但对数映射让 400 u 和 4921 u 只差 2 s；同一行左右错开 0.05 s、行与行错开 0.15 s，形成"一排排往前炸"的节奏。速度是按"要在 travelTime 到"反算出来的（×3 是经验系数，推断是因为弯路径比直线长）。

#### 3.2.3 两段式投射物

**抛射段**（`nut:727-831`）：

```
flatRight = 水平右方向
swarmVector = normalize( dir + flatRight * fanAdjustments[i] * fan )   // fan = 0.1 / 升级 0.06
swarmVector.z = 0.7，再 normalize                                      // 一律往斜上方扇出
抛射出生点 = attackPos + flatRight*(-18)（左侧）或 *(+10)（右侧）       // 模拟左右两个发射舱
抛射速度 = (swarmVector + <0,0,0.75>) * 0.04*(0.8+lob)
角度：朝前、抬 15°；角速度 480；寿命 = lob；碰撞直接 return（惰性）
```

`fanAdjustments`（`nut:87-109`）= −1, 1, −2, 2, … −9, **10**, −11, 11（第 18 项是 10 不是 −10，推断是笔误，结果 index 16、17 都往右偏）。

**导弹段**（`Thread_WaitForIgnition`，`nut:875-971`）：抛射体销毁（寿命到）时触发 `OnThreadEnd`：

```
missile = FireWeaponMissile(pos = grenade 当前位置)
grace 0.5 s；换模型；挂尾焰
phase1Vec = normalize(swarmVector)*0.6     // 继续往扇出方向
phase2Vec = normalize(dir2d + <0,0,0.7>)*0.8   // 转向目标并抬升
phase3Vec = dir2d*0.9                       // 水平冲向目标
// 防撞：
如果 phase2 起止连线撞墙：phase2Vec *= clamp(fraction-0.5, 0.1, 1)，关竖直摆动，水平摆动上限 0.1
否则如果 phase2End→phase3End 撞墙：phase2Vec *= 0.4，phase2To3Time = 0.1，同样减摆动
InitMissileExpandContract(speed, phase1..3Vec, 各阶段时间, curTar)
摆动：水平速度 0.2–0.3、时间 0.1–0.3；竖直速度 0.1–0.2、时间 0.2–0.3；easeIn 0.7；第 9 枚起延迟 0.2 s
```

#### 3.2.4 爆炸和递减伤害

- `OnProjectileCollision`（`nut:1057-1093`）：类名是 `grenade` 就忽略；否则
  `Explosion(pos, owner, owner, dmg=valk_tac_dmg(15), heavyArmor=15, inner=150, outer=150, …, force=10, explosive, mp_ability_valk_cluster_missile, "exp_valk_rocket")`，再删掉对应的预警 prop、震屏、销毁导弹、在飞计数 −1。
- `ValkTac_OnEntityDamagedByPlayer`（`nut:162-215`）：

```
last = table[valk][hitEnt]（没有就是 0）；table[valk][hitEnt] = now
if now < last + 5 且 hitEnt 是玩家/NPC: damage = floor(damage * valk_tac_followup_dmg_mult(0.2))
if hitEnt 是 Revenant 暗影护盾: hitEnt = 它的主人
if 玩家/NPC: emp(0.2, 2 s, 淡出 1.5) + move_slow 0.75 + turn_slow 0.0 + 电流特效 2 s + valk_tac_scan 1.5 s
```

注意：每次命中都刷新"上次时间"，所以只要 5 s 内持续被打，**只有第一枚吃满伤害**。晕眩每次命中都重加（时长不叠加，推断由状态效果系统按最大值处理）。

### 3.3 客户端表现

- **瞄准预览**（`ValkTacShowTargetLocsThread`，`nut:317-363`）：开始时按目标数建粒子（距离剔除系数 999，修 R5DEV-253916），之后每帧重算网格、更新粒子位置和朝向。只有本地视角玩家看得到。
- **锁定圈**（`ShowFinalLocsThread`，`nut:386-426`）：服务端粒子实体只放进 Valk 的 realm（`RemoveFromAllRealms` + `AddToOtherEntitysRealms(player)`）。
- **对敌威胁指示**（`ValkTacManageThreatIndicator`，`nut:526-643`）：取最近的预警实体；距离 ≤ 150×1.3 = 195 u、不在相位、从落点到眼睛射线不被挡，就显示手雷威胁箭头（挂在 cockpit `CAMERA_BASE`，偏移 <25,0,−4>），看不见后再留 0.25 s。注意预警 prop 也只加进 Valk 的 realm（`nut:442-443`），推断"realm"在这里是队伍 / 平行世界隔离，敌人在同一个 realm 才看得到（第 5 节）。
- **高亮**（`nut:219-246`）：本地玩家造成伤害且有 `PAS_VALK` 时，记录目标高亮到期时间 = now + 1.5；目标同时有 `valk_tac_scan` 才高亮。

### 3.4 依赖的公共代码

- `GiveEMPStunStatusEffects`（`wu:2866-2887`）：加 `turn_slow` 和 `move_slow` 两个计时状态效果（时长、淡出），玩家身上记下来以便相位时清掉。
- `EMP_FX`（`wu:3436` 起）：身体挂点粒子，死亡 / 相位 / 新 EMP_FX 时结束。
- `Explosion()`、`StatusEffect_AddTimed`、`TrackingVision_CreatePOI`、`PlayerUsedOffhand`：通用。
- 引擎：`GetWeaponMissileMultipleTargets`、`MissilePath_GetExpandContractPositionAtTime`、`InitMissileExpandContract`、`InitMissileWiggleSettings`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| MAX_ATTACK_RANGE | 125 m = 4921 | u | `nut:16` | 网格最远距离 | 远了覆盖面大、飞行慢 |
| MIN_ATTACK_RANGE | 400 | u | `nut:17` | 最近距离，避免炸自己 | 小了可能自伤 |
| MIN / MAX_TRAVEL_TIME | 2 / 4 | s | `nut:18-19` | 距离→飞行时间映射两端 | 拉开则远近差更明显 |
| 跳伞射程 / 时间 | 250 m / 0.3–5 | u / s | `nut:20-22` | 跳伞时 | — |
| SIDE_STEPS / FORWARD_STEPS | 2 / 4 | 步 | `nut:28-29` | 网格每行 1+2×2=5 列、5 行 | 只用前 burst 个 |
| 升级 SIDE / FORWARD | 3 / 4 | 步 | `nut:23-24` | 每行 7 列 | — |
| STEP_HEIGHT | 250 | u | `nut:31` | 找地面时先向上的高度 | 推断：影响能否落到台阶上 |
| STEP_SIDE | 163.16 | u | `nut:32` | 列距 | 大了更散、密度低 |
| STEP_FORWARD | 185 | u | `nut:33` | 行距 | 同上 |
| FANOUT_ON_LAUNCH | 0.1（升级 0.06） | — | `nut:25-26` | 抛射扇出系数 | 大了起飞更散 |
| fanAdjustments | ±1…±11（20 项） | — | `nut:87-109` | 每枚的左右偏移倍数 | — |
| MISSILE_SPEED / MISSILE_APEX_HEIGHT | 1600 / 400 | u/s / u | `nut:34-35` | **未使用**（脚本里没引用） | — |
| GRENADE_LOB_TIME | 0.75（随机 −0.2…+0.1） | s | `nut:36`、`nut:794` | 抛射段时长 | 长了起飞更"慢悠悠" |
| 抛射速度系数 | 0.04×(0.8+lob) | — | `nut:795` | 抛射初速（乘方向） | 见第 5 节 |
| 抛射出生偏移 | 左 −18 / 右 +10 | u | `nut:762-769` | 模拟两个发射舱 | — |
| 速度系数 | (dist−200)/t×3 | u/s | `nut:798-799` | 导弹速度 | — |
| 阶段时间比例 | 0.1 / 0.16 / 0.1 | ×rocketTime | `nut:805-807` | 弯路径各段 | — |
| phase 向量系数 | 0.6 / 0.8 / 0.9，抬升 0.7 | — | `nut:746-748` | 弯路径形状 | — |
| 摆动 | 水平 0.2–0.3 / 0.1–0.3 s；竖直 0.1–0.2 / 0.2–0.3 s；easeIn 0.7 | — | `nut:929-939` | 导弹抖动 | — |
| 摆动起始延迟 | projectileIndex ≥ 8 时 0.2 | s | `nut:964-965` | — | — |
| grace period | 0.5 | s | `nut:919` | 导弹出生后不碰撞 | — |
| IN_ROW_DELAY | 0.05 | s | `nut:49` | 同行错开 | — |
| ROW_TO_ROW_DELAY | 0.15 | s | `nut:50` | 行间错开 | — |
| INITIAL_DELAY | 0.75 | s | `nut:52` | 传给原生网格函数 | 推断：填进 target.delay |
| EXPLOSION_DAMAGE | 15（playlist `valk_tac_dmg`） | HP | `nut:44`、`nut:1069` | 每枚伤害 | — |
| EXPLOSION_RADIUS | 150（内外相同） | u | `nut:47`、`nut:1087` | 爆炸半径；内外一样 = 半径内不衰减（推断） | — |
| 爆炸推力 | 10 | — | `nut:1087` | — | — |
| EXPLOSION_FOLLOWUP_FACTOR | 0.2（playlist `valk_tac_followup_dmg_mult`） | × | `nut:45`、`nut:192` | 5 s 内后续命中伤害倍数 | 15→3（floor） |
| EXPLOSION_FOLLOWUP_TIME | 5 | s | `nut:46` | 递减窗口 | — |
| STUN_DURATION | 2.0 | s | `nut:38` | 晕眩时长 | — |
| STUN_EASEOUT | 1.5 | s | `nut:39` | 淡出 | — |
| STUN_MOVESLOW | 0.75 | 严重度 | `nut:41` | `move_slow` 严重度（按 APEX 2.2 实测的语义（严重度 s → 速度 ×(1−s)）= 速度 ×0.25，见 `_shared/B-electric-emp.md`） | — |
| STUN_TURNSLOW | 0.0 | 严重度 | `nut:42` | 不减转向 | — |
| emp 严重度 | 0.2 | — | `nut:203` | 屏幕干扰（推断） | — |
| HIGHLIGHT_DURATION | 1.5 | s | `nut:27` | 被打中者高亮 | — |
| 威胁指示距离 | 150×1.3 = 195 | u | `nut:594` | 敌人多近看到箭头 | — |
| 锁定圈最长 | 5 | s | `nut:423` | — | — |
| 爆炸音效防抖 | 5 | s | `nut:1080` | — | — |
| fire_rate | 25 | 发/s | `txt:10` | 每 0.04 s 一枚 | — |
| burst_fire_count | 12（升级 20） | 枚 | `txt:17`、`txt:128` | 导弹数 | — |
| ammo_clip_size / per_shot | 300 / 25（升级 400 / 20） | — | `txt:20-24`、`txt:122-126` | 一次用光 | — |
| regen_ammo_refill_rate | 12（升级 20；升级+冷却被动 26.667） | /s | `txt:26`、`txt:127`、`txt:139` | 冷却 25 s / 20 s / 15 s | — |
| deploy_time | 0.3 | s | `txt:30` | 举炮 | — |
| projectile_launch_speed | 4000 | u/s | `txt:71` | 推断：抛射初速的倍数 | 见第 5 节 |
| projectile_air_friction | 1268 | — | `txt:78` | 推断：抛射段很快减速 | — |
| projectile_gravity_scale / _time_2 | 1 / 0.504 | — / s | `txt:77-79` | — | — |
| damage_near_value / explosionradius（.txt） | 8 / 80 | HP / u | `txt:32-33` | 推断：被脚本 `Explosion()` 覆盖，只可能用于导弹直撞 | 见第 5 节 |
| 冷却 mod | armor ×1.25 / ×1.5；paused ×0；staging ×5 | × | `txt:156-184` | 通用 | — |

## 5. 未解决和要实测的

1. **网格到底是几行几列**：脚本行列算法给 5 列 × 5 行取前 12 个（5+5+2），本地化说"4x3 → 3x5"。`GetWeaponMissileMultipleTargets` 是原生的。**测**：火力训练场平地，脚本里打印 `weapon.w.valkTac_targetData` 的 pos（或开 `DebugDrawSphere`），俯视截图；升级再测一次。
2. **抛射段初速**：`0.04×(0.8+lob)` 很小，推断引擎把它乘以 `projectile_launch_speed 4000`（≈250 u/s 量级）。**测**：AgentLink 每 0.1 s 记录抛射体位置（W4 `w4_probe.py` 的 `scripted` 模式可借）。
3. **导弹直撞伤害**：`.txt` 的 8 伤害 / 80 半径是否用于 `projectileImpact`。**测**：把假人放在导弹路径上（不在落点），看伤害数。
4. **半径内是否衰减**：内外半径都是 150，推断半径内满伤。**测**：在落点中心和 140 u 处各放假人比较。
5. **move_slow 0.75 的实际效果**：是"减 75%"还是"剩 75%"。**测**：打中自己（单人可设友伤或打 NPC 记录速度），对照 APEX-REPORT 2.2 的电弧星减速实测法。
6. **递减伤害按玩家统计**：表的键是 Valk，两个 Valk 不共享。PvE 单人不影响。
7. **预警 prop 只在 Valk realm**：敌人能否看到威胁箭头取决于 realm 含义。PvE 不重要，列着。
8. 服务端代码看起来是官方原样（见第 1 节），SDK 重写嫌疑低。

## 6. HSD 实现

**未实现**。`HSD-Unity/Assets/HSD/Game/Runtime/Combat/` 里没有导弹齐射；现有能用的零件：

- `CombatSim` 的爆炸（线性衰减 + 推力 + 墙挡，README 表）——可以直接用；R5 是内外半径相同（不衰减），用 `inner = outer = 150`。
- `CombatSim.Items.cs:354` 的 `Emp(u, t, turnSlow)` + `CombatUnit.slowScale/slowUntil`（`CombatCore.cs:76-86`）：现在是电弧星专用、没有淡出。建议先做 `_shared/E-STATUS-EFFECT.md`（批次 E）描述的通用状态效果层，带淡出的减速放进去，晕眩用它。
- `Throw.cs` 投掷物基类：抛射段可以用它（短寿命、不碰撞）。

建议做法（新文件 `Combat/Barrage.cs`，类 `MissileSwarm`）：

1. **落点**：自己实现网格（不用猜原生）：从准星落点（射线到地面，限制 400–4921 u）为第一行中心，向前每 185 u 一行、向左右每 163 u 一列，每点从上方 250 u 往下打射线贴地。先按"5 列 × N 行取前 12"做，第 5 节第 1 条测完再改。
2. **时间表**：照搬 3.2.2 的公式（对数映射 + 行列延迟）。
3. **路径**：不用复刻引擎的 expand-contract；用三次贝塞尔（起点 → 起点 + 扇出方向×抬升 → 目标上方 → 目标）按 travelTime 匀速插值，加小幅正弦摆动，视觉接近即可。差别记进 `R5-DIFF-ARCHIVE.md`（"导弹路径用贝塞尔近似"）。
4. **伤害**：15 / 150 u / 5 s 内同目标 ×0.2。PvE 里建议做成开关 `missileSwarm.followupMult`（默认 0.2 = R5；PvE 打怪群时这个规则只影响同一只怪，保留）。
5. **对 AI 的晕眩**：2 s 减速（R5 0.75 严重度）+ 1.5 s 淡出；AI 在晕眩期间可以加"打断攻击 / 硬直"——这是 HSD 新增，做开关 `missileSwarm.stunInterruptsAi`，默认关。
6. **表现**：瞄准时地面画目标圈（R5 每帧更新），锁定后变色保持到最后一枚落地；抛射段小尾焰、点火后大尾焰。
7. **冷却**：25 s、必须充满（R5 是弹量系统，HSD 可用 `Charges` 一格 25 s）。

开关建议：PlayerPrefs `hsd.combat.valk.*`（`count`、`followupMult`、`stunInterruptsAi`、`upgraded`）。
