# M4b: grapple swing, steering, detach and release (Pathfinder), rounds 1 and 2

Status: offline analysis of three M4b swing sessions, plus the two M4 grapple sessions for the detach test and the envelopes. Round 2 adds the cross-swing session (tangential speed at attach). Nothing was launched. No game data and no file outside this folder was changed.

**Round 2 (current outputs in this folder):**
```
py -3 swing_analysis.py \
    --swing ../../data/20261021_022923_M4b_swing ../../data/20261021_023520_M4b_swing2 \
    --m4 ../../data/20261021_003330_M4_pathfinder ../../data/20261021_011119_M4_pathfinder2 \
    --cross ../../data/20261021_030659_M4b_swing3 \
    --json results.json --params params.json > analysis_output.txt
```
It runs for about 5–8 minutes; the open-loop model fits take most of that time.

**Round 1:** the same command without `--cross`. It reproduces the round-1 `analysis_output.txt`, `results.json` and `params.json` byte for byte (verified).

- `swing_analysis.py` computes every number in this file. It is stdlib only and has no local paths.
  - It imports the M4 `lg_load.py` wrapper and `lift_grapple_analysis.py` unchanged. The M2 join comes through them. Grapple events are detected by the unchanged M4 `grapple_events()`.
  - The first `--swing` folder must hold `report/census.csv`. The other M4b sessions ran with `--no-census`.
  - `--cross` (round 2) adds its trials to sections 1–7 and adds section 8 (cross analysis, model comparison, joint fit).
- `analysis_output.txt` is the console output. `results.json` holds the per-trial and per-group values. `params.json` lists each parameter with value, unit, source, n and spread; the `r2.*` keys are from round 2.

Labels: **[obs]** read from the client first-time MOVE-TRACE commands; **[fit]** a fitted formula with its residual; **[inf]** an interpretation the data support but do not prove.

## TL;DR (after round 2)

| Question | Answer |
|---|---|
| Rope constraint or acceleration? | **Neither a pendulum nor a pure central pull. The chosen model is RF (§7.3):**<br>- the speed **along the rope** ramps linearly (d v_r/dt = 494.5 ± 3.6 u/s² in cross, 494.5 ± 5.1 in walk, even with 300 u/s of cross speed);<br>- the speed **across the rope** is removed at a roughly **constant ~370–420 u/s²** (walk: −368 ± 4 u/s², linear down to 0).<br>Open-loop rms on the cross trials: RF 11.5 u, R1 (exponential damping) 15.9 u, pure acceleration F1 80.2 u, rope/pendulum RC 80.1 u. Speed **dips** (301 → 269, walk 205 → 186) before it grows; F1 and RC cannot produce a dip. [obs/fit] |
| One model for every anchor and initial speed | **RF, one parameter set, all 62 no-input trials:** along-rope ramp A = 541 u/s²; constant tangential deceleration C = 423 u/s²; s = 0.68 (gravity on the perpendicular part only); target = aim-ray hit + 32 u up.<br>Open-loop rms 11.8 u (horizontal 6.8 u); per condition 4.5–10 u, except p0 20 and cross 22. The same F1 joint fit gives 39 u.<br>Round 1 could not choose between F1 and R1. **RF is the simplest model the data support.** [fit] |
| Swing / tangential motion | Round 1 had none (the anchor was on the line of motion). With 200–300 u/s of cross speed (round 2), the cross speed is **braked, not swung**:<br>- walk: across-rope speed 197 → 0 in about 0.55 s, then stays at 0;<br>- sprint: 294 → 108 at 0.8 s, then it grows again as the player closes in. The path curves into the rope (lateral deviation 42–94 u from the start→anchor line). [obs] |
| Pull direction / anchor | **The world-fixed aim-ray hit at fire still holds.**<br>- Round 1: horizontal acceleration toward it to 0.01 ± 0.08°.<br>- Round 2, with lateral motion: a free lateral anchor shift fits to −20 u. An aim ray re-cast from the attach position would need +54 u, which is rejected. The open-loop gain from the shift is only 11.5 → 11.0 u.<br>The acceleration is no longer toward the anchor, because of the tangential brake. [fit] |
| Steering by view, no W | **Almost none:** +1.00 ± 0.05° heading for a 54° turn (round 1). [obs] |
| Steering with W | **Strong.** v·ŵ (velocity along the flat view forward) is **clamped at exactly 483.000 = 420·msc** (cross_w, 126 commands); v_h reaches 560 (cross_w) and 609 (turn_w). The M4 "v_h ≤ 483" is the special case where the view lies along the motion.<br>Before the clamp, a·ŵ is 645 ± 2 (cross_w), 584 ± 4 (turn_w) and 576 ± 0.2 (M4 fwd). In cross_w the sideways accel is −424 ± 1, the size of the tangential brake C. [obs] |
| Detach rule | **Unidentified after three rounds.** All 13 single-feature thresholds fail on the 79 trials; the best still mispredicts 28. The cross runs make it worse:<br>- cross_w releases at a 90 u 3D anchor distance;<br>- cross (no input) is still pulled at contact in 4 of 6 trials (gap 15–24 u);<br>- cross_walk releases early, at a 41–47 u gap (4–6 commands before impact), two of them past the wall's edge (y 6350–6355).<br>Envelope: release 2–6 commands (≈ 20–47 u) before the surface, or at contact. [obs] |
| Momentum after release | **Kept exactly** (69 releases): no boost or cut (0.003 u/s), then ballistic (g 750.1, v_h constant). [obs] |
| Jump release | **Does not exist in this build** (round 1). [obs] |
| Air control after release | **Not exercised** in either round. |

