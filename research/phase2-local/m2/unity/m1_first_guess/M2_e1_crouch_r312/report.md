# R5 replay — M2_e1_crouch_r312

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e1_crouch`, 1008 steps aligned by cmd (14707..15714). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 1008 | 201.20 | 293.39 | 201.20 | 293.39 | 67.82 | 121.44 | 67.82 | 121.44 | 0 |
| idle | 568 | 230.91 | 293.39 | 230.91 | 293.39 | 11.45 | 120.94 | 11.45 | 120.94 | 0 |
| accel | 4 | 0.70 | 1.16 | 0.70 | 1.16 | 45.88 | 67.10 | 45.88 | 67.10 | 0 |
| cruise | 428 | 151.89 | 280.67 | 151.89 | 280.67 | 101.93 | 107.53 | 101.93 | 107.53 | 0 |
| decel | 8 | 284.24 | 287.12 | 284.24 | 287.12 | 115.42 | 121.44 | 115.42 | 121.44 | 0 |
| air | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 216 | 216 | 0 |
| release (first step without move input) | 648 | 648 | 0 |
| stop (spd2d < 1 u/s after release) | 656 | 670 | +14 |
| takeoff | – | – | – |
| land | – | – | – |
| apex step | – | – | – |
| peak speed step | 220 | 279 | +59 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | – | – | – |
| takeoff v_z (u/s, state after takeoff step) | – | – | – |
| peak horizontal speed (u/s) | 92.00 | 199.53 | +107.53 |
| horizontal distance start→end (u) | 277.80 | 571.19 | +293.39 |
| release→stop (steps) | 8 | 22 | |
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
| terminal speed (u/s, 1 s before release) | 92.000 | 199.525 | +107.525 | |
| accel_low (u/s²) | 2874.919 | – | – | 4/0 |
| accel_mid (u/s²) | – | 450.000 | – | 0/63 |
| decel_stand (u/s²) | – | 1250.000 | – | 0/22 |
| decel_duck (u/s²) | 1498.980 | – | – | 8/0 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 800/1008.

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
