# M6-A1 lurch stacking and tap strafe: model check

Status: offline analysis of two sessions. Nothing was launched, and no data or earlier analysis file was changed.
Everything in this folder is produced by one script:

```
cd research/phase2-local/m6/a1_lurch
py -3 a1_lurch_analysis.py ../../data/20261021_143512_M6_A1_lurch ../../data/20261021_143728_M6_A1_topup \
    --json results.json --params params.json > analysis_output.txt
```

- `a1_lurch_analysis.py` (stdlib only) computes every number below. It imports the M3 lurch code
  (`../../m3/lurch/lurch_analysis.py`), the M2 loader and join (`../../m2/air_jump/aj_load.py`) and `hsdtel`, and
  does not modify them.
- `analysis_output.txt` is its stdout. `results.json` holds every press row, the tap-strafe tracks, parity and
  closed-loop rows. `params.json` lists the parameters with source, n and spread.
- Section numbers like "out §3" refer to sections of `analysis_output.txt`.

Evidence labels: **[obs]** read from the logs; **[fit]** model compared with data, residuals given; **[inf]** an
interpretation the data are consistent with; **[src]** from SDK source; **[pred]** model prediction, not measured.

## TL;DR

**The M3 per-usercmd lurch model needs no change.** It predicts every one of the 395 press-edge commands in 17
conditions. Outside the fade, the error is at print precision (≤ 0.008 u/s). Inside the fade it is at most 0.32 u/s,
which is a 0.5 ms clock offset (§7). There are only two generalisations, and both were already implicit in M3:

1. **Every new press edge lurches again.** That covers the same key, the opposite key, a sequence and three in a row.
   Each press uses the same λ(t), with t counted from the jump. There is no per-jump budget, no diminishing and no
   cooldown, even for presses 2 commands (16.7 ms) apart. **The 209.3 u/s clamp applies to each press on its own,
   not to a running total.** One jump took three clamped presses: 627.9 u/s of total change.
2. **The window anchor is the latest jump command, and that includes the wall-bounce jump.** A bounce restarts
   the 0.2 s / 0.5 s window.

What follows from the model:

- **Tap strafe is the same rule, with W as the key.** A W press edge pulls v toward the current view yaw when the
  two differ. This answers M3 open question 4. Each W edge closes 70 % of the yaw–heading gap at constant speed.
- At 360 °/s, v turned 81.0° while the view turned 88.6°. At 180 °/s, 40.5° against 44.3°. Speed was kept
  (×1.0002), and the slide-jump entry at 350 u/s behaved the same.
- **Turn-only does not change the heading.** With W held, v turned only 3.1°, because AirAccelerate's 69 u/s wish
  cap blocks it.
- **A diagonal wish is the unit vector** of the two keys.
- **The client (native S21) and the dedi agree** to ≤ 0.005 u/s on every free-air command.

## 1. Data and method

| session | scored trials | notes |
|---|---|---|
| 20261021_143512_M6_A1_lurch | 79 | census present. Not scored: r90 (warmup); a1_rrr_n6 r2716–2720 and a1_lr_n12 r2722 (ok=false: frame rate under the gate, or the schedule over-ran) |
| 20261021_143728_M6_A1_topup | 8 | no census; a1_rrr_n6 ×6, a1_lr_n12 ×2; r90 warmup not scored |

- Trials per condition: 5 each, except a1_rrr_n6 = 6 and a1_lr_n12 = 6, both topped up. 120 fps, Gibraltar,
  empty-handed, movescale 1.15.
- Join: 35 438 of 35 525 client commands joined, with 0 state mismatches (M2 rule, validated per command).

**Per command [obs → fit].**
- An airborne command is one whose pre-state and post-state are both airborne and that is not a jump command.
- A **jump command** has an IN_JUMP press edge with a grounded or wall-contact pre-state and an airborne post-state.
  This picks up the ground jump, the slide jump and the wall-bounce jump. The wall climb before a bounce reports
  `ground=1`, so it is excluded from "airborne".
- A **press** is a command with a new bit in `buttons & 0x618` (FORWARD 0x8, BACK 0x10, MOVELEFT 0x200,
  MOVERIGHT 0x400). Every scheduled tap is one command long and carries ±0.5 on its axis.
- Each prediction starts from the observed pre-state, buttons, the command's own view yaw and dt:
  `v' = v + AirAccelerate(v)` (M2), then on a press `v' = lurch(v', wishdir, λ(t), 209.3)` (M3 §8).
