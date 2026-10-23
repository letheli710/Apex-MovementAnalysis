# M10 track R ③: Octane stim re-use, jump pad direction / arcs / upgrades, ceiling surf

Status: 2 sessions on the R5Flowstate **local hybrid build (S21 client + S3 dedicated server + SDK)**, offline, 120 fps, Octane
with kit. Pads are created with `JumpPad_CreateAtLocation` (EVAL shortcut, as M4/M8). Nothing is committed. Labels **[meas]
[src] [inf] [hyb]** (S21-client vs S3-dedi difference; the dedi is authoritative locally). Spec = track D §6 O-1..O-8.

## TL;DR

| Item | Answer | Evidence | Spec |
|---|---|---|---|
| Stim regression | Onset 0.158 s after the press, msc 1.4927 (×1.298) for 6.0 s, back to 1.15 at 6.49 s; health −20 per stim (`STIM_HEALTH_COST 20`), passive regen afterwards; stim sprint cap 420.95. | [meas 33] | O-1 agree |
| Stim re-use | A second press at +1.0 / 2.0 / 3.0 / 5.9 s: **no new stim, no refresh, no health cost** (blocked while `stim_visual_effect` is on, [src]). At +6.1 / 6.6 s still nothing (charge cooldown 0.7 s after the 6 s charge, [src] `charge_cooldown_time`). At **+7.5 s and +9.0 s a new stim fires** (−20 health, new 6.5 s boost). | [meas 18 + 4] | O-2 agree (6 s block; the wiki's 1.8 s is contradicted) |
| Stim + slide / hops | Slide start 594.7 vs 457.8 without stim (×1.299), +1 s 347 vs 236; bhop jumps at 410.6 vs 299. msc scales everything that scales in M2. | [meas 2–9] | — |
| Pad launch | Stand 1147.76 at 63.38° (= normalize(ĥ + 2·up)), crouch 1148.23 at 44.91° (V = 1), apex 707.2 / 439.7–442.4 (as M4). Approach speed irrelevant (walk / sprint / drift same launch). | [meas 21] | O-4 agree (707.9 / 442.8) |
| Pad direction | ĥ = the **direction of motion at contact**: view yaw 90° with D held (moving +X) → launch +X; view 180° with S (moving +X) → +X; a 12-frame W tap and no key at contact (drifting at 170 u/s) → **63.4° along the drift, not straight up**. | [meas 9] | O-3: (d) velocity, not view/wish; "no key → straight up" contradicted |
| Pad ×1.2 | With `PAS_ULT_UPGRADE_ONE` given before the pad is created: launch **1377.8** (stand) / 1378.2 (crouch), apex 1018 / 624. Local script `JumpPad_GetPushVelocity` [src]; S21 status of that upgrade per track D. | [meas 6] | identified locally |
| Upgraded pad DJ (Airborne Agility) | `PAS_ULT_UPGRADE_THREE` (upgraded pad → `enable_doublejump_aircontrol`): the double jump with D held is **identical** to the non-upgraded one (Δv (−264, −272, +197), v 0.5 s later the same). No measurable effect in this test. The local script also refills a Sparrow double jump (post-S21 content). | [meas 9] | O: not reproduced |
| **Ceiling surf** | **[hyb]** The S21 client predicts the surf exactly as the wiki/track D describe: on contact z stays pinned while vz stays > 0 (e.g. 886 → 861 over 6 commands, −600 u/s² = g·0.8 slow-mo) and v_h is kept. **The S3 dedi clips vz to ~0 on the contact command** (−31..+24 depending on the ceiling slope) and keeps v_h (514 → 520 on the 2° up-slope), so the client is corrected after 6–16 commands. Same on a smooth single-rock ceiling and on a rough three-rock ceiling, at 100–600 u, standing and crouched. Locally there is no surf; the S21 movement code (client) has it. | [meas 68 trials, client vs dedi per usercmd] | O-6: agree for the S21 client, contradicted by the local authority |
| Normal jump into a ceiling (control) | Standing jump under a 100 u ceiling: vz clipped (−2.9) on both sides; sprint jump: the client pins 3 commands with vz 180, the dedi clips (−10). So the client-side surf is not pad-specific. | [meas 9] | — |

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_210453_M10R_octane` | stim (once, re-press at 1.0–6.6 s, sprint, slide, hops + controls), pads (walk / crouch / sprint / drift / side / back, ×1.2, upgraded DJ), rough ceiling grid 100–600 u (3 rocks pitched +90°), controls | r16506 `stim_slide` (fps 112.3), r16577 `ceil_h100_cr` (fps 116.3) |
| `20261022_213225_M10R_octane2` | smooth ceiling (1 rock pitched −90°, yaw 180, its climbable face down; underside rises ~1.9° along +X) 150 / 250 / 400 u, drift / steer / no-W, jump control; stim re-press 7.5 / 9.0 s | r16913–16915 `ceil2_h400_st` (fps 116 / 93 / 114), r16925 `ceil2_h250_noW` (fps 110), r16933 `restim_t75` (+5 frames). **Contaminated (kept in the output, not used for re-use timing):** r16932, r16934–16936 started inside the previous trial's second stim (their first press is blocked). |

Ceiling heights are traced by the dedi logger 0.3 s after the spawn (`[M10-OCT] ceiling`). In the smooth set, `ceil2_h150_st`
and `ceil2_h400_cr`, `ceil2_h250_drift` hit the ceiling lip / did not reach it in a pinned state; the pinned rule (post z within
0.5 u of the pre z while vz > 100) filters free-flight apexes.

## Model for HSD

- Stim: unchanged (M4) plus the re-press rule: blocked for 6.0 s, then a 0.7 s cooldown.
- Pad: launch direction = horizontal velocity direction at contact (any speed, also without keys), stand 63.4° / crouch 45°,
  1148 u/s, ×1.2 with the upgrade.
- Ceiling surf: a design decision for the user. Local authority (S3 dedi) = no surf (vz clipped). S21 client prediction =
  surf (keep vz while pinned, decay at g·0.8 during the pad flight, keep v_h). Track D's sources describe the client behaviour.

## Open questions

1. Whether the S21 server also surfs (expected, since the client prediction is S21 code) — not testable on this build.
2. The upgraded-pad air-control mod: a test with continuous strafing after the double jump.
3. Pad wallrun (O-8) and TS off the pad (O-5): not run.

## Rerun

```
cd research/phase2-local/m10/r_octane
py -3 octane_analysis.py ../../data/20261022_210453_M10R_octane ../../data/20261022_213225_M10R_octane2 \
  --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --label M10R_octane --trials 3 --run-base 16501 --batch-base 16501 -- --fps 120 --legend octane --kit
--no-census --state-log --m10-log --schedule <40 m10_o_* names>`; `--label M10R_octane2 --run-base 16901 ... --schedule <12 names>`.
