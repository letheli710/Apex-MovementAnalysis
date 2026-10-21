# M3 E3 lurch (tap-strafe): model

Status: offline analysis of five sessions. Nothing was launched, and no existing file was changed. The script,
its output and the parameters are in this folder:

```
python lurch_analysis.py <session> [<session> ...] [--json results.json]
python lurch_analysis.py ../../data/20261020_220752_M3_lurch_chain ../../data/20261020_215746_M3_pilot \
    ../../data/20261020_223838_M3_fps120 ../../data/20261020_224455_M3_fps120_rerun ../../data/20261020_225255_M3_fps60 \
    --json results.json
```

- `lurch_analysis.py` computes every number in this file. It reuses the M2 loader and frame join
  (`../../m2/air_jump/aj_load.py`). Its output is in `analysis_output.txt`, and its per-press rows are in
  `results.json`.
- `params.json` lists the parameters with their source, n and spread.

Evidence labels: **[obs]** read directly from the logs; **[fit]** fitted, with residuals given; **[inf]** an
interpretation the data is consistent with but does not prove; **[src]** from phase-1 notes or SDK source.

## TL;DR

On the one command that has a direction-key press edge, after AirAccelerate, the game moves the horizontal
velocity toward a **lerp of the velocity direction and the wish direction**. The speed is kept, and the change
is clamped to **209.3 u/s**:

```
lam  = 0.7 * clamp((0.5 - t) / 0.3, 0, 1)        t = seconds since the start of the jump command
d    = normalize((1 - lam) * vhat + lam * wishdir)
D    = |v| * d - v ;  if |D| > 209.3: D *= 209.3 / |D|
v   += D
```

- The window is defined **in time**, not in frames. It is full strength until 0.200 s and fades linearly to
  0 at 0.500 s, at 60, 120 and 144 fps alike.
- v₁ = a·v₀ + b·|v₀|·wishdir with constant a and b does **not** hold. a and b change with speed, and the form
  fails for back and W presses.
- Back **does** lurch. It is a straight 209.3 u/s brake with no heading change. A W re-tap does nothing
  because the wish direction is already the velocity direction.
- The S3 dedi computes the same lurch natively, and it matches in 101 of 102 trials.

## 1. Data and method

**Trials.** All e3_* trials with ok=true and warmup=false, Gibraltar, movescale 1.15: 102 trials, each with
one press event.

| session | fps | trials | schedules |
|---|---|---|---|
| M3_lurch_chain | 144 | 51 | right_k1–k90 (2–3 each), back_k3/12/35, wtap_k3/12/35, right_walk_k5, right_slide350_k5 |
| M3_pilot | 144 | 20 | the same set, one each, without k40/45/55/60/65 |
| M3_fps120 | 120 | 6 | right_k2/4/7/10/15/21 (the other trials failed the fps gate and are not used) |
| M3_fps120_rerun | 120 | 10 | right_k1/29/33/38/42/46/50/54/58/75 |
| M3_fps60 | 60 | 15 | right_k1–k38 |

The join of commands to frames uses the M2 rule. 41 335 of 41 437 commands joined, with 0 state mismatches.
The unjoined commands are the first commands of each trial.

**Events [obs].**
- Jump command j: the pre-state is on the ground and post vz > 50. The jump press is on this command, and
  take-off happens on it too.
- Press command p: the first later command with a new bit in 0x618.
- On every press command the pressed axis has |fwd| or |sidemove| = 0.5, which is the half-frame key state.
  W and sprint are released on the same command (right and back schedules).

**Lurch term.** The pre-lurch velocity is v′ = v₀ + AirAccelerate(v₀), using the M2 model with no free
parameters. The lurch is D = v₁ − v′, written in the frame (v̂′, n), where n is the normal on the wish side.
The angle θ is between v′ and wishdir. It is 88.4–89.4° for the right presses: AirAccelerate has already
turned v′ by 0.6–1.6°. It is 180° for back and 0° for W.

