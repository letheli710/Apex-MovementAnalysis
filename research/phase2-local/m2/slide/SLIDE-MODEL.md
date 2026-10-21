# M2 / E5: slide and slide-jump momentum model

Status: offline analysis of the logged sessions `20261020_204723_M2_main` (e5 trials) and
`20261020_205712_M2_rerun` (e1_sprint baseline, plus an e4_stand cross-check). Nothing was launched and no
existing file was changed.

```
python slide_analysis.py <session folder> [<session folder> ...] [--jump-xcheck] [--params params.json] [--json all.json] [--verbose]
```

The script (stdlib + `hsdtel`) writes `params.json`. Every number below comes from its output.

Labels: **[obs]** is read directly from the logs. **[fit]** is a least-squares value over usercmds. **[inf]** is
an inference that the data are consistent with but do not prove. **[cen]** is an E0 census value.

## 1. Data and method

| schedule | runs | trials used | what it does (144 fps frames) |
|---|---|---|---|
| e5_slide | r271–275 | 5 | sprint + W 288 f, then hold duck 432 f, release |
| e5_slidejump02 | r276–280 | 5 | as above, tap jump 29 f (0.20 s) after the duck press |
| e5_slidejump06 | r281–285 | 5 | as above, tap jump 86 f (0.60 s) after the duck press |
| e1_sprint (baseline) | r306–310 | 5 | sprint 3 s, release |
| e4_stand (`--jump-xcheck` only) | r251–253, r351–355 | 8 | one standing jump; used only to calibrate how the jump usercmd logs vz (§4.2) |

- Only `ok=true, warmup=false` trials are used. Gibraltar, empty-handed, movescale (msc) 1.15 in every usercmd.
  Measured fps was 143.85–143.98 for all e5 trials.
- **Physics truth.** Client MOVE-TRACE first-time usercmds (side `cl`, not `rp=1`), which give the pre-state
  (`v`) and post-state (`pv`) of each `FullWalkMove`. Speed means |v_xy|.
- **dt per usercmd.** Each moving HSD client frame is joined to the usercmd whose post-state (`po`, `pv`, six
  values at 0.001 precision) equals the frame state. The usercmd must also be logged no later than the frame
  (wall clock + 20 ms). The frame's `ft` becomes that usercmd's dt (SAMPLING-PHASE.md).
  - **Join validation [obs]:** all 20 e5 and e1 trials have 0 unjoined moving frames and 0 frames with more
    than one candidate. Consecutive joined frames advance the usercmd number by exactly 1 (100 %).
    |ft − dt_est| has a median of 3.2–3.5 µs and a p95 ≤ 7.5 µs over usercmds above 150 u/s.
  - Static frames are not joined because they are not needed. Every fitted usercmd moves.
- **Dedi parity.** Every client usercmd of the 15 e5 trials is joined to its dedi MT line (100 %). Dedi post-speed
  minus client post-speed is **0.000** (max abs) and the slide flags never differ. The S3 dedi therefore
  reproduces the S21 client slide physics bit for bit.

## 2. Slide start and boost

| quantity | value (n = 15 trials, all three schedules) | label |
|---|---|---|
| entry speed (post of the usercmd before the duck press) | 299.000, spread 0 | [obs] |
| first slide usercmd | **the duck-press usercmd itself** (offset 0 in 15/15) | [obs] |
| pre-state speed of that usercmd (the peak) | **460.000**, spread 0 | [obs] |
| boost gain = peak − entry | **161.000**, spread 0 | [obs] |
| time to peak | 0: the boost is applied inside the duck-press usercmd *before* the move. That usercmd's post is already decayed (458.17–458.20) | [obs] |
| maxspeed while sliding (MT `ms`) | 92 (= crouch) | [obs] |

The duck-press usercmd already carries `slide=1` and the boosted speed in its *pre*-move state. This fits
Phase 1 §5: `Duck → TryBeginSlide` runs before `FullWalkMove`.

