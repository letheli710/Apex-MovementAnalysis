# M6-C in HSD-Unity: combination course, cross-family chains, robustness, feedback entry

- Branch `m6c/combination-playground` of HSD-Unity, from main `9e858a2` (M6-A merged).
- Unity 6000.6.5f1, SOURCE units.
- Plan: [../M6-PLAN.md](../M6-PLAN.md) §M6-C.
- Design notes: [../M6-C-DESIGN-NOTES.md](../M6-C-DESIGN-NOTES.md).
- Playtest guide: [../PLAYTEST-GUIDE-M6C.md](../PLAYTEST-GUIDE-M6C.md).

Labels: **[meas] / [fit] / [src]** as in M6-A; **[design]** an HSD choice; **[course]** a number produced in Unity on the course by real input
(not an R5 measurement).

## 1. What changed (all game layer; the simulation core `R5Replay/` is untouched)

| File | Change |
|---|---|
| `Game/Runtime/CombinationCourse.cs` (new) | The course geometry, its route, stations and challenge gates. Also extends the boundary walls to 5000 u and adds an invisible sky ceiling (§4.3). |
| `Game/Runtime/PracticeMap.cs` | `MapRamp`, `TimeTrialRoute`, `ChallengeGate`; lists `ramps`, `courseStations`, `gates`, `routes`; `BlockKind.Sky`. Ramps go into the world after every block, so every M5 / M6 block keeps its index and surface id. |
| `Game/Runtime/PracticeSession.cs` | Time-trial routes (`RouteIndex`, `SetRoute`, `NextRoute`, `Checkpoints`, `BestKey`). Route 0 is the M5 route with its old best-time key. Challenge gates: a read-only check after each command, which logs `CHALLENGE <gate> via <mechanics of the last 4 s>`. |
| `Game/Runtime/MovementDemosM6.cs` | The four M6 chain demos are built by factories (`BounceTapStrafeAt`, `ClimbSuperglideAt`, `GrappleReleaseSlideAt`). The M6 versions pass their old constants, so the inputs are the same bit for bit; smoke lines unchanged. |
| `Game/Runtime/MovementDemosM6C.cs` (new) | 7 course demos (§3). |
| `Game/Runtime/CourseAutopilot.cs` (new) | A scripted player for a full ground lap of the course (tests and smoke). |
| `Game/Runtime/FeedbackRecorder.cs` (new) | The playtest feedback entry (§5). |
| `Game/Runtime/PracticeGame.cs` | Ramp meshes; gate frames and markers; course signs; checkpoints of both routes. Keys: F2 route, F9 / F10 feedback. Feedback overlay and toast; help line; demo panel buttons in rows. Smoke: M6-C demo count, course lap, feedback snapshot. |
| Tests | New `M6CourseTests` (§6), plus small updates to existing tests (§6). |

## 2. The course (south strip y −2600 … −1000, x −1150 … 12350)

- The course is a loop. It goes out east along the south lane and comes back west along the north lane.
- A spine wall (y −1820…−1780, height 360) separates the lanes. Both of its faces are wall-bounce surfaces.
- Nothing of the M5.5 map or of M6 stations F–I moved. This is tested: every course solid, ramp, rope, checkpoint and gate lies south of y −1000, and every older block lies north of it.

| Section | Geometry | Alternatives |
|---|---|---|
| J launch hill + slide tunnel | ramp up (0→120, 400 u), deck 120, ramp down (600 u); tunnel x 1000–1200 (ceiling at 60, roof top 120) at the foot | slide down the hill and through the tunnel (tested: the downhill slide carries through, hull stays crouched); go around the tunnel; mantle onto the roof |
| K barrier canyon | slab across the lane, x 3500–3600, z 60–150 | crouch-slide under it (tested; a standing walk stops at the face); climb + mantle + superglide over it (demo 12) |
| L zip yard | uphill rope (5000, −2350, 130) → (7700, −2350, 380) onto the yard deck (top 250); walk-up ramp (22.6°); super-jump perch x 5130–5330, y −2310…−2130, top 320 | rope (tested: rides to its end and lands on the deck); ramp (autopilot lap); climb |
| M east tower | x 10900–11950, y −1700…−1100, top 440. Vertical rope at (10860, −1400) up to 500; world gravity lift at (10700, −1500); 240 step on the south face | vertical rope (tested, lands on top); lift (tested with all 3 loadouts); step + climb; abilities |
| N high line | rope (11100, −1250, 520) → (6900, −1250, 400), out of use reach from the floor; world pad under it at (9900, −1250); three grapple anchors over the spine | use on the tower top (tested, rides to the end); grapple the rope from the floor (handoff, demo 15); pad + air mount in fun (demo 17) |
| O superglide wall | x 4940–5000, y −1780…−1250, top 180; walk-around gap north of it | climb + mantle + superglide (the ring needs it); walk around (autopilot lap) |
| P bounce alley | north walls x 2600–3400 and 800–1600 (height 300), a 50 u slope ridge | bounce, tap-strafe; or run |

