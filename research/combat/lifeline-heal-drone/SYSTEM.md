# Lifeline 战术 D.O.C. Heal Drone · 系统记录

批次 D（伙伴 / 无人机 / 分身），会话 `combat-d`，2026-10-31。只做了静态研究（读脚本和 `.txt`），没开游戏。

来源路径都从 `research-src/s21-platform/scripts/` 开始。主脚本简写为 **FM** = `vscripts/weapons/mp_ability_lifeline_follow_medic.nut`，**FM.txt** = `weapons/mp_ability_lifeline_follow_medic.txt`。

> **先看这一条**：FM 的服务端部分**几乎可以确定是 SDK 社区重写的**（证据见 5.1）。下面的公式是"本地这份脚本"的行为，不一定等于 S21 正版。HSD 用它当"一套能用的跟随系统"没问题；要说"贴合 R5"，先做 5.2 的实测。

## 0. 概要

- **技能**：Lifeline（Revived 版）/ 战术 / D.O.C. Heal Drone / `mp_ability_lifeline_follow_medic`。配套的"指令"副武器 `mp_weapon_following_medic_orders`（`vscripts/weapons/mp_weapon_following_medic_orders.nut`）。
- **一句话**：扔出一架无人机，自动跟在准星对着的队友（没有就跟自己）身后上方，20 s 内给 256 u 范围内掉血的队友拉治疗绳回血，每秒 8；之后可以再按战术键改派给另一个队友，按角色键召回。
- **分类**：系统（主）、可视化（次）。效果（回血）本身简单。
- **可拆出的部件**：
  - 指派目标（锥内选最正的队友，没有就选自己）→ 3.2.1 `FollowMedic_FindBestTarget` / `TryDroneAssignOrRecall`；共用文档 [`_shared/D-TARGET-ASSIGN.md`](../_shared/D-TARGET-ASSIGN.md)
  - 跟随运动（偏移目标点 + 比例速度 + 指数平滑）→ 3.2.2 `FollowMedic_MoveThread`；共用文档 [`_shared/D-FOLLOW-MOTION.md`](../_shared/D-FOLLOW-MOTION.md)
  - 断线瞬移（超距 / 断视线 1 s）→ 3.2.3 `FollowMedic_Teleport`
  - 飞行姿态（速度→前倾、转向→侧倾）→ 3.2.2 末尾
  - 范围治疗 + 治疗绳（两根绳分别给本人和别人看）→ 3.2.4 / 3.3
  - 寿命 + "治疗中延后消失" → 3.2.5 `FollowMedic_LifetimeThread`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 / 来源 |
