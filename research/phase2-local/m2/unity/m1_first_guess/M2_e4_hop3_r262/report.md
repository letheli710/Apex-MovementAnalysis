# R5 replay — M2_e4_hop3_r262

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e4_hop3`, 995 steps aligned by cmd (63813..64807). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 995 | 313.88 | 480.43 | 313.21 | 480.43 | 125.83 | 305.13 | 82.04 | 126.20 | 164 |
| idle | 254 | 406.68 | 480.43 | 406.68 | 480.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 143 | 44.77 | 75.17 | 44.77 | 75.17 | 80.78 | 126.20 | 80.78 | 126.20 | 0 |
| cruise | 173 | 331.25 | 462.32 | 329.51 | 462.32 | 213.56 | 305.13 | 99.45 | 99.63 | 164 |
| decel | 34 | 473.00 | 480.43 | 473.00 | 480.43 | 80.96 | 91.07 | 80.96 | 91.07 | 0 |
| air | 391 | 273.02 | 441.22 | 271.99 | 438.89 | 130.99 | 166.67 | 98.97 | 99.62 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 779 | 779 | 0 |
| stop (spd2d < 1 u/s after release) | 813 | 802 | -11 |
| takeoff | 216 | 216 | 0 |
| land | 325 | 327 | +2 |
| apex step | 270 | 271 | +1 |
| peak speed step | 524 | 135 | -389 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.94 | 56.00 | +1.06 |
| takeoff v_z (u/s, state after takeoff step) | 282.01 | 284.62 | +2.61 |
| peak horizontal speed (u/s) | 299.15 | 199.53 | -99.63 |
| horizontal distance start→end (u) | 1433.30 | 952.86 | -480.43 |
| release→stop (steps) | 34 | 23 | |
| takeoff→land (steps) | 109 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 216, 329, 442, 555, 668 | 216, 329, 442, 555, 668 | 0, 0, 0, 0, 0 |
| land | 325, 387, 524, 620, 745 | 327, 440, 553, 666, 779 | +2, +53, +29, +46, +34 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 216/216 | 282.01 | 284.62 | +2.610 | 54.93 | 56.00 | +1.064 | 296.87 | 199.53 | -97.344 |
| 2 | 329/329 | 150.93 | 284.62 | +133.688 | 16.24 | 56.00 | +39.760 | 299.00 | 199.53 | -99.478 |
| 3 | 442/442 | 211.32 | 284.59 | +73.262 | 31.24 | 56.00 | +24.763 | 299.01 | 199.53 | -99.480 |
| 4 | 555/555 | 170.22 | 284.63 | +114.414 | 20.50 | 56.00 | +35.502 | 299.00 | 199.53 | -99.478 |
| 5 | 668/668 | 199.73 | 284.62 | +84.883 | 27.97 | 56.00 | +28.024 | 299.00 | 199.53 | -99.479 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2875.866 | – | – | 7/0 |
| accel_mid (u/s²) | 517.253 | 450.000 | -67.253 | 17/63 |
| accel_sprint (u/s²) | 114.859 | – | – | 121/0 |
| decel_stand (u/s²) | 1249.322 | 1250.000 | +0.678 | 34/21 |

Flag mismatches (steps): grounded 164, sliding 0, sprinting 315, maxspeed 315/995.

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
