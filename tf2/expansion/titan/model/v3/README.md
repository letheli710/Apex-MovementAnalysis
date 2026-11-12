# 泰坦模型 v3：五台成品

2026-11-12。按用户的《HSD 泰坦建模规范》做的五台正式泰坦，规范校对版见 [SPEC.md](SPEC.md)（v1.6）。

## 大白话

五台都做完了：剪影 → 中模 → 细节 → 材质 → 挂点 → 导出 FBX，然后 lead 审阅过一轮（R5），各自改过一次。三副骨架（轻、中、重），五套装甲：

| 代号 | 名字 | 骨架 | 文件夹 | 现行版本 | 说明 |
|---|---|---|---|---|---|
| L-1 | 北辰 | 轻型 | [L/](L/) | r5b（`L/L1/r5b/`） | 窄身长腿，肩后一对翼面，长枪 |
| L-2 | 浪人 | 轻型 | [L/](L/) | r5b（`L/L2/r5b/`） | 左肩叠片肩甲，背后大剑 |
| M-1 | 棱镜 | 中型（v2） | [M1/](M1/) | r6（`M1/r6_final/`） | 楔形躯干、实体肩甲、火箭巢 |
| H-1 | 熔炉 | 重型 | [H/](H/) | r6b（`H/H1/r6b_final/`，关节补缝 + 后裙让开大腿） | 圆桶躯干、半球肩甲、背后燃料罐 |
| H-2 | 军团 | 重型 | [H/](H/) | r6b（`H/H2/r6b_final/`，方案 D + 后裙让开大腿） | 方盒躯干、加粗的转轮炮右臂、外移的左肩盾 |

每条线文件夹里的 `Titan_<代号>.blend / .fbx` 就是现行版本。

五台并排的对比和"缩到 1/4 能不能分清"的判断在 [lineup/](lineup/)：现行是 `lineup/r7/`（静止姿势，H-2 方案 D）：10 对都能分清，H-1 / H-2 从最弱变成和别的对一样好分，现在最弱的是 L-1 / L-2。`r6/` 是五台 `stand_aim` 的试验和 H-2 小样，`r5/`、根目录是更早的版本。关节贴合的跨线检查在 [checks/](checks/)。

还没做的：没有导入 Unity；Blender 里重新导入 FBX 是对的，Unity 怎么读没验证。

## 版本

| 版本 | 内容 | PR |
|---|---|---|
| V1 | 五台第一版成品（L r4、M-1 r4、H r4）+ 第一版并排 | Apex-MovementAnalysis#116 第一个提交 |
| V2 | R5 修改轮：M-1 螺栓和自查、重型骨长统一 ×0.878 和跪姿、轻型端枪 / 握把 / 关节补缝，并排重出 | 同一个 PR |
| V3 | R6：M-1 关节贴合（补 5 处缝）；五台 `stand_aim` 并排和两两重叠比例；H-2 改法小样 | 同一个 PR |
| V4 | H-2 方案 D（炮加粗、肩盾外移 + 实心盾座）+ H-2 关节补缝；跨线关节检查（H-1、L-1、L-2 只报告）；并排 r7 | 同一个 PR |
| V5 | H-1 关节补缝（同 H-2 的关节件）；L 的缝定为不修 | 同一个 PR |
| V6 | 重型骨盆后裙让开大腿（两台 r6b），走路逐帧复核 0 帧相交 | 同一个 PR |

## 这个文件夹里放了什么（仓库里）

- 所有脚本（`.py`）、说明（`.md`）、每一轮的检查数字（`checks.json`）。
- 每台的成品 `.blend` 和 `.fbx`，以及各线自己存档的上一版（`M1/final/Titan_M1_r4.*`、`H/H*/r4_final/Titan_H*.*`、`L/L*/r4_final`、`r5_i1`、`r5_i2` 里的 `Titan_L*.*`）。
- **渲染图只放每一版的最后一轮**：
  - V1：`M1/final/`、`H/H1/r4_final/`、`H/H2/r4_final/`、`L/L1/r4_final/`、`L/L2/r4_final/`、`lineup/`、`L/lineup/`、`H/compare/`、`H/H*/rounds_3q.png`。
  - V2：`M1/r5_final/`、`H/H*/r5c_final/`、`H/compare/r5c_final/`、`H/H*/rounds_3q_r5c_final.png`、`L/L*/r5b/`、`lineup/r5/`。
  - V3：`M1/r6_final/`、`lineup/r6/`（含单台剪影 `masks/` 和 `h2_options/`）。
  - V4：`H/H2/r6_final/`（含 `poses/`）、`lineup/r7/`（含 `stand_aim/`）。
  - V5：`H/H1/r6_final/`（含 `poses/`）。
  - V6：`H/H1/r6b_final/`、`H/H2/r6b_final/`（含 `poses/`、`walk_replay.json`）。
- **中间轮次的图只留在本机的 `TF2-Research/expansion/titan/model/v3`**，没有进仓库（V1 时约 139 MB，R5 又加了 r5、r5b、r5_i1、r5_i2、r5b_i1 等）。各子文件夹 README 里提到的中间轮 PNG 都在那里。
- **中间轮次的 `.blend` 放进来了**（L 的 r1–r3、M-1 的剪影稿、各线存档的上一版成品）。理由：中间轮的图不进仓库，留下这些小文件，以后还能打开当时的模型看；H 线的中间轮没有单独存 `.blend`，可以用 `build_heavy.py` 重新生成。Blender 的自动备份 `.blend1` 没放。
