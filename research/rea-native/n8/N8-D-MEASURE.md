# N8-D：实测

## 1. 相位中踩跳板（验证 N8-C："`JumpPadLaunch` 在相位中直接返回"）

日期 2026-10-24。会话 `phase2-local/data/20261024_025925_N8_phasepad/`（runner.json + report/）。

**设置**
- Wraith（`--legend wraith --kit`），lane C，朝 +x。
- 用脚本 `JumpPad_CreateAtLocation` 在前方 300 u 放一个 Octane 跳板（和 M10 的 `m10_o_pad_*` 相同）。
- 服务器每帧记录相位标志、相位类型、z、vz、`speed_boost`。
- 计划表在 `hsd_trial.py` 的 `n8_pp_*`，每种 3 次：

| 计划表 | 做什么 |
|---|---|
| `n8_pp_phase` | 按战术 → 0.5 s 后按住 W 走 3 s（相位中走上跳板） |
| `n8_pp_ctrl` | 同样的走法，不按战术（对照） |
| `n8_pp_after` | 按战术 → 等 4.8 s（相位已结束）→ 走上跳板 |

**结果**

| 计划表 | 相位时长 | 相位类型 | 经过跳板的时刻（从开始算） | 最大上升 | 最大 vz |
|---|---|---|---|---|---|
| `n8_pp_phase` × 3 | 3.9–4.0 s | 1（`BALANCE`） | 2.23–2.39 s（**在相位中**） | **0.7 u** | **0** |
| `n8_pp_ctrl` × 3 | — | — | 2.35–2.49 s | 707.8 u | 1001–1011 |
| `n8_pp_after` × 3 | 3.9 s | 1 | 6.49–6.69 s（相位结束后） | 707.8 u | 976–1011 |

**结论：一致。** 相位中走过跳板，三次都**完全没有发射**（0.7 u 是地面高度的小起伏）。不按战术的对照，和相位结束后再走上去，都正常发射到 707.8 u。所以跳板不发射的原因是相位窗口，不是 Wraith 角色、也不是跳板本身。这和原生 `JumpPadLaunch`（`0x140a38a90`）开头的相位检查一致。

**顺带确认**
- 相位类型：Into the Void 是 1，也就是脚本里的 `PHASETYPE_BALANCE`。
- 相位持续 ≈ 4 s，和 `mp_ability_phase_walk.txt` 的 `charge_time` 4 一致。
- 相位期间 `speed_boost` 严重度是 0.30，和脚本 `OnWeaponChargeBegin_ability_phase_walk` 加的 0.3 一致。
- 相位中走得更远（3 s 走到 x ≈ −13740，对照是 −13128 但含飞行段），说明加速确实生效。
