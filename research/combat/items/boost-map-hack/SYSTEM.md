# 增益包：地图透视 系统记录

会话 `i1-records`，2026-11-01。静态记录。**本地只有壳**，公共证据见 [I-STUB-ITEMS](../_shared/I-STUB-ITEMS.md)。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。

## 0. 概要

- **道具**：增益包 / `mp_ability_boost_kit_map_hack`（`survival_loot.csv:414`，被注释，被动 `PAS_MAP_HACK`，全局搜无引用）。
- **一句话**：意图是全图显示敌人（名字推断）。本地没有触发者。只有客户端"被透视"的显示。
- **分类**：可视化（参考）。
- **可拆出的部件**：`maphack_detected` 的显示端 → 3.3。

## 1. 它用什么实现各种效果

| 效果 | 本地有什么 | 证据 |
|---|---|---|
| 物品壳 | 模板 `.txt` | `scripts/weapons/mp_ability_boost_kit_map_hack.txt` |
| 被透视状态 | 状态效果 `maphack_detected` | `client/cl_minimap.gnut:1331`、`weapons/cl_smart_ammo.gnut:372`、`:396`；**只有读取，全局没有 `StatusEffect_Add`** |
| 小地图 | `RuiTrackFloat( rui, "maphackDetectedFrac", ent, 严重度 )` | `client/cl_minimap.gnut:1331` |
| 警告文字 | `#MAPHACK_WARNING` | `weapons/cl_smart_ammo.gnut:397` |
| 图标 | `rui/menu/boosts/boost_icon_map_hack` | `pilot/cl_pilot_tracking_vision.gnut:1176`（被别的 POI 借用） |

## 2. 流程

**写不出。不编。** 已知：如果某处给敌人挂 `maphack_detected`，小地图和警告文字会亮。

## 3. 代码

### 3.3 显示端

小地图每个单位的 RUI 跟踪这个严重度（`cl_minimap.gnut:1331`）。被透视者屏幕上显示警告（`cl_smart_ammo.gnut:372-397`）。真正的画法在 RUI 资源，脚本里没有。

## 4. 参数

没有。范围、时长全无。

## 5. 未解决和要实测的

实测帮不上。手动挂状态效果可以看小地图样子（脚本 `StatusEffect_AddTimed( npc, eStatusEffect.maphack_detected, 1, 10, 0 )`）。低优先级，HSD 不用 RUI。

## 6. HSD 实现

**不需要从这里实现**。APEX-REPORT 2.6 已给完整方案：勘测信标"敌人扫描"（全图敌人的扫描当时位置画到大地图和小地图，30 s，后 15 s 淡出）。视觉部件见 [E-SONAR-HIGHLIGHT](../../_shared/E-SONAR-HIGHLIGHT.md)。

filter 写的"APEX-REPORT 2.6 相关"成立。
