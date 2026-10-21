# M6-A3 ziplines: mount, ride, detach, jump-off, Super Jump

Status: offline analysis of one session (`20261021_150043_M6_A3_zip`: 120 fps, Gibraltar, empty-handed). Nothing was
launched and no data file was changed. One stdlib script produces every number in this folder:

```
cd research/phase2-local/m6/a3_zip
py -3 a3_zip_analysis.py ../../data/20261021_150043_M6_A3_zip > analysis_output.txt
```

The script writes `results.json` (per-trial measurements, fit tables) and `params.json` (the Unity model with evidence
labels) next to itself. You can pass several session folders, and `--json` / `--params` override the output paths.

Evidence labels:
- **[meas]**: measured here.
- **[fit]**: fitted here; the residual is given.
- **[src]**: source audit (`../SOURCE-AUDIT.md` §A3) or the session census.
- **[unknown]**: not determined.

## 0. Data, method, caveats

- **Trials.** 126 trials, all ok. One warm-up (r90, z0_off0) is skipped, which leaves 125 trials over 25 schedules,
  5 each.
- **MOVE-TRACE has a gap while the player is on the rope.**
  - The native MOVE-TRACE hook is not reached on zipline commands, on either side.
  - The client MT therefore has a gap from the mount command to the detach command, both included.
  - hsd_tel labels the post-gap MT rows as bursts (`b<n>`). The script assigns MT rows to trials by command range
    instead.
- **Ride data comes from HSD client frames.** The per-command record during the ride is the client HSD frame stream
  (one frame per usercmd at 120 fps: post-state origin, velocity, ground, view).
  - The client `[HSD-STATE]` logger did not compile. Zipline state is therefore inferred from motion, from the MT gap
    and from the SDK diag lines.
  - The diag lines are `[ZIPRAIL-USE]` (mount command, server Find point), `[ZIP-JUMPOFF]` (client and dedi jump-off
    velocity), `[ZIP-MOVESTOP]` (dedi detach command) and `[ZIP-DISC]` (budget).
- **Key edges.** They come from runner.json `sched_lines` and map onto HSD frames by time; there are 0 mismatches
  against the edge frame numbers.
- **IN_USE = 0x20** [meas]. All 25 failed use presses show buttons = 32 in MT. A successful press is never in MT,
  because the mount command is the first missing MT command (95/95).
- **Precision.** Origins in rows.csv are rounded to 6 significant digits, so x is known to 0.1 u. That gives about
  ±6 u/s of per-frame noise in a speed computed from positions; logged velocities are exact to 0.001.
- **Census.**
  - The `[CLASSVAR]` lines give `ziplineSpeed 600`, `ziplineDetachSpeed 600`,
    `ziplineMaxVerticalDetachSpeed 1500`, `ziplineViewOffset -16 -6 0`, `jumpHeight 56` and `gravityScale 1` [src].
  - They also give the ziprail values `ziprailAcceleration 150`, `ziprailDetachSpeed 450`, `maxJumpOffSpeed 550`,
    `minJumpOffSpeed 100` and `viewInfluenceOnJumpDirection 0.5`. These belong to S21 ziprails and do not apply to
    plain ropes; see §3.
  - The client reports `ziplinePreventManualDetach` and `ziprailMountReverseDistance` as unknown keys.
  - **The `find jump_grace / zipline / mantle_boost / lurch` census produced nothing.** The client forwards `find` to
    the dedi, which logs `Command 'find' doesn't exist`. `jump_graceperiod` and the other grace cvars stay
    [unknown].
- **Gravity.** Measured from 8196 free-flight frame pairs: **750.12 u/s²** (sd 0.33) [meas]. The census predicts the
  ground-jump speed √(2·g·56) = 289.85.

## 1. Mount (Q1)

| schedule | mounted (motion / client diag / dedi diag) | notes |
|---|---|---|
| z0_off0 | 5/5 / 5/5 / 5/5 | |
| z0_off40 | 5/5 / 5/5 / 5/5 | |
| z0_off80 | **0/5** | IN_USE seen in MT, no Find |
| z0_off120 | **0/5** | |
| z0_off160 | **0/5** | |
| z0_nouse (control) | 0/5 | no air frame, no MT gap, no diag event: **no auto-attach on touch** [meas] |
| z2_jump_pd30 (view +30 down) | **0/5** | the later jump is a ground jump |
| z7_air | **0/5** | see §5 |
| all other schedules | 5/5 each | |

