# 10 技能设计结构、敌人 AI

由 hb-ch10 写（2026-11-14）。分支 `handbook/ch10`，还没合并。写法照 [README.md](README.md) 的写法规范；单位和身高比例照 [01 单位与身体](01-units-body.md)（1 u = 0.0254 m，H = 72 u）。TF2 的长度也是 Source 单位 u，换算相同；TF2 铁驭的碰撞体高度也按 72 u 算身高比例。

## 白话说明

这一章分两半。

**前一半讲技能的"骨架"**：不讲某个技能怎么飞、怎么拉（那些在 [第 05 章](05-wall-external.md)），而讲所有技能共用的东西：一个技能有哪几种状态、充能和冷却怎么算、两个技能同时发生谁赢、什么时候被打断、技能怎么改动玩家的移动、减速和眩晕这类"控制"怎么叠加。结论先说：

1. **每个技能任何时刻只处在四种状态之一**：空闲、准备中（按下了，还没作用到身体）、驱动中（每条命令都在推身体）、余效中（只改移动倍率之类的修正）。**驱动中同时最多一个**，每种状态都有一个"保证退出"的超时。
2. **充能按"被用掉"算，不按"按键"算**：钩爪没打中、被拒绝的按键都不扣充能。一格用完后过一个冷却回一格，一格一格串行回。
3. **技能改速度只有两种方式**：替换速度（跳板、突袭这类"发射"，同一条命令只认一个，优先级高的赢）、乘移动倍率（兴奋剂这类"加速"，加速不叠加只取最大，减速相乘）。所有结果再统一截到速度上限（水平 900 u/s，向上 1100 u/s）。
4. **控制要短、要有预告**（设计哲学 P9）：威力大的先给 1–3 s 预告；夺走玩家按键的时间以 0.8 s 为锚点；减速走统一的"状态效果"，同类取最大、有淡出。

**后一半讲敌人 AI**。Unity 里**还没有任何 AI 实现**，所以这一半写成"规格 + 实现模板"：规则全部来自 TF2（文件 + 反编译 + 本地实测），写成和引擎无关的形式，再给出在 Unity 里怎么搭的模板。**这一半没有参考实现**，每一项的"实现模板"都标"没有参考实现"。结论先说：

1. **AI 是三层**：设置表（每种敌人的数）→ 行为树（按优先级挑一个"计划"）→ 计划表（一串任务 + 打断条件）。
2. **发现玩家要时间**：每 0.15 s 扫一次，近处 0.1 s、远处 0.5–2 s 才"看见"，偏离正前方 30° 以外更慢。实测 250 / 800 / 1400 u 分别 0.37 / 0.75 / 1.33 s 发现，**发现到第一枪还要 3–4 s**。
3. **对快速移动的铁驭故意打偏**：跑墙、在空中或速度 > 180 u/s 时，每颗子弹有固定概率被瞄到玩家身旁 30–80 u 的空处。默认难度下快速铁驭只有 25 % 的子弹是"真瞄"。这是 TF2 让高速移动"有用"的核心规则。
4. **刚盯上你的头 10 s 散布更大**（×2 → ×1），子弹偏向散布圈边缘。

读完前一半，能给一个新技能定好状态、冷却、优先级、和移动的接口；读完后一半，能从零搭出一个和 TF2 规则一致的敌人士兵，并用 TF2 实测的命中率表验收。

**和别章的分界**

| 内容 | 在哪一章 |
|---|---|
| 每个移动技能自己的物理（钩爪、跳板、升梯、喷气、突袭、传送门、滑索枪…） | [05](05-wall-external.md)。本章 §10.9 只给一行概要并指过去 |
| 跳跃键被谁拿走（跳跃键仲裁） | [06](06-momentum-arbitration-input.md)。本章 §10.5 只写技能层和它的接口 |
| 技能的镜头（发射 kick、FOV） | [07](07-camera.md) |
| 枪、后坐、命中反馈 | [09](09-combat-feel.md)。本章只写 AI 怎么开枪、打不打得中 |
| 技能、AI 怎么验收的总规则和合格线总表 | [11](11-acceptance.md) |

**本章出处缩写**（路径从研究仓库根目录算）

| 缩写 | 文件 | 在哪 |
|---|---|---|
| DP | `research/DESIGN-PHILOSOPHY.md` | main |
| SR | `research/phase2-local/m5/SKILL-RULES.md` | main |
| DEF | `DEFERRED-DESIGN-TODO.md` | main |
| SH | `SHELVED-ABILITIES.md` | main |
| C0 | `research/combat/C0-ABILITY-FILTER.md` | PR #86，还没合并 |
| SE | `research/combat/_shared/E-STATUS-EFFECT.md` | PR #86，还没合并 |
| MS | `research/combat/_shared/B-move-slow.md` | PR #86，还没合并 |
| EMP | `research/combat/_shared/B-electric-emp.md` | PR #86，还没合并 |
| DM | `research/combat/_shared/C-DAMAGE-MODIFIERS.md` | PR #86，还没合并 |
| TG | `research/combat/_shared/B-targeting.md`、`D-DECOY-AI.md` | PR #86，还没合并 |
| A–E | `research/combat/A-SUMMARY.md` … `E-SUMMARY.md` | PR #86，还没合并 |
| W2 | `research/combat/W2-RUNTIME.md` | PR #88，还没合并 |
| IP2 | `research/combat/IP2-RUNTIME.md` | PR #92，还没合并 |
| PL | `tf2/expansion/PILOT-LIST.md`、`DESIGN-LIST.md` | main |
| AS | `tf2/pve/AI-SPEC.md` | main |
| AL | `tf2/pve/AI-LIVE.md` | main |
| BT | `tf2/pve/BEHAVIOR-TREES.md`、`SCHEDULES.md` | main |
| FD | `tf2/pve/FD-RULES.md` | main |
| RN | `tf2/ref-native-tail/REF-NATIVE-1112.md` | PR #115，还没合并（分支 `ref/native-tail`） |

Unity 路径：`U:` = HSD-Unity。`U:…/Abilities/` = `Assets/HSD/R5Replay/Runtime/Abilities/`（main）；`U:…/Combat/` = `Assets/HSD/Game/Runtime/Combat/`。

---

## 10.0 共同约定

### "Unity 参考实现"指什么

- **移动技能**：`MovementConfigs.Reference()` 建出来的游戏身体（`SkillBody`：电机 `R5MotorV2` + 能力集合 + 仲裁器 `SkillArbiter`），技能组合来自 `SkillLoadouts`。框架在 `U:…/Abilities/_Core/`，main。
- **战斗技能和道具**（铁驭侧）：main 上只有 TF2X 占位层（`U:…/Combat/`）；公共框架（状态效果、减速、伤害链、放置物）在 HSD-Unity PR #53，各批技能在 PR #58，**都还没合并**。
- **泰坦套件**：HSD-Unity PR #82（`titan/kits-core`），还没合并。
- **敌人 AI**：**没有参考实现**。PR #60 里的 `EnemyGun` 只是两个站桩的假人枪手（§10.17）。

### 时间和命令

技能层和电机一样按固定命令走（120 Hz，[02 §2.1](02-foundation.md)）。本章的"每条命令"指一次 `SkillBody.Step`。AI 的时间是游戏时间（秒），各循环有自己的周期（§10.10）。

---

# 第一部分 技能

## 10.1 设计原则：威力换预告，夺控很少而且很短

#### 原理

技能是玩家之间"打破常规"的手段，所以它们最容易让人觉得不公平。R5 的做法是：**越强的技能，越要先告诉对方**（预告），**夺走对方操作的时间越短越好**（夺控）。被减速了还能走、能转身、能开枪；真正"按键无效"的时间很少超过 1 s。玩家和 NPC 用不同的数值，因为 NPC 不会抱怨、也不会靠走位躲。

这条是设计哲学 P9。它的**证据是全书最弱的**：大部分只读了脚本，没有实测，而且来自多人游戏。HSD 最终是 PvE（D-59），要不要跟由我们定。

#### 规则和公式

1. **预告**：伤害大、范围大的技能，从"能看见"到"开始生效"之间留 1–3 s。
2. **夺控短**：完全夺走按键的时间以 0.8 s 为锚点；之后只限速、不夺键。
3. **控制统一走状态效果**（§10.6）：有严重度、时长、淡出；同类取最大。
4. **玩家和 NPC 数值分开**：同一个减速区，对玩家和 NPC 写两个值。
5. **高速进入要想清楚**：从空中或滑铲进入减速区，R5 会把水平速度砍一半一次（防止高速穿过）。新技能要写明跟不跟。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 预告：滚雷、防御轰炸落地到开始 | — | 2 s | — | 1 – 3 s | [数据] A |
| 预告：Seer Focus of Attention | — | 1 s | — | — | [数据] C |
| 预告：Crypto EMP 蓄力 | — | 2.5 s | — | — | [数据] D |
| 预告：Conduit 屏障激活 | — | 3 s | — | — | [数据] D |
| 黑洞落地到开始拉 | — | 1.7 – 1.8 s（脚本 1.75 s） | — | — | [实测] W2 §2 |
| 黑洞夺键时长 | — | 0.8 s | — | 锚点 | [实测] W2 §2 |
| 黑洞夺键后的逃跑限速（离中心 98 → 304 u） | 3.226 → 2.614 m/s | 127.0 → 102.9 u/s | 1.764 → 1.429 H/s | 脚本公式 122.8 → 97.0 | [实测] W2 §2 |
| 尖刺减速：玩家 / NPC | — | 0.5 / 0.8（严重度） | — | — | [数据 + 实测] MS、W2 §1 |
| 反例：Valkyrie 导弹晕眩 | — | 2 s + 淡出 1.5 s（减速 0.75、转向 0） | — | — | [数据] C |

#### 实现模板

新技能先过 DP §9.2 的"技能 5 条"检查单，再写代码：

```
□ 控制走状态效果（有淡出、同类取最大）？        → §10.6
□ 威力大的有预告吗？预告多长？                   → 1–3 s
□ 夺控短吗？完全夺键多久？                       → 锚点 0.8 s
□ 玩家和 NPC 两个值都写了吗？                     → 参数表里两列
□ 空中 / 滑铲进入要不要砍一半？                   → 写明开关
```

然后照 DP §9.1 的 8 步：一句目标 → 两个 R5 锚点 → 用 T1–T9 的现成结构 → 填数（范围外要写理由）→ 过检查单 → 做进 Unity（开关、默认值、能切回）→ 同输入对照 → 留档（选中和没选中都写，没试玩前新值都标 [设计]）。

#### 验收

- 检查单每一条在技能的 README（D-14：一个技能一个文件夹 + README）里有答案。
- 预告和夺控时长有测试：例如 `CombatControlTests.BlackHoleStrongPullIgnoresKeysThenOnlyCapsEscape`（HSD-Unity PR #58，还没合并）。
- 合格线：夺控时长和 R5 锚点一致；超过 1 s 的夺控要在 R5-DIFF 里写成偏离。

#### 出处

- DP §1、§4 P9、§8.3、§9.1、§9.2（技能 5 条）。main
- W2 §1、§2：move_slow 语义、黑洞时间线和逃跑限速。PR #88，还没合并
- MS §4：尖刺玩家 0.5 / NPC 0.8。PR #86，还没合并
- A – D：预告时长。PR #86，还没合并
- D-14（一个技能一个文件夹）、D-59（HSD 是 PvE，机制先存档、数值以后定）。main

---

## 10.2 技能的状态和每条命令的顺序

#### 原理

技能五花八门，但从"身体"的角度看只有四种情况：没事、按了还没生效（钩子在飞、突袭在蓄力）、正在推身体（钩爪拉、升梯抬、喷气）、只是改了一下移动（兴奋剂、跳板后的慢动作飞行）。把每个技能都归到这四种状态，所有"谁打断谁、谁先谁后"的规则就能写在一个地方，而不是在每个技能里各写一遍。

#### 规则和公式

