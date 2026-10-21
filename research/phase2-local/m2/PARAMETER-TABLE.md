# M2 parameter table — R5Flowstate base movement (measured)

Units: Source units (u; 1 u = 0.0254 m), seconds. `msc` = per-command move scale (`m_cachedMoveScale`), 1.15 empty-handed in every M2 trial.

**Source column**

- **census**: the session's live client class var, read by the E0 census at the start of every session.
- **fitted**: estimated from the trials.
- **census ✓**: a census value the data confirm to within the stated spread.
- **assumed**: taken from Source convention, not identified in the data.

Every number comes from real client MOVE-TRACE usercmds (first-time predictions). The dedi matched the client bit for bit in every check.

Detailed models, residuals and scripts:

- [ground/GROUND-MODEL.md](ground/GROUND-MODEL.md)
- [air_jump/AIR-JUMP-MODEL.md](air_jump/AIR-JUMP-MODEL.md)
- [slide/SLIDE-MODEL.md](slide/SLIDE-MODEL.md)

**Legend caveat (found in M2).** The firing range assigns a random legend per session: session `M2_main` used Pathfinder (`pilot_survival_grapple`), and `M2_rerun` used Wraith (`pilot_survival_closer`).

- Their censuses differ only in `sprintAcceleration` (100 vs 102), `dodgeSpeed` and `dodgeDuration`.
- The measured sprint acceleration followed each session's census exactly: 115.01 = 100 × 1.15 and 117.30 = 102 × 1.15.
- So the model must read class vars per session. The runner now pins the legend (`--legend`, default Gibraltar).
- The air/jump `params.json` says "Gibraltar" in its scope line. That is wrong for the M2 sessions; this table is authoritative.

## Ground (E1: 35 trials, 7 conditions × 5)

| Parameter | Value | Unit | Source | Spread (5 trials) | Rule |
|---|---|---|---|---|---|
| speed | 173.5 | u/s | census ✓ | terminal 0 % | walk cap = speed·msc = 199.525 |
| sprintspeed | 260 | u/s | census ✓ | 0 % | sprint cap = 299.0 |
| crouch speed | 80 | u/s | fitted (no census key read) | 0 % | crouch cap = 92.0 |
| lowSpeed | 120 | u/s | census ✓ (bracketed) | — | below lowSpeed·msc (138) the low band applies |
| lowAcceleration | 2500 | u/s² | census ✓ | 0.096 % | a = 2500·msc = 2875 below 138 u/s |
| acceleration | 450 | u/s² | census ✓ | 0.104 % | a = 450·msc = 517.5 above 138 u/s |
| sprintAcceleration | 100 (Pathfinder/Gibraltar), 102 (Wraith) | u/s² | census ✓ per session | 0.022 % | a = sprintAcceleration·msc above walk speed while sprinting |
| deceleration | 1250 | u/s² | census ✓ | 0.077 % | no input: s −= 1250·dt (**not** × msc); Source friction rejected (3.1 vs 0.005 u/s per-cmd error) |
| crouch deceleration | 1500 | u/s² | fitted | 0.062 % | ducked, no input or above crouch cap |
| stop snap | 1 | u/s | assumed (data bracket 0.58–1.58) | — | s < 1 → 0 |
| speedScaleSide / speedScaleBack | 1 / 1 | – | census ✓ | 0 % | side and back move at walk speed |
| direction | — | — | fitted | heading = wishdir within 0.0006° | v = s·normalize(wishdir); redirect is instant; diagonal is normalized |
| sprint onset | ≈ 0.14–0.17 | s | fitted (2 deciding commands; weak) | — | sprint band starts after the press; `sprintStart*` keys showed no effect |
| turn key rate | 140.70 | °/s | fitted | 0.034 % | `+right` console turn (input device, not physics) |

## Air and jump (E2 + E4: 42 trials, 118 jumps)

