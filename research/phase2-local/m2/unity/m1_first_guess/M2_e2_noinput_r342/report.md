# R5 replay — M2_e2_noinput_r342

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e2_noinput`, 653 steps aligned by cmd (45793..46445). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 653 | 182.20 | 272.60 | 182.20 | 272.60 | 77.64 | 302.09 | 76.01 | 138.70 | 2 |
| idle | 221 | 223.84 | 272.60 | 223.84 | 272.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 136 | 45.68 | 75.29 | 45.68 | 75.29 | 85.38 | 138.70 | 85.38 | 138.70 | 0 |
| cruise | 152 | 131.51 | 180.05 | 131.51 | 180.05 | 99.44 | 99.48 | 99.44 | 99.48 | 0 |
| decel | 35 | 265.36 | 272.60 | 265.36 | 272.60 | 101.78 | 302.09 | 75.51 | 99.51 | 2 |
| air | 109 | 218.99 | 255.16 | 218.98 | 255.16 | 99.53 | 99.54 | 99.51 | 99.51 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 365 | 365 | 0 |
| stop (spd2d < 1 u/s after release) | 504 | 494 | -10 |
| takeoff | 360 | 360 | 0 |
| land | 469 | 471 | +2 |
| apex step | 414 | 415 | +1 |
| peak speed step | 364 | 135 | -229 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 55.00 | 56.00 | +1.00 |
| takeoff v_z (u/s, state after takeoff step) | 282.11 | 284.68 | +2.56 |
| peak horizontal speed (u/s) | 299.03 | 199.53 | -99.51 |
| horizontal distance start→end (u) | 798.44 | 525.83 | -272.60 |
| release→stop (steps) | 139 | 129 | |
| takeoff→land (steps) | 109 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 360 | 360 | 0 |
| land | 469 | 471 | +2 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 360/360 | 282.11 | 284.68 | +2.564 | 55.00 | 56.00 | +1.000 | 299.01 | 199.53 | -99.482 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2873.098 | – | – | 8/0 |
| accel_mid (u/s²) | 516.750 | 450.000 | -66.750 | 12/63 |
| accel_sprint (u/s²) | 117.204 | – | – | 120/0 |
| decel_stand (u/s²) | 1248.745 | 1250.000 | +1.255 | 33/21 |

Flag mismatches (steps): grounded 2, sliding 0, sprinting 288, maxspeed 288/653.

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
