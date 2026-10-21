# R5 replay — M2_e4_hop3_r261

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e4_hop3`, 995 steps aligned by cmd (62604..63598). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 995 | 314.05 | 480.62 | 313.38 | 480.62 | 126.01 | 306.39 | 82.08 | 126.30 | 165 |
| idle | 254 | 406.83 | 480.62 | 406.83 | 480.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 142 | 44.53 | 74.58 | 44.53 | 74.58 | 80.88 | 126.30 | 80.88 | 126.30 | 0 |
| cruise | 175 | 330.91 | 462.51 | 329.17 | 462.51 | 213.07 | 306.39 | 99.43 | 99.63 | 165 |
| decel | 34 | 473.18 | 480.62 | 473.18 | 480.62 | 80.94 | 91.03 | 80.94 | 91.03 | 0 |
| air | 390 | 272.85 | 440.74 | 271.82 | 438.38 | 131.10 | 166.72 | 99.00 | 99.62 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 779 | 779 | 0 |
| stop (spd2d < 1 u/s after release) | 813 | 802 | -11 |
| takeoff | 216 | 216 | 0 |
| land | 325 | 327 | +2 |
| apex step | 270 | 270 | 0 |
| peak speed step | 523 | 135 | -388 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.94 | 56.00 | +1.06 |
| takeoff v_z (u/s, state after takeoff step) | 281.95 | 284.59 | +2.64 |
| peak horizontal speed (u/s) | 299.15 | 199.53 | -99.63 |
| horizontal distance start→end (u) | 1433.53 | 952.92 | -480.62 |
| release→stop (steps) | 34 | 23 | |
| takeoff→land (steps) | 109 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 216, 329, 442, 555, 668 | 216, 329, 442, 555, 668 | 0, 0, 0, 0, 0 |
| land | 325, 387, 523, 621, 744 | 327, 440, 553, 666, 779 | +2, +53, +30, +45, +35 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 216/216 | 281.95 | 284.59 | +2.635 | 54.93 | 56.00 | +1.068 | 296.99 | 199.53 | -97.460 |
| 2 | 329/329 | 150.93 | 284.61 | +133.683 | 16.24 | 56.00 | +39.759 | 299.00 | 199.53 | -99.478 |
| 3 | 442/442 | 210.77 | 284.68 | +73.913 | 31.05 | 56.00 | +24.947 | 299.01 | 199.53 | -99.480 |
| 4 | 555/555 | 172.02 | 284.71 | +112.683 | 20.90 | 56.00 | +35.097 | 299.00 | 199.53 | -99.478 |
| 5 | 668/668 | 198.07 | 284.61 | +86.540 | 27.52 | 56.00 | +28.474 | 299.00 | 199.53 | -99.479 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2876.947 | – | – | 7/0 |
| accel_mid (u/s²) | 516.776 | 450.000 | -66.776 | 17/63 |
| accel_sprint (u/s²) | 114.868 | – | – | 121/0 |
| decel_stand (u/s²) | 1248.516 | 1250.000 | +1.484 | 34/21 |

Flag mismatches (steps): grounded 165, sliding 0, sprinting 316, maxspeed 316/995.

## Model choices

- Units: SOURCE (u, u/s); per-usercmd step with the recorded dt (dt / n_cmds sub-steps); double precision.
- Floor: flat plane at initial_state.pos.z; on ground z is pinned to it and v_z = 0.
- Wish: wishvel = cmd_fwd*F(yaw) + cmd_side*R(yaw), F=(cos,sin,0), R=(sin,-cos,0); wishspeed = speed*moveScale*min(|wishvel|,1).
- Ground: v_h += clamp_len(wishdir*wishspeed - v_h, rate*dt), rate = acceleration when wishspeed>0 else deceleration (vector approach, no separate friction, no lowSpeed/lowAcceleration branch).
- Jump: on the JUMP press edge while grounded, v_z = sqrt(2*sv_gravity*gravityScale*jumpHeight); no ground friction on that command; the air step runs on the same command.
- Air: half-step gravity (v_z -= g*dt/2; move; v_z -= g*dt/2); AirAccelerate with wishspd = min(wishspeed, airSpeed), accelspeed = min(airAcceleration*dt, wishspd - v_h.wishdir) (Phase 1 §3 [C] form, no *wishspeed).
- Land: after an air step, pos.z <= floor and v_z <= 0 -> snap to floor, v_z = 0, grounded.
- Not modelled: sprint, crouch/slide, lowSpeed/lowAcceleration, side/back speed scale, landSlowdown, skip_time/bhop penalties, collisions/slopes/steps.

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