|---|---|---|
| 无人机本体 | `script_mover` 实体，不碰撞（`solid 0`），不受伤（`DAMAGE_NO`） | FM:558-585。**不是** vehicle（S3 老无人机用的是 HoverVehicle 挂点，见 5.1） |
| 跟随移动 | 服务端每帧线程算速度，`NonPhysicsMoveTo( next, dt )` 一帧一帧挪 | FM:801-870 |
| 姿态（前倾 / 侧倾） | 每帧 `NonPhysicsRotateTo( <pitch, yaw, roll>, dt )` | FM:864-868 |
| 瞬移 | `SetOrigin` 直接搬 + 起点放拖尾粒子 `P_LLR_DOC_trail`（朝向终点）+ 出发 / 到达音效 | FM:792-799 |
| 选目标 | 服务端 0.1 s 一次扫描，结果写进玩家网络变量 `follow_drone_bestTarget` | FM:416-424 |
| 指派 / 召回 | 客户端按键回调 → `Remote_ServerCallFunction` → 服务端 `TryDroneAssignOrRecall`；客户端也同时跑一遍（预测） | FM:1101-1145、438-481 |
| 回血 | `EntityHealResource_Add( player, 时长, 8/s )`，引擎按时间加血；状态效果 `drone_healing` 驱动屏幕特效 | FM:909-922 |
| 治疗绳 | 每个被治的人两根 `CreateRope`（10 节点，材质 `models/cable/drone_medic_cable`）：一根只给被治者看（随视角模型渲染），一根给其他人看。绳尾挂在 `CHESTFOCUS`，用 `NonPhysicsMoveInWorldSpaceToLocalPos` 0.25 s 从无人机"射"到胸口 | FM:998-1025 |
| 绳长随距离变 | `GraphCapped( 距离, 85.3, 256, 214, 306 )` 每 0.1 s 设一次 | FM:1027-1038 |
| 收绳 | 绳尾解除挂接、0.25 s 移回无人机、关绳重力、长度设 5，然后销毁 | FM:1040-1066 |
| 喷口 / 眼睛光 | 粒子挂在模型挂点 `VENT_BOT`、`EYEGLOW`、4 个 `VENT_*` | FM:623-640 |
| 动画 | `deploy_F` 播完接循环 `lifeline_drone_floating` | FM:610-621 |
| 高亮 | 本人 / 队友高亮 `sp_friendly_hero`；能被声呐扫到（`AddSonarDetectionForPropScript`） | FM:581-584 |
| 消失 | `Dissolve( ENTITY_DISSOLVE_CORE )` + 溶解音效 | FM:715-726 |
| HUD（本人） | 战术图标换成 `meddrone_is_following_you_rui`：剩余时间比例、跟着谁（头像）、是否有新可指派目标 | FM:1210-1263、1070-1099 |
| HUD（队友身上的标） | 每个队友一个 `meddrone_targeting_rui`，跟着 `CHESTFOCUS`：是不是最佳目标、无人机是否在他身上、是否掉血、血量 | FM:1265-1325 |
| HUD（被跟的队友） | 全屏 `ally_drone_leashed_hud`，显示剩余时间 | FM:1172-1198 |
| 被指派时的方向提示 | 1P 粒子 `P_LLR_DOC_screen_indicator`，控制点 10 设成"无人机在我哪边"的角度，持续 2 s | FM:1364-1404 |
| 屏外血量图标 | `SetTargetInfoStatusIcon`：≤25、≤50、其他掉血三档 | FM:1342-1354 |

客户端 / 服务端：移动、选目标、回血、绳子全在服务端（`#if SERVER`）；客户端只做 HUD、按键、方向提示。

## 2. 流程

```
按战术键 ─► 扔出动画（fire_rate 1.25, charge 0.01 s）
          ─► OnWeaponPrimaryAttackAnimEvent ─► FollowMedic_Deploy(手的位置)
                 │  先 FollowMedic_End(旧的)：同一时间只有 1 架
                 │  目标 = 当前 bestTarget，无效就 = 自己
                 ▼
        ┌──────────── 跟随中（4 个线程并行） ────────────┐
        │ MoveThread  每帧：选点、移动、姿态、瞬移判断     │
        │ HealThread  0.1 s：进圈计时 1 s → 接绳回血       │
        │ LifetimeThread：到 20 s → 若还在治人再等 ≤10 s   │
        │ DroneAnims：deploy_F → floating                   │
        └──────────────────────────────────────────────────┘
          │ 再按战术键（无人机存在且 bestTarget ≠ 当前目标且在范围内）→ 改派
          │ 按角色键（当前目标 ≠ 自己）→ 召回到自己
          │ 目标死亡 / 断线 → 自动回到自己
          ▼
        FollowMedic_End：停所有治疗、收绳、清 HUD、溶解
```

- **触发条件**：弹夹满 250（FM.txt `ammo_min_to_fire 250`）。无人机在场时 `OnWeaponAttemptOffhandSwitch` 返回 false（FM:278-285），所以战术键不再是"扔"，而是"指派"（客户端回调 FM:1101）。
- **指派**：`TryDroneAssignOrRecall( isRecalling=false )`：防抖 0.25 s；要求 bestTarget 有效、不是当前目标、距离 ≤ 指派范围（FM:462）。成功会让玩家切到 `MEDIC_ORDERS_OFFHAND_SLOT`（右副手）播一个"下令"动作（FM:483-491）。失败只播失败音。
- **召回**：角色键 `+scriptCommand5`（FM:1120-1145）；1v1 模式下等待 / 休息时不响应（Flowstate 加的，FM:1128-1134）。
- **打断**：
  - 主人死亡 / 断线 → 结束（FM:729-744）。
  - 被跟的人死亡 / 断线 → 改跟主人（FM:734-738，MoveThread 里也兜底 FM:817-823）。
  - 主人倒地时不能下令（FM:514）。
  - 换角色 → 结束（`EndThreadOn_PlayerChangedClass`，FM:752）。