| Parameter | Value | Unit | Source | Spread | Rule |
|---|---|---|---|---|---|
| gravity | 750 | u/s² | census `sv_gravity` × `gravityScale` 1 ✓ | fit 749.91, sd 0.71 (n = 10 054 cmds) | half-step: vz −= g·dt/2; z += vz·dt; vz −= g·dt/2 |
| jumpHeight | 56 | u | census ✓ | V = 289.823, sd 0.005 (n = 42) | V = √(2·g·jumpHeight·frac). The jump command already removes 1.5·g·dt, so post vz = 282.0 at 144 fps |
| apex (consequence) | 54.95 | u | observed | sd 0.03 | about V·dt/2 below 56, so it depends on frame rate |
| air time (consequence) | 0.7631 | s | observed | sd 0.0009 | 109 usercmds at 144 fps |
| airAcceleration | 500 | u/s² | census ✓ | 499.95, sd 0.26 (n = 391) | accelspeed = 500·dt (no × wishspeed) |
| airSpeed | 60 | u/s | census ✓ | residual rms 0.004 u/s | wish cap = airSpeed·msc = 69 |
| airFriction / airDrag | 0 / 0 | – | census ✓ | 0.0000 u/s per cmd | no horizontal loss in the air |
| antiMultiJumpHeightFrac | 0.3 | – | census ✓ | 0.29998 | frac = clamp(0.3 + 0.7·(t − 0.15)/0.60, 0.3, 1), t = time since landing |
| multi-jump hold / ramp | 0.15 / 0.60 | s | fitted (no census key) | rms 0.00002 (n = 62) | full height again 0.75 s after landing |
| jump-command friction | skipped | – | observed | 0.003 u/s | bunny hops keep their speed |
| ground probe | 2 | u | assumed (Source) | 112/113 landings match | land when falling and the floor is within 2 u |
| skip_speed_reduce, landSlowdownDuration | — | — | not observed | — | need hops above 299 u/s and hard landings (M3) |
| lurch (first strafe press in the air) | ×0.8477 speed, −44.2° | – | observed, one condition | identical 5/5, dedi identical | not modelled. Belongs to M3 (tap strafe) |

## Slide (E5: 15 trials)

| Parameter | Value | Unit | Source | Spread | Rule |
|---|---|---|---|---|---|
| slideSpeedBoost | 150 | u/s | census (only bounded: ≥ 161 observed) | 0 | at the duck press: v = min(v + 150·msc, cap) |
| slideSpeedBoostCap | 400 | u/s | census ✓ | peak 460.000, 0 | cap = 400·msc |
| slideDecel | 100 | u/s² | census ✓ | 99.61 (1.06 %) | v' = (v − 100·dt)·0.7^dt (not × msc) |
| slideVelocityDecay | 0.7 | per s | census ✓ | 0.7001 (0.30 %) | same rule; residual 0.0008 u/s rms per cmd |
| slideStopSpeed | 125 | u/s | census ✓ | — | slide ends after the first cmd whose post speed is < 125. Lasts 1.693 s from 460 |
| crouch overspeed decel | 1500 | u/s² | fitted | 0.04 % | after the slide, while ducked: v −= 1500·dt down to 92 |
| refund window | 0.2 < w < 0.6 (0.4 per Phase 1 source note) | s | bracketed | — | a slide jump inside the window subtracts the stored gain (−160.99 observed) |
| slideMaxJumpSpeed | 350 | u/s | census ✓ | 350.005 | outside the window v_h = max(v_h, 350) (v > 350 not tested) |
| slideJumpHeight | 50 | u | census ✓ | H 50.37 early / 49.90 late | slide-jump V = √(2·750·50) |
| landing while ducked | — | – | observed | — | slide resumes with no loss and no new boost |
| not exercised | slideRequiredStartSpeed 200, slideAccel 50, slideWantToStopDecel 400, slideMaxStopSpeed 350 | | census | — | keep the census values |

## Acceptance (plan M2: R5 data)

| Limit | Result |
|---|---|
| Ground terminal speed variation, same condition, ≤ 2 % | **pass**: 0 % in all 7 E1 conditions |
| Accel/decel parameter variation ≤ 5 % | **pass**: worst 0.104 % ground, 1.06 % slide decel |
| ≥ 5 valid trials per condition | **pass**: 17 conditions, 5–8 each |

The Unity side of the acceptance is in [M2-REPORT.md](M2-REPORT.md).