**Boost formula (chosen):** `v_peak = min(v + slideSpeedBoost·msc, slideSpeedBoostCap·msc)`, which gives
`min(299 + 172.5, 460) = 460`. The gain is stored as `lastSlideBoost = v_peak − v` (161).
- 460.000 = 400 × 1.15 exactly, so the cap scales with movescale **[obs, one movescale]**.
- An unscaled boost (299 + 150 = 449) is **rejected**: the observation is 11 u/s higher.
- The data only show `boost·msc ≥ 161`. The census 150 × 1.15 = 172.5 is consistent but not measured, because
  the cap binds in every trial. The equivalent unscaled reading is `msc · min(v/msc + 150, 400)`.
- `slideRequiredStartSpeed` 200 [cen] was not exercised: slide entries were at 299, 248 and 350 u/s.
- **Comparison with the pilot:** the pilot's "peak ≈ 458" is the post-state of the first slide usercmd, and so is
  hsd_tel `slides` (`speed_peak` 458.17, `boost` 159.17). The true peak is 460 (pre-state).

## 3. Speed during the slide

### 3.1 Model choice (round 1: law)

The fits use a = (v_pre − v_post)/dt per grounded slide usercmd, over all slide segments of each trial
(n = 136–265 usercmds per trial), with W held on flat ground.

| law | e5_slide rmse of a (u/s²) | slidejump02 | slidejump06 | verdict |
|---|---|---|---|---|
| M1 constant decel a = D | 34.5 | 38.4 | 33.5 | rejected (D drifts 184–200 with the speed range) |
| M3 pure exponential a = k·v | 32.8 | 41.3 | 31.7 | rejected |
| **M2 a = D + k·v** | 1.29 | 0.11 | 0.11 | **chosen** |

**M2 fit per trial [fit]** (pooled over 15 trials):

| | mean | min..max | spread | census |
|---|---|---|---|---|
| D (u/s²) | 99.61 | 99.01..100.06 | **1.06 %** | slideDecel 100 |
| decay = e^−k (per s) | 0.7001 | 0.6989..0.7010 | **0.30 %** | slideVelocityDecay 0.7 |
| k (1/s) | 0.3565 | 0.3552..0.3582 | 0.84 % | −ln 0.7 = 0.3567 |

Both spreads are within the 5 % target. The duck=1 (crouching transition, first ~34 usercmds) and duck=2 subsets
give the same values within 2 %. **slideDecel is not scaled by movescale** (115 would be off by 15 %).

### 3.2 Step ordering (round 2)

The census values are used with no free parameter. Residual = observed post speed − predicted, in u/s per usercmd:

| step | mean | rms (pooled per-trial mean) | note |
|---|---|---|---|
| **decel then decay: v' = (v − 100·dt)·0.7^dt** | **+0.0004** | 0.0035 | chosen |
| ODE exact: v' = (v + D/k)·e^(−k·dt) − D/k | +0.0013 | 0.0039 | |
| decay then decel: v' = v·0.7^dt − 100·dt | +0.0021 | 0.0045 | |

- In the jump trials the chosen step gives an rms of 0.0007–0.0009 u/s and a max of 0.002 u/s per usercmd, which
  is the print precision.
- In e5_slide the rms is higher (0.007–0.011), only because of one floor spot.
  - Five to seven usercmds at 141–148 u/s, at the same map position in all five trials, deviate by up to
    ±0.12 u/s while |Δz| reaches 0.036 u.
  - The deviation is a ground-normal artefact [inf] and nets to ≈ 0. The slide takes the ground normal (Phase 1 §5).
- The three orderings differ by ≤ 0.002 u/s per usercmd, which is ≈ 0.5 u/s over a whole slide at 144 Hz.
  This is not a meaningful difference for the practice game.
- The decel-then-decay step is kept because it has the smallest bias and is equally simple. The ODE form is an
  acceptable frame-rate-independent substitute.

