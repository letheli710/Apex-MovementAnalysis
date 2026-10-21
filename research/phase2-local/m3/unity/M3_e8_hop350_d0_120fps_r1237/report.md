# R5 replay — M3_e8_hop350_d0_120fps_r1237

Model `R5MotorV2/m3` (not tuned per trial). Trial source `r5flowstate`, experiment `M3_e8_hop350_d0`, 695 steps aligned by cmd (35973..36667). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; lurchLamMax 0.7; lurchFullEnd 0.2; lurchZero 0.5; lurchClamp 209.3; groundJumpClampToSprintCap True; slideJumpFloorOnlyAfterBoost True; gravity 750.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 695 | 7.92 | 20.22 | 1.99 | 3.69 | 61.70 | 375.73 | 5.86 | 51.00 | 77 |
| idle | 92 | 1.90 | 3.23 | 1.86 | 3.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 240 | 0.47 | 0.71 | 0.22 | 0.34 | 0.13 | 0.22 | 0.13 | 0.22 | 0 |
| cruise | 112 | 3.17 | 20.22 | 1.92 | 3.58 | 22.70 | 216.65 | 0.02 | 0.17 | 2 |
| decel | 28 | 3.21 | 3.23 | 3.15 | 3.16 | 0.17 | 0.26 | 0.17 | 0.26 | 0 |
| air | 223 | 13.70 | 19.78 | 2.78 | 3.69 | 107.74 | 375.73 | 10.34 | 51.00 | 75 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 60 | 60 | 0 |
| release (first step without move input) | 635 | 635 | 0 |
| stop (spd2d < 1 u/s after release) | 663 | 663 | 0 |
| takeoff | 372 | 372 | 0 |
| land | 449 | 457 | +8 |
| apex step | 414 | 414 | 0 |
| peak speed step | 300 | 300 | 0 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 32.85 | 48.86 | +16.01 |
| takeoff v_z (u/s, state after takeoff step) | 264.16 | 264.48 | +0.32 |
| peak horizontal speed (u/s) | 457.80 | 457.80 | 0.00 |
| horizontal distance start→end (u) | 1486.38 | 1489.54 | +3.16 |
| release→stop (steps) | 28 | 28 | |
| takeoff→land (steps) | 77 | 85 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 372, 450, 499, 549 | 372, 499 | 0, +49 |
| land | 449, 498, 548, 598 | 457, 564 | +8, +66 |
| slide_start | 300 | 300 | 0 |
| slide_end | 372 | 372 | 0 |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 372/372 | 264.16 | 264.48 | +0.322 | 32.20 | 48.86 | +16.664 | 350.01 | 350.00 | -0.006 |
| 2 | 450/499 | 149.35 | 202.32 | +52.966 | 16.13 | 29.00 | +12.865 | 299.00 | 299.00 | -0.003 |
| 3 | 499/– | 149.36 | – | – | 16.13 | – | – | 299.00 | – | – |
| 4 | 549/– | 149.36 | – | – | 16.13 | – | – | 299.00 | – | – |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2877.135 | 2875.000 | -2.135 | 6/6 |
| accel_mid (u/s²) | 517.821 | 517.500 | -0.321 | 13/13 |
| accel_sprint (u/s²) | 115.079 | 115.000 | -0.079 | 103/103 |
| decel_stand (u/s²) | 1251.118 | 1250.000 | -1.118 | 28/28 |

Flag mismatches (steps): grounded 77, sliding 0, sprinting 77, maxspeed 86/695.

## Model choices

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

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