- **Time trial (route 1, F2).** Eight checkpoints: start, J, K, L deck, M tower top, N high-line end (a 700 u tall gate), O, finish.
  - Radii are 160–450, so every alternative of a section passes them.
  - Every respawn point is free and on its floor (tested).
- **Lap by real input.** `CourseAutopilot.GroundLap` takes the slow alternatives and presses no ability. It finishes **80.82 s** with every config × loadout (6/6, all 7 checkpoints in order).
- **Challenge gates (optional, logged only).**

  | Gate | Intended way | Other ways |
  |---|---|---|
  | Super-jump perch, top 320 | the zip super jump; demo 13 | jets + climb (tested) or grapple |
  | Superglide ring, x 4560–4660, z 120–260 | a straight superglide off O reaches it (tested); a 299 mantle jump does not (tested) | |
  | High-line rider | riding the high line (seen in every autopilot lap) | |

- **Geometry tuned to the measured models while building** (all [course]):
  - The tunnel is 200 u long. A downhill slide from the deck covers about 830 u and a sprint slide about 470 u, while the slope slide
    gains almost nothing ([design] scale ×1).
  - The tower is 1050 u wide. The vertical-rope top exit flies about 580 u: vz ≈ 550 plus a 400 push.
  - The perch is placed where the super-jump apex (+266 u above the jump-off) and a 32° lurch meet the mantle reach (top − z ≤ 80).

## 3. Chains by real input on the course

- Every demo is scripted keys and view through `PracticeSession.Advance → SkillBody.Step`.
- The existing integrity tests run on all of them automatically, because they are in `MovementDemos.All()`:
  - bit-identical to the recorded inputs through raw `SkillBody.Step` at uneven frame rates;
  - succeed for seeds 1–3 with every criterion met;
  - frame-rate independent;
  - unchanged by visuals;
  - fail at their shift for the expected reason, checked independently in `EveryDemoFailsWithItsFailureShift`.
- The source scan for simulation writes now also covers `MovementDemosM6.cs` and `MovementDemosM6C.cs`.

| # | Demo (id) | Success (shift 0), from the smoke | Failure variant |
|---|---|---|---|
| 11 | `m6c_canyon_bounce`: slide jump → wall bounce → tap strafe (spine wall, 40°) | bounce at 1.90 s → 9 W-tap lurches, flight 2.6° behind the view, 99° turned | bounce jump +0.3 s: contact 0.367 s old, no bounce |
| 12 | `m6c_barrier_superglide`: climb → mantle → superglide (barrier slab 150) | climb 0.17 s → mantle → superglide 460 u/s over the slab | jump −0.3 s: mantle cut |
| 13 | `m6c_zip_perch`: zipline → super jump → air redirect → mantle onto the 320 perch | vz 552, apex +266 u, lurch 32.4°, mantle onto 320, inside the gate | 2nd jump +0.3 s: no super jump, perch not reached |
| 14 | `m6c_anchor_release`: grapple release → air adjust (D) → landing slide | release 287 u/s (kept exactly), steer −13°, landing slide 296 u/s | release +1.5 s: pull already ended (GAP) |
| 15 | `m6c_grapple_highline` (cross): grapple → zipline handoff → jump-off → lurch | handoff at 387 u/s, ride 0.73 s, jump-off 400 u/s (cap), no super jump (grapple mount), D lurch 32.1°, max v_h 477 | lurch +0.6 s: window closed |
| 16 | `m6c_superglide_bounce` (cross): superglide → lurch → wall bounce | 460 → A lurch 27.4° (v_h 387) → spine bounce at 430 u/s, 258 u/s off the wall | bounce +0.3 s: contact 0.333 s old |
| 17 | `m6c_pad_airmount` (cross, fun): pad → zipline air mount | air mount 0.53 s after the launch, entry 494 u/s along the rope, ride ≤ 600 | use +0.8 s: rope out of reach (z 675) |