1. **四种状态**（`SkillState`）：
   - `Idle`：没在运行（已经放在世界里的物件不算）；
   - `Pending`：已接受，还没作用到身体（兴奋剂起效延迟、钩子飞行 + 0.2 s 收绳、突袭蓄力、传送延迟）；
   - `Driving`：每条命令都在推身体（钩爪拉、升梯、喷气、传送门的操作锁）。**同时最多一个**；
   - `Effect`：定时的余效，只改移动（兴奋剂、跳板后的慢动作飞行、喷气的后效、突袭飞行）。
2. 每个技能报告：当前状态、累计"被接受的使用次数"（`Activations`）、`Interrupt(reason)`（立刻结束所有状态，**保留当前速度**：不弹射、不砍竖直速度、不发射）。
3. **每条命令的顺序**（仲裁器是唯一应用规则的代码）：

   | 步 | 做什么 |
   |---|---|
   | 1 `BeginCommand` | 充能回复；没充能或被独占锁住的技能键在任何技能看到之前就被屏蔽（事件 `SLOT_REFUSED_<id>_COOLDOWN` / `_LOCKED`）；有技能在驱动时，空中的跳跃键被屏蔽（`JUMP_BLOCKED_DRIVING`） |
   | 2 各技能 `BeforeMove` | 改状态、申请加速 / 减速、申请发射 |
   | 3 `CombineBoosts` | 合并移动倍率（§10.5） |
   | 4 `AfterAbilities` | 挑一个发射、截到上限；发射结束可打断的驱动、打开 lurch 窗口 |
   | 5 晚到的钩子（`ILateMoveAbility`） | 钩爪拉力要用最终的移动倍率和输入 |
   | 6 电机移动 | [02](02-foundation.md)、[03](03-ground-air-jump.md) |
   | 7 各技能 `AfterMove` | 读移动后的状态 |
   | 8 `EndCommand` | 扣充能；独占技能生效时结束其他所有状态；只留一个驱动；超时；速度上限 |

| 技能 | Pending | Driving | Effect |
|---|---|---|---|
| 钩爪 | 钩子飞行 + 0.2 s 收绳 | 拉 | — |
| 重力升梯 | — | 在升梯里 | — |
| 喷气 | — | 按住跳推进 | 后效（0.45 g + 阻力，直到离地 50 u 以内） |
| 传送 / 传送门 | 按下到传送 | 传送门：操作锁 | — |
| 突袭 | 掏出 + 蓄力 | — | 飞行（移动倍率 1.0 直到落地） |
| 跳板 | — | — | 慢动作飞行直到落地 |
| 兴奋剂 / Wraith 相位 | 起效延迟 | — | 加速（Wraith 带部署减速） |
| 蹬墙跳 | — | — | —（瞬时） |

#### 实现模板

```
// 单位：u、s
interface ISkillAbility:
    State: Idle | Pending | Driving | Effect
    Activations: int            // 被接受的使用次数（没打中不算）
    Interrupt(reason)           // 结束一切，保留速度

per command:
    arbiter.BeginCommand(ctx)   // 充能、屏蔽键
    for a in abilities: a.BeforeMove(ctx)
    msc *= arbiter.CombineBoosts(ctx.boosts)
    arbiter.AfterAbilities(ctx, ctx.launches)
    for a in late: a.BeforeMoveLate(ctx)
    motor.Move(ctx)
    for a in abilities: a.AfterMove(ctx)
    arbiter.EndCommand(ctx)
```

Unity 参考实现：`U:…/Abilities/_Core/MovementAbility.cs`（`SkillState`、`ISkillAbility`、`ISecondPressAbility`、`ILateMoveAbility`、`AbilityContext`、`MovementAbilitySet`）、`SkillArbiter.cs`（`SkillArbiter.BeginCommand`、`CombineBoosts`、`AfterAbilities`、`EndCommand`）、`SkillBody.cs`（`SkillBody.Step`）。main。

#### 验收

- `SkillLoadoutTests.PresetsHaveThreeToFourValidSlots`、`InvalidLoadoutsAreRejected`、`SlotButtonsAreRebound`。
- `SkillFuzzTests.PathfinderOctane` / `ValkHorizonAerial` / `RevenantWraithGround` / `AshRoute`（每个 5 个种子）：随机按 30 s，再松手 12 s，**所有技能回到 `Idle` 并且站在地上**。
- 合格线：上面全部通过；回放基线不变（[11 §11.4](11-acceptance.md)）。

#### 出处

- SR §1（槽系统、状态、每命令顺序）。main
- `U:…/Abilities/_Core/README.md`、`MovementAbility.cs`、`SkillArbiter.cs`。main
- `U:Assets/HSD/R5Replay/Tests/Editor/R5MotorM5SkillTests.cs`（类 `SkillLoadoutTests`、`SkillFuzzTests`）。main

---

## 10.3 充能和冷却

#### 原理

冷却的目的是限制"多久能用一次"，不是惩罚手滑。所以只有技能**真的被用掉**（钩子打中了、兴奋剂打进去了）才扣充能；没打中、按键被拒绝都不扣。多格充能一格一格回，不是同时回，这样"连用两次"之后要等两个冷却才满。

#### 规则和公式

1. 一个槽 = 一个技能 + 一个键 + 充能格数 `charges` + 每格冷却 `cooldown`（s）。
2. **扣充能**：本条命令里技能的 `Activations` 增加了，才扣一格。
3. **回充能**：槽从满变成不满的那一刻起计时；过一个 `cooldown` 回一格；还没满就紧接着再计下一个 `cooldown`。
4. **脚本冷却**（`scriptCooldown`）：有的技能自己决定什么时候回（S21 钩爪按拉动距离 10 – 30 s；滑索枪 180 s），由技能报告回充时刻（`IChargeTimer.ChargeReadyTime`）。
5. **技能自己的复用锁**和槽冷却并存：例如兴奋剂运行中不能再按，即使槽有充能。
6. 没充能时按键在 `BeginCommand` 就被屏蔽，技能看不到这次按键。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| S21 钩爪冷却（脚本，按距离） | — | 10 – 30 s | — | — | [数据] `mp_ability_grapple.nut` |
| S21 兴奋剂复用锁（从按下算） | — | 6.7 s（6.0 + 0.7） | — | — | [实测] M10 r_octane、[数据] |
| S21 跳板冷却 | — | 90 s（练习预设 15 s） | — | — | [数据] |
| S21 Into the Void 冷却 | — | 25 s | — | — | [数据] |
| S21 次元裂隙冷却 | — | 180 s（练习预设 20 s） | — | — | [数据] |
| 滑索枪冷却 | — | 180 s（Reference）/ 10 s（Fun） | — | — | [数据] / [设计] |
| M5 练习预设：钩爪 2 × 8 s、兴奋剂 1 × 4 s、跳板 1 × 15 s、升梯 1 × 12 s、突袭 1 × 6 s、相位 1 × 10 s、传送门 1 × 6 s | — | — | — | — | [设计] SR §5 |

#### 实现模板

```
// 单位：s
slot: charges, max, cooldown, nextCharge = +∞

BeginCommand(now, dt):
    while charges < max and due(now, dt, nextCharge):
        charges += 1
        nextCharge = charges < max ? nextCharge + cooldown : +∞
    if pressed(slot.key) and (charges == 0 or lockedByExclusive): mask(slot.key)

EndCommand(now):
    if ability.Activations grew:
        wasFull = charges == max
        charges = max(0, charges - 1)
        if wasFull: nextCharge = now + cooldown
    if slot.scriptCooldown and charges < max: nextCharge = ability.ChargeReadyTime
```

Unity 参考实现：`U:…/Abilities/_Core/SkillRules.cs`（`SkillSlotEntry`：`charges`、`cooldown`、`scriptCooldown`；`SkillLoadouts` 各预设）、`SkillArbiter.cs`（`BeginCommand`、`EndCommand`）、`IChargeTimer.cs`。main。

**战斗层和泰坦层用的是另外两套冷却**（还没合并，§10.8）：

- 铁驭战斗层 `Charges`（`U:…/Combat/CombatCore.cs`，main）：次数 + 每格秒数，一格一格回；没有"开始回复前的延迟"、没有"最少多少才能用"；有 `paused`（A 型墙立着、Death Totem 立着时不回）；**换装备就新建一个满的**。
- 泰坦层 `KitAmmoCooldown`（HSD-Unity PR #82）：TF2 / R5 `.txt` 的弹药式冷却：总量、每次消耗、最少多少能用、每秒回多少、开始回复前的延迟、`hold`（运行中不回）。

R5 的技能也是 `.txt` + mod 写的（DP §8.3），所以**弹药式冷却更接近 R5**；铁驭战斗层的数值是把 `.txt` 换算成"次数 × 秒"（例：电网"30 弹药、每秒回 7.5 = 每格 4 s"）。三套并存是现状，统一与否写进 `_notes` 等用户定。

#### 验收

- `SkillCooldownTests.ChargesRechargeOneCooldownEach`、`MissDoesNotSpendACharge`、`StimCooldownAndItsOwnReuseLockout`。main
- `CombatSkillTests.TheSkillsChargeLikeTheRecordsSayAndFastChargeIsAFlag`、`CombatSystemsTests.DroneLossCostsTheChargeRecallDoesNot`、`PartyReleasedEarlyCostsNothing`（HSD-Unity PR #58，还没合并）。
- 合格线：充能时刻和"一格一个冷却、串行回"逐条命令相同；没打中不扣。

#### 出处

- SR §2"Cooldown semantics"。main
- `U:…/Abilities/_Core/SkillRules.cs`（各预设的注释写了 S21 冷却来源）。main
- `U:…/Combat/CombatCore.cs`（`Charges`）。main
- HSD-Unity PR #82：`Titan/Kits/Core/KitResources.cs`（`KitAmmoCooldown`、`KitEnergyPool`、`KitCharge`、`KitCoreMeter`）。还没合并
- DP §8.3（技能也是 `.txt` + mod）。main

---

## 10.4 打断、互斥、超时和优先级

#### 原理

两个技能可能在同一条命令上都想推身体。与其在每对技能之间写特例，不如定几条总规则：**驱动只有一个、最新的赢**；**像传送这种"把人搬走"的技能独占**；**每种状态都有保证退出的超时**，所以任何组合都不会卡死。优先级只在"同一条命令上撞车"时用。

#### 规则和公式

1. **驱动只有一个**（R1）：同时有两个驱动时，**最新开始的**留下，旧的被打断（`PREEMPTED`，保留速度）；独占的驱动永远赢；同一条命令开始的按优先级。
2. **独占**（`exclusive`）：传送 / 传送门在离开 Pending（身体被搬走）时，结束其他所有 Pending / Driving；它驱动期间其他技能键全部被拒（`LOCKED`）。相位突破（`exclusiveOnDrive`）在**开始驱动**时才结束别的（它的瞄准和取消是 Pending → Idle，不能结束别人）；它驱动时还屏蔽"使用"键（不能从相位里上滑索）。
3. **发射**：同一条命令多个发射，只认优先级最高的，其他的被打断（`LAUNCH_LOST`）。发射结束所有可打断的驱动，那一条命令按全重力（驱动对重力的改动随它结束）。
4. **超时**（保证退出）：状态持续到 `maxPending` / `maxDriving` / `maxEffect` 就被打断（`TIMEOUT`）。每个超时都放在最长的实测或建模时长之上，**所以超时从不改变实测行为**。
5. **自然退出**：落地结束跳板慢动作、突袭飞行、喷气、钩爪拉；钩爪碰墙、离钩点 34.1 u、3 s 也结束。
6. **第二次按键**（`ISecondPressAbility`）：运行中的钩爪再按一次是"松开"，不是新的使用，不受冷却屏蔽。