- **Latency** [meas]. The mount happens on the use press command itself, so the latency is 0 commands.
  - The client diag mount command equals the first missing MT command in 95/95 trials.
  - The client and dedi `[ZIPRAIL-USE]` command numbers are equal.
  - The client HSD post-state of the press command already shows the mount.
- **Find point** [fit]. Define P = pre-use origin + (0,0,72) (the SDK `ZE_MOUNT_SEARCH_EYE_RAISE`) and the eye
  direction from the pre-use view.
  - **Rule:** the dedi's Find point Q is the rope point that minimises angle(eye, Q−P) within |Q−P| ≤ **130**.
  - Every flat or sloped-rope Find point matches this rule to within 0.1° and 0.1 u. At pitch 0 the eye ray is
    parallel to the rope, so the minimum-angle point lies on the 130 u sphere, 126.83 u ahead.

  | case | angle(eye, Q−P) | rule minimum | Q−P |
  |---|---|---|---|
  | off0 / z1 / z2 / z3 / z5 | 12.679° | 12.682° | 130.00 |
  | off40 | 22.074° | 22.074° | 129.92 |
  | pu30 | 0.012° (ray hit, 49.4 u ahead) | 0.088° | 57.05 |
  | z6_up | 27.038° | 27.059° | 129.97 |

  - **Cone half-angle bracket** [fit]: success up to 27.04° (z6_up), failure from 40.74° (off80, where the best point
    within 130 u is at 40.7°). So **27.0° < θmax < 40.7°**.
    - off120 (best point 71.5°) and pd30 (42.7°) fail consistently with this bracket.
    - off160 has no rope point within 130 u.
  - The audit's "radius 120" is the rail-candidate collector. The effective Find distance on plain ropes is 130 [fit].
  - **Vertical rope Z3:** Q sits at origin.z + 80.1, which is the hang height. The angle to the eye is 11.45°, so Q is
    not the minimum-angle point (that point would be at eye height, angle 0) [meas, one geometry].
- **Snap on the mount command** [meas]. Origin z +22.000 (sd 0, 95/95), no horizontal move. 316.39 is also the dedi's
  logged `mountStart`.
- **Blend to the rope** [meas/fit].
  - Model: position_k = p0 + b(k)·(ropeRef_k − p0).
  - ropeRef = Find point advanced by the rope speed, minus the hang offset.
  - Mean b(k) over 90 flat/uphill mounts (k = commands after the mount; the 4-row table below samples it):

    | k | 4 | 8 | 12 | 16 | 20 | 24 | 30 | 40 |
    |---|---|---|---|---|---|---|---|---|
    | b(k) | 0.157 | 0.465 | 0.746 | 0.907 | 0.969 | 0.985 | 0.990 | 0.995 |

  - The full table is in `params.json` → `attach.blend_table_b_of_k`. The trial-to-trial spread of b is ≤ 0.08 up
    to k=30.
  - Position RMS by blend model:

    | model | parameter | position RMS |
    |---|---|---|
    | table | – | **0.51 u** |
    | smoothstep | T = 0.148 s | 3.57 u |
    | critically damped | ω = 25.9 /s | 4.10 u |
    | exponential | – | 10.7 u |

  - **Use the table.** The 0.4 u tail is the reference itself (see the integration note below).
- **Hang position** [meas].

  | | below the rope | lateral |
  |---|---|---|
  | client (steady ride, 90 trials) | 80.172 u | y − rope y = −0.23 |
  | dedi (MT at exit) | 80.00 u | 0 |

  On Z3 the client sits at x +0.20 and y −0.23 from the rope.
- **View pitch is driven to the rope pitch on mount** [meas]. pu30 goes from −30 to 0, and z6_up from 0 to −10.62 (the
  rope slope). Both reach 90% after 22 commands. Consequence: the pitch variants of Q3 could not be tested; see §3.
- **Entry speed:** every mount started at rest. The first ride command logs |v| = 8.33 [meas].

## 2. Ride and auto-detach (Q2)

