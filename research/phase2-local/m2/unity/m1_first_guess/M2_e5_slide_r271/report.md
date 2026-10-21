# R5 replay — M2_e5_slide_r271

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e5_slide`, 936 steps aligned by cmd (75423..76358). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 936 | 201.20 | 324.66 | 201.20 | 324.66 | 95.12 | 258.67 | 95.12 | 258.67 | 0 |
| idle | 206 | 123.80 | 157.47 | 123.80 | 157.47 | 15.73 | 105.68 | 15.73 | 105.68 | 0 |
| accel | 288 | 99.74 | 178.90 | 99.74 | 178.90 | 92.72 | 138.71 | 92.72 | 138.71 | 0 |
| cruise | 432 | 270.49 | 324.66 | 270.49 | 324.66 | 116.10 | 258.67 | 116.10 | 258.67 | 0 |
| decel | 10 | 161.60 | 164.91 | 161.60 | 164.91 | 109.20 | 109.22 | 109.20 | 109.22 | 0 |
| air | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 792 | 792 | 0 |
| stop (spd2d < 1 u/s after release) | 802 | 815 | +13 |
| takeoff | – | – | – |
| land | – | – | – |
| apex step | – | – | – |
| peak speed step | 360 | 135 | -225 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | – | – | – |
| takeoff v_z (u/s, state after takeoff step) | – | – | – |
| peak horizontal speed (u/s) | 458.20 | 199.53 | -258.67 |
| horizontal distance start→end (u) | 1122.84 | 969.47 | -153.37 |
| release→stop (steps) | 10 | 23 | |
| takeoff→land (steps) | – | – | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff |  |  |  |
| land |  |  |  |
| slide_start | 360 |  |  |
| slide_end | 603 |  |  |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | 92.000 | 199.525 | +107.525 | |
| accel_low (u/s²) | 2874.003 | – | – | 8/0 |
| accel_mid (u/s²) | 516.575 | 450.000 | -66.575 | 12/63 |
| accel_sprint (u/s²) | 114.839 | – | – | 122/0 |
| decel_stand (u/s²) | 1249.365 | 1250.000 | +0.635 | 9/23 |
| decel_duck (u/s²) | 1499.405 | – | – | 1/0 |

Flag mismatches (steps): grounded 0, sliding 243, sprinting 287, maxspeed 719/936.

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