- **结束和冷却**：寿命 20 s；之后如果还连着治疗对象，最多再等 10 s（FM:762-768）。冷却：`ammo_instant`，250 / 每秒 10 = 25 s，另有 `regen_ammo_forced_delay 20`（FM.txt:59-60、:102-109）。**推断**：强制延迟 20 s 正好盖住无人机寿命，所以总冷却约 45 s（从扔出算），要实测。
- **升级**：
  - `PAS_TAC_UPGRADE_ONE`：指派范围 ×1.5（playlist `upgrade_lifeline_doc_range_scaler`，FM:358-371）。
  - `upgrade_core_tac_cooldown_reduction`：弹夹 150 → 回充 15 s（FM.txt mods）。

## 3. 代码

### 3.1 入口

| 函数 | 行 | 做什么 |
|---|---|---|
| `MpWeaponFollowingMedic_Init` | FM:185-249 | 注册网络变量（`lifeline_drone_follow_ent`、`follow_drone_bestTarget`、`lifeline_drone_lifetime`）、按键回调、playlist 覆盖 |
| `OnWeaponOwnerChanged_ability_following_medic` | FM:256-276 | 拿到武器就开 `FollowMedic_TargetingThread`（常驻扫描） |
| `OnWeaponPrimaryAttackAnimEvent_ability_follow_medic` | FM:334-351 | 扣 250 弹药、服务端 `FollowMedic_Deploy( owner, attackParams.pos )` |
| `FollowMedic_Deploy` | FM:550-608 | 建实体、登记 `FollowDroneData`、起 4 个线程 |

### 3.2 核心逻辑

#### 3.2.1 指派目标

```
每 0.1 s（服务端）：
  best = null; bestDot = cos50° = 0.643
  对每个"可能的队友" ally（不含自己）：
    跳过：死、非友方、不同 realm、倒地、|主人原点 - ally 原点| > R
    dot = normalize(ally.世界中心 - 主人眼睛) · 主人视线
    if dot ≥ bestDot: bestDot = dot; best = ally       # 选"最正"的，不是最近的
  写入 bestTarget 网络变量
```
FM:520-548。R = 45 m = 1771.7 u（升级 ×1.5 = 2657.6 u）。距离用原点算三维距离，没有视线检查（推断：隔墙也能指派，要实测）。

下令：FM:438-481。指派用 bestTarget；召回固定改成主人自己。

#### 3.2.2 跟随运动（`FollowMedic_MoveThread`，FM:801-870）

每帧（`WaitFrame`，dt 下限 0.001）：

1. **目标点** `FollowMedic_DesiredPos`（FM:771-784）：
   - `dir = normalize( 右 − 0.6·前 )`，前 / 右按目标的**视角 yaw**（不看俯仰）。也就是在目标**右后方**，和"正右"夹 31°（atan 0.6）。
   - 水平距离 `d0`：站立 (60+85)/2 = **72.5 u**，蹲下 (35+45)/2 = **40 u**。
   - 高度 `h`：站立 **70 u**，蹲下 **46 u**（不低于 40）。
   - `desired = 目标原点 + dir·d0 + (0,0,h)`。
   - 再从"目标原点 + (0,0,h)"往 desired 扫一个 hull（±9 u × 0.7 = ±6.3 u 立方），碰墙就停在墙前。所以靠墙时无人机会被压到头顶附近。
2. **视线**：从无人机到目标眼睛画线（`TRACE_MASK_NPCWORLDSTATIC`），通就刷新 `lastLOSTime`（FM:786-790）。
3. **瞬移判断**（先于移动）：
   - `|无人机 − desired| > 406 u`（= 治疗半径 256 + 50 + 100，即"绳断距离"）→ 普通瞬移（FM:832-838）。
   - 断视线 **> 1.0 s** → 安静瞬移（音效不同，FM:839-845）。
   - 瞬移后速度清零，视线计时重置。
