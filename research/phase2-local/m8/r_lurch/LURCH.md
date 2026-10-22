# M8 R5 (lead add-on): lurch follow-ups (R5Flowstate S21, local offline)

Status: one local session, Gibraltar, 120 fps, lane B (slide jump on lane C, ledge on the 232 u rock top), 5 trials per condition, 105 scored, nothing excluded. Nothing is committed. The per-command model is the unchanged M6-A1 / M3 lurch model (`../../m6/a1_lurch/a1_lurch_analysis.py`: v' = v + AirAccelerate, then on a new move-key edge v' = lurch(v', wish, λ(t), 209.3), λ = 0.7·clamp01((0.5 − t)/0.3), t from the latest jump). Labels: **[meas]**, **[fit]**, **[inf]**.

## TL;DR

| Item | Answer | Evidence, n |
|---|---|---|
| a) Reverse chain W → W+D → D → S+D → S (and mirror), one press edge every g | Speed is kept (×0.98–1.00) but the heading does **not** reach 180°: **156.4° at g = 0.05 s, 125.9° at 0.083 s, 104.6° at 0.1 s** (the later presses fall into the 0.2–0.5 s fade). The first W tap does nothing (v already along the view). The unchanged M3 model predicts every press (max one-step residual 0.93 u/s, inside the fade) | [meas] 6 conditions × 5, 150 presses |
| b1) A held from before the jump, then a W press | **Diagonal lurch** toward W+A: heading 11.2° → 35.0°, |D| 119.1, speed kept. The direction matches an equal-weight 45° wish (predicted 35.0°), not the press-usercmd axes (fwd 0.5, side −1 → 48.4°). One-step residual 11.6 u/s remains (unexplained, AirAccelerate on that usercmd is the likely part) | [meas] 5 |
| b2) A held, then D pressed (opposing keys) | **No lurch** (|Δv| 3.5–4.2 = AirAccelerate only; heading unchanged). The usercmd carries side −0.5, and the M3 model would predict a 209.3 lurch to the left — it does not happen | [meas] 5 |
| c) Tap strafe at 720 °/s (W edge every 2 commands, 15 taps, 0.25 s) | View turns ~176°, the heading follows to **−161.2° (±2.0)** at 0.3 s, speed ×1.0002 | [meas] 5 (75 presses, max residual 0.14) |
| c) Tap strafe at 1440 °/s | The view does a full turn; the heading chases it around and ends **≈ 30° behind the view** (heading 35–44° with view 5–15° after one turn); speed ×1.0002 | [meas] 5 (max residual 0.28) |
| c) Turn only, no taps (controls) | Heading unchanged (0.0°) at both rates | [meas] 5 + 5 |
| d) Walk off a 232 u ledge (no jump), D press 0.017 / 0.1 / 0.2 / 0.4 s after leaving | **No lurch at any time**: |Δv| 4.17 on the press usercmd = AirAccelerate (500·dt); air time 0.784 s. The lurch window is anchored to a jump; leaving the ground does not open it | [meas] 20 presses + 5 controls |
| e) Clamp at a 350 u/s slide-jump entry (D at k ≈ 2) | |D| = **209.30**, the same as from a 299 sprint jump (209.30). The clamp is fixed (0.7 × sprint cap at msc 1.15, M4), not scaled by entry speed; the larger entry only turns less (37.3° vs 44.7°) | [meas] 5 + 5 |

## Model notes for Unity

- Chains need nothing new: every edge is an independent M3 lurch (A1). A ~180° reversal by edges alone needs about 5 edges inside the first ~0.25 s; at 0.1 s spacing it stops near 105°.
- Lurch wish: use the **keys** (W+A held/pressed = 45° diagonal), not the first-command 0.5 axis ramp [meas, b1].
- A press whose resulting wish cancels (A held + D pressed) gives **no** lurch [meas, b2].
- The lurch window opens only on a jump (ground, slide, wall-bounce, M6-A1; pad double jump, M8 R1), not on walking off a ledge [meas, d].

## Open questions

1. The 11.6 u/s residual in b1 (held key + new press).
2. Whether a held key plus a *different* new key (e.g. A held, S pressed) also lurches toward the combined wish (only W was tested).
3. Tap strafe above 1440 °/s and with sprint held (sprint scales key turning ×0.67, M4b).

## Rerun

```
cd research/phase2-local/m8/r_lurch
py -3 lurch_analysis.py ../../data/20261022_053952_M8_lurch --json results.json --params params.json > analysis_output.txt
```

Session: `tools/hsd_session.py --label M8_lurch --trials 5 -- --fps 120 --legend gibraltar --no-census --state-log --geometry m3 --schedule <21 m8_lurch_* schedules>`.
