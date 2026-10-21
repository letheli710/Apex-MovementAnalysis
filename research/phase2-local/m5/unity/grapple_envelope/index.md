# R5 replay — Unity motor R5MotorV2/m3 vs R5 trials

Generated 2026-10-21 08:10 UTC by Unity 6000.6.5f1. Models: `R5MotorV2/m3` (after) and `ReferenceMotor/m1-first-guess` (before, M1 first guess, reports in `m1_first_guess/`). Errors are sim − ref in Source units (u, u/s), per step aligned by usercmd. Open-loop replay from initial_state with the recorded inputs; nothing is tuned per trial.

## 1. Per trial (R5MotorV2)

Event cells: largest step delta sim − ref over all paired events (count ref/sim). Apex / takeoff vz: largest |error| over all jumps. Terminal: ground speed over the 1 s before the last release (– when that window is not all ground).

| condition | trial | steps | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ (u/s) | takeoff | land | slide start | slide end | apex err (u) | takeoff vz err (u/s) | M1 pos RMS 3D (before) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m4_grapple_hold | [M4_m4_grapple_hold_r1701](M4_m4_grapple_hold_r1701/report.md) | 721 | 490.505 | 674.370 | 490.503 | 674.370 | 253.361 | 779.001 | – | 0 (1) | +87 (1) | – | – | -0.570 | +0.001 | – |
| m4_grapple_hold | [M4_m4_grapple_hold_r1702](M4_m4_grapple_hold_r1702/report.md) | 721 | 490.526 | 674.377 | 490.525 | 674.377 | 253.775 | 618.449 | – | 0 (2/1) | +88 (2/1) | – | – | -0.262 | +0.004 | – |
| m4_grapple_near | [M4_m4_grapple_near_r2101](M4_m4_grapple_near_r2101/report.md) | 721 | 358.795 | 463.929 | 358.649 | 463.929 | 193.964 | 638.056 | – | 0 (2/1) | +90 (2/1) | – | – | +21.054 | +0.002 | – |
| m4_grapple_near | [M4_m4_grapple_near_r2102](M4_m4_grapple_near_r2102/report.md) | 721 | 359.156 | 464.320 | 359.001 | 464.320 | 194.532 | 638.213 | – | 0 (1) | +90 (1) | – | – | +21.446 | +0.004 | – |

## 2. Per condition (R5MotorV2; RMS = mean of the trials, max = worst trial)

| condition | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ | worst event Δ (steps) | apex err | takeoff vz err | M1 pos RMS 3D | M1 vel RMS 3D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m4_grapple_hold | 2 | 490.516 | 674.377 | 490.514 | 674.377 | 253.568 | 779.001 | – | +88 (count mismatch) | -0.570 | +0.004 | – | – |
| m4_grapple_near | 2 | 358.975 | 464.320 | 358.825 | 464.320 | 194.248 | 638.213 | – | +90 (count mismatch) | +21.446 | +0.004 | – | – |

## 3. Ground mapping: terminal speed and accel/decel, Unity motor vs R5

Same estimator on both series (ReplayMetrics.Ground: GROUND-MODEL §1 — band by nearest nominal rate, rate = ΣΔs/Σdt, decel excludes the zeroing step). Unity spread = (max − min)/mean over the condition's trials (plan acceptance: terminal ≤ 2 %, accel/decel ≤ 5 %); Unity vs R5 = (sim mean − ref mean)/ref mean.

| condition | quantity | R5 per trial | Unity per trial | R5 mean | Unity mean | Unity vs R5 | R5 spread | Unity spread | acceptance (Unity spread) |
|---|---|---|---|---|---|---|---|---|---|
| m4_grapple_hold | decel_stand (u/s²) | 77.946 / 77.181 | 1250.000 / 1250.000 | 77.563 | 1250.000 | +1511.588 % | 0.99 % | 0.00 % | pass (≤ 5 %) |
| m4_grapple_near | decel_stand (u/s²) | 32.707 / 78.810 | 1250.000 / 1250.000 | 55.758 | 1250.000 | +2141.814 % | 82.68 % | 0.00 % | pass (≤ 5 %) |

## 4. Flags (R5MotorV2 vs reference columns; steps that differ)

| trial | grounded | sliding | sprinting | maxspeed (n compared) |
|---|---|---|---|---|
| M4_m4_grapple_hold_r1701 | 87 | 0 | 0 | 0 (721) |
| M4_m4_grapple_hold_r1702 | 89 | 0 | 0 | 0 (721) |
| M4_m4_grapple_near_r2101 | 89 | 0 | 0 | 0 (721) |
| M4_m4_grapple_near_r2102 | 90 | 0 | 0 | 0 (721) |

## Model choices (R5MotorV2)

