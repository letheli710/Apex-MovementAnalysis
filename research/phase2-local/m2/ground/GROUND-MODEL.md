# M2 / E1 ground model: start, cruise, stop, directions, stances, turning

Status: offline analysis of one session (`20261020_205712_M2_rerun`, runs r301–r335, 7 conditions × 5
trials, every trial `ok=true`, `warmup=false`, measured 142.6–143.95 fps). Nothing was launched and no
existing file was changed. Every number below is in `results.json`. The script writes that file, along with
`params.json` and `curves_<cond>.csv/.svg`:

```
python ground_analysis.py <session folder> [<session folder> ...] [--out DIR]
```

The script uses only the stdlib and the `hsdtel` parse/derive modules. It reads the session's
`report/census.csv` for the class vars and writes no raw log lines and no local paths.

Evidence labels: **[obs]** = measured here at the precision stated. **[fit]** = a parameter estimated
from the data. **[census]** = the session's client class var (E0 dump). **[inf]** = an inference the
data are consistent with but do not prove.

## 1. Method

**Physics truth.** These are the client first-time MOVE-TRACE rows (`side=cl`, no `rp=1`): 29 519
commands in 35 trials with no command-number gaps. Speed is the 2D norm of `v` (pre) and `pv` (post). On
this flat floor, `vz`/`pvz` stay 0 and `ground` stays 1 throughout.

**dt per command (HSD join).** Within each trial, every HSD client `kind=frame` line was compared with the
MT post-states. 16 660 of 16 660 moving frames matched exactly one command's post-state, and all of them
gave the same offset `seq − cmd` (35/35 trials have a single offset). Under that offset, 29 485 of
29 519 commands have a frame whose state equals their post-state. The 34 without one are the last command
of each trial, whose frame is not logged at the label switch. They are always stationary and appear in
the tables as `dt_missing`. So each frame shows post(N), which confirms SAMPLING-PHASE at 144 fps.

`dt(N) = ft` of the frame showing post(N). Validation against `dt_est = |Δxy| / |pv_xy|` over 13 680
grounded commands with post speed ≥ 150 u/s:

| frame used | mean \|ft − dt_est\| | within 10 µs |
|---|---|---|
| post(N−1) | 21.5 µs | 87.8 % |
| **post(N)** | **3.8 µs** | **99.95 %** |
| post(N+1) | 21.6 µs | 87.8 % |

`ft` is printed to 10 µs, which explains the 3.8 µs. The view yaw of the same frame is command N's yaw.
The velocity heading equals the yaw-derived wish direction within 0.0006° over 15 770 moving commands,
against up to 1.03° for frame N+1.

**Dedi check [obs].** All 29 519 client commands joined a dedi MT row (`derive.join_sides`). Their
post-states are bit-identical, with a max difference of 0.0.

**Segmentation.** The **press** is the first command with a movement button (FORWARD/BACK/MOVELEFT/
MOVERIGHT, `b=`). The **release** is the first later command without one. Time t is the cumulative dt
from the start of the press command. **Terminal speed** is the mean post speed over the last 1.0 s
before the release.

**Fits.** Constant-rate steps are fitted as `a = ΣΔs / Σdt`, which is the least-squares solution for
`Δs = a·dt`. The accel commands are held, grounded commands whose post speed is not clamped at
`maxspeed`. Each one is assigned to the band (low / mid / sprint) whose rate it is closest to. The decel
commands come after the release, with s0 > 0 and post speed > 0, which excludes the final zeroing step.
Per-trial fits come first, and `spread = (max − min) / mean`.

**Model tests.**
- *Open loop*: one step of the chosen model from each observed pre-speed with the observed dt, for every
  command from the press to the end of the trial (26 280 commands).
- *Closed loop*: the speed is simulated from the press using only the observed dt and input bits, then
  compared with the observed speed curve.

## 2. Chosen model

```
msc = movescale (1.15 here)                        cap = speed·msc | sprintspeed·msc (sprint flag) | 80·msc (ducked)
if move input held and s < cap:
    a = lowAcceleration·msc                 if s < lowSpeed·msc                       (2875 below 138 u/s)
      = acceleration·msc                    elif not sprinting
                                                 or s + sprintAcceleration·msc·dt < speed·msc   (517.5)
      = sprintAcceleration·msc              otherwise                                  (117.3)
    s = min(cap, s + a·dt)                  (band chosen from the PRE-move speed; one step may overshoot a band edge)
else (no move input):
    s = s − D·dt,  D = deceleration = 1250 (standing) | 1500 (ducked), NOT scaled by msc
    if s < 1: s = 0
v_xy = s · wishdir,  wishdir = normalize(fwd·forward(yaw) + side·right(yaw))   (instant redirect)
```