## Round 1

### Round-1 sections 0–5 (unchanged numbers; the round-2 rerun adds the cross trials to the output tables)

## 0. Data

| Session | Scored trials (ok, not warm-up) | Excluded |
|---|---|---|
| M4b_swing (census) | side 4, turn 5, turn_w 3, jump 5, turn_jump 5 | r90 warm-up (101 fps), r2501 side (99 fps), r2511 and r2512 turn_w (104 and 103 fps): runner frame-rate rule |
| M4b_swing2 (no census) | side 1, turn_w 3 | r90 warm-up, r2531 side (99 fps) |
| M4_pathfinder + M4_pathfinder2 | hold, jump, fwd, near, far, p0, p20: 5 each | none (as in M4) |

- **Setup.** Start (−14100, 6350, 294.92), yaw 20°, pitch −10° (10° up). The test wall face is at x ≈ −13706.
  - The aim ray from an assumed eye height of 60 hits the face at y = 6493.4, z ≈ 428.8. Hook length 425.7 u.
- **Joins.** Every command joins except the first of each trial.
  - "state_bad" frames (55–74 per trial) are the frames of the post-impact mantle. MOVE-TRACE logs no commands there (cmd gaps 1–2), as in M4.
- **Census (swing session 1).** airSpeed 60, airAcceleration 500, gravityScale 1, jumpHeight 56, climbEnabled true, wallrun false. This is the same Pathfinder census as in M4.
- **The dedi is authoritative.** During the pull, client and dedi post velocities differ by at most 0.21 u/s (mean of the per-trial maxima 0.11), and positions by at most 0.017 u. The client receives 1–13 prediction corrections per pull. The release command (or the contact command for turn_w) is the **same usercmd on both sides** in 26/26 trials. All numbers below are from the client and hold for the dedi to within these bounds.

## 1. Timeline (all 61 trials)

| Condition | n | Hook length (u) | Attach (s) | M4 prediction | Wind-up (s) | Pull (s) | End | Speed at end (u/s) | Gap (u) |
|---|---|---|---|---|---|---|---|---|---|
| m4b side | 5 | 425.7 | 0.215 | 0.214 | 0.202 | 1.167 | release | 633.0 | 32.9 |
| m4b turn | 5 | 425.7 | 0.217 | 0.214 | 0.202 | 1.167 | release | 631.3 | 33.8 |
| m4b turn_w | 6 | 425.7 | 0.214 | 0.214 | 0.203 | 0.750 | **contact** | 634.3 | 18.4 |
| m4b jump | 5 | 425.7 | 0.217 | 0.214 | 0.205 | 1.167 | release | 633.1 | 32.8 |
| m4b turn_jump | 5 | 425.7 | 0.216 | 0.214 | 0.203 | 1.167 | release | 631.6 | 33.7 |
| M4 hold / jump / fwd / near / far / p0 / p20 | 35 | 248–705 | as in M4 | | 0.200–0.202 | 0.75–1.55 | release | 474–804 | 26–41 |