| 技能 | 优先级 | 可打断 | 独占 | maxPending / maxDriving / maxEffect | 最长建模时长 |
|---|---|---|---|---|---|
| 传送 / 传送门 | 100 | 否 | 是 | 2.0 / 1.0 / — s | 延迟 0.25 s，锁 0.3 s |
| 相位突破 | 100 | 否 | 是（开始驱动时） | 12.0 / 2.5 / — s | — |
| 次元裂隙 | 100 | — | 是 | 见 `SkillLoadouts` | 举起 1.04 s + 10 s |
| 跳板 | 80 | 是 | 否 | — / — / 6.0 s | 慢动作飞行约 3.4 s |
| 攀爬 | 75 | — | — | 见 `AdvancedMovementParams.Traits` | — |
| 蹬墙跳 | 70 | 是 | 否 | — | 瞬时；每 0.4 s 一次 [设计] |
| 滑索 | 65 | — | — | 同上 | — |
| 钩爪 | 60 | 是 | 否 | 1.0 / 3.0 / — s | 钩子 ≤ 0.42 + 0.20 s；拉 ≤ 1.55 s 实测 |
| Vantage 位移 | 55 | — | — | — | — |
| 重力升梯 | 50 | 是 | 否 | — / 6.0 / — s | 1080 u 上升 + 0.5 s 悬停 ≈ 4.1 s |
| 跑墙 | 45 | — | — | 见 `HsdMovementParams.Traits` | — |
| 喷气 | 40 | 是 | 否 | — / 9.0 / 10.0 s | 燃料 8 s |
| 飞行 | 35 | — | — | 见 `FunFeatureParams.Traits` | — |
| 突袭 | 30 | 是 | 否 | 2.5 / — / 6.0 s | 掏出 0.9 + 蓄力 1.3 s |
| 二段跳 | 25 | — | — | — | — |
| 滑索枪 | 20 | — | — | — | — |
| 兴奋剂 / Wraith 相位 / Into the Void | 10 | 是 | 否 | 0.5 / — / 7.0、5.0 s；Void 6 s | 0.16 s 起效、6.0 + 0.5 s；相位 4.73 s；Void 5.17 s |
| 重力切换 | 5 | — | — | — | — |

优先级、超时、独占全部是 [设计]（SR §7）。

#### 实现模板

```
EndCommand(now, dt):
    // 独占技能生效 → 结束其他所有 Pending / Driving
    if some exclusive slot just acted: interrupt every other Pending/Driving ("EXCLUSIVE")
    // 只留一个驱动
    drivers = slots where state == Driving
    if len(drivers) > 1:
        keep = exclusive driver (highest priority) or newest (ties: priority)
        interrupt every other driver ("PREEMPTED")
    // 超时
    for s in slots:
        limit = s.state == Pending ? maxPending : s.state == Driving ? maxDriving : s.state == Effect ? maxEffect : 0
        if limit > 0 and (now + dt - s.stateSince) >= limit: s.Interrupt("TIMEOUT")
```

Unity 参考实现：`U:…/Abilities/_Core/SkillRules.cs`（`SkillTraits`：`priority`、`interruptible`、`exclusive`、`exclusiveOnDrive`、`handlesJump`、`maxPending/maxDriving/maxEffect`；`SkillRules.DefaultTraits()`）、`SkillArbiter.cs`（`AfterAbilities`、`EndCommand`）。main。

**战斗层没有统一的打断层**（HSD-Unity PR #58，还没合并）：死亡清理在 `SystemSkills.OnPlayerDied`；蓄力型技能各自取消（Mirage 大招未满 1 s 松手不扣）；放置物到时、被 EMP 停机、超上限挤掉最旧的在 `Deployable` / `DeployableRegistry`；"沉默"状态有写入但没有代码读它去禁用技能。这是缺口（§缺口 3）。

#### 验收

- `SkillComboTests.NewerDriverWinsLiftThenGrapple`、`GrapplePreemptsJetsAndJumpDoesNotEngageJetsDuringThePull`、`PadLaunchEndsALiftRide`、`PortalExitLocksControlsRefusesOtherSlotsAndCancelsPendingStates`、`ContactEndsThePull`。main
- `SkillFuzzTests.*`（12 s 后全部 Idle，§10.2）。main
- 合格线：全部通过；超时次数在实测片段的回放里为 0（超时不改实测行为）。

#### 出处

- SR §2、§3 R1、R7、R8、R10 – R13、§7（这些是设计值）。main
- `U:…/Abilities/_Core/README.md`"SkillRules 默认仲裁行"。main
- HSD-Unity PR #58：`Systems/SystemSkills.cs`、`Deployable.cs`。还没合并

---

## 10.5 技能和移动的接口

#### 原理

技能不直接改电机的内部，只通过几个"口子"影响移动：**替换速度**（发射）、**乘移动倍率**（加减速）、**改重力 / 时间缩放**、**接管身体**（攀爬、滑索这类按运动学走的状态）、**禁止某些移动**（禁止跑墙、禁止翻越、强制 / 禁止冲刺）。口子少，组合就可控；最后再统一截一次速度上限，任何组合都不会飞出地图。

#### 规则和公式

1. **发射替换速度，不相加**（R5 跳板、突袭、升梯弹射都是这样）。发射像跳一样打开 lurch 窗口（`launchOpensLurchWindow`）；Reference 里升梯弹射、突袭、跳板按 R5 实测**不**打开（各自的开关）。
2. **移动倍率**：减速（< 1）相乘；加速（> 1）**不叠加，只取最大**（`boostStacking = Max`，可选 `Multiply`），再截到 ×1.40。
3. **速度上限**：每条命令结束、每次发射后，水平速度截到 900 u/s，向上速度截到 1100 u/s。
4. 叠加的冲量（不是替换的）各自有界：lurch |Δv| ≤ 0.7 × 冲刺上限且 |v| 不增；蹬墙跳最多 +258 u/s、每 0.4 s 一次；滑铲加成截在 400·msc，0.4 s 退还。
5. **驱动期间空中跳跃键被屏蔽**（`jumpBlockedWhileDriving`），除非这个驱动自己处理跳跃（攀爬、滑索：`handlesJump`）。跳跃键谁拿走的完整规则在 [06](06-momentum-arbitration-input.md)。
6. **禁止口**：`IWallRunBlocker`（突袭禁止跑墙 / 攀爬 / 悬挂）、`IMantleBlocker`（Vantage 位移禁止翻越）、`ForceSprint` / `BlockSprint`（传送门放置自动冲刺、举起时禁止冲刺）、`LockControls`（传送操作锁：丢掉本条命令的移动输入）。
7. **战斗层的口子**（HSD-Unity PR #58，开关 `CombatLoadout.motorHooks`，默认开；什么都没装时严格不写）：`externalMoveScale`（= (1 − 减速严重度) × 武器移速 × 加速）、`externalGroundFriction`、`externalSprintBlock`（减速 > 0.05 时禁止冲刺）、`playerForces`（黑洞、拴住在移动前写速度）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 水平速度上限 `maxHorizontalSpeed` | 22.86 m/s | 900 u/s | 12.5 H/s | 高于 R5 最大实测：钩爪松开 804、跳板 514、兴奋剂下滑铲 597 | [设计] SR §4 |
| 向上速度上限 `maxUpSpeed` | 27.94 m/s | 1100 u/s | 15.28 H/s | 跳板 1028.6 | [设计] SR §4 |
| 加速倍率上限 `maxSpeedBoost` | — | ×1.40 | — | Wraith ×1.388、Octane ×1.298 在下面 | [设计] SR §4 |
| 跳板发射速度 | 29.21 m/s | 1150 u/s（站 63°、蹲 45°） | 15.97 H/s | — | [实测] OCTANE §3.1 |
| 兴奋剂移动倍率 | — | ×1.298，6 s + 0.5 s 淡出 | — | — | [实测] |
| Wraith 相位：部署减速 → 加速 → 淡出 | — | ×0.80 1.17 s → ×1.388 2.77 s → 0.79 s | — | — | [实测] |

R5 原值：兴奋剂不放大跳板发射（跳板是固定的 1150 u/s 向量），只放大和 msc 有关的项（R5，SR §3 R5）。

#### 实现模板

```
// 单位：u、s
CombineBoosts(factors):
    slow = Π f for f < 1
    boost = max(f for f >= 1, default 1)        // Multiply 选项：Π f
    return slow * min(boost, maxSpeedBoost)

AfterAbilities(launches):
    best = highest priority (ties: later)
    interrupt others ("LAUNCH_LOST")
    v = clamp(best.velocity)                    // |v_h| ≤ 900, v_z ≤ 1100
    motor.launchVelocity = v
    end interruptible drivers; gravityScale = 1
    if opensLurchWindow(best): motor.jumpTime = now

EndCommand: motor.vel = clamp(motor.vel)
```

Unity 参考实现：`U:…/Abilities/_Core/SkillArbiter.cs`（`CombineBoosts`、`AfterAbilities`、`Clamp`）、`MovementAbility.cs`（`CommandModifiers`：`timeScale`、`gravityScale`、`hasLaunch`、`kinematic`、`phased`、`suppressLurch`；`AbilityContext.Launch`、`ApplySpeedBoost`、`LockControls`、`ForceSprint`、`BlockSprint`）、`WallRunLock.cs`、`IMantleBlocker.cs`、`SpeedBoost.cs`（R5 speed_boost：msc = W·(1 + 2·q(S))）。main。

#### 验收

- `SkillComboTests.PadThenLurch`、`StimDoesNotScaleThePadLaunch`、`BoostsDoNotStack`、`CeilingClipsALongGrapplePull`、`WallJumpThenPounceIsBoundedAndOpensTheLurchWindow`、`GrappleReleaseIntoSlideAndSlideJumpStayBounded`。main
- `SkillFrameRateTests.AllPresetsAt60And144Hz`：同一串输入在 60 / 144 Hz 下结果有界地接近（空间触发按命令开始时刻测，60 Hz 下会差一条命令）。main
- 战斗层口子：`CombatControlTests.NothingActingIsAnExactNoOp`、`SwitchOffLeavesTheBodyAlone`、`HooksSlowWalkByOneMinusSeverityAndFullSpeedAfter`、`SprintGateAboveFivePercent`（HSD-Unity PR #58，还没合并）。
- 合格线：全部通过；什么都不装时身体逐字节不变。

#### 出处

- SR §3（R3 – R9）、§4 上限。main
- `U:…/Abilities/_Core/README.md`、`SkillArbiter.cs`、`MovementAbility.cs`。main
- HSD-Unity PR #58 `Combat/README.md`"玩家电机接口"。还没合并
- `research/phase2-local/m4/octane/OCTANE-PRIMITIVES.md` §3.1：跳板 1150。main

---

## 10.6 状态效果和控制（减速、眩晕、电击）

#### 原理

减速、转向变慢、电击屏幕、沉默……R5 把这些全部做成同一种东西：**状态效果**。一个效果 = 类型 + 严重度 + 时长 + 淡出。同类型的多个效果不相加，只取最大，所以三个减速区叠在一起不会把人钉死。最后几秒线性淡出，玩家感觉"慢慢恢复"，不是突然解冻。

#### 规则和公式

1. 效果：`AddTimed(目标, 类型, 严重度 s, 时长 d, 淡出 f)`、`AddEndless(目标, 类型, s)`、`Stop`、`StopAllOfType`、`SetDuration`（延长同一个句柄）。
2. 当前严重度 = s × min(1, 剩余时间 / f)（淡出期内线性降到 0）。淡出参数的含义是 [推断]，Unity 照这个做。
3. **同类取最大**：同一类型多个句柄，取当前严重度最大的一个（`move_slow` 和 `speed_boost` 实测；其他类型是假设）。
4. **减速**：速度 = 基础 × (1 − s)，玩家和 NPC 相同。严重度 > 约 0.05 时**不能冲刺**（按走速再乘）。严重度存储有约 1/256 的量化（0.25 读回 0.247）。
5. **区域减速三种写法**：
   - A 在里面一直减（尖刺、黑幕）：进入加一个无限效果并计数，离开减计数，计数到 0 才停；重叠只计次数，不叠强度。
   - B 碰一下减一段（Conduit 屏障）：每次有效伤害加 0.25 × 1 s，淡出 1 s。
   - C 电击（电网、城墙、电弧星）：减速 + 转向减速 + 屏幕效果；再次被电先停掉上一次。NPC 被电击后 3 s 免疫。