4. **速度**：
   ```
   toD   = desired − cur;  dist = |toD|
   speed = 3·dist + (dist > 7 ? 40 : 0)
   want  = toD/dist · speed + 0.5·v_target
   cap   = 1.6·|v_target| + 120 + 3·dist          # 40·3 = 120
   if |want| > cap: want = want/|want|·cap
   v    += (want − v) · min(1, 8·dt)              # 一阶平滑，时间常数 0.125 s
   next  = cur + v·dt
   if |next − desired| > 50 且 dist < 50: next = desired   # 防过冲
   NonPhysicsMoveTo( next, dt )
   ```
   **更正（对照分叉会话的要点）**：上限不是"约目标速度 1.6 倍"，而是 `1.6·|v_t| + 120 + 3·dist`；目标在跑（v_t 大）时上限主要由 1.6·|v_t| 决定。例：目标冲刺 300 u/s、无人机落后 60 u → want ≈ 3·60+40+150 = 370，cap = 480+120+180 = 780，不封顶。
   稳态：目标匀速 v_t 时，无人机要和目标同速，需要 `3·dist(+40) + 0.5·v_t = v_t`，所以**稳态落后距离** ≈ (0.5·v_t − 40)/3（v_t = 300 时约 37 u）。
5. **姿态**：
   ```
   yaw   = 目标视角 yaw（直接照搬，不平滑）
   pitch = clamp( v · 前(yaw) / 400, −1, 1 ) · 20°     # 400 u/s 时前倾到满
   roll  = clamp( Δyaw / (dt·180), −1, 1 ) · 17°        # 目标转身 180°/s 时侧倾到满
   NonPhysicsRotateTo( <pitch, yaw, roll>, dt )
   ```
   开关：playlist `lifeline_follow_drone_pitchParamEnabled` / `rollParamEnabled`（FM:245-248）。

#### 3.2.3 瞬移 `FollowMedic_Teleport`（FM:792-799）

起点放拖尾粒子（朝终点方向）→ `SetOrigin( desired )` → 终点播到达音。两套音效：普通（绳断）和"安静"（断视线，`WarpOut_Quiet`）。没有渐隐，是一帧完成。

#### 3.2.4 治疗（`FollowMedic_HealThread` FM:952-996，判定 FM:872-907）

每 0.1 s：
1. 正在治的人不再满足条件 → `StopHeal`（停回血、停状态效果、收绳）。
2. 对主人队伍所有活着的玩家（**含主人自己**）：满足条件就记"进圈时间"；连续在圈里 **≥ 1.0 s** 且正在治的人数 < **5** → `StartHeal`。
3. 更新所有绳长。

"满足条件"（FM:872-907）：活着、友方、同 realm、没相位、不在毒气伤害里、没倒地、没在处决、**没满血**、`CanBeHealedByDroneMedic`，且
- 水平距离 ≤ 256 u（按无人机位置，不是目标）；
- 竖直：玩家比无人机高 ≤ 92 u，低 ≤ 80+72 = 152 u；
- 默认**穿墙也治**（playlist `lifeline_follow_drone_healThroughWalls` = true）。

回血：`EntityHealResource_Add( player, 剩余寿命+10 s, 8 HP/s )`，按时间连续加，满血时下一次检查（0.1 s 内）就断开。

#### 3.2.5 寿命（FM:746-769）

`endTime = 扔出 + 20 s`（playlist `lifeline_follow_medic_lifetime`）。到点后若 `healTargets` 非空且开关 `lifeline_follow_drone_healBlocksDespawns`（默认 true），最多再等 10 s。

### 3.3 客户端表现

- 战术图标 RUI（FM:1210-1263）：`durationFrac = 剩余 / 20`；`hasDeployTarget` = 有可指派的新目标；目标切换时设 `redeployAnimTime`、头像。
- 队友身上的指派标（FM:1265-1325）：每个队友一个；`isDeployBestTarget`、`droneIsDeployedToMe`、`needsDrone`（掉血且在范围内）。
- 被指派者：全屏剩余时间 RUI（FM:1172-1198）+ 2 s 方向指示粒子（FM:1364-1404）。方向角在正后方 ±70° 内时钳到 −20° / −160°（FM:1396-1397），避免指示器画到屏幕正下方。
- 回血屏幕特效来自状态效果 `drone_healing`，回调在老的 `mp_weapon_deployable_medic.nut:1674-1697`（`P_heal_loop_screen`），两个技能共用。