The M4 hook model (0.0043 + L/2034.9) predicts the M4b attach to +0.0023 ± 0.0023 s, and the 0.20 s wind-up holds (0.203 ± 0.004 s). The 20° yaw changes nothing in the attach phase. [obs]

## 2. Q1: rope constraint or pure acceleration

### 2.1 Measured (no-input M4b trials without a turn: side and jump, n = 10)

| Quantity | Value | Label |
|---|---|---|
| Largest change of the 3D anchor distance between commands | −0.202 u (always decreasing) | obs |
| Tangential speed at pull start (the 200 u/s hop) | 45.7 u/s. Below 10 u/s after 9–12 commands (the 1660 u/s² burst of M4) | obs |
| After the burst: largest tangential speed / smallest v_r/\|v\| | 58–100 u/s / 0.987 (the tangential part is vertical, see 2.2) | obs |
| Largest lateral deviation from the start→anchor line | 0.33 u (0.09–0.56) | obs |
| Horizontal acceleration azimuth − rope azimuth (> 150 u from the anchor) | 0.006 ± 0.085° between trials, 0.03° within a trial | obs |
| Where those acceleration lines cross the face, minus the aim-ray hit y | 0.03 ± 0.45 u | obs |
| Speed law | \|v\| = 50.3 + 501.9·t (rms 0.36 u/s, max 1.5) | fit |

The same holds for all 30 no-input M4 trials (yaw 0): azimuth error −0.007 ± 0.096°, crossing at −0.03 ± 0.52 u.

### 2.2 Interpretation

- **No rope constraint is visible.** A rope only acts when the body would move away from the anchor. Here the radial velocity is inward and growing on every command. A constraint model and a pure pull model therefore give the same trajectory, and the data cannot separate them.
  - What the data do show: the initial perpendicular velocity (the hop) is **actively removed** within about 10 commands, so the motion is not a free pendulum. Speed then grows at a constant 500 u/s², independent of direction. [inf]
- **The effective target is the aim-ray hit horizontally.** It is not a point shifted along the wall normal and not the view direction. The turn trials (§3) separate the view from the anchor.
- **Vertically the velocity does not point at the hit.** Mid-pull it is 3.5° below the rope to the eye-height hit. On the last pulled command it is 6.8° above. This is the M4 "extra upward curvature". A fixed target height does not fit (M4 §2.5). This round adds no new vertical model.

### 2.3 Why there was no swing

- The test needed the anchor off the line of motion. Firing from rest along a 20° yaw puts the anchor on the line of motion: the hook travels along the view, and the pull starts from almost zero speed.
- The "side offset" was relative to the wall normal, not to the rope, so the pull runs straight along the 20° line (heading 19.99 ± 0.06° at release).
- **Tangential swing dynamics are therefore untested.** A test needs real tangential speed at attach. Two options:
  - fire while sprinting or strafing across the aim line (for example a 299 u/s strafe with yaw 90° to the motion);
  - aim at a high anchor and release W/A/D mid-pull.

## 3. Q2: steering

### 3.1 View turn without W (turn and turn_jump against side and jump, 10 against 10)

| At the first released command | No turn | Turn (view 20° → −33.7°) |
|---|---|---|
| Velocity heading | 19.99 ± 0.06° | **20.99 ± 0.05°** |
| \|v\| | 633.1 | 631.5 |
| vz / z | 215.5 / 421.5 | 203.6 / 425.1 |
| Pull duration | 1.167 s | 1.167 s |

- **The pull does not follow the view.** The anchor stays world-fixed: after a 54° turn, the release heading moves only 1°, and it moves in the **opposite** direction to the turn.
- The horizontal acceleration perpendicular to the rope is the small residual:
  - while turning at ~90°/s: −13.3 ± 3.4 u/s², toward the turn;
  - after the turn stops: +24 ± 11 u/s², away from it, growing roughly as 1/d (a_lat·d = 3233 ± 451 u²/s²).