- t = Σ dt from the start of the anchor jump command to the start of the press command.

**Alternatives** run through the same code (out §2):
- AirAccelerate only
- one lurch per jump
- one shared 209.3 budget per jump
- no clamp
- t counted from the first (ground) jump
- the previous frame's yaw
- a raw or sign key vector as the wish
- lurch before AirAccelerate

**Closed loop** (out §9): the model is integrated from each jump's post-state over the whole airborne segment
with no resets.

## 2. Residuals, every condition (out §2, §9)

Non-press airborne commands are predicted by M2 AirAccelerate alone. On those commands, the residual is at most
0.008 u/s in every condition except a1_turn_hold_w, which reaches 0.016. That is M2's known residual air gain
while input is held (M2 §3.1, about 1.4·10⁻⁵·vz² u/s²).

The table gives the maximum one-step error on press commands, in u/s:

| condition | n trials | presses | **M3 model** | AA only | once/jump | shared budget | no clamp | t from 1st jump | prev-frame yaw | raw keys | lurch before AA | closed-loop end err |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a1_rr_n6 | 5 | 10 | **0.006** | 209.3 | 141.0 | 141.0 | 115.4 | 0.006 | 0.006 | 33.9 | 3.52 | 0.012 |
| a1_rr_n12 | 5 | 10 | **0.005** | 209.3 | 141.7 | 141.7 | 116.3 | 0.005 | 0.005 | 34.1 | 3.64 | 0.010 |
| a1_rr_n24 | 5 | 10 | **0.322** (fade) | 209.3 | 128.0 | 128.0 | 115.5 | 0.322 | 0.322 | 36.0 | 3.52 | 0.324 |
| a1_rrr_n6 | 6 | 18 | **0.006** | 209.3 | 141.0 | 141.0 | 115.4 | 0.006 | 0.006 | 34.0 | 3.52 | 0.017 |
| a1_lr_n12 | 6 | 12 | **0.002** | 209.3 | 209.3 | 209.3 | 201.7 | 0.002 | 0.002 | 60.1 | 3.53 | 0.007 |
| a1_shift | 5 | 15 | **0.003** | 209.3 | 209.3 | 209.3 | 206.7 | 0.003 | 0.003 | 71.9 | 4.17 | 0.008 |
| a1_diag_fr | 5 | 5 | **0.006** | 163.3 | – | – | 0.006 | 0.006 | 0.006 | 18.7 | 0.006 | 0.014 |
| a1_diag_br | 5 | 5 | **0.002** | 209.3 | – | – | 275.6 | 0.002 | 0.002 | 24.3 | 0.84 | 0.010 |
| a1_ts_360 | 5 | 75 | **0.070** (fade) | 31.1 | 31.1 | 31.1 | 0.070 | 0.070 | 10.9 | 8.75 | 0.070 | 0.131 |
| a1_ts_180 | 5 | 75 | **0.042** (fade) | 15.6 | 15.6 | 0.89 | 0.042 | 0.042 | 5.53 | 4.37 | 0.042 | 0.098 |
| a1_ts_noturn | 5 | 75 | **0.007** | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.070 |
| a1_turn_only | 5 | 0 | – | – | – | – | – | – | – | – | – | 0.008 |
| a1_turn_hold_w | 5 | 0 | – | – | – | – | – | – | – | – | – | 0.278 (M2 held-input gain) |
| a1_sj_ts_360 | 5 | 75 | **0.084** (fade) | 37.2 | 37.2 | 36.8 | 0.084 | 0.084 | 12.9 | 10.3 | 0.084 | 0.144 |
| a1_wb_lurch3 | 5 | 5 | **0.002** | 209.3 | 0.002 | 0.002 | 65.3 | 196.2 | 0.002 | 31.2 | 3.48 | 0.142 |
| a1_wb_lurch30 | 5 | 5 | **0.300** (fade) | 209.3 | 0.300 | 0.300 | 19.4 | 209.3 | 0.300 | 66.1 | 3.84 | 0.300 |
| e6_bounce_none_15 | 5 | 0 | – | – | – | – | – | – | – | – | – | 0.142 |

Over all 395 presses, the M3 residual is mean 0.017, sd 0.037 and max 0.322 u/s. Every residual above 0.01 u/s
falls on a fade press (0.2 s < t < 0.5 s) and is explained by §7.