- **Speed profile** [meas]. It is the same on Z1 flat, Z2 uphill (along the rope) and Z3 vertical; the direction is
  exactly the rope direction (dir·v̂ = 1.0).

  | segment | acceleration | per-trial sd |
  |---|---|---|
  | first command | v1 = 8.33 | |
  | k = 2 … 60 (0.5 s) | **600.0 u/s²** | ≤ 14 (33.6 in z5_sj_k40) |
  | after the switch | **400.0 u/s²** | ≤ 0.2 |

  - The switch comes at k = 61, t = 0.508 s, v = 303.0–303.3.
  - The cap is **600 = ziplineSpeed**, reached at t = 1.243–1.257 s.
  - The switch coincides with the dedi state 2→3 transition. A jump on command 61 logs dedi `state=2` in 9 of 40 z5
    trials (those with ride v ≈ 303.0, one command earlier) and `state=3` in the other 31.
  - I model it as a 0.5 s mount state. A speed threshold of 300 is not excluded, because every mount started at rest
    [open].
- **No slope effect** on the uphill rope: the profile of |v| along the rope is identical [meas]. Downhill was not
  tested.
- **Position integration** [fit]: x_k = x_{k−1} + v_k·dt, using the same command's (post) speed.
  - The blend reference built this way has a tail error of 0.43 u at k = 40–60, against 1.69 u with the previous
    command's speed.
  - |Δorigin|/ft − v is +1.9 u/s with the same command's speed and +5.2 u/s with the previous one.
- **Auto-detach velocity** [meas, matches the SDK rule with residual 0].

  | rope | measured v_out | rule |
  |---|---|---|
  | Z1 flat (z0_off0, z0_off40, z1) | (600, 0, 0) on both client and dedi | d̂_end · clamp(v·d̂_end, 600, 600) |
  | Z2 uphill | (589.723, 0, 110.573) = 600·d̂, residual 0.0003 | same |
  | Z3 vertical | (400, 0, 600) on both sides | vertical part = ride velocity 600, below the 1500 clamp |

  - On Z3 there is **an extra 400 u/s horizontal push along +X**. +X is both the view yaw and the start→rope
    direction, so the cause is ambiguous [meas].
  - The position is clamped at the top end: origin = top − 80.16, with a last step of 4.12 u instead of 5.
- **Where the auto-detach happens** [fit].
  - The post-state of the detach command is 90.1–94.8 u from the end, for Z1 and Z2 alike. The SDK `ZIP-ALPHA`
    reports `stopShort = 90` (auto-detach 100 − eyeHullDiff 10).
  - Rule: after the ride step, if remaining − v·dt < 90, detach at the current position with v_out. The next command
    is ordinary air movement.
  - The client detach command equals the dedi `[ZIP-MOVESTOP]` command in 95/95 trials.
- **Client/dedi parity** [meas].
  - At the detach the dedi sits higher by dz = 0.163 (0 … 0.201) and by dy = +0.22 (0 … 0.23). This is the hang
    offset above; it disappears in only 4/95 exits.
  - Velocities are identical: |Δv| ≤ 0.001 over 30 commands after the exit.
  - The exception is z1_ride r2935 and z5_k4 r2986. There the dedi lands one command later because it is 0.17 u
    higher, which gives a |Δv| of 164 on that one command.

## 3. Jump-off and crouch-off (Q3)

All 70 manual exits (25 z2 jumps, 5 z3 crouch-offs, 40 z5 jumps; z2_jump_pd30 never mounted) have the same client and
dedi `[ZIP-JUMPOFF]` velocity (70/70), and the MT post-state equals the diag value.

| exit | ride v before | v_out (client MT = dedi) |
|---|---|---|
| jump, keys none/fwd/back/right, pu30 (25) | 420.1–424.5 | (400, 0, 289.828) |
| jump, z5 all K (40) | 302.2–303.5 | (v_ride, 0, 289.828), e.g. 303.335 → 303.335 |
| crouch (tap duck) (5) | 420.1–424.5 | (400, 0, 0) |

- **Model** [fit, residual 0.000 on all 70 exits]:

  ```
  v_out = ĥ_rope · min(v_ride, 400) + ẑ · (289.828 if jump else 0)
  ```

  - 289.828 = √(2·750·56): the ground jump speed from `jumpHeight 56` [meas+src].
  - A proportional law v_h = k·v_ride is rejected: k = 1.000 at 303 and 0.945 at 423.
  - **Only two ride-speed levels were sampled** (≈303 and ≈423). "min(·, 400)" is the simplest law through both
    [fit, 2 points]. The value 400 (= ⅔·ziplineSpeed?) has unknown provenance.
  - The ziprail jump-off clamp [100, 550] and cone −10/+26° do not show: plain ropes keep the native result, as the
    audit predicted.
