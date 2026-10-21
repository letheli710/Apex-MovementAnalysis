# R5 replay — M2_e5_slide_r272

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e5_slide`, 935 steps aligned by cmd (76561..77495). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 935 | 198.61 | 321.53 | 198.61 | 321.53 | 94.48 | 258.64 | 94.48 | 258.64 | 0 |
| idle | 205 | 121.41 | 153.99 | 121.41 | 153.99 | 15.37 | 103.85 | 15.37 | 103.85 | 0 |
| accel | 288 | 97.27 | 175.70 | 97.27 | 175.70 | 90.75 | 125.95 | 90.75 | 125.95 | 0 |
| cruise | 432 | 267.39 | 321.53 | 267.39 | 321.53 | 115.94 | 258.64 | 115.94 | 258.64 | 0 |
| decel | 10 | 158.15 | 161.55 | 158.15 | 161.55 | 109.19 | 109.24 | 109.19 | 109.24 | 0 |
| air | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 71 | 71 | 0 |
| release (first step without move input) | 791 | 791 | 0 |
| stop (spd2d < 1 u/s after release) | 801 | 813 | +12 |
| takeoff | – | – | – |
| land | – | – | – |
| apex step | – | – | – |
| peak speed step | 359 | 134 | -225 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | – | – | – |
| takeoff v_z (u/s, state after takeoff step) | – | – | – |
| peak horizontal speed (u/s) | 458.17 | 199.53 | -258.64 |
| horizontal distance start→end (u) | 1120.53 | 970.49 | -150.04 |
| release→stop (steps) | 10 | 22 | |
| takeoff→land (steps) | – | – | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff |  |  |  |
| land |  |  |  |
| slide_start | 359 |  |  |
| slide_end | 602 |  |  |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | 92.000 | 199.525 | +107.525 | |
| accel_low (u/s²) | 2870.616 | – | – | 7/0 |
| accel_mid (u/s²) | 517.437 | 450.000 | -67.437 | 17/63 |
| accel_sprint (u/s²) | 114.922 | – | – | 121/0 |
| decel_stand (u/s²) | 1248.164 | 1250.000 | +1.836 | 9/22 |
| decel_duck (u/s²) | 1496.983 | – | – | 1/0 |

Flag mismatches (steps): grounded 0, sliding 243, sprinting 287, maxspeed 719/935.

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