**Validation [obs]:** the chosen step was applied to the observed dt from 460. Its first post below 125
falls on the same usercmd as the real slide end (244 usercmds) in 5/5 trials. The predicted final speed is 124.58
against 124.75 observed.

### 3.3 Not exercised

- **slideAccel 50:** no effect is visible with W held on flat ground. Fitted D stays within 0.4 % of 100, so any
  extra acceleration would be ≲ 1 u/s².
- **slideWantToStopDecel 400, slideMaxStopSpeed 350:** not exercised. Forward was held throughout, and
  there was no back or release input during the slide.

## 4. Slide end and crouch walk

| quantity | value (e5_slide, n = 5) | label |
|---|---|---|
| pre speed of the last slide usercmd | 125.76 (125.43..125.92) | [obs] |
| post speed of the last slide usercmd | 124.75 (124.42..124.91) | [obs] |
| rule | the slide ends after the first usercmd whose **post < slideStopSpeed 125** (unscaled), with duck still held | [obs] + [cen] |
| slide duration from 460 | **1.6928 s** (1.6923..1.6935, 244 usercmds) | [obs] |
| continuous check | t = ln((460 + D/k)/(125 + D/k))/k = 1.689 s | [inf] |
| post-landing slides (jump trials) | also end at post 124.26 / 124.72, with duck held | [obs] |
| crouch decel above crouch speed | **1499.55 u/s²** (1499.32..1499.86, spread 0.04 %; 3 usercmds per trial), 125 → 92 in 4 usercmds | [fit] |
| crouch-walk speed | **92.0** (= MT maxspeed while ducked) | [obs] |
| baseline: standing stop decel (e1_sprint release) | 1249.93 (1249.73..1250.07) = census `deceleration` 1250 | [fit] |

The crouched over-speed decel is 1500 = 1.2 × 1250. No census key for it was identified [inf]. It is modelled as a
constant: `v' = max(v − 1500·dt, 92)`.

## 5. Slide jump: early (0.2 s) and late (0.6 s)

### 5.1 Horizontal

| quantity | early (jump02, n = 5) | late (jump06, n = 5) |
|---|---|---|
| time from boost to jump usercmd | 0.2012 s (0.2007..0.2017) | 0.5967 s (0.5965..0.5969) |
| duck state at the jump | 1 (still crouching) | 2 |
| speed before the jump (pre) | 408.76 (408.64..408.88) | 318.15 (318.11..318.19) |
| take-off speed (post of the jump usercmd) | **247.77** (247.64..247.89) | **350.005** (spread 0) |
| change | **−160.992** (spread 0.0005) | **+31.85** (31.82..31.90) |
| expected | refund of lastSlideBoost: pre − 161 = 247.76 (residual +0.008 = in-air accel of the jump usercmd) | slideMaxJumpSpeed 350 (+0.005 air accel) |

**Readings:**

- **Refund confirmed [obs].** A slide jump 0.20 s after the boost loses exactly the stored gain, 161. That is the
  actual gain, not slideSpeedBoost 150 or 172.5. The full amount is taken even though 0.2 s of decay passed.
  At 0.60 s nothing is subtracted.
  - The window edge lies between 0.201 and 0.597 s.
  - The 0.4 s value comes from the source (Phase 1 §4.3) and is not measured here [C].
- **350 is a target, not only a cap [obs].** At 0.6 s the speed is *raised* from 318 to 350, unscaled (not 402.5).
  - Two rules fit both conditions:
    - (H1) `v' = max(v, 350)` outside the refund window;
    - (H2) `v' = max(v, min(v + J, 350))` with J ≥ 31.85.
  - In both rules, the early jump requires that the 350 rule is *not* applied after the refund (otherwise 247.8
    would be lifted to 350). Either the refund branch skips it, or the 350 rule runs first: max(408.9, 350) − 161.
  - **Chosen: H1**, because it has no unmeasured parameter (rule: with two indistinguishable models, take the
    simpler one).
  - H1 and H2 differ only for v < 350 − J. Neither rule is tested for v > 350 outside the window (keep or cap?).