- [inf] The post-turn part fits a rope whose player end sits about 7 u ahead of the origin along the flat view. That end rotates with the view. The opposite sign during the turn is not explained by that and remains open.

### 3.2 W held while turning (turn_w, n = 6)

| Quantity | turn_w | M4 fwd (W, view = rope azimuth) | No input |
|---|---|---|---|
| Accel along the flat view forward a·ŵ | **584.0 ± 3.5 u/s²** (576–589). The view is 0–54° off the rope azimuth, and up to 85° near the end | **576.2 ± 0.2** until v·ŵ = 483.000, then 0 | not constant: 548 → 415 with the view on the rope azimuth (side), 553 → 212 as the view turns away (turn) |
| Vertical accel | 187 ± 20 (163–231) | **231.0 ± 0.2, constant** | rises from about −180 to +340 along the pull |
| Speed ramp d\|v\|/dt | 633 | 608 (before the cap) | 502 |
| Max v_h / max v·ŵ | **609** / 464 | 483.000 / 483.000 | — |
| Heading at the end | 6.2° (view −33.7°) | 0° | 21° |
| Lateral path deviation from the rope line | 25 u | 0.3 u | 3 u |
| End | still pulled at wall contact, gap 18.4 u | released at gap 27.8 u | released at gap 33–34 u |

- **The M4 statement "W clamps v_h to 483" is wrong in general.** v_h reaches 609 here. The M4 number is v·ŵ, which equals v_h only when the view points along the motion.
  - A clamp on v·ŵ at 483 = 420·msc is consistent with both sessions. It was never reached in turn_w (max 464), so it is consistent but untested there.
- **The pull's own forward part does not add to W.** a·ŵ stays at 576–589 whatever the view–rope angle, while without W it falls with the view–rope angle.
  - [inf] W runs its own accelerate step along the flat view, at about 575–585 u/s² (≈ 500·msc = 575) up to v·ŵ = 483. The rope pull's component along ŵ is replaced, not added.
  - The side and vertical components with W follow no rule tested here (a fixed vertical 231 in M4 fwd, 163–231 in turn_w). **This part is unidentified.**

## 4. Q3: detach rule (all 61 M4 + M4b trials)

Each trial contributes its pulled commands (pre-state, from 10 commands after the pull start) and, if it released before contact, its first released command. A rule is "release at the first command where feature < T" (or > T).

| Feature | Released max | Pulled min | Best T | Mispredicted trials (of 61) | No input only (of 50) |
|---|---|---|---|---|---|
| gap to the face (pre-origin) | 40.6 | 17.6 | 35.9 | 20 | 9 |
| gap to the face (post-origin) | 34.2 | 15.4 | 31.3 | 18 | 7 |
| 3D distance to the aim-ray anchor (eye 60) | 60.9 | 36.0 | 36.8 | 15 | 15 |
| same, best of the eye 36–72 × body point 0–72 grid (eye 64, body 0) | 64.3 | 37.1 | — | 14 | — |
| horizontal distance to the anchor | 40.6 | 29.9 | 36.6 | 17 | 12 |
| time to face (gap − 16)/vx, time to anchor d/\|v\|, d/v_r | — | — | — | 25–26 | 16–21 |
| fraction of the initial rope length | 0.154 | 0.059 | 0.091 | 26 | 21 |
| time since pull start / since fire, speed, angle v–rope, rope elevation | — | — | — | 34–52 | 27–45 |

- **No single rule fits.** This is the third round (M4 tested static, look-ahead and 3D thresholds on 25 trials).
- The outliers are always the same:
  - **p0**: releases at a 58–61 u 3D distance; the anchor is 48 u above the body;
  - **far**: releases at a 40.6 u gap in 2/5 trials, near the top of the wall;
  - **p20**: releases late, at a 30.6 u gap;
  - **turn_w**: never releases; it is still pulled at contact with a 3D distance of 50–54 u.
- The release happens 2–4 commands before the wall impact in every released trial that has an impact command (49: 44 no-input + 5 fwd). The far trials and one p20 trial mantle without one.
  - [inf] The rule probably involves a trace against the geometry, for example a hull sweep along the velocity or toward the anchor, rather than a distance. That needs native code or a probe at a free-standing anchor (no wall behind the hit point).

