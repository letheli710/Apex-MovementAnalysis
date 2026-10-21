# R5 replay — M2_e4_hop0_r356

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e4_hop0`, 982 steps aligned by cmd (56957..57938). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 982 | 310.30 | 474.15 | 309.98 | 474.15 | 111.04 | 470.11 | 82.14 | 125.79 | 189 |
| idle | 253 | 402.15 | 474.15 | 402.15 | 474.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 140 | 44.08 | 73.78 | 44.08 | 73.78 | 80.87 | 125.79 | 80.87 | 125.79 | 0 |
| cruise | 169 | 327.77 | 456.03 | 327.21 | 456.03 | 165.87 | 305.85 | 99.44 | 99.62 | 68 |
| decel | 34 | 466.71 | 474.15 | 466.71 | 474.15 | 80.95 | 91.04 | 80.95 | 91.04 | 0 |
| air | 386 | 268.38 | 433.77 | 267.75 | 431.22 | 127.96 | 470.11 | 99.43 | 99.61 | 121 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 71 | 71 | 0 |
| release (first step without move input) | 766 | 766 | 0 |
| stop (spd2d < 1 u/s after release) | 800 | 789 | -11 |
| takeoff | 215 | 215 | 0 |
| land | 324 | 326 | +2 |
| apex step | 269 | 270 | +1 |
| peak speed step | 514 | 135 | -379 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.94 | 56.00 | +1.06 |
| takeoff v_z (u/s, state after takeoff step) | 282.01 | 284.61 | +2.60 |
| peak horizontal speed (u/s) | 299.14 | 199.53 | -99.62 |
| horizontal distance start→end (u) | 1410.48 | 936.33 | -474.15 |
| release→stop (steps) | 34 | 23 | |
| takeoff→land (steps) | 109 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 215, 325, 435, 545, 655 | 215, 435, 655 | 0, +110, +220 |
| land | 324, 383, 514, 610, 730 | 326, 546, 766 | +2, +163, +252 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 215/215 | 282.01 | 284.61 | +2.600 | 54.94 | 56.00 | +1.062 | 298.60 | 199.53 | -99.077 |
| 2 | 325/435 | 150.92 | 284.61 | +133.684 | 16.24 | 56.00 | +39.757 | 298.91 | 199.53 | -99.381 |
| 3 | 435/655 | 206.18 | 284.61 | +78.428 | 29.76 | 56.00 | +26.238 | 299.01 | 199.53 | -99.480 |
| 4 | 545/– | 170.22 | – | – | 20.50 | – | – | 299.00 | – | – |
| 5 | 655/– | 194.56 | – | – | 26.58 | – | – | 299.00 | – | – |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2870.616 | – | – | 7/0 |
| accel_mid (u/s²) | 516.785 | 450.000 | -66.785 | 17/64 |
| accel_sprint (u/s²) | 117.202 | – | – | 120/0 |
| decel_stand (u/s²) | 1248.927 | 1250.000 | +1.073 | 34/21 |

Flag mismatches (steps): grounded 189, sliding 0, sprinting 308, maxspeed 308/982.

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
