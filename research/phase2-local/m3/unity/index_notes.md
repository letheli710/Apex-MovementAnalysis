## 0. Findings

**What changed in the motor (HSD-Unity `m3/advanced-tech`).** Lurch on the airborne press-edge command after AirAccelerate
(lam 0.7, full to 0.2 s, zero at 0.5 s, time-based from the start of the jump command, |Δv| ≤ 209.3); a ground (non-slide) jump leaves at
min(v_h, sprintspeed·msc = 299); a slide resumed by a ducked landing is "not boosted" and its slide jump keeps its speed. `WallBounce` and
`MantleBoost` are separate primitives (unit-tested only: the replay has no wall geometry).

**Lurch command: reproduced.** On all 22 M3 press commands (right at 60/120/144 fps, walk, slide 350, back, W re-tap) the heading error
after the press is ≤ 0.04° and the error of the command's Δv is ≤ 0.07 u/s on the plateau (t < 0.2 s), back and W. In the fade
(t 0.25–0.49 s) the Δv error is 0.02–1.98 u/s and the heading error ≤ 0.25° (worst r1029, 120 fps, t 0.358 s). That is about 1 ms of window
clock, the edge uncertainty the lurch analysis reports (±1 ms, session clock offsets up to +0.74 ms at 120 fps); the replay clock is the sum of
samples.csv dt. Before (M2 motor, no lurch) the same commands were off by 209.3 u/s and up to 64°. M2 e2_strafe: pos RMS 80.8 → 0.47 u.

**Air phase (takeoff → landing): mostly ≤ 0.4 u RMS** for the e3 trials. Exceptions and causes:

- e3_right_k42_120fps (r1029) / k58_120fps (r1033): air pos RMS ≈ 0.9–1.0 u. These two trials (and the six e8 120 fps reruns) have an
  empty `parameters` block, so the preset census `sprintAcceleration` 102 is used instead of the session's 100; the sim reaches the jump
  1.5–1.6 u/s faster. Pre-existing loader/preset behaviour, not tuned.
- e3_right_slide350, e8_fast_hops, e8_hop350: air pos max ≈ 16 u and landing +8/+10 steps. In R5 the duck is released in the air and the
  un-crouch lowers the origin by ~16 u (crouched hull); the M2/M3 motor has no duck hull transition, so it lands later. On e8_hop350 this
  also makes the sim miss the immediate re-jumps (takeoffs 4 ref / 2 sim): the ground-jump cap (350 → 299) therefore is **not** exercised
  by the replay; it is covered by the unit test only.

**After landing (ground phase of the e3 trials): the largest errors, 12–43 u pos RMS, vel max up to 366 u/s.** R5 lands with the
lurched velocity and turns it toward the held key gradually (≈ 1250 u/s² as a vector), while the M2 ground model sets v = s·wishdir
instantly (GROUND-MODEL choice, unchanged here to keep M2 bit-for-bit). The lurch trials are the first to land with velocity far from the
input direction, so this M2 gap dominates their overall RMS. For the fade trials (k25/k50/k58/k60) the overall RMS is therefore similar to
or slightly worse than before although the air-phase pos RMS improved (k25 2.55 → 0.10, k50 16.3 → 0.21, k60 2.88 → 0.31; k58 0.95 → 0.89, its lurch is only 9 u/s) (before, the missing lurch left the sim moving +X, which happened to be
closer to the ref after landing).

**Slide chain: pos RMS 88.4 → 2.5 u.** The resumed-slide jump keeps 238 u/s instead of the M2 floor 350. Remaining: slide end +6 steps
on the duck release at the end (M2 slide-end rule).

**Regression:** 35 of 37 M2/M1 trials byte-identical to `../../m2/unity`; the 2 changed are e2_strafe (the only ones with a lurch).
Note: the M2 synthetic EditMode fixture (`synthetic_v2_trial`) encoded the M2 choice "350 floor on a resumed-slide jump"; it was regenerated
with its generator updated to the M3 rule (only rows ≥ 188 change); the test code is unchanged apart from one doc comment.

**Known gaps:** walls/climb/mantle are not in the replay (WallBounce / MantleBoost only unit-tested); pure side press on the wall jump
(measured 140.9/177.5) not reproduced by the O/I formula; mantle-boost camera gates and lurch suppression after a boost; lurch cutoff 1100,
movescale dependence of 209.3, diagonal presses, several presses per jump (each press edge lurches, untested); walk-speed ground jumps
(cap taken as sprint cap); duck hull transition; ground redirect after landing.