**Time.** t = Σ dt from the jump command up to, but not including, the press command. That is the clock at
the start of the press command minus the clock at the start of the jump command. The client frame `t` field
gives the same value within 0.5 ms.

## 2. One command only [obs]

The lurch acts on the press command alone.
- On the other 9 666 airborne commands of the 102 jumps, the largest gap between the observed velocity and the
  M2 AirAccelerate prediction is **0.033 u/s**.
- On the press command, |D| ranges from 0 to 209.3 u/s.
- The press command's vz follows gravity: (vz − pvz) − 750·dt lies between −0.005 and +0.011. The lurch is
  horizontal only.
- Holding the key after the press adds nothing beyond AirAccelerate.

## 3. The lurch formula (task 1)

### 3.1 Early presses (t < 0.20 s) [obs]

| condition | n | θ (°) | s₀ = \|v′\| | s₁ | D∥ | D⊥ | **\|D\|** | heading | a (user) | b (user) |
|---|---|---|---|---|---|---|---|---|---|---|
| sprint right 144 fps | 23 | 89.33 | 296.76 | 252.98 | −114.36 | 175.30 | **209.300** | −43.86° | 0.6147 | 0.5907 |
| sprint right 120 fps | 7 | 89.19 | 296.67 | 253.12 | −114.18 | 175.41 | **209.300** | −43.87° | 0.6151 | 0.5913 |
| sprint right 60 fps | 6 | 88.40 | 299.19 | 256.14 | −113.16 | 176.07 | **209.300** | −43.42° | 0.6218 | 0.5885 |
| walk right | 4 | 89.00 | 199.61 | 195.36 | −113.94 | 175.57 | **209.301** | −63.99° | 0.4292 | 0.8796 |
| slide right | 4 | 89.43 | 350.05 | 293.58 | −114.48 | 175.21 | **209.298** | −36.64° | 0.6729 | 0.5005 |
| back | 6 | 180 | 293.13 | 83.83 | −209.30 | 0.000 | **209.300** | 0.00° | – | – |
| W re-tap | 6 | 0 | 297.01 | 297.01 | 0.005 | 0.000 | 0.005 | 0.00° | – | – |

- The change D has the **same length, 209.300 u/s, at every speed and in the back case**. Over all 61 presses
  whose speed dropped, it is 209.3001 (sd 0.0016). A length that does not depend on speed or angle is a clamp.
- The "slide ~458" condition reaches the press at **350.05 u/s**. The slide decays from 460, and the slide
  jump command sets the horizontal speed to 350.00, which is census slideMaxJumpSpeed [obs].
- **The user's form v₁ = a·v₀ + b·|v₀|·wishdir with constant a, b is rejected.** a runs from 0.43 to 0.67 and
  b from 0.50 to 0.88 as the speed goes from 200 to 350. With a+b > 1, the same form would also speed up a W
  press, and for back it would leave about 6 u/s instead of 84.

### 3.2 Recovering the target [fit]

When D is clamped, the target T lies on the circle |T| = |v′| along D, so T is v′ reflected about the normal
of D. When D is not clamped, the speed is kept exactly (s₁/s₀ = 1.0000), and T = v₁. Solving
(1−λ)·v̂′ + λ·wishdir ∥ T for λ gives:

- **λ = 0.70000** (sd 0.000003, range 0.69999–0.70001, n = 44) on all early sideways presses. That covers
  walk, sprint and slide, 60/120/144 fps, and θ from 88.40° to 89.43°.
- A rotation by a fixed fraction of θ (a slerp) needs f = 0.7405–0.7416, which drifts with θ. The lerp weight
  does not drift.

### 3.3 Model comparison on early presses [fit]

Parameters are taken from "sprint right 144 fps" and applied to every condition. The table gives the maximum
|v₁,pred − v₁,obs| in u/s.

