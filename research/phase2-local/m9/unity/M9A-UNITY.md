# M9-A in HSD-Unity: zipline interaction fixes (A1) and technique validation (A3)

- Branch `m9a/zipline` of HSD-Unity (commit `1c1824b`), from main `e0e620b` (M9-B merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M9-PLAN.md](../M9-PLAN.md) items A1 and A3. Evidence: track R [../r_zip/ZIPLINE-A1.md](../r_zip/ZIPLINE-A1.md) + `params.json` (lead-verified), M6 [../../m6/a3_zip/A3-ZIPLINE.md](../../m6/a3_zip/A3-ZIPLINE.md), [../../m6/a3_zip/GRAPPLE-ZIP.md](../../m6/a3_zip/GRAPPLE-ZIP.md), M8-A [../../m8/unity/M8A-UNITY.md](../../m8/unity/M8A-UNITY.md) §zipline, track D [../d_library/TECHNIQUE-LIBRARY.md](../d_library/TECHNIQUE-LIBRARY.md) §3.13–3.16, §5, §6. Playtest guide (Chinese): [../PLAYTEST-GUIDE-M9A.md](../PLAYTEST-GUIDE-M9A.md).
- Track R's lurch measurements (R-1 / R-4 / R-5 / R-6 / R-10) had not arrived: those specs are tested against the current model and marked **[model]** (§6).

> **Acceptance status (three separate labels)**
> - **「数值/规则测试通过」** (numbers and rules): every R5 r_zip finding that Unity models is unit-tested (§3, §7); every R5 replay is identical; the M5 route, every older demo verdict text and the course lap (80.82 s) are unchanged (§8, §9).
> - **「真实按键演示通过」** (real-input demos): 8 M9-A demos, each with a failure variant, pass through the normal command loop (smoke `M9-A 16/16`, §9).
> - **「真人手感未验收」** (human feel): nobody has played it. The mount hint, the 0.35 s lockout feel, the Fun choices and every [design] value are open.

Labels: **[meas]** R5 measured (m9/r_zip unless noted), **[fit]**, **[src]** source / wiki, **[inf]** interpretation, **[model]** the current Unity model's output (no R5 result yet), **[design]** an HSD choice.

## 1. The user's report: reproduced, root causes

Reproduced on the practice map before any change (main `e0e620b`, scratch harness through `PracticeSession`, the default config = Reference; every map rope, standing at 6 / 25 / 50 / 75 / 97 % of its length, six views; then dismount-and-re-mount).

| Candidate cause | Finding (evidence) | Verdict |
|---|---|---|
| **Reference refused every air mount** (`ZiplineParams.airMount = false`, the M6-A3 choice after one dedi refusal at 120 u) | Jump-off or crouch-off mid-rope, X in the air 5 / 20 / 45 / 60 commands later: `ZIP_REFUSED_AIR` every time; only a ground press after landing mounted. R5 r_zip: air mounts 65/65, refused only within ~0.33–0.40 s of a detach | **Root cause 1** ("can't re-mount after a mid-rope dismount"; no Mid Air Interact) |
| **M8-A end refusal** (`refuseMountAtEnd = true`) | Standing near an end and looking at it (or looking up near it): `ZIP_REFUSED_END` (flat rope 6 % looking back, 97 % looking up / beside). R5 has no end refusal: it reverses the ride | **Root cause 2** ("only some spots work near the ends") |
| Rope height vs reach (map geometry) | The two 130 u ropes (M6 flat, M8-B yard) mounted standing at every point with the view along / at the rope. The sloped ropes (uphill 130 → 530, course yard 130 → 380) are 193–518 u above the floor beyond their first ~10–25 %; the high line (400–520) and the grapple rope (420) never: all `ZIP_NO_ROPE`. R5: ropes 200 / 240 u above the floor are never mountable standing | **Root cause 3** — geometry consistent with R5, not a code bug (the "only at the start" impression on sloped ropes) |
| No prompt / target hint, view across the rope | Standing under the rope with a level view across it: refused (R5 too, 90°); beside it with a level view: refused (R5 too). The game had no interact prompt; the use key is X (Apex: E) | **Contributing cause 4** (the player cannot see whether a press would mount) → prompt + grip marker added |
| `Rail.attachRadius = 48` (WorldGeometry.cs) | Only sets `RailHit.attachable` in `ClosestRail`; nothing in the zipline reads it (the grapple handoff uses `hookRadius`) | Not a cause (unchanged) |
| Find radius 130 vs the measured ~120 reach | Unity had no 120 u collector, so it was *more* permissive (128 u ropes mounted) | Not a cause; now modelled (`collectorRadius 120`) |
| Cone 34° | Inside the new bracket 33.2–35.9° | Not a cause (kept) |
| Camera eye (60) vs Find origin (+72) | Same view angles; aiming the crosshair from the eye at a rope point within reach mounts at that point (test `TheHintIsTheUsePress`, 12 offsets) | Not a cause |