- The **63 clamped presses** have |D| = 209.3001 (sd 0.0014).
- **λ recovered on 220 full-strength presses** (t < 0.195 s, θ > 2°) is 0.70001 (sd 0.00003).
- **Unclamped presses** gain +0.0038 u/s of speed (sd 0.0019, n = 257), where the model predicts exactly 0. This is
  the same M2 held-input gain: the press command has input on it.

## 3. Stacking (question 1) [fit]

Per-press means over the trials are below (out §3, §4). t is measured from the jump. "k" is the press index
within the jump.

| condition | k | key | t (s) | θ (°) | s′ → s₁ | \|D\| obs | \|D\| model | clamped | λ obs | λ model |
|---|---|---|---|---|---|---|---|---|---|---|
| rr_n6 | 0 / 1 | R / R | 0.033 / 0.083 | 89.2 / 45.3 | 296.77→253.20 / 253.20→253.20 | 209.300 / 140.258 | 209.300 / 140.254 | 5/5 / 0/5 | 0.7000 / 0.7000 | 0.7 / 0.7 |
| rr_n12 | 0 / 1 | R / R | 0.034 / 0.133 | 89.2 / 45.4 | → 253.34 / kept | 209.300 / 140.400 | 209.300 / 140.396 | 5/5 / 0/5 | 0.7000 / 0.7000 | 0.7 / 0.7 |
| rr_n24 | 0 / 1 | R / R | 0.032 / 0.232 | 89.2 / 45.4 | → 253.20 / kept | 209.300 / 125.244 | 209.300 / 125.341 | 5/5 / 0/5 | 0.7000 / 0.6247 | 0.7 / 0.6252 |
| rrr_n6 | 0/1/2 | R R R | 0.033/0.083/0.133 | 89.2/45.3/13.2 | → 253.14, then kept | 209.300/140.192/40.770 | 209.300/140.187/40.768 | 6/6, 0/6, 0/6 | 0.7000 each | 0.7 each |
| lr_n12 | 0 / 1 | L / R | 0.033 / 0.133 | 89.2 / 134.0 | 296.78→253.20 / 250.29→143.13 | 209.300 / 209.300 | 209.300 / 209.300 | 6/6 / 6/6 | 0.7000 / 0.7000 | 0.7 / 0.7 |
| shift | 0/1/2 | R B L | 0.033/0.100/0.166 | 89.2/134.8/167.8 | 297.12→253.45→141.60→78.27 | 209.300 ×3 | 209.300 ×3 | 5/5 each | 0.7000 each | 0.7 each |

- **Every press edge lurches again.** Each one follows the single-press M3 law with its own t, and the
  mechanism has no memory of earlier presses.
- A second R press keeps pulling toward the same wish direction. With λ = 0.7 the 45° gap is still more than
  the clamp needs, but |D| = 140 < 209.3, so that press keeps speed exactly. A third press closes the remaining
  13.2° gap.
- **The clamp applies to each press.** lr_n12 has two clamped presses per jump, 418.6 u/s in total. shift has
  three, 627.9 u/s in total, and ends at 78 u/s. A shared per-jump budget or a once-per-jump rule fails by
  128–209 u/s.
- **No cooldown or diminishing.** Presses 6 commands (50 ms) apart and, in the tap-strafe runs, 2 commands
  (16.7 ms) apart all show λ = 0.7000 inside the plateau.
- In rr_n24 the second press falls in the fade (t = 0.232 s), and λ_obs is 0.6247 against a model 0.6252. That is
  the 0.5 ms offset of §7.
- The repeat spread of |D| on later presses (up to 3.8 u/s) comes from the 0–4 ms jitter in press timing, which
  moves the velocity heading at the second press. The model, fed the observed pre-state, still matches to
  0.006 u/s.

## 4. Tap strafe (question 2) [obs/fit]

Window = jump+4 … jump+33, the 15 W edges 2 commands apart (out §5).

| condition | n | view turn | velocity turn | final lag | speed start → end |
|---|---|---|---|---|---|
| a1_ts_360 (W taps, 360 °/s) | 5 | −88.56° | **−81.02°** | −7.54° | 296.89 → 296.95 (×1.00021) |
| a1_ts_180 (W taps, 180 °/s) | 5 | −44.30° | **−40.52°** | −3.77° | 296.76 → 296.83 (×1.00021) |
| a1_sj_ts_360 (slide jump, 350 u/s) | 5 | −88.53° | **−81.00°** | −7.53° | 350.01 → 350.05 (×1.00012) |
| a1_ts_noturn (W taps, no turn) | 5 | 0 | 0.00° | 0 | ×1.00021 |
| a1_turn_only (turn, no keys) | 5 | −88.52° | **0.00°** | −88.52° | ×1.00000 |
| a1_turn_hold_w (turn, W held) | 5 | −87.70° | **−3.13°** | −84.56° | 297.33 → 299.76 (×1.008) |