**Envelope for Unity.** Release when the body is 30–40 u from the anchored surface (mean 34.1 ± 2.1 u, n = 50), that is about 2–4 physics steps before impact at 470–800 u/s. Keep pulling into contact when the player holds forward and the view is off the rope line (turn_w).

## 5. Q4: momentum at and after release

- **No boost and no cut.** Velocity is continuous across the release (0.005 u/s, max 0.11). The first released command is ballistic to 0.003 u/s (max 0.0095). [obs, n = 55]
- **After release.** Gravity is 750.08 ± 0.29, and v_h changes by at most 0.002 u/s per command until the wall impact (2–4 commands later). No input was held after a release in any trial, so **air control after release is not exercised**.
- **Speed at release** equals the speed law at the release time. The pull has no terminal speed.

| Condition | \|v\| at release | v_h | vz |
|---|---|---|---|
| m4b side / jump | 633.0 / 633.1 | 595 | 216 |
| m4b turn / turn_jump | 631.3 / 631.6 | 598 | 204 |
| M4 hold / near / far / p0 / p20 | 612.0 / 473.6 / 804.4 / 729.7 / 633.7 | 575 / 439 / 764 / 728 / 566 | 210 / 177 / 252 / 44 / 286 |
| M4 fwd (W) | 519.7 | 483.0 | 192 |

- **Wall impact.** vx drops to 6.0 ± 1.9. The wall-parallel vy is kept (change 0.05 ± 3.1 u/s). vz is 184 ± 53 after the impact. Then comes the wall climb and mantle of M3.
- **Jump release.**
  - jump vs side: max |Δv| after the press 2.4 ± 2.1 u/s, against 1.6 ± 0.5 within side.
  - turn_jump vs turn: 6.8, against 12.1 within turn.
  - M4 jump vs hold: 2.7, against 1.8.
  - Pull durations are identical (1.167 / 1.124 s), and the dedi received the jump bit (0x30000002).
  - **Jump does not release the grapple during the pull.** The "jump release" momentum question has no data, because the event never happens in this build. [obs]

## 6. Envelopes for a Unity "smooth and controllable" swing (updated after round 2)

**Chosen model (simplest that fits every anchor and initial speed): RF.** Per physics step, with r̂ the unit vector from the body origin to the target (the world-fixed aim-ray hit at fire, raised H):

```
v_r   = dot(v, r_hat)                    # along the rope
v_p   = v - v_r * r_hat                  # across the rope (3D)
v_p  += perp(-s * g * z_hat * dt)        # gravity on the perpendicular part only
v_p  *= max(0, |v_p| - C * dt) / |v_p|   # constant tangential brake
v_r  += A * dt                           # along-rope ramp, no cap
v     = v_r * r_hat + v_p
joint fit (62 no-input trials): A 541 u/s^2, C 423 u/s^2, s 0.68, H 32 u
cross-only fit (12 trials):     A 576,      C 420,      s 0.51, H 20
```

The A difference between the two fits trades off against H and s. The directly measured along-rope ramp is 494.5 u/s² against the eye-height hit (H = 0).

| Envelope | Observed | Use in Unity |
|---|---|---|
| Attach | t = 0.004 + L/2035 s (round 2: 0.0009 ± 0.0032 s error, n = 44), then a 0.20 s wind-up. A 200 u/s vertical hop at attach **also in the air**; the horizontal velocity is unchanged by the hop. | Copy |
| Along-rope speed | v_r grows linearly at ~495 u/s² from any start, with or without cross speed | RF ramp A; no terminal speed (804 u/s seen) |
| Cross speed | Removed at a constant ~370–420 u/s² (walk 368 ± 4 measured; RF C = 423). A 300 u/s sideways entry is braked within ~0.8 s; 200 u/s within ~0.55 s. It never swings past the rope line. | RF brake C. A *swing* feel would need a smaller C (design choice, no Apex reference) |
| Speed dip | \|v\| dips about 10 % (301 → 269 at 0.19 s; 205 → 186 at 0.13 s) before growing | Expected with RF; don't add a minimum-speed clamp |
| Direction | Target is the aim-ray hit at fire, world-fixed (±20 u laterally); 2–3 u lateral path error without cross speed, 10–12 u horizontal open-loop with it | Aim at the hit point; cache it at fire |
| Vertical | RF with s 0.68 and H 32: 3D open-loop 4.5–10 u for most conditions; p0 (horizontal aim) 20 u, cross 22 u | Accept; p0-like flat pulls are the worst case |
| View, no input | ≤ 1° effect | Ignore |
| W | Along the flat view: accelerate at ~575–645 u/s², hard clamp v·ŵ ≤ 483 = 420·msc; v_h can exceed 483 through the across-view part | Forward wish: accelerate along the flat view, clamp v·ŵ at 483, keep the RF rope terms for the rest (approximation [inf]) |
| Near-face boost | In the last ~120 u, a_z reaches +1400 u/s² (cross_w, M4 p0) | Optional; it is what lifts the player onto the ledge |
| Release | 2–6 steps before the surface (gap 15–47 u), or still pulled at contact; rule unidentified | Release on a short look-ahead (~0.03–0.05 s) against the anchored surface, or at contact; momentum kept exactly |
| After release | Fully ballistic; no jump release in Apex | Keep momentum |