- **Dedi:** the S3 take-off speed and vz are identical. The dedi `JUMP` event state carries the *pre*-jump speed
  (408.76 / 318.15), so the event is raised before the speed change.

### 5.2 Vertical

| quantity | early | late | plain standing jump (`--jump-xcheck`, n = 8) |
|---|---|---|---|
| post vz of the jump usercmd | 267.10 (267.03..267.19) | 265.80 (265.72..265.92) | 281.99 |
| H = (pvz + 1.5·g·dt)²/2g | **50.37** (spread 0.02 %) | **49.90** (spread 0.01 %) | **56.001** (census jumpHeight 56) |
| same with a 1.0·g·dt offset | — | — | 54.996 (rejected) |
| apex height above take-off origin | 49.37 | 48.91 | — |
| air time | 0.7215 s | 0.7214 s | — |
| gravity (−dvz/dt in air) | 749.97 | 749.81 | 749.75 |

- The plain jump shows that the jump usercmd logs `vz_post = sqrt(2·g·H) − 1.5·g·dt`. With that, H = 56.001 for
  the 8 plain jumps, which validates the conversion.
- Slide jumps then give H = 50.37 / 49.90 against **slideJumpHeight 50**, within 0.75 % [fit].
- The +0.47 u gap of the early jump (+1.0 u/s vz) coincides with duck=1, the crouch transition [inf: hull/eye
  offset while ducking]. It is too small to matter for the game.
- Take-off vertical speed: `v_up = sqrt(2·750·50) = 273.9 u/s`, using unscaled sv_gravity 750.

### 5.3 Landing ("landing momentum")

| quantity | early | late |
|---|---|---|
| landing speed | 248.11 | 350.21 |
| state on the landing usercmd | slide=1, duck=2 (slide resumes at once) | same |
| new boost on landing | **0** | **0** |
| decel of the landing usercmd | 188.17 (census law 188.49) | 224.52 (224.91) |
| post-landing slide | 108 usercmds, ends at 124.26 | 179 usercmds, ends at 124.72 |

- Landing with duck held above 200 u/s re-enters the slide with **no landing speed loss**. No
  `landSlowdownDuration` effect is visible while sliding.
- Re-entry gets **no new boost**. The cause is open: the cooldown (`player_slideBoostCooldown`, value unknown,
  > 1.32 s if it is the cause), the air entry (`bFromAir`), or the missing new duck press.
- Air speed gain over the 0.72 s flight: +0.34 / +0.21 u/s, which is negligible (E2 covers air accel).

## 6. Chosen model (for the Unity controller)

```
// constants: msc = movescale (1.15 Gibraltar); speeds are |v_xy| along the current horizontal direction
OnDuckPress (grounded, not sliding, |v| >= 200):         // 200 not tested
    vPeak = min(|v| + 150*msc, 400*msc)                   // 460 from sprint 299
    if boostAllowed: lastBoost = vPeak - |v|; tBoost = now; |v| = vPeak   // boostAllowed: see open Q4
    sliding = true
EachTick while sliding and grounded:
    s = (s - 100*dt) * pow(0.7, dt)                       // slideDecel, slideVelocityDecay (unscaled)
    if s < 125: sliding = false                           // slideStopSpeed (unscaled)
Ducked, not sliding: s = max(s - 1500*dt, 92)             // crouch over-speed decel; crouch speed at msc 1.15
Standing, no input:  s = max(s - 1250*dt, 0)              // census deceleration (baseline)
SlideJump (sliding, jump press):
    if now - tBoost < 0.4: s = s - lastBoost              // refund
    else:                  s = max(s, 350)                // slideMaxJumpSpeed (H1, see open Q2)
    vz = sqrt(2*750*50)                                   // slideJumpHeight
Air: vz -= 750*dt
Land with duck held and s >= 200: sliding = true, no boost, no speed loss
```

