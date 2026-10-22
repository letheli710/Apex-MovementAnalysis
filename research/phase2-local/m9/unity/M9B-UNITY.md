# M9-B in HSD-Unity: Revenant (Shadow Pounce + long climb) and the D1 mantle duration

- Branch `m9b/revenant` of HSD-Unity (commit `7a72289`), from main `2ea2a4f` (M8 merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M9-PLAN.md](../M9-PLAN.md) items B1–B3 and D1 (90 u mantle). Evidence: [../../m8/r2_revenant/REVENANT-CLIMB.md](../../m8/r2_revenant/REVENANT-CLIMB.md) (+ `params.json`), [../../m4/valk_rev/VALK-REV-PRIMITIVES.md](../../m4/valk_rev/VALK-REV-PRIMITIVES.md) §3, [../../m8/r_sg/SG.md](../../m8/r_sg/SG.md), [../../m6/a2_climb/A2-CLIMB.md](../../m6/a2_climb/A2-CLIMB.md), track D [../d_library/TECHNIQUE-LIBRARY.md](../d_library/TECHNIQUE-LIBRARY.md) §3.17–3.18 (relayed by the lead). Playtest guide (Chinese): [../PLAYTEST-GUIDE-M9B.md](../PLAYTEST-GUIDE-M9B.md).
- Track R's M9 Revenant measurements (pounce grid, smooth-face end rule, lateral input, exits) had not arrived when this was built. Every value they may refine is a parameter (§3.3, §9) and is listed as a gap (§8).

> **Acceptance status (three separate labels)**
> - **「数值/规则测试通过」** (numbers and rules): the pounce formula, the charge timing, the 0.85 s climb lock, the speed line, the mantle heights, the release / back / jump exits, the D1 mantle times and the bit-identity of every other body are unit-tested; every R5 replay is identical; every older demo verdict, the M5 route and the course lap (80.82 s) are unchanged (§6–7).
> - **「真实按键演示通过」** (real-input demos): 7 M9-B demos, each with a failure variant, pass through the normal command loop (smoke `M9-B 14/14`).
> - **「真人手感未验收」** (human feel): nobody has played it. The end rule, the 0.85 s lock feel, the Fun wall launch and every [design] value are open.

Labels: **[meas]** R5 S21 measured (M4 / M8 track R2 unless noted), **[fit]**, **[src]** S21 script source, **[lib]** community source (track D), **[inf]**, **[design]** an HSD choice.

## 1. Audit (before the build)

| Area | What existed | Gap | Decision |
|---|---|---|---|
| Pounce formula | `InstantImpulse.PounceLaunch` / `PounceAbility` (M4): v = (700 + 450c)·forward(pitch − 35°), c from the release, 0.9 s pull-out, high-angle fade, ground check | checked line by line against the source rules (VALK-REV §3.5) and track D's script constants (35°, −15°, 75°, 20° / 200 u → 15°, 0.9 + 1.3 s): **all equal** | unchanged; an independent re-statement is tested at 14 pitch / charge cases × 3 yaws (§2) |
| Charge timing | release before 0.9 s → launch at the pull-out end, c 0; later → next command | matches M4 (c13: launch 1.308 s, 839.1 u/s) | unchanged; game bodies auto-fire at 2.2 s (M5 [design]) |
| Full charge in the game | the 900 u/s rule ceiling cut a full-charge pounce (942 horizontal) | a [src] value clipped by a design cap | Revenant bodies get a 960 ceiling [design] |
| disable_wall_run | not modelled | [src] while charging + 0.75 s; R5 climb 0.855–0.89 s after the release [meas] | `IWallRunBlocker` on the pounce; blocks climb / hang / wall-run starts (§3.4) |
| Lurch after a pounce | the M5 rule: any launch opens the window | no evidence that a pounce is a jump; track D: the community pounce tap strafe is "hold Q → jump → release → strafe" (S18+, in S21) | Reference Revenant: the launch opens no window (the jump in the recipe does, and it works, tested); Fun keeps the M5 rule [design] |
| Landing | move scale 1.15 restored on the landing command | [meas] restored 6–14 commands after the touchdown | 0.083 s hold on Revenant bodies |
| Long climb | the generic M6-A climb (k 1.735, end z_ref + 147.06, contact detach 1.0 s, 4 s arbiter guard) | Revenant needs another speed line, end, release rule and guard; a 7 s climb would hit the 1.0 s detach and the 4 s guard | a per-legend **profile** written onto the body's own copy of the generic climb parameters (§3) |
| Revenant preset | M5 "Revenant-Wraith ground" (pounce + wraith phase + portal), used by the smoke route and older tests | changing it would change older routes / demos | **new preset "Revenant"** (pounce only, `legend = "revenant"`), key −; the M5 preset keeps the M4 / M5 model |
| Mantle 90 u (D1) | Unity 0.531 s vs R5 0.418 s (M8-B report) | — | test artefact, not a model error (§5) |