| model | W re-tap | back | slide | sprint 120 | sprint 144 | sprint 60 | walk |
|---|---|---|---|---|---|---|---|
| M0 AirAccelerate only (M2) | 0.006 | 209.3 | 209.3 | 209.3 | 209.3 | 209.3 | 209.3 |
| M1 v₁ = a·v′ + b·\|v′\|·w (a 0.6147, b 0.5907) | 61.1 | 77.8 | 36.5 | 2.63 | 2.57 | 2.87 | 69.7 |
| **M2 lerp λ 0.7 + clamp 209.3** | **0.006** | **0.002** | **0.002** | **0.002** | **0.002** | **0.002** | **0.002** |
| M3 slerp f 0.7415 + clamp 209.3 | 0.006 | 84.4 | 0.020 | 0.027 | 0.004 | 0.167 | 0.061 |
| M2b as M2, lurch before AirAccelerate | 0.006 | 0.002 | 3.00 | 3.58 | 3.04 | 7.04 | 2.92 |

Notes on the table:
- M2 reaches print precision in every condition with two numbers, λ = 0.7 and L = 209.3.
- The slerp fails for back: rotating by f·180° would change the heading, and the observed heading change is
  exactly 0.
- Applying AirAccelerate after the lurch fails, so the order is **AirAccelerate first, then the lurch**. This
  agrees with the hook location: the lurch lives inside AirMove [src].

**Speed dependence [fit]: none in λ or L.** The speed dependence that shows up in a, b and the heading comes
only from the clamp. A sideways press with λ = 0.7 asks for a 66.8° turn at constant speed, which is
|T − v| = 1.101·|v|. That is clamped once |v| > 190.1 u/s. In practice:
- Walk speed (199.6) is barely clamped. It turns 64° and loses 2 % of its speed.
- Sprint (297) turns 44° and keeps ×0.852 of its speed.
- Slide-jump speed (350) turns 37° and keeps ×0.839.

**Angle dependence.** Only θ ≈ 0°, 89° and 180° were tested. The model explains all three without a special
case (§5). Intermediate angles, such as a diagonal press, are a prediction and not yet a measurement.

**Movescale.** It was 1.15 in every trial, so it is **not determined** whether L scales with it.
209.3 = 0.7·299 = 0.7·260·1.15 = 182·1.15, which suggests a link to sprint speed and movescale. This is
**[inf]** only. λ is dimensionless.

**Wish magnitude.** The press command always had 0.5 on the axis. Whether a full 1.0 changes anything is
untested. The model uses the normalized wish direction, as M2 AirAccelerate does.

## 4. The window (task 2)

### 4.1 λ against time [fit]

All sideways sprint presses are used: 60 fps n = 15, 120 fps n = 16, 144 fps n = 45. Clamped and unclamped
presses are both converted to λ (§3.2).

Fade samples are those with 0.001 < λ < λ_max − 5 sd: n = 34 (60 fps 7, 120 fps 8, 144 fps 19). A straight
line is fitted to them, and the window edges are where the line reaches λ = 0.7 and λ = 0:

| fps | n | slope (1/s) | full strength ends | λ reaches 0 | rms of λ |
|---|---|---|---|---|---|
| 60 | 7 | −2.3329 (se 0.0004) | 0.2000 s | 0.5001 s | 0.0001 |
| 120 | 8 | −2.3378 (se 0.0008) | 0.1996 s | 0.4990 s | 0.0002 |
| 144 | 19 | −2.3307 (se 0.0010) | 0.2002 s | 0.5005 s | 0.0003 |
| all | 34 | −2.3329 (se 0.0024) | **0.2000 s** (se 0.0002) | **0.5001 s** (se 0.0002) | 0.0011 |

- The slope is λ_max / 0.3 s = 2.3333.
- The fade is **linear in λ**. The residuals are at print level (rms ≤ 0.0003 per frame rate), so no other
  shape is needed.
- Once the clamp no longer applies, the speed is kept exactly and only the heading turns. At 144 fps the
  heading change falls from 35.9° (t = 0.319 s) to 0.96° (t = 0.493 s).