## 2. Measured vs implemented (Reference)

| R5 finding (r_zip) | Before M9-A (Reference) | M9-A Reference | Evidence / test |
|---|---|---|---|
| Mid-rope standing mount anywhere, grip = min-angle point within 130 u of origin+72 | same Find (worked under 130 u ropes) | unchanged + collector | [meas] / `MidRopeStandingMountsAnywhereAlongTheRope` (7 positions) |
| Cone 33.2° < θ < 35.9° | 34° | 34° [design inside] | [fit] / `ConeBracketMatchesTheR5Bracket` |
| Reach: rope within ~120 u of origin+72 (115.6 ok, 128 refused) | none (130 sphere only) | `collectorRadius 120` | [fit] / `CollectorReachIs120FromTheSearchOrigin` |
| Heights: 100 / 130 mount, 170 looking up, 200 / 240 never | same except 200 (P→rope 128) partly mountable looking up | same as R5 | [meas] / `RopeHeightsAboveTheFloor` |
| 80 u rope never mounts (cause unknown) | mounts | mounts | **gap** (§10) |
| Beside the rope: view must be on the rope; level across refused; 120 u to the side never | same | same | [meas] / `BesideTheRopeTheViewMustBeOnTheRope` |
| Direction = sign(view · rope dir), ≤ 0 → toward the start, 5° flips; sloped: same | flat yaw · tangent, ≥ 0 → toward the end; air mounts with the momentum | 3-D view · tangent, ≤ 0 → start, air mounts by view | [meas] / `RideDirectionFollowsTheView`, `MidAirInteractGrid` |
| Direction fixed for the ride | fixed | fixed | [meas] / `TheDirectionIsFixedForTheRide` |
| **No end refusal**: grip within ~90 u (70–110) of the end you face rides away; 110 u rides into the stop-short, detaches at 600 from rest | refused within 90 u (`ZIP_REFUSED_END`) | `endZoneReverse`, `endZone 90` | [meas] / `EndZoneReversesInsteadOfRefusing` (50 / 70 / 110) |
| **Air mount / Mid Air Interact works** (65/65, 20 / 40 / 80 u, 0 / 45 / 80°, no height gate) | refused | `airMount = true` | [meas] / `MidAirInteractGrid` (9 cells), demo `m9a_midair_interact` |
| **Air re-mount refused ~0.33–0.40 s after any detach**; ground immediate | (air refused always) | `airRemountLockout 0.35` [design inside], anchored on `detachTime` (every exit; the super jump is not a detach) | [meas] / `AirReMountLockout` (jump-off 0.30 ✗ / 0.37 ✓, crouch-off 0.30 ✗ / 0.41 ✓), `GroundReMountIsImmediate…`, demo `m9a_air_remount_lockout` |
| Re-grab: ground + 2 air, the 3rd refused, landing resets | budget 3 [src] (same count) | unchanged | [meas] / `ReGrabBudgetGroundPlusTwoAir`, demo `m9a_regrab_budget` |
| Super jump mid-rope; 2nd press K 12 / 18 5/5, 24 3/5, 30 0/5 | 0.2 s from the mount | unchanged: K ≤ 23 ✓, K ≥ 24 ✗ (on the measured edge) | [meas] / `SuperJumpSecondPressWindow`, demo `m9a_midrope_superjump` |
| **No lurch window after the jump-off** (\|Δv\| 4.18) | jump-off = lurch anchor [design] | `jumpOffIsLurchAnchor = false` | [meas] / `JumpOffOpensNoLurchWindowInTheReference` |
| **Carry**: jump on the next command keeps the run velocity (0, 285, 289.8); 2 commands later rope-aligned 8.3 | (0, 0, 289.8) | `firstCommandCarry`: first ride command exit = pre-mount horizontal (cap 400 [src wiki]) | [meas] / `CarryKeepsThePreMountVelocityOnTheFirstCommand`, demo `m9a_carry` |
| **Entry speed carried** (sprint 299.7, slide 395, then the normal curve: 503.6 / 597.3 at 1.0 s) | ground mounts from rest | `groundEntrySpeed` (the speed along the ride = the mount-state floor) | [meas] / `GroundEntrySpeedIsTheMountStateFloor` |
| Crouched / sliding, level view 0/5, 45° up 5/5 | mounted | `crouchFindRaise 50` [inf: crouched eye 38 vs 60] | [meas] / `CrouchedLevelViewIsRefusedLookingUpMounts` |
| Vertical, mid height: level / up → up; turn down after the mount keeps up; air mount up | up | up | [meas] / `VerticalRopeMidHeight` |
| Vertical, looking down: client mounts, S3 dedi never dispatches | rode up | **Refuse** [design: the dedi result; unresolved for S21] | [meas, hybrid] / same test, demo `m9a_vertical_midheight` |
| Vertical jump-off: 400 along the view yaw + 289.8 | same | same | [meas] / same test |
| Grapple handoff (GRAPPLE-ZIP) | momentum, refused in the end zone | unchanged (end-zone refusal kept for the handoff [design], unmeasured) | — |