## 2. B1 Shadow Pounce

### 2.1 Measured / source vs implemented

| Rule | Evidence | Unity | Class |
|---|---|---|---|
| Speed (700 + 450c), elevation view − 35° at pitch −15…75 | M4 at pitch 0: 35.000°, 701.2 (c 0), 839.1 (c 0.309); [src] | `PounceLaunch`, exact | [meas] at 0°, [src] elsewhere |
| High angle: raise fades 35 → 0 and speed ÷ 1 → 1.5 over −15…−80 | [src] | same (test: −50° → 607.0 u/s, 66.2° up) | [src] |
| Looking down ≥ 20° with ground ≤ 200 u along the view → 15°; cap 75° | [src], [lib] | same (flat floor of the motor) | [src] |
| Pull-out 0.9 s, charge 1.3 s, c from the release | M4: tap / 0.6 s → 0.908–0.917 s; c13 → 1.308 s | tap 0.900, 0.6 → 0.900, 1.3 → 1.308 (c 0.3077), 1.55 → 1.558 (c 0.5), held → 2.200 (c 1) | [meas] / [design] auto-fire |
| Velocity replaced | [src] | the side speed before the launch is gone (test) | [src] |
| Flight ballistic, g 750, no drag; air time 129–131 cmds (c 0) | M4 | 126–131 band (Unity 128) | [meas] |
| Soft landing (no slowdown), ground friction | M4 | no `LAND_SLOW`; > 560 u/s after the touchdown | [meas] |
| Move scale 1.0 from the press to the landing, restored 6–14 cmds later | M4 | 1.0 from the press; Revenant bodies 0.083 s hold (10 cmds); M5 preset unchanged | [meas] |
| Mid-flight collisions | — | world collision (a slab 140 u up: the rise stops under it, the flight goes on and lands) | [inf] |
| Release / cancel | release before the pull-out cannot cut it short [meas]; no player cancel measured | an arbiter interrupt cancels the charge without a launch (a held button does not re-arm it) | [meas] / [design] |
| Lurch window | the R5 window is anchored on the last jump [meas M6-A1]; pounce TS recipe [lib] | Reference Revenant: no window from the launch; hold Q → jump → release → D + W taps lurches on the pounce (test, both configs); a jump after the release does nothing (Reference). Fun: the launch opens the window [design]. The Sep-2024 pounce-TS angle limit (post-S21) is not modelled | [inf] + [lib] |

Pounce ranges on flat ground (pitch 0 unless noted; Unity): c 0 → 616 u in 1.067 s, c 0.5 → 1080 u, c 1 → 1664 u (942 / 659.6), pitch −15 tap → 649 u, pitch +15 tap → 422 u, pitch −50 tap → 301 u.

### 2.2 Combos

- **Pounce → slide**: crouch held before the landing → slide on the landing command at 573 u/s, 434 u/s 0.5 s later (demo `m9b_pounce_slide`, test in both configs). Crouch 0.53 s after the landing: friction has already stopped the body.
- **Pounce → air turn**: see the lurch row above (`ThePounceTapStrafeRecipeWorksBecauseTheJumpAnchorsTheWindow`, `APounceIsNotAJumpInReferenceTheFunConfigLurches`).
- **Pounce → wall**: §3.4.