Accuracy. Open-loop max |error| is **0.0145 u/s** in every condition, which is the print and `ft`
quantisation level (2875 u/s² × 5 µs). No command errs by more than 0.05 u/s. The closed-loop speed RMS
is 0.002–0.037 u/s in 34 of 35 trials. In r331 it is 1.02 u/s (max 2.74), for the reason given in §3.3.

## 3. Results

### 3.1 Terminal speed and per-trial fits (5 trials each)

| condition | terminal u/s (spread) | low accel u/s² (spread) | mid accel (spread) | sprint accel (spread) | stop decel (spread) | stop time s / cmds |
|---|---|---|---|---|---|---|
| e1_walk | 199.525 (0 %) | 2875.36 (0.06 %) | 517.52 (0.10 %) | – | 1249.89 (0.04 %) | 0.160 / 23 |
| e1_sprint | 299.000 (0 %) | 2875.07 (0.07 %) | 517.46 (0.04 %) | 117.287 (0.02 %) | 1249.93 (0.03 %) | 0.243 / 35 |
| e1_crouch | 92.000 (0 %) | 2874.30 (0.03 %) | – (cap < 138) | – | **1499.76** (0.06 %) | 0.063 / 9 |
| e1_back | 199.525 (0 %) | 2874.56 (0.03 %) | 517.35 (0.04 %) | – | 1250.01 (0.07 %) | 0.160 / 23 |
| e1_side | 199.525 (0 %) | 2874.37 (0.04 %) | 517.43 (0.04 %) | – | 1249.67 (0.03 %) | 0.160 / 23 |
| e1_diag | 199.525 (0 %) | 2874.46 (0.05 %) | 517.50 (0.04 %) | – | 1250.01 (0.05 %) | 0.160 / 23 |
| e1_turn | 299.000 (0 %) | 2874.77 (0.09 %) | 517.50 (0.04 %) | 117.283 (0.02 %) | 1249.88 (0.03 %) | 0.243 / 35 |

Terminal speed is exactly `maxspeed` in every cruise command, so the spread is 0 by construction of the
clamp. It is a real zero, not rounding: the per-trial cruise SD is ≤ 0.0003 u/s.

Pooled values over all trials:
- low 2874.73 (n = 232 commands)
- mid 517.46 (479)
- sprint 117.285 (1204)
- standing decel 1249.90 (780)
- crouch decel 1499.76 (40)

Ratios to the census:
- low 2874.73 / 2500 = **1.1499**
- mid 517.46 / 450 = **1.1499**
- sprint 117.285 / 102 = **1.1499**
- decel 1249.90 / 1250 = **0.9999**

**Acceptance.** Terminal-speed spread ≤ 2 %: **pass**, 0 % in 7 of 7 conditions. Accel/decel parameter
spread ≤ 5 %: **pass**, the worst being 0.10 % (walk mid accel). Pooled across conditions, the spreads
are low 0.10 %, mid 0.10 %, sprint 0.02 % and decel 0.08 %.

### 3.2 Acceleration: piecewise constant with a low-speed branch [obs + census]

- The steps are linear in dt and constant within each band: one band below `lowSpeed·msc`, one above.
  The data put the low/mid edge at 136.38 < edge ≤ 138.47 u/s. That brackets lowSpeed × msc = 138.0.
  The band comes from the **pre-move** speed: a step from 135.6 u/s took the full low rate to 155.6.
- **Move scale multiplies accel and the speed limits, but not decel [obs ratio, inf mechanism].** All
  three accel rates are exactly census × 1.1499, and the decel is census × 1.0000. Only msc = 1.15 occurs,
  so the multiplication is shown by the exact ratios, not by varying msc.
- **Alternatives rejected.** These are closed-loop RMS values against the observed speed:

| model | walk-like RMS (u/s) | sprint RMS |
|---|---|---|
| chosen | 0.002–0.023 | 0.005–0.028 (r331: 1.02) |
| no low-speed branch (accel 517.5 from 0) | 23.1–24.6 | 24.0–26.5 |
| one constant accel fitted to all (1245.7) | 8.0–9.6 | 20.5–23.2 |
| decel × msc (1437.5) | 2.7 | 4.5–5.1 |