| parameter | value | source | n | spread | evidence |
|---|---|---|---|---|---|
| boost cap | 400·msc = 460 | census slideSpeedBoostCap + obs | 15 | 0 | A (one msc) |
| boost | 150·msc (≥ 161 shown) | census slideSpeedBoost | 15 | 0 | C |
| slideDecel | 100 (fit 99.61) | census + fit | 15 | 1.06 % | B |
| slideVelocityDecay | 0.7 (fit 0.7001) | census + fit | 15 | 0.30 % | B |
| slideStopSpeed | 125 | census + obs end | 5 (+10 post-landing) | end post 0.39 % | A |
| crouch over-speed decel | 1500 (fit 1499.55) | fit | 5 | 0.04 % | B |
| crouch speed | 92 | obs | 5 | 0 | A |
| refund window | 0.4 s | source (Phase 1), bracket 0.201–0.597 | 10 | — | C |
| refund amount | lastSlideBoost (161) | obs | 5 | 0.0006 % | A |
| slideMaxJumpSpeed | 350, rule max(v, 350) | census + obs (318 → 350) | 5 | 0 | C |
| slideJumpHeight | 50 (fit 50.37 / 49.90) | census + fit | 10 | ≤ 0.02 % per group, 0.9 % between | B |
| gravity | 750 (fit 749.89) | census sv_gravity + fit | 10 | 0.07 % | B |

## 7. Uncertainties and open questions

1. **Boost size and movescale scaling.** Only the cap was binding (one entry speed, one movescale). Test: a slide
   from an entry speed below 460 − 172.5 = 287.5 (for example duck 0.25 s into the sprint ramp) on a second
   legend or movescale.
2. **Slide-jump horizontal rule outside the refund window.** H1 (floor 350) and H2 (+J capped at 350) cannot be
   separated, and the case v > 350 is untested. Test: slide jumps at 1.0 s and 1.4 s (model speeds ≈ 268 and 206),
   and a fast (downhill) slide.
3. **Refund window edge** (0.201 < w ≤ 0.597 s). Test: jumps at 0.35 s and 0.45 s (frames 50 and 65).
4. **Boost on slide re-entry.** No boost at 0.92 s or 1.32 s after the first boost. It is unknown whether this is
   the cooldown or the air entry. Test: stand up and re-duck on the ground at 1, 2 and 3 s.
5. **slideRequiredStartSpeed, slideAccel, slideWantToStopDecel, slideMaxStopSpeed** were not exercised. Census
   values are kept [D]. Slopes (ground normal) and turning during a slide were also not tested (yaw 0, straight line).
6. **Early slide jump H = 50.37** (duck=1) against 49.90 (duck=2). This 1 % effect is attributed to the crouch
   transition [inf].
7. **Dedi HSD slide events.** `BEGIN_SLIDE`/`END_SLIDE` never appear: 0 of the 317 dedi events in the main
   session, although the mod registers them. Only JUMP / LEAVE_GROUND / TOUCH_GROUND fire. Dedi slide parity
   therefore rests on the dedi MT `slide` flag, which matches the client in 100 % of usercmds.
8. **Floor seam** in e5_slide near 145 u/s (±0.12 u/s, same spot in every trial). It is not excluded from any fit and
   only inflates the e5_slide rms.

## 8. Cross-check with `hsd_tel.py slides`

The generic tool uses the post-state speed. It reports `speed_peak` 458.17–458.20 and `boost` 159.17–159.20
(161 minus one usercmd of decay). Its linear `mean_decel` is 196.7 u/s² with r² 0.994 (e5_slide). The slide
durations are the same: 244 MT usercmds per e5_slide trial. Both agree with the results here, and the tool's
linear fit is the M1 law that §3.1 rejects.
