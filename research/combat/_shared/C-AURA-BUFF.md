# 公共部件 C：光环 buff（施法者周围的友方自动获得增益）

批次 C（combat-c），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/vscripts/weapons/`。

用到它的：Ballistic Tempest（`../ballistic-tempest/SYSTEM.md`，主来源 `mp_ability_portable_auto_loader.nut`，下文 `al`）。对照：Rampart 加强掩体的"盾后近距离换弹快"（`../rampart-amped-cover/SYSTEM.md` 3.2.4，`mp_weapon_cover_wall.nut:192-292`，下文 `cw`）——同一个 `auto_loader` mod 的另一种发放方式。

## 0. 概要

- **部件**：施法者线程每帧找范围内友方，没 buff 的就给一份 buff，**时长 = 施法者自己 buff 的剩余时间**；buff 本体是每个人一个线程（武器 mod + 无限弹 + 条件加速），结束时全部撤销；击杀时所有带 buff 的人统一延时。
- **一句话**：一个"会传染给附近队友、所有人同一时刻结束"的计时 buff。
- **分类**：系统。
- **谁能用**：任何群体增益（射速、换弹、移速、护甲）；PvE：给召唤物 / 炮塔 / AI 队友上 buff，或敌方"指挥官"给周围小怪加 buff。
- **可拆出的部件**：
  - 进入即上、离开不掉的光环 → 3.2.1
  - 武器 mod 型 buff（只给"当前手里的主武器"加，换枪时补加，扔掉时去掉）→ 3.2.2
  - 条件加速（拿着有 mod 的武器才加速）→ 3.2.2
  - 全队统一延时 → 3.2.3
  - 位置 + 朝向条件型发放（Rampart 盾后）→ 3.2.4

## 1. 实现手段

| 部分 | 手段 | 来源 |
|---|---|---|
| 计时 | 状态效果 `has_auto_loader`（1.0，时长，淡出 0.5） | `al:534` |
| 光环 | 施法者服务端线程每帧遍历同队玩家，脚底距离² < R² 且没 buff → 上 buff + 光束 2 s | `al:236-265` |
| buff 本体 | 每人一个线程：每帧给手里主武器加 `auto_loader` mod（登记到 `modsToRemoveOnDrop`），`SetInfiniteAmmoForPlayer`，`speed_boost` 0.075 | `al:522-650` |
| 延时 | 击杀 / 击倒回调 → 所有带 buff 的人：停掉再加（剩余 + 5） | `al:652-698` |
| 武器 mod 内容 | 换弹时间 ×0.6（含分段 late1–5），能量武器充能 / 过热冷却 ×0.6 | 例 `weapons/mp_weapon_r97.txt:781-795` |

## 2. 流程

```
施法 → 给自己上 buff（30 s）→ 光环线程：
   每帧：for 友方 in 队伍: 距离 < R 且无 buff → buff(友方, 施法者剩余)
   施法者 buff 到 0 → 结束
击杀 / 击倒（带 buff 的人干的）→ 全队带 buff 的人 +5 s（光环也跟着延长，因为它看施法者剩余）
```

## 3. 代码

### 3.2.1 光环（`al:236-265`）

只在"进入且没 buff"时发放，**没有离开判断**。所以 buff 一旦拿到就会持续到全队统一的结束时间。施法者死亡时队友 buff 也结束（`al:530-531` `EndSignal(ballisticPlayer, "OnDeath")`）。

### 3.2.2 武器 mod 型 buff（`al:592-628`）

```
每帧：w = 手里的主武器（非副手、flags == WPT_PRIMARY、非固定炮台）
  w 没 mod → AddMod + 登记"扔掉时去掉"
  加速：w 有 mod 且未加 → AddEndless(speed_boost, 0.075)；w 没 mod 且已加 → Stop
结束：所有主武器（含 Sling）去掉 mod；停加速；关无限弹
```

这种"每帧补加"的写法让换枪、捡枪都自动生效，不需要换枪回调。

### 3.2.3 统一延时（`al:677-698`）

延时不是 `SetDuration`，而是"停掉 + 重新加"（批次 E 的 `E-STATUS-EFFECT.md` 3.2.1 记了另一种写法 `StatusEffect_SetDuration`）。

### 3.2.4 Rampart 盾后发放（`cw:206-292`）

```
每帧：有 Tempest buff → 跳过（同一个 mod，避免冲突）
  任何加强盾 100 u 内、且在盾的正面一侧（dot(盾 forward, 玩家 − 盾) ≥ 0）→ 加 auto_loader
  否则去掉
```

和 Tempest 的区别：**持续检查位置**，离开就掉。

## 4. 参数

| 参数 | 值 | 单位 | 来源 |
|---|---|---|---|
| Tempest 时长 / 延时 | 30 / +5 | s | `al:8`、`al:16` |
| Tempest 半径 | 3620（升级 ×√50） | u | `al:15`、`al:104-132` |
| 持枪加速 | 0.075 | 严重度 | `al:13` |
| 光束 | 2 | s | `al:454` |
| Rampart 盾后距离 | 100 | u | `cw:211` |
| auto_loader | ×0.6 | 换弹时间 | 武器 `.txt` |

## 5. 未解决和要实测的

- `speed_boost` 严重度 → 速度倍率（批次 E `E-STATUS-EFFECT.md` 第 5 节也列了这一条，一起测）。

## 6. HSD 实现

**未实现**。建议 `Combat/Buffs.cs`：

```
class AuraBuff { center: Func<Vec3d>; radius; endsAt; enterOnly = true; Func<CombatUnit,bool> eligible; Action<CombatUnit> apply/remove }
每步：foreach 友方单位 u: eligible(u) && dist ≤ radius && !has(u) → apply(u)，u.buffUntil = endsAt
     enterOnly = false 时离开就 remove（Rampart 型）
延时：endsAt += k；所有持有者同步
```

PvE 里先给"玩家的召唤物"用（Boosts.cs 的哨戒炮、分身）；以后有 AI 队友直接生效。