## 3. Changes per config

`ZiplineParams` (R5Replay/Runtime/Traversal/ZiplineAbility.cs) defaults = Reference; `ZiplineParams.Fun()` is the Fun config's rope (`MovementConfigs.Fun` uses it). The preset assets `ReferenceConfig.asset` / `FunConfig.asset` were regenerated (`PresetAssets.CreateM5ConfigsBatch`).

| Parameter | Reference | Fun | Label |
|---|---|---|---|
| `airMount` | **true** (was false) | true | [meas] |
| `airRemountLockout` | **0.35 s** | 0 | Ref [meas, design inside 0.33–0.40]; Fun [design: the 3-mount budget is the only limit, fast juking] |
| `airRideWithMomentum` | false (view) | true (M6-A) | Ref [meas]; Fun [design] |
| `endZoneReverse` / `endZone` | **true / 90** | false | Ref [meas]; Fun [design] |
| `refuseMountAtEnd` | **false** (was true) | true (M8-A) | Fun [design: no 600 u/s launch from rest] |
| `jumpOffIsLurchAnchor` | **false** (was true) | true | Ref [meas]; Fun [design] |
| `groundEntrySpeed` | **true** | true | [meas] |
| `firstCommandCarry` | **true** | true | [meas] + cap [src] |
| `collectorRadius` | **120** | 120 | [fit] |
| `crouchFindRaise` | **50** | 50 | [inf] |
| `verticalDown` / `verticalDownPitch` | **Refuse** / 20° | RideDown / 20° (lets go 90 u above the foot) | [design] both (R5 unresolved) |
| direction tie / 3-D view | ≤ 0 → start | same (ground mounts) | [meas] |

New API: `ZiplineAbility.Evaluate(motor, yaw, pitch, now)` returns a `ZipMountChoice` (rope, grip, direction, reversed, refusal) without side effects; the use press and the HUD both call it. New events `ZIP_REFUSED_LOCKOUT`, `ZIP_REFUSED_DOWN`, `ZIP_CARRY`; `ZIP_REFUSED_AIR` now only appears if a config turns `airMount` off.

**Game (visual layer only):** `AbilityVisuals` evaluates the mount rule each frame for the current aim and draws a green ball on the grip and a 60 u arrow along the ride direction; `PracticeGame.ZipPrompt` writes "X 上索 zipline" above the crosshair (green), or the reason (orange: lockout countdown, no re-grabs left, end zone (Fun), vertical down (Reference)). Shown with the aim-aid toggle (`Visuals.grapple`). Never read by the simulation.

## 4. Practice map (zipline yard Z, appended after every older item)

`PracticeMapM9A.cs`, `BuildM9A` after `BuildM9B`: blocks 79–80, ropes 8–9, decals after every older one; nothing older moved (the M5 route, the course and its ropes, every index and surface id unchanged).

- **Markers under the M6 flat rope (130 u)**: tiles at 25 / 50 / 75 % (mid-rope spots) and 90 u strips at both ends (end zones).
- **Z1 `m9a-air`**: flat rope 200 u above the floor, x 6000…9000, y 2480 (the R5 r200 height: never from standing; jump and press X), tiles every 500 u.
- **Z2 `m9a-vertical`**: (10300, 2350) z 0 → 800, with two decks whose faces are 84 u from it (R5 m9zipv geometry): west top 120 (mantle), east top 230 (climb + jump-up + mantle).
- Two station signs (Z1, Z2), also in the feedback's nearest-station list.

