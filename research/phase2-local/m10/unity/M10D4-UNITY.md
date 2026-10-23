# M10-D4 (track U): the ground vector redirect lets a reversed input keep running forward

HSD-Unity branch `m10d4/redirect` (from main `d7b74c8`), commit `b0cccc1`. Build `HSD-Build/M10/HSD-Practice.exe` (the final M10 build).

## 1. Defect

Reference and Fun, on the ground: sprint (or walk) forward, then hold S with the mouse still. The body kept moving forward at 199.5 u/s
for as long as S was held. A one-command 180° turn while holding W did the same. A yaw change of about 1° or more got the body out, after a delay.
Found by the M10-W agent.

## 2. Root cause

`R5MotorV2.GroundVectorRedirect` (M5 reference option `groundVectorRedirect`, on in both configs) split v into a part along the wish ŵ
(`along = v·ŵ`) and a cross part, and decayed only the cross part at D:
- With the wish exactly opposite, `along = −s` and the cross part is 0, so the decay did nothing.
- The band acceleration adds `min(rate·dt, cap − s)`, which is 0 at the cap.
- The limit `|v| ≤ max(cap, s − D·dt)` takes an over-cap sprint down to the cap and then holds it.

So the backward along-component was never braked. The state is an unstable equilibrium: off 180° the cross part dies within a few
commands, `cap − s` grows only geometrically, and the escape time goes to infinity as the angle goes to 180°. With an over-cap
entry, wide turns stuck too: before the fix, a 143° snap turn from a sprint ended at 298.66 instead of 299.

## 3. Fix (one line, `R5MotorV2.cs`)

`along = max(0, v·ŵ)`. The off-wish part is now v minus its forward along-component: the cross part, plus the along part when it
points against the wish. That part decays at D (1250 u/s² standing, 1500 ducked, the M2 census deceleration). The band acceleration
along ŵ and the over-speed limit are unchanged.
- For v·ŵ ≥ 0 the arithmetic is the same as before, bit for bit (aligned motion is still the M2 rule; `AlignedGroundMotionIsTheM2RuleBitForBit` passes).
- The law is continuous through 90° and through 180°: no special case.
- Above the cap a reversal brakes at 1250 u/s². Below it, the band acceleration adds on top: about 1767.5 u/s² at walk band speed, and
  about 4124 u/s² below lowSpeed (low acceleration 2874 + 1250). From a 299 sprint the forward motion stops in about 0.19 s; from a walk, in about 0.11 s.
- **How this fits the R5 data.** It matches the M5 measurement (reference_config/README.md): after a landing, R5's friction vector is
  1250 u/s² and leans toward −ŵ, so it also brakes the along-wish part. M2 did not measure mid-run reversals (GROUND-MODEL §4.7), so the
  exact R5 reversal profile stays **[model]**.

## 4. Tests (`Game/Tests/Editor/M10D4GameTests.cs`, 16 cases; all 16 failed before the fix)

| Test | Checks |
|---|---|
| `HoldingBackAfterRunningReverses` (2 configs × sprint with or without the sprint key / walk) | each command, while the forward component is > 0 it falls by at least D·dt; it reaches 0 within 0.5 s; the body ends at −cap with no sideways drift |
| `OneCommand180TurnReverses` (2 configs × sprint / walk) | same checks, for a snap from yaw 0 to 180 while holding W |
| `SnapTurnIsContinuousAt180` (2 configs) | turns of 179, 179.9, 179.99, 180.01, 180.1 and 181° stay within 600·sin\|Δ\| of the 180° velocity at every command |
| `EveryWideTurnEndsAlongTheWish` (2 configs) | every snap turn from 91° to 180°, sprint and walk, ends at the cap along the wish with no cross part |
| `PracticeSprintThenHoldBackRunsBackward` (2 configs) | the practice game (demo runner, real key segments): 1.2 s of W+Sprint, then 1.2 s of S → backward at < −195 u/s (before the fix: +199.5) |

EditMode **1984 / 1984** (main 1968 + 16). PlayMode **1 / 1**.

## 5. Regression (default replay motor; outputs in a scratch folder)

| Set | Result |
|---|---|
| M2 + M1, `-motor both`, vs `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor (`m2/unity`) | 35 / 76 (the known M3 set) |
| M2 + M1, M1 first guess | 111 identical |
| M3 (`-motor v2`) | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `--base m4_replay`) | 114 identical |

Why: the replay motor (`R5MotorV2Params.FromTrial`, M4 scenarios) never turns `groundVectorRedirect` on. Only `MovementConfigs` sets it.

## 6. Build, smoke, changed trajectories

Build: `-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M10\HSD-Practice.exe`, exit 0. The build re-serialised
`Scenes/Practice.unity` and `ProjectSettings.asset`, and rewrote the line endings of the two config assets; all of these were reverted.
The ignore-cr stat equals the plain stat (3 files, +154 / −2). No CR in the committed .cs.

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 238/238 verdicts as expected (119 SUCCESS at shift 0, 119 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16, M9-C 14/14,
M10-A 14/14, M10-B 18/18, M10-C 20/20, M10-W 16/16); course lap 78.98 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok
(26 fields, 2129 bytes); 130646 commands in total
```

- All 476 smoke demo lines are identical to the M10-W build's. The M5.5 route ends at the same place.
- I hashed every command (position, velocity, buttons, lurch, events) of every demo run: all 119 demos, at shift 0 and at the failure shift.
  Fixed vs unfixed motor: 236 / 238 runs are identical. The 2 that differ keep their verdict text:
  - `m7_djump_gap`, failure shift: after falling into the gap, the body lands moving −99 u/s against the held W. That now brakes at
    D + low acceleration (−99 → 8 in 4 commands) instead of at the low acceleration alone.
  - `m10w_drop_long`, failure shift: the same case at −48.5 u/s (2 commands).
- **Course lap 80.55 → 78.98 s** (−1.57 s). The same change shows in all 6 config × loadout laps. Cause: the defect itself.
  - At stage "M tower top" the course autopilot walks to a 12 u stop radius and overshoots. It then holds W pointing back at the target,
    which is almost exactly opposite the motion.
  - Before the fix it took 132 commands (1.1 s) against its own velocity to turn around. Now it takes 27 commands (0.225 s).
  - Every stage before that one is identical. Every later stage shifts by the same 1.567 s. Timeouts: 0. Checkpoints: 7/7.
  - The lead's expected figure of 80.55 included the defect.

## 7. Open

- R5 has no recording of a reversal. The braking law (1250 u/s² + band acceleration along the wish) is the M5 friction-vector model
  extended to the antiparallel case: **[model]**, not measured. A quick R5 check would settle it: sprint, then S, then a 180° snap.
- 「真人手感未验收」: not playtested.
