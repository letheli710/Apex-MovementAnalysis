# 公共部件 B：指派目标（打分版，Conduit Radiant Transfer）

批次 B，会话 `combat-b`，2026-10-31。只读脚本。

**和 `_shared/D-TARGET-ASSIGN.md` 的关系**：D 批写的是 Lifeline D.O.C. 的版本（选"夹角最小"），并注明 Conduit "本批没读"。本文补上 Conduit 的版本（**加权打分**），并给两者的对照和 HSD 的统一写法。两份一起看。

来源：`research-src/s21-platform/scripts/vscripts/weapons/mp_ability_conduit_arc_flash.nut`（下称 AF）；`vscripts/_utility_shared.nut:1354`。

## 0. 概要

- **部件**：常驻打分线程 + 最佳目标 netvar + 每个候选一个 HUD。
- **一句话**：每帧给每个队友打分（缺盾 0–25 + 贴准星 0–35 + 距离 0），分数 > 0 的最高者是"最佳目标"；开火时对它施放。
- **分类**：系统。
- **能复用到**：PvE 里给友方单位（分身、炮台、伙伴）上增益；反过来选敌人（权重换成"血少 + 近 + 贴准星"）做锁定类技能。

## 1. 实现手段

| 部分 | 手段 | 来源 |
|---|---|---|
| 候选 | `GetArrayOfPossibleAlliesForPlayer`：同队活着的**玩家**（或同盟），去掉自己；**不含 NPC** | `_utility_shared.nut:1354` |
| 扫描 | 服务端线程，**每帧**（D.O.C. 是每 0.1 s）；拿到武器就开 | AF:430-470、AF:256 |
| 合法性 | `IsValidTacTarget` 返回枚举（失败原因：通用 / 超距 / 不在锥内），HUD 用原因决定显示 | AF:477-519 |
| 打分 | `ScoreTarget`：`GraphCapped` 三项相加 | AF:521-585 |
| 同步 | `player.SetPlayerNetEnt(CONDUIT_ARC_FLASH_BEST_TARGET_NETVAR, best)` | AF:461 |
| HUD | 客户端每个候选一个 RUI：可见 / 最佳 / 被敌人挡住（6 u hull trace）/ 护盾档位 | AF:1301-1452 |

## 2. 流程

```
常驻（每帧）:
   best = argmax_{a ∈ allies, score(a) > 0} score(a)
   写 netvar
施放:
   拿出武器 → 先给自己（Conduit 特有，见 conduit-radiant-transfer 3.2.2）
   开火 → 对 netvar 里的 best 施放；4 s 都没有 best → 自动收起
```

## 3. 代码

### 3.1 合法性 `IsValidTacTarget(user, target, ignoreFaceWhenClose)`

```
非友军 / 倒地 / 相位 / 暗影形态 / 重生中 → FAILED_GENERIC
ignoreFaceWhenClose 且 d < 5 m → SUCCESS（近距不看朝向）
d > 50 m → FAILED_OUT_OF_RANGE
dot(相机→目标胸, 视线) < cos 50° → FAILED_NOT_FACING_ALLY
SUCCESS
```

### 3.2 打分 `ScoreTarget`

```
if !合法: 0
score  = Graph(护盾比例, 0→1, 25→0)
       + Graph(d², 5m²→50m², 0→0)          // 距离权重 0
       + Graph(dot, cos50°→cos5°, 0→35)
```

### 3.3 和 D.O.C. 的对照

| 项 | Conduit（本文） | Lifeline D.O.C.（D-TARGET-ASSIGN） |
|---|---|---|
| 选法 | 加权打分，取最高 | 取夹角最小 |
| 频率 | 每帧 | 每 0.1 s |
| 锥角 / 距离 | 50° / 50 m（近 5 m 不看朝向） | 50° / R（见 D 文档） |
| 需求项 | 缺盾越多越优先 | 无（D 文档 HUD 有"需要"标记） |
| 视线 | 不查（只在 HUD 提示被敌人挡） | 见 D 文档 |
| 没有目标 | 拿出时就先给自己，4 s 后收起 | 按键时派给自己 |
| 可信度 | 脚本看起来是原版结构（未见 SDK 痕迹） | D 文档：SDK 重写嫌疑 |

## 4. 参数

| 参数 | 值 | 来源 |
|---|---|---|
| 锥角 | 50°（满分 5°） | AF:26、AF:556 |
| 距离 | 5 m 近距 / 50 m 最远（升级 ×1.2） | AF:29-31、AF:185 |
| 权重 | 护盾 25 / 距离 0 / 角度 35 | AF:523-525 |
| 没目标收起 | 4 s | AF:360 |

## 5. 未解决和要实测的

- 不查视线：队友在墙后能否被选中并施放（见 conduit-radiant-transfer 第 5 节）。
- 每帧重选会不会"跳目标"：两个队友都在锥内时晃准星，看 HUD 最佳标记的切换。

## 6. HSD 实现

**未实现。** 建议和 D 批合成一个部件 `Combat/Targeting.cs`：

```csharp
// 每帧 / 每 0.1 s 调用
CombatUnit Pick(Vec3d eye, Vec3d view, IEnumerable<CombatUnit> candidates,
                Func<CombatUnit, bool> valid, Weights w, double coneDeg, double maxDist, double nearDist)
score(u) = w.need  · Need(u)                                // Conduit：1 − 护盾比例；敌人版：1 − 血量比例
         + w.angle · Remap(dot, cos(cone), cos(5°), 0, 1)
         + w.dist  · Remap(d², near², max², 1, 0)
best = argmax score, score > 0
```

- D.O.C. 版本 = `w.angle` 只用夹角、其他 0；Conduit 版本 = need 25 / angle 35 / dist 0。
- HUD：`CombatHud.UnitRect`（`CombatHud.cs:168`）画框，最佳目标高亮。
- 开关：每个技能自己的权重配置。