**Each W edge redirects v toward the current view.** This resolves M3 Q4: IN_FORWARD is a lurch press like the
other three. When v already points along the view, the press does nothing, as in M3's W re-tap and in ts_noturn
(|D| ≤ 0.007).

Per edge, the gap between yaw and heading drops to 0.30 of its size, because λ = 0.7 at constant speed:

- **At 360 °/s.** The gaps go −1.50→−0.45, −6.47→−1.94, then settle at −8.57→−2.57. This is the steady state
  g = Δ/0.7 for a turn of Δ = 6° between edges.
- **At 180 °/s.** The gaps settle at −4.29→−1.29.
- **In the fade** (t > 0.2 s). λ_obs follows the M3 ramp (0.699, 0.660, 0.621, 0.582, 0.543), so the lag grows
  toward −9.9°.

**Speed is kept.** Every tap-strafe press was unclamped, with |D| ≤ 31.1 u/s at 297 and ≤ 37.2 at 350. The only
gain is the +0.004 u/s per press from M2's held-input gain.

**Controls.**
- **Turn only.** The heading does not change. Air control needs a wish input.
- **Turn with W held.** This is plain AirAccelerate with the 60·1.15 = 69 u/s wish cap, so it can only add
  velocity along the wish once v·wish < 69, that is, once the gap exceeds about 76.5°. Over 0.25 s v turned 3.1°
  (almost all in the last 3 commands) and gained 2.4 u/s. **Tap strafe is the lurch, not air strafing.**

**Clamp scaling at slide-jump speed.** The 350 u/s entry did not exercise the clamp: |D| was at most 37 u/s.
**This data cannot tell whether the clamp scales with entry speed.** M4 showed it scales with the sprint cap.

**Total redirect achievable [pred].** The measured window is only 0.033–0.267 s. With the same model, keeping 60 Hz
W edges and turning until 0.5 s gives (out §10):

| turn rate | v turn by 0.267 s | v turn by 0.5 s | speed at 0.5 s (297 entry) |
|---|---|---|---|
| 90 °/s | −20.3° | −33.3° | 297.0 |
| 180 °/s | −40.5° (measured −40.5°) | −66.6° | 297.0 |
| 360 °/s | −81.0° (measured −81.0°) | −133.0° | 297.0 |
| 720 °/s | −162.0° | −264.3° | 297.0 |
| 1440 °/s | −324.1° | −515.6° | 286.8 |

- At about 2880 °/s the step between edges (48°) passes what the clamp allows: 2·asin(209.3 / 2s) = 41.3° per
  press at 297 u/s and 34.8° at 350. At that point presses are clamped and speed falls (to 224 at 297 entry).
- Below about 1500 °/s at 60 Hz edges, the redirect is limited only by how fast the view turns and by the fade.
  The rows above 360 °/s are **untested**.

## 5. Diagonals (question 3) [fit]

Each diagonal press puts fwd ±0.5 and side 0.5 on one command (out §6).

| condition | θ | s′ → s₁ | \|D\| obs | heading after | M3 (unit wishdir) | raw key vector | sign key vector |
|---|---|---|---|---|---|---|---|
| diag_fr (W+D) | 45.00° | 296.78 → 296.78 | 163.149 (unclamped) | −31.91° | **0.006** | 18.7 | 16.0 |
| diag_br (S+D) | 134.43° | 293.99 → 170.10 | 209.300 (clamped) | −44.89° | **0.002** | 24.3 | 15.1 |

- **The wish direction is normalized**, using the unit vector of fwd·forward + side·right. A key vector with
  magnitude 0.707 (raw half values) or 1.414 (signs) is rejected by 15–24 u/s.
- θ = 45° from W+D at an exact 45° confirms equal weighting of the two axes.
- Lurch before AirAccelerate is rejected again, by 0.84 u/s for diag_br.

## 6. Wall bounce (question 4) [fit]

- **Geometry.** The bounce jump is the jump press during the wall climb. It comes 0.434–0.450 s after the ground
  jump, at command 53 in every trial.
