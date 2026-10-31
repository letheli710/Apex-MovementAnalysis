# 公共部件 C：伤害修正（标记增伤、同目标递减、穿盾加成、溢出）

批次 C（combat-c），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/vscripts/`。

用到它的（本批）：Vantage 标记（`../vantage-snipers-mark/SYSTEM.md`，`weapons/mp_ability_sniper_ult.nut`，下文 `su`）、Valkyrie 递减（`../valkyrie-missile-swarm/SYSTEM.md`，`weapons/mp_ability_valk_cluster_missile.nut`，下文 `vk`）、Rampart 穿盾 ×1.2（`../rampart-amped-cover/SYSTEM.md`，`sh_codecallbacks.gnut`，下文 `cb`）、Gibraltar 枪盾溢出（`../gibraltar-gun-shield/SYSTEM.md`，`weapons/mp_ability_gibraltar_shield.nut`，下文 `gs`）、Ballistic 过热爆炸不致死（`weapons/mp_ability_debuff_zone.nut:525`）。

## 0. 概要

- **部件**：R5 改伤害的四种挂法。
- **一句话**：①按"伤害来源"注册回调（`AddDamageCallbackSourceID`）；②按"攻击者类型"注册全局回调（`AddDamageByCallback("player", …)`）；③实体自己的 `OnDamaged / OnPostDamaged`；④引擎给穿过某物的子弹加武器 mod。
- **分类**：系统（HSD 战斗层的伤害结算要预留这几个钩子）。
- **可拆出的部件**：
  - 标记 + 来源区分倍数（标记者本人 / 队友不同倍数）→ 3.2.1
  - 同目标短时间内递减 → 3.2.2
  - 穿过某物的子弹加 mod（×1.2）→ 3.2.3
  - 护盾吸收 + 溢出传给本人（爆炸不溢出）→ 3.2.4
  - 不致死伤害 `min(hp − 1, X)` → 3.2.5

## 1. 实现手段

| 修正 | 挂法 | 来源 |
|---|---|---|
| Vantage 标记 | ② 全局"玩家造成的伤害"回调；看目标状态效果 `sonar_round_embedded` 和 `p.sonarRoundsAttacker` 的队伍 | `su:101`、`su:457-543` |
| Valk 递减 | ① damageSourceId 回调；表 `[攻击者][目标] = 上次命中时间` | `vk:148`、`vk:162-195` |
| 穿盾加成 | ④ 引擎穿透回调返回 mod 名 `amped_damage`，武器 `.txt` 里定义 ×1.2 | `cb:845-893` |
| 枪盾溢出 | ③ 盾实体 `OnPostDamaged`，多出部分用 `DF_OVERFLOW` 再打给本人 | `gs:367-483` |
| 过热不致死 | 直接 `TakeDamage(min(hp − 1, 30))` | `weapons/mp_ability_debuff_zone.nut:525` |

## 2. 流程（一发子弹的伤害结算顺序，推断）

```
引擎算武器基础伤害（距离衰减、爆头倍数、穿盾加的 mod 已在武器上）
→ ① damageSourceId 回调（Valk 递减）
→ ② 攻击者类型回调（Vantage 标记）
→ ③ 目标实体回调（护盾 / 墙 / 炮台的特殊规则）
→ 扣血
```

顺序是推断（脚本看不到引擎调用顺序），第 5 节。

## 3. 代码

### 3.2.1 标记倍数（`su:487-507`）

```
if 目标有 sonar_round_embedded 且 攻击者队伍 == 标记者队伍:
    来源是标记武器 → ×2.5（旧 2）
    其他 → ×1.15
```

"先判断是否已标记、再给标记"——第一发不吃加成（`su:487` 在 `su:539` 之前）。`DF_OVERFLOW` 跳过（`su:459`），防止溢出伤害被重复加成。

### 3.2.2 同目标递减（`vk:162-195`）

```
last = T[attacker][target]（默认 0）；T[attacker][target] = now
if now < last + 5 且 target 是玩家 / NPC: dmg = floor(dmg × 0.2)
```

每次命中都刷新时间，所以持续命中时只有第一下满伤。

### 3.2.3 穿盾加 mod（`cb:858-889`）

```
hitEnt 有 pass_through_amps_weapon:
   子弹已有 amped_damage → 这面盾受满血伤害（打碎），防止叠加
   能量 AR → "amped_damage_alt"；否则 "amped_damage"
```

### 3.2.4 护盾溢出（`gs:387-398`、`gs:476-479`）

```
if dmg > 剩余护盾: carry = dmg − 剩余；dmg = 剩余；爆炸 → carry = 0
护盾破 → owner.TakeDamage(carry, DF_OVERFLOW)
```

### 3.2.5 不致死

`TakeDamage(min(target.hp − 1, 30))`：留 1 血。

## 4. 参数

| 参数 | 值 | 来源 |
|---|---|---|
| 标记本人 / 队友 | ×2.5（旧 ×2）/ ×1.15 | `su:43-47` |
| 标记时长 | 10 s | `su:42` |
| 递减倍数 / 窗口 | ×0.2 / 5 s | `vk:45-46` |
| 穿盾 | ×1.2 | 武器 `.txt` `amped_damage` |
| 过热伤害 | 30（留 1 血） | `mp_ability_debuff_zone.nut:44` |

## 5. 未解决和要实测的

- 回调顺序（第 2 节）和"倍数乘在爆头之后"。**测**：Vantage 标记训练假人后爆头一枪，看数字是否 = 50 × 1.5 × 2.5 = 187。

## 6. HSD 实现

**未实现**。现有：`CombatSim` 的伤害结算是直接扣（README）。`AWall.PassAmp` 已经实现了"穿墙 ×1.2"的一种（`Tacticals.cs:135`）。

建议：在 `CombatSim` 伤害结算加一个修正链 `List<IDamageModifier>`（按"来源 → 攻击者 → 目标"三段），每个修正拿到 `DamageEvent{attacker, target, source, amount, flags}` 可改 `amount` 或追加事件（溢出）。上面五种各写一个实现。`DF_OVERFLOW` 一类的标志也要有，避免溢出伤害再被放大。
