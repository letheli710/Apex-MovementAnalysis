# Catalyst 战术 Piercing Spikes（尖刺）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_spike_strip.nut`（2045 行），`txt` = `weapons/mp_ability_spike_strip.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Catalyst / 战术 / Piercing Spikes / `mp_ability_spike_strip`。
- **一句话**：扔一个铁磁液体球，落到平地上后展开成 9×3 的尖刺地毯（中心核 + 每 47 u 一排）。2 s 后进入待机；半径 440 内有**看得见核心**的敌人时尖刺竖起（核心变实体、可被打）；站在尖刺上的敌人移动 ×0.5（NPC ×0.8），每秒 15 伤害。没有持续时间，最多同时 2 块。
- **分类**：好技能（区域减速 + 伤害）；系统（"看见敌人才激活"的待机陷阱；沿地面铺开的网格）；可视化（尖刺待机 / 竖起两种模型、从中心向外长）。
- **可拆出的部件**：
  - 沿地面铺开的网格（每一格向下 trace 贴地、断开的格子剪掉）→ 3.2.2 `CreateSpikeStrip2` / `CreateSpikeLineData2`，见 `_shared/B-placement.md`
  - 待机 / 激活（有视线才激活）→ 3.2.3 `SpikeTotemTriggerThread`
  - 区域内持续减速（引用计数、进入时砍一半水平速度）→ 3.2.4，见 `_shared/B-move-slow.md`
  - 每人 1 s 伤害冷却表 → 3.2.4 `file.lastSpikeDamageTime`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 投掷 | 引擎 grenade，1400 u/s，仰角 8°，弹跳系数都是 0.1（几乎不弹），最多碰 50 次 | `txt:105-117` |
| 落地条件 | 碰撞法线 z > 0.75 才落地，否则记下"反方向"继续；超过次数 → 删除并退还 | `nut:310-330` |
| 落地爆点 | `Explosion(伤害 0, 半径 0)` 只为特效 `exp_ferro_tac_SM` | `nut:345-360` |
| 核心 | `CreateResinShard`（资源化"树脂"实体），血 300，开始不可伤、不实体 | `nut:520`、`nut:1415-1420` |
| 尖刺片 | 每格一个 prop，模型待机 / 激活两套，`SetModel` 切换（没有动画） | `nut:1316-1405` |
| 检测范围 | `trigger_cylinder` 半径 440（升级 330）、上下各 150 | `nut:530-545` |
| 伤害 / 减速判定 | 不是每片尖刺一个触发器（那段被注释掉了），而是**每帧对每片尖刺做 `PointInCylinder(底, 底+up·50, r 32, 脚底位置)`** | `nut:1610-1646`；注释掉的旧写法 `nut:1345-1360` |
| 减速 | 状态效果 `move_slow`，`StatusEffect_AddEndless`（离开才停），玩家 0.5，NPC 0.8 | `nut:1660` |
| 进入时砍速度 | 空中或滑铲进入 → 水平速度 ÷ 2（一次） | `nut:1661-1670` |
| 伤害 | `TakeDamage(15, damageSourceId mp_ability_spike_strip)`，每人 1.0 s 一次 | `nut:1700-1715` |
| 挡 ping | 核心 `CreateTraceBlockerVolume(半径 64)` | `nut:567` |
| 收回 | 主人对核心按 Use | `nut:469-500` |

## 2. 流程

```
按住（toss_pullout 0.2）→ 松开（toss_time 0.6）→ 投出
飞行：碰到墙 / 斜面（法线 z ≤ 0.75）→ 继续；碰到平地且 CanDeployOnEnt → PlantStickyEntity
落地：特效爆点 → SpawnSpikeArea
 ├ 生成核心（不实体、不可伤）→ SpikeTotemThread：检测圆柱、挡 ping、加入 activeTraps（> 2 删最旧）
 ├ 0.3 s 后 CreateSpikeStrip2：以投掷方向为宽、垂直方向为长，铺 9×3 网格
 └ 每片 SpikeLifeTimeThread：2 s 激活前若被推开 > 250 → 删除
2.0 s（activationDelay）后，SpikeTotemTriggerThread 每帧：
 ├ 圆柱内有活着的敌人（玩家 / 分身 / NPC）→ touchingEnemy
 │   从核心中心到敌人胸口、头各一条 trace：打到敌人本身（或 Gibraltar 枪盾）→ visibleEnemy
 ├ visibleEnemy 刚变真 → 核心 Solid + 可伤（尖刺换成激活模型）；变假 → 反过来
 └ touchingEnemy：圆柱里每个敌人（不在相位、非友军、没有 PAS_LOCKDOWN）若脚底在任一片尖刺圆柱里
       → 加入 ent.e.spikeCoreTriggers，第一次加入时起 SpikeStripEnterThread
SpikeStripEnterThread（每人一个）：
 ├ 上 move_slow（玩家 0.5 / NPC 0.8），空中或滑铲 → 水平速度 ÷2
 └ 每帧：还在尖刺上？visibleEnemy 且核心 Solid → 每 1.0 s 15 伤害；不在任何尖刺上 → 结束，撤减速
结束：核心被打掉（300 HP，非近战、非尖刺本身的伤害 ×2）/ 友军近战一刀秒 / 被 EMP / 主人收回 / 主人死亡出局 / 回合结束
```