- The M6 station versions (demos 7–10) are unchanged.
- The four plan chains now exist at two geometries each:
  - slide jump → bounce → tap strafe: 7 and 11;
  - climb → mantle → fast exit: 8 and 12;
  - zipline → super jump → redirect: 9 and 13;
  - grapple release → adjust → slide: 10 and 14.
- Plus three cross-family chains: 15, 16 and 17.

## 4. Robustness of continuous operation

### 4.1 Random play on the course (`RandomPlayOnTheCourseHasNoAbnormalStates`, 2 configs × 3 loadouts)

**Setup.**
- 12 seeds × 5 episodes of 25 s, each followed by 10 idle seconds.
- Half the episodes start with a chain demo (60 % the M6-C ones) played in this config and loadout, with timing errors of 0 / ±0.03 / ±0.1 s and a stim / phase press 50 % of the time; random input follows.
- The rest start at one of 14 spawn points over every section with random keys, view, use and slots.

**Asserted every command:**
- the state is finite;
- the hull (crouched) is never inside a solid;
- never below the floor or off the map;
- the horizontal ceiling 900 and the upward ceiling 1100 hold;
- the rope speed stays ≤ 600;
- a jump-off stays ≤ 400;
- a superglide exit stays ≤ 460 × 1.40;
- there is no super jump after a grapple-mounted ride;
- jets and a traversal never drive together.

**Asserted per run:**
- every state has ended after the idle seconds;
- no climb / zipline guard timeout;
- no swept segment through a solid (sampled every 4 u);
- no traversal frozen in place for 1 s;
- no unresolved collision (`lastStuck`).

**Totals:** 360 episodes, 1 512 000 commands (12 600 s, 3.5 h of play).

| Config / loadout | climbs / mantles | superglides | bounces | zip mounts (+grapple handoffs) | super jumps | chain counts | max v_h / vz / rope | guard timeouts (non-traversal) |
|---|---|---|---|---|---|---|---|---|
| Ref / Pathfinder-Octane | 92 / 9 | 3 | 172 | 8 (+3) | 1 | grapple→zip jump-offs 3, stim+superglide 1 (460) | 813 / 1026 / 523 | 0 |
| Ref / Valk-Horizon | 52 / 7 | 1 | 120 | 7 (+2) | 4 | jets→climb/mantle ≤ 1 s 41 | 638 / 1026 / 600 | 6 (grapple 1, pad 5) |
| Ref / Revenant-Wraith | 129 / 12 | 3 | 228 | 13 | 2 | – | 676 / 1026 / 298 | 0 |
| Fun / Pathfinder-Octane | 63 / 15 | 4 | 121 | 57 (+2) | 4 | grapple→zip 2, stim+superglide 2 (460), pad+zip air mounts 11 | 813 / 1027 / 600 | 6 (pad 4, grapple 2) |
| Fun / Valk-Horizon | 29 / 10 | 3 | 69 | 48 (+2) | 4 | grapple→zip 1, pad+zip 2, jets→climb 23 | 867 / 1026 / 600 | 7 (pad 4, jets 1, grapple 2) |
| Fun / Revenant-Wraith | 75 / 12 | 0 | 130 | 43 | 1 | pad+zip 1 | 813 / 1026 / 511 | 11 (pad 1, pounce 10) |

Every row has:
- 0 exit failures;
- 0 traversal timeouts;
- 0 tunnelling candidates;
- 0 frozen traversals;
- 0 unresolved collisions.

The Unity run and the .NET harness gave the same counts.

**Guard timeouts that fired (reported, not hidden).** All of them are M5 abilities' own guards (SKILL-RULES §2); the M6 traversals never needed theirs.