- **Held keys do nothing on the jump command** [meas].
  - The dedi diag `flags` carry the buttons (0x2 jump, 0xa +fwd, 0x12 +back, 0x402 +right, 0x4 duck), yet v_out is
    identical.
  - From the next command on, the keys act through normal air control [meas]:
    - back: −4.17 per command along x, i.e. −500 u/s²;
    - right: −4.17 per command along y until |vy| = 69, the M2 wish cap (60 × 1.15);
    - forward: about 0, already beyond the cap.
- **The jump and crouch commands do not translate.** The post-state position equals the last ride position; flight
  starts on the next command [meas].
- **View pitch law: [unknown].** The mount drives the view to the rope pitch (§1), so pu30 jumped with pitch 0 and gave
  the same result. pd30 never mounted.
- **Direction** (rope vs view yaw): [unknown]. The yaw was always along the rope.
- **Crouch-off.** v_out = (400, 0, 0) at a ride speed of about 423 [fit, 1 level].
  - Tap duck leaves the player un-ducked: MT duck = 0 after the exit.
  - **Half-duck parity:** no divergence of half-hull size was observed.
    - At the crouch-off the dedi is higher by dz 0.158 — the same 0.15–0.17 hang offset as every other exit kind.
    - The duck was a 1-command tap released on the detach command, so the late-latch case (`bridge_halfduck_zip_parity
      0`) was **not exercised**. That needs duck held through and after the detach [open].

## 4. Super Jump (Q4)

| K (waitf) | second press after the jump-off | height above floor | applied? |
|---|---|---|---|
| 1 | +2 cmds (0.016 s) | 22.2 u | no (5/5) |
| 2 | +3 cmds | 24.6 u | no (5/5) |
| 3 | +4 cmds | 26.8 u | no (5/5) |
| 4 | +5 cmds | 28.0–29.1 u | no (5/5) |
| 6 | +7 cmds | 33.4 u | no (5/5) |
| 8 | +9 cmds | 37.5 u | no (5/5) |
| 12 | +13 cmds | 45.0 u | no (5/5) |
| 40 (control) | +41 cmds (0.34 s) | 74.8 u | no (5/5) |

- **The second jump never applies, 0/40** [meas].
  - The HSD frame logs in_jump = 1, and MT shows IN_JUMP with ground = 0.
  - vz follows gravity exactly: |Δvz − g·dt| ≤ 0.005, MT Δvz = −6.25 per command, and Δv_xy = 0.
  - Every second press is airborne. A zipline jump-off grants no grace/coyote jump and no double jump
    (`doubleJump false`, `superjumpLimit 1` in the census).
- **Landing** comes 99–101 commands after the jump-off. No trial takes off again after landing, so no buffered jump
  was seen.
- So with the community definition, Super Jump does not exist in this build for a press 1–41 commands after the
  jump-off. The variant that relies on a ground or grace jump right at landing (K ≈ 95–105) was not sampled [open].

## 5. Air grab (Q5)

- **z7_air: 0/5 mounts. There was no client or dedi `[ZIPRAIL-USE]` event at all**, so Find returned nothing.
- At the use press the player was:

  | quantity | value |
  |---|---|
  | origin | (−14550, 6613.4, 344.0), 49 u above the floor |
  | velocity | (0, 69.2, 92.7) |
  | distance from P to the rope | 187.8 u |
  | closest P-to-rope distance in the whole trial | 153 u |

- The standing jump from 200 u covered only about 15 u of the gap, so the press came far outside the ground range
  (40 u ok, 80 u fail). **Air mount itself is untested** [unknown]. The long-use (hold) path was not tried either.

## 6. Re-mount budget

- `[ZIP-DISC]` only logs the first trials: `consume left=2` and `reset ground left=3` on both sides, so each mount
  costs one charge and landing resets [meas].
- The +1 per 3 s and the refusal after 3 were not exercised: there was no Z4 schedule [src only].

## 7. Per-usercmd zipline model for Unity

Source units, dt = command frame time, g = 750.