### 3.4 依赖的公共代码

- `EntityHealResource_Add / _Remove`（引擎 / 公共）：按时长回血。`_gamemode_survival.nut:5660`、`sh_medical_bay.gnut:1542` 也用它。
- `HealRopeInit`、`CanBeHealedByDroneMedic`：`mp_weapon_deployable_medic.nut:12`、`:905`。
- `IsPlayerLifelineRevived`：`pilot/sh_pilot_passive_drone_rider.gnut:59`。
- 指令副武器：`mp_weapon_following_medic_orders.nut`（右副手；mod `medic_assign` / `halo_held_assign` / `halo_held_recall` 只换下令动作）。
- `Dissolve`、`AddSonarDetectionForPropScript`、`Highlight_*`。

### 3.5 和 `mp_ability_lifeline_halo` 的关系

`mp_ability_lifeline_halo.nut`（724 行）是 Lifeline Revived 的**大招**（"Halo"）：扔出去后在地上放一架**同一个模型**的无人机（`HALO_MODEL = lifeline_drone_rework.rmdl`，halo:17），0.75 s 后展开半径 245 u、高 160 u 的护盾区（halo:43-47、504-547），区内的人获得被动 `PAS_FAST_HEAL`（快速治疗）和 `halo_visuals`（halo:568-599），持续 20 s，最后 5 s 警告。

和 D.O.C. 的关系只有：
- 共用无人机模型和喷口 / 眼睛粒子（halo:17、27-29）；
- 共用清理信号 `CleanupAllDroneMedics`（halo:420、FM:751）；
- 下令副武器在**手里拿着 Halo** 时换成 `halo_held_assign` / `halo_held_recall` 动作（`mp_weapon_following_medic_orders.nut:52-98`）。

逻辑上互不调用。Halo 不跟随，是固定位置的区域效果（`script_mover` 挂在地面实体上，halo:375-377）。它的写法和 FM 一样带英文注释、结构简洁，**推断**也是社区重写。属于"区域护盾 + 区域增益"，不在本批，留给防御类研究。

## 4. 参数

