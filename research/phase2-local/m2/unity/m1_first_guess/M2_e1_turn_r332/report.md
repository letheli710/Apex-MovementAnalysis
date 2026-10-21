# R5 replay — M2_e1_turn_r332

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e1_turn`, 936 steps aligned by cmd (35585..36520). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 936 | 154.60 | 215.42 | 154.60 | 215.42 | 77.71 | 126.68 | 76.97 | 126.68 | 0 |
| idle | 326 | 154.57 | 175.11 | 154.57 | 175.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 139 | 44.22 | 73.87 | 44.22 | 73.87 | 81.47 | 126.68 | 81.47 | 126.68 | 0 |
| cruise | 437 | 174.31 | 215.42 | 174.31 | 215.42 | 101.12 | 111.88 | 99.90 | 102.67 | 0 |
| decel | 34 | 174.34 | 175.11 | 174.34 | 175.11 | 87.67 | 99.76 | 87.67 | 99.76 | 0 |
| air | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 648 | 648 | 0 |
| stop (spd2d < 1 u/s after release) | 682 | 670 | -12 |
| takeoff | – | – | – |
| land | – | – | – |
| apex step | – | – | – |
| peak speed step | 411 | 360 | -51 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | – | – | – |
| takeoff v_z (u/s, state after takeoff step) | – | – | – |
| peak horizontal speed (u/s) | 299.00 | 199.53 | -99.48 |
| horizontal distance start→end (u) | 556.66 | 383.49 | -173.17 |
| release→stop (steps) | 34 | 22 | |
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
| terminal speed (u/s, 1 s before release) | 299.000 | 199.362 | -99.637 | |
| accel_low (u/s²) | 2873.475 | – | – | 7/0 |
| accel_mid (u/s²) | 517.342 | 450.000 | -67.342 | 17/63 |
| accel_sprint (u/s²) | 117.186 | 37.424 | -79.762 | 119/11 |
| decel_stand (u/s²) | 1248.049 | 1250.000 | +1.951 | 34/22 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 575, maxspeed 575/936.

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