Map ropes outside the measured standing reach (unchanged, used by the M5 / M6-C routes or by design): `uphill` beyond ~10 %, `course-yard` beyond ~10 %, `course-highline`, `grapple-only` (test `MapRopesAgainstTheMeasuredReach`). The course lap uses the tower rope (vertical, looking up) and the high line from the tower top; both still mount the same way (lap 80.82 s).

## 5. Demos (real input, Reference; each with a failure variant)

| Demo | Success (shift 0) | Failure variant |
|---|---|---|
| `m9a_midrope_mount` | 50 % mark, turn from across to along, X: mount 1000 u from each end, ride the way the view faces | turn 0.5 s later: X while looking across → `ZIP_NO_ROPE` |
| `m9a_midair_interact` | under the 200 u rope, jump, X 0.35 s later: air mount | X before the jump (standing) → out of reach |
| `m9a_air_remount_lockout` | ride, jump off, X at +0.20 s refused (lockout), X at +0.42 s: air re-mount | 2nd X at +0.22 s → both refused, no re-mount |
| `m9a_regrab_budget` | ground mount + 2 air re-grabs, the 3rd refused (`ZIP_REFUSED_BUDGET`), ground X after landing mounts | the last X 0.26 s before the landing → refused (budget) |
| `m9a_midrope_superjump` | mid-rope mount, jump next command, 2nd jump K 18 → super jump, apex +181 u | K 30 → none |
| `m9a_endzone_rideaway` | 166 u from the start, look back level: grip ~50 u from the start → reversed, rides 1.3 s toward the end | still looking 45° up at the press: grip ~108 u → rides into the stop-short, thrown off at 600 after 0.23 s |
| `m9a_vertical_midheight` | 120 deck edge, view from 25° down to level, X: mid-height mount, up to the top in 1.56 s | still looking down → `ZIP_REFUSED_DOWN` |
| `m9a_carry` | sprint across the rope, look up, X, jump next command: exit (0, 299, 290) | jump one command later → rope-aligned 8 u/s |

## 6. Technique validation (A3, library §6)

Classes: **works** / **model missing** / **input condition** / **window too narrow** / **player error**. Nothing in the Reference lurch model changed.

| Spec | Unity result (real inputs) | Class |
|---|---|---|
| R-1b W+S held, D edge 0.10 s | one lurch, pure right, −44.3° [model] | works (R5 pending) |
| R-1a A+W held, D edge | no lurch: the input layer has one side axis, A+D collapse to "no side key", the D edge is lost | **model missing (input layer)** — pinned by `R1LurchCombos` |
| R-2 lurchless air strafe (A+D, release D) | releasing D is seen as an A press → a lurch (+59.7°) where the wiki expects none | **model missing (input layer)** — pinned |
| R-3 tap strafe 360 / 720 | measured, M8-B regression (`m8b_ts_720`, `LurchM8BTests`) | works |
| R-4 Momentumshift (slide jump, A/S/D at +4/8/12 or +6/12/18, view +90°) | 3 lurches, heading ~99° right of the view, only ~22 % of 350 kept [model] | input condition / model unconfirmed (R5 pending; the wiki gives no speed) |
| R-5 OG Ras from a walk | D, D+S, S: −115.8°, 98 % [model]; A, S, D: +235°, 63 % [model]; spacing 4–10 the same | not "straight backwards" with these orders: input condition (author key order unknown), R5 pending |
| R-6 reverse chain at other entries | camera fixed: walk 160–162°, sprint 157° (R5 156.4° [meas]), slide jump 145° / 83 % [model]; with a 90° view turn > 180° (207–239°) | works (sprint measured); others [model] |
| R-7a/b sideways / backward SG | Fun lateral superglide exists (M8-B `SuperglideExit.Input`); Reference leaves along the input (M8-B tests) | not re-tested here (no new data) |
| R-10 bunny hop above 399 | 299 from the first hop on (M3 min(v, 299)) [model]; wiki: −100 per hop | model unconfirmed above 399 (R5 pending) |
| R-11 zip jump / crouch | measured law (M6 `JumpOffLaw`, `CrouchOff…`) | works |
| R-12 carry | (0, 285, 289.8) on the next command; rope-aligned one command later | works (needs the jump on the very next command: window 1 command → "window too narrow" for most players) |
| R-13 super jump edge | K ≤ 23 ✓, K ≥ 24 ✗ | works (R5 K 24 3/5) |
| R-14 Mid Air Interact | 9/9 grid cells mount | works |
| R-15 re-grab limit | ground + 2 air, 3rd refused, landing resets; 3 s refill [src] untested in R5 | works |
| R-16 mid-rope mount, heights | 100 / 130 / 170 (up) mount, 200 / 240 never | works |
| R-17 vertical mid mount | level / up → up; down: Reference refused [design], Fun down [design] | works / [unresolved] |
| Mantle jump, gorilla, hyper jump, air dance, mantle crouch, float jump (library §3.14–3.16) | need mid-air interact (now on) + mantle cancel; not scripted | not tested (inputs [lib] only) |

