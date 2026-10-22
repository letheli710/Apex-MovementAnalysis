# M6-B in HSD-Unity: Valkyrie jets (measured model) and Ash Phase Breach (route tool)

- Branch `m6b/valk-ash` of HSD-Unity, from main `e281a3a` (M6-A + M6-C merged). Unity 6000.6.5f1, SOURCE units.
- Source of truth: [../b_legends/M6-B-REPORT.md](../b_legends/M6-B-REPORT.md) and `params.json`, plus `m4/valk_rev/VALK-REV-PRIMITIVES.md`
  and `m5/SKILL-RULES.md`. No new reverse engineering was done for this step.
- Playtest guide (Chinese): [../PLAYTEST-GUIDE-M6B.md](../PLAYTEST-GUIDE-M6B.md).
- Scope: only Valkyrie and Ash. Alter, Loba and other legends were not built. No combat and no final art.

> **Acceptance status (two separate labels)**
> - **「数值通过」**: every measured number and rule below is reproduced by automated tests. The default replay motor is byte-identical. All demos and the headless smoke pass (§6–§8).
> - **「真人手感未验收」**: nobody has played it yet. That covers the jets feel, the breach freeze and exit, the aiming UX, the camera cues and every Fun value. These are design values until the user has played them.

Labels: **[meas]** measured in R5 (M6-B); **[fit]** fitted to measurements; **[src]** S21 script / SDK constant; **[census]** setfile
census value; **[design]** an HSD choice (tunable parameter, not Apex data); **[dwe]** design within the evidence (the data allows more
than one reading and one is picked).

## 1. Two configs, kept strictly apart

- `MovementConfig` now owns its legend parameter sets: `jets` (`JetpackParams`) and `phaseBreach` (`PhaseBreachParams`).
- `CreateBody` copies them into every new body, and keeps the slot's trigger binding.
- **Reference** = `JetpackParams.Measured()` / `PhaseBreachParams.R5Reference()`: the measured values.
- **Fun** = `JetpackParams.Fun()` / `PhaseBreachParams.Fun()`: design values only, and labelled so in code, HUD text and the guide. No Fun value is presented as Apex data.
- The test `ReferenceAndFunConfigsOwnSeparateParameters` proves three things:
  - a Reference body has the measured values field by field;
  - a Fun body has the Fun values;
  - the two sets are separate objects, and changing a Fun body's parameters leaves a new Reference body unchanged.
- The M4 replay preset is a third set, `JetpackParams.R5Reference()` = the M4 model, used only by the replay (§7).

| Fun [design] | Value | Reference |
|---|---|---|
| jets thrust / with input | 2.0 / 1.8 | 1.9 / 1.7 [fit, census] |
| jets activation cost | 0.5 | 1.000 [meas] |
| jets recharge | 1.0 /s from 2.0 s after landing | 0.7494 /s from 4.43 s [meas] |
| breach freeze | 0.08 + 0.05 × frames s | 0.152 + 0.1017 × frames s [fit] |
| breach exit velocity | 0.5 × entry v_h + 150 u/s along the path | exactly 0 [meas] |

## 2. Valkyrie jets: measured vs implemented

`JetpackAbility` with `JetpackParams.Measured()` (game). Each new rule is a parameter, and its M4 value leaves the M4 step unchanged.

