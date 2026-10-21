# R5 replay — M2_e1_walk_r301

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e1_walk`, 792 steps aligned by cmd (3590..4381). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 792 | 32.12 | 34.50 | 32.12 | 34.50 | 24.92 | 125.64 | 24.92 | 125.64 | 0 |
| idle | 338 | 30.58 | 34.47 | 30.58 | 34.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 23 | 9.35 | 16.85 | 9.35 | 16.85 | 110.04 | 125.64 | 110.04 | 125.64 | 0 |
| cruise | 409 | 34.01 | 34.50 | 34.01 | 34.50 | 22.83 | 124.53 | 22.83 | 124.53 | 0 |
| decel | 22 | 34.47 | 34.47 | 34.47 | 34.47 | 0.01 | 0.01 | 0.01 | 0.01 | 0 |
| air | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 504 | 504 | 0 |
| stop (spd2d < 1 u/s after release) | 526 | 526 | 0 |
| takeoff | – | – | – |
| land | – | – | – |
| apex step | – | – | – |
| peak speed step | 95 | 135 | +40 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | – | – | – |
| takeoff v_z (u/s, state after takeoff step) | – | – | – |
| peak horizontal speed (u/s) | 199.53 | 199.53 | 0.00 |
| horizontal distance start→end (u) | 605.01 | 570.54 | -34.47 |
| release→stop (steps) | 22 | 22 | |
| takeoff→land (steps) | – | – | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff |  |  |  |
| land |  |  |  |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | 199.525 | 199.525 | 0.000 | |
| accel_low (u/s²) | 2874.774 | – | – | 7/0 |
| accel_mid (u/s²) | 517.580 | 450.000 | -67.580 | 16/63 |
| decel_stand (u/s²) | 1249.977 | 1250.000 | +0.023 | 22/22 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 0/792.

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
