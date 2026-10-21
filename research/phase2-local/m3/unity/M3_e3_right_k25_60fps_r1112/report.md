# R5 replay — M3_e3_right_k25_60fps_r1112

Model `R5MotorV2/m3` (not tuned per trial). Trial source `r5flowstate`, experiment `M3_e3_right_k25`, 200 steps aligned by cmd (6304..6503). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; lurchLamMax 0.7; lurchFullEnd 0.2; lurchZero 0.5; lurchClamp 209.3; groundJumpClampToSprintCap True; slideJumpFloorOnlyAfterBoost True; gravity 750.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 200 | 23.77 | 44.05 | 23.77 | 44.05 | 55.32 | 345.04 | 11.19 | 68.85 | 0 |
| idle | 51 | 28.26 | 44.05 | 28.26 | 44.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 58 | 0.01 | 0.02 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0 |
| cruise | 38 | 37.98 | 44.05 | 37.98 | 44.05 | 126.91 | 345.04 | 25.67 | 68.85 | 0 |
| decel | 9 | 44.05 | 44.05 | 44.05 | 44.05 | 0.01 | 0.01 | 0.01 | 0.01 | 0 |
| air | 44 | 0.09 | 0.17 | 0.05 | 0.11 | 0.31 | 0.55 | 0.14 | 0.17 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 30 | 30 | 0 |
| release (first step without move input) | 170 | 170 | 0 |
| stop (spd2d < 1 u/s after release) | 179 | 179 | 0 |
| takeoff | 90 | 90 | 0 |
| land | 134 | 134 | 0 |
| apex step | 112 | 112 | 0 |
| peak speed step | 134 | 117 | -17 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 53.55 | 53.60 | +0.06 |
| takeoff v_z (u/s, state after takeoff step) | 271.06 | 271.09 | +0.02 |
| peak horizontal speed (u/s) | 300.81 | 300.63 | -0.18 |
| horizontal distance start→end (u) | 506.67 | 484.36 | -22.31 |
| release→stop (steps) | 9 | 9 | |
| takeoff→land (steps) | 44 | 44 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 90 | 90 | 0 |
| land | 134 | 134 | 0 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 90/90 | 271.06 | 271.09 | +0.023 | 53.54 | 53.60 | +0.065 | 299.02 | 299.00 | -0.015 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2875.045 | 2875.000 | -0.045 | 3/3 |
| accel_mid (u/s²) | 548.482 | 517.500 | -30.982 | 14/7 |
| accel_sprint (u/s²) | 114.567 | 115.000 | +0.433 | 51/49 |
| decel_stand (u/s²) | 1249.947 | 1250.000 | +0.053 | 9/9 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 0/200.

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
