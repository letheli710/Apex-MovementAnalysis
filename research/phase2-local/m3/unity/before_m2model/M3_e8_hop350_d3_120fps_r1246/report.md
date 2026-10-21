# R5 replay — M3_e8_hop350_d3_120fps_r1246

Model `R5MotorV2/m2` (not tuned per trial). Trial source `r5flowstate`, experiment `M3_e8_hop350_d3`, 702 steps aligned by cmd (43955..44656). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 102; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; gravity 750.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 702 | 8.27 | 25.95 | 1.46 | 2.82 | 61.86 | 394.45 | 5.01 | 51.00 | 83 |
| idle | 92 | 1.35 | 2.29 | 1.30 | 2.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 240 | 0.46 | 0.71 | 0.19 | 0.36 | 0.60 | 1.65 | 0.60 | 1.65 | 0 |
| cruise | 121 | 5.47 | 25.95 | 1.42 | 2.66 | 44.84 | 237.58 | 3.52 | 31.12 | 8 |
| decel | 28 | 2.29 | 2.30 | 2.19 | 2.20 | 0.16 | 0.27 | 0.16 | 0.27 | 0 |
| air | 221 | 14.11 | 25.25 | 2.07 | 2.82 | 105.14 | 394.45 | 8.52 | 51.00 | 75 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 60 | 60 | 0 |
| release (first step without move input) | 642 | 642 | 0 |
| stop (spd2d < 1 u/s after release) | 670 | 670 | 0 |
| takeoff | 372 | 372 | 0 |
| land | 449 | 457 | +8 |
| apex step | 414 | 414 | 0 |
| peak speed step | 300 | 300 | 0 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 32.85 | 48.86 | +16.01 |
| takeoff v_z (u/s, state after takeoff step) | 264.14 | 264.48 | +0.34 |
| peak horizontal speed (u/s) | 457.80 | 457.80 | 0.00 |
| horizontal distance start→end (u) | 1505.69 | 1507.89 | +2.20 |
| release→stop (steps) | 28 | 28 | |
| takeoff→land (steps) | 77 | 85 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 372, 453, 505, 557 | 372, 505 | 0, +52 |
| land | 449, 501, 553, 605 | 457, 574 | +8, +73 |
| slide_start | 300 | 300 | 0 |
| slide_end | 372 | 372 | 0 |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 372/372 | 264.14 | 264.48 | +0.337 | 32.20 | 48.86 | +16.666 | 350.01 | 350.00 | -0.006 |
| 2 | 453/505 | 149.35 | 213.55 | +64.202 | 16.13 | 32.21 | +16.077 | 299.00 | 299.00 | -0.003 |
| 3 | 505/– | 149.35 | – | – | 16.13 | – | – | 299.00 | – | – |
| 4 | 557/– | 149.35 | – | – | 16.13 | – | – | 299.00 | – | – |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2877.415 | 2875.000 | -2.415 | 6/6 |
| accel_mid (u/s²) | 517.985 | 517.500 | -0.485 | 13/13 |
| accel_sprint (u/s²) | 115.128 | 117.300 | +2.172 | 103/101 |
| decel_stand (u/s²) | 1251.138 | 1250.000 | -1.138 | 28/28 |

Flag mismatches (steps): grounded 83, sliding 0, sprinting 83, maxspeed 92/702.

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