## 3. B2 Revenant long climb: a profile on the generic climb

### 3.1 Design

- `ClimbParams` got the profile hooks, every default equal to the M6-A climb: `speedLineAnchor` / `endAnchor` (Takeoff | Contact), `maxClimbTime` (0 = off), `slideClock` (SinceContact | SinceRelease), `climbJump` (Bounce | WallLaunch) and the launch values. `ClimbAbility` reads them; with the defaults every expression is the old one (same operands, same order).
- `ClimbProfile` (`Traversal/RevenantProfile.cs`) holds the values a legend changes; `ApplyTo` writes them onto the body's own copy of the config's climb (`advanced.climb`). Everything else (contact step, 490 accel, mantle reach and traversal, superglide, side drift, back key, bounce vector) stays generic.
- `RevenantParams` on `MovementConfig.revenant` (Reference `Measured()`, Fun `Fun()`): the profile, the pounce lock, the lurch rule, the landing hold, the climb arbiter guard (+9 s) and the horizontal ceiling. `CreateBody` applies it only when the loadout's new `legend` field is the profile's ("revenant"); `Apply` copies the legend and adds the guard / ceiling for that body.
- **Proof that other bodies are untouched** (tests, §6): every older preset in both configs has the generic climb fields; trajectories of all four older presets over eight climb scenarios (H90 mantle … side key, with the tactical pressed) are **bit-identical** with and without the Revenant set; the Revenant body with `ClimbProfile.Generic()` is bit-identical to a body without the set; all M6-A / M7 / M8 climb tests unchanged; replays identical (§7).

### 3.2 Measured vs implemented (Reference)

| Rule | R5 (r2_revenant) | Unity | Class |
|---|---|---|---|
| Start | airborne W into the face (generic) | generic | [meas] |
| Speed line | vz = 0.0921·(Z0 − z); Z0 − z_contact ≈ 2493 (sprint), 2498 / 2480 (pounce) | k 0.0921, Z0 = z at the climb start + 2493 | [fit] |
| Profile | peak 225.97 at ~95 u; 207 at 300; 188 at 500 | 225.4 at 98.6; 206.8; 188.3 | [meas] |
| Mantle on top | 300 / 500 / 800 mantled; climb 0.90 / 1.91 / 3.63 s (stacked rocks, joint losses) | 0.867 / 1.842 / 3.492 s; 1200 → 6.18 s; on top at every height | [meas] (Unity 4 % faster: no joints) |
| End | 2 of 3 clean ends: jump-up at floor + 1246.6 after 7.38 / 7.44 s; 1 at 1112 / 7.21 s after a re-climb; creep without end after an impact | jump-up at z_takeoff + 1246.6 (1600 wall: 7.19 s, z 1249.3); time guard 9 s | value [meas n 2], **rule [design]** |
| Jump-up | dvz +144.5 / +146.0 | jumpUpDvz 150.1 with the generic −584·dt → +145.2 at 120 fps | [meas] |
| No contact clock | W held 12 s: no detach | `detachAfterContact` 1e9 | [meas] |
| Release W | climb ends 0–0.18 s later (mean 0.125, n 24), no hang, falls | slide on the release clock, detach + 69.97 out at 0.125 s | [meas] / slide ramp [design] |
| Back key | — | generic back detach 0.060 s | [design] (generic) |
| Side key | unmeasured for Revenant | generic measured drift (113·(1 − v/102.6)) | [design] |
| Climb jump | unmeasured for Revenant ([lib]: "Revenant always gets a mini-bounce") | Reference: M3 bounce (Gibraltar-measured). Fun: wall launch (Sparrow [meas]: post vz 670.82 − g·dt/2, 442.8 out, rise ≈ 300, once per landing) | [inf] / Fun [design] |
| Arbiter guard | — | climb row 4 + 9 s (+ hang time in Fun) | [design] |

### 3.3 Parameters track R may refine (all on `ClimbProfile` / `RevenantParams`)

