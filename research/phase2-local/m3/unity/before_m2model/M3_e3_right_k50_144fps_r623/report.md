# R5 replay — M3_e3_right_k50_144fps_r623

Model `R5MotorV2/m2` (not tuned per trial). Trial source `r5flowstate`, experiment `M3_e3_right_k50`, 469 steps aligned by cmd (17535..18003). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; gravity 750.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 469 | 13.81 | 36.40 | 13.81 | 36.40 | 55.09 | 298.12 | 8.12 | 45.18 | 0 |
| idle | 122 | 12.31 | 19.23 | 12.31 | 19.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 140 | 0.03 | 0.06 | 0.03 | 0.05 | 0.02 | 0.06 | 0.02 | 0.06 | 0 |
| cruise | 76 | 21.27 | 36.40 | 21.27 | 36.40 | 111.39 | 298.12 | 19.32 | 45.18 | 0 |
| decel | 22 | 19.23 | 19.23 | 19.23 | 19.23 | 0.02 | 0.03 | 0.02 | 0.03 | 0 |
| air | 109 | 16.16 | 35.87 | 16.16 | 35.87 | 66.38 | 140.19 | 4.82 | 7.75 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 397 | 397 | 0 |
| stop (spd2d < 1 u/s after release) | 419 | 419 | 0 |
| takeoff | 216 | 216 | 0 |
| land | 325 | 325 | 0 |
| apex step | 270 | 270 | 0 |
| peak speed step | 325 | 286 | -39 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.93 | 54.99 | +0.06 |
| takeoff v_z (u/s, state after takeoff step) | 281.90 | 281.92 | +0.02 |
| peak horizontal speed (u/s) | 296.29 | 303.97 | +7.68 |
| horizontal distance start→end (u) | 495.33 | 478.86 | -16.47 |
| release→stop (steps) | 22 | 22 | |
| takeoff→land (steps) | 109 | 109 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 216 | 216 | 0 |
| land | 325 | 325 | 0 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 216/216 | 281.90 | 281.92 | +0.018 | 54.92 | 54.99 | +0.064 | 296.05 | 296.03 | -0.016 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2874.075 | 2875.000 | +0.925 | 7/7 |
| accel_mid (u/s²) | 509.828 | 517.500 | +7.672 | 28/17 |
| accel_sprint (u/s²) | 117.237 | 115.000 | -2.237 | 124/120 |
| decel_stand (u/s²) | 1250.197 | 1250.000 | -0.197 | 22/22 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 0/469.

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