## 7. Round 2: cross swing (`m4b_swing_cross*`, session M4b_swing3)

### 7.1 Setup and data

- **Schedule.** Start (−14100, 6050, 294.92), yaw 90, pitch −10, cl_yawspeed 700.
  - Sprint (cross, cross_w) or walk (cross_walk) along +Y for 1.0 s, then jump and release the move keys.
  - +right for 12 frames: the view turns to 18.7–24.4° at fire (mean per group); the velocity stays along +Y.
  - Then the grapple tap. cross_w holds W from the tap.
- **Data.** 18/18 trials scored, all at 120 fps. Client and dedi:
  - max |Δv| during the pull 0.24 u/s;
  - release/contact on the same usercmd in every trial.
- **State at fire.** |v_h| is 297 (sprint) or 199.5 (walk), heading 90°.
  - The attach matches the hook model (error −0.003 … +0.001 s).
  - **The 200 u/s hop is applied in the air as well.** vz is set to 200.00 on the attach command, and v_h is unchanged (0.000).

### 7.2 What the tangential component does (§8.2 of the output)

| t from pull start (s) | 0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
|---|---|---|---|---|---|---|
| cross: \|v\| | 301 | 269 | 302 | 377 | 476 | 603 |
| cross: v_r (along the rope) | 49 | 144 | 244 | 342 | 435 | 502 |
| cross: v_th (horizontal, across the rope) | 294 | 228 | 174 | 133 | 108 | 160 |
| walk: \|v\| | 205 | 191 | 255 | 351 | 450 | 550 |
| walk: v_th | 197 | 122 | 49 | 3 | 2 | 0 |

- **The along-rope speed ramps linearly** at 494.5 u/s² (sd 3.6 cross, 5.1 walk, over 0.1–0.6 s), independent of the cross speed.
  - A pure acceleration toward the anchor would add v_t²/d (up to ~220 u/s²) to that ramp. It is not there.
- **The across-rope speed falls linearly** in walk: −368 ± 4 u/s², down to about 0, where it stays.
  - That is a constant brake, not an exponential decay.
  - In cross the decay looks slower (−307 over 0.05–0.30 s), because the closing distance spins the rope (v_t·v_r/d is positive). The angular momentum |r × v| falls from 1207 to about 400 (×100 u²/s) and then stays roughly constant.
- **The speed therefore dips first, then grows.** This is the "296 → 270 → 425" seen on the dedi.

### 7.3 Model comparison (two rounds, open-loop position over the pull)

| Model | Parameters | Fit on cross + walk (12 trials): open-loop rms, 3D / horizontal | One-step rms | Simulated min\|v\| (observed 227 ± 44) | Joint fit, all 62 no-input trials |
|---|---|---|---|---|---|
| F1 pure acceleration toward the target + s·g | A, s, H | 80.2 / 79.8 u | 3.58 u/s | no dip (297 / 201) | 39.0 u (cross 92, walk 77, round-1 conditions 5.6–22) |
| RC rope / pendulum (tangential kept) | A, s, H | 80.1 / 79.8 u | 3.20 | no dip | not fitted (same as F1 on cross) |
| R1 exponential tangential damping (M4) | A, s, H, D | 15.9 / 14.8 u | 2.97 | 238 / 182 | — |
| **RF constant tangential brake** | A, s, H, C | **11.5 / 9.9 u** | **2.16** | 261 / 182 | **11.8 / 6.8 u** (round-1 conditions 4.5–10, far 10, p0 20, cross 22, walk 18) |