`speedLineK`, `speedLineZ0`, `speedLineAnchor`, `endHeight`, `endAnchor`, `maxClimbTime`, `detachAfterRelease`, `slideClock`, `jumpUpDvz`, `climbJump` (+ launch values), `pounceWallRunLock`, `pounceOpensLurchWindow`, `pounceLandingMoveScaleHold`. A smooth-face end rule plugs in as `endHeight` / `endAnchor` / `maxClimbTime` without code changes; a speed-threshold end would need one more field.

### 3.4 The climb lock and its arbitration

| Situation | Unity | Evidence |
|---|---|---|
| Pounce (d150, pitch −15) reaches the face 0.342 s after the launch | `CLIMB_LOCKED` (once per lock); the body keeps flying up the face | R5 contact 0.333–0.343 s [meas] |
| Lock end while still touching | climb starts 0.850 s after the launch (Reference) / 0.750 (Fun) | R5 0.855–0.89 s = 0.75 [src] + ≤ 1 server tick [meas] |
| Pounce d500: face after the lock (1.117 s) | climbs at the contact | R5 contact 1.108 s, climb 0.083 s later (gap) |
| Charging at a wall | no climb start | [src] |
| Ledge hang (M7-A) during the lock | refused (it replaces a climb start) | [design] |
| Wall-run (M7-A) during the lock | refused | [design] from the flag name |
| Space at the wall during the lock | the M5 base-layer wall jump (no climb to bounce from) | [design] |
| Mantle during the lock | allowed (a mantle is not a wall-run) | [inf] |
| Normal climb | once per airborne phase, generic | [meas] |
| Bodies without the Revenant set | no blocker: unchanged | — |

## 4. B3 Revenant yard, preset, demos