注意两点：
1. **减速在待机时也生效**：`SpikeStripEnterThread` 只要求"在尖刺上 + touchingEnemy"，减速不看 visibleEnemy；**伤害**才要求 visibleEnemy 且核心实体。推断：躲在看不到核心的地方踩上去，只减速不掉血。要实测。
2. 小尖刺受到的伤害全部转给核心（`OnLittleSpikeDamaged`，`nut:1824`），自己 ×0。

升级：`PAS_TAC_UPGRADE_TWO` → 最多 3 块；`PAS_TAC_UPGRADE_THREE` → 检测半径 330（更小，推断是"更难被发现"的反向升级，要核对描述）。

## 3. 代码

### 3.1 入口

- `OnWeaponTossReleaseAnimEvent_ability_spike_strip`（`nut:272`）：投出。
- `OnProjectileCollision_ability_spike_strip`（`nut:293`）：落地判定 → `SpawnSpikeArea`（`nut:501`）。

### 3.2 核心逻辑

#### 3.2.1 落地

```
bounceCount++；超过 50 且没落地 → DestroyProjectileAndRefund（退还 1 次）
法线·上 ≤ 0.75 → savedDir = 水平(-法线)（记住"墙的反方向"），return
CanDeployOnEnt(hitEnt) 失败 → return
PlantStickyEntity(…, <90,0,0>) → 隐藏 + 停物理 → SpawnSpikeArea(方向 = savedDir)
```

#### 3.2.2 网格（`CreateSpikeStrip2`，`nut:720`）

```
网格 长 9（核心两侧各 4，间距 47）× 宽 3（核心两侧各 1，间距 30）
长方向 = 投掷方向的右向量；宽方向 = 投掷方向
CreateSpikeLineData2（nut:966）：每一步从上一点 +40 高、沿方向走 spacing，再向下 80 trace 找地面
  → 贴地（台阶 ≤ 40 上、≤ 40 下）
剪枝（nut:880-930）：第 i 列里不和第 i-1 列连着、也找不到经同列有效格通到"桥"的格子 → 无效
每个有效格 CreateSpikeSegment，四个角用 L / R 角模型
```

最多 27 片（含核心）。和 Thermite 的贴地线（APEX 2.3）是同一类写法，连 playlist 变量名都借用 `thermite_grenade_use_new_traces`（`nut:978`）。

#### 3.2.3 待机 / 激活（`SpikeTotemTriggerThread`，`nut:1406`）

见第 2 节。视线检查是两条 `TraceLine`（胸、头），忽略圆柱内其他实体；打到 Gibraltar 枪盾也算"看见"。

#### 3.2.4 减速 + 伤害（`SpikeStripEnterThread`，`nut:1648`）

```
handle = move_slow(Endless, 0.5 或 0.8)
if 空中 or 滑铲: v.xy /= 2
loop 每帧:
  for 每个记录的核心:
     if 脚底在尖刺圆柱里:
        保留
        if visibleEnemy && 核心.IsSolid() && now - lastDamage[ent] > 1.0:
            TakeDamage(15); lastDamage[ent] = now
     else 移除
  列表空 → 结束（撤 move_slow）
```

`lastSpikeDamageTime` 是按受害者存的全局表：踩在两块尖刺上也只每秒 15。

另有一条旧路径 `SpikeTriggerEnter` / `SpikeTriggerEnterThread`（`nut:1740-1822`，引用计数 + 只在第一帧砍滑铲速度），只被注释掉的每片触发器调用，现在不跑。

### 3.3 客户端表现

- 尖刺模型：待机 `SPIKE_STRIP_SPIKE_DORMANT`，激活 `altModel`；缩放常量都是 1.0（`nut:86-88`），所以只换模型不缩放。
- 敌我颜色：友军蓝 `<80,150,255>`、敌人红 `<255,32,10>`，描边强度 0.1 / 1.0（`nut:96-99`）。
- 待机 / 激活两套循环音，每 18 s 一轮，按距离错开起点（`nut:49-52`）。
- 收回提示、小地图图标。

