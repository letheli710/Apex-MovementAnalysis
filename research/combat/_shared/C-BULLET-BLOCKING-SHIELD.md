# 公共部件 C：挡子弹的护盾实体

批次 C（combat-c），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/vscripts/`。

用到它的（本批）：Gibraltar 护罩（`../gibraltar-dome-of-protection/SYSTEM.md`，`_bubble_shield.gnut`，下文 `bs`）、Gibraltar 枪盾（`../gibraltar-gun-shield/SYSTEM.md`，`pilot/sh_pilot_gun_shield.gnut` + `weapons/mp_ability_gibraltar_shield.nut`，下文 `pg` / `gs`）、Rampart 加强掩体（`../rampart-amped-cover/SYSTEM.md`，`weapons/mp_weapon_cover_wall.nut`，下文 `cw`）。对照：TF2 A 型墙（`HSD-Unity/.../Combat/Tacticals.cs` `AWall`）；批次 B 的 Newcastle 移动护盾、Wattson 拦截塔（`../newcastle-mobile-shield/`、`../wattson-interception-pylon/`）。

## 0. 概要

- **部件**：一个只和"武器"碰撞的实体，加上"有没有血、哪个方向挡、穿过时做什么"三个选项。
- **一句话**：R5 的护盾都是 `prop_script` / `prop_dynamic` + 碰撞组 `TRACE_COLLISION_GROUP_BLOCK_WEAPONS`（挡子弹和投射物、不挡人和 AI）；Gibraltar 护罩无血、双向挡；枪盾的血是玩家的资源条；Rampart 盾有血、单向放行并给子弹加 mod。
- **分类**：系统。
- **可拆出的部件**：
  - 碰撞组"挡武器不挡人" → 3.2.1
  - 血量三选一（无敌 / 自己的血 / 外部资源条）→ 3.2.2
  - 单向穿透 + 穿过加 mod → 3.2.3
  - 挡爆炸、挡视线、挡 AI 寻路、挡钩爪的开关 → 3.2.4

## 1. 实现手段（对照表）

| 属性 | 护罩 | 枪盾 | Rampart 盾 |
|---|---|---|---|
| 实体 | `prop_script`，`SOLID_VPHYSICS`（`bs:224-227`） | `prop_dynamic`，挂在 `L_FOREARM_SHIELD`（`pg:47-103`） | `prop_script`，`SOLID_VPHYSICS`，挂在底座上（`cw:950-985`） |
| 碰撞组 | `BLOCK_WEAPONS`（`bs:239`） | `BLOCK_WEAPONS`（`pg:57`） | `BLOCK_WEAPONS_AND_PHYSICS`，`CONTENTS_WINDOW`（`cw:961-962`） |
| 血量 | 无（推断不可破，只被 EMP 摧毁） | 共享能量（`gs:492`、`gs:543-548`） | 175（`cw:932-938`） |
| 方向 | 双向挡 | 正面 85° 挡（vortex 球，`gs:494-496`） | 单向：`SetPassThroughDirection(-0.55)`（`cw:998`） |
| 穿过时 | — | — | `PTF_ADDS_MODS` → 加 `amped_damage`（`cw:979`、`cb:858-889`） |
| 挡爆炸 | 是（`bs:240`） | 否（推断，`modelBlockRadiusDamage` 默认 false，`pg:36`） | 是（`cw:980`） |
| 挡视线 | 否（`bs:241`） | 否（`gs:523`） | 推断否（`CONTENTS_WINDOW`） |
| 挡 AI 寻路 | 是 `SPF_BLOCKS_AI_NAVIGATION`（`bs:237`） | — | — |
| 其他 | 不能钩（`CONTENTS_NOGRAPPLE`） | 只收伤害事件 `DAMAGE_EVENTS_ONLY` | 挡铝热剂、不能粘东西 |
| 被 EMP | 摧毁（`mp_weapon_bubble_bunker.nut:477-481`） | — | 扣血（`AddEMPDamageDevice`，`cw:991`） |

## 2. 流程

所有护盾的结构相同：**生成 → 设碰撞组 / 方向 / 血 → 挂特效（友 / 敌两份）→ 受伤回调改颜色 / 碎裂 → 到时或被毁时销毁**。

## 3. 代码

### 3.2.1 挡武器不挡人

`kv.CollisionGroup = TRACE_COLLISION_GROUP_BLOCK_WEAPONS`。注释（`bs:238`）原文意思：挡子弹和投射物，不挡玩家和 AI；不挡视线所以 AI 能看穿。

### 3.2.2 血量

- 无敌：不设伤害类型（护罩）。
- 自己的血：`SetMaxHealth/SetHealth` + `SetTakeDamageType(DAMAGE_YES)`（Rampart）。
- 外部资源条：`DAMAGE_EVENTS_ONLY`，在 `OnPostDamaged` 里扣外部资源、把实体血保持 ≥ 1（枪盾，`gs:430-431`）。

### 3.2.3 单向 + 加 mod

见 `C-DAMAGE-MODIFIERS.md` 3.2.3 和 `../rampart-amped-cover/SYSTEM.md` 3.2.2。

## 4. 参数

各技能的数值见各自 SYSTEM.md 第 4 节。公共的只有碰撞组和标志。

## 5. 未解决和要实测的

- 护罩是否真不可破（打满一个弹匣）。
- 枪盾是否挡爆炸。
- Rampart 盾 −0.55 方向阈值是三维还是水平。

## 6. HSD 实现

**已有部分**：`IWallBlocker`（`CombatCore.cs:140`）+ `CombatSim` 结算子弹（`CombatSim.cs:378`）和爆炸（`CombatSim.cs:322`）时都会问所有墙；`AWall` 实现了"单向 + 加成 + 挡爆炸 + 血"。

建议把 `IWallBlocker` 扩展成通用护盾接口：

```
interface IShield : IWallBlocker {
  ShieldShape shape;          // 平板 / 半球 / 跟随视线的圆盘
  bool oneWay; double passCos; double passAmp;   // Rampart
  IHealthSource hp;           // 无敌 / 自己 / 外部资源（枪盾）
  bool blocksExplosions, blocksAiPath;
}
```

护罩（半球、无敌、双向、挡爆炸、可选挡 AI 寻路）、枪盾（圆盘、外部资源、正面）、Rampart（平板、自己的血、单向 ×1.2）都是它的配置。