- **Preset**: `SkillLoadouts.Revenant()` (5th, key −; pounce on Q, 1 charge × 3 s [design]), in both configs. Preset asset `Presets/Loadouts/Revenant.asset`; config assets regenerated (`PresetAssets.CreateM5LoadoutsBatch` / `CreateM5ConfigsBatch`; the older loadout assets gained the empty `legend` field only).
- **Yard Y** (`PracticeMapM9B.cs`, appended after every older block: block indices 0–72 unchanged, M9-B blocks 73–78), x 200–2900, y −1000…−300, south of lane A and north of the course strip: tall walls 300 / 500 / 800 / 1200 and a 1600 end-rule wall (faces y −800), a 600 u lock wall with 150 / 500 u tiles, a pounce range with stripes every 250 u and landing tiles (616 / 649 / 1080 / 1664). All dimensions [design].
- **Demos** (Reference unless noted; failure variant = the panel's timing shift):

| Id | Success (shift 0) | Failure (shift) |
|---|---|---|
| `m9b_pounce_charge` | Q 1.55 s → c 0.50, 925 u/s, lands 1080 u | −0.95 s: released at 0.6 s → c 0, 700 u/s, 616 u |
| `m9b_pounce_slide` | crouch before the landing → slide at 573, 434 u/s 0.5 s later | +0.9 s: crouch 0.53 s after the landing, body already stopped |
| `m9b_pounce_lock_climb` | face at 0.342 s (locked), climb at 0.850 s, climbing | −1.5 s: W released 0.6 s after the launch (inside the lock), no climb |
| `m9b_long_climb_mantle` | 1200 wall: climb 6.19 s, mantle on top | −5 s: W released 2.9 s in, no mantle |
| `m9b_long_climb_end` | 1600 wall: jump-up at z 1247.6 after 7.21 s [design rule] | −5 s: ended by the release |
| `m9b_climb_release` | W released at z 349 → off the wall 0.125 s later, falls, no hang | +3.5 s: never released |
| `m9b_wall_launch` (Fun) | launch 0.49 s into the climb: post vz 667.70, +303 u, 439 out | −0.75 s: Space before the climb, nothing |

## 5. D1 mantle duration (90 u: Unity 0.531 s vs R5 0.418 s)

**Result: no model discrepancy, no code change.** Unity's traversal time is the A2 fit T = 0.1728 + 0.0055·rise, with the rise taken where the trigger fires. R5's T0 values (r_sg: 0.418 / 0.581 / 0.602 / 0.600 / 0.587 at H90…H232; A2: 0.414 / 0.578 / 0.604 / 0.612 / 0.590) come from the A2 approach, a sprint jump ~100 u before the face: at H90 the body meets the face near the top of the jump (A2 rise 43.9 u). The 0.531 s in the M8-B report came from the M8-B superglide test helper, which searches the jump distance from 30 u and takes the first that mantles: a jump 30 u from the face reaches the face still rising, 65 u below the ledge, and the same law gives 0.531 s.

| H | Unity rise / T at the A2 approach (hull front 75 u) | R5 T0 (r_sg) | A2 T |
|---|---|---|---|
| 90 | ~43.5 / 0.412 | 0.418 | 0.414 |
| 120 | ~73.5 / 0.577 | 0.581 | 0.578 |
| 150 | ~79 / 0.608 | 0.602 | 0.604 |
| 180 | ~79 / 0.609 | 0.600 | 0.612 |
| 232 | ~78 / 0.604 | 0.587 | 0.590 |

All within 0.025 s (tested, `MantleDurationD1Tests`); the SG window is relative to the mantle end and its tests are unchanged. The remaining ≤ 0.017 s at H232 is the reach (R5 triggered at a 76 u gap, Unity ~78 u; "reach not sharp" in A2) and is left alone. No replay changed.

## 6. Tests

| Suite | Result |
|---|---|
| EditMode | **1273 / 1273** (main 1152; +121) |
| PlayMode | 1 / 1 (the smoke in the game loop, now also requiring `M9-B 14/14`; frame limit 160000 → 220000) |

New:
- `R5MotorM9BTests` (R5Replay): `PounceM9BTests` 34 cases — the formula vs an independent source re-statement (14 cases), charge / launch timing through the body (5), velocity replaced, ground check and high-angle fade, ballistic flight + soft landing, the landing move-scale hold (and the M5 preset unchanged), lurch rules (Reference / Fun / M5 preset), the pounce tap-strafe recipe (2), pounce → slide (2), ceiling mid-flight, lock d150 (Reference / Fun timing), d500, charging blocks the climb, the M4 pounce unchanged (report keys, no blocker), interrupt cancels the charge. `RevenantClimbM9BTests` 21 cases — only the Revenant preset gets the profile (2), the generic profile is a no-op (2), every older preset bit-identical with / without the set (2), speed line, top mantles 300 / 500 / 800 / 1200, the end near 1250, the time guard, release W, back key, climb jump (Reference bounce / Fun launch), launch once per landing, side drift, guard + ceiling, the lock blocks hang and wall-run, a jump inside the lock is the generic wall jump. `MantleDurationD1Tests` 6 cases.
- `M9BGameTests` 4: preset and the Revenant set in both configs, the yard appended after every older block, demo coverage (M9-B last), the feedback station name.
- 7 demos in every demo suite and 7 failure cases in `EveryDemoFailsWithItsFailureShift`.

Existing tests changed (each keeps its intent):
- `SkillLoadoutTests.PresetsHaveThreeToFourValidSlots`: the single-legend Revenant preset has 1 slot.
- `PhaseBreachTests.AshRouteLoadoutIsValid`: 5 presets; Ash stays index 3.
- `M8BGameTests.ChainYardIsAppendedAfterEveryOlderItemInFreeGround`: the M8-B anchor is the last block before the M9-B yard.
- `M8CGameTests.TheM8CDemosCoverItems8And9`: the M8-C demos come last before the M9-B demos.
- `PracticeGameTests.ConfigAssetsEqualTheFactory`: also the Revenant set and the new climb fields.
- `MovementDemoTests`: 7 failure cases; the simulation-write scan includes `MovementDemosM9B.cs`.
- `M6CourseTests` fuzz: the older demo pool excludes `m9b_` (the fuzz episodes are unchanged).
- PlayMode smoke test: `M9-B 14/14`, frame limit 220000.

## 7. Regression (default replay motor; outputs in a scratch folder outside the repositories)

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 (`-motor both`) | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 (`-motor v2`; includes the wall / mantle trials) | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `m4_replay_check.py --base m4_replay`) | `m5/unity/m4_replay` | **114 identical**, 0 different, 0 missing (incl. every `m4_pounce_*`) |