```
ATTACH (on the IN_USE press edge, ground or air):
  P = origin + (0,0,72); e = eye dir
  flat/sloped rope: Q = argmin_Q angle(e, Q-P) over rope points with |Q-P| <= 130         [fit]
                    accept if angle <= theta_max, 27.0 < theta_max < 40.7 deg               [fit, bracket]
  vertical rope:    Q = rope point at origin.z + 80.1                                         [meas, 1 geometry]
  no attach on touch                                                                          [meas]
  re-mount budget 3 (+1 / 3 s, reset on landing)                                              [src]
  on the attach cmd: origin.z += 22 (no xy move), v_logged = 0; state = MOUNT (t = 0); s = param(Q)
  view pitch -> rope pitch (90 % in 22 cmds)                                                  [meas]

RIDE (each cmd while attached):
  v = 8.33 on the first ride cmd; then
  v += (t < 0.5 s ? 600 : 400) * dt ; v = min(v, ziplineSpeed=600)                           [meas]
  s += v * dt                                         (same-cmd speed)                        [fit]
  ropeRef = rope(s) - (0,0,80) (+ client-only 0.17 down / 0.23 -y)                            [meas]
  origin = p0 + b(k) * (ropeRef - p0) during the blend (table b(k), k = cmds since attach;
           b(40) = 0.995 -> treat as 1)                                                       [meas]
  slope: no gravity term (same |v| profile along the uphill rope)                             [meas, uphill only]
  velocity reported = v * rope dir

AUTO-DETACH (rope with autoDetach 100):
  after the ride step, if (L - s) - v*dt < 90: detach at the current origin,
     v_out = d_end * clamp(v.d_end, 600, 600)                                                [meas+src, resid 0]
  vertical rope (autoDetach 0): at the end (origin clamped to end - 80.16):
     v_out = d_end * min(v, 1500) + 400 * (view-yaw horizontal dir)                           [meas; push dir ambiguous]

JUMP-OFF (IN_JUMP press while attached, any state):
  origin unchanged on that cmd
  v_out = h_rope * min(v, 400) + z * sqrt(2 g jumpHeight)  (289.83)                          [fit, resid 0, 2 speeds]
  held move keys ignored on this cmd; normal air control (500 u/s^2, wish cap 69) from the next cmd  [meas]
CROUCH-OFF (IN_DUCK press while attached):
  origin unchanged; v_out = h_rope * min(v, 400), vz = 0                                     [fit, 1 speed]
SUPER JUMP: a jump press while airborne after a jump-off does nothing (K = 1..41 cmds)       [meas]
```

## 8. Open questions and suggested follow-ups

1. **Jump-off horizontal law at other ride speeds.** Only ≈303 and ≈423 were sampled. Jump at t = 0.15, 0.3, 0.65,
   0.75, 1.0 and 1.5 s after the mount (v ≈ 90, 180, 340, 380, 500, 600) to test min(v, 400) against a [lo, 400]
   clamp or a different curve.
2. **Jump-off direction and view influence.** Is the direction set by the rope or by the view yaw? Turn the view with
   `left`/`right`/`lookup`/`lookdown` during the ride; the mount only locks the view initially, and whether the player
   can re-aim was not tested. Also ride Z1 in reverse.
3. **Air grab.** Start ≤ 40 u from the rope, or use a running jump, then tap or hold use near the apex. Also test the
   long-use path.
4. **Find cone.** Sweep the view yaw or offset between 27° and 41° to pin θmax. Re-check the vertical-rope Find rule
   at another height or offset.
5. **Accel switch: time or speed?** Mount with an entry speed (running, falling or air mount). This also answers
   whether the incoming velocity carries into the ride.
6. **Downhill rope** (Z2 mounted at the high end) and a longer uphill: is there any slope term beyond the cap?
7. **Vertical exit push** of 400 horizontal: does it follow the view yaw or point away from the rope? Also the
   vertical jump-off and crouch-off.
8. **Half-duck parity.** Hold duck through the crouch-off for ≥ 10 commands. Today's tap released on the detach
   command, so it did not exercise the late-latch case.
9. **Budget / cooldown (Z4).** Not run. `[ZIP-DISC]` logging is rate-limited, so raise its limit or log mount refusals.
10. **Super Jump at landing.** Second press K ≈ 95–105 commands after the jump-off (around touchdown). Read
    `jump_graceperiod` with a client-side cvar read (EVAL `GetConVarFloat`), not `find` on the dedi.
11. **Client hang offset.** Why does the client hang 0.17 u lower and 0.23 u to −y than the dedi, with 4/95 exits
    showing no offset? It might come from ziplineViewOffset or a prediction correction; it is irrelevant for feel.
12. **The 400 constant** (jump-off cap, crouch-off and the vertical-exit push): no source reference found; it is native.