## 7. Tests

| Suite | Result |
|---|---|
| EditMode | ****1398 / 1398** (main 1273; +125)** |
| PlayMode | 1 / 1 (the smoke in the game loop, now also requiring `M9-A 16/16`; frame limit 220000 → 260000) |

New:
- `R5MotorM9ATests` (`ZiplineM9ATests`, 39 cases): mid-rope positions (7), cone bracket, reach 115.6 / 128, heights, beside the rope, direction, direction fixed, end zone 50 / 70 / 110 (+ Fun refusal), Mid Air Interact grid, air lockout (4), ground re-mount + Fun no lockout, re-grab budget, super jump K 12/18/23/24/30, no lurch after the jump-off (Ref / Fun), carry (+ cap), entry speed sprint / slide, crouched / sliding, vertical mid height, `Evaluate` = the use press (300 random cases), and a **fuzz** (own random streams 91000+, both configs, 4 seeds × 30 s): per command no double mount, no stuck ride (≤ 12 s), no air mount inside the lockout, ≤ 3 air mounts per airborne phase (+1 per 3 s), ride ≤ 600, exits ≤ 600 / 400, |v_h| ≤ 900, never in a solid / below the floor, no arbiter timeout.
- `R5MotorM9ATechniqueTests` (`TechniqueM9ATests`, 15 cases): R-1, R-2, R-4, R-5, R-6, R-10 (§6).
- `M9AGameTests` (7): rules per config, the map ropes against the measured reach, the user's report on the practice map, the hint = the use press with eye-aimed views, the yard appended after every older item, demo coverage (M9-A last), the feedback station name.
- 8 demos in every demo suite and 8 failure cases in `EveryDemoFailsWithItsFailureShift`.

Existing tests changed (each because the R5 r_zip data contradicts the old Reference rule, or because the map / demo list grew):
- `A3Zipline.NoAutoAttachAndNoAirMountInTheReference` → `NoAutoAttachAndTheReferenceAirMount`: the Reference air press now mounts (R5 air_mount 65/65).
- `A3Zipline.JumpOffLaw` (5 cases): the jump-off is no longer the lurch anchor in Reference (R5 lurch_after_jumpoff |Δv| 4.18).
- `ZiplineM8Tests.AirMountOnlyInFun…` → `AirMountInBothConfigsAndFunKeepsTheMomentumWithoutALift`: Reference accepts (R5 air_mount).
- `M6BGameTests.JetsMeetTheZiplinePerConfig(0)`: Reference now mounts during the jets (R5 air_mount).
- `M6CourseTests.PadAirMountRespectsTheRopeCaps`: the Reference pad air mount is accepted, under the same 600 / 400 caps (R5 air_mount).
- `M6CourseTests.CourseLies…`, `M8GameTests` M8-A ramps test, `M6GameTests.EveryMapRopeMountsFromItsStart`: the "4 station ropes" filter also skips `m9a-` ropes.
- `M8BGameTests.ChainYard…`, `M9BGameTests.TheRevenantYard…`: the M8-B rope / M9-B blocks are the last before the M9-A items.
- `M8CGameTests`, `M9BGameTests` demo order: the M9-A demos now come last.
- `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: 8 M9-A failure cases.
- PlayMode smoke test: `M9-A 16/16`, frame limit 260000.

Existing tests checked unchanged: `BudgetThreeAirMountsResetOnLanding` and `QuickRemountAfterAJumpOffAndTheBudget` (Fun, no lockout), `AMountInsideTheEndZoneIsRefused…` (Fun keeps the refusal), the grapple handoff tests, `ConsecutiveJumps…`, every course / random-play test.

## 8. Changed demo

- **`m6c_grapple_highline`** (grapple → handoff → ride → jump-off → lurch) moved from Reference to **Fun** (config 1): in R5 a zipline jump-off opens no lurch window, so the Reference config has none and the demo's lurch could not happen there; Fun keeps the jump-off anchor as a [design] value. Its verdict text is unchanged (SUCCESS, same numbers); smoke M6-C stays 14/14. No other older demo changed: every older verdict line is identical (diffed).

## 9. Regression and smoke

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 (`-motor both`) | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 (`-motor v2`) | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `m4_replay_check.py --base m4_replay`) | `m5/unity/m4_replay` | **114 identical**, 0 different, 0 missing (M4 has no zipline trials; the replay kit has no zipline) |

Build: `HSD-Build/M9A/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M9A\HSD-Practice.exe`), exit 0, 0 errors. The re-serialised `ProjectSettings/ProjectSettings.asset` was reverted; the regenerated preset assets (new zipline fields) are committed. `git diff --stat --ignore-cr-at-eol main` equals the plain stat (31 files, +1746 / −100); no CR in the committed .cs blobs.

Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 156/156 verdicts as expected (78 SUCCESS at shift 0, 78 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16); course
lap 80.82 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2104 bytes); 79286 commands in total
```