6. **空中或滑铲进入减速区**：水平速度 ÷ 2，只砍一次。
7. **玩家和 NPC 数值分开**：尖刺 0.5 / 0.8；NPC 的 0.8 实测 = 速度 × 0.2。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冲刺门槛（严重度） | — | ≈ 0.05（0.047 能冲刺，0.059 不能） | — | 边界是 [推断] | [实测] W2 §1 |
| 减速 0.25 时走速 | 3.816 m/s | 150.23 u/s | 2.087 H/s | 199.52 × 0.753 | [实测] W2 §1 |
| 减速 0.50 时走速 | 2.544 m/s | 100.15 u/s | 1.391 H/s | — | [实测] W2 §1 |
| 电击：减速 / 转向减速 | — | 0.50 / 0.70（转身 × 0.3） | — | 实测 0.498 | [数据] EMP、[实测] |
| 电击：时长最长 / 最短、淡出 | — | 2.5 s / 0.2 s、1.0 s | — | — | [数据] EMP |
| NPC 电击免疫 | — | 3.0 s | — | — | [数据] EMP |
| Shellshock 减速 / 淡出 | — | 0.25 / 0.5 s（时长 3 – 6 s） | — | R5 只给玩家 | [数据] A |
| Crypto EMP 对玩家 | — | 减速 0.35、转向 0.7、2 s | — | — | [数据] D |
| 黑洞强拉速度（第一帧向心） | 9.906 m/s | 390 u/s（脚本 clamp 400） | 5.417 H/s | −2.4 % 是地面摩擦 | [实测] W2 §2 |

#### 实现模板

```
// 单位：u、s
class StatusEffect: type, severity, start, duration (+∞ = endless), fadeOut
    SeverityAt(now) = severity * min(1, (start + duration - now) / fadeOut)   // 过期 = 0

severity(unit, type, now) = max(e.SeverityAt(now) for e of that type)        // 同类取最大
moveScale(unit, now) = (1 - severity(MoveSlow)) * (1 + severity(SpeedBoost))
sprintBlocked = severity(MoveSlow) > 0.05

SlowZone.Enter(u): if first ref: handle = AddEndless(u, MoveSlow, u.isNpc ? npcS : playerS)
                   if halveOnEnter and (u.airborne or u.sliding): u.vel.xy /= 2
SlowZone.Exit(u):  if --refs == 0: Stop(handle)
```

Unity 参考实现：HSD-Unity PR #53（还没合并）`StatusEffects.cs`（`StatusEffect`、`StatusEffects`、`SeverityCombine { Max, Sum }`）、`MoveSlow.cs`（`MoveSlowMapping`、`MoveSlowCombine`、`SlowZone`、`Electric`、`HalveIfAirOrSliding`；`sprintBlockSeverity = 0.05`）。PR #58 接上电机（§10.5 第 7 条）。

HSD 有意和 R5 本地行为不同（都有开关，PR #58）：黑洞定住 NPC（`holdNpcs = true`，本地实测不定住）；Ash 电弧陷阱拉回（`pull = true`，本地无效）；Shellshock 也给 NPC（`shellshockNpc`）；Crypto EMP 也减速 AI（`slowsAi`）。R5 原值是本地 S3 dedi 上的行为；HSD 改成脚本里的意图，理由是 PvE 需要控制对 NPC 生效（D-59）。这些偏离还没有 D 行，见 `_notes`。

#### 验收

- `CombatFrameworkTests`（HSD-Unity PR #53）：`ATimedEffectFadesLinearlyOverItsLastSecondsThenGoesOff`、`HandlesOfOneTypeCombineByMaxOrBySum`、`TheMeasuredR5SpeedsComeOutOfTheReadBackSeverities`、`ASlowAboveFivePercentBlocksTheSprint`、`SeveralSlowsStackByTheStrongestOrMultiply`、`ASlowZoneCountsOverlapsAndStopsOnTheLastExit`、`EnteringAirborneHalvesTheHorizontalSpeedOnce`、`AnNpcIsImmuneToAStunForThreeSeconds`。
- `CombatControlTests.BlackHoleTimelineAndGroundSpeedAsMeasured`、`StrongestSlowWins`（PR #58）。
- 合格线：W2 §1 的实测速度表由读回严重度算出，差 < 0.1 u/s；同类取最大；冲刺门槛 0.05。

#### 出处

- SE、MS、EMP、A – E：框架、写法、数值。PR #86，还没合并
- W2 §1、§2、§6：减速语义、黑洞、Ash 拴住本地无效。PR #88，还没合并
- DP §8.3：同类取最大、状态效果框架。main
- HSD-Unity PR #53 `StatusEffects.cs`、`MoveSlow.cs`、`Tests/Editor/CombatFrameworkTests.cs`；PR #58 `Control/*`。还没合并

---

## 10.7 伤害修正链、放置物、选目标

#### 原理

这三样是很多技能共用的"零件"，单独写一次，技能只填参数。伤害修正链让"标记加伤""连续命中递减""穿盾"这些规则按固定顺序挂上去，而不是每个技能自己改伤害；放置物统一了"放下、展开、生效、到时、被 EMP 停机、超上限挤掉最旧"的生命周期；选目标统一了"打分取最高"。

#### 规则和公式

1. **伤害修正链顺序**（[推断]）：基础伤害（距离衰减、爆头、穿盾）→ 按伤害来源的修正 → 按攻击者的修正 → 目标自己的修正 → 不致死截到 hp − 1 → 扣血 → 派生伤害再走一遍。
2. 例：Vantage 标记 ×2.5（队友 ×1.15），10 s，第一发不吃；Valkyrie 连续命中 5 s 内 × 0.2；Rampart 穿盾 ×1.2；枪盾溢出把多出来的伤害传给主人（爆炸不传）。
3. **放置物**：放置方式（放下 / 投掷 / 粘附 / 脚本）、展开时间、寿命、血量、每人上限（超了挤掉最旧）、EMP 反应（无 / 伤害 / 停机 15 s / 摧毁）、收回规则。
4. **放置检查**：最远 300 u、坡度 ≤ 50°、往下找地面 72 u、离台沿比例 0.1。
5. **选目标**：最近 / 最居中 / 打分最高。例：Conduit 按护盾缺口 + 距离 + 朝向打分（5 m 内不看朝向，> 50 m 无效）；D.O.C. 选锥内夹角最小（45 m、50°，每 0.1 s，去抖 0.25 s）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 放置最远距离 | 7.62 m | 300 u | 4.167 H | — | [数据] `B-placement.md` |
| 往下找地面 | 1.829 m | 72 u | 1 H | — | [数据] |
| D.O.C. 选目标距离 | 45.0 m | 1771.7 u | 24.61 H | — | [数据] TG |
| 跟随：落后（走 / 冲刺） | 0.505 / 0.89 – 0.935 m | 19.9 / 34.9 – 36.8 u | 0.276 / 0.485 – 0.511 H | 公式 (0.5v − 40)/3 | [实测] W2 §5 |

#### 实现模板

```
Damage(e):
    e.amount = base(e)                        // 衰减、爆头、穿盾
    for m in sim.modifiers ordered by stage (Source, Attacker): m.Modify(e)
    for m in e.target.modifiers: m.Modify(e)
    if e.flags has NonLethal: e.amount = min(e.amount, target.hp - 1)
    target.hp -= e.amount
    for f in e.followUps: Damage(f)

Deployable.Step(now): expire? → OnExpire; deploying? → (invulnerable); first deployed → OnDeployed; Disabled (EMP) → skip Think
```

Unity 参考实现：HSD-Unity PR #53（还没合并）`DamageModifiers.cs`（`IDamageModifier`、`DamageStage`、`MarkAmp`、`RepeatHitFalloff`、`ShieldOverflow`）、`Deployable.cs`（`DeployableSpec`、`DeployableRegistry`）、`Placement.cs`（`PlacementParams`）、`TargetPicker.cs`。

#### 验收

`CombatFrameworkTests.TheChainRunsSourceThenAttackerThenTarget`、`TheMarkAmpsTheMarkersTeamButNotTheFirstShotOrOverflow`、`RepeatHitsOnOneTargetFallOffForFiveSeconds`、`ADeployableDeploysWorksAndExpires`、`AnEmpSwitchesADeployableOffForFifteenSeconds`、`TheRegistryPushesTheOldestOutPerOwnerAndGroup`、`ThePlacerFindsTheFloorAndRejectsTheSky`、`TheDocPicksTheMostCentredNotTheNearest`、`ConduitScoresNeedAndAim`；`CombatSystemsTests.FollowMatchesTheR5MeasuredOffsetLagAndPitch`（PR #53 / #58，还没合并）。合格线：全部通过；跟随偏移和 W2 §5 差 ≤ 1 u。

#### 出处

- DM、TG、`_shared/B-placement.md`、`C-PLACEABLE-DEPLOYABLE.md`、`D-FOLLOW-MOTION.md`。PR #86，还没合并
- W2 §5（D.O.C. 跟随 = 公式）。PR #88，还没合并
- HSD-Unity PR #53 / #58。还没合并

---

## 10.8 泰坦套件的技能模型

#### 原理

泰坦的技能（主武器、进攻、防御、战术、核心）照 TF2 的 `.txt` 写法：每个技能是一行字段，冷却是"弹药式"——有总量、每次消耗、多少才能用、每秒回多少、停多久才开始回。这比"次数 × 秒"更通用：能表达"按住持续消耗"（Ion 的能量）、"用完要等一会儿才回"、"部分充能也能用"。

#### 规则和公式

1. 一套套件 = 底盘（轻 / 中 / 重）+ 5 个槽（主武器、进攻、防御、战术、核心）+ 被动 + 升级（每组一选一）。旧主炮 + 火箭巢的 `legacy` 套件三种底盘都能选，是默认。
2. **弹药式冷却**：`ammo_default_total`、`ammo_per_shot`、`ammo_min_to_fire`、`regen_ammo_refill_rate`（每秒）、`regen_ammo_refill_start_delay`；`hold`（齐射中、墙立着时不回）。
3. **共享能量池**（Ion）：1000，最后一次花费 0.5 s 后以 80 / s 回（实测 80 – 84 / s）；按住型持续扣。
4. **核心表**：按时间和造成的伤害涨，满了激活（180 s、每点伤害 1/6000 是占位）。
5. **打断**：只有"停用"——换套件、离开泰坦时停止并放下手里的东西；换套件 = 重建（技能和资源都是新的、满的）。
6. 时间：套件世界 60 Hz；TF2 脚本里按 `WaitFrame` 计时的事件只在 10 Hz 的服务器帧上做。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| Ion 能量池 / 回复 / 延迟 | — | 1000 / 80 每秒 / 0.5 s | — | 实测 80 – 84 每秒 | [TF2 数据] [TF2 实测] |
| Tone 粒子墙弹药 | — | 140 / 140 / 回 10 每秒（≈ 14 s） | — | — | [TF2 数据] |
| Monarch 火箭齐射 | — | 120 / 每发 20 / 最少 120 / 回 20 每秒 / 延迟 1 s | — | — | [TF2 数据] |
| Vortex 半径 / 角度 | 3.81 m | 150 u、± 60° | 2.083 H | — | [TF2 数据] |

#### 实现模板

```
// 单位：s
KitAmmoCooldown: total, perShot, minToFire, refillRate, startDelay, hold
    CanUse = ammo >= minToFire
    Use(now):   ammo -= perShot; lastUse = now
    Step(now, dt): if not hold and now - lastUse >= startDelay: ammo = min(total, ammo + refillRate*dt)
```

Unity 参考实现：HSD-Unity PR #82（`titan/kits-core`，还没合并）`Titan/Kits/Core/KitDefs.cs`（`AbilityDef`、`KitDef`、`KitModDef`、`KitCatalog`）、`KitResources.cs`（`KitAmmoCooldown`、`KitEnergyPool`、`KitCharge`、`KitCoreMeter`）、`KitHost.cs`、`TitanKitHost.cs`、`Kits/README.md`。已做的槽：Ion Splitter + Vortex；Tone 40 mm + 追踪火箭 + 粒子墙；Monarch 火箭齐射；Scorch 铝热。其余是占位（按下显示"未做"）。中型（PR #85）、轻型（PR #86）另有 PR。泰坦电机还不读减速、相位、拴住、推力。