| Guard | Count | What happened |
|---|---|---|
| jump pad effect, 6 s | 19 | The pad's slow-mo effect lasts until landing. The body was kept airborne for more than 6 s by repeated jets, fun flight / low gravity, lifts or grapple pulls. |
| grapple pull, 3 s | 7 | The hook was on a wall top or edge, and the pull pressed the body into the face without reaching the release gap. |
| pounce, 2.5 s pending / 6 s effect | 10 | Fun only: long flights (gravity ×0.45, flight). |
| jets, 9 s driving | 1 | Fun gravity: a jets climb above z 2000. |

None of these cases arise in the scripted chains or the lap. See the design notes §3.1 for proposals.

### 4.2 Deterministic cross-family checks (wrong speed stacking)

| Test | Result |
|---|---|
| `GrappleMountedRideArmsNoSuperJump`: grapple → zip → jump-off → second jump inside 0.2 s → lurch | no super jump; jump-off v_h ≤ 400, vz 289.828; lurch ≤ 209.3; max v_h ≤ 609.3 |
| `StimSuperglideStaysUnderTheBoostCap` | exit **460.0** with stim running: stim does not stack on the superglide pose speed. Bounded by 460 × 1.40 |
| `PadAirMountRespectsTheRopeCaps` (fun) | ride ≤ 600, jump-off ≤ 400; the reference config refuses the air mount (`ZIP_REFUSED_AIR`) |
| `JetsAndClimbNeverStack` (Valk at the perch) | jets first: no climb starts while the jets thrust (M6-A `OtherDriving` rule); after the release the climb + jump-up + mantle reach the 320 perch; climb vz on its own line (≤ 1.735 · 180.4). Climb first: the second jump press is the climb's wall bounce, the jets do not engage. Never both driving, no timeout |

### 4.3 Collision issues found and fixed during M6-C

- **Escape over the map.** Random play flew over the 800 u boundary walls: z 942 with jets / grapple, z 6853 with fun gravity + flight.
  - New boundary blocks now sit on top of the old ones, up to 5000.
  - An invisible `Sky` slab at 5000 closes the map.
  - 5000 is above the 4000 u grapple-view / aim rays from any eye in normal play, so looking up still shows "no surface". The first try at 4000 broke `GrappleAimStatesMatchTheAbilitysRangeTest` and was raised.
  - The old walls are unchanged.
- **Spawns inside solids.** A fuzz spawn inside a ramp, or under the tunnel roof, left a standing body embedded.
  - The course respawn points and the fuzz spawns are now checked as free (tested).
  - `ResetToPose` itself does not validate (dev tool only).

## 5. Playtest feedback entry

- **Keys.**
  - **F9** pauses and captures the moment, then opens a small overlay: a one-line note, a rating 1–5 or none; Enter saves, Esc cancels.
  - **F10** saves a snapshot at once.
  - The menu has the same entry. The help line shows the keys, and a toast shows the saved file name.
- **Output.** `FeedbackRecorder.Save` writes `Feedback/feedback_<yyyyMMdd_HHmmss_fff>.json` and a `.md` summary.
  - The folder is next to the build: `Path.GetDirectoryName(Application.dataPath)/Feedback`. In the editor that is the project root.
  - It is git-ignored (`[Ff]eedback/`).
- **Fields (`hsd-feedback-1`):**
  - time (local, UTC); note, rating; config, loadout, route;
  - run state (running / time / last and next checkpoint / best); gates cleared;
  - sim time, position, velocity, |v_h|, view, nearest station;
  - motor flags and lurch-window age;
  - mechanics: climb phase and counts, zipline ride (rope, speed) or last exit and budget, grapple phase and last release, jets fuel, every slot;
  - the session's last 16 timed events;
  - the last 3 s of inputs, run-length coded as key letters × commands;
  - the last 3 s of command events with positions;
  - game side: build, camera settings, HUD mode, mouse sensitivity, running demo.
- **Read only.** The recorder is an `OnCommand` observer. `FeedbackSnapshotHoldsTheMomentAndNeverChangesTheSimulation` checks that the same demo gives identical positions and velocities with and without it, that the snapshot round-trips through JSON with the expected values, and that the .json + .md files are written.
- **Smoke.** The smoke writes a snapshot to a temporary folder, reads it back and deletes it: `feedback snapshot ok (26 fields, 2111 bytes)`.

