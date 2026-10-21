# R5 replay — M2_e5_slidejump02_r276

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e5_slidejump02`, 821 steps aligned by cmd (81108..81928). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 821 | 177.81 | 266.61 | 177.79 | 266.61 | 86.50 | 291.17 | 82.04 | 258.68 | 8 |
| idle | 205 | 144.18 | 182.20 | 144.18 | 182.20 | 15.52 | 104.39 | 15.52 | 104.39 | 0 |
| accel | 288 | 99.62 | 178.74 | 99.62 | 178.74 | 92.62 | 138.40 | 92.62 | 138.40 | 0 |
| cruise | 215 | 240.06 | 266.61 | 240.05 | 266.61 | 122.54 | 291.17 | 110.90 | 258.68 | 8 |
| decel | 10 | 186.31 | 189.72 | 186.31 | 189.72 | 109.19 | 109.25 | 109.19 | 109.25 | 0 |
| air | 103 | 243.35 | 260.38 | 243.24 | 260.08 | 51.62 | 51.69 | 48.53 | 48.69 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 71 | 71 | 0 |
| release (first step without move input) | 677 | 677 | 0 |
| stop (spd2d < 1 u/s after release) | 687 | 699 | +12 |
| takeoff | 388 | 388 | 0 |
| land | 491 | 499 | +8 |
| apex step | 439 | 443 | +4 |
| peak speed step | 359 | 135 | -224 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 49.36 | 56.00 | +6.64 |
| takeoff v_z (u/s, state after takeoff step) | 267.03 | 284.61 | +17.58 |
| peak horizontal speed (u/s) | 458.20 | 199.53 | -258.68 |
| horizontal distance start→end (u) | 989.47 | 811.27 | -178.20 |
| release→stop (steps) | 10 | 22 | |
| takeoff→land (steps) | 103 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 388 | 388 | 0 |
| land | 491 | 499 | +8 |
| slide_start | 359, 491 |  |  |
| slide_end | 388, 599 |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 388/388 | 267.03 | 284.61 | +17.581 | 49.36 | 56.00 | +6.638 | 247.89 | 199.53 | -48.363 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | 199.525 | – | |
| accel_low (u/s²) | 2868.269 | – | – | 8/0 |
| accel_mid (u/s²) | 516.599 | 450.000 | -66.599 | 12/64 |
| accel_sprint (u/s²) | 114.924 | – | – | 123/0 |
| decel_stand (u/s²) | 1249.269 | 1250.000 | +0.731 | 9/23 |
| decel_duck (u/s²) | 1495.584 | – | – | 1/0 |

Flag mismatches (steps): grounded 8, sliding 137, sprinting 287, maxspeed 605/821.

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