泰坦的步态、镜头在 [08](08-body-animation.md)、[07](07-camera.md)。

#### 验收

HSD-Unity PR #82 的套件测试（类名见该 PR 的 `Tests/`）；套件的 TF2 弹道和时间线对照在 `tf2/expansion/titan/kits/PROJECTILES.md`（研究 PR #121，还没合并）。合格线：弹药曲线和 `.txt` 字段逐秒一致；Ion 回复 80 / s 落在实测 80 – 84 内。

#### 出处

- `tf2/expansion/titan/kits/README.md` 和 7 份套件页（ION / LEGION / MONARCH / NORTHSTAR / RONIN / SCORCH / TONE）。main
- `tf2/expansion/titan/kits/PROJECTILES.md`、`kits/measure/`。研究 PR #121，还没合并
- HSD-Unity PR #82、#85、#86。还没合并

---

## 10.9 已做的技能一览

#### 原理

每个技能一个文件夹、一份 README（D-14），细节在各自的 README 和第 05 章。这里只给一行概要，方便查"有哪些、在哪、R5 还是 HSD 设计"。

#### 规则和公式

**移动技能**（`U:…/Abilities/<文件夹>/`，main；细节在 [05](05-wall-external.md)）

| 文件夹 | 技能 | 来源 | 一句话 |
|---|---|---|---|
| `Grapple/` | 钩爪 | Pathfinder 战术（S21） | 绳长 850 u；1.5 s 内 50 → 800 u/s；侧键 / 甩出加速；接上 0.2 s 内按跳 = 钩爪跳；蹲或再按 = 松开；视线偏离 > 100° 或经过钩点松开；冷却 10 – 30 s 按距离 |
| `ZiplineGun/` | 滑索枪 | Pathfinder 大招 | 700 – 8000 u 射出一条绳，骑法同地图滑索，升到 1000 u/s，最多 10 条 |
| `Zipline/` | 滑索骑行 | 通用 | 所有绳 |
| `Stim/` | 兴奋剂（含 Wraith 相位倍率） | Octane 战术 | 0.16 s 起效，×1.298 6 s + 0.5 s 淡出，冲刺 421 u/s，复用锁 6.7 s |
| `JumpPad/` | 跳板 | Octane 大招 | 1150 u/s 沿接触时的运动方向（静止时竖直），站 63° / 蹲 45°；低天花板下贴着飞 |
| `PadDoubleJump/` | 跳板二段跳 | Octane | 跳板飞行中空中按跳 |
| `GravityLift/` | 重力升梯 | Horizon 战术 | 300 u/s 上升、顶端悬停，0.5 s 后或离开时弹出 400 / 450 |
| `AirProfile/` | 传奇空中参数 | Horizon 被动 | 空中控制 + 软着陆 |
| `Jetpack/` | VTOL 喷气 | Valkyrie 被动 | 空中按跳；燃料每次 1、每秒 1，落地后每秒回 0.75 |
| `Pounce/` | 暗影突袭 | Revenant 战术 | 掏出 0.9 s + 最多 1.3 s 蓄力，700 – 1150 u/s，沿俯仰 − 35° |
| `Revenant/` | 长攀爬 + 突袭规则 | Revenant 被动 | 攀爬 profile |
| `PhaseBreach/` | 相位突破 | Ash 大招 | 瞄准 + 确认，入口门留 15 s，出门 1.0 s 后可再进 |
| `IntoTheVoid/` | 虚空行者 | Wraith 战术（S21） | 0.37 s 后短暂减速，1.18 – 5.18 s 相位 ×1.596，冷却 25 s |
| `DimensionalRift/` | 次元裂隙 | Wraith 大招（S21） | 按下 1.04 s 后放起点门并自动冲刺，再按（或 6000 u / 10 s）放终点；门留 45 s；穿门沿录下的路径走 0.5 – 3.7 s |
| `VantageEcho/` | Echo 部署 + 喷射位移 | Vantage 战术 | 点按放 Echo，按住喷向 Echo；位移中禁止翻越 |
| `Teleport/` | M5 传送原语 | Loba / 旧传送门 | 部分实测，余下 [设计] |
| `WallJump/` | 蹬墙跳 | 通用 | 碰墙 0.1 s 内空中按跳，+n̂·182.78 + d̂·75.08 |
| `Climb/` | 攀爬、翻越、superglide、悬挂 | 通用；悬挂 HSD | [04](04-slide-mantle.md) |
| `LandingSlowdown/` | 硬着陆减速 | 通用 | [03](03-ground-air-jump.md) |
| `WallRun/`、`DoubleJump/`、`DoubleJumpTf2/` | 跑墙、二段跳、TF2 二段跳 | HSD / TF2 | [05](05-wall-external.md) |
| `SlopeSlide/`、`Flight/`、`GravitySwitch/` | 斜坡滑铲、飞行、重力切换 | HSD（Fun） | [设计] |

**铁驭战斗技能和道具**（main 上是 TF2X 占位层 `U:…/Combat/`；公共框架 HSD-Unity PR #53，四批技能 PR #58，都还没合并）

| 层 | 内容 |
|---|---|
| main（TF2X） | 隐身、A 型墙、扫描、分身、地图透视、重力星、破片、电弧星、铝热剂、炸药包、悬停、相位回溯、蜘蛛雷、哨戒炮、增幅武器、能量电池等（PL 的去向表） |
| PR #58 投掷 / 区域 | 滚雷、防御轰炸、集束弹、火焰环、毒气陷阱、毒气手雷、钻头、破坏球 |
| PR #58 控制 | 黑洞、电网、拦截塔、电弧陷阱、尖刺、黑幕、能量屏障、城墙 |
| PR #58 投射 / 掩体 | 导弹群、狙击标记、Sheila + 加强掩体、护罩 + 枪盾、注视焦点、呼啸弹 |
| PR #58 系统 | 补给舱 / 空投刷兵、D.O.C.、Crypto 无人机、无人机 EMP、Mirage 分身和大招、Death Totem + Forged Shadows |

技能研究的筛选：41 份记录，保留 20、防御待定 5、参考 15、不要 6（C0、D-78，PR #86）。搁置的：Loba 手环传送、Alter 虚空通道（SH）。暂缓的设计：E1 两种二段跳能否同时装、E2 Fun 斜坡滑铲平衡、E3 跳跃输入缓冲（DEF）。

#### 实现模板

新技能：建 `Abilities/<技能名>/`（移动技能）并写 README（来源、证据等级、参数表、测试）；参数类和技能放一起；被多个技能用的接口放 `_Core/`（D-14）。战斗层目前按批平铺，不符合 D-14（`_notes`）。

#### 验收

每个文件夹 README 列它的测试；移动技能的回放对照在 `research/feel/FEEL.md` §7（M4 技能批）。

#### 出处

- `U:…/Abilities/README.md`（文件夹表）、`_Core/SkillRules.cs`（`SkillLoadouts` 的描述文字）。main
- PL（TF2 铁驭技能的去向）。main
- C0、A – E、`<技能>/SYSTEM.md`。PR #86，还没合并
- HSD-Unity PR #53、#58、#82。还没合并

---

# 第二部分 敌人 AI

**这一部分没有参考实现**。规则来自 TF2：设置文件和行为树文件（[TF2 数据]）、`server.dll` 反编译（[反编译]）、本地 Northstar 私服实测（[TF2 实测]：地图 `mp_lf_stacks`、`tdm`、难度 Low、NPC 熟练度被 Northstar 固定为 VERYGOOD）。R5 本地 NPC 不开火（W2 §0、DP §10.3），**AI 没有 R5 参考**。

## 10.10 AI 的三层结构

#### 原理

TF2 的敌人不是一大段 if-else，而是三层：**数**（每种敌人的视野、反应时间、血量、追多远）写在设置表里；**选做什么**写成一棵按优先级排的"选择器"清单；**怎么做**写成一张张"计划"（一串任务 + 什么情况打断）。换一种敌人通常只换数和清单顺序，计划是共用的。这让"新敌人"主要是填表。

#### 规则和公式

1. **设置表**（aisettings）：每种 NPC 一份，有继承；146 个文件解析出 145 种 NPC。
2. **行为树**：每种 NPC 一棵，分块 `Common`、`Idle`、`Alert`、`Combat`（泰坦、Reaper、AI 铁驭另有 `CombatAggressive` / `CombatEvasive`）。36 棵树、66 种选择器。
3. **决策流程**：
   1. 先从上到下试 `Common` 块；没有一个要行动，再试当前状态块（Idle = 没敌人没动静；Alert = 有可疑的、没确认敌人；Combat = 有敌人）。
   2. 第一个"想行动"的选择器返回一个计划。选择器可带条件，只有 `health > x` / `health < x` 两种形式。
   3. 按顺序执行计划的任务；任何一个打断条件成立就丢掉计划、从头重选；计划完成或失败也重选。计划可指定"失败了做 x""做完了做 x"。
4. **计划表**：126 个计划、122 种任务、55 种条件。
5. **循环周期**：

| 循环 | 周期 | 依据 |
|---|---|---|
| NPC 瞄准更新（每次都问一次"这次要不要打偏"） | 约 0.05 s | [TF2 实测] AL L-2（38 发 ↔ 348 次回调） |
| 扫描玩家（发现进度只在这里推进） | ≥ 0.15 s 一次 | [反编译] RN §2 |
| 重选计划 | 计划完成 / 失败 / 被打断时 | [推断] AS §3.1 |
| 远程攻击小动作的冷却 | 6 – 7.5 s 随机 | [反编译] AL N-7 |
| Tick 追击循环 | 0.1 s | [TF2 数据] AS §2.10 |

#### 实现模板（没有参考实现）

```
// 单位：u、s
class Npc:
    settings: AiSettings                     // 一种敌人一份，数据驱动
    tree: { Common: [Selector], Idle: [...], Alert: [...], Combat: [...] }
    state: Idle | Alert | Combat
    schedule: Schedule?; taskIndex

Think(now):
    if schedule == null or schedule.done or schedule.failed or any(c() for c in schedule.interrupts):
        schedule = Select()
    RunTask(schedule.tasks[taskIndex])

Select():
    for sel in tree.Common + tree[state]:
        if sel.condition(self) and (s = sel.Choose(self)): return s
    return IdleStand
```

建议放在 Unity 的 `Assets/HSD/Game/Runtime/AI/`（新文件夹，[设计]）：`AiSettings`（ScriptableObject 或 JSON，字段名沿用 TF2 键名，加 `[u]` 标记）、`BehaviorTree`（选择器清单是数据）、`Schedule` / `Task` / `Condition`（计划表也做成数据，照 `tf2/pve/data/schedules.tsv` 导入）。导航用 Unity NavMesh，掩体点用场景里摆的提示点（TF2 的 hint）。

#### 验收

还没有测试。建议的测试（名字是建议，还没有）：`AiTreeTests.CommonBlockWinsOverStateBlock`、`AiTreeTests.InterruptReselectsFromTheTop`、`AiImportTests.SchedulesTsvRoundTrips`（导入后 126 个计划、55 种条件不丢）。合格线：导入的树和计划与 `behavior-trees.tsv`、`schedules.tsv` 逐行一致。

#### 出处

- AS §1、§3.1、§4.1；BT（生成的全表）。main
- `tf2/pve/data/aisettings-resolved.tsv`、`behavior-trees.tsv`、`schedules.tsv`、`bt-users.tsv`；工具 `tf2/pve/tools/kv_resolve.py`、`bt_sched.py`。main
- AL L-2、N-7。main
- RN §2。PR #115，还没合并

---

## 10.11 感知：看见和发现

#### 原理

敌人不是一进视野就开火。它要先"注意到"你：离得越远、越在视野边上，注意到得越慢；短暂挡住视线，进度不会立刻清零；被注意过的人回来时立刻认出。这给了玩家"在被发现之前"的时间窗口，也是潜入和侧绕成立的前提。