## 6. Tests

- EditMode **511 / 511**: the 424 from before plus 87 new. PlayMode **1 / 1**.
- New EditMode cases (`M6CourseTests`, 31):
  - layout, and route switching;
  - the lap (6);
  - barrier, tunnel, perch-not-climbable;
  - course ropes; tower lift (3);
  - perch gate; superglide ring (2);
  - grapple-zip; stim-superglide; pad-zip; jets-climb (3);
  - feedback; random play (6).
- The other new cases come from the 7 new demos through the existing parameterised demo tests:
  - `EveryDemoSucceedsHeadless` ×3 seeds;
  - `EveryDemoFailsWithItsFailureShift`;
  - `DemoTrajectoryEquals…` ×2;
  - `DemoIsFrameRateIndependent`;
  - the visuals test.
- Existing tests changed on purpose, each keeping its intent:
  - `M6GameTests.EveryMapRopeMountsFromItsStart`: counts and rides only the 4 M6 station ropes; the course ropes have their own test.
  - `M6GameTests.M5StationsAndCheckpointsAreUnchanged`: the map-wide `Sky` slab is allowed like the boundary.
  - `WorldEquivalenceTests.SupportAndBlockedMatchTheM55BoxWorldOnTheMap`: sample hulls over a course ramp footprint are skipped. The frozen M5.5 BoxWorld has no ramps. Everything else is still compared, more than 10 000 blocked samples.
  - `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: cases for the 7 new demos.
  - `MovementDemoTests.DemoProbeAndVisualCodeHaveNoSimulationWrites`: scans the two chain-demo files too.
  - PlayMode smoke test: also requires the course lap (7/7) and the feedback snapshot.
- The M5.5 equivalence tests still pass unchanged: the smoke route and the 30 s runs against the frozen BoxWorld, `1441 commands final pos (341.586, 146.165, 10) |v_h| 92.0`.

## 7. Regression (default replay motor)

`R5Replay/` is untouched; the runs confirm it.

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 | `m3/unity` | 90 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set, unchanged |
| 38 M4 trials (`m4_replay_check.py <new> --base m4_replay`, `-scenarios <abs>/m4/unity/scenarios.json`) | `m5/unity/m4_replay` | 114 identical, 0 different, 0 missing |

## 8. Build and smoke

- `HSD-Build/M6C/HSD-Practice.exe`: 91 MB, 0 errors, 0 warnings.
- The scene, ProjectSettings and config assets that the build re-serialised (line endings only) were reverted.
- Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 17; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 34/34 verdicts as expected (17 SUCCESS at shift 0, 17 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14); course lap 80.82 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok
(26 fields, 2111 bytes); 22761 commands in total
```

- **The route part is identical to M5.5 / M6-A.**
- **Every M5.5 and M6 demo line carries its earlier values**:
  - M5.5: 24.0°, 350.0, 48.3°, 534, 127 / −32.7°, 0.358 s;
  - M6: 93°, 460, vz 552 / 67.2°, 248 / +16°.
- A run with graphics (`-smokeShot`) took screenshots of four course demos. The ramps, gate marker, perch, barrier and the extended walls render.

## 9. Open gaps

- **Values the course depends on that are [design] or single-geometry [meas]:**
  - super jump window 0.2 s;
  - superglide window at 150 / 180 (derived from 232);
  - the vertical-rope top push;
  - the grapple → rope handoff distance 136;
  - the rope hook radius 10;
  - the slope-slide scale;
  - the air mount (fun).
- **Stim does not affect the superglide exit** in HSD. R5 is unmeasured.
- **The non-traversal guard timeouts in random play** (§4.1) are by design. Possible rule refinements, such as grapple release when pressed into a face, or ending the pad effect when another driver takes over, are listed in the design notes and not implemented.
- **The autopilot lap takes only the ground route.** The faster alternatives are shown by the demos and tests, not by a scripted full lap.
- **Not done.** No section split times or ghost replay. The course is built in code, not from a data file.
- **Feedback overlay.** The overlay is plain IMGUI. Typing a note relies on the OS font (CJK as in the HUD).
- **No hand playtest yet.** No human has played the course; every camera cue is the M6-A one.