| Item | Unity (Reference) | Evidence | Test |
|---|---|---|---|
| Meter | 8.0 | [meas] glideDuration | `M4PresetKeepsEveryNewRuleOff` |
| Drain while thrusting | 1.000 /s | [meas] 1.0002 /s | `ContinuousHoldEmpties…` |
| Activation cost | 1.000 on the activation command | [meas] n 25 | `EveryActivationCosts…` (8 → 6.70 → 5.40 → 4.10 → 2.80 [meas]) |
| Continuous hold | the meter is empty 840 commands = **7.000 s** after the press, then a fuel stop like a release | [meas] 5/5 | `ContinuousHoldEmpties…` |
| Press with meter ≤ cost | refused | [design] (R5: no reactivation while empty [meas]) | `ReactivationNeeds…` |
| Reactivation delay | 0.25 s | [src] | `ReactivationNeeds…`, pulses |
| Stop rule | vz ≤ 265.75 (the thrust terminal at 120 Hz): vz × 0.4, then the post effect | [meas] + [src] jetpack.cpp:385-390 | `ReleaseAtOrBelow…` |
| High-speed release | vz > 265.75: no cut, **no post effect**, full gravity at once (event `JETS_OFF_*_FAST`) | [meas] 20/20 | `ReleaseAtOrBelow…`, demo B1 |
| Post effect | 0.45 g + drag 1.25e-4·v_h², ends at **3.0 s** (full g from 3.000 s; 359 low-g commands = 2.99 s) or 50 u above ground | [meas] 3.0 s + [src] probe | `ContinuousHoldEmpties…`, `LandingDuringThePostEffectEndsIt` |
| Recharge | 0.7494 /s, from **4.43 s after the landing** (clock = start of the landing command); a new activation stops it and restarts the clock | [meas] rate and delay; trigger landing vs release unresolved → landing [dwe]; `rechargeClock = Stop` option provided | `RechargeStartsAfter…`, `RechargeClockFromTheStopOption…` |
| Air recharge | allowed once the clock has run (census glideRechargeOnlyInGroundedState false) | [census], untested in R5 | `RechargeClockFromTheStopOption…` |
| Tightness sideways | 0.11 s (own decay **and** own limit, as in the SDK) | [census] (Unity had 0.14) | `SidewaysDecaysAt011…` |
| Tightness down | 0.1 s when vz ≤ 0 after the thrust | [census] + [src] | `SidewaysDecaysAt011…` |
| Flight model | unchanged (terminal 260.13) | [meas] no refit | `TerminalAndFlightModelUnchanged` |
| Landing during thrust | `JETS_OFF_LAND`, no post effect, recharge clock starts | [src] | `LandingDuringThrust…` |
| Grapple attach | ends the jets (no cut, no post effect) | [src] jetpack.cpp:419-420 | `JetsAttachedGrappleAndPadLaunchEndTheJets`, `GrapplePreemptsJets…` (M5), demo B7 |
| Pad launch | ends the jets (`launchEndsDrivers`) | [design] SKILL-RULES | same test |
| Zipline | Reference: an air mount is refused (`ZIP_REFUSED_AIR` [meas]), the jets go on. Fun: the air mount ends the jets. | [meas] / [design] | `JetsMeetTheZiplinePerConfig` |
| Climb | a climb never starts while the jets drive (M6-A rule) | [design] | `JetsAndClimbNeverStack` (M6-C), demo B1 |
| Breach | the breach start ends the jets; the exit is at rest | [design] | `TravelEndsJetsAndLocksOtherSlots` |

HUD:
- The fuel bar has a tick at one activation cost. It turns red when the meter is not above the cost.
- The text shows `-1/use`, `-1/s` while thrusting, `recharge in x s` (the delay countdown) and `+0.75/s` while recharging.
- Test: `HudMeterNoteShowsCostAndRecharge`.

## 3. Ash Phase Breach: measured vs implemented

New `PhaseBreachAbility` (ultimate slot, id `phase_breach`).

Flow:
- Z → targeting. The aim is re-evaluated every command.
- After the raise, LMB (`IN_ATTACK`, new `SkillInput.attack`) confirms.
- 0.401 s later the body travels a straight kinematic path. The travel is phased: new `CommandModifiers.phased` / `R5MotorV2.phased`. The world neither sweeps nor resolves it, and the motor does not clamp it to the floor.
- The body stops at the exit, then falls.
- The entry portal stays live and can be re-entered.