#### 规则和公式

1. **视野**：按状态（Idle / Alert / Combat）和距离分近 / 远两组角度（水平 × 竖直，全角）。近于 `FOV_Near_Dist` 用近角，远于 `FOV_Far_Dist` 用远角，中间**水平角插值、竖直用远角**。视野中心向下偏 20°（`FOV_Vert_Offset` −20，"高处的铁驭感觉更好"）。
2. **扫描**：两次扫描之间至少 0.15 s。每次对每个通过视野和视线检测的玩家：
   - 如果这个 NPC 记得他、且距上次看见 < `NoticeForgetPostTime`（5 s）：**立刻发现**；
   - 否则找到或新建一条"正在注意"记录（新建时记开始时刻）；
   - 按 3D 距离 d 取需要的时间 T：d ≤ `NoticeDistNear` 用 `NoticeTimeNear`，d ≥ `NoticeDistFar` 用 `NoticeTimeFar`，中间线性插值；
   - 如果 T < `NoticeTimePeripheral` 且玩家偏离 NPC 正前方 > 30°：T = `NoticeTimePeripheral`；
   - 从开始已经过了 T：**发现**，删记录；否则更新"上次看见"、NPC 转头看向玩家。
3. 扫描后，"上次看见"距今 ≥ `NoticeForgetPreTime` 的记录删掉（进度从 0 重来）。
4. 列取 NPC 当前的状态（Idle / Alert / Combat）。"看见""当作敌人""进入战斗"在同一帧发生。
5. 断视线：`CanSee` 在 0.03 – 0.17 s 内变 0，最多再开 1 枪；14 s 内不会忘记（遗忘时间推断是 ConVar `ai_enemy_discard_time` 60 s，没测到 60 s）。
6. 没有听觉键；听觉半径在原生代码里。

**士兵（MP）的数**（spectre 相同；"MP / SP"）

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| `FOV_Near_Dist` / `FOV_Far_Dist` | 3.81 / 50.8 m | 150 / 2000 u | 2.083 / 27.78 H | stalker 350 / 1000 | [TF2 数据] AS §5.2 |
| Combat 视野 近（水平 × 竖直） | — | 130 / 180° × 180 / 80° | — | — | [TF2 数据] |
| Combat 视野 远 | — | 100° × 60° | — | — | [TF2 数据] |
| `NoticeDistNear` Idle / Alert / Combat | 3.81 / 7.62 / 7.62 m | 150 / 300 / 300 u | 2.083 / 4.167 / 4.167 H | — | [TF2 数据] |
| `NoticeDistFar` Idle / Alert / Combat（MP） | 50.8 / 38.1 / 50.8 m | 2000 / 1500 / 2000 u（SP 2000 / 1800 / 2500） | 27.78 / 20.83 / 27.78 H | — | [TF2 数据] |
| `NoticeTimeNear` Idle / Alert / Combat（MP） | — | 0.1 / 0.1 / 0.0 s（SP 0.5 / 0.2 / 0.1） | — | — | [TF2 数据] |
| `NoticeTimeFar` Idle / Alert / Combat（MP） | — | 1.0 / 1.0 / 1.0 s（SP 2.0 / 0.75 / 0.5） | — | — | [TF2 数据] |
| `NoticeTimePeripheral`（MP） | — | 0.7 s（SP 2.0 / 1.0 / 0.75） | — | — | [TF2 数据] |
| 外围角 | — | 30°（点积 < 0.866） | — | — | [反编译] RN §2 |
| `NoticeForgetPreTime` / `PostTime` | — | 1.0 / 5.0 s（原生默认 0.3 / 5.0） | — | — | [TF2 数据] [反编译] |
| 扫描间隔下限 | — | 0.15 s | — | — | [反编译] RN §2 |
| `LookDistDefault` Idle / Alert / Combat | 38.1 / 76.2 / 127 m | 1500 / 3000 / 5000 u | 20.83 / 41.67 / 69.44 H | — | [TF2 数据] |

**实测**（新刷的 Idle MP 士兵，感知先关后开，玩家站着看它；从开感知算起）

| 情况 | 发现 | 转向玩家 | 第一枪 |
|---|---|---|---|
| 正前方 250 u（6.35 m，3.472 H） | 0.37 s | 0.07 s | 3.27 s |
| 正前方 800 u（20.32 m，11.11 H） | 0.75 s | 1.15 s | 4.35 s |
| 正前方 1400 u（35.56 m，19.44 H） | 1.33 s | 1.33 s | 6 s 内没有 |
| 侧面 100°，400 u | 0.77 s | 1.27 s | 3.37 s |
| 背后 180°，200 u | 1.73 s | 1.63 s | 2.93 s |
| 隐身，正前方 400 / 900 u | 6 s 内没有 | — | — |

两条没解释的：正前方发现 ≈ 0.3 s + 0.00072 s/u，按设置插值的斜率只有 0.00049 s/u（扫描量化只能解释 0.15 – 0.35 s 的偏移，解释不了斜率）；130° 视野以外（侧 100°、背后）也能在 0.8 – 1.7 s 发现（听觉？距离？）。

#### 实现模板（没有参考实现）

```
// 单位：u、s、°
every scan (now - lastScan >= 0.15):
    for p in players where InFov(p) and LineOfSight(p):
        if remembers(p) and now - lastSeen[p] < NoticeForgetPostTime: Notice(p); continue
        e = noticing.getOrCreate(p, start = now)
        d = |p.pos - pos|
        T = d <= nearDist ? nearTime : d >= farDist ? farTime : lerp(nearTime, farTime, (d-nearDist)/(farDist-nearDist))
        if T < peripheralTime and dot(forward, dir(p)) < cos(30°): T = peripheralTime
        if now - e.start >= T: Notice(p); noticing.remove(p)
        else: e.lastSeen = now; TurnHeadToward(p)
    noticing.removeWhere(now - e.lastSeen >= NoticeForgetPreTime)

InFov(p): fovH = d < nearFovDist ? nearH : d > farFovDist ? farH : lerp(nearH, farH, ...)
          fovV = d < nearFovDist ? nearV : farV           // 竖直不插值
          view = forward pitched down by 20°
```

#### 验收

还没有测试。建议：`AiPerceptionTests.DetectionTimeInterpolatesByDistance`（150 / 1000 / 2000 u 三点）、`PeripheralFloorAppliesOutside30Degrees`、`RememberedPlayerIsNoticedInstantlyWithin5s`、`ProgressResetsAfterForgetPreTime`。对照数据：上面的实测表（`tf2/pve/data-live/percept.tsv`）。合格线：正前方 250 / 800 / 1400 u 的发现时间和实测差 ≤ 0.15 s（一个扫描间隔）——**按设置表插值做不到 800 / 1400 u 这一档**（差 0.3 – 0.6 s），要先研究斜率（B10-3）。

#### 出处

- AS §5.1、§5.2：键和数。main
- RN §2：发现进度的原生算法。PR #115，还没合并
- AL L-3、L-4、L-5：发现时间、断视线、隐身。main
- `tf2/pve/data-live/percept.tsv`（运行 `20261108_134837_ai_percept`）。main
- [反编译] TF2 `server.dll`：发现 0x1803b5b70；扫描玩家 0x1803b4a80（视野虚函数 +0x8a0、视线掩码 0x84081）；清理 0x1803b38f0；0.15 s 常量 0x18089f31c；设置偏移 `NoticeForgetPreTime` +0xa3c、`PostTime` +0xa40、`NoticeDistNear/Far` +0xa44 / +0xa50、`NoticeTimeNear/Far` +0xa5c / +0xa68、`NoticeTimePeripheral` +0xa74。

---

## 10.12 命中和打偏：对快速铁驭故意打偏

#### 原理

TF2 的核心承诺是"跑起来就更安全"。它不靠玩家真的躲开子弹，而是规定：**玩家处在快速状态（跑墙、空中、速度 > 180 u/s）时，敌人有固定比例的子弹会被瞄到玩家身旁的空处**。打偏的点就在玩家身边 30 – 80 u，子弹看起来擦身而过，玩家感觉"差点被打中"，但不会真受伤。这条规则让高速移动在 PvE 里有明确的生存价值，也是 HSD 移动手感在战斗里"有用"的关键。

#### 规则和公式

1. **快速铁驭**：挂墙 → 否；跑墙 → 是；不在地上 → 是；速度（3D，平滑或当前）> 180 u/s → 是；否则否。滑铲只有速度 > 180 才算。
2. **要不要问"打偏"**：敌人在 1.0 s 内被看见过、敌人是玩家、武器 `npc_miss_fast_player` 为真、注册了打偏回调。每次瞄准更新（约 0.05 s）问一次，子弹用最近一次的答案。
3. **打偏回调**（Northstar MP 版，HSD 采用这一版）：
   - 难度档 L：0 VeryLow、1 Low（默认）、2 Medium、3 High、4 VeryHigh；
   - 玩家在泰坦里 → 不打偏；
   - 玩家正在执行情境动作（上泰坦、处决…）→ 75 % 打偏；
   - 快速铁驭：命中机会 = (L + 1) × 0.125；L ≤ Medium 且 NPC 是机械类时再 ÷ 1.25；随机数 ≥ 命中机会 → 打偏；
   - 否则不打偏。
4. **战役版**（备选）：快速铁驭固定 50 % 打偏。
5. **打偏点**：以玩家脚底为基准；s = 垂直于"NPC → 玩家"的水平单位向量，u ≈ 向上。按玩家朝向和"NPC → 玩家"方向的夹角 rel 选位置：|rel| < 45°（背对 NPC 跑开）左 / 右 / 上三选一；45° ≤ |rel| < 135°（侧着跑）只选玩家跑去的那一侧（跑在前方）；|rel| ≥ 135°（迎面）左 / 右 / 上 / 下四选一。**打偏不加散布**。
6. 不打偏 → 瞄玩家的瞄准点（可带提前量）+ 散布（§10.13）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 快速铁驭速度门槛 | 4.572 m/s | 180 u/s | 2.5 H/s | — | [TF2 数据] AS §7.1 |
| 快速铁驭命中机会：Low（默认）/ 机械类 | — | 0.25 / 0.2 | — | VeryLow 0.125 … VeryHigh 0.625 | [TF2 数据 NS] AS §7.3 |
| 战役版命中机会 | — | 0.5 | — | — | [TF2 数据] AS §7.2 |
| 情境动作中打偏 | — | 75 % | — | — | [TF2 数据 NS] |
| "最近被看见"窗口 | — | 1.0 s | — | — | [反编译] AL N-1 |
| 打偏点：左 / 右 横向 | 0.762 – 2.032 m | ±(30 … 80) u | 0.417 – 1.111 H | — | [反编译 + 实测] AL N-1 |
| 打偏点：左 / 右 竖向（脚底起） | −0.508 – 2.032 m | −20 … 80 u | −0.278 – 1.111 H | — | 同上 |
| 打偏点：上（眼睛起） | 横 ±1.27 m，竖 +0.508 – 1.016 m | 横 −50 … 50 u，竖 +20 … +40 u | — | — | 同上 |
| 打偏点：下（脚底起） | 竖 −0.508 – −1.016 m | 竖 −20 … −40 u | — | — | 同上 |

HSD 目前没有定用哪个版本、哪个难度。手册建议默认 Northstar MP 版、L = Low（FD 也是 Low），写进 `_notes` 的建议 D 行。

#### 实现模板（没有参考实现）

```
// 单位：u、s
IsFastPilot(p) = !p.wallHanging and (p.wallRunning or !p.grounded or |p.vel| > 180)

OnAimUpdate(npc, now):                         // 每约 0.05 s
    e = npc.enemy
    npc.forceMiss = e.isPlayer and npc.weapon.missFastPlayer and now - npc.lastSeen(e) < 1.0
                    and ShouldMiss(npc, e)

ShouldMiss(npc, p):
    if p.inTitan: return false
    if p.inContextAction: return rand() >= 0.25
    if IsFastPilot(p):
        chance = (L + 1) * 0.125
        if L <= Medium and npc.mechanical: chance /= 1.25
        return rand() >= chance
    return false

FireBullet(npc):
    if npc.forceMiss: dir = toward(MissPoint(npc, p))          // 不加散布
    else:             dir = Spread(toward(aimPoint(p) + lead), npc)   // §10.13
```