- **Choice: RF.** It is best on the new data in both rounds of fitting (one-step and open-loop). It is the only model that transfers with one parameter set to every anchor distance, pitch and entry speed (joint: A 541, C 423, s 0.68, H 32).
  - F1 and RC fail for the same reason: neither removes the cross speed.
  - R1 is second; the linear decay to zero in walk favours the constant brake.
- **Residuals that remain:** p0 at 20 u (the M4 downhill case) and cross at 22 u 3D. Most of the cross residual is vertical: 11.7 u horizontal.
- **Transfer of the cross-only fits to round 1** (no refit): RF 18.4 u 3D / 9.3 u horizontal; F1 38.2 / 34.2 u.

### 7.4 Anchor rule with lateral motion

- RF with a free lateral target shift dY gives dY = −20 u, and the open-loop rms only drops from 11.5 to 11.0 u.
- The player moved 53.8 u along +Y between fire and attach. An aim ray cast at attach (dY ≈ +54) is therefore rejected.
- **The target is the aim-ray hit at fire, world-fixed, to within about 20 u laterally.**

### 7.5 W in the cross case (cross_w)

Accelerations in the view frame (ŵ = flat view forward, 23°), more than 120 u from the face:

- **Before the clamp:**
  - a·ŵ = **645.2 ± 1.9 u/s²**;
  - sideways a = **−424.0 ± 0.8 u/s²**, constant while the sideways velocity changes sign. Its size equals the RF brake C, and it opposes the across-rope velocity, which stays at +130–160 [inf];
  - a_z = −161 ± 11.
- **Clamp.** **v·ŵ = 483.000 ± 0.000 from 0.36 s on (126 commands)**, while v_h grows to 560.
  - This confirms the clamp is on v·ŵ = 420·msc, not on v_h.
- **Near the face.** In the last 120 u, a_z reaches up to +1424 u/s² (the near-face lift, as in M4 p0).
- **Path.** The heading at release is 5.5° (cross: −12.9°). W keeps the player on the view side instead of letting the brake and pull settle onto the rope.
- **Release** at a 34–39 u gap, 3–4 commands before impact, |v| 559 ± 4.

### 7.6 Release and momentum (round 2)

| Condition | End | Gap (u) | 3D distance to the target (eye 60) | Commands to impact | \|v\| at release |
|---|---|---|---|---|---|
| cross | 4 contact / 2 release 1 cmd before | 15.5–23.6 | 65–69 | 0–1 | 701 (n = 2) |
| cross_w | release | 34.2–38.9 | 89–91 | 3–4 | 559 |
| cross_walk | release | 41.2–47.3 | 47–56 | 4–6 | 604 |

- **Detach.** With these trials the single-feature detach test (§4 of the output) mispredicts at least 28 of 79 trials, whatever the feature. Two of the walk releases happened at y 6350–6355, beyond the wall's traced edge (6380).
  - [inf] This hints at a geometry check (a trace at the anchor or along the path), not a distance.
- **Momentum.** Velocity is continuous and the first free command ballistic in all 69 releases (round 1 + 2).

## 8. Open questions

1. **The detach rule.** No distance, time, angle or look-ahead threshold fits 79 trials. Probe a free-standing anchor (thin pole) and an anchor near a wall edge.
2. **W law.** The v·ŵ clamp at 483 is confirmed. The forward accel is 576–645 u/s² depending on geometry, and the sideways part looks like the RF brake [inf]. A combined W model was not fitted.
3. **RF residuals.** p0 (flat aim, downhill pull) at 20 u and the cross vertical at 22 u. The vertical target height H and the gravity scale s trade off against A.
4. **Real swing** (anchor above and beside the player, a pendulum through the low point) remains untested. RF predicts the cross speed is braked away rather than swung.
5. **View coupling without W** (±13–24 u/s² lateral, sign flip), **air control after release**, and **jump after release** remain unexercised or unexplained.