- Units: SOURCE (u, u/s); one step per usercmd with the recorded dt (dt / n_cmds sub-steps); double precision; flat floor at initial_state z.
- Parameters: census class vars from the trial's own trial.json parameters; fitted constants (crouch speed 80, crouch decel 1500, stop snap 1, ground probe 2, multi-jump t0 0.15 / T 0.60, refund window 0.4) from the M2 params.json; movescale per step from samples.csv when present.
- Ground (GROUND-MODEL §2): piecewise accel low/mid/sprint by PRE-move speed, sprint edge rule 's + sprintAccel·msc·dt < speed·msc', caps speed/sprintspeed/crouch 80 ×msc, constant decel 1250 standing / 1500 ducked (not ×msc), snap < 1 u/s to 0, v = s·wishdir (instant redirect, diagonal normalized, input magnitude ignored on the ground).
- Sprint flag (GROUND-MODEL §3.3 'spr set one command after the press'; AIR-JUMP §3.1/§4.1): grounded pre-state, sprint held on this AND the previous command, forward > 0, not ducked, not sliding. Sprint button = IN_SPEED (1<<17) or bit 15 (the M2 trials record sprint as bit 15; in_sprint is always 0).
- Ducked state (choice): ducked = IN_DUCK held on the previous command (pre-state flag, mirrors the sprint flag lag); the release command still decelerates at 1500 in e5 data.
- Ground over-speed with input held (choice, not in GROUND-MODEL): s = max(cap, s - D·dt) with D = 1500 ducked (SLIDE-MODEL §4) or deceleration standing.
- speedScaleBack / speedScaleSide (choice, both 1 in every trial): multiply the cap when fwd < 0 / when fwd = 0 and side != 0.
- Jump (AIR-JUMP §2.2, §4.2, §6): press edge while grounded; frac = clamp(f + (1-f)(t-0.15)/0.60, f, 1), f = antiMultiJumpHeightFrac, t = start of the jump command - start of the last landing command (first jump of a trial: no landing yet -> frac 1, the trial reset is not a landing); V = sqrt(2 g H frac); vz = -g dt/2 + V, -g dt/2, move, -g dt/2 (post vz = V - 1.5 g dt); no ground friction; the jump command uses AirAccelerate (choice: 'ground clamp still applies' read as the clamp on ground commands only).
- Air (AIR-JUMP §2.1, §3.2): half-step gravity g = sv_gravity·gravityScale; AirAccelerate accelspeed = airAcceleration·dt, wishcap = airSpeed·msc, wishspeed = min(|wishvel|,1)·maxspeed_air (speed·msc, crouch·msc if duck held), current yaw; no air friction/drag.
- Land (AIR-JUMP §2.3): vz < 0 and floor within 2 u below after the move -> grounded, vz = 0, z kept; the next ground command snaps z to the floor.
- Slide (SLIDE-MODEL §6): duck press edge, grounded, |v| >= slideRequiredStartSpeed (unscaled) -> vPeak = min(|v| + 150·msc, 400·msc) before the move, lastBoost = vPeak - |v|; per command s = (s - 100·dt)·0.7^dt along the current velocity direction (no steering, no slideAccel); ends after the first command with post s < 125; ducked afterwards: over-speed decel 1500 down to 92.
- Slide jump (SLIDE-MODEL §5, H1): now - tBoost < 0.4 s -> s -= lastBoost, else s = max(s, 350); H = slideJumpHeight 50; the multi-jump frac is applied to slide jumps too (choice; frac = 1 in every trial used). Landing with duck held and s >= 200 resumes the slide with no boost and no speed loss.
- Lurch (M3 LURCH-MODEL §8): on an airborne command whose buttons gain a bit of IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT (0x618) vs the previous command, with move input, AFTER AirAccelerate: t = start of the press command - start of the last jump command (time-based window); lam = 0.7·clamp((0.5 - t)/0.3, 0, 1); d = normalize((1-lam)·v̂ + lam·wishdir) (skipped when zero); D = |v|·d - v, |D| <= 209.3; v_xy += D. Every new press edge can lurch (several presses per jump untested). Back = straight 209.3 brake, W re-press = no-op by geometry. No jump since Reset -> no lurch. Not modelled: cutoff speed 1100, mantle-boost suppression, movescale dependence of 209.3.
- Ground jump speed (M3 E8 hop350): a non-slide ground jump sets v_xy = min(|v_xy|, sprintspeed·msc) (299 at msc 1.15) before AirAccelerate, whatever the stance/sprint flag (walk-speed hops untested; min(v, cap) and max(v - 100, cap) only differ above 399).
- Slide chain (M3 E8 slide_chain): a slide resumed by a ducked landing (s >= slideRequiredStartSpeed) is flagged 'not boosted'; its slide jump keeps the horizontal speed (no 350 floor, no refund). A slide started by the duck press (boost) keeps the M2 rule. A trial that starts sliding counts as boosted (M2 behaviour).
- Not modelled: slideAccel / slideWantToStopDecel / slideMaxStopSpeed, landSlowdown, the 1.4e-5·vz² residual air gain, the duck transition (hull/eye offset), sprint timing keys, server corrections, slopes/steps/collisions, walls/climb/mantle in the replay (WallBounce / MantleBoost are separate primitives).