#### 验收

- 对照数据：AL L-1 的命中率表（`tf2/pve/data-live/hit_soldier_r201.tsv`、`hit_spectre_r201.tsv`、`hit_stalker_lstar.tsv`）。士兵 + R-201、< 500 u：

  | 玩家状态 | 发数 | 命中 / 发 |
  |---|---|---|
  | 站着 | 171 | 0.509 |
  | 走（174 u/s，不算快速） | 37 | 0.135 |
  | 冲刺 | 23 | 0 |
  | 空中 | 92 | 0.174 |
  | 跑墙（三种敌人合计 48 发） | 9 | 0 |

- 读法：快速状态命中明显低（空中 0.17 对站着 0.51，规则预测约 0.5 × 0.25 ≈ 0.13）；**走路单独就把 R-201 降到约 1/3**，因为瞄准每 0.05 s 按当前位置、没有提前量；L-STAR 有提前量（0.0005），走路不受影响（0.43 对 0.44），冲刺还有 0.3 – 0.4（侧着跑时打偏点放在跑者前方 30 – 80 u）；跑墙 48 发 0 中。
- 实测回调：46 / 46 次回调和规则一致（`ai_scout`，AL N-1）。
- 建议的测试（还没有）：`AiMissTests.FastPilotMissRateIsThreeQuartersAtLow`（10 000 次 ±1 %）、`MissPointSideFollowsRunDirection`、`WallHangIsNotFast`。
- 合格线：近距（< 500 u）各状态的命中率落在实测的 95 % 置信区间内（每格约 ±0.1 – 0.15）；中远距只有个位数到 20 发，暂不作合格线（B10-3：AI1）。

#### 出处

- AS §7.1 – §7.3、§7.7：快速铁驭、打偏回调、武器键。main
- AL N-1、N-3、L-1、L-2：原生打偏流程、打偏点、命中率表、回调频率。main
- `tf2/pve/data-live/hit_*.tsv`。main
- [反编译] 每发方向 `FUN_1802ee970`；打偏闸门 `FUN_18030d520`（敌人记忆"上次看见" +0x2c、武器 `npc_miss_fast_player` +0x758）；打偏点 `FUN_1802fc2e0`；瞄准点 `FUN_1802ee650`。ConVar `ai_missFastPlayer_sideWindowY/ZMin/Max`、`topWindowY/ZMin/Max`。

---

## 10.13 散布和瞄准收拢

#### 原理

敌人刚盯上你的时候打得散，盯得越久越准；而且刚开始的子弹偏向散布圈的**边缘**，看起来"擦着过"。这给玩家一个"被盯上之后还有几秒反应"的窗口。不在玩家视野里的敌人散布更大——从背后被偷袭不该一下就死。

#### 规则和公式

1. 子弹方向 = 瞄准方向 + tan(散布半角) × 单位圆盘里的随机点（按偏向 bias 的形状）。
2. 散布半角 = `proficiency_<档>_spreadscale` × 收拢系数 ÷ 精度倍率；没武器时 15°。
3. **收拢系数**：focus = 1 + (b − 1) × (1 − t / a)（t < a），t ≥ a 时为 1；t = 从开始盯这个敌人算起的时间（[推断]，没验证）。默认 a = 10 s、b = 2.0。
4. **偏向**：bias = `proficiency_<档>_bias` × min(1, t / 8 s)；NPC 不在玩家视野里、且 t < 2.5 s 时再 × 0.2。bias 1 = 集中在中心，0.5 = 均匀，0 = 集中在边缘。
5. 熟练度档：POOR 0、AVERAGE 1、GOOD 2、VERYGOOD 3、PERFECT 4。Northstar MP 的士兵类固定 VERYGOOD。
6. 连发：每串 `npc_min_burst` – `npc_max_burst` 发，串间休息 `npc_rest_time_between_bursts_min` – `max` + `proficiency_<档>_additional_rest`。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 收拢时间 a / 初始倍率 b | — | 10 s / ×2.0 | — | SP Easy 8 / 3.5 … Master 0.2 / 1.0 | [反编译] AL N-2、[TF2 数据] AS §7.5 |
| 偏向爬升时间 / 视野外时间 / 视野外系数 | — | 8 s / 2.5 s / 0.2 | — | — | [反编译] AL N-2 |
| R-201 spreadscale POOR / AVG / GOOD / VG（MP） | — | 5.0 / 2.0 / 3.0 / 2.5 | — | SP 单调 5.0 / 3.5 / 3.0 / 2.5 / 1.75 | [TF2 数据] AS §7.7 |
| R-201 射速 / 每串 / 串间休息 | — | 13.5 发 / s、2 – 4 发、0.5 – 0.8 s | — | — | [TF2 数据] |
| R-201 NPC 伤害 近 / 远（MP） | — | 10 / 8 | — | 玩家用 25 / 17 | [TF2 数据] |
| R-201 NPC 最远射程（MP） | 63.5 m | 2500 u | 34.72 H | SP 4000 u | [TF2 数据] |

R-201 MP 的 AVERAGE（2.0）比 GOOD（3.0）还准，文件里就是这样写的（SP 是单调的）；HSD 用哪一组要定（`_notes`）。

#### 实现模板（没有参考实现）

```
// 单位：°、s
Spread(dir, npc):
    t = now - npc.trackStart(enemy)
    focus = t < a ? 1 + (b - 1) * (1 - t / a) : 1
    half = weapon.spreadscale[npc.tier] * focus / max(1e-5, npc.accuracy)
    bias = weapon.bias[npc.tier] * min(1, t / 8) * (notInPlayerView and t < 2.5 ? 0.2 : 1)
    return dir + tan(half) * DiscPoint(bias)

DiscPoint(bias):                               // Source 的形状
    k = |2*bias - 1| * 0.5
    repeat: x = r1*k + r2*(1-k); y = r3*k + r4*(1-k)     // r ∈ [-1, 1]
    until x² + y² <= 1
    if bias < 0.5: push (x, y) toward the edge
```

#### 验收

建议的测试（还没有）：`AiSpreadTests.FocusGoesFromTwoToOneInTenSeconds`、`BiasZeroLandsOnTheEdge`。合格线：公式逐点一致。实测只能间接对照（L-1 命中率表），没有直接测过散布角（缺口）。

#### 出处

- AL N-2；AS §7.4、§7.5、§7.7；`tf2/pve/data/weapon-npc-keys.tsv`（111 把武器）。main
- [反编译] 散布角 `FUN_1802eec90`（盯住开始时刻 = 敌人记忆 +0x44；熟练度表在武器数据 +0x1c24，每档 12 字节）；偏向 `FUN_1802f0e80` + `FUN_180264110`。ConVar `ai_shot_bias`。

---

## 10.14 行为：选择器、计划、掩体、追击、闪避、小队

#### 原理

士兵的"打法"是一条优先级清单：先处理摔倒、受惊、躲危险区；进了战斗，能近战就近战，有掩体就去掩体打，看不到就追，追到能开枪就停。不同敌人只是清单顺序和几个数不同：stalker 不找掩体、直接走过来；Reaper 先闪避导弹、再跳、再冲。

#### 规则和公式

1. **士兵 MP 的 Combat 块顺序**：对付大型敌人 → 近战 → 掩体射击 → 追击 → 新敌人 → 弹药少时规避 → 去小队指定点 → 规避射击 → 射击小动作 → 远程攻击 → 敌人被挡住 → 打不到 → 面向敌人。Common 块：摔倒 → 受击 → 躲危险区 → 被跳过 → 发现隐身 → 受惊 → 子弹擦过 → 友方玩家 → 害怕 → 换姿态 → 同步近战 → … 。
2. **掩体射击**：以 NPC（或攻击点）为中心，直线半径 1200 u 内、导航路径 ≤ 2500 u 的掩体提示点，最多 64 个按路径排序；打分：0 = 不可用（敌人比 `shootingCoverFightRadius` 近、敌人不在提示点朝向内），1 = 能站 / 蹲但打不到，2 = 射击位到敌人眼睛的射线 ≥ 50 % 通畅，3 = ≥ 99 %。射击位 = 提示点 + 朝向 × 1.5 × NPC 宽度。没路径 4 s 内不重试。
3. **追击**：小队里已有 2 个追击者就不追；"够近了"= 被挡住且距离 < 停止距离 + 自身半径，或水平够近且高差在范围内，或最后已知位置到不了。追击计划在"能开枪"时被打断。
4. **闪避闸门**：这一周期的闪避次数 < `maxDodgePerPeriod`，距上次 ≥ `minConsecutiveDodgeTime`；侧闪由受伤触发，前闪在距离 ≥ max(800, 交战距离 + 闪避长度) 时。
5. **射击小动作**：距离 ≥ 300 u、冷却到了；下次冷却 = 6 × [1, 1.25] s。
6. **小队**：同一帧同一队刷出、没写小队名的多个 NPC 自动成一队；空投舱 4 个一队。
7. AI 铁驭**不跑墙、不二段跳**（树里没有，L-7 实测）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 掩体搜索半径（直线） | 30.48 m | 1200 u | 16.67 H | 攻击点战斗半径 | [反编译] AL N-4 |
| 掩体导航路径上限 | 63.5 m | 2500 u | 34.72 H | — | [反编译] AL N-4 |
| 每小队追击者上限 | — | 2 | — | ConVar `ai_squad_num_chasers` | [反编译] AL N-5 |
| 前闪距离门槛 | 20.32 m | 800 u | 11.11 H | `dodgeForwardThreshold` | [反编译] AL N-6 |
| 射击小动作最近距离 | 7.62 m | 300 u | 4.167 H | — | [反编译] AL N-7 |
| 士兵：近战伤害 / 距离（MP） | 1.016 m | 30 伤害、40 u | 0.556 H | SP 53 / 60 u | [TF2 数据] AS §2 |

**实测行为参考**（AL L-6，玩家站着 / 平移 / 跳，敌人 450 – 700 u）：士兵第一枪 4.2 s、30 s 走 415 u、最快 132 u/s；stalker 1.2 s、最快 110 u/s；Reaper 不开枪、冲锋最快 710 u/s、长跳离地最高 185 u；AI 铁驭 1.3 s、一直在地上。士兵 150 s × 3 的计划次数：面向 159、建立射线 140、开火 125、串间等 96、去掩体 80。

#### 实现模板（没有参考实现）

照 §10.10 的框架，把士兵的树写成数据：

```
soldier.tree.Combat = [AntiMassiveEnemy, MeleeAttack, ShootingCover, ChaseEnemy, CombatNewEnemy,
                       EvasiveLowAmmo, MoveToSquadAssignedNode, RangeAttackEvasive, RangeAttackTwitch,
                       RangeAttack, CombatOccludedEnemy, EnemyNotAttackable, CombatFace]
ShootingCover.Choose(npc):
    hints = NavSearch(center = npc.pos, radius 1200, pathMax 2500, limit 64)
    best = first 3 by score (3 > 2 > 1); after a 1 look 900 u further, after a 2 look 450 u further
    return best ? MOVE_TO_SHOOTING_COVER(best) : null
```

先做士兵一种（MP 版），其他敌人复用选择器、只换清单和数。

#### 验收

建议的测试（还没有）：`AiCoverTests.ScoresByRayClearance`、`AiChaseTests.AtMostTwoChasersPerSquad`。对照数据：L-6 的参考录像摘要（`tf2/pve/data-live/ref_summary.txt`）——第一枪时间、移动距离、最快速度、计划次数。合格线：建议士兵第一枪时间落在 3 – 4.5 s（实测 3.27 – 4.35 s）；其余先只记录不判（行为和地图有关）。

#### 出处