| Item | Unity (Reference) | Evidence | Test |
|---|---|---|---|
| Confirm → breach start | 0.401 s (48 commands at 120 Hz) | [meas] n 19 | `LockTimeExitDistance…` |
| Freeze | 0.152 + 0.1017 × frames, frames = round(clamp(path/1200, 0.3, 1.8)/0.1) | [fit] rms 0.025 s + [src] | 600 / 1200 / 2000 u aims: 0.6605 / 1.0673 / 1.6775 s vs [meas] 0.653 / 1.076 / 1.672 |
| Path motion | straight entry → exit during frames × 0.1 s, then held at the exit until the freeze ends | [src] 0.1 s mover frames; position inside the freeze [design] | `TravelIsFrozenStraight…` |
| Exit | 0.918 × the aimed 2D distance | [meas] 0.919 / 0.918 / 0.917 | 550.8 / 1101.6 / 1836 vs [meas] 551.2 / 1102.8 / 1832.5 |
| Exit height / velocity | +5 u above the ground; v = (0, 0, 0) exactly, whatever was held or the entry speed | [meas] 31/31 | `LockTime…`, `FunBreachIsShorter…` |
| Inputs during travel | dropped (`LockControls`). Jump press masked, other slots refused (`LOCKED`), use press masked (`USE_BLOCKED_phase_breach`: no zipline mount from inside the travel) | [src] FreezeControlsOnServer + [design] | `TravelIsFrozen…`, `TravelEndsJets…`, demo B5 failure |
| Range | eye-trace range = 2953 / cos(clamp(pitch, ±45°)) | [src] | `OutOfRangeAndOutsideTheCone…` |
| Invalid targets | `TOO_CLOSE` (< 200 u [src]); `NO_SURFACE`; `OUT_OF_RANGE` (a standable surface on the eye ray beyond the range); `OUTSIDE_CONE` (steeper than 45° the range is cut and the surface lies beyond it); `EXIT_NO_GROUND` (no walkable support within 64 u below the aim height at the exit [design]); `EXIT_BLOCKED` (the standing hull does not fit at the exit) | [src] constants + [design] checks | `InvalidTargetsRefuse…`, `OutOfRange…`; refused confirm: no charge, still aiming |
| Fallback when the eye ray finds no floor | walk back along the ray (64 u steps [design]); ground below within min(dist × cos 75°, 1000 u) | [src] TRACE_HEIGHT_SIN, DOWN_TRACE_DISTANCE | `AnObstacleOnTheAimRayShortens…` |
| Obstacles | on the aim ray: the target falls back in front of it. On the feet path: passed phased (no collision), and the exit is validated free. Ropes do not stop the aim (`MovementWorld.RaycastSolids`) | [design] | `AnObstacle…`, `PhasedTravelPassesThroughALedgeFace…`, `TheCourseTowerTop…` |
| Portal | lives 15 s from the travel start; touching it (≤ 32 u, −36…72 u [design]) sends the body along the same path to the same exit, at rest, with no charge; a new breach replaces it | [src] 15 s + [meas] 11/11 same exit | `EntryPortalSendsAlongTheSamePath…`, demo B4 |
| Raise | 0.8 s before a confirm is accepted | [design] (~0.8–1.0 s, lead's note; not in the report) | `InvalidTargets…` (REFUSED_RAISING), demo B3 failure |
| Charges | 1 × 15 s; spent when the travel **starts** | [design] | `AHitDuringAimOrWindup…` |
| Cancel / timeout | Z again cancels; targeting ends by itself after 10 s; neither costs a charge | [design] | `InvalidTargets…` |
| Interruption | aim or windup interrupted (an external hit, the arbiter): idle, no charge, no portal, body unmoved. Travel: not interruptible (exclusive, prio 100, `exclusiveOnDrive`); launches and drivers cannot touch it; the only exit is the guard timeout (2.5 s > the 1.983 s maximum), which puts the body at the validated exit | [design] | `AHitDuringAimOrWindup…`, `ATimedOutTravel…` |
| Arbiter | `SkillTraits.exclusiveOnDrive`: the breach ends other Pending / Driving states only when the travel starts (aim and cancel end nothing); the teleport / portal rows keep their old rule | [design] | `TravelEndsJetsAndLocksOtherSlots` |

Visuals and HUD:
- Ring at the aim point: green valid, grey while raising, red invalid.
- Exit ghost ring and path line while aiming.
- Violet entry-portal column fading over 15 s, exit ring and faint path while the portal lives.
- The crosshair label gives the distance and freeze, or the reason the aim is invalid.
- The HUD line shows the targeting, the windup and the portal countdown.

Camera:
- Follows the fps-camera-design method, with design values: `breachFov` 6° sustained while phased, a `breachStartKick` FOV kick of 3, and a `breachExitDip` of 1.5 u at the exit.
- The new terms sit in the existing intensity groups.
- The camera is a visual layer only. The demo-visual tests prove the simulation is identical with and without it.

## 4. Loadouts and map

- **Valk-Horizon aerial**: same slots; the jets now use the measured model.
- **Ash route** is a new preset, key `4`: jets on jump, grapple on Q (1 × 8 s), Phase Breach on Z (1 × 15 s). Asset `Presets/Loadouts/AshRoute.asset`.
- The three older presets and their demos are unchanged. Their loadout assets were regenerated for the new trait row; the config assets were regenerated for the new parameter sets.
- **Q Breach gap** (west strip, x −800…−400 / −1150…−250, y 700…2550):
  - mantle stair 60 → 170 → deck A (280);
  - a 950 u gap;
  - deck B (320: too high to climb from the floor, too far to jump).
  - Breach A → B, or cross with the jets.
  - The stair climb itself was not tested by input.
- **R Jets tower** (top 1300): one hold up the east face (demo B2).
- The M6-B blocks are added after every other block. No ramp, rope, checkpoint or gate was added, so the M5 route and the course lap are unchanged (§8).
- On the course, a breach from the east tower top to the north-lane floor is a valid alternative to the high line (`TheCourseTowerTop…`). No geometry was changed for it.

## 5. Demos (real input through Advance → Step; verdicts read the recorded simulation)

| Id | Chain | Failure variant (shift) |
|---|---|---|
| `m6b_valk_burst_climb` | 0.3 s jets burst (released above the terminal: no cut) → climb → mantle onto the 300 face | burst +0.6 s: the press is the climb's own, no jets, top not reached |
| `m6b_valk_hold_tower` | one hold (6.65 / 8 meter) up the 1300 tower → mantle | release −1.5 s: top not reached |
| `m6b_breach_gap_slide` | **Ash ↔ slide**: breach A → B (frozen 1.067 s, exit at rest) → sprint + slide from rest | confirm −0.5 s: refused while raising, no charge |
| `m6b_breach_portal_reuse` | breach → sprint back → portal re-entry → same exit, 1 charge | walk-back +12 s: the portal expired |
| `m6b_breach_zipline` | **Ash ↔ zipline**: exit at rest 60 u before the rope → use → ride | use −0.6 s: pressed during the travel, masked |
| `m6b_valk_superjump` | **Valkyrie ↔ Super Jump**: zipline super jump (vz 552) → jets at vz 483 (above the terminal) → onto the 320 perch | 2nd jump +0.3 s: no super jump (the late press engages the jets) |
| `m6b_valk_grapple` | **Valkyrie ↔ grapple**: jets → grapple attach ends the jets → manual release → jets again → over the anchor block | re-press −0.5 s: in the pull, `JUMP_BLOCKED_DRIVING` |

Every demo:
- succeeds at shift 0 with 3 frame seeds, and fails at its shift for the stated reason (checked independently of the verdict);
- is frame-rate independent;
- equals the recorded inputs fed straight to `SkillBody.Step`;
- runs the same with visuals on.

## 6. Tests

| Suite | Result |
|---|---|
| EditMode | **607 / 607** (main had 511; +96). New: `JetsMeasuredTests` (11), `PhaseBreachTests` (16), `M6BGameTests` (6), `SkillFuzzTests.AshRoute` ×5, 7 demos × the demo suites, course fuzz for the Ash loadout (×2 configs). |
| PlayMode | 1 / 1 (smoke with 48 demo verdicts) |

Fuzz:
- `SkillFuzzTests` (M5 world) and the course fuzz (`M6CourseTests`, 12 seeds × 5 episodes, both configs, now 4 loadouts) press attack from their own random generator, so the other presets' inputs are unchanged.
- A phased command is not subjected to the hull-in-solid test. Instead it is asserted to lie on its straight entry → exit path, frozen, and the exit must be free.
- Ash course fuzz: breaches > 0. No state left open after the idle seconds, no tunnelling candidate, no stuck command, every speed ceiling held.

## 7. Regression (default replay motor)

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 | `m3/unity` | 90 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set, unchanged |
| 38 M4 trials incl. every `m4_valk_*` (`m4_replay_check.py <new> --base m4_replay`, `-scenarios <abs>/m4/unity/scenarios.json`) | `m5/unity/m4_replay` | **114 identical, 0 different, 0 missing** |

Why the M4 Valkyrie replays did not change:
- The replay builds its kit with `new JetpackAbility()` = `JetpackParams.R5Reference()`. In that set every M6-B rule is off: activation cost 0, recharge 0, post effect after every airborne stop, ∞ timer, tightness down = up, sideways = forward.
- The sideways limit now uses `tightSide`. That is bit-identical while it equals `tightForwardBack`.
- The jets' report dictionary omits the inert M6-B fields when the M4 model is active (`IsM4Model`), so `summary.json` stays byte-identical.
- Only the game loadouts use the measured model.

## 8. Build and smoke

- `HSD-Build/M6B/HSD-Practice.exe`: 91 MB, 0 errors, 0 warnings. The scene and ProjectSettings re-serialised by the build were reverted.
- Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 17; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 48/48 verdicts as expected (24 SUCCESS at shift 0, 24 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14); course lap 80.82 s (7/7 checkpoints, Reference (R5 calibration)); feedback
snapshot ok (26 fields, 2112 bytes); 33835 commands in total
```

- The M5.5 route line is unchanged ("1441 commands … final pos (341.586, 146.165, 10) |v_h| 92.0").
- The M5.5, M6 and M6-C verdicts are unchanged. The course lap is unchanged at 80.82 s.

## 9. Open gaps

- Valkyrie:
  - what starts the recharge (landing vs release) — the landing is picked, with a Stop option;
  - air recharge (allowed, untested in R5);
  - `VerticalVelocityScaleOnActivation` for vz < 0 (not modelled);
  - fall damage (none in HSD).
- Ash:
  - targeting beyond flat ground: the R5 placement search (WallUp, FindGround, CheckSpace, CheckLos, scoring) is replaced by the eye-ray + fallback + exit checks above;
  - movers;
  - input response right after the exit;
  - weapon return (0.4 s, not modelled);
  - re-entry delay (none: immediate);
  - portal ownership / team rules (single player);
  - how the body moves inside the freeze (straight over frames × 0.1 s, then held).
- Design values to judge in play: raise 0.8 s, charge 1 × 15 s, portal trigger 32 u, exit drop limit 64 u, every Fun value, the camera cues.
- Not covered by an input test: the Q stair climb, and bursts falling short of the R tower (inferred from the measured u/meter ratios).
