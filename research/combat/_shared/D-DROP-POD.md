# 公共部件 D：空投舱从天而降（补给 / 刷敌人）

批次 D 共用，会话 `combat-d`，2026-10-31。只读脚本。

来源（都从 `research-src/s21-platform/scripts/vscripts/` 起）：`weapons/sh_care_package.nut`（SHCP）、`mp/sh_airdrops.gnut`（AD）、`ai/_droppod.gnut`（DP）、`sh_flightpath_utility.gnut`（FP）。详细见 [lifeline-care-package](../lifeline-care-package/SYSTEM.md)。

## 0. 概要

- **部件**：落点选择 + 落点合法性 + 动画驱动下落 + 落点预告 + 落地冲击 + 落地后的内容（物资 / NPC）。
- **一句话**：选好落点（抛物线 + 一套地形检查），在落点放一个 mover，让空投舱沿一段"从天上掉到 mover"的动画播放；动画事件触发推人和落地冲击；播完开门。
- **分类**：系统 + 可视化。
- **谁能用**：补给舱、刷敌人（Respawn 自己就有 NPC 版）、轰炸类技能的"弹头"、Newcastle 大招落地这类"从高处砸下来"的效果。

## 1. 实现手段

| 阶段 | 手段 | 来源 |
|---|---|---|
| 选点 | 虚拟抛物线（1600 u/s，重力 750，0.1 s 步长，1.6 s 内）第一个碰撞点 | SHCP:126-205；`_utility_shared.nut:2582` |
| 合法 | 天空通畅（+10000 往下扫）、坡度 ≤55°、贴地 16 u、脊 3 向、边缘 6 向、越界、禁区 | FP:928 起 |
| 预告 | 地面粒子 + 威胁指示（半径 128）+ AI 禁区 196 + 标记音；落地前不可用 | AD:1240-1275、1901-1942 |
| 下落 | 舱挂在落点 mover 上播动画（补给：`droppod_loot_drop_lifeline_fast`；NPC：`pod_testpath`） | DP:628-653、201-260 |
| 尘土 | 每 0.2 s 往下打线，地面放 `dropship_dust` | DP:776-794 |
| 推人 | 动画事件 `DroppodPushAway`：圆柱 r100 触发器，里面的人每帧 350 u/s 水平往外（NPC 版用 `point_push` 半径 192） | DP:719-773、285-308 |
| 落地 | 动画事件 `DroppodLanded` / `OnImpact`：震屏、冲击效果、压伤（补给：1000 / 72 u，玩家免疫；NPC 版 flag 可选） | DP:655-717、263-282 |
| 内容 | 补给：落地时才算物资；NPC：等 `doorOpenDelay` → 生成 ≤4 个 NPC → 开门出舱动画 | AD:1291-1320；DP:512-534 |

## 2. 流程

```
选点（客户端预览，每帧）→ 确认 → 服务端：建舱 + 预告
→ 播下落动画（PushAway 事件 → Landed 事件）→ StopBraking：预告消失
→ 内容（物资可用 / NPC 出舱）
```

## 3. 代码

见 lifeline-care-package 3.2.1–3.2.7。NPC 版入口 `Spawn_DropPodSquadCustom( spawnfuncs, customData, out npcs, team, spawnPoint, flags, doorOpenDelay )`（DP:512-534），flag 定义 DP:31-39。

## 4. 参数

| 参数 | 值 | 来源 |
|---|---|---|
| 选点抛射 | 1600 u/s，俯仰 −10..70°，1.6 s | SHCP:132-135 |
| 最近距离 | 72 u | SHCP:138 |
| 坡度 / 贴地 | 55° / 16 u | FP:930、937 |
| AI 禁区 | 196 u | `_gamemode_survival.nut:207` |
| 威胁指示 | 128 u | AD:1907 |
| 推人 | 350 u/s，r 100，上 256 下 32 | DP:724-726、771 |
| 补给落地压伤 | 1000，72 u，玩家免疫 | DP:672-717 |
| 补给落地震屏 | 16 / 150 / 1 s / 4000 | DP:665 |
| NPC 舱震屏 | 7 / 0.15 / 1.75 s / 768 | DP:273 |
| NPC 舱推力 | 半径 192、力 105 | DP:294-295 |
| NPC 舱跃迁特效高度 | 5888 u，从动画 4 s 处开始 | DP:246-251 |
| NPC 数 | ≤ 4 | DP:578 |
| 下落时长 / 高度 | **未知（动画）** | — |

## 5. 未解决和要实测的

下落曲线、事件时刻：见 lifeline-care-package 第 5 节（AgentLink 记舱体位置）。

## 6. HSD 实现

未实现。建议 `DropPod`：参数 = 落点、`AnimationCurve heightOverTime`（占位：+3000 u、2.5 s、末 0.5 s 减速）、`pushTime`、`landTime`、`onLanded` 回调（补给 / 刷敌人）。落点预告接 AI 避让（HSD AI 有了寻路后再接）。刷敌人用法：`DropPod.Spawn( 点, curve, onLanded: () => 生成 N 个敌人并给出舱动作 )`。