脚本值 = 本地 FM 的常量 / playlist 默认值；没有实测值；Unity 未实现。

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 寿命 | 20 | s | FM:62、231（playlist `lifeline_follow_medic_lifetime`） | 跟随 + 治疗总时长 | |
| 治疗中延后 | 10 | s | FM:115、766 | 到期还连着人时最多再留 | 0 = 到点就走 |
| 每秒回血 | 8 | HP/s | FM:69、237（`lifeline_follow_drone_healPerSec`） | | |
| 治疗半径（水平） | 256 | u | FM:66、236（`lifeline_follow_medic_healRadius`） | 也决定绳长和绳断距离 | 改它会连带改 306 / 406 |
| 治疗竖直范围 | 上 92 / 下 152 | u | FM:67-68、896 | 相对无人机 | |
| 进圈到开始治疗 | 1.0 | s | FM:65、985 | | |
| 同时治疗上限 | 5 | 人 | FM:64、987 | S3 老无人机是 3（`mp_weapon_deployable_medic.nut:29`） | |
| 治疗检查间隔 | 0.1 | s | FM:959 | | |
| 穿墙治疗 | true | — | FM:233 | false 时要无人机→眼睛的视线 | |
| 绳节点数 | 10 | 个 | FM:71 | 绳的平滑度 | |
| 绳最大长度 | 256+50 = 306 | u | FM:72、379-382 | | |
| 绳长曲线 | 距离 85.3→256 映射到 214→306 | u | FM:1032-1035 | 近时绳短、远时绳长 | |
| 绳射出 / 收回 | 0.25 / 0.25 | s | FM:73-74 | | |
| 绳断（瞬移）距离 | 306+100 = 406 | u | FM:75、384-393、832 | 无人机离"目标点"超过就瞬移 | |
| 断视线瞬移 | 1.0 | s | FM:114、839 | | 小 = 更"黏"，大 = 更真实 |
| 指派范围 | 45 m = 1771.7 | u | FM:78、240（`lifeline_follow_medic_targetingDistance`） | 三维原点距离 | |
| 指派范围升级 | ×1.5 | — | FM:360（`upgrade_lifeline_doc_range_scaler`） | | |
| 指派锥 | cos 50° = 0.643（半角 50°，全角 100°） | — | FM:79、241；`sh_utility_all.gnut:27` | | |
| 目标扫描间隔 | 0.1 | s | FM:116、424 | | |
| 下令防抖 | 0.25 | s | FM:80、242 | | |
| 指派方向提示 | 2.0 | s | FM:81、243 | | |
| 跟随距离（站） | 60–85，用中点 72.5 | u | FM:83-84、774 | | |
| 跟随距离（蹲） | 35–45，用中点 40 | u | FM:86-87、774 | | |
| 跟随高度（站 / 蹲） | 70 / 46 | u | FM:112-113 | 相对目标原点 | |
| 最低高度 | 40 | u | FM:88、779 | | |
| 偏移方向 | normalize(右 − 0.6·前) | — | FM:778 | 右后方 31° | 改系数可放到左边 / 正后方 |
| 比例增益 | 3 | 1/s | FM:93、850 | 速度 = 3·距离 | 大 = 跟得紧 |
| 基础速度 | 40（距离 > 7 时） | u/s | FM:92、94、851-852 | | |
| 继承目标速度 | 0.5 | — | FM:95、849 | | 1 = 不落后 |
| 速度上限 | 1.6·\|v_t\| + 120 + 3·dist | u/s | FM:97、854 | | |
| 平滑率 | 8 | 1/s | FM:857 | 时间常数 0.125 s | 大 = 更硬 |
| 防过冲距离 | 50 | u | FM:96、860 | | |
| 碰撞 hull | ±9 × 0.7 = ±6.3 | u | FM:100、109-110、782 | 只用于目标点的扫掠 | |
| 前倾最大 | 20 | ° | FM:103、247 | 400 u/s 前向速度时到满 | |
| 侧倾最大 | 17 | ° | FM:104、248 | 180°/s 转身时到满 | |
| 前倾满值速度 | 400 | u/s | FM:865 | | |
| 侧倾满值角速度 | 180 | °/s | FM:866 | | |
| 冷却（弹夹 / 回充） | 250 / 10 每秒 = 25 | s | FM.txt:102-109 | | |
| 强制回充延迟 | 20 | s | FM.txt:59 | **推断**总冷却 ≈ 45 s | |
| 冷却升级 | 弹夹 150 → 15 s | s | FM.txt `upgrade_core_tac_cooldown_reduction` | | |
| 出手 | fire_rate 1.25、charge 0.01、deploy 0.15 | s | FM.txt:44-60 | | |

声明了但**没用到**的常量（证据见 5.1）：`MEDIC_FOLLOW_TARGET_DISTANCE_TOLERANCE_SQR`（:85）、`HEIGHT_CORRECTION_TOLERANCE`（:89）、`PARENT_GROUND_HEIGHT_DIFF_TOLERANCE`（:90）、`DRONE_POSE_PARAM_MAX_VAL 45`（:102）、`DRONE_VEHICLE_OFFSET`（:106）。

实测（R5，2026-11-01）：跟随点、稳态落后、pitch / roll 都和上表、3.2.2 一致，见 5.2 末尾。

## 5. 未解决和要实测的

### 5.1 服务端是不是 SDK 重写（结论：几乎可以确定是）

证据：
1. 同一仓库只有一次提交（`9b21dc9 1.3`，CaféDeColombiaFPS），git 历史看不出来源，只能看代码本身。
2. 有 Flowstate 专属逻辑（`Flowstate_IsGame1v1Type`，FM:1129）和英文解释性注释（FM:111、765、1128），Respawn 原版脚本这种位置通常没有注释。
3. 声明了 5 个常量但不用（见第 4 节末）。`HEIGHT_CORRECTION_TOLERANCE`、`PARENT_GROUND_HEIGHT_DIFF_TOLERANCE` 和 `mp_ability_frag_drone.nut:80-81` 一模一样；`DRONE_VEHICLE_OFFSET` 来自 S3 老 Lifeline 无人机（`mp_weapon_deployable_medic.nut:79`，那里用来挂 HoverVehicle）。说明作者保留了 S21 的常量名，但运动逻辑是自己写的。
4. 治疗半径、绳参数、hull 和 S3 老无人机完全一致（`mp_weapon_deployable_medic.nut:31、39-42、64-65`），只有每秒回血（7 → 8）和人数（3 → 5）不同。
5. 无人机用 `script_mover` + `NonPhysicsMoveTo`；S21 正版**推断**用 vehicle（`DRONE_VEHICLE_OFFSET` 暗示），速度 / 姿态可能由引擎处理。