- While λ is still large enough for the clamp (t below about 0.29 s at sprint speed), the speed still drops.
  It does so less and less: s₁/s₀ = 0.852 → 0.925 at 0.25 s → 0.98 at 0.285 s.

**Brackets from the sampled points alone, with no fit:**

| fps | last full-strength sample | first partial sample | last partial sample | first zero sample |
|---|---|---|---|---|
| 60 | 0.1833 s | 0.2666 s | 0.4667 s | 0.5000 s |
| 120 | 0.1832 s | 0.2502 s | 0.4921 s | 0.6333 s |
| 144 | 0.1807 s | 0.2488 s | 0.4934 s | 0.6320 s |

### 4.2 Time or frames? [fit] Time.

- **In commands**, the same zero crossing is at **30.0 commands (60 fps), 59.8 (120 fps) and 72.0 (144 fps)**,
  and full strength ends at 12.0, 23.9 and 28.8 commands. A frame-defined window would give one command
  count at every frame rate. In seconds, all three are 0.200 / 0.500 s.
- **The clock convention also separates.** If the window were counted to the end of the press command
  (t + dt), or from the end of the jump command (t − dt), the three frame rates would disagree by about 10 ms
  on both edges (`analysis_output.txt` §5). With t measured start-to-start they agree within 1.5 ms.
- **The remaining offsets** are 60 fps −0.03 ms (sd 0.03), 120 fps +0.74 ms (sd 0.18) and 144 fps −0.35 ms
  (sd 0.18). They are sub-millisecond and of mixed sign, so they read as clock/sampling noise of the summed
  frametimes, not a frame-rate effect. The window edges are therefore known to about **±1 ms**. With rounded
  parameters (0.7 / 0.2 s / 0.5 s / 209.3), the model error on fade presses is at most 0.11 u/s (60 fps),
  0.93 u/s (120 fps) and 0.69 u/s (144 fps). On every other press it is at most 0.006 u/s.
- **Jump press or take-off.** These happen on the same command in every trial, including the slide jump, so
  they cannot be separated. The model anchors on the jump command, which is a single anchor that serves both
  readings. The name `jump_grace_*` [src] is consistent with an anchor at the jump.

### 4.3 Repeatability [obs]

Repeated trials of one schedule at 144 fps agree as follows:
- |D|: within 0.002 u/s on the plateau.
- λ: within sd 0.0002–0.004 in the fade. This spread is fully explained by the tA jitter of 0–2.5 ms between
  repeats, through the 2.33/s slope.
- Back, walk, slide and W re-tap: identical to 0.002 u/s.

## 5. Back and W re-tap (task 3) [fit]

**Back is not "no lurch".** With wishdir = −v̂, the lerp gives (1−λ)·v̂ + λ·(−v̂) = (1 − 2λ)·v̂. While λ > 0.5,
this vector points backwards, so T = −|v|·v̂ and T − v = −2|v|·v̂. That is clamped to **209.3 u/s straight
against the velocity**:
- The observed speed goes 293.1 → 83.8 u/s (n = 9, t = 0.03 / 0.09 / 0.25 s).
- The heading change is exactly 0.000°.
- The model error is 0.002 u/s.

The earlier "no lurch" reading came from looking only at the heading, which a collinear brake cannot change.

**W re-tap.** θ = 0, so the lerp of identical directions is v̂ itself, T = v and D = 0. The observed |D| is
0.001–0.006 u/s at t = 0.03, 0.09 and 0.25 s (n = 9).
- So the W press does reach the lurch code. It has **no new direction to pull toward**.
- This is the same formula, not a special rule for the forward bit or a gate on new wish directions.
- The data cannot exclude that IN_FORWARD is ignored altogether, because both readings predict 0 here. A W
  press while moving sideways would separate them (§7).