Every older demo line is identical to the M9-B build's smoke output (diffed, incl. `m6c_grapple_highline` now in Fun).

## 10. Open gaps

- **80 u rope** (R5 0/10, cause unknown): Unity mounts it (the rope is 8 u above origin + 72). No map rope is that low.
- **Lockout source**: one 0.35 s timer for every exit; R5's crouch-off was still refused at 0.359 s (Unity accepts from 0.35 s) while the jump-off was accepted at 0.334 s.
- **Re-grab limiter**: S21 client ladder (0.1 / 0.2 / 1.0 / 3.0 / 5.0 s) vs the SDK count (3); both refuse the 3rd air re-grab, Unity keeps the count; the 3 s refill [src] is untested in R5.
- **Vertical rope looking down**: [unresolved] (hybrid client/dedi split); Reference refuses, Fun rides down — both [design]. The "force up / force off" zones (V-MokZone) are not modelled.
- **Crouched reach**: modelled as a lower search origin (+50) [inf]; the R5 cause is unknown.
- **Air-mount lift**: 0 [design]; R5 did not report it.
- **Carry cap 400**: [src wiki]; R5 only tested 285.
- **Input layer**: A+D (and W+S) collapse to one axis in `SkillInput`, so R-1a / R-2 cannot be expressed (§6); fixing it means a new input representation (not done; lead decision).
- **Lurch specs R-1 / R-4 / R-5 / R-6 / R-10**: [model] values pinned; replace with track R's numbers when they arrive.
- Grapple handoff inside the end zone stays refused in both configs [design, unmeasured].
- Every [design] value and the prompt / marker are 「真人手感未验收」.

## 11. Design-value list (new or relabelled in M9-A)

| Mechanic | Parameter | Reference | Fun |
|---|---|---|---|
| Air re-mount lockout | `airRemountLockout` | 0.35 s (inside 0.33–0.40 [meas]) | 0 |
| End zone | `endZone` / reverse / refuse | 90 u (inside 70–110 [meas]) / reverse / – | – / – / refuse (M8-A) |
| Air ride direction | `airRideWithMomentum` | view [meas] | momentum |
| Jump-off lurch | `jumpOffIsLurchAnchor` | false [meas] | true |
| Vertical down | `verticalDown`, `verticalDownPitch` | Refuse, 20° | RideDown (let go 90 u above the foot), 20° |
| Crouched search origin | `crouchFindRaise` | 50 [inf] | 50 |
| Cone | `coneHalfAngle` | 34° (inside 33.2–35.9) | 34° |
| Super jump window | `superJumpWindow` | 0.2 s (on the K 24 edge) | 0.2 s |
| Carry cap | `jumpOffCap` on the carry | 400 [src] | 400 |
| Grapple handoff in the end zone | — | refused | refused |
| Hint | ball 7 u, arrow 60 u, aim-aid toggle | | |
| Yard Z | rope 200 u, vertical 0–800, decks 120 / 230 at 84 u, floor marks | | |
