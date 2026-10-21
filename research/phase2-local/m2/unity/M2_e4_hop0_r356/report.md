# R5 replay — M2_e4_hop0_r356

Model `R5MotorV2/m2` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e4_hop0`, 982 steps aligned by cmd (56957..57938). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 102; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; gravity 750.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 982 | 1.25 | 1.73 | 1.25 | 1.73 | 0.19 | 0.56 | 0.16 | 0.38 | 0 |
| idle | 253 | 1.44 | 1.70 | 1.44 | 1.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 140 | 0.30 | 0.52 | 0.30 | 0.52 | 0.33 | 0.38 | 0.33 | 0.38 | 0 |
| cruise | 169 | 1.39 | 1.72 | 1.39 | 1.72 | 0.06 | 0.38 | 0.06 | 0.38 | 0 |
| decel | 34 | 1.72 | 1.73 | 1.72 | 1.73 | 0.19 | 0.25 | 0.19 | 0.25 | 0 |
| air | 386 | 1.21 | 1.66 | 1.21 | 1.66 | 0.21 | 0.56 | 0.13 | 0.37 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 71 | 71 | 0 |
| release (first step without move input) | 766 | 766 | 0 |
| stop (spd2d < 1 u/s after release) | 800 | 800 | 0 |
| takeoff | 215 | 215 | 0 |
| land | 324 | 324 | 0 |
| apex step | 269 | 269 | 0 |
| peak speed step | 514 | 384 | -130 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.94 | 55.00 | +0.06 |
| takeoff v_z (u/s, state after takeoff step) | 282.01 | 282.00 | -0.01 |
| peak horizontal speed (u/s) | 299.14 | 299.00 | -0.14 |
| horizontal distance start→end (u) | 1410.48 | 1412.18 | +1.70 |
| release→stop (steps) | 34 | 34 | |
| takeoff→land (steps) | 109 | 109 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 215, 325, 435, 545, 655 | 215, 325, 435, 545, 655 | 0, 0, 0, 0, 0 |
| land | 324, 383, 514, 610, 730 | 324, 383, 514, 610, 730 | 0, 0, 0, 0, 0 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 215/215 | 282.01 | 282.00 | -0.010 | 54.94 | 55.00 | +0.061 | 298.60 | 298.98 | +0.374 |
| 2 | 325/325 | 150.92 | 150.92 | -0.009 | 16.24 | 16.25 | +0.012 | 298.91 | 298.98 | +0.070 |
| 3 | 435/435 | 206.18 | 206.30 | +0.117 | 29.76 | 29.82 | +0.064 | 299.01 | 299.00 | -0.005 |
| 4 | 545/545 | 170.22 | 170.30 | +0.076 | 20.50 | 20.53 | +0.032 | 299.00 | 299.00 | -0.003 |
| 5 | 655/655 | 194.56 | 194.68 | +0.125 | 26.58 | 26.64 | +0.059 | 299.00 | 299.00 | -0.004 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2870.616 | 2875.000 | +4.384 | 7/7 |
| accel_mid (u/s²) | 516.785 | 517.500 | +0.715 | 17/17 |
| accel_sprint (u/s²) | 117.202 | 117.300 | +0.098 | 120/120 |
| decel_stand (u/s²) | 1248.927 | 1250.000 | +1.073 | 34/34 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 0/982.

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
- Not modelled: lurch (first strafe press in air), slideAccel / slideWantToStopDecel / slideMaxStopSpeed, landSlowdown, skip_speed_reduce, the 1.4e-5·vz² residual air gain, the duck transition (hull/eye offset), sprint timing keys, server corrections, slopes/steps/collisions.

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