**Prediction (untested).** For back, the lurch should switch off abruptly once λ < 0.5, at t ≈ 0.286 s.
Beyond that point T = +v and nothing happens. This is a sharp test of the lerp form.

## 6. Client and dedi parity (task 1) [obs]

- **The dedi MT row of the press command is identical to the client within 0.002 in 101 of 102 trials.** That
  includes every clamped, back and fade case. The exception is r1033 (120 fps, t = 0.492 s, λ = 0.016): the
  client |D| is 4.880 and the dedi |D| is 4.858. This is a 0.022 u/s difference, which corresponds to about
  0.03 ms of window clock. It persists afterwards at the same size.
- **The dedi computes the lurch itself, on its own clock, and does not copy the client.** That resolves the
  phase-1 contradiction (Movement-Analysis §4.4) in favour of a native inline lurch on the S3 dedi. The SDK
  hook only masks the press bits for cutoff speed, mantle boost and gravity cannon [src].
- **No corrections.** Between jump − 2 and landing + 1 there is no client state discontinuity in any trial.
  The r1033 difference is below the correction threshold.
- **Replays.** No client rp=1 replay covered a press command in these trials (only 2–8 rp=1 rows per run, all
  elsewhere). Replay parity of the lurch is **not tested**.

## 7. Evidence level and open questions

| claim | level |
|---|---|
| Lurch on the press-edge command only, horizontal only, after AirAccelerate | [obs]/[fit], 102 trials |
| λ_max = 0.7, clamp 209.3 u/s, lerp of unit directions, speed kept when not clamped | [fit] at print precision, 5 speeds/conditions × 3 fps |
| Window 0.2 s full, linear to 0 at 0.5 s, defined in time | [fit], 34 fade samples over 3 frame rates, ±1 ms |
| Back = 209.3 u/s brake, W = no-op by geometry | [fit], 18 trials |
| Dedi reproduces natively | [obs], 101/102 identical, 1 clock-level difference |

Open questions:
1. **Cutoff speed.** bridge_lurch_cutoff_speed / jump_grace_cutoff_speed = 1100 [src]. All presses here were at
   ≤ 350 u/s, so it is untested.
2. **Movescale and legend.** Is L = 209.3 a constant, 0.7 × sprint speed × movescale, or something else? This
   needs a run at another movescale.
3. **Intermediate angles and wish magnitude.** Diagonal presses (θ ≈ 45°, 135°) and a full-strength (1.0)
   press command are untested.
4. **IN_FORWARD.** Does a W press lurch when the velocity is not along the view? The current data cannot tell.
5. **Back after 0.286 s.** The lerp model predicts the brake vanishes abruptly when λ < 0.5.
6. **Several presses in one window.** Can each new press edge lurch again, for example A then D within 0.5 s?
7. **Anchor.** Jump press versus last ground contact (a walk-off ledge with no jump). Is there a lurch at all
   without a jump?
8. **Mantle-boost suppression [src]** and the client replay path are not exercised.

## 8. Chosen model for Unity (per usercmd, after M2 AirMove's AirAccelerate)

```
if airborne and (buttonsPressed & (FORWARD|BACK|MOVELEFT|MOVERIGHT)) and wishdir != 0:
    t   = curtime - jumpStartTime              # start of the jump command
    lam = 0.7 * clamp01((0.5 - t) / 0.3)
    if lam > 0 and |v_xy| > 0:
        d = normalize((1 - lam) * normalize(v_xy) + lam * wishdir)   # skip if zero (lam = 0.5, w = -v)
        D = |v_xy| * d - v_xy
        if |D| > 209.3: D *= 209.3 / |D|
        v_xy += D
```

**Why this model.** It has three numbers (0.7, 0.2/0.5 s, 209.3), each measured directly. It reproduces every
press to print precision outside the fade, and to under 1 u/s inside it. Every simpler alternative tested
fails by tens of u/s: constant a/b, AirAccelerate only, or a frame-counted window. The one alternative that is
equally complex, the slerp, fails the back presses.
