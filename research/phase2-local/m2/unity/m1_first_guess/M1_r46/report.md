# R5 replay — M1_r46

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M1_loop`, 1225 steps aligned by cmd (3636..4860). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 1225 | 32.19 | 34.49 | 32.17 | 34.49 | 23.16 | 288.09 | 20.07 | 125.52 | 2 |
| idle | 662 | 31.55 | 33.48 | 31.55 | 33.42 | 15.69 | 288.09 | 0.01 | 0.30 | 2 |
| accel | 23 | 9.34 | 16.85 | 9.34 | 16.85 | 109.94 | 125.52 | 109.94 | 125.52 | 0 |
| cruise | 409 | 33.61 | 34.49 | 33.56 | 34.49 | 22.94 | 124.44 | 22.94 | 124.44 | 0 |
| decel | 22 | 33.42 | 33.42 | 33.42 | 33.42 | 0.01 | 0.01 | 0.01 | 0.01 | 0 |
| air | 109 | 33.44 | 33.48 | 33.42 | 33.42 | 2.62 | 2.63 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 504 | 504 | 0 |
| stop (spd2d < 1 u/s after release) | 526 | 526 | 0 |
| takeoff | 936 | 936 | 0 |
| land | 1045 | 1047 | +2 |
| apex step | 990 | 991 | +1 |
| peak speed step | 95 | 135 | +40 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.87 | 56.00 | +1.13 |
| takeoff v_z (u/s, state after takeoff step) | 281.96 | 284.59 | +2.63 |
| peak horizontal speed (u/s) | 199.53 | 199.53 | 0.00 |
| horizontal distance start→end (u) | 603.80 | 570.38 | -33.42 |
| release→stop (steps) | 22 | 22 | |
| takeoff→land (steps) | 109 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 936 | 936 | 0 |
| land | 1045 | 1047 | +2 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 936/936 | 281.96 | 284.59 | +2.625 | 54.99 | 56.00 | +1.008 | 0.00 | 0.00 | 0.000 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | 199.525 | 199.525 | 0.000 | |
| accel_low (u/s²) | 2875.236 | – | – | 7/0 |
| accel_mid (u/s²) | 517.530 | 450.000 | -67.530 | 16/63 |
| decel_stand (u/s²) | 1249.990 | 1250.000 | +0.010 | 22/23 |

Flag mismatches (steps): grounded 2, sliding 0, sprinting 0.

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
