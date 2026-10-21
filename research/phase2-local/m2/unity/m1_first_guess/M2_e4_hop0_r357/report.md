# R5 replay — M2_e4_hop0_r357

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e4_hop0`, 983 steps aligned by cmd (58166..59148). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 983 | 310.94 | 475.31 | 310.63 | 475.31 | 110.01 | 450.31 | 82.14 | 125.80 | 188 |
| idle | 254 | 402.34 | 475.31 | 402.34 | 475.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 140 | 44.15 | 73.93 | 44.15 | 73.93 | 80.94 | 125.80 | 80.94 | 125.80 | 0 |
| cruise | 169 | 328.04 | 457.20 | 327.51 | 457.20 | 165.84 | 305.01 | 99.45 | 99.62 | 67 |
| decel | 34 | 467.90 | 475.31 | 467.90 | 475.31 | 80.75 | 90.97 | 80.75 | 90.97 | 0 |
| air | 386 | 269.41 | 435.57 | 268.79 | 433.09 | 125.82 | 450.31 | 99.51 | 99.61 | 121 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 767 | 767 | 0 |
| stop (spd2d < 1 u/s after release) | 801 | 790 | -11 |
| takeoff | 216 | 216 | 0 |
| land | 325 | 327 | +2 |
| apex step | 270 | 271 | +1 |
| peak speed step | 515 | 135 | -380 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.95 | 56.00 | +1.05 |
| takeoff v_z (u/s, state after takeoff step) | 282.09 | 284.68 | +2.58 |
| peak horizontal speed (u/s) | 299.14 | 199.53 | -99.62 |
| horizontal distance start→end (u) | 1413.06 | 937.75 | -475.31 |
| release→stop (steps) | 34 | 23 | |
| takeoff→land (steps) | 109 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 216, 326, 436, 546, 656 | 216, 436, 656 | 0, +110, +220 |
| land | 325, 384, 515, 610, 732 | 327, 546, 767 | +2, +162, +252 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 216/216 | 282.09 | 284.68 | +2.581 | 54.95 | 56.00 | +1.052 | 298.83 | 199.53 | -99.308 |
| 2 | 326/436 | 151.04 | 284.68 | +133.648 | 16.25 | 56.00 | +39.751 | 299.00 | 199.53 | -99.478 |
| 3 | 436/656 | 206.36 | 284.61 | +78.247 | 29.79 | 56.00 | +26.204 | 299.00 | 199.53 | -99.479 |
| 4 | 546/– | 169.20 | – | – | 20.27 | – | – | 299.00 | – | – |
| 5 | 656/– | 196.51 | – | – | 27.10 | – | – | 299.00 | – | – |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2869.862 | – | – | 7/0 |
| accel_mid (u/s²) | 516.934 | 450.000 | -66.934 | 17/63 |
| accel_sprint (u/s²) | 117.202 | – | – | 120/0 |
| decel_stand (u/s²) | 1248.865 | 1250.000 | +1.135 | 34/21 |

Flag mismatches (steps): grounded 188, sliding 0, sprinting 308, maxspeed 308/983.

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