- AS §3.2、§4.2；BT（全表）。main
- AL N-4 – N-7、L-6、L-7。main
- [反编译] `SelectSchedule_ShootingCover` `FUN_18034cff0`、找掩体 `FUN_18031c810`、打分 `FUN_18031cfc0` / `FUN_180325d00` / `FUN_180325ba0`；`SelectSchedule_ChaseEnemy` `FUN_1803226c0`；闪避闸门 `FUN_1802e3ba0`；射击小动作 `FUN_1803242b0`。

---

## 10.15 敌人种类和出场

#### 原理

种类少而分工清楚：士兵是主力，盾牌队长和 specialist 是士兵的变体，spectre 是机械版士兵，stalker 是"走过来"的压力，Reaper 是重型近战，tick 是自爆，无人机在空中。出场方式（空投舱、Reaper 天降、泰坦降落）本身就是预告：落地前有几秒的提示和无敌。

#### 规则和公式

| 种类 | 血量（MP / SP） | 武器 | 要点 |
|---|---|---|---|
| 士兵 | 50 / 90 | R-201；破片手雷 | MP：总在警戒、跟着小队、不巡逻 |
| 盾牌队长 | 350 / 150 | LMG | 个人护盾 620、正面 105°、15 s 重建，EMP 一下打掉；贴近 30 – 50 u 电击 1.5 s |
| specialist | 120 | L-STAR | 扔 tick、召唤等离子无人机 |
| spectre | 100 / 130 | R-201 | 机械、可被黑入 |
| stalker | 150 / 250 | L-STAR | 不找掩体；打背包 → 倒地爬行 → 连环小爆 → 大爆；打断腿 → 爬行，血量设为 50 %，16 s 后自爆 |
| Reaper | 3500 / 3000 | 臂炮 | 重甲，只有弱点；每 6 s 闪避 1 次（MP）；长跳 600 – 1000 u，每 8 – 15 s；MP 不放 tick、死了不核爆 |
| tick | 110 / 45 | — | 受到任何伤害开始过载；触发距离 200 u、高差 ≤ 40 u；死亡 = 爆炸 |
| 无人机 | 100 / 90 | 光束 / 等离子 / 火箭 | 战斗最快 600 u/s，悬停 100 u，离主人 ≤ 768 u；EMP 后 5 s 重启 |
| AI 铁驭 | 250 | R-97 | VERYGOOD；每 4 s 闪避 2 次；不跑墙、不二段跳 |
| NPC 泰坦 | 按底盘 7500 / 10000 / 12500 | — | 护盾 2500；每 8 s 闪避 2 次 |

共同：部位伤害倍率只在攻击者是玩家时生效，取**玩家武器**的爆头倍率；MP 每第 3 个刷出的士兵 / spectre 拿火箭筒（AS §2.6 写"每 4 个"是旧的，以 §2.1.6 为准）。HSD 的占位血量：铁驭 100、AI 士兵 100、泰坦 2500、炮塔 300（D-61）。

**出场**

| 出场 | 时间线 | 依据 |
|---|---|---|
| 空投舱 | 4.97 s 落地动画，4.87 s 撞地，5.07 s 开门 4 人出来；出口 1.63 – 2.80 s；最后一个出来 10 s 后清掉舱 | [TF2 实测] AL L-8 |
| Reaper 天降 | 隐身无敌，+0.9 s 可见，0.2 s 下落（5000 u/s），+1.1 s 解除无敌 + 落地伤害 400（r 90 / 256）；Northstar 加 4.7 s 地面标记预告 | [TF2 数据] [TF2 实测] |
| NPC 泰坦降落 | 动画 6.67 s，撞地 5.03 s，起身 2.5 s，约 9.2 s 开始行动；起身完之前不能被锁定；泡泡盾 r 240 到起身后 3 s | [TF2 实测 + 数据] |

#### 实现模板（没有参考实现）

种类 = 设置表 + 树 + 少量专属脚本（护盾、爬行、自爆、天降）。专属脚本写成和计划并列的"组件"，不进选择器清单。出场写成时间线（每一步：动画、无敌、可锁定、伤害、预告），数据驱动。

#### 验收

建议的测试（还没有）：`AiEntranceTests.DropPodTimelineMatchesTf2`（撞地 4.87 s、开门 5.07 s，差 ≤ 1 帧）。合格线：时间线逐项一致；血量按 HSD 占位（D-61）。

#### 出处

- AS §2（各种类）、§6（出场）。main
- AL L-8（出场实测）。main
- D-61（占位血量）。main

---

## 10.16 FD 规则（Frontier Defense）

#### 原理

FD 是 TF2 的 PvE 模式：4 名玩家守一台"收割机"，敌人一波一波来，波间买装备。它是 HSD 做 PvE 时最直接的现成参考：难度怎么分档、一波怎么开始结束、经济怎么给、哪些敌人专门冲收割机。**本地只有客户端脚本、数据表和 playlist，每一波的具体内容和服务器逻辑都没有**，所以这里只有框架。用户 11-09 定 FD "到此为止"（REF-TESTS-1112 §3 记的，出处 D 行没找到，见 `_notes`）。

#### 规则和公式

1. **难度**（easy / normal / hard / master / insane）：泰坦血量调整 −5000 / −2500 / 0 / 0 / 0；Reaper −2000 / −1000 / 0 / 0 / 0；带反泰坦武器的士兵 0 / 0 / 2 / 4 / 4；盾牌队长 0 / 0 / 0 / 1 / 1；玩家受伤倍率 1.0 / 1.0 / 1.5 / 2.5 / 2.5；收割机护盾 6000 / 6000 / 5000 / 4000 / 4000；每波钱 700 / 700 / 600 / 600 / 600。变量含义是 [推断]（服务器代码缺）。
2. **共同**：收割机血量 25000，受伤 10 s 后开始回、10 s 回满；买东西时间 60 s；4 名玩家；复活 4 s；泰坦充能 240 s。
3. **波次状态机**：0 无、1 将要来、2 进行中、3 完成、4 休息；每张图推断 5 波。收割机被毁 → 这一波重来（推断 2 次重试，insane 0 次）。
4. **FD 专用敌人**：核爆泰坦走向收割机、400 u 内自弹出，1.3 s 后 1.5 s 内 3 次爆炸；电弧泰坦每 0.3 s 放电；迫击泰坦在出生点 1024 u 内找射击点、远程轰收割机；隐身无人机给 400 u 内的友军隐身；FD tick 速度 2.0 – 2.5 倍。
5. **经济**：每人上限 5000；商店：增幅武器 100、增幅电池 400、核爆骑乘 500、电弧陷阱 650、哨戒炮 1200、收割机护盾 1200。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 收割机血量 | — | 25000 | — | — | [TF2 数据] FD §1.2、§5 |
| 收割机回复：延迟 / 回满 | — | 10 s / 10 s | — | — | [TF2 数据] |
| 核爆泰坦自弹出距离 | 10.16 m | 400 u | 5.556 H | — | [TF2 数据] AS §2.14 |
| 迫击泰坦射击点范围 | 26.0 m | 1024 u | 14.22 H | — | [TF2 数据] AS §2.16 |
| 电弧陷阱：触发 / 电击半径 | 6.35 / 12.7 m | 250 / 500 u | 3.472 / 6.944 H | 冷却 12 s | [TF2 数据] FD §4 |

#### 实现模板（没有参考实现）

```
WaveDirector:
    state: None → Incoming → InProgress → Complete → Break(buyTime 60 s) → Incoming ...
    on harvester destroyed: restart wave (retries left)
    difficulty: one table row, applied at spawn (health adjust, extra AT grunts, captains)
```

波次内容要 HSD 自己设计（[设计]），参考 Attrition 的刷兵节奏（AS §6.11，Northstar 版：每队 4 小队 × 4 人、队里 NPC < 14 时补、一次只有一种出场）。

#### 验收

无：FD 框架以外没有对照数据。建议的测试（还没有）：`WaveDirectorTests.HarvesterLossRestartsTheWave`。

#### 出处

- FD §0 – §8（§3.3 拿 tick 爆炸和 AI 危险区的数比较是错的，以 AS §2.10 为准）。main
- AS §2.9 – §2.16、§6.11。main
- `TF2-Research/REF-TESTS-1112.md` §3（FD 到此为止）。本地，不在 git

---

## 10.17 AI 的实现模板和现状（Unity）

#### 原理

AI 的规则多，但能按依赖分层做：先能"看见"，再能"打中 / 打偏"，再能"选做什么"。前两层是手感的关键（它们决定 HSD 的高速移动在战斗里值不值），也最容易对着 TF2 实测验收；行为树可以先用最小的士兵清单。

#### 规则和公式

现状：**Unity 里没有 AI**。HSD-Unity PR #60（`combat/wp3-weapons`，还没合并）的 `EnemyGun` 是两个站桩假人枪手：可选开关 `enemyFire`（默认关），每步检查玩家可见、距离在射程内、射线通畅，按 R-201 的连发、射速、伤害、休息开火，散布 1.25°（猜的）× spreadscale。**没有感知、没有快速铁驭打偏、没有收拢、没有行为树**。

建议的做法顺序（[设计]）：

| 步 | 做什么 | 依赖 | 验收 |
|---|---|---|---|
| 1 | `AiSettings` 数据（士兵 MP 一行，键名沿用 TF2，标 `[u]`） | — | 导入表和 `aisettings-resolved.tsv` 一致 |
| 2 | 感知（§10.11） | 1 | 发现时间表 |
| 3 | 打偏 + 散布 + 收拢（§10.12、§10.13），替换 `EnemyGun` 的瞄准 | 1 | L-1 命中率表 |
| 4 | 最小行为树：RangeAttack、ChaseEnemy、CombatFace；计划表数据 | 2 | 第一枪时间 |
| 5 | 掩体、闪避、小队 | 4 | 只记录 |
| 6 | 其他种类、出场、波次 | 4 | 时间线 |

#### 实现模板（没有参考实现）

快速铁驭的判定要读 HSD 电机的状态：`R5MotorV2.grounded`、跑墙 / 挂墙状态（`WallRun/`、`Climb/` 的悬挂）、速度 `vel`（[u]）。门槛 180 u/s 在 u 模式下直接用；米模式下 = 4.572 m/s（[01 §5](01-units-body.md)）。

#### 验收

见各节。总规则在 [11](11-acceptance.md)（AI 的对照是"规则一致 + 命中率落在实测置信区间"，不是逐帧叠图）。

#### 出处

- HSD-Unity PR #60 `Assets/HSD/Game/Runtime/Combat/Arsenal/CombatSim.Arsenal.cs`（`EnemyGun`、`StepEnemyGuns`）、`ArsenalConfig.cs`（`EnemySpread` 1.25）。还没合并
- 00-INVENTORY 第 10 章"Unity 参考实现"。

---

## 缺口

都写进了 [`_notes/hb-ch10.md`](_notes/hb-ch10.md) 的"待研究"。

1. **三套冷却模型并存**（移动槽、铁驭战斗层 `Charges`、泰坦 `KitAmmoCooldown`），换装备就满充能；要不要统一没定。
2. **P9 证据弱**（B10-1）：预告时长全是脚本值，夺控只测了黑洞一个。
3. **铁驭战斗层没有统一的打断层**：沉默写了没人读；死亡、EMP、取消各写各的。
4. 状态效果的淡出含义是 [推断]；同类取最大只测了减速和加速；减速在空中 / 滑铲时没测。
5. **敌人 AI 在 Unity 里为 0**；没有一条 AI 测试。
6. AI 补测 AI1 – AI6 没有结果（两次运行都是 `no_game`）：中远距快速状态命中、高难度、断视线后收拢重来、被看见后隐身、遗忘时间、背后发现机制（B10-3）。
7. 发现时间的斜率（实测 0.00072 s/u 对设置 0.00049 s/u）没解释；`NoticeForgetPreTime` 实测的士兵用的是 1.0 还是 0.3 没核。
8. 66 个选择器只读了 N-4 – N-7 几个；122 种任务、55 种条件、听觉、进攻 / 规避切换的公式都没读。
9. FD 每一波的内容和服务器逻辑本地没有，做不了。
10. 技能镜头、技能音效同步没研究（99-TODO-RESEARCH 已列）。