- **lurch3.** The press 3 commands after the bounce has t = 0.025 s from the bounce, where λ = 0.700. Measured
  from the ground jump, t = 0.467 s and λ = 0.076.
  - Observed: s 252.59 → 223.92 and |D| = 209.30, which is clamped.
  - Error with t from the bounce: **0.000–0.002 u/s**. With t from the ground jump: **191.5–196.2 u/s**.
- **lurch30.** t = 0.250 s from the bounce, where λ = 0.583. From the ground jump, t = 0.692 s and λ = 0.
  - Observed: a clamped lurch, s 252.6 → 244.9.
  - Error with t from the bounce: **0.22–0.30 u/s**, the fade offset of §7. With t from the ground jump:
    **209.3 u/s**, because that model predicts no lurch at all.
- **e6_bounce_none_15**, the control, has no press edge in the air and needs no lurch. Its closed-loop error is
  0.142 u/s.

**The wall-bounce jump restarts the lurch window [fit].** The simplest rule that fits every condition is "t from
the latest jump command". The data cannot tell whether the anchor is the jump press or the take-off, because they
happen on the same command for the ground, slide and bounce jumps alike.

## 7. Window edge: a 0.5 ms clock offset [fit]

On the 70 fade presses (0.01 < λ_obs < 0.69), the t implied by λ_obs is later than the measured t:

- Against the Σdt clock: **+0.475 ms** (sd 0.134).
- Against the client frame-time clock: +0.624 ms (sd 0.181).
- By condition: ts_360 +0.48, ts_180 +0.49, sj_ts_360 +0.51, wb_lurch30 +0.53, rr_n24 +0.21 ms.

Shifting t by the mean cuts |λ_obs − λ_model| from 0.00112 to 0.00021. M3 found the same sign at 120 fps
(+0.74 ms) and placed the edges at ±1 ms, so **the model is not changed**.

- This offset is the whole source of the 0.04–0.32 u/s fade residuals.
- It is far below anything a player can feel. For Unity it does not matter.
- It cannot be told apart from the client clock printing (M2 noted that the dedi event clock is cleaner than
  client Σdt).

## 8. Client vs dedi parity (question 5) [obs]

The table compares the same usercmd on the dedi MOVE-TRACE and on the client, as the maximum difference over the
12 pre/post fields (out §8). Commands where one side made contact on a different command are left out. There was
one such command: r2771, where the dedi landed one command earlier.

| conditions | free-air max | press max | velocity max (vx vy pvx pvy) |
|---|---|---|---|
| rr_n6/n12, rrr_n6, lr_n12, shift, diag_fr/br, ts_noturn, turn_only, turn_hold_w | ≤ 0.001 | ≤ 0.001 | ≤ 0.001 |
| rr_n24, ts_360, ts_180, sj_ts_360 | 0.002–0.005 | 0.002–0.005 (fade presses) | ≤ 0.005 |
| wb_lurch3, wb_lurch30, e6_bounce_none_15 | 0.020–0.040 (z only) | 0.020–0.040 (z) | ≤ 0.001 |

- **The lurch on the dedi matches the native client** to ≤ 0.005 u/s in every condition, including stacked, back,
  diagonal, tap-strafe and post-bounce presses.
- The few-thousandths differences sit on fade presses only. They are the same clock-level effect as M3 r1033.
- In the wall trials the dedi and client positions differ by 0.01–0.04 u in z after the wall climb, while the
  velocities stay identical. In one trial (r2771) this moved the landing one command earlier on the dedi. That is
  a climb or contact effect, not a lurch effect.
- The dedi model residual on press commands (the model applied to the dedi pre-state) is ≤ 0.007 u/s outside
  the fade.