同样嫌疑：`mp_ability_lifeline_halo.nut`。

### 5.2 要实测

| 问题 | 为什么不确定 | 怎么测 |
|---|---|---|
| 跟随公式是不是这份脚本的行为 | 本地 dedi 跑的就是这份脚本，应该一致；但要确认没被别的脚本覆盖 | 火力训练场，扔无人机跟自己；AgentLink 每 0.05 s 记无人机和玩家位置（W4 的 `w4_probe.py` 改一下，按 scriptname `follow_medic` 找实体）。站着、走、冲刺、滑铲、转身 4 种。对比 3.2.2 的公式：稳态落后距离、跟随点在右后方 72.5 u / 高 70 |
| 和 S21 正版差多少 | 本地是重写版 | 只能找正版录像对照：看无人机相对 Lifeline 的位置（右后方？头顶？）、冲刺时落后多少、转身侧倾。精度只到"像不像" |
| 断视线 1 s 瞬移 | 视线终点是目标眼睛，hull 偏移可能让它常被小障碍挡 | 绕柱子跑，记瞬移次数和时机 |
| 隔墙能不能指派 | `FindBestTarget` 没视线检查 | 用 bot 当队友（需要两个玩家，火力训练场可能做不到；记为"需要多人环境"） |
| 总冷却 45 s | `regen_ammo_forced_delay` 的语义是推断 | 扔出后记战术弹药随时间变化 |
| 稳态落后距离 | 公式推的 | 同第一条 |

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
- ✅ **跟随公式 = 本地行为**（Lifeline 满充能点 `offhand1` 放出，每服务端帧记录）：站立偏移 后 37.3 / 右 62.2 / 高 70.0（和 3.2.2 完全一致）；稳态落后 走 199.5 → 19.9 u（公式 19.9）、冲刺 299 → 34.9–36.8 u（公式 36.5）；pitch 10.1° / 14.2–14.8° / 滑铲 20°（公式 v/400·20°）；蹲下滑铲时靠近到 右 38 / 高 49（公式 34.3 / 46，还在收敛）；原地转身 ~210°/s 时 roll 封顶 17°、yaw 晚一个 tick、停转 0.6 s 回位。
- 没测：断视线瞬移、隔墙指派、总冷却、和 S21 正版对比。

## 6. HSD 实现

**未实现。** `HSD-Unity/Assets/HSD/Game/Runtime/Combat/` 里没有伙伴 / 无人机类，`CombatSim` 也没有治疗（README 第 "文件" 表）。

建议做法：
- 新建 `Companions.cs`：`FollowMotion`（纯 C#，输入目标位置 / 速度 / yaw / 是否蹲，输出无人机位置 / 速度 / 姿态，公式照 3.2.2）、`TargetPicker`（3.2.1）、`HealDrone`（组合两者 + 治疗圈）。三个都按 `_shared/` 文档的接口写，后面 Crypto 无人机、伙伴 AI 都能复用 `FollowMotion`。
- 放进 `CombatSim.itemUnits`，`CombatVisuals` 画胶囊 + 绳（LineRenderer 10 个点，下垂用二次贝塞尔近似即可）。
- 开关：`CombatLoadout` 新增 `hsd.tf2.x.companion`；跟随公式的参数（偏移方向、增益 3、平滑率 8）做成 `FollowMotionSettings`，便于以后换成实测值。
- 和 R5 的差别：等实测（5.2）后写进 `R5-DIFF-ARCHIVE.md`。现在能确定的差别只有"本地版本 ≠ S21 正版"这一条。