- **Input magnitude.** The first held command always has `fwd` (or `side`) = 0.5, a key pressed partway
  through the frame. That step still takes the full 2875 rate, and the diagonal's first step
  (0.5, 0.5) does too. Accel does not scale with the input magnitude [obs, first-command only].

### 3.3 Sprint [obs]

- **Speed.** The sprint cap is `maxspeed` = 299.000 = 260 × 1.15. The MT `ms` jumps from 199.525 to
  299 one command after the press, when the `spr` flag is set. The speed button and forward were pressed
  on the same command.
- **Ramp.** The speed rises in the low band to 138, then in the mid band (517.5) to about 199.5. After
  that it rises linearly at **117.29 u/s² = sprintAcceleration (102) × 1.15** until it reaches 299,
  1.00–1.02 s after the press.
  - **Census note.** The census of this session reads `sprintAcceleration = 102`, while the T0-smoke
    census reads 100. With 100 × 1.15 = 115, the closed-loop RMS is 0.39–0.96 u/s instead of
    0.005–0.03, so 102 is what this build uses.
- **Timing keys.** The data show no `sprintStartDelay` (0.2 s), `sprintStartDuration` (0.8 s) or
  `sprintStartFastDuration` (0.2 s) effect on speed:
  - The sprint rate already starts 0.14–0.17 s after the press. A 0.2 s delay would show as a plateau
    at 199.5, and there is none.
  - The rate in the first 0.2 s of the sprint band is 117.27–117.31. After that it is 117.27–117.30, so
    there is no fast phase.
  - These keys may drive animation or the view, or apply in a path not exercised here [inf].
  - `sprintEndDuration` was not exercised, because sprint and forward were released together.
- **Mid → sprint edge.** The edge is not exactly `speed·msc`. The decisive commands:

| run | pre-speed s0 | rate used | prediction of the s0 ≥ speed·msc rule | prediction of s0 + a_spr·dt ≥ speed·msc |
|---|---|---|---|---|
| r332 | 197.970 | mid | ok | ok |
| r331 | 198.718 | **sprint** | wrong by 2.78 u/s | ok (−0.0009) |
| r309 | 198.779 | **sprint** | wrong by 2.78 u/s | ok (0.0002) |

  The "one sprint step below the walk cap" rule fits all 47 commands with s0 in 185–201 and needs no
  extra parameter, so it is the chosen rule. A fixed edge anywhere in (197.97, 198.72] would fit
  equally well, and only two commands discriminate, so the **evidence is weak**. In r331 the observed
  margin is 0.007 u/s. The closed-loop prediction drifts by about 0.01 u/s before that point and lands
  on the other side of the edge. It then trails by 2.74 u/s until the cap. That trailing error is the
  only closed-loop deviation above 0.11 u/s in all 35 trials. For a game the choice of edge is
  immaterial: at most 2.8 u/s for at most about 0.85 s.

### 3.4 Deceleration: constant, not Source friction [obs]

- **Constant rate.** Standing, the rate is 1249.90 u/s², and it is independent of speed. By 50 u/s
  band, from 0–50 up to 250–300, it ranges from 1249.80 to 1250.14. The per-command residual RMS is
  0.0046 u/s and the max is 0.0078 u/s. The sprint stop from 299 uses the same rate. `sprintDeceleration`
  is also 1250, so the two keys cannot be told apart here.
- **Source friction does worse.** In the Source form `drop = max(s, stopspeed)·f·dt`, a stopspeed of 100
  (f fitted, 7.46) gives a per-command RMS of 3.08 u/s. The least-squares stopspeed runs to the top of
  the grid (400 > 299), and there the Source form collapses into the constant-decel model (RMS 0.0046).
  The two are only indistinguishable when stopspeed exceeds the top speed. Constant decel is the simpler
  of the two and is chosen.
- **Crouch.** Ducked, the decel is **1499.76** (spread 0.06 %). No crouch census key was read. 1500 is
  not 1250 × 1.15 (1437.5) [obs].
- **Snap to zero.** In all 35 stops, the last step goes to exactly 0. In 6 of those stops the constant
  decel would have left 0.21–0.58 u/s, and the smallest post speed that was kept is 1.576. The model
  uses Source's `speed < 1 → 0`, which the data bracket in (0.58, 1.58] [obs bracket, value assumed].