**[src] correction to the task brief.** `s21-r5sdk/src/game/server/tapstrafe.cpp` does not reimplement the lurch.
Its header says "suppression on dedi's native inline lurch". It wraps the native `CGameMovement::AirMove` and only
masks the 0x618 bits of `m_nButtonsPressed` in three cases:
- mantle boost
- gravity-cannon flight
- horizontal speed above `bridge_lurch_cutoff_speed` (1100, mirroring the client's `jump_grace_cutoff_speed`)

None of these cases came up here, so the dedi ran its native lurch, which explains the bit-level parity.

## 9. Generalized per-usercmd model (chosen; unchanged from M3 §8, two rules made explicit)

```
# state: lurchAnchorTime = curtime at the start of the latest jump command
#        (ground jump, slide jump, wall-bounce jump: every jump sets it)
# per usercmd, inside AirMove, after M2 AirAccelerate (500*dt, wish cap 60*movescale):
pressed = buttons & ~prevButtons & (FORWARD|BACK|MOVELEFT|MOVERIGHT)      # 0x618
if airborne and pressed and |wish| > 0 and |v_xy| > 0:
    wishdir = normalize(fwd*forward(yaw) + side*right(yaw))   # this command's view yaw; magnitude ignored
    t   = curtime_at_cmd_start - lurchAnchorTime
    lam = 0.7 * clamp01((0.5 - t) / 0.3)
    if lam > 0:
        d = normalize((1 - lam)*normalize(v_xy) + lam*wishdir)  # skip if zero (lam = 0.5, wish = -v)
        D = |v_xy| * d - v_xy
        if |D| > 209.3: D *= 209.3 / |D|        # per press; no per-jump budget, no cooldown
        v_xy += D
```

| parameter | value | source |
|---|---|---|
| λ_max | 0.7 | M3; A1 0.70001 (sd 0.00003, n = 220) |
| window | full until 0.2 s, linear to 0 at 0.5 s, from the start of the latest jump command | M3 ±1 ms; A1 fade +0.5 ms (§7) |
| clamp | 209.3 u/s per press = 0.7 × sprint cap (299 at movescale 1.15) | M3, M4; A1 209.3001 (sd 0.0014, n = 63) |
| press gate | new bits in 0x618, every edge | A1 §3, §4 |
| wishdir | unit vector of the command's keys at the command's own yaw | A1 §5; prev-frame yaw rejected by 5.5–12.9 u/s |
| order | AirAccelerate, then lurch | M3; A1 (3.5 u/s worse the other way) |

**Residuals of this model.** Outside the fade, ≤ 0.008 u/s per command. In the fade, ≤ 0.32 u/s. Closed loop
over a whole airborne segment, ≤ 0.32 u/s.

## 10. What Unity must implement

1. **Edge detection on every command.** Use `pressed = buttons & ~prevButtons` for the four movement keys, and
   run the lurch on **every** edge while airborne. There is no counter, budget or cooldown. **Tap strafe and lurch
   stacking then come out of the same code with no special cases.** Do not gate W out: a W edge lurches toward
   the view.
2. **Taps must reach the movement step as edges.** A scroll-wheel bound to +forward, or a quick re-press, has to
   produce a press on its own command with a release in between. In the data, edges 2 commands apart (60 Hz at
   120 fps) all lurched at full strength. The input layer must not merge or debounce them, and must not drop a
   one-command tap.
3. **Use a unit wishdir from the current command's view yaw.** Two keys give a 45° unit direction, and key
   magnitude (0.5 vs 1) does not matter.
4. **Reset the anchor on every jump**, including the wall-bounce jump and the slide jump. Keep the window in
   seconds, not frames.
5. **Clamp each press at 0.7 × the current sprint cap** (209.3 at 299). The clamp is what makes stacked opposite
   presses act as hard brakes (shift: 297 → 78 u/s).
6. **Keep AirAccelerate (M2) separate and first.** Turning with W held must stay weak, because of the 69 u/s cap.
   That contrast is what makes tap strafing worth learning.
7. Optional, untested: suppress the lurch above 1100 u/s horizontal speed and during mantle boost [src].

## 11. Open questions / not tested

- **Clamp at higher entry speed.** No tap-strafe press was clamped, and the clamped presses ran at speeds of
  137–297 u/s only. Whether the clamp scales with entry speed (slide jump at 350) is untested here. M4 tied it to
  the sprint cap.
- **Fast turns.** The predictions above 360 °/s, including where the clamp starts to bind (around 2900 °/s at
  60 Hz edges), are not measured.
- **Fade on long tap strafes.** No tap-strafe edge was later than 0.267 s, so the ramp is checked only at
  0.20–0.27 s here. M3 covers 0.2–0.5 s with single presses.
- **Jump press or take-off as the anchor.** These cannot be separated, because they are always the same command.
  Lurch after a walk-off ledge, with no jump, is still untested (M3 Q7).
- **Cutoff speed 1100, mantle-boost suppression, gravity cannon.** None were exercised.
- **Window clock.** The +0.5 ms offset (§7) is unexplained. It could be client-clock printing or an edge just
  past 0.5 s.
- **Held-input residual.** The +0.004 u/s per press and up to 0.016 u/s per command with W held come from M2's
  residual air gain, which remains unmodelled. They are negligible.
- **Replay path.** Client replay rows (rp=1) were not examined, so replay parity is untested.