No replay preset changed: the pounce's M9-B fields are `[NonSerialized]` and neutral by default (its report parameter list is asserted), the climb is not in the replay kit, and D1 changed no code.

## 8. Build and smoke

Build: `HSD-Build/M9B/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M9B\HSD-Practice.exe`), exit 0. The re-serialised `ProjectSettings/ProjectSettings.asset` and `Scenes/Practice.unity` were reverted (`git checkout --`); `git diff --stat --ignore-cr-at-eol main` equals the plain stat (37 files, +1729 / −29); no CR in the committed .cs blobs.

Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 140/140 verdicts as expected (70 SUCCESS at shift 0, 70 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14); course lap 80.82 s
(7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2111 bytes); 74338 commands in total
```

The 126 older demo lines are identical to the M8-C build's smoke output (diffed). The feedback byte count varies with the timestamp.

## 9. Open gaps

- **End rule** of the long climb (track R, smooth tall face): height 1246.6 above the takeoff [design rule on n = 2 values]; time ≈ 7.2–7.4 s and a speed threshold ≈ 113 u/s are not excluded; the creep without end after an impact is not modelled.
- **Climb start after the lock**: R5 d500 climbed 0.083 s after the contact; Unity climbs at the contact. After a d150 lock the climb starts from the pounce's falling speed (vz −92) with the generic 490 u/s² — the R5 vz there is unmeasured.
- **Revenant climb jump**: unmeasured; Reference uses the M3 bounce, track D reports "always a mini-bounce" [lib]; Fun's wall launch uses Sparrow's numbers [design for Revenant]; the ledge-aware launch height is untested.
- **Lateral climb input, re-attach floor (×9 [lib]), obstacles on the face**: generic drift only; no re-attach rule.
- **Pounce grid** (pitch / charge / start speed, from the wall, in the air, full charge 1150): only pitch 0 at c ≤ 0.31 is measured; the rest is [src]. Pounce TS vs the 1100 lurch cutoff (horizontal ≤ 942, never reached).
- **Mid-climb pounce**: the charge does not detach an ongoing climb ([design]); the launch interrupts it (arbiter).
- **M5 "Revenant-Wraith ground"** keeps the M4 / M5 pounce and the generic climb (bit-identical older routes); whether it should get the Revenant set is a lead decision.
- D1 residual ≤ 0.017 s at H232 (mantle reach).
- Every [design] value is 「真人手感未验收」.

## 10. Design-value list (new in M9-B)

| Mechanic | Parameter | Reference | Fun |
|---|---|---|---|
| End rule | `endHeight` / `endAnchor` | 1246.6 / takeoff ([meas] value, rule [design]) | same |
| Climb guard | `maxClimbTime` | 9.0 s | same |
| Release slide | `slideClock` | since the release | same |
| Side key | generic drift | 113 / 102.6 | same |
| Climb jump | `climbJump` | Bounce | WallLaunch (670.82 / 442.8) |
| Lock | `pounceWallRunLock` | 0.85 s (0.75 [src] + tick [meas]) | 0.75 s |
| Lock scope | hang / wall-run / generic wall jump | blocked / blocked / allowed | same |
| Lurch after a pounce | `pounceOpensLurchWindow` | false | true |
| Landing hold | `pounceLandingMoveScaleHold` | 0.083 s ([meas] 6–14 cmds) | same |
| Arbiter guard | `climbGuard` | +9 s | same |
| Ceiling | `horizontalCeiling` | 960 u/s | same |
| Preset | Revenant, pounce 1 × 3 s, key − | | |
| Yard Y | wall heights, tiles, range | | |
| Pounce auto-fire | 2.2 s (M5) | | |
