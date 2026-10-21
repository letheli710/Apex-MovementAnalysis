# R5 replay — M1_r42

Model `ReferenceMotor/m1-first-guess` (first guess, not tuned). Trial source `r5flowstate`, experiment `M1_loop`, 1225 steps aligned by cmd (5104..6328). Units: Source u, u/s; errors are sim − ref. M1 reports, it does not gate.

Parameters: maxspeed = speed 173.50 × moveScale 1.15 = 199.525 u/s; acceleration 450.00; deceleration 1250.00; airSpeed 60.00; airAcceleration 500.00; jumpHeight 56.00; g = 750.00 × 1.00 → v_jump 289.83 u/s.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 1225 | 32.28 | 34.59 | 32.27 | 34.59 | 23.16 | 288.43 | 20.06 | 126.40 | 2 |
| idle | 662 | 31.64 | 33.58 | 31.64 | 33.51 | 15.71 | 288.43 | 0.00 | 0.00 | 2 |
| accel | 22 | 8.97 | 16.18 | 8.97 | 16.18 | 109.96 | 125.94 | 109.96 | 125.94 | 0 |
| cruise | 410 | 33.68 | 34.59 | 33.63 | 34.59 | 23.53 | 126.40 | 23.53 | 126.40 | 0 |
| decel | 22 | 33.51 | 33.51 | 33.51 | 33.51 | 0.01 | 0.02 | 0.01 | 0.02 | 0 |
| air | 109 | 33.54 | 33.58 | 33.51 | 33.51 | 2.65 | 2.69 | 0.00 | 0.00 | 0 |

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
| apex height above floor (u) | 54.88 | 56.00 | +1.12 |
| takeoff v_z (u/s, state after takeoff step) | 282.01 | 284.62 | +2.60 |
| peak horizontal speed (u/s) | 199.53 | 199.53 | 0.00 |
| horizontal distance start→end (u) | 604.56 | 571.04 | -33.51 |
| release→stop (steps) | 22 | 22 | |
| takeoff→land (steps) | 109 | 111 | |

## Model choices (M1 guesses)

- Units: SOURCE (u, u/s); per-usercmd step with the recorded dt (dt / n_cmds sub-steps); double precision.
- Floor: flat plane at initial_state.pos.z; on ground z is pinned to it and v_z = 0.
- Wish: wishvel = cmd_fwd*F(yaw) + cmd_side*R(yaw), F=(cos,sin,0), R=(sin,-cos,0); wishspeed = speed*moveScale*min(|wishvel|,1).
- Ground: v_h += clamp_len(wishdir*wishspeed - v_h, rate*dt), rate = acceleration when wishspeed>0 else deceleration (vector approach, no separate friction, no lowSpeed/lowAcceleration branch).
- Jump: on the JUMP press edge while grounded, v_z = sqrt(2*sv_gravity*gravityScale*jumpHeight); no ground friction on that command; the air step runs on the same command.
- Air: half-step gravity (v_z -= g*dt/2; move; v_z -= g*dt/2); AirAccelerate with wishspd = min(wishspeed, airSpeed), accelspeed = min(airAcceleration*dt, wishspd - v_h.wishdir) (Phase 1 §3 [C] form, no *wishspeed).
- Land: after an air step, pos.z <= floor and v_z <= 0 -> snap to floor, v_z = 0, grounded.
- Not modelled: sprint, crouch/slide, lowSpeed/lowAcceleration, side/back speed scale, landSlowdown, skip_time/bhop penalties, collisions/slopes/steps.

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