### 3.4 依赖

- `CreateResinShard` / `GetResinStructureRoot`（Catalyst 的"树脂"公共代码，大招 Dark Veil 也用）。
- `PlantStickyEntity`、`CreateTraceBlockerVolume`、`AddEMPDestroyDeviceNoDissolve`。
- `_shared/B-move-slow.md`、`_shared/B-placement.md`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 伤害 | 15 | HP | `nut:73` | 每秒一次 | |
| 伤害间隔 | 1.0 | s / 每人 | `nut:72` | | |
| 减速（玩家） | 0.5 | 强度 | `nut:74` | 速度 ×0.5 | |
| 减速（NPC） | 0.8 | 强度 | `nut:75` | NPC 更慢（×0.2？见第 5 节） | |
| 进入砍速 | ÷2 | 水平速度 | `nut:1664-1669` | 空中 / 滑铲进入 | |
| 网格 | 长 4+1+4，宽 1+1+1 | 片 | `nut:76-77`；playlist `catalyst_spikes_numPiecesLength / ExtraWidth` | 共 27 | |
| 间距 | 长 47，宽 30 | u | `nut:78-79` | 地毯 ≈ 376 × 60 u（+片半径） | |
| 尖刺判定圆柱 | r 32，高 50 | u | `nut:101-102` | 判定脚底点 | |
| 检测半径 / 高 | 440（升级 330）/ ±150 | u | `nut:81,83,104` | 何时激活 | |
| 激活延迟 | 2.0 | s | `nut:85` | | |
| 展开延迟 | 0.3 | s | `nut:89` | | |
| 偏离核心删除 | 250 | u | `nut:90` | | |
| 核心血量 | 300 | HP | `nut:66,80` | 非近战伤害 ×2 | |
| 持续时间 | 无（-1） | | `nut:67` | 一直在 | |
| 同时数量 | 2（升级 3） | 块 | `nut:62,64` | | |
| 投掷速度 / 仰角 | 1400 / 8° | | `txt:116-117` | | |
| 弹跳 | 0.1 / 0.1 / 0.1 | | `txt:105-107` | | |
| 落地法线阈值 | 0.75 | | `nut:316` | | |
| 冷却 | 弹匣 40、每次 20 → 2 次，回充 1/s → 20 s 一次 | | `txt:73-79` | | |
| 落地爆点伤害 | 0（`.txt` 写 20 / 256，但脚本传 0） | | `txt:83-88`；`nut:345` | | |

## 5. 未解决和要实测的

1. **NPC 减速 0.8**：状态效果强度 0.8 是"减 80%"还是"剩 80%"？电击里 0.5 = 速度 ×0.5（APEX 2.2 实测 0.498），按同一引擎规则，0.8 应是"减 80%"——NPC 反而更慢。测法：dedi 上刷 spectre 走过尖刺，量速度。
2. **待机时只减速不伤害**：站在核心看不到的位置（核心后面有箱子）踩尖刺，看是否掉血、是否减速。
3. 升级三把半径从 440 改成 330 的含义：查本地化 `localization/` 里 `upgrade_catalyst_tac_trigger_range` 的描述。
4. `.txt` 的 `explosion_damage 20` 是否被引擎用到（脚本里 Explosion 传 0）。测法：直接扔到敌人脚下看落地瞬间是否掉 20。

## 6. HSD 实现

**未实现。**

建议做法：

- `SpikeStrip : ThrownItem`（`Throw.cs`）：`ThrowParams { launchSpeed = 1400, pitchOffset = 8, shallow = 0.1, sharp = 0.1, alongNormal = 0.1 }`；`OnBounce` 里法线 z > 0.75 才部署（`AWall.OnBounce` 写法一样，`Tacticals.cs:96`）。
- 网格：照 Thermite 的贴地点生成（`Ordnance.cs` 的 `Thermite`，"每点向下最多 225、台阶 ≤ 46"）改成二维 9×3，用 `CombatSim.WorldRay` 向下 trace。
- 激活：每帧对 440 内的敌人做 `CombatSim.WorldClear(核心中心, 敌人胸 / 头)`。
- 减速：`CombatUnit.slowScale / slowUntil` 每帧刷新 `slowUntil = now + dt`（等于 Endless），离开即停；玩家进入时 `vel.xy /= 2`（要写身体，开关 `hsd.combat.spikes.halveOnEnter`）。
- 伤害：`Dictionary<CombatUnit,double> lastSpikeDamage`。
- 核心可被打：`CombatUnit` 子类，血 300，只有激活时 `Targetable`。
- 和 R5 的差：模型切换用颜色代替。写进 `R5-DIFF-ARCHIVE.md`。