- **Stop times.** From 199.525 the stop takes 23 commands, 0.160 s: 22 decel steps plus the zeroing
  step. The M1 first look counted 22. From 299 it takes 35 commands, 0.243 s. From 92 ducked it takes
  9 commands, 0.063 s.

### 3.5 Directions and stances [obs]

- **Back and side.** These match walk exactly: same caps, same rates (table 3.1), consistent with
  `speedScaleBack` = `speedScaleSide` = 1 [census]. Whether those keys would scale the cap or the accel
  when ≠ 1 is not tested.
- **Diagonal.** The wish direction is **normalized**. The cap stays 199.525, not 282, and all rates
  equal the forward ones. The velocity heading equals the wish direction (yaw 45° + right → +X) within
  0.0006°.
- **Crouch.**
  - Ducked speed cap 92.000 = 80 × 1.15.
  - Accel 2874.3, the low band, because 92 < 138. Crouch accel above 138 u/s is untested.
  - Decel 1500.
  - Forward was pressed 1 s after +duck, and `duck` reached 2 (full) 0.45–0.47 s after the press. Only
    fully-ducked motion was measured. Moving during the duck transition is untested.

### 3.6 Turning (e1_turn) [obs]

- **Yaw rate.** While +right is held (button bit 0x100), HSD yaw changes by `rate·dt` per command. The
  rate is **140.70 °/s** (per-trial medians 140.67–140.72, spread 0.03 %, per-command SD 0.09). The
  first command turns at half rate (70.4 °/s), the same partial-frame effect as `fwd = 0.5`. The total
  turn was 140.07–140.42° over 144 commands (≈ 1.0 s).
  - The rate is a client turn setting (cl_yawspeed-type), not movement physics. Source's default would
    be 210. Why it is 140.7 is open [inf].
- **Velocity follows the view instantly.** While running at the 299 cap, the velocity heading equals
  the yaw in every turn command, within a max of 0.0006° (mean 0.0003°).
  - The speed stays at 299.000 ± 0.0007 (loss 0.0002 %).
  - The `spr` flag and the 299 cap persist through the turn.
  - Once the turn stops, the heading stays locked to the yaw (≤ 0.0005°).

  At 140 °/s on the ground there is no acceleration-limited redirection and no turn speed penalty. The
  model is `v = s·wishdir`. Faster turns (flicks) and turns below the cap are untested.

## 4. Uncertainty and open questions

1. **Move scale.** Only msc = 1.15 was observed. The claim that "accel × msc, decel not × msc" rests on
   exact ratios. A run at a different msc (another legend or a weapon) would test it directly.
2. **Mid → sprint edge.** Two decisive commands support it (§3.3). Either rule is fine for the game.
3. **Crouch decel 1500 and crouch speed 80.** Both are fitted only; the per-stance class vars were not
   dumped. A crouch census (poseSettings row 1) would confirm them. Crouch accel above 138 u/s and
   movement during the duck transition are untested.
4. **Sprint timing keys.** sprintStartDelay, sprintStartDuration, sprintStartFastDuration and
   sprintEndDuration show no effect on speed. Releasing sprint while still holding forward (sprint → walk
   decel at `sprintDeceleration`) was not tested.
5. **Snap threshold.** The data give only the bracket (0.58, 1.58]; the value 1 is assumed from Source.
6. **Single session, single frame rate.** dt was 6.7–7.2 ms. The band-by-pre-speed rule makes the
   overshoot at band edges depend on dt. That is why time-to-cap varies by 0.145–0.167 s with the dt
   pattern (spread up to 13 % in e1_back), even though every rate is constant to 0.1 %. Another fps was
   not tested.
7. **Scope.** The floor was flat and the player was empty-handed (Gibraltar). Slopes, weapons, input
   magnitudes other than {0.5 on the first command, 1}, and mid-run direction reversals are not covered.

## 5. Files

- `ground_analysis.py`: the analysis described above.
- `results.json`: join and dt validation, per-trial fits, model comparisons (open and closed loop), the
  sprint edge commands, stop snap, turning, dedi check and acceptance.
- `params.json`: the chosen parameters with value, unit, source, n, spread and formula.
- `curves_<cond>.csv`: per trial and command: k from press, t, observed speed, closed-loop model speed,
  held/sprint/duck flags and yaw.
- `curves_<cond>.svg`: the 5 trials overlaid, with the model (first trial's dt) dashed.
